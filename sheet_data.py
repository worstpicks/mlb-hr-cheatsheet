#!/usr/bin/env python3
"""Shared helpers: sheet dates, Downloads CSV import, HR-targets parsing."""
from __future__ import annotations

import csv
import json
import re
import shutil
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
PREVIEW_INDEX = ROOT / "preview" / "index.html"
DEFAULT_DOWNLOADS = Path.home() / "Downloads"


def _run_synthetic_matchups(sheet_date: str, dest_dir: Path) -> None:
    """Re-apply slate-specific synthetic matchup CSVs after import stale cleanup."""
    import subprocess
    import sys

    mmdd = sheet_date[5:7] + sheet_date[8:10]
    script = ROOT / f"build-synthetic-{mmdd}-matchups.py"
    if not script.is_file():
        return
    subprocess.run([sys.executable, str(script)], cwd=str(ROOT), check=False)


def normalize_sheet_date(value: str, default_year: int | None = None) -> str:
    """Return ISO date YYYY-MM-DD from common inputs."""
    value = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value
    m = re.fullmatch(r"(\d{1,2})[-/](\d{1,2})(?:[-/](\d{4}))?", value)
    if m:
        month, day, year = int(m.group(1)), int(m.group(2)), m.group(3)
        year = int(year) if year else (default_year or date.today().year)
        return date(year, month, day).isoformat()
    m = re.fullmatch(r"(\d{4})(\d{2})(\d{2})", value)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
    raise ValueError(f"Could not parse sheet date: {value!r}")


def sheet_date_from_preview() -> str | None:
    if not PREVIEW_INDEX.exists():
        return None
    text = PREVIEW_INDEX.read_text(encoding="utf-8")
    m = re.search(r'<meta name="sheet-date" content="(\d{4}-\d{2}-\d{2})">', text)
    return m.group(1) if m else None


def date_match_tokens(iso_date: str) -> list[str]:
    """Substrings that should appear in Downloads CSV filenames for this slate."""
    y, m, d = iso_date.split("-")
    mm, dd = f"{int(m):02d}", f"{int(d):02d}"
    tokens = [
        iso_date,
        f"{y}-{int(m)}-{int(d)}",
        f"{mm}-{dd}",
        f"{int(m)}-{int(d)}",
        f"{y}{mm}{dd}",
    ]
    seen: set[str] = set()
    out: list[str] = []
    for token in tokens:
        if token not in seen:
            seen.add(token)
            out.append(token)
    return out


def find_downloads_csvs(
    sheet_date: str,
    downloads_dir: Path | None = None,
) -> list[Path]:
    """Find .csv files in Downloads whose names contain this slate's date."""
    downloads = downloads_dir or DEFAULT_DOWNLOADS
    if not downloads.is_dir():
        return []
    tokens = date_match_tokens(sheet_date)
    matches: list[Path] = []
    for path in sorted(downloads.glob("*.csv")):
        name_lower = path.name.lower()
        if any(token in name_lower for token in tokens):
            matches.append(path)
    return matches


def import_sheet_csvs(
    sheet_date: str,
    downloads_dir: Path | None = None,
    dest_dir: Path | None = None,
    dry_run: bool = False,
) -> list[Path]:
    """Copy matching Downloads CSVs into project data/ for this slate date."""
    dest = dest_dir or DATA_DIR
    found = find_downloads_csvs(sheet_date, downloads_dir)
    if not dest.exists() and not dry_run:
        dest.mkdir(parents=True, exist_ok=True)

    copied: list[Path] = []
    for src in found:
        target = dest / src.name
        if dry_run:
            copied.append(target)
            continue
        shutil.copy2(src, target)
        copied.append(target)

    # Drop stale matchup/weak-spots exports for this date not in today's Downloads pull.
    if not dry_run and copied:
        keep = {p.name for p in copied}
        for pattern in (f"hr-matchups-*-{sheet_date}.csv", f"pitcher-weak-spots-*-{sheet_date}.csv"):
            for stale in dest.glob(pattern):
                if stale.name not in keep:
                    stale.unlink()
        _run_synthetic_matchups(sheet_date, dest)

    manifest = {
        "sheet_date": sheet_date,
        "imported_at": datetime.now().isoformat(timespec="seconds"),
        "downloads_dir": str(downloads_dir or DEFAULT_DOWNLOADS),
        "files": [p.name for p in copied],
    }
    manifest_name = f"manifest-{sheet_date}.json"
    if not dry_run:
        (dest / manifest_name).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    return copied


def list_data_csvs(sheet_date: str, data_dir: Path | None = None) -> list[Path]:
    data = data_dir or DATA_DIR
    if not data.is_dir():
        return []
    tokens = date_match_tokens(sheet_date)
    out: list[Path] = []
    for path in sorted(data.glob("*.csv")):
        name_lower = path.name.lower()
        if any(token in name_lower for token in tokens):
            out.append(path)
    return out


def hr_targets_csv(sheet_date: str, data_dir: Path | None = None) -> Path | None:
    """Prefer hr-targets-overall-YYYY-MM-DD.csv, else first matching CSV in data/."""
    data = data_dir or DATA_DIR
    preferred = data / f"hr-targets-overall-{sheet_date}.csv"
    if preferred.exists():
        return preferred
    matches = list_data_csvs(sheet_date, data)
    for path in matches:
        if "hr-target" in path.name.lower():
            return path
    return matches[0] if matches else None


def resolve_pitcher(pitcher_map: dict, chip: str):
    key = chip.lower().strip()
    if key in pitcher_map:
        return pitcher_map[key]
    matches = [v for k, v in pitcher_map.items() if key in k or k.endswith(" " + key)]
    if len(matches) == 1:
        return matches[0]
    last = key.split()[-1]
    matches = [v for k, v in pitcher_map.items() if k.endswith(" " + last) or k == last]
    return matches[0] if len(matches) == 1 else None


def _risk_cell(val: str | None, *, default: float = 0.0) -> float | None:
    """Parse PropFinder risk cells; treat blank/'-' as default (thin platoon sample)."""
    raw = (val or "").strip()
    if not raw or raw == "-":
        return default
    try:
        return float(raw)
    except ValueError:
        return None


def load_pitcher_risk(csv_path: Path) -> dict:
    rows: dict = {}
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 7 or row[0] in ("HR Split", "Dates", "Games", "#"):
                continue
            if not row[0].isdigit() or not row[2]:
                continue
            pitcher = row[2].strip()
            if pitcher == "-":
                continue
            # Debut / zero-BF arms often ship overall/splits as "-" — treat as
            # league-average 0.0 so both SPs still appear in game headers.
            overall = _risk_cell(row[4], default=0.0)
            vs_lhb = _risk_cell(row[5], default=0.0)
            vs_rhb = _risk_cell(row[6], default=0.0)
            if overall is None or vs_lhb is None or vs_rhb is None:
                continue
            rows[pitcher.lower()] = {
                "pitcher": pitcher,
                "overall": overall,
                "vs_lhb": vs_lhb,
                "vs_rhb": vs_rhb,
            }
    return rows


def pitcher_risk_pct(score: float) -> int:
    """Map PropFinder HR risk / split score to cheat-sheet % (same sign as park factors).

    Scores are roughly z-scores in [-2, +2]. One point ≈ 50% relative HR vulnerability
    vs league-average for that split (0.49 → +25%, 1.46 → +73%, -0.86 → -43%).
    """
    return round(score * 50)


def format_pitcher_risk_pct(score: float) -> str:
    return f"{pitcher_risk_pct(score):+d}%"
