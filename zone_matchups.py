#!/usr/bin/env python3
"""Load PropFinder zone-matchups CSV for batter vs SP zone-fit scores."""
from __future__ import annotations

import csv
from pathlib import Path

from csv_slate_meta import name_lookup_key
from sheet_data import DATA_DIR

# Sheet probable may differ from PropFinder zone export (same overrides as build scripts).
ZONE_PITCHER_ALIASES: dict[str, list[str]] = {
    "gibson": ["bassitt"],
    "englert": ["seymour"],
}


def _num(val: str | None) -> float | None:
    if val is None:
        return None
    v = str(val).strip()
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def zone_csv_path(sheet_date: str, data_dir: Path | None = None) -> Path | None:
    data = data_dir or DATA_DIR
    path = data / f"zone-matchups-{sheet_date}.csv"
    return path if path.is_file() else None


def load_zone_lookup(sheet_date: str, data_dir: Path | None = None) -> dict[tuple[str, str], dict]:
    """(batter_key, pitcher_last_lower) -> zone stat dict."""
    path = zone_csv_path(sheet_date, data_dir)
    if not path:
        return {}
    lookup: dict[tuple[str, str], dict] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            batter = name_lookup_key(row.get("Batter", ""))
            pitcher = (row.get("Pitcher") or "").strip().split()[-1].lower()
            if not batter or not pitcher:
                continue
            entry = {
                "zone_score": _num(row.get("ZoneScore")),
                "contact": _num(row.get("Contact")),
                "barrel": _num(row.get("Barrel")),
                "hr": _num(row.get("HR")),
                "hard_hit": _num(row.get("HardHit")),
                "pitcher": row.get("Pitcher", "").strip(),
            }
            lookup[(batter, pitcher)] = entry
    return lookup


def pitcher_keys_for_lookup(pitcher_label: str) -> list[str]:
    """Last-name keys to try when joining zone row to sheet chip."""
    last = pitcher_label.replace("vs ", "").strip().split()[-1].lower()
    keys = [last]
    for alias in ZONE_PITCHER_ALIASES.get(last, []):
        if alias not in keys:
            keys.append(alias)
    return keys


def lookup_zone_row(batter_name: str, pitcher_chip: str, lookup: dict[tuple[str, str], dict]) -> dict | None:
    if not lookup:
        return None
    batter_key = name_lookup_key(batter_name)
    chip = (pitcher_chip or "").replace("vs ", "").strip()
    if not chip:
        return None
    for pk in pitcher_keys_for_lookup(chip):
        hit = lookup.get((batter_key, pk))
        if hit:
            return hit
    return None
