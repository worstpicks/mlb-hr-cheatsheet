#!/usr/bin/env python3
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
bs = importlib.util.spec_from_file_location("build", ROOT / "build-sheet-2026-06-05.py")
build = importlib.util.module_from_spec(bs)
bs.loader.exec_module(build)
from sheet_data import load_pitcher_risk, resolve_pitcher
from game_row_enrich import (
    enrich_games_list,
    game_key_from_title,
    load_weather_lookup,
    lookup_weather_for_game,
    resolve_park_context,
)

SHEET_DATE = "2026-06-05"
ENRICHED = enrich_games_list(build.games, SHEET_DATE)
PITCHER_RISK = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{SHEET_DATE}.csv")
weather_lookup = load_weather_lookup(SHEET_DATE)
rows = []
for g in ENRICHED:
    game_key = game_key_from_title(g["title"])
    weather = lookup_weather_for_game(g["title"], weather_lookup)
    park_ctx = resolve_park_context(g, weather)
    park_pct = park_ctx["park_pct"] if park_ctx["park_pct"] is not None else 0
    for r in g["rows"]:
        chip = r["chips"][0].replace("vs ", "")
        hand = r["name"].split("(")[-1].rstrip(")")
        risk_row = resolve_pitcher(PITCHER_RISK, chip)
        split = (risk_row["vs_lhb"] if hand == "L" else risk_row["vs_rhb"]) if risk_row else 0.0
        risk = risk_row["overall"] if risk_row else 0.0
        note = r["note"]
        hr = int(m.group(1)) if (m := re.search(r"(\d+)\s+HR", note)) else 0
        near = int(m.group(1)) if (m := re.search(r"(\d+)\s+near-HR", note)) else 0
        ev = float(m.group(1)) if (m := re.search(r"(\d+(?:\.\d+)?)\s+mph EV", note)) else 0.0
        sar = (
            r["score"] * 0.25
            + max(risk, 0) * 12
            + max(split, 0) * 10
            + park_pct * 0.65
            + hr * 3
            + near * 1.4
            + max(ev - 90, 0) * 0.45
        )
        rows.append(
            dict(
                name=r["name"],
                plain=r["name"].rsplit(" (", 1)[0],
                chip=chip,
                game=game_key,
                score=r["score"],
                hr=hr,
                near=near,
                ev=ev,
                split=split,
                risk=risk,
                park=park_pct,
                sar=sar,
            )
        )

rows.sort(key=lambda x: x["sar"], reverse=True)
print("TOP 15 O0.5 attack rank:")
for x in rows[:15]:
    print(
        f"  {x['plain']:28} vs {x['chip']:8} {x['game']:12} "
        f"sc={x['score']} hr={x['hr']} near={x['near']} ev={x['ev']:.1f} "
        f"split={x['split']:+.2f} risk={x['risk']:+.2f} park={x['park']:+d}%"
    )

strict = [
    x
    for x in rows
    if x["score"] >= 72
    and x["split"] >= 0
    and (x["risk"] >= 0.5 or x["park"] >= 3 or x["split"] >= 0.75)
    and (x["hr"] >= 1 or x["near"] >= 2 or x["ev"] >= 94)
]
strict.sort(key=lambda x: x["sar"], reverse=True)
print("\nStrict pool top 10:")
for x in strict[:10]:
    print(f"  {x['plain']:28} {x['game']} hr={x['hr']} near={x['near']} ev={x['ev']:.1f}")

form_strict = [
    x
    for x in rows
    if x["score"] >= 72
    and x["split"] >= 0
    and (x["risk"] >= 0.5 or x["park"] >= 3 or x["split"] >= 0.75)
    and (x["hr"] >= 1 or x["near"] >= 3)
]
form_strict.sort(key=lambda x: x["sar"], reverse=True)
print("\nForm-strict pool (hr>=1 or near>=3) top 10:")
for x in form_strict[:10]:
    print(f"  {x['plain']:28} {x['game']} hr={x['hr']} near={x['near']} ev={x['ev']:.1f}")

o15 = [x for x in rows if x["hr"] >= 2 and x["near"] >= 2 and x["score"] >= 78 and x["split"] >= 0]
o15.sort(
    key=lambda x: x["hr"] * 5
    + x["near"] * 2
    + max(x["ev"] - 90, 0) * 0.8
    + x["score"] * 0.25
    + x["split"] * 8
    + x["risk"] * 5
    + x["park"] * 0.4,
    reverse=True,
)
print("\nTOP O1.5:")
for x in o15[:8]:
    print(
        f"  {x['plain']:28} vs {x['chip']} {x['game']} "
        f"hr={x['hr']} near={x['near']} sc={x['score']}"
    )
