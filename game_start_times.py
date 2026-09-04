#!/usr/bin/env python3
"""First-pitch times from MLB Stats API for ordering slate games."""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request

SHEET_ABBR_FROM_API = {"AZ": "ARI", "WAS": "WSH", "WSN": "WSH", "OAK": "ATH"}


_DH_PROBABLES: dict[tuple[str, int], set] = {}


def _fold(name: str) -> str:
    """Accent- and punctuation-insensitive surname key for starter matching."""
    import unicodedata

    b = unicodedata.normalize("NFKD", name or "")
    b = "".join(c for c in b if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", b.lower())


def starters_from_title(title: str) -> set:
    """Both starter names out of a game title, folded for comparison."""
    if " - " not in title or " vs " not in title:
        return set()
    _, matchup = title.split(" - ", 1)
    out = set()
    for seg in matchup.split(" vs "):
        nm = seg.rsplit(" (", 1)[0].replace("\U0001f9e4", "").strip()
        if nm:
            out.add(_fold(nm))
    return out


def resolve_dh_time(key: str, title: str, times: dict) -> str | None:
    """Pick the doubleheader game whose probables match this title's starters.

    The plain "AWY @ HOM" key is filed under game one. When the sheet carries only
    game two -- game one already underway and never exported -- that handed the
    board a first pitch hours earlier than the game it was describing.
    """
    wanted = starters_from_title(title)
    if not wanted:
        return None
    best, best_hits = None, 0
    for (k, gn), names in _DH_PROBABLES.items():
        if k != key or not names:
            continue
        hits = len(wanted & names)
        if hits > best_hits:
            best, best_hits = f"{key} (G{gn})", hits
    if best and best_hits and best in times:
        return times[best]
    return None


def normalize_sheet_abbr(abbr: str) -> str:
    return SHEET_ABBR_FROM_API.get((abbr or "").upper(), (abbr or "").upper())


def game_key(away: str, home: str) -> str:
    return f"{normalize_sheet_abbr(away)} @ {normalize_sheet_abbr(home)}"


def parse_key_from_title(title: str) -> str | None:
    head = (title.split(" - ")[0] or "").strip()
    # Doubleheaders: "LAD @ NYY (G1)" / "LAD @ NYY (Game 2)"
    m = re.match(
        r"^([A-Za-z]+)\s*@\s*([A-Za-z]+)(?:\s*\((?:G|Game\s*)(\d+)\))?$",
        head,
        re.I,
    )
    if not m:
        return None
    base = game_key(m.group(1), m.group(2))
    if m.group(3):
        return f"{base} (G{m.group(3)})"
    return base


def fetch_start_times(sheet_date: str) -> dict[str, str]:
    """Return matchup key -> ISO gameDate (UTC) from MLB schedule.

    Doubleheaders use ``AWAY @ HOME (G1)`` / ``(G2)`` keys (and still set the
    plain ``AWAY @ HOME`` key to game 1 for single-key callers).
    """
    query = urllib.parse.urlencode(
        {"sportId": 1, "date": sheet_date, "hydrate": "team,probablePitcher"}
    )
    url = f"https://statsapi.mlb.com/api/v1/schedule?{query}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read())
    out: dict[str, str] = {}
    # Collect all games per matchup so DH gameNumber is preserved.
    by_matchup: dict[str, list[tuple[int, str]]] = {}
    # Starter names per (key, gameNumber), so a sheet carrying only one game of a
    # doubleheader can be matched to the right one rather than defaulting to G1.
    global _DH_PROBABLES
    _DH_PROBABLES = {}
    for day in data.get("dates") or []:
        for g in day.get("games") or []:
            away = (g.get("teams") or {}).get("away", {}).get("team", {}).get("abbreviation") or ""
            home = (g.get("teams") or {}).get("home", {}).get("team", {}).get("abbreviation") or ""
            if not away or not home:
                continue
            key = game_key(away, home)
            gd = g.get("gameDate") or ""
            try:
                gn = int(g.get("gameNumber") or 1)
            except (TypeError, ValueError):
                gn = 1
            by_matchup.setdefault(key, []).append((gn, gd))
            names = set()
            for side in ("away", "home"):
                nm = (((g.get("teams") or {}).get(side, {}).get("probablePitcher")) or {}).get(
                    "fullName"
                )
                if nm:
                    names.add(_fold(nm))
            _DH_PROBABLES[(key, gn)] = names
    for key, entries in by_matchup.items():
        entries.sort(key=lambda x: (x[0], x[1]))
        if len(entries) == 1:
            out[key] = entries[0][1]
            continue
        for gn, gd in entries:
            out[f"{key} (G{gn})"] = gd
        # Plain key -> earliest first pitch (G1)
        out[key] = entries[0][1]
    return out


def annotate_and_sort_games(games: list[dict], sheet_date: str) -> list[dict]:
    """Sort games by first pitch; attach startTime when schedule match exists."""
    times = fetch_start_times(sheet_date)

    def sort_key(game: dict) -> str:
        title = game.get("title", "")
        key = parse_key_from_title(title)
        if key:
            dh = resolve_dh_time(key, title, times)
            if dh:
                return dh
        if key and key in times:
            return times[key]
        # Fallback: bare matchup if title lacks (Gn)
        if key and " (G" in key:
            bare = key.split(" (G")[0]
            return times.get(bare, "9999-12-31T99:99:99Z")
        return times.get(key or "", "9999-12-31T99:99:99Z")

    ordered = sorted(games, key=sort_key)
    for game in ordered:
        title = game.get("title", "")
        key = parse_key_from_title(title)
        dh = resolve_dh_time(key, title, times) if key else None
        if dh:
            game["startTime"] = dh
            continue
        if key and key in times:
            game["startTime"] = times[key]
        elif key and " (G" in key:
            bare = key.split(" (G")[0]
            if bare in times:
                game["startTime"] = times[bare]
    return ordered
