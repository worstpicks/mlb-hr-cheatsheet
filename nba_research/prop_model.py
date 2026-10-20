"""The Prop Shop's projection model: one player, one stat, one line.

    projection = minutes x rate x matchup x pace

  minutes  how long he plays tonight. Last season's closing stretch and this
           preseason, blended (see project_minutes); a new team leans on the preseason.
  rate     his per-minute production, every game of last season plus the preseason,
           older games fading, shrunk toward his position's league rate by the
           minutes behind it. SHRINK and DECAY are fitted on 2025-26 (prop_fit.py).
  matchup  what tonight's opponent allowed per minute to his position, against the
           league, shrunk by how many games it rests on and by how much the roster
           has turned over (the start of a season leans on last year's teams).
  pace     tonight's total against an average game.

The chance of clearing a line comes from a negative binomial around the
projection whose level, spread and scatter were fitted on 2025-26 games the
model had not seen when it projected them (prop_shop_fit.json). Standard
library only, so the scheduled builders can run it.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIT = HERE / "prop_shop_fit.json"

STATS = ("pts", "reb", "ast", "threem", "stl", "blk")
COMBOS = {"pra": ("pts", "reb", "ast"), "pr": ("pts", "reb"), "pa": ("pts", "ast"),
          "ra": ("reb", "ast"), "stocks": ("stl", "blk")}
MARKETS = STATS + tuple(COMBOS)
LABELS = {"pts": "Points", "reb": "Rebounds", "ast": "Assists", "threem": "Threes",
          "stl": "Steals", "blk": "Blocks", "pra": "Pts + Reb + Ast", "pr": "Pts + Reb",
          "pa": "Pts + Ast", "ra": "Reb + Ast", "stocks": "Steals + Blocks"}

# Before a fit exists: league-average shrink and the projection at its word.
DEFAULT = {
    "decay": 0.98, "min_decay": 0.85,
    "shrink": {"pts": 60.0, "reb": 80.0, "ast": 80.0, "threem": 120.0, "stl": 250.0, "blk": 250.0},
    "params": {s: {"b": [0.0, 1.0], "phi": p} for s, p in
               {"pts": 2.5, "reb": 1.5, "ast": 1.5, "threem": 1.3, "stl": 1.1, "blk": 1.3,
                "pra": 3.0, "pr": 2.8, "pa": 2.8, "ra": 1.6, "stocks": 1.2}.items()},
}


def load_fit() -> dict:
    if FIT.exists():
        fit = json.loads(FIT.read_text(encoding="utf-8"))
        return {**DEFAULT, **{k: fit[k] for k in ("decay", "min_decay", "shrink", "params") if k in fit}}
    return DEFAULT


# ── negative binomial (variance = phi x mean) ──────────────────────────────────

def logpmf(y: int, m: float, phi: float) -> float:
    m = max(m, 1e-9)
    if phi <= 1.0005:  # no extra scatter: Poisson
        return y * math.log(m) - m - math.lgamma(y + 1)
    r = m / (phi - 1.0)
    return (math.lgamma(y + r) - math.lgamma(r) - math.lgamma(y + 1)
            + r * math.log(r / (r + m)) + y * math.log(m / (r + m)))


def at_least(k: int, m: float, phi: float) -> float:
    """P(X >= k)."""
    if k <= 0:
        return 1.0
    below = sum(math.exp(logpmf(j, m, phi)) for j in range(k))
    return min(1.0, max(0.0, 1.0 - below))


def mean(b: list[float], proj: float) -> float:
    return math.exp(b[0]) * max(proj, 0.02) ** b[1]


def chance_over(line: float, proj: float, params: dict) -> float:
    """Chance an Over `line` cashes: at least floor(line) + 1."""
    need = int(math.floor(line)) + 1
    return at_least(need, mean(params["b"], proj), params["phi"])


# ── the pieces of a projection ─────────────────────────────────────────────────

def rate_weight(log: dict, season: int) -> float:
    """How much a game's per-minute line counts before recency. Preseason minutes
    come against other clubs' fourth units; a rate from them counts less."""
    if log.get("type") == 2:
        return 1.0 if log.get("season") == season - 1 or log.get("season") == season else 0.7
    return 0.4


