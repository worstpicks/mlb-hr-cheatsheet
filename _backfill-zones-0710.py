#!/usr/bin/env python3
"""Backfill zone-matchups-2026-07-10.csv from hr-matchups ZONE columns for missing SPs."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-07-10"
ZONE_PATH = DATA / f"zone-matchups-{DATE}.csv"

# (batter, pitcher_full, bats, team, zone)
# bats/team filled from matchup header context when possible
NEEDED = [
    ("Kyle Teel", "Aaron Civale", "LHB", "CWS"),
    ("Junior Perez", "Aaron Civale", "RHB", "CWS"),
    ("Brandon Nimmo", "Hunter Brown", "LHB", "TEX"),
    ("Joc Pederson", "Hunter Brown", "LHB", "TEX"),
    ("Yordan Alvarez", "Cal Quantrill", "LHB", "HOU"),
    ("Taylor Trammell", "Cal Quantrill", "LHB", "HOU"),
    ("Christian Walker", "Cal Quantrill", "RHB", "HOU"),
    ("Kody Clemens", "Grayson Rodriguez", "LHB", "MIN"),
    ("Josh Bell", "Grayson Rodriguez", "SHB", "MIN"),
    ("Mike Trout", "Zebby Matthews", "RHB", "LAA"),
    ("Josh Lowe", "Zebby Matthews", "LHB", "LAA"),
    ("Manny Machado", "Shane Bieber", "RHB", "SD"),
    ("Fernando Tatis Jr.", "Shane Bieber", "RHB", "SD"),
    ("Luis Campusano", "Shane Bieber", "RHB", "SD"),
    ("Max Kepler", "Shohei Ohtani", "LHB", "ARI"),
    ("Ketel Marte", "Shohei Ohtani", "SHB", "ARI"),
    ("Corbin Carroll", "Shohei Ohtani", "LHB", "ARI"),
    ("Rafael Devers", "Tanner Gordon", "LHB", "SF"),
    ("Heliot Ramos", "Tanner Gordon", "RHB", "SF"),
    ("Bryce Eldridge", "Tanner Gordon", "LHB", "SF"),
    ("Victor Bericoto", "Tanner Gordon", "RHB", "SF"),
    ("Hunter Goodman", "Robbie Ray", "RHB", "COL"),
    ("Edouard Julien", "Robbie Ray", "LHB", "COL"),
]

THROWS = {
    "Aaron Civale": "R",
    "Hunter Brown": "R",
    "Cal Quantrill": "R",
    "Grayson Rodriguez": "R",
    "Zebby Matthews": "R",
    "Shane Bieber": "R",
    "Shohei Ohtani": "R",
    "Tanner Gordon": "R",
    "Robbie Ray": "L",
}


def zone_from_matchups() -> dict[tuple[str, str], str]:
    out: dict[tuple[str, str], str] = {}
    for path in DATA.glob(f"hr-matchups-*-{DATE}.csv"):
        pitcher = None
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.startswith("Pitcher,"):
                pitcher = line.split(",", 1)[1].strip()
                continue
            if not pitcher:
                continue
            for name, *_rest in NEEDED:
                if line.startswith(name + " ") or line.startswith(name + ","):
                    parts = next(csv.reader([line]))
                    zone = (parts[3] if len(parts) > 3 else "").strip()
                    if zone and zone not in {"-", "N/A", ""}:
                        out[(name, pitcher)] = zone
    return out


def main() -> None:
    zones = zone_from_matchups()
    existing = ZONE_PATH.read_text(encoding="utf-8-sig").splitlines()
    header = existing[0]
    # existing keys
    have: set[tuple[str, str]] = set()
    for line in existing[1:]:
        if not line.strip():
            continue
        parts = next(csv.reader([line]))
        if len(parts) >= 4:
            have.add((parts[0], parts[3]))

    added = 0
    new_lines: list[str] = []
    for batter, pitcher, bats, team in NEEDED:
        if (batter, pitcher) in have:
            continue
        zone = zones.get((batter, pitcher), "")
        if not zone:
            # still add empty? skip — won't help zoneScore count
            print("skip no zone", batter, pitcher)
            continue
        throws = THROWS.get(pitcher, "R")
        # Batter,Bats,Team,Pitcher,Throws,Contact,Barrel,HR,HardHit,ZoneScore
        row = [batter, bats, team, pitcher, throws, "", "", "", "", zone]
        buf = __import__("io").StringIO()
        csv.writer(buf, lineterminator="").writerow(row)
        new_lines.append(buf.getvalue())
        added += 1
        print("add", batter, "vs", pitcher, "zone", zone)

    if new_lines:
        text = "\n".join(existing + new_lines) + "\n"
        ZONE_PATH.write_text(text, encoding="utf-8")
    print("added", added)


if __name__ == "__main__":
    main()
