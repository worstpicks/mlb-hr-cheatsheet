#!/usr/bin/env python3
"""Patch preview sheet to 2026-07-29. Does not commit or push."""
from __future__ import annotations

import csv
import importlib.util
import json
import re
import shutil
from pathlib import Path

from hr_score_model import batter_split
from sheet_data import load_pitcher_risk, resolve_pitcher

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
MANIFEST_PATH = ROOT / "preview" / "sheets-manifest.json"
ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-07-27.html"
SHEET_DATE = "2026-07-29"

spec = importlib.util.spec_from_file_location("build0729", ROOT / "build-sheet-2026-07-29.py")
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
    row_hand_park_fields,
)
from note_compact import compact_goblin_leg, compact_note, compact_row_line, straight_pick_why
from goblin_hits_parlay import annotate_hits_ranks, fill_hits_parlay, select_hits_parlay
from post_patch import sync_research_tab_after_patch
from goblin_hr_zone_fit import (
    annotate_hr_zone_ranks,
    hand_park_pct,
    hr_rank_sort_key,
    o05_zone_lane_ok,
    park_gate_pct,
    top5_hr_ticket_rank,
    weather_play_rank,
)

ENRICHED_GAMES = enrich_games_list(build.games, SHEET_DATE)
GAMES_BLOCK = emit_games_js(ENRICHED_GAMES)
TOTAL_GAMES = len(build.games)
TOTAL_ROWS = sum(len(g["rows"]) for g in build.games)
ZONE_ROW_MIN = min(TOTAL_ROWS, max(45, TOTAL_ROWS - 20))
ZONE_ROW_COUNT = GAMES_BLOCK.count("zoneScore:")
if ZONE_ROW_COUNT < ZONE_ROW_MIN:
    raise SystemExit(
        f"GAMES_BLOCK missing zone data ({ZONE_ROW_COUNT} zoneScore fields; need {ZONE_ROW_MIN}+)"
    )

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
            park_fields = row_hand_park_fields(hand, park_ctx)
            hand_park = park_fields.get("hand_park_pct", park_pct)
            risk_row = resolve_pitcher(PITCHER_RISK, chip)
            if risk_row:
                split = batter_split(hand, risk_row) or 0.0
                risk = risk_row["overall"]
            else:
                split = 0.0
                risk = 0.0
            zone_score = r.get("zoneScore")
            rank = (
                r["score"]
                + split * 8.0
                + risk * 4.0
                + park_pct * 0.18
                + max(hand_park - park_pct, 0) * 0.07
                + (zone_score or 0) * 0.18
            )
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
                    "hand": hand,
                    "park_pct": park_pct,
                    **park_fields,
                    "zone_score": zone_score,
                    "zone_contact": r.get("zoneContact"),
                    "zone_barrel": r.get("zoneBarrel"),
                    "zone_hr": r.get("zoneHr"),
                    "zone_hard_hit": r.get("zoneHardHit"),
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
    """Load PropFinder ParkFactors; split same-matchup DH rows into (G1)/(G2) by Time."""
    data_dir = ROOT / "data"
    path = data_dir / f"ParkFactors_{SHEET_DATE}.csv"
    if not path.exists():
        matches = sorted(data_dir.glob(f"ParkFactors_{SHEET_DATE}*.csv"))
        if matches:
            path = matches[0]
    by_game: dict[str, list[dict]] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            game = " ".join(row["Game"].replace("  ", " ").split())
            try:
                hr_pct = int(row["HR %"].replace("%", ""))
            except ValueError:
                continue
            entry = {
                "game": game,
                "venue": row["Venue"],
                "hr_pct": hr_pct,
                "hr_pct_text": row["HR %"],
                "hr_stadium": row["HR % Stadium"],
                "hr_weather": row["HR % Weather"],
                "time": (row.get("Time") or "").strip(),
            }
            by_game.setdefault(game, []).append(entry)

    def _time_key(t: str) -> tuple[int, str]:
        m = re.match(r"^(\d{1,2}):(\d{2})", (t or "").strip())
        if not m:
            return (99_999, t or "")
        hour = int(m.group(1))
        minute = int(m.group(2))
        # PropFinder 12h clock without AM/PM: 1–11 = PM so 7:20 > 12:35.
        if 1 <= hour <= 11:
            hour += 12
        return (hour * 60 + minute, t or "")

    rows = []
    for game, entries in by_game.items():
        entries.sort(key=lambda e: _time_key(e.get("time", "")))
        if len(entries) == 1:
            rows.append(entries[0])
            continue
        for i, entry in enumerate(entries, 1):
            rows.append({**entry, "game": f"{game} (G{i})"})
    return rows


rows = collect_rows()
listed_rows = [r for r in rows if r["odds_value"] is not None]
if not listed_rows:
    listed_rows = rows
# Straights/Goblin HR legs: include N/A odds props (user list); listed-only for longshots display.
straight_rows = rows

weather_rows = load_weather_rows()


