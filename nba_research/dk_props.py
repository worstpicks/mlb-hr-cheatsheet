"""DraftKings player-prop prices for a slate, from ESPN's public odds API -- no key.

    python -m nba_research.dk_props --date 2026-10-20

ESPN carries DraftKings' board for every game on its core API (provider 100):
milestones ("2+ steals", one price each -- an Over 1.5), the main over/under pair
at the book's own line, and First Basket. Saved as data/nba-dk-props-<date>.json
with the time it was captured, so a sheet always shows the prices it was built on.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SLATES = ROOT / "preview" / "data"
CORE = "https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/events/{id}/competitions/{id}/odds/100/propBets?lang=en&region=us&limit=1000&page={page}"

# ESPN's market names → the research tab's stat keys
MILESTONES = {"Points Milestones": "pts", "Rebounds Milestones": "reb", "Assists Milestones": "ast",
              "3-Point Field Goals Milestones": "threem", "Steals Milestones": "stl", "Blocks Milestones": "blk",
              "Points + Assists + Rebounds Milestones": "pra", "Points + Rebounds Milestones": "pr",
              "Points + Assists Milestones": "pa"}
TOTALS = {"Total Points": "pts", "Total Rebounds": "reb", "Total Assists": "ast", "Total 3-Point Field Goals": "threem",
          "Total Steals": "stl", "Total Blocks": "blk", "Total Points, Rebounds, and Assists": "pra",
          "Total Points and Rebounds": "pr", "Total Points and Assists": "pa", "Total Assists and Rebounds": "ra",
          "Total Steals and Blocks": "stocks"}
SPECIALS = {"First Basket": "first_basket", "1st Team FG Scorer": "team_first_fg",
            "To Record a Double Double": "dd", "To Record a Triple Double": "td"}


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz NBA Prop Shop/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _american(item: dict) -> int | None:
    try:
        return int(str(((item.get("odds") or {}).get("american") or {}).get("value")).replace("+", ""))
    except (TypeError, ValueError):
        return None


def implied(american: int) -> float:
    """The chance a price asks for, vig and all."""
    return -american / (-american + 100) if american < 0 else 100 / (american + 100)


def ladders(entries: list[tuple[int, int]]) -> list[dict]:
    """Split one market's "N+" prices into ladders. DraftKings' feed files a
    first-quarter ladder under the full-game name (Harper 10/20: 3+ rebounds at
    -710 and again at +290). A price joins a ladder that has no price at its N yet
    and stays in order with it -- more needed, longer odds -- and of those, the one
    with a rung nearest its N, since a ladder climbs one step at a time."""
    out: list[dict] = []
    for n, price in entries:
        p = implied(price)
        fits = [lad for lad in out if str(n) not in lad and all(
            (implied(q) >= p) if int(k) < n else (implied(q) <= p) for k, q in lad.items())]
        if fits:
            min(fits, key=lambda lad: min(abs(int(k) - n) for k in lad))[str(n)] = price
        else:
            out.append({str(n): price})
    return out


def full_game(lads: list[dict], main: dict | None) -> dict:
    """The full-game ladder: the one whose price at the main line's milestone
    matches the main over/under (the over is the pair's first price), else the longest."""
    if len(lads) == 1:
        return lads[0]
    if main and main.get("prices"):
        need = str(int(float(main["line"])) + 1)
        over = implied(main["prices"][0])
        near = [l for l in lads if need in l and abs(implied(l[need]) - over) <= 0.06]
        if near:
            return near[0]
    return max(lads, key=len) if lads else {}


def board(items: list[dict]) -> dict:
    """{athlete id: {"milestones": {stat: {"N": price}}, "totals": {stat: {"line", "prices"}}, specials}}"""
    out: dict = {}
    raw: dict = {}
    for it in items:
        m = re.search(r"athletes/(\d+)", (it.get("athlete") or {}).get("$ref", ""))
        price = _american(it)
        if not m or price is None:
            continue
        who = out.setdefault(m.group(1), {"milestones": {}, "totals": {}})
        name = (it.get("type") or {}).get("name", "")
        target = ((it.get("current") or {}).get("target") or {}).get("value")
        if name in MILESTONES and target is not None:
            raw.setdefault((m.group(1), MILESTONES[name]), []).append((int(target), price))
        elif name in TOTALS and target is not None:
            t = who["totals"].setdefault(TOTALS[name], {"line": target, "prices": []})
            if t["line"] == target:
                t["prices"].append(price)
        elif name in SPECIALS:
            who[SPECIALS[name]] = price
    for (aid, stat), entries in raw.items():
        lads = ladders(entries)
        out[aid]["milestones"][stat] = full_game(lads, out[aid]["totals"].get(stat))
        if len(lads) > 1:
            out[aid].setdefault("partial", {})[stat] = [l for l in lads if l is not out[aid]["milestones"][stat]]
    return out


def over_price(entry: dict | None, stat: str, line: float) -> tuple[int | None, str]:
    """DraftKings' price for Over `line`: the "N+" milestone, else the over side of
    the main pair when the line is the book's own. ("", None) when neither is posted."""
    if not entry:
        return None, ""
    need = int(line) + 1  # Over 1.5 is 2+
    price = ((entry.get("milestones") or {}).get(stat) or {}).get(str(need))
    if price is not None:
        return price, f"{need}+ milestone"
    main = (entry.get("totals") or {}).get(stat)
    if main and float(main["line"]) == float(line) and len(main["prices"]) == 2:
        # ESPN lists the over first on every pair checked against its milestone
        return main["prices"][0], "main line"
    return None, ""


def fetch(date: str) -> Path:
    slate = json.loads((SLATES / f"nba-research-{date}.json").read_text(encoding="utf-8"))
    games = {}
    for g in slate.get("games") or []:
        items = []
        for page in range(1, 6):
            got = _get(CORE.format(id=g["id"], page=page))
            items += got.get("items") or []
            if page >= (got.get("pageCount") or 1):
                break
        games[g["id"]] = {"label": g.get("label", ""), "players": board(items), "items": len(items)}
        print(f"[dk_props] {g.get('label')}: {len(items)} prices for {len(games[g['id']]['players'])} players")
    out = {"date": date, "book": "DraftKings", "source": "ESPN core odds API (provider 100)",
           "captured": datetime.now(timezone.utc).isoformat(timespec="minutes"), "games": games}
    path = DATA / f"nba-dk-props-{date}.json"
    path.write_text(json.dumps(out, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
    print(f"[dk_props] wrote {path.relative_to(ROOT)}")
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", required=True)
    fetch(ap.parse_args().date)


if __name__ == "__main__":
    main()
