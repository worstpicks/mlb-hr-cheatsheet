#!/usr/bin/env python3
import re
from pathlib import Path

html = Path("preview/index.html").read_text(encoding="utf-8")
print(re.search(r"Tuesday, August 4, 2026 — Worst Pickz HR cheat sheet", html).group(0))
print(
    re.search(
        r"This board covers <strong>.*?</strong> across <strong>.*?</strong>, with <strong>.*?</strong>",
        html,
    ).group(0)
)
print("straights", re.findall(r'class="straight-pick-name">([^<]+)', html))
for m in re.finditer(
    r"data-goblin-label=\"([^\"]+)\"[^>]*data-goblin-gambly-lines='([^']+)'",
    html,
):
    print(m.group(1), "=>", m.group(2)[:180])
