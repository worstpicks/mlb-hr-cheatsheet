#!/usr/bin/env python3
"""Grand-slam candidates for any built slate: python _grand_slam.py --date YYYY-MM-DD

A slam is two independent things happening in the same plate appearance, so the
model is deliberately a product of two terms rather than one blended score:

    P(slam) = E[bases-loaded PA]  x  P(HR | that PA)

The first term is almost entirely about the three hitters batting IN FRONT of
him and where he hits in the order -- it has nothing to do with his own power.
The second is the usual HR question: his own rate, the arm's HR risk in HIS
hand lane (not the overall figure -- that was the mistake on 8/17), and the
park's factor for that hand.

Ranking is what matters here. The absolute numbers are small because grand
slams are rare: roughly 1 in every 1,100 plate appearances league-wide.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent

# Dated per slate but parameterised, so this stops accruing near-duplicate copies.
_ap = argparse.ArgumentParser(description="Grand-slam board for a built slate")
_ap.add_argument("--date", required=True, help="slate date, e.g. 2026-09-03")
_ap.add_argument("--top", type=int, default=18, help="rows to print")
ARGS = _ap.parse_args()
DATE = ARGS.date

# Expected PA by lineup slot, from the same 76-slate sample the hits rubric uses.
SLOT_PA = {1: 4.54, 2: 4.44, 3: 4.34, 4: 4.22, 5: 4.09, 6: 3.92, 7: 3.78, 8: 3.61, 9: 3.45}

# League baseline: share of plate appearances that arrive with the bases loaded.
LEAGUE_LOADED_RATE = 0.045
LEAGUE_WOBA = 0.320
LEAGUE_HR_PER_PA = 0.033
# Roughly 120 grand slams a season over ~43,700 player-games: 0.27% per player-game.
# The raw product below runs an order of magnitude hot, mostly because a 20-game
# window exaggerates both on-base ahead and the hitter's own HR rate. Anchor the
# board's mean to the real league rate so the printed numbers mean something.
LEAGUE_SLAM_PER_PLAYER_GAME = 0.0027
# A hitter needs a real sample before his wOBA is allowed to move the traffic term.
MIN_PA_FOR_WOBA = 40

# Slots 3-6 inherit the most traffic; leadoff comes up empty far more often.
SLOT_LOADED_MULT = {1: 0.55, 2: 0.85, 3: 1.15, 4: 1.30, 5: 1.25, 6: 1.10,
                    7: 0.95, 8: 0.85, 9: 0.75}


def norm(name: str) -> str:
    b = unicodedata.normalize("NFKD", name or "")
    b = "".join(c for c in b if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", b.lower())


def load_sheet_rows() -> dict:
    """name -> {split, risk, park_pct, hr, near, game, chip} from the built sheet."""
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location("bs", ROOT / f"build-sheet-{DATE}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bs"] = mod
    spec.loader.exec_module(mod)
    out = {}
    for game in mod.games:
        gkey = game["title"].split(" - ")[0]
        for row in game["rows"]:
            plain = row["name"].rsplit(" (", 1)[0]
            note = row.get("note") or ""
            split = None
            m = re.search(r"split ([+-]?\d+\.\d+)", note)
            if m:
                split = float(m.group(1))
            risk = None
            m = re.search(r"HR risk ([+-]?\d+\.\d+)", note)
            if m:
                risk = float(m.group(1))
            hr = near = 0
            m = re.search(r"(\d+) HR", note)
            if m:
                hr = int(m.group(1))
            m = re.search(r"(\d+) near-HR", note)
            if m:
                near = int(m.group(1))
            out[norm(plain)] = {
                "name": plain,
                "game": gkey,
                "chip": (row.get("chips") or [""])[0].replace("vs ", ""),
                "split": split,
                "risk": risk,
                "hr": hr,
                "near": near,
            }
    return out


def pitcher_risk_lookup() -> dict:
    """Opposing arm -> per-hand HR risk, straight from the HR-targets export.

    Reading the split off the prop row only works for hitters who are ON the
    board. Everyone else got a neutral matchup, which put Alex Bregman top of
    this list while he faced Misiorowski at -0.96 against right-handers. Load it
    from the source so listed and unlisted hitters are judged the same way.
    """
    from sheet_data import load_pitcher_risk

    return load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")


def hand_split(risk_row: dict | None, hand: str) -> float | None:
    if not risk_row or risk_row.get("no_data"):
        return None
    if hand == "L":
        return risk_row.get("vs_lhb")
    if hand == "R":
        return risk_row.get("vs_rhb")
    # switch hitter takes the friendlier of the two lanes
    return max(risk_row.get("vs_lhb", 0.0), risk_row.get("vs_rhb", 0.0))


def main() -> int:
    research = json.loads(
        (ROOT / "preview" / "data" / f"research-{DATE}.json").read_text(encoding="utf-8")
    )
    sheet = load_sheet_rows()
    risk = pitcher_risk_lookup()

    cands = []
    for game in research.get("games", []):
        gkey = f"{game.get('away')} @ {game.get('home')}"
        for side, opp_key, park_side in (
            ("awayLineup", "homePitcher", None),
            ("homeLineup", "awayPitcher", None),
        ):
            lineup = [p for p in (game.get(side) or []) if p.get("order") and p["order"] <= 9]
            if len(lineup) < 9:
                continue
            lineup.sort(key=lambda p: p["order"])
            by_slot = {p["order"]: p for p in lineup}
            throws = ((game.get(opp_key) or {}).get("throws") or "R").upper()

            for p in lineup:
                slot = p["order"]
                stats = p.get("stats") or {}
                hand = (p.get("hand") or "R").upper()

                # ── term 1: how often he bats with the bases loaded ──
                ahead = [by_slot[((slot - 1 - k - 1) % 9) + 1] for k in range(3)]
                woba_ahead = []
                for a in ahead:
                    st = a.get("stats") or {}
                    w = st.get("woba") or st.get("xwoba")
                    # a .500 wOBA off 20 games is noise, not a table-setter
                    if w and (st.get("pa") or 0) >= MIN_PA_FOR_WOBA:
                        woba_ahead.append(w)
                    else:
                        woba_ahead.append(LEAGUE_WOBA)
                mean_ahead = sum(woba_ahead) / len(woba_ahead)
                # traffic scales with the on-base of the men in front, but squared
                # and capped -- cubed let one hot window dominate the whole board
                traffic = min(1.8, max(0.55, (mean_ahead / LEAGUE_WOBA) ** 2))
                pa = SLOT_PA.get(slot, 3.9)
                loaded_pa = pa * LEAGUE_LOADED_RATE * SLOT_LOADED_MULT.get(slot, 1.0) * traffic

                # ── term 2: chance that PA is a homer ──
                hr_rate = None
                if stats.get("hr") is not None and (stats.get("pa") or 0) >= 30:
                    hr_rate = stats["hr"] / stats["pa"]
                if not hr_rate:
                    hr_rate = LEAGUE_HR_PER_PA
                # blend toward league and cap: a 20-game window can show 9% HR/PA,
                # which no hitter sustains
                hr_rate = min(0.075, 0.5 * hr_rate + 0.5 * LEAGUE_HR_PER_PA)

                row = sheet.get(norm(p["name"])) or {}
                # hand-correct split from the risk export, never the overall figure
                opp = (game.get(opp_key) or {}).get("name") or ""
                rrow = risk.get(opp.lower()) or risk.get(opp.split()[-1].lower() if opp else "")
                split = hand_split(rrow, hand)
                if split is None:
                    split = row.get("split")
                split_mult = 1.0 + max(-0.6, min(0.9, (split or 0.0) * 0.42))

                park = game.get("parkLhbPct") if hand == "L" else game.get("parkRhbPct")
                if hand == "S":
                    park = game.get("parkHrPct")
                park_mult = 1.0 + (park or 0) / 100.0

                p_hr = hr_rate * split_mult * park_mult
                p_slam = loaded_pa * p_hr

                cands.append(
                    {
                        "name": p["name"],
                        "team": game.get("away") if side == "awayLineup" else game.get("home"),
                        "game": gkey,
                        "slot": slot,
                        "hand": hand,
                        "vs": row.get("chip") or (game.get(opp_key) or {}).get("name", ""),
                        "throws": throws,
                        "ahead_woba": round(mean_ahead, 3),
                        "loaded_pa": round(loaded_pa, 4),
                        "hr_rate": round(hr_rate, 4),
                        "split": split,
                        "park": park,
                        "p_slam": p_slam,
                        "listed": norm(p["name"]) in sheet,
                        "hr": row.get("hr", 0),
                        "near": row.get("near", 0),
                    }
                )

    # Calibrate: scale the whole board so its mean equals the league rate.
    if cands:
        raw_mean = sum(c["p_slam"] for c in cands) / len(cands)
        scale = (LEAGUE_SLAM_PER_PLAYER_GAME / raw_mean) if raw_mean else 1.0
        for c in cands:
            c["p_slam"] *= scale

    cands.sort(key=lambda c: c["p_slam"], reverse=True)
    print(f"=== GRAND SLAM BOARD {DATE} ===")
    print(f"{'#':<3}{'player':<22}{'slot':>4} {'game':<12}{'vs':<14}"
          f"{'ahead wOBA':>11}{'loadedPA':>9}{'HR/PA':>7}{'split':>7}{'park':>6}{'P(slam)':>9}")
    for i, c in enumerate(cands[:ARGS.top], 1):
        star = "*" if c["listed"] else " "
        print(f"{i:<3}{c['name'][:21]:<22}{c['slot']:>4} {c['game']:<12}{c['vs'][:13]:<14}"
              f"{c['ahead_woba']:>11.3f}{c['loaded_pa']:>9.3f}{c['hr_rate']:>7.3f}"
              f"{(c['split'] if c['split'] is not None else 0):>7.2f}{(c['park'] or 0):>6}"
              f"{c['p_slam']*100:>8.3f}%{star}")
    print("\n* = on the listed prop board")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
