"""Cheat-sheet aggregates for the NFL Research tab.

Every sheet in here is built from a free source:

    * nflverse play-by-play      -> rushing gaps, red zone, explosive plays,
                                    team defence, team share
    * nflverse FTN charting      -> team tendencies (motion / play-action / RPO /
                                    screen / no-huddle / blitz + box counts)
    * Pro-Football-Reference adv -> coverage players, receiving value
    * nflverse schedules (1999-) -> home-field advantage, power ratings, SOS
    * nflverse injuries/snaps/depth charts

Three sheets from PropFinder's set are deliberately absent: coverage-scheme
matchups, alignment matchups and offensive/defensive line matchups. All three
need charting we cannot get for free (participation data stopped after 2023;
route alignment and line grades are PFF/SIS products). Shipping a thin
imitation of them would be worse than not shipping them. Routes run and
yards-per-route-run are unavailable for the same reason.
"""
from __future__ import annotations

from collections import defaultdict

import nflreadpy as nfl
import polars as pl

POSITIONS = ("QB", "RB", "WR", "TE")

# nflverse spells a few clubs differently from ESPN; normalise to ESPN's codes.
# ESPN says WSH, nflverse says WAS -- mapping it the other way silently dropped
# Washington out of team stats, tendencies and power ratings, because the slate
# looked them up under the ESPN code and found nothing.
TEAM_FIX = {"LA": "LAR", "OAK": "LV", "SD": "LAC", "STL": "LAR", "WAS": "WSH"}

RUN_GAPS = (
    ("left", "end"),
    ("left", "tackle"),
    ("left", "guard"),
    ("middle", None),
    ("right", "guard"),
    ("right", "tackle"),
    ("right", "end"),
)


def gap_key(location: str | None, gap: str | None) -> str | None:
    if not location:
        return None
    if location == "middle":
        return "middle"
    if not gap:
        return None
    return f"{location}-{gap}"


GAP_KEYS = [gap_key(loc, gap) for loc, gap in RUN_GAPS]


def fix_team(code: str | None) -> str | None:
    if not code:
        return None
    return TEAM_FIX.get(code, code)


def _pct_of_fraction(v, nd: int = 1) -> float | None:
    """PFR ships rate columns as 0-1 fractions; the sheet speaks 0-100."""
    if v is None:
        return None
    return round(float(v) * 100.0, nd)


def _rate(num: float, den: float, nd: int = 1) -> float | None:
    if not den:
        return None
    return round(100.0 * num / den, nd)


def _avg(total: float, n: float, nd: int = 2) -> float | None:
    if not n:
        return None
    return round(total / n, nd)


# --------------------------------------------------------------------------
# play-by-play driven sheets
# --------------------------------------------------------------------------


def load_pbp(season: int) -> pl.DataFrame:
    """Regular-season plays for one season, teams normalised to ESPN codes."""
    pbp = nfl.load_pbp(seasons=[season])
    pbp = pbp.filter(pl.col("season_type") == "REG")
    return pbp.with_columns(
        pl.col("posteam").replace(TEAM_FIX).alias("posteam"),
        pl.col("defteam").replace(TEAM_FIX).alias("defteam"),
    )


