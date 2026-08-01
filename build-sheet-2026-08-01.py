#!/usr/bin/env python3
"""Generate games[] block for 2026-08-01 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Bryce Harper (L)",
    "Cal Raleigh (S)",
    "Carter Jensen (L)",
    "Coby Mayo (R)",
    "Colson Montgomery (L)",
    "Dominic Canzone (L)",
    "Eugenio Suarez (R)",
    "Francisco Alvarez (R)",
    "Francisco Lindor (S)",
    "Jackson Merrill (L)",
    "Jake Bauers (L)",
    "Jordan Walker (R)",
    "Junior Caminero (R)",
    "Kody Clemens (L)",
    "Manny Machado (R)",
    "Munetaka Murakami (L)",
    "Riley Greene (L)",
    "Shohei Ohtani (L)",
}

GEMS = {
    "A.J. Ewing (L)",
    "Corey Seager (L)",
    "Enrique Hernandez (R)",
    "Hao-Yu Lee (R)",
    "Jimmy Crooks (L)",
    "John Rave (L)",
    "Kazuma Okamoto (R)",
    "Leo Jimenez (R)",
    "Michael Conforto (L)",
    "Mike Yastrzemski (L)",
    "Pete Alonso (R)",
    "Richie Palacios (L)",
    "Ronald Acuna Jr. (R)",
    "Salvador Perez (R)",
    "Ty France (R)",
    "Yainer Diaz (R)",
}

PLAYER_TEAMS = {
    "A.J. Ewing (L)": "NYM",
    "Alec Burleson (L)": "STL",
    "Alex Bregman (R)": "CHC",
    "Amed Rosario (R)": "NYY",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Vaughn (R)": "MIL",
    "Anthony Volpe (R)": "NYY",
    "Ben Rice (L)": "NYY",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Carson Kelly (R)": "CHC",
    "Carter Jensen (L)": "KC",
    "Chase DeLauter (L)": "CLE",
    "Coby Mayo (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Cooper Pratt (R)": "MIL",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Derek Hill (R)": "PHI",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Elly De La Cruz (S)": "CIN",
    "Enrique Hernandez (R)": "LAD",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Ezequiel Duran (R)": "TEX",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Freddie Freeman (L)": "LAD",
    "Gabriel Moreno (R)": "ARI",
    "Garrett Mitchell (L)": "MIL",
    "Hao-Yu Lee (R)": "DET",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ildemaro Vargas (S)": "ARI",
    "JJ Bleday (L)": "CIN",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jeremy Pena (R)": "HOU",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "LAA",
    "John Rave (L)": "KC",
    "Jordan Walker (R)": "STL",
    "Jorge Soler (R)": "LAA",
    "Jose Siri (R)": "LAA",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kody Clemens (L)": "MIN",
    "Kyle Tucker (L)": "LAD",
    "Lane Thomas (R)": "KC",
    "Lars Nootbaar (L)": "STL",
    "Lawrence Butler (L)": "ATH",
    "Leo Jimenez (R)": "MIA",
    "Luis Lara (S)": "MIL",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Michael Conforto (L)": "CHC",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Mike Yastrzemski (L)": "ATL",
    "Munetaka Murakami (L)": "CWS",
    "Otto Lopez (R)": "MIA",
    "Patrick Bailey (S)": "CLE",
    "Pete Alonso (R)": "BAL",
    "Rafael Devers (L)": "SF",
    "Rhys Hoskins (R)": "CLE",
    "Richie Palacios (L)": "TB",
    "Riley Greene (L)": "DET",
    "Rob Refsnyder (R)": "SEA",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan O'Hearn (L)": "PIT",
    "Salvador Perez (R)": "KC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Taylor Trammell (L)": "HOU",
    "Ty France (R)": "SD",
    "Tyler Soderstrom (L)": "ATH",
    "Victor Mesa Jr. (L)": "TB",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Yainer Diaz (R)": "HOU",
}

BUM_MATCHUPS = {
    ("ARI @ CLE", "Drake"),
    ("KC @ COL", "Feltner"),
    ("TEX @ HOU", "Blanco"),
    ("WSH @ ATL", "Mikolas"),
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
        "title": "ARI @ CLE - Kohl Drake 🧤 (L, ARI) vs Parker Messick (L, CLE)",
        "description": "Tail key data: Park boost +2% (stadium -4%, weather +6%). Drake 🧤 (HR risk 1.46, vs LHB +0.00, vs RHB +0.11). Messick (HR risk -0.90, vs LHB -0.97, vs RHB -0.64).",
        "rows": [
            row("Chase DeLauter", "L", "+520", 91, "🌕 💣", ["vs Drake"], """2 HR, 3 near-HR, 92.4 mph EV. Drake LHB split +0.00, HR risk 1.46.""", blast="high"),
            row("Patrick Bailey", "S", "N/A", 75, "", ["vs Drake"], """0 HR, 93.1 mph EV. Drake SHB→RHB split +0.11, HR risk 1.46. limited recent HR events.""", blast="good"),
            row("Rhys Hoskins", "R", "+320", 67, "", ["vs Drake"], """0 HR, 1 near-HR, 86.8 mph EV. Drake RHB split +0.11, HR risk 1.46. limited recent HR events; lighter EV form (86.8 mph)."""),
            row("Gabriel Moreno", "R", "+770", 58, "", ["vs Messick"], """1 HR, 3 near-HR, 98.0 mph EV. Messick RHB split -0.64, HR risk -0.90. tough split lane (-0.64); pitcher suppresses HR (-0.90).""", blast="good"),
            row("Ildemaro Vargas", "S", "+910", 58, "", ["vs Messick"], """0 HR, 94.8 mph EV. Messick SHB→RHB split -0.64, HR risk -0.90. tough split lane (-0.64); pitcher suppresses HR (-0.90).""", blast="good"),
            row("Max Kepler", "L", "N/A", 58, "", ["vs Messick"], """0 HR, 96.1 mph EV. Messick LHB split -0.97, HR risk -0.90. tough split lane (-0.97); pitcher suppresses HR (-0.90).""", blast="good"),
            row("Corbin Carroll", "L", "+461", 58, "", ["vs Messick"], """1 HR, 1 near-HR, 88.5 mph EV. Messick LHB split -0.97, HR risk -0.90. tough split lane (-0.97); pitcher suppresses HR (-0.90).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ LAD - Payton Tolle (L, BOS) vs Yoshinobu Yamamoto (R, LAD)",
        "description": "Tail key data: Park boost +20% (stadium +17%, weather +3%). Tolle (HR risk 0.41, vs LHB -0.11, vs RHB +0.68). Yamamoto (HR risk -0.53, vs LHB -0.32, vs RHB -0.54).",
        "rows": [
            row("Shohei Ohtani", "L", "+239", 85, "⭐ 🌕 💣", ["vs Tolle"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 99.2 mph EV. Tolle LHB split -0.11, HR risk 0.41. slight split headwind (-0.11).""", blast="high"),
            row("Enrique Hernandez", "R", "N/A", 82, "🚀 💎", ["vs Tolle"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 103.2 mph EV. Tolle RHB split +0.68, HR risk 0.41.""", blast="good"),
            row("Freddie Freeman", "L", "+461", 70, "", ["vs Tolle"], """0 HR, 1 near-HR, 95.1 mph EV. Tolle LHB split -0.11, HR risk 0.41. slight split headwind (-0.11); limited recent HR events.""", blast="good"),
            row("Kyle Tucker", "L", "+480", 74, "", ["vs Tolle"], """1 HR, 2 near-HR, 92.8 mph EV. Tolle LHB split -0.11, HR risk 0.41. slight split headwind (-0.11).""", blast="good"),
            row("Willson Contreras", "R", "+249", 58, "", ["vs Yamamoto"], """1 HR, 1 near-HR, 90.4 mph EV. Yamamoto RHB split -0.54, HR risk -0.53. tough split lane (-0.54); pitcher suppresses HR (-0.53).""", blast="good"),
        ],
    },
    {
        "title": "CWS @ TB - Jordan Hicks (R, CWS) vs Drew Rasmussen (R, TB)",
        "description": "Tail key data: Park boost -4% (stadium -5%, weather +1%). Hicks (HR risk -1.24, vs LHB -0.87, vs RHB -1.06). Rasmussen (HR risk -0.23, vs LHB -0.26, vs RHB -0.06).",
        "rows": [
            row("Richie Palacios", "L", "N/A", 58, "🌕 💣 💎", ["vs Hicks"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.9 mph EV. Hicks LHB split -0.87, HR risk -1.24. tough split lane (-0.87); pitcher suppresses HR (-1.24).""", blast="high"),
            row("Junior Caminero", "R", "+223", 58, "⭐", ["vs Hicks"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 90.8 mph EV. Hicks RHB split -1.06, HR risk -1.24. tough split lane (-1.06); pitcher suppresses HR (-1.24).""", blast="good"),
            row("Victor Mesa Jr.", "L", "N/A", 58, "🌕 💣", ["vs Hicks"], """2 HR, 3 near-HR, 88.1 mph EV. Hicks LHB split -0.87, HR risk -1.24. tough split lane (-0.87); pitcher suppresses HR (-1.24).""", blast="high"),
            row("Munetaka Murakami", "L", "+346", 69, "⭐ 🌕 💣", ["vs Rasmussen"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.7 mph EV. Rasmussen LHB split -0.26, HR risk -0.23. slight split headwind (-0.26); pitcher risk below avg (-0.23).""", blast="high"),
            row("Andrew Benintendi", "L", "+650", 58, "", ["vs Rasmussen"], """1 HR, 1 near-HR, 91.5 mph EV. Rasmussen LHB split -0.26, HR risk -0.23. slight split headwind (-0.26); pitcher risk below avg (-0.23).""", blast="good"),
            row("Miguel Vargas", "R", "+414", 58, "", ["vs Rasmussen"], """1 HR, 1 near-HR, 89.7 mph EV. Rasmussen RHB split -0.06, HR risk -0.23. slight split headwind (-0.06); pitcher risk below avg (-0.23).""", blast="good"),
            row("Colson Montgomery", "L", "+432", 58, "⭐", ["vs Rasmussen"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.1 mph EV. Rasmussen LHB split -0.26, HR risk -0.23. slight split headwind (-0.26); pitcher risk below avg (-0.23).""", blast="good"),
        ],
    },
    {
        "title": "DET @ ATH - Framber Valdez (L, DET) vs Jack Perkins (R, ATH)",
        "description": "Tail key data: Park boost +35% (stadium +33%, weather +3%). Valdez (HR risk -0.34, vs LHB -0.53, vs RHB -0.16). Perkins (HR risk 0.38, vs LHB +0.20, vs RHB +0.50).",
        "rows": [
            row("Tyler Soderstrom", "L", "+500", 60, "", ["vs Valdez"], """1 HR, 1 near-HR, 90.1 mph EV. Valdez LHB split -0.53, HR risk -0.34. tough split lane (-0.53); pitcher risk below avg (-0.34).""", blast="good"),
            row("Henry Bolte", "R", "+560", 62, "", ["vs Valdez"], """0 HR, 95.0 mph EV. Valdez RHB split -0.16, HR risk -0.34. slight split headwind (-0.16); pitcher risk below avg (-0.34).""", blast="good"),
            row("Lawrence Butler", "L", "+680", 58, "", ["vs Valdez"], """0 HR, 1 near-HR, 92.3 mph EV. Valdez LHB split -0.53, HR risk -0.34. tough split lane (-0.53); pitcher risk below avg (-0.34).""", blast="good"),
            row("Riley Greene", "L", "+330", 92, "⭐ 🌕 💣", ["vs Perkins"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 99.3 mph EV. Perkins LHB split +0.20, HR risk 0.38.""", blast="high"),
            row("Hao-Yu Lee", "R", "+470", 78, "💎", ["vs Perkins"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.5 mph EV. Perkins RHB split +0.50, HR risk 0.38.""", blast="good"),
            row("Dillon Dingler", "R", "+330", 80, "🌕 💣", ["vs Perkins"], """2 HR, 2 near-HR, 86.3 mph EV. Perkins RHB split +0.50, HR risk 0.38. lighter EV form (86.3 mph).""", blast="high"),
        ],
    },
    {
        "title": "KC @ COL - Luinder Avila (R, KC) vs Ryan Feltner 🧤 (R, COL)",
        "description": "Tail key data: Park boost +24% (stadium +20%, weather +4%). Avila (HR risk -0.72, vs LHB -0.73, vs RHB +0.33). Feltner 🧤 (HR risk 1.27, vs LHB +0.95, vs RHB +1.12).",
        "rows": [
            row("Hunter Goodman", "R", "+260", 83, "🌕 💣", ["vs Avila"], """3 HR, 4 near-HR, 94.9 mph EV. Avila RHB split +0.33, HR risk -0.72. pitcher suppresses HR (-0.72).""", blast="high"),
            row("Mickey Moniak", "L", "+325", 58, "", ["vs Avila"], """1 HR, 1 near-HR, 89.4 mph EV. Avila LHB split -0.73, HR risk -0.72. tough split lane (-0.73); pitcher suppresses HR (-0.72).""", blast="good"),
            row("Willi Castro", "S", "+579", 76, "🌕 💣", ["vs Avila"], """3 HR, 5 near-HR, 87.5 mph EV. Avila SHB→RHB split +0.33, HR risk -0.72. pitcher suppresses HR (-0.72); lighter EV form (87.5 mph).""", blast="high"),
            row("Salvador Perez", "R", "+310", 98, "🌕 💣 💎", ["vs Feltner"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 95.0 mph EV. Feltner RHB split +1.12, HR risk 1.27.""", blast="high"),
            row("Carter Jensen", "L", "+328", 93, "⭐ 🌕 💣", ["vs Feltner"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 92.1 mph EV. Feltner LHB split +0.95, HR risk 1.27.""", blast="good"),
            row("Lane Thomas", "R", "+451", 81, "", ["vs Feltner"], """0 HR, 90.3 mph EV. Feltner RHB split +1.12, HR risk 1.27. limited recent HR events."""),
            row("John Rave", "L", "+312", 94, "🌕 💣 💎", ["vs Feltner"], """Worst Pickz Hidden Gem. 1 HR, 4 near-HR, 89.8 mph EV. Feltner LHB split +0.95, HR risk 1.27.""", blast="high"),
        ],
    },
    {
        "title": "MIA @ NYM - Tyler Phillips (R, MIA) vs Zach Thornton (L, NYM)",
        "description": "Tail key data: Park boost +7% (stadium -2%, weather +9%). Phillips (HR risk -0.07, vs LHB +0.02, vs RHB -0.19). Thornton (HR risk -0.14, vs LHB +0.38, vs RHB -0.39).",
        "rows": [
            row("Francisco Alvarez", "R", "+437", 73, "⭐ 🌕 💣", ["vs Phillips"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.5 mph EV. Phillips RHB split -0.19, HR risk -0.07. slight split headwind (-0.19); pitcher risk below avg (-0.07).""", blast="high"),
            row("A.J. Ewing", "L", "+690", 58, "💎", ["vs Phillips"], """Worst Pickz Hidden Gem. 0 HR, 92.5 mph EV. Phillips LHB split +0.02, HR risk -0.07. pitcher risk below avg (-0.07); limited recent HR events.""", blast="good"),
            row("Francisco Lindor", "S", "+400", 59, "⭐", ["vs Phillips"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 87.8 mph EV. Phillips SHB→LHB split +0.02, HR risk -0.07. pitcher risk below avg (-0.07); lighter EV form (87.8 mph).""", blast="good"),
            row("Heriberto Hernandez", "R", "+324", 70, "🌕 💣", ["vs Thornton"], """2 HR, 2 near-HR, 94.2 mph EV. Thornton RHB split -0.39, HR risk -0.14. slight split headwind (-0.39); pitcher risk below avg (-0.14).""", blast="high"),
            row("Leo Jimenez", "R", "+870", 63, "💎", ["vs Thornton"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 99.3 mph EV. Thornton RHB split -0.39, HR risk -0.14. slight split headwind (-0.39); pitcher risk below avg (-0.14).""", blast="good"),
            row("Otto Lopez", "R", "+620", 63, "", ["vs Thornton"], """1 HR, 2 near-HR, 98.4 mph EV. Thornton RHB split -0.39, HR risk -0.14. slight split headwind (-0.39); pitcher risk below avg (-0.14).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ LAA - Robert Gasser (L, MIL) vs Jose Soriano (R, LAA)",
        "description": "Tail key data: Park boost -3% (stadium -8%, weather +4%). Gasser (HR risk 0.56, vs LHB -0.28, vs RHB +0.82). Soriano (HR risk -0.84, vs LHB -0.44, vs RHB -0.99).",
        "rows": [
            row("Jorge Soler", "R", "+360", 77, "", ["vs Gasser"], """1 HR, 2 near-HR, 93.5 mph EV. Gasser RHB split +0.82, HR risk 0.56. park suppresses carry (-8%).""", blast="good"),
            row("Jose Siri", "R", "+459", 89, "🌕 💣", ["vs Gasser"], """2 HR, 3 near-HR, 92.7 mph EV. Gasser RHB split +0.82, HR risk 0.56. park suppresses carry (-8%).""", blast="high"),
            row("Jo Adell", "R", "+364", 78, "🌕 💣", ["vs Gasser"], """2 HR, 2 near-HR, 86.3 mph EV. Gasser RHB split +0.82, HR risk 0.56. park suppresses carry (-8%); lighter EV form (86.3 mph).""", blast="high"),
            row("Cooper Pratt", "R", "+1060", 58, "", ["vs Soriano"], """1 HR, 1 near-HR, 88.2 mph EV. Soriano RHB split -0.99, HR risk -0.84. tough split lane (-0.99); pitcher suppresses HR (-0.84).""", blast="good"),
            row("Jake Bauers", "L", "+450", 58, "⭐", ["vs Soriano"], """Worst Pickz Favorite. 0 HR, 97.2 mph EV. Soriano LHB split -0.44, HR risk -0.84. tough split lane (-0.44); pitcher suppresses HR (-0.84).""", blast="good"),
            row("Garrett Mitchell", "L", "+630", 58, "", ["vs Soriano"], """0 HR, 96.4 mph EV. Soriano LHB split -0.44, HR risk -0.84. tough split lane (-0.44); pitcher suppresses HR (-0.84).""", blast="good"),
            row("Andrew Vaughn", "R", "+750", 58, "", ["vs Soriano"], """1 HR, 2 near-HR, 97.6 mph EV. Soriano RHB split -0.99, HR risk -0.84. tough split lane (-0.99); pitcher suppresses HR (-0.84).""", blast="good"),
            row("Luis Lara", "S", "+705", 58, "", ["vs Soriano"], """0 HR, 89.9 mph EV. Soriano SHB→LHB split -0.44, HR risk -0.84. tough split lane (-0.44); pitcher suppresses HR (-0.84)."""),
        ],
    },
    {
        "title": "MIN @ SEA - Connor Prielipp (L, MIN) vs Logan Gilbert (R, SEA)",
        "description": "Tail key data: Park boost +1% (stadium +1%, weather +0%). Prielipp (HR risk 0.17, vs LHB -0.30, vs RHB +0.48). Gilbert (HR risk -0.36, vs LHB -0.23, vs RHB -0.31).",
        "rows": [
            row("Dominic Canzone", "L", "+500", 73, "⭐ 🌕 💣", ["vs Prielipp"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.5 mph EV. Prielipp LHB split -0.30, HR risk 0.17. slight split headwind (-0.30).""", blast="high"),
            row("Cal Raleigh", "S", "+360", 70, "⭐", ["vs Prielipp"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.8 mph EV. Prielipp SHB→RHB split +0.48, HR risk 0.17.""", blast="good"),
            row("Julio Rodriguez", "R", "+446", 65, "", ["vs Prielipp"], """1 HR, 1 near-HR, 90.9 mph EV. Prielipp RHB split +0.48, HR risk 0.17.""", blast="good"),
            row("Rob Refsnyder", "R", "+700", 62, "", ["vs Prielipp"], """1 HR, 2 near-HR, 86.0 mph EV. Prielipp RHB split +0.48, HR risk 0.17. lighter EV form (86.0 mph).""", blast="good"),
            row("Kody Clemens", "L", "+361", 58, "⭐", ["vs Gilbert"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 93.5 mph EV. Gilbert LHB split -0.23, HR risk -0.36. slight split headwind (-0.23); pitcher risk below avg (-0.36).""", blast="good"),
            row("Royce Lewis", "R", "+390", 58, "", ["vs Gilbert"], """0 HR, 93.3 mph EV. Gilbert RHB split -0.31, HR risk -0.36. slight split headwind (-0.31); pitcher risk below avg (-0.36).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ CHC - Max Fried (L, NYY) vs David Peterson (L, CHC)",
        "description": "Tail key data: Park boost -20% (stadium -1%, weather -19%). Fried (HR risk -1.44, vs LHB -0.76, vs RHB -1.37). Peterson (HR risk -0.16, vs LHB +0.04, vs RHB -0.12).",
        "rows": [
            row("Michael Conforto", "L", "N/A", 58, "🚀 💎", ["vs Fried"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 106.2 mph EV. Fried LHB split -0.76, HR risk -1.44. tough split lane (-0.76); pitcher suppresses HR (-1.44).""", blast="good"),
            row("Carson Kelly", "R", "+1100", 58, "", ["vs Fried"], """1 HR, 1 near-HR, 86.5 mph EV. Fried RHB split -1.37, HR risk -1.44. tough split lane (-1.37); pitcher suppresses HR (-1.44).""", blast="good"),
            row("Alex Bregman", "R", "+1380", 58, "", ["vs Fried"], """1 HR, 1 near-HR, 87.7 mph EV. Fried RHB split -1.37, HR risk -1.44. tough split lane (-1.37); pitcher suppresses HR (-1.44).""", blast="good"),
            row("Ben Rice", "L", "+630", 58, "", ["vs Peterson"], """1 HR, 1 near-HR, 91.0 mph EV. Peterson LHB split +0.04, HR risk -0.16. pitcher risk below avg (-0.16); park/weather net drag (-20%).""", blast="good"),
            row("Anthony Volpe", "R", "+1220", 58, "", ["vs Peterson"], """0 HR, 1 near-HR, 92.0 mph EV. Peterson RHB split -0.12, HR risk -0.16. slight split headwind (-0.12); pitcher risk below avg (-0.16).""", blast="good"),
            row("Spencer Jones", "L", "N/A", 58, "", ["vs Peterson"], """1 HR, 1 near-HR, 91.7 mph EV. Peterson LHB split +0.04, HR risk -0.16. pitcher risk below avg (-0.16); park/weather net drag (-20%).""", blast="good"),
            row("Amed Rosario", "R", "+800", 58, "", ["vs Peterson"], """0 HR, 94.0 mph EV. Peterson RHB split -0.12, HR risk -0.16. slight split headwind (-0.12); pitcher risk below avg (-0.16).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ BAL - Cristopher Sanchez (L, PHI) vs Shane Baz (R, BAL)",
        "description": "Tail key data: Park boost +5% (stadium -6%, weather +11%). Sanchez (HR risk -0.20, vs LHB -0.90, vs RHB +0.26). Baz (HR risk -0.66, vs LHB -0.45, vs RHB -0.51).",
        "rows": [
            row("Coby Mayo", "R", "+451", 84, "🚀 ⭐ 🌕 💣", ["vs Sanchez"], """Worst Pickz Favorite. 4 HR, 5 near-HR, 100.2 mph EV. Sanchez RHB split +0.26, HR risk -0.20. pitcher risk below avg (-0.20); park suppresses carry (-6%).""", blast="high"),
            row("Pete Alonso", "R", "+401", 75, "🌕 💣 💎", ["vs Sanchez"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 95.4 mph EV. Sanchez RHB split +0.26, HR risk -0.20. pitcher risk below avg (-0.20); park suppresses carry (-6%).""", blast="high"),
            row("Bryce Harper", "L", "+332", 58, "⭐", ["vs Baz"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.1 mph EV. Baz LHB split -0.45, HR risk -0.66. tough split lane (-0.45); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Bryson Stott", "L", "+640", 58, "", ["vs Baz"], """1 HR, 2 near-HR, 97.1 mph EV. Baz LHB split -0.45, HR risk -0.66. tough split lane (-0.45); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Derek Hill", "R", "N/A", 63, "🌕 💣", ["vs Baz"], """2 HR, 2 near-HR, 93.5 mph EV. Baz RHB split -0.51, HR risk -0.66. tough split lane (-0.51); pitcher suppresses HR (-0.66).""", blast="high"),
        ],
    },
    {
        "title": "PIT @ CIN - Braxton Ashcraft (R, PIT) vs Andrew Abbott (L, CIN)",
        "description": "Tail key data: Park boost +13% (stadium +13%, weather +0%). Ashcraft (HR risk 0.59, vs LHB +0.76, vs RHB -0.71). Abbott (HR risk -0.34, vs LHB -0.07, vs RHB -0.37).",
        "rows": [
            row("Eugenio Suarez", "R", "+420", 81, "⭐ 🌕 💣", ["vs Ashcraft"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.3 mph EV. Ashcraft RHB split -0.71, HR risk 0.59. tough split lane (-0.71).""", blast="high"),
            row("Elly De La Cruz", "S", "+321", 89, "🌕 💣", ["vs Ashcraft"], """2 HR, 2 near-HR, 93.7 mph EV. Ashcraft SHB→LHB split +0.76, HR risk 0.59.""", blast="high"),
            row("JJ Bleday", "L", "+369", 74, "", ["vs Ashcraft"], """1 HR, 1 near-HR, 88.2 mph EV. Ashcraft LHB split +0.76, HR risk 0.59.""", blast="good"),
            row("Esmerlyn Valdez", "R", "+272", 58, "", ["vs Abbott"], """1 HR, 1 near-HR, 92.1 mph EV. Abbott RHB split -0.37, HR risk -0.34. slight split headwind (-0.37); pitcher risk below avg (-0.34).""", blast="good"),
            row("Ryan O'Hearn", "L", "N/A", 60, "", ["vs Abbott"], """1 HR, 2 near-HR, 90.3 mph EV. Abbott LHB split -0.07, HR risk -0.34. slight split headwind (-0.07); pitcher risk below avg (-0.34).""", blast="good"),
        ],
    },
    {
        "title": "SF @ SD - Tyler Mahle (R, SF) vs Walker Buehler (R, SD)",
        "description": "Tail key data: Park boost -1% (stadium -6%, weather +5%). Mahle (HR risk -0.64, vs LHB -0.36, vs RHB -0.73). Buehler (HR risk 0.86, vs LHB +0.37, vs RHB +1.17).",
        "rows": [
            row("Ty France", "R", "+562", 58, "💎", ["vs Mahle"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.3 mph EV. Mahle RHB split -0.73, HR risk -0.64. tough split lane (-0.73); pitcher suppresses HR (-0.64).""", blast="good"),
            row("Jackson Merrill", "L", "+443", 58, "⭐", ["vs Mahle"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.3 mph EV. Mahle LHB split -0.36, HR risk -0.64. slight split headwind (-0.36); pitcher suppresses HR (-0.64).""", blast="good"),
            row("Manny Machado", "R", "+420", 58, "⭐", ["vs Mahle"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.3 mph EV. Mahle RHB split -0.73, HR risk -0.64. tough split lane (-0.73); pitcher suppresses HR (-0.64).""", blast="good"),
            row("Bryce Eldridge", "L", "+473", 72, "", ["vs Buehler"], """1 HR, 1 near-HR, 90.0 mph EV. Buehler LHB split +0.37, HR risk 0.86. park suppresses carry (-6%).""", blast="good"),
            row("Rafael Devers", "L", "+361", 75, "", ["vs Buehler"], """1 HR, 2 near-HR, 91.3 mph EV. Buehler LHB split +0.37, HR risk 0.86. park suppresses carry (-6%).""", blast="good"),
        ],
    },
    {
        "title": "STL @ TOR - Matthew Liberatore (L, STL) vs Kevin Gausman (R, TOR)",
        "description": "Tail key data: Park boost +11% (stadium +6%, weather +4%). Liberatore (HR risk -0.10, vs LHB -0.10, vs RHB +0.04). Gausman (HR risk -0.55, vs LHB -0.76, vs RHB +0.17).",
        "rows": [
            row("Kazuma Okamoto", "R", "+417", 65, "💎", ["vs Liberatore"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.3 mph EV. Liberatore RHB split +0.04, HR risk -0.10. pitcher risk below avg (-0.10).""", blast="good"),
            row("Vladimir Guerrero Jr.", "R", "+500", 58, "", ["vs Liberatore"], """0 HR, 92.3 mph EV. Liberatore RHB split +0.04, HR risk -0.10. pitcher risk below avg (-0.10); limited recent HR events.""", blast="good"),
            row("Jimmy Crooks", "L", "+630", 58, "💎", ["vs Gausman"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.4 mph EV. Gausman LHB split -0.76, HR risk -0.55. tough split lane (-0.76); pitcher suppresses HR (-0.55).""", blast="good"),
            row("Jordan Walker", "R", "+420", 58, "⭐", ["vs Gausman"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 91.7 mph EV. Gausman RHB split +0.17, HR risk -0.55. pitcher suppresses HR (-0.55).""", blast="good"),
            row("Alec Burleson", "L", "+420", 58, "⭐", ["vs Gausman"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 95.4 mph EV. Gausman LHB split -0.76, HR risk -0.55. tough split lane (-0.76); pitcher suppresses HR (-0.55).""", blast="good"),
            row("Lars Nootbaar", "L", "+492", 58, "", ["vs Gausman"], """0 HR, 96.3 mph EV. Gausman LHB split -0.76, HR risk -0.55. tough split lane (-0.76); pitcher suppresses HR (-0.55).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ HOU - Jacob deGrom (R, TEX) vs Ronel Blanco 🧤 (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +0%). deGrom (HR risk -0.04, vs LHB +0.14, vs RHB -0.26). Blanco 🧤 (HR risk 2.60, vs LHB +1.81, vs RHB +1.25).",
        "rows": [
            row("Jeremy Pena", "R", "+600", 70, "🌕 💣", ["vs deGrom"], """2 HR, 2 near-HR, 93.6 mph EV. deGrom RHB split -0.26, HR risk -0.04. slight split headwind (-0.26); pitcher risk below avg (-0.04).""", blast="high"),
            row("Yainer Diaz", "R", "+810", 61, "💎", ["vs deGrom"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.9 mph EV. deGrom RHB split -0.26, HR risk -0.04. slight split headwind (-0.26); pitcher risk below avg (-0.04).""", blast="good"),
            row("Taylor Trammell", "L", "+520", 59, "", ["vs deGrom"], """1 HR, 1 near-HR, 88.9 mph EV. deGrom LHB split +0.14, HR risk -0.04. pitcher risk below avg (-0.04).""", blast="good"),
            row("Jake Burger", "R", "+420", 95, "🌕 💣", ["vs Blanco"], """2 HR, 2 near-HR, 95.9 mph EV. Blanco RHB split +1.25, HR risk 2.60.""", blast="high"),
            row("Ezequiel Duran", "R", "+710", 91, "🌕 💣", ["vs Blanco"], """1 HR, 1 near-HR, 94.1 mph EV. Blanco RHB split +1.25, HR risk 2.60.""", blast="good"),
            row("Corey Seager", "L", "+310", 97, "🌕 💣 💎", ["vs Blanco"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 91.8 mph EV. Blanco LHB split +1.81, HR risk 2.60.""", blast="high"),
        ],
    },
    {
        "title": "WSH @ ATL - Miles Mikolas 🧤 (R, WSH) vs Reynaldo Lopez (R, ATL)",
        "description": "Tail key data: Park boost +2% (stadium -1%, weather +4%). Mikolas 🧤 (HR risk 1.00, vs LHB +0.41, vs RHB +1.35). Lopez (HR risk 0.23, vs LHB +0.20, vs RHB +0.12).",
        "rows": [
            row("Mike Yastrzemski", "L", "+560", 92, "🌕 💣 💎", ["vs Mikolas"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 93.9 mph EV. Mikolas LHB split +0.41, HR risk 1.00.""", blast="high"),
            row("Matt Olson", "L", "+324", 83, "", ["vs Mikolas"], """1 HR, 2 near-HR, 95.5 mph EV. Mikolas LHB split +0.41, HR risk 1.00.""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+340", 87, "💎", ["vs Mikolas"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.6 mph EV. Mikolas RHB split +1.35, HR risk 1.00.""", blast="good"),
            row("Drake Baldwin", "L", "+420", 83, "", ["vs Mikolas"], """1 HR, 2 near-HR, 94.8 mph EV. Mikolas LHB split +0.41, HR risk 1.00.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-01")

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

    out = ROOT / '_games-0801.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
