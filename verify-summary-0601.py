#!/usr/bin/env python3
import re
from collections import Counter
from pathlib import Path

t = Path("preview/index.html").read_text(encoding="utf-8")

GAME_RE = re.compile(r"<small>([A-Z]{2,3} @ [A-Z]{2,3})")


def game_counts(section_html: str) -> Counter:
    return Counter(GAME_RE.findall(section_html))


def max_game_count(section_html: str) -> int:
    counts = game_counts(section_html)
    return max(counts.values()) if counts else 0


top_tickets_m = re.search(
    r"Top 5 HR Tickets \(Attack \+ Weather \+ HR Risk\)</h3>.*?<div class=\"top-five-list\">(.*?)</div>\s*</div>",
    t,
    flags=re.DOTALL,
)
weather_heavy_m = re.search(
    r"Top 5 Weather Heavy HR Plays</h3>.*?<div class=\"summary-list\">(.*?)</div>\s*</div>",
    t,
    flags=re.DOTALL,
)
top_tickets_html = top_tickets_m.group(1) if top_tickets_m else ""
weather_heavy_html = weather_heavy_m.group(1) if weather_heavy_m else ""

checks = [
    ("Sheet date meta", 'content="2026-06-04"' in t),
    ("June 4 header", "Thursday, June 4, 2026 — Worst Pickz HR cheat sheet" in t),
    ("Straights section", "Worst Pickz Straights of the Day" in t),
    ("Goblin section", "Goblin's Insight" in t),
    ("Top tickets section", "Top 5 HR Tickets (Attack + Weather + HR Risk)" in t),
    ("Top weather section", "Top 5 Weather Games" in t),
    ("No stale Adames/Gordon straight", "Willy Adames &mdash; vs Gordon" not in t),
    ("No stale Duran/Bibee straight", "Jarren Duran &mdash; vs Bibee" not in t),
    ("Count sentence games", "across <strong>" in t and "games</strong>" in t),
    ("Count sentence rows", "covers <strong>" in t and "listed HR props</strong>" in t),
    ("Count sentence favorites", "with <strong>" in t and "Worst Pickz Favorite</strong> rows" in t),
    ("Top 5 HR Tickets max 2 per game", max_game_count(top_tickets_html) <= 2),
    ("Weather Heavy max 2 per game", max_game_count(weather_heavy_html) <= 2),
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
