#!/usr/bin/env python3
"""Hard verify June 20 sheet: duplicates, counts, summary, straights, bums."""
from __future__ import annotations

import importlib.util
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
text = PREVIEW.read_text(encoding="utf-8")
errors: list[str] = []

date_m = re.search(r'<meta name="sheet-date" content="([^"]+)">', text)
sheet_date = date_m.group(1) if date_m else ""
if sheet_date != "2026-06-20":
    errors.append(f"sheet-date wrong: {sheet_date}")
if "Saturday, June 20, 2026" not in text:
    errors.append("header weekday wrong: expected Saturday, June 20, 2026")

bs = importlib.util.spec_from_file_location("build", ROOT / f"build-sheet-{sheet_date}.py")
build = importlib.util.module_from_spec(bs)
bs.loader.exec_module(build)

row_pat = re.compile(
    r'\{ name: "([^"]+)"[^}]*emojis: "([^"]*)"[^}]*note: "([^"]*)"[^}]*chips: \[(.*?)\]',
    re.DOTALL,
)
game_chunks = re.split(r"\{ title: ", text)[1:]
all_names: list[str] = []
matchup_keys: list[str] = []

for chunk in game_chunks:
    tm = re.match(r'"([^"]+)"', chunk)
    if not tm:
        continue
    for name, emojis, note, chips_raw in row_pat.findall(chunk):
        all_names.append(name)
        chips = re.findall(r'"([^"]+)"', chips_raw)
        chip = next((c.replace("vs ", "") for c in chips if c.startswith("vs ")), "")
        plain = name.rsplit(" (", 1)[0]
        matchup_keys.append(f"{plain}|{chip}")

name_counts = Counter(all_names)
dup_names = [n for n, c in name_counts.items() if c > 1]
if dup_names:
    errors.append(f"duplicate batter rows: {dup_names}")

match_counts = Counter(matchup_keys)
dup_matchups = [k for k, c in match_counts.items() if c > 1]
if dup_matchups:
    errors.append(f"duplicate batter-SP matchups: {dup_matchups}")

expected_games = len(build.games)
expected_rows = sum(len(g["rows"]) for g in build.games)
expected_favs = len(build.FAVS)
row_count = len(row_pat.findall(text))

if f"across <strong>{expected_games} games</strong>" not in text:
    errors.append(f"summary game count not {expected_games}")
if f"covers <strong>{expected_rows} listed HR props</strong>" not in text:
    errors.append(f"summary row count not {expected_rows}")
if f"<strong>{expected_favs} Worst Pickz Favorite</strong>" not in text:
    errors.append(f"summary fav count not {expected_favs}")

o05_m = re.search(
    r'straight-pick-hero">\s*<span class="straight-pick-tag">Over 0\.5 HR Straight</span>[\s\S]*?straight-pick-name">([^<]+)</strong>',
    text,
)
o15_m = re.search(
    r'straight-pick-hero--o15">[\s\S]*?straight-pick-name">([^<]+)</strong>',
    text,
)
if o05_m and o15_m:
    o05_game = re.search(
        r'straight-pick-hero">\s*<span class="straight-pick-tag">Over 0\.5 HR Straight</span>.*?Score \d+ &middot; ([A-Z]{2,3} @ [A-Z]{2,3})',
        text,
        re.DOTALL,
    )
    o15_game = re.search(
        r'straight-pick-hero--o15">.*?Score \d+ &middot; ([A-Z]{2,3} @ [A-Z]{2,3})',
        text,
        re.DOTALL,
    )
    if o05_game and o15_game and o05_game.group(1) == o15_game.group(1):
        errors.append(f"straights same game: {o05_game.group(1)}")

if "Homerun Form" not in text:
    errors.append("missing Homerun Form in damage window")

zone_row_count = len(re.findall(r"zoneScore:\s*[\d.]+", text))
zone_min = min(expected_rows, max(45, expected_rows - 12))
if zone_row_count < zone_min:
    errors.append(f"zone data missing from games block ({zone_row_count} zoneScore fields; need {zone_min}+)")
if "function zoneFitBoxHtml" not in text or "pick-row-zone" not in text:
    errors.append("zone fit UI helpers/CSS missing from preview")
if "Zone Fit Score" not in text:
    errors.append("missing Zone Fit Score in damage window")

bum_titles = [g["title"] for g in build.games if "🧤" in g["title"]]
if not bum_titles:
    errors.append("no bum gloves in game titles")
for bum in build.BUM_PITCHERS:
    found_title = any(bum in t for t in bum_titles)
    if not found_title:
        errors.append(f"bum {bum} in BUM_PITCHERS but not in any game title glove")

for name in build.FAVS:
    if f'name: "{name}"' not in text:
        errors.append(f"missing favorite row: {name}")
    else:
        chunk = text.split(f'name: "{name}"', 1)[1][:400]
        if "⭐" not in chunk:
            errors.append(f"favorite missing star: {name}")

gems = getattr(build, "GEMS", set())
for name in gems:
    if f'name: "{name}"' not in text:
        errors.append(f"missing hidden gem row: {name}")
    else:
        chunk = text.split(f'name: "{name}"', 1)[1][:500]
        if "💎" not in chunk:
            errors.append(f"hidden gem missing diamond: {name}")
        if "Worst Pickz Hidden Gem" not in chunk:
            errors.append(f"hidden gem missing note prefix: {name}")

stale_june19_only = [
    "Colt Keith", "Ben Rice", "Matt McLain", "Heriberto Hernandez", "Jackson Chourio",
    "Jackson Holliday", "Colson Montgomery", "Paul Goldschmidt", "James Wood",
    "Jeffrey Springs", "Randy Vasquez", "Tanner Bibee", "Kyle Freeland",
    "Juan Soto", "Spencer Torkelson",
]
for stale in stale_june19_only:
    if stale in all_names or any(n.startswith(f"{stale} (") for n in all_names):
        errors.append(f"stale prior-slate name still in preview rows: {stale}")

summary_start = text.find('class="summary-card full-width straight-of-day-card"')
summary_end = text.find('class="summary-card emoji-key-card"')
if summary_start != -1 and summary_end != -1 and summary_end > summary_start:
    summary_block = text[summary_start:summary_end]
    stale_summary = [
        "Juan Soto", "Colson Montgomery", "Randal Grichuk", "Ryan Weathers",
        "Matthew Liberatore", "Jazz Chisholm", "Michael Massey", "Drake Baldwin",
    ]
    for stale in stale_summary:
        if stale in summary_block:
            errors.append(f"stale prior-slate name in Goblin/summary block: {stale}")
    if "Kody Clemens" not in summary_block and "Endy Rodriguez" not in summary_block:
        errors.append("summary straights missing expected 6/20 picks")
else:
    errors.append("could not locate summary block for stale check")

if errors:
    print("FAIL hard-verify-0620:")
    for e in errors:
        print(f"  {e}")
    raise SystemExit(1)

print("OK hard-verify-0620")
print(f"  {expected_rows} rows, {expected_games} games, {expected_favs} favorites")
print(f"  bum games: {len(bum_titles)}")
if o05_m and o15_m:
    print(f"  O0.5: {o05_m.group(1)}")
    print(f"  O1.5: {o15_m.group(1)}")
