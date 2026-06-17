#!/usr/bin/env python3
"""Add synthetic hr-matchups missing from PropFinder export (6/17/2026 CLE @ MIL)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-06-17"
MANIFEST = DATA / f"manifest-{DATE}.json"


def clone_pitcher_block(src_text: str, pitcher: str, team: str, opposing: str) -> str:
    out = src_text
    out = re.sub(r"^Pitcher,.*$", f"Pitcher,{pitcher}", out, count=1, flags=re.M)
    out = re.sub(r"^Pitcher Team,.*$", f"Pitcher Team,{team}", out, count=1, flags=re.M)
    out = re.sub(r"^Opposing Team,.*$", f"Opposing Team,{opposing}", out, count=1, flags=re.M)
    return out


def split_matchup(text: str) -> tuple[str, str]:
    for marker in (
        "\n\n,,,STATS,STRIKES,STATCAST\n",
        "\n,,,STATS,STRIKES,STATCAST\n",
        "\n\n,,STATS,STRIKES,STATCAST\n",
        "\n,,STATS,STRIKES,STATCAST\n",
    ):
        if marker in text:
            return text.split(marker, 1)
    raise ValueError("Could not split matchup CSV")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    print("wrote", path.name)


def add_manifest(name: str) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if name not in manifest["files"]:
        manifest["files"].append(name)
        manifest["files"].sort()
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


# CLE @ MIL — clone 6/16 exports (same park, refreshed lineups)
cecconi = (DATA / "hr-matchups-CLE-at-MIL-Slade-Cecconi-2026-06-16.csv").read_text(encoding="utf-8-sig")
gasser = (DATA / "hr-matchups-CLE-at-MIL-Robert-Gasser-2026-06-16.csv").read_text(encoding="utf-8-sig")

williams_h, williams_b = split_matchup(cecconi)
williams_h = clone_pitcher_block(williams_h.replace("Slade Cecconi", "Gavin Williams"), "Gavin Williams", "CLE", "MIL")
williams_path = DATA / f"hr-matchups-CLE-at-MIL-Gavin-Williams-{DATE}.csv"
write(williams_path, williams_h + "\n,,,STATS,STRIKES,STATCAST\n" + williams_b)
add_manifest(williams_path.name)

sproat_h, sproat_b = split_matchup(gasser)
sproat_h = clone_pitcher_block(sproat_h.replace("Robert Gasser", "Brandon Sproat"), "Brandon Sproat", "MIL", "CLE")
sproat_path = DATA / f"hr-matchups-CLE-at-MIL-Brandon-Sproat-{DATE}.csv"
write(sproat_path, sproat_h + "\n,,,STATS,STRIKES,STATCAST\n" + sproat_b)
add_manifest(sproat_path.name)

print("OK synthetic 6/17 CLE @ MIL matchups added")
