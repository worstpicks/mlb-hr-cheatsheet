#!/usr/bin/env python3
"""Audit straight/fav picks for 2026-06-06."""
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
patch_globals = {"__file__": str(ROOT / "patch-0606-preview.py"), "__name__": "__main__"}
cut = (ROOT / "patch-0606-preview.py").read_text(encoding="utf-8").split("assert len(top3)")[0]
exec(compile(cut + "\n", "patch-0606-preview.py", "exec"), patch_globals)

print("Straights:", patch_globals["straight_o05"]["name_plain"], patch_globals["straight_o15"]["name_plain"])
print("Games:", patch_globals["straight_o05"]["game_key"], patch_globals["straight_o15"]["game_key"])
print("Top3:", [r["name_plain"] for r in patch_globals["top3"]])
print("Fav3:", [r["name_plain"] for r in patch_globals["fav3"]])

rows = patch_globals["rows"]
eligible = [r for r in rows if r["split"] >= 0 and (r["hr"] >= 1 or r["near"] >= 2)]
eligible.sort(key=patch_globals["straight_attack_rank"], reverse=True)
print("\nTOP 12 O0.5 attack:")
for x in eligible[:12]:
    print(
        f"  {x['name_plain']:22} {x['game_key']:11} vs {x['chip']:10} "
        f"hr={x['hr']} near={x['near']} split={x['split']:+.2f} risk={x['risk']:+.2f} park={x['park_pct']:+d}%"
    )

o15 = [r for r in rows if r["hr"] >= 2 and r["near"] >= 2 and r["score"] >= 78 and r["split"] >= 0]
o15.sort(key=patch_globals["multi_hr_rank"], reverse=True)
print("\nTOP O1.5:")
for x in o15[:8]:
    print(f"  {x['name_plain']:22} {x['game_key']} hr={x['hr']} near={x['near']} split={x['split']:+.2f} risk={x['risk']:+.2f} park={x['park_pct']:+d}%")
