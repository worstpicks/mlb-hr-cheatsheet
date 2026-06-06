#!/usr/bin/env python3
"""Verify Goblin summary tables use quality gates (no negative-split weather plays, etc.)."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
text = PREVIEW.read_text(encoding="utf-8")
errors: list[str] = []

patch_globals: dict = {"__file__": str(ROOT / "patch-0606-preview.py"), "__name__": "__main__"}
cut = (ROOT / "patch-0606-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
exec(compile(cut + "\n", "patch-0606-preview.py", "exec"), patch_globals)

top5 = patch_globals["top5"]
weather5 = patch_globals["weather5"]
longshots = patch_globals["longshots"]
hits = patch_globals["hits_parlay_legs"]
weather_play_ok = patch_globals["weather_play_ok"]
summary_ticket_ok = patch_globals["summary_ticket_ok"]
longshot_ok = patch_globals["longshot_ok"]

for label, picked, ok_fn in (
    ("Top 5 HR Tickets", top5, summary_ticket_ok),
    ("Top 5 Weather Heavy HR Plays", weather5, weather_play_ok),
):
    if len(picked) != 5:
        errors.append(f"{label}: expected 5 picks, got {len(picked)}")
    for r in picked:
        if not ok_fn(r):
            errors.append(
                f"{label}: {r['name_plain']} failed quality gate "
                f"(split={r['split']:+.2f}, park={r['park_pct']}%)"
            )
    counts = Counter(x["game_key"] for x in picked)
    if any(c > 2 for c in counts.values()):
        errors.append(f"{label}: more than 2 from same game")

for r in weather5:
    if r["split"] < 0.0:
        errors.append(f"Weather Heavy negative split: {r['name_plain']}")
    if r["split"] <= 0.0 and r["risk"] <= 0.0:
        errors.append(f"Weather Heavy 0/0 lane: {r['name_plain']}")

overlap = {r["name"] for r in top5} & {r["name"] for r in weather5}
if overlap:
    errors.append(f"Top 5 and Weather Heavy overlap: {sorted(overlap)}")

for r in longshots:
    if r["split"] < 0.0:
        errors.append(f"Longshot negative split: {r['name_plain']}")
    if (r["odds_value"] or 0) < 700:
        errors.append(f"Longshot not +700+: {r['name_plain']}")

if len(longshots) < 3:
    errors.append(f"Longshots: expected at least 3, got {len(longshots)}")
if len(longshots) > 4:
    errors.append(f"Longshots: expected at most 4, got {len(longshots)}")

for r in hits:
    if r["split"] < 0.0:
        errors.append(f"Hits parlay negative split: {r['name_plain']}")

wh_block = text.split("Top 5 Weather Heavy HR Plays")[1].split("Best longshot")[0]
if "split -" in wh_block:
    errors.append("Weather Heavy HTML contains negative split play")

if errors:
    print("FAIL verify-summary-0606:")
    for e in errors:
        print(f"  {e}")
    raise SystemExit(1)

print("OK verify-summary-0606")
print("  Top5:", [r["name_plain"] for r in top5])
print("  Weather5:", [r["name_plain"] for r in weather5])
print("  Longshots:", [r["name_plain"] for r in longshots])
print("  Hits:", [r["name_plain"] for r in hits])
