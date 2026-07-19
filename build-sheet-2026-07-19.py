#!/usr/bin/env python3
"""Generate games[] block for 2026-07-19 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Ben Rice (L)",
    "Brice Turang (L)",
    "Bryce Eldridge (L)",
    "Carter Jensen (L)",
    "Dalton Rushing (L)",
    "Drake Baldwin (L)",
    "Esmerlyn Valdez (R)",
    "Eugenio Suarez (R)",
    "George Springer (R)",
    "Heriberto Hernandez (R)",
    "Joc Pederson (L)",
    "Jonathan Aranda (L)",
    "Josh Lowe (L)",
    "Kyle Schwarber (L)",
    "Manny Machado (R)",
    "Max Muncy (L)",
    "Mickey Moniak (L)",
    "Ryan Jeffers (R)",
    "Ryan McMahon (L)",
    "Trent Grisham (L)",
    "Wilyer Abreu (L)",
}

GEMS = {
    "Brett Baty (L)",
    "Cole Young (L)",
    "Dominic Canzone (L)",
    "Jorge Soler (R)",
    "Kody Clemens (L)",
    "Lane Thomas (R)",
    "Max Muncy (L)",
    "Pete Crow-Armstrong (L)",
    "Shea Langeliers (R)",
    "Taylor Trammell (L)",
    "Trent Grisham (L)",
    "Vladimir Guerrero Jr. (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Andres Chaparro (R)": "WSH",
    "Andruw Monasterio (R)": "BOS",
    "Andy Pages (R)": "LAD",
    "Austin Hedges (R)": "CLE",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Braden Shewmake (L)": "MIL",
    "Brandon Lowe (L)": "PIT",
    "Brandon Valenzuela (S)": "TOR",
    "Brayan Rocchio (S)": "CLE",
    "Brett Baty (L)": "NYM",
    "Brice Turang (L)": "MIL",
    "Bryce Eldridge (L)": "SF",
    "Bryson Stott (L)": "PHI",
    "CJ Abrams (L)": "WSH",
    "Carter Jensen (L)": "KC",
    "Chase DeLauter (L)": "CLE",
    "Christian Yelich (L)": "MIL",
    "Colby Thomas (R)": "ATH",
    "Cole Young (L)": "SEA",
    "Colt Keith (L)": "DET",
    "Dalton Rushing (L)": "LAD",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Esmerlyn Valdez (R)": "PIT",
    "Esteury Ruiz (R)": "MIA",
    "Eugenio Suarez (R)": "CIN",
    "Gabriel Rincones Jr. (L)": "PHI",
    "George Springer (R)": "TOR",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "TB",
    "Jake McCarthy (L)": "COL",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jimmy Crooks (L)": "STL",
    "Joc Pederson (L)": "TEX",
    "Jonathan Aranda (L)": "TB",
    "Jorge Soler (R)": "LAA",
    "Josh Lowe (L)": "LAA",
    "Kerry Carpenter (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Tucker (L)": "LAD",
    "Lane Thomas (R)": "KC",
    "Logan O'Hoppe (R)": "LAA",
    "Luis Rengifo (S)": "SD",
    "Luke Keaschall (R)": "MIN",
    "Manny Machado (R)": "SD",
    "Marcell Ozuna (R)": "PIT",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Max Muncy (L)": "LAD",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Munetaka Murakami (L)": "CWS",
    "Nathan Church (L)": "STL",
    "Nelson Velazquez (R)": "STL",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Flores (R)": "PIT",
    "Randal Grichuk (R)": "CWS",
    "Riley Greene (L)": "DET",
    "Romy Gonzalez (R)": "BOS",
    "Ryan Jeffers (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Steer (R)": "CIN",
    "Taylor Trammell (L)": "HOU",
    "Teoscar Hernandez (R)": "LAD",
    "Trent Grisham (L)": "NYY",
    "Ty France (R)": "SD",
    "Tyler O'Neill (R)": "BAL",
    "Tyrone Taylor (R)": "NYM",
    "Victor Caratini (S)": "MIN",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("DET @ LAA", "Johnson"),
    ("MIN @ CHC", "Matthews"),
    ("SD @ KC", "Marquez"),
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
        "title": "BAL @ HOU - Brandon Young (R, BAL) vs Hunter Brown (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +0%). Young (HR risk -0.25, vs LHB +0.20, vs RHB -0.88). Brown (HR risk 0.38, vs LHB +0.57, vs RHB -0.09).",
        "rows": [
            row("Taylor Trammell", "L", "N/A", 79, "🌕 💣 💎", ["vs Young"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 95.7 mph EV. Young LHB split +0.20, HR risk -0.25. pitcher risk below avg (-0.25).""", blast="high"),
            row("Yordan Alvarez", "L", "+229", 72, "🌕 💣", ["vs Young"], """2 HR, 2 near-HR, 93.9 mph EV. Young LHB split +0.20, HR risk -0.25. pitcher risk below avg (-0.25).""", blast="high"),
            row("Tyler O'Neill", "R", "N/A", 58, "", ["vs Brown"], """0 HR, 1 near-HR, 91.6 mph EV. Brown RHB split -0.09, HR risk 0.38. slight split headwind (-0.09); limited recent HR events."""),
            row("Pete Alonso", "R", "+322", 58, "", ["vs Brown"], """1 HR, 1 near-HR, 84.9 mph EV. Brown RHB split -0.09, HR risk 0.38. slight split headwind (-0.09); lighter EV form (84.9 mph).""", blast="good"),
        ],
    },
    {
        "title": "CIN @ COL - Hunter Greene (R, CIN) vs Ryan Feltner (R, COL)",
        "description": "Tail key data: Park boost +23% (stadium +20%, weather +3%). Greene (HR risk 0.17, vs LHB +1.68, vs RHB -1.46). Feltner (HR risk 0.48, vs LHB +1.16, vs RHB -0.42).",
        "rows": [
            row("Willi Castro", "S", "N/A", 84, "", ["vs Greene"], """1 HR, 1 near-HR, 94.8 mph EV. Greene SHB→LHB split +1.68, HR risk 0.17.""", blast="good"),
            row("Mickey Moniak", "L", "N/A", 83, "⭐", ["vs Greene"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.3 mph EV. Greene LHB split +1.68, HR risk 0.17.""", blast="good"),
            row("Jake McCarthy", "L", "N/A", 75, "", ["vs Greene"], """1 HR, 1 near-HR, 83.4 mph EV. Greene LHB split +1.68, HR risk 0.17. lighter EV form (83.4 mph).""", blast="good"),
            row("Kyle Karros", "R", "N/A", 62, "", ["vs Greene"], """1 HR, 1 near-HR, 91.5 mph EV. Greene RHB split -1.46, HR risk 0.17. tough split lane (-1.46).""", blast="good"),
            row("Eugenio Suarez", "R", "N/A", 91, "⭐ 🌕 💣", ["vs Feltner"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 97.8 mph EV. Feltner RHB split -0.42, HR risk 0.48. tough split lane (-0.42).""", blast="high"),
            row("Spencer Steer", "R", "N/A", 76, "🌕 💣", ["vs Feltner"], """2 HR, 2 near-HR, 88.0 mph EV. Feltner RHB split -0.42, HR risk 0.48. tough split lane (-0.42).""", blast="high"),
        ],
    },
    {
        "title": "CWS @ TOR - Sean Burke (R, CWS) vs Trey Yesavage (R, TOR)",
        "description": "Tail key data: Park boost +5% (stadium +7%, weather -2%). Burke (HR risk 0.19, vs LHB +0.12, vs RHB +0.10). Yesavage (HR risk -0.37, vs LHB -0.71, vs RHB +0.29).",
        "rows": [
            row("Vladimir Guerrero Jr.", "R", "+508", 76, "🌕 💣 💎", ["vs Burke"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 89.7 mph EV. Burke RHB split +0.10, HR risk 0.19.""", blast="high"),
            row("George Springer", "R", "+442", 76, "⭐ 🌕 💣", ["vs Burke"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.1 mph EV. Burke RHB split +0.10, HR risk 0.19.""", blast="high"),
            row("Brandon Valenzuela", "S", "N/A", 62, "", ["vs Burke"], """1 HR, 1 near-HR, 89.8 mph EV. Burke SHB→LHB split +0.12, HR risk 0.19.""", blast="good"),
            row("Randal Grichuk", "R", "N/A", 58, "", ["vs Yesavage"], """0 HR, 1 near-HR, 90.6 mph EV. Yesavage RHB split +0.29, HR risk -0.37. pitcher risk below avg (-0.37); limited recent HR events."""),
            row("Miguel Vargas", "R", "+371", 59, "", ["vs Yesavage"], """0 HR, 1 near-HR, 94.5 mph EV. Yesavage RHB split +0.29, HR risk -0.37. pitcher risk below avg (-0.37); limited recent HR events.""", blast="good"),
            row("Munetaka Murakami", "L", "+282", 67, "🌕 💣", ["vs Yesavage"], """2 HR, 2 near-HR, 97.8 mph EV. Yesavage LHB split -0.71, HR risk -0.37. tough split lane (-0.71); pitcher risk below avg (-0.37).""", blast="high"),
        ],
    },
    {
        "title": "DET @ LAA - Casey Mize (R, DET) vs Ryan Johnson 🧤 (R, LAA)",
        "description": "Tail key data: Park boost +17% (stadium +9%, weather +8%). Mize (HR risk -0.73, vs LHB -0.85, vs RHB +0.00). Johnson 🧤 (HR risk 1.53, vs LHB +0.68, vs RHB +1.88).",
        "rows": [
            row("Jorge Soler", "R", "+370", 59, "💎", ["vs Mize"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 95.1 mph EV. Mize RHB split +0.00, HR risk -0.73. pitcher suppresses HR (-0.73).""", blast="good"),
            row("Josh Lowe", "L", "+520", 58, "⭐", ["vs Mize"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 90.0 mph EV. Mize LHB split -0.85, HR risk -0.73. tough split lane (-0.85); pitcher suppresses HR (-0.73).""", blast="good"),
            row("Logan O'Hoppe", "R", "+480", 58, "", ["vs Mize"], """0 HR, 89.6 mph EV. Mize RHB split +0.00, HR risk -0.73. pitcher suppresses HR (-0.73); limited recent HR events."""),
            row("Riley Greene", "L", "+290", 96, "🌕 💣", ["vs Johnson"], """2 HR, 3 near-HR, 93.6 mph EV. Johnson LHB split +0.68, HR risk 1.53.""", blast="high"),
            row("Colt Keith", "L", "+540", 98, "🌕 💣", ["vs Johnson"], """3 HR, 3 near-HR, 97.2 mph EV. Johnson LHB split +0.68, HR risk 1.53.""", blast="high"),
            row("Kerry Carpenter", "L", "+340", 89, "🌕 💣", ["vs Johnson"], """1 HR, 1 near-HR, 92.6 mph EV. Johnson LHB split +0.68, HR risk 1.53.""", blast="good"),
        ],
    },
    {
        "title": "LAD @ NYY (G1) - Yoshinobu Yamamoto (R, LAD) vs Cam Schlittler (R, NYY)",
        "description": "Tail key data: Park boost +5% (stadium +3%, weather +1%). Yamamoto (HR risk -0.77, vs LHB -0.57, vs RHB -0.59). Schlittler (HR risk 0.72, vs LHB +0.31, vs RHB +0.76).",
        "rows": [
            row("Ben Rice", "L", "N/A", 64, "⭐ 🌕 💣", ["vs Yamamoto"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.7 mph EV. Yamamoto LHB split -0.57, HR risk -0.77. tough split lane (-0.57); pitcher suppresses HR (-0.77).""", blast="high"),
            row("Ryan McMahon", "L", "N/A", 58, "⭐", ["vs Yamamoto"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.6 mph EV. Yamamoto LHB split -0.57, HR risk -0.77. tough split lane (-0.57); pitcher suppresses HR (-0.77).""", blast="good"),
            row("Trent Grisham", "L", "N/A", 58, "⭐", ["vs Yamamoto"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.7 mph EV. Yamamoto LHB split -0.57, HR risk -0.77. tough split lane (-0.57); pitcher suppresses HR (-0.77).""", blast="good"),
            row("Max Muncy", "L", "N/A", 65, "⭐", ["vs Schlittler"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 91.7 mph EV. Schlittler LHB split +0.31, HR risk 0.72. limited recent HR events."""),
            row("Teoscar Hernandez", "R", "N/A", 77, "", ["vs Schlittler"], """0 HR, 1 near-HR, 97.5 mph EV. Schlittler RHB split +0.76, HR risk 0.72. limited recent HR events.""", blast="good"),
            row("Shohei Ohtani", "L", "N/A", 74, "", ["vs Schlittler"], """1 HR, 1 near-HR, 91.8 mph EV. Schlittler LHB split +0.31, HR risk 0.72.""", blast="good"),
        ],
    },
    {
        "title": "LAD @ NYY (G2) - Emmet Sheehan (R, LAD) vs Ryan Weathers (L, NYY)",
        "description": "Tail key data: Park boost +5% (stadium +3%, weather +1%). Sheehan (HR risk 0.39, vs LHB +0.33, vs RHB +0.35). Weathers (HR risk -0.27, vs LHB +0.29, vs RHB -0.31).",
        "rows": [
            row("Ryan McMahon", "L", "N/A", 70, "⭐", ["vs Sheehan"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.9 mph EV. Sheehan LHB split +0.33, HR risk 0.39.""", blast="good"),
            row("Ben Rice", "L", "N/A", 80, "⭐ 🌕 💣", ["vs Sheehan"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.6 mph EV. Sheehan LHB split +0.33, HR risk 0.39.""", blast="high"),
            row("Jazz Chisholm Jr.", "L", "N/A", 58, "", ["vs Sheehan"], """0 HR, 88.7 mph EV. Sheehan LHB split +0.33, HR risk 0.39. limited recent HR events."""),
            row("Trent Grisham", "L", "N/A", 73, "💎", ["vs Sheehan"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 97.5 mph EV. Sheehan LHB split +0.33, HR risk 0.39.""", blast="good"),
            row("Dalton Rushing", "L", "N/A", 58, "⭐", ["vs Weathers"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 91.5 mph EV. Weathers LHB split +0.29, HR risk -0.27. pitcher risk below avg (-0.27); limited recent HR events."""),
            row("Max Muncy", "L", "N/A", 69, "🌕 💣 💎", ["vs Weathers"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 90.2 mph EV. Weathers LHB split +0.29, HR risk -0.27. pitcher risk below avg (-0.27).""", blast="high"),
            row("Andy Pages", "R", "N/A", 58, "", ["vs Weathers"], """1 HR, 2 near-HR, 86.6 mph EV. Weathers RHB split -0.31, HR risk -0.27. slight split headwind (-0.31); pitcher risk below avg (-0.27).""", blast="good"),
            row("Kyle Tucker", "L", "N/A", 58, "", ["vs Weathers"], """0 HR, 1 near-HR, 90.3 mph EV. Weathers LHB split +0.29, HR risk -0.27. pitcher risk below avg (-0.27); limited recent HR events."""),
        ],
    },
    {
        "title": "MIA @ MIL - Eury Perez (R, MIA) vs Robert Gasser (L, MIL)",
        "description": "Tail key data: Park boost +29% (stadium +10%, weather +19%). Perez (HR risk -0.13, vs LHB -0.51, vs RHB +0.68). Gasser (HR risk 0.77, vs LHB -0.26, vs RHB +0.84).",
        "rows": [
            row("Brice Turang", "L", "N/A", 80, "⭐ 🌕 💣", ["vs Perez"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 97.8 mph EV. Perez LHB split -0.51, HR risk -0.13. tough split lane (-0.51); pitcher risk below avg (-0.13).""", blast="high"),
            row("Christian Yelich", "L", "+600", 66, "", ["vs Perez"], """1 HR, 1 near-HR, 95.8 mph EV. Perez LHB split -0.51, HR risk -0.13. tough split lane (-0.51); pitcher risk below avg (-0.13).""", blast="good"),
            row("Braden Shewmake", "L", "N/A", 69, "", ["vs Perez"], """0 HR, 4 near-HR, 94.6 mph EV. Perez LHB split -0.51, HR risk -0.13. tough split lane (-0.51); pitcher risk below avg (-0.13).""", blast="good"),
            row("Heriberto Hernandez", "R", "+280", 93, "⭐ 🌕 💣", ["vs Gasser"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.9 mph EV. Gasser RHB split +0.84, HR risk 0.77.""", blast="high"),
            row("Esteury Ruiz", "R", "N/A", 92, "🌕 💣", ["vs Gasser"], """2 HR, 4 near-HR, 80.4 mph EV. Gasser RHB split +0.84, HR risk 0.77. lighter EV form (80.4 mph).""", blast="high"),
        ],
    },
    {
        "title": "MIN @ CHC - Zebby Matthews 🧤 (R, MIN) vs Shota Imanaga (L, CHC)",
        "description": "Tail key data: Park boost +26% (stadium -2%, weather +28%). Matthews 🧤 (HR risk 1.22, vs LHB +1.14, vs RHB +0.65). Imanaga (HR risk 0.81, vs LHB +1.00, vs RHB +0.49).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+407", 86, "💎", ["vs Matthews"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 85.5 mph EV. Matthews LHB split +1.14, HR risk 1.22. lighter EV form (85.5 mph).""", blast="good"),
            row("Kody Clemens", "L", "+750", 92, "🌕 💣 💎", ["vs Imanaga"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 91.0 mph EV. Imanaga LHB split +1.00, HR risk 0.81.""", blast="high"),
            row("Ryan Jeffers", "R", "+464", 81, "⭐", ["vs Imanaga"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 97.7 mph EV. Imanaga RHB split +0.49, HR risk 0.81. limited recent HR events.""", blast="good"),
            row("Victor Caratini", "S", "+310", 83, "", ["vs Imanaga"], """1 HR, 1 near-HR, 89.5 mph EV. Imanaga SHB→LHB split +1.00, HR risk 0.81.""", blast="good"),
            row("Luke Keaschall", "R", "+970", 78, "", ["vs Imanaga"], """1 HR, 1 near-HR, 88.7 mph EV. Imanaga RHB split +0.49, HR risk 0.81.""", blast="good"),
        ],
    },
    {
        "title": "NYM @ PHI - Nolan McLean (R, NYM) vs Alan Rangel (R, PHI)",
        "description": "Tail key data: Park boost +30% (stadium +14%, weather +16%). McLean (HR risk -0.94, vs LHB -0.87, vs RHB -0.58). Rangel (HR risk 0.03, vs LHB -0.40, vs RHB +0.47).",
        "rows": [
            row("Kyle Schwarber", "L", "+232", 58, "⭐", ["vs McLean"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 96.3 mph EV. McLean LHB split -0.87, HR risk -0.94. tough split lane (-0.87); pitcher suppresses HR (-0.94).""", blast="good"),
            row("Gabriel Rincones Jr.", "L", "+670", 59, "", ["vs McLean"], """1 HR, 1 near-HR, 96.5 mph EV. McLean LHB split -0.87, HR risk -0.94. tough split lane (-0.87); pitcher suppresses HR (-0.94).""", blast="good"),
            row("Bryson Stott", "L", "+630", 58, "", ["vs McLean"], """0 HR, 1 near-HR, 92.7 mph EV. McLean LHB split -0.87, HR risk -0.94. tough split lane (-0.87); pitcher suppresses HR (-0.94).""", blast="good"),
            row("Brett Baty", "L", "+342", 79, "🌕 💣 💎", ["vs Rangel"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 99.6 mph EV. Rangel LHB split -0.40, HR risk 0.03. tough split lane (-0.40).""", blast="high"),
            row("Jared Young", "L", "+509", 63, "", ["vs Rangel"], """0 HR, 1 near-HR, 93.6 mph EV. Rangel LHB split -0.40, HR risk 0.03. tough split lane (-0.40); limited recent HR events.""", blast="good"),
            row("Tyrone Taylor", "R", "N/A", 66, "", ["vs Rangel"], """1 HR, 1 near-HR, 82.7 mph EV. Rangel RHB split +0.47, HR risk 0.03. lighter EV form (82.7 mph).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ CLE - Paul Skenes (R, PIT) vs Joey Cantillo (L, CLE)",
        "description": "Tail key data: Park boost -2% (stadium -4%, weather +1%). Skenes (HR risk -0.54, vs LHB -0.42, vs RHB -0.38). Cantillo (HR risk -0.98, vs LHB -0.00, vs RHB -0.92).",
        "rows": [
            row("Chase DeLauter", "L", "+600", 65, "🌕 💣", ["vs Skenes"], """2 HR, 2 near-HR, 97.3 mph EV. Skenes LHB split -0.42, HR risk -0.54. tough split lane (-0.42); pitcher suppresses HR (-0.54).""", blast="high"),
            row("Austin Hedges", "R", "N/A", 58, "🌕 💣", ["vs Skenes"], """2 HR, 2 near-HR, 86.6 mph EV. Skenes RHB split -0.38, HR risk -0.54. slight split headwind (-0.38); pitcher suppresses HR (-0.54).""", blast="high"),
            row("Brayan Rocchio", "S", "+1000", 58, "", ["vs Skenes"], """1 HR, 1 near-HR, 85.6 mph EV. Skenes SHB→RHB split -0.38, HR risk -0.54. slight split headwind (-0.38); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Brandon Lowe", "L", "+350", 58, "", ["vs Cantillo"], """1 HR, 1 near-HR, 92.0 mph EV. Cantillo LHB split -0.00, HR risk -0.98. pitcher suppresses HR (-0.98).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+350", 60, "🚀 ⭐ 🌕 💣", ["vs Cantillo"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.2 mph EV. Cantillo RHB split -0.92, HR risk -0.98. tough split lane (-0.92); pitcher suppresses HR (-0.98).""", blast="high"),
            row("Marcell Ozuna", "R", "+560", 58, "", ["vs Cantillo"], """1 HR, 1 near-HR, 89.3 mph EV. Cantillo RHB split -0.92, HR risk -0.98. tough split lane (-0.92); pitcher suppresses HR (-0.98).""", blast="good"),
            row("Rafael Flores", "R", "N/A", 58, "", ["vs Cantillo"], """0 HR, 83.9 mph EV. Cantillo RHB split -0.92, HR risk -0.98. tough split lane (-0.92); pitcher suppresses HR (-0.98)."""),
        ],
    },
    {
        "title": "SD @ KC - German Marquez 🧤 (R, SD) vs Noah Cameron (L, KC)",
        "description": "Tail key data: Park boost +27% (stadium +12%, weather +16%). Marquez 🧤 (HR risk 1.49, vs LHB +1.53, vs RHB +0.29). Cameron (HR risk 0.63, vs LHB -0.31, vs RHB +0.92).",
        "rows": [
            row("Carter Jensen", "L", "+371", 98, "⭐ 🌕 💣", ["vs Marquez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.8 mph EV. Marquez LHB split +1.53, HR risk 1.49.""", blast="high"),
            row("Lane Thomas", "R", "+523", 94, "🌕 💣 💎", ["vs Marquez"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 99.9 mph EV. Marquez RHB split +0.29, HR risk 1.49.""", blast="high"),
            row("Bobby Witt Jr.", "R", "+372", 84, "", ["vs Marquez"], """0 HR, 1 near-HR, 92.2 mph EV. Marquez RHB split +0.29, HR risk 1.49. limited recent HR events.""", blast="good"),
            row("Ty France", "R", "+670", 87, "", ["vs Cameron"], """1 HR, 1 near-HR, 95.8 mph EV. Cameron RHB split +0.92, HR risk 0.63.""", blast="good"),
            row("Luis Rengifo", "S", "+840", 73, "", ["vs Cameron"], """0 HR, 91.1 mph EV. Cameron SHB→RHB split +0.92, HR risk 0.63. limited recent HR events."""),
            row("Manny Machado", "R", "+332", 90, "⭐ 🌕 💣", ["vs Cameron"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 93.9 mph EV. Cameron RHB split +0.92, HR risk 0.63.""", blast="good"),
        ],
    },
    {
        "title": "SF @ SEA - Robbie Ray (L, SF) vs Logan Gilbert (R, SEA)",
        "description": "Tail key data: Park boost -2% (stadium +1%, weather -3%). Ray (HR risk -0.44, vs LHB -1.06, vs RHB -0.02). Gilbert (HR risk -0.26, vs LHB -0.72, vs RHB +0.62).",
        "rows": [
            row("Dominic Canzone", "L", "N/A", 65, "🌕 💣 💎", ["vs Ray"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 99.4 mph EV. Ray LHB split -1.06, HR risk -0.44. tough split lane (-1.06); pitcher suppresses HR (-0.44).""", blast="high"),
            row("Cole Young", "L", "+950", 58, "💎", ["vs Ray"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.5 mph EV. Ray LHB split -1.06, HR risk -0.44. tough split lane (-1.06); pitcher suppresses HR (-0.44).""", blast="good"),
            row("Bryce Eldridge", "L", "+558", 65, "⭐ 🌕 💣", ["vs Gilbert"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.9 mph EV. Gilbert LHB split -0.72, HR risk -0.26. tough split lane (-0.72); pitcher risk below avg (-0.26).""", blast="high"),
        ],
    },
    {
        "title": "STL @ ARI - Andre Pallante (R, STL) vs Eduardo Rodriguez (L, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -7%, weather -1%). Pallante (HR risk -1.29, vs LHB -0.68, vs RHB -1.28). Rodriguez (HR risk 0.12, vs LHB +0.44, vs RHB -0.16).",
        "rows": [
            row("Max Kepler", "L", "+368", 58, "", ["vs Pallante"], """1 HR, 2 near-HR, 94.4 mph EV. Pallante LHB split -0.68, HR risk -1.29. tough split lane (-0.68); pitcher suppresses HR (-1.29).""", blast="good"),
            row("Nathan Church", "L", "+623", 71, "🌕 💣", ["vs Rodriguez"], """2 HR, 2 near-HR, 90.5 mph EV. Rodriguez LHB split +0.44, HR risk 0.12. park/weather net drag (-8%).""", blast="high"),
            row("Nelson Velazquez", "R", "+279", 71, "🌕 💣", ["vs Rodriguez"], """2 HR, 2 near-HR, 95.0 mph EV. Rodriguez RHB split -0.16, HR risk 0.12. slight split headwind (-0.16); park/weather net drag (-8%).""", blast="high"),
            row("Alec Burleson", "L", "+297", 69, "⭐", ["vs Rodriguez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.1 mph EV. Rodriguez LHB split +0.44, HR risk 0.12. park/weather net drag (-8%).""", blast="good"),
            row("Jimmy Crooks", "L", "N/A", 58, "", ["vs Rodriguez"], """0 HR, 1 near-HR, 91.2 mph EV. Rodriguez LHB split +0.44, HR risk 0.12. park/weather net drag (-8%); limited recent HR events."""),
        ],
    },
    {
        "title": "TB @ BOS - Shane McClanahan (L, TB) vs Sonny Gray (R, BOS)",
        "description": "Tail key data: Park boost +3% (stadium -6%, weather +9%). McClanahan (HR risk -0.31, vs LHB +0.59, vs RHB -0.65). Gray (HR risk -0.33, vs LHB -0.16, vs RHB -0.57).",
        "rows": [
            row("Wilyer Abreu", "L", "+518", 81, "⭐ 🌕 💣", ["vs McClanahan"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 96.0 mph EV. McClanahan LHB split +0.59, HR risk -0.31. pitcher risk below avg (-0.31); park suppresses carry (-6%).""", blast="high"),
            row("Romy Gonzalez", "R", "+529", 58, "", ["vs McClanahan"], """1 HR, 2 near-HR, 90.9 mph EV. McClanahan RHB split -0.65, HR risk -0.31. tough split lane (-0.65); pitcher risk below avg (-0.31).""", blast="good"),
            row("Willson Contreras", "R", "+335", 58, "", ["vs McClanahan"], """1 HR, 1 near-HR, 93.4 mph EV. McClanahan RHB split -0.65, HR risk -0.31. tough split lane (-0.65); pitcher risk below avg (-0.31).""", blast="good"),
            row("Andruw Monasterio", "R", "+800", 58, "", ["vs McClanahan"], """0 HR, 1 near-HR, 91.2 mph EV. McClanahan RHB split -0.65, HR risk -0.31. tough split lane (-0.65); pitcher risk below avg (-0.31)."""),
            row("Hunter Feduccia", "L", "+1040", 62, "", ["vs Gray"], """1 HR, 2 near-HR, 96.6 mph EV. Gray LHB split -0.16, HR risk -0.33. slight split headwind (-0.16); pitcher risk below avg (-0.33).""", blast="good"),
            row("Jonathan Aranda", "L", "+487", 66, "⭐", ["vs Gray"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 95.2 mph EV. Gray LHB split -0.16, HR risk -0.33. slight split headwind (-0.16); pitcher risk below avg (-0.33).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ ATL - Nathan Eovaldi (R, TEX) vs Grant Holmes (R, ATL)",
        "description": "Tail key data: Park boost +5% (stadium -1%, weather +7%). Eovaldi (HR risk -0.04, vs LHB -0.41, vs RHB +0.28). Holmes (HR risk -0.02, vs LHB -0.03, vs RHB -0.03).",
        "rows": [
            row("Matt Olson", "L", "+151", 72, "🌕 💣", ["vs Eovaldi"], """2 HR, 2 near-HR, 95.9 mph EV. Eovaldi LHB split -0.41, HR risk -0.04. tough split lane (-0.41); pitcher risk below avg (-0.04).""", blast="high"),
            row("Drake Baldwin", "L", "+182", 62, "⭐", ["vs Eovaldi"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.6 mph EV. Eovaldi LHB split -0.41, HR risk -0.04. tough split lane (-0.41); pitcher risk below avg (-0.04).""", blast="good"),
            row("Joc Pederson", "L", "+205", 70, "⭐ 🌕 💣", ["vs Holmes"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.0 mph EV. Holmes LHB split -0.03, HR risk -0.02. slight split headwind (-0.03); pitcher risk below avg (-0.02).""", blast="high"),
        ],
    },
    {
        "title": "WSH @ ATH - Foster Griffin (L, WSH) vs Jacob Lopez (L, ATH)",
        "description": "Tail key data: Park boost +33% (stadium +30%, weather +3%). Griffin (HR risk -0.53, vs LHB -0.15, vs RHB -0.40). Lopez (HR risk -0.62, vs LHB -1.30, vs RHB +0.16).",
        "rows": [
            row("Shea Langeliers", "R", "N/A", 65, "💎", ["vs Griffin"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 95.1 mph EV. Griffin RHB split -0.40, HR risk -0.53. tough split lane (-0.40); pitcher suppresses HR (-0.53).""", blast="good"),
            row("Colby Thomas", "R", "N/A", 58, "", ["vs Griffin"], """1 HR, 1 near-HR, 85.9 mph EV. Griffin RHB split -0.40, HR risk -0.53. tough split lane (-0.40); pitcher suppresses HR (-0.53).""", blast="good"),
            row("James Wood", "L", "N/A", 63, "🌕 💣", ["vs Lopez"], """2 HR, 2 near-HR, 87.0 mph EV. Lopez LHB split -1.30, HR risk -0.62. tough split lane (-1.30); pitcher suppresses HR (-0.62).""", blast="high"),
            row("CJ Abrams", "L", "N/A", 58, "", ["vs Lopez"], """1 HR, 1 near-HR, 88.7 mph EV. Lopez LHB split -1.30, HR risk -0.62. tough split lane (-1.30); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Andres Chaparro", "R", "N/A", 73, "🌕 💣", ["vs Lopez"], """2 HR, 2 near-HR, 91.4 mph EV. Lopez RHB split +0.16, HR risk -0.62. pitcher suppresses HR (-0.62).""", blast="high"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-19")

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

    out = ROOT / '_games-0711.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
