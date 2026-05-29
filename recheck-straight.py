#!/usr/bin/env python3
"""Recheck Straight of the Day picks against imported HR-targets CSV + sheet rows."""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

from sheet_data import (
    hr_targets_csv,
    import_sheet_csvs,
    load_pitcher_risk,
    normalize_sheet_date,
    resolve_pitcher,
    sheet_date_from_preview,
)

ROOT = Path(__file__).resolve().parent
HAND_MAP = {"L": "LHB", "R": "RHB", "S": "LHB"}


def batter_hand(name: str) -> str:
    m = re.search(r"\(([LRS])\)", name)
    return m.group(1) if m else "?"


def load_build_module(sheet_date: str):
    path = ROOT / f"build-sheet-{sheet_date}.py"
    if not path.exists():
        print(f"ERROR: missing {path.name}", file=sys.stderr)
        sys.exit(1)
    spec = importlib.util.spec_from_file_location("build_sheet", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Slate date (default: preview meta)")
    parser.add_argument("--import", dest="do_import", action="store_true", help="Import Downloads CSVs first")
    args = parser.parse_args()

    sheet_date = normalize_sheet_date(args.date or sheet_date_from_preview() or "")
    if args.do_import:
        import_sheet_csvs(sheet_date)

    csv_path = hr_targets_csv(sheet_date)
    if not csv_path:
        print(f"ERROR: no HR targets CSV in data/ for {sheet_date}.", file=sys.stderr)
        print("Run: python import-sheet-csvs.py --date", sheet_date, file=sys.stderr)
        return 1

    build = load_build_module(sheet_date)
    risk = load_pitcher_risk(csv_path)
    candidates = []

    for game in build.games:
        for row in game["rows"]:
            name = row["name"]
            chip = row["chips"][0].replace("vs ", "").strip()
            hand = batter_hand(name)
            split_risk, prow = None, None
            p = resolve_pitcher(risk, chip)
            if p:
                col = "vs_lhb" if HAND_MAP.get(hand, "LHB") == "LHB" else "vs_rhb"
                split_risk = p[col]
                prow = p
            note = row["note"]
            hr_m = re.search(r"(\d+) HR", note)
            near_m = re.search(r"(\d+) near-HR", note)
            candidates.append(
                {
                    "name": name,
                    "hand": hand,
                    "score": row["score"],
                    "opp": chip,
                    "split_risk": split_risk,
                    "hr": int(hr_m.group(1)) if hr_m else 0,
                    "near": int(near_m.group(1)) if near_m else 0,
                }
            )

    positive = [c for c in candidates if c["split_risk"] is not None and c["split_risk"] > 0]
    print(f"Sheet date: {sheet_date}")
    print(f"HR CSV:     {csv_path.name}\n")

    print("=== Top platoon-positive props (split HR risk > 0) ===")
    for c in sorted(positive, key=lambda x: (-x["split_risk"], -x["hr"], -x["score"]))[:12]:
        print(
            f"  {c['split_risk']:+.2f}  {c['name']} vs {c['opp']}  "
            f"({c['hr']} HR, {c['near']} near-HR, score {c['score']})"
        )

    print("\n=== Notable negative platoon (avoid for straights) ===")
    for c in sorted(candidates, key=lambda x: -x["hr"]):
        if c["split_risk"] is not None and c["split_risk"] <= 0 and c["hr"] >= 3:
            print(f"  {c['split_risk']:+.2f}  {c['name']} vs {c['opp']}  ({c['hr']} HR, score {c['score']})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
