#!/usr/bin/env python3
"""Comprehensive verification of 7/10 preview before pushing live."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
html = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
prev = (ROOT / "preview" / "archive" / "2026-07-09.html").read_text(encoding="utf-8")

spec = importlib.util.spec_from_file_location("b", ROOT / "build-sheet-2026-07-10.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

EXPECTED_GAMES = 15
EXPECTED_PROPS = 78
problems: list[str] = []

print("=" * 70)
print("FEATURE PARITY (headers)")
print("=" * 70)
headers_prev = set(re.findall(r"<h3>([^<]+)</h3>", prev)) | set(re.findall(r"<h4>([^<]+)</h4>", prev))
headers_cur = set(re.findall(r"<h3>([^<]+)</h3>", html)) | set(re.findall(r"<h4>([^<]+)</h4>", html))
missing = headers_prev - headers_cur
if missing:
    for h in sorted(missing):
        problems.append(f"missing section header: {h}")
        print("  MISSING:", h)
else:
    print("  OK - all 7/9 section headers present")

print("=" * 70)
print("DATA-KEY FEATURE PARITY")
print("=" * 70)
feature_markers = [
    "zoneScore:", "formTrend:", "gbPct:", "hhPct:", "fbPct:", "pullAir:",
    "zoneContact:", "zoneBarrel:", "zoneHr:", "zoneHardHit:", "contactRisk:",
    "blast:", "top3Detail:", "gameMeta:", "parkPct:", "parkLhbPct:", "parkRhbPct:",
    "startTime:", "data-goblin-gambly-lines", "WORST_PICKZ_FAVORITE_NAMES",
    "bet tracker", "Homerun Form", "Split + Risk + Park + Form + Zone",
]
for mk in feature_markers:
    cp = prev.count(mk)
    cc = html.count(mk)
    flag = "" if cc > 0 or cp == 0 else "  <<< MISSING IN 7/10"
    if flag:
        problems.append(f"feature missing: {mk}")
    print(f"  {mk:40} 7/9={cp:5}  7/10={cc:5}{flag}")

# ---- Bums ----
BUM_MIN = 0.95
bum_pitchers: dict[str, float] = {}
with (ROOT / "data" / "hr-targets-overall-2026-07-10.csv").open(encoding="utf-8-sig") as f:
    for line in f:
        m = re.match(r"\s*\d+,[\d: ]+[AP]M,([^,]+),(?:vs|@),([\-\d.]+),", line)
        if not m:
            continue
        name, risk = m.group(1).strip(), m.group(2)
        try:
            r = float(risk)
        except ValueError:
            continue
        bum_pitchers[name] = r

# Only bums who appear as SPs on this sheet
sheet_sps: set[str] = set()
for t in re.findall(r'title: "([^"]+)"', html):
    # "KEY - Away SP (hand, TEAM) vs Home SP (hand, TEAM)"
    if " - " not in t or " vs " not in t:
        continue
    matchup = t.split(" - ", 1)[1]
    for seg in matchup.split(" vs "):
        nm = seg.split("🧤")[0].rsplit("(", 1)[0].strip()
        sheet_sps.add(nm)

expected_bums = {n: r for n, r in bum_pitchers.items() if r >= BUM_MIN and n in sheet_sps}
print("=" * 70)
print(f"BUMS (HR risk >= {BUM_MIN}, on-sheet SPs only)")
for n, r in sorted(expected_bums.items(), key=lambda x: -x[1]):
    print(f"  {n:22} {r:.2f}")

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

print("=" * 70)
print("BUM-ROW EMOJI CHECK")
bum_last = {n.split()[-1] for n in expected_bums}
bum_rows_checked = 0
for rm in re.finditer(
    r'\{ name: "([^"]+)", odds: "[^"]*", score: \d+, emojis: "([^"]*)", note: "[^"]*", chips: (\[[^\]]+\])',
    html,
):
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
    problems.append("bum-row check captured 0 rows")

print("=" * 70)
print("FAVORITE / GEM EMOJI CHECK")
for fav in build.FAVS:
    m = re.search(rf'name: "{re.escape(fav)}".*?emojis: "([^"]*)"', html)
    if not m:
        problems.append(f"favorite row missing: {fav}")
    elif "⭐" not in m.group(1):
        problems.append(f"favorite missing star: {fav} | {m.group(1)}")
for gem in build.GEMS:
    m = re.search(rf'name: "{re.escape(gem)}".*?emojis: "([^"]*)"', html)
    if not m:
        problems.append(f"gem row missing: {gem}")
    elif "💎" not in m.group(1):
        problems.append(f"gem missing diamond: {gem} | {m.group(1)}")
print(f"  {len(build.FAVS)} favorites, {len(build.GEMS)} gems checked")

print("=" * 70)
print("EV 🚀 CHECK")
rows = re.findall(
    r'\{ name: "([^"]+)".*?score: (\d+), emojis: "([^"]*)", note: "([^"]*)"',
    html,
)
for name, score, em, note in rows:
    evm = re.search(r"([\d.]+) mph EV", note)
    ev = float(evm.group(1)) if evm else 0
    if ev >= 100 and "🚀" not in em:
        problems.append(f"EV {ev} but no 🚀: {name} | {em}")
print(f"  {len(rows)} rows scanned")

print("=" * 70)
print("PARK HEADER CHECK")
metas = re.findall(r'gameMeta: "([^"]*)"', html)
print(f"  {len(metas)} gameMeta lines / {len(titles)} titles")
for i, gm in enumerate(metas):
    tt = titles[i] if i < len(titles) else f"game{i}"
    if "Park " not in gm:
        problems.append(f"gameMeta missing Park%: {tt}")
    if "LHB " not in gm:
        problems.append(f"gameMeta missing LHB%: {tt}")
    if "RHB " not in gm:
        problems.append(f"gameMeta missing RHB%: {tt}")
pk, lh, rh = html.count("parkPct:"), html.count("parkLhbPct:"), html.count("parkRhbPct:")
print(f"  parkPct={pk} parkLhbPct={lh} parkRhbPct={rh} (expect {EXPECTED_GAMES})")
if not (pk == lh == rh == EXPECTED_GAMES):
    problems.append(f"park data field mismatch pk={pk} lh={lh} rh={rh}")

print("=" * 70)
print("PROP / ZONE COUNTS")
zc = html.count("zoneScore:")
print(f"  titles={len(titles)} zoneScore={zc} (expect games={EXPECTED_GAMES}, zones>={EXPECTED_PROPS - 20})")
if len(titles) != EXPECTED_GAMES:
    problems.append(f"game count {len(titles)} != {EXPECTED_GAMES}")
if zc < EXPECTED_PROPS - 20:
    problems.append(f"zoneScore {zc} too low")

print("=" * 70)
print("STRAIGHTS OF THE DAY")
for m in re.finditer(
    r'straight-pick-tag">([^<]+)</span>\s*<div class="straight-pick-header">\s*'
    r'<strong class="straight-pick-name">([^<]+)</strong>\s*'
    r'<span class="straight-pick-meta">([^<]+)</span>',
    html,
):
    print(f"  {m.group(1)}: {m.group(2).strip()} | {m.group(3).strip()}")

print("=" * 70)
print("ROOT SYNC CHECK")
root = (ROOT / "index.html").read_text(encoding="utf-8")
root_date = re.search(r'sheet-date" content="([^"]+)"', root)
prev_date = re.search(r'sheet-date" content="([^"]+)"', html)
print(f"  preview={prev_date.group(1) if prev_date else '?'} root={root_date.group(1) if root_date else '?'}")

print("=" * 70)
if problems:
    print(f"FAIL — {len(problems)} problems:")
    for p in problems:
        print("  -", p)
    raise SystemExit(1)
print("ALL CHECKS PASSED")
