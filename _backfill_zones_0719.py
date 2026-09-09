#!/usr/bin/env python3
"""Backfill zone-matchups from hr-matchups ZONE col for missing sheet props."""
from __future__ import annotations

import csv
import importlib.util
import io
import re
from pathlib import Path

from game_row_enrich import enrich_games_list, plain_name

ROOT = Path(__file__).resolve().parent
DATE = "2026-07-19"
ZONE_PATH = ROOT / "data" / f"zone-matchups-{DATE}.csv"

spec = importlib.util.spec_from_file_location("b0719", ROOT / f"build-sheet-{DATE}.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

enriched = enrich_games_list(build.games, DATE)
missing = []
for g in enriched:
    for r in g["rows"]:
        if r.get("zoneScore") is None:
            chip = (r.get("chips") or ["vs ?"])[0].replace("vs ", "").strip()
            missing.append((plain_name(r), r["name"], chip))

print(f"missing zoneScore: {len(missing)}")

zone_from_files: dict[tuple[str, str], tuple] = {}
for path in sorted((ROOT / "data").glob(f"hr-matchups-*-{DATE}.csv")):
    pitcher = None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("Pitcher,"):
            pitcher = line.split(",", 1)[1].strip()
            continue
        if not pitcher or line.startswith(("BATTER", ",", "SPLIT", "Matchup", "Pitcher Team", "Opposing")):
            continue
        parts = next(csv.reader([line]))
        if len(parts) < 4:
            continue
        bm = re.match(r"(.+?)\s+(LHB|RHB|SHB)\s*$", parts[0].strip())
        if not bm:
            continue
        name, bats = bm.group(1).strip(), bm.group(2)
        zone = (parts[3] or "").strip()
        if zone and zone not in {"-", "N/A", "—", ""}:
            zone_from_files[(name.lower(), pitcher.split()[-1].lower())] = (name, bats, zone, pitcher)

text = ZONE_PATH.read_text(encoding="utf-8-sig")
have = set()
for line in text.splitlines()[1:]:
    if not line.strip():
        continue
    parts = next(csv.reader([line]))
    if len(parts) >= 4:
        have.add((parts[0].lower(), parts[3].split()[-1].lower()))

LHP = {
    "Weathers", "Cantillo", "Cameron", "Gasser", "Imanaga", "Ray",
    "Griffin", "Lopez", "McClanahan", "Rodriguez",
}
added = 0
new_lines = []
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
        continue
    team = build.PLAYER_TEAMS.get(full, "")
    throws = "L" if any(x in pitcher for x in LHP) else "R"
    row = [name, bats, team, pitcher, throws, "", "", "", "", zone]
    buf = io.StringIO()
    csv.writer(buf, lineterminator="").writerow(row)
    new_lines.append(buf.getvalue())
    have.add(key)
    added += 1
    print("add", name, "vs", pitcher, zone)

if new_lines:
    if not text.endswith("\n"):
        text += "\n"
    ZONE_PATH.write_text(text + "\n".join(new_lines) + "\n", encoding="utf-8")
print("added", added)
