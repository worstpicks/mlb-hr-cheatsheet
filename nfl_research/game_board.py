"""Game Board: everything that decides a player prop, for one game, in one place.

The research tab grew a sheet per question -- role matchups, red zone, coverage,
rushing gaps, tendencies, defensive stats -- and answering "is he going to hit
his number?" meant opening six of them and doing the joining in your head. This
builds that join once, per game, per player:

    opportunity   how much of the work he gets, and whether that is growing
    matchup       what this defense gives up to the role he holds
    script        how many points his team is expected to score
    coverage      how he fares against the man/zone mix this defense plays
    touchdowns    red-zone work x how often this defense bends, plus long scores

and turns it into a projection, a touchdown chance and a 0-100 matchup grade,
with the reasons kept alongside so the grade can always be checked.

Two choices matter more than the rest:

  * Roles are usage, not yardage. A player's role in a game is his rank on his
    team by trailing five-game target share (receivers) or carry share (backs).
    Ranking by that game's yards -- what the older sheets did -- makes a defense
    look tough on WR1s whenever the WR2 happens to have the big day.

  * The window rolls across seasons: each player's and each defense's last
    seventeen regular-season games. In September that is mostly last season,
    which is the honest sample; a veteran who missed week one still has one.

Everything here is free data: nflverse weekly stats, play-by-play and
participation (coverage, pressure), plus the ESPN line already on the slate.
"""
from __future__ import annotations

import math
from collections import defaultdict

import nflreadpy as nfl
import polars as pl

from nfl_research.cheatsheets import SCRIMMAGE_PLAYS, TEAM_FIX

WINDOW = 17          # games per player and per defense
TRAIL = 5            # games of usage that decide a role
RECENT = 5           # games in the "recent form" split
LEAGUE_TEAM_POINTS = 22.5   # a typical implied team total, the script baseline

# Leak ratios get a fantasy-point buffer on both sides before dividing. A TE2 is
# worth about two points a game league-wide, so one decent outing against a
# defense otherwise swings its ratio from x0.3 to x1.8 -- noise dressed up as a
# weakness. Three points keeps a real WR1 leak visible and flattens the rest.
LEAK_BUFFER = 3.0

# Share at which a player's matchup counts in full. Below it the grade is pulled
# toward 50: a back with a 1% carry share in a soft matchup is not a play.
FULL_SHARE = {"RB": 30.0, "WR": 15.0, "TE": 15.0}
LOW_VOLUME = 0.4   # under this fraction of FULL_SHARE he is flagged low volume

ROLE_SLOTS = {"QB": 1, "RB": 2, "WR": 3, "TE": 2}
SKILL = tuple(ROLE_SLOTS)
ROLES = tuple(f"{p}{i}" for p, n in ROLE_SLOTS.items() for i in range(1, n + 1))

# The stats a board row projects, per position. The first is the headline.
PROJECT = {
    "QB": ("pass_yds", "pass_td", "rush_yds"),
    "RB": ("rush_yds", "rec_yds", "rec"),
    "WR": ("rec_yds", "rec", "tgt"),
    "TE": ("rec_yds", "rec", "tgt"),
}
# Volume stats move with the game script; efficiency stats do not.
SCRIPTED = {"pass_yds", "rush_yds", "rec_yds", "rec", "tgt", "rush_att", "pass_att"}

WEEKLY_COLS = {
    "attempts": "pass_att", "passing_yards": "pass_yds", "passing_tds": "pass_td",
    "passing_interceptions": "pass_int", "carries": "rush_att", "rushing_yards": "rush_yds",
    "rushing_tds": "rush_td", "targets": "tgt", "receptions": "rec",
    "receiving_yards": "rec_yds", "receiving_tds": "rec_td", "target_share": "tgt_share",
}
STATS = tuple(WEEKLY_COLS.values())


def _fix(code: str | None) -> str | None:
    return TEAM_FIX.get(code, code) if code else code


