#!/usr/bin/env python3
"""Load date-matched ParkFactors CSV and export per-slate lookup for Research."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from game_row_enrich import (
    ROOT,
    TITLE_WEATHER_KEY_ALIASES,
    load_venue_hand_stadium_pcts,
    normalize_game_key,
    normalize_venue_key,
)

_PARK_FACTORS_DATE_RE = re.compile(
    r"ParkFactors_(?P<y>\d{4})-(?P<m>\d{2})[-.](?P<d>\d{2})"
)


def _date_from_park_csv_name(name: str) -> str | None:
    m = _PARK_FACTORS_DATE_RE.search(name)
    if not m:
        return None
    return f"{m['y']}-{m['m']}-{m['d']}"


def park_factors_date_from_path(path: Path) -> str | None:
    return _date_from_park_csv_name(path.name)


def find_park_factors_csv(sheet_date: str, data_dir: Path | None = None) -> Path | None:
    """ParkFactors CSV for this slate date only (never a different day's file)."""
    data_dir = data_dir or ROOT / "data"
    y, m, d = sheet_date.split("-")
    candidates = [
        data_dir / f"ParkFactors_{sheet_date}.csv",
        data_dir / f"ParkFactors_{y}-{m}.{d}.csv",
    ]
    for path in candidates:
        if path.is_file():
            return path
    matches = sorted(data_dir.glob(f"ParkFactors_{sheet_date}*.csv"))
    if matches:
        return matches[0]
    for path in sorted(data_dir.glob("ParkFactors_*.csv")):
        if _date_from_park_csv_name(path.name) == sheet_date:
            return path
    return None


def _latest_hand_park_date(sheet_date: str, data_dir: Path) -> str | None:
    """Most recent Ballpark Pal L-hand export on or before sheet_date."""
    dates: list[str] = []
    for path in data_dir.glob("park-factors-L-all-*.csv"):
        m = re.search(r"park-factors-L-all-(\d{4}-\d{2}-\d{2})", path.name)
        if m:
            dates.append(m.group(1))
    if not dates:
        return None
    dates = sorted(set(dates))
    eligible = [d for d in dates if d <= sheet_date]
    return eligible[-1] if eligible else dates[-1]


def load_stadium_only_lookup(sheet_date: str, data_dir: Path | None = None) -> dict:
    """Stadium HR % by venue when the daily ParkFactors CSV is missing."""
    data_dir = data_dir or ROOT / "data"
    ref_date = _latest_hand_park_date(sheet_date, data_dir)
    if not ref_date:
        return {}
    lhb_stadium, rhb_stadium = load_venue_hand_stadium_pcts(ref_date)
    if not lhb_stadium and not rhb_stadium:
        return {}
    by_venue: dict[str, dict] = {}
    for vk in set(lhb_stadium) | set(rhb_stadium):
        lhb = lhb_stadium.get(vk)
        rhb = rhb_stadium.get(vk)
        if lhb is not None and rhb is not None:
            hr_pct = int(round((lhb + rhb) / 2))
        elif lhb is not None:
            hr_pct = lhb
        elif rhb is not None:
            hr_pct = rhb
        else:
            continue
        entry: dict = {
            "venue_key": vk,
            "hr_pct": hr_pct,
            "stadium_pct": hr_pct,
            "weather_pct": 0,
        }
        if lhb is not None:
            entry["lhb_stadium_pct"] = lhb
            entry["park_lhb_pct"] = lhb
        if rhb is not None:
            entry["rhb_stadium_pct"] = rhb
            entry["park_rhb_pct"] = rhb
        by_venue[vk] = entry
    if not by_venue:
        return {}
    return {
        "source": "ballpark-pal-stadium",
        "source_label": f"Ballpark Pal stadium ({ref_date})",
        "source_file": f"park-factors-L/R-all-{ref_date}.csv",
        "source_date": sheet_date,
        "hand_date": ref_date,
        "stadium_only": True,
        "by_game": {},
        "by_venue": by_venue,
    }


def _pct_from_field(val: str | None) -> int | None:
    if not val:
        return None
    m = re.search(r"([+-]?\d+)", str(val).replace("%", ""))
    return int(m.group(1)) if m else None


def _entry_from_row(
    row: dict,
    lhb_stadium: dict[str, int],
    rhb_stadium: dict[str, int],
) -> dict | None:
    # Special-event sites (e.g. Field of Dreams) ship a blank Game column. Keep the row
    # so it can still be matched on venue instead of dropping the game's park factors.
    game = normalize_game_key(row.get("Game", ""))
    try:
        hr_pct = int(str(row["HR %"]).replace("%", "").strip())
    except (ValueError, KeyError):
        return None
    venue = (row.get("Venue") or "").strip()
    venue_key = normalize_venue_key(venue)
    if not game and not venue_key:
        return None
    wx_pct = _pct_from_field(row.get("HR % Weather"))
    lhb_st = lhb_stadium.get(venue_key)
    rhb_st = rhb_stadium.get(venue_key)
    entry: dict = {
        "game": game,
        "venue": venue,
        "venue_key": venue_key,
        "hr_pct": hr_pct,
        "stadium_pct": _pct_from_field(row.get("HR % Stadium")),
        "weather_pct": wx_pct,
    }
    if lhb_st is not None:
        entry["lhb_stadium_pct"] = lhb_st
        entry["park_lhb_pct"] = lhb_st + (wx_pct or 0)
    if rhb_st is not None:
        entry["rhb_stadium_pct"] = rhb_st
        entry["park_rhb_pct"] = rhb_st + (wx_pct or 0)
    return entry


def load_park_lookup(sheet_date: str, data_dir: Path | None = None) -> dict:
    """Ballpark Pal park factors for one slate date. Empty dict if no matching CSV."""
    data_dir = data_dir or ROOT / "data"
    path = find_park_factors_csv(sheet_date, data_dir)
    if not path:
        return load_stadium_only_lookup(sheet_date, data_dir)

    pf_date = park_factors_date_from_path(path) or sheet_date
    if pf_date != sheet_date:
        return {}

    lhb_stadium, rhb_stadium = load_venue_hand_stadium_pcts(sheet_date)

    by_game: dict[str, dict] = {}
    by_venue: dict[str, dict] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = _entry_from_row(row, lhb_stadium, rhb_stadium)
            if not entry:
                continue
            if entry["game"]:
                by_game[entry["game"]] = entry
            if entry.get("venue_key"):
                by_venue[entry["venue_key"]] = entry

    return {
        "source": "ballpark-pal",
        "source_label": "Ballpark Pal",
        "source_file": path.name,
        "source_date": sheet_date,
        "hand_date": sheet_date,
        "by_game": by_game,
        "by_venue": by_venue,
    }


def attach_park_factors_to_games(games: list[dict], lookup: dict) -> None:
    if not lookup:
        return
    by_game = lookup.get("by_game") or {}
    by_venue = lookup.get("by_venue") or {}
    source_label = lookup.get("source_label") or "Ballpark Pal"
    for game in games:
        key = normalize_game_key(game.get("matchup") or "")
        key = TITLE_WEATHER_KEY_ALIASES.get(key, key)
        ctx = by_game.get(key)
        if not ctx:
            vk = normalize_venue_key(game.get("venue") or "")
            ctx = by_venue.get(vk)
            if not ctx and vk:
                for venue_key, entry in by_venue.items():
                    if vk in venue_key or venue_key in vk:
                        ctx = entry
                        break
        if not ctx:
            continue
        if ctx.get("hr_pct") is not None:
            game["parkHrPct"] = ctx["hr_pct"]
        if ctx.get("park_lhb_pct") is not None:
            game["parkLhbPct"] = ctx["park_lhb_pct"]
        else:
            game.pop("parkLhbPct", None)
        if ctx.get("park_rhb_pct") is not None:
            game["parkRhbPct"] = ctx["park_rhb_pct"]
        else:
            game.pop("parkRhbPct", None)
        if ctx.get("stadium_pct") is not None:
            game["parkStadiumPct"] = ctx["stadium_pct"]
        if ctx.get("weather_pct") is not None:
            game["parkWeatherPct"] = ctx["weather_pct"]
        if ctx.get("lhb_stadium_pct") is not None:
            game["parkLhbStadiumPct"] = ctx["lhb_stadium_pct"]
        if ctx.get("rhb_stadium_pct") is not None:
            game["parkRhbStadiumPct"] = ctx["rhb_stadium_pct"]
        if ctx.get("venue"):
            game["venue"] = game.get("venue") or ctx["venue"]
        if source_label:
            game["parkFactorSource"] = source_label


def write_park_factors_json(out_dir: Path, sheet_date: str) -> Path | None:
    lookup = load_park_lookup(sheet_date)
    if not lookup.get("by_game") and not lookup.get("by_venue"):
        return None
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"park-factors-{sheet_date}.json"
    out_path.write_text(json.dumps(lookup, indent=2) + "\n", encoding="utf-8")
    return out_path
