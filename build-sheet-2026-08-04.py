#!/usr/bin/env python3
"""Generate games[] block for 2026-08-04 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Brandon Lowe (L)",
    "Bryce Harper (L)",
    "Griffin Conine (L)",
    "Jake Bauers (L)",
    "Junior Caminero (R)",
    "Miguel Vargas (R)",
    "Owen Caissie (L)",
    "Pete Alonso (R)",
}

GEMS = {
    "J.T. Realmuto (R)",
    "John Rave (L)",
    "Nelson Velazquez (R)",
}

PLAYER_TEAMS = {
    "Austin Wells (L)": "NYY",
    "Ben Rice (L)": "NYY",
    "Brandon Lowe (L)": "PIT",
    "Bryce Harper (L)": "PHI",
    "Carlos Cortes (L)": "ATH",
    "Carter Jensen (L)": "KC",
    "Cole Young (L)": "SEA",
    "Colson Montgomery (L)": "CWS",
    "Corey Seager (L)": "TEX",
    "Daniel Susac (R)": "SF",
    "Daulton Varsho (L)": "HOU",
    "Dylan Crews (R)": "WSH",
    "Eugenio Suarez (R)": "CIN",
    "Freddie Freeman (L)": "LAD",
    "George Springer (R)": "TOR",
    "Gleyber Torres (R)": "DET",
    "Griffin Conine (L)": "MIA",
    "Hao-Yu Lee (R)": "DET",
    "Heliot Ramos (R)": "NYY",
    "Hunter Goodman (R)": "COL",
    "J.T. Realmuto (R)": "PHI",
    "JJ Bleday (L)": "CIN",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "John Rave (L)": "KC",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kevin McGonigle (L)": "DET",
    "Lawrence Butler (L)": "ATH",
    "Luis Garcia Jr. (L)": "NYY",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Michael Conforto (L)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Mike Yastrzemski (L)": "ATL",
    "Nelson Velazquez (R)": "STL",
    "Owen Caissie (L)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Rhys Hoskins (R)": "CLE",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Shohei Ohtani (L)": "LAD",
    "Taylor Trammell (L)": "HOU",
    "Tim Tawa (R)": "ARI",
    "Ty France (R)": "SD",
    "Tyler Soderstrom (L)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "Victor Mesa Jr. (L)": "TB",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
}

BUM_MATCHUPS = {
    ("LAA @ BAL", "Rodriguez"),
    ("MIN @ KC", "Ryan"),
    ("WSH @ PHI", "Littell"),
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
    chip_last = chip.split()[-1] if chip else chip
    if (game_key, chip) not in BUM_MATCHUPS and (game_key, chip_last) not in BUM_MATCHUPS:
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
        "title": "ATH @ CIN - JT Ginn (R, ATH) vs Brady Singer (R, CIN)",
        "description": "Tail key data: Park boost +18% (stadium +15%, weather +3%). Ginn (HR risk -0.16, vs LHB +0.08, vs RHB -0.27). Singer (HR risk -0.49, vs LHB -0.09, vs RHB -0.14).",
        "rows": [
            row("Tyler Stephenson", "R", "+479", 65, "", ["vs Ginn"], """1 HR, 1 near-HR, 97.2 mph EV. Ginn RHB split -0.27, HR risk -0.16. slight split headwind (-0.27); pitcher risk below avg (-0.16).""", blast="good"),
            row("Eugenio Suarez", "R", "+416", 63, "", ["vs Ginn"], """1 HR, 1 near-HR, 93.6 mph EV. Ginn RHB split -0.27, HR risk -0.16. slight split headwind (-0.27); pitcher risk below avg (-0.16).""", blast="good"),
            row("JJ Bleday", "L", "+330", 72, "🌕 💣", ["vs Ginn"], """2 HR, 2 near-HR, 89.9 mph EV. Ginn LHB split +0.08, HR risk -0.16. pitcher risk below avg (-0.16).""", blast="high"),
            row("Sal Stewart", "R", "+380", 80, "🌕 💣", ["vs Ginn"], """3 HR, 3 near-HR, 92.6 mph EV. Ginn RHB split -0.27, HR risk -0.16. slight split headwind (-0.27); pitcher risk below avg (-0.16).""", blast="high"),
            row("Carlos Cortes", "L", "+600", 60, "", ["vs Singer"], """0 HR, 1 near-HR, 96.9 mph EV. Singer LHB split -0.09, HR risk -0.49. slight split headwind (-0.09); pitcher suppresses HR (-0.49).""", blast="good"),
            row("Tyler Soderstrom", "L", "+328", 58, "", ["vs Singer"], """0 HR, 93.7 mph EV. Singer LHB split -0.09, HR risk -0.49. slight split headwind (-0.09); pitcher suppresses HR (-0.49).""", blast="good"),
            row("Lawrence Butler", "L", "+375", 61, "", ["vs Singer"], """0 HR, 2 near-HR, 97.6 mph EV. Singer LHB split -0.09, HR risk -0.49. slight split headwind (-0.09); pitcher suppresses HR (-0.49).""", blast="good"),
        ],
    },
    {
        "title": "CWS @ BOS - Davis Martin (R, CWS) vs Patrick Sandoval (L, BOS)",
        "description": "Tail key data: Park boost data unavailable. Martin (HR risk -0.44, vs LHB -0.18, vs RHB -0.33). Sandoval (HR risk 0.12, vs LHB +0.50, vs RHB -0.30).",
        "rows": [
            row("Willson Contreras", "R", "+360", 58, "", ["vs Martin"], """0 HR, 88.6 mph EV. Martin RHB split -0.33, HR risk -0.44. slight split headwind (-0.33); pitcher suppresses HR (-0.44)."""),
            row("Miguel Vargas", "R", "+425", 58, "⭐", ["vs Sandoval"], """Worst Pickz Favorite. 0 HR, 96.3 mph EV. Sandoval RHB split -0.30, HR risk 0.12. slight split headwind (-0.30); limited recent HR events.""", blast="good"),
            row("Colson Montgomery", "L", "+510", 58, "", ["vs Sandoval"], """0 HR, 85.2 mph EV. Sandoval LHB split +0.50, HR risk 0.12. limited recent HR events; lighter EV form (85.2 mph)."""),
        ],
    },
    {
        "title": "DET @ SEA - Troy Melton (R, DET) vs Emerson Hancock (R, SEA)",
        "description": "Tail key data: Park boost -1% (stadium +0%, weather -1%). Melton (HR risk -0.18, vs LHB +0.44, vs RHB -0.66). Hancock (HR risk 0.16, vs LHB +0.24, vs RHB -0.04).",
        "rows": [
            row("Cole Young", "L", "+600", 66, "", ["vs Melton"], """1 HR, 1 near-HR, 98.8 mph EV. Melton LHB split +0.44, HR risk -0.18. pitcher risk below avg (-0.18).""", blast="good"),
            row("Hao-Yu Lee", "R", "+650", 64, "", ["vs Hancock"], """1 HR, 1 near-HR, 95.1 mph EV. Hancock RHB split -0.04, HR risk 0.16. slight split headwind (-0.04).""", blast="good"),
            row("Gleyber Torres", "R", "+980", 59, "", ["vs Hancock"], """1 HR, 1 near-HR, 89.7 mph EV. Hancock RHB split -0.04, HR risk 0.16. slight split headwind (-0.04).""", blast="good"),
            row("Kevin McGonigle", "L", "+625", 59, "", ["vs Hancock"], """1 HR, 1 near-HR, 87.6 mph EV. Hancock LHB split +0.24, HR risk 0.16. lighter EV form (87.6 mph).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ BAL - Grayson Rodriguez 🧤 (R, LAA) vs Cade Povich (L, BAL)",
        "description": "Tail key data: Park boost -5% (stadium -7%, weather +2%). Rodriguez 🧤 (HR risk 1.16, vs LHB +0.59, vs RHB +0.74). Povich (HR risk 0.40, vs LHB +0.44, vs RHB -0.01).",
        "rows": [
            row("Pete Alonso", "R", "+285", 84, "⭐", ["vs Grayson Rodriguez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.7 mph EV. Grayson Rodriguez RHB split +0.74, HR risk 1.16. park/weather net drag (-5%).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ CHC - Tarik Skubal (L, LAD) vs Javier Assad (R, CHC)",
        "description": "Tail key data: Park boost +21% (stadium -1%, weather +22%). Skubal (HR risk 0.41, vs LHB +0.28, vs RHB +0.42). Assad (HR risk 0.74, vs LHB +0.71, vs RHB +0.03).",
        "rows": [
            row("Michael Conforto", "L", "N/A", 79, "🚀", ["vs Skubal"], """1 HR, 1 near-HR, 106.2 mph EV. Skubal LHB split +0.28, HR risk 0.41.""", blast="good"),
            row("Shohei Ohtani", "L", "+349", 81, "", ["vs Assad"], """1 HR, 1 near-HR, 92.4 mph EV. Assad LHB split +0.71, HR risk 0.74.""", blast="good"),
            row("Freddie Freeman", "L", "+630", 68, "", ["vs Assad"], """0 HR, 88.7 mph EV. Assad LHB split +0.71, HR risk 0.74. limited recent HR events."""),
        ],
    },
    {
        "title": "MIA @ ATL - Ryan Gusto (R, MIA) vs Grant Holmes (R, ATL)",
        "description": "Tail key data: Park boost +2% (stadium +0%, weather +2%). Gusto (HR risk 0.04, vs LHB +0.13, vs RHB -0.09). Holmes (HR risk 0.35, vs LHB +0.52, vs RHB -0.02).",
        "rows": [
            row("Ronald Acuna Jr.", "R", "+450", 74, "🌕 💣", ["vs Gusto"], """2 HR, 2 near-HR, 98.4 mph EV. Gusto RHB split -0.09, HR risk 0.04. slight split headwind (-0.09).""", blast="high"),
            row("Mike Yastrzemski", "L", "+500", 61, "", ["vs Gusto"], """1 HR, 1 near-HR, 90.6 mph EV. Gusto LHB split +0.13, HR risk 0.04.""", blast="good"),
            row("Matt Olson", "L", "+322", 71, "🌕 💣", ["vs Gusto"], """2 HR, 2 near-HR, 90.9 mph EV. Gusto LHB split +0.13, HR risk 0.04.""", blast="high"),
            row("Owen Caissie", "L", "+550", 86, "⭐ 🌕 💣", ["vs Holmes"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.8 mph EV. Holmes LHB split +0.52, HR risk 0.35.""", blast="high"),
            row("Griffin Conine", "L", "N/A", 58, "⭐", ["vs Holmes"], """Worst Pickz Favorite. 0 HR, 90.8 mph EV. Holmes LHB split +0.52, HR risk 0.35. limited recent HR events."""),
            row("Joe Mack", "L", "+690", 58, "", ["vs Holmes"], """0 HR, 71.6 mph EV. Holmes LHB split +0.52, HR risk 0.35. limited recent HR events; lighter EV form (71.6 mph)."""),
        ],
    },
    {
        "title": "MIN @ KC - Joe Ryan 🧤 (R, MIN) vs Randy Dobnak (R, KC)",
        "description": "Tail key data: Park boost +10% (stadium +12%, weather -2%). Ryan 🧤 (HR risk 1.35, vs LHB +1.20, vs RHB +0.63). Dobnak (HR risk -0.27, vs LHB -0.33, vs RHB +0.22).",
        "rows": [
            row("John Rave", "L", "+800", 91, "🌕 💣 💎", ["vs Ryan"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 88.2 mph EV. Ryan LHB split +1.20, HR risk 1.35.""", blast="good"),
            row("Salvador Perez", "R", "+438", 94, "🌕 💣", ["vs Ryan"], """2 HR, 4 near-HR, 90.4 mph EV. Ryan RHB split +0.63, HR risk 1.35.""", blast="high"),
            row("Carter Jensen", "L", "+425", 90, "🌕 💣", ["vs Ryan"], """1 HR, 1 near-HR, 92.5 mph EV. Ryan LHB split +1.20, HR risk 1.35.""", blast="good"),
            row("Royce Lewis", "R", "+477", 60, "", ["vs Dobnak"], """0 HR, 95.4 mph EV. Dobnak RHB split +0.22, HR risk -0.27. pitcher risk below avg (-0.27); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "NYM @ CLE - Sean Manaea (L, NYM) vs Joey Cantillo (L, CLE)",
        "description": "Tail key data: Park boost -13% (stadium -4%, weather -9%). Manaea (HR risk 0.72, vs LHB +0.10, vs RHB +0.80). Cantillo (HR risk -0.24, vs LHB -0.02, vs RHB -0.27).",
        "rows": [
            row("Rhys Hoskins", "R", "+395", 74, "", ["vs Manaea"], """1 HR, 2 near-HR, 91.7 mph EV. Manaea RHB split +0.80, HR risk 0.72. park/weather net drag (-13%).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ MIL - Jared Jones (R, PIT) vs Logan Henderson (R, MIL)",
        "description": "Tail key data: Park boost +18% (stadium +11%, weather +6%). Jones (HR risk -0.20, vs LHB -0.10, vs RHB -0.12). Henderson (HR risk 0.13, vs LHB -0.03, vs RHB +0.17).",
        "rows": [
            row("Jake Bauers", "L", "+395", 80, "⭐ 🌕 💣", ["vs Jones"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 99.3 mph EV. Jones LHB split -0.10, HR risk -0.20. slight split headwind (-0.10); pitcher risk below avg (-0.20).""", blast="high"),
            row("Brandon Lowe", "L", "+288", 64, "⭐", ["vs Henderson"], """Worst Pickz Favorite. 0 HR, 96.2 mph EV. Henderson LHB split -0.03, HR risk 0.13. slight split headwind (-0.03); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "SD @ ARI - Randy Vasquez (R, SD) vs Eduardo Rodriguez (L, ARI)",
        "description": "Tail key data: Park boost -9% (stadium -8%, weather +0%). Vasquez (HR risk 0.68, vs LHB +0.56, vs RHB +0.13). Rodriguez (HR risk 0.13, vs LHB +0.12, vs RHB +0.07).",
        "rows": [
            row("Tim Tawa", "R", "+750", 64, "", ["vs Vasquez"], """1 HR, 2 near-HR, 86.5 mph EV. Vasquez RHB split +0.13, HR risk 0.68. park/weather net drag (-9%); lighter EV form (86.5 mph).""", blast="good"),
            row("Manny Machado", "R", "+443", 62, "", ["vs Eduardo Rodriguez"], """1 HR, 1 near-HR, 94.3 mph EV. Eduardo Rodriguez RHB split +0.07, HR risk 0.13. park/weather net drag (-9%).""", blast="good"),
            row("Jackson Merrill", "L", "+571", 64, "", ["vs Eduardo Rodriguez"], """1 HR, 1 near-HR, 97.9 mph EV. Eduardo Rodriguez LHB split +0.12, HR risk 0.13. park/weather net drag (-9%).""", blast="good"),
            row("Ty France", "R", "+544", 58, "", ["vs Eduardo Rodriguez"], """0 HR, 95.5 mph EV. Eduardo Rodriguez RHB split +0.07, HR risk 0.13. park/weather net drag (-9%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "SF @ TEX - Blade Tidwell (R, SF) vs MacKenzie Gore (L, TEX)",
        "description": "Tail key data: Park boost -12% (stadium -11%, weather +0%). Tidwell (HR risk -0.09, vs LHB +0.11, vs RHB -0.04). Gore (HR risk 0.73, vs LHB -0.03, vs RHB +0.95).",
        "rows": [
            row("Corey Seager", "L", "+333", 68, "", ["vs Tidwell"], """1 HR, 3 near-HR, 97.0 mph EV. Tidwell LHB split +0.11, HR risk -0.09. pitcher risk below avg (-0.09); park/weather net drag (-12%).""", blast="good"),
            row("Joc Pederson", "L", "+355", 71, "🌕 💣", ["vs Tidwell"], """2 HR, 2 near-HR, 96.8 mph EV. Tidwell LHB split +0.11, HR risk -0.09. pitcher risk below avg (-0.09); park/weather net drag (-12%).""", blast="high"),
            row("Willy Adames", "R", "+508", 79, "", ["vs Gore"], """1 HR, 3 near-HR, 90.8 mph EV. Gore RHB split +0.95, HR risk 0.73. park/weather net drag (-12%).""", blast="good"),
            row("Daniel Susac", "R", "+810", 83, "🌕 💣", ["vs Gore"], """2 HR, 2 near-HR, 91.2 mph EV. Gore RHB split +0.95, HR risk 0.73. park/weather net drag (-12%).""", blast="high"),
        ],
    },
    {
        "title": "STL @ NYY - Hunter Dobbins (R, STL) vs Ryan Weathers (L, NYY)",
        "description": "Tail key data: Park boost +8% (stadium +4%, weather +5%). Dobbins (HR risk 0.09, vs LHB -0.17, vs RHB +0.27). Weathers (HR risk 0.15, vs LHB -0.13, vs RHB +0.36).",
        "rows": [
            row("Luis Garcia Jr.", "L", "+460", 66, "", ["vs Dobbins"], """1 HR, 2 near-HR, 94.4 mph EV. Dobbins LHB split -0.17, HR risk 0.09. slight split headwind (-0.17).""", blast="good"),
            row("Ben Rice", "L", "+310", 62, "", ["vs Dobbins"], """0 HR, 1 near-HR, 99.7 mph EV. Dobbins LHB split -0.17, HR risk 0.09. slight split headwind (-0.17); limited recent HR events.""", blast="good"),
            row("Heliot Ramos", "R", "+450", 58, "", ["vs Dobbins"], """0 HR, 87.4 mph EV. Dobbins RHB split +0.27, HR risk 0.09. limited recent HR events; lighter EV form (87.4 mph)."""),
            row("Ryan McMahon", "L", "+500", 66, "", ["vs Dobbins"], """1 HR, 1 near-HR, 96.7 mph EV. Dobbins LHB split -0.17, HR risk 0.09. slight split headwind (-0.17).""", blast="good"),
            row("Austin Wells", "L", "+470", 58, "", ["vs Dobbins"], """0 HR, 92.2 mph EV. Dobbins LHB split -0.17, HR risk 0.09. slight split headwind (-0.17); limited recent HR events.""", blast="good"),
            row("Nelson Velazquez", "R", "+448", 69, "💎", ["vs Weathers"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 92.8 mph EV. Weathers RHB split +0.36, HR risk 0.15.""", blast="good"),
        ],
    },
    {
        "title": "TB @ COL - Freddy Peralta (R, TB) vs Gabriel Hughes (R, COL)",
        "description": "Tail key data: Park boost +19% (stadium +17%, weather +2%). Peralta (HR risk 0.29, vs LHB +0.41, vs RHB -0.03). Hughes (HR risk -0.21, vs LHB -0.18, vs RHB -0.02).",
        "rows": [
            row("Hunter Goodman", "R", "+280", 63, "", ["vs Peralta"], """1 HR, 2 near-HR, 83.5 mph EV. Peralta RHB split -0.03, HR risk 0.29. slight split headwind (-0.03); lighter EV form (83.5 mph).""", blast="good"),
            row("Junior Caminero", "R", "+230", 85, "⭐ 🌕 💣", ["vs Hughes"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 98.6 mph EV. Hughes RHB split -0.02, HR risk -0.21. slight split headwind (-0.02); pitcher risk below avg (-0.21).""", blast="high"),
            row("Victor Mesa Jr.", "L", "+441", 58, "", ["vs Hughes"], """0 HR, 2 near-HR, 87.0 mph EV. Hughes LHB split -0.18, HR risk -0.21. slight split headwind (-0.18); pitcher risk below avg (-0.21).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ HOU - Trey Yesavage (R, TOR) vs Hayden Wesneski (R, HOU)",
        "description": "Tail key data: Park boost +6% (stadium +6%, weather -1%). Yesavage (HR risk 0.46, vs LHB +0.18, vs RHB +0.40). Wesneski (HR risk -0.03, vs LHB +0.00, vs RHB +0.02).",
        "rows": [
            row("Daulton Varsho", "L", "+581", 69, "", ["vs Yesavage"], """0 HR, 2 near-HR, 92.8 mph EV. Yesavage LHB split +0.18, HR risk 0.46.""", blast="good"),
            row("Taylor Trammell", "L", "+660", 73, "", ["vs Yesavage"], """1 HR, 2 near-HR, 92.8 mph EV. Yesavage LHB split +0.18, HR risk 0.46.""", blast="good"),
            row("George Springer", "R", "+560", 66, "", ["vs Wesneski"], """1 HR, 1 near-HR, 96.1 mph EV. Wesneski RHB split +0.02, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="good"),
            row("Kazuma Okamoto", "R", "+450", 58, "", ["vs Wesneski"], """0 HR, 85.6 mph EV. Wesneski RHB split +0.02, HR risk -0.03. pitcher risk below avg (-0.03); limited recent HR events."""),
        ],
    },
    {
        "title": "WSH @ PHI - Zack Littell 🧤 (R, WSH) vs Jesus Luzardo (L, PHI)",
        "description": "Tail key data: Park boost data unavailable. Littell 🧤 (HR risk 1.03, vs LHB +0.76, vs RHB +0.35). Luzardo (HR risk -0.11, vs LHB -0.16, vs RHB +0.52).",
        "rows": [
            row("Bryce Harper", "L", "+277", 92, "⭐ 🌕 💣", ["vs Littell"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.2 mph EV. Littell LHB split +0.76, HR risk 1.03.""", blast="high"),
            row("J.T. Realmuto", "R", "+560", 83, "💎", ["vs Littell"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 96.9 mph EV. Littell RHB split +0.35, HR risk 1.03.""", blast="good"),
            row("Dylan Crews", "R", "+592", 81, "🌕 💣", ["vs Luzardo"], """2 HR, 3 near-HR, 95.7 mph EV. Luzardo RHB split +0.52, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="high"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-04")

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

    out = ROOT / '_games-0804.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
