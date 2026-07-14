#!/usr/bin/env python3
"""Build the Straight-of-the-Day history used by the streak / last-7 tracker.

Scans preview/archive/*.html plus the current sheet (index.html) for the
"Worst Pickz Straights of the Day" picks (O0.5 and O1.5 sides), settles each
pick against the MLB Stats API (O0.5 = 1+ HR, O1.5 = 2+ HR), then:

  * writes preview/data/straights-history.json
  * embeds the same JSON into index.html and preview/index.html inside
    <script type="application/json" id="straights-history-data">

Already-settled results are cached in the JSON, so reruns only hit the API
for new/pending dates. Local-only: does not commit or push.
"""
from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
ARCHIVE_DIR = ROOT / "preview" / "archive"
CURRENT_SHEET = ROOT / "index.html"
HTML_TARGETS = [ROOT / "index.html", ROOT / "preview" / "index.html"]
JSON_OUT = ROOT / "preview" / "data" / "straights-history.json"

MLB_API = "https://statsapi.mlb.com/api/v1"
SETTLED = {"win", "loss", "void"}

TEAM_FROM_ABBR = {
    "ARI": "Arizona Diamondbacks", "ATL": "Atlanta Braves", "BAL": "Baltimore Orioles",
    "BOS": "Boston Red Sox", "CHC": "Chicago Cubs", "CIN": "Cincinnati Reds",
    "CLE": "Cleveland Guardians", "COL": "Colorado Rockies", "CWS": "Chicago White Sox",
    "CHW": "Chicago White Sox", "DET": "Detroit Tigers", "HOU": "Houston Astros",
    "KC": "Kansas City Royals", "LAA": "Los Angeles Angels", "LAD": "Los Angeles Dodgers",
    "MIA": "Miami Marlins", "MIL": "Milwaukee Brewers", "MIN": "Minnesota Twins",
    "NYM": "New York Mets", "NYY": "New York Yankees", "ATH": "Athletics", "OAK": "Athletics",
    "PHI": "Philadelphia Phillies", "PIT": "Pittsburgh Pirates", "SD": "San Diego Padres",
    "SDP": "San Diego Padres", "SEA": "Seattle Mariners", "SF": "San Francisco Giants",
    "STL": "St. Louis Cardinals", "TB": "Tampa Bay Rays", "TEX": "Texas Rangers",
    "TOR": "Toronto Blue Jays", "WSH": "Washington Nationals", "WAS": "Washington Nationals",
}

SIDE_SPECS = {
    "o05": {
        "tag": r"Over 0\.5 HR Straight",
        "line": r" - Over 0\.5 homerun",
        "min_hr": 1,
    },
    "o15": {
        "tag": r"Over 1\.5 HR Straight",
        "line": r" - Over 1\.5 homeruns?",
        "min_hr": 2,
    },
}

MATCHUP_RE = re.compile(r"^[A-Z]{2,4}\s*@\s*[A-Z]{2,4}$")


def normalize_player(name: str) -> str:
    s = re.sub(r"\s*\([LRS]\)\s*$", "", name or "", flags=re.I).strip()
    s = re.sub(r",?\s*(jr\.?|sr\.?|iii|ii|iv)\s*$", "", s, flags=re.I).strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", s.lower().replace(".", "")).strip()


def api_team_match(api_name: str, abbr: str) -> bool:
    full = TEAM_FROM_ABBR.get(abbr)
    if not full or not api_name:
        return False
    a, f = api_name.lower(), full.lower()
    if a == f:
        return True
    if abbr == "ATH" and "athletic" in a:
        return True
    return f.split()[-1] in a


