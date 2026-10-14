"""Build the weekly Anytime-TD cheat sheet page from the slate and the week's play list.

    python -m nfl_research.atd_sheet --season 2026 --week 2

Inputs
    nfl_research/atd_weeks/<season>-W<week>.txt   the plays, as exported from the
                                                 Research tab's Prop List
    preview/data/nfl-research-<season>-W<week>.json   the slate (fetch-nfl-research-slate.py)
    nfl_research/atd_weeks/defense-<season>-W<week>.csv   optional team-defense scoring
                                                 table; its TARGET verdicts mark the
                                                 exploitable defenses
    nfl_research/atd_weeks/odds-<season>-W<week>.csv   optional PropFinder "TD Matchups"
                                                 slate export; its Best Odds column is the
                                                 best anytime-TD price, which the value
                                                 picks compare against
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


def load_odds_csv(path: Path) -> tuple[dict[tuple[str, str], dict], str]:
    """(name, team) -> {price: best anytime-TD price (American), odd: True when that
    price is out of line with the market}, and when the prices were captured.

    "Out of line": the best price is the longest any book offers, so one boosted or
    stale line can land in it. The export also carries PropFinder's projected TDs a
    game; across a slate the best price implies about 1.1x the chance that projection
    gives. A price implying under ODD_PRICE of it (Bijan Robinson at +248 against a
    64% projection) is shown but flagged, and never called value.

    The export opens with a "Position,All" line and a blank before the real header
    ("#,Kickoff,Player,..."). A "Captured,<when>" line added above it records the
    time the prices were pulled -- prices move, so the sheet says how old they are."""
    if not path.exists():
        return {}, ""
    lines = io.open(path, encoding="utf-8-sig").read().splitlines()
    captured = next((l.split(",", 1)[1].strip() for l in lines if l.startswith("Captured,")), "")
    start = next((i for i, l in enumerate(lines) if l.startswith("#,")), None)
    if start is None:
        return {}, captured
    out = {}
    for r in csv.DictReader(lines[start:]):
        price = (r.get("Best Odds") or "").strip().replace("+", "")
        if not re.fullmatch(r"-?\d+", price):
            continue
        odd = False
        try:
            proj = float(r.get("Proj TD/G") or "")
        except ValueError:
            proj = None
        # a QB's projection counts his passing touchdowns, so it cannot judge his price
        if proj and r.get("Pos") != "QB":
            pf = 1 - math.exp(-proj)
            odd = pf >= 0.05 and implied_chance(int(price)) < ODD_PRICE * pf
        out[(norm(r["Player"]), TEAM_FIX.get(r["Team"], r["Team"]))] = {"price": int(price), "odd": odd}
    return out, captured


ODD_PRICE = 0.6


def load_insights_csv(path: Path) -> dict:
    """Keep workload and matchup evidence, including players without an odds quote."""
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("#,")), None)
    if start is None:
        return {}
    def number(value):
        match = re.search(r"[-+]?\d+(?:\.\d+)?", str(value or "").replace("−", "-"))
        return float(match.group()) if match else None
    out = {}
    for row in csv.DictReader(lines[start:]):
        out[(norm(row["Player"]), TEAM_FIX.get(row["Team"], row["Team"]))] = {
            "volume": number(row.get("Vol")),
            "volume_unit": "targets" if "tgt" in (row.get("Vol") or "") else "touches",
            "low_volume": bool((row.get("Low Volume") or "").strip()),
            "rz_looks": number(row.get("RZ Looks/G")),
            "role_leak": number(row.get("Role Leak")),
            "alignment_leak": number(row.get("Alignment Leak")),
            "baseline": number(row.get("His TD/G")),
            "projected": number(row.get("Proj TD/G")),
            "delta": number(row.get("Delta")),
        }
    return out


def implied_chance(american: int) -> float:
    """The chance a price implies, vig included -- the bar a bet has to clear."""
    return 100 / (american + 100) if american > 0 else -american / (-american + 100)


def calibrate(season: int, week: int) -> dict:
    """How far to trim the model so its TD chances match what actually happened.

    Every archived sheet of this season before `week` is graded against nflverse box
    scores (any touchdown, or a rushing one for a QB rush line). One factor `c` scales
    each player's expected touchdowns: c below 1 means the model has run hot. It is
    re-fitted every build; under 100 graded plays it stays at 1. Over-1.5 lines are left
    out -- they grade a different bet.

    The trim has to earn its place. Each graded week is also predicted by the trim fitted
    on the weeks before it, and the trim is used only if those unseen-week predictions
    beat the untrimmed chances. On 10/14 they did not: Week 2 ran hot, the trims fitted
    from it ran too low, and Weeks 3-5 scored 35% against an untrimmed 36%."""
    out = {"c": 1.0, "n": 0, "hit": None, "said": None, "fit": 1.0, "checked": None}
    rows = []
    try:
        stats = nfl.load_player_stats(seasons=season, summary_level="week").filter(
            pl.col("season_type") == "REG")
    except Exception:
        return out
    td_cols = [c for c in ("rushing_tds", "receiving_tds", "special_teams_tds", "fumble_recovery_tds")
               if c in stats.columns]
    box = {(r["week"], r["player_id"]): (r["rushing_tds"] or 0, sum((r[c] or 0) for c in td_cols))
           for r in stats.iter_rows(named=True)}
    for w in range(1, week):
        page = NFL_DIR / "archive" / f"{season}-week-{w}.html"
        if not page.exists():
            continue
        text = page.read_text(encoding="utf-8")
        at = text.find("var SHEET = ")
        if at < 0:
            continue
        try:
            sheet, _ = json.JSONDecoder().raw_decode(text[at + len("var SHEET = "):])
        except ValueError:
            continue
        # sheets built after calibration began record the untrimmed chance in `raw`
        for g in sheet.get("games", []):
            for plays in g["sides"].values():
                for p in plays:
                    m = p.get("m") or {}
                    td = m.get("raw", m.get("td"))
                    x = box.get((w, p.get("id")))
                    if td is None or x is None or p.get("line", 0.5) >= 1.5:
                        continue
                    rows.append((w, min(td / 100, 0.999), (x[0] if p.get("mk") == "rush_td" else x[1]) >= 1))
    if len(rows) < 100:
        out["n"] = len(rows)
        return out

    def loss(c, sample):
        total = 0.0
        for _, p, hit in sample:
            q = min(max(1 - math.exp(c * math.log(1 - p)), 1e-6), 1 - 1e-6)
            total -= math.log(q if hit else 1 - q)
        return total

    def fit(sample):
        return min((loss(k / 100, sample), k / 100) for k in range(50, 131))[1]

    # walk forward: every week after the first, predicted by the trim fitted before it
    held, raw_loss, trim_loss = [], 0.0, 0.0
    for w in sorted({r[0] for r in rows}):
        train, test = [r for r in rows if r[0] < w], [r for r in rows if r[0] == w]
        if len(train) < 50:
            continue
        c_then = fit(train)
        raw_loss += loss(1.0, test)
        trim_loss += loss(c_then, test)
        held += test
    out["fit"] = fit(rows)
    out["c"] = out["fit"] if held and trim_loss < raw_loss else 1.0
    if held:
        out["checked"] = {"n": len(held), "said": round(100 * sum(p for _, p, _ in held) / len(held), 1),
                          "hit": round(100 * sum(h for _, _, h in held) / len(held), 1),
                          "ll_raw": round(raw_loss / len(held), 4), "ll_trim": round(trim_loss / len(held), 4)}
    out["n"] = len(rows)
    out["hit"] = round(100 * sum(h for _, _, h in rows) / len(rows), 1)
    out["said"] = round(100 * sum(p for _, p, _ in rows) / len(rows), 1)
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


PBP_COLS = ["game_id", "season", "week", "season_type", "posteam", "defteam", "down", "ydstogo",
            "yardline_100", "play_type", "wp", "fixed_drive", "fixed_drive_result", "touchdown",
            "rush_touchdown", "pass_touchdown"]


def load_recent_pbp(seasons: list[int]) -> pl.DataFrame:
    parts = []
    for s_ in seasons:
        try:
            parts.append(nfl.load_pbp(seasons=[s_]).select(PBP_COLS))
        except Exception:
            pass
    if not parts:
        return pl.DataFrame()
    pbp = pl.concat(parts, how="diagonal_relaxed").filter(pl.col("season_type") == "REG")
    return pbp.with_columns(pl.col("posteam").replace(TEAM_FIX), pl.col("defteam").replace(TEAM_FIX))


def _last_games(pbp: pl.DataFrame, team_col: str, window: int) -> pl.DataFrame:
    """(team, season, week) for each team's last `window` games on that side of the ball."""
    return (pbp.filter(pl.col(team_col).is_not_null()).select([team_col, "season", "week"]).unique()
            .sort(["season", "week"]).group_by(team_col).tail(window))


