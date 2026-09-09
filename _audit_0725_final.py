#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

html = Path("preview/index.html").read_text(encoding="utf-8")
arch = Path("preview/archive/2026-07-24.html").read_text(encoding="utf-8")
errors = []

# sheet date
m = re.search(r'name="sheet-date" content="([^"]+)"', html)
assert m and m.group(1) == "2026-07-25", m

# all gameMeta blocks
metas = re.findall(
    r'title:\s*"([^"]+)"\s*,\s*startTime:[^,]*,\s*gameMeta:\s*"([^"]*)"',
    html,
)
print(f"gameMeta blocks: {len(metas)}")
for title, meta in metas:
    print(f"\n{title}")
    print(f"  {meta[:220]}")
    if "Park" not in meta and "park" not in meta:
        errors.append(f"{title}: missing Park in gameMeta")
    if "LHB" not in meta or "RHB" not in meta:
        errors.append(f"{title}: missing LHB/RHB in gameMeta")
    # pitcher splits often as "LHB +x% · RHB"
    if "overall" not in meta.lower() and "vs LHB" not in meta:
        # sheet uses "LHB +8% · RHB +60%" style inside pitcher-meta
        if meta.count("LHB") < 2:
            errors.append(f"{title}: thin pitcher split coverage")

# bums in titles
for bum in ["Bryce Elder", "Ryan Feltner", "Mason Barnett"]:
    if f"{bum}" not in html or "🧤" not in html:
        errors.append(f"missing bum display for {bum}")
    if not re.search(rf"{re.escape(bum)}[^\"\n]{{0,30}}🧤", html):
        errors.append(f"{bum} not marked 🧤 in title")

# stale SPs
for stale in ["Tim Mayza", "Mike Paredes"]:
    if stale in html:
        errors.append(f"stale SP present: {stale}")

# features present in both
for feat in [
    "Homerun Form",
    "Damage Window",
    "Straights of the Day",
    "Goblin",
    "Favorite 3",
    "Top 5 HR Tickets",
    "Weather Heavy",
    "Longshot",
    "Hits",
    "research",
    "gambly",
    "Pikkit",
]:
    if feat.lower() not in html.lower():
        errors.append(f"missing feature: {feat}")
    elif feat.lower() not in arch.lower() and feat not in ("research",):
        pass

# prop counts
stars = len(re.findall(r"⭐", html))
# count favorite props in games rows roughly
fav_rows = len(re.findall(r'emojis: "[^"]*⭐', html))
gem_rows = len(re.findall(r'emojis: "[^"]*💎', html))
print(f"\nfav rows={fav_rows} gem rows={gem_rows}")
if fav_rows < 15:
    errors.append(f"expected 15 favorite rows, got {fav_rows}")
if gem_rows < 13:
    errors.append(f"expected 13 gem rows, got {gem_rows}")

print("\nERRORS:" if errors else "\nPASS")
for e in errors:
    print(" -", e)
raise SystemExit(1 if errors else 0)
