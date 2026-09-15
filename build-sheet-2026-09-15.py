#!/usr/bin/env python3
"""Generate games[] block for 2026-09-15 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Corey Seager (L)",
    "Junior Caminero (R)",
    "Manny Machado (R)",
    "Victor Mesa Jr. (L)",
}

GEMS = {
    "Alejandro Kirk (R)",
    "Coby Mayo (R)",
    "Fernando Tatis Jr. (R)",
    "Lars Nootbaar (L)",
    "Otto Lopez (R)",
    "Salvador Perez (R)",
    "Spencer Torkelson (R)",
    "Ty France (R)",
    "Will Smith (R)",
    "William Contreras (R)",
}

PLAYER_TEAMS = {
    "Aaron Judge (R)": "NYY",
    "Adley Rutschman (S)": "BOS",
    "Alec Bohm (R)": "PHI",
    "Alejandro Kirk (R)": "TOR",
    "Andrew Pinckney (R)": "WSH",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Brett Callahan (L)": "DET",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Cal Raleigh (S)": "SEA",
    "Cam Smith (R)": "HOU",
    "Coby Mayo (R)": "BAL",
    "Cole Carrigg (S)": "COL",
    "Colt Keith (L)": "DET",
    "Connor Norby (R)": "COL",
    "Corey Seager (L)": "TEX",
    "Dillon Dingler (R)": "DET",
    "Dylan Crews (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Eugenio Suarez (R)": "CIN",
    "Ezequiel Duran (R)": "TEX",
    "Fernando Tatis Jr. (R)": "SD",
    "Gabriel Moreno (R)": "ARI",
    "Garrett Mitchell (L)": "MIL",
    "George Lombard Jr. (R)": "NYY",
    "George Springer (R)": "TOR",
    "Graham Pauley (L)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ivan Herrera (R)": "STL",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "Jackson Merrill (L)": "SD",
    "Jake Burger (R)": "TEX",
    "James Wood (L)": "WSH",
    "Javier Sanoja (R)": "MIA",
    "Jeremiah Jackson (R)": "BAL",
    "Joey Ortiz (R)": "MIL",
    "Jonathan Aranda (L)": "TB",
    "Jose Siri (R)": "LAA",
    "Jung Hoo Lee (L)": "SF",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kevin McGonigle (L)": "DET",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Lars Nootbaar (L)": "ARI",
    "Lazaro Montes (L)": "SEA",
    "Leonardo Bernal (S)": "STL",
    "Luis Garcia Jr. (L)": "NYY",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Michael Arroyo (R)": "SEA",
    "Michael Busch (L)": "CHC",
    "Mickey Gasper (S)": "BOS",
    "Mike Trout (R)": "LAA",
    "Moises Ballesteros (L)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Otto Lopez (R)": "MIA",
    "Patrick Bailey (S)": "CLE",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Flores (R)": "PIT",
    "Randal Grichuk (R)": "CWS",
    "Randy Arozarena (R)": "SEA",
    "Roman Anthony (L)": "BOS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan Kreidler (R)": "MIN",
    "Salvador Perez (R)": "KC",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Taylor Trammell (L)": "HOU",
    "Ty France (R)": "SD",
    "Victor Mesa Jr. (L)": "TB",
    "Vinnie Pasquantino (L)": "KC",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Will Smith (R)": "LAD",
    "William Contreras (R)": "MIL",
    "Xander Bogaerts (R)": "SD",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("BAL @ NYM", "Manaea"),
    ("SEA @ LAA", "Gilbert"),
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
        "title": "ATH @ TB - Jack Perkins (R, ATH) vs Griffin Jax (R, TB)",
        "kLines": {'Perkins': {'k': 4.2, 'lo': 3, 'hi': 6, 'bf': 21.5, 'matchupK': 19.6, 'ownK': 22.5}, 'Jax': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 19.2, 'matchupK': 26.0, 'ownK': 27.0}},
        "description": "Tail key data: Park boost -4% (stadium -5%, weather +1%). Perkins (HR risk 0.63, vs LHB +0.48, vs RHB +0.51). Jax (HR risk 0.04, vs LHB +0.55, vs RHB -0.45).",
        "rows": [
            row("Jonathan Aranda", "L", "+590", 94, "🌕 💣", ["vs Perkins"], """2 HR, 3 near-HR, 95.7 mph EV, 12.5% barrels. Perkins LHB split +0.48, HR risk 0.63.""", blast="high", contact={'stars': 3, 'k': 22.6, 'batterK': 23.5, 'batterWhiff': 24.3, 'pitcherK': 22.5}),
            row("Victor Mesa Jr.", "L", "+540", 90, "⭐ 🌕 💣", ["vs Perkins"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.5 mph EV, 25.0% barrels. Perkins LHB split +0.48, HR risk 0.63.""", blast="high", contact={'stars': 4, 'k': 19.6, 'batterK': 11.1, 'batterWhiff': 23.4, 'pitcherK': 22.5}),
            row("Junior Caminero", "R", "+289", 86, "⭐", ["vs Perkins"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.3 mph EV, 12.5% barrels. Perkins RHB split +0.51, HR risk 0.63.""", blast="good", contact={'stars': 4, 'k': 19.7, 'batterK': 15.9, 'batterWhiff': 20.6, 'pitcherK': 22.5}),
            row("Zack Gelof", "R", "+592", 79, "", ["vs Jax"], """1 HR, 1 near-HR, 97.0 mph EV, 12.5% barrels. Jax RHB split -0.45, HR risk 0.04. tough split lane (-0.45).""", blast="good", contact={'stars': 1, 'k': 27.6, 'batterK': 26.1, 'batterWhiff': 34.3, 'pitcherK': 27.0}),
        ],
    },
    {
        "title": "ATL @ CHC - Martin Perez (L, ATL) vs Kevin Gausman (R, CHC)",
        "kLines": {'Perez': {'k': 3.5, 'lo': 2, 'hi': 5, 'bf': 21.5, 'matchupK': 16.2, 'ownK': 16.8}, 'Gausman': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 23.2, 'matchupK': 22.6, 'ownK': 23.3}},
        "description": "Tail key data: Park boost -3% (stadium -2%, weather -1%). Perez (HR risk -0.77, vs LHB +0.86, vs RHB -1.16). Gausman (HR risk 0.84, vs LHB -0.24, vs RHB +1.50).",
        "rows": [
            row("Michael Busch", "L", "+625", 65, "", ["vs Perez"], """1 HR, 1 near-HR, 89.7 mph EV, 12.5% barrels. Perez LHB split +0.86, HR risk -0.77. pitcher suppresses HR (-0.77).""", blast="good", contact={'stars': 3, 'k': 20.9, 'batterK': 26.2, 'batterWhiff': 27.7, 'pitcherK': 16.8}),
            row("Pete Crow Armstrong", "L", "+394", 61, "", ["vs Perez"], """0 HR, 89.9 mph EV. Perez LHB split +0.86, HR risk -0.77. pitcher suppresses HR (-0.77); limited recent HR events.""", contact={'stars': 4, 'k': 19.4, 'batterK': 22.6, 'batterWhiff': 23.9, 'pitcherK': 16.8}),
            row("Matt Olson", "L", "+349", 86, "", ["vs Gausman"], """1 HR, 1 near-HR, 95.2 mph EV, 12.5% barrels. Gausman LHB split -0.24, HR risk 0.84. slight split headwind (-0.24).""", blast="good", contact={'stars': 3, 'k': 23.4, 'batterK': 22.6, 'batterWhiff': 28.0, 'pitcherK': 23.3}),
            row("Ronald Acuna Jr.", "R", "+395", 81, "", ["vs Gausman"], """0 HR, 92.2 mph EV. Gausman RHB split +1.50, HR risk 0.84. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.3, 'batterK': 15.9, 'batterWhiff': 26.9, 'pitcherK': 23.3}),
            row("Austin Riley", "R", "+525", 87, "", ["vs Gausman"], """1 HR, 2 near-HR, 93.9 mph EV, 25.0% barrels. Gausman RHB split +1.50, HR risk 0.84.""", blast="good", contact={'stars': 2, 'k': 24.6, 'batterK': 29.7, 'batterWhiff': 25.8, 'pitcherK': 23.3}),
        ],
    },
    {
        "title": "BAL @ NYM - Shane Baz (R, BAL) vs Sean Manaea 🧤 (L, NYM)",
        "kLines": {'Baz': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 24.3, 'matchupK': 21.4, 'ownK': 21.3}, 'Manaea': {'k': 5.4, 'lo': 4, 'hi': 7, 'bf': 23.6, 'matchupK': 22.7, 'ownK': 20.6}},
        "description": "Tail key data: Park boost -13% (stadium -2%, weather -11%). Baz (HR risk -0.04, vs LHB +0.53, vs RHB -0.90). Manaea 🧤 (HR risk 1.43, vs LHB -0.10, vs RHB +1.33).",
        "rows": [
            row("Pete Alonso", "R", "+300", 94, "🌕 💣", ["vs Manaea"], """0 HR, 1 near-HR, 99.2 mph EV, 25.0% barrels. Manaea RHB split +1.33, HR risk 1.43. park/weather net drag (-13%); limited recent HR events.""", blast="high", contact={'stars': 3, 'k': 22.5, 'batterK': 24.7, 'batterWhiff': 27.6, 'pitcherK': 20.6}),
            row("Coby Mayo", "R", "+350", 89, "🌕 💣 💎", ["vs Manaea"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 82.5 mph EV, 12.5% barrels. Manaea RHB split +1.33, HR risk 1.43. park/weather net drag (-13%); lighter EV form (82.5 mph).""", blast="good", contact={'stars': 3, 'k': 21.9, 'batterK': 24.7, 'batterWhiff': 25.3, 'pitcherK': 20.6}),
            row("Jeremiah Jackson", "R", "+800", 81, "", ["vs Manaea"], """0 HR, 1 near-HR, 92.8 mph EV, 37.5% barrels. Manaea RHB split +1.33, HR risk 1.43. park/weather net drag (-13%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.0, 'batterK': 30.0, 'batterWhiff': 36.0, 'pitcherK': 20.6}),
        ],
    },
    {
        "title": "BOS @ TEX - Patrick Sandoval (L, BOS) vs Jacob deGrom (R, TEX)",
        "kLines": {'Sandoval': {'k': 4.9, 'lo': 3, 'hi': 7, 'bf': 22.5, 'matchupK': 22.0, 'ownK': 22.2}, 'deGrom': {'k': 6.5, 'lo': 5, 'hi': 8, 'bf': 21.5, 'matchupK': 30.4, 'ownK': 32.0}},
        "description": "Tail key data: Park boost -12% (stadium -12%, weather -1%). Sandoval (HR risk -0.08, vs LHB -0.64, vs RHB +0.16). deGrom (HR risk -0.29, vs LHB -0.02, vs RHB -0.33).",
        "rows": [
            row("Jake Burger", "R", "+428", 92, "🌕 💣", ["vs Sandoval"], """3 HR, 3 near-HR, 94.9 mph EV, 50.0% barrels. Sandoval RHB split +0.16, HR risk -0.08. pitcher risk below avg (-0.08); park/weather net drag (-12%).""", blast="high", contact={'stars': 2, 'k': 26.0, 'batterK': 28.4, 'batterWhiff': 36.7, 'pitcherK': 22.2}),
            row("Ezequiel Duran", "R", "+820", 76, "", ["vs Sandoval"], """1 HR, 1 near-HR, 93.7 mph EV, 12.5% barrels. Sandoval RHB split +0.16, HR risk -0.08. pitcher risk below avg (-0.08); park/weather net drag (-12%).""", blast="good", contact={'stars': 3, 'k': 21.8, 'batterK': 20.7, 'batterWhiff': 25.3, 'pitcherK': 22.2}),
            row("Corey Seager", "L", "+470", 76, "⭐ 🌕 💣", ["vs Sandoval"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 88.3 mph EV, 25.0% barrels. Sandoval LHB split -0.64, HR risk -0.08. tough split lane (-0.64); pitcher risk below avg (-0.08).""", blast="high", contact={'stars': 3, 'k': 21.2, 'batterK': 16.9, 'batterWhiff': 28.5, 'pitcherK': 22.2}),
            row("Adley Rutschman", "S", "+576", 62, "", ["vs deGrom"], """1 HR, 1 near-HR, 91.5 mph EV, 12.5% barrels. deGrom SHB→LHB split -0.02, HR risk -0.29. slight split headwind (-0.02); pitcher risk below avg (-0.29).""", blast="good", contact={'stars': 2, 'k': 26.9, 'batterK': 24.4, 'batterWhiff': 21.1, 'pitcherK': 32.0}),
            row("Mickey Gasper", "S", "+620", 78, "", ["vs deGrom"], """1 HR, 1 near-HR, 92.2 mph EV, 25.0% barrels. deGrom SHB→LHB split -0.02, HR risk -0.29. slight split headwind (-0.02); pitcher risk below avg (-0.29).""", blast="good", contact={'stars': 3, 'k': 22.5, 'batterK': 11.3, 'batterWhiff': 16.7, 'pitcherK': 32.0}),
            row("Roman Anthony", "L", "+520", 72, "", ["vs deGrom"], """0 HR, 1 near-HR, 95.0 mph EV, 25.0% barrels. deGrom LHB split -0.02, HR risk -0.29. slight split headwind (-0.02); pitcher risk below avg (-0.29).""", blast="good", contact={'stars': 1, 'k': 29.1, 'batterK': 26.7, 'batterWhiff': 27.0, 'pitcherK': 32.0}),
        ],
    },
    {
        "title": "CWS @ CLE - Chris Murphy (L, CWS) vs Foster Griffin (L, CLE)",
        "kLines": {'Murphy': {'k': 1.3, 'lo': 0, 'hi': 3, 'bf': 5.9, 'matchupK': 22.8, 'ownK': 31.0}, 'Griffin': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 23.0, 'matchupK': 18.8, 'ownK': 16.2}},
        "description": "Tail key data: Park boost +4% (stadium -4%, weather +8%). Murphy (BAA vs LHB .237, vs RHB .233, HR/9 0.56). Griffin (HR risk -0.53, vs LHB +0.41, vs RHB -0.72).",
        "rows": [
            row("Patrick Bailey", "S", "+800", 50, "", ["vs Murphy"], """0 HR, 87.0 mph EV. limited split/risk sample; limited recent HR events.""", contact={'stars': 2, 'k': 24.7, 'batterK': 26.7, 'batterWhiff': 25.7, 'pitcherK': 31.0}),
            row("Randal Grichuk", "R", "+471", 77, "🚀 🌕 💣", ["vs Griffin"], """1 HR, 1 near-HR, 100.4 mph EV, 25.0% barrels. Griffin RHB split -0.72, HR risk -0.53. tough split lane (-0.72); pitcher suppresses HR (-0.53).""", blast="high", contact={'stars': 4, 'k': 19.5, 'batterK': 25.6, 'batterWhiff': 26.1, 'pitcherK': 16.2}),
            row("Munetaka Murakami", "L", "+380", 85, "🌕 💣", ["vs Griffin"], """1 HR, 2 near-HR, 97.5 mph EV, 25.0% barrels. Griffin LHB split +0.41, HR risk -0.53. pitcher suppresses HR (-0.53).""", blast="high", contact={'stars': 1, 'k': 27.8, 'batterK': 44.2, 'batterWhiff': 44.1, 'pitcherK': 16.2}),
        ],
    },
    {
        "title": "DET @ TOR - Drew Anderson (R, DET) vs Braydon Fisher (R, TOR)",
        "kLines": {'Anderson': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 19.9, 'matchupK': 18.4, 'ownK': 20.0}, 'Fisher': {'k': 1.3, 'lo': 0, 'hi': 3, 'bf': 5.0, 'matchupK': 26.9, 'ownK': 37.5}},
        "description": "Tail key data: Park boost +19% (stadium +6%, weather +13%). Anderson (HR risk 0.44, vs LHB +0.48, vs RHB +0.15). Fisher (BAA vs LHB .223, vs RHB .185, HR/9 0.99).",
        "rows": [
            row("Alejandro Kirk", "R", "+710", 90, "🌕 💣 💎", ["vs Anderson"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 97.4 mph EV, 25.0% barrels. Anderson RHB split +0.15, HR risk 0.44.""", blast="high", contact={'stars': 5, 'k': 17.1, 'batterK': 14.0, 'batterWhiff': 14.1, 'pitcherK': 20.0}),
            row("Kazuma Okamoto", "R", "+390", 83, "", ["vs Anderson"], """1 HR, 2 near-HR, 86.7 mph EV, 25.0% barrels. Anderson RHB split +0.15, HR risk 0.44. lighter EV form (86.7 mph).""", blast="good", contact={'stars': 3, 'k': 22.0, 'batterK': 22.2, 'batterWhiff': 29.3, 'pitcherK': 20.0}),
            row("George Springer", "R", "+511", 73, "", ["vs Anderson"], """0 HR, 97.2 mph EV. Anderson RHB split +0.15, HR risk 0.44. limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.3, 'batterK': 14.5, 'batterWhiff': 24.1, 'pitcherK': 20.0}),
            row("Vladimir Guerrero Jr.", "R", "+590", 72, "", ["vs Anderson"], """0 HR, 97.5 mph EV. Anderson RHB split +0.15, HR risk 0.44. limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.0, 'batterK': 13.8, 'batterWhiff': 20.0, 'pitcherK': 20.0}),
            row("Spencer Torkelson", "R", "+490", 87, "🌕 💣 💎", ["vs Fisher"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 95.4 mph EV, 12.5% barrels. limited split/risk sample.""", blast="high", contact={'stars': 1, 'k': 29.2, 'batterK': 34.8, 'batterWhiff': 36.0, 'pitcherK': 37.5}),
            row("Colt Keith", "L", "+980", 73, "", ["vs Fisher"], """0 HR, 92.3 mph EV, 12.5% barrels. limited split/risk sample; limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 26.8, 'batterK': 28.6, 'batterWhiff': 31.7, 'pitcherK': 37.5}),
            row("Brett Callahan", "L", "+800", 79, "🌕 💣", ["vs Fisher"], """0 HR, 2 near-HR, 97.8 mph EV, 25.0% barrels. limited split/risk sample.""", blast="high", contact={'stars': 1, 'k': 27.4, 'batterK': 37.3, 'batterWhiff': 30.2, 'pitcherK': 37.5}),
            row("Dillon Dingler", "R", "+590", 73, "", ["vs Fisher"], """1 HR, 1 near-HR, 85.4 mph EV, 12.5% barrels. limited split/risk sample; lighter EV form (85.4 mph).""", blast="good", contact={'stars': 2, 'k': 25.7, 'batterK': 29.1, 'batterWhiff': 23.1, 'pitcherK': 37.5}),
            row("Kevin McGonigle", "L", "+574", 70, "", ["vs Fisher"], """1 HR, 2 near-HR, 92.4 mph EV. limited split/risk sample.""", blast="good", contact={'stars': 4, 'k': 19.8, 'batterK': 12.2, 'batterWhiff': 17.9, 'pitcherK': 37.5}),
        ],
    },
    {
        "title": "KC @ HOU - Michael Wacha (R, KC) vs Hunter Brown (R, HOU)",
        "kLines": {'Wacha': {'k': 5.1, 'lo': 3, 'hi': 7, 'bf': 24.7, 'matchupK': 20.6, 'ownK': 20.5}, 'Brown': {'k': 5.4, 'lo': 4, 'hi': 7, 'bf': 22.4, 'matchupK': 24.1, 'ownK': 26.2}},
        "description": "Tail key data: Park boost +6% (stadium +6%, weather +0%). Wacha (HR risk 0.18, vs LHB -0.58, vs RHB +1.18). Brown (HR risk -0.46, vs LHB -0.05, vs RHB -0.51).",
        "rows": [
            row("Nelson Velazquez", "R", "N/A", 88, "🌕 💣", ["vs Wacha"], """1 HR, 2 near-HR, 99.3 mph EV, 25.0% barrels. Wacha RHB split +1.18, HR risk 0.18.""", blast="high", contact={'stars': 2, 'k': 26.1, 'batterK': 39.5, 'batterWhiff': 44.3, 'pitcherK': 20.5}),
            row("Taylor Trammell", "L", "+650", 72, "", ["vs Wacha"], """0 HR, 1 near-HR, 94.3 mph EV, 25.0% barrels. Wacha LHB split -0.58, HR risk 0.18. tough split lane (-0.58); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.9, 'batterK': 23.2, 'batterWhiff': 32.7, 'pitcherK': 20.5}),
            row("Cam Smith", "R", "+680", 60, "", ["vs Wacha"], """0 HR, 89.4 mph EV. Wacha RHB split +1.18, HR risk 0.18. limited recent HR events.""", contact={'stars': 3, 'k': 23.2, 'batterK': 30.8, 'batterWhiff': 27.5, 'pitcherK': 20.5}),
            row("Vinnie Pasquantino", "L", "+650", 76, "", ["vs Brown"], """1 HR, 2 near-HR, 94.0 mph EV, 25.0% barrels. Brown LHB split -0.05, HR risk -0.46. slight split headwind (-0.05); pitcher suppresses HR (-0.46).""", blast="good", contact={'stars': 4, 'k': 18.9, 'batterK': 10.6, 'batterWhiff': 14.8, 'pitcherK': 26.2}),
            row("Salvador Perez", "R", "+630", 59, "💎", ["vs Brown"], """Worst Pickz Hidden Gem. 0 HR, 93.2 mph EV. Brown RHB split -0.51, HR risk -0.46. tough split lane (-0.51); pitcher suppresses HR (-0.46).""", blast="good", contact={'stars': 3, 'k': 22.6, 'batterK': 16.5, 'batterWhiff': 24.7, 'pitcherK': 26.2}),
            row("Jac Caglianone", "L", "+554", 67, "", ["vs Brown"], """0 HR, 93.1 mph EV. Brown LHB split -0.05, HR risk -0.46. slight split headwind (-0.05); pitcher suppresses HR (-0.46).""", blast="good", contact={'stars': 2, 'k': 26.7, 'batterK': 25.3, 'batterWhiff': 32.6, 'pitcherK': 26.2}),
        ],
    },
    {
        "title": "LAD @ CIN - Yoshinobu Yamamoto (R, LAD) vs Rhett Lowder (R, CIN)",
        "kLines": {'Yamamoto': {'k': 6.8, 'lo': 5, 'hi': 8, 'bf': 24.6, 'matchupK': 27.6, 'ownK': 27.3}, 'Lowder': {'k': 3.6, 'lo': 2, 'hi': 5, 'bf': 22.0, 'matchupK': 16.5, 'ownK': 15.6}},
        "description": "Tail key data: Park boost +13% (stadium +14%, weather -2%). Yamamoto (HR risk 0.00, vs LHB +0.32, vs RHB -0.30). Lowder (HR risk 0.66, vs LHB +0.18, vs RHB +0.83).",
        "rows": [
            row("Elly De La Cruz", "S", "+481", 93, "🚀 🌕 💣", ["vs Yamamoto"], """3 HR, 4 near-HR, 107.0 mph EV, 75.0% barrels. Yamamoto SHB→LHB split +0.32, HR risk 0.00.""", blast="high", contact={'stars': 1, 'k': 28.5, 'batterK': 30.7, 'batterWhiff': 28.5, 'pitcherK': 27.3}),
            row("Eugenio Suarez", "R", "+490", 88, "🌕 💣", ["vs Yamamoto"], """2 HR, 4 near-HR, 95.3 mph EV, 50.0% barrels. Yamamoto RHB split -0.30, HR risk 0.00. slight split headwind (-0.30).""", blast="high", contact={'stars': 2, 'k': 25.4, 'batterK': 21.5, 'batterWhiff': 26.9, 'pitcherK': 27.3}),
            row("JJ Bleday", "L", "+520", 68, "", ["vs Yamamoto"], """0 HR, 91.6 mph EV, 25.0% barrels. Yamamoto LHB split +0.32, HR risk 0.00. limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 26.5, 'batterK': 25.0, 'batterWhiff': 27.8, 'pitcherK': 27.3}),
            row("Mookie Betts", "R", "+440", 83, "", ["vs Lowder"], """0 HR, 1 near-HR, 97.0 mph EV, 12.5% barrels. Lowder RHB split +0.83, HR risk 0.66. limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 13.6, 'batterK': 9.8, 'batterWhiff': 12.3, 'pitcherK': 15.6}),
            row("Will Smith", "R", "+375", 84, "💎", ["vs Lowder"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.1 mph EV, 12.5% barrels. Lowder RHB split +0.83, HR risk 0.66. limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 16.5, 'batterK': 17.4, 'batterWhiff': 16.8, 'pitcherK': 15.6}),
        ],
    },
    {
        "title": "MIA @ ARI - Janson Junk (R, MIA) vs Michael Soroka (R, ARI)",
        "kLines": {'Junk': {'k': 3.0, 'lo': 1, 'hi': 5, 'bf': 21.4, 'matchupK': 14.2, 'ownK': 13.0}, 'Soroka': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 21.9, 'matchupK': 20.8, 'ownK': 19.9}},
        "description": "Tail key data: Park boost -9% (stadium -9%, weather -1%). Junk (HR risk -0.55, vs LHB -0.53, vs RHB -0.11). Soroka (BAA vs LHB .275, vs RHB .181, HR/9 0.63).",
        "rows": [
            row("Lars Nootbaar", "L", "+625", 74, "💎", ["vs Junk"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.8 mph EV, 12.5% barrels. Junk LHB split -0.53, HR risk -0.55. tough split lane (-0.53); pitcher suppresses HR (-0.55).""", blast="good", contact={'stars': 5, 'k': 14.3, 'batterK': 12.9, 'batterWhiff': 11.8, 'pitcherK': 13.0}),
            row("Gabriel Moreno", "R", "+880", 52, "", ["vs Junk"], """0 HR, 93.6 mph EV. Junk RHB split -0.11, HR risk -0.55. slight split headwind (-0.11); pitcher suppresses HR (-0.55).""", blast="good", contact={'stars': 5, 'k': 14.5, 'batterK': 14.0, 'batterWhiff': 15.4, 'pitcherK': 13.0}),
            row("Otto Lopez", "R", "+1000", 60, "💎", ["vs Soroka"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 98.1 mph EV. limited split/risk sample; park/weather net drag (-9%).""", blast="good", contact={'stars': 4, 'k': 18.9, 'batterK': 15.7, 'batterWhiff': 23.1, 'pitcherK': 19.9}),
            row("Javier Sanoja", "R", "+1300", 62, "", ["vs Soroka"], """1 HR, 1 near-HR, 93.4 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-9%).""", blast="good", contact={'stars': 5, 'k': 14.6, 'batterK': 5.9, 'batterWhiff': 13.0, 'pitcherK': 19.9}),
            row("Graham Pauley", "L", "N/A", 74, "🌕 💣", ["vs Soroka"], """2 HR, 2 near-HR, 91.3 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-9%).""", blast="high", contact={'stars': 3, 'k': 20.7, 'batterK': 22.2, 'batterWhiff': 23.2, 'pitcherK': 19.9}),
        ],
    },
    {
        "title": "MIL @ PIT - Jacob Misiorowski (R, MIL) vs Lake Bachar (R, PIT)",
        "kLines": {'Misiorowski': {'k': 7.6, 'lo': 6, 'hi': 9, 'bf': 22.6, 'matchupK': 33.5, 'ownK': 36.5}, 'Bachar': {'k': 2.0, 'lo': 0, 'hi': 4, 'bf': 8.4, 'matchupK': 24.3, 'ownK': 26.5}},
        "description": "Tail key data: Park boost -22% (stadium -14%, weather -7%). Misiorowski (HR risk -1.07, vs LHB -0.73, vs RHB -0.79). Bachar (BAA vs LHB .214, vs RHB .160, HR/9 1.47).",
        "rows": [
            row("Bryan Reynolds", "S", "+900", 77, "🌕 💣", ["vs Misiorowski"], """1 HR, 3 near-HR, 98.8 mph EV, 25.0% barrels. Misiorowski SHB→LHB split -0.73, HR risk -1.07. tough split lane (-0.73); pitcher suppresses HR (-1.07).""", blast="high", contact={'stars': 1, 'k': 27.9, 'batterK': 16.9, 'batterWhiff': 24.5, 'pitcherK': 36.5}),
            row("Rafael Flores", "R", "+1050", 65, "🚀 🌕 💣", ["vs Misiorowski"], """0 HR, 1 near-HR, 100.4 mph EV, 25.0% barrels. Misiorowski RHB split -0.79, HR risk -1.07. tough split lane (-0.79); pitcher suppresses HR (-1.07).""", blast="high", contact={'stars': 1, 'k': 32.8, 'batterK': 28.8, 'batterWhiff': 29.6, 'pitcherK': 36.5}),
            row("William Contreras", "R", "+720", 73, "💎", ["vs Bachar"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 91.1 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-22%).""", blast="good", contact={'stars': 3, 'k': 21.0, 'batterK': 17.2, 'batterWhiff': 19.9, 'pitcherK': 26.5}),
            row("Joey Ortiz", "R", "+1400", 64, "", ["vs Bachar"], """1 HR, 1 near-HR, 94.8 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-22%).""", blast="good", contact={'stars': 3, 'k': 20.6, 'batterK': 16.1, 'batterWhiff': 16.5, 'pitcherK': 26.5}),
            row("Garrett Mitchell", "L", "+875", 86, "🌕 💣", ["vs Bachar"], """2 HR, 2 near-HR, 97.4 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-22%).""", blast="high", contact={'stars': 2, 'k': 26.4, 'batterK': 27.3, 'batterWhiff': 34.2, 'pitcherK': 26.5}),
        ],
    },
    {
        "title": "NYY @ MIN - Max Fried (L, NYY) vs Bailey Ober (R, MIN)",
        "kLines": {'Fried': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 21.3, 'matchupK': 24.2, 'ownK': 28.2}, 'Ober': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 22.4, 'matchupK': 19.6, 'ownK': 18.0}},
        "description": "Tail key data: Park boost -10% (stadium -7%, weather -3%). Fried (HR risk -1.14, vs LHB -1.31, vs RHB -0.70). Ober (HR risk 0.82, vs LHB +0.44, vs RHB +0.85).",
        "rows": [
            row("Royce Lewis", "R", "+700", 40, "", ["vs Fried"], """0 HR, 89.7 mph EV. Fried RHB split -0.70, HR risk -1.14. tough split lane (-0.70); pitcher suppresses HR (-1.14).""", contact={'stars': 2, 'k': 25.4, 'batterK': 20.5, 'batterWhiff': 28.4, 'pitcherK': 28.2}),
            row("Ryan Kreidler", "R", "N/A", 60, "", ["vs Fried"], """1 HR, 1 near-HR, 98.7 mph EV, 12.5% barrels. Fried RHB split -0.70, HR risk -1.14. tough split lane (-0.70); pitcher suppresses HR (-1.14).""", blast="good", contact={'stars': 1, 'k': 28.4, 'batterK': 34.4, 'batterWhiff': 37.7, 'pitcherK': 28.2}),
            row("George Lombard Jr.", "R", "+880", 81, "", ["vs Ober"], """1 HR, 2 near-HR, 94.2 mph EV, 12.5% barrels. Ober RHB split +0.85, HR risk 0.82. park/weather net drag (-10%).""", blast="good", contact={'stars': 3, 'k': 22.2, 'batterK': 32.5, 'batterWhiff': 24.2, 'pitcherK': 18.0}),
            row("Spencer Jones", "L", "+500", 87, "🌕 💣", ["vs Ober"], """0 HR, 98.2 mph EV, 25.0% barrels. Ober LHB split +0.44, HR risk 0.82. park/weather net drag (-10%); limited recent HR events.""", blast="high", contact={'stars': 2, 'k': 25.3, 'batterK': 34.7, 'batterWhiff': 40.0, 'pitcherK': 18.0}),
            row("Aaron Judge", "R", "+285", 88, "🌕 💣", ["vs Ober"], """0 HR, 1 near-HR, 97.5 mph EV, 12.5% barrels. Ober RHB split +0.85, HR risk 0.82. park/weather net drag (-10%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 32.1, 'batterWhiff': 30.8, 'pitcherK': 18.0}),
            row("Ben Rice", "L", "+333", 82, "", ["vs Ober"], """0 HR, 1 near-HR, 95.5 mph EV. Ober LHB split +0.44, HR risk 0.82. park/weather net drag (-10%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.0, 'batterK': 20.2, 'batterWhiff': 21.8, 'pitcherK': 18.0}),
            row("Luis Garcia Jr.", "L", "+424", 79, "", ["vs Ober"], """0 HR, 1 near-HR, 90.8 mph EV, 25.0% barrels. Ober LHB split +0.44, HR risk 0.82. park/weather net drag (-10%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.6, 'batterK': 18.4, 'batterWhiff': 27.2, 'pitcherK': 18.0}),
        ],
    },
    {
        "title": "PHI @ WSH - Cristopher Sanchez (L, PHI) vs Jackson Kent (L, WSH)",
        "kLines": {'Sanchez': {'k': 6.5, 'lo': 5, 'hi': 8, 'bf': 25.2, 'matchupK': 25.8, 'ownK': 26.1}, 'Kent': {'k': 4.1, 'lo': 3, 'hi': 6, 'bf': 21.6, 'matchupK': 19.1, 'ownK': 17.8}},
        "description": "Tail key data: Park boost -1% (stadium +4%, weather -6%). Sanchez (HR risk -0.56, vs LHB -1.65, vs RHB -0.16). Kent (HR risk -0.95, vs LHB -0.24, vs RHB -0.82).",
        "rows": [
            row("Andrew Pinckney", "R", "N/A", 73, "", ["vs Sanchez"], """1 HR, 1 near-HR, 96.5 mph EV, 25.0% barrels. Sanchez RHB split -0.16, HR risk -0.56. slight split headwind (-0.16); pitcher suppresses HR (-0.56).""", blast="good", contact={'stars': 2, 'k': 25.8, 'batterK': 30.8, 'batterWhiff': 31.6, 'pitcherK': 26.1}),
            row("Dylan Crews", "R", "+790", 58, "", ["vs Sanchez"], """0 HR, 95.2 mph EV. Sanchez RHB split -0.16, HR risk -0.56. slight split headwind (-0.16); pitcher suppresses HR (-0.56).""", blast="good", contact={'stars': 2, 'k': 26.2, 'batterK': 26.2, 'batterWhiff': 28.4, 'pitcherK': 26.1}),
            row("James Wood", "L", "+610", 70, "", ["vs Sanchez"], """0 HR, 98.1 mph EV, 12.5% barrels. Sanchez LHB split -1.65, HR risk -0.56. tough split lane (-1.65); pitcher suppresses HR (-0.56).""", blast="good", contact={'stars': 2, 'k': 24.8, 'batterK': 23.9, 'batterWhiff': 24.4, 'pitcherK': 26.1}),
            row("Kyle Schwarber", "L", "+310", 74, "", ["vs Kent"], """1 HR, 1 near-HR, 93.9 mph EV, 12.5% barrels. Kent LHB split -0.24, HR risk -0.95. slight split headwind (-0.24); pitcher suppresses HR (-0.95).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 27.5, 'batterWhiff': 30.9, 'pitcherK': 17.8}),
            row("Alec Bohm", "R", "+750", 50, "", ["vs Kent"], """0 HR, 1 near-HR, 89.1 mph EV, 12.5% barrels. Kent RHB split -0.82, HR risk -0.95. tough split lane (-0.82); pitcher suppresses HR (-0.95).""", contact={'stars': 4, 'k': 19.3, 'batterK': 19.0, 'batterWhiff': 21.8, 'pitcherK': 17.8}),
        ],
    },
    {
        "title": "SD @ COL - Walker Buehler (R, SD) vs Kyle Freeland (L, COL)",
        "kLines": {'Buehler': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 20.5, 'matchupK': 20.1, 'ownK': 20.0}, 'Freeland': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 23.6, 'matchupK': 18.7, 'ownK': 18.5}},
        "description": "Tail key data: Park boost +20% (stadium +20%, weather +0%). Buehler (HR risk 0.55, vs LHB +0.96, vs RHB -0.19). Freeland (HR risk 0.54, vs LHB -0.39, vs RHB +0.65).",
        "rows": [
            row("Connor Norby", "R", "+570", 83, "", ["vs Buehler"], """1 HR, 3 near-HR, 93.3 mph EV, 37.5% barrels. Buehler RHB split -0.19, HR risk 0.55. slight split headwind (-0.19).""", blast="good", contact={'stars': 3, 'k': 21.7, 'batterK': 25.9, 'batterWhiff': 23.5, 'pitcherK': 20.0}),
            row("Cole Carrigg", "S", "+820", 82, "", ["vs Buehler"], """1 HR, 1 near-HR, 90.5 mph EV. Buehler SHB→LHB split +0.96, HR risk 0.55.""", blast="good", contact={'stars': 3, 'k': 23.6, 'batterK': 30.5, 'batterWhiff': 27.5, 'pitcherK': 20.0}),
            row("Hunter Goodman", "R", "+290", 65, "", ["vs Buehler"], """0 HR, 1 near-HR, 86.3 mph EV, 12.5% barrels. Buehler RHB split -0.19, HR risk 0.55. slight split headwind (-0.19); limited recent HR events.""", contact={'stars': 3, 'k': 21.8, 'batterK': 22.9, 'batterWhiff': 27.9, 'pitcherK': 20.0}),
            row("Kyle Karros", "R", "+820", 75, "", ["vs Buehler"], """0 HR, 2 near-HR, 88.6 mph EV, 12.5% barrels. Buehler RHB split -0.19, HR risk 0.55. slight split headwind (-0.19).""", blast="good", contact={'stars': 4, 'k': 19.9, 'batterK': 21.1, 'batterWhiff': 20.0, 'pitcherK': 20.0}),
            row("Manny Machado", "R", "+310", 87, "⭐", ["vs Freeland"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.0 mph EV, 25.0% barrels. Freeland RHB split +0.65, HR risk 0.54.""", blast="good", contact={'stars': 4, 'k': 18.4, 'batterK': 16.7, 'batterWhiff': 23.5, 'pitcherK': 18.5}),
            row("Xander Bogaerts", "R", "+600", 64, "", ["vs Freeland"], """0 HR, 91.4 mph EV. Freeland RHB split +0.65, HR risk 0.54. limited recent HR events.""", contact={'stars': 4, 'k': 18.1, 'batterK': 16.5, 'batterWhiff': 20.8, 'pitcherK': 18.5}),
            row("Ty France", "R", "+470", 86, "💎", ["vs Freeland"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.4 mph EV. Freeland RHB split +0.65, HR risk 0.54.""", blast="good", contact={'stars': 4, 'k': 19.8, 'batterK': 17.4, 'batterWhiff': 30.4, 'pitcherK': 18.5}),
            row("Fernando Tatis Jr.", "R", "+330", 76, "💎", ["vs Freeland"], """Worst Pickz Hidden Gem. 0 HR, 84.7 mph EV. Freeland RHB split +0.65, HR risk 0.54. limited recent HR events; lighter EV form (84.7 mph).""", contact={'stars': 4, 'k': 18.7, 'batterK': 17.8, 'batterWhiff': 23.6, 'pitcherK': 18.5}),
            row("Jackson Merrill", "L", "+410", 84, "", ["vs Freeland"], """0 HR, 2 near-HR, 89.7 mph EV, 25.0% barrels. Freeland LHB split -0.39, HR risk 0.54. slight split headwind (-0.39).""", blast="good", contact={'stars': 4, 'k': 18.6, 'batterK': 15.9, 'batterWhiff': 25.9, 'pitcherK': 18.5}),
        ],
    },
    {
        "title": "SEA @ LAA - Logan Gilbert 🧤 (R, SEA) vs Ryan Johnson (R, LAA)",
        "kLines": {'Gilbert': {'k': 6.4, 'lo': 5, 'hi': 8, 'bf': 23.3, 'matchupK': 27.5, 'ownK': 28.7}, 'Johnson': {'k': 4.0, 'lo': 2, 'hi': 6, 'bf': 21.2, 'matchupK': 19.0, 'ownK': 17.8}},
        "description": "Tail key data: Park boost -2% (stadium -9%, weather +7%). Gilbert 🧤 (HR risk 1.39, vs LHB +0.31, vs RHB +1.71). Johnson (HR risk 0.78, vs LHB +1.14, vs RHB +0.09).",
        "rows": [
            row("Moises Ballesteros", "L", "+820", 86, "", ["vs Gilbert"], """1 HR, 1 near-HR, 94.7 mph EV, 12.5% barrels. Gilbert LHB split +0.31, HR risk 1.39. park suppresses carry (-9%).""", blast="good", contact={'stars': 1, 'k': 28.7, 'batterK': 29.5, 'batterWhiff': 29.7, 'pitcherK': 28.7}),
            row("Mike Trout", "R", "+420", 81, "", ["vs Gilbert"], """0 HR, 88.7 mph EV. Gilbert RHB split +1.71, HR risk 1.39. park suppresses carry (-9%); limited recent HR events.""", contact={'stars': 1, 'k': 28.8, 'batterK': 28.4, 'batterWhiff': 30.7, 'pitcherK': 28.7}),
            row("Jose Siri", "R", "+586", 85, "", ["vs Gilbert"], """0 HR, 87.1 mph EV, 25.0% barrels. Gilbert RHB split +1.71, HR risk 1.39. park suppresses carry (-9%); limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 30.4, 'batterK': 34.0, 'batterWhiff': 37.8, 'pitcherK': 28.7}),
            row("Lazaro Montes", "L", "+529", 83, "", ["vs Johnson"], """1 HR, 1 near-HR, 92.1 mph EV, 20.0% barrels. Johnson LHB split +1.14, HR risk 0.78. park suppresses carry (-9%).""", blast="good", contact={'stars': 2, 'k': 25.0, 'batterK': 44.8, 'batterWhiff': 50.8, 'pitcherK': 17.8}),
            row("Michael Arroyo", "R", "N/A", 84, "", ["vs Johnson"], """1 HR, 1 near-HR, 95.5 mph EV, 33.3% barrels. Johnson RHB split +0.09, HR risk 0.78. park suppresses carry (-9%).""", blast="good", contact={'stars': 4, 'k': 18.9, 'batterK': 17.6, 'batterWhiff': 16.7, 'pitcherK': 17.8}),
            row("Cal Raleigh", "S", "+334", 87, "", ["vs Johnson"], """0 HR, 1 near-HR, 94.0 mph EV, 12.5% barrels. Johnson SHB→LHB split +1.14, HR risk 0.78. park suppresses carry (-9%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.9, 'batterK': 30.2, 'batterWhiff': 30.5, 'pitcherK': 17.8}),
            row("Randy Arozarena", "R", "+450", 67, "", ["vs Johnson"], """0 HR, 91.1 mph EV. Johnson RHB split +0.09, HR risk 0.78. park suppresses carry (-9%); limited recent HR events.""", contact={'stars': 3, 'k': 20.2, 'batterK': 22.2, 'batterWhiff': 26.8, 'pitcherK': 17.8}),
        ],
    },
    {
        "title": "SF @ STL - Blade Tidwell (R, SF) vs Andre Pallante (R, STL)",
        "kLines": {'Tidwell': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 21.6, 'matchupK': 18.9, 'ownK': 18.6}, 'Pallante': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 22.9, 'matchupK': 16.8, 'ownK': 14.9}},
        "description": "Tail key data: Park boost -9% (stadium -9%, weather +0%). Tidwell (HR risk 0.86, vs LHB +1.78, vs RHB -0.46). Pallante (HR risk -1.54, vs LHB -1.04, vs RHB -1.16).",
        "rows": [
            row("Leonardo Bernal", "S", "+680", 89, "🌕 💣", ["vs Tidwell"], """2 HR, 2 near-HR, 97.2 mph EV, 25.0% barrels. Tidwell SHB→LHB split +1.78, HR risk 0.86. park/weather net drag (-9%).""", blast="high", contact={'stars': 4, 'k': 19.3, 'batterK': 17.9, 'batterWhiff': 21.3, 'pitcherK': 18.6}),
            row("Ivan Herrera", "R", "+790", 65, "", ["vs Tidwell"], """0 HR, 93.9 mph EV. Tidwell RHB split -0.46, HR risk 0.86. tough split lane (-0.46); park/weather net drag (-9%).""", blast="good", contact={'stars': 4, 'k': 18.6, 'batterK': 19.6, 'batterWhiff': 17.2, 'pitcherK': 18.6}),
            row("Bryce Eldridge", "L", "+710", 57, "", ["vs Pallante"], """0 HR, 95.6 mph EV. Pallante LHB split -1.04, HR risk -1.54. tough split lane (-1.04); pitcher suppresses HR (-1.54).""", blast="good", contact={'stars': 3, 'k': 20.0, 'batterK': 27.5, 'batterWhiff': 27.1, 'pitcherK': 14.9}),
            row("Jung Hoo Lee", "L", "+1800", 47, "", ["vs Pallante"], """0 HR, 95.0 mph EV. Pallante LHB split -1.04, HR risk -1.54. tough split lane (-1.04); pitcher suppresses HR (-1.54).""", blast="good", contact={'stars': 5, 'k': 13.2, 'batterK': 7.7, 'batterWhiff': 12.3, 'pitcherK': 14.9}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-15")

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

    out = ROOT / '_games-0915.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
