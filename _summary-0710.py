#!/usr/bin/env python3
from pathlib import Path
import re
import importlib.util

html = Path("preview/index.html").read_text(encoding="utf-8")
root = Path("index.html").read_text(encoding="utf-8")
print("preview sheet", re.search(r'sheet-date" content="([^"]+)"', html).group(1))
print("root sheet", re.search(r'sheet-date" content="([^"]+)"', root).group(1))

spec = importlib.util.spec_from_file_location("b", "build-sheet-2026-07-10.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
print("props", sum(len(g["rows"]) for g in b.games), "games", len(b.games))
print("favs", len(b.FAVS), "gems", len(b.GEMS))
print("FAVS:", ", ".join(sorted(x.split(" (")[0] for x in b.FAVS)))
print("GEMS:", ", ".join(sorted(x.split(" (")[0] for x in b.GEMS)))
for g in b.games:
    if "🧤" in g["title"]:
        print("BUM", g["title"])
