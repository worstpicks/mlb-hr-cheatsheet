"""Anytime-touchdown projection, written onto every skill player in the slate.

The inputs come from ``cheatsheets.red_zone_projection`` -- red-zone share per
player, trips per game per offence, TD rate allowed per defence -- and this is
where they meet a specific week's matchups:

    xTD    = share x trips per game x opponent TD rate allowed
    chance = 1 - exp(-xTD)          (Poisson: odds of at least one)

The point of keeping this separate is that the aggregates are season-wide and
cost a play-by-play load, while the projection is a matchup join that costs
nothing. Rebuilding a slate re-runs only the second half.

One compromise worth naming: a player who changed teams earned his red-zone
share with the old offence, and it is applied here to the new one's trips. That
is the same trade every early-season board makes, and it is why ``moved`` is
reported -- those numbers describe a role he no longer occupies.
"""
from __future__ import annotations

import math

# Positions that can catch or run the ball into the end zone. Quarterbacks are
# left out: their rushing touchdowns are a different market and the red-zone
# share here counts carries and targets, not kneel-downs and sneaks.
SCORING_POSITIONS = ("RB", "WR", "TE")


def project_player(share, trips_per_game, opp_td_rate):
    """Expected red-zone TDs a game, and the odds of at least one.

    Returns ``(xtd, chance)`` rounded for display, or ``(None, None)`` when any
    input is missing -- a blank cell is honest, a zero is not.
    """
    if share is None or trips_per_game is None or opp_td_rate is None:
        return None, None
    xtd = share * trips_per_game * (opp_td_rate / 100.0)
    return round(xtd, 3), round((1.0 - math.exp(-xtd)) * 100)


def attach_td_chance(slate_games: list[dict], proj: dict) -> dict:
    """Write ``rz_proj`` onto each RB/WR/TE in every game. Mutates in place.

    Returns a small report: how many players got a projection, how many were
    skipped for want of an input, and how many are being projected on a share
    they earned somewhere else.
    """
    players = proj.get("players") or {}
    teams = proj.get("teams") or {}
    defense = proj.get("defense") or {}
    if not players or not teams or not defense:
        return {"projected": 0, "skipped": 0, "moved": 0, "reason": "no red-zone aggregates"}

    projected = skipped = moved = 0

    for game in slate_games:
        for side, team, opp in (
            ("away_offense", game.get("away"), game.get("home")),
            ("home_offense", game.get("home"), game.get("away")),
        ):
            offense = game.get(side) or {}
            team_row = teams.get(team) or {}
            def_row = defense.get(opp) or {}
            for pos in SCORING_POSITIONS:
                for player in offense.get(pos) or []:
                    row = players.get(player.get("player_id") or "")
                    if not row:
                        skipped += 1
                        continue
                    # Share is a rate, not a season slice: his red-zone work per
                    # game he played over the offence's work per game. A back who
                    # missed half the year still reads as the man when he is out
                    # there, which is what a projection for Sunday needs.
                    gp = player.get("gp") or 0
                    per_game = team_row.get("weighted_per_game")
                    share = (
                        round((row["weighted"] / gp) / per_game, 4)
                        if gp and per_game else None
                    )
                    xtd, chance = project_player(
                        share,
                        team_row.get("trips_per_game"),
                        def_row.get("td_rate_allowed"),
                    )
                    if chance is None:
                        skipped += 1
                        continue
                    earned_with = row.get("team")
                    if earned_with and earned_with != team:
                        moved += 1
                    player["rz_proj"] = {
                        "chance": chance,
                        "xtd": xtd,
                        "share": share,
                        "rz_car_pg": round(row["rz_car"] / gp, 1) if gp else None,
                        "rz_tgt_pg": round(row["rz_tgt"] / gp, 1) if gp else None,
                        "trips_per_game": team_row.get("trips_per_game"),
                        "opp_td_rate": def_row.get("td_rate_allowed"),
                        "opp_rank": def_row.get("rank"),
                        "opp_of": def_row.get("of"),
                        # True when the share was earned with a different team, so
                        # the board can mark it rather than quietly trusting it.
                        "stale_team": bool(earned_with and earned_with != team),
                    }
                    projected += 1

    return {"projected": projected, "skipped": skipped, "moved": moved}


def top_plays(slate_games: list[dict], limit: int = 5, starters: set[str] | None = None) -> list[dict]:
    """The slate's best anytime-TD spots, ranked on red-zone chance.

    Red-zone chance already prices the opponent in, so it needs no second
    matchup term. Ties break toward the softer defence. Pass ``starters`` -- a
    set of player names confirmed to be starting -- to keep backups off the
    list; without it every rostered player is eligible and the caller has to do
    its own availability check.
    """
    rows = []
    for game in slate_games:
        for side, team, opp in (
            ("away_offense", game.get("away"), game.get("home")),
            ("home_offense", game.get("home"), game.get("away")),
        ):
            for pos in SCORING_POSITIONS:
                for player in (game.get(side) or {}).get(pos) or []:
                    p = player.get("rz_proj")
                    if not p or p.get("chance") is None:
                        continue
                    if starters is not None and player.get("name") not in starters:
                        continue
                    rows.append(
                        {
                            "name": player["name"],
                            "pos": pos,
                            "rank": player.get("rank"),
                            "team": team,
                            "opp": opp,
                            "kickoff": game.get("kickoff"),
                            "chance": p["chance"],
                            "opp_rank": p.get("opp_rank"),
                            "stale_team": p.get("stale_team", False),
                        }
                    )
    rows.sort(key=lambda r: (-r["chance"], -(r["opp_rank"] or 0)))
    return rows[:limit]
