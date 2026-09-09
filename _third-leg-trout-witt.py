#!/usr/bin/env python3
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("b", ROOT / "build-sheet-2026-06-05.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
from sheet_data import load_pitcher_risk, resolve_pitcher
from game_row_enrich import enrich_games_list, game_key_from_title, load_weather_lookup, lookup_weather_for_game, resolve_park_context

EXCLUDE_GAMES = {"SF @ CHC", "CWS @ PHI", "SEA @ DET"}
LOCKED = {"Mike Trout", "Bobby Witt Jr."}
SKIP_GAMES = {"LAA @ LAD", "KC @ MIN"}
prisk = load_pitcher_risk(ROOT / "data/hr-targets-overall-2026-06-05.csv")
weather = load_weather_lookup("2026-06-05")
rows = []
for g in enrich_games_list(b.games, "2026-06-05"):
    gk = game_key_from_title(g["title"])
    if gk in EXCLUDE_GAMES:
        continue
    w = lookup_weather_for_game(g["title"], weather)
    park = resolve_park_context(g, w)
    park_pct = park["park_pct"] if park["park_pct"] is not None else 0
    for r in g["rows"]:
        plain = r["name"].rsplit(" (", 1)[0]
        if plain in LOCKED:
            continue
        chip = r["chips"][0].replace("vs ", "")
        hand = r["name"].split("(")[-1].rstrip(")")
        pr = resolve_pitcher(prisk, chip)
        split = (pr["vs_lhb"] if hand == "L" else pr["vs_rhb"]) if pr else 0.0
        risk = pr["overall"] if pr else 0.0
        note = r["note"]
        hr = int(m.group(1)) if (m := re.search(r"(\d+)\s+HR", note)) else 0
        near = int(m.group(1)) if (m := re.search(r"(\d+)\s+near-HR", note)) else 0
        ev = float(m.group(1)) if (m := re.search(r"(\d+(?:\.\d+)?)\s+mph EV", note)) else 0.0
        fav = "⭐" in r["emojis"]
        moon = "🌕" in r["emojis"]
        attack = (
            r["score"] * 0.25
            + max(risk, 0) * 12
            + max(split, 0) * 10
            + park_pct * 0.65
            + hr * 3
            + near * 1.4
            + max(ev - 90, 0) * 0.45
        )
        talent = ev * 0.6 + r["score"] * 0.3 + max(split, 0) * 8 + (10 if fav else 0) + (5 if moon else 0)
        rows.append(
            dict(
                plain=plain,
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
                fav=fav,
                moon=moon,
                attack=attack,
                talent=talent,
                new_game=gk not in SKIP_GAMES,
            )
        )

new = [x for x in rows if x["new_game"] and x["split"] >= 0 and (x["hr"] >= 1 or x["near"] >= 2)]
new.sort(key=lambda x: x["attack"], reverse=True)
print("TOP 8 third legs (new game, positive split, HR form):")
for x in new[:8]:
    print(
        f"  {x['plain']:20} {x['game']:11} vs {x['chip']:8} "
        f"hr={x['hr']} near={x['near']} ev={x['ev']:.1f} split={x['split']:+.2f} "
        f"risk={x['risk']:+.2f} park={x['park']:+d}% fav={x['fav']} moon={x['moon']}"
    )

print()
talent_rows = [x for x in rows if x["new_game"] and x["split"] >= 0 and x["fav"]]
talent_rows.sort(key=lambda x: x["talent"], reverse=True)
print("TOP 5 talent/favorite style (new game):")
for x in talent_rows[:5]:
    print(
        f"  {x['plain']:20} {x['game']:11} hr={x['hr']} near={x['near']} ev={x['ev']:.1f} "
        f"split={x['split']:+.2f} risk={x['risk']:+.2f} park={x['park']:+d}% moon={x['moon']}"
    )

print()
bum = [x for x in rows if x["new_game"] and x["split"] >= 0 and x["risk"] >= 1.0]
bum.sort(key=lambda x: x["attack"], reverse=True)
print("TOP bum-target legs (HR risk >= 1.0, new game):")
for x in bum[:5]:
    print(f"  {x['plain']:20} {x['game']:11} vs {x['chip']:8} hr={x['hr']} split={x['split']:+.2f} risk={x['risk']:+.2f} park={x['park']:+d}%")