def rushing_gaps(pbp: pl.DataFrame) -> dict:
    """Where backs run, and where defences give it up.

    PropFinder's rushing sheet leads on gap mix -- which hole a back actually
    uses -- so the same split is what makes it useful here.
    """
    runs = pbp.filter(
        (pl.col("rush_attempt") == 1)
        & pl.col("rusher_player_name").is_not_null()
        & pl.col("run_location").is_not_null()
    ).with_columns(
        pl.struct(["run_location", "run_gap"])
        .map_elements(lambda s: gap_key(s["run_location"], s["run_gap"]), return_dtype=pl.Utf8)
        .alias("gap")
    ).filter(pl.col("gap").is_not_null())

    players: dict[tuple[str, str], dict] = {}
    for row in runs.select(
        ["posteam", "rusher_player_name", "gap", "yards_gained", "success", "rush_touchdown", "epa"]
    ).iter_rows(named=True):
        key = (row["posteam"], row["rusher_player_name"])
        rec = players.setdefault(
            key,
            {
                "team": row["posteam"],
                "name": row["rusher_player_name"],
                "att": 0,
                "yds": 0.0,
                "td": 0,
                "success": 0,
                "epa": 0.0,
                "gaps": {g: {"att": 0, "yds": 0.0} for g in GAP_KEYS},
            },
        )
        rec["att"] += 1
        rec["yds"] += row["yards_gained"] or 0
        rec["td"] += int(row["rush_touchdown"] or 0)
        rec["success"] += int(row["success"] or 0)
        rec["epa"] += row["epa"] or 0.0
        bucket = rec["gaps"].get(row["gap"])
        if bucket is not None:
            bucket["att"] += 1
            bucket["yds"] += row["yards_gained"] or 0

    out_players = []
    for rec in players.values():
        if rec["att"] < 20:
            continue
        mix = {}
        for g, b in rec["gaps"].items():
            mix[g] = {
                "att": b["att"],
                "share": _rate(b["att"], rec["att"]),
                "ypc": _avg(b["yds"], b["att"]),
            }
        out_players.append(
            {
                "team": rec["team"],
                "name": rec["name"],
                "att": rec["att"],
                "yds": round(rec["yds"], 1),
                "ypc": _avg(rec["yds"], rec["att"]),
                "td": rec["td"],
                "success_pct": _rate(rec["success"], rec["att"]),
                "epa_play": _avg(rec["epa"], rec["att"], 3),
                "gaps": mix,
            }
        )
    out_players.sort(key=lambda r: r["att"], reverse=True)

    defenses: dict[str, dict] = {}
    for row in runs.select(["defteam", "gap", "yards_gained", "success"]).iter_rows(named=True):
        rec = defenses.setdefault(
            row["defteam"],
            {"team": row["defteam"], "att": 0, "yds": 0.0, "success": 0,
             "gaps": {g: {"att": 0, "yds": 0.0, "success": 0} for g in GAP_KEYS}},
        )
        rec["att"] += 1
        rec["yds"] += row["yards_gained"] or 0
        rec["success"] += int(row["success"] or 0)
        b = rec["gaps"].get(row["gap"])
        if b is not None:
            b["att"] += 1
            b["yds"] += row["yards_gained"] or 0
            b["success"] += int(row["success"] or 0)

    out_def = {}
    for team, rec in defenses.items():
        out_def[team] = {
            "att": rec["att"],
            "ypc": _avg(rec["yds"], rec["att"]),
            "success_pct": _rate(rec["success"], rec["att"]),
            "gaps": {
                g: {"att": b["att"], "ypc": _avg(b["yds"], b["att"]),
                    "success_pct": _rate(b["success"], b["att"])}
                for g, b in rec["gaps"].items()
            },
        }

    lg_ypc = _avg(runs["yards_gained"].sum(), runs.height)
    return {"gap_keys": GAP_KEYS, "league_ypc": lg_ypc, "players": out_players, "defense": out_def}


