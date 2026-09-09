#!/usr/bin/env python3
import re
from pathlib import Path

html = Path("preview/index.html").read_text(encoding="utf-8")
print("picks", re.findall(r'class="straight-pick-name">([^<]+)', html))
# Goblin insight legs from summary cards
for label in ("3 Leg Homerun", "2 Leg Homerun", "Favorite 3 Leg"):
    i = html.find(label)
    print(label, "at", i)
# gambly lines from goblin cards
lines = re.findall(r"data-goblin-gambly-lines='([^']+)'", html)
import html as H
import json
for i, raw in enumerate(lines[:6]):
    s = raw.replace("&#39;", "'").replace("&quot;", '"')
    try:
        arr = json.loads(s)
    except Exception:
        arr = s[:120]
    print(f"gambly[{i}]", arr)
