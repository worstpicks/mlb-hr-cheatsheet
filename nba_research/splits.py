"""With / without: a player's games with a teammate on the floor, and with him sitting.

    python -m nba_research.splits               # preview/data/nba-splits.json, for the research tab
    python -m nba_research.splits --backtest    # replay 2025-26 with and without the Prop Shop's teammate-out
                                                # adjustment; writes nba_research/splits_fit.json

A teammate sat a game when his club played it while he was on the club and he is
not in the box score: a DNP, an injury, a rest night. He is on a club from the day
after his last game for another club to the day before his first game for the
next one, and a player on a roster today is on that club for the season so far.
Only regular-season games count: preseason rotations are not roles.

Sources: every 2025-26 game (season_rates/2025-26.json.gz, written by prop_fit.py
from the backtest cache) and this season's regular-season games from the research
slates' logs (preview/data/nba-research-<date>.json). A slate only carries each
club's last ten games, so the research file keeps every 2026-27 game it has seen
and adds the new ones on each build.

The Prop Shop calls tonight() when a listed player's high-usage teammate is out
tonight: his minutes and per-minute rates move toward his without-that-teammate
split, shrunk by its sample and by how much of his recent record already came
without him. It only moves a projection if the 2025-26 replay says it helps
(splits_fit.json, "enabled").
"""
from __future__ import annotations

import argparse
import bisect
import gzip
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from nba_research import prop_model as pm

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "nba_research"
SLATES = ROOT / "preview" / "data"
OUT = SLATES / "nba-splits.json"
SEASON_FILE = HERE / "season_rates" / "2025-26.json.gz"
FIT = HERE / "splits_fit.json"
COLS = ("min",) + pm.STATS
CURRENT = 2027                  # 2026-27
END = "~"                       # sorts after every ISO date

# Until a replay has been run: off, with the knobs the replay starts from.
DEFAULT = {"enabled": False, "usage": 14.0, "k_min": 8.0, "k_rate": 3.0, "paired": False, "min_with": 5,
           "cap_min": 8.0, "ratio_lo": 0.75, "ratio_hi": 1.33}


def season_of(iso: str) -> int:
    """2025-10-22 -> 2026: a season is named for the year it ends."""
    return int(iso[:4]) + (1 if iso[5:7] >= "07" else 0)


def label(season: int) -> str:
    return f"{season - 1}-{str(season)[2:]}"


# ── the index ──────────────────────────────────────────────────────────────────

class Index:
    """Every regular-season game a player appeared in, who was in each box, and
    which club each player was on when."""

    def __init__(self) -> None:
        self.names: dict = {}
        self.games: dict = defaultdict(list)       # pid -> [(iso, team, season, opp, line)], line = COLS
        self.played: set = set()                   # (pid, team, iso)
        self.team_games: dict = defaultdict(dict)  # team -> {iso: opp}
        self.roster: dict = {}                     # pid -> his club today
        self.stints: dict = {}                     # pid -> [(team, season, lo, hi)], lo < iso < hi
        self.club: dict = defaultdict(set)         # (team, season) -> pids with a stint there
        self._isos: dict = {}

    def add(self, pid: str, name: str, iso: str, team: str, opp: str, line) -> None:
        if (pid, team, iso) in self.played:
            return
        self.played.add((pid, team, iso))
        self.names.setdefault(pid, name)
        self.games[pid].append((iso, team, season_of(iso), opp, tuple(float(x or 0) for x in line)))
        self.team_games[team][iso] = opp

    def finish(self) -> "Index":
        for g in self.games.values():
            g.sort()
        for pid in set(self.games) | set(self.roster):
            games = self.games.get(pid, [])
            out = []
            for season in sorted({g[2] for g in games} | ({CURRENT} if pid in self.roster else set())):
                out += stints([(g[0], g[1]) for g in games if g[2] == season], season,
                              self.roster.get(pid) if season == CURRENT else None)
            self.stints[pid] = out
            for team, season, _, _ in out:
                self.club[(team, season)].add(pid)
        self._isos = {pid: [g[0] for g in games] for pid, games in self.games.items()}
        return self

    def on(self, pid: str, team: str, season: int, iso: str) -> bool:
        return any(t == team and s == season and lo < iso < hi for t, s, lo, hi in self.stints.get(pid, ()))

    def before(self, pid: str, iso: str) -> list:
        """His games before `iso`, oldest first."""
        return self.games.get(pid, [])[:bisect.bisect_left(self._isos.get(pid, []), iso)]

    def split(self, pid: str, mate: str, before: str = END) -> tuple[list, list]:
        """(with, without): his games on a club the teammate was on, split by
        whether the teammate is in the box."""
        w, wo = [], []
        for g in self.before(pid, before):
            if self.on(mate, g[1], g[2], g[0]):
                (w if (mate, g[1], g[0]) in self.played else wo).append(g)
        return w, wo

    def usage(self, pid: str, before: str, last: int = 30) -> float | None:
        """Points a game over his last 30 games: how much of the offense he carries."""
        games = self.before(pid, before)[-last:]
        return sum(g[4][1] for g in games) / len(games) if len(games) >= 5 else None


