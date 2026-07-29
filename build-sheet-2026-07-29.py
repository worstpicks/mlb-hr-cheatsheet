#!/usr/bin/env python3
"""Generate games[] block for 2026-07-29 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Cal Raleigh (S)",
    "Coby Mayo (R)",
    "Dominic Canzone (L)",
    "Drake Baldwin (L)",
    "Elly De La Cruz (S)",
    "Hunter Goodman (R)",
    "JJ Bleday (L)",
    "Jac Caglianone (L)",
    "James Wood (L)",
    "Joc Pederson (L)",
    "Kyle Manzardo (L)",
    "Kyle Tucker (L)",
    "Matt Olson (L)",
    "Mike Yastrzemski (L)",
    "Pete Alonso (R)",
    "Pete Crow-Armstrong (L)",
    "Rafael Devers (L)",
    "Rhys Hoskins (R)",
    "Ronald Acuna Jr. (R)",
    "Tyrone Taylor (R)",
    "Willson Contreras (R)",
}

GEMS = {
    "Brett Baty (L)",
    "Carter Jensen (L)",
    "Dalton Rushing (L)",
    "Dylan Crews (R)",
    "Heriberto Hernandez (R)",
    "Jacob Gonzalez (L)",
    "Jazz Chisholm Jr. (L)",
    "Jo Adell (R)",
    "Jorge Soler (R)",
    "Mickey Moniak (L)",
    "Munetaka Murakami (L)",
    "Noelvi Marte (R)",
    "Ryan Jeffers (R)",
    "Spencer Jones (L)",
    "Willi Castro (S)",
}

PLAYER_TEAMS = {
    "Anthony Seigler (S)": "BOS",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Brandon Lowe (L)": "PIT",
    "Brandon Valenzuela (S)": "TOR",
    "Brett Baty (L)": "NYM",
    "Brian Navarreto (R)": "MIA",
    "Brian Serven (R)": "ATH",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "CJ Abrams (L)": "WSH",
    "Cal Raleigh (S)": "SEA",
    "Carson Benge (L)": "NYM",
    "Carter Jensen (L)": "KC",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Coby Mayo (R)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "Daulton Varsho (L)": "TOR",
    "Derek Hill (R)": "PHI",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Dylan Crews (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Esteury Ruiz (R)": "MIA",
    "Eugenio Suarez (R)": "CIN",
    "Ezequiel Duran (R)": "TEX",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Lindor (S)": "NYM",
    "Gabriel Arias (R)": "CLE",
    "Garrett Mitchell (L)": "MIL",
    "Gleyber Torres (R)": "DET",
    "Hao-Yu Lee (R)": "DET",
    "Heliot Ramos (R)": "SF",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "Jacob Gonzalez (L)": "PIT",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Jorge Mateo (R)": "ATL",
    "Jorge Soler (R)": "LAA",
    "Josh Naylor (L)": "SEA",
    "Kody Clemens (L)": "MIN",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Tucker (L)": "LAD",
    "Luis Garcia Jr. (L)": "WSH",
    "Luis Lara (S)": "MIL",
    "Luis Rengifo (S)": "SD",
    "Manny Machado (R)": "SD",
    "Marcus Semien (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Michael Busch (L)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Mickey Moniak (L)": "COL",
    "Miguel Amaya (R)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Mike Yastrzemski (L)": "ATL",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "STL",
    "Noelvi Marte (R)": "CIN",
    "Otto Lopez (R)": "MIA",
    "Ozzie Albies (S)": "ATL",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Petey Halpin (L)": "CLE",
    "Rafael Devers (L)": "SF",
    "Rhys Hoskins (R)": "CLE",
    "Romy Gonzalez (R)": "BOS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan Jeffers (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Ryan Waldschmidt (R)": "ARI",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Taylor Trammell (L)": "HOU",
    "Tim Tawa (R)": "ARI",
    "Ty France (R)": "SD",
    "Tyler Soderstrom (L)": "ATH",
    "Tyrone Taylor (R)": "NYM",
    "Vaughn Grissom (R)": "LAA",
    "Victor Mesa Jr. (L)": "TB",
    "Vinnie Pasquantino (L)": "KC",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("ATL @ NYM (G1)", "Manaea"),
    ("HOU @ LAA", "Rodriguez"),
    ("HOU @ LAA", "Wesneski"),
    ("KC @ MIN", "Ryan"),
    ("SEA @ LAD", "Lauer"),
    ("TOR @ WSH", "Littell"),
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
        "title": "ARI @ PIT - Eduardo Rodriguez (L, ARI) vs Jared Jones (R, PIT)",
        "description": "Tail key data: Park boost -10% (stadium -15%, weather +6%). Rodriguez (HR risk 0.26, vs LHB +0.43, vs RHB +0.08). Jones (HR risk -0.22, vs LHB +0.02, vs RHB -0.42).",
        "rows": [
            row("Esmerlyn Valdez", "R", "+361", 60, "", ["vs Rodriguez"], """1 HR, 1 near-HR, 92.0 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; park/weather net drag (-10%).""", blast="good"),
            row("Brandon Lowe", "L", "+460", 58, "", ["vs Rodriguez"], """0 HR, 1 near-HR, 91.7 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; park/weather net drag (-10%)."""),
            row("Jacob Gonzalez", "L", "+760", 58, "💎", ["vs Rodriguez"], """Worst Pickz Hidden Gem. 0 HR, 93.8 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; park/weather net drag (-10%).""", blast="good"),
            row("Corbin Carroll", "L", "+368", 58, "", ["vs Jones"], """0 HR, 91.8 mph EV. Jones LHB split +0.02, HR risk -0.22. pitcher risk below avg (-0.22); park/weather net drag (-10%)."""),
            row("Ryan Waldschmidt", "R", "+920", 58, "", ["vs Jones"], """1 HR, 2 near-HR, 87.9 mph EV. Jones RHB split -0.42, HR risk -0.22. tough split lane (-0.42); pitcher risk below avg (-0.22).""", blast="good"),
            row("Tim Tawa", "R", "+830", 58, "", ["vs Jones"], """0 HR, 1 near-HR, 90.2 mph EV. Jones RHB split -0.42, HR risk -0.22. tough split lane (-0.42); pitcher risk below avg (-0.22)."""),
        ],
    },
    {
        "title": "ATL @ NYM (G1) - AJ Smith-Shawver (R, ATL) vs Sean Manaea 🧤 (L, NYM)",
        "description": "Tail key data: Park boost +3% (stadium -1%, weather +4%). Smith-Shawver (HR risk 0.34, vs LHB +0.41, vs RHB +0.10). Manaea 🧤 (HR risk 1.00, vs LHB -0.02, vs RHB +1.12).",
        "rows": [
            row("Brett Baty", "L", "+600", 81, "🌕 💣 💎", ["vs Smith-Shawver"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.1 mph EV. Smith-Shawver LHB split +0.41, HR risk 0.34.""", blast="high"),
            row("Jared Young", "L", "+470", 59, "", ["vs Smith-Shawver"], """0 HR, 1 near-HR, 91.9 mph EV. Smith-Shawver LHB split +0.41, HR risk 0.34. limited recent HR events."""),
            row("Francisco Lindor", "S", "+425", 63, "", ["vs Smith-Shawver"], """1 HR, 1 near-HR, 87.3 mph EV. Smith-Shawver SHB→LHB split +0.41, HR risk 0.34. lighter EV form (87.3 mph).""", blast="good"),
            row("Marcus Semien", "R", "+640", 78, "🌕 💣", ["vs Smith-Shawver"], """3 HR, 3 near-HR, 87.8 mph EV. Smith-Shawver RHB split +0.10, HR risk 0.34. lighter EV form (87.8 mph).""", blast="high"),
            row("Ronald Acuna Jr.", "R", "+400", 85, "⭐", ["vs Manaea"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.5 mph EV. Manaea RHB split +1.12, HR risk 1.00.""", blast="good"),
            row("Austin Riley", "R", "+425", 84, "", ["vs Manaea"], """0 HR, 1 near-HR, 95.3 mph EV. Manaea RHB split +1.12, HR risk 1.00. limited recent HR events.""", blast="good"),
            row("Jorge Mateo", "R", "N/A", 88, "🌕 💣", ["vs Manaea"], """1 HR, 1 near-HR, 97.2 mph EV. Manaea RHB split +1.12, HR risk 1.00.""", blast="good"),
            row("Ozzie Albies", "S", "+480", 91, "🌕 💣", ["vs Manaea"], """2 HR, 2 near-HR, 89.8 mph EV. Manaea SHB→RHB split +1.12, HR risk 1.00.""", blast="high"),
        ],
    },
    {
        "title": "ATL @ NYM (G2) - Chris Sale (L, ATL) vs Christian Scott (R, NYM)",
        "description": "Tail key data: Park boost +4% (stadium -1%, weather +5%). Sale (HR risk -0.59, vs LHB -1.03, vs RHB -0.06). Scott (HR risk 0.16, vs LHB +0.43, vs RHB -0.76).",
        "rows": [
            row("Tyrone Taylor", "R", "+680", 68, "⭐ 🌕 💣", ["vs Sale"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.3 mph EV. Sale RHB split -0.06, HR risk -0.59. slight split headwind (-0.06); pitcher suppresses HR (-0.59).""", blast="high"),
            row("Carson Benge", "L", "+870", 58, "", ["vs Sale"], """1 HR, 1 near-HR, 87.1 mph EV. Sale LHB split -1.03, HR risk -0.59. tough split lane (-1.03); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Marcus Semien", "R", "+540", 58, "", ["vs Sale"], """0 HR, 1 near-HR, 93.8 mph EV. Sale RHB split -0.06, HR risk -0.59. slight split headwind (-0.06); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Francisco Lindor", "S", "+390", 58, "", ["vs Sale"], """1 HR, 2 near-HR, 89.0 mph EV. Sale SHB→RHB split -0.06, HR risk -0.59. slight split headwind (-0.06); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Drake Baldwin", "L", "+390", 80, "⭐ 🌕 💣", ["vs Scott"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.4 mph EV. Scott LHB split +0.43, HR risk 0.16.""", blast="high"),
            row("Mike Yastrzemski", "L", "+540", 66, "⭐", ["vs Scott"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.9 mph EV. Scott LHB split +0.43, HR risk 0.16.""", blast="good"),
            row("Matt Olson", "L", "+320", 77, "⭐ 🌕 💣", ["vs Scott"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.4 mph EV. Scott LHB split +0.43, HR risk 0.16.""", blast="high"),
        ],
    },
    {
        "title": "BAL @ DET - Trevor Rogers (L, BAL) vs Tarik Skubal (L, DET)",
        "description": "Tail key data: Park boost +2% (stadium -9%, weather +11%). Rogers (HR risk -0.70, vs LHB -1.09, vs RHB -0.21). Skubal (HR risk -0.61, vs LHB +0.16, vs RHB -0.58).",
        "rows": [
            row("Dillon Dingler", "R", "+471", 58, "", ["vs Rogers"], """0 HR, 2 near-HR, 96.7 mph EV. Rogers RHB split -0.21, HR risk -0.70. slight split headwind (-0.21); pitcher suppresses HR (-0.70).""", blast="good"),
            row("Hao-Yu Lee", "R", "+547", 58, "", ["vs Rogers"], """0 HR, 1 near-HR, 93.6 mph EV. Rogers RHB split -0.21, HR risk -0.70. slight split headwind (-0.21); pitcher suppresses HR (-0.70).""", blast="good"),
            row("Gleyber Torres", "R", "+650", 58, "", ["vs Rogers"], """0 HR, 1 near-HR, 92.7 mph EV. Rogers RHB split -0.21, HR risk -0.70. slight split headwind (-0.21); pitcher suppresses HR (-0.70).""", blast="good"),
            row("Coby Mayo", "R", "+476", 64, "🚀 ⭐ 🌕 💣", ["vs Skubal"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 103.3 mph EV. Skubal RHB split -0.58, HR risk -0.61. tough split lane (-0.58); pitcher suppresses HR (-0.61).""", blast="high"),
            row("Pete Alonso", "R", "+362", 58, "🚀 ⭐", ["vs Skubal"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 100.2 mph EV. Skubal RHB split -0.58, HR risk -0.61. tough split lane (-0.58); pitcher suppresses HR (-0.61).""", blast="good"),
            row("Christian Encarnacion-Strand", "R", "+600", 58, "🌕 💣", ["vs Skubal"], """2 HR, 2 near-HR, 86.1 mph EV. Skubal RHB split -0.58, HR risk -0.61. tough split lane (-0.58); pitcher suppresses HR (-0.61).""", blast="high"),
        ],
    },
    {
        "title": "BOS @ ATH - Patrick Sandoval (L, BOS) vs Jacob Lopez (L, ATH)",
        "description": "Tail key data: Park boost +36% (stadium +32%, weather +4%). Sandoval (HR risk -1.03, vs LHB +2.10, vs RHB -1.59). Lopez (HR risk -0.54, vs LHB -0.75, vs RHB -0.19).",
        "rows": [
            row("Tyler Soderstrom", "L", "+390", 76, "", ["vs Sandoval"], """1 HR, 1 near-HR, 93.1 mph EV. Sandoval LHB split +2.10, HR risk -1.03. pitcher suppresses HR (-1.03).""", blast="good"),
            row("Henry Bolte", "R", "+700", 58, "", ["vs Sandoval"], """1 HR, 1 near-HR, 85.6 mph EV. Sandoval RHB split -1.59, HR risk -1.03. tough split lane (-1.59); pitcher suppresses HR (-1.03).""", blast="good"),
            row("Brian Serven", "R", "N/A", 58, "", ["vs Sandoval"], """1 HR, 1 near-HR, 94.7 mph EV. Sandoval RHB split -1.59, HR risk -1.03. tough split lane (-1.59); pitcher suppresses HR (-1.03).""", blast="good"),
            row("Willson Contreras", "R", "+235", 79, "⭐ 🌕 💣", ["vs Lopez"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.1 mph EV. Lopez RHB split -0.19, HR risk -0.54. slight split headwind (-0.19); pitcher suppresses HR (-0.54).""", blast="high"),
            row("Romy Gonzalez", "R", "+377", 58, "", ["vs Lopez"], """0 HR, 90.8 mph EV. Lopez RHB split -0.19, HR risk -0.54. slight split headwind (-0.19); pitcher suppresses HR (-0.54)."""),
            row("Wilyer Abreu", "L", "+350", 78, "🌕 💣", ["vs Lopez"], """2 HR, 3 near-HR, 96.7 mph EV. Lopez LHB split -0.75, HR risk -0.54. tough split lane (-0.75); pitcher suppresses HR (-0.54).""", blast="high"),
            row("Anthony Seigler", "S", "N/A", 61, "", ["vs Lopez"], """1 HR, 2 near-HR, 88.7 mph EV. Lopez SHB→RHB split -0.19, HR risk -0.54. slight split headwind (-0.19); pitcher suppresses HR (-0.54).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ STL - Matthew Boyd (L, CHC) vs Dustin May (R, STL)",
        "description": "Tail key data: Park boost -17% (stadium -10%, weather -8%). Boyd (HR risk 0.13, vs LHB -0.18, vs RHB +0.25). May (HR risk -0.93, vs LHB -0.49, vs RHB -0.75).",
        "rows": [
            row("Nelson Velazquez", "R", "+600", 62, "", ["vs Boyd"], """1 HR, 2 near-HR, 92.7 mph EV. Boyd RHB split +0.25, HR risk 0.13. park/weather net drag (-17%).""", blast="good"),
            row("Jordan Walker", "R", "+390", 59, "", ["vs Boyd"], """0 HR, 1 near-HR, 99.4 mph EV. Boyd RHB split +0.25, HR risk 0.13. park/weather net drag (-17%); limited recent HR events.""", blast="good"),
            row("Jimmy Crooks", "L", "N/A", 58, "", ["vs Boyd"], """0 HR, 1 near-HR, 89.7 mph EV. Boyd LHB split -0.18, HR risk 0.13. slight split headwind (-0.18); park/weather net drag (-17%)."""),
            row("Pete Crow-Armstrong", "L", "+400", 58, "⭐ 🌕 💣", ["vs May"], """Worst Pickz Favorite. 1 HR, 4 near-HR, 94.7 mph EV. May LHB split -0.49, HR risk -0.93. tough split lane (-0.49); pitcher suppresses HR (-0.93).""", blast="high"),
            row("Michael Conforto", "L", "N/A", 59, "🌕 💣", ["vs May"], """2 HR, 4 near-HR, 91.6 mph EV. May LHB split -0.49, HR risk -0.93. tough split lane (-0.49); pitcher suppresses HR (-0.93).""", blast="high"),
            row("Michael Busch", "L", "+525", 58, "", ["vs May"], """0 HR, 92.5 mph EV. May LHB split -0.49, HR risk -0.93. tough split lane (-0.49); pitcher suppresses HR (-0.93).""", blast="good"),
            row("Miguel Amaya", "R", "+499", 58, "", ["vs May"], """0 HR, 93.8 mph EV. May RHB split -0.75, HR risk -0.93. tough split lane (-0.75); pitcher suppresses HR (-0.93).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ CIN - Joey Cantillo (L, CLE) vs Brady Singer (R, CIN)",
        "description": "Tail key data: Park boost +19% (stadium +16%, weather +3%). Cantillo (HR risk -0.65, vs LHB -0.38, vs RHB -0.41). Singer (HR risk 0.52, vs LHB +0.64, vs RHB -0.42).",
        "rows": [
            row("JJ Bleday", "L", "+390", 76, "⭐ 🌕 💣", ["vs Cantillo"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 94.1 mph EV. Cantillo LHB split -0.38, HR risk -0.65. slight split headwind (-0.38); pitcher suppresses HR (-0.65).""", blast="high"),
            row("Elly De La Cruz", "S", "+360", 66, "⭐ 🌕 💣", ["vs Cantillo"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.2 mph EV. Cantillo SHB→LHB split -0.38, HR risk -0.65. slight split headwind (-0.38); pitcher suppresses HR (-0.65).""", blast="high"),
            row("Eugenio Suarez", "R", "+405", 58, "", ["vs Cantillo"], """1 HR, 1 near-HR, 88.8 mph EV. Cantillo RHB split -0.41, HR risk -0.65. tough split lane (-0.41); pitcher suppresses HR (-0.65).""", blast="good"),
            row("Sal Stewart", "R", "+373", 58, "", ["vs Cantillo"], """1 HR, 1 near-HR, 88.1 mph EV. Cantillo RHB split -0.41, HR risk -0.65. tough split lane (-0.41); pitcher suppresses HR (-0.65).""", blast="good"),
            row("Noelvi Marte", "R", "+600", 66, "🌕 💣 💎", ["vs Cantillo"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 92.1 mph EV. Cantillo RHB split -0.41, HR risk -0.65. tough split lane (-0.41); pitcher suppresses HR (-0.65).""", blast="high"),
            row("Kyle Manzardo", "L", "+310", 79, "⭐", ["vs Singer"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.5 mph EV. Singer LHB split +0.64, HR risk 0.52.""", blast="good"),
            row("Petey Halpin", "L", "+525", 67, "", ["vs Singer"], """0 HR, 90.0 mph EV. Singer LHB split +0.64, HR risk 0.52. limited recent HR events."""),
            row("Rhys Hoskins", "R", "N/A", 79, "⭐ 🌕 💣", ["vs Singer"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.8 mph EV. Singer RHB split -0.42, HR risk 0.52. tough split lane (-0.42).""", blast="high"),
            row("Gabriel Arias", "R", "N/A", 80, "🌕 💣", ["vs Singer"], """2 HR, 2 near-HR, 92.7 mph EV. Singer RHB split -0.42, HR risk 0.52. tough split lane (-0.42).""", blast="high"),
        ],
    },
    {
        "title": "COL @ SD - Gabriel Hughes (R, COL) vs Griffin Canning (R, SD)",
        "description": "Tail key data: Park boost +5% (stadium -5%, weather +10%). Hughes (HR risk -1.72, vs LHB -1.31, vs RHB -0.72). Canning (HR risk 0.58, vs LHB +0.95, vs RHB -0.15).",
        "rows": [
            row("Ty France", "R", "+537", 58, "", ["vs Hughes"], """1 HR, 1 near-HR, 97.6 mph EV. Hughes RHB split -0.72, HR risk -1.72. tough split lane (-0.72); pitcher suppresses HR (-1.72).""", blast="good"),
            row("Manny Machado", "R", "+381", 58, "", ["vs Hughes"], """1 HR, 1 near-HR, 88.5 mph EV. Hughes RHB split -0.72, HR risk -1.72. tough split lane (-0.72); pitcher suppresses HR (-1.72).""", blast="good"),
            row("Luis Rengifo", "S", "+1080", 58, "", ["vs Hughes"], """1 HR, 1 near-HR, 91.5 mph EV. Hughes SHB→RHB split -0.72, HR risk -1.72. tough split lane (-0.72); pitcher suppresses HR (-1.72).""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+450", 58, "", ["vs Hughes"], """0 HR, 98.7 mph EV. Hughes RHB split -0.72, HR risk -1.72. tough split lane (-0.72); pitcher suppresses HR (-1.72).""", blast="good"),
            row("Hunter Goodman", "R", "+304", 83, "⭐ 🌕 💣", ["vs Canning"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 89.2 mph EV. Canning RHB split -0.15, HR risk 0.58. slight split headwind (-0.15).""", blast="high"),
            row("Willi Castro", "S", "N/A", 91, "🌕 💣 💎", ["vs Canning"], """Worst Pickz Hidden Gem. 3 HR, 5 near-HR, 88.5 mph EV. Canning SHB→LHB split +0.95, HR risk 0.58.""", blast="high"),
            row("Mickey Moniak", "L", "+360", 88, "🌕 💣 💎", ["vs Canning"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 92.6 mph EV. Canning LHB split +0.95, HR risk 0.58.""", blast="high"),
        ],
    },
    {
        "title": "HOU @ LAA - Hayden Wesneski 🧤 (R, HOU) vs Grayson Rodriguez 🧤 (R, LAA)",
        "description": "Tail key data: Park boost -7% (stadium -10%, weather +3%). Wesneski 🧤 (HR risk 1.22, vs LHB +0.06, vs RHB +1.63). Rodriguez 🧤 (HR risk 0.95, vs LHB +0.45, vs RHB +1.03).",
        "rows": [
            row("Jorge Soler", "R", "+394", 84, "💎", ["vs Wesneski"], """Worst Pickz Hidden Gem. 0 HR, 93.3 mph EV. Wesneski RHB split +1.63, HR risk 1.22. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
            row("Jo Adell", "R", "+445", 77, "💎", ["vs Wesneski"], """Worst Pickz Hidden Gem. 0 HR, 90.5 mph EV. Wesneski RHB split +1.63, HR risk 1.22. park/weather net drag (-7%); limited recent HR events."""),
            row("Vaughn Grissom", "R", "+760", 88, "🌕 💣", ["vs Wesneski"], """1 HR, 2 near-HR, 90.9 mph EV. Wesneski RHB split +1.63, HR risk 1.22. park/weather net drag (-7%).""", blast="good"),
            row("Yordan Alvarez", "L", "+190", 61, "", ["vs Rodriguez"], """1 HR, 1 near-HR, 92.4 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; park/weather net drag (-7%).""", blast="good"),
            row("Taylor Trammell", "L", "N/A", 72, "🌕 💣", ["vs Rodriguez"], """2 HR, 3 near-HR, 89.4 mph EV. Rodriguez split/risk data unavailable. limited split/risk sample; park/weather net drag (-7%).""", blast="high"),
        ],
    },
    {
        "title": "KC @ MIN - Randy Dobnak (R, KC) vs Joe Ryan 🧤 (R, MIN)",
        "description": "Tail key data: Park boost -8% (stadium -6%, weather -2%). Dobnak (HR risk -0.29, vs LHB -0.61, vs RHB +0.87). Ryan 🧤 (HR risk 1.48, vs LHB +1.20, vs RHB +0.62).",
        "rows": [
            row("Ryan Jeffers", "R", "+500", 82, "🌕 💣 💎", ["vs Dobnak"], """Worst Pickz Hidden Gem. 4 HR, 4 near-HR, 94.1 mph EV. Dobnak RHB split +0.87, HR risk -0.29. pitcher risk below avg (-0.29); park/weather net drag (-8%).""", blast="high"),
            row("Kody Clemens", "L", "+375", 58, "", ["vs Dobnak"], """0 HR, 2 near-HR, 93.2 mph EV. Dobnak LHB split -0.61, HR risk -0.29. tough split lane (-0.61); pitcher risk below avg (-0.29).""", blast="good"),
            row("Royce Lewis", "R", "+450", 71, "🌕 💣", ["vs Dobnak"], """2 HR, 2 near-HR, 90.7 mph EV. Dobnak RHB split +0.87, HR risk -0.29. pitcher risk below avg (-0.29); park/weather net drag (-8%).""", blast="high"),
            row("Jac Caglianone", "L", "+390", 90, "⭐ 🌕 💣", ["vs Ryan"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.6 mph EV. Ryan LHB split +1.20, HR risk 1.48. park/weather net drag (-8%).""", blast="good"),
            row("Vinnie Pasquantino", "L", "+480", 82, "", ["vs Ryan"], """0 HR, 93.0 mph EV. Ryan LHB split +1.20, HR risk 1.48. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Salvador Perez", "R", "+480", 95, "🌕 💣", ["vs Ryan"], """3 HR, 3 near-HR, 96.7 mph EV. Ryan RHB split +0.62, HR risk 1.48. park/weather net drag (-8%).""", blast="high"),
            row("Carter Jensen", "L", "+475", 90, "🌕 💣 💎", ["vs Ryan"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 94.8 mph EV. Ryan LHB split +1.20, HR risk 1.48. park/weather net drag (-8%).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ SF - Shane Drohan (L, MIL) vs Logan Webb (R, SF)",
        "description": "Tail key data: Park boost -8% (stadium -19%, weather +10%). Drohan (HR risk -0.47, vs LHB -0.51, vs RHB -0.11). Webb (HR risk -0.46, vs LHB -0.36, vs RHB -0.29).",
        "rows": [
            row("Rafael Devers", "L", "+473", 58, "⭐", ["vs Drohan"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.4 mph EV. Drohan LHB split -0.51, HR risk -0.47. tough split lane (-0.51); pitcher suppresses HR (-0.47).""", blast="good"),
            row("Heliot Ramos", "R", "+501", 58, "", ["vs Drohan"], """1 HR, 1 near-HR, 96.7 mph EV. Drohan RHB split -0.11, HR risk -0.47. slight split headwind (-0.11); pitcher suppresses HR (-0.47).""", blast="good"),
            row("Bryce Eldridge", "L", "+670", 58, "", ["vs Drohan"], """0 HR, 94.1 mph EV. Drohan LHB split -0.51, HR risk -0.47. tough split lane (-0.51); pitcher suppresses HR (-0.47).""", blast="good"),
            row("Luis Lara", "S", "+1500", 58, "", ["vs Webb"], """0 HR, 91.2 mph EV. Webb SHB→RHB split -0.29, HR risk -0.46. slight split headwind (-0.29); pitcher suppresses HR (-0.46)."""),
            row("Jake Bauers", "L", "+650", 58, "", ["vs Webb"], """0 HR, 96.4 mph EV. Webb LHB split -0.36, HR risk -0.46. slight split headwind (-0.36); pitcher suppresses HR (-0.46).""", blast="good"),
            row("Garrett Mitchell", "L", "+875", 58, "", ["vs Webb"], """0 HR, 93.6 mph EV. Webb LHB split -0.36, HR risk -0.46. slight split headwind (-0.36); pitcher suppresses HR (-0.46).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ CWS - Cam Schlittler (R, NYY) vs Davis Martin (R, CWS)",
        "description": "Tail key data: Park boost -3% (stadium -5%, weather +2%). Schlittler (HR risk 0.56, vs LHB +0.41, vs RHB +0.34). Martin (HR risk -0.98, vs LHB -0.62, vs RHB -0.63).",
        "rows": [
            row("Munetaka Murakami", "L", "+317", 88, "🌕 💣 💎", ["vs Schlittler"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 95.1 mph EV. Schlittler LHB split +0.41, HR risk 0.56.""", blast="high"),
            row("Miguel Vargas", "R", "+450", 70, "", ["vs Schlittler"], """1 HR, 1 near-HR, 91.9 mph EV. Schlittler RHB split +0.34, HR risk 0.56.""", blast="good"),
            row("Ben Rice", "L", "+332", 58, "⭐", ["vs Martin"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.4 mph EV. Martin LHB split -0.62, HR risk -0.98. tough split lane (-0.62); pitcher suppresses HR (-0.98).""", blast="good"),
            row("Ryan McMahon", "L", "+550", 58, "", ["vs Martin"], """1 HR, 2 near-HR, 95.7 mph EV. Martin LHB split -0.62, HR risk -0.98. tough split lane (-0.62); pitcher suppresses HR (-0.98).""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "+438", 58, "🌕 💣 💎", ["vs Martin"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.5 mph EV. Martin LHB split -0.62, HR risk -0.98. tough split lane (-0.62); pitcher suppresses HR (-0.98).""", blast="high"),
            row("Spencer Jones", "L", "+630", 58, "💎", ["vs Martin"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.0 mph EV. Martin LHB split -0.62, HR risk -0.98. tough split lane (-0.62); pitcher suppresses HR (-0.98).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ MIA - Jesus Luzardo (L, PHI) vs Ryan Gusto (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -13%, weather +0%). Luzardo (HR risk -0.75, vs LHB -1.11, vs RHB -0.28). Gusto (HR risk -0.26, vs LHB +0.32, vs RHB -0.79).",
        "rows": [
            row("Heriberto Hernandez", "R", "+540", 68, "🌕 💣 💎", ["vs Luzardo"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 93.9 mph EV. Luzardo RHB split -0.28, HR risk -0.75. slight split headwind (-0.28); pitcher suppresses HR (-0.75).""", blast="high"),
            row("Esteury Ruiz", "R", "+1020", 58, "🌕 💣", ["vs Luzardo"], """2 HR, 3 near-HR, 77.9 mph EV. Luzardo RHB split -0.28, HR risk -0.75. slight split headwind (-0.28); pitcher suppresses HR (-0.75).""", blast="high"),
            row("Otto Lopez", "R", "+900", 58, "", ["vs Luzardo"], """0 HR, 1 near-HR, 90.8 mph EV. Luzardo RHB split -0.28, HR risk -0.75. slight split headwind (-0.28); pitcher suppresses HR (-0.75)."""),
            row("Brian Navarreto", "R", "+735", 58, "", ["vs Luzardo"], """0 HR, 91.5 mph EV. Luzardo RHB split -0.28, HR risk -0.75. slight split headwind (-0.28); pitcher suppresses HR (-0.75)."""),
            row("Bryce Harper", "L", "+411", 63, "", ["vs Gusto"], """1 HR, 2 near-HR, 98.6 mph EV. Gusto LHB split +0.32, HR risk -0.26. pitcher risk below avg (-0.26); park/weather net drag (-13%).""", blast="good"),
            row("Derek Hill", "R", "N/A", 63, "🌕 💣", ["vs Gusto"], """2 HR, 2 near-HR, 96.0 mph EV. Gusto RHB split -0.79, HR risk -0.26. tough split lane (-0.79); pitcher risk below avg (-0.26).""", blast="high"),
            row("Bryson Stott", "L", "+540", 61, "", ["vs Gusto"], """1 HR, 2 near-HR, 93.9 mph EV. Gusto LHB split +0.32, HR risk -0.26. pitcher risk below avg (-0.26); park/weather net drag (-13%).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ LAD - Emerson Hancock (R, SEA) vs Eric Lauer 🧤 (L, LAD)",
        "description": "Tail key data: Park boost +15% (stadium +16%, weather -1%). Hancock (HR risk 0.03, vs LHB +0.34, vs RHB -0.49). Lauer 🧤 (HR risk 1.05, vs LHB -0.04, vs RHB +1.16).",
        "rows": [
            row("Kyle Tucker", "L", "+560", 70, "⭐", ["vs Hancock"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 92.8 mph EV. Hancock LHB split +0.34, HR risk 0.03.""", blast="good"),
            row("Max Muncy", "L", "+306", 68, "", ["vs Hancock"], """1 HR, 1 near-HR, 92.7 mph EV. Hancock LHB split +0.34, HR risk 0.03.""", blast="good"),
            row("Shohei Ohtani", "L", "+215", 66, "", ["vs Hancock"], """0 HR, 99.6 mph EV. Hancock LHB split +0.34, HR risk 0.03. limited recent HR events.""", blast="good"),
            row("Dalton Rushing", "L", "+401", 69, "💎", ["vs Hancock"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.6 mph EV. Hancock LHB split +0.34, HR risk 0.03.""", blast="good"),
            row("Dominic Canzone", "L", "+373", 94, "⭐ 🌕 💣", ["vs Lauer"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 96.2 mph EV. Lauer LHB split -0.04, HR risk 1.05. slight split headwind (-0.04).""", blast="high"),
            row("Cal Raleigh", "S", "+270", 91, "⭐ 🌕 💣", ["vs Lauer"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.3 mph EV. Lauer SHB→RHB split +1.16, HR risk 1.05.""", blast="good"),
            row("Josh Naylor", "L", "+587", 74, "", ["vs Lauer"], """0 HR, 93.0 mph EV. Lauer LHB split -0.04, HR risk 1.05. slight split headwind (-0.04); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TEX @ TB - MacKenzie Gore (L, TEX) vs Casey Legumina (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -3%, weather +1%). Gore (HR risk 0.89, vs LHB +0.15, vs RHB +0.96). Legumina (HR risk 0.06, vs LHB +0.47, vs RHB -0.55).",
        "rows": [
            row("Jonathan Aranda", "L", "+584", 70, "", ["vs Gore"], """0 HR, 96.9 mph EV. Gore LHB split +0.15, HR risk 0.89. limited recent HR events.""", blast="good"),
            row("Victor Mesa Jr.", "L", "N/A", 73, "", ["vs Gore"], """1 HR, 1 near-HR, 92.8 mph EV. Gore LHB split +0.15, HR risk 0.89.""", blast="good"),
            row("Jake Burger", "R", "+384", 58, "", ["vs Legumina"], """1 HR, 1 near-HR, 88.7 mph EV. Legumina RHB split -0.55, HR risk 0.06. tough split lane (-0.55).""", blast="good"),
            row("Ezequiel Duran", "R", "+780", 58, "", ["vs Legumina"], """1 HR, 1 near-HR, 81.8 mph EV. Legumina RHB split -0.55, HR risk 0.06. tough split lane (-0.55); lighter EV form (81.8 mph).""", blast="good"),
            row("Wyatt Langford", "R", "+416", 58, "", ["vs Legumina"], """0 HR, 90.2 mph EV. Legumina RHB split -0.55, HR risk 0.06. tough split lane (-0.55); limited recent HR events."""),
            row("Joc Pederson", "L", "N/A", 61, "⭐", ["vs Legumina"], """Worst Pickz Favorite. 0 HR, 94.5 mph EV. Legumina LHB split +0.47, HR risk 0.06. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TOR @ WSH - Trey Yesavage (R, TOR) vs Zack Littell 🧤 (R, WSH)",
        "description": "Tail key data: Park boost -2% (stadium +3%, weather -5%). Yesavage (HR risk 0.42, vs LHB +0.10, vs RHB +0.47). Littell 🧤 (HR risk 1.14, vs LHB +0.82, vs RHB +0.64).",
        "rows": [
            row("James Wood", "L", "+320", 81, "⭐ 🌕 💣", ["vs Yesavage"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.0 mph EV. Yesavage LHB split +0.10, HR risk 0.42. weather carry headwind (-5%).""", blast="high"),
            row("Luis Garcia Jr.", "L", "+448", 58, "", ["vs Yesavage"], """0 HR, 1 near-HR, 88.5 mph EV. Yesavage LHB split +0.10, HR risk 0.42. weather carry headwind (-5%); limited recent HR events."""),
            row("Dylan Crews", "R", "+548", 72, "💎", ["vs Yesavage"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.4 mph EV. Yesavage RHB split +0.47, HR risk 0.42. weather carry headwind (-5%).""", blast="good"),
            row("CJ Abrams", "L", "+430", 67, "", ["vs Yesavage"], """1 HR, 1 near-HR, 91.5 mph EV. Yesavage LHB split +0.10, HR risk 0.42. weather carry headwind (-5%).""", blast="good"),
            row("Brandon Valenzuela", "S", "N/A", 77, "", ["vs Littell"], """1 HR, 2 near-HR, 85.4 mph EV. Littell SHB→LHB split +0.82, HR risk 1.14. weather carry headwind (-5%); lighter EV form (85.4 mph).""", blast="good"),
            row("Daulton Varsho", "L", "+425", 81, "", ["vs Littell"], """0 HR, 2 near-HR, 93.2 mph EV. Littell LHB split +0.82, HR risk 1.14. weather carry headwind (-5%).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-29")

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

    out = ROOT / '_games-0729.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
