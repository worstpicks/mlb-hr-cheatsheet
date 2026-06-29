#!/usr/bin/env python3
"""RotoWire daily lineups — fallback for TBD probables and projected batting orders."""
from __future__ import annotations

import re
import urllib.parse
import urllib.request
from datetime import date
from typing import Any

MLB_API = "https://statsapi.mlb.com/api/v1"

# Keep in sync with research.mlb_api.SHEET_ABBR_FROM_API
_SHEET_ABBR_FROM_API = {"AZ": "ARI", "WAS": "WSH", "WSN": "WSH", "OAK": "ATH", "TB": "TB", "SF": "SF"}


def _normalize_abbr(abbr: str) -> str:
    raw = (abbr or "").upper()
    return _SHEET_ABBR_FROM_API.get(raw, raw)


ROTOWIRE_LINEUPS_URL = "https://www.rotowire.com/baseball/daily-lineups.php"

# RotoWire team codes that differ from our MLB schedule abbreviations.
ROTOWIRE_ABBR_TO_SHEET: dict[str, str] = {
    "AZ": "ARI",
    "CHW": "CWS",
    "WAS": "WSH",
    "OAK": "ATH",
}


def _sheet_abbr(raw: str) -> str:
    abbr = (raw or "").strip().upper()
    abbr = ROTOWIRE_ABBR_TO_SHEET.get(abbr, abbr)
    return _normalize_abbr(abbr)


def _fetch_html(sheet_date: str) -> str:
    query = urllib.parse.urlencode({"date": sheet_date})
    url = f"{ROTOWIRE_LINEUPS_URL}?{query}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", "replace")


def _mlb_get(path_query: str, timeout: int = 20) -> dict:
    url = f"{MLB_API}{path_query}"
    req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz-Research/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return __import__("json").loads(resp.read())


def _search_mlb_person(name: str) -> dict | None:
    name = (name or "").strip()
    if not name or name.upper() == "TBD":
        return None
    query = urllib.parse.urlencode({"names": name, "sportId": 1})
    try:
        data = _mlb_get(f"/people/search?{query}", timeout=15)
    except Exception:
        return None
    people = data.get("people") or []
    if not people:
        return None
    target = name.lower()
    for person in people:
        if (person.get("fullName") or "").lower() == target:
            return person
    return people[0]


def _parse_side(side_html: str) -> dict[str, Any]:
    pitcher = None
    pm = re.search(
        r'lineup__player-highlight-name">\s*<a[^>]*>([^<]+)</a>\s*'
        r'<span class="lineup__throws">([LRS])</span>',
        side_html,
        re.I | re.S,
    )
    if pm:
        pitcher = {
            "name": pm.group(1).strip(),
            "throws": pm.group(2).strip().upper(),
        }

    status_m = re.search(r'class="lineup__status([^"]*)"[^>]*>([\s\S]*?)</li>', side_html, re.I)
    status_class = status_m.group(1) if status_m else ""
    status_text = re.sub(r"<[^>]+>", " ", status_m.group(2) if status_m else "").strip().lower()
    confirmed = "is-confirmed" in status_class or "confirmed lineup" in status_text
    projected = not confirmed

    lineup: list[dict[str, Any]] = []
    for order, m in enumerate(
        re.finditer(
            r'class="lineup__player">\s*<div class="lineup__pos">([^<]+)</div>\s*'
            r'<a title="([^"]*)"[^>]*>([^<]*)</a>\s*'
            r'<span class="lineup__bats">([LRS])</span>',
            side_html,
            re.I | re.S,
        ),
        start=1,
    ):
        pos = m.group(1).strip().upper()
        full_name = (m.group(2) or m.group(3) or "").strip()
        hand = m.group(4).strip().upper()
        if not full_name:
            continue
        lineup.append(
            {
                "name": full_name,
                "order": order,
                "position": pos,
                "hand": hand,
                "projected": projected,
            }
        )

    return {"pitcher": pitcher, "lineup": lineup, "confirmed": confirmed}


