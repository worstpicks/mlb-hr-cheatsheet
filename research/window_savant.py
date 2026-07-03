#!/usr/bin/env python3
"""Batter stat profiles — full-season Savant Statcast."""
from __future__ import annotations

import csv
import io
import urllib.request
from typing import Any

STATCAST_SEARCH_BASE = (
    "https://baseballsavant.mlb.com/statcast_search/csv?all=true&player_type=batter"
    "&hfSea={season}%7C&hfGT=R%7C&min_pitches=0&min_results=5"
    "&group_by=name&sort_col=pitches&sort_order=desc"
)

# Season-only Savant statcast window
WINDOW_SPECS: dict[str, int | None] = {
    "season": None,
}


def _float(val: Any) -> float | None:
    if val is None:
        return None
    s = str(val).strip().replace("%", "")
    if not s or s in ("-", "NA", "N/A", ""):
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


def _index_by_player(rows: list[dict]) -> dict[int, dict]:
    out: dict[int, dict] = {}
    for row in rows:
        pid = _int(row.get("player_id"))
        if pid:
            out[pid] = row
    return out


def _parse_core_row(row: dict) -> dict:
    ba = _float(row.get("ba"))
    slg = _float(row.get("slg"))
    iso = round(slg - ba, 3) if ba is not None and slg is not None else None
    return {
        "pa": _int(row.get("pa")),
        "hr": _int(row.get("hrs")),
        "avg": ba,
        "iso": iso,
        "xwoba": _float(row.get("xwoba")),
        "woba": _float(row.get("woba")),
        "barrelPct": _float(row.get("barrels_per_pa_percent")),
        "hardHitPct": _float(row.get("hardhit_percent")),
        "avgEV": _float(row.get("launch_speed")),
        "whiffPct": _float(row.get("swing_miss_percent")),
        "bip": _int(row.get("bip")),
    }


def fetch_season_statcast_lookup(season: int) -> dict[int, dict]:
    """Full-season Savant statcast search + pull spray metrics."""
    base = STATCAST_SEARCH_BASE.format(season=season)
    all_rows = _fetch_csv(base)
    pull_rows = _fetch_csv(base + "&hfPull=Pull%7C")
    pull_air_rows = _fetch_csv(base + "&hfPull=Pull%7C&hfBBT=fly_ball%7Cline_drive%7C")
    pull_barrel_rows = _fetch_csv(base + "&hfPull=Pull%7C&hfSA=6%7C")

    all_by_id = _index_by_player(all_rows)
    pull_by_id = _index_by_player(pull_rows)
    pull_air_by_id = _index_by_player(pull_air_rows)
    pull_barrel_by_id = _index_by_player(pull_barrel_rows)

    lookup: dict[int, dict] = {}
    for pid, row in all_by_id.items():
        stats = _parse_core_row(row)
        total_bip = stats.get("bip") or 0
        if total_bip > 0:
            pull_bip = _int((pull_by_id.get(pid) or {}).get("bip")) or 0
            pull_air_bip = _int((pull_air_by_id.get(pid) or {}).get("bip")) or 0
            pull_barrel_bip = _int((pull_barrel_by_id.get(pid) or {}).get("bip")) or 0
            stats["pullPct"] = round(100.0 * pull_bip / total_bip, 1)
            stats["pullAirPct"] = round(100.0 * pull_air_bip / total_bip, 1)
            stats["pullBarrelPct"] = round(100.0 * pull_barrel_bip / total_bip, 1)
        stats["source"] = "savant-season"
        lookup[pid] = stats
    return lookup


def fetch_all_window_lookups(
    season: int,
    sheet_date: str,
    player_ids: list[int],
) -> dict[str, dict[int, dict]]:
    """Full-season Savant statcast lookup."""
    del sheet_date, player_ids
    return {"season": fetch_season_statcast_lookup(season)}


def merge_season_savant(window_stats: dict, savant: dict | None) -> dict:
    """Overlay full-season Savant CSV fields onto statcast season window."""
    out = dict(window_stats or {})
    savant = savant or {}
    for key in (
        "avg",
        "iso",
        "xwoba",
        "barrelPct",
        "hardHitPct",
        "avgEV",
        "fbPct",
        "gbPct",
        "ldPct",
        "hrFbPct",
        "whiffPct",
        "pa",
        "recentForm",
        "hr",
        "pullPct",
        "pullAirPct",
        "pullBarrelPct",
        "xwobaVsLhp",
        "paVsLhp",
        "xwobaVsRhp",
        "paVsRhp",
    ):
        if savant.get(key) is not None:
            out[key] = savant[key]
    if savant.get("pullPct") is None and window_stats.get("pullPct") is not None:
        out["pullPct"] = window_stats["pullPct"]
    if savant.get("pullAirPct") is None and window_stats.get("pullAirPct") is not None:
        out["pullAirPct"] = window_stats["pullAirPct"]
    if savant.get("pullBarrelPct") is None and window_stats.get("pullBarrelPct") is not None:
        out["pullBarrelPct"] = window_stats["pullBarrelPct"]
    out["source"] = "savant"
    return out