def alias_game_keys(game: str) -> list[str]:
    normalized = " ".join(game.split())
    keys = {normalized}
    # Only map bare matchup -> DH row for G1 so G2 keys stay distinct.
    m = re.match(r"^(.+ @ .+)\s*\(G(\d+)\)$", normalized)
    if m and m.group(2) == "1":
        keys.add(m.group(1))
    for old, new in (("CHW @", "CWS @"), ("CWS @", "CHW @"), ("WAS @", "WSH @"), ("WSH @", "WAS @")):
        if old in normalized:
            keys.add(normalized.replace(old, new, 1))
            if m and m.group(2) == "1":
                keys.add(m.group(1).replace(old, new, 1))
    return list(keys)


weather_by_game: dict[str, dict] = {}
for w in weather_rows:
    game = " ".join(w["game"].split())
    w = {**w, "game": game}
    for key in alias_game_keys(game):
        weather_by_game[key] = w


def effective_park_pct(row: dict) -> int:
    gk = row["game_key"]
    w = weather_by_game.get(gk)
    if w is None:
        base = re.sub(r"\s*\(G\d+\)$", "", gk)
        w = weather_by_game.get(base)
    return w["hr_pct"] if w else row["park_pct"]


def effective_hand_park_pct(row: dict) -> int:
    return hand_park_pct(row, park_pct_fn=effective_park_pct)


annotate_hr_zone_ranks(rows, park_pct_fn=effective_park_pct)

# O0.5 straight: zone fit + attackable pitcher lane + park/weather support.
def pick_top_n(
    ranked: list[dict],
    n: int,
    *,
    exclude_names: set[str] | None = None,
    max_per_game: int = 2,
    max_per_team: int | None = 2,
    already: list[dict] | None = None,
) -> list[dict]:
    """Pick top rows with at most max_per_game from the same game (and team when set)."""
    exclude_names = exclude_names or set()
    picked: list[dict] = list(already or [])
    seen: set[str] = {r["name"] for r in picked}
    game_counts: dict[str, int] = {}
    team_counts: dict[str, int] = {}
    for r in picked:
        game_counts[r["game_key"]] = game_counts.get(r["game_key"], 0) + 1
        if max_per_team is not None and r.get("team"):
            team_counts[r["team"]] = team_counts.get(r["team"], 0) + 1

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
            and (
                r["risk"] >= 0.50
                or r["park_pct"] >= 3
                or r.get("hand_park_pct", 0) >= 6
                or r["split"] >= 0.75
            )
            and (r["hr"] >= 1 or r["near"] >= 3)
            and o05_zone_lane_ok(r)
        ]
    pool.sort(key=hr_rank_sort_key, reverse=True)
    return pool


o15_candidates = [
    r
    for r in straight_rows
    if r["name"] not in STRAIGHT_O15_BLOCKLIST
    and r["hr"] >= 2
    and r["near"] >= 2
    and r["score"] >= 78
    and r["split"] >= 0.0
    and not (r["split"] <= 0.0 and r["risk"] <= 0.0)
    and (r["split"] >= 0.15 or r["risk"] >= 0.25 or r["split"] >= 0.75)
    and (
        r["risk"] >= 0.25
        or park_gate_pct(r, park_pct_fn=effective_park_pct) >= 3
        or r.get("hand_park_pct", 0) >= 6
        or r["split"] >= 0.75
    )
]
o15_candidates.sort(key=lambda r: (r["multi_hr_rank"], r["hr_zone_fit"], r["score"]), reverse=True)

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
    straight_o15 = o15_candidates[0] if o15_candidates else None
    if straight_o15 is None:
        o15_relaxed = sorted(
            [
                r
                for r in straight_rows
                if r["name"] not in STRAIGHT_O15_BLOCKLIST
                and r["hr"] >= 2
                and r["near"] >= 2
                and r["score"] >= 78
                and r["split"] >= 0.15
                and not (r["split"] <= 0.0 and r["risk"] <= 0.0)
            ],
            key=lambda r: (r["multi_hr_rank"], r["hr_zone_fit"], r["score"]),
            reverse=True,
        )
        straight_o15 = o15_relaxed[0] if o15_relaxed else straight_rows[0]
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

# 6/22 judgment: O0.5 + O1.5 from best attack lanes after initial pool pick.
rows_by_plain_early = {r["name_plain"]: r for r in rows}


def row_is_favorite(row: dict) -> bool:
    # Prefer row emoji so DH props can be ⭐ in G1 and 💎 in G2 under the same name.
    em = row.get("emojis") or ""
    if "⭐" in em:
        return True
    if "💎" in em:
        return False
    return row["name"] in FAVS


def available_fav_count(exclude_names: set[str]) -> int:
    return sum(1 for r in rows if row_is_favorite(r) and r["name"] not in exclude_names)


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

straight_names = {straight_o05["name"], straight_o15["name"]}


