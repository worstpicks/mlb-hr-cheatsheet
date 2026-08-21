#!/usr/bin/env python3
"""Generate games[] block for 2026-08-21 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Adley Rutschman (S)",
    "Alec Bohm (R)",
    "Brandon Lowe (L)",
    "Brett Baty (L)",
    "Corey Seager (L)",
    "Francisco Lindor (S)",
    "Griffin Conine (L)",
    "Hunter Feduccia (L)",
    "Ivan Herrera (R)",
    "Jo Adell (R)",
    "Munetaka Murakami (L)",
    "Pete Alonso (R)",
    "Ryan Vilade (R)",
    "Teoscar Hernandez (R)",
    "Wilyer Abreu (L)",
    "Yandy Diaz (R)",
}

GEMS = {
    "Alejandro Kirk (R)",
    "Amed Rosario (R)",
    "Andres Chaparro (R)",
    "Angel Genao (S)",
    "Bryce Eldridge (L)",
    "Dylan Beavers (L)",
    "Gunnar Henderson (L)",
    "Ian Happ (S)",
    "Jesus Sanchez (L)",
    "Jose Siri (R)",
    "Max Muncy (L)",
    "Mickey Gasper (S)",
    "Vinnie Pasquantino (L)",
    "Zach Neto (R)",
}

PLAYER_TEAMS = {
    "AJ Ewing (L)": "NYM",
    "Adley Rutschman (S)": "BOS",
    "Alec Bohm (R)": "PHI",
    "Alejandro Kirk (R)": "TOR",
    "Alex Bregman (R)": "CHC",
    "Amed Rosario (R)": "NYY",
    "Andres Chaparro (R)": "WSH",
    "Angel Genao (S)": "CLE",
    "Ben Rice (L)": "NYY",
    "Brandon Lowe (L)": "PIT",
    "Brett Baty (L)": "NYM",
    "Bryce Eldridge (L)": "SF",
    "Byron Buxton (R)": "MIN",
    "Cal Raleigh (S)": "SEA",
    "Carson Benge (L)": "NYM",
    "Charles McAdoo (R)": "TOR",
    "Coby Mayo (R)": "BAL",
    "Corey Seager (L)": "TEX",
    "Donovan Walton (L)": "ATH",
    "Dylan Beavers (L)": "BAL",
    "Dylan Crews (R)": "WSH",
    "Eduardo Valencia (R)": "DET",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Lindor (S)": "NYM",
    "Freddy Fermin (R)": "SD",
    "Gabriel Moreno (R)": "ARI",
    "Griffin Conine (L)": "MIA",
    "Gunnar Henderson (L)": "BAL",
    "Heliot Ramos (R)": "NYY",
    "Hunter Feduccia (L)": "LAD",
    "Ian Happ (S)": "CHC",
    "Ivan Herrera (R)": "STL",
    "JT Realmuto (R)": "PHI",
    "Jac Caglianone (L)": "KC",
    "Jackson Merrill (L)": "SD",
    "Jake McCarthy (L)": "COL",
    "Jesus Sanchez (L)": "TOR",
    "Jo Adell (R)": "CLE",
    "Joe Mack (L)": "MIA",
    "Jose Siri (R)": "LAA",
    "Joshua Baez (R)": "STL",
    "Keibert Ruiz (S)": "WSH",
    "Kevin Alcantara (R)": "CHC",
    "Kody Clemens (L)": "MIN",
    "Lawrence Butler (L)": "ATH",
    "Luisangel Acuna (R)": "CWS",
    "Max Muncy (L)": "LAD",
    "Michael Conforto (L)": "CHC",
    "Michael Massey (L)": "KC",
    "Mickey Gasper (S)": "BOS",
    "Miguel Amaya (R)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Moises Ballesteros (L)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Oneil Cruz (L)": "PIT",
    "Owen Caissie (L)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Rafael Flores (R)": "PIT",
    "Randal Grichuk (R)": "CWS",
    "Ryan Jeffers (R)": "MIN",
    "Ryan Vilade (R)": "TB",
    "Sal Stewart (R)": "CIN",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Tyler Stephenson (R)": "CIN",
    "Vinnie Pasquantino (L)": "KC",
    "Willi Castro (S)": "COL",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("CLE @ COL", "Gordon"),
    ("MIN @ SD", "Prielipp"),
    ("NYM @ CWS", "Manaea"),
    ("WSH @ MIA", "Gusto"),
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
        "title": "ATH @ HOU - J.T. Ginn (R, ATH) vs Hayden Wesneski (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +0%). Ginn (HR risk -0.31, vs LHB +0.24, vs RHB -0.48). Wesneski (HR risk 0.01, vs LHB +1.22, vs RHB -1.18).",
        "rows": [
            row("Yordan Alvarez", "L", "+270", 58, "", ["vs Ginn"], """0 HR, 94.8 mph EV. Ginn LHB split +0.24, HR risk -0.31. pitcher risk below avg (-0.31); limited recent HR events.""", blast="good"),
            row("Lawrence Butler", "L", "+581", 80, "🌕 💣", ["vs Wesneski"], """2 HR, 2 near-HR, 91.0 mph EV. Wesneski LHB split +1.22, HR risk 0.01.""", blast="high"),
            row("Zack Gelof", "R", "+541", 72, "🌕 💣", ["vs Wesneski"], """2 HR, 3 near-HR, 93.6 mph EV. Wesneski RHB split -1.18, HR risk 0.01. tough split lane (-1.18).""", blast="high"),
            row("Donovan Walton", "L", "+1000", 60, "", ["vs Wesneski"], """0 HR, 90.0 mph EV. Wesneski LHB split +1.22, HR risk 0.01. limited recent HR events."""),
        ],
    },
    {
        "title": "CHC @ SEA - Matthew Boyd (R, CHC) vs Emerson Hancock (R, SEA)",
        "description": "Tail key data: Park boost +4% (stadium +0%, weather +4%). Boyd (HR risk 0.90, vs LHB -0.89, vs RHB +1.18). Hancock (HR risk 0.21, vs LHB +0.54, vs RHB -0.06).",
        "rows": [
            row("Cal Raleigh", "S", "+360", 86, "", ["vs Boyd"], """1 HR, 1 near-HR, 97.1 mph EV. Boyd SHB→RHB split +1.18, HR risk 0.90.""", blast="good"),
            row("Ian Happ", "S", "+491", 72, "💎", ["vs Hancock"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.4 mph EV. Hancock SHB→LHB split +0.54, HR risk 0.21.""", blast="good"),
            row("Pete Crow Armstrong", "L", "+320", 83, "🌕 💣", ["vs Hancock"], """3 HR, 3 near-HR, 90.1 mph EV. Hancock LHB split +0.54, HR risk 0.21.""", blast="high"),
            row("Alex Bregman", "R", "+680", 58, "", ["vs Hancock"], """0 HR, 89.2 mph EV. Hancock RHB split -0.06, HR risk 0.21. slight split headwind (-0.06); limited recent HR events."""),
            row("Kevin Alcantara", "R", "N/A", 61, "", ["vs Hancock"], """0 HR, 98.5 mph EV. Hancock RHB split -0.06, HR risk 0.21. slight split headwind (-0.06); limited recent HR events.""", blast="good"),
            row("Miguel Amaya", "R", "+880", 67, "", ["vs Hancock"], """1 HR, 2 near-HR, 94.7 mph EV. Hancock RHB split -0.06, HR risk 0.21. slight split headwind (-0.06).""", blast="good"),
            row("Michael Conforto", "L", "+544", 66, "", ["vs Hancock"], """1 HR, 2 near-HR, 88.3 mph EV. Hancock LHB split +0.54, HR risk 0.21.""", blast="good"),
        ],
    },
    {
        "title": "CIN @ ARI - Nick Lodolo (R, CIN) vs Eduardo Rodriguez (R, ARI)",
        "description": "Tail key data: Park boost -9% (stadium -9%, weather -1%). Lodolo (HR risk 0.69, vs LHB -1.16, vs RHB +0.91). Rodriguez (HR risk -0.69, vs LHB -0.71, vs RHB -0.34).",
        "rows": [
            row("Gabriel Moreno", "R", "+920", 74, "", ["vs Lodolo"], """1 HR, 1 near-HR, 91.7 mph EV. Lodolo RHB split +0.91, HR risk 0.69. park/weather net drag (-9%).""", blast="good"),
            row("Tim Tawa", "R", "+760", 72, "", ["vs Lodolo"], """0 HR, 94.4 mph EV. Lodolo RHB split +0.91, HR risk 0.69. park/weather net drag (-9%); limited recent HR events.""", blast="good"),
            row("Tyler Stephenson", "R", "+660", 58, "", ["vs Rodriguez"], """0 HR, 1 near-HR, 94.2 mph EV. Rodriguez RHB split -0.34, HR risk -0.69. slight split headwind (-0.34); pitcher suppresses HR (-0.69).""", blast="good"),
            row("Sal Stewart", "R", "+493", 58, "🌕 💣", ["vs Rodriguez"], """2 HR, 2 near-HR, 90.4 mph EV. Rodriguez RHB split -0.34, HR risk -0.69. slight split headwind (-0.34); pitcher suppresses HR (-0.69).""", blast="high"),
        ],
    },
    {
        "title": "CLE @ COL - Joey Cantillo (R, CLE) vs Tanner Gordon 🧤 (R, COL)",
        "description": "Tail key data: Park boost +20% (stadium +21%, weather -1%). Cantillo (HR risk 0.75, vs LHB +0.02, vs RHB +0.74). Gordon 🧤 (HR risk 1.37, vs LHB +1.19, vs RHB +0.85).",
        "rows": [
            row("Jake McCarthy", "L", "N/A", 74, "", ["vs Cantillo"], """1 HR, 1 near-HR, 91.0 mph EV. Cantillo LHB split +0.02, HR risk 0.75.""", blast="good"),
            row("Willi Castro", "S", "N/A", 90, "🌕 💣", ["vs Cantillo"], """1 HR, 3 near-HR, 97.2 mph EV. Cantillo SHB→RHB split +0.74, HR risk 0.75.""", blast="good"),
            row("Jo Adell", "R", "N/A", 87, "⭐", ["vs Gordon"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 93.3 mph EV. Gordon RHB split +0.85, HR risk 1.37. limited recent HR events.""", blast="good"),
            row("Angel Genao", "S", "N/A", 80, "💎", ["vs Gordon"], """Worst Pickz Hidden Gem. 0 HR, 89.3 mph EV. Gordon SHB→LHB split +1.19, HR risk 1.37. limited recent HR events."""),
        ],
    },
    {
        "title": "DET @ KC - Troy Melton (R, DET) vs Noah Cameron (R, KC)",
        "description": "Tail key data: Park boost +12% (stadium +10%, weather +2%). Melton (HR risk -0.81, vs LHB -0.02, vs RHB -1.18). Cameron (HR risk -0.99, vs LHB +0.15, vs RHB -0.92).",
        "rows": [
            row("Michael Massey", "L", "+730", 66, "🌕 💣", ["vs Melton"], """2 HR, 2 near-HR, 92.7 mph EV. Melton LHB split -0.02, HR risk -0.81. slight split headwind (-0.02); pitcher suppresses HR (-0.81).""", blast="high"),
            row("Vinnie Pasquantino", "L", "+570", 58, "💎", ["vs Melton"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 94.5 mph EV. Melton LHB split -0.02, HR risk -0.81. slight split headwind (-0.02); pitcher suppresses HR (-0.81).""", blast="good"),
            row("Jac Caglianone", "L", "+400", 58, "", ["vs Melton"], """0 HR, 1 near-HR, 97.1 mph EV. Melton LHB split -0.02, HR risk -0.81. slight split headwind (-0.02); pitcher suppresses HR (-0.81).""", blast="good"),
            row("Eduardo Valencia", "R", "+485", 70, "🌕 💣", ["vs Cameron"], """3 HR, 3 near-HR, 95.2 mph EV. Cameron RHB split -0.92, HR risk -0.99. tough split lane (-0.92); pitcher suppresses HR (-0.99).""", blast="high"),
        ],
    },
    {
        "title": "LAA @ TEX - Reid Detmers (R, LAA) vs MacKenzie Gore (R, TEX)",
        "description": "Tail key data: Park boost -12% (stadium -11%, weather +0%). Detmers (HR risk 0.86, vs LHB +0.71, vs RHB +0.41). Gore (HR risk 0.39, vs LHB -0.07, vs RHB +0.40).",
        "rows": [
            row("Corey Seager", "L", "+397", 78, "⭐", ["vs Detmers"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.7 mph EV. Detmers LHB split +0.71, HR risk 0.86. park/weather net drag (-12%).""", blast="good"),
            row("Wyatt Langford", "R", "+490", 69, "", ["vs Detmers"], """0 HR, 1 near-HR, 93.8 mph EV. Detmers RHB split +0.41, HR risk 0.86. park/weather net drag (-12%); limited recent HR events.""", blast="good"),
            row("Jose Siri", "R", "+581", 70, "💎", ["vs Gore"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 97.8 mph EV. Gore RHB split +0.40, HR risk 0.39. park/weather net drag (-12%).""", blast="good"),
            row("Zach Neto", "R", "+470", 67, "💎", ["vs Gore"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.5 mph EV. Gore RHB split +0.40, HR risk 0.39. park/weather net drag (-12%).""", blast="good"),
            row("Moises Ballesteros", "L", "+920", 58, "", ["vs Gore"], """0 HR, 93.5 mph EV. Gore LHB split -0.07, HR risk 0.39. slight split headwind (-0.07); park/weather net drag (-12%).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ SD - Connor Prielipp 🧤 (R, MIN) vs Randy Vasquez (R, SD)",
        "description": "Tail key data: Park boost +6% (stadium -3%, weather +9%). Prielipp 🧤 (HR risk 1.19, vs LHB +0.87, vs RHB +0.94). Vasquez (BAA vs LHB .309, vs RHB .234, HR/9 1.27).",
        "rows": [
            row("Fernando Tatis Jr.", "R", "+400", 97, "🌕 💣", ["vs Prielipp"], """3 HR, 3 near-HR, 97.8 mph EV. Prielipp RHB split +0.94, HR risk 1.19.""", blast="high"),
            row("Jackson Merrill", "L", "+590", 85, "", ["vs Prielipp"], """0 HR, 2 near-HR, 94.7 mph EV. Prielipp LHB split +0.87, HR risk 1.19.""", blast="good"),
            row("Freddy Fermin", "R", "N/A", 83, "", ["vs Prielipp"], """0 HR, 95.3 mph EV. Prielipp RHB split +0.94, HR risk 1.19. limited recent HR events.""", blast="good"),
            row("Kody Clemens", "L", "N/A", 67, "", ["vs Vasquez"], """1 HR, 1 near-HR, 94.7 mph EV. limited split/risk sample.""", blast="good"),
            row("Ryan Jeffers", "R", "N/A", 58, "", ["vs Vasquez"], """0 HR, 2 near-HR, 85.0 mph EV. limited split/risk sample; lighter EV form (85.0 mph).""", blast="good"),
            row("Byron Buxton", "R", "N/A", 58, "", ["vs Vasquez"], """0 HR, 80.8 mph EV. limited split/risk sample; limited recent HR events."""),
        ],
    },
    {
        "title": "NYM @ CWS - Sean Manaea 🧤 (R, NYM) vs Sean Burke (R, CWS)",
        "description": "Tail key data: Park boost +1% (stadium -5%, weather +6%). Manaea 🧤 (HR risk 1.17, vs LHB +0.34, vs RHB +1.11). Burke (HR risk 0.40, vs LHB +0.96, vs RHB -0.25).",
        "rows": [
            row("Munetaka Murakami", "L", "+320", 91, "🚀 ⭐ 🌕 💣", ["vs Manaea"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 102.3 mph EV. Manaea LHB split +0.34, HR risk 1.17.""", blast="high"),
            row("Miguel Vargas", "R", "+335", 85, "", ["vs Manaea"], """1 HR, 1 near-HR, 91.6 mph EV. Manaea RHB split +1.11, HR risk 1.17.""", blast="good"),
            row("Luisangel Acuna", "R", "+1050", 84, "🚀", ["vs Manaea"], """0 HR, 100.0 mph EV. Manaea RHB split +1.11, HR risk 1.17. limited recent HR events.""", blast="good"),
            row("Randal Grichuk", "R", "+375", 83, "", ["vs Manaea"], """0 HR, 94.9 mph EV. Manaea RHB split +1.11, HR risk 1.17. limited recent HR events.""", blast="good"),
            row("Brett Baty", "L", "+555", 87, "⭐ 🌕 💣", ["vs Burke"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.4 mph EV. Burke LHB split +0.96, HR risk 0.40.""", blast="high"),
            row("Francisco Lindor", "S", "+409", 80, "⭐", ["vs Burke"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.0 mph EV. Burke SHB→LHB split +0.96, HR risk 0.40.""", blast="good"),
            row("AJ Ewing", "L", "+690", 66, "", ["vs Burke"], """0 HR, 1 near-HR, 91.4 mph EV. Burke LHB split +0.96, HR risk 0.40. limited recent HR events."""),
            row("Carson Benge", "L", "+570", 75, "", ["vs Burke"], """1 HR, 1 near-HR, 91.9 mph EV. Burke LHB split +0.96, HR risk 0.40.""", blast="good"),
        ],
    },
    {
        "title": "PIT @ LAD - Bubba Chandler (R, PIT) vs Yoshinobu Yamamoto (R, LAD)",
        "description": "Tail key data: Park boost +21% (stadium +18%, weather +4%). Chandler (HR risk -1.27, vs LHB -0.28, vs RHB -1.49). Yamamoto (HR risk -0.46, vs LHB -0.47, vs RHB +0.04).",
        "rows": [
            row("Max Muncy", "L", "+300", 66, "🌕 💣 💎", ["vs Chandler"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 97.2 mph EV. Chandler LHB split -0.28, HR risk -1.27. slight split headwind (-0.28); pitcher suppresses HR (-1.27).""", blast="high"),
            row("Hunter Feduccia", "L", "+870", 58, "⭐", ["vs Chandler"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.4 mph EV. Chandler LHB split -0.28, HR risk -1.27. slight split headwind (-0.28); pitcher suppresses HR (-1.27).""", blast="good"),
            row("Teoscar Hernandez", "R", "+490", 58, "🚀 ⭐", ["vs Chandler"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 101.8 mph EV. Chandler RHB split -1.49, HR risk -1.27. tough split lane (-1.49); pitcher suppresses HR (-1.27).""", blast="good"),
            row("Oneil Cruz", "L", "+410", 68, "🌕 💣", ["vs Yamamoto"], """2 HR, 2 near-HR, 93.0 mph EV. Yamamoto LHB split -0.47, HR risk -0.46. tough split lane (-0.47); pitcher suppresses HR (-0.46).""", blast="high"),
            row("Rafael Flores", "R", "+431", 72, "🌕 💣", ["vs Yamamoto"], """2 HR, 2 near-HR, 92.9 mph EV. Yamamoto RHB split +0.04, HR risk -0.46. pitcher suppresses HR (-0.46).""", blast="high"),
            row("Brandon Lowe", "L", "+425", 71, "⭐ 🌕 💣", ["vs Yamamoto"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.6 mph EV. Yamamoto LHB split -0.47, HR risk -0.46. tough split lane (-0.47); pitcher suppresses HR (-0.46).""", blast="high"),
        ],
    },
    {
        "title": "SF @ BOS - Logan Webb (R, SF) vs Sonny Gray (R, BOS)",
        "description": "Tail key data: Park boost -17% (stadium -10%, weather -7%). Webb (HR risk -1.45, vs LHB -0.91, vs RHB -0.93). Gray (HR risk -0.58, vs LHB -0.74, vs RHB +0.65).",
        "rows": [
            row("Wilyer Abreu", "L", "+525", 58, "⭐", ["vs Webb"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.5 mph EV. Webb LHB split -0.91, HR risk -1.45. tough split lane (-0.91); pitcher suppresses HR (-1.45).""", blast="good"),
            row("Mickey Gasper", "S", "+1200", 58, "🌕 💣 💎", ["vs Webb"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 89.3 mph EV. Webb SHB→LHB split -0.91, HR risk -1.45. tough split lane (-0.91); pitcher suppresses HR (-1.45).""", blast="high"),
            row("Adley Rutschman", "S", "+1000", 58, "⭐", ["vs Webb"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 88.9 mph EV. Webb SHB→LHB split -0.91, HR risk -1.45. tough split lane (-0.91); pitcher suppresses HR (-1.45).""", blast="good"),
            row("Bryce Eldridge", "L", "+660", 58, "💎", ["vs Gray"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 94.0 mph EV. Gray LHB split -0.74, HR risk -0.58. tough split lane (-0.74); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Rafael Devers", "L", "+526", 58, "", ["vs Gray"], """1 HR, 1 near-HR, 92.9 mph EV. Gray LHB split -0.74, HR risk -0.58. tough split lane (-0.74); pitcher suppresses HR (-0.58).""", blast="good"),
        ],
    },
    {
        "title": "STL @ PHI - Hunter Dobbins (R, STL) vs Jesus Luzardo (R, PHI)",
        "description": "Tail key data: Park boost +11% (stadium +15%, weather -5%). Dobbins (HR risk -0.12, vs LHB -0.13, vs RHB +0.24). Luzardo (HR risk -0.78, vs LHB -1.41, vs RHB -0.23).",
        "rows": [
            row("Alec Bohm", "R", "+870", 62, "⭐", ["vs Dobbins"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 92.5 mph EV. Dobbins RHB split +0.24, HR risk -0.12. pitcher risk below avg (-0.12); weather carry headwind (-5%).""", blast="good"),
            row("JT Realmuto", "R", "+820", 58, "", ["vs Dobbins"], """0 HR, 1 near-HR, 91.2 mph EV. Dobbins RHB split +0.24, HR risk -0.12. pitcher risk below avg (-0.12); weather carry headwind (-5%)."""),
            row("Joshua Baez", "R", "+533", 68, "🌕 💣", ["vs Luzardo"], """2 HR, 2 near-HR, 99.9 mph EV. Luzardo RHB split -0.23, HR risk -0.78. slight split headwind (-0.23); pitcher suppresses HR (-0.78).""", blast="high"),
            row("Ivan Herrera", "R", "+750", 58, "⭐", ["vs Luzardo"], """Worst Pickz Favorite. 0 HR, 94.3 mph EV. Luzardo RHB split -0.23, HR risk -0.78. slight split headwind (-0.23); pitcher suppresses HR (-0.78).""", blast="good"),
        ],
    },
    {
        "title": "TB @ BAL - Freddy Peralta (R, TB) vs Trevor Rogers (R, BAL)",
        "description": "Tail key data: Park boost -7% (stadium -5%, weather -2%). Peralta (HR risk 0.74, vs LHB +0.51, vs RHB +0.67). Rogers (HR risk -0.12, vs LHB -1.35, vs RHB +0.36).",
        "rows": [
            row("Pete Alonso", "R", "+328", 87, "🚀 ⭐ 🌕 💣", ["vs Peralta"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 101.3 mph EV. Peralta RHB split +0.67, HR risk 0.74. park/weather net drag (-7%).""", blast="high"),
            row("Coby Mayo", "R", "+430", 72, "", ["vs Peralta"], """0 HR, 1 near-HR, 94.4 mph EV. Peralta RHB split +0.67, HR risk 0.74. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
            row("Gunnar Henderson", "L", "+431", 78, "💎", ["vs Peralta"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 96.2 mph EV. Peralta LHB split +0.51, HR risk 0.74. park/weather net drag (-7%).""", blast="good"),
            row("Dylan Beavers", "L", "+690", 89, "🌕 💣 💎", ["vs Peralta"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 94.8 mph EV. Peralta LHB split +0.51, HR risk 0.74. park/weather net drag (-7%).""", blast="high"),
            row("Yandy Diaz", "R", "+520", 74, "⭐ 🌕 💣", ["vs Rogers"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.8 mph EV. Rogers RHB split +0.36, HR risk -0.12. pitcher risk below avg (-0.12); park/weather net drag (-7%).""", blast="high"),
            row("Ryan Vilade", "R", "+650", 82, "⭐ 🌕 💣", ["vs Rogers"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 95.7 mph EV. Rogers RHB split +0.36, HR risk -0.12. pitcher risk below avg (-0.12); park/weather net drag (-7%).""", blast="high"),
        ],
    },
    {
        "title": "TOR @ NYY - Mason Fluharty (R, TOR) vs Cam Schlittler (R, NYY)",
        "description": "Tail key data: Park boost +12% (stadium +5%, weather +7%). Fluharty (HR risk -0.28, vs LHB -0.50, vs RHB +0.64). Schlittler (HR risk -0.41, vs LHB +0.07, vs RHB -0.66).",
        "rows": [
            row("Amed Rosario", "R", "+960", 76, "🌕 💣 💎", ["vs Fluharty"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 92.9 mph EV. Fluharty RHB split +0.64, HR risk -0.28. pitcher risk below avg (-0.28).""", blast="high"),
            row("Heliot Ramos", "R", "+500", 65, "", ["vs Fluharty"], """0 HR, 98.7 mph EV. Fluharty RHB split +0.64, HR risk -0.28. pitcher risk below avg (-0.28); limited recent HR events.""", blast="good"),
            row("Ben Rice", "L", "+390", 58, "", ["vs Fluharty"], """0 HR, 1 near-HR, 91.2 mph EV. Fluharty LHB split -0.50, HR risk -0.28. tough split lane (-0.50); pitcher risk below avg (-0.28)."""),
            row("Jesus Sanchez", "L", "+625", 61, "💎", ["vs Schlittler"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 90.8 mph EV. Schlittler LHB split +0.07, HR risk -0.41. pitcher suppresses HR (-0.41).""", blast="good"),
            row("Alejandro Kirk", "R", "+800", 67, "🌕 💣 💎", ["vs Schlittler"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 89.7 mph EV. Schlittler RHB split -0.66, HR risk -0.41. tough split lane (-0.66); pitcher suppresses HR (-0.41).""", blast="high"),
            row("Charles McAdoo", "R", "+980", 58, "", ["vs Schlittler"], """1 HR, 1 near-HR, 91.8 mph EV. Schlittler RHB split -0.66, HR risk -0.41. tough split lane (-0.66); pitcher suppresses HR (-0.41).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ MIA - Brad Lord (R, WSH) vs Ryan Gusto 🧤 (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -12%, weather -1%). Lord (HR risk -0.03, vs LHB +1.65, vs RHB -1.09). Gusto 🧤 (HR risk 1.09, vs LHB +0.32, vs RHB +1.36).",
        "rows": [
            row("Griffin Conine", "L", "+400", 91, "🚀 ⭐ 🌕 💣", ["vs Lord"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 102.0 mph EV. Lord LHB split +1.65, HR risk -0.03. pitcher risk below avg (-0.03); park/weather net drag (-13%).""", blast="high"),
            row("Owen Caissie", "L", "+550", 70, "", ["vs Lord"], """1 HR, 1 near-HR, 91.9 mph EV. Lord LHB split +1.65, HR risk -0.03. pitcher risk below avg (-0.03); park/weather net drag (-13%).""", blast="good"),
            row("Joe Mack", "L", "+710", 70, "", ["vs Lord"], """1 HR, 1 near-HR, 92.2 mph EV. Lord LHB split +1.65, HR risk -0.03. pitcher risk below avg (-0.03); park/weather net drag (-13%).""", blast="good"),
            row("Dylan Crews", "R", "+725", 79, "", ["vs Gusto"], """0 HR, 2 near-HR, 91.0 mph EV. Gusto RHB split +1.36, HR risk 1.09. park/weather net drag (-13%).""", blast="good"),
            row("Andres Chaparro", "R", "+522", 83, "💎", ["vs Gusto"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.4 mph EV. Gusto RHB split +1.36, HR risk 1.09. park/weather net drag (-13%).""", blast="good"),
            row("Keibert Ruiz", "S", "+800", 69, "", ["vs Gusto"], """0 HR, 87.8 mph EV. Gusto SHB→RHB split +1.36, HR risk 1.09. park/weather net drag (-13%); limited recent HR events."""),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-21")

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

    out = ROOT / '_games-0821.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
