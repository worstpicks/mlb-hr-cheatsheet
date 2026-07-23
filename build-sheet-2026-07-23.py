#!/usr/bin/env python3
"""Generate games[] block for 2026-07-23 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Jac Caglianone (L)",
    "Matt Olson (L)",
    "Patrick Bailey (S)",
    "Riley Greene (L)",
    "Royce Lewis (R)",
    "Ryan Jeffers (R)",
    "Trevor Larnach (L)",
}

GEMS = {
    "Jimmy Crooks (L)",
    "Kyle Manzardo (L)",
    "Mike Yastrzemski (L)",
}

PLAYER_TEAMS = {
    "Adrian Del Castillo (L)": "ARI",
    "Austin Riley (R)": "ATL",
    "Carter Jensen (L)": "KC",
    "Cedric Mullins (L)": "TB",
    "Chase DeLauter (L)": "CLE",
    "Colt Keith (L)": "DET",
    "Corbin Carroll (L)": "ARI",
    "Daulton Varsho (L)": "TOR",
    "Drake Baldwin (L)": "ATL",
    "Fernando Tatis Jr. (R)": "SD",
    "George Springer (R)": "TOR",
    "Hunter Feduccia (L)": "TB",
    "Jac Caglianone (L)": "KC",
    "Jimmy Crooks (L)": "STL",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kevin McGonigle (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Kyle Manzardo (L)": "CLE",
    "Lars Nootbaar (L)": "STL",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Mike Yastrzemski (L)": "ATL",
    "Patrick Bailey (S)": "CLE",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Royce Lewis (R)": "MIN",
    "Ryan Jeffers (R)": "MIN",
    "Ryan Waldschmidt (R)": "ARI",
    "Salvador Perez (R)": "KC",
    "Starling Marte (R)": "KC",
    "Tim Tawa (R)": "ARI",
    "Trevor Larnach (L)": "MIN",
}

BUM_MATCHUPS = {
    ("TB @ TOR", "Bieber"),
}

def odds_text(odds):
    return "Listed prop - Over 0.5 HR" if odds == "N/A" else f"Listed {odds} - Over 0.5 HR"

def row(name, hand, odds, score, emojis, chips, note, blast=None):
    item = {
        "name": f"{name} ({hand})",
        "odds": odds_text(odds),
        "score": score,
        "emojis": emojis,
        "note": note,
        "chips": chips,
    }
    if blast:
        item["blast"] = blast
    return item

def add_bum_row_emojis(entry, game_key):
    chip = entry["chips"][0].replace("vs ", "").strip()
    if (game_key, chip) not in BUM_MATCHUPS:
        return
    em = entry["emojis"]
    if "⚾" not in em:
        em = f"{em} ⚾".strip()
    if "🕊️" not in em:
        em = f"{em} 🕊️".strip()
    if "🧤" not in em:
        em = f"{em} 🧤".strip()
    entry["emojis"] = em

games = [
    {
        "title": "ARI @ STL - Brandon Pfaadt (R, ARI) vs Michael McGreevy (R, STL)",
        "description": "Tail key data: Park boost -26% (stadium -10%, weather -16%). Pfaadt (HR risk -0.71, vs LHB -0.08, vs RHB -0.72). McGreevy (HR risk -0.17, vs LHB -0.00, vs RHB -0.25).",
        "rows": [
            row("Lars Nootbaar", "L", "+700", 58, "", ["vs Pfaadt"], """1 HR, 1 near-HR, 93.9 mph EV. Pfaadt LHB split -0.08, HR risk -0.71. slight split headwind (-0.08); pitcher suppresses HR (-0.71).""", blast="good"),
            row("Jimmy Crooks", "L", "+810", 58, "💎", ["vs Pfaadt"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 96.0 mph EV. Pfaadt LHB split -0.08, HR risk -0.71. slight split headwind (-0.08); pitcher suppresses HR (-0.71).""", blast="good"),
            row("Corbin Carroll", "L", "+450", 58, "", ["vs McGreevy"], """1 HR, 2 near-HR, 94.1 mph EV. McGreevy LHB split -0.00, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-26%).""", blast="good"),
            row("Tim Tawa", "R", "+870", 58, "", ["vs McGreevy"], """0 HR, 1 near-HR, 91.3 mph EV. McGreevy RHB split -0.25, HR risk -0.17. slight split headwind (-0.25); pitcher risk below avg (-0.17)."""),
            row("Ryan Waldschmidt", "R", "+1400", 58, "", ["vs McGreevy"], """1 HR, 1 near-HR, 88.4 mph EV. McGreevy RHB split -0.25, HR risk -0.17. slight split headwind (-0.25); pitcher risk below avg (-0.17).""", blast="good"),
            row("Adrian Del Castillo", "L", "+367", 58, "", ["vs McGreevy"], """1 HR, 1 near-HR, 89.1 mph EV. McGreevy LHB split -0.00, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-26%).""", blast="good"),
        ],
    },
    {
        "title": "KC @ DET - Randy Dobnak (R, KC) vs Troy Melton (R, DET)",
        "description": "Tail key data: Park boost -21% (stadium -10%, weather -11%). Dobnak (HR risk -0.30, vs LHB -0.77, vs RHB +0.57). Melton (HR risk -0.77, vs LHB +0.06, vs RHB -1.12).",
        "rows": [
            row("Riley Greene", "L", "+393", 69, "⭐ 🌕 💣", ["vs Dobnak"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 95.8 mph EV. Dobnak LHB split -0.77, HR risk -0.30. tough split lane (-0.77); pitcher risk below avg (-0.30).""", blast="high"),
            row("Kevin McGonigle", "L", "+650", 58, "", ["vs Dobnak"], """1 HR, 1 near-HR, 90.1 mph EV. Dobnak LHB split -0.77, HR risk -0.30. tough split lane (-0.77); pitcher risk below avg (-0.30).""", blast="good"),
            row("Colt Keith", "L", "+870", 58, "", ["vs Dobnak"], """1 HR, 1 near-HR, 91.4 mph EV. Dobnak LHB split -0.77, HR risk -0.30. tough split lane (-0.77); pitcher risk below avg (-0.30).""", blast="good"),
            row("Jac Caglianone", "L", "N/A", 58, "⭐", ["vs Melton"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.1 mph EV. Melton LHB split +0.06, HR risk -0.77. pitcher suppresses HR (-0.77); park/weather net drag (-21%).""", blast="good"),
            row("Starling Marte", "R", "+1250", 58, "", ["vs Melton"], """1 HR, 1 near-HR, 97.0 mph EV. Melton RHB split -1.12, HR risk -0.77. tough split lane (-1.12); pitcher suppresses HR (-0.77).""", blast="good"),
            row("Salvador Perez", "R", "+491", 65, "🌕 💣", ["vs Melton"], """3 HR, 3 near-HR, 96.1 mph EV. Melton RHB split -1.12, HR risk -0.77. tough split lane (-1.12); pitcher suppresses HR (-0.77).""", blast="high"),
            row("Carter Jensen", "L", "+542", 59, "", ["vs Melton"], """1 HR, 3 near-HR, 96.3 mph EV. Melton LHB split +0.06, HR risk -0.77. pitcher suppresses HR (-0.77); park/weather net drag (-21%).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ CLE - Taj Bradley (R, MIN) vs Gavin Williams (R, CLE)",
        "description": "Tail key data: Park boost -11% (stadium -3%, weather -8%). Bradley (HR risk 0.14, vs LHB +0.47, vs RHB -0.30). Williams (HR risk 0.70, vs LHB -0.25, vs RHB +1.29).",
        "rows": [
            row("Kyle Manzardo", "L", "+525", 68, "💎", ["vs Bradley"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 95.7 mph EV. Bradley LHB split +0.47, HR risk 0.14. park/weather net drag (-11%).""", blast="good"),
            row("Patrick Bailey", "S", "+900", 67, "⭐", ["vs Bradley"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.8 mph EV. Bradley SHB→LHB split +0.47, HR risk 0.14. park/weather net drag (-11%).""", blast="good"),
            row("Rhys Hoskins", "R", "+437", 61, "", ["vs Bradley"], """1 HR, 1 near-HR, 96.0 mph EV. Bradley RHB split -0.30, HR risk 0.14. slight split headwind (-0.30); park/weather net drag (-11%).""", blast="good"),
            row("Chase DeLauter", "L", "+500", 67, "", ["vs Bradley"], """1 HR, 1 near-HR, 96.8 mph EV. Bradley LHB split +0.47, HR risk 0.14. park/weather net drag (-11%).""", blast="good"),
            row("Trevor Larnach", "L", "+597", 78, "⭐ 🌕 💣", ["vs Williams"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.2 mph EV. Williams LHB split -0.25, HR risk 0.70. slight split headwind (-0.25); park/weather net drag (-11%).""", blast="high"),
            row("Kody Clemens", "L", "+428", 58, "", ["vs Williams"], """0 HR, 91.6 mph EV. Williams LHB split -0.25, HR risk 0.70. slight split headwind (-0.25); park/weather net drag (-11%)."""),
            row("Ryan Jeffers", "R", "+470", 90, "⭐ 🌕 💣", ["vs Williams"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 91.5 mph EV. Williams RHB split +1.29, HR risk 0.70. park/weather net drag (-11%).""", blast="high"),
            row("Royce Lewis", "R", "+500", 80, "⭐", ["vs Williams"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.3 mph EV. Williams RHB split +1.29, HR risk 0.70. park/weather net drag (-11%).""", blast="good"),
        ],
    },
    {
        "title": "SD @ ATL - Griffin Canning (R, SD) vs Chris Sale (L, ATL)",
        "description": "Tail key data: Park boost +0% (stadium -4%, weather +4%). Canning (HR risk -0.29, vs LHB -0.29, vs RHB -0.28). Sale (HR risk -0.98, vs LHB -1.60, vs RHB -0.29).",
        "rows": [
            row("Matt Olson", "L", "+320", 58, "⭐", ["vs Canning"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.3 mph EV. Canning LHB split -0.29, HR risk -0.29. slight split headwind (-0.29); pitcher risk below avg (-0.29).""", blast="good"),
            row("Drake Baldwin", "L", "+400", 59, "", ["vs Canning"], """1 HR, 1 near-HR, 95.3 mph EV. Canning LHB split -0.29, HR risk -0.29. slight split headwind (-0.29); pitcher risk below avg (-0.29).""", blast="good"),
            row("Austin Riley", "R", "+446", 58, "", ["vs Canning"], """1 HR, 1 near-HR, 92.6 mph EV. Canning RHB split -0.28, HR risk -0.29. slight split headwind (-0.28); pitcher risk below avg (-0.29).""", blast="good"),
            row("Mike Yastrzemski", "L", "+650", 58, "💎", ["vs Canning"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 87.6 mph EV. Canning LHB split -0.29, HR risk -0.29. slight split headwind (-0.29); pitcher risk below avg (-0.29).""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+550", 59, "🌕 💣", ["vs Sale"], """2 HR, 2 near-HR, 92.4 mph EV. Sale RHB split -0.29, HR risk -0.98. slight split headwind (-0.29); pitcher suppresses HR (-0.98).""", blast="high"),
            row("Manny Machado", "R", "+438", 58, "", ["vs Sale"], """1 HR, 3 near-HR, 90.9 mph EV. Sale RHB split -0.29, HR risk -0.98. slight split headwind (-0.29); pitcher suppresses HR (-0.98).""", blast="good"),
        ],
    },
    {
        "title": "TB @ TOR - Ian Seymour (L, TB) vs Shane Bieber 🧤 (R, TOR)",
        "description": "Tail key data: Park boost -1% (stadium +6%, weather -7%). Seymour (HR risk 0.51, vs LHB +1.70, vs RHB -0.34). Bieber 🧤 (HR risk 1.87, vs LHB +0.76, vs RHB +1.45).",
        "rows": [
            row("Daulton Varsho", "L", "+670", 78, "", ["vs Seymour"], """0 HR, 94.5 mph EV. Seymour LHB split +1.70, HR risk 0.51. weather carry headwind (-7%); limited recent HR events.""", blast="good"),
            row("Kazuma Okamoto", "R", "+330", 79, "🌕 💣", ["vs Seymour"], """2 HR, 2 near-HR, 97.9 mph EV. Seymour RHB split -0.34, HR risk 0.51. slight split headwind (-0.34); weather carry headwind (-7%).""", blast="high"),
            row("George Springer", "R", "+467", 67, "", ["vs Seymour"], """1 HR, 2 near-HR, 91.9 mph EV. Seymour RHB split -0.34, HR risk 0.51. slight split headwind (-0.34); weather carry headwind (-7%).""", blast="good"),
            row("Cedric Mullins", "L", "+453", 78, "", ["vs Bieber"], """1 HR, 1 near-HR, 83.7 mph EV. Bieber LHB split +0.76, HR risk 1.87. weather carry headwind (-7%); lighter EV form (83.7 mph).""", blast="good"),
            row("Hunter Feduccia", "L", "+960", 91, "🌕 💣", ["vs Bieber"], """1 HR, 3 near-HR, 95.1 mph EV. Bieber LHB split +0.76, HR risk 1.87. weather carry headwind (-7%).""", blast="good"),
            row("Junior Caminero", "R", "+242", 86, "", ["vs Bieber"], """0 HR, 93.4 mph EV. Bieber RHB split +1.45, HR risk 1.87. weather carry headwind (-7%); limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-23")

if __name__ == '__main__':
    def js_string(value):
        return json.dumps(value, ensure_ascii=False)

    def emit_games_js(games_data):
        out = ['const games = [']
        for game in games_data:
            out.append('    {')
            out.append(f"        title: {js_string(game['title'])},")
            out.append(f"        description: {js_string(game['description'])},")
            if game.get("startTime"):
                out.append(f"        startTime: {js_string(game['startTime'])},")
            out.append('        rows: [')
            for entry in game['rows']:
                parts = [
                    f"name: {js_string(entry['name'])}",
                    f"odds: {js_string(entry['odds'])}",
                    f"score: {entry['score']}",
                    f"emojis: {js_string(entry['emojis'])}",
                    f"note: {js_string(entry['note'])}",
                    f"chips: {js_string(entry['chips'])}",
                ]
                if entry.get('blast'):
                    parts.append(f"blast: {js_string(entry['blast'])}")
                out.append('            { ' + ', '.join(parts) + ' },')
            out.append('        ],')
            out.append('    },')
        out.append('];')
        return '\n'.join(out)

    out = ROOT / '_games-0711.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
