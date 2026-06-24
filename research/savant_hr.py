#!/usr/bin/env python3
"""Baseball Savant Home Run Tracker (encode=raw embedded JSON)."""
from __future__ import annotations

import json
import re
import urllib.request
from typing import Any

SAVANT_HR_RAW_URL = (
    "https://baseballsavant.mlb.com/leaderboard/home-runs"
    "?player_type=Batter&year={season}&min=0&cat=adj_xhr&encode=raw"
)


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


def _extract_data_array(html: str) -> list[dict]:
    match = re.search(r"var\s+data\s*=\s*(\[)", html)
    if not match:
        return []
    start = match.start(1)
    depth = 0
    for i, ch in enumerate(html[start:], start):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return json.loads(html[start : i + 1])
    return []


def _hr_luck_flag(hr_luck_diff: float | None, mostly_gone: int | None, hr_total: int | None) -> str | None:
    """Actionable regression / park-context tiers for prop research."""
    if hr_luck_diff is not None and hr_luck_diff >= 2.0:
        return "due"
    mg = mostly_gone or 0
    hr = hr_total or 0
    if mg >= 6 and hr_luck_diff is not None and hr_luck_diff >= 1.0:
        return "park"
    if mg >= 8 and hr <= 15:
        return "park"
    return None


def _parse_hr_row(row: dict) -> dict:
    xhr = _float(row.get("xhr"))
    hr_total = _int(row.get("hr_total"))
    mostly_gone = _int(row.get("mostly_gone"))
    no_doubters = _int(row.get("no_doubters"))
    doublers = _int(row.get("doubters"))
    near_hr = _int(row.get("non_hr_would_have_left"))
    hr_luck_diff = round(xhr - hr_total, 1) if xhr is not None and hr_total is not None else None
    return {
        "expectedHr": xhr,
        "hrLuckDiff": hr_luck_diff,
        "mostlyGone": mostly_gone,
        "noDoubters": no_doubters,
        "doubters": doublers,
        "nearHr": near_hr,
        "hrLuckFlag": _hr_luck_flag(hr_luck_diff, mostly_gone, hr_total),
        "hrTrackerSource": "savant-hr",
    }


def fetch_hr_tracker_lookup(season: int, timeout: int = 90) -> dict[int, dict]:
    """player_id -> Savant HR tracker profile (xHR, luck diff, mostly-gone, near HR)."""
    url = SAVANT_HR_RAW_URL.format(season=season)
    req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz-Research/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        html = resp.read().decode("utf-8", "replace")
    lookup: dict[int, dict] = {}
    for row in _extract_data_array(html):
        pid = _int(row.get("player_id"))
        if not pid:
            continue
        parsed = _parse_hr_row(row)
        if any(parsed.get(k) is not None for k in ("expectedHr", "nearHr", "mostlyGone")):
            lookup[pid] = parsed
    return lookup