# Goblin HR legs: real form plus a usable opposing split/risk lane (reject 0/0 pitcher data).
def goblin_hr_leg_ok(row: dict) -> bool:
    if row["hr"] < 1 and row["near"] < 2:
        return False
    if row["split"] <= 0.0 and row["risk"] <= 0.0:
        return False
    if row["split"] > 0.0:
        return True
    return (
        row["risk"] >= 0.25
        or park_gate_pct(row, park_pct_fn=effective_park_pct) >= 3
        or row.get("hand_park_pct", 0) >= 6
    )


def goblin_top3_ok(row: dict) -> bool:
    """3-leg parlay: require a real platoon edge, not just park carry on a negative split."""
    if not goblin_hr_leg_ok(row):
        return False
    if row["split"] >= 0.15:
        return True
    if row["split"] >= 0.0 and row["risk"] >= 0.50:
        return True
    return False


def summary_ticket_ok(row: dict) -> bool:
    """Top 5 HR tickets: loud form plus a usable opposing lane."""
    if row["split"] < -0.10:
        return False
    if row["split"] <= 0.0 and row["risk"] <= 0.0:
        return False
    park = park_gate_pct(row, park_pct_fn=effective_park_pct)
    hand_park = effective_hand_park_pct(row)
    if park < -5 and hand_park < -3 and row["split"] < 0.50:
        return False
    return goblin_hr_leg_ok(row) or (row["score"] >= 80 and row["split"] >= 0.0)


def weather_play_ok(row: dict) -> bool:
    """Weather-heavy plays: park/weather boost is a primary edge."""
    park = park_gate_pct(row, park_pct_fn=effective_park_pct)
    hand_park = effective_hand_park_pct(row)
    if park < 5 and hand_park < 6:
        return False
    if row["split"] == 0.0 and row["risk"] == 0.0:
        return False

    has_form = row["hr"] >= 1 or row["near"] >= 2 or row["score"] >= 75

    # Positive split + usable platoon at a boosted park.
    if row["split"] >= 0.0:
        if park >= 20 and row["split"] >= 0.50:
            return has_form or row["score"] >= 65
        has_platoon = row["split"] >= 0.15 or row["risk"] >= 0.35
        if has_form and has_platoon:
            return True
        if park >= 8 and row["risk"] >= 1.0 and has_form:
            return True

    # Wind-out spots: near-neutral split with loud form.
    if park >= 8 and row["split"] >= -0.10 and row["score"] >= 82 and has_form:
        return True

    # Extreme park carry (+35%+): environment leads even when SP split fights it.
    if park >= 35 and row["score"] >= 75 and has_form:
        return True

    # Coors-grade net park (+28%+): playable form even with slight split drag.
    if park >= 28 and row["split"] >= -0.30 and row["score"] >= 68 and has_form:
        return True

    return False


def longshot_ok(row: dict) -> bool:
    if (row["odds_value"] or 0) < 700:
        return False
    if row["split"] < -0.15:
        return False
    if row["split"] >= 0.0:
        return goblin_hr_leg_ok(row) or (
            row["split"] >= 0.50
            and row["risk"] >= 0.50
            and (row["hr"] >= 1 or row["near"] >= 2)
        )
    return row["split"] >= -0.10 and row["score"] >= 72 and (row["hr"] >= 1 or row["near"] >= 1)


top3_pool = [
    r for r in straight_rows if r["name"] not in straight_names and goblin_top3_ok(r)
]
top3_pool.sort(key=hr_rank_sort_key, reverse=True)

fav_reserve = sorted(
    [
        r
        for r in rows
        if r["name"] in FAVS
        and r["name"] not in straight_names
    ],
    key=lambda x: (x["straight_attack_rank"], x["hr_zone_fit"], x["score"]),
    reverse=True,
)[:3]
reserved_fav_names = {r["name"] for r in fav_reserve}

top3_pool_reserved = [r for r in top3_pool if r["name"] not in reserved_fav_names]
top3 = pick_top_n(top3_pool_reserved, 3, exclude_names=straight_names, max_per_game=2, max_per_team=2)
# Keep reserved ⭐ out of Goblin 3-leg so Favorite 3-leg can fill on thin boards.
_top3_ex = straight_names | reserved_fav_names
if len(top3) < 3:
    top3 = pick_top_n(top3_pool, 3, exclude_names=_top3_ex, max_per_game=2, max_per_team=2)
if len(top3) < 3:
    extra = sorted(
        [r for r in straight_rows if r["name"] not in _top3_ex and goblin_top3_ok(r)],
        key=hr_rank_sort_key,
        reverse=True,
    )
    top3 = pick_top_n(extra, 3, exclude_names=_top3_ex, max_per_game=2, max_per_team=2)
if len(top3) < 3:
    extra_relaxed = sorted(
        [r for r in straight_rows if r["name"] not in _top3_ex and goblin_hr_leg_ok(r)],
        key=hr_rank_sort_key,
        reverse=True,
    )
    top3 = pick_top_n(extra_relaxed, 3, exclude_names=_top3_ex, max_per_game=2, max_per_team=2)
