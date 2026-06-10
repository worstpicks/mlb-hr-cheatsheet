#!/usr/bin/env python3
"""Comprehensive June 10 sheet audit."""
from __future__ import annotations

import importlib.util
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
SHEET_DATE = "2026-06-10"

spec = importlib.util.spec_from_file_location("b", ROOT / f"build-sheet-{SHEET_DATE}.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

errors: list[str] = []

for g in build.games:
    for r in g["rows"]:
        name = r["name"]
        em = r["emojis"]
        is_fav = name in build.FAVS
        is_gem = name in build.GEMS
        if is_fav and "⭐" not in em:
            errors.append(f"FAV missing star: {name} -> {em}")
        if is_gem and "💎" not in em:
            errors.append(f"GEM missing diamond: {name} -> {em}")
        if not is_fav and "⭐" in em:
            errors.append(f"non-fav has star: {name} -> {em}")
        note = r.get("note", "")
        if is_fav and "Worst Pickz Favorite" not in note:
            errors.append(f"FAV missing note prefix: {name}")
        if is_gem and "Worst Pickz Hidden Gem" not in note:
            errors.append(f"GEM missing note prefix: {name}")

keys = []
for g in build.games:
    for r in g["rows"]:
        plain = r["name"].rsplit(" (", 1)[0]
        chip = r["chips"][0].replace("vs ", "")
        keys.append(f"{plain}|{chip}")
dup = [k for k, c in Counter(keys).items() if c > 1]
if dup:
    errors.append(f"dup matchups: {dup}")

for g in build.games:
    for r in g["rows"]:
        chip = r["chips"][0].replace("vs ", "")
        if chip in build.BUM_PITCHERS and "🧤" not in r["emojis"]:
            errors.append(f"bum row missing glove: {r['name']} vs {chip}")

for bum in build.BUM_PITCHERS:
    if not any(bum in g["title"] for g in build.games):
        errors.append(f"bum {bum} not in any game title")

text = PREVIEW.read_text(encoding="utf-8")
zone_count = len(re.findall(r"zoneScore:\s*[\d.]+", text))
if zone_count < 80:
    errors.append(f"zone data low: {zone_count}")

if f'<meta name="sheet-date" content="{SHEET_DATE}">' not in text:
    errors.append("sheet-date meta wrong")
if "Wednesday, June 10, 2026" not in text:
    errors.append("header date wrong")

stale = ["Shea Langeliers", "Colby Thomas", "Eric Lauer", "Tomoyuki Sugano", "Ronald Acuna Jr.", "Willi Castro", "Grant Holmes", "Logan Gilbert"]
for s in stale:
    if s in text:
        errors.append(f"stale prior-slate name in preview: {s}")

# Summary must match patch-computed picks (no stale Goblin block).
patch_globals: dict = {"__file__": str(ROOT / "patch-0610-preview.py"), "__name__": "__main__"}
cut = (ROOT / "patch-0610-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
exec(compile(cut + "\n", "patch-0610-preview.py", "exec"), patch_globals)
for r in patch_globals["top3"]:
    if r["name_plain"] not in text:
        errors.append(f"3-leg pick missing from preview summary: {r['name_plain']}")
if patch_globals["straight_o05"]["name_plain"] not in text:
    errors.append(f"O0.5 straight missing from preview: {patch_globals['straight_o05']['name_plain']}")
if patch_globals["straight_o15"]["name_plain"] not in text:
    errors.append(f"O1.5 straight missing from preview: {patch_globals['straight_o15']['name_plain']}")
for r in patch_globals["fav3"]:
    if r["name_plain"] not in text:
        errors.append(f"Favorite 3-leg missing from preview: {r['name_plain']}")
for r in patch_globals["top5"]:
    if r["name_plain"] not in text:
        errors.append(f"Top5 ticket missing from preview: {r['name_plain']}")
if patch_globals["load_pitchers_to_attack"]()[0]["pitcher"] not in text:
    errors.append("Top attack pitcher missing from preview summary")

if errors:
    print("FAIL:")
    for e in errors:
        print(f"  {e}")
    raise SystemExit(1)

print(f"FAVS={len(build.FAVS)} GEMS={len(build.GEMS)} BUMS={sorted(build.BUM_PITCHERS)}")
print(f"games={len(build.games)} rows={sum(len(g['rows']) for g in build.games)} zones={zone_count}")
print("OK comprehensive audit")
