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
            try:
                overall = float(row[4])
                vs_lhb = float(row[5])
                vs_rhb = float(row[6])
            except ValueError:
                continue
            rows[pitcher.lower()] = {
                "pitcher": pitcher,
                "overall": overall,
                "vs_lhb": vs_lhb,
                "vs_rhb": vs_rhb,
            }
    return rows
