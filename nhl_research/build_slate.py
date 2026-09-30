"""Assemble the NHL Research slate JSON: NHL schedule + per-game aggregates.

A hockey slate is a DATE, not a week, so this writes one file per day:
    preview/data/nhl-research-2026-09-29.json
and keeps preview/data/nhl-research-manifest.json listing the days that exist,
which is what lets the page fall back to a posted slate instead of going blank.
"""
from __future__ import annotations

import json
from datetime import date as _date
from datetime import datetime, timedelta
from pathlib import Path

from nhl_research.nhl_api import fetch_day_games, fetch_records, season_bounds
from nhl_research.nhl_stats import (
    GOALIE_KEYS,
    POSITIONS,
    SKATER_KEYS,
    build_aggregates,
    build_goalie_rows,
    build_rows,
    current_roster,
    league_averages,
    rating_scales,
)
from nhl_research.odds_api import fetch_props, normalize_name
from nhl_research.preseason import fetch_preseason
from nhl_research.shot_quality import load_shots, merge_into_goalies, merge_into_rows

OUT_DIR = Path(__file__).resolve().parent.parent / "preview" / "data"
MANIFEST = OUT_DIR / "nhl-research-manifest.json"
# Slates older than this are dropped from the site. A finished night's research
# has little use, and at 5-15 MB a day they would otherwise pile up all season.
KEEP_DAYS = 7


def season_id_for(date: str) -> int:
    """The NHL season a date belongs to, as the API numbers it (20262027)."""
    year, month = int(date[:4]), int(date[5:7])
    start = year if month >= 7 else year - 1
    return int(f"{start}{start + 1}")


# The league-wide half of a build is identical for every date in a run, so
# building today and tomorrow back to back does the heavy part once.
_LEAGUE: dict = {}


