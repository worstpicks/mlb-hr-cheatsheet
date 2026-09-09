#!/usr/bin/env python3
"""Custom 3-leg: split + park + attack SP + form + green/yellow Boom%."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

BOOM_CONTACT_W = {
    "barrelPct": 26,
    "blastPct": 20,
    "hardHitPct": 18,
    "airPct": 16,
    "fbPct": 14,
    "solidContactPct": 6,
}
BOOM_W = {"boomContact": 55, "mixPlus": 25, "hrFormPct": 20}
HR_FORM_W = {
    "hrLuckDiff": 30,
    "hrProximity": 25,
    "rollingHrBoost": 15,
    "mixPlus": 20,
    "hrContactShape": 10,
}


def percentile_rank(values: list[float], value: float, higher_better: bool) -> float:
    if not values:
        return 50.0
    if len(values) == 1:
        return 50.0
    sorted_v = sorted(values)
    if higher_better:
        below = sum(1 for v in sorted_v if v < value)
        equal = sum(1 for v in sorted_v if v == value)
        return ((below + 0.5 * equal) / len(sorted_v)) * 100
    above = sum(1 for v in sorted_v if v > value)
    equal = sum(1 for v in sorted_v if v == value)
    return ((above + 0.5 * equal) / len(sorted_v)) * 100


def boom_contact(stats: dict) -> float | None:
    air = stats.get("airPct")
    if air is None and stats.get("fbPct") is not None and stats.get("ldPct") is not None:
        air = float(stats["fbPct"]) + float(stats["ldPct"])
    parts = {
        "barrelPct": stats.get("barrelPct"),
        "blastPct": stats.get("blastPct"),
        "hardHitPct": stats.get("hardHitPct"),
        "airPct": air,
        "fbPct": stats.get("fbPct"),
        "solidContactPct": stats.get("solidContactPct"),
    }
    wsum = 0.0
    total = 0.0
    for k, w in BOOM_CONTACT_W.items():
        v = parts.get(k)
        if v is None:
            continue
        wsum += float(v) * w
        total += w
    return wsum / total if total else None


def hr_proximity(stats: dict) -> float | None:
    near = stats.get("nearHr")
    mostly = stats.get("mostlyGone")
    if near is None and mostly is None:
        return None
    return (float(near or 0)) + (float(mostly or 0)) * 0.75


def hr_contact_shape(stats: dict) -> float | None:
    air = stats.get("airPct")
    if air is None and stats.get("fbPct") is not None and stats.get("ldPct") is not None:
        air = float(stats["fbPct"]) + float(stats["ldPct"])
    pull = stats.get("pullPct")
    if air is None and pull is None:
        return None
    air_part = max(float(air) - 38, 0) if air is not None else 0
    pull_part = max(float(pull) - 38, 0) if pull is not None else 0
    if air is None:
        return pull_part
    if pull is None:
        return air_part
    return air_part * 0.6 + pull_part * 0.4


def rolling_hr_boost(stats: dict) -> float | None:
    hr = float(stats.get("hr") or 0)
    pa = float(stats.get("pa") or 0)
    if pa <= 0:
        return None
    iso = stats.get("iso")
    if iso is not None:
        return float(iso) * 0.65 + (hr / pa) * 0.35
    slg = stats.get("slg")
    if slg is not None:
        est_iso = max(float(slg) - 0.22, 0)
        return est_iso * 0.65 + (hr / pa) * 0.35
    return hr / pa


def score_from_pools(parts: list[tuple[str, float | None, float]], pools: dict) -> float | None:
    weighted = 0.0
    total = 0.0
    for key, val, weight in parts:
        if val is None or not weight:
            continue
        pool = pools.get(key) or []
        if not pool:
            continue
        pct = percentile_rank(pool, float(val), True)
        weighted += pct * weight
        total += weight
    return round(weighted / total, 1) if total else None


def boom_tone(pct: float | None) -> str | None:
    if pct is None:
        return None
    if pct >= 66:
        return "green"
    if pct <= 33:
        return "red"
    return "yellow"


def norm_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def collect_research_entries(data: dict) -> list[dict]:
    out = []
    for gi, game in enumerate(data.get("games") or []):
        matchup = game.get("matchup", "")
        park = game.get("parkHrPct")
        for side, opp_key in (("awayLineup", "homePitcher"), ("homeLineup", "awayPitcher")):
            pitcher = game.get(opp_key) or {}
            for row in game.get(side) or []:
                stats = dict(row.get("stats") or {})
                pf = (data.get("propfinder_lookup") or {}).get(norm_name(row.get("name", "")))
                if pf:
                    for k in ("nearHr", "hr", "blastPct", "mostlyGone", "solidContactPct"):
                        if stats.get(k) is None and pf.get(k) is not None:
                            stats[k] = pf[k]
                out.append(
                    {
                        "name": row.get("name"),
                        "id": row.get("id"),
                        "hand": row.get("hand"),
                        "stats": stats,
                        "mixPlus": stats.get("mixPlus"),
                        "pitcher": pitcher.get("name", "?"),
                        "pitcher_risk": (pitcher.get("stats") or {}).get("hrRisk"),
                        "game": matchup,
                        "park": park if park is not None else (row.get("hrProp") or {}).get("parkPct"),
                        "game_idx": gi,
                    }
                )
    return out


def main() -> None:
    cut = (ROOT / "patch-0707-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
    g: dict = {"__file__": str(ROOT / "patch-0707-preview.py"), "__name__": "__main__"}
    exec(compile(cut + "\n", "patch-0707-preview.py", "exec"), g)

    sheet_rows = g["rows"]
    sheet_names = {norm_name(r["name_plain"]) for r in sheet_rows}
    sheet_by_name = {norm_name(r["name_plain"]): r for r in sheet_rows}

    research = json.loads((ROOT / "preview" / "data" / "research-2026-07-07.json").read_text(encoding="utf-8"))
    entries = collect_research_entries(research)

    # Build pools across full slate (matches research tab)
    boom_pools: dict[str, list[float]] = {"boomContact": [], "mixPlus": [], "hrFormPct": []}
    form_pools: dict[str, list[float]] = {
        "hrLuckDiff": [],
        "hrProximity": [],
        "rollingHrBoost": [],
        "mixPlus": [],
        "hrContactShape": [],
    }
    for e in entries:
        s = e["stats"]
        bc = boom_contact(s)
        if bc is not None:
            boom_pools["boomContact"].append(bc)
        mix = e["mixPlus"]
        if mix is not None:
            boom_pools["mixPlus"].append(float(mix))
            form_pools["mixPlus"].append(float(mix))
        prox = hr_proximity(s)
        if prox is not None:
            form_pools["hrProximity"].append(prox)
        shape = hr_contact_shape(s)
        if shape is not None:
            form_pools["hrContactShape"].append(shape)
        roll = rolling_hr_boost(s)
        if roll is not None:
            form_pools["rollingHrBoost"].append(roll)
        if s.get("hrLuckDiff") is not None:
            form_pools["hrLuckDiff"].append(float(s["hrLuckDiff"]))

    scored: list[dict] = []
    for e in entries:
        key = norm_name(e["name"] or "")
        if key not in sheet_names:
            continue
        s = e["stats"]
        mix = e["mixPlus"]
        hr_form = score_from_pools(
            [
                ("hrLuckDiff", s.get("hrLuckDiff"), HR_FORM_W["hrLuckDiff"]),
                ("hrProximity", hr_proximity(s), HR_FORM_W["hrProximity"]),
                ("rollingHrBoost", rolling_hr_boost(s), HR_FORM_W["rollingHrBoost"]),
                ("mixPlus", mix, HR_FORM_W["mixPlus"]),
                ("hrContactShape", hr_contact_shape(s), HR_FORM_W["hrContactShape"]),
            ],
            form_pools,
        )
        boom = score_from_pools(
            [
                ("boomContact", boom_contact(s), BOOM_W["boomContact"]),
                ("mixPlus", mix, BOOM_W["mixPlus"]),
                ("hrFormPct", hr_form, BOOM_W["hrFormPct"]),
            ],
            boom_pools,
        )
        tone = boom_tone(boom)
        if tone not in ("green", "yellow"):
            continue

        sr = sheet_by_name[key]
        if sr["hr"] < 1 and sr["near"] < 2:
            continue
        if sr["split"] <= 0.0 and sr["risk"] <= 0.0:
            continue
        if sr["split"] < 0.15 and sr["risk"] < 0.50:
            continue

        park = g["effective_hand_park_pct"](sr)
        attack = max(sr["split"], 0) * 12 + max(sr["risk"], 0) * 14 + max(park, sr["park_pct"], 0) * 0.65
        form_pts = sr["hr"] * 4 + sr["near"] * 2 + (hr_form or 0) * 0.15
        composite = attack + (boom or 0) * 0.85 + form_pts

        scored.append(
            {
                **sr,
                "boom": boom,
                "boom_tone": tone,
                "hr_form_pct": hr_form,
                "mix_plus": mix,
                "research_pitcher": e["pitcher"],
                "composite": composite,
                "attack": attack,
            }
        )

    scored.sort(key=lambda r: (r["composite"], r["boom"] or 0, r["attack"]), reverse=True)

    print("=" * 100)
    print("TOP CANDIDATES (Boom green/yellow + split/park/attack + form)")
    print("=" * 100)
    for i, r in enumerate(scored[:20], 1):
        print(
            f"{i:2}. {r['name_plain']:22} {r['game_key']:12} vs {r['chip']:12} "
            f"| split {r['split']:+.2f} risk {r['risk']:+.2f} park {g['effective_hand_park_pct'](r):+3d}% "
            f"| Boom {r['boom']:.0f} ({r['boom_tone']}) HRform {r['hr_form_pct']} mix {r['mix_plus']} "
            f"| {r['hr']}HR {r['near']}near comp {r['composite']:.1f}"
        )

    picked: list[dict] = []
    seen_games: set[str] = set()
    for r in scored:
        if r["game_key"] in seen_games:
            continue
        picked.append(r)
        seen_games.add(r["game_key"])
        if len(picked) == 3:
            break

    print("\n" + "=" * 100)
    print("RECOMMENDED 3-LEG HR PARLAY")
    print("=" * 100)
    for i, r in enumerate(picked, 1):
        print(f"\nLeg {i}: {r['name_plain']} — Over 0.5 HR")
        print(f"  Game: {r['game_key']} vs {r['chip']}")
        print(f"  Split {r['split']:+.2f} · HR risk {r['risk']:+.2f} · Park {g['effective_hand_park_pct'](r):+d}%")
        print(f"  Form: {r['hr']} HR, {r['near']} near-HR · {r['ev']:.1f} mph EV")
        print(f"  Boom% {r['boom']:.0f} ({r['boom_tone']}) · Mix+ {r['mix_plus']} · HR Form% {r['hr_form_pct']}")
        print(f"  Odds: {r['odds']}")

    print("\nGambly lines:")
    for r in picked:
        print(f"  {r['name_plain']} - Over 0.5 homerun")


if __name__ == "__main__":
    main()
