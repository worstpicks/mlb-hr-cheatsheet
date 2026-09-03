#!/usr/bin/env python3
"""Build 2026-09-03 sheet from imported CSVs and user prop list."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

from game_row_enrich import alias_weather_game_key
from csv_slate_meta import (
    derive_games_from_csv,
    pitcher_chip_name,
    manifest_matchup_files,
    name_lookup_key,
    read_batter_rows,
    read_matchup_header,
)
from hr_score_model import batter_split, score_from_model
from sheet_data import load_pitcher_risk, resolve_pitcher

ROOT = Path(__file__).resolve().parent
DATE = "2026-09-03"
OUT = ROOT / "build-sheet-2026-09-03.py"
BUM_RISK_MIN = 0.95

# Arms whose HR-risk row was carried from an earlier slate by
# build-synthetic-0903-matchups.py. Nothing is carried today: every arm the sheet
# lists has its own same-day PropFinder risk row except Randy Vasquez, who has no
# prior score anywhere and gets his real measured lane instead.
CARRIED_RISK: dict[str, str] = {}

RAW_PROPS = [
    "Bryan Reynolds⭐",
    "Oneil Cruz💎",
    "Esmerlyn Valdez",
    "Brandon Lowe💎",
    "Rafael Devers⭐",
    "Drew Gilbert",
    "Andrew Knizner",
    "Bryce Eldridge",
    "Nathaniel Lowe⭐",
    "Chase DeLauter",
    "Brayan Roochio",
    "Brandon Valenzuela",
    "Jesus Sanchez",
    "Andres Gimenez",
    "Nelson Velazquez💎",
    "Daulton Varsho",
    "Yainer Diaz",
    "Christian Walker",
    "Tristan Peters",
    "Munetaka Murakami",
    "Andrew Benintendi⭐",
    "Pete Crow Armstrong⭐",
    "Michael Busch💎",
    "Nico Hoerner💎",
    "Jackson Chourio⭐",
    "Joey Ortiz",
    "Jake Bauers💎",
    "Luis Lara",
    "Christian Yelich",
    "Luis Robert💎",
    "Coby Mayo",
    "Pete Alonso",
    "Mickey Gasper⭐",
    "Adley Rutschman",
    "Roman Anthony💎",
    "Jarren Duran💎",
    "Carter Jensen⭐",
    "Jac Caglianone",
    "Vinnie Pasquantino",
    "Heriberto Hernandez⭐",
    "Graham Pauley💎",
    "Kyle Stowers💎",
    "Brandon Nimmo💎",
    "Corey Seager⭐",
    "Elias Diaz",
    "Jake Burger⭐",
    "Ezequiel Duran💎",
    "Justin Foscue",
    "Yandy Diaz⭐",
    "Junior Caminero💎",
    "Jonathan Aranda",
    "Cal Raleigh⭐",
    "Dominic Canzone💎",
    "Henry Bolte💎",
    "Lawrence Butler",
    "Teoscar Hernandez⭐",
    "Dalton Rushing",
    "Freddie Freeman⭐",
    "Will Smith⭐",
    "Ramon Urias💎",
    "Joshua Baez",
    "Nolan Gorman💎",
]

ALIASES = {
    # prop-list typos
    "Brayan Roochio": "Brayan Rocchio",
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuna": "Ronald Acuna Jr.",
    "Jazz Chisholm Jr.": "Jazz Chisholm Jr.",
    "Nathaniel Lowe": "Nathaniel Lowe",
    "Travis d'Arnaud": "Travis d'Arnaud",
    "Tyler O'Neill": "Tyler O'Neill",
    "Jonny DeLuca": "Jonny DeLuca",
    "Kazuma Okamoto": "Kazuma Okamoto",
    "Munetaka Murakami": "Munetaka Murakami",
    "Vinnie Pasquantino": "Vinnie Pasquantino",
    "Jac Caglianone": "Jac Caglianone",
    "Abimelec Ortiz": "Abimelec Ortiz",
    "Nelson Velazquez": "Nelson Velazquez",
    "Samuel Basallo": "Samuel Basallo",
    "Bryce Eldridge": "Bryce Eldridge",
    "Jung Hoo Lee": "Jung Hoo Lee",
    "Daz Cameron": "Daz Cameron",
    "Weston Wilson": "Weston Wilson",
    "Julio Rodriguez": "Julio Rodriguez",
    "Randy Arozarena": "Randy Arozarena",
    "Jimmy Crooks": "Jimmy Crooks",
    "Brian Serven": "Brian Serven",
    "Amed Rosario": "Amed Rosario",
    "Jarred Kelenic": "Jarred Kelenic",
    "Randal Grichuk": "Randal Grichuk",
    "Lane Thomas": "Lane Thomas",
    "Taylor Trammell": "Taylor Trammell",
    "Daulton Varsho": "Daulton Varsho",
}

MANUAL_BATTER_ROWS: dict[str, dict] = {}

# Both Max Muncys are listed props today and the prop list tags each with its club,
# so each row carries its own per-prop game override and no global pin is needed.
BATTER_GAME_OVERRIDES: dict[str, str] = {}

PROP_GAME_OVERRIDES: dict[str, str] = {}

# Boston at New York is a doubleheader and PropFinder exported all four arms under the
# one "BOS @ NYY" key. Arizona at San Francisco is also a doubleheader, but only game 1
# was exported, so it stays a single game.
# No doubleheader on this slate.
DOUBLEHEADER_SPECS: dict[str, dict[str, dict]] = {}


PROBABLE_OVERRIDES: dict[str, dict] = {}

PITCHER_HAND = {
    # named by the sheet owner / after the export, so not in today's MLB probables
    "Quinn Mathews": "L",
    "Kade Anderson": "L",
    # 8/20 LHP
    "Ian Seymour": "L",
    "Anthony Kay": "L",
    "Gage Jump": "L",
    "Robert Gasser": "L",
    "Andrew Alvarez": "L",
    # 8/20 RHP
    "Michael McGreevy": "R",
    "Brady Singer": "R",
    "Landen Roupp": "R",
    "Gavin Williams": "R",
    "Shane Bieber": "R",
    "Grant Holmes": "R",
    "Randy Dobnak": "R",
    "George Kirby": "R",
    "Gerrit Cole": "R",
    "Kyle Bradish": "R",
    "Jacob deGrom": "R",
    "Grayson Rodriguez": "R",
    "Peter Lambert": "R",
}


def load_mlb_pitcher_hands(sheet_date: str) -> dict[str, str]:
    """Probable -> L/R from the MLB Stats API, cached per slate date.

    PITCHER_HAND is a hand-maintained dict and pitcher_hand_label() defaulted every
    unknown arm to "R" -- so ten of this slate's fifteen games named a left-hander as
    a righty in the game title. Handedness is a fact, not a judgement call: read it.
    """
    cache = ROOT / "data" / f"pitcher-hands-{sheet_date}.json"
    if cache.is_file():
        try:
            return json.loads(cache.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
    import urllib.request

    out: dict[str, str] = {}
    try:
        url = (
            "https://statsapi.mlb.com/api/v1/schedule?sportId=1"
            f"&date={sheet_date}&hydrate=probablePitcher"
        )
        sched = json.load(urllib.request.urlopen(url, timeout=30))
        ids = {
            (t.get("probablePitcher") or {}).get("id"): (t.get("probablePitcher") or {}).get("fullName")
            for d in sched.get("dates", [])
            for g in d.get("games", [])
            for t in g["teams"].values()
        }
        ids.pop(None, None)
        for pid, name in ids.items():
            person = json.load(
                urllib.request.urlopen(f"https://statsapi.mlb.com/api/v1/people/{pid}", timeout=30)
            )
            code = person["people"][0].get("pitchHand", {}).get("code")
            if code:
                out[name] = code
    except Exception as exc:  # offline / API hiccup -> fall back to the static map
        print(f"  WARN could not read pitcher hands from MLB ({exc}); using static map")
        return {}
    if out:
        cache.write_text(json.dumps(out, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
    return out


MLB_PITCHER_HAND: dict[str, str] = {}


def lookup_hand_by_name(full_name: str) -> str | None:
    """Handedness for an arm MLB does not list among today's probables.

    Arms named by the sheet's owner while MLB still shows TBD never appear in the
    schedule hydrate, so they fell through to the "R" default -- which put a lefty
    (Matthew Liberatore) on the board as a righty. Resolve them by name instead,
    restricted to players whose primary position is pitcher.
    """
    import urllib.parse
    import urllib.request

    try:
        url = "https://statsapi.mlb.com/api/v1/people/search?names=" + urllib.parse.quote(full_name)
        people = json.load(urllib.request.urlopen(url, timeout=30)).get("people", [])
    except Exception:
        return None
    hands = {
        person["pitchHand"]["code"]
        for person in people
        if (person.get("primaryPosition") or {}).get("code") == "1"
        and (person.get("pitchHand") or {}).get("code")
    }
    # Only trust an unambiguous answer; two pitchers of the same name means guessing.
    return hands.pop() if len(hands) == 1 else None


def pitcher_hand_label(full_name: str) -> str:
    hand = MLB_PITCHER_HAND.get(full_name) or PITCHER_HAND.get(full_name)
    if hand:
        return hand
    # accent-insensitive retry (the API spells Martin Perez with accents)
    key = name_lookup_key(full_name)
    for src in (MLB_PITCHER_HAND, PITCHER_HAND):
        for k, v in src.items():
            if name_lookup_key(k) == key:
                return v
    looked_up = lookup_hand_by_name(full_name)
    if looked_up:
        MLB_PITCHER_HAND[full_name] = looked_up
        print(f"  pitcher hand for {full_name}: {looked_up} (MLB name lookup)")
        return looked_up
    print(f"  WARN no handedness found for {full_name}; defaulting to R")
    return "R"


def apply_probable_overrides(games: dict[str, dict]) -> None:
    for key, ov in PROBABLE_OVERRIDES.items():
        gm = games[key]
        sp_key = f"{ov['side']}_sp"
        full_key = f"{ov['side']}_sp_full"
        old = ov["from"]
        if gm[sp_key] != old:
            print(f"WARN {key}: expected {old} as {ov['side']} SP, got {gm[sp_key]}")
        gm[sp_key] = ov["to"]
        gm[full_key] = ov["full"]
        for row in gm["batters"].values():
            if row["vs"] == old:
                row["vs"] = ov["to"]


def split_doubleheader(games: dict[str, dict]) -> None:
    """Split a game key that carries all four arms of a doubleheader into G1 and G2.

    derive_games_from_csv keys purely on "AWY @ HOM", so a doubleheader arrives as one
    entry whose away_sp/home_sp are whichever file happened to be read last and whose
    batter rows are silently merged across both games. This used to be hardcoded to
    "STL @ CIN"; it is driven by DOUBLEHEADER_SPECS now so any slate's doubleheader
    splits correctly instead of quietly collapsing into one wrong game.
    """
    for base, specs in DOUBLEHEADER_SPECS.items():
        if base not in games:
            continue
        origin = games.pop(base)
        for gkey, spec in specs.items():
            gm = {
                "key": gkey,
                "away": origin["away"],
                "home": origin["home"],
                "away_sp": pitcher_chip_name(spec["away_sp_full"]),
                "home_sp": pitcher_chip_name(spec["home_sp_full"]),
                "away_sp_full": spec["away_sp_full"],
                "home_sp_full": spec["home_sp_full"],
                "batters": {},
            }
            for fname in spec["files"]:
                path = ROOT / "data" / fname
                hdr = read_matchup_header(path)
                for b in read_batter_rows(path):
                    gm["batters"][name_lookup_key(b["name"])] = {
                        **b,
                        "vs": pitcher_chip_name(hdr["pitcher"]),
                        "vs_full": hdr["pitcher"],
                        "file": fname,
                    }
            games[gkey] = gm


TEAM_TO_GAME: dict[str, str] = {}


def parse_prop_label(raw: str) -> tuple[str, bool, bool, str | None]:
    clean = raw.strip()
    fav = False
    while "⭐" in clean:
        fav = True
        clean = clean.replace("⭐", "", 1).strip()
    gem = "💎" in clean
    if gem:
        clean = clean.replace("💎", "", 1).strip()
    game_override = None
    # "Name(TEAM)" disambiguates two players who share a name (two Max Muncys today).
    # The team -> game map is built from THIS slate in main(); the previous version
    # hardcoded "LAD @ COL" / "ATH @ KC" from an old slate and silently mis-assigned
    # the prop on every day those pairings were not the real matchups.
    m = re.search(r"\((?!G[12]\))([A-Z]{2,3})\)\s*$", clean)
    if m:
        team = m.group(1).upper()
        clean = clean[: m.start()].strip()
        game_override = TEAM_TO_GAME.get(team)
        if game_override is None:
            raise SystemExit(
                f"prop tagged ({team}) but that club is not on this slate: {raw!r}"
            )
    dh = re.search(r"\(G([12])\)\s*$", clean, re.I)
    if dh:
        # Which doubleheader is implied comes from DOUBLEHEADER_SPECS, not a hardcoded
        # "STL @ CIN" left over from an old slate. Exactly one doubleheader may be
        # split at a time, so an ambiguous tag stops the build rather than guessing.
        bases = list(DOUBLEHEADER_SPECS)
        if len(bases) != 1:
            raise SystemExit(
                f"(G{dh.group(1)}) tag needs exactly one split doubleheader, found {bases}"
            )
        game_override = f"{bases[0]} (G{dh.group(1)})"
        clean = re.sub(r"\s*\(G[12]\)\s*$", "", clean, flags=re.I).strip()
    clean = ALIASES.get(clean, clean)
    return clean, fav, gem, game_override


def build_game_title(gm: dict) -> str:
    away_full = gm["away_sp_full"]
    home_full = gm["home_sp_full"]
    return (
        f"{gm['key']} - {away_full} ({pitcher_hand_label(away_full)}, {gm['away']}) "
        f"vs {home_full} ({pitcher_hand_label(home_full)}, {gm['home']})"
    )


def blast_from_stats(hr: int, near: int, ev: float | None, barrel: float | None) -> str | None:
    ev = ev or 0.0
    barrel = barrel or 0.0
    if hr >= 2 or (hr + near >= 5) or (ev >= 97 and barrel >= 20):
        return "high"
    if hr >= 1 or near >= 2 or ev >= 92 or barrel >= 15:
        return "good"
    return None


def display(name: str, hand: str) -> str:
    return f"{name} ({hand})"


def emoji_string(
    is_fav: bool,
    is_gem: bool,
    ev: float | None,
    score: int,
    blast: str | None,
) -> str:
    em: list[str] = []
    moonshot = score >= 88 or blast == "high"
    if ev is not None and ev >= 100:
        em.append("🚀")
    if is_fav:
        em.append("⭐")
    if moonshot:
        em.extend(["🌕", "💣"])
    if is_gem:
        em.append("💎")
    seen = set()
    dedup = []
    for x in em:
        if x not in seen:
            seen.add(x)
            dedup.append(x)
    return " ".join(dedup)


def core_reason(hr: int, near: int, ev: float, barrel: float) -> str:
    parts = [f"{hr} HR"]
    if near:
        parts.append(f"{near} near-HR")
    parts.append(f"{ev:.1f} mph EV")
    if barrel:
        parts.append(f"{barrel:.1f}% barrels")
    return ", ".join(parts)


def _pct_value(text: str | None) -> int:
    if not text:
        return 0
    m = re.search(r"([+-]?\d+)", text)
    return int(m.group(1)) if m else 0


def _time_sort_key(t: str) -> tuple[int, str]:
    m = re.match(r"^(\d{1,2}):(\d{2})", (t or "").strip())
    if not m:
        return (99_999, t or "")
    hour = int(m.group(1))
    minute = int(m.group(2))
    if 1 <= hour <= 11:
        hour += 12
    return (hour * 60 + minute, t or "")


def load_park_context(date: str) -> dict[str, dict]:
    data_dir = ROOT / "data"
    path = data_dir / f"ParkFactors_{date}.csv"
    if not path.exists():
        matches = sorted(data_dir.glob(f"ParkFactors_{date}*.csv"))
        if matches:
            path = matches[0]
    by_game: dict[str, list[tuple[str, dict]]] = {}
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = " ".join((row.get("Game") or "").replace("  ", " ").split())
            if not key:
                continue
            time_val = (row.get("Time") or "").strip()
            entry = {
                "hr_pct": _pct_value(row.get("HR %")),
                "hr_weather": _pct_value(row.get("HR % Weather")),
                "hr_stadium": _pct_value(row.get("HR % Stadium")),
            }
            by_game.setdefault(key, []).append((time_val, entry))

    # Keyed by the Ballpark Pal spelling ("CHW @ CHC"); callers come in with the
    # sheet spelling ("CWS @ CHC") and are aliased forward by effective_park_key.
    # The old local alias table enumerated opponent pairs, so any matchup that had
    # not been seen before silently lost its park row.
    out: dict[str, dict] = {}
    for key, entries in by_game.items():
        entries.sort(key=lambda e: _time_sort_key(e[0]))
        out[key] = entries[0][1]
        if len(entries) == 1:
            continue
        for i, (_time_val, entry) in enumerate(entries, 1):
            out[f"{key} (G{i})"] = entry

    return out


_MLB_LANE_CACHE: dict[str, str | None] = {}


def mlb_season_lane(full_name: str) -> str | None:
    """This season's MLB batting-average-against, as a .xxx string, or None."""
    if full_name in _MLB_LANE_CACHE:
        return _MLB_LANE_CACHE[full_name]
    import urllib.parse
    import urllib.request

    avg = None
    try:
        url = "https://statsapi.mlb.com/api/v1/people/search?names=" + urllib.parse.quote(full_name)
        people = [
            p
            for p in json.load(urllib.request.urlopen(url, timeout=30)).get("people", [])
            if (p.get("primaryPosition") or {}).get("code") == "1"
        ]
        if len(people) == 1:
            stats = json.load(
                urllib.request.urlopen(
                    f"https://statsapi.mlb.com/api/v1/people/{people[0]['id']}"
                    f"/stats?stats=season&season={DATE[:4]}&group=pitching",
                    timeout=30,
                )
            )
            for st in stats.get("stats", []):
                for sp in st.get("splits", []):
                    avg = sp["stat"].get("avg") or avg
    except Exception:
        avg = None
    _MLB_LANE_CACHE[full_name] = avg
    return avg