def stints(apps: list[tuple[str, str]], season: int, today: str | None) -> list[tuple]:
    """A season's clubs, each from the day after his last game for the one before
    to the day before his first game for the next. `today` is his club on today's
    roster (this season only): it holds him from his last game anywhere, or all
    season if he has not played yet."""
    runs: list[list] = []
    for iso, team in sorted(apps):
        if runs and runs[-1][0] == team:
            runs[-1][2] = iso
        else:
            runs.append([team, iso, iso])
    out = [(team, season, runs[i - 1][2] if i else "", runs[i + 1][1] if i + 1 < len(runs) else END)
           for i, (team, _, _) in enumerate(runs)]
    if today:
        if not runs:
            out = [(today, season, "", END)]
        elif runs[-1][0] != today:
            team, s, lo, _ = out[-1]
            out[-1] = (team, s, lo, runs[-1][2] + END)
            out.append((today, season, runs[-1][2], END))
    return out


def from_backtest(games: list[dict]) -> Index:
    """2025-26 from the box-score cache, with each club's roster known in hindsight."""
    ix = Index()
    for tg in games:
        for p in tg["players"]:
            ix.add(p["id"], p["name"], tg["date"], tg["team"], tg["opp"], [p.get(c) for c in COLS])
    return ix.finish()