# Last resort only: allow dipping into reserved favs if the board cannot fill otherwise.
if len(top3) < 3:
    top3 = pick_top_n(top3_pool, 3, exclude_names=straight_names, max_per_game=2, max_per_team=2)
if len(top3) < 3 and len(rows) <= 30:
    thin_top3 = sorted(
        [
            r
            for r in straight_rows
            if r["name"] not in straight_names
            and r["name"] not in {x["name"] for x in top3}
            and (r["hr"] >= 1 or r["near"] >= 2)
            and r["score"] >= 70
        ],
        key=hr_rank_sort_key,
        reverse=True,
    )
    top3.extend(
        pick_top_n(
            thin_top3,
            3 - len(top3),
            exclude_names=straight_names | {x["name"] for x in top3},
            max_per_game=2,
            max_per_team=3,
        )
    )

two_leg_pool = [
    r
    for r in straight_rows
    if r["name"] not in straight_names
    and r["name"] not in {x["name"] for x in top3}
    and r["name"] not in FAVS
    and goblin_top3_ok(r)
]
two_leg_pool.sort(key=hr_rank_sort_key, reverse=True)
two_leg = pick_top_n(
    two_leg_pool,
    2,
    exclude_names=straight_names | {x["name"] for x in top3},
    max_per_game=1,
    max_per_team=2,
)
if len(two_leg) < 2:
    two_leg_fallback = sorted(
        [
            r
            for r in straight_rows
            if r["name"] not in straight_names
            and r["name"] not in {x["name"] for x in top3}
            and r["name"] not in FAVS
            and goblin_hr_leg_ok(r)
        ],
        key=hr_rank_sort_key,
        reverse=True,
    )
    two_leg = pick_top_n(
        two_leg_fallback,
        2,
        exclude_names=straight_names | {x["name"] for x in top3},
        max_per_game=1,
        max_per_team=2,
    )
if len(two_leg) < 2:
    two_leg_fallback = sorted(
        [
            r
            for r in straight_rows
            if r["name"] not in straight_names
            and r["name"] not in {x["name"] for x in top3}
            and r["name"] not in FAVS
        ],
        key=hr_rank_sort_key,
        reverse=True,
    )
    two_leg = pick_top_n(
        two_leg_fallback,
        2,
        exclude_names=straight_names | {x["name"] for x in top3},
        max_per_game=1,
        max_per_team=2,
    )
if len(two_leg) < 2 and len(rows) <= 30:
    thin_two = sorted(
        [
            r
            for r in straight_rows
            if r["name"] not in straight_names
            and r["name"] not in {x["name"] for x in top3}
            and r["name"] not in FAVS
            and r["name"] not in {x["name"] for x in two_leg}
            and (r["hr"] >= 1 or r["near"] >= 2)
        ],
        key=hr_rank_sort_key,
        reverse=True,
    )
    two_leg.extend(
        pick_top_n(
            thin_two,
            2 - len(two_leg),
            exclude_names=straight_names | {x["name"] for x in top3} | {x["name"] for x in two_leg},
            max_per_game=1,
            max_per_team=3,
        )
    )

def fav_lane_ok(row: dict) -> bool:
    """Favorites: positive platoon preferred; allow slight negative split vs bum arms."""
    if row["split"] >= 0.0:
        return True
    return row["risk"] >= 1.0 and row["split"] >= -0.30


def fav3_lane_ok(row: dict) -> bool:
    """Favorite 3-leg: no harsh negative platoon (e.g. Colt Keith -1.01 vs Lambert)."""
    # Thin-slate: allow slight negative split when recent HR form is loud.
    if row["split"] >= -0.05 and (row["hr"] >= 2 or (row["hr"] >= 1 and row["near"] >= 2)):
        pass
    elif not fav_lane_ok(row):
        return False
    park = park_gate_pct(row, park_pct_fn=effective_park_pct)
    if row["split"] < -0.15:
        if not (row["risk"] >= 0.50 and park >= 10):
            return False
    has_form = row["hr"] >= 1 or row["near"] >= 2
    # Elite platoon + risk can carry a near-miss form day (e.g. Muncy vs Pfaadt).
    if not has_form and row["near"] >= 1 and row["split"] >= 1.0 and row["risk"] >= 0.70:
        has_form = True
    if not has_form and not (row["risk"] >= 1.0 and row["near"] >= 1):
        return False
    return True


def fav_secondary_lane_ok(row: dict) -> bool:
    """Favorites with loud HR form can qualify even without a huge platoon edge."""
    park = park_gate_pct(row, park_pct_fn=effective_park_pct)
    hand_park = effective_hand_park_pct(row)
    if row["score"] >= 88 and row["hr"] >= 2 and row["split"] >= -0.20:
        return True
    if row["risk"] >= 0.25 or row["split"] >= 0.50 or park >= 3 or hand_park >= 6:
        return True
    return False