def red_zone(pbp: pl.DataFrame) -> dict:
    """Inside-the-20 usage per player and what each defence concedes there."""
    rz = pbp.filter((pl.col("yardline_100") <= 20) & pl.col("play_type").is_in(["run", "pass"]))

    players: dict[tuple[str, str], dict] = {}

    def _bump(team, name, field, yards=0, td=0):
        if not name:
            return
        rec = players.setdefault(
            (team, name),
            {"team": team, "name": name, "rz_tgt": 0, "rz_rec": 0, "rz_car": 0,
             "rz_td": 0, "rz_yds": 0.0, "in10_tgt": 0, "in10_car": 0},
        )
        rec[field] += 1
        rec["rz_yds"] += yards or 0
        rec["rz_td"] += td

    for row in rz.select(
        ["posteam", "yardline_100", "rusher_player_name", "receiver_player_name",
         "complete_pass", "yards_gained", "rush_touchdown", "pass_touchdown"]
    ).iter_rows(named=True):
        inside10 = (row["yardline_100"] or 99) <= 10
        if row["rusher_player_name"]:
            _bump(row["posteam"], row["rusher_player_name"], "rz_car",
                  row["yards_gained"], int(row["rush_touchdown"] or 0))
            if inside10:
                players[(row["posteam"], row["rusher_player_name"])]["in10_car"] += 1
        if row["receiver_player_name"]:
            _bump(row["posteam"], row["receiver_player_name"], "rz_tgt",
                  row["yards_gained"] if row["complete_pass"] else 0,
                  int(row["pass_touchdown"] or 0))
            rec = players[(row["posteam"], row["receiver_player_name"])]
            if row["complete_pass"]:
                rec["rz_rec"] += 1
            if inside10:
                rec["in10_tgt"] += 1

    team_touch: dict[str, int] = defaultdict(int)
    for rec in players.values():
        team_touch[rec["team"]] += rec["rz_car"] + rec["rz_tgt"]

    out_players = []
    for rec in players.values():
        touches = rec["rz_car"] + rec["rz_tgt"]
        if touches < 4:
            continue
        out_players.append(
            {
                **{k: v for k, v in rec.items() if k != "rz_yds"},
                "rz_touches": touches,
                "rz_share": _rate(touches, team_touch[rec["team"]]),
                "in10_touches": rec["in10_car"] + rec["in10_tgt"],
            }
        )
    out_players.sort(key=lambda r: r["rz_touches"], reverse=True)

    defenses: dict[str, dict] = {}
    for row in rz.select(["defteam", "touchdown", "play_type", "epa"]).iter_rows(named=True):
        rec = defenses.setdefault(row["defteam"], {"plays": 0, "td": 0, "epa": 0.0, "rush": 0, "pass": 0})
        rec["plays"] += 1
        rec["td"] += int(row["touchdown"] or 0)
        rec["epa"] += row["epa"] or 0.0
        rec[row["play_type"]] = rec.get(row["play_type"], 0) + 1

    out_def = {
        team: {
            "rz_plays": rec["plays"],
            "rz_td": rec["td"],
            "rz_td_pct": _rate(rec["td"], rec["plays"]),
            "rz_epa_play": _avg(rec["epa"], rec["plays"], 3),
            "rush_pct": _rate(rec.get("run", 0), rec["plays"]),
        }
        for team, rec in defenses.items()
    }
    lg_td = _rate(sum(r["td"] for r in defenses.values()), sum(r["plays"] for r in defenses.values()))
    return {"league_rz_td_pct": lg_td, "players": out_players, "defense": out_def}


def explosive_plays(pbp: pl.DataFrame) -> dict:
    """20+ yard receptions, 10+/20+ yard carries -- for players and defences."""
    plays = pbp.filter(pl.col("play_type").is_in(["run", "pass"]))

    players: dict[tuple[str, str], dict] = {}
    for row in plays.select(
        ["posteam", "play_type", "rusher_player_name", "receiver_player_name",
         "complete_pass", "yards_gained"]
    ).iter_rows(named=True):
        yds = row["yards_gained"] or 0
        if row["play_type"] == "run" and row["rusher_player_name"]:
            rec = players.setdefault(
                (row["posteam"], row["rusher_player_name"]),
                {"team": row["posteam"], "name": row["rusher_player_name"],
                 "car": 0, "rec": 0, "rush10": 0, "rush20": 0, "rec20": 0, "long_rush": 0, "long_rec": 0},
            )
            rec["car"] += 1
            rec["rush10"] += int(yds >= 10)
            rec["rush20"] += int(yds >= 20)
            rec["long_rush"] = max(rec["long_rush"], yds)
        elif row["play_type"] == "pass" and row["receiver_player_name"] and row["complete_pass"]:
            rec = players.setdefault(
                (row["posteam"], row["receiver_player_name"]),
                {"team": row["posteam"], "name": row["receiver_player_name"],
                 "car": 0, "rec": 0, "rush10": 0, "rush20": 0, "rec20": 0, "long_rush": 0, "long_rec": 0},
            )
            rec["rec"] += 1
            rec["rec20"] += int(yds >= 20)
            rec["long_rec"] = max(rec["long_rec"], yds)

    out_players = []
    for rec in players.values():
        if rec["car"] + rec["rec"] < 20:
            continue
        out_players.append(
            {
                **rec,
                "rush10_rate": _rate(rec["rush10"], rec["car"]),
                "rush20_rate": _rate(rec["rush20"], rec["car"]),
                "rec20_rate": _rate(rec["rec20"], rec["rec"]),
            }
        )
    out_players.sort(key=lambda r: (r["rec20"] + r["rush20"]), reverse=True)

    defenses: dict[str, dict] = {}
    for row in plays.select(
        ["defteam", "play_type", "complete_pass", "yards_gained"]
    ).iter_rows(named=True):
        yds = row["yards_gained"] or 0
        rec = defenses.setdefault(
            row["defteam"],
            {"car": 0, "rec": 0, "rush10": 0, "rush20": 0, "rec20": 0},
        )
        if row["play_type"] == "run":
            rec["car"] += 1
            rec["rush10"] += int(yds >= 10)
            rec["rush20"] += int(yds >= 20)
        elif row["complete_pass"]:
            rec["rec"] += 1
            rec["rec20"] += int(yds >= 20)

    out_def = {
        team: {
            **rec,
            "rush10_rate": _rate(rec["rush10"], rec["car"]),
            "rush20_rate": _rate(rec["rush20"], rec["car"]),
            "rec20_rate": _rate(rec["rec20"], rec["rec"]),
        }
        for team, rec in defenses.items()
    }
    return {"players": out_players, "defense": out_def}


