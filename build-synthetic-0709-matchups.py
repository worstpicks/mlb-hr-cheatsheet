#!/usr/bin/env python3
"""Synthesize missing 7/9 hr-matchups from prior-day form rows + today's zone/odds context."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-07-09"
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
    with (DATA / f"zone-matchups-{DATE}.csv").open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            out[(row["Batter"], row["Pitcher"])] = row
    return out


def rewrite_batter_line(line: str, *, odds: str | None = None, zone: str | None = None) -> str:
    import io

    parts = next(csv.reader([line]))
    # BATTER,SAVE,ODDS,ZONE,...
    if odds is not None and len(parts) > 2:
        parts[2] = odds
    if zone is not None and len(parts) > 3:
        parts[3] = zone
    # pad/truncate to header width
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

    # --- NYY @ TB: Drew Rasmussen (home SP) faces NYY batters ---
    src_nyy = DATA / "hr-matchups-NYY-at-TB-Shane-McClanahan-2026-07-08.csv"
    nyy_lines = []
    for name, hand in [("Ben Rice", "LHB"), ("Max Schuemann", "RHB")]:
        raw = extract_batter_line(src_nyy, name)
        if not raw:
            raise SystemExit(f"missing {name} in {src_nyy.name}")
        z = zones.get((name, "Drew Rasmussen"))
        zone = z["ZoneScore"] if z and z.get("ZoneScore") else None
        # keep prior odds if present; zone from today when available
        nyy_lines.append(rewrite_batter_line(raw, zone=zone))

    write_matchup(
        f"hr-matchups-NYY-at-TB-Drew-Rasmussen-{DATE}.csv",
        matchup="NYY @ TB",
        pitcher="Drew Rasmussen",
        pitcher_team="TB",
        opposing="NYY",
        batter_lines=nyy_lines,
    )

    # --- NYY @ TB: Ryan Yarbrough (away SP) faces TB batters ---
    src_tb = DATA / "hr-matchups-NYY-at-TB-Gerrit-Cole-2026-07-08.csv"
    tb_lines = []
    for name in ("Junior Caminero", "Ryan Vilade"):
        raw = extract_batter_line(src_tb, name)
        if not raw:
            raise SystemExit(f"missing {name} in {src_tb.name}")
        tb_lines.append(rewrite_batter_line(raw))

    write_matchup(
        f"hr-matchups-NYY-at-TB-Ryan-Yarbrough-{DATE}.csv",
        matchup="NYY @ TB",
        pitcher="Ryan Yarbrough",
        pitcher_team="NYY",
        opposing="TB",
        batter_lines=tb_lines,
    )

    # --- COL @ SF: Carson Whisenhunt (home SP) faces COL batters ---
    src_col = DATA / "hr-matchups-COL-at-LAD-Roki-Sasaki-2026-07-08.csv"
    col_lines = []
    for name in ("Hunter Goodman", "Kyle Karros", "Edouard Julien"):
        raw = extract_batter_line(src_col, name)
        if not raw:
            raise SystemExit(f"missing {name} in {src_col.name}")
        col_lines.append(rewrite_batter_line(raw))

    write_matchup(
        f"hr-matchups-COL-at-SF-Carson-Whisenhunt-{DATE}.csv",
        matchup="COL @ SF",
        pitcher="Carson Whisenhunt",
        pitcher_team="SF",
        opposing="COL",
        batter_lines=col_lines,
    )

    print("done")


if __name__ == "__main__":
    main()
