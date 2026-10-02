"""Preseason player stats, built from boxscores.

The NHL's aggregate stats API publishes nothing for the preseason -- twenty-two
games had been played and `skater/summary` with gameTypeId=1 still answered
zero rows. The per-game boxscores carry all of it though, so this walks the
preseason schedule and reads them directly. Same gap, same fix, as the football
tab's espn_preseason.py.

It is an opt-in source, never the default. Preseason ice time belongs largely
to camp bodies who will not see a regular-season shift, so the page shows
preseason numbers for the players who are ALREADY on the club's lineup and
leaves the prospects off -- otherwise the toggle just swaps a real board for a
list of names nobody can bet.
"""
from __future__ import annotations

import gzip
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from nhl_research.nhl_api import get_json
from nhl_research.nhl_stats import (
    CACHE,
    GOALIE_KEYS,
    SKATER_KEYS,
    _get,
    _zero,
)

WEB = "https://api-web.nhle.com/v1"

# The season preseason rows belong to. Set by fetch_preseason so the merged
# log sorts them after last season rather than into a bucket of their own.
_SEASON_ID = 20262027


def _toi_seconds(toi) -> float:
    """"18:51" -> 1131."""
    try:
        mins, secs = str(toi or "0:00").split(":")
        return int(mins) * 60 + int(secs)
    except (ValueError, AttributeError):
        return 0.0


def preseason_game_ids(start_date: str, through_date: str) -> list[tuple]:
    """[(game_id, date)] for every finished preseason game in the window."""
    out, cursor, seen = [], start_date, set()
    while cursor and cursor <= through_date:
        try:
            payload = get_json(f"{WEB}/schedule/{cursor}")
        except Exception:
            break
        for day in payload.get("gameWeek") or []:
            date = day.get("date", "")
            if date > through_date:
                continue
            for game in day.get("games") or []:
                # gameType 1 is preseason; only completed games have stats
                if game.get("gameType") != 1:
                    continue
                if game.get("gameState") not in ("FINAL", "OFF"):
                    continue
                gid = game.get("id")
                if gid and gid not in seen:
                    seen.add(gid)
                    out.append((gid, date))
        nxt = payload.get("nextStartDate")
        if not nxt or nxt <= cursor:
            break
        cursor = nxt
    return sorted(out, key=lambda x: x[1])


def _game_rows(entry: tuple) -> list[dict]:
    """Every skater and goalie line from one preseason boxscore."""
    game_id, date = entry
    try:
        box = _get(f"{WEB}/gamecenter/{game_id}/boxscore")
    except Exception:
        return []
    stats_by_side = box.get("playerByGameStats") or {}
    sides = {
        "awayTeam": ((box.get("awayTeam") or {}).get("abbrev"),
                     (box.get("homeTeam") or {}).get("abbrev"), "@"),
        "homeTeam": ((box.get("homeTeam") or {}).get("abbrev"),
                     (box.get("awayTeam") or {}).get("abbrev"), "vs"),
    }

    rows = []
    for side_key, (team, opp, ha) in sides.items():
        if not team or not opp:
            continue
        block = stats_by_side.get(side_key) or {}
        for group in ("forwards", "defense"):
            for p in block.get(group) or []:
                stats = _zero(SKATER_KEYS)
                stats.update({
                    "g": float(p.get("goals") or 0),
                    "a": float(p.get("assists") or 0),
                    "p": float(p.get("points") or 0),
                    "sog": float(p.get("sog") or 0),
                    "pim": float(p.get("pim") or 0),
                    "pm": float(p.get("plusMinus") or 0),
                    "pp_g": float(p.get("powerPlayGoals") or 0),
                    "hits": float(p.get("hits") or 0),
                    "blk": float(p.get("blockedShots") or 0),
                    "tk": float(p.get("takeaways") or 0),
                    "gv": float(p.get("giveaways") or 0),
                    "toi": _toi_seconds(p.get("toi")),
                })
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
                    "player_id": p.get("playerId"),
                    "name": (p.get("name") or {}).get("default", ""),
                    "pos": p.get("position", ""),
                    "team": team, "opp": opp, "ha": ha,
                    "game_id": game_id, "date": date, "season": _SEASON_ID, "pre": True,
                    "stats": stats,
                })
        for p in block.get("goalies") or []:
            stats = _zero(GOALIE_KEYS)
            shots = float(p.get("shotsAgainst") or 0)
            goals = float(p.get("goalsAgainst") or 0)
            # A few preseason box scores leave "saves" out; it is shots less goals.
            saves = (float(p["saves"]) if p.get("saves") is not None
                     else max(shots - goals, 0.0))
            stats.update({
                "sv": saves,
                "sa": shots,
                "ga": goals,
                "toi": _toi_seconds(p.get("toi")),
                "start": 1.0,
                "win": 1.0 if p.get("decision") == "W" else 0.0,
                "sv_25": float(saves >= 25), "sv_30": float(saves >= 30),
                "sv_35": float(saves >= 35),
            })
            if stats["sa"]:
                stats["sv_pct"] = stats["sv"] / stats["sa"]
                stats["so"] = 1.0 if stats["ga"] == 0 else 0.0
            rows.append({
                "player_id": p.get("playerId"),
                "name": (p.get("name") or {}).get("default", ""),
                "pos": "G",
                "team": team, "opp": opp, "ha": ha,
                "game_id": game_id, "date": date, "season": _SEASON_ID, "pre": True,
                "stats": stats,
            })
    return rows


