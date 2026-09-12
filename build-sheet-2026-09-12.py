#!/usr/bin/env python3
"""Generate games[] block for 2026-09-12 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Adley Rutschman (S)",
    "Brandon Lowe (L)",
    "Bryce Eldridge (L)",
    "Coby Mayo (R)",
    "Heliot Ramos (R)",
    "James Wood (L)",
    "Junior Caminero (R)",
    "Rafael Devers (L)",
    "Ryan Jeffers (R)",
}

GEMS = {
    "Aaron Judge (R)",
    "Andrew Benintendi (L)",
    "Austin Riley (R)",
    "Brandon Marsh (L)",
    "Brice Turang (L)",
    "Brooks Lee (S)",
    "Bryan Reynolds (S)",
    "Colt Keith (L)",
    "Josh Bell (S)",
    "Kevin McGonigle (L)",
    "Kody Clemens (L)",
    "Lars Nootbaar (L)",
    "Lawrence Butler (L)",
    "Mickey Gasper (S)",
    "Mookie Betts (R)",
    "Munetaka Murakami (L)",
    "Otto Lopez (R)",
    "Pete Crow Armstrong (L)",
    "Roman Anthony (L)",
    "Ryan Vilade (R)",
    "Samuel Basallo (L)",
    "Trea Turner (R)",
    "Victor Mesa Jr. (L)",
    "Zack Gelof (R)",
}

PLAYER_TEAMS = {
    "Aaron Judge (R)": "NYY",
    "Adael Amador (S)": "COL",
    "Adley Rutschman (S)": "BOS",
    "Alec Burleson (L)": "STL",
    "Alejandro Kirk (R)": "TOR",
    "Alex Freeland (S)": "LAD",
    "Amed Rosario (R)": "NYY",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Knizner (R)": "SF",
    "Andrew Pinckney (R)": "WSH",
    "Angel Martinez (S)": "CLE",
    "Austin Riley (R)": "ATL",
    "BJ Murray Jr. (S)": "CHC",
    "Bo Bichette (R)": "NYM",
    "Bo Naylor (L)": "MIL",
    "Braden Montgomery (S)": "CWS",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Brandon Valenzuela (S)": "TOR",
    "Brett Baty (L)": "NYM",
    "Brewer Hicklen (R)": "ATL",
    "Brice Turang (L)": "MIL",
    "Brooks Lee (S)": "MIN",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Cam Smith (R)": "HOU",
    "Carter Jensen (L)": "KC",
    "Christian Moore (R)": "LAA",
    "Coby Mayo (R)": "BAL",
    "Cody Bellinger (L)": "NYY",
    "Cole Carrigg (S)": "COL",
    "Cole Young (L)": "SEA",
    "Colt Keith (L)": "DET",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Daulton Varsho (L)": "HOU",
    "David Fry (R)": "CLE",
    "David Hamilton (L)": "MIL",
    "Daylen Lile (L)": "WSH",
    "Dominic Canzone (L)": "SEA",
    "Dylan Crews (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Eugenio Suarez (R)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Lindor (S)": "NYM",
    "Freddie Freeman (L)": "LAD",
    "Garrett Mitchell (L)": "MIL",
    "Griffin Conine (L)": "MIA",
    "Heliot Ramos (R)": "NYY",
    "Ivan Herrera (R)": "STL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jake McCarthy (L)": "COL",
    "James Wood (L)": "WSH",
    "Jarren Duran (L)": "BOS",
    "Jase Bowen (R)": "SD",
    "Javier Sanoja (R)": "MIA",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "John Peck (R)": "DET",
    "Jonah Heim (S)": "ATH",
    "Jordan Walker (R)": "STL",
    "Jose Siri (R)": "LAA",
    "Josh Bell (S)": "MIN",
    "Joshua Baez (R)": "STL",
    "Juan Soto (L)": "NYM",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Keibert Ruiz (S)": "WSH",
    "Kevin McGonigle (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Kyle Tucker (L)": "LAD",
    "LaMonte Wade Jr. (L)": "HOU",
    "Lars Nootbaar (L)": "ARI",
    "Lawrence Butler (L)": "ATH",
    "Leonardo Bernal (S)": "STL",
    "Luis Torrens (R)": "NYM",
    "Manny Machado (R)": "SD",
    "Marcus Semien (R)": "NYM",
    "Max Clark (L)": "DET",
    "Max Muncy (R)": "ATH",
    "Michael Massey (L)": "KC",
    "Michael Stefanic (R)": "ATH",
    "Mickey Gasper (S)": "BOS",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Nathaniel Lowe (L)": "CLE",
    "Nelson Velazquez (R)": "HOU",
    "Nolan Gorman (L)": "STL",
    "Oneil Cruz (L)": "PIT",
    "Otto Lopez (R)": "MIA",
    "Owen Caissie (L)": "MIA",
    "Ozzie Albies (S)": "ATL",
    "Patrick Bailey (S)": "CLE",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Roman Anthony (L)": "BOS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan Jeffers (R)": "MIN",
    "Ryan O'Hearn (L)": "PIT",
    "Ryan Vilade (R)": "TB",
    "Sal Stewart (R)": "CIN",
    "Samuel Basallo (L)": "BAL",
    "Sean Keys (L)": "TOR",
    "Seiya Suzuki (R)": "CHC",
    "Spencer Torkelson (R)": "DET",
    "Sung-Mun Song (L)": "SD",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Travis d'Arnaud (R)": "LAA",
    "Trea Turner (R)": "PHI",
    "Tristan Peters (L)": "CWS",
    "Troy Johnston (L)": "COL",
    "Tyler Stephenson (R)": "CIN",
    "Victor Mesa Jr. (L)": "TB",
    "Vinnie Pasquantino (L)": "KC",
    "William Contreras (R)": "MIL",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yainer Diaz (R)": "HOU",
    "Yohandy Morales (R)": "WSH",
    "Yordan Alvarez (L)": "HOU",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("CIN @ MIL", "Singer"),
    ("HOU @ TB", "Seymour"),
    ("NYM @ NYY", "Thornton"),
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
        "title": "BAL @ TOR - Kyle Bradish (R, BAL) vs Spencer Miles (R, TOR)",
        "kLines": {'Bradish': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 23.0, 'matchupK': 16.5, 'ownK': 17.5}, 'Miles': {'k': 4.0, 'lo': 2, 'hi': 6, 'bf': 17.2, 'matchupK': 23.0, 'ownK': 21.4}},
        "description": "Tail key data: Park boost +16%. Bradish (HR risk 0.67, vs LHB +0.57, vs RHB +0.21). Miles (HR risk -1.36, vs LHB -0.38, vs RHB -1.60).",
        "rows": [
            row("Kazuma Okamoto", "R", "+464", 88, "🌕 💣", ["vs Bradish"], """1 HR, 1 near-HR, 96.9 mph EV, 12.5% barrels. Bradish RHB split +0.21, HR risk 0.67.""", blast="good", contact={'stars': 3, 'k': 20.9, 'batterK': 23.2, 'batterWhiff': 30.0, 'pitcherK': 17.5}),
            row("Sean Keys", "L", "N/A", 86, "", ["vs Bradish"], """1 HR, 1 near-HR, 90.2 mph EV, 25.0% barrels. Bradish LHB split +0.57, HR risk 0.67.""", blast="good", contact={'stars': 3, 'k': 22.5, 'batterK': 38.3, 'batterWhiff': 31.2, 'pitcherK': 17.5}),
            row("Brandon Valenzuela", "S", "N/A", 63, "", ["vs Bradish"], """0 HR, 1 near-HR, 90.8 mph EV. Bradish SHB→LHB split +0.57, HR risk 0.67. limited recent HR events.""", contact={'stars': 3, 'k': 21.3, 'batterK': 28.9, 'batterWhiff': 29.7, 'pitcherK': 17.5}),
            row("Alejandro Kirk", "R", "+820", 63, "", ["vs Bradish"], """0 HR, 87.6 mph EV. Bradish RHB split +0.21, HR risk 0.67. limited recent HR events; lighter EV form (87.6 mph).""", contact={'stars': 5, 'k': 15.4, 'batterK': 12.6, 'batterWhiff': 13.9, 'pitcherK': 17.5}),
            row("Coby Mayo", "R", "+386", 88, "⭐ 🌕 💣", ["vs Miles"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 97.7 mph EV, 37.5% barrels. Miles RHB split -1.60, HR risk -1.36. tough split lane (-1.60); pitcher suppresses HR (-1.36).""", blast="high", contact={'stars': 3, 'k': 23.5, 'batterK': 25.3, 'batterWhiff': 29.1, 'pitcherK': 21.4}),
            row("Samuel Basallo", "L", "+529", 71, "💎", ["vs Miles"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 97.8 mph EV, 12.5% barrels. Miles LHB split -0.38, HR risk -1.36. slight split headwind (-0.38); pitcher suppresses HR (-1.36).""", blast="good", contact={'stars': 2, 'k': 24.9, 'batterK': 27.1, 'batterWhiff': 34.2, 'pitcherK': 21.4}),
            row("Colton Cowser", "L", "+790", 64, "", ["vs Miles"], """0 HR, 95.0 mph EV. Miles LHB split -0.38, HR risk -1.36. slight split headwind (-0.38); pitcher suppresses HR (-1.36).""", blast="good", contact={'stars': 2, 'k': 24.4, 'batterK': 33.9, 'batterWhiff': 27.6, 'pitcherK': 21.4}),
        ],
    },
    {
        "title": "CIN @ MIL - Brady Singer 🧤 (R, CIN) vs Kyle Harrison (L, MIL)",
        "kLines": {'Singer': {'k': 4.2, 'lo': 3, 'hi': 6, 'bf': 23.2, 'matchupK': 17.9, 'ownK': 17.2}, 'Harrison': {'k': 5.4, 'lo': 4, 'hi': 7, 'bf': 20.7, 'matchupK': 26.3, 'ownK': 26.5}},
        "description": "Tail key data: Park boost +8%. Singer 🧤 (HR risk 1.08, vs LHB +1.02, vs RHB +0.24). Harrison (BAA vs LHB .230, vs RHB .257, HR/9 1.63).",
        "rows": [
            row("Brice Turang", "L", "+540", 87, "💎", ["vs Singer"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.2 mph EV, 25.0% barrels. Singer LHB split +1.02, HR risk 1.08.""", blast="good", contact={'stars': 4, 'k': 19.8, 'batterK': 24.7, 'batterWhiff': 22.8, 'pitcherK': 17.2}),
            row("Jake Bauers", "L", "+340", 90, "🌕 💣", ["vs Singer"], """1 HR, 1 near-HR, 89.7 mph EV, 12.5% barrels. Singer LHB split +1.02, HR risk 1.08.""", blast="good", contact={'stars': 3, 'k': 23.2, 'batterK': 30.4, 'batterWhiff': 35.4, 'pitcherK': 17.2}),
            row("William Contreras", "R", "+560", 81, "🚀", ["vs Singer"], """0 HR, 100.1 mph EV. Singer RHB split +0.24, HR risk 1.08. limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 17.9, 'batterK': 19.1, 'batterWhiff': 20.6, 'pitcherK': 17.2}),
            row("Bo Naylor", "L", "N/A", 81, "", ["vs Singer"], """0 HR, 1 near-HR, 92.5 mph EV, 12.5% barrels. Singer LHB split +1.02, HR risk 1.08. limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 17.9, 'batterK': 25.9, 'batterWhiff': 14.0, 'pitcherK': 17.2}),
            row("Garrett Mitchell", "L", "+600", 88, "🌕 💣", ["vs Singer"], """0 HR, 1 near-HR, 99.8 mph EV, 12.5% barrels. Singer LHB split +1.02, HR risk 1.08. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.0, 'batterK': 27.3, 'batterWhiff': 33.9, 'pitcherK': 17.2}),
            row("David Hamilton", "L", "N/A", 61, "", ["vs Singer"], """0 HR, 91.0 mph EV. Singer LHB split +1.02, HR risk 1.08. limited recent HR events.""", contact={'stars': 5, 'k': 16.8, 'batterK': 15.9, 'batterWhiff': 16.2, 'pitcherK': 17.2}),
            row("Elly De La Cruz", "S", "N/A", 93, "🌕 💣", ["vs Harrison"], """2 HR, 4 near-HR, 98.0 mph EV, 62.5% barrels. limited split/risk sample.""", blast="high", contact={'stars': 2, 'k': 26.0, 'batterK': 27.0, 'batterWhiff': 26.1, 'pitcherK': 26.5}),
            row("Sal Stewart", "R", "N/A", 73, "", ["vs Harrison"], """0 HR, 2 near-HR, 94.8 mph EV. limited split/risk sample.""", blast="good", contact={'stars': 3, 'k': 22.5, 'batterK': 15.9, 'batterWhiff': 25.8, 'pitcherK': 26.5}),
            row("Eugenio Suarez", "R", "N/A", 87, "🌕 💣", ["vs Harrison"], """2 HR, 3 near-HR, 91.0 mph EV, 37.5% barrels. limited split/risk sample.""", blast="high", contact={'stars': 1, 'k': 27.7, 'batterK': 28.9, 'batterWhiff': 32.6, 'pitcherK': 26.5}),
            row("Tyler Stephenson", "R", "N/A", 62, "", ["vs Harrison"], """0 HR, 91.9 mph EV, 12.5% barrels. limited split/risk sample; limited recent HR events.""", contact={'stars': 1, 'k': 28.8, 'batterK': 34.2, 'batterWhiff': 31.9, 'pitcherK': 26.5}),
        ],
    },
    {
        "title": "CLE @ MIN - Daniel Espino (R, CLE) vs Connor Prielipp (L, MIN)",
        "kLines": {'Espino': {'k': 5.7, 'lo': 4, 'hi': 7, 'bf': 21.7, 'matchupK': 26.3, 'ownK': 41.9}, 'Prielipp': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 22.4, 'matchupK': 23.7, 'ownK': 27.7}},
        "description": "Tail key data: Park boost +3%. Espino (HR risk -0.98, vs LHB -1.48, vs RHB +0.17). Prielipp (HR risk 0.07, vs LHB +0.38, vs RHB -0.04).",
        "rows": [
            row("Kody Clemens", "L", "+427", 89, "🌕 💣 💎", ["vs Espino"], """Worst Pickz Hidden Gem. 4 HR, 4 near-HR, 96.8 mph EV, 50.0% barrels. Espino LHB split -1.48, HR risk -0.98. tough split lane (-1.48); pitcher suppresses HR (-0.98).""", blast="high", contact={'stars': 3, 'k': 23.9, 'batterK': 19.8, 'batterWhiff': 20.0, 'pitcherK': 41.9}),
            row("Ryan Jeffers", "R", "+586", 90, "⭐ 🌕 💣", ["vs Espino"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 98.8 mph EV, 25.0% barrels. Espino RHB split +0.17, HR risk -0.98. pitcher suppresses HR (-0.98).""", blast="high", contact={'stars': 3, 'k': 20.7, 'batterK': 15.0, 'batterWhiff': 11.4, 'pitcherK': 41.9}),
            row("Josh Bell", "S", "+600", 71, "💎", ["vs Espino"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.7 mph EV, 37.5% barrels. Espino SHB→LHB split -1.48, HR risk -0.98. tough split lane (-1.48); pitcher suppresses HR (-0.98).""", blast="good", contact={'stars': 3, 'k': 22.0, 'batterK': 14.3, 'batterWhiff': 19.1, 'pitcherK': 41.9}),
            row("Brooks Lee", "S", "+680", 61, "💎", ["vs Espino"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.0 mph EV, 12.5% barrels. Espino SHB→LHB split -1.48, HR risk -0.98. tough split lane (-1.48); pitcher suppresses HR (-0.98).""", blast="good", contact={'stars': 3, 'k': 21.9, 'batterK': 14.5, 'batterWhiff': 18.2, 'pitcherK': 41.9}),
            row("Royce Lewis", "R", "+550", 59, "", ["vs Espino"], """0 HR, 1 near-HR, 94.4 mph EV, 12.5% barrels. Espino RHB split +0.17, HR risk -0.98. pitcher suppresses HR (-0.98); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.4, 'batterK': 20.3, 'batterWhiff': 26.4, 'pitcherK': 41.9}),
            row("Angel Martinez", "S", "+730", 83, "🌕 💣", ["vs Prielipp"], """2 HR, 2 near-HR, 89.8 mph EV, 25.0% barrels. Prielipp SHB→RHB split -0.04, HR risk 0.07. slight split headwind (-0.04).""", blast="high", contact={'stars': 3, 'k': 22.9, 'batterK': 20.0, 'batterWhiff': 17.3, 'pitcherK': 27.7}),
            row("Patrick Bailey", "S", "N/A", 61, "", ["vs Prielipp"], """0 HR, 98.2 mph EV. Prielipp SHB→RHB split -0.04, HR risk 0.07. slight split headwind (-0.04); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.1, 'batterK': 23.7, 'batterWhiff': 24.1, 'pitcherK': 27.7}),
            row("Nathaniel Lowe", "L", "N/A", 52, "", ["vs Prielipp"], """0 HR, 91.7 mph EV. Prielipp LHB split +0.38, HR risk 0.07. limited recent HR events.""", contact={'stars': 2, 'k': 24.7, 'batterK': 23.1, 'batterWhiff': 22.0, 'pitcherK': 27.7}),
            row("David Fry", "R", "+880", 52, "", ["vs Prielipp"], """0 HR, 90.8 mph EV. Prielipp RHB split -0.04, HR risk 0.07. slight split headwind (-0.04); limited recent HR events.""", contact={'stars': 2, 'k': 25.5, 'batterK': 23.7, 'batterWhiff': 26.3, 'pitcherK': 27.7}),
        ],
    },
    {
        "title": "COL @ DET - Tanner Gordon (R, COL) vs Andrew Sears (L, DET)",
        "kLines": {'Gordon': {'k': 4.0, 'lo': 2, 'hi': 6, 'bf': 22.1, 'matchupK': 18.0, 'ownK': 14.9}, 'Sears': {'k': 4.2, 'lo': 3, 'hi': 6, 'bf': 21.9, 'matchupK': 19.1, 'ownK': 15.7}},
        "description": "Tail key data: Park boost -7%. Gordon (HR risk 0.46, vs LHB +0.34, vs RHB +0.38). Sears (HR risk -0.57, vs LHB +1.13, vs RHB -1.11).",
        "rows": [
            row("Kevin McGonigle", "L", "+525", 89, "🌕 💣 💎", ["vs Gordon"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 93.5 mph EV, 12.5% barrels. Gordon LHB split +0.34, HR risk 0.46. park/weather net drag (-7%).""", blast="high", contact={'stars': 5, 'k': 14.8, 'batterK': 12.5, 'batterWhiff': 16.2, 'pitcherK': 14.9}),
            row("John Peck", "R", "+800", 68, "", ["vs Gordon"], """0 HR, 99.0 mph EV. Gordon RHB split +0.38, HR risk 0.46. park/weather net drag (-7%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.0, 'batterK': 21.2, 'batterWhiff': 27.9, 'pitcherK': 14.9}),
            row("Colt Keith", "L", "+525", 85, "💎", ["vs Gordon"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.1 mph EV, 25.0% barrels. Gordon LHB split +0.34, HR risk 0.46. park/weather net drag (-7%).""", blast="good", contact={'stars': 3, 'k': 20.7, 'batterK': 29.1, 'batterWhiff': 32.0, 'pitcherK': 14.9}),
            row("Max Clark", "L", "+820", 73, "", ["vs Gordon"], """1 HR, 1 near-HR, 96.8 mph EV. Gordon LHB split +0.34, HR risk 0.46. park/weather net drag (-7%).""", blast="good", contact={'stars': 4, 'k': 17.2, 'batterK': 21.6, 'batterWhiff': 18.0, 'pitcherK': 14.9}),
            row("Spencer Torkelson", "R", "N/A", 77, "", ["vs Gordon"], """1 HR, 1 near-HR, 93.7 mph EV, 12.5% barrels. Gordon RHB split +0.38, HR risk 0.46. park/weather net drag (-7%).""", blast="good", contact={'stars': 3, 'k': 23.6, 'batterK': 39.1, 'batterWhiff': 38.1, 'pitcherK': 14.9}),
            row("Jake McCarthy", "L", "+1020", 56, "", ["vs Sears"], """0 HR, 86.6 mph EV, 12.5% barrels. Sears LHB split +1.13, HR risk -0.57. pitcher suppresses HR (-0.57); park/weather net drag (-7%).""", contact={'stars': 5, 'k': 16.1, 'batterK': 11.7, 'batterWhiff': 14.9, 'pitcherK': 15.7}),
            row("Troy Johnston", "L", "N/A", 44, "", ["vs Sears"], """0 HR, 90.5 mph EV. Sears LHB split +1.13, HR risk -0.57. pitcher suppresses HR (-0.57); park/weather net drag (-7%).""", contact={'stars': 3, 'k': 21.2, 'batterK': 21.5, 'batterWhiff': 27.5, 'pitcherK': 15.7}),
            row("Cole Carrigg", "S", "+740", 44, "", ["vs Sears"], """0 HR, 86.9 mph EV, 12.5% barrels. Sears SHB→RHB split -1.11, HR risk -0.57. tough split lane (-1.11); pitcher suppresses HR (-0.57).""", contact={'stars': 3, 'k': 23.4, 'batterK': 30.9, 'batterWhiff': 27.2, 'pitcherK': 15.7}),
            row("Adael Amador", "S", "+775", 40, "", ["vs Sears"], """0 HR, 77.4 mph EV. Sears SHB→RHB split -1.11, HR risk -0.57. tough split lane (-1.11); pitcher suppresses HR (-0.57).""", contact={'stars': 4, 'k': 18.0, 'batterK': 15.6, 'batterWhiff': 13.7, 'pitcherK': 15.7}),
        ],
    },
    {
        "title": "CWS @ STL - Sean Newcomb (L, CWS) vs Kyle Leahy (R, STL)",
        "kLines": {'Newcomb': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 21.7, 'matchupK': 20.1, 'ownK': 17.7}, 'Leahy': {'k': 5.8, 'lo': 4, 'hi': 7, 'bf': 20.9, 'matchupK': 27.6, 'ownK': 28.2}},
        "description": "Tail key data: Park boost -4%. Newcomb (HR risk -1.29, vs LHB -1.24, vs RHB -0.57). Leahy (HR risk 0.13, vs LHB +0.23, vs RHB -0.16).",
        "rows": [
            row("Joshua Baez", "R", "N/A", 76, "🌕 💣", ["vs Newcomb"], """2 HR, 2 near-HR, 92.6 mph EV, 12.5% barrels. Newcomb RHB split -0.57, HR risk -1.29. tough split lane (-0.57); pitcher suppresses HR (-1.29).""", blast="high", contact={'stars': 2, 'k': 25.7, 'batterK': 33.8, 'batterWhiff': 37.7, 'pitcherK': 17.7}),
            row("Nolan Gorman", "L", "+460", 76, "🌕 💣", ["vs Newcomb"], """1 HR, 3 near-HR, 98.2 mph EV, 37.5% barrels. Newcomb LHB split -1.24, HR risk -1.29. tough split lane (-1.24); pitcher suppresses HR (-1.29).""", blast="high", contact={'stars': 2, 'k': 26.2, 'batterK': 34.8, 'batterWhiff': 40.2, 'pitcherK': 17.7}),
            row("Jordan Walker", "R", "+453", 64, "", ["vs Newcomb"], """1 HR, 1 near-HR, 85.9 mph EV, 12.5% barrels. Newcomb RHB split -0.57, HR risk -1.29. tough split lane (-0.57); pitcher suppresses HR (-1.29).""", blast="good", contact={'stars': 2, 'k': 25.2, 'batterK': 30.6, 'batterWhiff': 37.1, 'pitcherK': 17.7}),
            row("Ivan Herrera", "R", "+680", 53, "", ["vs Newcomb"], """0 HR, 93.5 mph EV. Newcomb RHB split -0.57, HR risk -1.29. tough split lane (-0.57); pitcher suppresses HR (-1.29).""", blast="good", contact={'stars': 4, 'k': 19.8, 'batterK': 22.6, 'batterWhiff': 17.3, 'pitcherK': 17.7}),
            row("Alec Burleson", "L", "+475", 44, "", ["vs Newcomb"], """0 HR, 89.7 mph EV. Newcomb LHB split -1.24, HR risk -1.29. tough split lane (-1.24); pitcher suppresses HR (-1.29).""", contact={'stars': 4, 'k': 19.6, 'batterK': 18.1, 'batterWhiff': 23.9, 'pitcherK': 17.7}),
            row("Leonardo Bernal", "S", "+870", 50, "🚀", ["vs Newcomb"], """0 HR, 1 near-HR, 102.1 mph EV. Newcomb SHB→RHB split -0.57, HR risk -1.29. tough split lane (-0.57); pitcher suppresses HR (-1.29).""", blast="good", contact={'stars': 4, 'k': 19.5, 'batterK': 15.9, 'batterWhiff': 20.9, 'pitcherK': 17.7}),
            row("Munetaka Murakami", "L", "+422", 83, "💎", ["vs Leahy"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.9 mph EV, 12.5% barrels. Leahy LHB split +0.23, HR risk 0.13.""", blast="good", contact={'stars': 1, 'k': 35.1, 'batterK': 44.7, 'batterWhiff': 42.0, 'pitcherK': 28.2}),
            row("Andrew Benintendi", "L", "+870", 68, "💎", ["vs Leahy"], """Worst Pickz Hidden Gem. 0 HR, 96.1 mph EV, 12.5% barrels. Leahy LHB split +0.23, HR risk 0.13. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.8, 'batterK': 19.7, 'batterWhiff': 21.2, 'pitcherK': 28.2}),
            row("Tristan Peters", "L", "+1060", 68, "", ["vs Leahy"], """0 HR, 92.6 mph EV, 12.5% barrels. Leahy LHB split +0.23, HR risk 0.13. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.9, 'batterK': 18.1, 'batterWhiff': 23.8, 'pitcherK': 28.2}),
            row("Braden Montgomery", "S", "+1000", 50, "", ["vs Leahy"], """0 HR, 85.5 mph EV. Leahy SHB→LHB split +0.23, HR risk 0.13. limited recent HR events; lighter EV form (85.5 mph).""", contact={'stars': 3, 'k': 22.6, 'batterK': 10.4, 'batterWhiff': 27.6, 'pitcherK': 28.2}),
            row("Randal Grichuk", "R", "N/A", 69, "", ["vs Leahy"], """1 HR, 1 near-HR, 91.6 mph EV. Leahy RHB split -0.16, HR risk 0.13. slight split headwind (-0.16).""", blast="good", contact={'stars': 2, 'k': 24.9, 'batterK': 25.6, 'batterWhiff': 22.5, 'pitcherK': 28.2}),
        ],
    },
    {
        "title": "HOU @ TB - Peter Lambert (R, HOU) vs Ian Seymour 🧤 (L, TB)",
        "kLines": {'Lambert': {'k': 4.8, 'lo': 3, 'hi': 6, 'bf': 23.4, 'matchupK': 20.4, 'ownK': 23.2}, 'Seymour': {'k': 5.8, 'lo': 4, 'hi': 7, 'bf': 20.4, 'matchupK': 28.3, 'ownK': 30.1}},
        "description": "Tail key data: Park boost -3%. Lambert (HR risk -0.52, vs LHB -0.69, vs RHB +0.11). Seymour 🧤 (HR risk 1.70, vs LHB +0.58, vs RHB +1.59).",
        "rows": [
            row("Victor Mesa Jr.", "L", "+517", 89, "🌕 💣 💎", ["vs Lambert"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 95.5 mph EV, 37.5% barrels. Lambert LHB split -0.69, HR risk -0.52. tough split lane (-0.69); pitcher suppresses HR (-0.52).""", blast="high", contact={'stars': 3, 'k': 20.3, 'batterK': 10.1, 'batterWhiff': 25.2, 'pitcherK': 23.2}),
            row("Junior Caminero", "R", "+298", 87, "⭐ 🌕 💣", ["vs Lambert"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.5 mph EV, 25.0% barrels. Lambert RHB split +0.11, HR risk -0.52. pitcher suppresses HR (-0.52).""", blast="high", contact={'stars': 3, 'k': 20.2, 'batterK': 15.9, 'batterWhiff': 21.5, 'pitcherK': 23.2}),
            row("Ryan Vilade", "R", "N/A", 68, "💎", ["vs Lambert"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 83.3 mph EV, 12.5% barrels. Lambert RHB split +0.11, HR risk -0.52. pitcher suppresses HR (-0.52); lighter EV form (83.3 mph).""", blast="good", contact={'stars': 3, 'k': 23.7, 'batterK': 24.0, 'batterWhiff': 28.7, 'pitcherK': 23.2}),
            row("Nelson Velazquez", "R", "+347", 91, "🌕 💣", ["vs Seymour"], """1 HR, 1 near-HR, 90.9 mph EV, 12.5% barrels. Seymour RHB split +1.59, HR risk 1.70.""", blast="good", contact={'stars': 1, 'k': 32.9, 'batterK': 43.2, 'batterWhiff': 48.5, 'pitcherK': 30.1}),
            row("Yordan Alvarez", "L", "+335", 88, "🌕 💣", ["vs Seymour"], """1 HR, 1 near-HR, 93.1 mph EV. Seymour LHB split +0.58, HR risk 1.70.""", blast="good", contact={'stars': 2, 'k': 24.6, 'batterK': 20.9, 'batterWhiff': 18.8, 'pitcherK': 30.1}),
            row("Yainer Diaz", "R", "+650", 86, "", ["vs Seymour"], """1 HR, 2 near-HR, 91.1 mph EV. Seymour RHB split +1.59, HR risk 1.70.""", blast="good", contact={'stars': 2, 'k': 24.8, 'batterK': 18.2, 'batterWhiff': 22.3, 'pitcherK': 30.1}),
            row("Cam Smith", "R", "+563", 88, "🌕 💣", ["vs Seymour"], """1 HR, 1 near-HR, 82.7 mph EV, 12.5% barrels. Seymour RHB split +1.59, HR risk 1.70. lighter EV form (82.7 mph).""", blast="good", contact={'stars': 1, 'k': 28.3, 'batterK': 29.2, 'batterWhiff': 27.5, 'pitcherK': 30.1}),
            row("LaMonte Wade Jr.", "L", "N/A", 74, "", ["vs Seymour"], """0 HR, 94.8 mph EV. Seymour LHB split +0.58, HR risk 1.70. limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 28.8, 'batterK': 37.5, 'batterWhiff': 29.9, 'pitcherK': 30.1}),
            row("Daulton Varsho", "L", "+710", 79, "", ["vs Seymour"], """1 HR, 1 near-HR, 78.2 mph EV, 12.5% barrels. Seymour LHB split +0.58, HR risk 1.70. lighter EV form (78.2 mph).""", blast="good", contact={'stars': 2, 'k': 25.5, 'batterK': 20.5, 'batterWhiff': 23.5, 'pitcherK': 30.1}),
        ],
    },
    {
        "title": "KC @ BOS - Randy Dobnak (R, KC) vs Ranger Suarez (L, BOS)",
        "kLines": {'Dobnak': {'k': 4.2, 'lo': 3, 'hi': 6, 'bf': 22.3, 'matchupK': 19.0, 'ownK': 17.2}, 'Suarez': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 21.7, 'matchupK': 18.7, 'ownK': 18.4}},
        "description": "Tail key data: Park boost -10%. Dobnak (HR risk -0.08, vs LHB +0.42, vs RHB -1.15). Suarez (HR risk -0.81, vs LHB -0.59, vs RHB -0.36).",
        "rows": [
            row("Adley Rutschman", "S", "+680", 75, "⭐ 🌕 💣", ["vs Dobnak"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.1 mph EV, 25.0% barrels. Dobnak SHB→LHB split +0.42, HR risk -0.08. pitcher risk below avg (-0.08); park/weather net drag (-10%).""", blast="high", contact={'stars': 4, 'k': 19.3, 'batterK': 25.3, 'batterWhiff': 19.7, 'pitcherK': 17.2}),
            row("Mickey Gasper", "S", "+680", 82, "💎", ["vs Dobnak"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 91.3 mph EV, 12.5% barrels. Dobnak SHB→LHB split +0.42, HR risk -0.08. pitcher risk below avg (-0.08); park/weather net drag (-10%).""", blast="good", contact={'stars': 5, 'k': 16.1, 'batterK': 12.2, 'batterWhiff': 17.2, 'pitcherK': 17.2}),
            row("Wilyer Abreu", "L", "+410", 67, "", ["vs Dobnak"], """1 HR, 1 near-HR, 90.3 mph EV, 12.5% barrels. Dobnak LHB split +0.42, HR risk -0.08. pitcher risk below avg (-0.08); park/weather net drag (-10%).""", blast="good", contact={'stars': 4, 'k': 19.5, 'batterK': 22.7, 'batterWhiff': 23.9, 'pitcherK': 17.2}),
            row("Jarren Duran", "L", "+590", 72, "", ["vs Dobnak"], """1 HR, 2 near-HR, 92.3 mph EV, 12.5% barrels. Dobnak LHB split +0.42, HR risk -0.08. pitcher risk below avg (-0.08); park/weather net drag (-10%).""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 23.3, 'batterWhiff': 32.9, 'pitcherK': 17.2}),
            row("Roman Anthony", "L", "+550", 75, "💎", ["vs Dobnak"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.8 mph EV, 25.0% barrels. Dobnak LHB split +0.42, HR risk -0.08. pitcher risk below avg (-0.08); park/weather net drag (-10%).""", blast="good", contact={'stars': 3, 'k': 22.3, 'batterK': 29.7, 'batterWhiff': 29.1, 'pitcherK': 17.2}),
            row("Carter Jensen", "L", "+600", 65, "", ["vs Suarez"], """0 HR, 95.6 mph EV, 12.5% barrels. Suarez LHB split -0.59, HR risk -0.81. tough split lane (-0.59); pitcher suppresses HR (-0.81).""", blast="good", contact={'stars': 4, 'k': 19.8, 'batterK': 20.5, 'batterWhiff': 24.8, 'pitcherK': 18.4}),
            row("Vinnie Pasquantino", "L", "+880", 58, "", ["vs Suarez"], """0 HR, 2 near-HR, 93.4 mph EV, 12.5% barrels. Suarez LHB split -0.59, HR risk -0.81. tough split lane (-0.59); pitcher suppresses HR (-0.81).""", blast="good", contact={'stars': 5, 'k': 14.8, 'batterK': 9.0, 'batterWhiff': 13.5, 'pitcherK': 18.4}),
            row("Michael Massey", "L", "+1100", 40, "", ["vs Suarez"], """0 HR, 87.4 mph EV. Suarez LHB split -0.59, HR risk -0.81. tough split lane (-0.59); pitcher suppresses HR (-0.81).""", contact={'stars': 4, 'k': 18.5, 'batterK': 16.0, 'batterWhiff': 22.5, 'pitcherK': 18.4}),
        ],
    },
    {
        "title": "LAA @ WSH - Walbert Urena (R, LAA) vs Andrew Alvarez (L, WSH)",
        "kLines": {'Urena': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 22.2, 'matchupK': 22.4, 'ownK': 22.8}, 'Alvarez': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 21.0, 'matchupK': 22.2, 'ownK': 20.0}},
        "description": "Tail key data: Park boost +17%. Urena (HR risk -0.34, vs LHB -0.81, vs RHB +0.49). Alvarez (HR risk -0.47, vs LHB -0.26, vs RHB -0.26).",
        "rows": [
            row("Yohandy Morales", "R", "+469", 79, "", ["vs Urena"], """1 HR, 1 near-HR, 93.1 mph EV, 25.0% barrels. Urena RHB split +0.49, HR risk -0.34. pitcher risk below avg (-0.34).""", blast="good", contact={'stars': 2, 'k': 25.3, 'batterK': 34.8, 'batterWhiff': 40.9, 'pitcherK': 22.8}),
            row("Daylen Lile", "L", "+650", 84, "🚀 🌕 💣", ["vs Urena"], """1 HR, 1 near-HR, 100.1 mph EV, 25.0% barrels. Urena LHB split -0.81, HR risk -0.34. tough split lane (-0.81); pitcher risk below avg (-0.34).""", blast="high", contact={'stars': 3, 'k': 21.2, 'batterK': 20.0, 'batterWhiff': 21.1, 'pitcherK': 22.8}),
            row("Dylan Crews", "R", "+725", 52, "", ["vs Urena"], """0 HR, 89.2 mph EV. Urena RHB split +0.49, HR risk -0.34. pitcher risk below avg (-0.34); limited recent HR events.""", contact={'stars': 2, 'k': 24.7, 'batterK': 27.4, 'batterWhiff': 29.1, 'pitcherK': 22.8}),
            row("Keibert Ruiz", "S", "+800", 53, "", ["vs Urena"], """0 HR, 2 near-HR, 91.2 mph EV. Urena SHB→LHB split -0.81, HR risk -0.34. tough split lane (-0.81); pitcher risk below avg (-0.34).""", blast="good", contact={'stars': 4, 'k': 17.5, 'batterK': 7.4, 'batterWhiff': 15.0, 'pitcherK': 22.8}),
            row("James Wood", "L", "+390", 84, "🚀 ⭐ 🌕 💣", ["vs Urena"], """Worst Pickz Favorite. 0 HR, 100.2 mph EV, 25.0% barrels. Urena LHB split -0.81, HR risk -0.34. tough split lane (-0.81); pitcher risk below avg (-0.34).""", blast="high", contact={'stars': 3, 'k': 22.3, 'batterK': 22.0, 'batterWhiff': 24.4, 'pitcherK': 22.8}),
            row("Andrew Pinckney", "R", "N/A", 73, "", ["vs Urena"], """0 HR, 95.9 mph EV, 20.0% barrels. Urena RHB split +0.49, HR risk -0.34. pitcher risk below avg (-0.34); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.9, 'batterK': 30.8, 'batterWhiff': 31.6, 'pitcherK': 22.8}),
            row("Jose Siri", "R", "+500", 80, "", ["vs Alvarez"], """1 HR, 1 near-HR, 93.0 mph EV, 25.0% barrels. Alvarez RHB split -0.26, HR risk -0.47. slight split headwind (-0.26); pitcher suppresses HR (-0.47).""", blast="good", contact={'stars': 2, 'k': 25.7, 'batterK': 35.8, 'batterWhiff': 39.3, 'pitcherK': 20.0}),
            row("Travis d'Arnaud", "R", "+800", 72, "🌕 💣", ["vs Alvarez"], """1 HR, 1 near-HR, 97.3 mph EV, 20.0% barrels. Alvarez RHB split -0.26, HR risk -0.47. slight split headwind (-0.26); pitcher suppresses HR (-0.47).""", blast="high", contact={'stars': 3, 'k': 23.9, 'batterK': 39.5, 'batterWhiff': 31.5, 'pitcherK': 20.0}),
            row("Christian Moore", "R", "+880", 62, "", ["vs Alvarez"], """0 HR, 2 near-HR, 91.5 mph EV, 25.0% barrels. Alvarez RHB split -0.26, HR risk -0.47. slight split headwind (-0.26); pitcher suppresses HR (-0.47).""", blast="good", contact={'stars': 3, 'k': 23.4, 'batterK': 27.8, 'batterWhiff': 30.5, 'pitcherK': 20.0}),
        ],
    },
    {
        "title": "LAD @ MIA - Tyler Glasnow (R, LAD) vs Tyler Phillips (R, MIA)",
        "kLines": {'Glasnow': {'k': 6.5, 'lo': 5, 'hi': 8, 'bf': 21.8, 'matchupK': 29.9, 'ownK': 32.0}, 'Phillips': {'k': 4.2, 'lo': 3, 'hi': 6, 'bf': 20.0, 'matchupK': 21.0, 'ownK': 22.0}},
        "description": "Tail key data: Park boost -12%. Glasnow (HR risk 0.35, vs LHB -0.18, vs RHB +0.99). Phillips (HR risk 0.14, vs LHB +0.14, vs RHB +0.08).",
        "rows": [
            row("Kyle Stowers", "L", "+525", 78, "", ["vs Glasnow"], """0 HR, 96.2 mph EV, 12.5% barrels. Glasnow LHB split -0.18, HR risk 0.35. slight split headwind (-0.18); park/weather net drag (-12%).""", blast="good", contact={'stars': 1, 'k': 33.8, 'batterK': 33.3, 'batterWhiff': 39.2, 'pitcherK': 32.0}),
            row("Otto Lopez", "R", "+1040", 66, "💎", ["vs Glasnow"], """Worst Pickz Hidden Gem. 0 HR, 97.2 mph EV, 12.5% barrels. Glasnow RHB split +0.99, HR risk 0.35. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 12.4, 'batterWhiff': 20.0, 'pitcherK': 32.0}),
            row("Owen Caissie", "L", "+920", 81, "", ["vs Glasnow"], """1 HR, 2 near-HR, 95.2 mph EV, 25.0% barrels. Glasnow LHB split -0.18, HR risk 0.35. slight split headwind (-0.18); park/weather net drag (-12%).""", blast="good", contact={'stars': 1, 'k': 31.1, 'batterK': 33.3, 'batterWhiff': 32.1, 'pitcherK': 32.0}),
            row("Javier Sanoja", "R", "+1300", 68, "", ["vs Glasnow"], """1 HR, 1 near-HR, 96.8 mph EV, 12.5% barrels. Glasnow RHB split +0.99, HR risk 0.35. park/weather net drag (-12%).""", blast="good", contact={'stars': 4, 'k': 19.5, 'batterK': 6.0, 'batterWhiff': 11.7, 'pitcherK': 32.0}),
            row("Griffin Conine", "L", "+591", 66, "", ["vs Glasnow"], """0 HR, 1 near-HR, 88.3 mph EV, 12.5% barrels. Glasnow LHB split -0.18, HR risk 0.35. slight split headwind (-0.18); park/weather net drag (-12%).""", contact={'stars': 1, 'k': 31.6, 'batterK': 28.2, 'batterWhiff': 35.9, 'pitcherK': 32.0}),
            row("Joe Mack", "L", "+920", 62, "", ["vs Glasnow"], """0 HR, 93.6 mph EV. Glasnow LHB split -0.18, HR risk 0.35. slight split headwind (-0.18); park/weather net drag (-12%).""", blast="good", contact={'stars': 1, 'k': 28.5, 'batterK': 26.7, 'batterWhiff': 25.4, 'pitcherK': 32.0}),
            row("Teoscar Hernandez", "R", "+600", 68, "", ["vs Phillips"], """0 HR, 1 near-HR, 93.2 mph EV, 12.5% barrels. Phillips RHB split +0.08, HR risk 0.14. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.8, 'batterK': 26.2, 'batterWhiff': 33.8, 'pitcherK': 22.0}),
            row("Mookie Betts", "R", "+880", 68, "💎", ["vs Phillips"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.1 mph EV, 25.0% barrels. Phillips RHB split +0.08, HR risk 0.14. park/weather net drag (-12%).""", blast="good", contact={'stars': 5, 'k': 15.6, 'batterK': 8.5, 'batterWhiff': 12.0, 'pitcherK': 22.0}),
            row("Kyle Tucker", "L", "+700", 55, "", ["vs Phillips"], """0 HR, 1 near-HR, 90.8 mph EV, 12.5% barrels. Phillips LHB split +0.14, HR risk 0.14. park/weather net drag (-12%); limited recent HR events.""", contact={'stars': 4, 'k': 17.5, 'batterK': 10.1, 'batterWhiff': 16.3, 'pitcherK': 22.0}),
            row("Freddie Freeman", "L", "+725", 58, "", ["vs Phillips"], """0 HR, 1 near-HR, 90.0 mph EV. Phillips LHB split +0.14, HR risk 0.14. park/weather net drag (-12%); limited recent HR events.""", contact={'stars': 3, 'k': 22.2, 'batterK': 21.8, 'batterWhiff': 26.3, 'pitcherK': 22.0}),
            row("Alex Freeland", "S", "+1200", 61, "", ["vs Phillips"], """0 HR, 93.7 mph EV, 12.5% barrels. Phillips SHB→LHB split +0.14, HR risk 0.14. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.6, 'batterK': 34.0, 'batterWhiff': 30.9, 'pitcherK': 22.0}),
        ],
    },
    {
        "title": "NYM @ NYY - Zach Thornton 🧤 (L, NYM) vs Gerrit Cole (R, NYY)",
        "kLines": {'Thornton': {'k': 4.8, 'lo': 3, 'hi': 6, 'bf': 21.7, 'matchupK': 22.2, 'ownK': None}, 'Cole': {'k': 6.0, 'lo': 4, 'hi': 8, 'bf': 23.3, 'matchupK': 25.7, 'ownK': 26.8}},
        "description": "Tail key data: Park boost -1%. Thornton 🧤 (HR risk 1.56, vs LHB +0.22, vs RHB +1.67). Cole (HR risk 0.84, vs LHB +0.03, vs RHB +1.08).",
        "rows": [
            row("Heliot Ramos", "R", "+423", 92, "⭐ 🌕 💣", ["vs Thornton"], """Worst Pickz Favorite. 0 HR, 95.6 mph EV, 12.5% barrels. Thornton RHB split +1.67, HR risk 1.56. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.6, 'batterK': 25.0, 'batterWhiff': 31.0, 'pitcherK': 18.2}),
            row("Aaron Judge", "R", "+215", 88, "🌕 💣 💎", ["vs Thornton"], """Worst Pickz Hidden Gem. 0 HR, 98.6 mph EV. Thornton RHB split +1.67, HR risk 1.56. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.8, 'batterK': 26.4, 'batterWhiff': 28.9, 'pitcherK': 18.2}),
            row("Amed Rosario", "R", "+600", 90, "🌕 💣", ["vs Thornton"], """0 HR, 1 near-HR, 96.9 mph EV, 12.5% barrels. Thornton RHB split +1.67, HR risk 1.56. limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.7, 'batterK': 21.6, 'batterWhiff': 23.6, 'pitcherK': 18.2}),
            row("Cody Bellinger", "L", "+420", 69, "", ["vs Thornton"], """0 HR, 92.1 mph EV. Thornton LHB split +0.22, HR risk 1.56. limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 17.4, 'batterK': 15.5, 'batterWhiff': 19.5, 'pitcherK': 18.2}),
            row("Luis Torrens", "R", "N/A", 96, "🌕 💣", ["vs Cole"], """3 HR, 3 near-HR, 98.2 mph EV, 37.5% barrels. Cole RHB split +1.08, HR risk 0.84.""", blast="high", contact={'stars': 3, 'k': 22.2, 'batterK': 16.9, 'batterWhiff': 18.1, 'pitcherK': 26.8}),
            row("Marcus Semien", "R", "+610", 77, "", ["vs Cole"], """0 HR, 1 near-HR, 94.6 mph EV, 25.0% barrels. Cole RHB split +1.08, HR risk 0.84. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.7, 'batterK': 10.1, 'batterWhiff': 21.0, 'pitcherK': 26.8}),
            row("Brett Baty", "L", "+670", 93, "🌕 💣", ["vs Cole"], """2 HR, 3 near-HR, 95.7 mph EV, 25.0% barrels. Cole LHB split +0.03, HR risk 0.84.""", blast="high", contact={'stars': 2, 'k': 26.9, 'batterK': 22.6, 'batterWhiff': 34.3, 'pitcherK': 26.8}),
            row("Francisco Lindor", "S", "+360", 82, "", ["vs Cole"], """1 HR, 1 near-HR, 89.2 mph EV, 12.5% barrels. Cole SHB→LHB split +0.03, HR risk 0.84.""", blast="good", contact={'stars': 2, 'k': 24.5, 'batterK': 21.7, 'batterWhiff': 24.3, 'pitcherK': 26.8}),
            row("Juan Soto", "L", "+282", 86, "", ["vs Cole"], """0 HR, 1 near-HR, 93.5 mph EV, 12.5% barrels. Cole LHB split +0.03, HR risk 0.84. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 15.1, 'batterWhiff': 29.4, 'pitcherK': 26.8}),
            row("Bo Bichette", "R", "+680", 77, "", ["vs Cole"], """1 HR, 1 near-HR, 82.4 mph EV, 12.5% barrels. Cole RHB split +1.08, HR risk 0.84. lighter EV form (82.4 mph).""", blast="good", contact={'stars': 3, 'k': 22.8, 'batterK': 18.4, 'batterWhiff': 20.9, 'pitcherK': 26.8}),
        ],
    },
    {
        "title": "PHI @ ATL - Tim Mayza (L, PHI) vs Tyler Mahle (R, ATL)",
        "kLines": {'Mayza': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 21.7, 'matchupK': 21.6, 'ownK': 20.5}, 'Mahle': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 22.5, 'matchupK': 22.1, 'ownK': 23.2}},
        "description": "Tail key data: Park boost +0%. Mayza (BAA vs LHB .212, vs RHB .227, HR/9 0.88). Mahle (HR risk -0.20, vs LHB -0.41, vs RHB +0.13).",
        "rows": [
            row("Austin Riley", "R", "+650", 69, "💎", ["vs Mayza"], """Worst Pickz Hidden Gem. 0 HR, 93.3 mph EV, 12.5% barrels. limited split/risk sample; limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.5, 'batterK': 32.4, 'batterWhiff': 27.1, 'pitcherK': 20.5}),
            row("Ronald Acuna Jr.", "R", "+450", 53, "", ["vs Mayza"], """0 HR, 90.4 mph EV. limited split/risk sample; limited recent HR events.""", contact={'stars': 3, 'k': 21.8, 'batterK': 19.5, 'batterWhiff': 28.8, 'pitcherK': 20.5}),
            row("Brewer Hicklen", "R", "+880", 63, "🚀", ["vs Mayza"], """0 HR, 109.1 mph EV. limited split/risk sample; limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.5, 'batterK': 33.3, 'batterWhiff': 42.9, 'pitcherK': 20.5}),
            row("Ozzie Albies", "S", "+620", 44, "", ["vs Mayza"], """0 HR, 88.9 mph EV. limited split/risk sample; limited recent HR events.""", contact={'stars': 4, 'k': 19.3, 'batterK': 17.3, 'batterWhiff': 17.8, 'pitcherK': 20.5}),
            row("Trea Turner", "R", "+650", 79, "🌕 💣 💎", ["vs Mahle"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 94.9 mph EV, 12.5% barrels. Mahle RHB split +0.13, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="high", contact={'stars': 3, 'k': 23.4, 'batterK': 20.0, 'batterWhiff': 32.2, 'pitcherK': 23.2}),
            row("Kyle Schwarber", "L", "+270", 72, "", ["vs Mahle"], """1 HR, 1 near-HR, 90.1 mph EV, 12.5% barrels. Mahle LHB split -0.41, HR risk -0.20. tough split lane (-0.41); pitcher risk below avg (-0.20).""", blast="good", contact={'stars': 2, 'k': 25.1, 'batterK': 26.1, 'batterWhiff': 31.4, 'pitcherK': 23.2}),
            row("Bryson Stott", "L", "+900", 63, "", ["vs Mahle"], """1 HR, 2 near-HR, 92.8 mph EV, 25.0% barrels. Mahle LHB split -0.41, HR risk -0.20. tough split lane (-0.41); pitcher risk below avg (-0.20).""", blast="good", contact={'stars': 3, 'k': 22.3, 'batterK': 21.9, 'batterWhiff': 23.0, 'pitcherK': 23.2}),
            row("Bryce Harper", "L", "+450", 59, "", ["vs Mahle"], """0 HR, 90.2 mph EV. Mahle LHB split -0.41, HR risk -0.20. tough split lane (-0.41); pitcher risk below avg (-0.20).""", contact={'stars': 2, 'k': 25.9, 'batterK': 27.1, 'batterWhiff': 34.5, 'pitcherK': 23.2}),
            row("Brandon Marsh", "L", "+775", 64, "💎", ["vs Mahle"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.3 mph EV, 12.5% barrels. Mahle LHB split -0.41, HR risk -0.20. tough split lane (-0.41); pitcher risk below avg (-0.20).""", blast="good", contact={'stars': 3, 'k': 22.8, 'batterK': 24.0, 'batterWhiff': 24.1, 'pitcherK': 23.2}),
        ],
    },
    {
        "title": "PIT @ CHC - Paul Skenes (R, PIT) vs Clay Holmes (R, CHC)",
        "kLines": {'Skenes': {'k': 5.1, 'lo': 3, 'hi': 7, 'bf': 22.0, 'matchupK': 23.2, 'ownK': 26.4}, 'Holmes': {'k': 4.9, 'lo': 3, 'hi': 7, 'bf': 22.8, 'matchupK': 21.6, 'ownK': 20.1}},
        "description": "Tail key data: Park boost +21%. Skenes (HR risk -0.47, vs LHB -0.47, vs RHB -0.18). Holmes (HR risk -1.08, vs LHB -1.24, vs RHB -0.14).",
        "rows": [
            row("Pete Crow Armstrong", "L", "+285", 91, "🌕 💣 💎", ["vs Skenes"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 97.6 mph EV, 25.0% barrels. Skenes LHB split -0.47, HR risk -0.47. tough split lane (-0.47); pitcher suppresses HR (-0.47).""", blast="high", contact={'stars': 3, 'k': 23.1, 'batterK': 20.2, 'batterWhiff': 21.9, 'pitcherK': 26.4}),
            row("Seiya Suzuki", "R", "+420", 65, "", ["vs Skenes"], """0 HR, 90.8 mph EV, 12.5% barrels. Skenes RHB split -0.18, HR risk -0.47. slight split headwind (-0.18); pitcher suppresses HR (-0.47).""", contact={'stars': 3, 'k': 20.4, 'batterK': 14.7, 'batterWhiff': 17.1, 'pitcherK': 26.4}),
            row("BJ Murray Jr.", "S", "N/A", 59, "", ["vs Skenes"], """0 HR, 97.9 mph EV. Skenes SHB→LHB split -0.47, HR risk -0.47. tough split lane (-0.47); pitcher suppresses HR (-0.47).""", blast="good", contact={'stars': 3, 'k': 23.7, 'batterK': 36.4, 'batterWhiff': 16.7, 'pitcherK': 26.4}),
            row("Bryan Reynolds", "S", "+590", 72, "💎", ["vs Holmes"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 96.8 mph EV, 37.5% barrels. Holmes SHB→LHB split -1.24, HR risk -1.08. tough split lane (-1.24); pitcher suppresses HR (-1.08).""", blast="good", contact={'stars': 4, 'k': 19.0, 'batterK': 14.8, 'batterWhiff': 25.0, 'pitcherK': 20.1}),
            row("Ryan O'Hearn", "L", "+575", 55, "", ["vs Holmes"], """0 HR, 92.7 mph EV. Holmes LHB split -1.24, HR risk -1.08. tough split lane (-1.24); pitcher suppresses HR (-1.08).""", blast="good", contact={'stars': 3, 'k': 20.0, 'batterK': 19.8, 'batterWhiff': 22.6, 'pitcherK': 20.1}),
            row("Oneil Cruz", "L", "+350", 71, "", ["vs Holmes"], """1 HR, 1 near-HR, 87.9 mph EV, 12.5% barrels. Holmes LHB split -1.24, HR risk -1.08. tough split lane (-1.24); pitcher suppresses HR (-1.08).""", blast="good", contact={'stars': 2, 'k': 24.4, 'batterK': 29.8, 'batterWhiff': 32.6, 'pitcherK': 20.1}),
            row("Brandon Lowe", "L", "+431", 54, "⭐", ["vs Holmes"], """Worst Pickz Favorite. 0 HR, 92.6 mph EV. Holmes LHB split -1.24, HR risk -1.08. tough split lane (-1.24); pitcher suppresses HR (-1.08).""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 26.5, 'batterWhiff': 32.5, 'pitcherK': 20.1}),
        ],
    },
    {
        "title": "SD @ SF - Michael King (R, SD) vs Cesar Perdomo (L, SF)",
        "kLines": {'King': {'k': 4.9, 'lo': 3, 'hi': 7, 'bf': 23.3, 'matchupK': 21.0, 'ownK': 21.4}, 'Perdomo': {'k': 4.9, 'lo': 3, 'hi': 7, 'bf': 21.5, 'matchupK': 22.9, 'ownK': 22.9}},
        "description": "Tail key data: Park boost -14%. King (HR risk -0.04, vs LHB +0.05, vs RHB -0.31). Perdomo (HR risk -0.35, vs LHB +1.71, vs RHB -1.34).",
        "rows": [
            row("Rafael Devers", "L", "+401", 90, "🚀 ⭐ 🌕 💣", ["vs King"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 102.9 mph EV, 37.5% barrels. King LHB split +0.05, HR risk -0.04. pitcher risk below avg (-0.04); park/weather net drag (-14%).""", blast="high", contact={'stars': 3, 'k': 21.8, 'batterK': 20.9, 'batterWhiff': 27.7, 'pitcherK': 21.4}),
            row("Bryce Eldridge", "L", "+585", 68, "⭐", ["vs King"], """Worst Pickz Favorite. 0 HR, 96.9 mph EV. King LHB split +0.05, HR risk -0.04. pitcher risk below avg (-0.04); park/weather net drag (-14%).""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 26.7, 'batterWhiff': 27.2, 'pitcherK': 21.4}),
            row("Andrew Knizner", "R", "N/A", 48, "", ["vs King"], """0 HR, 1 near-HR, 90.7 mph EV, 14.3% barrels. King RHB split -0.31, HR risk -0.04. slight split headwind (-0.31); pitcher risk below avg (-0.04).""", contact={'stars': 3, 'k': 22.3, 'batterK': 22.9, 'batterWhiff': 27.1, 'pitcherK': 21.4}),
            row("Sung-Mun Song", "L", "N/A", 55, "", ["vs Perdomo"], """0 HR, 94.9 mph EV. Perdomo LHB split +1.71, HR risk -0.35. pitcher risk below avg (-0.35); park/weather net drag (-14%).""", blast="good", contact={'stars': 3, 'k': 20.5, 'batterK': 21.9, 'batterWhiff': 15.1, 'pitcherK': 22.9}),
            row("Jase Bowen", "R", "N/A", 76, "🚀 🌕 💣", ["vs Perdomo"], """2 HR, 2 near-HR, 100.2 mph EV, 25.0% barrels. Perdomo RHB split -1.34, HR risk -0.35. tough split lane (-1.34); pitcher risk below avg (-0.35).""", blast="high", contact={'stars': 3, 'k': 23.5, 'batterK': 31.3, 'batterWhiff': 34.2, 'pitcherK': 22.9}),
            row("Jackson Merrill", "L", "+590", 67, "", ["vs Perdomo"], """0 HR, 2 near-HR, 84.2 mph EV, 12.5% barrels. Perdomo LHB split +1.71, HR risk -0.35. pitcher risk below avg (-0.35); park/weather net drag (-14%).""", blast="good", contact={'stars': 3, 'k': 21.5, 'batterK': 18.6, 'batterWhiff': 25.9, 'pitcherK': 22.9}),
            row("Manny Machado", "R", "+570", 58, "", ["vs Perdomo"], """1 HR, 1 near-HR, 87.8 mph EV, 12.5% barrels. Perdomo RHB split -1.34, HR risk -0.35. tough split lane (-1.34); pitcher risk below avg (-0.35).""", blast="good", contact={'stars': 3, 'k': 21.3, 'batterK': 20.2, 'batterWhiff': 22.9, 'pitcherK': 22.9}),
            row("Fernando Tatis Jr.", "R", "+531", 54, "", ["vs Perdomo"], """0 HR, 87.8 mph EV. Perdomo RHB split -1.34, HR risk -0.35. tough split lane (-1.34); pitcher risk below avg (-0.35).""", contact={'stars': 3, 'k': 20.5, 'batterK': 17.0, 'batterWhiff': 23.3, 'pitcherK': 22.9}),
        ],
    },
    {
        "title": "SEA @ ATH - Bryan Woo (R, SEA) vs Gage Jump (L, ATH)",
        "kLines": {'Woo': {'k': 5.5, 'lo': 4, 'hi': 7, 'bf': 21.7, 'matchupK': 25.1, 'ownK': 26.1}, 'Jump': {'k': 5.5, 'lo': 4, 'hi': 7, 'bf': 22.2, 'matchupK': 24.9, 'ownK': 26.2}},
        "description": "Tail key data: Park boost +42%. Woo (HR risk 0.69, vs LHB +0.54, vs RHB +0.33). Jump (HR risk 0.25, vs LHB -0.76, vs RHB +0.65).",
        "rows": [
            row("Lawrence Butler", "L", "+422", 89, "🌕 💣 💎", ["vs Woo"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 89.5 mph EV, 12.5% barrels. Woo LHB split +0.54, HR risk 0.69.""", blast="good", contact={'stars': 2, 'k': 27.1, 'batterK': 31.4, 'batterWhiff': 25.3, 'pitcherK': 26.1}),
            row("Zack Gelof", "R", "+490", 88, "🌕 💣 💎", ["vs Woo"], """Worst Pickz Hidden Gem. 0 HR, 98.5 mph EV. Woo RHB split +0.33, HR risk 0.69. limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 27.5, 'batterK': 27.3, 'batterWhiff': 33.7, 'pitcherK': 26.1}),
            row("Michael Stefanic", "R", "N/A", 77, "", ["vs Woo"], """0 HR, 96.2 mph EV. Woo RHB split +0.33, HR risk 0.69. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.5, 'batterK': 15.0, 'batterWhiff': 13.9, 'pitcherK': 26.1}),
            row("Max Muncy", "R", "+530", 70, "", ["vs Woo"], """0 HR, 84.9 mph EV. Woo RHB split +0.33, HR risk 0.69. limited recent HR events; lighter EV form (84.9 mph).""", contact={'stars': 2, 'k': 25.6, 'batterK': 24.3, 'batterWhiff': 28.7, 'pitcherK': 26.1}),
            row("Jonah Heim", "S", "+560", 65, "", ["vs Woo"], """0 HR, 90.9 mph EV. Woo SHB→LHB split +0.54, HR risk 0.69. limited recent HR events.""", contact={'stars': 3, 'k': 21.0, 'batterK': 17.3, 'batterWhiff': 15.0, 'pitcherK': 26.1}),
            row("Dominic Canzone", "L", "+426", 86, "🌕 💣", ["vs Jump"], """0 HR, 1 near-HR, 99.2 mph EV, 25.0% barrels. Jump LHB split -0.76, HR risk 0.25. tough split lane (-0.76); limited recent HR events.""", blast="high", contact={'stars': 2, 'k': 25.1, 'batterK': 25.8, 'batterWhiff': 23.7, 'pitcherK': 26.2}),
            row("Cole Young", "L", "+800", 79, "", ["vs Jump"], """0 HR, 3 near-HR, 92.4 mph EV, 25.0% barrels. Jump LHB split -0.76, HR risk 0.25. tough split lane (-0.76).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 19.5, 'batterWhiff': 22.9, 'pitcherK': 26.2}),
            row("Julio Rodriguez", "R", "+400", 64, "", ["vs Jump"], """0 HR, 85.3 mph EV. Jump RHB split +0.65, HR risk 0.25. limited recent HR events; lighter EV form (85.3 mph)."""),
        ],
    },
    {
        "title": "TEX @ ARI - Kumar Rocker (R, TEX) vs Brandon Pfaadt (R, ARI)",
        "kLines": {'Rocker': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 21.8, 'matchupK': 20.7, 'ownK': 22.9}, 'Pfaadt': {'k': 3.9, 'lo': 2, 'hi': 6, 'bf': 23.4, 'matchupK': 16.6, 'ownK': 14.3}},
        "description": "Tail key data: Park boost -9%. Rocker (HR risk 0.46, vs LHB +0.50, vs RHB -0.32). Pfaadt (HR risk 0.14, vs LHB +0.66, vs RHB -0.56).",
        "rows": [
            row("Lars Nootbaar", "L", "+650", 69, "💎", ["vs Rocker"], """Worst Pickz Hidden Gem. 0 HR, 92.6 mph EV. Rocker LHB split +0.50, HR risk 0.46. park/weather net drag (-9%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.2, 'batterK': 14.3, 'batterWhiff': 15.5, 'pitcherK': 22.9}),
            row("Corbin Carroll", "L", "+500", 81, "", ["vs Rocker"], """0 HR, 1 near-HR, 94.9 mph EV, 37.5% barrels. Rocker LHB split +0.50, HR risk 0.46. park/weather net drag (-9%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.2, 'batterK': 25.3, 'batterWhiff': 29.2, 'pitcherK': 22.9}),
            row("Tim Tawa", "R", "+810", 87, "🌕 💣", ["vs Rocker"], """2 HR, 2 near-HR, 89.7 mph EV, 25.0% barrels. Rocker RHB split -0.32, HR risk 0.46. slight split headwind (-0.32); park/weather net drag (-9%).""", blast="high", contact={'stars': 2, 'k': 25.7, 'batterK': 29.7, 'batterWhiff': 32.2, 'pitcherK': 22.9}),
            row("Joc Pederson", "L", "+399", 72, "", ["vs Pfaadt"], """1 HR, 1 near-HR, 84.1 mph EV, 12.5% barrels. Pfaadt LHB split +0.66, HR risk 0.14. park/weather net drag (-9%); lighter EV form (84.1 mph).""", blast="good", contact={'stars': 4, 'k': 18.1, 'batterK': 22.9, 'batterWhiff': 27.1, 'pitcherK': 14.3}),
            row("Brandon Nimmo", "L", "+725", 64, "", ["vs Pfaadt"], """0 HR, 93.7 mph EV. Pfaadt LHB split +0.66, HR risk 0.14. park/weather net drag (-9%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 17.9, 'batterK': 23.0, 'batterWhiff': 25.3, 'pitcherK': 14.3}),
            row("Corey Seager", "L", "+425", 86, "🌕 💣", ["vs Pfaadt"], """2 HR, 2 near-HR, 86.9 mph EV, 25.0% barrels. Pfaadt LHB split +0.66, HR risk 0.14. park/weather net drag (-9%); lighter EV form (86.9 mph).""", blast="high", contact={'stars': 4, 'k': 17.9, 'batterK': 19.3, 'batterWhiff': 31.3, 'pitcherK': 14.3}),
            row("Wyatt Langford", "R", "+550", 62, "", ["vs Pfaadt"], """1 HR, 1 near-HR, 85.7 mph EV, 12.5% barrels. Pfaadt RHB split -0.56, HR risk 0.14. tough split lane (-0.56); park/weather net drag (-9%).""", blast="good", contact={'stars': 5, 'k': 16.7, 'batterK': 19.1, 'batterWhiff': 23.3, 'pitcherK': 14.3}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-12")

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

    out = ROOT / '_games-0912.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
