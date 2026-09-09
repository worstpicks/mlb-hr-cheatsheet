#!/usr/bin/env python3
"""Compare parlay picks vs same-game alternatives where form was tiebreaker."""
import importlib.util
import re
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

PARLAY = {
    "Parlay 1": [
        ("Jackson Chourio", "MIL @ COL"),
        ("Jordan Walker", "CIN @ STL"),
        ("James Wood", "WSH @ ARI"),
    ],
    "Parlay 2": [
        ("JJ Bleday", "CIN @ STL"),
        ("Jo Adell", "LAA @ LAD"),
        ("Vinnie Pasquantino", "KC @ MIN"),
    ],
}
picked = {name for legs in PARLAY.values() for name, _ in legs}

rows_by_game = {}
for g in enrich_games_list(b.games, "2026-06-05"):
    gk = game_key_from_title(g["title"])
    if gk in EXCLUDE:
        continue
    w = lookup_weather_for_game(g["title"], weather)
    park = resolve_park_context(g, w)
    park_pct = park["park_pct"] if park["park_pct"] is not None else 0
    game_rows = []
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
        plain = r["name"].rsplit(" (", 1)[0]
        game_rows.append(
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
                emojis=r["emojis"],
                note=note[:120],
            )
        )
    rows_by_game[gk] = game_rows


def form_score(r):
    return r["hr"] * 3 + r["near"] * 1.5


def matchup_score(r):
    return max(r["split"], 0) * 10 + max(r["risk"], 0) * 8 + r["park"] * 0.5


for parlay_name, legs in PARLAY.items():
    print(f"\n{'='*60}\n{parlay_name}\n{'='*60}")
    for pick_name, game in legs:
        pool = rows_by_game.get(game, [])
        pick = next((r for r in pool if r["plain"] == pick_name), None)
        if not pick:
            print(f"  {pick_name}: not found")
            continue
        # Same SP target
        same_sp = [r for r in pool if r["chip"] == pick["chip"] and r["plain"] != pick_name]
        # Similar split lane (within 0.15, same hand bucket rough)
        similar = [
            r
            for r in pool
            if r["plain"] != pick_name
            and r["split"] >= pick["split"] - 0.20
            and abs(r["split"] - pick["split"]) <= 0.35
        ]
        similar.sort(key=lambda x: (-form_score(x), -matchup_score(x), -x["score"]))

        print(f"\n  PICK: {pick_name} vs {pick['chip']} ({game})")
        print(
            f"    form {pick['hr']} HR / {pick['near']} near | split {pick['split']:+.2f} | "
            f"risk {pick['risk']:+.2f} | EV {pick['ev']:.1f} | score {pick['score']} | {pick['emojis']}"
        )

        alts = [r for r in similar if form_score(r) < form_score(pick) or (r["hr"] == 0 and pick["hr"] > 0)]
        alts = sorted(
            {r["plain"]: r for r in (same_sp + similar)}.values(),
            key=lambda x: (-matchup_score(x), -x["ev"], -x["score"]),
        )
        shown = []
        for alt in alts:
            if alt["plain"] in shown or alt["plain"] == pick_name:
                continue
            # flag if matchup similar/better but form worse
            better_match = alt["split"] >= pick["split"] - 0.05 or alt["ev"] > pick["ev"] + 2
            worse_form = form_score(alt) < form_score(pick) - 1 or (alt["hr"] == 0 and pick["hr"] >= 1)
            if better_match and worse_form:
                shown.append(alt["plain"])
                print(f"    OVER instead of: {alt['plain']} vs {alt['chip']}")
                print(
                    f"      form {alt['hr']} HR / {alt['near']} near | split {alt['split']:+.2f} | "
                    f"risk {alt['risk']:+.2f} | EV {alt['ev']:.1f} | score {alt['score']} | {alt['emojis']}"
                )
                if alt["hr"] == 0 and pick["hr"] > 0:
                    print("      >> mainly recent HRs (0 HR vs pick's HR output)")
                elif form_score(alt) < form_score(pick):
                    print(f"      >> mainly recent HRs ({alt['hr']} HR/{alt['near']} near vs {pick['hr']} HR/{pick['near']} near)")
