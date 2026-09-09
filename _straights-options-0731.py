#!/usr/bin/env python3
"""List Straight of the Day + Goblin options for 2026-07-31."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
cut = (ROOT / "patch-0731-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
g: dict = {"__file__": str(ROOT / "patch-0731-preview.py"), "__name__": "__main__"}
exec(compile(cut + "\n", "patch-0731-preview.py", "exec"), g)

from goblin_hr_zone_fit import hr_power_form, hr_rank_sort_key
from note_compact import straight_pick_why

straight_rows = g["straight_rows"]
effective_park_pct = g["effective_park_pct"]
effective_hand_park_pct = g["effective_hand_park_pct"]
straight_o05_pool = g["straight_o05_pool"]
o15_candidates = g["o15_candidates"]
straight_o05 = g["straight_o05"]
straight_o15 = g["straight_o15"]
rows = g["rows"]
FAVS = set(g["FAVS"])


def composite(row: dict) -> float:
    zone = row.get("hr_zone_fit", 0)
    form = hr_power_form(row)
    split = max(row["split"], 0) * 12
    risk = max(row["risk"], 0) * 14
    park = max(effective_hand_park_pct(row), effective_park_pct(row), 0) * 0.65
    return zone * 1.0 + form * 0.85 + split + risk + park


def fmt_row(r: dict) -> str:
    hp = effective_hand_park_pct(r)
    odds = r.get("odds") or "N/A"
    return (
        f"  {r['name_plain']:22} vs {r['chip']:12} ({r['game_key']}) "
        f"| split {r['split']:+.2f} risk {r['risk']:+.2f} park {hp:+3d}% "
        f"| zone {r.get('hr_zone_fit', 0):5.1f} form {hr_power_form(r):4.1f} "
        f"| {r['hr']}HR {r['near']}near {r['ev']:.0f}mph score {r['score']} "
        f"| odds {odds} | comp {composite(r):5.1f}"
    )


print("=" * 110)
print("CURRENT STRAIGHTS ON SHEET (7/31)")
print("=" * 110)
for leg, r in [("O0.5", straight_o05), ("O1.5", straight_o15)]:
    primary, why = straight_pick_why(r, leg=("o05" if leg == "O0.5" else "o15"))
    print(f"\n{leg}: {r['name_plain']} vs {r['chip']} ({r['game_key']})")
    print(f"  Primary: {primary}")
    print(f"  Why: {why}")
    print(fmt_row(r))

print("\n" + "=" * 110)
print("ALL O0.5 OPTIONS — strict pool")
print("=" * 110)
o05_strict = straight_o05_pool(straight_rows, strict=True)
if not o05_strict:
    print("  (empty)")
for i, r in enumerate(o05_strict, 1):
    tag = " *** CURRENT ***" if r["name"] == straight_o05["name"] else ""
    print(f"{i:2}.{fmt_row(r)}{tag}")

print("\n" + "=" * 110)
print("ALL O1.5 CANDIDATES")
print("=" * 110)
cands = o15_candidates(straight_rows)
if not cands:
    print("  (empty — showing multi-HR form rows)")
    cands = [
        r
        for r in straight_rows
        if r["hr"] >= 2 or (r["hr"] >= 1 and r["near"] >= 2)
    ]
    cands.sort(key=lambda r: (r.get("multi_hr_rank", 0), r.get("hr_zone_fit", 0)), reverse=True)
for i, r in enumerate(cands[:15], 1):
    tag = " *** CURRENT ***" if r["name"] == straight_o15["name"] else ""
    print(f"{i:2}.{fmt_row(r)}{tag}")

print("\n" + "=" * 110)
print("TOP HR ZONE RANKS (Goblin / Top5 pool)")
print("=" * 110)
ranked = sorted(rows, key=hr_rank_sort_key, reverse=True)
for i, r in enumerate(ranked[:20], 1):
    star = "⭐" if r["name_plain"] in FAVS or r.get("name", "").split(" (")[0] in FAVS else ""
    print(
        f"{i:2}. {r['name_plain']:22} vs {r['chip']:12} {star:2} "
        f"zone {r.get('hr_zone_fit', 0):5.1f} split {r['split']:+.2f} "
        f"risk {r['risk']:+.2f} park {effective_hand_park_pct(r):+3d}% "
        f"{r['hr']}HR/{r['near']}near score {r['score']}"
    )

print("\nFAVORITES with ranks:")
for r in ranked:
    if r["name_plain"] in FAVS or any(f in r.get("name", "") for f in FAVS):
        print(fmt_row(r))
