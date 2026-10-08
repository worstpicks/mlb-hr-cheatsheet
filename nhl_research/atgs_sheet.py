"""Build the Anytime Goal Scorer cheat sheet from a slate.

    python -m nhl_research.atgs_sheet --date 2026-09-29

The page the hand-built nhl_cheatsheet_*_revamp.html sheets were: the Worst
Pickz rating model, the score bands, top rated targets, plus-money value,
profile warnings, then every play by matchup. The difference is that nothing
here is pasted -- the old sheets were scored off a board copied in by hand (and
carried a note about team-label noise in the feed); this reads the slate the
research tab already built, so the numbers and the uniforms are the same ones
on the board.

Inputs
    preview/data/nhl-research-<date>.json   the slate (fetch-nhl-research-slate.py)
    nhl_research/atgs_days/<date>.txt        optional: the day's plays, pasted as
                                             exported from the research tab's Prop
                                             List. With it, the sheet is those plays;
                                             without it, every rated forward.
    nhl_research/atgs_days/<date>.lineup.txt optional: tonight's starting goalies and
                                             scratches, from the morning lineup
                                             reports. See load_lineup.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from nhl_research.rating import WEIGHTS, build_scales, score_row, warnings_for

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "preview" / "data"
NHL_DIR = ROOT / "preview" / "nhl-research"
TEMPLATE = Path(__file__).resolve().parent / "templates" / "atgs_sheet.html"
MANIFEST = NHL_DIR / "atgs-manifest.json"
PLAYS_DIR = Path(__file__).resolve().parent / "atgs_days"

# One Prop List row, as the research tab exports it. The name and the line slot
# arrive glued together ("Carter VerhaegheC4"), and so do the matchup and the
# market ("FLA vs CAROver 0.5 Goals"), so the pattern pins the slot and the
# three-letter codes rather than relying on spaces.
PLAY_LINE = re.compile(
    r"^(?P<name>.+?)(?P<role>[CLRDG]\d+)\s*\u00b7\s*"
    r"(?P<team>[A-Z]{2,3})\s+vs\s+(?P<opp>[A-Z]{2,3})"
    r"(?P<side>Over|Under)\s+(?P<line>\d+(?:\.\d+)?)\s+(?P<market>.+?)\s*$"
)

# A skater needs this many games before he is rated rather than merely shown.
MIN_GAMES = 8
# Forwards carry the market. A defenseman scores on about four percent of his
# nights; he belongs on the research board for blocks and shots, not here.
SCORING_POS = ("C", "L", "R")


def norm_name(name: str) -> str:
    """"Juraj Slafkovsk\u00fd" and "Juraj Slafkovsky" are the same man."""
    text = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", text.lower())


# One line of a lineup file:  goalie CGY Dustin Wolf | confirmed
#                             out NJD Connor Brown | lower body
#                             doubt WSH Ivan Miroshnichenko | Projected scratch -- why
LINEUP_LINE = re.compile(r"^(?P<kind>goalie|out|doubt)\s+(?P<team>[A-Z]{2,3})\s+(?P<name>[^|]+?)"
                         r"\s*(?:\|\s*(?P<note>.*))?$", re.IGNORECASE)


SEASON_DIR = Path(__file__).resolve().parent / "season_rates"
# Columns of a season export (per 60) and the window key each one feeds.
SEASON_COLS = {"g": "G/60", "sog": "SOG/60", "icf": "ICF/60", "iff": "IFF/60",
               "iscf": "ISCF/60", "ihdcf": "IHDCF/60"}
# The export counts chances its own way. Against our play-by-play counts for the
# same 263 skaters (10/6), its scoring chances run 1/0.78 of ours and its
# high-danger chances 1/1.12; shots, attempts and goals agree. Scaled to ours
# before blending, so a blended number means what the window number means.
SEASON_SCALE = {"iscf": 0.78, "ihdcf": 1.12}
# Weight on the season: games / (games + this). A full 82-game season gets ~0.62,
# a nine-game call-up ~0.15 -- the window still moves a role change.
SEASON_PRIOR_GAMES = 50


# A day's last-5-games export rides on top as recent form: a quarter of the
# rate at five games played, less with fewer. Five games is a role and a hot
# hand, not a sample -- it nudges, it does not steer.
RECENT_WEIGHT = 0.25


def _read_rate_export(path: Path) -> dict:
    """{(name, "F"|"D"): row} from one per-60 export.

    The export (PLAYER = "Brady Tkachuk LW", per-60 rates) sits under a few
    lines of settings; the table starts at its PLAYER header. A player on the
    injury report carries a tag after his position ("Macklin Celebrini C DTD"),
    kept as row["_status"]. Two players with one name and one position group
    are both dropped rather than guessed.

    Each row is also filed under ("~" + first initial + surname, group), so a
    first name spelled two ways ("Max" / "Maxim Shabanov") still finds him --
    see rate_row().
    """
    out: dict = {}
    seen: dict = {}
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    start = next((i for i, r in enumerate(rows) if r and r[0] == "PLAYER"), None)
    if start is None:
        return out
    head = rows[start]
    for raw in rows[start + 1:]:
        if not raw or not raw[0]:
            continue
        row = dict(zip(head, raw))
        m = re.match(r"^(.*?)\s+(C|LW|RW|D)(?:\s+([A-Z][A-Za-z-]*))?$", row["PLAYER"].strip())
        name, pos = (m.group(1), m.group(2)) if m else (row["PLAYER"].strip(), "")
        row["_status"] = (m.group(3) or "") if m else ""
        group = "D" if pos == "D" else "F"
        for key in ((norm_name(name), group), (_short_key(name), group)):
            seen[key] = seen.get(key, 0) + 1
            out[key] = row
    return {k: v for k, v in out.items() if seen[k] == 1}


def _short_key(name: str) -> str:
    """First initial + surname, the fallback key: "~mshabanov"."""
    parts = (name or "").split()
    return "~" + norm_name((parts[0][:1] if parts else "") + (parts[-1] if parts else ""))


def rate_row(rates: dict, r: dict) -> dict | None:
    """This row's export line: by full name, else by initial + surname."""
    group = "D" if r["pos"] == "D" else "F"
    return rates.get((norm_name(r["name"]), group)) or rates.get((_short_key(r["name"]), group))