_DEBUT_CACHE: dict[str, bool] = {}


def is_mlb_debut(full_name: str) -> bool:
    """True only when MLB confirms this arm has never pitched a big-league inning."""
    if full_name in _DEBUT_CACHE:
        return _DEBUT_CACHE[full_name]
    import urllib.parse
    import urllib.request

    verdict = False
    try:
        url = "https://statsapi.mlb.com/api/v1/people/search?names=" + urllib.parse.quote(full_name)
        people = [
            p
            for p in json.load(urllib.request.urlopen(url, timeout=30)).get("people", [])
            if (p.get("primaryPosition") or {}).get("code") == "1"
        ]
        if len(people) == 1:
            stats = json.load(
                urllib.request.urlopen(
                    f"https://statsapi.mlb.com/api/v1/people/{people[0]['id']}"
                    "/stats?stats=career&group=pitching",
                    timeout=30,
                )
            )
            verdict = not [s for st in stats.get("stats", []) for s in st.get("splits", [])]
    except Exception:
        verdict = False
    _DEBUT_CACHE[full_name] = verdict
    return verdict


def load_measured_lanes() -> dict[str, dict]:
    """Folded SP name -> real BAA / HR-9 lane read from that arm's matchup CSV.

    PropFinder's HR-risk export is keyed to the probables it knew about when the
    file was pulled, so an arm named after the export has no risk row at all. The
    sheet still owes the reader a split at the top of the game, and the matchup
    CSV's own Season/vsLHB/vsRHB block is a real measurement -- so use that rather
    than either inventing a risk score or printing nothing.
    """
    out: dict[str, dict] = {}
    for path in manifest_matchup_files(DATE):
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        hdr = read_matchup_header(path)
        pitcher = (hdr.get("pitcher") or "").strip()
        if not pitcher:
            continue
        hdr_i = next(
            (i for i, l in enumerate(lines) if l.split(",")[0].strip() == "SPLIT"), None
        )
        if hdr_i is None:
            continue
        cols = [c.strip() for c in next(csv.reader([lines[hdr_i]]))]
        lane: dict[str, dict] = {}
        for line in lines[hdr_i + 1 :]:
            row = next(csv.reader([line]), None)
            if not row or row[0].strip() not in ("Season", "vsLHB", "vsRHB"):
                break
            lane[row[0].strip()] = dict(zip(cols, row))

        def cell(split: str, col: str) -> float | None:
            try:
                return float((lane.get(split) or {}).get(col, "").strip())
            except (TypeError, ValueError):
                return None

        rec = {
            "baa_lhb": cell("vsLHB", "BAA"),
            "baa_rhb": cell("vsRHB", "BAA"),
            "hr9": cell("Season", "HR/9"),
        }
        if any(v is not None for v in rec.values()):
            out[name_lookup_key(pitcher)] = rec
    return out


