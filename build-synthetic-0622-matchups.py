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


singer_path = DATA / f"hr-matchups-MIL-at-CIN-Brady-Singer-{DATE}.csv"
if not singer_path.exists():
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
    write(singer_path, singer_h + "\n,,,STATS,STRIKES,STATCAST\n" + filter_batters(mil_b, mil_names))
    add_manifest(singer_path.name)
else:
    print("skip", singer_path.name, "(already exists)")

print("OK synthetic 6/22 matchups")
