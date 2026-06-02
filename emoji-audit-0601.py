#!/usr/bin/env python3
"""Strict emoji audit for June 1 sheet."""
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("b", ROOT / "build-sheet-2026-06-02.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

FAVS = b.FAVS
BUM = b.BUM_PITCHERS

errors = []
warnings = []

for game in b.games:
    title = game["title"]
    bum_in_title = []
    for part in re.split(r"\s+vs\s+", title.split(" - ", 1)[-1]):
        if "🧤" in part:
            name = part.split("🧤")[0].strip()
            bum_in_title.append(re.sub(r"\s*\([LR].*$", "", name).split()[-1])

    for row in game["rows"]:
        name = row["name"]
        em = row["emojis"]
        note = row.get("note", "")
        chip = row["chips"][0].replace("vs ", "").strip()
        ev_m = re.search(r"(\d+(?:\.\d+)?)\s*mph\s*EV", note, re.I)
        ev = float(ev_m.group(1)) if ev_m else None

        if "🚀" in em and (ev is None or ev < 100.0):
            errors.append(f"🚀 without 100+ EV: {name} ({ev} mph) [{em}]")

        if "⭐" in em and name not in FAVS:
            errors.append(f"⭐ not a favorite: {name}")
        if name in FAVS and "⭐" not in em:
            errors.append(f"Missing ⭐ on favorite: {name}")

        if chip in BUM or chip in bum_in_title:
            for need in ("⚾", "🕊️", "🧤"):
                if need not in em:
                    errors.append(f"Missing {need} vs bum {chip}: {name} [{em}]")
        elif any(x in em for x in ("⚾", "🕊️", "🧤")):
            errors.append(f"Stray bum emoji vs non-bum {chip}: {name} [{em}]")

        if "📜" in em and "BvP" not in note and "career HR" not in note.lower() and "bvp" not in note.lower():
            warnings.append(f"📜 without BvP note: {name}")

print(f"Errors: {len(errors)}")
for e in errors:
    print(" ERROR:", e)
print(f"Warnings: {len(warnings)}")
for w in warnings:
    print(" WARN:", w)
if errors:
    raise SystemExit(1)
print("OK emoji audit")
