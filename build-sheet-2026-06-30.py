#!/usr/bin/env python3
"""Generate games[] block for 2026-06-30 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Andy Pages (R)",
    "Brandon Lowe (L)",
    "Bryce Harper (L)",
    "Corbin Carroll (L)",
    "Esmerlyn Valdez (R)",
    "Hunter Goodman (R)",
    "Jake Bauers (L)",
    "Joc Pederson (L)",
    "Ketel Marte (S)",
    "Kyle Schwarber (L)",
    "Max Muncy (R)",
    "Nelson Velazquez (R)",
    "Nick Kurtz (L)",
    "Paul Goldschmidt (R)",
    "Rafael Devers (L)",
    "Shohei Ohtani (L)",
    "Taylor Trammell (L)",
    "Willson Contreras (R)",
    "Zach Neto (R)",
}

GEMS = {
    "Brandon Marsh (L)",
    "Bryce Eldridge (L)",
    "Cam Smith (R)",
    "Dillon Dingler (R)",
    "Drew Romo (S)",
    "Francisco Alvarez (R)",
    "Nate Eaton (R)",
    "Ty France (R)",
    "William Contreras (R)",
}

PLAYER_TEAMS = {
    "Andrew Benintendi (L)": "CWS",
    "Andrew Vaughn (R)": "MIL",
    "Andy Pages (R)": "LAD",
    "Austin Riley (R)": "ATL",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Cam Smith (R)": "HOU",
    "Casey Schmitt (R)": "SF",
    "Chase DeLauter (L)": "CLE",
    "Corbin Carroll (L)": "ARI",
    "Curtis Mead (R)": "WSH",
    "Dansby Swanson (R)": "CHC",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Donovan Walton (L)": "LAA",
    "Drew Romo (S)": "CWS",
    "Edmundo Sosa (R)": "PHI",
    "Endy Rodriguez (S)": "PIT",
    "Eric Wagaman (R)": "NYM",
    "Esmerlyn Valdez (R)": "PIT",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Gabriel Moreno (R)": "ARI",
    "Gary Sanchez (R)": "MIL",
    "Griffin Conine (L)": "MIA",
    "Heliot Ramos (R)": "SF",
    "Henry Bolte (R)": "ATH",
    "Hunter Feduccia (L)": "TB",
    "Hunter Goodman (R)": "COL",
    "Isaac Paredes (R)": "HOU",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Holliday (L)": "BAL",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Joc Pederson (L)": "TEX",
    "John Rave (L)": "KC",
    "Jordan Walker (R)": "STL",
    "Josh Bell (S)": "MIN",
    "Josh Jung (R)": "TEX",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Kerry Carpenter (L)": "DET",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Kyle Tucker (L)": "LAD",
    "Luke Raley (L)": "SEA",
    "Manny Machado (R)": "SD",
    "Masataka Yoshida (L)": "BOS",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Max Muncy (R)": "ATH",
    "Max Schuemann (R)": "NYY",
    "Michael Conforto (L)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Nate Eaton (R)": "BOS",
    "Nelson Velazquez (R)": "STL",
    "Nick Kurtz (L)": "ATH",
    "Owen Caissie (L)": "MIA",
    "Paul Goldschmidt (R)": "NYY",
    "Pete Alonso (R)": "BAL",
    "Rafael Devers (L)": "SF",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Sal Stewart (R)": "CIN",
    "Seiya Suzuki (R)": "CHC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Torkelson (R)": "DET",
    "Taylor Trammell (L)": "HOU",
    "Ty France (R)": "SD",
    "Willi Castro (S)": "COL",
    "William Contreras (R)": "MIL",
    "Willson Contreras (R)": "BOS",
    "Yohendrick Pinango (L)": "TOR",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("LAD @ ATH", "Springs"),
    ("STL @ ATL", "Liberatore"),
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
        "title": "CIN @ MIL - Rhett Lowder (R, CIN) vs Brandon Sproat (R, MIL)",
        "description": "Tail key data: Park boost +24% (stadium +10%, weather +14%). Lowder (HR risk 0.79, vs LHB +1.41, vs RHB -0.74). Sproat (HR risk -0.05, vs LHB -0.36, vs RHB +0.54).",
        "rows": [
            row("Jake Bauers", "L", "+350", 80, "⭐", ["vs Lowder"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.1 mph EV. Lowder LHB split +1.41, HR risk 0.79.""", blast="good"),
            row("Jackson Chourio", "R", "+376", 71, "", ["vs Lowder"], """0 HR, 1 near-HR, 93.4 mph EV. Lowder RHB split -0.74, HR risk 0.79. tough split lane (-0.74); limited recent HR events.""", blast="good"),
            row("William Contreras", "R", "+470", 90, "🌕 💣 💎", ["vs Lowder"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 98.3 mph EV. Lowder RHB split -0.74, HR risk 0.79. tough split lane (-0.74).""", blast="high"),
            row("Gary Sanchez", "R", "N/A", 76, "", ["vs Lowder"], """1 HR, 1 near-HR, 94.1 mph EV. Lowder RHB split -0.74, HR risk 0.79. tough split lane (-0.74).""", blast="good"),
            row("Andrew Vaughn", "R", "N/A", 65, "", ["vs Lowder"], """0 HR, 91.1 mph EV. Lowder RHB split -0.74, HR risk 0.79. tough split lane (-0.74); limited recent HR events."""),
            row("Matt McLain", "R", "+750", 73, "", ["vs Sproat"], """0 HR, 97.2 mph EV. Sproat RHB split +0.54, HR risk -0.05. pitcher risk below avg (-0.05); limited recent HR events.""", blast="good"),
            row("Sal Stewart", "R", "+420", 79, "🌕 💣", ["vs Sproat"], """1 HR, 4 near-HR, 89.4 mph EV. Sproat RHB split +0.54, HR risk -0.05. pitcher risk below avg (-0.05).""", blast="high"),
            row("JJ Bleday", "L", "+400", 62, "", ["vs Sproat"], """0 HR, 86.0 mph EV. Sproat LHB split -0.36, HR risk -0.05. slight split headwind (-0.36); pitcher risk below avg (-0.05)."""),
        ],
    },
    {
        "title": "CWS @ BAL - Erick Fedde (R, CWS) vs Trey Gibson (R, BAL)",
        "description": "Tail key data: Park boost data unavailable. Fedde (HR risk -0.74, vs LHB -0.46, vs RHB -0.46). Gibson (HR risk -0.01, vs LHB -0.12, vs RHB +0.34).",
        "rows": [
            row("Pete Alonso", "R", "+320", 72, "", ["vs Fedde"], """1 HR, 2 near-HR, 85.6 mph EV. Fedde RHB split -0.46, HR risk -0.74. tough split lane (-0.46); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Jackson Holliday", "L", "+630", 72, "", ["vs Fedde"], """1 HR, 1 near-HR, 89.9 mph EV. Fedde LHB split -0.46, HR risk -0.74. tough split lane (-0.46); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Drew Romo", "S", "N/A", 62, "💎", ["vs Gibson"], """Worst Pickz Hidden Gem. 0 HR, 83.1 mph EV. Gibson RHB split +0.34, HR risk -0.01. pitcher risk below avg (-0.01); limited recent HR events."""),
            row("Miguel Vargas", "R", "+370", 80, "🌕 💣", ["vs Gibson"], """2 HR, 3 near-HR, 88.3 mph EV. Gibson RHB split +0.34, HR risk -0.01. pitcher risk below avg (-0.01).""", blast="high"),
            row("Andrew Benintendi", "L", "+485", 82, "🌕 💣", ["vs Gibson"], """2 HR, 2 near-HR, 92.5 mph EV. Gibson LHB split -0.12, HR risk -0.01. slight split headwind (-0.12); pitcher risk below avg (-0.01).""", blast="high"),
        ],
    },
    {
        "title": "DET @ NYY - Tarik Skubal (L, DET) vs Cam Schlittler (R, NYY)",
        "description": "Tail key data: Park boost +13% (stadium +5%, weather +7%). Skubal (HR risk 0.20, vs LHB -0.08, vs RHB +0.44). Schlittler (HR risk -0.97, vs LHB -0.85, vs RHB -0.33).",
        "rows": [
            row("Paul Goldschmidt", "R", "+500", 81, "⭐ 🌕 💣", ["vs Skubal"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.4 mph EV. Skubal RHB split +0.44, HR risk 0.20.""", blast="high"),
            row("Max Schuemann", "R", "+960", 76, "", ["vs Skubal"], """1 HR, 1 near-HR, 94.3 mph EV. Skubal RHB split +0.44, HR risk 0.20.""", blast="good"),
            row("Dillon Dingler", "R", "+489", 90, "🌕 💣 💎", ["vs Schlittler"], """Worst Pickz Hidden Gem. 3 HR, 4 near-HR, 92.2 mph EV. Schlittler RHB split -0.33, HR risk -0.97. slight split headwind (-0.33); pitcher suppresses HR (-0.97).""", blast="high"),
            row("Kerry Carpenter", "L", "+360", 83, "🌕 💣", ["vs Schlittler"], """2 HR, 3 near-HR, 91.4 mph EV. Schlittler LHB split -0.85, HR risk -0.97. tough split lane (-0.85); pitcher suppresses HR (-0.97).""", blast="high"),
            row("Spencer Torkelson", "R", "+470", 73, "", ["vs Schlittler"], """1 HR, 1 near-HR, 90.6 mph EV. Schlittler RHB split -0.33, HR risk -0.97. slight split headwind (-0.33); pitcher suppresses HR (-0.97).""", blast="good"),
            row("Riley Greene", "L", "+360", 66, "", ["vs Schlittler"], """0 HR, 91.6 mph EV. Schlittler LHB split -0.85, HR risk -0.97. tough split lane (-0.85); pitcher suppresses HR (-0.97)."""),
        ],
    },
    {
        "title": "LAA @ SEA - Jose Soriano (R, LAA) vs Bryan Woo (R, SEA)",
        "description": "Tail key data: Park boost +3% (stadium +1%, weather +2%). Soriano (HR risk 0.42, vs LHB +1.01, vs RHB -1.11). Woo (HR risk -0.33, vs LHB -0.07, vs RHB -0.34).",
        "rows": [
            row("Julio Rodriguez", "R", "+400", 85, "🌕 💣", ["vs Soriano"], """2 HR, 4 near-HR, 90.7 mph EV. Soriano RHB split -1.11, HR risk 0.42. tough split lane (-1.11).""", blast="high"),
            row("Dominic Canzone", "L", "+360", 91, "🌕 💣", ["vs Soriano"], """2 HR, 5 near-HR, 95.4 mph EV. Soriano LHB split +1.01, HR risk 0.42.""", blast="high"),
            row("Luke Raley", "L", "+540", 75, "", ["vs Soriano"], """0 HR, 2 near-HR, 94.8 mph EV. Soriano LHB split +1.01, HR risk 0.42.""", blast="good"),
            row("Zach Neto", "R", "+479", 91, "⭐ 🌕 💣", ["vs Woo"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 93.1 mph EV. Woo RHB split -0.34, HR risk -0.33. slight split headwind (-0.34); pitcher risk below avg (-0.33).""", blast="high"),
            row("Donovan Walton", "L", "+1140", 79, "🌕 💣", ["vs Woo"], """2 HR, 2 near-HR, 88.9 mph EV. Woo LHB split -0.07, HR risk -0.33. slight split headwind (-0.07); pitcher risk below avg (-0.33).""", blast="high"),
        ],
    },
    {
        "title": "LAD @ ATH - Justin Wrobleski (L, LAD) vs Jeffrey Springs 🧤 (L, ATH)",
        "description": "Tail key data: Park boost +39% (stadium +32%, weather +8%). Wrobleski (HR risk -0.20, vs LHB +0.52, vs RHB -0.28). Springs 🧤 (HR risk 1.45, vs LHB +0.36, vs RHB +1.45).",
        "rows": [
            row("Nick Kurtz", "L", "+270", 83, "⭐", ["vs Wrobleski"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 98.8 mph EV. Wrobleski LHB split +0.52, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="good"),
            row("Henry Bolte", "R", "+500", 76, "", ["vs Wrobleski"], """1 HR, 1 near-HR, 94.1 mph EV. Wrobleski RHB split -0.28, HR risk -0.20. slight split headwind (-0.28); pitcher risk below avg (-0.20).""", blast="good"),
            row("Shohei Ohtani", "L", "+215", 82, "⭐", ["vs Springs"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.6 mph EV. Springs LHB split +0.36, HR risk 1.45.""", blast="good"),
            row("Andy Pages", "R", "+352", 80, "⭐", ["vs Springs"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.6 mph EV. Springs RHB split +1.45, HR risk 1.45.""", blast="good"),
            row("Max Muncy", "R", "N/A", 62, "⭐", ["vs Wrobleski"], """Worst Pickz Favorite. 0 HR, 77.3 mph EV. Wrobleski RHB split -0.28, HR risk -0.20. slight split headwind (-0.28); pitcher risk below avg (-0.20)."""),
            row("Kyle Tucker", "L", "+464", 70, "", ["vs Springs"], """0 HR, 94.5 mph EV. Springs LHB split +0.36, HR risk 1.45. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ COL - Eury Perez (R, MIA) vs Tanner Gordon (R, COL)",
        "description": "Tail key data: Park boost +31% (stadium +21%, weather +10%). Perez (HR risk 0.88, vs LHB +0.13, vs RHB +1.60). Gordon (HR risk 0.06, vs LHB +0.95, vs RHB -0.59).",
        "rows": [
            row("Hunter Goodman", "R", "+220", 93, "⭐ 🌕 💣", ["vs Perez"], """Worst Pickz Favorite. 3 HR, 5 near-HR, 93.0 mph EV. Perez split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Willi Castro", "S", "+500", 72, "", ["vs Perez"], """0 HR, 96.0 mph EV. Perez split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Griffin Conine", "L", "+326", 72, "", ["vs Gordon"], """1 HR, 1 near-HR, 89.9 mph EV. Gordon LHB split +0.95, HR risk 0.06.""", blast="good"),
            row("Kyle Stowers", "L", "+285", 64, "", ["vs Gordon"], """0 HR, 1 near-HR, 85.8 mph EV. Gordon LHB split +0.95, HR risk 0.06. limited recent HR events; lighter EV form (85.8 mph)."""),
            row("Owen Caissie", "L", "+390", 74, "", ["vs Gordon"], """1 HR, 3 near-HR, 82.7 mph EV. Gordon LHB split +0.95, HR risk 0.06. lighter EV form (82.7 mph).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ HOU - Joe Ryan (R, MIN) vs Mike Burrows (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +0%). Ryan (HR risk 0.28, vs LHB +0.37, vs RHB +0.16). Burrows (HR risk 0.58, vs LHB +0.83, vs RHB -0.01).",
        "rows": [
            row("Yordan Alvarez", "L", "+240", 73, "", ["vs Ryan"], """0 HR, 2 near-HR, 92.9 mph EV. Ryan LHB split +0.37, HR risk 0.28.""", blast="good"),
            row("Taylor Trammell", "L", "+600", 90, "⭐ 🌕 💣", ["vs Ryan"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 97.7 mph EV. Ryan LHB split +0.37, HR risk 0.28.""", blast="high"),
            row("Cam Smith", "R", "+700", 87, "🌕 💣 💎", ["vs Ryan"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 90.6 mph EV. Ryan RHB split +0.16, HR risk 0.28.""", blast="high"),
            row("Isaac Paredes", "R", "+540", 70, "", ["vs Ryan"], """1 HR, 1 near-HR, 88.1 mph EV. Ryan RHB split +0.16, HR risk 0.28.""", blast="good"),
            row("Kody Clemens", "L", "+310", 79, "", ["vs Burrows"], """1 HR, 3 near-HR, 92.6 mph EV. Burrows LHB split +0.83, HR risk 0.58.""", blast="good"),
            row("Josh Bell", "S", "+496", 84, "🌕 💣", ["vs Burrows"], """2 HR, 3 near-HR, 92.0 mph EV. Burrows RHB split -0.01, HR risk 0.58. slight split headwind (-0.01).""", blast="high"),
            row("Byron Buxton", "R", "+230", 81, "🌕 💣", ["vs Burrows"], """2 HR, 3 near-HR, 89.3 mph EV. Burrows RHB split -0.01, HR risk 0.58. slight split headwind (-0.01).""", blast="high"),
        ],
    },
    {
        "title": "NYM @ TOR - Nolan McLean (R, NYM) vs Kevin Gausman (R, TOR)",
        "description": "Tail key data: Park boost +2% (stadium +7%, weather -4%). McLean (HR risk -0.97, vs LHB -0.66, vs RHB -0.62). Gausman (HR risk 0.60, vs LHB -0.04, vs RHB +1.28).",
        "rows": [
            row("Yohendrick Pinango", "L", "+800", 62, "", ["vs McLean"], """0 HR, 87.8 mph EV. McLean LHB split -0.66, HR risk -0.97. tough split lane (-0.66); pitcher suppresses HR (-0.97)."""),
            row("Francisco Lindor", "S", "+415", 96, "🚀 🌕 💣", ["vs Gausman"], """3 HR, 3 near-HR, 100.1 mph EV. Gausman RHB split +1.28, HR risk 0.60. weather carry headwind (-4%).""", blast="high"),
            row("Eric Wagaman", "R", "N/A", 62, "", ["vs Gausman"], """0 HR, 0.0 mph EV. Gausman RHB split +1.28, HR risk 0.60. weather carry headwind (-4%); limited recent HR events."""),
            row("Francisco Alvarez", "R", "+650", 75, "💎", ["vs Gausman"], """Worst Pickz Hidden Gem. 0 HR, 98.6 mph EV. Gausman RHB split +1.28, HR risk 0.60. weather carry headwind (-4%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "PIT @ PHI - Bubba Chandler (R, PIT) vs Cristopher Sanchez (L, PHI)",
        "description": "Tail key data: Park boost +26% (stadium +14%, weather +11%). Chandler (HR risk -0.88, vs LHB -0.02, vs RHB -1.23). Sanchez (HR risk -0.36, vs LHB -1.41, vs RHB +0.22).",
        "rows": [
            row("Bryce Harper", "L", "+300", 98, "⭐ 🌕 💣", ["vs Chandler"], """Worst Pickz Favorite. 4 HR, 4 near-HR, 99.8 mph EV. Chandler LHB split -0.02, HR risk -0.88. slight split headwind (-0.02); pitcher suppresses HR (-0.88).""", blast="high"),
            row("Kyle Schwarber", "L", "+180", 96, "🚀 ⭐ 🌕 💣", ["vs Chandler"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 101.0 mph EV. Chandler LHB split -0.02, HR risk -0.88. slight split headwind (-0.02); pitcher suppresses HR (-0.88).""", blast="high"),
            row("Brandon Marsh", "L", "+492", 79, "🌕 💣 💎", ["vs Chandler"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 89.0 mph EV. Chandler LHB split -0.02, HR risk -0.88. slight split headwind (-0.02); pitcher suppresses HR (-0.88).""", blast="high"),
            row("Edmundo Sosa", "R", "N/A", 72, "", ["vs Chandler"], """1 HR, 2 near-HR, 87.5 mph EV. Chandler RHB split -1.23, HR risk -0.88. tough split lane (-1.23); pitcher suppresses HR (-0.88).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+560", 82, "🚀 ⭐", ["vs Sanchez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 104.8 mph EV. Sanchez RHB split +0.22, HR risk -0.36. pitcher risk below avg (-0.36).""", blast="good"),
            row("Brandon Lowe", "L", "+600", 80, "⭐", ["vs Sanchez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.8 mph EV. Sanchez LHB split -1.41, HR risk -0.36. tough split lane (-1.41); pitcher risk below avg (-0.36).""", blast="good"),
            row("Bryan Reynolds", "S", "+830", 72, "", ["vs Sanchez"], """1 HR, 2 near-HR, 86.4 mph EV. Sanchez RHB split +0.22, HR risk -0.36. pitcher risk below avg (-0.36); lighter EV form (86.4 mph).""", blast="good"),
            row("Endy Rodriguez", "S", "N/A", 62, "", ["vs Sanchez"], """0 HR, 85.5 mph EV. Sanchez RHB split +0.22, HR risk -0.36. pitcher risk below avg (-0.36); limited recent HR events."""),
        ],
    },
    {
        "title": "SD @ CHC - JP Sears (L, SD) vs Matthew Boyd (L, CHC)",
        "description": "Tail key data: Park boost +49% (stadium -1%, weather +50%). Sears (HR risk 0.68, vs LHB -0.43, vs RHB +1.08). Boyd (HR risk -0.81, vs LHB -1.25, vs RHB -0.27).",
        "rows": [
            row("Michael Conforto", "L", "+248", 76, "🚀", ["vs Sears"], """0 HR, 105.9 mph EV. Sears LHB split -0.43, HR risk 0.68. tough split lane (-0.43); limited recent HR events.""", blast="good"),
            row("Seiya Suzuki", "R", "+245", 79, "", ["vs Sears"], """1 HR, 2 near-HR, 94.7 mph EV. Sears RHB split +1.08, HR risk 0.68.""", blast="good"),
            row("Dansby Swanson", "R", "+344", 70, "", ["vs Sears"], """1 HR, 1 near-HR, 85.4 mph EV. Sears RHB split +1.08, HR risk 0.68. lighter EV form (85.4 mph).""", blast="good"),
            row("Ty France", "R", "+340", 79, "💎", ["vs Boyd"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.9 mph EV. Boyd RHB split -0.27, HR risk -0.81. slight split headwind (-0.27); pitcher suppresses HR (-0.81).""", blast="good"),
            row("Manny Machado", "R", "+224", 67, "", ["vs Boyd"], """0 HR, 1 near-HR, 91.3 mph EV. Boyd RHB split -0.27, HR risk -0.81. slight split headwind (-0.27); pitcher suppresses HR (-0.81)."""),
        ],
    },
    {
        "title": "SF @ ARI - Landen Roupp (R, SF) vs Brandon Pfaadt (R, ARI)",
        "description": "Tail key data: Park boost -9% (stadium -9%, weather +0%). Roupp (HR risk -1.28, vs LHB -0.64, vs RHB -1.26). Home starter risk unavailable.",
        "rows": [
            row("Corbin Carroll", "L", "+560", 65, "⭐", ["vs Roupp"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 89.2 mph EV. Roupp LHB split -0.64, HR risk -1.28. tough split lane (-0.64); pitcher suppresses HR (-1.28)."""),
            row("Ketel Marte", "S", "+480", 72, "⭐", ["vs Roupp"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 90.5 mph EV. Roupp RHB split -1.26, HR risk -1.28. tough split lane (-1.26); pitcher suppresses HR (-1.28).""", blast="good"),
            row("Gabriel Moreno", "R", "+1050", 65, "", ["vs Roupp"], """0 HR, 90.7 mph EV. Roupp RHB split -1.26, HR risk -1.28. tough split lane (-1.26); pitcher suppresses HR (-1.28)."""),
            row("Max Kepler", "L", "+800", 64, "", ["vs Roupp"], """0 HR, 1 near-HR, 83.5 mph EV. Roupp LHB split -0.64, HR risk -1.28. tough split lane (-0.64); pitcher suppresses HR (-1.28)."""),
            row("Bryce Eldridge", "L", "+600", 83, "💎", ["vs Pfaadt"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 97.0 mph EV. Pfaadt split/risk data unavailable. limited split/risk sample; park/weather net drag (-9%).""", blast="good"),
            row("Rafael Devers", "L", "+400", 88, "⭐ 🌕 💣", ["vs Pfaadt"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.5 mph EV. Pfaadt split/risk data unavailable. limited split/risk sample; park/weather net drag (-9%).""", blast="high"),
            row("Heliot Ramos", "R", "+650", 74, "", ["vs Pfaadt"], """1 HR, 1 near-HR, 91.8 mph EV. Pfaadt split/risk data unavailable. limited split/risk sample; park/weather net drag (-9%).""", blast="good"),
            row("Casey Schmitt", "R", "+500", 79, "", ["vs Pfaadt"], """1 HR, 3 near-HR, 92.9 mph EV. Pfaadt split/risk data unavailable. limited split/risk sample; park/weather net drag (-9%).""", blast="good"),
        ],
    },
    {
        "title": "STL @ ATL - Matthew Liberatore 🧤 (L, STL) vs Martin Perez (L, ATL)",
        "description": "Tail key data: Park boost +1% (stadium -5%, weather +5%). Liberatore 🧤 (HR risk 1.04, vs LHB +0.33, vs RHB +1.15). Perez (HR risk -0.91, vs LHB -0.38, vs RHB -0.73).",
        "rows": [
            row("Austin Riley", "R", "+463", 73, "", ["vs Liberatore"], """0 HR, 97.4 mph EV. Liberatore RHB split +1.15, HR risk 1.04. limited recent HR events.""", blast="good"),
            row("Matt Olson", "L", "+375", 63, "", ["vs Liberatore"], """0 HR, 89.4 mph EV. Liberatore LHB split +0.33, HR risk 1.04. limited recent HR events."""),
            row("Nelson Velazquez", "R", "+482", 78, "⭐", ["vs Perez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.5 mph EV. Perez split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Jordan Walker", "R", "+340", 79, "", ["vs Perez"], """1 HR, 1 near-HR, 96.7 mph EV. Perez split/risk data unavailable. limited split/risk sample.""", blast="good"),
        ],
    },
    {
        "title": "TB @ KC - Griffin Jax (R, TB) vs Noah Cameron (L, KC)",
        "description": "Tail key data: Park boost +38% (stadium +10%, weather +28%). Jax (HR risk 0.74, vs LHB +0.78, vs RHB +0.22). Cameron (HR risk -0.82, vs LHB -0.09, vs RHB -0.66).",
        "rows": [
            row("John Rave", "L", "+650", 72, "", ["vs Jax"], """1 HR, 2 near-HR, 86.0 mph EV. Jax LHB split +0.78, HR risk 0.74. lighter EV form (86.0 mph).""", blast="good"),
            row("Jac Caglianone", "L", "+355", 95, "🌕 💣", ["vs Jax"], """3 HR, 3 near-HR, 99.0 mph EV. Jax LHB split +0.78, HR risk 0.74.""", blast="high"),
            row("Junior Caminero", "R", "+268", 72, "", ["vs Cameron"], """0 HR, 95.9 mph EV. Cameron RHB split -0.66, HR risk -0.82. tough split lane (-0.66); pitcher suppresses HR (-0.82).""", blast="good"),
            row("Hunter Feduccia", "L", "N/A", 70, "", ["vs Cameron"], """0 HR, 94.0 mph EV. Cameron LHB split -0.09, HR risk -0.82. slight split headwind (-0.09); pitcher suppresses HR (-0.82).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ CLE - Jacob deGrom (R, TEX) vs Tanner Bibee (R, CLE)",
        "description": "Tail key data: Park boost +16% (stadium -1%, weather +17%). deGrom (HR risk -0.46, vs LHB -0.58, vs RHB +0.14). Bibee (HR risk 0.03, vs LHB +0.12, vs RHB +0.03).",
        "rows": [
            row("Rhys Hoskins", "R", "+504", 79, "", ["vs deGrom"], """1 HR, 1 near-HR, 97.2 mph EV. deGrom RHB split +0.14, HR risk -0.46. pitcher suppresses HR (-0.46).""", blast="good"),
            row("Chase DeLauter", "L", "+508", 72, "", ["vs deGrom"], """0 HR, 96.0 mph EV. deGrom LHB split -0.58, HR risk -0.46. tough split lane (-0.58); pitcher suppresses HR (-0.46).""", blast="good"),
            row("Joc Pederson", "L", "+348", 98, "⭐ 🌕 💣", ["vs Bibee"], """Worst Pickz Favorite. 4 HR, 5 near-HR, 96.2 mph EV. Bibee LHB split +0.12, HR risk 0.03.""", blast="high"),
            row("Josh Jung", "R", "+560", 75, "", ["vs Bibee"], """0 HR, 1 near-HR, 97.2 mph EV. Bibee RHB split +0.03, HR risk 0.03. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "WSH @ BOS - Cade Cavalli (R, WSH) vs Connelly Early (L, BOS)",
        "description": "Tail key data: Park boost data unavailable. Cavalli (HR risk -0.40, vs LHB -0.19, vs RHB -0.44). Early (HR risk 0.18, vs LHB -0.78, vs RHB +0.80).",
        "rows": [
            row("Nate Eaton", "R", "N/A", 77, "💎", ["vs Cavalli"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.1 mph EV. Cavalli RHB split -0.44, HR risk -0.40. tough split lane (-0.44); pitcher suppresses HR (-0.40).""", blast="good"),
            row("Willson Contreras", "R", "+498", 87, "⭐ 🌕 💣", ["vs Cavalli"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.9 mph EV. Cavalli RHB split -0.44, HR risk -0.40. tough split lane (-0.44); pitcher suppresses HR (-0.40).""", blast="high"),
            row("Masataka Yoshida", "L", "+900", 70, "", ["vs Cavalli"], """1 HR, 1 near-HR, 88.5 mph EV. Cavalli LHB split -0.19, HR risk -0.40. slight split headwind (-0.19); pitcher suppresses HR (-0.40).""", blast="good"),
            row("James Wood", "L", "+360", 74, "", ["vs Early"], """1 HR, 1 near-HR, 92.5 mph EV. Early LHB split -0.78, HR risk 0.18. tough split lane (-0.78).""", blast="good"),
            row("Curtis Mead", "R", "+495", 72, "", ["vs Early"], """1 HR, 2 near-HR, 86.6 mph EV. Early RHB split +0.80, HR risk 0.18. lighter EV form (86.6 mph).""", blast="good"),
            row("CJ Abrams", "L", "+578", 64, "", ["vs Early"], """0 HR, 89.5 mph EV. Early LHB split -0.78, HR risk 0.18. tough split lane (-0.78); limited recent HR events."""),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-30")

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

    out = ROOT / '_games-0630.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
