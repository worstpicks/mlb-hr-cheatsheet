#!/usr/bin/env python3
"""Generate games[] block for 2026-07-10 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Heliot Ramos (R)",
    "Heriberto Hernandez (R)",
    "Hunter Goodman (R)",
    "Jac Caglianone (L)",
    "Jarren Duran (L)",
    "Jordan Walker (R)",
    "Juan Soto (L)",
    "Kazuma Okamoto (R)",
    "Kyle Schwarber (L)",
    "Manny Machado (R)",
    "Matt Olson (L)",
    "Max Kepler (L)",
    "Mike Trout (R)",
    "Mookie Betts (R)",
    "Munetaka Murakami (L)",
    "Nick Kurtz (L)",
    "Pete Crow-Armstrong (L)",
    "Riley Greene (L)",
    "Shea Langeliers (R)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Joey Bart (R)",
    "Kyle Teel (L)",
    "Nelson Velazquez (R)",
    "Taylor Trammell (L)",
    "Victor Bericoto (R)",
}

PLAYER_TEAMS = {
    "A.J. Ewing (L)": "NYM",
    "Austin Wells (L)": "NYY",
    "Ben Rice (L)": "NYY",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Brice Turang (L)": "MIL",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Christian Walker (R)": "HOU",
    "Cole Young (L)": "SEA",
    "Corbin Carroll (L)": "ARI",
    "Curtis Mead (R)": "WSH",
    "Dalton Rushing (L)": "LAD",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Dylan Crews (R)": "WSH",
    "Edmundo Sosa (R)": "PHI",
    "Edouard Julien (L)": "COL",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Fernando Tatis Jr. (R)": "SD",
    "Garrett Mitchell (L)": "MIL",
    "George Springer (R)": "TOR",
    "Griffin Conine (L)": "MIA",
    "Heliot Ramos (R)": "SF",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "TB",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Jac Caglianone (L)": "KC",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Jarren Duran (L)": "BOS",
    "Joc Pederson (L)": "TEX",
    "Joey Bart (R)": "ATL",
    "Jordan Walker (R)": "STL",
    "Josh Bell (S)": "MIN",
    "Josh Lowe (L)": "LAA",
    "Juan Soto (L)": "NYM",
    "Junior Perez (R)": "CWS",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Teel (L)": "CWS",
    "Lane Thomas (R)": "KC",
    "Leo Jimenez (R)": "MIA",
    "Luis Campusano (R)": "SD",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Max Muncy (L)": "LAD",
    "Max Schuemann (R)": "NYY",
    "Michael Conforto (L)": "CHC",
    "Michael Massey (L)": "KC",
    "Mike Trout (R)": "LAA",
    "Mike Yastrzemski (L)": "ATL",
    "Mitch Garver (R)": "SEA",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "STL",
    "Nick Kurtz (L)": "ATH",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Ryan O'Hearn (L)": "PIT",
    "Sal Stewart (R)": "CIN",
    "Samuel Basallo (L)": "BAL",
    "Seiya Suzuki (R)": "CHC",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Taylor Trammell (L)": "HOU",
    "Trent Grisham (L)": "NYY",
    "Tyler O'Neill (R)": "BAL",
    "Victor Bericoto (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("ATH @ CWS", "Civale"),
    ("CHC @ CIN", "Greene"),
    ("COL @ SF", "Gordon"),
    ("LAA @ MIN", "Matthews"),
    ("TOR @ SD", "Bieber"),
    ("TOR @ SD", "Sears"),
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
        "title": "ARI @ LAD - Eduardo Rodriguez (L, ARI) vs Shohei Ohtani (R, LAD)",
        "description": "Tail key data: Park boost +16% (stadium +17%, weather -1%). Rodriguez (HR risk -0.16, vs LHB -0.08, vs RHB -0.11). Ohtani (HR risk -1.01, vs LHB -0.85, vs RHB -1.05).",
        "rows": [
            row("Shohei Ohtani", "L", "N/A", 62, "", ["vs Rodriguez"], """1 HR, 1 near-HR, 87.8 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; lighter EV form (87.8 mph).""", blast="good"),
            row("Max Muncy", "L", "N/A", 62, "", ["vs Rodriguez"], """1 HR, 1 near-HR, 87.2 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; lighter EV form (87.2 mph).""", blast="good"),
            row("Dalton Rushing", "L", "N/A", 58, "", ["vs Rodriguez"], """0 HR, 91.9 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
            row("Mookie Betts", "R", "N/A", 62, "⭐", ["vs Rodriguez"], """Worst Pickz Favorite. 0 HR, 93.0 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Max Kepler", "L", "N/A", 58, "⭐", ["vs Ohtani"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 92.0 mph EV. Ohtani LHB split -0.85, HR risk -1.01. tough split lane (-0.85); pitcher suppresses HR (-1.01).""", blast="good"),
            row("Ketel Marte", "S", "N/A", 68, "🌕 💣", ["vs Ohtani"], """2 HR, 3 near-HR, 96.0 mph EV. Ohtani RHB split -1.05, HR risk -1.01. tough split lane (-1.05); pitcher suppresses HR (-1.01).""", blast="high"),
            row("Corbin Carroll", "L", "N/A", 58, "", ["vs Ohtani"], """0 HR, 1 near-HR, 92.2 mph EV. Ohtani LHB split -0.85, HR risk -1.01. tough split lane (-0.85); pitcher suppresses HR (-1.01).""", blast="good"),
        ],
    },
    {
        "title": "ATH @ CWS - Aaron Civale 🧤 (R, ATH) vs Sean Burke (R, CWS)",
        "description": "Tail key data: Park boost +10% (stadium +3%, weather +7%). Civale 🧤 (HR risk 1.11, vs LHB +1.22, vs RHB +0.50). Burke (HR risk 0.23, vs LHB +0.08, vs RHB +0.25).",
        "rows": [
            row("Kyle Teel", "L", "+279", 89, "🌕 💣 💎", ["vs Civale"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.5 mph EV. Civale LHB split +1.22, HR risk 1.11.""", blast="good"),
            row("Junior Perez", "R", "N/A", 86, "🚀", ["vs Civale"], """1 HR, 1 near-HR, 100.9 mph EV. Civale RHB split +0.50, HR risk 1.11.""", blast="good"),
            row("Munetaka Murakami", "L", "N/A", 94, "🚀 ⭐ 🌕 💣", ["vs Civale"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 101.1 mph EV. Civale LHB split +1.22, HR risk 1.11.""", blast="high"),
            row("Nick Kurtz", "L", "+137", 71, "⭐", ["vs Burke"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.9 mph EV. Burke LHB split +0.08, HR risk 0.23.""", blast="good"),
            row("Shea Langeliers", "R", "+155", 64, "⭐", ["vs Burke"], """Worst Pickz Favorite. 0 HR, 94.7 mph EV. Burke RHB split +0.25, HR risk 0.23. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "ATL @ STL - Chris Sale (L, ATL) vs Kyle Leahy (R, STL)",
        "description": "Tail key data: Park boost -11% (stadium -10%, weather -1%). Sale (HR risk -0.74, vs LHB -1.32, vs RHB -0.32). Leahy (HR risk -0.15, vs LHB -0.44, vs RHB +0.22).",
        "rows": [
            row("Jordan Walker", "R", "N/A", 58, "🚀 ⭐", ["vs Sale"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 104.5 mph EV. Sale RHB split -0.32, HR risk -0.74. slight split headwind (-0.32); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 58, "💎", ["vs Sale"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.8 mph EV. Sale RHB split -0.32, HR risk -0.74. slight split headwind (-0.32); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Matt Olson", "L", "N/A", 69, "⭐ 🌕 💣", ["vs Leahy"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.1 mph EV. Leahy LHB split -0.44, HR risk -0.15. tough split lane (-0.44); pitcher risk below avg (-0.15).""", blast="high"),
            row("Joey Bart", "R", "N/A", 61, "💎", ["vs Leahy"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 89.3 mph EV. Leahy RHB split +0.22, HR risk -0.15. pitcher risk below avg (-0.15); park/weather net drag (-11%).""", blast="good"),
            row("Drake Baldwin", "L", "N/A", 58, "", ["vs Leahy"], """0 HR, 95.1 mph EV. Leahy LHB split -0.44, HR risk -0.15. tough split lane (-0.44); pitcher risk below avg (-0.15).""", blast="good"),
            row("Mike Yastrzemski", "L", "N/A", 58, "", ["vs Leahy"], """1 HR, 2 near-HR, 84.9 mph EV. Leahy LHB split -0.44, HR risk -0.15. tough split lane (-0.44); pitcher risk below avg (-0.15).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ NYM - Sonny Gray (R, BOS) vs Nolan McLean (R, NYM)",
        "description": "Tail key data: Park boost +5% (stadium -1%, weather +6%). Gray (HR risk -0.39, vs LHB -0.23, vs RHB -0.54). McLean (HR risk -0.74, vs LHB -0.89, vs RHB -0.37).",
        "rows": [
            row("Juan Soto", "L", "+309", 65, "⭐ 🌕 💣", ["vs Gray"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.7 mph EV. Gray LHB split -0.23, HR risk -0.39. slight split headwind (-0.23); pitcher risk below avg (-0.39).""", blast="high"),
            row("A.J. Ewing", "L", "+880", 78, "🌕 💣", ["vs Gray"], """3 HR, 4 near-HR, 97.8 mph EV. Gray LHB split -0.23, HR risk -0.39. slight split headwind (-0.23); pitcher risk below avg (-0.39).""", blast="high"),
            row("Wilyer Abreu", "L", "+460", 58, "", ["vs McLean"], """0 HR, 1 near-HR, 93.9 mph EV. McLean LHB split -0.89, HR risk -0.74. tough split lane (-0.89); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Jarren Duran", "L", "+610", 58, "⭐", ["vs McLean"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 90.8 mph EV. McLean LHB split -0.89, HR risk -0.74. tough split lane (-0.89); pitcher suppresses HR (-0.74).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ CIN - Shota Imanaga (L, CHC) vs Hunter Greene 🧤 (R, CIN)",
        "description": "Tail key data: Park boost +28% (stadium +14%, weather +14%). Imanaga (HR risk 0.25, vs LHB +0.61, vs RHB +0.10). Greene 🧤 (HR risk 1.63, vs LHB +2.31, vs RHB -0.34).",
        "rows": [
            row("Sal Stewart", "R", "+400", 82, "🌕 💣", ["vs Imanaga"], """2 HR, 2 near-HR, 94.3 mph EV. Imanaga RHB split +0.10, HR risk 0.25.""", blast="high"),
            row("Elly De La Cruz", "S", "+400", 80, "", ["vs Imanaga"], """1 HR, 2 near-HR, 95.9 mph EV. Imanaga RHB split +0.10, HR risk 0.25.""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+320", 99, "⭐ 🌕 💣", ["vs Greene"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 87.3 mph EV. Greene LHB split +2.31, HR risk 1.63. lighter EV form (87.3 mph).""", blast="high"),
            row("Seiya Suzuki", "R", "+340", 69, "", ["vs Greene"], """0 HR, 1 near-HR, 84.9 mph EV. Greene RHB split -0.34, HR risk 1.63. slight split headwind (-0.34); limited recent HR events."""),
            row("Ian Happ", "S", "+300", 92, "🌕 💣", ["vs Greene"], """0 HR, 92.9 mph EV. Greene RHB split -0.34, HR risk 1.63. slight split headwind (-0.34); limited recent HR events.""", blast="good"),
            row("Michael Conforto", "L", "+370", 96, "🌕 💣", ["vs Greene"], """1 HR, 3 near-HR, 90.0 mph EV. Greene LHB split +2.31, HR risk 1.63.""", blast="good"),
        ],
    },
    {
        "title": "CLE @ MIA - Parker Messick (L, CLE) vs Sandy Alcantara (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -13%, weather +0%). Messick (HR risk -1.02, vs LHB -1.07, vs RHB -0.69). Alcantara (HR risk -0.89, vs LHB -0.65, vs RHB -0.98).",
        "rows": [
            row("Heriberto Hernandez", "R", "N/A", 58, "⭐ 🌕 💣", ["vs Messick"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.6 mph EV. Messick RHB split -0.69, HR risk -1.02. tough split lane (-0.69); pitcher suppresses HR (-1.02).""", blast="high"),
            row("Griffin Conine", "L", "N/A", 58, "", ["vs Messick"], """0 HR, 91.2 mph EV. Messick LHB split -1.07, HR risk -1.02. tough split lane (-1.07); pitcher suppresses HR (-1.02)."""),
            row("Leo Jimenez", "R", "N/A", 58, "", ["vs Messick"], """1 HR, 2 near-HR, 90.7 mph EV. Messick RHB split -0.69, HR risk -1.02. tough split lane (-0.69); pitcher suppresses HR (-1.02).""", blast="good"),
            row("Rhys Hoskins", "R", "N/A", 58, "", ["vs Alcantara"], """1 HR, 1 near-HR, 90.7 mph EV. Alcantara RHB split -0.98, HR risk -0.89. tough split lane (-0.98); pitcher suppresses HR (-0.89).""", blast="good"),
        ],
    },
    {
        "title": "COL @ SF - Tanner Gordon 🧤 (R, COL) vs Robbie Ray (L, SF)",
        "description": "Tail key data: Park boost -23% (stadium -16%, weather -7%). Gordon 🧤 (HR risk 1.14, vs LHB +1.33, vs RHB +0.63). Ray (HR risk -0.20, vs LHB -0.54, vs RHB +0.01).",
        "rows": [
            row("Rafael Devers", "L", "N/A", 91, "🌕 💣", ["vs Gordon"], """2 HR, 2 near-HR, 92.5 mph EV. Gordon LHB split +1.33, HR risk 1.14. park/weather net drag (-23%).""", blast="high"),
            row("Heliot Ramos", "R", "N/A", 73, "⭐", ["vs Gordon"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 91.8 mph EV. Gordon RHB split +0.63, HR risk 1.14. park/weather net drag (-23%).""", blast="good"),
            row("Bryce Eldridge", "L", "N/A", 81, "", ["vs Gordon"], """0 HR, 1 near-HR, 96.2 mph EV. Gordon LHB split +1.33, HR risk 1.14. park/weather net drag (-23%); limited recent HR events.""", blast="good"),
            row("Victor Bericoto", "R", "N/A", 78, "💎", ["vs Gordon"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.1 mph EV. Gordon RHB split +0.63, HR risk 1.14. park/weather net drag (-23%).""", blast="good"),
            row("Hunter Goodman", "R", "N/A", 67, "⭐ 🌕 💣", ["vs Ray"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.1 mph EV. Ray RHB split +0.01, HR risk -0.20. pitcher risk below avg (-0.20); park/weather net drag (-23%).""", blast="high"),
            row("Edouard Julien", "L", "N/A", 58, "", ["vs Ray"], """0 HR, 1 near-HR, 92.7 mph EV. Ray LHB split -0.54, HR risk -0.20. tough split lane (-0.54); pitcher risk below avg (-0.20).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ TEX - Hunter Brown (R, HOU) vs Cal Quantrill (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -10%, weather -1%). Brown (HR risk -0.09, vs LHB -0.11, vs RHB +0.05). Quantrill (HR risk 0.20, vs LHB +0.15, vs RHB +0.12).",
        "rows": [
            row("Brandon Nimmo", "L", "N/A", 58, "", ["vs Brown"], """0 HR, 1 near-HR, 90.8 mph EV. Brown LHB split -0.11, HR risk -0.09. slight split headwind (-0.11); pitcher risk below avg (-0.09)."""),
            row("Joc Pederson", "L", "N/A", 58, "", ["vs Brown"], """1 HR, 2 near-HR, 92.2 mph EV. Brown LHB split -0.11, HR risk -0.09. slight split headwind (-0.11); pitcher risk below avg (-0.09).""", blast="good"),
            row("Yordan Alvarez", "L", "+270", 58, "⭐", ["vs Quantrill"], """Worst Pickz Favorite. 0 HR, 94.3 mph EV. Quantrill LHB split +0.15, HR risk 0.20. park/weather net drag (-11%); limited recent HR events.""", blast="good"),
            row("Taylor Trammell", "L", "N/A", 58, "💎", ["vs Quantrill"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 79.2 mph EV. Quantrill LHB split +0.15, HR risk 0.20. park/weather net drag (-11%); lighter EV form (79.2 mph).""", blast="good"),
            row("Christian Walker", "R", "+401", 58, "", ["vs Quantrill"], """1 HR, 1 near-HR, 85.2 mph EV. Quantrill RHB split +0.12, HR risk 0.20. park/weather net drag (-11%); lighter EV form (85.2 mph).""", blast="good"),
        ],
    },
    {
        "title": "KC @ BAL - Luinder Avila (R, KC) vs Brandon Young (R, BAL)",
        "description": "Tail key data: Park boost +5% (stadium -1%, weather +6%). Avila (HR risk -0.45, vs LHB -0.68, vs RHB +0.30). Young (HR risk -0.61, vs LHB -0.46, vs RHB -0.65).",
        "rows": [
            row("Pete Alonso", "R", "N/A", 58, "", ["vs Avila"], """1 HR, 2 near-HR, 84.0 mph EV. Avila RHB split +0.30, HR risk -0.45. pitcher suppresses HR (-0.45); lighter EV form (84.0 mph).""", blast="good"),
            row("Tyler O'Neill", "R", "N/A", 60, "", ["vs Avila"], """0 HR, 1 near-HR, 95.9 mph EV. Avila RHB split +0.30, HR risk -0.45. pitcher suppresses HR (-0.45); limited recent HR events.""", blast="good"),
            row("Samuel Basallo", "L", "N/A", 72, "🌕 💣", ["vs Avila"], """2 HR, 4 near-HR, 96.3 mph EV. Avila LHB split -0.68, HR risk -0.45. tough split lane (-0.68); pitcher suppresses HR (-0.45).""", blast="high"),
            row("Jac Caglianone", "L", "N/A", 66, "🚀 ⭐ 🌕 💣", ["vs Young"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 107.5 mph EV. Young LHB split -0.46, HR risk -0.61. tough split lane (-0.46); pitcher suppresses HR (-0.61).""", blast="high"),
            row("Michael Massey", "L", "N/A", 58, "", ["vs Young"], """0 HR, 2 near-HR, 94.8 mph EV. Young LHB split -0.46, HR risk -0.61. tough split lane (-0.46); pitcher suppresses HR (-0.61).""", blast="good"),
            row("Lane Thomas", "R", "N/A", 58, "", ["vs Young"], """0 HR, 94.6 mph EV. Young RHB split -0.65, HR risk -0.61. tough split lane (-0.65); pitcher suppresses HR (-0.61).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ MIN - Grayson Rodriguez (R, LAA) vs Zebby Matthews 🧤 (R, MIN)",
        "description": "Tail key data: Park boost +1% (stadium -7%, weather +8%). Rodriguez (HR risk 0.80, vs LHB +1.48, vs RHB -0.49). Matthews 🧤 (HR risk 0.98, vs LHB +1.09, vs RHB +0.61).",
        "rows": [
            row("Kody Clemens", "L", "+412", 81, "🌕 💣", ["vs Rodriguez"], """2 HR, 3 near-HR, 98.0 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; park suppresses carry (-7%).""", blast="high"),
            row("Josh Bell", "S", "+520", 69, "", ["vs Rodriguez"], """1 HR, 3 near-HR, 92.0 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; park suppresses carry (-7%).""", blast="good"),
            row("Mike Trout", "R", "N/A", 85, "⭐ 🌕 💣", ["vs Matthews"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 88.1 mph EV. Matthews RHB split +0.61, HR risk 0.98. park suppresses carry (-7%).""", blast="high"),
            row("Josh Lowe", "L", "N/A", 91, "🌕 💣", ["vs Matthews"], """1 HR, 3 near-HR, 94.7 mph EV. Matthews LHB split +1.09, HR risk 0.98. park suppresses carry (-7%).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ PIT - Brandon Sproat (R, MIL) vs Braxton Ashcraft (R, PIT)",
        "description": "Tail key data: Park boost +1% (stadium -15%, weather +16%). Sproat (HR risk -0.33, vs LHB -0.49, vs RHB +0.01). Ashcraft (HR risk -0.25, vs LHB +0.01, vs RHB -0.66).",
        "rows": [
            row("Bryan Reynolds", "S", "+560", 60, "", ["vs Sproat"], """1 HR, 3 near-HR, 88.0 mph EV. Sproat RHB split +0.01, HR risk -0.33. pitcher risk below avg (-0.33); park suppresses carry (-15%).""", blast="good"),
            row("Ryan O'Hearn", "L", "+560", 58, "", ["vs Sproat"], """1 HR, 2 near-HR, 90.7 mph EV. Sproat LHB split -0.49, HR risk -0.33. tough split lane (-0.49); pitcher risk below avg (-0.33).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+470", 58, "", ["vs Sproat"], """0 HR, 1 near-HR, 83.9 mph EV. Sproat RHB split +0.01, HR risk -0.33. pitcher risk below avg (-0.33); park suppresses carry (-15%)."""),
            row("Brandon Lowe", "L", "+350", 58, "", ["vs Sproat"], """1 HR, 2 near-HR, 94.2 mph EV. Sproat LHB split -0.49, HR risk -0.33. tough split lane (-0.49); pitcher risk below avg (-0.33).""", blast="good"),
            row("Jake Bauers", "L", "+750", 58, "", ["vs Ashcraft"], """0 HR, 87.0 mph EV. Ashcraft LHB split +0.01, HR risk -0.25. pitcher risk below avg (-0.25); park suppresses carry (-15%)."""),
            row("Garrett Mitchell", "L", "+600", 64, "🚀", ["vs Ashcraft"], """1 HR, 2 near-HR, 100.0 mph EV. Ashcraft LHB split +0.01, HR risk -0.25. pitcher risk below avg (-0.25); park suppresses carry (-15%).""", blast="good"),
            row("Brice Turang", "L", "+830", 58, "", ["vs Ashcraft"], """0 HR, 96.1 mph EV. Ashcraft LHB split +0.01, HR risk -0.25. pitcher risk below avg (-0.25); park suppresses carry (-15%).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ WSH - Ryan Weathers (L, NYY) vs Carson Palmquist (L, WSH)",
        "description": "Tail key data: Park boost +14% (stadium +3%, weather +11%). Weathers (HR risk 0.26, vs LHB +0.41, vs RHB +0.27). Palmquist (HR risk -0.79, vs LHB -0.06, vs RHB -0.06).",
        "rows": [
            row("James Wood", "L", "+340", 74, "🌕 💣", ["vs Weathers"], """2 HR, 2 near-HR, 86.6 mph EV. Weathers LHB split +0.41, HR risk 0.26. lighter EV form (86.6 mph).""", blast="high"),
            row("Curtis Mead", "R", "+400", 61, "", ["vs Weathers"], """0 HR, 2 near-HR, 87.0 mph EV. Weathers RHB split +0.27, HR risk 0.26. lighter EV form (87.0 mph).""", blast="good"),
            row("Dylan Crews", "R", "+430", 72, "", ["vs Weathers"], """1 HR, 1 near-HR, 95.0 mph EV. Weathers RHB split +0.27, HR risk 0.26.""", blast="good"),
            row("Ben Rice", "L", "+300", 68, "⭐ 🌕 💣", ["vs Palmquist"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.3 mph EV. Palmquist LHB split -0.06, HR risk -0.79. slight split headwind (-0.06); pitcher suppresses HR (-0.79).""", blast="high"),
            row("Austin Wells", "L", "+430", 58, "", ["vs Palmquist"], """1 HR, 1 near-HR, 86.8 mph EV. Palmquist LHB split -0.06, HR risk -0.79. slight split headwind (-0.06); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Max Schuemann", "R", "N/A", 58, "", ["vs Palmquist"], """1 HR, 2 near-HR, 78.7 mph EV. Palmquist RHB split -0.06, HR risk -0.79. slight split headwind (-0.06); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Trent Grisham", "L", "+500", 58, "", ["vs Palmquist"], """0 HR, 88.6 mph EV. Palmquist LHB split -0.06, HR risk -0.79. slight split headwind (-0.06); pitcher suppresses HR (-0.79)."""),
        ],
    },
    {
        "title": "PHI @ DET - Aaron Nola (R, PHI) vs Jack Flaherty (R, DET)",
        "description": "Tail key data: Park boost +4% (stadium -12%, weather +16%). Nola (HR risk 0.79, vs LHB +0.59, vs RHB +0.86). Flaherty (HR risk -0.55, vs LHB -0.61, vs RHB -0.26).",
        "rows": [
            row("Riley Greene", "L", "+350", 88, "⭐ 🌕 💣", ["vs Nola"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 89.4 mph EV. Nola LHB split +0.59, HR risk 0.79. park suppresses carry (-12%).""", blast="high"),
            row("Kyle Schwarber", "L", "+210", 58, "⭐", ["vs Flaherty"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.2 mph EV. Flaherty LHB split -0.61, HR risk -0.55. tough split lane (-0.61); pitcher suppresses HR (-0.55).""", blast="good"),
            row("Edmundo Sosa", "R", "N/A", 58, "", ["vs Flaherty"], """1 HR, 2 near-HR, 93.6 mph EV. Flaherty RHB split -0.26, HR risk -0.55. slight split headwind (-0.26); pitcher suppresses HR (-0.55).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ TB - Luis Castillo (R, SEA) vs Nick Martinez (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Castillo (HR risk -0.35, vs LHB -0.02, vs RHB -0.81). Martinez (HR risk -0.21, vs LHB +0.22, vs RHB -0.78).",
        "rows": [
            row("Hunter Feduccia", "L", "+463", 66, "", ["vs Castillo"], """1 HR, 3 near-HR, 95.5 mph EV. Castillo LHB split -0.02, HR risk -0.35. slight split headwind (-0.02); pitcher risk below avg (-0.35).""", blast="good"),
            row("Dominic Canzone", "L", "+156", 75, "🌕 💣", ["vs Martinez"], """2 HR, 3 near-HR, 93.6 mph EV. Martinez LHB split +0.22, HR risk -0.21. pitcher risk below avg (-0.21).""", blast="high"),
            row("Cole Young", "L", "+340", 72, "🌕 💣", ["vs Martinez"], """2 HR, 2 near-HR, 94.9 mph EV. Martinez LHB split +0.22, HR risk -0.21. pitcher risk below avg (-0.21).""", blast="high"),
            row("Mitch Garver", "R", "N/A", 58, "", ["vs Martinez"], """1 HR, 1 near-HR, 90.3 mph EV. Martinez RHB split -0.78, HR risk -0.21. tough split lane (-0.78); pitcher risk below avg (-0.21).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ SD - Shane Bieber 🧤 (R, TOR) vs JP Sears 🧤 (L, SD)",
        "description": "Tail key data: Park boost +2% (stadium -3%, weather +5%). Bieber 🧤 (HR risk 2.60, vs LHB +1.54, vs RHB +2.91). Sears 🧤 (HR risk 1.31, vs LHB +0.93, vs RHB +1.25).",
        "rows": [
            row("Manny Machado", "R", "N/A", 99, "⭐ 🌕 💣", ["vs Bieber"], """Worst Pickz Favorite. 3 HR, 5 near-HR, 96.8 mph EV. Bieber RHB split +2.91, HR risk 2.60.""", blast="high"),
            row("Fernando Tatis Jr.", "R", "N/A", 83, "", ["vs Bieber"], """0 HR, 90.7 mph EV. Bieber RHB split +2.91, HR risk 2.60. limited recent HR events."""),
            row("Luis Campusano", "R", "N/A", 92, "🌕 💣", ["vs Bieber"], """1 HR, 1 near-HR, 92.2 mph EV. Bieber RHB split +2.91, HR risk 2.60.""", blast="good"),
            row("Kazuma Okamoto", "R", "N/A", 97, "⭐ 🌕 💣", ["vs Sears"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 93.6 mph EV. Sears RHB split +1.25, HR risk 1.31.""", blast="high"),
            row("George Springer", "R", "N/A", 88, "🌕 💣", ["vs Sears"], """1 HR, 2 near-HR, 90.5 mph EV. Sears RHB split +1.25, HR risk 1.31.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-10")

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

    out = ROOT / '_games-0710.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