def fourth_down_aggression(pbp: pl.DataFrame, window: int = 17) -> dict[str, float]:
    """Share of 4th-and-3-or-less snaps past a team's own 40 where it went for it,
    over each offense's last `window` games, with the game still in the balance."""
    if pbp.is_empty():
        return {}
    games = _last_games(pbp, "posteam", window)
    snaps = pbp.join(games, on=["posteam", "season", "week"], how="inner").filter(
        (pl.col("down") == 4) & (pl.col("ydstogo") <= 3) & (pl.col("yardline_100") <= 60)
        & pl.col("wp").is_between(0.10, 0.90)
        & pl.col("play_type").is_in(["run", "pass", "punt", "field_goal"])
    )
    rates = snaps.group_by("posteam").agg(
        (pl.col("play_type").is_in(["run", "pass"]).sum() / pl.len()).alias("go")
    )
    return {r["posteam"]: float(r["go"]) for r in rates.iter_rows(named=True)}


OPENING_DRIVES = 2      # "early" means each offense's first two possessions
OPENING_PRIOR = 20      # drives of league average mixed into every team's opening rate


def game_context(pbp: pl.DataFrame, seasons: list[int], window: int = 17) -> dict:
    """What the first-touchdown model and the exploitable-defense flag need, all from
    each team's last `window` games:

      td_per_point  offensive touchdowns per point scored, league-wide -- turns an
                    implied total into expected offensive touchdowns
      other_td_pg   defensive and special-teams touchdowns per game, both teams
      open_off[t]   share of t's first two drives of a game that ended in a touchdown,
                    regressed toward league with OPENING_PRIOR drives
      open_def[t]   the same allowed by t's defense
      open_league   the league rate both are regressed toward
      pa_pg[t]      points t's defense allowed per game
    """
    out = {"td_per_point": 0.105, "other_td_pg": 0.2, "open_off": {}, "open_def": {},
           "open_league": 0.22, "pa_pg": {}}
    if pbp.is_empty():
        return out

    tds = pbp.filter(pl.col("touchdown") == 1)
    off_tds = tds.filter((pl.col("rush_touchdown") == 1) | (pl.col("pass_touchdown") == 1)).height
    other_tds = tds.height - off_tds
    n_games = pbp.select(pl.col("game_id").n_unique()).item()

    try:
        sched = nfl.load_schedules(seasons=seasons).filter(
            (pl.col("game_type") == "REG") & pl.col("home_score").is_not_null())
    except Exception:
        sched = pl.DataFrame()
    if sched.height:
        points = sched.select((pl.col("home_score") + pl.col("away_score")).sum()).item()
        if points:
            out["td_per_point"] = off_tds / points
        sides = pl.concat([
            sched.select(pl.col("home_team").alias("def"), "season", "week", pl.col("away_score").alias("pa")),
            sched.select(pl.col("away_team").alias("def"), "season", "week", pl.col("home_score").alias("pa")),
        ]).with_columns(pl.col("def").replace(TEAM_FIX)).sort(["season", "week"]).group_by("def").tail(window)
        for r in sides.group_by("def").agg(pl.col("pa").mean().alias("pa")).iter_rows(named=True):
            out["pa_pg"][r["def"]] = float(r["pa"])
    if n_games:
        out["other_td_pg"] = other_tds / n_games

    # each offense's first two possessions of every game, and how they ended
    drives = (pbp.filter(pl.col("posteam").is_not_null() & pl.col("fixed_drive").is_not_null())
              .group_by(["game_id", "season", "week", "posteam", "defteam", "fixed_drive"])
              .agg(pl.col("fixed_drive_result").first().alias("result"))
              .sort("fixed_drive").group_by(["game_id", "posteam"]).head(OPENING_DRIVES)
              .with_columns((pl.col("result") == "Touchdown").cast(pl.Int32).alias("td")))
    league = drives.select(pl.col("td").mean()).item() or 0.22
    out["open_league"] = float(league)
    for side, col in (("open_off", "posteam"), ("open_def", "defteam")):
        recent = drives.join(_last_games(drives, col, window), on=[col, "season", "week"], how="inner")
        for r in recent.group_by(col).agg(pl.col("td").sum().alias("td"), pl.len().alias("n")).iter_rows(named=True):
            out[side][r[col]] = (r["td"] + OPENING_PRIOR * league) / (r["n"] + OPENING_PRIOR)
    return out