fav_pool = [
    r
    for r in rows
    if r["name"] in FAVS
    and r["name"] not in {x["name"] for x in top3}
    and r["name"] not in {x["name"] for x in two_leg}
    and r["name"] not in straight_names
    and fav3_lane_ok(r)
    and (r["risk"] >= 0.0 or r["split"] >= 0.50)
    and fav_secondary_lane_ok(r)
]
fav_pool.sort(key=lambda x: (x["straight_attack_rank"], x["hr_zone_fit"], x["score"]), reverse=True)
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
        and fav3_lane_ok(r)
        and (r["risk"] >= 0.0 or r["split"] >= 0.50)
    ]
    fav_fallback.sort(key=lambda x: (x["straight_attack_rank"], x["hr_zone_fit"], x["score"]), reverse=True)
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
        and fav3_lane_ok(r)
        and (r["risk"] >= 0.0 or r["split"] >= 0.50)
    ]
    fav_fill.sort(key=lambda x: (x["straight_attack_rank"], x["hr_zone_fit"], x["score"]), reverse=True)
    fav3.extend(
        pick_top_n(
            fav_fill,
            3 - len(fav3),
            exclude_names={x["name"] for x in top3} | {x["name"] for x in two_leg} | straight_names | {x["name"] for x in fav3},
            max_per_game=2,
            max_per_team=2,
        )
    )
if len(fav3) < 3:
    fav_last = sorted(
        [
            r
            for r in rows
            if r["name"] in FAVS
            and r["name"] not in {x["name"] for x in top3}
            and r["name"] not in {x["name"] for x in two_leg}
            and r["name"] not in straight_names
            and r["name"] not in {x["name"] for x in fav3}
            and fav3_lane_ok(r)
        ],
        key=lambda x: (x["straight_attack_rank"], x["hr_zone_fit"], x["score"]),
        reverse=True,
    )
    fav3.extend(
        pick_top_n(
            fav_last,
            3 - len(fav3),
            exclude_names={x["name"] for x in top3} | {x["name"] for x in two_leg} | straight_names | {x["name"] for x in fav3},
            max_per_game=2,
            max_per_team=2,
        )
    )
if len(fav3) < 3 and len(rows) <= 30:
    fav_thin = sorted(
        [
            r
            for r in rows
            if r["name"] in FAVS
            and r["name"] not in {x["name"] for x in top3}
            and r["name"] not in {x["name"] for x in two_leg}
            and r["name"] not in straight_names
            and r["name"] not in {x["name"] for x in fav3}
        ],
        key=lambda x: (x["straight_attack_rank"], x["hr_zone_fit"], x["score"]),
        reverse=True,
    )
    fav3.extend(
        pick_top_n(
            fav_thin,
            3 - len(fav3),
            exclude_names={x["name"] for x in top3} | {x["name"] for x in two_leg} | straight_names | {x["name"] for x in fav3},
            max_per_game=2,
            max_per_team=3,
        )
    )

rows_by_plain = {r["name_plain"]: r for r in rows}

# 7/21 Fav3: data-driven from user ⭐ (straights excluded upstream).


def fav_leg_label(row: dict) -> str:
    return f"{row['name_plain']} HR &#11088;"


assert len(top3) == 3, "Goblin 3-leg needs 3 picks"
assert len(two_leg) == 2, "Goblin 2-leg needs 2 picks"
assert len(fav3) == 3, "Favorite 3-leg needs 3 picks"
assert not ({x["name"] for x in two_leg} & straight_names), "2 Leg HR must not reuse Straights of the Day"

# Hits parlay selector (max 11 legs): BIP% + zone fit first, contact form second.
annotate_hits_ranks(rows, row_high_whiff=row_high_whiff, sheet_date=SHEET_DATE)

hits_parlay_legs = select_hits_parlay(rows, row_high_whiff=row_high_whiff, avoid_whiff=True)
hits_parlay_legs = fill_hits_parlay(rows, hits_parlay_legs, row_high_whiff=row_high_whiff)
hits_line_a = ", ".join(r["name_plain"] for r in hits_parlay_legs[:6])
hits_line_b = ", ".join(r["name_plain"] for r in hits_parlay_legs[6:11])

pitchers_attack = load_pitchers_to_attack()

weather_top = sorted(weather_rows, key=lambda x: x["hr_pct"], reverse=True)[:5]
weather_fades = sorted([w for w in weather_rows if w["hr_pct"] < 0], key=lambda x: x["hr_pct"])[:4]


def assert_game_cap(label: str, picked: list[dict], max_per_game: int = 2) -> None:
    from collections import Counter

    counts = Counter(r["game_key"] for r in picked)
    bad = {game: count for game, count in counts.items() if count > max_per_game}
    if bad:
        raise SystemExit(f"{label}: more than {max_per_game} players from same game: {bad}")


# Top 5 HR tickets: Split + Risk + Park + Form + Zone (goblin_hr_zone_fit.top5_hr_ticket_rank).
combined_ranked = []
for r in rows:
    if not summary_ticket_ok(r):
        continue
    combined_ranked.append(
        {
            **r,
            "combined_rank": top5_hr_ticket_rank(r, park_pct_fn=effective_park_pct),
        }
    )

