#!/usr/bin/env python3
"""Generate games[] block for 2026-06-22 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Byron Buxton (R)",
    "Dalton Rushing (L)",
    "Dillon Dingler (R)",
    "Eric Wagaman (R)",
    "Jac Caglianone (L)",
    "Jazz Chisholm Jr. (L)",
    "Kazuma Okamoto (R)",
    "Kyle Schwarber (L)",
    "Kyle Stowers (L)",
    "Pete Alonso (R)",
    "Pete Crow-Armstrong (L)",
    "Shohei Ohtani (L)",
    "Ty France (R)",
}

GEMS = {
    "James Wood (L)",
    "Matt Shaw (R)",
    "Owen Caissie (L)",
    "Rowdy Tellez (L)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Andrew Benintendi (L)": "CWS",
    "Bo Bichette (R)": "NYM",
    "Brandon Nimmo (L)": "TEX",
    "Brandon Valenzuela (S)": "TOR",
    "Braxton Fulford (R)": "COL",
    "Byron Buxton (R)": "MIN",
    "Caleb Durbin (R)": "BOS",
    "Carson Benge (L)": "NYM",
    "Carter Jensen (L)": "KC",
    "Ceddanne Rafaela (R)": "BOS",
    "Cedric Mullins (L)": "TB",
    "Cody Bellinger (L)": "NYY",
    "Colt Keith (L)": "DET",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "Daniel Schneemann (L)": "CLE",
    "Davis Schneider (R)": "TOR",
    "Dillon Dingler (R)": "DET",
    "Donovan Walton (L)": "LAA",
    "Drake Baldwin (L)": "ATL",
    "Dylan Crews (R)": "WSH",
    "Eric Wagaman (R)": "NYM",
    "Eugenio Suarez (R)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Garrett Mitchell (L)": "MIL",
    "Gary Sanchez (R)": "MIL",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "TB",
    "Hunter Goodman (R)": "COL",
    "Ivan Herrera (R)": "STL",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "James Wood (L)": "WSH",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jo Adell (R)": "LAA",
    "Jonathan Aranda (L)": "TB",
    "Jose Altuve (R)": "HOU",
    "Jose Caballero (R)": "NYY",
    "Josh Bell (S)": "MIN",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Manny Machado (R)": "SD",
    "Mark Vientos (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Matt Shaw (R)": "CHC",
    "Miguel Amaya (R)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Mike Yastrzemski (L)": "ATL",
    "Mookie Betts (R)": "LAD",
    "Nate Eaton (R)": "BOS",
    "Owen Caissie (L)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Randal Grichuk (R)": "CWS",
    "Riley Greene (L)": "DET",
    "Rowdy Tellez (L)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan Vilade (R)": "TB",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Sam Antonacci (L)": "CWS",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Steer (R)": "CIN",
    "Travis Bazzana (L)": "CLE",
    "Ty France (R)": "SD",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Willi Castro (S)": "COL",
    "Wyatt Langford (R)": "TEX",
    "Yainer Diaz (R)": "HOU",
    "Yordan Alvarez (L)": "HOU",
}

BUM_RISK_MIN = 0.95

BUM_PITCHERS = {
    "Imanaga",
    "Lauer",
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
        "title": "ARI @ STL - Merrill Kelly (R, ARI) vs Andre Pallante (R, STL)",
        "description": "Tail key data: Park boost -21% (stadium -9%, weather -11%). Kelly (HR risk 0.72, vs LHB +0.94, vs RHB +0.11). Pallante (HR risk -0.62, vs LHB -0.15, vs RHB -0.75).",
        "rows": [
            row("Alec Burleson", "L", "+450", 93, "🌕 💣", ["vs Kelly"], """3 HR, 4 near-HR, 94.8 mph EV. Kelly LHB split +0.94, HR risk 0.72. park/weather net drag (-21%).""", blast="high"),
            row("Ivan Herrera", "R", "+710", 84, "🌕 💣", ["vs Kelly"], """2 HR, 2 near-HR, 94.2 mph EV. Kelly RHB split +0.11, HR risk 0.72. park/weather net drag (-21%).""", blast="high"),
            row("JJ Wetherholt", "L", "+540", 84, "🌕 💣", ["vs Kelly"], """3 HR, 2 near-HR, 89.9 mph EV. Kelly LHB split +0.94, HR risk 0.72. park/weather net drag (-21%).""", blast="high"),
            row("Corbin Carroll", "L", "+594", 90, "🌕 💣", ["vs Pallante"], """3 HR, 3 near-HR, 94.5 mph EV. Pallante LHB split -0.15, HR risk -0.62. slight split headwind (-0.15); pitcher suppresses HR (-0.62).""", blast="high"),
            row("Ketel Marte", "S", "+620", 72, "", ["vs Pallante"], """0 HR, 96.4 mph EV. Pallante RHB split -0.75, HR risk -0.62. tough split lane (-0.75); pitcher suppresses HR (-0.62).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ SD - Grant Holmes (L, ATL) vs Michael King (R, SD)",
        "description": "Tail key data: Park boost -8% (stadium -4%, weather -4%). Holmes (HR risk 0.91, vs LHB +0.93, vs RHB +0.29). King (HR risk 0.24, vs LHB +0.22, vs RHB +0.21).",
        "rows": [
            row("Ty France", "R", "+650", 81, "⭐ 🌕 💣", ["vs Holmes"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.7 mph EV. Holmes RHB split +0.29, HR risk 0.91. park/weather net drag (-8%).""", blast="high"),
            row("Fernando Tatis Jr.", "R", "+450", 85, "", ["vs Holmes"], """1 HR, 3 near-HR, 98.7 mph EV. Holmes RHB split +0.29, HR risk 0.91. park/weather net drag (-8%).""", blast="good"),
            row("Manny Machado", "R", "+430", 73, "", ["vs Holmes"], """1 HR, 2 near-HR, 88.8 mph EV. Holmes RHB split +0.29, HR risk 0.91. park/weather net drag (-8%).""", blast="good"),
            row("Matt Olson", "L", "+340", 81, "", ["vs King"], """1 HR, 2 near-HR, 97.2 mph EV. King LHB split +0.22, HR risk 0.24. park/weather net drag (-8%).""", blast="good"),
            row("Mike Yastrzemski", "L", "+650", 75, "", ["vs King"], """1 HR, 1 near-HR, 92.9 mph EV. King LHB split +0.22, HR risk 0.24. park/weather net drag (-8%).""", blast="good"),
            row("Drake Baldwin", "L", "+358", 72, "", ["vs King"], """1 HR, 1 near-HR, 90.5 mph EV. King LHB split +0.22, HR risk 0.24. park/weather net drag (-8%).""", blast="good"),
            row("Rowdy Tellez", "L", "N/A", 73, "💎", ["vs King"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.2 mph EV. King LHB split +0.22, HR risk 0.24. park/weather net drag (-8%).""", blast="good"),
        ],
    },
    {
        "title": "BAL @ LAA - Kyle Bradish (R, BAL) vs Samuel Aldegheri (L, LAA)",
        "description": "Tail key data: Park boost +8% (stadium +9%, weather -1%). Bradish (HR risk -0.07, vs LHB +0.04, vs RHB -0.12). Aldegheri (HR risk -0.68, vs LHB +0.37, vs RHB -0.55).",
        "rows": [
            row("Donovan Walton", "L", "+850", 79, "🌕 💣", ["vs Bradish"], """2 HR, 2 near-HR, 88.8 mph EV. Bradish LHB split +0.04, HR risk -0.07. pitcher risk below avg (-0.07).""", blast="high"),
            row("Jo Adell", "R", "+489", 63, "", ["vs Bradish"], """0 HR, 88.9 mph EV. Bradish RHB split -0.12, HR risk -0.07. slight split headwind (-0.12); pitcher risk below avg (-0.07)."""),
            row("Pete Alonso", "R", "+287", 74, "⭐", ["vs Aldegheri"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.2 mph EV. Aldegheri RHB split -0.55, HR risk -0.68. tough split lane (-0.55); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Colton Cowser", "L", "N/A", 63, "", ["vs Aldegheri"], """0 HR, 89.2 mph EV. Aldegheri LHB split +0.37, HR risk -0.68. pitcher suppresses HR (-0.68); limited recent HR events."""),
        ],
    },
    {
        "title": "BOS @ COL - Jake Bennett (L, BOS) vs Ryan Feltner (R, COL)",
        "description": "Tail key data: Park boost +32% (stadium +21%, weather +11%). Bennett (HR risk -1.05, vs LHB -1.96, vs RHB -0.24). Feltner (HR risk -0.23, vs LHB -0.24, vs RHB -0.06).",
        "rows": [
            row("Hunter Goodman", "R", "+265", 72, "", ["vs Bennett"], """1 HR, 1 near-HR, 89.5 mph EV. Bennett RHB split -0.24, HR risk -1.05. slight split headwind (-0.24); pitcher suppresses HR (-1.05).""", blast="good"),
            row("Willi Castro", "S", "+570", 68, "", ["vs Bennett"], """1 HR, 86.3 mph EV. Bennett RHB split -0.24, HR risk -1.05. slight split headwind (-0.24); pitcher suppresses HR (-1.05).""", blast="good"),
            row("Braxton Fulford", "R", "+680", 66, "", ["vs Bennett"], """0 HR, 1 near-HR, 89.5 mph EV. Bennett RHB split -0.24, HR risk -1.05. slight split headwind (-0.24); pitcher suppresses HR (-1.05)."""),
            row("Ceddanne Rafaela", "R", "+493", 72, "", ["vs Feltner"], """1 HR, 2 near-HR, 82.1 mph EV. Feltner RHB split -0.06, HR risk -0.23. slight split headwind (-0.06); pitcher risk below avg (-0.23).""", blast="good"),
            row("Nate Eaton", "R", "N/A", 76, "", ["vs Feltner"], """1 HR, 1 near-HR, 94.3 mph EV. Feltner RHB split -0.06, HR risk -0.23. slight split headwind (-0.06); pitcher risk below avg (-0.23).""", blast="good"),
            row("Caleb Durbin", "R", "+870", 84, "🌕 💣", ["vs Feltner"], """3 HR, 3 near-HR, 82.8 mph EV. Feltner RHB split -0.06, HR risk -0.23. slight split headwind (-0.06); pitcher risk below avg (-0.23).""", blast="high"),
        ],
    },
    {
        "title": "CHC @ NYM - Shota Imanaga 🧤 (L, CHC) vs Kodai Senga 🧤 (R, NYM)",
        "description": "Tail key data: Park boost +3% (stadium -1%, weather +4%). Imanaga 🧤 (HR risk 1.21, vs LHB +0.23, vs RHB +1.36). Senga 🧤 (HR risk 1.46, vs LHB +0.85, vs RHB +1.51).",
        "rows": [
            row("Eric Wagaman", "R", "+324", 82, "🚀 ⭐", ["vs Imanaga"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 109.4 mph EV. Imanaga RHB split +1.36, HR risk 1.21.""", blast="good"),
            row("Juan Soto", "L", "+329", 78, "", ["vs Imanaga"], """1 HR, 1 near-HR, 95.6 mph EV. Imanaga LHB split +0.23, HR risk 1.21.""", blast="good"),
            row("Bo Bichette", "R", "+490", 70, "", ["vs Imanaga"], """0 HR, 94.3 mph EV. Imanaga RHB split +1.36, HR risk 1.21. limited recent HR events.""", blast="good"),
            row("Carson Benge", "L", "+630", 76, "", ["vs Imanaga"], """1 HR, 2 near-HR, 92.3 mph EV. Imanaga LHB split +0.23, HR risk 1.21.""", blast="good"),
            row("Mark Vientos", "R", "+414", 65, "", ["vs Imanaga"], """0 HR, 90.9 mph EV. Imanaga RHB split +1.36, HR risk 1.21. limited recent HR events."""),
            row("Pete Crow-Armstrong", "L", "+342", 82, "⭐ 🌕 💣", ["vs Senga"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 89.5 mph EV. Senga LHB split +0.85, HR risk 1.46.""", blast="high"),
            row("Matt Shaw", "R", "+820", 73, "💎", ["vs Senga"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.1 mph EV. Senga RHB split +1.51, HR risk 1.46. limited recent HR events.""", blast="good"),
            row("Miguel Amaya", "R", "N/A", 73, "", ["vs Senga"], """0 HR, 2 near-HR, 93.4 mph EV. Senga RHB split +1.51, HR risk 1.46.""", blast="good"),
        ],
    },
    {
        "title": "CLE @ CWS - Gavin Williams (R, CLE) vs Anthony Kay (L, CWS)",
        "description": "Tail key data: Park boost data unavailable. Williams (HR risk 0.77, vs LHB +0.37, vs RHB +0.96). Kay (HR risk 0.27, vs LHB +0.14, vs RHB +0.30).",
        "rows": [
            row("Andrew Benintendi", "L", "+463", 86, "🌕 💣", ["vs Williams"], """3 HR, 2 near-HR, 92.2 mph EV. Williams LHB split +0.37, HR risk 0.77.""", blast="high"),
            row("Miguel Vargas", "R", "+400", 68, "", ["vs Williams"], """0 HR, 2 near-HR, 88.4 mph EV. Williams RHB split +0.96, HR risk 0.77.""", blast="good"),
            row("Sam Antonacci", "L", "+820", 90, "🌕 💣", ["vs Williams"], """3 HR, 3 near-HR, 94.4 mph EV. Williams LHB split +0.37, HR risk 0.77.""", blast="high"),
            row("Randal Grichuk", "R", "N/A", 74, "", ["vs Williams"], """0 HR, 1 near-HR, 95.6 mph EV. Williams RHB split +0.96, HR risk 0.77. limited recent HR events.""", blast="good"),
            row("Daniel Schneemann", "L", "N/A", 72, "", ["vs Kay"], """1 HR, 1 near-HR, 89.5 mph EV. Kay LHB split +0.14, HR risk 0.27.""", blast="good"),
            row("Kyle Manzardo", "L", "+498", 71, "", ["vs Kay"], """0 HR, 1 near-HR, 93.1 mph EV. Kay LHB split +0.14, HR risk 0.27. limited recent HR events.""", blast="good"),
            row("Travis Bazzana", "L", "+820", 62, "", ["vs Kay"], """0 HR, 84.1 mph EV. Kay LHB split +0.14, HR risk 0.27. limited recent HR events; lighter EV form (84.1 mph)."""),
        ],
    },
    {
        "title": "HOU @ TOR - Hunter Brown (R, HOU) vs Dylan Cease (R, TOR)",
        "description": "Tail key data: Park boost +1% (stadium +6%, weather -5%). Brown (HR risk -1.77, vs LHB -1.07, vs RHB -1.61). Cease (HR risk -0.51, vs LHB -0.03, vs RHB -1.01).",
        "rows": [
            row("Kazuma Okamoto", "R", "+520", 85, "⭐ 🌕 💣", ["vs Brown"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 92.6 mph EV. Brown RHB split -1.61, HR risk -1.77. tough split lane (-1.61); pitcher suppresses HR (-1.77).""", blast="high"),
            row("Vladimir Guerrero Jr.", "R", "+650", 70, "", ["vs Brown"], """1 HR, 1 near-HR, 87.9 mph EV. Brown RHB split -1.61, HR risk -1.77. tough split lane (-1.61); pitcher suppresses HR (-1.77).""", blast="good"),
            row("Davis Schneider", "R", "N/A", 70, "", ["vs Brown"], """1 HR, 1 near-HR, 82.8 mph EV. Brown RHB split -1.61, HR risk -1.77. tough split lane (-1.61); pitcher suppresses HR (-1.77).""", blast="good"),
            row("Brandon Valenzuela", "S", "N/A", 88, "🌕 💣", ["vs Brown"], """2 HR, 4 near-HR, 93.6 mph EV. Brown RHB split -1.61, HR risk -1.77. tough split lane (-1.61); pitcher suppresses HR (-1.77).""", blast="high"),
            row("Yordan Alvarez", "L", "+295", 63, "", ["vs Cease"], """0 HR, 89.3 mph EV. Cease LHB split -0.03, HR risk -0.51. slight split headwind (-0.03); pitcher suppresses HR (-0.51)."""),
            row("Yainer Diaz", "R", "+1060", 75, "", ["vs Cease"], """1 HR, 1 near-HR, 92.7 mph EV. Cease RHB split -1.01, HR risk -0.51. tough split lane (-1.01); pitcher suppresses HR (-0.51).""", blast="good"),
            row("Jose Altuve", "R", "+800", 72, "", ["vs Cease"], """1 HR, 2 near-HR, 87.8 mph EV. Cease RHB split -1.01, HR risk -0.51. tough split lane (-1.01); pitcher suppresses HR (-0.51).""", blast="good"),
        ],
    },
    {
        "title": "KC @ TB - Michael Wacha (R, KC) vs Drew Rasmussen (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Wacha (HR risk -0.85, vs LHB -0.43, vs RHB -0.86). Rasmussen (HR risk -0.79, vs LHB -0.30, vs RHB -1.05).",
        "rows": [
            row("Jonathan Aranda", "L", "+486", 73, "", ["vs Wacha"], """1 HR, 1 near-HR, 90.9 mph EV. Wacha LHB split -0.43, HR risk -0.85. tough split lane (-0.43); pitcher suppresses HR (-0.85).""", blast="good"),
            row("Ryan Vilade", "R", "N/A", 89, "🌕 💣", ["vs Wacha"], """2 HR, 2 near-HR, 99.2 mph EV. Wacha RHB split -0.86, HR risk -0.85. tough split lane (-0.86); pitcher suppresses HR (-0.85).""", blast="high"),
            row("Junior Caminero", "R", "+310", 76, "🚀", ["vs Wacha"], """0 HR, 101.0 mph EV. Wacha RHB split -0.86, HR risk -0.85. tough split lane (-0.86); pitcher suppresses HR (-0.85).""", blast="good"),
            row("Cedric Mullins", "L", "+575", 72, "", ["vs Wacha"], """1 HR, 2 near-HR, 88.2 mph EV. Wacha LHB split -0.43, HR risk -0.85. tough split lane (-0.43); pitcher suppresses HR (-0.85).""", blast="good"),
            row("Hunter Feduccia", "L", "+1140", 74, "", ["vs Wacha"], """0 HR, 98.1 mph EV. Wacha LHB split -0.43, HR risk -0.85. tough split lane (-0.43); pitcher suppresses HR (-0.85).""", blast="good"),
            row("Jac Caglianone", "L", "+500", 90, "⭐ 🌕 💣", ["vs Rasmussen"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 94.0 mph EV. Rasmussen LHB split -0.30, HR risk -0.79. slight split headwind (-0.30); pitcher suppresses HR (-0.79).""", blast="high"),
            row("Carter Jensen", "L", "+630", 62, "", ["vs Rasmussen"], """0 HR, 87.4 mph EV. Rasmussen LHB split -0.30, HR risk -0.79. slight split headwind (-0.30); pitcher suppresses HR (-0.79)."""),
            row("Salvador Perez", "R", "+489", 66, "", ["vs Rasmussen"], """0 HR, 1 near-HR, 89.9 mph EV. Rasmussen RHB split -1.05, HR risk -0.79. tough split lane (-1.05); pitcher suppresses HR (-0.79)."""),
        ],
    },
    {
        "title": "LAD @ MIN - Eric Lauer 🧤 (L, LAD) vs Zebby Matthews (R, MIN)",
        "description": "Tail key data: Park boost -15% (stadium -6%, weather -9%). Lauer 🧤 (HR risk 1.06, vs LHB +1.10, vs RHB +0.95). Matthews (HR risk 0.73, vs LHB +0.58, vs RHB +0.57).",
        "rows": [
            row("Byron Buxton", "R", "+230", 97, "⭐ 🌕 💣", ["vs Lauer"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 98.8 mph EV. Lauer RHB split +0.95, HR risk 1.06. park/weather net drag (-15%).""", blast="high"),
            row("Josh Bell", "S", "+500", 70, "", ["vs Lauer"], """1 HR, 1 near-HR, 87.5 mph EV. Lauer RHB split +0.95, HR risk 1.06. park/weather net drag (-15%); lighter EV form (87.5 mph).""", blast="good"),
            row("Royce Lewis", "R", "+390", 74, "", ["vs Lauer"], """1 HR, 2 near-HR, 90.1 mph EV. Lauer RHB split +0.95, HR risk 1.06. park/weather net drag (-15%).""", blast="good"),
            row("Shohei Ohtani", "L", "+220", 83, "⭐ 🌕 💣", ["vs Matthews"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 90.6 mph EV. Matthews LHB split +0.58, HR risk 0.73. park/weather net drag (-15%).""", blast="high"),
            row("Dalton Rushing", "L", "+518", 76, "⭐", ["vs Matthews"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.1 mph EV. Matthews LHB split +0.58, HR risk 0.73. park/weather net drag (-15%).""", blast="good"),
            row("Mookie Betts", "R", "+557", 83, "🌕 💣", ["vs Matthews"], """2 HR, 3 near-HR, 90.9 mph EV. Matthews RHB split +0.57, HR risk 0.73. park/weather net drag (-15%).""", blast="high"),
        ],
    },
    {
        "title": "MIL @ CIN - Brandon Woodruff (R, MIL) vs Brady Singer (R, CIN)",
        "description": "Tail key data: Park boost +18% (stadium +14%, weather +4%). Away starter risk unavailable. Singer (HR risk 0.75, vs LHB +0.56, vs RHB +0.77).",
        "rows": [
            row("Eugenio Suarez", "R", "+390", 70, "", ["vs Woodruff"], """1 HR, 1 near-HR, 88.0 mph EV. Woodruff split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Sal Stewart", "R", "+440", 76, "", ["vs Woodruff"], """1 HR, 2 near-HR, 91.8 mph EV. Woodruff split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Spencer Steer", "R", "+450", 78, "🌕 💣", ["vs Woodruff"], """2 HR, 2 near-HR, 88.5 mph EV. Woodruff split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Jake Bauers", "L", "N/A", 62, "", ["vs Singer"], """0 HR, 73.6 mph EV. Singer LHB split +0.56, HR risk 0.75. limited recent HR events; lighter EV form (73.6 mph)."""),
            row("Gary Sanchez", "R", "+490", 62, "", ["vs Singer"], """0 HR, 81.0 mph EV. Singer RHB split +0.77, HR risk 0.75. limited recent HR events; lighter EV form (81.0 mph)."""),
            row("Garrett Mitchell", "L", "+920", 62, "", ["vs Singer"], """0 HR, 87.7 mph EV. Singer LHB split +0.56, HR risk 0.75. limited recent HR events; lighter EV form (87.7 mph)."""),
            row("Jackson Chourio", "R", "+490", 86, "🌕 💣", ["vs Singer"], """2 HR, 3 near-HR, 94.4 mph EV. Singer RHB split +0.77, HR risk 0.75.""", blast="high"),
        ],
    },
    {
        "title": "NYY @ DET - Gerrit Cole (R, NYY) vs Framber Valdez (L, DET)",
        "description": "Tail key data: Park boost -5% (stadium -11%, weather +7%). Cole (HR risk -0.73, vs LHB -0.71, vs RHB -0.33). Valdez (HR risk -0.41, vs LHB -0.40, vs RHB -0.13).",
        "rows": [
            row("Colt Keith", "L", "+840", 89, "🌕 💣", ["vs Cole"], """3 HR, 5 near-HR, 88.7 mph EV. Cole LHB split -0.71, HR risk -0.73. tough split lane (-0.71); pitcher suppresses HR (-0.73).""", blast="high"),
            row("Dillon Dingler", "R", "+454", 83, "⭐ 🌕 💣", ["vs Cole"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 91.4 mph EV. Cole RHB split -0.33, HR risk -0.73. slight split headwind (-0.33); pitcher suppresses HR (-0.73).""", blast="high"),
            row("Riley Greene", "L", "+415", 84, "🌕 💣", ["vs Cole"], """2 HR, 3 near-HR, 92.1 mph EV. Cole LHB split -0.71, HR risk -0.73. tough split lane (-0.71); pitcher suppresses HR (-0.73).""", blast="high"),
            row("Jose Caballero", "R", "+1140", 62, "", ["vs Valdez"], """0 HR, 76.4 mph EV. Valdez RHB split -0.13, HR risk -0.41. slight split headwind (-0.13); pitcher suppresses HR (-0.41)."""),
            row("Jazz Chisholm Jr.", "L", "+790", 90, "🚀 ⭐ 🌕 💣", ["vs Valdez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 101.5 mph EV. Valdez LHB split -0.40, HR risk -0.41. tough split lane (-0.40); pitcher suppresses HR (-0.41).""", blast="high"),
            row("Cody Bellinger", "L", "+660", 70, "", ["vs Valdez"], """1 HR, 1 near-HR, 83.4 mph EV. Valdez LHB split -0.40, HR risk -0.41. tough split lane (-0.40); pitcher suppresses HR (-0.41).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ WSH - Alan Rangel (R, PHI) vs Foster Griffin (L, WSH)",
        "description": "Tail key data: Park boost data unavailable. Away starter risk unavailable. Griffin (HR risk 0.27, vs LHB -0.94, vs RHB +0.78).",
        "rows": [
            row("James Wood", "L", "+320", 77, "💎", ["vs Rangel"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.1 mph EV. Rangel split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Dylan Crews", "R", "+630", 78, "", ["vs Rangel"], """1 HR, 1 near-HR, 96.2 mph EV. Rangel split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Kyle Schwarber", "L", "+245", 87, "⭐ 🌕 💣", ["vs Griffin"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 88.7 mph EV. Griffin LHB split -0.94, HR risk 0.27. tough split lane (-0.94).""", blast="high"),
        ],
    },
    {
        "title": "TEX @ MIA - Kumar Rocker (R, TEX) vs Tyler Phillips (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -13%, weather +0%). Rocker (HR risk -0.09, vs LHB +0.49, vs RHB -0.86). Phillips (HR risk -0.24, vs LHB -0.04, vs RHB -0.30).",
        "rows": [
            row("Kyle Stowers", "L", "+450", 86, "⭐ 🌕 💣", ["vs Rocker"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 90.2 mph EV. Rocker LHB split +0.49, HR risk -0.09. pitcher risk below avg (-0.09); park/weather net drag (-13%).""", blast="high"),
            row("Owen Caissie", "L", "+760", 84, "🌕 💣 💎", ["vs Rocker"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 87.8 mph EV. Rocker LHB split +0.49, HR risk -0.09. pitcher risk below avg (-0.09); park/weather net drag (-13%).""", blast="high"),
            row("Heriberto Hernandez", "R", "+660", 76, "", ["vs Rocker"], """1 HR, 1 near-HR, 94.0 mph EV. Rocker RHB split -0.86, HR risk -0.09. tough split lane (-0.86); pitcher risk below avg (-0.09).""", blast="good"),
            row("Wyatt Langford", "R", "+590", 72, "", ["vs Phillips"], """1 HR, 1 near-HR, 90.1 mph EV. Phillips RHB split -0.30, HR risk -0.24. slight split headwind (-0.30); pitcher risk below avg (-0.24).""", blast="good"),
            row("Brandon Nimmo", "L", "+725", 74, "", ["vs Phillips"], """0 HR, 1 near-HR, 96.1 mph EV. Phillips LHB split -0.04, HR risk -0.24. slight split headwind (-0.04); pitcher risk below avg (-0.24).""", blast="good"),
            row("Jake Burger", "R", "+524", 74, "", ["vs Phillips"], """1 HR, 3 near-HR, 85.8 mph EV. Phillips RHB split -0.30, HR risk -0.24. slight split headwind (-0.30); pitcher risk below avg (-0.24).""", blast="good"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-22")

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
