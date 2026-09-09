#!/usr/bin/env python3
"""HR Due / Overdue (💤) — all six rules must pass."""
from __future__ import annotations

import re
from typing import Any

MLB_BARREL_MEDIAN = 7.0
MLB_HR9_AVG = 1.3
HR_LA_MIN = 18.0
HR_LA_MAX = 32.0
OVERDUE_EMOJI = "💤"

# 2026 season HR/9 (full-season; split rates in notes may be higher)
PITCHER_HR9: dict[str, float] = {
    "mcclanahan": 1.31,
    "rogers": 1.31,
    "lodolo": 2.62,
    "painter": 2.89,
    "ritchie": 1.66,
    "meyer": 0.76,
    "cecconi": 1.60,
    "valdez": 1.60,
    "scott": 0.57,
    "irvin": 1.27,
    "corbin": 0.79,
    "weathers": 1.20,
    "imai": 1.42,
    "rojas": 0.00,
    "gray": 1.06,
    "lugo": 0.17,
    "sproat": 2.00,
    "imanaga": 0.83,
    "quintana": 1.32,
    "gore": 1.12,
    "ginn": 1.04,
    "urena": 0.66,
    "schultz": 0.61,
    "woo": 1.02,
    "yamamoto": 1.44,
    "king": 1.44,
    "ray": 1.79,
    "gallen": 1.26,
}


def park_hr_factor(description: str) -> float | None:
    if not description:
        return None
    m = re.search(r"([+-]?\d+)%\s*HR\s*row", description, re.I)
    if m:
        return 1.0 + int(m.group(1)) / 100.0
    if re.search(r"flat HR row|0%\s*HR", description, re.I):
        return 1.0
    return None


def opponent_key(row: dict[str, Any]) -> str:
    chips = row.get("chips") or []
    if not chips:
        return ""
    return re.sub(r"^vs\s+", "", chips[0], flags=re.I).strip().lower()


def pitcher_hr9_for_row(row: dict[str, Any], game: dict[str, Any]) -> float | None:
    key = opponent_key(row)
    if not key:
        return None
    note = row.get("note") or ""
    desc = game.get("description") or ""
    title = game.get("title") or ""
    rates: list[float] = []
    if key in PITCHER_HR9 and PITCHER_HR9[key] > 0:
        rates.append(PITCHER_HR9[key])
    for text in (note, desc, title):
        pat = re.compile(
            rf"{re.escape(key)}[^.\d]{{0,60}}?(\d+\.\d+)\s*HR/9",
            re.I,
        )
        m = pat.search(text)
        if m:
            rates.append(float(m.group(1)))
        m2 = re.search(r"(\d+\.\d+)\s*HR/9[^.\d]{0,40}" + re.escape(key), text, re.I)
        if m2:
            rates.append(float(m2.group(1)))
    return max(rates) if rates else None


def parse_note_metrics(note: str) -> dict[str, float | int | None]:
    if not note:
        return {"hr": 0, "near_hr": 0, "barrel_pct": None, "pull_air": None, "la_avg": None}
    hr = 0
    near_hr = 0
    barrel_pct = None
    pull_air = None
    la_avg = None

    for m in re.finditer(r"(\d+)\s+HR\b", note, re.I):
        hr = max(hr, int(m.group(1)))
    for m in re.finditer(r"(\d+)\s+near[- ]?HR", note, re.I):
        near_hr = max(near_hr, int(m.group(1)))
    bm = re.search(r"(\d+(?:\.\d+)?)%\s*barrels", note, re.I)
    if bm:
        barrel_pct = float(bm.group(1))
    pm = re.search(r"(\d+(?:\.\d+)?)%\s*pull-air", note, re.I)
    if pm:
        pull_air = float(pm.group(1))
    lam = re.search(r"(\d+(?:\.\d+)?)°\s*(?:avg\s*)?LA", note, re.I)
    if lam:
        la_avg = float(lam.group(1))

    return {
        "hr": hr,
        "near_hr": near_hr,
        "barrel_pct": barrel_pct,
        "pull_air": pull_air,
        "la_avg": la_avg,
    }


def merge_due_stats(row: dict[str, Any]) -> dict[str, float | int | None]:
    base = parse_note_metrics(row.get("note") or "")
    due = row.get("due") or {}
    for k, v in due.items():
        if v is not None and not str(k).startswith("_"):
            base[k] = v
    return base


def rule_barrel_last_3(stats: dict[str, Any]) -> bool:
    if stats.get("barrels_l3") is not None:
        return int(stats["barrels_l3"]) >= 1
    hr = int(stats.get("hr") or 0)
    near = int(stats.get("near_hr") or 0)
    barrel_pct = stats.get("barrel_pct")
    if near >= 1:
        return True
    if hr >= 1 and barrel_pct is not None and float(barrel_pct) >= 8.0:
        return True
    return False


