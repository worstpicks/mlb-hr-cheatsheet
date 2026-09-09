#!/usr/bin/env python3
"""How often would the CURRENT implemented Hits Lotto have cashed?

Mirrors the shipped rubric exactly: season/recent contact blend, strikeout
structure, opposing-arm BAA lane, park 1B, platoon xwOBA, SELECTION_CALIBRATION,
E[PA] by slot, MAX_PER_GAME=4 / MAX_PER_TEAM=3, soft MIN_SEASON_PA, slots 1-9.
Graded against real MLB boxscores.
"""
from __future__ import annotations
import json, importlib.util
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("sweep", ROOT/"_hits_variant_sweep.py")
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
import goblin_hits_parlay as G

cache = json.loads(S.CACHE.read_text(encoding="utf-8"))
LG_K = G.LEAGUE_K_PCT


def leg_prob(order, st, sv, lane, p1b, hand):
    """Recreate goblin_hits_parlay.hit_probability from research-JSON fields."""
    row = {
        "lineup_slot": order,
        "avg_bat": st.get("avg"), "pa_bat": st.get("pa"),
        "avg_season": sv.get("avg"), "pa_season": sv.get("pa"),
        "k_pct": st.get("kPct"), "k_pct_season": sv.get("kPct"),
        "bip_pct": st.get("bipPct"), "xwoba_bat": st.get("xwoba"),
        "ld_pct": st.get("ldPct"), "whiff_pct": st.get("whiffPct"),
        "sp_lane_baa": (lane or {}).get("baa"),
        "sp_lane_k_pct": (lane or {}).get("k"),
        "park_1b_pct": p1b,
        "platoon_xwoba": st.get("xwobaVsLhp") if hand == "L" else st.get("xwobaVsRhp"),
        "platoon_pa": st.get("paVsLhp") if hand == "L" else st.get("paVsRhp"),
    }
    return G.hit_probability(row), row


rows = []
for path in sorted((ROOT/"preview"/"archive").glob("2026-*.html")):
    date = path.stem
    rj = ROOT/"preview"/"data"/f"research-{date}.json"
    if date not in cache or not rj.is_file() or not cache[date]:
        continue
    res = cache[date]; data = json.loads(rj.read_text(encoding="utf-8"))
    bd = S.board(path); lanes = S.sp_lanes(date); p1bs = S.park_col(date, "1B %")
    sv_all = data.get("savant_lookup") or {}

    pool = []
    for g in data.get("games") or []:
        mk = g.get("matchup", "")
        teams = [t.strip() for t in mk.split("@")] if "@" in mk else ["", ""]
        for idx, (side, opp) in enumerate((("awayLineup","homePitcher"), ("homeLineup","awayPitcher"))):
            sp = g.get(opp) or {}; lane = lanes.get(S.fold(sp.get("name","")), {})
            hand_side = teams[idx] if len(teams) == 2 else ""
            for pl in g.get(side) or []:
                o = pl.get("order")
                if not o or o > 9: continue
                k = S.fold(pl.get("name",""))
                if k not in bd or k not in res: continue
                hand = pl.get("hand") or "R"
                st = pl.get("stats") or {}; sv = sv_all.get(str(pl.get("id"))) or {}
                p, row = leg_prob(o, st, sv, lane.get("L" if hand=="L" else "R"), p1bs.get(mk), hand)
                pool.append({"p": p, "k": k, "game": mk, "team": hand_side,
                             "pa": sv.get("pa") or st.get("pa") or 0})
    if len(pool) < G.TICKET_LEGS: continue
    pool.sort(key=lambda r: -r["p"])

    deep = [r for r in pool if r["pa"] >= G.MIN_SEASON_PA]
    use = deep if len(deep) >= G.TICKET_LEGS else pool

    legs, seen, pg, pt = [], set(), Counter(), Counter()
    for r in use:
        if r["k"] in seen: continue
        if pg[r["game"]] >= G.MAX_PER_GAME or pt[r["team"]] >= G.MAX_PER_TEAM: continue
        seen.add(r["k"]); pg[r["game"]] += 1; pt[r["team"]] += 1; legs.append(r)
        if len(legs) == G.TICKET_LEGS: break
    for r in use:                       # backfill without caps, as the real code does
        if len(legs) == G.TICKET_LEGS: break
        if r["k"] in seen: continue
        seen.add(r["k"]); legs.append(r)
    if len(legs) < G.TICKET_LEGS: continue

    got = sum(1 for r in legs if res[r["k"]]["hits"] >= 1)
    rows.append((date, got, len(legs), sum(r["p"] for r in legs)/len(legs),
                 __import__("math").prod(r["p"] for r in legs)))

n = len(rows)
legs_tot = sum(r[2] for r in rows); hits_tot = sum(r[1] for r in rows)
cashed = [r for r in rows if r[1] == r[2]]
print(f"slates graded: {n}   legs: {legs_tot}")
print(f"per-leg hit rate: {hits_tot/legs_tot:.4f}")
print(f"\n*** LOTTO CASHED: {len(cashed)} / {n} ***")
if cashed:
    for d,g,t,mp,pp in cashed: print(f"      {d}  {g}/{t}")
exp = sum(r[4] for r in rows)
print(f"\nexpected wins from the model itself: {exp:.2f} over {n} slates")
print(f"mean modelled P(all 11): {exp/n*100:.2f}%")
print("\nhow close, by legs hit:")
c = Counter(r[1] for r in rows)
for k in sorted(c, reverse=True):
    print(f"   {k:2}/11  {c[k]:3}  {'#'*c[k]}")
near = sum(v for k,v in c.items() if k >= 10)
print(f"\nslates within one leg (10+/11): {near}/{n}")
