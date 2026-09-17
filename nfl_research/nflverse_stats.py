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
    # target share arrives as a fraction; it is stored as a percent below
    "tgt_share": "target_share",
    "air_yds": "receiving_air_yards",
    "yac": "receiving_yards_after_catch",
    # air-yards share arrives as a fraction too
    "air_share": "air_yards_share",
    "pass_air": "passing_air_yards",
    "sacks": "sacks_suffered",
    "pass_1d": "passing_first_downs",
    "rush_1d": "rushing_first_downs",
    "rec_1d": "receiving_first_downs",
    "fpts_ppr": "fantasy_points_ppr",
}

# Keys computed rather than read straight off the weekly feed. `td` is every
# touchdown he scored; the play-by-play keys come from
# cheatsheets.player_game_extras; `spread` is his team's line that game.
PBP_KEYS = (
    # receiving
    "long", "lng_td", "rec_20", "deep_tgt",
    "rz_tgt", "rz_share", "rz_rec", "i10_tgt",
    # rushing
    "long_rush", "rush_10", "rz_car", "rz_car_share", "i10_car", "i5_car", "scrambles",
    # passing
    "long_pass", "pass_20", "deep_att", "rz_pass_att", "rz_pass_td",
    # scoring
    "rz_td", "first_td", "last_td",
)
SNAP_KEYS = ("snaps", "snap_pct")
DERIVED_KEYS = ("td", "fum_lost", "fpts_half", "rush_share", "spread") + PBP_KEYS + SNAP_KEYS
STAT_KEYS = tuple(STAT_COLUMNS) + DERIVED_KEYS

# Summing these across every receiver a defense faced in a game produces nothing
# meaningful -- five longest receptions added together is not a longest
# reception. They stay in the per-rank tables, where each game is one player.
NON_ADDITIVE = ("long", "lng_td", "long_rush", "long_pass", "spread", "snaps", "snap_pct")

# stat used to sort a position group into depth ranks (WR1, WR2, ...)
RANK_STAT = {"QB": "pass_yds", "RB": "rush_yds", "WR": "rec_yds", "TE": "rec_yds"}
# stats kept in per-game logs (position-relevant subset to keep the JSON lean)
_RECEIVER_LOG = ("tgt", "rec", "rec_yds", "rec_td", "td", "tgt_share", "air_yds", "air_share", "yac",
                 "long", "lng_td", "rec_1d", "rec_20", "deep_tgt",
                 "rz_tgt", "rz_share", "rz_rec", "i10_tgt", "rz_td", "first_td", "last_td",
                 "rush_att", "rush_yds", "fum_lost", "fpts_half", "fpts_ppr", "snaps", "snap_pct", "spread")
POS_LOG_KEYS = {
    # QBs carry rush_td so the sheet can separate a thrown touchdown (PTD) from
    # one the quarterback scored himself. Without it every QB TD looked alike.
    "QB": ("pass_att", "pass_cmp", "pass_yds", "pass_td", "pass_int", "sacks", "pass_air", "pass_1d",
           "long_pass", "pass_20", "deep_att", "rz_pass_att", "rz_pass_td",
           "rush_att", "rush_yds", "rush_td", "rush_1d", "long_rush", "scrambles", "rz_car", "i5_car",
           "rz_td", "td", "first_td", "last_td", "fum_lost", "fpts_half", "fpts_ppr", "snap_pct", "spread"),
    "RB": ("rush_att", "rush_yds", "rush_td", "rush_share", "rush_1d", "long_rush", "rush_10",
           "rz_car", "rz_car_share", "i10_car", "i5_car",
           "tgt", "rec", "rec_yds", "rec_td", "rec_1d", "tgt_share", "yac", "long",
           "rz_tgt", "rz_share", "rz_rec", "rz_td", "td", "first_td", "last_td",
           "fum_lost", "fpts_half", "fpts_ppr", "snaps", "snap_pct", "spread"),
    "WR": _RECEIVER_LOG,
    "TE": _RECEIVER_LOG,
}
# Averages and defense tables cover each player's and each defense's last this-many
# games, across seasons. Logs keep every game loaded, so L5/L10 reach back into last
# season while this one is young -- the same window the Game Board uses.
STATS_WINDOW = 17

