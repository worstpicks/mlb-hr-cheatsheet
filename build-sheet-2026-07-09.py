#!/usr/bin/env python3
"""Generate games[] block for 2026-07-09 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Brandon Lowe (L)",
    "Brandon Marsh (L)",
    "Ceddanne Rafaela (R)",
    "Elly De La Cruz (S)",
    "Garrett Mitchell (L)",
    "Heriberto Hernandez (R)",
    "Josh Bell (S)",
    "Josh Lowe (L)",
    "Kody Clemens (L)",
    "Kyle Schwarber (L)",
    "Kyle Stowers (L)",
    "Lars Nootbaar (L)",
    "Max Schuemann (R)",
    "Miguel Vargas (R)",
    "Mike Trout (R)",
    "Nick Kurtz (L)",
    "Owen Caissie (L)",
    "Salvador Perez (R)",
    "Spencer Torkelson (R)",
    "Tyler O'Neill (R)",
}

GEMS = {
    "Austin Hedges (R)",
    "Carson Kelly (R)",
    "Drake Baldwin (L)",
    "Eugenio Suarez (R)",
    "Joe Mack (L)",
    "Max Kepler (L)",
    "Michael Conforto (L)",
    "Riley Greene (L)",
    "Ryan O'Hearn (L)",
}

PLAYER_TEAMS = {
    "A.J. Ewing (L)": "NYM",
    "Alec Burleson (L)": "STL",
    "Austin Hedges (R)": "CLE",
    "Ben Malgeri (R)": "DET",
    "Ben Rice (L)": "NYY",
    "Bo Bichette (R)": "NYM",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Bryan Reynolds (S)": "PIT",
    "Cal Raleigh (S)": "SEA",
    "Carson Benge (L)": "NYM",
    "Carson Kelly (R)": "CHC",
    "Ceddanne Rafaela (R)": "BOS",
    "Coby Mayo (R)": "BAL",
    "Colby Thomas (R)": "ATH",
    "Colson Montgomery (L)": "CWS",
    "Colt Keith (L)": "DET",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Edouard Julien (L)": "COL",
    "Elly De La Cruz (S)": "CIN",
    "Eugenio Suarez (R)": "CIN",
    "Francisco Lindor (S)": "NYM",
    "Gabriel Arias (R)": "CLE",
    "Garrett Mitchell (L)": "MIL",
    "Geraldo Perdomo (S)": "ARI",
    "Heliot Ramos (R)": "SF",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ivan Herrera (R)": "STL",
    "J.T. Realmuto (R)": "PHI",
    "Jake Bauers (L)": "MIL",
    "Joe Mack (L)": "MIA",
    "Joey Bart (R)": "ATL",
    "Jordan Walker (R)": "STL",
    "Josh Bell (S)": "MIN",
    "Josh Lowe (L)": "LAA",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kody Clemens (L)": "MIN",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lars Nootbaar (L)": "STL",
    "Luis Campusano (R)": "SD",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Max Schuemann (R)": "NYY",
    "Michael Conforto (L)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Mitch Garver (R)": "SEA",
    "Nick Kurtz (L)": "ATH",
    "Otto Lopez (R)": "MIA",
    "Owen Caissie (L)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Randy Arozarena (R)": "SEA",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Royce Lewis (R)": "MIN",
    "Ryan O'Hearn (L)": "PIT",
    "Ryan Vilade (R)": "TB",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Shea Langeliers (R)": "ATH",
    "Spencer Torkelson (R)": "DET",
    "Tommy Troy (R)": "ARI",
    "Trevor Larnach (L)": "MIN",
    "Tyler O'Neill (R)": "BAL",
    "Tyler Stephenson (R)": "CIN",
    "William Contreras (R)": "MIL",
    "Willson Contreras (R)": "BOS",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("ARI @ SD", "Kelly"),
    ("CLE @ MIN", "Ober"),
    ("CLE @ MIN", "Williams"),
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
        "title": "ARI @ SD - Merrill Kelly 🧤 (R, ARI) vs Griffin Canning (R, SD)",
        "description": "Tail key data: Park boost +1% (stadium -5%, weather +6%). Kelly 🧤 (HR risk 1.07, vs LHB +0.49, vs RHB +1.11). Canning (HR risk 0.06, vs LHB +1.02, vs RHB -1.20).",
        "rows": [
            row("Manny Machado", "R", "+413", 96, "🌕 💣", ["vs Kelly"], """3 HR, 4 near-HR, 95.6 mph EV. Kelly RHB split +1.11, HR risk 1.07.""", blast="high"),
            row("Luis Campusano", "R", "+650", 90, "🌕 💣", ["vs Kelly"], """2 HR, 2 near-HR, 88.3 mph EV. Kelly RHB split +1.11, HR risk 1.07.""", blast="high"),
            row("Max Kepler", "L", "+544", 66, "💎", ["vs Canning"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 87.1 mph EV. Canning LHB split +1.02, HR risk 0.06. lighter EV form (87.1 mph).""", blast="good"),
            row("Tommy Troy", "R", "+950", 58, "", ["vs Canning"], """1 HR, 1 near-HR, 85.6 mph EV. Canning RHB split -1.20, HR risk 0.06. tough split lane (-1.20); lighter EV form (85.6 mph).""", blast="good"),
            row("Geraldo Perdomo", "S", "+920", 65, "", ["vs Canning"], """1 HR, 2 near-HR, 86.3 mph EV. Canning RHB split -1.20, HR risk 0.06. tough split lane (-1.20); lighter EV form (86.3 mph).""", blast="good"),
        ],
    },
    {
        "title": "ATH @ DET - Jack Perkins (R, ATH) vs Framber Valdez (L, DET)",
        "description": "Tail key data: Park boost +2% (stadium -11%, weather +13%). Perkins (HR risk 0.94, vs LHB +0.29, vs RHB +1.22). Valdez (HR risk -0.31, vs LHB -0.49, vs RHB -0.04).",
        "rows": [
            row("Riley Greene", "L", "+375", 90, "🌕 💣 💎", ["vs Perkins"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 92.8 mph EV. Perkins LHB split +0.29, HR risk 0.94. park suppresses carry (-11%).""", blast="high"),
            row("Dillon Dingler", "R", "+520", 89, "🌕 💣", ["vs Perkins"], """1 HR, 3 near-HR, 92.7 mph EV. Perkins RHB split +1.22, HR risk 0.94. park suppresses carry (-11%).""", blast="good"),
            row("Spencer Torkelson", "R", "+450", 92, "⭐ 🌕 💣", ["vs Perkins"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 90.1 mph EV. Perkins RHB split +1.22, HR risk 0.94. park suppresses carry (-11%).""", blast="high"),
            row("Colt Keith", "L", "+750", 64, "", ["vs Perkins"], """0 HR, 1 near-HR, 89.1 mph EV. Perkins LHB split +0.29, HR risk 0.94. park suppresses carry (-11%); limited recent HR events."""),
            row("Ben Malgeri", "R", "N/A", 80, "", ["vs Perkins"], """0 HR, 95.6 mph EV. Perkins RHB split +1.22, HR risk 0.94. park suppresses carry (-11%); limited recent HR events.""", blast="good"),
            row("Shea Langeliers", "R", "+335", 58, "", ["vs Valdez"], """0 HR, 87.1 mph EV. Valdez RHB split -0.04, HR risk -0.31. slight split headwind (-0.04); pitcher risk below avg (-0.31)."""),
            row("Colby Thomas", "R", "+620", 58, "", ["vs Valdez"], """1 HR, 1 near-HR, 91.8 mph EV. Valdez RHB split -0.04, HR risk -0.31. slight split headwind (-0.04); pitcher risk below avg (-0.31).""", blast="good"),
            row("Nick Kurtz", "L", "+370", 60, "🚀 ⭐", ["vs Valdez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 100.7 mph EV. Valdez LHB split -0.49, HR risk -0.31. tough split lane (-0.49); pitcher risk below avg (-0.31).""", blast="good"),
            row("Zack Gelof", "R", "+660", 58, "", ["vs Valdez"], """1 HR, 1 near-HR, 91.7 mph EV. Valdez RHB split -0.04, HR risk -0.31. slight split headwind (-0.04); pitcher risk below avg (-0.31).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ PIT - Bryce Elder (R, ATL) vs Mitch Keller (R, PIT)",
        "description": "Tail key data: Park boost -5% (stadium -15%, weather +10%). Elder (HR risk 0.46, vs LHB +0.07, vs RHB +0.84). Keller (HR risk 0.48, vs LHB +0.82, vs RHB -0.52).",
        "rows": [
            row("Brandon Lowe", "L", "+342", 86, "⭐ 🌕 💣", ["vs Elder"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 96.0 mph EV. Elder LHB split +0.07, HR risk 0.46. park/weather net drag (-5%).""", blast="high"),
            row("Ryan O'Hearn", "L", "+660", 81, "🌕 💣 💎", ["vs Elder"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 92.0 mph EV. Elder LHB split +0.07, HR risk 0.46. park/weather net drag (-5%).""", blast="high"),
            row("Bryan Reynolds", "S", "+620", 69, "", ["vs Elder"], """1 HR, 2 near-HR, 85.0 mph EV. Elder RHB split +0.84, HR risk 0.46. park/weather net drag (-5%); lighter EV form (85.0 mph).""", blast="good"),
            row("Matt Olson", "L", "+281", 90, "🌕 💣", ["vs Keller"], """2 HR, 3 near-HR, 94.5 mph EV. Keller LHB split +0.82, HR risk 0.48. park/weather net drag (-5%).""", blast="high"),
            row("Drake Baldwin", "L", "+442", 71, "💎", ["vs Keller"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.0 mph EV. Keller LHB split +0.82, HR risk 0.48. park/weather net drag (-5%).""", blast="good"),
            row("Joey Bart", "R", "N/A", 67, "", ["vs Keller"], """1 HR, 3 near-HR, 90.4 mph EV. Keller RHB split -0.52, HR risk 0.48. tough split lane (-0.52); park/weather net drag (-5%).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ CWS - Patrick Sandoval (L, BOS) vs Anthony Kay (L, CWS)",
        "description": "Tail key data: Park boost +14% (stadium +4%, weather +11%). Away starter risk unavailable. Kay (HR risk -0.95, vs LHB -0.82, vs RHB -0.62).",
        "rows": [
            row("Colson Montgomery", "L", "+317", 60, "", ["vs Sandoval"], """1 HR, 1 near-HR, 85.5 mph EV. Sandoval split/risk data unavailable. limited split/risk sample; lighter EV form (85.5 mph).""", blast="good"),
            row("Miguel Vargas", "R", "+336", 62, "⭐", ["vs Sandoval"], """Worst Pickz Favorite. 0 HR, 93.5 mph EV. Sandoval split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Ceddanne Rafaela", "R", "+620", 58, "⭐", ["vs Kay"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 85.4 mph EV. Kay RHB split -0.62, HR risk -0.95. tough split lane (-0.62); pitcher suppresses HR (-0.95).""", blast="good"),
            row("Willson Contreras", "R", "+336", 58, "", ["vs Kay"], """1 HR, 2 near-HR, 86.0 mph EV. Kay RHB split -0.62, HR risk -0.95. tough split lane (-0.62); pitcher suppresses HR (-0.95).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ BAL - David Peterson (L, CHC) vs Trevor Rogers (L, BAL)",
        "description": "Tail key data: Park boost +16% (stadium -4%, weather +20%). Peterson (HR risk 0.46, vs LHB +0.89, vs RHB -0.04). Rogers (HR risk -0.93, vs LHB -1.28, vs RHB -0.30).",
        "rows": [
            row("Pete Alonso", "R", "+310", 70, "", ["vs Peterson"], """0 HR, 96.0 mph EV. Peterson RHB split -0.04, HR risk 0.46. slight split headwind (-0.04); limited recent HR events.""", blast="good"),
            row("Tyler O'Neill", "R", "+445", 85, "⭐ 🌕 💣", ["vs Peterson"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.2 mph EV. Peterson RHB split -0.04, HR risk 0.46. slight split headwind (-0.04).""", blast="high"),
            row("Coby Mayo", "R", "+364", 85, "🌕 💣", ["vs Peterson"], """2 HR, 2 near-HR, 97.4 mph EV. Peterson RHB split -0.04, HR risk 0.46. slight split headwind (-0.04).""", blast="high"),
            row("Michael Conforto", "L", "N/A", 58, "💎", ["vs Rogers"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.6 mph EV. Rogers LHB split -1.28, HR risk -0.93. tough split lane (-1.28); pitcher suppresses HR (-0.93).""", blast="good"),
            row("Carson Kelly", "R", "+480", 58, "💎", ["vs Rogers"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 91.4 mph EV. Rogers RHB split -0.30, HR risk -0.93. slight split headwind (-0.30); pitcher suppresses HR (-0.93).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ MIN - Gavin Williams 🧤 (R, CLE) vs Bailey Ober 🧤 (R, MIN)",
        "description": "Tail key data: Park boost +2% (stadium -8%, weather +9%). Williams 🧤 (HR risk 1.16, vs LHB +0.36, vs RHB +1.81). Ober 🧤 (HR risk 1.27, vs LHB +1.59, vs RHB -0.33).",
        "rows": [
            row("Kody Clemens", "L", "+412", 93, "⭐ 🌕 💣", ["vs Williams"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 98.0 mph EV. Williams LHB split +0.36, HR risk 1.16. park suppresses carry (-8%).""", blast="high"),
            row("Royce Lewis", "R", "+524", 92, "🌕 💣", ["vs Williams"], """0 HR, 3 near-HR, 93.9 mph EV. Williams RHB split +1.81, HR risk 1.16. park suppresses carry (-8%).""", blast="good"),
            row("Josh Bell", "S", "+520", 93, "⭐ 🌕 💣", ["vs Williams"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 92.0 mph EV. Williams RHB split +1.81, HR risk 1.16. park suppresses carry (-8%).""", blast="good"),
            row("Trevor Larnach", "L", "+690", 84, "", ["vs Williams"], """0 HR, 3 near-HR, 94.9 mph EV. Williams LHB split +0.36, HR risk 1.16. park suppresses carry (-8%).""", blast="good"),
            row("Austin Hedges", "R", "N/A", 80, "💎", ["vs Ober"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 91.6 mph EV. Ober RHB split -0.33, HR risk 1.27. slight split headwind (-0.33); park suppresses carry (-8%).""", blast="good"),
            row("Rhys Hoskins", "R", "+400", 79, "", ["vs Ober"], """1 HR, 1 near-HR, 95.9 mph EV. Ober RHB split -0.33, HR risk 1.27. slight split headwind (-0.33); park suppresses carry (-8%).""", blast="good"),
            row("Gabriel Arias", "R", "+299", 74, "", ["vs Ober"], """1 HR, 1 near-HR, 91.5 mph EV. Ober RHB split -0.33, HR risk 1.27. slight split headwind (-0.33); park suppresses carry (-8%).""", blast="good"),
        ],
    },
    {
        "title": "COL @ SF - Ryan Feltner (R, COL) vs Carson Whisenhunt (L, SF)",
        "description": "Tail key data: Park boost -21% (stadium -16%, weather -6%). Feltner (HR risk 0.01, vs LHB +0.70, vs RHB -0.61). Home starter risk unavailable.",
        "rows": [
            row("Heliot Ramos", "R", "+595", 69, "🌕 💣", ["vs Feltner"], """3 HR, 5 near-HR, 92.8 mph EV. Feltner RHB split -0.61, HR risk 0.01. tough split lane (-0.61); park/weather net drag (-21%).""", blast="high"),
            row("Hunter Goodman", "R", "+253", 67, "🌕 💣", ["vs Whisenhunt"], """2 HR, 3 near-HR, 87.7 mph EV. Whisenhunt split/risk data unavailable. limited split/risk sample; park/weather net drag (-21%).""", blast="high"),
            row("Kyle Karros", "R", "+630", 76, "🌕 💣", ["vs Whisenhunt"], """3 HR, 3 near-HR, 92.8 mph EV. Whisenhunt split/risk data unavailable. limited split/risk sample; park/weather net drag (-21%).""", blast="high"),
            row("Edouard Julien", "L", "+870", 58, "", ["vs Whisenhunt"], """0 HR, 91.4 mph EV. Whisenhunt split/risk data unavailable. limited split/risk sample; park/weather net drag (-21%)."""),
        ],
    },
    {
        "title": "KC @ NYM - Michael Wacha (R, KC) vs Sean Manaea (L, NYM)",
        "description": "Tail key data: Park boost +16% (stadium -1%, weather +17%). Wacha (HR risk -0.68, vs LHB -0.43, vs RHB -0.28). Manaea (HR risk -0.13, vs LHB -0.88, vs RHB +0.48).",
        "rows": [
            row("Juan Soto", "L", "+256", 65, "🌕 💣", ["vs Wacha"], """2 HR, 2 near-HR, 92.2 mph EV. Wacha LHB split -0.43, HR risk -0.68. tough split lane (-0.43); pitcher suppresses HR (-0.68).""", blast="high"),
            row("Francisco Lindor", "S", "+420", 60, "", ["vs Wacha"], """1 HR, 1 near-HR, 95.4 mph EV. Wacha RHB split -0.28, HR risk -0.68. slight split headwind (-0.28); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Carson Benge", "L", "+551", 58, "", ["vs Wacha"], """0 HR, 89.1 mph EV. Wacha LHB split -0.43, HR risk -0.68. tough split lane (-0.43); pitcher suppresses HR (-0.68)."""),
            row("Bo Bichette", "R", "+523", 58, "", ["vs Wacha"], """0 HR, 1 near-HR, 86.8 mph EV. Wacha RHB split -0.28, HR risk -0.68. slight split headwind (-0.28); pitcher suppresses HR (-0.68)."""),
            row("A.J. Ewing", "L", "+750", 58, "", ["vs Wacha"], """1 HR, 2 near-HR, 91.7 mph EV. Wacha LHB split -0.43, HR risk -0.68. tough split lane (-0.43); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Salvador Perez", "R", "+323", 66, "⭐", ["vs Manaea"], """Worst Pickz Favorite. 0 HR, 96.5 mph EV. Manaea RHB split +0.48, HR risk -0.13. pitcher risk below avg (-0.13); limited recent HR events.""", blast="good"),
            row("Bobby Witt Jr.", "R", "+333", 65, "", ["vs Manaea"], """0 HR, 95.5 mph EV. Manaea RHB split +0.48, HR risk -0.13. pitcher risk below avg (-0.13); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "LAA @ TEX - Reid Detmers (L, LAA) vs Nathan Eovaldi (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -11%, weather +0%). Detmers (HR risk -0.69, vs LHB -1.19, vs RHB -0.10). Eovaldi (HR risk 0.33, vs LHB +0.28, vs RHB +0.19).",
        "rows": [
            row("Justin Foscue", "R", "+518", 58, "🌕 💣", ["vs Detmers"], """2 HR, 2 near-HR, 88.8 mph EV. Detmers RHB split -0.10, HR risk -0.69. slight split headwind (-0.10); pitcher suppresses HR (-0.69).""", blast="high"),
            row("Mike Trout", "R", "+380", 79, "⭐ 🌕 💣", ["vs Eovaldi"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 91.3 mph EV. Eovaldi RHB split +0.19, HR risk 0.33. park/weather net drag (-11%).""", blast="high"),
            row("Josh Lowe", "L", "+680", 82, "⭐ 🌕 💣", ["vs Eovaldi"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 96.5 mph EV. Eovaldi LHB split +0.28, HR risk 0.33. park/weather net drag (-11%).""", blast="high"),
        ],
    },
    {
        "title": "MIL @ STL - Logan Henderson (R, MIL) vs Andre Pallante (R, STL)",
        "description": "Tail key data: Park boost -9% (stadium -10%, weather +1%). Henderson (HR risk -0.29, vs LHB -0.30, vs RHB +0.45). Pallante (HR risk -1.24, vs LHB -0.76, vs RHB -0.84).",
        "rows": [
            row("Lars Nootbaar", "L", "+422", 58, "⭐", ["vs Henderson"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 92.9 mph EV. Henderson LHB split -0.30, HR risk -0.29. slight split headwind (-0.30); pitcher risk below avg (-0.29).""", blast="good"),
            row("Alec Burleson", "L", "+382", 58, "", ["vs Henderson"], """0 HR, 1 near-HR, 95.9 mph EV. Henderson LHB split -0.30, HR risk -0.29. slight split headwind (-0.30); pitcher risk below avg (-0.29).""", blast="good"),
            row("Ivan Herrera", "R", "+587", 58, "", ["vs Henderson"], """1 HR, 1 near-HR, 88.1 mph EV. Henderson RHB split +0.45, HR risk -0.29. pitcher risk below avg (-0.29); park/weather net drag (-9%).""", blast="good"),
            row("Jordan Walker", "R", "+390", 60, "", ["vs Henderson"], """1 HR, 1 near-HR, 92.4 mph EV. Henderson RHB split +0.45, HR risk -0.29. pitcher risk below avg (-0.29); park/weather net drag (-9%).""", blast="good"),
            row("Jake Bauers", "L", "+500", 58, "", ["vs Pallante"], """0 HR, 86.1 mph EV. Pallante LHB split -0.76, HR risk -1.24. tough split lane (-0.76); pitcher suppresses HR (-1.24)."""),
            row("Garrett Mitchell", "L", "+650", 58, "🚀 ⭐", ["vs Pallante"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 100.0 mph EV. Pallante LHB split -0.76, HR risk -1.24. tough split lane (-0.76); pitcher suppresses HR (-1.24).""", blast="good"),
            row("William Contreras", "R", "+820", 58, "", ["vs Pallante"], """0 HR, 99.0 mph EV. Pallante RHB split -0.84, HR risk -1.24. tough split lane (-0.84); pitcher suppresses HR (-1.24).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ TB - Ryan Yarbrough (L, NYY) vs Drew Rasmussen (R, TB)",
        "description": "Tail key data: Park boost -2% (stadium -3%, weather +0%). Away starter risk unavailable. Rasmussen (HR risk -0.44, vs LHB -0.04, vs RHB -0.53).",
        "rows": [
            row("Ryan Vilade", "R", "N/A", 61, "", ["vs Yarbrough"], """1 HR, 1 near-HR, 91.4 mph EV. Yarbrough split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Junior Caminero", "R", "+253", 83, "🌕 💣", ["vs Yarbrough"], """5 HR, 5 near-HR, 95.1 mph EV. Yarbrough split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Ben Rice", "L", "+444", 58, "⭐", ["vs Rasmussen"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 87.6 mph EV. Rasmussen LHB split -0.04, HR risk -0.44. slight split headwind (-0.04); pitcher suppresses HR (-0.44).""", blast="good"),
            row("Max Schuemann", "R", "N/A", 58, "⭐", ["vs Rasmussen"], """Worst Pickz Favorite. 0 HR, 92.7 mph EV. Rasmussen RHB split -0.53, HR risk -0.44. tough split lane (-0.53); pitcher suppresses HR (-0.44).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ CIN - Jesus Luzardo (L, PHI) vs Brady Singer (R, CIN)",
        "description": "Tail key data: Park boost +28% (stadium +14%, weather +13%). Luzardo (HR risk -1.58, vs LHB -1.37, vs RHB -0.93). Singer (HR risk 0.38, vs LHB +0.78, vs RHB -0.58).",
        "rows": [
            row("Tyler Stephenson", "R", "+570", 58, "", ["vs Luzardo"], """0 HR, 1 near-HR, 92.0 mph EV. Luzardo RHB split -0.93, HR risk -1.58. tough split lane (-0.93); pitcher suppresses HR (-1.58).""", blast="good"),
            row("Elly De La Cruz", "S", "+425", 58, "🚀 ⭐", ["vs Luzardo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 101.1 mph EV. Luzardo RHB split -0.93, HR risk -1.58. tough split lane (-0.93); pitcher suppresses HR (-1.58).""", blast="good"),
            row("Sal Stewart", "R", "+390", 58, "", ["vs Luzardo"], """1 HR, 1 near-HR, 92.8 mph EV. Luzardo RHB split -0.93, HR risk -1.58. tough split lane (-0.93); pitcher suppresses HR (-1.58).""", blast="good"),
            row("Eugenio Suarez", "R", "+401", 58, "💎", ["vs Luzardo"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.9 mph EV. Luzardo RHB split -0.93, HR risk -1.58. tough split lane (-0.93); pitcher suppresses HR (-1.58).""", blast="good"),
            row("Kyle Schwarber", "L", "+150", 76, "⭐", ["vs Singer"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 90.8 mph EV. Singer LHB split +0.78, HR risk 0.38.""", blast="good"),
            row("Brandon Marsh", "L", "+447", 89, "⭐ 🌕 💣", ["vs Singer"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 90.1 mph EV. Singer LHB split +0.78, HR risk 0.38.""", blast="high"),
            row("J.T. Realmuto", "R", "+620", 60, "", ["vs Singer"], """1 HR, 1 near-HR, 83.3 mph EV. Singer RHB split -0.58, HR risk 0.38. tough split lane (-0.58); lighter EV form (83.3 mph).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ MIA - Bryce Miller (R, SEA) vs Janson Junk (R, MIA)",
        "description": "Tail key data: Park boost -12% (stadium -12%, weather +0%). Miller (HR risk 0.28, vs LHB -0.12, vs RHB +0.70). Junk (HR risk 0.37, vs LHB +0.39, vs RHB +0.14).",
        "rows": [
            row("Heriberto Hernandez", "R", "+573", 83, "⭐ 🌕 💣", ["vs Miller"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.5 mph EV. Miller RHB split +0.70, HR risk 0.28. park/weather net drag (-12%).""", blast="high"),
            row("Owen Caissie", "L", "+550", 77, "⭐ 🌕 💣", ["vs Miller"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.8 mph EV. Miller LHB split -0.12, HR risk 0.28. slight split headwind (-0.12); park/weather net drag (-12%).""", blast="high"),
            row("Kyle Stowers", "L", "+390", 73, "🚀 ⭐ 🌕 💣", ["vs Miller"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 102.2 mph EV. Miller LHB split -0.12, HR risk 0.28. slight split headwind (-0.12); park/weather net drag (-12%).""", blast="high"),
            row("Otto Lopez", "R", "+840", 74, "🌕 💣", ["vs Miller"], """2 HR, 3 near-HR, 84.0 mph EV. Miller RHB split +0.70, HR risk 0.28. park/weather net drag (-12%); lighter EV form (84.0 mph).""", blast="high"),
            row("Joe Mack", "L", "+750", 76, "🌕 💣 💎", ["vs Miller"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 91.7 mph EV. Miller LHB split -0.12, HR risk 0.28. slight split headwind (-0.12); park/weather net drag (-12%).""", blast="high"),
            row("Dominic Canzone", "L", "+446", 58, "", ["vs Junk"], """0 HR, 1 near-HR, 89.8 mph EV. Junk LHB split +0.39, HR risk 0.37. park/weather net drag (-12%); limited recent HR events."""),
            row("Cal Raleigh", "S", "+306", 67, "", ["vs Junk"], """1 HR, 1 near-HR, 94.9 mph EV. Junk RHB split +0.14, HR risk 0.37. park/weather net drag (-12%).""", blast="good"),
            row("Mitch Garver", "R", "N/A", 61, "", ["vs Junk"], """1 HR, 1 near-HR, 90.8 mph EV. Junk RHB split +0.14, HR risk 0.37. park/weather net drag (-12%).""", blast="good"),
            row("Randy Arozarena", "R", "+540", 75, "🌕 💣", ["vs Junk"], """2 HR, 3 near-HR, 91.3 mph EV. Junk RHB split +0.14, HR risk 0.37. park/weather net drag (-12%).""", blast="high"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-09")

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

    out = ROOT / '_games-0709.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
