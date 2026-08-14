#!/usr/bin/env python3
"""Detail sheet for 8/14 straight / Goblin candidates."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-14"

spec = importlib.util.spec_from_file_location("b0814", ROOT / f"build-sheet-{DATE}.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

from game_row_enrich import enrich_games_list  # noqa: E402
from goblin_hr_zone_fit import annotate_hr_zone_ranks  # noqa: E402

games = enrich_games_list(build.games, DATE)

rows: list[dict] = []
for g in games:
    title = g["title"]
    park = g.get("parkPct")
    lhb = g.get("parkLhbPct")
    rhb = g.get("parkRhbPct")
    for r in g.get("rows", []):
        note = r.get("note", "") or ""
        hand = "R"
        m = re.search(r"\((L|R|S)\)$", r["name"].strip())
        if m:
            hand = m.group(1)
        hp = park
        if hand == "L" and lhb is not None:
            hp = lhb
        elif hand == "R" and rhb is not None:
            hp = rhb
        elif hand == "S" and lhb is not None and rhb is not None:
            hp = max(lhb, rhb)
        hrm = re.search(r"(\d+) HR, (\d+) near-HR, ([\d.]+) mph EV", note)
        split_m = re.search(r"split ([+-][\d.]+)", note)
        risk_m = re.search(r"HR risk ([+-]?\d+(?:\.\d+)?)", note)
        rows.append(
            {
                "name": r["name"].rsplit(" (", 1)[0],
                "hand": hand,
                "game": title.split(" - ")[0],
                "chip": (r.get("chips") or [""])[0].replace("vs ", ""),
                "score": r.get("score"),
                "odds": r.get("odds", ""),
                "emojis": r.get("emojis", ""),
                "hr": int(hrm.group(1)) if hrm else 0,
                "near": int(hrm.group(2)) if hrm else 0,
                "ev": float(hrm.group(3)) if hrm else 0.0,
                "split": float(split_m.group(1)) if split_m else None,
                "risk": float(risk_m.group(1)) if risk_m else None,
                "park": park,
                "hand_park": hp,
                "zone": r.get("zoneScore"),
                "zone_hr": r.get("zoneHr"),
                "zone_brl": r.get("zoneBarrel"),
                "zone_hh": r.get("zoneHardHit"),
                "trend": r.get("formTrend"),
                "blast": r.get("blast"),
                "hh": r.get("hhPct"),
                "fb": r.get("fbPct"),
                "note": note,
            }
        )

annotate_hr_zone_ranks(rows, park_pct_fn=lambda r: r.get("hand_park") or 0)

WATCH = [
    "Owen Caissie",
    "Teoscar Hernandez",
    "Pete Alonso",
    "Jesus Sanchez",
    "Jackson Merrill",
    "Yordan Alvarez",
    "Jac Caglianone",
    "Munetaka Murakami",
    "Cam Smith",
    "Isaac Collins",
    "Coby Mayo",
    "Zack Gelof",
    "Kazuma Okamoto",
    "Salvador Perez",
    "Mookie Betts",
    "Abimelec Ortiz",
    "Lawrence Butler",
    "Eugenio Suarez",
    "Victor Mesa Jr.",
    "Griffin Conine",
    "George Springer",
    "Tyler Stephenson",
    "William Contreras",
    "Nathaniel Lowe",
    "Daylen Lile",
    "Wilyer Abreu",
    "Jonathan Aranda",
    "Junior Caminero",
    "Shohei Ohtani",
    "Matt Olson",
    "Josh Naylor",
    "Hunter Goodman",
    "Bobby Witt Jr.",
    "Rafael Devers",
    "Willy Adames",
    "Julio Rodriguez",
]

by_name = {r["name"]: r for r in rows}
print(f"{'name':22}{'gm':12}{'vs':11}{'H':2} {'odds':>6} {'zone':>5}{'zHR':>6}{'zBRL':>6}{'HH':>5} "
      f"{'spl':>6}{'risk':>6}{'park':>5}{'hp':>4} {'form':>8} {'trend':>8} {'blast':>6}")
for n in WATCH:
    r = by_name.get(n)
    if not r:
        print(f"{n:22}  -- not on sheet --")
        continue
    odds_m = re.search(r"([+-]\d+)", r["odds"] or "")
    odds = odds_m.group(1) if odds_m else "N/A"
    form = f"{r['hr']}HR/{r['near']}nr {r['ev']:.0f}"
    zone = "-" if r["zone"] is None else r["zone"]
    zhr = "-" if r["zone_hr"] is None else r["zone_hr"]
    zbrl = "-" if r["zone_brl"] is None else r["zone_brl"]
    zhh = "-" if r["zone_hh"] is None else r["zone_hh"]
    print(
        f"{r['name']:22}{r['game']:12}{r['chip']:11}{r['hand']:2} "
        f"{odds:>6} {zone:>5}{zhr:>6}{zbrl:>6}{zhh:>5} "
        f"{r['split'] or 0:>+6.2f}{r['risk'] or 0:>+6.2f}"
        f"{r['park']:>+5}{r['hand_park']:>+4} "
        f"{form:>12} {str(r['trend']):>8} {str(r['blast']):>6}"
    )

print("\n--- top by hr_zone_fit (all rows) ---")
for r in sorted(rows, key=lambda x: -(x.get("hr_zone_fit") or 0))[:14]:
    print(
        f"  {r['name']:22}{r['game']:12} fit={r.get('hr_zone_fit'):6.1f} "
        f"atk={r.get('straight_attack_rank') or 0:6.1f} multi={r.get('multi_hr_rank') or 0:6.1f} "
        f"spl={r['split'] if r['split'] is not None else 0:+.2f} risk={r['risk'] if r['risk'] is not None else 0:+.2f} "
        f"hp={r['hand_park']:+d} {r['hr']}HR/{r['near']}nr"
    )
