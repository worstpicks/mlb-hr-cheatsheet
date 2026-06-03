#!/usr/bin/env python3
"""First-pitch times from MLB Stats API for ordering slate games."""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request

SHEET_ABBR_FROM_API = {"AZ": "ARI", "WAS": "WSH", "WSN": "WSH", "OAK": "ATH"}


def normalize_sheet_abbr(abbr: str) -> str:
    return SHEET_ABBR_FROM_API.get((abbr or "").upper(), (abbr or "").upper())


def game_key(away: str, home: str) -> str:
    return f"{normalize_sheet_abbr(away)} @ {normalize_sheet_abbr(home)}"


def parse_key_from_title(title: str) -> str | None:
    head = (title.split(" - ")[0] or "").strip()
    m = re.match(r"^([A-Za-z]+)\s*@\s*([A-Za-z]+)$", head)
    if not m:
        return None
    return game_key(m.group(1), m.group(2))


def fetch_start_times(sheet_date: str) -> dict[str, str]:
    """Return matchup key -> ISO gameDate (UTC) from MLB schedule."""
    query = urllib.parse.urlencode({"sportId": 1, "date": sheet_date, "hydrate": "team"})
    url = f"https://statsapi.mlb.com/api/v1/schedule?{query}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read())
    out: dict[str, str] = {}
    for day in data.get("dates") or []:
        for g in day.get("games") or []:
            away = (g.get("teams") or {}).get("away", {}).get("team", {}).get("abbreviation") or ""
            home = (g.get("teams") or {}).get("home", {}).get("team", {}).get("abbreviation") or ""
            if not away or not home:
                continue
            key = game_key(away, home)
            out[key] = g.get("gameDate") or ""
    return out


def annotate_and_sort_games(games: list[dict], sheet_date: str) -> list[dict]:
    """Sort games by first pitch; attach startTime when schedule match exists."""
    times = fetch_start_times(sheet_date)

    def sort_key(game: dict) -> str:
        key = parse_key_from_title(game.get("title", ""))
        return times.get(key or "", "9999-12-31T99:99:99Z")

    ordered = sorted(games, key=sort_key)
    for game in ordered:
        key = parse_key_from_title(game.get("title", ""))
        if key and key in times:
            game["startTime"] = times[key]
    return ordered
