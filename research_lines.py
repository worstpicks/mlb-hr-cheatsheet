"""Data for the research tabs' Moneyline & Puck Line / Spread tab.

Two files per sport, both refreshed once a day inside the daily research run:

  preview/data/results-<sport>.json  every team's recent games -- final score and
      DraftKings' closing spread / total -- from ESPN's public game summaries (no
      key). A rolling log: each run adds the last two days, and each team keeps
      its last KEEP_PER_TEAM games so "Last 10" stays full across an off-season.
  preview/data/lines-<sport>.json    tonight's and the coming days' moneyline,
      spread / puck line and total from The Rundown (therundown.io). Full-game main
      lines only, which the free plan carries: one request per sport and date, a
      few dozen data points a game, well inside the free 20,000 a day. NBA and NFL
      games The Rundown leaves unpriced -- or every game, when no key reaches the run
      (10/15-10/21 every daily run skipped the lines that way) -- get DraftKings'
      lines from ESPN's public odds API instead, so the tab is never left without one.

The Rundown key is read from the RUNDOWN_API_KEY environment variable (a GitHub
Actions secret in the daily run), else from ~/.config/worstpickz/rundown.key on
this machine. It is never printed, logged or written anywhere.

    python research_lines.py --date 2026-10-15            # daily: results + tonight's lines
    python research_lines.py --date 2026-10-15 --sports nhl
    python research_lines.py --sports nhl --results-from 2026-03-15 --results-to 2026-06-25   # backfill
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import date as Date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "preview" / "data"
BASE = "https://therundown.io/api/v2"
KEY_FILE = Path.home() / ".config" / "worstpickz" / "rundown.key"

# sport -> (Rundown sport id, days to pull from the run's date)
SPORTS = {
    "nhl": (6, 2),
    "nba": (4, 2),
    "nfl": (2, 7),
    "mlb": (3, 2),
}
MARKETS = "1,2,3"  # moneyline, spread / puck line / run line, total
BOOKS = {
    19: "DraftKings", 23: "FanDuel", 22: "BetMGM", 35: "Caesars", 24: "theScore Bet",
    3: "Pinnacle", 2: "Bovada", 6: "BetOnline", 21: "Unibet", 32: "Circa", 4: "Sportsbetting",
}
# The Rundown's abbreviation -> the one the MLB research slate uses (it carries no team names)
MLB_ABBR = {"CHW": "CWS", "ARI": "AZ", "WAS": "WSH", "KCR": "KC", "SDP": "SD", "SFG": "SF", "TBR": "TB", "OAK": "ATH"}


def api_key() -> str:
    key = os.environ.get("RUNDOWN_API_KEY", "").strip()
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8-sig").strip()
    return key


def et_offset_minutes(day: Date) -> int:
    """Minutes Eastern sits behind UTC on that day (240 in daylight time, 300 in standard)."""
    # second Sunday of March to the first Sunday of November
    mar = Date(day.year, 3, 8 + (6 - Date(day.year, 3, 8).weekday()) % 7)
    nov = Date(day.year, 11, 1 + (6 - Date(day.year, 11, 1).weekday()) % 7)
    return 240 if mar <= day < nov else 300


def get(path: str, key: str):
    req = urllib.request.Request(f"{BASE}{path}", headers={
        "X-TheRundown-Key": key, "Accept": "application/json", "User-Agent": "worstpickz-research"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        used = resp.headers.get("x-datapoints")
        left = resp.headers.get("x-datapoints-monthly-remaining")
        return json.loads(resp.read().decode("utf-8")), used, left


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", text.lower())


def et_date(iso: str) -> str:
    when = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return (when - timedelta(minutes=et_offset_minutes(when.date()))).date().isoformat()


# ---- the site's own games, so each line lands on the page's game id ----------

def site_games(sport: str, days: list[str]) -> list[dict]:
    out = []
    if sport == "nhl":
        for d in days:
            p = DATA / f"nhl-research-{d}.json"
            if p.exists():
                for g in json.loads(p.read_text(encoding="utf-8")).get("games") or []:
                    out.append({"id": str(g["id"]), "date": d, "away": g["away"], "home": g["home"],
                                "away_name": g.get("away_name", ""), "home_name": g.get("home_name", "")})
    elif sport == "nba":
        for d in days:
            p = DATA / f"nba-research-{d}.json"
            if p.exists():
                for g in json.loads(p.read_text(encoding="utf-8")).get("games") or []:
                    s = g.get("sides") or {}
                    out.append({"id": str(g["id"]), "date": d,
                                "away": (s.get("away") or {}).get("abbr", ""), "home": (s.get("home") or {}).get("abbr", ""),
                                "away_name": (s.get("away") or {}).get("name", ""), "home_name": (s.get("home") or {}).get("name", "")})
    elif sport == "nfl":
        for p in sorted(DATA.glob("nfl-research-*-W*.json")):
            for g in json.loads(p.read_text(encoding="utf-8")).get("games") or []:
                d = et_date(g["kickoff"]) if g.get("kickoff") else ""
                if d in days:
                    out.append({"id": str(g["id"]), "date": d, "away": g["away"], "home": g["home"],
                                "away_name": g.get("away_name", ""), "home_name": g.get("home_name", "")})
    elif sport == "mlb":
        for d in days:
            p = DATA / f"research-{d}.json"
            if p.exists():
                for g in json.loads(p.read_text(encoding="utf-8")).get("games") or []:
                    out.append({"id": str(g.get("gamePk")), "date": d, "away": g.get("away", ""),
                                "home": g.get("home", ""), "away_name": "", "home_name": ""})
    return out


def same_team(site_abbr: str, site_name: str, team: dict, sport: str) -> bool:
    full = norm(f"{team.get('name', '')} {team.get('mascot', '')}")
    mascot = norm(team.get("mascot", ""))
    if site_name:
        n = norm(site_name)
        return n == full or (mascot and n.endswith(mascot))
    abbr = team.get("abbreviation", "")
    return site_abbr == (MLB_ABBR.get(abbr, abbr) if sport == "mlb" else abbr)


# ---- one event's lines ---------------------------------------------------------

def _price(prices: dict, book: str):
    p = prices.get(book) or {}
    if p.get("closed_at"):
        return None
    return p.get("price")


def event_lines(ev: dict) -> dict:
    """{book: {"ml": {away, home}, "spread": {away: [line, price], home: [...]}, "total": [line, over, under]}}"""
    teams = {("home" if t.get("is_home") else "away"): t for t in ev.get("teams_normalized") or []}
    side_of = {}
    for side, t in teams.items():
        side_of[norm(f"{t.get('name', '')} {t.get('mascot', '')}")] = side
        side_of[norm(t.get("mascot", ""))] = side
    books: dict = {}

    def side(participant):
        n = norm(participant.get("name", ""))
        return side_of.get(n) or next((s for k, s in side_of.items() if k and n.endswith(k)), None)

    for m in ev.get("markets") or []:
        if m.get("period_id", 0) != 0:
            continue
        mid = m.get("market_id")
        for part in m.get("participants") or []:
            if mid in (1, 2):
                s = side(part)
                if not s:
                    continue
            for line in part.get("lines") or []:
                for book, pr in (line.get("prices") or {}).items():
                    if mid != 1 and not pr.get("is_main_line"):
                        continue
                    price = _price(line["prices"], book)
                    if price in (None, 0):
                        continue
                    b = books.setdefault(book, {})
                    if mid == 1:
                        b.setdefault("ml", {})[s] = price
                    elif mid == 2:
                        b.setdefault("spread", {})[s] = [float(line.get("value")), price]
                    elif mid == 3:
                        t = b.setdefault("total", {"line": float(line.get("value"))})
                        t["over" if part.get("name", "").lower() == "over" else "under"] = price
    return books


def implied(american: float) -> float:
    return 100 / (american + 100) if american > 0 else -american / (-american + 100)


def summarize(books: dict) -> dict:
    """Best price on each side, the books' fair (no-vig) win chances, the consensus total."""
    rows, fair = [], []
    for book, b in books.items():
        name = BOOKS.get(int(book), f"Book {book}")
        ml, sp, tot = b.get("ml") or {}, b.get("spread") or {}, b.get("total") or {}
        rows.append({"book": name, "ml": ml or None, "spread": sp or None,
                     "total": tot if "over" in tot and "under" in tot else None})
        if "away" in ml and "home" in ml:
            a, h = implied(ml["away"]), implied(ml["home"])
            fair.append(a / (a + h))
    rows.sort(key=lambda r: list(BOOKS.values()).index(r["book"]) if r["book"] in BOOKS.values() else 99)

    def best_ml(s):
        c = [(r["ml"][s], r["book"]) for r in rows if r["ml"] and s in r["ml"]]
        return {"price": max(c)[0], "book": max(c)[1]} if c else None

    def best_spread(s):
        c = [(r["spread"][s][0], r["spread"][s][1], r["book"]) for r in rows if r["spread"] and s in r["spread"]]
        if not c:
            return None
        line = statistics.mode([x[0] for x in c])
        at = [x for x in c if x[0] == line]
        top = max(at, key=lambda x: x[1])
        return {"line": line, "price": top[1], "book": top[2]}

    totals = [r["total"] for r in rows if r["total"]]
    total = None
    if totals:
        line = statistics.mode([t["line"] for t in totals])
        at = [(t, r["book"]) for r in rows if (t := r["total"]) and t["line"] == line]
        o = max(at, key=lambda x: x[0]["over"]); u = max(at, key=lambda x: x[0]["under"])
        total = {"line": line, "over": o[0]["over"], "over_book": o[1], "under": u[0]["under"], "under_book": u[1]}
    return {
        "books": rows,
        "best": {"ml_away": best_ml("away"), "ml_home": best_ml("home"),
                 "spread_away": best_spread("away"), "spread_home": best_spread("home"), "total": total},
        "fair": {"away": round(statistics.mean(fair), 4), "home": round(1 - statistics.mean(fair), 4)} if fair else None,
    }


