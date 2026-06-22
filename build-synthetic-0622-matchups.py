#!/usr/bin/env python3
"""Add synthetic hr-matchups missing from PropFinder export (6/22/2026)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-06-22"
MANIFEST = DATA / f"manifest-{DATE}.json"


def clone_pitcher_block(src_text: str, pitcher: str, team: str, opposing: str, matchup: str) -> str:
    out = src_text
    out = re.sub(r"^Matchup,.*$", f"Matchup,{matchup}", out, count=1, flags=re.M)
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


def filter_batters(batter_block: str, names: set[str]) -> str:
    """Keep only batter rows whose normalized name is in names."""
    lines = batter_block.strip().splitlines()
    header = lines[0]
    kept = [header]
    for line in lines[1:]:
        if not line.strip():
            continue
        raw = line.split(",")[0]
        name = re.sub(r"\s+(LHB|RHB|SHB)\s*$", "", raw.strip(), flags=re.I)
        name = re.sub(r"^\d+\s+", "", name).strip()
        if name in names:
            kept.append(line)
    return "\n".join(kept) + "\n"


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    print("wrote", path.name)


def add_manifest(name: str) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if name not in manifest["files"]:
        manifest["files"].append(name)
        manifest["files"].sort()
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


# MIL @ CIN — Brady Singer (CIN) vs MIL batters (from 6/18 CLE @ MIL export)
singer_src = (DATA / "hr-matchups-NYM-at-CIN-Brady-Singer-2026-06-16.csv").read_text(encoding="utf-8-sig")
messick = (DATA / "hr-matchups-CLE-at-MIL-Parker-Messick-2026-06-18.csv").read_text(encoding="utf-8-sig")
singer_h, _ = split_matchup(singer_src)
_, mil_b = split_matchup(messick)
mil_names = {
    "Jackson Chourio",
    "Jake Bauers",
    "Garrett Mitchell",
    "Gary Sanchez",
    "Christian Yelich",
    "William Contreras",
    "Brice Turang",
    "Sal Frelick",
}
singer_h = clone_pitcher_block(singer_h, "Brady Singer", "CIN", "MIL", "MIL @ CIN")
singer_path = DATA / f"hr-matchups-MIL-at-CIN-Brady-Singer-{DATE}.csv"
write(singer_path, singer_h + "\n,,,STATS,STRIKES,STATCAST\n" + filter_batters(mil_b, mil_names))
add_manifest(singer_path.name)

# MIL @ CIN — Brandon Woodruff (MIL) vs CIN batters (from 6/17 NYM @ CIN McLean)
wacha = (DATA / "hr-matchups-KC-at-TB-Michael-Wacha-2026-06-22.csv").read_text(encoding="utf-8-sig")
mclean = (DATA / "hr-matchups-NYM-at-CIN-Nolan-McLean-2026-06-17.csv").read_text(encoding="utf-8-sig")
wood_h, _ = split_matchup(wacha)
_, cin_b = split_matchup(mclean)
cin_names = {
    "Eugenio Suarez",
    "Sal Stewart",
    "Spencer Steer",
    "JJ Bleday",
    "Nathaniel Lowe",
    "Matt McLain",
    "Edwin Arroyo",
    "Tyler Stephenson",
}
wood_h = clone_pitcher_block(wood_h, "Brandon Woodruff", "MIL", "CIN", "MIL @ CIN")
wood_h = wood_h.replace("Michael Wacha", "Brandon Woodruff")
wood_path = DATA / f"hr-matchups-MIL-at-CIN-Brandon-Woodruff-{DATE}.csv"
write(wood_path, wood_h + "\n,,,STATS,STRIKES,STATCAST\n" + filter_batters(cin_b, cin_names))
add_manifest(wood_path.name)

# PHI @ WSH — Alan Rangel (PHI) vs WSH batters (James Wood, Dylan Crews from 6/19 WSH @ TB)
cole = (DATA / "hr-matchups-NYY-at-DET-Gerrit-Cole-2026-06-22.csv").read_text(encoding="utf-8-sig")
wsh_src = (DATA / "hr-matchups-WSH-at-TB-Griffin-Jax-2026-06-19.csv").read_text(encoding="utf-8-sig")
rangel_h, _ = split_matchup(cole)
_, wsh_b = split_matchup(wsh_src)
wsh_names = {
    "James Wood",
    "Dylan Crews",
    "CJ Abrams",
    "Curtis Mead",
    "Andres Chaparro",
    "Daylen Lile",
    "Jacob Young",
    "Nasim Nuñez",
    "Keibert Ruiz",
}
rangel_h = clone_pitcher_block(rangel_h, "Alan Rangel", "PHI", "WSH", "PHI @ WSH")
rangel_h = rangel_h.replace("Gerrit Cole", "Alan Rangel")
rangel_path = DATA / f"hr-matchups-PHI-at-WSH-Alan-Rangel-{DATE}.csv"
write(rangel_path, rangel_h + "\n,,,STATS,STRIKES,STATCAST\n" + filter_batters(wsh_b, wsh_names))
add_manifest(rangel_path.name)

print("OK synthetic 6/22 matchups added")