def _fantasy(r: dict) -> float:
    """Half-PPR points: one scale that lets a QB leak and a TE leak be compared."""
    return (
        0.04 * r["pass_yds"] + 4 * r["pass_td"] - 2 * r["pass_int"]
        + 0.1 * (r["rush_yds"] + r["rec_yds"]) + 6 * (r["rush_td"] + r["rec_td"])
        + 0.5 * r["rec"]
    )


def _clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


# ── loading ──────────────────────────────────────────────────────────────────

def load_frames(season: int) -> dict:
    """Last season and this one, whichever of each feed is published."""
    seasons = [season - 1, season]

    weekly = nfl.load_player_stats(seasons=seasons, summary_level="week").filter(
        (pl.col("season_type") == "REG") & pl.col("position").is_in(list(SKILL))
    )

    pbp_parts = []
    for s in seasons:
        try:
            pbp_parts.append(nfl.load_pbp(seasons=[s]))
        except Exception:
            pass
    pbp = pl.concat(pbp_parts, how="diagonal_relaxed").filter(pl.col("season_type") == "REG")
    pbp = pbp.with_columns(
        pl.col("posteam").replace(TEAM_FIX), pl.col("defteam").replace(TEAM_FIX)
    )

    part_parts, cov_seasons = [], []
    for s in seasons:
        try:
            part_parts.append(nfl.load_participation(seasons=[s]).select(
                ["nflverse_game_id", "play_id", "defense_man_zone_type", "was_pressure"]
            ))
            cov_seasons.append(s)
        except Exception:
            # Participation lags the season by weeks; coverage reads use what exists.
            pass
    part = pl.concat(part_parts) if part_parts else None
    return {"weekly": weekly, "pbp": pbp, "part": part, "seasons": seasons,
            "coverage_seasons": cov_seasons}


# ── windows and roles ────────────────────────────────────────────────────────

def _team_windows(pbp: pl.DataFrame) -> dict[str, dict[str, set]]:
    """Each club's last WINDOW games, as (season, week), on offence and defence."""
    out: dict[str, dict[str, set]] = defaultdict(lambda: {"off": set(), "def": set()})
    for side, col in (("off", "posteam"), ("def", "defteam")):
        games = (
            pbp.filter(pl.col(col).is_not_null())
            .select([col, "season", "week"]).unique()
            .sort(["season", "week"], descending=True)
        )
        for team, grp in games.group_by(col):
            keep = grp.sort(["season", "week"], descending=True).head(WINDOW)
            out[team[0]][side] = {(r["season"], r["week"]) for r in keep.iter_rows(named=True)}
    return out


def _player_rows(weekly: pl.DataFrame) -> list[dict]:
    """Weekly rows with stats normalised, team codes fixed, and a usage role."""
    df = weekly.select(
        ["player_id", "player_display_name", "position", "team", "opponent_team", "season", "week",
         "headshot_url", *WEEKLY_COLS.keys()]
    ).rename({**WEEKLY_COLS, "player_display_name": "name", "position": "pos", "opponent_team": "opp"})
    df = df.with_columns(
        [pl.col(c).fill_null(0).cast(pl.Float64) for c in STATS]
        + [pl.col("team").replace(TEAM_FIX), pl.col("opp").replace(TEAM_FIX)]
    )
    team_carries = df.group_by(["team", "season", "week"]).agg(pl.col("rush_att").sum().alias("team_car"))
    df = df.join(team_carries, on=["team", "season", "week"], how="left").with_columns(
        (pl.when(pl.col("team_car") > 0).then(pl.col("rush_att") / pl.col("team_car")).otherwise(0.0))
        .alias("car_share")
    )
    # Usage decides the role: trailing mean of the share that defines each position.
    df = df.sort(["player_id", "season", "week"]).with_columns(
        pl.col("tgt_share").rolling_mean(TRAIL, min_samples=1).over("player_id").alias("trail_tgt"),
        pl.col("car_share").rolling_mean(TRAIL, min_samples=1).over("player_id").alias("trail_car"),
    )
    rows = df.to_dicts()

    by_game: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        by_game[(r["team"], r["season"], r["week"], r["pos"])].append(r)
    for (_, _, _, pos), grp in by_game.items():
        key = {"QB": "pass_att", "RB": "trail_car"}.get(pos, "trail_tgt")
        grp.sort(key=lambda r: r[key], reverse=True)
        for i, r in enumerate(grp, start=1):
            r["role"] = f"{pos}{i}" if i <= ROLE_SLOTS[pos] else None
    for r in rows:
        r["fp"] = _fantasy(r)
    return rows


