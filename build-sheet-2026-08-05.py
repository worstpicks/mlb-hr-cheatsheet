#!/usr/bin/env python3
"""Generate games[] block for 2026-08-05 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Bryce Harper (L)",
    "Coby Mayo (R)",
    "Daylen Lile (L)",
    "Elly De La Cruz (S)",
    "Francisco Alvarez (R)",
    "Luis Garcia Jr. (L)",
    "Michael Conforto (L)",
    "Munetaka Murakami (L)",
    "Patrick Bailey (S)",
    "Riley Greene (L)",
    "Victor Mesa Jr. (L)",
    "Willson Contreras (R)",
}

GEMS = {
    "Andrew Benintendi (L)",
    "Brady House (R)",
    "Chase DeLauter (L)",
    "Griffin Conine (L)",
    "Henry Bolte (R)",
    "Jake Burger (R)",
    "Jase Bowen (R)",
    "Jazz Chisholm Jr. (L)",
    "Jimmy Crooks (L)",
    "Matt Olson (L)",
    "Pete Alonso (R)",
    "Teoscar Hernandez (R)",
    "Tyrone Taylor (R)",
    "Willi Castro (S)",
}

PLAYER_TEAMS = {
    "Abimelec Ortiz (L)": "WSH",
    "Adley Rutschman (S)": "BOS",
    "Alan Roden (L)": "MIN",
    "Alec Burleson (L)": "STL",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Vaughn (R)": "MIL",
    "Austin Riley (R)": "ATL",
    "Austin Wells (L)": "NYY",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brady House (R)": "WSH",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Brandon Valenzuela (S)": "TOR",
    "Bryan De La Cruz (R)": "PHI",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Carson Benge (L)": "NYM",
    "Cedric Mullins (L)": "TB",
    "Chase DeLauter (L)": "CLE",
    "Coby Mayo (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Dansby Swanson (R)": "CHC",
    "Daylen Lile (L)": "WSH",
    "Derek Hill (R)": "PHI",
    "Dillon Dingler (R)": "DET",
    "Dominic Smith (L)": "ATL",
    "Elly De La Cruz (S)": "CIN",
    "Enrique Hernandez (R)": "LAD",
    "Esmerlyn Valdez (R)": "PIT",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "George Springer (R)": "TOR",
    "Gleyber Torres (R)": "DET",
    "Griffin Conine (L)": "MIA",
    "Henry Bolte (R)": "ATH",
    "Hunter Feduccia (L)": "LAD",
    "Hunter Goodman (R)": "COL",
    "J.T. Realmuto (R)": "PHI",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jacob Gonzalez (L)": "PIT",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jake McCarthy (L)": "COL",
    "Jase Bowen (R)": "SD",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jimmy Crooks (L)": "STL",
    "Jose Siri (R)": "LAA",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Kody Clemens (L)": "MIN",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Kyle Tucker (L)": "LAD",
    "Lawrence Butler (L)": "ATH",
    "Liam Hicks (L)": "TB",
    "Luis Garcia Jr. (L)": "NYY",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Michael Conforto (L)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "STL",
    "Owen Caissie (L)": "MIA",
    "Patrick Bailey (S)": "CLE",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randy Arozarena (R)": "SEA",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Ronald Acuna Jr. (R)": "ATL",
    "Ryan McMahon (L)": "NYY",
    "Seiya Suzuki (R)": "CHC",
    "Shohei Ohtani (L)": "LAD",
    "Taylor Trammell (L)": "HOU",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Tommy Edman (S)": "LAD",
    "Travis Bazzana (L)": "CLE",
    "Travis d'Arnaud (R)": "LAA",
    "Tyler O'Neill (R)": "BAL",
    "Tyler Soderstrom (L)": "ATH",
    "Tyrone Taylor (R)": "CHC",
    "Victor Mesa Jr. (L)": "TB",
    "Willi Castro (S)": "COL",
    "William Contreras (R)": "MIL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
    "Zach Dezenzo (R)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("MIA @ ATL", "Elder"),
    ("MIN @ KC", "Kremer"),
    ("TB @ COL", "Sugano"),
    ("TOR @ HOU", "Taillon"),
    ("WSH @ PHI", "Irvin"),
    ("WSH @ PHI", "Painter"),
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
        "title": "ATH @ CIN - Jacob Lopez (L, ATH) vs Rhett Lowder (R, CIN)",
        "description": "Tail key data: Park boost +22% (stadium +15%, weather +7%). Lopez (HR risk -0.72, vs LHB -1.03, vs RHB -0.24). Lowder (HR risk -0.22, vs LHB +0.44, vs RHB -1.27).",
        "rows": [
            row("Elly De La Cruz", "S", "+300", 79, "⭐ 🌕 💣", ["vs Lopez"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 96.3 mph EV. Lopez SHB→RHB split -0.24, HR risk -0.72. slight split headwind (-0.24); pitcher suppresses HR (-0.72).""", blast="high"),
            row("JJ Bleday", "L", "+360", 70, "🌕 💣", ["vs Lopez"], """3 HR, 3 near-HR, 90.1 mph EV. Lopez LHB split -1.03, HR risk -0.72. tough split lane (-1.03); pitcher suppresses HR (-0.72).""", blast="high"),
            row("Lawrence Butler", "L", "+366", 68, "", ["vs Lowder"], """0 HR, 2 near-HR, 94.8 mph EV. Lowder LHB split +0.44, HR risk -0.22. pitcher risk below avg (-0.22).""", blast="good"),
            row("Henry Bolte", "R", "+600", 63, "💎", ["vs Lowder"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.2 mph EV. Lowder RHB split -1.27, HR risk -0.22. tough split lane (-1.27); pitcher risk below avg (-0.22).""", blast="good"),
            row("Tyler Soderstrom", "L", "+320", 66, "", ["vs Lowder"], """0 HR, 97.2 mph EV. Lowder LHB split +0.44, HR risk -0.22. pitcher risk below avg (-0.22); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ BOS - Sean Burke (R, CWS) vs Sonny Gray (R, BOS)",
        "description": "Tail key data: Park boost data unavailable. Burke (HR risk -0.34, vs LHB -0.17, vs RHB -0.43). Gray (HR risk -0.57, vs LHB -0.43, vs RHB -0.35).",
        "rows": [
            row("Willson Contreras", "R", "+342", 58, "⭐", ["vs Burke"], """Worst Pickz Favorite. 0 HR, 89.0 mph EV. Burke RHB split -0.43, HR risk -0.34. tough split lane (-0.43); pitcher risk below avg (-0.34)."""),
            row("Wilyer Abreu", "L", "+422", 58, "", ["vs Burke"], """1 HR, 1 near-HR, 90.3 mph EV. Burke LHB split -0.17, HR risk -0.34. slight split headwind (-0.17); pitcher risk below avg (-0.34).""", blast="good"),
            row("Adley Rutschman", "S", "N/A", 58, "", ["vs Burke"], """0 HR, 1 near-HR, 96.0 mph EV. Burke SHB→LHB split -0.17, HR risk -0.34. slight split headwind (-0.17); pitcher risk below avg (-0.34).""", blast="good"),
            row("Munetaka Murakami", "L", "+310", 65, "🚀 ⭐ 🌕 💣", ["vs Gray"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.7 mph EV. Gray LHB split -0.43, HR risk -0.57. tough split lane (-0.43); pitcher suppresses HR (-0.57).""", blast="high"),
            row("Andrew Benintendi", "L", "+531", 70, "🌕 💣 💎", ["vs Gray"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 95.6 mph EV. Gray LHB split -0.43, HR risk -0.57. tough split lane (-0.43); pitcher suppresses HR (-0.57).""", blast="high"),
            row("Colson Montgomery", "L", "+373", 58, "", ["vs Gray"], """1 HR, 1 near-HR, 94.5 mph EV. Gray LHB split -0.43, HR risk -0.57. tough split lane (-0.43); pitcher suppresses HR (-0.57).""", blast="good"),
            row("Miguel Vargas", "R", "+373", 58, "🌕 💣", ["vs Gray"], """2 HR, 2 near-HR, 87.8 mph EV. Gray RHB split -0.35, HR risk -0.57. slight split headwind (-0.35); pitcher suppresses HR (-0.57).""", blast="high"),
        ],
    },
    {
        "title": "DET @ SEA - Drew Anderson (R, DET) vs Bryan Woo (R, SEA)",
        "description": "Tail key data: Park boost -3% (stadium +0%, weather -2%). Anderson (HR risk -0.57, vs LHB -0.71, vs RHB +0.22). Woo (HR risk -0.42, vs LHB -0.04, vs RHB -0.59).",
        "rows": [
            row("Julio Rodriguez", "R", "+460", 61, "", ["vs Anderson"], """1 HR, 2 near-HR, 95.0 mph EV. Anderson RHB split +0.22, HR risk -0.57. pitcher suppresses HR (-0.57).""", blast="good"),
            row("Cal Raleigh", "S", "+345", 58, "", ["vs Anderson"], """0 HR, 2 near-HR, 91.8 mph EV. Anderson SHB→RHB split +0.22, HR risk -0.57. pitcher suppresses HR (-0.57).""", blast="good"),
            row("Randy Arozarena", "R", "+500", 58, "", ["vs Anderson"], """0 HR, 1 near-HR, 94.4 mph EV. Anderson RHB split +0.22, HR risk -0.57. pitcher suppresses HR (-0.57); limited recent HR events.""", blast="good"),
            row("Riley Greene", "L", "+336", 66, "⭐", ["vs Woo"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 98.1 mph EV. Woo LHB split -0.04, HR risk -0.42. slight split headwind (-0.04); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Gleyber Torres", "R", "+870", 61, "🌕 💣", ["vs Woo"], """2 HR, 2 near-HR, 92.6 mph EV. Woo RHB split -0.59, HR risk -0.42. tough split lane (-0.59); pitcher suppresses HR (-0.42).""", blast="high"),
            row("Dillon Dingler", "R", "+480", 58, "", ["vs Woo"], """1 HR, 1 near-HR, 84.0 mph EV. Woo RHB split -0.59, HR risk -0.42. tough split lane (-0.59); pitcher suppresses HR (-0.42).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ BAL - Reid Detmers (L, LAA) vs Trevor Rogers (L, BAL)",
        "description": "Tail key data: Park boost +6% (stadium -8%, weather +14%). Detmers (HR risk 0.46, vs LHB +0.22, vs RHB +0.39). Rogers (HR risk -0.82, vs LHB -1.38, vs RHB -0.43).",
        "rows": [
            row("Coby Mayo", "R", "+301", 92, "🚀 ⭐ 🌕 💣", ["vs Detmers"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 103.0 mph EV. Detmers RHB split +0.39, HR risk 0.46. park suppresses carry (-8%).""", blast="high"),
            row("Pete Alonso", "R", "+285", 83, "🌕 💣 💎", ["vs Detmers"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.5 mph EV. Detmers RHB split +0.39, HR risk 0.46. park suppresses carry (-8%).""", blast="high"),
            row("Tyler O'Neill", "R", "+331", 82, "🌕 💣", ["vs Detmers"], """2 HR, 2 near-HR, 92.7 mph EV. Detmers RHB split +0.39, HR risk 0.46. park suppresses carry (-8%).""", blast="high"),
            row("Jose Siri", "R", "+448", 61, "🌕 💣", ["vs Rogers"], """2 HR, 2 near-HR, 92.4 mph EV. Rogers RHB split -0.43, HR risk -0.82. tough split lane (-0.43); pitcher suppresses HR (-0.82).""", blast="high"),
            row("Zach Neto", "R", "+367", 58, "", ["vs Rogers"], """0 HR, 85.7 mph EV. Rogers RHB split -0.43, HR risk -0.82. tough split lane (-0.43); pitcher suppresses HR (-0.82)."""),
            row("Travis d'Arnaud", "R", "+520", 58, "", ["vs Rogers"], """1 HR, 1 near-HR, 86.9 mph EV. Rogers RHB split -0.43, HR risk -0.82. tough split lane (-0.43); pitcher suppresses HR (-0.82).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ CHC - Eric Lauer (L, LAD) vs Shota Imanaga (L, CHC)",
        "description": "Tail key data: Park boost +23% (stadium +0%, weather +23%). Lauer (HR risk 0.17, vs LHB -0.31, vs RHB +0.57). Imanaga (HR risk -0.07, vs LHB +0.62, vs RHB -0.14).",
        "rows": [
            row("Tyrone Taylor", "R", "+465", 82, "🌕 💣 💎", ["vs Lauer"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 92.2 mph EV. Lauer RHB split +0.57, HR risk 0.17.""", blast="high"),
            row("Seiya Suzuki", "R", "+330", 76, "🌕 💣", ["vs Lauer"], """2 HR, 2 near-HR, 85.7 mph EV. Lauer RHB split +0.57, HR risk 0.17. lighter EV form (85.7 mph).""", blast="high"),
            row("Dansby Swanson", "R", "+421", 73, "", ["vs Lauer"], """1 HR, 1 near-HR, 92.3 mph EV. Lauer RHB split +0.57, HR risk 0.17.""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+362", 58, "", ["vs Lauer"], """0 HR, 84.1 mph EV. Lauer LHB split -0.31, HR risk 0.17. slight split headwind (-0.31); limited recent HR events."""),
            row("Michael Conforto", "L", "N/A", 79, "⭐ 🌕 💣", ["vs Lauer"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.3 mph EV. Lauer LHB split -0.31, HR risk 0.17. slight split headwind (-0.31).""", blast="high"),
            row("Enrique Hernandez", "R", "N/A", 68, "", ["vs Imanaga"], """1 HR, 1 near-HR, 96.9 mph EV. Imanaga RHB split -0.14, HR risk -0.07. slight split headwind (-0.14); pitcher risk below avg (-0.07).""", blast="good"),
            row("Kyle Tucker", "L", "+515", 75, "", ["vs Imanaga"], """1 HR, 3 near-HR, 90.5 mph EV. Imanaga LHB split +0.62, HR risk -0.07. pitcher risk below avg (-0.07).""", blast="good"),
            row("Hunter Feduccia", "L", "+800", 68, "", ["vs Imanaga"], """0 HR, 1 near-HR, 93.4 mph EV. Imanaga LHB split +0.62, HR risk -0.07. pitcher risk below avg (-0.07); limited recent HR events.""", blast="good"),
            row("Tommy Edman", "S", "+450", 71, "", ["vs Imanaga"], """1 HR, 1 near-HR, 92.9 mph EV. Imanaga SHB→LHB split +0.62, HR risk -0.07. pitcher risk below avg (-0.07).""", blast="good"),
            row("Teoscar Hernandez", "R", "+448", 68, "💎", ["vs Imanaga"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.6 mph EV. Imanaga RHB split -0.14, HR risk -0.07. slight split headwind (-0.14); pitcher risk below avg (-0.07).""", blast="good"),
            row("Shohei Ohtani", "L", "+220", 67, "", ["vs Imanaga"], """1 HR, 1 near-HR, 88.6 mph EV. Imanaga LHB split +0.62, HR risk -0.07. pitcher risk below avg (-0.07).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ ATL - Eury Perez (R, MIA) vs Bryce Elder 🧤 (R, ATL)",
        "description": "Tail key data: Park boost +4% (stadium -1%, weather +5%). Perez (HR risk -0.85, vs LHB -0.89, vs RHB -0.29). Elder 🧤 (HR risk 1.01, vs LHB +0.83, vs RHB +0.99).",
        "rows": [
            row("Matt Olson", "L", "+339", 62, "🌕 💣 💎", ["vs Perez"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 97.1 mph EV. Perez LHB split -0.89, HR risk -0.85. tough split lane (-0.89); pitcher suppresses HR (-0.85).""", blast="high"),
            row("Dominic Smith", "L", "N/A", 64, "🌕 💣", ["vs Perez"], """2 HR, 3 near-HR, 93.0 mph EV. Perez LHB split -0.89, HR risk -0.85. tough split lane (-0.89); pitcher suppresses HR (-0.85).""", blast="high"),
            row("Ronald Acuna Jr.", "R", "+390", 58, "", ["vs Perez"], """1 HR, 2 near-HR, 95.6 mph EV. Perez RHB split -0.29, HR risk -0.85. slight split headwind (-0.29); pitcher suppresses HR (-0.85).""", blast="good"),
            row("Austin Riley", "R", "+520", 58, "", ["vs Perez"], """0 HR, 95.1 mph EV. Perez RHB split -0.29, HR risk -0.85. slight split headwind (-0.29); pitcher suppresses HR (-0.85).""", blast="good"),
            row("Griffin Conine", "L", "+429", 86, "💎", ["vs Elder"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.7 mph EV. Elder LHB split +0.83, HR risk 1.01.""", blast="good"),
            row("Kyle Stowers", "L", "+328", 86, "", ["vs Elder"], """1 HR, 1 near-HR, 95.8 mph EV. Elder LHB split +0.83, HR risk 1.01.""", blast="good"),
            row("Owen Caissie", "L", "+464", 92, "🌕 💣", ["vs Elder"], """2 HR, 2 near-HR, 95.6 mph EV. Elder LHB split +0.83, HR risk 1.01.""", blast="high"),
        ],
    },
    {
        "title": "MIN @ KC - Dean Kremer 🧤 (R, MIN) vs Noah Cameron (L, KC)",
        "description": "Tail key data: Park boost +19% (stadium +11%, weather +8%). Kremer 🧤 (HR risk 0.98, vs LHB +0.80, vs RHB +1.12). Cameron (HR risk -0.13, vs LHB +0.08, vs RHB -0.07).",
        "rows": [
            row("Jac Caglianone", "L", "+370", 88, "🌕 💣", ["vs Kremer"], """1 HR, 1 near-HR, 94.9 mph EV. Kremer LHB split +0.80, HR risk 0.98.""", blast="good"),
            row("Bobby Witt Jr.", "R", "+369", 85, "", ["vs Kremer"], """0 HR, 1 near-HR, 92.6 mph EV. Kremer RHB split +1.12, HR risk 0.98. limited recent HR events.""", blast="good"),
            row("Kody Clemens", "L", "+454", 61, "", ["vs Cameron"], """1 HR, 1 near-HR, 87.9 mph EV. Cameron LHB split +0.08, HR risk -0.13. pitcher risk below avg (-0.13); lighter EV form (87.9 mph).""", blast="good"),
            row("Alan Roden", "L", "N/A", 62, "", ["vs Cameron"], """0 HR, 94.6 mph EV. Cameron LHB split +0.08, HR risk -0.13. pitcher risk below avg (-0.13); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "NYM @ CLE - Christian Scott (R, NYM) vs Tanner Bibee (R, CLE)",
        "description": "Tail key data: Park boost -2% (stadium -3%, weather +1%). Scott (HR risk -0.75, vs LHB -0.23, vs RHB -1.06). Bibee (HR risk -0.45, vs LHB -0.02, vs RHB -0.81).",
        "rows": [
            row("Patrick Bailey", "S", "+930", 65, "⭐ 🌕 💣", ["vs Scott"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.6 mph EV. Scott SHB→LHB split -0.23, HR risk -0.75. slight split headwind (-0.23); pitcher suppresses HR (-0.75).""", blast="high"),
            row("Chase DeLauter", "L", "+502", 58, "💎", ["vs Scott"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.2 mph EV. Scott LHB split -0.23, HR risk -0.75. slight split headwind (-0.23); pitcher suppresses HR (-0.75).""", blast="good"),
            row("Rhys Hoskins", "R", "N/A", 60, "🌕 💣", ["vs Scott"], """2 HR, 2 near-HR, 93.8 mph EV. Scott RHB split -1.06, HR risk -0.75. tough split lane (-1.06); pitcher suppresses HR (-0.75).""", blast="high"),
            row("Travis Bazzana", "L", "+770", 58, "", ["vs Scott"], """0 HR, 1 near-HR, 87.9 mph EV. Scott LHB split -0.23, HR risk -0.75. slight split headwind (-0.23); pitcher suppresses HR (-0.75)."""),
            row("Carson Benge", "L", "+554", 58, "", ["vs Bibee"], """1 HR, 1 near-HR, 91.5 mph EV. Bibee LHB split -0.02, HR risk -0.45. slight split headwind (-0.02); pitcher suppresses HR (-0.45).""", blast="good"),
            row("Francisco Alvarez", "R", "+560", 58, "⭐", ["vs Bibee"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 92.0 mph EV. Bibee RHB split -0.81, HR risk -0.45. tough split lane (-0.81); pitcher suppresses HR (-0.45).""", blast="good"),
            row("Francisco Lindor", "S", "+400", 58, "", ["vs Bibee"], """1 HR, 1 near-HR, 93.2 mph EV. Bibee SHB→LHB split -0.02, HR risk -0.45. slight split headwind (-0.02); pitcher suppresses HR (-0.45).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ MIL - Paul Skenes (R, PIT) vs Kyle Harrison (L, MIL)",
        "description": "Tail key data: Park boost +6% (stadium +10%, weather -4%). Skenes (HR risk -0.61, vs LHB -0.42, vs RHB -0.36). Harrison (HR risk -0.26, vs LHB -0.72, vs RHB +0.07).",
        "rows": [
            row("Jackson Chourio", "R", "+450", 58, "", ["vs Skenes"], """1 HR, 1 near-HR, 91.9 mph EV. Skenes RHB split -0.36, HR risk -0.61. slight split headwind (-0.36); pitcher suppresses HR (-0.61).""", blast="good"),
            row("Andrew Vaughn", "R", "+660", 59, "", ["vs Skenes"], """1 HR, 2 near-HR, 95.6 mph EV. Skenes RHB split -0.36, HR risk -0.61. slight split headwind (-0.36); pitcher suppresses HR (-0.61).""", blast="good"),
            row("Jake Bauers", "L", "N/A", 58, "", ["vs Skenes"], """0 HR, 1 near-HR, 96.8 mph EV. Skenes LHB split -0.42, HR risk -0.61. tough split lane (-0.42); pitcher suppresses HR (-0.61).""", blast="good"),
            row("William Contreras", "R", "+536", 58, "", ["vs Skenes"], """0 HR, 1 near-HR, 88.8 mph EV. Skenes RHB split -0.36, HR risk -0.61. slight split headwind (-0.36); pitcher suppresses HR (-0.61)."""),
            row("Bryan Reynolds", "S", "+408", 58, "", ["vs Harrison"], """0 HR, 91.9 mph EV. Harrison SHB→RHB split +0.07, HR risk -0.26. pitcher risk below avg (-0.26); weather carry headwind (-4%)."""),
            row("Brandon Lowe", "L", "+435", 58, "", ["vs Harrison"], """1 HR, 2 near-HR, 93.9 mph EV. Harrison LHB split -0.72, HR risk -0.26. tough split lane (-0.72); pitcher risk below avg (-0.26).""", blast="good"),
            row("Jacob Gonzalez", "L", "N/A", 58, "🚀", ["vs Harrison"], """0 HR, 102.7 mph EV. Harrison LHB split -0.72, HR risk -0.26. tough split lane (-0.72); pitcher risk below avg (-0.26).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+320", 61, "", ["vs Harrison"], """1 HR, 1 near-HR, 92.8 mph EV. Harrison RHB split +0.07, HR risk -0.26. pitcher risk below avg (-0.26); weather carry headwind (-4%).""", blast="good"),
        ],
    },
    {
        "title": "SD @ ARI - Casey Mize (R, SD) vs Mitch Bratt (L, ARI)",
        "description": "Tail key data: Park boost -9% (stadium -8%, weather +0%). Mize (HR risk -0.95, vs LHB -0.96, vs RHB -0.31). Bratt (HR risk 0.22, vs LHB +0.99, vs RHB -0.09).",
        "rows": [
            row("Corbin Carroll", "L", "+416", 58, "", ["vs Mize"], """1 HR, 1 near-HR, 96.8 mph EV. Mize LHB split -0.96, HR risk -0.95. tough split lane (-0.96); pitcher suppresses HR (-0.95).""", blast="good"),
            row("Tim Tawa", "R", "+750", 58, "", ["vs Mize"], """1 HR, 2 near-HR, 81.7 mph EV. Mize RHB split -0.31, HR risk -0.95. slight split headwind (-0.31); pitcher suppresses HR (-0.95).""", blast="good"),
            row("Jase Bowen", "R", "+830", 58, "💎", ["vs Bratt"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.3 mph EV. Bratt RHB split -0.09, HR risk 0.22. slight split headwind (-0.09); park/weather net drag (-9%).""", blast="good"),
            row("Jackson Merrill", "L", "+537", 66, "", ["vs Bratt"], """0 HR, 95.0 mph EV. Bratt LHB split +0.99, HR risk 0.22. park/weather net drag (-9%); limited recent HR events.""", blast="good"),
            row("Manny Machado", "R", "+353", 58, "", ["vs Bratt"], """0 HR, 92.8 mph EV. Bratt RHB split -0.09, HR risk 0.22. slight split headwind (-0.09); park/weather net drag (-9%).""", blast="good"),
        ],
    },
    {
        "title": "SF @ TEX - Carson Whisenhunt (L, SF) vs Cody Bradford (L, TEX)",
        "description": "Tail key data: Park boost -12% (stadium -11%, weather -1%). Whisenhunt (HR risk 0.94, vs LHB -1.56, vs RHB +1.68). Bradford (HR risk 0.00, vs LHB +0.00, vs RHB +0.00).",
        "rows": [
            row("Jake Burger", "R", "+390", 88, "🌕 💣 💎", ["vs Whisenhunt"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 96.8 mph EV. Whisenhunt RHB split +1.68, HR risk 0.94. park/weather net drag (-12%).""", blast="good"),
            row("Brandon Nimmo", "L", "+502", 73, "🌕 💣", ["vs Whisenhunt"], """2 HR, 2 near-HR, 91.5 mph EV. Whisenhunt LHB split -1.56, HR risk 0.94. tough split lane (-1.56); park/weather net drag (-12%).""", blast="high"),
            row("Wyatt Langford", "R", "+390", 79, "", ["vs Whisenhunt"], """1 HR, 2 near-HR, 87.4 mph EV. Whisenhunt RHB split +1.68, HR risk 0.94. park/weather net drag (-12%); lighter EV form (87.4 mph).""", blast="good"),
            row("Corey Seager", "L", "+460", 59, "", ["vs Whisenhunt"], """1 HR, 1 near-HR, 86.7 mph EV. Whisenhunt LHB split -1.56, HR risk 0.94. tough split lane (-1.56); park/weather net drag (-12%).""", blast="good"),
            row("Rafael Devers", "L", "+340", 58, "", ["vs Bradford"], """1 HR, 2 near-HR, 90.6 mph EV. Bradford LHB split +0.00, HR risk 0.00. park/weather net drag (-12%).""", blast="good"),
            row("Bryce Eldridge", "L", "+453", 68, "", ["vs Bradford"], """1 HR, 3 near-HR, 96.0 mph EV. Bradford LHB split +0.00, HR risk 0.00. park/weather net drag (-12%).""", blast="good"),
        ],
    },
    {
        "title": "STL @ NYY - Andre Pallante (R, STL) vs Will Warren (R, NYY)",
        "description": "Tail key data: Park boost +13% (stadium +4%, weather +8%). Pallante (HR risk -1.18, vs LHB -0.51, vs RHB -1.29). Warren (HR risk 0.60, vs LHB +0.58, vs RHB +0.33).",
        "rows": [
            row("Jazz Chisholm Jr.", "L", "+400", 63, "🚀 🌕 💣 💎", ["vs Pallante"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 100.6 mph EV. Pallante LHB split -0.51, HR risk -1.18. tough split lane (-0.51); pitcher suppresses HR (-1.18).""", blast="high"),
            row("Luis Garcia Jr.", "L", "+430", 58, "⭐", ["vs Pallante"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.4 mph EV. Pallante LHB split -0.51, HR risk -1.18. tough split lane (-0.51); pitcher suppresses HR (-1.18).""", blast="good"),
            row("Austin Wells", "L", "N/A", 58, "", ["vs Pallante"], """0 HR, 93.0 mph EV. Pallante LHB split -0.51, HR risk -1.18. tough split lane (-0.51); pitcher suppresses HR (-1.18).""", blast="good"),
            row("Ben Rice", "L", "+315", 63, "🌕 💣", ["vs Pallante"], """2 HR, 2 near-HR, 98.7 mph EV. Pallante LHB split -0.51, HR risk -1.18. tough split lane (-0.51); pitcher suppresses HR (-1.18).""", blast="high"),
            row("Ryan McMahon", "L", "+520", 58, "", ["vs Pallante"], """1 HR, 1 near-HR, 96.2 mph EV. Pallante LHB split -0.51, HR risk -1.18. tough split lane (-0.51); pitcher suppresses HR (-1.18).""", blast="good"),
            row("Jimmy Crooks", "L", "+520", 92, "🚀 🌕 💣 💎", ["vs Warren"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 100.0 mph EV. Warren LHB split +0.58, HR risk 0.60.""", blast="high"),
            row("Alec Burleson", "L", "+323", 82, "⭐", ["vs Warren"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.4 mph EV. Warren LHB split +0.58, HR risk 0.60.""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 75, "", ["vs Warren"], """0 HR, 1 near-HR, 96.5 mph EV. Warren RHB split +0.33, HR risk 0.60. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TB @ COL - Nick Martinez (R, TB) vs Tomoyuki Sugano 🧤 (R, COL)",
        "description": "Tail key data: Park boost +30% (stadium +17%, weather +13%). Martinez (HR risk -0.14, vs LHB +0.27, vs RHB -0.60). Sugano 🧤 (HR risk 0.97, vs LHB +1.11, vs RHB +0.41).",
        "rows": [
            row("Willi Castro", "S", "+680", 81, "🌕 💣 💎", ["vs Martinez"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 87.0 mph EV. Martinez SHB→LHB split +0.27, HR risk -0.14. pitcher risk below avg (-0.14); lighter EV form (87.0 mph).""", blast="high"),
            row("Jake McCarthy", "L", "+810", 58, "", ["vs Martinez"], """0 HR, 1 near-HR, 85.1 mph EV. Martinez LHB split +0.27, HR risk -0.14. pitcher risk below avg (-0.14); limited recent HR events."""),
            row("Kyle Karros", "R", "+600", 60, "", ["vs Martinez"], """0 HR, 96.6 mph EV. Martinez RHB split -0.60, HR risk -0.14. tough split lane (-0.60); pitcher risk below avg (-0.14).""", blast="good"),
            row("Hunter Goodman", "R", "+300", 66, "", ["vs Martinez"], """1 HR, 2 near-HR, 94.2 mph EV. Martinez RHB split -0.60, HR risk -0.14. tough split lane (-0.60); pitcher risk below avg (-0.14).""", blast="good"),
            row("Junior Caminero", "R", "+233", 95, "🌕 💣", ["vs Sugano"], """2 HR, 3 near-HR, 95.7 mph EV. Sugano RHB split +0.41, HR risk 0.97.""", blast="high"),
            row("Victor Mesa Jr.", "L", "+348", 85, "⭐", ["vs Sugano"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 88.6 mph EV. Sugano LHB split +1.11, HR risk 0.97.""", blast="good"),
            row("Cedric Mullins", "L", "+400", 86, "", ["vs Sugano"], """1 HR, 2 near-HR, 85.3 mph EV. Sugano LHB split +1.11, HR risk 0.97. lighter EV form (85.3 mph).""", blast="good"),
            row("Liam Hicks", "L", "+560", 88, "🌕 💣", ["vs Sugano"], """1 HR, 1 near-HR, 89.7 mph EV. Sugano LHB split +1.11, HR risk 0.97.""", blast="good"),
        ],
    },
    {
        "title": "TOR @ HOU - Jameson Taillon 🧤 (R, TOR) vs Hunter Brown (R, HOU)",
        "description": "Tail key data: Park boost +6% (stadium +6%, weather -1%). Taillon 🧤 (HR risk 1.95, vs LHB +1.32, vs RHB +2.11). Brown (HR risk -0.40, vs LHB +0.21, vs RHB -0.88).",
        "rows": [
            row("Yordan Alvarez", "L", "+304", 81, "", ["vs Taillon"], """0 HR, 91.5 mph EV. Taillon LHB split +1.32, HR risk 1.95. limited recent HR events."""),
            row("Taylor Trammell", "L", "+780", 97, "🌕 💣", ["vs Taillon"], """2 HR, 3 near-HR, 97.3 mph EV. Taillon LHB split +1.32, HR risk 1.95.""", blast="high"),
            row("Zach Dezenzo", "R", "N/A", 90, "🌕 💣", ["vs Taillon"], """0 HR, 1 near-HR, 92.2 mph EV. Taillon RHB split +2.11, HR risk 1.95. limited recent HR events.""", blast="good"),
            row("Brandon Valenzuela", "S", "+800", 58, "", ["vs Brown"], """1 HR, 2 near-HR, 87.0 mph EV. Brown SHB→LHB split +0.21, HR risk -0.40. pitcher suppresses HR (-0.40); lighter EV form (87.0 mph).""", blast="good"),
            row("George Springer", "R", "+560", 58, "", ["vs Brown"], """1 HR, 2 near-HR, 93.4 mph EV. Brown RHB split -0.88, HR risk -0.40. tough split lane (-0.88); pitcher suppresses HR (-0.40).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ PHI - Jake Irvin 🧤 (R, WSH) vs Andrew Painter 🧤 (R, PHI)",
        "description": "Tail key data: Park boost data unavailable. Irvin 🧤 (HR risk 0.98, vs LHB +0.63, vs RHB +1.02). Painter 🧤 (HR risk 1.19, vs LHB +1.27, vs RHB +0.33).",
        "rows": [
            row("Bryce Harper", "L", "+240", 93, "⭐ 🌕 💣", ["vs Irvin"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 99.8 mph EV. Irvin LHB split +0.63, HR risk 0.98.""", blast="high"),
            row("Derek Hill", "R", "N/A", 84, "", ["vs Irvin"], """1 HR, 1 near-HR, 93.7 mph EV. Irvin RHB split +1.02, HR risk 0.98.""", blast="good"),
            row("Bryson Stott", "L", "+586", 83, "", ["vs Irvin"], """1 HR, 1 near-HR, 96.7 mph EV. Irvin LHB split +0.63, HR risk 0.98.""", blast="good"),
            row("Kyle Schwarber", "L", "+200", 77, "", ["vs Irvin"], """0 HR, 95.6 mph EV. Irvin LHB split +0.63, HR risk 0.98. limited recent HR events.""", blast="good"),
            row("Bryan De La Cruz", "R", "N/A", 86, "", ["vs Irvin"], """1 HR, 1 near-HR, 95.7 mph EV. Irvin RHB split +1.02, HR risk 0.98.""", blast="good"),
            row("J.T. Realmuto", "R", "+630", 82, "", ["vs Irvin"], """0 HR, 1 near-HR, 96.9 mph EV. Irvin RHB split +1.02, HR risk 0.98. limited recent HR events.""", blast="good"),
            row("Daylen Lile", "L", "+417", 92, "⭐ 🌕 💣", ["vs Painter"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 89.9 mph EV. Painter LHB split +1.27, HR risk 1.19.""", blast="high"),
            row("Brady House", "R", "N/A", 77, "💎", ["vs Painter"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 92.2 mph EV. Painter RHB split +0.33, HR risk 1.19.""", blast="good"),
            row("Abimelec Ortiz", "L", "+450", 85, "", ["vs Painter"], """0 HR, 98.6 mph EV. Painter LHB split +1.27, HR risk 1.19. limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-05")

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

    out = ROOT / '_games-0805.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
