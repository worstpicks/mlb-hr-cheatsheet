#!/usr/bin/env python3
"""Baseball Savant statcast leaderboard (CSV export API)."""
from __future__ import annotations

import csv
import io
import json
import urllib.request
from pathlib import Path
from typing import Any

SAVANT_CUSTOM_CSV = (
    "https://baseballsavant.mlb.com/leaderboard/custom"
    "?year={season}&type=batter&filter=&min=10"
    "&selections=player_id,player_name,woba,xwoba,xba,xiso,pa,home_run,whiff_percent,"
    "barrel_batted_rate,hard_hit_percent,exit_velocity_avg,flyballs_percent,"
    "groundballs_percent,linedrives_percent,flyballs,hr_flyball_percent,pull_percent"
    "&chart=false&csv=true"
)

SAVANT_EXPECTED_CSV = (
    "https://baseballsavant.mlb.com/leaderboard/expected_statistics"
    "?type=batter&year={season}&position=&team=&min=10&csv=true"
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


def _fetch_csv(url: str, timeout: int = 90) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz-Research/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def _hr_fb_pct(row: dict) -> float | None:
    direct = _float(row.get("hr_flyball_percent"))
    if direct is not None:
        return direct
    hr = _int(row.get("home_run"))
    flyballs = _int(row.get("flyballs"))
    if hr is not None and flyballs and flyballs > 0:
        return round(100.0 * hr / flyballs, 1)
    return None


def _iso_from_ba_slg(ba: float | None, slg: float | None) -> float | None:
    if ba is not None and slg is not None:
        return round(slg - ba, 3)
    return None


def _parse_custom_row(row: dict) -> dict:
    return {
        "xwoba": _float(row.get("xwoba")),
        "iso": _float(row.get("xiso")),
        "pa": _int(row.get("pa")),
        "hr": _int(row.get("home_run")),
        "whiffPct": _float(row.get("whiff_percent")),
        "barrelPct": _float(row.get("barrel_batted_rate")),
        "hardHitPct": _float(row.get("hard_hit_percent")),
        "avgEV": _float(row.get("exit_velocity_avg")),
        "fbPct": _float(row.get("flyballs_percent")),
        "gbPct": _float(row.get("groundballs_percent")),
        "ldPct": _float(row.get("linedrives_percent")),
        "hrFbPct": _hr_fb_pct(row),
        "pullPct": _float(row.get("pull_percent")),
    }


def _parse_expected_row(row: dict) -> dict:
    ba = _float(row.get("ba"))
    slg = _float(row.get("slg"))
    form_diff = _float(row.get("est_woba_minus_woba_diff"))
    recent_form = round(form_diff * 100, 1) if form_diff is not None else None
    return {
        "avg": ba,
        "slg": slg,
        "iso": _iso_from_ba_slg(ba, slg),
        "xwoba": _float(row.get("est_woba")),
        "pa": _int(row.get("pa")),
        "recentForm": recent_form,
    }


def _merge_savant_rows(custom: dict, expected: dict) -> dict:
    out: dict = {"source": "savant"}
    for key, val in custom.items():
        if val is not None:
            out[key] = val
    for key, val in expected.items():
        if val is not None:
            out[key] = val
    if out.get("iso") is None and custom.get("iso") is not None:
        out["iso"] = custom["iso"]
    return out


def fetch_batter_statcast_lookup(season: int) -> dict[int, dict]:
    """player_id -> Savant season profile (custom + expected statistics CSVs)."""
    custom_rows = _fetch_csv(SAVANT_CUSTOM_CSV.format(season=season))
    expected_rows = _fetch_csv(SAVANT_EXPECTED_CSV.format(season=season))

    expected_by_id: dict[int, dict] = {}
    for row in expected_rows:
        pid = _int(row.get("player_id"))
        if pid:
            expected_by_id[pid] = _parse_expected_row(row)

    lookup: dict[int, dict] = {}
    seen: set[int] = set()
    for row in custom_rows:
        pid = _int(row.get("player_id"))
        if not pid:
            continue
        seen.add(pid)
        lookup[pid] = _merge_savant_rows(_parse_custom_row(row), expected_by_id.get(pid, {}))

    for pid, expected in expected_by_id.items():
        if pid not in seen:
            lookup[pid] = _merge_savant_rows({}, expected)

    return lookup


def write_savant_cache(lookup: dict[int, dict], out_dir: Path, season: int) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"savant-batter-{season}.json"
    payload = {
        "season": season,
        "source": "savant-csv",
        "batters": len(lookup),
        "lookup": {str(k): v for k, v in lookup.items()},
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out_path


def merge_into_hitter_stats(
    window: dict | None,
    savant: dict | None,
    propfinder: dict | None = None,
    *,
    savant_only: bool = True,
) -> dict:
    """Savant CSV profile; optional MLB window + PropFinder when savant_only=False."""
    out: dict = {"source": "savant"}
    savant = savant or {}

    savant_keys = (
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
        "pullPct",
        "pullAirPct",
        "pullBarrelPct",
    )
    for key in savant_keys:
        if savant.get(key) is not None:
            out[key] = savant[key]

    propfinder = propfinder or {}
    if propfinder.get("nearHr") is not None:
        out["nearHr"] = propfinder["nearHr"]

    if savant_only:
        if propfinder:
            out["source"] = "savant+propfinder" if out.get("nearHr") is not None else "savant"
        return out

    window = window or {}
    for key in ("hr", "hits", "ab"):
        if window.get(key) is not None:
            out[key] = window[key]
    if out.get("hr") is None and savant.get("hr") is not None:
        out["hr"] = savant["hr"]
    for key in ("obp", "slg", "kPct", "bbPct"):
        if window.get(key) is not None:
            out[key] = window[key]

    sources = ["savant"]
    if window:
        sources.append("mlb-window")
    if propfinder:
        sources.append("propfinder")
    out["source"] = "+".join(sources)
    return out