def load_goalie_evidence(date: str) -> dict:
    paths = sorted(p for p in (ROOT / "data").glob("nhl-goalie-summary-*-????-??-??.csv")
                   if p.stem[-10:] <= date)
    if not paths:
        return {}
    path = paths[-1]
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("Time,Goalie,")), None)
    if start is None:
        return {}
    def number(value):
        try:
            return float(str(value).replace("%", ""))
        except ValueError:
            return None
    out = {}
    for row in csv.DictReader(lines[start:]):
        out[(norm_name(row["Goalie"]), row["Team"])] = {
            "date": path.stem[-10:], "gp": number(row["GP"]),
            **{key: number(row.get(col, "")) for key, col in {
                "sa": "SA/G", "hdsa": "HDSA/G", "sv": "SV%", "hdsv": "HDSV%",
                "sa_pct": "SA Pctl", "hdsa_pct": "HDSA Pctl",
                "sv_pct": "SV% Pctl", "hdsv_pct": "HDSV% Pctl"}.items()},
        }
    return out


def load_recent_rates(date: str) -> dict:
    """The day's last-5 export, atgs_days/<date>.l5.csv, or {} without one."""
    path = PLAYS_DIR / f"{date}.l5.csv"
    return _read_rate_export(path) if path.exists() else {}


def blend_recent(rows: list[dict], recent: dict) -> int:
    """Lean each row's shot and goal rates a little toward his last five games.

    The rate is taken at the ice time he is getting in those five games, so a
    promotion to the top line shows up even before the window catches it.
    """
    blended = 0
    for r in rows:
        s = rate_row(recent, r)
        if not s:
            continue
        if s.get("_status"):
            r["csv_status"] = s["_status"]
        try:
            gp = int(float(s["GP"]))
            toi = float(s.get("TOI/G") or 0) or r["toi"]
        except (KeyError, ValueError):
            gp, toi = 0, r["toi"]
        if not gp:
            continue
        baseline = {key: r.get(key) for key in SEASON_COLS}
        raw_recent = {}
        for key, col in SEASON_COLS.items():
            try:
                raw_recent[key] = float(s[col]) * toi / 60
            except (KeyError, ValueError):
                raw_recent[key] = None
        r["recent_evidence"] = {"gp": gp, "toi": toi, "baseline": baseline,
                                "raw": raw_recent,
                                "recent": {key: value * SEASON_SCALE.get(key, 1.0) if value is not None else None
                                           for key, value in raw_recent.items()}}
        w = RECENT_WEIGHT * min(gp, 5) / 5
        for key, col in SEASON_COLS.items():
            try:
                per60 = float(s.get(col) or 0)
            except ValueError:
                continue
            recent_pg = per60 * toi / 60 * SEASON_SCALE.get(key, 1.0)
            r[key] = round((1 - w) * r[key] + w * recent_pg, 3)
        r["recent_gp"] = gp
        blended += 1
    return blended


def load_season_rates() -> dict:
    """{(name, "F"|"D"): row} from every season export in season_rates/.

    Each export covers the clubs on the night it was pulled, so the files add
    up: a later file wins for a player who appears in two.
    """
    out: dict = {}
    for path in sorted(SEASON_DIR.glob("skaters-*.csv")):
        out.update(_read_rate_export(path))
    return out