if len(combined_ranked) < 5:
    for r in rows:
        if r["split"] < -0.10 or (r["split"] <= 0.0 and r["risk"] <= 0.0):
            continue
        if any(x["name"] == r["name"] for x in combined_ranked):
            continue
        combined_ranked.append(
            {
                **r,
                "combined_rank": top5_hr_ticket_rank(r, park_pct_fn=effective_park_pct),
            }
        )

combined_ranked.sort(
    key=lambda r: (r["combined_rank"], r["hr_zone_fit"], r.get("top5_ticket_rank", 0)),
    reverse=True,
)
top5_target = min(5, len(rows))
top5_quality = [r for r in rows if summary_ticket_ok(r)]
top5_candidates = sorted(
    top5_quality,
    key=lambda r: top5_hr_ticket_rank(r, park_pct_fn=effective_park_pct),
    reverse=True,
)
top5 = pick_top_n(top5_candidates, top5_target, max_per_game=2, max_per_team=2)
if len(top5) < top5_target:
    have = {r["name"] for r in top5}
    # Soft fill: reject harsh negative splits, prefer usable lanes.
    soft = sorted(
        [
            r
            for r in rows
            if r["name"] not in have
            and r["split"] >= -0.10
            and not (r["split"] <= 0.0 and r["risk"] <= 0.0)
        ],
        key=lambda r: top5_hr_ticket_rank(r, park_pct_fn=effective_park_pct),
        reverse=True,
    )
    top5 = pick_top_n(
        soft,
        top5_target,
        exclude_names=have,
        max_per_game=2,
        max_per_team=2,
        already=top5,
    )
top5_target = min(5, max(len(top5_quality), len(top5)))
top5 = top5[:5]

# Weather-heavy HR list: park boost + positive split + form; distinct from Top 5.
top5_names = {r["name"] for r in top5}
weather_primary = [r for r in rows if r["name"] not in top5_names and weather_play_ok(r)]
weather_relaxed = [
    r
    for r in rows
    if r["name"] not in top5_names
    and effective_park_pct(r) >= 5
    and r["split"] >= 0.15
    and not (r["split"] <= 0.0 and r["risk"] <= 0.0)
    and (r["hr"] >= 1 or r["near"] >= 1)
]
weather_fill = [
    r
    for r in rows
    if r["name"] not in top5_names
    and effective_park_pct(r) >= 10
    and r["split"] >= 0.0
    and not (r["split"] <= 0.0 and r["risk"] <= 0.0)
    and r["score"] >= 75
]
weather_merged: dict[str, dict] = {}
for r in weather_primary + weather_relaxed + weather_fill:
    weather_merged.setdefault(r["name"], r)
weather_candidates = sorted(
    [r for r in weather_merged.values() if weather_play_ok(r)],
    key=lambda r: (
        weather_play_rank(r, park_pct_fn=effective_park_pct),
        r["hr_zone_fit"],
        r["score"],
        r["risk"],
    ),
    reverse=True,
)
boosted_weather_games = {r["game_key"] for r in weather_merged.values() if effective_park_pct(r) >= 5}
extreme_weather_games = {r["game_key"] for r in weather_merged.values() if effective_park_pct(r) >= 20}
coors_slate = any(effective_park_pct(r) >= 28 for r in weather_merged.values())
if len(extreme_weather_games) == 1:
    weather_max_per_game = 5
elif coors_slate or len(boosted_weather_games) <= 2:
    weather_max_per_game = 3
else:
    weather_max_per_game = 2
weather5 = pick_top_n(
    weather_candidates,
    5,
    exclude_names=top5_names,
    max_per_game=weather_max_per_game,
    max_per_team=None,
)
if len(weather5) < 5:
    have = {r["name"] for r in weather5}
    fill_pool = sorted(
        weather_merged.values(),
        key=lambda r: (
            weather_play_rank(r, park_pct_fn=effective_park_pct),
            r["hr_zone_fit"],
            r["score"],
        ),
        reverse=True,
    )
    for r in fill_pool:
        if r["name"] in have or r["name"] in top5_names:
            continue
        if not weather_play_ok(r):
            continue
        game_count = sum(1 for x in weather5 if x["game_key"] == r["game_key"])
        if game_count >= weather_max_per_game:
            continue
        weather5.append(r)
        have.add(r["name"])
        if len(weather5) == 5:
            break

longshot_pool = [r for r in listed_rows if longshot_ok(r)]
longshot_pool.sort(key=lambda r: (r["straight_attack_rank"], r["hr_zone_fit"]), reverse=True)
longshots = pick_top_n(longshot_pool, 4, max_per_game=2, max_per_team=2)
if len(longshots) < 1:
    thin_long = sorted(
        [
            r
            for r in listed_rows
            if (r["odds_value"] or 0) >= 700
            and (r["hr"] >= 1 or r["near"] >= 2)
            and r["split"] >= -0.10
        ],
        key=hr_rank_sort_key,
        reverse=True,
    )
    longshots = pick_top_n(thin_long, min(4, len(thin_long)), max_per_game=2, max_per_team=2)
