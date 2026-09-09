#!/usr/bin/env python3
"""Feature / date / park / bum parity audit for 2026-08-08 vs prior archive."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
ARCHIVE = ROOT / "preview" / "archive" / "2026-08-07.html"
errors: list[str] = []

text = PREVIEW.read_text(encoding="utf-8")
arch = ARCHIVE.read_text(encoding="utf-8") if ARCHIVE.is_file() else ""

# Date correctness
if 'content="2026-08-08"' not in text:
    errors.append("sheet-date meta is not 2026-08-08")
if "Saturday, August 8, 2026" not in text:
    errors.append("hero date is not Saturday, August 8, 2026")
if "Friday, August" in text.split("games =")[0]:
    errors.append("Friday still appears in hero/summary region")
if arch and "Friday, August 7, 2026" not in arch:
    errors.append("archive 2026-08-07 missing Friday hero")
if arch and 'content="2026-08-07"' not in arch:
    errors.append("archive sheet-date not 2026-08-07")

# Feature markers present on current sheet
features = {
    "Homerun Form": "Homerun Form",
    "Damage Window Stats": "Damage Window Stats",
    "straight-streak-badge": "straight-streak-badge",
    "Pikkit": "pikkit-link__wordmark",
    "bet tracker": "bet-tracker-save-btn",
    "Gambly": "btn-gambly",
    "Research tab link": "research/index.html",
    "PropFinder Weather": "propfinder.app/weather",
    "Worst Pickz Straights": "straight-of-day-card",
    "Goblin": "Goblin",
    "Top 5 HR Tickets": "Top 5 HR Tickets",
    "Weather Heavy": "Weather Heavy",
    "Hidden Gem": "💎",
    "Favorite star": "⭐",
    "Bum glove filter": 'data-emoji="🧤"',
    "Zone Fit Score": "Zone Fit Score",
    "My Slip": "My Slip",
    "straights history": "straights-history-data",
}
for label, needle in features.items():
    if needle not in text:
        errors.append(f"missing feature: {label}")

# Props / games counts from hero
m = re.search(
    r"<strong>(\d+) listed HR props</strong> across <strong>(\d+) games</strong>",
    text,
)
if not m or int(m.group(1)) != 80 or int(m.group(2)) != 15:
    errors.append(f"hero prop/game counts wrong: {m.groups() if m else None}")

# All game titles have park + pitcher metas
titles = re.findall(r'title:\s*"([^"]+)"', text)
metas = re.findall(r'gameMeta:\s*"([^"]+)"', text)
if len(titles) != 15:
    errors.append(f"expected 15 game titles, got {len(titles)}")
if len(metas) != 15:
    errors.append(f"expected 15 gameMeta, got {len(metas)}")
for i, meta in enumerate(metas):
    if "Park" not in meta and "park" not in meta:
        errors.append(f"gameMeta missing Park: {titles[i] if i < len(titles) else i}")
    if "pitcher-meta" not in meta:
        errors.append(f"gameMeta missing pitcher-meta: {titles[i] if i < len(titles) else i}")
    if "LHB" not in meta or "RHB" not in meta:
        errors.append(f"gameMeta missing LHB/RHB: {titles[i] if i < len(titles) else i}")

# Bums gloved in titles
gloved = [t for t in titles if "🧤" in t]
need = ["Aaron Nola", "Robert Stock", "Max Scherzer"]
for n in need:
    if not any(n.split()[-1] in t and "🧤" in t for t in titles):
        # last-name match in gloved title
        last = n.split()[-1]
        if not any(last in t and "🧤" in t for t in titles):
            errors.append(f"bum not gloved in title: {n}")
if len(gloved) < 2:
    errors.append(f"expected gloves on TOR@PHI and NYM@PIT titles, got {gloved}")

# Research + park JSON
research = ROOT / "preview" / "data" / "research-2026-08-08.json"
park = ROOT / "preview" / "data" / "park-factors-2026-08-08.json"
if not research.is_file():
    errors.append("missing research-2026-08-08.json")
else:
    data = json.loads(research.read_text(encoding="utf-8"))
    games = data.get("games") or data.get("slate") or []
    if isinstance(data, dict) and "games" in data and len(data["games"]) != 15:
        errors.append(f"research games != 15: {len(data['games'])}")
if not park.is_file():
    errors.append("missing park-factors-2026-08-08.json")
else:
    pj = json.loads(park.read_text(encoding="utf-8"))
    if pj.get("source") not in {"ballpark-pal", "Ballpark Pal", "ballpark_pal"} and "ballpark" not in str(
        pj.get("source", "")
    ).lower():
        # accept common variants
        if "source" in pj and "ballpark" not in str(pj["source"]).lower():
            errors.append(f"park factors source unexpected: {pj.get('source')}")

# Manifest current first
man = json.loads((ROOT / "preview" / "sheets-manifest.json").read_text(encoding="utf-8"))
sheets = man.get("sheets") or []
if not sheets or sheets[0].get("date") != "2026-08-08":
    errors.append(f"manifest first date wrong: {sheets[0].get('date') if sheets else None}")
if not any(s.get("date") == "2026-08-07" for s in sheets):
    errors.append("manifest missing 2026-08-07")

# Zone coverage in preview games block
zone_n = text.count("zoneScore:")
if zone_n < 80:
    errors.append(f"zoneScore fields < 80: {zone_n}")

# Straights / Goblin not yesterday
if "vs Perkins" in text or "Alec Burleson &mdash; vs Feltner" in text:
    errors.append("stale Aug 7 straights still on preview")
if "Derek Hill &mdash; vs Scherzer" not in text:
    errors.append("O0.5 Hill missing")
if "Willson Contreras &mdash; vs Jump" not in text:
    errors.append("O1.5 Contreras missing")

if errors:
    print("FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)
print("OK feature/date/park/bum audit")
print(f"  games={len(titles)} metas={len(metas)} zones={zone_n} gloves={len(gloved)}")
print("  gloved titles:")
for t in gloved:
    print("   ", t)
