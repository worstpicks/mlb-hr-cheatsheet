#!/usr/bin/env python3
"""Backfill blank/missing 8/3 zone scores from hr-matchups ZONE col."""
from __future__ import annotations

import csv
import importlib.util
import io
import re
from pathlib import Path

from game_row_enrich import enrich_games_list, plain_name

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-10"
ZONE_PATH = ROOT / "data" / f"zone-matchups-{DATE}.csv"

LHP = {
    "Rogers",
    "Gore",
    "Detmers",
    "Lopez",
    "Cameron",
    "Skubal",
}

spec = importlib.util.spec_from_file_location("b0810", ROOT / f"build-sheet-{DATE}.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

enriched = enrich_games_list(build.games, DATE)
missing = []
for g in enriched:
    for r in g["rows"]:
        if r.get("zoneScore") is None:
            chip = (r.get("chips") or ["vs ?"])[0].replace("vs ", "").strip()
            missing.append((plain_name(r), r["name"], chip))
print("missing", len(missing))

zone_from_files: dict[tuple[str, str], tuple] = {}
for path in sorted((ROOT / "data").glob(f"hr-matchups-*-{DATE}.csv")):
    pitcher = None
    in_batters = False
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("Pitcher,"):
            pitcher = line.split(",", 1)[1].strip()
            in_batters = False
            continue
        if line.startswith("BATTER,"):
            in_batters = True
            continue
        if not in_batters or not pitcher:
            continue
        parts = next(csv.reader([line]))
        if len(parts) < 4:
            continue
        bm = re.match(r"(.+?)\s+(LHB|RHB|SHB)\s*$", parts[0].strip())
        if not bm:
            continue
        name, bats = bm.group(1).strip(), bm.group(2)
        name = re.sub(r"^\d+\s+", "", name).strip()
        zone = (parts[3] or "").strip()
        if zone and zone not in {"-", "N/A", "—", ""}:
            zone_from_files[(name.lower(), pitcher.split()[-1].lower())] = (
                name,
                bats,
                zone,
                pitcher,
            )

text = ZONE_PATH.read_text(encoding="utf-8-sig")
rows_out = []
reader = csv.reader(io.StringIO(text))
header = next(reader)
have: set[tuple[str, str]] = set()
for parts in reader:
    if len(parts) < 10:
        continue
    batter, bats, team, pitcher, throws = parts[:5]
    contact, barrel, hr, hard_hit, zone_score = parts[5:10]
    key = (batter.lower(), pitcher.split()[-1].lower())
    have.add(key)
    rows_out.append(
        [batter, bats, team, pitcher, throws, contact, barrel, hr, hard_hit, zone_score]
    )

added = 0
still = []
for plain, full, chip in missing:
    info = zone_from_files.get((plain.lower(), chip.lower()))
    if not info:
        still.append((plain, chip))
        continue
    name, bats, zone, pitcher = info
    key = (name.lower(), pitcher.split()[-1].lower())
    if key in have:
        continue
    team = build.PLAYER_TEAMS.get(full, "") or build.PLAYER_TEAMS.get(name, "")
    throws = "L" if any(x in pitcher for x in LHP) else "R"
    rows_out.append([name, bats, team, pitcher, throws, "", "", "", "", zone])
    have.add(key)
    added += 1
    print("add", name, "vs", pitcher, zone)

for plain, chip in still:
    print("skip", plain, "vs", chip)

buf = io.StringIO()
w = csv.writer(buf, lineterminator="\n")
w.writerow(header)
w.writerows(rows_out)
ZONE_PATH.write_text(buf.getvalue(), encoding="utf-8")
print("added", added)

enriched2 = enrich_games_list(build.games, DATE)
print(
    "after",
    sum(1 for g in enriched2 for r in g["rows"] if r.get("zoneScore") is not None),
    "missing",
    sum(1 for g in enriched2 for r in g["rows"] if r.get("zoneScore") is None),
)