# ── defence: what it gives up to each role ───────────────────────────────────

def defense_allowed(rows: list[dict], windows: dict) -> tuple[dict, dict]:
    """(allowed[def][role] -> per-game stats with ranks, league[role] -> per-game)."""
    sums: dict[tuple, dict] = defaultdict(lambda: defaultdict(float))
    for r in rows:
        role, d = r.get("role"), r["opp"]
        if not role or not d or (r["season"], r["week"]) not in windows.get(d, {}).get("def", ()):
            continue
        bucket = sums[(d, role)]
        for s in (*STATS, "fp"):
            bucket[s] += r[s]

    allowed: dict[str, dict] = defaultdict(dict)
    for (d, role), bucket in sums.items():
        games = len(windows[d]["def"]) or 1
        allowed[d][role] = {s: v / games for s, v in bucket.items()}

    league: dict[str, dict] = {}
    for role in ROLES:
        vals = [allowed[d][role] for d in allowed if role in allowed[d]]
        if vals:
            league[role] = {s: sum(v.get(s, 0.0) for v in vals) / len(vals) for s in (*STATS, "fp")}

    # rank 32 is the softest, matching the D# convention on the ATD board
    for role in ROLES:
        teams = [d for d in allowed if role in allowed[d]]
        for i, d in enumerate(sorted(teams, key=lambda t: allowed[t][role]["fp"]), start=1):
            row = allowed[d][role]
            row["rank"] = i
            row["of"] = len(teams)
            base = league.get(role, {}).get("fp")
            row["index"] = round((row["fp"] + LEAK_BUFFER) / (base + LEAK_BUFFER), 3) if base is not None else None
            tds = row.get("rec_td", 0) + row.get("rush_td", 0) + row.get("pass_td", 0) * (role == "QB1")
            ltds = (league[role].get("rec_td", 0) + league[role].get("rush_td", 0)
                    + league[role].get("pass_td", 0) * (role == "QB1"))
            row["td_index"] = round(tds / ltds, 3) if ltds else None
    return allowed, league


# ── team environment ─────────────────────────────────────────────────────────