def blend_season(rows: list[dict], season: dict) -> int:
    """Move each row's shot and goal rates toward his full season.

    The window is 25 games stitched from the end of last season, the preseason
    and the first nights of this one -- a few hot or cold nights move it a lot.
    A full season of per-60 rates, converted at the ice time he is playing now,
    is the steadier read of the same thing. Recent form (g5, last 5) is left
    to the window on purpose. Returns how many rows were blended.
    """
    blended = 0
    for r in rows:
        s = rate_row(season, r)
        try:
            gp = int(float(s["GP"])) if s else 0
        except (KeyError, ValueError):
            gp = 0
        if not gp:
            continue
        w = gp / (gp + SEASON_PRIOR_GAMES)
        for key, col in SEASON_COLS.items():
            try:
                per60 = float(s.get(col) or 0)
            except ValueError:
                continue
            season_pg = per60 * r["toi"] / 60 * SEASON_SCALE.get(key, 1.0)
            r[key] = round((1 - w) * r[key] + w * season_pg, 3)
        r["season_gp"] = gp
        r["season_w"] = round(w, 2)
        blended += 1
    return blended


def load_lineup(date: str) -> dict:
    """Tonight's starting goalies and scratches from atgs_days/<date>.lineup.txt.

    The slate cannot know either. Its goalie is the club's busiest by average
    ice time, which on opening night picked an injured-reserve goalie for two
    clubs and the wrong healthy one for three more; and the roster feed it reads
    still lists players on injured reserve. The morning lineup reports (RotoWire,
    DailyFaceoff) know both, so the day's file carries them:

        goalie PHI Joseph Woll | expected
        out NJD Connor Brown | lower body, out at least two games

    A named starter replaces the slate's guess for every skater shooting at him;
    a scratched player comes off the sheet and is reported, not rated. `doubt`
    is for the in-between -- healthy, but not in the projected lineup: the play
    stays (a bet on a player who does not dress is voided, not lost) and carries
    the note's first clause as its warning chip, and the whole note on his card.

        doubt WSH Ivan Miroshnichenko | Projected scratch -- not in the 12 forwards
    """
    lineup: dict = {"goalies": {}, "out": {}, "doubt": {}}
    path = PLAYS_DIR / f"{date}.lineup.txt"
    if not path.exists():
        return lineup
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        m = LINEUP_LINE.match(line)
        if not m:
            print(f"[atgs] WARN {path.name}: cannot read {raw.strip()!r}")
            continue
        team, name, note = m["team"].upper(), m["name"].strip(), (m["note"] or "").strip()
        kind = m["kind"].lower()
        if kind == "goalie":
            lineup["goalies"][team] = {"name": name, "note": note}
        else:
            lineup[kind][(norm_name(name), team)] = {"name": name, "team": team, "note": note}
    return lineup


def load_plays(date: str) -> list[dict] | None:
    """The day's plays from atgs_days/<date>.txt, or None when there is no list.

    Anything that is not a play row -- the game headers, the "x" remove buttons
    the export carries along -- simply does not match and is skipped.
    """
    path = PLAYS_DIR / f"{date}.txt"
    if not path.exists():
        return None
    plays = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        m = PLAY_LINE.match(raw.strip())
        if m:
            plays.append({
                "name": m["name"].strip(), "role": m["role"],
                "team": m["team"], "opp": m["opp"],
                "side": m["side"], "line": float(m["line"]), "market": m["market"].strip(),
            })
    return plays


def _stat(node: dict, key: str, default: float = 0.0) -> float:
    return float((node or {}).get(key) or default)


def _allowed_slot(allowed: dict, pos: str, rank: int) -> dict:
    """What this opponent gives up to that exact line slot, or to the group."""
    node = allowed.get(pos) or {}
    slot = (node.get("ranks") or {}).get(str(rank)) or {}
    if slot.get("gp"):
        return slot.get("stats") or {}
    return (node.get("overall") or {}).get("stats") or {}


def _starter(skaters: dict, named: str = "") -> dict:
    """The opponent's starter: the one the lineup file names, else the busiest.

    The NHL names starters an hour before puck drop, long after this builds, so
    without a lineup file the goalie with the most ice time is the stand-in.
    Where a club has no goalie rows the matchup component scores neutral rather
    than inventing an edge.
    """
    goalies = skaters.get("G") or []
    if named:
        want = norm_name(named)
        for goalie in goalies:
            if norm_name(goalie.get("name", "")) == want:
                return goalie
        # A starter the slate has no games for -- a third goalie up on a
        # back-to-back. Scored as neutral under his own name; falling back to
        # the busiest goalie would rate tonight's shooters against a goalie
        # who is not playing.
        return {"name": named, "stats": {}}
    return goalies[0] if goalies else {}


CARD_STATS = ("g", "sog", "iscf", "ihdcf")


def _league_slot(league: dict, pos: str, rank: int) -> dict:
    """What an average club gives up to this line slot -- the matchup's yardstick."""
    node = league.get(pos) or {}
    return (node.get("ranks") or {}).get(str(rank)) or node.get("overall") or {}


