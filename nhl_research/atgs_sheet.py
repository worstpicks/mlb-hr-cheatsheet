"""Build the Anytime Goal Scorer cheat sheet from a slate.

    python -m nhl_research.atgs_sheet --date 2026-09-29

The page the hand-built nhl_cheatsheet_*_revamp.html sheets were: the Worst
Pickz rating model, the score bands, top rated targets, plus-money value,
profile warnings, then every play by matchup. The difference is that nothing
here is pasted -- the old sheets were scored off a board copied in by hand (and
carried a note about team-label noise in the feed); this reads the slate the
research tab already built, so the numbers and the uniforms are the same ones
on the board.

Inputs
    preview/data/nhl-research-<date>.json   the slate (fetch-nhl-research-slate.py)
    nhl_research/atgs_days/<date>.txt        optional: the day's plays, pasted as
                                             exported from the research tab's Prop
                                             List. With it, the sheet is those plays;
                                             without it, every rated forward.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from nhl_research.rating import WEIGHTS, build_scales, score_row, warnings_for

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "preview" / "data"
NHL_DIR = ROOT / "preview" / "nhl-research"
TEMPLATE = Path(__file__).resolve().parent / "templates" / "atgs_sheet.html"
MANIFEST = NHL_DIR / "atgs-manifest.json"
PLAYS_DIR = Path(__file__).resolve().parent / "atgs_days"

# One Prop List row, as the research tab exports it. The name and the line slot
# arrive glued together ("Carter VerhaegheC4"), and so do the matchup and the
# market ("FLA vs CAROver 0.5 Goals"), so the pattern pins the slot and the
# three-letter codes rather than relying on spaces.
PLAY_LINE = re.compile(
    r"^(?P<name>.+?)(?P<role>[CLRDG]\d+)\s*\u00b7\s*"
    r"(?P<team>[A-Z]{2,3})\s+vs\s+(?P<opp>[A-Z]{2,3})"
    r"(?P<side>Over|Under)\s+(?P<line>\d+(?:\.\d+)?)\s+(?P<market>.+?)\s*$"
)

# A skater needs this many games before he is rated rather than merely shown.
MIN_GAMES = 8
# Forwards carry the market. A defenseman scores on about four percent of his
# nights; he belongs on the research board for blocks and shots, not here.
SCORING_POS = ("C", "L", "R")


def norm_name(name: str) -> str:
    """"Juraj Slafkovsk\u00fd" and "Juraj Slafkovsky" are the same man."""
    text = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", text.lower())


def load_plays(date: str) -> list[dict] | None:
    """The day's plays from atgs_days/<date>.txt, or None when there is no list.

    Anything that is not a play row -- the game headers, the "x" remove buttons
    the export carries along -- simply does not match and is skipped.
    """
    path = PLAYS_DIR / f"{date}.txt"
    if not path.exists():
        return None
    plays = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        m = PLAY_LINE.match(raw.strip())
        if m:
            plays.append({
                "name": m["name"].strip(), "role": m["role"],
                "team": m["team"], "opp": m["opp"],
                "side": m["side"], "line": float(m["line"]), "market": m["market"].strip(),
            })
    return plays


def _stat(node: dict, key: str, default: float = 0.0) -> float:
    return float((node or {}).get(key) or default)


def _allowed_slot(allowed: dict, pos: str, rank: int) -> dict:
    """What this opponent gives up to that exact line slot, or to the group."""
    node = allowed.get(pos) or {}
    slot = (node.get("ranks") or {}).get(str(rank)) or {}
    if slot.get("gp"):
        return slot.get("stats") or {}
    return (node.get("overall") or {}).get("stats") or {}


def _starter(skaters: dict) -> dict:
    """The opponent's likely starter: the goalie with the most ice time.

    The NHL names starters an hour before puck drop, long after this builds, so
    the busiest goalie is the honest stand-in. Where a club has no goalie rows
    the matchup component scores neutral rather than inventing an edge.
    """
    goalies = skaters.get("G") or []
    return goalies[0] if goalies else {}


def collect(slate: dict) -> list[dict]:
    """One row per rateable skater on the slate, with every model input on it."""
    rows: list[dict] = []
    for game in slate.get("games") or []:
        for side, other in (("away", "home"), ("home", "away")):
            team, opp = game[side], game[other]
            allowed = game.get(f"{other}_allowed") or {}
            goalie = _starter(game.get(f"{other}_skaters") or {})
            g_stats = goalie.get("stats") or {}
            hd_sa = _stat(g_stats, "hd_sa")
            for pos in SCORING_POS:
                for player in (game.get(f"{side}_skaters") or {}).get(pos) or []:
                    stats = player.get("stats") or {}
                    rank = player.get("rank", 1)
                    slot = _allowed_slot(allowed, pos, rank)
                    log = player.get("log") or []
                    last5 = log[-5:]
                    g5 = sum(_stat(x.get("stats"), "g") for x in last5)
                    rows.append({
                        "id": f"{game['id']}-{player.get('player_id')}",
                        "player_id": player.get("player_id"),
                        "name": player.get("name", ""),
                        "pos": pos,
                        "rank": rank,
                        "role": f"{pos}{rank}",
                        "team": team,
                        "opp": opp,
                        "headshot": player.get("headshot", ""),
                        "game": f"{game['away']}@{game['home']}",
                        "games": int(player.get("gp") or 0),
                        "small": int(player.get("gp") or 0) < MIN_GAMES,
                        # his own profile
                        "g": round(_stat(stats, "g"), 3),
                        "sog": round(_stat(stats, "sog"), 2),
                        "icf": round(_stat(stats, "icf"), 2),
                        "iff": round(_stat(stats, "iff"), 2),
                        "iscf": round(_stat(stats, "iscf"), 2),
                        "ihdcf": round(_stat(stats, "ihdcf"), 2),
                        "toi": round(_stat(stats, "toi") / 60, 1),
                        "pp_p": round(_stat(stats, "pp_p"), 2),
                        "g5": g5,
                        "g5_rate": round(g5 / max(len(last5), 1), 3),
                        # the lane he is attacking
                        "opp_g": round(_stat(slot, "g"), 3),
                        "opp_sog": round(_stat(slot, "sog"), 2),
                        "opp_iscf": round(_stat(slot, "iscf"), 2),
                        # the goalie in his way
                        "g_name": goalie.get("name", ""),
                        "g_sv_pct": round(_stat(g_stats, "sv") / _stat(g_stats, "sa", 1), 4)
                                    if _stat(g_stats, "sa") else 0.0,
                        "g_hd_sv_pct": round(_stat(g_stats, "hd_sv") / hd_sa, 4) if hd_sa else 0.0,
                        "g_ga": round(_stat(g_stats, "ga"), 2),
                        "lines": player.get("lines") or {},
                    })
    return rows


def rate(rows: list[dict], slate_scales: dict) -> list[dict]:
    """Score every row, then tag it."""
    scales = build_scales(slate_scales)
    for r in rows:
        r.update(score_row(r, scales))
        r["warning"] = warnings_for(r, r["parts"])
        tags = []
        if r["band"] in ("elite", "strong"):
            tags.append("fav")
        if r["parts"]["defense"] / WEIGHTS["defense"] >= 0.75:
            tags.append("mat")
        if r["parts"]["volume"] / WEIGHTS["volume"] >= 0.78:
            tags.append("vol")
        if r["parts"]["quality"] / WEIGHTS["quality"] >= 0.78:
            tags.append("qual")
        if r["parts"]["goalie"] / WEIGHTS["goalie"] >= 0.75:
            tags.append("gl")
        if r["pp_p"] >= 0.35:
            tags.append("pp")
        if r["g5"] >= 3:
            tags.append("hot")
        r["tags"] = tags
        r["why"] = why(r)
    return rows


def pct3(value: float) -> str:
    """Save percentage as hockey writes it: .893, not 0.893."""
    return f"{value:.3f}".lstrip("0") if value < 1 else f"{value:.3f}"


def why(r: dict) -> str:
    """The edge, in the voice the hand-built sheets used."""
    bits = [
        f"{r['sog']:.1f} shots and {r['iscf']:.1f} scoring chances a game on "
        f"{r['toi']:.1f} minutes, scoring {r['g']:.2f} a night over his last {r['games']}."
    ]
    if r["parts"]["defense"] / WEIGHTS["defense"] >= 0.7:
        bits.append(f"{r['opp']} leaks {r['opp_g']:.2f} goals and {r['opp_sog']:.1f} shots "
                    f"a game to {r['role']}s.")
    elif r["parts"]["defense"] / WEIGHTS["defense"] <= 0.45:
        bits.append(f"{r['opp']} holds {r['role']}s to {r['opp_g']:.2f} goals a game.")
    if r["g_name"] and r["g_sv_pct"]:
        trend = "a leaking" if r["parts"]["goalie"] / WEIGHTS["goalie"] >= 0.7 else "a steady"
        bits.append(f"{r['g_name']} is {trend} {pct3(r['g_sv_pct'])} with a "
                    f"{pct3(r['g_hd_sv_pct'])} high-danger rate.")
    if r["pp_p"] >= 0.35:
        bits.append(f"He works the power play for {r['pp_p']:.2f} points a game.")
    if r["g5"] >= 3:
        bits.append(f"{int(r['g5'])} goals in his last five.")
    return " ".join(bits)


def build_sheet(date: str) -> dict:
    path = DATA / f"nhl-research-{date}.json"
    if not path.exists():
        raise SystemExit(
            f"No slate for {date}. Run: python fetch-nhl-research-slate.py --date {date}")
    slate = json.loads(path.read_text(encoding="utf-8"))

    rows = rate(collect(slate), slate.get("scales") or {})

    # With a play list the sheet is exactly those plays. Scoring happens first,
    # against league-wide scales, so narrowing the board does not move a score.
    plays = load_plays(date)
    unmatched: list[dict] = []
    if plays is not None:
        index = {(norm_name(r["name"]), r["team"]): r for r in rows}
        listed = []
        for play in plays:
            row = index.get((norm_name(play["name"]), play["team"]))
            if row is None:
                unmatched.append(play)
                continue
            row["market"] = f'{play["side"]} {play["line"]:g} {play["market"]}'
            row["listed_role"] = play["role"]
            # what settles it on the page: a 0.5 line needs one goal, 1.5 needs two
            row["line"] = play["line"]
            row["side"] = play["side"]
            listed.append(row)
        rows = listed
    by_id = {r["id"]: r for r in rows}

    games_out = []
    for game in slate.get("games") or []:
        key = f"{game['away']}@{game['home']}"
        sides = {}
        for team in (game["away"], game["home"]):
            plays = [r for r in rows if r["game"] == key and r["team"] == team]
            plays.sort(key=lambda r: r["score"], reverse=True)
            sides[team] = plays
        games_out.append({
            "away": game["away"], "home": game["home"],
            "away_name": game.get("away_name", ""), "home_name": game.get("home_name", ""),
            "kick": game.get("kickoff", ""), "venue": game.get("venue", ""),
            "away_record": game.get("away_record", ""),
            "home_record": game.get("home_record", ""),
            "sides": sides,
        })

    rated = sorted((r for r in rows if not r["small"]), key=lambda r: r["score"], reverse=True)
    top = [r["id"] for r in rated[:5]]

    # Plus-money value: the best scores that still pay better than even. Without
    # a price feed there is nothing to sort on, so the section stays empty
    # rather than inventing odds.
    value = [r["id"] for r in rated
             if str(r["lines"].get("atgs", "")).startswith("+")][:5]

    # Profile warnings: names the model likes less than their reputation would.
    warned = sorted((r for r in rated if r["warning"]), key=lambda r: r["score"])
    warnings = [r["id"] for r in warned[:5]]

    kicks = sorted(g["kick"] for g in games_out if g["kick"])
    return {
        "date": date,
        "season": slate.get("season"),
        "stats_season": slate.get("stats_season"),
        "root": "",
        "built": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "first_kick": kicks[0] if kicks else "",
        "last_kick": kicks[-1] if kicks else "",
        "games": games_out,
        "top5": top,
        "value": value,
        "warnings": warnings,
        "has_props": slate.get("has_props", False),
        "weights": WEIGHTS,
        "by_id": by_id,
        "listed": plays is not None,
        "unmatched": unmatched,
    }


def render(sheet: dict, root: str) -> str:
    html = TEMPLATE.read_text(encoding="utf-8")
    data = dict(sheet, root=root)
    html = html.replace("/*__SHEET__*/null",
                        json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    return html.replace("__ROOT__", root).replace("__DATE__", sheet["date"])


_BUILT_STAMP = re.compile(r'"built":"[^"]*"')


def _write_if_changed(path: Path, text: str) -> bool:
    """Write `text` unless the file already says the same thing bar the build time.

    The scheduled build re-renders the sheet several times a day. Without this
    every run would differ by its timestamp alone and commit the page again.
    """
    if path.exists():
        old = path.read_text(encoding="utf-8")
        if _BUILT_STAMP.sub('"built":""', old) == _BUILT_STAMP.sub('"built":""', text):
            return False
    path.write_text(text, encoding="utf-8")
    return True


def publish(sheet: dict) -> Path:
    """Current slate at nhl-research/atgs.html, every slate in archive/, and
    atgs-manifest.json feeding the date dropdown. Only the newest date takes
    over atgs.html, so rebuilding an old slate never replaces today's."""
    date = sheet["date"]
    archive = NHL_DIR / "archive" / f"{date}.html"
    archive.parent.mkdir(parents=True, exist_ok=True)
    changed = _write_if_changed(archive, render(sheet, "../"))

    manifest = {"version": 1, "sheets": []}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = {e["key"]: e for e in manifest.get("sheets", [])}
    entries[date] = {"key": date, "date": date}
    ordered = sorted(entries.values(), key=lambda e: e["date"], reverse=True)
    # "Current" is the newest slate that has actually arrived. Taking the newest
    # date outright let a slate built ahead of time sit on atgs.html and hide
    # tonight's board behind the dropdown.
    # The scheduled build runs on a UTC clock, where it is already tomorrow by
    # 8 pm Eastern -- it passes the Eastern date in NHL_TODAY so an evening run
    # does not promote the next day's sheet early.
    today = os.environ.get("NHL_TODAY") or datetime.now().date().isoformat()
    latest = next((e for e in ordered if e["date"] <= today), ordered[0])
    for e in ordered:
        # "%-d" strips the leading zero on Unix but raises on Windows, so the
        # zero comes off the formatted string instead.
        try:
            pretty = datetime.strptime(e["date"], "%Y-%m-%d").strftime("%b %d").replace(" 0", " ")
        except ValueError:
            pretty = e["date"]
        if e is latest:
            e["label"], e["href"] = f"{pretty} — current slate", "atgs.html"
        else:
            e["label"], e["href"] = pretty, f"archive/{e['date']}.html"
    body = json.dumps({"version": 1, "sheets": ordered}, indent=2, ensure_ascii=False) + "\n"
    if not MANIFEST.exists() or MANIFEST.read_text(encoding="utf-8") != body:
        MANIFEST.write_text(body, encoding="utf-8")

    if latest["key"] == date:
        changed = _write_if_changed(NHL_DIR / "atgs.html", render(sheet, "")) or changed
        print(f"[atgs] {date} is the current slate: nhl-research/atgs.html")
    print(f"[atgs] {'archived as' if changed else 'unchanged:'} {archive.relative_to(ROOT)}; "
          f"the list has {len(ordered)} slates")
    return archive


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the NHL Anytime Goal Scorer sheet")
    parser.add_argument("--date", required=True, help='Slate date, "2026-09-29"')
    args = parser.parse_args()

    sheet = build_sheet(args.date)
    rows = list(sheet["by_id"].values())
    bands: dict = {}
    for r in rows:
        bands[r["band_label"]] = bands.get(r["band_label"], 0) + 1
    if sheet["unmatched"]:
        print(f"[atgs] WARN {len(sheet['unmatched'])} listed play(s) not on the slate:")
        for play in sheet["unmatched"]:
            print(f"[atgs]   {play['name']} ({play['team']} {play['role']}) -- not in the club's lineup")
    moved = [r for r in rows if r.get("listed_role") and r["listed_role"] != r["role"]]
    for r in moved:
        print(f"[atgs] note {r['name']}: listed as {r['listed_role']}, slate has him at {r['role']}")
    print(f"[atgs] {len(sheet['games'])} games, {len(rows)} plays, bands {bands}, "
          f"{sum(1 for r in rows if r['small'])} small samples")
    print("[atgs] top 5: " + ", ".join(
        f"{sheet['by_id'][i]['name']} ({sheet['by_id'][i]['score']})" for i in sheet["top5"]))
    if sheet["warnings"]:
        print("[atgs] warnings: " + ", ".join(
            f"{sheet['by_id'][i]['name']} — {sheet['by_id'][i]['warning']}"
            for i in sheet["warnings"]))
    publish(sheet)


if __name__ == "__main__":
    main()
