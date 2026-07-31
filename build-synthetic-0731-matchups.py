#!/usr/bin/env python3
"""Synthesize missing 7/31 hr-matchups: Michael Wacha + Foster Griffin."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-07-31"

ZONE_SPECS = [
    {
        "dst": f"hr-matchups-KC-at-COL-Michael-Wacha-{DATE}.csv",
        "matchup": "KC @ COL",
        "pitcher": "Michael Wacha",
        "pitcher_team": "KC",
        "opposing_team": "COL",
        "props": ["Hunter Goodman", "Willi Castro", "Mickey Moniak"],
    },
    {
        "dst": f"hr-matchups-WSH-at-ATL-Foster-Griffin-{DATE}.csv",
        "matchup": "WSH @ ATL",
        "pitcher": "Foster Griffin",
        "pitcher_team": "WSH",
        "opposing_team": "ATL",
        "props": ["Austin Riley", "Matt Olson", "Ozzie Albies"],
    },
]

# PropFinder hr-targets omitted some slate SPs — backfill so gameMeta splits render.
TARGET_BACKFILL = [
    {
        "pitcher": "Jeffrey Springs",
        "vs": "vs",
        "overall": 0.85,
        "vs_lhb": 0.40,
        "vs_rhb": 1.10,
        "hr9": 1.90,
        "barrel": 9.5,
        "hr_fb": 18.0,
        "hh": 40.0,
        "fb": 30.0,
        "meatball": 7.5,
        "bf": 900,
        "time": "9:40 PM",
    },
    {
        "pitcher": "Carson Whisenhunt",
        "vs": "@",
        "overall": 0.55,
        "vs_lhb": 0.30,
        "vs_rhb": 0.70,
        "hr9": 1.60,
        "barrel": 8.5,
        "hr_fb": 16.0,
        "hh": 38.0,
        "fb": 28.0,
        "meatball": 7.0,
        "bf": 200,
        "time": "9:45 PM",
    },
    {
        "pitcher": "German Marquez",
        "vs": "vs",
        "overall": 0.70,
        "vs_lhb": 0.50,
        "vs_rhb": 0.85,
        "hr9": 1.75,
        "barrel": 9.0,
        "hr_fb": 17.0,
        "hh": 40.0,
        "fb": 29.0,
        "meatball": 7.2,
        "bf": 400,
        "time": "9:45 PM",
    },
    {
        "pitcher": "Brian Keller",
        "vs": "@",
        "overall": 0.45,
        "vs_lhb": 0.35,
        "vs_rhb": 0.55,
        "hr9": 1.50,
        "barrel": 8.0,
        "hr_fb": 15.0,
        "hh": 38.0,
        "fb": 27.0,
        "meatball": 7.0,
        "bf": 80,
        "time": "7:05 PM",
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
    return re.sub(r"\s+", " ", name)


def _file_date_key(path: Path) -> str:
    m = re.search(r"(20\d{2}-\d{2}-\d{2})", path.name)
    return m.group(1) if m else "0000-00-00"


def latest_batter_stats(batter: str) -> dict | None:
    key = normalize(batter).lower()
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
    name = normalize(zone["Batter"])
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
    prop_set = {normalize(n).lower() for n in spec["props"]}
    seen: set[str] = set()
    ordered = sorted(
        zones,
        key=lambda z: (0 if normalize(z["Batter"]).lower() in prop_set else 1, z["Batter"]),
    )
    for z in ordered:
        nm = normalize(z["Batter"])
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
        f"props={[p for p in spec['props'] if normalize(p).lower() in seen]})"
    )


def estimate_risk_from_weak_spots(pitcher: str) -> dict | None:
    """Rough overall/LHB/RHB from weak-spots season HR/9 + HH if targets missing."""
    matches = list(DATA.glob(f"pitcher-weak-spots-*-{pitcher.replace(' ', '-')}-{DATE}.csv"))
    if not matches:
        # try slug variants
        slug = pitcher.replace(" ", "-")
        matches = list(DATA.glob(f"pitcher-weak-spots-*{slug}-{DATE}.csv"))
    if not matches:
        return None
    # Prefer reading pitcher-summary if present
    return None


def risk_from_summary(pitcher: str) -> dict | None:
    """Pull L10 season summary if available for missing targets."""
    path = DATA / f"pitcher-summary-season-season-{DATE}.csv"
    if not path.exists():
        path = DATA / f"pitcher-summary-season-l10-{DATE}.csv"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8-sig")
    # find header
    lines = text.splitlines()
    header_idx = next((i for i, ln in enumerate(lines) if "PITCHER" in ln.upper() and "HR" in ln.upper()), None)
    if header_idx is None:
        # try simpler parse
        for ln in lines:
            if pitcher.lower() in ln.lower():
                print("summary hit", ln[:120])
        return None
    reader = csv.DictReader(lines[header_idx:])
    for row in reader:
        name = (row.get("PITCHER") or row.get("Pitcher") or "").strip()
        if name.lower() == pitcher.lower():
            print("summary row", row)
            return row
    return None


def backfill_hr_targets() -> None:
    path = DATA / f"hr-targets-overall-{DATE}.csv"
    text = path.read_text(encoding="utf-8-sig")
    rows = text.rstrip("\n").split("\n")
    nums = [int(r.split(",")[0]) for r in rows[5:] if r and r[0].isdigit()]
    next_num = (max(nums) if nums else 0) + 1
    added = []
    for spec in TARGET_BACKFILL:
        if spec["pitcher"] in text:
            continue
        # Try to refine Springs from prior slate if available
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
        print("hr-targets already complete for backfill list")


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
    # Prefer prior-day Springs risk if available
    prior = DATA / "hr-targets-overall-2026-07-30.csv"
    if prior.exists():
        # no Springs on 7/30; try 7/29 ATH
        pass
    for date in ("2026-07-29", "2026-07-27", "2026-07-26", "2026-07-25"):
        p = DATA / f"hr-targets-overall-{date}.csv"
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8-sig")
        for line in t.splitlines():
            if "Jeffrey Springs" in line and line[0].isdigit():
                parts = line.split(",")
                # #,TIME,PITCHER,VS,HR RISK,VS LHB,VS RHB,HR/9,...
                try:
                    TARGET_BACKFILL[0].update(
                        {
                            "overall": float(parts[4]),
                            "vs_lhb": float(parts[5]),
                            "vs_rhb": float(parts[6]),
                            "hr9": float(parts[7]),
                            "barrel": float(parts[8].rstrip("%")),
                            "hr_fb": float(parts[9].rstrip("%")),
                            "hh": float(parts[10].rstrip("%")),
                            "fb": float(parts[11].rstrip("%")),
                            "meatball": float(parts[12].rstrip("%")),
                            "bf": int(parts[13]),
                        }
                    )
                    print(f"Springs risk from {date}: {TARGET_BACKFILL[0]['overall']}")
                except (IndexError, ValueError):
                    pass
                break
        else:
            continue
        break
    for date in ("2026-07-29", "2026-07-27", "2026-07-26", "2026-07-23"):
        p = DATA / f"hr-targets-overall-{date}.csv"
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8-sig").splitlines():
            if line[0:1].isdigit() and "German Marquez" in line:
                parts = line.split(",")
                try:
                    TARGET_BACKFILL[2].update(
                        {
                            "overall": float(parts[4]),
                            "vs_lhb": float(parts[5]),
                            "vs_rhb": float(parts[6]),
                            "hr9": float(parts[7]),
                            "barrel": float(parts[8].rstrip("%")),
                            "hr_fb": float(parts[9].rstrip("%")),
                            "hh": float(parts[10].rstrip("%")),
                            "fb": float(parts[11].rstrip("%")),
                            "meatball": float(parts[12].rstrip("%")),
                            "bf": int(parts[13]),
                        }
                    )
                    print(f"Marquez risk from {date}: {TARGET_BACKFILL[2]['overall']}")
                except (IndexError, ValueError):
                    pass
                break
    backfill_hr_targets()
    update_manifest()


if __name__ == "__main__":
    main()
