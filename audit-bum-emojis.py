#!/usr/bin/env python3
"""Audit bum-on-mound glove tags in games block."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
html = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
block = re.search(r"const games = \[(.*?)\];", html, re.S)
if not block:
    sys.exit("games block not found")

text = block.group(0)
BUM_RE = re.compile(r"([\w.'\-\s]+?)\s*\U0001f9e4\s*\(", re.UNICODE)

missing = []
checked = 0
for gm in re.finditer(
    r'title: "([^"]+)".*?rows: \[(.*?)\]\s*\}',
    text,
    re.S,
):
    title = gm.group(1)
    bums = {m.group(1).strip().split()[-1].lower() for m in BUM_RE.finditer(title)}
    if not bums:
        continue
    for row in re.finditer(
        r'\{\s*name: "([^"]+)".*?emojis: "([^"]*)".*?chips: (\[[^\]]+\])',
        gm.group(2),
        re.S,
    ):
        checked += 1
        name = row.group(1)
        emojis = row.group(2)
        chips = json.loads(row.group(3))
        vs = chips[0].replace("vs ", "").strip().lower()
        if vs in bums and "\U0001f9e4" not in emojis:
            missing.append((name, vs, emojis))

if missing:
    print(f"MISSING GLOVE ({len(missing)}):")
    for name, vs, emojis in missing:
        print(f"  {name} vs {vs}: {emojis}")
    sys.exit(1)

print(f"OK — all {checked} rows facing bum SPs include glove in static emojis")
