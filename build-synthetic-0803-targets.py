#!/usr/bin/env python3
"""Backfill missing 8/3 SP rows into hr-targets-overall (Williams, Wrobleski, Quantrill)."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PATH = ROOT / "data" / "hr-targets-overall-2026-08-03.csv"

# Conservative league-ish fills so gameMeta still shows LHB/RHB; not gloves.
BACKFILL = [
    {
        "time": "6:40 PM",
        "pitcher": "Trevor Williams",
        "vs": "@",
        "overall": 0.20,
        "vs_lhb": 0.10,
        "vs_rhb": 0.30,
        "hr9": 1.40,
        "barrel": 8.0,
        "hr_fb": 14.0,
        "hh": 38.0,
        "fb": 26.0,
        "meatball": 7.0,
        "bf": 200,
    },
    {
        "time": "8:05 PM",
        "pitcher": "Justin Wrobleski",
        "vs": "@",
        "overall": 0.15,
        "vs_lhb": 0.05,
        "vs_rhb": 0.25,
        "hr9": 1.20,
        "barrel": 7.5,
        "hr_fb": 13.0,
        "hh": 36.0,
        "fb": 25.0,
        "meatball": 6.5,
        "bf": 400,
    },
    {
        "time": "8:05 PM",
        "pitcher": "Cal Quantrill",
        "vs": "vs",
        "overall": 0.40,
        "vs_lhb": 0.55,
        "vs_rhb": 0.25,
        "hr9": 1.45,
        "barrel": 8.5,
        "hr_fb": 15.0,
        "hh": 39.0,
        "fb": 27.0,
        "meatball": 7.5,
        "bf": 900,
    },
]


def main() -> None:
    with PATH.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    have = {
        r[2].strip().lower()
        for r in rows
        if len(r) >= 7 and r[0].isdigit() and r[2].strip()
    }
    max_n = max((int(r[0]) for r in rows if r and r[0].isdigit()), default=0)
    added = []
    for spec in BACKFILL:
        if spec["pitcher"].lower() in have:
            continue
        max_n += 1
        added.append(
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
        print("backfill", spec["pitcher"], spec["overall"])
    if not added:
        print("targets already complete")
        return
    with PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerows(rows + added)
    print("wrote", len(added), "rows")


if __name__ == "__main__":
    main()
