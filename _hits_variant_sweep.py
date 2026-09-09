#!/usr/bin/env python3
"""Sweep candidate hits-model variants over 47 backtested slates.

Only question asked: which formula puts the highest-hitting eleven on the card?
Every variant is scored on realized top-11 hit rate against real boxscores.
"""
from __future__ import annotations
import csv, json, re, html as htmllib, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = Path("C:/Users/allmi/AppData/Local/Temp/claude/C--Users-allmi-claude/"
             "33dec01e-fce9-422f-9b86-8d758d45d517/scratchpad/boxscore-cache.json")
SLOT_PA = {1:4.54,2:4.44,3:4.34,4:4.22,5:4.09,6:3.92,7:3.78,8:3.61,9:3.45}
LG_P, LG_BAA, LG_K = 0.208, 0.245, 0.222

def fold(n):
    b=unicodedata.normalize("NFKD",n or ""); b="".join(c for c in b if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]","",b.lower())

def sp_lanes(date):
    out={}
    for p in ROOT.glob(f"data/hr-matchups-*-{date}.csv"):
        L=p.read_text(encoding="utf-8-sig",errors="ignore").splitlines()
        nm=next((l.split(",",1)[1].strip() for l in L if l.startswith("Pitcher,")),None)
        i=next((j for j,l in enumerate(L) if l.split(",")[0].strip()=="SPLIT"),None)
        if not nm or i is None: continue
        hdr=next(csv.reader([L[i]])); lane={}
        for l in L[i+1:i+4]:
            r=next(csv.reader([l]),None)
            if not r or r[0] not in ("vsLHB","vsRHB"): continue
            rec=dict(zip(hdr,r))
            def num(k):
                try: return float((rec.get(k) or "").replace("%","")) or None
                except ValueError: return None
            lane["L" if r[0]=="vsLHB" else "R"]={"baa":num("BAA"),"k":num("K%"),"whip":num("WHIP")}
        if lane: out[fold(nm)]=lane
    return out

def park_col(date, col):
    m=sorted(ROOT.glob(f"data/ParkFactors_{date}*.csv"))
    if not m: return {}
    out={}
    with m[0].open(encoding="utf-8-sig",newline="") as f:
        for row in csv.DictReader(f):
            k=" ".join((row.get("Game") or "").split())
            v=re.search(r"([+-]?\d+)",(row.get(col) or "").replace("%",""))
            if k and v: out.setdefault(k,int(v.group(1)))
    return out

def board(path):
    t=path.read_text(encoding="utf-8",errors="ignore")
    return {fold(n.rsplit(" (",1)[0]) for n in re.findall(r'\{ name: "([^"]+)"',t)}

def blend(recent, season, pa_r, pa_s, w_season):
    vals=[v for v in (recent,season) if v is not None]
    if not vals: return None
    if recent is None: return season
    if season is None: return recent
    return recent*(1-w_season)+season*w_season

