#!/usr/bin/env python3
"""Hits parlay leg selection — contact + zone fit across the full slate.

Canonical rubric for all future MLB cheat sheet slates. Patch scripts should
import from here (see .cursor/rules/mlb-hr-slate-workflow.mdc — Hits parlay rubric).
Do not duplicate this logic inline in patch-YYYY-MM-DD-preview.py.

Design goals (revised Jul 2026):
- Cover the whole cheat sheet, not only +split HR-zone names.
- Prefer contact / put-in-play signals over HR power form.
- Ball-in-play % from the Research tab (Savant) is the primary opportunity
  signal — more balls in play means more chances at a hit.
- Soften platoon headwinds (hits still happen on mild negative splits).
- Spread legs across games so the ticket reflects the slate.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Callable

# Hits still happen on tough platoon lanes — only extreme headwinds are hard-cut.
# Ranking applies a soft split penalty so deep negatives need elite contact to climb.
SPLIT_HARD_FLOOR = -0.85
SPLIT_SOFT_FLOOR = -0.15

# Prefer slate coverage over stacking one game.
MAX_PER_GAME = 2
MAX_PER_TEAM = 2

_ROOT = Path(__file__).resolve().parent


def _norm_name(name: str) -> str:
    """Accent-insensitive join key: 'J. Peña (R)' -> 'jpena'."""
    base = unicodedata.normalize("NFKD", name or "")
    base = "".join(c for c in base if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", base.lower())


def load_research_hit_stats(sheet_date: str, root: Path | None = None) -> dict[str, dict]:
    """Per-batter contact stats from the Research tab JSON (Savant-backed).

    Returns norm-name -> {bip_pct, avg_bat, xwoba_bat, ld_pct, sweet_spot_pct, pa_bat}.
    Missing file returns {} so slates without research data still build.
    """
    path = (root or _ROOT) / "preview" / "data" / f"research-{sheet_date}.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    savant = data.get("savant_lookup") or {}
    out: dict[str, dict] = {}
    for game in data.get("games") or []:
        for side in ("awayLineup", "homeLineup"):
            for player in game.get(side) or []:
                stats = player.get("stats") or {}
                sv = savant.get(str(player.get("id"))) or {}
                entry = {
                    "bip_pct": stats.get("bipPct", sv.get("bipPct")),
                    "avg_bat": stats.get("avg", sv.get("avg")),
                    "xwoba_bat": stats.get("xwoba", sv.get("xwoba")),
                    "ld_pct": stats.get("ldPct", sv.get("ldPct")),
                    "sweet_spot_pct": sv.get("sweetSpotPct", stats.get("sweetSpotPct")),
                    "pa_bat": stats.get("pa", sv.get("pa")),
                }
                key = _norm_name(player.get("name") or "")
                if key and any(v is not None for v in entry.values()):
                    out[key] = entry
    return out


def attach_research_hit_stats(
    rows: list[dict], sheet_date: str, root: Path | None = None
) -> int:
    """Merge research-tab contact stats onto ranked rows by batter name."""
    lookup = load_research_hit_stats(sheet_date, root=root)
    if not lookup:
        return 0
    matched = 0
    for row in rows:
        key = _norm_name(row.get("name_plain") or row.get("name") or "")
        entry = lookup.get(key)
        if entry:
            row.update(entry)
            matched += 1
    return matched


def zone_hits_fit(row: dict) -> float:
    """Pitch-zone fit for O0.5 hits — contact first, overall zone second."""
    zone_score = row.get("zone_score") or 0.0
    zone_contact = row.get("zone_contact")
    zone_hard_hit = row.get("zone_hard_hit")
    zone_barrel = row.get("zone_barrel")

    # Contact in the zone is the primary hits signal.
    fit = 0.0
    if zone_contact is not None:
        fit += zone_contact * 1.15
        fit += max(zone_contact - 28.0, 0.0) * 0.55
    else:
        # Missing zone-contact: fall back to overall zone score at a discount.
        fit += zone_score * 0.85

    # Overall zone still matters, but less than for HR boards.
    fit += zone_score * 0.55

    if zone_hard_hit is not None:
        fit += max(zone_hard_hit - 20.0, 0.0) * 0.35
    if zone_barrel is not None:
        # Light barrel bump — barrels help, but this is a hits ticket.
        fit += max(zone_barrel - 14.0, 0.0) * 0.12
    return fit


def contact_hit_form(row: dict) -> float:
    """Recent contact profile — EV / hard contact over HR counting stats."""
    ev = row.get("ev") or 0.0
    hh = row.get("hh_pct")
    barrel = row.get("barrel") or 0.0
    gb = row.get("gb_pct")

    form = 0.0
    # Solid contact EV band for singles/doubles (not just moonshots).
    if ev >= 86.0:
        form += min(ev - 86.0, 12.0) * 0.55
    if hh is not None:
        form += max(hh - 35.0, 0.0) * 0.12
    # Light recent-event signal (presence of contact events, not HR chase).
    form += min(row.get("hr") or 0, 2) * 0.6
    form += min(row.get("near") or 0, 3) * 0.45
    form += min(barrel, 20.0) / 12.0

    # Ground-ball heavy profiles still get hits; don't punish them.
    if gb is not None and 35.0 <= gb <= 55.0:
        form += 1.2

    whiff = row.get("whiff_pct")
    k_pct = row.get("k_pct")
    for pct in (whiff, k_pct):
        if pct is not None and pct <= 22.0:
            form += (22.0 - pct) * 0.22
        elif pct is not None and pct <= 26.0:
            form += (26.0 - pct) * 0.08
    return form


def _research_sample_weight(row: dict) -> float:
    """Discount research terms on thin season samples (<60 PA)."""
    pa = row.get("pa_bat")
    if pa is None:
        return 1.0
    if pa >= 60:
        return 1.0
    return max(pa, 0) / 60.0


def bip_opportunity(row: dict) -> float:
    """Ball-in-play % (Research tab) — the core hits-opportunity signal.

    Slate median sits near 68%; reward high-BIP bats (more chances at a hit),
    drag low-BIP swing-and-miss profiles. Capped so it complements zone fit
    rather than dominating it.
    """
    bip = row.get("bip_pct")
    if bip is None:
        return 0.0
    edge = bip - 66.0
    if edge >= 0.0:
        term = min(edge, 18.0) * 0.65
    else:
        term = max(edge, -20.0) * 0.50
    return term * _research_sample_weight(row)


def research_contact_form(row: dict) -> float:
    """Season hit quality from the Research tab — AVG, xwOBA, LD%, sweet spot."""
    form = 0.0
    avg = row.get("avg_bat")
    if avg is not None:
        form += (avg - 0.240) * 40.0
    xwoba = row.get("xwoba_bat")
    if xwoba is not None:
        form += (xwoba - 0.310) * 25.0
    ld = row.get("ld_pct")
    if ld is not None:
        form += max(ld - 20.0, 0.0) * 0.15
    sweet = row.get("sweet_spot_pct")
    if sweet is not None:
        form += max(sweet - 32.0, 0.0) * 0.10
    return form * _research_sample_weight(row)


def whiff_penalty(row: dict, *, row_high_whiff: Callable[..., bool]) -> float:
    penalty = 0.0
    for pct in (row.get("whiff_pct"), row.get("k_pct")):
        if pct is not None and pct >= 20.0:
            penalty = max(penalty, (pct - 19.0) * 2.4)
    if row_high_whiff(row, for_hits=True):
        penalty += 45.0
    return penalty


def split_adjustment(row: dict) -> float:
    """Soft platoon edge — reward +split, light penalty for mild headwinds."""
    split = row.get("split") or 0.0
    if split >= 0.0:
        return split * 5.5
    if split >= SPLIT_SOFT_FLOOR:
        return split * 3.0  # mild headwind: small drag
    if split >= SPLIT_HARD_FLOOR:
        return split * 5.0  # deeper headwind: stronger drag, still eligible
    return split * 8.0


def compute_hits_rank(row: dict, *, row_high_whiff: Callable[..., bool]) -> float:
    zone_fit = zone_hits_fit(row)
    contact = contact_hit_form(row)
    park_edge = (row.get("park_pct") or 0) * 0.10
    # Model score is HR-tilted — keep it light so hits board isn't a HR clone.
    score_edge = (row.get("score") or 0) * 0.035
    return (
        zone_fit
        + contact * 0.85
        + bip_opportunity(row)
        + research_contact_form(row)
        + split_adjustment(row)
        + park_edge
        + score_edge
        - whiff_penalty(row, row_high_whiff=row_high_whiff)
    )


def annotate_hits_ranks(
    rows: list[dict],
    *,
    row_high_whiff: Callable[..., bool],
    sheet_date: str | None = None,
) -> None:
    if sheet_date:
        attach_research_hit_stats(rows, sheet_date)
    for row in rows:
        row["hits_rank"] = compute_hits_rank(row, row_high_whiff=row_high_whiff)
        row["hits_zone_fit"] = zone_hits_fit(row)


def _has_hit_form(row: dict) -> bool:
    return (
        (row.get("hr") or 0) >= 1
        or (row.get("near") or 0) >= 1
        or (row.get("ev") or 0) >= 88
        or (row.get("hh_pct") or 0) >= 40
        # Research tab: high ball-in-play rate or strong hit tool counts as form.
        or (row.get("bip_pct") or 0) >= 72
        or (row.get("avg_bat") or 0) >= 0.280
    )


def hits_base_pool(candidates: list[dict]) -> list[dict]:
    """Contact/zone pool across the slate; relax only if we cannot fill 11 legs."""

    def qualifies(r: dict, *, min_zone: float, min_contact: float, split_floor: float) -> bool:
        if (r.get("split") or 0.0) < split_floor:
            return False
        zone = r.get("zone_score") or 0.0
        z_contact = r.get("zone_contact") or 0.0
        # Strong zone-contact alone is enough for hits.
        if z_contact >= min_contact:
            return True
        if zone >= min_zone and z_contact >= min_contact - 6:
            return True
        if zone >= min_zone + 4:
            return True
        if z_contact >= min_contact - 4 and _has_hit_form(r):
            return True
        if zone >= min_zone - 2 and _has_hit_form(r):
            return True
        return False

    strict = [
        r
        for r in candidates
        if qualifies(r, min_zone=16.0, min_contact=26.0, split_floor=SPLIT_HARD_FLOOR)
    ]
    if len(strict) >= 11:
        return strict

    relaxed = [
        r
        for r in candidates
        if qualifies(r, min_zone=12.0, min_contact=22.0, split_floor=SPLIT_HARD_FLOOR)
    ]
    if len(relaxed) >= 11:
        return relaxed

    fallback = [
        r
        for r in candidates
        if (r.get("split") or 0.0) >= SPLIT_HARD_FLOOR
        and (
            (r.get("zone_score") or 0) >= 10
            or (r.get("zone_contact") or 0) >= 20
            or _has_hit_form(r)
        )
    ]
    if fallback:
        return fallback
    return [r for r in candidates if (r.get("split") or 0.0) >= -0.55]


def _pick_diverse(pool: list[dict], n: int) -> list[dict]:
    """Take top ranks with per-game / per-team caps so the ticket spans the slate."""
    legs: list[dict] = []
    seen: set[str] = set()
    game_counts: dict[str, int] = {}
    team_counts: dict[str, int] = {}

    for row in pool:
        if row["name"] in seen:
            continue
        game = row.get("game_key") or ""
        team = row.get("team") or ""
        if game and game_counts.get(game, 0) >= MAX_PER_GAME:
            continue
        if team and team_counts.get(team, 0) >= MAX_PER_TEAM:
            continue
        seen.add(row["name"])
        legs.append(row)
        if game:
            game_counts[game] = game_counts.get(game, 0) + 1
        if team:
            team_counts[team] = team_counts.get(team, 0) + 1
        if len(legs) == n:
            break

    # If diversity caps left us short, fill remaining by rank without caps.
    if len(legs) < n:
        for row in pool:
            if row["name"] in seen:
                continue
            seen.add(row["name"])
            legs.append(row)
            if len(legs) == n:
                break
    return legs


def select_hits_parlay(
    candidates: list[dict],
    *,
    row_high_whiff: Callable[..., bool],
    avoid_whiff: bool = True,
    n: int = 11,
    sheet_date: str | None = None,
) -> list[dict]:
    annotate_hits_ranks(candidates, row_high_whiff=row_high_whiff, sheet_date=sheet_date)
    pool = hits_base_pool(candidates)
    if avoid_whiff:
        pool = [r for r in pool if not row_high_whiff(r, for_hits=True)]
    pool = sorted(pool, key=lambda x: (x["hits_rank"], x.get("hits_zone_fit") or 0), reverse=True)
    return _pick_diverse(pool, n)


def fill_hits_parlay(
    candidates: list[dict],
    legs: list[dict],
    *,
    row_high_whiff: Callable[..., bool],
    n: int = 11,
) -> list[dict]:
    if len(legs) >= n:
        return legs[:n]
    have = {r["name"] for r in legs}
    game_counts: dict[str, int] = {}
    team_counts: dict[str, int] = {}
    for row in legs:
        game = row.get("game_key") or ""
        team = row.get("team") or ""
        if game:
            game_counts[game] = game_counts.get(game, 0) + 1
        if team:
            team_counts[team] = team_counts.get(team, 0) + 1

    def can_backfill(row: dict, *, respect_caps: bool) -> bool:
        if row["name"] in have:
            return False
        if row_high_whiff(row, for_hits=True):
            return False
        if (row.get("split") or 0.0) < SPLIT_HARD_FLOOR:
            return False
        if respect_caps:
            game = row.get("game_key") or ""
            team = row.get("team") or ""
            if game and game_counts.get(game, 0) >= MAX_PER_GAME:
                return False
            if team and team_counts.get(team, 0) >= MAX_PER_TEAM:
                return False
        zone = row.get("zone_score") or 0.0
        z_contact = row.get("zone_contact") or 0.0
        if zone >= 11.0 or z_contact >= 22.0:
            return True
        return _has_hit_form(row)

    ranked = sorted(
        candidates,
        key=lambda x: (x.get("hits_rank") or 0, x.get("hits_zone_fit") or 0),
        reverse=True,
    )
    for respect_caps in (True, False):
        for row in ranked:
            if not can_backfill(row, respect_caps=respect_caps):
                continue
            have.add(row["name"])
            legs.append(row)
            game = row.get("game_key") or ""
            team = row.get("team") or ""
            if game:
                game_counts[game] = game_counts.get(game, 0) + 1
            if team:
                team_counts[team] = team_counts.get(team, 0) + 1
            if len(legs) == n:
                return legs
    return legs
