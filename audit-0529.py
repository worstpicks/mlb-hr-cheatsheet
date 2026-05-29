#!/usr/bin/env python3
"""Audit May 29 sheet: matchups, bum gloves, emoji sanity."""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")

spec = importlib.util.spec_from_file_location("build", ROOT / "build-sheet-2026-05-29.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

spec2 = importlib.util.spec_from_file_location("v", ROOT / "validate-index-matchups.py")
v = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(v)

row_pat = re.compile(r'\{ name: "([^"]+)"[^}]*emojis: "([^"]*)"[^}]*chips: \[(.*?)\][^}]*\}', re.DOTALL)
title_pat = re.compile(r'title: "([^"]+)"')

errors = []
warnings = []

for chunk in re.split(r"\{ title: ", idx)[1:]:
    tm = re.match(r'"([^"]+)"', chunk)
    if not tm:
        continue
    title = tm.group(1)
    try:
        g = v.parse_game(title)
    except ValueError as e:
        errors.append(f"TITLE PARSE: {title} — {e}")
        continue

    bum_names = []
    for part in re.split(r"\s+vs\s+", title.split(" - ", 1)[-1]):
        if "🧤" in part:
            name = part.split("🧤")[0].strip()
            name = re.sub(r"\s*\([LRSHB].*$", "", name).strip()
            bum_names.append(v.pitcher_chip_name(name))

    for name, emojis, chips_raw in row_pat.findall(chunk):
        chips = re.findall(r'"([^"]+)"', chips_raw)
        vs = next((c for c in chips if c.startswith("vs ")), "").replace("vs ", "").strip()
        team = build.PLAYER_TEAMS.get(name)
        if not team:
            errors.append(f"NO TEAM: {name}")
            continue
        own = g["pitcher_by_team"].get(team)
        opp = g["home"] if team == g["away"] else g["away"]
        expected = g["pitcher_by_team"].get(opp)
        if vs.lower() == (own or "").lower():
            errors.append(f"OWN SP: {name} ({team}) {vs} — own SP is {own}")
        elif vs.lower() != (expected or "").lower():
            errors.append(f"MISMATCH: {name} ({team}) {vs} — expected vs {expected}")

        if any(vs.lower() == b.lower() for b in bum_names):
            for need in ("⚾", "🕊️", "🧤"):
                if need not in emojis:
                    warnings.append(f"BUM EMOJI missing {need}: {name} vs {vs} — [{emojis}]")

        if "⚾" in emojis and not any(vs.lower() == b.lower() for b in bum_names):
            if vs not in build.BUM_PITCHERS:
                warnings.append(f"STRAY ⚾ (not a titled bum): {name} vs {vs} — [{emojis}]")

print(f"Games: {len(title_pat.findall(idx))}")
print(f"Rows: {len(row_pat.findall(idx))}")
print(f"Errors: {len(errors)}")
for e in errors:
    print("  ERROR:", e)
print(f"Warnings: {len(warnings)}")
for w in warnings:
    print("  WARN:", w)

if errors:
    sys.exit(1)