def extract_side(html_text: str, side: str) -> dict | None:
    """Pull {player, matchup} for one straight side out of a sheet's HTML."""
    spec = SIDE_SPECS[side]
    card_re = re.compile(
        r'<span class="straight-pick-tag">' + spec["tag"] + r"</span>(?P<body>.*?)Straight to Gambly",
        re.S,
    )
    m = card_re.search(html_text)
    if not m:
        return None
    body = m.group("body")
    player = None
    pm = re.search(
        r"data-goblin-gambly-lines='\[&quot;(?P<p>.+?)" + spec["line"] + r"&quot;\]'",
        body,
    )
    if pm:
        player = html.unescape(pm.group("p")).strip()
    matchup = ""
    mm = re.search(r'<span class="straight-pick-meta">(?P<meta>.*?)</span>', body, re.S)
    if mm:
        meta = html.unescape(re.sub(r"<[^>]+>", "", mm.group("meta")))
        for seg in re.split(r"[·\u00b7]", meta):
            seg = seg.strip()
            if MATCHUP_RE.match(seg):
                matchup = seg
    if not player:
        return None
    return {"player": player, "matchup": matchup}


def sheet_date_from_meta(html_text: str) -> str | None:
    m = re.search(r'<meta name="sheet-date" content="(\d{4}-\d{2}-\d{2})"', html_text)
    return m.group(1) if m else None


def get_json(session: requests.Session, path_query: str) -> dict:
    res = session.get(MLB_API + path_query, timeout=30)
    res.raise_for_status()
    return res.json()


def schedule_games(session, cache: dict, ymd: str) -> list:
    if ymd not in cache:
        data = get_json(session, f"/schedule?sportId=1&date={ymd}")
        games = []
        for d in data.get("dates") or []:
            games.extend(d.get("games") or [])
        cache[ymd] = games
    return cache[ymd]


def hr_line_from_boxscore(box: dict, player: str) -> dict | None:
    want = normalize_player(player)
    for side in ("away", "home"):
        players = (((box.get("teams") or {}).get(side) or {}).get("players")) or {}
        for pl in players.values():
            full = ((pl.get("person") or {}).get("fullName")) or ""
            if normalize_player(full) != want:
                continue
            batting = ((pl.get("stats") or {}).get("batting")) or {}
            if not batting:
                continue
            return {
                "pa": int(batting.get("plateAppearances") or 0),
                "hr": int(batting.get("homeRuns") or 0),
            }
    return None


def resolve_pick(session, sched_cache, box_cache, ymd: str, pick: dict, min_hr: int) -> dict:
    """Settle a straight pick. Returns {result, hr?} — mirrors the sheet's JS rules."""
    matchup = (pick.get("matchup") or "").strip()
    mm = re.match(r"^([A-Za-z]+)\s*@\s*([A-Za-z]+)$", matchup)
    if not mm:
        return {"result": "void", "note": "bad matchup"}
    away, home = mm.group(1).upper(), mm.group(2).upper()
    games = schedule_games(session, sched_cache, ymd)
    matches = [
        g for g in games
        if api_team_match(((g.get("teams") or {}).get("away") or {}).get("team", {}).get("name", ""), away)
        and api_team_match(((g.get("teams") or {}).get("home") or {}).get("team", {}).get("name", ""), home)
    ]
    if not matches:
        return {"result": "void", "note": "no game"}
    def detailed(g):
        return str(((g.get("status") or {}).get("detailedState")) or "").lower()
    if all(re.search(r"postponed|cancelled|canceled", detailed(g)) for g in matches):
        return {"result": "void", "note": "postponed"}
    finals = [g for g in matches if ((g.get("status") or {}).get("abstractGameState")) == "Final"]
    pool = finals or matches
    pool.sort(key=lambda g: g.get("gameNumber") or 1)
    g = pool[0]
    if ((g.get("status") or {}).get("abstractGameState")) != "Final":
        return {"result": "pending"}
    pk = g.get("gamePk")
    if pk not in box_cache:
        box_cache[pk] = get_json(session, f"/game/{pk}/boxscore")
    line = hr_line_from_boxscore(box_cache[pk], pick["player"])
    if line is None:
        return {"result": "void", "note": "player not in box"}
    if line["pa"] <= 0:
        return {"result": "void", "note": "no PA", "hr": line["hr"]}
    return {"result": "win" if line["hr"] >= min_hr else "loss", "hr": line["hr"]}


