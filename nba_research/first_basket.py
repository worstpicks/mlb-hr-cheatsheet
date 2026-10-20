"""How a club's games open: the tip, the first shot and the first basket, from ESPN play-by-play.

For each club on the slate, every game in the research file's window (last
season's closing games and this preseason) is read from its play-by-play:

  jump      who jumped for each side, and which side came away with it
  first FG  the first made field goal of the game -- the First Basket bet;
            free throws never settle it -- and each side's own first basket
  first FGA each side's first shot attempt, made or not

Summaries come through build_slate.fetch and cache with the box scores.
"""
from __future__ import annotations

import re
from collections import Counter

from nba_research import build_slate

FINAL_TTL = 365 * 24 * 3600


def _ids(play: dict) -> list[str]:
    return [str((x.get("athlete") or {}).get("id")) for x in play.get("participants") or [] if x.get("athlete")]


def opening(event: str) -> dict | None:
    """The jump, the first basket and each side's first shot of one game."""
    summary = build_slate.fetch(f"summary?event={event}", ttl=FINAL_TTL)
    plays = sorted(summary.get("plays") or [], key=lambda p: int(p.get("sequenceNumber") or 0))
    teams = {}
    for c in ((summary.get("header") or {}).get("competitions") or [{}])[0].get("competitors") or []:
        teams[str((c.get("team") or {}).get("id"))] = (c.get("team") or {}).get("abbreviation", "")
    if not plays or len(teams) != 2:
        return None
    out: dict = {"event": event, "jumpers": [], "tip_team": None, "first_fg": None, "first_fg_team": None,
                 "first_fga": {}, "first_team_fg": {}}
    for p in plays:
        text = (p.get("type") or {}).get("text", "")
        team = teams.get(str((p.get("team") or {}).get("id")))
        if text == "Jumpball" and not out["jumpers"]:
            ids = _ids(p)
            out["jumpers"] = ids[:2]
            out["tip_team"] = team
            m = re.search(r"\((.+?) gains possession\)", p.get("text") or "")
            out["tip_text"] = p.get("text") or ""
            out["gainer"] = ids[2] if len(ids) > 2 else (m.group(1) if m else None)
            continue
        if p.get("shootingPlay") and "Free Throw" not in text:
            ids = _ids(p)
            if team and team not in out["first_fga"] and ids:
                out["first_fga"][team] = ids[0]
            if p.get("scoringPlay") and ids:
                if out["first_fg"] is None:
                    out["first_fg"], out["first_fg_team"] = ids[0], team
                if team and team not in out["first_team_fg"]:
                    out["first_team_fg"][team] = ids[0]
        if len(out["first_team_fg"]) == 2 and len(out["first_fga"]) == 2:
            break
    return out


def player_openings(player: dict, limit: int = 15) -> dict:
    """One player's own record at the start of games, whichever club he played for:
    starts, jumps and tips won, his team's first basket and first shot."""
    logs = sorted((l for l in player.get("logs") or [] if l.get("event")), key=lambda l: l["date"], reverse=True)[:limit]
    games = build_slate.parallel([l["event"] for l in logs], opening)
    rec = {"games": 0, "starts": 0, "jumps": 0, "jump_won": 0, "team_first": 0, "his_team_first_fg": 0,
           "game_first_fg": 0, "team_first_fga": 0, "start_games": 0, "clubs": []}
    pid = player["id"]
    for log, g in zip(logs, games):
        if not g:
            continue
        team = log.get("team")
        rec["games"] += 1
        if team not in rec["clubs"]:
            rec["clubs"].append(team)
        if not log.get("starter"):
            continue
        rec["starts"] += 1
        if pid in g["jumpers"]:
            rec["jumps"] += 1
            rec["jump_won"] += g["tip_team"] == team
        rec["team_first"] += g["first_fg_team"] == team
        rec["his_team_first_fg"] += g["first_team_fg"].get(team) == pid
        rec["game_first_fg"] += g["first_fg"] == pid
        rec["team_first_fga"] += g["first_fga"].get(team) == pid
    return rec


def club_events(side: dict) -> list[tuple[str, str]]:
    """(date, event) for every game in the research window this club played."""
    ev = {}
    for p in side.get("players") or []:
        for log in p.get("logs") or []:
            if log.get("team") == side["abbr"]:
                ev[log["event"]] = log["date"]
    return sorted(((d, e) for e, d in ev.items()), reverse=True)


def club_openings(side: dict) -> dict:
    """Everything the first-basket card says about one club."""
    events = club_events(side)
    games = [g for g in build_slate.parallel([e for _, e in events], opening) if g]
    abbr = side["abbr"]
    jumps: Counter = Counter()
    won: Counter = Counter()
    first_fg: Counter = Counter()
    first_fga: Counter = Counter()
    team_first = tip_won = 0
    for g in games:
        ours = [j for j in g["jumpers"] if j in {p["id"] for p in side.get("players") or []}]
        for j in ours:
            jumps[j] += 1
            if g["tip_team"] == abbr:
                won[j] += 1
        tip_won += g["tip_team"] == abbr
        team_first += g["first_fg_team"] == abbr
        if g["first_fg_team"] == abbr:
            first_fg[g["first_fg"]] += 1
        if g["first_fga"].get(abbr):
            first_fga[g["first_fga"][abbr]] += 1
    return {"abbr": abbr, "games": len(games), "tip_won": tip_won, "team_first": team_first,
            "jumps": dict(jumps), "jump_won": dict(won), "first_fg": dict(first_fg), "first_fga": dict(first_fga),
            "events": [g["event"] for g in games]}
