#!/usr/bin/env python3
"""Worst Pickz 100-pt HR rating model — shared across slates.

  Power Profile ................ 30 pts  (HR / near-HR / EV)
  Pitcher HR Weakness .......... 20 pts  (overall HR risk of opposing SP)
  Recent Form .................. 15 pts  (blast profile, multi near-HR)
  Batter vs Pitcher Hand Edge .. 10 pts  (platoon split vs opposing SP)
  Contact Quality .............. 10 pts  (barrel / HR-FB / hard-hit, Savant)
  Park + Weather ............... 10 pts  (net HR park boost)
  Batter's Own Lane ............  8 pts  (his xwOBA vs this arm's hand)
  Zone Fit ......................  8 pts  (PropFinder zone score for the matchup)
  Pitcher Weak Spots ...........  5 pts  (bum-tier leak bonus)

Rebalanced 2026-09-07 against 6,323 archived prop rows joined to the box scores
for those same dates. Two things were wrong, and both pushed hitters the owner
had flagged as favorites down to the bottom of the card:

1. The old floor was 58, and 32.5% of every board landed exactly on it. That is
   not a rating, it is the scale refusing to answer. Inside that block, rows that
   homered 9.4% of the time printed the same number as rows that homered 14.5% of
   the time -- a 1.5x difference in real outcomes, erased. The floor is now 40 and
   binds on roughly one row in a thousand.

2. The pitcher outweighed the hitter, and the results say it should not. Measured
   against what actually happened, near-HR count separates 1.36x, HR count 1.29x
   and exit velocity 1.23x, while the opposing arm's HR risk manages 1.22x, park
   1.13x and the platoon split 1.12x -- and the split is not even monotonic. Yet
   the split and risk terms together swung 45 points against the batter's 22, so a
   suppressed arm dragged every bat facing him to the floor no matter how he was
   swinging. Hand edge drops 15 -> 10 pts, HR weakness 25 -> 20, and the HR +
   near-HR term inside Power Profile is allowed 20 instead of 14.

3. The rating read data the site had already collected and then threw most of it
   away. Contact quality, the batter's own platoon lane and the PropFinder zone
   score were all sitting in the pipeline unused, and every one of them separates
   harder than the terms the score was leaning on: HR/FB 1.72x, barrel rate 1.67x,
   zone fit 1.65x and own lane 1.42x, against 1.22x for the pitcher's split, 1.21x
   for his HR risk and 1.18x for exit velocity. Worse, `float("25.0%")` raises, so
   the export's percent columns had always parsed as None and the barrel term --
   6 of the 30 Power Profile points -- had never once fired.

Top-versus-bottom decile separation went from 1.38x to 2.71x on slates the fit
never saw, and the 90-100 band from 16.3% to 20.7% against a 14.0% board.
Favorites were NOT given a bonus: they rise because the form that made them
favorites finally counts for what it is worth.

Import from build-XXXX-from-csv.py; do NOT copy/paste the formula so
future slates can't silently revert to an older model.
"""
from __future__ import annotations


# Chosen on holdout slates, not by eye. Base 26 puts the median card at ~72, which
# is where it has always sat, so the sheet still reads the way the owner is used to
# even though three new components are now in play. The knee at 86 keeps the elite
# band selective: 90-100 now hits 20.7% against a 14.0% board, where it used to hit
# 16.3% and mean almost nothing.
CONTACT_POINTS = 10.0
OWN_LANE_POINTS = 8.0
ZONE_POINTS = 8.0
BASE_SCORE = 26.0
ELITE_KNEE = 86.0
ELITE_SLOPE = 0.45
# A real floor, not a hiding place. The old 58 absorbed a third of every board.
SCORE_FLOOR = 40.0


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



def contact_quality(profile: dict | None, points: float = 10.0) -> float:
    """Quality of contact from the Savant profile, 0..points.

    Barrel rate, HR/FB and hard-hit rate describe the same swing from three
    angles, so they are averaged rather than stacked -- stacking them would let
    one hot fortnight buy 30 points. Measured against results these separate
    1.67x, 1.72x and 1.40x, where the pitcher terms the rating leaned on manage
    about 1.2x. A batter with no profile gets a neutral share, never a penalty.

    Deliberately NOT the per-matchup percentages in the PropFinder export: those
    are computed over roughly eight batted balls, so a single barrel reads as 12.5%
    and two read as 25%. That is noise wearing a rate's clothing.
    """
    if not profile:
        return points * 0.4
    parts = []
    barrel, hrfb, hard = profile.get("barrel"), profile.get("hrfb"), profile.get("hard")
    if barrel is not None:
        parts.append(_clamp((barrel - 6.0) / 9.0, 0.0, 1.0))
    if hrfb is not None:
        parts.append(_clamp((hrfb - 9.0) / 11.0, 0.0, 1.0))
    if hard is not None:
        parts.append(_clamp((hard - 36.0) / 14.0, 0.0, 1.0))
    if not parts:
        return points * 0.4
    return (sum(parts) / len(parts)) * points


