#!/usr/bin/env python3
"""Generate games[] block for 2026-09-27 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Ben Rice (L)",
    "Corey Seager (L)",
    "Drake Baldwin (L)",
    "J.P. Crawford (L)",
    "Jake Burger (R)",
    "Joe Mack (L)",
    "Jordan Walker (R)",
    "Juan Soto (L)",
    "Randal Grichuk (R)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Connor Norby (R)",
    "Griffin Conine (L)",
    "Henry Bolte (R)",
    "Manny Machado (R)",
}

PLAYER_TEAMS = {
    "Agustin Ramirez (R)": "MIA",
    "Alec Bohm (R)": "PHI",
    "Alec Burleson (L)": "STL",
    "Andres Chaparro (R)": "WSH",
    "Andrew Knizner (R)": "SF",
    "Andy Pages (R)": "LAD",
    "Ben Rice (L)": "NYY",
    "Bo Naylor (L)": "MIL",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Nimmo (L)": "TEX",
    "Brenton Doyle (R)": "CWS",
    "Brice Turang (L)": "MIL",
    "Brooks Lee (S)": "MIN",
    "Carter Jensen (L)": "KC",
    "Cedric Mullins (L)": "TB",
    "Chase DeLauter (L)": "CLE",
    "Christian Moore (R)": "LAA",
    "Christian Walker (R)": "HOU",
    "Cole Carrigg (S)": "COL",
    "Connor Norby (R)": "COL",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Dylan Beavers (L)": "BAL",
    "Eduardo Valencia (R)": "DET",
    "Elly De La Cruz (S)": "CIN",
    "Eugenio Suarez (R)": "CIN",
    "Ezequiel Tovar (R)": "COL",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Freddie Freeman (L)": "LAD",
    "Garrett Mitchell (L)": "MIL",
    "George Springer (R)": "TOR",
    "Graham Pauley (L)": "MIA",
    "Grant McCray (L)": "SF",
    "Griffin Conine (L)": "MIA",
    "Gunnar Henderson (L)": "BAL",
    "Hector Rodriguez (L)": "CIN",
    "Henry Bolte (R)": "ATH",
    "Ivan Herrera (R)": "STL",
    "J.P. Crawford (L)": "SEA",
    "J.T. Realmuto (R)": "PHI",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "Jake Burger (R)": "TEX",
    "Jake Cronenworth (L)": "SD",
    "James McCann (R)": "ARI",
    "James Wood (L)": "WSH",
    "Jeremy Pena (R)": "HOU",
    "Jo Adell (R)": "CLE",
    "Joe Mack (L)": "MIA",
    "Jonah Heim (S)": "ATH",
    "Jonathan Aranda (L)": "TB",
    "Jordan Beck (R)": "COL",
    "Jordan Walker (R)": "STL",
    "Jose Ramirez (S)": "CLE",
    "Jose Siri (R)": "LAA",
    "Juan Soto (L)": "NYM",
    "Konnor Griffin (R)": "PIT",
    "Kyle Karros (R)": "COL",
    "Kyle Stowers (L)": "MIA",
    "Lars Nootbaar (L)": "ARI",
    "Leonardo Bernal (S)": "STL",
    "Manny Machado (R)": "SD",
    "Marcelo Mayer (L)": "SF",
    "Marcus Semien (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Mike Trout (R)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Oneil Cruz (L)": "PIT",
    "Otto Lopez (R)": "MIA",
    "Pete Crow Armstrong (L)": "CHC",
    "Randal Grichuk (R)": "CWS",
    "Randy Arozarena (R)": "SEA",
    "Riley Greene (L)": "DET",
    "Roman Anthony (L)": "BOS",
    "Ryan Kreidler (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Sal Stewart (R)": "CIN",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Taylor Trammell (L)": "HOU",
    "Taylor Ward (R)": "SEA",
    "Trea Turner (R)": "PHI",
    "Victor Mesa Jr. (L)": "TB",
    "Will Smith (R)": "LAD",
    "William Contreras (R)": "MIL",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("ATL @ MIA", "Ritchie"),
    ("COL @ CWS", "Freeland"),
    ("LAA @ SEA", "Gilbert"),
    ("LAD @ SF", "Seymour"),
}

def odds_text(odds):
    return "Listed prop - Over 0.5 HR" if odds == "N/A" else f"Listed {odds} - Over 0.5 HR"

def row(name, hand, odds, score, emojis, chips, note, blast=None, contact=None):
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
    if contact:
        item["contact"] = contact
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
        "title": "ARI @ SD - Michael Soroka (R, ARI) vs Randy Vasquez (R, SD)",
        "kLines": {'Soroka': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 21.9, 'matchupK': 23.8, 'ownK': 25.1}, 'Vasquez': {'k': 3.2, 'lo': 2, 'hi': 5, 'bf': 21.0, 'matchupK': 15.1, 'ownK': 13.8}},
        "description": "Tail key data: Park boost +3% (stadium -4%, weather +7%). Soroka (HR risk -0.35, vs LHB +0.22, vs RHB -0.60). Vasquez (HR risk -0.16, vs LHB +0.50, vs RHB -0.43).",
        "rows": [
            row("Manny Machado", "R", "+450", 73, "💎", ["vs Soroka"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.7 mph EV, 20.0% barrels. Soroka RHB split -0.60, HR risk -0.35. tough split lane (-0.60); pitcher risk below avg (-0.35).""", blast="good", contact={'stars': 3, 'k': 21.7, 'batterK': 18.0, 'batterWhiff': 21.6, 'pitcherK': 25.1}),
            row("Jake Cronenworth", "L", "+900", 60, "", ["vs Soroka"], """0 HR, 1 near-HR, 92.6 mph EV, 20.0% barrels. Soroka LHB split +0.22, HR risk -0.35. pitcher risk below avg (-0.35); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.3, 'batterK': 20.3, 'batterWhiff': 15.8, 'pitcherK': 25.1}),
            row("Fernando Tatis Jr.", "R", "+350", 68, "", ["vs Soroka"], """0 HR, 89.9 mph EV, 20.0% barrels. Soroka RHB split -0.60, HR risk -0.35. tough split lane (-0.60); pitcher risk below avg (-0.35).""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 17.6, 'batterWhiff': 19.7, 'pitcherK': 25.1}),
            row("James McCann", "R", "N/A", 71, "", ["vs Vasquez"], """1 HR, 1 near-HR, 90.1 mph EV, 25.0% barrels. Vasquez RHB split -0.43, HR risk -0.16. tough split lane (-0.43); pitcher risk below avg (-0.16).""", blast="good", contact={'stars': 3, 'k': 21.0, 'batterK': 28.6, 'batterWhiff': 34.2, 'pitcherK': 13.8}),
            row("Lars Nootbaar", "L", "N/A", 75, "", ["vs Vasquez"], """1 HR, 1 near-HR, 92.7 mph EV, 25.0% barrels. Vasquez LHB split +0.50, HR risk -0.16. pitcher risk below avg (-0.16).""", blast="good", contact={'stars': 4, 'k': 18.0, 'batterK': 24.7, 'batterWhiff': 19.8, 'pitcherK': 13.8}),
            row("Corbin Carroll", "L", "N/A", 63, "", ["vs Vasquez"], """0 HR, 88.3 mph EV. Vasquez LHB split +0.50, HR risk -0.16. pitcher risk below avg (-0.16); limited recent HR events.""", contact={'stars': 3, 'k': 20.6, 'batterK': 29.3, 'batterWhiff': 28.8, 'pitcherK': 13.8}),
        ],
    },
    {
        "title": "ATL @ MIA - JR Ritchie 🧤 (R, ATL) vs Janson Junk (R, MIA)",
        "kLines": {'Ritchie': {'k': 5.1, 'lo': 3, 'hi': 7, 'bf': 22.1, 'matchupK': 22.9, 'ownK': 23.8}, 'Junk': {'k': 3.3, 'lo': 2, 'hi': 5, 'bf': 21.1, 'matchupK': 15.5, 'ownK': 13.7}},
        "description": "Tail key data: Park boost -12% (stadium -12%, weather +0%). Ritchie 🧤 (HR risk 1.23, vs LHB +1.28, vs RHB +0.82). Junk (HR risk -0.36, vs LHB -0.45, vs RHB +0.17).",
        "rows": [
            row("Kyle Stowers", "L", "+300", 96, "🌕 💣", ["vs Ritchie"], """2 HR, 2 near-HR, 99.6 mph EV, 40.0% barrels. Ritchie LHB split +1.28, HR risk 1.23. park/weather net drag (-12%).""", blast="high", contact={'stars': 2, 'k': 26.4, 'batterK': 29.5, 'batterWhiff': 32.6, 'pitcherK': 23.8}),
            row("Joe Mack", "L", "+800", 89, "⭐ 🌕 💣", ["vs Ritchie"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.5 mph EV, 40.0% barrels. Ritchie LHB split +1.28, HR risk 1.23. park/weather net drag (-12%).""", blast="high", contact={'stars': 3, 'k': 23.2, 'batterK': 23.0, 'batterWhiff': 25.8, 'pitcherK': 23.8}),
            row("Graham Pauley", "L", "+750", 85, "", ["vs Ritchie"], """1 HR, 1 near-HR, 94.8 mph EV, 20.0% barrels. Ritchie LHB split +1.28, HR risk 1.23. park/weather net drag (-12%).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 27.3, 'batterWhiff': 23.7, 'pitcherK': 23.8}),
            row("Griffin Conine", "L", "+421", 88, "🌕 💣 💎", ["vs Ritchie"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.0 mph EV, 20.0% barrels. Ritchie LHB split +1.28, HR risk 1.23. park/weather net drag (-12%).""", blast="good", contact={'stars': 2, 'k': 24.4, 'batterK': 22.1, 'batterWhiff': 32.7, 'pitcherK': 23.8}),
            row("Otto Lopez", "R", "+840", 70, "", ["vs Ritchie"], """0 HR, 96.7 mph EV. Ritchie RHB split +0.82, HR risk 1.23. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.1, 'batterK': 12.0, 'batterWhiff': 21.9, 'pitcherK': 23.8}),
            row("Agustin Ramirez", "R", "+565", 73, "", ["vs Ritchie"], """0 HR, 99.9 mph EV. Ritchie RHB split +0.82, HR risk 1.23. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.6, 'batterK': 27.4, 'batterWhiff': 28.9, 'pitcherK': 23.8}),
            row("Drake Baldwin", "L", "+449", 81, "⭐", ["vs Junk"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.7 mph EV, 20.0% barrels. Junk LHB split -0.45, HR risk -0.36. tough split lane (-0.45); pitcher risk below avg (-0.36).""", blast="good", contact={'stars': 4, 'k': 18.0, 'batterK': 21.7, 'batterWhiff': 23.6, 'pitcherK': 13.7}),
            row("Matt Olson", "L", "+343", 64, "", ["vs Junk"], """0 HR, 99.1 mph EV. Junk LHB split -0.45, HR risk -0.36. tough split lane (-0.45); pitcher risk below avg (-0.36).""", blast="good", contact={'stars': 5, 'k': 16.9, 'batterK': 15.7, 'batterWhiff': 25.2, 'pitcherK': 13.7}),
            row("Michael Harris II", "L", "+382", 70, "🚀 🌕 💣", ["vs Junk"], """0 HR, 2 near-HR, 103.2 mph EV, 20.0% barrels. Junk LHB split -0.45, HR risk -0.36. tough split lane (-0.45); pitcher risk below avg (-0.36).""", blast="high", contact={'stars': 5, 'k': 16.0, 'batterK': 14.5, 'batterWhiff': 21.3, 'pitcherK': 13.7}),
        ],
    },
    {
        "title": "BAL @ NYY - Shane Baz (R, BAL) vs Elmer Rodríguez (R, NYY)",
        "kLines": {'Baz': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 24.3, 'matchupK': 20.7, 'ownK': 19.3}, 'Rodríguez': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 21.3, 'matchupK': 21.0, 'ownK': 16.8}},
        "description": "Tail key data: Park boost -8% (stadium +5%, weather -13%). Baz (HR risk -0.17, vs LHB +0.69, vs RHB -1.04). Rodríguez (HR risk -0.59, vs LHB +0.35, vs RHB -0.82).",
        "rows": [
            row("Ben Rice", "L", "+450", 81, "⭐", ["vs Baz"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 89.6 mph EV, 20.0% barrels. Baz LHB split +0.69, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-8%).""", blast="good", contact={'stars': 4, 'k': 19.5, 'batterK': 20.0, 'batterWhiff': 22.1, 'pitcherK': 19.3}),
            row("Ryan McMahon", "L", "+800", 75, "🌕 💣", ["vs Baz"], """1 HR, 1 near-HR, 99.3 mph EV, 20.0% barrels. Baz LHB split +0.69, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-8%).""", blast="high", contact={'stars': 3, 'k': 20.8, 'batterK': 25.4, 'batterWhiff': 23.6, 'pitcherK': 19.3}),
            row("Spencer Jones", "L", "+600", 77, "🚀 🌕 💣", ["vs Baz"], """0 HR, 100.2 mph EV, 20.0% barrels. Baz LHB split +0.69, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-8%).""", blast="high", contact={'stars': 1, 'k': 27.8, 'batterK': 39.8, 'batterWhiff': 40.4, 'pitcherK': 19.3}),
            row("Dylan Beavers", "L", "+620", 73, "🌕 💣", ["vs Rodríguez"], """2 HR, 2 near-HR, 88.5 mph EV, 40.0% barrels. Rodríguez LHB split +0.35, HR risk -0.59. pitcher suppresses HR (-0.59); park/weather net drag (-8%).""", blast="high", contact={'stars': 2, 'k': 24.1, 'batterK': 33.7, 'batterWhiff': 29.7, 'pitcherK': 16.8}),
            row("Gunnar Henderson", "L", "+600", 53, "", ["vs Rodríguez"], """0 HR, 90.9 mph EV. Rodríguez LHB split +0.35, HR risk -0.59. pitcher suppresses HR (-0.59); park/weather net drag (-8%).""", contact={'stars': 3, 'k': 21.4, 'batterK': 28.6, 'batterWhiff': 22.1, 'pitcherK': 16.8}),
        ],
    },
    {
        "title": "CHC @ BOS - Julian Aguiar (R, CHC) vs Patrick Sandoval (L, BOS)",
        "kLines": {'Aguiar': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 21.7, 'matchupK': 21.4, 'ownK': 14.3}, 'Sandoval': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 22.4, 'matchupK': 20.4, 'ownK': 22.5}},
        "description": "Tail key data: Park boost -1% (stadium -2%, weather +0%). Aguiar - thin book: 3.0 IP this season (34.2 career IP, 6.23 ERA). Sandoval (BAA vs LHB .368, vs RHB .273, HR/9 0.96).",
        "rows": [
            row("Michael Conforto", "L", "N/A", 87, "🚀 🌕 💣", ["vs Sandoval"], """2 HR, 2 near-HR, 102.6 mph EV, 50.0% barrels. limited split/risk sample.""", blast="high", contact={'stars': 3, 'k': 20.4, 'batterK': 15.6, 'batterWhiff': 21.1, 'pitcherK': 22.5}),
            row("Pete Crow Armstrong", "L", "N/A", 57, "", ["vs Sandoval"], """0 HR, 82.5 mph EV. limited split/risk sample; limited recent HR events.""", contact={'stars': 3, 'k': 22.2, 'batterK': 22.3, 'batterWhiff': 23.7, 'pitcherK': 22.5}),
            row("Roman Anthony", "L", "N/A", 72, "", ["vs Aguiar"], """0 HR, 97.3 mph EV, 12.5% barrels. limited split/risk sample; limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.8, 'batterK': 31.9, 'batterWhiff': 31.7, 'pitcherK': 14.3}),
        ],
    },
    {
        "title": "CIN @ TOR - Brandon Williamson (L, CIN) vs Max Scherzer (R, TOR)",
        "kLines": {'Williamson': {'k': 3.3, 'lo': 2, 'hi': 5, 'bf': 21.5, 'matchupK': 15.3, 'ownK': 15.5}, 'Scherzer': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 20.3, 'matchupK': 22.0, 'ownK': 19.5}},
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +0%). Williamson (HR risk 0.31, vs LHB +0.53, vs RHB +0.39). Scherzer (HR risk 0.34, vs LHB +0.77, vs RHB +0.05).",
        "rows": [
            row("George Springer", "R", "+591", 64, "", ["vs Williamson"], """1 HR, 1 near-HR, 92.1 mph EV. Williamson RHB split +0.39, HR risk 0.31.""", blast="good", contact={'stars': 4, 'k': 18.9, 'batterK': 20.3, 'batterWhiff': 27.0, 'pitcherK': 15.5}),
            row("Hector Rodriguez", "L", "+575", 85, "🚀 🌕 💣", ["vs Scherzer"], """1 HR, 2 near-HR, 100.0 mph EV, 20.0% barrels. Scherzer LHB split +0.77, HR risk 0.34.""", blast="high"),
            row("JJ Bleday", "L", "+476", 76, "", ["vs Scherzer"], """1 HR, 1 near-HR, 90.2 mph EV, 20.0% barrels. Scherzer LHB split +0.77, HR risk 0.34.""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 28.4, 'batterWhiff': 30.1, 'pitcherK': 19.5}),
            row("Elly De La Cruz", "S", "+402", 85, "", ["vs Scherzer"], """1 HR, 1 near-HR, 92.7 mph EV, 20.0% barrels. Scherzer SHB→LHB split +0.77, HR risk 0.34.""", blast="good", contact={'stars': 2, 'k': 24.0, 'batterK': 29.1, 'batterWhiff': 33.1, 'pitcherK': 19.5}),
            row("Sal Stewart", "R", "+440", 73, "", ["vs Scherzer"], """0 HR, 96.9 mph EV. Scherzer RHB split +0.05, HR risk 0.34. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.4, 'batterK': 29.4, 'batterWhiff': 29.2, 'pitcherK': 19.5}),
            row("Eugenio Suarez", "R", "+440", 80, "", ["vs Scherzer"], """1 HR, 1 near-HR, 94.0 mph EV, 40.0% barrels. Scherzer RHB split +0.05, HR risk 0.34.""", blast="good", contact={'stars': 3, 'k': 22.8, 'batterK': 27.5, 'batterWhiff': 28.9, 'pitcherK': 19.5}),
        ],
    },
    {
        "title": "CLE @ KC - Parker Messick (L, CLE) vs Daniel Lynch IV (L, KC)",
        "kLines": {'Messick': {'k': 6.3, 'lo': 5, 'hi': 8, 'bf': 23.3, 'matchupK': 27.1, 'ownK': 29.4}, 'Lynch IV': {'k': 2.7, 'lo': 1, 'hi': 4, 'bf': 18.7, 'matchupK': 14.4, 'ownK': 12.9}},
        "description": "Tail key data: Park boost +17% (stadium +12%, weather +5%). Messick (HR risk -0.46, vs LHB +0.32, vs RHB -0.66). Lynch IV (HR risk 0.23, vs LHB -0.88, vs RHB +0.69).",
        "rows": [
            row("Carter Jensen", "L", "+584", 75, "", ["vs Messick"], """1 HR, 1 near-HR, 87.5 mph EV, 20.0% barrels. Messick LHB split +0.32, HR risk -0.46. pitcher suppresses HR (-0.46); lighter EV form (87.5 mph).""", blast="good", contact={'stars': 1, 'k': 29.0, 'batterK': 26.4, 'batterWhiff': 32.5, 'pitcherK': 29.4}),
            row("Bobby Witt Jr.", "R", "+413", 81, "🌕 💣", ["vs Messick"], """0 HR, 1 near-HR, 98.0 mph EV, 20.0% barrels. Messick RHB split -0.66, HR risk -0.46. tough split lane (-0.66); pitcher suppresses HR (-0.46).""", blast="high", contact={'stars': 2, 'k': 25.0, 'batterK': 18.2, 'batterWhiff': 25.9, 'pitcherK': 29.4}),
            row("Jose Ramirez", "S", "+520", 69, "", ["vs Lynch IV"], """0 HR, 94.6 mph EV. Lynch IV SHB→RHB split +0.69, HR risk 0.23. limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 16.8, 'batterK': 11.1, 'batterWhiff': 13.0, 'pitcherK': None}),
            row("Chase DeLauter", "L", "+700", 70, "", ["vs Lynch IV"], """0 HR, 97.3 mph EV. Lynch IV LHB split -0.88, HR risk 0.23. tough split lane (-0.88); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 17.9, 'batterK': 14.9, 'batterWhiff': 12.5, 'pitcherK': None}),
            row("Jo Adell", "R", "+400", 81, "🚀", ["vs Lynch IV"], """0 HR, 100.9 mph EV. Lynch IV RHB split +0.69, HR risk 0.23. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.4, 'batterK': 24.4, 'batterWhiff': 28.2, 'pitcherK': None}),
        ],
    },
    {
        "title": "COL @ CWS - Kyle Freeland 🧤 (L, COL) vs Anthony Kay (L, CWS)",
        "kLines": {'Freeland': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 23.3, 'matchupK': 20.0, 'ownK': 16.0}, 'Kay': {'k': 3.9, 'lo': 2, 'hi': 5, 'bf': 21.8, 'matchupK': 17.7, 'ownK': 17.1}},
        "description": "Tail key data: Park boost -14% (stadium -5%, weather -9%). Freeland 🧤 (HR risk 1.07, vs LHB +0.17, vs RHB +1.20). Kay (HR risk -0.13, vs LHB -1.19, vs RHB +0.40).",
        "rows": [
            row("Randal Grichuk", "R", "+333", 93, "🚀 ⭐ 🌕 💣", ["vs Freeland"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 101.6 mph EV, 40.0% barrels. Freeland RHB split +1.20, HR risk 1.07. park/weather net drag (-14%).""", blast="high", contact={'stars': 4, 'k': 17.4, 'batterK': 17.7, 'batterWhiff': 20.7, 'pitcherK': 16.0}),
            row("Brenton Doyle", "R", "+540", 90, "🌕 💣", ["vs Freeland"], """1 HR, 2 near-HR, 98.1 mph EV, 20.0% barrels. Freeland RHB split +1.20, HR risk 1.07. park/weather net drag (-14%).""", blast="high", contact={'stars': 3, 'k': 22.9, 'batterK': 41.9, 'batterWhiff': 37.9, 'pitcherK': 16.0}),
            row("Munetaka Murakami", "L", "+351", 88, "🌕 💣", ["vs Freeland"], """1 HR, 1 near-HR, 91.5 mph EV, 20.0% barrels. Freeland LHB split +0.17, HR risk 1.07. park/weather net drag (-14%).""", blast="good", contact={'stars': 2, 'k': 27.0, 'batterK': 43.5, 'batterWhiff': 41.7, 'pitcherK': 16.0}),
            row("Connor Norby", "R", "+574", 65, "💎", ["vs Kay"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.6 mph EV, 20.0% barrels. Kay RHB split +0.40, HR risk -0.13. pitcher risk below avg (-0.13); park/weather net drag (-14%).""", blast="good", contact={'stars': 4, 'k': 19.3, 'batterK': 23.7, 'batterWhiff': 21.4, 'pitcherK': 17.1}),
            row("Kyle Karros", "R", "+650", 79, "🌕 💣", ["vs Kay"], """2 HR, 2 near-HR, 91.8 mph EV, 40.0% barrels. Kay RHB split +0.40, HR risk -0.13. pitcher risk below avg (-0.13); park/weather net drag (-14%).""", blast="high", contact={'stars': 3, 'k': 20.1, 'batterK': 23.2, 'batterWhiff': 26.7, 'pitcherK': 17.1}),
            row("Cole Carrigg", "S", "+548", 64, "", ["vs Kay"], """0 HR, 93.8 mph EV, 20.0% barrels. Kay SHB→RHB split +0.40, HR risk -0.13. pitcher risk below avg (-0.13); park/weather net drag (-14%).""", blast="good", contact={'stars': 3, 'k': 21.8, 'batterK': 30.1, 'batterWhiff': 26.4, 'pitcherK': 17.1}),
            row("Ezequiel Tovar", "R", "+680", 55, "", ["vs Kay"], """1 HR, 1 near-HR, 88.0 mph EV, 20.0% barrels. Kay RHB split +0.40, HR risk -0.13. pitcher risk below avg (-0.13); park/weather net drag (-14%).""", blast="good", contact={'stars': 3, 'k': 21.3, 'batterK': 28.8, 'batterWhiff': 28.8, 'pitcherK': 17.1}),
            row("Jordan Beck", "R", "+800", 54, "", ["vs Kay"], """0 HR, 96.2 mph EV. Kay RHB split +0.40, HR risk -0.13. pitcher risk below avg (-0.13); park/weather net drag (-14%).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 39.6, 'batterWhiff': 34.3, 'pitcherK': 17.1}),
        ],
    },
    {
        "title": "HOU @ ATH - Peter Lambert (R, HOU) vs Seth Johnson (R, ATH)",
        "kLines": {'Lambert': {'k': 5.4, 'lo': 4, 'hi': 7, 'bf': 23.1, 'matchupK': 23.2, 'ownK': 23.3}, 'Johnson': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 21.7, 'matchupK': 24.4, 'ownK': 25.7}},
        "description": "Tail key data: Park boost +24% (stadium +29%, weather -4%). Lambert (HR risk -0.09, vs LHB +0.03, vs RHB +0.13). Johnson (HR risk 0.75, vs LHB +1.31, vs RHB +0.24).",
        "rows": [
            row("Henry Bolte", "R", "+520", 83, "🚀 🌕 💣 💎", ["vs Lambert"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 101.2 mph EV, 20.0% barrels. Lambert RHB split +0.13, HR risk -0.09. pitcher risk below avg (-0.09); weather carry headwind (-4%).""", blast="high", contact={'stars': 2, 'k': 26.9, 'batterK': 33.0, 'batterWhiff': 30.4, 'pitcherK': 23.3}),
            row("Jonah Heim", "S", "+770", 52, "", ["vs Lambert"], """0 HR, 91.9 mph EV. Lambert SHB→LHB split +0.03, HR risk -0.09. pitcher risk below avg (-0.09); weather carry headwind (-4%).""", contact={'stars': 4, 'k': 19.6, 'batterK': 15.3, 'batterWhiff': 16.7, 'pitcherK': 23.3}),
            row("Christian Walker", "R", "+420", 90, "🚀 🌕 💣", ["vs Johnson"], """1 HR, 2 near-HR, 102.1 mph EV, 20.0% barrels. Johnson RHB split +0.24, HR risk 0.75. weather carry headwind (-4%).""", blast="high", contact={'stars': 3, 'k': 22.9, 'batterK': 20.5, 'batterWhiff': 26.4, 'pitcherK': 25.7}),
            row("Nelson Velazquez", "R", "+360", 91, "🌕 💣", ["vs Johnson"], """1 HR, 2 near-HR, 99.9 mph EV, 40.0% barrels. Johnson RHB split +0.24, HR risk 0.75. weather carry headwind (-4%).""", blast="high", contact={'stars': 1, 'k': 28.0, 'batterK': 44.1, 'batterWhiff': 43.8, 'pitcherK': 25.7}),
            row("Taylor Trammell", "L", "N/A", 92, "🌕 💣", ["vs Johnson"], """0 HR, 1 near-HR, 99.0 mph EV, 20.0% barrels. Johnson LHB split +1.31, HR risk 0.75. weather carry headwind (-4%); limited recent HR events.""", blast="high", contact={'stars': 1, 'k': 28.1, 'batterK': 34.5, 'batterWhiff': 39.7, 'pitcherK': 25.7}),
            row("Yordan Alvarez", "L", "+240", 97, "⭐ 🌕 💣", ["vs Johnson"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.4 mph EV, 20.0% barrels. Johnson LHB split +1.31, HR risk 0.75. weather carry headwind (-4%).""", blast="high", contact={'stars': 3, 'k': 20.7, 'batterK': 16.3, 'batterWhiff': 21.7, 'pitcherK': 25.7}),
            row("Jeremy Pena", "R", "+470", 88, "🌕 💣", ["vs Johnson"], """1 HR, 1 near-HR, 91.2 mph EV, 20.0% barrels. Johnson RHB split +0.24, HR risk 0.75. weather carry headwind (-4%).""", blast="good", contact={'stars': 1, 'k': 28.0, 'batterK': 32.9, 'batterWhiff': 35.0, 'pitcherK': 25.7}),
        ],
    },
    {
        "title": "LAA @ SEA - Yusei Kikuchi (L, LAA) vs Logan Gilbert 🧤 (R, SEA)",
        "kLines": {'Kikuchi': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 21.7, 'matchupK': 20.0, 'ownK': 20.8}, 'Gilbert': {'k': 6.3, 'lo': 5, 'hi': 8, 'bf': 23.4, 'matchupK': 27.1, 'ownK': 26.6}},
        "description": "Tail key data: Park boost -11% (stadium +0%, weather -11%). Kikuchi (HR risk -0.11, vs LHB -0.46, vs RHB -0.01). Gilbert 🧤 (HR risk 1.01, vs LHB +0.97, vs RHB +0.96).",
        "rows": [
            row("Dominic Canzone", "L", "+520", 65, "", ["vs Kikuchi"], """0 HR, 1 near-HR, 89.2 mph EV, 20.0% barrels. Kikuchi LHB split -0.46, HR risk -0.11. tough split lane (-0.46); pitcher risk below avg (-0.11).""", blast="good", contact={'stars': 4, 'k': 19.0, 'batterK': 15.7, 'batterWhiff': 21.5, 'pitcherK': 20.8}),
            row("Randy Arozarena", "R", "+463", 63, "", ["vs Kikuchi"], """0 HR, 92.3 mph EV. Kikuchi RHB split -0.01, HR risk -0.11. slight split headwind (-0.01); pitcher risk below avg (-0.11).""", blast="good", contact={'stars': 3, 'k': 21.7, 'batterK': 22.2, 'batterWhiff': 26.4, 'pitcherK': 20.8}),
            row("J.P. Crawford", "L", "+930", 64, "⭐", ["vs Kikuchi"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 89.8 mph EV, 40.0% barrels. Kikuchi LHB split -0.46, HR risk -0.11. tough split lane (-0.46); pitcher risk below avg (-0.11).""", blast="good", contact={'stars': 5, 'k': 17.1, 'batterK': 14.1, 'batterWhiff': 13.0, 'pitcherK': 20.8}),
            row("Taylor Ward", "R", "N/A", 58, "", ["vs Kikuchi"], """0 HR, 96.8 mph EV. Kikuchi RHB split -0.01, HR risk -0.11. slight split headwind (-0.01); pitcher risk below avg (-0.11).""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 26.4, 'batterWhiff': 20.8, 'pitcherK': 20.8}),
            row("Jose Siri", "R", "N/A", 90, "🌕 💣", ["vs Gilbert"], """1 HR, 1 near-HR, 97.5 mph EV, 20.0% barrels. Gilbert RHB split +0.96, HR risk 1.01. park/weather net drag (-11%).""", blast="high", contact={'stars': 1, 'k': 29.1, 'batterK': 30.2, 'batterWhiff': 40.4, 'pitcherK': 26.6}),
            row("Zach Neto", "R", "+407", 89, "🌕 💣", ["vs Gilbert"], """1 HR, 2 near-HR, 93.1 mph EV, 40.0% barrels. Gilbert RHB split +0.96, HR risk 1.01. park/weather net drag (-11%).""", blast="good", contact={'stars': 2, 'k': 26.9, 'batterK': 27.2, 'batterWhiff': 28.5, 'pitcherK': 26.6}),
            row("Mike Trout", "R", "+448", 92, "🚀 🌕 💣", ["vs Gilbert"], """0 HR, 1 near-HR, 100.1 mph EV, 20.0% barrels. Gilbert RHB split +0.96, HR risk 1.01. park/weather net drag (-11%); limited recent HR events.""", blast="high", contact={'stars': 1, 'k': 28.1, 'batterK': 27.8, 'batterWhiff': 34.3, 'pitcherK': 26.6}),
            row("Christian Moore", "R", "+910", 81, "", ["vs Gilbert"], """1 HR, 2 near-HR, 90.5 mph EV, 40.0% barrels. Gilbert RHB split +0.96, HR risk 1.01. park/weather net drag (-11%).""", blast="good", contact={'stars': 1, 'k': 28.8, 'batterK': 33.3, 'batterWhiff': 32.5, 'pitcherK': 26.6}),
        ],
    },
    {
        "title": "LAD @ SF - Justin Wrobleski (L, LAD) vs Carson Seymour 🧤 (R, SF)",
        "kLines": {'Wrobleski': {'k': 5.7, 'lo': 4, 'hi': 7, 'bf': 23.4, 'matchupK': 24.3, 'ownK': 23.8}, 'Seymour': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 21.7, 'matchupK': 18.8, 'ownK': 12.5}},
        "description": "Tail key data: Park boost -19% (stadium -13%, weather -6%). Wrobleski (BAA vs LHB .238, vs RHB .238, HR/9 1.37). Seymour 🧤 (HR risk 1.03, vs LHB +1.28, vs RHB +0.59).",
        "rows": [
            row("Freddie Freeman", "L", "+630", 80, "", ["vs Seymour"], """0 HR, 94.2 mph EV, 20.0% barrels. Seymour LHB split +1.28, HR risk 1.03. park/weather net drag (-19%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.8, 'batterK': 25.6, 'batterWhiff': 31.8, 'pitcherK': 12.5}),
            row("Andy Pages", "R", "+730", 80, "", ["vs Seymour"], """1 HR, 1 near-HR, 87.5 mph EV, 20.0% barrels. Seymour RHB split +0.59, HR risk 1.03. park/weather net drag (-19%); lighter EV form (87.5 mph).""", blast="good", contact={'stars': 4, 'k': 18.5, 'batterK': 18.3, 'batterWhiff': 18.0, 'pitcherK': 12.5}),
            row("Will Smith", "R", "N/A", 87, "", ["vs Seymour"], """1 HR, 1 near-HR, 90.8 mph EV, 20.0% barrels. Seymour RHB split +0.59, HR risk 1.03. park/weather net drag (-19%).""", blast="good", contact={'stars': 4, 'k': 17.8, 'batterK': 15.7, 'batterWhiff': 16.5, 'pitcherK': 12.5}),
            row("Marcelo Mayer", "L", "N/A", 57, "", ["vs Wrobleski"], """0 HR, 2 near-HR, 89.4 mph EV, 20.0% barrels. limited split/risk sample; park/weather net drag (-19%).""", blast="good", contact={'stars': 2, 'k': 25.4, 'batterK': 30.0, 'batterWhiff': 31.1, 'pitcherK': 23.8}),
            row("Grant McCray", "L", "N/A", 66, "🌕 💣", ["vs Wrobleski"], """0 HR, 97.7 mph EV, 20.0% barrels. limited split/risk sample; park/weather net drag (-19%).""", blast="high", contact={'stars': 2, 'k': 26.0, 'batterK': 32.6, 'batterWhiff': 35.6, 'pitcherK': 23.8}),
            row("Andrew Knizner", "R", "+1180", 49, "", ["vs Wrobleski"], """0 HR, 93.7 mph EV. limited split/risk sample; park/weather net drag (-19%).""", blast="good", contact={'stars': 3, 'k': 22.4, 'batterK': 17.5, 'batterWhiff': 26.2, 'pitcherK': 23.8}),
        ],
    },
    {
        "title": "NYM @ WSH - Sean Manaea (L, NYM) vs DJ Herz (L, WSH)",
        "kLines": {'Manaea': {'k': 5.6, 'lo': 4, 'hi': 7, 'bf': 23.6, 'matchupK': 23.8, 'ownK': 22.8}, 'Herz': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 21.3, 'matchupK': 21.8, 'ownK': 21.1}},
        "description": "Tail key data: Park boost -8% (stadium +5%, weather -13%). Manaea (HR risk 0.53, vs LHB -0.48, vs RHB +0.73). Herz (HR risk 0.00, vs LHB +0.00, vs RHB +2.09).",
        "rows": [
            row("Andres Chaparro", "R", "+433", 87, "🚀 🌕 💣", ["vs Manaea"], """1 HR, 2 near-HR, 100.1 mph EV, 20.0% barrels. Manaea RHB split +0.73, HR risk 0.53. park/weather net drag (-8%).""", blast="high", contact={'stars': 2, 'k': 27.0, 'batterK': 29.2, 'batterWhiff': 40.3, 'pitcherK': 22.8}),
            row("James Wood", "L", "+468", 69, "🚀", ["vs Manaea"], """0 HR, 100.6 mph EV. Manaea LHB split -0.48, HR risk 0.53. tough split lane (-0.48); park/weather net drag (-8%).""", blast="good", contact={'stars': 2, 'k': 24.2, 'batterK': 28.6, 'batterWhiff': 24.8, 'pitcherK': 22.8}),
            row("Marcus Semien", "R", "N/A", 57, "", ["vs Herz"], """0 HR, 85.5 mph EV. Herz RHB split +2.09, HR risk 0.00. park/weather net drag (-8%); limited recent HR events.""", contact={'stars': 5, 'k': 16.3, 'batterK': 7.2, 'batterWhiff': 14.9, 'pitcherK': 21.1}),
            row("Juan Soto", "L", "N/A", 64, "⭐", ["vs Herz"], """Worst Pickz Favorite. 0 HR, 94.6 mph EV. Herz LHB split +0.00, HR risk 0.00. park/weather net drag (-8%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.8, 'batterK': 14.7, 'batterWhiff': 19.9, 'pitcherK': 21.1}),
            row("Francisco Alvarez", "R", "N/A", 80, "", ["vs Herz"], """0 HR, 96.9 mph EV. Herz RHB split +2.09, HR risk 0.00. park/weather net drag (-8%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 26.7, 'batterK': 34.7, 'batterWhiff': 34.0, 'pitcherK': 21.1}),
        ],
    },
    {
        "title": "PIT @ DET - Jared Jones (R, PIT) vs River Ryan (R, DET)",
        "kLines": {'Jones': {'k': 5.8, 'lo': 4, 'hi': 7, 'bf': 20.5, 'matchupK': 28.2, 'ownK': 29.8}, 'Ryan': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 20.3, 'matchupK': 22.3, 'ownK': 25.0}},
        "description": "Tail key data: Park boost -9% (stadium -11%, weather +2%). Jones (HR risk -0.59, vs LHB -0.02, vs RHB -0.84). Ryan - thin book: 3.0 IP this season (23.1 career IP, 1.16 ERA).",
        "rows": [
            row("Spencer Torkelson", "R", "+585", 80, "🌕 💣", ["vs Jones"], """2 HR, 2 near-HR, 95.0 mph EV, 20.0% barrels. Jones RHB split -0.84, HR risk -0.59. tough split lane (-0.84); pitcher suppresses HR (-0.59).""", blast="high", contact={'stars': 1, 'k': 32.7, 'batterK': 34.6, 'batterWhiff': 40.2, 'pitcherK': 29.8}),
            row("Eduardo Valencia", "R", "+660", 72, "🌕 💣", ["vs Jones"], """0 HR, 1 near-HR, 98.4 mph EV, 20.0% barrels. Jones RHB split -0.84, HR risk -0.59. tough split lane (-0.84); pitcher suppresses HR (-0.59).""", blast="high", contact={'stars': 2, 'k': 25.8, 'batterK': 19.2, 'batterWhiff': 26.7, 'pitcherK': 29.8}),
            row("Riley Greene", "L", "+460", 64, "", ["vs Jones"], """0 HR, 1 near-HR, 88.6 mph EV, 20.0% barrels. Jones LHB split -0.02, HR risk -0.59. slight split headwind (-0.02); pitcher suppresses HR (-0.59).""", blast="good", contact={'stars': 2, 'k': 25.2, 'batterK': 18.6, 'batterWhiff': 25.8, 'pitcherK': 29.8}),
            row("Oneil Cruz", "L", "+344", 86, "🚀 🌕 💣", ["vs Ryan"], """1 HR, 1 near-HR, 101.1 mph EV, 20.0% barrels. limited split/risk sample; park/weather net drag (-9%).""", blast="high", contact={'stars': 2, 'k': 24.8, 'batterK': 27.5, 'batterWhiff': 30.5, 'pitcherK': 25.0}),
            row("Konnor Griffin", "R", "+680", 73, "🌕 💣", ["vs Ryan"], """0 HR, 1 near-HR, 97.1 mph EV, 20.0% barrels. limited split/risk sample; park/weather net drag (-9%).""", blast="high", contact={'stars': 3, 'k': 21.0, 'batterK': 19.3, 'batterWhiff': 22.3, 'pitcherK': 25.0}),
        ],
    },
    {
        "title": "STL @ MIL - Andre Pallante (R, STL) vs Jacob Misiorowski (R, MIL)",
        "kLines": {'Pallante': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 23.1, 'matchupK': 17.7, 'ownK': 14.7}, 'Misiorowski': {'k': 7.3, 'lo': 6, 'hi': 9, 'bf': 22.2, 'matchupK': 33.0, 'ownK': 35.7}},
        "description": "Tail key data: Park boost -10% (stadium -1%, weather -9%). Pallante (HR risk -1.13, vs LHB -0.43, vs RHB -1.24). Misiorowski (HR risk -1.00, vs LHB -0.76, vs RHB -0.66).",
        "rows": [
            row("William Contreras", "R", "+545", 61, "", ["vs Pallante"], """0 HR, 1 near-HR, 95.2 mph EV, 20.0% barrels. Pallante RHB split -1.24, HR risk -1.13. tough split lane (-1.24); pitcher suppresses HR (-1.13).""", blast="good", contact={'stars': 4, 'k': 17.5, 'batterK': 20.9, 'batterWhiff': 23.1, 'pitcherK': 14.7}),
            row("Bo Naylor", "L", "N/A", 69, "🌕 💣", ["vs Pallante"], """1 HR, 2 near-HR, 99.6 mph EV, 40.0% barrels. Pallante LHB split -0.43, HR risk -1.13. tough split lane (-0.43); pitcher suppresses HR (-1.13).""", blast="high", contact={'stars': 5, 'k': 16.6, 'batterK': 26.2, 'batterWhiff': 13.4, 'pitcherK': 14.7}),
            row("Garrett Mitchell", "L", "+750", 52, "", ["vs Pallante"], """0 HR, 89.8 mph EV. Pallante LHB split -0.43, HR risk -1.13. tough split lane (-0.43); pitcher suppresses HR (-1.13).""", contact={'stars': 3, 'k': 21.7, 'batterK': 33.3, 'batterWhiff': 32.8, 'pitcherK': 14.7}),
            row("Brice Turang", "L", "+870", 64, "", ["vs Pallante"], """0 HR, 1 near-HR, 93.0 mph EV, 20.0% barrels. Pallante LHB split -0.43, HR risk -1.13. tough split lane (-0.43); pitcher suppresses HR (-1.13).""", blast="good", contact={'stars': 4, 'k': 19.2, 'batterK': 25.0, 'batterWhiff': 27.5, 'pitcherK': 14.7}),
            row("Alec Burleson", "L", "+460", 89, "🚀 ⭐ 🌕 💣", ["vs Misiorowski"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 102.3 mph EV, 60.0% barrels. Misiorowski LHB split -0.76, HR risk -1.00. tough split lane (-0.76); pitcher suppresses HR (-1.00).""", blast="high", contact={'stars': 1, 'k': 30.6, 'batterK': 26.3, 'batterWhiff': 24.9, 'pitcherK': 35.7}),
            row("Ivan Herrera", "R", "+750", 65, "", ["vs Misiorowski"], """1 HR, 2 near-HR, 91.6 mph EV, 40.0% barrels. Misiorowski RHB split -0.66, HR risk -1.00. tough split lane (-0.66); pitcher suppresses HR (-1.00).""", blast="good", contact={'stars': 1, 'k': 31.2, 'batterK': 27.9, 'batterWhiff': 24.7, 'pitcherK': 35.7}),
            row("Jordan Walker", "R", "+500", 64, "⭐", ["vs Misiorowski"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.2 mph EV, 20.0% barrels. Misiorowski RHB split -0.66, HR risk -1.00. tough split lane (-0.66); pitcher suppresses HR (-1.00).""", blast="good", contact={'stars': 1, 'k': 36.4, 'batterK': 35.1, 'batterWhiff': 40.1, 'pitcherK': 35.7}),
            row("JJ Wetherholt", "L", "+750", 62, "", ["vs Misiorowski"], """0 HR, 93.3 mph EV, 20.0% barrels. Misiorowski LHB split -0.76, HR risk -1.00. tough split lane (-0.76); pitcher suppresses HR (-1.00).""", blast="good", contact={'stars': 1, 'k': 29.2, 'batterK': 25.0, 'batterWhiff': 20.4, 'pitcherK': 35.7}),
            row("Leonardo Bernal", "S", "+600", 52, "", ["vs Misiorowski"], """0 HR, 92.4 mph EV. Misiorowski SHB→LHB split -0.76, HR risk -1.00. tough split lane (-0.76); pitcher suppresses HR (-1.00).""", blast="good", contact={'stars': 1, 'k': 30.9, 'batterK': 25.9, 'batterWhiff': 26.6, 'pitcherK': 35.7}),
        ],
    },
    {
        "title": "TB @ PHI - Nick Martinez (R, TB) vs Zack Wheeler (R, PHI)",
        "kLines": {'Martinez': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 23.2, 'matchupK': 18.4, 'ownK': 17.6}, 'Wheeler': {'k': 5.8, 'lo': 4, 'hi': 7, 'bf': 22.8, 'matchupK': 25.4, 'ownK': 28.8}},
        "description": "Tail key data: Park boost -11% (stadium +15%, weather -26%). Martinez (HR risk -0.16, vs LHB -0.11, vs RHB +0.06). Wheeler (HR risk -0.80, vs LHB -0.38, vs RHB -0.69).",
        "rows": [
            row("J.T. Realmuto", "R", "+830", 58, "", ["vs Martinez"], """0 HR, 93.6 mph EV. Martinez RHB split +0.06, HR risk -0.16. pitcher risk below avg (-0.16); park/weather net drag (-11%).""", blast="good", contact={'stars': 3, 'k': 21.0, 'batterK': 26.7, 'batterWhiff': 27.1, 'pitcherK': 17.6}),
            row("Alec Bohm", "R", "+810", 50, "", ["vs Martinez"], """0 HR, 89.8 mph EV. Martinez RHB split +0.06, HR risk -0.16. pitcher risk below avg (-0.16); park/weather net drag (-11%).""", contact={'stars': 5, 'k': 16.2, 'batterK': 12.8, 'batterWhiff': 17.2, 'pitcherK': 17.6}),
            row("Trea Turner", "R", "+740", 50, "", ["vs Martinez"], """0 HR, 91.8 mph EV. Martinez RHB split +0.06, HR risk -0.16. pitcher risk below avg (-0.16); park/weather net drag (-11%).""", contact={'stars': 4, 'k': 18.9, 'batterK': 16.9, 'batterWhiff': 29.0, 'pitcherK': 17.6}),
            row("Jonathan Aranda", "L", "+750", 82, "🌕 💣", ["vs Wheeler"], """2 HR, 2 near-HR, 97.5 mph EV, 20.0% barrels. Wheeler LHB split -0.38, HR risk -0.80. slight split headwind (-0.38); pitcher suppresses HR (-0.80).""", blast="high", contact={'stars': 1, 'k': 29.7, 'batterK': 33.7, 'batterWhiff': 28.5, 'pitcherK': 28.8}),
            row("Cedric Mullins", "L", "+910", 53, "", ["vs Wheeler"], """1 HR, 1 near-HR, 90.1 mph EV, 20.0% barrels. Wheeler LHB split -0.38, HR risk -0.80. slight split headwind (-0.38); pitcher suppresses HR (-0.80).""", blast="good", contact={'stars': 3, 'k': 21.7, 'batterK': 13.3, 'batterWhiff': 14.9, 'pitcherK': 28.8}),
            row("Victor Mesa Jr.", "L", "+830", 75, "🚀 🌕 💣", ["vs Wheeler"], """0 HR, 1 near-HR, 101.8 mph EV, 20.0% barrels. Wheeler LHB split -0.38, HR risk -0.80. slight split headwind (-0.38); pitcher suppresses HR (-0.80).""", blast="high", contact={'stars': 2, 'k': 24.2, 'batterK': 15.5, 'batterWhiff': 25.6, 'pitcherK': 28.8}),
            row("Yandy Diaz", "R", "+920", 43, "", ["vs Wheeler"], """0 HR, 90.5 mph EV. Wheeler RHB split -0.69, HR risk -0.80. tough split lane (-0.69); pitcher suppresses HR (-0.80).""", contact={'stars': 3, 'k': 20.8, 'batterK': 13.3, 'batterWhiff': 15.5, 'pitcherK': 28.8}),
        ],
    },
    {
        "title": "TEX @ MIN - MacKenzie Gore (L, TEX) vs Dean Kremer (R, MIN)",
        "kLines": {'Gore': {'k': 4.0, 'lo': 2, 'hi': 6, 'bf': 22.3, 'matchupK': 17.9, 'ownK': 17.4}, 'Kremer': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 21.4, 'matchupK': 24.3, 'ownK': 22.7}},
        "description": "Tail key data: Park boost -15% (stadium -7%, weather -8%). Gore (HR risk -0.44, vs LHB -0.35, vs RHB -0.34). Kremer (HR risk 0.34, vs LHB +0.63, vs RHB +0.30).",
        "rows": [
            row("Ryan Kreidler", "R", "N/A", 76, "🌕 💣", ["vs Gore"], """2 HR, 2 near-HR, 97.5 mph EV, 25.0% barrels. Gore RHB split -0.34, HR risk -0.44. slight split headwind (-0.34); pitcher suppresses HR (-0.44).""", blast="high", contact={'stars': 3, 'k': 21.4, 'batterK': 29.3, 'batterWhiff': 30.7, 'pitcherK': 17.4}),
            row("Brooks Lee", "S", "N/A", 40, "", ["vs Gore"], """0 HR, 74.6 mph EV. Gore SHB→RHB split -0.34, HR risk -0.44. slight split headwind (-0.34); pitcher suppresses HR (-0.44).""", contact={'stars': 4, 'k': 18.6, 'batterK': 18.1, 'batterWhiff': 24.0, 'pitcherK': 17.4}),
            row("Jake Burger", "R", "N/A", 84, "⭐ 🌕 💣", ["vs Kremer"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 88.7 mph EV, 25.0% barrels. Kremer RHB split +0.30, HR risk 0.34. park/weather net drag (-15%).""", blast="high", contact={'stars': 2, 'k': 25.9, 'batterK': 27.4, 'batterWhiff': 35.8, 'pitcherK': 22.7}),
            row("Brandon Nimmo", "L", "N/A", 53, "", ["vs Kremer"], """0 HR, 87.4 mph EV. Kremer LHB split +0.63, HR risk 0.34. park/weather net drag (-15%); limited recent HR events.""", contact={'stars': 2, 'k': 27.2, 'batterK': 33.3, 'batterWhiff': 34.5, 'pitcherK': 22.7}),
            row("Corey Seager", "L", "N/A", 62, "⭐", ["vs Kremer"], """Worst Pickz Favorite. 0 HR, 83.5 mph EV, 12.5% barrels. Kremer LHB split +0.63, HR risk 0.34. park/weather net drag (-15%); limited recent HR events.""", contact={'stars': 2, 'k': 24.6, 'batterK': 25.0, 'batterWhiff': 32.6, 'pitcherK': 22.7}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-27")

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

    out = ROOT / '_games-0927.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
