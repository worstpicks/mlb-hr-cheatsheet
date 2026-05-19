#!/usr/bin/env python3
"""Validate preview/index.html: all row chips face the opposing starter."""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
date_m = re.search(r'<meta name="sheet-date" content="([^"]+)">', idx)
sheet_date = date_m.group(1) if date_m else "2026-05-19"
build_path = ROOT / f"build-sheet-{sheet_date}.py"
if not build_path.exists():
    build_path = ROOT / "build-sheet-2026-05-19.py"

spec = importlib.util.spec_from_file_location("sheet_build", build_path)
sheet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sheet)
PLAYER_TEAMS = getattr(sheet, "PLAYER_TEAMS", {})

row_pat = re.compile(r'\{ name: "([^"]+)"[^}]*chips: \[(.*?)\][^}]*\}', re.DOTALL)
title_pat = re.compile(r'title: "([^"]+)"')
game_chunks = re.split(r'\{ title: ', idx)[1:]
titles = title_pat.findall(idx)
errors = []


def strip_glove(value: str) -> str:
    return value.replace("\U0001f9e4", "").strip()


def pitcher_chip_name(full_name: str) -> str:
    parts = strip_glove(full_name).split()
    if len(parts) >= 2 and parts[-1].rstrip(".").lower() == "jr":
        return f"{parts[-2]} {parts[-1]}"
    return parts[-1] if parts else ""


def parse_game(title: str):
    m = re.match(
        r"(?P<away>[A-Z]{2,3}) @ (?P<home>[A-Z]{2,3}) - "
        r"(?P<p1>.*?) \([LR], (?P<t1>[A-Z]{2,3})\) vs "
        r"(?P<p2>.*?) \([LR], (?P<t2>[A-Z]{2,3})\)",
        title,
    )
    if not m:
        raise ValueError(f"cannot parse game title: {title}")
    pitcher_by_team = {
        m.group("t1"): pitcher_chip_name(m.group("p1")),
        m.group("t2"): pitcher_chip_name(m.group("p2")),
    }
    return {
        "away": m.group("away"),
        "home": m.group("home"),
        "pitcher_by_team": pitcher_by_team,
    }


for chunk in game_chunks:
    tm = re.match(r'"([^"]+)"', chunk)
    if not tm:
        continue
    title = tm.group(1)
    info = parse_game(title)
    for name, chips_raw in row_pat.findall(chunk):
        chips = re.findall(r'"([^"]+)"', chips_raw)
        chip = next((c for c in chips if c.startswith("vs ")), "")
        chip_pitcher = chip.replace("vs ", "").strip()
        team = PLAYER_TEAMS.get(name)
        if not team:
            errors.append(f"NO TEAM: {name}")
            continue
        if team not in (info["away"], info["home"]):
            errors.append(f"WRONG GAME: {name} ({team}) in {info['away']}@{info['home']}")
            continue
        own = info["pitcher_by_team"].get(team)
        opp_team = info["home"] if team == info["away"] else info["away"]
        expected = info["pitcher_by_team"].get(opp_team)
        if chip_pitcher.lower() == (own or "").lower():
            errors.append(f"OWN PITCHER: {name} ({team}) {chip} (own SP {own})")
        elif chip_pitcher.lower() != (expected or "").lower():
            errors.append(f"MISMATCH: {name} ({team}) {chip} expected vs {expected}")

print(f"Sheet date: {sheet_date}")
print(f"Games: {len(titles)}")
print(f"Rows: {len(row_pat.findall(idx))}")
print(f"Matchup errors: {len(errors)}")
for e in errors:
    print(" ", e)

print("\nGlove counts (🧤 in title):")
for title in titles:
    print(f"  {title.count(chr(0x1F9E4))}  {title}")

if errors:
    sys.exit(1)
print("OK all chips face opposing SP")
