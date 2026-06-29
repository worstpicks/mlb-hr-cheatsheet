#!/usr/bin/env python3
"""Shared finalize steps after patch-*-preview.py."""
from __future__ import annotations

from research.sync_tab import print_refresh_summary, refresh_research_tab


def sync_research_tab_after_patch(sheet_date: str, *, with_stats: bool = True) -> None:
    """Refresh MLB Research tab JSON whenever the cheat sheet is patched."""
    result = refresh_research_tab(sheet_date, with_stats=with_stats, update_meta=True)
    print_refresh_summary(result)
