#!/usr/bin/env python3
"""Generate games[] block for 2026-06-23 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Bryan Reynolds (S)",
    "Bryce Eldridge (L)",
    "Byron Buxton (R)",
    "Colson Montgomery (L)",
    "Dominic Canzone (L)",
    "James Wood (L)",
    "Jordan Walker (R)",
    "Kazuma Okamoto (R)",
    "Matt Shaw (R)",
    "Max Muncy (R)",
    "Nick Kurtz (L)",
    "Pete Crow-Armstrong (L)",
    "Randal Grichuk (R)",
}

GEMS = {
    "Brandon Valenzuela (S)",
    "Fernando Tatis Jr. (R)",
    "Juan Soto (L)",
    "Nelson Velazquez (R)",
    "Ryan Vilade (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Alex Jackson (R)": "MIN",
    "Andrew Vaughn (R)": "MIL",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Brandon Valenzuela (S)": "TOR",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "Cam Smith (R)": "HOU",
    "Carson Benge (L)": "NYM",
    "Ceddanne Rafaela (R)": "BOS",
    "Christian Walker (R)": "HOU",
    "Cole Young (L)": "SEA",
    "Colson Montgomery (L)": "CWS",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "Davis Schneider (R)": "TOR",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Dominic Smith (L)": "ATL",
    "Donovan Walton (L)": "LAA",
    "Edouard Julien (L)": "COL",
    "Endy Rodriguez (S)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Freddie Freeman (L)": "LAD",
    "Gunnar Henderson (L)": "BAL",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "James Wood (L)": "WSH",
    "Jeremy Pena (R)": "HOU",
    "Jesus Sanchez (L)": "TOR",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "John Rave (L)": "KC",
    "Jonah Cox (R)": "SF",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Junior Perez (R)": "CWS",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Logan O'Hoppe (R)": "LAA",
    "Luis Garcia Jr. (L)": "WSH",
    "Luke Raley (L)": "SEA",
    "Maikel Garcia (R)": "KC",
    "Marcell Ozuna (R)": "PIT",
    "Marcelo Mayer (L)": "BOS",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Matt Shaw (R)": "CHC",
    "Max Muncy (R)": "ATH",
    "Michael Massey (L)": "KC",
    "Miguel Amaya (R)": "CHC",
    "Mike Yastrzemski (L)": "ATL",
    "Mookie Betts (R)": "LAD",
    "Nelson Velazquez (R)": "STL",
    "Nick Kurtz (L)": "ATH",
    "Paul Goldschmidt (R)": "NYY",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Riley Greene (L)": "DET",
    "Royce Lewis (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Ryan Vilade (R)": "TB",
    "Salvador Perez (R)": "KC",
    "Samad Taylor (R)": "SD",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Horwitz (L)": "PIT",
    "Spencer Jones (L)": "NYY",
    "Ty France (R)": "SD",
    "Tyler Callihan (L)": "PIT",
    "Tyler Stephenson (R)": "CIN",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Will Wagner (L)": "SD",
    "William Contreras (R)": "MIL",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_RISK_MIN = 0.95

BUM_PITCHERS = {
    "Cabrera",
    "Civale",
    "Johnson",
    "Ryan",
    "Senga",
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

def add_bum_row_emojis(entry):
    chip = entry["chips"][0].replace("vs ", "").strip()
    if chip not in BUM_PITCHERS:
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
        "title": "ARI @ STL - Eduardo Rodriguez (L, ARI) vs Kyle Leahy (R, STL)",
        "description": "Tail key data: Park boost -20% (stadium -9%, weather -12%). Rodriguez (HR risk -0.13, vs LHB -0.52, vs RHB +0.11). Leahy (HR risk 0.24, vs LHB +0.70, vs RHB -0.26).",
        "rows": [
            row("Jordan Walker", "R", "N/A", 80, "⭐", ["vs Rodriguez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.5 mph EV. Rodriguez RHB split +0.11, HR risk -0.13. pitcher risk below avg (-0.13); park/weather net drag (-20%).""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 80, "💎", ["vs Rodriguez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.0 mph EV. Rodriguez RHB split +0.11, HR risk -0.13. pitcher risk below avg (-0.13); park/weather net drag (-20%).""", blast="good"),
            row("Alec Burleson", "L", "N/A", 64, "", ["vs Rodriguez"], """0 HR, 90.2 mph EV. Rodriguez LHB split -0.52, HR risk -0.13. tough split lane (-0.52); pitcher risk below avg (-0.13)."""),
            row("Corbin Carroll", "L", "N/A", 76, "", ["vs Leahy"], """1 HR, 2 near-HR, 92.1 mph EV. Leahy LHB split +0.70, HR risk 0.24. park/weather net drag (-20%).""", blast="good"),
            row("Ketel Marte", "S", "N/A", 71, "", ["vs Leahy"], """0 HR, 95.3 mph EV. Leahy RHB split -0.26, HR risk 0.24. slight split headwind (-0.26); park/weather net drag (-20%).""", blast="good"),
        ],
    },
    {
        "title": "ATH @ SF - Aaron Civale 🧤 (R, ATH) vs Robbie Ray (L, SF)",
        "description": "Tail key data: Park boost -20% (stadium -13%, weather -6%). Civale 🧤 (HR risk 1.11, vs LHB +1.22, vs RHB +0.50). Ray (HR risk -0.03, vs LHB -0.17, vs RHB +0.02).",
        "rows": [
            row("Max Muncy", "R", "N/A", 62, "⭐", ["vs Ray"], """Worst Pickz Favorite. 0 HR, 85.6 mph EV. Ray RHB split +0.02, HR risk -0.03. pitcher risk below avg (-0.03); park/weather net drag (-20%)."""),
            row("Bryce Eldridge", "L", "N/A", 96, "⭐ 🌕 💣", ["vs Civale"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 98.5 mph EV. Civale LHB split +1.22, HR risk 1.11. park/weather net drag (-20%).""", blast="high"),
            row("Rafael Devers", "L", "N/A", 80, "", ["vs Civale"], """1 HR, 1 near-HR, 98.1 mph EV. Civale LHB split +1.22, HR risk 1.11. park/weather net drag (-20%).""", blast="good"),
            row("Jonah Cox", "R", "N/A", 71, "", ["vs Civale"], """0 HR, 95.3 mph EV. Civale RHB split +0.50, HR risk 1.11. park/weather net drag (-20%); limited recent HR events.""", blast="good"),
            row("Nick Kurtz", "L", "N/A", 88, "⭐ 🌕 💣", ["vs Ray"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.2 mph EV. Ray LHB split -0.17, HR risk -0.03. slight split headwind (-0.17); pitcher risk below avg (-0.03).""", blast="high"),
            row("Henry Bolte", "R", "N/A", 90, "🚀 🌕 💣", ["vs Ray"], """2 HR, 2 near-HR, 100.7 mph EV. Ray RHB split +0.02, HR risk -0.03. pitcher risk below avg (-0.03); park/weather net drag (-20%).""", blast="high"),
            row("Zack Gelof", "R", "N/A", 83, "🌕 💣", ["vs Ray"], """2 HR, 3 near-HR, 91.4 mph EV. Ray RHB split +0.02, HR risk -0.03. pitcher risk below avg (-0.03); park/weather net drag (-20%).""", blast="high"),
            row("Shea Langeliers", "R", "N/A", 70, "", ["vs Ray"], """1 HR, 1 near-HR, 88.4 mph EV. Ray RHB split +0.02, HR risk -0.03. pitcher risk below avg (-0.03); park/weather net drag (-20%).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ SD - JR Ritchie (R, ATL) vs German Marquez (R, SD)",
        "description": "Tail key data: Park boost -6% (stadium -4%, weather -2%). Ritchie (HR risk 0.20, vs LHB +0.72, vs RHB -0.82). Home starter risk unavailable.",
        "rows": [
            row("Ty France", "R", "N/A", 81, "🌕 💣", ["vs Ritchie"], """2 HR, 2 near-HR, 90.6 mph EV. Ritchie RHB split -0.82, HR risk 0.20. tough split lane (-0.82); park/weather net drag (-6%).""", blast="high"),
            row("Will Wagner", "L", "N/A", 62, "", ["vs Ritchie"], """0 HR, 83.9 mph EV. Ritchie LHB split +0.72, HR risk 0.20. park/weather net drag (-6%); limited recent HR events."""),
            row("Fernando Tatis Jr.", "R", "N/A", 85, "💎", ["vs Ritchie"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 98.7 mph EV. Ritchie RHB split -0.82, HR risk 0.20. tough split lane (-0.82); park/weather net drag (-6%).""", blast="good"),
            row("Samad Taylor", "R", "N/A", 62, "", ["vs Ritchie"], """0 HR, 79.6 mph EV. Ritchie RHB split -0.82, HR risk 0.20. tough split lane (-0.82); park/weather net drag (-6%)."""),
            row("Matt Olson", "L", "+340", 81, "", ["vs Marquez"], """1 HR, 2 near-HR, 97.2 mph EV. Marquez split/risk data unavailable. limited split/risk sample; park/weather net drag (-6%).""", blast="good"),
            row("Mike Yastrzemski", "L", "+650", 75, "", ["vs Marquez"], """1 HR, 1 near-HR, 92.9 mph EV. Marquez split/risk data unavailable. limited split/risk sample; park/weather net drag (-6%).""", blast="good"),
            row("Dominic Smith", "L", "+630", 68, "", ["vs Marquez"], """0 HR, 2 near-HR, 84.9 mph EV. Marquez split/risk data unavailable. limited split/risk sample; park/weather net drag (-6%).""", blast="good"),
        ],
    },
    {
        "title": "BAL @ LAA - Shane Baz (R, BAL) vs Ryan Johnson 🧤 (R, LAA)",
        "description": "Tail key data: Park boost +10% (stadium +10%, weather +0%). Baz (HR risk -0.72, vs LHB -0.57, vs RHB -0.50). Johnson 🧤 (HR risk 1.45, vs LHB +0.81, vs RHB +1.48).",
        "rows": [
            row("Zach Neto", "R", "N/A", 83, "🌕 💣", ["vs Baz"], """2 HR, 2 near-HR, 93.1 mph EV. Baz RHB split -0.50, HR risk -0.72. tough split lane (-0.50); pitcher suppresses HR (-0.72).""", blast="high"),
            row("Donovan Walton", "L", "N/A", 78, "🌕 💣", ["vs Baz"], """2 HR, 2 near-HR, 82.0 mph EV. Baz LHB split -0.57, HR risk -0.72. tough split lane (-0.57); pitcher suppresses HR (-0.72).""", blast="high"),
            row("Logan O'Hoppe", "R", "N/A", 74, "", ["vs Baz"], """1 HR, 2 near-HR, 90.1 mph EV. Baz RHB split -0.50, HR risk -0.72. tough split lane (-0.50); pitcher suppresses HR (-0.72).""", blast="good"),
            row("Jo Adell", "R", "N/A", 62, "", ["vs Baz"], """0 HR, 84.3 mph EV. Baz RHB split -0.50, HR risk -0.72. tough split lane (-0.50); pitcher suppresses HR (-0.72)."""),
            row("Gunnar Henderson", "L", "N/A", 86, "🌕 💣", ["vs Johnson"], """2 HR, 2 near-HR, 96.4 mph EV. Johnson LHB split +0.81, HR risk 1.45.""", blast="high"),
            row("Pete Alonso", "R", "N/A", 87, "🌕 💣", ["vs Johnson"], """3 HR, 3 near-HR, 91.3 mph EV. Johnson RHB split +1.48, HR risk 1.45.""", blast="high"),
        ],
    },
    {
        "title": "BOS @ COL - Sonny Gray (R, BOS) vs Sean Sullivan (L, COL)",
        "description": "Tail key data: Park boost +18% (stadium +21%, weather -3%). Gray (HR risk -0.43, vs LHB -0.15, vs RHB -0.59). Home starter risk unavailable.",
        "rows": [
            row("Hunter Goodman", "R", "+200", 76, "🌕 💣", ["vs Gray"], """2 HR, 1 near-HR, 87.7 mph EV. Gray RHB split -0.59, HR risk -0.43. tough split lane (-0.59); pitcher suppresses HR (-0.43).""", blast="high"),
            row("Edouard Julien", "L", "N/A", 76, "", ["vs Gray"], """0 HR, 2 near-HR, 95.6 mph EV. Gray LHB split -0.15, HR risk -0.43. slight split headwind (-0.15); pitcher suppresses HR (-0.43).""", blast="good"),
            row("Marcelo Mayer", "L", "N/A", 70, "", ["vs Sullivan"], """1 HR, 1 near-HR, 82.4 mph EV. Sullivan split/risk data unavailable. limited split/risk sample; lighter EV form (82.4 mph).""", blast="good"),
            row("Ceddanne Rafaela", "R", "+245", 70, "", ["vs Sullivan"], """1 HR, 1 near-HR, 87.7 mph EV. Sullivan split/risk data unavailable. limited split/risk sample; lighter EV form (87.7 mph).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ NYM - Edward Cabrera 🧤 (R, CHC) vs Kodai Senga 🧤 (R, NYM)",
        "description": "Tail key data: Park boost -9% (stadium -1%, weather -8%). Cabrera 🧤 (HR risk 1.26, vs LHB +0.74, vs RHB +1.27). Senga 🧤 (HR risk 1.41, vs LHB +0.77, vs RHB +1.32).",
        "rows": [
            row("Juan Soto", "L", "+250", 82, "🌕 💣 💎", ["vs Cabrera"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 89.7 mph EV. Cabrera LHB split +0.74, HR risk 1.26. park/weather net drag (-9%).""", blast="high"),
            row("Carson Benge", "L", "+354", 83, "🌕 💣", ["vs Cabrera"], """2 HR, 3 near-HR, 90.8 mph EV. Cabrera LHB split +0.74, HR risk 1.26. park/weather net drag (-9%).""", blast="high"),
            row("Pete Crow-Armstrong", "L", "+191", 82, "⭐ 🌕 💣", ["vs Senga"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 89.5 mph EV. Senga LHB split +0.77, HR risk 1.41. park/weather net drag (-9%).""", blast="high"),
            row("Miguel Amaya", "R", "N/A", 73, "", ["vs Senga"], """0 HR, 2 near-HR, 93.4 mph EV. Senga RHB split +1.32, HR risk 1.41. park/weather net drag (-9%).""", blast="good"),
            row("Matt Shaw", "R", "+413", 73, "⭐", ["vs Senga"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.1 mph EV. Senga RHB split +1.32, HR risk 1.41. park/weather net drag (-9%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CLE @ CWS - Parker Messick (L, CLE) vs Sean Burke (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Messick (HR risk -0.79, vs LHB -0.48, vs RHB -0.66). Burke (HR risk -0.03, vs LHB +0.30, vs RHB -0.63).",
        "rows": [
            row("Randal Grichuk", "R", "N/A", 90, "⭐ 🌕 💣", ["vs Messick"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 94.1 mph EV. Messick RHB split -0.66, HR risk -0.79. tough split lane (-0.66); pitcher suppresses HR (-0.79).""", blast="high"),
            row("Junior Perez", "R", "N/A", 75, "", ["vs Messick"], """1 HR, 1 near-HR, 92.9 mph EV. Messick RHB split -0.66, HR risk -0.79. tough split lane (-0.66); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Colson Montgomery", "L", "N/A", 86, "⭐ 🌕 💣", ["vs Messick"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 90.0 mph EV. Messick LHB split -0.48, HR risk -0.79. tough split lane (-0.48); pitcher suppresses HR (-0.79).""", blast="high"),
        ],
    },
    {
        "title": "HOU @ TOR - Peter Lambert (R, HOU) vs Shane Bieber (R, TOR)",
        "description": "Tail key data: Park boost +6% (stadium +6%, weather +0%). Lambert (HR risk -0.31, vs LHB -0.73, vs RHB +0.28). Bieber (HR risk 0.65, vs LHB -0.64, vs RHB +1.77).",
        "rows": [
            row("Kazuma Okamoto", "R", "+320", 84, "⭐ 🌕 💣", ["vs Lambert"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 91.9 mph EV. Lambert RHB split +0.28, HR risk -0.31. pitcher risk below avg (-0.31).""", blast="high"),
            row("Brandon Valenzuela", "S", "N/A", 96, "🌕 💣 💎", ["vs Lambert"], """Worst Pickz Hidden Gem. 3 HR, 6 near-HR, 93.7 mph EV. Lambert RHB split +0.28, HR risk -0.31. pitcher risk below avg (-0.31).""", blast="high"),
            row("Davis Schneider", "R", "N/A", 70, "", ["vs Lambert"], """1 HR, 1 near-HR, 82.5 mph EV. Lambert RHB split +0.28, HR risk -0.31. pitcher risk below avg (-0.31); lighter EV form (82.5 mph).""", blast="good"),
            row("Vladimir Guerrero Jr.", "R", "+490", 73, "", ["vs Lambert"], """1 HR, 1 near-HR, 90.8 mph EV. Lambert RHB split +0.28, HR risk -0.31. pitcher risk below avg (-0.31).""", blast="good"),
            row("Jesus Sanchez", "L", "+490", 75, "", ["vs Lambert"], """1 HR, 2 near-HR, 90.8 mph EV. Lambert LHB split -0.73, HR risk -0.31. tough split lane (-0.73); pitcher risk below avg (-0.31).""", blast="good"),
            row("Yordan Alvarez", "L", "+260", 71, "", ["vs Bieber"], """1 HR, 1 near-HR, 89.3 mph EV. Bieber LHB split -0.64, HR risk 0.65. tough split lane (-0.64).""", blast="good"),
            row("Jeremy Pena", "R", "N/A", 78, "🌕 💣", ["vs Bieber"], """2 HR, 2 near-HR, 84.7 mph EV. Bieber RHB split +1.77, HR risk 0.65. lighter EV form (84.7 mph).""", blast="high"),
            row("Christian Walker", "R", "+420", 81, "", ["vs Bieber"], """1 HR, 2 near-HR, 96.6 mph EV. Bieber RHB split +1.77, HR risk 0.65.""", blast="good"),
            row("Cam Smith", "R", "+610", 72, "", ["vs Bieber"], """0 HR, 96.4 mph EV. Bieber RHB split +1.77, HR risk 0.65. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "KC @ TB - Luinder Avila (R, KC) vs Shane McClanahan (L, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Avila (HR risk -0.73, vs LHB -0.21, vs RHB -0.88). McClanahan (HR risk -0.86, vs LHB -0.88, vs RHB -0.64).",
        "rows": [
            row("Ryan Vilade", "R", "+920", 82, "🚀 💎", ["vs Avila"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 100.1 mph EV. Avila RHB split -0.88, HR risk -0.73. tough split lane (-0.88); pitcher suppresses HR (-0.73).""", blast="good"),
            row("Jonathan Aranda", "L", "+490", 73, "", ["vs Avila"], """1 HR, 1 near-HR, 91.2 mph EV. Avila LHB split -0.21, HR risk -0.73. slight split headwind (-0.21); pitcher suppresses HR (-0.73).""", blast="good"),
            row("Junior Caminero", "R", "+310", 74, "", ["vs Avila"], """0 HR, 97.8 mph EV. Avila RHB split -0.88, HR risk -0.73. tough split lane (-0.88); pitcher suppresses HR (-0.73).""", blast="good"),
            row("Jac Caglianone", "L", "+570", 83, "🌕 💣", ["vs McClanahan"], """2 HR, 3 near-HR, 91.0 mph EV. McClanahan LHB split -0.88, HR risk -0.86. tough split lane (-0.88); pitcher suppresses HR (-0.86).""", blast="high"),
            row("Bobby Witt Jr.", "R", "N/A", 79, "", ["vs McClanahan"], """1 HR, 1 near-HR, 97.2 mph EV. McClanahan RHB split -0.64, HR risk -0.86. tough split lane (-0.64); pitcher suppresses HR (-0.86).""", blast="good"),
            row("John Rave", "L", "N/A", 78, "🚀", ["vs McClanahan"], """0 HR, 1 near-HR, 102.8 mph EV. McClanahan LHB split -0.88, HR risk -0.86. tough split lane (-0.88); pitcher suppresses HR (-0.86).""", blast="good"),
            row("Maikel Garcia", "R", "+790", 71, "", ["vs McClanahan"], """0 HR, 1 near-HR, 92.8 mph EV. McClanahan RHB split -0.64, HR risk -0.86. tough split lane (-0.64); pitcher suppresses HR (-0.86).""", blast="good"),
            row("Salvador Perez", "R", "+390", 69, "", ["vs McClanahan"], """0 HR, 2 near-HR, 89.4 mph EV. McClanahan RHB split -0.64, HR risk -0.86. tough split lane (-0.64); pitcher suppresses HR (-0.86).""", blast="good"),
            row("Michael Massey", "L", "N/A", 70, "", ["vs McClanahan"], """1 HR, 1 near-HR, 79.8 mph EV. McClanahan LHB split -0.88, HR risk -0.86. tough split lane (-0.88); pitcher suppresses HR (-0.86).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ MIN - Justin Wrobleski (L, LAD) vs Joe Ryan 🧤 (R, MIN)",
        "description": "Tail key data: Park boost -8% (stadium -6%, weather -2%). Wrobleski (HR risk -0.24, vs LHB +0.26, vs RHB -0.32). Ryan 🧤 (HR risk 1.45, vs LHB +0.81, vs RHB +1.48).",
        "rows": [
            row("Byron Buxton", "R", "+245", 76, "⭐", ["vs Wrobleski"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 92.2 mph EV. Wrobleski RHB split -0.32, HR risk -0.24. slight split headwind (-0.32); pitcher risk below avg (-0.24).""", blast="good"),
            row("Royce Lewis", "R", "+420", 72, "", ["vs Wrobleski"], """0 HR, 1 near-HR, 93.5 mph EV. Wrobleski RHB split -0.32, HR risk -0.24. slight split headwind (-0.32); pitcher risk below avg (-0.24).""", blast="good"),
            row("Alex Jackson", "R", "+590", 70, "", ["vs Wrobleski"], """0 HR, 93.5 mph EV. Wrobleski RHB split -0.32, HR risk -0.24. slight split headwind (-0.32); pitcher risk below avg (-0.24).""", blast="good"),
            row("Shohei Ohtani", "L", "+198", 88, "🌕 💣", ["vs Ryan"], """2 HR, 3 near-HR, 95.5 mph EV. Ryan LHB split +0.81, HR risk 1.45. park/weather net drag (-8%).""", blast="high"),
            row("Freddie Freeman", "L", "+410", 70, "", ["vs Ryan"], """1 HR, 1 near-HR, 84.5 mph EV. Ryan LHB split +0.81, HR risk 1.45. park/weather net drag (-8%); lighter EV form (84.5 mph).""", blast="good"),
            row("Mookie Betts", "R", "+570", 80, "🌕 💣", ["vs Ryan"], """2 HR, 3 near-HR, 87.2 mph EV. Ryan RHB split +1.48, HR risk 1.45. park/weather net drag (-8%); lighter EV form (87.2 mph).""", blast="high"),
            row("Dalton Rushing", "L", "N/A", 72, "", ["vs Ryan"], """1 HR, 1 near-HR, 90.5 mph EV. Ryan LHB split +0.81, HR risk 1.45. park/weather net drag (-8%).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ CIN - Brandon Sproat (R, MIL) vs Nick Lodolo (L, CIN)",
        "description": "Tail key data: Park boost +11% (stadium +14%, weather -3%). Sproat (HR risk 0.14, vs LHB -0.20, vs RHB +0.65). Lodolo (HR risk -0.13, vs LHB -1.09, vs RHB +0.29).",
        "rows": [
            row("Eugenio Suarez", "R", "+410", 86, "🌕 💣", ["vs Sproat"], """3 HR, 3 near-HR, 90.3 mph EV. Sproat RHB split +0.65, HR risk 0.14.""", blast="high"),
            row("Matt McLain", "R", "N/A", 72, "", ["vs Sproat"], """0 HR, 1 near-HR, 94.4 mph EV. Sproat RHB split +0.65, HR risk 0.14. limited recent HR events.""", blast="good"),
            row("Tyler Stephenson", "R", "+570", 84, "🌕 💣", ["vs Sproat"], """2 HR, 2 near-HR, 93.7 mph EV. Sproat RHB split +0.65, HR risk 0.14.""", blast="high"),
            row("Andrew Vaughn", "R", "+470", 81, "", ["vs Lodolo"], """1 HR, 1 near-HR, 99.1 mph EV. Lodolo RHB split +0.29, HR risk -0.13. pitcher risk below avg (-0.13).""", blast="good"),
            row("William Contreras", "R", "+370", 67, "", ["vs Lodolo"], """0 HR, 1 near-HR, 91.4 mph EV. Lodolo RHB split +0.29, HR risk -0.13. pitcher risk below avg (-0.13); limited recent HR events."""),
            row("Jackson Chourio", "R", "+300", 76, "", ["vs Lodolo"], """1 HR, 2 near-HR, 92.5 mph EV. Lodolo RHB split +0.29, HR risk -0.13. pitcher risk below avg (-0.13).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ DET - Carlos Rodon (L, NYY) vs Casey Mize (R, DET)",
        "description": "Tail key data: Park boost -16% (stadium -11%, weather -4%). Rodon (HR risk -0.59, vs LHB +0.27, vs RHB -0.66). Mize (HR risk -0.94, vs LHB -0.70, vs RHB -0.51).",
        "rows": [
            row("Riley Greene", "L", "+520", 77, "", ["vs Rodon"], """0 HR, 1 near-HR, 99.2 mph EV. Rodon LHB split +0.27, HR risk -0.59. pitcher suppresses HR (-0.59); park/weather net drag (-16%).""", blast="good"),
            row("Dillon Dingler", "R", "+520", 64, "", ["vs Rodon"], """0 HR, 89.5 mph EV. Rodon RHB split -0.66, HR risk -0.59. tough split lane (-0.66); pitcher suppresses HR (-0.59)."""),
            row("Ben Rice", "L", "+420", 97, "⭐ 🌕 💣", ["vs Mize"], """Worst Pickz Favorite. 3 HR, 6 near-HR, 95.4 mph EV. Mize LHB split -0.70, HR risk -0.94. tough split lane (-0.70); pitcher suppresses HR (-0.94).""", blast="high"),
            row("Ryan McMahon", "L", "+520", 65, "", ["vs Mize"], """0 HR, 91.2 mph EV. Mize LHB split -0.70, HR risk -0.94. tough split lane (-0.70); pitcher suppresses HR (-0.94)."""),
            row("Spencer Jones", "L", "+630", 73, "", ["vs Mize"], """0 HR, 97.0 mph EV. Mize LHB split -0.70, HR risk -0.94. tough split lane (-0.70); pitcher suppresses HR (-0.94).""", blast="good"),
            row("Paul Goldschmidt", "R", "+520", 78, "🌕 💣", ["vs Mize"], """2 HR, 2 near-HR, 85.0 mph EV. Mize RHB split -0.51, HR risk -0.94. tough split lane (-0.51); pitcher suppresses HR (-0.94).""", blast="high"),
        ],
    },
    {
        "title": "PHI @ WSH - Jesus Luzardo (L, PHI) vs Zack Littell (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Luzardo (HR risk -0.59, vs LHB -1.22, vs RHB -0.18). Littell (HR risk 0.62, vs LHB +1.00, vs RHB -0.22).",
        "rows": [
            row("James Wood", "L", "N/A", 79, "⭐", ["vs Luzardo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.0 mph EV. Luzardo LHB split -1.22, HR risk -0.59. tough split lane (-1.22); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Luis Garcia Jr.", "L", "N/A", 81, "", ["vs Luzardo"], """1 HR, 1 near-HR, 98.6 mph EV. Luzardo LHB split -1.22, HR risk -0.59. tough split lane (-1.22); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Bryce Harper", "L", "N/A", 86, "🌕 💣", ["vs Littell"], """2 HR, 2 near-HR, 95.5 mph EV. Littell LHB split +1.00, HR risk 0.62.""", blast="high"),
            row("Kyle Schwarber", "L", "N/A", 80, "", ["vs Littell"], """1 HR, 1 near-HR, 97.7 mph EV. Littell LHB split +1.00, HR risk 0.62.""", blast="good"),
        ],
    },
    {
        "title": "SEA @ PIT - George Kirby (R, SEA) vs Mitch Keller (R, PIT)",
        "description": "Tail key data: Park boost -10% (stadium -13%, weather +3%). Kirby (HR risk -0.34, vs LHB -0.37, vs RHB -0.04). Keller (HR risk -0.39, vs LHB -0.37, vs RHB -0.09).",
        "rows": [
            row("Brandon Lowe", "L", "+477", 78, "", ["vs Kirby"], """1 HR, 1 near-HR, 95.5 mph EV. Kirby LHB split -0.37, HR risk -0.34. slight split headwind (-0.37); pitcher risk below avg (-0.34).""", blast="good"),
            row("Endy Rodriguez", "S", "+880", 78, "", ["vs Kirby"], """1 HR, 1 near-HR, 96.2 mph EV. Kirby RHB split -0.04, HR risk -0.34. slight split headwind (-0.04); pitcher risk below avg (-0.34).""", blast="good"),
            row("Tyler Callihan", "L", "+930", 62, "", ["vs Kirby"], """0 HR, 79.0 mph EV. Kirby LHB split -0.37, HR risk -0.34. slight split headwind (-0.37); pitcher risk below avg (-0.34)."""),
            row("Bryan Reynolds", "S", "+680", 98, "⭐ 🌕 💣", ["vs Kirby"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 99.7 mph EV. Kirby RHB split -0.04, HR risk -0.34. slight split headwind (-0.04); pitcher risk below avg (-0.34).""", blast="high"),
            row("Spencer Horwitz", "L", "+750", 75, "", ["vs Kirby"], """1 HR, 2 near-HR, 90.6 mph EV. Kirby LHB split -0.37, HR risk -0.34. slight split headwind (-0.37); pitcher risk below avg (-0.34).""", blast="good"),
            row("Marcell Ozuna", "R", "N/A", 78, "", ["vs Kirby"], """1 HR, 1 near-HR, 95.6 mph EV. Kirby RHB split -0.04, HR risk -0.34. slight split headwind (-0.04); pitcher risk below avg (-0.34).""", blast="good"),
            row("Dominic Canzone", "L", "+610", 88, "⭐ 🌕 💣", ["vs Keller"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 92.1 mph EV. Keller LHB split -0.37, HR risk -0.39. slight split headwind (-0.37); pitcher risk below avg (-0.39).""", blast="high"),
            row("Luke Raley", "L", "+526", 72, "", ["vs Keller"], """0 HR, 1 near-HR, 93.7 mph EV. Keller LHB split -0.37, HR risk -0.39. slight split headwind (-0.37); pitcher risk below avg (-0.39).""", blast="good"),
            row("Cole Young", "L", "+660", 83, "🌕 💣", ["vs Keller"], """2 HR, 2 near-HR, 92.8 mph EV. Keller LHB split -0.37, HR risk -0.39. slight split headwind (-0.37); pitcher risk below avg (-0.39).""", blast="high"),
        ],
    },
    {
        "title": "TEX @ MIA - Cal Quantrill (R, TEX) vs Sandy Alcantara (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -13%, weather +0%). Away starter risk unavailable. Alcantara (HR risk -0.26, vs LHB -0.08, vs RHB -0.27).",
        "rows": [
            row("Heriberto Hernandez", "R", "+325", 83, "", ["vs Quantrill"], """1 HR, 3 near-HR, 97.1 mph EV. Quantrill split/risk data unavailable. limited split/risk sample; park/weather net drag (-13%).""", blast="good"),
            row("Kyle Stowers", "L", "+177", 71, "", ["vs Quantrill"], """1 HR, 1 near-HR, 89.2 mph EV. Quantrill split/risk data unavailable. limited split/risk sample; park/weather net drag (-13%).""", blast="good"),
            row("Joe Mack", "L", "+329", 74, "", ["vs Quantrill"], """1 HR, 1 near-HR, 92.5 mph EV. Quantrill split/risk data unavailable. limited split/risk sample; park/weather net drag (-13%).""", blast="good"),
            row("Brandon Nimmo", "L", "+300", 77, "", ["vs Alcantara"], """0 HR, 3 near-HR, 95.3 mph EV. Alcantara LHB split -0.08, HR risk -0.26. slight split headwind (-0.08); pitcher risk below avg (-0.26).""", blast="good"),
            row("Joc Pederson", "L", "+301", 77, "", ["vs Alcantara"], """1 HR, 1 near-HR, 95.1 mph EV. Alcantara LHB split -0.08, HR risk -0.26. slight split headwind (-0.08); pitcher risk below avg (-0.26).""", blast="good"),
            row("Wyatt Langford", "R", "+278", 84, "🌕 💣", ["vs Alcantara"], """3 HR, 3 near-HR, 87.9 mph EV. Alcantara RHB split -0.27, HR risk -0.26. slight split headwind (-0.27); pitcher risk below avg (-0.26).""", blast="high"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-23")

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

    out = ROOT / '_games-0622.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
