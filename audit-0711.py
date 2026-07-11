#!/usr/bin/env python3
"""Quick audit for 2026-07-11 sheet before push."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
html = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
errors: list[str] = []

EXPECTED_GAMES = 7
EXPECTED_PROPS = 25
ZONE_MIN = min(EXPECTED_PROPS, max(45, EXPECTED_PROPS - 20))

if 'sheet-date" content="2026-07-11"' not in html:
    errors.append("wrong sheet-date meta")

games_block = re.search(r"const games = \[(.*?)\];", html, re.S)
games_text = games_block.group(1) if games_block else ""
if games_block:
    game_count = games_text.count("title:")
    park_count = games_text.count("parkPct:")
    lhb_count = games_text.count("parkLhbPct:")
    rhb_count = games_text.count("parkRhbPct:")
    meta_park = games_text.count("Park ")
    if not (park_count == lhb_count == rhb_count == game_count == EXPECTED_GAMES):
        errors.append(
            f"park fields mismatch: games={game_count} park={park_count} "
            f"lhb={lhb_count} rhb={rhb_count} expected={EXPECTED_GAMES}"
        )
    if meta_park < EXPECTED_GAMES:
        errors.append(f"gameMeta missing park lines: {meta_park}")

zc = html.count("zoneScore:")
if zc < ZONE_MIN:
    errors.append(f"zoneScore count {zc} < {ZONE_MIN} props")

for needle in ("Homerun Form", "Split + Risk + Park + Form + Zone", "Worst Pickz Straights"):
    if needle not in html:
        errors.append(f"missing feature: {needle}")

if not (ROOT / "preview" / "data" / "research-2026-07-11.json").exists():
    errors.append("missing preview/data/research-2026-07-11.json")
if not (ROOT / "preview" / "data" / "park-factors-2026-07-11.json").exists():
    errors.append("missing preview/data/park-factors-2026-07-11.json")

if bum_titles := re.findall(r'title: "([^"]*🧤[^"]*)"', html):
    if games_block:
        for gm in re.finditer(r'title: "([^"]+)".*?rows: \[(.*?)\]\s*\}', games_text, re.S):
            title = gm.group(1)
            if "🧤" not in title:
                continue
            bum_names = set()
            for part in title.split(" vs "):
                if "🧤" in part:
                    name = part.split("🧤")[0].split("(")[0].split("-")[-1].strip().split()[-1].lower()
                    bum_names.add(name)
            for row in re.finditer(
                r'name: "([^"]+)".*?emojis: "([^"]*)".*?chips: (\[[^\]]+\])', gm.group(2), re.S
            ):
                chips = json.loads(row.group(3))
                vs = chips[0].replace("vs ", "").strip().lower()
                if vs in bum_names:
                    em = row.group(2)
                    for need in ("⚾", "🕊️", "🧤"):
                        if need not in em:
                            errors.append(f"bum row missing {need}: {row.group(1)} vs {vs} emojis={em}")

spec = importlib.util.spec_from_file_location("b", ROOT / "build-sheet-2026-07-11.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

for fav in build.FAVS:
    if f'name: "{fav}"' not in html:
        errors.append(f"missing favorite row: {fav}")
        continue
    m = re.search(rf'name: "{re.escape(fav)}".*?emojis: "([^"]*)"', html)
    if m and "⭐" not in m.group(1) and "&#11088;" not in html[m.start() : m.start() + 200]:
        errors.append(f"favorite missing star: {fav} emojis={m.group(1)}")

for gem in build.GEMS:
    if f'name: "{gem}"' not in html:
        errors.append(f"missing gem row: {gem}")
        continue
    m = re.search(rf'name: "{re.escape(gem)}".*?emojis: "([^"]*)"', html)
    if m and "💎" not in m.group(1):
        errors.append(f"gem missing diamond: {gem} emojis={m.group(1)}")

manifest = json.loads((ROOT / "preview" / "sheets-manifest.json").read_text(encoding="utf-8"))
if manifest["sheets"][0]["date"] != "2026-07-11":
    errors.append("manifest current slate not 2026-07-11")

if errors:
    print("FAIL audit-0711:")
    for e in errors:
        print(" ", e)
    raise SystemExit(1)

print(
    f"OK audit-0711 — sheet-date, {EXPECTED_GAMES}/{EXPECTED_GAMES} park headers, "
    f"zone data, favs/gems, straights, manifest"
)
