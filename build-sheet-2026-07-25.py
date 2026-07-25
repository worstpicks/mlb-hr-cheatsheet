#!/usr/bin/env python3
"""Generate games[] block for 2026-07-25 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Andrew Vaughn (R)",
    "Bryan De La Cruz (R)",
    "Christian Encarnacion-Strand (R)",
    "Drake Baldwin (L)",
    "Elly De La Cruz (S)",
    "Esmerlyn Valdez (R)",
    "Kyle Manzardo (L)",
    "Matt Olson (L)",
    "Munetaka Murakami (L)",
    "Pete Alonso (R)",
    "Seiya Suzuki (R)",
    "Shohei Ohtani (L)",
    "Taylor Trammell (L)",
    "Victor Mesa Jr. (L)",
}

GEMS = {
    "Brett Baty (L)",
    "Brice Turang (L)",
    "Francisco Alvarez (R)",
    "Hunter Goodman (R)",
    "Jimmy Crooks (L)",
    "Julio Rodriguez (R)",
    "Lars Nootbaar (L)",
    "Max Schuemann (R)",
    "Michael Conforto (L)",
    "Patrick Bailey (S)",
    "Sal Stewart (R)",
    "Tyler Stephenson (R)",
    "Yordan Alvarez (L)",
}

PLAYER_TEAMS = {
    "Alan Roden (L)": "MIN",
    "Alec Bohm (R)": "PHI",
    "Alec Burleson (L)": "STL",
    "Amed Rosario (R)": "NYY",
    "Andrew Vaughn (R)": "MIL",
    "Ben Rice (L)": "NYY",
    "Brandon Nimmo (L)": "TEX",
    "Braxton Fulford (R)": "COL",
    "Brett Baty (L)": "NYM",
    "Brice Turang (L)": "MIL",
    "Bryan De La Cruz (R)": "PHI",
    "Byron Buxton (R)": "MIN",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Dalton Rushing (L)": "LAD",
    "Drake Baldwin (L)": "ATL",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Hunter Feduccia (L)": "TB",
    "Hunter Goodman (R)": "COL",
    "Isaac Paredes (R)": "HOU",
    "JJ Wetherholt (L)": "STL",
    "Jake Burger (R)": "TEX",
    "Jimmy Crooks (L)": "STL",
    "Joc Pederson (L)": "TEX",
    "Jonah Heim (S)": "ATH",
    "Julio Rodriguez (R)": "SEA",
    "Kyle Karros (R)": "COL",
    "Kyle Manzardo (L)": "CLE",
    "Lars Nootbaar (L)": "STL",
    "Luke Raley (L)": "SEA",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Max Muncy (R)": "ATH",
    "Max Schuemann (R)": "NYY",
    "Michael Conforto (L)": "CHC",
    "Mike Yastrzemski (L)": "ATL",
    "Munetaka Murakami (L)": "CWS",
    "Patrick Bailey (S)": "CLE",
    "Paul Goldschmidt (R)": "NYY",
    "Pete Alonso (R)": "BAL",
    "Richie Palacios (L)": "TB",
    "Ryan O'Hearn (L)": "PIT",
    "Sal Stewart (R)": "CIN",
    "Seiya Suzuki (R)": "CHC",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Steer (R)": "CIN",
    "Taylor Trammell (L)": "HOU",
    "Trea Turner (R)": "PHI",
    "Tristan Peters (L)": "CWS",
    "Tyler Soderstrom (L)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "Victor Mesa Jr. (L)": "TB",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("ATH @ MIN", "Barnett"),
    ("ATL @ BAL", "Elder"),
    ("COL @ MIL", "Feltner"),
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
        "title": "ATH @ MIN - Mason Barnett 🧤 (R, ATH) vs Connor Prielipp (L, MIN)",
        "description": "Tail key data: Park boost +2% (stadium -5%, weather +8%). Barnett 🧤 (HR risk 1.05, vs LHB +1.35, vs RHB +0.85). Prielipp (HR risk 0.83, vs LHB +0.25, vs RHB +1.18).",
        "rows": [
            row("Byron Buxton", "R", "+242", 84, "", ["vs Barnett"], """1 HR, 2 near-HR, 92.1 mph EV. Barnett RHB split +0.85, HR risk 1.05.""", blast="good"),
            row("Alan Roden", "L", "+370", 83, "", ["vs Barnett"], """0 HR, 1 near-HR, 92.7 mph EV. Barnett LHB split +1.35, HR risk 1.05. limited recent HR events.""", blast="good"),
            row("Shea Langeliers", "R", "+320", 70, "", ["vs Prielipp"], """0 HR, 90.6 mph EV. Prielipp RHB split +1.18, HR risk 0.83. limited recent HR events."""),
            row("Max Muncy", "R", "N/A", 92, "🌕 💣", ["vs Prielipp"], """3 HR, 3 near-HR, 88.8 mph EV. Prielipp RHB split +1.18, HR risk 0.83.""", blast="high"),
            row("Tyler Soderstrom", "L", "+560", 70, "", ["vs Prielipp"], """1 HR, 1 near-HR, 88.2 mph EV. Prielipp LHB split +0.25, HR risk 0.83.""", blast="good"),
            row("Jonah Heim", "S", "+630", 69, "", ["vs Prielipp"], """0 HR, 89.1 mph EV. Prielipp SHB→RHB split +1.18, HR risk 0.83. limited recent HR events."""),
        ],
    },
    {
        "title": "ATL @ BAL - Bryce Elder 🧤 (R, ATL) vs Brandon Young (R, BAL)",
        "description": "Tail key data: Park boost -2% (stadium -1%, weather -1%). Elder 🧤 (HR risk 1.49, vs LHB +0.56, vs RHB +2.02). Young (HR risk -0.37, vs LHB +0.22, vs RHB -0.81).",
        "rows": [
            row("Christian Encarnacion-Strand", "R", "+450", 80, "⭐", ["vs Elder"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 86.6 mph EV. Elder RHB split +2.02, HR risk 1.49. limited recent HR events; lighter EV form (86.6 mph)."""),
            row("Pete Alonso", "R", "+300", 91, "🚀 ⭐ 🌕 💣", ["vs Elder"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 100.0 mph EV. Elder RHB split +2.02, HR risk 1.49. limited recent HR events.""", blast="good"),
            row("Drake Baldwin", "L", "+182", 62, "⭐", ["vs Young"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.6 mph EV. Young LHB split +0.22, HR risk -0.37. pitcher risk below avg (-0.37).""", blast="good"),
            row("Matt Olson", "L", "+490", 62, "⭐ 🌕 💣", ["vs Young"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 86.0 mph EV. Young LHB split +0.22, HR risk -0.37. pitcher risk below avg (-0.37); lighter EV form (86.0 mph).""", blast="high"),
            row("Mike Yastrzemski", "L", "N/A", 58, "", ["vs Young"], """0 HR, 94.9 mph EV. Young LHB split +0.22, HR risk -0.37. pitcher risk below avg (-0.37); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CHC @ PIT - Shota Imanaga (L, CHC) vs Paul Skenes (R, PIT)",
        "description": "Tail key data: Park boost -16% (stadium -16%, weather -1%). Imanaga (HR risk 0.52, vs LHB +0.98, vs RHB +0.15). Skenes (HR risk -0.72, vs LHB -0.54, vs RHB -0.39).",
        "rows": [
            row("Ryan O'Hearn", "L", "+640", 73, "", ["vs Imanaga"], """1 HR, 2 near-HR, 91.5 mph EV. Imanaga LHB split +0.98, HR risk 0.52. park/weather net drag (-16%).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+300", 87, "🚀 ⭐ 🌕 💣", ["vs Imanaga"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 101.3 mph EV. Imanaga RHB split +0.15, HR risk 0.52. park/weather net drag (-16%).""", blast="high"),
            row("Seiya Suzuki", "R", "+500", 58, "⭐ 🌕 💣", ["vs Skenes"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.0 mph EV. Skenes RHB split -0.39, HR risk -0.72. slight split headwind (-0.39); pitcher suppresses HR (-0.72).""", blast="high"),
            row("Michael Conforto", "L", "N/A", 59, "🌕 💣 💎", ["vs Skenes"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 91.0 mph EV. Skenes LHB split -0.54, HR risk -0.72. tough split lane (-0.54); pitcher suppresses HR (-0.72).""", blast="high"),
        ],
    },
    {
        "title": "CIN @ STL - Hunter Greene (R, CIN) vs Andre Pallante (R, STL)",
        "description": "Tail key data: Park boost -8% (stadium -9%, weather +1%). Greene (HR risk 0.86, vs LHB +0.15, vs RHB +1.21). Pallante (HR risk -1.24, vs LHB -0.60, vs RHB -1.29).",
        "rows": [
            row("Jimmy Crooks", "L", "+800", 73, "💎", ["vs Greene"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.5 mph EV. Greene LHB split +0.15, HR risk 0.86. park/weather net drag (-8%).""", blast="good"),
            row("JJ Wetherholt", "L", "+551", 73, "", ["vs Greene"], """1 HR, 1 near-HR, 94.2 mph EV. Greene LHB split +0.15, HR risk 0.86. park/weather net drag (-8%).""", blast="good"),
            row("Lars Nootbaar", "L", "+600", 70, "💎", ["vs Greene"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.3 mph EV. Greene LHB split +0.15, HR risk 0.86. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Alec Burleson", "L", "+450", 69, "⭐", ["vs Greene"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.0 mph EV. Greene LHB split +0.15, HR risk 0.86. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Elly De La Cruz", "S", "+600", 61, "🚀 ⭐ 🌕 💣", ["vs Pallante"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 101.0 mph EV. Pallante SHB→LHB split -0.60, HR risk -1.24. tough split lane (-0.60); pitcher suppresses HR (-1.24).""", blast="high"),
            row("Tyler Stephenson", "R", "+800", 58, "🌕 💣 💎", ["vs Pallante"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.0 mph EV. Pallante RHB split -1.29, HR risk -1.24. tough split lane (-1.29); pitcher suppresses HR (-1.24).""", blast="high"),
            row("Eugenio Suarez", "R", "+514", 58, "", ["vs Pallante"], """1 HR, 1 near-HR, 96.0 mph EV. Pallante RHB split -1.29, HR risk -1.24. tough split lane (-1.29); pitcher suppresses HR (-1.24).""", blast="good"),
            row("Spencer Steer", "R", "+750", 58, "🌕 💣", ["vs Pallante"], """2 HR, 2 near-HR, 89.1 mph EV. Pallante RHB split -1.29, HR risk -1.24. tough split lane (-1.29); pitcher suppresses HR (-1.24).""", blast="high"),
            row("Sal Stewart", "R", "+586", 58, "🌕 💣 💎", ["vs Pallante"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.3 mph EV. Pallante RHB split -1.29, HR risk -1.24. tough split lane (-1.29); pitcher suppresses HR (-1.24).""", blast="high"),
        ],
    },
    {
        "title": "CLE @ TB - Tanner Bibee (R, CLE) vs Nick Martinez (R, TB)",
        "description": "Tail key data: Park boost -4% (stadium -5%, weather +1%). Bibee (HR risk -0.11, vs LHB +0.48, vs RHB -0.91). Martinez (HR risk -0.26, vs LHB +0.52, vs RHB -0.99).",
        "rows": [
            row("Victor Mesa Jr.", "L", "+560", 77, "⭐ 🌕 💣", ["vs Bibee"], """Worst Pickz Favorite. 3 HR, 2 near-HR, 91.8 mph EV. Bibee LHB split +0.48, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="high"),
            row("Richie Palacios", "L", "+1060", 61, "", ["vs Bibee"], """1 HR, 2 near-HR, 89.5 mph EV. Bibee LHB split +0.48, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="good"),
            row("Hunter Feduccia", "L", "+900", 58, "", ["vs Bibee"], """0 HR, 91.8 mph EV. Bibee LHB split +0.48, HR risk -0.11. pitcher risk below avg (-0.11); limited recent HR events."""),
            row("Kyle Manzardo", "L", "+460", 67, "⭐", ["vs Martinez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.7 mph EV. Martinez LHB split +0.52, HR risk -0.26. pitcher risk below avg (-0.26).""", blast="good"),
            row("Patrick Bailey", "S", "+860", 75, "🌕 💣 💎", ["vs Martinez"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 97.8 mph EV. Martinez SHB→LHB split +0.52, HR risk -0.26. pitcher risk below avg (-0.26).""", blast="high"),
        ],
    },
    {
        "title": "COL @ MIL - Ryan Feltner 🧤 (R, COL) vs Robert Gasser (L, MIL)",
        "description": "Tail key data: Park boost +29% (stadium +10%, weather +19%). Feltner 🧤 (HR risk 1.29, vs LHB +1.41, vs RHB +0.52). Gasser (HR risk 0.84, vs LHB -0.40, vs RHB +0.86).",
        "rows": [
            row("Brice Turang", "L", "+600", 98, "🌕 💣 💎", ["vs Feltner"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 93.6 mph EV. Feltner LHB split +1.41, HR risk 1.29.""", blast="high"),
            row("Andrew Vaughn", "R", "+450", 91, "⭐ 🌕 💣", ["vs Feltner"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.1 mph EV. Feltner RHB split +0.52, HR risk 1.29.""", blast="good"),
            row("Hunter Goodman", "R", "+255", 97, "🚀 🌕 💣 💎", ["vs Gasser"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 100.5 mph EV. Gasser RHB split +0.86, HR risk 0.84.""", blast="high"),
            row("Braxton Fulford", "R", "N/A", 82, "", ["vs Gasser"], """0 HR, 1 near-HR, 92.7 mph EV. Gasser RHB split +0.86, HR risk 0.84. limited recent HR events.""", blast="good"),
            row("Kyle Karros", "R", "+620", 73, "", ["vs Gasser"], """0 HR, 89.8 mph EV. Gasser RHB split +0.86, HR risk 0.84. limited recent HR events."""),
        ],
    },
    {
        "title": "HOU @ CWS - Hunter Brown (R, HOU) vs Sean Burke (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Brown (HR risk -0.03, vs LHB +0.33, vs RHB -0.27). Burke (HR risk -0.10, vs LHB -0.06, vs RHB -0.17).",
        "rows": [
            row("Munetaka Murakami", "L", "+320", 77, "⭐ 🌕 💣", ["vs Brown"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 90.7 mph EV. Brown LHB split +0.33, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="high"),
            row("Tristan Peters", "L", "+875", 58, "", ["vs Brown"], """0 HR, 1 near-HR, 90.8 mph EV. Brown LHB split +0.33, HR risk -0.03. pitcher risk below avg (-0.03); limited recent HR events."""),
            row("Taylor Trammell", "L", "N/A", 77, "⭐ 🌕 💣", ["vs Burke"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 96.0 mph EV. Burke LHB split -0.06, HR risk -0.10. slight split headwind (-0.06); pitcher risk below avg (-0.10).""", blast="high"),
            row("Yordan Alvarez", "L", "+235", 77, "🌕 💣 💎", ["vs Burke"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 99.1 mph EV. Burke LHB split -0.06, HR risk -0.10. slight split headwind (-0.06); pitcher risk below avg (-0.10).""", blast="high"),
            row("Isaac Paredes", "R", "+437", 58, "", ["vs Burke"], """1 HR, 1 near-HR, 84.6 mph EV. Burke RHB split -0.17, HR risk -0.10. slight split headwind (-0.17); pitcher risk below avg (-0.10).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ NYM - Yoshinobu Yamamoto (R, LAD) vs Nolan McLean (R, NYM)",
        "description": "Tail key data: Park boost -1% (stadium -2%, weather +1%). Yamamoto (HR risk -0.74, vs LHB -0.39, vs RHB -0.67). McLean (HR risk -0.75, vs LHB -0.74, vs RHB -0.39).",
        "rows": [
            row("Francisco Lindor", "S", "+500", 58, "", ["vs Yamamoto"], """1 HR, 1 near-HR, 94.6 mph EV. Yamamoto SHB→LHB split -0.39, HR risk -0.74. slight split headwind (-0.39); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Brett Baty", "L", "+775", 60, "🌕 💣 💎", ["vs Yamamoto"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 92.3 mph EV. Yamamoto LHB split -0.39, HR risk -0.74. slight split headwind (-0.39); pitcher suppresses HR (-0.74).""", blast="high"),
            row("Francisco Alvarez", "R", "+540", 58, "🌕 💣 💎", ["vs Yamamoto"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 88.8 mph EV. Yamamoto RHB split -0.67, HR risk -0.74. tough split lane (-0.67); pitcher suppresses HR (-0.74).""", blast="high"),
            row("Shohei Ohtani", "L", "+291", 58, "⭐", ["vs McLean"], """Worst Pickz Favorite. 0 HR, 98.5 mph EV. McLean LHB split -0.74, HR risk -0.75. tough split lane (-0.74); pitcher suppresses HR (-0.75).""", blast="good"),
            row("Dalton Rushing", "L", "+550", 58, "", ["vs McLean"], """1 HR, 1 near-HR, 93.5 mph EV. McLean LHB split -0.74, HR risk -0.75. tough split lane (-0.74); pitcher suppresses HR (-0.75).""", blast="good"),
            row("Max Muncy", "L", "+500", 58, "", ["vs McLean"], """1 HR, 1 near-HR, 92.7 mph EV. McLean LHB split -0.74, HR risk -0.75. tough split lane (-0.74); pitcher suppresses HR (-0.75).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ PHI - Ryan Weathers (L, NYY) vs Brian Keller (R, PHI)",
        "description": "Tail key data: Park boost +22% (stadium +14%, weather +8%). Weathers (HR risk -0.16, vs LHB -0.08, vs RHB -0.11). Keller (HR risk -0.57, vs LHB -1.14, vs RHB +0.24).",
        "rows": [
            row("Bryan De La Cruz", "R", "N/A", 68, "🚀 ⭐", ["vs Weathers"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 105.8 mph EV. Weathers RHB split -0.11, HR risk -0.16. slight split headwind (-0.11); pitcher risk below avg (-0.16).""", blast="good"),
            row("Alec Bohm", "R", "+630", 73, "🌕 💣", ["vs Weathers"], """2 HR, 2 near-HR, 92.3 mph EV. Weathers RHB split -0.11, HR risk -0.16. slight split headwind (-0.11); pitcher risk below avg (-0.16).""", blast="high"),
            row("Trea Turner", "R", "+520", 76, "🌕 💣", ["vs Weathers"], """2 HR, 2 near-HR, 95.1 mph EV. Weathers RHB split -0.11, HR risk -0.16. slight split headwind (-0.11); pitcher risk below avg (-0.16).""", blast="high"),
            row("Max Schuemann", "R", "N/A", 66, "💎", ["vs Keller"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.2 mph EV. Keller RHB split +0.24, HR risk -0.57. pitcher suppresses HR (-0.57).""", blast="good"),
            row("Amed Rosario", "R", "N/A", 59, "", ["vs Keller"], """0 HR, 93.7 mph EV. Keller RHB split +0.24, HR risk -0.57. pitcher suppresses HR (-0.57); limited recent HR events.""", blast="good"),
            row("Ben Rice", "L", "+333", 58, "", ["vs Keller"], """1 HR, 2 near-HR, 84.8 mph EV. Keller LHB split -1.14, HR risk -0.57. tough split lane (-1.14); pitcher suppresses HR (-0.57).""", blast="good"),
            row("Paul Goldschmidt", "R", "+455", 61, "", ["vs Keller"], """1 HR, 2 near-HR, 88.3 mph EV. Keller RHB split +0.24, HR risk -0.57. pitcher suppresses HR (-0.57).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ TEX - Bryan Woo (R, SEA) vs Nathan Eovaldi (R, TEX)",
        "description": "Tail key data: Park boost -10% (stadium -9%, weather -1%). Woo (HR risk -0.34, vs LHB -0.06, vs RHB -0.43). Eovaldi (HR risk 0.32, vs LHB +0.10, vs RHB +0.50).",
        "rows": [
            row("Jake Burger", "R", "+473", 63, "🌕 💣", ["vs Woo"], """2 HR, 2 near-HR, 94.4 mph EV. Woo RHB split -0.43, HR risk -0.34. tough split lane (-0.43); pitcher risk below avg (-0.34).""", blast="high"),
            row("Joc Pederson", "L", "+356", 65, "🌕 💣", ["vs Woo"], """2 HR, 2 near-HR, 93.4 mph EV. Woo LHB split -0.06, HR risk -0.34. slight split headwind (-0.06); pitcher risk below avg (-0.34).""", blast="high"),
            row("Brandon Nimmo", "L", "+409", 58, "", ["vs Woo"], """0 HR, 89.5 mph EV. Woo LHB split -0.06, HR risk -0.34. slight split headwind (-0.06); pitcher risk below avg (-0.34)."""),
            row("Julio Rodriguez", "R", "+500", 70, "💎", ["vs Eovaldi"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 95.5 mph EV. Eovaldi RHB split +0.50, HR risk 0.32. park/weather net drag (-10%).""", blast="good"),
            row("Luke Raley", "L", "+440", 58, "", ["vs Eovaldi"], """0 HR, 91.1 mph EV. Eovaldi LHB split +0.10, HR risk 0.32. park/weather net drag (-10%); limited recent HR events."""),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-25")

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
