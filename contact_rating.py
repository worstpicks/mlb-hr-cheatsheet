#!/usr/bin/env python3
"""Five-star contact rating: how likely is this hitter to put the ball in play today.

One star is a bat that strikes out a lot in this matchup, five is a bat that makes
contact. The number behind the stars is an EXPECTED strikeout rate for this specific
matchup, not the hitter's season K% -- a 15% strikeout hitter against Dylan Cease is
not the same proposition as the same hitter against a soft-tossing lefty, and a star
that ignores the arm would say they were.

Three things make it steadier than raw K%:

1. log5. Combining a batter rate and a pitcher rate by averaging them is wrong at
   the extremes; log5 is the standard odds-ratio method and behaves properly when
   either side is unusual.

2. Whiff rate as a second estimate. Whiff% is measured on every pitch rather than
   every plate appearance, so it settles far sooner. Fitted over 13,907 batter
   profiles, K% = 0.39 + 0.871 x whiff% with r = 0.82 -- it explains 68% of the
   variation in K%, which makes it a good stand-in when the PA sample is thin.

3. Regression to league by sample size. A hitter with 40 plate appearances does not
   get a five-star or a one-star on 40 plate appearances' worth of evidence.
"""
from __future__ import annotations

# Both batters and pitchers average 22.2% across every archived slate.
LEAGUE_K_PCT = 22.2

# K% = A + B x whiff%, fitted on batters with >= 60 PA in their profile window.
K_FROM_WHIFF = (0.39, 0.871)

# K% settles quickly, so the priors are light. PA/BF beyond these barely move.
BATTER_PRIOR_PA = 90.0
# How hard to pull a pitcher's strikeout rate toward league. The two uses below
# genuinely want different answers, and forcing one number on both makes each
# slightly worse, so each carries its own -- tuned on its own outcome:
#
#   the star on a single plate appearance wants MORE shrinkage (200): one matchup
#   is noisy, and at 80 the per-batter separation falls from 15.6pp to 14.6pp
#
#   the projected K line over a whole start wants LESS (80): at 200 a starter with
#   50 innings is half-regressed to league, which flattens every line toward
#   "about five" -- spread sd 0.68 against 0.89, for a hair more error
PITCHER_PRIOR_BF = 200.0
K_LINE_PITCHER_PRIOR_BF = 80.0
# Below this many PA, lean on the whiff-implied estimate instead of the observed K%.
PA_FULL_TRUST = 150.0
# Starters in this sample average 21.66 batters faced over 5.21 innings.
BF_PER_IP = 4.16


def _blend_batter_k(k_pct: float | None, pa: float | None, whiff_pct: float | None) -> float | None:
    """The hitter's own strikeout rate, steadied by his whiff rate."""
    pa = pa or 0.0
    implied = None
    if whiff_pct is not None:
        implied = K_FROM_WHIFF[0] + K_FROM_WHIFF[1] * whiff_pct
    if k_pct is None:
        return implied
    if implied is None:
        return k_pct
    trust_own = min(1.0, pa / PA_FULL_TRUST)
    return trust_own * k_pct + (1.0 - trust_own) * implied


def _regress(rate: float | None, sample: float | None, prior: float) -> float:
    """Pull a rate toward league in proportion to how little of it there is."""
    if rate is None:
        return LEAGUE_K_PCT
    sample = max(0.0, sample or 0.0)
    return (rate * sample + LEAGUE_K_PCT * prior) / (sample + prior)


def pitcher_sample(pitcher_bf: float | None, pitcher_ip: float | None) -> float:
    """Batters faced, from innings when the batters-faced figure is absent.

    The research profile carries innings and not batters faced, and _regress treats
    a missing sample as zero -- which pulled every arm all the way to the league
    strikeout rate and quietly removed the pitcher from this calculation entirely.
    A 20% strikeout hitter came out at 20.5% against a soft-tosser and 20.5%
    against Dylan Cease.
    """
    if pitcher_bf:
        return float(pitcher_bf)
    if pitcher_ip:
        return float(pitcher_ip) * BF_PER_IP
    return 0.0


def expected_k_pct(
    batter_k: float | None,
    batter_pa: float | None,
    batter_whiff: float | None,
    pitcher_k: float | None,
    pitcher_bf: float | None = None,
    pitcher_ip: float | None = None,
    pitcher_prior: float | None = None,
) -> float:
    """Matchup strikeout rate, as a percentage, via log5."""
    b = _regress(_blend_batter_k(batter_k, batter_pa, batter_whiff), batter_pa, BATTER_PRIOR_PA) / 100.0
    prior = PITCHER_PRIOR_BF if pitcher_prior is None else pitcher_prior
    p = _regress(pitcher_k, pitcher_sample(pitcher_bf, pitcher_ip), prior) / 100.0
    lg = LEAGUE_K_PCT / 100.0
    b = min(max(b, 0.01), 0.75)
    p = min(max(p, 0.01), 0.75)
    num = b * p / lg
    den = num + ((1.0 - b) * (1.0 - p) / (1.0 - lg))
    return 100.0 * (num / den) if den else LEAGUE_K_PCT


