"""Assemble the NFL Research slate JSON: ESPN week schedule + nflverse aggregates."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from nfl_research.espn_api import fetch_week_games
from nfl_research.nflverse_stats import POSITIONS, build_aggregates, download_weekly_stats
from nfl_research.cheatsheets import build_cheatsheets
from nfl_research.espn_preseason import build_preseason
from nfl_research.odds_api import fetch_props, normalize_name
from nfl_research.weather import fetch_game_weather

OUT_DIR = Path(__file__).resolve().parent.parent / "preview" / "data"


def resolve_stats_season(schedule_season: int) -> tuple[int, list[dict]]:
    """Use the schedule season's nflverse stats if published, else fall back a year."""
    for season in (schedule_season, schedule_season - 1):
        try:
            return season, download_weekly_stats(season)
        except FileNotFoundError:
            continue
    raise RuntimeError(f"No nflverse weekly stats found for {schedule_season} or {schedule_season - 1}")


def build_slate(season: int, week: int) -> dict:
    games = fetch_week_games(season, week)
    stats_season, rows = resolve_stats_season(season)
    players, defense = build_aggregates(rows)
    props = fetch_props(games)

    empty_pos = {pos: [] for pos in POSITIONS}
    slate_games = []
    for game in games:
        game_props = props.get(f"{game['away_name']} @ {game['home_name']}", {})
        slate_games.append(
            {
                **game,
                "away_offense": _with_lines(players.get(game["away"], empty_pos), game_props),
                "home_offense": _with_lines(players.get(game["home"], empty_pos), game_props),
                "away_def_vs_pos": defense.get(game["away"], {}),
                "home_def_vs_pos": defense.get(game["home"], {}),
            }
        )

    # Preseason is the only football newer than last season -- nflverse has no
    # rows for a season before it starts. It rides alongside the real aggregates
    # as an opt-in source; it is never the default, because the snaps belong to
    # roster hopefuls rather than the players anyone is betting.
    teams_list = sorted({g["away"] for g in games} | {g["home"] for g in games})
    try:
        pre_players, pre_defense, pre_rows = build_preseason(season, teams_list)
    except Exception as exc:
        print(f"[nfl-research] preseason fetch failed ({exc}); regular season only")
        pre_players, pre_defense, pre_rows = {}, {}, 0
    if pre_rows:
        print(f"[nfl-research] preseason: {pre_rows} player-game rows from ESPN")
        for game, slate_game in zip(games, slate_games):
            slate_game["away_offense_pre"] = pre_players.get(game["away"], empty_pos)
            slate_game["home_offense_pre"] = pre_players.get(game["home"], empty_pos)
            slate_game["away_def_vs_pos_pre"] = pre_defense.get(game["away"], {})
            slate_game["home_def_vs_pos_pre"] = pre_defense.get(game["home"], {})

    weather = fetch_game_weather(games)
    for game in slate_games:
        game["weather"] = weather.get(game["id"])

    teams = {g["away"] for g in games} | {g["home"] for g in games}
    sheets = build_cheatsheets(stats_season, teams)

    return {
        "season": season,
        "week": week,
        "stats_season": stats_season,
        "has_props": bool(props),
        "has_preseason": bool(pre_rows),
        "preseason_rows": pre_rows,
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "games": slate_games,
        "sheets": sheets,
    }


def _with_lines(offense: dict, game_props: dict) -> dict:
    """Attach sportsbook prop lines to each player dict as `lines`."""
    if not game_props:
        return offense
    out = {}
    for pos, bucket in offense.items():
        out[pos] = [
            {**player, "lines": game_props.get(normalize_name(player["name"]), {})}
            for player in bucket
        ]
    return out


def write_slate(season: int, week: int) -> Path:
    payload = build_slate(season, week)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"nfl-research-{season}-W{week}.json"
    # compact separators: game logs make this file large enough to matter
    out_path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    return out_path