def team_defense(pbp: pl.DataFrame) -> dict:
    """EPA / success / yards per play allowed, overall and split pass vs rush."""
    plays = pbp.filter(pl.col("play_type").is_in(["run", "pass"]))
    out: dict[str, dict] = {}
    for row in plays.select(
        ["defteam", "posteam", "play_type", "yards_gained", "epa", "success", "sack", "interception"]
    ).iter_rows(named=True):
        for side, team in (("def", row["defteam"]), ("off", row["posteam"])):
            rec = out.setdefault(team, {})
            b = rec.setdefault(
                side,
                {"plays": 0, "yds": 0.0, "epa": 0.0, "success": 0, "sacks": 0, "int": 0,
                 "pass_plays": 0, "pass_epa": 0.0, "rush_plays": 0, "rush_epa": 0.0},
            )
            b["plays"] += 1
            b["yds"] += row["yards_gained"] or 0
            b["epa"] += row["epa"] or 0.0
            b["success"] += int(row["success"] or 0)
            b["sacks"] += int(row["sack"] or 0)
            b["int"] += int(row["interception"] or 0)
            if row["play_type"] == "pass":
                b["pass_plays"] += 1
                b["pass_epa"] += row["epa"] or 0.0
            else:
                b["rush_plays"] += 1
                b["rush_epa"] += row["epa"] or 0.0

    shaped: dict[str, dict] = {}
    for team, rec in out.items():
        shaped[team] = {}
        for side, b in rec.items():
            shaped[team][side] = {
                "plays": b["plays"],
                "ypp": _avg(b["yds"], b["plays"]),
                "epa_play": _avg(b["epa"], b["plays"], 3),
                "success_pct": _rate(b["success"], b["plays"]),
                "pass_epa_play": _avg(b["pass_epa"], b["pass_plays"], 3),
                "rush_epa_play": _avg(b["rush_epa"], b["rush_plays"], 3),
                "sacks": b["sacks"],
                "int": b["int"],
                "pass_rate": _rate(b["pass_plays"], b["plays"]),
            }
    return shaped


