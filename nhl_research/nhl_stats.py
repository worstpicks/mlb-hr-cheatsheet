"""Load + aggregate NHL per-game player stats for the NHL Research tab.

Source (free, no key): NHL.com's public stats API
    https://api.nhle.com/stats/rest/en/skater/summary?isGame=true...

This is hockey's answer to nflverse. Three reports carry everything the page
needs, each one row per player per game:

    skater/summary   goals, assists, points, shots, TOI, power play, +/-
    skater/realtime  hits, blocks, takeaways, giveaways, missed shots, first goal
    goalie/summary   saves, shots against, goals against, save %, starts

The API answers 100 rows at a time and refuses to page past 10,000, while a full
season of skaters is roughly 47,000 rows. So every pull is chunked by team --
about 1,500 rows a club, comfortably inside the ceiling -- and cached on disk, so
a rebuild costs nothing.

Produces:
    * per-player per-game averages over a rolling window, plus a full game log
    * per-team "allowed to position" averages, overall and by line rank
      (C1/C2..., D1/D2..., ranked within each game by ice time)
"""
from __future__ import annotations

import gzip
import json
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CACHE = Path(__file__).resolve().parent / "cache"
REST = "https://api.nhle.com/stats/rest/en"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0 Safari/537.36"
PAGE = 100          # the API's hard ceiling per request
MAX_OFFSET = 10000  # ...and it will not page past this

# Skater positions, in the order the page stacks them. The feed's positionCode
# is C / L / R / D; goalies come from a separate report.
POSITIONS = ("C", "L", "R", "D", "G")
POS_LABEL = {"C": "Centers", "L": "Left Wing", "R": "Right Wing", "D": "Defense", "G": "Goalies"}

# The 32 clubs. Held as a constant because the pull is chunked by team and a
# roster feed would be one more round trip for something that does not change.
TEAMS = (
    "ANA", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL", "DAL", "DET",
    "EDM", "FLA", "LAK", "MIN", "MTL", "NJD", "NSH", "NYI", "NYR", "OTT",
    "PHI", "PIT", "SEA", "SJS", "STL", "TBL", "TOR", "UTA", "VAN", "VGK",
    "WPG", "WSH",
)

# ── stat keys ───────────────────────────────────────────────────────────────
# output key -> column on skater/summary
SUMMARY_COLUMNS = {
    "g": "goals",
    "a": "assists",
    "p": "points",
    "sog": "shots",
    "pim": "penaltyMinutes",
    "pm": "plusMinus",
    "pp_g": "ppGoals",
    "pp_p": "ppPoints",
    "sh_g": "shGoals",
    "sh_p": "shPoints",
    "ev_g": "evGoals",
    "ev_p": "evPoints",
    "gwg": "gameWinningGoals",
    "otg": "otGoals",
    "toi": "timeOnIcePerGame",   # seconds in that game
}
# output key -> column on skater/realtime
REALTIME_COLUMNS = {
    "hits": "hits",
    "blk": "blockedShots",
    "tk": "takeaways",
    "gv": "giveaways",
    "msog": "missedShots",
    "satt": "totalShotAttempts",
    "first_g": "firstGoals",
    "en_g": "emptyNetGoals",
}
# output key -> column on goalie/summary
GOALIE_COLUMNS = {
    "sv": "saves",
    "sa": "shotsAgainst",
    "ga": "goalsAgainst",
    "sv_pct": "savePct",
    "so": "shutouts",
    "start": "gamesStarted",
    "win": "wins",
    "toi": "timeOnIce",
}

# Derived on the way out rather than read off a column.
DERIVED_KEYS = ("sog_1", "sog_2", "sog_3", "sog_4", "pts_1", "pts_2", "g_1", "a_1", "blk_1", "blk_2", "hits_1", "hits_3")
# Shot quality, merged in from play-by-play (nhl_research/shot_quality.py).
# Declared here so the aggregates, the league baseline and the allowed-by-slot
# tables all carry them without a second code path.
SHOT_QUALITY_KEYS = ("icf", "iff", "iscf", "ihdcf")

SKATER_KEYS = tuple(SUMMARY_COLUMNS) + tuple(REALTIME_COLUMNS) + DERIVED_KEYS + SHOT_QUALITY_KEYS
GOALIE_KEYS = tuple(GOALIE_COLUMNS) + ("sv_25", "sv_30", "sv_35", "hd_sa", "hd_sv")
ALL_KEYS = tuple(dict.fromkeys(SKATER_KEYS + GOALIE_KEYS))

