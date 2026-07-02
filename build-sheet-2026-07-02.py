#!/usr/bin/env python3
"""Generate games[] block for 2026-07-02 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Brandon Lowe (L)",
    "Junior Caminero (R)",
    "Kerry Carpenter (L)",
    "Kyle Manzardo (L)",
    "Manny Machado (R)",
    "Matt Olson (L)",
    "Mickey Moniak (L)",
    "Nelson Velazquez (R)",
    "Owen Caissie (L)",
    "Riley Greene (L)",
    "Spencer Torkelson (R)",
}

GEMS = {
    "Carter Jensen (L)",
    "Cedric Mullins (L)",
    "Dominic Canzone (L)",
    "Edmundo Sosa (R)",
    "Ty France (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Austin Hedges (R)": "CLE",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Brice Turang (L)": "MIL",
    "Bryce Harper (L)": "PHI",
    "Carter Jensen (L)": "KC",
    "Cedric Mullins (L)": "TB",
    "Cole Young (L)": "SEA",
    "Colson Montgomery (L)": "CWS",
    "Dalton Rushing (L)": "LAD",
    "Dominic Canzone (L)": "SEA",
    "Edmundo Sosa (R)": "PHI",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Freddie Freeman (L)": "LAD",
    "Gavin Sheets (L)": "SD",
    "Griffin Conine (L)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Jac Caglianone (L)": "KC",
    "Jake Bauers (L)": "MIL",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "Josh Lowe (L)": "LAA",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kerry Carpenter (L)": "DET",
    "Kevin McGonigle (L)": "DET",
    "Kyle Higashioka (R)": "TEX",
    "Kyle Karros (R)": "COL",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lars Nootbaar (L)": "STL",
    "Manny Machado (R)": "SD",
    "Marcell Ozuna (R)": "PIT",
    "Matt Olson (L)": "ATL",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Mike Yastrzemski (L)": "ATL",
    "Nelson Velazquez (R)": "STL",
    "Noelvi Marte (R)": "CIN",
    "Owen Caissie (L)": "MIA",
    "Ozzie Albies (S)": "ATL",
    "Riley Greene (L)": "DET",
    "Rowdy Tellez (L)": "ATL",
    "Ryan O'Hearn (L)": "PIT",
    "Ryan Vilade (R)": "TB",
    "Sal Stewart (R)": "CIN",
    "Spencer Steer (R)": "CIN",
    "Spencer Torkelson (R)": "DET",
    "Sung-Mun Song (L)": "SD",
    "Travis Bazzana (L)": "CLE",
    "Ty France (R)": "SD",
    "Tyler Stephenson (R)": "CIN",
    "Willi Castro (S)": "COL",
    "William Contreras (R)": "MIL",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("SD @ LAD", "Sasaki"),
    ("SD @ LAD", "Vasquez"),
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
        "title": "CIN @ MIL - Chase Burns (R, CIN) vs Jacob Misiorowski (R, MIL)",
        "description": "Tail key data: Park boost +24% (stadium +10%, weather +14%). Burns (HR risk 0.00, vs LHB +0.29, vs RHB -0.64). Misiorowski (HR risk -1.20, vs LHB -1.32, vs RHB -0.44).",
        "rows": [
            row("William Contreras", "R", "+547", 75, "", ["vs Burns"], """0 HR, 1 near-HR, 97.3 mph EV. Burns RHB split -0.64, HR risk 0.00. tough split lane (-0.64); limited recent HR events.""", blast="good"),
            row("Jake Bauers", "L", "+470", 75, "", ["vs Burns"], """1 HR, 1 near-HR, 93.4 mph EV. Burns LHB split +0.29, HR risk 0.00.""", blast="good"),
            row("Brice Turang", "L", "+600", 62, "", ["vs Burns"], """0 HR, 86.2 mph EV. Burns LHB split +0.29, HR risk 0.00. limited recent HR events; lighter EV form (86.2 mph)."""),
            row("Tyler Stephenson", "R", "N/A", 76, "", ["vs Misiorowski"], """1 HR, 1 near-HR, 90.0 mph EV, 12.0% barrels. Misiorowski RHB split -0.44, HR risk -1.20. tough split lane (-0.44); pitcher suppresses HR (-1.20).""", blast="good"),
            row("Sal Stewart", "R", "N/A", 81, "", ["vs Misiorowski"], """1 HR, 2 near-HR, 92.0 mph EV, 14.0% barrels. Misiorowski RHB split -0.44, HR risk -1.20. tough split lane (-0.44); pitcher suppresses HR (-1.20).""", blast="good"),
            row("Elly De La Cruz", "S", "N/A", 89, "🌕 💣", ["vs Misiorowski"], """2 HR, 2 near-HR, 94.0 mph EV, 16.0% barrels. Misiorowski RHB split -0.44, HR risk -1.20. tough split lane (-0.44); pitcher suppresses HR (-1.20).""", blast="high"),
            row("Noelvi Marte", "R", "N/A", 80, "", ["vs Misiorowski"], """1 HR, 1 near-HR, 93.0 mph EV, 15.0% barrels. Misiorowski RHB split -0.44, HR risk -1.20. tough split lane (-0.44); pitcher suppresses HR (-1.20).""", blast="good"),
            row("Spencer Steer", "R", "N/A", 74, "", ["vs Misiorowski"], """1 HR, 1 near-HR, 88.0 mph EV, 12.0% barrels. Misiorowski RHB split -0.44, HR risk -1.20. tough split lane (-0.44); pitcher suppresses HR (-1.20).""", blast="good"),
        ],
    },
    {
        "title": "CWS @ CLE - Davis Martin (R, CWS) vs Slade Cecconi (R, CLE)",
        "description": "Tail key data: Park boost +19% (stadium -2%, weather +21%). Martin (HR risk -0.32, vs LHB -0.35, vs RHB -0.25). Cecconi (HR risk -0.06, vs LHB +0.17, vs RHB -0.38).",
        "rows": [
            row("Kyle Manzardo", "L", "+420", 80, "⭐ 🌕 💣", ["vs Martin"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.4 mph EV. Martin LHB split -0.35, HR risk -0.32. slight split headwind (-0.35); pitcher risk below avg (-0.32).""", blast="high"),
            row("Austin Hedges", "R", "N/A", 72, "", ["vs Martin"], """1 HR, 2 near-HR, 87.8 mph EV. Martin RHB split -0.25, HR risk -0.32. slight split headwind (-0.25); pitcher risk below avg (-0.32).""", blast="good"),
            row("Travis Bazzana", "L", "+598", 70, "", ["vs Martin"], """1 HR, 1 near-HR, 87.3 mph EV. Martin LHB split -0.35, HR risk -0.32. slight split headwind (-0.35); pitcher risk below avg (-0.32).""", blast="good"),
            row("Colson Montgomery", "L", "+303", 62, "", ["vs Cecconi"], """0 HR, 83.4 mph EV. Cecconi LHB split +0.17, HR risk -0.06. pitcher risk below avg (-0.06); limited recent HR events."""),
            row("Miguel Vargas", "R", "+377", 79, "", ["vs Cecconi"], """1 HR, 2 near-HR, 94.9 mph EV. Cecconi RHB split -0.38, HR risk -0.06. slight split headwind (-0.38); pitcher risk below avg (-0.06).""", blast="good"),
        ],
    },
    {
        "title": "DET @ TEX - Framber Valdez (L, DET) vs Nathan Eovaldi (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -11%, weather +0%). Valdez (HR risk -0.29, vs LHB -0.58, vs RHB +0.04). Eovaldi (HR risk 0.25, vs LHB +0.13, vs RHB +0.14).",
        "rows": [
            row("Justin Foscue", "R", "+750", 63, "", ["vs Valdez"], """0 HR, 88.6 mph EV. Valdez RHB split +0.04, HR risk -0.29. pitcher risk below avg (-0.29); park/weather net drag (-11%)."""),
            row("Joc Pederson", "L", "N/A", 76, "🚀", ["vs Valdez"], """0 HR, 101.5 mph EV. Valdez LHB split -0.58, HR risk -0.29. tough split lane (-0.58); pitcher risk below avg (-0.29).""", blast="good"),
            row("Kyle Higashioka", "R", "+710", 80, "🌕 💣", ["vs Valdez"], """2 HR, 3 near-HR, 87.8 mph EV. Valdez RHB split +0.04, HR risk -0.29. pitcher risk below avg (-0.29); park/weather net drag (-11%).""", blast="high"),
            row("Kerry Carpenter", "L", "+393", 93, "⭐ 🌕 💣", ["vs Eovaldi"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 96.8 mph EV. Eovaldi LHB split +0.13, HR risk 0.25. park/weather net drag (-11%).""", blast="high"),
            row("Kevin McGonigle", "L", "+529", 77, "", ["vs Eovaldi"], """1 HR, 2 near-HR, 93.4 mph EV. Eovaldi LHB split +0.13, HR risk 0.25. park/weather net drag (-11%).""", blast="good"),
            row("Riley Greene", "L", "+370", 76, "⭐", ["vs Eovaldi"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 92.2 mph EV. Eovaldi LHB split +0.13, HR risk 0.25. park/weather net drag (-11%).""", blast="good"),
            row("Spencer Torkelson", "R", "+530", 84, "⭐ 🌕 💣", ["vs Eovaldi"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 92.1 mph EV. Eovaldi RHB split +0.14, HR risk 0.25. park/weather net drag (-11%).""", blast="high"),
        ],
    },
    {
        "title": "LAA @ SEA - Walbert Urena (R, LAA) vs Bryce Miller (R, SEA)",
        "description": "Tail key data: Park boost -2% (stadium +1%, weather -3%). Urena (HR risk -0.89, vs LHB -0.65, vs RHB -0.68). Miller (HR risk 0.77, vs LHB -0.18, vs RHB +1.44).",
        "rows": [
            row("Dominic Canzone", "L", "+436", 78, "💎", ["vs Urena"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 94.3 mph EV. Urena LHB split -0.65, HR risk -0.89. tough split lane (-0.65); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Cole Young", "L", "+870", 72, "", ["vs Urena"], """1 HR, 1 near-HR, 90.2 mph EV. Urena LHB split -0.65, HR risk -0.89. tough split lane (-0.65); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Zach Neto", "R", "+440", 87, "🌕 💣", ["vs Miller"], """3 HR, 4 near-HR, 88.8 mph EV. Miller RHB split +1.44, HR risk 0.77.""", blast="high"),
            row("Jo Adell", "R", "+478", 79, "", ["vs Miller"], """1 HR, 2 near-HR, 94.7 mph EV. Miller RHB split +1.44, HR risk 0.77.""", blast="good"),
            row("Josh Lowe", "L", "+830", 71, "", ["vs Miller"], """0 HR, 1 near-HR, 93.2 mph EV. Miller LHB split -0.18, HR risk 0.77. slight split headwind (-0.18); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ COL - Ryan Gusto (R, MIA) vs Michael Lorenzen (R, COL)",
        "description": "Tail key data: Park boost +30% (stadium +20%, weather +10%). Gusto (HR risk 0.03, vs LHB +0.24, vs RHB -0.25). Lorenzen (HR risk 0.46, vs LHB +0.17, vs RHB +0.61).",
        "rows": [
            row("Hunter Goodman", "R", "+240", 98, "🌕 💣", ["vs Gusto"], """4 HR, 6 near-HR, 96.1 mph EV. Gusto RHB split -0.25, HR risk 0.03. slight split headwind (-0.25).""", blast="high"),
            row("Mickey Moniak", "L", "+265", 81, "⭐ 🌕 💣", ["vs Gusto"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.2 mph EV. Gusto LHB split +0.24, HR risk 0.03.""", blast="high"),
            row("Kyle Karros", "R", "+870", 86, "🌕 💣", ["vs Gusto"], """2 HR, 2 near-HR, 96.0 mph EV. Gusto RHB split -0.25, HR risk 0.03. slight split headwind (-0.25).""", blast="high"),
            row("Willi Castro", "S", "+475", 78, "", ["vs Gusto"], """1 HR, 1 near-HR, 96.3 mph EV. Gusto RHB split -0.25, HR risk 0.03. slight split headwind (-0.25).""", blast="good"),
            row("Owen Caissie", "L", "+360", 87, "⭐ 🌕 💣", ["vs Lorenzen"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 93.4 mph EV. Lorenzen LHB split +0.17, HR risk 0.46.""", blast="high"),
            row("Joe Mack", "L", "+522", 83, "🌕 💣", ["vs Lorenzen"], """2 HR, 3 near-HR, 90.8 mph EV. Lorenzen LHB split +0.17, HR risk 0.46.""", blast="high"),
            row("Kyle Stowers", "L", "+280", 81, "", ["vs Lorenzen"], """1 HR, 3 near-HR, 94.6 mph EV. Lorenzen LHB split +0.17, HR risk 0.46.""", blast="good"),
            row("Griffin Conine", "L", "+389", 71, "", ["vs Lorenzen"], """1 HR, 1 near-HR, 88.7 mph EV. Lorenzen LHB split +0.17, HR risk 0.46.""", blast="good"),
        ],
    },
    {
        "title": "PIT @ PHI - Jared Jones (R, PIT) vs Alan Rangel (R, PHI)",
        "description": "Tail key data: Park boost +34% (stadium +14%, weather +20%). Jones (HR risk 0.60, vs LHB +1.02, vs RHB -0.27). Rangel (HR risk -0.96, vs LHB -0.47, vs RHB -1.09).",
        "rows": [
            row("Brandon Marsh", "L", "+524", 86, "🌕 💣", ["vs Jones"], """3 HR, 4 near-HR, 87.8 mph EV. Jones LHB split +1.02, HR risk 0.60. lighter EV form (87.8 mph).""", blast="high"),
            row("Kyle Schwarber", "L", "+186", 86, "🌕 💣", ["vs Jones"], """2 HR, 2 near-HR, 96.1 mph EV. Jones LHB split +1.02, HR risk 0.60.""", blast="high"),
            row("Bryce Harper", "L", "+290", 93, "🌕 💣", ["vs Jones"], """3 HR, 3 near-HR, 97.3 mph EV. Jones LHB split +1.02, HR risk 0.60.""", blast="high"),
            row("Edmundo Sosa", "R", "N/A", 76, "💎", ["vs Jones"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 92.1 mph EV. Jones RHB split -0.27, HR risk 0.60. slight split headwind (-0.27).""", blast="good"),
            row("Brandon Lowe", "L", "+265", 80, "⭐", ["vs Rangel"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.9 mph EV. Rangel LHB split -0.47, HR risk -0.96. tough split lane (-0.47); pitcher suppresses HR (-0.96).""", blast="good"),
            row("Ryan O'Hearn", "L", "+440", 70, "", ["vs Rangel"], """1 HR, 1 near-HR, 84.5 mph EV. Rangel LHB split -0.47, HR risk -0.96. tough split lane (-0.47); pitcher suppresses HR (-0.96).""", blast="good"),
            row("Marcell Ozuna", "R", "N/A", 75, "", ["vs Rangel"], """1 HR, 1 near-HR, 93.2 mph EV. Rangel RHB split -1.09, HR risk -0.96. tough split lane (-1.09); pitcher suppresses HR (-0.96).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+341", 82, "", ["vs Rangel"], """1 HR, 2 near-HR, 98.2 mph EV. Rangel RHB split -1.09, HR risk -0.96. tough split lane (-1.09); pitcher suppresses HR (-0.96).""", blast="good"),
        ],
    },
    {
        "title": "SD @ LAD - Randy Vasquez 🧤 (R, SD) vs Roki Sasaki 🧤 (R, LAD)",
        "description": "Tail key data: Park boost +10% (stadium +18%, weather -8%). Vasquez 🧤 (HR risk 1.46, vs LHB +0.73, vs RHB +1.50). Sasaki 🧤 (HR risk 1.30, vs LHB +0.54, vs RHB +1.42).",
        "rows": [
            row("Freddie Freeman", "L", "+360", 84, "🌕 💣", ["vs Vasquez"], """2 HR, 2 near-HR, 94.1 mph EV. Vasquez LHB split +0.73, HR risk 1.46. weather carry headwind (-8%).""", blast="high"),
            row("Dalton Rushing", "L", "+441", 73, "", ["vs Vasquez"], """1 HR, 1 near-HR, 91.4 mph EV. Vasquez LHB split +0.73, HR risk 1.46. weather carry headwind (-8%).""", blast="good"),
            row("Manny Machado", "R", "+424", 90, "⭐ 🌕 💣", ["vs Sasaki"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 96.4 mph EV. Sasaki RHB split +1.42, HR risk 1.30. weather carry headwind (-8%).""", blast="high"),
            row("Gavin Sheets", "L", "+450", 82, "🌕 💣", ["vs Sasaki"], """2 HR, 2 near-HR, 91.6 mph EV. Sasaki LHB split +0.54, HR risk 1.30. weather carry headwind (-8%).""", blast="high"),
            row("Sung-Mun Song", "L", "N/A", 73, "", ["vs Sasaki"], """1 HR, 1 near-HR, 91.2 mph EV. Sasaki LHB split +0.54, HR risk 1.30. weather carry headwind (-8%).""", blast="good"),
            row("Ty France", "R", "+640", 87, "🌕 💣 💎", ["vs Sasaki"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 91.4 mph EV. Sasaki RHB split +1.42, HR risk 1.30. weather carry headwind (-8%).""", blast="high"),
        ],
    },
    {
        "title": "STL @ ATL - Dustin May (R, STL) vs Hurston Waldrep (R, ATL)",
        "description": "Tail key data: Park boost +8% (stadium -3%, weather +10%). May (HR risk -0.27, vs LHB -0.48, vs RHB +0.21). Waldrep (HR risk -1.80, vs LHB -1.39, vs RHB -1.06).",
        "rows": [
            row("Matt Olson", "L", "+349", 69, "⭐", ["vs May"], """Worst Pickz Favorite. 0 HR, 93.3 mph EV. May LHB split -0.48, HR risk -0.27. tough split lane (-0.48); pitcher risk below avg (-0.27).""", blast="good"),
            row("Mike Yastrzemski", "L", "+630", 62, "", ["vs May"], """0 HR, 88.2 mph EV. May LHB split -0.48, HR risk -0.27. tough split lane (-0.48); pitcher risk below avg (-0.27)."""),
            row("Rowdy Tellez", "L", "N/A", 65, "", ["vs May"], """0 HR, 91.2 mph EV. May LHB split -0.48, HR risk -0.27. tough split lane (-0.48); pitcher risk below avg (-0.27)."""),
            row("Ozzie Albies", "S", "+650", 73, "", ["vs May"], """1 HR, 2 near-HR, 88.9 mph EV. May RHB split +0.21, HR risk -0.27. pitcher risk below avg (-0.27).""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 76, "⭐", ["vs Waldrep"], """Worst Pickz Favorite. 0 HR, 99.6 mph EV. Waldrep RHB split -1.06, HR risk -1.80. tough split lane (-1.06); pitcher suppresses HR (-1.80).""", blast="good"),
            row("Alec Burleson", "L", "+437", 66, "", ["vs Waldrep"], """0 HR, 91.7 mph EV. Waldrep LHB split -1.39, HR risk -1.80. tough split lane (-1.39); pitcher suppresses HR (-1.80)."""),
            row("Lars Nootbaar", "L", "+560", 63, "", ["vs Waldrep"], """0 HR, 89.3 mph EV. Waldrep LHB split -1.39, HR risk -1.80. tough split lane (-1.39); pitcher suppresses HR (-1.80)."""),
        ],
    },
    {
        "title": "TB @ KC - Ian Seymour (L, TB) vs Stephen Kolek (R, KC)",
        "description": "Tail key data: Park boost +38% (stadium +11%, weather +27%). Seymour (HR risk 0.46, vs LHB +1.89, vs RHB -0.69). Kolek (HR risk 0.45, vs LHB +0.25, vs RHB +0.39).",
        "rows": [
            row("Bobby Witt Jr.", "R", "+325", 74, "", ["vs Seymour"], """0 HR, 98.3 mph EV. Seymour RHB split -0.69, HR risk 0.46. tough split lane (-0.69); limited recent HR events.""", blast="good"),
            row("Jac Caglianone", "L", "+316", 70, "", ["vs Seymour"], """1 HR, 1 near-HR, 88.2 mph EV. Seymour LHB split +1.89, HR risk 0.46.""", blast="good"),
            row("Carter Jensen", "L", "+473", 80, "💎", ["vs Seymour"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 96.4 mph EV. Seymour LHB split +1.89, HR risk 0.46.""", blast="good"),
            row("Junior Caminero", "R", "+244", 98, "⭐ 🌕 💣", ["vs Kolek"], """Worst Pickz Favorite. 6 HR, 7 near-HR, 94.9 mph EV. Kolek RHB split +0.39, HR risk 0.45.""", blast="high"),
            row("Ryan Vilade", "R", "N/A", 74, "", ["vs Kolek"], """1 HR, 1 near-HR, 92.3 mph EV. Kolek RHB split +0.39, HR risk 0.45.""", blast="good"),
            row("Cedric Mullins", "L", "+509", 78, "🌕 💣 💎", ["vs Kolek"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 86.3 mph EV. Kolek LHB split +0.25, HR risk 0.45. lighter EV form (86.3 mph).""", blast="high"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-02")

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

    out = ROOT / '_games-0702.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
