#!/usr/bin/env python3
"""Quick peek at 8/2 sheet picks / coverage."""
from __future__ import annotations

import re
from pathlib import Path

html = Path("preview/index.html").read_text(encoding="utf-8")
print("date", re.search(r'sheet-date" content="([^"]+)"', html).group(1))
print("hero", re.search(r"<p>((?:Sunday|Saturday), [^<]+)", html).group(1))
props = re.search(r"(\d+) listed HR props", html)
print(props.group(0) if props else "no props line")
picks = re.findall(r'class="straight-pick-name">([^<]+)', html)
print("straights", picks)
# goblin cards
for label in ("3 Leg Homerun", "2 Leg Homerun", "Favorite 3 Leg", "Hits"):
    print(label, "present" if label in html else "MISSING")
# missing zones
zs = html.count("zoneScore:")
print("zoneScore fields", zs)
# bum
print("Scherzer glove", "Max Scherzer 🧤" in html)
# fav/gem counts in hero
m = re.search(r"(\d+)⭐.*?(\d+)💎", html)
print("hero stars/gems", m.groups() if m else None)
