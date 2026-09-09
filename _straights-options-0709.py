#!/usr/bin/env python3
"""List all straight options for 2026-07-06."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
cut = (ROOT / "patch-0709-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
g: dict = {"__file__": str(ROOT / "patch-0709-preview.py"), "__name__": "__main__"}
exec(compile(cut + "\n", "patch-0709-preview.py", "exec"), g)

from goblin_hr_zone_fit import hr_power_form
from note_compact import straight_pick_why

straight_rows = g["straight_rows"]
effective_park_pct = g["effective_park_pct"]
effective_hand_park_pct = g["effective_hand_park_pct"]
straight_o05_pool = g["straight_o05_pool"]
o15_candidates = g["o15_candidates"]
straight_o05 = g["straight_o05"]
straight_o15 = g["straight_o15"]


def composite(row: dict) -> float:
    zone = row.get("hr_zone_fit", 0)
    form = hr_power_form(row)
    split = max(row["split"], 0) * 12
    risk = max(row["risk"], 0) * 14
    park = max(effective_hand_park_pct(row), effective_park_pct(row), 0) * 0.65
    return zone * 1.0 + form * 0.85 + split + risk + park


def fmt_row(r: dict) -> str:
    hp = effective_hand_park_pct(r)
    comp = composite(r)
    odds = r.get("odds") or "N/A"
    return (
        f"  {r['name_plain']:22} {r['game_key']:12} vs {r['chip']:12} "
        f"| split {r['split']:+.2f} risk {r['risk']:+.2f} park {hp:+3d}% "
        f"| zone {r.get('hr_zone_fit', 0):5.1f} form {hr_power_form(r):4.1f} "
        f"| {r['hr']}HR {r['near']}near {r['ev']:.0f}mph score {r['score']} "
        f"| comp {comp:5.1f} | {odds}"
    )


print("=" * 100)
print("CURRENT STRAIGHTS ON SHEET (7/9)")
print("=" * 100)
for leg, r in [("O0.5", straight_o05), ("O1.5", straight_o15)]:
    primary, why = straight_pick_why(r, leg=leg.lower().replace(".", ""))
    print(f"\n{leg}: {r['name_plain']} vs {r['chip']} ({r['game_key']})")
    print(f"  Primary: {primary}")
    print(f"  Why: {why}")
    print(fmt_row(r))

print("\n" + "=" * 100)
print("ALL O0.5 OPTIONS — strict pool")
print("=" * 100)
o05_strict = straight_o05_pool(straight_rows, strict=True)
for i, r in enumerate(o05_strict, 1):
    tag = " *** CURRENT ***" if r["name"] == straight_o05["name"] else ""
    print(f"{i:2}.{fmt_row(r)}{tag}")

print("\n" + "=" * 100)
print("ALL O0.5 OPTIONS — relaxed pool")
print("=" * 100)
o05_relaxed = [
    r
    for r in straight_rows
    if r["split"] >= 0.0
    and not (r["split"] <= 0.0 and r["risk"] <= 0.0)
    and (r["hr"] >= 1 or r["near"] >= 2)
]
o05_relaxed.sort(key=lambda r: (composite(r), r.get("straight_attack_rank", 0)), reverse=True)
seen: set[str] = set()
for i, r in enumerate(o05_relaxed, 1):
    if r["name"] in seen:
        continue
    seen.add(r["name"])
    tag = ""
    if r["name"] == straight_o05["name"]:
        tag = " *** CURRENT ***"
    elif r in o05_strict:
        tag = " [strict pool]"
    print(f"{i:2}.{fmt_row(r)}{tag}")

print("\n" + "=" * 100)
print("ALL O0.5 BY COMPOSITE — top 20")
print("=" * 100)
o05_comp = sorted(
    [r for r in straight_rows if r["split"] >= 0 and (r["hr"] >= 1 or r["near"] >= 2)],
    key=composite,
    reverse=True,
)
for i, r in enumerate(o05_comp[:20], 1):
    tag = " *** CURRENT ***" if r["name"] == straight_o05["name"] else ""
    print(f"{i:2}.{fmt_row(r)}{tag}")

print("\n" + "=" * 100)
print("ALL O1.5 OPTIONS — strict pool")
print("=" * 100)
for i, r in enumerate(o15_candidates, 1):
    tag = " *** CURRENT ***" if r["name"] == straight_o15["name"] else ""
    print(f"{i:2}.{fmt_row(r)} multi_rank {r.get('multi_hr_rank', 0):.1f}{tag}")

print("\n" + "=" * 100)
print("ALL O1.5 OPTIONS — relaxed (2+ HR, 2+ near, split >= 0.15)")
print("=" * 100)
o15_relaxed = sorted(
    [
        r
        for r in straight_rows
        if r["hr"] >= 2
        and r["near"] >= 2
        and r["split"] >= 0.15
        and not (r["split"] <= 0.0 and r["risk"] <= 0.0)
    ],
    key=lambda r: (r.get("multi_hr_rank", 0), composite(r)),
    reverse=True,
)
for i, r in enumerate(o15_relaxed, 1):
    tag = " *** CURRENT ***" if r["name"] == straight_o15["name"] else ""
    print(f"{i:2}.{fmt_row(r)} multi_rank {r.get('multi_hr_rank', 0):.1f}{tag}")

print("\n" + "=" * 100)
print("TOP O0.5 + O1.5 PAIRS (different games)")
print("=" * 100)
pairs: list[tuple[float, dict, dict]] = []
for o15 in o15_relaxed[:12]:
    for o05 in o05_comp[:15]:
        if o05["game_key"] == o15["game_key"] or o05["name"] == o15["name"]:
            continue
        pairs.append((composite(o05) + composite(o15), o05, o15))
pairs.sort(key=lambda x: x[0], reverse=True)
for i, (score, o05, o15) in enumerate(pairs[:15], 1):
    cur = o05["name"] == straight_o05["name"] and o15["name"] == straight_o15["name"]
    tag = " *** CURRENT SHEET ***" if cur else ""
    print(f"\n{i}. O0.5 {o05['name_plain']} vs {o05['chip']} ({o05['game_key']})")
    print(f"   O1.5 {o15['name_plain']} vs {o15['chip']} ({o15['game_key']})")
    print(f"   combined comp {score:.1f}{tag}")


