#!/usr/bin/env python3
"""Generate games[] block for 2026-08-19 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Austin Riley (R)",
    "Ben Rice (L)",
    "Bo Bichette (R)",
    "Bryce Harper (L)",
    "Carter Jensen (L)",
    "Corbin Carroll (L)",
    "Dominic Canzone (L)",
    "Jo Adell (R)",
    "Jonathan Aranda (L)",
    "Jose Tena (L)",
    "Kody Clemens (L)",
    "Matt Olson (L)",
    "Michael Massey (L)",
    "Oneil Cruz (L)",
    "Shohei Ohtani (L)",
    "Spencer Torkelson (R)",
    "Taylor Trammell (L)",
    "Tyler Stephenson (R)",
    "Willi Castro (S)",
    "William Contreras (R)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Abimelec Ortiz (L)",
    "Ben Malgeri (R)",
    "Brett Baty (L)",
    "Coby Mayo (R)",
    "Jac Caglianone (L)",
    "Jimmy Crooks (L)",
    "Josh Lowe (L)",
    "Luis Garcia Jr. (L)",
    "Luis Lara (S)",
    "Nelson Velazquez (R)",
    "Pete Alonso (R)",
    "Teoscar Hernandez (R)",
    "Zac Veen (L)",
}

PLAYER_TEAMS = {
    "Abimelec Ortiz (L)": "WSH",
    "Adley Rutschman (S)": "BOS",
    "Alec Burleson (L)": "STL",
    "Andy Pages (R)": "LAD",
    "Austin Riley (R)": "ATL",
    "Ben Malgeri (R)": "DET",
    "Ben Rice (L)": "NYY",
    "Bo Bichette (R)": "NYM",
    "Brandon Lowe (L)": "PIT",
    "Brenton Doyle (R)": "CWS",
    "Brett Baty (L)": "NYM",
    "Brett Callahan (L)": "DET",
    "Brice Turang (L)": "MIL",
    "Brock Rodden (S)": "SEA",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "CJ Abrams (L)": "WSH",
    "Carter Jensen (L)": "KC",
    "Christian Yelich (L)": "MIL",
    "Coby Mayo (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Dane Myers (R)": "CIN",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Dylan Beavers (L)": "BAL",
    "Dylan Crews (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Evan Carter (L)": "TEX",
    "Francisco Lindor (S)": "NYM",
    "Gabriel Moreno (R)": "ARI",
    "Garrett Mitchell (L)": "MIL",
    "Gary Sanchez (R)": "MIL",
    "Griffin Conine (L)": "MIA",
    "Gunnar Henderson (L)": "BAL",
    "Heliot Ramos (R)": "NYY",
    "Ivan Herrera (R)": "STL",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jeff McNeil (L)": "ATH",
    "Jesus Sanchez (L)": "TOR",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "CLE",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "Jonathan Aranda (L)": "TB",
    "Jonny DeLuca (R)": "TB",
    "Jorge Mateo (R)": "TB",
    "Jose Tena (L)": "WSH",
    "Josh Bell (S)": "MIN",
    "Josh Lowe (L)": "LAA",
    "Joshua Baez (R)": "STL",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Lawrence Butler (L)": "ATH",
    "Leody Taveras (S)": "BAL",
    "Luis Campusano (R)": "SD",
    "Luis Garcia Jr. (L)": "NYY",
    "Luis Lara (S)": "MIL",
    "Maikel Garcia (R)": "KC",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Max Muncy (L)": "LAD",
    "Max Muncy (R)": "ATH",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Michael Massey (L)": "KC",
    "Mickey Moniak (L)": "COL",
    "Miguel Amaya (R)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Mookie Betts (R)": "LAD",
    "Nathaniel Lowe (L)": "CLE",
    "Nelson Velazquez (R)": "HOU",
    "Oneil Cruz (L)": "PIT",
    "Owen Caissie (L)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Rhys Hoskins (R)": "CLE",
    "Richie Palacios (L)": "TB",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan Kreidler (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Taylor Trammell (L)": "HOU",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Travis d'Arnaud (R)": "LAA",
    "Trent Grisham (L)": "NYY",
    "Tyler Stephenson (R)": "CIN",
    "Victor Bericoto (R)": "SF",
    "Willi Castro (S)": "COL",
    "William Contreras (R)": "MIL",
    "Wilyer Abreu (L)": "BOS",
    "Yordan Alvarez (L)": "HOU",
    "Zac Veen (L)": "COL",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("DET @ PIT", "Jobe"),
    ("MIA @ PHI", "Nola"),
    ("TOR @ TB", "Scherzer"),
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
        "title": "ARI @ BOS - Brandon Pfaadt (R, ARI) vs Payton Tolle (L, BOS)",
        "description": "Tail key data: Park boost +5% (stadium -8%, weather +12%). Pfaadt (HR risk -0.80, vs LHB -0.76, vs RHB -0.43). Tolle (HR risk 0.21, vs LHB +0.60, vs RHB +0.23).",
        "rows": [
            row("Wilyer Abreu", "L", "N/A", 58, "", ["vs Pfaadt"], """1 HR, 2 near-HR, 95.5 mph EV. Pfaadt LHB split -0.76, HR risk -0.80. tough split lane (-0.76); pitcher suppresses HR (-0.80).""", blast="good"),
            row("Adley Rutschman", "S", "N/A", 58, "", ["vs Pfaadt"], """1 HR, 1 near-HR, 88.9 mph EV. Pfaadt SHB→RHB split -0.43, HR risk -0.80. tough split lane (-0.43); pitcher suppresses HR (-0.80).""", blast="good"),
            row("Corbin Carroll", "L", "N/A", 77, "⭐ 🌕 💣", ["vs Tolle"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.5 mph EV. Tolle LHB split +0.60, HR risk 0.21. park suppresses carry (-8%).""", blast="high"),
            row("Max Kepler", "L", "N/A", 67, "", ["vs Tolle"], """0 HR, 97.6 mph EV. Tolle LHB split +0.60, HR risk 0.21. park suppresses carry (-8%); limited recent HR events.""", blast="good"),
            row("Gabriel Moreno", "R", "N/A", 67, "", ["vs Tolle"], """1 HR, 2 near-HR, 91.6 mph EV. Tolle RHB split +0.23, HR risk 0.21. park suppresses carry (-8%).""", blast="good"),
            row("Tim Tawa", "R", "N/A", 61, "", ["vs Tolle"], """0 HR, 93.2 mph EV. Tolle RHB split +0.23, HR risk 0.21. park suppresses carry (-8%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "ATH @ KC - Gage Jump (R, ATH) vs Seth Lugo (R, KC)",
        "description": "Tail key data: Park boost +6% (stadium +10%, weather -4%). Jump. Lugo.",
        "rows": [
            row("Zack Gelof", "R", "+582", 70, "🌕 💣", ["vs Lugo"], """2 HR, 2 near-HR, 88.5 mph EV. limited split/risk sample; weather carry headwind (-4%).""", blast="high"),
            row("Lawrence Butler", "L", "+740", 74, "🌕 💣", ["vs Lugo"], """2 HR, 2 near-HR, 92.5 mph EV. limited split/risk sample; weather carry headwind (-4%).""", blast="high"),
            row("Max Muncy", "R", "N/A", 63, "", ["vs Lugo"], """0 HR, 2 near-HR, 93.6 mph EV. limited split/risk sample; weather carry headwind (-4%).""", blast="good"),
            row("Jeff McNeil", "L", "+980", 78, "🌕 💣", ["vs Lugo"], """2 HR, 2 near-HR, 96.5 mph EV. limited split/risk sample; weather carry headwind (-4%).""", blast="high"),
            row("Jac Caglianone", "L", "+660", 82, "🌕 💣 💎", ["vs Jump"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 96.9 mph EV. limited split/risk sample; weather carry headwind (-4%).""", blast="high"),
            row("Michael Massey", "L", "+1060", 58, "⭐", ["vs Jump"], """Worst Pickz Favorite. 0 HR, 90.2 mph EV. limited split/risk sample; weather carry headwind (-4%)."""),
            row("Maikel Garcia", "R", "+1120", 64, "", ["vs Jump"], """0 HR, 1 near-HR, 99.4 mph EV. limited split/risk sample; weather carry headwind (-4%).""", blast="good"),
            row("Carter Jensen", "L", "+700", 62, "⭐", ["vs Jump"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 89.8 mph EV. limited split/risk sample; weather carry headwind (-4%).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ MIN - AJ Smith-Shawver (R, ATL) vs Taj Bradley (R, MIN)",
        "description": "Tail key data: Park boost -2% (stadium -7%, weather +5%). Smith-Shawver (HR risk 0.07, vs LHB -0.04, vs RHB -0.01). Bradley (HR risk 0.23, vs LHB +0.61, vs RHB -0.46).",
        "rows": [
            row("Josh Bell", "S", "+560", 61, "", ["vs Smith-Shawver"], """1 HR, 1 near-HR, 92.7 mph EV. Smith-Shawver SHB→RHB split -0.01, HR risk 0.07. slight split headwind (-0.01); park suppresses carry (-7%).""", blast="good"),
            row("Kody Clemens", "L", "+518", 64, "⭐", ["vs Smith-Shawver"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.5 mph EV. Smith-Shawver LHB split -0.04, HR risk 0.07. slight split headwind (-0.04); park suppresses carry (-7%).""", blast="good"),
            row("Royce Lewis", "R", "+484", 65, "", ["vs Smith-Shawver"], """1 HR, 2 near-HR, 95.2 mph EV. Smith-Shawver RHB split -0.01, HR risk 0.07. slight split headwind (-0.01); park suppresses carry (-7%).""", blast="good"),
            row("Ryan Kreidler", "R", "N/A", 58, "", ["vs Smith-Shawver"], """0 HR, 1 near-HR, 91.6 mph EV. Smith-Shawver RHB split -0.01, HR risk 0.07. slight split headwind (-0.01); park suppresses carry (-7%)."""),
            row("Matt Olson", "L", "+307", 85, "⭐ 🌕 💣", ["vs Bradley"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 97.9 mph EV. Bradley LHB split +0.61, HR risk 0.23. park suppresses carry (-7%).""", blast="high"),
            row("Michael Harris II", "L", "+437", 68, "", ["vs Bradley"], """1 HR, 1 near-HR, 93.5 mph EV. Bradley LHB split +0.61, HR risk 0.23. park suppresses carry (-7%).""", blast="good"),
            row("Drake Baldwin", "L", "+412", 58, "", ["vs Bradley"], """0 HR, 1 near-HR, 90.9 mph EV. Bradley LHB split +0.61, HR risk 0.23. park suppresses carry (-7%); limited recent HR events."""),
            row("Austin Riley", "R", "+535", 58, "⭐", ["vs Bradley"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 92.7 mph EV. Bradley RHB split -0.46, HR risk 0.23. tough split lane (-0.46); park suppresses carry (-7%).""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+348", 58, "", ["vs Bradley"], """0 HR, 1 near-HR, 95.9 mph EV. Bradley RHB split -0.46, HR risk 0.23. tough split lane (-0.46); park suppresses carry (-7%).""", blast="good"),
        ],
    },
    {
        "title": "CWS @ CHC - Sean Newcomb (L, CWS) vs Clay Holmes (R, CHC)",
        "description": "Tail key data: Park boost -16% (stadium -2%, weather -14%). Newcomb (HR risk -1.16, vs LHB -1.25, vs RHB -0.61). Holmes (HR risk -0.81, vs LHB -0.47, vs RHB -0.87).",
        "rows": [
            row("Miguel Amaya", "R", "N/A", 58, "", ["vs Newcomb"], """1 HR, 2 near-HR, 96.0 mph EV. Newcomb RHB split -0.61, HR risk -1.16. tough split lane (-0.61); pitcher suppresses HR (-1.16).""", blast="good"),
            row("Michael Conforto", "L", "N/A", 58, "", ["vs Newcomb"], """0 HR, 1 near-HR, 84.4 mph EV. Newcomb LHB split -1.25, HR risk -1.16. tough split lane (-1.25); pitcher suppresses HR (-1.16)."""),
            row("Pete Crow-Armstrong", "L", "N/A", 58, "", ["vs Newcomb"], """0 HR, 85.1 mph EV. Newcomb LHB split -1.25, HR risk -1.16. tough split lane (-1.25); pitcher suppresses HR (-1.16)."""),
            row("Colson Montgomery", "L", "N/A", 58, "", ["vs Holmes"], """1 HR, 2 near-HR, 96.8 mph EV. Holmes LHB split -0.47, HR risk -0.81. tough split lane (-0.47); pitcher suppresses HR (-0.81).""", blast="good"),
            row("Miguel Vargas", "R", "N/A", 58, "", ["vs Holmes"], """1 HR, 1 near-HR, 90.8 mph EV. Holmes RHB split -0.87, HR risk -0.81. tough split lane (-0.87); pitcher suppresses HR (-0.81).""", blast="good"),
            row("Brenton Doyle", "R", "N/A", 58, "", ["vs Holmes"], """0 HR, 1 near-HR, 88.6 mph EV. Holmes RHB split -0.87, HR risk -0.81. tough split lane (-0.87); pitcher suppresses HR (-0.81)."""),
        ],
    },
    {
        "title": "DET @ PIT - Jackson Jobe 🧤 (R, DET) vs Paul Skenes (R, PIT)",
        "description": "Tail key data: Park boost -3% (stadium -15%, weather +11%). Jobe 🧤 (HR risk 1.24, vs LHB +2.06, vs RHB -1.20). Skenes (HR risk 0.14, vs LHB -0.16, vs RHB +0.49).",
        "rows": [
            row("Oneil Cruz", "L", "+370", 94, "⭐ 🌕 💣", ["vs Jobe"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.8 mph EV. Jobe LHB split +2.06, HR risk 1.24. park suppresses carry (-15%).""", blast="high"),
            row("Brandon Lowe", "L", "+373", 90, "🌕 💣", ["vs Jobe"], """1 HR, 1 near-HR, 92.1 mph EV. Jobe LHB split +2.06, HR risk 1.24. park suppresses carry (-15%).""", blast="good"),
            row("Ben Malgeri", "R", "N/A", 63, "💎", ["vs Skenes"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 89.7 mph EV. Skenes RHB split +0.49, HR risk 0.14. park suppresses carry (-15%).""", blast="good"),
            row("Spencer Torkelson", "R", "+460", 62, "⭐", ["vs Skenes"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 93.1 mph EV. Skenes RHB split +0.49, HR risk 0.14. park suppresses carry (-15%); limited recent HR events.""", blast="good"),
            row("Brett Callahan", "L", "N/A", 64, "", ["vs Skenes"], """1 HR, 1 near-HR, 99.9 mph EV. Skenes LHB split -0.16, HR risk 0.14. slight split headwind (-0.16); park suppresses carry (-15%).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ HOU - Walbert Urena (R, LAA) vs Ethan Pecko (R, HOU)",
        "description": "Tail key data: Park boost +6% (stadium +7%, weather +0%). Urena (HR risk -1.09, vs LHB -0.80, vs RHB -0.89). Pecko.",
        "rows": [
            row("Yordan Alvarez", "L", "+285", 58, "⭐", ["vs Urena"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.4 mph EV. Urena LHB split -0.80, HR risk -1.09. tough split lane (-0.80); pitcher suppresses HR (-1.09).""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 58, "💎", ["vs Urena"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.6 mph EV. Urena RHB split -0.89, HR risk -1.09. tough split lane (-0.89); pitcher suppresses HR (-1.09).""", blast="good"),
            row("Taylor Trammell", "L", "+800", 58, "⭐", ["vs Urena"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 93.4 mph EV. Urena LHB split -0.80, HR risk -1.09. tough split lane (-0.80); pitcher suppresses HR (-1.09).""", blast="good"),
            row("Josh Lowe", "L", "N/A", 58, "💎", ["vs Pecko"], """Worst Pickz Hidden Gem. 0 HR, 88.0 mph EV. limited split/risk sample; limited recent HR events."""),
            row("Travis d'Arnaud", "R", "N/A", 63, "", ["vs Pecko"], """0 HR, 1 near-HR, 94.8 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "LAD @ COL - Roki Sasaki (R, LAD) vs Kyle Freeland (L, COL)",
        "description": "Tail key data: Park boost +26% (stadium +20%, weather +6%). Sasaki (HR risk 0.03, vs LHB -0.50, vs RHB +0.88). Freeland (HR risk 0.49, vs LHB -0.47, vs RHB +0.94).",
        "rows": [
            row("Willi Castro", "S", "+600", 84, "⭐", ["vs Sasaki"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 97.2 mph EV. Sasaki SHB→RHB split +0.88, HR risk 0.03.""", blast="good"),
            row("Mickey Moniak", "L", "+362", 72, "🌕 💣", ["vs Sasaki"], """2 HR, 2 near-HR, 90.8 mph EV. Sasaki LHB split -0.50, HR risk 0.03. tough split lane (-0.50).""", blast="high"),
            row("Zac Veen", "L", "+600", 62, "🚀 💎", ["vs Sasaki"], """Worst Pickz Hidden Gem. 0 HR, 106.0 mph EV. Sasaki LHB split -0.50, HR risk 0.03. tough split lane (-0.50); limited recent HR events.""", blast="good"),
            row("Andy Pages", "R", "+330", 92, "🌕 💣", ["vs Freeland"], """2 HR, 2 near-HR, 96.1 mph EV. Freeland RHB split +0.94, HR risk 0.49.""", blast="high"),
            row("Max Muncy", "L", "+310", 75, "", ["vs Freeland"], """1 HR, 2 near-HR, 94.6 mph EV. Freeland LHB split -0.47, HR risk 0.49. tough split lane (-0.47).""", blast="good"),
            row("Teoscar Hernandez", "R", "+360", 91, "🌕 💣 💎", ["vs Freeland"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 97.4 mph EV. Freeland RHB split +0.94, HR risk 0.49.""", blast="good"),
            row("Shohei Ohtani", "L", "+215", 71, "⭐", ["vs Freeland"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.5 mph EV. Freeland LHB split -0.47, HR risk 0.49. tough split lane (-0.47).""", blast="good"),
            row("Mookie Betts", "R", "+420", 80, "", ["vs Freeland"], """1 HR, 1 near-HR, 89.7 mph EV. Freeland RHB split +0.94, HR risk 0.49.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ PHI - Sandy Alcantara (R, MIA) vs Aaron Nola 🧤 (R, PHI)",
        "description": "Tail key data: Park boost +19% (stadium +16%, weather +3%). Alcantara (HR risk -0.36, vs LHB -0.41, vs RHB -0.08). Nola 🧤 (HR risk 1.27, vs LHB +1.16, vs RHB +0.69).",
        "rows": [
            row("Bryce Harper", "L", "N/A", 58, "⭐", ["vs Alcantara"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 93.8 mph EV. Alcantara LHB split -0.41, HR risk -0.36. tough split lane (-0.41); pitcher risk below avg (-0.36).""", blast="good"),
            row("Kyle Schwarber", "L", "N/A", 78, "🌕 💣", ["vs Alcantara"], """2 HR, 4 near-HR, 96.4 mph EV. Alcantara LHB split -0.41, HR risk -0.36. tough split lane (-0.41); pitcher risk below avg (-0.36).""", blast="high"),
            row("Griffin Conine", "L", "N/A", 97, "🌕 💣", ["vs Nola"], """2 HR, 3 near-HR, 95.3 mph EV. Nola LHB split +1.16, HR risk 1.27.""", blast="high"),
            row("Owen Caissie", "L", "N/A", 90, "🌕 💣", ["vs Nola"], """1 HR, 1 near-HR, 91.3 mph EV. Nola LHB split +1.16, HR risk 1.27.""", blast="good"),
            row("Joe Mack", "L", "N/A", 75, "", ["vs Nola"], """0 HR, 85.9 mph EV. Nola LHB split +1.16, HR risk 1.27. limited recent HR events; lighter EV form (85.9 mph)."""),
        ],
    },
    {
        "title": "NYY @ BAL - Will Warren (R, NYY) vs Chris Bassitt (R, BAL)",
        "description": "Tail key data: Park boost +5% (stadium +0%, weather +5%). Warren (HR risk 0.79, vs LHB +0.32, vs RHB +1.05). Bassitt (HR risk -0.27, vs LHB +0.28, vs RHB -1.19).",
        "rows": [
            row("Leody Taveras", "S", "+521", 86, "", ["vs Warren"], """1 HR, 2 near-HR, 96.6 mph EV. Warren SHB→RHB split +1.05, HR risk 0.79.""", blast="good"),
            row("Pete Alonso", "R", "+199", 84, "💎", ["vs Warren"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.3 mph EV. Warren RHB split +1.05, HR risk 0.79.""", blast="good"),
            row("Dylan Beavers", "L", "+391", 73, "", ["vs Warren"], """0 HR, 1 near-HR, 95.0 mph EV. Warren LHB split +0.32, HR risk 0.79. limited recent HR events.""", blast="good"),
            row("Coby Mayo", "R", "+319", 78, "💎", ["vs Warren"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.0 mph EV. Warren RHB split +1.05, HR risk 0.79. limited recent HR events.""", blast="good"),
            row("Gunnar Henderson", "L", "+252", 71, "", ["vs Warren"], """0 HR, 2 near-HR, 91.5 mph EV. Warren LHB split +0.32, HR risk 0.79.""", blast="good"),
            row("Colton Cowser", "L", "+392", 64, "", ["vs Warren"], """0 HR, 1 near-HR, 90.0 mph EV. Warren LHB split +0.32, HR risk 0.79. limited recent HR events."""),
            row("Spencer Jones", "L", "+291", 74, "🌕 💣", ["vs Bassitt"], """2 HR, 1 near-HR, 96.9 mph EV. Bassitt LHB split +0.28, HR risk -0.27. pitcher risk below avg (-0.27).""", blast="high"),
            row("Trent Grisham", "L", "+226", 70, "🌕 💣", ["vs Bassitt"], """2 HR, 2 near-HR, 90.8 mph EV. Bassitt LHB split +0.28, HR risk -0.27. pitcher risk below avg (-0.27).""", blast="high"),
            row("Jazz Chisholm Jr.", "L", "+271", 69, "🌕 💣", ["vs Bassitt"], """2 HR, 2 near-HR, 89.5 mph EV. Bassitt LHB split +0.28, HR risk -0.27. pitcher risk below avg (-0.27).""", blast="high"),
            row("Heliot Ramos", "R", "+353", 58, "", ["vs Bassitt"], """0 HR, 96.3 mph EV. Bassitt RHB split -1.19, HR risk -0.27. tough split lane (-1.19); pitcher risk below avg (-0.27).""", blast="good"),
            row("Ryan McMahon", "L", "+378", 58, "", ["vs Bassitt"], """0 HR, 1 near-HR, 92.8 mph EV. Bassitt LHB split +0.28, HR risk -0.27. pitcher risk below avg (-0.27); limited recent HR events.""", blast="good"),
            row("Luis Garcia Jr.", "L", "+265", 59, "💎", ["vs Bassitt"], """Worst Pickz Hidden Gem. 0 HR, 94.9 mph EV. Bassitt LHB split +0.28, HR risk -0.27. pitcher risk below avg (-0.27); limited recent HR events.""", blast="good"),
            row("Ben Rice", "L", "+196", 62, "⭐", ["vs Bassitt"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.6 mph EV. Bassitt LHB split +0.28, HR risk -0.27. pitcher risk below avg (-0.27); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "SD @ NYM - Michael King (R, SD) vs Robert Stock (R, NYM)",
        "description": "Tail key data: Park boost +2% (stadium -1%, weather +3%). King (HR risk 0.34, vs LHB +0.32, vs RHB +0.16). Stock (HR risk -0.30, vs LHB -0.05, vs RHB -0.78).",
        "rows": [
            row("Francisco Lindor", "S", "+324", 69, "", ["vs King"], """1 HR, 2 near-HR, 93.0 mph EV. King SHB→LHB split +0.32, HR risk 0.34.""", blast="good"),
            row("Brett Baty", "L", "+536", 71, "💎", ["vs King"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.1 mph EV. King LHB split +0.32, HR risk 0.34.""", blast="good"),
            row("Bo Bichette", "R", "+473", 71, "⭐", ["vs King"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.5 mph EV. King RHB split +0.16, HR risk 0.34.""", blast="good"),
            row("Jackson Merrill", "L", "+308", 63, "🚀", ["vs Stock"], """1 HR, 2 near-HR, 100.9 mph EV. Stock LHB split -0.05, HR risk -0.30. slight split headwind (-0.05); pitcher risk below avg (-0.30).""", blast="good"),
            row("Manny Machado", "R", "+237", 58, "", ["vs Stock"], """1 HR, 1 near-HR, 92.4 mph EV. Stock RHB split -0.78, HR risk -0.30. tough split lane (-0.78); pitcher risk below avg (-0.30).""", blast="good"),
            row("Luis Campusano", "R", "+417", 58, "", ["vs Stock"], """0 HR, 2 near-HR, 89.2 mph EV. Stock RHB split -0.78, HR risk -0.30. tough split lane (-0.78); pitcher risk below avg (-0.30).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ MIL - Logan Gilbert (R, SEA) vs Dustin May (R, MIL)",
        "description": "Tail key data: Park boost -2% (stadium -1%, weather -2%). Gilbert (HR risk 0.47, vs LHB +0.19, vs RHB +0.63). May (HR risk -0.29, vs LHB -0.47, vs RHB +0.09).",
        "rows": [
            row("Jackson Chourio", "R", "N/A", 82, "", ["vs Gilbert"], """1 HR, 3 near-HR, 97.3 mph EV. Gilbert RHB split +0.63, HR risk 0.47.""", blast="good"),
            row("William Contreras", "R", "N/A", 64, "⭐", ["vs Gilbert"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 91.5 mph EV. Gilbert RHB split +0.63, HR risk 0.47. limited recent HR events."""),
            row("Brice Turang", "L", "N/A", 67, "", ["vs Gilbert"], """0 HR, 95.7 mph EV. Gilbert LHB split +0.19, HR risk 0.47. limited recent HR events.""", blast="good"),
            row("Gary Sanchez", "R", "N/A", 60, "", ["vs Gilbert"], """0 HR, 89.0 mph EV. Gilbert RHB split +0.63, HR risk 0.47. limited recent HR events."""),
            row("Christian Yelich", "L", "N/A", 80, "🌕 💣", ["vs Gilbert"], """2 HR, 2 near-HR, 94.0 mph EV. Gilbert LHB split +0.19, HR risk 0.47.""", blast="high"),
            row("Garrett Mitchell", "L", "N/A", 64, "", ["vs Gilbert"], """0 HR, 92.4 mph EV. Gilbert LHB split +0.19, HR risk 0.47. limited recent HR events.""", blast="good"),
            row("Luis Lara", "S", "N/A", 69, "💎", ["vs Gilbert"], """Worst Pickz Hidden Gem. 0 HR, 94.0 mph EV. Gilbert SHB→RHB split +0.63, HR risk 0.47. limited recent HR events.""", blast="good"),
            row("Dominic Canzone", "L", "N/A", 58, "⭐", ["vs May"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.2 mph EV. May LHB split -0.47, HR risk -0.29. tough split lane (-0.47); pitcher risk below avg (-0.29).""", blast="good"),
            row("Brock Rodden", "S", "N/A", 58, "", ["vs May"], """0 HR, 1 near-HR, 91.5 mph EV. May SHB→RHB split +0.09, HR risk -0.29. pitcher risk below avg (-0.29); limited recent HR events."""),
        ],
    },
    {
        "title": "SF @ CLE - Matt Wilkinson (L, SF) vs Parker Messick (L, CLE)",
        "description": "Tail key data: Park boost -6% (stadium -4%, weather -3%). Wilkinson. Messick (HR risk -0.45, vs LHB -0.38, vs RHB -0.14).",
        "rows": [
            row("Jo Adell", "R", "N/A", 60, "⭐", ["vs Wilkinson"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 89.6 mph EV. limited split/risk sample; park/weather net drag (-6%).""", blast="good"),
            row("Rhys Hoskins", "R", "N/A", 64, "", ["vs Wilkinson"], """1 HR, 1 near-HR, 95.5 mph EV. limited split/risk sample; park/weather net drag (-6%).""", blast="good"),
            row("Nathaniel Lowe", "L", "N/A", 61, "", ["vs Wilkinson"], """1 HR, 1 near-HR, 92.0 mph EV. limited split/risk sample; park/weather net drag (-6%).""", blast="good"),
            row("Victor Bericoto", "R", "N/A", 58, "", ["vs Messick"], """0 HR, 1 near-HR, 97.0 mph EV. Messick RHB split -0.14, HR risk -0.45. slight split headwind (-0.14); pitcher suppresses HR (-0.45).""", blast="good"),
            row("Rafael Devers", "L", "N/A", 58, "", ["vs Messick"], """0 HR, 95.5 mph EV. Messick LHB split -0.38, HR risk -0.45. slight split headwind (-0.38); pitcher suppresses HR (-0.45).""", blast="good"),
            row("Bryce Eldridge", "L", "N/A", 58, "", ["vs Messick"], """0 HR, 93.7 mph EV. Messick LHB split -0.38, HR risk -0.45. slight split headwind (-0.38); pitcher suppresses HR (-0.45).""", blast="good"),
        ],
    },
    {
        "title": "STL @ CIN - Matthew Liberatore (L, STL) vs Chase Burns (R, CIN)",
        "description": "Tail key data: Park boost +17% (stadium +14%, weather +3%). Liberatore (HR risk 0.19, vs LHB +0.69, vs RHB +0.22). Burns (HR risk -0.70, vs LHB -0.41, vs RHB -0.63).",
        "rows": [
            row("Elly De La Cruz", "S", "+282", 61, "", ["vs Liberatore"], """0 HR, 90.2 mph EV. Liberatore SHB→LHB split +0.69, HR risk 0.19. limited recent HR events."""),
            row("Tyler Stephenson", "R", "N/A", 58, "⭐", ["vs Liberatore"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 89.8 mph EV. Liberatore RHB split +0.22, HR risk 0.19. limited recent HR events."""),
            row("Dane Myers", "R", "+323", 65, "", ["vs Liberatore"], """1 HR, 1 near-HR, 88.8 mph EV. Liberatore RHB split +0.22, HR risk 0.19.""", blast="good"),
            row("Ivan Herrera", "R", "+322", 58, "", ["vs Burns"], """0 HR, 96.3 mph EV. Burns RHB split -0.63, HR risk -0.70. tough split lane (-0.63); pitcher suppresses HR (-0.70).""", blast="good"),
            row("Jimmy Crooks", "L", "N/A", 58, "💎", ["vs Burns"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.1 mph EV. Burns LHB split -0.41, HR risk -0.70. tough split lane (-0.41); pitcher suppresses HR (-0.70).""", blast="good"),
            row("Alec Burleson", "L", "+179", 58, "", ["vs Burns"], """1 HR, 1 near-HR, 95.0 mph EV. Burns LHB split -0.41, HR risk -0.70. tough split lane (-0.41); pitcher suppresses HR (-0.70).""", blast="good"),
            row("JJ Wetherholt", "L", "+321", 58, "", ["vs Burns"], """0 HR, 90.5 mph EV. Burns LHB split -0.41, HR risk -0.70. tough split lane (-0.41); pitcher suppresses HR (-0.70)."""),
            row("Joshua Baez", "R", "+344", 58, "", ["vs Burns"], """0 HR, 93.8 mph EV. Burns RHB split -0.63, HR risk -0.70. tough split lane (-0.63); pitcher suppresses HR (-0.70).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ TB - Max Scherzer 🧤 (R, TOR) vs Drew Rasmussen (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Scherzer 🧤 (HR risk 1.08, vs LHB +0.68, vs RHB +1.25). Rasmussen (HR risk -0.84, vs LHB -0.77, vs RHB -0.48).",
        "rows": [
            row("Jonny DeLuca", "R", "N/A", 92, "🌕 💣", ["vs Scherzer"], """2 HR, 2 near-HR, 93.0 mph EV. Scherzer RHB split +1.25, HR risk 1.08.""", blast="high"),
            row("Jorge Mateo", "R", "N/A", 84, "", ["vs Scherzer"], """1 HR, 1 near-HR, 91.9 mph EV. Scherzer RHB split +1.25, HR risk 1.08.""", blast="good"),
            row("Jonathan Aranda", "L", "+420", 75, "⭐", ["vs Scherzer"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 89.6 mph EV. Scherzer LHB split +0.68, HR risk 1.08.""", blast="good"),
            row("Richie Palacios", "L", "+820", 77, "", ["vs Scherzer"], """0 HR, 94.2 mph EV. Scherzer LHB split +0.68, HR risk 1.08. limited recent HR events.""", blast="good"),
            row("Jesus Sanchez", "L", "+810", 58, "", ["vs Rasmussen"], """1 HR, 2 near-HR, 97.3 mph EV. Rasmussen LHB split -0.77, HR risk -0.84. tough split lane (-0.77); pitcher suppresses HR (-0.84).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ TEX - Cade Cavalli (R, WSH) vs Kumar Rocker (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -9%, weather -1%). Cavalli (HR risk 0.36, vs LHB +0.05, vs RHB +0.75). Rocker (HR risk 0.16, vs LHB -0.03, vs RHB +0.37).",
        "rows": [
            row("Corey Seager", "L", "+420", 58, "", ["vs Cavalli"], """0 HR, 92.4 mph EV. Cavalli LHB split +0.05, HR risk 0.36. park/weather net drag (-11%); limited recent HR events.""", blast="good"),
            row("Joc Pederson", "L", "+441", 58, "", ["vs Cavalli"], """0 HR, 1 near-HR, 92.9 mph EV. Cavalli LHB split +0.05, HR risk 0.36. park/weather net drag (-11%); limited recent HR events.""", blast="good"),
            row("Evan Carter", "L", "+910", 58, "", ["vs Cavalli"], """0 HR, 2 near-HR, 86.3 mph EV. Cavalli LHB split +0.05, HR risk 0.36. park/weather net drag (-11%); lighter EV form (86.3 mph).""", blast="good"),
            row("Abimelec Ortiz", "L", "+515", 70, "🌕 💣 💎", ["vs Rocker"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.3 mph EV. Rocker LHB split -0.03, HR risk 0.16. slight split headwind (-0.03); park/weather net drag (-11%).""", blast="high"),
            row("Jose Tena", "L", "N/A", 59, "⭐", ["vs Rocker"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.0 mph EV. Rocker LHB split -0.03, HR risk 0.16. slight split headwind (-0.03); park/weather net drag (-11%).""", blast="good"),
            row("CJ Abrams", "L", "+358", 58, "", ["vs Rocker"], """0 HR, 88.0 mph EV. Rocker LHB split -0.03, HR risk 0.16. slight split headwind (-0.03); park/weather net drag (-11%)."""),
            row("Dylan Crews", "R", "+600", 58, "", ["vs Rocker"], """0 HR, 2 near-HR, 87.5 mph EV. Rocker RHB split +0.37, HR risk 0.16. park/weather net drag (-11%); lighter EV form (87.5 mph).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-19")

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

    out = ROOT / '_games-0819.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
