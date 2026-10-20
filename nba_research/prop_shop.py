"""The WorstPickz Prop Shop: the night's handpicked NBA props, rated and ranked.

    python -m nba_research.dk_props --date 2026-10-20     # DraftKings prices first
    python -m nba_research.prop_shop --date 2026-10-20

Reads, for the date:
  nba_research/prop_days/<date>.txt               the list (the research tab's Prop List export)
  nba_research/prop_days/<date>.first_basket.txt  "Name | TEAM" per first-basket pick
  nba_research/prop_days/<date>.lineup.txt        out / doubt / starters (checked that day)
  preview/data/nba-research-<date>.json           the research slate: rosters, recent logs, totals
  nba_research/season_rates/<last season>.json.gz every game of last season (prop_fit.py)
  nba_research/prop_shop_fit.json                 the fitted model
  data/nba-dk-props-<date>.json                   DraftKings prices (dk_props.py)

Every prop is projected (prop_model.py), given its chance to cash, and rated out
of 100 the way the NHL sheet rates a scorer: the chance, his track record at the
line, the matchup, his role and the price. Writes preview/nba-research/prop-shop.html
(the current night), archive/<date>.html and prop-shop-manifest.json.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from nba_research import dk_props, first_basket, prop_grade, prop_model as pm

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "nba_research"
DAYS = HERE / "prop_days"
DATA = ROOT / "data"
SLATES = ROOT / "preview" / "data"
NBA_DIR = ROOT / "preview" / "nba-research"
ARCHIVE = NBA_DIR / "prop-shop-archive"
MANIFEST = NBA_DIR / "prop-shop-manifest.json"
TEMPLATE = HERE / "templates" / "prop_shop.html"
SEASON = 2027                       # 2026-27
LAST = "2025-26"

WEIGHTS = {"chance": 40, "form": 20, "matchup": 15, "role": 15, "price": 10}
BANDS = [(90, "elite", "Elite"), (80, "strong", "Strong"), (70, "playable", "Playable"), (60, "thin", "Thin"), (0, "dart", "Dart")]
VALUE_EDGE = 4.0      # points of chance over the price's
MATCHUP_FLOOR = 50    # out of 100
MARKET_CODES = {"PTS": "pts", "REB": "reb", "AST": "ast", "3PM": "threem", "STL": "stl", "BLK": "blk",
                "PRA": "pra", "PR": "pr", "PA": "pa", "RA": "ra", "SB": "stocks", "STOCKS": "stocks"}
ICON = {"pts": "🏀", "reb": "🪟", "ast": "🍽️", "threem": "💦", "stl": "🧤", "blk": "🚫",
        "pra": "📦", "pr": "📦", "pa": "📦", "ra": "📦", "stocks": "🧤"}
STAT_WORD = {"pts": "points", "reb": "rebounds", "ast": "assists", "threem": "threes", "stl": "steals",
             "blk": "blocks", "pra": "points + rebounds + assists", "pr": "points + rebounds",
             "pa": "points + assists", "ra": "rebounds + assists", "stocks": "steals + blocks"}
POS_WORD = {"G": "guards", "F": "forwards", "C": "centers"}
# A side that wins the opening tip scores the first basket about 57% of the time.
TIP_EDGE = 0.57


def norm(name: str) -> str:
    s = unicodedata.normalize("NFD", name or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    s = re.sub(r"[.'’]", "", s)
    s = re.sub(r"\b(jr|sr|ii|iii|iv)\b", "", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


# ── inputs ─────────────────────────────────────────────────────────────────────

def load_list(date: str) -> list[dict]:
    """'2026-10-20 | Jayson Tatum | over 1.5 STL | auto, last 5, all' per line."""
    path = DAYS / f"{date}.txt"
    if not path.exists():
        raise SystemExit(f"No list for {date}: save the Prop List as {path.relative_to(ROOT)}")
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) < 3 or raw.lstrip().startswith("#"):
            continue
        m = re.match(r"(over|under)\s+([\d.]+)\s+(\S+)", parts[2], re.I)
        if not m or m.group(3).upper() not in MARKET_CODES:
            print(f"[prop_shop] WARN can't read '{parts[2]}' for {parts[1]} -- left off")
            continue
        out.append({"name": parts[1], "side": m.group(1).lower(), "line": float(m.group(2)),
                    "market": MARKET_CODES[m.group(3).upper()], "code": m.group(3).upper()})
    return out


def load_first_basket(date: str) -> list[tuple[str, str]]:
    path = DAYS / f"{date}.first_basket.txt"
    if not path.exists():
        return []
    rows = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if "|" in raw and not raw.lstrip().startswith("#"):
            name, team = (p.strip() for p in raw.split("|", 1))
            rows.append((name, team.upper()))
    return rows


def load_lineup(date: str) -> dict:
    out = {"out": {}, "doubt": {}, "starters": {}}
    path = DAYS / f"{date}.lineup.txt"
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        m = re.match(r"starters\s+(\w+):\s*(.+)$", raw)
        if m:
            out["starters"][m.group(1).upper()] = [norm(n) for n in m.group(2).split(",")]
            continue
        m = re.match(r"(out|doubt)\s+(\w+)\s+([^|]+?)\s*(?:\|\s*(.*))?$", raw)
        if m:
            out[m.group(1)][(norm(m.group(3)), m.group(2).upper())] = (m.group(4) or "").replace(" -- ", " — ")
    return out


def load_season() -> dict:
    with gzip.open(HERE / "season_rates" / f"{LAST}.json.gz", "rt", encoding="utf-8") as fh:
        return json.load(fh)


def season_logs(season: dict, pid: str) -> list[dict]:
    row = (season.get("players") or {}).get(pid)
    if not row:
        return []
    cols = season["columns"]
    out = []
    for g in row["games"]:
        d = dict(zip(cols, g))
        d.update({"type": 2, "season": season["season"], "starter": bool(d["starter"])})
        out.append(d)
    return out


def load_prices(date: str) -> dict:
    path = DATA / f"nba-dk-props-{date}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


# ── one prop ───────────────────────────────────────────────────────────────────

def stat_of(log: dict, market: str) -> float:
    return sum(log.get(s) or 0.0 for s in pm.COMBOS.get(market, (market,)))


def hits(logs: list[dict], market: str, line: float) -> list[int]:
    need = math.floor(line) + 1
    return [sum(1 for l in logs if stat_of(l, market) >= need), len(logs)]


def band_of(score: float) -> tuple[str, str]:
    for floor, key, label in BANDS:
        if score >= floor:
            return key, label
    return "dart", "Dart"


def scale(x: float, lo: float, hi: float) -> float:
    return max(0.0, min(1.0, (x - lo) / (hi - lo)))


def matchup_rank(season: dict, opp: str, pos: str, market: str) -> tuple[int, int, float, float]:
    """(rank, clubs, opp per-36 allowed, league per-36): rank 1 gives up the most."""
    parts = pm.COMBOS.get(market, (market,))
    rates = {}
    for team, by in season["allowed"].items():
        a = by.get(pos)
        if a and a["min"]:
            rates[team] = sum(a[s] for s in parts) / a["min"]
    order = sorted(rates, key=lambda t: -rates[t])
    lg = sum(season["league"][pos][s] for s in parts)
    if opp not in rates:
        return 0, len(order), 0.0, 36 * lg
    return order.index(opp) + 1, len(order), 36 * rates[opp], 36 * lg


def rate_prop(play: dict, player: dict, side: dict, opp_side: dict, game: dict, season: dict,
              fit: dict, lineup: dict, prices: dict) -> dict:
    market, line = play["market"], play["line"]
    team, opp, pos = side["abbr"], opp_side["abbr"], player["pos"]
    last = season_logs(season, player["id"])
    # research logs from last season are inside the season file already; keep its full year
    recent = [l for l in player.get("logs") or []
              if not (last and l.get("type") == 2 and l.get("season") == season["season"])]
    logs = last + recent
    logs.sort(key=lambda l: l["date"])
    pre = [l for l in logs if l.get("type") == 1 and l.get("season") == SEASON]
    reg_last = [l for l in logs if l.get("type") == 2 and l.get("season") == season["season"]]

    starters = lineup["starters"].get(team)
    starting = bool(starters) and norm(player["name"]) in starters
    minutes, min_src = pm.project_minutes(logs, team, SEASON, fit["min_decay"],
                                          starting if starters else None)
    if starters:
        if starting and minutes < 28:
            minutes += 0.5 * (28 - minutes)
            min_src += ", lifted for a projected start"
        elif not starting and minutes > 26:
            minutes -= 0.5 * (minutes - 26)
            min_src += ", trimmed: projected off the bench"
    made, mins = pm.decayed(logs, SEASON, fit["decay"])
    lg = season["league"].get(pos) or {}
    rate = pm.per_minute(made, mins, lg, fit["shrink"])
    allowed = (season["allowed"].get(opp) or {}).get(pos)
    opp_rate = {s: allowed[s] / allowed["min"] for s in pm.STATS} if allowed and allowed["min"] else None
    # the season is a new one: last year's opponent is about half of tonight's
    ratio = pm.matchup_ratio(opp_rate, lg, market, (allowed or {}).get("games", 0), turnover=0.5)
    pace = pm.pace_factor((game.get("odds") or {}).get("overUnder"), season["league_total"])
    parts = pm.COMBOS.get(market, (market,))
    proj = sum(minutes * rate[s] for s in parts) * ratio * pace
    params = fit["params"][market]
    chance = pm.chance_over(line, proj, params)
    if play["side"] == "under":
        chance = 1 - chance

    # the track record at this exact line
    newest = sorted(logs, key=lambda l: l["date"], reverse=True)
    h_season, h10, h5, h_pre = hits(reg_last, market, line), hits(newest[:10], market, line), \
        hits(newest[:5], market, line), hits(pre, market, line)
    if play["side"] == "under":
        h_season, h10, h5, h_pre = ([n - h, n] for h, n in (h_season, h10, h5, h_pre))
    # last season's year, the last ten and the preseason, shrunk toward the model
    w_h = 0.3 * h_season[0] + 1.0 * h10[0] + 0.5 * h_pre[0] + 5 * chance
    w_n = 0.3 * h_season[1] + 1.0 * h10[1] + 0.5 * h_pre[1] + 5
    track = w_h / w_n

    rank, clubs, opp36, lg36 = matchup_rank(season, opp, pos, market)
    match = round(100 * (clubs - rank) / (clubs - 1)) if rank else 50

    price, price_src = dk_props.over_price(
        ((prices.get("games") or {}).get(game["id"]) or {}).get("players", {}).get(player["id"]), market, line) \
        if play["side"] == "over" else (None, "")
    implied = 100 * dk_props.implied(price) if price is not None else None
    edge = round(100 * chance - implied, 1) if implied is not None else None
    book_mid = book_center(((((prices.get("games") or {}).get(game["id"]) or {}).get("players") or {})
                            .get(player["id"]) or {}).get("milestones", {}).get(market))

    doubt = lineup["doubt"].get((norm(player["name"]), team))
    status = (player.get("injury") or "").lower()
    if not doubt and status in ("day-to-day", "questionable", "doubtful"):
        doubt = player.get("injury_note") or player.get("injury")
    small = len(reg_last) + len(pre) < 8 or not reg_last
    new_team = bool(reg_last) and reg_last[-1].get("team") != team

    score_parts = {
        "chance": round(WEIGHTS["chance"] * scale(chance, 0.20, 0.80), 1),
        "form": round(WEIGHTS["form"] * scale(track, 0.20, 0.80), 1),
        "matchup": round(WEIGHTS["matchup"] * match / 100, 1),
        "role": round(WEIGHTS["role"] * scale(minutes, 14, 34) - (5 if doubt else 0), 1),
        "price": round(WEIGHTS["price"] * scale(edge, -10, 10), 1) if edge is not None else WEIGHTS["price"] / 2,
    }
    score_parts["role"] = max(0.0, score_parts["role"])
    score = round(sum(score_parts.values()), 1)
    band, band_label = band_of(score)

    avg = lambda rows: round(sum(stat_of(l, market) for l in rows) / len(rows), 2) if rows else None
    prop_id = f"{player['id']}-{market}-{line:g}"
    row = {
        "id": prop_id, "pid": player["id"], "name": player["name"], "team": team, "opp": opp,
        "game": game["id"], "kick": game["date"], "pos": pos, "role": player.get("position") or pos,
        "headshot": player.get("headshot", ""), "market": market, "label": pm.LABELS[market],
        "word": STAT_WORD[market], "icon": ICON[market], "code": play["code"],
        "side": play["side"], "line": line, "need": math.floor(line) + 1,
        "proj": round(proj, 2), "mean": round(pm.mean(params["b"], proj), 2), "chance": round(100 * chance, 1),
        "minutes": round(minutes, 1), "min_src": min_src, "starting": starting, "starters_known": bool(starters),
        "per36": round(36 * sum(rate[s] for s in parts), 2), "ratio": round(ratio, 3), "pace": round(pace, 3),
        "total": (game.get("odds") or {}).get("overUnder"),
        "hits": {"season": h_season, "last10": h10, "last5": h5, "pre": h_pre},
        "avg": {"season": avg(reg_last), "last10": avg(newest[:10]), "last5": avg(newest[:5]), "pre": avg(pre)},
        "log": [{"d": l["date"][:10], "opp": l.get("opp", ""), "v": stat_of(l, market), "min": round(l.get("min") or 0),
                 "pre": l.get("type") == 1, "team": l.get("team", "")} for l in newest[:10]],
        "track": round(100 * track, 1), "match": match, "rank": rank, "clubs": clubs,
        "opp36": round(opp36, 2), "lg36": round(lg36, 2),
        "price": price, "price_src": price_src, "implied": round(implied, 1) if implied is not None else None,
        "edge": edge, "parts": score_parts, "score": score, "band": band, "band_label": band_label,
        "small": small, "new_team": new_team, "last_team": reg_last[-1]["team"] if reg_last else "",
        "doubt_note": doubt or "", "season_games": len(reg_last), "pre_games": len(pre),
        "book_mid": book_mid,
    }
    # DraftKings' ladder centered far from our projection: usually a role the
    # book has already moved (Edgecombe 10/20, with LeBron and Brown arriving)
    mean_ = row["mean"]
    if book_mid and book_mid >= 2 and not 0.74 <= mean_ / book_mid <= 1.35:
        row["book_gap"] = "less" if mean_ > book_mid else "more"
    row["tags"] = tags(row)
    row["why"] = why(row)
    return row


def book_center(ladder: dict | None) -> float | None:
    """Where DraftKings' "N+" ladder crosses even money: the count the book centers on."""
    if not ladder:
        return None
    pts = sorted((int(k), dk_props.implied(v)) for k, v in ladder.items())
    for (n0, p0), (n1, p1) in zip(pts, pts[1:]):
        if p0 >= 0.5 >= p1:
            return round(n0 + (p0 - 0.5) / (p0 - p1) * (n1 - n0) - 0.5, 1) if p0 != p1 else n0 - 0.5
    return None


