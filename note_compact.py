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
    hand_park = row.get("hand_park_pct")
    hand = (row.get("hand") or "").upper()
    if hand_park is not None and park is not None and abs(hand_park - park) >= 3:
        tag = "LHB" if hand == "L" else "RHB"
        parts.append(f"{tag} park {hand_park:+d}%")
    elif park is not None:
        parts.append(f"park {park:+d}%")
    zone = row.get("zone_score")
    if zone is not None:
        parts.append(f"zone {zone:.1f}")
    return " · ".join(parts)


def straight_pick_why(row: dict, *, leg: str) -> tuple[str, str]:
    """Primary edge + form line for Straights of the Day cards."""
    edge_bits: list[str] = []
    split = row.get("split")
    risk = row.get("risk")
    park = row.get("park_pct")
    chip = row.get("chip", "")
    if split is not None and split >= 0.75:
        edge_bits.append(f"strong platoon split {split:+.2f} vs {chip}")
    elif split is not None and split >= 0:
        edge_bits.append(f"favorable split {split:+.2f} vs {chip}")
    if risk is not None and risk >= 0.50:
        edge_bits.append(f"attackable HR risk {risk:+.2f}")
    park = row.get("park_pct")
    hand_park = row.get("hand_park_pct")
    hand = (row.get("hand") or "").upper()
    if hand_park is not None and park is not None and abs(hand_park - park) >= 3:
        tag = "LHB" if hand == "L" else "RHB"
        if hand_park >= 3:
            edge_bits.append(f"{tag} park +{hand_park}%")
        elif hand_park <= -3:
            edge_bits.append(f"{tag} park {hand_park}%")
    elif hand_park is not None and hand_park >= 6 and (park is None or park < 3):
        tag = "LHB" if hand == "L" else "RHB"
        edge_bits.append(f"{tag} park +{hand_park}%")
    elif park is not None and park >= 3:
        edge_bits.append(f"park/weather +{park}%")
    zone = row.get("zone_score")
    zone_hr = row.get("zone_hr")
    if zone is not None and zone >= 28:
        edge_bits.append(f"elite zone fit {zone:.1f}")
    elif zone is not None and zone >= 22:
        edge_bits.append(f"zone fit {zone:.1f}")
    if zone_hr is not None and zone_hr >= 14.0:
        edge_bits.append(f"zone HR rate {zone_hr:.1f}%")
    primary = (
        ", ".join(edge_bits)
        if edge_bits
        else f"top attack score vs {chip} on today's board"
    )
    form = compact_row_line(row)
    if leg == "o15":
        hr = row.get("hr", 0)
        near = row.get("near", 0)
        form = f"{form} · {hr} HR / {near} near-HR multi-HR profile"
    elif leg == "o05":
        form = f"{form} · best O0.5 straight lane (zone fit + form + split + park)"
    return primary, form


def compact_goblin_leg(row: dict) -> str:
    base = compact_note(row.get("note", ""))
    zone = row.get("zone_score")
    zone_hr = row.get("zone_hr")
    tails: list[str] = []
    if zone is not None and "zone" not in base.lower():
        tails.append(f"zone {zone:.1f}")
    if zone_hr is not None and zone_hr >= 10.0 and "zone hr" not in base.lower():
        tails.append(f"zone HR {zone_hr:.1f}%")
    if tails:
        tail = " · ".join(tails)
        return f"{base} · {tail}" if base else tail
    return base
