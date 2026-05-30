#!/usr/bin/env python3
"""Audit May 30 sheet: matchups, bum gloves, emoji sanity, duplicates."""
import importlib.util
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")

spec = importlib.util.spec_from_file_location("build", ROOT / "build-sheet-2026-05-30.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

spec2 = importlib.util.spec_from_file_location("v", ROOT / "validate-index-matchups.py")
v = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(v)

row_pat = re.compile(
    r'\{ name: "([^"]+)"[^}]*emojis: "([^"]*)"[^}]*note: "([^"]*)"[^}]*chips: \[(.*?)\][^}]*\}',
    re.DOTALL,
)
title_pat = re.compile(r'title: "([^"]+)"')

errors = []
warnings = []

all_names = []
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

    for name, emojis, note, chips_raw in row_pat.findall(chunk):
        all_names.append(name)
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
                    errors.append(f"BUM EMOJI missing {need}: {name} vs {vs} — [{emojis}]")

        if vs in build.BUM_PITCHERS or any(vs.lower() == b.lower() for b in bum_names):
            pass
        elif any(x in emojis for x in ("⚾", "🕊️", "🧤")):
            errors.append(f"STRAY bum emoji vs non-bum {vs}: {name} [{emojis}]")

        if "⭐" in emojis and name not in build.FAVS:
            errors.append(f"⭐ not a favorite: {name}")
        if name in build.FAVS and "⭐" not in emojis:
            errors.append(f"Missing ⭐ on favorite: {name}")

        ev_m = re.search(r"(\d+(?:\.\d+)?)\s*mph\s*EV", note, re.I)
        ev = float(ev_m.group(1)) if ev_m else None
        if "🚀" in emojis and (ev is None or ev < 100.0):
            errors.append(f"🚀 without 100+ EV: {name} ({ev} mph)")

        if "📜" in emojis and "BvP" not in note and "bvp" not in note.lower():
            warnings.append(f"📜 without BvP note: {name}")

dupes = [n for n, c in Counter(all_names).items() if c > 1]
for n in dupes:
    errors.append(f"DUPLICATE ROW: {n} appears {Counter(all_names)[n]} times")

print(f"Games: {len(title_pat.findall(idx))}")
print(f"Rows: {len(all_names)}")
print(f"Errors: {len(errors)}")
for e in errors:
    print("  ERROR:", e)
print(f"Warnings: {len(warnings)}")
for w in warnings:
    print("  WARN:", w)

if errors:
    sys.exit(1)
print("OK audit-0530")
