#!/usr/bin/env python3
"""Does the SELECTION POLICY cost the lotto more than the formula does?

Key idea being tested: the rubric caps legs at 2 per game to 'spread the ticket'.
That is portfolio thinking, and a parlay is not a portfolio -- every leg must hit,
so there is no diversification benefit. Worse, same-game legs are POSITIVELY
correlated (one good offensive night lifts several), which helps an all-must-hit
ticket. So the cap may be forcing worse legs onto the card for no gain.
"""
from __future__ import annotations
import json, re, unicodedata
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location("sweep", Path(__file__).parent/"_hits_variant_sweep.py")
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)

ROOT = Path(__file__).resolve().parent
cache = json.loads(S.CACHE.read_text(encoding="utf-8"))

POLICIES = {
    "P0 caps 2/game (current)": dict(cap=2, slot_max=9, min_pa=0),
    "P1 no caps":               dict(cap=99, slot_max=9, min_pa=0),
    "P2 cap 3/game":            dict(cap=3, slot_max=9, min_pa=0),
    "P3 no caps, slots 1-6":    dict(cap=99, slot_max=6, min_pa=0),
    "P4 no caps, slots 1-5":    dict(cap=99, slot_max=5, min_pa=0),
    "P5 no caps, slots 1-4":    dict(cap=99, slot_max=4, min_pa=0),
    "P6 no caps, min 150 PA":   dict(cap=99, slot_max=9, min_pa=150),
    "P7 no caps, 1-5, 150 PA":  dict(cap=99, slot_max=5, min_pa=150),
}
tot = {k: [0, 0, 0] for k in POLICIES}   # hits, legs, full-ticket cashes
tickets = {k: 0 for k in POLICIES}

for path in sorted((ROOT/"preview"/"archive").glob("2026-*.html")):
    date = path.stem
    rj = ROOT/"preview"/"data"/f"research-{date}.json"
    if date not in cache or not rj.is_file() or not cache[date]:
        continue
    res = cache[date]; data = json.loads(rj.read_text(encoding="utf-8"))
    bd = S.board(path); lanes = S.sp_lanes(date)
    p1bs = S.park_col(date, "1B %"); runs = S.park_col(date, "Runs %")
    sv_all = data.get("savant_lookup") or {}

    pool = []
    for g in data.get("games") or []:
        mk = g.get("matchup", "")
        for side, opp in (("awayLineup","homePitcher"), ("homeLineup","awayPitcher")):
            sp = g.get(opp) or {}; lane = lanes.get(S.fold(sp.get("name","")), {})
            for pl in g.get(side) or []:
                o = pl.get("order")
                if not o or o > 9: continue
                k = S.fold(pl.get("name",""))
                if k not in bd or k not in res: continue
                hand = pl.get("hand") or "R"
                st = pl.get("stats") or {}; sv = sv_all.get(str(pl.get("id"))) or {}
                v = S.variants(o, st, sv, lane.get("L" if hand=="L" else "R"),
                               p1bs.get(mk), runs.get(mk), hand)["V3 +platoon xwOBA"]
                p = max(.08, min(.32, v))
                prob = 1 - (1-p) ** S.SLOT_PA.get(o, 3.9)
                pool.append({"p": prob, "k": k, "game": mk, "slot": o,
                             "pa": sv.get("pa") or st.get("pa") or 0})
    if len(pool) < 11: continue
    pool.sort(key=lambda r: -r["p"])

    for name, cfg in POLICIES.items():
        legs = []; seen = set(); per_game = {}
        for r in pool:
            if r["k"] in seen: continue
            if r["slot"] > cfg["slot_max"]: continue
            if r["pa"] < cfg["min_pa"]: continue
            if per_game.get(r["game"], 0) >= cfg["cap"]: continue
            seen.add(r["k"]); per_game[r["game"]] = per_game.get(r["game"], 0) + 1
            legs.append(r)
            if len(legs) == 11: break
        if len(legs) < 11:      # backfill ignoring the restriction, as the real code does
            for r in pool:
                if r["k"] in seen: continue
                seen.add(r["k"]); legs.append(r)
                if len(legs) == 11: break
        if len(legs) < 11: continue
        got = sum(1 for r in legs if res[r["k"]]["hits"] >= 1)
        tot[name][0] += got; tot[name][1] += len(legs)
        tot[name][2] += 1 if got == len(legs) else 0
        tickets[name] += 1

print(f"{'POLICY':28} {'per-leg':>8} {'lotto hits':>11} {'best slip':>10}")
for name in POLICIES:
    h, n, c = tot[name]
    if not n: continue
    print(f"{name:28} {h/n:>8.4f} {c:>6}/{tickets[name]:<4} {'':>10}")