# Cut points on expected K%, placed at the 10th/30th/70th/90th percentile of the
# board so every tier is a slice someone will actually see -- an earlier pass put
# five stars on 1.6% of bats and three stars on 49%, which is a rating that mostly
# says nothing. Checked against 17,967 batter-games of box scores:
#
#   *****  10.1% of bats   struck out 12.6% of the time
#   ****   20.0%                      17.5%
#   ***    40.0%                      22.5%   (league is 22.2%)
#   **     19.9%                      27.2%
#   *      10.0%                      32.0%
STAR_EDGES = (17.2, 19.9, 24.0, 27.4)


def contact_stars(expected_k: float | None) -> int:
    """5 = puts it in play, 1 = strikeout risk. Lower expected K% earns more stars."""
    if expected_k is None:
        return 3
    for stars, edge in zip((5, 4, 3, 2), STAR_EDGES):
        if expected_k < edge:
            return stars
    return 1


def contact_profile(batter_stats: dict | None, pitcher_stats: dict | None) -> dict | None:
    """Everything the card needs: stars, the matchup rate, and both inputs."""
    if not batter_stats:
        return None
    bk = batter_stats.get("kPct")
    bw = batter_stats.get("whiffPct")
    if bk is None and bw is None:
        return None
    pk = (pitcher_stats or {}).get("kPct")
    ps = pitcher_stats or {}
    exp = expected_k_pct(bk, batter_stats.get("pa"), bw, pk, ps.get("bf"), ps.get("ip"))
    return {
        "stars": contact_stars(exp),
        "k": round(exp, 1),
        "batterK": round(bk, 1) if bk is not None else None,
        "batterWhiff": round(bw, 1) if bw is not None else None,
        "pitcherK": round(pk, 1) if pk is not None else None,
    }


# Starters in this sample average 21.7 batters faced and 5.2 innings per start.
LEAGUE_BF_PER_START = 21.7
# Measured miss of this projection across 1,768 starts. Most of it is irreducible:
# one start is close to binomial(22, .238), which alone carries an sd of 1.98 K, so
# a perfect rate model would still miss by about 1.6 K on average. Anyone quoting a
# K line to one decimal and meaning it is not telling you about this number.
LINE_RESIDUAL_SD = 2.31
# 0.7 sd covers 64% of starts in a band about 3 K wide. A full standard deviation
# covers 77% but spans nearly 5 K, which is too vague to bet into.
LINE_BAND_SD = 0.7
# Starts needed before a pitcher's own workload is trusted over the league figure.
BF_PRIOR_STARTS = 6.0


def batters_faced_estimate(bf_total: float | None, starts: float | None) -> float:
    """How many hitters this arm should see, regressed toward the league start."""
    if not bf_total or not starts:
        return LEAGUE_BF_PER_START
    own = bf_total / starts
    weight = starts / (starts + BF_PRIOR_STARTS)
    return weight * own + (1.0 - weight) * LEAGUE_BF_PER_START


def projected_k_line(
    pitcher_stats: dict | None,
    lineup: list[dict] | None,
    bf: float | None = None,
) -> dict | None:
    """Projected strikeouts for this start, added up one hitter at a time.

    A pitcher's K% against the league is not his K% against the nine men actually
    posted behind the plate tonight, which is the whole point of putting a line on
    the card: the same arm is a different bet against a contact lineup than against
    a lineup that whiffs. Each batter in the order contributes his own log5 rate,
    and the order wraps -- the top of the lineup gets a third look, the bottom does
    not, which is worth roughly half a strikeout on its own.

    Returns the projection plus the pieces behind it so the card can show its work.
    """
    if not lineup:
        return None
    faced = bf if bf is not None else LEAGUE_BF_PER_START
    if faced <= 0:
        return None
    pk = (pitcher_stats or {}).get("kPct")
    pbf = (pitcher_stats or {}).get("bf")
    pip = (pitcher_stats or {}).get("ip")

    total = 0.0
    seen = 0.0
    i = 0
    while seen < faced:
        batter = lineup[i % len(lineup)]
        share = min(1.0, faced - seen)
        rate = expected_k_pct(
            batter.get("kPct"), batter.get("pa"), batter.get("whiffPct"), pk, pbf, pip,
            K_LINE_PITCHER_PRIOR_BF,
        )
        total += share * rate / 100.0
        seen += share
        i += 1

    band = LINE_RESIDUAL_SD * LINE_BAND_SD
    return {
        "k": round(total, 1),
        "lo": max(0, round(total - band)),
        "hi": round(total + band),
        "bf": round(faced, 1),
        # the rate he is actually running against THIS order, which is the number
        # that differs from his season K% and the reason the line moves
        "matchupK": round(100.0 * total / faced, 1),
        "ownK": round(pk, 1) if pk is not None else None,
    }
