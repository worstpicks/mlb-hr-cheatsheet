"""Assemble the NFL Research slate JSON: ESPN week schedule + nflverse aggregates."""
from __future__ import annotations

import json

import polars as pl
from datetime import datetime
from pathlib import Path

from nfl_research.espn_api import fetch_week_games
from nfl_research.nflverse_stats import (
    POSITIONS,
    build_aggregates,
    SNAP_KEYS,
    current_team_lookup,
    download_weekly_stats,
    merge_game_extras,
    snap_extras,
)
from nfl_research.cheatsheets import (
    build_cheatsheets,
    current_depth_charts,
    load_pbp,
    player_game_extras,
)
from nfl_research.game_board import attach_game_boards
from nfl_research.lineups import build_lineups
from nfl_research.espn_preseason import build_preseason
from nfl_research.odds_api import fetch_props, normalize_name
from nfl_research.redzone import attach_td_chance
from nfl_research.weather import fetch_game_weather

OUT_DIR = Path(__file__).resolve().parent.parent / "preview" / "data"
# Season-long sheets keep reading last season until this many weeks of the new one exist
SHEETS_MIN_WEEKS = 4


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
    # Stats come from whatever season nflverse has published; the uniform comes from
    # THIS season's roster. Without the second half the board shows last year's
    # depth charts -- A.J. Brown under Philadelphia when he plays for New England.
    current_teams = current_team_lookup(season)
    if not current_teams:
        print(f"[nfl-research] WARN no {season} roster published yet; "
              f"players stay on their {stats_season} teams")
    # Play-by-play once, up front: the per-game extras need it before aggregation,
    # and the sheets reuse the same frame instead of downloading it a second time.
    pbp = load_pbp(stats_season)
    extras_pbp = pbp
    prev_pbp = None
    # Once the season is underway, reach back into the last one: a player's log then
    # holds his actual last five or ten games rather than one week of this season.
    if stats_season == season:
        try:
            rows = download_weekly_stats(season - 1) + rows
            prev_pbp = load_pbp(season - 1)
            extras_pbp = pl.concat([prev_pbp, pbp], how="diagonal_relaxed")
            print(f"[nfl-research] logs reach back into {season - 1} alongside {season}")
        except FileNotFoundError:
            pass
    touched = merge_game_extras(rows, player_game_extras(extras_pbp))
    print(f"[nfl-research] play-by-play extras merged into {touched} player-games")
    log_seasons = sorted({r.get("season") for r in rows if r.get("season")})
    snapped = merge_game_extras(rows, snap_extras(log_seasons), SNAP_KEYS)
    print(f"[nfl-research] snap counts merged into {snapped} of {len(rows)} player-games")

    players, defense = build_aggregates(rows, current_teams, cap=None)
    # The newest regular-season game in the sample. A slate for a week further out
    # than the next one is an early look, and the page says so.
    last = max(((r.get("season") or 0, r["week"]) for r in rows), default=(None, None))
    stats_through = {"season": last[0], "week": last[1]}

    # The lineup is whoever the club lists, not whoever gained the most yards last
    # year. See lineups.py for why that distinction put the wrong backs on top.
    teams = {g["away"] for g in games} | {g["home"] for g in games}
    depth, depth_season = current_depth_charts(season)
    players, lineup_report = build_lineups(players, depth, teams)
    print(f"[nfl-research] lineups: {lineup_report['from_depth']} players from depth charts, "
          f"{lineup_report['fallback']} from last season's volume "
          f"({len(lineup_report['teams_without_chart'])} clubs without a chart), "
          f"{len(lineup_report['no_history'])} starters with no {stats_season} games")
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
    # Once two regular-season weeks are in, August snaps have nothing left to add
    # and the toggle only offers a worse sample, so the source is dropped.
    teams_list = sorted({g["away"] for g in games} | {g["home"] for g in games})
    reg_weeks = len({r["week"] for r in rows if r.get("season") == season})
    pre_players, pre_defense, pre_rows = {}, {}, 0
    if reg_weeks >= 2:
        print(f"[nfl-research] preseason: skipped, {season} has {reg_weeks} regular-season weeks")
    else:
        try:
            pre_players, pre_defense, pre_rows = build_preseason(season, teams_list)
        except Exception as exc:
            print(f"[nfl-research] preseason fetch failed ({exc}); regular season only")
    if pre_rows:
        print(f"[nfl-research] preseason: {pre_rows} player-game rows from ESPN")
        for game, slate_game in zip(games, slate_games):
            slate_game["away_offense_pre"] = _lineup_only(pre_players.get(game["away"], empty_pos), players.get(game["away"], {}))
            slate_game["home_offense_pre"] = _lineup_only(pre_players.get(game["home"], empty_pos), players.get(game["home"], {}))
            slate_game["away_def_vs_pos_pre"] = pre_defense.get(game["away"], {})
            slate_game["home_def_vs_pos_pre"] = pre_defense.get(game["home"], {})

    weather = fetch_game_weather(games)
    for game in slate_games:
        game["weather"] = weather.get(game["id"])

    # The sheets (red zone, rushing gaps, hit rates, team share...) aggregate a whole
    # season of play-by-play. Early in a new one that is a sample of a game or two --
    # the Week 2 red-zone sheet had 20 players -- so until SHEETS_MIN_WEEKS are in they
    # keep reading last season, the way Week 1 did. Logs and the Game Board are not
    # affected: they run on each player's rolling window across both seasons.
    sheets_season, sheets_pbp = stats_season, pbp
    weeks_in = pbp.select(pl.col("week").n_unique()).item() if pbp.height else 0
    if stats_season == season and weeks_in < SHEETS_MIN_WEEKS and prev_pbp is not None:
        sheets_season, sheets_pbp = season - 1, prev_pbp
        print(f"[nfl-research] sheets: {season} has {weeks_in} week(s) of play-by-play; "
              f"reading {season - 1} until {SHEETS_MIN_WEEKS} are in")
    sheets = build_cheatsheets(sheets_season, teams, season, pbp=sheets_pbp)

    # Anytime-TD chance per player. The season aggregates ride in `sheets`; this
    # is the matchup join, so the cheat sheet no longer needs a pasted board.
    rz_report = attach_td_chance(slate_games, sheets.get("red_zone_proj") or {})
    print(f"[nfl-research] red zone: {rz_report['projected']} players projected, "
          f"{rz_report['skipped']} without an input, {rz_report['moved']} on a share "
          f"earned with another team")

    # The Game Board: every lineup player graded against this week's opponent, on a
    # rolling window that reaches back into last season while this one is young.
    board_report = attach_game_boards(slate_games, players, season)
    print(f"[nfl-research] game board: {board_report['graded']} players graded on "
          f"{board_report['seasons']} games, {board_report['no_history']} without a sample, "
          f"coverage from {board_report['coverage_seasons'] or 'no season'}")

    return {
        "season": season,
        "week": week,
        "stats_season": stats_season,
        "has_props": bool(props),
        "has_preseason": bool(pre_rows),
        "preseason_rows": pre_rows,
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "stats_through": stats_through,
        "depth_season": depth_season,
        # seasons the game logs reach into, so the page can say "'25–'26"
        "log_seasons": sorted({r.get("season") for r in rows if r.get("season")}),
        "lineup_no_history": lineup_report["no_history"],
        "games": slate_games,
        "sheets": sheets,
    }


def _norm(name: str) -> str:
    return "".join(ch for ch in (name or "").lower() if ch.isalpha())


def _lineup_only(pre: dict, lineup: dict) -> dict:
    """Preseason cards for the same seven players, in the same order.

    Without this the 2026 PRE toggle brought the old fourteen-card board straight
    back, full of camp bodies who will not see a regular-season snap.
    """
    out = {}
    for pos, bucket in lineup.items():
        by_name = {_norm(p.get("name")): p for p in (pre.get(pos) or [])}
        out[pos] = [dict(by_name[_norm(p["name"])], rank=p["rank"])
                    for p in bucket if _norm(p["name"]) in by_name]
    return out


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
