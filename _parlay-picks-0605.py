#!/usr/bin/env python3
import importlib.util
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("b", ROOT / "build-sheet-2026-06-05.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
from sheet_data import load_pitcher_risk, resolve_pitcher
from game_row_enrich import enrich_games_list, game_key_from_title, load_weather_lookup, lookup_weather_for_game, resolve_park_context

EXCLUDE = {"SF @ CHC", "CWS @ PHI", "SEA @ DET"}
PITCHER_RISK = load_pitcher_risk(ROOT / "data/hr-targets-overall-2026-06-05.csv")
weather = load_weather_lookup("2026-06-05")
rows = []
for g in enrich_games_list(b.games, "2026-06-05"):
    gk = game_key_from_title(g["title"])
    if gk in EXCLUDE:
        continue
    w = lookup_weather_for_game(g["title"], weather)
    park = resolve_park_context(g, w)
    park_pct = park["park_pct"] if park["park_pct"] is not None else 0
    for r in g["rows"]:
        chip = r["chips"][0].replace("vs ", "")
        hand = r["name"].split("(")[-1].rstrip(")")
        pr = resolve_pitcher(PITCHER_RISK, chip)
        split = (pr["vs_lhb"] if hand == "L" else pr["vs_rhb"]) if pr else 0.0
        risk = pr["overall"] if pr else 0.0
        note = r["note"]
        hr = int(m.group(1)) if (m := re.search(r"(\d+)\s+HR", note)) else 0
        near = int(m.group(1)) if (m := re.search(r"(\d+)\s+near-HR", note)) else 0
        ev = float(m.group(1)) if (m := re.search(r"(\d+(?:\.\d+)?)\s+mph EV", note)) else 0.0
        rank = (
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
                plain=r["name"].rsplit(" (", 1)[0],
                game=gk,
                chip=chip,
                score=r["score"],
                hr=hr,
                near=near,
                ev=ev,
                split=split,
                risk=risk,
                park=park_pct,
                odds=r["odds"],
                rank=rank,
                fav="⭐" in r["emojis"],
                moon="🌕" in r["emojis"],
            )
        )

eligible = [r for r in rows if r["split"] >= 0 and (r["hr"] >= 1 or r["near"] >= 2)]
eligible.sort(key=lambda x: x["rank"], reverse=True)

print("TOP 20 (excluded SF@CHC, CWS@PHI, SEA@DET):")
for x in eligible[:20]:
    print(
        f"  {x['plain']:22} {x['game']:12} vs {x['chip']:10} "
        f"sc={x['score']} hr={x['hr']} near={x['near']} split={x['split']:+.2f} "
        f"risk={x['risk']:+.2f} park={x['park']:+d}% odds={x['odds']}"
    )

print("\nBest per remaining game:")
by_game = defaultdict(list)
for x in eligible:
    by_game[x["game"]].append(x)
for gk in sorted(by_game):
    top = by_game[gk][:2]
    print(gk + ": " + ", ".join(f"{t['plain']}({t['split']:+.2f}/{t['risk']:+.2f})" for t in top))