def tags(r: dict) -> list[str]:
    t = []
    if r["match"] >= 70:
        t.append("mat")
    s_h, s_n = r["hits"]["season"]
    t10, n10 = r["hits"]["last10"]
    if (s_n >= 20 and s_h / s_n >= 0.7) or (n10 >= 8 and t10 / n10 >= 0.8):
        t.append("track")
    if r["minutes"] >= 32:
        t.append("mins")
    h5, n5 = r["hits"]["last5"]
    if n5 >= 4 and h5 >= n5 - 1 and h5 >= 3:
        t.append("hot")
    return t


def plural(n: int | float, word: str) -> str:
    return f"{n:g} {word}" if n == 1 else f"{n:g} {word}s" if not word.endswith("s") else f"{n:g} {word}"


def market_need(r: dict) -> str:
    """'2+ steals', '1+ block'."""
    word = r["word"]
    if r["need"] == 1 and word.endswith("s") and "+" not in word:
        word = word[:-1]
    return f"{r['need']}+ {word}"


def why(r: dict) -> str:
    bits = [f"Projected {r['mean']:.1f} {r['word']} on {r['minutes']:.0f} minutes"
            f" ({r['chance']:.0f}% to reach {market_need(r)})."]
    s_h, s_n = r["hits"]["season"]
    if s_n:
        bits.append(f"Reached it in {s_h} of {s_n} games last season" +
                    (f" and {r['hits']['last5'][0]} of his last {r['hits']['last5'][1]}." if r["hits"]["last5"][1] else "."))
    elif r["hits"]["pre"][1]:
        bits.append(f"Reached it in {r['hits']['pre'][0]} of {r['hits']['pre'][1]} preseason games.")
    if r["rank"] and r["match"] >= 70:
        bits.append(f"{r['opp']} gave up {nth(r['rank'], 'most')} {r['word']} to {POS_WORD.get(r['pos'], 'his position')} last season.")
    elif r["rank"] and r["match"] <= 30:
        bits.append(f"{r['opp']} gave up {nth(r['clubs'] - r['rank'] + 1, 'fewest')} {r['word']} to {POS_WORD.get(r['pos'], 'his position')} last season.")
    if r["new_team"]:
        bits.append(f"First regular-season game with {r['team']} after last season with {r['last_team']}.")
    if r.get("book_gap"):
        bits.append(f"DraftKings sees {'a smaller' if r['book_gap'] == 'less' else 'a bigger'} night: its ladder centers "
                    f"on about {r['book_mid']:g} {r['word']}, where we have {r['mean']:.1f}.")
    return " ".join(bits)


