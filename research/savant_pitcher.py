#!/usr/bin/env python3
"""Baseball Savant pitcher statcast profile (contact allowed + command)."""
from __future__ import annotations

import csv
import io
import json
import urllib.request
from pathlib import Path
from typing import Any

SAVANT_PITCHER_CUSTOM_CSV = (
    "https://baseballsavant.mlb.com/leaderboard/custom"
    "?year={season}&type=pitcher&filter=&min=10"
    "&selections=player_id,player_name,barrel_batted_rate,hard_hit_percent,exit_velocity_avg,"
    "flyballs_percent,hr_flyball_percent,pull_percent,in_zone_percent,edge_percent,whiff_percent,"
    "k_percent,sweet_spot_percent,meatball_percent,home_run,flyballs,innings_pitched"
    "&chart=false&csv=true"
)

SAVANT_PITCHER_HAND_SEARCH = (
    "https://baseballsavant.mlb.com/statcast_search/csv?all=true&player_type=pitcher"
    "&hfSea={season}%7C&hfGT=R%7C&min_pitches=0&min_results=10"
    "&group_by=name&sort_col=pitches&sort_order=desc&min_abs=0"
    "&batter_stands={batter_stand}{extra}"
)


def _index_rows_by_player(rows: list[dict]) -> dict[int, dict]:
    out: dict[int, dict] = {}
    for row in rows:
        pid = _int(row.get("player_id"))
        if pid:
            out[pid] = row
    return out


def _parse_hand_search_row(all_row: dict, fly_row: dict | None = None) -> dict:
    """Pitcher allowed-contact profile vs LHB or RHB from Statcast Search."""
    bip = _int(all_row.get("bip"))
    fly_bip = _int((fly_row or {}).get("bip"))
    fly_hrs = _int((fly_row or {}).get("hrs"))
    pa = _int(all_row.get("pa"))
    hrs = _int(all_row.get("hrs"))
    hr9 = None
    if hrs is not None and pa and pa > 0:
        hr9 = round((hrs / pa) * 27.0, 2)
    fb_pct = None
    if bip and fly_bip is not None and bip > 0:
        fb_pct = round(100.0 * fly_bip / bip, 1)
    hr_fb_pct = None
    if fly_hrs is not None and fly_bip and fly_bip > 0:
        hr_fb_pct = round(100.0 * fly_hrs / fly_bip, 1)
    return {
        "barrelPct": _float(all_row.get("barrels_per_bbe_percent")),
        "hardHitPct": _float(all_row.get("hardhit_percent")),
        "avgEV": _float(all_row.get("launch_speed")),
        "fbPct": fb_pct,
        "hrFbPct": hr_fb_pct,
        "kPct": _float(all_row.get("k_percent")),
        "whiffPct": _float(all_row.get("swing_miss_percent")),
        "hrAllowed": hrs,
        "flyballsAllowed": fly_bip,
        "bip": bip,
        "pa": pa,
        "hr9": hr9,
    }


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


def _parse_custom_row(row: dict) -> dict:
    hr = _int(row.get("home_run"))
    ip = _float(row.get("innings_pitched"))
    hr9 = round((hr / ip) * 9.0, 2) if hr is not None and ip and ip > 0 else None
    return {
        "barrelPct": _float(row.get("barrel_batted_rate")),
        "hardHitPct": _float(row.get("hard_hit_percent")),
        "avgEV": _float(row.get("exit_velocity_avg")),
        "fbPct": _float(row.get("flyballs_percent")),
        "hrFbPct": _hr_fb_pct(row),
        "pullPct": _float(row.get("pull_percent")),
        "zonePct": _float(row.get("in_zone_percent")),
        "edgePct": _float(row.get("edge_percent")),
        "whiffPct": _float(row.get("whiff_percent")),
        "kPct": _float(row.get("k_percent")),
        "sweetSpotPct": _float(row.get("sweet_spot_percent")),
        "meatballPct": _float(row.get("meatball_percent")),
        "hrAllowed": hr,
        "inningsPitched": ip,
        "flyballsAllowed": _int(row.get("flyballs")),
        "hr9": hr9,
    }


def _parse_expected_row(row: dict) -> dict:
    return {
        "xera": _float(row.get("xera")),
        "era": _float(row.get("era")),
    }


SAVANT_PITCHER_EXPECTED_CSV = (
    "https://baseballsavant.mlb.com/leaderboard/expected_statistics"
    "?type=pitcher&year={season}&position=&team=&min=10&csv=true"
)


def fetch_pitcher_hand_split_lookup(season: int) -> dict[int, dict[str, dict]]:
    """player_id -> { lhb: stats, rhb: stats } from Savant vs LHB / vs RHB (batter_stands)."""
    lookup: dict[int, dict[str, dict]] = {}
    for hand_key, stand in (("lhb", "L"), ("rhb", "R")):
        all_rows = _fetch_csv(
            SAVANT_PITCHER_HAND_SEARCH.format(season=season, batter_stand=stand, extra="")
        )
        fly_rows = _fetch_csv(
            SAVANT_PITCHER_HAND_SEARCH.format(
                season=season, batter_stand=stand, extra="&hfBBT=fly_ball%7C"
            )
        )
        fly_by_id = _index_rows_by_player(fly_rows)
        for row in all_rows:
            pid = _int(row.get("player_id"))
            if not pid:
                continue
            parsed = _parse_hand_search_row(row, fly_by_id.get(pid))
            if not any(v is not None for k, v in parsed.items() if k not in ("bip", "pa")):
                continue
            parsed["source"] = f"savant-pitcher-{hand_key}"
            bucket = lookup.setdefault(pid, {})
            bucket[hand_key] = parsed
    return lookup


def write_savant_pitcher_hand_cache(lookup: dict[int, dict[str, dict]], out_dir: Path, season: int) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"savant-pitcher-hand-{season}.json"
    payload = {
        "season": season,
        "source": "savant-pitcher-hand-statcast-search",
        "pitchers": len(lookup),
        "lookup": {str(k): v for k, v in lookup.items()},
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out_path


def fetch_pitcher_statcast_lookup(season: int) -> dict[int, dict]:
    """player_id -> Savant pitcher season profile."""
    custom_rows = _fetch_csv(SAVANT_PITCHER_CUSTOM_CSV.format(season=season))
    expected_rows = _fetch_csv(SAVANT_PITCHER_EXPECTED_CSV.format(season=season))

    expected_by_id: dict[int, dict] = {}
    for row in expected_rows:
        pid = _int(row.get("player_id"))
        if pid:
            expected_by_id[pid] = _parse_expected_row(row)

    lookup: dict[int, dict] = {}
    for row in custom_rows:
        pid = _int(row.get("player_id"))
        if not pid:
            continue
        out: dict[str, Any] = {"source": "savant-pitcher"}
        for key, val in _parse_custom_row(row).items():
            if val is not None:
                out[key] = val
        for key, val in expected_by_id.get(pid, {}).items():
            if val is not None:
                out[key] = val
        if out.get("xera") is not None:
            out["sierra"] = out["xera"]
            out["sierraSource"] = "xera-proxy"
        lookup[pid] = out

    return lookup


def write_savant_pitcher_cache(lookup: dict[int, dict], out_dir: Path, season: int) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"savant-pitcher-{season}.json"
    payload = {
        "season": season,
        "source": "savant-pitcher-csv",
        "pitchers": len(lookup),
        "lookup": {str(k): v for k, v in lookup.items()},
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out_path
