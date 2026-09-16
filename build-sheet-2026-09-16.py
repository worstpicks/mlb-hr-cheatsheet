#!/usr/bin/env python3
"""Generate games[] block for 2026-09-16 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "A.J. Ewing (L)",
    "Alec Burleson (L)",
    "Bobby Witt Jr. (R)",
    "Bryan Reynolds (S)",
    "Colt Keith (L)",
    "Drake Baldwin (L)",
    "Fernando Tatis Jr. (R)",
    "Jackson Merrill (L)",
    "Joe Mack (L)",
    "Juan Soto (L)",
    "Ketel Marte (S)",
    "Kyle Tucker (L)",
    "Oneil Cruz (L)",
    "Shea Langeliers (R)",
    "Trea Turner (R)",
}

GEMS = {
    "Alec Bohm (R)",
    "Angel Martinez (S)",
    "Brice Turang (L)",
    "Bryce Eldridge (L)",
    "Cal Raleigh (S)",
    "Christian Encarnacion-Strand (R)",
    "Cody Bellinger (L)",
    "Cole Carrigg (S)",
    "Cole Young (L)",
    "Daylen Lile (L)",
    "Ezequiel Duran (R)",
    "Garrett Mitchell (L)",
    "Jake Burger (R)",
    "Javier Sanoja (R)",
    "Josh Jung (R)",
    "Kevin McGonigle (L)",
    "Lars Nootbaar (L)",
    "Leonardo Bernal (S)",
    "Moises Ballesteros (L)",
    "Munetaka Murakami (L)",
    "Pete Crow Armstrong (L)",
    "Rafael Flores (R)",
    "Randy Arozarena (R)",
    "Salvador Perez (R)",
    "Spencer Torkelson (R)",
    "Teoscar Hernandez (R)",
    "Ty France (R)",
    "Vinnie Pasquantino (L)",
    "Yandy Diaz (R)",
    "Yordan Alvarez (L)",
    "Zack Gelof (R)",
}

PLAYER_TEAMS = {
    "A.J. Ewing (L)": "NYM",
    "Aaron Judge (R)": "NYY",
    "Alec Bohm (R)": "PHI",
    "Alec Burleson (L)": "STL",
    "Alejandro Kirk (R)": "TOR",
    "Amed Rosario (R)": "NYY",
    "Andres Gimenez (L)": "TOR",
    "Andrew Pinckney (R)": "WSH",
    "Angel Martinez (S)": "CLE",
    "Austin Riley (R)": "ATL",
    "Austin Wells (L)": "NYY",
    "Ben Rice (L)": "NYY",
    "Bo Naylor (L)": "MIL",
    "Bobby Witt Jr. (R)": "KC",
    "Brady House (R)": "WSH",
    "Brandon Nimmo (L)": "TEX",
    "Brett Bateman (L)": "TOR",
    "Brett Baty (L)": "NYM",
    "Brett Callahan (L)": "DET",
    "Brice Turang (L)": "MIL",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Cal Raleigh (S)": "SEA",
    "Carson Benge (L)": "NYM",
    "Carter Jensen (L)": "KC",
    "Chase Meidroth (R)": "CWS",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Coby Mayo (R)": "BAL",
    "Cody Bellinger (L)": "NYY",
    "Cole Carrigg (S)": "COL",
    "Cole Young (L)": "SEA",
    "Colson Montgomery (L)": "CWS",
    "Colt Keith (L)": "DET",
    "Connor Norby (R)": "COL",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Daylen Lile (L)": "WSH",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Eliezer Alfonzo (S)": "LAD",
    "Elly De La Cruz (S)": "CIN",
    "Emmanuel Rodriguez (L)": "MIN",
    "Ezequiel Duran (R)": "TEX",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Lindor (S)": "NYM",
    "Gabriel Arias (R)": "CHC",
    "Gabriel Moreno (R)": "ARI",
    "Garrett Mitchell (L)": "MIL",
    "Graham Pauley (L)": "MIA",
    "Heliot Ramos (R)": "NYY",
    "Hunter Feduccia (L)": "LAD",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Jac Caglianone (L)": "KC",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Javier Sanoja (R)": "MIA",
    "Jeff McNeil (L)": "ATH",
    "Jeremy Pena (R)": "HOU",
    "Jo Adell (R)": "CLE",
    "Joe Mack (L)": "MIA",
    "John Rave (L)": "KC",
    "Jordan Walker (R)": "STL",
    "Jose Altuve (R)": "HOU",
    "Jose Siri (R)": "LAA",
    "Josh Jung (R)": "TEX",
    "Josh Lowe (L)": "LAA",
    "Joshua Baez (R)": "STL",
    "Juan Brito (S)": "CIN",
    "Juan Soto (L)": "NYM",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kazuma Okamoto (R)": "TOR",
    "Keibert Ruiz (S)": "WSH",
    "Ketel Marte (S)": "ARI",
    "Kevin McGonigle (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Kyle Tucker (L)": "LAD",
    "Lars Nootbaar (L)": "ARI",
    "Lawrence Butler (L)": "ATH",
    "Leody Taveras (S)": "BAL",
    "Leonardo Bernal (S)": "STL",
    "Luis Garcia Jr. (L)": "NYY",
    "Manny Machado (R)": "SD",
    "Matt McLain (R)": "CIN",
    "Max Muncy (L)": "LAD",
    "Michael Harris II (L)": "ATL",
    "Michael Stefanic (R)": "ATH",
    "Miguel Vargas (R)": "CWS",
    "Moises Ballesteros (L)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Nathan Lukes (L)": "TOR",
    "Nelson Velazquez (R)": "HOU",
    "Nick Sogard (S)": "BOS",
    "Oneil Cruz (L)": "PIT",
    "Patrick Bailey (S)": "CLE",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Flores (R)": "PIT",
    "Randal Grichuk (R)": "CWS",
    "Randy Arozarena (R)": "SEA",
    "Riley Greene (L)": "DET",
    "Ryan Kreidler (R)": "MIN",
    "Salvador Perez (R)": "KC",
    "Shay Whitcomb (R)": "SF",
    "Shea Langeliers (R)": "ATH",
    "Spencer Torkelson (R)": "DET",
    "Teoscar Hernandez (R)": "LAD",
    "Thomas Saggese (R)": "STL",
    "Travis d'Arnaud (R)": "LAA",
    "Trea Turner (R)": "PHI",
    "Troy Johnston (L)": "COL",
    "Ty France (R)": "SD",
    "Tyler Stephenson (R)": "CIN",
    "Vinnie Pasquantino (L)": "KC",
    "William Contreras (R)": "MIL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Xander Bogaerts (R)": "SD",
    "Yainer Diaz (R)": "HOU",
    "Yandy Diaz (R)": "TB",
    "Yohandy Morales (R)": "WSH",
    "Yordan Alvarez (L)": "HOU",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("ATL @ CHC", "Imanaga"),
    ("SD @ COL", "Adams"),
    ("SF @ STL", "Liberatore"),
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
        "title": "ATH @ TB - Brady Basso (L, ATH) vs Nick Martinez (R, TB)",
        "kLines": {'Basso': {'k': 2.9, 'lo': 1, 'hi': 4, 'bf': 16.7, 'matchupK': 17.1, 'ownK': 16.3}, 'Martinez': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 23.3, 'matchupK': 17.4, 'ownK': 15.3}},
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Basso (HR risk -1.38, vs LHB -1.16, vs RHB -0.72). Martinez (HR risk -0.42, vs LHB -0.47, vs RHB +0.06).",
        "rows": [
            row("Junior Caminero", "R", "+296", 69, "", ["vs Basso"], """1 HR, 1 near-HR, 90.0 mph EV, 12.5% barrels. Basso RHB split -0.72, HR risk -1.38. tough split lane (-0.72); pitcher suppresses HR (-1.38).""", blast="good", contact={'stars': 4, 'k': 18.7, 'batterK': 18.2, 'batterWhiff': 21.0, 'pitcherK': 16.3}),
            row("Yandy Diaz", "R", "+540", 55, "💎", ["vs Basso"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 91.9 mph EV, 12.5% barrels. Basso RHB split -0.72, HR risk -1.38. tough split lane (-0.72); pitcher suppresses HR (-1.38).""", contact={'stars': 5, 'k': 16.8, 'batterK': 15.4, 'batterWhiff': 14.8, 'pitcherK': 16.3}),
            row("Zack Gelof", "R", "+520", 78, "💎", ["vs Martinez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.6 mph EV, 12.5% barrels. Martinez RHB split +0.06, HR risk -0.42. pitcher suppresses HR (-0.42).""", blast="good", contact={'stars': 4, 'k': 19.9, 'batterK': 24.4, 'batterWhiff': 31.2, 'pitcherK': 15.3}),
            row("Michael Stefanic", "R", "N/A", 55, "", ["vs Martinez"], """0 HR, 96.2 mph EV. Martinez RHB split +0.06, HR risk -0.42. pitcher suppresses HR (-0.42); limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 16.7, 'batterK': 14.3, 'batterWhiff': 13.2, 'pitcherK': 15.3}),
            row("Lawrence Butler", "L", "+565", 83, "🌕 💣", ["vs Martinez"], """2 HR, 2 near-HR, 90.6 mph EV, 25.0% barrels. Martinez LHB split -0.47, HR risk -0.42. tough split lane (-0.47); pitcher suppresses HR (-0.42).""", blast="high", contact={'stars': 3, 'k': 20.4, 'batterK': 30.2, 'batterWhiff': 25.8, 'pitcherK': 15.3}),
            row("Jeff McNeil", "L", "+980", 42, "", ["vs Martinez"], """0 HR, 90.5 mph EV. Martinez LHB split -0.47, HR risk -0.42. tough split lane (-0.47); pitcher suppresses HR (-0.42).""", contact={'stars': 5, 'k': 13.2, 'batterK': 10.1, 'batterWhiff': 11.2, 'pitcherK': 15.3}),
            row("Shea Langeliers", "R", "+350", 58, "⭐", ["vs Martinez"], """Worst Pickz Favorite. 0 HR, 86.7 mph EV. Martinez RHB split +0.06, HR risk -0.42. pitcher suppresses HR (-0.42); limited recent HR events.""", contact={'stars': 3, 'k': 22.7, 'batterK': 36.4, 'batterWhiff': 33.5, 'pitcherK': 15.3}),
        ],
    },
    {
        "title": "ATL @ CHC - JR Ritchie (R, ATL) vs Shota Imanaga 🧤 (L, CHC)",
        "kLines": {'Ritchie': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 22.2, 'matchupK': 19.6, 'ownK': 22.1}, 'Imanaga': {'k': 5.1, 'lo': 3, 'hi': 7, 'bf': 22.6, 'matchupK': 22.4, 'ownK': 22.9}},
        "description": "Tail key data: Park boost -34% (stadium -2%, weather -32%). Ritchie (HR risk 0.51, vs LHB -0.06, vs RHB +0.72). Imanaga 🧤 (HR risk 1.09, vs LHB +1.21, vs RHB +0.77).",
        "rows": [
            row("Gabriel Arias", "R", "N/A", 80, "", ["vs Ritchie"], """1 HR, 1 near-HR, 96.3 mph EV, 12.5% barrels. Ritchie RHB split +0.72, HR risk 0.51. park/weather net drag (-34%).""", blast="good", contact={'stars': 1, 'k': 29.8, 'batterK': 40.7, 'batterWhiff': 49.6, 'pitcherK': 22.1}),
            row("Pete Crow Armstrong", "L", "+420", 83, "💎", ["vs Ritchie"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.6 mph EV, 12.5% barrels. Ritchie LHB split -0.06, HR risk 0.51. slight split headwind (-0.06); park/weather net drag (-34%).""", blast="good", contact={'stars': 3, 'k': 22.5, 'batterK': 23.7, 'batterWhiff': 24.5, 'pitcherK': 22.1}),
            row("Ian Happ", "S", "+600", 66, "", ["vs Ritchie"], """0 HR, 94.2 mph EV. Ritchie SHB→LHB split -0.06, HR risk 0.51. slight split headwind (-0.06); park/weather net drag (-34%).""", blast="good", contact={'stars': 3, 'k': 21.8, 'batterK': 22.9, 'batterWhiff': 22.4, 'pitcherK': 22.1}),
            row("Austin Riley", "R", "+594", 82, "🚀 🌕 💣", ["vs Imanaga"], """0 HR, 1 near-HR, 101.8 mph EV, 50.0% barrels. Imanaga RHB split +0.77, HR risk 1.09. park/weather net drag (-34%); limited recent HR events.""", blast="high", contact={'stars': 2, 'k': 25.2, 'batterK': 32.4, 'batterWhiff': 26.6, 'pitcherK': 22.9}),
            row("Drake Baldwin", "L", "+630", 79, "🚀 ⭐", ["vs Imanaga"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 100.5 mph EV. Imanaga LHB split +1.21, HR risk 1.09. park/weather net drag (-34%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.2, 'batterK': 27.5, 'batterWhiff': 30.5, 'pitcherK': 22.9}),
            row("Michael Harris II", "L", "+600", 63, "", ["vs Imanaga"], """0 HR, 91.5 mph EV. Imanaga LHB split +1.21, HR risk 1.09. park/weather net drag (-34%); limited recent HR events.""", contact={'stars': 3, 'k': 21.2, 'batterK': 20.3, 'batterWhiff': 20.4, 'pitcherK': 22.9}),
        ],
    },
    {
        "title": "BAL @ NYM - Chris Bassitt (R, BAL) vs Robert Stock (R, NYM)",
        "kLines": {'Bassitt': {'k': 4.2, 'lo': 3, 'hi': 6, 'bf': 22.7, 'matchupK': 18.4, 'ownK': 17.2}, 'Stock': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 21.2, 'matchupK': 21.9, 'ownK': 19.7}},
        "description": "Tail key data: Park boost -1% (stadium -2%, weather +1%). Bassitt (HR risk -0.20, vs LHB +0.15, vs RHB -0.33). Stock (HR risk -0.41, vs LHB -0.21, vs RHB -0.63).",
        "rows": [
            row("A.J. Ewing", "L", "+850", 83, "⭐ 🌕 💣", ["vs Bassitt"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.6 mph EV, 25.0% barrels. Bassitt LHB split +0.15, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="high", contact={'stars': 4, 'k': 18.5, 'batterK': 20.5, 'batterWhiff': 21.2, 'pitcherK': 17.2}),
            row("Francisco Lindor", "S", "+421", 91, "🌕 💣", ["vs Bassitt"], """3 HR, 3 near-HR, 93.5 mph EV, 12.5% barrels. Bassitt SHB→LHB split +0.15, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="high", contact={'stars': 3, 'k': 20.9, 'batterK': 25.3, 'batterWhiff': 27.3, 'pitcherK': 17.2}),
            row("Carson Benge", "L", "+760", 71, "", ["vs Bassitt"], """1 HR, 1 near-HR, 92.6 mph EV, 25.0% barrels. Bassitt LHB split +0.15, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="good", contact={'stars': 3, 'k': 20.9, 'batterK': 27.0, 'batterWhiff': 25.3, 'pitcherK': 17.2}),
            row("Jared Young", "L", "+593", 78, "🌕 💣", ["vs Bassitt"], """1 HR, 1 near-HR, 97.9 mph EV, 25.0% barrels. Bassitt LHB split +0.15, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="high", contact={'stars': 4, 'k': 17.9, 'batterK': 18.7, 'batterWhiff': 19.7, 'pitcherK': 17.2}),
            row("Juan Soto", "L", "+315", 71, "⭐", ["vs Bassitt"], """Worst Pickz Favorite. 0 HR, 92.7 mph EV. Bassitt LHB split +0.15, HR risk -0.20. pitcher risk below avg (-0.20); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.2, 'batterK': 16.9, 'batterWhiff': 25.2, 'pitcherK': 17.2}),
            row("Brett Baty", "L", "+640", 72, "", ["vs Bassitt"], """1 HR, 1 near-HR, 94.4 mph EV, 12.5% barrels. Bassitt LHB split +0.15, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="good", contact={'stars': 3, 'k': 20.1, 'batterK': 17.3, 'batterWhiff': 30.5, 'pitcherK': 17.2}),
            row("Coby Mayo", "R", "+400", 69, "", ["vs Stock"], """1 HR, 1 near-HR, 90.6 mph EV, 12.5% barrels. Stock RHB split -0.63, HR risk -0.41. tough split lane (-0.63); pitcher suppresses HR (-0.41).""", blast="good", contact={'stars': 3, 'k': 21.8, 'batterK': 24.1, 'batterWhiff': 25.9, 'pitcherK': 19.7}),
            row("Christian Encarnacion-Strand", "R", "+425", 57, "💎", ["vs Stock"], """Worst Pickz Hidden Gem. 0 HR, 93.2 mph EV. Stock RHB split -0.63, HR risk -0.41. tough split lane (-0.63); pitcher suppresses HR (-0.41).""", blast="good", contact={'stars': 2, 'k': 24.3, 'batterK': 28.0, 'batterWhiff': 34.6, 'pitcherK': 19.7}),
            row("Leody Taveras", "S", "N/A", 42, "", ["vs Stock"], """0 HR, 1 near-HR, 88.9 mph EV. Stock SHB→LHB split -0.21, HR risk -0.41. slight split headwind (-0.21); pitcher suppresses HR (-0.41).""", contact={'stars': 2, 'k': 24.0, 'batterK': 40.6, 'batterWhiff': 23.1, 'pitcherK': 19.7}),
        ],
    },
    {
        "title": "BOS @ TEX - Jake Bennett (L, BOS) vs MacKenzie Gore (L, TEX)",
        "kLines": {'Bennett': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 22.8, 'matchupK': 20.5, 'ownK': 20.3}, 'Gore': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 22.5, 'matchupK': 22.3, 'ownK': 21.8}},
        "description": "Tail key data: Park boost -12% (stadium -11%, weather -1%). Bennett (HR risk 0.93, vs LHB -1.45, vs RHB +1.30). Gore (HR risk -0.65, vs LHB -0.31, vs RHB -0.49).",
        "rows": [
            row("Jake Burger", "R", "+377", 92, "🌕 💣 💎", ["vs Bennett"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.6 mph EV, 37.5% barrels. Bennett RHB split +1.30, HR risk 0.93. park/weather net drag (-12%).""", blast="high", contact={'stars': 2, 'k': 24.4, 'batterK': 27.2, 'batterWhiff': 35.8, 'pitcherK': 20.3}),
            row("Ezequiel Duran", "R", "+840", 73, "💎", ["vs Bennett"], """Worst Pickz Hidden Gem. 0 HR, 93.9 mph EV. Bennett RHB split +1.30, HR risk 0.93. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 19.9, 'batterK': 18.6, 'batterWhiff': 23.4, 'pitcherK': 20.3}),
            row("Brandon Nimmo", "L", "+775", 64, "", ["vs Bennett"], """0 HR, 96.5 mph EV. Bennett LHB split -1.45, HR risk 0.93. tough split lane (-1.45); park/weather net drag (-12%).""", blast="good", contact={'stars': 3, 'k': 22.8, 'batterK': 25.3, 'batterWhiff': 29.7, 'pitcherK': 20.3}),
            row("Corey Seager", "L", "+446", 77, "", ["vs Bennett"], """1 HR, 1 near-HR, 90.6 mph EV, 12.5% barrels. Bennett LHB split -1.45, HR risk 0.93. tough split lane (-1.45); park/weather net drag (-12%).""", blast="good", contact={'stars': 3, 'k': 20.5, 'batterK': 18.0, 'batterWhiff': 28.3, 'pitcherK': 20.3}),
            row("Josh Jung", "R", "+660", 70, "💎", ["vs Bennett"], """Worst Pickz Hidden Gem. 0 HR, 91.4 mph EV, 12.5% barrels. Bennett RHB split +1.30, HR risk 0.93. park/weather net drag (-12%); limited recent HR events.""", contact={'stars': 4, 'k': 19.5, 'batterK': 21.6, 'batterWhiff': 16.4, 'pitcherK': 20.3}),
            row("Justin Foscue", "R", "+539", 86, "", ["vs Bennett"], """0 HR, 92.3 mph EV, 12.5% barrels. Bennett RHB split +1.30, HR risk 0.93. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.0, 'batterK': 25.5, 'batterWhiff': 21.9, 'pitcherK': 20.3}),
            row("Willson Contreras", "R", "+359", 61, "", ["vs Gore"], """0 HR, 94.9 mph EV. Gore RHB split -0.49, HR risk -0.65. tough split lane (-0.49); pitcher suppresses HR (-0.65).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 24.4, 'batterWhiff': 28.0, 'pitcherK': 21.8}),
            row("Wilyer Abreu", "L", "+425", 59, "", ["vs Gore"], """0 HR, 2 near-HR, 92.2 mph EV, 25.0% barrels. Gore LHB split -0.31, HR risk -0.65. slight split headwind (-0.31); pitcher suppresses HR (-0.65).""", blast="good", contact={'stars': 3, 'k': 21.9, 'batterK': 22.1, 'batterWhiff': 24.9, 'pitcherK': 21.8}),
            row("Nick Sogard", "S", "+1150", 40, "", ["vs Gore"], """0 HR, 86.8 mph EV. Gore SHB→RHB split -0.49, HR risk -0.65. tough split lane (-0.49); pitcher suppresses HR (-0.65).""", contact={'stars': 3, 'k': 22.6, 'batterK': 25.3, 'batterWhiff': 23.8, 'pitcherK': 21.8}),
        ],
    },
    {
        "title": "CWS @ CLE - Anthony Kay (L, CWS) vs Parker Messick (L, CLE)",
        "kLines": {'Kay': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 22.0, 'matchupK': 17.2, 'ownK': 18.3}, 'Messick': {'k': 6.8, 'lo': 5, 'hi': 8, 'bf': 23.3, 'matchupK': 29.3, 'ownK': 28.3}},
        "description": "Tail key data: Park boost -15% (stadium -5%, weather -10%). Kay (HR risk 0.03, vs LHB -1.05, vs RHB +0.49). Messick (HR risk -0.84, vs LHB +0.18, vs RHB -0.98).",
        "rows": [
            row("Jo Adell", "R", "+524", 69, "", ["vs Kay"], """1 HR, 1 near-HR, 88.3 mph EV, 12.5% barrels. Kay RHB split +0.49, HR risk 0.03. park/weather net drag (-15%).""", blast="good", contact={'stars': 3, 'k': 20.6, 'batterK': 22.1, 'batterWhiff': 27.5, 'pitcherK': 18.3}),
            row("Patrick Bailey", "S", "+750", 57, "", ["vs Kay"], """0 HR, 98.3 mph EV. Kay SHB→RHB split +0.49, HR risk 0.03. park/weather net drag (-15%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.5, 'batterK': 25.0, 'batterWhiff': 24.3, 'pitcherK': 18.3}),
            row("Chase Meidroth", "R", "+1120", 64, "🌕 💣", ["vs Messick"], """2 HR, 2 near-HR, 87.9 mph EV, 25.0% barrels. Messick RHB split -0.98, HR risk -0.84. tough split lane (-0.98); pitcher suppresses HR (-0.84).""", blast="high", contact={'stars': 2, 'k': 24.9, 'batterK': 20.7, 'batterWhiff': 23.7, 'pitcherK': 28.3}),
            row("Angel Martinez", "S", "+675", 69, "💎", ["vs Kay"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 88.8 mph EV, 12.5% barrels. Kay SHB→RHB split +0.49, HR risk 0.03. park/weather net drag (-15%).""", blast="good", contact={'stars': 4, 'k': 18.8, 'batterK': 21.3, 'batterWhiff': 18.8, 'pitcherK': 18.3}),
            row("Colson Montgomery", "L", "+471", 80, "🌕 💣", ["vs Messick"], """2 HR, 2 near-HR, 94.7 mph EV, 37.5% barrels. Messick LHB split +0.18, HR risk -0.84. pitcher suppresses HR (-0.84); park/weather net drag (-15%).""", blast="high", contact={'stars': 1, 'k': 33.7, 'batterK': 42.2, 'batterWhiff': 36.8, 'pitcherK': 28.3}),
            row("Munetaka Murakami", "L", "+432", 67, "💎", ["vs Messick"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 98.3 mph EV, 12.5% barrels. Messick LHB split +0.18, HR risk -0.84. pitcher suppresses HR (-0.84); park/weather net drag (-15%).""", blast="good", contact={'stars': 1, 'k': 36.3, 'batterK': 44.8, 'batterWhiff': 44.5, 'pitcherK': 28.3}),
            row("Randal Grichuk", "R", "+610", 53, "", ["vs Messick"], """0 HR, 98.4 mph EV. Messick RHB split -0.98, HR risk -0.84. tough split lane (-0.98); pitcher suppresses HR (-0.84).""", blast="good", contact={'stars': 2, 'k': 25.5, 'batterK': 25.5, 'batterWhiff': 23.0, 'pitcherK': 28.3}),
            row("Miguel Vargas", "R", "+514", 70, "🌕 💣", ["vs Messick"], """1 HR, 2 near-HR, 97.8 mph EV, 25.0% barrels. Messick RHB split -0.98, HR risk -0.84. tough split lane (-0.98); pitcher suppresses HR (-0.84).""", blast="high", contact={'stars': 2, 'k': 24.2, 'batterK': 21.1, 'batterWhiff': 19.5, 'pitcherK': 28.3}),
        ],
    },
    {
        "title": "DET @ TOR - Keider Montero (R, DET) vs Max Scherzer (R, TOR)",
        "kLines": {'Montero': {'k': 3.5, 'lo': 2, 'hi': 5, 'bf': 22.2, 'matchupK': 15.9, 'ownK': 16.0}, 'Scherzer': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 20.2, 'matchupK': 20.1, 'ownK': 19.4}},
        "description": "Tail key data: Park boost -11% (stadium +6%, weather -17%). Montero (HR risk 0.10, vs LHB +0.62, vs RHB -0.75). Scherzer (HR risk 0.51, vs LHB +0.52, vs RHB +0.42).",
        "rows": [
            row("Kazuma Okamoto", "R", "+360", 87, "🌕 💣", ["vs Montero"], """2 HR, 2 near-HR, 95.5 mph EV, 25.0% barrels. Montero RHB split -0.75, HR risk 0.10. tough split lane (-0.75); park/weather net drag (-11%).""", blast="high", contact={'stars': 4, 'k': 19.5, 'batterK': 21.3, 'batterWhiff': 28.6, 'pitcherK': 16.0}),
            row("Andres Gimenez", "L", "+930", 46, "", ["vs Montero"], """0 HR, 91.8 mph EV. Montero LHB split +0.62, HR risk 0.10. park/weather net drag (-11%); limited recent HR events.""", contact={'stars': 5, 'k': 16.8, 'batterK': 14.3, 'batterWhiff': 20.3, 'pitcherK': 16.0}),
            row("Brett Bateman", "L", "+1400", 71, "🌕 💣", ["vs Montero"], """2 HR, 2 near-HR, 88.5 mph EV, 25.0% barrels. Montero LHB split +0.62, HR risk 0.10. park/weather net drag (-11%).""", blast="high", contact={'stars': 4, 'k': 17.3, 'batterK': 21.7, 'batterWhiff': 14.3, 'pitcherK': 16.0}),
            row("Alejandro Kirk", "R", "+590", 62, "", ["vs Montero"], """1 HR, 1 near-HR, 87.5 mph EV, 12.5% barrels. Montero RHB split -0.75, HR risk 0.10. tough split lane (-0.75); park/weather net drag (-11%).""", blast="good", contact={'stars': 5, 'k': 15.3, 'batterK': 14.1, 'batterWhiff': 13.8, 'pitcherK': 16.0}),
            row("Nathan Lukes", "L", "+920", 43, "", ["vs Montero"], """0 HR, 83.2 mph EV. Montero LHB split +0.62, HR risk 0.10. park/weather net drag (-11%); limited recent HR events.""", contact={'stars': 5, 'k': 15.4, 'batterK': 13.7, 'batterWhiff': 13.5, 'pitcherK': 16.0}),
            row("Spencer Torkelson", "R", "+433", 90, "🌕 💣 💎", ["vs Scherzer"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 95.4 mph EV, 12.5% barrels. Scherzer RHB split +0.42, HR risk 0.51. park/weather net drag (-11%).""", blast="high", contact={'stars': 2, 'k': 25.2, 'batterK': 33.8, 'batterWhiff': 36.5, 'pitcherK': 19.4}),
            row("Kevin McGonigle", "L", "+490", 86, "🌕 💣 💎", ["vs Scherzer"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 97.3 mph EV, 25.0% barrels. Scherzer LHB split +0.52, HR risk 0.51. park/weather net drag (-11%).""", blast="high", contact={'stars': 5, 'k': 16.5, 'batterK': 11.2, 'batterWhiff': 18.1, 'pitcherK': 19.4}),
            row("Dillon Dingler", "R", "+488", 74, "", ["vs Scherzer"], """1 HR, 1 near-HR, 85.4 mph EV, 12.5% barrels. Scherzer RHB split +0.42, HR risk 0.51. park/weather net drag (-11%); lighter EV form (85.4 mph).""", blast="good", contact={'stars': 3, 'k': 22.1, 'batterK': 29.1, 'batterWhiff': 23.1, 'pitcherK': 19.4}),
            row("Riley Greene", "L", "+300", 80, "", ["vs Scherzer"], """1 HR, 1 near-HR, 91.0 mph EV, 12.5% barrels. Scherzer LHB split +0.52, HR risk 0.51. park/weather net drag (-11%).""", blast="good", contact={'stars': 3, 'k': 23.8, 'batterK': 29.4, 'batterWhiff': 31.5, 'pitcherK': 19.4}),
            row("Colt Keith", "L", "+475", 83, "⭐", ["vs Scherzer"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.5 mph EV, 25.0% barrels. Scherzer LHB split +0.52, HR risk 0.51. park/weather net drag (-11%).""", blast="good", contact={'stars': 3, 'k': 23.0, 'batterK': 28.6, 'batterWhiff': 31.7, 'pitcherK': 19.4}),
            row("Brett Callahan", "L", "+491", 68, "", ["vs Scherzer"], """0 HR, 2 near-HR, 91.0 mph EV, 25.0% barrels. Scherzer LHB split +0.52, HR risk 0.51. park/weather net drag (-11%).""", blast="good", contact={'stars': 3, 'k': 23.9, 'batterK': 38.8, 'batterWhiff': 31.4, 'pitcherK': 19.4}),
        ],
    },
    {
        "title": "KC @ HOU - Daniel Lynch IV (L, KC) vs Cristian Javier (R, HOU)",
        "kLines": {'Lynch IV': {'k': 3.1, 'lo': 1, 'hi': 5, 'bf': 18.6, 'matchupK': 16.4, 'ownK': 12.2}, 'Javier': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 19.8, 'matchupK': 23.9, 'ownK': 26.1}},
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +0%). Lynch IV (HR risk -0.49, vs LHB -0.69, vs RHB -0.13). Javier (HR risk 0.04, vs LHB -0.53, vs RHB +0.93).",
        "rows": [
            row("Jose Altuve", "R", "+600", 59, "", ["vs Lynch IV"], """1 HR, 1 near-HR, 91.9 mph EV. Lynch IV RHB split -0.13, HR risk -0.49. slight split headwind (-0.13); pitcher suppresses HR (-0.49).""", blast="good", contact={'stars': 4, 'k': 19.6, 'batterK': 16.5, 'batterWhiff': 19.5, 'pitcherK': None}),
            row("Nelson Velazquez", "R", "N/A", 80, "", ["vs Lynch IV"], """1 HR, 2 near-HR, 92.8 mph EV, 12.5% barrels. Lynch IV RHB split -0.13, HR risk -0.49. slight split headwind (-0.13); pitcher suppresses HR (-0.49).""", blast="good", contact={'stars': 2, 'k': 27.2, 'batterK': 39.5, 'batterWhiff': 44.3, 'pitcherK': None}),
            row("Yainer Diaz", "R", "+600", 61, "", ["vs Lynch IV"], """0 HR, 93.5 mph EV. Lynch IV RHB split -0.13, HR risk -0.49. slight split headwind (-0.13); pitcher suppresses HR (-0.49).""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 19.1, 'batterWhiff': 23.0, 'pitcherK': None}),
            row("Yordan Alvarez", "L", "+360", 61, "💎", ["vs Lynch IV"], """Worst Pickz Hidden Gem. 0 HR, 90.7 mph EV. Lynch IV LHB split -0.69, HR risk -0.49. tough split lane (-0.69); pitcher suppresses HR (-0.49).""", contact={'stars': 3, 'k': 21.3, 'batterK': 22.1, 'batterWhiff': 20.5, 'pitcherK': None}),
            row("Jeremy Pena", "R", "+536", 57, "", ["vs Lynch IV"], """0 HR, 88.7 mph EV. Lynch IV RHB split -0.13, HR risk -0.49. slight split headwind (-0.13); pitcher suppresses HR (-0.49).""", contact={'stars': 2, 'k': 27.1, 'batterK': 32.9, 'batterWhiff': 35.6, 'pitcherK': None}),
            row("Salvador Perez", "R", "+396", 75, "💎", ["vs Javier"], """Worst Pickz Hidden Gem. 0 HR, 94.6 mph EV, 12.5% barrels. Javier RHB split +0.93, HR risk 0.04. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.5, 'batterK': 16.9, 'batterWhiff': 24.7, 'pitcherK': 26.1}),
            row("Bobby Witt Jr.", "R", "+380", 86, "⭐", ["vs Javier"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 95.8 mph EV, 25.0% barrels. Javier RHB split +0.93, HR risk 0.04.""", blast="good", contact={'stars': 3, 'k': 22.3, 'batterK': 16.5, 'batterWhiff': 25.7, 'pitcherK': 26.1}),
            row("Carter Jensen", "L", "+370", 70, "", ["vs Javier"], """0 HR, 91.9 mph EV, 25.0% barrels. Javier LHB split -0.53, HR risk 0.04. tough split lane (-0.53); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.9, 'batterK': 25.9, 'batterWhiff': 28.9, 'pitcherK': 26.1}),
            row("Vinnie Pasquantino", "L", "+466", 74, "💎", ["vs Javier"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.0 mph EV, 12.5% barrels. Javier LHB split -0.53, HR risk 0.04. tough split lane (-0.53).""", blast="good", contact={'stars': 4, 'k': 19.5, 'batterK': 13.1, 'batterWhiff': 15.4, 'pitcherK': 26.1}),
            row("Jac Caglianone", "L", "+333", 66, "", ["vs Javier"], """0 HR, 92.6 mph EV. Javier LHB split -0.53, HR risk 0.04. tough split lane (-0.53); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 27.3, 'batterK': 29.3, 'batterWhiff': 32.4, 'pitcherK': 26.1}),
            row("John Rave", "L", "N/A", 77, "🌕 💣", ["vs Javier"], """2 HR, 2 near-HR, 94.8 mph EV. Javier LHB split -0.53, HR risk 0.04. tough split lane (-0.53).""", blast="high", contact={'stars': 3, 'k': 23.5, 'batterK': 21.7, 'batterWhiff': 23.0, 'pitcherK': 26.1}),
        ],
    },
    {
        "title": "LAD @ CIN - Blake Snell (L, LAD) vs Andrew Abbott (L, CIN)",
        "kLines": {'Snell': {'k': 6.7, 'lo': 5, 'hi': 8, 'bf': 21.9, 'matchupK': 30.8, 'ownK': 33.1}, 'Abbott': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 22.5, 'matchupK': 17.0, 'ownK': 16.2}},
        "description": "Tail key data: Park boost +15% (stadium +14%, weather +1%). Snell (HR risk -2.10, vs LHB -1.72, vs RHB -1.50). Abbott (HR risk 0.88, vs LHB +2.06, vs RHB +0.01).",
        "rows": [
            row("Elly De La Cruz", "S", "+489", 81, "🌕 💣", ["vs Snell"], """2 HR, 2 near-HR, 97.3 mph EV, 25.0% barrels. Snell SHB→RHB split -1.50, HR risk -2.10. tough split lane (-1.50); pitcher suppresses HR (-2.10).""", blast="high", contact={'stars': 1, 'k': 29.8, 'batterK': 28.7, 'batterWhiff': 28.4, 'pitcherK': 33.1}),
            row("Juan Brito", "S", "+880", 56, "", ["vs Snell"], """1 HR, 1 near-HR, 94.0 mph EV, 37.5% barrels. Snell SHB→RHB split -1.50, HR risk -2.10. tough split lane (-1.50); pitcher suppresses HR (-2.10).""", blast="good", contact={'stars': 1, 'k': 28.7, 'batterK': 26.5, 'batterWhiff': 28.5, 'pitcherK': 33.1}),
            row("Tyler Stephenson", "R", "+600", 58, "", ["vs Snell"], """1 HR, 1 near-HR, 93.9 mph EV, 12.5% barrels. Snell RHB split -1.50, HR risk -2.10. tough split lane (-1.50); pitcher suppresses HR (-2.10).""", blast="good", contact={'stars': 1, 'k': 29.4, 'batterK': 29.7, 'batterWhiff': 27.3, 'pitcherK': 33.1}),
            row("Matt McLain", "R", "+750", 50, "", ["vs Snell"], """1 HR, 1 near-HR, 90.5 mph EV, 12.5% barrels. Snell RHB split -1.50, HR risk -2.10. tough split lane (-1.50); pitcher suppresses HR (-2.10).""", blast="good", contact={'stars': 1, 'k': 30.5, 'batterK': 31.6, 'batterWhiff': 29.8, 'pitcherK': 33.1}),
            row("Kyle Tucker", "L", "+520", 93, "⭐ 🌕 💣", ["vs Abbott"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.4 mph EV, 25.0% barrels. Abbott LHB split +2.06, HR risk 0.88.""", blast="high", contact={'stars': 5, 'k': 14.9, 'batterK': 11.5, 'batterWhiff': 13.7, 'pitcherK': 16.2}),
            row("Teoscar Hernandez", "R", "+336", 93, "🌕 💣 💎", ["vs Abbott"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 95.8 mph EV, 37.5% barrels. Abbott RHB split +0.01, HR risk 0.88.""", blast="high", contact={'stars': 3, 'k': 22.2, 'batterK': 26.5, 'batterWhiff': 36.9, 'pitcherK': 16.2}),
            row("Max Muncy", "L", "+187", 88, "🌕 💣", ["vs Abbott"], """1 HR, 1 near-HR, 92.9 mph EV. Abbott LHB split +2.06, HR risk 0.88.""", blast="good", contact={'stars': 3, 'k': 21.4, 'batterK': 28.2, 'batterWhiff': 30.9, 'pitcherK': 16.2}),
            row("Eliezer Alfonzo", "S", "N/A", 57, "", ["vs Abbott"], """0 HR, 90.5 mph EV. Abbott SHB→RHB split +0.01, HR risk 0.88. limited recent HR events.""", contact={'stars': 5, 'k': 17.0, 'batterK': 10.7, 'batterWhiff': 13.7, 'pitcherK': 16.2}),
            row("Hunter Feduccia", "L", "N/A", 79, "", ["vs Abbott"], """0 HR, 1 near-HR, 93.8 mph EV, 12.5% barrels. Abbott LHB split +2.06, HR risk 0.88. limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.4, 'batterK': 20.7, 'batterWhiff': 22.0, 'pitcherK': 16.2}),
        ],
    },
    {
        "title": "MIA @ ARI - Ryan Gusto (R, MIA) vs Merrill Kelly (R, ARI)",
        "kLines": {'Gusto': {'k': 3.5, 'lo': 2, 'hi': 5, 'bf': 20.0, 'matchupK': 17.7, 'ownK': 18.2}, 'Kelly': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 23.9, 'matchupK': 18.9, 'ownK': 17.5}},
        "description": "Tail key data: Park boost -9% (stadium -9%, weather -1%). Gusto (HR risk -0.25, vs LHB +0.23, vs RHB -0.43). Kelly (HR risk -0.23, vs LHB +0.15, vs RHB -0.44).",
        "rows": [
            row("Lars Nootbaar", "L", "+550", 79, "💎", ["vs Gusto"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.8 mph EV, 12.5% barrels. Gusto LHB split +0.23, HR risk -0.25. pitcher risk below avg (-0.25); park/weather net drag (-9%).""", blast="good", contact={'stars': 4, 'k': 18.1, 'batterK': 19.0, 'batterWhiff': 16.8, 'pitcherK': 18.2}),
            row("Ketel Marte", "S", "+430", 66, "⭐", ["vs Gusto"], """Worst Pickz Favorite. 0 HR, 97.9 mph EV, 12.5% barrels. Gusto SHB→LHB split +0.23, HR risk -0.25. pitcher risk below avg (-0.25); park/weather net drag (-9%).""", blast="good", contact={'stars': 5, 'k': 13.7, 'batterK': 6.7, 'batterWhiff': 11.7, 'pitcherK': 18.2}),
            row("Gabriel Moreno", "R", "+940", 60, "", ["vs Gusto"], """1 HR, 1 near-HR, 90.1 mph EV, 12.5% barrels. Gusto RHB split -0.43, HR risk -0.25. tough split lane (-0.43); pitcher risk below avg (-0.25).""", blast="good", contact={'stars': 5, 'k': 16.5, 'batterK': 13.8, 'batterWhiff': 15.9, 'pitcherK': 18.2}),
            row("Corbin Carroll", "L", "+457", 74, "", ["vs Gusto"], """0 HR, 95.6 mph EV, 25.0% barrels. Gusto LHB split +0.23, HR risk -0.25. pitcher risk below avg (-0.25); park/weather net drag (-9%).""", blast="good", contact={'stars': 3, 'k': 23.8, 'batterK': 31.7, 'batterWhiff': 32.2, 'pitcherK': 18.2}),
            row("Graham Pauley", "L", "N/A", 66, "", ["vs Kelly"], """1 HR, 1 near-HR, 93.7 mph EV, 20.0% barrels. Kelly LHB split +0.15, HR risk -0.23. pitcher risk below avg (-0.23); park/weather net drag (-9%).""", blast="good", contact={'stars': 4, 'k': 19.7, 'batterK': 23.4, 'batterWhiff': 24.2, 'pitcherK': 17.5}),
            row("Joe Mack", "L", "+760", 52, "⭐", ["vs Kelly"], """Worst Pickz Favorite. 0 HR, 92.9 mph EV. Kelly LHB split +0.15, HR risk -0.23. pitcher risk below avg (-0.23); park/weather net drag (-9%).""", blast="good", contact={'stars': 3, 'k': 20.8, 'batterK': 25.9, 'batterWhiff': 28.0, 'pitcherK': 17.5}),
            row("Javier Sanoja", "R", "+1160", 57, "💎", ["vs Kelly"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 91.1 mph EV, 20.0% barrels. Kelly RHB split -0.44, HR risk -0.23. tough split lane (-0.44); pitcher risk below avg (-0.23).""", blast="good", contact={'stars': 5, 'k': 13.8, 'batterK': 5.9, 'batterWhiff': 13.8, 'pitcherK': 17.5}),
            row("Kyle Stowers", "L", "+380", 56, "", ["vs Kelly"], """0 HR, 1 near-HR, 89.5 mph EV. Kelly LHB split +0.15, HR risk -0.23. pitcher risk below avg (-0.23); park/weather net drag (-9%).""", contact={'stars': 2, 'k': 26.0, 'batterK': 37.3, 'batterWhiff': 39.8, 'pitcherK': 17.5}),
        ],
    },
    {
        "title": "MIL @ PIT - Logan Henderson (R, MIL) vs Jared Jones (R, PIT)",
        "kLines": {'Henderson': {'k': 6.0, 'lo': 4, 'hi': 8, 'bf': 20.8, 'matchupK': 29.0, 'ownK': 30.0}, 'Jones': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 20.3, 'matchupK': 25.7, 'ownK': 28.6}},
        "description": "Tail key data: Park boost -9% (stadium -14%, weather +6%). Henderson (HR risk 0.07, vs LHB +0.41, vs RHB -0.30). Jones (HR risk -0.18, vs LHB +0.38, vs RHB -0.69).",
        "rows": [
            row("Bryan Reynolds", "S", "+725", 80, "⭐", ["vs Henderson"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.3 mph EV, 12.5% barrels. Henderson SHB→LHB split +0.41, HR risk 0.07. park/weather net drag (-9%).""", blast="good", contact={'stars': 2, 'k': 24.7, 'batterK': 16.9, 'batterWhiff': 24.6, 'pitcherK': 30.0}),
            row("Rafael Flores", "R", "+800", 79, "🌕 💣 💎", ["vs Henderson"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 98.8 mph EV, 25.0% barrels. Henderson RHB split -0.30, HR risk 0.07. slight split headwind (-0.30); park/weather net drag (-9%).""", blast="high", contact={'stars': 1, 'k': 28.8, 'batterK': 28.0, 'batterWhiff': 28.8, 'pitcherK': 30.0}),
            row("Oneil Cruz", "L", "+425", 78, "⭐", ["vs Henderson"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 90.6 mph EV, 12.5% barrels. Henderson LHB split +0.41, HR risk 0.07. park/weather net drag (-9%).""", blast="good", contact={'stars': 1, 'k': 31.0, 'batterK': 30.6, 'batterWhiff': 34.3, 'pitcherK': 30.0}),
            row("Garrett Mitchell", "L", "+800", 77, "💎", ["vs Jones"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.6 mph EV, 12.5% barrels. Jones LHB split +0.38, HR risk -0.18. pitcher risk below avg (-0.18); park/weather net drag (-9%).""", blast="good", contact={'stars': 1, 'k': 28.3, 'batterK': 26.9, 'batterWhiff': 33.0, 'pitcherK': 28.6}),
            row("Brice Turang", "L", "+760", 65, "💎", ["vs Jones"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 90.9 mph EV, 12.5% barrels. Jones LHB split +0.38, HR risk -0.18. pitcher risk below avg (-0.18); park/weather net drag (-9%).""", contact={'stars': 2, 'k': 24.4, 'batterK': 21.1, 'batterWhiff': 21.4, 'pitcherK': 28.6}),
            row("Jake Bauers", "L", "+500", 70, "", ["vs Jones"], """1 HR, 1 near-HR, 88.0 mph EV, 12.5% barrels. Jones LHB split +0.38, HR risk -0.18. pitcher risk below avg (-0.18); park/weather net drag (-9%).""", blast="good", contact={'stars': 1, 'k': 29.2, 'batterK': 29.1, 'batterWhiff': 33.8, 'pitcherK': 28.6}),
            row("William Contreras", "R", "+600", 59, "", ["vs Jones"], """0 HR, 92.8 mph EV. Jones RHB split -0.69, HR risk -0.18. tough split lane (-0.69); pitcher risk below avg (-0.18).""", blast="good", contact={'stars': 3, 'k': 23.0, 'batterK': 17.2, 'batterWhiff': 21.1, 'pitcherK': 28.6}),
            row("Bo Naylor", "L", "N/A", 79, "", ["vs Jones"], """1 HR, 3 near-HR, 94.4 mph EV, 37.5% barrels. Jones LHB split +0.38, HR risk -0.18. pitcher risk below avg (-0.18); park/weather net drag (-9%).""", blast="good", contact={'stars': 3, 'k': 23.6, 'batterK': 25.9, 'batterWhiff': 14.0, 'pitcherK': 28.6}),
        ],
    },
    {
        "title": "NYY @ MIN - Carlos Rodon (L, NYY) vs Zebby Matthews (R, MIN)",
        "kLines": {'Rodon': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 21.0, 'matchupK': 24.0, 'ownK': 27.8}, 'Matthews': {'k': 4.9, 'lo': 3, 'hi': 7, 'bf': 23.3, 'matchupK': 21.2, 'ownK': 20.0}},
        "description": "Tail key data: Park boost -31% (stadium -7%, weather -24%). Rodon (HR risk -0.20, vs LHB +0.05, vs RHB -0.15). Matthews (HR risk 0.65, vs LHB +0.99, vs RHB +0.02).",
        "rows": [
            row("Emmanuel Rodriguez", "L", "N/A", 70, "", ["vs Rodon"], """0 HR, 1 near-HR, 97.7 mph EV, 16.7% barrels. Rodon LHB split +0.05, HR risk -0.20. pitcher risk below avg (-0.20); park/weather net drag (-31%).""", blast="good", contact={'stars': 2, 'k': 24.9, 'batterK': 26.7, 'batterWhiff': 23.3, 'pitcherK': 27.8}),
            row("Ryan Kreidler", "R", "+930", 63, "", ["vs Rodon"], """1 HR, 1 near-HR, 96.4 mph EV, 12.5% barrels. Rodon RHB split -0.15, HR risk -0.20. slight split headwind (-0.15); pitcher risk below avg (-0.20).""", blast="good", contact={'stars': 2, 'k': 27.3, 'batterK': 27.6, 'batterWhiff': 35.7, 'pitcherK': 27.8}),
            row("Kody Clemens", "L", "+610", 51, "", ["vs Rodon"], """0 HR, 85.6 mph EV. Rodon LHB split +0.05, HR risk -0.20. pitcher risk below avg (-0.20); park/weather net drag (-31%).""", contact={'stars': 3, 'k': 23.4, 'batterK': 21.4, 'batterWhiff': 17.9, 'pitcherK': 27.8}),
            row("Cody Bellinger", "L", "+567", 88, "🌕 💣 💎", ["vs Matthews"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.7 mph EV, 25.0% barrels. Matthews LHB split +0.99, HR risk 0.65. park/weather net drag (-31%).""", blast="high", contact={'stars': 4, 'k': 17.6, 'batterK': 13.1, 'batterWhiff': 18.8, 'pitcherK': 20.0}),
            row("Austin Wells", "L", "+600", 86, "🌕 💣", ["vs Matthews"], """2 HR, 2 near-HR, 95.1 mph EV, 12.5% barrels. Matthews LHB split +0.99, HR risk 0.65. park/weather net drag (-31%).""", blast="high", contact={'stars': 3, 'k': 22.6, 'batterK': 31.3, 'batterWhiff': 25.0, 'pitcherK': 20.0}),
            row("Amed Rosario", "R", "N/A", 79, "", ["vs Matthews"], """1 HR, 1 near-HR, 94.7 mph EV, 12.5% barrels. Matthews RHB split +0.02, HR risk 0.65. park/weather net drag (-31%).""", blast="good", contact={'stars': 3, 'k': 20.4, 'batterK': 17.6, 'batterWhiff': 24.5, 'pitcherK': 20.0}),
            row("Aaron Judge", "R", "+310", 85, "", ["vs Matthews"], """0 HR, 1 near-HR, 95.9 mph EV, 12.5% barrels. Matthews RHB split +0.02, HR risk 0.65. park/weather net drag (-31%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.7, 'batterK': 32.1, 'batterWhiff': 30.8, 'pitcherK': 20.0}),
            row("Ben Rice", "L", "+370", 82, "", ["vs Matthews"], """0 HR, 1 near-HR, 92.9 mph EV, 12.5% barrels. Matthews LHB split +0.99, HR risk 0.65. park/weather net drag (-31%); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.6, 'batterK': 19.8, 'batterWhiff': 20.8, 'pitcherK': 20.0}),
            row("Heliot Ramos", "R", "N/A", 73, "", ["vs Matthews"], """0 HR, 1 near-HR, 93.4 mph EV, 12.5% barrels. Matthews RHB split +0.02, HR risk 0.65. park/weather net drag (-31%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 26.6, 'batterWhiff': 31.7, 'pitcherK': 20.0}),
            row("Luis Garcia Jr.", "L", "+450", 71, "", ["vs Matthews"], """0 HR, 91.2 mph EV, 12.5% barrels. Matthews LHB split +0.99, HR risk 0.65. park/weather net drag (-31%); limited recent HR events.""", contact={'stars': 3, 'k': 20.3, 'batterK': 18.2, 'batterWhiff': 26.0, 'pitcherK': 20.0}),
        ],
    },
    {
        "title": "PHI @ WSH - Zack Wheeler (R, PHI) vs Jared Simpson (L, WSH)",
        "kLines": {'Wheeler': {'k': 6.1, 'lo': 5, 'hi': 8, 'bf': 22.7, 'matchupK': 27.1, 'ownK': 29.2}, 'Simpson': {'k': 5.1, 'lo': 3, 'hi': 7, 'bf': 21.7, 'matchupK': 23.5, 'ownK': 36.4}},
        "description": "Tail key data: Park boost +4% (stadium +3%, weather +1%). Wheeler (HR risk 0.28, vs LHB +0.87, vs RHB -0.28). Simpson - thin book: first MLB start, 4.0 career IP.",
        "rows": [
            row("James Wood", "L", "+360", 83, "", ["vs Wheeler"], """0 HR, 94.8 mph EV, 12.5% barrels. Wheeler LHB split +0.87, HR risk 0.28. limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 26.1, 'batterK': 23.9, 'batterWhiff': 23.8, 'pitcherK': 29.2}),
            row("Brady House", "R", "+750", 77, "🌕 💣", ["vs Wheeler"], """0 HR, 99.2 mph EV, 25.0% barrels. Wheeler RHB split -0.28, HR risk 0.28. slight split headwind (-0.28); limited recent HR events.""", blast="high", contact={'stars': 3, 'k': 22.9, 'batterK': 16.0, 'batterWhiff': 18.9, 'pitcherK': 29.2}),
            row("Keibert Ruiz", "S", "+800", 69, "", ["vs Wheeler"], """1 HR, 2 near-HR, 91.8 mph EV, 12.5% barrels. Wheeler SHB→LHB split +0.87, HR risk 0.28.""", blast="good", contact={'stars': 3, 'k': 20.7, 'batterK': 7.4, 'batterWhiff': 17.1, 'pitcherK': 29.2}),
            row("Yohandy Morales", "R", "+990", 79, "", ["vs Wheeler"], """1 HR, 1 near-HR, 93.1 mph EV, 25.0% barrels. Wheeler RHB split -0.28, HR risk 0.28. slight split headwind (-0.28).""", blast="good", contact={'stars': 1, 'k': 28.6, 'batterK': 30.0, 'batterWhiff': 37.7, 'pitcherK': 29.2}),
            row("Daylen Lile", "L", "+592", 78, "💎", ["vs Wheeler"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.0 mph EV, 25.0% barrels. Wheeler LHB split +0.87, HR risk 0.28. limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.4, 'batterK': 21.1, 'batterWhiff': 24.8, 'pitcherK': 29.2}),
            row("Andrew Pinckney", "R", "N/A", 70, "", ["vs Wheeler"], """0 HR, 95.9 mph EV, 20.0% barrels. Wheeler RHB split -0.28, HR risk 0.28. slight split headwind (-0.28); limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 27.6, 'batterK': 34.5, 'batterWhiff': 31.1, 'pitcherK': 29.2}),
            row("Alec Bohm", "R", "+800", 82, "🌕 💣 💎", ["vs Simpson"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 99.8 mph EV, 25.0% barrels. limited split/risk sample.""", blast="high", contact={'stars': 3, 'k': 21.8, 'batterK': 19.2, 'batterWhiff': 21.3, 'pitcherK': 36.4}),
            row("Trea Turner", "R", "+600", 62, "⭐", ["vs Simpson"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 92.2 mph EV, 12.5% barrels. limited split/risk sample; limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.8, 'batterK': 19.3, 'batterWhiff': 32.7, 'pitcherK': 36.4}),
            row("Kyle Schwarber", "L", "+300", 74, "", ["vs Simpson"], """1 HR, 1 near-HR, 90.9 mph EV. limited split/risk sample.""", blast="good", contact={'stars': 2, 'k': 25.5, 'batterK': 26.7, 'batterWhiff': 29.5, 'pitcherK': 36.4}),
        ],
    },
    {
        "title": "SD @ COL - Robbie Ray (L, SD) vs Mason Adams 🧤 (R, COL)",
        "kLines": {'Ray': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 22.6, 'matchupK': 19.2, 'ownK': 19.3}, 'Adams': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 20.7, 'matchupK': 24.4, 'ownK': 28.6}},
        "description": "Tail key data: Park boost +21% (stadium +20%, weather +0%). Ray (HR risk 0.21, vs LHB -0.51, vs RHB +0.49). Adams 🧤 (HR risk 1.93, vs LHB +0.88, vs RHB +2.31).",
        "rows": [
            row("Cole Carrigg", "S", "+586", 64, "💎", ["vs Ray"], """Worst Pickz Hidden Gem. 0 HR, 90.0 mph EV. Ray SHB→RHB split +0.49, HR risk 0.21. limited recent HR events.""", contact={'stars': 3, 'k': 23.0, 'batterK': 30.1, 'batterWhiff': 26.7, 'pitcherK': 19.3}),
            row("Troy Johnston", "L", "+448", 51, "", ["vs Ray"], """0 HR, 91.9 mph EV. Ray LHB split -0.51, HR risk 0.21. tough split lane (-0.51); limited recent HR events.""", contact={'stars': 3, 'k': 21.8, 'batterK': 21.7, 'batterWhiff': 30.8, 'pitcherK': 19.3}),
            row("Connor Norby", "R", "+520", 69, "", ["vs Ray"], """0 HR, 2 near-HR, 86.3 mph EV, 12.5% barrels. Ray RHB split +0.49, HR risk 0.21. lighter EV form (86.3 mph).""", blast="good", contact={'stars': 3, 'k': 21.3, 'batterK': 25.9, 'batterWhiff': 23.5, 'pitcherK': 19.3}),
            row("Hunter Goodman", "R", "+210", 86, "🌕 💣", ["vs Ray"], """2 HR, 2 near-HR, 92.0 mph EV. Ray RHB split +0.49, HR risk 0.21.""", blast="high", contact={'stars': 3, 'k': 21.4, 'batterK': 22.9, 'batterWhiff': 27.9, 'pitcherK': 19.3}),
            row("Fernando Tatis Jr.", "R", "+301", 99, "🚀 ⭐ 🌕 💣", ["vs Adams"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 103.1 mph EV, 25.0% barrels. Adams RHB split +2.31, HR risk 1.93.""", blast="high", contact={'stars': 3, 'k': 22.9, 'batterK': 18.9, 'batterWhiff': 25.0, 'pitcherK': 28.6}),
            row("Jackson Merrill", "L", "+349", 99, "🚀 ⭐ 🌕 💣", ["vs Adams"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 102.4 mph EV, 12.5% barrels. Adams LHB split +0.88, HR risk 1.93.""", blast="good", contact={'stars': 3, 'k': 22.3, 'batterK': 16.1, 'batterWhiff': 25.7, 'pitcherK': 28.6}),
            row("Xander Bogaerts", "R", "+650", 84, "", ["vs Adams"], """0 HR, 90.7 mph EV. Adams RHB split +2.31, HR risk 1.93. limited recent HR events.""", contact={'stars': 3, 'k': 22.7, 'batterK': 19.0, 'batterWhiff': 22.6, 'pitcherK': 28.6}),
            row("Manny Machado", "R", "+354", 94, "🌕 💣", ["vs Adams"], """2 HR, 2 near-HR, 84.0 mph EV, 12.5% barrels. Adams RHB split +2.31, HR risk 1.93. lighter EV form (84.0 mph).""", blast="high", contact={'stars': 3, 'k': 21.4, 'batterK': 15.7, 'batterWhiff': 21.9, 'pitcherK': 28.6}),
            row("Ty France", "R", "+510", 85, "💎", ["vs Adams"], """Worst Pickz Hidden Gem. 0 HR, 89.9 mph EV. Adams RHB split +2.31, HR risk 1.93. limited recent HR events.""", contact={'stars': 3, 'k': 23.9, 'batterK': 18.6, 'batterWhiff': 30.1, 'pitcherK': 28.6}),
        ],
    },
    {
        "title": "SEA @ LAA - George Kirby (R, SEA) vs Yusei Kikuchi (L, LAA)",
        "kLines": {'Kirby': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 24.3, 'matchupK': 18.6, 'ownK': 16.7}, 'Kikuchi': {'k': 4.9, 'lo': 3, 'hi': 7, 'bf': 21.5, 'matchupK': 22.9, 'ownK': 23.8}},
        "description": "Tail key data: Park boost -6% (stadium -9%, weather +3%). Kirby (HR risk -0.12, vs LHB +0.31, vs RHB -0.34). Kikuchi (HR risk 0.41, vs LHB -0.52, vs RHB +0.70).",
        "rows": [
            row("Moises Ballesteros", "L", "+710", 79, "🌕 💣 💎", ["vs Kirby"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.0 mph EV, 25.0% barrels. Kirby LHB split +0.31, HR risk -0.12. pitcher risk below avg (-0.12); park/weather net drag (-6%).""", blast="high", contact={'stars': 3, 'k': 21.4, 'batterK': 28.9, 'batterWhiff': 29.3, 'pitcherK': 16.7}),
            row("Josh Lowe", "L", "+680", 68, "", ["vs Kirby"], """1 HR, 1 near-HR, 93.3 mph EV, 12.5% barrels. Kirby LHB split +0.31, HR risk -0.12. pitcher risk below avg (-0.12); park/weather net drag (-6%).""", blast="good", contact={'stars': 3, 'k': 22.7, 'batterK': 34.5, 'batterWhiff': 34.9, 'pitcherK': 16.7}),
            row("Jose Siri", "R", "+502", 67, "", ["vs Kirby"], """0 HR, 93.2 mph EV, 25.0% barrels. Kirby RHB split -0.34, HR risk -0.12. slight split headwind (-0.34); pitcher risk below avg (-0.12).""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 36.0, 'batterWhiff': 39.8, 'pitcherK': 16.7}),
            row("Travis d'Arnaud", "R", "N/A", 52, "", ["vs Kirby"], """0 HR, 94.4 mph EV. Kirby RHB split -0.34, HR risk -0.12. slight split headwind (-0.34); pitcher risk below avg (-0.12).""", blast="good", contact={'stars': 3, 'k': 22.4, 'batterK': 40.0, 'batterWhiff': 33.3, 'pitcherK': 16.7}),
            row("Randy Arozarena", "R", "+444", 94, "🌕 💣 💎", ["vs Kikuchi"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 99.3 mph EV, 25.0% barrels. Kikuchi RHB split +0.70, HR risk 0.41. park/weather net drag (-6%).""", blast="high", contact={'stars': 3, 'k': 23.1, 'batterK': 22.5, 'batterWhiff': 25.1, 'pitcherK': 23.8}),
            row("Cal Raleigh", "S", "+310", 80, "💎", ["vs Kikuchi"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 89.0 mph EV, 12.5% barrels. Kikuchi SHB→RHB split +0.70, HR risk 0.41. park/weather net drag (-6%).""", blast="good", contact={'stars': 2, 'k': 26.8, 'batterK': 31.4, 'batterWhiff': 31.2, 'pitcherK': 23.8}),
            row("Dominic Canzone", "L", "+528", 82, "", ["vs Kikuchi"], """1 HR, 2 near-HR, 94.3 mph EV, 25.0% barrels. Kikuchi LHB split -0.52, HR risk 0.41. tough split lane (-0.52); park/weather net drag (-6%).""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 24.7, 'batterWhiff': 23.6, 'pitcherK': 23.8}),
            row("Julio Rodriguez", "R", "+434", 77, "", ["vs Kikuchi"], """0 HR, 94.5 mph EV, 12.5% barrels. Kikuchi RHB split +0.70, HR risk 0.41. park/weather net drag (-6%); limited recent HR events.""", blast="good"),
            row("Cole Young", "L", "+870", 74, "💎", ["vs Kikuchi"], """Worst Pickz Hidden Gem. 0 HR, 3 near-HR, 92.6 mph EV, 25.0% barrels. Kikuchi LHB split -0.52, HR risk 0.41. tough split lane (-0.52); park/weather net drag (-6%).""", blast="good", contact={'stars': 3, 'k': 20.8, 'batterK': 15.8, 'batterWhiff': 21.8, 'pitcherK': 23.8}),
        ],
    },
    {
        "title": "SF @ STL - Anthony Molina (R, SF) vs Matthew Liberatore 🧤 (L, STL)",
        "kLines": {'Molina': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 21.0, 'matchupK': 21.4, 'ownK': 20.2}, 'Liberatore': {'k': 5.4, 'lo': 4, 'hi': 7, 'bf': 21.7, 'matchupK': 24.9, 'ownK': 26.9}},
        "description": "Tail key data: Park boost -15% (stadium -10%, weather -5%). Molina (HR risk 0.52, vs LHB +0.89, vs RHB +0.07). Liberatore 🧤 (HR risk 1.26, vs LHB +0.12, vs RHB +1.46).",
        "rows": [
            row("Alec Burleson", "L", "+500", 73, "⭐", ["vs Molina"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 91.0 mph EV, 12.5% barrels. Molina LHB split +0.89, HR risk 0.52. park/weather net drag (-15%); limited recent HR events.""", contact={'stars': 3, 'k': 20.7, 'batterK': 20.2, 'batterWhiff': 23.4, 'pitcherK': 20.2}),
            row("Leonardo Bernal", "S", "+600", 84, "🌕 💣 💎", ["vs Molina"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 99.3 mph EV, 37.5% barrels. Molina SHB→LHB split +0.89, HR risk 0.52. park/weather net drag (-15%).""", blast="high", contact={'stars': 4, 'k': 19.8, 'batterK': 16.7, 'batterWhiff': 20.8, 'pitcherK': 20.2}),
            row("Jordan Walker", "R", "+425", 72, "", ["vs Molina"], """0 HR, 96.2 mph EV. Molina RHB split +0.07, HR risk 0.52. park/weather net drag (-15%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 27.0, 'batterK': 34.6, 'batterWhiff': 38.4, 'pitcherK': 20.2}),
            row("Thomas Saggese", "R", "+800", 65, "", ["vs Molina"], """0 HR, 95.8 mph EV. Molina RHB split +0.07, HR risk 0.52. park/weather net drag (-15%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.0, 'batterK': 17.1, 'batterWhiff': 22.2, 'pitcherK': 20.2}),
            row("Joshua Baez", "R", "+630", 72, "", ["vs Molina"], """0 HR, 1 near-HR, 97.0 mph EV. Molina RHB split +0.07, HR risk 0.52. park/weather net drag (-15%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 26.2, 'batterK': 32.4, 'batterWhiff': 38.0, 'pitcherK': 20.2}),
            row("Bryce Eldridge", "L", "+520", 90, "🌕 💣 💎", ["vs Liberatore"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.0 mph EV, 12.5% barrels. Liberatore LHB split +0.12, HR risk 1.26. park/weather net drag (-15%).""", blast="good", contact={'stars': 2, 'k': 26.8, 'batterK': 27.5, 'batterWhiff': 27.5, 'pitcherK': 26.9}),
            row("Shay Whitcomb", "R", "+630", 62, "", ["vs Liberatore"], """0 HR, 1 near-HR, 84.9 mph EV. Liberatore RHB split +1.46, HR risk 1.26. park/weather net drag (-15%); limited recent HR events.""", contact={'stars': 3, 'k': 23.2, 'batterK': 21.0, 'batterWhiff': 19.8, 'pitcherK': 26.9}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-16")

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

    out = ROOT / '_games-0916.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