def nth(n: int, word: str) -> str:
    """'the most', 'the 4th-most'."""
    return f"the {word}" if n == 1 else f"the {ordinal(n)}-{word}"


def ordinal(n: int) -> str:
    return f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def reasons(r: dict) -> list[dict]:
    """The five parts of the rating, each with the numbers behind it."""
    def frac(h):
        return f"{h[0]}/{h[1]}" if h[1] else "—"
    s = r["hits"]
    return [
        {"part": "chance", "label": "Model chance",
         "text": f"{r['chance']:.0f}% to reach {market_need(r)}: {r['mean']:.2f} projected on {r['minutes']:.0f} minutes "
                 f"({r['min_src']}), {r['per36']:.2f} per 36"},
        {"part": "form", "label": "Track record",
         "text": f"Last season {frac(s['season'])} · last 10 {frac(s['last10'])} · last 5 {frac(s['last5'])}"
                 + (f" · preseason {frac(s['pre'])}" if s["pre"][1] else "")},
        {"part": "matchup", "label": "Matchup",
         "text": (f"{r['opp']} allowed {r['opp36']:.2f} {r['word']} per 36 to {POS_WORD.get(r['pos'], r['pos'])} last season "
                  f"({ordinal(r['rank'])} of {r['clubs']}; league {r['lg36']:.2f})") if r["rank"] else "No matchup data"},
        {"part": "role", "label": "Role & minutes",
         "text": f"{r['minutes']:.0f} projected minutes" + (" · expected starter" if r["starting"] else
                                                          " · off the bench" if r["starters_known"] else "")
                 + (f" · {r['doubt_note']}" if r["doubt_note"] else "")},
        {"part": "price", "label": "Price check",
         "text": (f"DraftKings {fmt_price(r['price'])} ({r['price_src']}) asks for {r['implied']:.0f}%; we have "
                  f"{r['chance']:.0f}% ({'+' if r['edge'] >= 0 else ''}{r['edge']:.1f})") if r["price"] is not None
                 else "No DraftKings price at this line -- scored as neutral"},
    ]