def team_environment(pbp: pl.DataFrame, part: pl.DataFrame | None, windows: dict) -> dict:
    """Pace, lean, red-zone conversion, pressure and coverage for every club."""
    env: dict[str, dict] = defaultdict(dict)
    plays = pbp.filter(pl.col("play_type").is_in(["pass", "run"]) & pl.col("posteam").is_not_null())

    def in_window(frame, col, side):
        keys = [(t, s, w) for t, sides in windows.items() for (s, w) in sides[side]]
        allowed = pl.DataFrame(keys, schema=[col, "season", "week"], orient="row")
        return frame.join(allowed, on=[col, "season", "week"], how="inner")

    off = in_window(plays, "posteam", "off")
    for r in off.group_by("posteam").agg(
        pl.len().alias("plays"),
        pl.struct(["season", "week"]).n_unique().alias("games"),
    ).iter_rows(named=True):
        env[r["posteam"]]["pace"] = round(r["plays"] / r["games"], 1)

    neutral = off.filter(
        (pl.col("qtr") <= 3) & (pl.col("score_differential").abs() <= 7) & pl.col("down").is_in([1, 2, 3])
    )
    for r in neutral.group_by("posteam").agg(
        (pl.col("play_type") == "pass").mean().alias("rate")
    ).iter_rows(named=True):
        env[r["posteam"]]["neutral_pass"] = round(100 * r["rate"], 1)

    # red-zone trips: scrimmage drives that reached the 20 (see redzone.py for why
    # extra points are excluded)
    rz = in_window(pbp.filter((pl.col("yardline_100") <= 20) & pl.col("play_type").is_in(SCRIMMAGE_PLAYS)
                              & pl.col("posteam").is_not_null()), "posteam", "off")
    trips = rz.group_by(["game_id", "posteam", "defteam", "fixed_drive", "season", "week"]).agg(
        (pl.col("fixed_drive_result").drop_nulls().first() == "Touchdown").alias("scored")
    )
    for r in trips.group_by("posteam").agg(
        pl.len().alias("n"), pl.col("scored").sum().alias("td"),
        pl.struct(["season", "week"]).n_unique().alias("games"),
    ).iter_rows(named=True):
        env[r["posteam"]]["rz_trips"] = round(r["n"] / max(len(windows[r["posteam"]]["off"]), 1), 2)
        env[r["posteam"]]["rz_td"] = round(100 * r["td"] / r["n"], 1) if r["n"] else None
    dtrips = trips.join(
        pl.DataFrame([(t, s, w) for t, sd in windows.items() for (s, w) in sd["def"]],
                     schema=["defteam", "season", "week"], orient="row"),
        on=["defteam", "season", "week"], how="inner",
    )
    for r in dtrips.group_by("defteam").agg(
        pl.len().alias("n"), pl.col("scored").sum().alias("td")
    ).iter_rows(named=True):
        env[r["defteam"]]["def_rz_td"] = round(100 * r["td"] / r["n"], 1) if r["n"] else None

    if part is not None:
        dropbacks = pbp.filter(pl.col("qb_dropback") == 1).select(
            ["game_id", "play_id", "posteam", "defteam", "season", "week"]
        ).join(part.rename({"nflverse_game_id": "game_id"}), on=["game_id", "play_id"], how="inner")
        for r in in_window(dropbacks, "posteam", "off").group_by("posteam").agg(
            pl.col("was_pressure").cast(pl.Float64).mean().alias("p")
        ).iter_rows(named=True):
            env[r["posteam"]]["pressure_allowed"] = round(100 * r["p"], 1) if r["p"] is not None else None
        dwin = in_window(dropbacks, "defteam", "def")
        for r in dwin.group_by("defteam").agg(
            pl.col("was_pressure").cast(pl.Float64).mean().alias("p"),
            (pl.col("defense_man_zone_type") == "MAN_COVERAGE").sum().alias("man"),
            pl.col("defense_man_zone_type").is_in(["MAN_COVERAGE", "ZONE_COVERAGE"]).sum().alias("charted"),
        ).iter_rows(named=True):
            e = env[r["defteam"]]
            e["def_pressure"] = round(100 * r["p"], 1) if r["p"] is not None else None
            e["def_man"] = round(100 * r["man"] / r["charted"], 1) if r["charted"] else None

    # ranks across the league, 32 = most (pace, pressure) so a reader never has to
    # remember which direction is good for which column
    for key in ("pace", "neutral_pass", "rz_trips", "rz_td", "def_rz_td", "pressure_allowed",
                "def_pressure", "def_man"):
        teams = [t for t in env if env[t].get(key) is not None]
        for i, t in enumerate(sorted(teams, key=lambda t: env[t][key]), start=1):
            env[t][key + "_rank"] = i
    return dict(env)


# ── players ──────────────────────────────────────────────────────────────────

