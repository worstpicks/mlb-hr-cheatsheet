#!/usr/bin/env python3
import json
import re
from pathlib import Path

html = Path("preview/index.html").read_text(encoding="utf-8")
print("hero Saturday?", "Saturday, August 1, 2026" in html)
print("meta", re.search(r'sheet-date" content="([^"]+)"', html).group(1))
print("props", re.search(r"(\d+) listed HR props", html).group(0))
print("picks", re.findall(r'class="straight-pick-name">([^<]+)', html))
lines = re.findall(r"data-goblin-gambly-lines='([^']+)'", html)
for i, raw in enumerate(lines[:6]):
    s = raw.replace("&#39;", "'").replace("&quot;", '"')
    try:
        print(f"gambly[{i}]", json.loads(s))
    except Exception:
        print(f"gambly[{i}]", s[:120])

# parks/splits
block = re.search(r"const games = \[(.*?)\n\];", html, re.S).group(1)
titles = re.findall(r'title:\s*"([^"]+)"', block)
metas = re.findall(r'gameMeta:\s*"((?:\\.|[^"\\])*)"', block)
print("games", len(titles))
for title, meta in zip(titles, metas):
    s = meta.encode().decode("unicode_escape")
    ok = "Park" in s and "LHB" in s and "RHB" in s and s.count("pitcher-meta") == 2
    print(("OK" if ok else "BAD"), title.split(" - ")[0], "glove" if "🧤" in title else "")
