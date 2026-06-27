#!/usr/bin/env python3
"""HR Goblin + Straights ranking — zone fit first, HR power form second.

Canonical rubric for Straights of the Day, 3-leg / 2-leg / Favorite HR parlays,
Top 5 HR Tickets, Weather Heavy, and longshots. Patch scripts import from here
(see .cursor/rules/mlb-hr-slate-workflow.mdc).
"""
from __future__ import annotations

import re
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


def _batter_hand(row: dict) -> str:
    hand = (row.get("hand") or "").strip().upper()
    if hand in ("L", "R", "S"):
        return hand
    m = re.search(r"\(([LRS])\)", row.get("name", ""))
    return m.group(1) if m else "R"


def has_hand_park_data(row: dict) -> bool:
    return row.get("park_lhb_pct") is not None or row.get("park_rhb_pct") is not None


def hand_park_pct(row: dict, *, park_pct_fn: Callable[[dict], int] | None = None) -> int:
    """Net HR park % for this batter's hand (Ballpark Pal stadium + PropFinder wx)."""
    if row.get("hand_park_pct") is not None:
        return int(row["hand_park_pct"])
    hand = _batter_hand(row)
    if hand == "L" and row.get("park_lhb_pct") is not None:
        return int(row["park_lhb_pct"])
    if hand in ("R", "S") and row.get("park_rhb_pct") is not None:
        return int(row["park_rhb_pct"])
    return _park(row, park_pct_fn)


def hand_park_nudge(row: dict, *, park_pct_fn: Callable[[dict], int] | None = None) -> float:
    """Small tiebreaker when per-hand park differs from game net park."""
    if not has_hand_park_data(row):
        return 0.0
    overall = float(_park(row, park_pct_fn))
    hand = float(hand_park_pct(row, park_pct_fn=park_pct_fn))
    delta = hand - overall
    if delta > 0:
        return min(delta * 0.38, 2.2)
    return max(delta * 0.22, -1.2)


def park_gate_pct(row: dict, *, park_pct_fn: Callable[[dict], int] | None = None) -> int:
    """Eligibility gates: lean on hand park only when it helps the batter."""
    overall = _park(row, park_pct_fn)
    if not has_hand_park_data(row):
        return overall
    hand = hand_park_pct(row, park_pct_fn=park_pct_fn)
    if hand > overall:
        return int(round(overall * 0.74 + hand * 0.26))
    return overall


def straight_attack_rank(row: dict, *, park_pct_fn: Callable[[dict], int] | None = None) -> float:
    """O0.5 straight, Goblin HR legs, longshots — zone fit leads."""
    park = _park(row, park_pct_fn)
    nudge = hand_park_nudge(row, park_pct_fn=park_pct_fn)
    zone_fit = zone_hr_fit(row)
    power = hr_power_form(row)
    matchup = (
        max(row.get("risk") or 0.0, 0.0) * 10.0
        + max(row.get("split") or 0.0, 0.0) * 8.0
        + park * 0.55
        + nudge * 1.05
    )
    return zone_fit + power * 0.62 + matchup + (row.get("score") or 0) * 0.14


def multi_hr_rank(row: dict, *, park_pct_fn: Callable[[dict], int] | None = None) -> float:
    """O1.5 straight — multi-HR profile with zone-fit lead."""
    park = _park(row, park_pct_fn)
    nudge = hand_park_nudge(row, park_pct_fn=park_pct_fn)
    zone_fit = zone_hr_fit(row)
    power = hr_power_form(row)
    return (
        zone_fit * 1.12
        + power * 0.95
        + max(row.get("split") or 0.0, 0.0) * 6.5
        + max(row.get("risk") or 0.0, 0.0) * 5.0
        + park * 0.38
        + nudge * 0.72
        + (row.get("score") or 0) * 0.12
    )


def top5_hr_ticket_rank(
    row: dict,
    *,
    park_pct_fn: Callable[[dict], int] | None = None,
) -> float:
    """Top 5 HR Tickets — Split, Risk, Park, Form, Zone (no board score)."""
    zone_fit = zone_hr_fit(row)
    form = hr_power_form(row)
    split = max(row.get("split") or 0.0, 0.0) * 12.0
    risk = max(row.get("risk") or 0.0, 0.0) * 14.0
    hand_park = float(hand_park_pct(row, park_pct_fn=park_pct_fn))
    overall = float(_park(row, park_pct_fn))
    park_signal = max(hand_park, overall, 0.0) * 0.65
    if hand_park < 0 or overall < 0:
        park_signal += min(hand_park, overall, 0.0) * 0.22
    return zone_fit * 1.0 + form * 0.85 + split + risk + park_signal


def summary_combined_rank(
    row: dict,
    *,
    park_pct_fn: Callable[[dict], int] | None = None,
    attack_bonus: float = 0.0,
) -> float:
    """Top 5 HR Tickets — alias for top5_hr_ticket_rank (attack_bonus ignored)."""
    _ = attack_bonus
    return top5_hr_ticket_rank(row, park_pct_fn=park_pct_fn)


def weather_play_rank(row: dict, *, park_pct_fn: Callable[[dict], int] | None = None) -> float:
    """Weather-heavy HR plays — park-led with zone fit as tiebreaker."""
    overall = _park(row, park_pct_fn)
    hand = float(hand_park_pct(row, park_pct_fn=park_pct_fn))
    if has_hand_park_data(row):
        park_signal = overall * 0.58 + hand * 0.42
    else:
        park_signal = float(overall)
    park_signal += hand_park_nudge(row, park_pct_fn=park_pct_fn) * 0.55
    zone_fit = zone_hr_fit(row)
    power = hr_power_form(row)
    return (
        park_signal * 1.85
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
        row["top5_ticket_rank"] = top5_hr_ticket_rank(row, park_pct_fn=park_pct_fn)


def o05_zone_lane_ok(row: dict) -> bool:
    """O0.5 strict pool: usable zone fit or loud HR form."""
    zone = row.get("zone_score") or 0.0
    zone_hr = row.get("zone_hr") or 0.0
    if zone >= 12.0 or zone_hr >= 10.0:
        return True
    if zone >= 8.0 and (row.get("zone_barrel") or 0.0) >= 14.0:
        return True
    return row.get("hr", 0) >= 2 and row.get("near", 0) >= 3
