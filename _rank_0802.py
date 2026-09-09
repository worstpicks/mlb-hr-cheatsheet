#!/usr/bin/env python3
"""Rank 8/2 straight / goblin candidates from enriched rows."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from game_row_enrich import enrich_games_list, plain_name
from goblin_hr_zone_fit import (
    annotate_hr_zone_ranks,
    hr_rank_sort_key,
    o05_zone_lane_ok,
    weather_play_rank,
)
from sheet_data import load_pitcher_risk

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-02"

spec = importlib.util.spec_from_file_location("b0802", ROOT / f"build-sheet-{DATE}.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
games = enrich_games_list(build.games, DATE)
risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")

rows = []
for g in games:
    park = g.get("parkPct")
    for r in g["rows"]:
        chip = (r.get("chips") or ["vs ?"])[0].replace("vs ", "").strip()
        # resolve pitcher risk
        pr = None
        for k, v in risk.items():
            if chip.lower() in k or k.split()[-1] == chip.lower() or v["pitcher"].split()[-1].lower() == chip.lower():
                pr = v
                break
        hand = r["name"].split("(")[-1].rstrip(")") if "(" in r["name"] else "?"
        split = r.get("split")
        if split is None and pr:
            from hr_score_model import batter_split

            split = batter_split(hand, pr)
        row = {
            "name": plain_name(r),
            "full": r["name"],
            "game": g["title"].split(" - ")[0],
            "chip": chip,
            "emojis": r.get("emojis") or "",
            "odds": r.get("odds"),
            "score": r.get("score"),
            "hr": r.get("hr") or 0,
            "near": r.get("near") or 0,
            "ev": r.get("ev"),
            "barrel": r.get("barrel"),
            "split": split if split is not None else r.get("split") or 0,
            "risk": (pr or {}).get("overall", r.get("risk") or 0),
            "park": park,
            "park_lhb": g.get("parkLhbPct"),
            "park_rhb": g.get("parkRhbPct"),
            "zone": r.get("zoneScore"),
            "zone_hr": r.get("zoneHr"),
            "zone_barrel": r.get("zoneBarrel"),
            "zone_hard_hit": r.get("zoneHardHit"),
            "zone_score": r.get("zoneScore"),
            "hand": hand,
            "fav": "⭐" in (r.get("emojis") or ""),
            "gem": "💎" in (r.get("emojis") or ""),
            "game_key": g["title"].split(" - ")[0],
            "name_plain": plain_name(r),
        }
        # fields expected by annotate
        row.update(
            {
                "blast": r.get("blast"),
                "formTrend": r.get("formTrend"),
                "hand_park_pct": r.get("handParkPct") or 0,
            }
        )
        rows.append(row)

# Use patch's effective park via enrich fields already on rows when possible
annotate_hr_zone_ranks(rows, park_pct_fn=lambda r: r.get("park") or 0)

print("=== TOP O0.5 (zone lane ok) ===")
o05 = [r for r in rows if o05_zone_lane_ok(r) and r["split"] > 0]
o05.sort(key=hr_rank_sort_key, reverse=True)
for r in o05[:15]:
    print(
        f"{r['name']:22} vs {r['chip']:12} {r['game']:12} "
        f"HR{r['hr']}/N{r['near']} EV{r['ev']} split{r['split']:+.2f} "
        f"risk{r['risk']:+.2f} park{r['park']} zone{r['zone']} "
        f"{'⭐' if r['fav'] else ''}{'💎' if r['gem'] else ''} "
        f"atk={r.get('straight_attack_rank',0):.1f} zf={r.get('hr_zone_fit',0):.1f}"
    )

print("\n=== TOP O1.5 multi ===")
o15 = [r for r in rows if r["hr"] >= 2 and r["near"] >= 2 and r["split"] >= 0]
o15.sort(key=lambda r: (r.get("multi_hr_rank", 0), r.get("hr_zone_fit", 0), r["score"] or 0), reverse=True)
for r in o15[:12]:
    print(
        f"{r['name']:22} vs {r['chip']:12} {r['game']:12} "
        f"HR{r['hr']}/N{r['near']} EV{r['ev']} split{r['split']:+.2f} "
        f"risk{r['risk']:+.2f} park{r['park']} zone{r['zone']} "
        f"{'⭐' if r['fav'] else ''}{'💎' if r['gem'] else ''} "
        f"multi={r.get('multi_hr_rank',0):.1f}"
    )

print("\n=== TOP HR attack (goblin pool) ===")
atk = [r for r in rows if (r["hr"] >= 1 or r["near"] >= 2) and (r["split"] > 0 or r["risk"] >= 0.25)]
atk.sort(key=hr_rank_sort_key, reverse=True)
for r in atk[:20]:
    print(
        f"{r['name']:22} vs {r['chip']:12} {r['game']:12} "
        f"HR{r['hr']}/N{r['near']} EV{r['ev']} split{r['split']:+.2f} "
        f"risk{r['risk']:+.2f} zone{r['zone']} "
        f"{'⭐' if r['fav'] else ''}{'💎' if r['gem'] else ''} "
        f"atk={r.get('straight_attack_rank',0):.1f}"
    )

print("\n=== FAVORITES ranked ===")
favs = [r for r in rows if r["fav"]]
favs.sort(key=hr_rank_sort_key, reverse=True)
for r in favs[:15]:
    print(
        f"{r['name']:22} vs {r['chip']:12} HR{r['hr']}/N{r['near']} "
        f"split{r['split']:+.2f} risk{r['risk']:+.2f} zone{r['zone']} "
        f"atk={r.get('straight_attack_rank',0):.1f}"
    )

print("\n=== TITLES / LHP / BUMS ===")
for g in build.games:
    print(g["title"])
