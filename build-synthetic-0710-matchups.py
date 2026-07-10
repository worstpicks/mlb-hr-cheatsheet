#!/usr/bin/env python3
"""Synthesize missing 7/10 hr-matchups from prior-day form rows."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-07-10"
MANIFEST = DATA / f"manifest-{DATE}.json"

HEADER = (
    "BATTER,SAVE,ODDS,ZONE,PA,L5 PA/G,HR,NEAR HR,BA,OBP,SLG,ISO,WOBA,BB%,WHIFF%,K%,SWSTR%,"
    "EV,AVGDIST,300+,350+,BARREL%,PULLBRL%,PULLAIR%,HH%,LA SS%,BAT SPD,FAST%,SQUP%,BLAST%,"
    "COMP%,AIR%,FB%,HR/FB%,LD%,GB%,PULL%,STRAIGHT%,OPPO%,1ST PITCH SWING%"
)


def add_manifest(name: str) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if name not in manifest["files"]:
        manifest["files"].append(name)
        manifest["files"].sort()
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def extract_batter_line(path: Path, name: str) -> str | None:
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith(name + " ") or line.startswith(name + ","):
            return line
    return None


def zone_lookup() -> dict[tuple[str, str], dict]:
    out: dict[tuple[str, str], dict] = {}
    path = DATA / f"zone-matchups-{DATE}.csv"
    if not path.exists():
        return out
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            out[(row["Batter"], row["Pitcher"])] = row
    return out


def rewrite_batter_line(line: str, *, odds: str | None = None, zone: str | None = None) -> str:
    parts = next(csv.reader([line]))
    if odds is not None and len(parts) > 2:
        parts[2] = odds
    if zone is not None and len(parts) > 3:
        parts[3] = zone
    want = len(HEADER.split(","))
    if len(parts) < want:
        parts.extend([""] * (want - len(parts)))
    elif len(parts) > want:
        parts = parts[:want]
    buf = io.StringIO()
    csv.writer(buf, lineterminator="").writerow(parts)
    return buf.getvalue()


def write_matchup(
    filename: str,
    *,
    matchup: str,
    pitcher: str,
    pitcher_team: str,
    opposing: str,
    batter_lines: list[str],
) -> None:
    path = DATA / filename
    body = [
        f"Matchup,{matchup}",
        f"Pitcher,{pitcher}",
        f"Pitcher Team,{pitcher_team}",
        f"Opposing Team,{opposing}",
        "",
        ",STATS,STRIKES,STATCAST",
        "SPLIT,IP,BF,BAA,WOBA,SLG,ISO,WHIP,HR,HR/9,BB%,WHIFF%,K%,PUTAWAY%,SWSTR%,K/9,1STPS%,MEATBALL%,BARREL%,HH%,FB%,HR/FB%,PULLAIR%",
        "Season,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-",
        "",
        ",,,STATS,STRIKES,STATCAST",
        HEADER,
        *batter_lines,
        "",
    ]
    path.write_text("\n".join(body), encoding="utf-8")
    add_manifest(filename)
    print("wrote", filename, f"({len(batter_lines)} batters)")


def main() -> None:
    zones = zone_lookup()

    # --- HOU @ TEX: Cal Quantrill (home SP) faces HOU batters ---
    src_hou = DATA / "hr-matchups-HOU-at-WSH-Foster-Griffin-2026-07-08.csv"
    hou_lines = []
    for name in ("Yordan Alvarez", "Christian Walker", "Taylor Trammell"):
        raw = extract_batter_line(src_hou, name)
        if not raw:
            raise SystemExit(f"missing {name} in {src_hou.name}")
        z = zones.get((name, "Cal Quantrill"))
        zone = z["ZoneScore"] if z and z.get("ZoneScore") else None
        hou_lines.append(rewrite_batter_line(raw, zone=zone))

    write_matchup(
        f"hr-matchups-HOU-at-TEX-Cal-Quantrill-{DATE}.csv",
        matchup="HOU @ TEX",
        pitcher="Cal Quantrill",
        pitcher_team="TEX",
        opposing="HOU",
        batter_lines=hou_lines,
    )

    # --- LAA @ MIN: Grayson Rodriguez (away SP) faces MIN batters ---
    src_min = DATA / "hr-matchups-CLE-at-MIN-Gavin-Williams-2026-07-09.csv"
    min_lines = []
    for name in ("Kody Clemens", "Josh Bell"):
        raw = extract_batter_line(src_min, name)
        if not raw:
            raise SystemExit(f"missing {name} in {src_min.name}")
        z = zones.get((name, "Grayson Rodriguez"))
        zone = z["ZoneScore"] if z and z.get("ZoneScore") else None
        min_lines.append(rewrite_batter_line(raw, zone=zone))

    write_matchup(
        f"hr-matchups-LAA-at-MIN-Grayson-Rodriguez-{DATE}.csv",
        matchup="LAA @ MIN",
        pitcher="Grayson Rodriguez",
        pitcher_team="LAA",
        opposing="MIN",
        batter_lines=min_lines,
    )

    print("done")


if __name__ == "__main__":
    main()
