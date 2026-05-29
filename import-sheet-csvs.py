#!/usr/bin/env python3
"""Import slate-day CSV exports from Downloads into data/.

Examples:
  python import-sheet-csvs.py --date 2026-05-29
  python import-sheet-csvs.py --date 05-29
  python import-sheet-csvs.py                    # uses preview meta sheet-date
  python import-sheet-csvs.py --date 05-29 --dry-run
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sheet_data import (
    DATA_DIR,
    DEFAULT_DOWNLOADS,
    find_downloads_csvs,
    import_sheet_csvs,
    list_data_csvs,
    normalize_sheet_date,
    sheet_date_from_preview,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Import Downloads CSVs for an MLB HR cheat sheet date.")
    parser.add_argument(
        "--date",
        help="Slate date: YYYY-MM-DD, MM-DD, or M-D (default: preview meta sheet-date)",
    )
    parser.add_argument(
        "--downloads",
        type=Path,
        default=DEFAULT_DOWNLOADS,
        help=f"Downloads folder (default: {DEFAULT_DOWNLOADS})",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=DATA_DIR,
        help=f"Project data folder (default: {DATA_DIR})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show matches without copying")
    args = parser.parse_args()

    raw_date = args.date or sheet_date_from_preview()
    if not raw_date:
        print("ERROR: pass --date YYYY-MM-DD or set preview meta sheet-date first.", file=sys.stderr)
        return 1

    sheet_date = normalize_sheet_date(raw_date)
    found = find_downloads_csvs(sheet_date, args.downloads)

    print(f"Sheet date: {sheet_date}")
    print(f"Downloads:  {args.downloads}")
    print(f"Dest:       {args.dest}")

    if not found:
        print("\nNo matching CSV files in Downloads.")
        print("Expected filename to include the slate date, e.g.:")
        print(f"  hr-targets-overall-{sheet_date}.csv")
        existing = list_data_csvs(sheet_date, args.dest)
        if existing:
            print("\nAlready in data/:")
            for path in existing:
                print(f"  {path.name}")
            return 0
        return 1

    print(f"\nFound {len(found)} file(s) in Downloads:")
    for path in found:
        print(f"  {path.name}")

    copied = import_sheet_csvs(
        sheet_date,
        downloads_dir=args.downloads,
        dest_dir=args.dest,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print("\nDry run — would copy to data/:")
        for path in copied:
            print(f"  {path.name}")
    else:
        print(f"\nCopied {len(copied)} file(s) to {args.dest}:")
        for path in copied:
            print(f"  {path.name}")
        print(f"Wrote manifest-{sheet_date}.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
