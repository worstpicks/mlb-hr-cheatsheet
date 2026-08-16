#!/usr/bin/env python3
"""Generate games[] block for 2026-08-16 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Brandon Lowe (L)",
    "Pete Alonso (R)",
    "Wilyer Abreu (L)",
}

GEMS = {
    "Agustin Ramirez (R)",
    "Alex Bregman (R)",
    "Austin Riley (R)",
    "Jazz Chisholm Jr. (L)",
    "Jose Siri (R)",
    "Mickey Moniak (L)",
    "Taylor Trammell (L)",
    "Tyler Soderstrom (L)",
}

PLAYER_TEAMS = {
    "Abimelec Ortiz (L)": "WSH",
    "Agustin Ramirez (R)": "MIA",
    "Alex Bregman (R)": "CHC",
    "Angel Genao (S)": "CLE",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Bo Bichette (R)": "NYM",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Brett Baty (L)": "NYM",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryson Stott (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Carter Jensen (L)": "KC",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Coby Mayo (R)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Dominic Canzone (L)": "SEA",
    "Dylan Crews (R)": "WSH",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Lindor (S)": "NYM",
    "Gary Sanchez (R)": "MIL",
    "Griffin Conine (L)": "MIA",
    "Gunnar Henderson (L)": "BAL",
    "Hunter Feduccia (L)": "LAD",
    "Hunter Goodman (R)": "COL",
    "J.T. Realmuto (R)": "PHI",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jarren Duran (L)": "BOS",
    "Jazz Chisholm Jr. (L)": "NYY",
    "John Rave (L)": "KC",
    "Jonah Heim (S)": "ATH",
    "Jorge Mateo (R)": "TB",
    "Jose Siri (R)": "LAA",
    "Josh Bell (S)": "MIN",
    "Jung Hoo Lee (L)": "SF",
    "Kazuma Okamoto (R)": "TOR",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Lars Nootbaar (L)": "ARI",
    "Leody Taveras (S)": "BAL",
    "Luis Garcia Jr. (L)": "NYY",
    "Manny Machado (R)": "SD",
    "Masataka Yoshida (L)": "BOS",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Mickey Moniak (L)": "COL",
    "Miguel Amaya (R)": "CHC",
    "Mike Trout (R)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Randal Grichuk (R)": "CWS",
    "Rhys Hoskins (R)": "CLE",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan Vilade (R)": "TB",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Taylor Trammell (L)": "HOU",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Trent Grisham (L)": "NYY",
    "Ty France (R)": "SD",
    "Tyler Soderstrom (L)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "Willi Castro (S)": "COL",
    "Wilyer Abreu (L)": "BOS",
    "Xander Bogaerts (R)": "SD",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zac Veen (L)": "COL",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("BOS @ PIT", "Bachar"),
    ("KC @ LAA", "Johnson"),
    ("STL @ CHC", "Cabrera"),
    ("WSH @ NYM", "Irvin"),
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
        "title": "ARI @ ATL - Michael Soroka (R, ARI) vs Bryce Elder (R, ATL)",
        "description": "Tail key data: Park boost +5% (stadium -2%, weather +7%). Soroka (HR risk -0.34, vs LHB -0.33, vs RHB -0.12). Elder (HR risk 0.70, vs LHB +0.51, vs RHB +0.64).",
        "rows": [
            row("Matt Olson", "L", "+285", 67, "🌕 💣", ["vs Soroka"], """2 HR, 3 near-HR, 89.3 mph EV. Soroka LHB split -0.33, HR risk -0.34. slight split headwind (-0.33); pitcher risk below avg (-0.34).""", blast="high"),
            row("Ronald Acuna Jr.", "R", "+369", 58, "", ["vs Soroka"], """0 HR, 1 near-HR, 95.2 mph EV. Soroka RHB split -0.12, HR risk -0.34. slight split headwind (-0.12); pitcher risk below avg (-0.34).""", blast="good"),
            row("Austin Riley", "R", "+421", 58, "💎", ["vs Soroka"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.7 mph EV. Soroka RHB split -0.12, HR risk -0.34. slight split headwind (-0.12); pitcher risk below avg (-0.34).""", blast="good"),
            row("Corbin Carroll", "L", "+320", 77, "", ["vs Elder"], """1 HR, 1 near-HR, 93.5 mph EV. Elder LHB split +0.51, HR risk 0.70.""", blast="good"),
            row("Tim Tawa", "R", "+640", 80, "", ["vs Elder"], """1 HR, 1 near-HR, 97.2 mph EV. Elder RHB split +0.64, HR risk 0.70.""", blast="good"),
            row("Lars Nootbaar", "L", "+567", 73, "", ["vs Elder"], """0 HR, 1 near-HR, 93.6 mph EV. Elder LHB split +0.51, HR risk 0.70. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "BAL @ TB - Trevor Rogers (L, BAL) vs Freddy Peralta (R, TB)",
        "description": "Tail key data: Park boost -2% (stadium -3%, weather +1%). Rogers (HR risk -0.36, vs LHB -1.33, vs RHB +0.12). Peralta (HR risk 0.63, vs LHB +0.16, vs RHB +0.93).",
        "rows": [
            row("Yandy Diaz", "R", "+484", 69, "🌕 💣", ["vs Rogers"], """2 HR, 2 near-HR, 94.1 mph EV. Rogers RHB split +0.12, HR risk -0.36. pitcher risk below avg (-0.36).""", blast="high"),
            row("Ryan Vilade", "R", "+600", 75, "🌕 💣", ["vs Rogers"], """2 HR, 3 near-HR, 95.3 mph EV. Rogers RHB split +0.12, HR risk -0.36. pitcher risk below avg (-0.36).""", blast="high"),
            row("Jorge Mateo", "R", "+541", 58, "", ["vs Rogers"], """0 HR, 92.3 mph EV. Rogers RHB split +0.12, HR risk -0.36. pitcher risk below avg (-0.36); limited recent HR events.""", blast="good"),
            row("Pete Alonso", "R", "+310", 82, "⭐", ["vs Peralta"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.1 mph EV. Peralta RHB split +0.93, HR risk 0.63.""", blast="good"),
            row("Christian Encarnacion-Strand", "R", "+267", 77, "", ["vs Peralta"], """1 HR, 1 near-HR, 93.3 mph EV. Peralta RHB split +0.93, HR risk 0.63.""", blast="good"),
            row("Coby Mayo", "R", "+534", 76, "", ["vs Peralta"], """0 HR, 1 near-HR, 96.2 mph EV. Peralta RHB split +0.93, HR risk 0.63. limited recent HR events.""", blast="good"),
            row("Gunnar Henderson", "L", "+500", 75, "", ["vs Peralta"], """1 HR, 2 near-HR, 97.9 mph EV. Peralta LHB split +0.16, HR risk 0.63.""", blast="good"),
            row("Leody Taveras", "S", "+1040", 82, "", ["vs Peralta"], """1 HR, 2 near-HR, 96.2 mph EV. Peralta SHB→RHB split +0.93, HR risk 0.63.""", blast="good"),
        ],
    },
    {
        "title": "BOS @ PIT - Patrick Sandoval (L, BOS) vs Lake Bachar 🧤 (R, PIT)",
        "description": "Tail key data: Park boost +1% (stadium -17%, weather +18%). Sandoval (HR risk -0.65, vs LHB +1.44, vs RHB -1.10). Bachar 🧤 (HR risk 0.95, vs LHB +0.33, vs RHB +1.02).",
        "rows": [
            row("Bryan Reynolds", "S", "+820", 62, "", ["vs Sandoval"], """0 HR, 92.9 mph EV. Sandoval SHB→LHB split +1.44, HR risk -0.65. pitcher suppresses HR (-0.65); park suppresses carry (-17%).""", blast="good"),
            row("Brandon Lowe", "L", "+650", 58, "⭐", ["vs Sandoval"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 88.1 mph EV. Sandoval LHB split +1.44, HR risk -0.65. pitcher suppresses HR (-0.65); park suppresses carry (-17%)."""),
            row("Wilyer Abreu", "L", "N/A", 76, "⭐", ["vs Bachar"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 90.6 mph EV. Bachar LHB split +0.33, HR risk 0.95. park suppresses carry (-17%).""", blast="good"),
            row("Jarren Duran", "L", "N/A", 80, "", ["vs Bachar"], """1 HR, 1 near-HR, 95.5 mph EV. Bachar LHB split +0.33, HR risk 0.95. park suppresses carry (-17%).""", blast="good"),
            row("Masataka Yoshida", "L", "N/A", 65, "", ["vs Bachar"], """0 HR, 90.0 mph EV. Bachar LHB split +0.33, HR risk 0.95. park suppresses carry (-17%); limited recent HR events."""),
        ],
    },
    {
        "title": "COL @ SF - Gabriel Hughes (R, COL) vs Blade Tidwell (R, SF)",
        "description": "Tail key data: Park boost -23% (stadium -17%, weather -5%). Hughes (HR risk -0.91, vs LHB -0.85, vs RHB -0.20). Tidwell (HR risk -0.89, vs LHB -0.20, vs RHB -1.05).",
        "rows": [
            row("Jung Hoo Lee", "L", "+1100", 58, "", ["vs Hughes"], """1 HR, 2 near-HR, 95.5 mph EV. Hughes LHB split -0.85, HR risk -0.91. tough split lane (-0.85); pitcher suppresses HR (-0.91).""", blast="good"),
            row("Bryce Eldridge", "L", "+480", 58, "", ["vs Hughes"], """1 HR, 1 near-HR, 90.8 mph EV. Hughes LHB split -0.85, HR risk -0.91. tough split lane (-0.85); pitcher suppresses HR (-0.91).""", blast="good"),
            row("Mickey Moniak", "L", "+440", 67, "🌕 💣 💎", ["vs Tidwell"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 96.8 mph EV. Tidwell LHB split -0.20, HR risk -0.89. slight split headwind (-0.20); pitcher suppresses HR (-0.89).""", blast="high"),
            row("Willi Castro", "S", "+820", 64, "🌕 💣", ["vs Tidwell"], """3 HR, 5 near-HR, 92.6 mph EV. Tidwell SHB→LHB split -0.20, HR risk -0.89. slight split headwind (-0.20); pitcher suppresses HR (-0.89).""", blast="high"),
            row("Hunter Goodman", "R", "N/A", 58, "", ["vs Tidwell"], """1 HR, 3 near-HR, 93.4 mph EV. Tidwell RHB split -1.05, HR risk -0.89. tough split lane (-1.05); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Zac Veen", "L", "+640", 58, "🚀", ["vs Tidwell"], """0 HR, 100.8 mph EV. Tidwell LHB split -0.20, HR risk -0.89. slight split headwind (-0.20); pitcher suppresses HR (-0.89).""", blast="good"),
        ],
    },
    {
        "title": "CWS @ DET - Sean Burke (R, CWS) vs Drew Anderson (R, DET)",
        "description": "Tail key data: Park boost data unavailable. Burke (HR risk 0.09, vs LHB +0.25, vs RHB -0.20). Anderson (HR risk 0.10, vs LHB +0.09, vs RHB +0.12).",
        "rows": [
            row("Spencer Torkelson", "R", "+400", 61, "", ["vs Burke"], """0 HR, 2 near-HR, 99.5 mph EV. Burke RHB split -0.20, HR risk 0.09. slight split headwind (-0.20).""", blast="good"),
            row("Munetaka Murakami", "L", "+379", 84, "🌕 💣", ["vs Anderson"], """3 HR, 3 near-HR, 98.2 mph EV. Anderson LHB split +0.09, HR risk 0.10.""", blast="high"),
            row("Randal Grichuk", "R", "N/A", 61, "", ["vs Anderson"], """0 HR, 1 near-HR, 94.4 mph EV. Anderson RHB split +0.12, HR risk 0.10. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "KC @ LAA - Noah Cameron (L, KC) vs Ryan Johnson 🧤 (R, LAA)",
        "description": "Tail key data: Park boost -9% (stadium -9%, weather +0%). Cameron (HR risk -0.65, vs LHB +0.29, vs RHB -0.76). Johnson 🧤 (HR risk 1.63, vs LHB +1.87, vs RHB +0.28).",
        "rows": [
            row("Jose Siri", "R", "+500", 58, "💎", ["vs Cameron"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 98.0 mph EV. Cameron RHB split -0.76, HR risk -0.65. tough split lane (-0.76); pitcher suppresses HR (-0.65).""", blast="good"),
            row("Mike Trout", "R", "+350", 58, "", ["vs Cameron"], """1 HR, 1 near-HR, 91.7 mph EV. Cameron RHB split -0.76, HR risk -0.65. tough split lane (-0.76); pitcher suppresses HR (-0.65).""", blast="good"),
            row("Jac Caglianone", "L", "+301", 96, "🌕 💣", ["vs Johnson"], """2 HR, 2 near-HR, 97.9 mph EV. Johnson LHB split +1.87, HR risk 1.63. park/weather net drag (-9%).""", blast="high"),
            row("Carter Jensen", "L", "+303", 92, "🌕 💣", ["vs Johnson"], """1 HR, 2 near-HR, 94.9 mph EV. Johnson LHB split +1.87, HR risk 1.63. park/weather net drag (-9%).""", blast="good"),
            row("John Rave", "L", "+620", 92, "🌕 💣", ["vs Johnson"], """1 HR, 2 near-HR, 93.8 mph EV. Johnson LHB split +1.87, HR risk 1.63. park/weather net drag (-9%).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ CIN - Eury Perez (R, MIA) vs Nick Lodolo (L, CIN)",
        "description": "Tail key data: Park boost +25% (stadium +15%, weather +10%). Perez (HR risk -0.66, vs LHB -0.79, vs RHB -0.15). Lodolo (HR risk 0.43, vs LHB -1.20, vs RHB +0.87).",
        "rows": [
            row("Matt McLain", "R", "+600", 62, "", ["vs Perez"], """1 HR, 2 near-HR, 93.0 mph EV. Perez RHB split -0.15, HR risk -0.66. slight split headwind (-0.15); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Tyler Stephenson", "R", "+560", 63, "", ["vs Perez"], """1 HR, 1 near-HR, 95.6 mph EV. Perez RHB split -0.15, HR risk -0.66. slight split headwind (-0.15); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Agustin Ramirez", "R", "+520", 85, "💎", ["vs Lodolo"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.3 mph EV. Lodolo RHB split +0.87, HR risk 0.43.""", blast="good"),
            row("Griffin Conine", "L", "+390", 64, "", ["vs Lodolo"], """0 HR, 93.2 mph EV. Lodolo LHB split -1.20, HR risk 0.43. tough split lane (-1.20); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIL @ LAD - Logan Henderson (R, MIL) vs Tarik Skubal (L, LAD)",
        "description": "Tail key data: Park boost +20% (stadium +18%, weather +2%). Henderson (HR risk 0.89, vs LHB +0.99, vs RHB +0.05). Skubal (HR risk -0.38, vs LHB -0.07, vs RHB -0.28).",
        "rows": [
            row("Hunter Feduccia", "L", "N/A", 84, "", ["vs Henderson"], """1 HR, 1 near-HR, 91.7 mph EV. Henderson LHB split +0.99, HR risk 0.89.""", blast="good"),
            row("Teoscar Hernandez", "R", "+461", 78, "", ["vs Henderson"], """1 HR, 1 near-HR, 93.2 mph EV. Henderson RHB split +0.05, HR risk 0.89.""", blast="good"),
            row("Jake Bauers", "L", "+480", 63, "", ["vs Skubal"], """1 HR, 1 near-HR, 93.5 mph EV. Skubal LHB split -0.07, HR risk -0.38. slight split headwind (-0.07); pitcher risk below avg (-0.38).""", blast="good"),
            row("Gary Sanchez", "R", "+454", 64, "", ["vs Skubal"], """1 HR, 1 near-HR, 96.6 mph EV. Skubal RHB split -0.28, HR risk -0.38. slight split headwind (-0.28); pitcher risk below avg (-0.38).""", blast="good"),
            row("Jackson Chourio", "R", "+427", 63, "", ["vs Skubal"], """1 HR, 2 near-HR, 93.9 mph EV. Skubal RHB split -0.28, HR risk -0.38. slight split headwind (-0.28); pitcher risk below avg (-0.38).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ TOR - Ryan Weathers (L, NYY) vs Dylan Cease (R, TOR)",
        "description": "Tail key data: Park boost +11% (stadium +7%, weather +4%). Weathers (HR risk -0.23, vs LHB -0.66, vs RHB +0.14). Cease (HR risk -0.46, vs LHB +0.04, vs RHB -0.74).",
        "rows": [
            row("Kazuma Okamoto", "R", "+459", 58, "", ["vs Weathers"], """0 HR, 92.4 mph EV. Weathers RHB split +0.14, HR risk -0.23. pitcher risk below avg (-0.23); limited recent HR events.""", blast="good"),
            row("Trent Grisham", "L", "+455", 73, "🌕 💣", ["vs Cease"], """2 HR, 2 near-HR, 96.8 mph EV. Cease LHB split +0.04, HR risk -0.46. pitcher suppresses HR (-0.46).""", blast="high"),
            row("Jazz Chisholm Jr.", "L", "+462", 59, "💎", ["vs Cease"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.6 mph EV. Cease LHB split +0.04, HR risk -0.46. pitcher suppresses HR (-0.46); limited recent HR events.""", blast="good"),
            row("Spencer Jones", "L", "+800", 58, "", ["vs Cease"], """0 HR, 97.6 mph EV. Cease LHB split +0.04, HR risk -0.46. pitcher suppresses HR (-0.46); limited recent HR events.""", blast="good"),
            row("Luis Garcia Jr.", "L", "+583", 58, "", ["vs Cease"], """0 HR, 1 near-HR, 95.0 mph EV. Cease LHB split +0.04, HR risk -0.46. pitcher suppresses HR (-0.46); limited recent HR events.""", blast="good"),
            row("Ben Rice", "L", "+403", 58, "", ["vs Cease"], """0 HR, 98.4 mph EV. Cease LHB split +0.04, HR risk -0.46. pitcher suppresses HR (-0.46); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "PHI @ MIN - Andrew Painter (R, PHI) vs Dean Kremer (R, MIN)",
        "description": "Tail key data: Park boost +1% (stadium -7%, weather +8%). Painter (HR risk 0.40, vs LHB +0.41, vs RHB +0.22). Kremer (HR risk 0.33, vs LHB -0.25, vs RHB +0.85).",
        "rows": [
            row("Kody Clemens", "L", "+544", 75, "", ["vs Painter"], """1 HR, 1 near-HR, 97.4 mph EV. Painter LHB split +0.41, HR risk 0.40. park suppresses carry (-7%).""", blast="good"),
            row("Josh Bell", "S", "+548", 71, "", ["vs Painter"], """1 HR, 1 near-HR, 92.6 mph EV. Painter SHB→LHB split +0.41, HR risk 0.40. park suppresses carry (-7%).""", blast="good"),
            row("Royce Lewis", "R", "+450", 70, "", ["vs Painter"], """1 HR, 2 near-HR, 91.7 mph EV. Painter RHB split +0.22, HR risk 0.40. park suppresses carry (-7%).""", blast="good"),
            row("Kyle Schwarber", "L", "+278", 76, "🌕 💣", ["vs Kremer"], """2 HR, 3 near-HR, 92.3 mph EV. Kremer LHB split -0.25, HR risk 0.33. slight split headwind (-0.25); park suppresses carry (-7%).""", blast="high"),
            row("J.T. Realmuto", "R", "+950", 68, "", ["vs Kremer"], """0 HR, 1 near-HR, 93.9 mph EV. Kremer RHB split +0.85, HR risk 0.33. park suppresses carry (-7%); limited recent HR events.""", blast="good"),
            row("Bryson Stott", "L", "+680", 58, "", ["vs Kremer"], """0 HR, 89.3 mph EV. Kremer LHB split -0.25, HR risk 0.33. slight split headwind (-0.25); park suppresses carry (-7%)."""),
        ],
    },
    {
        "title": "SD @ CLE - Casey Mize (R, SD) vs Tanner Bibee (R, CLE)",
        "description": "Tail key data: Park boost +19% (stadium -2%, weather +21%). Mize (HR risk 0.02, vs LHB -0.25, vs RHB +0.30). Bibee (HR risk -0.09, vs LHB +0.40, vs RHB -0.76).",
        "rows": [
            row("Rhys Hoskins", "R", "N/A", 69, "", ["vs Mize"], """1 HR, 1 near-HR, 93.0 mph EV. Mize RHB split +0.30, HR risk 0.02.""", blast="good"),
            row("Angel Genao", "S", "+920", 68, "", ["vs Mize"], """0 HR, 1 near-HR, 98.4 mph EV. Mize SHB→RHB split +0.30, HR risk 0.02. limited recent HR events.""", blast="good"),
            row("Jackson Merrill", "L", "+470", 73, "", ["vs Bibee"], """1 HR, 2 near-HR, 99.6 mph EV. Bibee LHB split +0.40, HR risk -0.09. pitcher risk below avg (-0.09).""", blast="good"),
            row("Manny Machado", "R", "+500", 58, "🚀", ["vs Bibee"], """0 HR, 100.9 mph EV. Bibee RHB split -0.76, HR risk -0.09. tough split lane (-0.76); pitcher risk below avg (-0.09).""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+441", 63, "", ["vs Bibee"], """1 HR, 1 near-HR, 96.0 mph EV. Bibee RHB split -0.76, HR risk -0.09. tough split lane (-0.76); pitcher risk below avg (-0.09).""", blast="good"),
            row("Xander Bogaerts", "R", "+850", 58, "", ["vs Bibee"], """0 HR, 95.2 mph EV. Bibee RHB split -0.76, HR risk -0.09. tough split lane (-0.76); pitcher risk below avg (-0.09).""", blast="good"),
            row("Ty France", "R", "+549", 58, "", ["vs Bibee"], """0 HR, 93.5 mph EV. Bibee RHB split -0.76, HR risk -0.09. tough split lane (-0.76); pitcher risk below avg (-0.09).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ HOU - Bryan Woo (R, SEA) vs Hunter Brown (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +0%). Woo (HR risk -0.13, vs LHB -0.03, vs RHB -0.13). Brown (HR risk -0.35, vs LHB +0.51, vs RHB -1.33).",
        "rows": [
            row("Taylor Trammell", "L", "+564", 80, "🚀 🌕 💣 💎", ["vs Woo"], """Worst Pickz Hidden Gem. 2 HR, 4 near-HR, 101.5 mph EV. Woo LHB split -0.03, HR risk -0.13. slight split headwind (-0.03); pitcher risk below avg (-0.13).""", blast="high"),
            row("Yordan Alvarez", "L", "+250", 58, "", ["vs Woo"], """0 HR, 89.0 mph EV. Woo LHB split -0.03, HR risk -0.13. slight split headwind (-0.03); pitcher risk below avg (-0.13)."""),
            row("Nelson Velazquez", "R", "N/A", 60, "", ["vs Woo"], """0 HR, 1 near-HR, 96.5 mph EV. Woo RHB split -0.13, HR risk -0.13. slight split headwind (-0.13); pitcher risk below avg (-0.13).""", blast="good"),
            row("Dominic Canzone", "L", "+520", 66, "", ["vs Brown"], """1 HR, 1 near-HR, 95.5 mph EV. Brown LHB split +0.51, HR risk -0.35. pitcher risk below avg (-0.35).""", blast="good"),
            row("Cal Raleigh", "S", "+400", 63, "", ["vs Brown"], """0 HR, 2 near-HR, 95.0 mph EV. Brown SHB→LHB split +0.51, HR risk -0.35. pitcher risk below avg (-0.35).""", blast="good"),
        ],
    },
    {
        "title": "STL @ CHC - Hunter Dobbins (R, STL) vs Edward Cabrera 🧤 (R, CHC)",
        "description": "Tail key data: Park boost -1% (stadium +1%, weather -2%). Dobbins (HR risk -0.45, vs LHB -0.76, vs RHB +0.48). Cabrera 🧤 (HR risk 1.42, vs LHB +0.68, vs RHB +1.84).",
        "rows": [
            row("Alex Bregman", "R", "+630", 77, "🌕 💣 💎", ["vs Dobbins"], """Worst Pickz Hidden Gem. 4 HR, 4 near-HR, 91.7 mph EV. Dobbins RHB split +0.48, HR risk -0.45. pitcher suppresses HR (-0.45).""", blast="high"),
            row("Miguel Amaya", "R", "N/A", 66, "", ["vs Dobbins"], """1 HR, 2 near-HR, 96.2 mph EV. Dobbins RHB split +0.48, HR risk -0.45. pitcher suppresses HR (-0.45).""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+365", 58, "", ["vs Dobbins"], """1 HR, 2 near-HR, 89.9 mph EV. Dobbins LHB split -0.76, HR risk -0.45. tough split lane (-0.76); pitcher suppresses HR (-0.45).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ ATH - Cody Bradford (L, TEX) vs Jacob Lopez (L, ATH)",
        "description": "Tail key data: Park boost +38% (stadium +32%, weather +6%). Bradford (HR risk -0.90, vs LHB -1.05, vs RHB -0.40). Lopez (HR risk -0.22, vs LHB -0.82, vs RHB +0.17).",
        "rows": [
            row("Tyler Soderstrom", "L", "+409", 73, "🌕 💣 💎", ["vs Bradford"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 94.3 mph EV. Bradford LHB split -1.05, HR risk -0.90. tough split lane (-1.05); pitcher suppresses HR (-0.90).""", blast="high"),
            row("Zack Gelof", "R", "+457", 72, "🌕 💣", ["vs Bradford"], """2 HR, 2 near-HR, 95.4 mph EV. Bradford RHB split -0.40, HR risk -0.90. tough split lane (-0.40); pitcher suppresses HR (-0.90).""", blast="high"),
            row("Jonah Heim", "S", "+446", 60, "", ["vs Bradford"], """1 HR, 1 near-HR, 93.1 mph EV. Bradford SHB→RHB split -0.40, HR risk -0.90. tough split lane (-0.40); pitcher suppresses HR (-0.90).""", blast="good"),
            row("Jake Burger", "R", "+300", 72, "", ["vs Lopez"], """1 HR, 2 near-HR, 92.9 mph EV. Lopez RHB split +0.17, HR risk -0.22. pitcher risk below avg (-0.22).""", blast="good"),
            row("Brandon Nimmo", "L", "+430", 81, "🌕 💣", ["vs Lopez"], """2 HR, 3 near-HR, 98.5 mph EV. Lopez LHB split -0.82, HR risk -0.22. tough split lane (-0.82); pitcher risk below avg (-0.22).""", blast="high"),
        ],
    },
    {
        "title": "WSH @ NYM - Jake Irvin 🧤 (R, WSH) vs Christian Scott (R, NYM)",
        "description": "Tail key data: Park boost data unavailable. Irvin 🧤 (HR risk 1.28, vs LHB +1.43, vs RHB +0.09). Scott (HR risk -1.20, vs LHB -0.82, vs RHB -0.90).",
        "rows": [
            row("Brett Baty", "L", "+800", 94, "🌕 💣", ["vs Irvin"], """2 HR, 2 near-HR, 95.1 mph EV. Irvin LHB split +1.43, HR risk 1.28.""", blast="high"),
            row("Francisco Lindor", "S", "+359", 92, "🌕 💣", ["vs Irvin"], """1 HR, 2 near-HR, 97.9 mph EV. Irvin SHB→LHB split +1.43, HR risk 1.28.""", blast="good"),
            row("Bo Bichette", "R", "+640", 79, "", ["vs Irvin"], """1 HR, 1 near-HR, 93.5 mph EV. Irvin RHB split +0.09, HR risk 1.28.""", blast="good"),
            row("Abimelec Ortiz", "L", "+544", 66, "🌕 💣", ["vs Scott"], """3 HR, 3 near-HR, 96.0 mph EV. Scott LHB split -0.82, HR risk -1.20. tough split lane (-0.82); pitcher suppresses HR (-1.20).""", blast="high"),
            row("Dylan Crews", "R", "+551", 58, "", ["vs Scott"], """0 HR, 1 near-HR, 93.7 mph EV. Scott RHB split -0.90, HR risk -1.20. tough split lane (-0.90); pitcher suppresses HR (-1.20).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-16")

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

    out = ROOT / '_games-0816.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
