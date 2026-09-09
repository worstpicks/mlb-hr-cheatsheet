#!/usr/bin/env python3
"""Backfill 7/31 zone-matchups ZoneScore from hr-matchups ZONE for missing sheet props."""
from __future__ import annotations

import csv
import importlib.util
import io
import re
from pathlib import Path

from game_row_enrich import enrich_games_list, plain_name

ROOT = Path(__file__).resolve().parent
DATE = "2026-07-31"
ZONE_PATH = ROOT / "data" / f"zone-matchups-{DATE}.csv"

LHP = {
    "Imanaga",
    "Griffin",
    "Bratt",
    "Drohan",
    "Springs",
    "Whisenhunt",
    "Suarez",
}

spec = importlib.util.spec_from_file_location("b0731", ROOT / f"build-sheet-{DATE}.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

enriched = enrich_games_list(build.games, DATE)
missing: list[tuple[str, str, str]] = []
for g in enriched:
    for r in g["rows"]:
        if r.get("zoneScore") is None:
            chip = (r.get("chips") or ["vs ?"])[0].replace("vs ", "").strip()
            missing.append((plain_name(r), r["name"], chip))

print(f"missing zoneScore: {len(missing)}")

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
            # Some rows omit hand tag
            name = parts[0].strip()
            if not name or name.startswith(","):
                continue
            bats = "RHB"
            zone = (parts[3] or "").strip()
        else:
            name, bats = bm.group(1).strip(), bm.group(2)
            zone = (parts[3] or "").strip()
        if zone and zone not in {"-", "N/A", "—", ""}:
            zone_from_files[(name.lower(), pitcher.split()[-1].lower())] = (
                name,
                bats,
                zone,
                pitcher,
            )

text = ZONE_PATH.read_text(encoding="utf-8-sig")
have: set[tuple[str, str]] = set()
rows_out: list[list[str]] = []
reader = csv.reader(io.StringIO(text))
header = next(reader)
for parts in reader:
    if len(parts) < 10:
        continue
    batter, bats, team, pitcher, throws = parts[:5]
    contact, barrel, hr, hard_hit, zone_score = parts[5:10]
    key = (batter.lower(), pitcher.split()[-1].lower())
    have.add(key)
    # Fill blank ZoneScore for Eduardo Valencia vs Springs if matchup has ZONE
    if (not zone_score or not str(zone_score).strip()) and key in zone_from_files:
        zone_score = zone_from_files[key][2]
        print("fill blank", batter, "vs", pitcher, zone_score)
    rows_out.append(
        [batter, bats, team, pitcher, throws, contact, barrel, hr, hard_hit, zone_score]
    )

added = 0
for plain, full, chip in missing:
    info = zone_from_files.get((plain.lower(), chip.lower()))
    if not info:
        for (bn, pl), v in zone_from_files.items():
            if bn == plain.lower() and (pl in chip.lower() or chip.lower() in pl):
                info = v
                break
    if not info:
        print("skip", plain, "vs", chip)
        continue
    name, bats, zone, pitcher = info
    key = (name.lower(), pitcher.split()[-1].lower())
    if key in have:
        # Already present but maybe blank score — handled above
        continue
    team = build.PLAYER_TEAMS.get(full, "") or build.PLAYER_TEAMS.get(name, "")
    throws = "L" if any(x in pitcher for x in LHP) else "R"
    rows_out.append([name, bats, team, pitcher, throws, "", "", "", "", zone])
    have.add(key)
    added += 1
    print("add", name, "vs", pitcher, zone)

buf = io.StringIO()
w = csv.writer(buf, lineterminator="\n")
w.writerow(header)
w.writerows(rows_out)
ZONE_PATH.write_text(buf.getvalue(), encoding="utf-8")
print("added", added, "total rows", len(rows_out))

# Re-check coverage
enriched2 = enrich_games_list(build.games, DATE)
still = sum(1 for g in enriched2 for r in g["rows"] if r.get("zoneScore") is None)
have_n = sum(1 for g in enriched2 for r in g["rows"] if r.get("zoneScore") is not None)
print(f"after backfill: have {have_n}, still missing {still}")
