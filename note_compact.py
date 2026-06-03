#!/usr/bin/env python3
"""Strip boilerplate from prop notes for the cheat sheet UI."""
from __future__ import annotations

import re

GENERIC_FADE_RE = re.compile(
    r"HR outcomes are still high-variance|"
    r"limited recent HR events|"
    r"lighter EV form \(\d",
    re.I,
)


def compact_note(note: str) -> str:
    """Actionable note text only — no fades, scores, or odds repeated from the row UI."""
    n = (note or "").strip()
    n = re.sub(r"^Worst Pickz Favorite\.\s*", "", n, flags=re.I)
    n = re.sub(r"\s*Model score \d+;\s*odds .*$", "", n, flags=re.I)
    n = re.sub(r"\s*Fade:\s*.+$", "", n, flags=re.I)
    n = n.replace("Tail: ", "").replace("Matchup: ", "· ")
    n = re.sub(r"\s+", " ", n).strip()
    n = re.sub(r"(·\s*)+", "· ", n).strip(" ·")
    return n


def compact_row_line(row: dict) -> str:
    """One-line stat summary for summary cards."""
    parts: list[str] = []
    hr = row.get("hr")
    near = row.get("near")
    ev = row.get("ev")
    if hr is not None and near is not None:
        parts.append(f"{hr} HR, {near} near-HR")
    if ev:
        parts.append(f"{ev:.1f} mph EV")
    if row.get("split") is not None:
        parts.append(f"split {row['split']:+.2f}")
    if row.get("risk") is not None:
        parts.append(f"risk {row['risk']:+.2f}")
    park = row.get("park_pct")
    if park is not None:
        parts.append(f"park {park:+d}%")
    return " · ".join(parts)


def compact_goblin_leg(row: dict) -> str:
    base = compact_note(row.get("note", ""))
    extra = compact_row_line(row)
    if base and extra:
        # Avoid duplicating stats already in compact_note
        if base in extra or extra in base:
            return base
    return base or extra