def _card_log(log: list, n: int = 10) -> list[dict]:
    """His last `n` games, trimmed to what the card's table shows."""
    out = []
    for g in log[-n:]:
        st = g.get("stats") or {}
        out.append({
            "d": g.get("date"), "ha": g.get("ha"), "opp": g.get("opp"), "toi": g.get("toi"),
            "g": int(st.get("g") or 0), "a": int(st.get("a") or 0),
            "sog": int(st.get("sog") or 0), "iscf": int(st.get("iscf") or 0),
            **({"pre": True} if g.get("pre") else {}),
        })
    return out


def goals_chance(rate: float, mult: float, need: int) -> float:
    """P(at least `need` goals) as a percent -- the same Poisson as goal_chance."""
    lam = max(rate, 0.0) * max(0.72, min(1.38, mult))
    below = sum(math.exp(-lam) * lam ** k / math.factorial(k) for k in range(need))
    return round(100 * (1 - below), 1)


def goal_chance(rate: float, mult: float) -> float:
    """P(at least one goal) as a percent: his rate, moved by the matchup.

    Goals arrive as rare independent events, which is what the Poisson tail
    describes -- a 0.6-goal scorer is not 60% to score, he is 45%. The matchup
    multiplier is clamped: 25 games of one line slot is thin enough that an
    unclamped ratio would hand a 3x to whoever drew one bad defensive night.
    """
    lam = max(rate, 0.0) * max(0.72, min(1.38, mult))
    return round(100 * (1 - math.exp(-lam)), 1)


# A goalie's save rates are read as if he had also faced this many shots at the
# league's rate. A starter's 25 games (~650 shots) barely move; DiPietro's four
# games at .935 on 10/3 come back to about .91 instead of branding every Wild
# shooter "too hot" on a hundred shots.
GOALIE_PRIOR_SHOTS = 150


def _goalie_rates(g_stats: dict, gp: int, league_g: dict) -> tuple[float, float, float, float]:
    """(save rate, high-danger save rate) as the model reads them, then as he posted them."""
    sa, sv = _stat(g_stats, "sa"), _stat(g_stats, "sv")
    hd_sa, hd_sv = _stat(g_stats, "hd_sa"), _stat(g_stats, "hd_sv")
    if not sa:
        return 0.0, 0.0, 0.0, 0.0
    lg_sa, lg_hd_sa = _stat(league_g, "sa"), _stat(league_g, "hd_sa")
    lg_sv = _stat(league_g, "sv") / lg_sa if lg_sa else 0.895
    lg_hd = _stat(league_g, "hd_sv") / lg_hd_sa if lg_hd_sa else 0.81
    games = max(gp, 1)
    k = GOALIE_PRIOR_SHOTS
    k_hd = k * (lg_hd_sa / lg_sa if lg_sa else 0.3)
    read = (sv * games + k * lg_sv) / (sa * games + k)
    read_hd = (hd_sv * games + k_hd * lg_hd) / (hd_sa * games + k_hd) if hd_sa else 0.0
    return read, read_hd, sv / sa, (hd_sv / hd_sa if hd_sa else 0.0)


