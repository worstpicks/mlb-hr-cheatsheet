#!/usr/bin/env python3
"""11-leg hits ticket with a hard one-player-per-game cap for 2026-08-14.

The sheet's own hits parlay allows 2 per game (goblin_hits_parlay.MAX_PER_GAME), so
this is a separate view rather than a reuse of select_hits_parlay: take each game's
single best hit profile under the shared rubric, then keep the 11 strongest games.
Row construction mirrors collect_rows() in patch-0814-preview.py so the ranks match
the board exactly.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from goblin_hits_parlay import SPLIT_HARD_FLOOR, annotate_hits_ranks
from hr_score_model import batter_split
from note_compact import compact_note
from sheet_data import load_pitcher_risk, resolve_pitcher

ROOT = Path(__file__).resolve().parent
SHEET_DATE = "2026-08-14"
N_LEGS = 11

spec = importlib.util.spec_from_file_location("build0814", ROOT / "build-sheet-2026-08-14.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

from game_row_enrich import (  # noqa: E402  (build module must load first)
    contact_risk,
    enrich_games_list,
    game_key_from_title,
    load_weather_lookup,
    lookup_weather_for_game,
    resolve_park_context,
    row_hand_park_fields,
)

ENRICHED_GAMES = enrich_games_list(build.games, SHEET_DATE)
PITCHER_RISK = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{SHEET_DATE}.csv")


def row_high_whiff(row: dict, *, for_hits: bool = False) -> bool:
    if row.get("contact_risk"):
        return True
    whiff = row.get("whiff_pct")
    k_pct = row.get("k_pct")
    limit = 26.0 if for_hits else 28.0
    return (whiff is not None and whiff >= limit) or (k_pct is not None and k_pct >= limit)


def collect_rows() -> list[dict]:
    rows: list[dict] = []
    weather_lookup = load_weather_lookup(SHEET_DATE)
    for g in ENRICHED_GAMES:
        game_key = game_key_from_title(g["title"])
        weather = lookup_weather_for_game(g["title"], weather_lookup)
        park_ctx = resolve_park_context(g, weather)
        park_pct = park_ctx["park_pct"] if park_ctx["park_pct"] is not None else 0
        for r in g["rows"]:
            chip = r["chips"][0].replace("vs ", "")
            hand = r["name"].split("(")[-1].rstrip(")")
            park_fields = row_hand_park_fields(hand, park_ctx)
            risk_row = resolve_pitcher(PITCHER_RISK, chip)
            split = batter_split(hand, risk_row) or 0.0 if risk_row else 0.0
            risk = risk_row["overall"] if risk_row else 0.0
            whiff_pct = r.get("whiffPct")
            k_pct = r.get("kPct")
            rows.append(
                {
                    "game_key": game_key,
                    "name": r["name"],
                    "name_plain": r["name"].rsplit(" (", 1)[0],
                    "team": build.PLAYER_TEAMS.get(r["name"], ""),
                    "odds": r["odds"],
                    "score": r["score"],
                    "chip": chip,
                    "note": compact_note(r["note"]),
                    "hr": 0,
                    "near": 0,
                    "ev": 0.0,
                    "barrel": 0.0,
                    "split": split,
                    "risk": risk,
                    "hand": hand,
                    "park_pct": park_pct,
                    **park_fields,
                    "zone_score": r.get("zoneScore"),
                    "zone_contact": r.get("zoneContact"),
                    "zone_barrel": r.get("zoneBarrel"),
                    "zone_hr": r.get("zoneHr"),
                    "zone_hard_hit": r.get("zoneHardHit"),
                    "whiff_pct": whiff_pct,
                    "k_pct": k_pct,
                    "contact_risk": bool(r.get("contactRisk")) or contact_risk(whiff_pct, k_pct),
                }
            )
    return rows


def sample_weight(row: dict) -> float:
    """Trust ramp on season rate stats; ramps to full at 120 PA."""
    pa = row.get("pa_bat") or 0
    return max(0.35, min(1.0, pa / 120.0)) if pa else 0.5


def hit_quality(row: dict) -> float:
    """Hit-ability-first score: getting on base via a knock, not driving the ball out.

    The shared hits rubric leads with zone contact, which on this slate floated bats
    hitting .123 and .176 into the ticket. For a one-per-game 'best bat for a hit' ask,
    season hit rate and contact quality lead and zone fit only supports.
    """
    w = sample_weight(row)
    avg = row.get("avg_bat")
    xw = row.get("xwoba_bat")
    bip = row.get("bip_pct")
    ld = row.get("ld_pct")
    ss = row.get("sweet_spot_pct")

    score = 0.0
    if avg is not None:
        score += (avg - 0.240) * 420.0 * w
    if xw is not None:
        score += (xw - 0.310) * 260.0 * w
    if bip is not None:
        score += (bip - 66.0) * 0.85
    if ld is not None:
        score += (ld - 20.0) * 0.55 * w
    if ss is not None:
        score += (ss - 33.0) * 0.30 * w

    # Strikeouts are the main way a hit ticket dies.
    for pct in (row.get("whiff_pct"), row.get("k_pct")):
        if pct is not None:
            score += (24.0 - pct) * 0.55

    # Matchup contact fit supports but cannot carry a weak bat.
    zc = row.get("zone_contact")
    if zc is not None:
        score += (zc - 34.0) * 0.30
    score += (row.get("zone_score") or 0.0) * 0.10

    # Platoon lane is a light nudge for hits.
    score += (row.get("split") or 0.0) * 1.5

    ev = row.get("ev") or 0.0
    if ev >= 88.0:
        score += min(ev - 88.0, 10.0) * 0.25
    return score


MIN_PA = 45


def sample_ok(row: dict) -> bool:
    """A leg needs a real sample. 3 PA at a .594 xwOBA is noise, not a hit profile."""
    pa = row.get("pa_bat")
    if pa is None:
        return True  # unknown sample: judged on zone/matchup rather than dropped
    return pa >= MIN_PA


def hit_floor_ok(row: dict) -> bool:
    """Reject bats with no real hit case; a hot zone chart cannot fix a .12 bat."""
    avg = row.get("avg_bat")
    xw = row.get("xwoba_bat")
    pa = row.get("pa_bat") or 0
    if avg is None and xw is None:
        return True  # no season data: let the rubric decide rather than blind-drop
    if pa >= 40:
        if avg is not None and avg < 0.215:
            return False
        if xw is not None and xw < 0.285:
            return False
    return True


def main() -> None:
    rows = collect_rows()
    annotate_hits_ranks(rows, row_high_whiff=row_high_whiff, sheet_date=SHEET_DATE)

    eligible = [
        r
        for r in rows
        if not row_high_whiff(r, for_hits=True) and (r.get("split") or 0.0) >= SPLIT_HARD_FLOOR
    ]

    for r in rows:
        r["hit_quality"] = hit_quality(r)

    pool = [r for r in eligible if hit_floor_ok(r) and sample_ok(r)]

    thin = [r for r in eligible if hit_floor_ok(r) and not sample_ok(r)]
    if thin:
        print(f"=== dropped on sample (< {MIN_PA} PA) ===")
        for r in sorted(thin, key=lambda x: x["hit_quality"], reverse=True)[:6]:
            print(
                f"    {r['name_plain']:22} {r['game_key']:11} PA {r.get('pa_bat') or 0:3}"
                f" · AVG {('%.3f' % r['avg_bat']) if r.get('avg_bat') else 'n/a'}"
                f" · xwOBA {('%.3f' % r['xwoba_bat']) if r.get('xwoba_bat') else 'n/a'}"
            )
        print()

    print("=== per-game candidates (hit-quality order) ===")
    by_game: dict[str, list[dict]] = {}
    for r in sorted(pool, key=lambda x: x["hit_quality"], reverse=True):
        by_game.setdefault(r["game_key"], []).append(r)
    for gk, cands in by_game.items():
        print(f"  {gk}")
        for c in cands[:3]:
            avg = c.get("avg_bat")
            xw = c.get("xwoba_bat")
            bip = c.get("bip_pct")
            print(
                f"      {c['name_plain']:22} hq {c['hit_quality']:6.2f} · rubric {c['hits_rank']:6.2f}"
                f" · AVG {('%.3f' % avg) if avg else ' n/a '} · xwOBA {('%.3f' % xw) if xw else ' n/a '}"
                f" · BIP {('%.0f%%' % bip) if bip else 'n/a'} · zc {c.get('zone_contact') or 0:5.1f}"
                f" · split {c['split']:+.2f} · PA {c.get('pa_bat') or 0}"
            )
    print()

    dropped = [r for r in eligible if not hit_floor_ok(r)]
    if dropped:
        print("=== failed hit floor (AVG < .215 or xwOBA < .285 on 40+ PA) ===")
        for r in sorted(dropped, key=lambda x: x["hits_rank"], reverse=True)[:8]:
            avg = r.get("avg_bat")
            xw = r.get("xwoba_bat")
            print(
                f"    {r['name_plain']:22} {r['game_key']:11} rubric {r['hits_rank']:6.2f}"
                f" · AVG {('%.3f' % avg) if avg else 'n/a'} · xwOBA {('%.3f' % xw) if xw else 'n/a'}"
                f" · PA {r.get('pa_bat') or 0}"
            )
        print()

    best_by_game: dict[str, dict] = {}
    for r in sorted(pool, key=lambda x: x["hit_quality"], reverse=True):
        best_by_game.setdefault(r["game_key"], r)

    ordered = sorted(best_by_game.values(), key=lambda x: x["hit_quality"], reverse=True)
    legs = ordered[:N_LEGS]
    benched = ordered[N_LEGS:]

    print(f"=== 11-LEG HITS TICKET (max 1 per game) — {SHEET_DATE} ===")
    print(f"eligible bats {len(eligible)}/{len(rows)} · games represented {len(best_by_game)}\n")
    for i, r in enumerate(legs, 1):
        bip = r.get("bip_pct")
        avg = r.get("avg_bat")
        xw = r.get("xwoba_bat")
        print(f"{i:2}. {r['name_plain']:22} {r['team']:4} {r['game_key']:11} vs {r['chip']}")
        print(
            f"      hq {r['hit_quality']:6.2f} · rubric {r['hits_rank']:6.2f}"
            f" · zone contact {r.get('zone_contact') or 0:5.1f}"
            f" · zone {r.get('zone_score') or 0:5.1f} · split {r['split']:+.2f}"
            f" · BIP {('%.0f%%' % bip) if bip else '  n/a':>5}"
            f" · AVG {('%.3f' % avg) if avg else ' n/a'}"
            f" · xwOBA {('%.3f' % xw) if xw else ' n/a'}"
            f" · whiff {r.get('whiff_pct') if r.get('whiff_pct') is not None else 'n/a'}"
            f" · K% {r.get('k_pct') if r.get('k_pct') is not None else 'n/a'}"
        )
        print(f"      {r['note'][:150]}")

    if benched:
        print("\n--- games left out (their best bat) ---")
        for r in benched:
            avg = r.get("avg_bat")
            print(
                f"    {r['name_plain']:22} {r['game_key']:11} hq {r['hit_quality']:6.2f}"
                f" · AVG {('%.3f' % avg) if avg else 'n/a'}"
                f" · zone contact {r.get('zone_contact') or 0:5.1f} · split {r['split']:+.2f}"
            )

    games = [r["game_key"] for r in legs]
    assert len(set(games)) == len(games), "duplicate game in ticket"
    assert len(legs) == N_LEGS, f"only {len(legs)} legs"
    print("\nOK  11 legs, 11 distinct games, no high-whiff bats")
    print("\nGambly lines:")
    for r in legs:
        print(f"  {r['name_plain']} - Over 0.5 hits")


if __name__ == "__main__":
    main()