def load_league(date: str) -> dict:
    """Every player's and every club's numbers, as of now.

    The logs reach across three stretches, oldest first: last season, this
    preseason, this season. That is the football tab's rule too -- "logs reach
    back into last season alongside this one".

    The first version of this picked ONE season: this one as soon as it had any
    games, otherwise the last. On the second day of a season that meant five
    games of data: twenty-two clubs with no players at all, and the other ten
    rated on a single night.
    """
    schedule_season = season_id_for(date)
    calendar = season_bounds(date)
    regular_start = calendar.get("regular_start")
    key = (schedule_season, min(date, regular_start) if regular_start else date)
    if key in _LEAGUE:
        return _LEAGUE[key]

    # ── last season: finished, so its cache is good for ever ──
    prev_season = schedule_season - 10001
    rows = build_rows(prev_season)
    goalie_rows = build_goalie_rows(prev_season)
    shots = load_shots(prev_season, sorted({r["game_id"] for r in rows}))
    merge_into_rows(rows, shots)
    merge_into_goalies(goalie_rows, shots)

    # ── this season: topped up on every build ──
    cur_rows = build_rows(schedule_season, live=True)
    cur_goalies = build_goalie_rows(schedule_season, live=True)
    cur_games = sorted({r["game_id"] for r in cur_rows})
    if cur_rows:
        cur_shots = load_shots(schedule_season, cur_games)
        merge_into_rows(cur_rows, cur_shots)
        merge_into_goalies(cur_goalies, cur_shots)
    stats_season = schedule_season if cur_rows else prev_season
    print(f"[nhl-research] {prev_season}: {len(rows)} skater-games · "
          f"{schedule_season}: {len(cur_rows)} skater-games over {len(cur_games)} games")

    # Production comes from the games; the uniform comes from this season's
    # roster. Without the second half every summer move is invisible.
    current_teams, roster_names = current_roster(schedule_season)
    if not current_teams:
        print(f"[nhl-research] WARN no {schedule_season} roster published; "
              f"players stay on the club they last played for")

    # ── preseason, folded into the same log and marked `pre` ──
    pre_skaters: list = []
    pre_goalies: list = []
    pre_count = 0
    try:
        pre_start = calendar.get("preseason_start")
        if pre_start and pre_start <= date:
            pre_skaters, pre_goalies = fetch_preseason(
                pre_start, date, schedule_season, regular_start)
            if pre_skaters:
                pre_ids = sorted({r["game_id"] for r in pre_skaters})
                pre_count = len(pre_ids)
                # shot quality for these games too, or iCF/iFF/iSCF would read
                # as a flat zero on every preseason row instead of "not played"
                pre_shots = load_shots(schedule_season, pre_ids, game_type=1)
                merge_into_rows(pre_skaters, pre_shots)
                merge_into_goalies(pre_goalies, pre_shots)
    except Exception as exc:
        print(f"[nhl-research] preseason merge failed ({exc}); regular season only")

    # build_aggregates orders each log by (season, date); preseason rows carry
    # this season's id and September dates, so they land between the two.
    rows = rows + pre_skaters + cur_rows
    goalie_rows = goalie_rows + pre_goalies + cur_goalies

    players, allowed = build_aggregates(
        rows, current_teams, season_id=schedule_season, names=roster_names)
    goalies, goalies_allowed = build_aggregates(
        goalie_rows, current_teams, season_id=schedule_season, keys=GOALIE_KEYS,
        names=roster_names,
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

    out = {
        "schedule_season": schedule_season,
        "stats_season": stats_season,
        "log_seasons": sorted({r["season"] for r in rows}),
        "season_games": len(cur_games),
        "preseason_games": pre_count,
        "calendar": calendar,
        "players": players,
        "allowed": allowed,
        "league": league,
        # The cheat sheet's rating model scores each input against the league,
        # not against the handful of clubs playing tonight.
        "scales": rating_scales(players, allowed),
        "records": fetch_records(schedule_season),
    }
    _LEAGUE[key] = out
    return out


def build_slate(date: str) -> dict:
    games = fetch_day_games(date)
    lg = load_league(date)
    players, allowed = lg["players"], lg["allowed"]
    props = fetch_props(games)

    empty = {pos: [] for pos in POSITIONS}
    slate_games = []
    for game in games:
        game_props = props.get(f"{game['away_name']} @ {game['home_name']}", {})
        slate_games.append({
            **game,
            "away_record": lg["records"].get(game["away"], ""),
            "home_record": lg["records"].get(game["home"], ""),
            "away_skaters": _with_lines(players.get(game["away"], empty), game_props),
            "home_skaters": _with_lines(players.get(game["home"], empty), game_props),
            "away_allowed": allowed.get(game["away"], {}),
            "home_allowed": allowed.get(game["home"], {}),
        })
    graded = sum(len(b) for g in slate_games
                 for side in ("away_skaters", "home_skaters")
                 for b in g[side].values())
    print(f"[nhl-research] {date}: {len(slate_games)} games, {graded} player cards")

    return {
        "date": date,
        "season": lg["schedule_season"],
        "stats_season": lg["stats_season"],
        # seasons the logs reach into, so the page can say "25-26 + 26-27"
        "log_seasons": lg["log_seasons"],
        "season_games": lg["season_games"],
        "has_props": bool(props),
        "preseason_games": lg["preseason_games"],
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "calendar": lg["calendar"],
        "league": lg["league"],
        "scales": lg["scales"],
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


def _unchanged(path: Path, payload: dict) -> bool:
    """True when the slate on disk already says exactly this, bar the timestamp.

    A scheduled build runs several times a day and mostly finds nothing new.
    Rewriting the file anyway would stamp a new time on it, and every one of
    those would be another multi-megabyte commit of the same numbers.
    """
    if not path.exists():
        return False
    try:
        old = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    new = json.loads(json.dumps(payload))
    old.pop("fetched_at", None)
    new.pop("fetched_at", None)
    return old == new


def write_slate(date: str) -> tuple[Path, bool]:
    """Build one day. Returns (path, whether the file actually changed)."""
    payload = build_slate(date)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"nhl-research-{date}.json"
    if _unchanged(out_path, payload):
        return out_path, False
    # compact separators: game logs make this file large enough to matter
    out_path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    return out_path, True


def slate_dates() -> list[str]:
    """Every day that has a slate on disk, oldest first."""
    return sorted(p.stem.replace("nhl-research-", "") for p in OUT_DIR.glob("nhl-research-20*.json"))


def prune(today: str, keep_days: int = KEEP_DAYS) -> list[str]:
    """Delete slates older than `keep_days` before `today`. Returns what went."""
    cutoff = (_date.fromisoformat(today) - timedelta(days=keep_days)).isoformat()
    gone = []
    for day in slate_dates():
        if day < cutoff:
            (OUT_DIR / f"nhl-research-{day}.json").unlink()
            gone.append(day)
    return gone


def write_manifest() -> list[str]:
    """List the posted days, for the page to steer by."""
    dates = slate_dates()
    body = json.dumps({"version": 1, "dates": dates}, indent=2) + "\n"
    if not MANIFEST.exists() or MANIFEST.read_text(encoding="utf-8") != body:
        MANIFEST.write_text(body, encoding="utf-8")
    return dates
