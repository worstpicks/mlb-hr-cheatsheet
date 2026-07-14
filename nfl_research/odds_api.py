"""Player prop lines from The Odds API (free key at the-odds-api.com).

Set the ODDS_API_KEY environment variable to enable. Without a key (or in the
offseason before books post props) the slate simply builds without prop lines.

Free tier is 500 credits/month; one build with the default markets costs
(#games x #markets) credits, so a weekly refresh fits comfortably.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

BASE = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl"

# The Odds API market key -> our stat key ("atd" = anytime TD, american odds)
MARKET_TO_STAT = {
    "player_pass_attempts": "pass_att",
    "player_pass_yds": "pass_yds",
    "player_pass_tds": "pass_td",
    "player_rush_attempts": "rush_att",
    "player_rush_yds": "rush_yds",
    "player_receptions": "rec",
    "player_reception_yds": "rec_yds",
    "player_anytime_td": "atd",
}


def normalize_name(name: str) -> str:
    name = re.sub(r"[.'`-]", "", (name or "").lower())
    name = re.sub(r"\s+(jr|sr|ii|iii|iv|v)$", "", name.strip())
    return re.sub(r"\s+", " ", name)


def _get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "worstpickz-nfl-research"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_props(games: list[dict]) -> dict:
    """Return {"AwayName @ HomeName": {normalized player: {stat_key: line, "atd": "+150"}}}.

    Empty dict when ODDS_API_KEY is unset or books have no props posted yet.
    """
    api_key = os.environ.get("ODDS_API_KEY", "").strip()
    if not api_key:
        print("[nfl-research] ODDS_API_KEY not set - skipping player prop lines")
        return {}

    try:
        events = _get_json(f"{BASE}/events?apiKey={api_key}")
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"[nfl-research] The Odds API events fetch failed: {exc}")
        return {}

    wanted = {f"{g['away_name']} @ {g['home_name']}" for g in games}
    markets = ",".join(MARKET_TO_STAT)
    props: dict[str, dict] = {}

    for event in events:
        key = f"{event.get('away_team')} @ {event.get('home_team')}"
        if key not in wanted:
            continue
        url = (
            f"{BASE}/events/{event['id']}/odds?apiKey={api_key}"
            f"&regions=us&markets={markets}&oddsFormat=american"
        )
        try:
            payload = _get_json(url)
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            print(f"[nfl-research] props fetch failed for {key}: {exc}")
            continue
        game_props: dict[str, dict] = {}
        for book in payload.get("bookmakers", []):
            for market in book.get("markets", []):
                stat_key = MARKET_TO_STAT.get(market.get("key"))
                if not stat_key:
                    continue
                for outcome in market.get("outcomes", []):
                    player = normalize_name(outcome.get("description") or "")
                    if not player:
                        continue
                    slot = game_props.setdefault(player, {})
                    if stat_key == "atd":
                        # anytime TD is priced, not a line; keep "Yes" odds
                        if outcome.get("name") == "Yes" and "atd" not in slot:
                            price = outcome.get("price")
                            slot["atd"] = f"+{price}" if isinstance(price, int) and price > 0 else str(price)
                    else:
                        # Over/Under share the same point; first book wins
                        if outcome.get("point") is not None and stat_key not in slot:
                            slot[stat_key] = outcome["point"]
        if game_props:
            props[key] = game_props
    if props:
        print(f"[nfl-research] prop lines found for {len(props)} game(s)")
    else:
        print("[nfl-research] no player prop lines posted yet (normal in the offseason)")
    return props
