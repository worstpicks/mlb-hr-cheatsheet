#!/usr/bin/env python3
"""Generate games[] block for 2026-09-09 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Bobby Witt Jr. (R)",
    "Brett Baty (L)",
    "Bryan Reynolds (S)",
    "Colt Keith (L)",
    "Elly De La Cruz (S)",
    "Kazuma Okamoto (R)",
    "Kody Clemens (L)",
    "Kyren Paris (R)",
    "Matt Olson (L)",
    "Pete Alonso (R)",
    "Pete Crow Armstrong (L)",
    "Rafael Devers (L)",
    "Travis Bazzana (L)",
    "Trea Turner (R)",
    "Vinnie Pasquantino (L)",
}

GEMS = {
    "Andrew Benintendi (L)",
    "Blaze Alexander (R)",
    "Brandon Marsh (L)",
    "Bryce Harper (L)",
    "Christian Encarnacion-Strand (R)",
    "Coby Mayo (R)",
    "Corey Seager (L)",
    "Dominic Canzone (L)",
    "Francisco Alvarez (R)",
    "Henry Bolte (R)",
    "Isaac Paredes (R)",
    "Jake McCarthy (L)",
    "Javier Sanoja (R)",
    "Josh Bell (S)",
    "Juan Soto (L)",
    "Kyle Stowers (L)",
    "Leonardo Bernal (S)",
    "Roman Anthony (L)",
    "Salvador Perez (R)",
    "TJ Rumfield (L)",
    "Tristan Peters (L)",
}

PLAYER_TEAMS = {
    "Aaron Judge (R)": "NYY",
    "Adley Rutschman (S)": "BOS",
    "Alec Burleson (L)": "STL",
    "Alex Bregman (R)": "CHC",
    "Alex Freeland (S)": "LAD",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Vaughn (R)": "MIL",
    "Angel Genao (S)": "CLE",
    "Austin Riley (R)": "ATL",
    "Austin Wells (L)": "NYY",
    "Blaze Alexander (R)": "BAL",
    "Bo Bichette (R)": "NYM",
    "Bo Naylor (L)": "MIL",
    "Bobby Witt Jr. (R)": "KC",
    "Brady House (R)": "WSH",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Brett Baty (L)": "NYM",
    "Brice Turang (L)": "MIL",
    "Brooks Lee (S)": "MIN",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Cam Smith (R)": "HOU",
    "Carson Kelly (R)": "CHC",
    "Carter Jensen (L)": "KC",
    "Chase DeLauter (L)": "CLE",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Christian Moore (R)": "LAA",
    "Christian Walker (R)": "HOU",
    "Coby Mayo (R)": "BAL",
    "Colt Keith (L)": "DET",
    "Corey Seager (L)": "TEX",
    "Daylen Lile (L)": "WSH",
    "Dominic Canzone (L)": "SEA",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Ezequiel Duran (R)": "TEX",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Gabriel Moreno (R)": "ARI",
    "George Springer (R)": "TOR",
    "Griffin Conine (L)": "MIA",
    "Hao Yu Lee (R)": "DET",
    "Henry Bolte (R)": "ATH",
    "Henry Davis (R)": "PIT",
    "Heriberto Hernandez (R)": "MIA",
    "Isaac Paredes (R)": "HOU",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jake McCarthy (L)": "COL",
    "James McCann (R)": "ARI",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jarren Duran (L)": "BOS",
    "Javier Sanoja (R)": "MIA",
    "Joe Mack (L)": "MIA",
    "John Peck (R)": "DET",
    "Jonathan Aranda (L)": "TB",
    "Jose Siri (R)": "LAA",
    "Josh Bell (S)": "MIN",
    "Joshua Baez (R)": "STL",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Konnor Griffin (R)": "PIT",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Kyle Tucker (L)": "LAD",
    "Kyren Paris (R)": "LAA",
    "Lawrence Butler (L)": "ATH",
    "Leonardo Bernal (S)": "STL",
    "Luis Torrens (R)": "NYM",
    "Manny Machado (R)": "SD",
    "Mark Vientos (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Max Muncy (R)": "ATH",
    "Michael Busch (L)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Mike Trout (R)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Nasim Nunez (S)": "WSH",
    "Nelson Velazquez (R)": "HOU",
    "Nick Sogard (S)": "BOS",
    "Ozzie Albies (S)": "ATL",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Rafael Flores (R)": "PIT",
    "Randy Arozarena (R)": "SEA",
    "Roman Anthony (L)": "BOS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "TJ Rumfield (L)": "COL",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Travis Bazzana (L)": "CLE",
    "Trea Turner (R)": "PHI",
    "Trevor Larnach (L)": "MIN",
    "Trevor Story (R)": "BOS",
    "Tristan Peters (L)": "CWS",
    "Ty France (R)": "SD",
    "Vinnie Pasquantino (L)": "KC",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Yainer Diaz (R)": "HOU",
    "Yandy Diaz (R)": "TB",
    "Yohandy Morales (R)": "WSH",
    "Yordan Alvarez (L)": "HOU",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("ARI @ KC", "Gallen"),
    ("COL @ NYY", "Sugano"),
    ("COL @ NYY", "Warren"),
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
        "title": "ARI @ KC - Zac Gallen 🧤 (R, ARI) vs Daniel Lynch IV (L, KC)",
        "kLines": {'Gallen': {'k': 3.2, 'lo': 2, 'hi': 5, 'bf': 22.8, 'matchupK': 14.2, 'ownK': 13.0}, 'Lynch IV': {'k': 2.7, 'lo': 1, 'hi': 4, 'bf': 18.4, 'matchupK': 14.8, 'ownK': 11.3}},
        "description": "Tail key data: Park boost +27% (stadium +12%, weather +15%). Gallen 🧤 (HR risk 1.35, vs LHB +0.49, vs RHB +1.62). Lynch IV (HR risk -0.11, vs LHB -0.26, vs RHB +0.07).",
        "rows": [
            row("Vinnie Pasquantino", "L", "+585", 93, "⭐ 🌕 💣", ["vs Gallen"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.4 mph EV, 20.0% barrels. Gallen LHB split +0.49, HR risk 1.35.""", blast="high", contact={'stars': 5, 'k': 11.6, 'batterK': 5.7, 'batterWhiff': 12.6, 'pitcherK': 13.0}),
            row("Carter Jensen", "L", "+493", 92, "🌕 💣", ["vs Gallen"], """1 HR, 1 near-HR, 96.0 mph EV, 20.0% barrels. Gallen LHB split +0.49, HR risk 1.35.""", blast="good", contact={'stars': 4, 'k': 17.2, 'batterK': 21.3, 'batterWhiff': 26.2, 'pitcherK': 13.0}),
            row("Salvador Perez", "R", "+485", 92, "🌕 💣 💎", ["vs Gallen"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.1 mph EV, 20.0% barrels. Gallen RHB split +1.62, HR risk 1.35.""", blast="good", contact={'stars': 5, 'k': 15.3, 'batterK': 15.1, 'batterWhiff': 22.7, 'pitcherK': 13.0}),
            row("Bobby Witt Jr.", "R", "+475", 93, "⭐ 🌕 💣", ["vs Gallen"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 94.0 mph EV, 20.0% barrels. Gallen RHB split +1.62, HR risk 1.35. limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 15.2, 'batterK': 14.1, 'batterWhiff': 24.8, 'pitcherK': 13.0}),
            row("Jac Caglianone", "L", "N/A", 82, "", ["vs Gallen"], """0 HR, 90.6 mph EV. Gallen LHB split +0.49, HR risk 1.35. limited recent HR events.""", contact={'stars': 4, 'k': 18.1, 'batterK': 21.3, 'batterWhiff': 31.2, 'pitcherK': 13.0}),
            row("Ketel Marte", "S", "+521", 75, "", ["vs Lynch IV"], """0 HR, 96.0 mph EV. Lynch IV SHB→RHB split +0.07, HR risk -0.11. pitcher risk below avg (-0.11); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.7, 'batterK': 14.0, 'batterWhiff': 18.2, 'pitcherK': None}),
            row("James McCann", "R", "+800", 74, "", ["vs Lynch IV"], """0 HR, 1 near-HR, 92.3 mph EV, 20.0% barrels. Lynch IV RHB split +0.07, HR risk -0.11. pitcher risk below avg (-0.11); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 23.6, 'batterWhiff': 30.0, 'pitcherK': None}),
            row("Tim Tawa", "R", "+650", 75, "", ["vs Lynch IV"], """0 HR, 96.9 mph EV. Lynch IV RHB split +0.07, HR risk -0.11. pitcher risk below avg (-0.11); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.2, 'batterK': 30.4, 'batterWhiff': 30.1, 'pitcherK': None}),
            row("Gabriel Moreno", "R", "+750", 71, "", ["vs Lynch IV"], """0 HR, 1 near-HR, 91.5 mph EV. Lynch IV RHB split +0.07, HR risk -0.11. pitcher risk below avg (-0.11); limited recent HR events.""", contact={'stars': 4, 'k': 18.8, 'batterK': 14.8, 'batterWhiff': 17.8, 'pitcherK': None}),
        ],
    },
    {
        "title": "CHC @ MIL - Kevin Gausman (R, CHC) vs Logan Henderson (R, MIL)",
        "kLines": {'Gausman': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 23.2, 'matchupK': 22.6, 'ownK': 23.9}, 'Henderson': {'k': 5.4, 'lo': 4, 'hi': 7, 'bf': 21.0, 'matchupK': 25.6, 'ownK': 28.6}},
        "description": "Tail key data: Park boost +15% (stadium -2%, weather +17%). Gausman (HR risk 0.32, vs LHB -0.31, vs RHB +1.08). Henderson (HR risk 0.51, vs LHB +0.61, vs RHB +0.04).",
        "rows": [
            row("Bo Naylor", "L", "N/A", 72, "", ["vs Gausman"], """1 HR, 2 near-HR, 91.6 mph EV, 25.0% barrels. Gausman LHB split -0.31, HR risk 0.32. slight split headwind (-0.31).""", blast="good", contact={'stars': 3, 'k': 21.0, 'batterK': 24.6, 'batterWhiff': 13.5, 'pitcherK': 23.9}),
            row("Andrew Vaughn", "R", "N/A", 87, "", ["vs Gausman"], """1 HR, 2 near-HR, 95.4 mph EV, 12.5% barrels. Gausman RHB split +1.08, HR risk 0.32.""", blast="good", contact={'stars': 3, 'k': 20.4, 'batterK': 18.0, 'batterWhiff': 15.7, 'pitcherK': 23.9}),
            row("Jake Bauers", "L", "+500", 74, "", ["vs Gausman"], """0 HR, 97.1 mph EV. Gausman LHB split -0.31, HR risk 0.32. slight split headwind (-0.31); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 26.6, 'batterK': 29.1, 'batterWhiff': 33.6, 'pitcherK': 23.9}),
            row("Brice Turang", "L", "+1040", 58, "", ["vs Gausman"], """0 HR, 91.7 mph EV. Gausman LHB split -0.31, HR risk 0.32. slight split headwind (-0.31); limited recent HR events.""", contact={'stars': 3, 'k': 23.2, 'batterK': 24.4, 'batterWhiff': 21.6, 'pitcherK': 23.9}),
            row("Jackson Chourio", "R", "+456", 82, "", ["vs Gausman"], """0 HR, 1 near-HR, 96.1 mph EV. Gausman RHB split +1.08, HR risk 0.32. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 17.2, 'batterWhiff': 23.4, 'pitcherK': 23.9}),
            row("Pete Crow Armstrong", "L", "+319", 97, "🚀 ⭐ 🌕 💣", ["vs Henderson"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.7 mph EV, 25.0% barrels. Henderson LHB split +0.61, HR risk 0.51.""", blast="high", contact={'stars': 2, 'k': 24.4, 'batterK': 20.2, 'batterWhiff': 21.5, 'pitcherK': 28.6}),
            row("Michael Conforto", "L", "+700", 83, "", ["vs Henderson"], """1 HR, 1 near-HR, 83.3 mph EV, 12.5% barrels. Henderson LHB split +0.61, HR risk 0.51. lighter EV form (83.3 mph).""", blast="good", contact={'stars': 2, 'k': 25.0, 'batterK': 20.8, 'batterWhiff': 22.6, 'pitcherK': 28.6}),
            row("Carson Kelly", "R", "+900", 65, "", ["vs Henderson"], """0 HR, 90.8 mph EV, 12.5% barrels. Henderson RHB split +0.04, HR risk 0.51. limited recent HR events.""", contact={'stars': 3, 'k': 24.0, 'batterK': 19.5, 'batterWhiff': 20.0, 'pitcherK': 28.6}),
            row("Alex Bregman", "R", "+700", 79, "", ["vs Henderson"], """0 HR, 2 near-HR, 92.3 mph EV, 12.5% barrels. Henderson RHB split +0.04, HR risk 0.51.""", blast="good", contact={'stars': 3, 'k': 20.6, 'batterK': 11.0, 'batterWhiff': 18.1, 'pitcherK': 28.6}),
            row("Michael Busch", "L", "+479", 79, "", ["vs Henderson"], """0 HR, 92.8 mph EV. Henderson LHB split +0.61, HR risk 0.51. limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 29.4, 'batterK': 29.1, 'batterWhiff': 32.4, 'pitcherK': 28.6}),
        ],
    },
    {
        "title": "CIN @ LAD - Rhett Lowder (R, CIN) vs Yoshinobu Yamamoto (R, LAD)",
        "kLines": {'Lowder': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 22.1, 'matchupK': 16.8, 'ownK': 15.0}, 'Yamamoto': {'k': 6.8, 'lo': 5, 'hi': 8, 'bf': 24.7, 'matchupK': 27.6, 'ownK': 27.2}},
        "description": "Tail key data: Park boost +26% (stadium +19%, weather +7%). Lowder (HR risk 0.52, vs LHB +0.23, vs RHB +0.62). Yamamoto (HR risk -0.31, vs LHB -0.13, vs RHB -0.22).",
        "rows": [
            row("Mookie Betts", "R", "+537", 73, "", ["vs Lowder"], """0 HR, 94.3 mph EV. Lowder RHB split +0.62, HR risk 0.52. limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 13.0, 'batterK': 8.6, 'batterWhiff': 11.9, 'pitcherK': 15.0}),
            row("Teoscar Hernandez", "R", "+426", 84, "🚀", ["vs Lowder"], """0 HR, 100.7 mph EV. Lowder RHB split +0.62, HR risk 0.52. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.5, 'batterK': 27.4, 'batterWhiff': 35.0, 'pitcherK': 15.0}),
            row("Max Muncy", "L", "+422", 87, "", ["vs Lowder"], """0 HR, 91.9 mph EV, 25.0% barrels. Lowder LHB split +0.23, HR risk 0.52. limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.9, 'batterK': 20.3, 'batterWhiff': 28.8, 'pitcherK': 15.0}),
            row("Kyle Tucker", "L", "+540", 77, "", ["vs Lowder"], """1 HR, 1 near-HR, 92.9 mph EV, 12.5% barrels. Lowder LHB split +0.23, HR risk 0.52.""", blast="good", contact={'stars': 5, 'k': 15.5, 'batterK': 11.4, 'batterWhiff': 20.1, 'pitcherK': 15.0}),
            row("Alex Freeland", "S", "+700", 78, "", ["vs Lowder"], """0 HR, 96.6 mph EV, 25.0% barrels. Lowder SHB→LHB split +0.23, HR risk 0.52. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.5, 'batterK': 34.1, 'batterWhiff': 35.4, 'pitcherK': 15.0}),
            row("Elly De La Cruz", "S", "+537", 87, "🚀 ⭐ 🌕 💣", ["vs Yamamoto"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 100.5 mph EV, 25.0% barrels. Yamamoto SHB→LHB split -0.13, HR risk -0.31. slight split headwind (-0.13); pitcher risk below avg (-0.31).""", blast="high", contact={'stars': 2, 'k': 26.7, 'batterK': 26.7, 'batterWhiff': 25.6, 'pitcherK': 27.2}),
            row("Sal Stewart", "R", "+485", 72, "", ["vs Yamamoto"], """0 HR, 2 near-HR, 93.0 mph EV. Yamamoto RHB split -0.22, HR risk -0.31. slight split headwind (-0.22); pitcher risk below avg (-0.31).""", blast="good", contact={'stars': 3, 'k': 23.6, 'batterK': 16.9, 'batterWhiff': 26.2, 'pitcherK': 27.2}),
            row("JJ Bleday", "L", "+460", 66, "", ["vs Yamamoto"], """0 HR, 88.6 mph EV, 25.0% barrels. Yamamoto LHB split -0.13, HR risk -0.31. slight split headwind (-0.13); pitcher risk below avg (-0.31).""", blast="good", contact={'stars': 2, 'k': 27.3, 'batterK': 26.2, 'batterWhiff': 29.9, 'pitcherK': 27.2}),
        ],
    },
    {
        "title": "CLE @ BAL - Foster Griffin (L, CLE) vs Shane Baz (R, BAL)",
        "kLines": {'Griffin': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 23.2, 'matchupK': 19.7, 'ownK': 17.7}, 'Baz': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 24.3, 'matchupK': 20.5, 'ownK': 23.4}},
        "description": "Tail key data: Park boost +11% (stadium -4%, weather +15%). Griffin (HR risk -0.20, vs LHB +0.21, vs RHB -0.26). Baz (HR risk -0.48, vs LHB -0.05, vs RHB -0.86).",
        "rows": [
            row("Pete Alonso", "R", "+350", 88, "⭐ 🌕 💣", ["vs Griffin"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.5 mph EV, 37.5% barrels. Griffin RHB split -0.26, HR risk -0.20. slight split headwind (-0.26); pitcher risk below avg (-0.20).""", blast="good", contact={'stars': 3, 'k': 20.8, 'batterK': 23.5, 'batterWhiff': 29.1, 'pitcherK': 17.7}),
            row("Coby Mayo", "R", "+393", 89, "🌕 💣 💎", ["vs Griffin"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 90.4 mph EV, 25.0% barrels. Griffin RHB split -0.26, HR risk -0.20. slight split headwind (-0.26); pitcher risk below avg (-0.20).""", blast="high", contact={'stars': 3, 'k': 20.7, 'batterK': 24.0, 'batterWhiff': 28.0, 'pitcherK': 17.7}),
            row("Christian Encarnacion-Strand", "R", "+400", 76, "💎", ["vs Griffin"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 86.7 mph EV, 25.0% barrels. Griffin RHB split -0.26, HR risk -0.20. slight split headwind (-0.26); pitcher risk below avg (-0.20).""", blast="good", contact={'stars': 3, 'k': 22.1, 'batterK': 31.0, 'batterWhiff': 28.3, 'pitcherK': 17.7}),
            row("Blaze Alexander", "R", "+800", 61, "💎", ["vs Griffin"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.3 mph EV. Griffin RHB split -0.26, HR risk -0.20. slight split headwind (-0.26); pitcher risk below avg (-0.20).""", blast="good", contact={'stars': 4, 'k': 19.0, 'batterK': 20.5, 'batterWhiff': 22.9, 'pitcherK': 17.7}),
            row("Travis Bazzana", "L", "+540", 78, "⭐ 🌕 💣", ["vs Baz"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 88.9 mph EV, 25.0% barrels. Baz LHB split -0.05, HR risk -0.48. slight split headwind (-0.05); pitcher suppresses HR (-0.48).""", blast="high", contact={'stars': 3, 'k': 20.7, 'batterK': 15.8, 'batterWhiff': 22.1, 'pitcherK': 23.4}),
            row("Chase DeLauter", "L", "+390", 68, "", ["vs Baz"], """0 HR, 2 near-HR, 91.1 mph EV, 12.5% barrels. Baz LHB split -0.05, HR risk -0.48. slight split headwind (-0.05); pitcher suppresses HR (-0.48).""", blast="good", contact={'stars': 4, 'k': 19.4, 'batterK': 17.3, 'batterWhiff': 13.5, 'pitcherK': 23.4}),
            row("Angel Genao", "S", "+800", 52, "", ["vs Baz"], """0 HR, 89.9 mph EV. Baz SHB→LHB split -0.05, HR risk -0.48. slight split headwind (-0.05); pitcher suppresses HR (-0.48).""", contact={'stars': 3, 'k': 21.6, 'batterK': 18.1, 'batterWhiff': 23.2, 'pitcherK': 23.4}),
        ],
    },
    {
        "title": "COL @ NYY - Tomoyuki Sugano 🧤 (R, COL) vs Will Warren 🧤 (R, NYY)",
        "kLines": {'Sugano': {'k': 3.9, 'lo': 2, 'hi': 5, 'bf': 22.5, 'matchupK': 17.1, 'ownK': 14.3}, 'Warren': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 22.3, 'matchupK': 21.0, 'ownK': 21.2}},
        "description": "Tail key data: Park boost +27% (stadium +6%, weather +21%). Sugano 🧤 (HR risk 0.99, vs LHB +1.15, vs RHB -0.32). Warren 🧤 (HR risk 0.99, vs LHB +0.14, vs RHB +1.40).",
        "rows": [
            row("Spencer Jones", "L", "+310", 98, "🚀 🌕 💣", ["vs Sugano"], """2 HR, 2 near-HR, 102.0 mph EV, 50.0% barrels. Sugano LHB split +1.15, HR risk 0.99.""", blast="high", contact={'stars': 3, 'k': 23.1, 'batterK': 37.5, 'batterWhiff': 37.3, 'pitcherK': 14.3}),
            row("Aaron Judge", "R", "+219", 91, "🌕 💣", ["vs Sugano"], """0 HR, 1 near-HR, 96.0 mph EV, 12.5% barrels. Sugano RHB split -0.32, HR risk 0.99. slight split headwind (-0.32); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.8, 'batterK': 26.4, 'batterWhiff': 29.4, 'pitcherK': 14.3}),
            row("Austin Wells", "L", "+500", 88, "🌕 💣", ["vs Sugano"], """0 HR, 1 near-HR, 97.6 mph EV, 12.5% barrels. Sugano LHB split +1.15, HR risk 0.99. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 19.9, 'batterK': 33.3, 'batterWhiff': 26.0, 'pitcherK': 14.3}),
            row("Ryan McMahon", "L", "+520", 84, "", ["vs Sugano"], """0 HR, 96.0 mph EV. Sugano LHB split +1.15, HR risk 0.99. limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.4, 'batterK': 26.7, 'batterWhiff': 29.1, 'pitcherK': 14.3}),
            row("Jake McCarthy", "L", "+900", 96, "🌕 💣 💎", ["vs Warren"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 97.4 mph EV, 37.5% barrels. Warren LHB split +0.14, HR risk 0.99.""", blast="high", contact={'stars': 4, 'k': 17.8, 'batterK': 14.0, 'batterWhiff': 16.6, 'pitcherK': 21.2}),
            row("TJ Rumfield", "L", "+870", 83, "💎", ["vs Warren"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 89.9 mph EV, 25.0% barrels. Warren LHB split +0.14, HR risk 0.99. limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 17.1, 'batterK': 10.5, 'batterWhiff': 17.0, 'pitcherK': 21.2}),
        ],
    },
    {
        "title": "HOU @ PHI - Hunter Brown (R, HOU) vs Cristopher Sanchez (L, PHI)",
        "kLines": {'Brown': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 22.5, 'matchupK': 22.1, 'ownK': 24.5}, 'Sanchez': {'k': 6.7, 'lo': 5, 'hi': 8, 'bf': 25.2, 'matchupK': 26.5, 'ownK': 27.3}},
        "description": "Tail key data: Park boost +37% (stadium +14%, weather +23%). Brown (HR risk -0.50, vs LHB +0.10, vs RHB -1.03). Sanchez (HR risk -1.24, vs LHB -1.48, vs RHB -0.70).",
        "rows": [
            row("Bryson Stott", "L", "+810", 75, "", ["vs Brown"], """1 HR, 2 near-HR, 93.9 mph EV, 25.0% barrels. Brown LHB split +0.10, HR risk -0.50. pitcher suppresses HR (-0.50).""", blast="good", contact={'stars': 3, 'k': 21.3, 'batterK': 16.7, 'batterWhiff': 21.2, 'pitcherK': 24.5}),
            row("Kyle Schwarber", "L", "+255", 90, "🌕 💣", ["vs Brown"], """2 HR, 2 near-HR, 91.6 mph EV, 25.0% barrels. Brown LHB split +0.10, HR risk -0.50. pitcher suppresses HR (-0.50).""", blast="high", contact={'stars': 2, 'k': 24.2, 'batterK': 21.7, 'batterWhiff': 30.4, 'pitcherK': 24.5}),
            row("Brandon Marsh", "L", "+690", 72, "💎", ["vs Brown"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.1 mph EV, 12.5% barrels. Brown LHB split +0.10, HR risk -0.50. pitcher suppresses HR (-0.50); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.0, 'batterK': 19.6, 'batterWhiff': 20.2, 'pitcherK': 24.5}),
            row("Trea Turner", "R", "+770", 65, "⭐", ["vs Brown"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 94.1 mph EV. Brown RHB split -1.03, HR risk -0.50. tough split lane (-1.03); pitcher suppresses HR (-0.50).""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 20.0, 'batterWhiff': 28.2, 'pitcherK': 24.5}),
            row("Bryce Harper", "L", "+472", 70, "💎", ["vs Brown"], """Worst Pickz Hidden Gem. 0 HR, 88.5 mph EV. Brown LHB split +0.10, HR risk -0.50. pitcher suppresses HR (-0.50); limited recent HR events.""", contact={'stars': 3, 'k': 23.8, 'batterK': 21.2, 'batterWhiff': 28.5, 'pitcherK': 24.5}),
            row("Yordan Alvarez", "L", "+360", 74, "", ["vs Sanchez"], """1 HR, 1 near-HR, 93.1 mph EV. Sanchez LHB split -1.48, HR risk -1.24. tough split lane (-1.48); pitcher suppresses HR (-1.24).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 21.2, 'batterWhiff': 16.7, 'pitcherK': 27.3}),
            row("Nelson Velazquez", "R", "+500", 68, "", ["vs Sanchez"], """0 HR, 92.6 mph EV. Sanchez RHB split -0.70, HR risk -1.24. tough split lane (-0.70); pitcher suppresses HR (-1.24).""", blast="good", contact={'stars': 1, 'k': 31.5, 'batterK': 43.2, 'batterWhiff': 48.5, 'pitcherK': 27.3}),
            row("Isaac Paredes", "R", "+534", 57, "💎", ["vs Sanchez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 71.7 mph EV, 12.5% barrels. Sanchez RHB split -0.70, HR risk -1.24. tough split lane (-0.70); pitcher suppresses HR (-1.24).""", blast="good", contact={'stars': 4, 'k': 18.6, 'batterK': 9.3, 'batterWhiff': 12.8, 'pitcherK': 27.3}),
            row("Cam Smith", "R", "+650", 66, "", ["vs Sanchez"], """1 HR, 1 near-HR, 86.5 mph EV, 12.5% barrels. Sanchez RHB split -0.70, HR risk -1.24. tough split lane (-0.70); pitcher suppresses HR (-1.24).""", blast="good", contact={'stars': 1, 'k': 28.4, 'batterK': 32.2, 'batterWhiff': 32.3, 'pitcherK': 27.3}),
            row("Yainer Diaz", "R", "+900", 62, "", ["vs Sanchez"], """0 HR, 2 near-HR, 86.9 mph EV, 25.0% barrels. Sanchez RHB split -0.70, HR risk -1.24. tough split lane (-0.70); pitcher suppresses HR (-1.24).""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 16.4, 'batterWhiff': 21.8, 'pitcherK': 27.3}),
            row("Christian Walker", "R", "+560", 47, "", ["vs Sanchez"], """0 HR, 86.9 mph EV. Sanchez RHB split -0.70, HR risk -1.24. tough split lane (-0.70); pitcher suppresses HR (-1.24).""", contact={'stars': 2, 'k': 26.0, 'batterK': 24.4, 'batterWhiff': 26.6, 'pitcherK': 27.3}),
        ],
    },
    {
        "title": "LAA @ BOS - Ryan Johnson (R, LAA) vs Jake Bennett (L, BOS)",
        "kLines": {'Johnson': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 21.1, 'matchupK': 17.7, 'ownK': 16.3}, 'Bennett': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 22.8, 'matchupK': 22.9, 'ownK': 21.0}},
        "description": "Tail key data: Park boost +7% (stadium -7%, weather +14%). Johnson (HR risk 0.65, vs LHB +0.52, vs RHB +0.46). Bennett (HR risk 0.27, vs LHB -1.70, vs RHB +0.94).",
        "rows": [
            row("Roman Anthony", "L", "+501", 89, "🚀 🌕 💣 💎", ["vs Johnson"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 102.2 mph EV, 25.0% barrels. Johnson LHB split +0.52, HR risk 0.65. park suppresses carry (-7%).""", blast="high", contact={'stars': 3, 'k': 20.7, 'batterK': 26.7, 'batterWhiff': 27.0, 'pitcherK': 16.3}),
            row("Nick Sogard", "S", "+870", 79, "", ["vs Johnson"], """1 HR, 1 near-HR, 91.4 mph EV, 12.5% barrels. Johnson SHB→LHB split +0.52, HR risk 0.65. park suppresses carry (-7%).""", blast="good", contact={'stars': 4, 'k': 18.4, 'batterK': 21.8, 'batterWhiff': 20.5, 'pitcherK': 16.3}),
            row("Adley Rutschman", "S", "+600", 79, "", ["vs Johnson"], """1 HR, 1 near-HR, 92.8 mph EV, 12.5% barrels. Johnson SHB→LHB split +0.52, HR risk 0.65. park suppresses carry (-7%).""", blast="good", contact={'stars': 4, 'k': 18.8, 'batterK': 25.0, 'batterWhiff': 18.9, 'pitcherK': 16.3}),
            row("Jarren Duran", "L", "+520", 87, "", ["vs Johnson"], """1 HR, 1 near-HR, 93.7 mph EV, 12.5% barrels. Johnson LHB split +0.52, HR risk 0.65. park suppresses carry (-7%).""", blast="good", contact={'stars': 3, 'k': 20.7, 'batterK': 23.3, 'batterWhiff': 32.4, 'pitcherK': 16.3}),
            row("Trevor Story", "R", "+525", 60, "", ["vs Johnson"], """0 HR, 89.8 mph EV, 12.5% barrels. Johnson RHB split +0.46, HR risk 0.65. park suppresses carry (-7%); limited recent HR events.""", contact={'stars': 3, 'k': 23.3, 'batterK': 34.1, 'batterWhiff': 32.4, 'pitcherK': 16.3}),
            row("Mike Trout", "R", "+475", 76, "", ["vs Bennett"], """0 HR, 1 near-HR, 94.0 mph EV, 12.5% barrels. Bennett RHB split +0.94, HR risk 0.27. park suppresses carry (-7%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.2, 'batterK': 28.4, 'batterWhiff': 30.4, 'pitcherK': 21.0}),
            row("Kyren Paris", "R", "+690", 71, "⭐", ["vs Bennett"], """Worst Pickz Favorite. 0 HR, 99.9 mph EV. Bennett RHB split +0.94, HR risk 0.27. park suppresses carry (-7%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 57.1, 'batterWhiff': 50.0, 'pitcherK': 21.0}),
            row("Jose Siri", "R", "+462", 73, "", ["vs Bennett"], """0 HR, 95.2 mph EV. Bennett RHB split +0.94, HR risk 0.27. park suppresses carry (-7%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 26.8, 'batterK': 40.0, 'batterWhiff': 40.6, 'pitcherK': 21.0}),
            row("Christian Moore", "R", "+630", 61, "", ["vs Bennett"], """0 HR, 94.1 mph EV. Bennett RHB split +0.94, HR risk 0.27. park suppresses carry (-7%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.6, 'batterK': 24.4, 'batterWhiff': 27.7, 'pitcherK': 21.0}),
        ],
    },
    {
        "title": "MIN @ DET - Zebby Matthews (R, MIN) vs Keider Montero (R, DET)",
        "kLines": {'Matthews': {'k': 4.9, 'lo': 3, 'hi': 7, 'bf': 23.7, 'matchupK': 20.8, 'ownK': 19.3}, 'Montero': {'k': 3.9, 'lo': 2, 'hi': 5, 'bf': 22.4, 'matchupK': 17.2, 'ownK': 17.6}},
        "description": "Tail key data: Park boost +12% (stadium -10%, weather +22%). Matthews (HR risk 0.77, vs LHB +0.81, vs RHB +0.15). Montero (HR risk -0.04, vs LHB +0.13, vs RHB -0.27).",
        "rows": [
            row("Spencer Torkelson", "R", "+470", 89, "🌕 💣", ["vs Matthews"], """2 HR, 2 near-HR, 93.6 mph EV, 25.0% barrels. Matthews RHB split +0.15, HR risk 0.77. park suppresses carry (-10%).""", blast="high", contact={'stars': 2, 'k': 26.1, 'batterK': 39.4, 'batterWhiff': 37.4, 'pitcherK': 19.3}),
            row("Colt Keith", "L", "+590", 82, "⭐", ["vs Matthews"], """Worst Pickz Favorite. 0 HR, 94.2 mph EV, 12.5% barrels. Matthews LHB split +0.81, HR risk 0.77. park suppresses carry (-10%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.6, 'batterK': 26.4, 'batterWhiff': 32.2, 'pitcherK': 19.3}),
            row("John Peck", "R", "+820", 87, "🚀 🌕 💣", ["vs Matthews"], """0 HR, 1 near-HR, 100.7 mph EV, 25.0% barrels. Matthews RHB split +0.15, HR risk 0.77. park suppresses carry (-10%); limited recent HR events.""", blast="high", contact={'stars': 3, 'k': 20.9, 'batterK': 24.0, 'batterWhiff': 26.5, 'pitcherK': 19.3}),
            row("Hao Yu Lee", "R", "+591", 82, "", ["vs Matthews"], """1 HR, 1 near-HR, 91.2 mph EV, 12.5% barrels. Matthews RHB split +0.15, HR risk 0.77. park suppresses carry (-10%).""", blast="good", contact={'stars': 3, 'k': 22.7, 'batterK': 26.7, 'batterWhiff': 30.9, 'pitcherK': 19.3}),
            row("Kody Clemens", "L", "+427", 89, "⭐ 🌕 💣", ["vs Montero"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.8 mph EV, 25.0% barrels. Montero LHB split +0.13, HR risk -0.04. pitcher risk below avg (-0.04); park suppresses carry (-10%).""", blast="high", contact={'stars': 4, 'k': 18.2, 'batterK': 18.5, 'batterWhiff': 20.4, 'pitcherK': 17.6}),
            row("Josh Bell", "S", "+520", 78, "💎", ["vs Montero"], """Worst Pickz Hidden Gem. 0 HR, 94.3 mph EV, 25.0% barrels. Montero SHB→LHB split +0.13, HR risk -0.04. pitcher risk below avg (-0.04); park suppresses carry (-10%).""", blast="good", contact={'stars': 5, 'k': 16.8, 'batterK': 14.3, 'batterWhiff': 18.4, 'pitcherK': 17.6}),
            row("Trevor Larnach", "L", "+880", 79, "", ["vs Montero"], """1 HR, 2 near-HR, 92.3 mph EV, 12.5% barrels. Montero LHB split +0.13, HR risk -0.04. pitcher risk below avg (-0.04); park suppresses carry (-10%).""", blast="good", contact={'stars': 3, 'k': 21.4, 'batterK': 22.4, 'batterWhiff': 33.0, 'pitcherK': 17.6}),
            row("Royce Lewis", "R", "+425", 65, "", ["vs Montero"], """0 HR, 1 near-HR, 94.5 mph EV, 12.5% barrels. Montero RHB split -0.27, HR risk -0.04. slight split headwind (-0.27); pitcher risk below avg (-0.04).""", blast="good", contact={'stars': 4, 'k': 19.4, 'batterK': 18.8, 'batterWhiff': 26.6, 'pitcherK': 17.6}),
            row("Brooks Lee", "S", "+610", 72, "", ["vs Montero"], """1 HR, 1 near-HR, 90.9 mph EV, 12.5% barrels. Montero SHB→LHB split +0.13, HR risk -0.04. pitcher risk below avg (-0.04); park suppresses carry (-10%).""", blast="good", contact={'stars': 5, 'k': 15.8, 'batterK': 12.2, 'batterWhiff': 15.3, 'pitcherK': 17.6}),
        ],
    },
    {
        "title": "NYM @ MIA - Robert Stock (R, NYM) vs Janson Junk (R, MIA)",
        "kLines": {'Stock': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 21.3, 'matchupK': 21.4, 'ownK': 19.7}, 'Junk': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 21.5, 'matchupK': 17.2, 'ownK': 14.7}},
        "description": "Tail key data: Park boost -12% (stadium -12%, weather +0%). Stock (HR risk -0.80, vs LHB -0.68, vs RHB -0.78). Junk (HR risk -0.92, vs LHB -0.47, vs RHB -0.69).",
        "rows": [
            row("Kyle Stowers", "L", "+400", 61, "💎", ["vs Stock"], """Worst Pickz Hidden Gem. 0 HR, 99.4 mph EV. Stock LHB split -0.68, HR risk -0.80. tough split lane (-0.68); pitcher suppresses HR (-0.80).""", blast="good", contact={'stars': 2, 'k': 27.3, 'batterK': 35.4, 'batterWhiff': 40.3, 'pitcherK': 19.7}),
            row("Javier Sanoja", "R", "+1100", 56, "💎", ["vs Stock"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.4 mph EV, 12.5% barrels. Stock RHB split -0.78, HR risk -0.80. tough split lane (-0.78); pitcher suppresses HR (-0.80).""", blast="good", contact={'stars': 5, 'k': 15.4, 'batterK': 7.5, 'batterWhiff': 12.4, 'pitcherK': 19.7}),
            row("Griffin Conine", "L", "+450", 55, "", ["vs Stock"], """0 HR, 1 near-HR, 89.9 mph EV, 12.5% barrels. Stock LHB split -0.68, HR risk -0.80. tough split lane (-0.68); pitcher suppresses HR (-0.80).""", contact={'stars': 2, 'k': 24.6, 'batterK': 27.6, 'batterWhiff': 36.0, 'pitcherK': 19.7}),
            row("Heriberto Hernandez", "R", "+450", 57, "", ["vs Stock"], """1 HR, 1 near-HR, 86.9 mph EV. Stock RHB split -0.78, HR risk -0.80. tough split lane (-0.78); pitcher suppresses HR (-0.80).""", blast="good", contact={'stars': 3, 'k': 22.6, 'batterK': 24.1, 'batterWhiff': 29.4, 'pitcherK': 19.7}),
            row("Joe Mack", "L", "+800", 48, "", ["vs Stock"], """0 HR, 92.7 mph EV. Stock LHB split -0.68, HR risk -0.80. tough split lane (-0.68); pitcher suppresses HR (-0.80).""", blast="good", contact={'stars': 3, 'k': 22.2, 'batterK': 26.7, 'batterWhiff': 26.1, 'pitcherK': 19.7}),
            row("Brett Baty", "L", "+775", 84, "⭐ 🌕 💣", ["vs Junk"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 96.6 mph EV, 25.0% barrels. Junk LHB split -0.47, HR risk -0.92. tough split lane (-0.47); pitcher suppresses HR (-0.92).""", blast="high", contact={'stars': 3, 'k': 20.1, 'batterK': 21.4, 'batterWhiff': 33.6, 'pitcherK': 14.7}),
            row("Juan Soto", "L", "+330", 57, "💎", ["vs Junk"], """Worst Pickz Hidden Gem. 0 HR, 86.9 mph EV, 12.5% barrels. Junk LHB split -0.47, HR risk -0.92. tough split lane (-0.47); pitcher suppresses HR (-0.92).""", contact={'stars': 5, 'k': 17.0, 'batterK': 14.5, 'batterWhiff': 25.6, 'pitcherK': 14.7}),
            row("Mark Vientos", "R", "N/A", 54, "", ["vs Junk"], """0 HR, 95.0 mph EV. Junk RHB split -0.69, HR risk -0.92. tough split lane (-0.69); pitcher suppresses HR (-0.92).""", blast="good", contact={'stars': 3, 'k': 21.1, 'batterK': 27.6, 'batterWhiff': 34.5, 'pitcherK': 14.7}),
            row("Luis Torrens", "R", "+1200", 83, "🌕 💣", ["vs Junk"], """3 HR, 3 near-HR, 93.9 mph EV, 37.5% barrels. Junk RHB split -0.69, HR risk -0.92. tough split lane (-0.69); pitcher suppresses HR (-0.92).""", blast="high", contact={'stars': 4, 'k': 17.3, 'batterK': 18.8, 'batterWhiff': 20.2, 'pitcherK': 14.7}),
            row("Francisco Alvarez", "R", "+910", 74, "💎", ["vs Junk"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 93.5 mph EV, 25.0% barrels. Junk RHB split -0.69, HR risk -0.92. tough split lane (-0.69); pitcher suppresses HR (-0.92).""", blast="good", contact={'stars': 2, 'k': 27.0, 'batterK': 48.6, 'batterWhiff': 43.4, 'pitcherK': 14.7}),
            row("Bo Bichette", "R", "+870", 53, "", ["vs Junk"], """1 HR, 1 near-HR, 84.3 mph EV, 12.5% barrels. Junk RHB split -0.69, HR risk -0.92. tough split lane (-0.69); pitcher suppresses HR (-0.92).""", blast="good", contact={'stars': 5, 'k': 16.7, 'batterK': 16.7, 'batterWhiff': 20.8, 'pitcherK': 14.7}),
            row("Jared Young", "L", "+650", 41, "", ["vs Junk"], """0 HR, 89.8 mph EV. Junk LHB split -0.47, HR risk -0.92. tough split lane (-0.47); pitcher suppresses HR (-0.92).""", contact={'stars': 4, 'k': 17.9, 'batterK': 21.1, 'batterWhiff': 21.9, 'pitcherK': 14.7}),
        ],
    },
    {
        "title": "PIT @ CWS - Lake Bachar (R, PIT) vs Davis Martin (R, CWS)",
        "kLines": {'Bachar': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 21.7, 'matchupK': 24.6, 'ownK': 24.7}, 'Martin': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 22.0, 'matchupK': 17.2, 'ownK': 13.8}},
        "description": "Tail key data: Park boost +4% (stadium -5%, weather +10%). Bachar (HR risk -0.07, vs LHB -0.37, vs RHB +0.85). Martin (HR risk 0.83, vs LHB +0.48, vs RHB +0.72).",
        "rows": [
            row("Tristan Peters", "L", "+725", 72, "💎", ["vs Bachar"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 96.2 mph EV, 25.0% barrels. Bachar LHB split -0.37, HR risk -0.07. slight split headwind (-0.37); pitcher risk below avg (-0.07).""", blast="good", contact={'stars': 3, 'k': 21.1, 'batterK': 13.9, 'batterWhiff': 24.8, 'pitcherK': 24.7}),
            row("Andrew Benintendi", "L", "+525", 72, "🌕 💣 💎", ["vs Bachar"], """Worst Pickz Hidden Gem. 0 HR, 99.6 mph EV, 25.0% barrels. Bachar LHB split -0.37, HR risk -0.07. slight split headwind (-0.37); pitcher risk below avg (-0.07).""", blast="high", contact={'stars': 3, 'k': 21.4, 'batterK': 17.6, 'batterWhiff': 21.8, 'pitcherK': 24.7}),
            row("Munetaka Murakami", "L", "+310", 71, "", ["vs Bachar"], """0 HR, 92.3 mph EV, 12.5% barrels. Bachar LHB split -0.37, HR risk -0.07. slight split headwind (-0.37); pitcher risk below avg (-0.07).""", blast="good", contact={'stars': 1, 'k': 32.1, 'batterK': 42.2, 'batterWhiff': 42.0, 'pitcherK': 24.7}),
            row("Bryan Reynolds", "S", "+550", 89, "⭐ 🌕 💣", ["vs Martin"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.6 mph EV, 25.0% barrels. Martin SHB→LHB split +0.48, HR risk 0.83.""", blast="good", contact={'stars': 5, 'k': 17.0, 'batterK': 16.9, 'batterWhiff': 26.0, 'pitcherK': 13.8}),
            row("Rafael Flores", "R", "+650", 89, "🌕 💣", ["vs Martin"], """1 HR, 2 near-HR, 96.9 mph EV, 12.5% barrels. Martin RHB split +0.72, HR risk 0.83.""", blast="good", contact={'stars': 3, 'k': 20.6, 'batterK': 29.7, 'batterWhiff': 30.3, 'pitcherK': 13.8}),
            row("Esmerlyn Valdez", "R", "+400", 85, "", ["vs Martin"], """0 HR, 92.5 mph EV, 25.0% barrels. Martin RHB split +0.72, HR risk 0.83. limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.4, 'batterK': 39.3, 'batterWhiff': 38.0, 'pitcherK': 13.8}),
            row("Brandon Lowe", "L", "+346", 76, "", ["vs Martin"], """0 HR, 92.3 mph EV. Martin LHB split +0.48, HR risk 0.83. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.0, 'batterK': 28.0, 'batterWhiff': 34.2, 'pitcherK': 13.8}),
            row("Konnor Griffin", "R", "+600", 71, "", ["vs Martin"], """0 HR, 89.8 mph EV, 12.5% barrels. Martin RHB split +0.72, HR risk 0.83. limited recent HR events.""", contact={'stars': 4, 'k': 19.8, 'batterK': 25.8, 'batterWhiff': 29.1, 'pitcherK': 13.8}),
            row("Henry Davis", "R", "N/A", 80, "", ["vs Martin"], """1 HR, 1 near-HR, 89.7 mph EV, 12.5% barrels. Martin RHB split +0.72, HR risk 0.83.""", blast="good", contact={'stars': 4, 'k': 18.5, 'batterK': 20.6, 'batterWhiff': 27.6, 'pitcherK': 13.8}),
        ],
    },
    {
        "title": "STL @ SF - Andre Pallante (R, STL) vs Blade Tidwell (R, SF)",
        "kLines": {'Pallante': {'k': 3.6, 'lo': 2, 'hi': 5, 'bf': 23.0, 'matchupK': 15.5, 'ownK': 14.3}, 'Tidwell': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 21.6, 'matchupK': 21.9, 'ownK': 20.1}},
        "description": "Tail key data: Park boost -14% (stadium -17%, weather +4%). Pallante (HR risk -1.52, vs LHB -0.96, vs RHB -1.19). Tidwell (HR risk 0.76, vs LHB +1.18, vs RHB -0.31).",
        "rows": [
            row("Rafael Devers", "L", "+440", 85, "🚀 ⭐ 🌕 💣", ["vs Pallante"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 101.9 mph EV, 50.0% barrels. Pallante LHB split -0.96, HR risk -1.52. tough split lane (-0.96); pitcher suppresses HR (-1.52).""", blast="high", contact={'stars': 4, 'k': 17.7, 'batterK': 19.8, 'batterWhiff': 27.9, 'pitcherK': 14.3}),
            row("Bryce Eldridge", "L", "+680", 54, "", ["vs Pallante"], """0 HR, 93.4 mph EV. Pallante LHB split -0.96, HR risk -1.52. tough split lane (-0.96); pitcher suppresses HR (-1.52).""", blast="good", contact={'stars': 4, 'k': 19.1, 'batterK': 26.7, 'batterWhiff': 25.9, 'pitcherK': 14.3}),
            row("Alec Burleson", "L", "+500", 88, "⭐ 🌕 💣", ["vs Tidwell"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.6 mph EV, 25.0% barrels. Tidwell LHB split +1.18, HR risk 0.76. park/weather net drag (-14%).""", blast="good", contact={'stars': 3, 'k': 21.3, 'batterK': 21.4, 'batterWhiff': 26.2, 'pitcherK': 20.1}),
            row("Joshua Baez", "R", "+563", 68, "", ["vs Tidwell"], """0 HR, 95.5 mph EV. Tidwell RHB split -0.31, HR risk 0.76. slight split headwind (-0.31); park/weather net drag (-14%).""", blast="good", contact={'stars': 2, 'k': 25.7, 'batterK': 33.3, 'batterWhiff': 36.2, 'pitcherK': 20.1}),
            row("Leonardo Bernal", "S", "+800", 67, "💎", ["vs Tidwell"], """Worst Pickz Hidden Gem. 0 HR, 95.0 mph EV. Tidwell SHB→LHB split +1.18, HR risk 0.76. park/weather net drag (-14%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TB @ ATL - Griffin Jax (R, TB) vs Reynaldo Lopez (R, ATL)",
        "kLines": {'Jax': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 19.3, 'matchupK': 27.6, 'ownK': 28.3}, 'Lopez': {'k': 4.1, 'lo': 3, 'hi': 6, 'bf': 20.1, 'matchupK': 20.6, 'ownK': 23.3}},
        "description": "Tail key data: Park boost -7% (stadium -2%, weather -5%). Jax (HR risk -0.08, vs LHB +0.29, vs RHB -0.54). Lopez (season BAA .245).",
        "rows": [
            row("Matt Olson", "L", "+349", 75, "⭐", ["vs Jax"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 97.3 mph EV, 12.5% barrels. Jax LHB split +0.29, HR risk -0.08. pitcher risk below avg (-0.08); park/weather net drag (-7%).""", blast="good", contact={'stars': 1, 'k': 28.5, 'batterK': 28.9, 'batterWhiff': 31.4, 'pitcherK': 28.3}),
            row("Ronald Acuna Jr.", "R", "+466", 73, "🌕 💣", ["vs Jax"], """2 HR, 2 near-HR, 91.6 mph EV, 25.0% barrels. Jax RHB split -0.54, HR risk -0.08. tough split lane (-0.54); pitcher risk below avg (-0.08).""", blast="high"),
            row("Austin Riley", "R", "+540", 66, "", ["vs Jax"], """1 HR, 1 near-HR, 96.1 mph EV, 25.0% barrels. Jax RHB split -0.54, HR risk -0.08. tough split lane (-0.54); pitcher risk below avg (-0.08).""", blast="good", contact={'stars': 1, 'k': 29.6, 'batterK': 36.0, 'batterWhiff': 29.0, 'pitcherK': 28.3}),
            row("Ozzie Albies", "S", "+700", 46, "", ["vs Jax"], """0 HR, 91.4 mph EV. Jax SHB→LHB split +0.29, HR risk -0.08. pitcher risk below avg (-0.08); park/weather net drag (-7%).""", contact={'stars': 3, 'k': 22.3, 'batterK': 16.7, 'batterWhiff': 18.2, 'pitcherK': 28.3}),
            row("Junior Caminero", "R", "+301", 89, "🌕 💣", ["vs Lopez"], """2 HR, 2 near-HR, 96.0 mph EV, 37.5% barrels. limited split/risk sample; park/weather net drag (-7%).""", blast="high", contact={'stars': 3, 'k': 20.4, 'batterK': 15.9, 'batterWhiff': 22.8, 'pitcherK': 23.3}),
            row("Yandy Diaz", "R", "+600", 71, "", ["vs Lopez"], """0 HR, 1 near-HR, 93.0 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-7%).""", blast="good", contact={'stars': 4, 'k': 18.2, 'batterK': 13.3, 'batterWhiff': 15.1, 'pitcherK': 23.3}),
            row("Jonathan Aranda", "L", "+501", 68, "", ["vs Lopez"], """0 HR, 93.2 mph EV. limited split/risk sample; park/weather net drag (-7%).""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 25.9, 'batterWhiff': 24.0, 'pitcherK': 23.3}),
        ],
    },
    {
        "title": "TEX @ SEA - Cody Bradford (L, TEX) vs Kade Anderson (L, SEA)",
        "kLines": {'Bradford': {'k': 3.6, 'lo': 2, 'hi': 5, 'bf': 22.0, 'matchupK': 16.4, 'ownK': 11.9}, 'Anderson': {'k': 4.2, 'lo': 3, 'hi': 6, 'bf': 21.5, 'matchupK': 19.7, 'ownK': 17.5}},
        "description": "Tail key data: Park boost -3% (stadium +1%, weather -4%). Bradford (HR risk 0.57, vs LHB +0.18, vs RHB +0.65). Anderson (HR risk 0.76, vs LHB +2.00, vs RHB +0.28).",
        "rows": [
            row("Dominic Canzone", "L", "+520", 71, "💎", ["vs Bradford"], """Worst Pickz Hidden Gem. 0 HR, 91.8 mph EV, 12.5% barrels. Bradford LHB split +0.18, HR risk 0.57. weather carry headwind (-4%); limited recent HR events.""", contact={'stars': 4, 'k': 19.0, 'batterK': 25.6, 'batterWhiff': 24.4, 'pitcherK': 11.9}),
            row("Cal Raleigh", "S", "+350", 69, "", ["vs Bradford"], """0 HR, 91.2 mph EV. Bradford SHB→RHB split +0.65, HR risk 0.57. weather carry headwind (-4%); limited recent HR events.""", contact={'stars': 3, 'k': 19.9, 'batterK': 25.6, 'batterWhiff': 31.0, 'pitcherK': 11.9}),
            row("Randy Arozarena", "R", "+410", 78, "", ["vs Bradford"], """1 HR, 1 near-HR, 88.3 mph EV, 12.5% barrels. Bradford RHB split +0.65, HR risk 0.57. weather carry headwind (-4%).""", blast="good", contact={'stars': 4, 'k': 19.4, 'batterK': 25.0, 'batterWhiff': 27.8, 'pitcherK': 11.9}),
            row("Brandon Nimmo", "L", "+725", 83, "", ["vs Anderson"], """0 HR, 1 near-HR, 97.6 mph EV. Anderson LHB split +2.00, HR risk 0.76. weather carry headwind (-4%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.6, 'batterK': 21.8, 'batterWhiff': 22.9, 'pitcherK': 17.5}),
            row("Corey Seager", "L", "+395", 89, "🌕 💣 💎", ["vs Anderson"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.9 mph EV, 25.0% barrels. Anderson LHB split +2.00, HR risk 0.76. weather carry headwind (-4%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.8, 'batterK': 18.2, 'batterWhiff': 29.9, 'pitcherK': 17.5}),
            row("Jake Burger", "R", "+470", 93, "🌕 💣", ["vs Anderson"], """2 HR, 2 near-HR, 93.8 mph EV, 37.5% barrels. Anderson RHB split +0.28, HR risk 0.76. weather carry headwind (-4%).""", blast="high", contact={'stars': 3, 'k': 24.0, 'batterK': 28.2, 'batterWhiff': 32.9, 'pitcherK': 17.5}),
            row("Ezequiel Duran", "R", "+820", 82, "", ["vs Anderson"], """1 HR, 1 near-HR, 91.7 mph EV, 12.5% barrels. Anderson RHB split +0.28, HR risk 0.76. weather carry headwind (-4%).""", blast="good", contact={'stars': 3, 'k': 21.6, 'batterK': 22.1, 'batterWhiff': 28.0, 'pitcherK': 17.5}),
            row("Justin Foscue", "R", "+630", 87, "", ["vs Anderson"], """1 HR, 1 near-HR, 91.7 mph EV, 12.5% barrels. Anderson RHB split +0.28, HR risk 0.76. weather carry headwind (-4%).""", blast="good", contact={'stars': 4, 'k': 18.4, 'batterK': 16.7, 'batterWhiff': 16.0, 'pitcherK': 17.5}),
        ],
    },
    {
        "title": "TOR @ ATH - Braydon Fisher (R, TOR) vs Brady Basso (L, ATH)",
        "kLines": {'Fisher': {'k': 5.5, 'lo': 4, 'hi': 7, 'bf': 21.7, 'matchupK': 25.4, 'ownK': 32.4}, 'Basso': {'k': 3.5, 'lo': 2, 'hi': 5, 'bf': 21.7, 'matchupK': 16.2, 'ownK': 13.9}},
        "description": "Tail key data: Park boost +20% (stadium +30%, weather -10%). Fisher (HR risk -0.59, vs LHB +0.04, vs RHB -0.51). Basso (HR risk -1.52, vs LHB -1.41, vs RHB -0.61).",
        "rows": [
            row("Max Muncy", "R", "+572", 88, "🌕 💣", ["vs Fisher"], """2 HR, 2 near-HR, 94.7 mph EV, 25.0% barrels. Fisher RHB split -0.51, HR risk -0.59. tough split lane (-0.51); pitcher suppresses HR (-0.59).""", blast="high", contact={'stars': 2, 'k': 24.0, 'batterK': 20.3, 'batterWhiff': 28.8, 'pitcherK': 32.4}),
            row("Lawrence Butler", "L", "+670", 84, "🚀 🌕 💣", ["vs Fisher"], """1 HR, 1 near-HR, 100.6 mph EV, 25.0% barrels. Fisher LHB split +0.04, HR risk -0.59. pitcher suppresses HR (-0.59); weather carry headwind (-10%).""", blast="high", contact={'stars': 1, 'k': 27.6, 'batterK': 34.1, 'batterWhiff': 27.6, 'pitcherK': 32.4}),
            row("Zack Gelof", "R", "+562", 80, "", ["vs Fisher"], """1 HR, 2 near-HR, 93.4 mph EV, 25.0% barrels. Fisher RHB split -0.51, HR risk -0.59. tough split lane (-0.51); pitcher suppresses HR (-0.59).""", blast="good", contact={'stars': 2, 'k': 27.0, 'batterK': 27.3, 'batterWhiff': 34.7, 'pitcherK': 32.4}),
            row("Henry Bolte", "R", "+770", 73, "🚀 💎", ["vs Fisher"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 103.8 mph EV, 12.5% barrels. Fisher RHB split -0.51, HR risk -0.59. tough split lane (-0.51); pitcher suppresses HR (-0.59).""", blast="good", contact={'stars': 1, 'k': 27.4, 'batterK': 29.5, 'batterWhiff': 32.3, 'pitcherK': 32.4}),
            row("Kazuma Okamoto", "R", "+342", 73, "⭐", ["vs Basso"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.3 mph EV, 12.5% barrels. Basso RHB split -0.61, HR risk -1.52. tough split lane (-0.61); pitcher suppresses HR (-1.52).""", blast="good", contact={'stars': 3, 'k': 20.1, 'batterK': 20.5, 'batterWhiff': 28.3, 'pitcherK': 13.9}),
            row("Vladimir Guerrero Jr.", "R", "+450", 68, "", ["vs Basso"], """1 HR, 2 near-HR, 91.6 mph EV, 25.0% barrels. Basso RHB split -0.61, HR risk -1.52. tough split lane (-0.61); pitcher suppresses HR (-1.52).""", blast="good", contact={'stars': 5, 'k': 15.2, 'batterK': 9.5, 'batterWhiff': 15.1, 'pitcherK': 13.9}),
            row("George Springer", "R", "+463", 59, "", ["vs Basso"], """1 HR, 1 near-HR, 96.8 mph EV, 12.5% barrels. Basso RHB split -0.61, HR risk -1.52. tough split lane (-0.61); pitcher suppresses HR (-1.52).""", blast="good", contact={'stars': 4, 'k': 19.1, 'batterK': 18.9, 'batterWhiff': 24.0, 'pitcherK': 13.9}),
        ],
    },
    {
        "title": "WSH @ SD - Jackson Kent (L, WSH) vs Walker Buehler (R, SD)",
        "kLines": {'Kent': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 22.0, 'matchupK': 20.5, 'ownK': 18.8}, 'Buehler': {'k': 4.0, 'lo': 2, 'hi': 6, 'bf': 20.8, 'matchupK': 19.2, 'ownK': 18.4}},
        "description": "Tail key data: Park boost +1% (stadium -6%, weather +7%). Kent (HR risk -1.04, vs LHB -0.91, vs RHB -0.67). Buehler (HR risk 0.15, vs LHB +0.17, vs RHB +0.09).",
        "rows": [
            row("Fernando Tatis Jr.", "R", "+493", 75, "", ["vs Kent"], """1 HR, 1 near-HR, 94.4 mph EV, 12.5% barrels. Kent RHB split -0.67, HR risk -1.04. tough split lane (-0.67); pitcher suppresses HR (-1.04).""", blast="good", contact={'stars': 4, 'k': 19.2, 'batterK': 17.2, 'batterWhiff': 22.4, 'pitcherK': 18.8}),
            row("Ty France", "R", "+750", 61, "", ["vs Kent"], """1 HR, 1 near-HR, 96.0 mph EV. Kent RHB split -0.67, HR risk -1.04. tough split lane (-0.67); pitcher suppresses HR (-1.04).""", blast="good", contact={'stars': 3, 'k': 20.5, 'batterK': 17.6, 'batterWhiff': 28.7, 'pitcherK': 18.8}),
            row("Manny Machado", "R", "+535", 58, "", ["vs Kent"], """1 HR, 1 near-HR, 86.3 mph EV, 12.5% barrels. Kent RHB split -0.67, HR risk -1.04. tough split lane (-0.67); pitcher suppresses HR (-1.04).""", blast="good", contact={'stars': 4, 'k': 19.7, 'batterK': 18.2, 'batterWhiff': 23.5, 'pitcherK': 18.8}),
            row("Daylen Lile", "L", "+640", 87, "🚀 🌕 💣", ["vs Buehler"], """1 HR, 1 near-HR, 100.4 mph EV, 25.0% barrels. Buehler LHB split +0.17, HR risk 0.15. park suppresses carry (-6%).""", blast="high", contact={'stars': 3, 'k': 20.8, 'batterK': 25.3, 'batterWhiff': 23.9, 'pitcherK': 18.4}),
            row("James Wood", "L", "+397", 87, "🚀 🌕 💣", ["vs Buehler"], """0 HR, 100.2 mph EV, 25.0% barrels. Buehler LHB split +0.17, HR risk 0.15. park suppresses carry (-6%); limited recent HR events.""", blast="high", contact={'stars': 4, 'k': 19.8, 'batterK': 21.5, 'batterWhiff': 23.3, 'pitcherK': 18.4}),
            row("Yohandy Morales", "R", "N/A", 78, "", ["vs Buehler"], """1 HR, 1 near-HR, 94.8 mph EV, 25.0% barrels. Buehler RHB split +0.09, HR risk 0.15. park suppresses carry (-6%).""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 50.0, 'batterWhiff': 48.5, 'pitcherK': 18.4}),
            row("Nasim Nunez", "S", "+1800", 58, "", ["vs Buehler"], """0 HR, 2 near-HR, 91.5 mph EV, 25.0% barrels. Buehler SHB→LHB split +0.17, HR risk 0.15. park suppresses carry (-6%).""", blast="good", contact={'stars': 4, 'k': 19.6, 'batterK': 20.0, 'batterWhiff': 23.3, 'pitcherK': 18.4}),
            row("Brady House", "R", "+830", 60, "", ["vs Buehler"], """0 HR, 89.4 mph EV, 12.5% barrels. Buehler RHB split +0.09, HR risk 0.15. park suppresses carry (-6%); limited recent HR events.""", contact={'stars': 4, 'k': 19.2, 'batterK': 20.0, 'batterWhiff': 21.9, 'pitcherK': 18.4}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-09")

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

    out = ROOT / '_games-0909.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
