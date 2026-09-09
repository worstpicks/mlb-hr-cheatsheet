#!/usr/bin/env python3
import re
from pathlib import Path

html = Path("preview/index.html").read_text(encoding="utf-8")
print("sheet-date", re.search(r'content="(2026-08-\d+)"', html).group(1))
print("hero", re.search(r"<p>((?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday), [^<]+)", html).group(1)[:80])
print("props", re.search(r"(\d+) listed HR props", html).group(0))
print("favs", re.search(r"(\d+) Worst Pickz Favorite", html).group(0))
print("gems", re.search(r"(\d+) Worst Pickz Hidden", html).group(0) if re.search(r"(\d+) Worst Pickz Hidden", html) else None)
print("straights", re.findall(r'class="straight-pick-name">([^<]+)', html))
for label in ["3 Leg Homerun", "2 Leg Homerun", "Favorite 3 Leg"]:
    pass
for m in re.finditer(r"Add (3 Leg HR|2 Leg HR|Favorite 3 Leg) to Gambly", html):
    # find preceding data attr
    start = html.rfind("data-goblin-gambly-lines", 0, m.start())
    chunk = html[start : m.start() + 20]
    lines = re.search(r"data-goblin-gambly-lines='([^']+)'", chunk)
    print(m.group(1), "=>", lines.group(1) if lines else "?")
# gloves
gloves = re.findall(r"([A-Za-z .'-]+) 🧤", html)
print("gloves unique", sorted(set(gloves))[:20])
# park/splits sample
metas = re.findall(r'gameMeta:\s*"((?:\\.|[^"\\])*)"', html)
print("games with Park", sum(1 for m in metas if "Park" in m.encode().decode("unicode_escape")))
print("games with LHB", sum(1 for m in metas if "LHB" in m.encode().decode("unicode_escape")))
print("games with pitcher-meta", sum(1 for m in metas if "pitcher-meta" in m.encode().decode("unicode_escape")))
# stale dates
for bad in ["Monday, August 3", "Sunday, August", "Wednesday, August 4", "Monday, August 4", "August 3, 2026 — current"]:
    if bad in html:
        print("BAD", bad)
print("Alonso chip check", "Grayson Rodriguez" in html or "vs Rodriguez" in html)
# features
for f in ["Homerun Form", "Damage Window", "Goblin's Insight", "MLB Research", "straight-streak", "worst-pickz-gem", "theme-toggle", "Pikkit", "Gambly"]:
    print(("OK" if f in html else "MISSING"), f)