def fmt_price(p: int | None) -> str:
    return "" if p is None else f"+{p}" if p > 0 else str(p)


# ── first basket ───────────────────────────────────────────────────────────────

def jumper(side: dict, lineup: dict) -> dict | None:
    """Tonight's jumper: the projected starter who has jumped most often."""
    starters = set(lineup["starters"].get(side["abbr"]) or [])
    best = None
    for p in side.get("players") or []:
        if starters and norm(p["name"]) not in starters:
            continue
        rec = first_basket.player_openings(p)
        if rec["jumps"] and (best is None or rec["jumps"] > best[1]["jumps"]):
            best = (p, rec)
    return {"name": best[0]["name"], "id": best[0]["id"], **best[1]} if best else None


def tip_chance(a: dict | None, b: dict | None) -> float:
    def rate(j):
        return (j["jump_won"] + 3) / (j["jumps"] + 6) if j else 0.5
    pa, pb = rate(a), rate(b)
    return pa * (1 - pb) / (pa * (1 - pb) + pb * (1 - pa))


def first_basket_cards(date: str, picks: list[tuple[str, str]], slate: dict, lineup: dict, prices: dict) -> list[dict]:
    cards = []
    for name, team in picks:
        found = None
        for g in slate.get("games") or []:
            for k, other in (("away", "home"), ("home", "away")):
                side = g["sides"][k]
                if side["abbr"] != team:
                    continue
                for p in side.get("players") or []:
                    if norm(p["name"]) == norm(name):
                        found = (g, side, g["sides"][other], p)
        if not found:
            print(f"[prop_shop] WARN first-basket pick {name} ({team}) is not on tonight's slate -- left off")
            continue
        g, side, opp_side, p = found
        rec = first_basket.player_openings(p)
        ours, theirs = jumper(side, lineup), jumper(opp_side, lineup)
        p_tip = tip_chance(ours, theirs)
        p_first = p_tip * TIP_EDGE + (1 - p_tip) * (1 - TIP_EDGE)
        # his share of his side's first basket: his own record as a starter, shrunk
        # toward an even fifth of the starting five
        share = (rec["his_team_first_fg"] + 4 * 0.2) / (rec["starts"] + 4)
        starters = lineup["starters"].get(team)
        starting = not starters or norm(p["name"]) in starters
        chance = p_first * share if starting else p_first * share * 0.1
        dk = (((prices.get("games") or {}).get(g["id"]) or {}).get("players") or {}).get(p["id"]) or {}
        price = dk.get("first_basket")
        implied = 100 * dk_props.implied(price) if price is not None else None
        cards.append({
            "name": p["name"], "pid": p["id"], "team": team, "opp": opp_side["abbr"], "game": g["id"],
            "kick": g["date"], "headshot": p.get("headshot", ""), "starting": starting,
            "rec": rec, "jumper": ours, "opp_jumper": theirs, "p_tip": round(100 * p_tip, 1),
            "p_first": round(100 * p_first, 1), "share": round(100 * share, 1),
            "chance": round(100 * chance, 1), "chance_if_starts": round(100 * p_first * share, 1),
            "price": price, "implied": round(implied, 1) if implied is not None else None,
            "edge": round(100 * chance - implied, 1) if implied is not None else None,
            "team_first_fg_price": dk.get("team_first_fg"),
        })
    return cards


