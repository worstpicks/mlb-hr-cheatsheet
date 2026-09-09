#!/usr/bin/env python3
"""Backtest the Goblin hits parlay: what did the legs actually do?

Reads the hits legs out of every archived sheet, pulls real boxscore outcomes
from the MLB Stats API, and reports per-leg hit rate, per-ticket leg counts and
how often an 11-leg ticket could ever have cashed. Boxscores are cached so
re-runs are cheap.
"""
from __future__ import annotations

import json
import re
import html as htmllib
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = Path(
    "C:/Users/allmi/AppData/Local/Temp/claude/C--Users-allmi-claude/"
    "33dec01e-fce9-422f-9b86-8d758d45d517/scratchpad/boxscore-cache.json"
)


def fold(n: str) -> str:
    b = unicodedata.normalize("NFKD", n or "")
    b = "".join(c for c in b if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", b.lower())


def get(url: str):
    with urllib.request.urlopen(url, timeout=40) as r:
        return json.load(r)


def load_cache() -> dict:
    if CACHE.is_file():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def save_cache(c: dict) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(c), encoding="utf-8")


def day_results(date: str, cache: dict) -> dict:
    """folded name -> {hits, pa, ab, slot} for every batter that played."""
    if date in cache:
        return cache[date]
    out: dict[str, dict] = {}
    try:
        sched = get(f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}")
    except Exception as e:
        print(f"  {date}: schedule error {e}")
        cache[date] = out
        return out
    pks = [g["gamePk"] for d in sched.get("dates", []) for g in d.get("games", [])]
    for pk in pks:
        try:
            box = get(f"https://statsapi.mlb.com/api/v1/game/{pk}/boxscore")
        except Exception:
            continue
        for side in ("away", "home"):
            team = box.get("teams", {}).get(side, {})
            for pid, p in (team.get("players") or {}).items():
                bat = (p.get("stats") or {}).get("batting") or {}
                if not bat:
                    continue
                name = (p.get("person") or {}).get("fullName") or ""
                order = p.get("battingOrder")
                slot = int(order) // 100 if order and str(order).isdigit() else None
                sub = bool(order) and str(order)[-2:] != "00"
                key = fold(name)
                prev = out.get(key)
                rec = {
                    "hits": bat.get("hits", 0),
                    "pa": bat.get("plateAppearances", 0),
                    "ab": bat.get("atBats", 0),
                    "slot": slot,
                    "sub": sub,
                }
                # A doubleheader gives two lines; sum them (either game can cash).
                if prev:
                    rec["hits"] += prev["hits"]
                    rec["pa"] += prev["pa"]
                    rec["ab"] += prev["ab"]
                    rec["slot"] = prev["slot"] or rec["slot"]
                out[key] = rec
    cache[date] = out
    return out


def archive_legs() -> list[tuple[str, list[str]]]:
    out = []
    for path in sorted((ROOT / "preview" / "archive").glob("2026-*.html")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for a in re.findall(r"data-goblin-gambly-lines='([^']+)'", text):
            u = htmllib.unescape(a)
            if "hits" not in u:
                continue
            try:
                legs = json.loads(u)
            except Exception:
                continue
            names = [l.split(" - ")[0].strip() for l in legs if "hits" in l]
            if names:
                out.append((path.stem, names))
                break
    return out


def main() -> None:
    cache = load_cache()
    tickets = archive_legs()
    print(f"archived hits tickets: {len(tickets)}\n")

    tot_legs = tot_hit = 0
    cashed = 0
    per_ticket = []
    slot_hits: dict[int, list[int]] = {}
    missing = 0

    for date, names in tickets:
        res = day_results(date, cache)
        if not res:
            continue
        got = 0
        n = 0
        for nm in names:
            r = res.get(fold(nm))
            if r is None:
                missing += 1
                continue
            n += 1
            hit = 1 if r["hits"] >= 1 else 0
            got += hit
            tot_legs += 1
            tot_hit += hit
            if r["slot"]:
                slot_hits.setdefault(r["slot"], []).append(hit)
        if n:
            per_ticket.append((date, got, n))
            if got == n:
                cashed += 1
        save_cache(cache)

    print(f"legs graded: {tot_legs}  (unmatched names skipped: {missing})")
    print(f"PER-LEG HIT RATE: {tot_hit/tot_legs:.3f}" if tot_legs else "no legs")
    print(f"TICKETS CASHED (all legs): {cashed}/{len(per_ticket)}")
    print()
    print("distribution of legs hit per ticket:")
    from collections import Counter
    c = Counter(f"{g}/{n}" for _d, g, n in per_ticket)
    for k in sorted(c, key=lambda x: (-int(x.split('/')[0]))):
        print(f"   {k:7} {c[k]:3}  {'#'*c[k]}")
    print()
    print("realized hit rate by lineup slot (all graded legs):")
    for s in sorted(slot_hits):
        v = slot_hits[s]
        print(f"   slot {s}: {sum(v)/len(v):.3f}  (n={len(v)})")

    if per_ticket:
        import statistics
        avg = statistics.mean(g / n for _d, g, n in per_ticket)
        print(f"\nmean fraction of legs hitting: {avg:.3f}")
        for k in (3, 4, 5, 6, 7, 8, 11):
            p = (tot_hit / tot_legs) ** k if tot_legs else 0
            print(f"   independent-model P(all {k:2} legs) at that rate: {p*100:5.2f}%")


if __name__ == "__main__":
    main()
