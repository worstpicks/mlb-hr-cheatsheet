#!/usr/bin/env python3
"""Review 8/2 straights / goblin / top5 with key signals."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from game_row_enrich import enrich_games_list, plain_name
from goblin_hr_zone_fit import annotate_hr_zone_ranks

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-02"
html = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")

spec = importlib.util.spec_from_file_location("b0802", ROOT / f"build-sheet-{DATE}.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
games = enrich_games_list(build.games, DATE)

# LHP check
print("=== TITLES (LHP should show L) ===")
for g in build.games:
    t = g["title"]
    if any(x in t for x in ("Kay", "Freeland", "Jump", "Bennett", "Liberatore")):
        print(t)

print("\n=== STRAIGHTS FROM HTML ===")
for m in re.finditer(
    r'class="straight-pick-name">([^<]+).*?class="straight-pick-meta">([^<]+)',
    html,
    re.S,
):
    print(m.group(1).replace("&mdash;", "—"), "|", m.group(2)[:80])

# Find Crooks / Castro rows
print("\n=== KEY ROWS ===")
for g in games:
    for r in g["rows"]:
        n = plain_name(r)
        if n in ("Jimmy Crooks", "Willi Castro", "Salvador Perez", "Alec Burleson", "Munetaka Murakami"):
            print(
                f"{n:22} vs {(r.get('chips') or [''])[0]:16} "
                f"HR={r.get('hr')} near={r.get('near')} EV={r.get('ev')} "
                f"split={r.get('split')} risk={r.get('risk')} "
                f"park={r.get('parkPct')} zone={r.get('zoneScore')} "
                f"em={r.get('emojis')}"
            )

print("\n=== GOBLIN / FAV FROM HTML ===")
for label in ("3 Leg Homerun", "2 Leg Homerun", "Favorite 3 Leg"):
    idx = html.find(label)
    chunk = html[idx : idx + 1200] if idx >= 0 else ""
    names = re.findall(r'class="goblin-leg-name"[^>]*>([^<]+)', chunk)
    if not names:
        names = re.findall(r"goblin-player[^>]*>([^<]+)", chunk)
    print(label, names[:5] or "parse-miss")
