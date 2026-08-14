#!/usr/bin/env python3
"""Generate games[] block for 2026-08-14 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Abimelec Ortiz (L)",
    "Coby Mayo (R)",
    "Daylen Lile (L)",
    "Griffin Conine (L)",
    "Hunter Goodman (R)",
    "Jac Caglianone (L)",
    "Jackson Merrill (L)",
    "Lawrence Butler (L)",
    "Luis Robert (R)",
    "Mike Trout (R)",
    "Munetaka Murakami (L)",
    "Pete Alonso (R)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Angel Genao (S)",
    "Bryan Reynolds (S)",
    "Daulton Varsho (L)",
    "Dominic Canzone (L)",
    "Drake Baldwin (L)",
    "Francisco Alvarez (R)",
    "Jake Bauers (L)",
    "Jonathan Aranda (L)",
    "Josh Naylor (L)",
    "Shohei Ohtani (L)",
    "Teoscar Hernandez (R)",
    "Tyler Soderstrom (L)",
    "Tyler Stephenson (R)",
    "Victor Mesa Jr. (L)",
    "William Contreras (R)",
}

PLAYER_TEAMS = {
    "A.J. Ewing (L)": "NYM",
    "Abimelec Ortiz (L)": "WSH",
    "Andy Pages (R)": "LAD",
    "Angel Genao (S)": "CLE",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brice Turang (L)": "MIL",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Cam Smith (R)": "HOU",
    "Carson Benge (L)": "NYM",
    "Chase DeLauter (L)": "CLE",
    "Coby Mayo (R)": "BAL",
    "Daulton Varsho (L)": "HOU",
    "Daylen Lile (L)": "WSH",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Drew Romo (S)": "CWS",
    "Eduardo Valencia (R)": "DET",
    "Elias Diaz (R)": "TEX",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "George Springer (R)": "TOR",
    "Gleyber Torres (R)": "DET",
    "Griffin Conine (L)": "MIA",
    "Henry Bolte (R)": "ATH",
    "Hunter Goodman (R)": "COL",
    "Isaac Collins (S)": "KC",
    "Jac Caglianone (L)": "KC",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jarren Duran (L)": "BOS",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jesus Sanchez (L)": "TOR",
    "Joe Mack (L)": "MIA",
    "Joey Ortiz (R)": "MIL",
    "Jonathan Aranda (L)": "TB",
    "Jose Tena (L)": "WSH",
    "Josh Naylor (L)": "SEA",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kazuma Okamoto (R)": "TOR",
    "Lawrence Butler (L)": "ATH",
    "Luis Garcia Jr. (L)": "NYY",
    "Luis Robert (R)": "NYM",
    "Manny Machado (R)": "SD",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Michael Harris II (L)": "ATL",
    "Mike Trout (R)": "LAA",
    "Moises Ballesteros (L)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Nathaniel Lowe (L)": "CLE",
    "Nelson Velazquez (R)": "HOU",
    "Owen Caissie (L)": "MIA",
    "Patrick Bailey (S)": "CLE",
    "Pete Alonso (R)": "BAL",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Ronny Simon (S)": "PIT",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Taylor Trammell (L)": "HOU",
    "Teoscar Hernandez (R)": "LAD",
    "Tyler Soderstrom (L)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "Victor Bericoto (R)": "SF",
    "Victor Mesa Jr. (L)": "TB",
    "Willi Castro (S)": "COL",
    "William Contreras (R)": "MIL",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Xander Bogaerts (R)": "SD",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zac Veen (L)": "COL",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("KC @ LAA", "Rodriguez"),
    ("SD @ CLE", "Williams"),
    ("TEX @ ATH", "Rocker"),
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
        "title": "ARI @ ATL - Brandon Pfaadt (R, ARI) vs Chris Sale (L, ATL)",
        "description": "Tail key data: Park boost +7% (stadium -3%, weather +10%). Pfaadt (HR risk -0.69, vs LHB -0.40, vs RHB -0.51). Sale (HR risk -0.94, vs LHB -0.82, vs RHB -0.51).",
        "rows": [
            row("Matt Olson", "L", "+310", 69, "🌕 💣", ["vs Pfaadt"], """2 HR, 3 near-HR, 94.6 mph EV. Pfaadt LHB split -0.40, HR risk -0.69. tough split lane (-0.40); pitcher suppresses HR (-0.69).""", blast="high"),
            row("Drake Baldwin", "L", "+457", 58, "💎", ["vs Pfaadt"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.8 mph EV. Pfaadt LHB split -0.40, HR risk -0.69. tough split lane (-0.40); pitcher suppresses HR (-0.69).""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+387", 58, "", ["vs Pfaadt"], """0 HR, 1 near-HR, 95.2 mph EV. Pfaadt RHB split -0.51, HR risk -0.69. tough split lane (-0.51); pitcher suppresses HR (-0.69).""", blast="good"),
            row("Michael Harris II", "L", "+411", 58, "", ["vs Pfaadt"], """0 HR, 2 near-HR, 96.0 mph EV. Pfaadt LHB split -0.40, HR risk -0.69. tough split lane (-0.40); pitcher suppresses HR (-0.69).""", blast="good"),
        ],
    },
    {
        "title": "BAL @ TB - Chris Bassitt (R, BAL) vs Steven Matz (L, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +0%). Bassitt (HR risk -0.20, vs LHB +0.56, vs RHB -1.21). Matz (HR risk 0.31, vs LHB -0.56, vs RHB +1.01).",
        "rows": [
            row("Victor Mesa Jr.", "L", "+541", 76, "🌕 💣 💎", ["vs Bassitt"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.1 mph EV. Bassitt LHB split +0.56, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="high"),
            row("Yandy Diaz", "R", "+790", 58, "", ["vs Bassitt"], """1 HR, 1 near-HR, 95.3 mph EV. Bassitt RHB split -1.21, HR risk -0.20. tough split lane (-1.21); pitcher risk below avg (-0.20).""", blast="good"),
            row("Jonathan Aranda", "L", "+553", 58, "💎", ["vs Bassitt"], """Worst Pickz Hidden Gem. 0 HR, 91.6 mph EV. Bassitt LHB split +0.56, HR risk -0.20. pitcher risk below avg (-0.20); limited recent HR events."""),
            row("Junior Caminero", "R", "+330", 58, "", ["vs Bassitt"], """1 HR, 1 near-HR, 85.9 mph EV. Bassitt RHB split -1.21, HR risk -0.20. tough split lane (-1.21); pitcher risk below avg (-0.20).""", blast="good"),
            row("Pete Alonso", "R", "+360", 75, "⭐", ["vs Matz"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.0 mph EV. Matz RHB split +1.01, HR risk 0.31.""", blast="good"),
            row("Coby Mayo", "R", "+450", 73, "⭐", ["vs Matz"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 92.4 mph EV. Matz RHB split +1.01, HR risk 0.31.""", blast="good"),
        ],
    },
    {
        "title": "BOS @ PIT - Jake Bennett (L, BOS) vs Bubba Chandler (R, PIT)",
        "description": "Tail key data: Park boost -15% (stadium -17%, weather +1%). Bennett (HR risk -0.73, vs LHB -1.57, vs RHB -0.06). Chandler (HR risk -1.00, vs LHB -0.31, vs RHB -1.14).",
        "rows": [
            row("Ronny Simon", "S", "+1450", 58, "🚀", ["vs Bennett"], """0 HR, 1 near-HR, 101.2 mph EV. Bennett SHB→RHB split -0.06, HR risk -0.73. slight split headwind (-0.06); pitcher suppresses HR (-0.73).""", blast="good"),
            row("Bryan Reynolds", "S", "+820", 58, "💎", ["vs Bennett"], """Worst Pickz Hidden Gem. 0 HR, 91.0 mph EV. Bennett SHB→RHB split -0.06, HR risk -0.73. slight split headwind (-0.06); pitcher suppresses HR (-0.73)."""),
            row("Esmerlyn Valdez", "R", "+670", 58, "", ["vs Bennett"], """1 HR, 1 near-HR, 90.8 mph EV. Bennett RHB split -0.06, HR risk -0.73. slight split headwind (-0.06); pitcher suppresses HR (-0.73).""", blast="good"),
            row("Jarren Duran", "L", "+700", 58, "", ["vs Chandler"], """1 HR, 1 near-HR, 96.3 mph EV. Chandler LHB split -0.31, HR risk -1.00. slight split headwind (-0.31); pitcher suppresses HR (-1.00).""", blast="good"),
            row("Wilyer Abreu", "L", "+540", 58, "🌕 💣", ["vs Chandler"], """2 HR, 2 near-HR, 91.9 mph EV. Chandler LHB split -0.31, HR risk -1.00. slight split headwind (-0.31); pitcher suppresses HR (-1.00).""", blast="high"),
        ],
    },
    {
        "title": "COL @ SF - Kyle Freeland (L, COL) vs Landen Roupp (R, SF)",
        "description": "Tail key data: Park boost -19% (stadium -16%, weather -3%). Freeland (HR risk 0.77, vs LHB -0.74, vs RHB +1.27). Roupp (HR risk -0.81, vs LHB -0.65, vs RHB -0.34).",
        "rows": [
            row("Rafael Devers", "L", "+580", 58, "", ["vs Freeland"], """0 HR, 90.1 mph EV. Freeland LHB split -0.74, HR risk 0.77. tough split lane (-0.74); park/weather net drag (-19%)."""),
            row("Bryce Eldridge", "L", "+640", 58, "", ["vs Freeland"], """0 HR, 93.6 mph EV. Freeland LHB split -0.74, HR risk 0.77. tough split lane (-0.74); park/weather net drag (-19%).""", blast="good"),
            row("Victor Bericoto", "R", "+660", 66, "", ["vs Freeland"], """0 HR, 91.4 mph EV. Freeland RHB split +1.27, HR risk 0.77. park/weather net drag (-19%); limited recent HR events."""),
            row("Willy Adames", "R", "+565", 62, "", ["vs Freeland"], """0 HR, 88.1 mph EV. Freeland RHB split +1.27, HR risk 0.77. park/weather net drag (-19%); limited recent HR events."""),
            row("Zac Veen", "L", "+1000", 58, "🚀", ["vs Roupp"], """1 HR, 1 near-HR, 104.7 mph EV. Roupp LHB split -0.65, HR risk -0.81. tough split lane (-0.65); pitcher suppresses HR (-0.81).""", blast="good"),
            row("Willi Castro", "S", "+1120", 58, "", ["vs Roupp"], """0 HR, 88.6 mph EV. Roupp SHB→RHB split -0.34, HR risk -0.81. slight split headwind (-0.34); pitcher suppresses HR (-0.81)."""),
            row("Hunter Goodman", "R", "+600", 58, "⭐ 🌕 💣", ["vs Roupp"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.5 mph EV. Roupp RHB split -0.34, HR risk -0.81. slight split headwind (-0.34); pitcher suppresses HR (-0.81).""", blast="high"),
        ],
    },
    {
        "title": "CWS @ DET - Sean Newcomb (L, CWS) vs Jackson Jobe (R, DET)",
        "description": "Tail key data: Park boost data unavailable. Newcomb (HR risk -1.17, vs LHB -1.02, vs RHB -0.57). Jobe (HR risk -0.43, vs LHB +0.44, vs RHB -0.86).",
        "rows": [
            row("Eduardo Valencia", "R", "+400", 59, "🌕 💣", ["vs Newcomb"], """2 HR, 2 near-HR, 96.5 mph EV. Newcomb RHB split -0.57, HR risk -1.17. tough split lane (-0.57); pitcher suppresses HR (-1.17).""", blast="high"),
            row("Gleyber Torres", "R", "+720", 58, "", ["vs Newcomb"], """1 HR, 3 near-HR, 96.4 mph EV. Newcomb RHB split -0.57, HR risk -1.17. tough split lane (-0.57); pitcher suppresses HR (-1.17).""", blast="good"),
            row("Spencer Torkelson", "R", "+409", 58, "", ["vs Newcomb"], """0 HR, 93.0 mph EV. Newcomb RHB split -0.57, HR risk -1.17. tough split lane (-0.57); pitcher suppresses HR (-1.17).""", blast="good"),
            row("Munetaka Murakami", "L", "+252", 74, "⭐ 🌕 💣", ["vs Jobe"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.4 mph EV. Jobe LHB split +0.44, HR risk -0.43. pitcher suppresses HR (-0.43).""", blast="high"),
            row("Drew Romo", "S", "+980", 58, "", ["vs Jobe"], """1 HR, 1 near-HR, 89.4 mph EV. Jobe SHB→LHB split +0.44, HR risk -0.43. pitcher suppresses HR (-0.43).""", blast="good"),
            row("Randal Grichuk", "R", "N/A", 58, "", ["vs Jobe"], """0 HR, 97.0 mph EV. Jobe RHB split -0.86, HR risk -0.43. tough split lane (-0.86); pitcher suppresses HR (-0.43).""", blast="good"),
        ],
    },
    {
        "title": "KC @ LAA - Seth Lugo (R, KC) vs Grayson Rodriguez 🧤 (R, LAA)",
        "description": "Tail key data: Park boost -9% (stadium -9%, weather +0%). Lugo (HR risk -0.18, vs LHB -0.08, vs RHB -0.11). Rodriguez 🧤 (HR risk 1.57, vs LHB +0.16, vs RHB +2.12).",
        "rows": [
            row("Mike Trout", "R", "+410", 59, "⭐", ["vs Lugo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.8 mph EV. Lugo RHB split -0.11, HR risk -0.18. slight split headwind (-0.11); pitcher risk below avg (-0.18).""", blast="good"),
            row("Moises Ballesteros", "L", "+630", 58, "", ["vs Lugo"], """0 HR, 94.4 mph EV. Lugo LHB split -0.08, HR risk -0.18. slight split headwind (-0.08); pitcher risk below avg (-0.18).""", blast="good"),
            row("Jac Caglianone", "L", "+280", 78, "⭐", ["vs Rodriguez"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 98.9 mph EV. Rodriguez LHB split +0.16, HR risk 1.57. park/weather net drag (-9%); limited recent HR events.""", blast="good"),
            row("Salvador Perez", "R", "+440", 82, "", ["vs Rodriguez"], """0 HR, 1 near-HR, 90.5 mph EV. Rodriguez RHB split +2.12, HR risk 1.57. park/weather net drag (-9%); limited recent HR events."""),
            row("Bobby Witt Jr.", "R", "+390", 89, "🌕 💣", ["vs Rodriguez"], """0 HR, 2 near-HR, 92.4 mph EV. Rodriguez RHB split +2.12, HR risk 1.57. park/weather net drag (-9%).""", blast="good"),
            row("Isaac Collins", "S", "+625", 86, "", ["vs Rodriguez"], """0 HR, 92.1 mph EV. Rodriguez SHB→RHB split +2.12, HR risk 1.57. park/weather net drag (-9%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ CIN - Sandy Alcantara (R, MIA) vs Chase Burns (R, CIN)",
        "description": "Tail key data: Park boost +20% (stadium +14%, weather +5%). Alcantara (HR risk 0.02, vs LHB -0.17, vs RHB +0.37). Burns (HR risk -0.40, vs LHB +0.01, vs RHB -0.68).",
        "rows": [
            row("Tyler Stephenson", "R", "+520", 70, "💎", ["vs Alcantara"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.1 mph EV. Alcantara RHB split +0.37, HR risk 0.02.""", blast="good"),
            row("Matt McLain", "R", "+680", 72, "", ["vs Alcantara"], """1 HR, 2 near-HR, 93.8 mph EV. Alcantara RHB split +0.37, HR risk 0.02.""", blast="good"),
            row("Eugenio Suarez", "R", "+397", 78, "🌕 💣", ["vs Alcantara"], """2 HR, 2 near-HR, 92.2 mph EV. Alcantara RHB split +0.37, HR risk 0.02.""", blast="high"),
            row("Sal Stewart", "R", "+422", 65, "", ["vs Alcantara"], """1 HR, 1 near-HR, 88.5 mph EV. Alcantara RHB split +0.37, HR risk 0.02.""", blast="good"),
            row("Griffin Conine", "L", "+440", 80, "🚀 ⭐ 🌕 💣", ["vs Burns"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 100.8 mph EV. Burns LHB split +0.01, HR risk -0.40. pitcher suppresses HR (-0.40).""", blast="high"),
            row("Joe Mack", "L", "+720", 66, "", ["vs Burns"], """1 HR, 1 near-HR, 96.2 mph EV. Burns LHB split +0.01, HR risk -0.40. pitcher suppresses HR (-0.40).""", blast="good"),
            row("Owen Caissie", "L", "+590", 73, "🌕 💣", ["vs Burns"], """2 HR, 2 near-HR, 93.7 mph EV. Burns LHB split +0.01, HR risk -0.40. pitcher suppresses HR (-0.40).""", blast="high"),
        ],
    },
    {
        "title": "MIL @ LAD - Robert Gasser (L, MIL) vs Yoshinobu Yamamoto (R, LAD)",
        "description": "Tail key data: Park boost +12% (stadium +19%, weather -7%). Gasser (HR risk 0.68, vs LHB -0.10, vs RHB +0.67). Yamamoto (HR risk -0.21, vs LHB -0.57, vs RHB +0.53).",
        "rows": [
            row("Teoscar Hernandez", "R", "+443", 86, "💎", ["vs Gasser"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 94.3 mph EV. Gasser RHB split +0.67, HR risk 0.68. weather carry headwind (-7%).""", blast="good"),
            row("Mookie Betts", "R", "+494", 81, "", ["vs Gasser"], """1 HR, 2 near-HR, 93.4 mph EV. Gasser RHB split +0.67, HR risk 0.68. weather carry headwind (-7%).""", blast="good"),
            row("Shohei Ohtani", "L", "+260", 84, "🌕 💣 💎", ["vs Gasser"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.6 mph EV. Gasser LHB split -0.10, HR risk 0.68. slight split headwind (-0.10); weather carry headwind (-7%).""", blast="high"),
            row("Andy Pages", "R", "+406", 81, "", ["vs Gasser"], """1 HR, 1 near-HR, 94.9 mph EV. Gasser RHB split +0.67, HR risk 0.68. weather carry headwind (-7%).""", blast="good"),
            row("Jake Bauers", "L", "+476", 58, "💎", ["vs Yamamoto"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.3 mph EV. Yamamoto LHB split -0.57, HR risk -0.21. tough split lane (-0.57); pitcher risk below avg (-0.21).""", blast="good"),
            row("Brice Turang", "L", "N/A", 58, "", ["vs Yamamoto"], """0 HR, 97.9 mph EV. Yamamoto LHB split -0.57, HR risk -0.21. tough split lane (-0.57); pitcher risk below avg (-0.21).""", blast="good"),
            row("William Contreras", "R", "+593", 63, "💎", ["vs Yamamoto"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.4 mph EV. Yamamoto RHB split +0.53, HR risk -0.21. pitcher risk below avg (-0.21); weather carry headwind (-7%).""", blast="good"),
            row("Joey Ortiz", "R", "+1080", 58, "", ["vs Yamamoto"], """0 HR, 91.1 mph EV. Yamamoto RHB split +0.53, HR risk -0.21. pitcher risk below avg (-0.21); weather carry headwind (-7%)."""),
        ],
    },
    {
        "title": "NYY @ TOR - Gerrit Cole (R, NYY) vs Shane Bieber (R, TOR)",
        "description": "Tail key data: Park boost +1% (stadium +7%, weather -6%). Cole (HR risk 0.48, vs LHB +0.30, vs RHB +0.38). Bieber (HR risk 0.59, vs LHB +0.69, vs RHB +0.11).",
        "rows": [
            row("Jesus Sanchez", "L", "+500", 68, "", ["vs Cole"], """1 HR, 1 near-HR, 89.7 mph EV. Cole LHB split +0.30, HR risk 0.48. weather carry headwind (-6%).""", blast="good"),
            row("Kazuma Okamoto", "R", "+428", 68, "", ["vs Cole"], """1 HR, 1 near-HR, 88.9 mph EV. Cole RHB split +0.38, HR risk 0.48. weather carry headwind (-6%).""", blast="good"),
            row("George Springer", "R", "+514", 85, "🌕 💣", ["vs Cole"], """2 HR, 3 near-HR, 91.4 mph EV. Cole RHB split +0.38, HR risk 0.48. weather carry headwind (-6%).""", blast="high"),
            row("Ben Rice", "L", "+330", 70, "", ["vs Bieber"], """0 HR, 93.0 mph EV. Bieber LHB split +0.69, HR risk 0.59. weather carry headwind (-6%); limited recent HR events.""", blast="good"),
            row("Spencer Jones", "L", "+520", 63, "", ["vs Bieber"], """0 HR, 89.9 mph EV. Bieber LHB split +0.69, HR risk 0.59. weather carry headwind (-6%); limited recent HR events."""),
            row("Jazz Chisholm Jr.", "L", "+490", 75, "", ["vs Bieber"], """0 HR, 1 near-HR, 97.0 mph EV. Bieber LHB split +0.69, HR risk 0.59. weather carry headwind (-6%); limited recent HR events.""", blast="good"),
            row("Luis Garcia Jr.", "L", "+440", 76, "", ["vs Bieber"], """1 HR, 2 near-HR, 92.3 mph EV. Bieber LHB split +0.69, HR risk 0.59. weather carry headwind (-6%).""", blast="good"),
        ],
    },
    {
        "title": "SD @ CLE - Michael King (R, SD) vs Gavin Williams 🧤 (R, CLE)",
        "description": "Tail key data: Park boost -7% (stadium -2%, weather -5%). King (HR risk 0.61, vs LHB +0.41, vs RHB +0.52). Williams 🧤 (HR risk 1.12, vs LHB +0.93, vs RHB +0.74).",
        "rows": [
            row("Angel Genao", "S", "+800", 77, "💎", ["vs King"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 98.4 mph EV. King SHB→RHB split +0.52, HR risk 0.61. park/weather net drag (-7%).""", blast="good"),
            row("Nathaniel Lowe", "L", "+587", 71, "", ["vs King"], """1 HR, 2 near-HR, 91.2 mph EV. King LHB split +0.41, HR risk 0.61. park/weather net drag (-7%).""", blast="good"),
            row("Patrick Bailey", "S", "+875", 75, "", ["vs King"], """1 HR, 1 near-HR, 95.6 mph EV. King SHB→RHB split +0.52, HR risk 0.61. park/weather net drag (-7%).""", blast="good"),
            row("Chase DeLauter", "L", "+590", 68, "", ["vs King"], """0 HR, 1 near-HR, 93.1 mph EV. King LHB split +0.41, HR risk 0.61. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
            row("Jackson Merrill", "L", "+540", 95, "⭐ 🌕 💣", ["vs Williams"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 98.3 mph EV. Williams LHB split +0.93, HR risk 1.12. park/weather net drag (-7%).""", blast="high"),
            row("Manny Machado", "R", "+630", 78, "🚀", ["vs Williams"], """0 HR, 101.3 mph EV. Williams RHB split +0.74, HR risk 1.12. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
            row("Xander Bogaerts", "R", "+990", 83, "", ["vs Williams"], """1 HR, 1 near-HR, 95.3 mph EV. Williams RHB split +0.74, HR risk 1.12. park/weather net drag (-7%).""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+499", 69, "", ["vs Williams"], """0 HR, 90.9 mph EV. Williams RHB split +0.74, HR risk 1.12. park/weather net drag (-7%); limited recent HR events."""),
        ],
    },
    {
        "title": "SEA @ HOU - George Kirby (R, SEA) vs Peter Lambert (R, HOU)",
        "description": "Tail key data: Park boost +6% (stadium +6%, weather -1%). Kirby (HR risk 0.90, vs LHB +0.88, vs RHB +0.49). Lambert (HR risk -0.32, vs LHB -0.23, vs RHB -0.22).",
        "rows": [
            row("Daulton Varsho", "L", "+670", 80, "💎", ["vs Kirby"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.6 mph EV. Kirby LHB split +0.88, HR risk 0.90.""", blast="good"),
            row("Taylor Trammell", "L", "+475", 79, "", ["vs Kirby"], """1 HR, 2 near-HR, 89.5 mph EV. Kirby LHB split +0.88, HR risk 0.90.""", blast="good"),
            row("Yordan Alvarez", "L", "+250", 79, "🚀 ⭐", ["vs Kirby"], """Worst Pickz Favorite. 0 HR, 100.8 mph EV. Kirby LHB split +0.88, HR risk 0.90. limited recent HR events.""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 77, "", ["vs Kirby"], """0 HR, 1 near-HR, 96.5 mph EV. Kirby RHB split +0.49, HR risk 0.90. limited recent HR events.""", blast="good"),
            row("Cam Smith", "R", "+610", 68, "", ["vs Kirby"], """0 HR, 1 near-HR, 90.6 mph EV. Kirby RHB split +0.49, HR risk 0.90. limited recent HR events."""),
            row("Julio Rodriguez", "R", "+470", 79, "🌕 💣", ["vs Lambert"], """3 HR, 3 near-HR, 96.6 mph EV. Lambert RHB split -0.22, HR risk -0.32. slight split headwind (-0.22); pitcher risk below avg (-0.32).""", blast="high"),
            row("Dominic Canzone", "L", "+410", 61, "💎", ["vs Lambert"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.8 mph EV. Lambert LHB split -0.23, HR risk -0.32. slight split headwind (-0.23); pitcher risk below avg (-0.32).""", blast="good"),
            row("Josh Naylor", "L", "+680", 58, "💎", ["vs Lambert"], """Worst Pickz Hidden Gem. 0 HR, 95.6 mph EV. Lambert LHB split -0.23, HR risk -0.32. slight split headwind (-0.23); pitcher risk below avg (-0.32).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ ATH - Kumar Rocker 🧤 (R, TEX) vs Gage Jump (L, ATH)",
        "description": "Tail key data: Park boost +32% (stadium +30%, weather +2%). Rocker 🧤 (HR risk 1.06, vs LHB +1.22, vs RHB +0.49). Home starter risk unavailable.",
        "rows": [
            row("Lawrence Butler", "L", "+555", 99, "⭐ 🌕 💣", ["vs Rocker"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 98.9 mph EV. Rocker LHB split +1.22, HR risk 1.06.""", blast="high"),
            row("Tyler Soderstrom", "L", "+390", 90, "🌕 💣 💎", ["vs Rocker"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.2 mph EV. Rocker LHB split +1.22, HR risk 1.06. limited recent HR events.""", blast="good"),
            row("Henry Bolte", "R", "+880", 85, "", ["vs Rocker"], """0 HR, 98.6 mph EV. Rocker RHB split +0.49, HR risk 1.06. limited recent HR events.""", blast="good"),
            row("Zack Gelof", "R", "+520", 82, "", ["vs Rocker"], """1 HR, 2 near-HR, 85.4 mph EV. Rocker RHB split +0.49, HR risk 1.06. lighter EV form (85.4 mph).""", blast="good"),
            row("Justin Foscue", "R", "+570", 58, "", ["vs Jump"], """0 HR, 87.0 mph EV. Jump split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
            row("Elias Diaz", "R", "+590", 67, "", ["vs Jump"], """0 HR, 1 near-HR, 92.6 mph EV. Jump split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "WSH @ NYM - Andrew Alvarez (L, WSH) vs Robert Stock (R, NYM)",
        "description": "Tail key data: Park boost data unavailable. Alvarez (HR risk -1.38, vs LHB -0.82, vs RHB -0.96). Stock (HR risk 0.56, vs LHB +1.28, vs RHB -0.93).",
        "rows": [
            row("Francisco Alvarez", "R", "+496", 58, "💎", ["vs Alvarez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.4 mph EV. Alvarez RHB split -0.96, HR risk -1.38. tough split lane (-0.96); pitcher suppresses HR (-1.38).""", blast="good"),
            row("Carson Benge", "L", "+1040", 58, "", ["vs Alvarez"], """0 HR, 1 near-HR, 94.2 mph EV. Alvarez LHB split -0.82, HR risk -1.38. tough split lane (-0.82); pitcher suppresses HR (-1.38).""", blast="good"),
            row("A.J. Ewing", "L", "+980", 58, "", ["vs Alvarez"], """0 HR, 92.6 mph EV. Alvarez LHB split -0.82, HR risk -1.38. tough split lane (-0.82); pitcher suppresses HR (-1.38).""", blast="good"),
            row("Luis Robert", "R", "+710", 58, "⭐", ["vs Alvarez"], """Worst Pickz Favorite. 0 HR, 94.3 mph EV. Alvarez RHB split -0.96, HR risk -1.38. tough split lane (-0.96); pitcher suppresses HR (-1.38).""", blast="good"),
            row("Daylen Lile", "L", "+569", 79, "⭐", ["vs Stock"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.8 mph EV. Stock LHB split +1.28, HR risk 0.56. limited recent HR events.""", blast="good"),
            row("Abimelec Ortiz", "L", "+562", 94, "⭐ 🌕 💣", ["vs Stock"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 97.2 mph EV. Stock LHB split +1.28, HR risk 0.56.""", blast="high"),
            row("Jose Tena", "L", "+880", 77, "", ["vs Stock"], """1 HR, 1 near-HR, 90.5 mph EV. Stock LHB split +1.28, HR risk 0.56.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-14")

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

    out = ROOT / '_games-0814.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
