#!/usr/bin/env python3
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("build0626", ROOT / "build-sheet-2026-06-26.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

from game_row_enrich import (
    enrich_games_list,
    game_key_from_title,
    load_weather_lookup,
    lookup_weather_for_game,
    resolve_park_context,
    row_hand_park_fields,
)
from goblin_hr_zone_fit import (
    annotate_hr_zone_ranks,
    hand_park_pct,
    hr_power_form,
    park_gate_pct,
    zone_hr_fit,
)
from sheet_data import load_pitcher_risk, resolve_pitcher

SHEET_DATE = "2026-06-26"
ENRICHED = enrich_games_list(build.games, SHEET_DATE)
PITCHER_RISK = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{SHEET_DATE}.csv")
weather_lookup = load_weather_lookup(SHEET_DATE)


def note_int(note: str, pat: str) -> int:
    m = re.search(pat, note)
    return int(m.group(1)) if m else 0


def note_float(note: str, pat: str) -> float:
    m = re.search(pat, note)
    return float(m.group(1)) if m else 0.0


rows = []
for g in ENRICHED:
    game_key = game_key_from_title(g["title"])
    weather = lookup_weather_for_game(g["title"], weather_lookup)
    park_ctx = resolve_park_context(g, weather)
    park_pct = park_ctx["park_pct"] if park_ctx["park_pct"] is not None else 0
    for r in g["rows"]:
        chip = r["chips"][0].replace("vs ", "")
        hand = r["name"].split("(")[-1].rstrip(")")
        park_fields = row_hand_park_fields(hand, park_ctx)
        risk_row = resolve_pitcher(PITCHER_RISK, chip)
        if risk_row:
            split = risk_row["vs_lhb"] if hand == "L" else risk_row["vs_rhb"]
            risk = risk_row["overall"]
        else:
            split = 0.0
            risk = 0.0
        note = r.get("note", "")
        row = {
            "name": r["name"],
            "name_plain": r["name"].split(" (")[0],
            "game_key": game_key,
            "chip": chip,
            "score": r["score"],
            "hand": hand,
            "split": split,
            "risk": risk,
            "park_pct": park_pct,
            "hr": note_int(note, r"(\d+)\s+HR"),
            "near": note_int(note, r"(\d+)\s+near-HR"),
            "ev": note_float(note, r"([\d.]+)\s+mph EV"),
            "zone_score": r.get("zoneScore"),
            "zone_hr": r.get("zoneHr"),
            "zone_barrel": r.get("zoneBarrel"),
            **park_fields,
        }
        row["hand_park_pct"] = hand_park_pct(row)
        rows.append(row)

annotate_hr_zone_ranks(rows)


def composite(r: dict) -> float:
    zone = zone_hr_fit(r)
    form = hr_power_form(r)
    split = max(r["split"], 0) * 12
    risk = max(r["risk"], 0) * 14
    park = max(r["hand_park_pct"], r["park_pct"], 0) * 0.65
    return zone * 1.0 + form * 0.85 + split + risk + park


def lane_ok(r: dict) -> bool:
    if r["hr"] < 1 and r["near"] < 2:
        return False
    if r["split"] <= 0 and r["risk"] <= 0:
        return False
    if r["split"] >= 0.15:
        return True
    if r["split"] >= 0 and r["risk"] >= 0.35:
        return True
    return r["risk"] >= 0.50


for r in rows:
    r["composite"] = composite(r)

pool = [r for r in rows if lane_ok(r)]
pool.sort(key=lambda r: r["composite"], reverse=True)

STRAIGHTS = {"Jac Caglianone (L)", "Kyle Higashioka (R)"}

picked = []
used_games: set[str] = set()
for r in pool:
    if r["game_key"] in used_games:
        continue
    picked.append(r)
    used_games.add(r["game_key"])
    if len(picked) == 3:
        break
if len(picked) < 3:
    for r in pool:
        if r in picked:
            continue
        picked.append(r)
        if len(picked) == 3:
            break

print("=== TOP 15 BY SPLIT + RISK + PARK + FORM + ZONE ===")
for i, r in enumerate(pool[:15], 1):
    zs = r.get("zone_score") or 0
    print(
        f"{i:2}. {r['name_plain']:22} {r['game_key']:12} vs {r['chip']:14} "
        f"split {r['split']:+.2f} risk {r['risk']:+.2f} park {r['hand_park_pct']:+3d}% "
        f"zone {r['hr_zone_fit']:.1f} (zs {zs}) form {hr_power_form(r):.1f} comp {r['composite']:.1f} score {r['score']}"
    )

print()
print("=== RECOMMENDED 3-LEG (1 per game) ===")
for i, r in enumerate(picked, 1):
    tag = " [STRAIGHT]" if r["name"] in STRAIGHTS else ""
    print(f"{i}. {r['name_plain']} HR — {r['game_key']} vs {r['chip']}{tag}")
    print(
        f"   Split {r['split']:+.2f} | Risk {r['risk']:+.2f} | Park {r['hand_park_pct']:+d}% "
        f"| Zone {r['hr_zone_fit']:.1f} | Form: {r['hr']} HR, {r['near']} near, {r['ev']} mph EV"
    )

print()
print("=== ALT 3-LEG (exclude straights, max 2 per game ok) ===")
alt_pool = [r for r in pool if r["name"] not in STRAIGHTS]
alt = []
alt_games: dict[str, int] = {}
for r in alt_pool:
    if alt_games.get(r["game_key"], 0) >= 2:
        continue
    alt.append(r)
    alt_games[r["game_key"]] = alt_games.get(r["game_key"], 0) + 1
    if len(alt) == 3:
        break
for i, r in enumerate(alt, 1):
    print(f"{i}. {r['name_plain']} HR — {r['game_key']} vs {r['chip']}")
    print(
        f"   Split {r['split']:+.2f} | Risk {r['risk']:+.2f} | Park {r['hand_park_pct']:+d}% "
        f"| Zone {r['hr_zone_fit']:.1f} | Form: {r['hr']} HR, {r['near']} near, {r['ev']} mph EV"
    )

print()
print("=== 3-LEG (HR risk >= 0.25, 1 per game) ===")
risk_pool = [r for r in pool if r["risk"] >= 0.25]
risk_pool.sort(key=lambda r: r["composite"], reverse=True)
risk_picked = []
risk_games: set[str] = set()
for r in risk_pool:
    if r["game_key"] in risk_games:
        continue
    risk_picked.append(r)
    risk_games.add(r["game_key"])
    if len(risk_picked) == 3:
        break
for i, r in enumerate(risk_picked, 1):
    print(f"{i}. {r['name_plain']} — {r['game_key']} vs {r['chip']}")
    print(
        f"   Split {r['split']:+.2f} | Risk {r['risk']:+.2f} | Park {r['hand_park_pct']:+d}% "
        f"| Zone {r['hr_zone_fit']:.1f} | Form: {r['hr']} HR, {r['near']} near, {r['ev']} mph EV"
    )

print()
print("=== BEST OF THE BEST (definitive picks) ===")
show = ["Jac Caglianone", "Kody Clemens", "Victor Mesa Jr.", "Junior Caminero", "Kazuma Okamoto", "Jesus Sanchez"]
by_name = {r["name_plain"]: r for r in rows}
for nm in show:
    r = by_name[nm]
    print(
        f"{nm:20} comp {composite(r):6.1f} | split {r['split']:+.2f} risk {r['risk']:+.2f} "
        f"park {r['hand_park_pct']:+3d}% zone {r['hr_zone_fit']:5.1f} form {hr_power_form(r):4.1f} | {r['game_key']}"
    )
