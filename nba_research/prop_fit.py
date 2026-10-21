"""Fit the Prop Shop model on a finished regular season, then check it on games it never saw.

    python -m nba_research.prop_fit --season 2026      # 2025-26, from backtest's box-score cache

Every game is projected the way the shop projects tonight: from that player's
games before the date, the league's per-position rates to date, and what the
opponent had allowed to his position to date. The first part of the season
(through January) picks the two knobs -- how hard a rate shrinks toward its
position and how fast old games fade -- and fits the scatter; February on, which
the fit never saw, is the check. The report prints how often each line actually
cashed against how often the model said it would.

Writes:
  nba_research/prop_shop_fit.json            the fitted knobs, scatter and the check
  nba_research/season_rates/<YYYY-YY>.json.gz every player's games that season,
                                              each club's allowed-by-position and the league rates
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from nba_research import prop_model as pm

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
SEASON_DIR = HERE / "season_rates"
TRAIN_END = "02-01"          # month-day; the season's second year
MIN_PRIOR = 5                # games before one is projected
CHECK_LINES = {"pts": [10, 15, 20, 25], "reb": [3, 5, 7, 9], "ast": [2, 3, 5, 7], "threem": [1, 2, 3, 4],
               "stl": [1, 2], "blk": [1, 2], "stocks": [1, 2, 3], "pra": [20, 25, 30, 35]}


def season_label(season: int) -> str:
    return f"{season - 1}-{str(season)[2:]}"


def load_games(season: int) -> list[dict]:
    path = CACHE / f"backtest-{season}.json"
    if not path.exists():
        raise SystemExit(f"No box scores for {season_label(season)}. Run: python -m nba_research.backtest --season {season}")
    return sorted(json.loads(path.read_text(encoding="utf-8")), key=lambda g: g["date"])


def replay(games: list[dict], decay: float, min_decay: float) -> list[dict]:
    """One row per player-game: what the model knew that morning, and what happened."""
    by_day = defaultdict(list)
    for tg in games:
        by_day[tg["date"][:10]].append(tg)
    s_made: dict = defaultdict(lambda: {s: 0.0 for s in pm.STATS})
    s_min: dict = defaultdict(float)
    mins_hist: dict = defaultdict(list)
    n_games: dict = defaultdict(int)
    allowed: dict = defaultdict(lambda: {"min": 0.0, **{s: 0.0 for s in pm.STATS}})
    allowed_games: dict = defaultdict(int)
    league: dict = defaultdict(lambda: {"min": 0.0, **{s: 0.0 for s in pm.STATS}})
    rows = []
    for day in sorted(by_day):
        lg_rate = {pos: {s: a[s] / a["min"] for s in pm.STATS} for pos, a in league.items() if a["min"]}
        for tg in by_day[day]:
            opp = tg["opp"]
            for p in tg["players"]:
                key = p["id"]
                if n_games[key] < MIN_PRIOR or p["pos"] not in lg_rate:
                    continue
                hist = mins_hist[key][-15:][::-1]
                w = sum(min_decay ** i for i in range(len(hist)))
                m = sum(min_decay ** i * x for i, x in enumerate(hist)) / w
                a = allowed.get((opp, p["pos"]))
                lg = lg_rate[p["pos"]]
                opp_rate = {s: a[s] / a["min"] for s in pm.STATS} if a and a["min"] else None
                rows.append({
                    "date": day, "id": key, "team": tg["team"], "iso": tg["date"], "pos": p["pos"], "m": m,
                    "made": dict(s_made[key]), "mins": s_min[key], "lg": lg,
                    "opp": opp_rate, "opp_games": allowed_games[(opp, p["pos"])],
                    "y": {s: int(p.get(s) or 0) for s in pm.STATS}, "min": p["min"],
                })
        # the day's games join the record only after every one of them was projected
        for tg in by_day[day]:
            for p in tg["players"]:
                key = p["id"]
                for s in pm.STATS:
                    s_made[key][s] = s_made[key][s] * decay + (p.get(s) or 0.0)
                s_min[key] = s_min[key] * decay + p["min"]
                mins_hist[key].append(p["min"])
                n_games[key] += 1
                acc = allowed[(tg["opp"], p["pos"])]
                lgacc = league[p["pos"]]
                for s in pm.STATS:
                    acc[s] += p.get(s) or 0.0
                    lgacc[s] += p.get(s) or 0.0
                acc["min"] += p["min"]
                lgacc["min"] += p["min"]
            for pos in {p["pos"] for p in tg["players"]}:
                allowed_games[(tg["opp"], pos)] += 1
    return rows


def projections(rows: list[dict], shrink: dict) -> dict:
    """{market: [projection per row]}."""
    out = {s: [] for s in pm.MARKETS}
    for r in rows:
        rate = pm.per_minute(r["made"], r["mins"], r["lg"], shrink)
        one = {}
        for s in pm.STATS:
            ratio = pm.matchup_ratio(r["opp"], r["lg"], s, r["opp_games"])
            one[s] = r["m"] * rate[s] * ratio
        for c, parts in pm.COMBOS.items():
            one[c] = sum(one[s] for s in parts)
        for s in pm.MARKETS:
            out[s].append(one[s])
    return out


def actual(r: dict, s: str) -> int:
    return sum(r["y"][p] for p in pm.COMBOS.get(s, (s,)))


def fit_b(xs: list[float], ys: list[int]) -> list[float]:
    """Poisson-score (b0, b1) for mean = exp(b0) * proj^b1: the mean's estimating
    equation does not depend on the scatter, so this is the NB1 fit for any phi."""
    lx = [math.log(max(x, 0.02)) for x in xs]
    b = [0.0, 1.0]
    for _ in range(25):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for x, y in zip(lx, ys):
            m = math.exp(max(-12.0, min(8.0, b[0] + b[1] * x)))
            g0 += y - m
            g1 += (y - m) * x
            h00 += m
            h01 += m * x
            h11 += m * x * x
        det = h00 * h11 - h01 * h01
        if abs(det) < 1e-12:
            break
        s0 = (h11 * g0 - h01 * g1) / det
        s1 = (-h01 * g0 + h00 * g1) / det
        b = [b[0] + s0, b[1] + s1]
        if max(abs(s0), abs(s1)) < 1e-8:
            break
    return [round(b[0], 5), round(b[1], 5)]


def loglik(xs, ys, b, phi) -> float:
    return sum(pm.logpmf(y, pm.mean(b, x), phi) for x, y in zip(xs, ys))


def fit_phi(xs, ys, b) -> float:
    grid = [1.0] + [1.0 + 0.05 * i for i in range(1, 21)] + [2.0 + 0.25 * i for i in range(1, 17)]
    best = max(grid, key=lambda phi: loglik(xs, ys, b, phi))
    # a finer pass around the best
    fine = [max(1.0, best + d) for d in (-0.04, -0.02, 0.0, 0.02, 0.04)]
    return round(max(fine, key=lambda phi: loglik(xs, ys, b, phi)), 3)


def calibration(xs, ys, params, lines) -> list[dict]:
    """For each line: the average chance the model gave, how often it cashed, and the
    log loss against simply using the base rate."""
    out = []
    for k in lines:
        ps = [pm.at_least(k, pm.mean(params["b"], x), params["phi"]) for x in xs]
        hits = [1 if y >= k else 0 for y in ys]
        base = sum(hits) / len(hits)
        ll = -sum(h * math.log(max(p, 1e-6)) + (1 - h) * math.log(max(1 - p, 1e-6)) for p, h in zip(ps, hits)) / len(ps)
        ll0 = -sum(h * math.log(max(base, 1e-6)) + (1 - h) * math.log(max(1 - base, 1e-6)) for h in hits) / len(hits)
        # deciles of the model's own chance: said vs happened
        order = sorted(range(len(ps)), key=lambda i: ps[i])
        bins = []
        for q in range(5):
            idx = order[q * len(order) // 5:(q + 1) * len(order) // 5]
            if idx:
                bins.append([round(100 * sum(ps[i] for i in idx) / len(idx), 1),
                             round(100 * sum(hits[i] for i in idx) / len(idx), 1)])
        out.append({"line": f"{k}+", "said": round(100 * sum(ps) / len(ps), 1), "hit": round(100 * base, 1),
                    "logloss": round(ll, 4), "base_logloss": round(ll0, 4), "quintiles": bins})
    return out


def season_file(games: list[dict], season: int) -> dict:
    """Every player's games, each club's allowed-by-position and the league rates."""
    players: dict = {}
    allowed: dict = defaultdict(lambda: defaultdict(lambda: {"min": 0.0, "games": 0, **{s: 0.0 for s in pm.STATS}}))
    league: dict = defaultdict(lambda: {"min": 0.0, **{s: 0.0 for s in pm.STATS}})
    totals: dict = defaultdict(float)
    for tg in games:
        totals[tg["event"]] += sum(p.get("pts") or 0.0 for p in tg["players"])
        seen = set()
        for p in tg["players"]:
            row = players.setdefault(p["id"], {"name": p["name"], "pos": p["pos"], "games": []})
            row["games"].append([tg["date"], tg["team"], tg["opp"], int(bool(p.get("starter"))), p["min"]]
                                + [int(p.get(s) or 0) for s in pm.STATS])
            a = allowed[tg["opp"]][p["pos"]]
            for s in pm.STATS:
                a[s] += p.get(s) or 0.0
                league[p["pos"]][s] += p.get(s) or 0.0
            a["min"] += p["min"]
            league[p["pos"]]["min"] += p["min"]
            if p["pos"] not in seen:
                a["games"] += 1
                seen.add(p["pos"])
    return {
        "season": season, "label": season_label(season),
        "columns": ["date", "team", "opp", "starter", "min", *pm.STATS],
        "players": players,
        "allowed": {t: {pos: {k: round(v, 3) if isinstance(v, float) else v for k, v in a.items()}
                        for pos, a in by.items()} for t, by in allowed.items()},
        "league": {pos: {s: a[s] / a["min"] for s in pm.STATS} for pos, a in league.items()},
        "league_total": round(sum(totals.values()) / len(totals), 2),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--season", type=int, default=2026)
    args = ap.parse_args()
    games = load_games(args.season)
    cut = f"{args.season}-{TRAIN_END}"

    best = None
    for decay in (0.95, 0.98, 1.0):
        rows = replay(games, decay, pm.DEFAULT["min_decay"])
        train = [i for i, r in enumerate(rows) if r["date"] < cut]
        test = [i for i, r in enumerate(rows) if r["date"] >= cut]
        for mult in (0.5, 1.0, 2.0):
            shrink = {s: v * mult for s, v in pm.DEFAULT["shrink"].items()}
            proj = projections(rows, shrink)
            score = 0.0
            for s in pm.STATS:
                xs = [proj[s][i] for i in train]
                ys = [actual(rows[i], s) for i in train]
                b = fit_b(xs, ys)
                phi = fit_phi(xs, ys, b)
                xt = [proj[s][i] for i in test]
                yt = [actual(rows[i], s) for i in test]
                score += loglik(xt, yt, b, phi) / len(test)
            print(f"[prop_fit] decay {decay} shrink x{mult}: held-out log-lik {score:.4f}", flush=True)
            if best is None or score > best[0]:
                best = (score, decay, mult)

    _, decay, mult = best
    shrink = {s: v * mult for s, v in pm.DEFAULT["shrink"].items()}
    rows = replay(games, decay, pm.DEFAULT["min_decay"])
    proj = projections(rows, shrink)
    train = [i for i, r in enumerate(rows) if r["date"] < cut]
    test = [i for i, r in enumerate(rows) if r["date"] >= cut]
    params, check = {}, {}
    for s in pm.MARKETS:
        xs = [proj[s][i] for i in train]
        ys = [actual(rows[i], s) for i in train]
        b = fit_b(xs, ys)
        params[s] = {"b": b, "phi": fit_phi(xs, ys, b)}
        if s in CHECK_LINES:
            check[s] = calibration([proj[s][i] for i in test], [actual(rows[i], s) for i in test],
                                   params[s], CHECK_LINES[s])
    # the shop runs on the whole season once the check is in
    for s in pm.MARKETS:
        xs = proj[s]
        ys = [actual(r, s) for r in rows]
        b = fit_b(xs, ys)
        params[s] = {"b": b, "phi": fit_phi(xs, ys, b)}

    out = {
        "fitted": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "season": args.season, "label": season_label(args.season),
        "rows": len(rows), "train_rows": len(train), "test_rows": len(test), "test_from": cut,
        "decay": decay, "min_decay": pm.DEFAULT["min_decay"], "shrink": shrink,
        "params": params, "check": check,
    }
    pm.FIT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"[prop_fit] decay {decay}, shrink x{mult}; {len(rows)} player-games, check on {len(test)} from {cut}")
    for s, lines in check.items():
        print(f"  {s:7s} phi {params[s]['phi']:<5} b {params[s]['b']}  " + "  ".join(
            f"{c['line']} said {c['said']}% hit {c['hit']}% (ll {c['logloss']} vs {c['base_logloss']})" for c in lines))

    SEASON_DIR.mkdir(exist_ok=True)
    path = SEASON_DIR / f"{season_label(args.season)}.json.gz"
    body = json.dumps(season_file(games, args.season), separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(path, "wb", mtime=0) as fh:  # mtime 0: the same season writes the same bytes
        fh.write(body)
    print(f"[prop_fit] wrote {path.relative_to(HERE.parent)} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
