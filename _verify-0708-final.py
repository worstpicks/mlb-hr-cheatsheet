#!/usr/bin/env python3
"""Comprehensive verification of 7/8 preview before pushing live."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
html = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")

spec = importlib.util.spec_from_file_location("b", ROOT / "build-sheet-2026-07-08.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

problems = []

# ---- Bums from source data ----
BUM_MIN = 0.95
bum_pitchers = {}
with (ROOT / "data" / "hr-targets-overall-2026-07-08.csv").open(encoding="utf-8-sig") as f:
    for line in f:
        m = re.match(r"\s*(?:\d+\||)\s*\d+,[\d: ]+[AP]M,([^,]+),(?:vs|@),([\-\d.]+),", line)
        if m:
            name, risk = m.group(1).strip(), m.group(2)
            try:
                r = float(risk)
            except ValueError:
                continue
            bum_pitchers[name] = r
expected_bums = {n: r for n, r in bum_pitchers.items() if r >= BUM_MIN}
print("=" * 70)
print(f"BUMS (HR risk >= {BUM_MIN}) expected on sheet:")
for n, r in sorted(expected_bums.items(), key=lambda x: -x[1]):
    print(f"  {n:22} {r:.2f}")

# ---- Bums flagged in game titles ----
titles = re.findall(r'title: "([^"]+)"', html)
flagged = set()
for t in titles:
    for seg in t.split(" vs "):
        if "🧤" in seg:
            nm = seg.split("🧤")[0]
            nm = nm.split(" - ")[-1].rsplit("(", 1)[0].strip()
            flagged.add(nm)
print("Flagged 🧤 in titles:", sorted(flagged))
for n in expected_bums:
    last = n.split()[-1]
    if not any(last in f for f in flagged):
        problems.append(f"BUM not flagged in title: {n}")
# reverse: flagged that arent expected bums
for f in flagged:
    if not any(f.split()[-1] in bn for bn in expected_bums):
        problems.append(f"Title flags 🧤 for non-bum: {f}")

# ---- Every batter facing a bum gets the glove emojis ----
print("=" * 70)
print("BUM-ROW EMOJI CHECK (⚾ 🕊️ 🧤 for batters vs bum)")
bum_last = {n.split()[-1] for n in expected_bums}
bum_rows_checked = 0
for rm in re.finditer(r'\{ name: "([^"]+)", odds: "[^"]*", score: \d+, emojis: "([^"]*)", note: "[^"]*", chips: (\[[^\]]+\])', html):
    chips = json.loads(rm.group(3))
    vs = chips[0].replace("vs ", "").strip()
    if vs in bum_last:
        em = rm.group(2)
        bum_rows_checked += 1
        for need in ("⚾", "🕊️", "🧤"):
            if need not in em:
                problems.append(f"bum row missing {need}: {rm.group(1)} vs {vs} | {em}")
print(f"  checked {bum_rows_checked} batter rows facing bums")
if bum_rows_checked == 0:
    problems.append("bum-row check captured 0 rows (regex or data problem)")

# ---- Favorites get star, gems get diamond ----
print("=" * 70)
print("FAVORITE / GEM EMOJI CHECK")
for fav in build.FAVS:
    m = re.search(rf'name: "{re.escape(fav)}".*?emojis: "([^"]*)"', html)
    if not m:
        problems.append(f"favorite row missing entirely: {fav}")
    elif "⭐" not in m.group(1):
        problems.append(f"favorite missing star: {fav} | {m.group(1)}")
for gem in build.GEMS:
    m = re.search(rf'name: "{re.escape(gem)}".*?emojis: "([^"]*)"', html)
    if not m:
        problems.append(f"gem row missing entirely: {gem}")
    elif "💎" not in m.group(1):
        problems.append(f"gem missing diamond: {gem} | {m.group(1)}")
print(f"  {len(build.FAVS)} favorites, {len(build.GEMS)} gems checked")

# ---- Rocket emoji for EV>=100, moonshot for high score/blast ----
print("=" * 70)
print("EV/SCORE EMOJI SANITY (🚀 for 100+ EV, 🌕💣 for moonshot)")
rows = re.findall(r'\{ name: "([^"]+)".*?score: (\d+), emojis: "([^"]*)", note: "([^"]*)"', html)
ev_flag = moon_flag = 0
for name, score, em, note in rows:
    evm = re.search(r"([\d.]+) mph EV", note)
    ev = float(evm.group(1)) if evm else 0
    if ev >= 100 and "🚀" not in em:
        problems.append(f"EV {ev} but no 🚀: {name} | {em}")
    if ev >= 100:
        ev_flag += 1
    if (int(score) >= 88 or '"high"' in note) and ("🌕" in em or "💣" in em):
        moon_flag += 1
print(f"  {len(rows)} rows scanned; {ev_flag} with 100+ EV")

# ---- Park header on every game ----
print("=" * 70)
print("PARK HEADER CHECK (Park% + LHB% + RHB% on every game)")
metas = re.findall(r'gameMeta: "([^"]*)"', html)
print(f"  {len(metas)} gameMeta lines")
for i, gm in enumerate(metas):
    tt = titles[i] if i < len(titles) else f"game{i}"
    if "Park " not in gm:
        problems.append(f"gameMeta missing Park%: {tt}")
    if "LHB " not in gm:
        problems.append(f"gameMeta missing LHB%: {tt}")
    if "RHB " not in gm:
        problems.append(f"gameMeta missing RHB%: {tt}")
pk = html.count("parkPct:")
lh = html.count("parkLhbPct:")
rh = html.count("parkRhbPct:")
print(f"  parkPct={pk} parkLhbPct={lh} parkRhbPct={rh} (expect 15 each)")
if not (pk == lh == rh == 15):
    problems.append(f"park data field mismatch pk={pk} lh={lh} rh={rh}")

# ---- Straights ----
print("=" * 70)
print("STRAIGHTS OF THE DAY")
for m in re.finditer(r'straight-pick-tag">([^<]+)</span>\s*<div class="straight-pick-header">\s*<strong class="straight-pick-name">([^<]+)</strong>\s*<span class="straight-pick-meta">([^<]+)</span>', html):
    print(f"  {m.group(1)}: {m.group(2).strip()} | {m.group(3).strip()}")

print("=" * 70)
if problems:
    print(f"FAIL — {len(problems)} problems:")
    for p in problems:
        print("  -", p)
    raise SystemExit(1)
print("ALL CHECKS PASSED")
