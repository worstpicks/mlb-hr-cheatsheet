from pathlib import Path
from sheet_data import load_pitcher_risk

risks = load_pitcher_risk(Path("data/hr-targets-overall-2026-08-07.csv"))
items = sorted(risks.items(), key=lambda x: -x[1]["overall"])
print("count", len(items))
bums = []
for k, v in items:
    o = v["overall"]
    mark = " BUM" if o >= 0.95 else ""
    print(f"  {v['pitcher']}: {o}{mark}")
    if o >= 0.95:
        bums.append(v["pitcher"])
print("BUMS:", bums)