# how many depth ranks the defense-allowed breakdown keeps per position
MAX_RANKS = {"QB": 1, "RB": 3, "WR": 4, "TE": 2}
# how many players per position each offense panel shows
ROSTER_CAP = {"QB": 2, "RB": 4, "WR": 5, "TE": 3}

# nflverse team abbr -> ESPN team abbr
TEAM_TO_ESPN = {"LA": "LAR", "WAS": "WSH"}


def espn_abbr(team: str) -> str:
    return TEAM_TO_ESPN.get(team, team)


def current_team_lookup(season: int) -> dict[str, str]:
    """gsis id -> the team he plays for NOW, from this season's published roster.

    Player-to-team used to come from whichever season the STATS came from, so every
    offseason move was invisible: A.J. Brown sat under Philadelphia while playing
    for New England, and 150 players were filed under a team they had left. nflverse
    publishes rosters well before it publishes weekly stats, which is exactly the
    gap this closes -- last season's production, this season's uniform.

    Abbreviations are normalised on the way out. The roster feed says LA and WAS
    where the schedule says LAR and WSH, and comparing them raw makes it look like
    the entire Rams roster changed teams.
    """
    try:
        roster = nflreadpy.load_rosters(seasons=season)
    except Exception:
        return {}
    out: dict[str, str] = {}
    for row in roster.iter_rows(named=True):
        gsis, team = row.get("gsis_id"), row.get("team")
        if gsis and team:
            out[gsis] = espn_abbr(team)
    return out


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
        # nflverse `spread_line` is how many points the home side is favoured by.
        # Stored the way a sportsbook prints it for each team: favourite negative.
        line = r.get("spread_line")
        home_spread = -float(line) if line is not None else 0.0
        lookup[(week, home)] = {"ha": "vs", "wl": home_wl, "spread": home_spread}
        lookup[(week, away)] = {"ha": "@", "wl": away_wl, "spread": -home_spread}
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
            "season": season,
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
        row["tgt_share"] = round(row["tgt_share"] * 100.0, 1)
        row["air_share"] = round(row["air_share"] * 100.0, 1)
        row["td"] = row["rush_td"] + row["rec_td"]
        row["fum_lost"] = sum(float(raw.get(c) or 0) for c in
                              ("rushing_fumbles_lost", "receiving_fumbles_lost", "sack_fumbles_lost"))
        row["fpts_half"] = round(row["fpts_ppr"] - 0.5 * row["rec"], 2)
        row["spread"] = game.get("spread", 0.0)
        for key in PBP_KEYS + SNAP_KEYS:
            row[key] = 0.0
        rows.append(row)

    # carry share: his carries over every carry his team logged that game
    team_carries: dict[tuple, float] = defaultdict(float)
    for row in rows:
        team_carries[(row["week"], row["team"])] += row["rush_att"]
    for row in rows:
        total = team_carries[(row["week"], row["team"])]
        row["rush_share"] = round(100.0 * row["rush_att"] / total, 1) if total else 0.0
    return rows


def snap_extras(seasons) -> dict[tuple[str, int, int], dict]:
    """(gsis id, season, week) -> offensive snaps and snap share, from nflverse's
    Pro Football Reference snap counts. Those are keyed by PFR id, so the players
    table bridges them to the gsis ids every other feed uses. A season not yet
    published is skipped rather than failing the build."""
    try:
        players = nflreadpy.load_players().select(["gsis_id", "pfr_id"]).drop_nulls()
    except Exception:
        return {}
    to_gsis = dict(zip(players["pfr_id"].to_list(), players["gsis_id"].to_list()))
    out: dict[tuple[str, int, int], dict] = {}
    for season in seasons:
        try:
            snaps = nflreadpy.load_snap_counts(seasons=season)
        except Exception:
            continue
        for r in snaps.filter(pl.col("game_type") == "REG").iter_rows(named=True):
            gsis = to_gsis.get(r["pfr_player_id"])
            if not gsis or not r["offense_snaps"]:
                continue
            out[(gsis, int(r["season"]), int(r["week"]))] = {
                "snaps": float(r["offense_snaps"]),
                "snap_pct": round(100.0 * float(r["offense_pct"] or 0), 1),
            }
    return out


