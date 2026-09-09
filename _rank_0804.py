#!/usr/bin/env python3
"""Rank 8/4 using the same row shape as patch-0804-preview.py."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from game_row_enrich import contact_risk, enrich_games_list, row_hand_park_fields
from goblin_hr_zone_fit import (
    annotate_hr_zone_ranks,
    hr_rank_sort_key,
    o05_zone_lane_ok,
)
from hr_score_model import batter_split
from sheet_data import load_pitcher_risk, resolve_pitcher

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-04"

spec = importlib.util.spec_from_file_location("b", ROOT / f"build-sheet-{DATE}.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
PITCHER_RISK = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
ENRICHED = enrich_games_list(build.games, DATE)


def parse_odds_value(odds_text: str):
    m = re.search(r"Listed ([+-]\d+)", odds_text)
    return int(m.group(1)) if m else None


def note_hr_count(note: str) -> int:
    m = re.search(r"(\d+)\s+HR", note)
    return int(m.group(1)) if m else 0


def note_near_count(note: str) -> int:
    m = re.search(r"(\d+)\s+near", note, re.I)
    return int(m.group(1)) if m else 0


def note_ev(note: str) -> float:
    m = re.search(r"EV\s+(\d+(?:\.\d+)?)", note)
    return float(m.group(1)) if m else 0.0


def note_barrel(note: str) -> float:
    m = re.search(r"(\d+(?:\.\d+)?)%\s+barrel", note, re.I)
    return float(m.group(1)) if m else 0.0


rows = []
for g in ENRICHED:
    gkey = g.get("key") or g["title"].split(" - ")[0]
    park_pct = g.get("parkPct") or 0
    park_ctx = {
        "park_pct": g.get("parkPct"),
        "park_lhb_pct": g.get("parkLhbPct"),
        "park_rhb_pct": g.get("parkRhbPct"),
    }
    for r in g["rows"]:
        chip = (r.get("chips") or ["vs ?"])[0].replace("vs ", "").strip()
        hand = "L" if "(L)" in r["name"] else ("S" if "(S)" in r["name"] else "R")
        sp = resolve_pitcher(PITCHER_RISK, chip)
        split = batter_split(hand, sp) if sp else 0.0
        risk = sp["overall"] if sp else 0.0
        park_fields = row_hand_park_fields(hand, park_ctx)
        em = "".join(r.get("emojis") or [])
        rows.append(
            {
                "name": r["name"].rsplit(" (", 1)[0],
                "game_key": gkey,
                "chip": chip,
                "hand": hand,
                "split": split,
                "risk": risk,
                "park_pct": park_pct,
                "hr": note_hr_count(r.get("note") or ""),
                "near": note_near_count(r.get("note") or ""),
                "ev": note_ev(r.get("note") or ""),
                "barrel": note_barrel(r.get("note") or ""),
                "score": r.get("score") or 0,
                "zone_score": r.get("zoneScore") or 0,
                "zone_contact": r.get("zoneContact"),
                "zone_barrel": r.get("zoneBarrel"),
                "zone_hr": r.get("zoneHr"),
                "zone_hard_hit": r.get("zoneHardHit"),
                "rank": r.get("score") or 0,
                "fav": "⭐" in em,
                "gem": "💎" in em,
                "odds_value": parse_odds_value(r.get("odds") or ""),
                **park_fields,
            }
        )

annotate_hr_zone_ranks(rows, park_pct_fn=lambda r: int(r.get("hand_park_pct") or r.get("park_pct") or 0))

print("=== TOP O0.5 (zone lane) ===")
o05 = [r for r in rows if o05_zone_lane_ok(r)]
o05.sort(key=hr_rank_sort_key)
for r in o05[:15]:
    mark = ("⭐" if r["fav"] else "") + ("💎" if r["gem"] else "")
    print(
        f"{r['name']:22}{mark:3} vs {r['chip']:20} zfit={r['hr_zone_fit']:5.1f} "
        f"zs={r['zone_score']:4.1f} split={r['split']:+.2f} risk={r['risk']:+.2f} "
        f"park={r['park_pct']:+d} HR={r['hr']}/{r['near']} EV={r['ev']:.1f} {r['game_key']}"
    )

print("\n=== TOP O1.5 (multi) ===")
for r in sorted(rows, key=lambda x: (-x["multi_hr_rank"], -x["hr_zone_fit"]))[:12]:
    mark = ("⭐" if r["fav"] else "") + ("💎" if r["gem"] else "")
    print(
        f"{r['name']:22}{mark:3} vs {r['chip']:20} multi={r['multi_hr_rank']:5.1f} "
        f"zfit={r['hr_zone_fit']:5.1f} split={r['split']:+.2f} risk={r['risk']:+.2f} "
        f"HR={r['hr']}/{r['near']} EV={r['ev']:.1f} {r['game_key']}"
    )

print("\n=== TOP Goblin attack ===")
for r in sorted(rows, key=hr_rank_sort_key)[:15]:
    mark = ("⭐" if r["fav"] else "") + ("💎" if r["gem"] else "")
    print(
        f"{r['name']:22}{mark:3} vs {r['chip']:20} atk={r['straight_attack_rank']:5.1f} "
        f"zfit={r['hr_zone_fit']:5.1f} split={r['split']:+.2f} risk={r['risk']:+.2f} "
        f"park={r['park_pct']:+d} HR={r['hr']}/{r['near']} {r['game_key']}"
    )

print("\n=== FAVORITES by attack ===")
for r in sorted([r for r in rows if r["fav"]], key=hr_rank_sort_key):
    print(
        f"  {r['name']:22} vs {r['chip']:20} atk={r['straight_attack_rank']:5.1f} "
        f"split={r['split']:+.2f} risk={r['risk']:+.2f} park={r['park_pct']:+d} HR={r['hr']}/{r['near']}"
    )