def player_profiles(rows: list[dict], pbp: pl.DataFrame, part: pl.DataFrame | None) -> dict[str, dict]:
    """Window and recent averages, usage trend, red-zone work and coverage splits."""
    by_player: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_player[r["player_id"]].append(r)

    # red-zone work and touchdowns from outside the 20, per player-game
    rz_work: dict[tuple, float] = defaultdict(float)
    team_rz: dict[tuple, float] = defaultdict(float)
    long_td: dict[tuple, float] = defaultdict(float)
    for r in pbp.filter(pl.col("play_type").is_in(["pass", "run"])).select(
        ["season", "week", "posteam", "yardline_100", "rusher_player_id", "receiver_player_id",
         "touchdown", "td_player_id"]
    ).iter_rows(named=True):
        g = (r["season"], r["week"])
        inside = (r["yardline_100"] or 99) <= 20
        if inside:
            if r["receiver_player_id"]:
                rz_work[(r["receiver_player_id"], *g)] += 1.0
                team_rz[(r["posteam"], *g)] += 1.0
            if r["rusher_player_id"]:
                rz_work[(r["rusher_player_id"], *g)] += 0.75
                team_rz[(r["posteam"], *g)] += 0.75
        elif r["touchdown"] == 1 and r["td_player_id"]:
            long_td[(r["td_player_id"], *g)] += 1.0

    cov: dict[str, dict] = defaultdict(lambda: {"man_t": 0, "man_y": 0.0, "zone_t": 0, "zone_y": 0.0})
    if part is not None:
        tg = pbp.filter((pl.col("pass_attempt") == 1) & pl.col("receiver_player_id").is_not_null()).select(
            ["game_id", "play_id", "receiver_player_id", "yards_gained"]
        ).join(part.rename({"nflverse_game_id": "game_id"}), on=["game_id", "play_id"], how="inner")
        for r in tg.iter_rows(named=True):
            kind = {"MAN_COVERAGE": "man", "ZONE_COVERAGE": "zone"}.get(r["defense_man_zone_type"])
            if kind:
                c = cov[r["receiver_player_id"]]
                c[kind + "_t"] += 1
                c[kind + "_y"] += float(r["yards_gained"] or 0)

    out: dict[str, dict] = {}
    for pid, games in by_player.items():
        games.sort(key=lambda r: (r["season"], r["week"]))
        win = games[-WINDOW:]
        recent = games[-RECENT:]
        last3 = games[-3:]
        n = len(win)

        def avg(rows_, key):
            return sum(r[key] for r in rows_) / len(rows_) if rows_ else 0.0

        pos = win[-1]["pos"]
        share_key = "car_share" if pos == "RB" else "tgt_share"
        rz_player = sum(rz_work.get((pid, r["season"], r["week"]), 0.0) for r in win)
        rz_team = sum(team_rz.get((r["team"], r["season"], r["week"]), 0.0) for r in win)
        c = cov.get(pid)
        out[pid] = {
            "name": win[-1]["name"],
            "pos": pos,
            "team": win[-1]["team"],
            # every game's team, so a board can tell a player who moved this year
            # (one game with the new club, sixteen with the old) from a veteran
            "win_teams": [r["team"] for r in win],
            "headshot": win[-1]["headshot_url"] or "",
            "games": n,
            "seasons": sorted({r["season"] for r in win}),
            "window": {s: round(avg(win, s), 2) for s in STATS},
            "recent": {s: round(avg(recent, s), 2) for s in STATS},
            "share": round(100 * avg(win, share_key), 1),
            "share_l3": round(100 * avg(last3, share_key), 1),
            "rz_share": round(100 * rz_player / rz_team, 1) if rz_team else 0.0,
            "rz_work_pg": round(rz_player / n, 2) if n else 0.0,
            "long_td_pg": round(sum(long_td.get((pid, r["season"], r["week"]), 0.0) for r in win) / n, 3) if n else 0.0,
            "log": [
                {"season": r["season"], "week": r["week"], "opp": r["opp"], "team": r["team"],
                 "role": r["role"], **{s: r[s] for s in STATS}}
                for r in games[-RECENT:]
            ],
            "cov": (
                {"man_ypt": round(c["man_y"] / c["man_t"], 2) if c["man_t"] else None, "man_t": c["man_t"],
                 "zone_ypt": round(c["zone_y"] / c["zone_t"], 2) if c["zone_t"] else None, "zone_t": c["zone_t"]}
                if c else None
            ),
        }
    return out