# ---- DraftKings via ESPN: the fallback ------------------------------------------

ESPN_CORE = {"nba": "basketball/leagues/nba", "nfl": "football/leagues/nfl"}


def espn_event_lines(sport: str, event_id: str) -> dict | None:
    """{"19": {ml, spread, total}} -- DraftKings (ESPN provider 100), keyed like The Rundown's book id."""
    url = (f"https://sports.core.api.espn.com/v2/sports/{ESPN_CORE[sport]}/events/{event_id}"
           f"/competitions/{event_id}/odds?lang=en&region=us")
    try:
        items = espn_get(url).get("items") or []
    except Exception:
        return None
    it = next((x for x in items if str((x.get("provider") or {}).get("id")) == "100"), None)
    if not it:
        return None
    b: dict = {}
    a, h = it.get("awayTeamOdds") or {}, it.get("homeTeamOdds") or {}
    if a.get("moneyLine") is not None and h.get("moneyLine") is not None:
        b["ml"] = {"away": int(a["moneyLine"]), "home": int(h["moneyLine"])}
    sp = {}
    for side, o in (("away", a), ("home", h)):
        line = _num((((o.get("current") or {}).get("pointSpread") or {}).get("american")))
        if line is not None and o.get("spreadOdds") is not None:
            sp[side] = [line, int(o["spreadOdds"])]
    if len(sp) == 2:
        b["spread"] = sp
    if it.get("overUnder") is not None and it.get("overOdds") is not None and it.get("underOdds") is not None:
        b["total"] = {"line": float(it["overUnder"]), "over": int(it["overOdds"]), "under": int(it["underOdds"])}
    return {"19": b} if b else None


