#!/usr/bin/env python3
"""Rebuild 5/30 sheet from manifest hr-matchups CSVs (correct SPs)."""
from __future__ import annotations

import csv
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-05-30"

spec = importlib.util.spec_from_file_location("gen0530", ROOT / "generate-0530-sheet.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

from csv_slate_meta import derive_games_from_csv, opposing_sp_for_team
from sheet_data import load_pitcher_risk, resolve_pitcher


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


TEAM_ALIAS = {
    "CHW": "CWS",
    "WAS": "WSH",
}


def canon_team(team: str) -> str:
    return TEAM_ALIAS.get(team.strip().upper(), team.strip().upper())


def canon_game_key(raw: str) -> str:
    m = re.search(r"([A-Z]{2,3})\s*@\s*([A-Z]{2,3})", raw.upper())
    if not m:
        return " ".join(raw.upper().split())
    away = canon_team(m.group(1))
    home = canon_team(m.group(2))
    return f"{away} @ {home}"


def load_park_factors(sheet_date: str) -> dict[str, dict]:
    path = ROOT / "data" / f"ParkFactors_{sheet_date}.csv"
    if not path.exists():
        return {}
    out: dict[str, dict] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            game = row.get("Game", "").strip()
            if not game:
                continue
            key = canon_game_key(game)
            out[key] = {
                "venue": row.get("Venue", "").strip(),
                "hr_pct": row.get("HR %", "").strip(),
                "hr_stadium": row.get("HR % Stadium", "").strip(),
                "hr_weather": row.get("HR % Weather", "").strip(),
            }
    return out


def fmt_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}"


def risk_note(label: str, risk_row: dict | None) -> str:
    if not risk_row:
        return f"{label}: no reliable HR-risk sample in today's export"
    overall = risk_row["overall"]
    lhb = risk_row["vs_lhb"]
    rhb = risk_row["vs_rhb"]
    split_lane = "RHB" if rhb >= lhb else "LHB"
    split_val = rhb if rhb >= lhb else lhb
    return (
        f"{label}: {overall:.2f} HR risk "
        f"(vs LHB {fmt_pct(lhb)}, vs RHB {fmt_pct(rhb)}; strongest {split_lane} lane {fmt_pct(split_val)})"
    )


def main() -> int:
    games_csv = {g["key"]: g for g in derive_games_from_csv(DATE)}
    park_factors = load_park_factors(DATE)
    pitcher_risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
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
        away_r = resolve_pitcher(pitcher_risk, away_full) or resolve_pitcher(pitcher_risk, g["away_sp"])
        home_r = resolve_pitcher(pitcher_risk, home_full) or resolve_pitcher(pitcher_risk, g["home_sp"])
        g["away_risk"] = away_r["overall"] if away_r else None
        g["home_risk"] = home_r["overall"] if home_r else None

        park = park_factors.get(g["key"], {})
        venue = park.get("venue") or g["key"]
        hr_pct = park.get("hr_pct") or "N/A"
        hr_stadium = park.get("hr_stadium") or "N/A"
        hr_weather = park.get("hr_weather") or "N/A"
        desc = (
            f"{venue} — HR environment {hr_pct} "
            f"(stadium {hr_stadium}, weather {hr_weather}). "
            f"{risk_note(away_full, away_r)}. "
            f"{risk_note(home_full, home_r)}."
        )
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