# ── the board for one game ───────────────────────────────────────────────────

def implied_totals(game: dict) -> dict[str, float] | None:
    """Split the total by the spread: favourite gets half the total plus half the line."""
    odds = game.get("odds") or {}
    total, details = odds.get("over_under"), odds.get("details") or ""
    if total is None:
        return None
    parts = details.split()
    try:
        fav, line = parts[0], abs(float(parts[1]))
    except (IndexError, ValueError):
        if details.strip().upper() in ("EVEN", "PK", "PICK"):
            return {game["away"]: total / 2, game["home"]: total / 2}
        return None
    fav = _fix(fav)
    dog = game["home"] if fav == game["away"] else game["away"]
    return {fav: round(total / 2 + line / 2, 1), dog: round(total / 2 - line / 2, 1)}


def _shrunk(mult: float, weight: float = 0.5, lo: float = 0.7, hi: float = 1.35) -> float:
    """Pull a multiplier halfway to neutral: one matchup is evidence, not a certainty."""
    return max(lo, min(hi, 1.0 + weight * (mult - 1.0)))


def _ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _leak_text(opp, role, d_role):
    """'BUF gives up 12% more than league to WR1s (3rd softest of 32)' -- the same
    words the matchup panels use, so the reason never needs a rank decoded."""
    pct = round((d_role["index"] - 1) * 100)
    of, soft_rank = d_role["of"], d_role["of"] + 1 - d_role["rank"]
    # name the end of the table it is nearer: "5th toughest", not "28th softest"
    tough_rank = of + 1 - soft_rank
    where = ("softest" if soft_rank == 1 else "toughest" if soft_rank == of
             else f"{_ordinal(soft_rank)} softest" if soft_rank <= of / 2
             else f"{_ordinal(tough_rank)} toughest")
    if pct == 0:
        return f"{opp} gives up league-average production to {role}s ({where} of {of})"
    more = "more" if pct > 0 else "less"
    return f"{opp} gives up {abs(pct)}% {more} than league to {role}s ({where} of {of})"


