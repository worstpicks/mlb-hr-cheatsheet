from pathlib import Path
from sheet_data import load_pitcher_risk

r = load_pitcher_risk(Path("data/hr-targets-overall-2026-08-10.csv"))
print("count", len(r))
for p, o in sorted(((v["pitcher"], v["overall"]) for v in r.values()), key=lambda x: -x[1]):
    mark = " BUM" if o >= 0.95 else ""
    print(f"  {p}: {o:.2f}{mark}")

print("HOU matchups", list(Path("data").glob("hr-matchups-HOU*2026-08-10*")))
print("weak HOU", [p.name for p in Path("data").glob("pitcher-weak*HOU*2026-08-10*")])
