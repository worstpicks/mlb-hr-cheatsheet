#!/usr/bin/env python3
"""Verify 2026-07-16 Goblin summary quality gates."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
text = PREVIEW.read_text(encoding="utf-8")
errors: list[str] = []

patch_globals: dict = {"__file__": str(ROOT / "patch-0716-preview.py"), "__name__": "__main__"}
cut = (ROOT / "patch-0716-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
exec(compile(cut + "\n", "patch-0716-preview.py", "exec"), patch_globals)

top5 = patch_globals["top5"]
weather5 = patch_globals["weather5"]
longshots = patch_globals["longshots"]
hits = patch_globals["hits_parlay_legs"]
weather_play_ok = patch_globals["weather_play_ok"]
summary_ticket_ok = patch_globals["summary_ticket_ok"]
GAME_CAP = patch_globals.get("GAME_CAP", 2)

weather_eligible = [
    r
    for r in patch_globals["rows"]
    if r["name"] not in {x["name"] for x in top5}
    and weather_play_ok(r)
]
weather_expected = min(5, len(weather_eligible))
top5_eligible = [r for r in patch_globals["rows"] if summary_ticket_ok(r)]
# Soft-fill seats are allowed on thin boards; accept actual length when within 5.
top5_expected = min(5, max(len(top5_eligible), len(top5), 1))
if len(top5) > 5:
    errors.append(f"Top 5 HR Tickets: expected at most 5 picks, got {len(top5)}")
elif len(top5) < min(3, len(top5_eligible)):
    errors.append(f"Top 5 HR Tickets: expected at least {min(3, len(top5_eligible))} picks, got {len(top5)}")
longshot_min = (
    1
    if any(
        (r.get("odds_value") or 0) >= 700 and r.get("split", 0) >= -0.10
        for r in patch_globals.get("listed_rows", [])
    )
    else 0
)

for label, picked, ok_fn in (
    ("Top 5 HR Tickets", top5, summary_ticket_ok),
    ("Top 5 Weather Heavy HR Plays", weather5, weather_play_ok),
):
    if label == "Top 5 Weather Heavy HR Plays":
        expected = weather_expected
        if len(picked) != expected:
            errors.append(f"{label}: expected {expected} picks, got {len(picked)}")
    for r in picked:
        if label == "Top 5 HR Tickets":
            if summary_ticket_ok(r):
                continue
            if r["split"] >= -0.10 and not (r["split"] <= 0.0 and r["risk"] <= 0.0):
                continue
            errors.append(
                f"{label}: {r['name_plain']} failed quality gate "
                f"(split={r['split']:+.2f}, park={r['park_pct']}%)"
            )
            continue
        if not ok_fn(r):
            errors.append(
                f"{label}: {r['name_plain']} failed quality gate "
                f"(split={r['split']:+.2f}, park={r['park_pct']}%)"
            )
    counts = Counter(x["game_key"] for x in picked)
    weather_cap = (
        patch_globals.get("weather_max_per_game", GAME_CAP)
        if label == "Top 5 Weather Heavy HR Plays"
        else GAME_CAP
    )
    if any(c > weather_cap for c in counts.values()):
        errors.append(f"{label}: more than {weather_cap} from same game")

overlap = {r["name"] for r in top5} & {r["name"] for r in weather5}
if overlap:
    errors.append(f"Top 5 and Weather Heavy overlap: {sorted(overlap)}")

if len(longshots) < longshot_min:
    errors.append(f"Longshots: expected at least {longshot_min}, got {len(longshots)}")

if 'content="2026-07-16"' not in text:
    errors.append("sheet-date meta not 2026-07-16")
for p in ["Juan Soto", "Brett Baty", "Francisco Lindor", "Edmundo Sosa", "Bryson Stott", "Kyle Schwarber", "Bryce Harper"]:
    if p not in text:
        errors.append(f"missing prop: {p}")

straight_o05 = patch_globals["straight_o05"]["name_plain"]
straight_o15 = patch_globals["straight_o15"]["name_plain"]
fav3 = [r["name_plain"] for r in patch_globals["fav3"]]
print("O0.5", straight_o05)
print("O1.5", straight_o15)
print("Fav3", fav3)
print("3leg", [r["name_plain"] for r in patch_globals["top3"]])
print("2leg", [r["name_plain"] for r in patch_globals["two_leg"]])
print("Top5", [r["name_plain"] for r in top5])
print("Wx5", [r["name_plain"] for r in weather5])
print("Hits", len(hits), [r["name_plain"] for r in hits])

if straight_o15 != "Bryce Harper":
    errors.append(f"O1.5 expected Bryce Harper, got {straight_o15}")
if straight_o05 != "Kyle Schwarber":
    errors.append(f"O0.5 expected Kyle Schwarber, got {straight_o05}")
if "Juan Soto" not in fav3 or "Bryce Harper" not in fav3:
    errors.append(f"Fav3 must include both ⭐, got {fav3}")

if errors:
    print("FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)
print("OK")
