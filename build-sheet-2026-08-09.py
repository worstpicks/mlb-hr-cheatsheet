#!/usr/bin/env python3
"""Generate games[] block for 2026-08-09 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Andrew Vaughn (R)",
    "Ben Rice (L)",
    "Brandon Nimmo (L)",
    "Bryce Harper (L)",
    "Cal Raleigh (S)",
    "Corey Seager (L)",
    "Daylen Lile (L)",
    "Dominic Canzone (L)",
    "Drake Baldwin (L)",
    "Elly De La Cruz (S)",
    "Esmerlyn Valdez (R)",
    "Gunnar Henderson (L)",
    "Jimmy Crooks (L)",
    "Josh Bell (S)",
    "Kyle Schwarber (L)",
    "Kyle Stowers (L)",
    "Matt Olson (L)",
    "Moisés Ballesteros (L)",
    "Salvador Perez (R)",
    "Shohei Ohtani (L)",
    "Taylor Trammell (L)",
    "Wilyer Abreu (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Austin Wells (L)",
    "Bobby Witt Jr. (R)",
    "Brett Baty (L)",
    "Bryan Reynolds (S)",
    "Bryson Stott (L)",
    "Colton Cowser (L)",
    "Jake Burger (R)",
    "Jazz Chisholm Jr. (L)",
    "Kazuma Okamoto (R)",
    "Lawrence Butler (L)",
    "Mike Yastrzemski (L)",
    "Nathaniel Lowe (L)",
    "Patrick Bailey (S)",
    "Royce Lewis (R)",
    "Ryan Kreidler (R)",
    "Ty France (R)",
    "Tyler Soderstrom (L)",
    "Tyler Stephenson (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Andrew Vaughn (R)": "MIL",
    "Andy Pages (R)": "LAD",
    "Austin Riley (R)": "ATL",
    "Austin Wells (L)": "NYY",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Nimmo (L)": "TEX",
    "Brett Baty (L)": "NYM",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "CJ Abrams (L)": "WSH",
    "Cal Raleigh (S)": "SEA",
    "Carter Jensen (L)": "KC",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Colt Emerson (L)": "SEA",
    "Colt Keith (L)": "DET",
    "Colton Cowser (L)": "BAL",
    "Corey Seager (L)": "TEX",
    "Daylen Lile (L)": "WSH",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Dylan Beavers (L)": "BAL",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Everson Pereira (R)": "STL",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Gabriel Moreno (R)": "ARI",
    "Griffin Conine (L)": "MIA",
    "Gunnar Henderson (L)": "BAL",
    "Hao-Yu Lee (R)": "DET",
    "Henry Davis (R)": "PIT",
    "Ivan Herrera (R)": "STL",
    "J.T. Realmuto (R)": "PHI",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Holliday (L)": "BAL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jake McCarthy (L)": "COL",
    "Jarren Duran (L)": "BOS",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jimmy Crooks (L)": "STL",
    "John Rave (L)": "KC",
    "Jose Tena (L)": "WSH",
    "Josh Bell (S)": "MIN",
    "Jung Hoo Lee (L)": "SF",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Kyle Tucker (L)": "LAD",
    "Lawrence Butler (L)": "ATH",
    "Leody Taveras (S)": "BAL",
    "Luis Garcia Jr. (L)": "NYY",
    "Luis Lara (S)": "MIL",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Max Muncy (L)": "LAD",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Mike Yastrzemski (L)": "ATL",
    "Moisés Ballesteros (L)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Nathaniel Lowe (L)": "CLE",
    "Owen Caissie (L)": "MIA",
    "Patrick Bailey (S)": "CLE",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan Kreidler (R)": "MIN",
    "Ryan Waldschmidt (R)": "ARI",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Torkelson (R)": "DET",
    "Taylor Trammell (L)": "HOU",
    "Travis Bazzana (L)": "CLE",
    "Ty France (R)": "SD",
    "Tyler Soderstrom (L)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "Victor Mesa Jr. (L)": "TB",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("CIN @ WSH", "Lord"),
    ("LAA @ MIA", "Rodriguez"),
    ("LAD @ ARI", "Wrobleski"),
    ("NYM @ PIT", "Manaea"),
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
        "title": "ATH @ BOS - J.T. Ginn (R, ATH) vs Brayan Bello (R, BOS)",
        "description": "Tail key data: Park boost +15% (stadium -8%, weather +23%). Ginn (HR risk -0.23, vs LHB +0.31, vs RHB -0.99). Bello (HR risk 0.00, vs LHB +0.00, vs RHB +0.00).",
        "rows": [
            row("Wilyer Abreu", "L", "+224", 78, "⭐ 🌕 💣", ["vs Ginn"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.7 mph EV. Ginn LHB split +0.31, HR risk -0.23. pitcher risk below avg (-0.23); park suppresses carry (-8%).""", blast="high"),
            row("Jarren Duran", "L", "+345", 79, "🌕 💣", ["vs Ginn"], """3 HR, 3 near-HR, 88.7 mph EV. Ginn LHB split +0.31, HR risk -0.23. pitcher risk below avg (-0.23); park suppresses carry (-8%).""", blast="high"),
            row("Willson Contreras", "R", "+224", 58, "", ["vs Ginn"], """0 HR, 97.3 mph EV. Ginn RHB split -0.99, HR risk -0.23. tough split lane (-0.99); pitcher risk below avg (-0.23).""", blast="good"),
            row("Lawrence Butler", "L", "+434", 67, "💎", ["vs Bello"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.5 mph EV. Bello LHB split +0.00, HR risk 0.00. park suppresses carry (-8%).""", blast="good"),
            row("Tyler Soderstrom", "L", "+296", 64, "💎", ["vs Bello"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 97.5 mph EV. Bello LHB split +0.00, HR risk 0.00. park suppresses carry (-8%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "ATL @ NYY - Grant Holmes (R, ATL) vs Cam Schlittler (R, NYY)",
        "description": "Tail key data: Park boost +18% (stadium +5%, weather +13%). Holmes (HR risk 0.30, vs LHB +0.63, vs RHB -0.44). Schlittler (HR risk -0.42, vs LHB -0.15, vs RHB -0.22).",
        "rows": [
            row("Jazz Chisholm Jr.", "L", "+392", 92, "🌕 💣 💎", ["vs Holmes"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 98.8 mph EV. Holmes LHB split +0.63, HR risk 0.30.""", blast="high"),
            row("Ben Rice", "L", "+290", 78, "🚀 ⭐", ["vs Holmes"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 100.3 mph EV. Holmes LHB split +0.63, HR risk 0.30.""", blast="good"),
            row("Austin Wells", "L", "+596", 76, "💎", ["vs Holmes"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.1 mph EV. Holmes LHB split +0.63, HR risk 0.30.""", blast="good"),
            row("Luis Garcia Jr.", "L", "+362", 74, "", ["vs Holmes"], """1 HR, 1 near-HR, 92.8 mph EV. Holmes LHB split +0.63, HR risk 0.30.""", blast="good"),
            row("Drake Baldwin", "L", "+385", 62, "🚀 ⭐", ["vs Schlittler"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 100.7 mph EV. Schlittler LHB split -0.15, HR risk -0.42. slight split headwind (-0.15); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Mike Yastrzemski", "L", "+562", 76, "🌕 💣 💎", ["vs Schlittler"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 93.5 mph EV. Schlittler LHB split -0.15, HR risk -0.42. slight split headwind (-0.15); pitcher suppresses HR (-0.42).""", blast="high"),
            row("Matt Olson", "L", "+269", 67, "⭐", ["vs Schlittler"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 92.7 mph EV. Schlittler LHB split -0.15, HR risk -0.42. slight split headwind (-0.15); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Austin Riley", "R", "+517", 58, "", ["vs Schlittler"], """0 HR, 94.1 mph EV. Schlittler RHB split -0.22, HR risk -0.42. slight split headwind (-0.22); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+407", 58, "", ["vs Schlittler"], """0 HR, 1 near-HR, 91.7 mph EV. Schlittler RHB split -0.22, HR risk -0.42. slight split headwind (-0.22); pitcher suppresses HR (-0.42)."""),
        ],
    },
    {
        "title": "BAL @ TEX - Cade Povich (L, BAL) vs Kumar Rocker (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -11%, weather -1%). Povich (HR risk 0.43, vs LHB +1.31, vs RHB -0.31). Rocker (HR risk 0.34, vs LHB +0.67, vs RHB -0.35).",
        "rows": [
            row("Corey Seager", "L", "N/A", 88, "⭐ 🌕 💣", ["vs Povich"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.2 mph EV. Povich LHB split +1.31, HR risk 0.43. park/weather net drag (-11%).""", blast="high"),
            row("Brandon Nimmo", "L", "N/A", 77, "⭐", ["vs Povich"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.3 mph EV. Povich LHB split +1.31, HR risk 0.43. park/weather net drag (-11%).""", blast="good"),
            row("Jake Burger", "R", "N/A", 72, "💎", ["vs Povich"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 96.4 mph EV. Povich RHB split -0.31, HR risk 0.43. slight split headwind (-0.31); park/weather net drag (-11%).""", blast="good"),
            row("Jackson Holliday", "L", "+415", 64, "", ["vs Rocker"], """1 HR, 1 near-HR, 90.2 mph EV. Rocker LHB split +0.67, HR risk 0.34. park/weather net drag (-11%).""", blast="good"),
            row("Dylan Beavers", "L", "+357", 65, "", ["vs Rocker"], """0 HR, 1 near-HR, 94.9 mph EV. Rocker LHB split +0.67, HR risk 0.34. park/weather net drag (-11%); limited recent HR events.""", blast="good"),
            row("Colton Cowser", "L", "+403", 61, "💎", ["vs Rocker"], """Worst Pickz Hidden Gem. 0 HR, 92.4 mph EV. Rocker LHB split +0.67, HR risk 0.34. park/weather net drag (-11%); limited recent HR events.""", blast="good"),
            row("Gunnar Henderson", "L", "+234", 58, "⭐", ["vs Rocker"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 91.9 mph EV. Rocker LHB split +0.67, HR risk 0.34. park/weather net drag (-11%); limited recent HR events."""),
            row("Leody Taveras", "S", "+457", 62, "", ["vs Rocker"], """1 HR, 1 near-HR, 88.0 mph EV. Rocker SHB→LHB split +0.67, HR risk 0.34. park/weather net drag (-11%).""", blast="good"),
            row("Christian Encarnacion-Strand", "R", "+252", 58, "", ["vs Rocker"], """0 HR, 90.2 mph EV. Rocker RHB split -0.35, HR risk 0.34. slight split headwind (-0.35); park/weather net drag (-11%)."""),
        ],
    },
    {
        "title": "CHC @ KC - Matthew Boyd (L, CHC) vs Randy Dobnak (R, KC)",
        "description": "Tail key data: Park boost +34% (stadium +11%, weather +23%). Boyd (HR risk -0.30, vs LHB -0.45, vs RHB -0.09). Dobnak (HR risk -1.36, vs LHB -0.97, vs RHB -0.20).",
        "rows": [
            row("Salvador Perez", "R", "+381", 68, "⭐", ["vs Boyd"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.2 mph EV. Boyd RHB split -0.09, HR risk -0.30. slight split headwind (-0.09); pitcher risk below avg (-0.30).""", blast="good"),
            row("John Rave", "L", "+564", 63, "🚀", ["vs Boyd"], """0 HR, 1 near-HR, 102.8 mph EV. Boyd LHB split -0.45, HR risk -0.30. tough split lane (-0.45); pitcher risk below avg (-0.30).""", blast="good"),
            row("Bobby Witt Jr.", "R", "+385", 66, "💎", ["vs Boyd"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.4 mph EV. Boyd RHB split -0.09, HR risk -0.30. slight split headwind (-0.09); pitcher risk below avg (-0.30).""", blast="good"),
            row("Jac Caglianone", "L", "+528", 76, "🌕 💣", ["vs Boyd"], """2 HR, 2 near-HR, 96.4 mph EV. Boyd LHB split -0.45, HR risk -0.30. tough split lane (-0.45); pitcher risk below avg (-0.30).""", blast="high"),
            row("Carter Jensen", "L", "+517", 66, "", ["vs Boyd"], """1 HR, 1 near-HR, 94.8 mph EV. Boyd LHB split -0.45, HR risk -0.30. tough split lane (-0.45); pitcher risk below avg (-0.30).""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+331", 58, "", ["vs Dobnak"], """1 HR, 1 near-HR, 93.0 mph EV. Dobnak LHB split -0.97, HR risk -1.36. tough split lane (-0.97); pitcher suppresses HR (-1.36).""", blast="good"),
        ],
    },
    {
        "title": "CIN @ WSH - Brady Singer (R, CIN) vs Brad Lord 🧤 (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Singer (HR risk -0.67, vs LHB -0.17, vs RHB -0.74). Lord 🧤 (HR risk 1.44, vs LHB +2.05, vs RHB -1.22).",
        "rows": [
            row("Daylen Lile", "L", "+303", 63, "⭐ 🌕 💣", ["vs Singer"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.6 mph EV. Singer LHB split -0.17, HR risk -0.67. slight split headwind (-0.17); pitcher suppresses HR (-0.67).""", blast="high"),
            row("CJ Abrams", "L", "+231", 58, "", ["vs Singer"], """1 HR, 1 near-HR, 89.6 mph EV. Singer LHB split -0.17, HR risk -0.67. slight split headwind (-0.17); pitcher suppresses HR (-0.67).""", blast="good"),
            row("Jose Tena", "L", "+466", 67, "🌕 💣", ["vs Singer"], """2 HR, 2 near-HR, 97.7 mph EV. Singer LHB split -0.17, HR risk -0.67. slight split headwind (-0.17); pitcher suppresses HR (-0.67).""", blast="high"),
            row("Elly De La Cruz", "S", "+258", 98, "⭐ 🌕 💣", ["vs Lord"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 93.5 mph EV. Lord SHB→LHB split +2.05, HR risk 1.44.""", blast="high"),
            row("Eugenio Suarez", "R", "+217", 91, "🌕 💣", ["vs Lord"], """2 HR, 3 near-HR, 96.3 mph EV. Lord RHB split -1.22, HR risk 1.44. tough split lane (-1.22).""", blast="high"),
            row("Sal Stewart", "R", "+244", 72, "", ["vs Lord"], """1 HR, 1 near-HR, 90.1 mph EV. Lord RHB split -1.22, HR risk 1.44. tough split lane (-1.22).""", blast="good"),
            row("Tyler Stephenson", "R", "+304", 76, "💎", ["vs Lord"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.4 mph EV. Lord RHB split -1.22, HR risk 1.44. tough split lane (-1.22).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ CWS - Joey Cantillo (L, CLE) vs Davis Martin (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Cantillo (HR risk 0.15, vs LHB -0.33, vs RHB +0.38). Martin (HR risk -0.14, vs LHB +0.38, vs RHB -0.56).",
        "rows": [
            row("Munetaka Murakami", "L", "+338", 59, "", ["vs Cantillo"], """1 HR, 2 near-HR, 90.0 mph EV. Cantillo LHB split -0.33, HR risk 0.15. slight split headwind (-0.33).""", blast="good"),
            row("Randal Grichuk", "R", "+492", 59, "", ["vs Cantillo"], """0 HR, 92.1 mph EV. Cantillo RHB split +0.38, HR risk 0.15. limited recent HR events.""", blast="good"),
            row("Miguel Vargas", "R", "+370", 60, "", ["vs Cantillo"], """0 HR, 92.5 mph EV. Cantillo RHB split +0.38, HR risk 0.15. limited recent HR events.""", blast="good"),
            row("Patrick Bailey", "S", "+850", 66, "💎", ["vs Martin"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.4 mph EV. Martin SHB→LHB split +0.38, HR risk -0.14. pitcher risk below avg (-0.14).""", blast="good"),
            row("Travis Bazzana", "L", "+590", 60, "", ["vs Martin"], """0 HR, 1 near-HR, 94.0 mph EV. Martin LHB split +0.38, HR risk -0.14. pitcher risk below avg (-0.14); limited recent HR events.""", blast="good"),
            row("Nathaniel Lowe", "L", "+562", 61, "💎", ["vs Martin"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 88.8 mph EV. Martin LHB split +0.38, HR risk -0.14. pitcher risk below avg (-0.14).""", blast="good"),
        ],
    },
    {
        "title": "COL @ STL - Michael Lorenzen (R, COL) vs Michael McGreevy (R, STL)",
        "description": "Tail key data: Park boost +5% (stadium -10%, weather +15%). Lorenzen (HR risk 0.77, vs LHB +0.68, vs RHB +0.17). McGreevy (HR risk 0.42, vs LHB +0.31, vs RHB +0.47).",
        "rows": [
            row("Jimmy Crooks", "L", "N/A", 80, "⭐", ["vs Lorenzen"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.5 mph EV. Lorenzen LHB split +0.68, HR risk 0.77. park suppresses carry (-10%).""", blast="good"),
            row("Ivan Herrera", "R", "N/A", 77, "", ["vs Lorenzen"], """1 HR, 1 near-HR, 99.9 mph EV. Lorenzen RHB split +0.17, HR risk 0.77. park suppresses carry (-10%).""", blast="good"),
            row("Alec Burleson", "L", "N/A", 80, "", ["vs Lorenzen"], """1 HR, 2 near-HR, 93.8 mph EV. Lorenzen LHB split +0.68, HR risk 0.77. park suppresses carry (-10%).""", blast="good"),
            row("Everson Pereira", "R", "N/A", 70, "", ["vs Lorenzen"], """1 HR, 2 near-HR, 87.4 mph EV. Lorenzen RHB split +0.17, HR risk 0.77. park suppresses carry (-10%); lighter EV form (87.4 mph).""", blast="good"),
            row("Willi Castro", "S", "N/A", 68, "", ["vs McGreevy"], """1 HR, 2 near-HR, 82.2 mph EV. McGreevy SHB→RHB split +0.47, HR risk 0.42. park suppresses carry (-10%); lighter EV form (82.2 mph).""", blast="good"),
            row("Mickey Moniak", "L", "N/A", 75, "🌕 💣", ["vs McGreevy"], """2 HR, 2 near-HR, 86.7 mph EV. McGreevy LHB split +0.31, HR risk 0.42. park suppresses carry (-10%); lighter EV form (86.7 mph).""", blast="high"),
            row("Jake McCarthy", "L", "N/A", 68, "", ["vs McGreevy"], """1 HR, 1 near-HR, 89.1 mph EV. McGreevy LHB split +0.31, HR risk 0.42. park suppresses carry (-10%).""", blast="good"),
        ],
    },
    {
        "title": "DET @ SF - Troy Melton (R, DET) vs Logan Webb (R, SF)",
        "description": "Tail key data: Park boost -11% (stadium -17%, weather +6%). Melton (HR risk -1.13, vs LHB -0.22, vs RHB -1.45). Webb (HR risk -1.46, vs LHB -0.84, vs RHB -0.95).",
        "rows": [
            row("Jung Hoo Lee", "L", "N/A", 58, "🌕 💣", ["vs Melton"], """2 HR, 2 near-HR, 91.2 mph EV. Melton LHB split -0.22, HR risk -1.13. slight split headwind (-0.22); pitcher suppresses HR (-1.13).""", blast="high"),
            row("Rafael Devers", "L", "N/A", 58, "", ["vs Melton"], """0 HR, 96.0 mph EV. Melton LHB split -0.22, HR risk -1.13. slight split headwind (-0.22); pitcher suppresses HR (-1.13).""", blast="good"),
            row("Hao-Yu Lee", "R", "N/A", 58, "🌕 💣", ["vs Webb"], """2 HR, 2 near-HR, 95.2 mph EV. Webb RHB split -0.95, HR risk -1.46. tough split lane (-0.95); pitcher suppresses HR (-1.46).""", blast="high"),
            row("Colt Keith", "L", "N/A", 58, "", ["vs Webb"], """0 HR, 2 near-HR, 91.6 mph EV. Webb LHB split -0.84, HR risk -1.46. tough split lane (-0.84); pitcher suppresses HR (-1.46).""", blast="good"),
            row("Spencer Torkelson", "R", "N/A", 58, "", ["vs Webb"], """0 HR, 92.4 mph EV. Webb RHB split -0.95, HR risk -1.46. tough split lane (-0.95); pitcher suppresses HR (-1.46).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ SD - Cristian Javier (R, HOU) vs Randy Vasquez (R, SD)",
        "description": "Tail key data: Park boost +0% (stadium -4%, weather +4%). Javier (HR risk -0.51, vs LHB -0.88, vs RHB +0.56). Vasquez (HR risk 0.00, vs LHB +0.00, vs RHB +0.00).",
        "rows": [
            row("Fernando Tatis Jr.", "R", "N/A", 60, "", ["vs Javier"], """0 HR, 1 near-HR, 95.8 mph EV. Javier RHB split +0.56, HR risk -0.51. pitcher suppresses HR (-0.51); limited recent HR events.""", blast="good"),
            row("Manny Machado", "R", "N/A", 58, "", ["vs Javier"], """1 HR, 2 near-HR, 88.3 mph EV. Javier RHB split +0.56, HR risk -0.51. pitcher suppresses HR (-0.51).""", blast="good"),
            row("Jackson Merrill", "L", "N/A", 58, "🌕 💣", ["vs Javier"], """2 HR, 2 near-HR, 88.7 mph EV. Javier LHB split -0.88, HR risk -0.51. tough split lane (-0.88); pitcher suppresses HR (-0.51).""", blast="high"),
            row("Ty France", "R", "N/A", 58, "💎", ["vs Javier"], """Worst Pickz Hidden Gem. 0 HR, 90.7 mph EV. Javier RHB split +0.56, HR risk -0.51. pitcher suppresses HR (-0.51); limited recent HR events."""),
            row("Taylor Trammell", "L", "N/A", 78, "⭐ 🌕 💣", ["vs Vasquez"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.9 mph EV. Vasquez LHB split +0.00, HR risk 0.00.""", blast="high"),
            row("Yordan Alvarez", "L", "N/A", 59, "⭐", ["vs Vasquez"], """Worst Pickz Favorite. 0 HR, 96.3 mph EV. Vasquez LHB split +0.00, HR risk 0.00. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "LAA @ MIA - Grayson Rodriguez 🧤 (R, LAA) vs Ryan Gusto (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -13%, weather +0%). Rodriguez 🧤 (HR risk 1.28, vs LHB -0.05, vs RHB +2.02). Gusto (HR risk -0.08, vs LHB +0.20, vs RHB -0.23).",
        "rows": [
            row("Owen Caissie", "L", "N/A", 91, "🌕 💣", ["vs Grayson Rodriguez"], """3 HR, 3 near-HR, 93.0 mph EV. Grayson Rodriguez LHB split -0.05, HR risk 1.28. slight split headwind (-0.05); park/weather net drag (-13%).""", blast="high"),
            row("Griffin Conine", "L", "N/A", 86, "🌕 💣", ["vs Grayson Rodriguez"], """2 HR, 2 near-HR, 95.5 mph EV. Grayson Rodriguez LHB split -0.05, HR risk 1.28. slight split headwind (-0.05); park/weather net drag (-13%).""", blast="high"),
            row("Kyle Stowers", "L", "N/A", 74, "⭐", ["vs Grayson Rodriguez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.6 mph EV. Grayson Rodriguez LHB split -0.05, HR risk 1.28. slight split headwind (-0.05); park/weather net drag (-13%).""", blast="good"),
            row("Mike Trout", "R", "N/A", 58, "", ["vs Gusto"], """1 HR, 1 near-HR, 89.5 mph EV. Gusto RHB split -0.23, HR risk -0.08. slight split headwind (-0.23); pitcher risk below avg (-0.08).""", blast="good"),
            row("Zach Neto", "R", "N/A", 58, "", ["vs Gusto"], """1 HR, 1 near-HR, 92.4 mph EV. Gusto RHB split -0.23, HR risk -0.08. slight split headwind (-0.23); pitcher risk below avg (-0.08).""", blast="good"),
            row("Moisés Ballesteros", "L", "N/A", 58, "⭐", ["vs Gusto"], """Worst Pickz Favorite. 0 HR, 82.6 mph EV. Gusto LHB split +0.20, HR risk -0.08. pitcher risk below avg (-0.08); park/weather net drag (-13%)."""),
        ],
    },
    {
        "title": "LAD @ ARI - Justin Wrobleski 🧤 (L, LAD) vs Eduardo Rodriguez (L, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Wrobleski 🧤 (HR risk 1.22, vs LHB +0.52, vs RHB +0.92). Rodriguez (HR risk -0.58, vs LHB -0.18, vs RHB -0.38).",
        "rows": [
            row("Ryan Waldschmidt", "R", "N/A", 83, "", ["vs Wrobleski"], """0 HR, 2 near-HR, 95.5 mph EV. Wrobleski RHB split +0.92, HR risk 1.22. park/weather net drag (-8%).""", blast="good"),
            row("Gabriel Moreno", "R", "+680", 85, "", ["vs Wrobleski"], """1 HR, 3 near-HR, 89.4 mph EV. Wrobleski RHB split +0.92, HR risk 1.22. park/weather net drag (-8%).""", blast="good"),
            row("Max Kepler", "L", "N/A", 77, "", ["vs Wrobleski"], """0 HR, 96.1 mph EV. Wrobleski LHB split +0.52, HR risk 1.22. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Andy Pages", "R", "+460", 58, "", ["vs Eduardo Rodriguez"], """1 HR, 1 near-HR, 92.7 mph EV. Eduardo Rodriguez RHB split -0.38, HR risk -0.58. slight split headwind (-0.38); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Shohei Ohtani", "L", "+290", 64, "⭐ 🌕 💣", ["vs Eduardo Rodriguez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.1 mph EV. Eduardo Rodriguez LHB split -0.18, HR risk -0.58. slight split headwind (-0.18); pitcher suppresses HR (-0.58).""", blast="high"),
            row("Kyle Tucker", "L", "+560", 58, "", ["vs Eduardo Rodriguez"], """1 HR, 2 near-HR, 94.1 mph EV. Eduardo Rodriguez LHB split -0.18, HR risk -0.58. slight split headwind (-0.18); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Max Muncy", "L", "N/A", 58, "", ["vs Eduardo Rodriguez"], """1 HR, 2 near-HR, 92.2 mph EV. Eduardo Rodriguez LHB split -0.18, HR risk -0.58. slight split headwind (-0.18); pitcher suppresses HR (-0.58).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ MIL - Connor Prielipp (L, MIN) vs Jacob Misiorowski (R, MIL)",
        "description": "Tail key data: Park boost +21% (stadium +9%, weather +12%). Prielipp (HR risk 0.00, vs LHB -0.68, vs RHB +0.41). Misiorowski (HR risk 0.08, vs LHB -0.66, vs RHB +1.20).",
        "rows": [
            row("Andrew Vaughn", "R", "N/A", 73, "⭐", ["vs Prielipp"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.9 mph EV. Prielipp RHB split +0.41, HR risk 0.00.""", blast="good"),
            row("Jackson Chourio", "R", "N/A", 59, "", ["vs Prielipp"], """0 HR, 1 near-HR, 90.3 mph EV. Prielipp RHB split +0.41, HR risk 0.00. limited recent HR events."""),
            row("Luis Lara", "S", "N/A", 68, "", ["vs Prielipp"], """0 HR, 97.7 mph EV. Prielipp SHB→RHB split +0.41, HR risk 0.00. limited recent HR events.""", blast="good"),
            row("Jake Bauers", "L", "N/A", 61, "", ["vs Prielipp"], """1 HR, 1 near-HR, 92.0 mph EV. Prielipp LHB split -0.68, HR risk 0.00. tough split lane (-0.68).""", blast="good"),
            row("Josh Bell", "S", "N/A", 78, "⭐", ["vs Misiorowski"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.1 mph EV. Misiorowski SHB→RHB split +1.20, HR risk 0.08.""", blast="good"),
            row("Royce Lewis", "R", "N/A", 73, "💎", ["vs Misiorowski"], """Worst Pickz Hidden Gem. 0 HR, 94.6 mph EV. Misiorowski RHB split +1.20, HR risk 0.08. limited recent HR events.""", blast="good"),
            row("Kody Clemens", "L", "N/A", 61, "", ["vs Misiorowski"], """0 HR, 1 near-HR, 96.5 mph EV. Misiorowski LHB split -0.66, HR risk 0.08. tough split lane (-0.66); limited recent HR events.""", blast="good"),
            row("Ryan Kreidler", "R", "N/A", 76, "💎", ["vs Misiorowski"], """Worst Pickz Hidden Gem. 0 HR, 3 near-HR, 90.4 mph EV. Misiorowski RHB split +1.20, HR risk 0.08.""", blast="good"),
        ],
    },
    {
        "title": "NYM @ PIT - Sean Manaea 🧤 (L, NYM) vs Jared Jones (R, PIT)",
        "description": "Tail key data: Park boost -14% (stadium -16%, weather +2%). Manaea 🧤 (HR risk 0.99, vs LHB +0.41, vs RHB +0.78). Jones (HR risk 0.35, vs LHB -0.39, vs RHB +1.17).",
        "rows": [
            row("Esmerlyn Valdez", "R", "+474", 90, "⭐ 🌕 💣", ["vs Manaea"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.8 mph EV. Manaea RHB split +0.78, HR risk 0.99. park/weather net drag (-14%).""", blast="high"),
            row("Henry Davis", "R", "N/A", 76, "", ["vs Manaea"], """0 HR, 97.2 mph EV. Manaea RHB split +0.78, HR risk 0.99. park/weather net drag (-14%); limited recent HR events.""", blast="good"),
            row("Bryan Reynolds", "S", "+534", 66, "💎", ["vs Manaea"], """Worst Pickz Hidden Gem. 0 HR, 90.2 mph EV. Manaea SHB→RHB split +0.78, HR risk 0.99. park/weather net drag (-14%); limited recent HR events."""),
            row("Brett Baty", "L", "+576", 70, "🌕 💣 💎", ["vs Jones"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 95.7 mph EV. Jones LHB split -0.39, HR risk 0.35. slight split headwind (-0.39); park/weather net drag (-14%).""", blast="high"),
            row("Francisco Alvarez", "R", "+593", 70, "", ["vs Jones"], """1 HR, 1 near-HR, 92.9 mph EV. Jones RHB split +1.17, HR risk 0.35. park/weather net drag (-14%).""", blast="good"),
        ],
    },
    {
        "title": "TB @ SEA - Ian Seymour (L, TB) vs Emerson Hancock (R, SEA)",
        "description": "Tail key data: Park boost +4% (stadium +1%, weather +3%). Seymour (HR risk 0.00, vs LHB +0.00, vs RHB +0.00). Hancock (HR risk -0.03, vs LHB +0.28, vs RHB -0.36).",
        "rows": [
            row("Dominic Canzone", "L", "N/A", 75, "🚀 ⭐ 🌕 💣", ["vs Seymour"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 101.3 mph EV. Seymour LHB split +0.00, HR risk 0.00.""", blast="high"),
            row("Cal Raleigh", "S", "N/A", 66, "⭐", ["vs Seymour"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.3 mph EV. Seymour SHB→LHB split +0.00, HR risk 0.00.""", blast="good"),
            row("Colt Emerson", "L", "N/A", 60, "", ["vs Seymour"], """1 HR, 1 near-HR, 90.5 mph EV. Seymour LHB split +0.00, HR risk 0.00.""", blast="good"),
            row("Junior Caminero", "R", "N/A", 76, "🌕 💣", ["vs Hancock"], """2 HR, 3 near-HR, 95.9 mph EV. Hancock RHB split -0.36, HR risk -0.03. slight split headwind (-0.36); pitcher risk below avg (-0.03).""", blast="high"),
            row("Victor Mesa Jr.", "L", "N/A", 61, "", ["vs Hancock"], """0 HR, 3 near-HR, 87.9 mph EV. Hancock LHB split +0.28, HR risk -0.03. pitcher risk below avg (-0.03); lighter EV form (87.9 mph).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ PHI - Shane Bieber (R, TOR) vs Jesus Luzardo (L, PHI)",
        "description": "Tail key data: Park boost +40% (stadium +16%, weather +24%). Bieber (HR risk -0.07, vs LHB -0.26, vs RHB +0.47). Luzardo (HR risk -0.82, vs LHB -1.52, vs RHB -0.04).",
        "rows": [
            row("Bryce Harper", "L", "N/A", 72, "⭐", ["vs Bieber"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.6 mph EV. Bieber LHB split -0.26, HR risk -0.07. slight split headwind (-0.26); pitcher risk below avg (-0.07).""", blast="good"),
            row("J.T. Realmuto", "R", "N/A", 76, "", ["vs Bieber"], """1 HR, 1 near-HR, 93.9 mph EV. Bieber RHB split +0.47, HR risk -0.07. pitcher risk below avg (-0.07).""", blast="good"),
            row("Bryson Stott", "L", "N/A", 66, "💎", ["vs Bieber"], """Worst Pickz Hidden Gem. 0 HR, 98.0 mph EV. Bieber LHB split -0.26, HR risk -0.07. slight split headwind (-0.26); pitcher risk below avg (-0.07).""", blast="good"),
            row("Kyle Schwarber", "L", "N/A", 65, "⭐", ["vs Bieber"], """Worst Pickz Favorite. 0 HR, 94.5 mph EV. Bieber LHB split -0.26, HR risk -0.07. slight split headwind (-0.26); pitcher risk below avg (-0.07).""", blast="good"),
            row("Kazuma Okamoto", "R", "N/A", 68, "💎", ["vs Luzardo"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 97.6 mph EV. Luzardo RHB split -0.04, HR risk -0.82. slight split headwind (-0.04); pitcher suppresses HR (-0.82).""", blast="good"),
            row("Vladimir Guerrero Jr.", "R", "N/A", 59, "", ["vs Luzardo"], """0 HR, 93.4 mph EV. Luzardo RHB split -0.04, HR risk -0.82. slight split headwind (-0.04); pitcher suppresses HR (-0.82).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-09")

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

    out = ROOT / '_games-0809.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
