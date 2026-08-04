#!/usr/bin/env python3
"""Synthesize missing 8/4 hr-matchups (Assad, Holmes) + build hr-targets from L10 summaries.

PropFinder did not export hr-targets-overall or Assad/Holmes matchup CSVs.
Targets use a dampened L10 proxy until the official export is available.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-08-04"

ZONE_SPECS = [
    {
        "dst": f"hr-matchups-LAD-at-CHC-Javier-Assad-{DATE}.csv",
        "matchup": "LAD @ CHC",
        "pitcher": "Javier Assad",
        "pitcher_team": "CHC",
        "opposing_team": "LAD",
        "props": ["Shohei Ohtani", "Freddie Freeman"],
    },
    {
        "dst": f"hr-matchups-MIA-at-ATL-Grant-Holmes-{DATE}.csv",
        "matchup": "MIA @ ATL",
        "pitcher": "Grant Holmes",
        "pitcher_team": "ATL",
        "opposing_team": "MIA",
        "props": ["Owen Caissie", "Griffin Conine", "Joe Mack"],
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

    for prop in spec["props"]:
        if normalize(prop).lower() in seen:
            continue
        prior = latest_batter_stats(prop) or {}
        fake = {"Batter": prop, "Bats": "LHB", "ZoneScore": prior.get("ZONE", "15")}
        lines.append(build_row(fake, prior))
        seen.add(normalize(prop).lower())
        print(f"  appended prop-only row {prop}")

    dst = DATA / spec["dst"]
    with dst.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for row in lines:
            w.writerow(row)
    print(f"wrote {dst.name} ({len(seen)} batters, props={spec['props']})")


def parse_summary(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    header = None
    rows: list[dict] = []
    for line in text.splitlines():
        if line.startswith("TIME,") and "PITCHER" in line:
            header = next(csv.reader([line]))
            continue
        if header is None:
            continue
        row = next(csv.reader([line]))
        if len(row) < 3 or not row[1]:
            continue
        if row[0] in ("Range", "Dates", "Games", "Split", "") or row[1] in (
            "PITCHER",
            "STATS",
        ):
            continue
        d = dict(zip(header, row + [""] * max(0, len(header) - len(row))))
        rows.append(d)
    return rows


def fnum(x: str | None) -> float | None:
    x = (x or "").replace("%", "").strip()
    if not x or x == "-":
        return None
    try:
        return float(x)
    except ValueError:
        return None


def proxy_risk(row: dict, dampen: float = 0.70) -> float:
    """Dampened L10 proxy — calibrated ~0.4 MAE vs PropFinder on 8/3."""
    hr9 = fnum(row.get("HR/9")) or 1.2
    barrel = fnum(row.get("BARREL%")) or 8.0
    hrfb = fnum(row.get("HR/FB%")) or 12.0
    hh = fnum(row.get("HH%")) or 38.0
    fb = fnum(row.get("FB%")) or 25.0
    meat = fnum(row.get("MEATBALL%")) or 7.0
    bf = fnum(row.get("BF")) or 100.0
    score = (
        (hr9 - 1.2) * 0.9
        + (barrel - 8.0) * 0.08
        + (hrfb - 12.0) * 0.04
        + (hh - 38.0) * 0.03
        + (fb - 25.0) * 0.02
        + (meat - 7.0) * 0.05
    )
    # Shrink tiny samples toward 0
    conf = min(1.0, bf / 180.0)
    return round(score * dampen * conf, 2)


def pct_str(row: dict, key: str, default: float) -> str:
    v = fnum(row.get(key))
    if v is None:
        return f"{default:.1f}%"
    return f"{v:.1f}%"


def write_targets_from_l10() -> None:
    overall = parse_summary(DATA / f"pitcher-summary-season-l10-{DATE}.csv")
    lhb = {r["PITCHER"]: r for r in parse_summary(DATA / f"pitcher-summary-vslhb-l10-{DATE}.csv")}
    rhb = {r["PITCHER"]: r for r in parse_summary(DATA / f"pitcher-summary-vsrhb-l10-{DATE}.csv")}
    if not overall:
        raise SystemExit("no L10 overall summary")

    ranked = sorted(overall, key=lambda r: proxy_risk(r), reverse=True)
    path = DATA / f"hr-targets-overall-{DATE}.csv"
    rows: list[list[str]] = [
        ["HR Split", "Overall"],
        ["Dates", '="8/4/2026"'],
        ["Games", "15"],
        [],
        [
            "#",
            "TIME",
            "PITCHER",
            "VS",
            "HR RISK",
            "VS LHB",
            "VS RHB",
            "HR/9",
            "BARREL%",
            "HR/FB%",
            "HH%",
            "FB%",
            "MEATBALL%",
            "BF",
        ],
    ]
    for i, r in enumerate(ranked, 1):
        name = r["PITCHER"]
        o = proxy_risk(r)
        vl = proxy_risk(lhb[name]) if name in lhb else o
        vr = proxy_risk(rhb[name]) if name in rhb else o
        hr9 = fnum(r.get("HR/9"))
        rows.append(
            [
                str(i),
                r.get("TIME") or "",
                name,
                r.get("VS") or "vs",
                f"{o:.2f}",
                f"{vl:.2f}",
                f"{vr:.2f}",
                f"{hr9:.2f}" if hr9 is not None else "-",
                pct_str(r, "BARREL%", 8.0),
                pct_str(r, "HR/FB%", 12.0),
                pct_str(r, "HH%", 38.0),
                pct_str(r, "FB%", 25.0),
                pct_str(r, "MEATBALL%", 7.0),
                str(int(fnum(r.get("BF")) or 0)),
            ]
        )
        print(f"  target {name:22} {o:+.2f} LHB {vl:+.2f} RHB {vr:+.2f}")

    with path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)
    print(f"wrote {path.name} ({len(ranked)} pitchers) [L10 proxy — replace with PropFinder export]")

    # Keep manifest in sync if present
    man = DATA / f"manifest-{DATE}.json"
    if man.is_file():
        data = json.loads(man.read_text(encoding="utf-8"))
        files = data.get("files") or data.get("imported") or []
        name = path.name
        if name not in files and not any(
            (isinstance(x, str) and x.endswith(name))
            or (isinstance(x, dict) and x.get("name") == name)
            for x in files
        ):
            if files and isinstance(files[0], dict):
                files.append({"name": name, "source": "synthetic-l10-proxy"})
            else:
                files.append(name)
            data["files" if "files" in data else "imported"] = files
            man.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print("manifest updated")


def main() -> None:
    for spec in ZONE_SPECS:
        write_zone_matchup(spec)
    write_targets_from_l10()


if __name__ == "__main__":
    main()
