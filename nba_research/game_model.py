"""Our own number for every NBA game: projected score, spread, total and win chance.

    python -m nba_research.game_model --fit                 # fit and check it on 2025-26
    python -m nba_research.game_model --date 2026-10-21     # tonight's games

Built from the players up, so a trade or an injury moves it the night it happens:

  1. Each team's rotation tonight -- projected minutes from prop_model (last season,
     the preseason, the expected starters and who is out), scaled so they add up to
     240 -- times each player's points per minute (his last season and preseason,
     shrunk toward his position) is the team's raw scoring.
  2. A fitted line turns that into points: the opponent's defense (points it allowed
     per 100 possessions against the league), both clubs' pace and home court.
     The coefficients were fitted on 2025-26 through January and checked on
     February-April games the fit never saw (--fit prints that check, and how far
     DraftKings' closing spread and total missed on the same games).
  3. The spread is the projected margin, the total the projected sum. The chance a
     side wins or covers, or the game goes over, comes from how far real games fell
     from the projection (a normal with the fitted spread of misses).

Writes preview/data/nba-game-model-<date>.json, read by the Lines tab (wp-lines.js).
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from nba_research import prop_model as pm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "preview" / "data"
FIT = HERE / "game_model_fit.json"
SEASON = 2027
TRAIN_END = "2026-02-01"
DECAY = 0.95          # the props fit's choice for rates
MIN_DECAY = 0.85
SHRINK_PTS = 30.0     # minutes of position-average scoring mixed into a rate
TURNOVER = 0.5        # last season's defense and pace, half-trusted in a new season
ROTATION = 10         # players who share tonight's 240 minutes


def phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def american(p: float) -> int:
    p = min(max(p, 0.01), 0.99)
    return round(-100 * p / (1 - p)) if p >= 0.5 else round(100 * (1 - p) / p)


def implied(a: float) -> float:
    return 100 / (a + 100) if a > 0 else -a / (-a + 100)


# ── the fit: replay 2025-26 day by day ──────────────────────────────────────────

def _features(raw: float, opp_def: float, pace: float, home: int) -> list[float]:
    """raw scoring, raw x (opponent's defense - 1), raw x (pace - 1), home."""
    return [1.0, raw, raw * (opp_def - 1.0), raw * (pace - 1.0), float(home)]


def _ols(X: list[list[float]], y: list[float]) -> list[float]:
    n = len(X[0])
    A = [[sum(r[i] * r[j] for r in X) for j in range(n)] for i in range(n)]
    b = [sum(r[i] * t for r, t in zip(X, y)) for i in range(n)]
    for i in range(n):  # Gauss-Jordan
        piv = max(range(i, n), key=lambda k: abs(A[k][i]))
        A[i], A[piv], b[i], b[piv] = A[piv], A[i], b[piv], b[i]
        for k in range(n):
            if k != i and A[i][i]:
                f = A[k][i] / A[i][i]
                A[k] = [a - f * c for a, c in zip(A[k], A[i])]
                b[k] -= f * b[i]
    return [b[i] / A[i][i] for i in range(n)]


def replay(games: list[dict]) -> list[dict]:
    """One row per game: both sides' features as the model knew them that morning."""
    by_day = defaultdict(list)
    for tg in games:
        by_day[tg["date"][:10]].append(tg)
    p_pts: dict = defaultdict(float)     # decayed points and minutes per player
    p_min: dict = defaultdict(float)
    p_hist: dict = defaultdict(list)
    pos_pts: dict = defaultdict(lambda: [0.0, 0.0])  # league points and minutes by position
    t_for: dict = defaultdict(lambda: [0.0, 0.0])    # team points scored, possessions
    t_against: dict = defaultdict(lambda: [0.0, 0.0])
    t_games: dict = defaultdict(int)
    rows = []
    for day in sorted(by_day):
        lg_poss = sum(v[1] for v in t_for.values()) / max(1, sum(t_games.values()))
        lg_ppp = sum(v[0] for v in t_for.values()) / max(1.0, sum(v[1] for v in t_for.values()))
        by_event = defaultdict(dict)
        for tg in by_day[day]:
            by_event[tg["event"]]["home" if tg["home"] else "away"] = tg
        for ev, sides in by_event.items():
            if set(sides) != {"home", "away"} or min(t_games[sides["home"]["team"]], t_games[sides["away"]["team"]]) < 8:
                continue
            feat = {}
            for k, o in (("home", "away"), ("away", "home")):
                tg, ot = sides[k], sides[o]
                mins, rates = [], []
                for p in tg["players"]:
                    h = p_hist[p["id"]][-15:][::-1]
                    if not h:
                        continue
                    w = sum(MIN_DECAY ** i for i in range(len(h)))
                    m = sum(MIN_DECAY ** i * x for i, x in enumerate(h)) / w
                    lg = pos_pts[p["pos"]][0] / pos_pts[p["pos"]][1] if pos_pts[p["pos"]][1] else 0.48
                    rates.append((p_pts[p["id"]] + SHRINK_PTS * lg) / (p_min[p["id"]] + SHRINK_PTS))
                    mins.append(m)
                if sum(mins) < 150:
                    break
                scale = 240.0 / sum(mins)
                raw = sum(m * scale * r for m, r in zip(mins, rates))
                a = t_against[ot["team"]]
                opp_def = (a[0] / a[1]) / lg_ppp if a[1] and lg_ppp else 1.0
                pace_t = t_for[tg["team"]][1] / max(1, t_games[tg["team"]])
                pace_o = t_for[ot["team"]][1] / max(1, t_games[ot["team"]])
                pace = ((pace_t + pace_o) / 2) / pace_t if pace_t else 1.0
                feat[k] = {"x": _features(raw, opp_def, pace, int(k == "home")),
                           "y": sum(p["pts"] for p in tg["players"])}
            if len(feat) == 2:
                rows.append({"date": day, "event": ev, "home": feat["home"], "away": feat["away"],
                             "teams": (sides["away"]["team"], sides["home"]["team"])})
        for tg in by_day[day]:
            pts = sum(p["pts"] for p in tg["players"])
            t_for[tg["team"]][0] += pts
            t_for[tg["team"]][1] += tg.get("possessions_est") or 100.0
            t_against[tg["opp"]][0] += pts
            t_against[tg["opp"]][1] += tg.get("possessions_est") or 100.0
            t_games[tg["team"]] += 1
            for p in tg["players"]:
                p_pts[p["id"]] = p_pts[p["id"]] * DECAY + p["pts"]
                p_min[p["id"]] = p_min[p["id"]] * DECAY + p["min"]
                p_hist[p["id"]].append(p["min"])
                pos_pts[p["pos"]][0] += p["pts"]
                pos_pts[p["pos"]][1] += p["min"]
    return rows


def fit() -> None:
    games = sorted(json.loads((HERE / "cache" / "backtest-2026.json").read_text(encoding="utf-8")), key=lambda g: g["date"])
    rows = replay(games)
    train = [r for r in rows if r["date"] < TRAIN_END]
    test = [r for r in rows if r["date"] >= TRAIN_END]
    X = [r[s]["x"] for r in train for s in ("home", "away")]
    y = [r[s]["y"] for r in train for s in ("home", "away")]
    c = _ols(X, y)
    pred = lambda f: sum(a * b for a, b in zip(c, f))

    def check(rs):
        m_err = [(pred(r["home"]["x"]) - pred(r["away"]["x"])) - (r["home"]["y"] - r["away"]["y"]) for r in rs]
        t_err = [(pred(r["home"]["x"]) + pred(r["away"]["x"])) - (r["home"]["y"] + r["away"]["y"]) for r in rs]
        sd_m = math.sqrt(sum(e * e for e in m_err) / len(m_err))
        sd_t = math.sqrt(sum(e * e for e in t_err) / len(t_err))
        wins = sum(1 for r in rs if (pred(r["home"]["x"]) > pred(r["away"]["x"])) == (r["home"]["y"] > r["away"]["y"]))
        return {"games": len(rs), "margin_mae": round(sum(abs(e) for e in m_err) / len(m_err), 2), "margin_sd": round(sd_m, 2),
                "total_mae": round(sum(abs(e) for e in t_err) / len(t_err), 2), "total_sd": round(sd_t, 2),
                "picked_winner": round(100 * wins / len(rs), 1)}
    held = check(test)
    # DraftKings' closing spread and total on the same held-out games, where the results log has them
    book = None
    res = DATA / "results-nba.json"
    if res.exists():
        close = {str(g["id"]): g for g in json.loads(res.read_text(encoding="utf-8")).get("games") or []
                 if (g.get("close") or {}).get("spread_home") is not None}
        both = [r for r in test if r["event"] in close]
        if both:
            # spread_home +18.5: the home side gets 18.5, so the book has the home margin at -18.5
            bm = [abs(-close[r["event"]]["close"]["spread_home"] - (r["home"]["y"] - r["away"]["y"])) for r in both]
            bt = [abs(close[r["event"]]["close"]["total"] - (r["home"]["y"] + r["away"]["y"])) for r in both
                  if close[r["event"]]["close"].get("total")]
            ours = check(both)
            book = {"games": len(both), "book_margin_mae": round(sum(bm) / len(bm), 2),
                    "book_total_mae": round(sum(bt) / len(bt), 2) if bt else None,
                    "our_margin_mae": ours["margin_mae"], "our_total_mae": ours["total_mae"]}
    # team pace and defense, the whole season, for tonight's games
    t_for, t_against, t_games = defaultdict(lambda: [0.0, 0.0]), defaultdict(lambda: [0.0, 0.0]), defaultdict(int)
    for tg in games:
        pts = sum(p["pts"] for p in tg["players"])
        t_for[tg["team"]][0] += pts; t_for[tg["team"]][1] += tg.get("possessions_est") or 100.0
        t_against[tg["opp"]][0] += pts; t_against[tg["opp"]][1] += tg.get("possessions_est") or 100.0
        t_games[tg["team"]] += 1
    lg_ppp = sum(v[0] for v in t_for.values()) / sum(v[1] for v in t_for.values())
    teams = {t: {"pace": round(t_for[t][1] / t_games[t], 2), "def": round((t_against[t][0] / t_against[t][1]) / lg_ppp, 4),
                 "off": round((t_for[t][0] / t_for[t][1]) / lg_ppp, 4), "ortg": round(100 * t_for[t][0] / t_for[t][1], 1),
                 "drtg": round(100 * t_against[t][0] / t_against[t][1], 1), "games": t_games[t]} for t in t_games}
    for key, best_high in (("pace", True), ("ortg", True), ("drtg", False)):
        order = sorted(teams, key=lambda x: -teams[x][key] if best_high else teams[x][key])
        for i, x in enumerate(order):
            teams[x][key + "_rank"] = i + 1
    # how far real games fall from DraftKings' closing spread: the yardstick for what a spread
    # says about winning, and the honest record of our number against it
    book_sd, record = None, None
    if res.exists():
        logged = [g for g in json.loads(res.read_text(encoding="utf-8")).get("games") or []
                  if (g.get("close") or {}).get("spread_home") is not None and g.get("type") in (2, 3, 5)]
        if logged:
            book_sd = round(math.sqrt(sum(((g["hs"] - g["as"]) + g["close"]["spread_home"]) ** 2 for g in logged) / len(logged)), 2)
    if book:
        w = l = tw = tl = 0
        for r in [r for r in test if r["event"] in close]:
            cl = close[r["event"]]["close"]
            ours, bk = pred(r["home"]["x"]) - pred(r["away"]["x"]), -cl["spread_home"]
            res_ = ((r["home"]["y"] - r["away"]["y"]) - bk) * (1 if ours > bk else -1)
            w += res_ > 0; l += res_ < 0
            if cl.get("total"):
                ot = pred(r["home"]["x"]) + pred(r["away"]["x"])
                rt = ((r["home"]["y"] + r["away"]["y"]) - cl["total"]) * (1 if ot > cl["total"] else -1)
                tw += rt > 0; tl += rt < 0
        record = {"spread": [w, l], "total": [tw, tl]}
    # the misses used for chances: the held-out spread, which is the honest one
    out = {"fitted": datetime.now(timezone.utc).isoformat(timespec="minutes"), "season": "2025-26",
           "train_games": len(train), "coef": [round(v, 5) for v in c], "margin_sd": held["margin_sd"],
           "total_sd": held["total_sd"], "check": held, "vs_book": book, "book_margin_sd": book_sd,
           "record_vs_close": record, "teams": teams,
           "league_pace": round(sum(v["pace"] for v in teams.values()) / len(teams), 2)}
    FIT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"[game_model] fitted on {len(train)} games, checked on {len(test)}: {held}")
    if book:
        print(f"[game_model] on {book['games']} of those with DraftKings' close: ours missed the margin by "
              f"{book['our_margin_mae']}, DK's spread by {book['book_margin_mae']}; total {book['our_total_mae']} vs {book['book_total_mae']}")


