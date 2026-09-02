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

patch_globals: dict = {"__file__": str(ROOT / "patch-0902-preview.py"), "__name__": "__main__"}
cut = (ROOT / "patch-0902-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
exec(compile(cut + "\n", "patch-0902-preview.py", "exec"), patch_globals)

top5 = patch_globals["top5"]
weather5 = patch_globals["weather5"]
longshots = patch_globals["longshots"]
hits = patch_globals["hits_parlay_legs"]
weather_play_ok = patch_globals["weather_play_ok"]
summary_ticket_ok = patch_globals["summary_ticket_ok"]
longshot_ok = patch_globals["longshot_ok"]

weather_eligible = [
    r
    for r in patch_globals["rows"]
    if r["name"] not in {x["name"] for x in top5}
    and weather_play_ok(r)
]
weather_expected = min(5, len(weather_eligible))
top5_eligible = [r for r in patch_globals["rows"] if summary_ticket_ok(r)]
top5_expected = min(5, max(len(top5_eligible), 1))
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
    expected = weather_expected if label == "Top 5 Weather Heavy HR Plays" else top5_expected
    if len(picked) != expected:
        errors.append(f"{label}: expected {expected} picks, got {len(picked)}")
    for r in picked:
        if label == "Top 5 HR Tickets":
            # Soft-fill seats allowed at split >= -0.10 with usable risk; reject harsh negatives.
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
    if label == "Top 5 Weather Heavy HR Plays":
        # The patch deliberately lets ONE standout park stack (weather_game_caps),
        # so read the per-game caps instead of asserting a flat 2 -- checking the
        # flat number failed a correct sheet on 2026-08-20, when Milwaukee's +22%
        # hand park was the slate's only extreme game.
        base_cap = patch_globals.get("weather_max_per_game", 2)
        game_caps = patch_globals.get("weather_game_caps") or {}
        over = [f"{g} ({c}>{game_caps.get(g, base_cap)})"
                for g, c in counts.items() if c > game_caps.get(g, base_cap)]
        if over:
            errors.append(f"{label}: over per-game cap: {', '.join(over)}")
    elif any(c > 2 for c in counts.values()):
        errors.append(f"{label}: more than 2 from same game")

for r in weather5:
    park = patch_globals["effective_park_pct"](r)
    if r["split"] < 0.0:
        allowed = (park >= 35 and r["score"] >= 75 and (r["hr"] >= 1 or r["near"] >= 2)) or (
            park >= 28 and r["split"] >= -0.30 and r["score"] >= 68 and (r["hr"] >= 1 or r["near"] >= 1)
        ) or (
            park >= 8 and r["split"] >= -0.10 and r["score"] >= 82
        )
        if not allowed:
            errors.append(f"Weather Heavy negative split: {r['name_plain']}")
    if r["split"] == 0.0 and r["risk"] == 0.0:
        errors.append(f"Weather Heavy 0/0 lane: {r['name_plain']}")

overlap = {r["name"] for r in top5} & {r["name"] for r in weather5}
if overlap:
    errors.append(f"Top 5 and Weather Heavy overlap: {sorted(overlap)}")

for r in longshots:
    if r["split"] < -0.10:
        errors.append(f"Longshot negative split: {r['name_plain']}")
    if (r["odds_value"] or 0) < 700:
        errors.append(f"Longshot not +700+: {r['name_plain']}")

if len(longshots) < longshot_min:
    errors.append(f"Longshots: expected at least {longshot_min}, got {len(longshots)}")
if len(longshots) > 4:
    errors.append(f"Longshots: expected at most 4, got {len(longshots)}")

from goblin_hits_parlay import SPLIT_HARD_FLOOR

for r in hits:
    if r["split"] < SPLIT_HARD_FLOOR:
        errors.append(
            f"Hits parlay extreme negative split ({r['split']:+.2f} < {SPLIT_HARD_FLOOR}): {r['name_plain']}"
        )
    if patch_globals["row_high_whiff"](r, for_hits=True):
        errors.append(f"Hits parlay high-whiff leg: {r['name_plain']}")
if len(hits) != 11:
    errors.append(f"Hits parlay: expected 11 legs, got {len(hits)}")
n_games = len({r.get("game_key") for r in patch_globals["rows"] if r.get("game_key")})
# Thin slates (≤5 games) cannot fill 11 legs at 2/game — allow ceil(11/n).
# Read the cap from the rubric module rather than restating it. The two drifted on
# 2026-08-20: the rubric moved to 4 per game (a parlay is not a portfolio -- see
# goblin_hits_parlay) while this check still demanded 2, and failed a correct sheet.
from goblin_hits_parlay import MAX_PER_GAME as _HITS_MAX_PER_GAME, TICKET_LEGS as _HITS_LEGS

hits_game_cap = (
    _HITS_MAX_PER_GAME
    if n_games >= 6
    else max(_HITS_MAX_PER_GAME, (_HITS_LEGS + max(n_games, 1) - 1) // max(n_games, 1))
)
per_game = Counter(r.get("game_key") for r in hits)
over_game = [g for g, c in per_game.items() if c > hits_game_cap]
if over_game:
    errors.append(f"Hits parlay >{hits_game_cap} legs in game(s): {over_game}")

wh_block = text.split("Top 5 Weather Heavy HR Plays")[1].split("Best longshot")[0]
if "split -" in wh_block:
    errors.append("Weather Heavy HTML contains negative split play")

if errors:
    print("FAIL verify-summary-0902:")
    for e in errors:
        print(f"  {e}")
    raise SystemExit(1)

print("OK verify-summary-0902")
print("  Top5:", [r["name_plain"] for r in top5])
print("  Weather5:", [r["name_plain"] for r in weather5])
print("  Longshots:", [r["name_plain"] for r in longshots])
print("  Hits:", [r["name_plain"] for r in hits])
