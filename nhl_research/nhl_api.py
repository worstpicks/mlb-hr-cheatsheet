"""Official NHL API (free, no key) schedule fetch for the NHL Research tab.

The NFL tab reads ESPN's unofficial scoreboard. Hockey has something better:
NHL.com's own public API, which carries the schedule, rosters, per-game player
lines and team logos without a key or a scrape.

A hockey slate is a DATE, not a week. The NFL page asks for season + week; this
one asks for a day, the way the MLB research tab does.
"""
from __future__ import annotations

import json
import urllib.request

WEB = "https://api-web.nhle.com/v1"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0 Safari/537.36"

# gameType in the NHL feed: 1 preseason, 2 regular season, 3 playoffs
GAME_TYPE_LABEL = {1: "PRE", 2: "REG", 3: "POST"}


def get_json(url: str, timeout: int = 60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _team(side: dict) -> dict:
    """Flatten one side of a game into the shape the page renders."""
    place = (side.get("placeName") or {}).get("default", "")
    common = (side.get("commonName") or {}).get("default", "")
    return {
        "abbr": side.get("abbrev", ""),
        "name": f"{place} {common}".strip(),
        "short": common or place,
        "logo": side.get("logo", ""),
        "dark_logo": side.get("darkLogo", ""),
        "team_id": side.get("id"),
        "score": side.get("score"),
    }


def fetch_day_games(date: str) -> list[dict]:
    """Return one day's games: [{id, away, home, away_name, home_name, kickoff, ...}].

    `date` is ISO, "2026-09-29". The feed answers with a whole week starting at
    that date, so the day itself is picked back out of `gameWeek`.
    """
    payload = get_json(f"{WEB}/schedule/{date}")
    day = next((d for d in payload.get("gameWeek", []) if d.get("date") == date), None)
    games = []
    for game in (day or {}).get("games", []):
        away, home = _team(game.get("awayTeam") or {}), _team(game.get("homeTeam") or {})
        if not away["abbr"] or not home["abbr"]:
            continue
        games.append(
            {
                "id": str(game.get("id", "")),
                "season": game.get("season"),
                "game_type": game.get("gameType"),
                "game_type_label": GAME_TYPE_LABEL.get(game.get("gameType"), ""),
                "kickoff": game.get("startTimeUTC", ""),
                "status": game.get("gameState", ""),
                "venue": (game.get("venue") or {}).get("default", ""),
                "away": away["abbr"],
                "home": home["abbr"],
                "away_name": away["name"],
                "home_name": home["name"],
                "away_short": away["short"],
                "home_short": home["short"],
                "away_logo": away["logo"],
                "home_logo": home["logo"],
                "away_dark_logo": away["dark_logo"],
                "home_dark_logo": home["dark_logo"],
                "away_id": away["team_id"],
                "home_id": home["team_id"],
                "away_score": away["score"],
                "home_score": home["score"],
                "broadcasts": [b.get("network", "") for b in (game.get("tvBroadcasts") or [])],
            }
        )
    games.sort(key=lambda g: g["kickoff"])
    return games


def season_bounds(date: str) -> dict:
    """The calendar the page needs: which season `date` sits in and its edges."""
    payload = get_json(f"{WEB}/schedule/{date}")
    return {
        "preseason_start": payload.get("preSeasonStartDate"),
        "regular_start": payload.get("regularSeasonStartDate"),
        "regular_end": payload.get("regularSeasonEndDate"),
        "playoff_end": payload.get("playoffEndDate"),
    }


def fetch_records(season_id: int) -> dict:
    """abbr -> "W-L-OTL" from the standings, for the little line under each team."""
    try:
        rows = get_json(f"{WEB}/standings/now").get("standings", [])
    except Exception:
        return {}
    out = {}
    for row in rows:
        abbr = (row.get("teamAbbrev") or {}).get("default", "")
        if abbr:
            out[abbr] = f"{row.get('wins', 0)}-{row.get('losses', 0)}-{row.get('otLosses', 0)}"
    return out
