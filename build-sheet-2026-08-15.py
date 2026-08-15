#!/usr/bin/env python3
"""Generate games[] block for 2026-08-15 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Austin Riley (R)",
    "Ben Rice (L)",
    "Corbin Carroll (L)",
    "Corey Seager (L)",
    "Dominic Canzone (L)",
    "Griffin Conine (L)",
    "Jac Caglianone (L)",
    "Jackson Chourio (R)",
    "Jackson Merrill (L)",
    "Jesus Sanchez (L)",
    "Jordan Walker (R)",
    "Munetaka Murakami (L)",
    "Pete Alonso (R)",
    "Royce Lewis (R)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Andrew Vaughn (R)",
    "Brandon Lowe (L)",
    "Brett Baty (L)",
    "Bryce Eldridge (L)",
    "Carter Jensen (L)",
    "Chase DeLauter (L)",
    "Coby Mayo (R)",
    "Colson Montgomery (L)",
    "Eduardo Valencia (R)",
    "Fernando Tatis Jr. (R)",
    "Gunnar Henderson (L)",
    "J.T. Realmuto (R)",
    "Jarren Duran (L)",
    "Joc Pederson (L)",
    "Lars Nootbaar (L)",
    "Manny Machado (R)",
    "Miguel Amaya (R)",
    "Pete Crow-Armstrong (L)",
    "Taylor Trammell (L)",
    "Tyler Soderstrom (L)",
    "Tyler Stephenson (R)",
    "Zac Veen (L)",
}

PLAYER_TEAMS = {
    "Andrew Benintendi (L)": "CWS",
    "Andrew Pinckney (R)": "WSH",
    "Andrew Vaughn (R)": "MIL",
    "Austin Martin (R)": "MIN",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Braden Montgomery (S)": "CWS",
    "Brady House (R)": "WSH",
    "Brandon Lowe (L)": "PIT",
    "Brett Baty (L)": "NYM",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "Cal Raleigh (S)": "SEA",
    "Carter Jensen (L)": "KC",
    "Chase DeLauter (L)": "CLE",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Coby Mayo (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Connor Wong (R)": "BOS",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Daulton Varsho (L)": "HOU",
    "Daylen Lile (L)": "WSH",
    "Dominic Canzone (L)": "SEA",
    "Dylan Crews (R)": "WSH",
    "Eduardo Valencia (R)": "DET",
    "Ernie Clement (R)": "TOR",
    "Eugenio Suarez (R)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Lindor (S)": "NYM",
    "Gary Sanchez (R)": "MIL",
    "Gleyber Torres (R)": "DET",
    "Griffin Conine (L)": "MIA",
    "Gunnar Henderson (L)": "BAL",
    "Heliot Ramos (R)": "NYY",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "LAD",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Ivan Herrera (R)": "STL",
    "J.T. Realmuto (R)": "PHI",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jacob Gonzalez (L)": "PIT",
    "Jake Bauers (L)": "MIL",
    "Jake Mangum (S)": "PIT",
    "Jarren Duran (L)": "BOS",
    "Jase Bowen (R)": "SD",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jeremiah Jackson (R)": "BAL",
    "Jesus Sanchez (L)": "TOR",
    "Jim Jarvis (L)": "ATL",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "CLE",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "Jonah Heim (S)": "ATH",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Jorge Polanco (S)": "NYM",
    "Jose Fermin (R)": "STL",
    "Josh Lowe (L)": "LAA",
    "Josh Naylor (L)": "SEA",
    "Julio Rodriguez (R)": "SEA",
    "Jung Hoo Lee (L)": "SF",
    "Junior Caminero (R)": "TB",
    "Kyle Schwarber (L)": "PHI",
    "Lane Thomas (R)": "ATL",
    "Lars Nootbaar (L)": "ARI",
    "Luis Garcia Jr. (L)": "NYY",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Michael Conforto (L)": "CHC",
    "Mickey Moniak (L)": "COL",
    "Miguel Amaya (R)": "CHC",
    "Moises Ballesteros (L)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Nathaniel Lowe (L)": "CLE",
    "Nelson Velazquez (R)": "HOU",
    "Owen Caissie (L)": "MIA",
    "Ozzie Albies (S)": "ATL",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randy Arozarena (R)": "SEA",
    "Rhys Hoskins (R)": "CLE",
    "Royce Lewis (R)": "MIN",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Taylor Trammell (L)": "HOU",
    "Teoscar Hernandez (R)": "LAD",
    "Travis d'Arnaud (R)": "LAA",
    "Trea Turner (R)": "PHI",
    "Trent Grisham (L)": "NYY",
    "Tyler Soderstrom (L)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "Victor Caratini (S)": "MIN",
    "Victor Mesa Jr. (L)": "TB",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Willi Castro (S)": "COL",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
    "Zac Veen (L)": "COL",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("BOS @ PIT", "Jones"),
    ("COL @ SF", "Lorenzen"),
    ("MIL @ LAD", "Wrobleski"),
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
        "title": "ARI @ ATL - Eduardo Rodriguez (L, ARI) vs Grant Holmes (R, ATL)",
        "description": "Tail key data: Park boost +5% (stadium -3%, weather +8%). Rodriguez (HR risk -1.05, vs LHB -0.99, vs RHB -0.51). Holmes (HR risk 0.33, vs LHB +0.69, vs RHB -0.33).",
        "rows": [
            row("Ozzie Albies", "S", "+520", 58, "", ["vs Rodriguez"], """1 HR, 1 near-HR, 95.5 mph EV. Rodriguez SHB→RHB split -0.51, HR risk -1.05. tough split lane (-0.51); pitcher suppresses HR (-1.05).""", blast="good"),
            row("Matt Olson", "L", "+309", 66, "🌕 💣", ["vs Rodriguez"], """3 HR, 5 near-HR, 93.6 mph EV. Rodriguez LHB split -0.99, HR risk -1.05. tough split lane (-0.99); pitcher suppresses HR (-1.05).""", blast="high"),
            row("Lane Thomas", "R", "+650", 69, "🌕 💣", ["vs Rodriguez"], """3 HR, 4 near-HR, 95.7 mph EV. Rodriguez RHB split -0.51, HR risk -1.05. tough split lane (-0.51); pitcher suppresses HR (-1.05).""", blast="high"),
            row("Austin Riley", "R", "+455", 58, "🚀 ⭐", ["vs Rodriguez"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 100.4 mph EV. Rodriguez RHB split -0.51, HR risk -1.05. tough split lane (-0.51); pitcher suppresses HR (-1.05).""", blast="good"),
            row("Jim Jarvis", "L", "N/A", 58, "", ["vs Rodriguez"], """0 HR, 1 near-HR, 96.4 mph EV. Rodriguez LHB split -0.99, HR risk -1.05. tough split lane (-0.99); pitcher suppresses HR (-1.05).""", blast="good"),
            row("Corbin Carroll", "L", "+454", 73, "⭐", ["vs Holmes"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.0 mph EV. Holmes LHB split +0.69, HR risk 0.33.""", blast="good"),
            row("Lars Nootbaar", "L", "+563", 68, "💎", ["vs Holmes"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.5 mph EV. Holmes LHB split +0.69, HR risk 0.33. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "BAL @ TB - Kyle Bradish (R, BAL) vs Ian Seymour (L, TB)",
        "description": "Tail key data: Park boost -4% (stadium -4%, weather +0%). Bradish (HR risk -0.87, vs LHB -0.95, vs RHB -0.05). Seymour (HR risk 0.59, vs LHB +1.23, vs RHB +0.10).",
        "rows": [
            row("Jonathan Aranda", "L", "+600", 58, "", ["vs Bradish"], """0 HR, 1 near-HR, 95.2 mph EV. Bradish LHB split -0.95, HR risk -0.87. tough split lane (-0.95); pitcher suppresses HR (-0.87).""", blast="good"),
            row("Victor Mesa Jr.", "L", "N/A", 58, "", ["vs Bradish"], """1 HR, 1 near-HR, 86.4 mph EV. Bradish LHB split -0.95, HR risk -0.87. tough split lane (-0.95); pitcher suppresses HR (-0.87).""", blast="good"),
            row("Junior Caminero", "R", "+350", 58, "", ["vs Bradish"], """1 HR, 1 near-HR, 86.1 mph EV. Bradish RHB split -0.05, HR risk -0.87. slight split headwind (-0.05); pitcher suppresses HR (-0.87).""", blast="good"),
            row("Gunnar Henderson", "L", "+680", 78, "💎", ["vs Seymour"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.2 mph EV. Seymour LHB split +1.23, HR risk 0.59. limited recent HR events.""", blast="good"),
            row("Christian Encarnacion-Strand", "R", "+537", 87, "🌕 💣", ["vs Seymour"], """2 HR, 4 near-HR, 94.9 mph EV. Seymour RHB split +0.10, HR risk 0.59.""", blast="high"),
            row("Coby Mayo", "R", "+420", 72, "💎", ["vs Seymour"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.9 mph EV. Seymour RHB split +0.10, HR risk 0.59.""", blast="good"),
            row("Pete Alonso", "R", "+423", 73, "⭐", ["vs Seymour"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.3 mph EV. Seymour RHB split +0.10, HR risk 0.59.""", blast="good"),
            row("Jeremiah Jackson", "R", "N/A", 68, "", ["vs Seymour"], """0 HR, 1 near-HR, 95.7 mph EV. Seymour RHB split +0.10, HR risk 0.59. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "BOS @ PIT - Sonny Gray (R, BOS) vs Jared Jones 🧤 (R, PIT)",
        "description": "Tail key data: Park boost -12% (stadium -16%, weather +3%). Gray (HR risk -0.54, vs LHB -0.75, vs RHB +0.54). Jones 🧤 (HR risk 1.06, vs LHB -0.33, vs RHB +2.14).",
        "rows": [
            row("Jacob Gonzalez", "L", "+1080", 58, "", ["vs Gray"], """1 HR, 1 near-HR, 97.9 mph EV. Gray LHB split -0.75, HR risk -0.54. tough split lane (-0.75); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Brandon Lowe", "L", "+431", 58, "💎", ["vs Gray"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.2 mph EV. Gray LHB split -0.75, HR risk -0.54. tough split lane (-0.75); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Jake Mangum", "S", "+1500", 58, "", ["vs Gray"], """0 HR, 1 near-HR, 91.9 mph EV. Gray SHB→RHB split +0.54, HR risk -0.54. pitcher suppresses HR (-0.54); park/weather net drag (-12%)."""),
            row("Connor Wong", "R", "+885", 84, "", ["vs Jones"], """1 HR, 1 near-HR, 88.6 mph EV. Jones RHB split +2.14, HR risk 1.06. park/weather net drag (-12%).""", blast="good"),
            row("Jarren Duran", "L", "+546", 73, "💎", ["vs Jones"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.5 mph EV. Jones LHB split -0.33, HR risk 1.06. slight split headwind (-0.33); park/weather net drag (-12%).""", blast="good"),
            row("Wilyer Abreu", "L", "+342", 68, "", ["vs Jones"], """1 HR, 1 near-HR, 90.6 mph EV. Jones LHB split -0.33, HR risk 1.06. slight split headwind (-0.33); park/weather net drag (-12%).""", blast="good"),
        ],
    },
    {
        "title": "COL @ SF - Michael Lorenzen 🧤 (R, COL) vs Logan Webb (R, SF)",
        "description": "Tail key data: Park boost -23% (stadium -18%, weather -6%). Lorenzen 🧤 (HR risk 1.17, vs LHB +1.17, vs RHB +0.46). Webb (HR risk -1.50, vs LHB -0.90, vs RHB -0.99).",
        "rows": [
            row("Jung Hoo Lee", "L", "+1060", 85, "", ["vs Lorenzen"], """1 HR, 2 near-HR, 94.9 mph EV. Lorenzen LHB split +1.17, HR risk 1.17. park/weather net drag (-23%).""", blast="good"),
            row("Bryce Eldridge", "L", "+439", 79, "💎", ["vs Lorenzen"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.7 mph EV. Lorenzen LHB split +1.17, HR risk 1.17. park/weather net drag (-23%).""", blast="good"),
            row("Rafael Devers", "L", "+376", 82, "", ["vs Lorenzen"], """1 HR, 1 near-HR, 93.4 mph EV. Lorenzen LHB split +1.17, HR risk 1.17. park/weather net drag (-23%).""", blast="good"),
            row("Zac Veen", "L", "+870", 58, "💎", ["vs Webb"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.7 mph EV. Webb LHB split -0.90, HR risk -1.50. tough split lane (-0.90); pitcher suppresses HR (-1.50).""", blast="good"),
            row("Willi Castro", "S", "+800", 58, "", ["vs Webb"], """0 HR, 2 near-HR, 91.9 mph EV. Webb SHB→LHB split -0.90, HR risk -1.50. tough split lane (-0.90); pitcher suppresses HR (-1.50).""", blast="good"),
            row("Hunter Goodman", "R", "+430", 58, "", ["vs Webb"], """1 HR, 3 near-HR, 90.3 mph EV. Webb RHB split -0.99, HR risk -1.50. tough split lane (-0.99); pitcher suppresses HR (-1.50).""", blast="good"),
            row("Mickey Moniak", "L", "+690", 58, "", ["vs Webb"], """0 HR, 1 near-HR, 93.8 mph EV. Webb LHB split -0.90, HR risk -1.50. tough split lane (-0.90); pitcher suppresses HR (-1.50).""", blast="good"),
        ],
    },
    {
        "title": "CWS @ DET - Anthony Kay (L, CWS) vs Troy Melton (R, DET)",
        "description": "Tail key data: Park boost data unavailable. Kay (HR risk 0.11, vs LHB -1.31, vs RHB +0.80). Melton (HR risk -1.04, vs LHB -0.15, vs RHB -1.48).",
        "rows": [
            row("Eduardo Valencia", "R", "+400", 81, "🌕 💣 💎", ["vs Kay"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 95.2 mph EV. Kay RHB split +0.80, HR risk 0.11.""", blast="high"),
            row("Gleyber Torres", "R", "+770", 65, "", ["vs Kay"], """1 HR, 1 near-HR, 89.1 mph EV. Kay RHB split +0.80, HR risk 0.11.""", blast="good"),
            row("Munetaka Murakami", "L", "+285", 71, "🚀 ⭐ 🌕 💣", ["vs Melton"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 102.2 mph EV. Melton LHB split -0.15, HR risk -1.04. slight split headwind (-0.15); pitcher suppresses HR (-1.04).""", blast="high"),
            row("Colson Montgomery", "L", "+398", 58, "💎", ["vs Melton"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.0 mph EV. Melton LHB split -0.15, HR risk -1.04. slight split headwind (-0.15); pitcher suppresses HR (-1.04).""", blast="good"),
            row("Andrew Benintendi", "L", "+590", 58, "", ["vs Melton"], """1 HR, 2 near-HR, 95.2 mph EV. Melton LHB split -0.15, HR risk -1.04. slight split headwind (-0.15); pitcher suppresses HR (-1.04).""", blast="good"),
            row("Braden Montgomery", "S", "+960", 58, "", ["vs Melton"], """0 HR, 1 near-HR, 93.4 mph EV. Melton SHB→LHB split -0.15, HR risk -1.04. slight split headwind (-0.15); pitcher suppresses HR (-1.04).""", blast="good"),
        ],
    },
    {
        "title": "KC @ LAA - Randy Dobnak (R, KC) vs Reid Detmers (L, LAA)",
        "description": "Tail key data: Park boost -4% (stadium -9%, weather +6%). Dobnak (HR risk -1.40, vs LHB -1.09, vs RHB -0.62). Detmers (HR risk 0.69, vs LHB +0.26, vs RHB +0.44).",
        "rows": [
            row("Travis d'Arnaud", "R", "N/A", 58, "", ["vs Dobnak"], """0 HR, 90.4 mph EV. Dobnak RHB split -0.62, HR risk -1.40. tough split lane (-0.62); pitcher suppresses HR (-1.40)."""),
            row("Moises Ballesteros", "L", "+600", 58, "", ["vs Dobnak"], """0 HR, 1 near-HR, 96.6 mph EV. Dobnak LHB split -1.09, HR risk -1.40. tough split lane (-1.09); pitcher suppresses HR (-1.40).""", blast="good"),
            row("Josh Lowe", "L", "+560", 58, "", ["vs Dobnak"], """0 HR, 90.9 mph EV. Dobnak LHB split -1.09, HR risk -1.40. tough split lane (-1.09); pitcher suppresses HR (-1.40)."""),
            row("Jac Caglianone", "L", "+430", 84, "⭐ 🌕 💣", ["vs Detmers"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.2 mph EV. Detmers LHB split +0.26, HR risk 0.69. park suppresses carry (-9%).""", blast="high"),
            row("Carter Jensen", "L", "+470", 75, "💎", ["vs Detmers"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.6 mph EV. Detmers LHB split +0.26, HR risk 0.69. park suppresses carry (-9%).""", blast="good"),
            row("Salvador Perez", "R", "+252", 69, "", ["vs Detmers"], """0 HR, 1 near-HR, 92.3 mph EV. Detmers RHB split +0.44, HR risk 0.69. park suppresses carry (-9%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ CIN - Ryan Gusto (R, MIA) vs Brady Singer (R, CIN)",
        "description": "Tail key data: Park boost +18% (stadium +15%, weather +3%). Gusto (HR risk 0.32, vs LHB +0.09, vs RHB +0.49). Singer (HR risk -0.27, vs LHB +0.21, vs RHB -0.66).",
        "rows": [
            row("Tyler Stephenson", "R", "+500", 76, "💎", ["vs Gusto"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.4 mph EV. Gusto RHB split +0.49, HR risk 0.32.""", blast="good"),
            row("Eugenio Suarez", "R", "+329", 79, "🌕 💣", ["vs Gusto"], """2 HR, 2 near-HR, 89.5 mph EV. Gusto RHB split +0.49, HR risk 0.32.""", blast="high"),
            row("Sal Stewart", "R", "+351", 67, "", ["vs Gusto"], """1 HR, 1 near-HR, 87.0 mph EV. Gusto RHB split +0.49, HR risk 0.32. lighter EV form (87.0 mph).""", blast="good"),
            row("Griffin Conine", "L", "+430", 78, "⭐ 🌕 💣", ["vs Singer"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.5 mph EV. Singer LHB split +0.21, HR risk -0.27. pitcher risk below avg (-0.27).""", blast="high"),
            row("Heriberto Hernandez", "R", "+399", 58, "", ["vs Singer"], """1 HR, 1 near-HR, 89.0 mph EV. Singer RHB split -0.66, HR risk -0.27. tough split lane (-0.66); pitcher risk below avg (-0.27).""", blast="good"),
            row("Owen Caissie", "L", "+399", 58, "", ["vs Singer"], """0 HR, 86.7 mph EV. Singer LHB split +0.21, HR risk -0.27. pitcher risk below avg (-0.27); limited recent HR events."""),
            row("Joe Mack", "L", "+470", 58, "", ["vs Singer"], """0 HR, 85.7 mph EV. Singer LHB split +0.21, HR risk -0.27. pitcher risk below avg (-0.27); limited recent HR events."""),
        ],
    },
    {
        "title": "MIL @ LAD - Jacob Misiorowski (R, MIL) vs Justin Wrobleski 🧤 (L, LAD)",
        "description": "Tail key data: Park boost +20% (stadium +19%, weather +2%). Misiorowski (HR risk 0.38, vs LHB +0.24, vs RHB +0.21). Wrobleski 🧤 (HR risk 1.52, vs LHB +0.73, vs RHB +1.17).",
        "rows": [
            row("Shohei Ohtani", "L", "+300", 62, "", ["vs Misiorowski"], """0 HR, 1 near-HR, 90.7 mph EV. Misiorowski LHB split +0.24, HR risk 0.38. limited recent HR events."""),
            row("Hunter Feduccia", "L", "+1040", 65, "", ["vs Misiorowski"], """1 HR, 1 near-HR, 86.6 mph EV. Misiorowski LHB split +0.24, HR risk 0.38. lighter EV form (86.6 mph).""", blast="good"),
            row("Teoscar Hernandez", "R", "+620", 70, "", ["vs Misiorowski"], """1 HR, 1 near-HR, 91.8 mph EV. Misiorowski RHB split +0.21, HR risk 0.38.""", blast="good"),
            row("Max Muncy", "L", "+450", 67, "", ["vs Misiorowski"], """1 HR, 1 near-HR, 88.4 mph EV. Misiorowski LHB split +0.24, HR risk 0.38.""", blast="good"),
            row("Andrew Vaughn", "R", "+434", 93, "🌕 💣 💎", ["vs Wrobleski"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.4 mph EV. Wrobleski RHB split +1.17, HR risk 1.52.""", blast="good"),
            row("Jake Bauers", "L", "+371", 90, "🌕 💣", ["vs Wrobleski"], """1 HR, 1 near-HR, 92.9 mph EV. Wrobleski LHB split +0.73, HR risk 1.52.""", blast="good"),
            row("Jackson Chourio", "R", "+354", 90, "⭐ 🌕 💣", ["vs Wrobleski"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 88.1 mph EV. Wrobleski RHB split +1.17, HR risk 1.52.""", blast="good"),
            row("Gary Sanchez", "R", "+372", 93, "🌕 💣", ["vs Wrobleski"], """2 HR, 2 near-HR, 86.5 mph EV. Wrobleski RHB split +1.17, HR risk 1.52. lighter EV form (86.5 mph).""", blast="high"),
        ],
    },
    {
        "title": "NYY @ TOR - Cam Schlittler (R, NYY) vs Braydon Fisher (R, TOR)",
        "description": "Tail key data: Park boost +6% (stadium +7%, weather -1%). Schlittler (HR risk -0.52, vs LHB -0.02, vs RHB -0.66). Fisher (HR risk -1.09, vs LHB -0.13, vs RHB -0.60).",
        "rows": [
            row("Jesus Sanchez", "L", "+527", 58, "⭐", ["vs Schlittler"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 89.1 mph EV. Schlittler LHB split -0.02, HR risk -0.52. slight split headwind (-0.02); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Vladimir Guerrero Jr.", "R", "N/A", 58, "", ["vs Schlittler"], """1 HR, 1 near-HR, 90.7 mph EV. Schlittler RHB split -0.66, HR risk -0.52. tough split lane (-0.66); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Ernie Clement", "R", "+980", 58, "", ["vs Schlittler"], """0 HR, 83.6 mph EV. Schlittler RHB split -0.66, HR risk -0.52. tough split lane (-0.66); pitcher suppresses HR (-0.52)."""),
            row("Trent Grisham", "L", "+386", 65, "🌕 💣", ["vs Fisher"], """2 HR, 2 near-HR, 96.8 mph EV. Fisher LHB split -0.13, HR risk -1.09. slight split headwind (-0.13); pitcher suppresses HR (-1.09).""", blast="high"),
            row("Jazz Chisholm Jr.", "L", "+438", 58, "", ["vs Fisher"], """1 HR, 2 near-HR, 97.3 mph EV. Fisher LHB split -0.13, HR risk -1.09. slight split headwind (-0.13); pitcher suppresses HR (-1.09).""", blast="good"),
            row("Luis Garcia Jr.", "L", "+465", 58, "", ["vs Fisher"], """0 HR, 1 near-HR, 94.5 mph EV. Fisher LHB split -0.13, HR risk -1.09. slight split headwind (-0.13); pitcher suppresses HR (-1.09).""", blast="good"),
            row("Spencer Jones", "L", "+520", 58, "", ["vs Fisher"], """0 HR, 92.4 mph EV. Fisher LHB split -0.13, HR risk -1.09. slight split headwind (-0.13); pitcher suppresses HR (-1.09).""", blast="good"),
            row("Ben Rice", "L", "+362", 58, "⭐", ["vs Fisher"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 97.7 mph EV. Fisher LHB split -0.13, HR risk -1.09. slight split headwind (-0.13); pitcher suppresses HR (-1.09).""", blast="good"),
            row("Heliot Ramos", "R", "+460", 58, "", ["vs Fisher"], """0 HR, 94.5 mph EV. Fisher RHB split -0.60, HR risk -1.09. tough split lane (-0.60); pitcher suppresses HR (-1.09).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ MIN - Jesus Luzardo (L, PHI) vs Connor Prielipp (L, MIN)",
        "description": "Tail key data: Park boost +3% (stadium -7%, weather +10%). Luzardo (HR risk -0.75, vs LHB -1.74, vs RHB +0.03). Prielipp (HR risk 0.74, vs LHB +0.10, vs RHB +0.73).",
        "rows": [
            row("Royce Lewis", "R", "+483", 70, "⭐ 🌕 💣", ["vs Luzardo"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 92.8 mph EV. Luzardo RHB split +0.03, HR risk -0.75. pitcher suppresses HR (-0.75); park suppresses carry (-7%).""", blast="high"),
            row("Byron Buxton", "R", "+355", 58, "", ["vs Luzardo"], """0 HR, 1 near-HR, 93.4 mph EV. Luzardo RHB split +0.03, HR risk -0.75. pitcher suppresses HR (-0.75); park suppresses carry (-7%).""", blast="good"),
            row("Austin Martin", "R", "+1280", 58, "", ["vs Luzardo"], """1 HR, 1 near-HR, 91.0 mph EV. Luzardo RHB split +0.03, HR risk -0.75. pitcher suppresses HR (-0.75); park suppresses carry (-7%).""", blast="good"),
            row("Victor Caratini", "S", "+960", 58, "", ["vs Luzardo"], """0 HR, 88.0 mph EV. Luzardo SHB→RHB split +0.03, HR risk -0.75. pitcher suppresses HR (-0.75); park suppresses carry (-7%)."""),
            row("Bryson Stott", "L", "+800", 71, "", ["vs Prielipp"], """0 HR, 2 near-HR, 93.7 mph EV. Prielipp LHB split +0.10, HR risk 0.74. park suppresses carry (-7%).""", blast="good"),
            row("Kyle Schwarber", "L", "+250", 61, "", ["vs Prielipp"], """0 HR, 1 near-HR, 89.3 mph EV. Prielipp LHB split +0.10, HR risk 0.74. park suppresses carry (-7%); limited recent HR events."""),
            row("Trea Turner", "R", "+570", 73, "", ["vs Prielipp"], """0 HR, 93.8 mph EV. Prielipp RHB split +0.73, HR risk 0.74. park suppresses carry (-7%); limited recent HR events.""", blast="good"),
            row("J.T. Realmuto", "R", "+650", 81, "💎", ["vs Prielipp"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.0 mph EV. Prielipp RHB split +0.73, HR risk 0.74. park suppresses carry (-7%).""", blast="good"),
            row("Bryce Harper", "L", "+420", 68, "", ["vs Prielipp"], """1 HR, 1 near-HR, 87.8 mph EV. Prielipp LHB split +0.10, HR risk 0.74. park suppresses carry (-7%); lighter EV form (87.8 mph).""", blast="good"),
        ],
    },
    {
        "title": "SD @ CLE - Randy Vasquez (R, SD) vs Joey Cantillo (L, CLE)",
        "description": "Tail key data: Park boost +3% (stadium -3%, weather +6%). Away starter risk unavailable. Cantillo (HR risk 0.63, vs LHB -0.19, vs RHB +0.74).",
        "rows": [
            row("Nathaniel Lowe", "L", "+315", 64, "", ["vs Vasquez"], """1 HR, 1 near-HR, 92.6 mph EV. Vasquez split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Chase DeLauter", "L", "+250", 66, "💎", ["vs Vasquez"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.3 mph EV. Vasquez split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Jo Adell", "R", "+270", 61, "", ["vs Vasquez"], """1 HR, 1 near-HR, 89.8 mph EV. Vasquez split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Rhys Hoskins", "R", "N/A", 67, "", ["vs Vasquez"], """1 HR, 1 near-HR, 95.6 mph EV. Vasquez split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Jase Bowen", "R", "N/A", 64, "", ["vs Cantillo"], """0 HR, 89.2 mph EV. Cantillo RHB split +0.74, HR risk 0.63. limited recent HR events."""),
            row("Fernando Tatis Jr.", "R", "+270", 76, "💎", ["vs Cantillo"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.3 mph EV. Cantillo RHB split +0.74, HR risk 0.63.""", blast="good"),
            row("Jackson Merrill", "L", "+301", 67, "⭐", ["vs Cantillo"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.0 mph EV. Cantillo LHB split -0.19, HR risk 0.63. slight split headwind (-0.19); limited recent HR events.""", blast="good"),
            row("Manny Machado", "R", "+273", 66, "💎", ["vs Cantillo"], """Worst Pickz Hidden Gem. 0 HR, 91.5 mph EV. Cantillo RHB split +0.74, HR risk 0.63. limited recent HR events."""),
        ],
    },
    {
        "title": "SEA @ HOU - Emerson Hancock (R, SEA) vs Hayden Wesneski (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +0%). Hancock (HR risk 0.09, vs LHB +0.32, vs RHB -0.17). Wesneski (HR risk 0.09, vs LHB +1.33, vs RHB -1.18).",
        "rows": [
            row("Yordan Alvarez", "L", "+250", 64, "⭐", ["vs Hancock"], """Worst Pickz Favorite. 0 HR, 97.8 mph EV. Hancock LHB split +0.32, HR risk 0.09. limited recent HR events.""", blast="good"),
            row("Taylor Trammell", "L", "+549", 72, "💎", ["vs Hancock"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 92.4 mph EV. Hancock LHB split +0.32, HR risk 0.09.""", blast="good"),
            row("Daulton Varsho", "L", "+770", 62, "", ["vs Hancock"], """0 HR, 94.1 mph EV. Hancock LHB split +0.32, HR risk 0.09. limited recent HR events.""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 61, "", ["vs Hancock"], """0 HR, 1 near-HR, 96.5 mph EV. Hancock RHB split -0.17, HR risk 0.09. slight split headwind (-0.17); limited recent HR events.""", blast="good"),
            row("Dominic Canzone", "L", "+416", 76, "⭐", ["vs Wesneski"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.5 mph EV. Wesneski LHB split +1.33, HR risk 0.09.""", blast="good"),
            row("Cal Raleigh", "S", "+367", 72, "", ["vs Wesneski"], """0 HR, 2 near-HR, 93.7 mph EV. Wesneski SHB→LHB split +1.33, HR risk 0.09.""", blast="good"),
            row("Josh Naylor", "L", "+630", 61, "", ["vs Wesneski"], """0 HR, 89.4 mph EV. Wesneski LHB split +1.33, HR risk 0.09. limited recent HR events."""),
            row("Julio Rodriguez", "R", "+523", 61, "", ["vs Wesneski"], """1 HR, 1 near-HR, 95.4 mph EV. Wesneski RHB split -1.18, HR risk 0.09. tough split lane (-1.18).""", blast="good"),
            row("Randy Arozarena", "R", "+560", 58, "", ["vs Wesneski"], """1 HR, 1 near-HR, 91.3 mph EV. Wesneski RHB split -1.18, HR risk 0.09. tough split lane (-1.18).""", blast="good"),
        ],
    },
    {
        "title": "STL @ CHC - Michael McGreevy (R, STL) vs Matthew Boyd (L, CHC)",
        "description": "Tail key data: Park boost +18% (stadium +1%, weather +18%). McGreevy (HR risk 0.83, vs LHB +0.74, vs RHB +0.48). Boyd (HR risk -0.20, vs LHB -0.67, vs RHB +0.03).",
        "rows": [
            row("Ian Happ", "S", "+496", 91, "🌕 💣", ["vs McGreevy"], """2 HR, 2 near-HR, 94.3 mph EV. McGreevy SHB→LHB split +0.74, HR risk 0.83.""", blast="high"),
            row("Miguel Amaya", "R", "+436", 85, "💎", ["vs McGreevy"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 97.2 mph EV. McGreevy RHB split +0.48, HR risk 0.83.""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+330", 82, "💎", ["vs McGreevy"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 91.2 mph EV. McGreevy LHB split +0.74, HR risk 0.83.""", blast="good"),
            row("Michael Conforto", "L", "+532", 79, "", ["vs McGreevy"], """0 HR, 1 near-HR, 93.5 mph EV. McGreevy LHB split +0.74, HR risk 0.83. limited recent HR events.""", blast="good"),
            row("Jordan Walker", "R", "+320", 62, "⭐", ["vs Boyd"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 90.7 mph EV. Boyd RHB split +0.03, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="good"),
            row("Ivan Herrera", "R", "+493", 58, "", ["vs Boyd"], """0 HR, 1 near-HR, 91.8 mph EV. Boyd RHB split +0.03, HR risk -0.20. pitcher risk below avg (-0.20); limited recent HR events."""),
            row("Jimmy Crooks", "L", "N/A", 58, "", ["vs Boyd"], """0 HR, 1 near-HR, 93.5 mph EV. Boyd LHB split -0.67, HR risk -0.20. tough split lane (-0.67); pitcher risk below avg (-0.20).""", blast="good"),
            row("Jose Fermin", "R", "+720", 63, "", ["vs Boyd"], """1 HR, 1 near-HR, 91.8 mph EV. Boyd RHB split +0.03, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ ATH - MacKenzie Gore (L, TEX) vs J.T. Ginn (R, ATH)",
        "description": "Tail key data: Park boost +31% (stadium +31%, weather +0%). Gore (HR risk 0.58, vs LHB +0.09, vs RHB +0.48). Ginn (HR risk -0.48, vs LHB +0.31, vs RHB -1.13).",
        "rows": [
            row("Tyler Soderstrom", "L", "+503", 90, "🌕 💣 💎", ["vs Gore"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 97.3 mph EV. Gore LHB split +0.09, HR risk 0.58.""", blast="high"),
            row("Jonah Heim", "S", "+511", 85, "", ["vs Gore"], """1 HR, 2 near-HR, 94.8 mph EV. Gore SHB→RHB split +0.48, HR risk 0.58.""", blast="good"),
            row("Henry Bolte", "R", "+458", 74, "", ["vs Gore"], """1 HR, 1 near-HR, 83.2 mph EV. Gore RHB split +0.48, HR risk 0.58. lighter EV form (83.2 mph).""", blast="good"),
            row("Zack Gelof", "R", "+482", 91, "🌕 💣", ["vs Gore"], """2 HR, 2 near-HR, 93.5 mph EV. Gore RHB split +0.48, HR risk 0.58.""", blast="high"),
            row("Joc Pederson", "L", "+320", 80, "🚀 🌕 💣 💎", ["vs Ginn"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 101.4 mph EV. Ginn LHB split +0.31, HR risk -0.48. pitcher suppresses HR (-0.48).""", blast="high"),
            row("Corey Seager", "L", "+350", 65, "⭐", ["vs Ginn"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 90.4 mph EV. Ginn LHB split +0.31, HR risk -0.48. pitcher suppresses HR (-0.48).""", blast="good"),
            row("Wyatt Langford", "R", "+420", 58, "", ["vs Ginn"], """1 HR, 1 near-HR, 91.3 mph EV. Ginn RHB split -1.13, HR risk -0.48. tough split lane (-1.13); pitcher suppresses HR (-0.48).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ NYM - Brad Lord (R, WSH) vs Sean Manaea (L, NYM)",
        "description": "Tail key data: Park boost data unavailable. Lord (HR risk -0.33, vs LHB +1.17, vs RHB -1.15). Manaea (HR risk 0.91, vs LHB +0.54, vs RHB +0.68).",
        "rows": [
            row("Brett Baty", "L", "+610", 84, "🌕 💣 💎", ["vs Lord"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 94.9 mph EV. Lord LHB split +1.17, HR risk -0.33. pitcher risk below avg (-0.33).""", blast="high"),
            row("Francisco Lindor", "S", "+460", 62, "", ["vs Lord"], """0 HR, 93.1 mph EV. Lord SHB→LHB split +1.17, HR risk -0.33. pitcher risk below avg (-0.33); limited recent HR events.""", blast="good"),
            row("Jorge Polanco", "S", "+571", 61, "", ["vs Lord"], """1 HR, 1 near-HR, 85.5 mph EV. Lord SHB→LHB split +1.17, HR risk -0.33. pitcher risk below avg (-0.33); lighter EV form (85.5 mph).""", blast="good"),
            row("Daylen Lile", "L", "+650", 74, "", ["vs Manaea"], """0 HR, 1 near-HR, 94.2 mph EV. Manaea LHB split +0.54, HR risk 0.91. limited recent HR events.""", blast="good"),
            row("Brady House", "R", "+526", 81, "", ["vs Manaea"], """1 HR, 1 near-HR, 96.3 mph EV. Manaea RHB split +0.68, HR risk 0.91.""", blast="good"),
            row("Andrew Pinckney", "R", "+690", 81, "🚀", ["vs Manaea"], """1 HR, 1 near-HR, 103.1 mph EV. Manaea RHB split +0.68, HR risk 0.91.""", blast="good"),
            row("Dylan Crews", "R", "+422", 73, "", ["vs Manaea"], """0 HR, 93.3 mph EV. Manaea RHB split +0.68, HR risk 0.91. limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-15")

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

    out = ROOT / '_games-0815.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
