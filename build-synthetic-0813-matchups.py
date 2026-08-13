#!/usr/bin/env python3
"""Synthesize the three hr-matchups games PropFinder did not export for 2026-08-13.

BOS @ TOR, CHC @ WSH and TEX @ LAA shipped zone, risk and pitcher-summary data but
no hr-matchups CSVs, so without this the sheet would render 6 of 9 games and drop
16 listed props (including Scherzer, the slate's loudest bum).

Everything here is real slate data, reassembled:
  - lineups, handedness and ZONE come from zone-matchups-2026-08-13.csv
  - the pitcher Season/vsLHB/vsRHB block comes from the pitcher-summary exports
  - batter recent-form (HR, near-HR, EV, barrel, batted-ball) is carried from each
    hitter's most recent PropFinder matchup export, since form is pitcher-independent

ODDS are deliberately left N/A: no 8/13 price was exported for these games, and the
opposing starter differs from the carried day, so a stale number would be wrong.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-08-13"

# pitcher -> (matchup, pitcher team, opposing/batter team)
GAPS: dict[str, tuple[str, str, str]] = {
    "Payton Tolle": ("BOS @ TOR", "BOS", "TOR"),
    "Max Scherzer": ("BOS @ TOR", "TOR", "BOS"),
    "Kevin Gausman": ("CHC @ WSH", "CHC", "WSH"),
    "Cade Cavalli": ("CHC @ WSH", "WSH", "CHC"),
    "Jacob deGrom": ("TEX @ LAA", "TEX", "LAA"),
    "Walbert Urena": ("TEX @ LAA", "LAA", "TEX"),
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
    return n.lower().replace(".", "").replace("'", "").replace("\u2019", "")


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


def pitcher_block_rows(pitcher: str, summaries: dict[str, dict[str, dict]]) -> list[list[str]]:
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
        "N/A",  # no 8/13 price exported for this game
        zone,
        p("L5 PA/G"),
        p("BBE"),
        p("HR", "0"),
        p("NEAR HR", "0"),
        p("EV"),
        *[p(c) for c in BATTER_HEADER[9:]],
    ]
    return row, prior is not None


def write_game(pitcher: str, zrows: list[dict], summaries, prior_index) -> str | None:
    matchup, pteam, oteam = GAPS[pitcher]
    dst = DATA / f"hr-matchups-{slug(matchup.replace(' @ ', '-at-'))}-{slug(pitcher)}-{DATE}.csv"

    if is_real_export(dst):
        print(f"skip {dst.name} — real PropFinder export present")
        return dst.name

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
        BATTER_HEADER,
    ]

    with_form = 0
    for z in zrows:
        row, had = batter_row(z, prior_index)
        lines.append(row)
        with_form += int(had)

    with dst.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for row in lines:
            w.writerow(row)
    print(f"wrote {dst.name} ({len(zrows)} batters, {with_form} with carried form)")
    return dst.name


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
    missing = [p for p in GAPS if p not in lineups]
    if missing:
        print("WARN no zone rows for:", missing)

    summaries = {s: load_summary(s) for s in ("season", "vslhb", "vsrhb")}
    prior_index = build_prior_form_index()
    print(f"prior-form index: {len(prior_index)} batters\n")

    written: list[str] = []
    for pitcher in GAPS:
        zrows = lineups.get(pitcher)
        if not zrows:
            continue
        name = write_game(pitcher, zrows, summaries, prior_index)
        if name:
            written.append(name)
    update_manifest(written)


if __name__ == "__main__":
    main()
