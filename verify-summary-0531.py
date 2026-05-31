#!/usr/bin/env python3
from pathlib import Path

t = Path("preview/index.html").read_text(encoding="utf-8")

checks = [
    ("Sheet date meta", 'content="2026-05-31"' in t),
    ("May 31 header", "Sunday, May 31, 2026 — Worst Pickz HR cheat sheet" in t),
    ("Straights section", "Worst Pickz Straights of the Day" in t),
    ("Goblin section", "Goblin's Insight" in t),
    ("Top 5 section", "Top 5 HR Tickets (Holistic)" in t),
    ("Top weather section", "Top 5 Weather Games" in t),
    ("No stale Soto/Meyer straight", "Juan Soto &mdash; vs Max Meyer" not in t),
    ("No stale Adames/Feltner straight", "Willy Adames &mdash; vs Ryan Feltner" not in t),
    ("Count sentence games", "across <strong>14 games</strong>" in t),
    ("Count sentence rows", "covers <strong>71 listed HR props</strong>" in t),
    ("Count sentence favorites", "with <strong>20 Worst Pickz Favorite</strong> rows" in t),
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
