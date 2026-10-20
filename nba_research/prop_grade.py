"""Grade the Prop Shop against ESPN's final box scores and keep the record.

    python -m nba_research.prop_grade                     # grade every night that has finals, then report
    python -m nba_research.prop_grade --date 2026-10-20   # one night
    python -m nba_research.prop_grade --report            # the report only, no ESPN calls

Each night is read from its archive, preview/nba-research/prop-shop-archive/<date>.html:
the SHEET embedded in the page is the sheet as it was published, prices and all.
Once a prop's game is final it gets one row in nba_research/prop_shop_record.csv:

  hit / miss  an Over N.5 needs floor(N) + 1; an Under N.5 needs floor(N) or fewer
  push        a whole-number line landed exactly on it
  void        he never checked in, or the game was postponed or canceled

First-basket cards settle on the first made field goal (first_basket.opening) and
are void the same way. A row is never rewritten: a rerun appends only the props
that are still ungraded, so it is safe to run every morning. This module never
writes an archive, and once a night has rows prop_shop.py refuses to rebuild it.

The report: hit rate by score band and by market, the model's chance against what
actually happened (Brier and log loss next to DraftKings' implied chance on the same
props), and flat-stake ROI at the listed price. Nothing here changes the rating
weights or refits the model; below REFIT_FLOOR graded props it says so and stops.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from nba_research import build_slate, first_basket, prop_model as pm

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "preview" / "nba-research" / "prop-shop-archive"
RECORD = ROOT / "nba_research" / "prop_shop_record.csv"
FINAL_TTL = first_basket.FINAL_TTL
REFIT_FLOOR = 150   # graded props before a refit or a weight change is worth proposing

COLUMNS = ["date", "pid", "market", "line", "side", "chance", "price", "implied", "score", "band", "tags",
           "result", "actual",
           # beyond the bet: who, where, and the model's pieces, for the refit
           "name", "team", "opp", "game", "prop_id", "edge", "mean", "minutes", "actual_min",
           "pts_chance", "pts_form", "pts_matchup", "pts_role", "pts_price", "note"]
BANDS = ["elite", "strong", "playable", "thin", "dart"]
CHANCE_BINS = ((0, 40), (40, 50), (50, 60), (60, 70), (70, 80), (80, 101))
VOID_STATES = {"STATUS_POSTPONED", "STATUS_CANCELED", "STATUS_CANCELLED", "STATUS_FORFEIT"}


# ── the archive and the record ─────────────────────────────────────────────────

def read_sheet(path: Path) -> dict:
    """The `var SHEET = {...}` a published night carries."""
    html = path.read_text(encoding="utf-8")
    at = html.index("var SHEET = ") + len("var SHEET = ")
    sheet, _ = json.JSONDecoder().raw_decode(html[at:])
    return sheet


def nights() -> list[str]:
    return sorted(p.stem for p in ARCHIVE.glob("????-??-??.html"))


def load_record() -> list[dict]:
    if not RECORD.exists():
        return []
    with RECORD.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def graded_dates() -> set[str]:
    """Nights with at least one graded row: their archives are frozen."""
    return {r["date"] for r in load_record()}


def append(rows: list[dict]) -> None:
    if not rows:
        return
    new = not RECORD.exists()
    with RECORD.open("a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerows(rows)


# ── ESPN ───────────────────────────────────────────────────────────────────────

def state_of(summary: dict) -> str:
    """final, void (postponed or canceled) or pending."""
    st = ((((summary.get("header") or {}).get("competitions") or [{}])[0].get("status") or {}).get("type") or {})
    if st.get("completed") and st.get("name") not in VOID_STATES:
        return "final"
    return "void" if st.get("name") in VOID_STATES else "pending"


def final_summary(event: str) -> tuple[dict, str]:
    """A game's ESPN summary and its state. build_slate caches summaries for a
    year, so a game that isn't over is fetched fresh and its file removed: the
    research build must never read a half-played box score as a final."""
    route = f"summary?event={event}"
    path = build_slate.CACHE / (hashlib.sha256(route.encode()).hexdigest() + ".json")
    cached = path.exists()
    summary = build_slate.fetch(route, ttl=FINAL_TTL)
    if cached and state_of(summary) != "final":
        summary = build_slate.fetch(route, ttl=0)
    state = state_of(summary)
    if state != "final":
        path.unlink(missing_ok=True)
    return summary, state


def box_lines(summary: dict) -> tuple[dict, dict]:
    """({athlete id: stat line} for everyone who checked in, {athlete id: name})."""
    header = summary["header"]
    comp = header["competitions"][0]
    event = {"id": header["id"], "date": comp.get("date", ""), "season": header.get("season") or {},
             "seasonType": {"type": (header.get("season") or {}).get("type", 2)}, "competitions": [comp]}
    lines = {p["id"]: p for team in build_slate.parse_summary(event, summary) for p in team["players"]}
    names = {}
    for group in (summary.get("boxscore") or {}).get("players") or []:
        for section in group.get("statistics") or []:
            for a in section.get("athletes") or []:
                aid = str((a.get("athlete") or {}).get("id"))
                names[aid] = (a.get("athlete") or {}).get("displayName", "")
                # parse_summary drops a player with no minutes; seconds on the floor still count
                if aid not in lines and not a.get("didNotPlay") and a.get("stats"):
                    lines[aid] = build_slate.stats(section["names"], a["stats"])
    return lines, names


# ── grading ────────────────────────────────────────────────────────────────────

def settle(side: str, line: float, actual: float) -> str:
    if line == int(line) and actual == line:
        return "push"
    over = actual >= math.floor(line) + 1
    return ("hit" if over else "miss") if side == "over" else ("miss" if over else "hit")


def fmt(x) -> str:
    return "" if x is None else f"{x:g}" if isinstance(x, float) else str(x)


def prop_row(date: str, r: dict, result: str, actual, line_: dict | None, note: str = "") -> dict:
    parts = r.get("parts") or {}
    return {"date": date, "pid": r["pid"], "market": r["market"], "line": fmt(r["line"]), "side": r["side"],
            "chance": fmt(r["chance"]), "price": fmt(r.get("price")), "implied": fmt(r.get("implied")),
            "score": fmt(r["score"]), "band": r["band"], "tags": " ".join(r.get("tags") or []),
            "result": result, "actual": fmt(actual), "name": r["name"], "team": r["team"], "opp": r["opp"],
            "game": r["game"], "prop_id": r["id"], "edge": fmt(r.get("edge")), "mean": fmt(r.get("mean")),
            "minutes": fmt(r.get("minutes")), "actual_min": fmt(round(line_["min"], 1)) if line_ and line_.get("min") else "",
            "pts_chance": fmt(parts.get("chance")), "pts_form": fmt(parts.get("form")),
            "pts_matchup": fmt(parts.get("matchup")), "pts_role": fmt(parts.get("role")),
            "pts_price": fmt(parts.get("price")), "note": note}


def basket_row(date: str, c: dict, result: str, actual, note: str) -> dict:
    return {**{k: "" for k in COLUMNS}, "date": date, "pid": c["pid"], "market": "first_basket", "side": "yes",
            "chance": fmt(c["chance"]), "price": fmt(c.get("price")), "implied": fmt(c.get("implied")),
            "tags": "" if c.get("starting", True) else "bench", "result": result, "actual": fmt(actual),
            "name": c["name"], "team": c["team"], "opp": c["opp"], "game": c["game"],
            "prop_id": f"{c['pid']}-first_basket", "edge": fmt(c.get("edge")), "note": note}


def grade_night(date: str, done: set[tuple[str, str]]) -> tuple[list[dict], int]:
    """(new rows, props still waiting on their game) for one archived night."""
    sheet = read_sheet(ARCHIVE / f"{date}.html")
    props = [r for r in sheet.get("by_id", {}).values() if (date, r["id"]) not in done]
    cards = [c for c in sheet.get("first_basket") or [] if (date, f"{c['pid']}-first_basket") not in done]
    games = sorted({r["game"] for r in props} | {c["game"] for c in cards})
    rows, pending = [], 0
    for game in games:
        summary, state = final_summary(game)
        mine = [r for r in props if r["game"] == game]
        theirs = [c for c in cards if c["game"] == game]
        if state == "pending":
            pending += len(mine) + len(theirs)
            continue
        if state == "void":
            why = "game " + (((summary.get("header") or {}).get("competitions") or [{}])[0]
                             .get("status", {}).get("type", {}).get("description", "postponed")).lower()
            rows += [prop_row(date, r, "void", None, None, why) for r in mine]
            rows += [basket_row(date, c, "void", None, why) for c in theirs]
            continue
        lines, names = box_lines(summary)
        for r in sorted(mine, key=lambda r: -r["score"]):
            line_ = lines.get(r["pid"])
            if line_ is None:
                rows.append(prop_row(date, r, "void", None, None, "never checked in"))
                continue
            actual = sum(line_.get(s) or 0 for s in pm.COMBOS.get(r["market"], (r["market"],)))
            rows.append(prop_row(date, r, settle(r["side"], r["line"], actual), int(actual), line_))
        if theirs:
            opening = first_basket.opening(game)
            if not opening or not opening.get("first_fg"):
                print(f"[prop_grade] {date} game {game}: no play-by-play yet -- first basket left for later")
                pending += len(theirs)
                continue
            scorer = opening["first_fg"]
            note = f"first basket: {names.get(scorer, scorer)} ({opening.get('first_fg_team') or '?'})"
            for c in theirs:
                if c["pid"] not in lines:
                    rows.append(basket_row(date, c, "void", None, "never checked in; " + note))
                else:
                    won = scorer == c["pid"]
                    rows.append(basket_row(date, c, "hit" if won else "miss", int(won), note))
    return rows, pending


def grade(dates: list[str]) -> None:
    done = {(r["date"], r["prop_id"]) for r in load_record()}
    for date in dates:
        if not (ARCHIVE / f"{date}.html").exists():
            print(f"[prop_grade] {date}: no archive -- nothing to grade")
            continue
        rows, pending = grade_night(date, done)
        append(rows)
        done |= {(r["date"], r["prop_id"]) for r in rows}
        tally = [f"{sum(r['result'] == k for r in rows)} {k}" for k in ("hit", "miss", "push", "void")
                 if k in ("hit", "miss") or any(r["result"] == k for r in rows)]
        said = ([f"graded {len(rows)} ({', '.join(tally)})"] if rows else []) + \
            ([f"{pending} waiting on games not final yet"] if pending else [])
        if said:
            print(f"[prop_grade] {date}: " + ", ".join(said))
        for r in rows:
            mark = r["result"].upper().ljust(4)
            what = "first basket" if r["market"] == "first_basket" else f"{r['side']} {r['line']} {r['market']}"
            print(f"    {mark} {r['name']:24s} {what:20s} actual {r['actual'] or '—':>3s}  "
                  f"chance {r['chance']:>5s}%  score {r['score'] or '—':>5s}  {r['note']}")
    if build_slate.ERRORS:
        print(f"[prop_grade] {len(build_slate.ERRORS)} ESPN requests failed: those games stay ungraded")


# ── the report ─────────────────────────────────────────────────────────────────

def payout(price: int) -> float:
    """Profit on one unit that cashes."""
    return price / 100 if price > 0 else 100 / -price


def summarize(rows: list[dict]) -> str:
    n = len(rows)
    if not n:
        return "    —"
    hit = sum(r["result"] == "hit" for r in rows)
    chance = sum(float(r["chance"]) for r in rows) / n
    priced = [r for r in rows if r["implied"]]
    implied = f"{sum(float(r['implied']) for r in priced) / len(priced):5.1f}%" if priced else "     —"
    return f"{n:4d} {hit:4d} {100 * hit / n:6.1f}%  {chance:5.1f}%  {implied}"


def table(title: str, lines: list[tuple[str, list[dict]]]) -> None:
    """Hit rate, the model's average chance and DraftKings' average implied, per group."""
    print(f"\n{title:18s}{'n':>4s} {'hit':>4s} {'rate':>7s}  {'model':>6s}  {'DK':>6s}")
    for label, rows in lines:
        if rows:
            print(f"  {label:16s}{summarize(rows)}")


def brier(rows: list[dict], key: str) -> tuple[float, float]:
    b = ll = 0.0
    for r in rows:
        p = min(0.99, max(0.01, float(r[key]) / 100))
        y = r["result"] == "hit"
        b += (p - y) ** 2
        ll -= math.log(p if y else 1 - p)
    return b / len(rows), ll / len(rows)


def roi(rows: list[dict]) -> str:
    bets = [r for r in rows if r["price"] and r["side"] in ("over", "yes")]
    if not bets:
        return "   no priced bets"
    profit = sum(payout(int(r["price"])) if r["result"] == "hit" else -1.0 for r in bets)
    hit = sum(r["result"] == "hit" for r in bets)
    return f"{len(bets):4d} bets  {hit:3d} hit  {profit:+7.2f} u  ROI {100 * profit / len(bets):+6.1f}%"


def report() -> None:
    record = load_record()
    settled = [r for r in record if r["result"] in ("hit", "miss")]
    props = [r for r in settled if r["market"] != "first_basket"]
    baskets = [r for r in settled if r["market"] == "first_basket"]
    voids = sum(r["result"] in ("void", "push") for r in record)
    nights_ = sorted({r["date"] for r in record})
    print(f"\nProp Shop record: {len(props)} props and {len(baskets)} first baskets settled over {len(nights_)} "
          f"night{'s' * (len(nights_) != 1)}{f', {voids} void or push' if voids else ''}")
    if not settled:
        print("Nothing graded yet.")
        return
    table("By score band", [(b.title(), [r for r in props if r["band"] == b]) for b in BANDS])
    table("By market", [(pm.LABELS.get(m, m), [r for r in props if r["market"] == m])
                        for m in sorted({r["market"] for r in props})] + [("First basket", baskets)])
    table("By model chance", [(f"{lo}-{min(hi, 100)}%", [r for r in props if lo <= float(r["chance"]) < hi])
                              for lo, hi in CHANCE_BINS])
    both = [r for r in props if r["implied"]]
    if both:
        mb, ml = brier(both, "chance")
        db, dl = brier(both, "implied")
        print(f"\n  On the {len(both)} props DraftKings priced:   Brier   log loss   (lower is better)")
        print(f"    Prop Shop model                      {mb:.4f}   {ml:.4f}")
        print(f"    DraftKings implied (vig in)          {db:.4f}   {dl:.4f}")

    print("\nFlat 1-unit stakes at the listed DraftKings price")
    print(f"  All priced props  {roi(props)}")
    print(f"  Top Shelf         {roi([r for r in props if 'fav' in r['tags'].split()])}")
    print(f"  Bargain Bin       {roi([r for r in props if 'val' in r['tags'].split()])}")
    if baskets:
        print(f"  First basket      {roi(baskets)}")

    print()
    if len(props) < REFIT_FLOOR:
        print(f"Refit: {len(props)} of {REFIT_FLOOR} graded props -- too few to judge the weights or refit the "
              "model. Keep grading.")
        return
    flags = []
    rates = [(b, sum(r["result"] == "hit" for r in rows) / len(rows))
             for b in BANDS for rows in [[r for r in props if r["band"] == b]] if len(rows) >= 15]
    if any(a[1] < b[1] for a, b in zip(rates, rates[1:])):
        flags.append("a higher score band hit less often than a lower one")
    if both and brier(both, "chance")[0] > brier(both, "implied")[0]:
        flags.append("DraftKings' prices beat the model's chance on Brier")
    for lo, hi in CHANCE_BINS:
        rows = [r for r in props if lo <= float(r["chance"]) < hi]
        if len(rows) >= 25:
            gap = 100 * sum(r["result"] == "hit" for r in rows) / len(rows) - sum(float(r["chance"]) for r in rows) / len(rows)
            if abs(gap) > 8:
                flags.append(f"props the model put at {lo}-{min(hi, 100)}% hit {gap:+.0f} points off")
    if flags:
        print("Refit: the record supports a review -- " + "; ".join(flags) + ". Propose it to the owner; change nothing yet.")
    else:
        print("Refit: the record doesn't argue for a change: bands rank in order and the chances hold up.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Grade the WorstPickz NBA Prop Shop and report its record")
    ap.add_argument("--date", help="grade one night (default: every archived night)")
    ap.add_argument("--report", action="store_true", help="report only; no ESPN calls")
    args = ap.parse_args()
    if not args.report:
        grade([args.date] if args.date else nights())
    report()


if __name__ == "__main__":
    main()
