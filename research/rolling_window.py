#!/usr/bin/env python3
"""Rolling Savant + MLB windows for MLB Research (last N games / starts)."""
from __future__ import annotations

import csv
import io
import json
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

MLB_API = "https://statsapi.mlb.com/api/v1"

HITTER_ROLLING_GAMES = 20
PITCHER_ROLLING_STARTS = 10

SAVANT_BATTER_SEARCH = (
    "https://baseballsavant.mlb.com/statcast_search/csv?all=true&player_type=batter"
    "&hfSea={season}%7C&hfGT=R%7C&min_pitches=0&min_results=1"
    "&group_by=name&sort_col=pitches&sort_order=desc"
    "&batters_lookup%5B%5D={player_id}&game_date_gt={start}&game_date_lt={end}"
)

SAVANT_PITCHER_SEARCH = (
    "https://baseballsavant.mlb.com/statcast_search/csv?all=true&player_type=pitcher"
    "&hfSea={season}%7C&hfGT=R%7C&min_pitches=0&min_results=10"
    "&group_by=name&sort_col=pitches&sort_order=desc"
    "&pitchers_lookup%5B%5D={player_id}&game_date_gt={start}&game_date_lt={end}"
)


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


def _pct(num: Any, den: Any) -> float | None:
    n, d = _int(num), _int(den)
    if n is None or d is None or d == 0:
        return None
    return round(100.0 * n / d, 1)


def _fetch_json(url: str, timeout: int = 45) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz-Research/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_csv(url: str, timeout: int = 75) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz-Research/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode("utf-8-sig")
    if not text.strip() or text.lstrip().startswith("<!"):
        return []
    return list(csv.DictReader(io.StringIO(text)))


def _parse_ip(ip_str: str | None) -> float | None:
    if not ip_str or str(ip_str).strip() in ("-", "0.0", "0"):
        return None
    try:
        parts = str(ip_str).strip().split(".")
        whole = int(parts[0]) if parts[0] else 0
        frac = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        return round(whole + frac / 3.0, 2)
    except ValueError:
        return _float(ip_str)


def _hitter_game_dates(player_id: int, season: int, games: int) -> tuple[str, str] | None:
    url = f"{MLB_API}/people/{player_id}/stats?stats=gameLog&group=hitting&season={season}"
    try:
        payload = _fetch_json(url)
    except Exception:
        return None
    splits = (payload.get("stats") or [{}])[0].get("splits") or []
    if not splits:
        return None
    tail = splits[-games:] if len(splits) > games else splits
    dates = sorted((s.get("date") or "")[:10] for s in tail if s.get("date"))
    if not dates:
        return None
    return dates[0], dates[-1]


def _pitcher_start_dates(player_id: int, season: int, starts: int) -> tuple[str, str] | None:
    url = f"{MLB_API}/people/{player_id}/stats?stats=gameLog&group=pitching&season={season}"
    try:
        payload = _fetch_json(url)
    except Exception:
        return None
    splits = (payload.get("stats") or [{}])[0].get("splits") or []
    start_splits = []
    for split in splits:
        st = split.get("stat") or {}
        if _parse_ip(st.get("inningsPitched")):
            start_splits.append(split)
    if not start_splits:
        return None
    tail = start_splits[-starts:] if len(start_splits) > starts else start_splits
    dates = sorted((s.get("date") or "")[:10] for s in tail if s.get("date"))
    if not dates:
        return None
    return dates[0], dates[-1]


def merge_rolling_over_season(rolling: dict | None, season: dict | None) -> dict | None:
    """Overlay rolling-window Savant on season profile; keep season-only tracker fields."""
    if not rolling:
        return season
    out = dict(season or {})
    season_only = (
        "expectedHr",
        "hrLuckDiff",
        "mostlyGone",
        "nearHr",
        "noDoubters",
        "doubters",
        "hrTrackerSource",
        "propfinderNearHr",
        "nearHrSource",
        "blastPct",
        "solidContactPct",
        "batSpeed",
        "swingStrength",
        "mixPlus",
        "mixEdge",
        "mixXwoba",
        "mixBest",
        "mixWorst",
        "mixPitches",
    )
    for key, val in rolling.items():
        if val is not None:
            out[key] = val
    for key in season_only:
        if season and season.get(key) is not None:
            out[key] = season[key]
    out["source"] = rolling.get("source", out.get("source", "savant-rolling"))
    return out


def _pitcher_start_ip(player_id: int, season: int, starts: int) -> float | None:
    url = f"{MLB_API}/people/{player_id}/stats?stats=gameLog&group=pitching&season={season}"
    try:
        payload = _fetch_json(url)
    except Exception:
        return None
    splits = (payload.get("stats") or [{}])[0].get("splits") or []
    start_ips: list[float] = []
    for split in splits:
        ip = _parse_ip((split.get("stat") or {}).get("inningsPitched"))
        if ip:
            start_ips.append(ip)
    if not start_ips:
        return None
    tail = start_ips[-starts:] if len(start_ips) > starts else start_ips
    return round(sum(tail), 1)


