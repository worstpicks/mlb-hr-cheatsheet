#!/usr/bin/env python3
"""Build 2026-08-04 sheet from imported CSVs and user prop list."""
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
DATE = "2026-08-04"
OUT = ROOT / "build-sheet-2026-08-04.py"
BUM_RISK_MIN = 0.95

RAW_PROPS = [
    "Pete Alonso⭐",
    "Bryce Harper⭐",
    "J.T. Realmuto💎",
    "Dylan Crews",
    "Rhys Hoskins",
    "Tyler Stephenson",
    "Eugenio Suarez",
    "JJ Bleday",
    "Sal Stewart",
    "Carlos Cortes",
    "Tyler Soderstrom",
    "Lawrence Butler",
    "Luis Garcia Jr.",
    "Ben Rice",
    "Heliot Ramos",
    "Ryan McMahon",
    "Austin Wells",
    "Nelson Velazquez💎",
    "Willson Contreras",
    "Miguel Vargas⭐",
    "Colson Montgomery",
    "Ronald Acuna Jr.",
    "Mike Yastrzemski",
    "Matt Olson",
    "Owen Caissie⭐",
    "Griffin Conine⭐",
    "Joe Mack",
    "Jake Bauers⭐",
    "Brandon Lowe⭐",
    "John Rave💎",
    "Salvador Perez",
    "Carter Jensen",
    "Royce Lewis",
    "Corey Seager",
    "Joc Pederson",
    "Willy Adames",
    "Daniel Susac",
    "Michael Conforto",
    "Shohei Ohtani",
    "Freddie Freeman",
    "Daulton Varsho",
    "Taylor Trammell",
    "George Springer",
    "Kazuma Okamoto",
    "Hunter Goodman",
    "Junior Caminero⭐",
    "Victor Mesa Jr.",
    "Cole Young",
    "Hao-Yu Lee",
    "Gleyber Torres",
    "Kevin McGonigle",
    "Tim Tawa",
    "Manny Machado",
    "Jackson Merrill",
    "Ty France",
]

ALIASES = {
    "JT Realmuto": "J.T. Realmuto",
    "J.T Realmuto": "J.T. Realmuto",
    "J.T. Realmuto": "J.T. Realmuto",
    "Hao Yu Lee": "Hao-Yu Lee",
    "Hao-Yu Lee": "Hao-Yu Lee",
    "Tim tawa": "Tim Tawa",
    "Tim Tawa": "Tim Tawa",
    "Nelson Velazquez": "Nelson Velazquez",
    "Luis Garcia Jr.": "Luis Garcia Jr.",
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Mike Yastrzemski": "Mike Yastrzemski",
    "Daulton Varsho": "Daulton Varsho",
    "Kazuma Okamoto": "Kazuma Okamoto",
    "Victor Mesa Jr.": "Victor Mesa Jr.",
    "Kevin McGonigle": "Kevin McGonigle",
    "Carlos Cortes": "Carlos Cortes",
    "Griffin Conine": "Griffin Conine",
    "Owen Caissie": "Owen Caissie",
    "Colson Montgomery": "Colson Montgomery",
    "Daniel Susac": "Daniel Susac",
    "Junior Caminero": "Junior Caminero",
    "Willson Contreras": "Willson Contreras",
    "Eugenio Suarez": "Eugenio Suarez",
}

MANUAL_BATTER_ROWS: dict[str, dict] = {}

BATTER_GAME_OVERRIDES: dict[str, str] = {}

PROP_GAME_OVERRIDES: dict[str, str] = {}

ATL_NYM_DH_SPECS: dict[str, dict] = {}

PROBABLE_OVERRIDES: dict[str, dict] = {}

PITCHER_HAND = {
    # 8/4 LHP
    "Cade Povich": "L",
    "Sean Manaea": "L",
    "Joey Cantillo": "L",
    "Jesus Luzardo": "L",
    "Ryan Weathers": "L",
    "Patrick Sandoval": "L",
    "MacKenzie Gore": "L",
    "Tarik Skubal": "L",
    "Eduardo Rodriguez": "L",
    # 8/4 RHP (explicit)
    "Grayson Rodriguez": "R",
    "J.T. Ginn": "R",
    "Brady Singer": "R",
    "Zack Littell": "R",
    "Hunter Dobbins": "R",
    "Davis Martin": "R",
    "Ryan Gusto": "R",
    "Grant Holmes": "R",
    "Joe Ryan": "R",
    "Randy Dobnak": "R",
    "Jared Jones": "R",
    "Logan Henderson": "R",
    "Blade Tidwell": "R",
    "Javier Assad": "R",
    "Trey Yesavage": "R",
    "Hayden Wesneski": "R",
    "Freddy Peralta": "R",
    "Gabriel Hughes": "R",
    "Troy Melton": "R",
    "Emerson Hancock": "R",
    "Randy Vasquez": "R",
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


def split_atl_nym_doubleheader(games: dict[str, dict]) -> None:
    if "ATL @ NYM" not in games:
        return
    games.pop("ATL @ NYM", None)
    for gkey, spec in ATL_NYM_DH_SPECS.items():
        gm = {
            "key": gkey,
            "away": "ATL",
            "home": "NYM",
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
    game_override = None
    m = re.search(r"Max Muncy\s*\((LAD|ATH)\)", clean, re.I)
    if m:
        clean = "Max Muncy"
        game_override = "LAD @ NYM" if m.group(1).upper() == "LAD" else "ATH @ MIN"
    dh = re.search(r"\(G([12])\)\s*$", clean, re.I)
    if dh:
        game_override = f"ATL @ NYM (G{dh.group(1)})"
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
        "CWS @ TEX": "CHW @ TEX",
        "CWS @ TB": "CHW @ TB",
        "TB @ CWS": "TB @ CHW",
        "WSH @ ATH": "WAS @ ATH",
        "WAS @ ATH": "WAS @ ATH",
        "WSH @ COL": "WAS @ COL",
        "CHW @ TEX": "CHW @ TEX",
        "NYY @ CWS": "NYY @ CHW",
        "WSH @ ATL": "WAS @ ATL",
        "WAS @ ATL": "WAS @ ATL",
        "TOR @ WSH": "TOR @ WAS",
    }
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

    out: dict[str, dict] = {}

    def _alias_keys(base_key: str, entry: dict) -> None:
        out[base_key] = entry
        for sheet_key, csv_key in park_key_aliases.items():
            if base_key == csv_key:
                out[sheet_key] = entry

    for key, entries in by_game.items():
        entries.sort(key=lambda e: _time_sort_key(e[0]))
        if len(entries) == 1:
            _alias_keys(key, entries[0][1])
            continue
        _alias_keys(key, entries[0][1])
        for i, (_time_val, entry) in enumerate(entries, 1):
            gkey = f"{key} (G{i})"
            out[gkey] = entry
            for sheet_key, csv_key in park_key_aliases.items():
                if key == csv_key:
                    out[f"{sheet_key} (G{i})"] = entry

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
    split_atl_nym_doubleheader(games_csv)
    apply_probable_overrides(games_csv)
    pitcher_risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
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

    lines = [
        "#!/usr/bin/env python3",
        '"""Generate games[] block for 2026-08-04 MLB HR cheat sheet."""',
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
            "    out = ROOT / '_games-0804.txt'",
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