def collect(slate: dict, starters: dict | None = None) -> list[dict]:
    """One row per rateable skater on the slate, with every model input on it.

    `starters` maps a club to the goalie it is starting tonight (load_lineup).
    """
    rows: list[dict] = []
    league = slate.get("league") or {}
    starters = starters or {}
    for game in slate.get("games") or []:
        for side, other in (("away", "home"), ("home", "away")):
            team, opp = game[side], game[other]
            allowed = game.get(f"{other}_allowed") or {}
            named = starters.get(opp) or {}
            goalie = _starter(game.get(f"{other}_skaters") or {}, named.get("name", ""))
            # did the lineup file pick him, or is he the slate's guess?
            g_set = bool(named) and norm_name(goalie.get("name", "")) == norm_name(named["name"])
            g_stats = goalie.get("stats") or {}
            league_g = (league.get("G") or {}).get("overall") or {}
            g_gp = int(goalie.get("gp") or 0)
            g_read, g_read_hd, g_raw, g_raw_hd = _goalie_rates(g_stats, g_gp, league_g)
            lg_sa = _stat(league_g, "sa", 27.0)
            prior_games = GOALIE_PRIOR_SHOTS / lg_sa
            g_load = (_stat(g_stats, "sa") * g_gp + lg_sa * prior_games) / (g_gp + prior_games)
            for pos in SCORING_POS:
                for player in (game.get(f"{side}_skaters") or {}).get(pos) or []:
                    stats = player.get("stats") or {}
                    rank = player.get("rank", 1)
                    slot = _allowed_slot(allowed, pos, rank)
                    log = player.get("log") or []
                    last5 = log[-5:]
                    g5 = sum(_stat(x.get("stats"), "g") for x in last5)
                    rows.append({
                        "id": f"{game['id']}-{player.get('player_id')}",
                        "player_id": player.get("player_id"),
                        "name": player.get("name", ""),
                        "pos": pos,
                        "rank": rank,
                        "role": f"{pos}{rank}",
                        "team": team,
                        "opp": opp,
                        "headshot": player.get("headshot", ""),
                        "game": f"{game['away']}@{game['home']}",
                        "games": int(player.get("gp") or 0),
                        "small": int(player.get("gp") or 0) < MIN_GAMES,
                        # his own profile
                        "g": round(_stat(stats, "g"), 3),
                        "sog": round(_stat(stats, "sog"), 2),
                        "icf": round(_stat(stats, "icf"), 2),
                        "iff": round(_stat(stats, "iff"), 2),
                        "iscf": round(_stat(stats, "iscf"), 2),
                        "ihdcf": round(_stat(stats, "ihdcf"), 2),
                        "toi": round(_stat(stats, "toi") / 60, 1),
                        "pp_p": round(_stat(stats, "pp_p"), 2),
                        "g5": g5,
                        "g5_rate": round(g5 / max(len(last5), 1), 3),
                        # the lane he is attacking
                        "opp_g": round(_stat(slot, "g"), 3),
                        "opp_sog": round(_stat(slot, "sog"), 2),
                        "opp_iscf": round(_stat(slot, "iscf"), 2),
                        # the goalie in his way
                        "g_name": goalie.get("name", ""),
                        # what the model reads (shrunk by sample) and what he posted
                        "g_sv_pct": round(g_read, 4),
                        "g_hd_sv_pct": round(g_read_hd, 4),
                        "g_sv_raw": round(g_raw, 4),
                        "g_hd_raw": round(g_raw_hd, 4),
                        # goals against as the model reads it: his workload at the read
                        # save rate, the workload shrunk the same way -- a few relief
                        # appearances make a light-looking night, not a stingy goalie
                        "g_ga": round(g_load * (1 - g_read), 2) if g_read else round(_stat(g_stats, "ga"), 2),
                        "g_ga_raw": round(_stat(g_stats, "ga"), 2),
                        "g_src": "lineup" if g_set else "model",
                        "g_note": named.get("note", "") if g_set else "",
                        "lines": player.get("lines") or {},
                        # ── for the player card ──
                        "game_id": game.get("id"),
                        "side": side,
                        "kick": game.get("kickoff", ""),
                        "seasons": player.get("seasons") or [],
                        "a": round(_stat(stats, "a"), 3),
                        "p": round(_stat(stats, "p"), 3),
                        # hit rates over his window: the flags average to a share
                        "hit": {k: round(100 * _stat(stats, k)) for k in
                                ("g_1", "pts_1", "sog_2", "sog_3", "sog_4")},
                        "slot": {k: round(_stat(slot, k), 3) for k in CARD_STATS},
                        "lg_slot": {k: round(_stat(_league_slot(league, pos, rank), k), 3)
                                    for k in CARD_STATS},
                        "g_sa": round(_stat(g_stats, "sa"), 1),
                        "g_gp": int(goalie.get("gp") or 0),
                        "log10": _card_log(log),
                    })
    return rows


def rate(rows: list[dict], slate_scales: dict) -> list[dict]:
    """Score every row, then tag it."""
    scales = build_scales(slate_scales)
    for r in rows:
        r.update(score_row(r, scales))
        r["warning"] = warnings_for(r, r["parts"])
        tags = []
        if r["band"] in ("elite", "strong"):
            tags.append("fav")
        if r["parts"]["defense"] / WEIGHTS["defense"] >= 0.75:
            tags.append("mat")
        if r["parts"]["volume"] / WEIGHTS["volume"] >= 0.78:
            tags.append("vol")
        if r["parts"]["quality"] / WEIGHTS["quality"] >= 0.78:
            tags.append("qual")
        if r["parts"]["goalie"] / WEIGHTS["goalie"] >= 0.75:
            tags.append("gl")
        if r["pp_p"] >= 0.35:
            tags.append("pp")
        if r["g5"] >= 3:
            tags.append("hot")
        r["tags"] = tags
        r["why"] = why(r)
        lg_g = r["lg_slot"].get("g") or 0
        r["mult"] = round(r["opp_g"] / lg_g, 3) if lg_g and r["opp_g"] else 1.0
        r["chance"] = goal_chance(r["g"], r["mult"])
        # where he sits among the league's forwards, for "top 12%" style reads
        r["pctl"] = {k: round(100 * scales[k].of(r[k]))
                     for k in ("sog", "icf", "iscf", "ihdcf", "g", "toi", "pp_p") if k in scales}
        r["reasons"] = reasons(r)
    return rows


def pct3(value: float) -> str:
    """Save percentage as hockey writes it: .893, not 0.893."""
    return f"{value:.3f}".lstrip("0") if value < 1 else f"{value:.3f}"


