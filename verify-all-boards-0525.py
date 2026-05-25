#!/usr/bin/env python3
"""Verify every board matches its slate date."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "preview" / "sheets-manifest.json").read_text(encoding="utf-8"))
CURRENT = MANIFEST["sheets"][0]["date"]

STALE_MAY25 = [
    "Juan Soto - Over 0.5 homerun",
    "Aaron Judge - Over 0.5 homerun",
    "Braydon Fisher",
    "ATH @ LAA",
    "Thursday, May 21, 2026",
    "73 listed HR props",
]

EXPECTED = {
    "2026-05-25": {
        "path": ROOT / "preview" / "index.html",
        "header": "Sunday, May 25, 2026",
        "counts": ("53 listed HR props", "13 games", "8 Worst Pickz Favorite"),
        "goblin": "James Wood HR</strong><small>Littell",
        "games": 13,
        "rows": 53,
    },
}


def board_errors(path: Path, date: str) -> list[str]:
    if not path.is_file():
        return [f"missing {path}"]
    t = path.read_text(encoding="utf-8")
    errors = []
    meta = re.search(r'sheet-date" content="([^"]+)"', t)
    if not meta or meta.group(1) != date:
        errors.append(f"sheet-date want {date}, got {meta.group(1) if meta else None}")

    if date == CURRENT:
        spec = EXPECTED[CURRENT]
        if spec["header"] not in t:
            errors.append(f"missing header {spec['header']}")
        for c in spec["counts"]:
            if c not in t:
                errors.append(f"missing count phrase: {c}")
        if spec["goblin"] not in t:
            errors.append("Goblin not updated for May 25")
        g = re.search(r"const games = \[.*?\];", t, re.S)
        if g:
            titles = g.group(0).count("title:")
            rows = len(re.findall(r"name:", g.group(0)))
            if titles != spec["games"]:
                errors.append(f"expected {spec['games']} games, got {titles}")
            if rows != spec["rows"]:
                errors.append(f"expected {spec['rows']} rows, got {rows}")
        for stale in STALE_MAY25:
            if stale in t:
                errors.append(f"stale May 21 bleed: {stale!r}")
    else:
        # archives keep their own header date text
        y, m, d = date.split("-")
        month_names = {
            "01": "January", "02": "February", "03": "March", "04": "April",
            "05": "May", "06": "June", "07": "July", "08": "August",
            "09": "September", "10": "October", "11": "November", "12": "December",
        }
        if f"May {int(d)}, 2026" not in t and month_names.get(m, "") not in t:
            errors.append("archive missing readable date in body")
        if "Goblin's Insight" not in t:
            errors.append("missing Goblin board")
        if "../assets/" not in t and "pikkit" in t.lower():
            errors.append("archive asset paths not relative")
    return errors


def main() -> int:
    errors = []
    for sheet in MANIFEST["sheets"]:
        date = sheet["date"]
        href = sheet["href"]
        path = ROOT / "preview" / href if href != "index.html" else ROOT / "preview" / "index.html"
        for e in board_errors(path, date):
            errors.append(f"{href}: {e}")

    root = ROOT / "index.html"
    if root.is_file():
        for e in board_errors(root, CURRENT):
            errors.append(f"index.html: {e}")

    if errors:
        print("BOARD VERIFY FAILED:")
        for e in errors:
            print(" -", e)
        return 1
    print("BOARD VERIFY OK")
    print(f"  current={CURRENT} archives={len(MANIFEST['sheets']) - 1} root=synced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
