#!/usr/bin/env python3
"""Generate games[] block for 2026-07-03 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Dominic Canzone (L)",
    "Elly De La Cruz (S)",
    "Esmerlyn Valdez (R)",
    "Francisco Alvarez (R)",
    "Francisco Lindor (S)",
    "Garrett Mitchell (L)",
    "Gary Sanchez (R)",
    "James Wood (L)",
    "Matt Olson (L)",
    "Mickey Moniak (L)",
    "Owen Caissie (L)",
    "Pete Alonso (R)",
    "Randal Grichuk (R)",
    "Yordan Alvarez (L)",
    "Zach Neto (R)",
}

GEMS = {
    "CJ Abrams (L)",
    "David Fry (R)",
    "Jordan Walker (R)",
    "Junior Perez (R)",
    "Pete Crow-Armstrong (L)",
    "Taylor Trammell (L)",
}

PLAYER_TEAMS = {
    "A.J. Ewing (L)": "NYM",
    "Amed Rosario (R)": "NYY",
    "Ben Rice (L)": "NYY",
    "Brandon Lowe (L)": "PIT",
    "Brandon Valenzuela (S)": "TOR",
    "Brice Turang (L)": "MIL",
    "CJ Abrams (L)": "WSH",
    "Casey Schmitt (R)": "SF",
    "Cedric Mullins (L)": "TB",
    "Cole Young (L)": "SEA",
    "Colson Montgomery (L)": "CWS",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "Dansby Swanson (R)": "CHC",
    "David Fry (R)": "CLE",
    "Denzer Guzman (R)": "LAA",
    "Dominic Canzone (L)": "SEA",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Garrett Mitchell (L)": "MIL",
    "Gary Sanchez (R)": "MIL",
    "Gavin Sheets (L)": "SD",
    "Heliot Ramos (R)": "SF",
    "JJ Wetherholt (L)": "STL",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Joe Mack (L)": "MIA",
    "Jordan Walker (R)": "STL",
    "Jose Siri (R)": "LAA",
    "Josh Bell (S)": "MIN",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Junior Perez (R)": "CWS",
    "Kahlil Watson (L)": "CLE",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Stowers (L)": "MIA",
    "Lawrence Butler (L)": "ATH",
    "Leody Taveras (S)": "BAL",
    "Luis Garcia Jr. (L)": "WSH",
    "Luke Raley (L)": "SEA",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Schuemann (R)": "NYY",
    "Michael Conforto (L)": "CHC",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Mookie Betts (R)": "LAD",
    "Nelson Velazquez (R)": "STL",
    "Nick Kurtz (L)": "ATH",
    "Owen Caissie (L)": "MIA",
    "Paul Goldschmidt (R)": "NYY",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Ryan Kreidler (R)": "MIN",
    "Sean Keys (L)": "TOR",
    "Shea Langeliers (R)": "ATH",
    "Sung-Mun Song (L)": "SD",
    "Taylor Trammell (L)": "HOU",
    "Ty France (R)": "SD",
    "Tyler O'Neill (R)": "BAL",
    "Tyler Stephenson (R)": "CIN",
    "Willi Castro (S)": "COL",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("CWS @ CLE", "Williams"),
    ("MIL @ ARI", "Cabrera"),
    ("MIN @ NYY", "Cole"),
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
        "title": "BAL @ CIN - Trevor Rogers (L, BAL) vs Brady Singer (R, CIN)",
        "description": "Tail key data: Park boost +22% (stadium +14%, weather +8%). Rogers (HR risk -0.88, vs LHB -1.25, vs RHB -0.27). Singer (HR risk 0.46, vs LHB +0.76, vs RHB -0.41).",
        "rows": [
            row("Elly De La Cruz", "S", "+397", 58, "⭐", ["vs Rogers"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.3 mph EV. Rogers RHB split -0.27, HR risk -0.88. slight split headwind (-0.27); pitcher suppresses HR (-0.88).""", blast="good"),
            row("Tyler Stephenson", "R", "+390", 58, "", ["vs Rogers"], """0 HR, 1 near-HR, 89.0 mph EV. Rogers RHB split -0.27, HR risk -0.88. slight split headwind (-0.27); pitcher suppresses HR (-0.88)."""),
            row("Pete Alonso", "R", "+302", 84, "⭐ 🌕 💣", ["vs Singer"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 90.6 mph EV. Singer RHB split -0.41, HR risk 0.46. tough split lane (-0.41).""", blast="high"),
            row("Tyler O'Neill", "R", "N/A", 68, "", ["vs Singer"], """0 HR, 99.2 mph EV. Singer RHB split -0.41, HR risk 0.46. tough split lane (-0.41); limited recent HR events.""", blast="good"),
            row("Leody Taveras", "S", "N/A", 78, "", ["vs Singer"], """0 HR, 96.0 mph EV. Singer RHB split -0.41, HR risk 0.46. tough split lane (-0.41); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "BOS @ LAA - Jake Bennett (L, BOS) vs Reid Detmers (L, LAA)",
        "description": "Tail key data: Park boost +9% (stadium +9%, weather -1%). Bennett (HR risk -1.40, vs LHB -2.00, vs RHB -0.50). Detmers (HR risk -0.83, vs LHB -1.17, vs RHB -0.21).",
        "rows": [
            row("Zach Neto", "R", "N/A", 58, "⭐ 🌕 💣", ["vs Bennett"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.0 mph EV. Bennett RHB split -0.50, HR risk -1.40. tough split lane (-0.50); pitcher suppresses HR (-1.40).""", blast="high"),
            row("Denzer Guzman", "R", "N/A", 58, "🌕 💣", ["vs Bennett"], """2 HR, 2 near-HR, 94.0 mph EV. Bennett RHB split -0.50, HR risk -1.40. tough split lane (-0.50); pitcher suppresses HR (-1.40).""", blast="high"),
            row("Jose Siri", "R", "N/A", 58, "", ["vs Bennett"], """1 HR, 2 near-HR, 98.8 mph EV. Bennett RHB split -0.50, HR risk -1.40. tough split lane (-0.50); pitcher suppresses HR (-1.40).""", blast="good"),
        ],
    },
    {
        "title": "CWS @ CLE - Anthony Kay (L, CWS) vs Gavin Williams 🧤 (R, CLE)",
        "description": "Tail key data: Park boost +16% (stadium -3%, weather +20%). Kay (HR risk -0.09, vs LHB -0.11, vs RHB -0.05). Williams 🧤 (HR risk 1.34, vs LHB +0.64, vs RHB +1.58).",
        "rows": [
            row("Kahlil Watson", "L", "+630", 58, "", ["vs Kay"], """0 HR, 1 near-HR, 91.8 mph EV. Kay LHB split -0.11, HR risk -0.09. slight split headwind (-0.11); pitcher risk below avg (-0.09)."""),
            row("David Fry", "R", "+540", 68, "🌕 💣 💎", ["vs Kay"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 87.6 mph EV. Kay RHB split -0.05, HR risk -0.09. slight split headwind (-0.05); pitcher risk below avg (-0.09).""", blast="high"),
            row("Junior Perez", "R", "N/A", 93, "🚀 🌕 💣 💎", ["vs Williams"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 100.9 mph EV. Williams RHB split +1.58, HR risk 1.34.""", blast="good"),
            row("Randal Grichuk", "R", "N/A", 94, "⭐ 🌕 💣", ["vs Williams"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.1 mph EV. Williams RHB split +1.58, HR risk 1.34.""", blast="good"),
            row("Miguel Vargas", "R", "+390", 91, "🌕 💣", ["vs Williams"], """0 HR, 1 near-HR, 94.0 mph EV. Williams RHB split +1.58, HR risk 1.34. limited recent HR events.""", blast="good"),
            row("Colson Montgomery", "L", "+400", 73, "", ["vs Williams"], """0 HR, 1 near-HR, 84.9 mph EV. Williams LHB split +0.64, HR risk 1.34. limited recent HR events; lighter EV form (84.9 mph)."""),
        ],
    },
    {
        "title": "MIA @ ATH - Tyler Phillips (R, MIA) vs Jack Perkins (R, ATH)",
        "description": "Tail key data: Park boost +34% (stadium +30%, weather +4%). Phillips (HR risk 0.62, vs LHB +0.79, vs RHB +0.14). Perkins (HR risk 0.26, vs LHB -0.17, vs RHB +0.77).",
        "rows": [
            row("Nick Kurtz", "L", "+128", 85, "", ["vs Phillips"], """0 HR, 2 near-HR, 99.8 mph EV. Phillips LHB split +0.79, HR risk 0.62.""", blast="good"),
            row("Lawrence Butler", "L", "+261", 84, "🚀", ["vs Phillips"], """0 HR, 1 near-HR, 100.4 mph EV. Phillips LHB split +0.79, HR risk 0.62. limited recent HR events.""", blast="good"),
            row("Shea Langeliers", "R", "+149", 79, "", ["vs Phillips"], """1 HR, 2 near-HR, 90.7 mph EV. Phillips RHB split +0.14, HR risk 0.62.""", blast="good"),
            row("Joe Mack", "L", "+279", 84, "🌕 💣", ["vs Perkins"], """2 HR, 3 near-HR, 92.0 mph EV. Perkins LHB split -0.17, HR risk 0.26. slight split headwind (-0.17).""", blast="high"),
            row("Owen Caissie", "L", "+280", 89, "⭐ 🌕 💣", ["vs Perkins"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 97.4 mph EV. Perkins LHB split -0.17, HR risk 0.26. slight split headwind (-0.17).""", blast="high"),
            row("Kyle Stowers", "L", "+166", 68, "", ["vs Perkins"], """0 HR, 1 near-HR, 94.5 mph EV. Perkins LHB split -0.17, HR risk 0.26. slight split headwind (-0.17); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIL @ ARI - Kyle Harrison (L, MIL) vs Jose Cabrera 🧤 (R, ARI)",
        "description": "Tail key data: Park boost -9% (stadium -9%, weather +0%). Harrison (HR risk 0.64, vs LHB -0.31, vs RHB +0.97). Cabrera 🧤 (HR risk 1.13, vs LHB +0.80, vs RHB +1.03).",
        "rows": [
            row("Ketel Marte", "S", "+366", 80, "", ["vs Harrison"], """1 HR, 2 near-HR, 96.7 mph EV. Harrison RHB split +0.97, HR risk 0.64. park/weather net drag (-9%).""", blast="good"),
            row("Corbin Carroll", "L", "+560", 63, "", ["vs Harrison"], """0 HR, 96.1 mph EV. Harrison LHB split -0.31, HR risk 0.64. slight split headwind (-0.31); park/weather net drag (-9%).""", blast="good"),
            row("Gary Sanchez", "R", "N/A", 94, "⭐ 🌕 💣", ["vs Cabrera"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 98.4 mph EV. Cabrera RHB split +1.03, HR risk 1.13. park/weather net drag (-9%).""", blast="high"),
            row("Garrett Mitchell", "L", "+710", 91, "⭐ 🌕 💣", ["vs Cabrera"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.1 mph EV. Cabrera LHB split +0.80, HR risk 1.13. park/weather net drag (-9%).""", blast="high"),
            row("Jake Bauers", "L", "+458", 80, "", ["vs Cabrera"], """1 HR, 1 near-HR, 92.0 mph EV. Cabrera LHB split +0.80, HR risk 1.13. park/weather net drag (-9%).""", blast="good"),
            row("Brice Turang", "L", "+800", 74, "", ["vs Cabrera"], """1 HR, 1 near-HR, 86.0 mph EV. Cabrera LHB split +0.80, HR risk 1.13. park/weather net drag (-9%); lighter EV form (86.0 mph).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ NYY - Mike Paredes (R, MIN) vs Gerrit Cole 🧤 (R, NYY)",
        "description": "Tail key data: Park boost +25% (stadium +5%, weather +20%). Paredes (HR risk 0.80, vs LHB +0.12, vs RHB +1.67). Cole 🧤 (HR risk 1.10, vs LHB +0.85, vs RHB +0.50).",
        "rows": [
            row("Ben Rice", "L", "+240", 92, "⭐ 🌕 💣", ["vs Paredes"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 97.7 mph EV. Paredes LHB split +0.12, HR risk 0.80.""", blast="high"),
            row("Amed Rosario", "R", "N/A", 84, "", ["vs Paredes"], """1 HR, 1 near-HR, 85.7 mph EV. Paredes RHB split +1.67, HR risk 0.80. lighter EV form (85.7 mph).""", blast="good"),
            row("Max Schuemann", "R", "N/A", 89, "🌕 💣", ["vs Paredes"], """0 HR, 99.5 mph EV. Paredes RHB split +1.67, HR risk 0.80. limited recent HR events.""", blast="good"),
            row("Paul Goldschmidt", "R", "+390", 93, "🌕 💣", ["vs Paredes"], """2 HR, 2 near-HR, 89.9 mph EV. Paredes RHB split +1.67, HR risk 0.80.""", blast="high"),
            row("Kody Clemens", "L", "+273", 95, "🌕 💣", ["vs Cole"], """2 HR, 3 near-HR, 92.9 mph EV. Cole LHB split +0.85, HR risk 1.10.""", blast="high"),
            row("Josh Bell", "S", "+364", 95, "🌕 💣", ["vs Cole"], """2 HR, 3 near-HR, 91.5 mph EV. Cole RHB split +0.50, HR risk 1.10.""", blast="high"),
            row("Ryan Kreidler", "R", "+630", 85, "", ["vs Cole"], """1 HR, 2 near-HR, 89.6 mph EV. Cole RHB split +0.50, HR risk 1.10.""", blast="good"),
        ],
    },
    {
        "title": "NYM @ ATL - Christian Scott (R, NYM) vs Grant Holmes (R, ATL)",
        "description": "Tail key data: Park boost +4% (stadium -1%, weather +5%). Scott (HR risk -0.01, vs LHB +0.48, vs RHB -1.03). Holmes (HR risk 0.36, vs LHB +0.27, vs RHB +0.41).",
        "rows": [
            row("Matt Olson", "L", "+280", 64, "🚀 ⭐", ["vs Scott"], """Worst Pickz Favorite. 0 HR, 103.8 mph EV. Scott LHB split +0.48, HR risk -0.01. pitcher risk below avg (-0.01); limited recent HR events.""", blast="good"),
            row("Francisco Alvarez", "R", "+394", 90, "⭐ 🌕 💣", ["vs Holmes"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 97.1 mph EV. Holmes RHB split +0.41, HR risk 0.36.""", blast="high"),
            row("Francisco Lindor", "S", "+514", 82, "⭐ 🌕 💣", ["vs Holmes"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.6 mph EV. Holmes RHB split +0.41, HR risk 0.36.""", blast="high"),
            row("Juan Soto", "L", "+357", 66, "", ["vs Holmes"], """0 HR, 1 near-HR, 95.1 mph EV. Holmes LHB split +0.27, HR risk 0.36. limited recent HR events.""", blast="good"),
            row("A.J. Ewing", "L", "+900", 63, "", ["vs Holmes"], """0 HR, 1 near-HR, 92.3 mph EV. Holmes LHB split +0.27, HR risk 0.36. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "PIT @ WSH - Mitch Keller (R, PIT) vs Foster Griffin (L, WSH)",
        "description": "Tail key data: Park boost +2% (stadium +4%, weather -2%). Keller (HR risk 0.10, vs LHB +0.12, vs RHB +0.15). Griffin (HR risk -0.13, vs LHB -0.08, vs RHB +0.05).",
        "rows": [
            row("James Wood", "L", "+299", 61, "⭐", ["vs Keller"], """Worst Pickz Favorite. 0 HR, 98.4 mph EV. Keller LHB split +0.12, HR risk 0.10. limited recent HR events.""", blast="good"),
            row("CJ Abrams", "L", "+432", 71, "🌕 💣 💎", ["vs Keller"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 90.4 mph EV. Keller LHB split +0.12, HR risk 0.10.""", blast="high"),
            row("Luis Garcia Jr.", "L", "+450", 84, "🌕 💣", ["vs Keller"], """6 HR, 7 near-HR, 95.9 mph EV. Keller LHB split +0.12, HR risk 0.10.""", blast="high"),
            row("Esmerlyn Valdez", "R", "+418", 78, "⭐ 🌕 💣", ["vs Griffin"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 99.9 mph EV. Griffin RHB split +0.05, HR risk -0.13. pitcher risk below avg (-0.13).""", blast="high"),
            row("Brandon Lowe", "L", "+418", 59, "", ["vs Griffin"], """0 HR, 1 near-HR, 95.5 mph EV. Griffin LHB split -0.08, HR risk -0.13. slight split headwind (-0.08); pitcher risk below avg (-0.13).""", blast="good"),
        ],
    },
    {
        "title": "SD @ LAD - Michael King (R, SD) vs Shohei Ohtani (R, LAD)",
        "description": "Tail key data: Park boost +10% (stadium +18%, weather -8%). King (HR risk -0.03, vs LHB -0.12, vs RHB +0.18). Ohtani (HR risk -1.78, vs LHB -1.16, vs RHB -1.20).",
        "rows": [
            row("Dalton Rushing", "L", "+500", 58, "", ["vs King"], """0 HR, 90.7 mph EV. King LHB split -0.12, HR risk -0.03. slight split headwind (-0.12); pitcher risk below avg (-0.03)."""),
            row("Mookie Betts", "R", "+470", 82, "🌕 💣", ["vs King"], """3 HR, 4 near-HR, 92.6 mph EV. King RHB split +0.18, HR risk -0.03. pitcher risk below avg (-0.03); weather carry headwind (-8%).""", blast="high"),
            row("Fernando Tatis Jr.", "R", "+400", 58, "", ["vs Ohtani"], """0 HR, 96.0 mph EV. Ohtani RHB split -1.20, HR risk -1.78. tough split lane (-1.20); pitcher suppresses HR (-1.78).""", blast="good"),
            row("Ty France", "R", "+600", 58, "", ["vs Ohtani"], """1 HR, 1 near-HR, 85.5 mph EV. Ohtani RHB split -1.20, HR risk -1.78. tough split lane (-1.20); pitcher suppresses HR (-1.78).""", blast="good"),
            row("Gavin Sheets", "L", "+520", 59, "🌕 💣", ["vs Ohtani"], """3 HR, 3 near-HR, 91.6 mph EV. Ohtani LHB split -1.16, HR risk -1.78. tough split lane (-1.16); pitcher suppresses HR (-1.78).""", blast="high"),
            row("Manny Machado", "R", "+420", 58, "", ["vs Ohtani"], """0 HR, 2 near-HR, 97.2 mph EV. Ohtani RHB split -1.20, HR risk -1.78. tough split lane (-1.20); pitcher suppresses HR (-1.78).""", blast="good"),
            row("Sung-Mun Song", "L", "N/A", 58, "", ["vs Ohtani"], """1 HR, 1 near-HR, 92.3 mph EV. Ohtani LHB split -1.16, HR risk -1.78. tough split lane (-1.16); pitcher suppresses HR (-1.78).""", blast="good"),
        ],
    },
    {
        "title": "SF @ COL - Logan Webb (R, SF) vs Ryan Feltner (R, COL)",
        "description": "Tail key data: Park boost +32% (stadium +20%, weather +12%). Away starter risk unavailable. Feltner (HR risk -0.14, vs LHB +0.31, vs RHB -0.40).",
        "rows": [
            row("Mickey Moniak", "L", "+196", 89, "⭐ 🌕 💣", ["vs Webb"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 93.0 mph EV. Webb split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Willi Castro", "S", "+366", 73, "", ["vs Webb"], """1 HR, 1 near-HR, 94.3 mph EV. Webb split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Rafael Devers", "L", "+145", 88, "🌕 💣", ["vs Feltner"], """4 HR, 5 near-HR, 93.2 mph EV. Feltner LHB split +0.31, HR risk -0.14. pitcher risk below avg (-0.14).""", blast="high"),
            row("Casey Schmitt", "R", "+174", 78, "🌕 💣", ["vs Feltner"], """1 HR, 4 near-HR, 94.6 mph EV. Feltner RHB split -0.40, HR risk -0.14. tough split lane (-0.40); pitcher risk below avg (-0.14).""", blast="high"),
            row("Heliot Ramos", "R", "+197", 79, "🌕 💣", ["vs Feltner"], """3 HR, 4 near-HR, 89.8 mph EV. Feltner RHB split -0.40, HR risk -0.14. tough split lane (-0.40); pitcher risk below avg (-0.14).""", blast="high"),
        ],
    },
    {
        "title": "STL @ CHC - Andre Pallante (R, STL) vs David Peterson (L, CHC)",
        "description": "Tail key data: Park boost +36% (stadium +0%, weather +36%). Pallante (HR risk -1.20, vs LHB -0.83, vs RHB -0.66). Peterson (HR risk 0.17, vs LHB +0.34, vs RHB +0.12).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+144", 58, "🌕 💣 💎", ["vs Pallante"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 79.9 mph EV. Pallante LHB split -0.83, HR risk -1.20. tough split lane (-0.83); pitcher suppresses HR (-1.20).""", blast="high"),
            row("Michael Conforto", "L", "+217", 58, "", ["vs Pallante"], """0 HR, 1 near-HR, 92.8 mph EV. Pallante LHB split -0.83, HR risk -1.20. tough split lane (-0.83); pitcher suppresses HR (-1.20).""", blast="good"),
            row("Dansby Swanson", "R", "+193", 58, "", ["vs Pallante"], """1 HR, 1 near-HR, 96.1 mph EV. Pallante RHB split -0.66, HR risk -1.20. tough split lane (-0.66); pitcher suppresses HR (-1.20).""", blast="good"),
            row("JJ Wetherholt", "L", "+254", 70, "", ["vs Peterson"], """0 HR, 1 near-HR, 92.7 mph EV. Peterson LHB split +0.34, HR risk 0.17. limited recent HR events.""", blast="good"),
            row("Nelson Velazquez", "R", "+171", 77, "", ["vs Peterson"], """1 HR, 2 near-HR, 95.9 mph EV. Peterson RHB split +0.12, HR risk 0.17.""", blast="good"),
            row("Jordan Walker", "R", "+157", 76, "💎", ["vs Peterson"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 99.3 mph EV. Peterson RHB split +0.12, HR risk 0.17.""", blast="good"),
        ],
    },
    {
        "title": "TB @ HOU - Nick Martinez (R, TB) vs Spencer Arrighetti (R, HOU)",
        "description": "Tail key data: Park boost +4% (stadium +9%, weather -5%). Martinez (HR risk 0.01, vs LHB +0.11, vs RHB -0.03). Arrighetti (HR risk 0.91, vs LHB +1.42, vs RHB -0.29).",
        "rows": [
            row("Yordan Alvarez", "L", "N/A", 79, "⭐ 🌕 💣", ["vs Martinez"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.8 mph EV. Martinez LHB split +0.11, HR risk 0.01. weather carry headwind (-5%).""", blast="high"),
            row("Taylor Trammell", "L", "N/A", 80, "🌕 💣 💎", ["vs Martinez"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 95.4 mph EV. Martinez LHB split +0.11, HR risk 0.01. weather carry headwind (-5%).""", blast="high"),
            row("Junior Caminero", "R", "N/A", 91, "🌕 💣", ["vs Arrighetti"], """6 HR, 7 near-HR, 95.4 mph EV. Arrighetti RHB split -0.29, HR risk 0.91. slight split headwind (-0.29); weather carry headwind (-5%).""", blast="high"),
            row("Cedric Mullins", "L", "N/A", 91, "🌕 💣", ["vs Arrighetti"], """2 HR, 2 near-HR, 91.7 mph EV. Arrighetti LHB split +1.42, HR risk 0.91. weather carry headwind (-5%).""", blast="high"),
        ],
    },
    {
        "title": "TOR @ SEA - Dylan Cease (R, TOR) vs Luis Castillo (R, SEA)",
        "description": "Tail key data: Park boost -4% (stadium +1%, weather -4%). Cease (HR risk -1.03, vs LHB -0.08, vs RHB -1.44). Castillo (HR risk -0.34, vs LHB +0.26, vs RHB -1.08).",
        "rows": [
            row("Dominic Canzone", "L", "+520", 58, "⭐", ["vs Cease"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.0 mph EV. Cease LHB split -0.08, HR risk -1.03. slight split headwind (-0.08); pitcher suppresses HR (-1.03).""", blast="good"),
            row("Luke Raley", "L", "+600", 58, "", ["vs Cease"], """1 HR, 2 near-HR, 93.9 mph EV. Cease LHB split -0.08, HR risk -1.03. slight split headwind (-0.08); pitcher suppresses HR (-1.03).""", blast="good"),
            row("Cole Young", "L", "+900", 58, "", ["vs Cease"], """1 HR, 2 near-HR, 90.3 mph EV. Cease LHB split -0.08, HR risk -1.03. slight split headwind (-0.08); pitcher suppresses HR (-1.03).""", blast="good"),
            row("Brandon Valenzuela", "S", "N/A", 74, "🌕 💣", ["vs Castillo"], """2 HR, 3 near-HR, 93.5 mph EV. Castillo RHB split -1.08, HR risk -0.34. tough split lane (-1.08); pitcher risk below avg (-0.34).""", blast="high"),
            row("Sean Keys", "L", "N/A", 59, "", ["vs Castillo"], """1 HR, 1 near-HR, 92.9 mph EV. Castillo LHB split +0.26, HR risk -0.34. pitcher risk below avg (-0.34); weather carry headwind (-4%).""", blast="good"),
            row("Kazuma Okamoto", "R", "+420", 59, "🌕 💣", ["vs Castillo"], """2 HR, 2 near-HR, 89.6 mph EV. Castillo RHB split -1.08, HR risk -0.34. tough split lane (-1.08); pitcher risk below avg (-0.34).""", blast="high"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-03")

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

    out = ROOT / '_games-0703.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
