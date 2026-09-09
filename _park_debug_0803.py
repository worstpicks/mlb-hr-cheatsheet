#!/usr/bin/env python3
from pathlib import Path
import json
from game_row_enrich import load_weather_lookup, enrich_games_list
import importlib.util

DATE = "2026-08-03"
wx = load_weather_lookup(DATE)
print("weather keys:")
for k in sorted(wx):
    print(" ", k, wx[k])

pf = json.loads(Path(f"preview/data/park-factors-{DATE}.json").read_text(encoding="utf-8"))
print("\npark-factors games:", list(pf.get("games", pf) if isinstance(pf, dict) else [])[:20])
if isinstance(pf, dict):
    for k in list(pf.keys())[:30]:
        print(k, type(pf[k]).__name__)

spec = importlib.util.spec_from_file_location("b", f"build-sheet-{DATE}.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
games = enrich_games_list(b.games, DATE)
for g in games:
    print(
        g["title"].split(" - ")[0],
        "parkPct",
        g.get("parkPct"),
        "LHB",
        g.get("parkLhbPct"),
        "RHB",
        g.get("parkRhbPct"),
    )
    meta = g.get("gameMeta") or ""
    print("  Park in meta?", "Park" in meta, meta[:180].replace("\n", " "))
