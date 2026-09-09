#!/usr/bin/env python3
"""Feature / date / park / bum parity audit for 2026-08-09."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
ARCHIVE = ROOT / "preview" / "archive" / "2026-08-08.html"
errors: list[str] = []

text = PREVIEW.read_text(encoding="utf-8")
arch = ARCHIVE.read_text(encoding="utf-8") if ARCHIVE.is_file() else ""

if 'content="2026-08-09"' not in text:
    errors.append("sheet-date meta is not 2026-08-09")
if "Sunday, August 9, 2026" not in text:
    errors.append("hero date is not Sunday, August 9, 2026")
if "Saturday, August 9" in text or "Monday, August 9" in text:
    errors.append("wrong weekday on August 9")
if "Saturday, August 8, 2026 — Worst" in text.split("const games")[0]:
    errors.append("stale Saturday Aug 8 hero still on current sheet")
if arch and "Saturday, August 8, 2026" not in arch:
    errors.append("archive 2026-08-08 missing Saturday hero")
if arch and 'content="2026-08-08"' not in arch:
    errors.append("archive sheet-date not 2026-08-08")

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

m = re.search(
    r"<strong>(\d+) listed HR props</strong> across <strong>(\d+) games</strong>",
    text,
)
if not m or int(m.group(1)) != 97 or int(m.group(2)) != 15:
    errors.append(f"hero prop/game counts wrong: {m.groups() if m else None}")

block = re.search(r"const games = \[(.*?)\n\];", text, re.S)
if not block:
    errors.append("games block missing")
else:
    titles = re.findall(r'title:\s*"([^"]+)"', block.group(1))
    metas = re.findall(r'gameMeta:\s*"((?:\\.|[^"\\])*)"', block.group(1))
    if len(titles) != 15:
        errors.append(f"expected 15 game titles, got {len(titles)}")
    if len(metas) != 15:
        errors.append(f"expected 15 gameMeta, got {len(metas)}")
    for title, meta in zip(titles, metas):
        s = meta.encode().decode("unicode_escape")
        if "Park" not in s:
            errors.append(f"missing Park: {title}")
        if s.count("pitcher-meta") != 2:
            errors.append(f"expected 2 pitcher-meta: {title}")
        if "LHB" not in s or "RHB" not in s:
            errors.append(f"missing LHB/RHB: {title}")
    for last in ("Lord", "Rodriguez", "Wrobleski", "Manaea"):
        # Grayson Rodriguez + Eduardo Rodriguez both contain Rodriguez; require glove on bum titles
        if last == "Rodriguez":
            if "Grayson Rodriguez 🧤" not in text:
                errors.append("bum Grayson Rodriguez not gloved")
        elif not any(last in t and "🧤" in t for t in titles):
            errors.append(f"bum not gloved in title: {last}")

if "Josh Bell &mdash; vs Misiorowski" not in text:
    errors.append("O0.5 Bell missing")
if "Jazz Chisholm Jr. &mdash; vs Holmes" not in text:
    errors.append("O1.5 Jazz missing")
if "Derek Hill &mdash; vs Scherzer" in text:
    errors.append("stale Aug 8 straight still on preview")

man = json.loads((ROOT / "preview" / "sheets-manifest.json").read_text(encoding="utf-8"))
sheets = man.get("sheets") or []
if not sheets or sheets[0].get("date") != "2026-08-09":
    errors.append(f"manifest first date wrong: {sheets[0].get('date') if sheets else None}")
if not any(s.get("date") == "2026-08-08" for s in sheets):
    errors.append("manifest missing 2026-08-08")

zone_n = text.count("zoneScore:")
if zone_n < 95:
    errors.append(f"zoneScore fields < 95: {zone_n}")

if errors:
    print("FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)
print("OK feature/date/park/bum audit")
print(f"  zones={zone_n} manifest0={sheets[0]['date']}")
