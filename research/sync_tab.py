#!/usr/bin/env python3
"""Refresh MLB Research tab JSON + park factors for a slate date."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from research.mlb_api import build_slate
from research.park_factors import write_park_factors_json
from sheet_data import normalize_sheet_date

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "preview" / "data"
RESEARCH_INDEX = ROOT / "preview" / "research" / "index.html"


def update_research_date_meta(_sheet_date: str = "") -> bool:
    """Clear preview/research/index.html meta research-date (UI defaults to today)."""
    if not RESEARCH_INDEX.is_file():
        return False
    text = RESEARCH_INDEX.read_text(encoding="utf-8")
    new_text = re.sub(
        r'(<meta name="research-date" content=")[^"]*(")',
        r'\g<1>\2',
        text,
        count=1,
    )
    if new_text == text:
        return False
    RESEARCH_INDEX.write_text(new_text, encoding="utf-8")
    return True


def refresh_research_tab(
    sheet_date: str,
    *,
    with_stats: bool = True,
    update_meta: bool = True,
) -> dict[str, Path | str | None]:
    """Build and write research + park-factors JSON for a slate date."""
    sheet_date = normalize_sheet_date(sheet_date)
    payload = build_slate(sheet_date, with_stats=with_stats)
    payload["fetched_at"] = datetime.now().isoformat(timespec="seconds")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    research_path = OUT_DIR / f"research-{sheet_date}.json"
    research_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    pf_path = write_park_factors_json(OUT_DIR, sheet_date)

    if update_meta:
        update_research_date_meta(sheet_date)

    return {
        "sheet_date": sheet_date,
        "research": research_path,
        "park_factors": pf_path,
    }


def print_refresh_summary(result: dict[str, Path | str | None]) -> None:
    sheet_date = result.get("sheet_date")
    research = result.get("research")
    pf = result.get("park_factors")
    print(f"Research tab refreshed for {sheet_date}")
    if isinstance(research, Path):
        n_games = 0
        n_hitters = 0
        try:
            data = json.loads(research.read_text(encoding="utf-8"))
            n_games = len(data.get("games") or [])
            n_hitters = sum(
                len(g.get("awayLineup") or []) + len(g.get("homeLineup") or [])
                for g in data.get("games") or []
            )
        except (json.JSONDecodeError, OSError):
            pass
        print(f"  {research.relative_to(ROOT)} — {n_games} games, {n_hitters} lineup slots")
    if isinstance(pf, Path):
        print(f"  {pf.relative_to(ROOT)}")
    elif pf is None:
        print("  park-factors: stadium fallback or unavailable (import Ballpark Pal CSV)")
