"""Per-player shot quality (iCF / iFF / iSCF / iHDCF) from NHL play-by-play.

The Worst Pickz rating model leans on iFF and iSCF -- dangerous touches rather
than empty volume -- and those are not on the summary feeds. They come from the
play-by-play, which carries an (x, y) for every shot attempt:

    https://api-web.nhle.com/v1/gamecenter/<gameId>/play-by-play

Definitions, in the usual terms:
    iCF   every shot attempt he took        (on goal + missed + blocked)
    iFF   the unblocked ones                (on goal + missed)
    iSCF  unblocked attempts from the danger area in front of the net
    iHDCF the subset from the inner slot

Natural Stat Trick draws its scoring-chance area as a "home plate" polygon and
does not publish it as a formula, so the area below is the usual distance-and-
angle reading of it. It is an approximation of NST's shape, not a copy of it,
and it is applied identically to every skater and every defense -- so the
comparison between them holds even where the absolute count drifts from NST's.

One crawl of a season is ~1,300 requests, about four minutes threaded, and it is
cached on disk afterwards.
"""
from __future__ import annotations

import gzip
import json
import math
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from nhl_research.nhl_stats import CACHE, _get

WEB = "https://api-web.nhle.com/v1"

# Shot events that count as an attempt, and which bucket each falls in.
ON_GOAL = {"shot-on-goal", "goal"}
UNBLOCKED = ON_GOAL | {"missed-shot"}
ATTEMPTS = UNBLOCKED | {"blocked-shot"}

# Rink geometry: the net sits 11 feet in from the boards, at x = +/-89.
GOAL_X = 89.0
# Inner slot -- the front of the net, where most goals come from.
HIGH_DANGER_FT = 18.0
# The wider danger area: out to about the top of the circles, kept inside the
# faceoff dots so point shots and bad-angle wristers do not count as chances.
CHANCE_FT = 32.0
CHANCE_HALF_WIDTH = 22.0


def _danger(x, y) -> tuple[bool, bool]:
    """(is_scoring_chance, is_high_danger) for one shot's coordinates."""
    if x is None or y is None:
        return False, False
    # Teams switch ends, so the shot is folded onto one half of the rink.
    dx = GOAL_X - abs(float(x))
    dy = abs(float(y))
    if dx < -3:                      # behind the goal line by more than the net
        return False, False
    dist = math.hypot(max(dx, 0.0), dy)
    high = dist <= HIGH_DANGER_FT
    chance = high or (dist <= CHANCE_FT and dy <= CHANCE_HALF_WIDTH)
    return chance, high


def _cache_path(season_id: int, game_type: int) -> Path:
    return CACHE / f"shot-quality-{season_id}-{game_type}.json.gz"


def _game_shots(game_id: int) -> list[dict]:
    """Every shot attempt in one game, flattened."""
    try:
        payload = _get(f"{WEB}/gamecenter/{game_id}/play-by-play")
    except Exception:
        return []
    out = []
    for play in payload.get("plays") or []:
        kind = play.get("typeDescKey")
        if kind not in ATTEMPTS:
            continue
        d = play.get("details") or {}
        # On a blocked shot the NHL feed names the BLOCKER as the event owner in
        # some seasons and the shooter in others; "shootingPlayerId" is the one
        # field that always means the man who took it.
        shooter = d.get("shootingPlayerId") or d.get("scoringPlayerId")
        if not shooter:
            continue
        chance, high = _danger(d.get("xCoord"), d.get("yCoord"))
        out.append({
            "game_id": game_id,
            "player_id": shooter,
            "goalie_id": d.get("goalieInNetId"),
            "on_goal": kind in ON_GOAL,
            "unblocked": kind in UNBLOCKED,
            "goal": kind == "goal",
            "chance": chance,
            "high": high,
        })
    return out


def load_shots(season_id: int, game_ids: list[int], game_type: int = 2,
               refresh: bool = False) -> dict:
    """{(player_id, game_id): {icf, iff, iscf, ihdcf, goals}} for the season.

    Also returns goalie rows under ("G", goalie_id, game_id) so the goalie
    component of the rating can read a real high-danger save rate.
    """
    path = _cache_path(season_id, game_type)
    if path.exists() and not refresh:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            raw = json.load(fh)
        return {tuple(k.split("|")): v for k, v in raw.items()}

    shots: list[dict] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for chunk in pool.map(_game_shots, game_ids):
            shots.extend(chunk)

    agg: dict = defaultdict(lambda: {"icf": 0, "iff": 0, "iscf": 0, "ihdcf": 0, "goals": 0})
    goalies: dict = defaultdict(lambda: {"sa": 0, "hd_sa": 0, "hd_ga": 0, "ga": 0})
    for s in shots:
        row = agg[(str(s["player_id"]), str(s["game_id"]))]
        row["icf"] += 1
        if s["unblocked"]:
            row["iff"] += 1
            if s["chance"]:
                row["iscf"] += 1
            if s["high"]:
                row["ihdcf"] += 1
        if s["goal"]:
            row["goals"] += 1
        gid = s.get("goalie_id")
        if gid and s["on_goal"]:
            g = goalies[(str(gid), str(s["game_id"]))]
            g["sa"] += 1
            if s["high"]:
                g["hd_sa"] += 1
            if s["goal"]:
                g["ga"] += 1
                if s["high"]:
                    g["hd_ga"] += 1

    out = {f"{pid}|{gid}": row for (pid, gid), row in agg.items()}
    out.update({f"G{gid}|{game}": row for (gid, game), row in goalies.items()})
    CACHE.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        json.dump(out, fh, separators=(",", ":"))
    print(f"[nhl-research] shot quality: {len(shots)} attempts over {len(game_ids)} games")
    return {tuple(k.split("|")): v for k, v in out.items()}


def merge_into_rows(rows: list[dict], shots: dict) -> int:
    """Fold iCF/iFF/iSCF/iHDCF onto each skater-game row's stats."""
    touched = 0
    for row in rows:
        key = (str(row["player_id"]), str(row["game_id"]))
        extra = shots.get(key)
        if not extra:
            continue
        touched += 1
        stats = row["stats"]
        stats["icf"] = float(extra["icf"])
        stats["iff"] = float(extra["iff"])
        stats["iscf"] = float(extra["iscf"])
        stats["ihdcf"] = float(extra["ihdcf"])
    return touched


def merge_into_goalies(rows: list[dict], shots: dict) -> int:
    """Fold high-danger shots against / goals against onto each goalie-game."""
    touched = 0
    for row in rows:
        key = (f"G{row['player_id']}", str(row["game_id"]))
        extra = shots.get(key)
        if not extra:
            continue
        touched += 1
        stats = row["stats"]
        stats["hd_sa"] = float(extra["hd_sa"])
        stats["hd_sv"] = float(extra["hd_sa"] - extra["hd_ga"])
    return touched