def park_for(park_context: dict[str, dict], game_key: str) -> dict | None:
    """Park entry for a sheet game key, tolerating CWS/CHW and WSH/WAS spellings."""
    if game_key in park_context:
        return park_context[game_key]
    return park_context.get(alias_weather_game_key(game_key))


def fade_reason(
    split: float | None,
    risk_overall: float | None,
    hr: int,
    near: int,
    ev: float,
    park_ctx: dict | None,
) -> str:
    parts: list[str] = []
    if split is None or risk_overall is None:
        parts.append("limited split/risk sample")
    else:
        if split <= -0.40:
            parts.append(f"tough split lane ({split:+.2f})")
        elif split < 0:
            parts.append(f"slight split headwind ({split:+.2f})")
        if risk_overall <= -0.40:
            parts.append(f"pitcher suppresses HR ({risk_overall:+.2f})")
        elif risk_overall < 0:
            parts.append(f"pitcher risk below avg ({risk_overall:+.2f})")

    if park_ctx:
        if park_ctx["hr_pct"] <= -5:
            parts.append(f"park/weather net drag ({park_ctx['hr_pct']:+d}%)")
        elif park_ctx["hr_weather"] <= -4:
            parts.append(f"weather carry headwind ({park_ctx['hr_weather']:+d}%)")
        elif park_ctx["hr_stadium"] <= -6:
            parts.append(f"park suppresses carry ({park_ctx['hr_stadium']:+d}%)")

    if hr == 0 and near <= 1:
        parts.append("limited recent HR events")
    if ev < 88:
        parts.append(f"lighter EV form ({ev:.1f} mph)")

    return "; ".join(parts[:2]) if parts else ""


