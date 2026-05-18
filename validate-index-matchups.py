#!/usr/bin/env python3
"""Validate preview/index.html: chips face opposing SP; list glove counts."""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "fix_batter_vs_pitcher", ROOT / "fix-batter-vs-pitcher.py"
)
fix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fix)

idx = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
pat = re.compile(
    r'\{ name: "([^"]+)"[^}]*chips: \[(.*?)\] \}',
    re.DOTALL,
)
title_pat = re.compile(r'title: "([^"]+)"')

titles = title_pat.findall(idx)
# Split block by game objects
game_chunks = re.split(r'\{ title: ', idx)[1:]  # skip before first game
errors = []
glove_issues = []

for i, chunk in enumerate(game_chunks):
    tm = re.match(r'"([^"]+)"', chunk)
    if not tm:
        continue
    title = tm.group(1)
    info = fix.parse_game(title)
    gloves = title.count("\U0001f9e4")
    if gloves < 2:
        # flag games where description mentions two leak angles
        desc_m = re.search(r'description: "([^"]+)"', chunk)
        desc = desc_m.group(1) if desc_m else ""
        glove_issues.append((gloves, title[:55], desc[:80]))

    for name, chips_raw in pat.findall(chunk):
        chips = re.findall(r'"([^"]+)"', chips_raw)
        chip = next((c for c in chips if c.startswith("vs ")), "")
        chip_p = chip.replace("vs ", "").strip()
        team = fix.PLAYER_TEAMS.get(name)
        opp = fix.opponent_pitcher(name, info)
        if not team:
            errors.append(f"NO TEAM: {name}")
            continue
        if team not in (info["away"], info["home"]):
            errors.append(f"WRONG GAME: {name} ({team}) in {info['away']}@{info['home']}")
            continue
        if not opp:
            continue
        own = info["pitcher_teams"].get(team, "")
        if chip_p.lower() == own.lower():
            errors.append(f"OWN PITCHER: {name} ({team}) {chip} (own SP {own})")
        elif chip_p.lower() != opp.lower():
            errors.append(f"MISMATCH: {name} ({team}) {chip} expected vs {opp}")

print(f"Games: {len(titles)}")
print(f"Matchup errors: {len(errors)}")
for e in errors:
    print(" ", e)

print(f"\nGlove counts (🧤 in title):")
for t in titles:
    print(f"  {t.count(chr(0x1F9E4))}  {t}")

if errors:
    sys.exit(1)
print("OK all chips face opposing SP")