if len(longshots) < 4:
    have = {x["name"] for x in longshots}
    longshot_fallback = sorted(
        [
            r
            for r in listed_rows
            if (r["odds_value"] or 0) >= 700
            and r["split"] >= 0.0
            and r["name"] not in have
        ],
        key=lambda r: (r["straight_attack_rank"], r["hr_zone_fit"]),
        reverse=True,
    )
    longshots.extend(
        pick_top_n(
            longshot_fallback,
            4 - len(longshots),
            exclude_names=have,
            max_per_game=2,
            max_per_team=2,
        )
    )
assert_game_cap("Top 5 HR Tickets", top5)
assert_game_cap("Top 5 Weather Heavy HR Plays", weather5, max_per_game=weather_max_per_game)


def weather_micro_note(row):
    w = weather_by_game.get(row["game_key"])
    net = w["hr_pct_text"] if w else f"{row['park_pct']:+d}%"
    park = effective_park_pct(row)
    hand_park = effective_hand_park_pct(row)
    hand = row.get("hand", "R")
    hand_tag = "LHB" if hand == "L" else "RHB"
    if hand_park != park and abs(hand_park - park) >= 3:
        net = f"{net} · {hand_tag} {hand_park:+d}%"
    if park >= 35 and row["split"] < 0.15:
        return f'vs {row["chip"]} · net {net} · park-first carry'
    if park >= 28 and row["split"] < 0.15:
        return f'vs {row["chip"]} · net {net} · Coors carry'
    if park >= 8 and -0.10 <= row["split"] < 0.15:
        return f'vs {row["chip"]} · net {net} · wind-out form'
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
                    <h3>Top 5 HR Tickets (Split + Risk + Park + Form + Zone)</h3>
                    <div class="top-five-list">
