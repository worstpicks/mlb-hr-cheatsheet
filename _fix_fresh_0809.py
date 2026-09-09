#!/usr/bin/env python3
"""Repair 8/9 after fresh import: missing SP risk rows + zone backfill."""
from __future__ import annotations

import csv
import importlib.util
import io
import re
from pathlib import Path

from game_row_enrich import enrich_games_list, plain_name

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-09"
TARGETS = ROOT / "data" / f"hr-targets-overall-{DATE}.csv"
ZONE = ROOT / "data" / f"zone-matchups-{DATE}.csv"

# PropFinder still omits these three from hr-targets — keep 0.00 placeholders so metas render.
MISSING_SPS = [
    ("28", "1:35 PM", "Brayan Bello", "vs"),
    ("29", "4:10 PM", "Ian Seymour", "@"),
    ("30", "8:20 PM", "Randy Vasquez", "vs"),
]


def ensure_sp_risk() -> None:
    text = TARGETS.read_text(encoding="utf-8-sig")
    added = 0
    for num, time, name, vs in MISSING_SPS:
        if name in text:
            continue
        text = text.rstrip("\n") + f"\n{num},{time},{name},{vs},0.00,0.00,0.00,0.00,0.0%,0.0%,0.0%,0.0%,0.0%,0\n"
        added += 1
        print("added risk", name)
    TARGETS.write_text(text, encoding="utf-8")
    print("risk rows added:", added)


def backfill_zones() -> None:
    spec = importlib.util.spec_from_file_location("b0809", ROOT / f"build-sheet-{DATE}.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    enriched = enrich_games_list(build.games, DATE)
    missing = []
    for g in enriched:
        for r in g["rows"]:
            if r.get("zoneScore") is None:
                chip = (r.get("chips") or ["vs ?"])[0].replace("vs ", "").strip()
                missing.append((plain_name(r), chip, r["name"]))
    print("missing zones before:", len(missing))

    zone_map: dict[tuple[str, str], tuple] = {}
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
            name = re.sub(r"^\d+\s+", "", bm.group(1).strip())
            bats = bm.group(2)
            zone = (parts[3] or "").strip()
            if zone and zone not in {"-", "N/A", "—", ""}:
                last = pitcher.split()[-1].lower()
                zone_map[(name.lower(), last)] = (name, bats, zone, pitcher)
                zone_map[(name.lower(), pitcher.lower())] = (name, bats, zone, pitcher)

    rows = list(csv.reader(io.StringIO(ZONE.read_text(encoding="utf-8-sig"))))
    header = rows[0]
    by_key: dict[tuple[str, str], list] = {}
    out: list[list] = []
    for parts in rows[1:]:
        if len(parts) < 10:
            continue
        key = (parts[0].lower(), parts[3].split()[-1].lower())
        by_key[key] = parts
        out.append(parts)

    fixed = 0
    still = []
    lhp_tokens = {
        "Luzardo",
        "Manaea",
        "Cantillo",
        "Boyd",
        "Prielipp",
        "Povich",
        "Seymour",
        "Wrobleski",
        "Eduardo",
    }
    for plain, chip, full in missing:
        info = zone_map.get((plain.lower(), chip.lower())) or zone_map.get(
            (plain.lower(), chip.split()[-1].lower())
        )
        if not info:
            still.append((plain, chip))
            continue
        name, bats, zone, pitcher = info
        key = (name.lower(), pitcher.split()[-1].lower())
        if key in by_key:
            parts = by_key[key]
            if not (parts[9] or "").strip():
                parts[9] = zone
                fixed += 1
                print("fill", name, "vs", pitcher, zone)
            continue
        team = build.PLAYER_TEAMS.get(full, "") or build.PLAYER_TEAMS.get(name, "")
        throws = "L" if any(x in pitcher for x in lhp_tokens) else "R"
        row = [name, bats, team, pitcher, throws, "", "", "", "", zone]
        out.append(row)
        by_key[key] = row
        fixed += 1
        print("add", name, "vs", pitcher, zone)

    for plain, chip in still:
        print("skip", plain, "vs", chip)

    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(out)
    ZONE.write_text(buf.getvalue(), encoding="utf-8")
    print("zone fixes:", fixed)

    en2 = enrich_games_list(build.games, DATE)
    z = sum(1 for g in en2 for r in g["rows"] if r.get("zoneScore") is not None)
    n = sum(1 for g in en2 for r in g["rows"])
    print(f"zones after: {z}/{n}")
    bad = []
    for g in en2:
        meta = g.get("gameMeta") or ""
        if meta.count("pitcher-meta") != 2 or "Park" not in meta:
            bad.append(g["title"][:60])
    print("bad metas:", bad or "none")


if __name__ == "__main__":
    ensure_sp_risk()
    backfill_zones()