def reasons(r: dict) -> list[dict]:
    """The five components, each with its points and the numbers behind them."""
    pc = r.get("pctl") or {}

    def top(k):
        v = pc.get(k)
        return f"top {max(1, 100 - v)}% of forwards" if v is not None and v >= 50 else (
            f"bottom {max(1, v)}%" if v is not None else "")

    lg = r.get("lg_slot") or {}
    diff = (r["mult"] - 1) * 100 if r.get("mult") else 0
    lane = ("an average club" if abs(diff) < 4 else
            f"{abs(diff):.0f}% {'more' if diff > 0 else 'less'} than an average club")
    thin = r.get("g_gp", 25) < 10
    goalie = (f"{r['g_name']}: {pct3(r.get('g_sv_raw') or r['g_sv_pct'])} save rate, "
              f"{pct3(r.get('g_hd_raw') or r['g_hd_sv_pct'])} on high-danger shots, "
              f"{r.get('g_ga_raw', r['g_ga']):.2f} goals against a game"
              + (f" -- over only {r['g_gp']} games, so read as {pct3(r['g_sv_pct'])}" if thin else "")
              if r.get("g_name") and r.get("g_sv_pct") else
              f"{r['g_name']} has no NHL games in the sample -- scored as neutral" if r.get("g_name")
              else "No starter to read yet -- scored as neutral")
    return [
        {"part": "volume", "label": "Shot volume",
         "text": f"{r['sog']:.1f} shots and {r['icf']:.1f} attempts a game \u2014 {top('sog')}"
                 + _blend_note(r)},
        {"part": "quality", "label": "Shot quality",
         "text": f"{r['iscf']:.1f} scoring chances a game, {r['ihdcf']:.1f} from the inner slot, "
                 f"{r['iff']:.1f} unblocked \u2014 {top('iscf')}"},
        {"part": "defense", "label": "Defensive lane",
         "text": f"{r['opp']} gives up {r['opp_g']:.2f} goals and {r['opp_sog']:.1f} shots a game to "
                 f"{r['role']}s \u2014 {lane} (league {lg.get('g', 0):.2f})"},
        {"part": "goalie", "label": "Goalie", "text": goalie},
        {"part": "form", "label": "Form & role",
         "text": f"{int(r['g5'])} goals in his last 5 \u00b7 {r['toi']:.1f} minutes a night \u00b7 "
                 f"{r['pp_p']:.2f} power-play points a game"},
    ]


def _blend_note(r: dict) -> str:
    """Where the rates came from, when more than the 25-game window went in."""
    extra = []
    if r.get("season_gp"):
        extra.append(f"his {r['season_gp']}-game 2025-26 season")
    if r.get("recent_gp"):
        extra.append(f"his last {r['recent_gp']} games")
    return f" (his last {r['games']} games blended with {' and '.join(extra)})" if extra else ""


def why(r: dict) -> str:
    """The edge, in the voice the hand-built sheets used."""
    bits = [
        f"{r['sog']:.1f} shots and {r['iscf']:.1f} scoring chances a game on "
        f"{r['toi']:.1f} minutes, scoring {r['g']:.2f} a night over his last {r['games']}."
    ]
    if r["parts"]["defense"] / WEIGHTS["defense"] >= 0.7:
        bits.append(f"{r['opp']} leaks {r['opp_g']:.2f} goals and {r['opp_sog']:.1f} shots "
                    f"a game to {r['role']}s.")
    elif r["parts"]["defense"] / WEIGHTS["defense"] <= 0.45:
        bits.append(f"{r['opp']} holds {r['role']}s to {r['opp_g']:.2f} goals a game.")
    if r["g_name"] and r["g_sv_pct"]:
        trend = "a leaking" if r["parts"]["goalie"] / WEIGHTS["goalie"] >= 0.7 else "a steady"
        if r.get("g_gp", 25) < 10:
            bits.append(f"{r['g_name']} has {r['g_gp']} games to his name "
                        f"({pct3(r.get('g_sv_raw') or r['g_sv_pct'])}), read as {pct3(r['g_sv_pct'])}.")
        else:
            bits.append(f"{r['g_name']} is {trend} {pct3(r.get('g_sv_raw') or r['g_sv_pct'])} with a "
                        f"{pct3(r.get('g_hd_raw') or r['g_hd_sv_pct'])} high-danger rate.")
    if r["pp_p"] >= 0.35:
        bits.append(f"He works the power play for {r['pp_p']:.2f} points a game.")
    if r["g5"] >= 3:
        bits.append(f"{int(r['g5'])} goals in his last five.")
    return " ".join(bits)


