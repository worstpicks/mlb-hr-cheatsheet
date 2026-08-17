#!/usr/bin/env python3
"""Build 2026-08-17 sheet from imported CSVs and user prop list."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

from game_row_enrich import alias_weather_game_key
from csv_slate_meta import (
    derive_games_from_csv,
    name_lookup_key,
    read_batter_rows,
    read_matchup_header,
)
from hr_score_model import batter_split, score_from_model
from sheet_data import load_pitcher_risk, resolve_pitcher

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-17"
OUT = ROOT / "build-sheet-2026-08-17.py"
BUM_RISK_MIN = 0.95

# Arms whose HR-risk row was carried from an earlier slate get labelled here so a
# reader never mistakes a stale split for a same-day number. Empty since the 11:42
# re-export shipped all 22 arms.
CARRIED_RISK: dict[str, str] = {}

RAW_PROPS = [
    "Elly De La Cruz(G1)",
    "Eugenio Suarez(G1)",
    "Sal Stewart(G1)",
    "Tyler Stephenson💎(G1)",
    "Alec Burleson💎(G1)",
    "Jordan Walker(G1)",
    "Victor Mesa Jr.💎",
    "Christian Encarnacion-Strand⭐",
    "Pete Alonso💎",
    "Coby Mayo",
    "Kyle Schwarber⭐",
    "Brandon Marsh",
    "Derek Hill",
    "Agustin Ramirez",
    "Heriberto Hernandez⭐",
    "Ke'Bryan Hayes(G2)",
    "Elly De La Cruz(G2)",
    "Tyler Stephenson(G2)",
    "Michael Toglia(G2)",
    "Alec Burleson(G2)",
    "Ivan Herrera(G2)",
    "Joshua Baez(G2)⭐",
    "Jordan Walker(G2)",
    "Rafael Flores⭐",
    "Esmerlyn Valdez💎",
    "Bryan Reynolds",
    "Ronny Simon",
    "Spencer Torkelson⭐",
    "Ben Malgeri💎",
    "Colt Keith",
    "Brett Baty",
    "Francisco Lindor💎",
    "Bo Bichette",
    "Gavin Sheets",
    "Xander Bogaerts💎",
    "Fernando Tatis Jr.",
    "Manny Machado",
    "Jackson Merrill💎",
    "Ceddanne Rafaela💎",
    "Jahmai Jones",
    "Corbin Carroll",
    "Max Kepler",
    "Ketel Marte",
    "Josh Bell💎",
    "Byron Buxton",
    "Austin Riley",
    "Matt Olson",
    "Mike Yastrzemski",
    "Ronald Acuna Jr.",
    "Jac Caglianone",
    "Michael Massey",
    "Zack Gelof💎",
    "Lawrence Butler⭐",
    "Jeff McNeil",
    "Michael Conforto⭐",
    "Pete Crow Armstrong",
    "Dansby Swanson💎",
    "Miguel Amaya",
    "Munetaka Murakami⭐",
    "Miguel Vargas💎",
    "Luisangel Acuna",
    "Cole Carrigg",
    "Jake McCarthy",
    "Mickey Moniak",
    "Hunter Goodman",
    "Max Muncy💎",
    "Hunter Feduccia💎",
    "Shohei Ohtani",
    "Teoscar Hernandez",
]

ALIASES = {
    # The request wrote "Pete Crow Armstrong"; PropFinder exports the hyphen.
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Pete Crow-Armstrong": "Pete Crow-Armstrong",
    # The slate page drops the suffix; PropFinder exports "Victor Mesa Jr.".
    "Victor Mesa": "Victor Mesa Jr.",
    "Victor Mesa Jr.": "Victor Mesa Jr.",
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Ronald Acuna": "Ronald Acuna Jr.",
    "Luisangel Acuna": "Luisangel Acuna",
    "Fernando Tatis Jr.": "Fernando Tatis Jr.",
    "Ke'Bryan Hayes": "Ke'Bryan Hayes",
    "Christian Encarnacion-Strand": "Christian Encarnacion-Strand",
    "Agustin Ramirez": "Agustin Ramirez",
    "Agustín Ramírez": "Agustin Ramirez",
    "Heriberto Hernandez": "Heriberto Hernandez",
    "Teoscar Hernandez": "Teoscar Hernandez",
    "Munetaka Murakami": "Munetaka Murakami",
    "Esmerlyn Valdez": "Esmerlyn Valdez",
    "Rafael Flores": "Rafael Flores",
    "Ben Malgeri": "Ben Malgeri",
    "Ronny Simon": "Ronny Simon",
    "Cole Carrigg": "Cole Carrigg",
    "Jac Caglianone": "Jac Caglianone",
    "Hunter Goodman": "Hunter Goodman",
    "Hunter Feduccia": "Hunter Feduccia",
    "Jahmai Jones": "Jahmai Jones",
    "Ceddanne Rafaela": "Ceddanne Rafaela",
    "Michael Toglia": "Michael Toglia",
    "Joshua Baez": "Joshua Baez",
    "Ivan Herrera": "Ivan Herrera",
    "Iván Herrera": "Ivan Herrera",
    "Miguel Vargas": "Miguel Vargas",
    "Zack Gelof": "Zack Gelof",
    "Lawrence Butler": "Lawrence Butler",
    "Jake McCarthy": "Jake McCarthy",
    "Mickey Moniak": "Mickey Moniak",
    "Shohei Ohtani": "Shohei Ohtani",
    "Max Muncy": "Max Muncy",
}

MANUAL_BATTER_ROWS: dict[str, dict] = {}

BATTER_GAME_OVERRIDES: dict[str, str] = {}

PROP_GAME_OVERRIDES: dict[str, str] = {}

STL_CIN_DH_SPECS: dict[str, dict] = {
    "STL @ CIN (G1)": {
        "away_sp": "Mathews",
        "home_sp": "Emanuel",
        "away_sp_full": "Quinn Mathews",
        "home_sp_full": "Kent Emanuel",
        "files": [
            "hr-matchups-STL-at-CIN-Quinn-Mathews-2026-08-17.csv",
            "hr-matchups-STL-at-CIN-Kent-Emanuel-2026-08-17.csv",
        ],
    },
    "STL @ CIN (G2)": {
        "away_sp": "Pallante",
        "home_sp": "Lowder",
        "away_sp_full": "Andre Pallante",
        "home_sp_full": "Rhett Lowder",
        "files": [
            "hr-matchups-STL-at-CIN-Andre-Pallante-2026-08-17.csv",
            "hr-matchups-STL-at-CIN-Rhett-Lowder-2026-08-17.csv",
        ],
    },
}

PROBABLE_OVERRIDES: dict[str, dict] = {}

PITCHER_HAND = {
    # 8/17 LHP
    "Quinn Mathews": "L",
    "Kent Emanuel": "L",
    "Alec Gamboa": "L",
    "Shane McClanahan": "L",
    "Cristopher Sanchez": "L",
    "Framber Valdez": "L",
    "Mitch Bratt": "L",
    "Martin Perez": "L",
    "Shota Imanaga": "L",
    "Blake Snell": "L",
    # 8/17 RHP
    "Brandon Young": "R",
    "Janson Junk": "R",
    "Andre Pallante": "R",
    "Rhett Lowder": "R",
    "Carmen Mlodzinski": "R",
    "Walker Buehler": "R",
    "Nolan McLean": "R",
    "Mason Barnett": "R",
    "Michael Wacha": "R",
    "Bailey Ober": "R",
    "Luis Castillo": "R",
    "Tomoyuki Sugano": "R",
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


def split_stl_cin_doubleheader(games: dict[str, dict]) -> None:
    if "STL @ CIN" not in games:
        return
    games.pop("STL @ CIN", None)
    for gkey, spec in STL_CIN_DH_SPECS.items():
        gm = {
            "key": gkey,
            "away": "STL",
            "home": "CIN",
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
        game_override = "KC @ LAD" if m.group(1).upper() == "LAD" else "TB @ ATH"
    dh = re.search(r"\(G([12])\)\s*$", clean, re.I)
    if dh:
        game_override = f"STL @ CIN (G{dh.group(1)})"
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
    games_csv = {g["key"]: g for g in derive_games_from_csv(DATE)}
    split_stl_cin_doubleheader(games_csv)
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
                "away_risk": away_r,
                "home_risk": home_r,
            }
        )

    prop_by_game: dict[str, list] = {g["key"]: [] for g in game_meta}
    for p in props:
        prop_by_game[p[10]].append(p)

    lines = [
        "#!/usr/bin/env python3",
        '"""Generate games[] block for 2026-08-17 MLB HR cheat sheet."""',
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
        def _sp_line(label: str, r: dict | None, side: str) -> str:
            if not r:
                return f"{side} starter risk unavailable"
            if r.get("no_data"):
                return f"{label} (no MLB HR data yet)"
            return (
                f"{label} "
                f"(HR risk {r['overall']:.2f}, vs LHB {r['vs_lhb']:+.2f}, vs RHB {r['vs_rhb']:+.2f})"
            )

        away_line = _sp_line(away_sp_label, away_r, "Away")
        home_line = _sp_line(home_sp_label, home_r, "Home")
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
                matchup = f"{chip} has no MLB HR data yet"
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
                matchup = f"{chip} split/risk data unavailable"
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
            "    out = ROOT / '_games-0817.txt'",
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
