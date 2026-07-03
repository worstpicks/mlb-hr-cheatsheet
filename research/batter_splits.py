#!/usr/bin/env python3
"""Batter platoon splits (xwOBA vs LHP/RHP) from Baseball Savant statcast search."""
from __future__ import annotations

import csv
import io
import json
import urllib.request
from pathlib import Path
from typing import Any

SAVANT_BATTER_HAND_SEARCH = (
    "https://baseballsavant.mlb.com/statcast_search/csv?all=true&player_type=batter"
    "&hfSea={season}%7C&hfGT=R%7C&min_pitches=0&min_results=20"
    "&group_by=name&sort_col=pitches&sort_order=desc&min_abs=0"
    "&pitcher_throws={hand}"
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


def _fetch_csv(url: str, timeout: int = 120) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz-Research/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode("utf-8-sig")
    if not text.strip() or text.lstrip().startswith("<!"):
        return []
    return list(csv.DictReader(io.StringIO(text)))


def fetch_batter_hand_split_lookup(season: int) -> dict[int, dict]:
    """{batter_id: {xwobaVsLhp, paVsLhp, xwobaVsRhp, paVsRhp}} for the season."""
    out: dict[int, dict] = {}
    for hand, xw_key, pa_key in (("L", "xwobaVsLhp", "paVsLhp"), ("R", "xwobaVsRhp", "paVsRhp")):
        url = SAVANT_BATTER_HAND_SEARCH.format(season=season, hand=hand)
        for row in _fetch_csv(url):
            pid = _int(row.get("player_id"))
            if not pid:
                continue
            xwoba = _float(row.get("xwoba"))
            pa = _int(row.get("pa"))
            if xwoba is None:
                continue
            entry = out.setdefault(pid, {})
            entry[xw_key] = xwoba
            if pa is not None:
                entry[pa_key] = pa
    return out


def write_batter_hand_cache(lookup: dict[int, dict], out_dir: Path, season: int) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"savant-batter-hand-{season}.json"
    payload = {
        "season": season,
        "source": "savant-batter-hand-splits",
        "batters": len(lookup),
        "lookup": {str(k): v for k, v in lookup.items()},
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out_path
