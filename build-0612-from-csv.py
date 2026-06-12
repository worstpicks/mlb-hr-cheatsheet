#!/usr/bin/env python3
"""Build 2026-06-12 sheet from imported CSVs and user prop list."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

from csv_slate_meta import derive_games_from_csv, name_lookup_key
from sheet_data import load_pitcher_risk, resolve_pitcher

ROOT = Path(__file__).resolve().parent
DATE = "2026-06-12"
OUT = ROOT / "build-sheet-2026-06-12.py"

RAW_PROPS = [
    "Tyler Callihan⭐",
    "Endy Rodriguez💎",
    "Bryan Reynolds",
    "Kyle Stowers⭐",
    "Owen Caissie",
    "Heriberto Hernandez",
    "Daylen Lile⭐",
    "James Wood⭐",
    "Luis Garcia Jr.💎",
    "Dominic Canzone",
    "Luke Raley",
    "Colton Cowser💎",
    "Samuel Basallo",
    "Pete Alonso",
    "Fernando Tatis Jr⭐",
    "Jackson Merrill",
    "Manny Machado",
    "Kyle Manzardo",
    "Riley Greene⭐",
    "Dillon Dingler",
    "Kerry Carpenter",
    "Wilyer Abreu⭐",
    "Jarren Duran",
    "Mickey Gasper",
    "Wyatt Langford",
    "Jake Burger",
    "Corey Seager",
    "Jared Young",
    "Luis Torrens",
    "Matt Olson⭐",
    "Spencer Steer⭐",
    "Ketel Marte⭐",
    "Ryan Waldschmidt",
    "Tommy Troy💎",
    "Kazuma Okamoto⭐",
    "Ben Rice",
    "Ryan McMahon",
    "Gary Sanchez",
    "Jake Bauers",
    "Garrett Mitchell⭐",
    "Jackson Chourio",
    "Edmundo Sosa",
    "Bryce Harper",
    "JT Realmuto",
    "Brandon Marsh",
    "Kyle Schwarber",
    "Colson Montgomery⭐",
    "Miguel Vargas💎",
    "Jacob Gonzalez💎",
    "Braden Montogomery",
    "Andy Pages",
    "Shohei Ohtani⭐",
    "Mookie Betts",
    "Victor Caratini💎",
    "Byron Buxton",
    "Alec Burleson⭐",
    "Lars Nootbaar",
    "Jordan Walker",
    "JJ Wetherholt",
    "Jac Caglianone⭐",
    "Vinnie Pasqunatino",
    "Michael Massey",
    "Yordan Alvarez⭐",
    "Isaac Paredes",
    "Cam Smith💎",
    "Zach Neto",
    "Mike Trout⭐",
    "Oswald Peraza",
    "Logan O Hoppe",
    "Hunter Feduccia",
    "Junior Caminero",
    "Yandy Diaz",
    "Nick Kurtz⭐",
    "Shea Langeliers",
    "Henry Bolte💎",
    "Zack Gelof",
    "Colby Thomas",
    "Kyle Karros",
    "Hunter Goodman",
    "Edouard Jullien",
    "Eric Hasse💎",
    "Willy Adames",
    "BRyce Eldridge",
    "Pete Crow Armstrong",
    "Ian Happ",
    "Seiya Suzuki",
]

ALIASES = {
    "BRyce Eldridge": "Bryce Eldridge",
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Edouard Jullien": "Edouard Julien",
    "Vinnie Pasqunatino": "Vinnie Pasquantino",
    "Braden Montogomery": "Braden Montgomery",
    "Fernando Tatis Jr": "Fernando Tatis Jr.",
    "Logan O Hoppe": "Logan O'Hoppe",
    "JT Realmuto": "J.T. Realmuto",
    "Eric Hasse": "Eric Haase",
    "Samuel Basallo": "Samuel Basallo",
}

PROBABLE_OVERRIDES: dict[str, dict] = {}

PITCHER_HAND = {
    "Sandy Alcantara": "R",
    "Braxton Ashcraft": "R",
    "Bryce Miller": "R",
    "Zack Littell": "R",
    "Griffin Canning": "R",
    "Shane Baz": "R",
    "Jack Leiter": "R",
    "Sonny Gray": "R",
    "Jack Flaherty": "R",
    "Tanner Bibee": "R",
    "Eduardo Rodriguez": "L",
    "Nick Lodolo": "L",
    "Spencer Strider": "R",
    "Nolan McLean": "R",
    "Ryan Weathers": "L",
    "Trey Yesavage": "R",
    "Andrew Painter": "R",
    "Jacob Misiorowski": "R",
    "Roki Sasaki": "R",
    "Anthony Kay": "L",
    "Kyle Leahy": "R",
    "Joe Ryan": "R",
    "Shane McClanahan": "L",
    "Samuel Aldegheri": "L",
    "Tatsuya Imai": "R",
    "Luinder Avila": "R",
    "Javier Assad": "R",
    "Landen Roupp": "R",
    "Kyle Freeland": "L",
    "Gage Jump": "L",
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


def build_game_title(gm: dict) -> str:
    away_full = gm["away_sp_full"]
    home_full = gm["home_sp_full"]
    return (
        f"{gm['key']} - {away_full} ({pitcher_hand_label(away_full)}, {gm['away']}) "
        f"vs {home_full} ({pitcher_hand_label(home_full)}, {gm['home']})"
    )


def score_from_stats(hr, near, ev, barrel, blast):
    s = 62 + hr * 4 + near * 2
    if ev:
        s += min(max(ev - 88, 0), 12)
    if barrel:
        s += min(barrel / 3, 10)
    if blast == "high":
        s += 4
    elif blast == "good":
        s += 2
    return min(98, max(58, int(round(s))))


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
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = " ".join((row.get("Game") or "").replace("  ", " ").split())
            if not key:
                continue
            out[key] = {
                "hr_pct": _pct_value(row.get("HR %")),
                "hr_weather": _pct_value(row.get("HR % Weather")),
                "hr_stadium": _pct_value(row.get("HR % Stadium")),
            }
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
    apply_probable_overrides(games_csv)
    pitcher_risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
    park_context = load_park_context(DATE)

    batter_ctx: dict[str, dict] = {}
    for g in games_csv.values():
        for row in g["batters"].values():
            vs = row["vs"]
            if vs == g["away_sp"]:
                team = g["home"]
            elif vs == g["home_sp"]:
                team = g["away"]
            else:
                continue
            batter_ctx[name_lookup_key(row["name"])] = {
                "game": g["key"],
                "team": team,
                "opp_sp": vs,
                "row": row,
            }

    fav_names: set[str] = set()
    gem_names: set[str] = set()
    selected: list[str] = []
    for raw in RAW_PROPS:
        clean = raw.strip()
        fav = clean.endswith("⭐")
        gem = clean.endswith("💎")
        if fav:
            clean = clean[:-1].strip()
        elif gem:
            clean = clean[:-1].strip()
        clean = ALIASES.get(clean, clean)
        selected.append(clean)
        if fav:
            fav_names.add(clean)
        if gem:
            gem_names.add(clean)

    missing: list[str] = []
    props: list[tuple] = []
    team_map: dict[str, str] = {}
    for name in selected:
        ctx = batter_ctx.get(name_lookup_key(name))
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
        score = score_from_stats(hr, near, ev, barrel, blast)
        team_map[name] = ctx["team"]
        props.append((name, hand, odds, score, ctx["opp_sp"], hr, near, ev, barrel, blast, ctx["game"]))

    favs_display = sorted(
        [display(name, next(p[1] for p in props if p[0] == name)) for name in fav_names if any(p[0] == name for p in props)]
    )
    gems_display = sorted(
        [display(name, next(p[1] for p in props if p[0] == name)) for name in gem_names if any(p[0] == name for p in props)]
    )

    game_meta: list[dict] = []
    bum_pitchers: set[str] = set()
    for g in sorted(games_csv.values(), key=lambda x: x["key"]):
        away_r = resolve_pitcher(pitcher_risk, g["away_sp_full"]) or resolve_pitcher(pitcher_risk, g["away_sp"])
        home_r = resolve_pitcher(pitcher_risk, g["home_sp_full"]) or resolve_pitcher(pitcher_risk, g["home_sp"])
        if away_r and away_r["overall"] >= 1.0:
            bum_pitchers.add(g["away_sp"])
        if home_r and home_r["overall"] >= 1.0:
            bum_pitchers.add(g["home_sp"])
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
        '"""Generate games[] block for 2026-06-12 MLB HR cheat sheet."""',
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
        hand = next(p[1] for p in props if p[0] == name)
        lines.append(f'    "{display(name, hand)}": "{team}",')
    lines.extend(["}", "", "BUM_PITCHERS = {"])
    for b in sorted(bum_pitchers):
        lines.append(f'    "{b}",')
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
            "def add_bum_row_emojis(entry):",
            '    chip = entry["chips"][0].replace("vs ", "").strip()',
            "    if chip not in BUM_PITCHERS:",
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
        if away_r and away_r["overall"] >= 1.0:
            away_sp_label = f"{away_sp_label} 🧤"
        if home_r and home_r["overall"] >= 1.0:
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
            if away_r and away_r["overall"] >= 1.0 and "🧤" not in away_name:
                away_name = f"{away_name} 🧤"
            if home_r and home_r["overall"] >= 1.0 and "🧤" not in home_name:
                home_name = f"{home_name} 🧤"
            game_title = f"{key_part} - {away_name}{away_tail} vs {home_name}{home_tail}"
        lines.append("    {")
        lines.append(f'        "title": {json.dumps(game_title, ensure_ascii=False)},')
        lines.append(f'        "description": {json.dumps(desc, ensure_ascii=False)},')
        lines.append('        "rows": [')
        for p in prop_by_game[gm["key"]]:
            name, hand, odds, score, chip, hr, near, ev, barrel, blast, _game = p
            is_fav = display(name, hand) in favs_display
            is_gem = display(name, hand) in gems_display
            em = emoji_string(is_fav, is_gem, ev, score, blast)
            risk = resolve_pitcher(pitcher_risk, chip)
            if risk:
                split = risk["vs_lhb"] if hand == "L" else risk["vs_rhb"]
                split_side = "LHB" if hand == "L" else "RHB"
                matchup = f"{chip} {split_side} split {split:+.2f}, HR risk {risk['overall']:.2f}"
            else:
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
            "    for entry in game['rows']:",
            "        add_bum_row_emojis(entry)",
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
            "    out = ROOT / '_games-0612.txt'",
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
