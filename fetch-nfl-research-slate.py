#!/usr/bin/env python3
"""Build the NFL Research slate JSON (free data: ESPN schedule + nflverse stats).

Usage:
    python fetch-nfl-research-slate.py --season 2026 --week 1
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
    args = parser.parse_args()

    out_path = write_slate(args.season, args.week)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
