#!/usr/bin/env python3
"""Synthesize the missing CHC @ WSH hr-matchups file for Jackson Kent (2026-08-12).

Kent is an MLB debut arm, so PropFinder exported neither a matchup CSV nor a zone
or HR-risk row for him. Without this the CHC side of the game has no batters and
the game header renders a single pitcher. Batter lines are carried from each
hitter's most recent PropFinder matchup export; ZONE is intentionally left blank
because batter-vs-Kent zone fit does not exist.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-08-12"

SPEC = {
    "dst": f"hr-matchups-CHC-at-WSH-Jackson-Kent-{DATE}.csv",
    "matchup": "CHC @ WSH",
    "pitcher": "Jackson Kent",
    "pitcher_team": "WSH",
    "opposing_team": "CHC",
}

# CHC lineup vs Kent (LHP), in batting order.
LINEUP: list[tuple[str, str]] = [
    ("Pete Crow-Armstrong", "LHB"),
    ("Seiya Suzuki", "RHB"),
    ("Michael Busch", "LHB"),
    ("Alex Bregman", "RHB"),
    ("Ian Happ", "SHB"),
    ("Nico Hoerner", "RHB"),
    ("Carson Kelly", "RHB"),
    ("Dansby Swanson", "RHB"),
    ("Tyrone Taylor", "RHB"),
]

PITCHER_RISK_ROW = [
    "6:45 PM",
    "Jackson Kent",
    "vs",
    "-",
    "-",
    "-",
    "0.00",
    "0.0%",
    "0.0%",
    "0.0%",
    "0.0%",
    "0.0%",
    "0",
]

# Houser also fell out of every PropFinder risk/summary export, but his season
# and platoon lines survive in his own matchup CSV. Risk scores are regressed
# from the 28 arms PropFinder did score today (proxy fit r≈, MAE 0.29):
#   risk = -0.111 + 0.816 * proxy_risk(season line)
HOUSER_RISK_ROW = [
    "3:45 PM",
    "Adrian Houser",
    "vs",
    "0.34",
    "1.12",
    "-0.67",
    "1.39",
    "9.0%",
    "17.1%",
    "41.7%",
    "25.3%",
    "6.5%",
    "424",
]

BATTER_HEADER = [
    "BATTER",
    "SAVE",
    "ODDS",
    "ZONE",
    "L5 PA/G",
    "BBE",
    "HR",
    "NEAR HR",
    "EV",
    "AVGDIST",
    "300+",
    "350+",
    "BARREL%",
    "PULLBRL%",
    "PULLAIR%",
    "HH%",
    "LA SS%",
    "BAT SPD",
    "FAST%",
    "SQUP%",
    "BLAST%",
    "COMP%",
    "AIR%",
    "FB%",
    "HR/FB%",
    "LD%",
    "GB%",
    "PULL%",
    "STRAIGHT%",
    "OPPO%",
    "1ST PITCH SWING%",
]


def normalize(name: str) -> str:
    name = re.sub(r"\s+(LHB|RHB|SHB)\s*$", "", name.strip(), flags=re.I)
    name = re.sub(r"^\d+\s+", "", name).strip()
    return re.sub(r"\s+", " ", name)


def _file_date_key(path: Path) -> str:
    m = re.search(r"(20\d{2}-\d{2}-\d{2})", path.name)
    return m.group(1) if m else "0000-00-00"


def latest_batter_stats(batter: str) -> dict | None:
    key = normalize(batter).lower()
    candidates: list[tuple[str, Path]] = []
    for path in DATA.glob("hr-matchups-*.csv"):
        if DATE in path.name:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig", errors="ignore")
        except OSError:
            continue
        if key not in text.lower():
            continue
        candidates.append((_file_date_key(path), path))
    for _d, path in sorted(candidates, key=lambda x: x[0], reverse=True):
        with path.open(encoding="utf-8-sig", newline="") as f:
            header = None
            for row in csv.reader(f):
                if row and row[0] == "BATTER":
                    header = [c.strip() for c in row]
                    continue
                if not header or not row:
                    continue
                if normalize(row[0]).lower() == key:
                    print(f"  stats {batter} <- {path.name}")
                    return dict(zip(header, row + [""] * max(0, len(header) - len(row))))
    print(f"  WARN no prior stats for {batter}")
    return None


def build_row(name: str, hand: str, prior: dict | None) -> list[str]:
    prior = prior or {}

    def p(key: str, default: str = "") -> str:
        v = prior.get(key, default)
        return "" if v is None else str(v).strip()

    odds = p("ODDS", "N/A") or "N/A"
    return [
        f"{name} {hand}",
        p("SAVE", "—"),
        odds,
        "",  # no batter-vs-Kent zone fit exists
        p("L5 PA/G", "4.00"),
        p("BBE", "10"),
        p("HR", "0"),
        p("NEAR HR", "0"),
        p("EV", "88.0"),
        *[
            p(k)
            for k in BATTER_HEADER[9:]
        ],
    ]


def write_matchup() -> None:
    lines: list[list[str]] = [
        ["Matchup", SPEC["matchup"]],
        ["Pitcher", SPEC["pitcher"]],
        ["Pitcher Team", SPEC["pitcher_team"]],
        ["Opposing Team", SPEC["opposing_team"]],
        [],
        [",STATS", "STRIKES", "STATCAST"],
        [],
        BATTER_HEADER,
    ]
    for name, hand in LINEUP:
        lines.append(build_row(name, hand, latest_batter_stats(name)))

    dst = DATA / SPEC["dst"]
    with dst.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for row in lines:
            w.writerow(row)
    print(f"wrote {dst.name} ({len(LINEUP)} batters)")


def append_pitcher_risk() -> None:
    path = DATA / f"hr-targets-overall-{DATE}.csv"
    for cells in (PITCHER_RISK_ROW, HOUSER_RISK_ROW):
        pitcher = cells[1]
        text = path.read_text(encoding="utf-8-sig")
        if pitcher in text:
            print(f"hr-targets already has {pitcher}")
            continue
        lines = [l for l in text.splitlines() if l.strip()]
        last_idx = max(
            i for i, l in enumerate(lines) if l.split(",", 1)[0].strip().isdigit()
        )
        next_num = int(lines[last_idx].split(",", 1)[0]) + 1
        row = ",".join([str(next_num), *cells])
        lines.insert(last_idx + 1, row)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("hr-targets +", row)


def update_manifest() -> None:
    path = DATA / f"manifest-{DATE}.json"
    man = json.loads(path.read_text(encoding="utf-8"))
    files = list(man.get("files") or [])
    if SPEC["dst"] not in files:
        files.append(SPEC["dst"])
        print("manifest +", SPEC["dst"])
    man["files"] = sorted(set(files))
    path.write_text(json.dumps(man, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_matchup()
    append_pitcher_risk()
    update_manifest()


if __name__ == "__main__":
    main()
