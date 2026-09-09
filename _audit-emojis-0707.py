#!/usr/bin/env python3
"""Audit fav/gem/bum emojis on 7/7 preview."""
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
html = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")

spec = importlib.util.spec_from_file_location("b", ROOT / "build-sheet-2026-07-07.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

errors = []
rows = re.findall(
    r'name: "([^"]+)".*?emojis: "([^"]*)".*?chips: (\[[^\]]+\])',
    html,
    re.S,
)

print(f"Rows parsed: {len(rows)}")
print(f"Expected props: 75")
print(f"FAVS: {len(build.FAVS)} GEMS: {len(build.GEMS)} BUM_MATCHUPS: {len(build.BUM_MATCHUPS)}")

for name, emojis, chips_raw in rows:
    import json
    chips = json.loads(chips_raw)
    vs = chips[0].replace("vs ", "").strip()
    game_key = None
    for g in re.finditer(r'title: "([^"]+)".*?rows: \[(.*?)\]\s*\}', html, re.S):
        if f'name: "{name}"' in g.group(2):
            game_key = g.group(1).split(" - ")[0]
            break

    if name in build.FAVS and "⭐" not in emojis:
        errors.append(f"FAV missing ⭐: {name} emojis={emojis!r}")
    if name in build.GEMS and "💎" not in emojis:
        errors.append(f"GEM missing 💎: {name} emojis={emojis!r}")

    if game_key:
        if (game_key, vs) in build.BUM_MATCHUPS or (game_key, vs.split()[0]) in build.BUM_MATCHUPS:
            for need in ("⚾", "🕊️", "🧤"):
                if need not in emojis:
                    errors.append(f"BUM row missing {need}: {name} vs {vs} emojis={emojis!r}")

# Bum titles
bum_titles = re.findall(r'title: "([^"]*🧤[^"]*)"', html)
print(f"\nBum titles ({len(bum_titles)}):")
for t in bum_titles:
    print(f"  {t}")

if errors:
    print(f"\nFAIL {len(errors)} emoji issues:")
    for e in errors:
        print(f"  {e}")
    raise SystemExit(1)
print("\nOK all fav/gem/bum emojis")
