#!/usr/bin/env python3
"""Hard verify for 2026-05-22 deploy."""
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
html = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
manifest = json.loads((ROOT / "preview" / "sheets-manifest.json").read_text(encoding="utf-8"))
EXCLUDED_MATCHUP = "HOU @ CHC"
EXCLUDED_SHORT = {
    "Ian Happ",
    "Michael Conforto",
    "Michael Busch",
    "Yordan Alvarez",
    "Isaac Paredes",
    "Christian Walker",
}
errors = []
spec = importlib.util.spec_from_file_location("build0522", ROOT / "build-sheet-2026-05-22.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

games_block = re.search(r"const games = \[(.*?)\];", html, re.S).group(0)
names = re.findall(r'name: "([^"]+)"', games_block)
titles = games_block.count("title:")
fav_block = re.search(r"WORST_PICKZ_FAVORITE_NAMES = new Set\(\[(.*?)\]\)", html, re.S).group(1)
favs = re.findall(r'"([^"]+)"', fav_block)

if titles != 15:
    errors.append(f"expected 15 games, got {titles}")
if len(names) != 73:
    errors.append(f"expected 73 rows, got {len(names)}")
if len(favs) != 17:
    errors.append(f"expected 17 favorites, got {len(favs)}")

submitted = set(mod.PLAYER_TEAMS.keys())
sheet = set(names)
missing = sorted(submitted - sheet)
extra = sorted(sheet - submitted)
if missing:
    errors.append(f"missing props: {missing}")
if extra:
    errors.append(f"extra props: {extra}")

if re.search(r'sheet-date" content="2026-05-22"', html) is None:
    errors.append("sheet-date not 2026-05-22")
if "Friday, May 22, 2026" not in html:
    errors.append("header date missing May 22")
if "73 listed HR props" not in html or "15 games" not in html or "17 Worst Pickz Favorite" not in html:
    errors.append("count sentence wrong")
if manifest["sheets"][0]["date"] != "2026-05-22":
    errors.append("manifest current not 2026-05-22")
if not (ROOT / "preview" / "archive" / "2026-05-21.html").exists():
    errors.append("missing archive 2026-05-21.html")

arch = (ROOT / "preview" / "archive" / "2026-05-21.html").read_text(encoding="utf-8")
if 'src="../assets/' not in arch:
    errors.append("archive missing ../assets paths")

gambly = re.findall(r"data-goblin-gambly-lines='([^']+)'", html)
if len(gambly) != 4:
    errors.append(f"expected 4 gambly buttons, got {len(gambly)}")
parsed = []
for attr in gambly:
    try:
        parsed.append(json.loads(attr.replace("&quot;", '"')))
    except json.JSONDecodeError as e:
        errors.append(f"gambly json parse fail: {e}")

if len(parsed) >= 2:
    leg3 = {x.split(" - ")[0] for x in parsed[0]}
    leg2 = {x.split(" - ")[0] for x in parsed[1]}
    if leg3 & leg2:
        errors.append(f"3-leg and 2-leg HR overlap: {leg3 & leg2}")
    expected3 = {"Kyle Schwarber", "Bobby Witt Jr.", "Austin Riley"}
    expected2 = {"Julio Rodriguez", "Elly De La Cruz"}
    if leg3 != expected3:
        errors.append(f"3-leg HR mismatch: got {sorted(leg3)}")
    if leg2 != expected2:
        errors.append(f"2-leg HR mismatch: got {sorted(leg2)}")
    if leg3 & EXCLUDED_SHORT:
        errors.append(f"3-leg HR includes finished HOU @ CHC players: {sorted(leg3 & EXCLUDED_SHORT)}")
    if leg2 & EXCLUDED_SHORT:
        errors.append(f"2-leg HR includes finished HOU @ CHC players: {sorted(leg2 & EXCLUDED_SHORT)}")
if len(parsed) >= 3:
    if len(parsed[2]) != 11:
        errors.append(f"hits parlay should be 11 legs, got {len(parsed[2])}")
    expected_hits = {
        "Kyle Schwarber",
        "Ben Rice",
        "Juan Soto",
        "Austin Riley",
        "Bobby Witt Jr.",
        "Corbin Carroll",
        "Julio Rodriguez",
        "Mike Yastrzemski",
        "Elly De La Cruz",
        "Max Muncy",
        "Yandy Diaz",
    }
    hits = {x.split(" - ")[0] for x in parsed[2]}
    if hits != expected_hits:
        errors.append(f"hits parlay mismatch: got {sorted(hits)}")
    if hits & EXCLUDED_SHORT:
        errors.append(f"hits parlay includes finished HOU @ CHC players: {sorted(hits & EXCLUDED_SHORT)}")

if EXCLUDED_MATCHUP not in html or "excluded from parlays" not in html.lower():
    errors.append("missing HOU @ CHC parlay exclusion note")

glove_rows = len(re.findall(r"emojis: \"[^\"]*🧤", games_block))
if glove_rows < 40:
    errors.append(f"expected at least 40 glove emoji rows facing bums, got {glove_rows}")

emoji_stars = len(re.findall(r"emojis: \"[^\"]*⭐", games_block))
if emoji_stars != 17:
    errors.append(f"expected 17 star emoji rows, got {emoji_stars}")

glove_titles = len(re.findall(r"🧤", games_block))
if glove_titles < 18:
    errors.append(f"expected at least 18 bum gloves in games block, got {glove_titles}")

for fav in favs:
    if fav not in sheet:
        errors.append(f"favorite not on sheet: {fav}")

if "Goblin's Insight" not in html:
    errors.append("missing Goblin's Insight")
if "HR Props That Cashed" not in html:
    errors.append("missing HR Props That Cashed heading")
if "Listed Batters Who Recorded a Hit" not in html:
    errors.append("missing hit heading")

# confidence tier function presence
if "confidenceTierText" not in html:
    errors.append("confidence tier logic missing")

if "May 21, 2026 — Worst Pickz" in html:
    errors.append("stale May 21 header in current sheet")

dup_names = [n for n in names if names.count(n) > 1]
if dup_names:
    errors.append(f"duplicate row names: {sorted(set(dup_names))}")

if errors:
    print("HARD VERIFY FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print("HARD VERIFY OK")
print(f"  games={titles} rows={len(names)} favs={len(favs)} gambly={len(gambly)}")
print(f"  3-leg HR: {[x.split(' - ')[0] for x in parsed[0]]}")
print(f"  2-leg HR: {[x.split(' - ')[0] for x in parsed[1]]}")
print(f"  hits parlay legs: {len(parsed[2])}")
