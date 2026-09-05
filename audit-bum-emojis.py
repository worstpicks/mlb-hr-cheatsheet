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
# The game objects carry several bracketed fields (top3, top3Detail) between the
# title and the rows array, and rows entries hold nested arrays of their own -- so
# the old `rows: \[(.*?)\]\s*\}` pattern matched NOTHING and this audit quietly
# checked zero rows. Anchor on the shape the deep audit uses: the rows array closes
# on its own line at the game's indent level.
GAME_RE = re.compile(
    r'\{\s*title: "([^"]+)".*?\n        rows: \[(.*?)\n        \],', re.S
)

bum_games = 0
for gm in GAME_RE.finditer(text):
    title = gm.group(1)
    bums = {m.group(1).strip().split()[-1].lower() for m in BUM_RE.finditer(title)}
    if not bums:
        continue
    bum_games += 1
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

# A vacuous pass is the failure this audit actually had: it printed OK while
# matching no games at all. Cross-check against the gloves present in the titles.
titles_with_glove = sum(
    1 for t in re.findall(r'title: "([^"]+)"', text) if '\U0001f9e4' in t
)
if titles_with_glove and not bum_games:
    sys.exit(
        f'audit is not matching games: {titles_with_glove} title(s) carry a glove '
        'but the game regex found none — fix the parser, do not trust this OK'
    )
if bum_games and not checked:
    sys.exit(f'{bum_games} bum game(s) matched but no rows parsed inside them')

print(
    f'OK — all {checked} rows in {bum_games} bum game(s) facing bum SPs '
    'include glove in static emojis'
)
