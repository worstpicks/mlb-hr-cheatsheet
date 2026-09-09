#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
cut = (ROOT / "patch-0801-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
g: dict = {"__file__": str(ROOT / "patch-0801-preview.py"), "__name__": "x"}
exec(compile(cut + "\n", "patch-0801-preview.py", "exec"), g)

from goblin_hr_zone_fit import hr_power_form

print("O0.5", g["straight_o05"]["name_plain"], "vs", g["straight_o05"]["chip"], g["straight_o05"]["game_key"],
      f"{g['straight_o05']['hr']}HR/{g['straight_o05']['near']}near split={g['straight_o05']['split']:+.2f} risk={g['straight_o05']['risk']:+.2f}")
print("O1.5", g["straight_o15"]["name_plain"], "vs", g["straight_o15"]["chip"], g["straight_o15"]["game_key"],
      f"{g['straight_o15']['hr']}HR/{g['straight_o15']['near']}near split={g['straight_o15']['split']:+.2f} risk={g['straight_o15']['risk']:+.2f}")

print("\nO0.5 strict top 10:")
for i, r in enumerate(g["straight_o05_pool"](g["straight_rows"], strict=True)[:10], 1):
    tag = " ***" if r["name"] == g["straight_o05"]["name"] else ""
    print(f"{i:2}. {r['name_plain']:22} vs {r['chip']:12} {r['hr']}HR/{r['near']}near "
          f"split {r['split']:+.2f} risk {r['risk']:+.2f} zone {r.get('hr_zone_fit',0):.1f}{tag}")

print("\nO1.5 candidates:")
for i, r in enumerate(g["o15_candidates"][:10], 1):
    tag = " ***" if r["name"] == g["straight_o15"]["name"] else ""
    print(f"{i:2}. {r['name_plain']:22} vs {r['chip']:12} {r['hr']}HR/{r['near']}near "
          f"multi={r.get('multi_hr_rank',0):.1f} zone={r.get('hr_zone_fit',0):.1f}{tag}")

print("top3", [x["name_plain"] for x in g["top3"]])
print("two", [x["name_plain"] for x in g["two_leg"]])
print("fav3", [x["name_plain"] for x in g["fav3"]])