# ── the sheet ──────────────────────────────────────────────────────────────────

def build(date: str) -> dict:
    slate = json.loads((SLATES / f"nba-research-{date}.json").read_text(encoding="utf-8"))
    season, fit, lineup, prices = load_season(), pm.load_fit(), load_lineup(date), load_prices(date)
    plays = load_list(date)
    index = {}
    for g in slate.get("games") or []:
        for k, other in (("away", "home"), ("home", "away")):
            side = g["sides"][k]
            for p in side.get("players") or []:
                index.setdefault(norm(p["name"]), []).append((g, side, g["sides"][other], p))

    rows, scratched, unmatched = [], [], []
    for play in plays:
        hits_ = index.get(norm(play["name"])) or []
        if not hits_:
            unmatched.append(play)
            print(f"[prop_shop] WARN {play['name']} is not on tonight's slate -- left off")
            continue
        g, side, opp_side, p = hits_[0]
        out_note = lineup["out"].get((norm(p["name"]), side["abbr"]))
        if out_note is not None or (p.get("injury") or "").lower() == "out":
            scratched.append({"name": p["name"], "team": side["abbr"], "line": play["line"], "side": play["side"],
                              "market": play["market"], "label": pm.LABELS[play["market"]],
                              "icon": ICON[play["market"]],
                              "note": out_note or p.get("injury_note") or "Out"})
            continue
        rows.append(rate_prop(play, p, side, opp_side, g, season, fit, lineup, prices))

    by_id = {r["id"]: r for r in rows}
    ranked = sorted(rows, key=lambda r: -r["score"])
    top = [r["id"] for r in ranked if not r["small"]][:5]
    for pid in top:
        by_id[pid]["tags"] = ["fav"] + by_id[pid]["tags"]

    # Best value: plus money (the owner's rule for every value section), our chance
    # over the price's by VALUE_EDGE or more, in a matchup that isn't fighting back.
    def ok(r):
        return (r["price"] is not None and r["price"] > 0 and r["match"] >= MATCHUP_FLOOR
                and not r["doubt_note"] and not r["small"] and not r.get("book_gap"))
    valued = sorted((r for r in rows if ok(r) and r["edge"] >= VALUE_EDGE),
                    key=lambda r: -(r["edge"] * r["match"] / 100))
    for r in valued:
        r["tags"].append("val")
    close = sorted((r for r in rows if ok(r) and 0 < r["edge"] < VALUE_EDGE), key=lambda r: -r["edge"])
    walled = sorted((r for r in rows if r["price"] is not None and r["price"] > 0 and r["edge"] >= VALUE_EDGE
                     and r["id"] not in {v["id"] for v in valued}), key=lambda r: -r["edge"])
    value = [r["id"] for r in valued[:5]]
    value_close = [r["id"] for r in close[:max(0, 5 - len(value))]]

    for r in rows:
        r["reasons"] = reasons(r)

    games = []
    for g in slate.get("games") or []:
        sides = {}
        for k in ("away", "home"):
            abbr = g["sides"][k]["abbr"]
            sides[abbr] = [r["id"] for r in sorted((r for r in rows if r["game"] == g["id"] and r["team"] == abbr),
                                                    key=lambda r: -r["score"])]
        odds = g.get("odds") or {}
        games.append({"id": g["id"], "away": g["sides"]["away"]["abbr"], "home": g["sides"]["home"]["abbr"],
                      "away_name": g["sides"]["away"].get("name", ""), "home_name": g["sides"]["home"].get("name", ""),
                      "away_logo": g["sides"]["away"].get("logo", ""), "home_logo": g["sides"]["home"].get("logo", ""),
                      "kick": g["date"], "venue": g.get("venue", ""), "total": odds.get("overUnder"),
                      "spread": odds.get("details", ""), "sides": sides})

    fb = first_basket_cards(date, load_first_basket(date), slate, lineup, prices)
    opening = all(g.get("type") == 2 for g in slate.get("games") or []) and not any(
        l.get("type") == 2 and l.get("season") == SEASON
        for g in slate.get("games") or [] for s in g["sides"].values() for p in s["players"] for l in p.get("logs") or [])
    check = {m: (json.loads(pm.FIT.read_text(encoding="utf-8")).get("check") or {}).get(m)
             for m in {r["market"] for r in rows}} if pm.FIT.exists() else {}
    return {
        "date": date, "season": "2026-27", "stats_season": LAST,
        "built": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "opening_night": opening, "games": games, "by_id": by_id, "top5": top,
        "value": value, "value_close": value_close, "value_count": len(valued), "value_edge": VALUE_EDGE,
        "value_match_floor": MATCHUP_FLOOR, "value_walled": [r["id"] for r in walled[:4]], "first_basket": fb, "scratched": scratched,
        "unmatched": [u["name"] for u in unmatched], "weights": WEIGHTS,
        "prices_from": "DraftKings via ESPN" if prices else "", "prices_captured": prices.get("captured", ""),
        "fit": {"label": json.loads(pm.FIT.read_text(encoding="utf-8")).get("label") if pm.FIT.exists() else "",
                "test_rows": json.loads(pm.FIT.read_text(encoding="utf-8")).get("test_rows") if pm.FIT.exists() else 0,
                "check": check},
    }


