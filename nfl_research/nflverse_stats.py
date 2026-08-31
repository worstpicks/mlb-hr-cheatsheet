"""Load + aggregate nflverse weekly player stats for the NFL Research tab.

Source (free, CC-BY 4.0) via the nflreadpy package:
    https://nflreadpy.nflverse.com/  ->  nflverse-data stats_player releases

Produces:
    * per-player season per-game averages (QB / RB / WR / TE)
    * per-defense "allowed to position" per-game averages, both overall and
      by depth rank (WR1/WR2/... ranked by that week's yardage vs the defense)
"""
from __future__ import annotations

from collections import defaultdict

import nflreadpy
import polars as pl

POSITIONS = ("QB", "RB", "WR", "TE")

# output stat key -> nflreadpy load_player_stats() column
STAT_COLUMNS = {
    "pass_att": "attempts",
    "pass_cmp": "completions",
    "pass_yds": "passing_yards",
    "pass_td": "passing_tds",
    "pass_int": "passing_interceptions",
    "rush_att": "carries",
    "rush_yds": "rushing_yards",
    "rush_td": "rushing_tds",
    "tgt": "targets",
    "rec": "receptions",
    "rec_yds": "receiving_yards",
    "rec_td": "receiving_tds",
}

# stat used to sort a position group into depth ranks (WR1, WR2, ...)
RANK_STAT = {"QB": "pass_yds", "RB": "rush_yds", "WR": "rec_yds", "TE": "rec_yds"}
# stats kept in per-game logs (position-relevant subset to keep the JSON lean)
POS_LOG_KEYS = {
    # QBs carry rush_td so the sheet can separate a thrown touchdown (PTD) from
    # one the quarterback scored himself. Without it every QB TD looked alike.
    "QB": ("pass_att", "pass_cmp", "pass_yds", "pass_td", "pass_int",
           "rush_att", "rush_yds", "rush_td"),
    "RB": ("rush_att", "rush_yds", "rush_td", "tgt", "rec", "rec_yds"),
    "WR": ("tgt", "rec", "rec_yds", "rec_td"),
    "TE": ("tgt", "rec", "rec_yds", "rec_td"),
}
# how many depth ranks the defense-allowed breakdown keeps per position
MAX_RANKS = {"QB": 1, "RB": 3, "WR": 4, "TE": 2}
# how many players per position each offense panel shows
ROSTER_CAP = {"QB": 2, "RB": 4, "WR": 5, "TE": 3}

# nflverse team abbr -> ESPN team abbr
TEAM_TO_ESPN = {"LA": "LAR", "WAS": "WSH"}


def espn_abbr(team: str) -> str:
    return TEAM_TO_ESPN.get(team, team)


def _schedule_lookup(season: int) -> dict:
    """(week, team) -> {"ha": "vs"|"@", "wl": "W"|"L"|"T"} from nflverse schedules."""
    try:
        sched = nflreadpy.load_schedules([season])
    except Exception:
        return {}
    lookup: dict[tuple, dict] = {}
    for r in sched.iter_rows(named=True):
        if r.get("game_type") not in ("REG", None):
            continue
        week = int(r.get("week") or 0)
        home = espn_abbr(r.get("home_team") or "")
        away = espn_abbr(r.get("away_team") or "")
        hs, aws = r.get("home_score"), r.get("away_score")
        if hs is None or aws is None:
            home_wl = away_wl = ""
        elif hs == aws:
            home_wl = away_wl = "T"
        else:
            home_wl, away_wl = ("W", "L") if hs > aws else ("L", "W")
        lookup[(week, home)] = {"ha": "vs", "wl": home_wl}
        lookup[(week, away)] = {"ha": "@", "wl": away_wl}
    return lookup


def download_weekly_stats(season: int) -> list[dict]:
    """Load nflverse weekly player stats for a season via nflreadpy.

    Returns normalized row dicts (REG season, QB/RB/WR/TE only) or raises
    ``FileNotFoundError`` if nflverse has no data for that season yet.
    """
    try:
        df = nflreadpy.load_player_stats(seasons=season, summary_level="week")
    except Exception as exc:
        raise FileNotFoundError(f"nflreadpy has no weekly stats for {season}") from exc
    if df.height == 0:
        raise FileNotFoundError(f"nflreadpy returned no rows for {season}")

    df = df.filter(
        (pl.col("season_type") == "REG") & pl.col("position").is_in(list(POSITIONS))
    )
    schedule = _schedule_lookup(season)

    rows = []
    for raw in df.iter_rows(named=True):
        team = espn_abbr(raw.get("team") or "")
        if not team:
            continue
        week = int(raw.get("week") or 0)
        opp = espn_abbr(raw.get("opponent_team") or "")
        game = schedule.get((week, team), {})
        def_game = schedule.get((week, opp), {})
        row = {
            "player_id": raw.get("player_id") or "",
            "name": raw.get("player_display_name") or raw.get("player_name") or "",
            "pos": raw.get("position") or "",
            "team": team,
            "opp": opp,
            "week": week,
            "headshot": raw.get("headshot_url") or "",
            "ha": game.get("ha", ""),
            "wl": game.get("wl", ""),
            "def_ha": def_game.get("ha", ""),
            "def_wl": def_game.get("wl", ""),
        }
        for key, col in STAT_COLUMNS.items():
            val = raw.get(col)
            row[key] = float(val) if val is not None else 0.0
        rows.append(row)
    return rows


