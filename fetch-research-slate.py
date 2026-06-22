#!/usr/bin/env python3
"""Fetch MLB research slate from Stats API → preview/data/research-YYYY-MM-DD.json."""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path

from research.mlb_api import build_slate
from sheet_data import normalize_sheet_date, sheet_date_from_preview

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "preview" / "data"


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch API research slate JSON (local only).")
    parser.add_argument("--date", help="Slate date YYYY-MM-DD (default: preview meta or today)")
    parser.add_argument("--no-stats", action="store_true", help="Skip per-player season stat calls")
    args = parser.parse_args()

    sheet_date = args.date or sheet_date_from_preview() or date.today().isoformat()
    sheet_date = normalize_sheet_date(sheet_date)

    print(f"Fetching research slate for {sheet_date}…")
    payload = build_slate(sheet_date, with_stats=not args.no_stats)
    payload["fetched_at"] = datetime.now().isoformat(timespec="seconds")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"research-{sheet_date}.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    n_games = len(payload.get("games") or [])
    n_hitters = sum(
        len(g.get("awayLineup") or []) + len(g.get("homeLineup") or [])
        for g in payload.get("games") or []
    )
    print(f"Wrote {out_path} — {n_games} games, {n_hitters} lineup slots")
    print("Local only — not synced to production index.html")


if __name__ == "__main__":
    main()