def own_lane(profile: dict | None, points: float = 8.0) -> float:
    """The batter's own xwOBA against this arm's hand, 0..points.

    The rating has always read the PITCHER's platoon split and never the hitter's.
    That is how Alec Burleson came to be rated 47 on 2026-09-07 carrying a .401
    xwOBA against right-handers over 422 plate appearances, against a right-hander
    -- and he homered. Damped by sample: 200 PA earns the full swing, 50 earns a
    quarter of it, so a hot fortnight cannot masquerade as a platoon edge.
    """
    if not profile or profile.get("lane_xwoba") is None:
        return points * 0.4
    trust = _clamp((profile.get("lane_pa") or 0) / 200.0, 0.25, 1.0)
    edge = _clamp((profile["lane_xwoba"] - 0.320) / 0.080, -1.0, 1.0)
    return points * (0.4 + 0.6 * edge * trust)


def zone_fit_points(zone: float | None, points: float = 8.0) -> float:
    """PropFinder's zone score for this batter against this arm, 0..points.

    Already trusted enough to rank the Goblin cards; it separates 1.65x against
    results, so it belongs in the number on the card too.
    """
    if zone is None:
        return points * 0.4
    return points * _clamp((zone - 12.0) / 18.0, 0.0, 1.0)


def score_from_model(
    hr: int,
    near: int,
    ev: float | None,
    barrel: float | None,
    blast: str | None,
    split: float | None,
    risk_overall: float | None,
    park_pct: int | None,
    profile: dict | None = None,
    zone: float | None = None,
) -> int:
    """`profile` carries the batter's Savant contact rates and his xwOBA against
    this arm's hand; `zone` is his PropFinder zone score for the matchup. Both are
    optional so the historical dated builders keep running, but every current
    builder passes them -- without them a third of the rating goes neutral."""
    # Power Profile (0-30). The HR + near-HR term is allowed 20 of those points:
    # near-HR count is the single best predictor in the backtest, and capping the
    # pair at 14 flattened a bat carrying 3 HR and 3 near-HR into one holding two.
    power = min(hr * 4.0 + near * 1.5, 20.0)
    if ev:
        power += _clamp(ev - 86.0, 0.0, 10.0)
    if barrel:
        power += _clamp(barrel * 0.4, 0.0, 6.0)
    power = min(power, 30.0)

    # Hand Edge (-4 to 10); unknown split gets small neutral credit.
    # Halved from 8.0/leverage 20: the platoon split separated only 1.12x against
    # real outcomes and was not monotonic, which is not worth 20 points of swing.
    if split is None:
        hand_edge = 3.0
    else:
        hand_edge = _clamp(split * 4.0, -4.0, 10.0)

    # Pitcher HR Weakness (-6 to 20) + Weak Spots bum bonus (0-5).
    # Still the largest single matchup term, just no longer able to bury a hot bat
    # on its own: at 9.0 leverage a -1.9 arm subtracted 17 points before the hitter
    # was even considered.
    if risk_overall is None:
        weakness = 8.0
        weak_spots = 0.0
    else:
        weakness = _clamp(10.0 + risk_overall * 6.0, -6.0, 20.0)
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

    raw = (
        power
        + hand_edge
        + weakness
        + weak_spots
        + park
        + form
        + contact_quality(profile, CONTACT_POINTS)
        + own_lane(profile, OWN_LANE_POINTS)
        + zone_fit_points(zone, ZONE_POINTS)
    )
    value = BASE_SCORE + raw
    # Soft-compress the elite band so stacked matchups don't all pin at the cap.
    if value > ELITE_KNEE:
        value = ELITE_KNEE + (value - ELITE_KNEE) * ELITE_SLOPE
    return int(round(_clamp(value, SCORE_FLOOR, 99.0)))