def first_td_team(ctx: dict, team: str, opp: str, implied: dict) -> tuple[float, float]:
    """(chance `team` scores the game's first touchdown, its expected offensive TDs).

    Touchdowns are treated as arriving at a steady rate through the game, so the first
    one belongs to each source in proportion to its rate: this offense, the other one,
    and the defensive/special-teams touchdowns either side can score. An offense's rate
    is its implied points turned into touchdowns, nudged by how often it scores on its
    opening drives against how often this defense allows it -- the first TD is usually
    an early one."""
    lg = ctx["open_league"] or 0.22

    def rate(off, dfn):
        base = ctx["td_per_point"] * (implied.get(off) or LEAGUE_POINTS)
        early = (ctx["open_off"].get(off, lg) / lg) * (ctx["open_def"].get(dfn, lg) / lg)
        return base, base * min(1.25, max(0.8, early ** 0.5))

    base_a, lam_a = rate(team, opp)
    _, lam_b = rate(opp, team)
    total = lam_a + lam_b + ctx["other_td_pg"]
    return lam_a / total * (1 - math.exp(-total)), base_a


def fair_odds(p: float) -> str:
    """American odds with no margin -- what the price would be if this chance were right."""
    if p <= 0 or p >= 1:
        return ""
    if p >= 0.5:
        return f"-{round(100 * p / (1 - p) / 5) * 5}"
    return f"+{round(100 * (1 - p) / p / 5) * 5}"