def team_share(pbp: pl.DataFrame) -> dict:
    """Target / carry share of team volume, plus a touch mix per player."""
    plays = pbp.filter(pl.col("play_type").is_in(["run", "pass"]))
    team_tot: dict[str, dict] = defaultdict(lambda: {"tgt": 0, "car": 0})
    players: dict[tuple[str, str], dict] = {}
    for row in plays.select(
        ["posteam", "rusher_player_name", "receiver_player_name", "complete_pass", "yards_gained"]
    ).iter_rows(named=True):
        team = row["posteam"]
        if row["rusher_player_name"]:
            team_tot[team]["car"] += 1
            rec = players.setdefault(
                (team, row["rusher_player_name"]),
                {"team": team, "name": row["rusher_player_name"], "tgt": 0, "rec": 0,
                 "car": 0, "rec_yds": 0.0, "rush_yds": 0.0},
            )
            rec["car"] += 1
            rec["rush_yds"] += row["yards_gained"] or 0
        if row["receiver_player_name"]:
            team_tot[team]["tgt"] += 1
            rec = players.setdefault(
                (team, row["receiver_player_name"]),
                {"team": team, "name": row["receiver_player_name"], "tgt": 0, "rec": 0,
                 "car": 0, "rec_yds": 0.0, "rush_yds": 0.0},
            )
            rec["tgt"] += 1
            if row["complete_pass"]:
                rec["rec"] += 1
                rec["rec_yds"] += row["yards_gained"] or 0

    out = []
    for rec in players.values():
        touches = rec["car"] + rec["tgt"]
        if touches < 15:
            continue
        tot = team_tot[rec["team"]]
        out.append(
            {
                **rec,
                "rec_yds": round(rec["rec_yds"], 1),
                "rush_yds": round(rec["rush_yds"], 1),
                "touches": touches,
                "tgt_share": _rate(rec["tgt"], tot["tgt"]),
                "car_share": _rate(rec["car"], tot["car"]),
                "rec_mix": _rate(rec["tgt"], touches),
            }
        )
    out.sort(key=lambda r: r["touches"], reverse=True)
    return {"players": out}


def hit_rates(pbp: pl.DataFrame) -> dict:
    """Per-game totals per player so the front end can compute hit rate vs any line."""
    plays = pbp.filter(pl.col("play_type").is_in(["run", "pass"]))
    per_game: dict[tuple[str, str, str], dict] = {}
    for row in plays.select(
        ["game_id", "week", "posteam", "rusher_player_name", "receiver_player_name",
         "complete_pass", "yards_gained", "rush_touchdown", "pass_touchdown"]
    ).iter_rows(named=True):
        for name, kind in ((row["rusher_player_name"], "rush"), (row["receiver_player_name"], "rec")):
            if not name:
                continue
            key = (row["posteam"], name, row["game_id"])
            rec = per_game.setdefault(
                key,
                {"team": row["posteam"], "name": name, "week": row["week"],
                 "rush_yds": 0.0, "rec_yds": 0.0, "rec": 0, "tgt": 0, "car": 0, "td": 0},
            )
            if kind == "rush":
                rec["car"] += 1
                rec["rush_yds"] += row["yards_gained"] or 0
                rec["td"] += int(row["rush_touchdown"] or 0)
            else:
                rec["tgt"] += 1
                if row["complete_pass"]:
                    rec["rec"] += 1
                    rec["rec_yds"] += row["yards_gained"] or 0
                    rec["td"] += int(row["pass_touchdown"] or 0)

    grouped: dict[tuple[str, str], list] = defaultdict(list)
    for (team, name, _gid), rec in per_game.items():
        grouped[(team, name)].append(rec)

    out = []
    for (team, name), games in grouped.items():
        if len(games) < 4:
            continue
        games.sort(key=lambda g: g["week"])
        out.append(
            {
                "team": team,
                "name": name,
                "games": [
                    {"week": g["week"], "rush_yds": round(g["rush_yds"], 1),
                     "rec_yds": round(g["rec_yds"], 1), "rec": g["rec"],
                     "tgt": g["tgt"], "car": g["car"], "td": g["td"]}
                    for g in games
                ],
            }
        )
    out.sort(key=lambda r: len(r["games"]), reverse=True)
    return {"players": out}


# --------------------------------------------------------------------------
# charting / advanced-stat sheets
# --------------------------------------------------------------------------