# Adding five players' longest anything is meaningless; these stay per-player.
NON_ADDITIVE = ("toi", "sv_pct", "pm")

# The stat that sorts a position group into line ranks. Ice time is the honest
# proxy for deployment: the NHL publishes no depth chart, but the coach's line
# one is whoever he plays the most.
RANK_STAT = "toi"

# How many line ranks the allowed-to-position breakdown keeps.
MAX_RANKS = {"C": 4, "L": 4, "R": 4, "D": 6, "G": 1}
# How many players per position each team panel shows.
ROSTER_CAP = {"C": 4, "L": 4, "R": 4, "D": 6, "G": 2}

# Averages and allowed-tables read each player's / team's last this-many games.
STATS_WINDOW = 25


def _zero(keys=ALL_KEYS) -> dict:
    return {k: 0.0 for k in keys}


# Threshold flags are "did he clear the number" -- 1 or 0 in a single game. As a
# season average they are a hit rate and have to be stored, but inside a game log
# every one of them is recomputable from the count beside it, and storing the
# dozen of them per game was over half the slate's size. The page derives them.
FLAG_FROM = {
    "sog_1": ("sog", 1), "sog_2": ("sog", 2), "sog_3": ("sog", 3), "sog_4": ("sog", 4),
    "pts_1": ("p", 1), "pts_2": ("p", 2), "g_1": ("g", 1), "a_1": ("a", 1),
    "blk_1": ("blk", 1), "blk_2": ("blk", 2), "hits_1": ("hits", 1), "hits_3": ("hits", 3),
    "sv_25": ("sv", 25), "sv_30": ("sv", 30), "sv_35": ("sv", 35),
}


def _log_stats(stats: dict) -> dict:
    """One game's stats, minus what the page can work out for itself."""
    return {k: round(v, 3) for k, v in stats.items() if v and k not in FLAG_FROM}


def _get(url: str, tries: int = 3):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))


def _fetch_report(report: str, season_id: int, game_type: int, team: str) -> list[dict]:
    """Every per-game row of one report for one club, paged to exhaustion."""
    exp = (f'seasonId={season_id} and gameTypeId={game_type} '
           f'and teamAbbrev="{team}"')
    # The sort has to be total, not just by date. Paging a feed ordered on
    # gameDate alone leaves every row of a given night in arbitrary order, so the
    # same row can land on two pages while another falls between them: the first
    # pull came back with 1,108 duplicates AND McDavid two games short of the 82
    # he played. gameId + playerId is unique, which makes the paging stable.
    sort = ('[{"property":"gameId","direction":"ASC"},'
            '{"property":"playerId","direction":"ASC"}]')
    rows, start = [], 0
    while start < MAX_OFFSET:
        url = (f"{REST}/{report}?isAggregate=false&isGame=true&start={start}&limit={PAGE}"
               f"&sort=" + urllib.parse.quote(sort)
               + "&cayenneExp=" + urllib.parse.quote(exp))
        page = (_get(url) or {}).get("data", [])
        rows.extend(page)
        if len(page) < PAGE:
            break
        start += PAGE
    return rows


def _cache_path(report: str, season_id: int, game_type: int) -> Path:
    return CACHE / f"{report.replace('/', '-')}-{season_id}-{game_type}.json.gz"


def load_report(report: str, season_id: int, game_type: int = 2,
                refresh: bool = False, teams=TEAMS) -> list[dict]:
    """All per-game rows of one report for a season, cached on disk.

    A cold pull is ~32 clubs x ~15 pages; threaded it takes well under a minute.
    Every later build reads the cache instead.
    """
    path = _cache_path(report, season_id, game_type)
    if path.exists() and not refresh:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for chunk in pool.map(lambda t: _fetch_report(report, season_id, game_type, t), teams):
            rows.extend(chunk)
    if rows:
        CACHE.mkdir(parents=True, exist_ok=True)
        with gzip.open(path, "wt", encoding="utf-8") as fh:
            json.dump(rows, fh, separators=(",", ":"))
    return rows


# ── normalising the three reports into one row per player-game ──────────────

def _toi_str(seconds) -> str:
    s = int(seconds or 0)
    return f"{s // 60}:{s % 60:02d}"


def _key(row: dict) -> tuple:
    return (row.get("playerId"), row.get("gameId"))