def build_sheet(date: str) -> dict:
    path = DATA / f"nhl-research-{date}.json"
    if not path.exists():
        raise SystemExit(
            f"No slate for {date}. Run: python fetch-nhl-research-slate.py --date {date}")
    slate = json.loads(path.read_text(encoding="utf-8"))

    lineup = load_lineup(date)
    for team, named in lineup["goalies"].items():
        clubs = [g for g in slate.get("games") or [] if team in (g["away"], g["home"])]
        side = clubs and ("away" if clubs[0]["away"] == team else "home")
        names = [norm_name(p.get("name", "")) for p in
                 ((clubs[0].get(f"{side}_skaters") or {}).get("G") or [])] if clubs else []
        if norm_name(named["name"]) not in names:
            print(f"[atgs] note: starter {named['name']} ({team}) has no games in the slate -- "
                  f"the goalie component is scored as neutral for {team}'s opponents")
    rows = collect(slate, lineup["goalies"])
    season = load_season_rates()
    if season:
        n = blend_season(rows, season)
        print(f"[atgs] season rates: {n} of {len(rows)} skaters blended with 2025-26")
    recent = load_recent_rates(date)
    if recent:
        n = blend_recent(rows, recent)
        print(f"[atgs] last-5 rates: {n} of {len(rows)} skaters leaned toward their last five games")
        tagged = [f"{r['name']} ({r['team']}) {r['csv_status']}" for r in rows if r.get("csv_status")]
        if tagged:
            print(f"[atgs] the export tags as injured: {', '.join(tagged)} -- check the lineup file")
    rows = rate(rows, slate.get("scales") or {})
    out = lineup["out"]
    rows = [r for r in rows if (norm_name(r["name"]), r["team"]) not in out]
    for r in rows:
        doubt = lineup["doubt"].get((norm_name(r["name"]), r["team"]))
        if doubt:
            r["warning"] = doubt["note"].split(" -- ")[0] or "Lineup in doubt"
            r["doubt_note"] = doubt["note"].replace(" -- ", ": ", 1)

    # With a play list the sheet is exactly those plays. Scoring happens first,
    # against league-wide scales, so narrowing the board does not move a score.
    plays = load_plays(date)
    unmatched: list[dict] = []
    scratched: list[dict] = []
    if plays is not None:
        index = {(norm_name(r["name"]), r["team"]): r for r in rows}
        listed = []
        for play in plays:
            key = (norm_name(play["name"]), play["team"])
            if key in out:
                scratched.append({**play, "note": out[key]["note"]})
                continue
            row = index.get(key)
            if row is None:
                unmatched.append(play)
                continue
            row["market"] = f'{play["side"]} {play["line"]:g} {play["market"]}'
            row["listed_role"] = play["role"]
            # what settles it on the page: a 0.5 line needs one goal, 1.5 needs two
            row["line"] = play["line"]
            # "Over 1 Goals" is a two-goal bet. The rating still reads his profile,
            # but the chance has to be the one the bet needs.
            need = int(math.floor(play["line"])) + 1
            if need >= 2:
                row["need"] = need
                row["chance"] = goals_chance(row["g"], row["mult"], need)
            # "ou", not "side": "side" is the home/away the card's research link needs
            row["ou"] = play["side"]
            listed.append(row)
        rows = listed
    goalie_evidence = load_goalie_evidence(date)
    for r in rows:
        r["goalie_evidence"] = goalie_evidence.get((norm_name(r.get("g_name", "")), r["opp"]), {})
    by_id = {r["id"]: r for r in rows}

    games_out = []
    for game in slate.get("games") or []:
        key = f"{game['away']}@{game['home']}"
        sides = {}
        for team in (game["away"], game["home"]):
            plays = [r for r in rows if r["game"] == key and r["team"] == team]
            plays.sort(key=lambda r: r["score"], reverse=True)
            sides[team] = plays
        games_out.append({
            "away": game["away"], "home": game["home"],
            "away_name": game.get("away_name", ""), "home_name": game.get("home_name", ""),
            "kick": game.get("kickoff", ""), "venue": game.get("venue", ""),
            "away_record": game.get("away_record", ""),
            "home_record": game.get("home_record", ""),
            "sides": sides,
        })

    rated = sorted((r for r in rows if not r["small"]), key=lambda r: r["score"], reverse=True)
    # The Top 5 is the one-goal board: a two-goal bet at the top would read as
    # the night's best anytime scorer.
    top = [r["id"] for r in rated if not r.get("need")][:5]

    # Plus-money value: the best scores that still pay better than even. Without
    # a price feed there is nothing to sort on, so the section stays empty
    # rather than inventing odds.
    value = [r["id"] for r in rated
             if not r.get("need") and str(r["lines"].get("atgs", "")).startswith("+")][:5]

    # Profile warnings: names the model likes less than their reputation would.
    warned = sorted((r for r in rated if r["warning"]), key=lambda r: r["score"])
    warnings = [r["id"] for r in warned[:5]]

    kicks = sorted(g["kick"] for g in games_out if g["kick"])
    return {
        "date": date,
        "season": slate.get("season"),
        "stats_season": slate.get("stats_season"),
        "root": "",
        "built": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "first_kick": kicks[0] if kicks else "",
        "last_kick": kicks[-1] if kicks else "",
        "games": games_out,
        "top5": top,
        "value": value,
        "warnings": warnings,
        "has_props": slate.get("has_props", False),
        "weights": WEIGHTS,
        "by_id": by_id,
        "listed": plays is not None,
        "unmatched": unmatched,
        "scratched": scratched,
    }


