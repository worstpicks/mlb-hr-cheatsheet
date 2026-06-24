#!/usr/bin/env python3
"""Generate games[] block for 2026-06-24 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Brandon Nimmo (L)",
    "Byron Buxton (R)",
    "Cam Smith (R)",
    "Hunter Goodman (R)",
    "Jac Caglianone (L)",
    "Joe Mack (L)",
    "Jordan Walker (R)",
    "Juan Soto (L)",
    "Kazuma Okamoto (R)",
    "Kody Clemens (L)",
    "Kyle Manzardo (L)",
    "Kyle Schwarber (L)",
    "Max Muncy (L)",
    "Pete Alonso (R)",
    "Pete Crow-Armstrong (L)",
    "Seiya Suzuki (R)",
}

GEMS = {
    "Edmundo Sosa (R)",
    "Eric Wagaman (R)",
    "Jarred Kelenic (L)",
    "Ryan Vilade (R)",
}

PLAYER_TEAMS = {
    "Anthony Volpe (R)": "NYY",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Bo Bichette (R)": "NYM",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Brice Turang (L)": "MIL",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Cam Smith (R)": "HOU",
    "Carson Benge (L)": "NYM",
    "Carson Kelly (R)": "CHC",
    "Ceddanne Rafaela (R)": "BOS",
    "Christian Walker (R)": "HOU",
    "Cole Carrigg (S)": "COL",
    "Colson Montgomery (L)": "CWS",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "Dansby Swanson (R)": "CHC",
    "Daulton Varsho (L)": "TOR",
    "Davis Schneider (R)": "TOR",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Donovan Walton (L)": "LAA",
    "Drake Baldwin (L)": "ATL",
    "Edmundo Sosa (R)": "PHI",
    "Endy Rodriguez (S)": "PIT",
    "Eric Wagaman (R)": "NYM",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Garrett Mitchell (L)": "MIL",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "James Wood (L)": "WSH",
    "Jarred Kelenic (L)": "TEX",
    "Jeremy Pena (R)": "HOU",
    "Jesus Sanchez (L)": "TOR",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "Jordan Walker (R)": "STL",
    "Jorge Soler (R)": "LAA",
    "Josh Bell (S)": "MIN",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kerry Carpenter (L)": "DET",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lawrence Butler (L)": "ATH",
    "Luis Garcia Jr. (L)": "WSH",
    "Luke Raley (L)": "SEA",
    "MJ Melendez (L)": "NYM",
    "Manny Machado (R)": "SD",
    "Marcell Ozuna (R)": "PIT",
    "Matt Chapman (R)": "SF",
    "Matt Vierling (R)": "DET",
    "Max Muncy (L)": "LAD",
    "Max Muncy (R)": "ATH",
    "Miguel Vargas (R)": "CWS",
    "Nathan Church (L)": "STL",
    "Nick Kurtz (L)": "ATH",
    "Owen Caissie (L)": "MIA",
    "Paul Goldschmidt (R)": "NYY",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Petey Halpin (L)": "CLE",
    "Randal Grichuk (R)": "CWS",
    "Randy Arozarena (R)": "SEA",
    "Riley Greene (L)": "DET",
    "Rowdy Tellez (L)": "ATL",
    "Ryan Vilade (R)": "TB",
    "Salvador Perez (R)": "KC",
    "Seiya Suzuki (R)": "CHC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Torkelson (R)": "DET",
    "Travis Bazzana (L)": "CLE",
    "Ty France (R)": "SD",
    "Tyler Callihan (L)": "PIT",
    "Tyler Soderstrom (L)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "William Contreras (R)": "MIL",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("ARI @ STL", "Liberatore"),
    ("CLE @ CWS", "Bibee"),
    ("KC @ TB", "Jax"),
    ("NYY @ DET", "Weathers"),
    ("TEX @ MIA", "Perez"),
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
        "title": "ARI @ STL - Mitch Bratt (L, ARI) vs Matthew Liberatore 🧤 (L, STL)",
        "description": "Tail key data: Park boost -6% (stadium -10%, weather +4%). Away starter risk unavailable. Liberatore 🧤 (HR risk 1.12, vs LHB +0.64, vs RHB +1.11).",
        "rows": [
            row("Jordan Walker", "R", "+413", 89, "⭐ 🌕 💣", ["vs Bratt"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 99.1 mph EV. Bratt split/risk data unavailable. limited split/risk sample; park/weather net drag (-6%).""", blast="high"),
            row("JJ Wetherholt", "L", "+620", 64, "", ["vs Bratt"], """0 HR, 1 near-HR, 88.2 mph EV. Bratt split/risk data unavailable. limited split/risk sample; park/weather net drag (-6%)."""),
            row("Nathan Church", "L", "+920", 62, "", ["vs Bratt"], """0 HR, 83.3 mph EV. Bratt split/risk data unavailable. limited split/risk sample; park/weather net drag (-6%)."""),
            row("Ketel Marte", "S", "+367", 88, "🌕 💣", ["vs Liberatore"], """2 HR, 2 near-HR, 98.0 mph EV. Liberatore RHB split +1.11, HR risk 1.12. park/weather net drag (-6%).""", blast="high"),
            row("Corbin Carroll", "L", "+501", 77, "", ["vs Liberatore"], """0 HR, 2 near-HR, 96.9 mph EV. Liberatore LHB split +0.64, HR risk 1.12. park/weather net drag (-6%).""", blast="good"),
        ],
    },
    {
        "title": "ATH @ SF - Gage Jump (R, ATH) vs Tyler Mahle (R, SF)",
        "description": "Tail key data: Park boost -28% (stadium -15%, weather -13%). Jump (HR risk -1.93, vs LHB -1.43, vs RHB -1.42). Mahle (HR risk -0.06, vs LHB -0.04, vs RHB -0.11).",
        "rows": [
            row("Bryce Eldridge", "L", "+680", 66, "", ["vs Jump"], """0 HR, 1 near-HR, 89.7 mph EV. Jump LHB split -1.43, HR risk -1.93. tough split lane (-1.43); pitcher suppresses HR (-1.93)."""),
            row("Matt Chapman", "R", "+725", 81, "", ["vs Jump"], """1 HR, 2 near-HR, 96.7 mph EV. Jump RHB split -1.42, HR risk -1.93. tough split lane (-1.42); pitcher suppresses HR (-1.93).""", blast="good"),
            row("Nick Kurtz", "L", "+390", 81, "🌕 💣", ["vs Mahle"], """2 HR, 3 near-HR, 89.3 mph EV. Mahle LHB split -0.04, HR risk -0.06. slight split headwind (-0.04); pitcher risk below avg (-0.06).""", blast="high"),
            row("Lawrence Butler", "L", "+840", 72, "", ["vs Mahle"], """1 HR, 2 near-HR, 77.7 mph EV. Mahle LHB split -0.04, HR risk -0.06. slight split headwind (-0.04); pitcher risk below avg (-0.06).""", blast="good"),
            row("Zack Gelof", "R", "+670", 70, "", ["vs Mahle"], """1 HR, 1 near-HR, 85.6 mph EV. Mahle RHB split -0.11, HR risk -0.06. slight split headwind (-0.11); pitcher risk below avg (-0.06).""", blast="good"),
            row("Tyler Soderstrom", "L", "+575", 62, "", ["vs Mahle"], """0 HR, 85.5 mph EV. Mahle LHB split -0.04, HR risk -0.06. slight split headwind (-0.04); pitcher risk below avg (-0.06)."""),
            row("Max Muncy", "R", "+457", 77, "", ["vs Mahle"], """1 HR, 2 near-HR, 93.1 mph EV. Mahle RHB split -0.11, HR risk -0.06. slight split headwind (-0.11); pitcher risk below avg (-0.06).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ SD - Martin Perez (L, ATL) vs JP Sears (L, SD)",
        "description": "Tail key data: Park boost -2% (stadium -2%, weather +0%). Perez (HR risk -0.94, vs LHB -0.37, vs RHB -0.87). Sears (HR risk 0.91, vs LHB +0.13, vs RHB +0.93).",
        "rows": [
            row("Manny Machado", "R", "+397", 70, "", ["vs Perez"], """0 HR, 94.4 mph EV. Perez split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Ty France", "R", "+770", 68, "", ["vs Perez"], """0 HR, 92.0 mph EV. Perez split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+504", 62, "", ["vs Perez"], """0 HR, 87.2 mph EV. Perez split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
            row("Drake Baldwin", "L", "+425", 93, "🌕 💣", ["vs Sears"], """3 HR, 4 near-HR, 94.7 mph EV. Sears LHB split +0.13, HR risk 0.91.""", blast="high"),
            row("Austin Riley", "R", "+425", 76, "🚀", ["vs Sears"], """0 HR, 102.0 mph EV. Sears RHB split +0.93, HR risk 0.91. limited recent HR events.""", blast="good"),
            row("Rowdy Tellez", "L", "N/A", 72, "", ["vs Sears"], """0 HR, 1 near-HR, 94.2 mph EV. Sears LHB split +0.13, HR risk 0.91. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "BAL @ LAA - Trey Gibson (R, BAL) vs Jose Soriano (R, LAA)",
        "description": "Tail key data: Park boost +12% (stadium +9%, weather +3%). Gibson (HR risk -0.15, vs LHB -0.20, vs RHB +0.12). Soriano (HR risk 0.06, vs LHB +0.18, vs RHB -0.21).",
        "rows": [
            row("Zach Neto", "R", "+372", 75, "", ["vs Gibson"], """1 HR, 2 near-HR, 91.2 mph EV. Gibson RHB split +0.12, HR risk -0.15. pitcher risk below avg (-0.15).""", blast="good"),
            row("Donovan Walton", "L", "+592", 81, "🌕 💣", ["vs Gibson"], """2 HR, 2 near-HR, 90.9 mph EV. Gibson LHB split -0.20, HR risk -0.15. slight split headwind (-0.20); pitcher risk below avg (-0.15).""", blast="high"),
            row("Jorge Soler", "R", "+427", 64, "", ["vs Gibson"], """0 HR, 89.5 mph EV. Gibson RHB split +0.12, HR risk -0.15. pitcher risk below avg (-0.15); limited recent HR events."""),
            row("Pete Alonso", "R", "+414", 80, "⭐ 🌕 💣", ["vs Soriano"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 89.7 mph EV. Soriano RHB split -0.21, HR risk 0.06. slight split headwind (-0.21).""", blast="high"),
            row("Colton Cowser", "L", "+680", 70, "", ["vs Soriano"], """1 HR, 1 near-HR, 82.2 mph EV. Soriano LHB split +0.18, HR risk 0.06. lighter EV form (82.2 mph).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ COL - Ranger Suarez (L, BOS) vs Kyle Freeland (L, COL)",
        "description": "Tail key data: Park boost +35% (stadium +21%, weather +14%). Suarez (HR risk -1.30, vs LHB -0.37, vs RHB -1.16). Freeland (HR risk 0.71, vs LHB -0.90, vs RHB +1.09).",
        "rows": [
            row("Hunter Goodman", "R", "+315", 79, "⭐", ["vs Suarez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.6 mph EV. Suarez RHB split -1.16, HR risk -1.30. tough split lane (-1.16); pitcher suppresses HR (-1.30).""", blast="good"),
            row("Cole Carrigg", "S", "+800", 70, "", ["vs Suarez"], """1 HR, 1 near-HR, 83.7 mph EV. Suarez RHB split -1.16, HR risk -1.30. tough split lane (-1.16); pitcher suppresses HR (-1.30).""", blast="good"),
            row("Wilyer Abreu", "L", "+360", 74, "", ["vs Freeland"], """1 HR, 1 near-HR, 91.9 mph EV. Freeland LHB split -0.90, HR risk 0.71. tough split lane (-0.90).""", blast="good"),
            row("Ceddanne Rafaela", "R", "+490", 72, "", ["vs Freeland"], """1 HR, 2 near-HR, 86.3 mph EV. Freeland RHB split +1.09, HR risk 0.71. lighter EV form (86.3 mph).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ NYM (G1) - Shota Imanaga (L, CHC) vs Sean Manaea (L, NYM)",
        "description": "Tail key data: Park boost data unavailable. Away starter risk unavailable. Manaea (HR risk -0.07, vs LHB -0.44, vs RHB +0.26).",
        "rows": [
            row("Juan Soto", "L", "N/A", 78, "⭐", ["vs Imanaga"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.6 mph EV. Imanaga split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("MJ Melendez", "L", "N/A", 70, "", ["vs Imanaga"], """1 HR, 1 near-HR, 81.5 mph EV. Imanaga split/risk data unavailable. limited split/risk sample; lighter EV form (81.5 mph).""", blast="good"),
            row("Francisco Alvarez", "R", "N/A", 64, "", ["vs Imanaga"], """0 HR, 89.9 mph EV. Imanaga split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
            row("Eric Wagaman", "R", "N/A", 82, "🚀 💎", ["vs Imanaga"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 109.4 mph EV. Imanaga split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Carson Benge", "L", "N/A", 76, "", ["vs Imanaga"], """1 HR, 2 near-HR, 92.3 mph EV. Imanaga split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Pete Crow-Armstrong", "L", "N/A", 74, "⭐", ["vs Manaea"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.6 mph EV. Manaea LHB split -0.44, HR risk -0.07. tough split lane (-0.44); pitcher risk below avg (-0.07).""", blast="good"),
            row("Ian Happ", "S", "N/A", 70, "", ["vs Manaea"], """1 HR, 1 near-HR, 87.5 mph EV. Manaea RHB split +0.26, HR risk -0.07. pitcher risk below avg (-0.07); lighter EV form (87.5 mph).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ NYM (G2) - Javier Assad (R, CHC) vs Nolan McLean (R, NYM)",
        "description": "Tail key data: Park boost data unavailable. Away starter risk unavailable. McLean (HR risk -0.87, vs LHB -0.70, vs RHB -0.57).",
        "rows": [
            row("Juan Soto", "L", "N/A", 89, "⭐ 🌕 💣", ["vs Assad"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 90.9 mph EV. Assad split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Carson Benge", "L", "N/A", 82, "🌕 💣", ["vs Assad"], """2 HR, 3 near-HR, 90.1 mph EV. Assad split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Bo Bichette", "R", "N/A", 80, "🌕 💣", ["vs Assad"], """2 HR, 2 near-HR, 90.5 mph EV. Assad split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Francisco Alvarez", "R", "N/A", 70, "", ["vs Assad"], """1 HR, 1 near-HR, 87.4 mph EV. Assad split/risk data unavailable. limited split/risk sample; lighter EV form (87.4 mph).""", blast="good"),
            row("Seiya Suzuki", "R", "N/A", 72, "⭐", ["vs McLean"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 93.6 mph EV. McLean RHB split -0.57, HR risk -0.87. tough split lane (-0.57); pitcher suppresses HR (-0.87).""", blast="good"),
            row("Dansby Swanson", "R", "N/A", 62, "", ["vs McLean"], """0 HR, 87.2 mph EV. McLean RHB split -0.57, HR risk -0.87. tough split lane (-0.57); pitcher suppresses HR (-0.87)."""),
            row("Carson Kelly", "R", "N/A", 62, "", ["vs McLean"], """0 HR, 77.4 mph EV. McLean RHB split -0.57, HR risk -0.87. tough split lane (-0.57); pitcher suppresses HR (-0.87)."""),
            row("Ian Happ", "S", "N/A", 64, "", ["vs McLean"], """0 HR, 1 near-HR, 86.0 mph EV. McLean RHB split -0.57, HR risk -0.87. tough split lane (-0.57); pitcher suppresses HR (-0.87)."""),
        ],
    },
    {
        "title": "CLE @ CWS - Tanner Bibee 🧤 (R, CLE) vs Erick Fedde (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Bibee 🧤 (HR risk 1.34, vs LHB +1.22, vs RHB +0.83). Fedde (HR risk -0.24, vs LHB -0.31, vs RHB +0.12).",
        "rows": [
            row("Colson Montgomery", "L", "+337", 77, "", ["vs Bibee"], """1 HR, 1 near-HR, 94.6 mph EV. Bibee LHB split +1.22, HR risk 1.34.""", blast="good"),
            row("Miguel Vargas", "R", "+383", 64, "", ["vs Bibee"], """0 HR, 1 near-HR, 85.5 mph EV. Bibee RHB split +0.83, HR risk 1.34. limited recent HR events; lighter EV form (85.5 mph)."""),
            row("Randal Grichuk", "R", "N/A", 67, "", ["vs Bibee"], """0 HR, 1 near-HR, 90.7 mph EV. Bibee RHB split +0.83, HR risk 1.34. limited recent HR events."""),
            row("Kyle Manzardo", "L", "+370", 76, "⭐", ["vs Fedde"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.9 mph EV. Fedde LHB split -0.31, HR risk -0.24. slight split headwind (-0.31); pitcher risk below avg (-0.24).""", blast="good"),
            row("Travis Bazzana", "L", "+590", 70, "", ["vs Fedde"], """1 HR, 1 near-HR, 77.2 mph EV. Fedde LHB split -0.31, HR risk -0.24. slight split headwind (-0.31); pitcher risk below avg (-0.24).""", blast="good"),
            row("Petey Halpin", "L", "+730", 62, "", ["vs Fedde"], """0 HR, 85.0 mph EV. Fedde LHB split -0.31, HR risk -0.24. slight split headwind (-0.31); pitcher risk below avg (-0.24)."""),
        ],
    },
    {
        "title": "HOU @ TOR - Mike Burrows (R, HOU) vs Trey Yesavage (R, TOR)",
        "description": "Tail key data: Park boost +2% (stadium +6%, weather -4%). Burrows (HR risk 0.77, vs LHB +0.67, vs RHB +0.40). Yesavage (HR risk -0.28, vs LHB -0.47, vs RHB +0.11).",
        "rows": [
            row("Kazuma Okamoto", "R", "+376", 88, "⭐ 🌕 💣", ["vs Burrows"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 91.7 mph EV. Burrows RHB split +0.40, HR risk 0.77. weather carry headwind (-4%).""", blast="high"),
            row("Davis Schneider", "R", "N/A", 70, "", ["vs Burrows"], """1 HR, 1 near-HR, 85.2 mph EV. Burrows RHB split +0.40, HR risk 0.77. weather carry headwind (-4%); lighter EV form (85.2 mph).""", blast="good"),
            row("Daulton Varsho", "L", "+494", 78, "🌕 💣", ["vs Burrows"], """2 HR, 2 near-HR, 83.0 mph EV. Burrows LHB split +0.67, HR risk 0.77. weather carry headwind (-4%); lighter EV form (83.0 mph).""", blast="high"),
            row("Jesus Sanchez", "L", "+475", 64, "", ["vs Burrows"], """0 HR, 89.7 mph EV. Burrows LHB split +0.67, HR risk 0.77. weather carry headwind (-4%); limited recent HR events."""),
            row("Cam Smith", "R", "+730", 84, "⭐ 🌕 💣", ["vs Yesavage"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.5 mph EV. Yesavage RHB split +0.11, HR risk -0.28. pitcher risk below avg (-0.28); weather carry headwind (-4%).""", blast="high"),
            row("Yordan Alvarez", "L", "+311", 64, "", ["vs Yesavage"], """0 HR, 1 near-HR, 88.4 mph EV. Yesavage LHB split -0.47, HR risk -0.28. tough split lane (-0.47); pitcher risk below avg (-0.28)."""),
            row("Jeremy Pena", "R", "+720", 78, "🌕 💣", ["vs Yesavage"], """2 HR, 2 near-HR, 86.1 mph EV. Yesavage RHB split +0.11, HR risk -0.28. pitcher risk below avg (-0.28); weather carry headwind (-4%).""", blast="high"),
            row("Christian Walker", "R", "+394", 76, "", ["vs Yesavage"], """1 HR, 2 near-HR, 92.4 mph EV. Yesavage RHB split +0.11, HR risk -0.28. pitcher risk below avg (-0.28); weather carry headwind (-4%).""", blast="good"),
        ],
    },
    {
        "title": "KC @ TB - Noah Cameron (L, KC) vs Griffin Jax 🧤 (R, TB)",
        "description": "Tail key data: Park boost -2% (stadium -3%, weather +1%). Cameron (HR risk -0.52, vs LHB +0.10, vs RHB -0.40). Jax 🧤 (HR risk 1.07, vs LHB +0.98, vs RHB +0.45).",
        "rows": [
            row("Ryan Vilade", "R", "+920", 70, "💎", ["vs Cameron"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 87.2 mph EV. Cameron RHB split -0.40, HR risk -0.52. tough split lane (-0.40); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Junior Caminero", "R", "+315", 71, "", ["vs Cameron"], """0 HR, 95.1 mph EV. Cameron RHB split -0.40, HR risk -0.52. tough split lane (-0.40); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Yandy Diaz", "R", "+474", 65, "", ["vs Cameron"], """0 HR, 90.6 mph EV. Cameron RHB split -0.40, HR risk -0.52. tough split lane (-0.40); pitcher suppresses HR (-0.52)."""),
            row("Jac Caglianone", "L", "+458", 90, "⭐ 🌕 💣", ["vs Jax"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 94.2 mph EV. Jax LHB split +0.98, HR risk 1.07.""", blast="high"),
            row("Salvador Perez", "R", "+420", 72, "", ["vs Jax"], """1 HR, 2 near-HR, 87.4 mph EV. Jax RHB split +0.45, HR risk 1.07. lighter EV form (87.4 mph).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ MIN - Shohei Ohtani (R, LAD) vs Joe Ryan (R, MIN)",
        "description": "Tail key data: Park boost +1% (stadium -6%, weather +7%). Ohtani (HR risk -1.52, vs LHB -1.21, vs RHB -1.10). Ryan (HR risk 0.29, vs LHB +0.44, vs RHB -0.20).",
        "rows": [
            row("Byron Buxton", "R", "+381", 85, "⭐ 🌕 💣", ["vs Ohtani"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 93.0 mph EV. Ohtani RHB split -1.10, HR risk -1.52. tough split lane (-1.10); pitcher suppresses HR (-1.52).""", blast="high"),
            row("Kody Clemens", "L", "+504", 80, "⭐", ["vs Ohtani"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 93.7 mph EV. Ohtani LHB split -1.21, HR risk -1.52. tough split lane (-1.21); pitcher suppresses HR (-1.52).""", blast="good"),
            row("Josh Bell", "S", "+680", 70, "", ["vs Ohtani"], """1 HR, 1 near-HR, 85.6 mph EV. Ohtani RHB split -1.10, HR risk -1.52. tough split lane (-1.10); pitcher suppresses HR (-1.52).""", blast="good"),
            row("Shohei Ohtani", "L", "+240", 89, "🌕 💣", ["vs Ryan"], """2 HR, 3 near-HR, 97.2 mph EV. Ryan LHB split +0.44, HR risk 0.29. park suppresses carry (-6%).""", blast="high"),
            row("Max Muncy", "L", "+340", 75, "⭐", ["vs Ryan"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 91.1 mph EV. Ryan LHB split +0.44, HR risk 0.29. park suppresses carry (-6%).""", blast="good"),
            row("Dalton Rushing", "L", "+273", 72, "", ["vs Ryan"], """1 HR, 1 near-HR, 90.5 mph EV. Ryan LHB split +0.44, HR risk 0.29. park suppresses carry (-6%).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ CIN - Shane Drohan (L, MIL) vs Rhett Lowder (R, CIN)",
        "description": "Tail key data: Park boost +15% (stadium +13%, weather +2%). Drohan (HR risk -0.24, vs LHB -1.15, vs RHB +0.59). Lowder (HR risk 0.38, vs LHB +1.33, vs RHB -1.63).",
        "rows": [
            row("Tyler Stephenson", "R", "+551", 62, "", ["vs Drohan"], """0 HR, 88.2 mph EV. Drohan RHB split +0.59, HR risk -0.24. pitcher risk below avg (-0.24); limited recent HR events."""),
            row("JJ Bleday", "L", "+544", 71, "", ["vs Drohan"], """1 HR, 1 near-HR, 89.2 mph EV. Drohan LHB split -1.15, HR risk -0.24. tough split lane (-1.15); pitcher risk below avg (-0.24).""", blast="good"),
            row("Garrett Mitchell", "L", "+509", 70, "", ["vs Lowder"], """1 HR, 1 near-HR, 88.4 mph EV. Lowder LHB split +1.33, HR risk 0.38.""", blast="good"),
            row("Jake Bauers", "L", "+333", 72, "", ["vs Lowder"], """0 HR, 96.3 mph EV. Lowder LHB split +1.33, HR risk 0.38. limited recent HR events.""", blast="good"),
            row("William Contreras", "R", "+444", 78, "", ["vs Lowder"], """1 HR, 2 near-HR, 93.5 mph EV. Lowder RHB split -1.63, HR risk 0.38. tough split lane (-1.63).""", blast="good"),
            row("Jackson Chourio", "R", "+350", 66, "", ["vs Lowder"], """0 HR, 91.8 mph EV. Lowder RHB split -1.63, HR risk 0.38. tough split lane (-1.63); limited recent HR events."""),
            row("Brice Turang", "L", "+490", 64, "", ["vs Lowder"], """0 HR, 90.1 mph EV. Lowder LHB split +1.33, HR risk 0.38. limited recent HR events."""),
        ],
    },
    {
        "title": "NYY @ DET - Ryan Weathers 🧤 (L, NYY) vs Tarik Skubal (L, DET)",
        "description": "Tail key data: Park boost -13% (stadium -12%, weather -2%). Weathers 🧤 (HR risk 1.03, vs LHB +1.31, vs RHB +0.66). Skubal (HR risk -0.44, vs LHB +0.17, vs RHB -0.36).",
        "rows": [
            row("Dillon Dingler", "R", "+520", 77, "", ["vs Weathers"], """1 HR, 1 near-HR, 95.2 mph EV. Weathers RHB split +0.66, HR risk 1.03. park/weather net drag (-13%).""", blast="good"),
            row("Matt Vierling", "R", "+710", 75, "", ["vs Weathers"], """1 HR, 2 near-HR, 91.0 mph EV. Weathers RHB split +0.66, HR risk 1.03. park/weather net drag (-13%).""", blast="good"),
            row("Riley Greene", "L", "+610", 78, "🚀", ["vs Weathers"], """0 HR, 1 near-HR, 100.7 mph EV. Weathers LHB split +1.31, HR risk 1.03. park/weather net drag (-13%); limited recent HR events.""", blast="good"),
            row("Kerry Carpenter", "L", "N/A", 71, "", ["vs Weathers"], """0 HR, 1 near-HR, 92.8 mph EV. Weathers LHB split +1.31, HR risk 1.03. park/weather net drag (-13%); limited recent HR events.""", blast="good"),
            row("Spencer Torkelson", "R", "+420", 62, "", ["vs Weathers"], """0 HR, 81.5 mph EV. Weathers RHB split +0.66, HR risk 1.03. park/weather net drag (-13%); limited recent HR events."""),
            row("Paul Goldschmidt", "R", "+650", 79, "🌕 💣", ["vs Skubal"], """2 HR, 2 near-HR, 88.6 mph EV. Skubal RHB split -0.36, HR risk -0.44. slight split headwind (-0.36); pitcher suppresses HR (-0.44).""", blast="high"),
            row("Ben Rice", "L", "+570", 62, "", ["vs Skubal"], """0 HR, 88.3 mph EV. Skubal LHB split +0.17, HR risk -0.44. pitcher suppresses HR (-0.44); park/weather net drag (-13%)."""),
            row("Anthony Volpe", "R", "+940", 63, "", ["vs Skubal"], """0 HR, 89.2 mph EV. Skubal RHB split -0.36, HR risk -0.44. slight split headwind (-0.36); pitcher suppresses HR (-0.44)."""),
        ],
    },
    {
        "title": "PHI @ WSH - Aaron Nola (R, PHI) vs Miles Mikolas (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Nola (HR risk 0.55, vs LHB +0.84, vs RHB -0.07). Mikolas (HR risk 0.40, vs LHB -0.19, vs RHB +1.09).",
        "rows": [
            row("James Wood", "L", "+312", 66, "", ["vs Nola"], """0 HR, 91.9 mph EV. Nola LHB split +0.84, HR risk 0.55. limited recent HR events."""),
            row("CJ Abrams", "L", "+410", 76, "", ["vs Nola"], """1 HR, 1 near-HR, 94.0 mph EV. Nola LHB split +0.84, HR risk 0.55.""", blast="good"),
            row("Luis Garcia Jr.", "L", "+563", 84, "🌕 💣", ["vs Nola"], """3 HR, 3 near-HR, 87.2 mph EV. Nola LHB split +0.84, HR risk 0.55. lighter EV form (87.2 mph).""", blast="high"),
            row("Kyle Schwarber", "L", "+204", 86, "⭐ 🌕 💣", ["vs Mikolas"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.6 mph EV. Mikolas LHB split -0.19, HR risk 0.40. slight split headwind (-0.19).""", blast="high"),
            row("Bryce Harper", "L", "+390", 73, "", ["vs Mikolas"], """1 HR, 1 near-HR, 90.6 mph EV. Mikolas LHB split -0.19, HR risk 0.40. slight split headwind (-0.19).""", blast="good"),
            row("Edmundo Sosa", "R", "+630", 72, "💎", ["vs Mikolas"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 88.1 mph EV. Mikolas RHB split +1.09, HR risk 0.40.""", blast="good"),
            row("Brandon Marsh", "L", "+640", 72, "", ["vs Mikolas"], """1 HR, 2 near-HR, 84.2 mph EV. Mikolas LHB split -0.19, HR risk 0.40. slight split headwind (-0.19); lighter EV form (84.2 mph).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ PIT - Bryan Woo (R, SEA) vs Braxton Ashcraft (R, PIT)",
        "description": "Tail key data: Park boost -14% (stadium -12%, weather -1%). Woo (HR risk -0.17, vs LHB +0.01, vs RHB -0.35). Ashcraft (HR risk -0.89, vs LHB -0.09, vs RHB -1.33).",
        "rows": [
            row("Brandon Lowe", "L", "+340", 76, "", ["vs Woo"], """1 HR, 1 near-HR, 93.5 mph EV. Woo LHB split +0.01, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-14%).""", blast="good"),
            row("Tyler Callihan", "L", "N/A", 62, "", ["vs Woo"], """0 HR, 88.1 mph EV. Woo LHB split +0.01, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-14%)."""),
            row("Bryan Reynolds", "S", "+600", 86, "🌕 💣", ["vs Woo"], """2 HR, 2 near-HR, 96.3 mph EV. Woo RHB split -0.35, HR risk -0.17. slight split headwind (-0.35); pitcher risk below avg (-0.17).""", blast="high"),
            row("Endy Rodriguez", "S", "+725", 80, "", ["vs Woo"], """1 HR, 1 near-HR, 97.5 mph EV. Woo RHB split -0.35, HR risk -0.17. slight split headwind (-0.35); pitcher risk below avg (-0.17).""", blast="good"),
            row("Marcell Ozuna", "R", "+625", 80, "", ["vs Woo"], """1 HR, 1 near-HR, 97.5 mph EV. Woo RHB split -0.35, HR risk -0.17. slight split headwind (-0.35); pitcher risk below avg (-0.17).""", blast="good"),
            row("Dominic Canzone", "L", "+575", 81, "🌕 💣", ["vs Ashcraft"], """2 HR, 2 near-HR, 90.9 mph EV. Ashcraft LHB split -0.09, HR risk -0.89. slight split headwind (-0.09); pitcher suppresses HR (-0.89).""", blast="high"),
            row("Luke Raley", "L", "+630", 77, "", ["vs Ashcraft"], """1 HR, 2 near-HR, 92.8 mph EV. Ashcraft LHB split -0.09, HR risk -0.89. slight split headwind (-0.09); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Randy Arozarena", "R", "+750", 80, "", ["vs Ashcraft"], """1 HR, 2 near-HR, 95.5 mph EV. Ashcraft RHB split -1.33, HR risk -0.89. tough split lane (-1.33); pitcher suppresses HR (-0.89).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ MIA - Jacob deGrom (R, TEX) vs Eury Perez 🧤 (R, MIA)",
        "description": "Tail key data: Park boost -12% (stadium -12%, weather +0%). deGrom (HR risk -0.01, vs LHB -0.24, vs RHB +0.26). Perez 🧤 (HR risk 1.01, vs LHB +0.06, vs RHB +1.79).",
        "rows": [
            row("Heriberto Hernandez", "R", "+511", 72, "", ["vs deGrom"], """0 HR, 95.9 mph EV. deGrom RHB split +0.26, HR risk -0.01. pitcher risk below avg (-0.01); park/weather net drag (-12%).""", blast="good"),
            row("Owen Caissie", "L", "+630", 80, "🌕 💣", ["vs deGrom"], """2 HR, 3 near-HR, 86.5 mph EV. deGrom LHB split -0.24, HR risk -0.01. slight split headwind (-0.24); pitcher risk below avg (-0.01).""", blast="high"),
            row("Kyle Stowers", "L", "+421", 70, "", ["vs deGrom"], """1 HR, 1 near-HR, 83.1 mph EV. deGrom LHB split -0.24, HR risk -0.01. slight split headwind (-0.24); pitcher risk below avg (-0.01).""", blast="good"),
            row("Joe Mack", "L", "+900", 86, "⭐ 🌕 💣", ["vs deGrom"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.6 mph EV. deGrom LHB split -0.24, HR risk -0.01. slight split headwind (-0.24); pitcher risk below avg (-0.01).""", blast="high"),
            row("Jake Burger", "R", "+490", 80, "🌕 💣", ["vs Perez"], """2 HR, 3 near-HR, 85.0 mph EV. Perez split/risk data unavailable. limited split/risk sample; park/weather net drag (-12%).""", blast="high"),
            row("Jarred Kelenic", "L", "N/A", 73, "💎", ["vs Perez"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 89.0 mph EV. Perez split/risk data unavailable. limited split/risk sample; park/weather net drag (-12%).""", blast="good"),
            row("Brandon Nimmo", "L", "+462", 81, "⭐", ["vs Perez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.6 mph EV. Perez split/risk data unavailable. limited split/risk sample; park/weather net drag (-12%).""", blast="good"),
            row("Wyatt Langford", "R", "+498", 81, "🌕 💣", ["vs Perez"], """2 HR, 2 near-HR, 91.1 mph EV. Perez split/risk data unavailable. limited split/risk sample; park/weather net drag (-12%).""", blast="high"),
            row("Joc Pederson", "L", "+382", 75, "", ["vs Perez"], """1 HR, 1 near-HR, 92.7 mph EV. Perez split/risk data unavailable. limited split/risk sample; park/weather net drag (-12%).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-24")

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

    out = ROOT / '_games-0624.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
