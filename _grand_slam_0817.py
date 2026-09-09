#!/usr/bin/env python3
"""Rank 2026-08-17 hitters by grand-slam upside.

A grand slam needs two independent things to line up, and the HR board only
ranks the first:

  1. the hitter goes deep, and
  2. he comes up with the bases loaded.

So this scores P(HR) x P(loaded), built only from slate data already on disk:

  P(HR)      sheet model score + research power shape (ISO, barrel%, HR/FB%,
             hard-hit) + the hand-correct park factor + opposing SP HR risk
  P(loaded)  lineup slot's RBI-opportunity curve x on-base quality of the three
             hitters batting immediately in front (PA-shrunk xwOBA) x opposing
             starter's traffic rate (WHIP, BB%) x park run environment

Everything is printed with its components so the ranking can be argued with.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-17"
DATA = ROOT / "data"

LEAGUE_XWOBA = 0.320
SHRINK_PA = 120  # PA at which a hitter's xwOBA is trusted at full weight

# Relative share of bases-loaded plate appearances by lineup slot. The 3-4-5 band
# hits with the top-of-order on base most often; the leadoff man is guaranteed one
# bases-empty PA a game and leads off innings far more than anyone else.
SLOT_WEIGHT = {1: 0.72, 2: 0.88, 3: 1.06, 4: 1.15, 5: 1.10, 6: 1.00, 7: 0.93, 8: 0.88, 9: 0.80}


def fold(name: str) -> str:
    n = unicodedata.normalize("NFKD", (name or "").strip())
    n = "".join(c for c in n if not unicodedata.combining(c))
    return n.lower().replace(".", "").replace("'", "").replace("’", "")


def pitcher_traffic() -> dict[str, dict]:
    """Opposing-starter WHIP and BB% from this slate's matchup exports."""
    out: dict[str, dict] = {}
    manifest = json.loads((DATA / f"manifest-{DATE}.json").read_text(encoding="utf-8"))
    for fname in manifest.get("files", []):
        if not fname.startswith("hr-matchups-"):
            continue
        path = DATA / fname
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        pitcher = next((l.split(",", 1)[1].strip() for l in lines if l.startswith("Pitcher,")), None)
        hdr_i = next((i for i, l in enumerate(lines) if l.split(",")[0].strip() == "SPLIT"), None)
        if not pitcher or hdr_i is None:
            continue
        header = [c.strip() for c in next(csv.reader([lines[hdr_i]]))]
        season = next(
            (next(csv.reader([l])) for l in lines[hdr_i + 1 :] if l.startswith("Season,")), None
        )
        if not season:
            continue
        rec = dict(zip(header, season))

        def num(key: str) -> float | None:
            v = (rec.get(key) or "").strip().replace("%", "")
            try:
                return float(v)
            except ValueError:
                return None

        out[fold(pitcher)] = {"whip": num("WHIP"), "bb": num("BB%"), "name": pitcher}
    return out


def park_runs_pct() -> dict[str, int]:
    """Ballpark Pal Runs % per game key (first pitch order for doubleheaders)."""
    matches = sorted(DATA.glob(f"ParkFactors_{DATE}*.csv"))
    if not matches:
        return {}
    rows: dict[str, list[tuple[str, int]]] = {}
    with matches[0].open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            key = " ".join((row.get("Game") or "").split())
            m = re.search(r"([+-]?\d+)", (row.get("Runs %") or "").replace("%", ""))
            if key and m:
                rows.setdefault(key, []).append(((row.get("Time") or "").strip(), int(m.group(1))))

    def tkey(t: str) -> int:
        mm = re.match(r"^(\d{1,2}):(\d{2})", t)
        if not mm:
            return 9999
        h, mi = int(mm.group(1)), int(mm.group(2))
        return (h + 12 if 1 <= h <= 11 else h) * 60 + mi

    out: dict[str, int] = {}
    for key, entries in rows.items():
        entries.sort(key=lambda e: tkey(e[0]))
        out[key] = entries[0][1]
        for i, (_t, v) in enumerate(entries, 1):
            out[f"{key} (G{i})"] = v
    return out


