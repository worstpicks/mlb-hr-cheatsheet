#!/usr/bin/env python3
"""Rank 8/5 O0.5 / O1.5 / Goblin candidates for judgment locks."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from game_row_enrich import enrich_games_list, row_hand_park_fields
from goblin_hr_zone_fit import annotate_hr_zone_ranks, hr_rank_sort_key, o05_zone_lane_ok
from hr_score_model import batter_split
from sheet_data import load_pitcher_risk, resolve_pitcher

ROOT = Path(".")
spec = importlib.util.spec_from_file_location("b", "build-sheet-2026-08-10.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
risk = load_pitcher_risk(ROOT / "data/hr-targets-overall-2026-08-10.csv")
rows = []
for g in enrich_games_list(b.games, "2026-08-10"):
    gkey = g.get("key") or g["title"].split(" - ")[0]
    park_ctx = {
        "park_pct": g.get("parkPct"),
        "park_lhb_pct": g.get("parkLhbPct"),
        "park_rhb_pct": g.get("parkRhbPct"),
    }
    for r in g["rows"]:
        chip = (r.get("chips") or ["vs ?"])[0].replace("vs ", "").strip()
        hand = "L" if "(L)" in r["name"] else ("S" if "(S)" in r["name"] else "R")
        sp = resolve_pitcher(risk, chip)
        split = batter_split(hand, sp) if sp else 0.0
        note = r.get("note") or ""
        hr = int(m.group(1)) if (m := re.search(r"(\d+)\s+HR", note)) else 0
        near = int(m.group(1)) if (m := re.search(r"(\d+)\s+near", note, re.I)) else 0
        em = "".join(r.get("emojis") or [])
        rows.append(
            {
                "name": r["name"].rsplit(" (", 1)[0],
                "game_key": gkey,
                "chip": chip,
                "hand": hand,
                "split": split,
                "risk": sp["overall"] if sp else 0,
                "park_pct": g.get("parkPct") or 0,
                "hr": hr,
                "near": near,
                "ev": 0,
                "barrel": 0,
                "score": r.get("score") or 0,
                "zone_score": r.get("zoneScore") or 0,
                "zone_contact": r.get("zoneContact"),
                "zone_barrel": r.get("zoneBarrel"),
                "zone_hr": r.get("zoneHr"),
                "zone_hard_hit": r.get("zoneHardHit"),
                "rank": r.get("score") or 0,
                "fav": "⭐" in em,
                "gem": "💎" in em,
                **row_hand_park_fields(hand, park_ctx),
            }
        )
annotate_hr_zone_ranks(
    rows, park_pct_fn=lambda r: int(r.get("hand_park_pct") or r.get("park_pct") or 0)
)

print("BUMS:", sorted([(k, v["overall"]) for k, v in risk.items() if v["overall"] >= 0.95], key=lambda x: -x[1]))
print("\nBEST O0.5:")
o05 = [
    r
    for r in rows
    if o05_zone_lane_ok(r) and r["split"] >= 0 and not (r["split"] <= 0 and r["risk"] <= 0)
]
o05.sort(key=hr_rank_sort_key, reverse=True)
for r in o05[:15]:
    mark = ("⭐" if r["fav"] else "") + ("💎" if r["gem"] else "")
    print(
        f"  {r['name']:22}{mark:3} vs {r['chip']:18} atk={r['straight_attack_rank']:5.1f} "
        f"z={r['hr_zone_fit']:5.1f} split={r['split']:+.2f} risk={r['risk']:+.2f} "
        f"park={r['park_pct']:+d} HR={r['hr']}/{r['near']} {r['game_key']}"
    )

print("\nBEST O1.5:")
o15 = sorted(
    [r for r in rows if r["hr"] >= 2 and r["near"] >= 2 and r["split"] >= 0],
    key=lambda r: (r["multi_hr_rank"], r["hr_zone_fit"]),
    reverse=True,
)
for r in o15[:12]:
    mark = ("⭐" if r["fav"] else "") + ("💎" if r["gem"] else "")
    print(
        f"  {r['name']:22}{mark:3} vs {r['chip']:18} multi={r['multi_hr_rank']:5.1f} "
        f"split={r['split']:+.2f} risk={r['risk']:+.2f} park={r['park_pct']:+d} "
        f"HR={r['hr']}/{r['near']} {r['game_key']}"
    )

print("\nTOP FAVS:")
for r in sorted([r for r in rows if r["fav"]], key=hr_rank_sort_key, reverse=True)[:15]:
    print(
        f"  {r['name']:22} vs {r['chip']:18} atk={r['straight_attack_rank']:5.1f} "
        f"split={r['split']:+.2f} risk={r['risk']:+.2f} park={r['park_pct']:+d} HR={r['hr']}/{r['near']}"
    )

print("\nPARK coverage:")
for g in enrich_games_list(b.games, "2026-08-10"):
    meta = g.get("gameMeta") or ""
    ok = "Park" in meta and "LHB" in meta and meta.count("pitcher-meta") == 2
    print(("OK" if ok else "BAD"), g["title"][:70], "park", g.get("parkPct"))
