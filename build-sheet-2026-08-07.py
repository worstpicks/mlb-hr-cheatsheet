#!/usr/bin/env python3
"""Generate games[] block for 2026-08-07 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Bryce Harper (L)",
    "Esmerlyn Valdez (R)",
    "Owen Caissie (L)",
    "Pete Crow-Armstrong (L)",
    "Rhys Hoskins (R)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Bobby Witt Jr. (R)",
    "Brett Baty (L)",
    "Griffin Conine (L)",
    "Jesus Sanchez (L)",
    "Jimmy Crooks (L)",
    "Mickey Moniak (L)",
    "Pete Alonso (R)",
    "Tyler Stephenson (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Alejandro Osuna (L)": "TEX",
    "Austin Riley (R)": "ATL",
    "Austin Wells (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brady House (R)": "WSH",
    "Brandon Valenzuela (S)": "TOR",
    "Brett Baty (L)": "NYM",
    "Brian Serven (R)": "ATH",
    "Bryce Harper (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Derek Hill (R)": "PHI",
    "Dillon Dingler (R)": "DET",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Francisco Lindor (S)": "NYM",
    "Freddie Freeman (L)": "LAD",
    "Gage Workman (L)": "SD",
    "George Lombard Jr. (R)": "NYY",
    "Gleyber Torres (R)": "DET",
    "Griffin Conine (L)": "MIA",
    "Ivan Herrera (R)": "STL",
    "JJ Bleday (L)": "CIN",
    "Jackson Chourio (R)": "MIL",
    "Jake Bauers (L)": "MIL",
    "Jakob Marsee (L)": "MIA",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jesus Sanchez (L)": "TOR",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "CLE",
    "Jonah Heim (S)": "ATH",
    "Jose Caballero (R)": "NYY",
    "Josh Lowe (L)": "LAA",
    "Junior Caminero (R)": "TB",
    "Kyle Stowers (L)": "MIA",
    "Luis Arraez (L)": "PHI",
    "Max Muncy (L)": "LAD",
    "Michael Harris II (L)": "ATL",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Nelson Velazquez (R)": "STL",
    "Nick Allen (R)": "HOU",
    "Owen Caissie (L)": "MIA",
    "Ozzie Albies (S)": "ATL",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Ryan Kreidler (R)": "MIN",
    "Sal Stewart (R)": "CIN",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Torkelson (R)": "DET",
    "Tim Tawa (R)": "ARI",
    "Tyler Soderstrom (L)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "Tyrone Taylor (R)": "CHC",
    "Victor Mesa Jr. (L)": "TB",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("ATH @ BOS", "Perkins"),
    ("COL @ STL", "Feltner"),
    ("HOU @ SD", "Blanco"),
    ("LAA @ MIA", "Klassen"),
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
        "title": "ATH @ BOS - Jack Perkins 🧤 (R, ATH) vs Payton Tolle (L, BOS)",
        "description": "Tail key data: Park boost +11% (stadium -8%, weather +19%). Perkins 🧤 (HR risk 0.96, vs LHB +1.21, vs RHB +0.37). Tolle (HR risk 0.11, vs LHB -0.02, vs RHB +0.10).",
        "rows": [
            row("Wilyer Abreu", "L", "+360", 85, "", ["vs Perkins"], """0 HR, 98.2 mph EV. Perkins LHB split +1.21, HR risk 0.96. park suppresses carry (-8%); limited recent HR events.""", blast="good"),
            row("Willson Contreras", "R", "+390", 74, "", ["vs Perkins"], """1 HR, 1 near-HR, 83.3 mph EV. Perkins RHB split +0.37, HR risk 0.96. park suppresses carry (-8%); lighter EV form (83.3 mph).""", blast="good"),
            row("Brian Serven", "R", "N/A", 79, "🌕 💣", ["vs Tolle"], """2 HR, 2 near-HR, 99.0 mph EV. Tolle RHB split +0.10, HR risk 0.11. park suppresses carry (-8%).""", blast="high"),
            row("Tyler Soderstrom", "L", "+559", 63, "🚀", ["vs Tolle"], """0 HR, 101.6 mph EV. Tolle LHB split -0.02, HR risk 0.11. slight split headwind (-0.02); park suppresses carry (-8%).""", blast="good"),
            row("Jonah Heim", "S", "+573", 67, "", ["vs Tolle"], """1 HR, 1 near-HR, 93.7 mph EV. Tolle SHB→RHB split +0.10, HR risk 0.11. park suppresses carry (-8%).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ NYY - Tyler Mahle (R, ATL) vs Max Fried (L, NYY)",
        "description": "Tail key data: Park boost +15% (stadium +4%, weather +12%). Mahle (HR risk -0.53, vs LHB -0.52, vs RHB -0.30). Fried (HR risk -1.56, vs LHB -0.95, vs RHB -1.12).",
        "rows": [
            row("Austin Wells", "L", "+450", 59, "🚀", ["vs Mahle"], """1 HR, 1 near-HR, 101.1 mph EV. Mahle LHB split -0.52, HR risk -0.53. tough split lane (-0.52); pitcher suppresses HR (-0.53).""", blast="good"),
            row("Jose Caballero", "R", "N/A", 66, "🌕 💣", ["vs Mahle"], """2 HR, 2 near-HR, 91.3 mph EV. Mahle RHB split -0.30, HR risk -0.53. slight split headwind (-0.30); pitcher suppresses HR (-0.53).""", blast="high"),
            row("George Lombard Jr.", "R", "N/A", 58, "🚀", ["vs Mahle"], """0 HR, 101.9 mph EV. Mahle RHB split -0.30, HR risk -0.53. slight split headwind (-0.30); pitcher suppresses HR (-0.53).""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "+450", 58, "", ["vs Mahle"], """0 HR, 92.5 mph EV. Mahle LHB split -0.52, HR risk -0.53. tough split lane (-0.52); pitcher suppresses HR (-0.53).""", blast="good"),
            row("Michael Harris II", "L", "+586", 58, "", ["vs Fried"], """1 HR, 1 near-HR, 93.9 mph EV. Fried LHB split -0.95, HR risk -1.56. tough split lane (-0.95); pitcher suppresses HR (-1.56).""", blast="good"),
            row("Austin Riley", "R", "+600", 58, "", ["vs Fried"], """1 HR, 1 near-HR, 98.1 mph EV. Fried RHB split -1.12, HR risk -1.56. tough split lane (-1.12); pitcher suppresses HR (-1.56).""", blast="good"),
            row("Ozzie Albies", "S", "+640", 58, "", ["vs Fried"], """0 HR, 94.4 mph EV. Fried SHB→LHB split -0.95, HR risk -1.56. tough split lane (-0.95); pitcher suppresses HR (-1.56).""", blast="good"),
        ],
    },
    {
        "title": "BAL @ TEX - Shane Baz (R, BAL) vs Nathan Eovaldi (R, TEX)",
        "description": "Tail key data: Park boost -10% (stadium -10%, weather -1%). Baz (HR risk -0.76, vs LHB -0.63, vs RHB -0.58). Eovaldi (HR risk 0.74, vs LHB +0.17, vs RHB +0.92).",
        "rows": [
            row("Corey Seager", "L", "+441", 58, "🚀", ["vs Baz"], """0 HR, 101.5 mph EV. Baz LHB split -0.63, HR risk -0.76. tough split lane (-0.63); pitcher suppresses HR (-0.76).""", blast="good"),
            row("Alejandro Osuna", "L", "N/A", 58, "", ["vs Baz"], """0 HR, 95.1 mph EV. Baz LHB split -0.63, HR risk -0.76. tough split lane (-0.63); pitcher suppresses HR (-0.76).""", blast="good"),
            row("Wyatt Langford", "R", "+523", 58, "", ["vs Baz"], """0 HR, 97.9 mph EV. Baz RHB split -0.58, HR risk -0.76. tough split lane (-0.58); pitcher suppresses HR (-0.76).""", blast="good"),
            row("Pete Alonso", "R", "+419", 79, "💎", ["vs Eovaldi"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.7 mph EV. Eovaldi RHB split +0.92, HR risk 0.74. park/weather net drag (-10%).""", blast="good"),
            row("Christian Encarnacion-Strand", "R", "+540", 71, "", ["vs Eovaldi"], """0 HR, 93.1 mph EV. Eovaldi RHB split +0.92, HR risk 0.74. park/weather net drag (-10%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CHC @ KC - Kevin Gausman (R, CHC) vs Easton McGee (R, KC)",
        "description": "Tail key data: Park boost +18% (stadium +10%, weather +8%). Gausman (HR risk -0.74, vs LHB -0.91, vs RHB -0.25). McGee (HR risk -0.95, vs LHB -0.11, vs RHB -1.12).",
        "rows": [
            row("Bobby Witt Jr.", "R", "+400", 62, "💎", ["vs Gausman"], """Worst Pickz Hidden Gem. 0 HR, 3 near-HR, 98.3 mph EV. Gausman RHB split -0.25, HR risk -0.74. slight split headwind (-0.25); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Tyrone Taylor", "R", "+650", 65, "🌕 💣", ["vs McGee"], """2 HR, 2 near-HR, 96.5 mph EV. McGee RHB split -1.12, HR risk -0.95. tough split lane (-1.12); pitcher suppresses HR (-0.95).""", blast="high"),
            row("Pete Crow-Armstrong", "L", "+369", 58, "⭐", ["vs McGee"], """Worst Pickz Favorite. 0 HR, 95.0 mph EV. McGee LHB split -0.11, HR risk -0.95. slight split headwind (-0.11); pitcher suppresses HR (-0.95).""", blast="good"),
        ],
    },
    {
        "title": "CIN @ WSH - Chase Petty (R, CIN) vs Cade Cavalli (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Petty (HR risk 0.31, vs LHB -0.09, vs RHB +0.55). Cavalli (HR risk -0.02, vs LHB +0.25, vs RHB -0.34).",
        "rows": [
            row("Brady House", "R", "N/A", 64, "", ["vs Petty"], """0 HR, 1 near-HR, 92.7 mph EV. Petty RHB split +0.55, HR risk 0.31. limited recent HR events.""", blast="good"),
            row("JJ Bleday", "L", "+420", 72, "🌕 💣", ["vs Cavalli"], """2 HR, 2 near-HR, 91.8 mph EV. Cavalli LHB split +0.25, HR risk -0.02. pitcher risk below avg (-0.02).""", blast="high"),
            row("Eugenio Suarez", "R", "+463", 58, "🚀", ["vs Cavalli"], """0 HR, 1 near-HR, 100.7 mph EV. Cavalli RHB split -0.34, HR risk -0.02. slight split headwind (-0.34); pitcher risk below avg (-0.02).""", blast="good"),
            row("Tyler Stephenson", "R", "+560", 62, "💎", ["vs Cavalli"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 99.1 mph EV. Cavalli RHB split -0.34, HR risk -0.02. slight split headwind (-0.34); pitcher risk below avg (-0.02).""", blast="good"),
            row("Elly De La Cruz", "S", "+500", 65, "", ["vs Cavalli"], """1 HR, 1 near-HR, 94.4 mph EV. Cavalli SHB→LHB split +0.25, HR risk -0.02. pitcher risk below avg (-0.02).""", blast="good"),
            row("Sal Stewart", "R", "+422", 59, "", ["vs Cavalli"], """1 HR, 1 near-HR, 93.6 mph EV. Cavalli RHB split -0.34, HR risk -0.02. slight split headwind (-0.34); pitcher risk below avg (-0.02).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ CWS - Parker Messick (L, CLE) vs Noah Schultz (L, CWS)",
        "description": "Tail key data: Park boost data unavailable. Messick (HR risk -0.86, vs LHB -1.12, vs RHB -0.54). Schultz (HR risk 0.35, vs LHB -0.33, vs RHB +0.31).",
        "rows": [
            row("Miguel Vargas", "R", "+390", 58, "", ["vs Messick"], """0 HR, 99.3 mph EV. Messick RHB split -0.54, HR risk -0.86. tough split lane (-0.54); pitcher suppresses HR (-0.86).""", blast="good"),
            row("Rhys Hoskins", "R", "+390", 68, "⭐", ["vs Schultz"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 92.1 mph EV. Schultz RHB split +0.31, HR risk 0.35.""", blast="good"),
            row("Jo Adell", "R", "+350", 66, "", ["vs Schultz"], """0 HR, 2 near-HR, 94.8 mph EV. Schultz RHB split +0.31, HR risk 0.35.""", blast="good"),
        ],
    },
    {
        "title": "COL @ STL - Ryan Feltner 🧤 (R, COL) vs Kyle Leahy (R, STL)",
        "description": "Tail key data: Park boost -2% (stadium -10%, weather +8%). Feltner 🧤 (HR risk 1.36, vs LHB +1.21, vs RHB +0.92). Leahy (HR risk -0.03, vs LHB +0.14, vs RHB -0.10).",
        "rows": [
            row("Alec Burleson", "L", "+460", 93, "⭐ 🌕 💣", ["vs Feltner"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.0 mph EV. Feltner LHB split +1.21, HR risk 1.36. park suppresses carry (-10%).""", blast="high"),
            row("Jimmy Crooks", "L", "+750", 91, "🌕 💣 💎", ["vs Feltner"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 98.3 mph EV. Feltner LHB split +1.21, HR risk 1.36. park suppresses carry (-10%).""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 85, "🚀", ["vs Feltner"], """0 HR, 1 near-HR, 101.0 mph EV. Feltner RHB split +0.92, HR risk 1.36. park suppresses carry (-10%); limited recent HR events.""", blast="good"),
            row("Ivan Herrera", "R", "+680", 83, "🚀", ["vs Feltner"], """0 HR, 104.3 mph EV. Feltner RHB split +0.92, HR risk 1.36. park suppresses carry (-10%); limited recent HR events.""", blast="good"),
            row("Mickey Moniak", "L", "+470", 74, "🌕 💣 💎", ["vs Leahy"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 95.2 mph EV. Leahy LHB split +0.14, HR risk -0.03. pitcher risk below avg (-0.03); park suppresses carry (-10%).""", blast="high"),
            row("Willi Castro", "S", "+820", 58, "", ["vs Leahy"], """1 HR, 1 near-HR, 88.2 mph EV. Leahy SHB→LHB split +0.14, HR risk -0.03. pitcher risk below avg (-0.03); park suppresses carry (-10%).""", blast="good"),
        ],
    },
    {
        "title": "DET @ SF - Keider Montero (R, DET) vs Adrian Houser (R, SF)",
        "description": "Tail key data: Park boost -26% (stadium -17%, weather -9%). Montero (HR risk -0.37, vs LHB +0.03, vs RHB -0.51). Houser (HR risk -0.02, vs LHB +0.97, vs RHB -0.57).",
        "rows": [
            row("Rafael Devers", "L", "+365", 58, "", ["vs Montero"], """0 HR, 95.0 mph EV. Montero LHB split +0.03, HR risk -0.37. pitcher risk below avg (-0.37); park/weather net drag (-26%).""", blast="good"),
            row("Dillon Dingler", "R", "+630", 64, "🌕 💣", ["vs Houser"], """2 HR, 2 near-HR, 98.7 mph EV. Houser RHB split -0.57, HR risk -0.02. tough split lane (-0.57); pitcher risk below avg (-0.02).""", blast="high"),
            row("Spencer Torkelson", "R", "+525", 58, "", ["vs Houser"], """0 HR, 1 near-HR, 95.6 mph EV. Houser RHB split -0.57, HR risk -0.02. tough split lane (-0.57); pitcher risk below avg (-0.02).""", blast="good"),
            row("Gleyber Torres", "R", "+900", 58, "", ["vs Houser"], """0 HR, 1 near-HR, 93.0 mph EV. Houser RHB split -0.57, HR risk -0.02. tough split lane (-0.57); pitcher risk below avg (-0.02).""", blast="good"),
            row("Riley Greene", "L", "+475", 60, "", ["vs Houser"], """1 HR, 1 near-HR, 89.2 mph EV. Houser LHB split +0.97, HR risk -0.02. pitcher risk below avg (-0.02); park/weather net drag (-26%).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ SD - Ronel Blanco 🧤 (R, HOU) vs Robbie Ray (L, SD)",
        "description": "Tail key data: Park boost -1% (stadium -4%, weather +3%). Blanco 🧤 (HR risk 1.84, vs LHB +1.75, vs RHB +0.88). Ray (HR risk -0.46, vs LHB -0.94, vs RHB -0.14).",
        "rows": [
            row("Gage Workman", "L", "N/A", 81, "", ["vs Blanco"], """0 HR, 90.5 mph EV. Blanco LHB split +1.75, HR risk 1.84. limited recent HR events."""),
            row("Yordan Alvarez", "L", "+310", 61, "⭐", ["vs Ray"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 99.2 mph EV. Ray LHB split -0.94, HR risk -0.46. tough split lane (-0.94); pitcher suppresses HR (-0.46).""", blast="good"),
            row("Nick Allen", "R", "N/A", 58, "", ["vs Ray"], """0 HR, 1 near-HR, 94.9 mph EV. Ray RHB split -0.14, HR risk -0.46. slight split headwind (-0.14); pitcher suppresses HR (-0.46).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ MIA - George Klassen 🧤 (R, LAA) vs Tyler Phillips (R, MIA)",
        "description": "Tail key data: Park boost -12% (stadium -13%, weather +0%). Klassen 🧤 (HR risk 1.50, vs LHB -0.16, vs RHB +2.90). Phillips (HR risk -0.14, vs LHB -0.29, vs RHB +0.01).",
        "rows": [
            row("Owen Caissie", "L", "+630", 88, "⭐ 🌕 💣", ["vs Klassen"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 99.7 mph EV. Klassen LHB split -0.16, HR risk 1.50. slight split headwind (-0.16); park/weather net drag (-12%).""", blast="high"),
            row("Jakob Marsee", "L", "+1060", 74, "", ["vs Klassen"], """1 HR, 1 near-HR, 91.4 mph EV. Klassen LHB split -0.16, HR risk 1.50. slight split headwind (-0.16); park/weather net drag (-12%).""", blast="good"),
            row("Griffin Conine", "L", "+480", 78, "💎", ["vs Klassen"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.3 mph EV. Klassen LHB split -0.16, HR risk 1.50. slight split headwind (-0.16); park/weather net drag (-12%).""", blast="good"),
            row("Kyle Stowers", "L", "+400", 78, "", ["vs Klassen"], """1 HR, 1 near-HR, 95.5 mph EV. Klassen LHB split -0.16, HR risk 1.50. slight split headwind (-0.16); park/weather net drag (-12%).""", blast="good"),
            row("Josh Lowe", "L", "+820", 58, "", ["vs Phillips"], """0 HR, 92.6 mph EV. Phillips LHB split -0.29, HR risk -0.14. slight split headwind (-0.29); pitcher risk below avg (-0.14).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ ARI - Roki Sasaki (R, LAD) vs Merrill Kelly (R, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Sasaki (HR risk 0.63, vs LHB +0.50, vs RHB +0.56). Kelly (HR risk 0.41, vs LHB +0.64, vs RHB +0.05).",
        "rows": [
            row("Corbin Carroll", "L", "+561", 75, "", ["vs Sasaki"], """1 HR, 1 near-HR, 98.8 mph EV. Sasaki LHB split +0.50, HR risk 0.63. park/weather net drag (-8%).""", blast="good"),
            row("Tim Tawa", "R", "+830", 76, "", ["vs Sasaki"], """1 HR, 1 near-HR, 99.4 mph EV. Sasaki RHB split +0.56, HR risk 0.63. park/weather net drag (-8%).""", blast="good"),
            row("Max Muncy", "L", "+411", 69, "", ["vs Kelly"], """0 HR, 96.0 mph EV. Kelly LHB split +0.64, HR risk 0.41. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Shohei Ohtani", "L", "+285", 66, "", ["vs Kelly"], """0 HR, 92.9 mph EV. Kelly LHB split +0.64, HR risk 0.41. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Freddie Freeman", "L", "+530", 66, "", ["vs Kelly"], """0 HR, 93.5 mph EV. Kelly LHB split +0.64, HR risk 0.41. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIN @ MIL - Zebby Matthews (R, MIN) vs Shane Drohan (L, MIL)",
        "description": "Tail key data: Park boost +18% (stadium +10%, weather +8%). Matthews (HR risk 0.55, vs LHB +0.42, vs RHB +0.33). Drohan (HR risk -0.43, vs LHB -0.66, vs RHB -0.19).",
        "rows": [
            row("Jake Bauers", "L", "+360", 80, "", ["vs Matthews"], """1 HR, 2 near-HR, 93.9 mph EV. Matthews LHB split +0.42, HR risk 0.55.""", blast="good"),
            row("Jackson Chourio", "R", "+397", 81, "", ["vs Matthews"], """1 HR, 2 near-HR, 99.0 mph EV. Matthews RHB split +0.33, HR risk 0.55.""", blast="good"),
            row("Ryan Kreidler", "R", "+750", 58, "", ["vs Drohan"], """0 HR, 95.7 mph EV. Drohan RHB split -0.19, HR risk -0.43. slight split headwind (-0.19); pitcher suppresses HR (-0.43).""", blast="good"),
        ],
    },
    {
        "title": "NYM @ PIT - Zach Thornton (L, NYM) vs Carmen Mlodzinski (R, PIT)",
        "description": "Tail key data: Park boost -6% (stadium -16%, weather +10%). Thornton (HR risk -0.32, vs LHB -0.25, vs RHB -0.18). Mlodzinski (HR risk -0.35, vs LHB -0.02, vs RHB -0.60).",
        "rows": [
            row("Esmerlyn Valdez", "R", "+400", 68, "⭐ 🌕 💣", ["vs Thornton"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 99.8 mph EV. Thornton RHB split -0.18, HR risk -0.32. slight split headwind (-0.18); pitcher risk below avg (-0.32).""", blast="high"),
            row("Brett Baty", "L", "+616", 60, "💎", ["vs Mlodzinski"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.9 mph EV. Mlodzinski LHB split -0.02, HR risk -0.35. slight split headwind (-0.02); pitcher risk below avg (-0.35).""", blast="good"),
            row("Francisco Lindor", "S", "+500", 61, "", ["vs Mlodzinski"], """1 HR, 2 near-HR, 98.8 mph EV. Mlodzinski SHB→LHB split -0.02, HR risk -0.35. slight split headwind (-0.02); pitcher risk below avg (-0.35).""", blast="good"),
        ],
    },
    {
        "title": "TB @ SEA - Drew Rasmussen (R, TB) vs Logan Gilbert (R, SEA)",
        "description": "Tail key data: Park boost +5% (stadium +1%, weather +4%). Rasmussen (HR risk -0.14, vs LHB +0.02, vs RHB -0.18). Gilbert (HR risk -0.01, vs LHB +0.09, vs RHB -0.02).",
        "rows": [
            row("Cal Raleigh", "S", "+390", 59, "", ["vs Rasmussen"], """0 HR, 2 near-HR, 92.8 mph EV. Rasmussen SHB→LHB split +0.02, HR risk -0.14. pitcher risk below avg (-0.14).""", blast="good"),
            row("Junior Caminero", "R", "+265", 60, "", ["vs Gilbert"], """1 HR, 2 near-HR, 88.7 mph EV. Gilbert RHB split -0.02, HR risk -0.01. slight split headwind (-0.02); pitcher risk below avg (-0.01).""", blast="good"),
            row("Victor Mesa Jr.", "L", "+585", 58, "", ["vs Gilbert"], """0 HR, 2 near-HR, 86.5 mph EV. Gilbert LHB split +0.09, HR risk -0.01. pitcher risk below avg (-0.01); lighter EV form (86.5 mph).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ PHI - Jose Soriano (R, TOR) vs Zack Wheeler (R, PHI)",
        "description": "Tail key data: Park boost +38% (stadium +15%, weather +23%). Soriano (HR risk -0.90, vs LHB -0.53, vs RHB -0.79). Wheeler (HR risk -0.16, vs LHB +0.10, vs RHB -0.40).",
        "rows": [
            row("Bryce Harper", "L", "+450", 62, "🚀 ⭐", ["vs Soriano"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 102.3 mph EV. Soriano LHB split -0.53, HR risk -0.90. tough split lane (-0.53); pitcher suppresses HR (-0.90).""", blast="good"),
            row("Derek Hill", "R", "N/A", 61, "", ["vs Soriano"], """1 HR, 1 near-HR, 97.3 mph EV. Soriano RHB split -0.79, HR risk -0.90. tough split lane (-0.79); pitcher suppresses HR (-0.90).""", blast="good"),
            row("Luis Arraez", "L", "+1740", 58, "", ["vs Soriano"], """1 HR, 2 near-HR, 91.3 mph EV. Soriano LHB split -0.53, HR risk -0.90. tough split lane (-0.53); pitcher suppresses HR (-0.90).""", blast="good"),
            row("Jesus Sanchez", "L", "+500", 69, "💎", ["vs Wheeler"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.1 mph EV. Wheeler LHB split +0.10, HR risk -0.16. pitcher risk below avg (-0.16).""", blast="good"),
            row("Brandon Valenzuela", "S", "N/A", 71, "", ["vs Wheeler"], """1 HR, 2 near-HR, 92.4 mph EV. Wheeler SHB→LHB split +0.10, HR risk -0.16. pitcher risk below avg (-0.16).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-07")

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

    out = ROOT / '_games-0807.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
