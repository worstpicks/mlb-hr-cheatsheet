#!/usr/bin/env python3
"""Audit 7/25 sheet: parks, splits, bums, features vs 7/24 archive."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
html = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
arch = (ROOT / "preview" / "archive" / "2026-07-24.html").read_text(encoding="utf-8")

errors: list[str] = []
warns: list[str] = []


def must(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def warn(cond: bool, msg: str) -> None:
    if not cond:
        warns.append(msg)


# --- meta ---
m = re.search(r'name="sheet-date" content="([^"]+)"', html)
must(m and m.group(1) == "2026-07-25", f"sheet-date={m.group(1) if m else None}")

# --- games / rows from embedded JS ---
# Prefer build-sheet source of truth
bs = (ROOT / "build-sheet-2026-07-25.py").read_text(encoding="utf-8")
# count games in GAMES or similar
game_keys = re.findall(r'"key":\s*"([^"]+ @ [^"]+)"', bs)
if not game_keys:
    game_keys = re.findall(r'title":\s*"([^"]+ @ [^"]+)', html)
print("games", len(set(game_keys)), sorted(set(game_keys)))

# --- required SPs ---
required_sps = [
    "Ryan Weathers",
    "Brian Keller",
    "Tanner Bibee",
    "Nick Martinez",
    "Shota Imanaga",
    "Paul Skenes",
    "Bryce Elder",
    "Brandon Young",
    "Hunter Brown",
    "Sean Burke",
    "Ryan Feltner",
    "Robert Gasser",
    "Mason Barnett",
    "Connor Prielipp",
    "Bryan Woo",
    "Nathan Eovaldi",
    "Yoshinobu Yamamoto",
    "Nolan McLean",
    "Hunter Greene",
    "Andre Pallante",
]
for sp in required_sps:
    must(sp in html, f"missing SP in preview: {sp}")
for stale in ["Tim Mayza", "Mike Paredes"]:
    must(stale not in html, f"stale SP still in preview: {stale}")

# --- bums (risk >= 0.95) ---
from sheet_data import load_pitcher_risk

risks = load_pitcher_risk("2026-07-25")
bums = sorted(
    [(n, float(r)) for n, r in risks.items() if float(r) >= 0.95],
    key=lambda x: -x[1],
)
print("BUMS from targets (>=0.95):")
for n, r in bums:
    glove_ok = f"{n}" in html and "🧤" in html
    # title should include glove near name
    in_title = bool(re.search(rf"{re.escape(n)}[^<\n]{{0,40}}🧤|🧤[^<\n]{{0,40}}{re.escape(n)}", html))
    print(f"  {n} {r:+.2f} title_glove={in_title}")
    must(in_title, f"bum {n} ({r:+.2f}) missing 🧤 in game title")

# --- park % + splits at top of each game ---
# Look for parkPct / LHB / RHB patterns in games block
park_hits = len(re.findall(r"park[_ ]?(?:pct|hr)|HR\s*[+\-]?\d+%|parkPct", html, re.I))
lhb = len(re.findall(r"LHB|vs LHB|park_lhb", html, re.I))
rhb = len(re.findall(r"RHB|vs RHB|park_rhb", html, re.I))
print(f"park-ish mentions={park_hits} LHB-ish={lhb} RHB-ish={rhb}")

# Parse GAME_META / games from preview script if present
meta_blocks = re.findall(
    r"(?:parkPct|park_pct|hrPark|weatherPark)[^,]{0,80}",
    html,
    re.I,
)
print("park field samples:", meta_blocks[:8])

# Check each game card has park and split chips - look for common sheet pattern
# In recent sheets: game descriptions include park % and pitcher vs LHB/RHB
for gk in sorted(set(game_keys)):
    # find a window around game key
    idx = html.find(gk.replace(" @ ", " @ "))
    if idx < 0:
        # try without spaces variants
        idx = html.find(gk)
    if idx < 0:
        warns.append(f"game key not found in html: {gk}")
        continue
    window = html[max(0, idx - 200) : idx + 2500]
    has_pct = bool(re.search(r"[+\-]?\d+%", window))
    has_split = bool(re.search(r"vs\s*LHB|vs\s*RHB|LHB|RHB|split", window, re.I))
    if not has_pct:
        errors.append(f"{gk}: no park/weather % near game header")
    if not has_split:
        warns.append(f"{gk}: weak/missing pitcher split signals near header")

# --- feature parity vs 7/24 ---
features = [
    ("Homerun Form", "Homerun Form"),
    ("Damage Window", "Damage Window"),
    ("Straights of the Day", "Straights of the Day"),
    ("Goblin", "Goblin"),
    ("Favorite 3", "Favorite 3"),
    ("3 Leg HR", "3 Leg"),
    ("2 Leg HR", "2 Leg"),
    ("Top 5 HR", "Top 5"),
    ("Weather", "Weather"),
    ("Longshot", "Longshot"),
    ("Hits", "Hits"),
    ("MLB Research", "research"),
    ("Gambly", "gambly"),
    ("worstpickz-theme / theme", "theme"),
    ("Pikkit", "Pikkit"),
]
print("\nFeature parity vs 7/24 archive:")
for label, needle in features:
    now = needle.lower() in html.lower()
    then = needle.lower() in arch.lower()
    status = "OK" if now else ("MISSING" if then else "N/A")
    print(f"  [{status}] {label} (7/24={then} 7/25={now})")
    if then and not now:
        errors.append(f"feature missing vs 7/24: {label}")

# --- research / park JSON ---
must(
    (ROOT / "preview/data/research-2026-07-25.json").is_file(),
    "missing research-2026-07-25.json",
)
pf = ROOT / "preview/data/park-factors-2026-07-25.json"
must(pf.is_file(), "missing park-factors-2026-07-25.json")
if pf.is_file():
    data = json.loads(pf.read_text(encoding="utf-8"))
    src = data.get("source") or data.get("source_label") or ""
    print("park JSON source:", src or list(data.keys())[:8])
    must(
        "ballpark" in json.dumps(data).lower() or src,
        "park factors JSON missing ballpark-pal attribution",
    )

# --- props / emoji counts ---
stars = html.count("⭐")
gems = html.count("💎")
print(f"\nemoji counts: stars={stars} gems={gems} gloves={html.count('🧤')}")

# --- zone data presence ---
zone_n = len(re.findall(r"zoneScore|zone_score|zoneHR", html, re.I))
print("zone field mentions:", zone_n)
must(zone_n >= 40, f"low zone data presence ({zone_n})")

print("\n=== WARNINGS ===")
for w in warns:
    print("WARN:", w)
print("\n=== ERRORS ===")
for e in errors:
    print("ERR:", e)
print("\nRESULT:", "FAIL" if errors else "PASS")
raise SystemExit(1 if errors else 0)
