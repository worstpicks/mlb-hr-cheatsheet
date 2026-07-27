#!/usr/bin/env python3
"""Synthesize missing 7/27 hr-matchups: Mitch Keller (ARI @ PIT)."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-07-27"

ZONE_SPECS = [
    {
        "dst": f"hr-matchups-ARI-at-PIT-Mitch-Keller-{DATE}.csv",
        "matchup": "ARI @ PIT",
        "pitcher": "Mitch Keller",
        "pitcher_team": "PIT",
        "opposing_team": "ARI",
        "props": ["Corbin Carroll", "Ketel Marte", "Ryan Waldschmidt"],
    },
]

# PropFinder hr-targets omitted Matthew Liberatore (24th SP). Backfill from his
# 7/27 matchup season line (HR/9 1.64 / elevated vs LHB) so gameMeta + splits render.
TARGET_BACKFILL = [
    {
        "pitcher": "Matthew Liberatore",
        "vs": "vs",
        "overall": 0.48,
        "vs_lhb": 0.72,
        "vs_rhb": 0.28,
        "hr9": 1.64,
        "barrel": 9.3,
        "hr_fb": 17.2,
        "hh": 43.0,
        "fb": 29.0,
        "meatball": 7.1,
        "bf": 437,
        "time": "7:45 PM",
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


def _file_date_key(path: Path) -> str:
    m = re.search(r"(20\d{2}-\d{2}-\d{2})", path.name)
    return m.group(1) if m else "0000-00-00"


def latest_batter_stats(batter: str) -> dict | None:
    """Prefer the newest PropFinder matchup row (by filename date), not alpha-sorted paths."""
    key = batter.lower()
    candidates: list[tuple[str, Path]] = []
    for path in DATA.glob("hr-matchups-*.csv"):
        if DATE in path.name or "(1)" in path.name:
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
            reader = csv.reader(f)
            header = None
            for row in reader:
                if row and row[0] == "BATTER":
                    header = [c.strip() for c in row]
                    continue
                if not header or not row:
                    continue
                if normalize(row[0]).lower() == key:
                    print(f"  stats {batter} <- {path.name}")
                    return dict(zip(header, row + [""] * max(0, len(header) - len(row))))
    return None


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


def write_zone_matchup(spec: dict) -> None:
    zones = zone_rows_for_pitcher(spec["pitcher"])
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
    seen: set[str] = set()
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
    print(
        f"wrote {dst.name} ({len(seen)} batters, "
        f"props={[p for p in spec['props'] if p.lower() in seen]})"
    )


def backfill_hr_targets() -> None:
    path = DATA / f"hr-targets-overall-{DATE}.csv"
    text = path.read_text(encoding="utf-8-sig")
    if any(spec["pitcher"] in text for spec in TARGET_BACKFILL):
        present = [s["pitcher"] for s in TARGET_BACKFILL if s["pitcher"] in text]
        print(f"hr-targets already has {present}")
        return
    rows = text.rstrip("\n").split("\n")
    nums = [int(r.split(",")[0]) for r in rows[5:] if r and r[0].isdigit()]
    next_num = (max(nums) if nums else 0) + 1
    added = []
    for spec in TARGET_BACKFILL:
        if spec["pitcher"] in text:
            continue
        row = (
            f"{next_num},{spec['time']},{spec['pitcher']},{spec['vs']},"
            f"{spec['overall']:.2f},{spec['vs_lhb']:.2f},{spec['vs_rhb']:.2f},"
            f"{spec['hr9']:.2f},{spec['barrel']:.1f}%,{spec['hr_fb']:.1f}%,"
            f"{spec['hh']:.1f}%,{spec['fb']:.1f}%,{spec['meatball']:.1f}%,{spec['bf']}"
        )
        rows.append(row)
        added.append(spec["pitcher"])
        next_num += 1
    if added:
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        print(f"backfilled hr-targets: {added}")


def update_manifest() -> None:
    path = DATA / f"manifest-{DATE}.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    files = list(manifest.get("files", []))
    for spec in ZONE_SPECS:
        if spec["dst"] not in files:
            insert_at = next(
                (i for i, n in enumerate(files) if not n.startswith("hr-matchups-")),
                len(files),
            )
            files.insert(insert_at, spec["dst"])
    hr = sorted(f for f in files if f.startswith("hr-matchups-"))
    rest = [f for f in files if not f.startswith("hr-matchups-")]
    manifest["files"] = hr + rest
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("updated manifest")


def main() -> None:
    for spec in ZONE_SPECS:
        write_zone_matchup(spec)
    backfill_hr_targets()
    update_manifest()


if __name__ == "__main__":
    main()
