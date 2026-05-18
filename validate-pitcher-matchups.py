#!/usr/bin/env python3
"""Fail if any batter chip references own team's starting pitcher."""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

spec_fix = importlib.util.spec_from_file_location(
    "fix_batter_vs_pitcher", ROOT / "fix-batter-vs-pitcher.py"
)
fix = importlib.util.module_from_spec(spec_fix)
spec_fix.loader.exec_module(fix)

spec = importlib.util.spec_from_file_location("build0518", ROOT / "build-sheet-2026-05-18.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

games, _ = fix.fix_games(mod.games)
errors = []
for g in games:
    info = fix.parse_game(g["title"])
    for r in g["rows"]:
        batter = r["name"]
        team = fix.PLAYER_TEAMS.get(batter)
        opp = fix.opponent_pitcher(batter, info)
        chip = next((c for c in r["chips"] if c.startswith("vs ")), "")
        chip_p = chip.replace("vs ", "").strip()
        if not team or not opp:
            errors.append(f"{batter}: missing team/opp in {g['title'][:35]}")
            continue
        if chip_p.lower() != opp.lower():
            errors.append(f"{batter} ({team}): chip {chip} expected vs {opp}")
        own = info["pitcher_teams"].get(team)
        if own and chip_p.lower() == own.lower():
            errors.append(f"{batter} ({team}): faces OWN pitcher {own}")

if errors:
    print("FAIL", len(errors), "matchup errors")
    for e in errors[:20]:
        print(" ", e)
    sys.exit(1)
print("OK all", sum(len(g["rows"]) for g in mod.games), "props face opposing SP")
