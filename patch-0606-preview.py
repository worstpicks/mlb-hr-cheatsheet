#!/usr/bin/env python3
"""Patch preview sheet to 2026-06-06. Does not commit or push."""
from __future__ import annotations

import csv
import importlib.util
import json
import re
import shutil
from pathlib import Path

from sheet_data import load_pitcher_risk, resolve_pitcher

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
MANIFEST_PATH = ROOT / "preview" / "sheets-manifest.json"
ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-06-05.html"
SHEET_DATE = "2026-06-06"

spec = importlib.util.spec_from_file_location("build0606", ROOT / "build-sheet-2026-06-06.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

from game_row_enrich import (
    contact_risk,
    enrich_games_list,
    emit_games_js,
    game_key_from_title,
    load_weather_lookup,
    lookup_weather_for_game,
    resolve_park_context,
)
from note_compact import compact_goblin_leg, compact_note, compact_row_line, straight_pick_why

ENRICHED_GAMES = enrich_games_list(build.games, SHEET_DATE)
GAMES_BLOCK = emit_games_js(ENRICHED_GAMES)

TOTAL_GAMES = len(build.games)
TOTAL_ROWS = sum(len(g["rows"]) for g in build.games)
TOTAL_FAVS = len(build.FAVS)
FAVS = sorted(build.FAVS)

PITCHER_RISK = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{SHEET_DATE}.csv")


def data_attr(lines):
    """JSON for data-goblin-gambly-lines (attribute delimited with single quotes)."""
    return json.dumps(lines).replace('"', "&quot;").replace("'", "&#39;")


def parse_odds_value(odds_text: str) -> int | None:
    m = re.search(r"Listed ([+-]\d+)", odds_text)
    return int(m.group(1)) if m else None


def note_hr_count(note: str) -> int:
    m = re.search(r"(\d+)\s+HR", note)
    return int(m.group(1)) if m else 0


def note_near_count(note: str) -> int:
    m = re.search(r"(\d+)\s+near-HR", note)
    return int(m.group(1)) if m else 0


def note_ev(note: str) -> float:
    m = re.search(r"(\d+(?:\.\d+)?)\s+mph EV", note)
    return float(m.group(1)) if m else 0.0


def note_barrel(note: str) -> float:
    m = re.search(r"(\d+(?:\.\d+)?)% barrels", note)
    return float(m.group(1)) if m else 0.0


def row_high_whiff(row: dict, *, for_hits: bool = False) -> bool:
    """True when Whiff pill would show, or (for hits) elevated miss rate."""
    if row.get("contact_risk"):
        return True
    whiff = row.get("whiff_pct")
    k_pct = row.get("k_pct")
    limit = 26.0 if for_hits else 28.0
    return (whiff is not None and whiff >= limit) or (k_pct is not None and k_pct >= limit)


def collect_rows():
    rows = []
    weather_lookup = load_weather_lookup(SHEET_DATE)
    for g in ENRICHED_GAMES:
        game_key = game_key_from_title(g["title"])
        weather = lookup_weather_for_game(g["title"], weather_lookup)
        park_ctx = resolve_park_context(g, weather)
        park_pct = park_ctx["park_pct"] if park_ctx["park_pct"] is not None else 0
        for r in g["rows"]:
            chip = r["chips"][0].replace("vs ", "")
            hand = r["name"].split("(")[-1].rstrip(")")
            risk_row = resolve_pitcher(PITCHER_RISK, chip)
            if risk_row:
                split = risk_row["vs_lhb"] if hand == "L" else risk_row["vs_rhb"]
                risk = risk_row["overall"]
            else:
                split = 0.0
                risk = 0.0
            rank = r["score"] + split * 8.0 + risk * 4.0 + park_pct * 0.20
            whiff_pct = r.get("whiffPct")
            k_pct = r.get("kPct")
            rows.append(
                {
                    "game_key": game_key,
                    "name": r["name"],
                    "name_plain": r["name"].rsplit(" (", 1)[0],
                    "team": build.PLAYER_TEAMS.get(r["name"], ""),
                    "odds": r["odds"],
                    "odds_value": parse_odds_value(r["odds"]),
                    "score": r["score"],
                    "chip": chip,
                    "note": compact_note(r["note"]),
                    "hr": note_hr_count(r["note"]),
                    "near": note_near_count(r["note"]),
                    "ev": note_ev(r["note"]),
                    "barrel": note_barrel(r["note"]),
                    "split": split,
                    "risk": risk,
                    "park_pct": park_pct,
                    "rank": rank,
                    "whiff_pct": whiff_pct,
                    "k_pct": k_pct,
                    "contact_risk": bool(r.get("contactRisk"))
                    or contact_risk(whiff_pct, k_pct),
                }
            )
    rows.sort(key=lambda x: (x["rank"], x["score"], x["odds_value"] or -9999), reverse=True)
    return rows


def load_pitchers_to_attack():
    out = [
        {
            "pitcher": row["pitcher"],
            "risk": row["overall"],
            "vs_lhb": f"{row['vs_lhb']:+.2f}",
            "vs_rhb": f"{row['vs_rhb']:+.2f}",
        }
        for row in PITCHER_RISK.values()
    ]
    out.sort(key=lambda x: x["risk"], reverse=True)
    return out[:5]


def load_weather_rows():
    data_dir = ROOT / "data"
    path = data_dir / f"ParkFactors_{SHEET_DATE}.csv"
    if not path.exists():
        matches = sorted(data_dir.glob(f"ParkFactors_{SHEET_DATE}*.csv"))
        if matches:
            path = matches[0]
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            game = " ".join(row["Game"].replace("  ", " ").split())
            try:
                hr_pct = int(row["HR %"].replace("%", ""))
            except ValueError:
                continue
            rows.append(
                {
                    "game": game,
                    "venue": row["Venue"],
                    "hr_pct": hr_pct,
                    "hr_pct_text": row["HR %"],
                    "hr_stadium": row["HR % Stadium"],
                    "hr_weather": row["HR % Weather"],
                }
            )
    return rows


rows = collect_rows()
listed_rows = [r for r in rows if r["odds_value"] is not None]
if not listed_rows:
    listed_rows = rows
# Straights/Goblin HR legs: include N/A odds props (user list); listed-only for longshots display.
straight_rows = rows

# O0.5 straight: prioritize attackable pitcher lanes plus park/weather support,
# not just the highest raw batter-form score.
def straight_attack_rank(row: dict) -> float:
    return (
        row["score"] * 0.25
        + max(row["risk"], 0.0) * 12.0
        + max(row["split"], 0.0) * 10.0
        + row["park_pct"] * 0.65
        + row["hr"] * 3.0
        + row["near"] * 1.4
        + max(row["ev"] - 90.0, 0.0) * 0.45
    )


def pick_top_n(
    ranked: list[dict],
    n: int,
    *,
    exclude_names: set[str] | None = None,
    max_per_game: int = 2,
    max_per_team: int | None = 2,
) -> list[dict]:
    """Pick top rows with at most max_per_game from the same game (and team when set)."""
    exclude_names = exclude_names or set()
    picked: list[dict] = []
    seen: set[str] = set()
    game_counts: dict[str, int] = {}
    team_counts: dict[str, int] = {}

    for r in ranked:
        if r["name"] in seen or r["name"] in exclude_names:
            continue
        game_count = game_counts.get(r["game_key"], 0)
        if game_count >= max_per_game:
            continue
        if max_per_team is not None and r.get("team"):
            team_count = team_counts.get(r["team"], 0)
            if team_count >= max_per_team:
                continue
        seen.add(r["name"])
        picked.append(r)
        game_counts[r["game_key"]] = game_count + 1
        if max_per_team is not None and r.get("team"):
            team_counts[r["team"]] = team_counts.get(r["team"], 0) + 1
        if len(picked) == n:
            break

    return picked


STRAIGHT_O15_BLOCKLIST: set[str] = set()
STRAIGHT_O05_BLOCKLIST: set[str] = set()

def multi_hr_rank(row: dict) -> float:
    """O1.5 straight rank: true multi-HR profile, not just highest raw HR score."""
    rank = (
        row["hr"] * 5.0
        + row["near"] * 2.0
        + max(row["ev"] - 90.0, 0.0) * 0.8
        + row["score"] * 0.25
        + row["split"] * 8.0
        + row["risk"] * 5.0
        + row["park_pct"] * 0.40
    )
    return rank

def straight_o05_pool(
    candidates: list[dict],
    *,
    exclude_name: str | None = None,
    exclude_game: str | None = None,
    strict: bool = True,
) -> list[dict]:
    pool = [
        r
        for r in candidates
        if r["name"] not in STRAIGHT_O05_BLOCKLIST
        and (exclude_name is None or r["name"] != exclude_name)
        and (exclude_game is None or r["game_key"] != exclude_game)
    ]
    if strict:
        pool = [
            r
            for r in pool
            if r["score"] >= 72
            and r["split"] >= 0.0
            and (r["risk"] >= 0.50 or r["park_pct"] >= 3 or r["split"] >= 0.75)
            and (r["hr"] >= 1 or r["near"] >= 3)
        ]
    pool.sort(key=straight_attack_rank, reverse=True)
    return pool


o15_candidates = [
    r
    for r in straight_rows
    if r["name"] not in STRAIGHT_O15_BLOCKLIST
    and r["hr"] >= 2
    and r["near"] >= 2
    and r["score"] >= 78
    and r["split"] >= 0.0
    and (r["risk"] >= 0.25 or r["park_pct"] >= 3 or r["split"] >= 0.75)
]
o15_candidates.sort(key=multi_hr_rank, reverse=True)

straight_o15 = None
straight_o05 = None

if straight_o15 is None:
    for o15 in o15_candidates:
        o05_pool = straight_o05_pool(straight_rows, exclude_name=o15["name"], exclude_game=o15["game_key"])
        if o05_pool:
            straight_o15 = o15
            straight_o05 = o05_pool[0]
            break

if straight_o15 is None:
    straight_o15 = o15_candidates[0] if o15_candidates else straight_rows[0]
    o05_pool = straight_o05_pool(
        straight_rows,
        exclude_name=straight_o15["name"],
        exclude_game=straight_o15["game_key"],
    )
    if not o05_pool:
        o05_pool = straight_o05_pool(
            straight_rows,
            exclude_name=straight_o15["name"],
            exclude_game=straight_o15["game_key"],
            strict=False,
        )
    straight_o05 = o05_pool[0] if o05_pool else straight_o15

if straight_o05["game_key"] == straight_o15["game_key"]:
    alt_o15 = next(
        (r for r in o15_candidates if r["game_key"] != straight_o05["game_key"]),
        None,
    )
    if alt_o15:
        straight_o15 = alt_o15

straight_names = {straight_o05["name"], straight_o15["name"]}


def row_is_favorite(row: dict) -> bool:
    return row["name"] in FAVS


def available_fav_count(exclude_names: set[str]) -> int:
    return sum(1 for r in rows if r["name"] in FAVS and r["name"] not in exclude_names)


# If straights consume too many favorites, swap O0.5 to next attack lane so Favorite 3-leg can fill.
if available_fav_count(straight_names) < 3 and row_is_favorite(straight_o05):
    for alt_o05 in straight_o05_pool(
        straight_rows,
        exclude_name=straight_o15["name"],
        exclude_game=straight_o15["game_key"],
    )[1:]:
        if row_is_favorite(alt_o05):
            continue
        trial = {alt_o05["name"], straight_o15["name"]}
        if available_fav_count(trial) >= 3:
            straight_o05 = alt_o05
            straight_names = trial
            break

# Goblin HR legs: real form plus a usable opposing split/risk lane (reject 0/0 pitcher data).
def goblin_hr_leg_ok(row: dict) -> bool:
    if row["hr"] < 1 and row["near"] < 2:
        return False
    if row["split"] <= 0.0 and row["risk"] <= 0.0:
        return False
    if row["split"] > 0.0:
        return True
    return row["risk"] >= 0.25 or row["park_pct"] >= 3


top3_pool = [
    r for r in straight_rows if r["name"] not in straight_names and goblin_hr_leg_ok(r)
]
top3_pool.sort(key=lambda x: (straight_attack_rank(x), x["rank"], x["score"]), reverse=True)

fav_reserve = sorted(
    [
        r
        for r in rows
        if r["name"] in FAVS
        and r["name"] not in straight_names
        and r["split"] >= 0.0
    ],
    key=lambda x: (straight_attack_rank(x), x["score"]),
    reverse=True,
)[:3]
reserved_fav_names = {r["name"] for r in fav_reserve}

top3_pool_reserved = [r for r in top3_pool if r["name"] not in reserved_fav_names]
top3 = pick_top_n(top3_pool_reserved, 3, exclude_names=straight_names, max_per_game=2, max_per_team=2)
if len(top3) < 3:
    top3 = pick_top_n(top3_pool, 3, exclude_names=straight_names, max_per_game=2, max_per_team=2)
if len(top3) < 3:
    extra = sorted(
        [r for r in straight_rows if r["name"] not in straight_names and goblin_hr_leg_ok(r)],
        key=lambda x: (straight_attack_rank(x), x["rank"], x["score"]),
        reverse=True,
    )
    top3 = pick_top_n(extra, 3, exclude_names=straight_names, max_per_game=2, max_per_team=2)

two_leg_pool = [
    r
    for r in straight_rows
    if r["name"] not in straight_names
    and r["name"] not in {x["name"] for x in top3}
    and goblin_hr_leg_ok(r)
]
two_leg_pool.sort(key=lambda x: (straight_attack_rank(x), x["rank"], x["score"]), reverse=True)
two_leg = pick_top_n(
    two_leg_pool,
    2,
    exclude_names=straight_names | {x["name"] for x in top3},
    max_per_game=1,
    max_per_team=2,
)
if len(two_leg) < 2:
    two_leg_fallback = [
        r
        for r in straight_rows
        if r["name"] not in straight_names
        and r["name"] not in {x["name"] for x in top3}
    ]
    two_leg_fallback.sort(key=lambda x: (straight_attack_rank(x), x["rank"], x["score"]), reverse=True)
    two_leg = pick_top_n(
        two_leg_fallback,
        2,
        exclude_names=straight_names | {x["name"] for x in top3},
        max_per_game=1,
        max_per_team=2,
    )

fav_pool = [
    r
    for r in rows
    if r["name"] in FAVS
    and r["name"] not in {x["name"] for x in top3}
    and r["name"] not in {x["name"] for x in two_leg}
    and r["name"] not in straight_names
    and r["split"] >= 0.0
    and r["risk"] >= 0.0
    and (r["risk"] >= 0.25 or r["split"] >= 0.50 or r["park_pct"] >= 3)
]
fav_pool.sort(key=lambda x: (straight_attack_rank(x), x["score"]), reverse=True)
fav3 = pick_top_n(
    fav_pool,
    3,
    exclude_names={x["name"] for x in top3} | {x["name"] for x in two_leg} | straight_names,
    max_per_game=2,
    max_per_team=2,
)
if len(fav3) < 3:
    fav_fallback = [
        r
        for r in rows
        if r["name"] in FAVS
        and r["name"] not in {x["name"] for x in top3}
        and r["name"] not in {x["name"] for x in two_leg}
        and r["name"] not in straight_names
        and r["split"] >= 0.0
    ]
    fav_fallback.sort(key=lambda x: (straight_attack_rank(x), x["score"]), reverse=True)
    fav3 = pick_top_n(
        fav_fallback,
        3,
        exclude_names={x["name"] for x in top3} | {x["name"] for x in two_leg} | straight_names,
        max_per_game=2,
        max_per_team=2,
    )
if len(fav3) < 3:
    fav_fill = [
        r
        for r in rows
        if r["name"] in FAVS
        and r["name"] not in {x["name"] for x in top3}
        and r["name"] not in {x["name"] for x in two_leg}
        and r["name"] not in straight_names
        and r["name"] not in {x["name"] for x in fav3}
    ]
    fav_fill.sort(key=lambda x: (straight_attack_rank(x), x["score"]), reverse=True)
    fav3.extend(
        pick_top_n(
            fav_fill,
            3 - len(fav3),
            exclude_names={x["name"] for x in top3} | {x["name"] for x in two_leg} | straight_names | {x["name"] for x in fav3},
            max_per_game=2,
            max_per_team=2,
        )
    )


def fav_leg_label(row: dict) -> str:
    return f"{row['name_plain']} HR &#11088;"


assert len(top3) == 3, "Goblin 3-leg needs 3 picks"
assert len(two_leg) == 2, "Goblin 2-leg needs 2 picks"
assert len(fav3) == 3, "Favorite 3-leg needs 3 picks"
assert not ({x["name"] for x in two_leg} & straight_names), "2 Leg HR must not reuse Straights of the Day"

top5, seen = [], set()
for r in rows:
    if r["name"] in seen:
        continue
    seen.add(r["name"])
    top5.append(r)
    if len(top5) == 5:
        break

longshots = [r for r in listed_rows if (r["odds_value"] or 0) >= 700][:4]
if len(longshots) < 4:
    extra = [r for r in listed_rows if r not in longshots]
    longshots.extend(extra[: 4 - len(longshots)])

# Hits parlay selector (max 11 legs): contact-friendly hit form; skip high-whiff batters.
for r in rows:
    recent_hit_form = (r["hr"] * 2.5) + (r["near"] * 1.5) + max(r["ev"] - 88.0, 0) * 0.6 + (r["barrel"] / 6.0)
    matchup_edge = (r["split"] * 10.0) + (r["park_pct"] * 0.10)
    whiff_penalty = 0.0
    for pct in (r.get("whiff_pct"), r.get("k_pct")):
        if pct is not None and pct >= 18.0:
            whiff_penalty = max(whiff_penalty, (pct - 17.0) * 3.0)
    if row_high_whiff(r, for_hits=True):
        whiff_penalty += 40.0
    r["hits_rank"] = recent_hit_form + matchup_edge + (r["score"] * 0.10) - whiff_penalty


def hits_base_pool(candidates: list[dict]) -> list[dict]:
    pool = [
        r
        for r in candidates
        if (r["hr"] >= 1 or r["near"] >= 1 or r["ev"] >= 90)
        and r["split"] >= -0.20
    ]
    return pool if pool else list(candidates)


def select_hits_parlay(candidates: list[dict], *, avoid_whiff: bool, n: int = 11) -> list[dict]:
    pool = hits_base_pool(candidates)
    if avoid_whiff:
        pool = [r for r in pool if not row_high_whiff(r, for_hits=True)]
    pool = sorted(pool, key=lambda x: x["hits_rank"], reverse=True)
    legs: list[dict] = []
    seen: set[str] = set()
    for r in pool:
        if r["name"] in seen:
            continue
        seen.add(r["name"])
        legs.append(r)
        if len(legs) == n:
            break
    return legs


hits_parlay_legs = select_hits_parlay(rows, avoid_whiff=True)
if len(hits_parlay_legs) < 11:
    have = {r["name"] for r in hits_parlay_legs}
    backfill_pool = sorted(
        [
            r
            for r in hits_base_pool(rows)
            if r["name"] not in have and not row_high_whiff(r, for_hits=True)
        ],
        key=lambda x: x["hits_rank"],
        reverse=True,
    )
    for r in backfill_pool:
        have.add(r["name"])
        hits_parlay_legs.append(r)
        if len(hits_parlay_legs) == 11:
            break
hits_line_a = ", ".join(r["name_plain"] for r in hits_parlay_legs[:6])
hits_line_b = ", ".join(r["name_plain"] for r in hits_parlay_legs[6:11])

weather_rows = load_weather_rows()
weather_top = sorted(weather_rows, key=lambda x: x["hr_pct"], reverse=True)[:5]
weather_fades = sorted(weather_rows, key=lambda x: x["hr_pct"])[:4]
weather_by_game = {w["game"]: w for w in weather_rows}
pitchers_attack = load_pitchers_to_attack()


def assert_game_cap(label: str, picked: list[dict], max_per_game: int = 2) -> None:
    from collections import Counter

    counts = Counter(r["game_key"] for r in picked)
    bad = {game: count for game, count in counts.items() if count > max_per_game}
    if bad:
        raise SystemExit(f"{label}: more than {max_per_game} players from same game: {bad}")


# Top 5 HR tickets: combine attackability, weather/park, and HR risk into one rank.
attack_bonus_by_pitcher = {
    p["pitcher"]: max(0.0, 5.0 - idx) * 2.0
    for idx, p in enumerate(pitchers_attack)
}
combined_ranked = []
for r in rows:
    risk_row = resolve_pitcher(PITCHER_RISK, r["chip"])
    pitcher_name = risk_row["pitcher"] if risk_row else r["chip"]
    attack_bonus = attack_bonus_by_pitcher.get(pitcher_name, 0.0)
    combined_rank = (
        (r["risk"] * 12.0)
        + (r["split"] * 10.0)
        + (r["park_pct"] * 0.60)
        + (r["hr"] * 2.8)
        + (r["near"] * 1.6)
        + (max(r["ev"] - 90.0, 0.0) * 0.35)
        + (r["score"] * 0.18)
        + attack_bonus
    )
    combined_ranked.append({**r, "combined_rank": combined_rank})

combined_ranked.sort(key=lambda r: (r["combined_rank"], r["score"]), reverse=True)
top5 = pick_top_n(combined_ranked, 5, max_per_game=2, max_per_team=2)

# Weather-heavy HR list: prioritize park/weather, distinct from Top 5, max 2 per game.
top5_names = {r["name"] for r in top5}
weather_ranked = sorted(
    rows,
    key=lambda r: (
        r["park_pct"],
        r["split"],
        r["hr"],
        r["near"],
        r["score"],
    ),
    reverse=True,
)
weather5 = pick_top_n(
    weather_ranked,
    5,
    exclude_names=top5_names,
    max_per_game=2,
    max_per_team=None,
)
assert_game_cap("Top 5 HR Tickets", top5)
assert_game_cap("Top 5 Weather Heavy HR Plays", weather5)


def weather_micro_note(row):
    w = weather_by_game.get(row["game_key"])
    net = w["hr_pct_text"] if w else f"{row['park_pct']:+d}%"
    return f'vs {row["chip"]} · net {net} · split {row["split"]:+.2f}'

THREE_LEG_HR = [f"{r['name_plain']} - Over 0.5 homerun" for r in top3]
FAV_THREE_LEG = [f"{r['name_plain']} - Over 0.5 homerun" for r in fav3]
STRAIGHT_OF_DAY = f"{straight_o05['name_plain']} - Over 0.5 homerun"
STRAIGHT_O15_DAY = f"{straight_o15['name_plain']} - Over 1.5 homeruns"
TWO_LEG_HR = [f"{r['name_plain']} - Over 0.5 homerun" for r in two_leg]

straight_o05_primary, straight_o05_form = straight_pick_why(straight_o05, leg="o05")
straight_o15_primary, straight_o15_form = straight_pick_why(straight_o15, leg="o15")

FAV_SET = (
    "            const WORST_PICKZ_FAVORITE_NAMES = new Set([\n"
    + ",\n".join(f"                {json.dumps(name)}" for name in FAVS)
    + "\n            ]);"
)

STRAIGHT_OF_DAY_CARD = f"""                <div class="summary-card full-width straight-of-day-card">
                    <h3>Worst Pickz Straights of the Day</h3>
                    <div class="straight-picks-grid">
                        <div class="straight-pick-hero">
                            <span class="straight-pick-tag">Over 0.5 HR Straight</span>
                            <div class="straight-pick-header">
                                <strong class="straight-pick-name">{straight_o05['name_plain']} &mdash; vs {straight_o05['chip']}</strong>
                                <span class="straight-pick-meta">{straight_o05['odds']} &middot; Score {straight_o05['score']} &middot; {straight_o05['game_key']}</span>
                            </div>
                            <ul class="straight-pick-factors">
                                <li><strong>Primary edge</strong><small>{straight_o05_primary}</small></li>
                                <li><strong>Why this pick</strong><small>{straight_o05_form}</small></li>
                            </ul>
                            <div class="straight-pick-actions">
                                <button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr([STRAIGHT_OF_DAY])}'>Add O0.5 Straight to Gambly</button>
                            </div>
                        </div>
                        <div class="straight-pick-hero straight-pick-hero--o15">
                            <span class="straight-pick-tag">Over 1.5 HR Straight</span>
                            <div class="straight-pick-header">
                                <strong class="straight-pick-name">{straight_o15['name_plain']} &mdash; vs {straight_o15['chip']}</strong>
                                <span class="straight-pick-meta">{straight_o15['odds']} &middot; Score {straight_o15['score']} &middot; {straight_o15['game_key']}</span>
                            </div>
                            <ul class="straight-pick-factors">
                                <li><strong>Primary edge</strong><small>{straight_o15_primary}</small></li>
                                <li><strong>Why this pick</strong><small>{straight_o15_form}</small></li>
                            </ul>
                            <div class="straight-pick-actions">
                                <button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr([STRAIGHT_O15_DAY])}'>Add O1.5 Straight to Gambly</button>
                            </div>
                        </div>
                    </div>
                </div>"""

GOBLIN_CARD = f"""                <div class="summary-card full-width best-bets-card">
                    <h3>Goblin's Insight</h3>
                    <div class="best-bets-grid">
                        <div class="best-bets-group">
                            <h4>3 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>{top3[0]['name_plain']} HR</strong><small>{compact_goblin_leg(top3[0])}</small></li>
                                <li><strong>{top3[1]['name_plain']} HR</strong><small>{compact_goblin_leg(top3[1])}</small></li>
                                <li><strong>{top3[2]['name_plain']} HR</strong><small>{compact_goblin_leg(top3[2])}</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(THREE_LEG_HR)}'>Add 3 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>2 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>{two_leg[0]['name_plain']} HR</strong><small>{compact_goblin_leg(two_leg[0])}</small></li>
                                <li><strong>{two_leg[1]['name_plain']} HR</strong><small>{compact_goblin_leg(two_leg[1])}</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(TWO_LEG_HR)}'>Add 2 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Hits Parlay</h4>
                            <ul>
                                <li><strong>{hits_line_a}</strong></li>
                                <li><strong>{hits_line_b}</strong></li>
                            </ul>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr([f"{r['name_plain']} - Over 0.5 hits" for r in hits_parlay_legs])}'>Add Hits Parlay to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Worst Pickz Favorite 3 Leg</h4>
                            <ol>
                                <li><strong>{fav_leg_label(fav3[0])}</strong><small>{compact_goblin_leg(fav3[0])}</small></li>
                                <li><strong>{fav_leg_label(fav3[1])}</strong><small>{compact_goblin_leg(fav3[1])}</small></li>
                                <li><strong>{fav_leg_label(fav3[2])}</strong><small>{compact_goblin_leg(fav3[2])}</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(FAV_THREE_LEG)}'>Add Favorite 3 Leg to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Top 5 Pitchers To Attack</h4>
                            <ol>
                                {''.join(f"<li><strong>{p['pitcher']}</strong><small>HR risk {p['risk']:.2f}; vs LHB {p['vs_lhb']}, vs RHB {p['vs_rhb']}.</small></li>" for p in pitchers_attack)}
                            </ol>
                        </div>
                    </div>
                </div>"""

TOP_CARD = """                <div class="summary-card full-width top-five-card">
                    <h3>Top 5 HR Tickets (Attack + Weather + HR Risk)</h3>
                    <div class="top-five-list">
""" + "\n".join(
    f'                        <div class="top-five-item"><span>{r["name_plain"]} <small>{r["game_key"]} vs {r["chip"]} • risk {r["risk"]:+.2f} • split {r["split"]:+.2f} • park {r["park_pct"]}%</small></span><strong>{r["score"]}</strong></div>'
    for r in top5
) + """
                    </div>
                </div>"""

PARK_INNER = "\n".join(
    f'                        <div class="summary-item"><span>{w["game"]} <small>{w["venue"]} (stadium {w["hr_stadium"]}, weather {w["hr_weather"]})</small></span><strong>{w["hr_pct_text"]}</strong></div>'
    for w in weather_top
)
WEATHER5_INNER = "\n".join(
    f'                        <div class="summary-item"><span>#{i+1} {r["name_plain"]} <small>{weather_micro_note(r)}</small></span><strong>{r["score"]}</strong></div>'
    for i, r in enumerate(weather5)
)
LONGSHOT_INNER = "\n".join(
    f'                        <div class="summary-item"><span>{r["name_plain"]} <small>{r["odds"]} vs {r["chip"]}</small></span><strong>{r["score"]}</strong></div>'
    for r in longshots
)
FADES_INNER = "\n".join(
    f'                        <div class="summary-item"><span>{w["game"]} <small>{w["venue"]}</small></span><strong>{w["hr_pct_text"]}</strong></div>'
    for w in weather_fades
)

SUMMARY_BLOCK = (
    STRAIGHT_OF_DAY_CARD
    + "\n"
    + GOBLIN_CARD
    + "\n"
    + TOP_CARD
    + """
                <div class="summary-card">
                    <h3>Top 5 Weather Games</h3>
                    <div class="summary-list">"""
    + PARK_INNER
    + """
                    </div>
                </div>
                <div class="summary-card">
                    <h3>Top 5 Weather Heavy HR Plays</h3>
                    <div class="summary-list">"""
    + WEATHER5_INNER
    + """
                    </div>
                </div>
                <div class="summary-card">
                    <h3>Best longshot HR (listed +700+)</h3>
                    <div class="summary-list">"""
    + LONGSHOT_INNER
    + """
                    </div>
                </div>
                <div class="summary-card">
                    <h3>Harsh Environment Fades</h3>
                    <div class="summary-list">"""
    + FADES_INNER
    + """
                    </div>
                </div>
"""
)


def update_manifest():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    old = {sheet["date"]: sheet for sheet in manifest.get("sheets", [])}
    ordered = [
        {"date": SHEET_DATE, "label": "June 6, 2026 — current slate", "href": "index.html"},
        {"date": "2026-06-05", "label": "June 5, 2026", "href": "archive/2026-06-05.html"},
        {"date": "2026-06-04", "label": "June 4, 2026", "href": "archive/2026-06-04.html"},
        {"date": "2026-06-01", "label": "June 1, 2026", "href": "archive/2026-06-01.html"},
        {"date": "2026-05-31", "label": "May 31, 2026", "href": "archive/2026-05-31.html"},
        {"date": "2026-05-30", "label": "May 30, 2026", "href": "archive/2026-05-30.html"},
        {"date": "2026-05-29", "label": "May 29, 2026", "href": "archive/2026-05-29.html"},
        {"date": "2026-05-28", "label": "May 28, 2026", "href": "archive/2026-05-28.html"},
        {"date": "2026-05-27", "label": "May 27, 2026", "href": "archive/2026-05-27.html"},
        {"date": "2026-05-25", "label": "May 25, 2026", "href": "archive/2026-05-25.html"},
        {"date": "2026-05-21", "label": "May 21, 2026", "href": "archive/2026-05-21.html"},
    ]
    for date in ["2026-05-20", "2026-05-19", "2026-05-18", "2026-05-16", "2026-05-15", "2026-05-14"]:
        if date in old:
            ordered.append(old[date])
    payload = {"version": 1, "sheets": ordered}
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def manifest_fallback(manifest):
    return (
        '<script type="application/json" id="sheets-manifest-fallback">'
        + json.dumps(manifest, ensure_ascii=False).replace("</", "<\\/")
        + "</script>"
    )


def patch_preview(manifest):
    text = PREVIEW.read_text(encoding="utf-8")
    games_pat = r"const games = \[.*?\];"
    if re.search(games_pat, text, flags=re.DOTALL):
        text = re.sub(games_pat, lambda _: GAMES_BLOCK, text, count=1, flags=re.DOTALL)
    else:
        insert_pat = r'\(\(\) => \{\s*\n\s*const grid = document\.getElementById\("gamesGrid"\);'
        insert_repl = "(() => {\n" + GAMES_BLOCK + '\n\n            const grid = document.getElementById("gamesGrid");'
        text, n = re.subn(insert_pat, insert_repl, text, count=1)
        if n != 1:
            raise SystemExit("Could not insert games block")

    text = re.sub(r"const WORST_PICKZ_FAVORITE_NAMES = new Set\(\[[\s\S]*?\]\);", FAV_SET, text, count=1)
    text = re.sub(r'<meta name="sheet-date" content="[^"]*">', f'<meta name="sheet-date" content="{SHEET_DATE}">', text, count=1)
    text = re.sub(
        r'<script type="application/json" id="sheets-manifest-fallback">.*?</script>',
        lambda _m: manifest_fallback(manifest),
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<p>(?:Friday|Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday), \w+ \d+, 2026 — Worst Pickz HR cheat sheet",
        "<p>Saturday, June 6, 2026 — Worst Pickz HR cheat sheet",
        text,
        count=1,
    )

    count_sentence = (
        f"This board covers <strong>{TOTAL_ROWS} listed HR props</strong> across "
        f"<strong>{TOTAL_GAMES} games</strong>, with <strong>{TOTAL_FAVS} Worst Pickz Favorite</strong> rows (&#11088;)."
    )
    text, count = re.subn(
        r"This board covers <strong>.*?</strong> across <strong>.*?</strong>, with <strong>.*?</strong> rows \((?:&#11088;|⭐)\)\.",
        count_sentence,
        text,
        count=1,
    )
    if count == 0:
        text = text.replace(
            'PropFinder Weather</a>. Designated <strong>Worst Pickz Favorites</strong>',
            f'PropFinder Weather</a>. {count_sentence} Designated <strong>Worst Pickz Favorites</strong>',
            1,
        )

    start_m = re.search(r'\s*<div class="summary-card full-width straight-of-day-card">', text)
    end_m = re.search(r'<div class="summary-card emoji-key-card">', text)
    if not start_m or not end_m or end_m.start() <= start_m.start():
        raise SystemExit("Could not locate summary block anchors")
    text = text[: start_m.start()] + SUMMARY_BLOCK + text[end_m.start() :]

    PREVIEW.write_text(text, encoding="utf-8")
    print("patched", PREVIEW.relative_to(ROOT))


def sync_root_index():
    shutil.copy2(PREVIEW, ROOT / "index.html")
    print("synced root index.html")


def main():
    import sys

    preview_date_m = re.search(
        r'<meta name="sheet-date" content="([^"]+)">',
        PREVIEW.read_text(encoding="utf-8"),
    )
    preview_date = preview_date_m.group(1) if preview_date_m else ""
    archive_date = ARCHIVE_PREVIOUS.stem
    if preview_date == archive_date:
        ARCHIVE_PREVIOUS.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PREVIEW, ARCHIVE_PREVIOUS)
        print("archived current preview to", ARCHIVE_PREVIOUS.relative_to(ROOT))
    else:
        print(
            f"skip archive copy: preview is {preview_date or 'unknown'}, "
            f"expected {archive_date} (run restore-june-archives.py if archive is stale)"
        )
    manifest = update_manifest()
    patch_preview(manifest)
    if "--sync-root" in sys.argv:
        sync_root_index()
    else:
        print("preview only (pass --sync-root to copy to index.html)")


if __name__ == "__main__":
    main()
