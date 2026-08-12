#!/usr/bin/env python3
"""Verify archive picker entries: manifest, files, sheet-date, weekday headers."""
from __future__ import annotations

import json
import re
from datetime import date as dt_date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview"
MANIFEST_PATH = PREVIEW / "sheets-manifest.json"

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
HEADER_PAT = re.compile(
    r"<p>(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), "
    r"(January|February|March|April|May|June|July|August|September|October|November|December) "
    r"(\d+), 2026 — Worst Pickz HR cheat sheet"
)


def expected_weekday(iso: str) -> str:
    y, m, d = (int(x) for x in iso.split("-"))
    return WEEKDAYS[dt_date(y, m, d).weekday()]


def archive_path(href: str) -> Path:
    if href == "index.html":
        return PREVIEW / "index.html"
    if href.startswith("archive/"):
        return PREVIEW / href.replace("/", "\\") if "\\" in str(PREVIEW) else PREVIEW / href
    return PREVIEW / href


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    sheets = manifest.get("sheets", [])
    errors: list[str] = []

    # The current slate moves every day, so read it from the live preview rather than
    # pinning a date here — a hardcoded date turns this check into permanent noise.
    preview_m = re.search(
        r'<meta name="sheet-date" content="([^"]+)">',
        (PREVIEW / "index.html").read_text(encoding="utf-8"),
    )
    expected_current = preview_m.group(1) if preview_m else ""

    listed = {s["date"] for s in sheets}
    on_disk = {p.stem for p in (PREVIEW / "archive").glob("20??-??-??.html")}
    missing = on_disk - listed
    if missing:
        errors.append(f"manifest missing archives on disk: {sorted(missing)}")

    current = [s for s in sheets if "current slate" in s.get("label", "").lower()]
    if len(current) != 1 or current[0]["date"] != expected_current:
        errors.append(f"manifest current slate must be {expected_current}")

    for sheet in sheets:
        iso = sheet.get("date", "")
        href = sheet.get("href", "")
        path = PREVIEW / href if href != "index.html" else PREVIEW / "index.html"
        if not path.is_file():
            errors.append(f"missing file for {iso}: {href}")
            continue
        text = path.read_text(encoding="utf-8")
        meta_m = re.search(r'<meta name="sheet-date" content="([^"]+)">', text)
        meta = meta_m.group(1) if meta_m else ""
        if meta != iso:
            errors.append(f"{path.name}: sheet-date {meta!r} != manifest {iso!r}")

        hm = HEADER_PAT.search(text)
        if not hm:
            errors.append(f"{path.name}: missing intro header paragraph")
            continue
        wd, month, day = hm.group(1), hm.group(2), int(hm.group(3))
        exp = expected_weekday(iso)
        if wd != exp:
            errors.append(f"{path.name}: header says {wd} but {iso} is {exp}")
        month_num = {
            "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
        }[month]
        y, m, d = (int(x) for x in iso.split("-"))
        if m != month_num or d != day:
            errors.append(f"{path.name}: header date {month} {day} != manifest {iso}")

        if href.startswith("archive/") and 'src="../assets/' not in text:
            if 'src="assets/' in text:
                errors.append(f"{path.name}: archive should use ../assets/ paths")

    if errors:
        print("FAIL verify-archives:")
        for e in errors:
            print(f"  {e}")
        return 1

    print("OK verify-archives")
    print(f"  {len(sheets)} sheets in manifest")
    for s in sheets[:6]:
        print(f"  {s['date']} -> {s['href']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
