"""Assemble the NHL Research slate JSON: NHL schedule + per-game aggregates.

A hockey slate is a DATE, not a week, so this writes one file per day:
    preview/data/nhl-research-2026-09-29.json
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from nhl_research.nhl_api import fetch_day_games, fetch_records, season_bounds
from nhl_research.nhl_stats import (
    GOALIE_KEYS,
    POSITIONS,
    SKATER_KEYS,
    build_aggregates,
    build_goalie_rows,
    build_rows,
    current_team_lookup,
    league_averages,
    rating_scales,
)
from nhl_research.odds_api import fetch_props, normalize_name
from nhl_research.shot_quality import load_shots, merge_into_goalies, merge_into_rows

OUT_DIR = Path(__file__).resolve().parent.parent / "preview" / "data"


def season_id_for(date: str) -> int:
    """The NHL season a date belongs to, as the API numbers it (20262027)."""
    year, month = int(date[:4]), int(date[5:7])
    start = year if month >= 7 else year - 1
    return int(f"{start}{start + 1}")


def resolve_stats_season(schedule_season: int) -> tuple[int, list, list]:
    """Use the schedule season's games if any are played, else fall back a year.

    Mirrors the NFL tab: on opening night this season has no rows, so the board
    would be empty. Last season's production is what everyone is actually
    betting off in October.
    """
    for season in (schedule_season, schedule_season - 10001):
        rows = build_rows(season)
        if rows:
            return season, rows, build_goalie_rows(season)
    raise RuntimeError(f"No NHL stats for {schedule_season} or the season before")


def build_slate(date: str) -> dict:
    games = fetch_day_games(date)
    schedule_season = season_id_for(date)
    stats_season, rows, goalie_rows = resolve_stats_season(schedule_season)
    if stats_season != schedule_season:
        print(f"[nhl-research] {schedule_season} has no games played yet; "
              f"reading {stats_season}")

    # iFF / iSCF are the heart of the rating model's shot-quality component and
    # live only in the play-by-play, so they are folded onto each player-game
    # before anything aggregates. Cached, so this costs one crawl per season.
    game_ids = sorted({r["game_id"] for r in rows})
    shots = load_shots(stats_season, game_ids)
    merged = merge_into_rows(rows, shots)
    merged_g = merge_into_goalies(goalie_rows, shots)
    print(f"[nhl-research] shot quality merged into {merged} skater-games "
          f"and {merged_g} goalie-games")

    # Stats come from whatever season is finished; the uniform comes from this
    # one. Without the second half every summer move is invisible.
    current_teams = current_team_lookup(schedule_season)
    if not current_teams:
        print(f"[nhl-research] WARN no {schedule_season} roster published; "
              f"players stay on their {stats_season} clubs")

    players, allowed = build_aggregates(rows, current_teams, season_id=schedule_season)
    goalies, goalies_allowed = build_aggregates(
        goalie_rows, current_teams, season_id=schedule_season, keys=GOALIE_KEYS,
    )
    # Goalies ride in the same per-team bucket under "G".
    for team, bucket in goalies.items():
        players.setdefault(team, {})["G"] = bucket.get("G", [])
    for team, bucket in goalies_allowed.items():
        allowed.setdefault(team, {})["G"] = bucket.get("G", {})

    # Built from the allowed tables so the baseline is "what an average club
    # gives up", which is what each team's table is measured against.
    league = league_averages(allowed, SKATER_KEYS)
    league["G"] = league_averages(goalies_allowed, GOALIE_KEYS).get("G", {})

    # The cheat sheet's rating model scores each input against the league, not
    # against the handful of clubs playing tonight, so the distributions are
    # built here where every team is still in hand.
    scales = rating_scales(players, allowed)

    records = fetch_records(schedule_season)
    props = fetch_props(games)

    empty = {pos: [] for pos in POSITIONS}
    slate_games = []
    for game in games:
        game_props = props.get(f"{game['away_name']} @ {game['home_name']}", {})
        slate_games.append({
            **game,
            "away_record": records.get(game["away"], ""),
            "home_record": records.get(game["home"], ""),
            "away_skaters": _with_lines(players.get(game["away"], empty), game_props),
            "home_skaters": _with_lines(players.get(game["home"], empty), game_props),
            "away_allowed": allowed.get(game["away"], {}),
            "home_allowed": allowed.get(game["home"], {}),
        })

    graded = sum(len(b) for g in slate_games
                 for side in ("away_skaters", "home_skaters")
                 for b in g[side].values())
    print(f"[nhl-research] {len(slate_games)} games, {graded} player cards")

    return {
        "date": date,
        "season": schedule_season,
        "stats_season": stats_season,
        "has_props": bool(props),
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "calendar": season_bounds(date),
        "league": league,
        "scales": scales,
        "games": slate_games,
    }


def _with_lines(skaters: dict, game_props: dict) -> dict:
    """Attach sportsbook prop lines to each player dict as `lines`."""
    if not game_props:
        return skaters
    return {
        pos: [{**p, "lines": game_props.get(normalize_name(p["name"]), {})} for p in bucket]
        for pos, bucket in skaters.items()
    }


def write_slate(date: str) -> Path:
    payload = build_slate(date)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"nhl-research-{date}.json"
    # compact separators: game logs make this file large enough to matter
    out_path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    return out_path