# ── tonight ─────────────────────────────────────────────────────────────────────

def side_projection(side: dict, team: str, season: dict, lineup: dict, prefit: dict) -> dict:
    from nba_research import prop_shop as ps
    starters = lineup["starters"].get(team)
    out_keys = {k for k in lineup["out"]}
    players = []
    for p in side.get("players") or []:
        if (p.get("injury") or "").lower() == "out" or (ps.norm(p["name"]), team) in out_keys:
            continue
        last = ps.season_logs(season, p["id"])
        logs = last + [l for l in p.get("logs") or [] if not (last and l.get("type") == 2 and l.get("season") == season["season"])]
        if not logs:
            continue
        reg = [l for l in logs if l.get("type") == 2 and l.get("season") == season["season"]]
        new_team = bool(reg) and sorted(reg, key=lambda l: l["date"])[-1].get("team") != team
        starting = bool(starters) and ps.norm(p["name"]) in starters
        m, _ = pm.project_minutes(logs, team, SEASON, MIN_DECAY, starting if starters else None)
        if starters and not starting and m > 26:
            m -= 0.5 * (m - 26)
        if m < 6:
            continue
        made, mins = pm.decayed(logs, SEASON, DECAY, pre_weight=1.0 if new_team else 0.4)
        lg = (season["league"].get(p["pos"]) or {}).get("pts", 0.48)
        rate = (made["pts"] + SHRINK_PTS * lg) / (mins + SHRINK_PTS)
        players.append({"name": p["name"], "min": m, "rate": rate, "start": starting})
    # a rotation is about ten deep: the eleventh man's exhibition minutes are not tonight's
    players = sorted(players, key=lambda x: -x["min"])[:ROTATION]
    total_min = sum(x["min"] for x in players)
    scale = 240.0 / total_min if total_min else 1.0
    for x in players:
        x["min"] *= scale
        x["pts"] = x["min"] * x["rate"]
    players.sort(key=lambda x: -x["pts"])
    return {"raw": sum(x["pts"] for x in players), "players": players, "scale": scale}


