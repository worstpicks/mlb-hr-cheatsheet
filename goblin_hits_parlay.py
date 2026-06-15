#!/usr/bin/env python3
"""Hits parlay leg selection — zone fit first, contact quality second.

Canonical rubric for all future MLB cheat sheet slates. Patch scripts should
import from here (see .cursor/rules/mlb-hr-slate-workflow.mdc — Hits parlay rubric).
Do not duplicate this logic inline in patch-YYYY-MM-DD-preview.py.
"""
from __future__ import annotations

from typing import Callable


def zone_hits_fit(row: dict) -> float:
    """Pitch-zone fit for O0.5 hits (primary hits-parlay signal)."""
    zone_score = row.get("zone_score") or 0.0
    zone_contact = row.get("zone_contact")
    zone_hard_hit = row.get("zone_hard_hit")
    zone_barrel = row.get("zone_barrel")

    fit = zone_score * 1.55
    if zone_contact is not None:
        fit += max(zone_contact - 22.0, 0.0) * 0.42
    if zone_hard_hit is not None:
        fit += max(zone_hard_hit - 18.0, 0.0) * 0.28
    if zone_barrel is not None:
        fit += max(zone_barrel - 12.0, 0.0) * 0.18
    return fit


def contact_hit_form(row: dict) -> float:
    """Secondary: recent contact / barrel profile (not HR-specific)."""
    recent = (row.get("hr") or 0) * 1.2 + (row.get("near") or 0) * 1.0
    recent += max((row.get("ev") or 0.0) - 88.0, 0.0) * 0.45
    recent += (row.get("barrel") or 0.0) / 8.0
    whiff = row.get("whiff_pct")
    k_pct = row.get("k_pct")
    for pct in (whiff, k_pct):
        if pct is not None and pct <= 22.0:
            recent += (22.0 - pct) * 0.15
    return recent


def whiff_penalty(row: dict, *, row_high_whiff: Callable[..., bool]) -> float:
    penalty = 0.0
    for pct in (row.get("whiff_pct"), row.get("k_pct")):
        if pct is not None and pct >= 18.0:
            penalty = max(penalty, (pct - 17.0) * 3.0)
    if row_high_whiff(row, for_hits=True):
        penalty += 40.0
    return penalty


def compute_hits_rank(row: dict, *, row_high_whiff: Callable[..., bool]) -> float:
    zone_fit = zone_hits_fit(row)
    contact = contact_hit_form(row)
    matchup_edge = (row.get("split") or 0.0) * 6.0 + (row.get("park_pct") or 0) * 0.08
    return (
        zone_fit
        + contact * 0.55
        + matchup_edge
        + (row.get("score") or 0) * 0.06
        - whiff_penalty(row, row_high_whiff=row_high_whiff)
    )


def annotate_hits_ranks(rows: list[dict], *, row_high_whiff: Callable[..., bool]) -> None:
    for row in rows:
        row["hits_rank"] = compute_hits_rank(row, row_high_whiff=row_high_whiff)
        row["hits_zone_fit"] = zone_hits_fit(row)


def hits_base_pool(candidates: list[dict]) -> list[dict]:
    """Zone-fit-first pool; relax only if we cannot fill 11 legs."""
    def qualifies(r: dict, *, min_zone: float, min_contact: float) -> bool:
        if r.get("split", 0.0) < 0.0:
            return False
        zone = r.get("zone_score") or 0.0
        z_contact = r.get("zone_contact") or 0.0
        has_form = (
            r.get("hr", 0) >= 1
            or r.get("near", 0) >= 1
            or r.get("ev", 0) >= 90
        )
        if zone >= min_zone:
            return True
        if zone >= min_zone - 4 and z_contact >= min_contact:
            return True
        if z_contact >= min_contact + 8 and has_form:
            return True
        return False

    strict = [r for r in candidates if qualifies(r, min_zone=18.0, min_contact=28.0)]
    if len(strict) >= 11:
        return strict

    relaxed = [r for r in candidates if qualifies(r, min_zone=14.0, min_contact=24.0)]
    if len(relaxed) >= 11:
        return relaxed

    fallback = [
        r
        for r in candidates
        if r.get("split", 0.0) >= 0.0
        and (
            (r.get("zone_score") or 0) >= 10
            or r.get("hr", 0) >= 1
            or r.get("near", 0) >= 1
            or r.get("ev", 0) >= 90
        )
    ]
    if fallback:
        return fallback
    return [r for r in candidates if r.get("split", 0.0) >= -0.10]


def select_hits_parlay(
    candidates: list[dict],
    *,
    row_high_whiff: Callable[..., bool],
    avoid_whiff: bool = True,
    n: int = 11,
) -> list[dict]:
    annotate_hits_ranks(candidates, row_high_whiff=row_high_whiff)
    pool = hits_base_pool(candidates)
    if avoid_whiff:
        pool = [r for r in pool if not row_high_whiff(r, for_hits=True)]
    pool = sorted(pool, key=lambda x: (x["hits_rank"], x.get("hits_zone_fit") or 0), reverse=True)
    legs: list[dict] = []
    seen: set[str] = set()
    for row in pool:
        if row["name"] in seen:
            continue
        seen.add(row["name"])
        legs.append(row)
        if len(legs) == n:
            break
    return legs


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

    def can_backfill(row: dict) -> bool:
        if row["name"] in have:
            return False
        if row_high_whiff(row, for_hits=True):
            return False
        if row.get("split", 0.0) < 0.0:
            return False
        zone = row.get("zone_score") or 0.0
        z_contact = row.get("zone_contact") or 0.0
        if zone >= 12.0 or z_contact >= 26.0:
            return True
        return row.get("hr", 0) >= 1 or row.get("near", 0) >= 1 or row.get("ev", 0) >= 90

    backfill_pool = sorted(
        [r for r in candidates if can_backfill(r)],
        key=lambda x: (x.get("hits_rank") or 0, x.get("hits_zone_fit") or 0),
        reverse=True,
    )
    for row in backfill_pool:
        have.add(row["name"])
        legs.append(row)
        if len(legs) == n:
            break
    return legs
