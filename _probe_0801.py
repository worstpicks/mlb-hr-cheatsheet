#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from pathlib import Path

from csv_slate_meta import name_lookup_key

DATE = "2026-08-01"
ROOT = Path(__file__).resolve().parent

raw = (ROOT / "build-0801-from-csv.py").read_text(encoding="utf-8")
m = re.search(r"RAW_PROPS = \[(.*?)\]", raw, re.S)
props = []
for line in m.group(1).splitlines():
    s = line.strip().strip(",").strip('"')
    if s:
        props.append(s)
print(
    "props",
    len(props),
    "fav",
    sum(1 for p in props if "⭐" in p),
    "gem",
    sum(1 for p in props if "💎" in p),
)

batters: set[str] = set()
pitchers: list[tuple[str, str]] = []
for path in sorted((ROOT / "data").glob(f"hr-matchups-*-{DATE}.csv")):
    pitcher = None
    in_b = False
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("Pitcher,"):
            pitcher = line.split(",", 1)[1].strip()
            pitchers.append((path.name, pitcher))
            in_b = False
            continue
        if line.startswith("BATTER,"):
            in_b = True
            continue
        if not in_b:
            continue
        parts = next(csv.reader([line]))
        if not parts or not parts[0].strip():
            continue
        bm = re.match(r"(.+?)\s+(LHB|RHB|SHB)\s*$", parts[0].strip())
        name = bm.group(1).strip() if bm else parts[0].strip()
        if name:
            batters.add(name_lookup_key(name))

print("matchup files", len(pitchers))
for n, p in pitchers:
    print(f"  {p:22} {n}")

aliases = {
    "andrew beintendi": "andrew benintendi",
    "aj ewing": "a.j. ewing",
    "garret mitchell": "garrett mitchell",
    "hao-yu-lee": "hao-yu lee",
    "hao yu lee": "hao-yu lee",
}
missing = []
for p in props:
    plain = p.replace("⭐", "").replace("💎", "").strip()
    key = name_lookup_key(aliases.get(plain.lower(), plain))
    if key not in batters:
        missing.append(plain)
print("missing", len(missing))
for name in missing:
    print("  MISSING", name)

# targets bums
from sheet_data import load_pitcher_risk

risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
print("targets", len(risk))
for _k, r in sorted(risk.items(), key=lambda x: -x[1]["overall"]):
    flag = " GLOVE" if r["overall"] >= 0.95 else ""
    if r["overall"] >= 0.80 or flag:
        print(f"  {r['pitcher']}: {r['overall']:.2f}{flag}")
