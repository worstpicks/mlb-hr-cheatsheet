#!/usr/bin/env python3
"""Build 2026-07-19 sheet from imported CSVs and user prop list."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

from csv_slate_meta import (
    derive_games_from_csv,
    name_lookup_key,
    read_batter_rows,
    read_matchup_header,
)
from hr_score_model import batter_split, score_from_model
from sheet_data import load_pitcher_risk, resolve_pitcher

ROOT = Path(__file__).resolve().parent
DATE = "2026-07-19"
OUT = ROOT / "build-sheet-2026-07-19.py"
BUM_RISK_MIN = 0.95

RAW_PROPS = [
    "Vladimir Guerrero Jr.💎",
    "George Springer⭐",
    "Brandon Valenzuela",
    "Randal Grichuk",
    "Miguel Vargas",
    "Munetaka Murakami",
    "Ben Rice⭐(Game 1)",
    "Ryan McMahon⭐(Game 1)",
    "Trent Grisham⭐(Game 1)",
    "Max Muncy⭐(Game 1)",
    "Teoscar Hernandez(Game 1)",
    "Shohei Ohtani(Game 1)",
    "Kyle Schwarber⭐",
    "Gabriel Rincones Jr.",
    "Bryson Stott",
    "Brett Baty💎",
    "Jared Young",
    "Tyrone Taylor",
    "Wilyer Abreu⭐",
    "Romy Gonzalez",
    "Willson Contreras",
    "Andruw Monasterio",
    "Hunter Feduccia",
    "Jonathan Aranda⭐",
    "Matt Olson",
    "Drake Baldwin⭐",
    "Joc Pederson⭐",
    "Chase DeLauter",
    "Austin Hedges",
    "Brayan Rocchio",
    "Brandon Lowe",
    "Esmerlyn Valdez⭐",
    "Marcell Ozuna",
    "Rafael Flores",
    "Brice Turang⭐",
    "Christian Yelich",
    "Braden Shewmake",
    "Heriberto Hernandez⭐",
    "Esteury Ruiz",
    "Carter Jensen⭐",
    "Lane Thomas💎",
    "Bobby Witt Jr.",
    "Ty France",
    "Luis Rengifo",
    "Manny Machado⭐",
    "Taylor Trammell💎",
    "Yordan Alvarez",
    "Tyler O'Neil",
    "Pete Alonso",
    "Pete Crow Armstrong💎",
    "Kody Clemens💎",
    "Ryan Jeffers⭐",
    "Victor Caratini",
    "Luke Keaschall",
    "Willi Castro",
    "Mickey Moniak⭐",
    "Jake McCarthy",
    "Kyle Karros",
    "Eugenio Suarez⭐",
    "Spencer Steer",
    "Shea Langeliers💎",
    "Colby Thomas",
    "James Wood",
    "CJ Abrams",
    "Andrew Chaparro",
    "Jorge Soler💎",
    "Josh Lowe⭐",
    "Logan O'Hoppe",
    "Riley Greene",
    "Colt Keith",
    "Kerry Carpenter",
    "Dominic Canzone💎",
    "Cole Young💎",
    "Bryce Eldridge⭐",
    "Max Kepler",
    "Nathan Church",
    "Nelson Velazquez",
    "Alec Burleson⭐",
    "Jimmy Crooks",
    "Ryan McMahon⭐(Game 2)",
    "Ben Rice⭐(Game 2)",
    "Jazz Chisholm Jr.(Game 2)",
    "Trent Grisham💎(Game 2)",
    "Dalton Rushing⭐(Game 2)",
    "Max Muncy💎(Game 2)",
    "Andy Pages(Game 2)",
    "Kyle Tucker(Game 2)",
]

ALIASES = {
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Pete Crow-Armstrong": "Pete Crow-Armstrong",
    "Tyler O'Neil": "Tyler O'Neill",
    "Tyler O'Neill": "Tyler O'Neill",
    "Vladimir Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Jazz Chisholm Jr.": "Jazz Chisholm Jr.",
    "Gabriel Rincones Jr.": "Gabriel Rincones Jr.",
    "Bobby Witt Jr.": "Bobby Witt Jr.",
    "Logan O'Hoppe": "Logan O'Hoppe",
    "Teoscar Hernandez": "Teoscar Hernandez",
    "Shohei Ohtani": "Shohei Ohtani",
    "Andrew Chaparro": "Andres Chaparro",
    "Andres Chaparro": "Andres Chaparro",
}

MANUAL_BATTER_ROWS: dict[str, dict] = {}

BATTER_GAME_OVERRIDES: dict[str, str] = {}

PROP_GAME_OVERRIDES: dict[str, str] = {}

CHC_DH_SPECS = {
    "LAD @ NYY (G1)": {
        "away_sp": "Yamamoto",
        "home_sp": "Schlittler",
        "away_sp_full": "Yoshinobu Yamamoto",
        "home_sp_full": "Cam Schlittler",
        "files": [
            "hr-matchups-LAD-at-NYY-Yoshinobu-Yamamoto-2026-07-19.csv",
            "hr-matchups-LAD-at-NYY-Cam-Schlittler-2026-07-19.csv",
        ],
    },
    "LAD @ NYY (G2)": {
        "away_sp": "Sheehan",
        "home_sp": "Weathers",
        "away_sp_full": "Emmet Sheehan",
        "home_sp_full": "Ryan Weathers",
        "files": [
            "hr-matchups-LAD-at-NYY-Emmet-Sheehan-2026-07-19.csv",
            "hr-matchups-LAD-at-NYY-Ryan-Weathers-2026-07-19.csv",
        ],
    },
}

PROBABLE_OVERRIDES: dict[str, dict] = {}

PITCHER_HAND = {
    "Sean Burke": "R",
    "Trey Yesavage": "R",
    "Yoshinobu Yamamoto": "R",
    "Cam Schlittler": "R",
    "Emmet Sheehan": "R",
    "Ryan Weathers": "L",
    "Shane McClanahan": "L",
    "Sonny Gray": "R",
    "Nathan Eovaldi": "R",
    "Grant Holmes": "R",
    "Nolan McLean": "R",
    "Alan Rangel": "R",
    "Paul Skenes": "R",
    "Joey Cantillo": "L",
    "German Marquez": "R",
    "Noah Cameron": "L",
    "Eury Perez": "R",
    "Robert Gasser": "L",
    "Brandon Young": "R",
    "Hunter Brown": "R",
    "Zebby Matthews": "R",
    "Shota Imanaga": "L",
    "Hunter Greene": "R",
    "Ryan Feltner": "R",
    "Foster Griffin": "L",
    "Jacob Lopez": "L",
    "Casey Mize": "R",
    "Ryan Johnson": "R",
    "Robbie Ray": "L",
    "Logan Gilbert": "R",
    "Andre Pallante": "R",
    "Eduardo Rodriguez": "L",
}


def pitcher_hand_label(full_name: str) -> str:
    return PITCHER_HAND.get(full_name, "R")


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


def split_chc_doubleheader(games: dict[str, dict]) -> None:
    if "LAD @ NYY" not in games:
        return
    games.pop("LAD @ NYY", None)
    for gkey, spec in CHC_DH_SPECS.items():
        gm = {
            "key": gkey,
            "away": "LAD",
            "home": "NYY",
            "away_sp": spec["away_sp"],
            "home_sp": spec["home_sp"],
            "away_sp_full": spec["away_sp_full"],
            "home_sp_full": spec["home_sp_full"],
            "batters": {},
        }
        for fname in spec["files"]:
            path = ROOT / "data" / fname
            hdr = read_matchup_header(path)
            sp_last = hdr["pitcher"].split()[-1]
            for b in read_batter_rows(path):
                gm["batters"][name_lookup_key(b["name"])] = {**b, "vs": sp_last, "file": fname}
        games[gkey] = gm


def parse_prop_label(raw: str) -> tuple[str, bool, bool, str | None]:
    clean = raw.strip()
    fav = False
    while "⭐" in clean:
        fav = True
        clean = clean.replace("⭐", "", 1).strip()
    gem = "💎" in clean
    if gem:
        clean = clean.replace("💎", "", 1).strip()
    # Normalize (G1)/(G2) → (Game 1)/(Game 2)
    clean = re.sub(r"\(G([12])\)", lambda m: f"(Game {m.group(1)})", clean, flags=re.I)
    game_override = None
    m = re.search(r"\(Game\s*(\d)\)", clean, re.I)
    if m:
        game_override = f"LAD @ NYY (G{m.group(1)})"
        clean = re.sub(r"\s*\(Game\s*\d\)", "", clean, flags=re.I).strip()
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


def load_park_context(date: str) -> dict[str, dict]:
    data_dir = ROOT / "data"
    path = data_dir / f"ParkFactors_{date}.csv"
    if not path.exists():
        matches = sorted(data_dir.glob(f"ParkFactors_{date}*.csv"))
        if matches:
            path = matches[0]
    park_key_aliases = {
        "CWS @ BAL": "CHW @ BAL",
        "CWS @ CLE": "CHW @ CLE",
        "CWS @ MIN": "CHW @ MIN",
        "CWS @ NYY": "CHW @ NYY",
        "PIT @ WSH": "PIT @ WAS",
        "HOU @ WSH": "HOU @ WAS",
        "BOS @ CWS": "BOS @ CHW",
        "ATH @ CWS": "ATH @ CHW",
        "NYY @ WSH": "NYY @ WAS",
        "CWS @ TOR": "CHW @ TOR",
        "WSH @ ATH": "WAS @ ATH",
        "WAS @ ATH": "WAS @ ATH",
        "LAD @ NYY (G1)": "LAD @ NYY",
        "LAD @ NYY (G2)": "LAD @ NYY",
    }
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = " ".join((row.get("Game") or "").replace("  ", " ").split())
            if not key:
                continue
            entry = {
                "hr_pct": _pct_value(row.get("HR %")),
                "hr_weather": _pct_value(row.get("HR % Weather")),
                "hr_stadium": _pct_value(row.get("HR % Stadium")),
            }
            out[key] = entry
            for sheet_key, csv_key in park_key_aliases.items():
                if key == csv_key:
                    out[sheet_key] = entry
    return out


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
    games_csv = {g["key"]: g for g in derive_games_from_csv(DATE)}
    split_chc_doubleheader(games_csv)
    apply_probable_overrides(games_csv)
    pitcher_risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
    park_context = load_park_context(DATE)

    batter_ctx: dict[str, dict] = {}
    batter_by_game: dict[tuple[str, str], dict] = {}
    for g in games_csv.values():
        for row in g["batters"].values():
            vs = row["vs"]
            if vs == g["away_sp"]:
                team = g["home"]
            elif vs == g["home_sp"]:
                team = g["away"]
            else:
                continue
            entry = {
                "game": g["key"],
                "team": team,
                "opp_sp": vs,
                "row": row,
            }
            key = name_lookup_key(row["name"])
            batter_by_game[(key, g["key"])] = entry
            if key not in batter_ctx:
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

    # Per (name, game) so DH props can be ⭐ in G1 and 💎 in G2.
    fav_keys: set[tuple[str, str]] = set()
    gem_keys: set[tuple[str, str]] = set()
    prop_entries: list[tuple[str, bool, bool, str | None]] = []
    for raw in RAW_PROPS:
        clean, fav, gem, game_override = parse_prop_label(raw)
        prop_entries.append((clean, fav, gem, game_override))

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
        park_ctx = park_context.get(ctx["game"])
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
                "away_risk": away_r,
                "home_risk": home_r,
            }
        )

    prop_by_game: dict[str, list] = {g["key"]: [] for g in game_meta}
    for p in props:
        prop_by_game[p[10]].append(p)

    # FAVS/GEMS sets are display-name based for sheet filters; per-row flags carry DH truth.

    lines = [
        "#!/usr/bin/env python3",
        '"""Generate games[] block for 2026-07-19 MLB HR cheat sheet."""',
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
            "    if (game_key, chip) not in BUM_MATCHUPS:",
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
        park = park_context.get(gm["key"])
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
        away_line = (
            f"{away_sp_label} "
            f"(HR risk {away_r['overall']:.2f}, vs LHB {away_r['vs_lhb']:+.2f}, vs RHB {away_r['vs_rhb']:+.2f})"
            if away_r
            else "Away starter risk unavailable"
        )
        home_line = (
            f"{home_sp_label} "
            f"(HR risk {home_r['overall']:.2f}, vs LHB {home_r['vs_lhb']:+.2f}, vs RHB {home_r['vs_rhb']:+.2f})"
            if home_r
            else "Home starter risk unavailable"
        )
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
            if risk:
                split = batter_split(hand, risk)
                if hand == "S":
                    split_side = "LHB" if risk["vs_lhb"] >= risk["vs_rhb"] else "RHB"
                    matchup = (
                        f"{chip} SHB→{split_side} split {split:+.2f}, HR risk {risk['overall']:.2f}"
                    )
                else:
                    split_side = "LHB" if hand == "L" else "RHB"
                    matchup = f"{chip} {split_side} split {split:+.2f}, HR risk {risk['overall']:.2f}"
            else:
                split = None
                matchup = f"{chip} split/risk data unavailable"
            fade = fade_reason(
                split if risk else None,
                risk["overall"] if risk else None,
                hr,
                near,
                ev,
                park_context.get(_game),
            )
            prefix = ""
            if is_fav:
                prefix = "Worst Pickz Favorite. "
            elif is_gem:
                prefix = "Worst Pickz Hidden Gem. "
            note = prefix + f"{core_reason(hr, near, ev, barrel)}. {matchup}."
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
            "    out = ROOT / '_games-0711.txt'",
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
