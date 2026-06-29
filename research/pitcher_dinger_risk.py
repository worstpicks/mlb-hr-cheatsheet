#!/usr/bin/env python3
"""Pitcher Dinger Risk — slate-relative HR vulnerability score."""
from __future__ import annotations

from typing import Any

# Higher raw value = more HR-prone for most metrics. K% is inverted (contact = risk).
DINGER_RISK_WEIGHTS: dict[str, float] = {
    "hr9": 20.0,
    "barrelPct": 18.0,
    "hrFbPct": 15.0,
    "hardHitPct": 12.0,
    "fbPct": 10.0,
    "meatballPct": 10.0,
    "sweetSpotPct": 10.0,
    "kPct": 5.0,
}

INVERT_RISK_KEYS = frozenset({"kPct"})


def _stats_blob(pitcher: dict | None) -> dict:
    if not pitcher:
        return {}
    return dict(pitcher.get("stats") or {})


def collect_slate_pitchers(games: list[dict]) -> list[dict]:
    out: list[dict] = []
    for game in games:
        for side, key in (("away", "awayPitcher"), ("home", "homePitcher")):
            pitcher = game.get(key)
            if not pitcher or not pitcher.get("name"):
                continue
            out.append(
                {
                    "pitcher": pitcher,
                    "side": side,
                    "gamePk": game.get("gamePk"),
                    "matchup": game.get("matchup"),
                }
            )
    return out


def _percentile_rank(values: list[float], value: float, *, higher_is_riskier: bool) -> float:
    if not values:
        return 50.0
    if len(values) == 1:
        return 50.0
    sorted_vals = sorted(values)
    if higher_is_riskier:
        below = sum(1 for v in sorted_vals if v < value)
        equal = sum(1 for v in sorted_vals if v == value)
        return ((below + 0.5 * equal) / len(sorted_vals)) * 100.0
    above = sum(1 for v in sorted_vals if v > value)
    equal = sum(1 for v in sorted_vals if v == value)
    return ((above + 0.5 * equal) / len(sorted_vals)) * 100.0


def _metric_values(entries: list[dict], key: str) -> list[float]:
    vals: list[float] = []
    for entry in entries:
        stats = _stats_blob(entry["pitcher"])
        val = stats.get(key)
        if val is None:
            continue
        try:
            vals.append(float(val))
        except (TypeError, ValueError):
            continue
    return vals


def compute_dinger_risk_for_stats(stats: dict, metric_pools: dict[str, list[float]]) -> float | None:
    total_weight = 0.0
    weighted = 0.0
    for key, weight in DINGER_RISK_WEIGHTS.items():
        val = stats.get(key)
        if val is None:
            continue
        pool = metric_pools.get(key) or []
        if not pool:
            continue
        try:
            num = float(val)
        except (TypeError, ValueError):
            continue
        pct = _percentile_rank(pool, num, higher_is_riskier=key not in INVERT_RISK_KEYS)
        weighted += pct * weight
        total_weight += weight
    if total_weight <= 0:
        return None
    return round(weighted / total_weight, 1)


def _build_hand_metric_pools(
    entries: list[dict], hand_key: str, hand_lookup: dict[int, dict[str, dict]]
) -> tuple[list[tuple[dict, dict]], dict[str, list[float]]]:
    pairs: list[tuple[dict, dict]] = []
    metric_pools: dict[str, list[float]] = {key: [] for key in DINGER_RISK_WEIGHTS}
    for entry in entries:
        pitcher = entry["pitcher"]
        pid = pitcher.get("id")
        if not pid:
            continue
        split = (hand_lookup.get(int(pid)) or {}).get(hand_key) or {}
        if not split:
            continue
        merged = dict(split)
        main = _stats_blob(pitcher)
        if merged.get("hr9") is None and main.get("hr9") is not None:
            merged["hr9"] = main["hr9"]
        pairs.append((entry, merged))
        for key in DINGER_RISK_WEIGHTS:
            val = merged.get(key)
            if val is None:
                continue
            try:
                metric_pools[key].append(float(val))
            except (TypeError, ValueError):
                continue
    return pairs, metric_pools


def _attach_hand_dinger_from_savant(
    entries: list[dict], hand_lookup: dict[int, dict[str, dict]] | None
) -> None:
    if not hand_lookup:
        return
    for hand_key, stat_key in (("lhb", "dingerRiskLhbPct"), ("rhb", "dingerRiskRhbPct")):
        pairs, metric_pools = _build_hand_metric_pools(entries, hand_key, hand_lookup)
        if not pairs:
            continue
        for entry, hstats in pairs:
            stats = _stats_blob(entry["pitcher"])
            if stats.get(stat_key) is not None:
                continue
            score = compute_dinger_risk_for_stats(hstats, metric_pools)
            if score is None:
                continue
            stats[stat_key] = int(round(score))
            stats[f"{stat_key}Source"] = "savant-hand"
            entry["pitcher"]["stats"] = stats


def attach_dinger_risk_to_games(
    games: list[dict], *, hand_lookup: dict[int, dict[str, dict]] | None = None
) -> None:
    entries = collect_slate_pitchers(games)
    if not entries:
        return

    metric_pools = {key: _metric_values(entries, key) for key in DINGER_RISK_WEIGHTS}
    lhb_pool = _metric_values(entries, "vsLhb")
    rhb_pool = _metric_values(entries, "vsRhb")

    ranked: list[tuple[float, dict]] = []
    for entry in entries:
        pitcher = entry["pitcher"]
        stats = _stats_blob(pitcher)
        score = compute_dinger_risk_for_stats(stats, metric_pools)
        if score is not None:
            stats["dingerRisk"] = score
            stats["dingerRiskPct"] = int(round(score))
        if stats.get("vsLhb") is not None and lhb_pool:
            try:
                stats["dingerRiskLhbPct"] = int(
                    round(_percentile_rank(lhb_pool, float(stats["vsLhb"]), higher_is_riskier=True))
                )
                stats["dingerRiskLhbPctSource"] = "propfinder"
            except (TypeError, ValueError):
                pass
        if stats.get("vsRhb") is not None and rhb_pool:
            try:
                stats["dingerRiskRhbPct"] = int(
                    round(_percentile_rank(rhb_pool, float(stats["vsRhb"]), higher_is_riskier=True))
                )
                stats["dingerRiskRhbPctSource"] = "propfinder"
            except (TypeError, ValueError):
                pass
        pitcher["stats"] = stats
        if score is not None:
            ranked.append((score, pitcher))

    _attach_hand_dinger_from_savant(entries, hand_lookup)

    ranked.sort(key=lambda item: item[0], reverse=True)
    for idx, (score, pitcher) in enumerate(ranked, start=1):
        stats = _stats_blob(pitcher)
        stats["dingerRiskRank"] = idx
        stats["dingerRiskSlateSize"] = len(ranked)
        pitcher["stats"] = stats
