#!/usr/bin/env python3
"""MLB Stats API hitting splits for a rolling date window."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import date, timedelta
from typing import Any

MLB_API = "https://statsapi.mlb.com/api/v1"


def _float(val: Any) -> float | None:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _int(val: Any) -> int | None:
    if val is None or val == "":
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _iso(stat: dict) -> float | None:
    slg = _float(stat.get("slg"))
    avg = _float(stat.get("avg"))
    if slg is not None and avg is not None:
        return round(slg - avg, 3)
    return None


def _pct(num: Any, den: Any) -> float | None:
    n, d = _int(num), _int(den)
    if n is None or d is None or d == 0:
        return None
    return round(100.0 * n / d, 1)


def _get(path_query: str, timeout: int = 30) -> dict:
    url = f"{MLB_API}{path_query}"
    req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz-Research/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def window_bounds(sheet_date: str, days: int = 30) -> tuple[str, str]:
    end = date.fromisoformat(sheet_date)
    start = end - timedelta(days=days)
    return start.isoformat(), sheet_date


def _parse_mlb_stat(stat: dict, *, source: str) -> dict:
    avg = _float(stat.get("avg"))
    slg = _float(stat.get("slg"))
    pa = _int(stat.get("plateAppearances"))
    return {
        "hr": _int(stat.get("homeRuns")),
        "hits": _int(stat.get("hits")),
        "ab": _int(stat.get("atBats")),
        "pa": pa,
        "avg": avg,
        "obp": _float(stat.get("obp")),
        "slg": slg,
        "iso": _iso(stat),
        "kPct": _pct(stat.get("strikeOuts"), pa),
        "bbPct": _pct(stat.get("baseOnBalls"), pa),
        "source": source,
    }


def _parse_window_stat(stat: dict) -> dict:
    return _parse_mlb_stat(stat, source="mlb-window")


def fetch_last_games_stats_batch(
    player_ids: list[int],
    season: int,
    games: int,
    *,
    chunk_size: int = 25,
) -> dict[int, dict]:
    """player_id -> last-N-games hitting stats via MLB lastXGames hydrate."""
    lookup: dict[int, dict] = {}
    unique = sorted({int(x) for x in player_ids if x})
    hydrate = urllib.parse.quote(
        f"stats(group=[hitting],type=[lastXGames],season={season},limit={games})"
    )
    for i in range(0, len(unique), chunk_size):
        chunk = unique[i : i + chunk_size]
        ids_str = ",".join(str(x) for x in chunk)
        try:
            data = _get(f"/people?personIds={ids_str}&hydrate={hydrate}", timeout=60)
        except Exception:
            continue
        for person in data.get("people") or []:
            pid = _int(person.get("id"))
            if not pid:
                continue
            for group in person.get("stats") or []:
                splits = group.get("splits") or []
                if not splits:
                    continue
                stat = splits[0].get("stat") or {}
                if stat:
                    lookup[pid] = _parse_mlb_stat(stat, source=f"mlb-last{games}g")
                    break
    return lookup


def fetch_window_stats_batch(
    player_ids: list[int],
    start: str,
    end: str,
    season: int,
    *,
    chunk_size: int = 25,
) -> dict[int, dict]:
    """player_id -> last-N-days hitting stats via MLB byDateRange hydrate."""
    lookup: dict[int, dict] = {}
    unique = sorted({int(x) for x in player_ids if x})
    hydrate = urllib.parse.quote(
        f"stats(group=[hitting],type=[byDateRange],startDate={start},endDate={end},season={season})"
    )
    for i in range(0, len(unique), chunk_size):
        chunk = unique[i : i + chunk_size]
        ids_str = ",".join(str(x) for x in chunk)
        try:
            data = _get(f"/people?personIds={ids_str}&hydrate={hydrate}", timeout=60)
        except Exception:
            continue
        for person in data.get("people") or []:
            pid = _int(person.get("id"))
            if not pid:
                continue
            for group in person.get("stats") or []:
                splits = group.get("splits") or []
                if not splits:
                    continue
                stat = splits[0].get("stat") or {}
                if stat:
                    lookup[pid] = _parse_window_stat(stat)
                    break
    return lookup
