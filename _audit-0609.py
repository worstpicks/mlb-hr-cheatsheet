#!/usr/bin/env python3
"""Comprehensive June 9 sheet audit."""
from __future__ import annotations

import importlib.util
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"

spec = importlib.util.spec_from_file_location("b", ROOT / "build-sheet-2026-06-09.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

errors: list[str] = []

for g in build.games:
    for r in g["rows"]:
        name = r["name"]
        em = r["emojis"]
        is_fav = name in build.FAVS
        is_gem = name in build.GEMS
        if is_fav and "⭐" not in em:
            errors.append(f"FAV missing star: {name} -> {em}")
        if is_gem and "💎" not in em:
            errors.append(f"GEM missing diamond: {name} -> {em}")
        if not is_fav and "⭐" in em:
            errors.append(f"non-fav has star: {name} -> {em}")
        note = r.get("note", "")
        if is_fav and "Worst Pickz Favorite" not in note:
            errors.append(f"FAV missing note prefix: {name}")
        if is_gem and "Worst Pickz Hidden Gem" not in note:
            errors.append(f"GEM missing note prefix: {name}")

keys = []
for g in build.games:
    for r in g["rows"]:
        plain = r["name"].rsplit(" (", 1)[0]
        chip = r["chips"][0].replace("vs ", "")
        keys.append(f"{plain}|{chip}")
dup = [k for k, c in Counter(keys).items() if c > 1]
if dup:
    errors.append(f"dup matchups: {dup}")

for g in build.games:
    for r in g["rows"]:
        chip = r["chips"][0].replace("vs ", "")
        if chip in build.BUM_PITCHERS and "🧤" not in r["emojis"]:
            errors.append(f"bum row missing glove: {r['name']} vs {chip}")

for bum in build.BUM_PITCHERS:
    if not any(bum in g["title"] for g in build.games):
        errors.append(f"bum {bum} not in any game title")

text = PREVIEW.read_text(encoding="utf-8")
zone_count = len(re.findall(r"zoneScore:\s*[\d.]+", text))
if zone_count < 60:
    errors.append(f"zone data low: {zone_count}")

if "Tuesday, June 9, 2026" not in text:
    errors.append("header date wrong")

# Stale June 8 names in summary
stale = ["Jackson Chourio", "Eric Haase", "Jonathan Aranda", "Jeffrey Springs", "Grayson Rodriguez"]
for s in stale:
    if s in text:
        errors.append(f"stale June 8 name in preview: {s}")

print(f"FAVS={len(build.FAVS)} GEMS={len(build.GEMS)} BUMS={build.BUM_PITCHERS}")
print(f"games={len(build.games)} rows={sum(len(g['rows']) for g in build.games)} zones={zone_count}")
if errors:
    print("FAIL:")
    for e in errors:
        print(f"  {e}")
    raise SystemExit(1)
print("OK comprehensive audit")
