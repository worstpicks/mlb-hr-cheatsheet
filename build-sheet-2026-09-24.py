#!/usr/bin/env python3
"""Generate games[] block for 2026-09-24 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Brett Baty (L)",
    "Dominic Canzone (L)",
    "Elly De La Cruz (S)",
    "Heliot Ramos (R)",
    "Lazaro Montes (L)",
    "Max Muncy (L)",
    "Mickey Gasper (S)",
    "Rafael Flores (R)",
    "Spencer Jones (L)",
    "Vinnie Pasquantino (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Adley Rutschman (S)",
    "Agustin Ramirez (R)",
    "Alex Freeland (S)",
    "Andrew Benintendi (L)",
    "Bo Naylor (L)",
    "Brandon Marsh (L)",
    "Bryson Stott (L)",
    "Christian Walker (R)",
    "Francisco Lindor (S)",
    "Heriberto Hernandez (R)",
    "Jac Caglianone (L)",
    "Jackson Merrill (L)",
    "Jonathan Aranda (L)",
    "Jose Ramirez (S)",
    "Junior Caminero (R)",
    "Ketel Marte (S)",
    "Lawrence Butler (L)",
    "Michael Harris II (L)",
    "Mike Trout (R)",
    "Patrick Bailey (S)",
    "Sam Antonacci (L)",
    "Victor Mesa Jr. (L)",
    "Zach Neto (R)",
}

PLAYER_TEAMS = {
    "A.J. Ewing (L)": "NYM",
    "Adley Rutschman (S)": "BOS",
    "Agustin Ramirez (R)": "MIA",
    "Alec Burleson (L)": "STL",
    "Alex Freeland (S)": "LAD",
    "Andrew Benintendi (L)": "CWS",
    "Angel Martinez (S)": "CLE",
    "Bo Naylor (L)": "MIL",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Brett Baty (L)": "NYM",
    "Bryan De La Cruz (R)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Chase DeLauter (L)": "CLE",
    "Christian Walker (R)": "HOU",
    "Cole Young (L)": "SEA",
    "Connor Norby (R)": "COL",
    "Corbin Carroll (L)": "ARI",
    "Dane Myers (R)": "CIN",
    "Dansby Swanson (R)": "CHC",
    "Dominic Canzone (L)": "SEA",
    "Elly De La Cruz (S)": "CIN",
    "Eugenio Suarez (R)": "CIN",
    "Ezequiel Duran (R)": "TEX",
    "Francisco Lindor (S)": "NYM",
    "Griffin Conine (L)": "MIA",
    "Heliot Ramos (R)": "NYY",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Isaac Paredes (R)": "HOU",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jake Cronenworth (L)": "SD",
    "James McCann (R)": "ARI",
    "Joey Ortiz (R)": "MIL",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Jose Ramirez (S)": "CLE",
    "Josh Jung (R)": "TEX",
    "Josh Lowe (L)": "LAA",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Ketel Marte (S)": "ARI",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Kyle Teel (L)": "CWS",
    "Lawrence Butler (L)": "ATH",
    "Lazaro Montes (L)": "SEA",
    "Leonardo Bernal (S)": "STL",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Mickey Gasper (S)": "BOS",
    "Mike Trout (R)": "LAA",
    "Moises Ballesteros (L)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Ozzie Albies (S)": "ATL",
    "Patrick Bailey (S)": "CLE",
    "Paul Goldschmidt (R)": "NYY",
    "Pavin Smith (L)": "ARI",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Flores (R)": "PIT",
    "Roman Anthony (L)": "BOS",
    "Ryan O'Hearn (L)": "PIT",
    "Sal Stewart (R)": "CIN",
    "Sam Antonacci (L)": "CWS",
    "Seiya Suzuki (R)": "CHC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "TJ Rumfield (L)": "COL",
    "Taylor Trammell (L)": "HOU",
    "Teoscar Hernandez (R)": "LAD",
    "Victor Mesa Jr. (L)": "TB",
    "Vinnie Pasquantino (L)": "KC",
    "Wade Meckler (L)": "LAA",
    "Wyatt Langford (R)": "TEX",
    "Xander Bogaerts (R)": "SD",
    "Yainer Diaz (R)": "HOU",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("CIN @ ATL", "Singer"),
    ("HOU @ ATH", "Barnett"),
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
        "title": "ARI @ COL - Eduardo Rodriguez (L, ARI) vs Tanner Gordon (R, COL)",
        "kLines": {'Rodriguez': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 24.1, 'matchupK': 20.6, 'ownK': 21.1}, 'Gordon': {'k': 3.9, 'lo': 2, 'hi': 6, 'bf': 22.0, 'matchupK': 17.8, 'ownK': 17.5}},
        "description": "Tail key data: Park boost +13% (stadium +20%, weather -7%). Rodriguez (HR risk -0.55, vs LHB +0.54, vs RHB -0.54). Gordon (HR risk 0.51, vs LHB +0.49, vs RHB +0.32).",
        "rows": [
            row("Kyle Karros", "R", "+600", 70, "🌕 💣", ["vs Eduardo Rodriguez"], """2 HR, 2 near-HR, 82.7 mph EV, 25.0% barrels. Eduardo Rodriguez RHB split -0.54, HR risk -0.55. tough split lane (-0.54); pitcher suppresses HR (-0.55).""", blast="high", contact={'stars': 3, 'k': 20.6, 'batterK': 18.8, 'batterWhiff': 24.2, 'pitcherK': 21.1}),
            row("TJ Rumfield", "L", "+870", 51, "", ["vs Eduardo Rodriguez"], """0 HR, 87.6 mph EV, 12.5% barrels. Eduardo Rodriguez LHB split +0.54, HR risk -0.55. pitcher suppresses HR (-0.55); weather carry headwind (-7%).""", contact={'stars': 5, 'k': 17.2, 'batterK': 14.0, 'batterWhiff': 13.0, 'pitcherK': 21.1}),
            row("Connor Norby", "R", "+560", 61, "", ["vs Eduardo Rodriguez"], """0 HR, 3 near-HR, 90.4 mph EV, 12.5% barrels. Eduardo Rodriguez RHB split -0.54, HR risk -0.55. tough split lane (-0.54); pitcher suppresses HR (-0.55).""", blast="good", contact={'stars': 3, 'k': 21.4, 'batterK': 24.7, 'batterWhiff': 21.0, 'pitcherK': 21.1}),
            row("Pavin Smith", "L", "+503", 71, "", ["vs Gordon"], """0 HR, 1 near-HR, 98.6 mph EV. Gordon LHB split +0.49, HR risk 0.51. weather carry headwind (-7%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.5, 'batterK': 17.7, 'batterWhiff': 20.9, 'pitcherK': 17.5}),
            row("Corbin Carroll", "L", "+307", 87, "", ["vs Gordon"], """1 HR, 1 near-HR, 91.1 mph EV, 12.5% barrels. Gordon LHB split +0.49, HR risk 0.51. weather carry headwind (-7%).""", blast="good", contact={'stars': 3, 'k': 21.8, 'batterK': 26.8, 'batterWhiff': 29.1, 'pitcherK': 17.5}),
            row("Ketel Marte", "S", "+357", 69, "💎", ["vs Gordon"], """Worst Pickz Hidden Gem. 0 HR, 93.3 mph EV. Gordon SHB→LHB split +0.49, HR risk 0.51. weather carry headwind (-7%); limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 14.6, 'batterK': 9.9, 'batterWhiff': 12.8, 'pitcherK': 17.5}),
            row("James McCann", "R", "+540", 72, "", ["vs Gordon"], """0 HR, 1 near-HR, 94.3 mph EV. Gordon RHB split +0.32, HR risk 0.51. weather carry headwind (-7%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.9, 'batterK': 26.2, 'batterWhiff': 31.9, 'pitcherK': 17.5}),
        ],
    },
    {
        "title": "CIN @ ATL - Brady Singer 🧤 (R, CIN) vs Tyler Mahle (R, ATL)",
        "kLines": {'Singer': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 23.3, 'matchupK': 15.9, 'ownK': 14.6}, 'Mahle': {'k': 5.7, 'lo': 4, 'hi': 7, 'bf': 22.6, 'matchupK': 25.3, 'ownK': 24.0}},
        "description": "Tail key data: Park boost -21% (stadium -2%, weather -19%). Singer 🧤 (HR risk 1.11, vs LHB +1.19, vs RHB +0.29). Mahle (HR risk -0.98, vs LHB -0.82, vs RHB -0.52).",
        "rows": [
            row("Michael Harris II", "L", "+481", 77, "💎", ["vs Singer"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.2 mph EV, 12.5% barrels. Singer LHB split +1.19, HR risk 1.11. park/weather net drag (-21%).""", blast="good", contact={'stars': 5, 'k': 15.8, 'batterK': 15.0, 'batterWhiff': 19.2, 'pitcherK': 14.6}),
            row("Matt Olson", "L", "+329", 74, "", ["vs Singer"], """0 HR, 92.9 mph EV. Singer LHB split +1.19, HR risk 1.11. park/weather net drag (-21%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.7, 'batterK': 21.7, 'batterWhiff': 28.0, 'pitcherK': 14.6}),
            row("Ozzie Albies", "S", "+563", 58, "", ["vs Singer"], """0 HR, 91.2 mph EV. Singer SHB→LHB split +1.19, HR risk 1.11. park/weather net drag (-21%); limited recent HR events.""", contact={'stars': 5, 'k': 16.9, 'batterK': 17.3, 'batterWhiff': 23.3, 'pitcherK': 14.6}),
            row("Elly De La Cruz", "S", "+432", 78, "🚀 ⭐ 🌕 💣", ["vs Mahle"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 102.7 mph EV, 37.5% barrels. Mahle SHB→LHB split -0.82, HR risk -0.98. tough split lane (-0.82); pitcher suppresses HR (-0.98).""", blast="high", contact={'stars': 2, 'k': 25.9, 'batterK': 28.2, 'batterWhiff': 30.1, 'pitcherK': 24.0}),
            row("Eugenio Suarez", "R", "+610", 81, "🌕 💣", ["vs Mahle"], """2 HR, 3 near-HR, 98.1 mph EV, 37.5% barrels. Mahle RHB split -0.52, HR risk -0.98. tough split lane (-0.52); pitcher suppresses HR (-0.98).""", blast="high", contact={'stars': 2, 'k': 25.6, 'batterK': 28.4, 'batterWhiff': 28.9, 'pitcherK': 24.0}),
            row("JJ Bleday", "L", "+564", 47, "", ["vs Mahle"], """0 HR, 95.0 mph EV. Mahle LHB split -0.82, HR risk -0.98. tough split lane (-0.82); pitcher suppresses HR (-0.98).""", blast="good", contact={'stars': 2, 'k': 24.9, 'batterK': 24.3, 'batterWhiff': 30.8, 'pitcherK': 24.0}),
            row("Sal Stewart", "R", "+573", 53, "", ["vs Mahle"], """0 HR, 1 near-HR, 95.9 mph EV. Mahle RHB split -0.52, HR risk -0.98. tough split lane (-0.52); pitcher suppresses HR (-0.98).""", blast="good", contact={'stars': 2, 'k': 24.5, 'batterK': 25.3, 'batterWhiff': 27.4, 'pitcherK': 24.0}),
            row("Dane Myers", "R", "+1100", 57, "", ["vs Mahle"], """1 HR, 1 near-HR, 94.6 mph EV, 12.5% barrels. Mahle RHB split -0.52, HR risk -0.98. tough split lane (-0.52); pitcher suppresses HR (-0.98).""", blast="good", contact={'stars': 3, 'k': 23.7, 'batterK': 23.9, 'batterWhiff': 25.6, 'pitcherK': 24.0}),
        ],
    },
    {
        "title": "CLE @ BOS - Joey Cantillo (L, CLE) vs Ranger Suarez (L, BOS)",
        "kLines": {'Cantillo': {'k': 4.9, 'lo': 3, 'hi': 6, 'bf': 21.2, 'matchupK': 22.9, 'ownK': None}, 'Suarez': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 21.9, 'matchupK': 16.7, 'ownK': 17.5}},
        "description": "Tail key data: Park boost -36% (stadium -8%, weather -28%). Cantillo (BAA vs LHB .241, vs RHB .249, HR/9 0.68 vs LHB, 1.11 vs RHB). Suarez (HR risk -1.00, vs LHB -0.36, vs RHB -0.59).",
        "rows": [
            row("Mickey Gasper", "S", "+687", 76, "⭐", ["vs Cantillo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.3 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-36%).""", blast="good", contact={'stars': 3, 'k': 20.6, 'batterK': 20.6, 'batterWhiff': 18.7, 'pitcherK': None}),
            row("Adley Rutschman", "S", "+980", 60, "💎", ["vs Cantillo"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.9 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-36%).""", blast="good", contact={'stars': 4, 'k': 19.7, 'batterK': 19.2, 'batterWhiff': 16.1, 'pitcherK': None}),
            row("Roman Anthony", "L", "+750", 68, "", ["vs Cantillo"], """0 HR, 97.3 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-36%).""", blast="good", contact={'stars': 2, 'k': 26.0, 'batterK': 31.2, 'batterWhiff': 30.6, 'pitcherK': None}),
            row("Angel Martinez", "S", "+900", 63, "", ["vs Suarez"], """1 HR, 1 near-HR, 98.9 mph EV, 12.5% barrels. Suarez SHB→RHB split -0.59, HR risk -1.00. tough split lane (-0.59); pitcher suppresses HR (-1.00).""", blast="good", contact={'stars': 4, 'k': 19.3, 'batterK': 22.7, 'batterWhiff': 21.7, 'pitcherK': 17.5}),
            row("Chase DeLauter", "L", "+1060", 62, "", ["vs Suarez"], """1 HR, 1 near-HR, 95.1 mph EV, 12.5% barrels. Suarez LHB split -0.36, HR risk -1.00. slight split headwind (-0.36); pitcher suppresses HR (-1.00).""", blast="good", contact={'stars': 5, 'k': 16.1, 'batterK': 15.4, 'batterWhiff': 13.1, 'pitcherK': 17.5}),
            row("Jose Ramirez", "S", "+730", 50, "💎", ["vs Suarez"], """Worst Pickz Hidden Gem. 0 HR, 99.4 mph EV, 12.5% barrels. Suarez SHB→RHB split -0.59, HR risk -1.00. tough split lane (-0.59); pitcher suppresses HR (-1.00).""", blast="good", contact={'stars': 5, 'k': 14.6, 'batterK': 10.3, 'batterWhiff': 12.2, 'pitcherK': 17.5}),
            row("Patrick Bailey", "S", "N/A", 44, "💎", ["vs Suarez"], """Worst Pickz Hidden Gem. 0 HR, 98.2 mph EV. Suarez SHB→RHB split -0.59, HR risk -1.00. tough split lane (-0.59); pitcher suppresses HR (-1.00).""", blast="good", contact={'stars': 3, 'k': 22.1, 'batterK': 31.7, 'batterWhiff': 30.1, 'pitcherK': 17.5}),
        ],
    },
    {
        "title": "CWS @ KC - David Sandlin (R, CWS) vs Randy Dobnak (R, KC)",
        "kLines": {'Sandlin': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 21.2, 'matchupK': 22.2, 'ownK': 22.8}, 'Dobnak': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 22.1, 'matchupK': 19.7, 'ownK': 16.7}},
        "description": "Tail key data: Park boost -3% (stadium +13%, weather -16%). Sandlin (HR risk 0.07, vs LHB +0.94, vs RHB -0.98). Dobnak (HR risk -0.20, vs LHB +0.54, vs RHB -1.00).",
        "rows": [
            row("Vinnie Pasquantino", "L", "+591", 84, "⭐", ["vs Sandlin"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.4 mph EV, 25.0% barrels. Sandlin LHB split +0.94, HR risk 0.07. weather carry headwind (-16%).""", blast="good", contact={'stars': 4, 'k': 18.3, 'batterK': 13.8, 'batterWhiff': 14.5, 'pitcherK': 22.8}),
            row("Jac Caglianone", "L", "+425", 77, "💎", ["vs Sandlin"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.8 mph EV, 12.5% barrels. Sandlin LHB split +0.94, HR risk 0.07. weather carry headwind (-16%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.4, 'batterK': 28.0, 'batterWhiff': 33.1, 'pitcherK': 22.8}),
            row("Munetaka Murakami", "L", "+360", 88, "🌕 💣", ["vs Dobnak"], """1 HR, 1 near-HR, 99.9 mph EV, 37.5% barrels. Dobnak LHB split +0.54, HR risk -0.20. pitcher risk below avg (-0.20); weather carry headwind (-16%).""", blast="high", contact={'stars': 1, 'k': 27.9, 'batterK': 44.6, 'batterWhiff': 43.5, 'pitcherK': 16.7}),
            row("Kyle Teel", "L", "+875", 86, "🌕 💣", ["vs Dobnak"], """2 HR, 2 near-HR, 94.1 mph EV, 25.0% barrels. Dobnak LHB split +0.54, HR risk -0.20. pitcher risk below avg (-0.20); weather carry headwind (-16%).""", blast="high", contact={'stars': 2, 'k': 24.3, 'batterK': 39.1, 'batterWhiff': 35.3, 'pitcherK': 16.7}),
            row("Sam Antonacci", "L", "+1200", 64, "💎", ["vs Dobnak"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.9 mph EV, 25.0% barrels. Dobnak LHB split +0.54, HR risk -0.20. pitcher risk below avg (-0.20); weather carry headwind (-16%).""", blast="good", contact={'stars': 5, 'k': 14.6, 'batterK': 10.5, 'batterWhiff': 11.9, 'pitcherK': 16.7}),
            row("Andrew Benintendi", "L", "+725", 58, "💎", ["vs Dobnak"], """Worst Pickz Hidden Gem. 0 HR, 93.2 mph EV. Dobnak LHB split +0.54, HR risk -0.20. pitcher risk below avg (-0.20); weather carry headwind (-16%).""", blast="good", contact={'stars': 4, 'k': 18.5, 'batterK': 23.6, 'batterWhiff': 20.0, 'pitcherK': 16.7}),
        ],
    },
    {
        "title": "HOU @ ATH - Peter Lambert (R, HOU) vs Mason Barnett 🧤 (R, ATH)",
        "kLines": {'Lambert': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 23.4, 'matchupK': 22.4, 'ownK': 22.5}, 'Barnett': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 20.9, 'matchupK': 18.3, 'ownK': 15.8}},
        "description": "Tail key data: Park boost +31% (stadium +28%, weather +3%). Lambert (HR risk -0.55, vs LHB -0.63, vs RHB -0.07). Barnett 🧤 (HR risk 1.28, vs LHB -0.53, vs RHB +2.05).",
        "rows": [
            row("Lawrence Butler", "L", "+540", 78, "💎", ["vs Lambert"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.5 mph EV, 25.0% barrels. Lambert LHB split -0.63, HR risk -0.55. tough split lane (-0.63); pitcher suppresses HR (-0.55).""", blast="good", contact={'stars': 2, 'k': 24.1, 'batterK': 27.6, 'batterWhiff': 25.9, 'pitcherK': 22.5}),
            row("Zack Gelof", "R", "+377", 82, "", ["vs Lambert"], """1 HR, 2 near-HR, 92.7 mph EV, 37.5% barrels. Lambert RHB split -0.07, HR risk -0.55. slight split headwind (-0.07); pitcher suppresses HR (-0.55).""", blast="good", contact={'stars': 3, 'k': 22.6, 'batterK': 20.9, 'batterWhiff': 28.3, 'pitcherK': 22.5}),
            row("Henry Bolte", "R", "+475", 65, "", ["vs Lambert"], """0 HR, 90.3 mph EV, 12.5% barrels. Lambert RHB split -0.07, HR risk -0.55. slight split headwind (-0.07); pitcher suppresses HR (-0.55).""", contact={'stars': 2, 'k': 25.4, 'batterK': 29.7, 'batterWhiff': 29.1, 'pitcherK': 22.5}),
            row("Christian Walker", "R", "+390", 91, "🌕 💣 💎", ["vs Barnett"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 91.8 mph EV, 25.0% barrels. Barnett RHB split +2.05, HR risk 1.28.""", blast="good", contact={'stars': 3, 'k': 20.4, 'batterK': 24.0, 'batterWhiff': 26.4, 'pitcherK': 15.8}),
            row("Isaac Paredes", "R", "+350", 88, "🌕 💣", ["vs Barnett"], """1 HR, 1 near-HR, 89.6 mph EV, 12.5% barrels. Barnett RHB split +2.05, HR risk 1.28.""", blast="good", contact={'stars': 5, 'k': 16.1, 'batterK': 15.5, 'batterWhiff': 13.2, 'pitcherK': 15.8}),
            row("Yordan Alvarez", "L", "+230", 95, "⭐ 🌕 💣", ["vs Barnett"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.3 mph EV, 12.5% barrels. Barnett LHB split -0.53, HR risk 1.28. tough split lane (-0.53).""", blast="good", contact={'stars': 4, 'k': 17.2, 'batterK': 15.3, 'batterWhiff': 19.9, 'pitcherK': 15.8}),
            row("Yainer Diaz", "R", "+340", 94, "🌕 💣", ["vs Barnett"], """0 HR, 1 near-HR, 94.3 mph EV, 12.5% barrels. Barnett RHB split +2.05, HR risk 1.28. limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.0, 'batterK': 15.1, 'batterWhiff': 22.7, 'pitcherK': 15.8}),
            row("Taylor Trammell", "L", "+450", 87, "", ["vs Barnett"], """0 HR, 1 near-HR, 98.6 mph EV, 12.5% barrels. Barnett LHB split -0.53, HR risk 1.28. tough split lane (-0.53); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 30.6, 'batterWhiff': 37.4, 'pitcherK': 15.8}),
            row("Nelson Velazquez", "R", "N/A", 93, "🌕 💣", ["vs Barnett"], """0 HR, 1 near-HR, 96.4 mph EV, 12.5% barrels. Barnett RHB split +2.05, HR risk 1.28. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 24.0, 'batterK': 42.9, 'batterWhiff': 41.8, 'pitcherK': 15.8}),
        ],
    },
    {
        "title": "LAA @ SEA - Grayson Rodriguez (R, LAA) vs Bryan Woo (R, SEA)",
        "kLines": {'Rodriguez': {'k': 4.9, 'lo': 3, 'hi': 6, 'bf': 22.0, 'matchupK': 22.1, 'ownK': 22.6}, 'Woo': {'k': 6.0, 'lo': 4, 'hi': 8, 'bf': 23.3, 'matchupK': 25.7, 'ownK': 24.8}},
        "description": "Tail key data: Park boost +0% (stadium +0%, weather +0%). Rodriguez (HR risk 0.37, vs LHB +0.93, vs RHB -0.59). Woo (HR risk -0.28, vs LHB +0.15, vs RHB -0.46).",
        "rows": [
            row("Lazaro Montes", "L", "N/A", 88, "⭐ 🌕 💣", ["vs Grayson Rodriguez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.3 mph EV, 25.0% barrels. Grayson Rodriguez LHB split +0.93, HR risk 0.37.""", blast="high", contact={'stars': 1, 'k': 29.4, 'batterK': 44.9, 'batterWhiff': 46.2, 'pitcherK': 22.6}),
            row("Dominic Canzone", "L", "N/A", 78, "⭐", ["vs Grayson Rodriguez"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 92.9 mph EV, 12.5% barrels. Grayson Rodriguez LHB split +0.93, HR risk 0.37. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.3, 'batterK': 16.7, 'batterWhiff': 22.2, 'pitcherK': 22.6}),
            row("Cole Young", "L", "N/A", 54, "", ["vs Grayson Rodriguez"], """0 HR, 87.5 mph EV. Grayson Rodriguez LHB split +0.93, HR risk 0.37. limited recent HR events; lighter EV form (87.5 mph).""", contact={'stars': 3, 'k': 21.2, 'batterK': 19.7, 'batterWhiff': 22.0, 'pitcherK': 22.6}),
            row("Cal Raleigh", "S", "N/A", 63, "", ["vs Grayson Rodriguez"], """0 HR, 86.2 mph EV. Grayson Rodriguez SHB→LHB split +0.93, HR risk 0.37. limited recent HR events; lighter EV form (86.2 mph).""", contact={'stars': 2, 'k': 26.2, 'batterK': 30.3, 'batterWhiff': 32.8, 'pitcherK': 22.6}),
            row("Josh Lowe", "L", "N/A", 49, "", ["vs Woo"], """0 HR, 85.0 mph EV. Woo LHB split +0.15, HR risk -0.28. pitcher risk below avg (-0.28); limited recent HR events.""", contact={'stars': 1, 'k': 29.0, 'batterK': 40.4, 'batterWhiff': 38.7, 'pitcherK': 24.8}),
            row("Mike Trout", "R", "N/A", 72, "💎", ["vs Woo"], """Worst Pickz Hidden Gem. 0 HR, 92.2 mph EV, 25.0% barrels. Woo RHB split -0.46, HR risk -0.28. tough split lane (-0.46); pitcher risk below avg (-0.28).""", blast="good", contact={'stars': 1, 'k': 27.6, 'batterK': 29.9, 'batterWhiff': 34.3, 'pitcherK': 24.8}),
            row("Zach Neto", "R", "N/A", 72, "💎", ["vs Woo"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.6 mph EV, 12.5% barrels. Woo RHB split -0.46, HR risk -0.28. tough split lane (-0.46); pitcher risk below avg (-0.28).""", blast="good", contact={'stars': 2, 'k': 27.0, 'batterK': 30.3, 'batterWhiff': 29.9, 'pitcherK': 24.8}),
            row("Moises Ballesteros", "L", "N/A", 44, "", ["vs Woo"], """0 HR, 84.4 mph EV. Woo LHB split +0.15, HR risk -0.28. pitcher risk below avg (-0.28); limited recent HR events.""", contact={'stars': 2, 'k': 25.4, 'batterK': 24.0, 'batterWhiff': 31.4, 'pitcherK': 24.8}),
            row("Wade Meckler", "L", "N/A", 42, "", ["vs Woo"], """0 HR, 80.6 mph EV. Woo LHB split +0.15, HR risk -0.28. pitcher risk below avg (-0.28); limited recent HR events.""", contact={'stars': 4, 'k': 18.6, 'batterK': 10.8, 'batterWhiff': 14.0, 'pitcherK': 24.8}),
        ],
    },
    {
        "title": "MIA @ CHC - Tyler Phillips (R, MIA) vs Matthew Boyd (L, CHC)",
        "kLines": {'Phillips': {'k': 4.2, 'lo': 3, 'hi': 6, 'bf': 19.5, 'matchupK': 21.5, 'ownK': 23.0}, 'Boyd': {'k': 3.9, 'lo': 2, 'hi': 6, 'bf': 23.1, 'matchupK': 16.8, 'ownK': 15.4}},
        "description": "Tail key data: Park boost -33% (stadium -1%, weather -32%). Phillips (HR risk -0.02, vs LHB +0.16, vs RHB -0.10). Boyd (HR risk -0.84, vs LHB -1.40, vs RHB -0.17).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+460", 88, "🌕 💣", ["vs Phillips"], """1 HR, 2 near-HR, 98.1 mph EV, 25.0% barrels. Phillips LHB split +0.16, HR risk -0.02. pitcher risk below avg (-0.02); park/weather net drag (-33%).""", blast="high", contact={'stars': 3, 'k': 23.5, 'batterK': 24.5, 'batterWhiff': 26.0, 'pitcherK': 23.0}),
            row("Seiya Suzuki", "R", "+650", 62, "", ["vs Phillips"], """1 HR, 1 near-HR, 85.1 mph EV, 12.5% barrels. Phillips RHB split -0.10, HR risk -0.02. slight split headwind (-0.10); pitcher risk below avg (-0.02).""", blast="good", contact={'stars': 3, 'k': 20.8, 'batterK': 21.6, 'batterWhiff': 16.0, 'pitcherK': 23.0}),
            row("Michael Conforto", "L", "+830", 66, "", ["vs Phillips"], """0 HR, 1 near-HR, 89.3 mph EV, 25.0% barrels. Phillips LHB split +0.16, HR risk -0.02. pitcher risk below avg (-0.02); park/weather net drag (-33%).""", blast="good", contact={'stars': 3, 'k': 20.9, 'batterK': 17.2, 'batterWhiff': 20.9, 'pitcherK': 23.0}),
            row("Dansby Swanson", "R", "+800", 72, "🌕 💣", ["vs Phillips"], """2 HR, 2 near-HR, 89.7 mph EV, 12.5% barrels. Phillips RHB split -0.10, HR risk -0.02. slight split headwind (-0.10); pitcher risk below avg (-0.02).""", blast="high", contact={'stars': 2, 'k': 24.3, 'batterK': 25.3, 'batterWhiff': 30.0, 'pitcherK': 23.0}),
            row("Griffin Conine", "L", "+840", 59, "", ["vs Boyd"], """1 HR, 1 near-HR, 93.6 mph EV, 37.5% barrels. Boyd LHB split -1.40, HR risk -0.84. tough split lane (-1.40); pitcher suppresses HR (-0.84).""", blast="good", contact={'stars': 3, 'k': 21.1, 'batterK': 27.8, 'batterWhiff': 34.0, 'pitcherK': 15.4}),
            row("Kyle Stowers", "L", "+630", 73, "", ["vs Boyd"], """1 HR, 3 near-HR, 94.0 mph EV, 37.5% barrels. Boyd LHB split -1.40, HR risk -0.84. tough split lane (-1.40); pitcher suppresses HR (-0.84).""", blast="good", contact={'stars': 3, 'k': 21.7, 'batterK': 29.7, 'batterWhiff': 33.3, 'pitcherK': 15.4}),
            row("Heriberto Hernandez", "R", "+390", 63, "💎", ["vs Boyd"], """Worst Pickz Hidden Gem. 0 HR, 99.2 mph EV. Boyd RHB split -0.17, HR risk -0.84. slight split headwind (-0.17); pitcher suppresses HR (-0.84).""", blast="good", contact={'stars': 4, 'k': 19.9, 'batterK': 25.5, 'batterWhiff': 28.9, 'pitcherK': 15.4}),
            row("Agustin Ramirez", "R", "+730", 48, "💎", ["vs Boyd"], """Worst Pickz Hidden Gem. 0 HR, 91.0 mph EV. Boyd RHB split -0.17, HR risk -0.84. slight split headwind (-0.17); pitcher suppresses HR (-0.84).""", contact={'stars': 4, 'k': 19.2, 'batterK': 25.0, 'batterWhiff': 27.3, 'pitcherK': 15.4}),
        ],
    },
    {
        "title": "MIL @ PHI - Bryse Wilson (R, MIL) vs Andrew Painter (R, PHI)",
        "kLines": {'Wilson': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 21.7, 'matchupK': 20.4, 'ownK': 20.7}, 'Painter': {'k': 5.4, 'lo': 4, 'hi': 7, 'bf': 22.0, 'matchupK': 24.5, 'ownK': 23.6}},
        "description": "Tail key data: Park boost -22% (stadium +15%, weather -37%). Wilson (HR risk -0.80, vs LHB -0.56, vs RHB -0.18). Painter (HR risk -0.05, vs LHB -0.69, vs RHB +0.50).",
        "rows": [
            row("Bryan De La Cruz", "R", "N/A", 49, "", ["vs Wilson"], """0 HR, 91.9 mph EV, 12.5% barrels. Wilson RHB split -0.18, HR risk -0.80. slight split headwind (-0.18); pitcher suppresses HR (-0.80).""", contact={'stars': 3, 'k': 20.8, 'batterK': 22.4, 'batterWhiff': 20.2, 'pitcherK': 20.7}),
            row("Bryson Stott", "L", "+900", 44, "💎", ["vs Wilson"], """Worst Pickz Hidden Gem. 0 HR, 91.2 mph EV, 12.5% barrels. Wilson LHB split -0.56, HR risk -0.80. tough split lane (-0.56); pitcher suppresses HR (-0.80).""", contact={'stars': 4, 'k': 18.3, 'batterK': 12.8, 'batterWhiff': 18.9, 'pitcherK': 20.7}),
            row("Kyle Schwarber", "L", "+306", 55, "", ["vs Wilson"], """0 HR, 93.4 mph EV. Wilson LHB split -0.56, HR risk -0.80. tough split lane (-0.56); pitcher suppresses HR (-0.80).""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 26.4, 'batterWhiff': 28.2, 'pitcherK': 20.7}),
            row("Brandon Marsh", "L", "+800", 50, "💎", ["vs Wilson"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 87.3 mph EV, 12.5% barrels. Wilson LHB split -0.56, HR risk -0.80. tough split lane (-0.56); pitcher suppresses HR (-0.80).""", blast="good", contact={'stars': 3, 'k': 22.1, 'batterK': 26.0, 'batterWhiff': 24.4, 'pitcherK': 20.7}),
            row("Bo Naylor", "L", "N/A", 77, "🌕 💣 💎", ["vs Painter"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 93.6 mph EV, 25.0% barrels. Painter LHB split -0.69, HR risk -0.05. tough split lane (-0.69); pitcher risk below avg (-0.05).""", blast="high", contact={'stars': 3, 'k': 21.1, 'batterK': 26.2, 'batterWhiff': 13.4, 'pitcherK': 23.6}),
            row("Jake Bauers", "L", "+483", 73, "", ["vs Painter"], """1 HR, 1 near-HR, 91.9 mph EV, 12.5% barrels. Painter LHB split -0.69, HR risk -0.05. tough split lane (-0.69); pitcher risk below avg (-0.05).""", blast="good", contact={'stars': 1, 'k': 29.0, 'batterK': 34.2, 'batterWhiff': 40.6, 'pitcherK': 23.6}),
            row("Jackson Chourio", "R", "+425", 62, "", ["vs Painter"], """0 HR, 94.4 mph EV, 12.5% barrels. Painter RHB split +0.50, HR risk -0.05. pitcher risk below avg (-0.05); park/weather net drag (-22%).""", blast="good", contact={'stars': 2, 'k': 24.2, 'batterK': 24.0, 'batterWhiff': 29.1, 'pitcherK': 23.6}),
            row("Joey Ortiz", "R", "+920", 59, "", ["vs Painter"], """1 HR, 1 near-HR, 92.0 mph EV, 12.5% barrels. Painter RHB split +0.50, HR risk -0.05. pitcher risk below avg (-0.05); park/weather net drag (-22%).""", blast="good", contact={'stars': 3, 'k': 23.2, 'batterK': 23.9, 'batterWhiff': 24.6, 'pitcherK': 23.6}),
        ],
    },
    {
        "title": "NYM @ TEX - Zach Thornton (L, NYM) vs Kumar Rocker (R, TEX)",
        "kLines": {'Thornton': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 22.4, 'matchupK': 23.3, 'ownK': None}, 'Rocker': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 21.5, 'matchupK': 21.7, 'ownK': 22.2}},
        "description": "Tail key data: Park boost -12% (stadium -11%, weather -1%). Thornton (HR risk 0.84, vs LHB +0.80, vs RHB +0.49). Rocker (HR risk -0.07, vs LHB +0.33, vs RHB -0.49).",
        "rows": [
            row("Josh Jung", "R", "+780", 79, "", ["vs Thornton"], """0 HR, 1 near-HR, 92.2 mph EV, 12.5% barrels. Thornton RHB split +0.49, HR risk 0.84. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.3, 'batterK': 20.2, 'batterWhiff': 17.7, 'pitcherK': 18.2}),
            row("Ezequiel Duran", "R", "+940", 75, "", ["vs Thornton"], """0 HR, 1 near-HR, 96.0 mph EV. Thornton RHB split +0.49, HR risk 0.84. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.9, 'batterK': 20.5, 'batterWhiff': 20.8, 'pitcherK': 18.2}),
            row("Brandon Nimmo", "L", "+610", 60, "", ["vs Thornton"], """0 HR, 87.4 mph EV. Thornton LHB split +0.80, HR risk 0.84. park/weather net drag (-12%); limited recent HR events.""", contact={'stars': 3, 'k': 23.0, 'batterK': 28.6, 'batterWhiff': 33.1, 'pitcherK': 18.2}),
            row("Wyatt Langford", "R", "+452", 74, "", ["vs Thornton"], """0 HR, 1 near-HR, 90.8 mph EV, 25.0% barrels. Thornton RHB split +0.49, HR risk 0.84. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 29.4, 'batterWhiff': 32.1, 'pitcherK': 18.2}),
            row("Brett Baty", "L", "+680", 72, "⭐", ["vs Rocker"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.2 mph EV, 12.5% barrels. Rocker LHB split +0.33, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-12%).""", blast="good", contact={'stars': 2, 'k': 24.3, 'batterK': 20.0, 'batterWhiff': 36.3, 'pitcherK': 22.2}),
            row("A.J. Ewing", "L", "+700", 67, "", ["vs Rocker"], """1 HR, 1 near-HR, 95.3 mph EV, 12.5% barrels. Rocker LHB split +0.33, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-12%).""", blast="good", contact={'stars': 3, 'k': 21.5, 'batterK': 19.8, 'batterWhiff': 24.8, 'pitcherK': 22.2}),
            row("Francisco Lindor", "S", "+387", 74, "💎", ["vs Rocker"], """Worst Pickz Hidden Gem. 0 HR, 96.1 mph EV, 12.5% barrels. Rocker SHB→LHB split +0.33, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-12%).""", blast="good", contact={'stars': 3, 'k': 22.6, 'batterK': 23.2, 'batterWhiff': 25.7, 'pitcherK': 22.2}),
            row("Juan Soto", "L", "+326", 73, "", ["vs Rocker"], """0 HR, 94.6 mph EV. Rocker LHB split +0.33, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-12%).""", blast="good", contact={'stars': 4, 'k': 18.9, 'batterK': 14.7, 'batterWhiff': 19.9, 'pitcherK': 22.2}),
        ],
    },
    {
        "title": "SD @ LAD - Nick Pivetta (R, SD) vs Tyler Glasnow (R, LAD)",
        "kLines": {'Pivetta': {'k': 4.9, 'lo': 3, 'hi': 7, 'bf': 19.2, 'matchupK': 25.6, 'ownK': 29.2}, 'Glasnow': {'k': 6.4, 'lo': 5, 'hi': 8, 'bf': 21.9, 'matchupK': 29.3, 'ownK': 33.2}},
        "description": "Tail key data: Park boost +21% (stadium +19%, weather +2%). Pivetta (HR risk -0.38, vs LHB -0.79, vs RHB +0.26). Glasnow (HR risk -0.34, vs LHB -0.01, vs RHB -0.45).",
        "rows": [
            row("Max Muncy", "L", "+433", 87, "⭐ 🌕 💣", ["vs Pivetta"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.1 mph EV, 37.5% barrels. Pivetta LHB split -0.79, HR risk -0.38. tough split lane (-0.79); pitcher risk below avg (-0.38).""", blast="high", contact={'stars': 2, 'k': 26.7, 'batterK': 26.0, 'batterWhiff': 28.9, 'pitcherK': 29.2}),
            row("Alex Freeland", "S", "N/A", 79, "💎", ["vs Pivetta"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.5 mph EV, 25.0% barrels. Pivetta SHB→LHB split -0.79, HR risk -0.38. tough split lane (-0.79); pitcher risk below avg (-0.38).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 16.3, 'batterWhiff': 20.3, 'pitcherK': 29.2}),
            row("Teoscar Hernandez", "R", "+400", 71, "", ["vs Pivetta"], """0 HR, 95.1 mph EV. Pivetta RHB split +0.26, HR risk -0.38. pitcher risk below avg (-0.38); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 26.3, 'batterK': 22.1, 'batterWhiff': 32.5, 'pitcherK': 29.2}),
            row("Shohei Ohtani", "L", "+314", 75, "", ["vs Pivetta"], """0 HR, 92.9 mph EV, 12.5% barrels. Pivetta LHB split -0.79, HR risk -0.38. tough split lane (-0.79); pitcher risk below avg (-0.38).""", blast="good", contact={'stars': 1, 'k': 30.1, 'batterK': 31.5, 'batterWhiff': 36.6, 'pitcherK': 29.2}),
            row("Jackson Merrill", "L", "+540", 78, "💎", ["vs Glasnow"], """Worst Pickz Hidden Gem. 0 HR, 96.9 mph EV. Glasnow LHB split -0.01, HR risk -0.34. slight split headwind (-0.01); pitcher risk below avg (-0.34).""", blast="good", contact={'stars': 1, 'k': 27.9, 'batterK': 18.8, 'batterWhiff': 29.1, 'pitcherK': 33.2}),
            row("Xander Bogaerts", "R", "+725", 74, "", ["vs Glasnow"], """1 HR, 2 near-HR, 95.4 mph EV, 12.5% barrels. Glasnow RHB split -0.45, HR risk -0.34. tough split lane (-0.45); pitcher risk below avg (-0.34).""", blast="good", contact={'stars': 1, 'k': 28.0, 'batterK': 22.0, 'batterWhiff': 25.0, 'pitcherK': 33.2}),
            row("Jake Cronenworth", "L", "+1120", 61, "", ["vs Glasnow"], """1 HR, 2 near-HR, 86.5 mph EV, 25.0% barrels. Glasnow LHB split -0.01, HR risk -0.34. slight split headwind (-0.01); pitcher risk below avg (-0.34).""", blast="good", contact={'stars': 2, 'k': 25.0, 'batterK': 19.0, 'batterWhiff': 15.6, 'pitcherK': 33.2}),
        ],
    },
    {
        "title": "STL @ PIT - Kyle Leahy (R, STL) vs Paul Skenes (R, PIT)",
        "kLines": {'Leahy': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 20.5, 'matchupK': 25.5, 'ownK': 27.9}, 'Skenes': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 22.1, 'matchupK': 23.9, 'ownK': 24.1}},
        "description": "Tail key data: Park boost -46% (stadium -15%, weather -31%). Leahy (HR risk 0.12, vs LHB -0.08, vs RHB +0.24). Skenes (HR risk -0.22, vs LHB +0.60, vs RHB -0.76).",
        "rows": [
            row("Rafael Flores", "R", "+875", 81, "⭐", ["vs Leahy"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.3 mph EV, 25.0% barrels. Leahy RHB split +0.24, HR risk 0.12. park/weather net drag (-46%).""", blast="good", contact={'stars': 2, 'k': 26.2, 'batterK': 26.0, 'batterWhiff': 26.9, 'pitcherK': 27.9}),
            row("Ryan O'Hearn", "L", "+1000", 52, "", ["vs Leahy"], """0 HR, 93.0 mph EV. Leahy LHB split -0.08, HR risk 0.12. slight split headwind (-0.08); park/weather net drag (-46%).""", blast="good", contact={'stars': 3, 'k': 23.9, 'batterK': 18.8, 'batterWhiff': 24.6, 'pitcherK': 27.9}),
            row("Leonardo Bernal", "S", "+860", 60, "", ["vs Skenes"], """1 HR, 1 near-HR, 90.2 mph EV, 12.5% barrels. Skenes SHB→LHB split +0.60, HR risk -0.22. pitcher risk below avg (-0.22); park/weather net drag (-46%).""", blast="good", contact={'stars': 3, 'k': 22.8, 'batterK': 22.1, 'batterWhiff': 23.0, 'pitcherK': 24.1}),
            row("Jordan Walker", "R", "+680", 69, "🌕 💣", ["vs Skenes"], """0 HR, 97.0 mph EV, 25.0% barrels. Skenes RHB split -0.76, HR risk -0.22. tough split lane (-0.76); pitcher risk below avg (-0.22).""", blast="high", contact={'stars': 1, 'k': 29.8, 'batterK': 36.7, 'batterWhiff': 40.1, 'pitcherK': 24.1}),
            row("Alec Burleson", "L", "+650", 58, "", ["vs Skenes"], """0 HR, 89.8 mph EV, 12.5% barrels. Skenes LHB split +0.60, HR risk -0.22. pitcher risk below avg (-0.22); park/weather net drag (-46%).""", contact={'stars': 2, 'k': 24.7, 'batterK': 26.8, 'batterWhiff': 26.6, 'pitcherK': 24.1}),
            row("JJ Wetherholt", "L", "+920", 64, "", ["vs Skenes"], """0 HR, 1 near-HR, 92.8 mph EV. Skenes LHB split +0.60, HR risk -0.22. pitcher risk below avg (-0.22); park/weather net drag (-46%).""", blast="good", contact={'stars': 3, 'k': 22.3, 'batterK': 23.2, 'batterWhiff': 19.0, 'pitcherK': 24.1}),
        ],
    },
    {
        "title": "TB @ NYY - Ian Seymour (L, TB) vs Cam Schlittler (R, NYY)",
        "kLines": {'Seymour': {'k': 5.9, 'lo': 4, 'hi': 8, 'bf': 20.8, 'matchupK': 28.6, 'ownK': 30.3}, 'Schlittler': {'k': 6.5, 'lo': 5, 'hi': 8, 'bf': 23.1, 'matchupK': 28.1, 'ownK': 33.2}},
        "description": "Tail key data: Park boost -23% (stadium +12%, weather -35%). Seymour (HR risk 0.82, vs LHB +0.73, vs RHB +0.47). Schlittler (HR risk -0.86, vs LHB -0.71, vs RHB -0.27).",
        "rows": [
            row("Spencer Jones", "L", "+340", 87, "⭐", ["vs Seymour"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.8 mph EV, 12.5% barrels. Seymour LHB split +0.73, HR risk 0.82. park/weather net drag (-23%).""", blast="good", contact={'stars': 1, 'k': 34.6, 'batterK': 38.6, 'batterWhiff': 40.9, 'pitcherK': 30.3}),
            row("Paul Goldschmidt", "R", "+584", 82, "", ["vs Seymour"], """1 HR, 1 near-HR, 95.1 mph EV, 12.5% barrels. Seymour RHB split +0.47, HR risk 0.82. park/weather net drag (-23%).""", blast="good", contact={'stars': 2, 'k': 24.5, 'batterK': 15.7, 'batterWhiff': 20.4, 'pitcherK': 30.3}),
            row("Heliot Ramos", "R", "+541", 74, "⭐", ["vs Seymour"], """Worst Pickz Favorite. 0 HR, 96.4 mph EV. Seymour RHB split +0.47, HR risk 0.82. park/weather net drag (-23%); limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 30.6, 'batterK': 31.3, 'batterWhiff': 34.5, 'pitcherK': 30.3}),
            row("Victor Mesa Jr.", "L", "+541", 83, "🚀 🌕 💣 💎", ["vs Schlittler"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 100.4 mph EV, 37.5% barrels. Schlittler LHB split -0.71, HR risk -0.86. tough split lane (-0.71); pitcher suppresses HR (-0.86).""", blast="high", contact={'stars': 2, 'k': 26.3, 'batterK': 12.9, 'batterWhiff': 25.8, 'pitcherK': 33.2}),
            row("Jonathan Aranda", "L", "+650", 83, "🌕 💣 💎", ["vs Schlittler"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 95.9 mph EV, 12.5% barrels. Schlittler LHB split -0.71, HR risk -0.86. tough split lane (-0.71); pitcher suppresses HR (-0.86).""", blast="high", contact={'stars': 1, 'k': 31.4, 'batterK': 30.5, 'batterWhiff': 27.6, 'pitcherK': 33.2}),
            row("Junior Caminero", "R", "+377", 72, "💎", ["vs Schlittler"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 98.8 mph EV, 12.5% barrels. Schlittler RHB split -0.27, HR risk -0.86. slight split headwind (-0.27); pitcher suppresses HR (-0.86).""", blast="good", contact={'stars': 2, 'k': 26.5, 'batterK': 20.0, 'batterWhiff': 19.9, 'pitcherK': 33.2}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-24")

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

    out = ROOT / '_games-0924.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
