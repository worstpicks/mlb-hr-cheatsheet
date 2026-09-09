#!/usr/bin/env python3
"""Diagnose hits parlay coverage on current 7/10 slate."""
from pathlib import Path

from goblin_hits_parlay import (
    compute_hits_rank,
    hits_base_pool,
    select_hits_parlay,
    fill_hits_parlay,
    zone_hits_fit,
    contact_hit_form,
    whiff_penalty,
)

ROOT = Path(__file__).resolve().parent
cut = (ROOT / "patch-0710-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
g: dict = {"__file__": str(ROOT / "patch-0710-preview.py"), "__name__": "__main__"}
exec(compile(cut + "\n", "patch-0710-preview.py", "exec"), g)

rows = g["rows"]
whiff = g["row_high_whiff"]
legs = g["hits_parlay_legs"]

print("total rows", len(rows))
print("current legs", len(legs), [r["name_plain"] for r in legs])

pool = hits_base_pool(rows)
print("base pool", len(pool))
pool_no_whiff = [r for r in pool if not whiff(r, for_hits=True)]
print("base pool after avoid_whiff", len(pool_no_whiff))

high_whiff = [r for r in rows if whiff(r, for_hits=True)]
print("high whiff count", len(high_whiff))
neg_split = [r for r in rows if r.get("split", 0) < 0]
print("neg split", len(neg_split))

print("\nALL ROWS ranked by hits_rank:")
ranked = sorted(rows, key=lambda r: -compute_hits_rank(r, row_high_whiff=whiff))
for i, r in enumerate(ranked, 1):
    in_leg = r["name"] in {x["name"] for x in legs}
    hw = whiff(r, for_hits=True)
    mark = " ***" if in_leg else ""
    print(
        f"{i:2}. {r['name_plain']:22} split={r['split']:+.2f} "
        f"zone={r.get('zone_score') or 0:5.1f} zC={r.get('zone_contact') or 0:5.1f} "
        f"whiff={r.get('whiff_pct')} k={r.get('k_pct')} "
        f"hw={hw} form={contact_hit_form(r):5.1f} "
        f"rank={compute_hits_rank(r, row_high_whiff=whiff):6.1f} "
        f"pen={whiff_penalty(r, row_high_whiff=whiff):5.1f}{mark}"
    )
