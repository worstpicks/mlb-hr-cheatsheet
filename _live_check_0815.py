#!/usr/bin/env python3
"""Confirm the live hosts serve the 2026-08-15 sheet.

Netlify (www.worstpickz.win) is the primary site and does not always deploy from
the Git push, so GitHub Pages alone is not proof the update shipped.
"""

from __future__ import annotations

import re
import urllib.request

HOSTS = [
    ("Netlify  (primary)", "https://www.worstpickz.win/"),
    ("GitHub Pages", "https://worstpicks.github.io/mlb-hr-cheatsheet/"),
]

MARKERS = [
    ("slate date meta", r'name="sheet-date" content="2026-08-15"'),
    ("hero date", r"Saturday, August 15, 2026"),
    ("O0.5 straight", r"Jackson Chourio"),
    ("O1.5 straight", r"Christian Encarnacion-Strand"),
    ("bum glove", r"Justin Wrobleski"),
    ("15th game", r"TEX @ ATH"),
]

WRONG_WEEKDAYS = [
    "Monday, August 15",
    "Tuesday, August 15",
    "Wednesday, August 15",
    "Thursday, August 15",
    "Friday, August 15",
    "Sunday, August 15",
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "worstpickz-deploy-check"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def main() -> int:
    bad = 0
    for label, url in HOSTS:
        print(f"=== {label} — {url}")
        try:
            html = fetch(url)
        except Exception as exc:  # noqa: BLE001
            print(f"  FETCH FAILED: {exc}")
            bad += 1
            continue
        for name, pat in MARKERS:
            ok = re.search(pat, html) is not None
            print(f"  {'OK  ' if ok else 'MISS'}  {name}")
            if not ok:
                bad += 1
        wrong = [w for w in WRONG_WEEKDAYS if w in html]
        print(f"  {'OK  ' if not wrong else 'FAIL'}  no wrong weekday{'  ' + str(wrong) if wrong else ''}")
        if wrong:
            bad += 1
        games = len(re.findall(r'title: "', html))
        print(f"  {'OK  ' if games == 15 else 'FAIL'}  15 game blocks (got {games})")
        if games != 15:
            bad += 1
        print()
    print("RESULT:", "BOTH HOSTS SERVING 8/15" if not bad else f"{bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