def team_tendencies(season: int, pbp: pl.DataFrame) -> dict:
    """Motion / play-action / RPO / screen / no-huddle / blitz rates from FTN.

    This is the honest free stand-in for PropFinder's scheme tendencies. It does
    NOT contain coverage shells -- nflverse participation data stopped after
    2023 and there is no free replacement.
    """
    try:
        ftn = nfl.load_ftn_charting(seasons=[season])
    except Exception:
        return {}
    # pbp ships play_id as f64 and FTN as i32; polars will not join across that.
    keys = pbp.select(["game_id", "play_id", "posteam", "defteam"]).rename(
        {"game_id": "nflverse_game_id", "play_id": "nflverse_play_id"}
    ).with_columns(pl.col("nflverse_play_id").cast(pl.Int64))
    ftn = ftn.with_columns(pl.col("nflverse_play_id").cast(pl.Int64))
    joined = ftn.join(keys, on=["nflverse_game_id", "nflverse_play_id"], how="inner")

    off: dict[str, dict] = defaultdict(lambda: defaultdict(float))
    dfs: dict[str, dict] = defaultdict(lambda: defaultdict(float))
    for row in joined.select(
        ["posteam", "defteam", "is_motion", "is_play_action", "is_rpo", "is_screen_pass",
         "is_no_huddle", "n_blitzers", "n_pass_rushers", "n_defense_box", "n_offense_backfield"]
    ).iter_rows(named=True):
        o = off[row["posteam"]]
        o["plays"] += 1
        for flag in ("is_motion", "is_play_action", "is_rpo", "is_screen_pass", "is_no_huddle"):
            o[flag] += 1 if row[flag] else 0
        backfield = row["n_offense_backfield"] or 0
        if backfield > 0:
            o["backfield_sum"] += backfield
            o["backfield_n"] += 1
        d = dfs[row["defteam"]]
        d["plays"] += 1
        # FTN encodes "not charted on this play" as 0, not null. Averaging the
        # zeros in drags every number toward nothing -- pass rushers came out at
        # 2.1 and box count at 4.9, both impossible. Count only charted plays.
        rushers = row["n_pass_rushers"] or 0
        if rushers > 0:
            d["rushers_sum"] += rushers
            d["rushers_n"] += 1
            d["blitz_n"] += 1
            d["blitz"] += 1 if (row["n_blitzers"] or 0) > 0 else 0
        box = row["n_defense_box"] or 0
        if box > 0:
            d["box_sum"] += box
            d["box_n"] += 1

    out: dict[str, dict] = {}
    for team, o in off.items():
        if not team:  # plays with no possession team (kickoffs slipping the filter)
            continue
        out.setdefault(team, {})["offense"] = {
            "plays": int(o["plays"]),
            "motion_pct": _rate(o["is_motion"], o["plays"]),
            "play_action_pct": _rate(o["is_play_action"], o["plays"]),
            "rpo_pct": _rate(o["is_rpo"], o["plays"]),
            "screen_pct": _rate(o["is_screen_pass"], o["plays"]),
            "no_huddle_pct": _rate(o["is_no_huddle"], o["plays"]),
            "avg_backfield": _avg(o["backfield_sum"], o["backfield_n"]),
        }
    for team, d in dfs.items():
        if not team:
            continue
        out.setdefault(team, {})["defense"] = {
            "plays": int(d["plays"]),
            "blitz_pct": _rate(d["blitz"], d["blitz_n"]),
            "avg_pass_rushers": _avg(d["rushers_sum"], d["rushers_n"]),
            "avg_box": _avg(d["box_sum"], d["box_n"]),
        }
    return out


def coverage_players(season: int) -> dict:
    """Defensive-back results from PFR advanced stats.

    Not coverage *scheme* -- this is what actually happened when the man was
    thrown at: completion rate allowed, yards per target, passer rating allowed,
    missed-tackle rate.
    """
    try:
        df = nfl.load_pfr_advstats(seasons=[season], stat_type="def", summary_level="season")
    except Exception:
        return {"players": []}
    out = []
    for row in df.iter_rows(named=True):
        tgt = row.get("tgt") or 0
        if tgt < 20:
            continue
        out.append(
            {
                "name": row.get("player"),
                "team": fix_team(row.get("tm")),
                "pos": row.get("pos"),
                "g": row.get("g"),
                "tgt": tgt,
                "cmp": row.get("cmp"),
                "cmp_pct": _pct_of_fraction(row.get("cmp_percent")),
                "yds": row.get("yds"),
                "yds_tgt": row.get("yds_tgt"),
                "td": row.get("td"),
                "int": row.get("int"),
                "rating_allowed": row.get("rat"),
                "dadot": row.get("dadot"),
                "yac": row.get("yac"),
                "missed_tkl_pct": _pct_of_fraction(row.get("m_tkl_percent")),
                "pressures": row.get("prss"),
                "blitz": row.get("bltz"),
            }
        )
    out.sort(key=lambda r: (r["rating_allowed"] if r["rating_allowed"] is not None else 999))
    return {"players": out}