def rule_barrel_pct_median(stats: dict[str, Any]) -> bool:
    bp = stats.get("barrel_pct")
    return bp is not None and float(bp) >= MLB_BARREL_MEDIAN


def rule_drought_z(stats: dict[str, Any]) -> bool:
    z = stats.get("drought_z")
    if z is not None:
        return float(z) > 0
    hr = int(stats.get("hr") or 0)
    near = int(stats.get("near_hr") or 0)
    bips = stats.get("bips_since_hr")
    if hr > 0:
        return False
    if bips is not None and float(bips) > 0:
        median_gap = stats.get("median_hr_gap")
        if median_gap is not None and float(bips) > float(median_gap):
            return True
    if near >= 2:
        return True
    if near >= 1 and stats.get("barrel_pct") is not None and float(stats["barrel_pct"]) >= MLB_BARREL_MEDIAN:
        return True
    return False


def rule_launch_angle_hr_range(stats: dict[str, Any]) -> bool:
    la7 = stats.get("la_last7")
    if la7 is not None:
        return HR_LA_MIN <= float(la7) <= HR_LA_MAX
    la = stats.get("la_avg")
    if la is not None:
        return HR_LA_MIN <= float(la) <= HR_LA_MAX
    la_ss = stats.get("la_ss_pct")
    if la_ss is not None and float(la_ss) >= 18.0:
        return True
    pull = stats.get("pull_air")
    if pull is not None and float(pull) >= 18.0:
        return True
    return False


def rule_hr_friendly_pitcher(hr9: float | None) -> bool:
    return hr9 is not None and float(hr9) > MLB_HR9_AVG


def rule_hr_friendly_park(factor: float | None) -> bool:
    return factor is not None and float(factor) > 1.0


def evaluate_overdue(row: dict[str, Any], game: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    stats = merge_due_stats(row)
    park = park_hr_factor(game.get("description") or "")
    hr9 = pitcher_hr9_for_row(row, game)
    checks = {
        "barrel_l3": rule_barrel_last_3(stats),
        "barrel_pct": rule_barrel_pct_median(stats),
        "drought_z": rule_drought_z(stats),
        "launch_angle": rule_launch_angle_hr_range(stats),
        "pitcher_hr9": rule_hr_friendly_pitcher(hr9),
        "park_factor": rule_hr_friendly_park(park),
    }
    return all(checks.values()), checks


def infer_due_from_context(row: dict[str, Any], game: dict[str, Any]) -> dict[str, Any]:
    """Fill due fields from sheet notes when PropFinder export is not on file."""
    stats = parse_note_metrics(row.get("note") or "")
    due: dict[str, Any] = {}
    park = park_hr_factor(game.get("description") or "")
    hr9 = pitcher_hr9_for_row(row, game)
    if park is None or park <= 1.0 or hr9 is None or hr9 <= MLB_HR9_AVG:
        return due

    hr = int(stats.get("hr") or 0)
    near = int(stats.get("near_hr") or 0)
    barrel_pct = stats.get("barrel_pct")
    pull_air = stats.get("pull_air")

    if near >= 1 or (hr >= 1 and barrel_pct is not None and float(barrel_pct) >= 8.0):
        due["barrels_l3"] = 1

    if barrel_pct is not None:
        due["barrel_pct"] = barrel_pct

    if hr == 0 and near >= 1:
        due["drought_z"] = round(0.2 + 0.12 * near, 2)
    elif hr == 0 and near == 0 and barrel_pct is not None and float(barrel_pct) >= MLB_BARREL_MEDIAN:
        due["drought_z"] = 0.35

    if pull_air is not None and float(pull_air) >= 18.0:
        due["la_last7"] = round(min(HR_LA_MAX, max(HR_LA_MIN, 17.5 + float(pull_air) * 0.15)), 1)
        due["la_ss_pct"] = float(pull_air)
    elif barrel_pct is not None and float(barrel_pct) >= 18.0:
        due["la_last7"] = 21.0
        due["la_ss_pct"] = float(barrel_pct)

    return due


def apply_inferred_due(row: dict[str, Any], game: dict[str, Any]) -> None:
    inferred = infer_due_from_context(row, game)
    existing = row.get("due") or {}
    for k, v in inferred.items():
        if k not in existing or existing.get(k) is None:
            existing[k] = v
    if existing:
        row["due"] = existing


def tag_row_overdue(row: dict[str, Any], game: dict[str, Any]) -> bool:
    ok, _ = evaluate_overdue(row, game)
    if ok:
        row["overdue"] = True
        em = row.get("emojis") or ""
        if OVERDUE_EMOJI not in em:
            row["emojis"] = f"{em} {OVERDUE_EMOJI}".strip()
    else:
        row.pop("overdue", None)
    return ok


def tag_games_overdue(games: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []
    for game in games:
        for row in game.get("rows") or []:
            if tag_row_overdue(row, game):
                names.append(row["name"])
    return names
