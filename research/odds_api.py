"""MLB home-run prop lines from The Odds API (free key at the-odds-api.com).

Set the ODDS_API_KEY environment variable to enable. Without a key (or before
books post lines for the slate) the research JSON simply builds without odds.

Credit budget, which is why this only ever pulls the one market:
  /events                       0 credits (exempt from quota)
  /events/{id}/odds             [markets] x [regions] credits
With markets=batter_home_runs and regions=us that is 1 credit per game, so a
~15-game slate costs ~15 credits. The free tier is 500 credits/month, which
covers one refresh per day with a little room to spare -- run this more than
once a day and you will run out before month end.

Only the current line is fetched. Line movement needs the historical-odds
endpoint, which is paid-plan only.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.the-odds-api.com/v4/sports/baseball_mlb"

HR_MARKET = "batter_home_runs"
REGIONS = "us"

# Books to prefer when several price the same batter, best first. The list is
# only a tie-breaker: any book is better than no line.
BOOK_PRIORITY = [
    "draftkings",
    "fanduel",
    "betmgm",
    "caesars",
    "pointsbetus",
    "betrivers",
]

# The slate carries MLB team ids; The Odds API carries full club names. Ids are
# the stable join -- abbreviations disagree between sources (WSH vs WAS) and
# club names drift (Oakland Athletics -> Athletics).
MLB_TEAM_NAMES = {
    108: "Los Angeles Angels",
    109: "Arizona Diamondbacks",
    110: "Baltimore Orioles",
    111: "Boston Red Sox",
    112: "Chicago Cubs",
    113: "Cincinnati Reds",
    114: "Cleveland Guardians",
    115: "Colorado Rockies",
    116: "Detroit Tigers",
    117: "Houston Astros",
    118: "Kansas City Royals",
    119: "Los Angeles Dodgers",
    120: "Washington Nationals",
    121: "New York Mets",
    133: "Athletics",
    134: "Pittsburgh Pirates",
    135: "San Diego Padres",
    136: "Seattle Mariners",
    137: "San Francisco Giants",
    138: "St. Louis Cardinals",
    139: "Tampa Bay Rays",
    140: "Texas Rangers",
    141: "Toronto Blue Jays",
    142: "Minnesota Twins",
    143: "Philadelphia Phillies",
    144: "Atlanta Braves",
    145: "Chicago White Sox",
    146: "Miami Marlins",
    147: "New York Yankees",
    158: "Milwaukee Brewers",
}

# Nickname -> id, so a renamed or relocated club still resolves. Every current
# nickname is unique across the league.
_NICKNAME_TO_ID = {name.split()[-1].lower(): tid for tid, name in MLB_TEAM_NAMES.items()}


def team_id_from_name(name: str) -> int | None:
    """Resolve an Odds API club name to an MLB team id."""
    n = re.sub(r"\s+", " ", (name or "").strip().lower())
    if not n:
        return None
    for tid, full in MLB_TEAM_NAMES.items():
        if full.lower() == n:
            return tid
    # Fall back to the nickname, which survives city/branding changes.
    return _NICKNAME_TO_ID.get(n.split()[-1])


def normalize_name(name: str) -> str:
    """Match Savant/MLB naming against sportsbook naming."""
    name = re.sub(r"[.'`’-]", "", (name or "").lower())
    name = re.sub(r"\s+(jr|sr|ii|iii|iv|v)$", "", name.strip())
    return re.sub(r"\s+", " ", name)


def american_odds(price) -> str | None:
    if price is None:
        return None
    try:
        n = int(price)
    except (TypeError, ValueError):
        return None
    return f"+{n}" if n > 0 else str(n)


def implied_pct(price) -> float | None:
    """American odds -> implied probability, rounded to a tenth of a percent."""
    try:
        n = int(price)
    except (TypeError, ValueError):
        return None
    if n == 0:
        return None
    prob = 100 / (n + 100) if n > 0 else -n / (-n + 100)
    return round(prob * 100, 1)


def _get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "worstpickz-mlb-research"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8")), dict(resp.headers)


def _book_rank(key: str) -> int:
    try:
        return BOOK_PRIORITY.index(key)
    except ValueError:
        return len(BOOK_PRIORITY)


def parse_event_odds(payload: dict) -> dict:
    """Pull the Over 0.5 HR price for each batter out of one event's odds.

    Returns {normalized name: {"odds", "impliedPct", "line", "book", "under"}}.
    """
    out: dict[str, dict] = {}
    for book in payload.get("bookmakers") or []:
        book_key = book.get("key") or ""
        rank = _book_rank(book_key)
        for market in book.get("markets") or []:
            if market.get("key") != HR_MARKET:
                continue
            # Over and Under for a batter arrive as separate outcomes sharing a
            # description, so collect both before deciding.
            by_player: dict[str, dict] = {}
            for outcome in market.get("outcomes") or []:
                player = normalize_name(outcome.get("description") or "")
                if not player:
                    continue
                slot = by_player.setdefault(player, {})
                side = (outcome.get("name") or "").lower()
                if side in ("over", "under"):
                    slot[side] = outcome
            for player, sides in by_player.items():
                over = sides.get("over")
                if not over:
                    continue
                # 0.5 is the standard "to hit a home run" line; alternate lines
                # (1.5+) are a different bet and would be misleading here.
                point = over.get("point")
                if point is not None and abs(float(point) - 0.5) > 0.01:
                    continue
                prev = out.get(player)
                if prev is not None and prev["_rank"] <= rank:
                    continue
                under = sides.get("under") or {}
                out[player] = {
                    "odds": american_odds(over.get("price")),
                    "impliedPct": implied_pct(over.get("price")),
                    "line": 0.5 if point is None else float(point),
                    "book": book_key,
                    "under": american_odds(under.get("price")),
                    "_rank": rank,
                }
    for slot in out.values():
        slot.pop("_rank", None)
    return out


def fetch_hr_props(games: list[dict]) -> dict:
    """Return {"AWY @ HOM": {normalized batter: {...odds...}}} for the slate.

    Empty dict when ODDS_API_KEY is unset, the slate has no matching events, or
    books have not posted home-run props yet.
    """
    api_key = os.environ.get("ODDS_API_KEY", "").strip()
    if not api_key:
        print("[mlb-research] ODDS_API_KEY not set - skipping HR prop lines")
        return {}

    try:
        events, _ = _get_json(f"{BASE}/events?apiKey={urllib.parse.quote(api_key)}")
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"[mlb-research] The Odds API events fetch failed: {exc}")
        return {}

    wanted: dict[tuple[int, int], str] = {}
    for g in games:
        away_id = g.get("awayTeamId")
        home_id = g.get("homeTeamId")
        if away_id is None or home_id is None:
            continue
        wanted[(int(away_id), int(home_id))] = f"{g.get('away')} @ {g.get('home')}"

    props: dict[str, dict] = {}
    remaining = None
    unmatched: list[str] = []
    for event in events:
        away_id = team_id_from_name(event.get("away_team"))
        home_id = team_id_from_name(event.get("home_team"))
        key = wanted.get((away_id, home_id)) if away_id and home_id else None
        if not key:
            unmatched.append(f"{event.get('away_team')} @ {event.get('home_team')}")
            continue
        url = (
            f"{BASE}/events/{event['id']}/odds?apiKey={urllib.parse.quote(api_key)}"
            f"&regions={REGIONS}&markets={HR_MARKET}&oddsFormat=american"
        )
        try:
            payload, headers = _get_json(url)
        except urllib.error.HTTPError as exc:
            # 422 just means this event has no such market yet.
            if exc.code != 422:
                print(f"[mlb-research] HR props fetch failed for {key}: {exc}")
            continue
        except urllib.error.URLError as exc:
            print(f"[mlb-research] HR props fetch failed for {key}: {exc}")
            continue
        remaining = headers.get("x-requests-remaining", remaining)
        parsed = parse_event_odds(payload)
        if parsed:
            props[key] = parsed

    if props:
        total = sum(len(v) for v in props.values())
        print(f"[mlb-research] HR prop lines: {total} batters across {len(props)} game(s)")
    else:
        print("[mlb-research] no HR prop lines posted yet")
    # An event we can't map is a silent hole in coverage, so name it.
    if unmatched and not props:
        print(f"[mlb-research] no slate events matched; API listed {len(unmatched)} game(s), e.g. {unmatched[0]}")
    if remaining is not None:
        print(f"[mlb-research] The Odds API credits remaining this month: {remaining}")
    return props


def attach_hr_props_to_games(games: list[dict], props: dict) -> int:
    """Write each batter's line onto their lineup row. Returns rows matched."""
    if not props:
        return 0
    matched = 0
    for g in games:
        game_props = props.get(f"{g.get('away')} @ {g.get('home')}")
        if not game_props:
            continue
        for side in ("awayLineup", "homeLineup"):
            for row in g.get(side) or []:
                entry = game_props.get(normalize_name(row.get("name") or ""))
                if not entry:
                    continue
                row["hrOdds"] = entry
                matched += 1
    return matched
