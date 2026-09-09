#!/usr/bin/env python3
from pathlib import Path
from sheet_data import load_pitcher_risk

risk = load_pitcher_risk(Path("data") / "hr-targets-overall-2026-08-03.csv")
print("pitchers", len(risk))
for row in sorted(risk.values(), key=lambda x: -x["overall"]):
    glove = " GLOVE" if row["overall"] >= 0.95 else ""
    print(
        f"  {row['pitcher']:24} {row['overall']:+.2f} "
        f"LHB {row['vs_lhb']:+.2f} RHB {row['vs_rhb']:+.2f}{glove}"
    )