""" + "\n".join(
    f'                        <div class="top-five-item"><span>{r["name_plain"]} <small>{r["game_key"]} vs {r["chip"]} • risk {r["risk"]:+.2f} • split {r["split"]:+.2f} • park {effective_hand_park_pct(r)}%</small></span><strong>{r["score"]}</strong></div>'
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
    # Promote prior current slate into archive entry.
    if "2026-07-27" in old or (ARCHIVE_PREVIOUS.is_file()):
        old["2026-07-27"] = {
            "date": "2026-07-27",
            "label": "July 27, 2026",
            "href": "archive/2026-07-27.html",
        }
    ordered = [
        {"date": SHEET_DATE, "label": "July 29, 2026 — current slate", "href": "index.html"},
    ]
    for date in [
        "2026-07-27",
        "2026-07-26",
        "2026-07-25",
        "2026-07-24",
        "2026-07-22",
        "2026-07-21",
        "2026-07-20",
        "2026-07-19",
        "2026-07-18",
        "2026-07-17",
        "2026-07-16",
        "2026-07-14",
        "2026-07-11",
        "2026-07-10",
        "2026-07-07",
        "2026-07-06",
        "2026-07-03",
        "2026-07-02",
        "2026-07-01",
        "2026-06-29",
        "2026-06-28",
        "2026-06-27",
        "2026-06-26",
        "2026-06-25",
        "2026-06-24",
        "2026-06-23",
        "2026-06-22",
        "2026-06-20",
        "2026-06-19",
        "2026-06-18",
        "2026-06-17",
        "2026-06-16",
        "2026-06-15",
        "2026-06-14",
        "2026-06-13",
        "2026-06-12",
        "2026-06-09",
        "2026-06-08",
        "2026-06-06",
        "2026-06-05",
        "2026-06-04",
        "2026-06-01",
        "2026-05-31",
        "2026-05-30",
        "2026-05-29",
        "2026-05-28",
        "2026-05-27",
        "2026-05-25",
        "2026-05-21",
        "2026-05-20",
        "2026-05-19",
        "2026-05-18",
        "2026-05-16",
        "2026-05-15",
        "2026-05-14",
    ]:
        if date in old and date != SHEET_DATE:
            ordered.append(old[date])
        elif date == "2026-07-27":
            ordered.append(
                {
                    "date": "2026-07-27",
                    "label": "July 27, 2026",
                    "href": "archive/2026-07-27.html",
                }
            )
        elif date == "2026-07-26":
            ordered.append(
                {
                    "date": "2026-07-26",
                    "label": "July 26, 2026",
                    "href": "archive/2026-07-26.html",
                }
            )
        elif date == "2026-07-25":
            ordered.append(
                {
                    "date": "2026-07-25",
                    "label": "July 25, 2026",
                    "href": "archive/2026-07-25.html",
                }
            )
        elif date == "2026-07-24":
            ordered.append(
                {
                    "date": "2026-07-24",
                    "label": "July 24, 2026",
                    "href": "archive/2026-07-24.html",
                }
            )
        elif date == "2026-07-22":
            ordered.append(
                {
                    "date": "2026-07-22",
                    "label": "July 22, 2026",
                    "href": "archive/2026-07-22.html",
                }
            )
        elif date == "2026-07-21":
            ordered.append(
                {
                    "date": "2026-07-21",
                    "label": "July 21, 2026",
                    "href": "archive/2026-07-21.html",
                }
            )
        elif date == "2026-07-20":
            ordered.append(
                {
                    "date": "2026-07-20",
                    "label": "July 20, 2026",
                    "href": "archive/2026-07-20.html",
                }
            )
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
    # Match games block until closing `];` before gamesGrid init (non-greedy `.*?` breaks on `];` in notes).
    games_pat = r"const games = \[.*?\n\];\n\n            const grid = document\.getElementById\(\"gamesGrid\"\);"
    if re.search(games_pat, text, flags=re.DOTALL):
        repl = GAMES_BLOCK.rstrip() + '\n\n            const grid = document.getElementById("gamesGrid");'
        text = re.sub(games_pat, lambda _: repl, text, count=1, flags=re.DOTALL)
    else:
        games_pat_loose = r"const games = \[.*?\];"
        if re.search(games_pat_loose, text, flags=re.DOTALL):
            text = re.sub(games_pat_loose, lambda _: GAMES_BLOCK, text, count=1, flags=re.DOTALL)
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
        r"<p>(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday), \w+ \d+, 2026 — Worst Pickz HR cheat sheet",
        "<p>Wednesday, July 29, 2026 — Worst Pickz HR cheat sheet",
        text,
        count=1,
    )

    count_sentence = (
        f"This board covers <strong>{TOTAL_ROWS} listed HR props</strong> across "
        f"<strong>{TOTAL_GAMES} games</strong>, with <strong>{TOTAL_FAVS} Worst Pickz Favorite</strong> rows (&#11088;)."
    )
    gem_count = len(build.GEMS)
    count_sentence_gems = (
        f"This board covers <strong>{TOTAL_ROWS} listed HR props</strong> across "
        f"<strong>{TOTAL_GAMES} games</strong>, with <strong>{TOTAL_FAVS} Worst Pickz Favorite</strong> rows (&#11088;) "
        f"and <strong>{gem_count} Worst Pickz Hidden Gemz</strong> (&#128142;)."
    )
    text, count = re.subn(
        r"This board covers <strong>.*?</strong> across <strong>.*?</strong>, with <strong>.*?</strong> rows \((?:&#11088;|⭐)\)(?: and <strong>.*?</strong> \(&#128142;\))?\.?",
        count_sentence_gems,
        text,
        count=1,
    )
    if count == 0:
        text, count = re.subn(
            r"This board covers <strong>.*?</strong> across <strong>.*?</strong>, with <strong>.*?</strong> rows \((?:&#11088;|⭐)\)\.",
            count_sentence,
            text,
            count=1,
        )
    if count == 0:
        text = text.replace(
            'PropFinder Weather</a>. Designated <strong>Worst Pickz Favorites</strong>',
            f'PropFinder Weather</a>. {count_sentence_gems} Designated <strong>Worst Pickz Favorites</strong>',
            1,
        )
        if f"This board covers <strong>{TOTAL_ROWS} listed HR props</strong>" not in text:
            text = text.replace(
                'PropFinder Weather</a>. This board covers',
                f'PropFinder Weather</a>. {count_sentence_gems}',
                1,
            )

    start_m = re.search(r'\s*<div class="summary-card full-width straight-of-day-card">', text)
    end_m = re.search(r'<div class="summary-card emoji-key-card">', text)
    if not start_m or not end_m or end_m.start() <= start_m.start():
        raise SystemExit("Could not locate summary block anchors")
    text = text[: start_m.start()] + SUMMARY_BLOCK + text[end_m.start() :]

    zone_written = len(re.findall(r"zoneScore:\s*[\d.]+", text))
    if zone_written < ZONE_ROW_MIN:
        raise SystemExit(
            f"patch would write preview without zone data ({zone_written} zoneScore fields)"
        )
    PREVIEW.write_text(text, encoding="utf-8")
    print("patched", PREVIEW.relative_to(ROOT), f"({zone_written} zone rows)")


def apply_hidden_gem_ui():
    """Blue border + badge for sheet-designated Hidden Gemz rows."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("gemui", ROOT / "patch-hidden-gem-ui.py")
    gemui = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gemui)
    text = PREVIEW.read_text(encoding="utf-8")
    PREVIEW.write_text(gemui.patch(text, sheet_date=SHEET_DATE), encoding="utf-8")
    print("applied hidden gem UI styling")


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
    apply_hidden_gem_ui()
    sync_research_tab_after_patch(SHEET_DATE)
    if "--sync-root" in sys.argv:
        sync_root_index()
    else:
        print("preview only (pass --sync-root to copy to index.html)")


if __name__ == "__main__":
    main()
