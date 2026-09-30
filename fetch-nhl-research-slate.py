#!/usr/bin/env python3
"""Build the NHL Research slate JSON (free data: NHL's own public API).

Usage:
    python fetch-nhl-research-slate.py --date today
    python fetch-nhl-research-slate.py --date 2026-10-04 --days 2 --prune 7

--days builds that date and the ones after it. The scheduled build uses 2, so
tomorrow's slate is already posted when the date rolls over at midnight and a
single failed run never leaves the page empty.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date as _date
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from nhl_research.build_slate import prune, write_manifest, write_slate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch NHL Research day slates")
    parser.add_argument("--date", required=True,
                        help='First slate date, "2026-09-29" or "today"')
    parser.add_argument("--days", type=int, default=1,
                        help="How many consecutive days to build, starting at --date")
    parser.add_argument("--prune", type=int, default=0, metavar="N",
                        help="Delete slates more than N days older than --date (0 keeps all)")
    args = parser.parse_args()
    first = _date.today() if args.date == "today" else _date.fromisoformat(args.date)

    failed = []
    for offset in range(max(1, args.days)):
        day = (first + timedelta(days=offset)).isoformat()
        try:
            path, changed = write_slate(day)
            print(f"{'Wrote' if changed else 'Unchanged'} {path}")
        except Exception as exc:                      # one bad day must not stop the rest
            failed.append(day)
            print(f"[nhl-research] ERROR {day}: {type(exc).__name__}: {exc}")

    if args.prune > 0:
        gone = prune(first.isoformat(), args.prune)
        if gone:
            print(f"Pruned {len(gone)} old slate(s): {', '.join(gone)}")
    dates = write_manifest()
    print(f"Manifest: {len(dates)} slate(s) posted, {dates[0] if dates else '-'} to "
          f"{dates[-1] if dates else '-'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
