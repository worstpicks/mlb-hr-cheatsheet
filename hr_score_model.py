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


def batter_split(hand: str, risk: dict | None, throws: str | None = None) -> float | None:
    """Platoon split vs the opposing SP, in the lane the batter will actually stand in.

    A switch hitter does not get to pick his better side -- he bats OPPOSITE the arm.
    Against a left-hander he is a right-handed batter, so the pitcher's vs-RHB lane
    is the one that applies. Taking max() of the two lanes, which is what this did
    until 2026-09-05, can only ever inflate a switch hitter and never deflate him:
    it put Cal Raleigh on the 3-leg card carrying a +1.58 split he was never going to
    see (Springs is a lefty, Raleigh bats right against him, and Springs sits at
    +0.25 in that lane), and it made Leo Bernal the second-highest score on the whole
    board off +1.50 when his real lane against Mason Adams is +0.82.

    `throws` is optional only so the historical dated scripts that import this keep
    running; every current builder passes it.
    """
    if not risk:
        return None
    if hand == "S":
        if throws:
            return risk["vs_rhb"] if throws.upper() == "L" else risk["vs_lhb"]
        return max(risk["vs_lhb"], risk["vs_rhb"])
    return risk["vs_lhb"] if hand == "L" else risk["vs_rhb"]


def switch_side(throws: str | None) -> str:
    """Which side a switch hitter bats from against this arm."""
    return "RHB" if (throws or "").upper() == "L" else "LHB"


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