def sheet_rows() -> dict[tuple[str, str], dict]:
    """Listed props from the built sheet: (game key, folded name) -> row info."""
    src = (ROOT / "build-sheet-2026-08-17.py").read_text(encoding="utf-8")
    out: dict[tuple[str, str], dict] = {}
    for gm in re.finditer(r'"title": "([^"]+)",\s*\n\s*"description".*?"rows": \[(.*?)\n        \],', src, re.S):
        gkey = gm.group(1).split(" - ")[0]
        for rm in re.finditer(
            r'row\("([^"]+)", "([LRS])", "([^"]+)", (\d+), "([^"]*)", \["vs ([^"]+)"\]', gm.group(2)
        ):
            name, hand, odds, score, emojis, chip = rm.groups()
            out[(gkey, fold(name))] = {
                "name": name,
                "hand": hand,
                "odds": odds,
                "score": int(score),
                "emojis": emojis,
                "vs": chip,
            }
    return out


def shrunk_xwoba(stats: dict) -> float:
    x = stats.get("xwoba")
    pa = stats.get("pa") or 0
    if x is None:
        x = stats.get("woba")
    if x is None:
        return LEAGUE_XWOBA
    w = min(pa, SHRINK_PA) / SHRINK_PA
    return x * w + LEAGUE_XWOBA * (1 - w)


def power_index(stats: dict, score: int | None) -> float:
    """Hitter HR ability, 0-100ish. Sheet score leads; research shape refines it."""
    iso = stats.get("iso") or 0.0
    barrel = stats.get("barrelPct") or 0.0
    hrfb = stats.get("hrFbPct") or 0.0
    hard = stats.get("hardHitPct") or 0.0
    pull_air = stats.get("pullAirPct") or 0.0
    pa = stats.get("pa") or 0
    trust = min(pa, SHRINK_PA) / SHRINK_PA

    shape = (
        min(iso / 0.250, 1.6) * 26
        + min(barrel / 12.0, 1.8) * 24
        + min(hrfb / 15.0, 1.8) * 20
        + min(hard / 45.0, 1.5) * 18
        + min(pull_air / 18.0, 1.6) * 12
    )
    shape *= trust
    if score is None:
        return shape
    return 0.55 * score + 0.45 * shape


