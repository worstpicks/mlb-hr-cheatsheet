"""The Worst Pickz anytime-goal rating: five components, 100 points.

Ported from the hand-built NHL cheat sheets (nhl_cheatsheet_*_revamp.html) so
the generated board scores plays the same way the old ones did:

    Shot Volume            20   shots per game, and whether he is firing enough
                                to make several goal paths instead of needing
                                one perfect chance
    Shot Quality           20   weighted toward iFF and iSCF, so the top of the
                                board is dangerous touches rather than volume
    Defensive Exploitability 20 opponent goals, shots and attempts allowed,
                                overall and to his line slot
    Goalie Matchup         15   the opposing goalie's SV%, GA/G and high-danger
                                save rate
    Form and Tendencies    15   recent goal pace, role security, power-play work

    90-100 Elite Target · 80-89 Strong · 70-79 Playable · 60-69 Thin · <60 Dart

Each component is scored by where a player sits in the league's distribution for
that input rather than against a fixed cutoff, so the bands keep their meaning
when scoring across the league moves.
"""
from __future__ import annotations

from bisect import bisect_left

BANDS = (
    (90, "elite", "Elite Target"),
    (80, "strong", "Strong Target"),
    (70, "playable", "Playable"),
    (60, "thin", "Thin"),
    (0, "dart", "Dart"),
)

WEIGHTS = {"volume": 20, "quality": 20, "defense": 20, "goalie": 15, "form": 15}


def band(score: float) -> tuple[str, str]:
    for cut, key, label in BANDS:
        if score >= cut:
            return key, label
    return "dart", "Dart"


class Percentile:
    """Where a value sits in a league distribution, 0..1.

    Fed the breakpoints the slate ships (nhl_stats.percentile_breaks), so a
    player is measured against the whole league rather than against the dozen
    clubs on tonight's slate. Scoring off the slate made the bands drift with
    its size: a five-game night is mostly depth forwards, and grading them
    against each other pushed almost the entire board into Dart.
    """

    def __init__(self, breaks):
        self.breaks = list(breaks or [])

    def of(self, value) -> float:
        if not self.breaks or value is None:
            return 0.5
        i = bisect_left(self.breaks, value)
        return min(1.0, i / (len(self.breaks) - 1))


def _pts(pct: float, weight: int) -> float:
    """A percentile into points.

    The curve is deliberately gentle at the bottom: a player in the 10th
    percentile for shot volume still takes shots, and zeroing him out would let
    one weak component drag an otherwise strong profile below the bands.
    """
    return round(weight * (0.25 + 0.75 * max(0.0, min(1.0, pct))), 2)


def build_scales(slate_scales: dict) -> dict:
    """Wrap the slate's shipped league breakpoints as lookups."""
    return {key: Percentile(breaks) for key, breaks in (slate_scales or {}).items()}


def score_row(r: dict, s: dict) -> dict:
    """Score one skater against one opponent. Returns the parts and the total."""
    # ── Shot Volume (20) ── how many paths to a goal he creates
    volume = _pts(0.6 * s["sog"].of(r["sog"]) + 0.4 * s["icf"].of(r["icf"]),
                  WEIGHTS["volume"])

    # ── Shot Quality (20) ── weighted toward iFF and iSCF, per the model
    quality = _pts(0.25 * s["iff"].of(r["iff"])
                   + 0.45 * s["iscf"].of(r["iscf"])
                   + 0.30 * s["ihdcf"].of(r["ihdcf"]),
                   WEIGHTS["quality"])

    # ── Defensive Exploitability (20) ── the soft lane, by slot and overall
    defense = _pts(0.40 * s["opp_g"].of(r["opp_g"])
                   + 0.30 * s["opp_sog"].of(r["opp_sog"])
                   + 0.30 * s["opp_iscf"].of(r["opp_iscf"]),
                   WEIGHTS["defense"])

    # ── Goalie Matchup (15) ── a leaking goalie lifts a fringe shooter
    if r["g_sv_pct"]:
        # inverted: the WORSE the goalie saves, the better for the shooter
        goalie = _pts(0.45 * (1 - s["gsv"].of(r["g_sv_pct"]))
                      + 0.35 * (1 - s["ghd"].of(r["g_hd_sv_pct"]))
                      + 0.20 * s["gga"].of(r["g_ga"]),
                      WEIGHTS["goalie"])
    else:
        # No named starter yet: score it neutral rather than inventing an edge.
        goalie = WEIGHTS["goalie"] * 0.6

    # ── Form and Tendencies (15) ── recent pace, role security, power play
    form = _pts(0.40 * s["g"].of(r["g5_rate"])
                + 0.35 * s["toi"].of(r["toi"])
                + 0.25 * s["pp_p"].of(r["pp_p"]),
                WEIGHTS["form"])

    total = round(volume + quality + defense + goalie + form, 1)
    key, label = band(total)
    return {
        "score": total,
        "band": key,
        "band_label": label,
        "parts": {
            "volume": round(volume, 1), "quality": round(quality, 1),
            "defense": round(defense, 1), "goalie": round(goalie, 1),
            "form": round(form, 1),
        },
    }


def warnings_for(r: dict, parts: dict) -> str:
    """The one thing most fighting this profile, or "" when nothing is."""
    worst = min(parts.items(), key=lambda kv: kv[1] / WEIGHTS[kv[0]])
    name, points = worst
    share = points / WEIGHTS[name]
    if share >= 0.62:
        return ""
    return {
        "volume": "Not enough shot volume",
        "quality": "Shots are from low-danger ice",
        "defense": "Defense travels well",
        "goalie": f"{r.get('g_name') or 'The goalie'} is too hot",
        "form": "Weak recent scoring lane",
    }[name]