def load_season_file() -> dict:
    with gzip.open(SEASON_FILE, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def slate_files() -> list[Path]:
    return sorted(SLATES.glob("nba-research-20*.json"))


def index(season: dict | None = None) -> Index:
    """Last season from the season file, this season from the stored research
    file and every research slate on disk, and today's rosters from the newest
    slate each club is on."""
    ix = Index()
    season = season or load_season_file()
    cols = season["columns"]
    for pid, row in season["players"].items():
        for g in row["games"]:
            d = dict(zip(cols, g))
            ix.add(pid, row["name"], d["date"], d["team"], d["opp"], [d.get(c) for c in COLS])
    built = sorted(((s.get("built", ""), s) for s in (json.loads(p.read_text(encoding="utf-8")) for p in slate_files())
                    if s.get("season") == CURRENT), key=lambda b: b[0])
    # newest build first, then the stored file: a box score ESPN corrected beats the copy kept from before
    for _, slate in reversed(built):
        for g in slate.get("games") or []:
            for side in g["sides"].values():
                for p in side.get("players") or []:
                    for l in p.get("logs") or []:
                        if l.get("type") == 2 and l.get("season") == CURRENT and l.get("min"):
                            ix.add(p["id"], p["name"], l["date"], l["team"], l.get("opp", ""), [l.get(c) for c in COLS])
    if OUT.exists():
        stored = json.loads(OUT.read_text(encoding="utf-8"))
        for pid, p in stored.get("players", {}).items():
            for team, rows in p.get("g", {}).items():
                for r in rows:
                    iso, opp = stored["teams"][team][r[0]]
                    if season_of(iso) == CURRENT:
                        ix.add(pid, p["n"], iso, team, opp, r[1:])
    for _, slate in built:
        for g in slate.get("games") or []:
            for side in g["sides"].values():
                for p in side.get("players") or []:
                    ix.roster[p["id"]] = side["abbr"]
                    ix.names[p["id"]] = p["name"]
    return ix.finish()


# ── the research tab's file ────────────────────────────────────────────────────

def payload(ix: Index) -> dict:
    """Every player on a roster today: his games on each club, and the stretch
    of each club's games he was on it. The page splits any pair from these."""
    teams = {t: sorted(games.items()) for t, games in ix.team_games.items()}
    at = {t: {iso: i for i, (iso, _) in enumerate(rows)} for t, rows in teams.items()}
    players = {}
    for pid in sorted(ix.roster):
        g = defaultdict(list)
        for iso, team, _, _, line in ix.games.get(pid, ()):
            g[team].append([at[team][iso]] + [round(x) for x in line])
        on = defaultdict(list)
        for team, season, lo, hi in ix.stints.get(pid, ()):
            idx = [i for i, (iso, _) in enumerate(teams.get(team, ())) if season_of(iso) == season and lo < iso < hi]
            if idx:
                on[team].append([idx[0], idx[-1]])
        players[pid] = {"n": ix.names.get(pid, ""), "t": ix.roster[pid], "g": dict(g), "on": dict(on)}
    newest = max((iso for rows in teams.values() for iso, _ in rows), default="")
    return {"version": 1, "through": newest, "seasons": sorted({label(season_of(i)) for r in teams.values() for i, _ in r}),
            "cols": list(COLS), "teams": {t: [[iso, opp] for iso, opp in rows] for t, rows in sorted(teams.items())},
            "players": players}


def write(ix: Index) -> bool:
    """Rewrite the research file only when a game or a roster moved."""
    body = payload(ix)
    if OUT.exists() and {k: v for k, v in json.loads(OUT.read_text(encoding="utf-8")).items() if k != "built"} == body:
        return False
    body["built"] = datetime.now(timezone.utc).isoformat(timespec="minutes")
    text = json.dumps(body, separators=(",", ":"), ensure_ascii=False) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(f"[splits] wrote {OUT.relative_to(ROOT)} ({len(text) // 1024} KB, {len(body['players'])} players, "
          f"games through {body['through']})")
    return True


# ── the Prop Shop's adjustment ─────────────────────────────────────────────────

def load_fit() -> dict:
    """The knobs and the on/off switch the replay settled on."""
    if not FIT.exists():
        return dict(DEFAULT)
    fit = json.loads(FIT.read_text(encoding="utf-8"))
    return {**DEFAULT, **fit.get("knobs", {}), "enabled": bool(fit.get("enabled"))}


def shares(logs: list[dict], without: set, season: int, decay: float, min_decay: float,
           pre_weight: float = 0.4) -> tuple[float, float]:
    """(minutes, rate): how much of his minutes projection and of his per-minute
    rate already came from games without the teammate, weighted the way the model
    weighs them (prop_model.project_minutes, prop_model.decayed)."""
    newest = sorted(logs, key=lambda l: l["date"], reverse=True)
    reg = [l for l in newest if l.get("type") == 2 and l.get("min")][:15]
    wm = [min_decay ** i for i in range(len(reg))]
    m_share = sum(w for w, l in zip(wm, reg) if l["date"] in without) / sum(wm) if reg else 0.0
    tot = wo = 0.0
    for i, l in enumerate(newest):
        w = pm.rate_weight(l, season, pre_weight) * decay ** i * (l.get("min") or 0.0)
        tot += w
        if l["date"] in without:
            wo += w
    return m_share, (wo / tot if tot else 0.0)


def summary(w: list, wo: list) -> dict:
    """Games, minutes and stat totals each side of the split, and the paired minutes gap."""
    def side(games):
        return {"n": len(games), "min": sum(g[4][0] for g in games),
                **{s: sum(g[4][j] for g in games) for j, s in enumerate(pm.STATS, 1)}}
    return {"with": side(w), "without": side(wo), "paired_min": paired_gap(w, wo)}


def paired_gap(w: list, wo: list, near: int = 3) -> float | None:
    """His minutes in each game the teammate sat, against his nearest games with him
    (up to three either side): the gap without the role he had at the time. A
    rookie whose without-games all came in October, before he was in the rotation,
    reads no gap from that."""
    if not w or not wo:
        return None
    isos = [g[0] for g in w]
    gaps = []
    for g in wo:
        i = bisect.bisect_left(isos, g[0])
        local = w[max(0, i - near):i + near]
        gaps.append(g[4][0] - sum(x[4][0] for x in local) / len(local))
    return sum(gaps) / len(gaps)


def effect(sm: dict, rate: dict, m_share: float, r_share: float, knobs: dict, shrink: dict) -> dict | None:
    """One teammate out: (minutes change, per-minute ratio per stat).

    Minutes move by his without-minus-with gap, shrunk by the without games
    (k_min) and by the share of the projection already from without games. Each
    rate moves by its without/with ratio, the without rate shrunk toward the with
    rate by k_rate x the model's own shrink for that stat."""
    a, b = sm["with"], sm["without"]
    if a["n"] < knobs["min_with"] or b["n"] < 1:
        return None
    d_min = 0.0
    if knobs["k_min"] is not None:
        gap = sm["paired_min"] if knobs.get("paired") else b["min"] / b["n"] - a["min"] / a["n"]
        d_min = b["n"] / (b["n"] + knobs["k_min"]) * (1 - m_share) * gap
    ratio = {s: 1.0 for s in pm.STATS}
    if knobs["k_rate"] is not None:
        for s in pm.STATS:
            c = knobs["k_rate"] * shrink[s]
            r_w = (a[s] + c * rate[s]) / (a["min"] + c)
            r_wo = (b[s] + c * r_w) / (b["min"] + c)
            if r_w > 0:
                ratio[s] = 1 + (1 - r_share) * (r_wo / r_w - 1)
    return {"d_min": d_min, "ratio": ratio}


def combine(effects: list[dict], knobs: dict) -> dict | None:
    effects = [e for e in effects if e]
    if not effects:
        return None
    d_min = max(-knobs["cap_min"], min(knobs["cap_min"], sum(e["d_min"] for e in effects)))
    ratio = {s: max(knobs["ratio_lo"], min(knobs["ratio_hi"], math.prod(e["ratio"][s] for e in effects)))
             for s in pm.STATS}
    return {"d_min": d_min, "ratio": ratio}


def tonight(ix: Index, pid: str, logs: list[dict], mates: list[dict], before: str, rate: dict,
            fit: dict, knobs: dict, season: int, pre_weight: float) -> dict:
    """The teammates out tonight who carry the offense, each with his split, and
    the change they make to tonight's minutes and rates."""
    out, effects = [], []
    for mate in mates:
        use = ix.usage(mate["id"], before)
        if use is None or use < knobs["usage"]:
            continue
        w, wo = ix.split(pid, mate["id"], before)
        sm = summary(w, wo)
        m_share, r_share = shares(logs, {g[0] for g in wo}, season, fit["decay"], fit["min_decay"], pre_weight)
        e = effect(sm, rate, m_share, r_share, knobs, fit["shrink"])
        out.append({"id": mate["id"], "name": mate["name"], "usage": round(use, 1), "split": sm,
                    "m_share": round(m_share, 3), "r_share": round(r_share, 3), "effect": e})
        effects.append(e)
    return {"mates": out, "effect": combine(effects, knobs)}


# ── the replay ─────────────────────────────────────────────────────────────────

USAGE_GRID = (10.0, 14.0, 18.0)
K_MIN_GRID = (4.0, 8.0, 16.0, None)
K_RATE_GRID = (3.0, 9.0, None)
PAIRED_GRID = (False, True)


def notes(ix: Index, rows: list[dict], fit: dict) -> list[list[dict]]:
    """Per replayed player-game: every teammate on the club who is not in the
    box, his usage that morning and the split as it stood that morning."""
    out = []
    for r in rows:
        pid, team, iso = r["id"], r["team"], r["iso"]
        season = season_of(iso)
        prior = [{"date": g[0], "type": 2, "season": season, "min": g[4][0]} for g in ix.before(pid, iso)]
        mine = []
        for mate in ix.club.get((team, season), ()):
            if mate == pid or (mate, team, iso) in ix.played or not ix.on(mate, team, season, iso):
                continue
            use = ix.usage(mate, iso)
            if use is None or use < min(USAGE_GRID):
                continue
            w, wo = ix.split(pid, mate, iso)
            m_share, r_share = shares(prior, {g[0] for g in wo}, season, fit["decay"], fit["min_decay"])
            mine.append({"usage": use, "split": summary(w, wo), "m_share": m_share, "r_share": r_share})
        out.append(mine)
    return out


def adjusted(rows: list[dict], nts: list[list[dict]], shrink: dict, knobs: dict | None) -> tuple[dict, list[bool]]:
    """prop_fit.projections with the teammate-out adjustment; and which rows it moved."""
    out = {s: [] for s in pm.MARKETS}
    moved = []
    for r, mine in zip(rows, nts):
        rate = pm.per_minute(r["made"], r["mins"], r["lg"], shrink)
        m = r["m"]
        e = None
        if knobs:
            e = combine([effect(n["split"], rate, n["m_share"], n["r_share"], knobs, shrink)
                         for n in mine if n["usage"] >= knobs["usage"]], knobs)
        if e:
            m = max(0.0, min(44.0, m + e["d_min"]))
            rate = {s: rate[s] * e["ratio"][s] for s in pm.STATS}
        moved.append(bool(e) and (abs(e["d_min"]) > 1e-9 or any(abs(v - 1) > 1e-9 for v in e["ratio"].values())))
        one = {}
        for s in pm.STATS:
            one[s] = m * rate[s] * pm.matchup_ratio(r["opp"], r["lg"], s, r["opp_games"])
        for c, parts in pm.COMBOS.items():
            one[c] = sum(one[s] for s in parts)
        for s in pm.MARKETS:
            out[s].append(one[s])
    return out, moved


def score(proj: dict, rows: list[dict], train: list[int], test: list[int], markets) -> dict:
    """Fit level and scatter on the train rows; mean log-likelihood per row on
    each side, per market (higher is better; log loss is its negative)."""
    from nba_research import prop_fit as pf
    res = {}
    for s in markets:
        xs, ys = [proj[s][i] for i in train], [pf.actual(rows[i], s) for i in train]
        b = pf.fit_b(xs, ys)
        phi = pf.fit_phi(xs, ys, b)
        lls = [pm.logpmf(pf.actual(rows[i], s), pm.mean(b, proj[s][i]), phi) for i in range(len(rows))]
        res[s] = {"b": b, "phi": phi, "ll": lls}
    return res


def mean_ll(res: dict, idx: list[int], markets) -> float:
    return sum(sum(res[s]["ll"][i] for i in idx) / len(idx) for s in markets) if idx else 0.0


def line_loss(res: dict, proj: dict, rows: list[dict], idx: list[int], s: str, k: int) -> float:
    """Binary log loss of 'at least k' on the given rows."""
    from nba_research import prop_fit as pf
    tot = 0.0
    for i in idx:
        p = pm.at_least(k, pm.mean(res[s]["b"], proj[s][i]), res[s]["phi"])
        h = 1 if pf.actual(rows[i], s) >= k else 0
        tot -= h * math.log(max(p, 1e-6)) + (1 - h) * math.log(max(1 - p, 1e-6))
    return tot / len(idx) if idx else 0.0


def backtest(season: int = 2026) -> dict:
    from nba_research import prop_fit as pf
    games = pf.load_games(season)
    fit = pm.load_fit()
    shrink = fit["shrink"]
    rows = pf.replay(games, fit["decay"], fit["min_decay"])
    ix = from_backtest(games)
    print(f"[splits] replay: {len(rows)} player-games; reading each morning's teammates out", flush=True)
    nts = notes(ix, rows, fit)
    cut = f"{season}-{pf.TRAIN_END}"
    train = [i for i, r in enumerate(rows) if r["date"] < cut]
    test = [i for i, r in enumerate(rows) if r["date"] >= cut]
    base_proj, _ = adjusted(rows, nts, shrink, None)
    base = score(base_proj, rows, train, test, pm.STATS)
    print(f"[splits] base: train {mean_ll(base, train, pm.STATS):.4f}  held-out {mean_ll(base, test, pm.STATS):.4f}", flush=True)

    grid = []
    for usage, k_min, k_rate, paired in ((u, km, kr, pa) for u in USAGE_GRID for km in K_MIN_GRID
                                         for kr in K_RATE_GRID for pa in PAIRED_GRID):
        if k_min is None and (k_rate is None or paired):
            continue
        knobs = {**DEFAULT, "usage": usage, "k_min": k_min, "k_rate": k_rate, "paired": paired}
        proj, moved = adjusted(rows, nts, shrink, knobs)
        res = score(proj, rows, train, test, pm.STATS)
        hit_test = [i for i in test if moved[i]]
        g = {"knobs": {k: knobs[k] for k in ("usage", "k_min", "k_rate", "paired")},
             "train": round(mean_ll(res, train, pm.STATS) - mean_ll(base, train, pm.STATS), 5),
             "held_out": round(mean_ll(res, test, pm.STATS) - mean_ll(base, test, pm.STATS), 5),
             "held_out_moved": round(mean_ll(res, hit_test, pm.STATS) - mean_ll(base, hit_test, pm.STATS), 5),
             "moved_train": sum(1 for i in train if moved[i]), "moved_test": len(hit_test)}
        grid.append(g)
        print(f"[splits] usage {usage:>4} k_min {str(k_min):>4} k_rate {str(k_rate):>4} "
              f"{'paired' if paired else 'pooled'}: train {g['train']:+.5f}  held-out {g['held_out']:+.5f}  "
              f"moved rows {g['held_out_moved']:+.5f} ({g['moved_test']})", flush=True)

    # the knobs are picked on the train months; February on only checks them
    best = max(grid, key=lambda g: g["train"])
    knobs = {**DEFAULT, **best["knobs"]}
    proj, moved = adjusted(rows, nts, shrink, knobs)
    res = score(proj, rows, train, test, pm.MARKETS)
    base_all = score(base_proj, rows, train, test, pm.MARKETS)
    hit_test = [i for i in test if moved[i]]
    per_market = {}
    for s in pm.MARKETS:
        b_all = -sum(base_all[s]["ll"][i] for i in test) / len(test)
        a_all = -sum(res[s]["ll"][i] for i in test) / len(test)
        b_mv = -sum(base_all[s]["ll"][i] for i in hit_test) / len(hit_test) if hit_test else 0.0
        a_mv = -sum(res[s]["ll"][i] for i in hit_test) / len(hit_test) if hit_test else 0.0
        lines = {}
        for k in pf.CHECK_LINES.get(s, []):
            lines[f"{k}+"] = {"off": round(line_loss(base_all, base_proj, rows, hit_test, s, k), 4),
                              "on": round(line_loss(res, proj, rows, hit_test, s, k), 4)}
        per_market[s] = {"log_loss_off": round(b_all, 5), "log_loss_on": round(a_all, 5),
                         "moved_log_loss_off": round(b_mv, 5), "moved_log_loss_on": round(a_mv, 5),
                         "moved_lines": lines}
    held = {"log_loss_off": round(-mean_ll(base_all, test, pm.STATS), 5),
            "log_loss_on": round(-mean_ll(res, test, pm.STATS), 5),
            "moved_log_loss_off": round(-mean_ll(base_all, hit_test, pm.STATS), 5),
            "moved_log_loss_on": round(-mean_ll(res, hit_test, pm.STATS), 5)}
    enabled = held["log_loss_on"] < held["log_loss_off"] and held["moved_log_loss_on"] < held["moved_log_loss_off"]
    out = {
        "fitted": datetime.now(timezone.utc).isoformat(timespec="minutes"), "season": season, "label": label(season),
        "rows": len(rows), "train_rows": len(train), "test_rows": len(test), "test_from": cut,
        "moved_test_rows": len(hit_test), "enabled": enabled,
        "rule": "on only if the knobs picked on the train months lower the held-out log loss, overall and on the rows it moves",
        "knobs": {k: knobs[k] for k in DEFAULT if k != "enabled"},
        "held_out": held, "markets": per_market, "grid": grid,
    }
    FIT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"[splits] picked usage {knobs['usage']} k_min {knobs['k_min']} k_rate {knobs['k_rate']} "
          f"{'paired' if knobs['paired'] else 'pooled'} on the train months")
    print(f"[splits] held-out log loss, six stats summed: {held['log_loss_off']} off -> {held['log_loss_on']} on; "
          f"on the {len(hit_test)} rows it moves: {held['moved_log_loss_off']} -> {held['moved_log_loss_on']}")
    for s, m in per_market.items():
        print(f"  {s:7s} all {m['log_loss_off']:.5f} -> {m['log_loss_on']:.5f}   moved {m['moved_log_loss_off']:.5f} -> "
              f"{m['moved_log_loss_on']:.5f}   " + "  ".join(f"{k} {v['off']}->{v['on']}" for k, v in m["moved_lines"].items()))
    print(f"[splits] {'ENABLED' if enabled else 'left OFF'}: wrote {FIT.relative_to(ROOT)}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--backtest", action="store_true", help="replay 2025-26 with and without the adjustment")
    ap.add_argument("--season", type=int, default=2026)
    args = ap.parse_args()
    if args.backtest:
        backtest(args.season)
        return
    if not write(index()):
        print(f"[splits] {OUT.relative_to(ROOT)} unchanged")


if __name__ == "__main__":
    main()