def main() -> None:
    research = json.loads((ROOT / "preview" / "data" / f"research-{DATE}.json").read_text(encoding="utf-8"))
    traffic = pitcher_traffic()
    runs = park_runs_pct()
    listed = sheet_rows()

    # Doubleheader: two entries share a matchup string, ordered by first pitch.
    seen: dict[str, int] = {}
    rows: list[dict] = []

    for g in sorted(research["games"], key=lambda x: x.get("startTime") or ""):
        base = g["matchup"]
        seen[base] = seen.get(base, 0) + 1
        dh = [x for x in research["games"] if x["matchup"] == base]
        gkey = f"{base} (G{seen[base]})" if len(dh) > 1 else base

        for side, opp_key in (("awayLineup", "homePitcher"), ("homeLineup", "awayPitcher")):
            lineup = [r for r in g.get(side) or [] if r.get("order")]
            if not lineup:
                continue
            by_order = {r["order"]: r for r in lineup}
            sp = g.get(opp_key) or {}
            tr = traffic.get(fold(sp.get("name", "")), {})
            whip = tr.get("whip")
            bbpct = tr.get("bb")
            sp_stats = sp.get("stats") or {}

            for r in lineup:
                order = r["order"]
                # Slots 10+ are bench/depth, not the batting order. On 8/17 that is
                # Ohtani, Freeman, Betts, Goodman, McCarthy and Moniak -- all really
                # out, confirmed against the MLB boxscore.
                if order > 9:
                    continue
                stats = r.get("stats") or {}
                hand = r.get("hand") or "R"

                # On-base quality of the three hitters batting immediately in front.
                front = []
                for back in (1, 2, 3):
                    o = order - back
                    o = o + 9 if o < 1 else o
                    prev = by_order.get(o)
                    if prev:
                        front.append(shrunk_xwoba(prev.get("stats") or {}))
                front_obp = sum(front) / len(front) if front else LEAGUE_XWOBA

                # Traffic the opposing starter allows. A 0-BF arm (Emanuel, Gamboa)
                # exports a blank block that parses as 0.0 — that is "unknown", not
                # "allows nobody", so it must land neutral rather than as a penalty.
                whip_mult = 1.0 if not whip else max(0.80, min(1.25, whip / 1.25))
                bb_mult = 1.0 if not bbpct else max(0.92, min(1.12, 1 + (bbpct - 8.0) / 100))

                runs_pct = runs.get(gkey, runs.get(base, 0))
                runs_mult = 1 + runs_pct / 200  # half-weight; run env is a nudge

                loaded = (
                    SLOT_WEIGHT.get(order, 0.9)
                    * (front_obp / LEAGUE_XWOBA)
                    * whip_mult
                    * bb_mult
                    * runs_mult
                )

                key = (gkey, fold(r["name"]))
                row = listed.get(key)
                park = g.get("parkLhbPct" if hand == "L" else "parkRhbPct")
                if park is None:
                    park = g.get("parkHrPct") or 0
                power = power_index(stats, row["score"] if row else None)
                park_mult = 1 + park / 100

                # Hand-correct split, matching the sheet's batter_split(): a switch
                # hitter takes his better lane. Using the pitcher's OVERALL hrRisk here
                # badly over-rated right-handed bats facing Quinn Mathews (-1.35 vs RHB)
                # and Blake Snell (-1.37 vs RHB), whose overall figure is far kinder
                # than the lane the hitter actually stands in.
                vsl, vsr = sp_stats.get("vsLhb"), sp_stats.get("vsRhb")
                if hand == "S":
                    sp_risk = max(v for v in (vsl, vsr) if v is not None) if (vsl is not None or vsr is not None) else None
                else:
                    sp_risk = vsl if hand == "L" else vsr
                if sp_risk is None:
                    sp_risk = sp_stats.get("hrRisk")
                risk_mult = 1.0 if sp_risk is None else max(0.75, min(1.30, 1 + sp_risk / 8))

                rows.append(
                    {
                        "name": r["name"],
                        "game": gkey,
                        "order": order,
                        "hand": hand,
                        "sp": sp.get("name", "?"),
                        "power": power,
                        "loaded": loaded,
                        "front_obp": front_obp,
                        "whip": whip,
                        "park": park,
                        "sp_risk": sp_risk,
                        "gs": power * park_mult * risk_mult * loaded,
                        "listed": row,
                        "hr": stats.get("hr") or 0,
                        "iso": stats.get("iso") or 0,
                        "barrel": stats.get("barrelPct") or 0,
                    }
                )

    rows.sort(key=lambda x: -x["gs"])

    print(f"=== GRAND SLAM INDEX {DATE} — power x bases-loaded opportunity ===\n")
    print(f"{'#':>2}  {'HITTER':22} {'GAME':16} {'SLOT':>4} {'GS':>6} {'PWR':>5} {'LOAD':>5} "
          f"{'FRONT3':>6} {'WHIP':>5} {'PARK':>5} {'ODDS':>7}")
    shown = 0
    for r in rows:
        if not r["listed"]:
            continue
        shown += 1
        if shown > 18:
            break
        odds = r["listed"]["odds"] if r["listed"] else "-"
        print(
            f"{shown:>2}  {r['name'][:22]:22} {r['game']:16} {r['order']:>4} {r['gs']:>6.1f} "
            f"{r['power']:>5.1f} {r['loaded']:>5.2f} {r['front_obp']:>6.3f} "
            f"{(f'{r[chr(39)+chr(39)]}' if False else (f'{r['''whip''']:.2f}' if r['''whip'''] else '   --')):>5} {r['park']:>4}% {odds:>7}"
        )

    print("\n--- top unlisted bats (no HR prop on the board, context only) ---")
    n = 0
    for r in rows:
        if r["listed"]:
            continue
        n += 1
        if n > 6:
            break
        print(f"    {r['name'][:22]:22} {r['game']:16} slot {r['order']}  GS {r['gs']:.1f}  "
              f"front3 {r['front_obp']:.3f}  vs {r['sp']}")


if __name__ == "__main__":
    main()
