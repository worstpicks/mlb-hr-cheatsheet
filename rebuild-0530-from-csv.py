#!/usr/bin/env python3
"""Rebuild 5/30 sheet from manifest hr-matchups CSVs (correct SPs)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-05-30"

spec = importlib.util.spec_from_file_location("gen0530", ROOT / "generate-0530-sheet.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

from csv_slate_meta import derive_games_from_csv, opposing_sp_for_team


def score_from_stats(hr, near, ev, barrel, blast):
    s = 62 + hr * 4 + near * 2
    if ev:
        s += min(max(ev - 88, 0), 12)
    if barrel:
        s += min(barrel / 3, 10)
    if blast == "high":
        s += 4
    elif blast == "good":
        s += 2
    return min(98, max(58, int(round(s))))


def main() -> int:
    games_csv = {g["key"]: g for g in derive_games_from_csv(DATE)}
    game_by_team = {}
    for g in games_csv.values():
        game_by_team[g["away"]] = g
        game_by_team[g["home"]] = g

    missing = []
    updated_props = []
    for p in gen.PROPS:
        name, hand, odds, score, _old_chip, hr, near, ev, barrel, angle, blast = p
        team = gen.TEAM_MAP.get(name)
        if not team or team not in game_by_team:
            missing.append(f"{name}: unknown team {team}")
            continue
        gm = game_by_team[team]
        chip = opposing_sp_for_team(gm, team)
        csv_row = gm["batters"].get(name.lower())
        if csv_row:
            hr = csv_row["hr"]
            near = csv_row["near"]
            ev = csv_row["ev"] if csv_row["ev"] is not None else ev
            barrel = csv_row["barrel"] if csv_row["barrel"] is not None else barrel
            if csv_row["odds"] != "N/A":
                odds = csv_row["odds"]
            score = score_from_stats(hr, near, ev, barrel, blast)
        else:
            missing.append(f"{name}: not in CSV for {gm['key']}")
        updated_props.append((name, hand, odds, score, chip, hr, near, ev, barrel, angle, blast))

    print(f"Props: {len(updated_props)} updated, {len(missing)} notes")
    for m in missing[:15]:
        print("  WARN", m)
    if len(missing) > 15:
        print(f"  ... and {len(missing) - 15} more")

    # Patch generator module state and rebuild GAME_META from CSV
    gen.PROPS = updated_props
    gen.GAME_META = []
    for g in sorted(games_csv.values(), key=lambda x: x["key"]):
        away_full = g["away_sp_full"]
        home_full = g["home_sp_full"]
        away_r = g.get("away_risk")
        home_r = g.get("home_risk")
        risk_bits = []
        if away_r is not None and away_r >= 1.0:
            risk_bits.append(f"{away_full} ({away_r:.2f} HR risk)")
        if home_r is not None and home_r >= 1.0:
            risk_bits.append(f"{home_full} ({home_r:.2f} HR risk)")
        desc = f"{g['key']} — PropFinder CSV slate. "
        if risk_bits:
            desc += "Attack lanes: " + "; ".join(risk_bits) + "."
        else:
            desc += f"{away_full} vs {home_full} per imported matchup files."
        gen.GAME_META.append(
            {
                "key": g["key"],
                "title": g["title"],
                "desc": desc,
                "away": g["away"],
                "home": g["home"],
                "away_sp": g["away_sp"],
                "home_sp": g["home_sp"],
            }
        )

    bums = set()
    for g in games_csv.values():
        if g.get("away_risk") and g["away_risk"] >= 1.0:
            bums.add(g["away_sp"])
        if g.get("home_risk") and g["home_risk"] >= 1.0:
            bums.add(g["home_sp"])
    gen.BUM_PITCHERS = bums

    gen.PROP_BY_GAME = {k: [] for k in games_csv}
    for p in updated_props:
        team = gen.TEAM_MAP[p[0]]
        for gm in gen.GAME_META:
            if team in (gm["away"], gm["home"]):
                gen.PROP_BY_GAME[gm["key"]].append(p)
                break

    gen.emit_build()
    print("Wrote build-sheet-2026-05-30.py from CSV matchups")
    return 0


if __name__ == "__main__":
    sys.exit(main())