def _parse_game_box(box_html: str) -> dict[str, Any] | None:
    away_m = re.search(
        r'lineup__team is-visit[\s\S]*?<div class="lineup__abbr">([A-Z]+)</div>',
        box_html,
        re.I,
    )
    home_m = re.search(
        r'lineup__team is-home[\s\S]*?<div class="lineup__abbr">([A-Z]+)</div>',
        box_html,
        re.I,
    )
    if not away_m or not home_m:
        return None
    away = _sheet_abbr(away_m.group(1))
    home = _sheet_abbr(home_m.group(1))
    if not away or not home:
        return None

    visit_m = re.search(
        r'<ul class="lineup__list is-visit">([\s\S]*?)</ul>',
        box_html,
        re.I,
    )
    home_list_m = re.search(
        r'<ul class="lineup__list is-home">([\s\S]*?)</ul>',
        box_html,
        re.I,
    )
    if not visit_m or not home_list_m:
        return None

    away_side = _parse_side(visit_m.group(1))
    home_side = _parse_side(home_list_m.group(1))
    return {
        "matchup": f"{away} @ {home}",
        "away": away,
        "home": home,
        "awayPitcher": away_side.get("pitcher"),
        "homePitcher": home_side.get("pitcher"),
        "awayLineup": away_side.get("lineup") or [],
        "homeLineup": home_side.get("lineup") or [],
        "awayLineupConfirmed": away_side.get("confirmed"),
        "homeLineupConfirmed": home_side.get("confirmed"),
    }


def fetch_rotowire_games(sheet_date: str) -> list[dict[str, Any]]:
    """Parse RotoWire daily lineups for a calendar date (best-effort; page defaults to today)."""
    html = _fetch_html(sheet_date)
    page_date_m = re.search(r"Starting MLB lineups for\s+([^<]+)", html, re.I)
    page_date_text = (page_date_m.group(1) or "").strip() if page_date_m else ""
    boxes = re.split(r'<div class="lineup__box">', html)[1:]
    games: list[dict[str, Any]] = []
    for box in boxes:
        parsed = _parse_game_box(box)
        if parsed:
            parsed["source"] = "rotowire"
            parsed["pageDate"] = page_date_text
            games.append(parsed)
    return games


