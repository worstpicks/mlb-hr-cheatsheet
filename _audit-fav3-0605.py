#!/usr/bin/env python3
"""Audit Favorite 3-leg pool for 2026-06-05."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("build", ROOT / "build-sheet-2026-06-05.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

# Replicate patch row building (minimal)
import json
import re

manifest_path = ROOT / "data" / "manifest-2026-06-05.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

def load_risk(chip):
    for p in build.BUM_PITCHERS + []:
        pass
    # use build games
    for game in build.games:
        for entry in game["rows"]:
            if chip in entry.get("chips", []):
                sp = game["sp"]
                for b in build.BUM_PITCHERS:
                    if b["name"] == sp:
                        return b
    return None

# Import patch helpers by exec up to fav3
patch_src = (ROOT / "patch-0605-preview.py").read_text(encoding="utf-8")
# Run patch in subprocess style - simpler: import as module with __file__ set
patch_globals = {"__file__": str(ROOT / "patch-0605-preview.py"), "__name__": "__main__"}
# Stop before asserts
cut = patch_src.split("assert len(top3)")[0]
exec(compile(cut + "\n", "patch-0605-preview.py", "exec"), patch_globals)

top3 = patch_globals["top3"]
straight_o05 = patch_globals["straight_o05"]
straight_o15 = patch_globals["straight_o15"]
fav_pool = patch_globals["fav_pool"]
fav_fallback = patch_globals.get("fav_fallback", [])
fav3 = patch_globals["fav3"]
rows = patch_globals["rows"]
FAVS = patch_globals["FAVS"]

print("Straights:", straight_o05["name_plain"], straight_o15["name_plain"])
print("Top3:", [r["name_plain"] for r in top3])
print("fav3 count:", len(fav3), [r["name_plain"] for r in fav3])
print()
print("All FAVS with moonshot:")
for r in sorted(rows, key=lambda x: -x["score"]):
    if r["name"] not in FAVS:
        continue
    has_moon = patch_globals["fav_row_has_moonshot"](r)
    in_top = r["name"] in {x["name"] for x in top3}
    in_str = r["name"] in {straight_o05["name"], straight_o15["name"]}
    print(
        f"  {r['name_plain']:22} moon={has_moon} split={r['split']:+.2f} risk={r['risk']:+.2f} "
        f"park={r['park_pct']}% score={r['score']} top3={in_top} straight={in_str}"
    )
print()
print("fav_pool:", len(fav_pool))
for r in fav_pool:
    print(f"  {r['name_plain']} split={r['split']:+.2f}")
print("fav_fallback:", len(fav_fallback))
for r in fav_fallback:
    print(f"  {r['name_plain']} split={r['split']:+.2f}")
