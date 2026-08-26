#!/usr/bin/env python3
"""Generate games[] block for 2026-08-26 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Austin Riley (R)",
    "Brandon Lowe (L)",
    "Brett Baty (L)",
    "Bryan Reynolds (S)",
    "Bryce Harper (L)",
    "Cal Raleigh (S)",
    "Cody Bellinger (L)",
    "Corbin Carroll (L)",
    "Drake Baldwin (L)",
    "Eduardo Valencia (R)",
    "Esmerlyn Valdez (R)",
    "Hunter Feduccia (L)",
    "JJ Wetherholt (L)",
    "Jac Caglianone (L)",
    "Jackson Merrill (L)",
    "Jake Bauers (L)",
    "Jo Adell (R)",
    "Luis Garcia Jr. (L)",
    "Luis Robert (R)",
    "Matt Olson (L)",
    "Michael Harris II (L)",
    "Miguel Amaya (R)",
    "Miguel Vargas (R)",
    "Munetaka Murakami (L)",
    "Oneil Cruz (L)",
    "Pete Alonso (R)",
    "Randal Grichuk (R)",
    "Shohei Ohtani (L)",
    "Spencer Jones (L)",
    "William Contreras (R)",
    "Zach Neto (R)",
}

GEMS = {
    "Carter Jensen (L)",
    "Colson Montgomery (L)",
    "Corey Seager (L)",
    "Daylen Lile (L)",
    "Dylan Beavers (L)",
    "Jackson Chourio (R)",
    "Jake Burger (R)",
    "Jake Rogers (R)",
    "Jesus Sanchez (L)",
    "Jimmy Crooks (L)",
    "Joey Ortiz (R)",
    "Jonah Cox (R)",
    "Josh Bell (S)",
    "Kody Clemens (L)",
    "Lawrence Butler (L)",
    "Luis Torrens (R)",
    "Max Muncy (L)",
    "Michael Busch (L)",
    "Mickey Gasper (S)",
    "Mickey Moniak (L)",
    "Pete Crow Armstrong (L)",
    "Ronald Acuna Jr. (R)",
    "Trent Grisham (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BOS",
    "Alec Burleson (L)": "STL",
    "Andres Chaparro (R)": "WSH",
    "Andrew Pinckney (R)": "WSH",
    "Andrew Vaughn (R)": "MIL",
    "Austin Riley (R)": "ATL",
    "Brady House (R)": "WSH",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Brett Baty (L)": "NYM",
    "Brett Sullivan (L)": "COL",
    "Brewer Hicklen (R)": "ATL",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Harper (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Carter Jensen (L)": "KC",
    "Chase DeLauter (L)": "CLE",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Coby Mayo (R)": "BAL",
    "Cody Bellinger (L)": "NYY",
    "Colson Montgomery (L)": "CWS",
    "Colt Keith (L)": "DET",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Daylen Lile (L)": "WSH",
    "Drake Baldwin (L)": "ATL",
    "Dylan Beavers (L)": "BAL",
    "Eduardo Valencia (R)": "DET",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Gavin Sheets (L)": "SD",
    "Griffin Conine (L)": "MIA",
    "Hao Yu Lee (R)": "DET",
    "Hunter Feduccia (L)": "LAD",
    "Hunter Goodman (R)": "COL",
    "Ivan Herrera (R)": "STL",
    "JJ Wetherholt (L)": "STL",
    "JT Realmuto (R)": "PHI",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jake Rogers (R)": "CWS",
    "Jakob Marsee (L)": "MIA",
    "Jarren Duran (L)": "BOS",
    "Jeff McNeil (L)": "ATH",
    "Jeremy Pena (R)": "HOU",
    "Jesus Sanchez (L)": "TOR",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "CLE",
    "Joc Pederson (L)": "TEX",
    "Joey Ortiz (R)": "MIL",
    "Jonah Cox (R)": "SF",
    "Jonah Heim (S)": "ATH",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Jose Siri (R)": "LAA",
    "Josh Bell (S)": "MIN",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kazuma Okamoto (R)": "TOR",
    "Kevin McGonigle (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Kyle Isbel (L)": "KC",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Tucker (L)": "LAD",
    "Lawrence Butler (L)": "ATH",
    "Luis Garcia Jr. (L)": "NYY",
    "Luis Robert (R)": "NYM",
    "Luis Torrens (R)": "NYM",
    "Luke Keaschall (R)": "MIN",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Michael Busch (L)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Mickey Gasper (S)": "BOS",
    "Mickey Moniak (L)": "COL",
    "Miguel Amaya (R)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Mike Yastrzemski (L)": "ATL",
    "Munetaka Murakami (L)": "CWS",
    "Nathan Lukes (L)": "TOR",
    "Nathaniel Lowe (L)": "CLE",
    "Nelson Velazquez (R)": "HOU",
    "Nick Allen (R)": "HOU",
    "Oneil Cruz (L)": "PIT",
    "Owen Caissie (L)": "MIA",
    "Patrick Wisdom (R)": "SEA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Rafael Flores (R)": "PIT",
    "Randal Grichuk (R)": "CWS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Taylor Trammell (L)": "HOU",
    "Tim Tawa (R)": "ARI",
    "Tommy White (R)": "ATH",
    "Trent Grisham (L)": "NYY",
    "Troy Johnston (L)": "COL",
    "Tyler Stephenson (R)": "CIN",
    "Willi Castro (S)": "COL",
    "William Contreras (R)": "MIL",
    "Xander Bogaerts (R)": "SD",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("BOS @ MIA", "Gusto"),
    ("CHC @ ARI", "Boyd"),
    ("CIN @ SF", "Lodolo"),
    ("COL @ WSH", "Gordon"),
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
        "title": "BAL @ STL - Kyle Bradish (R, BAL) vs Michael McGreevy (R, STL)",
        "description": "Tail key data: Park boost -7% (stadium -8%, weather +1%). Bradish (HR risk 0.07, vs LHB +0.33, vs RHB +0.04). McGreevy (HR risk 0.48, vs LHB +1.52, vs RHB -0.66).",
        "rows": [
            row("Jordan Walker", "R", "+573", 59, "", ["vs Bradish"], """1 HR, 1 near-HR, 91.2 mph EV. Bradish RHB split +0.04, HR risk 0.07. park/weather net drag (-7%).""", blast="good"),
            row("JJ Wetherholt", "L", "+850", 62, "⭐", ["vs Bradish"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 97.9 mph EV. Bradish LHB split +0.33, HR risk 0.07. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
            row("Jimmy Crooks", "L", "+1260", 62, "💎", ["vs Bradish"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.5 mph EV. Bradish LHB split +0.33, HR risk 0.07. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
            row("Alec Burleson", "L", "+600", 58, "", ["vs Bradish"], """0 HR, 1 near-HR, 91.4 mph EV. Bradish LHB split +0.33, HR risk 0.07. park/weather net drag (-7%); limited recent HR events."""),
            row("Ivan Herrera", "R", "+900", 63, "", ["vs Bradish"], """1 HR, 2 near-HR, 93.8 mph EV. Bradish RHB split +0.04, HR risk 0.07. park/weather net drag (-7%).""", blast="good"),
            row("Dylan Beavers", "L", "+810", 91, "🌕 💣 💎", ["vs McGreevy"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 91.8 mph EV. McGreevy LHB split +1.52, HR risk 0.48. park/weather net drag (-7%).""", blast="high"),
            row("Pete Alonso", "R", "+413", 75, "⭐ 🌕 💣", ["vs McGreevy"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.1 mph EV. McGreevy RHB split -0.66, HR risk 0.48. tough split lane (-0.66); park/weather net drag (-7%).""", blast="high"),
            row("Coby Mayo", "R", "+466", 59, "", ["vs McGreevy"], """0 HR, 1 near-HR, 94.0 mph EV. McGreevy RHB split -0.66, HR risk 0.48. tough split lane (-0.66); park/weather net drag (-7%).""", blast="good"),
            row("Christian Encarnacion-Strand", "R", "+550", 62, "", ["vs McGreevy"], """1 HR, 1 near-HR, 93.0 mph EV. McGreevy RHB split -0.66, HR risk 0.48. tough split lane (-0.66); park/weather net drag (-7%).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ MIA - Sonny Gray (R, BOS) vs Ryan Gusto 🧤 (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -13%, weather +0%). Gray (HR risk -0.27, vs LHB -0.28, vs RHB +0.21). Gusto 🧤 (HR risk 1.00, vs LHB +0.18, vs RHB +1.43).",
        "rows": [
            row("Griffin Conine", "L", "+534", 71, "🌕 💣", ["vs Gray"], """2 HR, 3 near-HR, 99.3 mph EV. Gray LHB split -0.28, HR risk -0.27. slight split headwind (-0.28); pitcher risk below avg (-0.27).""", blast="high"),
            row("Owen Caissie", "L", "+830", 58, "", ["vs Gray"], """1 HR, 1 near-HR, 93.0 mph EV. Gray LHB split -0.28, HR risk -0.27. slight split headwind (-0.28); pitcher risk below avg (-0.27).""", blast="good"),
            row("Jakob Marsee", "L", "+1080", 58, "", ["vs Gray"], """0 HR, 93.0 mph EV. Gray LHB split -0.28, HR risk -0.27. slight split headwind (-0.28); pitcher risk below avg (-0.27).""", blast="good"),
            row("Mickey Gasper", "S", "+830", 94, "🌕 💣 💎", ["vs Gusto"], """Worst Pickz Hidden Gem. 4 HR, 4 near-HR, 90.9 mph EV. Gusto SHB→RHB split +1.43, HR risk 1.00. park/weather net drag (-13%).""", blast="high"),
            row("Jarren Duran", "L", "+750", 70, "", ["vs Gusto"], """1 HR, 1 near-HR, 89.8 mph EV. Gusto LHB split +0.18, HR risk 1.00. park/weather net drag (-13%).""", blast="good"),
            row("Adley Rutschman", "S", "+760", 77, "", ["vs Gusto"], """1 HR, 1 near-HR, 85.7 mph EV. Gusto SHB→RHB split +1.43, HR risk 1.00. park/weather net drag (-13%); lighter EV form (85.7 mph).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ ARI - Matthew Boyd 🧤 (L, CHC) vs Eduardo Rodriguez (L, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Boyd 🧤 (HR risk 1.07, vs LHB -1.17, vs RHB +1.45). Rodriguez (HR risk -0.79, vs LHB -0.72, vs RHB -0.41).",
        "rows": [
            row("Corbin Carroll", "L", "+610", 73, "⭐", ["vs Boyd"], """Worst Pickz Favorite. 0 HR, 3 near-HR, 94.8 mph EV. Boyd LHB split -1.17, HR risk 1.07. tough split lane (-1.17); park/weather net drag (-8%).""", blast="good"),
            row("Tim Tawa", "R", "+750", 79, "", ["vs Boyd"], """0 HR, 92.0 mph EV. Boyd RHB split +1.45, HR risk 1.07. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Pete Crow Armstrong", "L", "+485", 66, "🌕 💣 💎", ["vs Eduardo Rodriguez"], """Worst Pickz Hidden Gem. 3 HR, 4 near-HR, 94.3 mph EV. Eduardo Rodriguez LHB split -0.72, HR risk -0.79. tough split lane (-0.72); pitcher suppresses HR (-0.79).""", blast="high"),
            row("Michael Busch", "L", "+790", 62, "🌕 💣 💎", ["vs Eduardo Rodriguez"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 94.1 mph EV. Eduardo Rodriguez LHB split -0.72, HR risk -0.79. tough split lane (-0.72); pitcher suppresses HR (-0.79).""", blast="high"),
            row("Miguel Amaya", "R", "N/A", 58, "⭐", ["vs Eduardo Rodriguez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 89.2 mph EV. Eduardo Rodriguez RHB split -0.41, HR risk -0.79. tough split lane (-0.41); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Michael Conforto", "L", "N/A", 58, "", ["vs Eduardo Rodriguez"], """1 HR, 1 near-HR, 96.6 mph EV. Eduardo Rodriguez LHB split -0.72, HR risk -0.79. tough split lane (-0.72); pitcher suppresses HR (-0.79).""", blast="good"),
        ],
    },
    {
        "title": "CIN @ SF - Nick Lodolo 🧤 (L, CIN) vs Landen Roupp (R, SF)",
        "description": "Tail key data: Park boost -13% (stadium -15%, weather +2%). Lodolo 🧤 (HR risk 1.18, vs LHB -1.25, vs RHB +1.18). Roupp (HR risk -0.76, vs LHB -0.25, vs RHB -0.84).",
        "rows": [
            row("Rafael Devers", "L", "+600", 58, "", ["vs Lodolo"], """0 HR, 90.6 mph EV. Lodolo LHB split -1.25, HR risk 1.18. tough split lane (-1.25); park/weather net drag (-13%)."""),
            row("Jonah Cox", "R", "+909", 82, "💎", ["vs Lodolo"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 84.3 mph EV. Lodolo RHB split +1.18, HR risk 1.18. park/weather net drag (-13%); lighter EV form (84.3 mph).""", blast="good"),
            row("Sal Stewart", "R", "+800", 58, "", ["vs Roupp"], """1 HR, 1 near-HR, 89.9 mph EV. Roupp RHB split -0.84, HR risk -0.76. tough split lane (-0.84); pitcher suppresses HR (-0.76).""", blast="good"),
            row("Eugenio Suarez", "R", "+610", 58, "", ["vs Roupp"], """0 HR, 92.4 mph EV. Roupp RHB split -0.84, HR risk -0.76. tough split lane (-0.84); pitcher suppresses HR (-0.76).""", blast="good"),
            row("Tyler Stephenson", "R", "+870", 58, "", ["vs Roupp"], """0 HR, 91.3 mph EV. Roupp RHB split -0.84, HR risk -0.76. tough split lane (-0.84); pitcher suppresses HR (-0.76)."""),
        ],
    },
    {
        "title": "CLE @ LAA - Joey Cantillo (L, CLE) vs Grayson Rodriguez (R, LAA)",
        "description": "Tail key data: Park boost +2% (stadium -9%, weather +11%). Cantillo (HR risk 0.47, vs LHB +0.11, vs RHB +0.44). Rodriguez (HR risk 0.42, vs LHB +0.07, vs RHB +0.59).",
        "rows": [
            row("Zach Neto", "R", "+430", 72, "⭐", ["vs Cantillo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.2 mph EV. Cantillo RHB split +0.44, HR risk 0.47. park suppresses carry (-9%).""", blast="good"),
            row("Jose Siri", "R", "+500", 68, "", ["vs Cantillo"], """0 HR, 1 near-HR, 92.2 mph EV. Cantillo RHB split +0.44, HR risk 0.47. park suppresses carry (-9%); limited recent HR events.""", blast="good"),
            row("Jo Adell", "R", "+400", 71, "⭐", ["vs Grayson Rodriguez"], """Worst Pickz Favorite. 0 HR, 98.0 mph EV. Grayson Rodriguez RHB split +0.59, HR risk 0.42. park suppresses carry (-9%); limited recent HR events.""", blast="good"),
            row("Chase DeLauter", "L", "N/A", 64, "", ["vs Grayson Rodriguez"], """0 HR, 93.5 mph EV. Grayson Rodriguez LHB split +0.07, HR risk 0.42. park suppresses carry (-9%); limited recent HR events.""", blast="good"),
            row("Nathaniel Lowe", "L", "+500", 58, "", ["vs Grayson Rodriguez"], """0 HR, 89.7 mph EV. Grayson Rodriguez LHB split +0.07, HR risk 0.42. park suppresses carry (-9%); limited recent HR events."""),
        ],
    },
    {
        "title": "COL @ WSH - Tanner Gordon 🧤 (R, COL) vs Matt Waldron (R, WSH)",
        "description": "Tail key data: Park boost +11% (stadium +3%, weather +8%). Gordon 🧤 (HR risk 1.18, vs LHB +1.41, vs RHB +0.57). Waldron (HR risk 0.05, vs LHB +0.88, vs RHB -0.13).",
        "rows": [
            row("Daylen Lile", "L", "+460", 87, "💎", ["vs Gordon"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 88.5 mph EV. Gordon LHB split +1.41, HR risk 1.18.""", blast="good"),
            row("Andres Chaparro", "R", "N/A", 92, "🌕 💣", ["vs Gordon"], """3 HR, 3 near-HR, 87.3 mph EV. Gordon RHB split +0.57, HR risk 1.18. lighter EV form (87.3 mph).""", blast="high"),
            row("Brady House", "R", "+480", 89, "🌕 💣", ["vs Gordon"], """0 HR, 3 near-HR, 99.8 mph EV. Gordon RHB split +0.57, HR risk 1.18.""", blast="good"),
            row("Andrew Pinckney", "R", "N/A", 73, "", ["vs Gordon"], """0 HR, 90.9 mph EV. Gordon RHB split +0.57, HR risk 1.18. limited recent HR events."""),
            row("Willi Castro", "S", "+557", 75, "", ["vs Waldron"], """1 HR, 1 near-HR, 96.1 mph EV. Waldron SHB→LHB split +0.88, HR risk 0.05.""", blast="good"),
            row("Brett Sullivan", "L", "N/A", 74, "", ["vs Waldron"], """1 HR, 2 near-HR, 93.3 mph EV. Waldron LHB split +0.88, HR risk 0.05.""", blast="good"),
            row("Mickey Moniak", "L", "+349", 75, "💎", ["vs Waldron"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.3 mph EV. Waldron LHB split +0.88, HR risk 0.05.""", blast="good"),
            row("Hunter Goodman", "R", "+289", 67, "", ["vs Waldron"], """1 HR, 3 near-HR, 90.3 mph EV. Waldron RHB split -0.13, HR risk 0.05. slight split headwind (-0.13).""", blast="good"),
            row("Troy Johnston", "L", "+870", 67, "", ["vs Waldron"], """0 HR, 93.6 mph EV. Waldron LHB split +0.88, HR risk 0.05. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "HOU @ NYY - Peter Lambert (R, HOU) vs Elmer Rodriguez (R, NYY)",
        "description": "Tail key data: Park boost +10% (stadium +4%, weather +6%). Lambert (HR risk -0.57, vs LHB -0.25, vs RHB -0.39). Rodriguez.",
        "rows": [
            row("Luis Garcia Jr.", "L", "N/A", 69, "🚀 ⭐ 🌕 💣", ["vs Lambert"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.8 mph EV. Lambert LHB split -0.25, HR risk -0.57. slight split headwind (-0.25); pitcher suppresses HR (-0.57).""", blast="high"),
            row("Spencer Jones", "L", "+520", 60, "⭐", ["vs Lambert"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.8 mph EV. Lambert LHB split -0.25, HR risk -0.57. slight split headwind (-0.25); pitcher suppresses HR (-0.57).""", blast="good"),
            row("Trent Grisham", "L", "+350", 64, "🌕 💣 💎", ["vs Lambert"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 90.6 mph EV. Lambert LHB split -0.25, HR risk -0.57. slight split headwind (-0.25); pitcher suppresses HR (-0.57).""", blast="high"),
            row("Cody Bellinger", "L", "+520", 59, "⭐", ["vs Lambert"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.6 mph EV. Lambert LHB split -0.25, HR risk -0.57. slight split headwind (-0.25); pitcher suppresses HR (-0.57).""", blast="good"),
            row("Jeremy Pena", "R", "N/A", 80, "🌕 💣", ["vs Elmer Rodriguez"], """2 HR, 3 near-HR, 92.5 mph EV. limited split/risk sample.""", blast="high"),
            row("Nick Allen", "R", "N/A", 67, "", ["vs Elmer Rodriguez"], """1 HR, 1 near-HR, 93.9 mph EV. limited split/risk sample.""", blast="good"),
            row("Taylor Trammell", "L", "N/A", 61, "", ["vs Elmer Rodriguez"], """0 HR, 1 near-HR, 92.0 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Yordan Alvarez", "L", "N/A", 64, "🚀", ["vs Elmer Rodriguez"], """0 HR, 100.7 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 63, "", ["vs Elmer Rodriguez"], """0 HR, 1 near-HR, 93.9 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "KC @ TOR - Randy Dobnak (R, KC) vs Spencer Miles (R, TOR)",
        "description": "Tail key data: Park boost +16% (stadium +7%, weather +9%). Dobnak (HR risk -1.55, vs LHB -1.18, vs RHB -1.15). Miles (HR risk -1.27, vs LHB -0.03, vs RHB -1.70).",
        "rows": [
            row("Jesus Sanchez", "L", "+630", 58, "💎", ["vs Dobnak"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.1 mph EV. Dobnak LHB split -1.18, HR risk -1.55. tough split lane (-1.18); pitcher suppresses HR (-1.55).""", blast="good"),
            row("Kazuma Okamoto", "R", "+397", 58, "", ["vs Dobnak"], """0 HR, 89.1 mph EV. Dobnak RHB split -1.15, HR risk -1.55. tough split lane (-1.15); pitcher suppresses HR (-1.55)."""),
            row("Nathan Lukes", "L", "+900", 58, "", ["vs Dobnak"], """1 HR, 1 near-HR, 91.3 mph EV. Dobnak LHB split -1.18, HR risk -1.55. tough split lane (-1.18); pitcher suppresses HR (-1.55).""", blast="good"),
            row("Jac Caglianone", "L", "+340", 58, "🚀 ⭐", ["vs Miles"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 100.7 mph EV. Miles LHB split -0.03, HR risk -1.27. slight split headwind (-0.03); pitcher suppresses HR (-1.27).""", blast="good"),
            row("Kyle Isbel", "L", "+1200", 66, "🌕 💣", ["vs Miles"], """2 HR, 2 near-HR, 95.2 mph EV. Miles LHB split -0.03, HR risk -1.27. slight split headwind (-0.03); pitcher suppresses HR (-1.27).""", blast="high"),
            row("Salvador Perez", "R", "+481", 58, "", ["vs Miles"], """1 HR, 1 near-HR, 91.9 mph EV. Miles RHB split -1.70, HR risk -1.27. tough split lane (-1.70); pitcher suppresses HR (-1.27).""", blast="good"),
            row("Carter Jensen", "L", "+487", 58, "💎", ["vs Miles"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 90.0 mph EV. Miles LHB split -0.03, HR risk -1.27. slight split headwind (-0.03); pitcher suppresses HR (-1.27)."""),
        ],
    },
    {
        "title": "LAD @ ATL - Roki Sasaki (R, LAD) vs AJ Smith-Shawver (R, ATL)",
        "description": "Tail key data: Park boost -5% (stadium -1%, weather -4%). Sasaki (HR risk 0.22, vs LHB -0.25, vs RHB +0.92). Smith-Shawver (HR risk -1.16, vs LHB -0.66, vs RHB -0.73).",
        "rows": [
            row("Matt Olson", "L", "+351", 79, "⭐ 🌕 💣", ["vs Sasaki"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 98.5 mph EV. Sasaki LHB split -0.25, HR risk 0.22. slight split headwind (-0.25); park/weather net drag (-5%).""", blast="high"),
            row("Austin Riley", "R", "+600", 74, "⭐", ["vs Sasaki"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.2 mph EV. Sasaki RHB split +0.92, HR risk 0.22. park/weather net drag (-5%).""", blast="good"),
            row("Drake Baldwin", "L", "+484", 63, "⭐", ["vs Sasaki"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.2 mph EV. Sasaki LHB split -0.25, HR risk 0.22. slight split headwind (-0.25); park/weather net drag (-5%).""", blast="good"),
            row("Mike Yastrzemski", "L", "+640", 63, "", ["vs Sasaki"], """1 HR, 1 near-HR, 95.4 mph EV. Sasaki LHB split -0.25, HR risk 0.22. slight split headwind (-0.25); park/weather net drag (-5%).""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+459", 64, "💎", ["vs Sasaki"], """Worst Pickz Hidden Gem. 0 HR, 92.5 mph EV. Sasaki RHB split +0.92, HR risk 0.22. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
            row("Michael Harris II", "L", "+480", 58, "⭐", ["vs Sasaki"], """Worst Pickz Favorite. 0 HR, 97.4 mph EV. Sasaki LHB split -0.25, HR risk 0.22. slight split headwind (-0.25); park/weather net drag (-5%).""", blast="good"),
            row("Brewer Hicklen", "R", "N/A", 67, "🚀", ["vs Sasaki"], """0 HR, 101.4 mph EV. Sasaki RHB split +0.92, HR risk 0.22. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
            row("Shohei Ohtani", "L", "+270", 58, "⭐", ["vs Smith-Shawver"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.4 mph EV. Smith-Shawver LHB split -0.66, HR risk -1.16. tough split lane (-0.66); pitcher suppresses HR (-1.16).""", blast="good"),
            row("Max Muncy", "L", "+375", 58, "💎", ["vs Smith-Shawver"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.4 mph EV. Smith-Shawver LHB split -0.66, HR risk -1.16. tough split lane (-0.66); pitcher suppresses HR (-1.16).""", blast="good"),
            row("Hunter Feduccia", "L", "+1050", 58, "⭐", ["vs Smith-Shawver"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.5 mph EV. Smith-Shawver LHB split -0.66, HR risk -1.16. tough split lane (-0.66); pitcher suppresses HR (-1.16).""", blast="good"),
            row("Kyle Tucker", "L", "+600", 58, "", ["vs Smith-Shawver"], """0 HR, 92.2 mph EV. Smith-Shawver LHB split -0.66, HR risk -1.16. tough split lane (-0.66); pitcher suppresses HR (-1.16).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ NYM - Dustin May (R, MIL) vs Robert Stock (R, NYM)",
        "description": "Tail key data: Park boost +4% (stadium -2%, weather +6%). May (HR risk -0.07, vs LHB -0.18, vs RHB +0.21). Stock (HR risk -0.22, vs LHB -0.12, vs RHB -0.36).",
        "rows": [
            row("Luis Robert", "R", "+610", 83, "⭐ 🌕 💣", ["vs May"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 94.8 mph EV. May RHB split +0.21, HR risk -0.07. pitcher risk below avg (-0.07).""", blast="high"),
            row("Luis Torrens", "R", "N/A", 80, "🌕 💣 💎", ["vs May"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 92.0 mph EV. May RHB split +0.21, HR risk -0.07. pitcher risk below avg (-0.07).""", blast="high"),
            row("Brett Baty", "L", "+740", 58, "⭐", ["vs May"], """Worst Pickz Favorite. 0 HR, 94.2 mph EV. May LHB split -0.18, HR risk -0.07. slight split headwind (-0.18); pitcher risk below avg (-0.07).""", blast="good"),
            row("Joey Ortiz", "R", "+800", 58, "💎", ["vs Stock"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.6 mph EV. Stock RHB split -0.36, HR risk -0.22. slight split headwind (-0.36); pitcher risk below avg (-0.22).""", blast="good"),
            row("Jake Bauers", "L", "+442", 58, "⭐", ["vs Stock"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 94.0 mph EV. Stock LHB split -0.12, HR risk -0.22. slight split headwind (-0.12); pitcher risk below avg (-0.22).""", blast="good"),
            row("William Contreras", "R", "+610", 58, "⭐", ["vs Stock"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 93.8 mph EV. Stock RHB split -0.36, HR risk -0.22. slight split headwind (-0.36); pitcher risk below avg (-0.22).""", blast="good"),
            row("Jackson Chourio", "R", "+478", 58, "💎", ["vs Stock"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.6 mph EV. Stock RHB split -0.36, HR risk -0.22. slight split headwind (-0.36); pitcher risk below avg (-0.22).""", blast="good"),
            row("Andrew Vaughn", "R", "+600", 58, "", ["vs Stock"], """0 HR, 95.2 mph EV. Stock RHB split -0.36, HR risk -0.22. slight split headwind (-0.36); pitcher risk below avg (-0.22).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ ATH - Connor Prielipp (L, MIN) vs J.T. Ginn (R, ATH)",
        "description": "Tail key data: Park boost +38% (stadium +30%, weather +9%). Prielipp (HR risk 0.80, vs LHB +1.12, vs RHB +0.51). Ginn (HR risk -0.77, vs LHB -0.46, vs RHB -0.46).",
        "rows": [
            row("Lawrence Butler", "L", "+600", 95, "🌕 💣 💎", ["vs Prielipp"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 95.3 mph EV. Prielipp LHB split +1.12, HR risk 0.80.""", blast="high"),
            row("Jonah Heim", "S", "+500", 86, "", ["vs Prielipp"], """0 HR, 1 near-HR, 93.0 mph EV. Prielipp SHB→LHB split +1.12, HR risk 0.80. limited recent HR events.""", blast="good"),
            row("Tommy White", "R", "+800", 74, "", ["vs Prielipp"], """0 HR, 91.2 mph EV. Prielipp RHB split +0.51, HR risk 0.80. limited recent HR events."""),
            row("Jeff McNeil", "L", "+1100", 78, "", ["vs Prielipp"], """0 HR, 89.9 mph EV. Prielipp LHB split +1.12, HR risk 0.80. limited recent HR events."""),
            row("Kody Clemens", "L", "+330", 64, "💎", ["vs Ginn"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 95.4 mph EV. Ginn LHB split -0.46, HR risk -0.77. tough split lane (-0.46); pitcher suppresses HR (-0.77).""", blast="good"),
            row("Luke Keaschall", "R", "+850", 60, "", ["vs Ginn"], """1 HR, 1 near-HR, 92.7 mph EV. Ginn RHB split -0.46, HR risk -0.77. tough split lane (-0.46); pitcher suppresses HR (-0.77).""", blast="good"),
            row("Josh Bell", "S", "+385", 58, "💎", ["vs Ginn"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 89.4 mph EV. Ginn SHB→LHB split -0.46, HR risk -0.77. tough split lane (-0.46); pitcher suppresses HR (-0.77)."""),
        ],
    },
    {
        "title": "PHI @ SEA - Jesus Luzardo (L, PHI) vs Bryan Woo (R, SEA)",
        "description": "Tail key data: Park boost +0% (stadium +0%, weather +0%). Luzardo (HR risk -0.28, vs LHB -1.34, vs RHB +0.13). Woo (HR risk 0.17, vs LHB -0.07, vs RHB +0.46).",
        "rows": [
            row("Cal Raleigh", "S", "+390", 63, "⭐", ["vs Luzardo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.1 mph EV. Luzardo SHB→RHB split +0.13, HR risk -0.28. pitcher risk below avg (-0.28).""", blast="good"),
            row("Julio Rodriguez", "R", "+610", 58, "", ["vs Luzardo"], """0 HR, 1 near-HR, 94.9 mph EV. Luzardo RHB split +0.13, HR risk -0.28. pitcher risk below avg (-0.28); limited recent HR events.""", blast="good"),
            row("Patrick Wisdom", "R", "N/A", 58, "", ["vs Luzardo"], """0 HR, 94.1 mph EV. Luzardo RHB split +0.13, HR risk -0.28. pitcher risk below avg (-0.28); limited recent HR events.""", blast="good"),
            row("Bryce Harper", "L", "+437", 61, "⭐", ["vs Woo"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.7 mph EV. Woo LHB split -0.07, HR risk 0.17. slight split headwind (-0.07); limited recent HR events.""", blast="good"),
            row("JT Realmuto", "R", "+870", 68, "", ["vs Woo"], """1 HR, 1 near-HR, 93.8 mph EV. Woo RHB split +0.46, HR risk 0.17.""", blast="good"),
            row("Kyle Schwarber", "L", "+260", 58, "", ["vs Woo"], """1 HR, 1 near-HR, 88.4 mph EV. Woo LHB split -0.07, HR risk 0.17. slight split headwind (-0.07).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ SD - Bubba Chandler (R, PIT) vs Randy Vasquez (R, SD)",
        "description": "Tail key data: Park boost +8% (stadium -5%, weather +13%). Chandler (HR risk -0.85, vs LHB +0.16, vs RHB -1.28). Vasquez (HR risk -0.24, vs LHB +0.10, vs RHB -0.31).",
        "rows": [
            row("Jackson Merrill", "L", "+439", 62, "⭐", ["vs Chandler"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.3 mph EV. Chandler LHB split +0.16, HR risk -0.85. pitcher suppresses HR (-0.85).""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+355", 58, "", ["vs Chandler"], """1 HR, 1 near-HR, 93.8 mph EV. Chandler RHB split -1.28, HR risk -0.85. tough split lane (-1.28); pitcher suppresses HR (-0.85).""", blast="good"),
            row("Gavin Sheets", "L", "+560", 60, "🌕 💣", ["vs Chandler"], """2 HR, 2 near-HR, 85.6 mph EV. Chandler LHB split +0.16, HR risk -0.85. pitcher suppresses HR (-0.85); lighter EV form (85.6 mph).""", blast="high"),
            row("Xander Bogaerts", "R", "+820", 58, "", ["vs Chandler"], """0 HR, 95.6 mph EV. Chandler RHB split -1.28, HR risk -0.85. tough split lane (-1.28); pitcher suppresses HR (-0.85).""", blast="good"),
            row("Oneil Cruz", "L", "+300", 69, "⭐ 🌕 💣", ["vs Vasquez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.7 mph EV. Vasquez LHB split +0.10, HR risk -0.24. pitcher risk below avg (-0.24).""", blast="high"),
            row("Rafael Flores", "R", "+1180", 68, "🌕 💣", ["vs Vasquez"], """2 HR, 2 near-HR, 92.9 mph EV. Vasquez RHB split -0.31, HR risk -0.24. slight split headwind (-0.31); pitcher risk below avg (-0.24).""", blast="high"),
            row("Brandon Lowe", "L", "+327", 63, "⭐", ["vs Vasquez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.7 mph EV. Vasquez LHB split +0.10, HR risk -0.24. pitcher risk below avg (-0.24).""", blast="good"),
            row("Bryan Reynolds", "S", "+475", 62, "⭐", ["vs Vasquez"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 95.1 mph EV. Vasquez SHB→LHB split +0.10, HR risk -0.24. pitcher risk below avg (-0.24).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+379", 58, "⭐", ["vs Vasquez"], """Worst Pickz Favorite. 0 HR, 87.8 mph EV. Vasquez RHB split -0.31, HR risk -0.24. slight split headwind (-0.31); pitcher risk below avg (-0.24)."""),
        ],
    },
    {
        "title": "TB @ DET - Freddy Peralta (R, TB) vs Troy Melton (R, DET)",
        "description": "Tail key data: Park boost -18% (stadium -10%, weather -8%). Peralta (HR risk 0.85, vs LHB +0.86, vs RHB +0.60). Melton (HR risk -0.30, vs LHB +0.54, vs RHB -1.04).",
        "rows": [
            row("Hao Yu Lee", "R", "+650", 85, "🌕 💣", ["vs Peralta"], """2 HR, 2 near-HR, 95.6 mph EV. Peralta RHB split +0.60, HR risk 0.85. park/weather net drag (-18%).""", blast="high"),
            row("Colt Keith", "L", "+680", 63, "", ["vs Peralta"], """0 HR, 90.7 mph EV. Peralta LHB split +0.86, HR risk 0.85. park/weather net drag (-18%); limited recent HR events."""),
            row("Kevin McGonigle", "L", "+680", 74, "", ["vs Peralta"], """1 HR, 2 near-HR, 91.2 mph EV. Peralta LHB split +0.86, HR risk 0.85. park/weather net drag (-18%).""", blast="good"),
            row("Eduardo Valencia", "R", "+429", 63, "⭐", ["vs Peralta"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 91.5 mph EV. Peralta RHB split +0.60, HR risk 0.85. park/weather net drag (-18%); limited recent HR events."""),
            row("Junior Caminero", "R", "+380", 58, "", ["vs Melton"], """0 HR, 98.1 mph EV. Melton RHB split -1.04, HR risk -0.30. tough split lane (-1.04); pitcher risk below avg (-0.30).""", blast="good"),
            row("Jonathan Aranda", "L", "+580", 58, "", ["vs Melton"], """0 HR, 92.6 mph EV. Melton LHB split +0.54, HR risk -0.30. pitcher risk below avg (-0.30); park/weather net drag (-18%).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ CWS - MacKenzie Gore (L, TEX) vs Sean Burke (R, CWS)",
        "description": "Tail key data: Park boost +4% (stadium -5%, weather +9%). Gore (HR risk 0.51, vs LHB +0.06, vs RHB +0.47). Burke (HR risk 0.63, vs LHB +0.87, vs RHB +0.27).",
        "rows": [
            row("Randal Grichuk", "R", "+400", 78, "⭐", ["vs Gore"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 98.6 mph EV. Gore RHB split +0.47, HR risk 0.51.""", blast="good"),
            row("Miguel Vargas", "R", "+350", 89, "⭐ 🌕 💣", ["vs Gore"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.3 mph EV. Gore RHB split +0.47, HR risk 0.51.""", blast="high"),
            row("Jake Rogers", "R", "+600", 89, "🌕 💣 💎", ["vs Gore"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 94.6 mph EV. Gore RHB split +0.47, HR risk 0.51.""", blast="high"),
            row("Colson Montgomery", "L", "+390", 64, "💎", ["vs Gore"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 84.6 mph EV. Gore LHB split +0.06, HR risk 0.51. lighter EV form (84.6 mph).""", blast="good"),
            row("Munetaka Murakami", "L", "+361", 88, "🚀 ⭐ 🌕 💣", ["vs Gore"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 100.3 mph EV. Gore LHB split +0.06, HR risk 0.51.""", blast="high"),
            row("Joc Pederson", "L", "+362", 81, "", ["vs Burke"], """1 HR, 1 near-HR, 98.3 mph EV. Burke LHB split +0.87, HR risk 0.63.""", blast="good"),
            row("Brandon Nimmo", "L", "+525", 74, "", ["vs Burke"], """0 HR, 94.6 mph EV. Burke LHB split +0.87, HR risk 0.63. limited recent HR events.""", blast="good"),
            row("Corey Seager", "L", "+330", 67, "💎", ["vs Burke"], """Worst Pickz Hidden Gem. 0 HR, 91.3 mph EV. Burke LHB split +0.87, HR risk 0.63. limited recent HR events."""),
            row("Jake Burger", "R", "+387", 69, "💎", ["vs Burke"], """Worst Pickz Hidden Gem. 0 HR, 94.6 mph EV. Burke RHB split +0.27, HR risk 0.63. limited recent HR events.""", blast="good"),
            row("Justin Foscue", "R", "N/A", 70, "", ["vs Burke"], """0 HR, 2 near-HR, 91.7 mph EV. Burke RHB split +0.27, HR risk 0.63.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-26")

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

    out = ROOT / '_games-0826.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