def _name_key(name: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", (name or "").lower()).strip()


def _build_roster_lookup(team_id: int, roster_season: int) -> dict[str, dict]:
    from research.mlb_api import fetch_team_hitters

    lookup: dict[str, dict] = {}
    for row in fetch_team_hitters(team_id, roster_season):
        name = row.get("name") or ""
        if not name:
            continue
        lookup[_name_key(name)] = row
        parts = name.split()
        if parts:
            lookup[_name_key(parts[-1])] = row
    return lookup


def _resolve_from_rosters(name: str, rosters: list[dict[str, dict]]) -> dict | None:
    key = _name_key(name)
    if not key:
        return None
    for roster in rosters:
        if key in roster:
            return roster[key]
    parts = (name or "").split()
    if parts:
        last = _name_key(parts[-1])
        matches = []
        for roster in rosters:
            hit = roster.get(last)
            if hit:
                matches.append(hit)
        if len(matches) == 1:
            return matches[0]
    return _search_mlb_person(name)


def _attach_mlb_ids(game: dict[str, Any], *, roster_season: int) -> None:
    away_roster = (
        _build_roster_lookup(int(game["awayTeamId"]), roster_season)
        if game.get("awayTeamId")
        else {}
    )
    home_roster = (
        _build_roster_lookup(int(game["homeTeamId"]), roster_season)
        if game.get("homeTeamId")
        else {}
    )
    rosters = [r for r in (away_roster, home_roster) if r]

    def person(name: str, side_roster: dict[str, dict] | None = None) -> dict | None:
        if side_roster:
            hit = _resolve_from_rosters(name, [side_roster])
            if hit:
                return hit
        return _resolve_from_rosters(name, rosters)

    for side_key, roster in (("awayPitcher", away_roster), ("homePitcher", home_roster)):
        raw = game.get(side_key)
        if not raw or not raw.get("name"):
            continue
        hit = _search_mlb_person(raw["name"])
        if not hit:
            continue
        game[side_key] = {
            "id": hit.get("id"),
            "name": hit.get("fullName") or raw["name"],
            "throws": raw.get("throws") or (hit.get("pitchHand") or {}).get("code") or "",
            "source": "rotowire",
            "projected": True,
        }

    for side_key, roster in (("awayLineup", away_roster), ("homeLineup", home_roster)):
        rows: list[dict[str, Any]] = []
        for row in game.get(side_key) or []:
            hit = person(row.get("name") or "", roster)
            rows.append(
                {
                    "id": hit.get("id") if hit else None,
                    "name": (hit.get("name") if hit else None) or row.get("name"),
                    "order": row.get("order"),
                    "position": row.get("position") or (hit.get("position") if hit else "") or "",
                    "hand": row.get("hand") or (hit.get("hand") if hit else "") or "",
                    "projected": bool(row.get("projected", True)),
                    "source": "rotowire",
                }
            )
        game[side_key] = rows


def _pitcher_missing(pitcher: dict | None) -> bool:
    if not pitcher:
        return True
    name = (pitcher.get("name") or "").strip()
    if not name or name.upper() == "TBD":
        return True
    return not pitcher.get("id")


def _lineup_is_roster_projection(lineup: list[dict] | None) -> bool:
    if not lineup:
        return True
    return all(bool(row.get("projected")) for row in lineup)


def _rotowire_lineup_better(existing: list[dict] | None, incoming: list[dict] | None) -> bool:
    if not incoming or len(incoming) < 7:
        return False
    if not existing:
        return True
    if _lineup_is_roster_projection(existing):
        return True
    return False


def apply_rotowire_fallback_to_games(
    games: list[dict], sheet_date: str, *, roster_season: int | None = None
) -> dict[str, Any]:
    """Fill TBD probables and roster-only lineups from RotoWire when available."""
    if roster_season is None:
        roster_season = int(sheet_date[:4]) if sheet_date[:4].isdigit() else date.today().year
    try:
        rotowire_games = fetch_rotowire_games(sheet_date)
    except Exception as exc:
        return {"source": "rotowire", "error": str(exc), "games": 0}

    rw_by_matchup = {g["matchup"]: g for g in rotowire_games}
    api_by_matchup = {g.get("matchup"): g for g in games if g.get("matchup")}

    for rw in rotowire_games:
        api_game = api_by_matchup.get(rw.get("matchup"))
        if api_game:
            rw["awayTeamId"] = api_game.get("awayTeamId")
            rw["homeTeamId"] = api_game.get("homeTeamId")
        _attach_mlb_ids(rw, roster_season=roster_season)

    by_matchup = rw_by_matchup
    stats = {
        "source": "rotowire",
        "games": len(rotowire_games),
        "pitchersFilled": 0,
        "lineupsFilled": 0,
        "pageDate": rotowire_games[0].get("pageDate") if rotowire_games else None,
        "sheetDate": sheet_date,
    }

    for game in games:
        rw = by_matchup.get(game.get("matchup") or "")
        if not rw:
            continue

        if _pitcher_missing(game.get("awayPitcher")) and rw.get("awayPitcher"):
            game["awayPitcher"] = dict(rw["awayPitcher"])
            stats["pitchersFilled"] += 1
        if _pitcher_missing(game.get("homePitcher")) and rw.get("homePitcher"):
            game["homePitcher"] = dict(rw["homePitcher"])
            stats["pitchersFilled"] += 1

        if _rotowire_lineup_better(game.get("awayLineup"), rw.get("awayLineup")):
            game["awayLineup"] = [dict(row) for row in rw.get("awayLineup") or []]
            stats["lineupsFilled"] += 1
        if _rotowire_lineup_better(game.get("homeLineup"), rw.get("homeLineup")):
            game["homeLineup"] = [dict(row) for row in rw.get("homeLineup") or []]
            stats["lineupsFilled"] += 1

        if rw.get("awayLineupConfirmed") or rw.get("homeLineupConfirmed"):
            away_conf = any(not row.get("projected") for row in game.get("awayLineup") or [])
            home_conf = any(not row.get("projected") for row in game.get("homeLineup") or [])
            if away_conf and home_conf:
                game["lineupStatus"] = "confirmed"
            elif away_conf or home_conf:
                game["lineupStatus"] = "partial"
            elif game.get("awayLineup") or game.get("homeLineup"):
                game["lineupStatus"] = "projected"

    return stats


def build_rotowire_payload(sheet_date: str, *, roster_season: int | None = None) -> dict[str, Any]:
    if roster_season is None:
        roster_season = int(sheet_date[:4]) if sheet_date[:4].isdigit() else date.today().year
    games = fetch_rotowire_games(sheet_date)
    try:
        from research.mlb_api import fetch_schedule

        schedule_by_matchup = {g["matchup"]: g for g in fetch_schedule(sheet_date)}
    except Exception:
        schedule_by_matchup = {}
    for game in games:
        api_game = schedule_by_matchup.get(game.get("matchup") or "")
        if api_game:
            game["awayTeamId"] = api_game.get("awayTeamId")
            game["homeTeamId"] = api_game.get("homeTeamId")
        _attach_mlb_ids(game, roster_season=roster_season)
    return {
        "date": sheet_date,
        "source": "rotowire-daily-lineups",
        "pageDate": games[0].get("pageDate") if games else None,
        "games": games,
    }