def receiving_value(season: int) -> dict:
    """Receiver efficiency from PFR advanced stats (aDOT, YAC, drops, broken tackles)."""
    try:
        df = nfl.load_pfr_advstats(seasons=[season], stat_type="rec", summary_level="season")
    except Exception:
        return {"players": []}
    out = []
    for row in df.iter_rows(named=True):
        tgt = row.get("tgt") or 0
        if tgt < 20:
            continue
        out.append(
            {
                "name": row.get("player"),
                "team": fix_team(row.get("tm")),
                "pos": row.get("pos"),
                "g": row.get("g"),
                "tgt": tgt,
                "rec": row.get("rec"),
                "yds": row.get("yds"),
                "td": row.get("td"),
                "adot": row.get("adot"),
                "ybc_r": row.get("ybc_r"),
                "yac_r": row.get("yac_r"),
                "brk_tkl": row.get("brk_tkl"),
                "drop_pct": _pct_of_fraction(row.get("drop_percent")),
                "rating_when_targeted": row.get("rat"),
            }
        )
    out.sort(key=lambda r: (r["yds"] or 0), reverse=True)
    return {"players": out}


# --------------------------------------------------------------------------
# schedule-driven sheets
# --------------------------------------------------------------------------


def home_field_advantage(through_season: int, first_season: int = 1999) -> dict:
    """Average home margin by season -- PropFinder's 1999-onward chart, free."""
    seasons = list(range(first_season, through_season + 1))
    try:
        sched = nfl.load_schedules(seasons=seasons)
    except Exception:
        return {"seasons": []}
    done = sched.filter(
        pl.col("home_score").is_not_null()
        & pl.col("away_score").is_not_null()
        & (pl.col("game_type") == "REG")
    )
    rows = []
    for season in seasons:
        yr = done.filter(pl.col("season") == season)
        if not yr.height:
            continue
        margins = (yr["home_score"] - yr["away_score"]).to_list()
        wins = sum(1 for m in margins if m > 0)
        rows.append(
            {
                "season": season,
                "games": len(margins),
                "avg_margin": round(sum(margins) / len(margins), 2),
                "home_win_pct": _rate(wins, len(margins)),
            }
        )
    overall = _avg(sum(r["avg_margin"] * r["games"] for r in rows), sum(r["games"] for r in rows))
    return {"seasons": rows, "all_time_avg_margin": overall}


def power_ratings(pbp: pl.DataFrame, season: int) -> dict:
    """EPA-based team ratings plus strength of schedule, from free data only."""
    plays = pbp.filter(pl.col("play_type").is_in(["run", "pass"]))
    agg: dict[str, dict] = defaultdict(lambda: {"off_epa": 0.0, "off_n": 0, "def_epa": 0.0, "def_n": 0})
    for row in plays.select(["posteam", "defteam", "epa"]).iter_rows(named=True):
        e = row["epa"] or 0.0
        agg[row["posteam"]]["off_epa"] += e
        agg[row["posteam"]]["off_n"] += 1
        agg[row["defteam"]]["def_epa"] += e
        agg[row["defteam"]]["def_n"] += 1

    ratings = {}
    for team, a in agg.items():
        off = _avg(a["off_epa"], a["off_n"], 4) or 0.0
        dfn = _avg(a["def_epa"], a["def_n"], 4) or 0.0
        ratings[team] = {"off_epa": off, "def_epa": dfn, "net_epa": round(off - dfn, 4)}

    # Scale net EPA/play to a points-per-game style number so it reads like a
    # power rating rather than a decimal nobody can eyeball. ~63 plays/side.
    for team, r in ratings.items():
        r["rating"] = round(r["net_epa"] * 63, 2)

    try:
        sched = nfl.load_schedules(seasons=[season])
        sched = sched.filter(pl.col("game_type") == "REG")
    except Exception:
        sched = None

    sos: dict[str, dict] = {}
    if sched is not None:
        opp: dict[str, list] = defaultdict(list)
        played: dict[str, list] = defaultdict(list)
        for row in sched.select(
            ["home_team", "away_team", "home_score", "away_score"]
        ).iter_rows(named=True):
            h, a = fix_team(row["home_team"]), fix_team(row["away_team"])
            complete = row["home_score"] is not None
            opp[h].append(a)
            opp[a].append(h)
            if complete:
                played[h].append(a)
                played[a].append(h)
        for team, all_opps in opp.items():
            def _mean(names):
                vals = [ratings[o]["rating"] for o in names if o in ratings]
                return round(sum(vals) / len(vals), 2) if vals else None

            done_opps = played.get(team, [])
            left = all_opps[len(done_opps):]
            sos[team] = {
                "sos_full": _mean(all_opps),
                "sos_played": _mean(done_opps),
                "sos_left": _mean(left),
                "games": len(all_opps),
            }

    out = []
    for team, r in ratings.items():
        out.append({"team": team, **r, **sos.get(team, {})})
    out.sort(key=lambda r: r["rating"], reverse=True)
    for i, r in enumerate(out, 1):
        r["rank"] = i
    return {"teams": out}


