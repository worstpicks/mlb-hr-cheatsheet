#!/usr/bin/env python3
"""Generate games[] block for 2026-07-24 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "A.J. Ewing (L)",
    "Austin Riley (R)",
    "Ben Rice (L)",
    "Dalton Rushing (L)",
    "Esmerlyn Valdez (R)",
    "Hunter Goodman (R)",
    "Jake Burger (R)",
    "James Wood (L)",
    "Joe Mack (L)",
    "Juan Soto (L)",
    "Kyle Stowers (L)",
    "Lane Thomas (R)",
    "Lars Nootbaar (L)",
    "Manny Machado (R)",
    "Randal Grichuk (R)",
    "Riley Greene (L)",
    "Shea Langeliers (R)",
    "Ty France (R)",
    "Willson Contreras (R)",
}

GEMS = {
    "Andres Chaparro (R)",
    "Chase DeLauter (L)",
    "Griffin Conine (L)",
    "Yohendrick Pinango (L)",
}

PLAYER_TEAMS = {
    "A.J. Ewing (L)": "NYM",
    "Alec Burleson (L)": "STL",
    "Alex Call (R)": "LAD",
    "Andres Chaparro (R)": "WSH",
    "Andy Pages (R)": "LAD",
    "Austin Riley (R)": "ATL",
    "Austin Wells (L)": "NYY",
    "Ben Rice (L)": "NYY",
    "Braden Shewmake (L)": "MIL",
    "Brett Baty (L)": "NYM",
    "Brewer Hicklen (R)": "ATL",
    "Brice Turang (L)": "MIL",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Carter Jensen (L)": "KC",
    "Casey Schmitt (R)": "SF",
    "Chase DeLauter (L)": "CLE",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Coby Mayo (R)": "BAL",
    "Colt Keith (L)": "DET",
    "Dalton Rushing (L)": "LAD",
    "Derek Hill (R)": "PHI",
    "Dillon Dingler (R)": "DET",
    "Esmerlyn Valdez (R)": "PIT",
    "Ezequiel Duran (R)": "TEX",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Lindor (S)": "NYM",
    "Gabriel Moreno (R)": "ARI",
    "Griffin Conine (L)": "MIA",
    "Gunnar Henderson (L)": "BAL",
    "Heliot Ramos (R)": "SF",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Ildemaro Vargas (S)": "ARI",
    "Isaac Paredes (R)": "HOU",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "Jackson Merrill (L)": "SD",
    "Jacob Young (R)": "WSH",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jim Jarvis (L)": "ATL",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "Jorge Soler (R)": "LAA",
    "Josh Naylor (L)": "SEA",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lane Thomas (R)": "KC",
    "Lars Nootbaar (L)": "STL",
    "Manny Machado (R)": "SD",
    "Michael Conforto (L)": "CHC",
    "Munetaka Murakami (L)": "CWS",
    "Nathaniel Lowe (L)": "CIN",
    "Nolan Arenado (R)": "ARI",
    "Randal Grichuk (R)": "CWS",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Ryan McMahon (L)": "NYY",
    "Ryan Vilade (R)": "TB",
    "Salvador Perez (R)": "KC",
    "Sam Huff (R)": "BAL",
    "Seiya Suzuki (R)": "CHC",
    "Shea Langeliers (R)": "ATH",
    "Trea Turner (R)": "PHI",
    "Tristan Peters (L)": "CWS",
    "Ty France (R)": "SD",
    "Tyler Soderstrom (L)": "ATH",
    "Willson Contreras (R)": "BOS",
    "Yandy Diaz (R)": "TB",
    "Yohendrick Pinango (L)": "TOR",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("ATH @ MIN", "Matthews"),
    ("COL @ MIL", "Sugano"),
    ("HOU @ CWS", "Arrighetti"),
    ("LAD @ NYM", "Sasaki"),
    ("SD @ MIA", "Marquez"),
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
        "title": "ARI @ WSH - Eduardo Rodriguez (L, ARI) vs Carson Palmquist (L, WSH)",
        "description": "Tail key data: Park boost data unavailable. Rodriguez (HR risk -0.06, vs LHB +0.18, vs RHB -0.15). Palmquist (HR risk -0.29, vs LHB +0.62, vs RHB -0.62).",
        "rows": [
            row("Andres Chaparro", "R", "+499", 81, "🌕 💣 💎", ["vs Rodriguez"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 93.1 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("James Wood", "L", "+285", 61, "⭐", ["vs Rodriguez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 90.6 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Jacob Young", "R", "+870", 60, "", ["vs Rodriguez"], """1 HR, 1 near-HR, 89.1 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Ildemaro Vargas", "S", "+830", 61, "", ["vs Palmquist"], """0 HR, 1 near-HR, 94.6 mph EV. Palmquist SHB→LHB split +0.62, HR risk -0.29. pitcher risk below avg (-0.29); limited recent HR events.""", blast="good"),
            row("Gabriel Moreno", "R", "+600", 59, "", ["vs Palmquist"], """1 HR, 3 near-HR, 91.9 mph EV. Palmquist RHB split -0.62, HR risk -0.29. tough split lane (-0.62); pitcher risk below avg (-0.29).""", blast="good"),
            row("Nolan Arenado", "R", "+483", 58, "", ["vs Palmquist"], """1 HR, 2 near-HR, 89.3 mph EV. Palmquist RHB split -0.62, HR risk -0.29. tough split lane (-0.62); pitcher risk below avg (-0.29).""", blast="good"),
        ],
    },
    {
        "title": "ATH @ MIN - Jacob Lopez (L, ATH) vs Zebby Matthews 🧤 (R, MIN)",
        "description": "Tail key data: Park boost -2% (stadium -6%, weather +4%). Lopez (HR risk -0.82, vs LHB -1.03, vs RHB -0.13). Matthews 🧤 (HR risk 1.17, vs LHB +0.59, vs RHB +1.14).",
        "rows": [
            row("Kody Clemens", "L", "+431", 58, "", ["vs Lopez"], """1 HR, 1 near-HR, 90.5 mph EV. Lopez LHB split -1.03, HR risk -0.82. tough split lane (-1.03); pitcher suppresses HR (-0.82).""", blast="good"),
            row("Shea Langeliers", "R", "+280", 93, "🚀 ⭐ 🌕 💣", ["vs Matthews"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 106.0 mph EV. Matthews RHB split +1.14, HR risk 1.17. park suppresses carry (-6%).""", blast="high"),
            row("Tyler Soderstrom", "L", "+350", 81, "", ["vs Matthews"], """1 HR, 1 near-HR, 92.6 mph EV. Matthews LHB split +0.59, HR risk 1.17. park suppresses carry (-6%).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ BAL - Grant Holmes (R, ATL) vs Trevor Rogers (L, BAL)",
        "description": "Tail key data: Park boost -9% (stadium -3%, weather -6%). Holmes (HR risk -0.35, vs LHB -0.29, vs RHB -0.25). Rogers (HR risk -0.48, vs LHB -0.95, vs RHB -0.15).",
        "rows": [
            row("Christian Encarnacion-Strand", "R", "N/A", 58, "", ["vs Holmes"], """0 HR, 78.1 mph EV. Holmes RHB split -0.25, HR risk -0.35. slight split headwind (-0.25); pitcher risk below avg (-0.35)."""),
            row("Gunnar Henderson", "L", "+347", 59, "", ["vs Holmes"], """1 HR, 3 near-HR, 91.8 mph EV. Holmes LHB split -0.29, HR risk -0.35. slight split headwind (-0.29); pitcher risk below avg (-0.35).""", blast="good"),
            row("Coby Mayo", "R", "+415", 58, "", ["vs Holmes"], """0 HR, 97.0 mph EV. Holmes RHB split -0.25, HR risk -0.35. slight split headwind (-0.25); pitcher risk below avg (-0.35).""", blast="good"),
            row("Sam Huff", "R", "+610", 58, "", ["vs Holmes"], """0 HR, 2 near-HR, 89.2 mph EV. Holmes RHB split -0.25, HR risk -0.35. slight split headwind (-0.25); pitcher risk below avg (-0.35).""", blast="good"),
            row("Austin Riley", "R", "+463", 58, "⭐", ["vs Rogers"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 97.5 mph EV. Rogers RHB split -0.15, HR risk -0.48. slight split headwind (-0.15); pitcher suppresses HR (-0.48).""", blast="good"),
            row("Jim Jarvis", "L", "+800", 58, "", ["vs Rogers"], """0 HR, 1 near-HR, 94.8 mph EV. Rogers LHB split -0.95, HR risk -0.48. tough split lane (-0.95); pitcher suppresses HR (-0.48).""", blast="good"),
            row("Brewer Hicklen", "R", "N/A", 58, "🚀", ["vs Rogers"], """0 HR, 104.4 mph EV. Rogers RHB split -0.15, HR risk -0.48. slight split headwind (-0.15); pitcher suppresses HR (-0.48).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ PIT - Matthew Boyd (L, CHC) vs Jared Jones (R, PIT)",
        "description": "Tail key data: Park boost -21% (stadium -16%, weather -6%). Boyd (HR risk 0.09, vs LHB -0.40, vs RHB +0.40). Jones (HR risk -0.90, vs LHB -0.78, vs RHB -0.37).",
        "rows": [
            row("Esmerlyn Valdez", "R", "+296", 81, "🚀 ⭐ 🌕 💣", ["vs Boyd"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 101.8 mph EV. Boyd RHB split +0.40, HR risk 0.09. park/weather net drag (-21%).""", blast="high"),
            row("Seiya Suzuki", "R", "+574", 58, "", ["vs Jones"], """1 HR, 2 near-HR, 90.7 mph EV. Jones RHB split -0.37, HR risk -0.90. slight split headwind (-0.37); pitcher suppresses HR (-0.90).""", blast="good"),
            row("Ian Happ", "S", "+511", 58, "", ["vs Jones"], """1 HR, 1 near-HR, 92.0 mph EV. Jones SHB→RHB split -0.37, HR risk -0.90. slight split headwind (-0.37); pitcher suppresses HR (-0.90).""", blast="good"),
            row("Michael Conforto", "L", "+600", 58, "🌕 💣", ["vs Jones"], """2 HR, 3 near-HR, 92.4 mph EV. Jones LHB split -0.78, HR risk -0.90. tough split lane (-0.78); pitcher suppresses HR (-0.90).""", blast="high"),
        ],
    },
    {
        "title": "CIN @ STL - Rhett Lowder (R, CIN) vs Dustin May (R, STL)",
        "description": "Tail key data: Park boost -26% (stadium -9%, weather -17%). Lowder (HR risk -0.18, vs LHB +0.15, vs RHB -1.19). May (HR risk -0.53, vs LHB -0.48, vs RHB -0.28).",
        "rows": [
            row("Jimmy Crooks", "L", "+660", 59, "", ["vs Lowder"], """1 HR, 1 near-HR, 95.6 mph EV. Lowder LHB split +0.15, HR risk -0.18. pitcher risk below avg (-0.18); park/weather net drag (-26%).""", blast="good"),
            row("Alec Burleson", "L", "+395", 58, "", ["vs Lowder"], """0 HR, 1 near-HR, 89.4 mph EV. Lowder LHB split +0.15, HR risk -0.18. pitcher risk below avg (-0.18); park/weather net drag (-26%)."""),
            row("Lars Nootbaar", "L", "+524", 58, "⭐", ["vs Lowder"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.2 mph EV. Lowder LHB split +0.15, HR risk -0.18. pitcher risk below avg (-0.18); park/weather net drag (-26%).""", blast="good"),
            row("Nathaniel Lowe", "L", "+630", 62, "🌕 💣", ["vs May"], """2 HR, 3 near-HR, 92.7 mph EV. May LHB split -0.48, HR risk -0.53. tough split lane (-0.48); pitcher suppresses HR (-0.53).""", blast="high"),
            row("JJ Bleday", "L", "+562", 58, "", ["vs May"], """1 HR, 2 near-HR, 92.7 mph EV. May LHB split -0.48, HR risk -0.53. tough split lane (-0.48); pitcher suppresses HR (-0.53).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ TB - Joey Cantillo (L, CLE) vs Shane McClanahan (L, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Cantillo (HR risk -0.88, vs LHB -0.28, vs RHB -0.76). McClanahan (HR risk -0.09, vs LHB +0.12, vs RHB -0.14).",
        "rows": [
            row("Ryan Vilade", "R", "+720", 60, "🌕 💣", ["vs Cantillo"], """2 HR, 2 near-HR, 95.4 mph EV. Cantillo RHB split -0.76, HR risk -0.88. tough split lane (-0.76); pitcher suppresses HR (-0.88).""", blast="high"),
            row("Junior Caminero", "R", "+300", 58, "", ["vs Cantillo"], """1 HR, 1 near-HR, 91.2 mph EV. Cantillo RHB split -0.76, HR risk -0.88. tough split lane (-0.76); pitcher suppresses HR (-0.88).""", blast="good"),
            row("Yandy Diaz", "R", "+520", 58, "", ["vs Cantillo"], """0 HR, 94.8 mph EV. Cantillo RHB split -0.76, HR risk -0.88. tough split lane (-0.76); pitcher suppresses HR (-0.88).""", blast="good"),
            row("Rhys Hoskins", "R", "+372", 67, "🌕 💣", ["vs McClanahan"], """2 HR, 2 near-HR, 91.9 mph EV. McClanahan RHB split -0.14, HR risk -0.09. slight split headwind (-0.14); pitcher risk below avg (-0.09).""", blast="high"),
            row("Chase DeLauter", "L", "+840", 72, "🌕 💣 💎", ["vs McClanahan"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.8 mph EV. McClanahan LHB split +0.12, HR risk -0.09. pitcher risk below avg (-0.09).""", blast="high"),
        ],
    },
    {
        "title": "COL @ MIL - Tomoyuki Sugano 🧤 (R, COL) vs Shane Drohan (L, MIL)",
        "description": "Tail key data: Park boost +9% (stadium +10%, weather -1%). Sugano 🧤 (HR risk 1.02, vs LHB +0.39, vs RHB +0.90). Drohan (HR risk -0.65, vs LHB -0.64, vs RHB -0.18).",
        "rows": [
            row("Jake Bauers", "L", "+314", 86, "", ["vs Sugano"], """1 HR, 2 near-HR, 99.5 mph EV. Sugano LHB split +0.39, HR risk 1.02.""", blast="good"),
            row("Brice Turang", "L", "+508", 81, "", ["vs Sugano"], """1 HR, 2 near-HR, 91.8 mph EV. Sugano LHB split +0.39, HR risk 1.02.""", blast="good"),
            row("Braden Shewmake", "L", "N/A", 76, "", ["vs Sugano"], """0 HR, 2 near-HR, 90.4 mph EV. Sugano LHB split +0.39, HR risk 1.02.""", blast="good"),
            row("Hunter Goodman", "R", "+286", 69, "🚀 ⭐ 🌕 💣", ["vs Drohan"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.7 mph EV. Drohan RHB split -0.18, HR risk -0.65. slight split headwind (-0.18); pitcher suppresses HR (-0.65).""", blast="high"),
        ],
    },
    {
        "title": "HOU @ CWS - Spencer Arrighetti 🧤 (R, HOU) vs Davis Martin (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Arrighetti 🧤 (HR risk 1.20, vs LHB +0.97, vs RHB -0.24). Martin (HR risk -1.13, vs LHB -0.80, vs RHB -0.66).",
        "rows": [
            row("Randal Grichuk", "R", "N/A", 80, "⭐", ["vs Arrighetti"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.9 mph EV. Arrighetti RHB split -0.24, HR risk 1.20. slight split headwind (-0.24).""", blast="good"),
            row("Munetaka Murakami", "L", "+322", 94, "🌕 💣", ["vs Arrighetti"], """2 HR, 3 near-HR, 92.9 mph EV. Arrighetti LHB split +0.97, HR risk 1.20.""", blast="high"),
            row("Tristan Peters", "L", "+900", 87, "", ["vs Arrighetti"], """1 HR, 2 near-HR, 93.0 mph EV. Arrighetti LHB split +0.97, HR risk 1.20.""", blast="good"),
            row("Yordan Alvarez", "L", "+224", 58, "🌕 💣", ["vs Martin"], """2 HR, 2 near-HR, 93.3 mph EV. Martin LHB split -0.80, HR risk -1.13. tough split lane (-0.80); pitcher suppresses HR (-1.13).""", blast="high"),
            row("Isaac Paredes", "R", "+566", 58, "", ["vs Martin"], """1 HR, 1 near-HR, 85.3 mph EV. Martin RHB split -0.66, HR risk -1.13. tough split lane (-0.66); pitcher suppresses HR (-1.13).""", blast="good"),
        ],
    },
    {
        "title": "KC @ DET - Beck Way (R, KC) vs Tarik Skubal (L, DET)",
        "description": "Tail key data: Park boost -20% (stadium -10%, weather -9%). Way (HR risk 0.40, vs LHB +1.51, vs RHB -1.06). Skubal (HR risk -0.19, vs LHB -0.13, vs RHB +0.20).",
        "rows": [
            row("Riley Greene", "L", "+392", 88, "⭐ 🌕 💣", ["vs Way"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 91.9 mph EV. Way LHB split +1.51, HR risk 0.40. park/weather net drag (-20%).""", blast="high"),
            row("Colt Keith", "L", "+784", 92, "🌕 💣", ["vs Way"], """3 HR, 3 near-HR, 98.3 mph EV. Way LHB split +1.51, HR risk 0.40. park/weather net drag (-20%).""", blast="high"),
            row("Dillon Dingler", "R", "+490", 61, "🌕 💣", ["vs Way"], """2 HR, 2 near-HR, 85.7 mph EV. Way RHB split -1.06, HR risk 0.40. tough split lane (-1.06); park/weather net drag (-20%).""", blast="high"),
            row("Lane Thomas", "R", "+830", 75, "🚀 ⭐ 🌕 💣", ["vs Skubal"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 100.6 mph EV. Skubal RHB split +0.20, HR risk -0.19. pitcher risk below avg (-0.19); park/weather net drag (-20%).""", blast="high"),
            row("Carter Jensen", "L", "+800", 58, "", ["vs Skubal"], """1 HR, 2 near-HR, 94.7 mph EV. Skubal LHB split -0.13, HR risk -0.19. slight split headwind (-0.13); pitcher risk below avg (-0.19).""", blast="good"),
            row("Salvador Perez", "R", "+790", 59, "", ["vs Skubal"], """1 HR, 1 near-HR, 98.3 mph EV. Skubal RHB split +0.20, HR risk -0.19. pitcher risk below avg (-0.19); park/weather net drag (-20%).""", blast="good"),
            row("Jac Caglianone", "L", "+780", 58, "", ["vs Skubal"], """1 HR, 1 near-HR, 91.1 mph EV. Skubal LHB split -0.13, HR risk -0.19. slight split headwind (-0.13); pitcher risk below avg (-0.19).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ SF - Grayson Rodriguez (R, LAA) vs Logan Webb (R, SF)",
        "description": "Tail key data: Park boost -15% (stadium -13%, weather -2%). Rodriguez (HR risk 0.48, vs LHB +0.00, vs RHB +0.88). Webb (HR risk -0.70, vs LHB -0.56, vs RHB -0.40).",
        "rows": [
            row("Bryce Eldridge", "L", "+370", 62, "", ["vs Rodriguez"], """1 HR, 1 near-HR, 95.4 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; park/weather net drag (-15%).""", blast="good"),
            row("Casey Schmitt", "R", "+450", 63, "", ["vs Rodriguez"], """1 HR, 1 near-HR, 97.4 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; park/weather net drag (-15%).""", blast="good"),
            row("Heliot Ramos", "R", "+484", 58, "", ["vs Rodriguez"], """1 HR, 1 near-HR, 91.1 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; park/weather net drag (-15%).""", blast="good"),
            row("Jorge Soler", "R", "+630", 58, "", ["vs Webb"], """0 HR, 83.0 mph EV. Webb RHB split -0.40, HR risk -0.70. tough split lane (-0.40); pitcher suppresses HR (-0.70)."""),
            row("Jo Adell", "R", "+910", 58, "", ["vs Webb"], """0 HR, 93.9 mph EV. Webb RHB split -0.40, HR risk -0.70. tough split lane (-0.40); pitcher suppresses HR (-0.70).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ NYM - Roki Sasaki 🧤 (R, LAD) vs Sean Manaea (L, NYM)",
        "description": "Tail key data: Park boost -7% (stadium -2%, weather -5%). Sasaki 🧤 (HR risk 1.61, vs LHB +0.42, vs RHB +2.04). Manaea (HR risk 0.70, vs LHB -0.35, vs RHB +1.15).",
        "rows": [
            row("Brett Baty", "L", "+800", 91, "🌕 💣", ["vs Sasaki"], """2 HR, 2 near-HR, 97.9 mph EV. Sasaki LHB split +0.42, HR risk 1.61. park/weather net drag (-7%).""", blast="high"),
            row("A.J. Ewing", "L", "+800", 86, "⭐", ["vs Sasaki"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.9 mph EV. Sasaki LHB split +0.42, HR risk 1.61. park/weather net drag (-7%).""", blast="good"),
            row("Francisco Lindor", "S", "+476", 92, "🌕 💣", ["vs Sasaki"], """1 HR, 1 near-HR, 96.8 mph EV. Sasaki SHB→RHB split +2.04, HR risk 1.61. park/weather net drag (-7%).""", blast="good"),
            row("Juan Soto", "L", "+314", 84, "⭐", ["vs Sasaki"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.2 mph EV. Sasaki LHB split +0.42, HR risk 1.61. park/weather net drag (-7%).""", blast="good"),
            row("Jared Young", "L", "+569", 69, "", ["vs Sasaki"], """0 HR, 1 near-HR, 88.9 mph EV. Sasaki LHB split +0.42, HR risk 1.61. park/weather net drag (-7%); limited recent HR events."""),
            row("Dalton Rushing", "L", "+544", 63, "⭐", ["vs Manaea"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 93.3 mph EV. Manaea LHB split -0.35, HR risk 0.70. slight split headwind (-0.35); park/weather net drag (-7%).""", blast="good"),
            row("Andy Pages", "R", "+406", 75, "", ["vs Manaea"], """1 HR, 1 near-HR, 89.9 mph EV. Manaea RHB split +1.15, HR risk 0.70. park/weather net drag (-7%).""", blast="good"),
            row("Alex Call", "R", "+1060", 75, "", ["vs Manaea"], """1 HR, 1 near-HR, 89.5 mph EV. Manaea RHB split +1.15, HR risk 0.70. park/weather net drag (-7%).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ PHI - Will Warren (R, NYY) vs Jesus Luzardo (L, PHI)",
        "description": "Tail key data: Park boost +9% (stadium +14%, weather -5%). Warren (HR risk 0.81, vs LHB +0.19, vs RHB +0.95). Luzardo (HR risk -1.29, vs LHB -1.31, vs RHB -0.58).",
        "rows": [
            row("Trea Turner", "R", "+600", 83, "", ["vs Warren"], """1 HR, 1 near-HR, 93.9 mph EV. Warren RHB split +0.95, HR risk 0.81. weather carry headwind (-5%).""", blast="good"),
            row("Derek Hill", "R", "N/A", 77, "", ["vs Warren"], """1 HR, 1 near-HR, 88.6 mph EV. Warren RHB split +0.95, HR risk 0.81. weather carry headwind (-5%).""", blast="good"),
            row("Bryce Harper", "L", "+370", 75, "", ["vs Warren"], """1 HR, 1 near-HR, 92.7 mph EV. Warren LHB split +0.19, HR risk 0.81. weather carry headwind (-5%).""", blast="good"),
            row("Kyle Schwarber", "L", "+215", 75, "🚀", ["vs Warren"], """0 HR, 1 near-HR, 101.8 mph EV. Warren LHB split +0.19, HR risk 0.81. weather carry headwind (-5%); limited recent HR events.""", blast="good"),
            row("Ben Rice", "L", "+430", 58, "⭐ 🌕 💣", ["vs Luzardo"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.4 mph EV. Luzardo LHB split -1.31, HR risk -1.29. tough split lane (-1.31); pitcher suppresses HR (-1.29).""", blast="high"),
            row("Austin Wells", "L", "N/A", 58, "", ["vs Luzardo"], """1 HR, 1 near-HR, 87.9 mph EV. Luzardo LHB split -1.31, HR risk -1.29. tough split lane (-1.31); pitcher suppresses HR (-1.29).""", blast="good"),
            row("Ryan McMahon", "L", "N/A", 58, "", ["vs Luzardo"], """0 HR, 1 near-HR, 88.0 mph EV. Luzardo LHB split -1.31, HR risk -1.29. tough split lane (-1.31); pitcher suppresses HR (-1.29)."""),
        ],
    },
    {
        "title": "SD @ MIA - German Marquez 🧤 (R, SD) vs Ryan Gusto (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -12%, weather +0%). Marquez 🧤 (HR risk 1.22, vs LHB +0.93, vs RHB +0.19). Gusto (HR risk -0.52, vs LHB -0.40, vs RHB -0.60).",
        "rows": [
            row("Joe Mack", "L", "+820", 95, "⭐ 🌕 💣", ["vs Marquez"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 99.0 mph EV. Marquez LHB split +0.93, HR risk 1.22. park/weather net drag (-13%).""", blast="high"),
            row("Kyle Stowers", "L", "+348", 92, "🚀 ⭐ 🌕 💣", ["vs Marquez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.0 mph EV. Marquez LHB split +0.93, HR risk 1.22. park/weather net drag (-13%).""", blast="high"),
            row("Griffin Conine", "L", "+600", 90, "🌕 💣 💎", ["vs Marquez"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 92.9 mph EV. Marquez LHB split +0.93, HR risk 1.22. park/weather net drag (-13%).""", blast="high"),
            row("Heriberto Hernandez", "R", "+531", 76, "", ["vs Marquez"], """0 HR, 2 near-HR, 97.4 mph EV. Marquez RHB split +0.19, HR risk 1.22. park/weather net drag (-13%).""", blast="good"),
            row("Ty France", "R", "+680", 69, "🚀 ⭐ 🌕 💣", ["vs Gusto"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 100.3 mph EV. Gusto RHB split -0.60, HR risk -0.52. tough split lane (-0.60); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Manny Machado", "R", "+375", 68, "⭐ 🌕 💣", ["vs Gusto"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 94.7 mph EV. Gusto RHB split -0.60, HR risk -0.52. tough split lane (-0.60); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Fernando Tatis Jr.", "R", "+536", 58, "", ["vs Gusto"], """1 HR, 2 near-HR, 96.6 mph EV. Gusto RHB split -0.60, HR risk -0.52. tough split lane (-0.60); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Jackson Merrill", "L", "+394", 58, "", ["vs Gusto"], """1 HR, 2 near-HR, 95.8 mph EV. Gusto LHB split -0.40, HR risk -0.52. tough split lane (-0.40); pitcher suppresses HR (-0.52).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ TEX - Bryce Miller (R, SEA) vs MacKenzie Gore (L, TEX)",
        "description": "Tail key data: Park boost -10% (stadium -10%, weather -1%). Miller (HR risk 0.16, vs LHB -0.15, vs RHB +0.31). Gore (HR risk 0.43, vs LHB -0.14, vs RHB +0.70).",
        "rows": [
            row("Joc Pederson", "L", "+333", 60, "", ["vs Miller"], """1 HR, 1 near-HR, 93.3 mph EV. Miller LHB split -0.15, HR risk 0.16. slight split headwind (-0.15); park/weather net drag (-10%).""", blast="good"),
            row("Jake Burger", "R", "+465", 66, "🚀 ⭐", ["vs Miller"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 101.5 mph EV. Miller RHB split +0.31, HR risk 0.16. park/weather net drag (-10%).""", blast="good"),
            row("Ezequiel Duran", "R", "+890", 62, "", ["vs Miller"], """1 HR, 1 near-HR, 92.4 mph EV. Miller RHB split +0.31, HR risk 0.16. park/weather net drag (-10%).""", blast="good"),
            row("Josh Naylor", "L", "+680", 58, "", ["vs Gore"], """0 HR, 89.2 mph EV. Gore LHB split -0.14, HR risk 0.43. slight split headwind (-0.14); park/weather net drag (-10%)."""),
        ],
    },
    {
        "title": "TOR @ BOS - Trey Yesavage (R, TOR) vs Patrick Sandoval (L, BOS)",
        "description": "Tail key data: Park boost -5% (stadium -6%, weather +1%). Yesavage (HR risk -0.52, vs LHB -0.55, vs RHB -0.14). Sandoval (HR risk -0.71, vs LHB +0.00, vs RHB -1.69).",
        "rows": [
            row("Willson Contreras", "R", "+498", 67, "⭐ 🌕 💣", ["vs Yesavage"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.9 mph EV. Yesavage RHB split -0.14, HR risk -0.52. slight split headwind (-0.14); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Yohendrick Pinango", "L", "+1150", 58, "💎", ["vs Sandoval"], """Worst Pickz Hidden Gem. 0 HR, 87.1 mph EV. Sandoval LHB split +0.00, HR risk -0.71. pitcher suppresses HR (-0.71); park/weather net drag (-5%)."""),
            row("Kazuma Okamoto", "R", "+600", 58, "🌕 💣", ["vs Sandoval"], """2 HR, 2 near-HR, 87.6 mph EV. Sandoval RHB split -1.69, HR risk -0.71. tough split lane (-1.69); pitcher suppresses HR (-0.71).""", blast="high"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-24")

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
