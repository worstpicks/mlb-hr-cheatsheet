#!/usr/bin/env python3
"""Starters the owner supplied that no feed carries yet, keyed per game.

MLB publishes one probable per team per day, and on a doubleheader that leaves the
second game TBD for hours. The projected-pitcher fallback is keyed by TEAM, so it
happily filled BOTH halves with the same arm -- on 2026-09-23 Baltimore's Trey Gibson
appeared as the starter of game one and game two at once, which no pitcher does.

Entries here are per game and win over any feed, because they come from the owner
reading the posted lineup card. Keys use the same "(G1)"/"(G2)" numbering the rest of
the code uses, numbered by start time. A value of None leaves that side alone.
"""
from __future__ import annotations

MANUAL_PROBABLES: dict[str, dict[str, tuple[str | None, str | None]]] = {
    "2026-09-23": {
        # Rain postponed 9/22 in Baltimore; it was made up as game one today, so the
        # second game needed its own pair. Owner's card: CJ Van Eyk and Trey Gibson.
        "TOR @ BAL (G1)": ("Max Scherzer", "Chris Bassitt"),
        "TOR @ BAL (G2)": ("CJ Van Eyk", "Trey Gibson"),
    },
}


def manual_starters(sheet_date: str) -> dict[str, tuple[str | None, str | None]]:
    return MANUAL_PROBABLES.get(sheet_date, {})
