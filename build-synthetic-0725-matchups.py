#!/usr/bin/env python3
"""Synthesize missing 7/25 hr-matchups: Keller, Prielipp, Young; backfill targets; drop stale SPs."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-07-25"

# Rename/copy existing matchup exports to confirmed probables.
COPY_SPECS = [
    {
        "src": f"hr-matchups-NYY-at-PHI-Tim-Mayza-{DATE}.csv",
        "dst": f"hr-matchups-NYY-at-PHI-Brian-Keller-{DATE}.csv",
        "pitcher": "Brian Keller",
    },
    {
        "src": f"hr-matchups-ATH-at-MIN-Mike-Paredes-{DATE}.csv",
        "dst": f"hr-matchups-ATH-at-MIN-Connor-Prielipp-{DATE}.csv",
        "pitcher": "Connor Prielipp",
    },
]

# Zone-synthesized SP with no PropFinder hr-matchups export.
ZONE_SPECS = [
    {
        "dst": f"hr-matchups-ATL-at-BAL-Brandon-Young-{DATE}.csv",
        "matchup": "ATL @ BAL",
        "pitcher": "Brandon Young",
        "pitcher_team": "BAL",
        "opposing_team": "ATL",
        "props": ["Drake Baldwin", "Matt Olson", "Mike Yastrzemski"],
    },
]

REMOVE_FILES = [
    f"hr-matchups-NYY-at-PHI-Tim-Mayza-{DATE}.csv",
    f"hr-matchups-ATH-at-MIN-Mike-Paredes-{DATE}.csv",
    f"hr-matchups-ATL-at-BAL-Bryce-Elder-{DATE}(1).csv",
]

# hr-targets rows to append (estimated from stale export or matchup stat line).
TARGET_BACKFILL = [
    {
        "pitcher": "Brian Keller",
        "vs": "vs",
        "overall": -0.57,
        "vs_lhb": -1.14,
        "vs_rhb": 0.24,
        "hr9": 0.61,
        "barrel": 8.0,
        "hr_fb": 9.6,
        "hh": 50.2,
        "fb": 19.0,
        "meatball": 6.3,
        "bf": 284,
        "time": "6:05 PM",
    },
    {
        "pitcher": "Connor Prielipp",
        "vs": "vs",
        "overall": 0.83,
        "vs_lhb": 0.25,
        "vs_rhb": 1.18,
        "hr9": 1.72,
        "barrel": 8.2,
        "hr_fb": 18.7,
        "hh": 53.3,
        "fb": 28.3,
        "meatball": 8.6,
        "bf": 244,
        "time": "7:10 PM",
    },
    {
        "pitcher": "Mason Barnett",
        "vs": "@",
        "overall": 1.05,
        "vs_lhb": 1.35,
        "vs_rhb": 0.85,
        "hr9": 2.11,
        "barrel": 10.5,
        "hr_fb": 20.0,
        "hh": 43.9,
        "fb": 35.1,
        "meatball": 5.7,
        "bf": 90,
        "time": "7:10 PM",
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


def copy_matchup(spec: dict) -> None:
    src = DATA / spec["src"]
    dst = DATA / spec["dst"]
    if dst.exists() and not src.exists():
        # Idempotent: already renamed/copied on a prior import pass.
        text = dst.read_text(encoding="utf-8-sig")
        if f"Pitcher,{spec['pitcher']}" in text or f'Pitcher,"{spec["pitcher"]}"' in text:
            print(f"keep existing {dst.name} ({spec['pitcher']})")
            return
    if not src.exists():
        if dst.exists():
            print(f"keep existing {dst.name} (source {src.name} already removed)")
            return
        raise SystemExit(f"missing source {src.name}")
    text = src.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    out: list[str] = []
    for line in lines:
        if line.startswith("Pitcher,"):
            out.append(f"Pitcher,{spec['pitcher']}")
        else:
            out.append(line)
    dst.write_text("\n".join(out) + ("\n" if out else ""), encoding="utf-8")
    print(f"copied {src.name} -> {dst.name} ({spec['pitcher']})")


def latest_batter_stats(batter: str) -> dict | None:
    key = batter.lower()
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
                    return dict(zip(header, row + [""] * max(0, len(header) - len(row))))
        break
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
    existing = {ln.split(",")[2] for ln in text.splitlines()[5:] if ln.count(",") >= 3}
    rows = text.rstrip("\n").split("\n")
    next_num = max(int(r.split(",")[0]) for r in rows[5:] if r and r[0].isdigit()) + 1
    added = []
    for spec in TARGET_BACKFILL:
        if spec["pitcher"] in existing:
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
    else:
        print("hr-targets already has Keller/Priellipp/Barnett")


def remove_stale() -> None:
    for name in REMOVE_FILES:
        path = DATA / name
        if path.exists():
            path.unlink()
            print(f"removed {name}")


def update_manifest() -> None:
    path = DATA / f"manifest-{DATE}.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    files = [f for f in manifest.get("files", []) if f not in REMOVE_FILES and "(1)" not in f]
    for spec in COPY_SPECS:
        if spec["dst"] not in files:
            insert_at = next(
                (i for i, n in enumerate(files) if not n.startswith("hr-matchups-")),
                len(files),
            )
            files.insert(insert_at, spec["dst"])
    for spec in ZONE_SPECS:
        if spec["dst"] not in files:
            insert_at = next(
                (i for i, n in enumerate(files) if not n.startswith("hr-matchups-")),
                len(files),
            )
            files.insert(insert_at, spec["dst"])
    manifest["files"] = sorted(set(files), key=lambda x: (0 if x.startswith("hr-matchups-") else 1, x))
    # Keep hr-matchups grouped — re-sort preserving relative order
    hr = [f for f in manifest["files"] if f.startswith("hr-matchups-")]
    rest = [f for f in manifest["files"] if not f.startswith("hr-matchups-")]
    manifest["files"] = sorted(hr) + rest
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("updated manifest")


def main() -> None:
    for spec in COPY_SPECS:
        copy_matchup(spec)
    for spec in ZONE_SPECS:
        write_zone_matchup(spec)
    backfill_hr_targets()
    remove_stale()
    update_manifest()


if __name__ == "__main__":
    main()
