#!/usr/bin/env python3
"""Generate games[] block for 2026-09-22 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Cody Bellinger (L)",
    "Elly De La Cruz (S)",
    "Fernando Tatis Jr. (R)",
    "Griffin Conine (L)",
    "Heriberto Hernandez (R)",
    "Hunter Goodman (R)",
    "Josh Jung (R)",
    "Kyle Stowers (L)",
    "Kyle Tucker (L)",
    "Mark Vientos (R)",
    "Riley Greene (L)",
    "Roman Anthony (L)",
}

GEMS = {
    "Austin Wells (L)",
    "Garrett Mitchell (L)",
    "Heliot Ramos (R)",
    "Ian Happ (S)",
    "Ivan Herrera (R)",
    "Josh Bell (S)",
    "Kyle Karros (R)",
    "Leonardo Bernal (S)",
    "Mickey Moniak (L)",
    "Mookie Betts (R)",
    "Nolan Arenado (R)",
    "Pete Crow Armstrong (L)",
    "Salvador Perez (R)",
    "Shea Langeliers (R)",
    "Spencer Jones (L)",
    "Tommy Pham (R)",
    "Ty France (R)",
    "Tyler Stephenson (R)",
    "William Contreras (R)",
    "Yandy Diaz (R)",
}

PLAYER_TEAMS = {
    "Abimelec Ortiz (L)": "WSH",
    "Alec Burleson (L)": "STL",
    "Alex Bregman (R)": "CHC",
    "Andres Chaparro (R)": "WSH",
    "Andrew Knizner (R)": "SF",
    "Angel Martinez (S)": "CLE",
    "Austin Hedges (R)": "CLE",
    "Austin Riley (R)": "ATL",
    "Austin Wells (L)": "NYY",
    "Ben Rice (L)": "NYY",
    "Bo Bichette (R)": "NYM",
    "Bobby Witt Jr. (R)": "KC",
    "Brewer Hicklen (R)": "ATL",
    "Brice Turang (L)": "MIL",
    "Brooks Lee (S)": "MIN",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Harper (L)": "PHI",
    "CJ Abrams (L)": "WSH",
    "Cal Raleigh (S)": "SEA",
    "Chase DeLauter (L)": "CLE",
    "Christian Moore (R)": "LAA",
    "Cody Bellinger (L)": "NYY",
    "Cole Young (L)": "SEA",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Drew Gilbert (L)": "SF",
    "Elly De La Cruz (S)": "CIN",
    "Emmanuel Rodriguez (L)": "MIN",
    "Enrique Hernandez (R)": "LAD",
    "Ezequiel Tovar (R)": "COL",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Garrett Mitchell (L)": "MIL",
    "Griffin Conine (L)": "MIA",
    "Gunnar Henderson (L)": "BAL",
    "Hao-Yu Lee (R)": "DET",
    "Heliot Ramos (R)": "NYY",
    "Henry Bolte (R)": "ATH",
    "Henry Davis (R)": "PIT",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Isaac Paredes (R)": "HOU",
    "Ivan Herrera (R)": "STL",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "Jackson Merrill (L)": "SD",
    "Jake Burger (R)": "TEX",
    "James Wood (L)": "WSH",
    "Joey Ortiz (R)": "MIL",
    "Jonah Heim (S)": "ATH",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Jose Ramirez (S)": "CLE",
    "Josh Bell (S)": "MIN",
    "Josh Jung (R)": "TEX",
    "Josh Smith (L)": "TOR",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Kyle Tucker (L)": "LAD",
    "Leonardo Bernal (S)": "STL",
    "Mark Vientos (R)": "NYM",
    "Max Muncy (L)": "LAD",
    "Michael Conforto (L)": "CHC",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Nolan Arenado (R)": "ARI",
    "Nolan Gorman (L)": "STL",
    "Patrick Bailey (S)": "CLE",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Flores (R)": "PIT",
    "Randal Grichuk (R)": "CWS",
    "Randy Arozarena (R)": "SEA",
    "Riley Greene (L)": "DET",
    "Roman Anthony (L)": "BOS",
    "Salvador Perez (R)": "KC",
    "Sean Keys (L)": "TOR",
    "Shay Whitcomb (R)": "SF",
    "Shea Langeliers (R)": "ATH",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Teoscar Hernandez (R)": "LAD",
    "Tommy Pham (R)": "CWS",
    "Tommy White (R)": "ATH",
    "Ty France (R)": "SD",
    "Tyler Stephenson (R)": "CIN",
    "Vaughn Grissom (R)": "LAA",
    "Victor Mesa Jr. (L)": "TB",
    "Vinnie Pasquantino (L)": "KC",
    "William Contreras (R)": "MIL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("ARI @ COL", "Freeland"),
    ("CIN @ ATL", "Ritchie"),
    ("CIN @ ATL", "Williamson"),
    ("HOU @ SEA", "Gilbert"),
    ("NYM @ TEX", "Manaea"),
}

def odds_text(odds):
    return "Listed prop - Over 0.5 HR" if odds == "N/A" else f"Listed {odds} - Over 0.5 HR"

def row(name, hand, odds, score, emojis, chips, note, blast=None, contact=None):
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
    if contact:
        item["contact"] = contact
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
        "title": "ARI @ COL - Michael Soroka (R, ARI) vs Kyle Freeland 🧤 (L, COL)",
        "kLines": {'Soroka': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 21.7, 'matchupK': 21.5, 'ownK': 22.4}, 'Freeland': {'k': 4.2, 'lo': 3, 'hi': 6, 'bf': 23.5, 'matchupK': 17.7, 'ownK': 17.9}},
        "description": "Tail key data: Park boost +23% (stadium +19%, weather +4%). Soroka (HR risk -0.54, vs LHB -0.28, vs RHB -0.36). Freeland 🧤 (HR risk 1.01, vs LHB -0.34, vs RHB +1.17).",
        "rows": [
            row("Hunter Goodman", "R", "+298", 82, "⭐ 🌕 💣", ["vs Soroka"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 98.4 mph EV, 25.0% barrels. Soroka RHB split -0.36, HR risk -0.54. slight split headwind (-0.36); pitcher suppresses HR (-0.54).""", blast="high", contact={'stars': 3, 'k': 23.2, 'batterK': 22.6, 'batterWhiff': 29.1, 'pitcherK': 22.4}),
            row("Kyle Karros", "R", "+750", 68, "💎", ["vs Soroka"], """Worst Pickz Hidden Gem. 0 HR, 99.4 mph EV. Soroka RHB split -0.36, HR risk -0.54. slight split headwind (-0.36); pitcher suppresses HR (-0.54).""", blast="good", contact={'stars': 3, 'k': 19.9, 'batterK': 16.0, 'batterWhiff': 20.9, 'pitcherK': 22.4}),
            row("Mickey Moniak", "L", "+381", 56, "💎", ["vs Soroka"], """Worst Pickz Hidden Gem. 0 HR, 90.7 mph EV. Soroka LHB split -0.28, HR risk -0.54. slight split headwind (-0.28); pitcher suppresses HR (-0.54).""", contact={'stars': 1, 'k': 27.8, 'batterK': 35.1, 'batterWhiff': 38.2, 'pitcherK': 22.4}),
            row("Ezequiel Tovar", "R", "+690", 50, "", ["vs Soroka"], """0 HR, 1 near-HR, 87.9 mph EV, 12.5% barrels. Soroka RHB split -0.36, HR risk -0.54. slight split headwind (-0.36); pitcher suppresses HR (-0.54).""", contact={'stars': 2, 'k': 25.4, 'batterK': 31.0, 'batterWhiff': 33.6, 'pitcherK': 22.4}),
            row("Corbin Carroll", "L", "+390", 91, "🌕 💣", ["vs Freeland"], """1 HR, 1 near-HR, 96.0 mph EV, 12.5% barrels. Freeland LHB split -0.34, HR risk 1.01. slight split headwind (-0.34).""", blast="good", contact={'stars': 3, 'k': 22.4, 'batterK': 28.9, 'batterWhiff': 30.3, 'pitcherK': 17.9}),
            row("Nolan Arenado", "R", "+420", 97, "🌕 💣 💎", ["vs Freeland"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 94.1 mph EV. Freeland RHB split +1.17, HR risk 1.01.""", blast="high", contact={'stars': 4, 'k': 19.1, 'batterK': 16.3, 'batterWhiff': 28.1, 'pitcherK': 17.9}),
            row("Ketel Marte", "S", "+239", 83, "", ["vs Freeland"], """0 HR, 1 near-HR, 87.2 mph EV, 12.5% barrels. Freeland SHB→RHB split +1.17, HR risk 1.01. limited recent HR events; lighter EV form (87.2 mph).""", contact={'stars': 5, 'k': 14.7, 'batterK': 10.2, 'batterWhiff': 12.6, 'pitcherK': 17.9}),
        ],
    },
    {
        "title": "CIN @ ATL - Brandon Williamson 🧤 (L, CIN) vs JR Ritchie 🧤 (R, ATL)",
        "kLines": {'Williamson': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 21.7, 'matchupK': 17.6, 'ownK': 15.8}, 'Ritchie': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 22.1, 'matchupK': 24.0, 'ownK': 22.6}},
        "description": "Tail key data: Park boost +1% (stadium -3%, weather +3%). Williamson 🧤 (HR risk 0.97, vs LHB +0.87, vs RHB +0.95). Ritchie 🧤 (HR risk 1.56, vs LHB +0.91, vs RHB +1.29).",
        "rows": [
            row("Austin Riley", "R", "+423", 88, "🌕 💣", ["vs Williamson"], """1 HR, 1 near-HR, 98.3 mph EV, 25.0% barrels. Williamson RHB split +0.95, HR risk 0.97.""", blast="high", contact={'stars': 3, 'k': 20.8, 'batterK': 30.7, 'batterWhiff': 24.8, 'pitcherK': 15.8}),
            row("Drake Baldwin", "L", "+500", 81, "", ["vs Williamson"], """0 HR, 1 near-HR, 99.8 mph EV. Williamson LHB split +0.87, HR risk 0.97. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.1, 'batterK': 27.2, 'batterWhiff': 28.7, 'pitcherK': 15.8}),
            row("Brewer Hicklen", "R", "N/A", 79, "🚀", ["vs Williamson"], """0 HR, 104.4 mph EV. Williamson RHB split +0.95, HR risk 0.97. limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.1, 'batterK': 39.5, 'batterWhiff': 46.7, 'pitcherK': 15.8}),
            row("Elly De La Cruz", "S", "+360", 92, "⭐ 🌕 💣", ["vs Ritchie"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.7 mph EV, 12.5% barrels. Ritchie SHB→LHB split +0.91, HR risk 1.56.""", blast="good", contact={'stars': 2, 'k': 25.3, 'batterK': 29.8, 'batterWhiff': 29.9, 'pitcherK': 22.6}),
            row("Tyler Stephenson", "R", "+572", 86, "💎", ["vs Ritchie"], """Worst Pickz Hidden Gem. 0 HR, 93.3 mph EV, 12.5% barrels. Ritchie RHB split +1.29, HR risk 1.56. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 25.7, 'batterWhiff': 26.7, 'pitcherK': 22.6}),
            row("JJ Bleday", "L", "+440", 78, "", ["vs Ritchie"], """0 HR, 92.7 mph EV. Ritchie LHB split +0.91, HR risk 1.56. limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.1, 'batterK': 24.7, 'batterWhiff': 31.0, 'pitcherK': 22.6}),
        ],
    },
    {
        "title": "CLE @ BOS - Parker Messick (L, CLE) vs Payton Tolle (L, BOS)",
        "kLines": {'Messick': {'k': 6.5, 'lo': 5, 'hi': 8, 'bf': 23.4, 'matchupK': 27.8, 'ownK': 28.7}, 'Tolle': {'k': 6.3, 'lo': 5, 'hi': 8, 'bf': 22.7, 'matchupK': 27.7, 'ownK': 33.8}},
        "description": "Tail key data: Park boost -40% (stadium -7%, weather -33%). Messick (HR risk -0.54, vs LHB +0.42, vs RHB -0.74). Tolle (HR risk -0.09, vs LHB -0.26, vs RHB +0.01).",
        "rows": [
            row("Roman Anthony", "L", "+640", 75, "⭐ 🌕 💣", ["vs Messick"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.2 mph EV, 25.0% barrels. Messick LHB split +0.42, HR risk -0.54. pitcher suppresses HR (-0.54); park/weather net drag (-40%).""", blast="high", contact={'stars': 1, 'k': 28.4, 'batterK': 28.0, 'batterWhiff': 28.3, 'pitcherK': 28.7}),
            row("Wilyer Abreu", "L", "+670", 65, "", ["vs Messick"], """0 HR, 1 near-HR, 94.2 mph EV, 12.5% barrels. Messick LHB split +0.42, HR risk -0.54. pitcher suppresses HR (-0.54); park/weather net drag (-40%).""", blast="good", contact={'stars': 2, 'k': 26.0, 'batterK': 22.4, 'batterWhiff': 25.7, 'pitcherK': 28.7}),
            row("Willson Contreras", "R", "+534", 57, "", ["vs Messick"], """0 HR, 92.7 mph EV. Messick RHB split -0.74, HR risk -0.54. tough split lane (-0.74); pitcher suppresses HR (-0.54).""", blast="good", contact={'stars': 2, 'k': 26.3, 'batterK': 23.3, 'batterWhiff': 25.9, 'pitcherK': 28.7}),
            row("Angel Martinez", "S", "+890", 80, "🌕 💣", ["vs Tolle"], """2 HR, 2 near-HR, 95.2 mph EV, 25.0% barrels. Tolle SHB→RHB split +0.01, HR risk -0.09. pitcher risk below avg (-0.09); park/weather net drag (-40%).""", blast="high", contact={'stars': 1, 'k': 27.8, 'batterK': 22.7, 'batterWhiff': 20.9, 'pitcherK': 33.8}),
            row("Jose Ramirez", "S", "+579", 62, "", ["vs Tolle"], """0 HR, 95.1 mph EV, 12.5% barrels. Tolle SHB→RHB split +0.01, HR risk -0.09. pitcher risk below avg (-0.09); park/weather net drag (-40%).""", blast="good", contact={'stars': 3, 'k': 21.9, 'batterK': 10.5, 'batterWhiff': 12.4, 'pitcherK': 33.8}),
            row("Chase DeLauter", "L", "+950", 53, "", ["vs Tolle"], """0 HR, 91.6 mph EV. Tolle LHB split -0.26, HR risk -0.09. slight split headwind (-0.26); pitcher risk below avg (-0.09).""", contact={'stars': 2, 'k': 24.2, 'batterK': 16.7, 'batterWhiff': 13.1, 'pitcherK': 33.8}),
            row("Patrick Bailey", "S", "N/A", 54, "", ["vs Tolle"], """0 HR, 97.3 mph EV. Tolle SHB→RHB split +0.01, HR risk -0.09. pitcher risk below avg (-0.09); park/weather net drag (-40%).""", blast="good", contact={'stars': 1, 'k': 31.3, 'batterK': 30.6, 'batterWhiff': 29.5, 'pitcherK': 33.8}),
            row("Austin Hedges", "R", "+1100", 49, "", ["vs Tolle"], """0 HR, 94.3 mph EV. Tolle RHB split +0.01, HR risk -0.09. pitcher risk below avg (-0.09); park/weather net drag (-40%).""", blast="good", contact={'stars': 1, 'k': 28.0, 'batterK': 19.1, 'batterWhiff': 25.7, 'pitcherK': 33.8}),
        ],
    },
    {
        "title": "CWS @ KC - Anthony Kay (L, CWS) vs Daniel Lynch IV (L, KC)",
        "kLines": {'Kay': {'k': 4.2, 'lo': 3, 'hi': 6, 'bf': 21.9, 'matchupK': 19.3, 'ownK': 18.2}, 'Lynch IV': {'k': 3.2, 'lo': 2, 'hi': 5, 'bf': 18.5, 'matchupK': 17.5, 'ownK': 13.1}},
        "description": "Tail key data: Park boost -17% (stadium +12%, weather -28%). Kay (HR risk 0.30, vs LHB -1.57, vs RHB +0.70). Lynch IV (HR risk -0.61, vs LHB -0.88, vs RHB -0.29).",
        "rows": [
            row("Jac Caglianone", "L", "+630", 60, "", ["vs Kay"], """0 HR, 1 near-HR, 93.8 mph EV. Kay LHB split -1.57, HR risk 0.30. tough split lane (-1.57); park/weather net drag (-17%).""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 29.2, 'batterWhiff': 34.5, 'pitcherK': 18.2}),
            row("Salvador Perez", "R", "+610", 53, "💎", ["vs Kay"], """Worst Pickz Hidden Gem. 0 HR, 90.3 mph EV. Kay RHB split +0.70, HR risk 0.30. park/weather net drag (-17%); limited recent HR events.""", contact={'stars': 4, 'k': 18.0, 'batterK': 14.1, 'batterWhiff': 23.0, 'pitcherK': 18.2}),
            row("Vinnie Pasquantino", "L", "+800", 60, "", ["vs Kay"], """0 HR, 1 near-HR, 91.3 mph EV, 12.5% barrels. Kay LHB split -1.57, HR risk 0.30. tough split lane (-1.57); park/weather net drag (-17%).""", contact={'stars': 5, 'k': 16.5, 'batterK': 14.8, 'batterWhiff': 14.5, 'pitcherK': 18.2}),
            row("Bobby Witt Jr.", "R", "+458", 58, "", ["vs Kay"], """0 HR, 86.5 mph EV. Kay RHB split +0.70, HR risk 0.30. park/weather net drag (-17%); limited recent HR events.""", contact={'stars': 4, 'k': 18.2, 'batterK': 15.7, 'batterWhiff': 24.1, 'pitcherK': 18.2}),
            row("Munetaka Murakami", "L", "+547", 81, "🌕 💣", ["vs Lynch IV"], """2 HR, 3 near-HR, 95.6 mph EV, 25.0% barrels. Lynch IV LHB split -0.88, HR risk -0.61. tough split lane (-0.88); pitcher suppresses HR (-0.61).""", blast="high", contact={'stars': 1, 'k': 32.7, 'batterK': 46.4, 'batterWhiff': 46.5, 'pitcherK': None}),
            row("Randal Grichuk", "R", "+501", 67, "", ["vs Lynch IV"], """0 HR, 1 near-HR, 93.3 mph EV, 12.5% barrels. Lynch IV RHB split -0.29, HR risk -0.61. slight split headwind (-0.29); pitcher suppresses HR (-0.61).""", blast="good", contact={'stars': 3, 'k': 21.6, 'batterK': 21.8, 'batterWhiff': 22.4, 'pitcherK': None}),
            row("Tommy Pham", "R", "+750", 52, "💎", ["vs Lynch IV"], """Worst Pickz Hidden Gem. 0 HR, 94.8 mph EV. Lynch IV RHB split -0.29, HR risk -0.61. slight split headwind (-0.29); pitcher suppresses HR (-0.61).""", blast="good", contact={'stars': 2, 'k': 24.9, 'batterK': 38.5, 'batterWhiff': 37.8, 'pitcherK': None}),
            row("Miguel Vargas", "R", "+433", 53, "", ["vs Lynch IV"], """0 HR, 90.9 mph EV. Lynch IV RHB split -0.29, HR risk -0.61. slight split headwind (-0.29); pitcher suppresses HR (-0.61).""", contact={'stars': 3, 'k': 21.1, 'batterK': 20.2, 'batterWhiff': 21.9, 'pitcherK': None}),
        ],
    },
    {
        "title": "HOU @ SEA - Cristian Javier (R, HOU) vs Logan Gilbert 🧤 (R, SEA)",
        "kLines": {'Javier': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 20.1, 'matchupK': 23.1, 'ownK': 23.9}, 'Gilbert': {'k': 5.9, 'lo': 4, 'hi': 8, 'bf': 23.4, 'matchupK': 25.3, 'ownK': 27.0}},
        "description": "Tail key data: Park boost -3% (stadium +1%, weather -4%). Javier (HR risk 0.04, vs LHB -0.50, vs RHB +0.81). Gilbert 🧤 (HR risk 1.44, vs LHB +0.99, vs RHB +1.32).",
        "rows": [
            row("Cole Young", "L", "+700", 67, "", ["vs Javier"], """1 HR, 2 near-HR, 94.5 mph EV, 12.5% barrels. Javier LHB split -0.50, HR risk 0.04. tough split lane (-0.50); weather carry headwind (-4%).""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 17.3, 'batterWhiff': 21.9, 'pitcherK': 23.9}),
            row("Cal Raleigh", "S", "+340", 74, "", ["vs Javier"], """1 HR, 1 near-HR, 94.7 mph EV, 25.0% barrels. Javier SHB→LHB split -0.50, HR risk 0.04. tough split lane (-0.50); weather carry headwind (-4%).""", blast="good", contact={'stars': 2, 'k': 27.0, 'batterK': 31.0, 'batterWhiff': 32.8, 'pitcherK': 23.9}),
            row("Randy Arozarena", "R", "+440", 60, "", ["vs Javier"], """0 HR, 1 near-HR, 90.6 mph EV. Javier RHB split +0.81, HR risk 0.04. weather carry headwind (-4%); limited recent HR events.""", contact={'stars': 3, 'k': 22.9, 'batterK': 22.0, 'batterWhiff': 24.4, 'pitcherK': 23.9}),
            row("Dominic Canzone", "L", "+444", 70, "", ["vs Javier"], """0 HR, 1 near-HR, 92.8 mph EV, 12.5% barrels. Javier LHB split -0.50, HR risk 0.04. tough split lane (-0.50); weather carry headwind (-4%).""", blast="good", contact={'stars': 3, 'k': 22.2, 'batterK': 20.0, 'batterWhiff': 24.4, 'pitcherK': 23.9}),
            row("Isaac Paredes", "R", "+566", 86, "", ["vs Gilbert"], """1 HR, 1 near-HR, 91.6 mph EV, 12.5% barrels. Gilbert RHB split +1.32, HR risk 1.44. weather carry headwind (-4%).""", blast="good", contact={'stars': 3, 'k': 20.9, 'batterK': 16.9, 'batterWhiff': 13.3, 'pitcherK': 27.0}),
            row("Nelson Velazquez", "R", "N/A", 90, "🌕 💣", ["vs Gilbert"], """0 HR, 1 near-HR, 97.6 mph EV, 25.0% barrels. Gilbert RHB split +1.32, HR risk 1.44. weather carry headwind (-4%); limited recent HR events.""", blast="high", contact={'stars': 1, 'k': 30.3, 'batterK': 41.7, 'batterWhiff': 44.8, 'pitcherK': 27.0}),
            row("Yordan Alvarez", "L", "+340", 91, "🌕 💣", ["vs Gilbert"], """1 HR, 1 near-HR, 91.0 mph EV, 12.5% barrels. Gilbert LHB split +0.99, HR risk 1.44. weather carry headwind (-4%).""", blast="good", contact={'stars': 3, 'k': 21.9, 'batterK': 15.7, 'batterWhiff': 19.9, 'pitcherK': 27.0}),
        ],
    },
    {
        "title": "LAA @ ATH - Yusei Kikuchi (L, LAA) vs Brady Basso (L, ATH)",
        "kLines": {'Kikuchi': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 21.7, 'matchupK': 24.3, 'ownK': 23.6}, 'Basso': {'k': 3.3, 'lo': 2, 'hi': 5, 'bf': 16.7, 'matchupK': 19.7, 'ownK': 12.9}},
        "description": "Tail key data: Park boost +28% (stadium +31%, weather -2%). Kikuchi (HR risk 0.68, vs LHB -0.59, vs RHB +0.78). Basso (HR risk -1.52, vs LHB -1.52, vs RHB -0.81).",
        "rows": [
            row("Henry Bolte", "R", "+577", 97, "🌕 💣", ["vs Kikuchi"], """2 HR, 2 near-HR, 99.6 mph EV, 25.0% barrels. Kikuchi RHB split +0.78, HR risk 0.68.""", blast="high", contact={'stars': 2, 'k': 26.5, 'batterK': 31.1, 'batterWhiff': 29.7, 'pitcherK': 23.6}),
            row("Zack Gelof", "R", "+455", 93, "🌕 💣", ["vs Kikuchi"], """2 HR, 2 near-HR, 89.7 mph EV, 25.0% barrels. Kikuchi RHB split +0.78, HR risk 0.68.""", blast="high", contact={'stars': 2, 'k': 24.5, 'batterK': 23.8, 'batterWhiff': 31.2, 'pitcherK': 23.6}),
            row("Shea Langeliers", "R", "+272", 96, "🌕 💣 💎", ["vs Kikuchi"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 99.1 mph EV, 25.0% barrels. Kikuchi RHB split +0.78, HR risk 0.68.""", blast="high", contact={'stars': 1, 'k': 27.7, 'batterK': 34.6, 'batterWhiff': 34.1, 'pitcherK': 23.6}),
            row("Jonah Heim", "S", "+579", 89, "🌕 💣", ["vs Kikuchi"], """1 HR, 2 near-HR, 94.1 mph EV, 12.5% barrels. Kikuchi SHB→RHB split +0.78, HR risk 0.68.""", blast="good", contact={'stars': 3, 'k': 20.3, 'batterK': 18.7, 'batterWhiff': 16.4, 'pitcherK': 23.6}),
            row("Tommy White", "R", "+1140", 76, "", ["vs Kikuchi"], """0 HR, 95.0 mph EV, 12.5% barrels. Kikuchi RHB split +0.78, HR risk 0.68. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.7, 'batterK': 13.8, 'batterWhiff': 22.1, 'pitcherK': 23.6}),
            row("Zach Neto", "R", "+338", 87, "🌕 💣", ["vs Basso"], """2 HR, 3 near-HR, 95.0 mph EV, 25.0% barrels. Basso RHB split -0.81, HR risk -1.52. tough split lane (-0.81); pitcher suppresses HR (-1.52).""", blast="high", contact={'stars': 3, 'k': 23.7, 'batterK': 34.4, 'batterWhiff': 31.1, 'pitcherK': 12.9}),
            row("Vaughn Grissom", "R", "+670", 58, "", ["vs Basso"], """1 HR, 1 near-HR, 90.9 mph EV, 12.5% barrels. Basso RHB split -0.81, HR risk -1.52. tough split lane (-0.81); pitcher suppresses HR (-1.52).""", blast="good", contact={'stars': 4, 'k': 18.6, 'batterK': 21.4, 'batterWhiff': 21.8, 'pitcherK': 12.9}),
            row("Christian Moore", "R", "+650", 61, "", ["vs Basso"], """0 HR, 2 near-HR, 96.7 mph EV, 25.0% barrels. Basso RHB split -0.81, HR risk -1.52. tough split lane (-0.81); pitcher suppresses HR (-1.52).""", blast="good", contact={'stars': 3, 'k': 22.2, 'batterK': 30.7, 'batterWhiff': 31.0, 'pitcherK': 12.9}),
        ],
    },
    {
        "title": "MIA @ CHC - Janson Junk (R, MIA) vs Shota Imanaga (L, CHC)",
        "kLines": {'Junk': {'k': 3.1, 'lo': 1, 'hi': 5, 'bf': 21.2, 'matchupK': 14.7, 'ownK': 12.3}, 'Imanaga': {'k': 5.5, 'lo': 4, 'hi': 7, 'bf': 22.6, 'matchupK': 24.4, 'ownK': 25.1}},
        "description": "Tail key data: Park boost -33% (stadium -2%, weather -31%). Junk (HR risk -0.11, vs LHB -0.51, vs RHB +0.52). Imanaga (BAA vs LHB .228, vs RHB .235, HR/9 1.82).",
        "rows": [
            row("Pete Crow Armstrong", "L", "+690", 92, "🌕 💣 💎", ["vs Junk"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 95.0 mph EV, 37.5% barrels. Junk LHB split -0.51, HR risk -0.11. tough split lane (-0.51); pitcher risk below avg (-0.11).""", blast="high", contact={'stars': 4, 'k': 18.4, 'batterK': 24.5, 'batterWhiff': 25.4, 'pitcherK': 12.3}),
            row("Michael Conforto", "L", "+1060", 67, "", ["vs Junk"], """1 HR, 2 near-HR, 90.8 mph EV, 12.5% barrels. Junk LHB split -0.51, HR risk -0.11. tough split lane (-0.51); pitcher risk below avg (-0.11).""", blast="good", contact={'stars': 5, 'k': 16.6, 'batterK': 18.6, 'batterWhiff': 21.6, 'pitcherK': 12.3}),
            row("Ian Happ", "S", "+1000", 74, "💎", ["vs Junk"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.0 mph EV, 12.5% barrels. Junk SHB→LHB split -0.51, HR risk -0.11. tough split lane (-0.51); pitcher risk below avg (-0.11).""", blast="good", contact={'stars': 4, 'k': 18.4, 'batterK': 25.8, 'batterWhiff': 26.0, 'pitcherK': 12.3}),
            row("Alex Bregman", "R", "N/A", 63, "", ["vs Junk"], """0 HR, 93.5 mph EV, 12.5% barrels. Junk RHB split +0.52, HR risk -0.11. pitcher risk below avg (-0.11); park/weather net drag (-33%).""", blast="good", contact={'stars': 5, 'k': 12.6, 'batterK': 7.2, 'batterWhiff': 13.4, 'pitcherK': 12.3}),
            row("Griffin Conine", "L", "+1400", 70, "⭐", ["vs Imanaga"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.0 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-33%).""", blast="good", contact={'stars': 2, 'k': 26.1, 'batterK': 26.0, 'batterWhiff': 32.4, 'pitcherK': 25.1}),
            row("Heriberto Hernandez", "R", "+563", 82, "🚀 ⭐ 🌕 💣", ["vs Imanaga"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 100.1 mph EV, 37.5% barrels. limited split/risk sample; park/weather net drag (-33%).""", blast="high", contact={'stars': 2, 'k': 26.7, 'batterK': 28.0, 'batterWhiff': 30.9, 'pitcherK': 25.1}),
            row("Kyle Stowers", "L", "+750", 81, "⭐ 🌕 💣", ["vs Imanaga"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 97.7 mph EV, 37.5% barrels. limited split/risk sample; park/weather net drag (-33%).""", blast="high", contact={'stars': 1, 'k': 29.1, 'batterK': 33.3, 'batterWhiff': 36.3, 'pitcherK': 25.1}),
        ],
    },
    {
        "title": "MIL @ PHI - Dustin May (R, MIL) vs Zack Wheeler (R, PHI)",
        "kLines": {'May': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 20.8, 'matchupK': 21.6, 'ownK': 22.7}, 'Wheeler': {'k': 6.1, 'lo': 4, 'hi': 8, 'bf': 22.8, 'matchupK': 26.8, 'ownK': 27.4}},
        "description": "Tail key data: Park boost -18% (stadium +15%, weather -33%). May (HR risk 0.42, vs LHB +0.16, vs RHB +0.46). Wheeler (HR risk 0.15, vs LHB +0.61, vs RHB -0.24).",
        "rows": [
            row("Kyle Schwarber", "L", "+300", 80, "", ["vs May"], """1 HR, 1 near-HR, 93.2 mph EV, 12.5% barrels. May LHB split +0.16, HR risk 0.42. park/weather net drag (-18%).""", blast="good", contact={'stars': 3, 'k': 23.8, 'batterK': 25.3, 'batterWhiff': 27.4, 'pitcherK': 22.7}),
            row("Bryce Harper", "L", "+572", 60, "", ["vs May"], """0 HR, 88.8 mph EV. May LHB split +0.16, HR risk 0.42. park/weather net drag (-18%); limited recent HR events.""", contact={'stars': 2, 'k': 26.1, 'batterK': 27.9, 'batterWhiff': 36.3, 'pitcherK': 22.7}),
            row("Garrett Mitchell", "L", "+770", 76, "💎", ["vs Wheeler"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.2 mph EV, 12.5% barrels. Wheeler LHB split +0.61, HR risk 0.15. park/weather net drag (-18%).""", blast="good", contact={'stars': 1, 'k': 28.3, 'batterK': 29.7, 'batterWhiff': 32.6, 'pitcherK': 27.4}),
            row("William Contreras", "R", "+690", 72, "💎", ["vs Wheeler"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.3 mph EV, 12.5% barrels. Wheeler RHB split -0.24, HR risk 0.15. slight split headwind (-0.24); park/weather net drag (-18%).""", blast="good", contact={'stars': 3, 'k': 23.8, 'batterK': 19.4, 'batterWhiff': 24.2, 'pitcherK': 27.4}),
            row("Joey Ortiz", "R", "+1100", 62, "", ["vs Wheeler"], """1 HR, 1 near-HR, 97.0 mph EV, 12.5% barrels. Wheeler RHB split -0.24, HR risk 0.15. slight split headwind (-0.24); park/weather net drag (-18%).""", blast="good", contact={'stars': 2, 'k': 24.8, 'batterK': 22.2, 'batterWhiff': 24.6, 'pitcherK': 27.4}),
            row("Brice Turang", "L", "+900", 61, "", ["vs Wheeler"], """0 HR, 94.5 mph EV. Wheeler LHB split +0.61, HR risk 0.15. park/weather net drag (-18%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 26.3, 'batterK': 25.9, 'batterWhiff': 26.6, 'pitcherK': 27.4}),
        ],
    },
    {
        "title": "MIN @ SF - Taj Bradley (R, MIN) vs Anthony Molina (R, SF)",
        "kLines": {'Bradley': {'k': 6.7, 'lo': 5, 'hi': 8, 'bf': 23.7, 'matchupK': 28.2, 'ownK': 28.8}, 'Molina': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 20.9, 'matchupK': 21.0, 'ownK': 21.9}},
        "description": "Tail key data: Park boost -21% (stadium -17%, weather -4%). Bradley (HR risk 0.52, vs LHB +1.21, vs RHB -0.25). Molina (HR risk 0.41, vs LHB +1.36, vs RHB -0.48).",
        "rows": [
            row("Andrew Knizner", "R", "N/A", 64, "", ["vs Bradley"], """0 HR, 1 near-HR, 94.4 mph EV, 25.0% barrels. Bradley RHB split -0.25, HR risk 0.52. slight split headwind (-0.25); park/weather net drag (-21%).""", blast="good", contact={'stars': 2, 'k': 26.4, 'batterK': 19.3, 'batterWhiff': 29.6, 'pitcherK': 28.8}),
            row("Shay Whitcomb", "R", "N/A", 73, "🌕 💣", ["vs Bradley"], """0 HR, 1 near-HR, 98.6 mph EV, 25.0% barrels. Bradley RHB split -0.25, HR risk 0.52. slight split headwind (-0.25); park/weather net drag (-21%).""", blast="high", contact={'stars': 3, 'k': 23.9, 'batterK': 17.5, 'batterWhiff': 20.4, 'pitcherK': 28.8}),
            row("Drew Gilbert", "L", "+930", 76, "", ["vs Bradley"], """1 HR, 1 near-HR, 90.0 mph EV, 12.5% barrels. Bradley LHB split +1.21, HR risk 0.52. park/weather net drag (-21%).""", blast="good", contact={'stars': 3, 'k': 23.8, 'batterK': 18.2, 'batterWhiff': 19.0, 'pitcherK': 28.8}),
            row("Emmanuel Rodriguez", "L", "+725", 87, "🌕 💣", ["vs Molina"], """2 HR, 2 near-HR, 92.4 mph EV, 57.1% barrels. Molina LHB split +1.36, HR risk 0.41. park/weather net drag (-21%).""", blast="high", contact={'stars': 2, 'k': 25.0, 'batterK': 35.1, 'batterWhiff': 35.3, 'pitcherK': 21.9}),
            row("Josh Bell", "S", "+610", 83, "💎", ["vs Molina"], """Worst Pickz Hidden Gem. 0 HR, 94.9 mph EV, 25.0% barrels. Molina SHB→LHB split +1.36, HR risk 0.41. park/weather net drag (-21%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.0, 'batterK': 17.6, 'batterWhiff': 20.6, 'pitcherK': 21.9}),
            row("Brooks Lee", "S", "+880", 61, "", ["vs Molina"], """0 HR, 93.2 mph EV. Molina SHB→LHB split +1.36, HR risk 0.41. park/weather net drag (-21%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.4, 'batterK': 14.3, 'batterWhiff': 22.2, 'pitcherK': 21.9}),
        ],
    },
    {
        "title": "NYM @ TEX - Sean Manaea 🧤 (L, NYM) vs MacKenzie Gore (L, TEX)",
        "kLines": {'Manaea': {'k': 5.1, 'lo': 3, 'hi': 7, 'bf': 23.4, 'matchupK': 21.8, 'ownK': 20.6}, 'Gore': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 22.4, 'matchupK': 20.9, 'ownK': 20.3}},
        "description": "Tail key data: Park boost -12% (stadium -11%, weather +0%). Manaea 🧤 (HR risk 1.59, vs LHB +0.11, vs RHB +1.42). Gore (HR risk -0.49, vs LHB -0.50, vs RHB -0.26).",
        "rows": [
            row("Josh Jung", "R", "+568", 91, "⭐ 🌕 💣", ["vs Manaea"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 99.3 mph EV, 40.0% barrels. Manaea RHB split +1.42, HR risk 1.59. park/weather net drag (-12%).""", blast="high", contact={'stars': 4, 'k': 19.8, 'batterK': 19.8, 'batterWhiff': 19.9, 'pitcherK': 20.6}),
            row("Jake Burger", "R", "+362", 90, "🌕 💣", ["vs Manaea"], """0 HR, 2 near-HR, 93.2 mph EV, 40.0% barrels. Manaea RHB split +1.42, HR risk 1.59. park/weather net drag (-12%).""", blast="good", contact={'stars': 2, 'k': 24.6, 'batterK': 27.4, 'batterWhiff': 35.6, 'pitcherK': 20.6}),
            row("Justin Foscue", "R", "+482", 86, "", ["vs Manaea"], """0 HR, 94.8 mph EV. Manaea RHB split +1.42, HR risk 1.59. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.9, 'batterK': 28.0, 'batterWhiff': 24.4, 'pitcherK': 20.6}),
            row("Mark Vientos", "R", "+500", 87, "⭐ 🌕 💣", ["vs Gore"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 93.6 mph EV, 37.5% barrels. Gore RHB split -0.26, HR risk -0.49. slight split headwind (-0.26); pitcher suppresses HR (-0.49).""", blast="high", contact={'stars': 3, 'k': 23.6, 'batterK': 27.6, 'batterWhiff': 32.7, 'pitcherK': 20.3}),
            row("Juan Soto", "L", "+346", 77, "", ["vs Gore"], """1 HR, 2 near-HR, 99.9 mph EV, 12.5% barrels. Gore LHB split -0.50, HR risk -0.49. tough split lane (-0.50); pitcher suppresses HR (-0.49).""", blast="good", contact={'stars': 4, 'k': 19.5, 'batterK': 17.8, 'batterWhiff': 22.4, 'pitcherK': 20.3}),
            row("Francisco Alvarez", "R", "+770", 75, "🚀", ["vs Gore"], """1 HR, 1 near-HR, 100.6 mph EV, 12.5% barrels. Gore RHB split -0.26, HR risk -0.49. slight split headwind (-0.26); pitcher suppresses HR (-0.49).""", blast="good", contact={'stars': 1, 'k': 28.2, 'batterK': 41.1, 'batterWhiff': 40.4, 'pitcherK': 20.3}),
            row("Bo Bichette", "R", "+810", 63, "", ["vs Gore"], """0 HR, 2 near-HR, 92.0 mph EV, 12.5% barrels. Gore RHB split -0.26, HR risk -0.49. slight split headwind (-0.26); pitcher suppresses HR (-0.49).""", blast="good", contact={'stars': 4, 'k': 19.8, 'batterK': 19.8, 'batterWhiff': 20.8, 'pitcherK': 20.3}),
        ],
    },
    {
        "title": "SD @ LAD - Michael King (R, SD) vs Roki Sasaki (R, LAD)",
        "kLines": {'King': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 23.4, 'matchupK': 19.2, 'ownK': 20.8}, 'Sasaki': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 22.1, 'matchupK': 20.9, 'ownK': 21.4}},
        "description": "Tail key data: Park boost +20% (stadium +19%, weather +0%). King (HR risk -0.34, vs LHB -0.02, vs RHB -0.24). Sasaki (BAA vs LHB .237, vs RHB .253, HR/9 1.66).",
        "rows": [
            row("Mookie Betts", "R", "+532", 66, "💎", ["vs King"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.6 mph EV. King RHB split -0.24, HR risk -0.34. slight split headwind (-0.24); pitcher risk below avg (-0.34).""", blast="good", contact={'stars': 5, 'k': 15.6, 'batterK': 9.7, 'batterWhiff': 12.9, 'pitcherK': 20.8}),
            row("Teoscar Hernandez", "R", "+522", 65, "", ["vs King"], """0 HR, 94.0 mph EV. King RHB split -0.24, HR risk -0.34. slight split headwind (-0.24); pitcher risk below avg (-0.34).""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 23.3, 'batterWhiff': 35.3, 'pitcherK': 20.8}),
            row("Enrique Hernandez", "R", "N/A", 74, "", ["vs King"], """1 HR, 1 near-HR, 96.1 mph EV, 12.5% barrels. King RHB split -0.24, HR risk -0.34. slight split headwind (-0.24); pitcher risk below avg (-0.34).""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 33.3, 'batterWhiff': 27.8, 'pitcherK': 20.8}),
            row("Max Muncy", "L", "+421", 69, "", ["vs King"], """0 HR, 89.8 mph EV, 12.5% barrels. King LHB split -0.02, HR risk -0.34. slight split headwind (-0.02); pitcher risk below avg (-0.34).""", contact={'stars': 3, 'k': 22.5, 'batterK': 24.0, 'batterWhiff': 28.7, 'pitcherK': 20.8}),
            row("Kyle Tucker", "L", "+591", 71, "⭐", ["vs King"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.9 mph EV, 12.5% barrels. King LHB split -0.02, HR risk -0.34. slight split headwind (-0.02); pitcher risk below avg (-0.34).""", blast="good", contact={'stars': 5, 'k': 16.5, 'batterK': 10.3, 'batterWhiff': 13.6, 'pitcherK': 20.8}),
            row("Fernando Tatis Jr.", "R", "+362", 93, "⭐ 🌕 💣", ["vs Sasaki"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 91.9 mph EV, 37.5% barrels. limited split/risk sample.""", blast="high", contact={'stars': 4, 'k': 19.4, 'batterK': 16.3, 'batterWhiff': 21.3, 'pitcherK': 21.4}),
            row("Jackson Merrill", "L", "+499", 82, "", ["vs Sasaki"], """0 HR, 98.8 mph EV, 12.5% barrels. limited split/risk sample; limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.6, 'batterK': 21.8, 'batterWhiff': 30.3, 'pitcherK': 21.4}),
            row("Ty France", "R", "+514", 65, "💎", ["vs Sasaki"], """Worst Pickz Hidden Gem. 0 HR, 90.8 mph EV. limited split/risk sample; limited recent HR events.""", contact={'stars': 3, 'k': 21.5, 'batterK': 18.4, 'batterWhiff': 29.4, 'pitcherK': 21.4}),
        ],
    },
    {
        "title": "STL @ PIT - Andre Pallante (R, STL) vs Jared Jones (R, PIT)",
        "kLines": {'Pallante': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 23.0, 'matchupK': 16.7, 'ownK': 14.7}, 'Jones': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 20.4, 'matchupK': 26.0, 'ownK': 28.1}},
        "description": "Tail key data: Park boost -33% (stadium -15%, weather -18%). Pallante (HR risk -1.21, vs LHB -0.51, vs RHB -1.27). Jones (HR risk -0.58, vs LHB +0.00, vs RHB -0.84).",
        "rows": [
            row("Rafael Flores", "R", "+1000", 65, "", ["vs Pallante"], """1 HR, 1 near-HR, 95.3 mph EV, 25.0% barrels. Pallante RHB split -1.27, HR risk -1.21. tough split lane (-1.27); pitcher suppresses HR (-1.21).""", blast="good", contact={'stars': 4, 'k': 19.1, 'batterK': 25.7, 'batterWhiff': 26.8, 'pitcherK': 14.7}),
            row("Bryan Reynolds", "S", "+1200", 65, "", ["vs Pallante"], """0 HR, 2 near-HR, 96.2 mph EV, 25.0% barrels. Pallante SHB→LHB split -0.51, HR risk -1.21. tough split lane (-0.51); pitcher suppresses HR (-1.21).""", blast="good", contact={'stars': 4, 'k': 17.6, 'batterK': 20.2, 'batterWhiff': 24.7, 'pitcherK': 14.7}),
            row("Henry Davis", "R", "N/A", 51, "", ["vs Pallante"], """1 HR, 1 near-HR, 87.6 mph EV, 12.5% barrels. Pallante RHB split -1.27, HR risk -1.21. tough split lane (-1.27); pitcher suppresses HR (-1.21).""", blast="good", contact={'stars': 4, 'k': 18.3, 'batterK': 19.3, 'batterWhiff': 28.0, 'pitcherK': 14.7}),
            row("Leonardo Bernal", "S", "+625", 73, "🌕 💣 💎", ["vs Jones"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 97.0 mph EV, 25.0% barrels. Jones SHB→LHB split +0.00, HR risk -0.58. pitcher suppresses HR (-0.58); park/weather net drag (-33%).""", blast="high", contact={'stars': 2, 'k': 24.2, 'batterK': 20.3, 'batterWhiff': 22.4, 'pitcherK': 28.1}),
            row("Jordan Walker", "R", "+725", 54, "", ["vs Jones"], """0 HR, 99.1 mph EV. Jones RHB split -0.84, HR risk -0.58. tough split lane (-0.84); pitcher suppresses HR (-0.58).""", blast="good", contact={'stars': 1, 'k': 32.4, 'batterK': 37.5, 'batterWhiff': 39.7, 'pitcherK': 28.1}),
            row("Alec Burleson", "L", "+725", 58, "", ["vs Jones"], """0 HR, 91.5 mph EV, 12.5% barrels. Jones LHB split +0.00, HR risk -0.58. pitcher suppresses HR (-0.58); park/weather net drag (-33%).""", contact={'stars': 2, 'k': 26.1, 'batterK': 24.4, 'batterWhiff': 26.2, 'pitcherK': 28.1}),
            row("Nolan Gorman", "L", "N/A", 54, "", ["vs Jones"], """0 HR, 1 near-HR, 89.7 mph EV, 12.5% barrels. Jones LHB split +0.00, HR risk -0.58. pitcher suppresses HR (-0.58); park/weather net drag (-33%).""", contact={'stars': 1, 'k': 28.1, 'batterK': 30.2, 'batterWhiff': 31.1, 'pitcherK': 28.1}),
            row("Ivan Herrera", "R", "+875", 53, "💎", ["vs Jones"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 88.3 mph EV, 12.5% barrels. Jones RHB split -0.84, HR risk -0.58. tough split lane (-0.84); pitcher suppresses HR (-0.58).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 18.0, 'batterWhiff': 20.9, 'pitcherK': 28.1}),
        ],
    },
    {
        "title": "TB @ NYY (G1) - Nick Martinez (R, TB) vs Carlos Rodon (L, NYY)",
        "kLines": {'Martinez': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 23.2, 'matchupK': 18.6, 'ownK': 17.0}, 'Rodon': {'k': 4.8, 'lo': 3, 'hi': 6, 'bf': 21.2, 'matchupK': 22.8, 'ownK': 26.5}},
        "description": "Tail key data: Park boost -28% (stadium +5%, weather -34%). Martinez (HR risk -0.28, vs LHB -0.70, vs RHB +0.26). Rodon (HR risk -0.19, vs LHB +0.18, vs RHB -0.23).",
        "rows": [
            row("Cody Bellinger", "L", "+570", 64, "⭐", ["vs Martinez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.4 mph EV, 12.5% barrels. Martinez LHB split -0.70, HR risk -0.28. tough split lane (-0.70); pitcher risk below avg (-0.28).""", blast="good", contact={'stars': 5, 'k': 16.9, 'batterK': 15.6, 'batterWhiff': 20.8, 'pitcherK': 17.0}),
            row("Austin Wells", "L", "+520", 64, "💎", ["vs Martinez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.1 mph EV, 25.0% barrels. Martinez LHB split -0.70, HR risk -0.28. tough split lane (-0.70); pitcher risk below avg (-0.28).""", blast="good", contact={'stars': 4, 'k': 18.9, 'batterK': 21.9, 'batterWhiff': 23.2, 'pitcherK': 17.0}),
            row("Ben Rice", "L", "+370", 52, "⭐", ["vs Martinez"], """Worst Pickz Favorite. 0 HR, 88.1 mph EV. Martinez LHB split -0.70, HR risk -0.28. tough split lane (-0.70); pitcher risk below avg (-0.28).""", contact={'stars': 5, 'k': 17.2, 'batterK': 18.7, 'batterWhiff': 17.4, 'pitcherK': 17.0}),
            row("Heliot Ramos", "R", "+540", 74, "🌕 💣 💎", ["vs Martinez"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 89.0 mph EV, 25.0% barrels. Martinez RHB split +0.26, HR risk -0.28. pitcher risk below avg (-0.28); park/weather net drag (-28%).""", blast="high", contact={'stars': 3, 'k': 22.1, 'batterK': 27.7, 'batterWhiff': 34.8, 'pitcherK': 17.0}),
            row("Victor Mesa Jr.", "L", "+570", 58, "", ["vs Rodon"], """1 HR, 2 near-HR, 86.6 mph EV, 12.5% barrels. Rodon LHB split +0.18, HR risk -0.19. pitcher risk below avg (-0.19); park/weather net drag (-28%).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 13.4, 'batterWhiff': 27.0, 'pitcherK': 26.5}),
            row("Junior Caminero", "R", "+418", 57, "", ["vs Rodon"], """0 HR, 1 near-HR, 86.6 mph EV, 12.5% barrels. Rodon RHB split -0.23, HR risk -0.19. slight split headwind (-0.23); pitcher risk below avg (-0.19).""", contact={'stars': 3, 'k': 23.1, 'batterK': 21.3, 'batterWhiff': 19.6, 'pitcherK': 26.5}),
            row("Jonathan Aranda", "L", "+760", 46, "", ["vs Rodon"], """0 HR, 1 near-HR, 86.8 mph EV. Rodon LHB split +0.18, HR risk -0.19. pitcher risk below avg (-0.19); park/weather net drag (-28%).""", contact={'stars': 2, 'k': 25.2, 'batterK': 25.3, 'batterWhiff': 24.2, 'pitcherK': 26.5}),
        ],
    },
    {
        "title": "TB @ NYY (G2) - Drew Rasmussen (R, TB) vs Max Fried (L, NYY)",
        "kLines": {'Rasmussen': {'k': 5.6, 'lo': 4, 'hi': 7, 'bf': 22.1, 'matchupK': 25.5, 'ownK': 26.1}, 'Fried': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 21.5, 'matchupK': 24.3, 'ownK': 28.9}},
        "description": "Tail key data: Park boost -30% (stadium +5%, weather -35%). Rasmussen (HR risk -0.82, vs LHB +0.21, vs RHB -1.14). Fried (HR risk -1.04, vs LHB -0.98, vs RHB -0.73).",
        "rows": [
            row("Cody Bellinger", "L", "+520", 63, "⭐", ["vs Rasmussen"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.4 mph EV, 12.5% barrels. Rasmussen LHB split +0.21, HR risk -0.82. pitcher suppresses HR (-0.82); park/weather net drag (-30%).""", blast="good", contact={'stars': 3, 'k': 21.5, 'batterK': 15.6, 'batterWhiff': 20.8, 'pitcherK': 26.1}),
            row("Austin Wells", "L", "+575", 66, "💎", ["vs Rasmussen"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.1 mph EV, 25.0% barrels. Rasmussen LHB split +0.21, HR risk -0.82. pitcher suppresses HR (-0.82); park/weather net drag (-30%).""", blast="good", contact={'stars': 3, 'k': 23.9, 'batterK': 21.9, 'batterWhiff': 23.2, 'pitcherK': 26.1}),
            row("Ben Rice", "L", "+350", 53, "", ["vs Rasmussen"], """0 HR, 88.1 mph EV. Rasmussen LHB split +0.21, HR risk -0.82. pitcher suppresses HR (-0.82); park/weather net drag (-30%).""", contact={'stars': 3, 'k': 21.8, 'batterK': 18.7, 'batterWhiff': 17.4, 'pitcherK': 26.1}),
            row("Spencer Jones", "L", "+450", 58, "💎", ["vs Rasmussen"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 88.9 mph EV, 12.5% barrels. Rasmussen LHB split +0.21, HR risk -0.82. pitcher suppresses HR (-0.82); park/weather net drag (-30%).""", contact={'stars': 1, 'k': 31.3, 'batterK': 36.7, 'batterWhiff': 40.5, 'pitcherK': 26.1}),
            row("Junior Caminero", "R", "+420", 53, "", ["vs Fried"], """0 HR, 1 near-HR, 83.0 mph EV, 12.5% barrels. Fried RHB split -0.73, HR risk -1.04. tough split lane (-0.73); pitcher suppresses HR (-1.04).""", contact={'stars': 2, 'k': 24.2, 'batterK': 21.3, 'batterWhiff': 19.6, 'pitcherK': 28.9}),
            row("Yandy Diaz", "R", "+800", 46, "💎", ["vs Fried"], """Worst Pickz Hidden Gem. 0 HR, 89.7 mph EV. Fried RHB split -0.73, HR risk -1.04. tough split lane (-0.73); pitcher suppresses HR (-1.04).""", contact={'stars': 3, 'k': 22.2, 'batterK': 16.5, 'batterWhiff': 17.9, 'pitcherK': 28.9}),
        ],
    },
    {
        "title": "TOR @ BAL - Max Scherzer (R, TOR) vs Chris Bassitt (R, BAL)",
        "kLines": {'Scherzer': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 20.2, 'matchupK': 21.1, 'ownK': 18.8}, 'Bassitt': {'k': 3.9, 'lo': 2, 'hi': 5, 'bf': 22.8, 'matchupK': 17.0, 'ownK': 17.8}},
        "description": "Tail key data: Park boost -28% (stadium -4%, weather -25%). Scherzer (HR risk 0.47, vs LHB +0.95, vs RHB -0.05). Bassitt (HR risk -0.26, vs LHB +0.15, vs RHB -0.49).",
        "rows": [
            row("Pete Alonso", "R", "+333", 87, "🌕 💣", ["vs Scherzer"], """2 HR, 2 near-HR, 83.9 mph EV, 25.0% barrels. Scherzer RHB split -0.05, HR risk 0.47. slight split headwind (-0.05); park/weather net drag (-28%).""", blast="high", contact={'stars': 3, 'k': 20.0, 'batterK': 22.7, 'batterWhiff': 21.6, 'pitcherK': 18.8}),
            row("Colton Cowser", "L", "+630", 62, "", ["vs Scherzer"], """0 HR, 90.5 mph EV. Scherzer LHB split +0.95, HR risk 0.47. park/weather net drag (-28%); limited recent HR events.""", contact={'stars': 2, 'k': 24.3, 'batterK': 40.7, 'batterWhiff': 30.6, 'pitcherK': 18.8}),
            row("Gunnar Henderson", "L", "+456", 69, "", ["vs Scherzer"], """0 HR, 1 near-HR, 83.4 mph EV, 25.0% barrels. Scherzer LHB split +0.95, HR risk 0.47. park/weather net drag (-28%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.5, 'batterK': 22.6, 'batterWhiff': 19.0, 'pitcherK': 18.8}),
            row("Sean Keys", "L", "N/A", 72, "", ["vs Bassitt"], """1 HR, 1 near-HR, 92.5 mph EV, 37.5% barrels. Bassitt LHB split +0.15, HR risk -0.26. pitcher risk below avg (-0.26); park/weather net drag (-28%).""", blast="good", contact={'stars': 3, 'k': 22.7, 'batterK': 36.5, 'batterWhiff': 31.0, 'pitcherK': 17.8}),
            row("Kazuma Okamoto", "R", "+566", 56, "", ["vs Bassitt"], """0 HR, 93.0 mph EV. Bassitt RHB split -0.49, HR risk -0.26. tough split lane (-0.49); pitcher risk below avg (-0.26).""", blast="good", contact={'stars': 3, 'k': 20.7, 'batterK': 23.2, 'batterWhiff': 28.7, 'pitcherK': 17.8}),
            row("Josh Smith", "L", "+920", 41, "", ["vs Bassitt"], """0 HR, 84.7 mph EV. Bassitt LHB split +0.15, HR risk -0.26. pitcher risk below avg (-0.26); park/weather net drag (-28%).""", contact={'stars': 3, 'k': 21.2, 'batterK': 29.1, 'batterWhiff': 27.1, 'pitcherK': 17.8}),
        ],
    },
    {
        "title": "WSH @ DET - Jackson Kent (L, WSH) vs Drew Anderson (R, DET)",
        "kLines": {'Kent': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 21.6, 'matchupK': 19.8, 'ownK': 17.9}, 'Anderson': {'k': 4.1, 'lo': 3, 'hi': 6, 'bf': 19.9, 'matchupK': 20.8, 'ownK': 20.6}},
        "description": "Tail key data: Park boost -20% (stadium -11%, weather -9%). Kent (HR risk -1.00, vs LHB +0.75, vs RHB -1.23). Anderson (HR risk 0.06, vs LHB +0.28, vs RHB -0.03).",
        "rows": [
            row("Riley Greene", "L", "+600", 80, "⭐ 🌕 💣", ["vs Kent"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 90.1 mph EV, 37.5% barrels. Kent LHB split +0.75, HR risk -1.00. pitcher suppresses HR (-1.00); park/weather net drag (-20%).""", blast="high", contact={'stars': 3, 'k': 22.1, 'batterK': 24.1, 'batterWhiff': 31.4, 'pitcherK': 17.9}),
            row("Hao-Yu Lee", "R", "+730", 76, "🚀 🌕 💣", ["vs Kent"], """2 HR, 3 near-HR, 101.3 mph EV, 50.0% barrels. Kent RHB split -1.23, HR risk -1.00. tough split lane (-1.23); pitcher suppresses HR (-1.00).""", blast="high", contact={'stars': 3, 'k': 22.9, 'batterK': 29.9, 'batterWhiff': 26.9, 'pitcherK': 17.9}),
            row("Spencer Torkelson", "R", "+546", 54, "", ["vs Kent"], """0 HR, 1 near-HR, 92.9 mph EV, 12.5% barrels. Kent RHB split -1.23, HR risk -1.00. tough split lane (-1.23); pitcher suppresses HR (-1.00).""", blast="good", contact={'stars': 2, 'k': 24.0, 'batterK': 28.8, 'batterWhiff': 36.6, 'pitcherK': 17.9}),
            row("James Wood", "L", "+425", 63, "", ["vs Anderson"], """0 HR, 91.1 mph EV. Anderson LHB split +0.28, HR risk 0.06. park/weather net drag (-20%); limited recent HR events.""", contact={'stars': 3, 'k': 22.7, 'batterK': 28.6, 'batterWhiff': 22.6, 'pitcherK': 20.6}),
            row("Abimelec Ortiz", "L", "+790", 56, "", ["vs Anderson"], """0 HR, 94.7 mph EV. Anderson LHB split +0.28, HR risk 0.06. park/weather net drag (-20%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.3, 'batterK': 28.8, 'batterWhiff': 24.2, 'pitcherK': 20.6}),
            row("CJ Abrams", "L", "+568", 60, "", ["vs Anderson"], """0 HR, 92.6 mph EV. Anderson LHB split +0.28, HR risk 0.06. park/weather net drag (-20%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.4, 'batterK': 31.0, 'batterWhiff': 33.3, 'pitcherK': 20.6}),
            row("Andres Chaparro", "R", "N/A", 51, "", ["vs Anderson"], """0 HR, 89.9 mph EV, 12.5% barrels. Anderson RHB split -0.03, HR risk 0.06. slight split headwind (-0.03); park/weather net drag (-20%).""", contact={'stars': 3, 'k': 23.1, 'batterK': 23.1, 'batterWhiff': 32.4, 'pitcherK': 20.6}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-22")

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

    out = ROOT / '_games-0922.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