# ── the sheet ──────────────────────────────────────────────────────────────────
def build(season: int, week: int) -> Path:
    slate_path = ROOT / "preview" / "data" / f"nfl-research-{season}-W{week}.json"
    slate = json.loads(slate_path.read_text(encoding="utf-8"))
    plan = load_plays(WEEKS / f"{season}-W{week}.txt")
    defense = load_defense_csv(WEEKS / f"defense-{season}-W{week}.csv")
    odds, odds_captured = load_odds_csv(WEEKS / f"odds-{season}-W{week}.csv")
    insights = load_insights_csv(WEEKS / f"odds-{season}-W{week}.csv")
    cal = calibrate(season, week)
    c = cal["c"]
    chk = cal.get("checked") or {}
    print(f"[atd] calibration: x{c:.2f} on expected TDs (fitted x{cal['fit']:.2f} from {cal['n']} graded plays, "
          f"model said {cal['said']}%, {cal['hit']}% hit; on unseen weeks raw {chk.get('ll_raw')} vs trim "
          f"{chk.get('ll_trim')} log loss over {chk.get('n')}); {len(odds)} prices"
          + (f" captured {odds_captured}" if odds_captured else ""))
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

    players = nfl.load_players().select(["gsis_id", "espn_id", "display_name", "latest_team"])
    espn_of = {g: e for g, e in zip(players["gsis_id"].to_list(), players["espn_id"].to_list()) if g and e}
    # name + team -> gsis id, for a listed player the depth chart has since dropped
    gsis_by_name = {(norm(n), TEAM_FIX.get(t, t)): g for n, t, g in zip(
        players["display_name"].to_list(), players["latest_team"].to_list(), players["gsis_id"].to_list())
        if n and t and g}

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
                # A player on the list stays on the sheet even after the club drops him
                # from its depth chart -- usually a move to injured reserve. He is shown
                # with his ESPN status and nothing rated, so the list is never silently short.
                problems.append(f"{p['name']} ({p['team']}) is off the depth chart; listed without numbers")
                stub = {"player_id": gsis_by_name.get((norm(p["name"]), p["team"])), "name": p["name"],
                        "role": p["slot"], "pos": p["slot"][:2], "team": p["team"], "opp": p["opp"],
                        "games": 0, "xtd": 0.0, "matchup": {}, "share": None, "share_l3": None}
                rows.append({"plan": p, "game": key, "b": stub, "avg": {}, "off_chart": True})
                continue
            b = hit[0]
            if b["role"] != p["slot"]:
                problems.append(f"{p['name']}: listed {p['slot']}, depth chart has {b['role']}")
            side = "away_offense" if p["team"] == g["away"] else "home_offense"
            pos = b["pos"]
            off = next((o for o in g[side].get(pos, []) if o.get("player_id") == b.get("player_id")), None)
            avg = (off or {}).get("stats") or {}
            rows.append({"plan": p, "game": key, "b": b, "avg": avg, "log": (off or {}).get("log") or []})
    if problems:
        print("[atd] CHECK:\n  " + "\n  ".join(problems))

    listed_teams = {r["plan"]["team"] for r in rows}
    wanted = {espn_of[r["b"]["player_id"]] for r in rows if r["b"].get("player_id") in espn_of}
    injuries = espn_injuries(listed_teams, wanted)
    print(f"[atd] ESPN injury feed: {len(injuries)} listed players carry an entry")
    pbp = load_recent_pbp([season - 1, season])
    aggression = fourth_down_aggression(pbp)
    ctx = game_context(pbp, [season - 1, season])
    print(f"[atd] context: {ctx['td_per_point']:.3f} offensive TDs per point, "
          f"{ctx['other_td_pg']:.2f} non-offensive TDs a game, opening-drive TD rate {ctx['open_league']:.1%}")
    # ties broken by name, so the top-ten cut is the same on every run
    agg_rank = {t: i + 1 for i, (t, _) in enumerate(sorted(aggression.items(), key=lambda kv: (-kv[1], kv[0])))}

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
        # The bet itself: an over-1.5 line needs two, so it ranks on the chance of two --
        # a 60% anytime scorer is a 23% over-1.5, and the favourites and Top 5 say so.
        r["bet"] = r["score"] if p["line"] < 1.5 else 1 - math.exp(-lam) * (1 + lam)
        r["small"] = (b.get("games") or 0) < MIN_GAMES
        edge = None
        if m.get("index") is not None and td_index is not None:
            edge = 0.5 * (m["index"] - 1) + 0.5 * (td_index - 1)
        r["edge"] = edge
        # Every chance this sheet prints runs on the trimmed rate, so the TD %, the 2+
        # chance and the value edge all agree with each other and with how the model
        # has actually hit. (Rankings are unchanged: the trim is the same for everyone.)
        lam_raw = c * xtd
        r["td_raw"] = 1 - math.exp(-xtd)
        r["td_cal"] = 1 - math.exp(-lam_raw)
        r["td2"] = round(100 * (1 - math.exp(-lam_raw) * (1 + lam_raw))) if p["line"] >= 1.5 else None
        # Two or more: the same expected-touchdown number behind his TD %, so the two
        # never disagree -- one minus the chance of none and of exactly one.
        r["two"] = 1 - math.exp(-lam_raw) * (1 + lam_raw)
        # The market: the best anytime price, the chance it implies, and our edge over it.
        # An over-1.5 line is a different bet from the anytime price, so it gets no edge.
        quote = odds.get((norm(p["name"]), team)) or {}
        r["book"] = quote.get("price")
        r["odd_price"] = bool(quote.get("odd"))
        r["p_book"] = implied_chance(r["book"]) if r["book"] is not None else None
        r["edge_pts"] = (100 * (r["td_cal"] - r["p_book"])
                         if r["p_book"] is not None and p["line"] < 1.5 else None)
        # how often he actually did it over his last 17 games (rushing only for a QB line)
        key_td = "rush_td" if p["market"] == "rush_td" else "td"
        recent = r.get("log", [])[-17:]
        r["multi"] = (sum(1 for g in recent if (g.get("stats") or {}).get(key_td, 0) >= 2), len(recent))
        r["gl"] = float(avg.get("i5_car") or 0.0)
        r["dz"] = dz_rank.get(opp)
        r["imp"] = imp
        r["trend"] = (b.get("share_l3") or 0) - (b.get("share") or 0) if b.get("share") is not None else 0.0

    # ── first touchdown of the game ──
    # His team's chance to score first, times his share of its expected touchdowns. The
    # share's denominator is every lineup player's expected TDs plus whatever the team is
    # expected to score beyond them (backups, fullbacks, trick plays) -- at least a tenth.
    team_first, team_lambda, lineup_xtd = {}, {}, {}
    for key, g in by_game.items():
        for t, o in ((g["away"], g["home"]), (g["home"], g["away"])):
            team_first[t], team_lambda[t] = first_td_team(ctx, t, o, implied)
            lineup_xtd[t] = sum(float(b.get("xtd") or 0) for b in g["board"]["players"] if b["team"] == t)
    for r in rows:
        t = r["plan"]["team"]
        others = max(0.1 * team_lambda[t], team_lambda[t] - lineup_xtd[t])
        denom = lineup_xtd[t] + others
        share = float(r["b"].get("xtd") or 0) / denom if denom else 0.0
        r["td_share"] = share
        r["first"] = team_first[t] * share

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

    ranked = sorted([r for r in rows if r["eligible"] and r["status"] != "q"], key=lambda r: -r["bet"])
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
        if id(r) in fav_ids or not r["eligible"] or r["plan"]["line"] >= 1.5:
            continue
        slot = r["b"]["role"][:2] + ("1" if r["b"]["role"].endswith("1") else "2+")
        above = r["score"] - medians.get(slot, r["score"])
        secondary = not r["b"]["role"].endswith("1") or r["b"]["pos"] == "TE"
        growing = secondary and r["trend"] >= 5 and "mat" in r["tags"] and r["score"] >= 0.25
        if (secondary and above >= 0.08 and r["score"] >= 0.28) or growing:
            r["tags"].insert(0, "val")

    # 💰 value, as on the NHL sheet: our chance clears the chance the best price implies
    # by VALUE_EDGE points or more, AND the matchup is on his side -- a good price on a
    # player walking into a wall is a trap. Healthy, rated, a normal-looking price.
    # A shrinking role is never value either: his 17-game chance still carries the bigger
    # job, while the price is set on the one he has now (RJ Harvey, Week 6: RB1 in 2025,
    # 31% of DEN's carries over 17 games, 17% over the last 3, 2-7 carries a game).
    for r in rows:
        r["match"] = matchup_score(r, len(dz_rank))
        r["usage_z"] = usage_z(r["b"])
    shrinking = [r for r in rows if r.get("edge_pts") is not None and r["usage_z"] is not None and r["usage_z"] <= -2]
    # Plus money only (the owner, 10/14): a favourite's price is already short, so even a
    # real edge pays too little to headline a value section.
    priced = [r for r in rows if r["eligible"] and r["status"] == "" and r.get("edge_pts") is not None
              and not r["odd_price"] and r not in shrinking and r["book"] > 0]
    # Ranked on value and matchup together (the user, 10/14): the edge counts in full
    # only in the softest matchup, so +11 in a 94/100 spot outranks +11 in a 51/100 one.
    rank_key = lambda r: (-r["edge_pts"] * r["match"] / 100, r["plan"]["name"])  # noqa: E731
    value_rows = sorted([r for r in priced if r["edge_pts"] >= VALUE_EDGE and r["match"] >= MATCHUP_FLOOR],
                        key=rank_key)
    walled = sorted([r for r in priced if r["edge_pts"] >= VALUE_EDGE and r["match"] < MATCHUP_FLOOR],
                    key=lambda r: (-r["edge_pts"], r["plan"]["name"]))
    # A thin week fills the open slots with the next positive edges in a good matchup,
    # shown as "Underpriced" and never tagged Value.
    close_rows = sorted([r for r in priced if 0 < r["edge_pts"] < VALUE_EDGE and r["match"] >= MATCHUP_FLOOR],
                        key=rank_key)[:max(0, 5 - len(value_rows))]
    for r in value_rows:
        r["tags"].append("edge")
    value5 = [{"id": r["b"]["player_id"], "edge": round(r["edge_pts"], 1), "ours": round(100 * r["td_cal"], 1),
               "book": fmt_price(r["book"]), "implied": round(100 * r["p_book"], 1), "close": close,
               "match": r["match"], "match_line": matchup_line(r, env, len(dz_rank)), "game_line": game_line(r, env)}
              for rs, close in ((value_rows[:5], False), (close_rows, True)) for r in rs]

    # ✈️ exploitable defenses: the scoring table's TARGET verdict when a table is
    # supplied for the week; otherwise the ten softest defenses on our own numbers --
    # points allowed a game and red-zone touchdown rate allowed, each ranked, averaged.
    if defense:
        exp_teams = {t for t, d in defense.items() if d["verdict"] == "TARGET"}
        exp_source = "csv"
    else:
        def pct_rank(values):
            # tied values share the average of their ranks, so the order the data
            # happened to arrive in can never move a team across the cut
            order = sorted(values.values())
            n = len(order)
            if n < 2:
                return {}
            first = {}
            for i, v in enumerate(order):
                first.setdefault(v, i)
            return {t: (first[v] + order.count(v) / 2 - 0.5) / (n - 1) for t, v in values.items()}
        pa = pct_rank(ctx["pa_pg"])
        rz = pct_rank({t: v["def_rz_td"] for t, v in env.items() if v.get("def_rz_td") is not None})
        soft = {t: (pa[t] + rz[t]) / 2 for t in pa if t in rz}
        # a tie at the cut goes to the defense softer on opening drives, then by name
        exp_teams = set(sorted(soft, key=lambda t: (-soft[t], -ctx["open_def"].get(t, 0), t))[:10])
        exp_source = "computed"
    print(f"[atd] exploitable defenses ({exp_source}): {', '.join(sorted(exp_teams))}")

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

    two_ranked = sorted([r for r in rows if r["eligible"] and r["status"] == ""], key=lambda r: -r["two"])[:5]
    two5 = [{"id": r["b"]["player_id"], "pct": round(100 * r["two"], 1), "fair": fair_odds(r["two"]),
             "why": why_two(r, env)} for r in two_ranked]
    first_ranked = sorted([r for r in rows if r["eligible"] and r["status"] == ""], key=lambda r: -r["first"])[:5]
    first5 = [{"id": r["b"]["player_id"], "pct": round(100 * r["first"], 1), "fair": fair_odds(r["first"]),
               "why": why_first(r, ctx, team_first, implied)} for r in first_ranked]

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
                "n": p["name"], "id": None if r.get("off_chart") else b.get("player_id"),
                "off": bool(r.get("off_chart")), "p": b["role"], "pos": b["pos"],
                "mk": p["market"], "line": p["line"], "t": r["tags"], "st": r["status"], "inj": r["injury"],
                "stl": r["status_label"],
                "m": {
                    "td": None if r.get("off_chart") else round(100 * r["td_cal"]),
                    "raw": None if r.get("off_chart") else round(100 * r["td_raw"]),
                    "td2": r["td2"],
                    "book": fmt_price(r["book"]), "pbook": None if r["p_book"] is None else round(100 * r["p_book"]),
                    "odd": r["odd_price"],
                    "edge": None if r.get("edge_pts") is None else round(r["edge_pts"]), "rz": b.get("rz_share"), "gl": round(r["gl"], 1),
                    "dz": r["dz"], "dedge": None if r["edge"] is None else round(100 * r["edge"]),
                    "g": b.get("games"), "tg": b.get("team_games"), "new": bool(b.get("new_team")),
                    "small": r["small"], "trend": round(r["trend"], 1),
                    "ftd": None if r.get("off_chart") or r["small"] else round(100 * r["first"], 1),
                    "ftd_fair": None if r.get("off_chart") or r["small"] else fair_odds(r["first"]),
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
    for r in [x for x in rows if not x.get("off_chart")]:
        b = r["b"]
        stats = list((b.get("proj") or {}).keys())
        m = b.get("matchup") or {}
        cards[b["player_id"]] = {
            **{k: b.get(k) for k in CARD_FIELDS},
            "csv": insights.get((norm(r["plan"]["name"]), b["team"]), {}),
            "workload_log": [{k: g.get(k) for k in ("season", "week", "team", "rush_att", "rec", "tgt")}
                             for g in (b.get("log") or [])],
            "td_chance": round(100 * r["td_cal"]),
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
        "games": games_out, "top5": top5, "first5": first5, "two5": two5, "value5": value5, "value_min_edge": VALUE_EDGE,
        "value_count": len(value_rows), "value_match_floor": MATCHUP_FLOOR, "teams": len(dz_rank), "tend": tend,
        "odds_captured": odds_captured, "has_odds": bool(odds),
        "calibration": {"c": c, "fit": cal["fit"], "n": cal["n"], "hit": cal["hit"], "said": cal["said"],
                        "checked": cal.get("checked")},
        "exp_source": exp_source,
        "cards": cards, "env": card_env, "leaks": card_leaks,
        "defense_source": bool(defense),
    }
    out = publish(sheet, season, week)

    n_plays = sum(len(s) for g in games_out for s in g["sides"].values())
    counts = {k: sum(1 for r in rows if k in r["tags"]) for k in ("fav", "val", "rz", "mat")}
    print(f"[atd] {len(games_out)} games, {n_plays} plays, tags {counts}, "
          f"{sum(1 for r in rows if r['status'])} with an injury status, {sum(1 for r in rows if r['small'])} small samples")
    print("[atd] top 5: " + ", ".join(r["plan"]["name"] for r in top))
    print("[atd] prices flagged out of line: " + ", ".join(
        f"{r['plan']['name']} {fmt_price(r['book'])}" for r in rows if r.get("odd_price")))
    print("[atd] value plays (" + str(len(value_rows)) + "): " + ", ".join(
        f"{r['plan']['name']} +{r['edge_pts']:.1f} ({100 * r['td_cal']:.0f}% vs {100 * r['p_book']:.0f}% at "
        f"{fmt_price(r['book'])}, matchup {r['match']}, ranks on {r['edge_pts'] * r['match'] / 100:.1f})" for r in value_rows))
    if close_rows:
        print("[atd] underpriced fill-ins: " + ", ".join(
            f"{r['plan']['name']} +{r['edge_pts']:.1f} (matchup {r['match']})" for r in close_rows))
    if shrinking:
        print("[atd] left off for a shrinking role: " + ", ".join(
            f"{r['plan']['name']} +{r['edge_pts']:.1f} (usage {r['usage_z']:+.1f} SD)" for r in shrinking if r["edge_pts"] > 0))
    if walled:
        print("[atd] priced well but left off for the matchup: " + ", ".join(
            f"{r['plan']['name']} +{r['edge_pts']:.1f} (matchup {r['match']})" for r in walled))
    print("[atd] 2+ TD top 5: " + ", ".join(f"{r['plan']['name']} {100 * r['two']:.1f}% ({fair_odds(r['two'])}) "
                                          f"[{r['multi'][0]} of {r['multi'][1]}]" for r in two_ranked))
    print("[atd] first TD top 5: " + ", ".join(f"{r['plan']['name']} {100 * r['first']:.1f}% ({fair_odds(r['first'])})"
                                             for r in first_ranked))
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


VALUE_EDGE = 4.0   # points our trimmed chance must clear the price's implied chance by


def fmt_price(american_odds):
    if american_odds is None:
        return None
    return f"+{american_odds}" if american_odds > 0 else str(american_odds)


# ...and the matchup has to be on his side: the lane (what this defense gives up to his
# role) and the end zone (how often its red-zone trips allowed become touchdowns), each
# as a percentile of this week's defenses, averaged. 50 is an average draw.
MATCHUP_FLOOR = 50


# A club's targets and carries in a typical game: the denominators of a share.
TEAM_VOLUME = {"target share": 33, "carry share": 26}


def usage_z(b: dict) -> float | None:
    """How far his last three games' share sits from his longer share, in standard
    deviations of three games' chance swing -- the test behind the sheet's usage arrow
    (atd-insights.js). None for a new team, a short sample or no share (quarterbacks)."""
    share, recent = b.get("share"), b.get("share_l3")
    if share is None or recent is None or not 0 < share < 100 or b.get("new_team") or (b.get("games") or 0) < 4:
        return None
    n = 3 * TEAM_VOLUME.get(b.get("share_kind"), 30)
    return (recent - share) / math.sqrt(share * (100 - share) / n)


def matchup_score(r: dict, teams: int) -> int:
    mu = r["b"].get("matchup") or {}
    lane = (mu["rank"] - 1) / (mu["of"] - 1) if mu.get("rank") and (mu.get("of") or 0) > 1 else 0.5
    zone = (r["dz"] - 1) / (teams - 1) if r.get("dz") and teams > 1 else 0.5
    return round(100 * (lane + zone) / 2)


def matchup_line(r: dict, env: dict, teams: int) -> str:
    """The lane he runs into and the red zone at the end of it, in two plain clauses."""
    p, b = r["plan"], r["b"]
    opp, role = p["opp"], b["role"]
    mu, d = b.get("matchup") or {}, env.get(p["opp"], {})
    bits = []
    if mu.get("index") is not None:
        pct = round((mu["index"] - 1) * 100)
        lane = ("about what an average defense allows" if abs(pct) < 4 else
                f"{abs(pct)}% {'more' if pct > 0 else 'less'} than an average defense")
        bits.append(f"{opp} gives up {lane} to {role}s")
    if d.get("def_rz_td") is not None and r.get("dz"):
        soft = ("one of the softest" if r["dz"] > 0.75 * teams else "softer than average" if r["dz"] > teams / 2
                else "tougher than average" if r["dz"] > teams / 4 else "one of the stingiest")
        bits.append(f"lets {d['def_rz_td']:.0f}% of red-zone trips score, {soft}")
    return (", and ".join(bits) + ".") if bits else "No matchup numbers for this defense yet."


def game_line(r: dict, env: dict) -> str:
    """His own role, then how often he has actually scored -- this season said apart, so a
    chance that leans on last year (Trevor Lawrence, Week 6) says so on the card."""
    p, b = r["plan"], r["b"]
    team = p["team"]
    e = env.get(team, {})
    bits = []
    if b.get("share") is not None:
        bits.append(f"{b['share']:.0f}% {b.get('share_kind') or 'share'} over his last {b.get('games')} games")
    if b["pos"] != "QB" and b.get("rz_share") is not None:
        bits.append(f"{b['rz_share']:.0f}% of {team}'s red-zone work")
    if r["gl"] >= 0.5:
        bits.append(f"{r['gl']:.1f} carries a game inside the 5")
    out = []
    if bits:
        out.append(bits[0][0].upper() + bits[0][1:] + "".join(", " + x for x in bits[1:]) + ".")
    rush = p["market"] == "rush_td"
    recent = (r.get("log") or [])[-17:]
    if recent:
        key = "rush_td" if rush else "td"
        scored = sum(1 for g in recent if (g.get("stats") or {}).get(key, 0) >= 1)
        this = [g for g in recent if g.get("season") == recent[-1].get("season")]
        this_scored = sum(1 for g in this if (g.get("stats") or {}).get(key, 0) >= 1)
        what = "Rushed for a TD" if rush else "Scored"
        line = f"{what} in {scored} of his last {len(recent)} games"
        if len(this) < len(recent):
            line += f", {'none' if this_scored == 0 else this_scored} of {len(this)} this season"
        out.append(line + ".")
    out.append(f"{team} reaches the red zone {e.get('rz_trips', 0):.1f} times a game.")
    return " ".join(out)


def why_two(r, env):
    p, b = r["plan"], r["b"]
    team, opp, pos = p["team"], p["opp"], b["pos"]
    x = -math.log(1 - r["td_cal"]) if r["td_cal"] < 1 else float(b.get("xtd") or 0)
    e, d = env.get(team, {}), env.get(opp, {})
    what = "rushing touchdowns" if p["market"] == "rush_td" else "touchdowns"
    bits = [f"He projects for {x:.2f} {what} this game."]
    if pos == "QB":
        bits.append(f"That is {r['gl']:.1f} carries a game inside the 5 against a {opp} defense that lets "
                    f"{d.get('def_rz_td', 0):.0f}% of red-zone trips score.")
    else:
        work = f"{b.get('rz_share', 0):.0f}% of {team}'s red-zone work"
        if r["gl"] >= 0.7:
            work += f" and {r['gl']:.1f} goal-line carries a game"
        bits.append(f"He holds {work}; {team} reaches the 20 {e.get('rz_trips', 0):.1f} times a game and "
                    f"{opp} lets {d.get('def_rz_td', 0):.0f}% of those trips score.")
    done, games = r["multi"]
    if games:
        bits.append(f"He scored 2+ in {done} of his last {games} games.")
    return " ".join(bits)


def why_first(r, ctx, team_first, implied):
    p, b = r["plan"], r["b"]
    team, opp = p["team"], p["opp"]
    lg = ctx["open_league"]
    off, dfn = ctx["open_off"].get(team), ctx["open_def"].get(opp)
    # the card prints the chance and fair price above this, so the words start with why
    bits = []
    lead = f"{team} scores first {100 * team_first[team]:.0f}% of the time on these numbers"
    if implied.get(team) is not None and implied.get(opp) is not None:
        lead += f" — implied {implied[team]:.1f} to {implied[opp]:.1f}"
    bits.append(lead + ".")
    if off is not None and dfn is not None:
        bits.append(f"Its first two drives end in a touchdown {100 * off:.0f}% of the time, and {opp} allows "
                    f"{100 * dfn:.0f}% on its own (league {100 * lg:.0f}%).")
    lead_in = "His own runs make up" if b["pos"] == "QB" else "He carries"
    bits.append(f"{lead_in} {100 * r['td_share']:.0f}% of {team}'s expected touchdowns.")
    return " ".join(bits)


def why(r, env, dz_rank, implied_rank, defense, rank_on_board):
    p, b = r["plan"], r["b"]
    team, opp, pos = p["team"], p["opp"], b["pos"]
    e, d = env.get(team, {}), env.get(opp, {})
    td = round(100 * r["td_cal"])
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
        bits.append(f"{opp} lets {d['def_rz_td']:.0f}% of red-zone trips end in a touchdown, {soft} ({dz} of {len(dz_rank)}).")
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
