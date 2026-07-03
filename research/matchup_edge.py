#!/usr/bin/env python3
"""Savant matchup edge — today's pitch-mix fit + batter vs pitcher Statcast history."""
from __future__ import annotations

import csv
import io
import urllib.request
from typing import Any

SAVANT_MATCHUP_SEARCH = (
    "https://baseballsavant.mlb.com/statcast_search/csv?all=true&player_type=batter"
    "&hfGT=R%7C&min_pitches=0&min_results=1"
    "&group_by=name&sort_col=pitches&sort_order=desc"
    "&batters_lookup%5B%5D={batter_id}&pitchers_lookup%5B%5D={pitcher_id}"
)

# History (batter vs pitcher career) is noisy at small samples, so it needs a
# real sample before it counts and never outweighs today's pitch-mix fit.
MATCHUP_EDGE_CAP = 25.0
MIN_HISTORY_PITCHES = 20
HISTORY_CONF_PITCHES = 90.0
MATCHUP_BLEND = 0.70
HISTORY_BLEND = 0.30


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


def matchup_pair_key(batter_id: int | str, pitcher_id: int | str) -> str:
    return f"{int(batter_id)}|{int(pitcher_id)}"


def _fetch_csv(url: str, timeout: int = 75) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz-Research/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode("utf-8-sig")
    if not text.strip() or text.lstrip().startswith("<!"):
        return []
    return list(csv.DictReader(io.StringIO(text)))


def parse_savant_matchup_row(row: dict) -> dict:
    whiff = _float(row.get("whiff_percent"))
    if whiff is None:
        whiff = _float(row.get("swing_miss_percent"))
    return {
        "pitches": _int(row.get("pitches")) or 0,
        "pa": _int(row.get("pa")),
        "xwoba": _float(row.get("xwoba")),
        "woba": _float(row.get("woba")),
        "whiffPct": whiff,
        "barrelPct": _float(row.get("barrel_batted_rate")) or _float(row.get("barrels_per_pa_percent")),
        "avgEV": _float(row.get("exit_velocity_avg")),
    }


def fetch_savant_matchup(batter_id: int, pitcher_id: int) -> dict | None:
    """Career Statcast profile for batter vs specific pitcher (Savant search)."""
    if not batter_id or not pitcher_id:
        return None
    url = SAVANT_MATCHUP_SEARCH.format(batter_id=int(batter_id), pitcher_id=int(pitcher_id))
    rows = _fetch_csv(url)
    if not rows:
        return None
    entry = parse_savant_matchup_row(rows[0])
    entry["source"] = "savant-matchup"
    return entry


def score_matchup_edge(
    season_stats: dict | None,
    *,
    mix_xwoba: float | None = None,
    history: dict | None = None,
    min_history_pitches: int = MIN_HISTORY_PITCHES,
) -> dict | None:
    """Edge% from Savant today's mix xwOBA + career matchup vs this SP."""
    season_stats = season_stats or {}
    season_xwoba = _float(season_stats.get("xwoba"))
    if season_xwoba is None:
        season_xwoba = 0.320

    matchup_edge = None
    if mix_xwoba is not None:
        matchup_edge = round((mix_xwoba - season_xwoba) * 1000) / 10

    history_edge = None
    pitches = 0
    hist_xwoba = None
    whiff = None
    if history:
        pitches = int(history.get("pitches") or 0)
        hist_xwoba = _float(history.get("xwoba"))
        whiff = _float(history.get("whiffPct"))
        if pitches >= min_history_pitches and hist_xwoba is not None:
            conf = min(pitches / HISTORY_CONF_PITCHES, 1.0)
            history_edge = round((hist_xwoba - season_xwoba) * 100 * conf * 10) / 10

    if matchup_edge is not None and history_edge is not None:
        mix_edge = round((matchup_edge * MATCHUP_BLEND + history_edge * HISTORY_BLEND) * 10) / 10
    elif matchup_edge is not None:
        mix_edge = matchup_edge
    elif history_edge is not None:
        mix_edge = history_edge
    else:
        return None

    mix_edge = max(-MATCHUP_EDGE_CAP, min(MATCHUP_EDGE_CAP, mix_edge))

    out: dict[str, Any] = {
        "mixEdge": mix_edge,
        "edgeSource": "savant-matchup",
    }
    if matchup_edge is not None:
        out["matchupEdge"] = matchup_edge
    if history_edge is not None:
        out["historyEdge"] = history_edge
    if pitches:
        out["matchPitches"] = pitches
    if hist_xwoba is not None:
        out["matchXwoba"] = round(hist_xwoba, 3)
    if whiff is not None:
        out["matchWhiffPct"] = whiff
    return out


def apply_matchup_edge_to_row(
    row: dict,
    opposing_pitcher: dict | None,
    history_lookup: dict[str, dict] | None = None,
) -> dict:
    enriched = dict(row)
    stats = dict(enriched.get("stats") or {})
    batter_id = enriched.get("id")
    pitcher_id = (opposing_pitcher or {}).get("id")
    mix_xwoba = _float(stats.get("mixXwoba"))

    history = None
    if history_lookup and batter_id and pitcher_id:
        history = history_lookup.get(matchup_pair_key(batter_id, pitcher_id))

    scored = score_matchup_edge(stats, mix_xwoba=mix_xwoba, history=history)
    if scored:
        stats.update(scored)
    else:
        for key in (
            "mixEdge",
            "matchupEdge",
            "historyEdge",
            "matchPitches",
            "matchXwoba",
            "matchWhiffPct",
            "edgeSource",
            "bvpKPct",
            "bvpAb",
            "bvpHr",
            "bvpIso",
            "bvpSlg",
            "bvpAvg",
            "bvpObp",
            "bvpSource",
        ):
            stats.pop(key, None)
        if mix_xwoba is not None and stats.get("xwoba") is not None:
            edge = round((mix_xwoba - float(stats["xwoba"])) * 1000) / 10
            stats["mixEdge"] = max(-MATCHUP_EDGE_CAP, min(MATCHUP_EDGE_CAP, edge))
            stats["edgeSource"] = "savant-matchup"

    if history and history.get("whiffPct") is not None:
        stats["matchWhiffPct"] = history["whiffPct"]
        stats["bvpKPct"] = history["whiffPct"]

    enriched["stats"] = stats
    return enriched


def apply_matchup_edge_to_lineup(
    lineup: list[dict],
    opposing_pitcher: dict | None,
    history_lookup: dict[str, dict] | None = None,
) -> list[dict]:
    return [
        apply_matchup_edge_to_row(row, opposing_pitcher, history_lookup)
        for row in lineup or []
    ]
