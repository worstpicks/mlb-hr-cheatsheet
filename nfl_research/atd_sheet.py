"""Build the weekly Anytime-TD cheat sheet page from the slate and the week's play list.

    python -m nfl_research.atd_sheet --season 2026 --week 2

Inputs
    nfl_research/atd_weeks/<season>-W<week>.txt   the plays, as exported from the
                                                 Research tab's Prop List
    preview/data/nfl-research-<season>-W<week>.json   the slate (fetch-nfl-research-slate.py)
    nfl_research/atd_weeks/defense-<season>-W<week>.csv   optional team-defense scoring
                                                 table; its TARGET verdicts mark the
                                                 exploitable defenses
Live
    ESPN injury reports (fresher than nflverse's mid-week table) and nflverse
    play-by-play for fourth-down aggressiveness.

Everything a play shows is computed here or on the Game Board -- nothing is pasted.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import nflreadpy as nfl
import polars as pl

ROOT = Path(__file__).resolve().parent.parent
WEEKS = Path(__file__).resolve().parent / "atd_weeks"
TEMPLATE = Path(__file__).resolve().parent / "templates" / "atd_sheet.html"
TEAM_FIX = {"LA": "LAR", "WAS": "WSH", "JAC": "JAX"}
LEAGUE_POINTS = 22.5
MIN_GAMES = 4          # fewer games than this and a player is shown, never rated
FAVORITES = 16         # roughly one a game
ESPN_CORE = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/"
ESPN_SITE = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/"


def norm(name: str) -> str:
    n = str(name or "").lower().replace(".", "").replace("'", "").replace("’", "")
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    n = re.sub(r"[^a-z ]", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


# ── inputs ─────────────────────────────────────────────────────────────────────
def load_plays(path: Path) -> list[dict]:
    games, current = [], None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" not in line:
            away, home = line.split("@")
            current = {"away": away.strip(), "home": home.strip(), "plays": []}
            games.append(current)
            continue
        name, slot, team, opp, over, market = [x.strip() for x in line.split("|")]
        current["plays"].append({"name": name, "slot": slot, "team": team, "opp": opp,
                                 "line": float(over), "market": market})
    return games


def load_defense_csv(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    out = {}
    for r in csv.DictReader(io.open(path, encoding="utf-8-sig")):
        code = TEAM_FIX.get(r["Code"], r["Code"])
        out[code] = {"verdict": r["Verdict"].split()[-1], "tier": r["Tier"],
                     "pts": round(float(r["PTS/G"]), 1), "rank": int(r["Rank"])}
    return out


def _get(url: str):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        return json.load(urllib.request.urlopen(req, timeout=30))
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None


def espn_injuries(teams: set[str], wanted_espn_ids: set[str]) -> dict[str, dict]:
    """espn athlete id -> {status, detail, date} from each club's injury feed.

    The feed lists newest first and keeps a player's old entries, so only his
    newest counts. Only the listed players' entries are opened.
    """
    listing = _get(ESPN_SITE + "teams") or {}
    ids = {t["team"]["abbreviation"]: t["team"]["id"]
           for t in listing.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])}
    refs = []
    for team in teams:
        tid = ids.get(team)
        page = _get(f"{ESPN_CORE}teams/{tid}/injuries?limit=100") if tid else None
        for item in (page or {}).get("items", []):
            refs.append(item["$ref"])

    def fetch(ref):
        return _get(ref)

    newest: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=16) as pool:
        for item in pool.map(fetch, refs):
            if not item:
                continue
            m = re.search(r"/athletes/(\d+)", (item.get("athlete") or {}).get("$ref", ""))
            if not m or m.group(1) not in wanted_espn_ids:
                continue
            aid = m.group(1)
            if aid in newest and newest[aid]["date"] >= item.get("date", ""):
                continue
            newest[aid] = {"status": item.get("status") or "", "date": item.get("date", ""),
                           "detail": item.get("shortComment") or ""}
    return newest


def fourth_down_aggression(seasons: list[int], window: int = 17) -> dict[str, float]:
    """Share of 4th-and-3-or-less snaps past a team's own 40 where it went for it,
    over each offense's last `window` games, with the game still in the balance."""
    parts = []
    for s in seasons:
        try:
            parts.append(nfl.load_pbp(seasons=[s]).select(
                ["game_id", "season", "week", "posteam", "down", "ydstogo", "yardline_100", "play_type", "wp",
                 "season_type"]))
        except Exception:
            pass
    if not parts:
        return {}
    pbp = pl.concat(parts, how="diagonal_relaxed").filter(pl.col("season_type") == "REG")
    pbp = pbp.with_columns(pl.col("posteam").replace(TEAM_FIX))
    games = (pbp.filter(pl.col("posteam").is_not_null()).select(["posteam", "season", "week"]).unique()
             .sort(["season", "week"]).group_by("posteam").tail(window))
    snaps = pbp.join(games, on=["posteam", "season", "week"], how="inner").filter(
        (pl.col("down") == 4) & (pl.col("ydstogo") <= 3) & (pl.col("yardline_100") <= 60)
        & pl.col("wp").is_between(0.10, 0.90)
        & pl.col("play_type").is_in(["run", "pass", "punt", "field_goal"])
    )
    rates = snaps.group_by("posteam").agg(
        (pl.col("play_type").is_in(["run", "pass"]).sum() / pl.len()).alias("go")
    )
    return {r["posteam"]: float(r["go"]) for r in rates.iter_rows(named=True)}