def _zero_stats() -> dict:
    return {key: 0.0 for key in STAT_COLUMNS}


def _per_game(totals: dict, games: int) -> dict:
    if games <= 0:
        return {key: 0.0 for key in STAT_COLUMNS}
    return {key: round(totals[key] / games, 1) for key in STAT_COLUMNS}


def build_aggregates(rows: list[dict]) -> tuple[dict, dict]:
    """Return (players_by_team, defense_vs_pos_by_team).

    players_by_team: { "KC": { "QB": [ {name, pos, gp, rank, headshot, stats{}} ] } }
    defense_vs_pos_by_team: { "KC": { "WR": { "overall": {...}, "ranks": {"1": {...}} } } }
    """
    # ── player season totals + per-game log ──
    player_totals: dict[str, dict] = {}
    for row in rows:
        entry = player_totals.setdefault(
            row["player_id"],
            {
                "name": row["name"],
                "pos": row["pos"],
                "team": row["team"],
                "headshot": row["headshot"],
                "gp": 0,
                "last_week": -1,
                "totals": _zero_stats(),
                "log": [],
            },
        )
        entry["gp"] += 1
        if row["week"] > entry["last_week"]:
            entry["last_week"] = row["week"]
            entry["team"] = row["team"]  # trades: keep most recent team
            if row["headshot"]:
                entry["headshot"] = row["headshot"]
        for key in STAT_COLUMNS:
            entry["totals"][key] += row[key]
        log_keys = POS_LOG_KEYS[row["pos"]]
        entry["log"].append(
            {
                "week": row["week"],
                "opp": row["opp"],
                "ha": row["ha"],
                "wl": row["wl"],
                "stats": {key: row[key] for key in log_keys},
            }
        )

    # ── defense games played (distinct weeks with at least one opponent row) ──
    def_weeks: dict[str, set] = defaultdict(set)
    for row in rows:
        if row["opp"]:
            def_weeks[row["opp"]].add(row["week"])
    def_games = {team: len(weeks) for team, weeks in def_weeks.items()}

    # ── defense allowed: overall per position ──
    def_totals: dict[tuple, dict] = defaultdict(_zero_stats)
    for row in rows:
        if not row["opp"]:
            continue
        totals = def_totals[(row["opp"], row["pos"])]
        for key in STAT_COLUMNS:
            totals[key] += row[key]

    # ── defense allowed: by depth rank within each game ──
    game_groups: dict[tuple, list] = defaultdict(list)
    for row in rows:
        if row["opp"]:
            game_groups[(row["opp"], row["week"], row["pos"])].append(row)

    rank_totals: dict[tuple, dict] = defaultdict(_zero_stats)
    rank_logs: dict[tuple, list] = defaultdict(list)
    for (opp, week, pos), group in game_groups.items():
        group.sort(key=lambda r: r[RANK_STAT[pos]], reverse=True)
        log_keys = POS_LOG_KEYS[pos]
        for idx, row in enumerate(group[: MAX_RANKS[pos]], start=1):
            totals = rank_totals[(opp, pos, idx)]
            for key in STAT_COLUMNS:
                totals[key] += row[key]
            rank_logs[(opp, pos, idx)].append(
                {
                    "week": week,
                    "opp": row["team"],  # the offense this defense faced
                    "ha": row["def_ha"],
                    "wl": row["def_wl"],
                    "player": row["name"],
                    "stats": {key: row[key] for key in log_keys},
                }
            )

    defense: dict[str, dict] = {}
    for (team, pos), totals in def_totals.items():
        games = def_games.get(team, 0)
        block = defense.setdefault(team, {}).setdefault(pos, {"overall": {}, "ranks": {}, "rank_logs": {}})
        block["overall"] = _per_game(totals, games)
    for (team, pos, rank), totals in rank_totals.items():
        games = def_games.get(team, 0)
        block = defense.setdefault(team, {}).setdefault(
            pos, {"overall": _zero_stats(), "ranks": {}, "rank_logs": {}}
        )
        block["ranks"][str(rank)] = _per_game(totals, games)
        block["rank_logs"][str(rank)] = sorted(rank_logs[(team, pos, rank)], key=lambda e: e["week"])

    # ── offense panels: top players per team/position with depth rank ──
    players: dict[str, dict] = {}
    by_team_pos: dict[tuple, list] = defaultdict(list)
    for entry in player_totals.values():
        if entry["gp"] > 0:
            by_team_pos[(entry["team"], entry["pos"])].append(entry)

    for (team, pos), entries in by_team_pos.items():
        entries.sort(key=lambda e: e["totals"][RANK_STAT[pos]], reverse=True)
        bucket = players.setdefault(team, {}).setdefault(pos, [])
        for idx, entry in enumerate(entries[: ROSTER_CAP[pos]], start=1):
            if entry["totals"][RANK_STAT[pos]] <= 0:
                continue
            bucket.append(
                {
                    "name": entry["name"],
                    "pos": pos,
                    "gp": entry["gp"],
                    "rank": min(idx, MAX_RANKS[pos]),
                    "headshot": entry["headshot"],
                    "stats": _per_game(entry["totals"], entry["gp"]),
                    "log": sorted(entry["log"], key=lambda e: e["week"]),
                }
            )

    return players, defense