def decayed(logs: list[dict], season: int, decay: float) -> tuple[dict, float]:
    """(counts, minutes), each game weighted by rate_weight and faded by age."""
    made = {s: 0.0 for s in STATS}
    mins = 0.0
    for i, log in enumerate(sorted(logs, key=lambda l: l["date"], reverse=True)):
        w = rate_weight(log, season) * decay ** i
        mins += w * (log.get("min") or 0.0)
        for s in STATS:
            made[s] += w * (log.get(s) or 0.0)
    return made, mins


def per_minute(made: dict, mins: float, prior: dict, shrink: dict) -> dict:
    return {s: (made[s] + shrink[s] * prior.get(s, 0.0)) / (mins + shrink[s]) for s in STATS}


def project_minutes(logs: list[dict], team: str, season: int, min_decay: float,
                    starting: bool | None = None) -> tuple[float, str]:
    """Tonight's minutes and where they came from.

    Last season's closing stretch with this club is the best read of a role; the
    preseason says whether the role moved. A player on a new club leans on the
    preseason, and a rookie has nothing else. Exhibition minutes run light:
    measured on the 2026-27 opening-week rosters against their 2025-26 closing
    games with the same club, starters played 1.5x their preseason minutes (75
    players, median) and bench players 1.2x (142)."""
    reg = sorted((l for l in logs if l.get("type") == 2 and l.get("min")), key=lambda l: l["date"], reverse=True)[:15]
    pre = [l for l in logs if l.get("type") == 1 and l.get("min") and l.get("season") == season]

    def fade(rows):
        w = sum(min_decay ** i for i in range(len(rows)))
        return sum(min_decay ** i * r["min"] for i, r in enumerate(rows)) / w if w else None

    m_reg = fade(reg)
    m_pre = None
    if pre:
        starts = sum(1 for l in pre if l.get("starter"))
        # tonight's lineup, when it is known, decides which lift applies: a rookie
        # who started exhibitions but comes off the bench tonight gets no lift
        start = starting if starting is not None else starts * 2 >= len(pre)
        lift = 1.5 if start else (1.2 if reg else 1.0)
        m_pre = lift * sum(l["min"] for l in pre) / len(pre)
    same_team = bool(reg) and reg[0].get("team") == team
    if m_reg is not None and m_pre is not None:
        w_pre = min(0.35, 0.1 * len(pre)) if same_team else min(0.7, 0.2 * len(pre))
        return (1 - w_pre) * m_reg + w_pre * m_pre, ("last season and the preseason" if same_team
                                                    else "the preseason with his new club and last season")
    if m_reg is not None:
        return m_reg, "last season's closing stretch"
    if m_pre is not None:
        return m_pre, "the preseason only"
    return 0.0, "no games"


def matchup_ratio(allowed: dict | None, league_pos: dict, stat: str, games: int, turnover: float = 1.0) -> float:
    """Opponent's per-minute allowed to the position against the league, shrunk
    by its sample and by `turnover` (1 = same roster, 0.5 = half of it is new)."""
    parts = COMBOS.get(stat, (stat,))
    if not allowed or not all(league_pos.get(s) for s in parts):
        return 1.0
    raw = sum(allowed.get(s, 0.0) for s in parts) / sum(league_pos[s] for s in parts)
    k = games / (games + 15.0) * turnover
    return max(0.85, min(1.15, 1.0 + k * (raw - 1.0)))


def pace_factor(total: float | None, league_total: float) -> float:
    """Possessions move with the total. Half of a total's gap to average is pace,
    the rest shooting, so counting stats move about half as far."""
    if not total or not league_total:
        return 1.0
    return max(0.95, min(1.05, 1.0 + 0.5 * (total / league_total - 1.0)))