# ── the sheet ──────────────────────────────────────────────────────────────────
def build(season: int, week: int) -> Path:
    slate_path = ROOT / "preview" / "data" / f"nfl-research-{season}-W{week}.json"
    slate = json.loads(slate_path.read_text(encoding="utf-8"))
    plan = load_plays(WEEKS / f"{season}-W{week}.txt")
    defense = load_defense_csv(WEEKS / f"defense-{season}-W{week}.csv")
    by_game = {f"{g['away']}@{g['home']}": g for g in slate["games"]}

    env: dict[str, dict] = {}
    implied: dict[str, float] = {}
    for g in slate["games"]:
        env.update(g["board"]["env"])
        implied.update(g["board"]["implied"])
    # red-zone TD rate allowed, ranked 1 (stingiest) to 32 (softest)
    order = sorted((v["def_rz_td"], t) for t, v in env.items() if v.get("def_rz_td") is not None)
    dz_rank = {t: i + 1 for i, (_, t) in enumerate(order)}
    implied_rank = {t: i + 1 for i, (t, _) in enumerate(sorted(implied.items(), key=lambda kv: -kv[1]))}

    players = nfl.load_players().select(["gsis_id", "espn_id"]).drop_nulls()
    espn_of = dict(zip(players["gsis_id"].to_list(), players["espn_id"].to_list()))

    problems: list[str] = []
    rows: list[dict] = []
    for gp in plan:
        key = f"{gp['away']}@{gp['home']}"
        g = by_game.get(key)
        if not g:
            problems.append(f"{key} is not on the Week {week} slate")
            continue
        board = g["board"]["players"]
        for p in gp["plays"]:
            if {p["team"], p["opp"]} != {g["away"], g["home"]}:
                problems.append(f"{p['name']}: {p['team']} vs {p['opp']} is not {key}")
            hit = [b for b in board if b["team"] == p["team"] and norm(b["name"]) == norm(p["name"])]
            if not hit:
                problems.append(f"{p['name']} ({p['team']}) is not in the depth-chart lineup")
                continue
            b = hit[0]
            if b["role"] != p["slot"]:
                problems.append(f"{p['name']}: listed {p['slot']}, depth chart has {b['role']}")
            side = "away_offense" if p["team"] == g["away"] else "home_offense"
            pos = b["pos"]
            off = next((o for o in g[side].get(pos, []) if o.get("player_id") == b.get("player_id")), None)
            avg = (off or {}).get("stats") or {}
            rows.append({"plan": p, "game": key, "b": b, "avg": avg})
    if problems:
        print("[atd] CHECK:\n  " + "\n  ".join(problems))

    listed_teams = {r["plan"]["team"] for r in rows}
    wanted = {espn_of[r["b"]["player_id"]] for r in rows if r["b"].get("player_id") in espn_of}
    injuries = espn_injuries(listed_teams, wanted)
    print(f"[atd] ESPN injury feed: {len(injuries)} listed players carry an entry")
    aggression = fourth_down_aggression([season - 1, season])
    agg_rank = {t: i + 1 for i, (t, _) in enumerate(sorted(aggression.items(), key=lambda kv: -kv[1]))}

    # ── per-play numbers ──
    for r in rows:
        p, b, avg = r["plan"], r["b"], r["avg"]
        team, opp, pos = p["team"], p["opp"], b["pos"]
        m = b.get("matchup") or {}
        inj = injuries.get(espn_of.get(b.get("player_id"), ""), {})
        st = inj.get("status", "").lower()
        r["status"] = ("out" if st in ("out", "injured reserve", "suspension") else
                       "d" if st == "doubtful" else "q" if st == "questionable" else "")
        detail = inj.get("detail", "").strip()
        # ESPN sometimes leaves only a code ("ir") where the note should be
        if r["status"] and len(detail) < 12:
            detail = inj.get("status", "")
        r["injury"] = detail if r["status"] else ""
        r["status_label"] = inj.get("status", "") if r["status"] else ""
        xtd = float(b.get("xtd") or 0.0)
        imp = implied.get(team)
        # the ranking score: his TD rate, moved a little by this week's implied points
        # and by how many touchdowns this defense has allowed to his role
        s_mult = min(1.2, max(0.85, 1 + 0.5 * ((imp or LEAGUE_POINTS) / LEAGUE_POINTS - 1)))
        td_index = m.get("td_index")
        m_mult = 1.0 if (pos == "QB" or td_index is None) else min(1.12, max(0.9, 1 + 0.2 * (td_index - 1)))
        lam = xtd * s_mult * m_mult
        r["score"] = 1 - math.exp(-lam)
        r["small"] = (b.get("games") or 0) < MIN_GAMES
        edge = None
        if m.get("index") is not None and td_index is not None:
            edge = 0.5 * (m["index"] - 1) + 0.5 * (td_index - 1)
        r["edge"] = edge
        lam_raw = xtd
        r["td2"] = round(100 * (1 - math.exp(-lam_raw) * (1 + lam_raw))) if p["line"] >= 1.5 else None
        r["gl"] = float(avg.get("i5_car") or 0.0)
        r["dz"] = dz_rank.get(opp)
        r["imp"] = imp
        r["trend"] = (b.get("share_l3") or 0) - (b.get("share") or 0) if b.get("share") is not None else 0.0

    # ── tags ──
    def rz_role(r):
        b, pos = r["b"], r["b"]["pos"]
        if pos == "QB":
            return r["gl"] >= 0.5
        if pos == "RB":
            return (b.get("rz_share") or 0) >= 30 or r["gl"] >= 1.0
        return (b.get("rz_share") or 0) >= 18

    for r in rows:
        tags = []
        eligible = not r["small"] and r["status"] not in ("out", "d")
        if r["status"] == "out":
            # ruled out or on injured reserve: listed, never tagged
            r["tags"], r["eligible"] = [], False
            continue
        if rz_role(r) and not r["small"]:
            tags.append("rz")
        if (r["edge"] is not None and r["edge"] >= 0.10 and (r["dz"] or 0) >= 13 and not r["small"]
                and r["b"]["pos"] != "QB"):
            tags.append("mat")
        if r["b"]["pos"] == "QB" and (r["b"].get("matchup") or {}).get("index", 0) >= 1.10 and (r["dz"] or 0) >= 13:
            tags.append("mat")
        r["tags"] = tags
        r["eligible"] = eligible

    ranked = sorted([r for r in rows if r["eligible"] and r["status"] != "q"], key=lambda r: -r["score"])
    for r in ranked[:FAVORITES]:
        r["tags"].insert(0, "fav")
    fav_ids = {id(r) for r in ranked[:FAVORITES]}

    # Underrated: not a favourite, rated, and either scoring well above the usual for a
    # player in his slot this week, or his role is growing into a defense that leaks.
    by_slot: dict[str, list[float]] = {}
    for r in rows:
        if not r["small"]:
            by_slot.setdefault(r["b"]["role"][:2] + ("1" if r["b"]["role"].endswith("1") else "2+"), []).append(r["score"])
    medians = {k: sorted(v)[len(v) // 2] for k, v in by_slot.items()}
    for r in rows:
        if id(r) in fav_ids or not r["eligible"]:
            continue
        slot = r["b"]["role"][:2] + ("1" if r["b"]["role"].endswith("1") else "2+")
        above = r["score"] - medians.get(slot, r["score"])
        secondary = not r["b"]["role"].endswith("1") or r["b"]["pos"] == "TE"
        growing = secondary and r["trend"] >= 5 and "mat" in r["tags"] and r["score"] >= 0.25
        if (secondary and above >= 0.08 and r["score"] >= 0.28) or growing:
            r["tags"].insert(0, "val")

    # ✈️ exploitable defenses: the scoring table's TARGET verdict
    exp_teams = {t for t, d in defense.items() if d["verdict"] == "TARGET"}

    # ── team tendencies (computed, not pasted) ──
    tend = {}
    for team, e in env.items():
        t = []
        npr = e.get("neutral_pass_rank")
        if npr is not None and npr <= 10:
            t.append("run")
        if npr is not None and npr >= 23:
            t.append("pass")
        if agg_rank.get(team, 99) <= 10:
            t.append("agg")
        tend[team] = t

    # ── top five: the best-scoring favourites, with the reasons in words ──
    top = [r for r in ranked if r["status"] == ""][:5]
    top5 = [{"id": r["b"]["player_id"], "why": why(r, env, dz_rank, implied_rank, defense, rank_on_board=i + 1)}
            for i, r in enumerate(top)]

    games_out = []
    for gp in plan:
        key = f"{gp['away']}@{gp['home']}"
        g = by_game.get(key)
        if not g:
            continue
        sides = {gp["away"]: [], gp["home"]: []}
        for r in [x for x in rows if x["game"] == key]:
            b, p = r["b"], r["plan"]
            sides[p["team"]].append({
                "n": p["name"], "id": b.get("player_id"), "p": b["role"], "pos": b["pos"],
                "mk": p["market"], "line": p["line"], "t": r["tags"], "st": r["status"], "inj": r["injury"],
                "stl": r["status_label"],
                "m": {
                    "td": b.get("td_chance"), "td2": r["td2"], "rz": b.get("rz_share"), "gl": round(r["gl"], 1),
                    "dz": r["dz"], "edge": None if r["edge"] is None else round(100 * r["edge"]),
                    "g": b.get("games"), "tg": b.get("team_games"), "new": bool(b.get("new_team")),
                    "small": r["small"], "trend": round(r["trend"], 1),
                },
            })
        exp = [t for t in (gp["away"], gp["home"]) if (gp["home"] if t == gp["away"] else gp["away"]) in exp_teams]
        games_out.append({
            "away": gp["away"], "home": gp["home"], "kick": g["kickoff"], "exp": exp,
            "implied": {t: implied.get(t) for t in (gp["away"], gp["home"])},
            "line": (g.get("odds") or {}).get("details"), "total": (g.get("odds") or {}).get("over_under"),
            "dverdict": {t: defense.get(t, {}).get("verdict") for t in (gp["away"], gp["home"])},
            "sides": sides,
        })

    # The player card popup: each listed player's Game Board entry, plus the team
    # context and defensive leaks the card quotes -- only what the card reads, so the
    # page carries ninety-odd players rather than the whole slate.
    cards, card_env, card_leaks = {}, {}, {}
    for r in rows:
        b = r["b"]
        stats = list((b.get("proj") or {}).keys())
        m = b.get("matchup") or {}
        cards[b["player_id"]] = {
            **{k: b.get(k) for k in CARD_FIELDS},
            "matchup": {k: m.get(k) for k in ("index", "rank", "of", "allowed", "league")} if m else None,
            "log": [{**{k: g.get(k) for k in ("season", "week", "opp", "role")}, **{k: g.get(k) for k in stats}}
                    for g in (b.get("log") or [])],
        }
        for t in (b["team"], b["opp"]):
            e = env.get(t, {})
            card_env[t] = {k: e.get(k) for k in ("rz_trips", "def_rz_td", "def_man", "def_pressure")}
        g = by_game[r["game"]]
        card_leaks[b["opp"]] = {role: {"index": v.get("index")}
                                for role, v in ((g["board"].get("leaks") or {}).get(b["opp"]) or {}).items()}

    kicks = sorted(datetime.fromisoformat(g["kick"].replace("Z", "+00:00")) for g in games_out)
    sheet = {
        "season": season, "week": week, "root": "",
        "built": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "first_kick": kicks[0].isoformat(), "last_kick": kicks[-1].isoformat(),
        "games": games_out, "top5": top5, "tend": tend,
        "cards": cards, "env": card_env, "leaks": card_leaks,
        "defense_source": bool(defense),
    }
    out = publish(sheet, season, week)

    n_plays = sum(len(s) for g in games_out for s in g["sides"].values())
    counts = {k: sum(1 for r in rows if k in r["tags"]) for k in ("fav", "val", "rz", "mat")}
    print(f"[atd] {len(games_out)} games, {n_plays} plays, tags {counts}, "
          f"{sum(1 for r in rows if r['status'])} with an injury status, {sum(1 for r in rows if r['small'])} small samples")
    print("[atd] top 5: " + ", ".join(r["plan"]["name"] for r in top))
    for r in rows:
        if r["status"]:
            print(f"[atd] status {r['plan']['name']} ({r['plan']['team']}): {r['status_label']} -- {r['injury'][:90]}")
    print(f"[atd] wrote {out}")
    return out


NFL_DIR = ROOT / "preview" / "nfl-research"
# the Game Board fields the player card popup reads (atd-card.js)
CARD_FIELDS = ("player_id", "name", "pos", "role", "team", "opp", "headshot", "games", "seasons",
               "new_team", "team_games", "no_history", "share", "share_l3", "share_kind", "low_volume",
               "rz_share", "proj", "window", "td_chance", "grade", "reasons", "cov")
MANIFEST = NFL_DIR / "atd-manifest.json"


def render(sheet: dict, season: int, week: int, root: str) -> str:
    """The page for one week. `root` is the path back to preview/nfl-research/:
    "" for the current-week page there, "../" for its copy in archive/."""
    html = TEMPLATE.read_text(encoding="utf-8")
    data = dict(sheet, root=root)
    html = html.replace("/*__SHEET__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    return html.replace("__ROOT__", root).replace("__WEEK__", str(week)).replace("__SEASON__", str(season))


def publish(sheet: dict, season: int, week: int) -> Path:
    """Laid out like the MLB sheet: the current week at nfl-research/atd.html, every week
    (the current one included) in nfl-research/archive/, and atd-manifest.json feeding
    the week dropdown. Only the newest week takes over atd.html, so rebuilding an old
    week never replaces the current one."""
    archive = NFL_DIR / "archive" / f"{season}-week-{week}.html"
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_text(render(sheet, season, week, "../"), encoding="utf-8")

    manifest = {"version": 1, "sheets": []}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    key = f"{season}-W{week}"
    entries = {e["key"]: e for e in manifest.get("sheets", [])}
    entries[key] = {"key": key, "season": season, "week": week}
    ordered = sorted(entries.values(), key=lambda e: (e["season"], e["week"]), reverse=True)
    latest = ordered[0]
    for e in ordered:
        if e is latest:
            e["label"], e["href"] = f"Week {e['week']} \u2014 current week", "atd.html"
        else:
            e["label"], e["href"] = f"Week {e['week']}", f"archive/{e['season']}-week-{e['week']}.html"
    MANIFEST.write_text(json.dumps({"version": 1, "sheets": ordered}, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")

    if latest["key"] == key:
        (NFL_DIR / "atd.html").write_text(render(sheet, season, week, ""), encoding="utf-8")
        print(f"[atd] Week {week} is the current week: nfl-research/atd.html")
    print(f"[atd] archived as {archive.relative_to(ROOT)}; the week list has {len(ordered)} weeks")
    return archive


def why(r, env, dz_rank, implied_rank, defense, rank_on_board):
    p, b = r["plan"], r["b"]
    team, opp, pos = p["team"], p["opp"], b["pos"]
    e, d = env.get(team, {}), env.get(opp, {})
    td = b.get("td_chance")
    bits = []
    if pos == "QB":
        bits.append(f"{td}% to run one in: {float(r['avg'].get('rush_td') or 0):.1f} rushing touchdowns a game over his "
                    f"last {b['games']}, with {r['gl']:.1f} carries a game inside the 5.")
    else:
        work = "work inside the 20" if pos == "RB" else "red-zone targets and carries"
        bits.append(f"{td}% to score, on {b.get('rz_share', 0):.0f}% of {team}'s {work}"
                    + (f" and {r['gl']:.1f} goal-line carries a game" if r["gl"] >= 0.7 else "") + ".")
    if r["imp"] is not None:
        bits.append(f"{team} is implied for {r['imp']:.1f} points, {ordinal(implied_rank.get(team, 0))} of the week, "
                    f"and reaches the red zone {e.get('rz_trips', 0):.1f} times a game.")
    dz = dz_rank.get(opp)
    if d.get("def_rz_td") is not None and dz:
        soft = ("among the softest" if dz >= 25 else "softer than average" if dz >= 17
                else "tougher than average" if dz >= 9 else "one of the stingiest")
        bits.append(f"{opp} lets {d['def_rz_td']:.0f}% of red-zone trips end in a touchdown, {soft} ({dz} of 32).")
    if pos != "QB" and r["edge"] is not None and abs(r["edge"]) >= 0.10:
        more = "more" if r["edge"] > 0 else "less"
        bits.append(f"Against {b['role']}s it has given up {abs(round(100 * r['edge']))}% {more} than league.")
    if r["td2"] is not None:
        bits.append(f"The listed line is 2+ touchdowns: {r['td2']}% on the same rate.")
    return " ".join(bits)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--season", type=int, required=True)
    ap.add_argument("--week", type=int, required=True)
    args = ap.parse_args()
    build(args.season, args.week)


if __name__ == "__main__":
    main()
