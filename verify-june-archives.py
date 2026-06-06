#!/usr/bin/env python3
"""Quick check: June 1/4/5/6 archives + manifest picker entries."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date as dt_date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

EXPECTED = {
    "2026-06-06": ("Saturday", "index.html", 87),
    "2026-06-05": ("Friday", "archive/2026-06-05.html", 93),
    "2026-06-04": ("Thursday", "archive/2026-06-04.html", 58),
    "2026-06-01": ("Monday", "archive/2026-06-01.html", 60),
}


def main() -> int:
    manifest = json.loads((PREVIEW / "sheets-manifest.json").read_text(encoding="utf-8"))
    by_date = {s["date"]: s for s in manifest["sheets"]}
    errors: list[str] = []

    for iso, (wd, href, props) in EXPECTED.items():
        if iso not in by_date:
            errors.append(f"manifest missing {iso}")
            continue
        if by_date[iso]["href"] != href:
            errors.append(f"{iso}: manifest href {by_date[iso]['href']!r} != {href!r}")
        path = PREVIEW / href if href != "index.html" else PREVIEW / "index.html"
        if not path.is_file():
            errors.append(f"{iso}: missing {path}")
            continue
        text = path.read_text(encoding="utf-8")
        meta = re.search(r'sheet-date" content="([^"]+)"', text)
        if not meta or meta.group(1) != iso:
            errors.append(f"{iso}: sheet-date {meta.group(1) if meta else None}")
        hdr = re.search(
            r"<p>(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), "
            r"(\w+) (\d+), 2026 — Worst Pickz HR cheat sheet",
            text,
        )
        if not hdr:
            errors.append(f"{iso}: missing header")
        else:
            got_wd = hdr.group(1)
            exp_wd = WEEKDAYS[dt_date(*map(int, iso.split("-"))).weekday()]
            if got_wd != exp_wd:
                errors.append(f"{iso}: weekday {got_wd} != {exp_wd}")
        if f"<strong>{props} listed HR props</strong>" not in text:
            errors.append(f"{iso}: expected {props} props in summary")
        if href.startswith("archive/") and "../assets/" not in text:
            errors.append(f"{iso}: archive missing ../assets/ paths")

    if errors:
        print("FAIL verify-june-archives:")
        for e in errors:
            print(f"  {e}")
        return 1

    print("OK verify-june-archives (June 1, 4, 5, 6)")
    for iso in EXPECTED:
        print(f"  {iso} -> {EXPECTED[iso][1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