def build_rows(season_id: int, game_type: int = 2, refresh: bool = False) -> list[dict]:
    """One row per skater per game, with the realtime report merged in."""
    summary = load_report("skater/summary", season_id, game_type, refresh)
    realtime = {_key(r): r for r in load_report("skater/realtime", season_id, game_type, refresh)}

    rows = []
    merged = 0
    seen = set()
    for src in summary:
        if _key(src) in seen:   # a stable sort should prevent this; cheap to be sure
            continue
        seen.add(_key(src))
        rt = realtime.get(_key(src), {})
        if rt:
            merged += 1
        stats = _zero(SKATER_KEYS)
        for out_key, col in SUMMARY_COLUMNS.items():
            stats[out_key] = float(src.get(col) or 0)
        for out_key, col in REALTIME_COLUMNS.items():
            stats[out_key] = float(rt.get(col) or 0)
        # Threshold flags: "did he clear the number" is how a prop is graded, so
        # the average of these columns reads straight off as a hit rate.
        sog, pts = stats["sog"], stats["p"]
        stats.update({
            "sog_1": float(sog >= 1), "sog_2": float(sog >= 2),
            "sog_3": float(sog >= 3), "sog_4": float(sog >= 4),
            "pts_1": float(pts >= 1), "pts_2": float(pts >= 2),
            "g_1": float(stats["g"] >= 1), "a_1": float(stats["a"] >= 1),
            "blk_1": float(stats["blk"] >= 1), "blk_2": float(stats["blk"] >= 2),
            "hits_1": float(stats["hits"] >= 1), "hits_3": float(stats["hits"] >= 3),
        })
        rows.append({
            "player_id": src.get("playerId"),
            "name": src.get("skaterFullName", ""),
            "pos": src.get("positionCode", ""),
            "team": src.get("teamAbbrev", ""),
            "opp": src.get("opponentTeamAbbrev", ""),
            "game_id": src.get("gameId"),
            "date": src.get("gameDate", ""),
            "ha": "vs" if src.get("homeRoad") == "H" else "@",
            "season": season_id,
            "stats": stats,
        })
    print(f"[nhl-research] realtime merged into {merged} of {len(rows)} skater-games")
    return rows


def build_goalie_rows(season_id: int, game_type: int = 2, refresh: bool = False) -> list[dict]:
    """One row per goalie per game."""
    rows = []
    seen = set()
    for src in load_report("goalie/summary", season_id, game_type, refresh):
        if _key(src) in seen:
            continue
        seen.add(_key(src))
        stats = _zero(GOALIE_KEYS)
        for out_key, col in GOALIE_COLUMNS.items():
            stats[out_key] = float(src.get(col) or 0)
        sv = stats["sv"]
        stats.update({"sv_25": float(sv >= 25), "sv_30": float(sv >= 30), "sv_35": float(sv >= 35)})
        rows.append({
            "player_id": src.get("playerId"),
            "name": src.get("goalieFullName", ""),
            "pos": "G",
            "team": src.get("teamAbbrev", ""),
            "opp": src.get("opponentTeamAbbrev", ""),
            "game_id": src.get("gameId"),
            "date": src.get("gameDate", ""),
            "ha": "vs" if src.get("homeRoad") == "H" else "@",
            "season": season_id,
            "stats": stats,
        })
    return rows


def headshot(player_id, team: str, season_id: int) -> str:
    return f"https://assets.nhle.com/mugs/nhl/{season_id}/{team}/{player_id}.png"


# ── aggregates ──────────────────────────────────────────────────────────────

def _avg(totals: dict, games: int, keys) -> dict:
    if not games:
        return {k: 0.0 for k in keys}
    return {k: round(totals.get(k, 0.0) / games, 4) for k in keys}


