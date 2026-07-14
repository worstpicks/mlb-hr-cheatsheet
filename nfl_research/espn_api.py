"""ESPN unofficial (free, no key) NFL schedule fetch for the Research tab."""
from __future__ import annotations

import json
import urllib.request

SCOREBOARD_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    "?seasontype=2&week={week}&dates={season}"
)


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "worstpickz-nfl-research"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_week_games(season: int, week: int) -> list[dict]:
    """Return the week's games: [{id, away, home, away_name, home_name, kickoff, ...}]."""
    payload = _get_json(SCOREBOARD_URL.format(season=season, week=week))
    games = []
    for event in payload.get("events", []):
        competitions = event.get("competitions") or []
        if not competitions:
            continue
        comp = competitions[0]
        away = home = None
        for side in comp.get("competitors", []):
            team = side.get("team") or {}
            info = {
                "abbr": team.get("abbreviation", ""),
                "name": team.get("displayName", ""),
                "short": team.get("shortDisplayName", ""),
                "logo": team.get("logo", ""),
                "record": next(
                    (r.get("summary", "") for r in side.get("records", []) if r.get("type") == "total"),
                    "",
                ),
            }
            if side.get("homeAway") == "home":
                home = info
            else:
                away = info
        if not away or not home:
            continue
        status = (event.get("status") or {}).get("type") or {}
        games.append(
            {
                "odds": _extract_odds(comp),
                "id": event.get("id", ""),
                "kickoff": event.get("date", ""),
                "status": status.get("shortDetail", ""),
                "away": away["abbr"],
                "home": home["abbr"],
                "away_name": away["name"],
                "home_name": home["name"],
                "away_short": away["short"],
                "home_short": home["short"],
                "away_logo": away["logo"],
                "home_logo": home["logo"],
                "away_record": away["record"],
                "home_record": home["record"],
            }
        )
    games.sort(key=lambda g: g["kickoff"])
    return games


def _extract_odds(comp: dict) -> dict | None:
    """Pull the primary sportsbook game line (spread / total / ML) if present."""
    odds_list = comp.get("odds") or []
    if not odds_list:
        return None
    odds = odds_list[0]
    provider = (odds.get("provider") or {}).get("displayName", "")

    def _ml(side: str) -> str:
        ml = odds.get("moneyline") or {}
        close = (ml.get(side) or {}).get("close") or {}
        return close.get("odds", "") or ""

    return {
        "book": provider,
        "details": odds.get("details", ""),  # e.g. "SEA -3.5"
        "over_under": odds.get("overUnder"),
        "ml_home": _ml("home"),
        "ml_away": _ml("away"),
    }