def tonight(date: str) -> Path:
    from nba_research import prop_shop as ps
    fitd = json.loads(FIT.read_text(encoding="utf-8"))
    c, teams, lg_pace = fitd["coef"], fitd["teams"], fitd["league_pace"]
    slate = json.loads((DATA / f"nba-research-{date}.json").read_text(encoding="utf-8"))
    season, lineup = ps.load_season(), ps.load_lineup(date)
    lines_file = DATA / "lines-nba.json"
    lines = (json.loads(lines_file.read_text(encoding="utf-8")).get("games") or {}) if lines_file.exists() else {}
    out = {}
    for g in slate.get("games") or []:
        sides = g["sides"]
        proj = {k: side_projection(sides[k], sides[k]["abbr"], season, lineup, fitd) for k in ("away", "home")}
        pts = {}
        for k, o in (("home", "away"), ("away", "home")):
            t, ot = sides[k]["abbr"], sides[o]["abbr"]
            d = teams.get(ot, {}).get("def", 1.0)
            opp_def = 1 + TURNOVER * (d - 1)
            pt, po = teams.get(t, {}).get("pace", lg_pace), teams.get(ot, {}).get("pace", lg_pace)
            pace = 1 + TURNOVER * (((pt + po) / 2) / pt - 1)
            pts[k] = sum(a * b for a, b in zip(c, _features(proj[k]["raw"], opp_def, pace, int(k == "home"))))
        margin = pts["home"] - pts["away"]
        total = pts["home"] + pts["away"]
        p_home = phi(margin / fitd["margin_sd"])
        row = {"away": sides["away"]["abbr"], "home": sides["home"]["abbr"], "kick": g["date"],
               "proj": {"away": round(pts["away"], 1), "home": round(pts["home"], 1)},
               "margin": round(margin, 1), "total": round(total, 1),
               "win": {"home": round(100 * p_home, 1), "away": round(100 * (1 - p_home), 1)},
               "fair_ml": {"home": american(p_home), "away": american(1 - p_home)},
               "spread": {"home": round(-margin * 2) / 2, "away": round(margin * 2) / 2},
               "top": {k: [{"name": x["name"], "pts": round(x["pts"], 1), "min": round(x["min"])} for x in proj[k]["players"][:3]]
                       for k in ("away", "home")},
               "out": {k: sorted({p["name"] for p in sides[k].get("players") or [] if (p.get("injury") or "").lower() == "out"
                                  or (ps.norm(p["name"]), sides[k]["abbr"]) in lineup["out"]}) for k in ("away", "home")}}
        # against the book: DraftKings first, else the consensus best
        book = lines.get(str(g["id"])) or {}
        dk = next((b for b in book.get("books") or [] if b.get("book") == "DraftKings"), None) or {}
        best = book.get("best") or {}
        sp = (dk.get("spread") or {}).get("home") or ([best["spread_home"]["line"], best["spread_home"]["price"]] if best.get("spread_home") else None)
        tot = dk.get("total") or best.get("total")
        ml = dk.get("ml") or ({"home": (best.get("ml_home") or {}).get("price"), "away": (best.get("ml_away") or {}).get("price")}
                               if best.get("ml_home") else None)
        vs = {"book": "DraftKings" if dk else (book and "best price")}
        if sp:
            book_margin = -float(sp[0])        # home -2.5 -> the book has home by 2.5
            cover = phi((margin - book_margin) / fitd["margin_sd"])
            vs["spread"] = {"home_line": float(sp[0]), "price": sp[1], "edge": round(margin - book_margin, 1),
                            "home_covers": round(100 * cover, 1)}
        if tot and tot.get("line") is not None:
            over = phi((total - float(tot["line"])) / fitd["total_sd"])
            vs["total"] = {"line": float(tot["line"]), "over_price": tot.get("over"), "under_price": tot.get("under"),
                           "edge": round(total - float(tot["line"]), 1), "over": round(100 * over, 1)}
        if ml and ml.get("home") is not None and ml.get("away") is not None:
            a, h = implied(ml["away"]), implied(ml["home"])
            fair_home = h / (a + h)
            vs["ml"] = {"home": ml["home"], "away": ml["away"], "book_home": round(100 * fair_home, 1),
                        "edge_home": round(100 * (p_home - fair_home), 1)}
        row["vs"] = vs
        # what DraftKings' own numbers say, with the vig out
        market = {}
        bsd = fitd.get("book_margin_sd") or 13.5
        if vs.get("ml"):
            market["win"] = {"home": vs["ml"]["book_home"], "away": round(100 - vs["ml"]["book_home"], 1)}
        if vs.get("spread"):
            bm = -vs["spread"]["home_line"]
            market["spread_win_home"] = round(100 * phi(bm / bsd), 1)   # the win chance a spread that size carries
            if vs.get("ml"):
                market["ml_minus_spread"] = round(vs["ml"]["book_home"] - market["spread_win_home"], 1)
            if vs.get("total"):
                tl = vs["total"]["line"]
                market["score"] = {"home": round(tl / 2 + bm / 2, 1), "away": round(tl / 2 - bm / 2, 1)}
        if vs.get("total") and vs["total"].get("over_price") and vs["total"].get("under_price"):
            o, u = implied(vs["total"]["over_price"]), implied(vs["total"]["under_price"])
            market["over"] = round(100 * o / (o + u), 1)
        row["market"] = market
        row["teams"] = {k: {key: teams.get(sides[k]["abbr"], {}).get(key) for key in
                            ("pace", "pace_rank", "ortg", "ortg_rank", "drtg", "drtg_rank")} for k in ("away", "home")}
        row["league_pace"] = lg_pace
        out[str(g["id"])] = row
    body = {"date": date, "built": datetime.now(timezone.utc).isoformat(timespec="minutes"),
            "model": {"season": fitd["season"], "margin_sd": fitd["margin_sd"], "total_sd": fitd["total_sd"],
                      "check": fitd["check"], "vs_book": fitd.get("vs_book"), "record_vs_close": fitd.get("record_vs_close"),
                      "book_margin_sd": fitd.get("book_margin_sd")},
            "games": out}
    path = DATA / f"nba-game-model-{date}.json"
    path.write_text(json.dumps(body, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--date")
    a = ap.parse_args()
    if a.fit:
        fit()
    if a.date:
        p = tonight(a.date)
        body = json.loads(p.read_text(encoding="utf-8"))
        for gid, r in body["games"].items():
            vs = r["vs"]
            print(f"  {r['away']:4s} {r['proj']['away']:6.1f} @ {r['home']:4s} {r['proj']['home']:6.1f}  "
                  f"ours {r['home']} {r['spread']['home']:+.1f} total {r['total']:.1f} win {r['win']['home']:.0f}%"
                  + (f" | DK {r['home']} {vs['spread']['home_line']:+.1f} ({vs['spread']['edge']:+.1f}, covers {vs['spread']['home_covers']:.0f}%)" if vs.get("spread") else "")
                  + (f" total {vs['total']['line']} ({vs['total']['edge']:+.1f}, over {vs['total']['over']:.0f}%)" if vs.get("total") else "")
                  + (f" ML {vs['ml']['home']:+d} ({vs['ml']['edge_home']:+.1f})" if vs.get("ml") else ""))
        print(f"[game_model] wrote {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
