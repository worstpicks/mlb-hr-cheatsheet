#!/usr/bin/env python3
"""Generate games[] block for 2026-09-08 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Aaron Judge (R)",
    "Brandon Nimmo (L)",
    "Bryan Reynolds (S)",
    "Elly De La Cruz (S)",
    "Francisco Lindor (S)",
    "Heriberto Hernandez (R)",
    "James Wood (L)",
    "Jonah Cox (R)",
    "Josh Bell (S)",
    "Juan Soto (L)",
    "Junior Caminero (R)",
    "Manny Machado (R)",
    "Mookie Betts (R)",
    "Munetaka Murakami (L)",
    "Pete Crow Armstrong (L)",
    "Ronald Acuna Jr. (R)",
    "Ryan Vilade (R)",
    "Salvador Perez (R)",
    "Teoscar Hernandez (R)",
    "Tyler Stephenson (R)",
}

GEMS = {
    "Brett Baty (L)",
    "Bryce Eldridge (L)",
    "Cal Raleigh (S)",
    "Carter Jensen (L)",
    "Dominic Canzone (L)",
    "Donovan Walton (L)",
    "Ian Happ (S)",
    "Justin Foscue (R)",
    "Keibert Ruiz (S)",
    "Kyle Stowers (L)",
    "Lawrence Butler (L)",
    "Leonardo Bernal (S)",
    "Max Muncy (L)",
    "Nelson Velazquez (R)",
    "Roman Anthony (L)",
    "Spencer Jones (L)",
    "TJ Rumfield (L)",
    "Trevor Larnach (L)",
    "Tristan Peters (L)",
    "Ty France (R)",
    "Vladimir Guerrero Jr. (R)",
}

PLAYER_TEAMS = {
    "A.J Ewing (L)": "NYM",
    "Aaron Judge (R)": "NYY",
    "Agustin Ramirez (R)": "MIA",
    "Alec Burleson (L)": "STL",
    "Alex Bregman (R)": "CHC",
    "Andres Gimenez (L)": "TOR",
    "Ben Malgeri (R)": "DET",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Nimmo (L)": "TEX",
    "Brett Baty (L)": "NYM",
    "Brett Callahan (L)": "DET",
    "Brewer Hicklen (R)": "ATL",
    "Brooks Lee (S)": "MIN",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Carson Kelly (R)": "CHC",
    "Carter Jensen (L)": "KC",
    "Chase DeLauter (L)": "CLE",
    "Coby Mayo (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Colt Keith (L)": "DET",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Daulton Varsho (L)": "HOU",
    "Daylen Lile (L)": "WSH",
    "Dominic Canzone (L)": "SEA",
    "Donovan Walton (L)": "ATH",
    "Drake Baldwin (L)": "ATL",
    "Dylan Crews (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Gabriel Moreno (R)": "ARI",
    "Garrett Mitchell (L)": "MIL",
    "George Springer (R)": "TOR",
    "Gleyber Torres (R)": "DET",
    "Griffin Conine (L)": "MIA",
    "Heliot Ramos (R)": "NYY",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Ian Happ (S)": "CHC",
    "Ivan Herrera (R)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake McCarthy (L)": "COL",
    "James Wood (L)": "WSH",
    "Jasson Dominguez (S)": "NYY",
    "Joc Pederson (L)": "TEX",
    "Joey Ortiz (R)": "MIL",
    "John Peck (R)": "DET",
    "Jonah Cox (R)": "SF",
    "Jonathan Aranda (L)": "TB",
    "Jose Siri (R)": "LAA",
    "Josh Bell (S)": "MIN",
    "Joshua Baez (R)": "STL",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kazuma Okamoto (R)": "TOR",
    "Keibert Ruiz (S)": "WSH",
    "Kevin McGonigle (L)": "DET",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lars Nootbaar (L)": "ARI",
    "Lawrence Butler (L)": "ATH",
    "Leonardo Bernal (S)": "STL",
    "Luis Garcia Jr. (L)": "NYY",
    "Luke Keaschall (R)": "MIN",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Michael Busch (L)": "CHC",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Nick Sogard (S)": "BOS",
    "Oneil Cruz (L)": "PIT",
    "Ozzie Albies (S)": "ATL",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randy Arozarena (R)": "SEA",
    "Riley Greene (L)": "DET",
    "Roman Anthony (L)": "BOS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan Vilade (R)": "TB",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Samuel Basallo (L)": "BAL",
    "Spencer Jones (L)": "NYY",
    "TJ Rumfield (L)": "COL",
    "Teoscar Hernandez (R)": "LAD",
    "Travis Bazzana (L)": "CLE",
    "Trevor Larnach (L)": "MIN",
    "Tristan Peters (L)": "CWS",
    "Ty France (R)": "SD",
    "Tyler Stephenson (R)": "CIN",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "William Contreras (R)": "MIL",
    "Yainer Diaz (R)": "HOU",
    "Yandy Diaz (R)": "TB",
    "Yohandy Morales (R)": "WSH",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("CIN @ LAD", "Lodolo"),
    ("NYM @ MIA", "Manaea"),
    ("WSH @ SD", "Mize"),
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
        "title": "ARI @ KC - Corbin Burnes (R, ARI) vs Michael Wacha (R, KC)",
        "kLines": {'Burnes': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 21.7, 'matchupK': 21.0, 'ownK': None}, 'Wacha': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 24.8, 'matchupK': 20.3, 'ownK': 21.0}},
        "description": "Tail key data: Park boost +24% (stadium +12%, weather +12%). Burnes (HR risk 0.06, vs LHB -0.94, vs RHB +0.76). Wacha (HR risk 0.48, vs LHB -0.54, vs RHB +1.65).",
        "rows": [
            row("Salvador Perez", "R", "+490", 88, "⭐ 🌕 💣", ["vs Burnes"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.2 mph EV, 25.0% barrels. Burnes RHB split +0.76, HR risk 0.06.""", blast="good", contact={'stars': 3, 'k': 20.2, 'batterK': 15.3, 'batterWhiff': 24.6, 'pitcherK': None}),
            row("Carter Jensen", "L", "+490", 76, "💎", ["vs Burnes"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.0 mph EV, 12.5% barrels. Burnes LHB split -0.94, HR risk 0.06. tough split lane (-0.94).""", blast="good", contact={'stars': 3, 'k': 22.0, 'batterK': 21.2, 'batterWhiff': 25.2, 'pitcherK': None}),
            row("Bobby Witt Jr.", "R", "+425", 88, "🌕 💣", ["vs Burnes"], """1 HR, 1 near-HR, 91.7 mph EV, 25.0% barrels. Burnes RHB split +0.76, HR risk 0.06.""", blast="good", contact={'stars': 4, 'k': 19.4, 'batterK': 14.1, 'batterWhiff': 23.6, 'pitcherK': None}),
            row("Jac Caglianone", "L", "N/A", 74, "", ["vs Burnes"], """0 HR, 95.1 mph EV. Burnes LHB split -0.94, HR risk 0.06. tough split lane (-0.94); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.2, 'batterK': 21.3, 'batterWhiff': 31.2, 'pitcherK': None}),
            row("Lars Nootbaar", "L", "+561", 91, "🌕 💣", ["vs Wacha"], """2 HR, 2 near-HR, 99.3 mph EV, 25.0% barrels. Wacha LHB split -0.54, HR risk 0.48. tough split lane (-0.54).""", blast="high", contact={'stars': 4, 'k': 18.8, 'batterK': 15.9, 'batterWhiff': 16.7, 'pitcherK': 21.0}),
            row("Gabriel Moreno", "R", "+630", 87, "", ["vs Wacha"], """1 HR, 1 near-HR, 90.2 mph EV, 12.5% barrels. Wacha RHB split +1.65, HR risk 0.48.""", blast="good", contact={'stars': 4, 'k': 18.3, 'batterK': 14.9, 'batterWhiff': 18.1, 'pitcherK': 21.0}),
            row("Corbin Carroll", "L", "+375", 87, "🌕 💣", ["vs Wacha"], """0 HR, 1 near-HR, 99.4 mph EV, 37.5% barrels. Wacha LHB split -0.54, HR risk 0.48. tough split lane (-0.54); limited recent HR events.""", blast="high", contact={'stars': 3, 'k': 22.5, 'batterK': 24.4, 'batterWhiff': 27.5, 'pitcherK': 21.0}),
        ],
    },
    {
        "title": "CHC @ MIL - David Peterson (L, CHC) vs Jacob Misiorowski (R, MIL)",
        "kLines": {'Peterson': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 21.7, 'matchupK': 20.4, 'ownK': 20.7}, 'Misiorowski': {'k': 7.2, 'lo': 6, 'hi': 9, 'bf': 22.6, 'matchupK': 31.7, 'ownK': 37.5}},
        "description": "Tail key data: Park boost +5% (stadium -2%, weather +7%). Peterson (HR risk -0.13, vs LHB -0.68, vs RHB +0.04). Misiorowski (HR risk -0.49, vs LHB +0.09, vs RHB -0.71).",
        "rows": [
            row("William Contreras", "R", "+710", 70, "", ["vs Peterson"], """1 HR, 1 near-HR, 94.2 mph EV, 12.5% barrels. Peterson RHB split +0.04, HR risk -0.13. pitcher risk below avg (-0.13).""", blast="good", contact={'stars': 4, 'k': 19.2, 'batterK': 16.3, 'batterWhiff': 22.0, 'pitcherK': 20.7}),
            row("Jackson Chourio", "R", "+520", 70, "", ["vs Peterson"], """1 HR, 1 near-HR, 91.2 mph EV, 12.5% barrels. Peterson RHB split +0.04, HR risk -0.13. pitcher risk below avg (-0.13).""", blast="good", contact={'stars': 3, 'k': 20.2, 'batterK': 18.3, 'batterWhiff': 25.0, 'pitcherK': 20.7}),
            row("Garrett Mitchell", "L", "+800", 63, "🚀", ["vs Peterson"], """0 HR, 103.1 mph EV. Peterson LHB split -0.68, HR risk -0.13. tough split lane (-0.68); pitcher risk below avg (-0.13).""", blast="good", contact={'stars': 3, 'k': 23.7, 'batterK': 28.1, 'batterWhiff': 31.2, 'pitcherK': 20.7}),
            row("Joey Ortiz", "R", "+1120", 59, "", ["vs Peterson"], """0 HR, 94.6 mph EV. Peterson RHB split +0.04, HR risk -0.13. pitcher risk below avg (-0.13); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.7, 'batterK': 22.4, 'batterWhiff': 21.2, 'pitcherK': 20.7}),
            row("Pete Crow Armstrong", "L", "+420", 93, "⭐ 🌕 💣", ["vs Misiorowski"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 97.9 mph EV, 37.5% barrels. Misiorowski LHB split +0.09, HR risk -0.49. pitcher suppresses HR (-0.49).""", blast="high", contact={'stars': 1, 'k': 28.2, 'batterK': 18.9, 'batterWhiff': 20.8, 'pitcherK': 37.5}),
            row("Ian Happ", "S", "+780", 76, "💎", ["vs Misiorowski"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.3 mph EV, 25.0% barrels. Misiorowski SHB→LHB split +0.09, HR risk -0.49. pitcher suppresses HR (-0.49).""", blast="good", contact={'stars': 1, 'k': 31.8, 'batterK': 25.3, 'batterWhiff': 27.2, 'pitcherK': 37.5}),
            row("Michael Busch", "L", "+680", 77, "", ["vs Misiorowski"], """1 HR, 1 near-HR, 95.7 mph EV, 12.5% barrels. Misiorowski LHB split +0.09, HR risk -0.49. pitcher suppresses HR (-0.49).""", blast="good", contact={'stars': 1, 'k': 33.7, 'batterK': 27.9, 'batterWhiff': 30.9, 'pitcherK': 37.5}),
            row("Carson Kelly", "R", "+980", 54, "", ["vs Misiorowski"], """1 HR, 2 near-HR, 92.5 mph EV. Misiorowski RHB split -0.71, HR risk -0.49. tough split lane (-0.71); pitcher suppresses HR (-0.49).""", blast="good", contact={'stars': 1, 'k': 28.2, 'batterK': 18.8, 'batterWhiff': 20.1, 'pitcherK': 37.5}),
            row("Alex Bregman", "R", "+880", 63, "", ["vs Misiorowski"], """0 HR, 1 near-HR, 92.7 mph EV, 12.5% barrels. Misiorowski RHB split -0.71, HR risk -0.49. tough split lane (-0.71); pitcher suppresses HR (-0.49).""", blast="good", contact={'stars': 2, 'k': 24.5, 'batterK': 11.0, 'batterWhiff': 17.3, 'pitcherK': 37.5}),
        ],
    },
    {
        "title": "CIN @ LAD - Nick Lodolo 🧤 (L, CIN) vs Tarik Skubal (L, LAD)",
        "kLines": {'Lodolo': {'k': 4.2, 'lo': 3, 'hi': 6, 'bf': 22.3, 'matchupK': 18.9, 'ownK': 18.4}, 'Skubal': {'k': 7.1, 'lo': 5, 'hi': 9, 'bf': 23.3, 'matchupK': 30.5, 'ownK': 30.6}},
        "description": "Tail key data: Park boost +27% (stadium +20%, weather +7%). Lodolo 🧤 (HR risk 1.70, vs LHB +0.17, vs RHB +1.14). Skubal (HR risk -0.78, vs LHB +0.39, vs RHB -0.77).",
        "rows": [
            row("Teoscar Hernandez", "R", "+333", 97, "🚀 ⭐ 🌕 💣", ["vs Lodolo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 100.5 mph EV, 50.0% barrels. Lodolo RHB split +1.14, HR risk 1.70.""", blast="high", contact={'stars': 3, 'k': 23.8, 'batterK': 28.6, 'batterWhiff': 35.4, 'pitcherK': 18.4}),
            row("Mookie Betts", "R", "+401", 91, "⭐ 🌕 💣", ["vs Lodolo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.7 mph EV, 12.5% barrels. Lodolo RHB split +1.14, HR risk 1.70.""", blast="good", contact={'stars': 5, 'k': 14.7, 'batterK': 9.7, 'batterWhiff': 12.5, 'pitcherK': 18.4}),
            row("Max Muncy", "L", "N/A", 87, "💎", ["vs Lodolo"], """Worst Pickz Hidden Gem. 0 HR, 92.4 mph EV. Lodolo LHB split +0.17, HR risk 1.70. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.0, 'batterK': 21.6, 'batterWhiff': 29.2, 'pitcherK': 18.4}),
            row("Elly De La Cruz", "S", "+475", 88, "🚀 ⭐ 🌕 💣", ["vs Skubal"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 105.5 mph EV, 50.0% barrels. Skubal SHB→RHB split -0.77, HR risk -0.78. tough split lane (-0.77); pitcher suppresses HR (-0.78).""", blast="high", contact={'stars': 1, 'k': 30.3, 'batterK': 30.5, 'batterWhiff': 26.9, 'pitcherK': 30.6}),
            row("Sal Stewart", "R", "+452", 70, "", ["vs Skubal"], """0 HR, 96.0 mph EV, 12.5% barrels. Skubal RHB split -0.77, HR risk -0.78. tough split lane (-0.77); pitcher suppresses HR (-0.78).""", blast="good", contact={'stars': 2, 'k': 25.6, 'batterK': 17.2, 'batterWhiff': 27.4, 'pitcherK': 30.6}),
            row("Tyler Stephenson", "R", "+640", 77, "⭐ 🌕 💣", ["vs Skubal"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.9 mph EV, 12.5% barrels. Skubal RHB split -0.77, HR risk -0.78. tough split lane (-0.77); pitcher suppresses HR (-0.78).""", blast="high", contact={'stars': 1, 'k': 32.9, 'batterK': 37.2, 'batterWhiff': 34.0, 'pitcherK': 30.6}),
        ],
    },
    {
        "title": "CLE @ BAL - Tanner Bibee (R, CLE) vs Brandon Young (R, BAL)",
        "kLines": {'Bibee': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 23.3, 'matchupK': 20.3, 'ownK': 18.9}, 'Young': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 23.8, 'matchupK': 18.0, 'ownK': 19.4}},
        "description": "Tail key data: Park boost -1% (stadium -3%, weather +2%). Bibee (HR risk -0.01, vs LHB +0.82, vs RHB -0.74). Young (HR risk 0.85, vs LHB +0.85, vs RHB +0.58).",
        "rows": [
            row("Coby Mayo", "R", "+380", 69, "", ["vs Bibee"], """1 HR, 1 near-HR, 93.7 mph EV, 12.5% barrels. Bibee RHB split -0.74, HR risk -0.01. tough split lane (-0.74); pitcher risk below avg (-0.01).""", blast="good", contact={'stars': 3, 'k': 22.0, 'batterK': 27.0, 'batterWhiff': 28.4, 'pitcherK': 18.9}),
            row("Samuel Basallo", "L", "+354", 74, "", ["vs Bibee"], """0 HR, 1 near-HR, 94.5 mph EV, 12.5% barrels. Bibee LHB split +0.82, HR risk -0.01. pitcher risk below avg (-0.01); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.9, 'batterK': 28.2, 'batterWhiff': 31.9, 'pitcherK': 18.9}),
            row("Pete Alonso", "R", "+290", 63, "", ["vs Bibee"], """0 HR, 89.4 mph EV. Bibee RHB split -0.74, HR risk -0.01. tough split lane (-0.74); pitcher risk below avg (-0.01).""", contact={'stars': 3, 'k': 21.9, 'batterK': 24.7, 'batterWhiff': 30.0, 'pitcherK': 18.9}),
            row("Chase DeLauter", "L", "+470", 82, "", ["vs Young"], """0 HR, 2 near-HR, 95.4 mph EV, 12.5% barrels. Young LHB split +0.85, HR risk 0.85.""", blast="good", contact={'stars': 4, 'k': 17.4, 'batterK': 17.3, 'batterWhiff': 13.5, 'pitcherK': 19.4}),
            row("Travis Bazzana", "L", "+820", 73, "", ["vs Young"], """1 HR, 1 near-HR, 87.0 mph EV, 12.5% barrels. Young LHB split +0.85, HR risk 0.85. lighter EV form (87.0 mph).""", blast="good", contact={'stars': 4, 'k': 18.3, 'batterK': 14.9, 'batterWhiff': 20.9, 'pitcherK': 19.4}),
        ],
    },
    {
        "title": "COL @ NYY - Gabriel Hughes (R, COL) vs Cam Schlittler (R, NYY)",
        "kLines": {'Hughes': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 21.9, 'matchupK': 20.5, 'ownK': 18.6}, 'Schlittler': {'k': 7.0, 'lo': 5, 'hi': 9, 'bf': 23.1, 'matchupK': 30.3, 'ownK': 33.6}},
        "description": "Tail key data: Park boost +3% (stadium +6%, weather -3%). Hughes (HR risk -0.29, vs LHB -0.52, vs RHB +0.42). Schlittler (HR risk -0.49, vs LHB -0.13, vs RHB -0.43).",
        "rows": [
            row("Spencer Jones", "L", "+390", 88, "🌕 💣 💎", ["vs Hughes"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.4 mph EV, 37.5% barrels. Hughes LHB split -0.52, HR risk -0.29. tough split lane (-0.52); pitcher risk below avg (-0.29).""", blast="high", contact={'stars': 2, 'k': 25.6, 'batterK': 37.5, 'batterWhiff': 36.3, 'pitcherK': 18.6}),
            row("Aaron Judge", "R", "+260", 81, "⭐", ["vs Hughes"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.0 mph EV, 12.5% barrels. Hughes RHB split +0.42, HR risk -0.29. pitcher risk below avg (-0.29); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.2, 'batterK': 25.8, 'batterWhiff': 29.9, 'pitcherK': 18.6}),
            row("Heliot Ramos", "R", "N/A", 68, "", ["vs Hughes"], """0 HR, 1 near-HR, 91.0 mph EV, 12.5% barrels. Hughes RHB split +0.42, HR risk -0.29. pitcher risk below avg (-0.29); limited recent HR events.""", contact={'stars': 3, 'k': 22.9, 'batterK': 28.8, 'batterWhiff': 31.9, 'pitcherK': 18.6}),
            row("Jasson Dominguez", "S", "+520", 62, "", ["vs Hughes"], """0 HR, 94.7 mph EV, 12.5% barrels. Hughes SHB→LHB split -0.52, HR risk -0.29. tough split lane (-0.52); pitcher risk below avg (-0.29).""", blast="good", contact={'stars': 4, 'k': 19.5, 'batterK': 22.2, 'batterWhiff': 20.0, 'pitcherK': 18.6}),
            row("Luis Garcia Jr.", "L", "+417", 73, "", ["vs Hughes"], """0 HR, 92.7 mph EV, 12.5% barrels. Hughes LHB split -0.52, HR risk -0.29. tough split lane (-0.52); pitcher risk below avg (-0.29).""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 24.0, 'batterWhiff': 27.5, 'pitcherK': 18.6}),
            row("Ben Rice", "L", "+300", 62, "", ["vs Hughes"], """0 HR, 89.8 mph EV. Hughes LHB split -0.52, HR risk -0.29. tough split lane (-0.52); pitcher risk below avg (-0.29).""", contact={'stars': 3, 'k': 20.8, 'batterK': 23.1, 'batterWhiff': 26.3, 'pitcherK': 18.6}),
            row("Mickey Moniak", "L", "+427", 70, "", ["vs Schlittler"], """1 HR, 1 near-HR, 91.7 mph EV, 12.5% barrels. Schlittler LHB split -0.13, HR risk -0.49. slight split headwind (-0.13); pitcher suppresses HR (-0.49).""", blast="good", contact={'stars': 1, 'k': 30.8, 'batterK': 27.8, 'batterWhiff': 28.2, 'pitcherK': 33.6}),
            row("Jake McCarthy", "L", "+980", 66, "", ["vs Schlittler"], """0 HR, 1 near-HR, 94.0 mph EV, 12.5% barrels. Schlittler LHB split -0.13, HR risk -0.49. slight split headwind (-0.13); pitcher suppresses HR (-0.49).""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 12.8, 'batterWhiff': 16.8, 'pitcherK': 33.6}),
            row("TJ Rumfield", "L", "+940", 56, "💎", ["vs Schlittler"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 83.8 mph EV, 25.0% barrels. Schlittler LHB split -0.13, HR risk -0.49. slight split headwind (-0.13); pitcher suppresses HR (-0.49).""", blast="good", contact={'stars': 3, 'k': 22.8, 'batterK': 10.5, 'batterWhiff': 16.9, 'pitcherK': 33.6}),
        ],
    },
    {
        "title": "HOU @ PHI - Hayden Wesneski (R, HOU) vs Andrew Painter (R, PHI)",
        "kLines": {'Wesneski': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 22.2, 'matchupK': 19.8, 'ownK': 20.9}, 'Painter': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 21.7, 'matchupK': 21.8, 'ownK': 21.8}},
        "description": "Tail key data: Park boost +9% (stadium +14%, weather -6%). Wesneski (HR risk -0.31, vs LHB +0.54, vs RHB -0.99). Painter (HR risk -0.36, vs LHB +0.34, vs RHB -0.59).",
        "rows": [
            row("Bryson Stott", "L", "+680", 77, "", ["vs Wesneski"], """1 HR, 3 near-HR, 93.5 mph EV, 25.0% barrels. Wesneski LHB split +0.54, HR risk -0.31. pitcher risk below avg (-0.31); weather carry headwind (-6%).""", blast="good", contact={'stars': 4, 'k': 19.6, 'batterK': 16.5, 'batterWhiff': 21.6, 'pitcherK': 20.9}),
            row("Kyle Schwarber", "L", "+235", 79, "", ["vs Wesneski"], """1 HR, 1 near-HR, 90.1 mph EV, 12.5% barrels. Wesneski LHB split +0.54, HR risk -0.31. pitcher risk below avg (-0.31); weather carry headwind (-6%).""", blast="good", contact={'stars': 3, 'k': 23.2, 'batterK': 22.8, 'batterWhiff': 33.2, 'pitcherK': 20.9}),
            row("Bryce Harper", "L", "+435", 79, "", ["vs Wesneski"], """1 HR, 1 near-HR, 89.2 mph EV, 12.5% barrels. Wesneski LHB split +0.54, HR risk -0.31. pitcher risk below avg (-0.31); weather carry headwind (-6%).""", blast="good", contact={'stars': 3, 'k': 21.4, 'batterK': 19.8, 'batterWhiff': 27.6, 'pitcherK': 20.9}),
            row("Nelson Velazquez", "R", "N/A", 69, "💎", ["vs Painter"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.2 mph EV, 12.5% barrels. Painter RHB split -0.59, HR risk -0.36. tough split lane (-0.59); pitcher risk below avg (-0.36).""", blast="good", contact={'stars': 1, 'k': 27.9, 'batterK': 43.2, 'batterWhiff': 48.5, 'pitcherK': 21.8}),
            row("Yainer Diaz", "R", "+850", 75, "", ["vs Painter"], """1 HR, 1 near-HR, 95.1 mph EV, 12.5% barrels. Painter RHB split -0.59, HR risk -0.36. tough split lane (-0.59); pitcher risk below avg (-0.36).""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 17.9, 'batterWhiff': 24.1, 'pitcherK': 21.8}),
            row("Yordan Alvarez", "L", "+250", 78, "", ["vs Painter"], """0 HR, 1 near-HR, 95.9 mph EV. Painter LHB split +0.34, HR risk -0.36. pitcher risk below avg (-0.36); weather carry headwind (-6%).""", blast="good", contact={'stars': 3, 'k': 20.0, 'batterK': 21.4, 'batterWhiff': 15.6, 'pitcherK': 21.8}),
            row("Daulton Varsho", "L", "+548", 63, "", ["vs Painter"], """0 HR, 3 near-HR, 84.1 mph EV, 25.0% barrels. Painter LHB split +0.34, HR risk -0.36. pitcher risk below avg (-0.36); weather carry headwind (-6%).""", blast="good", contact={'stars': 3, 'k': 21.9, 'batterK': 20.5, 'batterWhiff': 26.5, 'pitcherK': 21.8}),
        ],
    },
    {
        "title": "LAA @ BOS - Reid Detmers (L, LAA) vs Patrick Sandoval (L, BOS)",
        "kLines": {'Detmers': {'k': 6.4, 'lo': 5, 'hi': 8, 'bf': 23.0, 'matchupK': 27.8, 'ownK': 29.7}, 'Sandoval': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 22.3, 'matchupK': 23.9, 'ownK': 22.0}},
        "description": "Tail key data: Park boost -8% (stadium -6%, weather -2%). Detmers (HR risk -0.97, vs LHB -0.71, vs RHB -0.73). Sandoval (HR risk -0.04, vs LHB -0.61, vs RHB +0.17).",
        "rows": [
            row("Nick Sogard", "S", "+1150", 46, "", ["vs Detmers"], """1 HR, 1 near-HR, 83.2 mph EV. Detmers SHB→RHB split -0.73, HR risk -0.97. tough split lane (-0.73); pitcher suppresses HR (-0.97).""", blast="good", contact={'stars': 2, 'k': 24.1, 'batterK': 19.3, 'batterWhiff': 19.1, 'pitcherK': 29.7}),
            row("Roman Anthony", "L", "+790", 53, "💎", ["vs Detmers"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 90.8 mph EV, 20.0% barrels. Detmers LHB split -0.71, HR risk -0.97. tough split lane (-0.71); pitcher suppresses HR (-0.97).""", blast="good", contact={'stars': 1, 'k': 27.6, 'batterK': 25.6, 'batterWhiff': 25.9, 'pitcherK': 29.7}),
            row("Jose Siri", "R", "+600", 67, "", ["vs Sandoval"], """0 HR, 94.8 mph EV. Sandoval RHB split +0.17, HR risk -0.04. pitcher risk below avg (-0.04); park/weather net drag (-8%).""", blast="good", contact={'stars': 2, 'k': 26.9, 'batterK': 37.5, 'batterWhiff': 40.2, 'pitcherK': 22.0}),
            row("Mike Trout", "R", "+625", 67, "", ["vs Sandoval"], """0 HR, 94.6 mph EV. Sandoval RHB split +0.17, HR risk -0.04. pitcher risk below avg (-0.04); park/weather net drag (-8%).""", blast="good", contact={'stars': 2, 'k': 24.9, 'batterK': 28.7, 'batterWhiff': 30.5, 'pitcherK': 22.0}),
        ],
    },
    {
        "title": "MIN @ DET - Dean Kremer (R, MIN) vs Drew Anderson (R, DET)",
        "kLines": {'Kremer': {'k': 4.8, 'lo': 3, 'hi': 6, 'bf': 21.6, 'matchupK': 22.2, 'ownK': 21.4}, 'Anderson': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 19.8, 'matchupK': 18.8, 'ownK': 20.1}},
        "description": "Tail key data: Park boost -12% (stadium -10%, weather -2%). Kremer (HR risk 0.76, vs LHB +0.61, vs RHB +0.80). Anderson (HR risk 0.57, vs LHB +0.77, vs RHB +0.14).",
        "rows": [
            row("Colt Keith", "L", "+650", 68, "", ["vs Kremer"], """0 HR, 90.8 mph EV, 12.5% barrels. Kremer LHB split +0.61, HR risk 0.76. park/weather net drag (-12%); limited recent HR events.""", contact={'stars': 3, 'k': 23.8, 'batterK': 27.3, 'batterWhiff': 31.5, 'pitcherK': 21.4}),
            row("Gleyber Torres", "R", "+960", 64, "", ["vs Kremer"], """0 HR, 97.1 mph EV. Kremer RHB split +0.80, HR risk 0.76. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.1, 'batterK': 19.0, 'batterWhiff': 20.2, 'pitcherK': 21.4}),
            row("Kevin McGonigle", "L", "+725", 71, "", ["vs Kremer"], """1 HR, 1 near-HR, 84.3 mph EV, 12.5% barrels. Kremer LHB split +0.61, HR risk 0.76. park/weather net drag (-12%); lighter EV form (84.3 mph).""", blast="good", contact={'stars': 4, 'k': 17.3, 'batterK': 12.2, 'batterWhiff': 16.1, 'pitcherK': 21.4}),
            row("John Peck", "R", "+880", 81, "🚀 🌕 💣", ["vs Kremer"], """0 HR, 1 near-HR, 101.8 mph EV, 40.0% barrels. Kremer RHB split +0.80, HR risk 0.76. park/weather net drag (-12%); limited recent HR events.""", blast="high", contact={'stars': 3, 'k': 22.1, 'batterK': 24.0, 'batterWhiff': 26.5, 'pitcherK': 21.4}),
            row("Ben Malgeri", "R", "+980", 79, "", ["vs Kremer"], """1 HR, 1 near-HR, 93.5 mph EV, 12.5% barrels. Kremer RHB split +0.80, HR risk 0.76. park/weather net drag (-12%).""", blast="good", contact={'stars': 2, 'k': 24.3, 'batterK': 34.6, 'batterWhiff': 29.7, 'pitcherK': 21.4}),
            row("Riley Greene", "L", "+425", 74, "", ["vs Kremer"], """0 HR, 82.5 mph EV, 25.0% barrels. Kremer LHB split +0.61, HR risk 0.76. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.8, 'batterK': 26.4, 'batterWhiff': 29.9, 'pitcherK': 21.4}),
            row("Brett Callahan", "L", "+596", 74, "", ["vs Kremer"], """0 HR, 2 near-HR, 92.8 mph EV, 12.5% barrels. Kremer LHB split +0.61, HR risk 0.76. park/weather net drag (-12%).""", blast="good", contact={'stars': 3, 'k': 23.9, 'batterK': 37.2, 'batterWhiff': 28.9, 'pitcherK': 21.4}),
            row("Josh Bell", "S", "+550", 85, "⭐", ["vs Anderson"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.1 mph EV, 25.0% barrels. Anderson SHB→LHB split +0.77, HR risk 0.57. park/weather net drag (-12%).""", blast="good", contact={'stars': 4, 'k': 18.1, 'batterK': 14.3, 'batterWhiff': 18.4, 'pitcherK': 20.1}),
            row("Brooks Lee", "S", "+880", 75, "", ["vs Anderson"], """1 HR, 1 near-HR, 91.5 mph EV, 12.5% barrels. Anderson SHB→LHB split +0.77, HR risk 0.57. park/weather net drag (-12%).""", blast="good", contact={'stars': 5, 'k': 16.9, 'batterK': 12.2, 'batterWhiff': 14.4, 'pitcherK': 20.1}),
            row("Trevor Larnach", "L", "+990", 77, "💎", ["vs Anderson"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.0 mph EV, 12.5% barrels. Anderson LHB split +0.77, HR risk 0.57. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.9, 'batterK': 21.7, 'batterWhiff': 33.3, 'pitcherK': 20.1}),
            row("Royce Lewis", "R", "+525", 62, "", ["vs Anderson"], """0 HR, 1 near-HR, 87.5 mph EV, 25.0% barrels. Anderson RHB split +0.14, HR risk 0.57. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.5, 'batterK': 17.5, 'batterWhiff': 26.6, 'pitcherK': 20.1}),
            row("Luke Keaschall", "R", "+1000", 63, "", ["vs Anderson"], """1 HR, 1 near-HR, 94.5 mph EV. Anderson RHB split +0.14, HR risk 0.57. park/weather net drag (-12%).""", blast="good", contact={'stars': 5, 'k': 16.9, 'batterK': 13.0, 'batterWhiff': 14.9, 'pitcherK': 20.1}),
        ],
    },
    {
        "title": "NYM @ MIA - Sean Manaea 🧤 (L, NYM) vs Sandy Alcantara (R, MIA)",
        "kLines": {'Manaea': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 23.8, 'matchupK': 21.2, 'ownK': 20.8}, 'Alcantara': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 26.1, 'matchupK': 17.6, 'ownK': 15.8}},
        "description": "Tail key data: Park boost -13% (stadium -13%, weather +0%). Manaea 🧤 (HR risk 1.63, vs LHB +0.09, vs RHB +1.30). Alcantara (HR risk -0.77, vs LHB -0.08, vs RHB -0.96).",
        "rows": [
            row("Griffin Conine", "L", "+358", 77, "", ["vs Manaea"], """1 HR, 1 near-HR, 89.2 mph EV, 12.5% barrels. Manaea LHB split +0.09, HR risk 1.63. park/weather net drag (-13%).""", blast="good", contact={'stars': 2, 'k': 24.9, 'batterK': 28.0, 'batterWhiff': 36.3, 'pitcherK': 20.8}),
            row("Agustin Ramirez", "R", "+650", 81, "", ["vs Manaea"], """0 HR, 95.2 mph EV. Manaea RHB split +1.30, HR risk 1.63. park/weather net drag (-13%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.4, 'batterK': 23.3, 'batterWhiff': 24.1, 'pitcherK': 20.8}),
            row("Heriberto Hernandez", "R", "+390", 90, "⭐ 🌕 💣", ["vs Manaea"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 93.2 mph EV, 25.0% barrels. Manaea RHB split +1.30, HR risk 1.63. park/weather net drag (-13%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 26.1, 'batterWhiff': 30.5, 'pitcherK': 20.8}),
            row("Kyle Stowers", "L", "+475", 87, "💎", ["vs Manaea"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.9 mph EV, 25.0% barrels. Manaea LHB split +0.09, HR risk 1.63. park/weather net drag (-13%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 27.1, 'batterK': 34.6, 'batterWhiff': 39.0, 'pitcherK': 20.8}),
            row("A.J Ewing", "L", "+1000", 54, "", ["vs Alcantara"], """1 HR, 1 near-HR, 89.9 mph EV, 12.5% barrels. Alcantara LHB split -0.08, HR risk -0.77. slight split headwind (-0.08); pitcher suppresses HR (-0.77).""", blast="good", contact={'stars': 4, 'k': 19.2, 'batterK': 26.2, 'batterWhiff': 23.3, 'pitcherK': 15.8}),
            row("Francisco Lindor", "S", "+450", 68, "⭐", ["vs Alcantara"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.6 mph EV, 12.5% barrels. Alcantara SHB→LHB split -0.08, HR risk -0.77. slight split headwind (-0.08); pitcher suppresses HR (-0.77).""", blast="good", contact={'stars': 4, 'k': 18.4, 'batterK': 21.3, 'batterWhiff': 25.9, 'pitcherK': 15.8}),
            row("Juan Soto", "L", "+340", 79, "⭐", ["vs Alcantara"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 98.8 mph EV, 12.5% barrels. Alcantara LHB split -0.08, HR risk -0.77. slight split headwind (-0.08); pitcher suppresses HR (-0.77).""", blast="good", contact={'stars': 5, 'k': 16.9, 'batterK': 15.7, 'batterWhiff': 24.3, 'pitcherK': 15.8}),
            row("Brett Baty", "L", "+800", 65, "💎", ["vs Alcantara"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 94.0 mph EV, 25.0% barrels. Alcantara LHB split -0.08, HR risk -0.77. slight split headwind (-0.08); pitcher suppresses HR (-0.77).""", blast="good", contact={'stars': 3, 'k': 20.7, 'batterK': 26.3, 'batterWhiff': 33.9, 'pitcherK': 15.8}),
            row("Francisco Alvarez", "R", "+700", 71, "", ["vs Alcantara"], """1 HR, 3 near-HR, 94.4 mph EV, 25.0% barrels. Alcantara RHB split -0.96, HR risk -0.77. tough split lane (-0.96); pitcher suppresses HR (-0.77).""", blast="good", contact={'stars': 2, 'k': 26.6, 'batterK': 47.2, 'batterWhiff': 43.4, 'pitcherK': 15.8}),
        ],
    },
    {
        "title": "PIT @ CWS - Bubba Chandler (R, PIT) vs Sean Burke (R, CWS)",
        "kLines": {'Chandler': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 21.9, 'matchupK': 21.2, 'ownK': 19.7}, 'Burke': {'k': 6.2, 'lo': 5, 'hi': 8, 'bf': 22.4, 'matchupK': 27.5, 'ownK': 27.2}},
        "description": "Tail key data: Park boost -4% (stadium -5%, weather +1%). Chandler (HR risk -0.59, vs LHB +0.42, vs RHB -1.21). Burke (HR risk 0.40, vs LHB +0.96, vs RHB -0.06).",
        "rows": [
            row("Tristan Peters", "L", "+790", 72, "🌕 💣 💎", ["vs Chandler"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 99.6 mph EV, 25.0% barrels. Chandler LHB split +0.42, HR risk -0.59. pitcher suppresses HR (-0.59).""", blast="high", contact={'stars': 4, 'k': 19.4, 'batterK': 14.1, 'batterWhiff': 25.4, 'pitcherK': 19.7}),
            row("Munetaka Murakami", "L", "+312", 69, "⭐", ["vs Chandler"], """Worst Pickz Favorite. 0 HR, 99.0 mph EV. Chandler LHB split +0.42, HR risk -0.59. pitcher suppresses HR (-0.59); limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 28.5, 'batterK': 38.5, 'batterWhiff': 41.9, 'pitcherK': 19.7}),
            row("Colson Montgomery", "L", "+339", 67, "", ["vs Chandler"], """1 HR, 1 near-HR, 87.3 mph EV, 12.5% barrels. Chandler LHB split +0.42, HR risk -0.59. pitcher suppresses HR (-0.59); lighter EV form (87.3 mph).""", blast="good", contact={'stars': 1, 'k': 28.7, 'batterK': 44.0, 'batterWhiff': 36.7, 'pitcherK': 19.7}),
            row("Miguel Vargas", "R", "+413", 63, "", ["vs Chandler"], """1 HR, 1 near-HR, 89.3 mph EV, 12.5% barrels. Chandler RHB split -1.21, HR risk -0.59. tough split lane (-1.21); pitcher suppresses HR (-0.59).""", blast="good", contact={'stars': 4, 'k': 17.8, 'batterK': 15.6, 'batterWhiff': 17.5, 'pitcherK': 19.7}),
            row("Bryan Reynolds", "S", "+550", 85, "⭐", ["vs Burke"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.5 mph EV, 25.0% barrels. Burke SHB→LHB split +0.96, HR risk 0.40.""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 17.0, 'batterWhiff': 25.2, 'pitcherK': 27.2}),
            row("Oneil Cruz", "L", "+350", 76, "", ["vs Burke"], """0 HR, 90.6 mph EV, 12.5% barrels. Burke LHB split +0.96, HR risk 0.40. limited recent HR events.""", contact={'stars': 1, 'k': 30.7, 'batterK': 36.7, 'batterWhiff': 34.8, 'pitcherK': 27.2}),
        ],
    },
    {
        "title": "STL @ SF - Quinn Mathews (L, STL) vs Landen Roupp (R, SF)",
        "kLines": {'Mathews': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 22.0, 'matchupK': 21.4, 'ownK': 21.4}, 'Roupp': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 22.6, 'matchupK': 18.8, 'ownK': 16.3}},
        "description": "Tail key data: Park boost -12% (stadium -16%, weather +4%). Mathews (HR risk -1.71, vs LHB -2.00, vs RHB -1.10). Roupp (HR risk -0.87, vs LHB -0.52, vs RHB -0.64).",
        "rows": [
            row("Jonah Cox", "R", "+1150", 69, "⭐ 🌕 💣", ["vs Mathews"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 98.1 mph EV, 25.0% barrels. Mathews RHB split -1.10, HR risk -1.71. tough split lane (-1.10); pitcher suppresses HR (-1.71).""", blast="high", contact={'stars': 2, 'k': 25.7, 'batterK': 36.5, 'batterWhiff': 31.4, 'pitcherK': 21.4}),
            row("Bryce Eldridge", "L", "+610", 65, "🚀 💎", ["vs Mathews"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 102.7 mph EV, 12.5% barrels. Mathews LHB split -2.00, HR risk -1.71. tough split lane (-2.00); pitcher suppresses HR (-1.71).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 25.6, 'batterWhiff': 25.9, 'pitcherK': 21.4}),
            row("Rafael Devers", "L", "+501", 51, "", ["vs Mathews"], """1 HR, 1 near-HR, 90.8 mph EV, 12.5% barrels. Mathews LHB split -2.00, HR risk -1.71. tough split lane (-2.00); pitcher suppresses HR (-1.71).""", blast="good", contact={'stars': 3, 'k': 21.8, 'batterK': 19.8, 'batterWhiff': 28.6, 'pitcherK': 21.4}),
            row("Joshua Baez", "R", "+640", 67, "", ["vs Roupp"], """1 HR, 1 near-HR, 93.3 mph EV, 25.0% barrels. Roupp RHB split -0.64, HR risk -0.87. tough split lane (-0.64); pitcher suppresses HR (-0.87).""", blast="good", contact={'stars': 3, 'k': 23.7, 'batterK': 33.8, 'batterWhiff': 37.3, 'pitcherK': 16.3}),
            row("Alec Burleson", "L", "+725", 68, "", ["vs Roupp"], """1 HR, 1 near-HR, 96.2 mph EV, 25.0% barrels. Roupp LHB split -0.52, HR risk -0.87. tough split lane (-0.52); pitcher suppresses HR (-0.87).""", blast="good", contact={'stars': 4, 'k': 19.2, 'batterK': 22.5, 'batterWhiff': 25.5, 'pitcherK': 16.3}),
            row("Ivan Herrera", "R", "+875", 56, "", ["vs Roupp"], """1 HR, 2 near-HR, 91.3 mph EV, 12.5% barrels. Roupp RHB split -0.64, HR risk -0.87. tough split lane (-0.64); pitcher suppresses HR (-0.87).""", blast="good", contact={'stars': 4, 'k': 18.8, 'batterK': 23.7, 'batterWhiff': 20.2, 'pitcherK': 16.3}),
            row("Leonardo Bernal", "S", "+1050", 49, "💎", ["vs Roupp"], """Worst Pickz Hidden Gem. 0 HR, 98.3 mph EV. Roupp SHB→LHB split -0.52, HR risk -0.87. tough split lane (-0.52); pitcher suppresses HR (-0.87).""", blast="good"),
        ],
    },
    {
        "title": "TB @ ATL - Freddy Peralta (R, TB) vs AJ Smith-Shawver (R, ATL)",
        "kLines": {'Peralta': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 22.7, 'matchupK': 22.8, 'ownK': 21.7}, 'Smith-Shawver': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 21.4, 'matchupK': 17.7, 'ownK': 17.9}},
        "description": "Tail key data: Park boost -4% (stadium -1%, weather -3%). Peralta (HR risk 0.23, vs LHB +0.38, vs RHB +0.04). Smith-Shawver (HR risk -0.16, vs LHB -0.23, vs RHB +0.23).",
        "rows": [
            row("Ronald Acuna Jr.", "R", "+411", 83, "⭐ 🌕 💣", ["vs Peralta"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.9 mph EV, 25.0% barrels. Peralta RHB split +0.04, HR risk 0.23.""", blast="high"),
            row("Ozzie Albies", "S", "+650", 64, "", ["vs Peralta"], """1 HR, 1 near-HR, 92.2 mph EV, 12.5% barrels. Peralta SHB→LHB split +0.38, HR risk 0.23.""", blast="good", contact={'stars': 4, 'k': 19.0, 'batterK': 16.7, 'batterWhiff': 17.0, 'pitcherK': 21.7}),
            row("Matt Olson", "L", "+350", 69, "", ["vs Peralta"], """0 HR, 1 near-HR, 94.0 mph EV. Peralta LHB split +0.38, HR risk 0.23. limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.3, 'batterK': 30.1, 'batterWhiff': 32.1, 'pitcherK': 21.7}),
            row("Drake Baldwin", "L", "+440", 60, "", ["vs Peralta"], """0 HR, 89.1 mph EV. Peralta LHB split +0.38, HR risk 0.23. limited recent HR events.""", contact={'stars': 2, 'k': 25.5, 'batterK': 28.4, 'batterWhiff': 35.1, 'pitcherK': 21.7}),
            row("Brewer Hicklen", "R", "N/A", 70, "🌕 💣", ["vs Peralta"], """0 HR, 99.4 mph EV, 50.0% barrels. Peralta RHB split +0.04, HR risk 0.23. limited recent HR events.""", blast="high", contact={'stars': 2, 'k': 25.7, 'batterK': 35.7, 'batterWhiff': 44.2, 'pitcherK': 21.7}),
            row("Junior Caminero", "R", "+314", 86, "⭐ 🌕 💣", ["vs Smith-Shawver"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.1 mph EV, 25.0% barrels. Smith-Shawver RHB split +0.23, HR risk -0.16. pitcher risk below avg (-0.16).""", blast="high", contact={'stars': 4, 'k': 19.7, 'batterK': 17.2, 'batterWhiff': 25.0, 'pitcherK': 17.9}),
            row("Jonathan Aranda", "L", "+497", 69, "", ["vs Smith-Shawver"], """0 HR, 96.8 mph EV. Smith-Shawver LHB split -0.23, HR risk -0.16. slight split headwind (-0.23); pitcher risk below avg (-0.16).""", blast="good", contact={'stars': 3, 'k': 22.7, 'batterK': 28.6, 'batterWhiff': 25.1, 'pitcherK': 17.9}),
            row("Yandy Diaz", "R", "+520", 54, "", ["vs Smith-Shawver"], """0 HR, 89.4 mph EV. Smith-Shawver RHB split +0.23, HR risk -0.16. pitcher risk below avg (-0.16); limited recent HR events.""", contact={'stars': 5, 'k': 16.8, 'batterK': 13.3, 'batterWhiff': 15.2, 'pitcherK': 17.9}),
            row("Ryan Vilade", "R", "N/A", 69, "⭐", ["vs Smith-Shawver"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 83.9 mph EV, 12.5% barrels. Smith-Shawver RHB split +0.23, HR risk -0.16. pitcher risk below avg (-0.16); lighter EV form (83.9 mph).""", blast="good", contact={'stars': 3, 'k': 21.5, 'batterK': 21.7, 'batterWhiff': 27.6, 'pitcherK': 17.9}),
        ],
    },
    {
        "title": "TEX @ SEA - Cody Bradford (L, TEX) vs Bryce Miller (R, SEA)",
        "kLines": {'Bradford': {'k': 3.5, 'lo': 2, 'hi': 5, 'bf': 22.0, 'matchupK': 16.0, 'ownK': 11.9}, 'Miller': {'k': 4.1, 'lo': 3, 'hi': 6, 'bf': 22.1, 'matchupK': 18.7, 'ownK': 17.5}},
        "description": "Tail key data: Park boost -6% (stadium +1%, weather -7%). Bradford (BAA vs LHB .419, vs RHB .280, HR/9 1.19). Miller (BAA vs LHB .251, vs RHB .198, HR/9 1.55).",
        "rows": [
            row("Cal Raleigh", "S", "+285", 79, "💎", ["vs Bradford"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.4 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-6%).""", blast="good", contact={'stars': 3, 'k': 20.6, 'batterK': 26.6, 'batterWhiff': 33.8, 'pitcherK': 11.9}),
            row("Dominic Canzone", "L", "+566", 58, "💎", ["vs Bradford"], """Worst Pickz Hidden Gem. 0 HR, 91.3 mph EV. limited split/risk sample; park/weather net drag (-6%).""", contact={'stars': 4, 'k': 18.7, 'batterK': 24.4, 'batterWhiff': 24.2, 'pitcherK': 11.9}),
            row("Randy Arozarena", "R", "+470", 68, "", ["vs Bradford"], """1 HR, 1 near-HR, 87.8 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-6%).""", blast="good", contact={'stars': 4, 'k': 19.1, 'batterK': 23.9, 'batterWhiff': 28.0, 'pitcherK': 11.9}),
            row("Corey Seager", "L", "+357", 82, "", ["vs Miller"], """1 HR, 1 near-HR, 93.3 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-6%).""", blast="good", contact={'stars': 3, 'k': 20.0, 'batterK': 19.5, 'batterWhiff': 30.7, 'pitcherK': 17.5}),
            row("Justin Foscue", "R", "N/A", 80, "💎", ["vs Miller"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.9 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-6%).""", blast="good", contact={'stars': 5, 'k': 16.9, 'batterK': 15.5, 'batterWhiff': 15.1, 'pitcherK': 17.5}),
            row("Brandon Nimmo", "L", "+565", 69, "⭐", ["vs Miller"], """Worst Pickz Favorite. 0 HR, 94.6 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-6%).""", blast="good", contact={'stars': 4, 'k': 18.8, 'batterK': 19.8, 'batterWhiff': 22.9, 'pitcherK': 17.5}),
            row("Joc Pederson", "L", "+481", 79, "", ["vs Miller"], """1 HR, 1 near-HR, 91.5 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-6%).""", blast="good", contact={'stars': 3, 'k': 21.8, 'batterK': 32.7, 'batterWhiff': 29.9, 'pitcherK': 17.5}),
        ],
    },
    {
        "title": "TOR @ ATH - Jose Soriano (R, TOR) vs Jack Perkins (R, ATH)",
        "kLines": {'Soriano': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 23.1, 'matchupK': 18.6, 'ownK': 17.3}, 'Perkins': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 21.7, 'matchupK': 20.3, 'ownK': 22.9}},
        "description": "Tail key data: Park boost +27% (stadium +30%, weather -3%). Soriano (HR risk -0.57, vs LHB -0.30, vs RHB -0.37). Perkins (HR risk 0.33, vs LHB +0.84, vs RHB -0.11).",
        "rows": [
            row("Lawrence Butler", "L", "+630", 74, "💎", ["vs Soriano"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.2 mph EV, 25.0% barrels. Soriano LHB split -0.30, HR risk -0.57. slight split headwind (-0.30); pitcher suppresses HR (-0.57).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 34.1, 'batterWhiff': 28.0, 'pitcherK': 17.3}),
            row("Donovan Walton", "L", "+1160", 65, "💎", ["vs Soriano"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 89.3 mph EV, 12.5% barrels. Soriano LHB split -0.30, HR risk -0.57. slight split headwind (-0.30); pitcher suppresses HR (-0.57).""", blast="good", contact={'stars': 3, 'k': 20.0, 'batterK': 15.6, 'batterWhiff': 33.1, 'pitcherK': 17.3}),
            row("Henry Bolte", "R", "+980", 74, "", ["vs Soriano"], """1 HR, 1 near-HR, 97.9 mph EV, 12.5% barrels. Soriano RHB split -0.37, HR risk -0.57. slight split headwind (-0.37); pitcher suppresses HR (-0.57).""", blast="good", contact={'stars': 3, 'k': 22.1, 'batterK': 27.4, 'batterWhiff': 31.9, 'pitcherK': 17.3}),
            row("Kazuma Okamoto", "R", "+368", 82, "", ["vs Perkins"], """1 HR, 2 near-HR, 89.8 mph EV, 25.0% barrels. Perkins RHB split -0.11, HR risk 0.33. slight split headwind (-0.11).""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 21.7, 'batterWhiff': 30.7, 'pitcherK': 22.9}),
            row("George Springer", "R", "+430", 66, "", ["vs Perkins"], """0 HR, 93.2 mph EV. Perkins RHB split -0.11, HR risk 0.33. slight split headwind (-0.11); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.6, 'batterK': 18.9, 'batterWhiff': 24.0, 'pitcherK': 22.9}),
            row("Vladimir Guerrero Jr.", "R", "+422", 67, "🚀 💎", ["vs Perkins"], """Worst Pickz Hidden Gem. 0 HR, 102.3 mph EV. Perkins RHB split -0.11, HR risk 0.33. slight split headwind (-0.11); limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 16.5, 'batterK': 8.3, 'batterWhiff': 13.2, 'pitcherK': 22.9}),
            row("Andres Gimenez", "L", "+990", 68, "", ["vs Perkins"], """0 HR, 1 near-HR, 92.8 mph EV, 12.5% barrels. Perkins LHB split +0.84, HR risk 0.33. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.8, 'batterK': 15.5, 'batterWhiff': 23.5, 'pitcherK': 22.9}),
        ],
    },
    {
        "title": "WSH @ SD - Riley Cornelio (R, WSH) vs Casey Mize 🧤 (R, SD)",
        "kLines": {'Cornelio': {'k': 5.1, 'lo': 3, 'hi': 7, 'bf': 21.7, 'matchupK': 23.4, 'ownK': 25.0}, 'Mize': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 21.2, 'matchupK': 17.4, 'ownK': 15.2}},
        "description": "Tail key data: Park boost -5% (stadium -6%, weather +2%). Cornelio (HR risk 0.30, vs LHB -0.71, vs RHB +0.93). Mize 🧤 (HR risk 1.21, vs LHB +0.70, vs RHB +1.19).",
        "rows": [
            row("Manny Machado", "R", "+460", 74, "⭐", ["vs Cornelio"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.4 mph EV, 25.0% barrels. Cornelio RHB split +0.93, HR risk 0.30. park/weather net drag (-5%).""", blast="good", contact={'stars': 3, 'k': 21.6, 'batterK': 18.2, 'batterWhiff': 23.9, 'pitcherK': 25.0}),
            row("Ty France", "R", "+560", 76, "💎", ["vs Cornelio"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.3 mph EV, 25.0% barrels. Cornelio RHB split +0.93, HR risk 0.30. park/weather net drag (-5%).""", blast="good", contact={'stars': 3, 'k': 22.6, 'batterK': 18.6, 'batterWhiff': 28.6, 'pitcherK': 25.0}),
            row("Fernando Tatis Jr.", "R", "+444", 86, "", ["vs Cornelio"], """1 HR, 2 near-HR, 94.9 mph EV, 25.0% barrels. Cornelio RHB split +0.93, HR risk 0.30. park/weather net drag (-5%).""", blast="good", contact={'stars': 3, 'k': 20.5, 'batterK': 15.9, 'batterWhiff': 21.9, 'pitcherK': 25.0}),
            row("Jackson Merrill", "L", "+493", 82, "🚀 🌕 💣", ["vs Cornelio"], """0 HR, 106.9 mph EV, 37.5% barrels. Cornelio LHB split -0.71, HR risk 0.30. tough split lane (-0.71); park/weather net drag (-5%).""", blast="high", contact={'stars': 2, 'k': 24.3, 'batterK': 23.8, 'batterWhiff': 29.9, 'pitcherK': 25.0}),
            row("Daylen Lile", "L", "+484", 97, "🌕 💣", ["vs Mize"], """2 HR, 3 near-HR, 94.6 mph EV, 50.0% barrels. Mize LHB split +0.70, HR risk 1.21. park/weather net drag (-5%).""", blast="high", contact={'stars': 4, 'k': 18.8, 'batterK': 24.1, 'batterWhiff': 22.8, 'pitcherK': 15.2}),
            row("Yohandy Morales", "R", "N/A", 88, "🌕 💣", ["vs Mize"], """1 HR, 1 near-HR, 93.3 mph EV, 33.3% barrels. Mize RHB split +1.19, HR risk 1.21. park/weather net drag (-5%).""", blast="good", contact={'stars': 3, 'k': 20.6, 'batterK': 50.0, 'batterWhiff': 45.5, 'pitcherK': 15.2}),
            row("Keibert Ruiz", "S", "+660", 78, "💎", ["vs Mize"], """Worst Pickz Hidden Gem. 0 HR, 3 near-HR, 97.2 mph EV. Mize SHB→LHB split +0.70, HR risk 1.21. park/weather net drag (-5%).""", blast="good", contact={'stars': 5, 'k': 14.9, 'batterK': 9.7, 'batterWhiff': 16.8, 'pitcherK': 15.2}),
            row("James Wood", "L", "+306", 91, "⭐ 🌕 💣", ["vs Mize"], """Worst Pickz Favorite. 0 HR, 96.9 mph EV, 12.5% barrels. Mize LHB split +0.70, HR risk 1.21. park/weather net drag (-5%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.8, 'batterK': 22.3, 'batterWhiff': 25.7, 'pitcherK': 15.2}),
            row("Dylan Crews", "R", "+546", 72, "", ["vs Mize"], """0 HR, 92.5 mph EV. Mize RHB split +1.19, HR risk 1.21. park/weather net drag (-5%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.6, 'batterK': 27.2, 'batterWhiff': 29.5, 'pitcherK': 15.2}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-08")

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

    out = ROOT / '_games-0908.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