def build_aggregates(rows: list[dict], current_teams: dict | None = None,
                     cap: dict | None = ROSTER_CAP, season_id: int = 20252026,
                     keys=None) -> tuple[dict, dict]:
    """Return (players_by_team, allowed_vs_pos_by_team).

    players_by_team: { "EDM": { "C": [ {name, pos, gp, rank, headshot, stats{}, log[]} ] } }
    allowed_by_team: { "EDM": { "C": { "overall": {...}, "ranks": {"1": {...}} } } }

    `current_teams` moves a player onto the club he plays for NOW. Without it
    every summer trade stays invisible and last season's uniform is the one the
    board shows -- the same trap the NFL tab hit with A.J. Brown.
    """
    keys = keys or SKATER_KEYS
    current_teams = current_teams or {}

    # ── per player: rolling window of totals + a log of every game ──
    by_player: dict = defaultdict(list)
    for row in rows:
        by_player[row["player_id"]].append(row)

    player_totals: dict = {}
    for pid, games in by_player.items():
        games.sort(key=lambda r: (r["season"], r["date"]))
        latest = games[-1]
        window = games[-STATS_WINDOW:]
        totals = _zero(keys)
        for g in window:
            for k in keys:
                totals[k] += g["stats"].get(k, 0.0)
        team = current_teams.get(pid, latest["team"])
        player_totals[pid] = {
            "name": latest["name"],
            "pos": latest["pos"],
            "team": team,
            "player_id": pid,
            "headshot": headshot(pid, team, season_id),
            "gp": len(window),
            "seasons": sorted({g["season"] for g in window}),
            "stats": _avg(totals, len(window), keys),
            "log": [
                {
                    "season": g["season"], "date": g["date"], "opp": g["opp"],
                    "ha": g["ha"], "toi": _toi_str(g["stats"].get("toi")),
                    "stats": _log_stats(g["stats"]),
                }
                for g in games
            ],
        }

    # ── each team's games, and the last STATS_WINDOW its allowed tables use ──
    opp_games: dict = defaultdict(set)
    for row in rows:
        if row["opp"]:
            opp_games[row["opp"]].add((row["season"], row["date"]))
    opp_window = {t: set(sorted(g)[-STATS_WINDOW:]) for t, g in opp_games.items()}
    allowed_games = {t: len(w) for t, w in opp_window.items()}

    # ── allowed: overall per position ──
    allowed_totals: dict = defaultdict(lambda: _zero(keys))
    for row in rows:
        opp = row["opp"]
        if not opp or (row["season"], row["date"]) not in opp_window.get(opp, ()):
            continue
        totals = allowed_totals[(opp, row["pos"])]
        for k in keys:
            totals[k] += row["stats"].get(k, 0.0)

    # ── allowed: by line rank, ranked within each game by ice time ──
    game_groups: dict = defaultdict(list)
    for row in rows:
        if row["opp"]:
            game_groups[(row["opp"], row["season"], row["date"], row["pos"])].append(row)

    rank_totals: dict = defaultdict(lambda: _zero(keys))
    rank_games: dict = defaultdict(int)
    rank_logs: dict = defaultdict(list)
    for (opp, season, date, pos), group in game_groups.items():
        group.sort(key=lambda r: r["stats"].get(RANK_STAT, 0), reverse=True)
        in_window = (season, date) in opp_window.get(opp, ())
        for idx, row in enumerate(group[: MAX_RANKS.get(pos, 4)], start=1):
            if in_window:
                totals = rank_totals[(opp, pos, idx)]
                for k in keys:
                    totals[k] += row["stats"].get(k, 0.0)
                rank_games[(opp, pos, idx)] += 1
            rank_logs[(opp, pos, idx)].append({
                "season": season, "date": date, "opp": row["team"],
                "who": row["name"], "toi": _toi_str(row["stats"].get("toi")),
                "stats": _log_stats(row["stats"]),
            })

    # ── assemble ──
    players_by_team: dict = defaultdict(lambda: defaultdict(list))
    for entry in player_totals.values():
        if entry["pos"] in POSITIONS:
            players_by_team[entry["team"]][entry["pos"]].append(entry)

    for team, buckets in players_by_team.items():
        for pos, bucket in buckets.items():
            bucket.sort(key=lambda p: p["stats"].get(RANK_STAT, 0), reverse=True)
            if cap:
                del bucket[cap.get(pos, 4):]
            for idx, player in enumerate(bucket, start=1):
                player["rank"] = idx

    allowed_by_team: dict = defaultdict(dict)
    for (team, pos), totals in allowed_totals.items():
        games = allowed_games.get(team, 0)
        allowed_by_team[team].setdefault(pos, {})["overall"] = {
            "gp": games, "stats": _avg(totals, games, keys),
        }
    for (team, pos, idx), totals in rank_totals.items():
        games = rank_games.get((team, pos, idx), 0)
        node = allowed_by_team[team].setdefault(pos, {}).setdefault("ranks", {})
        node[str(idx)] = {
            "gp": games,
            "stats": _avg(totals, games, keys),
            "log": sorted(rank_logs.get((team, pos, idx), []), key=lambda r: (r["season"], r["date"])),
        }

    return ({k: dict(v) for k, v in players_by_team.items()}, dict(allowed_by_team))


