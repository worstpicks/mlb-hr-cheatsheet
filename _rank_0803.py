#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

from game_row_enrich import enrich_games_list, plain_name
from goblin_hr_zone_fit import annotate_hr_zone_ranks, hr_rank_sort_key, o05_zone_lane_ok
from hr_score_model import batter_split
from sheet_data import load_pitcher_risk

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-03"

spec = importlib.util.spec_from_file_location("b0803", ROOT / f"build-sheet-{DATE}.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
games = enrich_games_list(build.games, DATE)
risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")

rows = []
for g in games:
    for r in g["rows"]:
        chip = (r.get("chips") or ["vs ?"])[0].replace("vs ", "").strip()
        pr = None
        for k, v in risk.items():
            if v["pitcher"].split()[-1].lower() == chip.lower() or chip.lower() in k:
                pr = v
                break
        hand = r["name"].split("(")[-1].rstrip(")") if "(" in r["name"] else "?"
        split = r.get("split")
        if split is None and pr:
            split = batter_split(hand, pr)
        row = {
            "name": plain_name(r),
            "game": g["title"].split(" - ")[0],
            "chip": chip,
            "emojis": r.get("emojis") or "",
            "score": r.get("score"),
            "hr": r.get("hr") or 0,
            "near": r.get("near") or 0,
            "ev": r.get("ev"),
            "split": split if split is not None else 0,
            "risk": (pr or {}).get("overall", 0),
            "park": g.get("parkPct"),
            "zone": r.get("zoneScore"),
            "zone_score": r.get("zoneScore"),
            "zone_hr": r.get("zoneHr"),
            "zone_barrel": r.get("zoneBarrel"),
            "zone_hard_hit": r.get("zoneHardHit"),
            "fav": "⭐" in (r.get("emojis") or ""),
            "gem": "💎" in (r.get("emojis") or ""),
            "game_key": g["title"].split(" - ")[0],
            "name_plain": plain_name(r),
            "hand_park_pct": r.get("handParkPct") or 0,
            "blast": r.get("blast"),
        }
        rows.append(row)

annotate_hr_zone_ranks(rows, park_pct_fn=lambda r: r.get("park") or 0)

print("=== TITLES ===")
for g in build.games:
    print(g["title"])

print("\n=== TOP O0.5 ===")
o05 = [r for r in rows if o05_zone_lane_ok(r) and r["split"] > 0 and (r["hr"] >= 1 or r["near"] >= 2)]
o05.sort(key=hr_rank_sort_key, reverse=True)
for r in o05[:12]:
    print(
        f"{r['name']:22} vs {r['chip']:14} {r['game']:12} "
        f"HR{r['hr']}/N{r['near']} EV{r['ev']} split{r['split']:+.2f} "
        f"risk{r['risk']:+.2f} park{r['park']} zone{r['zone']} "
        f"{'⭐' if r['fav'] else ''}{'💎' if r['gem'] else ''} atk={r.get('straight_attack_rank',0):.1f}"
    )

print("\n=== TOP O1.5 ===")
o15 = [r for r in rows if r["hr"] >= 2 and r["near"] >= 2 and r["split"] >= 0]
o15.sort(key=lambda r: (r.get("multi_hr_rank", 0), r.get("hr_zone_fit", 0), r["score"] or 0), reverse=True)
for r in o15[:10]:
    print(
        f"{r['name']:22} vs {r['chip']:14} {r['game']:12} "
        f"HR{r['hr']}/N{r['near']} EV{r['ev']} split{r['split']:+.2f} "
        f"risk{r['risk']:+.2f} park{r['park']} zone{r['zone']} "
        f"{'⭐' if r['fav'] else ''}{'💎' if r['gem'] else ''} multi={r.get('multi_hr_rank',0):.1f}"
    )

print("\n=== TOP ATTACK ===")
atk = [r for r in rows if (r["hr"] >= 1 or r["near"] >= 2) and (r["split"] > 0 or r["risk"] >= 0.25)]
atk.sort(key=hr_rank_sort_key, reverse=True)
for r in atk[:15]:
    print(
        f"{r['name']:22} vs {r['chip']:14} HR{r['hr']}/N{r['near']} "
        f"split{r['split']:+.2f} risk{r['risk']:+.2f} zone{r['zone']} "
        f"{'⭐' if r['fav'] else ''}{'💎' if r['gem'] else ''} atk={r.get('straight_attack_rank',0):.1f}"
    )

print("\n=== FAVS ===")
favs = [r for r in rows if r["fav"]]
favs.sort(key=hr_rank_sort_key, reverse=True)
for r in favs:
    print(
        f"{r['name']:22} vs {r['chip']:14} HR{r['hr']}/N{r['near']} "
        f"split{r['split']:+.2f} risk{r['risk']:+.2f} zone{r['zone']} atk={r.get('straight_attack_rank',0):.1f}"
    )
