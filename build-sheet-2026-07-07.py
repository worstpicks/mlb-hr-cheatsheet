#!/usr/bin/env python3
"""Generate games[] block for 2026-07-07 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Heliot Ramos (R)",
    "Hunter Goodman (R)",
    "Joe Mack (L)",
    "Juan Soto (L)",
    "Kyle Stowers (L)",
    "Matt Olson (L)",
    "Max Kepler (L)",
    "Miguel Vargas (R)",
    "Pete Crow-Armstrong (L)",
    "Riley Greene (L)",
}

GEMS = {
    "Austin Hedges (R)",
    "Byron Buxton (R)",
    "Otto Lopez (R)",
    "Owen Caissie (L)",
    "Pete Alonso (R)",
    "Trent Grisham (L)",
    "Yordan Alvarez (L)",
}

PLAYER_TEAMS = {
    "Alec Bohm (R)": "PHI",
    "Austin Hedges (R)": "CLE",
    "Ben Rice (L)": "NYY",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Brandon Valenzuela (S)": "TOR",
    "Bryce Eldridge (L)": "SF",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Cal Raleigh (S)": "SEA",
    "Carter Jensen (L)": "KC",
    "Casey Schmitt (R)": "SF",
    "Colby Thomas (R)": "ATH",
    "Colson Montgomery (L)": "CWS",
    "Drake Baldwin (L)": "ATL",
    "Freddie Freeman (L)": "LAD",
    "Garrett Mitchell (L)": "MIL",
    "Heliot Ramos (R)": "SF",
    "Hunter Goodman (R)": "COL",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "James Wood (L)": "WSH",
    "Jarren Duran (L)": "BOS",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "Jonah Heim (S)": "ATH",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Josh Bell (S)": "MIN",
    "Josh Lowe (L)": "LAA",
    "Josh Naylor (L)": "SEA",
    "Josh Smith (L)": "TEX",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kerry Carpenter (L)": "DET",
    "Ketel Marte (S)": "ARI",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Stowers (L)": "MIA",
    "Lars Nootbaar (L)": "STL",
    "Luis Garcia Jr. (L)": "WSH",
    "Manny Machado (R)": "SD",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Max Schuemann (R)": "NYY",
    "Michael Harris II (L)": "ATL",
    "Miguel Vargas (R)": "CWS",
    "Mookie Betts (R)": "LAD",
    "Nelson Velazquez (R)": "STL",
    "Nick Kurtz (L)": "ATH",
    "Otto Lopez (R)": "MIA",
    "Owen Caissie (L)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Randal Grichuk (R)": "CWS",
    "Randy Arozarena (R)": "SEA",
    "Riley Greene (L)": "DET",
    "Ryan O'Hearn (L)": "PIT",
    "Sal Stewart (R)": "CIN",
    "Taylor Ward (R)": "BAL",
    "Trea Turner (R)": "PHI",
    "Trent Grisham (L)": "NYY",
    "Ty France (R)": "SD",
    "Tyler Callihan (L)": "PIT",
    "Victor Caratini (S)": "MIN",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("KC @ NYM", "Lugo"),
    ("MIL @ STL", "Dobbins"),
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
        "title": "ARI @ SD - Zac Gallen (R, ARI) vs Jhony Brito (R, SD)",
        "description": "Tail key data: Park boost -6% (stadium -5%, weather +0%). Gallen (HR risk 0.68, vs LHB +0.04, vs RHB +1.07). Home starter risk unavailable.",
        "rows": [
            row("Manny Machado", "R", "+428", 93, "🌕 💣", ["vs Gallen"], """3 HR, 4 near-HR, 94.7 mph EV. Gallen RHB split +1.07, HR risk 0.68. park/weather net drag (-6%).""", blast="high"),
            row("Ty France", "R", "+670", 73, "", ["vs Gallen"], """1 HR, 2 near-HR, 87.3 mph EV. Gallen RHB split +1.07, HR risk 0.68. park/weather net drag (-6%); lighter EV form (87.3 mph).""", blast="good"),
            row("Max Kepler", "L", "+550", 66, "⭐", ["vs Brito"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.4 mph EV. Brito split/risk data unavailable. limited split/risk sample; park/weather net drag (-6%).""", blast="good"),
            row("Ketel Marte", "S", "+331", 65, "", ["vs Brito"], """1 HR, 2 near-HR, 94.9 mph EV. Brito split/risk data unavailable. limited split/risk sample; park/weather net drag (-6%).""", blast="good"),
        ],
    },
    {
        "title": "ATH @ DET - J.T. Ginn (R, ATH) vs Tarik Skubal (L, DET)",
        "description": "Tail key data: Park boost -8% (stadium -11%, weather +3%). Ginn (HR risk -0.60, vs LHB -0.26, vs RHB -0.45). Skubal (HR risk 0.73, vs LHB +0.79, vs RHB +0.40).",
        "rows": [
            row("Riley Greene", "L", "+350", 71, "⭐ 🌕 💣", ["vs Ginn"], """Worst Pickz Favorite. 4 HR, 5 near-HR, 94.5 mph EV. Ginn LHB split -0.26, HR risk -0.60. slight split headwind (-0.26); pitcher suppresses HR (-0.60).""", blast="high"),
            row("Kerry Carpenter", "L", "+420", 59, "🌕 💣", ["vs Ginn"], """2 HR, 2 near-HR, 90.0 mph EV. Ginn LHB split -0.26, HR risk -0.60. slight split headwind (-0.26); pitcher suppresses HR (-0.60).""", blast="high"),
            row("Nick Kurtz", "L", "+450", 73, "", ["vs Skubal"], """0 HR, 98.9 mph EV. Skubal LHB split +0.79, HR risk 0.73. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Colby Thomas", "R", "+650", 68, "", ["vs Skubal"], """1 HR, 1 near-HR, 88.3 mph EV. Skubal RHB split +0.40, HR risk 0.73. park/weather net drag (-8%).""", blast="good"),
            row("Jonah Heim", "S", "+680", 88, "🌕 💣", ["vs Skubal"], """2 HR, 4 near-HR, 89.9 mph EV. Skubal RHB split +0.40, HR risk 0.73. park/weather net drag (-8%).""", blast="high"),
        ],
    },
    {
        "title": "ATL @ PIT - Hurston Waldrep (R, ATL) vs Paul Skenes (R, PIT)",
        "description": "Tail key data: Park boost -7% (stadium -15%, weather +8%). Waldrep (HR risk -0.56, vs LHB -1.39, vs RHB +0.77). Skenes (HR risk 0.07, vs LHB +0.19, vs RHB -0.12).",
        "rows": [
            row("Brandon Lowe", "L", "+400", 58, "", ["vs Waldrep"], """0 HR, 93.9 mph EV. Waldrep LHB split -1.39, HR risk -0.56. tough split lane (-1.39); pitcher suppresses HR (-0.56).""", blast="good"),
            row("Ryan O'Hearn", "L", "+800", 59, "🌕 💣", ["vs Waldrep"], """2 HR, 2 near-HR, 92.5 mph EV. Waldrep LHB split -1.39, HR risk -0.56. tough split lane (-1.39); pitcher suppresses HR (-0.56).""", blast="high"),
            row("Tyler Callihan", "L", "+775", 58, "", ["vs Waldrep"], """1 HR, 1 near-HR, 79.7 mph EV. Waldrep LHB split -1.39, HR risk -0.56. tough split lane (-1.39); pitcher suppresses HR (-0.56).""", blast="good"),
            row("Matt Olson", "L", "+360", 74, "⭐ 🌕 💣", ["vs Skenes"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.1 mph EV. Skenes LHB split +0.19, HR risk 0.07. park/weather net drag (-7%).""", blast="high"),
            row("Michael Harris II", "L", "+500", 62, "", ["vs Skenes"], """1 HR, 1 near-HR, 93.4 mph EV. Skenes LHB split +0.19, HR risk 0.07. park/weather net drag (-7%).""", blast="good"),
            row("Drake Baldwin", "L", "+557", 58, "", ["vs Skenes"], """0 HR, 90.4 mph EV. Skenes LHB split +0.19, HR risk 0.07. park/weather net drag (-7%); limited recent HR events."""),
        ],
    },
    {
        "title": "BOS @ CWS - Payton Tolle (L, BOS) vs Noah Schultz (L, CWS)",
        "description": "Tail key data: Park boost +3% (stadium +3%, weather +0%). Tolle (HR risk 0.41, vs LHB +0.50, vs RHB +0.27). Schultz (HR risk 0.74, vs LHB -1.04, vs RHB +1.06).",
        "rows": [
            row("Miguel Vargas", "R", "+355", 73, "⭐", ["vs Tolle"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.6 mph EV. Tolle RHB split +0.27, HR risk 0.41.""", blast="good"),
            row("Colson Montgomery", "L", "+331", 66, "", ["vs Tolle"], """1 HR, 1 near-HR, 81.9 mph EV. Tolle LHB split +0.50, HR risk 0.41. lighter EV form (81.9 mph).""", blast="good"),
            row("Randal Grichuk", "R", "+390", 58, "", ["vs Tolle"], """0 HR, 1 near-HR, 86.6 mph EV. Tolle RHB split +0.27, HR risk 0.41. limited recent HR events; lighter EV form (86.6 mph)."""),
            row("Wilyer Abreu", "L", "+480", 64, "", ["vs Schultz"], """1 HR, 2 near-HR, 88.8 mph EV. Schultz LHB split -1.04, HR risk 0.74. tough split lane (-1.04).""", blast="good"),
            row("Willson Contreras", "R", "+355", 73, "", ["vs Schultz"], """1 HR, 1 near-HR, 85.3 mph EV. Schultz RHB split +1.06, HR risk 0.74. lighter EV form (85.3 mph).""", blast="good"),
            row("Jarren Duran", "L", "+543", 58, "", ["vs Schultz"], """0 HR, 1 near-HR, 80.8 mph EV. Schultz LHB split -1.04, HR risk 0.74. tough split lane (-1.04); limited recent HR events."""),
        ],
    },
    {
        "title": "CHC @ BAL - Matthew Boyd (L, CHC) vs Shane Baz (R, BAL)",
        "description": "Tail key data: Park boost -6% (stadium -3%, weather -3%). Boyd (HR risk -0.00, vs LHB -1.15, vs RHB +0.44). Baz (HR risk -0.68, vs LHB -0.18, vs RHB -0.57).",
        "rows": [
            row("Pete Alonso", "R", "+340", 60, "💎", ["vs Boyd"], """Worst Pickz Hidden Gem. 0 HR, 94.7 mph EV. Boyd RHB split +0.44, HR risk -0.00. park/weather net drag (-6%); limited recent HR events.""", blast="good"),
            row("Taylor Ward", "R", "+480", 63, "", ["vs Boyd"], """1 HR, 1 near-HR, 92.6 mph EV. Boyd RHB split +0.44, HR risk -0.00. park/weather net drag (-6%).""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+317", 58, "⭐", ["vs Baz"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 83.8 mph EV. Baz LHB split -0.18, HR risk -0.68. slight split headwind (-0.18); pitcher suppresses HR (-0.68).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ MIN - Joey Cantillo (L, CLE) vs Taj Bradley (R, MIN)",
        "description": "Tail key data: Park boost +6% (stadium -7%, weather +13%). Cantillo (HR risk -0.07, vs LHB +0.15, vs RHB -0.14). Bradley (HR risk 0.81, vs LHB +1.48, vs RHB -0.53).",
        "rows": [
            row("Byron Buxton", "R", "+302", 78, "🌕 💣 💎", ["vs Cantillo"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 96.5 mph EV. Cantillo RHB split -0.14, HR risk -0.07. slight split headwind (-0.14); pitcher risk below avg (-0.07).""", blast="high"),
            row("Victor Caratini", "S", "+800", 60, "", ["vs Cantillo"], """1 HR, 1 near-HR, 89.5 mph EV. Cantillo RHB split -0.14, HR risk -0.07. slight split headwind (-0.14); pitcher risk below avg (-0.07).""", blast="good"),
            row("Josh Bell", "S", "+575", 58, "", ["vs Cantillo"], """0 HR, 1 near-HR, 87.8 mph EV. Cantillo RHB split -0.14, HR risk -0.07. slight split headwind (-0.14); pitcher risk below avg (-0.07)."""),
            row("Kyle Manzardo", "L", "+450", 78, "", ["vs Bradley"], """1 HR, 1 near-HR, 85.6 mph EV. Bradley LHB split +1.48, HR risk 0.81. park suppresses carry (-7%); lighter EV form (85.6 mph).""", blast="good"),
            row("Austin Hedges", "R", "N/A", 66, "💎", ["vs Bradley"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 88.8 mph EV. Bradley RHB split -0.53, HR risk 0.81. tough split lane (-0.53); park suppresses carry (-7%).""", blast="good"),
        ],
    },
    {
        "title": "COL @ LAD - Michael Lorenzen (R, COL) vs Justin Wrobleski (L, LAD)",
        "description": "Tail key data: Park boost +15% (stadium +17%, weather -3%). Lorenzen (HR risk -0.22, vs LHB +0.10, vs RHB -0.15). Wrobleski (HR risk -0.10, vs LHB +0.47, vs RHB -0.08).",
        "rows": [
            row("Mookie Betts", "R", "+446", 77, "🌕 💣", ["vs Lorenzen"], """2 HR, 3 near-HR, 93.9 mph EV. Lorenzen RHB split -0.15, HR risk -0.22. slight split headwind (-0.15); pitcher risk below avg (-0.22).""", blast="high"),
            row("Freddie Freeman", "L", "+340", 63, "", ["vs Lorenzen"], """1 HR, 1 near-HR, 92.4 mph EV. Lorenzen LHB split +0.10, HR risk -0.22. pitcher risk below avg (-0.22).""", blast="good"),
            row("Hunter Goodman", "R", "+265", 67, "🚀 ⭐", ["vs Wrobleski"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 102.9 mph EV. Wrobleski RHB split -0.08, HR risk -0.10. slight split headwind (-0.08); pitcher risk below avg (-0.10).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ WSH - Tatsuya Imai (R, HOU) vs Andrew Alvarez (L, WSH)",
        "description": "Tail key data: Park boost +10% (stadium +3%, weather +7%). Imai (HR risk 0.84, vs LHB +0.96, vs RHB -0.15). Alvarez (HR risk -1.82, vs LHB -0.90, vs RHB -1.15).",
        "rows": [
            row("Luis Garcia Jr.", "L", "N/A", 95, "🌕 💣", ["vs Imai"], """3 HR, 4 near-HR, 98.7 mph EV. Imai LHB split +0.96, HR risk 0.84.""", blast="high"),
            row("James Wood", "L", "+300", 92, "🌕 💣", ["vs Imai"], """2 HR, 2 near-HR, 98.4 mph EV. Imai LHB split +0.96, HR risk 0.84.""", blast="high"),
            row("CJ Abrams", "L", "+416", 82, "", ["vs Imai"], """1 HR, 3 near-HR, 86.9 mph EV. Imai LHB split +0.96, HR risk 0.84. lighter EV form (86.9 mph).""", blast="good"),
            row("Yordan Alvarez", "L", "+310", 58, "💎", ["vs Alvarez"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.1 mph EV. Alvarez LHB split -0.90, HR risk -1.82. tough split lane (-0.90); pitcher suppresses HR (-1.82).""", blast="good"),
        ],
    },
    {
        "title": "KC @ NYM - Seth Lugo 🧤 (R, KC) vs Kodai Senga (R, NYM)",
        "description": "Tail key data: Park boost -9% (stadium -1%, weather -8%). Lugo 🧤 (HR risk 1.27, vs LHB +0.62, vs RHB +1.34). Home starter risk unavailable.",
        "rows": [
            row("Juan Soto", "L", "+321", 92, "⭐ 🌕 💣", ["vs Lugo"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 93.4 mph EV. Lugo LHB split +0.62, HR risk 1.27. park/weather net drag (-9%).""", blast="high"),
            row("Jac Caglianone", "L", "+497", 58, "", ["vs Senga"], """1 HR, 1 near-HR, 86.2 mph EV. Senga split/risk data unavailable. limited split/risk sample; park/weather net drag (-9%).""", blast="good"),
            row("Carter Jensen", "L", "+470", 59, "", ["vs Senga"], """1 HR, 1 near-HR, 90.7 mph EV. Senga split/risk data unavailable. limited split/risk sample; park/weather net drag (-9%).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ TEX - Jose Soriano (R, LAA) vs Jacob deGrom (R, TEX)",
        "description": "Tail key data: Park boost -10% (stadium -10%, weather -1%). Soriano (HR risk 0.20, vs LHB +0.89, vs RHB -1.17). deGrom (HR risk -0.20, vs LHB -0.17, vs RHB +0.06).",
        "rows": [
            row("Jake Burger", "R", "+520", 58, "", ["vs Soriano"], """1 HR, 1 near-HR, 93.8 mph EV. Soriano RHB split -1.17, HR risk 0.20. tough split lane (-1.17); park/weather net drag (-10%).""", blast="good"),
            row("Brandon Nimmo", "L", "+600", 68, "", ["vs Soriano"], """0 HR, 2 near-HR, 95.5 mph EV. Soriano LHB split +0.89, HR risk 0.20. park/weather net drag (-10%).""", blast="good"),
            row("Joc Pederson", "L", "+484", 88, "🌕 💣", ["vs Soriano"], """3 HR, 3 near-HR, 96.3 mph EV. Soriano LHB split +0.89, HR risk 0.20. park/weather net drag (-10%).""", blast="high"),
            row("Josh Smith", "L", "N/A", 62, "", ["vs Soriano"], """1 HR, 2 near-HR, 85.8 mph EV. Soriano LHB split +0.89, HR risk 0.20. park/weather net drag (-10%); lighter EV form (85.8 mph).""", blast="good"),
            row("Jo Adell", "R", "+600", 58, "", ["vs deGrom"], """1 HR, 1 near-HR, 91.1 mph EV. deGrom RHB split +0.06, HR risk -0.20. pitcher risk below avg (-0.20); park/weather net drag (-10%).""", blast="good"),
            row("Zach Neto", "R", "+445", 58, "", ["vs deGrom"], """1 HR, 2 near-HR, 88.1 mph EV. deGrom RHB split +0.06, HR risk -0.20. pitcher risk below avg (-0.20); park/weather net drag (-10%).""", blast="good"),
            row("Josh Lowe", "L", "+500", 58, "", ["vs deGrom"], """0 HR, 1 near-HR, 91.7 mph EV. deGrom LHB split -0.17, HR risk -0.20. slight split headwind (-0.17); pitcher risk below avg (-0.20)."""),
        ],
    },
    {
        "title": "MIL @ STL - Robert Gasser (L, MIL) vs Hunter Dobbins 🧤 (R, STL)",
        "description": "Tail key data: Park boost -16% (stadium -10%, weather -5%). Gasser (HR risk 0.74, vs LHB +0.46, vs RHB +0.28). Dobbins 🧤 (HR risk 1.07, vs LHB +0.55, vs RHB +0.88).",
        "rows": [
            row("Lars Nootbaar", "L", "+600", 58, "", ["vs Gasser"], """0 HR, 87.4 mph EV. Gasser LHB split +0.46, HR risk 0.74. park/weather net drag (-16%); limited recent HR events."""),
            row("JJ Wetherholt", "L", "+680", 74, "", ["vs Gasser"], """1 HR, 1 near-HR, 97.9 mph EV. Gasser LHB split +0.46, HR risk 0.74. park/weather net drag (-16%).""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 72, "", ["vs Gasser"], """1 HR, 1 near-HR, 95.9 mph EV. Gasser RHB split +0.28, HR risk 0.74. park/weather net drag (-16%).""", blast="good"),
            row("Jordan Walker", "R", "+420", 58, "", ["vs Gasser"], """0 HR, 88.8 mph EV. Gasser RHB split +0.28, HR risk 0.74. park/weather net drag (-16%); limited recent HR events."""),
            row("Jake Bauers", "L", "+470", 63, "", ["vs Dobbins"], """0 HR, 88.7 mph EV. Dobbins LHB split +0.55, HR risk 1.07. park/weather net drag (-16%); limited recent HR events."""),
            row("Jackson Chourio", "R", "+470", 90, "🌕 💣", ["vs Dobbins"], """2 HR, 3 near-HR, 90.3 mph EV. Dobbins RHB split +0.88, HR risk 1.07. park/weather net drag (-16%).""", blast="high"),
            row("Garrett Mitchell", "L", "+560", 81, "", ["vs Dobbins"], """1 HR, 2 near-HR, 98.1 mph EV. Dobbins LHB split +0.55, HR risk 1.07. park/weather net drag (-16%).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ TB - Will Warren (R, NYY) vs Ian Seymour (L, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +0%). Warren (HR risk -0.23, vs LHB -0.22, vs RHB +0.05). Seymour (HR risk 0.02, vs LHB +1.59, vs RHB -1.03).",
        "rows": [
            row("Junior Caminero", "R", "+310", 76, "🌕 💣", ["vs Warren"], """4 HR, 4 near-HR, 92.8 mph EV. Warren RHB split +0.05, HR risk -0.23. pitcher risk below avg (-0.23).""", blast="high"),
            row("Jonathan Aranda", "L", "+491", 58, "", ["vs Warren"], """1 HR, 2 near-HR, 88.3 mph EV. Warren LHB split -0.22, HR risk -0.23. slight split headwind (-0.22); pitcher risk below avg (-0.23).""", blast="good"),
            row("Ben Rice", "L", "+395", 74, "⭐", ["vs Seymour"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.9 mph EV. Seymour LHB split +1.59, HR risk 0.02.""", blast="good"),
            row("Trent Grisham", "L", "N/A", 62, "💎", ["vs Seymour"], """Worst Pickz Hidden Gem. 0 HR, 91.1 mph EV. Seymour LHB split +1.59, HR risk 0.02. limited recent HR events."""),
            row("Max Schuemann", "R", "N/A", 58, "", ["vs Seymour"], """0 HR, 91.5 mph EV. Seymour RHB split -1.03, HR risk 0.02. tough split lane (-1.03); limited recent HR events."""),
            row("Jazz Chisholm Jr.", "L", "+475", 61, "", ["vs Seymour"], """0 HR, 89.6 mph EV. Seymour LHB split +1.59, HR risk 0.02. limited recent HR events."""),
        ],
    },
    {
        "title": "PHI @ CIN - Zack Wheeler (R, PHI) vs Andrew Abbott (L, CIN)",
        "description": "Tail key data: Park boost +18% (stadium +14%, weather +4%). Wheeler (HR risk -0.66, vs LHB -0.11, vs RHB -0.93). Abbott (HR risk 0.44, vs LHB -0.48, vs RHB +0.56).",
        "rows": [
            row("Sal Stewart", "R", "+360", 74, "🌕 💣", ["vs Wheeler"], """3 HR, 4 near-HR, 94.0 mph EV. Wheeler RHB split -0.93, HR risk -0.66. tough split lane (-0.93); pitcher suppresses HR (-0.66).""", blast="high"),
            row("Matt McLain", "R", "+780", 58, "", ["vs Wheeler"], """0 HR, 95.3 mph EV. Wheeler RHB split -0.93, HR risk -0.66. tough split lane (-0.93); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Trea Turner", "R", "+430", 78, "", ["vs Abbott"], """0 HR, 2 near-HR, 95.8 mph EV. Abbott RHB split +0.56, HR risk 0.44.""", blast="good"),
            row("Alec Bohm", "R", "+473", 67, "", ["vs Abbott"], """0 HR, 1 near-HR, 91.0 mph EV. Abbott RHB split +0.56, HR risk 0.44. limited recent HR events."""),
        ],
    },
    {
        "title": "SEA @ MIA - Bryan Woo (R, SEA) vs Max Meyer (R, MIA)",
        "description": "Tail key data: Park boost -12% (stadium -12%, weather +0%). Woo (HR risk -0.40, vs LHB +0.07, vs RHB -0.56). Meyer (HR risk 0.13, vs LHB -0.14, vs RHB +0.42).",
        "rows": [
            row("Kyle Stowers", "L", "+360", 68, "⭐ 🌕 💣", ["vs Woo"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.8 mph EV. Woo LHB split +0.07, HR risk -0.40. pitcher suppresses HR (-0.40); park/weather net drag (-12%).""", blast="high"),
            row("Otto Lopez", "R", "+870", 58, "🌕 💣 💎", ["vs Woo"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 84.3 mph EV. Woo RHB split -0.56, HR risk -0.40. tough split lane (-0.56); pitcher suppresses HR (-0.40).""", blast="high"),
            row("Owen Caissie", "L", "+525", 58, "💎", ["vs Woo"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 94.4 mph EV. Woo LHB split +0.07, HR risk -0.40. pitcher suppresses HR (-0.40); park/weather net drag (-12%).""", blast="good"),
            row("Joe Mack", "L", "+650", 74, "⭐ 🌕 💣", ["vs Woo"], """Worst Pickz Favorite. 4 HR, 4 near-HR, 93.6 mph EV. Woo LHB split +0.07, HR risk -0.40. pitcher suppresses HR (-0.40); park/weather net drag (-12%).""", blast="high"),
            row("Cal Raleigh", "S", "+340", 64, "", ["vs Meyer"], """1 HR, 1 near-HR, 94.0 mph EV. Meyer RHB split +0.42, HR risk 0.13. park/weather net drag (-12%).""", blast="good"),
            row("Randy Arozarena", "R", "+600", 72, "🌕 💣", ["vs Meyer"], """2 HR, 3 near-HR, 87.8 mph EV. Meyer RHB split +0.42, HR risk 0.13. park/weather net drag (-12%); lighter EV form (87.8 mph).""", blast="high"),
            row("Josh Naylor", "L", "+630", 58, "", ["vs Meyer"], """0 HR, 87.7 mph EV. Meyer LHB split -0.14, HR risk 0.13. slight split headwind (-0.14); park/weather net drag (-12%)."""),
        ],
    },
    {
        "title": "TOR @ SF - Patrick Corbin (L, TOR) vs Trevor McDonald (R, SF)",
        "description": "Tail key data: Park boost -18% (stadium -16%, weather -2%). Corbin (HR risk 0.57, vs LHB -0.45, vs RHB +0.74). McDonald (HR risk -1.36, vs LHB -0.37, vs RHB -1.53).",
        "rows": [
            row("Heliot Ramos", "R", "+550", 72, "⭐", ["vs Corbin"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.8 mph EV. Corbin RHB split +0.74, HR risk 0.57. park/weather net drag (-18%).""", blast="good"),
            row("Casey Schmitt", "R", "+569", 67, "", ["vs Corbin"], """0 HR, 1 near-HR, 93.2 mph EV. Corbin RHB split +0.74, HR risk 0.57. park/weather net drag (-18%); limited recent HR events.""", blast="good"),
            row("Bryce Eldridge", "L", "+860", 58, "", ["vs Corbin"], """0 HR, 2 near-HR, 90.2 mph EV. Corbin LHB split -0.45, HR risk 0.57. tough split lane (-0.45); park/weather net drag (-18%).""", blast="good"),
            row("Kazuma Okamoto", "R", "+600", 58, "🌕 💣", ["vs McDonald"], """2 HR, 2 near-HR, 87.6 mph EV. McDonald RHB split -1.53, HR risk -1.36. tough split lane (-1.53); pitcher suppresses HR (-1.36).""", blast="high"),
            row("Brandon Valenzuela", "S", "N/A", 58, "🌕 💣", ["vs McDonald"], """2 HR, 2 near-HR, 91.7 mph EV. McDonald RHB split -1.53, HR risk -1.36. tough split lane (-1.53); pitcher suppresses HR (-1.36).""", blast="high"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-07")

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

    out = ROOT / '_games-0707.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
