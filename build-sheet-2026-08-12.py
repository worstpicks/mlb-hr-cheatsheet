#!/usr/bin/env python3
"""Generate games[] block for 2026-08-12 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Austin Riley (R)",
    "Brandon Lowe (L)",
    "Cal Raleigh (S)",
    "Carter Jensen (L)",
    "Griffin Conine (L)",
    "Gunnar Henderson (L)",
    "Jac Caglianone (L)",
    "Jackson Merrill (L)",
    "Jarred Kelenic (L)",
    "Jarren Duran (L)",
    "Jo Adell (R)",
    "Kazuma Okamoto (R)",
    "Kody Clemens (L)",
    "Kyle Schwarber (L)",
    "Luis Garcia Jr. (L)",
    "Matt Olson (L)",
    "Mickey Moniak (L)",
    "Moises Ballesteros (L)",
    "Munetaka Murakami (L)",
    "Owen Caissie (L)",
    "Pete Alonso (R)",
    "Teoscar Hernandez (R)",
    "Willy Adames (R)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Brett Baty (L)",
    "Elly De La Cruz (S)",
    "Eugenio Suarez (R)",
    "James Outman (L)",
    "Jonny DeLuca (R)",
    "Jordan Walker (R)",
    "Lawrence Butler (L)",
    "Manny Machado (R)",
    "Nelson Velazquez (R)",
    "Randy Arozarena (R)",
    "Ty France (R)",
    "Victor Mesa Jr. (L)",
}

PLAYER_TEAMS = {
    "Andrew Vaughn (R)": "MIL",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Brandon Lowe (L)": "PIT",
    "Brett Baty (L)": "NYM",
    "Bryce Harper (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Carter Jensen (L)": "KC",
    "Ceddanne Rafaela (R)": "BOS",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Daylen Lile (L)": "WSH",
    "Dylan Crews (R)": "WSH",
    "Eduardo Valencia (R)": "DET",
    "Elias Diaz (R)": "TEX",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Freddie Freeman (L)": "LAD",
    "Griffin Conine (L)": "MIA",
    "Gunnar Henderson (L)": "BAL",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Ivan Herrera (R)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "James Outman (L)": "DET",
    "Jarred Kelenic (L)": "TEX",
    "Jarren Duran (L)": "BOS",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "CLE",
    "John Rave (L)": "KC",
    "Jonny DeLuca (R)": "TB",
    "Jordan Walker (R)": "STL",
    "Josh Naylor (L)": "SEA",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Lars Nootbaar (L)": "ARI",
    "Lawrence Butler (L)": "ATH",
    "Luis Garcia Jr. (L)": "NYY",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Michael Massey (L)": "KC",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Moises Ballesteros (L)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Nolan Schanuel (L)": "LAA",
    "Owen Caissie (L)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randy Arozarena (R)": "SEA",
    "Ronald Acuna Jr. (R)": "ATL",
    "Spencer Jones (L)": "NYY",
    "Taylor Trammell (L)": "HOU",
    "Teoscar Hernandez (R)": "LAD",
    "Ty France (R)": "SD",
    "Tyler Soderstrom (L)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "Victor Mesa Jr. (L)": "TB",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Willi Castro (S)": "COL",
    "William Contreras (R)": "MIL",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("CIN @ CWS", "Castillo"),
    ("COL @ ARI", "Feltner"),
    ("TB @ ATH", "Perkins"),
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
        "title": "BAL @ MIN - Shane Baz (R, BAL) vs Zebby Matthews (R, MIN)",
        "description": "Tail key data: Park boost -7% (stadium -7%, weather +0%). Baz (HR risk -0.71, vs LHB -0.47, vs RHB -0.71). Matthews (HR risk 0.78, vs LHB +0.13, vs RHB +0.85).",
        "rows": [
            row("Kody Clemens", "L", "+486", 58, "⭐", ["vs Baz"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.2 mph EV. Baz LHB split -0.47, HR risk -0.71. tough split lane (-0.47); pitcher suppresses HR (-0.71).""", blast="good"),
            row("Pete Alonso", "R", "+340", 91, "⭐ 🌕 💣", ["vs Matthews"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.3 mph EV. Matthews RHB split +0.85, HR risk 0.78. park/weather net drag (-7%).""", blast="high"),
            row("Gunnar Henderson", "L", "+425", 75, "⭐", ["vs Matthews"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.1 mph EV. Matthews LHB split +0.13, HR risk 0.78. park/weather net drag (-7%).""", blast="good"),
            row("Colton Cowser", "L", "+610", 72, "", ["vs Matthews"], """1 HR, 2 near-HR, 92.6 mph EV. Matthews LHB split +0.13, HR risk 0.78. park/weather net drag (-7%).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ TOR - Ranger Suarez (L, BOS) vs Jose Soriano (R, TOR)",
        "description": "Tail key data: Park boost +13% (stadium +7%, weather +6%). Suarez (HR risk -0.74, vs LHB +0.14, vs RHB -0.74). Soriano (HR risk -0.97, vs LHB -0.62, vs RHB -0.88).",
        "rows": [
            row("Kazuma Okamoto", "R", "+440", 58, "⭐", ["vs Suarez"], """Worst Pickz Favorite. 0 HR, 91.8 mph EV. Suarez RHB split -0.74, HR risk -0.74. tough split lane (-0.74); pitcher suppresses HR (-0.74)."""),
            row("Vladimir Guerrero Jr.", "R", "+600", 58, "", ["vs Suarez"], """0 HR, 92.8 mph EV. Suarez RHB split -0.74, HR risk -0.74. tough split lane (-0.74); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Jarren Duran", "L", "+750", 58, "⭐", ["vs Soriano"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.0 mph EV. Soriano LHB split -0.62, HR risk -0.97. tough split lane (-0.62); pitcher suppresses HR (-0.97).""", blast="good"),
            row("Wilyer Abreu", "L", "+461", 58, "", ["vs Soriano"], """0 HR, 91.9 mph EV. Soriano LHB split -0.62, HR risk -0.97. tough split lane (-0.62); pitcher suppresses HR (-0.97)."""),
            row("Ceddanne Rafaela", "R", "+870", 58, "", ["vs Soriano"], """0 HR, 1 near-HR, 89.3 mph EV. Soriano RHB split -0.88, HR risk -0.97. tough split lane (-0.88); pitcher suppresses HR (-0.97)."""),
        ],
    },
    {
        "title": "CHC @ WSH - David Peterson (L, CHC) vs Jackson Kent (L, WSH)",
        "description": "Tail key data: Park boost data unavailable. Peterson (HR risk -0.42, vs LHB +0.03, vs RHB -0.41). Kent (no MLB HR data yet).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+331", 58, "", ["vs Kent"], """0 HR, 2 near-HR, 91.9 mph EV. Kent has no MLB HR data yet. limited split/risk sample.""", blast="good"),
            row("Ian Happ", "S", "+420", 68, "🌕 💣", ["vs Kent"], """2 HR, 2 near-HR, 90.3 mph EV. Kent has no MLB HR data yet. limited split/risk sample.""", blast="high"),
            row("Dylan Crews", "R", "+435", 58, "", ["vs Peterson"], """0 HR, 93.4 mph EV. Peterson RHB split -0.41, HR risk -0.42. tough split lane (-0.41); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Daylen Lile", "L", "+790", 58, "", ["vs Peterson"], """0 HR, 93.4 mph EV. Peterson LHB split +0.03, HR risk -0.42. pitcher suppresses HR (-0.42); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CIN @ CWS - Rhett Lowder (R, CIN) vs Luis Castillo 🧤 (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Lowder (HR risk -0.11, vs LHB +0.52, vs RHB -1.02). Castillo 🧤 (HR risk 1.04, vs LHB +1.31, vs RHB -0.04).",
        "rows": [
            row("Munetaka Murakami", "L", "+259", 77, "⭐ 🌕 💣", ["vs Lowder"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.2 mph EV. Lowder LHB split +0.52, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="high"),
            row("Miguel Vargas", "R", "+360", 62, "", ["vs Lowder"], """1 HR, 3 near-HR, 93.0 mph EV. Lowder RHB split -1.02, HR risk -0.11. tough split lane (-1.02); pitcher risk below avg (-0.11).""", blast="good"),
            row("Elly De La Cruz", "S", "+340", 92, "🌕 💣 💎", ["vs Castillo"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 92.7 mph EV. Castillo SHB→LHB split +1.31, HR risk 1.04.""", blast="high"),
            row("Tyler Stephenson", "R", "+486", 79, "", ["vs Castillo"], """1 HR, 1 near-HR, 96.5 mph EV. Castillo RHB split -0.04, HR risk 1.04. slight split headwind (-0.04).""", blast="good"),
            row("Eugenio Suarez", "R", "+440", 91, "🌕 💣 💎", ["vs Castillo"], """Worst Pickz Hidden Gem. 3 HR, 4 near-HR, 91.6 mph EV. Castillo RHB split -0.04, HR risk 1.04. slight split headwind (-0.04).""", blast="high"),
        ],
    },
    {
        "title": "CLE @ DET - Foster Griffin (L, CLE) vs Framber Valdez (L, DET)",
        "description": "Tail key data: Park boost +0% (stadium -8%, weather +8%). Griffin (HR risk 0.01, vs LHB +1.11, vs RHB -0.24). Valdez (HR risk -0.79, vs LHB -0.86, vs RHB -0.44).",
        "rows": [
            row("James Outman", "L", "N/A", 71, "💎", ["vs Griffin"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.6 mph EV. Griffin LHB split +1.11, HR risk 0.01. park suppresses carry (-8%).""", blast="good"),
            row("Eduardo Valencia", "R", "+760", 60, "", ["vs Griffin"], """1 HR, 1 near-HR, 93.1 mph EV. Griffin RHB split -0.24, HR risk 0.01. slight split headwind (-0.24); park suppresses carry (-8%).""", blast="good"),
            row("Jo Adell", "R", "+521", 71, "⭐ 🌕 💣", ["vs Valdez"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 97.1 mph EV. Valdez RHB split -0.44, HR risk -0.79. tough split lane (-0.44); pitcher suppresses HR (-0.79).""", blast="high"),
        ],
    },
    {
        "title": "COL @ ARI - Ryan Feltner 🧤 (R, COL) vs Merrill Kelly (R, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Feltner 🧤 (HR risk 1.85, vs LHB +0.68, vs RHB +2.05). Kelly (HR risk 0.37, vs LHB +0.48, vs RHB -0.09).",
        "rows": [
            row("Corbin Carroll", "L", "+400", 83, "", ["vs Feltner"], """1 HR, 1 near-HR, 93.2 mph EV. Feltner LHB split +0.68, HR risk 1.85. park/weather net drag (-8%).""", blast="good"),
            row("Lars Nootbaar", "L", "+700", 73, "", ["vs Feltner"], """0 HR, 1 near-HR, 91.5 mph EV. Feltner LHB split +0.68, HR risk 1.85. park/weather net drag (-8%); limited recent HR events."""),
            row("Hunter Goodman", "R", "+402", 81, "🌕 💣", ["vs Kelly"], """2 HR, 4 near-HR, 98.2 mph EV. Kelly RHB split -0.09, HR risk 0.37. slight split headwind (-0.09); park/weather net drag (-8%).""", blast="high"),
            row("Willi Castro", "S", "+720", 70, "", ["vs Kelly"], """1 HR, 3 near-HR, 90.5 mph EV. Kelly SHB→LHB split +0.48, HR risk 0.37. park/weather net drag (-8%).""", blast="good"),
            row("Mickey Moniak", "L", "+485", 65, "⭐", ["vs Kelly"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.4 mph EV. Kelly LHB split +0.48, HR risk 0.37. park/weather net drag (-8%).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ SF - Bryan King (L, HOU) vs Adrian Houser (R, SF)",
        "description": "Tail key data: Park boost -10% (stadium -13%, weather +3%). King (HR risk -0.04, vs LHB -0.78, vs RHB +0.40). Houser (HR risk 0.34, vs LHB +1.12, vs RHB -0.67).",
        "rows": [
            row("Willy Adames", "R", "+486", 82, "⭐ 🌕 💣", ["vs King"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 96.6 mph EV. King RHB split +0.40, HR risk -0.04. pitcher risk below avg (-0.04); park/weather net drag (-10%).""", blast="high"),
            row("Rafael Devers", "L", "+400", 58, "", ["vs King"], """0 HR, 90.1 mph EV. King LHB split -0.78, HR risk -0.04. tough split lane (-0.78); pitcher risk below avg (-0.04)."""),
            row("Yordan Alvarez", "L", "+333", 69, "🚀 ⭐", ["vs Houser"], """Worst Pickz Favorite. 0 HR, 100.7 mph EV. Houser LHB split +1.12, HR risk 0.34. park/weather net drag (-10%); limited recent HR events.""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 58, "💎", ["vs Houser"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.4 mph EV. Houser RHB split -0.67, HR risk 0.34. tough split lane (-0.67); park/weather net drag (-10%).""", blast="good"),
            row("Taylor Trammell", "L", "+600", 71, "", ["vs Houser"], """1 HR, 2 near-HR, 91.9 mph EV. Houser LHB split +1.12, HR risk 0.34. park/weather net drag (-10%).""", blast="good"),
        ],
    },
    {
        "title": "KC @ LAD - Daniel Lynch IV (L, KC) vs Eric Lauer (L, LAD)",
        "description": "Tail key data: Park boost +14% (stadium +18%, weather -4%). Lynch IV (HR risk -1.23, vs LHB -1.31, vs RHB -0.40). Lauer (HR risk 0.91, vs LHB +1.09, vs RHB +0.59).",
        "rows": [
            row("Teoscar Hernandez", "R", "+400", 69, "⭐ 🌕 💣", ["vs Lynch IV"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 95.8 mph EV. Lynch IV RHB split -0.40, HR risk -1.23. tough split lane (-0.40); pitcher suppresses HR (-1.23).""", blast="high"),
            row("Freddie Freeman", "L", "+499", 58, "", ["vs Lynch IV"], """0 HR, 1 near-HR, 89.7 mph EV. Lynch IV LHB split -1.31, HR risk -1.23. tough split lane (-1.31); pitcher suppresses HR (-1.23)."""),
            row("Carter Jensen", "L", "+531", 88, "⭐ 🌕 💣", ["vs Lauer"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.9 mph EV. Lauer LHB split +1.09, HR risk 0.91. weather carry headwind (-4%).""", blast="good"),
            row("John Rave", "L", "+468", 83, "", ["vs Lauer"], """0 HR, 2 near-HR, 93.9 mph EV. Lauer LHB split +1.09, HR risk 0.91. weather carry headwind (-4%).""", blast="good"),
            row("Michael Massey", "L", "+520", 92, "🌕 💣", ["vs Lauer"], """2 HR, 2 near-HR, 93.7 mph EV. Lauer LHB split +1.09, HR risk 0.91. weather carry headwind (-4%).""", blast="high"),
            row("Jac Caglianone", "L", "+356", 84, "⭐", ["vs Lauer"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.9 mph EV. Lauer LHB split +1.09, HR risk 0.91. weather carry headwind (-4%).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ SD - Dustin May (R, MIL) vs Robbie Ray (L, SD)",
        "description": "Tail key data: Park boost +5% (stadium -5%, weather +10%). May (HR risk -0.49, vs LHB -0.39, vs RHB -0.34). Ray (HR risk -0.58, vs LHB -1.11, vs RHB -0.07).",
        "rows": [
            row("Jackson Merrill", "L", "+530", 76, "⭐ 🌕 💣", ["vs May"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 99.5 mph EV. May LHB split -0.39, HR risk -0.49. slight split headwind (-0.39); pitcher suppresses HR (-0.49).""", blast="high"),
            row("Ty France", "R", "+550", 58, "💎", ["vs May"], """Worst Pickz Hidden Gem. 0 HR, 90.5 mph EV. May RHB split -0.34, HR risk -0.49. slight split headwind (-0.34); pitcher suppresses HR (-0.49)."""),
            row("Manny Machado", "R", "+477", 58, "💎", ["vs May"], """Worst Pickz Hidden Gem. 0 HR, 93.8 mph EV. May RHB split -0.34, HR risk -0.49. slight split headwind (-0.34); pitcher suppresses HR (-0.49).""", blast="good"),
            row("Jake Bauers", "L", "+476", 58, "", ["vs Ray"], """1 HR, 1 near-HR, 93.3 mph EV. Ray LHB split -1.11, HR risk -0.58. tough split lane (-1.11); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Jackson Chourio", "R", "+401", 61, "", ["vs Ray"], """1 HR, 2 near-HR, 96.8 mph EV. Ray RHB split -0.07, HR risk -0.58. slight split headwind (-0.07); pitcher suppresses HR (-0.58).""", blast="good"),
            row("William Contreras", "R", "+453", 58, "", ["vs Ray"], """0 HR, 85.9 mph EV. Ray RHB split -0.07, HR risk -0.58. slight split headwind (-0.07); pitcher suppresses HR (-0.58)."""),
            row("Andrew Vaughn", "R", "+563", 58, "", ["vs Ray"], """1 HR, 2 near-HR, 90.3 mph EV. Ray RHB split -0.07, HR risk -0.58. slight split headwind (-0.07); pitcher suppresses HR (-0.58).""", blast="good"),
        ],
    },
    {
        "title": "NYM @ ATL - Zach Thornton (L, NYM) vs Tyler Mahle (R, ATL)",
        "description": "Tail key data: Park boost +7% (stadium -3%, weather +10%). Thornton (HR risk -0.50, vs LHB -0.37, vs RHB -0.24). Mahle (HR risk -0.53, vs LHB -0.68, vs RHB -0.09).",
        "rows": [
            row("Matt Olson", "L", "+285", 74, "⭐ 🌕 💣", ["vs Thornton"], """Worst Pickz Favorite. 3 HR, 5 near-HR, 93.6 mph EV. Thornton LHB split -0.37, HR risk -0.50. slight split headwind (-0.37); pitcher suppresses HR (-0.50).""", blast="high"),
            row("Austin Riley", "R", "+453", 58, "⭐", ["vs Thornton"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.3 mph EV. Thornton RHB split -0.24, HR risk -0.50. slight split headwind (-0.24); pitcher suppresses HR (-0.50).""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+400", 63, "🌕 💣", ["vs Thornton"], """2 HR, 2 near-HR, 89.7 mph EV. Thornton RHB split -0.24, HR risk -0.50. slight split headwind (-0.24); pitcher suppresses HR (-0.50).""", blast="high"),
            row("Francisco Alvarez", "R", "+448", 72, "🌕 💣", ["vs Mahle"], """2 HR, 3 near-HR, 93.5 mph EV. Mahle RHB split -0.09, HR risk -0.53. slight split headwind (-0.09); pitcher suppresses HR (-0.53).""", blast="high"),
            row("Francisco Lindor", "S", "+440", 58, "", ["vs Mahle"], """1 HR, 2 near-HR, 89.5 mph EV. Mahle SHB→RHB split -0.09, HR risk -0.53. slight split headwind (-0.09); pitcher suppresses HR (-0.53).""", blast="good"),
            row("Brett Baty", "L", "+600", 58, "💎", ["vs Mahle"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.3 mph EV. Mahle LHB split -0.68, HR risk -0.53. tough split lane (-0.68); pitcher suppresses HR (-0.53).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ STL - Zack Wheeler (R, PHI) vs Kyle Leahy (R, STL)",
        "description": "Tail key data: Park boost +3% (stadium -12%, weather +14%). Wheeler (HR risk -0.06, vs LHB +0.30, vs RHB -0.63). Leahy (HR risk 0.13, vs LHB +0.03, vs RHB +0.07).",
        "rows": [
            row("Jimmy Crooks", "L", "+760", 62, "", ["vs Wheeler"], """1 HR, 1 near-HR, 91.1 mph EV. Wheeler LHB split +0.30, HR risk -0.06. pitcher risk below avg (-0.06); park suppresses carry (-12%).""", blast="good"),
            row("Jordan Walker", "R", "+540", 58, "💎", ["vs Wheeler"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 87.7 mph EV. Wheeler RHB split -0.63, HR risk -0.06. tough split lane (-0.63); pitcher risk below avg (-0.06)."""),
            row("Ivan Herrera", "R", "+920", 58, "", ["vs Wheeler"], """0 HR, 1 near-HR, 99.6 mph EV. Wheeler RHB split -0.63, HR risk -0.06. tough split lane (-0.63); pitcher risk below avg (-0.06).""", blast="good"),
            row("Kyle Schwarber", "L", "+269", 62, "⭐", ["vs Leahy"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 89.4 mph EV. Leahy LHB split +0.03, HR risk 0.13. park suppresses carry (-12%).""", blast="good"),
            row("Bryce Harper", "L", "+446", 62, "", ["vs Leahy"], """1 HR, 2 near-HR, 89.7 mph EV. Leahy LHB split +0.03, HR risk 0.13. park suppresses carry (-12%).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ MIA - Carmen Mlodzinski (R, PIT) vs Janson Junk (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -13%, weather +0%). Mlodzinski (HR risk 0.09, vs LHB -0.11, vs RHB +0.03). Junk (HR risk 0.56, vs LHB +0.08, vs RHB +0.58).",
        "rows": [
            row("Griffin Conine", "L", "+453", 77, "🚀 ⭐ 🌕 💣", ["vs Mlodzinski"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 100.0 mph EV. Mlodzinski LHB split -0.11, HR risk 0.09. slight split headwind (-0.11); park/weather net drag (-13%).""", blast="high"),
            row("Owen Caissie", "L", "+675", 79, "⭐ 🌕 💣", ["vs Mlodzinski"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 98.1 mph EV. Mlodzinski LHB split -0.11, HR risk 0.09. slight split headwind (-0.11); park/weather net drag (-13%).""", blast="high"),
            row("Brandon Lowe", "L", "+340", 69, "⭐", ["vs Junk"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.0 mph EV. Junk LHB split +0.08, HR risk 0.56. park/weather net drag (-13%).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+467", 58, "", ["vs Junk"], """0 HR, 1 near-HR, 84.7 mph EV. Junk RHB split +0.58, HR risk 0.56. park/weather net drag (-13%); limited recent HR events."""),
        ],
    },
    {
        "title": "SEA @ NYY - Bryce Miller (R, SEA) vs Will Warren (R, NYY)",
        "description": "Tail key data: Park boost +14% (stadium +6%, weather +8%). Miller (HR risk 0.45, vs LHB -0.05, vs RHB +0.74). Warren (HR risk 0.16, vs LHB +0.30, vs RHB -0.17).",
        "rows": [
            row("Luis Garcia Jr.", "L", "+372", 61, "⭐", ["vs Miller"], """Worst Pickz Favorite. 0 HR, 91.4 mph EV. Miller LHB split -0.05, HR risk 0.45. slight split headwind (-0.05); limited recent HR events."""),
            row("Spencer Jones", "L", "+456", 59, "", ["vs Miller"], """0 HR, 1 near-HR, 88.0 mph EV. Miller LHB split -0.05, HR risk 0.45. slight split headwind (-0.05); limited recent HR events."""),
            row("Ben Rice", "L", "+271", 67, "", ["vs Miller"], """0 HR, 94.2 mph EV. Miller LHB split -0.05, HR risk 0.45. slight split headwind (-0.05); limited recent HR events.""", blast="good"),
            row("Josh Naylor", "L", "+540", 66, "", ["vs Warren"], """0 HR, 95.9 mph EV. Warren LHB split +0.30, HR risk 0.16. limited recent HR events.""", blast="good"),
            row("Cal Raleigh", "S", "+280", 74, "⭐", ["vs Warren"], """Worst Pickz Favorite. 0 HR, 3 near-HR, 95.8 mph EV. Warren SHB→LHB split +0.30, HR risk 0.16.""", blast="good"),
            row("Julio Rodriguez", "R", "+452", 64, "", ["vs Warren"], """1 HR, 1 near-HR, 92.1 mph EV. Warren RHB split -0.17, HR risk 0.16. slight split headwind (-0.17).""", blast="good"),
            row("Randy Arozarena", "R", "+510", 61, "💎", ["vs Warren"], """Worst Pickz Hidden Gem. 0 HR, 94.5 mph EV. Warren RHB split -0.17, HR risk 0.16. slight split headwind (-0.17); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TB @ ATH - Drew Rasmussen (R, TB) vs Jack Perkins 🧤 (R, ATH)",
        "description": "Tail key data: Park boost +25% (stadium +26%, weather -1%). Rasmussen (HR risk -0.70, vs LHB -0.58, vs RHB -0.41). Perkins 🧤 (HR risk 1.36, vs LHB +1.50, vs RHB +0.46).",
        "rows": [
            row("Lawrence Butler", "L", "+520", 69, "🌕 💣 💎", ["vs Rasmussen"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.1 mph EV. Rasmussen LHB split -0.58, HR risk -0.70. tough split lane (-0.58); pitcher suppresses HR (-0.70).""", blast="high"),
            row("Tyler Soderstrom", "L", "+440", 58, "", ["vs Rasmussen"], """0 HR, 1 near-HR, 96.4 mph EV. Rasmussen LHB split -0.58, HR risk -0.70. tough split lane (-0.58); pitcher suppresses HR (-0.70).""", blast="good"),
            row("Zack Gelof", "R", "+750", 58, "", ["vs Rasmussen"], """1 HR, 2 near-HR, 87.0 mph EV. Rasmussen RHB split -0.41, HR risk -0.70. tough split lane (-0.41); pitcher suppresses HR (-0.70).""", blast="good"),
            row("Yandy Diaz", "R", "+450", 91, "🌕 💣", ["vs Perkins"], """1 HR, 1 near-HR, 98.5 mph EV. Perkins RHB split +0.46, HR risk 1.36.""", blast="good"),
            row("Jonny DeLuca", "R", "N/A", 97, "🌕 💣 💎", ["vs Perkins"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 93.5 mph EV. Perkins RHB split +0.46, HR risk 1.36.""", blast="high"),
            row("Junior Caminero", "R", "+214", 90, "🌕 💣", ["vs Perkins"], """1 HR, 2 near-HR, 94.0 mph EV. Perkins RHB split +0.46, HR risk 1.36.""", blast="good"),
            row("Victor Mesa Jr.", "L", "+430", 94, "🌕 💣 💎", ["vs Perkins"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 84.7 mph EV. Perkins LHB split +1.50, HR risk 1.36. lighter EV form (84.7 mph).""", blast="high"),
        ],
    },
    {
        "title": "TEX @ LAA - Cal Quantrill (R, TEX) vs George Klassen (R, LAA)",
        "description": "Tail key data: Park boost -3% (stadium -8%, weather +6%). Quantrill (HR risk 0.08, vs LHB +0.63, vs RHB -0.58). Klassen (HR risk 0.08, vs LHB -0.97, vs RHB +1.74).",
        "rows": [
            row("Moises Ballesteros", "L", "+670", 64, "⭐", ["vs Quantrill"], """Worst Pickz Favorite. 0 HR, 96.9 mph EV. Quantrill LHB split +0.63, HR risk 0.08. park suppresses carry (-8%); limited recent HR events.""", blast="good"),
            row("Mike Trout", "R", "+320", 58, "", ["vs Quantrill"], """1 HR, 1 near-HR, 89.9 mph EV. Quantrill RHB split -0.58, HR risk 0.08. tough split lane (-0.58); park suppresses carry (-8%).""", blast="good"),
            row("Nolan Schanuel", "L", "+870", 58, "", ["vs Quantrill"], """0 HR, 1 near-HR, 90.9 mph EV. Quantrill LHB split +0.63, HR risk 0.08. park suppresses carry (-8%); limited recent HR events."""),
            row("Jarred Kelenic", "L", "+399", 58, "⭐", ["vs Klassen"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 92.1 mph EV. Klassen LHB split -0.97, HR risk 0.08. tough split lane (-0.97); park suppresses carry (-8%).""", blast="good"),
            row("Corey Seager", "L", "+331", 58, "", ["vs Klassen"], """0 HR, 94.9 mph EV. Klassen LHB split -0.97, HR risk 0.08. tough split lane (-0.97); park suppresses carry (-8%).""", blast="good"),
            row("Elias Diaz", "R", "+830", 68, "", ["vs Klassen"], """1 HR, 1 near-HR, 85.7 mph EV. Klassen RHB split +1.74, HR risk 0.08. park suppresses carry (-8%); lighter EV form (85.7 mph).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-12")

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

    out = ROOT / '_games-0812.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
