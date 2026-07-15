#!/usr/bin/env python3
"""Projected starting pitchers when MLB/Savant probable is still TBD.

Primary public source: FantasyPros probable-pitchers grid (next-7-days view).
RotoWire daily lineups remain preferred when scrapeable; call sites try RotoWire
first, then fill remaining TBD slots from this module. Confirmed MLB probables
(with id) are never overwritten.
"""
from __future__ import annotations

import re
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any

from research.mlb_api import game_key, normalize_abbr
from research.rotowire_lineups import _pitcher_missing, _search_mlb_person

FANTASYPROS_URL = "https://www.fantasypros.com/mlb/probable-pitchers.php"

# FantasyPros team cell labels → sheet abbreviations used in research slate.
FP_TEAM_TO_ABBR: dict[str, str] = {
    "athletics": "ATH",
    "arizona diamondbacks": "ARI",
    "atlanta braves": "ATL",
    "baltimore orioles": "BAL",
    "boston red sox": "BOS",
    "chicago cubs": "CHC",
    "chicago white sox": "CWS",
    "cincinnati reds": "CIN",
    "cleveland guardians": "CLE",
    "colorado rockies": "COL",
    "detroit tigers": "DET",
    "houston astros": "HOU",
    "kansas city royals": "KC",
    "los angeles angels": "LAA",
    "los angeles dodgers": "LAD",
    "miami marlins": "MIA",
    "milwaukee brewers": "MIL",
    "minnesota twins": "MIN",
    "new york mets": "NYM",
    "new york yankees": "NYY",
    "philadelphia phillies": "PHI",
    "pittsburgh pirates": "PIT",
    "san diego padres": "SD",
    "san francisco giants": "SF",
    "seattle mariners": "SEA",
    "st. louis cardinals": "STL",
    "st louis cardinals": "STL",
    "tampa bay rays": "TB",
    "texas rangers": "TEX",
    "toronto blue jays": "TOR",
    "washington nationals": "WSH",
}

ESPN_ABBR_TO_SHEET: dict[str, str] = {
    "WSH": "WSH",
    "WAS": "WSH",
    "AZ": "ARI",
    "ARI": "ARI",
    "CHW": "CWS",
    "CWS": "CWS",
    "OAK": "ATH",
    "ATH": "ATH",
    "SF": "SF",
    "TB": "TB",
}


def _fetch_html(url: str, timeout: int = 45) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def _name_from_slug(href: str) -> str:
    slug = (href or "").rstrip("/").split("/")[-1]
    slug = re.sub(r"\.php$", "", slug, flags=re.I)
    slug = slug.replace("-", " ").strip()
    if not slug:
        return ""
    # Title-case; keep short tokens like "jt" as "Jt" — MLB search still resolves.
    return " ".join(part.capitalize() for part in slug.split())


def _team_abbr_from_cell(raw: str) -> str | None:
    text = re.sub(r"<[^>]+>", " ", raw or "")
    text = re.sub(r"\s+", " ", text).strip().lower()
    if not text:
        return None
    if text in FP_TEAM_TO_ABBR:
        return FP_TEAM_TO_ABBR[text]
    # Fall back: last word nickname match (e.g. "diamondbacks")
    for label, abbr in FP_TEAM_TO_ABBR.items():
        if text.endswith(label.split()[-1]) or label in text:
            return abbr
    return None


def _header_matches_date(header: str, sheet_date: str) -> bool:
    """Match FantasyPros headers like 'Fri Jul 17' to YYYY-MM-DD."""
    try:
        target = datetime.strptime(sheet_date, "%Y-%m-%d")
    except ValueError:
        return False
    text = re.sub(r"<[^>]+>", " ", header or "")
    text = re.sub(r"\s+", " ", text).strip()
    # "Fri Jul 17" / "Wed Jul 15"
    m = re.search(r"([A-Za-z]{3})\s+(\d{1,2})\s*$", text)
    if not m:
        return False
    mon_abbr, day = m.group(1), int(m.group(2))
    try:
        parsed = datetime.strptime(f"{mon_abbr} {day} {target.year}", "%b %d %Y")
    except ValueError:
        return False
    return parsed.month == target.month and parsed.day == target.day


