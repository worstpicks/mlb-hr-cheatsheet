#!/usr/bin/env python3
from pathlib import Path

t = Path("preview/index.html").read_text(encoding="utf-8")

checks = [
    ("Sheet date meta", 'content="2026-06-01"' in t),
    ("June 1 header", "Monday, June 1, 2026 — Worst Pickz HR cheat sheet" in t),
    ("Straights section", "Worst Pickz Straights of the Day" in t),
    ("Goblin section", "Goblin's Insight" in t),
    ("Top 5 section", "Top 5 HR Tickets (Holistic)" in t),
    ("Top weather section", "Top 5 Weather Games" in t),
    ("No stale Adames/Gordon straight", "Willy Adames &mdash; vs Gordon" not in t),
    ("No stale Duran/Bibee straight", "Jarren Duran &mdash; vs Bibee" not in t),
    ("Count sentence games", "across <strong>9 games</strong>" in t),
    ("Count sentence rows", "covers <strong>60 listed HR props</strong>" in t),
    ("Count sentence favorites", "with <strong>9 Worst Pickz Favorite</strong> rows" in t),
]

failed = []
for name, ok in checks:
    status = "OK" if ok else "FAIL"
    print(f"{status}  {name}")
    if not ok:
        failed.append(name)

if failed:
    raise SystemExit(f"{len(failed)} check(s) failed")
print("\nAll summary checks passed.")