def render(sheet: dict, root: str) -> str:
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("/*__SHEET__*/null", json.dumps(dict(sheet, root=root), ensure_ascii=False, separators=(",", ":")))
    return html.replace("__ROOT__", root).replace("__DATE__", sheet["date"])


_BUILT = re.compile(r'"built":"[^"]*"')


def write_if_changed(path: Path, text: str) -> bool:
    if path.exists() and _BUILT.sub('"built":""', path.read_text(encoding="utf-8")) == _BUILT.sub('"built":""', text):
        return False
    path.write_text(text, encoding="utf-8")
    return True


def publish(sheet: dict) -> None:
    date = sheet["date"]
    if date in prop_grade.graded_dates():
        # the record was graded against this archive; a rebuild would change the sheet under it
        raise SystemExit(f"[prop_shop] {date} is already graded in {prop_grade.RECORD.name}: its archive is the "
                         "record and is not rebuilt")
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    write_if_changed(ARCHIVE / f"{date}.html", render(sheet, "../"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"version": 1, "sheets": []}
    entries = {e["key"]: e for e in manifest.get("sheets", [])}
    entries[date] = {"key": date, "date": date}
    ordered = sorted(entries.values(), key=lambda e: e["date"], reverse=True)
    today = os.environ.get("NBA_TODAY") or datetime.now().date().isoformat()
    latest = next((e for e in ordered if e["date"] <= today), ordered[0])
    for e in ordered:
        pretty = datetime.strptime(e["date"], "%Y-%m-%d").strftime("%b %d").replace(" 0", " ")
        e["label"], e["href"] = ((f"{pretty} — tonight", "prop-shop.html") if e is latest
                                 else (pretty, f"prop-shop-archive/{e['date']}.html"))
    body = json.dumps({"version": 1, "sheets": ordered}, indent=2, ensure_ascii=False) + "\n"
    if not MANIFEST.exists() or MANIFEST.read_text(encoding="utf-8") != body:
        MANIFEST.write_text(body, encoding="utf-8")
    if latest["key"] == date:
        write_if_changed(NBA_DIR / "prop-shop.html", render(sheet, ""))
        print(f"[prop_shop] {date} is tonight's shop: nba-research/prop-shop.html")
    # the old shell's ledger file, kept in step for anything still reading it
    ledger = {"title": "WorstPickz Prop Shop", "subtitle": "Goblin’s Ledger", "date": date, "updated": sheet["built"],
              "picks": [{"player": r["name"], "player_id": r["pid"], "game_id": r["game"], "market": r["market"],
                         "side": r["side"], "line": r["line"], "matchup": f"{r['team']} vs {r['opp']}",
                         "kickoff": r["kick"], "odds": fmt_price(r["price"]) or None, "book": "DraftKings" if r["price"] else None,
                         "note": r["why"], "result": "pending", "score": r["score"]}
                        for r in sorted(sheet["by_id"].values(), key=lambda r: -r["score"])]}
    (SLATES / "nba-prop-ledger.json").write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


_SHEET = re.compile(r"var SHEET = (\{.*?\});\n", re.S)


def embedded(path: Path) -> dict:
    """The sheet a published page carries, as it was published."""
    m = _SHEET.search(path.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit(f"[prop_shop] no SHEET in {path.relative_to(ROOT)}")
    return json.loads(m.group(1))


def rerender(date: str) -> None:
    """A new template on a night already published: layout only. The page is
    re-rendered from the SHEET it carries -- nothing is re-projected, re-priced or
    re-rated -- and the write is refused if a single field would change. Safe on a
    graded night for the same reason: the record still matches the page."""
    targets = [(ARCHIVE / f"{date}.html", "../")]
    current = NBA_DIR / "prop-shop.html"
    if current.exists() and embedded(current).get("date") == date:
        targets.append((current, ""))
    for path, root in targets:
        before = embedded(path)
        html = render({k: v for k, v in before.items() if k != "root"}, root)
        after = json.loads(_SHEET.search(html).group(1))
        if after != before:
            raise SystemExit(f"[prop_shop] re-render would change {path.name}'s data -- refused")
        changed = write_if_changed(path, html)
        print(f"[prop_shop] {'re-rendered' if changed else 'unchanged:'} {path.relative_to(ROOT)} (data identical)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the WorstPickz NBA Prop Shop")
    ap.add_argument("--date", required=True)
    ap.add_argument("--rerender", action="store_true",
                    help="new layout for a published night, from the data it already carries")
    args = ap.parse_args()
    if args.rerender:
        rerender(args.date)
        return
    sheet = build(args.date)
    rows = sorted(sheet["by_id"].values(), key=lambda r: -r["score"])
    for r in rows:
        print(f"  {r['score']:5.1f} {r['band_label']:8s} {r['name']:24s} {r['side']} {r['line']:g} {r['code']:4s} "
              f"chance {r['chance']:5.1f}%  proj {r['mean']:5.2f}  min {r['minutes']:4.1f}  "
              f"DK {fmt_price(r['price']) or '—':>5s} edge {r['edge'] if r['edge'] is not None else '—'}  "
              f"match {r['match']:3d}  {' '.join(r['tags'])}{'  SMALL' if r['small'] else ''}"
              f"{'  DOUBT ' + r['doubt_note'] if r['doubt_note'] else ''}")
    for s in sheet["scratched"]:
        print(f"[prop_shop] off the shelf: {s['name']} ({s['team']}) {s['side']} {s['line']:g} {s['label']} -- {s['note']}")
    print("[prop_shop] top 5: " + ", ".join(f"{sheet['by_id'][i]['name']} {sheet['by_id'][i]['code']}" for i in sheet["top5"]))
    print("[prop_shop] value: " + ", ".join(f"{sheet['by_id'][i]['name']} {sheet['by_id'][i]['code']} (+{sheet['by_id'][i]['edge']})"
                                          for i in sheet["value"] + sheet["value_close"]))
    for c in sheet["first_basket"]:
        print(f"[prop_shop] first basket {c['name']} ({c['team']}): DK {fmt_price(c['price'])} ({c['implied']}%), "
              f"ours {c['chance']}% (tip {c['p_tip']}%, side first {c['p_first']}%, share {c['share']}%)"
              f"{'' if c['starting'] else ' -- PROJECTED BENCH'}; rec {c['rec']}")
    if TEMPLATE.exists():
        publish(sheet)
    else:
        print("[prop_shop] no template yet -- built the data only")


if __name__ == "__main__":
    main()
