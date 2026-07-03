#!/usr/bin/env python3
"""Worst Pickz 100-pt HR rating model — shared across slates.

Implements the on-sheet legend weights so card scores reflect the full
matchup, not just batter form:

  Power Profile ................ 30 pts  (HR / near-HR / EV / barrels)
  Batter vs Pitcher Hand Edge .. 15 pts  (platoon split vs opposing SP)
  Pitcher HR Weakness .......... 25 pts  (overall HR risk of opposing SP)
  Pitcher Weak Spots ...........  5 pts  (bum-tier leak bonus)
  Park + Weather ............... 10 pts  (net HR park boost)
  Recent Form + Price .......... 15 pts  (blast profile, multi near-HR)

Import from build-XXXX-from-csv.py; do NOT copy/paste the formula so
future slates can't silently revert to an older model.
"""
from __future__ import annotations


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def batter_split(hand: str, risk: dict | None) -> float | None:
    """Platoon split vs opposing SP; switch hitters get their better lane."""
    if not risk:
        return None
    if hand == "S":
        return max(risk["vs_lhb"], risk["vs_rhb"])
    return risk["vs_lhb"] if hand == "L" else risk["vs_rhb"]


def score_from_model(
    hr: int,
    near: int,
    ev: float | None,
    barrel: float | None,
    blast: str | None,
    split: float | None,
    risk_overall: float | None,
    park_pct: int | None,
) -> int:
    # Power Profile (0-30)
    power = min(hr * 4.0 + near * 1.5, 14.0)
    if ev:
        power += _clamp(ev - 86.0, 0.0, 10.0)
    if barrel:
        power += _clamp(barrel * 0.4, 0.0, 6.0)
    power = min(power, 30.0)

    # Hand Edge (-5 to 15); unknown split gets small neutral credit
    if split is None:
        hand_edge = 4.0
    else:
        hand_edge = _clamp(split * 8.0, -5.0, 15.0)

    # Pitcher HR Weakness (-8 to 25) + Weak Spots bum bonus (0-5)
    if risk_overall is None:
        weakness = 10.0
        weak_spots = 0.0
    else:
        weakness = _clamp(12.0 + risk_overall * 9.0, -8.0, 25.0)
        if risk_overall >= 0.95:
            weak_spots = 5.0
        elif risk_overall >= 0.40:
            weak_spots = 3.0
        else:
            weak_spots = 0.0

    # Park + Weather (-5 to 10)
    park = _clamp((park_pct or 0) * 0.25, -5.0, 10.0)

    # Recent Form (0-15)
    form = {"high": 10.0, "good": 6.0}.get(blast or "", 2.0)
    if near >= 3:
        form += 3.0
    if hr >= 3:
        form += 2.0
    form = min(form, 15.0)

    raw = power + hand_edge + weakness + weak_spots + park + form
    value = 31.0 + raw
    # Soft-compress the elite band so stacked matchups don't all pin at the cap.
    if value > 90.0:
        value = 90.0 + (value - 90.0) * 0.4
    return int(round(_clamp(value, 58.0, 99.0)))
