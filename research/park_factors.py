#!/usr/bin/env python3
"""Scan data/ for the latest ParkFactors CSV and export lookup for Research."""
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

_PARK_FACTORS_RE = re.compile(r"ParkFactors_(\d{4}-\d{2}-\d{2})")
_HAND_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def park_factors_date_from_path(path: Path) -> str | None:
    m = _PARK_FACTORS_RE.search(path.name)
    return m.group(1) if m else None


def find_latest_park_factors_csv(data_dir: Path | None = None) -> Path | None:
    data_dir = data_dir or ROOT / "data"
    candidates = list(data_dir.glob("ParkFactors_*.csv"))
    if not candidates:
        return None

    def sort_key(p: Path) -> tuple[str, float]:
        date_key = park_factors_date_from_path(p) or "0000-00-00"
        return date_key, p.stat().st_mtime

    return max(candidates, key=sort_key)


def find_latest_park_hand_date(data_dir: Path | None = None) -> str | None:
    data_dir = data_dir or ROOT / "data"
    dates: list[str] = []
    for pattern in ("park-factors-L-all-*.csv", "park-factors-R-all-*.csv"):
        for path in data_dir.glob(pattern):
            m = _HAND_DATE_RE.search(path.name)
            if m:
                dates.append(m.group(1))
    return max(dates) if dates else None


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
    game = normalize_game_key(row.get("Game", ""))
    if not game:
        return None
    try:
        hr_pct = int(str(row["HR %"]).replace("%", "").strip())
    except (ValueError, KeyError):
        return None
    venue = (row.get("Venue") or "").strip()
    venue_key = normalize_venue_key(venue)
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


def load_latest_park_lookup(data_dir: Path | None = None) -> dict:
    data_dir = data_dir or ROOT / "data"
    path = find_latest_park_factors_csv(data_dir)
    if not path or not path.is_file():
        return {}

    pf_date = park_factors_date_from_path(path) or ""
    hand_date = find_latest_park_hand_date(data_dir) or pf_date
    lhb_stadium, rhb_stadium = (
        load_venue_hand_stadium_pcts(hand_date) if hand_date else ({}, {})
    )

    by_game: dict[str, dict] = {}
    by_venue: dict[str, dict] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = _entry_from_row(row, lhb_stadium, rhb_stadium)
            if not entry:
                continue
            by_game[entry["game"]] = entry
            if entry.get("venue_key"):
                by_venue[entry["venue_key"]] = entry

    return {
        "source_file": path.name,
        "source_date": pf_date,
        "hand_date": hand_date or None,
        "by_game": by_game,
        "by_venue": by_venue,
    }


def attach_park_factors_to_games(games: list[dict], lookup: dict) -> None:
    if not lookup:
        return
    by_game = lookup.get("by_game") or {}
    by_venue = lookup.get("by_venue") or {}
    source = lookup.get("source_file")
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
        if ctx.get("park_rhb_pct") is not None:
            game["parkRhbPct"] = ctx["park_rhb_pct"]
        if ctx.get("venue"):
            game["venue"] = game.get("venue") or ctx["venue"]
        if source:
            game["parkFactorSource"] = source


def write_park_factors_json(out_dir: Path) -> Path | None:
    lookup = load_latest_park_lookup()
    if not lookup.get("by_game") and not lookup.get("by_venue"):
        return None
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "park-factors.json"
    out_path.write_text(json.dumps(lookup, indent=2) + "\n", encoding="utf-8")
    return out_path