def _compact(stats: dict) -> dict:
    """A game log is mostly zeros -- no red-zone carries, no first touchdown -- and
    it is the bulk of the slate file. Zeros are dropped (the page reads a missing
    key as 0) and whole numbers lose their ".0"."""
    out = {}
    for key, val in stats.items():
        if val is None:
            out[key] = None
        elif val:
            out[key] = int(val) if float(val).is_integer() else val
    return out


def _zero_stats() -> dict:
    return {key: 0.0 for key in STAT_KEYS}


def _per_game(totals: dict, games: int) -> dict:
    if games <= 0:
        return {key: 0.0 for key in STAT_KEYS}
    return {key: round(totals[key] / games, 1) for key in STAT_KEYS}


def build_aggregates(
    rows: list[dict], current_teams: dict[str, str] | None = None,
    cap: dict[str, int] | None = ROSTER_CAP,
) -> tuple[dict, dict]:
    """Return (players_by_team, defense_vs_pos_by_team).

    players_by_team: { "KC": { "QB": [ {name, pos, gp, rank, headshot, stats{}} ] } }
    defense_vs_pos_by_team: { "KC": { "WR": { "overall": {...}, "ranks": {"1": {...}} } } }
    """
    # ── player totals over his last STATS_WINDOW games + a log of every game ──
    # Games are ordered by (season, week): week alone collides once two seasons are
    # loaded, and 2025 week 1 would sort beside 2026 week 1.
    by_player: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_player[row["player_id"]].append(row)

    player_totals: dict[str, dict] = {}
    for pid, games in by_player.items():
        games.sort(key=lambda r: (r.get("season", 0), r["week"]))
        latest = games[-1]
        window = games[-STATS_WINDOW:]
        headshot = next((g["headshot"] for g in reversed(games) if g["headshot"]), "")
        entry = {
            "name": latest["name"],
            "pos": latest["pos"],
            "team": latest["team"],  # trades: keep most recent team
            "player_id": pid,
            "headshot": headshot,
            "gp": len(window),
            "seasons": sorted({g.get("season") for g in window if g.get("season")}),
            "totals": _zero_stats(),
            "log": [],
        }
        for g in window:
            for key in STAT_KEYS:
                entry["totals"][key] += g[key]
        for g in games:
            entry["log"].append(
                {
                    "season": g.get("season"),
                    "week": g["week"],
                    "opp": g["opp"],
                    "ha": g["ha"],
                    "wl": g["wl"],
                    "stats": _compact({key: g[key] for key in POS_LOG_KEYS[g["pos"]]}),
                }
            )
        player_totals[pid] = entry

    # ── each defense's games, and the last STATS_WINDOW of them its tables use ──
    def_weeks: dict[str, set] = defaultdict(set)
    for row in rows:
        if row["opp"]:
            def_weeks[row["opp"]].add((row.get("season", 0), row["week"]))
    def_window = {team: set(sorted(g)[-STATS_WINDOW:]) for team, g in def_weeks.items()}
    def_games = {team: len(g) for team, g in def_window.items()}

    # ── defense allowed: overall per position ──
    def_totals: dict[tuple, dict] = defaultdict(_zero_stats)
    for row in rows:
        if not row["opp"]:
            continue
        if (row.get("season", 0), row["week"]) not in def_window.get(row["opp"], ()):
            continue
        totals = def_totals[(row["opp"], row["pos"])]
        for key in STAT_KEYS:
            totals[key] += row[key]

    # ── defense allowed: by depth rank within each game ──
    game_groups: dict[tuple, list] = defaultdict(list)
    for row in rows:
        if row["opp"]:
            game_groups[(row["opp"], row.get("season", 0), row["week"], row["pos"])].append(row)

    rank_totals: dict[tuple, dict] = defaultdict(_zero_stats)
    rank_logs: dict[tuple, list] = defaultdict(list)
    for (opp, season, week, pos), group in game_groups.items():
        group.sort(key=lambda r: r[RANK_STAT[pos]], reverse=True)
        log_keys = POS_LOG_KEYS[pos]
        in_window = (season, week) in def_window.get(opp, ())
        for idx, row in enumerate(group[: MAX_RANKS[pos]], start=1):
            if in_window:
                totals = rank_totals[(opp, pos, idx)]
                for key in STAT_KEYS:
                    totals[key] += row[key]
            rank_logs[(opp, pos, idx)].append(
                {
                    "season": season,
                    "week": week,
                    "opp": row["team"],  # the offense this defense faced
                    "ha": row["def_ha"],
                    "wl": row["def_wl"],
                    "player": row["name"],
                    "stats": _compact({key: row[key] for key in log_keys}),
                }
            )

    defense: dict[str, dict] = {}
    for (team, pos), totals in def_totals.items():
        games = def_games.get(team, 0)
        block = defense.setdefault(team, {}).setdefault(pos, {"overall": {}, "ranks": {}, "rank_logs": {}})
        block["overall"] = _per_game(totals, games)
        for key in NON_ADDITIVE:
            block["overall"][key] = None
    # a slot with games in its log but none inside the window still needs its log
    for key in rank_logs:
        rank_totals.setdefault(key, _zero_stats())
    for (team, pos, rank), totals in rank_totals.items():
        games = def_games.get(team, 0)
        block = defense.setdefault(team, {}).setdefault(
            pos, {"overall": _zero_stats(), "ranks": {}, "rank_logs": {}}
        )
        block["ranks"][str(rank)] = _per_game(totals, games)
        block["rank_logs"][str(rank)] = sorted(
            rank_logs[(team, pos, rank)], key=lambda e: (e["season"] or 0, e["week"])
        )

    # ── offense panels: top players per team/position with depth rank ──
    players: dict[str, dict] = {}
    by_team_pos: dict[tuple, list] = defaultdict(list)
    dropped = moved = 0
    for entry in player_totals.values():
        if entry["gp"] <= 0:
            continue
        team = entry["team"]
        if current_teams:
            now = current_teams.get(entry["player_id"])
            if now is None:
                # Off every roster this season -- retired or unsigned. Showing him
                # under last season's team puts a player on the board who cannot
                # take the field.
                dropped += 1
                continue
            if now != team:
                moved += 1
            team = now
        by_team_pos[(team, entry["pos"])].append(entry)
    if current_teams:
        print(f"[nfl-research] rosters: {moved} players re-filed onto their current "
              f"team, {dropped} no longer rostered and dropped")

    for (team, pos), entries in by_team_pos.items():
        entries.sort(key=lambda e: e["totals"][RANK_STAT[pos]], reverse=True)
        bucket = players.setdefault(team, {}).setdefault(pos, [])
        # cap=None hands back the whole pool, ordered by last season's volume, so
        # the depth chart can pick the real starters out of it. The old caps are
        # only a fallback for a club with no chart published.
        pool = entries if cap is None else entries[: cap[pos]]
        for idx, entry in enumerate(pool, start=1):
            if cap is not None and entry["totals"][RANK_STAT[pos]] <= 0:
                continue
            bucket.append(
                {
                    "name": entry["name"],
                    # kept so the red-zone projection can join on an id rather
                    # than guessing that "C.McCaffrey" is "Christian McCaffrey"
                    "player_id": entry["player_id"],
                    "pos": pos,
                    "gp": entry["gp"],
                    "seasons": entry["seasons"],
                    "rank": min(idx, MAX_RANKS[pos]),
                    "headshot": entry["headshot"],
                    "stats": _per_game(entry["totals"], entry["gp"]),
                    "log": entry["log"],
                }
            )

    return players, defense


def merge_game_extras(rows: list[dict], extras: dict[tuple[str, int], dict],
                      keys: tuple = PBP_KEYS) -> int:
    """Fold play-by-play per-game numbers into the weekly rows. Returns rows touched.

    Done before aggregation so the player's averages, his game log and every
    defense table all pick the new numbers up from one place.
    """
    touched = 0
    for row in rows:
        got = extras.get((row["player_id"], row.get("season"), row["week"]))
        if got:
            for key in keys:
                row[key] = got.get(key, 0.0)
            touched += 1
    return touched
