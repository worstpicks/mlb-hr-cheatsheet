#!/usr/bin/env python3
"""Generate games[] block for 2026-07-30 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Dalton Rushing (L)",
    "Francisco Alvarez (R)",
    "Griffin Conine (L)",
    "Heliot Ramos (R)",
    "Hunter Feduccia (L)",
    "JJ Bleday (L)",
    "Jimmy Crooks (L)",
    "Manny Machado (R)",
    "Michael Busch (L)",
    "Pete Crow-Armstrong (L)",
    "Salvador Perez (R)",
    "Shohei Ohtani (L)",
}

GEMS = {
    "Brett Baty (L)",
    "Bryce Eldridge (L)",
    "Elly De La Cruz (S)",
    "James Wood (L)",
    "Jazz Chisholm Jr. (L)",
    "Joc Pederson (L)",
    "Junior Caminero (R)",
    "Kody Clemens (L)",
    "Lawrence Butler (L)",
    "Matt Olson (L)",
    "Max Muncy (L)",
    "Michael Massey (L)",
    "Mike Yastrzemski (L)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Brady House (R)": "WSH",
    "Brett Baty (L)": "NYM",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Dalton Rushing (L)": "LAD",
    "Dominic Canzone (L)": "SEA",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Griffin Conine (L)": "MIA",
    "Heliot Ramos (R)": "SF",
    "Henry Davis (R)": "PIT",
    "Hunter Feduccia (L)": "TB",
    "JJ Bleday (L)": "CIN",
    "Jackson Merrill (L)": "SD",
    "Jake Burger (R)": "TEX",
    "James Wood (L)": "WSH",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jimmy Crooks (L)": "STL",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "Jonah Heim (S)": "ATH",
    "Junior Caminero (R)": "TB",
    "Justin Dean (R)": "CHC",
    "Kody Clemens (L)": "MIN",
    "Kyle Stowers (L)": "MIA",
    "Lane Thomas (R)": "KC",
    "Lawrence Butler (L)": "ATH",
    "Liam Hicks (L)": "MIA",
    "Luis Garcia Jr. (L)": "WSH",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Michael Busch (L)": "CHC",
    "Michael Massey (L)": "KC",
    "Miguel Vargas (R)": "CWS",
    "Mike Yastrzemski (L)": "ATL",
    "Munetaka Murakami (L)": "CWS",
    "Nick Kurtz (L)": "ATH",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randy Arozarena (R)": "SEA",
    "Rob Refsnyder (R)": "SEA",
    "Ronald Acuna Jr. (R)": "ATL",
    "Ryan Jeffers (R)": "MIN",
    "Ryan Kreidler (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Salvador Perez (R)": "KC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Ty France (R)": "SD",
    "Tyler Stephenson (R)": "CIN",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
}

BUM_MATCHUPS = {
    ("BOS @ ATH", "Barnett"),
    ("SEA @ LAD", "Sasaki"),
    ("TEX @ TB", "Winn"),
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
    if (game_key, chip) not in BUM_MATCHUPS:
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
        "title": "BOS @ ATH - Sonny Gray (R, BOS) vs Mason Barnett 🧤 (R, ATH)",
        "description": "Tail key data: Park boost +31% (stadium +33%, weather -2%). Gray (HR risk -0.46, vs LHB -0.52, vs RHB -0.23). Barnett 🧤 (HR risk 1.44, vs LHB +0.76, vs RHB +1.42).",
        "rows": [
            row("Jonah Heim", "S", "+563", 58, "", ["vs Gray"], """0 HR, 92.3 mph EV. Gray SHB→RHB split -0.23, HR risk -0.46. slight split headwind (-0.23); pitcher suppresses HR (-0.46).""", blast="good"),
            row("Nick Kurtz", "L", "+280", 60, "", ["vs Gray"], """0 HR, 1 near-HR, 99.5 mph EV. Gray LHB split -0.52, HR risk -0.46. tough split lane (-0.52); pitcher suppresses HR (-0.46).""", blast="good"),
            row("Lawrence Butler", "L", "+578", 60, "💎", ["vs Gray"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 98.3 mph EV. Gray LHB split -0.52, HR risk -0.46. tough split lane (-0.52); pitcher suppresses HR (-0.46).""", blast="good"),
            row("Wilyer Abreu", "L", "+310", 88, "🌕 💣", ["vs Barnett"], """1 HR, 1 near-HR, 88.2 mph EV. Barnett LHB split +0.76, HR risk 1.44.""", blast="good"),
            row("Willson Contreras", "R", "+290", 94, "🌕 💣", ["vs Barnett"], """1 HR, 2 near-HR, 92.2 mph EV. Barnett RHB split +1.42, HR risk 1.44.""", blast="good"),
        ],
    },
    {
        "title": "CHC @ STL - Javier Assad (R, CHC) vs Andre Pallante (R, STL)",
        "description": "Tail key data: Park boost -15% (stadium -10%, weather -5%). Assad (HR risk 0.60, vs LHB +1.43, vs RHB -0.12). Pallante (HR risk -1.35, vs LHB -0.88, vs RHB -1.30).",
        "rows": [
            row("Jimmy Crooks", "L", "+700", 81, "⭐", ["vs Assad"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.7 mph EV. Assad LHB split +1.43, HR risk 0.60. park/weather net drag (-15%).""", blast="good"),
            row("Alec Burleson", "L", "+500", 67, "", ["vs Assad"], """0 HR, 1 near-HR, 90.8 mph EV. Assad LHB split +1.43, HR risk 0.60. park/weather net drag (-15%); limited recent HR events."""),
            row("Michael Busch", "L", "+640", 58, "⭐", ["vs Pallante"], """Worst Pickz Favorite. 0 HR, 94.3 mph EV. Pallante LHB split -0.88, HR risk -1.35. tough split lane (-0.88); pitcher suppresses HR (-1.35).""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+438", 58, "⭐", ["vs Pallante"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 98.4 mph EV. Pallante LHB split -0.88, HR risk -1.35. tough split lane (-0.88); pitcher suppresses HR (-1.35).""", blast="good"),
            row("Justin Dean", "R", "N/A", 58, "🚀", ["vs Pallante"], """0 HR, 100.3 mph EV. Pallante RHB split -1.30, HR risk -1.35. tough split lane (-1.30); pitcher suppresses HR (-1.35).""", blast="good"),
        ],
    },
    {
        "title": "KC @ MIN - Noah Cameron (L, KC) vs Bailey Ober (R, MIN)",
        "description": "Tail key data: Park boost -8% (stadium -6%, weather -1%). Cameron (HR risk 0.56, vs LHB +0.16, vs RHB +0.66). Ober (HR risk 0.77, vs LHB +0.71, vs RHB +0.66).",
        "rows": [
            row("Kody Clemens", "L", "+360", 70, "💎", ["vs Cameron"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.7 mph EV. Cameron LHB split +0.16, HR risk 0.56. park/weather net drag (-8%).""", blast="good"),
            row("Ryan Jeffers", "R", "+480", 66, "", ["vs Cameron"], """1 HR, 1 near-HR, 85.8 mph EV. Cameron RHB split +0.66, HR risk 0.56. park/weather net drag (-8%); lighter EV form (85.8 mph).""", blast="good"),
            row("Ryan Kreidler", "R", "+740", 69, "", ["vs Cameron"], """0 HR, 94.9 mph EV. Cameron RHB split +0.66, HR risk 0.56. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Michael Massey", "L", "+484", 72, "💎", ["vs Ober"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.9 mph EV. Ober LHB split +0.71, HR risk 0.77. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Lane Thomas", "R", "+457", 68, "", ["vs Ober"], """0 HR, 92.2 mph EV. Ober RHB split +0.66, HR risk 0.77. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Salvador Perez", "R", "+390", 73, "⭐", ["vs Ober"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 90.1 mph EV. Ober RHB split +0.66, HR risk 0.77. park/weather net drag (-8%).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ NYM - Eury Perez (R, MIA) vs Nolan McLean (R, NYM)",
        "description": "Tail key data: Park boost -3% (stadium -2%, weather -1%). Perez (HR risk -0.73, vs LHB -1.01, vs RHB -0.24). McLean (HR risk -1.01, vs LHB -1.01, vs RHB -0.87).",
        "rows": [
            row("Francisco Alvarez", "R", "+450", 73, "⭐ 🌕 💣", ["vs Perez"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 97.2 mph EV. Perez RHB split -0.24, HR risk -0.73. slight split headwind (-0.24); pitcher suppresses HR (-0.73).""", blast="high"),
            row("Brett Baty", "L", "+830", 59, "🌕 💣 💎", ["vs Perez"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.2 mph EV. Perez LHB split -1.01, HR risk -0.73. tough split lane (-1.01); pitcher suppresses HR (-0.73).""", blast="high"),
            row("Kyle Stowers", "L", "+517", 58, "", ["vs McLean"], """0 HR, 1 near-HR, 94.9 mph EV. McLean LHB split -1.01, HR risk -1.01. tough split lane (-1.01); pitcher suppresses HR (-1.01).""", blast="good"),
            row("Joe Mack", "L", "+840", 58, "", ["vs McLean"], """1 HR, 1 near-HR, 94.9 mph EV. McLean LHB split -1.01, HR risk -1.01. tough split lane (-1.01); pitcher suppresses HR (-1.01).""", blast="good"),
            row("Griffin Conine", "L", "+550", 63, "⭐ 🌕 💣", ["vs McLean"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 91.8 mph EV. McLean LHB split -1.01, HR risk -1.01. tough split lane (-1.01); pitcher suppresses HR (-1.01).""", blast="high"),
            row("Liam Hicks", "L", "+1300", 58, "", ["vs McLean"], """1 HR, 1 near-HR, 84.4 mph EV. McLean LHB split -1.01, HR risk -1.01. tough split lane (-1.01); pitcher suppresses HR (-1.01).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ CWS - Ryan Weathers (L, NYY) vs Sean Burke (R, CWS)",
        "description": "Tail key data: Park boost -13% (stadium -5%, weather -8%). Weathers (HR risk -0.51, vs LHB -0.66, vs RHB -0.16). Burke (HR risk -0.52, vs LHB -0.57, vs RHB -0.35).",
        "rows": [
            row("Munetaka Murakami", "L", "+380", 58, "", ["vs Weathers"], """0 HR, 1 near-HR, 90.3 mph EV. Weathers LHB split -0.66, HR risk -0.51. tough split lane (-0.66); pitcher suppresses HR (-0.51)."""),
            row("Miguel Vargas", "R", "+396", 58, "", ["vs Weathers"], """0 HR, 98.1 mph EV. Weathers RHB split -0.16, HR risk -0.51. slight split headwind (-0.16); pitcher suppresses HR (-0.51).""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "+484", 62, "🌕 💣 💎", ["vs Burke"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 97.0 mph EV. Burke LHB split -0.57, HR risk -0.52. tough split lane (-0.57); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Ben Rice", "L", "+310", 70, "⭐ 🌕 💣", ["vs Burke"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 97.8 mph EV. Burke LHB split -0.57, HR risk -0.52. tough split lane (-0.57); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Ryan McMahon", "L", "+540", 58, "", ["vs Burke"], """1 HR, 1 near-HR, 95.8 mph EV. Burke LHB split -0.57, HR risk -0.52. tough split lane (-0.57); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Spencer Jones", "L", "+509", 58, "", ["vs Burke"], """0 HR, 1 near-HR, 94.3 mph EV. Burke LHB split -0.57, HR risk -0.52. tough split lane (-0.57); pitcher suppresses HR (-0.52).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ CIN - Yohan Ramirez (R, PIT) vs Rhett Lowder (R, CIN)",
        "description": "Tail key data: Park boost +20% (stadium +14%, weather +6%). Ramirez (HR risk -1.03, vs LHB -0.67, vs RHB -0.81). Lowder (HR risk -0.41, vs LHB +0.26, vs RHB -1.32).",
        "rows": [
            row("JJ Bleday", "L", "+355", 58, "⭐", ["vs Ramirez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.7 mph EV. Ramirez LHB split -0.67, HR risk -1.03. tough split lane (-0.67); pitcher suppresses HR (-1.03).""", blast="good"),
            row("Elly De La Cruz", "S", "+379", 58, "💎", ["vs Ramirez"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.5 mph EV. Ramirez SHB→LHB split -0.67, HR risk -1.03. tough split lane (-0.67); pitcher suppresses HR (-1.03).""", blast="good"),
            row("Tyler Stephenson", "R", "+461", 58, "", ["vs Ramirez"], """0 HR, 93.5 mph EV. Ramirez RHB split -0.81, HR risk -1.03. tough split lane (-0.81); pitcher suppresses HR (-1.03).""", blast="good"),
            row("Eugenio Suarez", "R", "+370", 58, "", ["vs Ramirez"], """1 HR, 1 near-HR, 91.4 mph EV. Ramirez RHB split -0.81, HR risk -1.03. tough split lane (-0.81); pitcher suppresses HR (-1.03).""", blast="good"),
            row("Bryan Reynolds", "S", "+390", 66, "", ["vs Lowder"], """1 HR, 2 near-HR, 93.0 mph EV. Lowder SHB→LHB split +0.26, HR risk -0.41. pitcher suppresses HR (-0.41).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+390", 61, "", ["vs Lowder"], """1 HR, 1 near-HR, 96.9 mph EV. Lowder RHB split -1.32, HR risk -0.41. tough split lane (-1.32); pitcher suppresses HR (-0.41).""", blast="good"),
            row("Henry Davis", "R", "N/A", 58, "", ["vs Lowder"], """0 HR, 1 near-HR, 85.9 mph EV. Lowder RHB split -1.32, HR risk -0.41. tough split lane (-1.32); pitcher suppresses HR (-0.41)."""),
        ],
    },
    {
        "title": "SEA @ LAD - Bryan Woo (R, SEA) vs Roki Sasaki 🧤 (R, LAD)",
        "description": "Tail key data: Park boost +18% (stadium +16%, weather +2%). Woo (HR risk -0.50, vs LHB -0.47, vs RHB -0.34). Sasaki 🧤 (HR risk 1.28, vs LHB +0.53, vs RHB +1.82).",
        "rows": [
            row("Shohei Ohtani", "L", "+214", 61, "🚀 ⭐", ["vs Woo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 100.3 mph EV. Woo LHB split -0.47, HR risk -0.50. tough split lane (-0.47); pitcher suppresses HR (-0.50).""", blast="good"),
            row("Max Muncy", "L", "+283", 78, "🌕 💣 💎", ["vs Woo"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 95.9 mph EV. Woo LHB split -0.47, HR risk -0.50. tough split lane (-0.47); pitcher suppresses HR (-0.50).""", blast="high"),
            row("Dalton Rushing", "L", "+400", 58, "⭐", ["vs Woo"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 86.2 mph EV. Woo LHB split -0.47, HR risk -0.50. tough split lane (-0.47); pitcher suppresses HR (-0.50).""", blast="good"),
            row("Randy Arozarena", "R", "+489", 92, "🌕 💣", ["vs Sasaki"], """0 HR, 96.4 mph EV. Sasaki RHB split +1.82, HR risk 1.28. limited recent HR events.""", blast="good"),
            row("Dominic Canzone", "L", "+384", 85, "", ["vs Sasaki"], """1 HR, 1 near-HR, 91.3 mph EV. Sasaki LHB split +0.53, HR risk 1.28.""", blast="good"),
            row("Rob Refsnyder", "R", "N/A", 90, "🌕 💣", ["vs Sasaki"], """0 HR, 92.0 mph EV. Sasaki RHB split +1.82, HR risk 1.28. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "SF @ SD - Robbie Ray (L, SF) vs JP Sears (L, SD)",
        "description": "Tail key data: Park boost -1% (stadium -4%, weather +3%). Ray (HR risk -0.46, vs LHB -0.52, vs RHB -0.23). Sears (HR risk 0.57, vs LHB +0.97, vs RHB +0.37).",
        "rows": [
            row("Fernando Tatis Jr.", "R", "+409", 65, "🌕 💣", ["vs Ray"], """2 HR, 2 near-HR, 93.5 mph EV. Ray RHB split -0.23, HR risk -0.46. slight split headwind (-0.23); pitcher suppresses HR (-0.46).""", blast="high"),
            row("Manny Machado", "R", "+280", 63, "⭐", ["vs Ray"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 94.6 mph EV. Ray RHB split -0.23, HR risk -0.46. slight split headwind (-0.23); pitcher suppresses HR (-0.46).""", blast="good"),
            row("Ty France", "R", "+630", 58, "", ["vs Ray"], """0 HR, 95.8 mph EV. Ray RHB split -0.23, HR risk -0.46. slight split headwind (-0.23); pitcher suppresses HR (-0.46).""", blast="good"),
            row("Jackson Merrill", "L", "+750", 58, "", ["vs Ray"], """0 HR, 97.3 mph EV. Ray LHB split -0.52, HR risk -0.46. tough split lane (-0.52); pitcher suppresses HR (-0.46).""", blast="good"),
            row("Bryce Eldridge", "L", "+430", 73, "💎", ["vs Sears"], """Worst Pickz Hidden Gem. 0 HR, 93.9 mph EV. Sears LHB split +0.97, HR risk 0.57. limited recent HR events.""", blast="good"),
            row("Heliot Ramos", "R", "+437", 73, "⭐", ["vs Sears"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.4 mph EV. Sears RHB split +0.37, HR risk 0.57.""", blast="good"),
            row("Rafael Devers", "L", "+420", 75, "", ["vs Sears"], """1 HR, 2 near-HR, 89.3 mph EV. Sears LHB split +0.97, HR risk 0.57.""", blast="good"),
        ],
    },
    {
        "title": "TEX @ TB - Cole Winn 🧤 (R, TEX) vs Shane McClanahan (L, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Winn 🧤 (HR risk 1.24, vs LHB +0.33, vs RHB +1.04). McClanahan (HR risk -0.14, vs LHB +0.62, vs RHB -0.39).",
        "rows": [
            row("Hunter Feduccia", "L", "+1080", 80, "⭐", ["vs Winn"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.4 mph EV. Winn LHB split +0.33, HR risk 1.24.""", blast="good"),
            row("Junior Caminero", "R", "+313", 74, "💎", ["vs Winn"], """Worst Pickz Hidden Gem. 0 HR, 90.8 mph EV. Winn RHB split +1.04, HR risk 1.24. limited recent HR events."""),
            row("Wyatt Langford", "R", "+408", 65, "🌕 💣", ["vs McClanahan"], """2 HR, 3 near-HR, 88.1 mph EV. McClanahan RHB split -0.39, HR risk -0.14. slight split headwind (-0.39); pitcher risk below avg (-0.14).""", blast="high"),
            row("Jake Burger", "R", "+372", 65, "", ["vs McClanahan"], """1 HR, 3 near-HR, 96.1 mph EV. McClanahan RHB split -0.39, HR risk -0.14. slight split headwind (-0.39); pitcher risk below avg (-0.14).""", blast="good"),
            row("Joc Pederson", "L", "N/A", 58, "💎", ["vs McClanahan"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 87.5 mph EV. McClanahan LHB split +0.62, HR risk -0.14. pitcher risk below avg (-0.14); limited recent HR events."""),
        ],
    },
    {
        "title": "WSH @ ATL - Jake Irvin (R, WSH) vs Grant Holmes (R, ATL)",
        "description": "Tail key data: Park boost +8% (stadium -1%, weather +10%). Irvin (HR risk 0.54, vs LHB +0.40, vs RHB +0.47). Holmes (HR risk -0.34, vs LHB -0.37, vs RHB -0.31).",
        "rows": [
            row("Matt Olson", "L", "+240", 77, "💎", ["vs Irvin"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.0 mph EV. Irvin LHB split +0.40, HR risk 0.54.""", blast="good"),
            row("Mike Yastrzemski", "L", "+600", 74, "💎", ["vs Irvin"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.5 mph EV. Irvin LHB split +0.40, HR risk 0.54.""", blast="good"),
            row("Austin Riley", "R", "+425", 83, "🌕 💣", ["vs Irvin"], """2 HR, 2 near-HR, 91.4 mph EV. Irvin RHB split +0.47, HR risk 0.54.""", blast="high"),
            row("Ronald Acuna Jr.", "R", "+360", 63, "", ["vs Irvin"], """0 HR, 90.5 mph EV. Irvin RHB split +0.47, HR risk 0.54. limited recent HR events."""),
            row("Luis Garcia Jr.", "L", "+405", 58, "", ["vs Holmes"], """0 HR, 1 near-HR, 92.0 mph EV. Holmes LHB split -0.37, HR risk -0.34. slight split headwind (-0.37); pitcher risk below avg (-0.34).""", blast="good"),
            row("James Wood", "L", "+270", 60, "💎", ["vs Holmes"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.5 mph EV. Holmes LHB split -0.37, HR risk -0.34. slight split headwind (-0.37); pitcher risk below avg (-0.34).""", blast="good"),
            row("Brady House", "R", "N/A", 58, "", ["vs Holmes"], """0 HR, 1 near-HR, 95.9 mph EV. Holmes RHB split -0.31, HR risk -0.34. slight split headwind (-0.31); pitcher risk below avg (-0.34).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-30")

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

    out = ROOT / '_games-0730.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
