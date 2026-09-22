"""Player prop lines from The Odds API (free key at the-odds-api.com).

Set the ODDS_API_KEY environment variable to enable. Without a key (or in the
offseason before books post props) the slate simply builds without prop lines --
the same graceful degradation the NFL tab uses.

Free tier is 500 credits/month; one build costs (#games x #markets) credits.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

BASE = "https://api.the-odds-api.com/v4/sports/icehockey_nhl"

# The Odds API market key -> our stat key ("atgs" = anytime goal scorer, american odds)
MARKET_TO_STAT = {
    "player_goal_scorer_anytime": "atgs",
    "player_points": "p",
    "player_assists": "a",
    "player_shots_on_goal": "sog",
    "player_blocked_shots": "blk",
    "player_total_saves": "sv",
    "player_power_play_points": "pp_p",
}

MARKETS = ",".join(MARKET_TO_STAT)


def normalize_name(name: str) -> str:
    name = re.sub(r"[.'`-]", "", (name or "").lower())
    name = re.sub(r"\s+(jr|sr|ii|iii|iv|v)$", "", name.strip())
    return re.sub(r"\s+", " ", name)


def _get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "worstpickz-nhl-research"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_props(games: list[dict]) -> dict:
    """Return {"Away Name @ Home Name": {normalized player: {stat_key: line}}}.

    Empty dict when ODDS_API_KEY is unset or books have nothing posted yet.
    """
    api_key = os.environ.get("ODDS_API_KEY", "").strip()
    if not api_key:
        print("[nhl-research] ODDS_API_KEY unset; slate builds without prop lines")
        return {}

    try:
        events = _get_json(f"{BASE}/events?apiKey={api_key}")
    except Exception as exc:
        print(f"[nhl-research] odds event list failed ({exc}); no prop lines")
        return {}

    # Match the book's event to our slate by team names on the same day.
    wanted = {}
    for game in games:
        key = f"{game['away_name']} @ {game['home_name']}"
        wanted[(game["away_name"], game["home_name"])] = key

    out: dict = {}
    for event in events:
        pair = (event.get("away_team", ""), event.get("home_team", ""))
        label = wanted.get(pair)
        if not label:
            continue
        url = (f"{BASE}/events/{event['id']}/odds?apiKey={api_key}"
               f"&regions=us&oddsFormat=american&markets={MARKETS}")
        try:
            payload = _get_json(url)
        except urllib.error.HTTPError as exc:
            if exc.code == 422:      # market not offered for this event
                continue
            print(f"[nhl-research] odds fetch failed for {label}: {exc}")
            continue
        except Exception as exc:
            print(f"[nhl-research] odds fetch failed for {label}: {exc}")
            continue

        players: dict = {}
        for book in payload.get("bookmakers", []):
            for market in book.get("markets", []):
                stat = MARKET_TO_STAT.get(market.get("key", ""))
                if not stat:
                    continue
                for outcome in market.get("outcomes", []):
                    who = normalize_name(outcome.get("description", ""))
                    if not who:
                        continue
                    bucket = players.setdefault(who, {})
                    if stat == "atgs":
                        # anytime scorer is a price, not a number
                        if outcome.get("name", "").lower() == "yes" and stat not in bucket:
                            bucket[stat] = _american(outcome.get("price"))
                    elif outcome.get("name", "").lower() == "over" and stat not in bucket:
                        bucket[stat] = outcome.get("point")
        if players:
            out[label] = players

    print(f"[nhl-research] prop lines for {len(out)} of {len(games)} games")
    return out


def _american(price) -> str:
    try:
        value = int(price)
    except (TypeError, ValueError):
        return ""
    return f"+{value}" if value > 0 else str(value)