# --------------------------------------------------------------------------
# roster context
# --------------------------------------------------------------------------


def roster_context(season: int, teams: set[str]) -> dict:
    """Injuries, snap shares and depth chart for the slate's teams."""
    out: dict[str, dict] = {t: {"injuries": [], "snaps": [], "depth": []} for t in teams}

    try:
        inj = nfl.load_injuries(seasons=[season])
        # Take each club's own most recent report. A single league-wide max week
        # leaves every team that was on bye -- or whose season ended earlier --
        # showing an empty injury list.
        latest = (
            inj.group_by("team").agg(pl.col("week").max().alias("week"))
        )
        inj = inj.join(latest, on=["team", "week"], how="inner")
        for row in inj.iter_rows(named=True):
            team = fix_team(row.get("team"))
            if team in out:
                out[team]["injuries"].append(
                    {
                        "name": row.get("full_name"),
                        "pos": row.get("position"),
                        "status": row.get("report_status") or row.get("practice_status"),
                        "injury": row.get("report_primary_injury"),
                        "week": row.get("week"),
                    }
                )
    except Exception:
        pass

    try:
        snaps = nfl.load_snap_counts(seasons=[season])
        agg = (
            snaps.group_by(["team", "player", "position"])
            .agg(
                pl.col("offense_pct").mean().alias("off_pct"),
                pl.col("defense_pct").mean().alias("def_pct"),
                pl.len().alias("games"),
            )
        )
        for row in agg.iter_rows(named=True):
            team = fix_team(row.get("team"))
            if team in out and (row.get("off_pct") or 0) > 0.05:
                out[team]["snaps"].append(
                    {
                        "name": row.get("player"),
                        "pos": row.get("position"),
                        "off_pct": round((row.get("off_pct") or 0) * 100, 1),
                        "games": row.get("games"),
                    }
                )
        for team in out:
            out[team]["snaps"].sort(key=lambda r: r["off_pct"], reverse=True)
            out[team]["snaps"] = out[team]["snaps"][:24]
    except Exception:
        pass

    try:
        depth = nfl.load_depth_charts(seasons=[season])
        wk = depth["week"].max()
        depth = depth.filter(pl.col("week") == wk)
        for row in depth.iter_rows(named=True):
            team = fix_team(row.get("team") or row.get("club_code"))
            if team in out:
                out[team]["depth"].append(
                    {
                        "name": row.get("player_name") or row.get("full_name"),
                        "pos": row.get("depth_position") or row.get("position"),
                        "rank": row.get("depth_team"),
                    }
                )
    except Exception:
        pass

    return out


# --------------------------------------------------------------------------


def build_cheatsheets(stats_season: int, teams: set[str]) -> dict:
    """Everything the Research tab's sheets need, in one payload."""
    pbp = load_pbp(stats_season)
    return {
        "stats_season": stats_season,
        "rushing_gaps": rushing_gaps(pbp),
        "red_zone": red_zone(pbp),
        "explosive": explosive_plays(pbp),
        "team_stats": team_defense(pbp),
        "team_share": team_share(pbp),
        "hit_rates": hit_rates(pbp),
        "tendencies": team_tendencies(stats_season, pbp),
        "coverage_players": coverage_players(stats_season),
        "receiving_value": receiving_value(stats_season),
        "power_ratings": power_ratings(pbp, stats_season),
        "hfa": home_field_advantage(stats_season),
        "roster": roster_context(stats_season, teams),
    }
