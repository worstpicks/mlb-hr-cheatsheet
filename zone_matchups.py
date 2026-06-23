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
    "ryan": ["rojas"],
    "rojas": ["ryan"],
    "marquez": ["ritchie", "canning"],
    "ritchie": ["marquez"],
    "canning": ["marquez"],
    "quantrill": ["corniell"],
    "corniell": ["quantrill"],
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


def zone_csv_paths(sheet_date: str, data_dir: Path | None = None) -> list[Path]:
    """All zone-matchups exports for a slate date (base + numbered re-exports)."""
    data = data_dir or DATA_DIR
    paths = sorted(data.glob(f"zone-matchups-{sheet_date}*.csv"))
    if paths:
        return paths
    legacy = data / f"zone-matchups-{sheet_date}.csv"
    return [legacy] if legacy.is_file() else []


def zone_csv_path(sheet_date: str, data_dir: Path | None = None) -> Path | None:
    paths = zone_csv_paths(sheet_date, data_dir)
    return paths[0] if paths else None


def _row_entry(row: dict) -> dict:
    return {
        "zone_score": _num(row.get("ZoneScore")),
        "contact": _num(row.get("Contact")),
        "barrel": _num(row.get("Barrel")),
        "hr": _num(row.get("HR")),
        "hard_hit": _num(row.get("HardHit")),
        "pitcher": (row.get("Pitcher") or "").strip(),
    }


def _merge_entry(existing: dict | None, incoming: dict) -> dict:
    if existing is None:
        return incoming
    if incoming.get("zone_score") is not None and existing.get("zone_score") is None:
        return incoming
    if existing.get("zone_score") is not None:
        return existing
    # Both missing zone score — keep whichever has more populated fields.
    existing_fields = sum(1 for k in ("contact", "barrel", "hr", "hard_hit") if existing.get(k) is not None)
    incoming_fields = sum(1 for k in ("contact", "barrel", "hr", "hard_hit") if incoming.get(k) is not None)
    return incoming if incoming_fields > existing_fields else existing


def load_zone_lookup(sheet_date: str, data_dir: Path | None = None) -> dict[tuple[str, str], dict]:
    """(batter_key, pitcher_last_lower) -> zone stat dict."""
    paths = zone_csv_paths(sheet_date, data_dir)
    if not paths:
        return {}
    lookup: dict[tuple[str, str], dict] = {}
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                batter = name_lookup_key(row.get("Batter", ""))
                pitcher = (row.get("Pitcher") or "").strip().split()[-1].lower()
                if not batter or not pitcher:
                    continue
                key = (batter, pitcher)
                lookup[key] = _merge_entry(lookup.get(key), _row_entry(row))
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
    best: dict | None = None
    for pk in pitcher_keys_for_lookup(chip):
        hit = lookup.get((batter_key, pk))
        if not hit:
            continue
        if hit.get("zone_score") is not None:
            return hit
        if best is None:
            best = hit
    return best
