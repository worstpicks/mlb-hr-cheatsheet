#!/usr/bin/env python3
"""HR Goblin + Straights ranking — zone fit first, HR power form second.

Canonical rubric for Straights of the Day, 3-leg / 2-leg / Favorite HR parlays,
Top 5 HR Tickets, Weather Heavy, and longshots. Patch scripts import from here
(see .cursor/rules/mlb-hr-slate-workflow.mdc).
"""
from __future__ import annotations

from typing import Callable


def zone_hr_fit(row: dict) -> float:
    """Pitch-zone fit tuned for homeruns (zone_hr, barrel, hard-hit in zone)."""
    zone_score = row.get("zone_score") or 0.0
    zone_hr = row.get("zone_hr")
    zone_barrel = row.get("zone_barrel")
    zone_hard_hit = row.get("zone_hard_hit")

    fit = zone_score * 1.65
    if zone_hr is not None:
        fit += max(zone_hr - 8.0, 0.0) * 0.90
    if zone_barrel is not None:
        fit += max(zone_barrel - 10.0, 0.0) * 0.58
    if zone_hard_hit is not None:
        fit += max(zone_hard_hit - 14.0, 0.0) * 0.38
    return fit


def hr_power_form(row: dict) -> float:
    """Secondary: recent HR / near-HR, EV, barrels."""
    form = (row.get("hr") or 0) * 2.8 + (row.get("near") or 0) * 1.6
    form += max((row.get("ev") or 0.0) - 90.0, 0.0) * 0.55
    form += (row.get("barrel") or 0.0) / 5.0
    return form


def _park(row: dict, park_pct_fn: Callable[[dict], int] | None) -> int:
    if park_pct_fn is not None:
        return int(park_pct_fn(row))
    return int(row.get("park_pct") or 0)


def straight_attack_rank(row: dict, *, park_pct_fn: Callable[[dict], int] | None = None) -> float:
    """O0.5 straight, Goblin HR legs, longshots — zone fit leads."""
    park = _park(row, park_pct_fn)
    zone_fit = zone_hr_fit(row)
    power = hr_power_form(row)
    matchup = (
        max(row.get("risk") or 0.0, 0.0) * 10.0
        + max(row.get("split") or 0.0, 0.0) * 8.0
        + park * 0.55
    )
    return zone_fit + power * 0.62 + matchup + (row.get("score") or 0) * 0.14


def multi_hr_rank(row: dict, *, park_pct_fn: Callable[[dict], int] | None = None) -> float:
    """O1.5 straight — multi-HR profile with zone-fit lead."""
    park = _park(row, park_pct_fn)
    zone_fit = zone_hr_fit(row)
    power = hr_power_form(row)
    return (
        zone_fit * 1.12
        + power * 0.95
        + max(row.get("split") or 0.0, 0.0) * 6.5
        + max(row.get("risk") or 0.0, 0.0) * 5.0
        + park * 0.38
        + (row.get("score") or 0) * 0.12
    )


def summary_combined_rank(
    row: dict,
    *,
    park_pct_fn: Callable[[dict], int] | None = None,
    attack_bonus: float = 0.0,
) -> float:
    """Top 5 HR Tickets combined rank."""
    park = _park(row, park_pct_fn)
    zone_fit = zone_hr_fit(row)
    power = hr_power_form(row)
    matchup = (
        max(row.get("risk") or 0.0, 0.0) * 9.0
        + max(row.get("split") or 0.0, 0.0) * 7.5
        + park * 0.52
    )
    return zone_fit * 1.05 + power * 0.58 + matchup + attack_bonus + (row.get("score") or 0) * 0.12


def weather_play_rank(row: dict, *, park_pct_fn: Callable[[dict], int] | None = None) -> float:
    """Weather-heavy HR plays — park-led with zone fit as tiebreaker."""
    park = _park(row, park_pct_fn)
    zone_fit = zone_hr_fit(row)
    power = hr_power_form(row)
    return (
        park * 1.85
        + zone_fit * 0.55
        + max(row.get("split") or 0.0, 0.0) * 16.0
        + max(row.get("risk") or 0.0, 0.0) * 8.0
        + power * 0.45
        + (row.get("score") or 0) * 0.28
    )


def hr_rank_sort_key(row: dict) -> tuple:
    """Default Goblin / straight sort tuple (rank, zone fit, board rank, score)."""
    return (
        row.get("straight_attack_rank") or 0.0,
        row.get("hr_zone_fit") or 0.0,
        row.get("rank") or 0,
        row.get("score") or 0,
    )


def annotate_hr_zone_ranks(
    rows: list[dict],
    *,
    park_pct_fn: Callable[[dict], int] | None = None,
) -> None:
    for row in rows:
        row["hr_zone_fit"] = zone_hr_fit(row)
        row["straight_attack_rank"] = straight_attack_rank(row, park_pct_fn=park_pct_fn)
        row["multi_hr_rank"] = multi_hr_rank(row, park_pct_fn=park_pct_fn)


def o05_zone_lane_ok(row: dict) -> bool:
    """O0.5 strict pool: usable zone fit or loud HR form."""
    zone = row.get("zone_score") or 0.0
    zone_hr = row.get("zone_hr") or 0.0
    if zone >= 12.0 or zone_hr >= 10.0:
        return True
    if zone >= 8.0 and (row.get("zone_barrel") or 0.0) >= 14.0:
        return True
    return row.get("hr", 0) >= 2 and row.get("near", 0) >= 3
