"""Per-team game logs split by period, for the Puck Line & Moneyline board.

The football tab's team板 breaks a game into quarters and halves. Hockey's
equivalents are the three periods, plus "first two periods" — the split the
books actually post a line on, and the hockey analogue of a first-half bet.

For each team this produces one row per game:

    date · opponent · home/away · final score · result (W / L / OTL)
    goals for and against in each period, and the margin in each
    the margin over the first two periods
    total goals in the game

Colouring on the page is the same idea as the football board: green when the
team won that slice, red when it lost it, neutral on a tie.

Source is the same play-by-play crawl the shot-quality module uses — goals
carry a period and a team, so the period splits come out of the feed rather
than out of a second scoreboard endpoint.

What is NOT here: the closing puck line, moneyline and total for each past
game. The NHL publishes no historical odds and the free feeds do not carry
them, so those columns stay empty until a price feed is connected rather than
being filled with a guess.
"""
from __future__ import annotations

import gzip
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from nhl_research.nhl_stats import CACHE, _get

WEB = "https://api-web.nhle.com/v1"
# How many games of history each panel keeps. The page filters to L10/L20 on
# top of this; 30 is enough to answer "this season so far" without doubling the
# slate's size.
TREND_WINDOW = 30


def _cache_path(season_id: int, game_type: int) -> Path:
    return CACHE / f"team-periods-{season_id}-{game_type}.json.gz"


def _game_periods(game_id: int) -> dict | None:
    """One game's per-period goals for both clubs, from its play-by-play."""
    try:
        payload = _get(f"{WEB}/gamecenter/{game_id}/play-by-play")
    except Exception:
        return None
    away, home = payload.get("awayTeam") or {}, payload.get("homeTeam") or {}
    a_abbr, h_abbr = away.get("abbrev"), home.get("abbrev")
    if not a_abbr or not h_abbr:
        return None
    by_team = {away.get("id"): "a", home.get("id"): "h"}

    # periods 1-3 plus anything past them (OT, and a shootout the feed numbers 5)
    goals = {"a": defaultdict(int), "h": defaultdict(int)}
    for play in payload.get("plays") or []:
        if play.get("typeDescKey") != "goal":
            continue
        d = play.get("details") or {}
        side = by_team.get(d.get("eventOwnerTeamId"))
        if not side:
            continue
        num = (play.get("periodDescriptor") or {}).get("number") or 0
        goals[side][min(int(num), 4)] += 1     # OT and SO both fold into 4

    return {
        "game_id": game_id,
        "date": (payload.get("gameDate") or "")[:10],
        "away": a_abbr,
        "home": h_abbr,
        "away_score": away.get("score"),
        "home_score": home.get("score"),
        "periods": {
            "a": {str(p): goals["a"].get(p, 0) for p in (1, 2, 3, 4)},
            "h": {str(p): goals["h"].get(p, 0) for p in (1, 2, 3, 4)},
        },
        # a game that reached period 4 was not settled in regulation
        "extra": bool(goals["a"].get(4) or goals["h"].get(4)),
    }


def load_periods(season_id: int, game_ids: list[int], game_type: int = 2,
                 refresh: bool = False) -> list[dict]:
    """Every game's period splits for a season, cached on disk."""
    path = _cache_path(season_id, game_type)
    if path.exists() and not refresh:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return json.load(fh)

    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for row in pool.map(_game_periods, game_ids):
            if row:
                rows.append(row)
    rows.sort(key=lambda r: (r["date"], r["game_id"]))
    CACHE.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        json.dump(rows, fh, separators=(",", ":"))
    print(f"[nhl-research] period splits for {len(rows)} of {len(game_ids)} games")
    return rows


def _result(gf: int, ga: int, extra: bool) -> str:
    """W, L, or OTL — hockey's third outcome, which a spread board has to show."""
    if gf > ga:
        return "W"
    return "OTL" if extra else "L"


def build_team_logs(period_rows: list[dict], window: int = TREND_WINDOW) -> dict:
    """{ "EDM": [ {date, opp, ha, gf, ga, margin, result, p1..p3, f2p, total} ] }."""
    logs: dict = defaultdict(list)
    for g in period_rows:
        a_total = g.get("away_score")
        h_total = g.get("home_score")
        if a_total is None or h_total is None:
            continue
        for side, team, opp, gf, ga in (
            ("a", g["away"], g["home"], a_total, h_total),
            ("h", g["home"], g["away"], h_total, a_total),
        ):
            other = "h" if side == "a" else "a"
            mine = g["periods"][side]
            theirs = g["periods"][other]
            per = {}
            for p in ("1", "2", "3"):
                f, a = int(mine.get(p, 0)), int(theirs.get(p, 0))
                per[f"p{p}"] = {"gf": f, "ga": a, "margin": f - a}
            f2_f = sum(int(mine.get(p, 0)) for p in ("1", "2"))
            f2_a = sum(int(theirs.get(p, 0)) for p in ("1", "2"))
            logs[team].append({
                "date": g["date"],
                "game_id": g["game_id"],
                "opp": opp,
                "ha": "vs" if side == "h" else "@",
                "gf": gf,
                "ga": ga,
                "margin": gf - ga,
                "total": gf + ga,
                "result": _result(gf, ga, g.get("extra", False)),
                "extra": bool(g.get("extra")),
                **per,
                "f2p": {"gf": f2_f, "ga": f2_a, "margin": f2_f - f2_a},
            })
    # newest last, then trimmed to the window the page needs
    return {team: sorted(rows, key=lambda r: r["date"])[-window:]
            for team, rows in logs.items()}
