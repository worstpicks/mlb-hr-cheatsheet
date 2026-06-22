#!/usr/bin/env python3
"""PropFinder hr-matchups CSV stats (Near HR, recent-window rates)."""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from csv_slate_meta import manifest_matchup_files, name_lookup_key, normalize_batter_name
from sheet_data import DATA_DIR

LINEUP_PREFIX_RE = re.compile(r"^\d+\s+")


def _float(val: Any) -> float | None:
    if val is None:
        return None
    s = str(val).strip().replace("%", "")
    if not s or s in ("-", "NA", "N/A"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _int(val: Any) -> int | None:
    f = _float(val)
    if f is None:
        return None
    return int(f)


def _read_matchup_batters(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header: list[str] | None = None
        for row in reader:
            if row and row[0] == "BATTER":
                header = [c.strip() for c in row]
                continue
            if not header or not row or not row[0]:
                continue
            if row[0].startswith("SPLIT") or row[0] == "BATTER":
                continue
            data = dict(zip(header, row))
            name = normalize_batter_name(row[0].strip())
            rows.append({"name": name, "data": data})
    return rows


def _row_to_stats(data: dict) -> dict:
    hr = _int(data.get("HR"))
    near = _int(data.get("NEAR HR"))
    pa = _int(data.get("PA"))
    avg = _float(data.get("BA"))
    iso = _float(data.get("ISO"))
    woba = _float(data.get("WOBA"))
    ev = _float(data.get("EV"))
    barrel = _float(data.get("BARREL%"))
    whiff = _float(data.get("WHIFF%"))
    fb = _float(data.get("FB%"))
    gb = _float(data.get("GB%"))
    ld = _float(data.get("LD%"))
    hr_fb = _float(data.get("HR/FB%"))
    hard_hit = _float(data.get("HH%"))
    return {
        "nearHr": near,
        "hr": hr,
        "pa": pa,
        "avg": avg,
        "iso": iso,
        "xwoba": woba,
        "avgEV": ev,
        "barrelPct": barrel,
        "whiffPct": whiff,
        "fbPct": fb,
        "gbPct": gb,
        "ldPct": ld,
        "hrFbPct": hr_fb,
        "hardHitPct": hard_hit,
        "source": "propfinder",
    }


def load_propfinder_lookup(sheet_date: str, data_dir: Path | None = None) -> dict[str, dict]:
    """name_lookup_key -> PropFinder recent-window profile."""
    data_dir = data_dir or DATA_DIR
    lookup: dict[str, dict] = {}
    for path in manifest_matchup_files(sheet_date, data_dir):
        if sheet_date not in path.name:
            continue
        for row in _read_matchup_batters(path):
            key = name_lookup_key(row["name"])
            stats = _row_to_stats(row["data"])
            if key not in lookup:
                lookup[key] = stats
            else:
                prev = lookup[key]
                if (stats.get("nearHr") or 0) > (prev.get("nearHr") or 0):
                    lookup[key] = stats
    return lookup