def _parse_batter_rolling_row(row: dict, *, games: int) -> dict:
    ba = _float(row.get("ba"))
    slg = _float(row.get("slg"))
    pa = _int(row.get("pa"))
    bip = _int(row.get("bip"))
    iso = _float(row.get("iso"))
    if iso is None and ba is not None and slg is not None:
        iso = round(slg - ba, 3)
    fb = _float(row.get("flyballs_percent"))
    ld = _float(row.get("linedrives_percent"))
    air = None
    if fb is not None and ld is not None:
        air = round(fb + ld, 1)
    out = {
        "source": f"savant-last{games}g",
        "statWindow": f"last{games}g",
        "pa": pa,
        "hr": _int(row.get("hrs")),
        "avg": ba,
        "slg": slg,
        "iso": iso,
        "xwoba": _float(row.get("xwoba")),
        "barrelPct": _float(row.get("barrels_per_bbe_percent")) or _float(row.get("barrels_per_pa_percent")),
        "hardHitPct": _float(row.get("hardhit_percent")),
        "avgEV": _float(row.get("launch_speed")),
        "launchAngle": _float(row.get("launch_angle")),
        "sweetSpotPct": _float(row.get("sweet_spot_percent")),
        "fbPct": fb,
        "gbPct": _float(row.get("groundballs_percent")),
        "ldPct": ld,
        "airPct": air,
        "whiffPct": _float(row.get("swing_miss_percent")),
        "kPct": _float(row.get("k_percent")),
        "bip": bip,
        "bipPct": _pct(bip, pa),
        "pullPct": _float(row.get("pull_percent")),
    }
    hr_fb = None
    hrs = _int(row.get("hrs"))
    if hrs is not None and bip and bip > 0 and fb is not None:
        est_fb = round(bip * fb / 100.0)
        if est_fb > 0:
            hr_fb = round(100.0 * hrs / est_fb, 1)
    if hr_fb is not None:
        out["hrFbPct"] = hr_fb
    return {k: v for k, v in out.items() if v is not None}


def _parse_pitcher_rolling_row(row: dict, *, starts: int, ip: float | None = None) -> dict:
    pa = _int(row.get("pa"))
    hrs = _int(row.get("hrs"))
    bip = _int(row.get("bip"))
    hr9 = None
    if hrs is not None and ip and ip > 0:
        hr9 = round((hrs / ip) * 9.0, 2)
    elif hrs is not None and pa and pa > 0:
        hr9 = round((hrs / pa) * 27.0, 2)
    fb_pct = None
    fly_bip = _int(row.get("fly_balls")) or _int(row.get("flyballs"))
    if bip and fly_bip is not None and bip > 0:
        fb_pct = round(100.0 * fly_bip / bip, 1)
    hr_fb_pct = None
    if hrs is not None and fly_bip and fly_bip > 0:
        hr_fb_pct = round(100.0 * hrs / fly_bip, 1)
    return {
        k: v
        for k, v in {
            "source": f"savant-last{starts}st",
            "statWindow": f"last{starts}st",
            "pa": pa,
            "hrAllowed": hrs,
            "barrelPct": _float(row.get("barrels_per_bbe_percent")),
            "hardHitPct": _float(row.get("hardhit_percent")),
            "avgEV": _float(row.get("launch_speed")),
            "fbPct": fb_pct,
            "hrFbPct": hr_fb_pct,
            "kPct": _float(row.get("k_percent")),
            "whiffPct": _float(row.get("swing_miss_percent")),
            "zonePct": _float(row.get("zone_percent")),
            "edgePct": _float(row.get("edge_percent")),
            "hr9": hr9,
            "inningsPitched": ip,
            "ip": ip,
        }.items()
        if v is not None
    }


def fetch_rolling_batter_profile(player_id: int, season: int, games: int = HITTER_ROLLING_GAMES) -> dict | None:
    bounds = _hitter_game_dates(player_id, season, games)
    if not bounds:
        return None
    start, end = bounds
    url = SAVANT_BATTER_SEARCH.format(season=season, player_id=player_id, start=start, end=end)
    try:
        rows = _fetch_csv(url)
    except Exception:
        return None
    if not rows:
        return None
    parsed = _parse_batter_rolling_row(rows[0], games=games)
    parsed["windowStart"] = start
    parsed["windowEnd"] = end
    parsed["windowGames"] = games
    return parsed


def fetch_rolling_pitcher_profile(player_id: int, season: int, starts: int = PITCHER_ROLLING_STARTS) -> dict | None:
    bounds = _pitcher_start_dates(player_id, season, starts)
    if not bounds:
        return None
    start, end = bounds
    url = SAVANT_PITCHER_SEARCH.format(season=season, player_id=player_id, start=start, end=end)
    try:
        rows = _fetch_csv(url)
    except Exception:
        return None
    if not rows:
        return None
    ip = _pitcher_start_ip(player_id, season, starts)
    parsed = _parse_pitcher_rolling_row(rows[0], starts=starts, ip=ip)
    parsed["windowStart"] = start
    parsed["windowEnd"] = end
    parsed["windowStarts"] = starts
    return parsed


def _batch_lookup(
    player_ids: list[int],
    fetch_fn,
    *,
    max_workers: int = 8,
) -> dict[int, dict]:
    unique = sorted({int(x) for x in player_ids if x})
    if not unique:
        return {}
    lookup: dict[int, dict] = {}

    def work(pid: int) -> tuple[int, dict | None]:
        try:
            return pid, fetch_fn(pid)
        except Exception:
            return pid, None

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(work, pid) for pid in unique]
        for fut in as_completed(futures):
            pid, profile = fut.result()
            if profile:
                lookup[pid] = profile
    return lookup


def fetch_rolling_batter_lookup(
    player_ids: list[int],
    season: int,
    games: int = HITTER_ROLLING_GAMES,
    *,
    max_workers: int = 8,
) -> dict[int, dict]:
    return _batch_lookup(
        player_ids,
        lambda pid: fetch_rolling_batter_profile(pid, season, games),
        max_workers=max_workers,
    )


def fetch_rolling_pitcher_lookup(
    player_ids: list[int],
    season: int,
    starts: int = PITCHER_ROLLING_STARTS,
    *,
    max_workers: int = 8,
) -> dict[int, dict]:
    return _batch_lookup(
        player_ids,
        lambda pid: fetch_rolling_pitcher_profile(pid, season, starts),
        max_workers=max_workers,
    )
