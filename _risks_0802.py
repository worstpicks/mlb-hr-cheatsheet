#!/usr/bin/env python3
from pathlib import Path
from sheet_data import load_pitcher_risk

risk = load_pitcher_risk(Path("data/hr-targets-overall-2026-08-02.csv"))
print("pitchers", len(risk))
for r in sorted(risk.values(), key=lambda z: -z["overall"]):
    flag = " GLOVE" if r["overall"] >= 0.95 else ""
    print(f"  {r['pitcher']}: {r['overall']:.2f} LHB {r.get('vs_lhb')} RHB {r.get('vs_rhb')}{flag}")
