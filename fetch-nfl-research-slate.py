#!/usr/bin/env python3
"""Build the NFL Research slate JSON (free data: ESPN schedule + nflverse stats).

Usage:
    python fetch-nfl-research-slate.py --season 2026 --week 3
    python fetch-nfl-research-slate.py --season 2026 --week 3 --through 18

A range builds every week in one process: nflreadpy keeps what it downloads in
memory, so weeks after the first reuse the same play-by-play and stats.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from nfl_research.build_slate import write_slate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch NFL Research week slate")
    parser.add_argument("--season", type=int, required=True, help="Schedule season, e.g. 2026")
    parser.add_argument("--week", type=int, required=True, help="Regular-season week 1-18")
    parser.add_argument("--through", type=int, default=None,
                        help="Also build every week after --week up to this one")
    args = parser.parse_args()

    last = args.through or args.week
    failed = []
    for week in range(args.week, last + 1):
        try:
            out_path = write_slate(args.season, week)
            print(f"Wrote {out_path}")
        except Exception as exc:  # one bad week should not cost the rest of the run
            print(f"[nfl-research] week {week} FAILED: {exc}")
            failed.append(week)
    if failed:
        print(f"[nfl-research] failed weeks: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
