#!/usr/bin/env python3
"""Generate games[] block for 2026-07-26 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alejandro Kirk (R)",
    "Bryce Eldridge (L)",
    "Esmerlyn Valdez (R)",
    "Griffin Conine (L)",
    "Hunter Goodman (R)",
    "Ian Happ (S)",
    "JJ Wetherholt (L)",
    "Jake Burger (R)",
    "Jeremy Pena (R)",
    "Kyle Schwarber (L)",
    "Luke Raley (L)",
    "Matt Olson (L)",
    "Patrick Bailey (S)",
    "Pete Crow-Armstrong (L)",
    "Riley Greene (L)",
    "Ty France (R)",
    "Willson Contreras (R)",
}

GEMS = {
    "Casey Schmitt (R)",
}

PLAYER_TEAMS = {
    "Alejandro Kirk (R)": "TOR",
    "Brandon Marsh (L)": "PHI",
    "Brett Baty (L)": "NYM",
    "Bryce Eldridge (L)": "SF",
    "Byron Buxton (R)": "MIN",
    "Casey Schmitt (R)": "SF",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Derek Hill (R)": "PHI",
    "Drake Baldwin (L)": "ATL",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Ezequiel Duran (R)": "TEX",
    "Francisco Lindor (S)": "NYM",
    "Gary Sanchez (R)": "MIL",
    "Griffin Conine (L)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "JJ Wetherholt (L)": "STL",
    "Jake Burger (R)": "TEX",
    "Jasson Dominguez (S)": "NYY",
    "Jeremy Pena (R)": "HOU",
    "Joe Mack (L)": "MIA",
    "Jorge Soler (R)": "LAA",
    "Kazuma Okamoto (R)": "TOR",
    "Kody Clemens (L)": "MIN",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Tucker (L)": "LAD",
    "Lane Thomas (R)": "KC",
    "Lars Nootbaar (L)": "STL",
    "Luke Raley (L)": "SEA",
    "Matt Olson (L)": "ATL",
    "Max Schuemann (R)": "NYY",
    "Michael Busch (L)": "CHC",
    "Mitch Garver (R)": "SEA",
    "Munetaka Murakami (L)": "CWS",
    "Nathaniel Lowe (L)": "CIN",
    "Nelson Velazquez (R)": "STL",
    "Nick Gonzales (R)": "PIT",
    "Patrick Bailey (S)": "CLE",
    "Paul Goldschmidt (R)": "NYY",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Randy Arozarena (R)": "SEA",
    "Riley Greene (L)": "DET",
    "Royce Lewis (R)": "MIN",
    "Ryan Waldschmidt (R)": "ARI",
    "Salvador Perez (R)": "KC",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Trea Turner (R)": "PHI",
    "Tristan Peters (L)": "CWS",
    "Ty France (R)": "SD",
    "Willson Contreras (R)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("CHC @ PIT", "Taillon"),
    ("HOU @ CWS", "Blanco"),
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
        "title": "ARI @ WSH - Kohl Drake (L, ARI) vs Miles Mikolas (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Drake (HR risk 0.00, vs LHB +0.00, vs RHB -0.25). Mikolas (HR risk 0.43, vs LHB +0.05, vs RHB +0.74).",
        "rows": [
            row("Tim Tawa", "R", "+561", 74, "", ["vs Mikolas"], """0 HR, 2 near-HR, 95.5 mph EV. Mikolas RHB split +0.74, HR risk 0.43.""", blast="good"),
            row("Ryan Waldschmidt", "R", "+660", 73, "", ["vs Mikolas"], """1 HR, 1 near-HR, 91.7 mph EV. Mikolas RHB split +0.74, HR risk 0.43.""", blast="good"),
        ],
    },
    {
        "title": "ATH @ MIN - Jeffrey Springs (L, ATH) vs Connor Prielipp (L, MIN)",
        "description": "Tail key data: Park boost +1% (stadium -5%, weather +6%). Springs (HR risk 0.88, vs LHB -0.41, vs RHB +1.23). Prielipp (HR risk 0.03, vs LHB -0.44, vs RHB +0.11).",
        "rows": [
            row("Byron Buxton", "R", "+210", 81, "", ["vs Springs"], """0 HR, 1 near-HR, 95.6 mph EV. Springs RHB split +1.23, HR risk 0.88. limited recent HR events.""", blast="good"),
            row("Kody Clemens", "L", "N/A", 67, "", ["vs Springs"], """1 HR, 1 near-HR, 90.9 mph EV. Springs LHB split -0.41, HR risk 0.88. tough split lane (-0.41).""", blast="good"),
            row("Royce Lewis", "R", "+330", 71, "", ["vs Springs"], """0 HR, 91.3 mph EV. Springs RHB split +1.23, HR risk 0.88. limited recent HR events."""),
            row("Shea Langeliers", "R", "+303", 65, "", ["vs Prielipp"], """1 HR, 2 near-HR, 93.9 mph EV. Prielipp RHB split +0.11, HR risk 0.03.""", blast="good"),
        ],
    },
    {
        "title": "ATL @ BAL - Reynaldo Lopez (R, ATL) vs Shane Baz (R, BAL)",
        "description": "Tail key data: Park boost +0% (stadium -1%, weather +1%). Lopez (HR risk 0.11, vs LHB +0.50, vs RHB -0.30). Baz (HR risk -0.75, vs LHB -0.32, vs RHB -0.78).",
        "rows": [
            row("Christian Encarnacion-Strand", "R", "+450", 58, "", ["vs Lopez"], """0 HR, 1 near-HR, 88.9 mph EV. Lopez RHB split -0.30, HR risk 0.11. slight split headwind (-0.30); limited recent HR events."""),
            row("Drake Baldwin", "L", "+379", 64, "🌕 💣", ["vs Baz"], """2 HR, 2 near-HR, 95.8 mph EV. Baz LHB split -0.32, HR risk -0.75. slight split headwind (-0.32); pitcher suppresses HR (-0.75).""", blast="high"),
            row("Matt Olson", "L", "+271", 64, "⭐ 🌕 💣", ["vs Baz"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.8 mph EV. Baz LHB split -0.32, HR risk -0.75. slight split headwind (-0.32); pitcher suppresses HR (-0.75).""", blast="high"),
        ],
    },
    {
        "title": "CHC @ PIT - Jameson Taillon 🧤 (R, CHC) vs Braxton Ashcraft (R, PIT)",
        "description": "Tail key data: Park boost -11% (stadium -15%, weather +4%). Taillon 🧤 (HR risk 1.17, vs LHB +1.14, vs RHB +0.98). Ashcraft (HR risk 0.56, vs LHB +1.03, vs RHB -0.77).",
        "rows": [
            row("Esmerlyn Valdez", "R", "+389", 91, "⭐ 🌕 💣", ["vs Taillon"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.1 mph EV. Taillon RHB split +0.98, HR risk 1.17. park/weather net drag (-11%).""", blast="high"),
            row("Nick Gonzales", "R", "+920", 77, "", ["vs Taillon"], """1 HR, 1 near-HR, 87.7 mph EV. Taillon RHB split +0.98, HR risk 1.17. park/weather net drag (-11%); lighter EV form (87.7 mph).""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+350", 77, "⭐", ["vs Ashcraft"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.8 mph EV. Ashcraft LHB split +1.03, HR risk 0.56. park/weather net drag (-11%).""", blast="good"),
            row("Michael Busch", "L", "+450", 75, "", ["vs Ashcraft"], """1 HR, 1 near-HR, 93.3 mph EV. Ashcraft LHB split +1.03, HR risk 0.56. park/weather net drag (-11%).""", blast="good"),
            row("Ian Happ", "S", "+447", 72, "⭐", ["vs Ashcraft"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 89.7 mph EV. Ashcraft SHB→LHB split +1.03, HR risk 0.56. park/weather net drag (-11%).""", blast="good"),
        ],
    },
    {
        "title": "CIN @ STL - Andrew Abbott (L, CIN) vs Kyle Leahy (R, STL)",
        "description": "Tail key data: Park boost +7% (stadium -9%, weather +15%). Abbott (HR risk -0.26, vs LHB -0.10, vs RHB -0.23). Leahy (HR risk -0.49, vs LHB -0.29, vs RHB -0.41).",
        "rows": [
            row("JJ Wetherholt", "L", "+600", 73, "⭐ 🌕 💣", ["vs Abbott"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.9 mph EV. Abbott LHB split -0.10, HR risk -0.26. slight split headwind (-0.10); pitcher risk below avg (-0.26).""", blast="high"),
            row("Nelson Velazquez", "R", "+465", 61, "", ["vs Abbott"], """1 HR, 1 near-HR, 94.5 mph EV. Abbott RHB split -0.23, HR risk -0.26. slight split headwind (-0.23); pitcher risk below avg (-0.26).""", blast="good"),
            row("Lars Nootbaar", "L", "N/A", 58, "", ["vs Abbott"], """1 HR, 1 near-HR, 90.9 mph EV. Abbott LHB split -0.10, HR risk -0.26. slight split headwind (-0.10); pitcher risk below avg (-0.26).""", blast="good"),
            row("Eugenio Suarez", "R", "+485", 64, "🌕 💣", ["vs Leahy"], """2 HR, 2 near-HR, 91.7 mph EV. Leahy RHB split -0.41, HR risk -0.49. tough split lane (-0.41); pitcher suppresses HR (-0.49).""", blast="high"),
            row("Nathaniel Lowe", "L", "+730", 58, "", ["vs Leahy"], """1 HR, 2 near-HR, 86.2 mph EV. Leahy LHB split -0.29, HR risk -0.49. slight split headwind (-0.29); pitcher suppresses HR (-0.49).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ TB - Parker Messick (L, CLE) vs Drew Rasmussen (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Messick (HR risk -0.85, vs LHB -0.80, vs RHB -0.67). Rasmussen (HR risk -0.28, vs LHB +0.08, vs RHB -0.41).",
        "rows": [
            row("Patrick Bailey", "S", "+850", 71, "⭐ 🌕 💣", ["vs Rasmussen"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.2 mph EV. Rasmussen SHB→LHB split +0.08, HR risk -0.28. pitcher risk below avg (-0.28).""", blast="high"),
        ],
    },
    {
        "title": "COL @ MIL - Kyle Freeland (L, COL) vs Jacob Misiorowski (R, MIL)",
        "description": "Tail key data: Park boost +18% (stadium +10%, weather +8%). Freeland (HR risk 0.68, vs LHB -0.09, vs RHB +0.92). Misiorowski (HR risk -0.25, vs LHB -0.84, vs RHB +0.95).",
        "rows": [
            row("Gary Sanchez", "R", "+204", 82, "", ["vs Freeland"], """1 HR, 1 near-HR, 92.5 mph EV. Freeland RHB split +0.92, HR risk 0.68.""", blast="good"),
            row("Hunter Goodman", "R", "+364", 83, "⭐ 🌕 💣", ["vs Misiorowski"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 87.1 mph EV. Misiorowski RHB split +0.95, HR risk -0.25. pitcher risk below avg (-0.25); lighter EV form (87.1 mph).""", blast="high"),
            row("Kyle Karros", "R", "+910", 61, "", ["vs Misiorowski"], """0 HR, 1 near-HR, 90.9 mph EV. Misiorowski RHB split +0.95, HR risk -0.25. pitcher risk below avg (-0.25); limited recent HR events."""),
        ],
    },
    {
        "title": "HOU @ CWS - Ronel Blanco 🧤 (R, HOU) vs Erick Fedde (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Blanco 🧤 (HR risk 2.77, vs LHB +3.38, vs RHB -0.60). Fedde (HR risk -0.36, vs LHB -0.21, vs RHB -0.15).",
        "rows": [
            row("Munetaka Murakami", "L", "+241", 97, "🌕 💣", ["vs Blanco"], """2 HR, 3 near-HR, 92.9 mph EV. Blanco LHB split +3.38, HR risk 2.77.""", blast="high"),
            row("Randal Grichuk", "R", "N/A", 70, "", ["vs Blanco"], """0 HR, 1 near-HR, 92.8 mph EV. Blanco RHB split -0.60, HR risk 2.77. tough split lane (-0.60); limited recent HR events.""", blast="good"),
            row("Tristan Peters", "L", "+640", 90, "🌕 💣", ["vs Blanco"], """0 HR, 1 near-HR, 93.5 mph EV. Blanco LHB split +3.38, HR risk 2.77. limited recent HR events.""", blast="good"),
            row("Jeremy Pena", "R", "+620", 69, "⭐ 🌕 💣", ["vs Fedde"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.7 mph EV. Fedde RHB split -0.15, HR risk -0.36. slight split headwind (-0.15); pitcher risk below avg (-0.36).""", blast="high"),
            row("Yordan Alvarez", "L", "+219", 58, "", ["vs Fedde"], """0 HR, 91.7 mph EV. Fedde LHB split -0.21, HR risk -0.36. slight split headwind (-0.21); pitcher risk below avg (-0.36)."""),
        ],
    },
    {
        "title": "KC @ DET - Luinder Avila (R, KC) vs Framber Valdez (L, DET)",
        "description": "Tail key data: Park boost -1% (stadium -10%, weather +9%). Avila (HR risk -0.85, vs LHB -0.69, vs RHB -0.08). Valdez (HR risk -0.73, vs LHB -0.45, vs RHB -0.66).",
        "rows": [
            row("Riley Greene", "L", "+363", 63, "⭐ 🌕 💣", ["vs Avila"], """Worst Pickz Favorite. 1 HR, 4 near-HR, 99.2 mph EV. Avila LHB split -0.69, HR risk -0.85. tough split lane (-0.69); pitcher suppresses HR (-0.85).""", blast="high"),
            row("Lane Thomas", "R", "+680", 58, "", ["vs Valdez"], """1 HR, 3 near-HR, 93.6 mph EV. Valdez RHB split -0.66, HR risk -0.73. tough split lane (-0.66); pitcher suppresses HR (-0.73).""", blast="good"),
            row("Salvador Perez", "R", "+466", 58, "", ["vs Valdez"], """1 HR, 1 near-HR, 90.7 mph EV. Valdez RHB split -0.66, HR risk -0.73. tough split lane (-0.66); pitcher suppresses HR (-0.73).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ SF - Jose Soriano (R, LAA) vs Carson Whisenhunt (L, SF)",
        "description": "Tail key data: Park boost -10% (stadium -11%, weather +1%). Soriano (HR risk -0.62, vs LHB +0.13, vs RHB -1.25). Whisenhunt (HR risk -0.20, vs LHB -1.10, vs RHB +0.51).",
        "rows": [
            row("Rafael Devers", "L", "+460", 58, "", ["vs Soriano"], """1 HR, 2 near-HR, 91.9 mph EV. Soriano LHB split +0.13, HR risk -0.62. pitcher suppresses HR (-0.62); park/weather net drag (-10%).""", blast="good"),
            row("Casey Schmitt", "R", "+560", 58, "🌕 💣 💎", ["vs Soriano"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 88.2 mph EV. Soriano RHB split -1.25, HR risk -0.62. tough split lane (-1.25); pitcher suppresses HR (-0.62).""", blast="high"),
            row("Bryce Eldridge", "L", "+531", 68, "⭐ 🌕 💣", ["vs Soriano"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 93.0 mph EV. Soriano LHB split +0.13, HR risk -0.62. pitcher suppresses HR (-0.62); park/weather net drag (-10%).""", blast="high"),
            row("Jorge Soler", "R", "+452", 58, "", ["vs Whisenhunt"], """0 HR, 1 near-HR, 87.2 mph EV. Whisenhunt RHB split +0.51, HR risk -0.20. pitcher risk below avg (-0.20); park/weather net drag (-10%)."""),
            row("Zach Neto", "R", "+412", 62, "", ["vs Whisenhunt"], """1 HR, 2 near-HR, 92.6 mph EV. Whisenhunt RHB split +0.51, HR risk -0.20. pitcher risk below avg (-0.20); park/weather net drag (-10%).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ NYM - Emmet Sheehan (R, LAD) vs Freddy Peralta (R, NYM)",
        "description": "Tail key data: Park boost -1% (stadium -2%, weather +1%). Sheehan (HR risk 0.38, vs LHB +0.45, vs RHB +0.31). Peralta (HR risk -0.11, vs LHB +0.06, vs RHB -0.07).",
        "rows": [
            row("Brett Baty", "L", "N/A", 78, "🌕 💣", ["vs Sheehan"], """2 HR, 2 near-HR, 93.2 mph EV. Sheehan LHB split +0.45, HR risk 0.38.""", blast="high"),
            row("Francisco Lindor", "S", "+450", 67, "", ["vs Sheehan"], """1 HR, 1 near-HR, 92.1 mph EV. Sheehan SHB→LHB split +0.45, HR risk 0.38.""", blast="good"),
            row("Shohei Ohtani", "L", "+263", 58, "", ["vs Peralta"], """0 HR, 97.9 mph EV. Peralta LHB split +0.06, HR risk -0.11. pitcher risk below avg (-0.11); limited recent HR events.""", blast="good"),
            row("Kyle Tucker", "L", "+582", 63, "", ["vs Peralta"], """1 HR, 2 near-HR, 93.6 mph EV. Peralta LHB split +0.06, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ PHI - Will Warren (R, NYY) vs Cristopher Sanchez (L, PHI)",
        "description": "Tail key data: Park boost +18% (stadium +14%, weather +4%). Warren (HR risk 0.62, vs LHB +0.62, vs RHB +0.34). Sanchez (HR risk -0.13, vs LHB -0.95, vs RHB +0.18).",
        "rows": [
            row("Trea Turner", "R", "+508", 80, "", ["vs Warren"], """1 HR, 1 near-HR, 97.3 mph EV. Warren RHB split +0.34, HR risk 0.62.""", blast="good"),
            row("Brandon Marsh", "L", "+600", 81, "", ["vs Warren"], """1 HR, 1 near-HR, 94.6 mph EV. Warren LHB split +0.62, HR risk 0.62.""", blast="good"),
            row("Kyle Schwarber", "L", "+210", 79, "⭐", ["vs Warren"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 99.3 mph EV. Warren LHB split +0.62, HR risk 0.62. limited recent HR events.""", blast="good"),
            row("Derek Hill", "R", "N/A", 73, "", ["vs Warren"], """1 HR, 1 near-HR, 88.6 mph EV. Warren RHB split +0.34, HR risk 0.62.""", blast="good"),
            row("Max Schuemann", "R", "+1180", 65, "", ["vs Sanchez"], """1 HR, 1 near-HR, 92.0 mph EV. Sanchez RHB split +0.18, HR risk -0.13. pitcher risk below avg (-0.13).""", blast="good"),
            row("Jasson Dominguez", "S", "N/A", 63, "", ["vs Sanchez"], """1 HR, 1 near-HR, 89.6 mph EV. Sanchez SHB→RHB split +0.18, HR risk -0.13. pitcher risk below avg (-0.13).""", blast="good"),
            row("Paul Goldschmidt", "R", "+534", 61, "", ["vs Sanchez"], """1 HR, 2 near-HR, 82.1 mph EV. Sanchez RHB split +0.18, HR risk -0.13. pitcher risk below avg (-0.13); lighter EV form (82.1 mph).""", blast="good"),
        ],
    },
    {
        "title": "SD @ MIA - Walker Buehler (R, SD) vs Janson Junk (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -12%, weather +0%). Buehler (HR risk 0.61, vs LHB +0.21, vs RHB +1.10). Junk (HR risk 0.39, vs LHB +0.31, vs RHB +0.41).",
        "rows": [
            row("Joe Mack", "L", "+760", 87, "🌕 💣", ["vs Buehler"], """3 HR, 3 near-HR, 93.8 mph EV. Buehler LHB split +0.21, HR risk 0.61. park/weather net drag (-13%).""", blast="high"),
            row("Griffin Conine", "L", "+533", 89, "⭐ 🌕 💣", ["vs Buehler"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 96.6 mph EV. Buehler LHB split +0.21, HR risk 0.61. park/weather net drag (-13%).""", blast="high"),
            row("Ty France", "R", "+596", 78, "🚀 ⭐ 🌕 💣", ["vs Junk"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.7 mph EV. Junk RHB split +0.41, HR risk 0.39. park/weather net drag (-13%).""", blast="high"),
        ],
    },
    {
        "title": "SEA @ TEX - Logan Gilbert (R, SEA) vs Jacob deGrom (R, TEX)",
        "description": "Tail key data: Park boost -10% (stadium -9%, weather -1%). Gilbert (HR risk -0.36, vs LHB -0.15, vs RHB -0.17). deGrom (HR risk -0.01, vs LHB +0.13, vs RHB -0.04).",
        "rows": [
            row("Jake Burger", "R", "+440", 71, "⭐ 🌕 💣", ["vs Gilbert"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 96.4 mph EV. Gilbert RHB split -0.17, HR risk -0.36. slight split headwind (-0.17); pitcher risk below avg (-0.36).""", blast="high"),
            row("Wyatt Langford", "R", "+568", 60, "", ["vs Gilbert"], """1 HR, 3 near-HR, 92.2 mph EV. Gilbert RHB split -0.17, HR risk -0.36. slight split headwind (-0.17); pitcher risk below avg (-0.36).""", blast="good"),
            row("Ezequiel Duran", "R", "+990", 58, "", ["vs Gilbert"], """1 HR, 1 near-HR, 93.2 mph EV. Gilbert RHB split -0.17, HR risk -0.36. slight split headwind (-0.17); pitcher risk below avg (-0.36).""", blast="good"),
            row("Luke Raley", "L", "+551", 61, "⭐", ["vs deGrom"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.1 mph EV. deGrom LHB split +0.13, HR risk -0.01. pitcher risk below avg (-0.01); park/weather net drag (-10%).""", blast="good"),
            row("Mitch Garver", "R", "N/A", 58, "", ["vs deGrom"], """1 HR, 1 near-HR, 91.4 mph EV. deGrom RHB split -0.04, HR risk -0.01. slight split headwind (-0.04); pitcher risk below avg (-0.01).""", blast="good"),
            row("Randy Arozarena", "R", "+670", 60, "", ["vs deGrom"], """1 HR, 1 near-HR, 94.5 mph EV. deGrom RHB split -0.04, HR risk -0.01. slight split headwind (-0.04); pitcher risk below avg (-0.01).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ BOS - Kevin Gausman (R, TOR) vs Ranger Suarez (L, BOS)",
        "description": "Tail key data: Park boost -6% (stadium -7%, weather +1%). Gausman (HR risk -0.16, vs LHB -0.42, vs RHB +0.51). Suarez (HR risk -1.35, vs LHB +0.10, vs RHB -1.45).",
        "rows": [
            row("Willson Contreras", "R", "+400", 58, "⭐", ["vs Gausman"], """Worst Pickz Favorite. 0 HR, 89.6 mph EV. Gausman RHB split +0.51, HR risk -0.16. pitcher risk below avg (-0.16); park/weather net drag (-6%)."""),
            row("Alejandro Kirk", "R", "+870", 58, "⭐", ["vs Suarez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 89.1 mph EV. Suarez RHB split -1.45, HR risk -1.35. tough split lane (-1.45); pitcher suppresses HR (-1.35).""", blast="good"),
            row("Kazuma Okamoto", "R", "+458", 58, "", ["vs Suarez"], """1 HR, 2 near-HR, 96.8 mph EV. Suarez RHB split -1.45, HR risk -1.35. tough split lane (-1.45); pitcher suppresses HR (-1.35).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-26")

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
