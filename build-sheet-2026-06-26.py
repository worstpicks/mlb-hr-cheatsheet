#!/usr/bin/env python3
"""Generate games[] block for 2026-06-26 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Bo Bichette (R)",
    "Dominic Canzone (L)",
    "Hunter Goodman (R)",
    "Jac Caglianone (L)",
    "Jake Bauers (L)",
    "James Wood (L)",
    "Joe Mack (L)",
    "Junior Caminero (R)",
    "Ketel Marte (S)",
    "Kyle Higashioka (R)",
    "Kyle Schwarber (L)",
    "Matt McLain (R)",
    "Max Muncy (R)",
    "Nick Kurtz (L)",
    "Pete Crow-Armstrong (L)",
    "Rafael Devers (L)",
    "Shohei Ohtani (L)",
    "Travis Bazzana (L)",
    "Victor Bericoto (R)",
    "Willi Castro (S)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Henry Davis (R)",
    "Juan Soto (L)",
    "Kahlil Watson (L)",
    "Max Muncy (R)",
    "Nate Eaton (R)",
    "Ty France (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Bo Bichette (R)": "NYM",
    "Braden Montgomery (S)": "CWS",
    "Brandon Lowe (L)": "PIT",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Cam Smith (R)": "HOU",
    "Carson Kelly (R)": "CHC",
    "Carter Jensen (L)": "KC",
    "Casey Schmitt (R)": "SF",
    "Coby Mayo (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "Dansby Swanson (R)": "CHC",
    "Derek Hill (R)": "PHI",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Henry Davis (R)": "PIT",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "TB",
    "Hunter Goodman (R)": "COL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "James Wood (L)": "WSH",
    "Jesus Sanchez (L)": "TOR",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "Jonathan Aranda (L)": "TB",
    "Jorge Soler (R)": "LAA",
    "Josh Naylor (L)": "SEA",
    "Josh Rojas (L)": "KC",
    "Juan Soto (L)": "NYM",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Kahlil Watson (L)": "CLE",
    "Kazuma Okamoto (R)": "TOR",
    "Kerry Carpenter (L)": "DET",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Higashioka (R)": "TEX",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lars Nootbaar (L)": "STL",
    "Matt McLain (R)": "CIN",
    "Max Muncy (L)": "LAD",
    "Max Muncy (R)": "ATH",
    "Max Schuemann (R)": "NYY",
    "Michael Harris II (L)": "ATL",
    "Miguel Amaya (R)": "CHC",
    "Mike Yastrzemski (L)": "ATL",
    "Mookie Betts (R)": "LAD",
    "Nate Eaton (R)": "BOS",
    "Nick Kurtz (L)": "ATH",
    "Nick Loftin (R)": "KC",
    "Nolan Arenado (R)": "ARI",
    "Otto Lopez (R)": "MIA",
    "Owen Caissie (L)": "MIA",
    "Paul Goldschmidt (R)": "NYY",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Ryan O'Hearn (L)": "PIT",
    "Ryan Vilade (R)": "KC",
    "Sal Stewart (R)": "CIN",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Steer (R)": "CIN",
    "Spencer Torkelson (R)": "DET",
    "TJ Rumfield (L)": "COL",
    "Taylor Trammell (L)": "HOU",
    "Taylor Ward (R)": "BAL",
    "Travis Bazzana (L)": "CLE",
    "Ty France (R)": "SD",
    "Tyler Soderstrom (L)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "Victor Bericoto (R)": "SF",
    "Victor Mesa Jr. (L)": "TB",
    "Willi Castro (S)": "COL",
    "William Contreras (R)": "MIL",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("COL @ MIN", "Bradley"),
    ("COL @ MIN", "Sugano"),
    ("KC @ CWS", "Cruz"),
    ("KC @ CWS", "Sandlin"),
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
        "title": "ARI @ TB - Zac Gallen (R, ARI) vs Nick Martinez (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Gallen (HR risk 0.48, vs LHB +0.45, vs RHB +0.37). Martinez (HR risk -0.34, vs LHB -0.18, vs RHB -0.23).",
        "rows": [
            row("Junior Caminero", "R", "+291", 89, "⭐ 🌕 💣", ["vs Gallen"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 96.8 mph EV. Gallen RHB split +0.37, HR risk 0.48.""", blast="high"),
            row("Jonathan Aranda", "L", "+430", 76, "", ["vs Gallen"], """1 HR, 1 near-HR, 94.5 mph EV. Gallen LHB split +0.45, HR risk 0.48.""", blast="good"),
            row("Hunter Feduccia", "L", "+1000", 72, "", ["vs Gallen"], """0 HR, 96.3 mph EV. Gallen LHB split +0.45, HR risk 0.48. limited recent HR events.""", blast="good"),
            row("Victor Mesa Jr.", "L", "N/A", 79, "", ["vs Gallen"], """1 HR, 2 near-HR, 94.9 mph EV. Gallen LHB split +0.45, HR risk 0.48.""", blast="good"),
            row("Nolan Arenado", "R", "+630", 62, "", ["vs Martinez"], """0 HR, 87.5 mph EV. Martinez RHB split -0.23, HR risk -0.34. slight split headwind (-0.23); pitcher risk below avg (-0.34)."""),
            row("Ketel Marte", "S", "+395", 71, "⭐", ["vs Martinez"], """Worst Pickz Favorite. 0 HR, 94.6 mph EV. Martinez RHB split -0.23, HR risk -0.34. slight split headwind (-0.23); pitcher risk below avg (-0.34).""", blast="good"),
            row("Corbin Carroll", "L", "+390", 66, "", ["vs Martinez"], """0 HR, 1 near-HR, 90.1 mph EV. Martinez LHB split -0.18, HR risk -0.34. slight split headwind (-0.18); pitcher risk below avg (-0.34)."""),
        ],
    },
    {
        "title": "ATH @ LAA - J.T. Ginn (R, ATH) vs Walbert Urena (R, LAA)",
        "description": "Tail key data: Park boost +9% (stadium +9%, weather +0%). Ginn (HR risk -0.62, vs LHB -0.28, vs RHB -0.67). Urena (HR risk -0.92, vs LHB -0.66, vs RHB -0.66).",
        "rows": [
            row("Zach Neto", "R", "+390", 75, "", ["vs Ginn"], """1 HR, 2 near-HR, 91.2 mph EV. Ginn RHB split -0.67, HR risk -0.62. tough split lane (-0.67); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Jorge Soler", "R", "+443", 70, "", ["vs Ginn"], """1 HR, 1 near-HR, 87.0 mph EV. Ginn RHB split -0.67, HR risk -0.62. tough split lane (-0.67); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Nick Kurtz", "L", "+347", 77, "⭐", ["vs Urena"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.7 mph EV. Urena LHB split -0.66, HR risk -0.92. tough split lane (-0.66); pitcher suppresses HR (-0.92).""", blast="good"),
            row("Tyler Soderstrom", "L", "+549", 81, "🌕 💣", ["vs Urena"], """2 HR, 2 near-HR, 91.4 mph EV. Urena LHB split -0.66, HR risk -0.92. tough split lane (-0.66); pitcher suppresses HR (-0.92).""", blast="high"),
            row("Max Muncy", "R", "+725", 80, "⭐ 🌕 💣 💎", ["vs Urena"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 88.0 mph EV. Urena RHB split -0.66, HR risk -0.92. tough split lane (-0.66); pitcher suppresses HR (-0.92).""", blast="high"),
        ],
    },
    {
        "title": "ATL @ SF - Reynaldo Lopez (R, ATL) vs Trevor McDonald (R, SF)",
        "description": "Tail key data: Park boost -20% (stadium -17%, weather -3%). Lopez (HR risk -0.99, vs LHB -0.82, vs RHB -0.01). Home starter risk unavailable.",
        "rows": [
            row("Rafael Devers", "L", "+517", 88, "⭐ 🌕 💣", ["vs Lopez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.9 mph EV. Lopez LHB split -0.82, HR risk -0.99. tough split lane (-0.82); pitcher suppresses HR (-0.99).""", blast="high"),
            row("Bryce Eldridge", "L", "+625", 86, "🌕 💣", ["vs Lopez"], """2 HR, 2 near-HR, 96.1 mph EV. Lopez LHB split -0.82, HR risk -0.99. tough split lane (-0.82); pitcher suppresses HR (-0.99).""", blast="high"),
            row("Victor Bericoto", "R", "+900", 90, "🚀 ⭐ 🌕 💣", ["vs Lopez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 108.7 mph EV. Lopez RHB split -0.01, HR risk -0.99. slight split headwind (-0.01); pitcher suppresses HR (-0.99).""", blast="high"),
            row("Willy Adames", "R", "+555", 78, "🌕 💣", ["vs Lopez"], """2 HR, 2 near-HR, 87.1 mph EV. Lopez RHB split -0.01, HR risk -0.99. slight split headwind (-0.01); pitcher suppresses HR (-0.99).""", blast="high"),
            row("Casey Schmitt", "R", "+550", 76, "", ["vs Lopez"], """0 HR, 2 near-HR, 95.6 mph EV. Lopez RHB split -0.01, HR risk -0.99. slight split headwind (-0.01); pitcher suppresses HR (-0.99).""", blast="good"),
            row("Mike Yastrzemski", "L", "+860", 70, "", ["vs McDonald"], """1 HR, 1 near-HR, 88.0 mph EV. McDonald split/risk data unavailable. limited split/risk sample; park/weather net drag (-20%).""", blast="good"),
            row("Michael Harris II", "L", "+610", 70, "", ["vs McDonald"], """0 HR, 1 near-HR, 92.0 mph EV. McDonald split/risk data unavailable. limited split/risk sample; park/weather net drag (-20%).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ MIL - Colin Rea (R, CHC) vs Jacob Misiorowski (R, MIL)",
        "description": "Tail key data: Park boost +1% (stadium +10%, weather -9%). Rea (HR risk 0.39, vs LHB -0.33, vs RHB +1.56). Misiorowski (HR risk -1.62, vs LHB -0.96, vs RHB -1.54).",
        "rows": [
            row("Jake Bauers", "L", "+374", 82, "🚀 ⭐", ["vs Rea"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 102.6 mph EV. Rea LHB split -0.33, HR risk 0.39. slight split headwind (-0.33); weather carry headwind (-9%).""", blast="good"),
            row("William Contreras", "R", "+564", 88, "🌕 💣", ["vs Rea"], """2 HR, 3 near-HR, 96.0 mph EV. Rea RHB split +1.56, HR risk 0.39. weather carry headwind (-9%).""", blast="high"),
            row("Jackson Chourio", "R", "+390", 69, "", ["vs Rea"], """0 HR, 92.7 mph EV. Rea RHB split +1.56, HR risk 0.39. weather carry headwind (-9%); limited recent HR events.""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+521", 93, "⭐ 🌕 💣", ["vs Misiorowski"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 96.9 mph EV. Misiorowski LHB split -0.96, HR risk -1.62. tough split lane (-0.96); pitcher suppresses HR (-1.62).""", blast="high"),
            row("Miguel Amaya", "R", "N/A", 70, "", ["vs Misiorowski"], """0 HR, 2 near-HR, 90.4 mph EV. Misiorowski RHB split -1.54, HR risk -1.62. tough split lane (-1.54); pitcher suppresses HR (-1.62).""", blast="good"),
            row("Carson Kelly", "R", "+1280", 78, "", ["vs Misiorowski"], """1 HR, 1 near-HR, 96.0 mph EV. Misiorowski RHB split -1.54, HR risk -1.62. tough split lane (-1.54); pitcher suppresses HR (-1.62).""", blast="good"),
            row("Dansby Swanson", "R", "+1100", 79, "", ["vs Misiorowski"], """1 HR, 1 near-HR, 96.7 mph EV. Misiorowski RHB split -1.54, HR risk -1.62. tough split lane (-1.54); pitcher suppresses HR (-1.62).""", blast="good"),
        ],
    },
    {
        "title": "CIN @ PIT - Andrew Abbott (L, CIN) vs Paul Skenes (R, PIT)",
        "description": "Tail key data: Park boost -6% (stadium -15%, weather +10%). Abbott (HR risk 0.24, vs LHB -0.28, vs RHB +0.67). Skenes (HR risk -0.52, vs LHB -0.22, vs RHB -0.56).",
        "rows": [
            row("Henry Davis", "R", "+357", 68, "💎", ["vs Abbott"], """Worst Pickz Hidden Gem. 0 HR, 92.4 mph EV. Abbott RHB split +0.67, HR risk 0.24. park/weather net drag (-6%); limited recent HR events.""", blast="good"),
            row("Bryan Reynolds", "S", "+291", 78, "🌕 💣", ["vs Abbott"], """2 HR, 2 near-HR, 87.9 mph EV. Abbott RHB split +0.67, HR risk 0.24. park/weather net drag (-6%); lighter EV form (87.9 mph).""", blast="high"),
            row("Ryan O'Hearn", "L", "+351", 70, "", ["vs Abbott"], """1 HR, 1 near-HR, 84.5 mph EV. Abbott LHB split -0.28, HR risk 0.24. slight split headwind (-0.28); park/weather net drag (-6%).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+431", 74, "", ["vs Abbott"], """0 HR, 97.6 mph EV. Abbott RHB split +0.67, HR risk 0.24. park/weather net drag (-6%); limited recent HR events.""", blast="good"),
            row("Brandon Lowe", "L", "+207", 62, "", ["vs Abbott"], """0 HR, 74.9 mph EV. Abbott LHB split -0.28, HR risk 0.24. slight split headwind (-0.28); park/weather net drag (-6%)."""),
            row("Matt McLain", "R", "+577", 73, "⭐", ["vs Skenes"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.2 mph EV. Skenes RHB split -0.56, HR risk -0.52. tough split lane (-0.56); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Spencer Steer", "R", "+424", 89, "🌕 💣", ["vs Skenes"], """3 HR, 4 near-HR, 90.7 mph EV. Skenes RHB split -0.56, HR risk -0.52. tough split lane (-0.56); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Elly De La Cruz", "S", "+282", 78, "", ["vs Skenes"], """1 HR, 1 near-HR, 95.7 mph EV. Skenes RHB split -0.56, HR risk -0.52. tough split lane (-0.56); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Sal Stewart", "R", "+364", 77, "", ["vs Skenes"], """1 HR, 3 near-HR, 90.9 mph EV. Skenes RHB split -0.56, HR risk -0.52. tough split lane (-0.56); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Tyler Stephenson", "R", "+443", 77, "", ["vs Skenes"], """1 HR, 1 near-HR, 95.4 mph EV. Skenes RHB split -0.56, HR risk -0.52. tough split lane (-0.56); pitcher suppresses HR (-0.52).""", blast="good"),
        ],
    },
    {
        "title": "COL @ MIN - Tomoyuki Sugano 🧤 (R, COL) vs Taj Bradley 🧤 (R, MIN)",
        "description": "Tail key data: Park boost -10% (stadium -7%, weather -3%). Sugano 🧤 (HR risk 0.97, vs LHB +1.10, vs RHB +0.03). Bradley 🧤 (HR risk 1.19, vs LHB +1.62, vs RHB -0.66).",
        "rows": [
            row("Byron Buxton", "R", "+265", 82, "🌕 💣", ["vs Sugano"], """2 HR, 3 near-HR, 90.2 mph EV. Sugano RHB split +0.03, HR risk 0.97. park/weather net drag (-10%).""", blast="high"),
            row("Kody Clemens", "L", "+353", 77, "", ["vs Sugano"], """1 HR, 3 near-HR, 90.9 mph EV. Sugano LHB split +1.10, HR risk 0.97. park/weather net drag (-10%).""", blast="good"),
            row("Hunter Goodman", "R", "+310", 89, "⭐ 🌕 💣", ["vs Bradley"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 97.2 mph EV. Bradley RHB split -0.66, HR risk 1.19. tough split lane (-0.66); park/weather net drag (-10%).""", blast="high"),
            row("Willi Castro", "S", "+625", 85, "⭐ 🌕 💣", ["vs Bradley"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.1 mph EV. Bradley RHB split -0.66, HR risk 1.19. tough split lane (-0.66); park/weather net drag (-10%).""", blast="high"),
            row("TJ Rumfield", "L", "+600", 70, "", ["vs Bradley"], """1 HR, 1 near-HR, 84.2 mph EV. Bradley LHB split +1.62, HR risk 1.19. park/weather net drag (-10%); lighter EV form (84.2 mph).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ DET - Spencer Arrighetti (R, HOU) vs Keider Montero (R, DET)",
        "description": "Tail key data: Park boost -12% (stadium -11%, weather -1%). Arrighetti (HR risk -0.07, vs LHB -0.12, vs RHB +0.13). Montero (HR risk -0.42, vs LHB -0.32, vs RHB -0.18).",
        "rows": [
            row("Spencer Torkelson", "R", "N/A", 84, "🌕 💣", ["vs Arrighetti"], """2 HR, 2 near-HR, 93.6 mph EV. Arrighetti RHB split +0.13, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-12%).""", blast="high"),
            row("Dillon Dingler", "R", "N/A", 82, "🌕 💣", ["vs Arrighetti"], """2 HR, 3 near-HR, 89.8 mph EV. Arrighetti RHB split +0.13, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-12%).""", blast="high"),
            row("Kerry Carpenter", "L", "N/A", 81, "", ["vs Arrighetti"], """1 HR, 2 near-HR, 96.7 mph EV. Arrighetti LHB split -0.12, HR risk -0.07. slight split headwind (-0.12); pitcher risk below avg (-0.07).""", blast="good"),
            row("Taylor Trammell", "L", "N/A", 77, "", ["vs Montero"], """1 HR, 1 near-HR, 94.6 mph EV. Montero LHB split -0.32, HR risk -0.42. slight split headwind (-0.32); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Yordan Alvarez", "L", "N/A", 66, "⭐", ["vs Montero"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 89.5 mph EV. Montero LHB split -0.32, HR risk -0.42. slight split headwind (-0.32); pitcher suppresses HR (-0.42)."""),
            row("Cam Smith", "R", "N/A", 75, "", ["vs Montero"], """1 HR, 2 near-HR, 90.9 mph EV. Montero RHB split -0.18, HR risk -0.42. slight split headwind (-0.18); pitcher suppresses HR (-0.42).""", blast="good"),
        ],
    },
    {
        "title": "KC @ CWS - Steven Cruz 🧤 (L, KC) vs David Sandlin 🧤 (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Cruz 🧤 (HR risk 1.06, vs LHB +0.83, vs RHB +0.47). Sandlin 🧤 (HR risk 1.87, vs LHB +2.37, vs RHB -0.61).",
        "rows": [
            row("Ryan Vilade", "R", "N/A", 76, "", ["vs Sandlin"], """1 HR, 1 near-HR, 90.8 mph EV, 8.3% barrels. Sandlin RHB split -0.61, HR risk 1.87. tough split lane (-0.61).""", blast="good"),
            row("Braden Montgomery", "S", "+750", 72, "", ["vs Cruz"], """1 HR, 1 near-HR, 90.3 mph EV. Cruz RHB split +0.47, HR risk 1.06.""", blast="good"),
            row("Colson Montgomery", "L", "+324", 72, "", ["vs Cruz"], """0 HR, 1 near-HR, 93.9 mph EV. Cruz LHB split +0.83, HR risk 1.06. limited recent HR events.""", blast="good"),
            row("Jac Caglianone", "L", "+400", 88, "⭐ 🌕 💣", ["vs Sandlin"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.4 mph EV. Sandlin LHB split +2.37, HR risk 1.87.""", blast="high"),
            row("Josh Rojas", "L", "N/A", 72, "", ["vs Sandlin"], """0 HR, 95.6 mph EV. Sandlin LHB split +2.37, HR risk 1.87. limited recent HR events.""", blast="good"),
            row("Carter Jensen", "L", "+470", 71, "", ["vs Sandlin"], """1 HR, 1 near-HR, 89.3 mph EV. Sandlin LHB split +2.37, HR risk 1.87.""", blast="good"),
            row("Nick Loftin", "R", "+940", 76, "", ["vs Sandlin"], """1 HR, 1 near-HR, 94.0 mph EV. Sandlin RHB split -0.61, HR risk 1.87. tough split lane (-0.61).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ SD - Roki Sasaki (R, LAD) vs Walker Buehler (R, SD)",
        "description": "Tail key data: Park boost -7% (stadium -5%, weather -2%). Sasaki (HR risk 0.59, vs LHB +0.28, vs RHB +0.77). Buehler (HR risk -0.49, vs LHB -0.81, vs RHB +0.28).",
        "rows": [
            row("Ty France", "R", "+700", 80, "🌕 💣 💎", ["vs Sasaki"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 89.9 mph EV. Sasaki RHB split +0.77, HR risk 0.59. park/weather net drag (-7%).""", blast="high"),
            row("Jackson Merrill", "L", "+470", 69, "", ["vs Sasaki"], """0 HR, 2 near-HR, 89.0 mph EV. Sasaki LHB split +0.28, HR risk 0.59. park/weather net drag (-7%).""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+475", 76, "", ["vs Sasaki"], """0 HR, 1 near-HR, 97.5 mph EV. Sasaki RHB split +0.77, HR risk 0.59. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
            row("Shohei Ohtani", "L", "+270", 98, "⭐ 🌕 💣", ["vs Buehler"], """Worst Pickz Favorite. 4 HR, 4 near-HR, 98.6 mph EV. Buehler LHB split -0.81, HR risk -0.49. tough split lane (-0.81); pitcher suppresses HR (-0.49).""", blast="high"),
            row("Max Muncy", "L", "+375", 66, "", ["vs Buehler"], """0 HR, 1 near-HR, 89.9 mph EV. Buehler LHB split -0.81, HR risk -0.49. tough split lane (-0.81); pitcher suppresses HR (-0.49)."""),
            row("Mookie Betts", "R", "+600", 85, "🌕 💣", ["vs Buehler"], """3 HR, 3 near-HR, 89.0 mph EV. Buehler RHB split +0.28, HR risk -0.49. pitcher suppresses HR (-0.49); park/weather net drag (-7%).""", blast="high"),
            row("Dalton Rushing", "L", "+575", 69, "", ["vs Buehler"], """0 HR, 92.8 mph EV. Buehler LHB split -0.81, HR risk -0.49. tough split lane (-0.81); pitcher suppresses HR (-0.49).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ STL - Max Meyer (R, MIA) vs Michael McGreevy (R, STL)",
        "description": "Tail key data: Park boost -8% (stadium -10%, weather +2%). Meyer (HR risk 0.08, vs LHB -0.55, vs RHB +1.21). McGreevy (HR risk 0.25, vs LHB +0.24, vs RHB +0.16).",
        "rows": [
            row("Lars Nootbaar", "L", "+650", 75, "", ["vs Meyer"], """0 HR, 2 near-HR, 94.9 mph EV. Meyer LHB split -0.55, HR risk 0.08. tough split lane (-0.55); park/weather net drag (-8%).""", blast="good"),
            row("Alec Burleson", "L", "+520", 72, "", ["vs Meyer"], """0 HR, 1 near-HR, 94.0 mph EV. Meyer LHB split -0.55, HR risk 0.08. tough split lane (-0.55); park/weather net drag (-8%).""", blast="good"),
            row("Owen Caissie", "L", "+560", 87, "🌕 💣", ["vs McGreevy"], """3 HR, 4 near-HR, 88.6 mph EV. McGreevy LHB split +0.24, HR risk 0.25. park/weather net drag (-8%).""", blast="high"),
            row("Heriberto Hernandez", "R", "+587", 77, "", ["vs McGreevy"], """1 HR, 1 near-HR, 94.6 mph EV. McGreevy RHB split +0.16, HR risk 0.25. park/weather net drag (-8%).""", blast="good"),
            row("Joe Mack", "L", "+920", 85, "⭐ 🌕 💣", ["vs McGreevy"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.6 mph EV. McGreevy LHB split +0.24, HR risk 0.25. park/weather net drag (-8%).""", blast="high"),
            row("Otto Lopez", "R", "+850", 63, "", ["vs McGreevy"], """0 HR, 88.9 mph EV. McGreevy RHB split +0.16, HR risk 0.25. park/weather net drag (-8%); limited recent HR events."""),
            row("Kyle Stowers", "L", "+407", 71, "", ["vs McGreevy"], """1 HR, 1 near-HR, 88.6 mph EV. McGreevy LHB split +0.24, HR risk 0.25. park/weather net drag (-8%).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ BOS - Will Warren (R, NYY) vs Payton Tolle (L, BOS)",
        "description": "Tail key data: Park boost +8% (stadium -8%, weather +16%). Warren (HR risk -0.41, vs LHB -0.53, vs RHB +0.26). Tolle (HR risk -0.15, vs LHB +0.41, vs RHB -0.46).",
        "rows": [
            row("Willson Contreras", "R", "+430", 69, "", ["vs Warren"], """0 HR, 93.1 mph EV. Warren RHB split +0.26, HR risk -0.41. pitcher suppresses HR (-0.41); park suppresses carry (-8%).""", blast="good"),
            row("Nate Eaton", "R", "N/A", 77, "💎", ["vs Warren"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.1 mph EV. Warren RHB split +0.26, HR risk -0.41. pitcher suppresses HR (-0.41); park suppresses carry (-8%).""", blast="good"),
            row("Paul Goldschmidt", "R", "+421", 78, "🌕 💣", ["vs Tolle"], """2 HR, 2 near-HR, 86.8 mph EV. Tolle RHB split -0.46, HR risk -0.15. tough split lane (-0.46); pitcher risk below avg (-0.15).""", blast="high"),
            row("Max Schuemann", "R", "N/A", 64, "", ["vs Tolle"], """0 HR, 90.4 mph EV. Tolle RHB split -0.46, HR risk -0.15. tough split lane (-0.46); pitcher risk below avg (-0.15)."""),
        ],
    },
    {
        "title": "PHI @ NYM - Zack Wheeler (R, PHI) vs Zach Thornton (L, NYM)",
        "description": "Tail key data: Park boost +15% (stadium -1%, weather +16%). Wheeler (HR risk 0.22, vs LHB +0.56, vs RHB -0.43). Home starter risk unavailable.",
        "rows": [
            row("Bo Bichette", "R", "+890", 82, "⭐ 🌕 💣", ["vs Wheeler"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.9 mph EV. Wheeler RHB split -0.43, HR risk 0.22. tough split lane (-0.43).""", blast="high"),
            row("Juan Soto", "L", "+342", 86, "🌕 💣 💎", ["vs Wheeler"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.0 mph EV. Wheeler LHB split +0.56, HR risk 0.22.""", blast="high"),
            row("Francisco Lindor", "S", "+480", 87, "🌕 💣", ["vs Wheeler"], """2 HR, 2 near-HR, 96.6 mph EV. Wheeler RHB split -0.43, HR risk 0.22. tough split lane (-0.43).""", blast="high"),
            row("Francisco Alvarez", "R", "+563", 81, "🌕 💣", ["vs Wheeler"], """2 HR, 2 near-HR, 90.8 mph EV. Wheeler RHB split -0.43, HR risk 0.22. tough split lane (-0.43).""", blast="high"),
            row("Kyle Schwarber", "L", "+291", 89, "⭐ 🌕 💣", ["vs Thornton"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 90.7 mph EV. Thornton split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Derek Hill", "R", "+800", 78, "", ["vs Thornton"], """1 HR, 1 near-HR, 95.7 mph EV. Thornton split/risk data unavailable. limited split/risk sample.""", blast="good"),
        ],
    },
    {
        "title": "SEA @ CLE - Luis Castillo (R, SEA) vs Joey Cantillo (L, CLE)",
        "description": "Tail key data: Park boost -5% (stadium -2%, weather -3%). Castillo (HR risk -0.35, vs LHB +0.34, vs RHB -1.36). Cantillo (HR risk 0.50, vs LHB +0.18, vs RHB +0.70).",
        "rows": [
            row("Travis Bazzana", "L", "+630", 89, "⭐ 🌕 💣", ["vs Castillo"], """Worst Pickz Favorite. 2 HR, 5 near-HR, 92.8 mph EV. Castillo LHB split +0.34, HR risk -0.35. pitcher risk below avg (-0.35); park/weather net drag (-5%).""", blast="high"),
            row("Kahlil Watson", "L", "+640", 82, "🚀 💎", ["vs Castillo"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 100.2 mph EV. Castillo LHB split +0.34, HR risk -0.35. pitcher risk below avg (-0.35); park/weather net drag (-5%).""", blast="good"),
            row("Kyle Manzardo", "L", "+423", 78, "", ["vs Castillo"], """1 HR, 2 near-HR, 93.7 mph EV. Castillo LHB split +0.34, HR risk -0.35. pitcher risk below avg (-0.35); park/weather net drag (-5%).""", blast="good"),
            row("Dominic Canzone", "L", "N/A", 78, "⭐", ["vs Cantillo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.0 mph EV. Cantillo LHB split +0.18, HR risk 0.50. park/weather net drag (-5%).""", blast="good"),
            row("Julio Rodriguez", "R", "+500", 73, "", ["vs Cantillo"], """0 HR, 1 near-HR, 94.8 mph EV. Cantillo RHB split +0.70, HR risk 0.50. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
            row("Josh Naylor", "L", "+750", 62, "", ["vs Cantillo"], """0 HR, 78.6 mph EV. Cantillo LHB split +0.18, HR risk 0.50. park/weather net drag (-5%); limited recent HR events."""),
        ],
    },
    {
        "title": "TEX @ TOR - Nathan Eovaldi (R, TEX) vs Patrick Corbin (L, TOR)",
        "description": "Tail key data: Park boost +5% (stadium +6%, weather -1%). Eovaldi (HR risk 0.46, vs LHB +0.20, vs RHB +0.75). Corbin (HR risk 0.08, vs LHB -0.94, vs RHB +0.88).",
        "rows": [
            row("Kazuma Okamoto", "R", "N/A", 87, "🌕 💣", ["vs Eovaldi"], """3 HR, 3 near-HR, 91.3 mph EV. Eovaldi RHB split +0.75, HR risk 0.46.""", blast="high"),
            row("Jesus Sanchez", "L", "N/A", 74, "", ["vs Eovaldi"], """1 HR, 1 near-HR, 92.4 mph EV. Eovaldi LHB split +0.20, HR risk 0.46.""", blast="good"),
            row("Kyle Higashioka", "R", "N/A", 87, "⭐ 🌕 💣", ["vs Corbin"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.2 mph EV. Corbin RHB split +0.88, HR risk 0.08.""", blast="high"),
            row("Wyatt Langford", "R", "N/A", 70, "", ["vs Corbin"], """1 HR, 1 near-HR, 82.2 mph EV. Corbin RHB split +0.88, HR risk 0.08. lighter EV form (82.2 mph).""", blast="good"),
            row("Jake Burger", "R", "N/A", 70, "", ["vs Corbin"], """1 HR, 1 near-HR, 88.4 mph EV. Corbin RHB split +0.88, HR risk 0.08.""", blast="good"),
            row("Joc Pederson", "L", "N/A", 74, "", ["vs Corbin"], """0 HR, 1 near-HR, 96.3 mph EV. Corbin LHB split -0.94, HR risk 0.08. tough split lane (-0.94); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "WSH @ BAL - Andrew Alvarez (L, WSH) vs Trevor Rogers (L, BAL)",
        "description": "Tail key data: Park boost data unavailable. Alvarez (HR risk -1.13, vs LHB -0.76, vs RHB -0.94). Rogers (HR risk -0.33, vs LHB -0.83, vs RHB +0.08).",
        "rows": [
            row("Taylor Ward", "R", "N/A", 76, "", ["vs Alvarez"], """1 HR, 1 near-HR, 94.2 mph EV. Alvarez RHB split -0.94, HR risk -1.13. tough split lane (-0.94); pitcher suppresses HR (-1.13).""", blast="good"),
            row("Pete Alonso", "R", "N/A", 69, "", ["vs Alvarez"], """0 HR, 93.0 mph EV. Alvarez RHB split -0.94, HR risk -1.13. tough split lane (-0.94); pitcher suppresses HR (-1.13).""", blast="good"),
            row("Coby Mayo", "R", "N/A", 80, "🌕 💣", ["vs Alvarez"], """2 HR, 2 near-HR, 89.5 mph EV. Alvarez RHB split -0.94, HR risk -1.13. tough split lane (-0.94); pitcher suppresses HR (-1.13).""", blast="high"),
            row("James Wood", "L", "N/A", 82, "🚀 ⭐", ["vs Rogers"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 103.4 mph EV. Rogers LHB split -0.83, HR risk -0.33. tough split lane (-0.83); pitcher risk below avg (-0.33).""", blast="good"),
            row("CJ Abrams", "L", "N/A", 62, "", ["vs Rogers"], """0 HR, 87.1 mph EV. Rogers LHB split -0.83, HR risk -0.33. tough split lane (-0.83); pitcher risk below avg (-0.33)."""),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-26")

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

    out = ROOT / '_games-0626.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
