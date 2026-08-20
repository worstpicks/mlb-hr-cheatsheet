#!/usr/bin/env python3
"""Generate games[] block for 2026-08-20 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Andrew Benintendi (L)",
    "Austin Riley (R)",
    "Bryce Eldridge (L)",
    "Corey Seager (L)",
    "Jac Caglianone (L)",
    "Kazuma Okamoto (R)",
    "Lane Thomas (R)",
    "Matt Olson (L)",
    "Miguel Vargas (R)",
    "Munetaka Murakami (L)",
    "Pete Alonso (R)",
    "Taylor Trammell (L)",
    "Vinnie Pasquantino (L)",
    "William Contreras (R)",
}

GEMS = {
    "Abimelec Ortiz (L)",
    "Coby Mayo (R)",
    "Gunnar Henderson (L)",
    "JJ Bleday (L)",
    "Jackson Chourio (R)",
    "Jazz Chisholm Jr. (L)",
    "Jimmy Crooks (L)",
    "Jonny DeLuca (R)",
    "Nathaniel Lowe (L)",
    "Ronald Acuna Jr. (R)",
    "Salvador Perez (R)",
    "Yandy Diaz (R)",
}

PLAYER_TEAMS = {
    "Abimelec Ortiz (L)": "WSH",
    "Alec Burleson (L)": "STL",
    "Amed Rosario (R)": "NYY",
    "Andrew Benintendi (L)": "CWS",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Brady House (R)": "WSH",
    "Brian Serven (R)": "ATH",
    "Bryce Eldridge (L)": "SF",
    "Cal Raleigh (S)": "SEA",
    "Cam Smith (R)": "HOU",
    "Coby Mayo (R)": "BAL",
    "Colton Cowser (L)": "BAL",
    "Corey Seager (L)": "TEX",
    "Daulton Varsho (L)": "HOU",
    "Daz Cameron (R)": "TOR",
    "Elly De La Cruz (S)": "CIN",
    "Eugenio Suarez (R)": "CIN",
    "Garrett Mitchell (L)": "MIL",
    "Gunnar Henderson (L)": "BAL",
    "Ivan Herrera (R)": "STL",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jarred Kelenic (L)": "TEX",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jeff McNeil (L)": "ATH",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "CLE",
    "Jonathan Aranda (L)": "TB",
    "Jonny DeLuca (R)": "TB",
    "Jorge Mateo (R)": "TB",
    "Julio Rodriguez (R)": "SEA",
    "Jung Hoo Lee (L)": "SF",
    "Kazuma Okamoto (R)": "TOR",
    "Lane Thomas (R)": "ATL",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Michael Toglia (S)": "CIN",
    "Miguel Vargas (R)": "CWS",
    "Munetaka Murakami (L)": "CWS",
    "Nathaniel Lowe (L)": "CLE",
    "Nelson Velazquez (R)": "HOU",
    "Pete Alonso (R)": "BAL",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Randy Arozarena (R)": "SEA",
    "Ronald Acuna Jr. (R)": "ATL",
    "Salvador Perez (R)": "KC",
    "Samuel Basallo (L)": "BAL",
    "Taylor Trammell (L)": "HOU",
    "Travis d'Arnaud (R)": "LAA",
    "Trent Grisham (L)": "NYY",
    "Tyler O'Neill (R)": "BAL",
    "Tyler Stephenson (R)": "CIN",
    "Vinnie Pasquantino (L)": "KC",
    "Weston Wilson (R)": "SEA",
    "William Contreras (R)": "MIL",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("LAA @ HOU", "Rodriguez"),
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
        "title": "ATH @ KC - Gage Jump (L, ATH) vs Randy Dobnak (R, KC)",
        "description": "Tail key data: Park boost +18% (stadium +10%, weather +8%). Jump (HR risk -0.08, vs LHB -0.04, vs RHB +0.08). Dobnak (HR risk -1.68, vs LHB -1.18, vs RHB -1.51).",
        "rows": [
            row("Jac Caglianone", "L", "+300", 82, "⭐ 🌕 💣", ["vs Jump"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 97.8 mph EV. Jump LHB split -0.04, HR risk -0.08. slight split headwind (-0.04); pitcher risk below avg (-0.08).""", blast="high"),
            row("Salvador Perez", "R", "+531", 58, "💎", ["vs Jump"], """Worst Pickz Hidden Gem. 0 HR, 91.1 mph EV. Jump RHB split +0.08, HR risk -0.08. pitcher risk below avg (-0.08); limited recent HR events."""),
            row("Vinnie Pasquantino", "L", "+870", 64, "⭐", ["vs Jump"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 90.8 mph EV. Jump LHB split -0.04, HR risk -0.08. slight split headwind (-0.04); pitcher risk below avg (-0.08).""", blast="good"),
            row("Jeff McNeil", "L", "+900", 58, "🌕 💣", ["vs Dobnak"], """2 HR, 2 near-HR, 95.1 mph EV. Dobnak LHB split -1.18, HR risk -1.68. tough split lane (-1.18); pitcher suppresses HR (-1.68).""", blast="high"),
            row("Zack Gelof", "R", "+630", 58, "", ["vs Dobnak"], """1 HR, 2 near-HR, 90.1 mph EV. Dobnak RHB split -1.51, HR risk -1.68. tough split lane (-1.51); pitcher suppresses HR (-1.68).""", blast="good"),
            row("Brian Serven", "R", "+869", 58, "", ["vs Dobnak"], """1 HR, 1 near-HR, 91.2 mph EV. Dobnak RHB split -1.51, HR risk -1.68. tough split lane (-1.51); pitcher suppresses HR (-1.68).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ CWS - Grant Holmes (R, ATL) vs Anthony Kay (L, CWS)",
        "description": "Tail key data: Park boost -9% (stadium -5%, weather -4%). Holmes (HR risk 0.73, vs LHB +0.69, vs RHB +0.54). Kay (HR risk -0.07, vs LHB -1.41, vs RHB +0.75).",
        "rows": [
            row("Munetaka Murakami", "L", "+272", 87, "⭐ 🌕 💣", ["vs Holmes"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.1 mph EV. Holmes LHB split +0.69, HR risk 0.73. park/weather net drag (-9%).""", blast="high"),
            row("Miguel Vargas", "R", "+369", 84, "⭐ 🌕 💣", ["vs Holmes"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.6 mph EV. Holmes RHB split +0.54, HR risk 0.73. park/weather net drag (-9%).""", blast="high"),
            row("Andrew Benintendi", "L", "+500", 74, "⭐", ["vs Holmes"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.3 mph EV. Holmes LHB split +0.69, HR risk 0.73. park/weather net drag (-9%).""", blast="good"),
            row("Randal Grichuk", "R", "N/A", 71, "", ["vs Holmes"], """0 HR, 97.9 mph EV. Holmes RHB split +0.54, HR risk 0.73. park/weather net drag (-9%); limited recent HR events.""", blast="good"),
            row("Lane Thomas", "R", "+640", 79, "⭐ 🌕 💣", ["vs Kay"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 92.9 mph EV. Kay RHB split +0.75, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-9%).""", blast="high"),
            row("Ronald Acuna Jr.", "R", "+420", 79, "🌕 💣 💎", ["vs Kay"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 90.1 mph EV. Kay RHB split +0.75, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-9%).""", blast="high"),
            row("Matt Olson", "L", "+340", 58, "⭐", ["vs Kay"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.0 mph EV. Kay LHB split -1.41, HR risk -0.07. tough split lane (-1.41); pitcher risk below avg (-0.07).""", blast="good"),
            row("Austin Riley", "R", "+481", 64, "⭐", ["vs Kay"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 98.2 mph EV. Kay RHB split +0.75, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-9%).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ HOU - Grayson Rodriguez 🧤 (R, LAA) vs Peter Lambert (R, HOU)",
        "description": "Tail key data: Park boost +6% (stadium +7%, weather +0%). Rodriguez 🧤 (HR risk 1.21, vs LHB +0.46, vs RHB +1.70). Lambert (HR risk -0.68, vs LHB -0.49, vs RHB -0.54).",
        "rows": [
            row("Taylor Trammell", "L", "+584", 94, "🚀 ⭐ 🌕 💣", ["vs Rodriguez"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 100.7 mph EV. Rodriguez LHB split +0.46, HR risk 1.21.""", blast="high"),
            row("Cam Smith", "R", "+574", 94, "🌕 💣", ["vs Rodriguez"], """2 HR, 2 near-HR, 92.1 mph EV. Rodriguez RHB split +1.70, HR risk 1.21.""", blast="high"),
            row("Yordan Alvarez", "L", "+240", 84, "", ["vs Rodriguez"], """1 HR, 1 near-HR, 94.7 mph EV. Rodriguez LHB split +0.46, HR risk 1.21.""", blast="good"),
            row("Daulton Varsho", "L", "+500", 77, "", ["vs Rodriguez"], """0 HR, 92.8 mph EV. Rodriguez LHB split +0.46, HR risk 1.21. limited recent HR events.""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 83, "", ["vs Rodriguez"], """0 HR, 1 near-HR, 91.6 mph EV. Rodriguez RHB split +1.70, HR risk 1.21. limited recent HR events."""),
            row("Travis d'Arnaud", "R", "N/A", 58, "", ["vs Lambert"], """0 HR, 90.5 mph EV. Lambert RHB split -0.54, HR risk -0.68. tough split lane (-0.54); pitcher suppresses HR (-0.68)."""),
        ],
    },
    {
        "title": "NYY @ BAL - Gerrit Cole (R, NYY) vs Kyle Bradish (R, BAL)",
        "description": "Tail key data: Park boost -1% (stadium +0%, weather -1%). Cole (HR risk -0.33, vs LHB -0.34, vs RHB -0.06). Bradish (HR risk -0.86, vs LHB -0.97, vs RHB -0.08).",
        "rows": [
            row("Pete Alonso", "R", "+345", 78, "🚀 ⭐ 🌕 💣", ["vs Cole"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 103.6 mph EV. Cole RHB split -0.06, HR risk -0.33. slight split headwind (-0.06); pitcher risk below avg (-0.33).""", blast="high"),
            row("Gunnar Henderson", "L", "+491", 60, "💎", ["vs Cole"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 96.2 mph EV. Cole LHB split -0.34, HR risk -0.33. slight split headwind (-0.34); pitcher risk below avg (-0.33).""", blast="good"),
            row("Coby Mayo", "R", "+475", 58, "💎", ["vs Cole"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 91.9 mph EV. Cole RHB split -0.06, HR risk -0.33. slight split headwind (-0.06); pitcher risk below avg (-0.33).""", blast="good"),
            row("Tyler O'Neill", "R", "+391", 58, "", ["vs Cole"], """0 HR, 1 near-HR, 89.1 mph EV. Cole RHB split -0.06, HR risk -0.33. slight split headwind (-0.06); pitcher risk below avg (-0.33)."""),
            row("Colton Cowser", "L", "+640", 58, "", ["vs Cole"], """1 HR, 2 near-HR, 92.1 mph EV. Cole LHB split -0.34, HR risk -0.33. slight split headwind (-0.34); pitcher risk below avg (-0.33).""", blast="good"),
            row("Samuel Basallo", "L", "+450", 71, "🌕 💣", ["vs Cole"], """2 HR, 3 near-HR, 94.8 mph EV. Cole LHB split -0.34, HR risk -0.33. slight split headwind (-0.34); pitcher risk below avg (-0.33).""", blast="high"),
            row("Ben Rice", "L", "+340", 59, "🌕 💣", ["vs Bradish"], """2 HR, 2 near-HR, 93.7 mph EV. Bradish LHB split -0.97, HR risk -0.86. tough split lane (-0.97); pitcher suppresses HR (-0.86).""", blast="high"),
            row("Jazz Chisholm Jr.", "L", "+504", 58, "💎", ["vs Bradish"], """Worst Pickz Hidden Gem. 0 HR, 90.4 mph EV. Bradish LHB split -0.97, HR risk -0.86. tough split lane (-0.97); pitcher suppresses HR (-0.86)."""),
            row("Trent Grisham", "L", "+430", 69, "🌕 💣", ["vs Bradish"], """3 HR, 3 near-HR, 96.6 mph EV. Bradish LHB split -0.97, HR risk -0.86. tough split lane (-0.97); pitcher suppresses HR (-0.86).""", blast="high"),
            row("Amed Rosario", "R", "N/A", 58, "", ["vs Bradish"], """1 HR, 1 near-HR, 93.5 mph EV. Bradish RHB split -0.08, HR risk -0.86. slight split headwind (-0.08); pitcher suppresses HR (-0.86).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ MIL - George Kirby (R, SEA) vs Robert Gasser (L, MIL)",
        "description": "Tail key data: Park boost -2% (stadium -1%, weather +0%). Kirby (HR risk 0.50, vs LHB +0.96, vs RHB +0.02). Gasser (HR risk 0.55, vs LHB -0.44, vs RHB +0.85).",
        "rows": [
            row("Garrett Mitchell", "L", "+550", 73, "", ["vs Kirby"], """0 HR, 95.6 mph EV. Kirby LHB split +0.96, HR risk 0.50. limited recent HR events.""", blast="good"),
            row("Jackson Chourio", "R", "+511", 71, "💎", ["vs Kirby"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.7 mph EV. Kirby RHB split +0.02, HR risk 0.50.""", blast="good"),
            row("William Contreras", "R", "+524", 63, "⭐", ["vs Kirby"], """Worst Pickz Favorite. 0 HR, 92.7 mph EV. Kirby RHB split +0.02, HR risk 0.50. limited recent HR events.""", blast="good"),
            row("Randy Arozarena", "R", "+459", 78, "", ["vs Gasser"], """1 HR, 1 near-HR, 95.7 mph EV. Gasser RHB split +0.85, HR risk 0.55.""", blast="good"),
            row("Julio Rodriguez", "R", "+423", 66, "", ["vs Gasser"], """0 HR, 1 near-HR, 91.1 mph EV. Gasser RHB split +0.85, HR risk 0.55. limited recent HR events."""),
            row("Cal Raleigh", "S", "+406", 64, "", ["vs Gasser"], """0 HR, 90.6 mph EV. Gasser SHB→RHB split +0.85, HR risk 0.55. limited recent HR events."""),
            row("Weston Wilson", "R", "+511", 70, "", ["vs Gasser"], """1 HR, 1 near-HR, 87.6 mph EV. Gasser RHB split +0.85, HR risk 0.55. lighter EV form (87.6 mph).""", blast="good"),
        ],
    },
    {
        "title": "SF @ CLE - Landen Roupp (R, SF) vs Gavin Williams (R, CLE)",
        "description": "Tail key data: Park boost -10% (stadium -2%, weather -8%). Roupp (HR risk -0.66, vs LHB -0.35, vs RHB -0.53). Williams (HR risk 0.79, vs LHB +0.59, vs RHB +0.99).",
        "rows": [
            row("Jo Adell", "R", "+630", 58, "", ["vs Roupp"], """0 HR, 1 near-HR, 93.3 mph EV. Roupp RHB split -0.53, HR risk -0.66. tough split lane (-0.53); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Nathaniel Lowe", "L", "+940", 58, "💎", ["vs Roupp"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 85.9 mph EV. Roupp LHB split -0.35, HR risk -0.66. slight split headwind (-0.35); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Bryce Eldridge", "L", "+556", 85, "⭐ 🌕 💣", ["vs Williams"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 89.8 mph EV. Williams LHB split +0.59, HR risk 0.79. park/weather net drag (-10%).""", blast="high"),
            row("Rafael Devers", "L", "+360", 84, "🌕 💣", ["vs Williams"], """2 HR, 2 near-HR, 93.7 mph EV. Williams LHB split +0.59, HR risk 0.79. park/weather net drag (-10%).""", blast="high"),
            row("Jung Hoo Lee", "L", "+1120", 78, "", ["vs Williams"], """1 HR, 3 near-HR, 91.5 mph EV. Williams LHB split +0.59, HR risk 0.79. park/weather net drag (-10%).""", blast="good"),
        ],
    },
    {
        "title": "STL @ CIN - Michael McGreevy (R, STL) vs Brady Singer (R, CIN)",
        "description": "Tail key data: Park boost +2% (stadium +15%, weather -13%). McGreevy (HR risk 0.67, vs LHB +1.09, vs RHB -0.30). Singer (HR risk 0.03, vs LHB +0.48, vs RHB -0.65).",
        "rows": [
            row("JJ Bleday", "L", "+390", 76, "💎", ["vs McGreevy"], """Worst Pickz Hidden Gem. 0 HR, 94.5 mph EV. McGreevy LHB split +1.09, HR risk 0.67. weather carry headwind (-13%); limited recent HR events.""", blast="good"),
            row("Michael Toglia", "S", "N/A", 77, "", ["vs McGreevy"], """0 HR, 96.5 mph EV. McGreevy SHB→LHB split +1.09, HR risk 0.67. weather carry headwind (-13%); limited recent HR events.""", blast="good"),
            row("Tyler Stephenson", "R", "+467", 77, "🌕 💣", ["vs McGreevy"], """2 HR, 2 near-HR, 91.8 mph EV. McGreevy RHB split -0.30, HR risk 0.67. slight split headwind (-0.30); weather carry headwind (-13%).""", blast="high"),
            row("Elly De La Cruz", "S", "+365", 77, "", ["vs McGreevy"], """0 HR, 95.9 mph EV. McGreevy SHB→LHB split +1.09, HR risk 0.67. weather carry headwind (-13%); limited recent HR events.""", blast="good"),
            row("Matt McLain", "R", "+558", 71, "", ["vs McGreevy"], """1 HR, 2 near-HR, 93.5 mph EV. McGreevy RHB split -0.30, HR risk 0.67. slight split headwind (-0.30); weather carry headwind (-13%).""", blast="good"),
            row("Eugenio Suarez", "R", "+401", 58, "", ["vs McGreevy"], """0 HR, 90.9 mph EV. McGreevy RHB split -0.30, HR risk 0.67. slight split headwind (-0.30); weather carry headwind (-13%)."""),
            row("Alec Burleson", "L", "+320", 79, "🚀 ⭐ 🌕 💣", ["vs Singer"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 102.2 mph EV. Singer LHB split +0.48, HR risk 0.03. weather carry headwind (-13%).""", blast="high"),
            row("Jimmy Crooks", "L", "+490", 65, "💎", ["vs Singer"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.7 mph EV. Singer LHB split +0.48, HR risk 0.03. weather carry headwind (-13%); limited recent HR events.""", blast="good"),
            row("Ivan Herrera", "R", "+588", 63, "", ["vs Singer"], """1 HR, 3 near-HR, 93.0 mph EV. Singer RHB split -0.65, HR risk 0.03. tough split lane (-0.65); weather carry headwind (-13%).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ TB - Shane Bieber (R, TOR) vs Ian Seymour (L, TB)",
        "description": "Tail key data: Park boost -3% (stadium -3%, weather +1%). Bieber (HR risk 0.89, vs LHB +1.07, vs RHB +0.19). Seymour (HR risk 0.38, vs LHB +0.36, vs RHB +0.38).",
        "rows": [
            row("Jonny DeLuca", "R", "N/A", 84, "🌕 💣 💎", ["vs Bieber"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.5 mph EV. Bieber RHB split +0.19, HR risk 0.89.""", blast="high"),
            row("Jorge Mateo", "R", "N/A", 74, "", ["vs Bieber"], """1 HR, 1 near-HR, 93.6 mph EV. Bieber RHB split +0.19, HR risk 0.89.""", blast="good"),
            row("Yandy Diaz", "R", "+630", 78, "🌕 💣 💎", ["vs Bieber"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 88.3 mph EV. Bieber RHB split +0.19, HR risk 0.89.""", blast="high"),
            row("Jonathan Aranda", "L", "+571", 72, "", ["vs Bieber"], """0 HR, 2 near-HR, 87.5 mph EV. Bieber LHB split +1.07, HR risk 0.89. lighter EV form (87.5 mph).""", blast="good"),
            row("Kazuma Okamoto", "R", "+428", 69, "⭐", ["vs Seymour"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.6 mph EV. Seymour RHB split +0.38, HR risk 0.38.""", blast="good"),
            row("Daz Cameron", "R", "N/A", 65, "🚀", ["vs Seymour"], """0 HR, 108.5 mph EV. Seymour RHB split +0.38, HR risk 0.38. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "WSH @ TEX - Andrew Alvarez (L, WSH) vs Jacob deGrom (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -10%, weather -1%). Alvarez (HR risk -1.41, vs LHB -1.04, vs RHB -1.04). deGrom (HR risk 0.01, vs LHB +0.56, vs RHB -0.81).",
        "rows": [
            row("Corey Seager", "L", "+420", 58, "⭐", ["vs Alvarez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.8 mph EV. Alvarez LHB split -1.04, HR risk -1.41. tough split lane (-1.04); pitcher suppresses HR (-1.41).""", blast="good"),
            row("Jake Burger", "R", "+470", 58, "", ["vs Alvarez"], """1 HR, 2 near-HR, 94.8 mph EV. Alvarez RHB split -1.04, HR risk -1.41. tough split lane (-1.04); pitcher suppresses HR (-1.41).""", blast="good"),
            row("Jarred Kelenic", "L", "N/A", 58, "", ["vs Alvarez"], """0 HR, 95.9 mph EV. Alvarez LHB split -1.04, HR risk -1.41. tough split lane (-1.04); pitcher suppresses HR (-1.41).""", blast="good"),
            row("Abimelec Ortiz", "L", "+447", 83, "🌕 💣 💎", ["vs deGrom"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 95.4 mph EV. deGrom LHB split +0.56, HR risk 0.01. park/weather net drag (-11%).""", blast="high"),
            row("Brady House", "R", "+730", 58, "", ["vs deGrom"], """0 HR, 2 near-HR, 92.8 mph EV. deGrom RHB split -0.81, HR risk 0.01. tough split lane (-0.81); park/weather net drag (-11%).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-20")

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

    out = ROOT / '_games-0820.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