def league_averages(allowed_by_team: dict, keys=None) -> dict:
    """The league baseline every heat colour on the opponent side is measured off.

    It has to be built from the ALLOWED tables, not from raw player rows. A
    team's "allowed to centers" is the whole center group's output in a game --
    four men's worth -- so holding it up against one average center paints every
    club bright red. Averaging the same table across all 32 teams compares like
    with like.

    Shape mirrors the per-team tables so a lookup is the same either side:
        { "C": { "overall": {...}, "ranks": { "1": {...} } } }
    """
    keys = keys or SKATER_KEYS
    overall_totals: dict = defaultdict(lambda: _zero(keys))
    overall_counts: dict = defaultdict(int)
    rank_totals: dict = defaultdict(lambda: _zero(keys))
    rank_counts: dict = defaultdict(int)

    for table in allowed_by_team.values():
        for pos, node in table.items():
            if node.get("overall"):
                overall_counts[pos] += 1
                for k in keys:
                    overall_totals[pos][k] += node["overall"]["stats"].get(k, 0.0)
            for idx, rank_node in (node.get("ranks") or {}).items():
                if not rank_node.get("gp"):
                    continue
                rank_counts[(pos, idx)] += 1
                for k in keys:
                    rank_totals[(pos, idx)][k] += rank_node["stats"].get(k, 0.0)

    league: dict = {}
    for pos, count in overall_counts.items():
        league[pos] = {"overall": _avg(overall_totals[pos], count, keys), "ranks": {}}
    for (pos, idx), count in rank_counts.items():
        league.setdefault(pos, {"overall": {}, "ranks": {}})["ranks"][idx] =             _avg(rank_totals[(pos, idx)], count, keys)
    return league


def current_team_lookup(season_id: int) -> dict:
    """player id -> the club he plays for NOW, from this season's rosters.

    Stats come from whatever season is finished; the uniform comes from this
    one. Without the second half every summer move is invisible.
    """
    from concurrent.futures import ThreadPoolExecutor

    def one(team: str) -> list[tuple]:
        try:
            payload = _get(f"https://api-web.nhle.com/v1/roster/{team}/{season_id}")
        except Exception:
            return []
        out = []
        for group in ("forwards", "defensemen", "goalies"):
            for player in payload.get(group) or []:
                if player.get("id"):
                    out.append((player["id"], team))
        return out

    lookup: dict = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for pairs in pool.map(one, TEAMS):
            lookup.update(dict(pairs))
    return lookup


def percentile_breaks(values, buckets: int = 101) -> list:
    """Compress a distribution to `buckets` evenly spaced breakpoints.

    The rating model scores each input by where it sits in the LEAGUE, not
    where it sits among the dozen teams playing tonight. Shipping the whole
    distribution would add megabytes to every slate, and 101 breakpoints read a
    percentile to within one point -- far finer than the model needs.
    """
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return []
    last = len(vals) - 1
    return [round(vals[round(i * last / (buckets - 1))], 4) for i in range(buckets)]


def rating_scales(players_by_team: dict, allowed_by_team: dict,
                  forward_pos=("C", "L", "R")) -> dict:
    """Every league distribution the anytime-goal rating scores against."""
    skaters = [p for team in players_by_team.values()
               for pos in forward_pos for p in (team.get(pos) or [])]
    goalies = [p for team in players_by_team.values() for p in (team.get("G") or [])]

    def col(rows, key, scale=1.0):
        return percentile_breaks([float((r.get("stats") or {}).get(key) or 0) * scale
                                  for r in rows])

    # what clubs give up to a forward line slot, across every club and slot
    slots = []
    for table in allowed_by_team.values():
        for pos in forward_pos:
            for node in ((table.get(pos) or {}).get("ranks") or {}).values():
                if node.get("gp"):
                    slots.append(node["stats"])
    def slot_col(key):
        return percentile_breaks([float(s.get(key) or 0) for s in slots])

    def goalie_rate(num, den):
        out = []
        for g in goalies:
            st = g.get("stats") or {}
            d = float(st.get(den) or 0)
            if d:
                out.append(float(st.get(num) or 0) / d)
        return percentile_breaks(out)

    return {
        "sog": col(skaters, "sog"), "icf": col(skaters, "icf"),
        "iff": col(skaters, "iff"), "iscf": col(skaters, "iscf"),
        "ihdcf": col(skaters, "ihdcf"), "g": col(skaters, "g"),
        "pp_p": col(skaters, "pp_p"),
        "toi": col(skaters, "toi", 1 / 60),
        "opp_g": slot_col("g"), "opp_sog": slot_col("sog"), "opp_iscf": slot_col("iscf"),
        "gsv": goalie_rate("sv", "sa"), "ghd": goalie_rate("hd_sv", "hd_sa"),
        "gga": col(goalies, "ga"),
    }