def board_player(card: dict, prof: dict | None, team: str, opp: str, implied: dict | None,
                 allowed: dict, league: dict, env: dict) -> dict:
    """One row of the board: projection, TD chance, grade and the reasons behind it."""
    pos, role = card["pos"], f'{card["pos"]}{card["rank"]}'
    base = {
        "name": card["name"], "pos": pos, "role": role, "team": team, "opp": opp,
        "player_id": card.get("player_id"),
        "headshot": card.get("headshot") or (prof or {}).get("headshot", ""),
    }
    if not prof or not prof["games"]:
        return {**base, "no_history": True, "grade": None, "reasons": [], "proj": {}, "td_chance": None}

    d_role = allowed.get(opp, {}).get(role) or {}
    l_role = league.get(role) or {}
    team_pts = (implied or {}).get(team)

    proj, notes = {}, {}
    for stat in PROJECT[pos]:
        mean = 0.6 * prof["window"][stat] + 0.4 * prof["recent"][stat]
        m_mult = _shrunk(d_role[stat] / l_role[stat]) if l_role.get(stat) and stat in d_role else 1.0
        s_mult = 1.0
        if stat in SCRIPTED and team_pts:
            s_mult = _shrunk(team_pts / LEAGUE_TEAM_POINTS, lo=0.85, hi=1.15)
        c_mult = 1.0
        cv, man = prof.get("cov"), env.get(opp, {}).get("def_man")
        if stat == "rec_yds" and cv and man is not None and cv["man_ypt"] and cv["zone_ypt"]:
            # his own yards per target, reweighted to this defense's man/zone mix;
            # thin samples lean on his overall rate so one big catch cannot swing it
            tot_t = cv["man_t"] + cv["zone_t"]
            overall = (cv["man_ypt"] * cv["man_t"] + cv["zone_ypt"] * cv["zone_t"]) / tot_t
            k = 30.0
            man_ypt = (cv["man_ypt"] * cv["man_t"] + overall * k) / (cv["man_t"] + k)
            zone_ypt = (cv["zone_ypt"] * cv["zone_t"] + overall * k) / (cv["zone_t"] + k)
            expect = (man / 100) * man_ypt + (1 - man / 100) * zone_ypt
            c_mult = _shrunk(expect / overall, lo=0.85, hi=1.15) if overall else 1.0
            # the text quotes his actual averages; the regressed rates only feed the maths,
            # and quoting them as "he averages" would contradict the raw split beside it
            notes["cov"] = {"mult": round(c_mult, 3), "man_ypt": round(cv["man_ypt"], 1),
                            "zone_ypt": round(cv["zone_ypt"], 1), "def_man": man}
        proj[stat] = round(mean * m_mult * s_mult * c_mult, 1)

    # touchdowns: red-zone work x trips x how often this defense lets a trip score,
    # plus the scores he gets from outside the 20
    e_team, e_opp = env.get(team, {}), env.get(opp, {})
    xtd = prof["long_td_pg"]
    if e_team.get("rz_trips") and e_opp.get("def_rz_td") is not None:
        xtd += (prof["rz_share"] / 100) * e_team["rz_trips"] * (e_opp["def_rz_td"] / 100)
    if pos == "QB":
        xtd = prof["window"]["rush_td"] * 0.9  # a QB's anytime TD is a rushing score
    td_chance = round(100 * (1 - math.exp(-xtd)))

    # grade: each part lands in [-1, 1], weighted, then mapped to 0-100 around 50.
    # Each part also carries `pct`, its edge in plain terms -- how far this factor sits
    # from normal for him -- which is what the page shows; grade points are the tooltip.
    parts = []
    if d_role.get("index"):
        parts.append(("matchup", _clamp((d_role["index"] - 1) / 0.30),
                      _leak_text(opp, role, d_role), 100 * (d_role["index"] - 1)))
    if team_pts:
        parts.append(("script", _clamp((team_pts - LEAGUE_TEAM_POINTS) / 6),
                      f"{team} implied for {team_pts:g} points (league average {LEAGUE_TEAM_POINTS:g})",
                      100 * (team_pts / LEAGUE_TEAM_POINTS - 1)))
    if "cov" in notes:
        cvn = notes["cov"]
        parts.append(("coverage", _clamp((cvn["mult"] - 1) / 0.10),
                      f'{opp} plays man {round(cvn["def_man"])}% · he averages {cvn["man_ypt"]} yds/tgt vs man, {cvn["zone_ypt"]} vs zone',
                      100 * (cvn["mult"] - 1)))
    share_name = {"RB": "carry share", "QB": None}.get(pos, "target share")
    if share_name:
        trend = prof["share_l3"] - prof["share"]
        parts.append(("usage", _clamp(trend / 7),
                      f"{share_name} {prof['share_l3']:g}% last 3 vs {prof['share']:g}% over {prof['games']} games",
                      100 * (prof["share_l3"] / prof["share"] - 1) if prof["share"] else None))

    weights = ({"matchup": .45, "script": .20, "coverage": .20, "usage": .15} if "cov" in notes
               else {"matchup": .60, "script": .25, "usage": .15})
    present = {k for k, _, _, _ in parts}
    scale = sum(w for k, w in weights.items() if k in present) or 1.0
    score = sum(weights[k] * v for k, v, _, _ in parts) / scale

    # Reliability: an edge only pays if he has the role to use it. Weight current
    # usage as heavily as the window, so a back whose carries just jumped counts.
    reliability, low_volume = 1.0, False
    if pos in FULL_SHARE:
        live_share = 0.5 * prof["share"] + 0.5 * prof["share_l3"]
        reliability = _clamp(live_share / FULL_SHARE[pos], 0.0, 1.0)
        low_volume = reliability < LOW_VOLUME
    grade = max(1, min(99, round(50 + 50 * score * reliability)))
    reasons = [{"part": k, "points": round(50 * weights[k] * v * reliability / scale, 1), "text": t,
                "pct": None if pct is None else round(pct)}
               for k, v, t, pct in parts]
    if reliability < 1:
        # shown as the discount on every edge above: counted at 45% reads as -55%
        reasons.append({"part": "volume", "points": None, "pct": round(100 * reliability) - 100,
                        "text": f"{share_name} only {0.5 * prof['share'] + 0.5 * prof['share_l3']:.0f}% -- "
                                f"edge counted at {round(100 * reliability)}% until he holds {FULL_SHARE[pos]:g}%"})

    return {
        **base,
        "games": prof["games"], "seasons": prof["seasons"],
        # "New team" means most of his sample was earned elsewhere. Comparing only his
        # latest game stopped working after Week 1: by then his latest game is already
        # with the new club, so nobody who moved was ever flagged.
        "team_games": sum(1 for t in prof["win_teams"] if t == team),
        "new_team": 2 * sum(1 for t in prof["win_teams"] if t == team) < prof["games"],
        "share": prof["share"] if share_name else None,
        "share_l3": prof["share_l3"] if share_name else None,
        "share_kind": share_name, "low_volume": low_volume, "reliability": round(reliability, 2),
        "rz_share": prof["rz_share"],
        "window": {s: prof["window"][s] for s in PROJECT[pos]},
        "recent": {s: prof["recent"][s] for s in PROJECT[pos]},
        "proj": proj, "td_chance": td_chance, "xtd": round(xtd, 3),
        "grade": grade, "reasons": reasons,
        "matchup": {"index": d_role.get("index"), "rank": d_role.get("rank"), "of": d_role.get("of"),
                    "td_index": d_role.get("td_index"),
                    "allowed": {s: round(d_role[s], 1) for s in PROJECT[pos] if s in d_role},
                    "league": {s: round(l_role[s], 1) for s in PROJECT[pos] if s in l_role}},
        "log": prof["log"],
        "cov": prof.get("cov"),
    }