def espn_fill(sport: str, start: Date, result: dict | None) -> dict | None:
    """Price every site game The Rundown did not, from DraftKings via ESPN."""
    if sport not in ESPN_CORE:
        return result
    days = [(start + timedelta(days=i)).isoformat() for i in range(SPORTS[sport][1])]
    games = site_games(sport, days)
    if not games:
        return result
    result = result or {"sport": sport, "source": "DraftKings via ESPN",
                        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "days": days, "games": {}}
    filled = 0
    for g in games:
        if g["id"] in result["games"]:
            continue
        books = espn_event_lines(sport, g["id"])
        if books:
            result["games"][g["id"]] = {"date": g["date"], "kickoff": None, "away": g["away"], "home": g["home"],
                                        "source": "DraftKings via ESPN", **summarize(books)}
            filled += 1
    if filled:
        print(f"[lines] {sport}: {filled} game(s) priced from DraftKings via ESPN")
        if result.get("source") == "The Rundown":
            result["source"] = "The Rundown and DraftKings via ESPN"
    return result


# ---- the run -------------------------------------------------------------------

def pull(sport: str, start: Date, key: str) -> dict | None:
    sport_id, n_days = SPORTS[sport]
    days = [(start + timedelta(days=i)).isoformat() for i in range(n_days)]
    games = site_games(sport, days)
    if not games:
        print(f"[lines] {sport}: no research slate for {days[0]}..{days[-1]}; skipped (no request made)")
        return None
    wanted = {g["date"] for g in games}
    out, unmatched, spent = {}, [], 0
    for d in sorted(wanted):
        try:
            data, used, left = get(f"/sports/{sport_id}/events/{d}?market_ids={MARKETS}&main_line=true"
                                   f"&offset={et_offset_minutes(Date.fromisoformat(d))}", key)
        except urllib.error.HTTPError as exc:
            print(f"[lines] {sport} {d}: HTTP {exc.code} -- keeping what was pulled")
            break
        except Exception as exc:  # network trouble never fails the research run
            print(f"[lines] {sport} {d}: {type(exc).__name__} -- keeping what was pulled")
            break
        spent += int(used or 0)
        for ev in data.get("events") or []:
            teams = {("home" if t.get("is_home") else "away"): t for t in ev.get("teams_normalized") or []}
            if len(teams) != 2:
                continue
            site = next((g for g in games if g["date"] == et_date(ev["event_date"])
                         and same_team(g["away"], g["away_name"], teams["away"], sport)
                         and same_team(g["home"], g["home_name"], teams["home"], sport)), None)
            label = f"{teams['away'].get('abbreviation')} @ {teams['home'].get('abbreviation')}"
            if not site:
                unmatched.append(f"{d} {label}")
                continue
            books = event_lines(ev)
            if not books:
                continue
            out[site["id"]] = {"date": site["date"], "kickoff": ev["event_date"],
                               "away": site["away"], "home": site["home"], **summarize(books)}
        time.sleep(1.2)  # the free plan allows one request a second
    print(f"[lines] {sport}: {len(out)} of {len(games)} games priced over {len(wanted)} day(s), "
          f"{spent} data points" + (f", {left} left this month" if left else "")
          + (f"; no site game for {', '.join(unmatched)}" if unmatched else ""))
    return {"sport": sport, "source": "The Rundown", "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "days": days, "games": out}


# ---- results: who won, who covered, over or under -------------------------------
# Final scores and DraftKings' closing spread / total from ESPN's public game
# summaries (no key, no Rundown points). Kept in preview/data/results-<sport>.json,
# a rolling log the Lines tab reads team by team: each day's run adds yesterday.

ESPN = {"nhl": "hockey/nhl", "nfl": "football/nfl", "nba": "basketball/nba"}
ESPN_ABBR = {"nhl": {"LA": "LAK", "NJ": "NJD", "SJ": "SJS", "TB": "TBL", "UTAH": "UTA"}}
# Each team's last games kept, so "Last 10" stays full across an off-season
# (Doink reaches back into last season the same way).
KEEP_PER_TEAM = 25


_TEAMS: dict = {}


def league_teams(sport: str) -> set:
    """The league's own clubs, so all-star games (AFC v NFC) and exhibitions
    against outside clubs never land in a team's log."""
    if sport not in _TEAMS:
        alias = ESPN_ABBR.get(sport, {})
        data = espn_get(f"https://site.api.espn.com/apis/site/v2/sports/{ESPN[sport]}/teams")
        _TEAMS[sport] = {alias.get(t["team"]["abbreviation"], t["team"]["abbreviation"])
                         for t in data["sports"][0]["leagues"][0]["teams"]}
    return _TEAMS[sport]


def espn_get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (worstpickz-research)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _odds(v):
    if v in (None, "", "-"):
        return None
    if str(v).upper() == "EVEN":
        return 100
    try:
        return int(float(str(v).replace("+", "")))
    except ValueError:
        return None


def _num(v):
    try:
        return float(re.sub(r"^[ou]", "", str(v)))
    except (TypeError, ValueError):
        return None


def closing_line(sport: str, event_id: str) -> dict | None:
    """DraftKings' (or the first book's) closing spread, total and moneyline from the game summary."""
    try:
        s = espn_get(f"https://site.api.espn.com/apis/site/v2/sports/{ESPN[sport]}/summary?event={event_id}")
    except Exception:
        return None
    pc = s.get("pickcenter") or []
    if not pc:
        return None
    p = next((x for x in pc if "draftkings" in ((x.get("provider") or {}).get("name") or "").lower()), pc[0])
    ml, sp, tot = p.get("moneyline") or {}, p.get("pointSpread") or {}, p.get("total") or {}
    close = lambda node, *path: ((node.get(path[0]) or {}).get("close") or {}).get(path[1])
    out = {"book": (p.get("provider") or {}).get("name"),
           "spread_home": _num(close(sp, "home", "line")),
           "total": _num(close(tot, "over", "line")),
           "ml_away": _odds(close(ml, "away", "odds")), "ml_home": _odds(close(ml, "home", "odds"))}
    if out["spread_home"] is None and p.get("spread") is not None:      # older games keep only the summary fields
        out["spread_home"] = _num(p.get("spread"))
    if out["total"] is None and p.get("overUnder") is not None:
        out["total"] = _num(p.get("overUnder"))
    return out if any(v is not None for k, v in out.items() if k != "book") else None


def espn_results(sport: str, day: str, known: dict | None = None) -> list[dict]:
    """Every final game on one Eastern date, with its score and closing line.
    A game already logged with its closing line is not asked for again."""
    sb = espn_get(f"https://site.api.espn.com/apis/site/v2/sports/{ESPN[sport]}/scoreboard?dates={day.replace('-', '')}")
    alias = ESPN_ABBR.get(sport, {})
    out = []
    for e in sb.get("events") or []:
        comp = (e.get("competitions") or [{}])[0]
        status = ((comp.get("status") or {}).get("type") or {})
        if not status.get("completed"):
            continue
        side = {c["homeAway"]: c for c in comp.get("competitors") or []}
        if set(side) != {"away", "home"}:
            continue
        ab = lambda c: alias.get(c["team"]["abbreviation"], c["team"]["abbreviation"])
        if not {ab(side["away"]), ab(side["home"])} <= league_teams(sport):
            continue
        detail = (status.get("shortDetail") or status.get("detail") or "")
        extra = "SO" if "SO" in detail else "OT" if "OT" in detail else None
        out.append({"id": str(e["id"]), "date": day, "away": ab(side["away"]), "home": ab(side["home"]),
                    "as": int(side["away"].get("score") or 0), "hs": int(side["home"].get("score") or 0),
                    "extra": extra, "type": (e.get("season") or {}).get("type"),
                    "close": None})
        prior = (known or {}).get(str(e["id"]))
        if prior and prior.get("close"):
            out[-1]["close"] = prior["close"]
        else:
            out[-1]["close"] = closing_line(sport, e["id"])
            time.sleep(0.25)
    return out


def update_results(sport: str, days: list[str]) -> None:
    path = DATA / f"results-{sport}.json"
    have = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"sport": sport, "games": []}
    try:
        clubs = league_teams(sport)
    except Exception:
        clubs = None
    games = {g["id"]: g for g in have.get("games") or []
             if not clubs or {g["away"], g["home"]} <= clubs}
    added = 0
    for d in days:
        try:
            for g in espn_results(sport, d, games):
                added += g["id"] not in games
                games[g["id"]] = g
        except Exception as exc:  # never fails the research run
            print(f"[results] {sport} {d}: {type(exc).__name__}; skipped")
    # keep a game while it is among either team's last KEEP_PER_TEAM
    by_team: dict = {}
    for g in sorted(games.values(), key=lambda g: (g["date"], g["id"]), reverse=True):
        for t in (g["away"], g["home"]):
            by_team.setdefault(t, []).append(g["id"])
    keep_ids = {i for ids in by_team.values() for i in ids[:KEEP_PER_TEAM]}
    kept = sorted((g for g in games.values() if g["id"] in keep_ids), key=lambda g: (g["date"], g["id"]))
    priced = sum(1 for g in kept if g.get("close"))
    path.write_text(json.dumps({"sport": sport, "source": "ESPN (scores, DraftKings closing lines)",
                                "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                "games": kept}, separators=(",", ":")), encoding="utf-8")
    span = f" from {days[0]}..{days[-1]}" if days else ""
    print(f"[results] {sport}: {added} new game(s){span}; {len(kept)} kept, {priced} with a closing line")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", default=None, help="first day, YYYY-MM-DD (default: today, Eastern)")
    ap.add_argument("--sports", default=",".join(SPORTS), help="comma list: nhl,nba,nfl,mlb")
    ap.add_argument("--results-days", type=int, default=2,
                    help="days of finished games to (re)read before --date (default 2; 7 to backfill a week)")
    ap.add_argument("--results-from", default=None,
                    help="backfill finished games from this date (YYYY-MM-DD) through --results-to; skips tonight's lines")
    ap.add_argument("--results-to", default=None, help="last day of a --results-from backfill")
    args = ap.parse_args()
    now = datetime.now(timezone.utc)
    start = Date.fromisoformat(args.date) if args.date else (now - timedelta(minutes=et_offset_minutes(now.date()))).date()
    sports = [s.strip() for s in args.sports.split(",") if s.strip() in SPORTS]

    if args.results_from:  # a one-off backfill
        a, b = Date.fromisoformat(args.results_from), Date.fromisoformat(args.results_to or args.results_from)
        span = [(a + timedelta(days=i)).isoformat() for i in range((b - a).days + 1)]
        for sport in sports:
            if sport in ESPN:
                update_results(sport, span)
        return 0

    # finished games first: free, and the Lines tab grades every team off them
    past = [(start - timedelta(days=i)).isoformat() for i in range(args.results_days, 0, -1)]
    for sport in sports:
        if sport in ESPN:
            update_results(sport, past)

    key = api_key()
    if not key:
        # Said loudly: from 10/15 to 10/21 this line was the only sign every daily run had skipped the lines.
        print("[lines] WARNING: RUNDOWN_API_KEY is not set (check the GitHub Actions secret); "
              "NBA/NFL fall back to DraftKings via ESPN, NHL/MLB lines are left as they were")
    for sport in sports:
        result = pull(sport, start, key) if key else None
        result = espn_fill(sport, start, result)
        if result:  # written even when nothing is priced yet, so the page's tab never asks for a missing file
            (DATA / f"lines-{sport}.json").write_text(json.dumps(result, separators=(",", ":")), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
