#!/usr/bin/env python3
"""Generate games[] block for 2026-09-14 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Bryce Eldridge (L)",
    "Coby Mayo (R)",
    "Dominic Canzone (L)",
    "Elly De La Cruz (S)",
    "Fernando Tatis Jr. (R)",
    "Francisco Lindor (S)",
    "Jackson Merrill (L)",
    "Josh Bell (S)",
    "Kazuma Okamoto (R)",
    "Pete Crow Armstrong (L)",
    "Sal Stewart (R)",
    "Spencer Jones (L)",
    "Spencer Torkelson (R)",
    "Zach Neto (R)",
}

GEMS = {
    "Brett Bateman (L)",
    "Corbin Carroll (L)",
    "Francisco Alvarez (R)",
    "Joshua Baez (R)",
    "Kody Clemens (L)",
    "Lars Nootbaar (L)",
    "Luis Garcia Jr. (L)",
    "Marcus Semien (R)",
    "Max Muncy (L)",
    "Otto Lopez (R)",
    "Royce Lewis (R)",
    "Teoscar Hernandez (R)",
    "Ty France (R)",
    "Tyler Stephenson (R)",
}

PLAYER_TEAMS = {
    "A.J. Ewing (L)": "NYM",
    "Aaron Judge (R)": "NYY",
    "Adael Amador (S)": "COL",
    "Alec Burleson (L)": "STL",
    "Andrew Benintendi (L)": "CWS",
    "Angel Martinez (S)": "CLE",
    "Ben Rice (L)": "NYY",
    "Brett Bateman (L)": "TOR",
    "Brett Baty (L)": "NYM",
    "Brett Callahan (L)": "DET",
    "Bryce Eldridge (L)": "SF",
    "Chase DeLauter (L)": "CLE",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Christian Moore (R)": "LAA",
    "Coby Mayo (R)": "BAL",
    "Cole Young (L)": "SEA",
    "Corbin Carroll (L)": "ARI",
    "Dominic Canzone (L)": "SEA",
    "Elly De La Cruz (S)": "CIN",
    "Emmanuel Rodriguez (L)": "MIN",
    "Enrique Hernandez (R)": "LAD",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Freddy Fermin (R)": "SD",
    "George Springer (R)": "TOR",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Jackson Merrill (L)": "SD",
    "Jake McCarthy (L)": "COL",
    "Jake Rogers (R)": "CWS",
    "Jo Adell (R)": "CLE",
    "Joe Mack (L)": "MIA",
    "Jordan Walker (R)": "STL",
    "Josh Bell (S)": "MIN",
    "Josh Smith (L)": "TOR",
    "Joshua Baez (R)": "STL",
    "Juan Brito (S)": "CIN",
    "Kazuma Okamoto (R)": "TOR",
    "Kevin McGonigle (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Kyle Stowers (L)": "MIA",
    "Kyle Teel (L)": "CWS",
    "Lars Nootbaar (L)": "ARI",
    "Leonardo Bernal (S)": "STL",
    "Luis Garcia Jr. (L)": "NYY",
    "Marcus Semien (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Max Clark (L)": "DET",
    "Max Muncy (L)": "LAD",
    "Otto Lopez (R)": "MIA",
    "Patrick Bailey (S)": "CLE",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Randal Grichuk (R)": "CWS",
    "Randy Arozarena (R)": "SEA",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Sal Stewart (R)": "CIN",
    "Seiya Suzuki (R)": "CHC",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "TJ Rumfield (L)": "COL",
    "Teoscar Hernandez (R)": "LAD",
    "Thomas Saggese (R)": "STL",
    "Tim Tawa (R)": "ARI",
    "Ty France (R)": "SD",
    "Tyler Stephenson (R)": "CIN",
    "Will Smith (R)": "LAD",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("CWS @ CLE", "Williams"),
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
        "title": "ATL @ CHC - Reynaldo Lopez (R, ATL) vs David Peterson (L, CHC)",
        "kLines": {'Lopez': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 20.3, 'matchupK': 20.2, 'ownK': 22.7}, 'Peterson': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 21.7, 'matchupK': 21.7, 'ownK': 21.7}},
        "description": "Tail key data: Park boost +14% (stadium -2%, weather +16%). Lopez (HR risk 0.45, vs LHB +0.94, vs RHB -0.17). Peterson (HR risk -0.32, vs LHB -0.77, vs RHB -0.01).",
        "rows": [
            row("Pete Crow Armstrong", "L", "+260", 93, "🚀 ⭐ 🌕 💣", ["vs Lopez"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 100.3 mph EV, 25.0% barrels. Lopez LHB split +0.94, HR risk 0.45. limited recent HR events.""", blast="high", contact={'stars': 3, 'k': 22.7, 'batterK': 23.7, 'batterWhiff': 24.1, 'pitcherK': 22.7}),
            row("Seiya Suzuki", "R", "+390", 81, "", ["vs Lopez"], """0 HR, 93.0 mph EV, 37.5% barrels. Lopez RHB split -0.17, HR risk 0.45. slight split headwind (-0.17); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 17.7, 'batterK': 12.1, 'batterWhiff': 16.0, 'pitcherK': 22.7}),
            row("Ian Happ", "S", "+520", 76, "", ["vs Lopez"], """0 HR, 92.8 mph EV. Lopez SHB→LHB split +0.94, HR risk 0.45. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 27.8, 'batterWhiff': 24.3, 'pitcherK': 22.7}),
            row("Ronald Acuna Jr.", "R", "+420", 59, "", ["vs Peterson"], """0 HR, 91.5 mph EV. Peterson RHB split -0.01, HR risk -0.32. slight split headwind (-0.01); pitcher risk below avg (-0.32).""", contact={'stars': 3, 'k': 21.3, 'batterK': 18.4, 'batterWhiff': 27.4, 'pitcherK': 21.7}),
            row("Matt Olson", "L", "+377", 72, "", ["vs Peterson"], """1 HR, 1 near-HR, 90.5 mph EV, 12.5% barrels. Peterson LHB split -0.77, HR risk -0.32. tough split lane (-0.77); pitcher risk below avg (-0.32).""", blast="good", contact={'stars': 3, 'k': 22.4, 'batterK': 22.4, 'batterWhiff': 27.5, 'pitcherK': 21.7}),
        ],
    },
    {
        "title": "BAL @ NYM - Brandon Young (R, BAL) vs Jonah Tong (R, NYM)",
        "kLines": {'Young': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 23.7, 'matchupK': 19.3, 'ownK': 18.6}, 'Tong': {'k': 4.8, 'lo': 3, 'hi': 6, 'bf': 21.6, 'matchupK': 22.2, 'ownK': 20.6}},
        "description": "Tail key data: Park boost -10% (stadium -2%, weather -9%). Young (HR risk 0.73, vs LHB +0.64, vs RHB +0.66). Tong (HR risk 0.01, vs LHB -0.57, vs RHB +0.70).",
        "rows": [
            row("Marcus Semien", "R", "+730", 69, "💎", ["vs Young"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.5 mph EV, 25.0% barrels. Young RHB split +0.66, HR risk 0.73. park/weather net drag (-10%); limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 16.5, 'batterK': 9.9, 'batterWhiff': 20.3, 'pitcherK': 18.6}),
            row("Francisco Lindor", "S", "+425", 95, "⭐ 🌕 💣", ["vs Young"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 92.5 mph EV, 12.5% barrels. Young SHB→LHB split +0.64, HR risk 0.73. park/weather net drag (-10%).""", blast="high", contact={'stars': 3, 'k': 21.0, 'batterK': 23.7, 'batterWhiff': 26.7, 'pitcherK': 18.6}),
            row("Francisco Alvarez", "R", "+596", 86, "💎", ["vs Young"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.2 mph EV, 12.5% barrels. Young RHB split +0.66, HR risk 0.73. park/weather net drag (-10%).""", blast="good", contact={'stars': 1, 'k': 27.8, 'batterK': 44.4, 'batterWhiff': 41.4, 'pitcherK': 18.6}),
            row("A.J. Ewing", "L", "+820", 71, "", ["vs Young"], """1 HR, 1 near-HR, 89.6 mph EV, 12.5% barrels. Young LHB split +0.64, HR risk 0.73. park/weather net drag (-10%).""", blast="good", contact={'stars': 4, 'k': 19.3, 'batterK': 20.5, 'batterWhiff': 22.0, 'pitcherK': 18.6}),
            row("Brett Baty", "L", "+790", 82, "", ["vs Young"], """1 HR, 2 near-HR, 94.2 mph EV, 12.5% barrels. Young LHB split +0.64, HR risk 0.73. park/weather net drag (-10%).""", blast="good", contact={'stars': 3, 'k': 20.9, 'batterK': 18.5, 'batterWhiff': 30.5, 'pitcherK': 18.6}),
            row("Coby Mayo", "R", "+380", 77, "⭐", ["vs Tong"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.7 mph EV, 12.5% barrels. Tong RHB split +0.70, HR risk 0.01. park/weather net drag (-10%).""", blast="good", contact={'stars': 3, 'k': 22.4, 'batterK': 25.0, 'batterWhiff': 24.8, 'pitcherK': 20.6}),
            row("Christian Encarnacion-Strand", "R", "+442", 60, "", ["vs Tong"], """0 HR, 94.5 mph EV. Tong RHB split +0.70, HR risk 0.01. park/weather net drag (-10%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.8, 'batterK': 27.0, 'batterWhiff': 29.7, 'pitcherK': 20.6}),
            row("Pete Alonso", "R", "+274", 78, "", ["vs Tong"], """1 HR, 1 near-HR, 81.4 mph EV, 12.5% barrels. Tong RHB split +0.70, HR risk 0.01. park/weather net drag (-10%); lighter EV form (81.4 mph).""", blast="good", contact={'stars': 3, 'k': 22.5, 'batterK': 23.6, 'batterWhiff': 26.6, 'pitcherK': 20.6}),
        ],
    },
    {
        "title": "CWS @ CLE - Sean Burke (R, CWS) vs Gavin Williams 🧤 (R, CLE)",
        "kLines": {'Burke': {'k': 4.8, 'lo': 3, 'hi': 6, 'bf': 22.2, 'matchupK': 21.8, 'ownK': 25.2}, 'Williams': {'k': 8.9, 'lo': 7, 'hi': 11, 'bf': 23.2, 'matchupK': 38.4, 'ownK': 42.5}},
        "description": "Tail key data: Park boost -27% (stadium -2%, weather -25%). Burke (BAA vs LHB .234, vs RHB .214, HR/9 1.20 vs LHB, 0.83 vs RHB). Williams 🧤 (HR risk 1.11, vs LHB -0.27, vs RHB +1.81).",
        "rows": [
            row("Patrick Bailey", "S", "+960", 57, "", ["vs Burke"], """0 HR, 97.3 mph EV. limited split/risk sample; park/weather net drag (-27%).""", blast="good", contact={'stars': 2, 'k': 24.2, 'batterK': 25.0, 'batterWhiff': 25.2, 'pitcherK': 25.2}),
            row("Angel Martinez", "S", "+880", 64, "", ["vs Burke"], """1 HR, 1 near-HR, 88.8 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-27%).""", blast="good", contact={'stars': 3, 'k': 21.3, 'batterK': 19.7, 'batterWhiff': 16.1, 'pitcherK': 25.2}),
            row("Chase DeLauter", "L", "+710", 60, "", ["vs Burke"], """0 HR, 93.0 mph EV. limited split/risk sample; park/weather net drag (-27%).""", blast="good", contact={'stars': 4, 'k': 19.8, 'batterK': 17.3, 'batterWhiff': 12.0, 'pitcherK': 25.2}),
            row("Jo Adell", "R", "+590", 57, "", ["vs Burke"], """0 HR, 92.4 mph EV. limited split/risk sample; park/weather net drag (-27%).""", blast="good", contact={'stars': 2, 'k': 24.6, 'batterK': 23.0, 'batterWhiff': 28.4, 'pitcherK': 25.2}),
            row("Randal Grichuk", "R", "N/A", 81, "", ["vs Williams"], """1 HR, 1 near-HR, 90.9 mph EV. Williams RHB split +1.81, HR risk 1.11. park/weather net drag (-27%).""", blast="good", contact={'stars': 1, 'k': 34.1, 'batterK': 27.3, 'batterWhiff': 26.6, 'pitcherK': 42.5}),
            row("Andrew Benintendi", "L", "+820", 76, "", ["vs Williams"], """0 HR, 98.0 mph EV, 12.5% barrels. Williams LHB split -0.27, HR risk 1.11. slight split headwind (-0.27); park/weather net drag (-27%).""", blast="good", contact={'stars': 1, 'k': 31.3, 'batterK': 18.8, 'batterWhiff': 21.4, 'pitcherK': 42.5}),
            row("Kyle Teel", "L", "+900", 88, "🌕 💣", ["vs Williams"], """2 HR, 3 near-HR, 85.5 mph EV, 25.0% barrels. Williams LHB split -0.27, HR risk 1.11. slight split headwind (-0.27); park/weather net drag (-27%).""", blast="high", contact={'stars': 1, 'k': 38.6, 'batterK': 35.5, 'batterWhiff': 35.6, 'pitcherK': 42.5}),
            row("Jake Rogers", "R", "N/A", 75, "", ["vs Williams"], """0 HR, 2 near-HR, 89.3 mph EV, 12.5% barrels. Williams RHB split +1.81, HR risk 1.11. park/weather net drag (-27%).""", blast="good", contact={'stars': 1, 'k': 33.3, 'batterK': 29.4, 'batterWhiff': 21.5, 'pitcherK': 42.5}),
        ],
    },
    {
        "title": "DET @ TOR - Troy Melton (R, DET) vs Jose Soriano (R, TOR)",
        "kLines": {'Melton': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 23.5, 'matchupK': 17.3, 'ownK': 18.8}, 'Soriano': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 23.2, 'matchupK': 18.5, 'ownK': 16.6}},
        "description": "Tail key data: Park boost -18% (stadium +6%, weather -24%). Melton (HR risk 0.26, vs LHB +0.82, vs RHB -0.47). Soriano (HR risk -0.60, vs LHB -0.03, vs RHB -1.04).",
        "rows": [
            row("Brett Bateman", "L", "+1500", 73, "🌕 💣 💎", ["vs Melton"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 89.3 mph EV, 25.0% barrels. Melton LHB split +0.82, HR risk 0.26. park/weather net drag (-18%).""", blast="high", contact={'stars': 4, 'k': 18.4, 'batterK': 20.4, 'batterWhiff': 16.0, 'pitcherK': 18.8}),
            row("Kazuma Okamoto", "R", "+421", 86, "⭐ 🌕 💣", ["vs Melton"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.1 mph EV, 25.0% barrels. Melton RHB split -0.47, HR risk 0.26. tough split lane (-0.47); park/weather net drag (-18%).""", blast="high", contact={'stars': 3, 'k': 20.9, 'batterK': 21.0, 'batterWhiff': 30.1, 'pitcherK': 18.8}),
            row("Josh Smith", "L", "+1220", 81, "🌕 💣", ["vs Melton"], """2 HR, 2 near-HR, 90.6 mph EV, 25.0% barrels. Melton LHB split +0.82, HR risk 0.26. park/weather net drag (-18%).""", blast="high", contact={'stars': 3, 'k': 22.9, 'batterK': 32.0, 'batterWhiff': 32.5, 'pitcherK': 18.8}),
            row("George Springer", "R", "+495", 47, "", ["vs Melton"], """0 HR, 90.4 mph EV. Melton RHB split -0.47, HR risk 0.26. tough split lane (-0.47); park/weather net drag (-18%).""", contact={'stars': 4, 'k': 19.3, 'batterK': 17.1, 'batterWhiff': 25.5, 'pitcherK': 18.8}),
            row("Spencer Torkelson", "R", "+393", 82, "⭐ 🌕 💣", ["vs Soriano"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 95.7 mph EV, 25.0% barrels. Soriano RHB split -1.04, HR risk -0.60. tough split lane (-1.04); pitcher suppresses HR (-0.60).""", blast="high", contact={'stars': 3, 'k': 22.2, 'batterK': 31.8, 'batterWhiff': 32.7, 'pitcherK': 16.6}),
            row("Max Clark", "L", "+1300", 57, "", ["vs Soriano"], """1 HR, 1 near-HR, 94.5 mph EV. Soriano LHB split -0.03, HR risk -0.60. slight split headwind (-0.03); pitcher suppresses HR (-0.60).""", blast="good", contact={'stars': 4, 'k': 17.5, 'batterK': 21.3, 'batterWhiff': 16.8, 'pitcherK': 16.6}),
            row("Brett Callahan", "L", "+1340", 61, "", ["vs Soriano"], """0 HR, 2 near-HR, 93.9 mph EV, 37.5% barrels. Soriano LHB split -0.03, HR risk -0.60. slight split headwind (-0.03); pitcher suppresses HR (-0.60).""", blast="good", contact={'stars': 3, 'k': 22.0, 'batterK': 39.2, 'batterWhiff': 30.2, 'pitcherK': 16.6}),
            row("Kevin McGonigle", "L", "+700", 61, "", ["vs Soriano"], """1 HR, 2 near-HR, 95.3 mph EV. Soriano LHB split -0.03, HR risk -0.60. slight split headwind (-0.03); pitcher suppresses HR (-0.60).""", blast="good", contact={'stars': 5, 'k': 15.3, 'batterK': 12.4, 'batterWhiff': 16.9, 'pitcherK': 16.6}),
        ],
    },
    {
        "title": "LAD @ CIN - Tarik Skubal (L, LAD) vs Nick Lodolo (L, CIN)",
        "kLines": {'Skubal': {'k': 6.9, 'lo': 5, 'hi': 9, 'bf': 23.4, 'matchupK': 29.5, 'ownK': 29.9}, 'Lodolo': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 22.3, 'matchupK': 19.6, 'ownK': 20.5}},
        "description": "Tail key data: Park boost -4% (stadium +14%, weather -17%). Skubal (HR risk -0.87, vs LHB -0.51, vs RHB -0.71). Lodolo (HR risk 0.81, vs LHB -0.16, vs RHB +0.59).",
        "rows": [
            row("Elly De La Cruz", "S", "+475", 87, "🚀 ⭐ 🌕 💣", ["vs Skubal"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.2 mph EV, 37.5% barrels. Skubal SHB→RHB split -0.71, HR risk -0.87. tough split lane (-0.71); pitcher suppresses HR (-0.87).""", blast="high", contact={'stars': 1, 'k': 29.6, 'batterK': 28.9, 'batterWhiff': 28.6, 'pitcherK': 29.9}),
            row("Juan Brito", "S", "+880", 73, "🌕 💣", ["vs Skubal"], """1 HR, 2 near-HR, 97.1 mph EV, 50.0% barrels. Skubal SHB→RHB split -0.71, HR risk -0.87. tough split lane (-0.71); pitcher suppresses HR (-0.87).""", blast="high", contact={'stars': 1, 'k': 29.7, 'batterK': 30.0, 'batterWhiff': 30.7, 'pitcherK': 29.9}),
            row("Tyler Stephenson", "R", "+610", 68, "💎", ["vs Skubal"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.2 mph EV, 37.5% barrels. Skubal RHB split -0.71, HR risk -0.87. tough split lane (-0.71); pitcher suppresses HR (-0.87).""", blast="good", contact={'stars': 1, 'k': 29.8, 'batterK': 30.0, 'batterWhiff': 29.7, 'pitcherK': 29.9}),
            row("Sal Stewart", "R", "+490", 64, "⭐", ["vs Skubal"], """Worst Pickz Favorite. 0 HR, 99.5 mph EV, 12.5% barrels. Skubal RHB split -0.71, HR risk -0.87. tough split lane (-0.71); pitcher suppresses HR (-0.87).""", blast="good", contact={'stars': 2, 'k': 25.9, 'batterK': 18.2, 'batterWhiff': 27.9, 'pitcherK': 29.9}),
            row("Teoscar Hernandez", "R", "+396", 87, "💎", ["vs Lodolo"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.4 mph EV, 37.5% barrels. Lodolo RHB split +0.59, HR risk 0.81. weather carry headwind (-17%).""", blast="good", contact={'stars': 2, 'k': 24.4, 'batterK': 27.4, 'batterWhiff': 34.2, 'pitcherK': 20.5}),
            row("Max Muncy", "L", "+445", 75, "💎", ["vs Lodolo"], """Worst Pickz Hidden Gem. 0 HR, 97.4 mph EV. Lodolo LHB split -0.16, HR risk 0.81. slight split headwind (-0.16); weather carry headwind (-17%).""", blast="good", contact={'stars': 3, 'k': 22.1, 'batterK': 23.4, 'batterWhiff': 27.4, 'pitcherK': 20.5}),
            row("Will Smith", "R", "+490", 73, "", ["vs Lodolo"], """1 HR, 1 near-HR, 89.1 mph EV, 25.0% barrels. Lodolo RHB split +0.59, HR risk 0.81. weather carry headwind (-17%).""", blast="good", contact={'stars': 4, 'k': 18.2, 'batterK': 15.7, 'batterWhiff': 15.8, 'pitcherK': 20.5}),
            row("Enrique Hernandez", "R", "+496", 66, "", ["vs Lodolo"], """0 HR, 1 near-HR, 87.3 mph EV, 12.5% barrels. Lodolo RHB split +0.59, HR risk 0.81. weather carry headwind (-17%); limited recent HR events.""", contact={'stars': 2, 'k': 24.5, 'batterK': 35.4, 'batterWhiff': 33.7, 'pitcherK': 20.5}),
        ],
    },
    {
        "title": "MIA @ ARI - Sandy Alcantara (R, MIA) vs Corbin Burnes (R, ARI)",
        "kLines": {'Alcantara': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 26.0, 'matchupK': 14.3, 'ownK': 13.6}, 'Burnes': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 20.5, 'matchupK': 21.3, 'ownK': 15.4}},
        "description": "Tail key data: Park boost -10% (stadium -9%, weather -1%). Alcantara (HR risk -0.15, vs LHB +0.53, vs RHB -0.91). Burnes (HR risk -0.44, vs LHB -0.19, vs RHB -0.17).",
        "rows": [
            row("Corbin Carroll", "L", "+477", 82, "🌕 💣 💎", ["vs Alcantara"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 99.3 mph EV, 37.5% barrels. Alcantara LHB split +0.53, HR risk -0.15. pitcher risk below avg (-0.15); park/weather net drag (-10%).""", blast="high", contact={'stars': 4, 'k': 19.8, 'batterK': 29.3, 'batterWhiff': 30.8, 'pitcherK': 13.6}),
            row("Lars Nootbaar", "L", "+600", 64, "💎", ["vs Alcantara"], """Worst Pickz Hidden Gem. 0 HR, 96.0 mph EV. Alcantara LHB split +0.53, HR risk -0.15. pitcher risk below avg (-0.15); park/weather net drag (-10%).""", blast="good", contact={'stars': 5, 'k': 13.9, 'batterK': 11.9, 'batterWhiff': 13.0, 'pitcherK': 13.6}),
            row("Tim Tawa", "R", "+820", 71, "", ["vs Alcantara"], """1 HR, 2 near-HR, 90.2 mph EV, 25.0% barrels. Alcantara RHB split -0.91, HR risk -0.15. tough split lane (-0.91); pitcher risk below avg (-0.15).""", blast="good", contact={'stars': 3, 'k': 20.2, 'batterK': 30.1, 'batterWhiff': 33.6, 'pitcherK': 13.6}),
            row("Joe Mack", "L", "+1120", 64, "", ["vs Burnes"], """1 HR, 1 near-HR, 94.2 mph EV, 12.5% barrels. Burnes LHB split -0.19, HR risk -0.44. slight split headwind (-0.19); pitcher suppresses HR (-0.44).""", blast="good", contact={'stars': 3, 'k': 22.6, 'batterK': 25.9, 'batterWhiff': 26.4, 'pitcherK': 15.4}),
            row("Otto Lopez", "R", "+1040", 46, "💎", ["vs Burnes"], """Worst Pickz Hidden Gem. 0 HR, 88.1 mph EV, 12.5% barrels. Burnes RHB split -0.17, HR risk -0.44. slight split headwind (-0.17); pitcher suppresses HR (-0.44).""", contact={'stars': 4, 'k': 18.4, 'batterK': 12.4, 'batterWhiff': 21.8, 'pitcherK': 15.4}),
            row("Kyle Stowers", "L", "+490", 79, "", ["vs Burnes"], """1 HR, 1 near-HR, 99.6 mph EV, 12.5% barrels. Burnes LHB split -0.19, HR risk -0.44. slight split headwind (-0.19); pitcher suppresses HR (-0.44).""", blast="good", contact={'stars': 1, 'k': 28.3, 'batterK': 37.0, 'batterWhiff': 39.5, 'pitcherK': 15.4}),
            row("Heriberto Hernandez", "R", "+478", 67, "", ["vs Burnes"], """1 HR, 2 near-HR, 79.8 mph EV, 12.5% barrels. Burnes RHB split -0.17, HR risk -0.44. slight split headwind (-0.17); pitcher suppresses HR (-0.44).""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 24.2, 'batterWhiff': 31.4, 'pitcherK': 15.4}),
        ],
    },
    {
        "title": "NYY @ MIN - Will Warren (R, NYY) vs Dean Kremer (R, MIN)",
        "kLines": {'Warren': {'k': 4.8, 'lo': 3, 'hi': 6, 'bf': 22.3, 'matchupK': 21.7, 'ownK': 23.9}, 'Kremer': {'k': 4.8, 'lo': 3, 'hi': 6, 'bf': 21.5, 'matchupK': 22.1, 'ownK': 21.0}},
        "description": "Tail key data: Park boost -10% (stadium -8%, weather -3%). Warren (HR risk 0.30, vs LHB -0.34, vs RHB +0.63). Kremer (HR risk 0.70, vs LHB +0.50, vs RHB +0.71).",
        "rows": [
            row("Josh Bell", "S", "+600", 80, "⭐", ["vs Warren"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.5 mph EV, 37.5% barrels. Warren SHB→LHB split -0.34, HR risk 0.30. slight split headwind (-0.34); park/weather net drag (-10%).""", blast="good", contact={'stars': 3, 'k': 20.8, 'batterK': 16.7, 'batterWhiff': 21.4, 'pitcherK': 23.9}),
            row("Kody Clemens", "L", "+425", 86, "🌕 💣 💎", ["vs Warren"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 95.1 mph EV, 25.0% barrels. Warren LHB split -0.34, HR risk 0.30. slight split headwind (-0.34); park/weather net drag (-10%).""", blast="high", contact={'stars': 3, 'k': 22.1, 'batterK': 22.0, 'batterWhiff': 20.7, 'pitcherK': 23.9}),
            row("Emmanuel Rodriguez", "L", "+940", 83, "🚀 🌕 💣", ["vs Warren"], """1 HR, 1 near-HR, 103.4 mph EV, 75.0% barrels. Warren LHB split -0.34, HR risk 0.30. slight split headwind (-0.34); park/weather net drag (-10%).""", blast="high", contact={'stars': 3, 'k': 23.6, 'batterK': 25.0, 'batterWhiff': 33.3, 'pitcherK': 23.9}),
            row("Royce Lewis", "R", "N/A", 62, "💎", ["vs Warren"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.0 mph EV, 12.5% barrels. Warren RHB split +0.63, HR risk 0.30. park/weather net drag (-10%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 20.5, 'batterWhiff': 28.4, 'pitcherK': 23.9}),
            row("Ben Rice", "L", "+346", 92, "⭐ 🌕 💣", ["vs Kremer"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.8 mph EV, 12.5% barrels. Kremer LHB split +0.50, HR risk 0.70. park/weather net drag (-10%).""", blast="high", contact={'stars': 3, 'k': 21.1, 'batterK': 21.3, 'batterWhiff': 23.6, 'pitcherK': 21.0}),
            row("Spencer Jones", "L", "+450", 87, "⭐ 🌕 💣", ["vs Kremer"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 99.2 mph EV, 25.0% barrels. Kremer LHB split +0.50, HR risk 0.70. park/weather net drag (-10%); limited recent HR events.""", blast="high", contact={'stars': 2, 'k': 26.3, 'batterK': 33.3, 'batterWhiff': 37.1, 'pitcherK': 21.0}),
            row("Aaron Judge", "R", "+300", 78, "", ["vs Kremer"], """0 HR, 1 near-HR, 90.0 mph EV, 12.5% barrels. Kremer RHB split +0.71, HR risk 0.70. park/weather net drag (-10%); limited recent HR events.""", contact={'stars': 2, 'k': 24.5, 'batterK': 30.6, 'batterWhiff': 28.6, 'pitcherK': 21.0}),
            row("Luis Garcia Jr.", "L", "N/A", 77, "💎", ["vs Kremer"], """Worst Pickz Hidden Gem. 0 HR, 90.8 mph EV, 25.0% barrels. Kremer LHB split +0.50, HR risk 0.70. park/weather net drag (-10%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.5, 'batterK': 19.2, 'batterWhiff': 27.7, 'pitcherK': 21.0}),
        ],
    },
    {
        "title": "SD @ COL - Casey Mize (R, SD) vs Tomoyuki Sugano (R, COL)",
        "kLines": {'Mize': {'k': 3.9, 'lo': 2, 'hi': 5, 'bf': 21.2, 'matchupK': 18.3, 'ownK': 17.0}, 'Sugano': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 22.5, 'matchupK': 16.8, 'ownK': 15.5}},
        "description": "Tail key data: Park boost +27% (stadium +20%, weather +6%). Mize (HR risk 0.85, vs LHB -0.08, vs RHB +1.36). Sugano (HR risk 0.75, vs LHB +1.14, vs RHB -0.01).",
        "rows": [
            row("TJ Rumfield", "L", "+640", 77, "", ["vs Mize"], """0 HR, 1 near-HR, 91.3 mph EV, 12.5% barrels. Mize LHB split -0.08, HR risk 0.85. slight split headwind (-0.08); limited recent HR events.""", contact={'stars': 5, 'k': 15.3, 'batterK': 11.6, 'batterWhiff': 15.4, 'pitcherK': 17.0}),
            row("Jake McCarthy", "L", "+680", 77, "", ["vs Mize"], """0 HR, 93.2 mph EV. Mize LHB split -0.08, HR risk 0.85. slight split headwind (-0.08); limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 15.6, 'batterK': 12.9, 'batterWhiff': 16.1, 'pitcherK': 17.0}),
            row("Adael Amador", "S", "+750", 83, "", ["vs Mize"], """1 HR, 1 near-HR, 79.9 mph EV, 12.5% barrels. Mize SHB→LHB split -0.08, HR risk 0.85. slight split headwind (-0.08); lighter EV form (79.9 mph).""", blast="good", contact={'stars': 5, 'k': 16.7, 'batterK': 15.1, 'batterWhiff': 13.9, 'pitcherK': 17.0}),
            row("Hunter Goodman", "R", "+260", 68, "", ["vs Mize"], """0 HR, 86.3 mph EV. Mize RHB split +1.36, HR risk 0.85. limited recent HR events; lighter EV form (86.3 mph).""", contact={'stars': 3, 'k': 20.3, 'batterK': 23.2, 'batterWhiff': 27.6, 'pitcherK': 17.0}),
            row("Jackson Merrill", "L", "+310", 99, "🚀 ⭐ 🌕 💣", ["vs Sugano"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 102.7 mph EV, 50.0% barrels. Sugano LHB split +1.14, HR risk 0.75.""", blast="high", contact={'stars': 5, 'k': 16.7, 'batterK': 14.9, 'batterWhiff': 24.2, 'pitcherK': 15.5}),
            row("Fernando Tatis Jr.", "R", "+250", 92, "⭐ 🌕 💣", ["vs Sugano"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.9 mph EV, 12.5% barrels. Sugano RHB split -0.01, HR risk 0.75. slight split headwind (-0.01).""", blast="good", contact={'stars': 4, 'k': 17.3, 'batterK': 17.8, 'batterWhiff': 23.7, 'pitcherK': 15.5}),
            row("Freddy Fermin", "R", "+650", 59, "", ["vs Sugano"], """0 HR, 90.1 mph EV. Sugano RHB split -0.01, HR risk 0.75. slight split headwind (-0.01); limited recent HR events.""", contact={'stars': 3, 'k': 22.0, 'batterK': 29.6, 'batterWhiff': 38.2, 'pitcherK': 15.5}),
            row("Ty France", "R", "+440", 81, "💎", ["vs Sugano"], """Worst Pickz Hidden Gem. 0 HR, 91.9 mph EV, 12.5% barrels. Sugano RHB split -0.01, HR risk 0.75. slight split headwind (-0.01); limited recent HR events.""", contact={'stars': 4, 'k': 18.4, 'batterK': 18.6, 'batterWhiff': 29.0, 'pitcherK': 15.5}),
        ],
    },
    {
        "title": "SEA @ LAA - Kade Anderson (L, SEA) vs Reid Detmers (L, LAA)",
        "kLines": {'Anderson': {'k': 4.8, 'lo': 3, 'hi': 6, 'bf': 21.7, 'matchupK': 22.3, 'ownK': 18.4}, 'Detmers': {'k': 6.5, 'lo': 5, 'hi': 8, 'bf': 22.9, 'matchupK': 28.2, 'ownK': 30.9}},
        "description": "Tail key data: Park boost -4% (stadium -8%, weather +5%). Anderson (HR risk 0.69, vs LHB +1.12, vs RHB +0.35). Detmers (HR risk -0.97, vs LHB -0.58, vs RHB -0.84).",
        "rows": [
            row("Zach Neto", "R", "+430", 82, "⭐", ["vs Anderson"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 89.0 mph EV, 12.5% barrels. Anderson RHB split +0.35, HR risk 0.69. park suppresses carry (-8%).""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 27.8, 'batterWhiff': 28.6, 'pitcherK': 18.4}),
            row("Christian Moore", "R", "+880", 70, "", ["vs Anderson"], """0 HR, 1 near-HR, 93.1 mph EV, 12.5% barrels. Anderson RHB split +0.35, HR risk 0.69. park suppresses carry (-8%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.1, 'batterK': 24.4, 'batterWhiff': 27.7, 'pitcherK': 18.4}),
            row("Dominic Canzone", "L", "+528", 74, "⭐", ["vs Detmers"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.4 mph EV, 25.0% barrels. Detmers LHB split -0.58, HR risk -0.97. tough split lane (-0.58); pitcher suppresses HR (-0.97).""", blast="good", contact={'stars': 2, 'k': 26.8, 'batterK': 23.6, 'batterWhiff': 21.6, 'pitcherK': 30.9}),
            row("Randy Arozarena", "R", "+483", 85, "🌕 💣", ["vs Detmers"], """3 HR, 3 near-HR, 92.7 mph EV, 25.0% barrels. Detmers RHB split -0.84, HR risk -0.97. tough split lane (-0.84); pitcher suppresses HR (-0.97).""", blast="high", contact={'stars': 1, 'k': 28.3, 'batterK': 24.2, 'batterWhiff': 28.1, 'pitcherK': 30.9}),
            row("Cole Young", "L", "+920", 64, "", ["vs Detmers"], """0 HR, 3 near-HR, 92.4 mph EV, 25.0% barrels. Detmers LHB split -0.58, HR risk -0.97. tough split lane (-0.58); pitcher suppresses HR (-0.97).""", blast="good", contact={'stars': 2, 'k': 24.9, 'batterK': 17.1, 'batterWhiff': 21.6, 'pitcherK': 30.9}),
        ],
    },
    {
        "title": "SF @ STL - Landen Roupp (R, SF) vs Quinn Mathews (L, STL)",
        "kLines": {'Roupp': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 22.6, 'matchupK': 18.0, 'ownK': 15.5}, 'Mathews': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 22.3, 'matchupK': 21.2, 'ownK': 20.4}},
        "description": "Tail key data: Park boost -11% (stadium -10%, weather -2%). Roupp (HR risk -0.98, vs LHB -0.66, vs RHB -0.78). Mathews (HR risk -0.83, vs LHB -0.23, vs RHB -0.73).",
        "rows": [
            row("Alec Burleson", "L", "+630", 62, "", ["vs Roupp"], """1 HR, 1 near-HR, 92.1 mph EV, 12.5% barrels. Roupp LHB split -0.66, HR risk -0.98. tough split lane (-0.66); pitcher suppresses HR (-0.98).""", blast="good", contact={'stars': 4, 'k': 17.6, 'batterK': 19.0, 'batterWhiff': 23.2, 'pitcherK': 15.5}),
            row("Joshua Baez", "R", "+564", 67, "💎", ["vs Roupp"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 97.4 mph EV, 12.5% barrels. Roupp RHB split -0.78, HR risk -0.98. tough split lane (-0.78); pitcher suppresses HR (-0.98).""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 34.3, 'batterWhiff': 38.5, 'pitcherK': 15.5}),
            row("Leonardo Bernal", "S", "+920", 52, "", ["vs Roupp"], """0 HR, 97.4 mph EV. Roupp SHB→LHB split -0.66, HR risk -0.98. tough split lane (-0.66); pitcher suppresses HR (-0.98).""", blast="good", contact={'stars': 4, 'k': 17.9, 'batterK': 19.2, 'batterWhiff': 22.9, 'pitcherK': 15.5}),
            row("Thomas Saggese", "R", "+1040", 50, "", ["vs Roupp"], """0 HR, 92.8 mph EV. Roupp RHB split -0.78, HR risk -0.98. tough split lane (-0.78); pitcher suppresses HR (-0.98).""", blast="good", contact={'stars': 4, 'k': 18.4, 'batterK': 20.6, 'batterWhiff': 25.0, 'pitcherK': 15.5}),
            row("Jordan Walker", "R", "+551", 40, "", ["vs Roupp"], """0 HR, 86.1 mph EV. Roupp RHB split -0.78, HR risk -0.98. tough split lane (-0.78); pitcher suppresses HR (-0.98).""", contact={'stars': 3, 'k': 23.4, 'batterK': 34.2, 'batterWhiff': 37.5, 'pitcherK': 15.5}),
            row("Bryce Eldridge", "L", "+566", 75, "⭐", ["vs Mathews"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.2 mph EV, 12.5% barrels. Mathews LHB split -0.23, HR risk -0.83. slight split headwind (-0.23); pitcher suppresses HR (-0.83).""", blast="good", contact={'stars': 3, 'k': 22.8, 'batterK': 26.4, 'batterWhiff': 25.6, 'pitcherK': 20.4}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-14")

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

    out = ROOT / '_games-0914.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