def attach_game_boards(slate_games: list[dict], lineups: dict, season: int) -> dict:
    """Write `board` onto every game. Mutates in place; returns a short report."""
    frames = load_frames(season)
    rows = _player_rows(frames["weekly"])
    windows = _team_windows(frames["pbp"])
    allowed, league = defense_allowed(rows, windows)
    env = team_environment(frames["pbp"], frames["part"], windows)
    profiles = player_profiles(rows, frames["pbp"], frames["part"])

    graded = no_hist = 0
    for game in slate_games:
        implied = implied_totals(game)
        players = []
        for team, opp in ((game["away"], game["home"]), (game["home"], game["away"])):
            for pos in SKILL:
                for card in (lineups.get(team, {}).get(pos) or []):
                    row = board_player(card, profiles.get(card.get("player_id") or ""), team, opp,
                                       implied, allowed, league, env)
                    no_hist += bool(row.get("no_history"))
                    graded += row.get("grade") is not None
                    players.append(row)
        players.sort(key=lambda r: (r["grade"] is None, -(r["grade"] or 0)))
        game["board"] = {
            "implied": implied,
            "env": {t: env.get(t, {}) for t in (game["away"], game["home"])},
            "leaks": {t: {role: {k: v for k, v in (allowed.get(t, {}).get(role) or {}).items()
                                 if k in ("index", "rank", "of", "td_index", "fp")}
                          for role in ROLES}
                      for t in (game["away"], game["home"])},
            "players": players,
        }

    seasons_in = sorted({s for r in rows for s in [r["season"]]})
    return {"graded": graded, "no_history": no_hist, "seasons": seasons_in,
            "coverage_seasons": frames["coverage_seasons"]}
