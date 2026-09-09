#!/usr/bin/env python3
"""Print every 8/12 game header (title + park/pitcher meta) for eyeball review."""
import re
from pathlib import Path

html = Path("preview/index.html").read_text(encoding="utf-8")
block = re.search(r"const games = \[(.*?)\n\];", html, re.S).group(1)
titles = re.findall(r'title:\s*"([^"]+)"', block)
metas = re.findall(r'gameMeta:\s*"((?:\\.|[^"\\])*)"', block)
print(f"{len(titles)} titles / {len(metas)} metas\n")
for t, m in zip(titles, metas):
    s = m.encode().decode("unicode_escape")
    s = re.sub(r"<[^>]+>", "", s)
    print(t)
    print("   ", s.strip())
