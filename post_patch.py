#!/usr/bin/env python3
"""Shared finalize steps after patch-*-preview.py."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from research.sync_tab import print_refresh_summary, refresh_research_tab

ROOT = Path(__file__).resolve().parent


def sync_research_tab_after_patch(sheet_date: str, *, with_stats: bool = True) -> None:
    """Refresh MLB Research tab JSON whenever the cheat sheet is patched."""
    result = refresh_research_tab(sheet_date, with_stats=with_stats, update_meta=True)
    print_refresh_summary(result)
    sync_straights_history_after_patch()


def sync_straights_history_after_patch() -> None:
    """Rebuild Straight-of-the-Day streak / last-7 tracker from archives + MLB API."""
    script = ROOT / "build-straights-history.py"
    if not script.is_file():
        print("WARNING: build-straights-history.py missing; skipping straights tracker sync")
        return
    print("Refreshing Straight-of-the-Day history tracker…")
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        check=False,
    )
    if completed.returncode != 0:
        print(
            f"WARNING: build-straights-history.py exited {completed.returncode}",
            file=sys.stderr,
        )
