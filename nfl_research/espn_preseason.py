"""2026-preseason player rows from ESPN, shaped like the nflverse ones.

nflverse publishes nothing for a season until it starts -- play-by-play stops at
2025 and stats_player_week_2026 does not exist -- so the only recent football is
preseason, and the only free source for it is ESPN's own boxscores.

The rows this returns match `nflverse_stats.build_aggregates()`'s input exactly,
so the whole Research tab renders off them with no other change.

A standing caveat, which the UI repeats: preseason volume belongs to roster
hopefuls, not starters. A camp arm throwing 22 passes is not evidence about the
week-one quarterback. This is offered as a recency toggle, never the default.
"""
from __future__ import annotations

import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

SITE = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
CACHE = Path(__file__).resolve().parent.parent / "data" / "espn-preseason-cache"

POSITIONS = ("QB", "RB", "WR", "TE")
STAT_KEYS = (
    "pass_att", "pass_cmp", "pass_yds", "pass_td", "pass_int",
    "rush_att", "rush_yds", "rush_td",
    "tgt", "rec", "rec_yds", "rec_td",
)


def _get(url: str, cache_key: str | None = None, timeout: int = 45) -> dict:
    """Fetch JSON, caching completed-game payloads so re-runs cost nothing."""
    path = CACHE / f"{cache_key}.json" if cache_key else None
    if path and path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
    req = urllib.request.Request(url, headers={"User-Agent": "worstpickz-nfl-research"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
    return data


def _num(v) -> float:
    if v in (None, "", "-", "--"):
        return 0.0
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return 0.0


def roster_positions(teams: list[str]) -> dict[str, str]:
    """ESPN athlete id -> position. Boxscores omit position entirely."""
    out: dict[str, str] = {}
    for team in teams:
        try:
            data = _get(f"{SITE}/teams/{team}/roster", cache_key=f"roster-{team}")
        except Exception:
            continue
        for group in data.get("athletes", []):
            for a in group.get("items", []):
                pos = ((a.get("position") or {}).get("abbreviation") or "").upper()
                if pos and a.get("id"):
                    out[str(a["id"])] = pos
    return out


def completed_games(season: int, max_week: int = 4) -> list[dict]:
    games = []
    for week in range(1, max_week + 1):
        try:
            data = _get(f"{SITE}/scoreboard?seasontype=1&week={week}&dates={season}")
        except Exception:
            continue
        for ev in data.get("events", []):
            status = ((ev.get("status") or {}).get("type") or {})
            if not status.get("completed"):
                continue
            games.append({"id": ev.get("id"), "week": week})
    return games


def _cat_rows(cat: dict) -> list[tuple[str, str, list]]:
    labels = [str(x).upper() for x in (cat.get("labels") or [])]
    out = []
    for entry in cat.get("athletes", []):
        athlete = entry.get("athlete") or {}
        aid = str(athlete.get("id") or "")
        name = athlete.get("displayName") or ""
        stats = entry.get("stats") or []
        if aid and name:
            out.append((aid, name, list(zip(labels, stats))))
    return out


def fetch_rows(season: int, teams: list[str]) -> list[dict]:
    """Normalised per-player, per-game preseason rows."""
    positions = roster_positions(teams)
    rows_by_key: dict[tuple, dict] = {}

    for game in completed_games(season):
        try:
            summary = _get(f"{SITE}/summary?event={game['id']}", cache_key=f"game-{game['id']}")
        except Exception:
            continue

        comp = ((summary.get("header") or {}).get("competitions") or [{}])[0]
        sides, scores = {}, {}
        for c in comp.get("competitors", []):
            abbr = (c.get("team") or {}).get("abbreviation")
            if abbr:
                sides[abbr] = c.get("homeAway")
                scores[abbr] = _num(c.get("score"))
        if len(sides) != 2:
            continue
        abbrs = list(sides)
        opp_of = {abbrs[0]: abbrs[1], abbrs[1]: abbrs[0]}

        def outcome(team):
            other = opp_of[team]
            if scores.get(team, 0) > scores.get(other, 0):
                return "W"
            if scores.get(team, 0) < scores.get(other, 0):
                return "L"
            return "T"

        for team_block in (summary.get("boxscore") or {}).get("players", []):
            team = ((team_block.get("team") or {}).get("abbreviation") or "")
            if team not in sides:
                continue
            for cat in team_block.get("statistics", []):
                kind = (cat.get("name") or "").lower()
                if kind not in ("passing", "rushing", "receiving"):
                    continue
                for aid, name, pairs in _cat_rows(cat):
                    key = (aid, game["id"])
                    row = rows_by_key.setdefault(
                        key,
                        {
                            "player_id": aid,
                            "name": name,
                            "pos": positions.get(aid, ""),
                            "team": team,
                            "headshot": f"https://a.espncdn.com/i/headshots/nfl/players/full/{aid}.png",
                            "week": game["week"],
                            "opp": opp_of[team],
                            "ha": "vs" if sides[team] == "home" else "@",
                            "wl": outcome(team),
                            # the defence's own view of the same game, which is
                            # what the "allowed" side of the board logs against
                            "def_ha": "@" if sides[team] == "home" else "vs",
                            "def_wl": outcome(opp_of[team]),
                            **{k: 0.0 for k in STAT_KEYS},
                        },
                    )
                    for label, value in pairs:
                        if kind == "passing":
                            if label == "C/ATT":
                                m = re.match(r"(\d+)\s*/\s*(\d+)", str(value) or "")
                                if m:
                                    row["pass_cmp"] += float(m.group(1))
                                    row["pass_att"] += float(m.group(2))
                            elif label == "YDS":
                                row["pass_yds"] += _num(value)
                            elif label == "TD":
                                row["pass_td"] += _num(value)
                            elif label == "INT":
                                row["pass_int"] += _num(value)
                        elif kind == "rushing":
                            if label == "CAR":
                                row["rush_att"] += _num(value)
                            elif label == "YDS":
                                row["rush_yds"] += _num(value)
                            elif label == "TD":
                                row["rush_td"] += _num(value)
                        else:  # receiving
                            if label == "REC":
                                row["rec"] += _num(value)
                            elif label == "YDS":
                                row["rec_yds"] += _num(value)
                            elif label == "TD":
                                row["rec_td"] += _num(value)
                            elif label == "TGTS":
                                row["tgt"] += _num(value)

    # Keep only the four skill positions the tab renders.
    return [r for r in rows_by_key.values() if r["pos"] in POSITIONS]


def build_preseason(season: int, teams: list[str]):
    """(players_by_team, defense_by_team, n_rows) using the nflverse aggregator."""
    from nfl_research.nflverse_stats import build_aggregates

    rows = fetch_rows(season, teams)
    if not rows:
        return {}, {}, 0
    players, defense = build_aggregates(rows)
    return players, defense, len(rows)
