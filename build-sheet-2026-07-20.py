#!/usr/bin/env python3
"""Generate games[] block for 2026-07-20 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Chase DeLauter (L)",
    "Coby Mayo (R)",
    "Colt Keith (L)",
    "Corbin Carroll (L)",
    "Esmerlyn Valdez (R)",
    "Eugenio Suarez (R)",
    "Griffin Conine (L)",
    "Hunter Goodman (R)",
    "Jazz Chisholm Jr. (L)",
    "Juan Soto (L)",
    "Kyle Stowers (L)",
    "Riley Greene (L)",
    "Shea Langeliers (R)",
    "Ty France (R)",
    "Tyler O'Neill (R)",
    "Vaughn Grissom (R)",
    "Willson Contreras (R)",
    "Wilyer Abreu (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Brett Baty (L)",
    "Derek Hill (R)",
    "Kazuma Okamoto (R)",
    "Lane Thomas (R)",
    "Lars Nootbaar (L)",
    "Miguel Vargas (R)",
    "Teoscar Hernandez (R)",
}

PLAYER_TEAMS = {
    "Alec Bohm (R)": "PHI",
    "Alex Bregman (R)": "CHC",
    "Andruw Monasterio (R)": "BOS",
    "Andy Pages (R)": "LAD",
    "Austin Hedges (R)": "CLE",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Braden Shewmake (L)": "MIL",
    "Brandon Valenzuela (S)": "TOR",
    "Brett Baty (L)": "NYM",
    "Brice Turang (L)": "MIL",
    "Bryce Eldridge (L)": "SF",
    "Bryson Stott (L)": "PHI",
    "Cam Smith (R)": "HOU",
    "Carter Jensen (L)": "KC",
    "Chase DeLauter (L)": "CLE",
    "Christian Walker (R)": "HOU",
    "Coby Mayo (R)": "BAL",
    "Cole Young (L)": "SEA",
    "Colt Emerson (L)": "SEA",
    "Colt Keith (L)": "DET",
    "Corbin Carroll (L)": "ARI",
    "Curtis Mead (R)": "WSH",
    "Daulton Varsho (L)": "TOR",
    "Derek Hill (R)": "PHI",
    "Dominic Canzone (L)": "SEA",
    "Dylan Crews (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Lindor (S)": "NYM",
    "Griffin Conine (L)": "MIA",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "TB",
    "Hunter Goodman (R)": "COL",
    "JJ Wetherholt (L)": "STL",
    "James Wood (L)": "WSH",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jonah Heim (S)": "ATH",
    "Jonathan Aranda (L)": "TB",
    "Jorge Soler (R)": "LAA",
    "Jose Altuve (R)": "HOU",
    "Josh Bell (S)": "MIN",
    "Josh Jung (R)": "TEX",
    "Josh Naylor (L)": "SEA",
    "Juan Soto (L)": "NYM",
    "Kazuma Okamoto (R)": "TOR",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lane Thomas (R)": "KC",
    "Lars Nootbaar (L)": "STL",
    "Logan O'Hoppe (R)": "LAA",
    "Luis Campusano (R)": "SD",
    "Michael Harris II (L)": "ATL",
    "Miguel Amaya (R)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Mitch Garver (R)": "SEA",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "STL",
    "Patrick Bailey (S)": "CLE",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Royce Lewis (R)": "MIN",
    "Ryan Jeffers (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Ryan O'Hearn (L)": "PIT",
    "Ryan Waldschmidt (R)": "ARI",
    "Sam Antonacci (L)": "CWS",
    "Seiya Suzuki (R)": "CHC",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Steer (R)": "CIN",
    "Spencer Torkelson (R)": "DET",
    "Taylor Ward (R)": "BAL",
    "Teoscar Hernandez (R)": "LAD",
    "Trent Grisham (L)": "NYY",
    "Tristan Peters (L)": "CWS",
    "Ty France (R)": "SD",
    "Tyler Freeman (R)": "COL",
    "Tyler O'Neill (R)": "BAL",
    "Vaughn Grissom (R)": "LAA",
    "Victor Mesa Jr. (L)": "TB",
    "Vinnie Pasquantino (L)": "KC",
    "Weston Wilson (R)": "SEA",
    "William Contreras (R)": "MIL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("ATH @ ARI", "Springs"),
    ("DET @ CHC", "Taillon"),
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
        "title": "ATH @ ARI - Jeffrey Springs 🧤 (L, ATH) vs Mitch Bratt (L, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -7%, weather -1%). Springs 🧤 (HR risk 1.36, vs LHB -0.49, vs RHB +1.75). Home starter risk unavailable.",
        "rows": [
            row("Corbin Carroll", "L", "+440", 71, "⭐", ["vs Springs"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 93.6 mph EV. Springs LHB split -0.49, HR risk 1.36. tough split lane (-0.49); park/weather net drag (-8%).""", blast="good"),
            row("Ryan Waldschmidt", "R", "+870", 85, "", ["vs Springs"], """0 HR, 2 near-HR, 89.4 mph EV. Springs RHB split +1.75, HR risk 1.36. park/weather net drag (-8%).""", blast="good"),
            row("Henry Bolte", "R", "+820", 70, "🌕 💣", ["vs Bratt"], """2 HR, 2 near-HR, 92.1 mph EV. Bratt split/risk data unavailable. limited split/risk sample; park/weather net drag (-8%).""", blast="high"),
            row("Jonah Heim", "S", "+630", 72, "🌕 💣", ["vs Bratt"], """2 HR, 3 near-HR, 89.5 mph EV. Bratt split/risk data unavailable. limited split/risk sample; park/weather net drag (-8%).""", blast="high"),
            row("Shea Langeliers", "R", "+340", 66, "⭐", ["vs Bratt"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.3 mph EV. Bratt split/risk data unavailable. limited split/risk sample; park/weather net drag (-8%).""", blast="good"),
        ],
    },
    {
        "title": "BAL @ BOS - Shane Baz (R, BAL) vs Payton Tolle (L, BOS)",
        "description": "Tail key data: Park boost -1% (stadium -7%, weather +5%). Baz (HR risk -0.71, vs LHB -0.55, vs RHB -0.41). Tolle (HR risk 0.09, vs LHB -0.21, vs RHB +0.34).",
        "rows": [
            row("Willson Contreras", "R", "+375", 72, "🚀 ⭐ 🌕 💣", ["vs Baz"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 100.4 mph EV. Baz RHB split -0.41, HR risk -0.71. tough split lane (-0.41); pitcher suppresses HR (-0.71).""", blast="high"),
            row("Wilyer Abreu", "L", "+402", 67, "⭐ 🌕 💣", ["vs Baz"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.9 mph EV. Baz LHB split -0.55, HR risk -0.71. tough split lane (-0.55); pitcher suppresses HR (-0.71).""", blast="high"),
            row("Andruw Monasterio", "R", "N/A", 58, "", ["vs Baz"], """1 HR, 1 near-HR, 88.2 mph EV. Baz RHB split -0.41, HR risk -0.71. tough split lane (-0.41); pitcher suppresses HR (-0.71).""", blast="good"),
            row("Tyler O'Neill", "R", "+425", 82, "🚀 ⭐ 🌕 💣", ["vs Tolle"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 100.3 mph EV. Tolle RHB split +0.34, HR risk 0.09. park suppresses carry (-7%).""", blast="high"),
            row("Taylor Ward", "R", "+640", 63, "", ["vs Tolle"], """1 HR, 1 near-HR, 90.8 mph EV. Tolle RHB split +0.34, HR risk 0.09. park suppresses carry (-7%).""", blast="good"),
            row("Coby Mayo", "R", "+500", 85, "⭐ 🌕 💣", ["vs Tolle"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 96.8 mph EV. Tolle RHB split +0.34, HR risk 0.09. park suppresses carry (-7%).""", blast="high"),
        ],
    },
    {
        "title": "CIN @ SEA - Andrew Abbott (L, CIN) vs George Kirby (R, SEA)",
        "description": "Tail key data: Park boost +3% (stadium +1%, weather +2%). Abbott (HR risk 0.18, vs LHB -0.27, vs RHB +0.37). Kirby (HR risk 0.08, vs LHB +0.03, vs RHB +0.16).",
        "rows": [
            row("Josh Naylor", "L", "+760", 61, "", ["vs Abbott"], """0 HR, 1 near-HR, 96.7 mph EV. Abbott LHB split -0.27, HR risk 0.18. slight split headwind (-0.27); limited recent HR events.""", blast="good"),
            row("Dominic Canzone", "L", "N/A", 74, "🚀 🌕 💣", ["vs Abbott"], """2 HR, 2 near-HR, 100.2 mph EV. Abbott LHB split -0.27, HR risk 0.18. slight split headwind (-0.27).""", blast="high"),
            row("Cole Young", "L", "+780", 64, "", ["vs Abbott"], """1 HR, 1 near-HR, 95.6 mph EV. Abbott LHB split -0.27, HR risk 0.18. slight split headwind (-0.27).""", blast="good"),
            row("Colt Emerson", "L", "+900", 58, "", ["vs Abbott"], """1 HR, 1 near-HR, 86.5 mph EV. Abbott LHB split -0.27, HR risk 0.18. slight split headwind (-0.27); lighter EV form (86.5 mph).""", blast="good"),
            row("Mitch Garver", "R", "+457", 64, "", ["vs Abbott"], """1 HR, 1 near-HR, 89.7 mph EV. Abbott RHB split +0.37, HR risk 0.18.""", blast="good"),
            row("Weston Wilson", "R", "+500", 76, "🌕 💣", ["vs Abbott"], """2 HR, 2 near-HR, 92.9 mph EV. Abbott RHB split +0.37, HR risk 0.18.""", blast="high"),
            row("Spencer Steer", "R", "+560", 67, "🌕 💣", ["vs Kirby"], """2 HR, 2 near-HR, 84.5 mph EV. Kirby RHB split +0.16, HR risk 0.08. lighter EV form (84.5 mph).""", blast="high"),
            row("Eugenio Suarez", "R", "+541", 85, "⭐ 🌕 💣", ["vs Kirby"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 97.8 mph EV. Kirby RHB split +0.16, HR risk 0.08.""", blast="high"),
            row("Elly De La Cruz", "S", "+475", 63, "", ["vs Kirby"], """0 HR, 1 near-HR, 95.4 mph EV. Kirby SHB→RHB split +0.16, HR risk 0.08. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ TEX - Erick Fedde (R, CWS) vs Jacob deGrom (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -10%, weather -1%). Fedde (HR risk -0.63, vs LHB -0.76, vs RHB +0.20). deGrom (HR risk -0.01, vs LHB -0.15, vs RHB +0.19).",
        "rows": [
            row("Josh Jung", "R", "+610", 58, "", ["vs Fedde"], """0 HR, 93.5 mph EV. Fedde RHB split +0.20, HR risk -0.63. pitcher suppresses HR (-0.63); park/weather net drag (-11%).""", blast="good"),
            row("Munetaka Murakami", "L", "+300", 70, "🌕 💣", ["vs deGrom"], """2 HR, 2 near-HR, 97.8 mph EV. deGrom LHB split -0.15, HR risk -0.01. slight split headwind (-0.15); pitcher risk below avg (-0.01).""", blast="high"),
            row("Sam Antonacci", "L", "+775", 61, "🌕 💣", ["vs deGrom"], """2 HR, 2 near-HR, 87.5 mph EV. deGrom LHB split -0.15, HR risk -0.01. slight split headwind (-0.15); pitcher risk below avg (-0.01).""", blast="high"),
            row("Tristan Peters", "L", "+900", 58, "", ["vs deGrom"], """1 HR, 1 near-HR, 93.8 mph EV. deGrom LHB split -0.15, HR risk -0.01. slight split headwind (-0.15); pitcher risk below avg (-0.01).""", blast="good"),
            row("Miguel Vargas", "R", "+425", 58, "💎", ["vs deGrom"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.4 mph EV. deGrom RHB split +0.19, HR risk -0.01. pitcher risk below avg (-0.01); park/weather net drag (-11%).""", blast="good"),
            row("Randal Grichuk", "R", "N/A", 58, "", ["vs deGrom"], """0 HR, 1 near-HR, 90.1 mph EV. deGrom RHB split +0.19, HR risk -0.01. pitcher risk below avg (-0.01); park/weather net drag (-11%)."""),
        ],
    },
    {
        "title": "DET @ CHC - Jack Flaherty (R, DET) vs Jameson Taillon 🧤 (R, CHC)",
        "description": "Tail key data: Park boost +48% (stadium -1%, weather +48%). Flaherty (HR risk -0.35, vs LHB -0.55, vs RHB +0.36). Taillon 🧤 (HR risk 2.03, vs LHB +1.76, vs RHB +1.24).",
        "rows": [
            row("Alex Bregman", "R", "+399", 83, "🌕 💣", ["vs Flaherty"], """2 HR, 2 near-HR, 95.4 mph EV. Flaherty RHB split +0.36, HR risk -0.35. pitcher risk below avg (-0.35).""", blast="high"),
            row("Pete Crow-Armstrong", "L", "+212", 61, "", ["vs Flaherty"], """1 HR, 1 near-HR, 90.4 mph EV. Flaherty LHB split -0.55, HR risk -0.35. tough split lane (-0.55); pitcher risk below avg (-0.35).""", blast="good"),
            row("Seiya Suzuki", "R", "+270", 59, "", ["vs Flaherty"], """0 HR, 1 near-HR, 88.4 mph EV. Flaherty RHB split +0.36, HR risk -0.35. pitcher risk below avg (-0.35); limited recent HR events."""),
            row("Miguel Amaya", "R", "N/A", 69, "", ["vs Flaherty"], """0 HR, 1 near-HR, 94.8 mph EV. Flaherty RHB split +0.36, HR risk -0.35. pitcher risk below avg (-0.35); limited recent HR events.""", blast="good"),
            row("Colt Keith", "L", "+423", 99, "⭐ 🌕 💣", ["vs Taillon"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.6 mph EV. Taillon LHB split +1.76, HR risk 2.03.""", blast="high"),
            row("Riley Greene", "L", "+217", 95, "⭐ 🌕 💣", ["vs Taillon"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 90.5 mph EV. Taillon LHB split +1.76, HR risk 2.03.""", blast="good"),
            row("Spencer Torkelson", "R", "+258", 99, "🌕 💣", ["vs Taillon"], """2 HR, 3 near-HR, 92.1 mph EV. Taillon RHB split +1.24, HR risk 2.03.""", blast="high"),
        ],
    },
    {
        "title": "LAD @ PHI - Emmet Sheehan (R, LAD) vs Cristopher Sanchez (L, PHI)",
        "description": "Tail key data: Park boost +22% (stadium +14%, weather +8%). Sheehan (HR risk 0.44, vs LHB +0.41, vs RHB +0.25). Sanchez (HR risk 0.16, vs LHB -1.21, vs RHB +0.64).",
        "rows": [
            row("Derek Hill", "R", "N/A", 79, "🚀 💎", ["vs Sheehan"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 100.4 mph EV. Sheehan RHB split +0.25, HR risk 0.44.""", blast="good"),
            row("Alec Bohm", "R", "+630", 66, "", ["vs Sheehan"], """0 HR, 1 near-HR, 91.5 mph EV. Sheehan RHB split +0.25, HR risk 0.44. limited recent HR events."""),
            row("Bryson Stott", "L", "+533", 76, "", ["vs Sheehan"], """0 HR, 1 near-HR, 96.0 mph EV. Sheehan LHB split +0.41, HR risk 0.44. limited recent HR events.""", blast="good"),
            row("Kyle Schwarber", "L", "+184", 74, "", ["vs Sheehan"], """0 HR, 1 near-HR, 93.5 mph EV. Sheehan LHB split +0.41, HR risk 0.44. limited recent HR events.""", blast="good"),
            row("Teoscar Hernandez", "R", "+576", 69, "💎", ["vs Sanchez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 88.5 mph EV. Sanchez RHB split +0.64, HR risk 0.16.""", blast="good"),
            row("Andy Pages", "R", "+533", 80, "🌕 💣", ["vs Sanchez"], """2 HR, 2 near-HR, 89.6 mph EV. Sanchez RHB split +0.64, HR risk 0.16.""", blast="high"),
            row("Shohei Ohtani", "L", "+430", 71, "🌕 💣", ["vs Sanchez"], """2 HR, 2 near-HR, 90.7 mph EV. Sanchez LHB split -1.21, HR risk 0.16. tough split lane (-1.21).""", blast="high"),
        ],
    },
    {
        "title": "MIA @ HOU - Janson Junk (R, MIA) vs Ronel Blanco (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +6%, weather -1%). Junk (HR risk 0.29, vs LHB -0.05, vs RHB +0.60). Blanco (HR risk -0.13, vs LHB +0.78, vs RHB -0.67).",
        "rows": [
            row("Yordan Alvarez", "L", "+240", 67, "⭐", ["vs Junk"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.1 mph EV. Junk LHB split -0.05, HR risk 0.29. slight split headwind (-0.05).""", blast="good"),
            row("Cam Smith", "R", "+578", 71, "", ["vs Junk"], """1 HR, 3 near-HR, 88.2 mph EV. Junk RHB split +0.60, HR risk 0.29.""", blast="good"),
            row("Christian Walker", "R", "+350", 69, "", ["vs Junk"], """1 HR, 2 near-HR, 90.3 mph EV. Junk RHB split +0.60, HR risk 0.29.""", blast="good"),
            row("Jose Altuve", "R", "+620", 73, "🌕 💣", ["vs Junk"], """2 HR, 2 near-HR, 86.5 mph EV. Junk RHB split +0.60, HR risk 0.29. lighter EV form (86.5 mph).""", blast="high"),
            row("Griffin Conine", "L", "+470", 83, "⭐ 🌕 💣", ["vs Blanco"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 90.6 mph EV. Blanco LHB split +0.78, HR risk -0.13. pitcher risk below avg (-0.13).""", blast="high"),
            row("Kyle Stowers", "L", "+330", 80, "⭐ 🌕 💣", ["vs Blanco"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 99.2 mph EV. Blanco LHB split +0.78, HR risk -0.13. pitcher risk below avg (-0.13).""", blast="high"),
            row("Heriberto Hernandez", "R", "+375", 58, "", ["vs Blanco"], """0 HR, 92.3 mph EV. Blanco RHB split -0.67, HR risk -0.13. tough split lane (-0.67); pitcher risk below avg (-0.13).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ CLE - Joe Ryan (R, MIN) vs Tanner Bibee (R, CLE)",
        "description": "Tail key data: Park boost -6% (stadium -2%, weather -4%). Ryan (HR risk -0.10, vs LHB +0.14, vs RHB -0.32). Bibee (HR risk 0.10, vs LHB +0.45, vs RHB -0.46).",
        "rows": [
            row("Chase DeLauter", "L", "+455", 58, "⭐", ["vs Ryan"], """Worst Pickz Favorite. 0 HR, 90.8 mph EV. Ryan LHB split +0.14, HR risk -0.10. pitcher risk below avg (-0.10); park/weather net drag (-6%)."""),
            row("Austin Hedges", "R", "N/A", 64, "🌕 💣", ["vs Ryan"], """2 HR, 2 near-HR, 90.9 mph EV. Ryan RHB split -0.32, HR risk -0.10. slight split headwind (-0.32); pitcher risk below avg (-0.10).""", blast="high"),
            row("Patrick Bailey", "S", "+875", 58, "", ["vs Ryan"], """0 HR, 94.9 mph EV. Ryan SHB→LHB split +0.14, HR risk -0.10. pitcher risk below avg (-0.10); park/weather net drag (-6%).""", blast="good"),
            row("Rhys Hoskins", "R", "+314", 58, "", ["vs Ryan"], """0 HR, 89.7 mph EV. Ryan RHB split -0.32, HR risk -0.10. slight split headwind (-0.32); pitcher risk below avg (-0.10)."""),
            row("Royce Lewis", "R", "+393", 58, "", ["vs Bibee"], """1 HR, 1 near-HR, 93.2 mph EV. Bibee RHB split -0.46, HR risk 0.10. tough split lane (-0.46); park/weather net drag (-6%).""", blast="good"),
            row("Josh Bell", "S", "+420", 62, "", ["vs Bibee"], """0 HR, 96.9 mph EV. Bibee SHB→LHB split +0.45, HR risk 0.10. park/weather net drag (-6%); limited recent HR events.""", blast="good"),
            row("Ryan Jeffers", "R", "+439", 58, "", ["vs Bibee"], """0 HR, 1 near-HR, 93.8 mph EV. Bibee RHB split -0.46, HR risk 0.10. tough split lane (-0.46); park/weather net drag (-6%).""", blast="good"),
        ],
    },
    {
        "title": "NYM @ MIL - Freddy Peralta (R, NYM) vs Jacob Misiorowski (R, MIL)",
        "description": "Tail key data: Park boost +22% (stadium +9%, weather +13%). Peralta (HR risk 0.10, vs LHB +0.36, vs RHB -0.46). Misiorowski (HR risk -0.30, vs LHB -1.06, vs RHB +1.09).",
        "rows": [
            row("Brice Turang", "L", "+470", 70, "", ["vs Peralta"], """0 HR, 1 near-HR, 96.3 mph EV. Peralta LHB split +0.36, HR risk 0.10. limited recent HR events.""", blast="good"),
            row("Braden Shewmake", "L", "N/A", 61, "", ["vs Peralta"], """0 HR, 2 near-HR, 81.5 mph EV. Peralta LHB split +0.36, HR risk 0.10. lighter EV form (81.5 mph).""", blast="good"),
            row("William Contreras", "R", "+585", 60, "", ["vs Peralta"], """0 HR, 1 near-HR, 93.0 mph EV. Peralta RHB split -0.46, HR risk 0.10. tough split lane (-0.46); limited recent HR events.""", blast="good"),
            row("Juan Soto", "L", "+295", 58, "⭐", ["vs Misiorowski"], """Worst Pickz Favorite. 0 HR, 92.2 mph EV. Misiorowski LHB split -1.06, HR risk -0.30. tough split lane (-1.06); pitcher risk below avg (-0.30).""", blast="good"),
            row("Francisco Lindor", "S", "+485", 75, "", ["vs Misiorowski"], """1 HR, 1 near-HR, 95.4 mph EV. Misiorowski SHB→RHB split +1.09, HR risk -0.30. pitcher risk below avg (-0.30).""", blast="good"),
            row("Brett Baty", "L", "N/A", 58, "💎", ["vs Misiorowski"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 85.2 mph EV. Misiorowski LHB split -1.06, HR risk -0.30. tough split lane (-1.06); pitcher risk below avg (-0.30).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ NYY - Braxton Ashcraft (R, PIT) vs Ryan Weathers (L, NYY)",
        "description": "Tail key data: Park boost +1% (stadium +2%, weather -1%). Ashcraft (HR risk 0.11, vs LHB +0.48, vs RHB -0.65). Weathers (HR risk -0.25, vs LHB +0.31, vs RHB -0.37).",
        "rows": [
            row("Trent Grisham", "L", "+340", 71, "", ["vs Ashcraft"], """1 HR, 2 near-HR, 96.4 mph EV. Ashcraft LHB split +0.48, HR risk 0.11.""", blast="good"),
            row("Ben Rice", "L", "+270", 69, "⭐", ["vs Ashcraft"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.9 mph EV. Ashcraft LHB split +0.48, HR risk 0.11.""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "+390", 70, "⭐", ["vs Ashcraft"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.8 mph EV. Ashcraft LHB split +0.48, HR risk 0.11.""", blast="good"),
            row("Ryan McMahon", "L", "+525", 66, "", ["vs Ashcraft"], """1 HR, 1 near-HR, 92.2 mph EV. Ashcraft LHB split +0.48, HR risk 0.11.""", blast="good"),
            row("Ryan O'Hearn", "L", "+670", 58, "", ["vs Weathers"], """0 HR, 1 near-HR, 90.8 mph EV. Weathers LHB split +0.31, HR risk -0.25. pitcher risk below avg (-0.25); limited recent HR events."""),
            row("Esmerlyn Valdez", "R", "+316", 69, "🚀 ⭐ 🌕 💣", ["vs Weathers"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 102.0 mph EV. Weathers RHB split -0.37, HR risk -0.25. slight split headwind (-0.37); pitcher risk below avg (-0.25).""", blast="high"),
        ],
    },
    {
        "title": "SD @ ATL - JP Sears (L, SD) vs Bryce Elder (R, ATL)",
        "description": "Tail key data: Park boost +3% (stadium -5%, weather +8%). Sears (HR risk 0.80, vs LHB +0.72, vs RHB +0.65). Elder (HR risk 0.90, vs LHB +0.50, vs RHB +0.80).",
        "rows": [
            row("Austin Riley", "R", "+461", 76, "", ["vs Sears"], """0 HR, 1 near-HR, 95.0 mph EV. Sears RHB split +0.65, HR risk 0.80. limited recent HR events.""", blast="good"),
            row("Michael Harris II", "L", "+498", 76, "", ["vs Sears"], """0 HR, 1 near-HR, 94.8 mph EV. Sears LHB split +0.72, HR risk 0.80. limited recent HR events.""", blast="good"),
            row("Ty France", "R", "+600", 93, "🚀 ⭐ 🌕 💣", ["vs Elder"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 103.2 mph EV. Elder RHB split +0.80, HR risk 0.90.""", blast="high"),
            row("Fernando Tatis Jr.", "R", "+475", 79, "", ["vs Elder"], """0 HR, 1 near-HR, 97.1 mph EV. Elder RHB split +0.80, HR risk 0.90. limited recent HR events.""", blast="good"),
            row("Luis Campusano", "R", "+650", 79, "", ["vs Elder"], """1 HR, 1 near-HR, 91.9 mph EV. Elder RHB split +0.80, HR risk 0.90.""", blast="good"),
        ],
    },
    {
        "title": "SF @ KC - Trevor McDonald (R, SF) vs Michael Wacha (R, KC)",
        "description": "Tail key data: Park boost +37% (stadium +12%, weather +25%). McDonald (HR risk -1.02, vs LHB -0.44, vs RHB -1.14). Wacha (HR risk -0.46, vs LHB -0.68, vs RHB +0.20).",
        "rows": [
            row("Lane Thomas", "R", "+680", 60, "💎", ["vs McDonald"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.4 mph EV. McDonald RHB split -1.14, HR risk -1.02. tough split lane (-1.14); pitcher suppresses HR (-1.02).""", blast="good"),
            row("Carter Jensen", "L", "+457", 59, "", ["vs McDonald"], """1 HR, 3 near-HR, 87.8 mph EV. McDonald LHB split -0.44, HR risk -1.02. tough split lane (-0.44); pitcher suppresses HR (-1.02).""", blast="good"),
            row("Vinnie Pasquantino", "L", "+578", 58, "", ["vs McDonald"], """0 HR, 1 near-HR, 93.8 mph EV. McDonald LHB split -0.44, HR risk -1.02. tough split lane (-0.44); pitcher suppresses HR (-1.02).""", blast="good"),
            row("Rafael Devers", "L", "+310", 74, "🌕 💣", ["vs Wacha"], """2 HR, 2 near-HR, 96.1 mph EV. Wacha LHB split -0.68, HR risk -0.46. tough split lane (-0.68); pitcher suppresses HR (-0.46).""", blast="high"),
            row("Bryce Eldridge", "L", "+367", 64, "", ["vs Wacha"], """1 HR, 1 near-HR, 95.8 mph EV. Wacha LHB split -0.68, HR risk -0.46. tough split lane (-0.68); pitcher suppresses HR (-0.46).""", blast="good"),
        ],
    },
    {
        "title": "STL @ LAA - Kyle Leahy (R, STL) vs Jose Soriano (R, LAA)",
        "description": "Tail key data: Park boost +9% (stadium +8%, weather +1%). Leahy (HR risk -0.52, vs LHB -0.51, vs RHB -0.18). Soriano (HR risk -0.38, vs LHB +0.17, vs RHB -1.09).",
        "rows": [
            row("Vaughn Grissom", "R", "+820", 58, "⭐", ["vs Leahy"], """Worst Pickz Favorite. 0 HR, 94.6 mph EV. Leahy RHB split -0.18, HR risk -0.52. slight split headwind (-0.18); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Jorge Soler", "R", "+425", 58, "", ["vs Leahy"], """0 HR, 86.3 mph EV. Leahy RHB split -0.18, HR risk -0.52. slight split headwind (-0.18); pitcher suppresses HR (-0.52)."""),
            row("Logan O'Hoppe", "R", "+560", 58, "", ["vs Leahy"], """0 HR, 88.7 mph EV. Leahy RHB split -0.18, HR risk -0.52. slight split headwind (-0.18); pitcher suppresses HR (-0.52)."""),
            row("JJ Wetherholt", "L", "+760", 60, "", ["vs Soriano"], """1 HR, 1 near-HR, 91.4 mph EV. Soriano LHB split +0.17, HR risk -0.38. pitcher risk below avg (-0.38).""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 58, "", ["vs Soriano"], """0 HR, 95.1 mph EV. Soriano RHB split -1.09, HR risk -0.38. tough split lane (-1.09); pitcher risk below avg (-0.38).""", blast="good"),
            row("Lars Nootbaar", "L", "+630", 59, "💎", ["vs Soriano"], """Worst Pickz Hidden Gem. 0 HR, 95.8 mph EV. Soriano LHB split +0.17, HR risk -0.38. pitcher risk below avg (-0.38); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TB @ TOR - Nick Martinez (R, TB) vs Dylan Cease (R, TOR)",
        "description": "Tail key data: Park boost +5% (stadium +6%, weather -1%). Martinez (HR risk -0.07, vs LHB +0.43, vs RHB -0.77). Cease (HR risk -1.46, vs LHB -0.92, vs RHB -1.15).",
        "rows": [
            row("Kazuma Okamoto", "R", "+363", 59, "💎", ["vs Martinez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.9 mph EV. Martinez RHB split -0.77, HR risk -0.07. tough split lane (-0.77); pitcher risk below avg (-0.07).""", blast="good"),
            row("Daulton Varsho", "L", "+506", 65, "", ["vs Martinez"], """0 HR, 1 near-HR, 97.7 mph EV. Martinez LHB split +0.43, HR risk -0.07. pitcher risk below avg (-0.07); limited recent HR events.""", blast="good"),
            row("Brandon Valenzuela", "S", "N/A", 61, "", ["vs Martinez"], """1 HR, 1 near-HR, 88.5 mph EV. Martinez SHB→LHB split +0.43, HR risk -0.07. pitcher risk below avg (-0.07).""", blast="good"),
            row("Hunter Feduccia", "L", "+1200", 58, "", ["vs Cease"], """1 HR, 2 near-HR, 94.9 mph EV. Cease LHB split -0.92, HR risk -1.46. tough split lane (-0.92); pitcher suppresses HR (-1.46).""", blast="good"),
            row("Victor Mesa Jr.", "L", "+700", 58, "🌕 💣", ["vs Cease"], """2 HR, 2 near-HR, 87.9 mph EV. Cease LHB split -0.92, HR risk -1.46. tough split lane (-0.92); pitcher suppresses HR (-1.46).""", blast="high"),
            row("Jonathan Aranda", "L", "+595", 58, "", ["vs Cease"], """0 HR, 1 near-HR, 96.7 mph EV. Cease LHB split -0.92, HR risk -1.46. tough split lane (-0.92); pitcher suppresses HR (-1.46).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ COL - Andrew Alvarez (L, WSH) vs Kyle Freeland (L, COL)",
        "description": "Tail key data: Park boost +26% (stadium +19%, weather +7%). Alvarez (HR risk -1.62, vs LHB -0.91, vs RHB -1.16). Freeland (HR risk 0.78, vs LHB -0.18, vs RHB +0.93).",
        "rows": [
            row("Hunter Goodman", "R", "+262", 58, "🚀 ⭐", ["vs Alvarez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 100.4 mph EV. Alvarez RHB split -1.16, HR risk -1.62. tough split lane (-1.16); pitcher suppresses HR (-1.62).""", blast="good"),
            row("Tyler Freeman", "R", "+990", 58, "", ["vs Alvarez"], """0 HR, 91.4 mph EV. Alvarez RHB split -1.16, HR risk -1.62. tough split lane (-1.16); pitcher suppresses HR (-1.62)."""),
            row("Curtis Mead", "R", "+371", 81, "", ["vs Freeland"], """0 HR, 1 near-HR, 92.4 mph EV. Freeland RHB split +0.93, HR risk 0.78. limited recent HR events.""", blast="good"),
            row("James Wood", "L", "+238", 73, "", ["vs Freeland"], """1 HR, 1 near-HR, 89.3 mph EV. Freeland LHB split -0.18, HR risk 0.78. slight split headwind (-0.18).""", blast="good"),
            row("Dylan Crews", "R", "+364", 83, "", ["vs Freeland"], """0 HR, 1 near-HR, 94.2 mph EV. Freeland RHB split +0.93, HR risk 0.78. limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-20")

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

    out = ROOT / '_games-0711.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
