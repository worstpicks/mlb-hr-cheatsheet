#!/usr/bin/env python3
"""Fetch MLB research slate from Stats API → preview/data/research-YYYY-MM-DD.json."""
from __future__ import annotations

import argparse
from datetime import date

from research.sync_tab import print_refresh_summary, refresh_research_tab
from sheet_data import normalize_sheet_date, sheet_date_from_preview


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch API research slate JSON (local only).")
    parser.add_argument("--date", help="Slate date YYYY-MM-DD (default: preview meta or today)")
    parser.add_argument("--no-stats", action="store_true", help="Skip per-player season stat calls")
    args = parser.parse_args()

    sheet_date = args.date or sheet_date_from_preview() or date.today().isoformat()
    sheet_date = normalize_sheet_date(sheet_date)

    print(f"Fetching research slate for {sheet_date}…")
    result = refresh_research_tab(sheet_date, with_stats=not args.no_stats, update_meta=True)
    print_refresh_summary(result)
    print("Local only — not synced to production index.html")


if __name__ == "__main__":
    main()