def _parse_cell_pitcher(cell_html: str) -> dict[str, Any] | None:
    """Extract first named starter from a FantasyPros day cell (skip TBD)."""
    links = re.findall(
        r'href="(/mlb/players/[^"]+\.php)"[^>]*>([^<]*)',
        cell_html or "",
        re.I,
    )
    for href, short_name in links:
        name = _name_from_slug(href) or (short_name or "").strip()
        if not name or name.upper() == "TBD":
            continue
        return {"name": name, "shortName": (short_name or "").strip(), "slug": href}
    text = re.sub(r"<[^>]+>", " ", cell_html or "")
    if re.search(r"\bTBD\b", text) and not links:
        return None
    return None


def fetch_fantasypros_pitchers_by_team(sheet_date: str) -> dict[str, dict[str, Any]]:
    """Return {team_abbr: {name, ...}} projected starters for sheet_date."""
    # FantasyPros accepts MM-DD-YYYY; also works with ISO in practice.
    try:
        dt = datetime.strptime(sheet_date, "%Y-%m-%d")
        fp_date = dt.strftime("%m-%d-%Y")
    except ValueError:
        fp_date = sheet_date
    query = urllib.parse.urlencode({"date": fp_date})
    html = _fetch_html(f"{FANTASYPROS_URL}?{query}")
    table_m = re.search(
        r'<table class="table table-condensed">([\s\S]*?)</table>',
        html,
        re.I,
    )
    if not table_m:
        return {}

    table = table_m.group(1)
    headers = re.findall(r"<th[^>]*>([\s\S]*?)</th>", table, re.I)
    date_col = None
    for idx, header in enumerate(headers):
        if idx == 0:
            continue
        if _header_matches_date(header, sheet_date):
            date_col = idx
            break
    if date_col is None:
        return {}

    by_team: dict[str, dict[str, Any]] = {}
    for row in re.findall(r"<tr>([\s\S]*?)</tr>", table, re.I):
        cells = re.findall(r"<t[dh][^>]*>([\s\S]*?)</t[dh]>", row, re.I)
        if len(cells) <= date_col:
            continue
        team = _team_abbr_from_cell(cells[0])
        if not team:
            continue
        parsed = _parse_cell_pitcher(cells[date_col])
        if not parsed:
            continue
        by_team[team] = parsed
    return by_team


def fetch_espn_pitchers_by_team(sheet_date: str) -> dict[str, dict[str, Any]]:
    """Supplement from ESPN scoreboard probables (JSON, no login)."""
    compact = sheet_date.replace("-", "")
    url = (
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
        f"?dates={compact}"
    )
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "WorstPickz-Research/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = __import__("json").loads(resp.read().decode("utf-8", "replace"))
    except Exception:
        return {}

    by_team: dict[str, dict[str, Any]] = {}
    for ev in data.get("events") or []:
        comps = (ev.get("competitions") or [{}])[0]
        for t in comps.get("competitors") or []:
            raw_abbr = (t.get("team") or {}).get("abbreviation") or ""
            abbr = normalize_abbr(ESPN_ABBR_TO_SHEET.get(raw_abbr.upper(), raw_abbr))
            if not abbr:
                continue
            probs = t.get("probables") or []
            if not probs:
                continue
            ath = (probs[0] or {}).get("athlete") or {}
            name = (ath.get("fullName") or ath.get("displayName") or "").strip()
            if not name or name.upper() == "TBD":
                continue
            by_team[abbr] = {
                "name": name,
                "espnId": ath.get("id"),
            }
    return by_team


