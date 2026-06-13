#!/usr/bin/env python3
"""Generate games[] block for 2026-06-13 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Bryce Eldridge (L)",
    "Cedric Mullins (L)",
    "Colby Thomas (R)",
    "Dominic Canzone (L)",
    "JJ Bleday (L)",
    "Jac Caglianone (L)",
    "Jake Bauers (L)",
    "James Wood (L)",
    "Jeremy Pena (R)",
    "Justin Foscue (R)",
    "Kyle Schwarber (L)",
    "Matt McLain (R)",
    "Mike Trout (R)",
    "Nick Kurtz (L)",
    "Pete Crow-Armstrong (L)",
    "Rhys Hoskins (R)",
    "Samuel Basallo (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Ben Rice (L)",
    "Brandon Marsh (L)",
    "Cole Carrigg (S)",
    "Colson Montgomery (L)",
    "Jimmy Crooks (L)",
    "Joc Pederson (L)",
    "Jonah Cox (R)",
    "Tyler Callihan (L)",
    "Willy Adames (R)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BAL",
    "Alec Burleson (L)": "STL",
    "Andy Pages (R)": "LAD",
    "Angel Martinez (S)": "CLE",
    "Ben Rice (L)": "NYY",
    "Blaze Alexander (R)": "BAL",
    "Brandon Marsh (L)": "PHI",
    "Brandon Valenzuela (S)": "TOR",
    "Bryce Eldridge (L)": "SF",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Caleb Durbin (R)": "BOS",
    "Cam Smith (R)": "HOU",
    "Cedric Mullins (L)": "TB",
    "Cody Bellinger (L)": "NYY",
    "Colby Thomas (R)": "ATH",
    "Cole Carrigg (S)": "COL",
    "Colson Montgomery (L)": "CWS",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "Dominic Canzone (L)": "SEA",
    "Dylan Crews (R)": "WSH",
    "Edmundo Sosa (R)": "PHI",
    "Endy Rodriguez (S)": "PIT",
    "Fernando Tatis Jr. (R)": "SD",
    "Freddie Freeman (L)": "LAD",
    "Gabriel Moreno (R)": "ARI",
    "Garrett Mitchell (L)": "MIL",
    "Gary Sanchez (R)": "MIL",
    "Gleyber Torres (R)": "DET",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Jarren Duran (L)": "BOS",
    "Jeremy Pena (R)": "HOU",
    "Jesus Sanchez (L)": "TOR",
    "Jimmy Crooks (L)": "STL",
    "Joc Pederson (L)": "TEX",
    "Jonah Cox (R)": "SF",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Jorge Mateo (R)": "ATL",
    "Justin Foscue (R)": "TEX",
    "Kody Clemens (L)": "MIN",
    "Kyle Higashioka (R)": "TEX",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Logan O'Hoppe (R)": "LAA",
    "Luis Garcia Jr. (L)": "WSH",
    "Luke Raley (L)": "SEA",
    "Manny Machado (R)": "SD",
    "Marcus Semien (R)": "NYM",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Michael Conforto (L)": "CHC",
    "Michael Massey (L)": "KC",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Nelson Velazquez (R)": "STL",
    "Nick Kurtz (L)": "ATH",
    "Owen Caissie (L)": "MIA",
    "Patrick Wisdom (R)": "SEA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Ryan McMahon (L)": "NYY",
    "Ryan O'Hearn (L)": "PIT",
    "Ryan Ward (L)": "LAD",
    "Salvador Perez (R)": "KC",
    "Samuel Basallo (L)": "BAL",
    "Seiya Suzuki (R)": "CHC",
    "Shea Langeliers (R)": "ATH",
    "Spencer Torkelson (R)": "DET",
    "TJ Rumfield (L)": "COL",
    "Tristan Gray (L)": "MIN",
    "Tyler Callihan (L)": "PIT",
    "Tyler Stephenson (R)": "CIN",
    "Wenceel Perez (S)": "DET",
    "Willi Castro (S)": "COL",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Yordan Alvarez (L)": "HOU",
    "Zack Gelof (R)": "ATH",
}

BUM_PITCHERS = {
    "Burrows",
    "Estes",
    "Freeland",
    "Vasquez",
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

def add_bum_row_emojis(entry):
    chip = entry["chips"][0].replace("vs ", "").strip()
    if chip not in BUM_PITCHERS:
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
        "title": "ARI @ CIN - Michael Soroka (R, ARI) vs Rhett Lowder (R, CIN)",
        "description": "Tail key data: Park boost +15% (stadium +14%, weather +1%). Soroka (HR risk -0.69, vs LHB -0.39, vs RHB -0.77). Lowder (HR risk -0.68, vs LHB -0.03, vs RHB -1.23).",
        "rows": [
            row("JJ Bleday", "L", "+325", 80, "⭐ 🌕 💣", ["vs Soroka"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.5 mph EV. Soroka LHB split -0.39, HR risk -0.69. slight split headwind (-0.39); pitcher suppresses HR (-0.69).""", blast="high"),
            row("Tyler Stephenson", "R", "+565", 83, "🌕 💣", ["vs Soroka"], """2 HR, 2 near-HR, 93.2 mph EV. Soroka RHB split -0.77, HR risk -0.69. tough split lane (-0.77); pitcher suppresses HR (-0.69).""", blast="high"),
            row("Matt McLain", "R", "+589", 80, "⭐", ["vs Soroka"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 93.8 mph EV. Soroka RHB split -0.77, HR risk -0.69. tough split lane (-0.77); pitcher suppresses HR (-0.69).""", blast="good"),
            row("Gabriel Moreno", "R", "+564", 83, "🌕 💣", ["vs Lowder"], """2 HR, 2 near-HR, 93.0 mph EV. Lowder RHB split -1.23, HR risk -0.68. tough split lane (-1.23); pitcher suppresses HR (-0.68).""", blast="high"),
            row("Corbin Carroll", "L", "+330", 82, "🌕 💣", ["vs Lowder"], """2 HR, 2 near-HR, 92.3 mph EV. Lowder LHB split -0.03, HR risk -0.68. slight split headwind (-0.03); pitcher suppresses HR (-0.68).""", blast="high"),
        ],
    },
    {
        "title": "ATL @ NYM - Martin Perez (L, ATL) vs Sean Manaea (L, NYM)",
        "description": "Tail key data: Park boost -1% (stadium -1%, weather +0%). Perez (HR risk -0.07, vs LHB +0.04, vs RHB -0.08). Home starter risk unavailable.",
        "rows": [
            row("Marcus Semien", "R", "N/A", 74, "", ["vs Perez"], """1 HR, 1 near-HR, 92.1 mph EV. Perez RHB split -0.08, HR risk -0.07. slight split headwind (-0.08); pitcher risk below avg (-0.07).""", blast="good"),
            row("Jorge Mateo", "R", "N/A", 82, "🌕 💣", ["vs Manaea"], """2 HR, 2 near-HR, 92.5 mph EV. Manaea split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Matt Olson", "L", "N/A", 79, "", ["vs Manaea"], """1 HR, 2 near-HR, 95.3 mph EV. Manaea split/risk data unavailable. limited split/risk sample.""", blast="good"),
        ],
    },
    {
        "title": "CHC @ SF - Ben Brown (R, CHC) vs Trevor McDonald (R, SF)",
        "description": "Tail key data: Park boost -16% (stadium -15%, weather -1%). Brown (HR risk -0.59, vs LHB -0.59, vs RHB -0.37). McDonald (HR risk -0.86, vs LHB -0.57, vs RHB -0.86).",
        "rows": [
            row("Bryce Eldridge", "L", "+550", 86, "⭐ 🌕 💣", ["vs Brown"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.3 mph EV. Brown LHB split -0.59, HR risk -0.59. tough split lane (-0.59); pitcher suppresses HR (-0.59).""", blast="high"),
            row("Willy Adames", "R", "+630", 89, "🌕 💣 💎", ["vs Brown"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 97.1 mph EV. Brown RHB split -0.37, HR risk -0.59. slight split headwind (-0.37); pitcher suppresses HR (-0.59).""", blast="high"),
            row("Jonah Cox", "R", "N/A", 71, "💎", ["vs Brown"], """Worst Pickz Hidden Gem. 0 HR, 95.3 mph EV. Brown RHB split -0.37, HR risk -0.59. slight split headwind (-0.37); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+600", 86, "⭐ 🌕 💣", ["vs McDonald"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.1 mph EV. McDonald LHB split -0.57, HR risk -0.86. tough split lane (-0.57); pitcher suppresses HR (-0.86).""", blast="high"),
            row("Seiya Suzuki", "R", "+730", 84, "🌕 💣", ["vs McDonald"], """2 HR, 3 near-HR, 91.8 mph EV. McDonald RHB split -0.86, HR risk -0.86. tough split lane (-0.86); pitcher suppresses HR (-0.86).""", blast="high"),
            row("Ian Happ", "S", "+525", 63, "", ["vs McDonald"], """0 HR, 89.0 mph EV. McDonald RHB split -0.86, HR risk -0.86. tough split lane (-0.86); pitcher suppresses HR (-0.86)."""),
            row("Michael Conforto", "L", "N/A", 72, "", ["vs McDonald"], """1 HR, 1 near-HR, 90.5 mph EV. McDonald LHB split -0.57, HR risk -0.86. tough split lane (-0.57); pitcher suppresses HR (-0.86).""", blast="good"),
        ],
    },
    {
        "title": "COL @ ATH - Kyle Freeland 🧤 (L, COL) vs Joey Estes 🧤 (R, ATH)",
        "description": "Tail key data: Park boost +92% (stadium +73%, weather +19%). Freeland 🧤 (HR risk 1.05, vs LHB -0.92, vs RHB +1.19). Estes 🧤 (HR risk 2.02, vs LHB +0.16, vs RHB +2.54).",
        "rows": [
            row("Nick Kurtz", "L", "+154", 81, "⭐ 🌕 💣", ["vs Freeland"], """Worst Pickz Favorite. 2 HR, 1 near-HR, 93.0 mph EV. Freeland LHB split -0.92, HR risk 1.05. tough split lane (-0.92).""", blast="high"),
            row("Shea Langeliers", "R", "+150", 95, "🌕 💣", ["vs Freeland"], """4 HR, 3 near-HR, 95.4 mph EV. Freeland RHB split +1.19, HR risk 1.05.""", blast="high"),
            row("Henry Bolte", "R", "+410", 82, "🚀", ["vs Freeland"], """1 HR, 1 near-HR, 102.9 mph EV. Freeland RHB split +1.19, HR risk 1.05.""", blast="good"),
            row("Colby Thomas", "R", "+264", 75, "⭐", ["vs Freeland"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.8 mph EV. Freeland RHB split +1.19, HR risk 1.05.""", blast="good"),
            row("Zack Gelof", "R", "+310", 75, "", ["vs Freeland"], """1 HR, 2 near-HR, 90.9 mph EV. Freeland RHB split +1.19, HR risk 1.05.""", blast="good"),
            row("Hunter Goodman", "R", "+154", 90, "🌕 💣", ["vs Estes"], """3 HR, 3 near-HR, 93.8 mph EV. Estes RHB split +2.54, HR risk 2.02.""", blast="high"),
            row("Cole Carrigg", "S", "N/A", 72, "💎", ["vs Estes"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.0 mph EV. Estes RHB split +2.54, HR risk 2.02.""", blast="good"),
            row("TJ Rumfield", "L", "+360", 70, "", ["vs Estes"], """1 HR, 1 near-HR, 83.8 mph EV. Estes LHB split +0.16, HR risk 2.02. lighter EV form (83.8 mph).""", blast="good"),
            row("Willi Castro", "S", "+310", 72, "", ["vs Estes"], """1 HR, 2 near-HR, 86.9 mph EV. Estes RHB split +2.54, HR risk 2.02. lighter EV form (86.9 mph).""", blast="good"),
        ],
    },
    {
        "title": "DET @ CLE - Tarik Skubal (L, DET) vs Joey Cantillo (L, CLE)",
        "description": "Tail key data: Park boost +10% (stadium -5%, weather +15%). Skubal (HR risk -0.88, vs LHB -0.55, vs RHB -0.53). Cantillo (HR risk 0.71, vs LHB +0.05, vs RHB +0.68).",
        "rows": [
            row("Angel Martinez", "S", "+570", 70, "", ["vs Skubal"], """1 HR, 1 near-HR, 87.8 mph EV. Skubal RHB split -0.53, HR risk -0.88. tough split lane (-0.53); pitcher suppresses HR (-0.88).""", blast="good"),
            row("Rhys Hoskins", "R", "+470", 78, "⭐", ["vs Skubal"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.5 mph EV. Skubal RHB split -0.53, HR risk -0.88. tough split lane (-0.53); pitcher suppresses HR (-0.88).""", blast="good"),
            row("Spencer Torkelson", "R", "+490", 65, "", ["vs Cantillo"], """0 HR, 1 near-HR, 89.0 mph EV. Cantillo RHB split +0.68, HR risk 0.71. limited recent HR events."""),
            row("Wenceel Perez", "S", "+710", 78, "🌕 💣", ["vs Cantillo"], """2 HR, 2 near-HR, 85.1 mph EV. Cantillo RHB split +0.68, HR risk 0.71. lighter EV form (85.1 mph).""", blast="high"),
            row("Riley Greene", "L", "+470", 75, "", ["vs Cantillo"], """1 HR, 1 near-HR, 92.9 mph EV. Cantillo LHB split +0.05, HR risk 0.71.""", blast="good"),
            row("Gleyber Torres", "R", "+920", 68, "", ["vs Cantillo"], """0 HR, 92.1 mph EV. Cantillo RHB split +0.68, HR risk 0.71. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "HOU @ KC - Mike Burrows 🧤 (R, HOU) vs Noah Cameron (L, KC)",
        "description": "Tail key data: Park boost +16% (stadium +12%, weather +3%). Burrows 🧤 (HR risk 1.21, vs LHB +1.36, vs RHB +0.55). Cameron (HR risk -0.72, vs LHB +0.15, vs RHB -0.61).",
        "rows": [
            row("Jac Caglianone", "L", "+425", 86, "🚀 ⭐", ["vs Burrows"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 100.0 mph EV. Burrows LHB split +1.36, HR risk 1.21.""", blast="good"),
            row("Michael Massey", "L", "+545", 79, "🌕 💣", ["vs Burrows"], """2 HR, 2 near-HR, 89.0 mph EV. Burrows LHB split +1.36, HR risk 1.21.""", blast="high"),
            row("Salvador Perez", "R", "+471", 68, "", ["vs Burrows"], """0 HR, 2 near-HR, 87.1 mph EV. Burrows RHB split +0.55, HR risk 1.21. lighter EV form (87.1 mph).""", blast="good"),
            row("Yordan Alvarez", "L", "+275", 88, "⭐ 🌕 💣", ["vs Cameron"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.8 mph EV. Cameron LHB split +0.15, HR risk -0.72. pitcher suppresses HR (-0.72).""", blast="high"),
            row("Jeremy Pena", "R", "+581", 76, "⭐", ["vs Cameron"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.5 mph EV. Cameron RHB split -0.61, HR risk -0.72. tough split lane (-0.61); pitcher suppresses HR (-0.72).""", blast="good"),
            row("Cam Smith", "R", "+680", 77, "", ["vs Cameron"], """1 HR, 1 near-HR, 95.0 mph EV. Cameron RHB split -0.61, HR risk -0.72. tough split lane (-0.61); pitcher suppresses HR (-0.72).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ CWS - Yoshinobu Yamamoto (R, LAD) vs Sean Burke (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Yamamoto (HR risk -0.52, vs LHB -1.26, vs RHB +0.20). Burke (HR risk -0.34, vs LHB -0.33, vs RHB -0.22).",
        "rows": [
            row("Colson Montgomery", "L", "+490", 80, "🌕 💣 💎", ["vs Yamamoto"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 90.0 mph EV. Yamamoto LHB split -1.26, HR risk -0.52. tough split lane (-1.26); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Miguel Vargas", "R", "+410", 84, "🌕 💣", ["vs Yamamoto"], """2 HR, 5 near-HR, 87.5 mph EV. Yamamoto RHB split +0.20, HR risk -0.52. pitcher suppresses HR (-0.52); lighter EV form (87.5 mph).""", blast="high"),
            row("Ryan Ward", "L", "+420", 77, "", ["vs Burke"], """1 HR, 2 near-HR, 93.0 mph EV. Burke LHB split -0.33, HR risk -0.34. slight split headwind (-0.33); pitcher risk below avg (-0.34).""", blast="good"),
            row("Andy Pages", "R", "+390", 62, "", ["vs Burke"], """0 HR, 86.8 mph EV. Burke RHB split -0.22, HR risk -0.34. slight split headwind (-0.22); pitcher risk below avg (-0.34)."""),
            row("Freddie Freeman", "L", "+470", 78, "🌕 💣", ["vs Burke"], """2 HR, 2 near-HR, 88.4 mph EV. Burke LHB split -0.33, HR risk -0.34. slight split headwind (-0.33); pitcher risk below avg (-0.34).""", blast="high"),
            row("Dalton Rushing", "L", "+430", 71, "", ["vs Burke"], """1 HR, 1 near-HR, 88.6 mph EV. Burke LHB split -0.33, HR risk -0.34. slight split headwind (-0.33); pitcher risk below avg (-0.34).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ PIT - Cade Gibson (L, MIA) vs Bubba Chandler (R, PIT)",
        "description": "Tail key data: Park boost -14% (stadium -15%, weather +1%). Gibson (HR risk -0.95, vs LHB -0.03, vs RHB -1.16). Chandler (HR risk -0.31, vs LHB +0.58, vs RHB -0.87).",
        "rows": [
            row("Tyler Callihan", "L", "N/A", 82, "💎", ["vs Gibson"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 97.6 mph EV. Gibson split/risk data unavailable. limited split/risk sample; park/weather net drag (-14%).""", blast="good"),
            row("Endy Rodriguez", "S", "N/A", 80, "", ["vs Gibson"], """1 HR, 2 near-HR, 95.6 mph EV. Gibson split/risk data unavailable. limited split/risk sample; park/weather net drag (-14%).""", blast="good"),
            row("Ryan O'Hearn", "L", "N/A", 82, "🌕 💣", ["vs Gibson"], """2 HR, 2 near-HR, 92.4 mph EV. Gibson split/risk data unavailable. limited split/risk sample; park/weather net drag (-14%).""", blast="high"),
            row("Kyle Stowers", "L", "N/A", 83, "🌕 💣", ["vs Chandler"], """2 HR, 3 near-HR, 90.7 mph EV. Chandler LHB split +0.58, HR risk -0.31. pitcher risk below avg (-0.31); park/weather net drag (-14%).""", blast="high"),
            row("Owen Caissie", "L", "N/A", 74, "", ["vs Chandler"], """1 HR, 1 near-HR, 91.8 mph EV. Chandler LHB split +0.58, HR risk -0.31. pitcher risk below avg (-0.31); park/weather net drag (-14%).""", blast="good"),
            row("Heriberto Hernandez", "R", "N/A", 71, "", ["vs Chandler"], """0 HR, 95.0 mph EV. Chandler RHB split -0.87, HR risk -0.31. tough split lane (-0.87); pitcher risk below avg (-0.31).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ TOR - Cam Schlittler (R, NYY) vs Kevin Gausman (R, TOR)",
        "description": "Tail key data: Park boost +23% (stadium +7%, weather +16%). Schlittler (HR risk -0.38, vs LHB -0.42, vs RHB -0.28). Gausman (HR risk -0.21, vs LHB -0.34, vs RHB +0.02).",
        "rows": [
            row("Jesus Sanchez", "L", "+520", 87, "🌕 💣", ["vs Schlittler"], """2 HR, 3 near-HR, 94.7 mph EV. Schlittler LHB split -0.42, HR risk -0.38. tough split lane (-0.42); pitcher risk below avg (-0.38).""", blast="high"),
            row("Brandon Valenzuela", "S", "+630", 77, "", ["vs Schlittler"], """1 HR, 3 near-HR, 91.1 mph EV. Schlittler RHB split -0.28, HR risk -0.38. slight split headwind (-0.28); pitcher risk below avg (-0.38).""", blast="good"),
            row("Ben Rice", "L", "+310", 66, "💎", ["vs Gausman"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 90.4 mph EV. Gausman LHB split -0.34, HR risk -0.21. slight split headwind (-0.34); pitcher risk below avg (-0.21)."""),
            row("Ryan McMahon", "L", "+590", 70, "", ["vs Gausman"], """1 HR, 1 near-HR, 78.0 mph EV. Gausman LHB split -0.34, HR risk -0.21. slight split headwind (-0.34); pitcher risk below avg (-0.21).""", blast="good"),
            row("Cody Bellinger", "L", "+520", 72, "", ["vs Gausman"], """1 HR, 1 near-HR, 89.5 mph EV. Gausman LHB split -0.34, HR risk -0.21. slight split headwind (-0.34); pitcher risk below avg (-0.21).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ MIL - Aaron Nola (R, PHI) vs Shane Drohan (L, MIL)",
        "description": "Tail key data: Park boost +6% (stadium +10%, weather -4%). Nola (HR risk 0.35, vs LHB +0.55, vs RHB +0.10). Drohan (HR risk 0.15, vs LHB -0.93, vs RHB +0.64).",
        "rows": [
            row("Jake Bauers", "L", "+409", 96, "🚀 ⭐ 🌕 💣", ["vs Nola"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 101.4 mph EV. Nola LHB split +0.55, HR risk 0.35. weather carry headwind (-4%).""", blast="high"),
            row("Gary Sanchez", "R", "N/A", 78, "", ["vs Nola"], """1 HR, 2 near-HR, 93.9 mph EV. Nola RHB split +0.10, HR risk 0.35. weather carry headwind (-4%).""", blast="good"),
            row("Jackson Chourio", "R", "+422", 95, "🌕 💣", ["vs Nola"], """4 HR, 4 near-HR, 92.9 mph EV. Nola RHB split +0.10, HR risk 0.35. weather carry headwind (-4%).""", blast="high"),
            row("Garrett Mitchell", "L", "+630", 72, "", ["vs Nola"], """0 HR, 3 near-HR, 90.2 mph EV. Nola LHB split +0.55, HR risk 0.35. weather carry headwind (-4%).""", blast="good"),
            row("Kyle Schwarber", "L", "+268", 85, "⭐ 🌕 💣", ["vs Drohan"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.9 mph EV. Drohan LHB split -0.93, HR risk 0.15. tough split lane (-0.93); weather carry headwind (-4%).""", blast="high"),
            row("Brandon Marsh", "L", "+900", 76, "💎", ["vs Drohan"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.0 mph EV. Drohan LHB split -0.93, HR risk 0.15. tough split lane (-0.93); weather carry headwind (-4%).""", blast="good"),
            row("Edmundo Sosa", "R", "+600", 70, "", ["vs Drohan"], """1 HR, 1 near-HR, 87.2 mph EV. Drohan RHB split +0.64, HR risk 0.15. weather carry headwind (-4%); lighter EV form (87.2 mph).""", blast="good"),
        ],
    },
    {
        "title": "SD @ BAL - Randy Vasquez 🧤 (R, SD) vs Trey Gibson (R, BAL)",
        "description": "Tail key data: Park boost -3% (stadium -2%, weather -1%). Vasquez 🧤 (HR risk 1.18, vs LHB +0.40, vs RHB +1.34). Gibson (HR risk 0.34, vs LHB +0.02, vs RHB +0.39).",
        "rows": [
            row("Colton Cowser", "L", "+245", 73, "", ["vs Vasquez"], """1 HR, 2 near-HR, 89.2 mph EV. Vasquez LHB split +0.40, HR risk 1.18.""", blast="good"),
            row("Pete Alonso", "R", "+174", 83, "🌕 💣", ["vs Vasquez"], """2 HR, 2 near-HR, 92.6 mph EV. Vasquez RHB split +1.34, HR risk 1.18.""", blast="high"),
            row("Blaze Alexander", "R", "N/A", 74, "", ["vs Vasquez"], """1 HR, 1 near-HR, 92.0 mph EV. Vasquez RHB split +1.34, HR risk 1.18.""", blast="good"),
            row("Adley Rutschman", "S", "+211", 76, "", ["vs Vasquez"], """1 HR, 1 near-HR, 94.3 mph EV. Vasquez RHB split +1.34, HR risk 1.18.""", blast="good"),
            row("Samuel Basallo", "L", "+155", 84, "⭐", ["vs Vasquez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 99.8 mph EV. Vasquez LHB split +0.40, HR risk 1.18.""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+275", 81, "", ["vs Gibson"], """1 HR, 2 near-HR, 97.4 mph EV. Gibson split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Manny Machado", "R", "+279", 65, "", ["vs Gibson"], """0 HR, 90.8 mph EV. Gibson split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
        ],
    },
    {
        "title": "SEA @ WSH - Luis Castillo (R, SEA) vs Cade Cavalli (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Castillo (HR risk 0.07, vs LHB +0.77, vs RHB -0.72). Cavalli (HR risk -0.19, vs LHB -0.38, vs RHB +0.02).",
        "rows": [
            row("James Wood", "L", "N/A", 74, "⭐", ["vs Castillo"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 90.3 mph EV. Castillo LHB split +0.77, HR risk 0.07.""", blast="good"),
            row("CJ Abrams", "L", "N/A", 65, "", ["vs Castillo"], """0 HR, 91.4 mph EV. Castillo LHB split +0.77, HR risk 0.07. limited recent HR events."""),
            row("Luis Garcia Jr.", "L", "N/A", 72, "", ["vs Castillo"], """1 HR, 2 near-HR, 88.1 mph EV. Castillo LHB split +0.77, HR risk 0.07.""", blast="good"),
            row("Dylan Crews", "R", "N/A", 68, "", ["vs Castillo"], """0 HR, 1 near-HR, 91.9 mph EV. Castillo RHB split -0.72, HR risk 0.07. tough split lane (-0.72); limited recent HR events."""),
            row("Dominic Canzone", "L", "N/A", 82, "⭐", ["vs Cavalli"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.5 mph EV. Cavalli LHB split -0.38, HR risk -0.19. slight split headwind (-0.38); pitcher risk below avg (-0.19).""", blast="good"),
            row("Luke Raley", "L", "N/A", 73, "", ["vs Cavalli"], """1 HR, 2 near-HR, 89.0 mph EV. Cavalli LHB split -0.38, HR risk -0.19. slight split headwind (-0.38); pitcher risk below avg (-0.19).""", blast="good"),
            row("Patrick Wisdom", "R", "N/A", 64, "", ["vs Cavalli"], """0 HR, 89.6 mph EV. Cavalli RHB split +0.02, HR risk -0.19. pitcher risk below avg (-0.19); limited recent HR events."""),
        ],
    },
    {
        "title": "STL @ MIN - Matthew Liberatore (L, STL) vs Connor Prielipp (L, MIN)",
        "description": "Tail key data: Park boost +8% (stadium -6%, weather +13%). Liberatore (HR risk 0.32, vs LHB +1.62, vs RHB -0.04). Prielipp (HR risk -0.64, vs LHB -0.16, vs RHB -0.49).",
        "rows": [
            row("Kody Clemens", "L", "N/A", 76, "", ["vs Liberatore"], """1 HR, 1 near-HR, 94.0 mph EV. Liberatore LHB split +1.62, HR risk 0.32. park suppresses carry (-6%).""", blast="good"),
            row("Tristan Gray", "L", "N/A", 71, "", ["vs Liberatore"], """1 HR, 1 near-HR, 88.9 mph EV. Liberatore LHB split +1.62, HR risk 0.32. park suppresses carry (-6%).""", blast="good"),
            row("Byron Buxton", "R", "N/A", 77, "", ["vs Liberatore"], """1 HR, 2 near-HR, 93.1 mph EV. Liberatore RHB split -0.04, HR risk 0.32. slight split headwind (-0.04); park suppresses carry (-6%).""", blast="good"),
            row("Jimmy Crooks", "L", "N/A", 78, "🚀 💎", ["vs Prielipp"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 103.9 mph EV. Prielipp LHB split -0.16, HR risk -0.64. slight split headwind (-0.16); pitcher suppresses HR (-0.64).""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 84, "🚀", ["vs Prielipp"], """1 HR, 2 near-HR, 100.6 mph EV. Prielipp RHB split -0.49, HR risk -0.64. tough split lane (-0.49); pitcher suppresses HR (-0.64).""", blast="good"),
            row("Alec Burleson", "L", "N/A", 62, "", ["vs Prielipp"], """0 HR, 86.1 mph EV. Prielipp LHB split -0.16, HR risk -0.64. slight split headwind (-0.16); pitcher suppresses HR (-0.64)."""),
            row("Jordan Walker", "R", "N/A", 76, "", ["vs Prielipp"], """1 HR, 1 near-HR, 94.1 mph EV. Prielipp RHB split -0.49, HR risk -0.64. tough split lane (-0.49); pitcher suppresses HR (-0.64).""", blast="good"),
        ],
    },
    {
        "title": "TB @ LAA - Griffin Jax (R, TB) vs Jose Soriano (R, LAA)",
        "description": "Tail key data: Park boost +7% (stadium +7%, weather +0%). Jax (HR risk 0.63, vs LHB +0.25, vs RHB +0.81). Soriano (HR risk 0.06, vs LHB +0.16, vs RHB +0.02).",
        "rows": [
            row("Mike Trout", "R", "+360", 84, "⭐", ["vs Jax"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 98.0 mph EV. Jax RHB split +0.81, HR risk 0.63.""", blast="good"),
            row("Logan O'Hoppe", "R", "+570", 78, "🌕 💣", ["vs Jax"], """2 HR, 2 near-HR, 86.7 mph EV. Jax RHB split +0.81, HR risk 0.63. lighter EV form (86.7 mph).""", blast="high"),
            row("Cedric Mullins", "L", "+660", 96, "⭐ 🌕 💣", ["vs Soriano"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 98.4 mph EV. Soriano LHB split +0.16, HR risk 0.06.""", blast="high"),
            row("Jonathan Aranda", "L", "+516", 75, "", ["vs Soriano"], """1 HR, 1 near-HR, 93.1 mph EV. Soriano LHB split +0.16, HR risk 0.06.""", blast="good"),
        ],
    },
    {
        "title": "TEX @ BOS - Jacob deGrom (R, TEX) vs Ranger Suarez (L, BOS)",
        "description": "Tail key data: Park boost +2% (stadium -7%, weather +9%). deGrom (HR risk 0.98, vs LHB +0.96, vs RHB +0.59). Suarez (HR risk -1.03, vs LHB -0.16, vs RHB -0.90).",
        "rows": [
            row("Wilyer Abreu", "L", "+410", 74, "", ["vs deGrom"], """1 HR, 1 near-HR, 92.5 mph EV. deGrom LHB split +0.96, HR risk 0.98. park suppresses carry (-7%).""", blast="good"),
            row("Jarren Duran", "L", "+440", 70, "", ["vs deGrom"], """1 HR, 1 near-HR, 88.5 mph EV. deGrom LHB split +0.96, HR risk 0.98. park suppresses carry (-7%).""", blast="good"),
            row("Caleb Durbin", "R", "+980", 70, "", ["vs deGrom"], """1 HR, 1 near-HR, 84.1 mph EV. deGrom RHB split +0.59, HR risk 0.98. park suppresses carry (-7%); lighter EV form (84.1 mph).""", blast="good"),
            row("Justin Foscue", "R", "+590", 91, "⭐ 🌕 💣", ["vs Suarez"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 98.8 mph EV. Suarez RHB split -0.90, HR risk -1.03. tough split lane (-0.90); pitcher suppresses HR (-1.03).""", blast="high"),
            row("Kyle Higashioka", "R", "+540", 74, "", ["vs Suarez"], """1 HR, 2 near-HR, 90.5 mph EV. Suarez RHB split -0.90, HR risk -1.03. tough split lane (-0.90); pitcher suppresses HR (-1.03).""", blast="good"),
            row("Joc Pederson", "L", "+490", 78, "🚀 💎", ["vs Suarez"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 101.5 mph EV. Suarez LHB split -0.16, HR risk -1.03. slight split headwind (-0.16); pitcher suppresses HR (-1.03).""", blast="good"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-13")

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

    out = ROOT / '_games-0613.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
