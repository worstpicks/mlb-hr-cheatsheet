#!/usr/bin/env python3
"""Generate games[] block for 2026-08-02 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Brandon Lowe (L)",
    "Corbin Carroll (L)",
    "Corey Seager (L)",
    "Dalton Rushing (L)",
    "Esmerlyn Valdez (R)",
    "Francisco Alvarez (R)",
    "Freddie Freeman (L)",
    "Griffin Conine (L)",
    "JJ Bleday (L)",
    "Jake Bauers (L)",
    "Kyle Manzardo (L)",
    "Manny Machado (R)",
    "Matt Olson (L)",
    "Miguel Vargas (R)",
    "Mitch Garver (R)",
    "Munetaka Murakami (L)",
    "Pete Alonso (R)",
    "Pete Crow-Armstrong (L)",
    "Randy Arozarena (R)",
    "Ronald Acuna Jr. (R)",
    "Salvador Perez (R)",
    "Taylor Trammell (L)",
    "Trent Grisham (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Andrew Vaughn (R)",
    "Brett Baty (L)",
    "Bryan Reynolds (S)",
    "Jimmy Crooks (L)",
    "Patrick Bailey (S)",
    "Randal Grichuk (R)",
    "Ryan McMahon (L)",
    "Ryan Vilade (R)",
    "Spencer Jones (L)",
    "Ty France (R)",
    "Tyrone Taylor (R)",
    "Vaughn Grissom (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Andrew Vaughn (R)": "MIL",
    "Andy Pages (R)": "LAD",
    "Austin Riley (R)": "ATL",
    "Bo Naylor (L)": "MIL",
    "Brandon Lowe (L)": "PIT",
    "Brenton Doyle (R)": "COL",
    "Brett Baty (L)": "NYM",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "CJ Abrams (L)": "WSH",
    "Chase DeLauter (L)": "CLE",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Coby Mayo (R)": "BAL",
    "Cole Young (L)": "SEA",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Dalton Rushing (L)": "LAD",
    "Derek Hill (R)": "PHI",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Elly De La Cruz (S)": "CIN",
    "Endy Rodriguez (S)": "PIT",
    "Enrique Hernandez (R)": "LAD",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Francisco Alvarez (R)": "NYM",
    "Freddie Freeman (L)": "LAD",
    "Garrett Mitchell (L)": "MIL",
    "Griffin Conine (L)": "MIA",
    "Hao-Yu Lee (R)": "DET",
    "Ildemaro Vargas (S)": "ARI",
    "J.T. Realmuto (R)": "PHI",
    "JJ Bleday (L)": "CIN",
    "Jacob Young (R)": "WSH",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "James Outman (L)": "DET",
    "James Wood (L)": "WSH",
    "Jeremy Pena (R)": "HOU",
    "Jimmy Crooks (L)": "STL",
    "John Rave (L)": "KC",
    "Jonathan Aranda (L)": "TB",
    "Jorge Soler (R)": "LAA",
    "Kazuma Okamoto (R)": "TOR",
    "Kody Clemens (L)": "MIN",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Stowers (L)": "MIA",
    "Lane Thomas (R)": "KC",
    "Lawrence Butler (L)": "ATH",
    "Luis Garcia Jr. (L)": "WSH",
    "Luke Keaschall (R)": "MIN",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Miguel Amaya (R)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Mitch Garver (R)": "SEA",
    "Munetaka Murakami (L)": "CWS",
    "Nick Kurtz (L)": "ATH",
    "Otto Lopez (R)": "MIA",
    "Owen Caissie (L)": "MIA",
    "Patrick Bailey (S)": "CLE",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Randal Grichuk (R)": "CWS",
    "Randy Arozarena (R)": "SEA",
    "Rhys Hoskins (R)": "CLE",
    "Ronald Acuna Jr. (R)": "ATL",
    "Ryan McMahon (L)": "NYY",
    "Ryan Vilade (R)": "TB",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Sam Antonacci (L)": "CWS",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Taylor Trammell (L)": "HOU",
    "Trent Grisham (L)": "NYY",
    "Ty France (R)": "SD",
    "Tyrone Taylor (R)": "NYM",
    "Vaughn Grissom (R)": "LAA",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("STL @ TOR", "Scherzer"),
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
        "title": "ARI @ CLE - Merrill Kelly (R, ARI) vs Gavin Williams (R, CLE)",
        "description": "Tail key data: Park boost +8% (stadium -1%, weather +9%). Kelly (HR risk 0.58, vs LHB +0.85, vs RHB +0.08). Williams (HR risk 0.73, vs LHB +0.42, vs RHB +0.62).",
        "rows": [
            row("Patrick Bailey", "S", "N/A", 89, "🌕 💣 💎", ["vs Kelly"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.9 mph EV. Kelly SHB→LHB split +0.85, HR risk 0.58.""", blast="high"),
            row("Rhys Hoskins", "R", "N/A", 85, "🌕 💣", ["vs Kelly"], """2 HR, 2 near-HR, 96.2 mph EV. Kelly RHB split +0.08, HR risk 0.58.""", blast="high"),
            row("Chase DeLauter", "L", "N/A", 76, "", ["vs Kelly"], """0 HR, 96.1 mph EV. Kelly LHB split +0.85, HR risk 0.58. limited recent HR events.""", blast="good"),
            row("Kyle Manzardo", "L", "N/A", 80, "⭐", ["vs Kelly"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.2 mph EV. Kelly LHB split +0.85, HR risk 0.58.""", blast="good"),
            row("Max Kepler", "L", "N/A", 77, "", ["vs Williams"], """1 HR, 1 near-HR, 93.4 mph EV. Williams LHB split +0.42, HR risk 0.73.""", blast="good"),
            row("Corbin Carroll", "L", "N/A", 74, "⭐", ["vs Williams"], """Worst Pickz Favorite. 0 HR, 98.2 mph EV. Williams LHB split +0.42, HR risk 0.73. limited recent HR events.""", blast="good"),
            row("Ildemaro Vargas", "S", "N/A", 76, "", ["vs Williams"], """0 HR, 97.8 mph EV. Williams SHB→RHB split +0.62, HR risk 0.73. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "BOS @ LAD - Jake Bennett (L, BOS) vs Emmet Sheehan (R, LAD)",
        "description": "Tail key data: Park boost +21% (stadium +17%, weather +4%). Bennett (HR risk -0.80, vs LHB -1.81, vs RHB -0.16). Sheehan (HR risk 0.03, vs LHB +0.08, vs RHB +0.08).",
        "rows": [
            row("Enrique Hernandez", "R", "N/A", 61, "🚀", ["vs Bennett"], """1 HR, 1 near-HR, 102.9 mph EV. Bennett RHB split -0.16, HR risk -0.80. slight split headwind (-0.16); pitcher suppresses HR (-0.80).""", blast="good"),
            row("Freddie Freeman", "L", "+470", 58, "⭐", ["vs Bennett"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 97.0 mph EV. Bennett LHB split -1.81, HR risk -0.80. tough split lane (-1.81); pitcher suppresses HR (-0.80).""", blast="good"),
            row("Dalton Rushing", "L", "+520", 58, "⭐", ["vs Bennett"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 92.9 mph EV. Bennett LHB split -1.81, HR risk -0.80. tough split lane (-1.81); pitcher suppresses HR (-0.80).""", blast="good"),
            row("Shohei Ohtani", "L", "+250", 58, "", ["vs Bennett"], """1 HR, 1 near-HR, 88.5 mph EV. Bennett LHB split -1.81, HR risk -0.80. tough split lane (-1.81); pitcher suppresses HR (-0.80).""", blast="good"),
            row("Andy Pages", "R", "+400", 58, "", ["vs Bennett"], """0 HR, 95.7 mph EV. Bennett RHB split -0.16, HR risk -0.80. slight split headwind (-0.16); pitcher suppresses HR (-0.80).""", blast="good"),
            row("Wilyer Abreu", "L", "+360", 63, "", ["vs Sheehan"], """1 HR, 1 near-HR, 88.3 mph EV. Sheehan LHB split +0.08, HR risk 0.03.""", blast="good"),
            row("Willson Contreras", "R", "+340", 68, "", ["vs Sheehan"], """1 HR, 2 near-HR, 91.7 mph EV. Sheehan RHB split +0.08, HR risk 0.03.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ TB - Anthony Kay (L, CWS) vs Griffin Jax (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Kay (HR risk -0.28, vs LHB -1.13, vs RHB +0.13). Jax (HR risk -0.22, vs LHB +0.03, vs RHB -0.16).",
        "rows": [
            row("Ryan Vilade", "R", "+349", 58, "💎", ["vs Kay"], """Worst Pickz Hidden Gem. 0 HR, 82.4 mph EV. Kay RHB split +0.13, HR risk -0.28. pitcher risk below avg (-0.28); limited recent HR events."""),
            row("Jonathan Aranda", "L", "+437", 58, "", ["vs Kay"], """1 HR, 2 near-HR, 88.1 mph EV. Kay LHB split -1.13, HR risk -0.28. tough split lane (-1.13); pitcher risk below avg (-0.28).""", blast="good"),
            row("Munetaka Murakami", "L", "+247", 80, "🚀 ⭐ 🌕 💣", ["vs Jax"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 102.1 mph EV. Jax LHB split +0.03, HR risk -0.22. pitcher risk below avg (-0.22).""", blast="high"),
            row("Randal Grichuk", "R", "N/A", 60, "💎", ["vs Jax"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.9 mph EV. Jax RHB split -0.16, HR risk -0.22. slight split headwind (-0.16); pitcher risk below avg (-0.22).""", blast="good"),
            row("Miguel Vargas", "R", "+276", 58, "⭐", ["vs Jax"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 91.6 mph EV. Jax RHB split -0.16, HR risk -0.22. slight split headwind (-0.16); pitcher risk below avg (-0.22).""", blast="good"),
            row("Sam Antonacci", "L", "+660", 59, "", ["vs Jax"], """1 HR, 1 near-HR, 92.9 mph EV. Jax LHB split +0.03, HR risk -0.22. pitcher risk below avg (-0.22).""", blast="good"),
        ],
    },
    {
        "title": "DET @ ATH - Keider Montero (R, DET) vs Gage Jump (L, ATH)",
        "description": "Tail key data: Park boost +32% (stadium +32%, weather +0%). Montero (HR risk -0.53, vs LHB +0.30, vs RHB -0.73). Jump (HR risk 0.31, vs LHB -0.13, vs RHB +0.25).",
        "rows": [
            row("Nick Kurtz", "L", "N/A", 70, "", ["vs Montero"], """1 HR, 1 near-HR, 95.8 mph EV. Montero LHB split +0.30, HR risk -0.53. pitcher suppresses HR (-0.53).""", blast="good"),
            row("Lawrence Butler", "L", "N/A", 66, "", ["vs Montero"], """0 HR, 2 near-HR, 94.6 mph EV. Montero LHB split +0.30, HR risk -0.53. pitcher suppresses HR (-0.53).""", blast="good"),
            row("James Outman", "L", "N/A", 74, "", ["vs Jump"], """1 HR, 2 near-HR, 94.5 mph EV. Jump LHB split -0.13, HR risk 0.31. slight split headwind (-0.13).""", blast="good"),
            row("Hao-Yu Lee", "R", "N/A", 63, "", ["vs Jump"], """0 HR, 1 near-HR, 90.1 mph EV. Jump RHB split +0.25, HR risk 0.31. limited recent HR events."""),
        ],
    },
    {
        "title": "KC @ COL - Seth Lugo (R, KC) vs Kyle Freeland (L, COL)",
        "description": "Tail key data: Park boost +35% (stadium +20%, weather +15%). Lugo (HR risk 0.05, vs LHB +0.48, vs RHB -0.26). Freeland (HR risk 0.67, vs LHB -0.21, vs RHB +0.60).",
        "rows": [
            row("Willi Castro", "S", "N/A", 88, "🌕 💣", ["vs Lugo"], """3 HR, 4 near-HR, 89.1 mph EV. Lugo SHB→LHB split +0.48, HR risk 0.05.""", blast="high"),
            row("Brenton Doyle", "R", "N/A", 58, "", ["vs Lugo"], """0 HR, 1 near-HR, 84.2 mph EV. Lugo RHB split -0.26, HR risk 0.05. slight split headwind (-0.26); limited recent HR events."""),
            row("Lane Thomas", "R", "N/A", 94, "🌕 💣", ["vs Freeland"], """2 HR, 3 near-HR, 95.8 mph EV. Freeland RHB split +0.60, HR risk 0.67.""", blast="high"),
            row("Salvador Perez", "R", "N/A", 86, "⭐", ["vs Freeland"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.1 mph EV. Freeland RHB split +0.60, HR risk 0.67.""", blast="good"),
            row("John Rave", "L", "N/A", 78, "🚀", ["vs Freeland"], """0 HR, 2 near-HR, 101.8 mph EV. Freeland LHB split -0.21, HR risk 0.67. slight split headwind (-0.21).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ NYM - Sandy Alcantara (R, MIA) vs Robert Stock (R, NYM)",
        "description": "Tail key data: Park boost +14% (stadium -2%, weather +16%). Alcantara (HR risk -0.39, vs LHB -0.09, vs RHB -0.31). Stock (HR risk 0.50, vs LHB +0.35, vs RHB +0.65).",
        "rows": [
            row("Griffin Conine", "L", "N/A", 64, "⭐", ["vs Stock"], """Worst Pickz Favorite. 0 HR, 90.8 mph EV. Stock LHB split +0.35, HR risk 0.50. limited recent HR events."""),
            row("Kyle Stowers", "L", "+450", 59, "", ["vs Stock"], """0 HR, 81.5 mph EV. Stock LHB split +0.35, HR risk 0.50. limited recent HR events; lighter EV form (81.5 mph)."""),
            row("Owen Caissie", "L", "+550", 91, "🌕 💣", ["vs Stock"], """2 HR, 3 near-HR, 95.8 mph EV. Stock LHB split +0.35, HR risk 0.50.""", blast="high"),
            row("Otto Lopez", "R", "+620", 82, "", ["vs Stock"], """1 HR, 2 near-HR, 98.4 mph EV. Stock RHB split +0.65, HR risk 0.50.""", blast="good"),
            row("Francisco Alvarez", "R", "+335", 76, "⭐ 🌕 💣", ["vs Alcantara"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 97.2 mph EV. Alcantara RHB split -0.31, HR risk -0.39. slight split headwind (-0.31); pitcher risk below avg (-0.39).""", blast="high"),
            row("Tyrone Taylor", "R", "N/A", 62, "🌕 💣 💎", ["vs Alcantara"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 86.5 mph EV. Alcantara RHB split -0.31, HR risk -0.39. slight split headwind (-0.31); pitcher risk below avg (-0.39).""", blast="high"),
            row("Brett Baty", "L", "+516", 68, "🌕 💣 💎", ["vs Alcantara"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 90.3 mph EV. Alcantara LHB split -0.09, HR risk -0.39. slight split headwind (-0.09); pitcher risk below avg (-0.39).""", blast="high"),
        ],
    },
    {
        "title": "MIL @ LAA - Jacob Misiorowski (R, MIL) vs Walbert Urena (R, LAA)",
        "description": "Tail key data: Park boost -2% (stadium -7%, weather +5%). Misiorowski (HR risk -0.02, vs LHB -0.72, vs RHB +0.77). Urena (HR risk -1.42, vs LHB -0.60, vs RHB -1.17).",
        "rows": [
            row("Vaughn Grissom", "R", "+900", 73, "🌕 💣 💎", ["vs Misiorowski"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 89.3 mph EV. Misiorowski RHB split +0.77, HR risk -0.02. pitcher risk below avg (-0.02); park suppresses carry (-7%).""", blast="high"),
            row("Jorge Soler", "R", "+480", 62, "", ["vs Misiorowski"], """0 HR, 1 near-HR, 92.0 mph EV. Misiorowski RHB split +0.77, HR risk -0.02. pitcher risk below avg (-0.02); park suppresses carry (-7%).""", blast="good"),
            row("Zach Neto", "R", "+450", 59, "", ["vs Misiorowski"], """0 HR, 2 near-HR, 87.3 mph EV. Misiorowski RHB split +0.77, HR risk -0.02. pitcher risk below avg (-0.02); park suppresses carry (-7%).""", blast="good"),
            row("Garrett Mitchell", "L", "+560", 58, "", ["vs Urena"], """0 HR, 94.0 mph EV. Urena LHB split -0.60, HR risk -1.42. tough split lane (-0.60); pitcher suppresses HR (-1.42).""", blast="good"),
            row("Andrew Vaughn", "R", "+600", 58, "💎", ["vs Urena"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 95.4 mph EV. Urena RHB split -1.17, HR risk -1.42. tough split lane (-1.17); pitcher suppresses HR (-1.42).""", blast="good"),
            row("Jake Bauers", "L", "+420", 58, "⭐", ["vs Urena"], """Worst Pickz Favorite. 0 HR, 98.6 mph EV. Urena LHB split -0.60, HR risk -1.42. tough split lane (-0.60); pitcher suppresses HR (-1.42).""", blast="good"),
            row("Bo Naylor", "L", "N/A", 58, "", ["vs Urena"], """1 HR, 2 near-HR, 92.2 mph EV. Urena LHB split -0.60, HR risk -1.42. tough split lane (-0.60); pitcher suppresses HR (-1.42).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ SEA - Taj Bradley (R, MIN) vs George Kirby (R, SEA)",
        "description": "Tail key data: Park boost -3% (stadium +1%, weather -4%). Bradley (HR risk 0.24, vs LHB +0.84, vs RHB -0.33). Kirby (HR risk 0.25, vs LHB +0.55, vs RHB -0.04).",
        "rows": [
            row("Mitch Garver", "R", "N/A", 60, "⭐", ["vs Bradley"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.9 mph EV. Bradley RHB split -0.33, HR risk 0.24. slight split headwind (-0.33); weather carry headwind (-4%).""", blast="good"),
            row("Randy Arozarena", "R", "+500", 63, "⭐", ["vs Bradley"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.0 mph EV. Bradley RHB split -0.33, HR risk 0.24. slight split headwind (-0.33); weather carry headwind (-4%).""", blast="good"),
            row("Dominic Canzone", "L", "+430", 66, "", ["vs Bradley"], """1 HR, 1 near-HR, 89.7 mph EV. Bradley LHB split +0.84, HR risk 0.24. weather carry headwind (-4%).""", blast="good"),
            row("Cole Young", "L", "+700", 69, "", ["vs Bradley"], """1 HR, 1 near-HR, 92.2 mph EV. Bradley LHB split +0.84, HR risk 0.24. weather carry headwind (-4%).""", blast="good"),
            row("Luke Keaschall", "R", "+1005", 64, "", ["vs Kirby"], """1 HR, 1 near-HR, 94.0 mph EV. Kirby RHB split -0.04, HR risk 0.25. slight split headwind (-0.04); weather carry headwind (-4%).""", blast="good"),
            row("Kody Clemens", "L", "+374", 64, "", ["vs Kirby"], """0 HR, 2 near-HR, 92.2 mph EV. Kirby LHB split +0.55, HR risk 0.25. weather carry headwind (-4%).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ CHC - Gerrit Cole (R, NYY) vs Colin Rea (R, CHC)",
        "description": "Tail key data: Park boost -12% (stadium -1%, weather -12%). Cole (HR risk 0.51, vs LHB +0.69, vs RHB +0.04). Rea (HR risk 0.14, vs LHB -0.29, vs RHB +0.61).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+474", 86, "⭐ 🌕 💣", ["vs Cole"], """Worst Pickz Favorite. 1 HR, 4 near-HR, 98.2 mph EV. Cole LHB split +0.69, HR risk 0.51. park/weather net drag (-12%).""", blast="high"),
            row("Miguel Amaya", "R", "N/A", 58, "", ["vs Cole"], """0 HR, 90.9 mph EV. Cole RHB split +0.04, HR risk 0.51. park/weather net drag (-12%); limited recent HR events."""),
            row("Ryan McMahon", "L", "+620", 60, "💎", ["vs Rea"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.8 mph EV. Rea LHB split -0.29, HR risk 0.14. slight split headwind (-0.29); park/weather net drag (-12%).""", blast="good"),
            row("Spencer Jones", "L", "+660", 59, "💎", ["vs Rea"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.5 mph EV. Rea LHB split -0.29, HR risk 0.14. slight split headwind (-0.29); park/weather net drag (-12%).""", blast="good"),
            row("Trent Grisham", "L", "+503", 58, "⭐", ["vs Rea"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 90.5 mph EV. Rea LHB split -0.29, HR risk 0.14. slight split headwind (-0.29); park/weather net drag (-12%).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ BAL - Zack Wheeler (R, PHI) vs Kyle Bradish (R, BAL)",
        "description": "Tail key data: Park boost +12% (stadium -2%, weather +14%). Wheeler (HR risk -0.26, vs LHB +0.18, vs RHB -0.50). Bradish (HR risk -0.90, vs LHB -0.69, vs RHB -0.40).",
        "rows": [
            row("Pete Alonso", "R", "+395", 61, "⭐", ["vs Wheeler"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.6 mph EV. Wheeler RHB split -0.50, HR risk -0.26. tough split lane (-0.50); pitcher risk below avg (-0.26).""", blast="good"),
            row("Coby Mayo", "R", "+492", 61, "", ["vs Wheeler"], """1 HR, 1 near-HR, 96.9 mph EV. Wheeler RHB split -0.50, HR risk -0.26. tough split lane (-0.50); pitcher risk below avg (-0.26).""", blast="good"),
            row("Christian Encarnacion-Strand", "R", "N/A", 58, "", ["vs Wheeler"], """0 HR, 1 near-HR, 93.8 mph EV. Wheeler RHB split -0.50, HR risk -0.26. tough split lane (-0.50); pitcher risk below avg (-0.26).""", blast="good"),
            row("Bryce Harper", "L", "+399", 62, "🌕 💣", ["vs Bradish"], """2 HR, 2 near-HR, 94.6 mph EV. Bradish LHB split -0.69, HR risk -0.90. tough split lane (-0.69); pitcher suppresses HR (-0.90).""", blast="high"),
            row("Bryson Stott", "L", "+670", 58, "", ["vs Bradish"], """1 HR, 2 near-HR, 95.6 mph EV. Bradish LHB split -0.69, HR risk -0.90. tough split lane (-0.69); pitcher suppresses HR (-0.90).""", blast="good"),
            row("J.T. Realmuto", "R", "+700", 58, "", ["vs Bradish"], """1 HR, 1 near-HR, 94.1 mph EV. Bradish RHB split -0.40, HR risk -0.90. tough split lane (-0.40); pitcher suppresses HR (-0.90).""", blast="good"),
            row("Derek Hill", "R", "N/A", 58, "", ["vs Bradish"], """1 HR, 1 near-HR, 90.8 mph EV. Bradish RHB split -0.40, HR risk -0.90. tough split lane (-0.40); pitcher suppresses HR (-0.90).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ CIN - Mitch Keller (R, PIT) vs Chase Burns (R, CIN)",
        "description": "Tail key data: Park boost +19% (stadium +14%, weather +5%). Keller (HR risk -0.17, vs LHB +0.44, vs RHB -0.63). Burns (HR risk -0.10, vs LHB +0.55, vs RHB -0.59).",
        "rows": [
            row("Elly De La Cruz", "S", "N/A", 64, "", ["vs Keller"], """0 HR, 94.5 mph EV. Keller SHB→LHB split +0.44, HR risk -0.17. pitcher risk below avg (-0.17); limited recent HR events.""", blast="good"),
            row("JJ Bleday", "L", "N/A", 76, "⭐ 🌕 💣", ["vs Keller"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.4 mph EV. Keller LHB split +0.44, HR risk -0.17. pitcher risk below avg (-0.17).""", blast="high"),
            row("Sal Stewart", "R", "N/A", 60, "", ["vs Keller"], """1 HR, 1 near-HR, 93.3 mph EV. Keller RHB split -0.63, HR risk -0.17. tough split lane (-0.63); pitcher risk below avg (-0.17).""", blast="good"),
            row("Eugenio Suarez", "R", "N/A", 72, "🌕 💣", ["vs Keller"], """2 HR, 2 near-HR, 95.9 mph EV. Keller RHB split -0.63, HR risk -0.17. tough split lane (-0.63); pitcher risk below avg (-0.17).""", blast="high"),
            row("Esmerlyn Valdez", "R", "N/A", 62, "⭐", ["vs Burns"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.7 mph EV. Burns RHB split -0.59, HR risk -0.10. tough split lane (-0.59); pitcher risk below avg (-0.10).""", blast="good"),
            row("Bryan Reynolds", "S", "N/A", 81, "🌕 💣 💎", ["vs Burns"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.4 mph EV. Burns SHB→LHB split +0.55, HR risk -0.10. pitcher risk below avg (-0.10).""", blast="high"),
            row("Endy Rodriguez", "S", "N/A", 73, "", ["vs Burns"], """1 HR, 1 near-HR, 96.9 mph EV. Burns SHB→LHB split +0.55, HR risk -0.10. pitcher risk below avg (-0.10).""", blast="good"),
            row("Brandon Lowe", "L", "N/A", 66, "⭐", ["vs Burns"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 93.4 mph EV. Burns LHB split +0.55, HR risk -0.10. pitcher risk below avg (-0.10); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "SF @ SD - Landen Roupp (R, SF) vs Michael King (R, SD)",
        "description": "Tail key data: Park boost +3% (stadium -6%, weather +9%). Roupp (HR risk -0.93, vs LHB -1.03, vs RHB -0.21). King (HR risk -0.39, vs LHB -0.12, vs RHB -0.21).",
        "rows": [
            row("Manny Machado", "R", "+297", 58, "⭐", ["vs Roupp"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.5 mph EV. Roupp RHB split -0.21, HR risk -0.93. slight split headwind (-0.21); pitcher suppresses HR (-0.93).""", blast="good"),
            row("Ty France", "R", "+393", 58, "💎", ["vs Roupp"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 91.9 mph EV. Roupp RHB split -0.21, HR risk -0.93. slight split headwind (-0.21); pitcher suppresses HR (-0.93).""", blast="good"),
            row("Bryce Eldridge", "L", "+249", 65, "🌕 💣", ["vs King"], """2 HR, 2 near-HR, 90.7 mph EV. King LHB split -0.12, HR risk -0.39. slight split headwind (-0.12); pitcher risk below avg (-0.39).""", blast="high"),
        ],
    },
    {
        "title": "STL @ TOR - Matthew Liberatore (L, STL) vs Max Scherzer 🧤 (R, TOR)",
        "description": "Tail key data: Park boost +15% (stadium +6%, weather +8%). Liberatore (HR risk -0.32, vs LHB +0.04, vs RHB -0.22). Scherzer 🧤 (HR risk 1.96, vs LHB +2.20, vs RHB +0.83).",
        "rows": [
            row("Kazuma Okamoto", "R", "+333", 58, "", ["vs Liberatore"], """0 HR, 93.0 mph EV. Liberatore RHB split -0.22, HR risk -0.32. slight split headwind (-0.22); pitcher risk below avg (-0.32).""", blast="good"),
            row("Vladimir Guerrero Jr.", "R", "+484", 58, "", ["vs Liberatore"], """0 HR, 93.1 mph EV. Liberatore RHB split -0.22, HR risk -0.32. slight split headwind (-0.22); pitcher risk below avg (-0.32).""", blast="good"),
            row("Jimmy Crooks", "L", "+680", 95, "🌕 💣 💎", ["vs Scherzer"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 95.5 mph EV. Scherzer LHB split +2.20, HR risk 1.96.""", blast="good"),
            row("Alec Burleson", "L", "+392", 93, "⭐ 🌕 💣", ["vs Scherzer"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 99.6 mph EV. Scherzer LHB split +2.20, HR risk 1.96. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TEX @ HOU - Kumar Rocker (R, TEX) vs Peter Lambert (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +0%). Rocker (HR risk -0.03, vs LHB +0.67, vs RHB -0.49). Lambert (HR risk -0.80, vs LHB -0.84, vs RHB -0.20).",
        "rows": [
            row("Taylor Trammell", "L", "N/A", 80, "🚀 ⭐ 🌕 💣", ["vs Rocker"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 101.2 mph EV. Rocker LHB split +0.67, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="high"),
            row("Jeremy Pena", "R", "+560", 71, "🌕 💣", ["vs Rocker"], """2 HR, 2 near-HR, 95.6 mph EV. Rocker RHB split -0.49, HR risk -0.03. tough split lane (-0.49); pitcher risk below avg (-0.03).""", blast="high"),
            row("Yordan Alvarez", "L", "+220", 58, "⭐", ["vs Rocker"], """Worst Pickz Favorite. 0 HR, 91.7 mph EV. Rocker LHB split +0.67, HR risk -0.03. pitcher risk below avg (-0.03); limited recent HR events."""),
            row("Corey Seager", "L", "+330", 65, "⭐ 🌕 💣", ["vs Lambert"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 93.4 mph EV. Lambert LHB split -0.84, HR risk -0.80. tough split lane (-0.84); pitcher suppresses HR (-0.80).""", blast="high"),
            row("Wyatt Langford", "R", "+340", 58, "", ["vs Lambert"], """1 HR, 1 near-HR, 94.9 mph EV. Lambert RHB split -0.20, HR risk -0.80. slight split headwind (-0.20); pitcher suppresses HR (-0.80).""", blast="good"),
            row("Jake Burger", "R", "+390", 58, "", ["vs Lambert"], """1 HR, 2 near-HR, 89.1 mph EV. Lambert RHB split -0.20, HR risk -0.80. slight split headwind (-0.20); pitcher suppresses HR (-0.80).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ ATL - Cade Cavalli (R, WSH) vs JR Ritchie (R, ATL)",
        "description": "Tail key data: Park boost +1% (stadium -3%, weather +4%). Cavalli (HR risk -0.42, vs LHB +0.05, vs RHB -0.50). Ritchie (HR risk 0.55, vs LHB +0.40, vs RHB +0.70).",
        "rows": [
            row("James Wood", "L", "+400", 76, "", ["vs Ritchie"], """1 HR, 1 near-HR, 96.1 mph EV. Ritchie LHB split +0.40, HR risk 0.55.""", blast="good"),
            row("CJ Abrams", "L", "+547", 60, "", ["vs Ritchie"], """0 HR, 89.4 mph EV. Ritchie LHB split +0.40, HR risk 0.55. limited recent HR events."""),
            row("Luis Garcia Jr.", "L", "+579", 76, "", ["vs Ritchie"], """1 HR, 2 near-HR, 94.9 mph EV. Ritchie LHB split +0.40, HR risk 0.55.""", blast="good"),
            row("Jacob Young", "R", "+1800", 59, "", ["vs Ritchie"], """0 HR, 79.8 mph EV. Ritchie RHB split +0.70, HR risk 0.55. limited recent HR events; lighter EV form (79.8 mph)."""),
            row("Ronald Acuna Jr.", "R", "N/A", 66, "⭐ 🌕 💣", ["vs Cavalli"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.4 mph EV. Cavalli RHB split -0.50, HR risk -0.42. tough split lane (-0.50); pitcher suppresses HR (-0.42).""", blast="high"),
            row("Matt Olson", "L", "N/A", 75, "⭐ 🌕 💣", ["vs Cavalli"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.7 mph EV. Cavalli LHB split +0.05, HR risk -0.42. pitcher suppresses HR (-0.42).""", blast="high"),
            row("Austin Riley", "R", "N/A", 58, "", ["vs Cavalli"], """0 HR, 94.5 mph EV. Cavalli RHB split -0.50, HR risk -0.42. tough split lane (-0.50); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Drake Baldwin", "L", "N/A", 58, "", ["vs Cavalli"], """0 HR, 1 near-HR, 94.1 mph EV. Cavalli LHB split +0.05, HR risk -0.42. pitcher suppresses HR (-0.42); limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-02")

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

    out = ROOT / '_games-0802.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