def _fill_saves(goalies: list) -> list:
    """Backfill saves the box score left out, in rows cached before the fix.

    11 of 169 goalie games this preseason came back with shots and goals but no
    saves, and were read as zero saves: Kochetkov's 23 saves on 28 shots counted
    as 0, which put him at .792 instead of .884 and handed every shooter facing
    him a goalie edge that was not there. Zero saves with fewer goals than shots
    cannot happen, so those rows are repaired as shots less goals.
    """
    for row in goalies:
        st = row["stats"]
        if st.get("sa") and not st.get("sv") and st.get("ga", 0) < st["sa"]:
            st["sv"] = st["sa"] - st.get("ga", 0)
            st["sv_pct"] = st["sv"] / st["sa"]
            for n in (25, 30, 35):
                st[f"sv_{n}"] = float(st["sv"] >= n)
    return goalies


def fetch_preseason(start_date: str, through_date: str, season_id: int = 20262027,
                    regular_start: str | None = None) -> tuple[list, list]:
    """(skater_rows, goalie_rows) for every finished preseason game.

    Once the regular season has begun the preseason is a closed set, so it is
    read once and cached. Left open-ended, every build walked the schedule a
    week at a time from the first preseason game to today -- a walk that gets
    one request longer every week of the season.
    """
    global _SEASON_ID
    _SEASON_ID = season_id
    over = bool(regular_start and through_date >= regular_start)
    path = CACHE / f"preseason-{season_id}.json.gz"
    if over and path.exists():
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            saved = json.load(fh)
        return saved["skaters"], _fill_saves(saved["goalies"])
    if regular_start:
        through_date = min(through_date, regular_start)

    games = preseason_game_ids(start_date, through_date)
    if not games:
        return [], []
    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for chunk in pool.map(_game_rows, games):
            rows.extend(chunk)
    skaters = [r for r in rows if r["pos"] != "G"]
    goalies = [r for r in rows if r["pos"] == "G"]
    print(f"[nhl-research] preseason: {len(games)} games, "
          f"{len(skaters)} skater lines, {len(goalies)} goalie lines")
    if over and skaters:
        CACHE.mkdir(parents=True, exist_ok=True)
        with gzip.open(path, "wt", encoding="utf-8") as fh:
            json.dump({"skaters": skaters, "goalies": goalies}, fh, separators=(",", ":"))
    return skaters, goalies


def lineup_only(pre: dict, lineup: dict) -> dict:
    """Preseason cards for the players already on the club's lineup, in order.

    Without this the toggle brings back a board full of camp invitees who will
    not play a regular-season shift -- the same trap the football tab hit, and
    the reason its preseason source is filtered the same way.
    """
    out = {}
    for pos, bucket in (lineup or {}).items():
        by_id = {p.get("player_id"): p for p in (pre.get(pos) or [])}
        keep = []
        for player in bucket:
            match = by_id.get(player.get("player_id"))
            if match:
                keep.append(dict(match, rank=player.get("rank"), name=player.get("name"),
                                 headshot=player.get("headshot", "")))
        out[pos] = keep
    return out
