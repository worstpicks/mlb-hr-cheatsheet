#!/usr/bin/env python3
"""Generate games[] block for 2026-09-11 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alejandro Kirk (R)",
    "Bryce Eldridge (L)",
    "Chase DeLauter (L)",
    "Coby Mayo (R)",
    "Cody Bellinger (L)",
    "Elly De La Cruz (S)",
    "Heriberto Hernandez (R)",
    "Isaac Paredes (R)",
    "Jackson Merrill (L)",
    "Jake Bauers (L)",
    "Junior Caminero (R)",
    "Kyle Schwarber (L)",
    "Mookie Betts (R)",
    "Spencer Jones (L)",
    "Travis Bazzana (L)",
    "Vladimir Guerrero Jr. (R)",
    "Will Smith (R)",
    "William Contreras (R)",
}

GEMS = {
    "Adael Amador (S)",
    "Andres Chaparro (R)",
    "Corbin Carroll (L)",
    "Dominic Canzone (L)",
    "Fernando Tatis Jr. (R)",
    "Francisco Lindor (S)",
    "Jake Rogers (R)",
    "Kazuma Okamoto (R)",
    "Ketel Marte (S)",
    "Lawrence Butler (L)",
    "Leonardo Bernal (S)",
    "Manny Machado (R)",
    "Matt Olson (L)",
    "Moises Ballesteros (L)",
    "Roman Anthony (L)",
    "Trea Turner (R)",
    "Ty France (R)",
    "Victor Mesa Jr. (L)",
    "Yainer Diaz (R)",
    "Zack Gelof (R)",
}

PLAYER_TEAMS = {
    "Aaron Judge (R)": "NYY",
    "Adael Amador (S)": "COL",
    "Adley Rutschman (S)": "BOS",
    "Alec Bohm (R)": "PHI",
    "Alejandro Kirk (R)": "TOR",
    "Andres Chaparro (R)": "WSH",
    "Andrew Vaughn (R)": "MIL",
    "Austin Riley (R)": "ATL",
    "Austin Wells (L)": "NYY",
    "Ben Rice (L)": "NYY",
    "Bo Bichette (R)": "NYM",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Nimmo (L)": "TEX",
    "Brett Bateman (L)": "TOR",
    "Brice Turang (L)": "MIL",
    "Brock Rodden (S)": "SEA",
    "Brooks Lee (S)": "MIN",
    "Bryce Eldridge (L)": "SF",
    "Cam Smith (R)": "HOU",
    "Chase DeLauter (L)": "CLE",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Coby Mayo (R)": "BAL",
    "Cody Bellinger (L)": "NYY",
    "Cole Young (L)": "SEA",
    "Colson Montgomery (L)": "CWS",
    "Colt Keith (L)": "DET",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Dylan Crews (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Eugenio Suarez (R)": "CIN",
    "Ezequiel Duran (R)": "TEX",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Gabriel Moreno (R)": "ARI",
    "Garrett Mitchell (L)": "MIL",
    "Gleyber Torres (R)": "DET",
    "Griffin Conine (L)": "MIA",
    "Harry Ford (R)": "WSH",
    "Heriberto Hernandez (R)": "MIA",
    "Isaac Paredes (R)": "HOU",
    "Ivan Herrera (R)": "STL",
    "JJ Bleday (L)": "CIN",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jake Rogers (R)": "CWS",
    "James Wood (L)": "WSH",
    "Jared Serna (R)": "MIA",
    "Jarren Duran (L)": "BOS",
    "Jonah Heim (S)": "ATH",
    "Jordan Walker (R)": "STL",
    "Josh Bell (S)": "MIN",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kazuma Okamoto (R)": "TOR",
    "Ke'Bryan Hayes (R)": "CIN",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Kyle Tucker (L)": "LAD",
    "Lawrence Butler (L)": "ATH",
    "Leody Taveras (S)": "BAL",
    "Leonardo Bernal (S)": "STL",
    "Luis Garcia Jr. (L)": "NYY",
    "Manny Machado (R)": "SD",
    "Mark Vientos (R)": "NYM",
    "Masyn Winn (R)": "STL",
    "Matt Olson (L)": "ATL",
    "Michael Massey (L)": "KC",
    "Mickey Gasper (S)": "BOS",
    "Miguel Vargas (R)": "CWS",
    "Moises Ballesteros (L)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Nathan Lukes (L)": "TOR",
    "Nathaniel Lowe (L)": "CLE",
    "Nelson Velazquez (R)": "HOU",
    "Nick Allen (R)": "HOU",
    "Ozzie Albies (S)": "ATL",
    "Pete Alonso (R)": "BAL",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Roman Anthony (L)": "BOS",
    "Royce Lewis (R)": "MIN",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Samuel Basallo (L)": "BAL",
    "Sean Murphy (R)": "ATL",
    "Spencer Jones (L)": "NYY",
    "Teoscar Hernandez (R)": "LAD",
    "Thomas Saggese (R)": "STL",
    "Travis Bazzana (L)": "CLE",
    "Trea Turner (R)": "PHI",
    "Troy Johnston (L)": "COL",
    "Turner Hill (L)": "SF",
    "Ty France (R)": "SD",
    "Tyler Stephenson (R)": "CIN",
    "Victor Mesa Jr. (L)": "TB",
    "Vinnie Pasquantino (L)": "KC",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Will Smith (R)": "LAD",
    "William Contreras (R)": "MIL",
    "Wyatt Langford (R)": "TEX",
    "Xander Bogaerts (R)": "SD",
    "Yainer Diaz (R)": "HOU",
    "Yandy Diaz (R)": "TB",
    "Yohandy Morales (R)": "WSH",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("COL @ DET", "Adams"),
    ("HOU @ TB", "Ullola"),
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
        "title": "BAL @ TOR - Chris Bassitt (R, BAL) vs Max Scherzer (R, TOR)",
        "kLines": {'Bassitt': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 22.6, 'matchupK': 16.6, 'ownK': 17.7}, 'Scherzer': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 20.1, 'matchupK': 20.4, 'ownK': 18.6}},
        "description": "Tail key data: Park boost -2% (stadium +7%, weather -8%). Bassitt (HR risk -0.45, vs LHB +0.03, vs RHB -0.77). Scherzer (HR risk -0.05, vs LHB -0.10, vs RHB +0.31).",
        "rows": [
            row("Kazuma Okamoto", "R", "+520", 81, "🌕 💣 💎", ["vs Bassitt"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 97.2 mph EV, 25.0% barrels. Bassitt RHB split -0.77, HR risk -0.45. tough split lane (-0.77); pitcher suppresses HR (-0.45).""", blast="high", contact={'stars': 3, 'k': 20.8, 'batterK': 22.9, 'batterWhiff': 29.7, 'pitcherK': 17.7}),
            row("Vladimir Guerrero Jr.", "R", "+650", 59, "🚀 ⭐", ["vs Bassitt"], """Worst Pickz Favorite. 0 HR, 101.4 mph EV, 12.5% barrels. Bassitt RHB split -0.77, HR risk -0.45. tough split lane (-0.77); pitcher suppresses HR (-0.45).""", blast="good", contact={'stars': 5, 'k': 14.6, 'batterK': 8.3, 'batterWhiff': 14.3, 'pitcherK': 17.7}),
            row("Nathan Lukes", "L", "+1120", 49, "", ["vs Bassitt"], """0 HR, 90.1 mph EV, 12.5% barrels. Bassitt LHB split +0.03, HR risk -0.45. pitcher suppresses HR (-0.45); weather carry headwind (-8%).""", contact={'stars': 4, 'k': 17.2, 'batterK': 16.7, 'batterWhiff': 17.1, 'pitcherK': 17.7}),
            row("Alejandro Kirk", "R", "+980", 46, "⭐", ["vs Bassitt"], """Worst Pickz Favorite. 0 HR, 87.5 mph EV. Bassitt RHB split -0.77, HR risk -0.45. tough split lane (-0.77); pitcher suppresses HR (-0.45).""", contact={'stars': 5, 'k': 15.2, 'batterK': 11.5, 'batterWhiff': 14.1, 'pitcherK': 17.7}),
            row("Brett Bateman", "L", "+1500", 42, "", ["vs Bassitt"], """0 HR, 89.5 mph EV. Bassitt LHB split +0.03, HR risk -0.45. pitcher suppresses HR (-0.45); weather carry headwind (-8%).""", contact={'stars': 4, 'k': 18.1, 'batterK': 19.8, 'batterWhiff': 18.1, 'pitcherK': 17.7}),
            row("Coby Mayo", "R", "+419", 86, "⭐ 🌕 💣", ["vs Scherzer"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.5 mph EV, 25.0% barrels. Scherzer RHB split +0.31, HR risk -0.05. pitcher risk below avg (-0.05); weather carry headwind (-8%).""", blast="high", contact={'stars': 3, 'k': 21.8, 'batterK': 25.3, 'batterWhiff': 28.8, 'pitcherK': 18.6}),
            row("Samuel Basallo", "L", "+410", 67, "", ["vs Scherzer"], """0 HR, 1 near-HR, 92.4 mph EV, 12.5% barrels. Scherzer LHB split -0.10, HR risk -0.05. slight split headwind (-0.10); pitcher risk below avg (-0.05).""", blast="good", contact={'stars': 3, 'k': 23.7, 'batterK': 30.0, 'batterWhiff': 34.2, 'pitcherK': 18.6}),
            row("Leody Taveras", "S", "+970", 65, "", ["vs Scherzer"], """1 HR, 2 near-HR, 93.4 mph EV, 12.5% barrels. Scherzer SHB→LHB split -0.10, HR risk -0.05. slight split headwind (-0.10); pitcher risk below avg (-0.05).""", blast="good", contact={'stars': 3, 'k': 21.6, 'batterK': 32.4, 'batterWhiff': 21.5, 'pitcherK': 18.6}),
            row("Pete Alonso", "R", "+310", 65, "", ["vs Scherzer"], """0 HR, 89.8 mph EV. Scherzer RHB split +0.31, HR risk -0.05. pitcher risk below avg (-0.05); weather carry headwind (-8%).""", contact={'stars': 3, 'k': 21.3, 'batterK': 23.3, 'batterWhiff': 28.4, 'pitcherK': 18.6}),
            row("Christian Encarnacion-Strand", "R", "+470", 60, "", ["vs Scherzer"], """0 HR, 91.9 mph EV. Scherzer RHB split +0.31, HR risk -0.05. pitcher risk below avg (-0.05); weather carry headwind (-8%).""", contact={'stars': 3, 'k': 23.2, 'batterK': 32.4, 'batterWhiff': 28.8, 'pitcherK': 18.6}),
        ],
    },
    {
        "title": "CIN @ MIL - Andrew Abbott (L, CIN) vs Dustin May (R, MIL)",
        "kLines": {'Abbott': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 22.7, 'matchupK': 18.0, 'ownK': 17.3}, 'May': {'k': 4.9, 'lo': 3, 'hi': 7, 'bf': 21.0, 'matchupK': 23.5, 'ownK': 21.8}},
        "description": "Tail key data: Park boost +3% (stadium -1%, weather +4%). Abbott (HR risk 0.18, vs LHB +0.70, vs RHB -0.16). May (HR risk -0.04, vs LHB -0.26, vs RHB +0.16).",
        "rows": [
            row("Jake Bauers", "L", "+370", 89, "⭐ 🌕 💣", ["vs Abbott"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.9 mph EV, 37.5% barrels. Abbott LHB split +0.70, HR risk 0.18.""", blast="high", contact={'stars': 3, 'k': 22.7, 'batterK': 29.1, 'batterWhiff': 33.6, 'pitcherK': 17.3}),
            row("Garrett Mitchell", "L", "+650", 81, "🚀", ["vs Abbott"], """1 HR, 1 near-HR, 100.5 mph EV, 12.5% barrels. Abbott LHB split +0.70, HR risk 0.18.""", blast="good", contact={'stars': 3, 'k': 23.0, 'batterK': 32.8, 'batterWhiff': 33.6, 'pitcherK': 17.3}),
            row("William Contreras", "R", "+520", 73, "⭐", ["vs Abbott"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.0 mph EV, 12.5% barrels. Abbott RHB split -0.16, HR risk 0.18. slight split headwind (-0.16).""", blast="good", contact={'stars': 4, 'k': 18.3, 'batterK': 19.4, 'batterWhiff': 21.1, 'pitcherK': 17.3}),
            row("Andrew Vaughn", "R", "+630", 61, "", ["vs Abbott"], """0 HR, 93.5 mph EV. Abbott RHB split -0.16, HR risk 0.18. slight split headwind (-0.16); limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 17.1, 'batterK': 17.7, 'batterWhiff': 14.9, 'pitcherK': 17.3}),
            row("Brice Turang", "L", "+1040", 56, "", ["vs Abbott"], """0 HR, 1 near-HR, 91.3 mph EV. Abbott LHB split +0.70, HR risk 0.18. limited recent HR events.""", contact={'stars': 4, 'k': 19.8, 'batterK': 24.4, 'batterWhiff': 22.1, 'pitcherK': 17.3}),
            row("Elly De La Cruz", "S", "+475", 91, "⭐ 🌕 💣", ["vs May"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 98.0 mph EV, 62.5% barrels. May SHB→LHB split -0.26, HR risk -0.04. slight split headwind (-0.26); pitcher risk below avg (-0.04).""", blast="high", contact={'stars': 3, 'k': 23.1, 'batterK': 25.8, 'batterWhiff': 25.0, 'pitcherK': 21.8}),
            row("Eugenio Suarez", "R", "+660", 86, "🌕 💣", ["vs May"], """2 HR, 3 near-HR, 91.0 mph EV, 37.5% barrels. May RHB split +0.16, HR risk -0.04. pitcher risk below avg (-0.04).""", blast="high", contact={'stars': 2, 'k': 24.8, 'batterK': 28.7, 'batterWhiff': 31.3, 'pitcherK': 21.8}),
            row("JJ Bleday", "L", "+549", 77, "", ["vs May"], """1 HR, 1 near-HR, 92.6 mph EV, 37.5% barrels. May LHB split -0.26, HR risk -0.04. slight split headwind (-0.26); pitcher risk below avg (-0.04).""", blast="good", contact={'stars': 2, 'k': 24.1, 'batterK': 26.5, 'batterWhiff': 30.2, 'pitcherK': 21.8}),
            row("Tyler Stephenson", "R", "+790", 66, "", ["vs May"], """0 HR, 91.9 mph EV, 12.5% barrels. May RHB split +0.16, HR risk -0.04. pitcher risk below avg (-0.04); limited recent HR events.""", contact={'stars': 2, 'k': 26.9, 'batterK': 35.4, 'batterWhiff': 32.9, 'pitcherK': 21.8}),
            row("Sal Stewart", "R", "+470", 76, "", ["vs May"], """0 HR, 2 near-HR, 94.8 mph EV. May RHB split +0.16, HR risk -0.04. pitcher risk below avg (-0.04).""", blast="good", contact={'stars': 3, 'k': 20.8, 'batterK': 17.0, 'batterWhiff': 26.4, 'pitcherK': 21.8}),
            row("Ke'Bryan Hayes", "R", "+1200", 67, "", ["vs May"], """0 HR, 96.2 mph EV. May RHB split +0.16, HR risk -0.04. pitcher risk below avg (-0.04); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.0, 'batterK': 22.9, 'batterWhiff': 29.4, 'pitcherK': 21.8}),
        ],
    },
    {
        "title": "CLE @ MIN - Parker Messick (L, CLE) vs Taj Bradley (R, MIN)",
        "kLines": {'Messick': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 23.3, 'matchupK': 22.8, 'ownK': 26.7}, 'Bradley': {'k': 5.4, 'lo': 4, 'hi': 7, 'bf': 23.7, 'matchupK': 22.9, 'ownK': 27.0}},
        "description": "Tail key data: Park boost +0% (stadium -7%, weather +7%). Messick (HR risk -0.74, vs LHB +0.03, vs RHB -0.88). Bradley (HR risk 0.49, vs LHB +0.97, vs RHB -0.32).",
        "rows": [
            row("Kody Clemens", "L", "+555", 54, "", ["vs Messick"], """0 HR, 85.2 mph EV. Messick LHB split +0.03, HR risk -0.74. pitcher suppresses HR (-0.74); park suppresses carry (-7%).""", contact={'stars': 3, 'k': 23.4, 'batterK': 19.8, 'batterWhiff': 21.7, 'pitcherK': 26.7}),
            row("Josh Bell", "S", "+725", 46, "", ["vs Messick"], """0 HR, 91.9 mph EV. Messick SHB→RHB split -0.88, HR risk -0.74. tough split lane (-0.88); pitcher suppresses HR (-0.74).""", contact={'stars': 3, 'k': 20.7, 'batterK': 13.1, 'batterWhiff': 18.1, 'pitcherK': 26.7}),
            row("Brooks Lee", "S", "+820", 47, "", ["vs Messick"], """0 HR, 92.9 mph EV. Messick SHB→RHB split -0.88, HR risk -0.74. tough split lane (-0.88); pitcher suppresses HR (-0.74).""", blast="good", contact={'stars': 3, 'k': 20.3, 'batterK': 12.2, 'batterWhiff': 17.2, 'pitcherK': 26.7}),
            row("Royce Lewis", "R", "+650", 44, "", ["vs Messick"], """0 HR, 89.5 mph EV. Messick RHB split -0.88, HR risk -0.74. tough split lane (-0.88); pitcher suppresses HR (-0.74).""", contact={'stars': 2, 'k': 24.5, 'batterK': 20.3, 'batterWhiff': 26.3, 'pitcherK': 26.7}),
            row("Chase DeLauter", "L", "+525", 91, "⭐ 🌕 💣", ["vs Bradley"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 97.6 mph EV, 25.0% barrels. Bradley LHB split +0.97, HR risk 0.49. park suppresses carry (-7%).""", blast="high", contact={'stars': 3, 'k': 20.6, 'batterK': 16.0, 'batterWhiff': 12.6, 'pitcherK': 27.0}),
            row("Travis Bazzana", "L", "+820", 87, "⭐ 🌕 💣", ["vs Bradley"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.8 mph EV, 25.0% barrels. Bradley LHB split +0.97, HR risk 0.49. park suppresses carry (-7%).""", blast="high", contact={'stars': 3, 'k': 21.7, 'batterK': 13.2, 'batterWhiff': 21.1, 'pitcherK': 27.0}),
            row("Nathaniel Lowe", "L", "+590", 80, "", ["vs Bradley"], """1 HR, 1 near-HR, 90.4 mph EV, 12.5% barrels. Bradley LHB split +0.97, HR risk 0.49. park suppresses carry (-7%).""", blast="good", contact={'stars': 2, 'k': 24.1, 'batterK': 22.5, 'batterWhiff': 21.1, 'pitcherK': 27.0}),
        ],
    },
    {
        "title": "COL @ DET - Mason Adams 🧤 (R, COL) vs Framber Valdez (L, DET)",
        "kLines": {'Adams': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 21.0, 'matchupK': 24.7, 'ownK': 28.8}, 'Valdez': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 24.1, 'matchupK': 18.3, 'ownK': 16.7}},
        "description": "Tail key data: Park boost -19% (stadium -11%, weather -8%). Adams 🧤 (HR risk 2.26, vs LHB +0.28, vs RHB +3.22). Valdez (HR risk -0.47, vs LHB -0.44, vs RHB -0.37).",
        "rows": [
            row("Dillon Dingler", "R", "+525", 78, "", ["vs Adams"], """0 HR, 90.7 mph EV, 12.5% barrels. Adams RHB split +3.22, HR risk 2.26. park/weather net drag (-19%); limited recent HR events.""", contact={'stars': 2, 'k': 24.7, 'batterK': 26.6, 'batterWhiff': 24.5, 'pitcherK': 28.8}),
            row("Gleyber Torres", "R", "+990", 84, "", ["vs Adams"], """0 HR, 96.9 mph EV. Adams RHB split +3.22, HR risk 2.26. park/weather net drag (-19%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.0, 'batterK': 19.0, 'batterWhiff': 21.3, 'pitcherK': 28.8}),
            row("Colt Keith", "L", "+725", 82, "", ["vs Adams"], """0 HR, 95.3 mph EV, 12.5% barrels. Adams LHB split +0.28, HR risk 2.26. park/weather net drag (-19%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.8, 'batterK': 27.3, 'batterWhiff': 31.6, 'pitcherK': 28.8}),
            row("Troy Johnston", "L", "+1350", 44, "", ["vs Valdez"], """0 HR, 93.0 mph EV. Valdez LHB split -0.44, HR risk -0.47. tough split lane (-0.44); pitcher suppresses HR (-0.47).""", blast="good", contact={'stars': 4, 'k': 19.4, 'batterK': 21.5, 'batterWhiff': 26.8, 'pitcherK': 16.7}),
            row("Adael Amador", "S", "+1000", 51, "💎", ["vs Valdez"], """Worst Pickz Hidden Gem. 0 HR, 99.5 mph EV. Valdez SHB→RHB split -0.37, HR risk -0.47. slight split headwind (-0.37); pitcher suppresses HR (-0.47).""", blast="good", contact={'stars': 5, 'k': 17.1, 'batterK': 17.1, 'batterWhiff': 15.2, 'pitcherK': 16.7}),
        ],
    },
    {
        "title": "CWS @ STL - Anthony Kay (L, CWS) vs Matthew Liberatore (L, STL)",
        "kLines": {'Kay': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 22.1, 'matchupK': 20.4, 'ownK': 19.6}, 'Liberatore': {'k': 5.9, 'lo': 4, 'hi': 8, 'bf': 21.7, 'matchupK': 27.3, 'ownK': 28.4}},
        "description": "Tail key data: Park boost -4% (stadium -11%, weather +7%). Kay (HR risk 0.17, vs LHB -1.20, vs RHB +0.49). Liberatore (HR risk 0.56, vs LHB -0.06, vs RHB +0.72).",
        "rows": [
            row("Leonardo Bernal", "S", "+870", 66, "💎", ["vs Kay"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 99.3 mph EV. Kay SHB→RHB split +0.49, HR risk 0.17. park suppresses carry (-11%); limited recent HR events.""", blast="good"),
            row("Thomas Saggese", "R", "+920", 82, "🌕 💣", ["vs Kay"], """2 HR, 2 near-HR, 90.8 mph EV, 25.0% barrels. Kay RHB split +0.49, HR risk 0.17. park suppresses carry (-11%).""", blast="high", contact={'stars': 3, 'k': 20.5, 'batterK': 20.0, 'batterWhiff': 25.2, 'pitcherK': 19.6}),
            row("Jordan Walker", "R", "+450", 83, "", ["vs Kay"], """1 HR, 1 near-HR, 91.6 mph EV, 25.0% barrels. Kay RHB split +0.49, HR risk 0.17. park suppresses carry (-11%).""", blast="good", contact={'stars': 2, 'k': 26.1, 'batterK': 33.7, 'batterWhiff': 37.6, 'pitcherK': 19.6}),
            row("Masyn Winn", "R", "+1150", 61, "", ["vs Kay"], """1 HR, 1 near-HR, 89.7 mph EV, 12.5% barrels. Kay RHB split +0.49, HR risk 0.17. park suppresses carry (-11%).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 30.1, 'batterWhiff': 28.3, 'pitcherK': 19.6}),
            row("Ivan Herrera", "R", "+790", 62, "", ["vs Kay"], """0 HR, 92.2 mph EV. Kay RHB split +0.49, HR risk 0.17. park suppresses carry (-11%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.7, 'batterK': 21.5, 'batterWhiff': 19.4, 'pitcherK': 19.6}),
            row("Colson Montgomery", "L", "+520", 88, "🌕 💣", ["vs Liberatore"], """2 HR, 2 near-HR, 91.5 mph EV, 37.5% barrels. Liberatore LHB split -0.06, HR risk 0.56. slight split headwind (-0.06); park suppresses carry (-11%).""", blast="high", contact={'stars': 1, 'k': 35.1, 'batterK': 45.8, 'batterWhiff': 39.8, 'pitcherK': 28.4}),
            row("Randal Grichuk", "R", "+475", 89, "🌕 💣", ["vs Liberatore"], """1 HR, 1 near-HR, 96.6 mph EV, 25.0% barrels. Liberatore RHB split +0.72, HR risk 0.56. park suppresses carry (-11%).""", blast="good", contact={'stars': 2, 'k': 24.7, 'batterK': 24.4, 'batterWhiff': 20.9, 'pitcherK': 28.4}),
            row("Miguel Vargas", "R", "+475", 86, "", ["vs Liberatore"], """1 HR, 2 near-HR, 91.7 mph EV, 25.0% barrels. Liberatore RHB split +0.72, HR risk 0.56. park suppresses carry (-11%).""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 19.5, 'batterWhiff': 18.9, 'pitcherK': 28.4}),
            row("Jake Rogers", "R", "+730", 81, "💎", ["vs Liberatore"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.9 mph EV, 25.0% barrels. Liberatore RHB split +0.72, HR risk 0.56. park suppresses carry (-11%).""", blast="good", contact={'stars': 2, 'k': 26.6, 'batterK': 32.1, 'batterWhiff': 24.0, 'pitcherK': 28.4}),
        ],
    },
    {
        "title": "HOU @ TB - Miguel Ullola 🧤 (R, HOU) vs Drew Rasmussen (R, TB)",
        "kLines": {'Ullola': {'k': 5.1, 'lo': 3, 'hi': 7, 'bf': 21.7, 'matchupK': 23.4, 'ownK': 37.0}, 'Rasmussen': {'k': 5.7, 'lo': 4, 'hi': 7, 'bf': 22.1, 'matchupK': 25.7, 'ownK': 27.3}},
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +0%). Ullola 🧤 (HR risk 1.84, vs LHB +1.73, vs RHB +1.12). Rasmussen (HR risk -0.65, vs LHB -0.26, vs RHB -0.71).",
        "rows": [
            row("Junior Caminero", "R", "+270", 98, "⭐ 🌕 💣", ["vs Ullola"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 99.4 mph EV, 37.5% barrels. Ullola RHB split +1.12, HR risk 1.84.""", blast="high", contact={'stars': 3, 'k': 21.6, 'batterK': 15.9, 'batterWhiff': 22.2, 'pitcherK': 37.0}),
            row("Victor Mesa Jr.", "L", "+454", 90, "🌕 💣 💎", ["vs Ullola"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 88.3 mph EV, 12.5% barrels. Ullola LHB split +1.73, HR risk 1.84.""", blast="good", contact={'stars': 3, 'k': 21.5, 'batterK': 9.9, 'batterWhiff': 25.6, 'pitcherK': 37.0}),
            row("Yandy Diaz", "R", "+590", 86, "", ["vs Ullola"], """0 HR, 1 near-HR, 91.6 mph EV, 12.5% barrels. Ullola RHB split +1.12, HR risk 1.84. limited recent HR events.""", contact={'stars': 4, 'k': 19.5, 'batterK': 14.3, 'batterWhiff': 14.2, 'pitcherK': 37.0}),
            row("Nick Allen", "R", "N/A", 53, "", ["vs Rasmussen"], """1 HR, 1 near-HR, 93.0 mph EV, 12.5% barrels. Rasmussen RHB split -0.71, HR risk -0.65. tough split lane (-0.71); pitcher suppresses HR (-0.65).""", blast="good", contact={'stars': 3, 'k': 22.8, 'batterK': 19.4, 'batterWhiff': 14.5, 'pitcherK': 27.3}),
            row("Nelson Velazquez", "R", "N/A", 64, "", ["vs Rasmussen"], """0 HR, 1 near-HR, 97.4 mph EV, 12.5% barrels. Rasmussen RHB split -0.71, HR risk -0.65. tough split lane (-0.71); pitcher suppresses HR (-0.65).""", blast="good", contact={'stars': 1, 'k': 31.4, 'batterK': 43.2, 'batterWhiff': 48.5, 'pitcherK': 27.3}),
            row("Cam Smith", "R", "+670", 47, "", ["vs Rasmussen"], """0 HR, 89.6 mph EV. Rasmussen RHB split -0.71, HR risk -0.65. tough split lane (-0.71); pitcher suppresses HR (-0.65).""", contact={'stars': 1, 'k': 27.9, 'batterK': 31.3, 'batterWhiff': 30.4, 'pitcherK': 27.3}),
            row("Yainer Diaz", "R", "+820", 62, "💎", ["vs Rasmussen"], """Worst Pickz Hidden Gem. 0 HR, 95.4 mph EV. Rasmussen RHB split -0.71, HR risk -0.65. tough split lane (-0.71); pitcher suppresses HR (-0.65).""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 19.0, 'batterWhiff': 21.4, 'pitcherK': 27.3}),
            row("Isaac Paredes", "R", "+640", 50, "⭐", ["vs Rasmussen"], """Worst Pickz Favorite. 0 HR, 93.1 mph EV. Rasmussen RHB split -0.71, HR risk -0.65. tough split lane (-0.71); pitcher suppresses HR (-0.65).""", blast="good", contact={'stars': 4, 'k': 19.4, 'batterK': 11.6, 'batterWhiff': 13.3, 'pitcherK': 27.3}),
        ],
    },
    {
        "title": "KC @ BOS - Seth Lugo (R, KC) vs Sonny Gray (R, BOS)",
        "kLines": {'Lugo': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 23.3, 'matchupK': 16.1, 'ownK': 14.0}, 'Gray': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 23.2, 'matchupK': 19.2, 'ownK': 21.0}},
        "description": "Tail key data: Park boost -8% (stadium -9%, weather +1%). Lugo (HR risk -0.37, vs LHB +0.08, vs RHB -0.55). Gray (HR risk -0.53, vs LHB -0.43, vs RHB -0.34).",
        "rows": [
            row("Roman Anthony", "L", "+550", 77, "💎", ["vs Lugo"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 94.1 mph EV, 25.0% barrels. Lugo LHB split +0.08, HR risk -0.37. pitcher risk below avg (-0.37); park/weather net drag (-8%).""", blast="good", contact={'stars': 3, 'k': 20.0, 'batterK': 28.9, 'batterWhiff': 28.2, 'pitcherK': 14.0}),
            row("Jarren Duran", "L", "+550", 68, "", ["vs Lugo"], """1 HR, 1 near-HR, 90.5 mph EV, 12.5% barrels. Lugo LHB split +0.08, HR risk -0.37. pitcher risk below avg (-0.37); park/weather net drag (-8%).""", blast="good", contact={'stars': 4, 'k': 18.6, 'batterK': 20.3, 'batterWhiff': 31.5, 'pitcherK': 14.0}),
            row("Mickey Gasper", "S", "+575", 73, "", ["vs Lugo"], """1 HR, 1 near-HR, 89.9 mph EV, 12.5% barrels. Lugo SHB→LHB split +0.08, HR risk -0.37. pitcher risk below avg (-0.37); park/weather net drag (-8%).""", blast="good", contact={'stars': 5, 'k': 14.0, 'batterK': 10.5, 'batterWhiff': 15.7, 'pitcherK': 14.0}),
            row("Adley Rutschman", "S", "+640", 72, "🌕 💣", ["vs Lugo"], """2 HR, 2 near-HR, 89.0 mph EV, 25.0% barrels. Lugo SHB→LHB split +0.08, HR risk -0.37. pitcher risk below avg (-0.37); park/weather net drag (-8%).""", blast="high", contact={'stars': 4, 'k': 17.5, 'batterK': 25.0, 'batterWhiff': 18.9, 'pitcherK': 14.0}),
            row("Bobby Witt Jr.", "R", "+500", 84, "🌕 💣", ["vs Gray"], """2 HR, 2 near-HR, 98.9 mph EV, 25.0% barrels. Gray RHB split -0.34, HR risk -0.53. slight split headwind (-0.34); pitcher suppresses HR (-0.53).""", blast="high", contact={'stars': 4, 'k': 18.8, 'batterK': 13.2, 'batterWhiff': 25.0, 'pitcherK': 21.0}),
            row("Salvador Perez", "R", "+550", 72, "🌕 💣", ["vs Gray"], """1 HR, 1 near-HR, 97.9 mph EV, 25.0% barrels. Gray RHB split -0.34, HR risk -0.53. slight split headwind (-0.34); pitcher suppresses HR (-0.53).""", blast="high", contact={'stars': 4, 'k': 19.3, 'batterK': 15.1, 'batterWhiff': 23.6, 'pitcherK': 21.0}),
            row("Vinnie Pasquantino", "L", "+640", 69, "", ["vs Gray"], """1 HR, 2 near-HR, 93.2 mph EV, 25.0% barrels. Gray LHB split -0.43, HR risk -0.53. tough split lane (-0.43); pitcher suppresses HR (-0.53).""", blast="good", contact={'stars': 5, 'k': 15.1, 'batterK': 6.8, 'batterWhiff': 13.3, 'pitcherK': 21.0}),
            row("Michael Massey", "L", "+780", 46, "", ["vs Gray"], """0 HR, 91.4 mph EV. Gray LHB split -0.43, HR risk -0.53. tough split lane (-0.43); pitcher suppresses HR (-0.53).""", contact={'stars': 4, 'k': 19.6, 'batterK': 16.0, 'batterWhiff': 22.3, 'pitcherK': 21.0}),
        ],
    },
    {
        "title": "LAA @ WSH - Yusei Kikuchi (L, LAA) vs Cade Cavalli (R, WSH)",
        "kLines": {'Kikuchi': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 21.6, 'matchupK': 23.1, 'ownK': 22.7}, 'Cavalli': {'k': 6.8, 'lo': 5, 'hi': 8, 'bf': 22.0, 'matchupK': 31.1, 'ownK': 32.6}},
        "description": "Tail key data: Park boost +13% (stadium +5%, weather +8%). Kikuchi (HR risk 0.46, vs LHB -0.53, vs RHB +0.56). Cavalli (HR risk -0.44, vs LHB -0.32, vs RHB -0.26).",
        "rows": [
            row("Yohandy Morales", "R", "+710", 83, "", ["vs Kikuchi"], """0 HR, 1 near-HR, 96.4 mph EV, 25.0% barrels. Kikuchi RHB split +0.56, HR risk 0.46. limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.9, 'batterK': 42.1, 'batterWhiff': 47.4, 'pitcherK': 22.7}),
            row("James Wood", "L", "+420", 81, "", ["vs Kikuchi"], """0 HR, 93.3 mph EV, 12.5% barrels. Kikuchi LHB split -0.53, HR risk 0.46. tough split lane (-0.53); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.2, 'batterK': 22.8, 'batterWhiff': 22.6, 'pitcherK': 22.7}),
            row("Andres Chaparro", "R", "+495", 77, "💎", ["vs Kikuchi"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.2 mph EV. Kikuchi RHB split +0.56, HR risk 0.46.""", blast="good", contact={'stars': 2, 'k': 24.6, 'batterK': 23.9, 'batterWhiff': 33.6, 'pitcherK': 22.7}),
            row("Dylan Crews", "R", "+520", 83, "", ["vs Kikuchi"], """1 HR, 1 near-HR, 92.4 mph EV, 12.5% barrels. Kikuchi RHB split +0.56, HR risk 0.46.""", blast="good", contact={'stars': 2, 'k': 25.0, 'batterK': 28.4, 'batterWhiff': 29.8, 'pitcherK': 22.7}),
            row("Harry Ford", "R", "+900", 63, "", ["vs Kikuchi"], """0 HR, 83.5 mph EV, 12.5% barrels. Kikuchi RHB split +0.56, HR risk 0.46. limited recent HR events; lighter EV form (83.5 mph).""", contact={'stars': 3, 'k': 22.8, 'batterK': 23.5, 'batterWhiff': 25.4, 'pitcherK': 22.7}),
            row("Moises Ballesteros", "L", "+800", 83, "🌕 💣 💎", ["vs Cavalli"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.9 mph EV, 25.0% barrels. Cavalli LHB split -0.32, HR risk -0.44. slight split headwind (-0.32); pitcher suppresses HR (-0.44).""", blast="high", contact={'stars': 1, 'k': 31.7, 'batterK': 29.6, 'batterWhiff': 32.1, 'pitcherK': 32.6}),
            row("Zach Neto", "R", "+570", 61, "", ["vs Cavalli"], """0 HR, 1 near-HR, 91.7 mph EV. Cavalli RHB split -0.26, HR risk -0.44. slight split headwind (-0.26); pitcher suppresses HR (-0.44).""", contact={'stars': 1, 'k': 28.4, 'batterK': 23.3, 'batterWhiff': 25.3, 'pitcherK': 32.6}),
        ],
    },
    {
        "title": "LAD @ MIA - Blake Snell (L, LAD) vs Ryan Gusto (R, MIA)",
        "kLines": {'Snell': {'k': 6.1, 'lo': 4, 'hi': 8, 'bf': 21.9, 'matchupK': 27.9, 'ownK': 32.6}, 'Gusto': {'k': 3.9, 'lo': 2, 'hi': 5, 'bf': 19.8, 'matchupK': 19.6, 'ownK': 19.5}},
        "description": "Tail key data: Park boost -13% (stadium -13%, weather +0%). Snell (BAA vs LHB .206, vs RHB .171). Gusto (HR risk 0.02, vs LHB +0.11, vs RHB -0.03).",
        "rows": [
            row("Heriberto Hernandez", "R", "+680", 83, "🚀 ⭐ 🌕 💣", ["vs Snell"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 100.1 mph EV, 37.5% barrels. limited split/risk sample; park/weather net drag (-13%).""", blast="high", contact={'stars': 1, 'k': 27.6, 'batterK': 22.5, 'batterWhiff': 30.7, 'pitcherK': 32.6}),
            row("Kyle Stowers", "L", "+870", 82, "🌕 💣", ["vs Snell"], """1 HR, 2 near-HR, 98.1 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-13%).""", blast="high", contact={'stars': 1, 'k': 33.2, 'batterK': 35.8, 'batterWhiff': 39.4, 'pitcherK': 32.6}),
            row("Griffin Conine", "L", "+940", 70, "", ["vs Snell"], """1 HR, 1 near-HR, 94.2 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-13%).""", blast="good", contact={'stars': 1, 'k': 29.5, 'batterK': 26.9, 'batterWhiff': 33.8, 'pitcherK': 32.6}),
            row("Jared Serna", "R", "+1450", 66, "", ["vs Snell"], """0 HR, 96.5 mph EV. limited split/risk sample; park/weather net drag (-13%).""", blast="good", contact={'stars': 2, 'k': 25.4, 'batterK': 10.0, 'batterWhiff': 15.8, 'pitcherK': 32.6}),
            row("Kyle Tucker", "L", "+710", 65, "", ["vs Gusto"], """1 HR, 1 near-HR, 93.1 mph EV, 25.0% barrels. Gusto LHB split +0.11, HR risk 0.02. park/weather net drag (-13%).""", blast="good", contact={'stars': 4, 'k': 17.6, 'batterK': 12.7, 'batterWhiff': 19.0, 'pitcherK': 19.5}),
            row("Will Smith", "R", "+675", 71, "⭐", ["vs Gusto"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 94.9 mph EV, 12.5% barrels. Gusto RHB split -0.03, HR risk 0.02. slight split headwind (-0.03); park/weather net drag (-13%).""", blast="good", contact={'stars': 5, 'k': 16.9, 'batterK': 13.7, 'batterWhiff': 13.5, 'pitcherK': 19.5}),
            row("Mookie Betts", "R", "+790", 74, "⭐ 🌕 💣", ["vs Gusto"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.0 mph EV, 25.0% barrels. Gusto RHB split -0.03, HR risk 0.02. slight split headwind (-0.03); park/weather net drag (-13%).""", blast="high", contact={'stars': 5, 'k': 14.5, 'batterK': 8.5, 'batterWhiff': 11.1, 'pitcherK': 19.5}),
            row("Teoscar Hernandez", "R", "+680", 61, "", ["vs Gusto"], """0 HR, 94.9 mph EV. Gusto RHB split -0.03, HR risk 0.02. slight split headwind (-0.03); park/weather net drag (-13%).""", blast="good", contact={'stars': 3, 'k': 24.0, 'batterK': 27.4, 'batterWhiff': 34.8, 'pitcherK': 19.5}),
        ],
    },
    {
        "title": "NYM @ NYY - Nolan McLean (R, NYM) vs Carlos Rodon (L, NYY)",
        "kLines": {'McLean': {'k': 5.8, 'lo': 4, 'hi': 7, 'bf': 23.6, 'matchupK': 24.8, 'ownK': 24.5}, 'Rodon': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 20.9, 'matchupK': 25.3, 'ownK': 25.5}},
        "description": "Tail key data: Park boost +1% (stadium +3%, weather -1%). McLean (HR risk -0.96, vs LHB -0.56, vs RHB -1.01). Rodon (HR risk -0.31, vs LHB +0.20, vs RHB -0.32).",
        "rows": [
            row("Spencer Jones", "L", "+495", 82, "🚀 ⭐ 🌕 💣", ["vs McLean"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 104.2 mph EV, 50.0% barrels. McLean LHB split -0.56, HR risk -0.96. tough split lane (-0.56); pitcher suppresses HR (-0.96).""", blast="high", contact={'stars': 2, 'k': 27.1, 'batterK': 30.6, 'batterWhiff': 33.7, 'pitcherK': 24.5}),
            row("Luis Garcia Jr.", "L", "+384", 72, "", ["vs McLean"], """1 HR, 2 near-HR, 90.7 mph EV, 25.0% barrels. McLean LHB split -0.56, HR risk -0.96. tough split lane (-0.56); pitcher suppresses HR (-0.96).""", blast="good", contact={'stars': 3, 'k': 23.7, 'batterK': 21.3, 'batterWhiff': 27.2, 'pitcherK': 24.5}),
            row("Austin Wells", "L", "+544", 60, "", ["vs McLean"], """0 HR, 1 near-HR, 97.6 mph EV, 12.5% barrels. McLean LHB split -0.56, HR risk -0.96. tough split lane (-0.56); pitcher suppresses HR (-0.96).""", blast="good", contact={'stars': 2, 'k': 25.7, 'batterK': 32.8, 'batterWhiff': 26.2, 'pitcherK': 24.5}),
            row("Cody Bellinger", "L", "+520", 58, "⭐", ["vs McLean"], """Worst Pickz Favorite. 0 HR, 94.4 mph EV, 12.5% barrels. McLean LHB split -0.56, HR risk -0.96. tough split lane (-0.56); pitcher suppresses HR (-0.96).""", blast="good", contact={'stars': 3, 'k': 21.1, 'batterK': 17.0, 'batterWhiff': 20.7, 'pitcherK': 24.5}),
            row("Aaron Judge", "R", "+270", 70, "", ["vs McLean"], """0 HR, 1 near-HR, 95.3 mph EV, 12.5% barrels. McLean RHB split -1.01, HR risk -0.96. tough split lane (-1.01); pitcher suppresses HR (-0.96).""", blast="good", contact={'stars': 2, 'k': 25.1, 'batterK': 25.3, 'batterWhiff': 28.7, 'pitcherK': 24.5}),
            row("Ben Rice", "L", "+310", 69, "", ["vs McLean"], """0 HR, 93.9 mph EV, 12.5% barrels. McLean LHB split -0.56, HR risk -0.96. tough split lane (-0.56); pitcher suppresses HR (-0.96).""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 22.0, 'batterWhiff': 24.5, 'pitcherK': 24.5}),
            row("Mark Vientos", "R", "+495", 88, "🌕 💣", ["vs Rodon"], """3 HR, 3 near-HR, 94.9 mph EV, 37.5% barrels. Rodon RHB split -0.32, HR risk -0.31. slight split headwind (-0.32); pitcher risk below avg (-0.31).""", blast="high", contact={'stars': 2, 'k': 26.8, 'batterK': 27.6, 'batterWhiff': 34.5, 'pitcherK': 25.5}),
            row("Francisco Alvarez", "R", "+525", 79, "", ["vs Rodon"], """1 HR, 1 near-HR, 96.9 mph EV, 12.5% barrels. Rodon RHB split -0.32, HR risk -0.31. slight split headwind (-0.32); pitcher risk below avg (-0.31).""", blast="good", contact={'stars': 1, 'k': 33.6, 'batterK': 48.6, 'batterWhiff': 43.4, 'pitcherK': 25.5}),
            row("Bo Bichette", "R", "+587", 66, "", ["vs Rodon"], """0 HR, 1 near-HR, 91.8 mph EV, 12.5% barrels. Rodon RHB split -0.32, HR risk -0.31. slight split headwind (-0.32); pitcher risk below avg (-0.31).""", contact={'stars': 3, 'k': 21.5, 'batterK': 17.4, 'batterWhiff': 19.9, 'pitcherK': 25.5}),
            row("Francisco Lindor", "S", "+399", 50, "💎", ["vs Rodon"], """Worst Pickz Hidden Gem. 0 HR, 87.6 mph EV. Rodon SHB→RHB split -0.32, HR risk -0.31. slight split headwind (-0.32); pitcher risk below avg (-0.31).""", contact={'stars': 2, 'k': 24.2, 'batterK': 22.8, 'batterWhiff': 25.4, 'pitcherK': 25.5}),
        ],
    },
    {
        "title": "PHI @ ATL - Aaron Nola (R, PHI) vs Chris Sale (L, ATL)",
        "kLines": {'Nola': {'k': 5.6, 'lo': 4, 'hi': 7, 'bf': 22.7, 'matchupK': 24.7, 'ownK': 25.2}, 'Sale': {'k': 6.8, 'lo': 5, 'hi': 8, 'bf': 23.6, 'matchupK': 28.9, 'ownK': 32.2}},
        "description": "Tail key data: Park boost -4% (stadium -3%, weather -1%). Nola (HR risk -0.05, vs LHB +0.06, vs RHB -0.12). Sale (HR risk -0.95, vs LHB -1.00, vs RHB -0.60).",
        "rows": [
            row("Matt Olson", "L", "+350", 71, "🚀 💎", ["vs Nola"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 100.6 mph EV, 12.5% barrels. Nola LHB split +0.06, HR risk -0.05. pitcher risk below avg (-0.05); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 26.3, 'batterK': 26.8, 'batterWhiff': 31.3, 'pitcherK': 25.2}),
            row("Ozzie Albies", "S", "+710", 53, "", ["vs Nola"], """0 HR, 95.3 mph EV. Nola SHB→LHB split +0.06, HR risk -0.05. pitcher risk below avg (-0.05); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.8, 'batterK': 18.8, 'batterWhiff': 19.5, 'pitcherK': 25.2}),
            row("Austin Riley", "R", "+575", 64, "", ["vs Nola"], """1 HR, 1 near-HR, 90.4 mph EV, 25.0% barrels. Nola RHB split -0.12, HR risk -0.05. slight split headwind (-0.12); pitcher risk below avg (-0.05).""", blast="good", contact={'stars': 2, 'k': 27.0, 'batterK': 34.2, 'batterWhiff': 27.1, 'pitcherK': 25.2}),
            row("Sean Murphy", "R", "+650", 67, "", ["vs Nola"], """1 HR, 1 near-HR, 94.7 mph EV, 12.5% barrels. Nola RHB split -0.12, HR risk -0.05. slight split headwind (-0.12); pitcher risk below avg (-0.05).""", blast="good", contact={'stars': 1, 'k': 27.6, 'batterK': 32.4, 'batterWhiff': 31.6, 'pitcherK': 25.2}),
            row("Drake Baldwin", "L", "+505", 75, "", ["vs Nola"], """1 HR, 1 near-HR, 87.3 mph EV, 25.0% barrels. Nola LHB split +0.06, HR risk -0.05. pitcher risk below avg (-0.05); lighter EV form (87.3 mph).""", blast="good", contact={'stars': 2, 'k': 27.0, 'batterK': 27.9, 'batterWhiff': 32.8, 'pitcherK': 25.2}),
            row("Kyle Schwarber", "L", "+400", 76, "⭐ 🌕 💣", ["vs Sale"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.4 mph EV, 25.0% barrels. Sale LHB split -1.00, HR risk -0.95. tough split lane (-1.00); pitcher suppresses HR (-0.95).""", blast="high", contact={'stars': 1, 'k': 29.2, 'batterK': 23.1, 'batterWhiff': 30.9, 'pitcherK': 32.2}),
            row("Alec Bohm", "R", "+820", 65, "", ["vs Sale"], """1 HR, 2 near-HR, 94.9 mph EV, 37.5% barrels. Sale RHB split -0.60, HR risk -0.95. tough split lane (-0.60); pitcher suppresses HR (-0.95).""", blast="good", contact={'stars': 2, 'k': 25.6, 'batterK': 17.9, 'batterWhiff': 20.8, 'pitcherK': 32.2}),
            row("Trea Turner", "R", "+775", 59, "💎", ["vs Sale"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 90.2 mph EV, 25.0% barrels. Sale RHB split -0.60, HR risk -0.95. tough split lane (-0.60); pitcher suppresses HR (-0.95).""", blast="good", contact={'stars': 1, 'k': 28.4, 'batterK': 20.2, 'batterWhiff': 31.7, 'pitcherK': 32.2}),
        ],
    },
    {
        "title": "SD @ SF - Robbie Ray (L, SD) vs Anthony Molina (R, SF)",
        "kLines": {'Ray': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 22.6, 'matchupK': 19.3, 'ownK': 18.8}, 'Molina': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 21.1, 'matchupK': 21.4, 'ownK': 20.3}},
        "description": "Tail key data: Park boost -21% (stadium -16%, weather -5%). Ray (HR risk 0.11, vs LHB -1.02, vs RHB +0.54). Molina (HR risk 0.47, vs LHB +0.71, vs RHB +0.30).",
        "rows": [
            row("Bryce Eldridge", "L", "+600", 86, "🚀 ⭐ 🌕 💣", ["vs Ray"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.8 mph EV, 25.0% barrels. Ray LHB split -1.02, HR risk 0.11. tough split lane (-1.02); park/weather net drag (-21%).""", blast="high", contact={'stars': 3, 'k': 22.1, 'batterK': 27.0, 'batterWhiff': 27.0, 'pitcherK': 18.8}),
            row("Rafael Devers", "L", "+520", 67, "", ["vs Ray"], """1 HR, 1 near-HR, 94.8 mph EV, 12.5% barrels. Ray LHB split -1.02, HR risk 0.11. tough split lane (-1.02); park/weather net drag (-21%).""", blast="good", contact={'stars': 3, 'k': 20.2, 'batterK': 19.8, 'batterWhiff': 27.9, 'pitcherK': 18.8}),
            row("Turner Hill", "L", "+1900", 44, "", ["vs Ray"], """0 HR, 93.7 mph EV. Ray LHB split -1.02, HR risk 0.11. tough split lane (-1.02); park/weather net drag (-21%).""", blast="good", contact={'stars': 5, 'k': 16.0, 'batterK': 13.5, 'batterWhiff': 10.8, 'pitcherK': 18.8}),
            row("Manny Machado", "R", "+529", 85, "🌕 💣 💎", ["vs Molina"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.1 mph EV, 37.5% barrels. Molina RHB split +0.30, HR risk 0.47. park/weather net drag (-21%).""", blast="high", contact={'stars': 3, 'k': 20.5, 'batterK': 19.3, 'batterWhiff': 23.4, 'pitcherK': 20.3}),
            row("Jackson Merrill", "L", "+660", 86, "🚀 ⭐", ["vs Molina"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 105.8 mph EV, 12.5% barrels. Molina LHB split +0.71, HR risk 0.47. park/weather net drag (-21%).""", blast="good", contact={'stars': 3, 'k': 22.8, 'batterK': 23.5, 'batterWhiff': 29.7, 'pitcherK': 20.3}),
            row("Fernando Tatis Jr.", "R", "+525", 83, "💎", ["vs Molina"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.8 mph EV, 12.5% barrels. Molina RHB split +0.30, HR risk 0.47. park/weather net drag (-21%).""", blast="good", contact={'stars': 4, 'k': 19.2, 'batterK': 15.9, 'batterWhiff': 21.4, 'pitcherK': 20.3}),
            row("Ty France", "R", "+740", 74, "💎", ["vs Molina"], """Worst Pickz Hidden Gem. 0 HR, 93.3 mph EV, 25.0% barrels. Molina RHB split +0.30, HR risk 0.47. park/weather net drag (-21%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.4, 'batterK': 18.6, 'batterWhiff': 29.0, 'pitcherK': 20.3}),
            row("Xander Bogaerts", "R", "+1150", 62, "", ["vs Molina"], """0 HR, 92.8 mph EV. Molina RHB split +0.30, HR risk 0.47. park/weather net drag (-21%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.8, 'batterK': 17.1, 'batterWhiff': 26.7, 'pitcherK': 20.3}),
        ],
    },
    {
        "title": "SEA @ ATH - George Kirby (R, SEA) vs Jeffrey Springs (L, ATH)",
        "kLines": {'Kirby': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 24.2, 'matchupK': 19.1, 'ownK': 17.9}, 'Springs': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 21.9, 'matchupK': 17.2, 'ownK': 15.0}},
        "description": "Tail key data: Park boost +35% (stadium +29%, weather +7%). Kirby (HR risk -0.23, vs LHB +0.12, vs RHB -0.49). Springs (HR risk 0.43, vs LHB +1.28, vs RHB -0.09).",
        "rows": [
            row("Lawrence Butler", "L", "+520", 82, "💎", ["vs Kirby"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.7 mph EV, 25.0% barrels. Kirby LHB split +0.12, HR risk -0.23. pitcher risk below avg (-0.23).""", blast="good", contact={'stars': 3, 'k': 22.4, 'batterK': 31.8, 'batterWhiff': 25.3, 'pitcherK': 17.9}),
            row("Zack Gelof", "R", "+447", 77, "💎", ["vs Kirby"], """Worst Pickz Hidden Gem. 0 HR, 92.2 mph EV, 12.5% barrels. Kirby RHB split -0.49, HR risk -0.23. tough split lane (-0.49); pitcher risk below avg (-0.23).""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 28.4, 'batterWhiff': 35.3, 'pitcherK': 17.9}),
            row("Jonah Heim", "S", "+600", 54, "", ["vs Kirby"], """0 HR, 90.6 mph EV. Kirby SHB→LHB split +0.12, HR risk -0.23. pitcher risk below avg (-0.23); limited recent HR events.""", contact={'stars': 5, 'k': 16.5, 'batterK': 16.0, 'batterWhiff': 13.4, 'pitcherK': 17.9}),
            row("Dominic Canzone", "L", "+360", 80, "💎", ["vs Springs"], """Worst Pickz Hidden Gem. 0 HR, 91.9 mph EV, 12.5% barrels. Springs LHB split +1.28, HR risk 0.43. limited recent HR events.""", contact={'stars': 4, 'k': 19.5, 'batterK': 25.8, 'batterWhiff': 24.6, 'pitcherK': 15.0}),
            row("Brock Rodden", "S", "N/A", 69, "", ["vs Springs"], """0 HR, 1 near-HR, 95.3 mph EV. Springs SHB→RHB split -0.09, HR risk 0.43. slight split headwind (-0.09); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.6, 'batterK': 26.9, 'batterWhiff': 33.0, 'pitcherK': 15.0}),
            row("Cole Young", "L", "+576", 68, "", ["vs Springs"], """0 HR, 1 near-HR, 87.0 mph EV, 12.5% barrels. Springs LHB split +1.28, HR risk 0.43. limited recent HR events; lighter EV form (87.0 mph).""", contact={'stars': 4, 'k': 18.3, 'batterK': 21.8, 'batterWhiff': 23.6, 'pitcherK': 15.0}),
        ],
    },
    {
        "title": "TEX @ ARI - MacKenzie Gore (L, TEX) vs Merrill Kelly (R, ARI)",
        "kLines": {'Gore': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 22.6, 'matchupK': 20.7, 'ownK': 23.3}, 'Kelly': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 24.1, 'matchupK': 19.3, 'ownK': 17.4}},
        "description": "Tail key data: Park boost -8% (stadium -8%, weather -1%). Gore (HR risk -0.74, vs LHB -0.48, vs RHB -0.57). Kelly (BAA vs LHB .272, vs RHB .266, HR/9 1.65).",
        "rows": [
            row("Corbin Carroll", "L", "+575", 65, "💎", ["vs Gore"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 92.4 mph EV, 25.0% barrels. Gore LHB split -0.48, HR risk -0.74. tough split lane (-0.48); pitcher suppresses HR (-0.74).""", blast="good", contact={'stars': 3, 'k': 23.8, 'batterK': 24.4, 'batterWhiff': 27.5, 'pitcherK': 23.3}),
            row("Gabriel Moreno", "R", "+880", 51, "", ["vs Gore"], """0 HR, 1 near-HR, 89.6 mph EV. Gore RHB split -0.57, HR risk -0.74. tough split lane (-0.57); pitcher suppresses HR (-0.74).""", contact={'stars': 4, 'k': 19.1, 'batterK': 14.1, 'batterWhiff': 17.5, 'pitcherK': 23.3}),
            row("Ketel Marte", "S", "+440", 58, "💎", ["vs Gore"], """Worst Pickz Hidden Gem. 0 HR, 98.7 mph EV. Gore SHB→RHB split -0.57, HR risk -0.74. tough split lane (-0.57); pitcher suppresses HR (-0.74).""", blast="good", contact={'stars': 4, 'k': 17.9, 'batterK': 11.8, 'batterWhiff': 14.7, 'pitcherK': 23.3}),
            row("Wyatt Langford", "R", "+525", 64, "", ["vs Kelly"], """1 HR, 1 near-HR, 83.3 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-8%).""", blast="good", contact={'stars': 4, 'k': 17.9, 'batterK': 16.9, 'batterWhiff': 22.8, 'pitcherK': 17.4}),
            row("Brandon Nimmo", "L", "+509", 57, "", ["vs Kelly"], """0 HR, 93.4 mph EV. limited split/risk sample; park/weather net drag (-8%).""", blast="good", contact={'stars': 3, 'k': 20.0, 'batterK': 23.0, 'batterWhiff': 25.9, 'pitcherK': 17.4}),
            row("Ezequiel Duran", "R", "+840", 60, "", ["vs Kelly"], """0 HR, 94.0 mph EV. limited split/risk sample; park/weather net drag (-8%).""", blast="good", contact={'stars': 4, 'k': 19.1, 'batterK': 19.8, 'batterWhiff': 25.4, 'pitcherK': 17.4}),
            row("Justin Foscue", "R", "N/A", 61, "", ["vs Kelly"], """0 HR, 91.5 mph EV. limited split/risk sample; park/weather net drag (-8%).""", contact={'stars': 4, 'k': 17.9, 'batterK': 18.3, 'batterWhiff': 18.7, 'pitcherK': 17.4}),
            row("Corey Seager", "L", "+400", 81, "🌕 💣", ["vs Kelly"], """2 HR, 2 near-HR, 88.3 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-8%).""", blast="high", contact={'stars': 3, 'k': 20.4, 'batterK': 20.5, 'batterWhiff': 32.3, 'pitcherK': 17.4}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-11")

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

    out = ROOT / '_games-0911.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