def render(sheet: dict, root: str) -> str:
    html = TEMPLATE.read_text(encoding="utf-8")
    data = dict(sheet, root=root)
    html = html.replace("/*__SHEET__*/null",
                        json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    return html.replace("__ROOT__", root).replace("__DATE__", sheet["date"])


_BUILT_STAMP = re.compile(r'"built":"[^"]*"')


def _write_if_changed(path: Path, text: str) -> bool:
    """Write `text` unless the file already says the same thing bar the build time.

    The scheduled build re-renders the sheet several times a day. Without this
    every run would differ by its timestamp alone and commit the page again.
    """
    if path.exists():
        old = path.read_text(encoding="utf-8")
        if _BUILT_STAMP.sub('"built":""', old) == _BUILT_STAMP.sub('"built":""', text):
            return False
    path.write_text(text, encoding="utf-8")
    return True


def publish(sheet: dict) -> Path:
    """Current slate at nhl-research/atgs.html, every slate in archive/, and
    atgs-manifest.json feeding the date dropdown. Only the newest date takes
    over atgs.html, so rebuilding an old slate never replaces today's."""
    date = sheet["date"]
    archive = NHL_DIR / "archive" / f"{date}.html"
    archive.parent.mkdir(parents=True, exist_ok=True)
    changed = _write_if_changed(archive, render(sheet, "../"))

    manifest = {"version": 1, "sheets": []}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = {e["key"]: e for e in manifest.get("sheets", [])}
    entries[date] = {"key": date, "date": date}
    ordered = sorted(entries.values(), key=lambda e: e["date"], reverse=True)
    # "Current" is the newest slate that has actually arrived. Taking the newest
    # date outright let a slate built ahead of time sit on atgs.html and hide
    # tonight's board behind the dropdown.
    # The scheduled build runs on a UTC clock, where it is already tomorrow by
    # 8 pm Eastern -- it passes the Eastern date in NHL_TODAY so an evening run
    # does not promote the next day's sheet early.
    today = os.environ.get("NHL_TODAY") or datetime.now().date().isoformat()
    latest = next((e for e in ordered if e["date"] <= today), ordered[0])
    for e in ordered:
        # "%-d" strips the leading zero on Unix but raises on Windows, so the
        # zero comes off the formatted string instead.
        try:
            pretty = datetime.strptime(e["date"], "%Y-%m-%d").strftime("%b %d").replace(" 0", " ")
        except ValueError:
            pretty = e["date"]
        if e is latest:
            e["label"], e["href"] = f"{pretty} — current slate", "atgs.html"
        else:
            e["label"], e["href"] = pretty, f"archive/{e['date']}.html"
    body = json.dumps({"version": 1, "sheets": ordered}, indent=2, ensure_ascii=False) + "\n"
    if not MANIFEST.exists() or MANIFEST.read_text(encoding="utf-8") != body:
        MANIFEST.write_text(body, encoding="utf-8")

    if latest["key"] == date:
        changed = _write_if_changed(NHL_DIR / "atgs.html", render(sheet, "")) or changed
        print(f"[atgs] {date} is the current slate: nhl-research/atgs.html")
    print(f"[atgs] {'archived as' if changed else 'unchanged:'} {archive.relative_to(ROOT)}; "
          f"the list has {len(ordered)} slates")
    return archive


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the NHL Anytime Goal Scorer sheet")
    parser.add_argument("--date", required=True, help='Slate date, "2026-09-29"')
    args = parser.parse_args()

    sheet = build_sheet(args.date)
    rows = list(sheet["by_id"].values())
    bands: dict = {}
    for r in rows:
        bands[r["band_label"]] = bands.get(r["band_label"], 0) + 1
    if sheet["unmatched"]:
        print(f"[atgs] WARN {len(sheet['unmatched'])} listed play(s) not on the slate:")
        for play in sheet["unmatched"]:
            print(f"[atgs]   {play['name']} ({play['team']} {play['role']}) -- not in the club's lineup")
    for r in rows:
        if r.get("doubt_note"):
            print(f"[atgs] doubt: {r['name']} ({r['team']} {r['role']}) -- {r['doubt_note']}")
    for play in sheet["scratched"]:
        print(f"[atgs] out: {play['name']} ({play['team']} {play['role']})"
              f"{' -- ' + play['note'] if play['note'] else ''}")
    moved = [r for r in rows if r.get("listed_role") and r["listed_role"] != r["role"]]
    for r in moved:
        print(f"[atgs] note {r['name']}: listed as {r['listed_role']}, slate has him at {r['role']}")
    print(f"[atgs] {len(sheet['games'])} games, {len(rows)} plays, bands {bands}, "
          f"{sum(1 for r in rows if r['small'])} small samples")
    print("[atgs] top 5: " + ", ".join(
        f"{sheet['by_id'][i]['name']} ({sheet['by_id'][i]['score']})" for i in sheet["top5"]))
    if sheet["warnings"]:
        print("[atgs] warnings: " + ", ".join(
            f"{sheet['by_id'][i]['name']} — {sheet['by_id'][i]['warning']}"
            for i in sheet["warnings"]))
    publish(sheet)


if __name__ == "__main__":
    main()
