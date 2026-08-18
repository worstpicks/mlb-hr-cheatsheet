#!/usr/bin/env python3
"""Generate games[] block for 2026-08-18 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Andrew Benintendi (L)",
    "Brice Turang (L)",
    "Cal Raleigh (S)",
    "Christian Encarnacion-Strand (R)",
    "Coby Mayo (R)",
    "Elly De La Cruz (S)",
    "Griffin Conine (L)",
    "Jackson Chourio (R)",
    "Jonathan Aranda (L)",
    "Joshua Baez (R)",
    "Manny Machado (R)",
    "Matt Olson (L)",
    "Max Muncy (L)",
    "Miguel Amaya (R)",
    "Miguel Vargas (R)",
    "Munetaka Murakami (L)",
    "Oneil Cruz (L)",
    "Pete Crow-Armstrong (L)",
    "Rhys Hoskins (R)",
    "Ronald Acuna Jr. (R)",
    "Wilyer Abreu (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "A.J. Ewing (L)",
    "Abimelec Ortiz (L)",
    "Colt Keith (L)",
    "Jackson Merrill (L)",
    "Jesus Sanchez (L)",
    "Jo Adell (R)",
    "Jordan Walker (R)",
    "Kody Clemens (L)",
    "Lawrence Butler (L)",
    "Pete Alonso (R)",
    "Shohei Ohtani (L)",
    "Spencer Jones (L)",
    "Spencer Torkelson (R)",
    "Taylor Trammell (L)",
    "Tim Tawa (R)",
    "Tyler Stephenson (R)",
}

PLAYER_TEAMS = {
    "A.J. Ewing (L)": "NYM",
    "Abimelec Ortiz (L)": "WSH",
    "Adley Rutschman (S)": "BOS",
    "Alec Bohm (R)": "PHI",
    "Andrew Benintendi (L)": "CWS",
    "Angel Martinez (S)": "CLE",
    "Austin Hays (R)": "SD",
    "Austin Riley (R)": "ATL",
    "Ben Malgeri (R)": "DET",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Braden Montgomery (S)": "CWS",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Brett Callahan (L)": "DET",
    "Brice Turang (L)": "MIL",
    "Bryce Eldridge (L)": "SF",
    "Cal Raleigh (S)": "SEA",
    "Ceddanne Rafaela (R)": "BOS",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Christopher Morel (R)": "NYM",
    "Coby Mayo (R)": "BAL",
    "Cole Carrigg (S)": "COL",
    "Colt Keith (L)": "DET",
    "Corbin Carroll (L)": "ARI",
    "Dominic Canzone (L)": "SEA",
    "Donovan Walton (L)": "ATH",
    "Drake Baldwin (L)": "ATL",
    "Elly De La Cruz (S)": "CIN",
    "Eugenio Suarez (R)": "CIN",
    "Francisco Lindor (S)": "NYM",
    "Freddy Fermin (R)": "SD",
    "Gary Sanchez (R)": "MIL",
    "George Springer (R)": "TOR",
    "Graham Pauley (L)": "MIA",
    "Griffin Conine (L)": "MIA",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "LAD",
    "Hunter Goodman (R)": "COL",
    "Ivan Herrera (R)": "STL",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jacob Young (R)": "WSH",
    "Jake Burger (R)": "TEX",
    "Jake McCarthy (L)": "COL",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jeff McNeil (L)": "ATH",
    "Jesus Sanchez (L)": "TOR",
    "Jo Adell (R)": "CLE",
    "Joe Mack (L)": "MIA",
    "Jonathan Aranda (L)": "TB",
    "Jordan Beck (R)": "COL",
    "Jordan Walker (R)": "STL",
    "Josh Bell (S)": "MIN",
    "Josh Lowe (L)": "LAA",
    "Josh Naylor (L)": "SEA",
    "Joshua Baez (R)": "STL",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "LaMonte Wade Jr. (L)": "HOU",
    "Lawrence Butler (L)": "ATH",
    "Luis Garcia Jr. (L)": "NYY",
    "Luis Robert (R)": "NYM",
    "Manny Machado (R)": "SD",
    "Marcus Semien (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Max Muncy (R)": "ATH",
    "Michael Massey (L)": "KC",
    "Mickey Moniak (L)": "COL",
    "Miguel Amaya (R)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Mike Yastrzemski (L)": "ATL",
    "Moises Ballesteros (L)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Oneil Cruz (L)": "PIT",
    "Owen Caissie (L)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Rhys Hoskins (R)": "CLE",
    "Ronald Acuna Jr. (R)": "ATL",
    "Salvador Perez (R)": "KC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Taylor Trammell (L)": "HOU",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Tommy White (R)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "Victor Bericoto (R)": "SF",
    "William Contreras (R)": "MIL",
    "Wilyer Abreu (L)": "BOS",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("LAD @ COL", "Feltner"),
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
        "title": "ARI @ BOS - Merrill Kelly (R, ARI) vs Ranger Suarez (L, BOS)",
        "description": "Tail key data: Park boost -9% (stadium -8%, weather -2%). Kelly (HR risk 0.75, vs LHB +1.07, vs RHB -0.11). Suarez (HR risk -1.23, vs LHB -0.47, vs RHB -0.99).",
        "rows": [
            row("Wilyer Abreu", "L", "+390", 77, "⭐", ["vs Kelly"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 91.4 mph EV. Kelly LHB split +1.07, HR risk 0.75. park/weather net drag (-9%).""", blast="good"),
            row("Ceddanne Rafaela", "R", "+790", 59, "", ["vs Kelly"], """0 HR, 2 near-HR, 81.1 mph EV. Kelly RHB split -0.11, HR risk 0.75. slight split headwind (-0.11); park/weather net drag (-9%).""", blast="good"),
            row("Adley Rutschman", "S", "+760", 66, "", ["vs Kelly"], """0 HR, 90.6 mph EV. Kelly SHB→LHB split +1.07, HR risk 0.75. park/weather net drag (-9%); limited recent HR events."""),
            row("Tim Tawa", "R", "+920", 58, "💎", ["vs Suarez"], """Worst Pickz Hidden Gem. 0 HR, 98.3 mph EV. Suarez RHB split -0.99, HR risk -1.23. tough split lane (-0.99); pitcher suppresses HR (-1.23).""", blast="good"),
            row("Corbin Carroll", "L", "+593", 58, "", ["vs Suarez"], """1 HR, 2 near-HR, 88.7 mph EV. Suarez LHB split -0.47, HR risk -1.23. tough split lane (-0.47); pitcher suppresses HR (-1.23).""", blast="good"),
        ],
    },
    {
        "title": "ATH @ KC - Brady Basso (L, ATH) vs Daniel Lynch IV (L, KC)",
        "description": "Tail key data: Park boost +17% (stadium +11%, weather +6%). Basso (HR risk -0.54, vs LHB -1.06, vs RHB -0.31). Lynch IV (HR risk -1.23, vs LHB -1.31, vs RHB -0.40).",
        "rows": [
            row("Michael Massey", "L", "N/A", 58, "", ["vs Basso"], """1 HR, 1 near-HR, 91.2 mph EV. Basso LHB split -1.06, HR risk -0.54 (risk carried from 7/25). tough split lane (-1.06); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Bobby Witt Jr.", "R", "N/A", 74, "🌕 💣", ["vs Basso"], """2 HR, 3 near-HR, 94.1 mph EV. Basso RHB split -0.31, HR risk -0.54 (risk carried from 7/25). slight split headwind (-0.31); pitcher suppresses HR (-0.54).""", blast="high"),
            row("Salvador Perez", "R", "N/A", 58, "", ["vs Basso"], """0 HR, 1 near-HR, 87.1 mph EV. Basso RHB split -0.31, HR risk -0.54 (risk carried from 7/25). slight split headwind (-0.31); pitcher suppresses HR (-0.54)."""),
            row("Jac Caglianone", "L", "N/A", 58, "", ["vs Basso"], """0 HR, 1 near-HR, 93.1 mph EV. Basso LHB split -1.06, HR risk -0.54 (risk carried from 7/25). tough split lane (-1.06); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Lawrence Butler", "L", "N/A", 70, "🌕 💣 💎", ["vs Lynch IV"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 98.0 mph EV. Lynch IV LHB split -1.31, HR risk -1.23 (risk carried from 8/12). tough split lane (-1.31); pitcher suppresses HR (-1.23).""", blast="high"),
            row("Max Muncy", "R", "N/A", 58, "", ["vs Lynch IV"], """0 HR, 2 near-HR, 93.6 mph EV. Lynch IV RHB split -0.40, HR risk -1.23 (risk carried from 8/12). tough split lane (-0.40); pitcher suppresses HR (-1.23).""", blast="good"),
            row("Donovan Walton", "L", "N/A", 58, "", ["vs Lynch IV"], """0 HR, 1 near-HR, 94.4 mph EV. Lynch IV LHB split -1.31, HR risk -1.23 (risk carried from 8/12). tough split lane (-1.31); pitcher suppresses HR (-1.23).""", blast="good"),
            row("Jeff McNeil", "L", "N/A", 60, "🌕 💣", ["vs Lynch IV"], """2 HR, 2 near-HR, 93.6 mph EV. Lynch IV LHB split -1.31, HR risk -1.23 (risk carried from 8/12). tough split lane (-1.31); pitcher suppresses HR (-1.23).""", blast="high"),
            row("Tommy White", "R", "N/A", 58, "🌕 💣", ["vs Lynch IV"], """2 HR, 2 near-HR, 87.0 mph EV. Lynch IV RHB split -0.40, HR risk -1.23 (risk carried from 8/12). tough split lane (-0.40); pitcher suppresses HR (-1.23).""", blast="high"),
        ],
    },
    {
        "title": "ATL @ MIN - Tyler Mahle (R, ATL) vs Zebby Matthews (R, MIN)",
        "description": "Tail key data: Park boost -5% (stadium -7%, weather +2%). Mahle (HR risk -0.25, vs LHB -0.39, vs RHB +0.15). Matthews (HR risk 0.90, vs LHB +0.81, vs RHB +0.57).",
        "rows": [
            row("Kody Clemens", "L", "+451", 66, "🌕 💣 💎", ["vs Mahle"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.5 mph EV. Mahle LHB split -0.39, HR risk -0.25. slight split headwind (-0.39); pitcher risk below avg (-0.25).""", blast="high"),
            row("Josh Bell", "S", "+529", 58, "", ["vs Mahle"], """0 HR, 91.6 mph EV. Mahle SHB→RHB split +0.15, HR risk -0.25. pitcher risk below avg (-0.25); park/weather net drag (-5%)."""),
            row("Matt Olson", "L", "+300", 88, "⭐ 🌕 💣", ["vs Matthews"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 89.2 mph EV. Matthews LHB split +0.81, HR risk 0.90. park/weather net drag (-5%).""", blast="high"),
            row("Mike Yastrzemski", "L", "+582", 79, "", ["vs Matthews"], """1 HR, 1 near-HR, 94.5 mph EV. Matthews LHB split +0.81, HR risk 0.90. park/weather net drag (-5%).""", blast="good"),
            row("Austin Riley", "R", "+480", 80, "", ["vs Matthews"], """1 HR, 2 near-HR, 96.4 mph EV. Matthews RHB split +0.57, HR risk 0.90. park/weather net drag (-5%).""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+390", 72, "⭐", ["vs Matthews"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 93.5 mph EV. Matthews RHB split +0.57, HR risk 0.90. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
            row("Drake Baldwin", "L", "+390", 73, "", ["vs Matthews"], """0 HR, 1 near-HR, 92.0 mph EV. Matthews LHB split +0.81, HR risk 0.90. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ CHC - Bryan Hudson (L, CWS) vs Kevin Gausman (R, CHC)",
        "description": "Tail key data: Park boost +26% (stadium -2%, weather +28%). Away starter risk unavailable. Gausman (HR risk -0.58, vs LHB -0.12, vs RHB -0.57).",
        "rows": [
            row("Miguel Amaya", "R", "N/A", 74, "⭐", ["vs Hudson"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.0 mph EV. Hudson split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Pete Crow-Armstrong", "L", "N/A", 58, "⭐", ["vs Hudson"], """Worst Pickz Favorite. 0 HR, 85.1 mph EV. Hudson split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
            row("Munetaka Murakami", "L", "+285", 78, "⭐ 🌕 💣", ["vs Gausman"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.7 mph EV. Gausman LHB split -0.12, HR risk -0.58. slight split headwind (-0.12); pitcher suppresses HR (-0.58).""", blast="high"),
            row("Miguel Vargas", "R", "+330", 72, "⭐ 🌕 💣", ["vs Gausman"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 92.3 mph EV. Gausman RHB split -0.57, HR risk -0.58. tough split lane (-0.57); pitcher suppresses HR (-0.58).""", blast="high"),
            row("Andrew Benintendi", "L", "+470", 64, "⭐", ["vs Gausman"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.6 mph EV. Gausman LHB split -0.12, HR risk -0.58. slight split headwind (-0.12); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Braden Montgomery", "S", "+840", 58, "", ["vs Gausman"], """0 HR, 1 near-HR, 92.3 mph EV. Gausman SHB→LHB split -0.12, HR risk -0.58. slight split headwind (-0.12); pitcher suppresses HR (-0.58).""", blast="good"),
        ],
    },
    {
        "title": "DET @ PIT - Keider Montero (R, DET) vs Braxton Ashcraft (R, PIT)",
        "description": "Tail key data: Park boost -12% (stadium -15%, weather +3%). Montero (HR risk 0.01, vs LHB +0.19, vs RHB +0.11). Ashcraft (HR risk 0.57, vs LHB +0.56, vs RHB +0.25).",
        "rows": [
            row("Oneil Cruz", "L", "+375", 69, "⭐ 🌕 💣", ["vs Montero"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.8 mph EV. Montero LHB split +0.19, HR risk 0.01. park/weather net drag (-12%).""", blast="high"),
            row("Brandon Lowe", "L", "+334", 59, "", ["vs Montero"], """1 HR, 1 near-HR, 91.8 mph EV. Montero LHB split +0.19, HR risk 0.01. park/weather net drag (-12%).""", blast="good"),
            row("Colt Keith", "L", "+725", 72, "💎", ["vs Ashcraft"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.7 mph EV. Ashcraft LHB split +0.56, HR risk 0.57. park/weather net drag (-12%).""", blast="good"),
            row("Brett Callahan", "L", "N/A", 69, "", ["vs Ashcraft"], """0 HR, 97.5 mph EV. Ashcraft LHB split +0.56, HR risk 0.57. park/weather net drag (-12%); limited recent HR events.""", blast="good"),
            row("Spencer Torkelson", "R", "+590", 67, "💎", ["vs Ashcraft"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.5 mph EV. Ashcraft RHB split +0.25, HR risk 0.57. park/weather net drag (-12%); limited recent HR events.""", blast="good"),
            row("Ben Malgeri", "R", "N/A", 75, "🌕 💣", ["vs Ashcraft"], """2 HR, 2 near-HR, 89.7 mph EV. Ashcraft RHB split +0.25, HR risk 0.57. park/weather net drag (-12%).""", blast="high"),
        ],
    },
    {
        "title": "LAA @ HOU - George Klassen (R, LAA) vs Cristian Javier (R, HOU)",
        "description": "Tail key data: Park boost +6% (stadium +6%, weather +0%). Klassen (HR risk 0.66, vs LHB +0.31, vs RHB +1.00). Javier (HR risk 0.35, vs LHB -0.16, vs RHB +0.79).",
        "rows": [
            row("Yordan Alvarez", "L", "+240", 77, "⭐", ["vs Klassen"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.3 mph EV. Klassen LHB split +0.31, HR risk 0.66.""", blast="good"),
            row("Taylor Trammell", "L", "+475", 83, "💎", ["vs Klassen"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 96.3 mph EV. Klassen LHB split +0.31, HR risk 0.66.""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 77, "", ["vs Klassen"], """0 HR, 1 near-HR, 93.9 mph EV. Klassen RHB split +1.00, HR risk 0.66. limited recent HR events.""", blast="good"),
            row("LaMonte Wade Jr.", "L", "N/A", 63, "", ["vs Klassen"], """0 HR, 1 near-HR, 89.2 mph EV. Klassen LHB split +0.31, HR risk 0.66. limited recent HR events."""),
            row("Moises Ballesteros", "L", "+540", 62, "", ["vs Javier"], """0 HR, 1 near-HR, 94.2 mph EV. Javier LHB split -0.16, HR risk 0.35. slight split headwind (-0.16); limited recent HR events.""", blast="good"),
            row("Josh Lowe", "L", "+525", 58, "", ["vs Javier"], """0 HR, 1 near-HR, 88.1 mph EV. Javier LHB split -0.16, HR risk 0.35. slight split headwind (-0.16); limited recent HR events."""),
        ],
    },
    {
        "title": "LAD @ COL - Eric Lauer (L, LAD) vs Ryan Feltner 🧤 (R, COL)",
        "description": "Tail key data: Park boost +25% (stadium +21%, weather +4%). Lauer (HR risk 0.68, vs LHB +1.11, vs RHB +0.40). Feltner 🧤 (HR risk 1.41, vs LHB +0.58, vs RHB +1.84).",
        "rows": [
            row("Mickey Moniak", "L", "+425", 80, "", ["vs Lauer"], """1 HR, 1 near-HR, 87.3 mph EV. Lauer LHB split +1.11, HR risk 0.68. lighter EV form (87.3 mph).""", blast="good"),
            row("Cole Carrigg", "S", "+590", 74, "", ["vs Lauer"], """0 HR, 1 near-HR, 89.0 mph EV. Lauer SHB→LHB split +1.11, HR risk 0.68. limited recent HR events."""),
            row("Jake McCarthy", "L", "+880", 79, "", ["vs Lauer"], """1 HR, 1 near-HR, 85.5 mph EV. Lauer LHB split +1.11, HR risk 0.68. lighter EV form (85.5 mph).""", blast="good"),
            row("Hunter Goodman", "R", "+240", 64, "", ["vs Lauer"], """0 HR, 81.3 mph EV. Lauer RHB split +0.40, HR risk 0.68. limited recent HR events; lighter EV form (81.3 mph)."""),
            row("Jordan Beck", "R", "+540", 65, "", ["vs Lauer"], """0 HR, 87.6 mph EV. Lauer RHB split +0.40, HR risk 0.68. limited recent HR events; lighter EV form (87.6 mph)."""),
            row("Max Muncy", "L", "+285", 95, "⭐ 🌕 💣", ["vs Feltner"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.4 mph EV. Feltner LHB split +0.58, HR risk 1.41.""", blast="high"),
            row("Hunter Feduccia", "L", "+880", 88, "🌕 💣", ["vs Feltner"], """1 HR, 1 near-HR, 91.4 mph EV. Feltner LHB split +0.58, HR risk 1.41.""", blast="good"),
            row("Teoscar Hernandez", "R", "+423", 94, "🌕 💣", ["vs Feltner"], """0 HR, 1 near-HR, 97.8 mph EV. Feltner RHB split +1.84, HR risk 1.41. limited recent HR events.""", blast="good"),
            row("Shohei Ohtani", "L", "+211", 89, "🌕 💣 💎", ["vs Feltner"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.7 mph EV. Feltner LHB split +0.58, HR risk 1.41. limited recent HR events.""", blast="good"),
            row("Mookie Betts", "R", "+470", 89, "🌕 💣", ["vs Feltner"], """0 HR, 91.5 mph EV. Feltner RHB split +1.84, HR risk 1.41. limited recent HR events."""),
        ],
    },
    {
        "title": "MIA @ PHI - Cade Gibson (R, MIA) vs Zack Wheeler (R, PHI)",
        "description": "Tail key data: Park boost +13% (stadium +15%, weather -2%). Gibson (HR risk -0.65, vs LHB -0.72, vs RHB -0.59). Wheeler (HR risk 0.01, vs LHB +0.66, vs RHB -0.70).",
        "rows": [
            row("Alec Bohm", "R", "+880", 58, "", ["vs Gibson"], """0 HR, 1 near-HR, 93.9 mph EV. Gibson RHB split -0.59, HR risk -0.65. tough split lane (-0.59); pitcher suppresses HR (-0.65).""", blast="good"),
            row("Kyle Schwarber", "L", "+260", 58, "", ["vs Gibson"], """0 HR, 1 near-HR, 88.1 mph EV. Gibson LHB split -0.72, HR risk -0.65. tough split lane (-0.72); pitcher suppresses HR (-0.65)."""),
            row("Owen Caissie", "L", "+570", 90, "🌕 💣", ["vs Wheeler"], """3 HR, 3 near-HR, 95.1 mph EV. Wheeler LHB split +0.66, HR risk 0.01.""", blast="high"),
            row("Griffin Conine", "L", "+505", 79, "🚀 ⭐", ["vs Wheeler"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 101.3 mph EV. Wheeler LHB split +0.66, HR risk 0.01.""", blast="good"),
            row("Joe Mack", "L", "+600", 71, "", ["vs Wheeler"], """1 HR, 1 near-HR, 94.0 mph EV. Wheeler LHB split +0.66, HR risk 0.01.""", blast="good"),
            row("Graham Pauley", "L", "N/A", 60, "", ["vs Wheeler"], """0 HR, 1 near-HR, 91.0 mph EV. Wheeler LHB split +0.66, HR risk 0.01. limited recent HR events."""),
            row("Heriberto Hernandez", "R", "+498", 58, "", ["vs Wheeler"], """1 HR, 1 near-HR, 83.3 mph EV. Wheeler RHB split -0.70, HR risk 0.01. tough split lane (-0.70); lighter EV form (83.3 mph).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ BAL - Carlos Rodon (L, NYY) vs Shane Baz (R, BAL)",
        "description": "Tail key data: Park boost +1% (stadium -3%, weather +3%). Rodon (HR risk -0.83, vs LHB -0.05, vs RHB -0.72). Baz (HR risk -0.70, vs LHB -0.34, vs RHB -0.89).",
        "rows": [
            row("Christian Encarnacion-Strand", "R", "+520", 58, "⭐", ["vs Rodon"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 99.7 mph EV. Rodon RHB split -0.72, HR risk -0.83. tough split lane (-0.72); pitcher suppresses HR (-0.83).""", blast="good"),
            row("Coby Mayo", "R", "+394", 58, "⭐", ["vs Rodon"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.4 mph EV. Rodon RHB split -0.72, HR risk -0.83. tough split lane (-0.72); pitcher suppresses HR (-0.83).""", blast="good"),
            row("Pete Alonso", "R", "+410", 58, "💎", ["vs Rodon"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.6 mph EV. Rodon RHB split -0.72, HR risk -0.83. tough split lane (-0.72); pitcher suppresses HR (-0.83).""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "+414", 58, "", ["vs Baz"], """0 HR, 1 near-HR, 98.5 mph EV. Baz LHB split -0.34, HR risk -0.70. slight split headwind (-0.34); pitcher suppresses HR (-0.70).""", blast="good"),
            row("Spencer Jones", "L", "+590", 58, "💎", ["vs Baz"], """Worst Pickz Hidden Gem. 0 HR, 95.4 mph EV. Baz LHB split -0.34, HR risk -0.70. slight split headwind (-0.34); pitcher suppresses HR (-0.70).""", blast="good"),
            row("Ben Rice", "L", "+347", 58, "", ["vs Baz"], """0 HR, 96.8 mph EV. Baz LHB split -0.34, HR risk -0.70. slight split headwind (-0.34); pitcher suppresses HR (-0.70).""", blast="good"),
            row("Luis Garcia Jr.", "L", "+471", 58, "", ["vs Baz"], """0 HR, 1 near-HR, 91.0 mph EV. Baz LHB split -0.34, HR risk -0.70. slight split headwind (-0.34); pitcher suppresses HR (-0.70)."""),
        ],
    },
    {
        "title": "SD @ NYM - Robbie Ray (L, SD) vs Zach Thornton (L, NYM)",
        "description": "Tail key data: Park boost -9% (stadium -1%, weather -8%). Ray (HR risk -0.43, vs LHB -1.07, vs RHB +0.07). Thornton (HR risk -0.10, vs LHB -0.60, vs RHB +0.29).",
        "rows": [
            row("Christopher Morel", "R", "+600", 58, "", ["vs Ray"], """0 HR, 1 near-HR, 95.8 mph EV. Ray RHB split +0.07, HR risk -0.43. pitcher suppresses HR (-0.43); park/weather net drag (-9%).""", blast="good"),
            row("Francisco Lindor", "S", "+343", 58, "", ["vs Ray"], """1 HR, 2 near-HR, 91.0 mph EV. Ray SHB→RHB split +0.07, HR risk -0.43. pitcher suppresses HR (-0.43); park/weather net drag (-9%).""", blast="good"),
            row("Marcus Semien", "R", "+630", 58, "", ["vs Ray"], """0 HR, 92.4 mph EV. Ray RHB split +0.07, HR risk -0.43. pitcher suppresses HR (-0.43); park/weather net drag (-9%).""", blast="good"),
            row("Luis Robert", "R", "+478", 58, "", ["vs Ray"], """1 HR, 1 near-HR, 89.9 mph EV. Ray RHB split +0.07, HR risk -0.43. pitcher suppresses HR (-0.43); park/weather net drag (-9%).""", blast="good"),
            row("A.J. Ewing", "L", "+880", 58, "🚀 💎", ["vs Ray"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 100.7 mph EV. Ray LHB split -1.07, HR risk -0.43. tough split lane (-1.07); pitcher suppresses HR (-0.43).""", blast="good"),
            row("Manny Machado", "R", "+346", 58, "⭐", ["vs Thornton"], """Worst Pickz Favorite. 0 HR, 96.9 mph EV. Thornton RHB split +0.29, HR risk -0.10. pitcher risk below avg (-0.10); park/weather net drag (-9%).""", blast="good"),
            row("Austin Hays", "R", "+650", 63, "", ["vs Thornton"], """1 HR, 1 near-HR, 95.6 mph EV. Thornton RHB split +0.29, HR risk -0.10. pitcher risk below avg (-0.10); park/weather net drag (-9%).""", blast="good"),
            row("Jackson Merrill", "L", "+580", 58, "💎", ["vs Thornton"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 96.3 mph EV. Thornton LHB split -0.60, HR risk -0.10. tough split lane (-0.60); pitcher risk below avg (-0.10).""", blast="good"),
            row("Freddy Fermin", "R", "+800", 58, "", ["vs Thornton"], """0 HR, 91.1 mph EV. Thornton RHB split +0.29, HR risk -0.10. pitcher risk below avg (-0.10); park/weather net drag (-9%)."""),
        ],
    },
    {
        "title": "SEA @ MIL - Bryce Miller (R, SEA) vs Kyle Harrison (L, MIL)",
        "description": "Tail key data: Park boost +13% (stadium -1%, weather +15%). Miller (HR risk 0.62, vs LHB +0.36, vs RHB +0.85). Harrison (HR risk 0.61, vs LHB -0.68, vs RHB +0.79).",
        "rows": [
            row("Jackson Chourio", "R", "+432", 94, "🚀 ⭐ 🌕 💣", ["vs Miller"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 101.1 mph EV. Miller RHB split +0.85, HR risk 0.62.""", blast="high"),
            row("Gary Sanchez", "R", "N/A", 77, "", ["vs Miller"], """1 HR, 1 near-HR, 89.6 mph EV. Miller RHB split +0.85, HR risk 0.62.""", blast="good"),
            row("Brice Turang", "L", "+540", 74, "⭐", ["vs Miller"], """Worst Pickz Favorite. 0 HR, 96.4 mph EV. Miller LHB split +0.36, HR risk 0.62. limited recent HR events.""", blast="good"),
            row("William Contreras", "R", "+566", 78, "", ["vs Miller"], """0 HR, 96.9 mph EV. Miller RHB split +0.85, HR risk 0.62. limited recent HR events.""", blast="good"),
            row("Cal Raleigh", "S", "+390", 91, "⭐ 🌕 💣", ["vs Harrison"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.2 mph EV. Harrison SHB→RHB split +0.79, HR risk 0.61.""", blast="high"),
            row("Josh Naylor", "L", "+890", 67, "", ["vs Harrison"], """0 HR, 1 near-HR, 96.2 mph EV. Harrison LHB split -0.68, HR risk 0.61. tough split lane (-0.68); limited recent HR events.""", blast="good"),
            row("Dominic Canzone", "L", "+540", 89, "🚀 🌕 💣", ["vs Harrison"], """3 HR, 3 near-HR, 100.0 mph EV. Harrison LHB split -0.68, HR risk 0.61. tough split lane (-0.68).""", blast="high"),
        ],
    },
    {
        "title": "SF @ CLE - Carson Whisenhunt (L, SF) vs Foster Griffin (L, CLE)",
        "description": "Tail key data: Park boost +7% (stadium -5%, weather +12%). Whisenhunt (HR risk 0.90, vs LHB -1.34, vs RHB +1.28). Griffin (HR risk 0.44, vs LHB +1.26, vs RHB +0.05).",
        "rows": [
            row("Jo Adell", "R", "+448", 91, "🌕 💣 💎", ["vs Whisenhunt"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 87.7 mph EV. Whisenhunt RHB split +1.28, HR risk 0.90. lighter EV form (87.7 mph).""", blast="high"),
            row("Rhys Hoskins", "R", "+422", 93, "⭐ 🌕 💣", ["vs Whisenhunt"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 92.4 mph EV. Whisenhunt RHB split +1.28, HR risk 0.90.""", blast="high"),
            row("Angel Martinez", "S", "+610", 75, "", ["vs Whisenhunt"], """0 HR, 2 near-HR, 80.8 mph EV. Whisenhunt SHB→RHB split +1.28, HR risk 0.90. lighter EV form (80.8 mph).""", blast="good"),
            row("Bryce Eldridge", "L", "+495", 81, "", ["vs Griffin"], """1 HR, 1 near-HR, 94.2 mph EV. Griffin LHB split +1.26, HR risk 0.44.""", blast="good"),
            row("Rafael Devers", "L", "+390", 78, "", ["vs Griffin"], """0 HR, 96.8 mph EV. Griffin LHB split +1.26, HR risk 0.44. limited recent HR events.""", blast="good"),
            row("Victor Bericoto", "R", "+880", 67, "", ["vs Griffin"], """0 HR, 1 near-HR, 93.1 mph EV. Griffin RHB split +0.05, HR risk 0.44. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "STL @ CIN - Kyle Leahy (R, STL) vs Andrew Abbott (L, CIN)",
        "description": "Tail key data: Park boost +18% (stadium +13%, weather +5%). Leahy (HR risk 0.03, vs LHB +0.09, vs RHB -0.07). Abbott (HR risk -0.65, vs LHB -0.63, vs RHB -0.33).",
        "rows": [
            row("Tyler Stephenson", "R", "+520", 73, "🌕 💣 💎", ["vs Leahy"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 90.7 mph EV. Leahy RHB split -0.07, HR risk 0.03. slight split headwind (-0.07).""", blast="high"),
            row("Elly De La Cruz", "S", "+390", 61, "⭐", ["vs Leahy"], """Worst Pickz Favorite. 0 HR, 92.9 mph EV. Leahy SHB→LHB split +0.09, HR risk 0.03. limited recent HR events.""", blast="good"),
            row("Eugenio Suarez", "R", "+450", 58, "", ["vs Leahy"], """0 HR, 89.8 mph EV. Leahy RHB split -0.07, HR risk 0.03. slight split headwind (-0.07); limited recent HR events."""),
            row("JJ Bleday", "L", "+360", 58, "", ["vs Leahy"], """0 HR, 85.8 mph EV. Leahy LHB split +0.09, HR risk 0.03. limited recent HR events; lighter EV form (85.8 mph)."""),
            row("Joshua Baez", "R", "+406", 70, "🚀 ⭐ 🌕 💣", ["vs Abbott"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 104.4 mph EV. Abbott RHB split -0.33, HR risk -0.65. slight split headwind (-0.33); pitcher suppresses HR (-0.65).""", blast="high"),
            row("Jordan Walker", "R", "+310", 63, "🌕 💣 💎", ["vs Abbott"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 89.0 mph EV. Abbott RHB split -0.33, HR risk -0.65. slight split headwind (-0.33); pitcher suppresses HR (-0.65).""", blast="high"),
            row("Ivan Herrera", "R", "+470", 58, "", ["vs Abbott"], """0 HR, 92.1 mph EV. Abbott RHB split -0.33, HR risk -0.65. slight split headwind (-0.33); pitcher suppresses HR (-0.65).""", blast="good"),
            row("JJ Wetherholt", "L", "+456", 58, "", ["vs Abbott"], """1 HR, 2 near-HR, 88.2 mph EV. Abbott LHB split -0.63, HR risk -0.65. tough split lane (-0.63); pitcher suppresses HR (-0.65).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ TB - Jose Soriano (R, TOR) vs Nick Martinez (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Soriano (HR risk -0.59, vs LHB -0.46, vs RHB -0.36). Martinez (HR risk -0.11, vs LHB +0.40, vs RHB -0.57).",
        "rows": [
            row("Jonathan Aranda", "L", "+625", 58, "⭐", ["vs Soriano"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 94.0 mph EV. Soriano LHB split -0.46, HR risk -0.59. tough split lane (-0.46); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Yandy Diaz", "R", "+790", 58, "", ["vs Soriano"], """1 HR, 1 near-HR, 97.0 mph EV. Soriano RHB split -0.36, HR risk -0.59. slight split headwind (-0.36); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Jesus Sanchez", "L", "+590", 66, "💎", ["vs Martinez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.3 mph EV. Martinez LHB split +0.40, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="good"),
            row("George Springer", "R", "+500", 58, "", ["vs Martinez"], """0 HR, 93.8 mph EV. Martinez RHB split -0.57, HR risk -0.11. tough split lane (-0.57); pitcher risk below avg (-0.11).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ TEX - Jackson Kent (L, WSH) vs Cal Quantrill (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -10%, weather -1%). Kent (HR risk 0.00, vs LHB +0.00, vs RHB -1.54). Quantrill (HR risk -0.60, vs LHB +0.16, vs RHB -0.88).",
        "rows": [
            row("Jake Burger", "R", "+470", 60, "🌕 💣", ["vs Kent"], """2 HR, 2 near-HR, 90.0 mph EV. Kent RHB split -1.54, HR risk 0.00. tough split lane (-1.54); park/weather net drag (-11%).""", blast="high"),
            row("Brandon Nimmo", "L", "+550", 63, "", ["vs Kent"], """1 HR, 2 near-HR, 95.4 mph EV. Kent LHB split +0.00, HR risk 0.00. park/weather net drag (-11%).""", blast="good"),
            row("Abimelec Ortiz", "L", "+443", 75, "🌕 💣 💎", ["vs Quantrill"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 97.4 mph EV. Quantrill LHB split +0.16, HR risk -0.60. pitcher suppresses HR (-0.60); park/weather net drag (-11%).""", blast="high"),
            row("Jacob Young", "R", "+1500", 58, "", ["vs Quantrill"], """0 HR, 93.2 mph EV. Quantrill RHB split -0.88, HR risk -0.60. tough split lane (-0.88); pitcher suppresses HR (-0.60).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-18")

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

    out = ROOT / '_games-0818.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
