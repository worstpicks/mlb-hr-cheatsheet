#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
cut = (ROOT / "patch-0731-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
g: dict = {"__file__": str(ROOT / "patch-0731-preview.py"), "__name__": "x"}
exec(compile(cut + "\n", "patch-0731-preview.py", "exec"), g)

from goblin_hr_zone_fit import hr_rank_sort_key, hr_power_form

print("O0.5", g["straight_o05"]["name_plain"], g["straight_o05"]["chip"], g["straight_o05"]["game_key"])
print("O1.5", g["straight_o15"]["name_plain"], g["straight_o15"]["chip"], g["straight_o15"]["game_key"],
      f"{g['straight_o15']['hr']}HR/{g['straight_o15']['near']}near")

print("\nO1.5 candidates:")
for i, r in enumerate(g["o15_candidates"][:12], 1):
    tag = " ***" if r["name"] == g["straight_o15"]["name"] else ""
    print(
        f"{i:2}. {r['name_plain']:22} vs {r['chip']:12} {r['game_key']:10} "
        f"{r['hr']}HR/{r['near']}near multi={r.get('multi_hr_rank',0):.1f} "
        f"zone={r.get('hr_zone_fit',0):.1f}{tag}"
    )

# Replicate top3 / two_leg / fav3 selection window from patch — read after annotate
# Find variables if present
for key in ("top3", "two_leg", "fav3", "THREE_LEG_HR", "TWO_LEG_HR", "FAV_THREE_LEG"):
    if key in g:
        val = g[key]
        if isinstance(val, list) and val and isinstance(val[0], dict):
            print(key, [r["name_plain"] for r in val])
        else:
            print(key, val)

# Manual top HR ranks excluding straights for 3-leg pool
straight_names = {g["straight_o05"]["name"], g["straight_o15"]["name"]}
rows = g["rows"]
fav_plain = {x.rsplit(" (", 1)[0] for x in g["FAVS"]}

ranked = sorted(rows, key=hr_rank_sort_key, reverse=True)
print("\nTop 15 HR ranks:")
for i, r in enumerate(ranked[:15], 1):
    flags = []
    if r["name"] in straight_names:
        flags.append("STRAIGHT")
    if r["name_plain"] in fav_plain:
        flags.append("FAV")
    print(
        f"{i:2}. {r['name_plain']:22} vs {r['chip']:12} "
        f"zone {r.get('hr_zone_fit',0):5.1f} form {hr_power_form(r):4.1f} "
        f"split {r['split']:+.2f} risk {r['risk']:+.2f} "
        f"{r['hr']}HR/{r['near']}near {' '.join(flags)}"
    )

print("\nTop favorites:")
for r in ranked:
    if r["name_plain"] in fav_plain:
        print(
            f"  {r['name_plain']:22} vs {r['chip']:12} "
            f"zone {r.get('hr_zone_fit',0):5.1f} split {r['split']:+.2f} "
            f"risk {r['risk']:+.2f} {r['hr']}HR/{r['near']}near score {r['score']}"
        )
