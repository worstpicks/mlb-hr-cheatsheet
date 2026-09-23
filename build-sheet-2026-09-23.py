#!/usr/bin/env python3
"""Generate games[] block for 2026-09-23 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Kyle Schwarber (L)",
    "Munetaka Murakami (L)",
    "Vinnie Pasquantino (L)",
}

GEMS = {
    "Bobby Witt Jr. (R)",
    "Ezequiel Tovar (R)",
    "Jake Bauers (L)",
    "Josh Jung (R)",
    "Kyle Tucker (L)",
    "Michael Conforto (L)",
    "Mookie Betts (R)",
    "Pavin Smith (L)",
    "Taylor Trammell (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BOS",
    "Agustin Ramirez (R)": "MIA",
    "Alec Burleson (L)": "STL",
    "Alex Bregman (R)": "CHC",
    "Andres Chaparro (R)": "WSH",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Vaughn (R)": "MIL",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brady House (R)": "WSH",
    "Brett Baty (L)": "NYM",
    "Brice Turang (L)": "MIL",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Harper (L)": "PHI",
    "CJ Abrams (L)": "WSH",
    "Chase DeLauter (L)": "CLE",
    "Coby Mayo (R)": "BAL",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Daylen Lile (L)": "WSH",
    "Derek Hill (R)": "PHI",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Emmanuel Rodriguez (L)": "MIN",
    "Ezequiel Tovar (R)": "COL",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Gleyber Torres (R)": "DET",
    "Grant McCray (L)": "SF",
    "Griffin Conine (L)": "MIA",
    "Hao-Yu Lee (R)": "DET",
    "Henry Bolte (R)": "ATH",
    "Ivan Herrera (R)": "STL",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jake Mangum (S)": "PIT",
    "James Wood (L)": "WSH",
    "Jarren Duran (L)": "BOS",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Josh Bell (S)": "MIN",
    "Josh Jung (R)": "TEX",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kevin McGonigle (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Konnor Griffin (R)": "PIT",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Tucker (L)": "LAD",
    "Lars Nootbaar (L)": "ARI",
    "Lazaro Montes (L)": "SEA",
    "Mark Vientos (R)": "NYM",
    "Michael Busch (L)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Mickey Moniak (L)": "COL",
    "Mike Trout (R)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Nathaniel Lowe (L)": "CLE",
    "Nelson Velazquez (R)": "HOU",
    "Nolan Arenado (R)": "ARI",
    "Otto Lopez (R)": "MIA",
    "Paul Goldschmidt (R)": "NYY",
    "Pavin Smith (L)": "ARI",
    "Pete Alonso (R)": "BAL",
    "Randy Arozarena (R)": "SEA",
    "Richie Palacios (L)": "TB",
    "Riley Greene (L)": "DET",
    "Roman Anthony (L)": "BOS",
    "Royce Lewis (R)": "MIN",
    "Ryan Kreidler (R)": "MIN",
    "Sal Stewart (R)": "CIN",
    "Samuel Basallo (L)": "BAL",
    "Sean Keys (L)": "TOR",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Taylor Trammell (L)": "HOU",
    "Travis Bazzana (L)": "CLE",
    "Trevor Story (R)": "BOS",
    "Victor Bericoto (R)": "SF",
    "Vinnie Pasquantino (L)": "KC",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Will Smith (R)": "LAD",
    "Willson Contreras (R)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Xander Bogaerts (R)": "SD",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("ARI @ COL", "Adams"),
    ("STL @ PIT", "Liberatore"),
    ("TB @ NYY", "Cole"),
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
        "title": "ARI @ COL - Merrill Kelly (R, ARI) vs Mason Adams 🧤 (R, COL)",
        "kLines": {'Kelly': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 23.9, 'matchupK': 19.9, 'ownK': 19.8}, 'Adams': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 21.0, 'matchupK': 21.1, 'ownK': 22.8}},
        "description": "Tail key data: Park boost +19% (stadium +19%, weather +0%). Kelly (HR risk -0.38, vs LHB -0.14, vs RHB -0.51). Adams 🧤 (HR risk 1.90, vs LHB +1.27, vs RHB +1.37).",
        "rows": [
            row("Mickey Moniak", "L", "+430", 69, "", ["vs Kelly"], """1 HR, 1 near-HR, 91.8 mph EV, 12.5% barrels. Kelly LHB split -0.14, HR risk -0.38. slight split headwind (-0.14); pitcher risk below avg (-0.38).""", blast="good", contact={'stars': 2, 'k': 25.8, 'batterK': 35.2, 'batterWhiff': 36.8, 'pitcherK': 19.8}),
            row("Kyle Karros", "R", "+730", 61, "", ["vs Kelly"], """0 HR, 97.7 mph EV. Kelly RHB split -0.51, HR risk -0.38. tough split lane (-0.51); pitcher risk below avg (-0.38).""", blast="good", contact={'stars': 4, 'k': 19.4, 'batterK': 17.5, 'batterWhiff': 22.9, 'pitcherK': 19.8}),
            row("Ezequiel Tovar", "R", "+700", 60, "💎", ["vs Kelly"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 85.4 mph EV, 25.0% barrels. Kelly RHB split -0.51, HR risk -0.38. tough split lane (-0.51); pitcher risk below avg (-0.38).""", blast="good", contact={'stars': 3, 'k': 23.9, 'batterK': 31.0, 'batterWhiff': 33.6, 'pitcherK': 19.8}),
            row("Pavin Smith", "L", "+525", 89, "🌕 💣 💎", ["vs Adams"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 98.5 mph EV, 12.5% barrels. Adams LHB split +1.27, HR risk 1.90.""", blast="good", contact={'stars': 3, 'k': 20.7, 'batterK': 18.8, 'batterWhiff': 20.0, 'pitcherK': 22.8}),
            row("Nolan Arenado", "R", "+430", 87, "", ["vs Adams"], """1 HR, 1 near-HR, 85.5 mph EV, 12.5% barrels. Adams RHB split +1.37, HR risk 1.90. lighter EV form (85.5 mph).""", blast="good", contact={'stars': 3, 'k': 21.3, 'batterK': 16.5, 'batterWhiff': 27.8, 'pitcherK': 22.8}),
            row("Lars Nootbaar", "L", "+475", 95, "🌕 💣", ["vs Adams"], """1 HR, 1 near-HR, 95.2 mph EV, 12.5% barrels. Adams LHB split +1.27, HR risk 1.90.""", blast="good", contact={'stars': 3, 'k': 22.3, 'batterK': 25.8, 'batterWhiff': 21.4, 'pitcherK': 22.8}),
            row("Corbin Carroll", "L", "+400", 94, "🌕 💣", ["vs Adams"], """1 HR, 2 near-HR, 94.2 mph EV, 12.5% barrels. Adams LHB split +1.27, HR risk 1.90.""", blast="good", contact={'stars': 2, 'k': 24.7, 'batterK': 27.7, 'batterWhiff': 29.4, 'pitcherK': 22.8}),
        ],
    },
    {
        "title": "CIN @ ATL - Andrew Abbott (L, CIN) vs Chris Sale (L, ATL)",
        "kLines": {'Abbott': {'k': 3.9, 'lo': 2, 'hi': 6, 'bf': 22.5, 'matchupK': 17.4, 'ownK': 15.9}, 'Sale': {'k': 7.5, 'lo': 6, 'hi': 9, 'bf': 23.7, 'matchupK': 31.8, 'ownK': 33.2}},
        "description": "Tail key data: Park boost -18% (stadium -4%, weather -14%). Abbott (HR risk 0.68, vs LHB +1.84, vs RHB -0.25). Sale (HR risk -1.11, vs LHB -1.39, vs RHB -0.39).",
        "rows": [
            row("Drake Baldwin", "L", "N/A", 80, "", ["vs Abbott"], """0 HR, 1 near-HR, 99.8 mph EV. Abbott LHB split +1.84, HR risk 0.68. park/weather net drag (-18%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.1, 'batterK': 24.2, 'batterWhiff': 28.1, 'pitcherK': 15.9}),
            row("Austin Riley", "R", "N/A", 78, "🌕 💣", ["vs Abbott"], """1 HR, 1 near-HR, 98.3 mph EV, 25.0% barrels. Abbott RHB split -0.25, HR risk 0.68. slight split headwind (-0.25); park/weather net drag (-18%).""", blast="high", contact={'stars': 3, 'k': 20.8, 'batterK': 30.3, 'batterWhiff': 25.2, 'pitcherK': 15.9}),
            row("Sal Stewart", "R", "N/A", 59, "", ["vs Sale"], """1 HR, 1 near-HR, 91.2 mph EV, 12.5% barrels. Sale RHB split -0.39, HR risk -1.11. slight split headwind (-0.39); pitcher suppresses HR (-1.11).""", blast="good", contact={'stars': 1, 'k': 28.5, 'batterK': 21.7, 'batterWhiff': 26.3, 'pitcherK': 33.2}),
        ],
    },
    {
        "title": "CLE @ BOS - Foster Griffin (L, CLE) vs Sonny Gray (R, BOS)",
        "kLines": {'Griffin': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 22.9, 'matchupK': 19.9, 'ownK': 18.2}, 'Gray': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 23.3, 'matchupK': 19.6, 'ownK': 22.1}},
        "description": "Tail key data: Park boost -42% (stadium -9%, weather -33%). Griffin (HR risk -1.11, vs LHB -0.60, vs RHB -0.65). Gray (HR risk -0.29, vs LHB -0.29, vs RHB -0.11).",
        "rows": [
            row("Roman Anthony", "L", "+950", 65, "🌕 💣", ["vs Griffin"], """1 HR, 1 near-HR, 97.8 mph EV, 25.0% barrels. Griffin LHB split -0.60, HR risk -1.11. tough split lane (-0.60); pitcher suppresses HR (-1.11).""", blast="high", contact={'stars': 3, 'k': 23.1, 'batterK': 29.8, 'batterWhiff': 29.1, 'pitcherK': 18.2}),
            row("Adley Rutschman", "S", "+1040", 40, "", ["vs Griffin"], """0 HR, 90.2 mph EV. Griffin SHB→RHB split -0.65, HR risk -1.11. tough split lane (-0.65); pitcher suppresses HR (-1.11).""", contact={'stars': 4, 'k': 17.9, 'batterK': 19.2, 'batterWhiff': 16.1, 'pitcherK': 18.2}),
            row("Willson Contreras", "R", "+450", 47, "", ["vs Griffin"], """0 HR, 89.8 mph EV. Griffin RHB split -0.65, HR risk -1.11. tough split lane (-0.65); pitcher suppresses HR (-1.11).""", contact={'stars': 3, 'k': 20.6, 'batterK': 23.3, 'batterWhiff': 25.9, 'pitcherK': 18.2}),
            row("Jarren Duran", "L", "N/A", 51, "", ["vs Griffin"], """1 HR, 1 near-HR, 87.6 mph EV, 25.0% barrels. Griffin LHB split -0.60, HR risk -1.11. tough split lane (-0.60); pitcher suppresses HR (-1.11).""", blast="good", contact={'stars': 3, 'k': 21.5, 'batterK': 22.4, 'batterWhiff': 31.8, 'pitcherK': 18.2}),
            row("Trevor Story", "R", "+950", 47, "", ["vs Griffin"], """1 HR, 1 near-HR, 85.8 mph EV, 12.5% barrels. Griffin RHB split -0.65, HR risk -1.11. tough split lane (-0.65); pitcher suppresses HR (-1.11).""", blast="good", contact={'stars': 3, 'k': 22.9, 'batterK': 30.0, 'batterWhiff': 30.1, 'pitcherK': 18.2}),
            row("Nathaniel Lowe", "L", "+930", 61, "", ["vs Gray"], """0 HR, 1 near-HR, 95.6 mph EV. Gray LHB split -0.29, HR risk -0.29. slight split headwind (-0.29); pitcher risk below avg (-0.29).""", blast="good", contact={'stars': 3, 'k': 21.6, 'batterK': 20.6, 'batterWhiff': 23.7, 'pitcherK': 22.1}),
            row("Chase DeLauter", "L", "+900", 55, "", ["vs Gray"], """0 HR, 93.2 mph EV. Gray LHB split -0.29, HR risk -0.29. slight split headwind (-0.29); pitcher risk below avg (-0.29).""", blast="good", contact={'stars': 4, 'k': 17.5, 'batterK': 13.9, 'batterWhiff': 11.5, 'pitcherK': 22.1}),
            row("Travis Bazzana", "L", "+1040", 75, "🌕 💣", ["vs Gray"], """2 HR, 2 near-HR, 93.5 mph EV, 25.0% barrels. Gray LHB split -0.29, HR risk -0.29. slight split headwind (-0.29); pitcher risk below avg (-0.29).""", blast="high", contact={'stars': 4, 'k': 19.7, 'batterK': 16.2, 'batterWhiff': 19.4, 'pitcherK': 22.1}),
        ],
    },
    {
        "title": "CWS @ KC - Erick Fedde (R, CWS) vs Seth Lugo (R, KC)",
        "kLines": {'Fedde': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 20.7, 'matchupK': 21.9, 'ownK': None}, 'Lugo': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 23.3, 'matchupK': 19.0, 'ownK': 15.9}},
        "description": "Tail key data: Park boost -7% (stadium +13%, weather -20%). Fedde (BAA vs LHB .243, vs RHB .266, HR/9 0.86 vs LHB, 2.24 vs RHB). Lugo (HR risk 0.92, vs LHB +1.30, vs RHB -0.24).",
        "rows": [
            row("Bobby Witt Jr.", "R", "N/A", 53, "💎", ["vs Fedde"], """Worst Pickz Hidden Gem. 0 HR, 86.5 mph EV. limited split/risk sample; park/weather net drag (-7%).""", contact={'stars': 3, 'k': 20.3, 'batterK': 15.9, 'batterWhiff': 24.7, 'pitcherK': None}),
            row("Vinnie Pasquantino", "L", "N/A", 62, "⭐", ["vs Fedde"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 91.3 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-7%).""", contact={'stars': 4, 'k': 18.0, 'batterK': 13.8, 'batterWhiff': 14.3, 'pitcherK': None}),
            row("Munetaka Murakami", "L", "N/A", 96, "⭐ 🌕 💣", ["vs Lugo"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.6 mph EV, 25.0% barrels. Lugo LHB split +1.30, HR risk 0.92. park/weather net drag (-7%).""", blast="high", contact={'stars': 1, 'k': 28.4, 'batterK': 46.4, 'batterWhiff': 45.8, 'pitcherK': 15.9}),
            row("Andrew Benintendi", "L", "N/A", 78, "", ["vs Lugo"], """0 HR, 93.9 mph EV, 12.5% barrels. Lugo LHB split +1.30, HR risk 0.92. park/weather net drag (-7%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.6, 'batterK': 24.6, 'batterWhiff': 21.4, 'pitcherK': 15.9}),
        ],
    },
    {
        "title": "HOU @ SEA - Ethan Pecko (R, HOU) vs George Kirby (R, SEA)",
        "kLines": {'Pecko': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 20.7, 'matchupK': 18.3, 'ownK': 16.4}, 'Kirby': {'k': 4.2, 'lo': 3, 'hi': 6, 'bf': 24.2, 'matchupK': 17.5, 'ownK': 16.2}},
        "description": "Tail key data: Park boost -9% (stadium +1%, weather -10%). Pecko (HR risk 0.71, vs LHB +1.21, vs RHB -0.98). Kirby (HR risk -0.40, vs LHB -0.14, vs RHB -0.48).",
        "rows": [
            row("Lazaro Montes", "L", "+620", 89, "🌕 💣", ["vs Pecko"], """2 HR, 2 near-HR, 93.3 mph EV, 25.0% barrels. Pecko LHB split +1.21, HR risk 0.71. park/weather net drag (-9%).""", blast="high", contact={'stars': 2, 'k': 26.5, 'batterK': 45.7, 'batterWhiff': 47.0, 'pitcherK': 16.4}),
            row("Dominic Canzone", "L", "+458", 81, "", ["vs Pecko"], """0 HR, 1 near-HR, 92.9 mph EV, 12.5% barrels. Pecko LHB split +1.21, HR risk 0.71. park/weather net drag (-9%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.6, 'batterK': 17.8, 'batterWhiff': 23.5, 'pitcherK': 16.4}),
            row("Randy Arozarena", "R", "+561", 69, "", ["vs Pecko"], """0 HR, 1 near-HR, 96.0 mph EV. Pecko RHB split -0.98, HR risk 0.71. tough split lane (-0.98); park/weather net drag (-9%).""", blast="good", contact={'stars': 4, 'k': 19.1, 'batterK': 19.8, 'batterWhiff': 23.2, 'pitcherK': 16.4}),
            row("Yordan Alvarez", "L", "N/A", 77, "", ["vs Kirby"], """1 HR, 1 near-HR, 91.0 mph EV, 12.5% barrels. Kirby LHB split -0.14, HR risk -0.40. slight split headwind (-0.14); pitcher suppresses HR (-0.40).""", blast="good", contact={'stars': 5, 'k': 16.6, 'batterK': 15.5, 'batterWhiff': 20.0, 'pitcherK': 16.2}),
            row("Nelson Velazquez", "R", "N/A", 70, "🌕 💣", ["vs Kirby"], """0 HR, 1 near-HR, 97.6 mph EV, 25.0% barrels. Kirby RHB split -0.48, HR risk -0.40. tough split lane (-0.48); pitcher suppresses HR (-0.40).""", blast="high", contact={'stars': 3, 'k': 22.9, 'batterK': 38.9, 'batterWhiff': 41.8, 'pitcherK': 16.2}),
            row("Taylor Trammell", "L", "N/A", 69, "💎", ["vs Kirby"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.2 mph EV, 12.5% barrels. Kirby LHB split -0.14, HR risk -0.40. slight split headwind (-0.14); pitcher suppresses HR (-0.40).""", blast="good", contact={'stars': 3, 'k': 21.9, 'batterK': 26.2, 'batterWhiff': 37.0, 'pitcherK': 16.2}),
        ],
    },
    {
        "title": "LAA @ ATH - Walbert Urena (R, LAA) vs Jeffrey Springs (L, ATH)",
        "kLines": {'Urena': {'k': 5.6, 'lo': 4, 'hi': 7, 'bf': 22.5, 'matchupK': 24.8, 'ownK': 25.1}, 'Springs': {'k': 4.1, 'lo': 3, 'hi': 6, 'bf': 21.8, 'matchupK': 18.9, 'ownK': 14.1}},
        "description": "Tail key data: Park boost +27% (stadium +31%, weather -4%). Urena (HR risk -1.21, vs LHB -1.13, vs RHB -0.32). Springs (HR risk 0.16, vs LHB +0.38, vs RHB +0.00).",
        "rows": [
            row("Henry Bolte", "R", "+810", 54, "", ["vs Urena"], """0 HR, 91.2 mph EV. Urena RHB split -0.32, HR risk -1.21. slight split headwind (-0.32); pitcher suppresses HR (-1.21).""", contact={'stars': 1, 'k': 27.6, 'batterK': 31.1, 'batterWhiff': 30.5, 'pitcherK': 25.1}),
            row("Zack Gelof", "R", "+522", 72, "", ["vs Urena"], """0 HR, 2 near-HR, 93.4 mph EV, 37.5% barrels. Urena RHB split -0.32, HR risk -1.21. slight split headwind (-0.32); pitcher suppresses HR (-1.21).""", blast="good", contact={'stars': 2, 'k': 24.8, 'batterK': 22.4, 'batterWhiff': 30.2, 'pitcherK': 25.1}),
            row("Zach Neto", "R", "+306", 84, "", ["vs Springs"], """1 HR, 1 near-HR, 94.6 mph EV, 12.5% barrels. Springs RHB split +0.00, HR risk 0.16. weather carry headwind (-4%).""", blast="good", contact={'stars': 3, 'k': 21.9, 'batterK': 32.2, 'batterWhiff': 31.9, 'pitcherK': 14.1}),
            row("Mike Trout", "R", "+315", 77, "", ["vs Springs"], """0 HR, 92.2 mph EV, 25.0% barrels. Springs RHB split +0.00, HR risk 0.16. weather carry headwind (-4%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 29.5, 'batterWhiff': 32.1, 'pitcherK': 14.1}),
        ],
    },
    {
        "title": "MIA @ CHC - Ryan Gusto (R, MIA) vs Kevin Gausman (R, CHC)",
        "kLines": {'Gusto': {'k': 3.5, 'lo': 2, 'hi': 5, 'bf': 20.1, 'matchupK': 17.6, 'ownK': 17.4}, 'Gausman': {'k': 5.6, 'lo': 4, 'hi': 7, 'bf': 23.2, 'matchupK': 24.1, 'ownK': 25.3}},
        "description": "Tail key data: Park boost -32% (stadium -2%, weather -30%). Gusto (HR risk 0.15, vs LHB +0.27, vs RHB -0.04). Gausman (HR risk 0.55, vs LHB -0.84, vs RHB +1.79).",
        "rows": [
            row("Michael Conforto", "L", "+810", 75, "💎", ["vs Gusto"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.6 mph EV, 25.0% barrels. Gusto LHB split +0.27, HR risk 0.15. park/weather net drag (-32%).""", blast="good", contact={'stars': 4, 'k': 18.6, 'batterK': 17.5, 'batterWhiff': 22.0, 'pitcherK': 17.4}),
            row("Alex Bregman", "R", "N/A", 57, "", ["vs Gusto"], """0 HR, 91.1 mph EV, 12.5% barrels. Gusto RHB split -0.04, HR risk 0.15. slight split headwind (-0.04); park/weather net drag (-32%).""", contact={'stars': 5, 'k': 14.2, 'batterK': 7.2, 'batterWhiff': 13.4, 'pitcherK': 17.4}),
            row("Michael Busch", "L", "+750", 50, "", ["vs Gusto"], """0 HR, 85.1 mph EV. Gusto LHB split +0.27, HR risk 0.15. park/weather net drag (-32%); limited recent HR events.""", contact={'stars': 3, 'k': 19.9, 'batterK': 23.8, 'batterWhiff': 23.4, 'pitcherK': 17.4}),
            row("Otto Lopez", "R", "+1050", 86, "", ["vs Gausman"], """1 HR, 3 near-HR, 95.4 mph EV, 25.0% barrels. Gausman RHB split +1.79, HR risk 0.55. park/weather net drag (-32%).""", blast="good", contact={'stars': 3, 'k': 21.1, 'batterK': 14.3, 'batterWhiff': 24.0, 'pitcherK': 25.3}),
            row("Agustin Ramirez", "R", "+860", 87, "🚀 🌕 💣", ["vs Gausman"], """2 HR, 2 near-HR, 101.1 mph EV, 25.0% barrels. Gausman RHB split +1.79, HR risk 0.55. park/weather net drag (-32%).""", blast="high", contact={'stars': 2, 'k': 25.6, 'batterK': 28.8, 'batterWhiff': 28.2, 'pitcherK': 25.3}),
            row("Griffin Conine", "L", "+740", 90, "🌕 💣", ["vs Gausman"], """3 HR, 4 near-HR, 94.2 mph EV, 50.0% barrels. Gausman LHB split -0.84, HR risk 0.55. tough split lane (-0.84); park/weather net drag (-32%).""", blast="high", contact={'stars': 2, 'k': 26.4, 'batterK': 26.0, 'batterWhiff': 32.7, 'pitcherK': 25.3}),
        ],
    },
    {
        "title": "MIL @ PHI - Logan Henderson (R, MIL) vs Aaron Nola (R, PHI)",
        "kLines": {'Henderson': {'k': 5.8, 'lo': 4, 'hi': 7, 'bf': 20.8, 'matchupK': 27.8, 'ownK': 31.2}, 'Nola': {'k': 5.6, 'lo': 4, 'hi': 7, 'bf': 22.8, 'matchupK': 24.7, 'ownK': 23.8}},
        "description": "Tail key data: Park boost -20% (stadium +15%, weather -34%). Henderson (HR risk 0.22, vs LHB +0.39, vs RHB -0.20). Nola (HR risk -0.01, vs LHB -0.03, vs RHB -0.05).",
        "rows": [
            row("Kyle Schwarber", "L", "+284", 79, "⭐", ["vs Henderson"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.8 mph EV, 12.5% barrels. Henderson LHB split +0.39, HR risk 0.22. park/weather net drag (-20%).""", blast="good", contact={'stars': 1, 'k': 28.7, 'batterK': 25.6, 'batterWhiff': 26.8, 'pitcherK': 31.2}),
            row("Derek Hill", "R", "N/A", 74, "", ["vs Henderson"], """1 HR, 2 near-HR, 93.9 mph EV, 12.5% barrels. Henderson RHB split -0.20, HR risk 0.22. slight split headwind (-0.20); park/weather net drag (-20%).""", blast="good", contact={'stars': 2, 'k': 26.3, 'batterK': 16.1, 'batterWhiff': 22.4, 'pitcherK': 31.2}),
            row("Bryce Harper", "L", "+487", 58, "", ["vs Henderson"], """0 HR, 88.8 mph EV. Henderson LHB split +0.39, HR risk 0.22. park/weather net drag (-20%); limited recent HR events.""", contact={'stars': 1, 'k': 30.6, 'batterK': 25.9, 'batterWhiff': 35.6, 'pitcherK': 31.2}),
            row("Jackson Chourio", "R", "+520", 48, "", ["vs Nola"], """0 HR, 89.3 mph EV. Nola RHB split -0.05, HR risk -0.01. slight split headwind (-0.05); pitcher risk below avg (-0.01).""", contact={'stars': 2, 'k': 24.5, 'batterK': 24.0, 'batterWhiff': 29.8, 'pitcherK': 23.8}),
            row("Brice Turang", "L", "+880", 67, "", ["vs Nola"], """1 HR, 1 near-HR, 94.9 mph EV, 12.5% barrels. Nola LHB split -0.03, HR risk -0.01. slight split headwind (-0.03); pitcher risk below avg (-0.01).""", blast="good", contact={'stars': 2, 'k': 25.1, 'batterK': 27.4, 'batterWhiff': 28.2, 'pitcherK': 23.8}),
            row("Jake Bauers", "L", "+450", 72, "💎", ["vs Nola"], """Worst Pickz Hidden Gem. 0 HR, 94.3 mph EV, 25.0% barrels. Nola LHB split -0.03, HR risk -0.01. slight split headwind (-0.03); pitcher risk below avg (-0.01).""", blast="good", contact={'stars': 1, 'k': 27.8, 'batterK': 30.0, 'batterWhiff': 38.8, 'pitcherK': 23.8}),
            row("Andrew Vaughn", "R", "N/A", 49, "", ["vs Nola"], """0 HR, 1 near-HR, 91.6 mph EV. Nola RHB split -0.05, HR risk -0.01. slight split headwind (-0.05); pitcher risk below avg (-0.01).""", contact={'stars': 3, 'k': 21.0, 'batterK': 21.7, 'batterWhiff': 15.5, 'pitcherK': 23.8}),
        ],
    },
    {
        "title": "MIN @ SF - Connor Prielipp (L, MIN) vs Cesar Perdomo (L, SF)",
        "kLines": {'Prielipp': {'k': 5.6, 'lo': 4, 'hi': 7, 'bf': 22.5, 'matchupK': 24.9, 'ownK': 24.7}, 'Perdomo': {'k': 3.9, 'lo': 2, 'hi': 5, 'bf': 22.0, 'matchupK': 17.6, 'ownK': 14.5}},
        "description": "Tail key data: Park boost -16% (stadium -12%, weather -4%). Prielipp (HR risk -0.95, vs LHB -0.28, vs RHB -0.62). Perdomo (HR risk 0.07, vs LHB +0.83, vs RHB -0.39).",
        "rows": [
            row("Victor Bericoto", "R", "+830", 73, "", ["vs Prielipp"], """1 HR, 2 near-HR, 96.2 mph EV, 25.0% barrels. Prielipp RHB split -0.62, HR risk -0.95. tough split lane (-0.62); pitcher suppresses HR (-0.95).""", blast="good", contact={'stars': 2, 'k': 26.1, 'batterK': 27.5, 'batterWhiff': 31.8, 'pitcherK': 24.7}),
            row("Grant McCray", "L", "N/A", 43, "", ["vs Prielipp"], """0 HR, 82.1 mph EV, 12.5% barrels. Prielipp LHB split -0.28, HR risk -0.95. slight split headwind (-0.28); pitcher suppresses HR (-0.95).""", contact={'stars': 1, 'k': 27.5, 'batterK': 34.8, 'batterWhiff': 37.2, 'pitcherK': 24.7}),
            row("Ryan Kreidler", "R", "+910", 78, "🌕 💣", ["vs Perdomo"], """2 HR, 2 near-HR, 97.5 mph EV, 25.0% barrels. Perdomo RHB split -0.39, HR risk 0.07. slight split headwind (-0.39); park/weather net drag (-16%).""", blast="high", contact={'stars': 3, 'k': 21.9, 'batterK': 28.9, 'batterWhiff': 32.1, 'pitcherK': 14.5}),
            row("Josh Bell", "S", "+600", 46, "", ["vs Perdomo"], """0 HR, 85.6 mph EV. Perdomo SHB→RHB split -0.39, HR risk 0.07. slight split headwind (-0.39); park/weather net drag (-16%).""", contact={'stars': 4, 'k': 18.2, 'batterK': 17.6, 'batterWhiff': 21.4, 'pitcherK': 14.5}),
            row("Royce Lewis", "R", "+550", 46, "", ["vs Perdomo"], """0 HR, 87.5 mph EV. Perdomo RHB split -0.39, HR risk 0.07. slight split headwind (-0.39); park/weather net drag (-16%).""", contact={'stars': 3, 'k': 22.4, 'batterK': 27.2, 'batterWhiff': 31.8, 'pitcherK': 14.5}),
            row("Kody Clemens", "L", "+505", 54, "", ["vs Perdomo"], """0 HR, 87.6 mph EV. Perdomo LHB split +0.83, HR risk 0.07. park/weather net drag (-16%); limited recent HR events.""", contact={'stars': 4, 'k': 18.7, 'batterK': 19.8, 'batterWhiff': 21.1, 'pitcherK': 14.5}),
            row("Emmanuel Rodriguez", "L", "+680", 59, "", ["vs Perdomo"], """0 HR, 90.5 mph EV. Perdomo LHB split +0.83, HR risk 0.07. park/weather net drag (-16%); limited recent HR events.""", contact={'stars': 3, 'k': 22.6, 'batterK': 35.0, 'batterWhiff': 33.8, 'pitcherK': 14.5}),
        ],
    },
    {
        "title": "NYM @ TEX - Nolan McLean (R, NYM) vs Cody Bradford (L, TEX)",
        "kLines": {'McLean': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 23.7, 'matchupK': 22.3, 'ownK': 21.3}, 'Bradford': {'k': 3.3, 'lo': 2, 'hi': 5, 'bf': 21.7, 'matchupK': 15.1, 'ownK': 11.8}},
        "description": "Tail key data: Park boost -11% (stadium -11%, weather -1%). McLean (HR risk -0.98, vs LHB -0.53, vs RHB -1.19). Bradford (BAA vs LHB .375, vs RHB .267, HR/9 0.93).",
        "rows": [
            row("Josh Jung", "R", "+930", 78, "🌕 💣 💎", ["vs McLean"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 95.3 mph EV, 25.0% barrels. McLean RHB split -1.19, HR risk -0.98. tough split lane (-1.19); pitcher suppresses HR (-0.98).""", blast="high", contact={'stars': 4, 'k': 19.8, 'batterK': 20.0, 'batterWhiff': 18.0, 'pitcherK': 21.3}),
            row("Wyatt Langford", "R", "+560", 62, "", ["vs McLean"], """1 HR, 2 near-HR, 94.7 mph EV, 37.5% barrels. McLean RHB split -1.19, HR risk -0.98. tough split lane (-1.19); pitcher suppresses HR (-0.98).""", blast="good", contact={'stars': 2, 'k': 24.5, 'batterK': 28.2, 'batterWhiff': 31.4, 'pitcherK': 21.3}),
            row("Juan Soto", "L", "+420", 86, "", ["vs Bradford"], """1 HR, 3 near-HR, 95.0 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-11%).""", blast="good", contact={'stars': 5, 'k': 15.6, 'batterK': 16.5, 'batterWhiff': 21.2, 'pitcherK': 11.8}),
            row("Francisco Alvarez", "R", "+530", 86, "🚀 🌕 💣", ["vs Bradford"], """1 HR, 2 near-HR, 102.7 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-11%).""", blast="high", contact={'stars': 3, 'k': 22.5, 'batterK': 37.8, 'batterWhiff': 36.5, 'pitcherK': 11.8}),
            row("Mark Vientos", "R", "+600", 89, "🌕 💣", ["vs Bradford"], """3 HR, 3 near-HR, 93.6 mph EV, 37.5% barrels. limited split/risk sample; park/weather net drag (-11%).""", blast="high", contact={'stars': 4, 'k': 19.4, 'batterK': 26.3, 'batterWhiff': 32.3, 'pitcherK': 11.8}),
            row("Francisco Lindor", "S", "+480", 64, "", ["vs Bradford"], """0 HR, 93.4 mph EV. limited split/risk sample; park/weather net drag (-11%).""", blast="good", contact={'stars': 4, 'k': 18.3, 'batterK': 24.5, 'batterWhiff': 25.9, 'pitcherK': 11.8}),
            row("Brett Baty", "L", "N/A", 56, "", ["vs Bradford"], """0 HR, 1 near-HR, 90.6 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-11%).""", contact={'stars': 4, 'k': 19.3, 'batterK': 21.1, 'batterWhiff': 35.5, 'pitcherK': 11.8}),
        ],
    },
    {
        "title": "SD @ LAD - Robbie Ray (L, SD) vs Yoshinobu Yamamoto (R, LAD)",
        "kLines": {'Ray': {'k': 4.1, 'lo': 3, 'hi': 6, 'bf': 22.6, 'matchupK': 18.3, 'ownK': 19.1}, 'Yamamoto': {'k': 6.4, 'lo': 5, 'hi': 8, 'bf': 24.6, 'matchupK': 26.2, 'ownK': 28.0}},
        "description": "Tail key data: Park boost +24% (stadium +19%, weather +4%). Ray (HR risk -0.05, vs LHB -0.98, vs RHB +0.51). Yamamoto (HR risk -0.48, vs LHB -0.40, vs RHB -0.30).",
        "rows": [
            row("Mookie Betts", "R", "+450", 89, "🌕 💣 💎", ["vs Ray"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.3 mph EV, 25.0% barrels. Ray RHB split +0.51, HR risk -0.05. pitcher risk below avg (-0.05).""", blast="high", contact={'stars': 5, 'k': 14.1, 'batterK': 7.5, 'batterWhiff': 11.3, 'pitcherK': 19.1}),
            row("Kyle Tucker", "L", "+545", 82, "🌕 💣 💎", ["vs Ray"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.1 mph EV, 25.0% barrels. Ray LHB split -0.98, HR risk -0.05. tough split lane (-0.98); pitcher risk below avg (-0.05).""", blast="high", contact={'stars': 5, 'k': 15.3, 'batterK': 9.0, 'batterWhiff': 12.6, 'pitcherK': 19.1}),
            row("Will Smith", "R", "+390", 80, "🌕 💣", ["vs Ray"], """2 HR, 2 near-HR, 84.7 mph EV, 25.0% barrels. Ray RHB split +0.51, HR risk -0.05. pitcher risk below avg (-0.05); lighter EV form (84.7 mph).""", blast="high", contact={'stars': 4, 'k': 18.1, 'batterK': 15.7, 'batterWhiff': 18.7, 'pitcherK': 19.1}),
            row("Jackson Merrill", "L", "+520", 72, "", ["vs Yamamoto"], """0 HR, 1 near-HR, 95.4 mph EV. Yamamoto LHB split -0.40, HR risk -0.48. tough split lane (-0.40); pitcher suppresses HR (-0.48).""", blast="good", contact={'stars': 2, 'k': 26.2, 'batterK': 20.9, 'batterWhiff': 29.8, 'pitcherK': 28.0}),
            row("Xander Bogaerts", "R", "+860", 76, "", ["vs Yamamoto"], """1 HR, 2 near-HR, 95.4 mph EV, 12.5% barrels. Yamamoto RHB split -0.30, HR risk -0.48. slight split headwind (-0.30); pitcher suppresses HR (-0.48).""", blast="good", contact={'stars': 2, 'k': 25.3, 'batterK': 20.5, 'batterWhiff': 25.8, 'pitcherK': 28.0}),
            row("Fernando Tatis Jr.", "R", "+441", 86, "🌕 💣", ["vs Yamamoto"], """2 HR, 2 near-HR, 88.3 mph EV, 25.0% barrels. Yamamoto RHB split -0.30, HR risk -0.48. slight split headwind (-0.30); pitcher suppresses HR (-0.48).""", blast="high", contact={'stars': 3, 'k': 23.6, 'batterK': 18.5, 'batterWhiff': 21.4, 'pitcherK': 28.0}),
        ],
    },
    {
        "title": "STL @ PIT - Matthew Liberatore 🧤 (L, STL) vs Lake Bachar (R, PIT)",
        "kLines": {'Liberatore': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 21.7, 'matchupK': 23.7, 'ownK': 24.7}, 'Bachar': {'k': 2.0, 'lo': 0, 'hi': 4, 'bf': 8.4, 'matchupK': 23.6, 'ownK': 25.3}},
        "description": "Tail key data: Park boost -34% (stadium -16%, weather -18%). Liberatore 🧤 (HR risk 0.96, vs LHB -0.45, vs RHB +1.48). Bachar (HR risk -0.90, vs LHB -0.69, vs RHB +0.10).",
        "rows": [
            row("Jake Mangum", "S", "+2200", 74, "", ["vs Liberatore"], """1 HR, 1 near-HR, 91.1 mph EV, 12.5% barrels. Liberatore SHB→RHB split +1.48, HR risk 0.96. park/weather net drag (-34%).""", blast="good", contact={'stars': 3, 'k': 20.5, 'batterK': 15.1, 'batterWhiff': 18.7, 'pitcherK': 24.7}),
            row("Bryan Reynolds", "S", "+850", 77, "", ["vs Liberatore"], """0 HR, 88.8 mph EV, 12.5% barrels. Liberatore SHB→RHB split +1.48, HR risk 0.96. park/weather net drag (-34%); limited recent HR events.""", contact={'stars': 3, 'k': 22.1, 'batterK': 18.2, 'batterWhiff': 24.0, 'pitcherK': 24.7}),
            row("Konnor Griffin", "R", "+930", 59, "", ["vs Liberatore"], """0 HR, 89.5 mph EV. Liberatore RHB split +1.48, HR risk 0.96. park/weather net drag (-34%); limited recent HR events.""", contact={'stars': 3, 'k': 22.3, 'batterK': 19.8, 'batterWhiff': 22.9, 'pitcherK': 24.7}),
            row("Ivan Herrera", "R", "+890", 56, "", ["vs Bachar"], """1 HR, 1 near-HR, 90.0 mph EV, 12.5% barrels. Bachar RHB split +0.10, HR risk -0.90. pitcher suppresses HR (-0.90); park/weather net drag (-34%).""", blast="good", contact={'stars': 3, 'k': 22.9, 'batterK': 22.5, 'batterWhiff': 24.0, 'pitcherK': 25.3}),
            row("Alec Burleson", "L", "+725", 55, "", ["vs Bachar"], """0 HR, 97.2 mph EV. Bachar LHB split -0.69, HR risk -0.90. tough split lane (-0.69); pitcher suppresses HR (-0.90).""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 23.2, 'batterWhiff': 25.1, 'pitcherK': 25.3}),
            row("Jordan Walker", "R", "+600", 61, "", ["vs Bachar"], """0 HR, 93.5 mph EV, 12.5% barrels. Bachar RHB split +0.10, HR risk -0.90. pitcher suppresses HR (-0.90); park/weather net drag (-34%).""", blast="good", contact={'stars': 1, 'k': 29.9, 'batterK': 38.0, 'batterWhiff': 39.6, 'pitcherK': 25.3}),
        ],
    },
    {
        "title": "TB @ NYY - Ian Seymour (L, TB) vs Gerrit Cole 🧤 (R, NYY)",
        "kLines": {'Seymour': {'k': 5.9, 'lo': 4, 'hi': 8, 'bf': 20.8, 'matchupK': 28.4, 'ownK': 30.3}, 'Cole': {'k': 4.9, 'lo': 3, 'hi': 7, 'bf': 23.2, 'matchupK': 21.2, 'ownK': 23.6}},
        "description": "Tail key data: Park boost -28% (stadium +12%, weather -40%). Seymour (HR risk 0.90, vs LHB +0.64, vs RHB +0.74). Cole 🧤 (HR risk 1.24, vs LHB +0.69, vs RHB +1.14).",
        "rows": [
            row("Spencer Jones", "L", "+567", 87, "", ["vs Seymour"], """1 HR, 1 near-HR, 95.8 mph EV, 12.5% barrels. Seymour LHB split +0.64, HR risk 0.90. park/weather net drag (-28%).""", blast="good", contact={'stars': 1, 'k': 34.3, 'batterK': 38.0, 'batterWhiff': 41.5, 'pitcherK': 30.3}),
            row("Paul Goldschmidt", "R", "+620", 83, "", ["vs Seymour"], """1 HR, 1 near-HR, 95.1 mph EV, 12.5% barrels. Seymour RHB split +0.74, HR risk 0.90. park/weather net drag (-28%).""", blast="good", contact={'stars': 2, 'k': 24.5, 'batterK': 15.7, 'batterWhiff': 20.4, 'pitcherK': 30.3}),
            row("Ben Rice", "L", "+470", 77, "", ["vs Seymour"], """1 HR, 1 near-HR, 87.0 mph EV, 12.5% barrels. Seymour LHB split +0.64, HR risk 0.90. park/weather net drag (-28%); lighter EV form (87.0 mph).""", blast="good", contact={'stars': 2, 'k': 25.0, 'batterK': 20.0, 'batterWhiff': 21.4, 'pitcherK': 30.3}),
            row("Jonathan Aranda", "L", "+568", 98, "🌕 💣", ["vs Cole"], """3 HR, 3 near-HR, 92.6 mph EV, 25.0% barrels. Cole LHB split +0.69, HR risk 1.24. park/weather net drag (-28%).""", blast="high", contact={'stars': 2, 'k': 24.8, 'batterK': 28.0, 'batterWhiff': 26.3, 'pitcherK': 23.6}),
            row("Yandy Diaz", "R", "+850", 81, "", ["vs Cole"], """0 HR, 1 near-HR, 94.2 mph EV. Cole RHB split +1.14, HR risk 1.24. park/weather net drag (-28%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.4, 'batterK': 17.6, 'batterWhiff': 18.4, 'pitcherK': 23.6}),
            row("Richie Palacios", "L", "+1140", 73, "", ["vs Cole"], """0 HR, 95.2 mph EV. Cole LHB split +0.69, HR risk 1.24. park/weather net drag (-28%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.7, 'batterK': 10.3, 'batterWhiff': 18.4, 'pitcherK': 23.6}),
            row("Junior Caminero", "R", "+420", 90, "🌕 💣", ["vs Cole"], """2 HR, 2 near-HR, 88.9 mph EV, 12.5% barrels. Cole RHB split +1.14, HR risk 1.24. park/weather net drag (-28%).""", blast="high", contact={'stars': 3, 'k': 21.0, 'batterK': 19.3, 'batterWhiff': 18.9, 'pitcherK': 23.6}),
        ],
    },
    {
        "title": "TOR @ BAL (G1) - Max Scherzer (R, TOR) vs Chris Bassitt (R, BAL)",
        "kLines": {'Scherzer': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 20.2, 'matchupK': 21.2, 'ownK': 18.8}, 'Bassitt': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 22.8, 'matchupK': 17.8, 'ownK': 17.8}},
        "description": "Tail key data: Park boost -23% (stadium -4%, weather -19%). Scherzer (HR risk 0.18, vs LHB +0.23, vs RHB +0.10). Bassitt (BAA vs LHB .310, vs RHB .264, HR/9 0.93).",
        "rows": [
            row("Pete Alonso", "R", "+332", 83, "🌕 💣", ["vs Scherzer"], """2 HR, 2 near-HR, 83.9 mph EV, 25.0% barrels. Scherzer RHB split +0.10, HR risk 0.18. park/weather net drag (-23%); lighter EV form (83.9 mph).""", blast="high", contact={'stars': 3, 'k': 20.0, 'batterK': 22.7, 'batterWhiff': 21.6, 'pitcherK': 18.8}),
            row("Samuel Basallo", "L", "+425", 59, "", ["vs Scherzer"], """0 HR, 93.4 mph EV. Scherzer LHB split +0.23, HR risk 0.18. park/weather net drag (-23%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 23.5, 'batterWhiff': 27.5, 'pitcherK': 18.8}),
            row("Colton Cowser", "L", "+700", 55, "", ["vs Scherzer"], """0 HR, 90.5 mph EV. Scherzer LHB split +0.23, HR risk 0.18. park/weather net drag (-23%); limited recent HR events.""", contact={'stars': 2, 'k': 24.3, 'batterK': 40.7, 'batterWhiff': 30.6, 'pitcherK': 18.8}),
            row("Coby Mayo", "R", "+420", 60, "", ["vs Scherzer"], """0 HR, 93.7 mph EV. Scherzer RHB split +0.10, HR risk 0.18. park/weather net drag (-23%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.0, 'batterK': 20.3, 'batterWhiff': 25.0, 'pitcherK': 18.8}),
            row("Sean Keys", "L", "+590", 73, "", ["vs Bassitt"], """1 HR, 1 near-HR, 92.5 mph EV, 37.5% barrels. limited split/risk sample; park/weather net drag (-23%).""", blast="good", contact={'stars': 3, 'k': 22.7, 'batterK': 36.5, 'batterWhiff': 31.0, 'pitcherK': 17.8}),
            row("Kazuma Okamoto", "R", "+559", 60, "", ["vs Bassitt"], """0 HR, 93.0 mph EV. limited split/risk sample; park/weather net drag (-23%).""", blast="good", contact={'stars': 3, 'k': 20.7, 'batterK': 23.2, 'batterWhiff': 28.7, 'pitcherK': 17.8}),
        ],
    },
    {
        "title": "TOR @ BAL (G2) - CJ Van Eyk (R, TOR) vs Trey Gibson (R, BAL)",
        "kLines": {'Eyk': {'k': 4.0, 'lo': 2, 'hi': 6, 'bf': 21.7, 'matchupK': 18.3, 'ownK': 2.9}, 'Gibson': {'k': 3.9, 'lo': 2, 'hi': 5, 'bf': 21.6, 'matchupK': 17.9, 'ownK': 18.6}},
        "description": "Tail key data: Park boost -23% (stadium -4%, weather -19%). Eyk - thin book: first MLB start, 6.2 career IP. Gibson (BAA vs LHB .304, vs RHB .255, HR/9 1.45 vs LHB, 2.57 vs RHB).",
        "rows": [
            row("Vladimir Guerrero Jr.", "R", "N/A", 49, "", ["vs Gibson"], """0 HR, 89.5 mph EV. limited split/risk sample; park/weather net drag (-23%).""", contact={'stars': 4, 'k': 18.4, 'batterK': 14.1, 'batterWhiff': 23.6, 'pitcherK': 18.6}),
            row("Kazuma Okamoto", "R", "N/A", 60, "", ["vs Gibson"], """0 HR, 93.0 mph EV. limited split/risk sample; park/weather net drag (-23%).""", blast="good", contact={'stars': 3, 'k': 21.6, 'batterK': 23.2, 'batterWhiff': 28.7, 'pitcherK': 18.6}),
            row("Pete Alonso", "R", "N/A", 80, "🌕 💣", ["vs Eyk"], """2 HR, 2 near-HR, 83.9 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-23%).""", blast="high", contact={'stars': 4, 'k': 19.4, 'batterK': 22.7, 'batterWhiff': 21.6, 'pitcherK': 2.9}),
            row("Coby Mayo", "R", "N/A", 58, "", ["vs Eyk"], """0 HR, 93.7 mph EV. limited split/risk sample; park/weather net drag (-23%).""", blast="good", contact={'stars': 4, 'k': 19.4, 'batterK': 20.3, 'batterWhiff': 25.0, 'pitcherK': 2.9}),
        ],
    },
    {
        "title": "WSH @ DET - Richard Lovelady (L, WSH) vs Framber Valdez (L, DET)",
        "kLines": {'Lovelady': {'k': 1.4, 'lo': 0, 'hi': 3, 'bf': 6.3, 'matchupK': 21.8, 'ownK': 18.8}, 'Valdez': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 24.1, 'matchupK': 18.3, 'ownK': 16.0}},
        "description": "Tail key data: Park boost -29% (stadium -10%, weather -19%). Lovelady (HR risk 0.28, vs LHB -1.24, vs RHB +1.19). Valdez (HR risk -0.90, vs LHB -0.32, vs RHB -0.74).",
        "rows": [
            row("Hao-Yu Lee", "R", "+600", 83, "", ["vs Lovelady"], """1 HR, 2 near-HR, 96.8 mph EV, 25.0% barrels. Lovelady RHB split +1.19, HR risk 0.28. park/weather net drag (-29%).""", blast="good", contact={'stars': 2, 'k': 24.8, 'batterK': 31.0, 'batterWhiff': 27.8, 'pitcherK': 18.8}),
            row("Spencer Torkelson", "R", "+592", 77, "", ["vs Lovelady"], """0 HR, 96.3 mph EV, 12.5% barrels. Lovelady RHB split +1.19, HR risk 0.28. park/weather net drag (-29%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.7, 'batterK': 28.4, 'batterWhiff': 37.9, 'pitcherK': 18.8}),
            row("Gleyber Torres", "R", "+1040", 62, "", ["vs Lovelady"], """0 HR, 1 near-HR, 92.0 mph EV, 12.5% barrels. Lovelady RHB split +1.19, HR risk 0.28. park/weather net drag (-29%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.3, 'batterK': 22.9, 'batterWhiff': 26.5, 'pitcherK': 18.8}),
            row("Kevin McGonigle", "L", "+860", 40, "", ["vs Lovelady"], """0 HR, 1 near-HR, 90.4 mph EV. Lovelady LHB split -1.24, HR risk 0.28. tough split lane (-1.24); park/weather net drag (-29%).""", contact={'stars': 4, 'k': 17.9, 'batterK': 13.7, 'batterWhiff': 17.6, 'pitcherK': 18.8}),
            row("Riley Greene", "L", "+540", 66, "", ["vs Lovelady"], """1 HR, 1 near-HR, 89.0 mph EV, 12.5% barrels. Lovelady LHB split -1.24, HR risk 0.28. tough split lane (-1.24); park/weather net drag (-29%).""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 24.1, 'batterWhiff': 31.4, 'pitcherK': 18.8}),
            row("James Wood", "L", "+590", 59, "", ["vs Valdez"], """0 HR, 99.9 mph EV. Valdez LHB split -0.32, HR risk -0.90. slight split headwind (-0.32); pitcher suppresses HR (-0.90).""", blast="good", contact={'stars': 3, 'k': 20.2, 'batterK': 28.9, 'batterWhiff': 24.0, 'pitcherK': 16.0}),
            row("CJ Abrams", "L", "+860", 58, "", ["vs Valdez"], """1 HR, 2 near-HR, 89.5 mph EV, 25.0% barrels. Valdez LHB split -0.32, HR risk -0.90. slight split headwind (-0.32); pitcher suppresses HR (-0.90).""", blast="good", contact={'stars': 3, 'k': 21.9, 'batterK': 30.2, 'batterWhiff': 32.4, 'pitcherK': 16.0}),
            row("Andres Chaparro", "R", "+600", 56, "", ["vs Valdez"], """1 HR, 1 near-HR, 91.0 mph EV, 25.0% barrels. Valdez RHB split -0.74, HR risk -0.90. tough split lane (-0.74); pitcher suppresses HR (-0.90).""", blast="good", contact={'stars': 3, 'k': 20.6, 'batterK': 23.9, 'batterWhiff': 33.8, 'pitcherK': 16.0}),
            row("Daylen Lile", "L", "N/A", 40, "", ["vs Valdez"], """0 HR, 79.2 mph EV. Valdez LHB split -0.32, HR risk -0.90. slight split headwind (-0.32); pitcher suppresses HR (-0.90).""", contact={'stars': 4, 'k': 18.8, 'batterK': 23.4, 'batterWhiff': 23.8, 'pitcherK': 16.0}),
            row("Brady House", "R", "+850", 48, "", ["vs Valdez"], """0 HR, 91.2 mph EV. Valdez RHB split -0.74, HR risk -0.90. tough split lane (-0.74); pitcher suppresses HR (-0.90).""", contact={'stars': 4, 'k': 17.4, 'batterK': 18.2, 'batterWhiff': 21.4, 'pitcherK': 16.0}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-23")

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

    out = ROOT / '_games-0923.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