def variants(slot, st, sv, lane, p1b, runs, hand):
    """Return {variant_name: p_PA}. E[PA] handled by caller."""
    r_avg, s_avg = st.get("avg"), sv.get("avg")
    r_pa, s_pa = st.get("pa") or 0, sv.get("pa") or 0
    r_k, s_k = st.get("kPct"), sv.get("kPct")
    baa = (lane or {}).get("baa"); spk=(lane or {}).get("k")
    out={}

    def shrink(v, pa, n=150):
        if v is None: return LG_P
        w=min(pa,n)/n
        return (v*0.88)*w + LG_P*(1-w)

    # V0: current shipped model (recent AVG only)
    p=shrink(r_avg,r_pa)
    if baa: p*=max(.82,min(1.20,baa/LG_BAA))
    if spk: p*=max(.88,min(1.10,1-(spk-22)/200))
    if p1b: p*=1+p1b/300
    out["V0 current"]=p*0.81

    # V1: blend season into recent AVG (season is the bigger, less noisy sample)
    ba=blend(r_avg,s_avg,r_pa,s_pa,0.65)
    p=shrink(ba,max(r_pa,s_pa),200)
    if baa: p*=max(.82,min(1.20,baa/LG_BAA))
    if spk: p*=max(.88,min(1.10,1-(spk-22)/200))
    if p1b: p*=1+p1b/300
    out["V1 +season blend"]=p*0.86

    # V2: V1 + explicit strikeout structure. A PA that ends in a K cannot be a hit,
    # so model p = (1-K) * hit-rate-on-contact instead of penalising K vaguely.
    kb=blend(r_k,s_k,r_pa,s_pa,0.65)
    kb=LG_K*100 if kb is None else kb
    k_rate=max(.08,min(.42,kb/100))
    sp_k=LG_K if not spk else max(.10,min(.38,spk/100))
    comb_k=max(.08,min(.45,(k_rate+sp_k)/2 + (k_rate-LG_K)*0.35))
    base=shrink(ba,max(r_pa,s_pa),200)
    hit_on_contact=base/(1-LG_K)
    p=(1-comb_k)*hit_on_contact
    if baa: p*=max(.82,min(1.20,baa/LG_BAA))
    if p1b: p*=1+p1b/300
    out["V2 +K structure"]=p*0.87

    # V3: V2 + batter's own xwOBA vs this hand
    xw = st.get("xwobaVsLhp") if hand=="L" else st.get("xwobaVsRhp")
    pa_v = st.get("paVsLhp") if hand=="L" else st.get("paVsRhp")
    p3=p
    if xw is not None and (pa_v or 0)>=40:
        p3*=max(.88,min(1.14,1+(xw-0.320)*0.55))
    out["V3 +platoon xwOBA"]=p3*0.87

    # V4: V3 + run environment lifts expected PA (handled as a p nudge here)
    p4=p3
    if runs: p4*=1+runs/600
    out["V4 +run env"]=p4*0.87
    return out


def main():
    cache=json.loads(CACHE.read_text(encoding="utf-8"))
    names=None; tot={}
    for path in sorted((ROOT/"preview"/"archive").glob("2026-*.html")):
        date=path.stem
        rj=ROOT/"preview"/"data"/f"research-{date}.json"
        if date not in cache or not rj.is_file() or not cache[date]: continue
        res=cache[date]; data=json.loads(rj.read_text(encoding="utf-8"))
        bd=board(path); lanes=sp_lanes(date)
        p1bs=park_col(date,"1B %"); runs=park_col(date,"Runs %")
        sv_all=data.get("savant_lookup") or {}
        cands={}
        for g in data.get("games") or []:
            mk=g.get("matchup","")
            for side,opp in (("awayLineup","homePitcher"),("homeLineup","awayPitcher")):
                sp=g.get(opp) or {}; lane=lanes.get(fold(sp.get("name","")),{})
                for pl in g.get(side) or []:
                    o=pl.get("order")
                    if not o or o>9: continue
                    k=fold(pl.get("name",""))
                    if k not in bd or k not in res: continue
                    hand=pl.get("hand") or "R"
                    st=pl.get("stats") or {}; sv=sv_all.get(str(pl.get("id"))) or {}
                    vs=variants(o,st,sv,lane.get("L" if hand=="L" else "R"),
                                p1bs.get(mk),runs.get(mk),hand)
                    epa=SLOT_PA.get(o,3.9)
                    for name,p in vs.items():
                        p=max(.08,min(.32,p))
                        cands.setdefault(name,[]).append((1-(1-p)**epa,k))
        if not cands: continue
        names=list(cands)
        for name,lst in cands.items():
            lst.sort(reverse=True)
            seen=set(); n=0
            for p,k in lst:
                if k in seen: continue
                seen.add(k); n+=1
                a=tot.setdefault(name,[0,0,0.0])
                a[0]+= 1 if res[k]["hits"]>=1 else 0; a[1]+=1; a[2]+=p
                if n==11: break

    print(f"{'VARIANT':22} {'realized':>9} {'predicted':>10} {'bias':>7} {'n':>6}")
    for name in names or []:
        h,t,pp=tot[name]
        print(f"{name:22} {h/t:>9.4f} {pp/t:>10.4f} {pp/t-h/t:>+7.3f} {t:>6}")

if __name__=="__main__":
    main()
