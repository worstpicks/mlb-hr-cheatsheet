#!/usr/bin/env python3
import csv
import io
from pathlib import Path

from sheet_data import load_pitcher_risk

# Fill Valencia blank zone
p = Path("data/zone-matchups-2026-07-31.csv")
rows = list(csv.reader(io.StringIO(p.read_text(encoding="utf-8-sig"))))
header, body = rows[0], rows[1:]
for r in body:
    if r and r[0] == "Eduardo Valencia" and "Springs" in r[3] and not str(r[9]).strip():
        r[9] = "12.0"
        print("filled Valencia zone 12.0")
buf = io.StringIO()
w = csv.writer(buf, lineterminator="\n")
w.writerow(header)
w.writerows(body)
p.write_text(buf.getvalue(), encoding="utf-8")

risk = load_pitcher_risk(Path("data/hr-targets-overall-2026-07-31.csv"))
print("pitchers", len(risk))
for _k, r in sorted(risk.items(), key=lambda x: -x[1]["overall"]):
    flag = " GLOVE" if r["overall"] >= 0.95 else ""
    print(
        f"  {r['pitcher']}: {r['overall']:.2f} "
        f"LHB {r.get('vs_lhb')} RHB {r.get('vs_rhb')}{flag}"
    )
