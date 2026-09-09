#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

from sheet_data import load_pitcher_risk

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DL = Path.home() / "Downloads"
DATE = "2026-08-02"

print("=== DOWNLOADS hr-matchups ===")
hm = sorted(DL.glob(f"hr-matchups-*-{DATE}.csv"))
print("count", len(hm))
for p in hm:
    print(" ", p.name)

print("\n=== DATA hr-matchups ===")
dm = sorted(DATA.glob(f"hr-matchups-*-{DATE}.csv"))
print("count", len(dm))
need = ["Anthony-Kay", "Robert-Stock", "JR-Ritchie", "Ritchie"]
for n in need:
    hits = [p.name for p in dm if n in p.name]
    print(n, hits or "MISSING")

print("\n=== ZONE pitchers ===")
with (DATA / f"zone-matchups-{DATE}.csv").open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))
print("rows", len(rows))
print(sorted({r.get("Pitcher", "") for r in rows}))

print("\n=== TARGETS top risks ===")
risk = load_pitcher_risk(DATA / f"hr-targets-overall-{DATE}.csv")
print("pitchers", len(risk))
for row in sorted(risk.values(), key=lambda x: -x["overall"])[:12]:
    glove = " GLOVE" if row["overall"] >= 0.95 else ""
    print(
        f"  {row['pitcher']:22} {row['overall']:+.2f} "
        f"LHB {row['vs_lhb']:+.2f} RHB {row['vs_rhb']:+.2f}{glove}"
    )
for name in ("JR Ritchie", "Robert Stock", "Anthony Kay"):
    r = risk.get(name.lower())
    print(f"lookup {name}:", r)