def load_existing() -> dict:
    if JSON_OUT.exists():
        try:
            data = json.loads(JSON_OUT.read_text(encoding="utf-8"))
            return {e["date"]: e for e in data.get("entries", []) if e.get("date")}
        except Exception:
            pass
    return {}


def embed_into_html(payload_json: str) -> None:
    tag = f'<script type="application/json" id="straights-history-data">{payload_json}</script>'
    for target in HTML_TARGETS:
        text = target.read_text(encoding="utf-8")
        if 'id="straights-history-data"' in text:
            new_text = re.sub(
                r'<script type="application/json" id="straights-history-data">.*?</script>',
                lambda _: tag,
                text,
                count=1,
                flags=re.S,
            )
        else:
            anchor = '    <meta property="og:title"'
            if anchor not in text:
                print(f"WARNING: no insertion anchor in {target}", file=sys.stderr)
                continue
            new_text = text.replace(anchor, f"    {tag}\n{anchor}", 1)
        if new_text != text:
            target.write_text(new_text, encoding="utf-8")
            print(f"embedded history into {target.relative_to(ROOT)}")
        else:
            print(f"no change for {target.relative_to(ROOT)}")


def main() -> int:
    sources: list[tuple[str, Path]] = []
    for f in sorted(ARCHIVE_DIR.glob("*.html")):
        m = re.match(r"^(\d{4}-\d{2}-\d{2})\.html$", f.name)
        if m:
            sources.append((m.group(1), f))
    cur_text = CURRENT_SHEET.read_text(encoding="utf-8")
    cur_date = sheet_date_from_meta(cur_text)
    if cur_date and cur_date not in {d for d, _ in sources}:
        sources.append((cur_date, CURRENT_SHEET))
    sources.sort(key=lambda t: t[0])

    existing = load_existing()
    session = requests.Session()
    session.headers["User-Agent"] = "worstpickz-straights-tracker/1.0"
    sched_cache: dict = {}
    box_cache: dict = {}
    today = datetime.now().strftime("%Y-%m-%d")

    entries = []
    api_calls = 0
    for ymd, path in sources:
        text = cur_text if path == CURRENT_SHEET else path.read_text(encoding="utf-8")
        entry = {"date": ymd}
        has_side = False
        for side, spec in SIDE_SPECS.items():
            pick = extract_side(text, side)
            if not pick:
                continue
            has_side = True
            prev = (existing.get(ymd) or {}).get(side) or {}
            if (
                prev.get("result") in SETTLED
                and normalize_player(prev.get("player", "")) == normalize_player(pick["player"])
            ):
                entry[side] = {**pick, "result": prev["result"], **({"hr": prev["hr"]} if "hr" in prev else {})}
                continue
            if ymd >= today:
                entry[side] = {**pick, "result": "pending"}
                continue
            try:
                res = resolve_pick(session, sched_cache, box_cache, ymd, pick, spec["min_hr"])
                api_calls += 1
            except Exception as err:
                print(f"WARNING {ymd} {side}: API error {err}", file=sys.stderr)
                res = {"result": "pending"}
            entry[side] = {**pick, **res}
        if has_side:
            entries.append(entry)

    payload = {
        "version": 1,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entries": entries,
    }
    JSON_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {JSON_OUT.relative_to(ROOT)} ({len(entries)} dates)")

    embed_into_html(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))

    def icon(r):
        return {"win": "W", "loss": "L", "void": "-", "pending": "?"}.get(r, "?")

    print("\ndate        O0.5                             O1.5")
    for e in entries:
        o05 = e.get("o05") or {}
        o15 = e.get("o15") or {}
        print(
            f"{e['date']}  [{icon(o05.get('result'))}] {o05.get('player', '—'):28.28}"
            f"  [{icon(o15.get('result'))}] {o15.get('player', '—')}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
