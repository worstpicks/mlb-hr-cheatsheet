#!/usr/bin/env python3
import importlib.util
from pathlib import Path

from game_row_enrich import enrich_games_list

spec = importlib.util.spec_from_file_location("b", "build-sheet-2026-08-01.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
eg = enrich_games_list(m.games, "2026-08-01")
missing = []
have = 0
for g in eg:
    for r in g["rows"]:
        if r.get("zoneScore") is None:
            chip = (r.get("chips") or ["?"])[0]
            missing.append((r["name"], g["title"].split(" - ")[0], chip))
        else:
            have += 1
print(f"have {have} missing {len(missing)}")
for x in missing:
    print(" ", x)
