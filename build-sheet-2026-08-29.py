#!/usr/bin/env python3
"""Generate games[] block for 2026-08-29 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Blaze Alexander (R)",
    "Bobby Witt Jr. (R)",
    "Carter Jensen (L)",
    "Coby Mayo (R)",
    "Elly De La Cruz (S)",
    "JJ Bleday (L)",
    "Jake Burger (R)",
    "Jo Adell (R)",
    "Junior Caminero (R)",
    "Lawrence Butler (L)",
    "Matt Olson (L)",
    "Michael Conforto (L)",
    "Michael Harris II (L)",
    "Pete Alonso (R)",
    "Rafael Devers (L)",
    "Spencer Jones (L)",
    "Tyler Stephenson (R)",
}

GEMS = {
    "Ben Rice (L)",
    "Eduardo Valencia (R)",
    "Jac Caglianone (L)",
    "Jackson Chourio (R)",
    "Jahmai Jones (R)",
    "Jake Bauers (L)",
    "Jimmy Crooks (L)",
    "Jonathan Aranda (L)",
    "Kyle Stowers (L)",
    "Max Muncy (L)",
    "Sal Stewart (R)",
    "Trent Grisham (L)",
    "Trevor Larnach (L)",
}

PLAYER_TEAMS = {
    "Alec Bohm (R)": "PHI",
    "Alejandro Kirk (R)": "TOR",
    "Andres Chaparro (R)": "WSH",
    "Ben Rice (L)": "NYY",
    "Blaze Alexander (R)": "BAL",
    "Bo Bichette (R)": "NYM",
    "Bobby Witt Jr. (R)": "KC",
    "Brady House (R)": "WSH",
    "Brandon Valenzuela (S)": "TOR",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Carter Jensen (L)": "KC",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Coby Mayo (R)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Daylen Lile (L)": "WSH",
    "Dominic Canzone (L)": "SEA",
    "Donovan Walton (L)": "ATH",
    "Drake Baldwin (L)": "ATL",
    "Drew Cavanaugh (L)": "SF",
    "Eduardo Valencia (R)": "DET",
    "Elias Diaz (R)": "TEX",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Francisco Alvarez (R)": "NYM",
    "Gabriel Moreno (R)": "ARI",
    "George Springer (R)": "TOR",
    "Griffin Conine (L)": "MIA",
    "Heliot Ramos (R)": "NYY",
    "Hunter Feduccia (L)": "LAD",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "JT Realmuto (R)": "PHI",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jahmai Jones (R)": "BOS",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "CLE",
    "Jonathan Aranda (L)": "TB",
    "Jose Siri (R)": "LAA",
    "Josh Naylor (L)": "SEA",
    "Junior Caminero (R)": "TB",
    "Kaelen Culpepper (R)": "MIN",
    "Kevin McGonigle (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lars Nootbaar (L)": "ARI",
    "Lawrence Butler (L)": "ATH",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Michael Busch (L)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Mike Yastrzemski (L)": "ATL",
    "Moises Ballesteros (L)": "LAA",
    "Nelson Velazquez (R)": "HOU",
    "Nick Allen (R)": "HOU",
    "Oneil Cruz (L)": "PIT",
    "Owen Caissie (L)": "MIA",
    "Patrick Bailey (S)": "CLE",
    "Paul Goldschmidt (R)": "NYY",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "TJ Rumfield (L)": "COL",
    "Trent Grisham (L)": "NYY",
    "Trevor Larnach (L)": "MIN",
    "Tristan Peters (L)": "CWS",
    "Troy Johnston (L)": "COL",
    "Turner Hill (L)": "SF",
    "Tyler Stephenson (R)": "CIN",
    "William Contreras (R)": "MIL",
    "Willson Contreras (R)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("PHI @ LAA", "Johnson"),
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
        "title": "ARI @ SF - Merrill Kelly (R, ARI) vs Anthony Molina (R, SF)",
        "description": "Tail key data: Park boost -26% (stadium -20%, weather -6%). Kelly (BAA vs LHB .284, vs RHB .265, HR/9 1.74). Molina (BAA vs LHB .250, vs RHB .154, HR/9 0.96).",
        "rows": [
            row("Rafael Devers", "L", "N/A", 79, "🚀 ⭐ 🌕 💣", ["vs Kelly"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 102.0 mph EV. limited split/risk sample; park/weather net drag (-26%).""", blast="high"),
            row("Bryce Eldridge", "L", "N/A", 58, "", ["vs Kelly"], """0 HR, 95.1 mph EV. limited split/risk sample; park/weather net drag (-26%).""", blast="good"),
            row("Drew Cavanaugh", "L", "N/A", 58, "", ["vs Kelly"], """0 HR, 1 near-HR, 93.7 mph EV. limited split/risk sample; park/weather net drag (-26%).""", blast="good"),
            row("Turner Hill", "L", "N/A", 58, "", ["vs Kelly"], """0 HR, 2 near-HR, 94.3 mph EV. limited split/risk sample; park/weather net drag (-26%).""", blast="good"),
            row("Gabriel Moreno", "R", "N/A", 71, "🌕 💣", ["vs Molina"], """2 HR, 4 near-HR, 90.4 mph EV. limited split/risk sample; park/weather net drag (-26%).""", blast="high"),
            row("Lars Nootbaar", "L", "N/A", 58, "", ["vs Molina"], """0 HR, 94.3 mph EV. limited split/risk sample; park/weather net drag (-26%).""", blast="good"),
            row("Corbin Carroll", "L", "N/A", 58, "", ["vs Molina"], """0 HR, 89.6 mph EV. limited split/risk sample; park/weather net drag (-26%)."""),
        ],
    },
    {
        "title": "BAL @ ATH - Shane Baz (R, BAL) vs Jack Perkins (R, ATH)",
        "description": "Tail key data: Park boost +38% (stadium +30%, weather +7%). Baz (HR risk -0.25, vs LHB -0.02, vs RHB -0.68). Perkins (BAA vs LHB .262, vs RHB .270, HR/9 1.69).",
        "rows": [
            row("Lawrence Butler", "L", "N/A", 63, "⭐", ["vs Baz"], """Worst Pickz Favorite. 0 HR, 93.2 mph EV. Baz LHB split -0.02, HR risk -0.25. slight split headwind (-0.02); pitcher risk below avg (-0.25).""", blast="good"),
            row("Donovan Walton", "L", "N/A", 58, "", ["vs Baz"], """0 HR, 91.2 mph EV. Baz LHB split -0.02, HR risk -0.25. slight split headwind (-0.02); pitcher risk below avg (-0.25)."""),
            row("Pete Alonso", "R", "N/A", 86, "⭐ 🌕 💣", ["vs Perkins"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.6 mph EV. limited split/risk sample.""", blast="high"),
            row("Christian Encarnacion-Strand", "R", "N/A", 70, "", ["vs Perkins"], """0 HR, 95.3 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Coby Mayo", "R", "N/A", 62, "⭐", ["vs Perkins"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 90.5 mph EV. limited split/risk sample; limited recent HR events."""),
            row("Blaze Alexander", "R", "N/A", 68, "⭐", ["vs Perkins"], """Worst Pickz Favorite. 0 HR, 93.5 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "BOS @ NYY (G1) - Jake Bennett (L, BOS) vs Carlos Rodon (L, NYY)",
        "description": "Tail key data: Park boost -3% (stadium +4%, weather -7%). Bennett (HR risk -0.21, vs LHB -1.14, vs RHB +0.35). Rodon (HR risk -0.39, vs LHB -0.23, vs RHB -0.39).",
        "rows": [
            row("Paul Goldschmidt", "R", "N/A", 63, "", ["vs Bennett"], """1 HR, 1 near-HR, 94.0 mph EV. Bennett RHB split +0.35, HR risk -0.21. pitcher risk below avg (-0.21); weather carry headwind (-7%).""", blast="good"),
            row("Ben Rice", "L", "N/A", 58, "", ["vs Bennett"], """1 HR, 2 near-HR, 96.8 mph EV. Bennett LHB split -1.14, HR risk -0.21. tough split lane (-1.14); pitcher risk below avg (-0.21).""", blast="good"),
            row("Heliot Ramos", "R", "N/A", 59, "", ["vs Bennett"], """0 HR, 95.6 mph EV. Bennett RHB split +0.35, HR risk -0.21. pitcher risk below avg (-0.21); weather carry headwind (-7%).""", blast="good"),
            row("Jahmai Jones", "R", "N/A", 58, "", ["vs Rodon"], """1 HR, 1 near-HR, 93.6 mph EV. Rodon RHB split -0.39, HR risk -0.39. slight split headwind (-0.39); pitcher risk below avg (-0.39).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ NYY (G2) - Brayan Bello (R, BOS) vs Max Fried (L, NYY)",
        "description": "Tail key data: Park boost -2% (stadium +4%, weather -5%). Bello (BAA vs LHB .280, vs RHB .270, HR/9 1.10). Fried (HR risk -1.19, vs LHB -0.72, vs RHB -1.03).",
        "rows": [
            row("Trent Grisham", "L", "N/A", 61, "💎", ["vs Bello"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.2 mph EV. limited split/risk sample; weather carry headwind (-5%).""", blast="good"),
            row("Spencer Jones", "L", "N/A", 66, "🚀 ⭐", ["vs Bello"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 100.2 mph EV. limited split/risk sample; weather carry headwind (-5%).""", blast="good"),
            row("Ben Rice", "L", "N/A", 60, "💎", ["vs Bello"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 89.6 mph EV. limited split/risk sample; weather carry headwind (-5%).""", blast="good"),
            row("Jahmai Jones", "R", "N/A", 58, "💎", ["vs Fried"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.7 mph EV. Fried RHB split -1.03, HR risk -1.19. tough split lane (-1.03); pitcher suppresses HR (-1.19).""", blast="good"),
            row("Willson Contreras", "R", "N/A", 58, "", ["vs Fried"], """0 HR, 91.4 mph EV. Fried RHB split -1.03, HR risk -1.19. tough split lane (-1.03); pitcher suppresses HR (-1.19)."""),
        ],
    },
    {
        "title": "CIN @ CHC - Andrew Abbott (L, CIN) vs Kevin Gausman (R, CHC)",
        "description": "Tail key data: Park boost +15% (stadium -3%, weather +18%). Abbott (HR risk -0.35, vs LHB -0.28, vs RHB -0.21). Gausman (HR risk -0.16, vs LHB +0.00, vs RHB -0.53).",
        "rows": [
            row("Michael Conforto", "L", "N/A", 63, "🚀 ⭐", ["vs Abbott"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 106.4 mph EV. Abbott LHB split -0.28, HR risk -0.35. slight split headwind (-0.28); pitcher risk below avg (-0.35).""", blast="good"),
            row("Pete Crow Armstrong", "L", "+360", 61, "", ["vs Abbott"], """1 HR, 2 near-HR, 92.4 mph EV. Abbott LHB split -0.28, HR risk -0.35. slight split headwind (-0.28); pitcher risk below avg (-0.35).""", blast="good"),
            row("Michael Busch", "L", "+470", 58, "", ["vs Abbott"], """1 HR, 2 near-HR, 88.9 mph EV. Abbott LHB split -0.28, HR risk -0.35. slight split headwind (-0.28); pitcher risk below avg (-0.35).""", blast="good"),
            row("JJ Bleday", "L", "+430", 66, "⭐", ["vs Gausman"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.2 mph EV. Gausman LHB split +0.00, HR risk -0.16. pitcher risk below avg (-0.16).""", blast="good"),
            row("Tyler Stephenson", "R", "+560", 67, "⭐ 🌕 💣", ["vs Gausman"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.5 mph EV. Gausman RHB split -0.53, HR risk -0.16. tough split lane (-0.53); pitcher risk below avg (-0.16).""", blast="high"),
            row("Sal Stewart", "R", "+440", 58, "💎", ["vs Gausman"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.0 mph EV. Gausman RHB split -0.53, HR risk -0.16. tough split lane (-0.53); pitcher risk below avg (-0.16).""", blast="good"),
            row("Elly De La Cruz", "S", "+420", 61, "⭐", ["vs Gausman"], """Worst Pickz Favorite. 0 HR, 98.3 mph EV. Gausman SHB→LHB split +0.00, HR risk -0.16. pitcher risk below avg (-0.16); limited recent HR events.""", blast="good"),
            row("Matt McLain", "R", "+600", 66, "🌕 💣", ["vs Gausman"], """2 HR, 2 near-HR, 90.2 mph EV. Gausman RHB split -0.53, HR risk -0.16. tough split lane (-0.53); pitcher risk below avg (-0.16).""", blast="high"),
        ],
    },
    {
        "title": "COL @ ATL - Ryan Feltner (R, COL) vs Martin Perez (L, ATL)",
        "description": "Tail key data: Park boost -4% (stadium -2%, weather -1%). Feltner (HR risk 0.44, vs LHB +0.05, vs RHB +0.77). Perez (HR risk -0.69, vs LHB +0.20, vs RHB -1.00).",
        "rows": [
            row("Matt Olson", "L", "N/A", 67, "⭐", ["vs Feltner"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 98.5 mph EV. Feltner LHB split +0.05, HR risk 0.44. limited recent HR events.""", blast="good"),
            row("Michael Harris II", "L", "N/A", 58, "⭐", ["vs Feltner"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 91.1 mph EV. Feltner LHB split +0.05, HR risk 0.44. limited recent HR events."""),
            row("Drake Baldwin", "L", "N/A", 71, "", ["vs Feltner"], """1 HR, 2 near-HR, 94.5 mph EV. Feltner LHB split +0.05, HR risk 0.44.""", blast="good"),
            row("Mike Yastrzemski", "L", "N/A", 65, "", ["vs Feltner"], """0 HR, 96.7 mph EV. Feltner LHB split +0.05, HR risk 0.44. limited recent HR events.""", blast="good"),
            row("Troy Johnston", "L", "N/A", 58, "", ["vs Perez"], """0 HR, 1 near-HR, 90.0 mph EV. Perez LHB split +0.20, HR risk -0.69. pitcher suppresses HR (-0.69); limited recent HR events."""),
            row("TJ Rumfield", "L", "N/A", 58, "", ["vs Perez"], """0 HR, 86.5 mph EV. Perez LHB split +0.20, HR risk -0.69. pitcher suppresses HR (-0.69); limited recent HR events."""),
        ],
    },
    {
        "title": "CWS @ MIN - Erick Fedde (R, CWS) vs Bailey Ober (R, MIN)",
        "description": "Tail key data: Park boost -4% (stadium -7%, weather +3%). Fedde (HR risk 0.23, vs LHB -0.27, vs RHB +1.06). Ober (HR risk 0.94, vs LHB +0.34, vs RHB +1.19).",
        "rows": [
            row("Kaelen Culpepper", "R", "N/A", 72, "", ["vs Fedde"], """1 HR, 1 near-HR, 94.2 mph EV. Fedde RHB split +1.06, HR risk 0.23. park suppresses carry (-7%).""", blast="good"),
            row("Trevor Larnach", "L", "N/A", 62, "💎", ["vs Fedde"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.1 mph EV. Fedde LHB split -0.27, HR risk 0.23. slight split headwind (-0.27); park suppresses carry (-7%).""", blast="good"),
            row("Kody Clemens", "L", "N/A", 58, "", ["vs Fedde"], """0 HR, 1 near-HR, 90.7 mph EV. Fedde LHB split -0.27, HR risk 0.23. slight split headwind (-0.27); park suppresses carry (-7%)."""),
            row("Tristan Peters", "L", "N/A", 91, "🌕 💣", ["vs Ober"], """4 HR, 4 near-HR, 93.0 mph EV. Ober LHB split +0.34, HR risk 0.94. park suppresses carry (-7%).""", blast="high"),
        ],
    },
    {
        "title": "HOU @ NYM - Bennett Sousa (L, HOU) vs Nolan McLean (R, NYM)",
        "description": "Tail key data: Park boost -6% (stadium -2%, weather -5%). Sousa (HR risk -0.09, vs LHB -0.27, vs RHB +0.26). McLean (HR risk -0.09, vs LHB +0.02, vs RHB -0.57).",
        "rows": [
            row("Francisco Alvarez", "R", "N/A", 63, "", ["vs Sousa"], """1 HR, 1 near-HR, 94.7 mph EV. Sousa RHB split +0.26, HR risk -0.09. pitcher risk below avg (-0.09); park/weather net drag (-6%).""", blast="good"),
            row("Bo Bichette", "R", "N/A", 58, "", ["vs Sousa"], """0 HR, 94.4 mph EV. Sousa RHB split +0.26, HR risk -0.09. pitcher risk below avg (-0.09); park/weather net drag (-6%).""", blast="good"),
            row("Yordan Alvarez", "L", "N/A", 58, "", ["vs McLean"], """0 HR, 96.7 mph EV. McLean LHB split +0.02, HR risk -0.09. pitcher risk below avg (-0.09); park/weather net drag (-6%).""", blast="good"),
            row("Nick Allen", "R", "N/A", 58, "", ["vs McLean"], """1 HR, 1 near-HR, 94.0 mph EV. McLean RHB split -0.57, HR risk -0.09. tough split lane (-0.57); pitcher risk below avg (-0.09).""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 58, "", ["vs McLean"], """0 HR, 1 near-HR, 96.2 mph EV. McLean RHB split -0.57, HR risk -0.09. tough split lane (-0.57); pitcher risk below avg (-0.09).""", blast="good"),
        ],
    },
    {
        "title": "KC @ CLE - Daniel Lynch IV (L, KC) vs Foster Griffin (L, CLE)",
        "description": "Tail key data: Park boost -4% (stadium -4%, weather +0%). Lynch IV (HR risk 0.11, vs LHB -0.22, vs RHB +0.10). Griffin (HR risk 0.84, vs LHB +1.17, vs RHB +0.30).",
        "rows": [
            row("Jo Adell", "R", "N/A", 58, "⭐", ["vs Lynch IV"], """Worst Pickz Favorite. 0 HR, 89.9 mph EV. Lynch IV RHB split +0.10, HR risk 0.11. limited recent HR events."""),
            row("Patrick Bailey", "S", "N/A", 58, "", ["vs Lynch IV"], """0 HR, 84.3 mph EV. Lynch IV SHB→RHB split +0.10, HR risk 0.11. limited recent HR events; lighter EV form (84.3 mph)."""),
            row("Carter Jensen", "L", "N/A", 83, "⭐", ["vs Griffin"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.3 mph EV. Griffin LHB split +1.17, HR risk 0.84.""", blast="good"),
            row("Jac Caglianone", "L", "N/A", 79, "💎", ["vs Griffin"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.7 mph EV. Griffin LHB split +1.17, HR risk 0.84. limited recent HR events.""", blast="good"),
            row("Bobby Witt Jr.", "R", "N/A", 69, "⭐", ["vs Griffin"], """Worst Pickz Favorite. 0 HR, 94.2 mph EV. Griffin RHB split +0.30, HR risk 0.84. limited recent HR events.""", blast="good"),
            row("Salvador Perez", "R", "N/A", 69, "", ["vs Griffin"], """1 HR, 1 near-HR, 88.3 mph EV. Griffin RHB split +0.30, HR risk 0.84.""", blast="good"),
        ],
    },
    {
        "title": "LAD @ DET - Blake Snell (L, LAD) vs Keider Montero (R, DET)",
        "description": "Tail key data: Park boost -25% (stadium -11%, weather -13%). Snell (HR risk -2.09, vs LHB -1.44, vs RHB -1.82). Montero (HR risk 0.13, vs LHB +0.16, vs RHB +0.02).",
        "rows": [
            row("Eduardo Valencia", "R", "+630", 58, "🌕 💣 💎", ["vs Snell"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.3 mph EV. Snell RHB split -1.82, HR risk -2.09. tough split lane (-1.82); pitcher suppresses HR (-2.09).""", blast="high"),
            row("Kevin McGonigle", "L", "+900", 58, "", ["vs Snell"], """0 HR, 1 near-HR, 92.4 mph EV. Snell LHB split -1.44, HR risk -2.09. tough split lane (-1.44); pitcher suppresses HR (-2.09).""", blast="good"),
            row("Max Muncy", "L", "+400", 62, "💎", ["vs Montero"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.0 mph EV. Montero LHB split +0.16, HR risk 0.13. park/weather net drag (-25%).""", blast="good"),
            row("Hunter Feduccia", "L", "+800", 58, "", ["vs Montero"], """1 HR, 1 near-HR, 85.5 mph EV. Montero LHB split +0.16, HR risk 0.13. park/weather net drag (-25%); lighter EV form (85.5 mph).""", blast="good"),
            row("Shohei Ohtani", "L", "+280", 58, "", ["vs Montero"], """0 HR, 98.2 mph EV. Montero LHB split +0.16, HR risk 0.13. park/weather net drag (-25%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ WSH - Sandy Alcantara (R, MIA) vs Cade Cavalli (R, WSH)",
        "description": "Tail key data: Park boost +4% (stadium +3%, weather +1%). Alcantara (HR risk -0.62, vs LHB -0.27, vs RHB -0.92). Cavalli (HR risk 0.71, vs LHB +0.20, vs RHB +1.06).",
        "rows": [
            row("Daylen Lile", "L", "+520", 59, "🌕 💣", ["vs Alcantara"], """2 HR, 2 near-HR, 88.0 mph EV. Alcantara LHB split -0.27, HR risk -0.62. slight split headwind (-0.27); pitcher suppresses HR (-0.62).""", blast="high"),
            row("Brady House", "R", "+680", 58, "", ["vs Alcantara"], """1 HR, 2 near-HR, 97.2 mph EV. Alcantara RHB split -0.92, HR risk -0.62. tough split lane (-0.92); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Andres Chaparro", "R", "N/A", 58, "", ["vs Alcantara"], """1 HR, 2 near-HR, 94.6 mph EV. Alcantara RHB split -0.92, HR risk -0.62. tough split lane (-0.92); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Griffin Conine", "L", "+500", 89, "🌕 💣", ["vs Cavalli"], """2 HR, 3 near-HR, 94.9 mph EV. Cavalli LHB split +0.20, HR risk 0.71.""", blast="high"),
            row("Owen Caissie", "L", "+630", 72, "", ["vs Cavalli"], """1 HR, 1 near-HR, 91.3 mph EV. Cavalli LHB split +0.20, HR risk 0.71.""", blast="good"),
            row("Kyle Stowers", "L", "+350", 71, "💎", ["vs Cavalli"], """Worst Pickz Hidden Gem. 0 HR, 95.8 mph EV. Cavalli LHB split +0.20, HR risk 0.71. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "PHI @ LAA - Cristopher Sanchez (L, PHI) vs Ryan Johnson 🧤 (R, LAA)",
        "description": "Tail key data: Park boost -1% (stadium -9%, weather +7%). Sanchez (HR risk -0.60, vs LHB -0.94, vs RHB -0.29). Johnson 🧤 (HR risk 1.38, vs LHB +0.97, vs RHB +0.97).",
        "rows": [
            row("Moises Ballesteros", "L", "+1060", 58, "", ["vs Sanchez"], """0 HR, 1 near-HR, 93.9 mph EV. Sanchez LHB split -0.94, HR risk -0.60. tough split lane (-0.94); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Jose Siri", "R", "+680", 58, "", ["vs Sanchez"], """0 HR, 92.2 mph EV. Sanchez RHB split -0.29, HR risk -0.60. slight split headwind (-0.29); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Kyle Schwarber", "L", "+176", 93, "🌕 💣", ["vs Johnson"], """2 HR, 2 near-HR, 95.4 mph EV. Johnson LHB split +0.97, HR risk 1.38. park suppresses carry (-9%).""", blast="high"),
            row("Bryce Harper", "L", "+340", 82, "", ["vs Johnson"], """0 HR, 1 near-HR, 92.2 mph EV. Johnson LHB split +0.97, HR risk 1.38. park suppresses carry (-9%); limited recent HR events.""", blast="good"),
            row("JT Realmuto", "R", "+750", 83, "", ["vs Johnson"], """0 HR, 95.2 mph EV. Johnson RHB split +0.97, HR risk 1.38. park suppresses carry (-9%); limited recent HR events.""", blast="good"),
            row("Alec Bohm", "R", "+680", 75, "", ["vs Johnson"], """0 HR, 91.1 mph EV. Johnson RHB split +0.97, HR risk 1.38. park suppresses carry (-9%); limited recent HR events."""),
        ],
    },
    {
        "title": "PIT @ STL - Lake Bachar (R, PIT) vs Kyle Leahy (R, STL)",
        "description": "Tail key data: Park boost -12% (stadium -9%, weather -2%). Bachar (season BAA .201). Leahy (HR risk -0.49, vs LHB -0.23, vs RHB -0.58).",
        "rows": [
            row("Jimmy Crooks", "L", "N/A", 58, "💎", ["vs Bachar"], """Worst Pickz Hidden Gem. 0 HR, 95.8 mph EV. limited split/risk sample; park/weather net drag (-12%).""", blast="good"),
            row("JJ Wetherholt", "L", "N/A", 60, "", ["vs Bachar"], """0 HR, 1 near-HR, 99.2 mph EV. limited split/risk sample; park/weather net drag (-12%).""", blast="good"),
            row("Bryan Reynolds", "S", "+396", 58, "", ["vs Leahy"], """0 HR, 1 near-HR, 94.6 mph EV. Leahy SHB→LHB split -0.23, HR risk -0.49. slight split headwind (-0.23); pitcher suppresses HR (-0.49).""", blast="good"),
            row("Oneil Cruz", "L", "+266", 60, "🌕 💣", ["vs Leahy"], """2 HR, 2 near-HR, 91.7 mph EV. Leahy LHB split -0.23, HR risk -0.49. slight split headwind (-0.23); pitcher suppresses HR (-0.49).""", blast="high"),
            row("Esmerlyn Valdez", "R", "+308", 58, "", ["vs Leahy"], """0 HR, 86.5 mph EV. Leahy RHB split -0.58, HR risk -0.49. tough split lane (-0.58); pitcher suppresses HR (-0.49)."""),
        ],
    },
    {
        "title": "SD @ TB - Walker Buehler (R, SD) vs Nick Martinez (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Buehler (HR risk -0.14, vs LHB -0.32, vs RHB +0.23). Martinez (HR risk 0.28, vs LHB +0.17, vs RHB +0.11).",
        "rows": [
            row("Jonathan Aranda", "L", "N/A", 58, "💎", ["vs Buehler"], """Worst Pickz Hidden Gem. 0 HR, 93.4 mph EV. Buehler LHB split -0.32, HR risk -0.14. slight split headwind (-0.32); pitcher risk below avg (-0.14).""", blast="good"),
            row("Junior Caminero", "R", "N/A", 59, "⭐", ["vs Buehler"], """Worst Pickz Favorite. 0 HR, 95.8 mph EV. Buehler RHB split +0.23, HR risk -0.14. pitcher risk below avg (-0.14); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "SEA @ TOR - Kade Anderson (L, SEA) vs Jose Soriano (R, TOR)",
        "description": "Tail key data: Park boost +13% (stadium +6%, weather +7%). Anderson (HR risk 0.00, vs LHB +0.00, vs RHB +1.26). Soriano (HR risk -0.37, vs LHB -0.29, vs RHB -0.18).",
        "rows": [
            row("George Springer", "R", "+314", 76, "", ["vs Anderson"], """1 HR, 1 near-HR, 94.4 mph EV. Anderson RHB split +1.26, HR risk 0.00.""", blast="good"),
            row("Alejandro Kirk", "R", "+400", 71, "", ["vs Anderson"], """0 HR, 94.4 mph EV. Anderson RHB split +1.26, HR risk 0.00. limited recent HR events.""", blast="good"),
            row("Brandon Valenzuela", "S", "N/A", 71, "", ["vs Anderson"], """0 HR, 1 near-HR, 93.4 mph EV. Anderson SHB→RHB split +1.26, HR risk 0.00. limited recent HR events.""", blast="good"),
            row("Dominic Canzone", "L", "+396", 62, "", ["vs Soriano"], """1 HR, 1 near-HR, 96.6 mph EV. Soriano LHB split -0.29, HR risk -0.37. slight split headwind (-0.29); pitcher risk below avg (-0.37).""", blast="good"),
            row("Cal Raleigh", "S", "+292", 72, "🌕 💣", ["vs Soriano"], """2 HR, 2 near-HR, 95.1 mph EV. Soriano SHB→RHB split -0.18, HR risk -0.37. slight split headwind (-0.18); pitcher risk below avg (-0.37).""", blast="high"),
            row("Josh Naylor", "L", "+680", 58, "", ["vs Soriano"], """0 HR, 92.2 mph EV. Soriano LHB split -0.29, HR risk -0.37. slight split headwind (-0.29); pitcher risk below avg (-0.37).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ MIL - Cal Quantrill (R, TEX) vs Shane Drohan (L, MIL)",
        "description": "Tail key data: Park boost +3% (stadium -2%, weather +5%). Quantrill (HR risk -0.45, vs LHB +0.02, vs RHB -0.94). Drohan (HR risk 0.03, vs LHB -0.49, vs RHB +0.61).",
        "rows": [
            row("Jackson Chourio", "R", "+420", 58, "💎", ["vs Quantrill"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.9 mph EV. Quantrill RHB split -0.94, HR risk -0.45. tough split lane (-0.94); pitcher suppresses HR (-0.45).""", blast="good"),
            row("Jake Bauers", "L", "+330", 58, "💎", ["vs Quantrill"], """Worst Pickz Hidden Gem. 0 HR, 94.4 mph EV. Quantrill LHB split +0.02, HR risk -0.45. pitcher suppresses HR (-0.45); limited recent HR events.""", blast="good"),
            row("William Contreras", "R", "+520", 58, "", ["vs Quantrill"], """0 HR, 1 near-HR, 93.2 mph EV. Quantrill RHB split -0.94, HR risk -0.45. tough split lane (-0.94); pitcher suppresses HR (-0.45).""", blast="good"),
            row("Jake Burger", "R", "+430", 80, "⭐ 🌕 💣", ["vs Drohan"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.0 mph EV. Drohan RHB split +0.61, HR risk 0.03.""", blast="high"),
            row("Elias Diaz", "R", "+750", 62, "", ["vs Drohan"], """0 HR, 92.9 mph EV. Drohan RHB split +0.61, HR risk 0.03. limited recent HR events.""", blast="good"),
            row("Wyatt Langford", "R", "+480", 66, "🚀", ["vs Drohan"], """0 HR, 1 near-HR, 100.5 mph EV. Drohan RHB split +0.61, HR risk 0.03. limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-29")

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

    out = ROOT / '_games-0829.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
