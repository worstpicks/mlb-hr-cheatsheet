#!/usr/bin/env python3
"""Synthesize missing 8/2 hr-matchups: Anthony Kay, Robert Stock, JR Ritchie."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-08-02"

ZONE_SPECS = [
    {
        "dst": f"hr-matchups-CWS-at-TB-Anthony-Kay-{DATE}.csv",
        "matchup": "CWS @ TB",
        "pitcher": "Anthony Kay",
        "pitcher_team": "CWS",
        "opposing_team": "TB",
        "props": ["Ryan Vilade", "Jonathan Aranda"],
    },
    {
        "dst": f"hr-matchups-MIA-at-NYM-Robert-Stock-{DATE}.csv",
        "matchup": "MIA @ NYM",
        "pitcher": "Robert Stock",
        "pitcher_team": "NYM",
        "opposing_team": "MIA",
        "props": ["Griffin Conine", "Kyle Stowers", "Owen Caissie", "Otto Lopez"],
    },
]

# No zone export for JR Ritchie — build from prior ATL home matchup + prop list.
RITCHIE_SPEC = {
    "dst": f"hr-matchups-WSH-at-ATL-JR-Ritchie-{DATE}.csv",
    "matchup": "WSH @ ATL",
    "pitcher": "JR Ritchie",
    "pitcher_team": "ATL",
    "opposing_team": "WSH",
    "props": ["James Wood", "CJ Abrams", "Luis Garcia Jr.", "Jacob Young"],
    "donor": "hr-matchups-WSH-at-ATL-Reynaldo-Lopez-2026-08-01.csv",
}

TARGET_BACKFILL = [
    {
        "pitcher": "JR Ritchie",
        "vs": "vs",
        "overall": 0.55,
        "vs_lhb": 0.40,
        "vs_rhb": 0.70,
        "hr9": 1.60,
        "barrel": 8.5,
        "hr_fb": 16.0,
        "hh": 38.0,
        "fb": 28.0,
        "meatball": 7.0,
        "bf": 150,
        "time": "1:35 PM",
    },
    {
        "pitcher": "Robert Stock",
        "vs": "vs",
        "overall": 0.50,
        "vs_lhb": 0.35,
        "vs_rhb": 0.65,
        "hr9": 1.55,
        "barrel": 8.0,
        "hr_fb": 15.0,
        "hh": 37.0,
        "fb": 27.0,
        "meatball": 7.0,
        "bf": 80,
        "time": "1:40 PM",
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
        p("SAVE", "—"),
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

    # Ensure listed props appear even if not in zone sample.
    for prop in spec["props"]:
        if normalize(prop).lower() in seen:
            continue
        prior = latest_batter_stats(prop) or {}
        bats = "LHB"
        fake = {"Batter": prop, "Bats": bats, "ZoneScore": prior.get("ZONE", "15")}
        lines.append(build_row(fake, prior))
        seen.add(normalize(prop).lower())
        print(f"  appended prop-only row {prop}")

    dst = DATA / spec["dst"]
    with dst.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for row in lines:
            w.writerow(row)
    print(f"wrote {dst.name} ({len(seen)} batters, props={spec['props']})")


def write_ritchie() -> None:
    donor = DATA / RITCHIE_SPEC["donor"]
    # Prefer donor if present; else scrape any recent WSH@ATL home SP file.
    if not donor.is_file():
        cands = sorted(DATA.glob("hr-matchups-WSH-at-ATL-*-2026-08-0*.csv"), reverse=True)
        donor = next((p for p in cands if "Cavalli" not in p.name), cands[0] if cands else None)
    if donor is None or not donor.is_file():
        raise SystemExit("no donor matchup for JR Ritchie")

    # Collect batter rows from donor for WSH lineup names + props.
    batters: dict[str, list[str]] = {}
    in_b = False
    with donor.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            if row and row[0] == "BATTER":
                in_b = True
                continue
            if not in_b or not row:
                continue
            nm = normalize(row[0])
            batters[nm.lower()] = row

    lines: list[list[str]] = [
        ["Matchup", RITCHIE_SPEC["matchup"]],
        ["Pitcher", RITCHIE_SPEC["pitcher"]],
        ["Pitcher Team", RITCHIE_SPEC["pitcher_team"]],
        ["Opposing Team", RITCHIE_SPEC["opposing_team"]],
        [],
        [",STATS", "STRIKES", "STATCAST"],
        [],
        BATTER_HEADER,
    ]
    seen: set[str] = set()
    for prop in RITCHIE_SPEC["props"]:
        key = normalize(prop).lower()
        prior = latest_batter_stats(prop)
        if key in batters:
            row = list(batters[key])
            # keep ZONE from prior/donor
            lines.append(row)
        elif prior:
            fake = {"Batter": prop, "Bats": "LHB", "ZoneScore": prior.get("ZONE", "18")}
            lines.append(build_row(fake, prior))
        else:
            fake = {"Batter": prop, "Bats": "LHB", "ZoneScore": "18"}
            lines.append(build_row(fake, {"ODDS": "N/A", "HR": "1", "NEAR HR": "1", "EV": "92.0"}))
        seen.add(key)
        print(f"  ritchie row {prop}")

    # Pad with other donor batters for realism.
    for key, row in batters.items():
        if key in seen:
            continue
        lines.append(row)
        seen.add(key)

    dst = DATA / RITCHIE_SPEC["dst"]
    with dst.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for row in lines:
            w.writerow(row)
    print(f"wrote {dst.name} ({len(seen)} batters)")


def backfill_targets() -> None:
    """Append Stock/Ritchie in PropFinder numbered-row format load_pitcher_risk expects."""
    path = DATA / f"hr-targets-overall-{DATE}.csv"
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    # Drop prior broken short backfill lines (name,overall only).
    cleaned: list[list[str]] = []
    for row in rows:
        if len(row) == 2 and row[0] in ("JR Ritchie", "Robert Stock"):
            continue
        cleaned.append(row)
    rows = cleaned

    have = {
        r[2].strip().lower()
        for r in rows
        if len(r) >= 7 and r[0].isdigit() and r[2].strip()
    }
    max_n = max((int(r[0]) for r in rows if r and r[0].isdigit()), default=0)
    new_rows: list[list[str]] = []
    for spec in TARGET_BACKFILL:
        if spec["pitcher"].lower() in have:
            continue
        max_n += 1
        new_rows.append(
            [
                str(max_n),
                spec["time"],
                spec["pitcher"],
                spec["vs"],
                f"{spec['overall']:.2f}",
                f"{spec['vs_lhb']:.2f}",
                f"{spec['vs_rhb']:.2f}",
                f"{spec['hr9']:.2f}",
                f"{spec['barrel']:.1f}%",
                f"{spec['hr_fb']:.1f}%",
                f"{spec['hh']:.1f}%",
                f"{spec['fb']:.1f}%",
                f"{spec['meatball']:.1f}%",
                str(spec["bf"]),
            ]
        )
        print(f"backfill target {spec['pitcher']} overall={spec['overall']}")

    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerows(rows + new_rows)
    if new_rows:
        print("backfilled hr-targets:", [r[2] for r in new_rows])
    else:
        print("hr-targets already complete for backfill list")


def update_manifest() -> None:
    man_path = DATA / f"manifest-{DATE}.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    files = man.get("files") or []
    for spec in ZONE_SPECS + [RITCHIE_SPEC]:
        name = spec["dst"]
        if name not in files:
            files.append(name)
    man["files"] = sorted(set(files))
    man_path.write_text(json.dumps(man, indent=2) + "\n", encoding="utf-8")
    print("updated manifest")


def main() -> None:
    for spec in ZONE_SPECS:
        write_zone_matchup(spec)
    write_ritchie()
    backfill_targets()
    update_manifest()


if __name__ == "__main__":
    main()
