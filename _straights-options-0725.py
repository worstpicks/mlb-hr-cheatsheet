#!/usr/bin/env python3
"""List all Straight of the Day options for 2026-07-25."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
cut = (ROOT / "patch-0725-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
g: dict = {"__file__": str(ROOT / "patch-0725-preview.py"), "__name__": "__main__"}
exec(compile(cut + "\n", "patch-0725-preview.py", "exec"), g)

from goblin_hr_zone_fit import hr_power_form
from note_compact import straight_pick_why

straight_rows = g["straight_rows"]
effective_park_pct = g["effective_park_pct"]
effective_hand_park_pct = g["effective_hand_park_pct"]
straight_o05_pool = g["straight_o05_pool"]
o15_candidates = g["o15_candidates"]
straight_o05 = g["straight_o05"]
straight_o15 = g["straight_o15"]
o05_zone_lane_ok = g["o05_zone_lane_ok"]


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
print("CURRENT STRAIGHTS ON SHEET (7/25)")
print("=" * 110)
for leg, r in [("O0.5", straight_o05), ("O1.5", straight_o15)]:
    primary, why = straight_pick_why(r, leg=("o05" if leg == "O0.5" else "o15"))
    print(f"\n{leg}: {r['name_plain']} vs {r['chip']} ({r['game_key']})")
    print(f"  Primary: {primary}")
    print(f"  Why: {why}")
    print(fmt_row(r))

print("\n" + "=" * 110)
print("ALL O0.5 OPTIONS — strict pool (zone lane + form + split/park/risk gates)")
print("=" * 110)
o05_strict = straight_o05_pool(straight_rows, strict=True)
if not o05_strict:
    print("  (empty)")
for i, r in enumerate(o05_strict, 1):
    tag = " *** CURRENT ***" if r["name"] == straight_o05["name"] else ""
    print(f"{i:2}.{fmt_row(r)}{tag}")

print("\n" + "=" * 110)
print("ALL O0.5 OPTIONS — relaxed (split >= 0, some HR form)")
print("=" * 110)
o05_relaxed = [
    r
    for r in straight_rows
    if r["split"] >= 0.0
    and not (r["split"] <= 0.0 and r["risk"] <= 0.0)
    and (r["hr"] >= 1 or r["near"] >= 2 or r["score"] >= 75)
]
o05_relaxed.sort(key=lambda r: (composite(r), r.get("straight_attack_rank", 0)), reverse=True)
seen: set[str] = set()
n = 0
for r in o05_relaxed:
    if r["name"] in seen:
        continue
    seen.add(r["name"])
    n += 1
    tag = " *** CURRENT ***" if r["name"] == straight_o05["name"] else ""
    lane = " zoneOK" if o05_zone_lane_ok(r) else ""
    print(f"{n:2}.{fmt_row(r)}{lane}{tag}")

print("\n" + "=" * 110)
print("ALL O1.5 OPTIONS — multi-HR pool (hr>=2 near>=2 + gates)")
print("=" * 110)
if not o15_candidates:
    print("  (empty under strict multi-HR gates)")
for i, r in enumerate(o15_candidates, 1):
    tag = " *** CURRENT ***" if r["name"] == straight_o15["name"] else ""
    print(f"{i:2}.{fmt_row(r)}{tag}")

print("\n" + "=" * 110)
print("O1.5 RELAXED — 2HR/2near, score>=78, split>=0.15 (no park/risk gate)")
print("=" * 110)
o15_relaxed = sorted(
    [
        r
        for r in straight_rows
        if r["hr"] >= 2
        and r["near"] >= 2
        and r["score"] >= 78
        and r["split"] >= 0.15
        and not (r["split"] <= 0.0 and r["risk"] <= 0.0)
    ],
    key=lambda r: (r["multi_hr_rank"], r["hr_zone_fit"], r["score"]),
    reverse=True,
)
seen.clear()
n = 0
for r in o15_relaxed:
    if r["name"] in seen:
        continue
    seen.add(r["name"])
    n += 1
    tag = " *** CURRENT ***" if r["name"] == straight_o15["name"] else ""
    print(f"{n:2}.{fmt_row(r)}{tag}")
