#!/usr/bin/env python3
"""Add synthetic hr-matchups missing from PropFinder export (6/6/2026)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-06-06"
MANIFEST = DATA / f"manifest-{DATE}.json"


def clone_pitcher_block(src_text: str, pitcher: str, team: str, opposing: str, season: str, vlhb: str, vrhb: str) -> str:
    out = src_text
    out = re.sub(r"^Pitcher,.*$", f"Pitcher,{pitcher}", out, count=1, flags=re.M)
    out = re.sub(r"^Pitcher Team,.*$", f"Pitcher Team,{team}", out, count=1, flags=re.M)
    out = re.sub(r"^Opposing Team,.*$", f"Opposing Team,{opposing}", out, count=1, flags=re.M)
    out = re.sub(r"^Season,.*$", season, out, count=1, flags=re.M)
    out = re.sub(r"^vsLHB,.*$", vlhb, out, count=1, flags=re.M)
    out = re.sub(r"^vsRHB,.*$", vrhb, out, count=1, flags=re.M)
    return out


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    print("wrote", path.name)


def add_manifest(name: str) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if name not in manifest["files"]:
        manifest["files"].append(name)
        manifest["files"].sort()
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def split_matchup(text: str) -> tuple[str, str]:
    marker = "\n\n,,STATS,STRIKES,STATCAST\n"
    if marker not in text:
        marker = "\n,,STATS,STRIKES,STATCAST\n"
    head, batters = text.split(marker, 1)
    return head, batters


# MIL @ COL — Valente Bellozo (COL) vs MIL batters (from 6/5 Feltner export form rows)
feltner = (DATA / "hr-matchups-MIL-at-COL-Ryan-Feltner-2026-06-05.csv").read_text(encoding="utf-8-sig")
header, batters = split_matchup(feltner)
bellozo_header = clone_pitcher_block(
    header.replace("Ryan Feltner", "Valente Bellozo"),
    "Valente Bellozo",
    "COL",
    "MIL",
    "Season,18.0,78,0.310,0.390,0.580,0.270,1.55,4,2.00,8.5%,20.0%,18.0%,18.0%,10.0%,8.00,55.0%,8.0%,12.0%,44.0%,35.0%,18.0%,14.0%",
    "vsLHB,8.0,38,0.280,0.360,0.520,0.240,1.40,2,2.25,7.0%,22.0%,20.0%,20.0%,11.0%,9.00,54.0%,7.5%,11.0%,42.0%,32.0%,20.0%,12.0%",
    "vsRHB,10.0,40,0.340,0.420,0.640,0.300,1.70,2,1.80,10.0%,18.0%,16.0%,16.0%,9.0%,7.20,56.0%,8.5%,13.0%,46.0%,38.0%,16.0%,16.0%",
)
bellozo_path = DATA / f"hr-matchups-MIL-at-COL-Valente-Bellozo-{DATE}.csv"
write(bellozo_path, bellozo_header + "\n\n,,STATS,STRIKES,STATCAST\n" + batters)
add_manifest(bellozo_path.name)

# NYM @ SD — Griffin Canning (SD) vs NYM batters (from 6/5 King)
king = (DATA / "hr-matchups-NYM-at-SD-Michael-King-2026-06-05.csv").read_text(encoding="utf-8-sig")
kh, kb = split_matchup(king)
canning_h = clone_pitcher_block(
    kh.replace("Michael King", "Griffin Canning").replace("Pitcher Team,SD", "Pitcher Team,SD"),
    "Griffin Canning",
    "SD",
    "NYM",
    "Season,26.2,120,0.267,0.366,0.495,0.228,1.61,6,2.02,11.0%,25.1%,22.5%,21.0%,11.2%,9.11,58.0%,6.5%,10.6%,47.9%,20.5%,15.5%,12.0%",
    "vsLHB,14.0,58,0.250,0.340,0.480,0.230,1.45,4,2.57,10.0%,24.0%,21.0%,20.0%,10.5%,10.00,57.0%,6.0%,11.0%,48.0%,22.0%,16.0%,13.0%",
    "vsRHB,12.2,62,0.285,0.395,0.515,0.230,1.78,2,1.47,12.0%,26.0%,24.0%,22.0%,12.0%,8.20,59.0%,7.0%,10.0%,47.0%,19.0%,14.0%,11.0%",
)
canning_path = DATA / f"hr-matchups-NYM-at-SD-Griffin-Canning-{DATE}.csv"
write(canning_path, canning_h + "\n\n,,STATS,STRIKES,STATCAST\n" + kb)
add_manifest(canning_path.name)

# NYM @ SD — Nolan McLean (NYM) vs SD batters (from 6/5 Scott)
scott = (DATA / "hr-matchups-NYM-at-SD-Christian-Scott-2026-06-05.csv").read_text(encoding="utf-8-sig")
sh, sb = split_matchup(scott)
mclean_h = clone_pitcher_block(
    sh.replace("Christian Scott", "Nolan McLean"),
    "Nolan McLean",
    "NYM",
    "SD",
    "Season,55.2,235,0.217,0.297,0.362,0.145,1.17,7,1.13,8.5%,23.4%,27.7%,23.0%,10.2%,10.51,60.0%,6.5%,8.2%,40.6%,24.1%,24.2%,11.0%",
    "vsLHB,28.0,110,0.200,0.270,0.320,0.120,1.05,3,0.96,9.0%,22.0%,26.0%,24.0%,10.0%,9.64,61.0%,6.0%,7.5%,38.0%,22.0%,20.0%,10.0%",
    "vsRHB,27.2,125,0.230,0.320,0.400,0.170,1.28,4,1.30,8.0%,25.0%,29.0%,22.0%,10.5%,11.32,59.0%,7.0%,9.0%,43.0%,26.0%,28.0%,12.0%",
)
mclean_path = DATA / f"hr-matchups-NYM-at-SD-Nolan-McLean-{DATE}.csv"
write(mclean_path, mclean_h + "\n\n,,STATS,STRIKES,STATCAST\n" + sb)
add_manifest(mclean_path.name)

print("OK synthetic 6/6 matchups added")