def _resolve_projected_pitcher(raw: dict[str, Any], *, source: str) -> dict[str, Any] | None:
    name = (raw.get("name") or "").strip()
    if not name or name.upper() == "TBD":
        return None
    hit = _search_mlb_person(name)
    if not hit and raw.get("shortName"):
        hit = _search_mlb_person(str(raw["shortName"]))
    if not hit:
        return None
    return {
        "id": hit.get("id"),
        "name": hit.get("fullName") or name,
        "throws": (hit.get("pitchHand") or {}).get("code") or "",
        "source": source,
        "projected": True,
    }


def collect_projected_pitchers_by_team(sheet_date: str) -> tuple[dict[str, dict], dict[str, Any]]:
    """Merge FantasyPros (preferred) + ESPN for remaining teams."""
    meta: dict[str, Any] = {
        "source": "projected-pitchers",
        "fantasypros": 0,
        "espn": 0,
        "resolved": 0,
    }
    merged: dict[str, dict[str, Any]] = {}

    try:
        fp = fetch_fantasypros_pitchers_by_team(sheet_date)
        meta["fantasypros"] = len(fp)
        for abbr, raw in fp.items():
            resolved = _resolve_projected_pitcher(raw, source="fantasypros")
            if resolved:
                merged[abbr] = resolved
                meta["resolved"] += 1
    except Exception as exc:
        meta["fantasyprosError"] = str(exc)

    try:
        espn = fetch_espn_pitchers_by_team(sheet_date)
        meta["espn"] = len(espn)
        for abbr, raw in espn.items():
            if abbr in merged:
                continue
            resolved = _resolve_projected_pitcher(raw, source="espn")
            if resolved:
                merged[abbr] = resolved
                meta["resolved"] += 1
    except Exception as exc:
        meta["espnError"] = str(exc)

    return merged, meta


def apply_projected_pitcher_fallback_to_games(
    games: list[dict], sheet_date: str
) -> dict[str, Any]:
    """Fill TBD / missing probable starters from FantasyPros (+ ESPN)."""
    by_team, meta = collect_projected_pitchers_by_team(sheet_date)
    stats = {
        **meta,
        "games": len(games),
        "pitchersFilled": 0,
        "sheetDate": sheet_date,
    }
    if not by_team:
        return stats

    for game in games:
        away = normalize_abbr(game.get("away") or "")
        home = normalize_abbr(game.get("home") or "")
        if _pitcher_missing(game.get("awayPitcher")) and away in by_team:
            game["awayPitcher"] = dict(by_team[away])
            stats["pitchersFilled"] += 1
        if _pitcher_missing(game.get("homePitcher")) and home in by_team:
            game["homePitcher"] = dict(by_team[home])
            stats["pitchersFilled"] += 1
        # Keep matchup key consistent if callers attach extras.
        if away and home and not game.get("matchup"):
            game["matchup"] = game_key(away, home)

    return stats


def build_projected_pitchers_payload(sheet_date: str) -> dict[str, Any]:
    """API payload: per-team projected SPs (+ optional schedule-shaped games)."""
    by_team, meta = collect_projected_pitchers_by_team(sheet_date)
    games_out: list[dict[str, Any]] = []
    try:
        from research.mlb_api import fetch_schedule

        for g in fetch_schedule(sheet_date):
            row = {
                "matchup": g.get("matchup"),
                "away": g.get("away"),
                "home": g.get("home"),
                "awayPitcher": None,
                "homePitcher": None,
            }
            away = g.get("away")
            home = g.get("home")
            if away in by_team:
                row["awayPitcher"] = dict(by_team[away])
            if home in by_team:
                row["homePitcher"] = dict(by_team[home])
            games_out.append(row)
    except Exception as exc:
        meta["scheduleError"] = str(exc)

    return {
        "date": sheet_date,
        "source": "projected-pitchers",
        "byTeam": by_team,
        "games": games_out,
        "meta": meta,
    }
