#!/usr/bin/env python3
"""Synthesize the hr-matchups games PropFinder did not export for 2026-08-17.

Two gaps on this slate:

1. ATL @ MIN (Martin Perez / Bailey Ober) shipped pitcher-weak-spots and
   pitcher-summary rows but no hr-matchups export. Without this the six listed
   bats in that game (Acuna, Olson, Riley, Yastrzemski, Buxton, Bell) would drop
   and Ober -- a real 0.64-risk arm -- would vanish from the board.

2. STL @ CIN is a doubleheader and PropFinder only exported the nightcap
   (Pallante / Lowder). Game 1 (Quinn Mathews / Chase Petty) has no matchup,
   weak-spot, zone or HR-risk row anywhere in the 8/17 pull.

Everything here is real slate data, reassembled -- nothing is invented:
  - ATL @ MIN lineups, handedness and ZONE come from zone-matchups-2026-08-17.csv
  - ATL @ MIN pitcher Season/vsLHB/vsRHB blocks come from the same-day
    pitcher-summary exports
  - STL @ CIN G1 lineups and batter form are copied verbatim from the same-day
    G2 exports: both games use the same two rosters and batter recent-form is
    pitcher-independent, so this is today's real form re-pointed at the G1 arm
  - Chase Petty's pitcher block is carried from his most recent export
    (2026-08-07, 204 BF season-to-date)
  - Quinn Mathews has no export anywhere; his block is left blank on purpose so
    the sheet renders the honest "no MLB HR data yet" lane rather than an
    invented split

ODDS are left N/A throughout: no 8/17 price was exported for either game. (The
real G2 export also carries N/A across the board, so the whole STL @ CIN
doubleheader is priceless in PropFinder today.)
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-08-17"

# pitcher -> gap spec.
#   matchup / pteam / oteam : header block written into the synthetic file
#   lineups                 : "zone"    -> pull the lineup from zone-matchups
#                             "sibling" -> copy batter rows from another export
#   sibling                 : file whose BATTER rows are this pitcher's opponents
#   block_from              : file whose Season/vsLHB/vsRHB block to carry
GAPS: dict[str, dict] = {
    "Martin Perez": {
        "matchup": "ATL @ MIN",
        "pteam": "ATL",
        "oteam": "MIN",
        "lineups": "zone",
    },
    "Bailey Ober": {
        "matchup": "ATL @ MIN",
        "pteam": "MIN",
        "oteam": "ATL",
        "lineups": "zone",
    },
    "Quinn Mathews": {
        "matchup": "STL @ CIN",
        "pteam": "STL",
        "oteam": "CIN",
        "lineups": "sibling",
        # Pallante is the STL arm in G2, so his batter rows are the CIN lineup.
        "sibling": f"hr-matchups-STL-at-CIN-Andre-Pallante-{DATE}.csv",
        "block_from": None,  # no export exists for Mathews -- blank on purpose
    },
    "Chase Petty": {
        "matchup": "STL @ CIN",
        "pteam": "CIN",
        "oteam": "STL",
        "lineups": "sibling",
        # Lowder is the CIN arm in G2, so his batter rows are the STL lineup.
        "sibling": f"hr-matchups-STL-at-CIN-Rhett-Lowder-{DATE}.csv",
        "block_from": "hr-matchups-CIN-at-WSH-Chase-Petty-2026-08-07.csv",
    },
}

PITCHER_BLOCK_COLS = [
    "IP", "BF", "BAA", "WOBA", "SLG", "ISO", "WHIP", "HR", "HR/9", "BB%",
    "WHIFF%", "K%", "PUTAWAY%", "SWSTR%", "K/9", "1STPS%", "MEATBALL%",
    "BARREL%", "HH%", "FB%", "HR/FB%", "PULLAIR%",
]

# pitcher-summary header name -> matchup pitcher-block column name
SUMMARY_TO_BLOCK = {"AVG": "BAA"}

BATTER_HEADER = [
    "BATTER", "SAVE", "ODDS", "ZONE", "L5 PA/G", "BBE", "HR", "NEAR HR", "EV",
    "AVGDIST", "300+", "350+", "BARREL%", "PULLBRL%", "PULLAIR%", "HH%",
    "LA SS%", "BAT SPD", "FAST%", "SQUP%", "BLAST%", "COMP%", "AIR%", "FB%",
    "HR/FB%", "LD%", "GB%", "PULL%", "STRAIGHT%", "OPPO%", "1ST PITCH SWING%",
]

# Written into every generated file so a later run can tell its own output apart from a
# real PropFinder export. Without this, re-importing after PropFinder finally ships these
# games would clobber the real odds with gap-fill rows.
SYNTHETIC_MARK = "SyntheticGapFill"


def slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-")


def is_real_export(path: Path) -> bool:
    """True when the file on disk came from PropFinder rather than this script."""
    if not path.is_file():
        return False
    try:
        return SYNTHETIC_MARK not in path.read_text(encoding="utf-8-sig", errors="ignore")
    except OSError:
        return False


def normalize(name: str) -> str:
    name = re.sub(r"\s+(LHB|RHB|SHB)\s*$", "", name.strip(), flags=re.I)
    name = re.sub(r"^\d+\s+", "", name).strip()
    return re.sub(r"\s+", " ", name)


def fold(name: str) -> str:
    import unicodedata

    n = unicodedata.normalize("NFKD", normalize(name))
    n = "".join(c for c in n if not unicodedata.combining(c))
    return n.lower().replace(".", "").replace("'", "").replace("’", "")


def load_zone_lineups() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    with (DATA / f"zone-matchups-{DATE}.csv").open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["Pitcher"] in GAPS:
                out.setdefault(row["Pitcher"], []).append(row)
    return out


def _summary_path(split: str) -> Path | None:
    exact = DATA / f"pitcher-summary-{split}-l10-{DATE}.csv"
    if exact.is_file():
        return exact
    hits = sorted(DATA.glob(f"pitcher-summary-{split}-*-{DATE}.csv"))
    return hits[0] if hits else None


def load_summary(split: str) -> dict[str, dict]:
    """pitcher (folded) -> {header: value} from a pitcher-summary export."""
    path = _summary_path(split)
    if path is None:
        print(f"  WARN missing pitcher-summary-{split}-*")
        return {}
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    hdr_i = next(
        (i for i, l in enumerate(lines) if l.split(",")[0].strip() == "TIME"), None
    )
    if hdr_i is None:
        return {}
    header = next(csv.reader([lines[hdr_i]]))
    out: dict[str, dict] = {}
    for line in lines[hdr_i + 1 :]:
        row = next(csv.reader([line]), None)
        if not row or len(row) < 3 or not row[1].strip():
            continue
        rec = dict(zip(header, row))
        out[fold(rec["PITCHER"])] = rec
    return out


def carried_pitcher_block(path_name: str) -> list[list[str]] | None:
    """Season/vsLHB/vsRHB rows lifted from a prior real export for this arm."""
    path = DATA / path_name
    if not path.is_file():
        print(f"  WARN carry source missing: {path_name}")
        return None
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    hdr_i = next(
        (i for i, l in enumerate(lines) if l.split(",")[0].strip() == "SPLIT"), None
    )
    if hdr_i is None:
        return None
    header = [c.strip() for c in next(csv.reader([lines[hdr_i]]))]
    out: list[list[str]] = []
    for line in lines[hdr_i + 1 :]:
        row = next(csv.reader([line]), None)
        if not row or not row[0].strip():
            break
        label = row[0].strip()
        if label not in ("Season", "vsLHB", "vsRHB"):
            break
        rec = dict(zip(header, row))
        out.append([label] + [str(rec.get(c, "")).strip() for c in PITCHER_BLOCK_COLS])
    return out or None


def pitcher_block_rows(pitcher: str, summaries: dict[str, dict[str, dict]]) -> list[list[str]]:
    spec = GAPS[pitcher]
    if spec.get("lineups") == "sibling":
        carry = spec.get("block_from")
        if carry:
            rows = carried_pitcher_block(carry)
            if rows:
                print(f"  carried {pitcher} pitcher block from {carry}")
                return rows
        # No export anywhere -- leave blank so the sheet shows "no MLB HR data yet".
        print(f"  {pitcher}: no pitcher block available, writing blank (no_data lane)")
        return [[label] + [""] * len(PITCHER_BLOCK_COLS) for label in ("Season", "vsLHB", "vsRHB")]

    rows: list[list[str]] = []
    for label, split in (("Season", "season"), ("vsLHB", "vslhb"), ("vsRHB", "vsrhb")):
        rec = summaries.get(split, {}).get(fold(pitcher))
        if not rec:
            print(f"  WARN no {split} summary row for {pitcher}")
            rows.append([label] + [""] * len(PITCHER_BLOCK_COLS))
            continue
        inv = {v: k for k, v in SUMMARY_TO_BLOCK.items()}
        rows.append(
            [label] + [str(rec.get(inv.get(c, c), "")).strip() for c in PITCHER_BLOCK_COLS]
        )
    return rows


def _file_date(path: Path) -> str:
    m = re.search(r"(20\d{2}-\d{2}-\d{2})", path.name)
    return m.group(1) if m else "0000-00-00"


_PRIOR_CACHE: dict[str, dict] | None = None


def build_prior_form_index() -> dict[str, dict]:
    """Folded batter name -> most recent prior matchup row (form stats)."""
    global _PRIOR_CACHE
    if _PRIOR_CACHE is not None:
        return _PRIOR_CACHE
    index: dict[str, tuple[str, dict]] = {}
    for path in sorted(DATA.glob("hr-matchups-*.csv"), key=_file_date):
        d = _file_date(path)
        if d >= DATE:
            continue
        lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
        hdr_i = next(
            (i for i, l in enumerate(lines) if l.split(",")[0].strip() == "BATTER"), None
        )
        if hdr_i is None:
            continue
        header = [c.strip() for c in next(csv.reader([lines[hdr_i]]))]
        for line in lines[hdr_i + 1 :]:
            row = next(csv.reader([line]), None)
            if not row or not row[0].strip():
                continue
            k = fold(row[0])
            prev = index.get(k)
            if prev is None or d >= prev[0]:
                index[k] = (d, dict(zip(header, row + [""] * (len(header) - len(row)))))
    _PRIOR_CACHE = {k: v[1] for k, v in index.items()}
    return _PRIOR_CACHE


def batter_row(zrow: dict, prior_index: dict[str, dict]) -> tuple[list[str], bool]:
    name = normalize(zrow["Batter"])
    hand = (zrow["Bats"] or "").strip() or "RHB"
    prior = prior_index.get(fold(name))

    def p(col: str, default: str = "") -> str:
        if not prior:
            return default
        v = prior.get(col, default)
        return default if v is None or str(v).strip() == "" else str(v).strip()

    zone = zrow.get("ZoneScore") or ""
    if zone:
        try:
            zone = str(int(round(float(zone))))
        except ValueError:
            zone = ""

    row = [
        f"{name} {hand}",
        "—",
        "N/A",  # no 8/17 price exported for this game
        zone,
        p("L5 PA/G"),
        p("BBE"),
        p("HR", "0"),
        p("NEAR HR", "0"),
        p("EV"),
        *[p(c) for c in BATTER_HEADER[9:]],
    ]
    return row, prior is not None


def sibling_batter_rows(sibling: str) -> tuple[list[list[str]], list[str]]:
    """Copy today's real batter rows out of the other game of a doubleheader.

    Both games use the same two rosters and batter form is pitcher-independent,
    so these are today's real numbers -- only ODDS is blanked, since the G1
    prices were never exported.
    """
    path = DATA / sibling
    if not path.is_file():
        print(f"  WARN sibling missing: {sibling}")
        return [], BATTER_HEADER
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    hdr_i = next(
        (i for i, l in enumerate(lines) if l.split(",")[0].strip() == "BATTER"), None
    )
    if hdr_i is None:
        print(f"  WARN sibling has no BATTER header: {sibling}")
        return [], BATTER_HEADER
    header = [c.strip() for c in next(csv.reader([lines[hdr_i]]))]
    odds_i = header.index("ODDS") if "ODDS" in header else None
    out: list[list[str]] = []
    for line in lines[hdr_i + 1 :]:
        row = next(csv.reader([line]), None)
        if not row or not row[0].strip():
            continue
        row = list(row) + [""] * (len(header) - len(row))
        if odds_i is not None:
            row[odds_i] = "N/A"
        out.append(row[: len(header)])
    return out, header


def write_game(pitcher: str, zrows, summaries, prior_index) -> str | None:
    spec = GAPS[pitcher]
    matchup, pteam, oteam = spec["matchup"], spec["pteam"], spec["oteam"]
    dst = DATA / f"hr-matchups-{slug(matchup.replace(' @ ', '-at-'))}-{slug(pitcher)}-{DATE}.csv"

    if is_real_export(dst):
        print(f"skip {dst.name} - real PropFinder export present")
        return dst.name

    if spec["lineups"] == "sibling":
        rows, header = sibling_batter_rows(spec["sibling"])
        batter_header = header
        with_form = len(rows)
        batter_rows = rows
    else:
        batter_header = BATTER_HEADER
        batter_rows = []
        with_form = 0
        for z in zrows:
            row, had = batter_row(z, prior_index)
            batter_rows.append(row)
            with_form += int(had)

    lines: list[list[str]] = [
        ["Matchup", matchup],
        ["Pitcher", pitcher],
        ["Pitcher Team", pteam],
        ["Opposing Team", oteam],
        ["Source", SYNTHETIC_MARK],
        [],
        ["", "STATS", "STRIKES", "STATCAST"],
        ["SPLIT"] + PITCHER_BLOCK_COLS,
        *pitcher_block_rows(pitcher, summaries),
        [],
        ["", "", "", "STATS", "STATCAST"],
        batter_header,
        *batter_rows,
    ]

    with dst.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for row in lines:
            w.writerow(row)
    print(f"wrote {dst.name} ({len(batter_rows)} batters, {with_form} with real form)")
    return dst.name


# PropFinder's 8/17 hr-targets-overall export lists only 18 of the slate's 22
# starters. Chase Petty is the one omitted arm with a real, recent row of his own
# (2026-08-07, 204 BF season-to-date), so it is carried forward here rather than
# leaving his four opposing bats with no split. Bello, Pallante and Mathews are
# deliberately NOT filled in -- they keep the honest "data unavailable" lane.
#
# This runs from the same script the importer re-invokes, so the carry survives
# every re-import instead of being wiped by a fresh Downloads copy.
CARRIED_RISK_ROWS: list[dict] = [
    {
        "pitcher": "Chase Petty",
        "time": "1:40 PM",
        "vs": "vs",  # CIN is home in Game 1
        "source": "hr-targets-overall-2026-08-07.csv",
        "cells": ["0.31", "-0.09", "0.55", "1.82", "6.9%", "21.4%", "34.6%", "25.3%", "7.3%", "204"],
    },
]


def carry_pitcher_risk_rows() -> None:
    """Append carried HR-risk rows for arms PropFinder dropped from today's export."""
    path = DATA / f"hr-targets-overall-{DATE}.csv"
    if not path.is_file():
        print(f"  WARN {path.name} missing, cannot carry risk rows")
        return
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    present = {fold(next(csv.reader([l]), [""] * 3)[2]) for l in lines if l.count(",") >= 6}
    last_num = 0
    for l in lines:
        first = l.split(",")[0].strip()
        if first.isdigit():
            last_num = max(last_num, int(first))

    added = []
    for spec in CARRIED_RISK_ROWS:
        if fold(spec["pitcher"]) in present:
            print(f"  {spec['pitcher']} already in {path.name} - no carry needed")
            continue
        last_num += 1
        row = [str(last_num), spec["time"], spec["pitcher"], spec["vs"], *spec["cells"]]
        lines.append(",".join(row))
        added.append(f"{spec['pitcher']} (from {spec['source']})")

    if not added:
        return
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for a in added:
        print("carried risk row:", a)


def update_manifest(names: list[str]) -> None:
    path = DATA / f"manifest-{DATE}.json"
    man = json.loads(path.read_text(encoding="utf-8"))
    files = set(man.get("files") or [])
    added = [n for n in names if n not in files]
    man["files"] = sorted(files | set(names))
    path.write_text(json.dumps(man, indent=2) + "\n", encoding="utf-8")
    for n in added:
        print("manifest +", n)


def main() -> None:
    lineups = load_zone_lineups()
    zone_gaps = [p for p, s in GAPS.items() if s["lineups"] == "zone"]
    missing = [p for p in zone_gaps if p not in lineups]
    if missing:
        print("WARN no zone rows for:", missing)

    summaries = {s: load_summary(s) for s in ("season", "vslhb", "vsrhb")}
    prior_index = build_prior_form_index()
    print(f"prior-form index: {len(prior_index)} batters\n")

    written: list[str] = []
    for pitcher, spec in GAPS.items():
        zrows = lineups.get(pitcher)
        if spec["lineups"] == "zone" and not zrows:
            continue
        name = write_game(pitcher, zrows, summaries, prior_index)
        if name:
            written.append(name)
    update_manifest(written)
    carry_pitcher_risk_rows()


if __name__ == "__main__":
    main()
