#!/usr/bin/env python3
import re
from pathlib import Path

html = Path("preview/index.html").read_text(encoding="utf-8")
print("sheet-date", re.search(r'content="(2026-08-\d+)"', html).group(1))
print(
    "hero",
    re.search(
        r"<p>((?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday), [^<]+)",
        html,
    ).group(1)[:100],
)
print(re.search(r"This board covers <strong>.*?</strong>", html).group(0))
print("straights", re.findall(r'class="straight-pick-name">([^<]+)', html))
for m in re.finditer(r"Add (3 Leg HR|2 Leg HR|Favorite 3 Leg) to Gambly", html):
    start = html.rfind("data-goblin-gambly-lines", 0, m.start())
    chunk = html[start : m.start() + 10]
    lines = re.search(r"data-goblin-gambly-lines='([^']+)'", chunk)
    print(m.group(1), "=>", lines.group(1) if lines else "?")
arch = Path("preview/archive/2026-08-04.html")
print(
    "8/4 archive",
    arch.exists(),
    re.search(r'content="(2026-08-\d+)"', arch.read_text(encoding="utf-8")).group(1),
)
print("stale Tue Aug4 hero?", "Tuesday, August 4, 2026 — Worst" in html)
print("Wed Aug5?", "Wednesday, August 5, 2026" in html)