def main() -> int:
    MLB_PITCHER_HAND.update(load_mlb_pitcher_hands(DATE))
    games_csv = {g["key"]: g for g in derive_games_from_csv(DATE)}
    TEAM_TO_GAME.update({g["away"]: g["key"] for g in games_csv.values()})
    TEAM_TO_GAME.update({g["home"]: g["key"] for g in games_csv.values()})
    split_doubleheader(games_csv)
    apply_probable_overrides(games_csv)
    pitcher_risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
    measured_lanes = load_measured_lanes()
    park_context = load_park_context(DATE)

    batter_ctx: dict[str, dict] = {}
    batter_by_game: dict[tuple[str, str], dict] = {}
    for g in games_csv.values():
        for row in g["batters"].values():
            vs = row["vs"]
            vs_full = (row.get("vs_full") or vs).strip()
            if vs in (g["away_sp"], g.get("away_sp_full")) or vs_full == g.get("away_sp_full"):
                team = g["home"]
            elif vs in (g["home_sp"], g.get("home_sp_full")) or vs_full == g.get("home_sp_full"):
                team = g["away"]
            else:
                continue
            entry = {
                "game": g["key"],
                "team": team,
                "opp_sp": vs,  # full name when last-name collides on slate
                "row": row,
            }
            key = name_lookup_key(row["name"])
            batter_by_game[(key, g["key"])] = entry
            batter_ctx[key] = entry

    for mkey, manual in MANUAL_BATTER_ROWS.items():
        if mkey in batter_ctx or any(mkey == k for k, _ in batter_by_game):
            continue
        game_key = manual["game"]
        entry = {
            "game": game_key,
            "team": manual["team"],
            "opp_sp": manual["opp_sp"],
            "row": manual["row"],
        }
        batter_by_game[(mkey, game_key)] = entry
        if mkey not in batter_ctx:
            batter_ctx[mkey] = entry

    fav_keys: set[tuple[str, str]] = set()
    gem_keys: set[tuple[str, str]] = set()
    prop_entries: list[tuple[str, bool, bool, str | None]] = []
    for raw in RAW_PROPS:
        clean, fav, gem, game_override = parse_prop_label(raw)
        prop_entries.append((clean, fav, gem, game_override))

    # A prop name that exists in more than one game silently resolves to whichever
    # game the dict happened to write last. That is arbitrary, so make it loud: any
    # ambiguous name must be pinned in BATTER_GAME_OVERRIDES or carry its own
    # override, or the build stops rather than guessing.
    games_for_name: dict[str, set[str]] = {}
    for (bkey, gkey) in batter_by_game:
        games_for_name.setdefault(bkey, set()).add(gkey)
    ambiguous = [
        name
        for name, _f, _g, override in prop_entries
        if not override
        and name not in BATTER_GAME_OVERRIDES
        and len(games_for_name.get(name_lookup_key(name), ())) > 1
    ]
    if ambiguous:
        raise SystemExit(
            "prop name matches batters in more than one game; pin it in "
            f"BATTER_GAME_OVERRIDES: {ambiguous}"
        )

    missing: list[str] = []
    props: list[tuple] = []
    team_map: dict[str, str] = {}
    for name, is_fav, is_gem, game_override in prop_entries:
        key = name_lookup_key(name)
        if game_override:
            ctx = batter_by_game.get((key, game_override))
        elif name in BATTER_GAME_OVERRIDES:
            ctx = batter_by_game.get((key, BATTER_GAME_OVERRIDES[name]))
        else:
            ctx = batter_ctx.get(key)
        if not ctx:
            missing.append(name)
            continue
        row = ctx["row"]
        hand = row["hand"]
        odds = row["odds"]
        hr = int(row["hr"] or 0)
        near = int(row["near"] or 0)
        ev = float(row["ev"]) if row["ev"] is not None else 0.0
        barrel = float(row["barrel"]) if row["barrel"] is not None else 0.0
        blast = blast_from_stats(hr, near, ev, barrel)
        sp_risk = resolve_pitcher(pitcher_risk, ctx["opp_sp"])
        split = batter_split(hand, sp_risk)
        park_ctx = park_for(park_context, ctx["game"])
        score = score_from_model(
            hr,
            near,
            ev,
            barrel,
            blast,
            split,
            sp_risk["overall"] if sp_risk else None,
            park_ctx["hr_pct"] if park_ctx else None,
        )
        team_map[display(name, hand)] = ctx["team"]
        gkey = ctx["game"]
        if is_fav:
            fav_keys.add((name, gkey))
        if is_gem:
            gem_keys.add((name, gkey))
        props.append(
            (name, hand, odds, score, ctx["opp_sp"], hr, near, ev, barrel, blast, gkey, is_fav, is_gem)
        )

    favs_display = sorted({display(n, next(p[1] for p in props if p[0] == n and p[11])) for n, _g in fav_keys})
    gems_display = sorted({display(n, next(p[1] for p in props if p[0] == n and p[12])) for n, _g in gem_keys})

    game_meta: list[dict] = []
    bum_matchups: set[tuple[str, str]] = set()
    for g in sorted(games_csv.values(), key=lambda x: x["key"]):
        away_r = resolve_pitcher(pitcher_risk, g["away_sp_full"]) or resolve_pitcher(pitcher_risk, g["away_sp"])
        home_r = resolve_pitcher(pitcher_risk, g["home_sp_full"]) or resolve_pitcher(pitcher_risk, g["home_sp"])
        if away_r and away_r["overall"] >= BUM_RISK_MIN:
            bum_matchups.add((g["key"], g["away_sp"]))
        if home_r and home_r["overall"] >= BUM_RISK_MIN:
            bum_matchups.add((g["key"], g["home_sp"]))
        game_meta.append(
            {
                "key": g["key"],
                "title": build_game_title(g),
                "away": g["away"],
                "home": g["home"],
                "away_sp": g["away_sp"],
                "home_sp": g["home_sp"],
                # full names carried so the header can fall back to an arm's own
                # measured BAA lane when PropFinder has no risk row for him
                "away_sp_full": g.get("away_sp_full"),
                "home_sp_full": g.get("home_sp_full"),
                "away_risk": away_r,
                "home_risk": home_r,
            }
        )

    prop_by_game: dict[str, list] = {g["key"]: [] for g in game_meta}
    for p in props:
        prop_by_game[p[10]].append(p)

    lines = [
        "#!/usr/bin/env python3",
        '"""Generate games[] block for 2026-09-03 MLB HR cheat sheet."""',
        "import json",
        "from pathlib import Path",
        "",
        "from overdue_eval import apply_inferred_due",
        "",
        "ROOT = Path(__file__).resolve().parent",
        "",
        "FAVS = {",
    ]
    for f in favs_display:
        lines.append(f'    "{f}",')
    lines.extend(["}", "", "GEMS = {"])
    for g in gems_display:
        lines.append(f'    "{g}",')
    lines.extend(["}", "", "PLAYER_TEAMS = {"])
    for name, team in sorted(team_map.items()):
        lines.append(f'    "{name}": "{team}",')
    lines.extend(["}", "", "BUM_MATCHUPS = {"])
    for gkey, sp in sorted(bum_matchups):
        lines.append(f'    ({json.dumps(gkey)}, {json.dumps(sp)}),')
    lines.extend(
        [
            "}",
            "",
            "def odds_text(odds):",
            '    return "Listed prop - Over 0.5 HR" if odds == "N/A" else f"Listed {odds} - Over 0.5 HR"',
            "",
            "def row(name, hand, odds, score, emojis, chips, note, blast=None):",
            "    item = {",
            '        "name": f"{name} ({hand})",',
            '        "odds": odds_text(odds),',
            '        "score": score,',
            '        "emojis": emojis,',
            '        "note": note,',
            '        "chips": chips,',
            "    }",
            "    if blast:",
            '        item["blast"] = blast',
            "    return item",
            "",
            "def add_bum_row_emojis(entry, game_key):",
            '    chip = entry["chips"][0].replace("vs ", "").strip()',
            "    chip_last = chip.split()[-1] if chip else chip",
            "    if (game_key, chip) not in BUM_MATCHUPS and (game_key, chip_last) not in BUM_MATCHUPS:",
            "        return",
            '    em = entry["emojis"]',
            '    if "⚾" not in em:',
            '        em = f"{em} ⚾".strip()',
            '    if "🕊️" not in em:',
            '        em = f"{em} 🕊️".strip()',
            '    if "🧤" not in em:',
            '        em = f"{em} 🧤".strip()',
            '    entry["emojis"] = em',
            "",
            "games = [",
        ]
    )

    for gm in game_meta:
        away_r = gm["away_risk"]
        home_r = gm["home_risk"]
        park = park_for(park_context, gm["key"])
        if park:
            park_line = (
                f"Park boost {park['hr_pct']:+d}% "
                f"(stadium {park['hr_stadium']:+d}%, weather {park['hr_weather']:+d}%)."
            )
        else:
            park_line = "Park boost data unavailable."
        away_sp_label = gm["away_sp"]
        home_sp_label = gm["home_sp"]
        if away_r and away_r["overall"] >= BUM_RISK_MIN:
            away_sp_label = f"{away_sp_label} 🧤"
        if home_r and home_r["overall"] >= BUM_RISK_MIN:
            home_sp_label = f"{home_sp_label} 🧤"
        def _sp_line(label: str, r: dict | None, side: str, sp_full: str = "") -> str:
            if r and not r.get("no_data"):
                return (
                    f"{label} "
                    f"(HR risk {r['overall']:.2f}, vs LHB {r['vs_lhb']:+.2f}, "
                    f"vs RHB {r['vs_rhb']:+.2f})"
                )
            # No PropFinder risk row. Fall back to the arm's own measured lane
            # before giving up -- a real BAA split beats an empty header, and a
            # "no HR data" placeholder is noise on a betting sheet.
            lane = measured_lanes.get(name_lookup_key(sp_full)) if sp_full else None
            if lane:
                bits = []
                if lane["baa_lhb"] is not None:
                    bits.append(f"BAA vs LHB {lane['baa_lhb']:.3f}".replace("0.", "."))
                if lane["baa_rhb"] is not None:
                    bits.append(f"vs RHB {lane['baa_rhb']:.3f}".replace("0.", "."))
                if lane["hr9"] is not None:
                    bits.append(f"HR/9 {lane['hr9']:.2f}")
                if bits:
                    return f"{label} ({', '.join(bits)})"
            # Nothing measured anywhere. If MLB confirms the arm has never thrown a
            # big-league inning, say so: "no book on a debut arm" is a real tail
            # angle, unlike the "no PropFinder HR risk found" boilerplate this sheet
            # deliberately dropped. Never guess -- only when career IP is confirmed 0.
            if sp_full and is_mlb_debut(sp_full):
                return f"{label} - MLB debut, no book"
            # No PropFinder block anywhere, but the arm may still have a real MLB
            # season line -- a replaced probable gets a synthetic file with a blank
            # pitcher block, which used to drop him from the header entirely.
            mlb = mlb_season_lane(sp_full) if sp_full else None
            if mlb:
                # An overall figure, labelled as one. Printing it in both hand lanes
                # would dress a single number up as a measured platoon split.
                return f"{label} (season BAA {mlb})"
            return label

        away_line = _sp_line(away_sp_label, away_r, "Away", gm.get("away_sp_full") or "")
        home_line = _sp_line(home_sp_label, home_r, "Home", gm.get("home_sp_full") or "")
        desc = f"Tail key data: {park_line} {away_line}. {home_line}."
        base_title = gm["title"]
        game_title = base_title
        if " - " in base_title and " vs " in base_title:
            key_part, matchup_part = base_title.split(" - ", 1)
            away_seg, home_seg = matchup_part.split(" vs ", 1)
            away_name = away_seg.rsplit(" (", 1)[0]
            home_name = home_seg.rsplit(" (", 1)[0]
            away_tail = away_seg[len(away_name) :]
            home_tail = home_seg[len(home_name) :]
            if away_r and away_r["overall"] >= BUM_RISK_MIN and "🧤" not in away_name:
                away_name = f"{away_name} 🧤"
            if home_r and home_r["overall"] >= BUM_RISK_MIN and "🧤" not in home_name:
                home_name = f"{home_name} 🧤"
            game_title = f"{key_part} - {away_name}{away_tail} vs {home_name}{home_tail}"
        lines.append("    {")
        lines.append(f'        "title": {json.dumps(game_title, ensure_ascii=False)},')
        lines.append(f'        "description": {json.dumps(desc, ensure_ascii=False)},')
        lines.append('        "rows": [')
        for p in prop_by_game[gm["key"]]:
            name, hand, odds, score, chip, hr, near, ev, barrel, blast, _game, is_fav, is_gem = p
            em = emoji_string(is_fav, is_gem, ev, score, blast)
            risk = resolve_pitcher(pitcher_risk, chip)
            if risk and risk.get("no_data"):
                split = None
                matchup = ""  # no measured risk -> say nothing rather than apologise
            elif risk:
                split = batter_split(hand, risk)
                if hand == "S":
                    split_side = "LHB" if risk["vs_lhb"] >= risk["vs_rhb"] else "RHB"
                    matchup = (
                        f"{chip} SHB→{split_side} split {split:+.2f}, HR risk {risk['overall']:.2f}"
                    )
                else:
                    split_side = "LHB" if hand == "L" else "RHB"
                    matchup = f"{chip} {split_side} split {split:+.2f}, HR risk {risk['overall']:.2f}"
                carried = CARRIED_RISK.get(chip) or CARRIED_RISK.get(chip.split()[-1])
                if carried:
                    matchup += f" (risk carried from {carried})"
            else:
                split = None
                matchup = ""
            has_risk = bool(risk) and not risk.get("no_data")
            fade = fade_reason(
                split if has_risk else None,
                risk["overall"] if has_risk else None,
                hr,
                near,
                ev,
                park_for(park_context, _game),
            )
            prefix = ""
            if is_fav:
                prefix = "Worst Pickz Favorite. "
            elif is_gem:
                prefix = "Worst Pickz Hidden Gem. "
            note = prefix + f"{core_reason(hr, near, ev, barrel)}."
            if matchup:
                note += f" {matchup}."
            if fade:
                note += f" {fade}."
            if blast:
                lines.append(
                    f'            row("{name}", "{hand}", "{odds}", {score}, "{em}", ["vs {chip}"], '
                    f'"""{note}""", blast="{blast}"),'
                )
            else:
                lines.append(
                    f'            row("{name}", "{hand}", "{odds}", {score}, "{em}", ["vs {chip}"], '
                    f'"""{note}"""),'
                )
        lines.extend(["        ],", "    },"])

    lines.extend(
        [
            "]",
            "",
            "for game in games:",
            '    game_key = game["title"].split(" - ")[0]',
            "    for entry in game['rows']:",
            "        add_bum_row_emojis(entry, game_key)",
            "        apply_inferred_due(entry, game)",
            "",
            "from game_start_times import annotate_and_sort_games",
            f'games = annotate_and_sort_games(games, "{DATE}")',
            "",
            "if __name__ == '__main__':",
            "    def js_string(value):",
            "        return json.dumps(value, ensure_ascii=False)",
            "",
            "    def emit_games_js(games_data):",
            "        out = ['const games = [']",
            "        for game in games_data:",
            "            out.append('    {')",
            "            out.append(f\"        title: {js_string(game['title'])},\")",
            "            out.append(f\"        description: {js_string(game['description'])},\")",
            '            if game.get("startTime"):',
            '                out.append(f"        startTime: {js_string(game[\'startTime\'])},")',
            "            out.append('        rows: [')",
            "            for entry in game['rows']:",
            "                parts = [",
            "                    f\"name: {js_string(entry['name'])}\",",
            "                    f\"odds: {js_string(entry['odds'])}\",",
            "                    f\"score: {entry['score']}\",",
            "                    f\"emojis: {js_string(entry['emojis'])}\",",
            "                    f\"note: {js_string(entry['note'])}\",",
            "                    f\"chips: {js_string(entry['chips'])}\",",
            "                ]",
            "                if entry.get('blast'):",
            "                    parts.append(f\"blast: {js_string(entry['blast'])}\")",
            "                out.append('            { ' + ', '.join(parts) + ' },')",
            "            out.append('        ],')",
            "            out.append('    },')",
            "        out.append('];')",
            "        return '\\n'.join(out)",
            "",
            "    out = ROOT / '_games-0903.txt'",
            "    out.write_text(emit_games_js(games) + '\\n', encoding='utf-8')",
            "    print('wrote', out.name)",
        ]
    )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"Wrote {OUT.name} with {len(props)} props, {len(game_meta)} games, "
        f"{len(favs_display)} favorites, {len(gems_display)} hidden gems"
    )
    if missing:
        print(f"WARN missing {len(missing)} props from CSV:")
        for n in missing:
            print(" ", n)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
