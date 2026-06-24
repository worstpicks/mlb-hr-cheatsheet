#!/usr/bin/env python3
"""Pitcher arsenal + batter vs pitch-type matchup scoring (Savant CSV)."""
from __future__ import annotations

import csv
import io
import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

PITCH_TYPES = ("FF", "SL", "CH", "CU", "SI", "FC", "ST", "FS", "KC", "SV")

PITCH_LABELS = {
    "FF": "4-seam",
    "SI": "sinker",
    "FC": "cutter",
    "SL": "slider",
    "CH": "changeup",
    "CU": "curve",
    "KC": "knuckle-curve",
    "ST": "sweeper",
    "FS": "splitter",
    "SV": "slurve",
}

SAVANT_PITCHER_ARSENAL_CSV = (
    "https://baseballsavant.mlb.com/leaderboard/pitch-arsenal-stats"
    "?year={season}&min=10&csv=true"
)

SAVANT_BATTER_PITCH_SEARCH = (
    "https://baseballsavant.mlb.com/statcast_search/csv?all=true&player_type=batter"
    "&hfSea={season}%7C&hfGT=R%7C&min_pitches=0&min_results=10"
    "&group_by=name&sort_col=pitches&sort_order=desc&hfPT={pitch}%7C"
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


def _fetch_csv(url: str, timeout: int = 90) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz-Research/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode("utf-8-sig")
    if not text.strip():
        return []
    return list(csv.DictReader(io.StringIO(text)))


def _parse_batter_pitch_row(row: dict) -> dict:
    whiff = _float(row.get("whiff_percent"))
    if whiff is None:
        whiff = _float(row.get("swing_miss_percent"))
    return {
        "pitches": _int(row.get("pitches")),
        "woba": _float(row.get("woba")),
        "xwoba": _float(row.get("xwoba")),
        "whiffPct": whiff,
        "barrelPct": _float(row.get("barrels_per_pa_percent")),
    }


def fetch_pitcher_arsenal_lookup(season: int) -> dict[int, dict[str, float]]:
    """player_id -> {FF: 45.4, SL: 17.7, ...} usage percent."""
    rows = _fetch_csv(SAVANT_PITCHER_ARSENAL_CSV.format(season=season))
    lookup: dict[int, dict[str, float]] = {}
    for row in rows:
        pid = _int(row.get("player_id"))
        pt = (row.get("pitch_type") or "").strip().upper()
        usage = _float(row.get("pitch_usage"))
        if not pid or not pt or usage is None or usage <= 0:
            continue
        bucket = lookup.setdefault(pid, {})
        bucket[pt] = round(usage, 1)
    return lookup


def fetch_batter_pitch_type_lookup(season: int) -> dict[int, dict[str, dict]]:
    """player_id -> pitch_type -> {xwoba, woba, pitches, ...}."""
    lookup: dict[int, dict[str, dict]] = {}
    for pitch in PITCH_TYPES:
        url = SAVANT_BATTER_PITCH_SEARCH.format(season=season, pitch=urllib.parse.quote(pitch))
        rows = _fetch_csv(url)
        for row in rows:
            pid = _int(row.get("player_id"))
            if not pid:
                continue
            parsed = _parse_batter_pitch_row(row)
            if parsed.get("pitches") is None:
                continue
            lookup.setdefault(pid, {})[pitch] = parsed
    return lookup


def league_pitch_averages(batter_pitch_lookup: dict[int, dict[str, dict]]) -> dict[str, dict]:
    """League-average batter performance vs each pitch type (xwOBA-weighted by pitches seen)."""
    totals: dict[str, dict[str, float]] = {pt: {"pitches": 0.0, "xwoba_w": 0.0, "woba_w": 0.0} for pt in PITCH_TYPES}
    for profile in batter_pitch_lookup.values():
        for pt, stats in profile.items():
            pitches = stats.get("pitches") or 0
            if pitches <= 0:
                continue
            bucket = totals.setdefault(pt, {"pitches": 0.0, "xwoba_w": 0.0, "woba_w": 0.0})
            w = float(pitches)
            bucket["pitches"] += w
            if stats.get("xwoba") is not None:
                bucket["xwoba_w"] += w * stats["xwoba"]
            if stats.get("woba") is not None:
                bucket["woba_w"] += w * stats["woba"]
    out: dict[str, dict] = {}
    for pt, bucket in totals.items():
        if bucket["pitches"] <= 0:
            continue
        out[pt] = {
            "xwoba": round(bucket["xwoba_w"] / bucket["pitches"], 3) if bucket["xwoba_w"] else None,
            "woba": round(bucket["woba_w"] / bucket["pitches"], 3) if bucket["woba_w"] else None,
            "pitches": int(bucket["pitches"]),
        }
    return out


def normalize_arsenal(raw: dict[str, float] | None, min_usage: float = 5.0) -> dict[str, float]:
    if not raw:
        return {}
    return {pt: usage for pt, usage in raw.items() if usage is not None and usage >= min_usage}


def score_batter_vs_arsenal(
    batter_id: int,
    arsenal: dict[str, float] | None,
    batter_pitch: dict[str, dict] | None,
    batter_overall_xwoba: float | None,
    league_avgs: dict[str, dict],
    *,
    min_pitch_pa: int = 15,
) -> dict | None:
    """Weighted batter xwOBA vs opposing pitcher's mix."""
    mix = normalize_arsenal(arsenal)
    if not mix or not batter_id:
        return None

    batter_pitch = batter_pitch or {}
    baseline = batter_overall_xwoba
    if baseline is None:
        baseline = 0.320

    total_w = 0.0
    weighted_xwoba = 0.0
    weighted_league = 0.0
    edges: list[tuple[str, float, float]] = []

    for pt, usage_pct in mix.items():
        w = usage_pct / 100.0
        b_stats = batter_pitch.get(pt) or {}
        pitches_seen = b_stats.get("pitches") or 0
        xw = b_stats.get("xwoba")
        if xw is None or pitches_seen < min_pitch_pa:
            xw = baseline
        lg_xw = (league_avgs.get(pt) or {}).get("xwoba") or baseline

        weighted_xwoba += w * xw
        weighted_league += w * lg_xw
        total_w += w
        edges.append((pt, xw - lg_xw, usage_pct))

    if total_w <= 0:
        return None

    weighted_xwoba /= total_w
    weighted_league /= total_w
    mix_plus = round((weighted_xwoba - weighted_league) * 1000) / 10
    mix_edge = round((weighted_xwoba - baseline) * 1000) / 10

    edges.sort(key=lambda x: x[1] * x[2], reverse=True)
    best_pt = edges[0][0] if edges else None
    worst_pt = min(edges, key=lambda x: x[1] * x[2])[0] if edges else None

    return {
        "mixPlus": mix_plus,
        "mixEdge": mix_edge,
        "mixXwoba": round(weighted_xwoba, 3),
        "mixBest": best_pt,
        "mixWorst": worst_pt,
        "mixPitches": len(mix),
    }


def attach_pitcher_arsenal(
    pitcher: dict | None,
    arsenal_lookup: dict[int, dict[str, float]],
    *,
    prior_lookup: dict[int, dict[str, float]] | None = None,
    season: int | None = None,
) -> dict | None:
    if not pitcher:
        return pitcher
    out = dict(pitcher)
    pid = int(out.get("id") or 0)
    arsenal = normalize_arsenal(arsenal_lookup.get(pid))
    arsenal_season = season
    if not arsenal and prior_lookup:
        arsenal = normalize_arsenal(prior_lookup.get(pid))
        if arsenal and season:
            arsenal_season = season - 1
    if arsenal:
        out["arsenal"] = arsenal
        top = sorted(arsenal.items(), key=lambda x: -x[1])[:4]
        label = " · ".join(f"{pt} {usage:.0f}%" for pt, usage in top)
        if arsenal_season and season and arsenal_season < season:
            label += f" ({arsenal_season} mix)"
        out["arsenalLabel"] = label
        if arsenal_season is not None:
            out["arsenalSeason"] = arsenal_season
    return out


def enrich_hitter_pitch_mix(
    row: dict,
    opposing_pitcher: dict | None,
    batter_pitch_lookup: dict[int, dict[str, dict]],
    league_avgs: dict[str, dict],
    savant_lookup: dict[int, dict],
) -> dict:
    enriched = dict(row)
    stats = dict(enriched.get("stats") or {})
    pid = int(enriched.get("id") or 0)
    pitcher = opposing_pitcher or {}
    batter_pitch = batter_pitch_lookup.get(pid) if pid else None
    overall_xwoba = (savant_lookup.get(pid) or stats).get("xwoba")
    mix = score_batter_vs_arsenal(
        pid,
        pitcher.get("arsenal"),
        batter_pitch,
        overall_xwoba,
        league_avgs,
    )
    if mix:
        stats.update(mix)
    enriched["stats"] = stats
    return enriched


def enrich_lineup_pitch_mix(
    lineup: list[dict],
    opposing_pitcher: dict | None,
    *,
    batter_pitch_lookup: dict[int, dict[str, dict]],
    league_avgs: dict[str, dict],
    savant_lookup: dict[int, dict],
) -> list[dict]:
    return [
        enrich_hitter_pitch_mix(
            row,
            opposing_pitcher,
            batter_pitch_lookup,
            league_avgs,
            savant_lookup,
        )
        for row in lineup
    ]


def write_pitch_mix_cache(
    pitcher_lookup: dict[int, dict[str, float]],
    batter_lookup: dict[int, dict[str, dict]],
    league_avgs: dict[str, dict],
    out_dir: Path,
    season: int,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    arsenal_path = out_dir / f"savant-pitcher-arsenal-{season}.json"
    batter_path = out_dir / f"savant-batter-pitch-type-{season}.json"
    arsenal_path.write_text(
        json.dumps(
            {
                "season": season,
                "source": "savant-pitch-arsenal-stats",
                "pitchers": len(pitcher_lookup),
                "lookup": {str(k): v for k, v in pitcher_lookup.items()},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    batter_path.write_text(
        json.dumps(
            {
                "season": season,
                "source": "savant-statcast-search",
                "batters": len(batter_lookup),
                "leagueAvgs": league_avgs,
                "lookup": {str(k): v for k, v in batter_lookup.items()},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return arsenal_path, batter_path
