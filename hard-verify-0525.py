#!/usr/bin/env python3
"""Hard verify for 2026-05-25 deploy."""
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
html = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
manifest = json.loads((ROOT / "preview" / "sheets-manifest.json").read_text(encoding="utf-8"))

spec = importlib.util.spec_from_file_location("bs525", ROOT / "build-sheet-2026-05-25.py")
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)

errors = []
games_block = re.search(r"const games = \[(.*?)\];", html, re.S)
if not games_block:
    errors.append("games block missing")
    sys.exit(1)

block = games_block.group(0)
names = re.findall(r'name: "([^"]+)"', block)
titles = block.count("title:")
fav_block = re.search(r"WORST_PICKZ_FAVORITE_NAMES = new Set\(\[(.*?)\]\)", html, re.S)
favs = re.findall(r'"([^"]+)"', fav_block.group(1)) if fav_block else []

if titles != 13:
    errors.append(f"expected 13 games, got {titles}")
if len(names) != 53:
    errors.append(f"expected 53 rows, got {len(names)}")
if len(favs) != 8:
    errors.append(f"expected 8 favorites, got {len(favs)}")

submitted = set(bs.PLAYER_TEAMS.keys())
sheet = set(names)
missing = sorted(submitted - sheet)
extra = sorted(sheet - submitted)
if missing:
    errors.append(f"missing props: {missing}")
if extra:
    errors.append(f"extra props: {extra}")

if re.search(r'sheet-date" content="2026-05-25"', html) is None:
    errors.append("sheet-date not 2026-05-25")
if "Sunday, May 25, 2026" not in html:
    errors.append("header date missing May 25")
if "53 listed HR props" not in html or "13 games" not in html or "8 Worst Pickz Favorite" not in html:
    errors.append("count sentence wrong")
if manifest["sheets"][0]["date"] != "2026-05-25":
    errors.append("manifest current not 2026-05-25")

if "Luzardo" in block and re.search(r"Luzardo\s*🧤", block):
    errors.append("Luzardo wrongly tagged as bum in games block")

for bad in ["vs Bradish"]:
    if 'Pete Alonso' in block:
        alonso = re.search(r'Pete Alonso \(R\)"[^}]*chips: \[(.*?)\]', block, re.S)
        if alonso and "vs Bradish" in alonso.group(1):
            errors.append("Pete Alonso still vs Bradish (same-team mixup)")

gambly = re.findall(r"data-goblin-gambly-lines='([^']+)'", html)
if len(gambly) != 4:
    errors.append(f"expected 4 gambly buttons, got {len(gambly)}")

glove_titles = len(re.findall(r"🧤", block))
if glove_titles < 13:
    errors.append(f"expected at least 13 bum gloves in titles, got {glove_titles}")

if "Goblin's Insight" not in html:
    errors.append("missing Goblin's Insight")

for stale in ["Juan Soto", "Mike Trout", "Braydon Fisher", "Jose Soriano"]:
    if stale in html and f"{stale} - Over 0.5 homerun" in html:
        errors.append(f"stale Goblin parlay name: {stale}")

expected_3leg = {"James Wood", "Ben Rice", "Miguel Vargas"}
expected_fav = {"Miguel Vargas", "Jac Caglianone", "Brandon Lowe"}
if gambly:
    leg3 = {x.split(" - ")[0] for x in json.loads(gambly[0].replace("&quot;", '"'))}
    fav3 = {x.split(" - ")[0] for x in json.loads(gambly[3].replace("&quot;", '"'))}
    if leg3 != expected_3leg:
        errors.append(f"3-leg HR mismatch: got {sorted(leg3)}")
    if fav3 != expected_fav:
        errors.append(f"favorite 3-leg mismatch: got {sorted(fav3)}")

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
