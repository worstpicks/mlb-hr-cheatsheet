#!/usr/bin/env python3
"""Generate games[] block for 2026-06-14 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Andrew Benintendi (L)",
    "Cedric Mullins (L)",
    "Jazz Chisholm Jr. (L)",
    "Joc Pederson (L)",
    "Juan Soto (L)",
    "Lars Nootbaar (L)",
    "Michael Harris II (L)",
    "Nick Kurtz (L)",
    "Riley Greene (L)",
    "Tyler Callihan (L)",
    "Willy Adames (R)",
}

GEMS = {
    "Braden Montgomery (S)",
    "Kazuma Okamoto (R)",
    "Ketel Marte (S)",
    "Patrick Wisdom (R)",
    "Starling Marte (R)",
    "Will Benson (L)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Vaughn (R)": "MIL",
    "Andy Pages (R)": "LAD",
    "Blaze Jordan (R)": "STL",
    "Braden Montgomery (S)": "CWS",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Brandon Valenzuela (S)": "TOR",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Cam Smith (R)": "HOU",
    "Cedric Mullins (L)": "TB",
    "Christian Walker (R)": "HOU",
    "Colson Montgomery (L)": "CWS",
    "Colt Keith (L)": "DET",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "David Fry (R)": "CLE",
    "Daylen Lile (L)": "WSH",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Dominic Smith (L)": "ATL",
    "Edmundo Sosa (R)": "PHI",
    "Ezequiel Tovar (R)": "COL",
    "Heriberto Hernandez (R)": "MIA",
    "Ian Happ (S)": "CHC",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "James Outman (L)": "DET",
    "James Wood (L)": "WSH",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "Joey Ortiz (R)": "MIL",
    "Jonathan Aranda (L)": "TB",
    "Josh Bell (S)": "MIN",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Higashioka (R)": "TEX",
    "Kyle Karros (R)": "COL",
    "Lars Nootbaar (L)": "STL",
    "Lawrence Butler (L)": "ATH",
    "Luis Garcia Jr. (L)": "WSH",
    "Luke Raley (L)": "SEA",
    "Manny Machado (R)": "SD",
    "Marcus Semien (R)": "NYM",
    "Matt Chapman (R)": "SF",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Michael Massey (L)": "KC",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Nick Kurtz (L)": "ATH",
    "Oswald Peraza (R)": "LAA",
    "Patrick Wisdom (R)": "SEA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Riley Greene (L)": "DET",
    "Ryan Waldschmidt (R)": "ARI",
    "Salvador Perez (R)": "KC",
    "Samuel Basallo (L)": "BAL",
    "Seiya Suzuki (R)": "CHC",
    "Shohei Ohtani (L)": "LAD",
    "Starling Marte (R)": "KC",
    "Trey Mancini (R)": "LAA",
    "Tristan Peters (L)": "CWS",
    "Tyler Callihan (L)": "PIT",
    "Will Benson (L)": "CIN",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Xander Bogaerts (R)": "SD",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_RISK_MIN = 0.95

BUM_PITCHERS = {
    "Mikolas",
    "Springs",
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
        "title": "ARI @ CIN - Zac Gallen (R, ARI) vs Andrew Abbott (L, CIN)",
        "description": "Tail key data: Park boost +19% (stadium +13%, weather +6%). Gallen (HR risk 0.36, vs LHB +0.35, vs RHB +0.19). Abbott (HR risk -0.05, vs LHB -0.20, vs RHB +0.15).",
        "rows": [
            row("JJ Bleday", "L", "+357", 80, "🌕 💣", ["vs Gallen"], """2 HR, 2 near-HR, 90.3 mph EV. Gallen LHB split +0.35, HR risk 0.36.""", blast="high"),
            row("Will Benson", "L", "+230", 70, "💎", ["vs Gallen"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 83.8 mph EV. Gallen LHB split +0.35, HR risk 0.36. lighter EV form (83.8 mph).""", blast="good"),
            row("Matt McLain", "R", "+551", 73, "", ["vs Gallen"], """0 HR, 96.8 mph EV. Gallen RHB split +0.19, HR risk 0.36. limited recent HR events.""", blast="good"),
            row("Ketel Marte", "S", "+331", 81, "💎", ["vs Abbott"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 96.6 mph EV. Abbott RHB split +0.15, HR risk -0.05. pitcher risk below avg (-0.05).""", blast="good"),
            row("Corbin Carroll", "L", "+339", 68, "", ["vs Abbott"], """0 HR, 92.2 mph EV. Abbott LHB split -0.20, HR risk -0.05. slight split headwind (-0.20); pitcher risk below avg (-0.05).""", blast="good"),
            row("Ryan Waldschmidt", "R", "+533", 73, "", ["vs Abbott"], """0 HR, 2 near-HR, 92.6 mph EV. Abbott RHB split +0.15, HR risk -0.05. pitcher risk below avg (-0.05).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ NYM - Bryce Elder (R, ATL) vs Freddy Peralta (R, NYM)",
        "description": "Tail key data: Park boost +5% (stadium -2%, weather +6%). Elder (HR risk -0.68, vs LHB -0.77, vs RHB +0.68). Peralta (HR risk 0.13, vs LHB +0.68, vs RHB -1.23).",
        "rows": [
            row("Juan Soto", "L", "N/A", 70, "⭐", ["vs Elder"], """Worst Pickz Favorite. 0 HR, 94.4 mph EV. Elder LHB split -0.77, HR risk -0.68. tough split lane (-0.77); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Marcus Semien", "R", "N/A", 74, "", ["vs Elder"], """1 HR, 1 near-HR, 92.1 mph EV. Elder RHB split +0.68, HR risk -0.68. pitcher suppresses HR (-0.68).""", blast="good"),
            row("Michael Harris II", "L", "N/A", 62, "⭐", ["vs Peralta"], """Worst Pickz Favorite. 0 HR, 84.8 mph EV. Peralta LHB split +0.68, HR risk 0.13. limited recent HR events; lighter EV form (84.8 mph)."""),
            row("Matt Olson", "L", "N/A", 79, "", ["vs Peralta"], """1 HR, 2 near-HR, 95.3 mph EV. Peralta LHB split +0.68, HR risk 0.13.""", blast="good"),
            row("Dominic Smith", "L", "N/A", 62, "", ["vs Peralta"], """0 HR, 80.4 mph EV. Peralta LHB split +0.68, HR risk 0.13. limited recent HR events; lighter EV form (80.4 mph)."""),
        ],
    },
    {
        "title": "CHC @ SF - Colin Rea (R, CHC) vs Logan Webb (R, SF)",
        "description": "Tail key data: Park boost -11% (stadium -15%, weather +4%). Rea (HR risk 0.70, vs LHB -0.22, vs RHB +1.70). Webb (HR risk -1.08, vs LHB -0.63, vs RHB -0.75).",
        "rows": [
            row("Willy Adames", "R", "N/A", 86, "⭐ 🌕 💣", ["vs Rea"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.2 mph EV. Rea RHB split +1.70, HR risk 0.70. park/weather net drag (-11%).""", blast="high"),
            row("Bryce Eldridge", "L", "N/A", 86, "🌕 💣", ["vs Rea"], """2 HR, 3 near-HR, 94.2 mph EV. Rea LHB split -0.22, HR risk 0.70. slight split headwind (-0.22); park/weather net drag (-11%).""", blast="high"),
            row("Matt Chapman", "R", "N/A", 75, "", ["vs Rea"], """1 HR, 2 near-HR, 90.7 mph EV. Rea RHB split +1.70, HR risk 0.70. park/weather net drag (-11%).""", blast="good"),
            row("Ian Happ", "S", "N/A", 86, "🌕 💣", ["vs Webb"], """2 HR, 3 near-HR, 93.6 mph EV. Webb RHB split -0.75, HR risk -1.08. tough split lane (-0.75); pitcher suppresses HR (-1.08).""", blast="high"),
            row("Michael Conforto", "L", "N/A", 67, "", ["vs Webb"], """0 HR, 1 near-HR, 90.6 mph EV. Webb LHB split -0.63, HR risk -1.08. tough split lane (-0.63); pitcher suppresses HR (-1.08)."""),
            row("Seiya Suzuki", "R", "N/A", 75, "", ["vs Webb"], """1 HR, 2 near-HR, 90.8 mph EV. Webb RHB split -0.75, HR risk -1.08. tough split lane (-0.75); pitcher suppresses HR (-1.08).""", blast="good"),
            row("Pete Crow-Armstrong", "L", "N/A", 72, "", ["vs Webb"], """1 HR, 2 near-HR, 88.4 mph EV. Webb LHB split -0.63, HR risk -1.08. tough split lane (-0.63); pitcher suppresses HR (-1.08).""", blast="good"),
        ],
    },
    {
        "title": "COL @ ATH - Tomoyuki Sugano (R, COL) vs Jeffrey Springs 🧤 (L, ATH)",
        "description": "Tail key data: Park boost +88% (stadium +73%, weather +15%). Sugano (HR risk 0.91, vs LHB +1.78, vs RHB -0.47). Springs 🧤 (HR risk 1.32, vs LHB +0.73, vs RHB +1.09).",
        "rows": [
            row("Nick Kurtz", "L", "N/A", 94, "⭐ 🌕 💣", ["vs Sugano"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 98.1 mph EV. Sugano LHB split +1.78, HR risk 0.91.""", blast="high"),
            row("Lawrence Butler", "L", "N/A", 78, "", ["vs Sugano"], """1 HR, 2 near-HR, 93.9 mph EV. Sugano LHB split +1.78, HR risk 0.91.""", blast="good"),
            row("Zack Gelof", "R", "N/A", 74, "", ["vs Sugano"], """1 HR, 3 near-HR, 78.3 mph EV. Sugano RHB split -0.47, HR risk 0.91. tough split lane (-0.47); lighter EV form (78.3 mph).""", blast="good"),
            row("Kyle Karros", "R", "N/A", 70, "", ["vs Springs"], """0 HR, 1 near-HR, 92.5 mph EV. Springs RHB split +1.09, HR risk 1.32. limited recent HR events.""", blast="good"),
            row("Ezequiel Tovar", "R", "N/A", 62, "", ["vs Springs"], """0 HR, 85.5 mph EV. Springs RHB split +1.09, HR risk 1.32. limited recent HR events; lighter EV form (85.5 mph)."""),
        ],
    },
    {
        "title": "DET @ CLE - Casey Mize (R, DET) vs Gavin Williams (R, CLE)",
        "description": "Tail key data: Park boost -5% (stadium -2%, weather -3%). Mize (HR risk -1.48, vs LHB -1.00, vs RHB -0.75). Williams (HR risk 0.84, vs LHB +0.76, vs RHB +0.39).",
        "rows": [
            row("David Fry", "R", "+317", 65, "", ["vs Mize"], """0 HR, 1 near-HR, 89.2 mph EV. Mize RHB split -0.75, HR risk -1.48. tough split lane (-0.75); pitcher suppresses HR (-1.48)."""),
            row("Dillon Dingler", "R", "N/A", 79, "", ["vs Williams"], """1 HR, 3 near-HR, 93.1 mph EV. Williams RHB split +0.39, HR risk 0.84. park/weather net drag (-5%).""", blast="good"),
            row("Riley Greene", "L", "N/A", 94, "⭐ 🌕 💣", ["vs Williams"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 97.5 mph EV. Williams LHB split +0.76, HR risk 0.84. park/weather net drag (-5%).""", blast="high"),
            row("Colt Keith", "L", "N/A", 70, "", ["vs Williams"], """0 HR, 2 near-HR, 90.5 mph EV. Williams LHB split +0.76, HR risk 0.84. park/weather net drag (-5%).""", blast="good"),
            row("James Outman", "L", "N/A", 79, "", ["vs Williams"], """1 HR, 1 near-HR, 97.1 mph EV. Williams LHB split +0.76, HR risk 0.84. park/weather net drag (-5%).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ KC - Spencer Arrighetti (R, HOU) vs Stephen Kolek (R, KC)",
        "description": "Tail key data: Park boost -17% (stadium +12%, weather -29%). Arrighetti (HR risk -1.01, vs LHB -1.08, vs RHB -0.34). Kolek (HR risk -0.99, vs LHB -0.75, vs RHB -0.46).",
        "rows": [
            row("Starling Marte", "R", "N/A", 81, "💎", ["vs Arrighetti"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 99.2 mph EV. Arrighetti RHB split -0.34, HR risk -1.01. slight split headwind (-0.34); pitcher suppresses HR (-1.01).""", blast="good"),
            row("Jac Caglianone", "L", "N/A", 80, "", ["vs Arrighetti"], """1 HR, 1 near-HR, 98.4 mph EV. Arrighetti LHB split -1.08, HR risk -1.01. tough split lane (-1.08); pitcher suppresses HR (-1.01).""", blast="good"),
            row("Michael Massey", "L", "N/A", 83, "🌕 💣", ["vs Arrighetti"], """2 HR, 2 near-HR, 93.1 mph EV. Arrighetti LHB split -1.08, HR risk -1.01. tough split lane (-1.08); pitcher suppresses HR (-1.01).""", blast="high"),
            row("Salvador Perez", "R", "N/A", 72, "", ["vs Arrighetti"], """0 HR, 2 near-HR, 91.8 mph EV. Arrighetti RHB split -0.34, HR risk -1.01. slight split headwind (-0.34); pitcher suppresses HR (-1.01).""", blast="good"),
            row("Yordan Alvarez", "L", "N/A", 88, "🌕 💣", ["vs Kolek"], """2 HR, 3 near-HR, 95.7 mph EV. Kolek LHB split -0.75, HR risk -0.99. tough split lane (-0.75); pitcher suppresses HR (-0.99).""", blast="high"),
            row("Christian Walker", "R", "N/A", 80, "", ["vs Kolek"], """1 HR, 2 near-HR, 96.4 mph EV. Kolek RHB split -0.46, HR risk -0.99. tough split lane (-0.46); pitcher suppresses HR (-0.99).""", blast="good"),
            row("Cam Smith", "R", "N/A", 71, "", ["vs Kolek"], """0 HR, 1 near-HR, 93.0 mph EV. Kolek RHB split -0.46, HR risk -0.99. tough split lane (-0.46); pitcher suppresses HR (-0.99).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ CWS - Emmet Sheehan (R, LAD) vs Erick Fedde (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Sheehan (HR risk 0.66, vs LHB +0.21, vs RHB +0.80). Fedde (HR risk 0.56, vs LHB +0.41, vs RHB +0.45).",
        "rows": [
            row("Colson Montgomery", "L", "+340", 86, "🌕 💣", ["vs Sheehan"], """3 HR, 3 near-HR, 89.9 mph EV. Sheehan LHB split +0.21, HR risk 0.66.""", blast="high"),
            row("Andrew Benintendi", "L", "+412", 98, "⭐ 🌕 💣", ["vs Sheehan"], """Worst Pickz Favorite. 4 HR, 5 near-HR, 94.1 mph EV. Sheehan LHB split +0.21, HR risk 0.66.""", blast="high"),
            row("Tristan Peters", "L", "+990", 72, "", ["vs Sheehan"], """1 HR, 2 near-HR, 87.3 mph EV. Sheehan LHB split +0.21, HR risk 0.66. lighter EV form (87.3 mph).""", blast="good"),
            row("Braden Montgomery", "S", "N/A", 84, "🚀 💎", ["vs Sheehan"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 101.2 mph EV. Sheehan RHB split +0.80, HR risk 0.66.""", blast="good"),
            row("Miguel Vargas", "R", "+399", 79, "🌕 💣", ["vs Sheehan"], """1 HR, 4 near-HR, 89.3 mph EV. Sheehan RHB split +0.80, HR risk 0.66.""", blast="high"),
            row("Shohei Ohtani", "L", "+267", 79, "", ["vs Fedde"], """1 HR, 1 near-HR, 97.3 mph EV. Fedde LHB split +0.41, HR risk 0.56.""", blast="good"),
            row("Andy Pages", "R", "+453", 74, "", ["vs Fedde"], """1 HR, 1 near-HR, 92.4 mph EV. Fedde RHB split +0.45, HR risk 0.56.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ PIT - Max Meyer (R, MIA) vs Paul Skenes (R, PIT)",
        "description": "Tail key data: Park boost -5% (stadium -15%, weather +10%). Meyer (HR risk -0.18, vs LHB -0.37, vs RHB +0.25). Skenes (HR risk -0.99, vs LHB -0.53, vs RHB -0.79).",
        "rows": [
            row("Tyler Callihan", "L", "+840", 84, "⭐ 🌕 💣", ["vs Meyer"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.8 mph EV. Meyer LHB split -0.37, HR risk -0.18. slight split headwind (-0.37); pitcher risk below avg (-0.18).""", blast="high"),
            row("Brandon Lowe", "L", "+385", 84, "🌕 💣", ["vs Meyer"], """2 HR, 3 near-HR, 92.4 mph EV. Meyer LHB split -0.37, HR risk -0.18. slight split headwind (-0.37); pitcher risk below avg (-0.18).""", blast="high"),
            row("Heriberto Hernandez", "R", "+830", 75, "", ["vs Skenes"], """1 HR, 1 near-HR, 93.3 mph EV. Skenes RHB split -0.79, HR risk -0.99. tough split lane (-0.79); pitcher suppresses HR (-0.99).""", blast="good"),
            row("Joe Mack", "L", "+1180", 73, "", ["vs Skenes"], """0 HR, 1 near-HR, 95.3 mph EV. Skenes LHB split -0.53, HR risk -0.99. tough split lane (-0.53); pitcher suppresses HR (-0.99).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ TOR - Will Warren (R, NYY) vs Patrick Corbin (L, TOR)",
        "description": "Tail key data: Park boost -3% (stadium +6%, weather -9%). Warren (HR risk -0.79, vs LHB -0.47, vs RHB -0.43). Corbin (HR risk 0.01, vs LHB -1.19, vs RHB +0.51).",
        "rows": [
            row("Brandon Valenzuela", "S", "+680", 86, "🌕 💣", ["vs Warren"], """2 HR, 4 near-HR, 92.3 mph EV. Warren RHB split -0.43, HR risk -0.79. tough split lane (-0.43); pitcher suppresses HR (-0.79).""", blast="high"),
            row("Kazuma Okamoto", "R", "+370", 77, "💎", ["vs Warren"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.2 mph EV. Warren RHB split -0.43, HR risk -0.79. tough split lane (-0.43); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "+573", 92, "⭐ 🌕 💣", ["vs Corbin"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 98.4 mph EV. Corbin LHB split -1.19, HR risk 0.01. tough split lane (-1.19); weather carry headwind (-9%).""", blast="high"),
        ],
    },
    {
        "title": "PHI @ MIL - Cristopher Sanchez (L, PHI) vs Kyle Harrison (L, MIL)",
        "description": "Tail key data: Park boost +3% (stadium +9%, weather -6%). Sanchez (HR risk -1.16, vs LHB -1.15, vs RHB -0.71). Harrison (HR risk -0.12, vs LHB -0.31, vs RHB -0.01).",
        "rows": [
            row("Andrew Vaughn", "R", "+421", 73, "", ["vs Sanchez"], """0 HR, 1 near-HR, 95.2 mph EV. Sanchez RHB split -0.71, HR risk -1.16. tough split lane (-0.71); pitcher suppresses HR (-1.16).""", blast="good"),
            row("Joey Ortiz", "R", "N/A", 71, "", ["vs Sanchez"], """0 HR, 95.3 mph EV. Sanchez RHB split -0.71, HR risk -1.16. tough split lane (-0.71); pitcher suppresses HR (-1.16).""", blast="good"),
            row("Brandon Marsh", "L", "N/A", 62, "", ["vs Harrison"], """0 HR, 86.6 mph EV. Harrison LHB split -0.31, HR risk -0.12. slight split headwind (-0.31); pitcher risk below avg (-0.12)."""),
            row("Edmundo Sosa", "R", "N/A", 86, "🌕 💣", ["vs Harrison"], """3 HR, 3 near-HR, 90.3 mph EV. Harrison RHB split -0.01, HR risk -0.12. slight split headwind (-0.01); pitcher risk below avg (-0.12).""", blast="high"),
            row("Bryce Harper", "L", "N/A", 76, "🚀", ["vs Harrison"], """0 HR, 100.2 mph EV. Harrison LHB split -0.31, HR risk -0.12. slight split headwind (-0.31); pitcher risk below avg (-0.12).""", blast="good"),
        ],
    },
    {
        "title": "SD @ BAL - Walker Buehler (R, SD) vs Trevor Rogers (L, BAL)",
        "description": "Tail key data: Park boost +3% (stadium -4%, weather +7%). Buehler (HR risk -0.64, vs LHB -0.36, vs RHB -0.49). Rogers (HR risk 0.00, vs LHB -1.09, vs RHB +0.31).",
        "rows": [
            row("Pete Alonso", "R", "+320", 95, "🌕 💣", ["vs Buehler"], """4 HR, 4 near-HR, 92.9 mph EV. Buehler RHB split -0.49, HR risk -0.64. tough split lane (-0.49); pitcher suppresses HR (-0.64).""", blast="high"),
            row("Colton Cowser", "L", "+490", 81, "🌕 💣", ["vs Buehler"], """2 HR, 3 near-HR, 88.7 mph EV. Buehler LHB split -0.36, HR risk -0.64. slight split headwind (-0.36); pitcher suppresses HR (-0.64).""", blast="high"),
            row("Samuel Basallo", "L", "+360", 84, "", ["vs Buehler"], """1 HR, 2 near-HR, 99.8 mph EV. Buehler LHB split -0.36, HR risk -0.64. slight split headwind (-0.36); pitcher suppresses HR (-0.64).""", blast="good"),
            row("Xander Bogaerts", "R", "+470", 71, "", ["vs Rogers"], """0 HR, 1 near-HR, 93.4 mph EV. Rogers RHB split +0.31, HR risk 0.00. limited recent HR events.""", blast="good"),
            row("Manny Machado", "R", "+320", 77, "", ["vs Rogers"], """1 HR, 2 near-HR, 92.8 mph EV. Rogers RHB split +0.31, HR risk 0.00.""", blast="good"),
        ],
    },
    {
        "title": "SEA @ WSH - Emerson Hancock (R, SEA) vs Miles Mikolas 🧤 (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Hancock (HR risk -0.02, vs LHB +0.38, vs RHB -0.47). Mikolas 🧤 (HR risk 0.96, vs LHB +0.48, vs RHB +1.10).",
        "rows": [
            row("James Wood", "L", "+295", 76, "", ["vs Hancock"], """1 HR, 2 near-HR, 92.4 mph EV. Hancock LHB split +0.38, HR risk -0.02. pitcher risk below avg (-0.02).""", blast="good"),
            row("Daylen Lile", "L", "+547", 74, "", ["vs Hancock"], """1 HR, 2 near-HR, 90.5 mph EV. Hancock LHB split +0.38, HR risk -0.02. pitcher risk below avg (-0.02).""", blast="good"),
            row("Luis Garcia Jr.", "L", "+567", 77, "", ["vs Hancock"], """1 HR, 3 near-HR, 91.0 mph EV. Hancock LHB split +0.38, HR risk -0.02. pitcher risk below avg (-0.02).""", blast="good"),
            row("CJ Abrams", "L", "+382", 76, "", ["vs Hancock"], """1 HR, 2 near-HR, 92.2 mph EV. Hancock LHB split +0.38, HR risk -0.02. pitcher risk below avg (-0.02).""", blast="good"),
            row("Dominic Canzone", "L", "+403", 92, "🌕 💣", ["vs Mikolas"], """3 HR, 4 near-HR, 94.5 mph EV. Mikolas LHB split +0.48, HR risk 0.96.""", blast="high"),
            row("Luke Raley", "L", "+298", 77, "", ["vs Mikolas"], """1 HR, 2 near-HR, 93.4 mph EV. Mikolas LHB split +0.48, HR risk 0.96.""", blast="good"),
            row("Patrick Wisdom", "R", "N/A", 66, "💎", ["vs Mikolas"], """Worst Pickz Hidden Gem. 0 HR, 91.8 mph EV. Mikolas RHB split +1.10, HR risk 0.96. limited recent HR events."""),
        ],
    },
    {
        "title": "STL @ MIN - Michael McGreevy (R, STL) vs Taj Bradley (R, MIN)",
        "description": "Tail key data: Park boost +0% (stadium -7%, weather +7%). McGreevy (HR risk 0.29, vs LHB +0.51, vs RHB -0.06). Bradley (HR risk 0.56, vs LHB +0.97, vs RHB -0.49).",
        "rows": [
            row("Josh Bell", "S", "N/A", 87, "🌕 💣", ["vs McGreevy"], """2 HR, 5 near-HR, 90.9 mph EV. McGreevy RHB split -0.06, HR risk 0.29. slight split headwind (-0.06); park suppresses carry (-7%).""", blast="high"),
            row("Byron Buxton", "R", "N/A", 81, "🌕 💣", ["vs McGreevy"], """2 HR, 2 near-HR, 91.0 mph EV. McGreevy RHB split -0.06, HR risk 0.29. slight split headwind (-0.06); park suppresses carry (-7%).""", blast="high"),
            row("Kody Clemens", "L", "N/A", 83, "🌕 💣", ["vs McGreevy"], """2 HR, 2 near-HR, 93.0 mph EV. McGreevy LHB split +0.51, HR risk 0.29. park suppresses carry (-7%).""", blast="high"),
            row("Alec Burleson", "L", "N/A", 96, "⭐ 🌕 💣", ["vs Bradley"], """Worst Pickz Favorite. 4 HR, 4 near-HR, 94.3 mph EV. Bradley LHB split +0.97, HR risk 0.56. park suppresses carry (-7%).""", blast="high"),
            row("Lars Nootbaar", "L", "N/A", 82, "⭐", ["vs Bradley"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.5 mph EV. Bradley LHB split +0.97, HR risk 0.56. park suppresses carry (-7%).""", blast="good"),
            row("Blaze Jordan", "R", "N/A", 82, "🚀", ["vs Bradley"], """1 HR, 1 near-HR, 102.0 mph EV. Bradley RHB split -0.49, HR risk 0.56. tough split lane (-0.49); park suppresses carry (-7%).""", blast="good"),
        ],
    },
    {
        "title": "TB @ LAA - Ian Seymour (L, TB) vs Grayson Rodriguez (R, LAA)",
        "description": "Tail key data: Park boost +4% (stadium +7%, weather -3%). Away starter risk unavailable. Rodriguez (HR risk 0.80, vs LHB +1.48, vs RHB -0.49).",
        "rows": [
            row("Oswald Peraza", "R", "N/A", 76, "", ["vs Seymour"], """1 HR, 1 near-HR, 94.3 mph EV. Seymour split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Trey Mancini", "R", "N/A", 78, "🚀", ["vs Seymour"], """0 HR, 1 near-HR, 102.7 mph EV. Seymour split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Mike Trout", "R", "N/A", 74, "", ["vs Seymour"], """1 HR, 1 near-HR, 91.9 mph EV. Seymour split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Zach Neto", "R", "N/A", 70, "", ["vs Seymour"], """1 HR, 1 near-HR, 87.0 mph EV. Seymour split/risk data unavailable. limited split/risk sample; lighter EV form (87.0 mph).""", blast="good"),
            row("Cedric Mullins", "L", "N/A", 88, "⭐ 🌕 💣", ["vs Rodriguez"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 93.5 mph EV. Rodriguez LHB split +1.48, HR risk 0.80.""", blast="high"),
            row("Jonathan Aranda", "L", "N/A", 74, "", ["vs Rodriguez"], """1 HR, 1 near-HR, 92.3 mph EV. Rodriguez LHB split +1.48, HR risk 0.80.""", blast="good"),
            row("Junior Caminero", "R", "N/A", 64, "", ["vs Rodriguez"], """0 HR, 90.3 mph EV. Rodriguez RHB split -0.49, HR risk 0.80. tough split lane (-0.49); limited recent HR events."""),
        ],
    },
    {
        "title": "TEX @ BOS - Nathan Eovaldi (R, TEX) vs Connelly Early (L, BOS)",
        "description": "Tail key data: Park boost +7% (stadium -7%, weather +15%). Eovaldi (HR risk 0.39, vs LHB +0.49, vs RHB -0.03). Early (HR risk 0.69, vs LHB +0.88, vs RHB +0.35).",
        "rows": [
            row("Wilyer Abreu", "L", "+390", 87, "🌕 💣", ["vs Eovaldi"], """2 HR, 3 near-HR, 95.3 mph EV. Eovaldi LHB split +0.49, HR risk 0.39. park suppresses carry (-7%).""", blast="high"),
            row("Willson Contreras", "R", "+410", 80, "🌕 💣", ["vs Eovaldi"], """2 HR, 3 near-HR, 87.9 mph EV. Eovaldi RHB split -0.03, HR risk 0.39. slight split headwind (-0.03); park suppresses carry (-7%).""", blast="high"),
            row("Kyle Higashioka", "R", "+492", 74, "", ["vs Early"], """1 HR, 2 near-HR, 90.5 mph EV. Early RHB split +0.35, HR risk 0.69. park suppresses carry (-7%).""", blast="good"),
            row("Justin Foscue", "R", "+650", 81, "", ["vs Early"], """1 HR, 2 near-HR, 96.9 mph EV. Early RHB split +0.35, HR risk 0.69. park suppresses carry (-7%).""", blast="good"),
            row("Joc Pederson", "L", "N/A", 83, "⭐", ["vs Early"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 98.6 mph EV. Early LHB split +0.88, HR risk 0.69. park suppresses carry (-7%).""", blast="good"),
            row("Corey Seager", "L", "+458", 74, "", ["vs Early"], """0 HR, 98.4 mph EV. Early LHB split +0.88, HR risk 0.69. park suppresses carry (-7%); limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-14")

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

    out = ROOT / '_games-0614.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
