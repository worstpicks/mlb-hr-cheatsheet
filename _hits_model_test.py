#!/usr/bin/env python3
"""Backtest a P(1+ hit) model against the legs the current rubric actually picked.

Model: P(1+ hit) = 1 - (1 - p_PA) ** E[PA]
  E[PA]  empirical, by lineup slot, from 76 slates of boxscores
  p_PA   batter contact rate, shrunk to league, scaled by the opposing starter's
         BAA in the hitter's hand lane and the park's 1B factor

Everything is taken from what was knowable pre-game: lineup slot and batter stats
come from that date's research JSON, the pitcher lane from that date's matchup CSV.
"""
from __future__ import annotations

import csv, json, re, html as htmllib, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = Path("C:/Users/allmi/AppData/Local/Temp/claude/C--Users-allmi-claude/"
             "33dec01e-fce9-422f-9b86-8d758d45d517/scratchpad/boxscore-cache.json")

SLOT_PA = {1:4.54, 2:4.44, 3:4.34, 4:4.22, 5:4.09, 6:3.92, 7:3.78, 8:3.61, 9:3.45}
LG_P_PA = 0.208      # league hit-per-PA from the same sample
LG_BAA  = 0.245
SHRINK_PA = 150


def fold(n):
    b = unicodedata.normalize("NFKD", n or "")
    b = "".join(c for c in b if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", b.lower())


def sp_lanes(date):
    """folded pitcher -> {'L': baa_vs_lhb, 'R': baa_vs_rhb}"""
    out = {}
    for p in ROOT.glob(f"data/hr-matchups-*-{date}.csv"):
        lines = p.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
        name = next((l.split(",",1)[1].strip() for l in lines if l.startswith("Pitcher,")), None)
        i = next((j for j,l in enumerate(lines) if l.split(",")[0].strip()=="SPLIT"), None)
        if not name or i is None: continue
        hdr = next(csv.reader([lines[i]]))
        lane = {}
        for l in lines[i+1:i+4]:
            r = next(csv.reader([l]), None)
            if not r or r[0] not in ("vsLHB","vsRHB"): continue
            rec = dict(zip(hdr,r))
            try: lane["L" if r[0]=="vsLHB" else "R"] = float(rec.get("BAA") or 0) or None
            except ValueError: pass
        if lane: out[fold(name)] = lane
    return out


def park_1b(date):
    m = sorted(ROOT.glob(f"data/ParkFactors_{date}*.csv"))
    if not m: return {}
    out = {}
    with m[0].open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            k = " ".join((row.get("Game") or "").split())
            v = re.search(r"([+-]?\d+)", (row.get("1B %") or "").replace("%",""))
            if k and v: out.setdefault(k, int(v.group(1)))
    return out


def board_names(path):
    t = path.read_text(encoding="utf-8", errors="ignore")
    return {fold(n.rsplit(" (",1)[0]) for n in re.findall(r'\{ name: "([^"]+)"', t)}


def p_hit(slot, avg, pa_sample, baa, park1b):
    e_pa = SLOT_PA.get(slot, 3.9)
    if avg is None:
        p = LG_P_PA
    else:
        raw = avg * 0.88                      # AVG is per AB; AB/PA ~ 0.88
        w = min(pa_sample or 0, SHRINK_PA) / SHRINK_PA
        p = raw * w + LG_P_PA * (1 - w)
    if baa:
        p *= max(0.82, min(1.20, baa / LG_BAA))
    if park1b:
        p *= 1 + park1b / 300.0               # 1B park factor is a mild nudge
    p = max(0.10, min(0.35, p))
    return 1 - (1 - p) ** e_pa


def main():
    cache = json.loads(CACHE.read_text(encoding="utf-8"))
    arch = ROOT / "preview" / "archive"
    rows_top = {5: [0,0], 8: [0,0], 11: [0,0]}
    actual = [0,0]
    pred = {5:[],8:[],11:[]}
    tickets = {5:[0,0], 8:[0,0], 11:[0,0]}

    for path in sorted(arch.glob("2026-*.html")):
        date = path.stem
        rj = ROOT / "preview" / "data" / f"research-{date}.json"
        if date not in cache or not rj.is_file(): continue
        res = cache[date]
        if not res: continue
        data = json.loads(rj.read_text(encoding="utf-8"))
        board = board_names(path)
        lanes = sp_lanes(date); parks = park_1b(date)

        cands = []
        for g in data.get("games") or []:
            p1b = parks.get(g.get("matchup",""))
            for side, opp in (("awayLineup","homePitcher"),("homeLineup","awayPitcher")):
                sp = g.get(opp) or {}
                lane = lanes.get(fold(sp.get("name","")), {})
                for pl in g.get(side) or []:
                    if not pl.get("order"): continue
                    k = fold(pl.get("name",""))
                    if k not in board or k not in res: continue
                    st = pl.get("stats") or {}
                    hand = pl.get("hand") or "R"
                    baa = lane.get("L" if hand=="L" else "R")
                    cands.append((p_hit(pl["order"], st.get("avg"), st.get("pa"), baa, p1b), k))
        if len(cands) < 11: continue
        cands.sort(reverse=True)
        seen=set(); picked=[]
        for p,k in cands:
            if k in seen: continue
            seen.add(k); picked.append((p,k))
        for n in (5,8,11):
            got=0
            for p,k in picked[:n]:
                h = 1 if res[k]["hits"]>=1 else 0
                rows_top[n][0]+=h; rows_top[n][1]+=1; got+=h
                pred[n].append(p)
            tickets[n][1]+=1
            if got==n: tickets[n][0]+=1

        # what the sheet actually used, on the same dates
        for a in re.findall(r"data-goblin-gambly-lines='([^']+)'", path.read_text(encoding="utf-8",errors="ignore")):
            u=htmllib.unescape(a)
            if "hits" not in u: continue
            for leg in json.loads(u):
                k=fold(leg.split(" - ")[0])
                if k in res:
                    actual[0]+= 1 if res[k]["hits"]>=1 else 0; actual[1]+=1
            break

    print(f"comparable dates: {tickets[11][1]}\n")
    print(f"CURRENT rubric legs on those dates : {actual[0]/actual[1]:.3f}  (n={actual[1]})")
    for n in (11,8,5):
        h,t = rows_top[n]
        c,tt = tickets[n]
        mp = sum(pred[n])/len(pred[n]) if pred[n] else 0
        print(f"PA-model top-{n:2} legs               : realized {h/t:.3f}  predicted {mp:.3f}  "
              f"bias {mp-h/t:+.3f}  (n={t})   cashed {c}/{tt}")
    print()
    for n in (3,4,5,6,8,11):
        h,t = rows_top[5]
        r = h/t
        print(f"   at the top-5 leg rate {r:.3f}, P(all {n:2}) = {r**n*100:5.2f}%")


if __name__ == "__main__":
    main()
