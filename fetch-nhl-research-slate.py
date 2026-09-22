#!/usr/bin/env python3
"""Build the NHL Research slate JSON (free data: NHL's own public API).

Usage:
    python fetch-nhl-research-slate.py --date 2026-09-29
    python fetch-nhl-research-slate.py --date today
"""
from __future__ import annotations

import argparse
import sys
from datetime import date as _date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from nhl_research.build_slate import write_slate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch NHL Research day slate")
    parser.add_argument("--date", required=True,
                        help='Slate date, "2026-09-29" or "today"')
    args = parser.parse_args()
    day = _date.today().isoformat() if args.date == "today" else args.date

    out_path = write_slate(day)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
