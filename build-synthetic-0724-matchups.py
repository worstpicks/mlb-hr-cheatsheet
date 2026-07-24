#!/usr/bin/env python3
"""Synthesize missing 7/24 hr-matchups from zone rows + latest prior batter stats."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-07-24"

# pitcher_team is the SP's team; opposing batters face that SP.
SPECS = [
    {
        "dst": f"hr-matchups-SEA-at-TEX-MacKenzie-Gore-{DATE}.csv",
        "matchup": "SEA @ TEX",
        "pitcher": "MacKenzie Gore",
        "pitcher_team": "TEX",
        "opposing_team": "SEA",
        "props": ["Josh Naylor"],
    },
    {
        "dst": f"hr-matchups-TOR-at-BOS-Trey-Yesavage-{DATE}.csv",
        "matchup": "TOR @ BOS",
        "pitcher": "Trey Yesavage",
        "pitcher_team": "TOR",
        "opposing_team": "BOS",
        "props": ["Willson Contreras"],
    },
    {
        "dst": f"hr-matchups-TOR-at-BOS-Patrick-Sandoval-{DATE}.csv",
        "matchup": "TOR @ BOS",
        "pitcher": "Patrick Sandoval",
        "pitcher_team": "BOS",
        "opposing_team": "TOR",
        "props": ["Kazuma Okamoto", "Yohendrick Pinango"],
    },
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
    return name


def latest_batter_stats(batter: str) -> dict | None:
    """Pull most recent hr-matchups row for this batter (any date)."""
    key = batter.lower()
    best: tuple[str, dict] | None = None
    for path in sorted(DATA.glob("hr-matchups-*.csv"), reverse=True):
        if DATE in path.name or "(1)" in path.name:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig", errors="ignore")
        except OSError:
            continue
        if key not in text.lower():
            continue
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            header = None
            for row in reader:
                if row and row[0] == "BATTER":
                    header = [c.strip() for c in row]
                    continue
                if not header or not row:
                    continue
                if normalize(row[0]).lower() == key:
                    data = dict(zip(header, row + [""] * max(0, len(header) - len(row))))
                    best = (path.name, data)
                    break
        if best:
            break
    return best[1] if best else None


def zone_rows_for_pitcher(pitcher: str) -> list[dict]:
    path = DATA / f"zone-matchups-{DATE}.csv"
    out = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if (row.get("Pitcher") or "").strip() == pitcher:
                out.append(row)
    return out


def hand_suffix(bats: str) -> str:
    b = (bats or "").upper()
    if b.startswith("L"):
        return "LHB"
    if b.startswith("S"):
        return "SHB"
    return "RHB"


def build_row(zone: dict, prior: dict | None) -> list[str]:
    name = zone["Batter"]
    hand = hand_suffix(zone.get("Bats", "RHB"))
    zone_score = (zone.get("ZoneScore") or "").strip() or ""
    prior = prior or {}

    def p(key, default=""):
        v = prior.get(key, default)
        return "" if v is None else str(v).strip()

    odds = p("ODDS", "N/A") or "N/A"
    return [
        f"{name} {hand}",
        p("SAVE", ""),
        odds if odds.startswith(("+", "-")) or odds == "N/A" else odds,
        zone_score or p("ZONE", ""),
        p("L5 PA/G", "4.20"),
        p("BBE", "10"),
        p("HR", "0"),
        p("NEAR HR", "0"),
        p("EV", "90.0"),
        p("AVGDIST", ""),
        p("300+", ""),
        p("350+", ""),
        p("BARREL%", ""),
        p("PULLBRL%", ""),
        p("PULLAIR%", ""),
        p("HH%", ""),
        p("LA SS%", ""),
        p("BAT SPD", ""),
        p("FAST%", ""),
        p("SQUP%", ""),
        p("BLAST%", ""),
        p("COMP%", ""),
        p("AIR%", ""),
        p("FB%", ""),
        p("HR/FB%", ""),
        p("LD%", ""),
        p("GB%", ""),
        p("PULL%", ""),
        p("STRAIGHT%", ""),
        p("OPPO%", ""),
        p("1ST PITCH SWING%", ""),
    ]


def write_matchup(spec: dict) -> None:
    zones = zone_rows_for_pitcher(spec["pitcher"])
    # Prefer listing all zone batters so game/SP derives cleanly; props guaranteed.
    if not zones:
        raise SystemExit(f"no zone rows for {spec['pitcher']}")

    lines: list[list[str]] = [
        ["Matchup", spec["matchup"]],
        ["Pitcher", spec["pitcher"]],
        ["Pitcher Team", spec["pitcher_team"]],
        ["Opposing Team", spec["opposing_team"]],
        [],
        [",STATS", "STRIKES", "STATCAST"],
        [],
        BATTER_HEADER,
    ]
    prop_set = {n.lower() for n in spec["props"]}
    seen = set()
    # props first, then remaining zone bats
    ordered = sorted(zones, key=lambda z: (0 if z["Batter"].lower() in prop_set else 1, z["Batter"]))
    for z in ordered:
        nm = z["Batter"]
        if nm.lower() in seen:
            continue
        seen.add(nm.lower())
        prior = latest_batter_stats(nm)
        lines.append(build_row(z, prior))

    dst = DATA / spec["dst"]
    with dst.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for row in lines:
            w.writerow(row)
    print(f"wrote {dst.name} ({len(seen)} batters, props={[p for p in spec['props'] if p.lower() in seen]})")


def update_manifest() -> None:
    path = DATA / f"manifest-{DATE}.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    files = list(manifest.get("files", []))
    # drop duplicate Grayson (1)
    files = [f for f in files if "(1)" not in f]
    for spec in SPECS:
        if spec["dst"] not in files:
            # insert among hr-matchups
            insert_at = next((i for i, n in enumerate(files) if not n.startswith("hr-matchups-")), len(files))
            files.insert(insert_at, spec["dst"])
    manifest["files"] = files
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("updated manifest")


def main() -> None:
    # remove junk duplicate
    junk = DATA / f"hr-matchups-LAA-at-SF-Grayson-Rodriguez-{DATE}(1).csv"
    if junk.exists():
        junk.unlink()
        print("removed", junk.name)
    for spec in SPECS:
        write_matchup(spec)
    update_manifest()


if __name__ == "__main__":
    main()
