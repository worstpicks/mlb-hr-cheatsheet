#!/usr/bin/env python3
"""Generate games[] block for 2026-09-10 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Bryan Reynolds (S)",
    "Cal Raleigh (S)",
    "Esmerlyn Valdez (R)",
    "Kyle Schwarber (L)",
    "Matt Olson (L)",
    "Munetaka Murakami (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Austin Riley (R)",
    "Bryson Stott (L)",
    "Junior Caminero (R)",
    "Ronald Acuna Jr. (R)",
    "Tristan Peters (L)",
}

PLAYER_TEAMS = {
    "Aaron Judge (R)": "NYY",
    "Adael Amador (S)": "COL",
    "Andrew Benintendi (L)": "CWS",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Brett Sullivan (L)": "COL",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Cam Smith (R)": "HOU",
    "Corey Seager (L)": "TEX",
    "Danny Jansen (R)": "TEX",
    "Derek Hill (R)": "PHI",
    "Dominic Canzone (L)": "SEA",
    "Esmerlyn Valdez (R)": "PIT",
    "Hunter Goodman (R)": "COL",
    "Isaac Paredes (R)": "HOU",
    "J.P Crawford (L)": "SEA",
    "Jacob Gonzalez (L)": "PIT",
    "Jake McCarthy (L)": "COL",
    "Jasson Dominguez (S)": "NYY",
    "Jonathan Aranda (L)": "TB",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kyle Schwarber (L)": "PHI",
    "LaMonte Wade Jr. (L)": "HOU",
    "Lazaro Montes (L)": "SEA",
    "Luis Garcia Jr. (L)": "NYY",
    "Matt Olson (L)": "ATL",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Oneil Cruz (L)": "PIT",
    "Ozzie Albies (S)": "ATL",
    "Rafael Flores (R)": "PIT",
    "Randal Grichuk (R)": "CWS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Ryan Vilade (R)": "TB",
    "Spencer Jones (L)": "NYY",
    "Trea Turner (R)": "PHI",
    "Tristan Peters (L)": "CWS",
    "Victor Mesa Jr. (L)": "TB",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("TEX @ SEA", "Gilbert"),
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
        "title": "COL @ NYY - Ryan Feltner (R, COL) vs Max Fried (L, NYY)",
        "kLines": {'Feltner': {'k': 4.0, 'lo': 2, 'hi': 6, 'bf': 21.9, 'matchupK': 18.3, 'ownK': 15.7}, 'Fried': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 21.7, 'matchupK': 24.4, 'ownK': 26.2}},
        "description": "Tail key data: Park boost +22% (stadium +5%, weather +17%). Feltner (HR risk -0.17, vs LHB -0.21, vs RHB -0.15). Fried (HR risk -1.16, vs LHB -1.46, vs RHB -0.65).",
        "rows": [
            row("Spencer Jones", "L", "+300", 90, "🌕 💣", ["vs Feltner"], """2 HR, 2 near-HR, 96.1 mph EV, 37.5% barrels. Feltner LHB split -0.21, HR risk -0.17. slight split headwind (-0.21); pitcher risk below avg (-0.17).""", blast="high", contact={'stars': 3, 'k': 23.6, 'batterK': 34.7, 'batterWhiff': 37.4, 'pitcherK': 15.7}),
            row("Ben Rice", "L", "+255", 86, "", ["vs Feltner"], """1 HR, 1 near-HR, 94.0 mph EV, 12.5% barrels. Feltner LHB split -0.21, HR risk -0.17. slight split headwind (-0.21); pitcher risk below avg (-0.17).""", blast="good", contact={'stars': 4, 'k': 19.3, 'batterK': 22.2, 'batterWhiff': 27.0, 'pitcherK': 15.7}),
            row("Aaron Judge", "R", "+190", 81, "", ["vs Feltner"], """0 HR, 1 near-HR, 94.2 mph EV, 12.5% barrels. Feltner RHB split -0.15, HR risk -0.17. slight split headwind (-0.15); pitcher risk below avg (-0.17).""", blast="good", contact={'stars': 3, 'k': 20.3, 'batterK': 25.3, 'batterWhiff': 28.7, 'pitcherK': 15.7}),
            row("Luis Garcia Jr.", "L", "+332", 77, "", ["vs Feltner"], """0 HR, 92.5 mph EV, 12.5% barrels. Feltner LHB split -0.21, HR risk -0.17. slight split headwind (-0.21); pitcher risk below avg (-0.17).""", blast="good", contact={'stars': 4, 'k': 19.8, 'batterK': 24.3, 'batterWhiff': 27.5, 'pitcherK': 15.7}),
            row("Jasson Dominguez", "S", "N/A", 68, "", ["vs Feltner"], """0 HR, 97.7 mph EV, 12.5% barrels. Feltner SHB→LHB split -0.21, HR risk -0.17. slight split headwind (-0.21); pitcher risk below avg (-0.17).""", blast="good", contact={'stars': 4, 'k': 18.3, 'batterK': 23.4, 'batterWhiff': 20.0, 'pitcherK': 15.7}),
            row("Adael Amador", "S", "+980", 63, "", ["vs Fried"], """0 HR, 2 near-HR, 93.4 mph EV, 14.3% barrels. Fried SHB→RHB split -0.65, HR risk -1.16. tough split lane (-0.65); pitcher suppresses HR (-1.16).""", blast="good", contact={'stars': 3, 'k': 21.4, 'batterK': 16.2, 'batterWhiff': 13.4, 'pitcherK': 26.2}),
            row("Hunter Goodman", "R", "+353", 67, "", ["vs Fried"], """1 HR, 1 near-HR, 92.1 mph EV. Fried RHB split -0.65, HR risk -1.16. tough split lane (-0.65); pitcher suppresses HR (-1.16).""", blast="good", contact={'stars': 2, 'k': 26.2, 'batterK': 25.0, 'batterWhiff': 31.1, 'pitcherK': 26.2}),
            row("Brett Sullivan", "L", "N/A", 46, "", ["vs Fried"], """0 HR, 1 near-HR, 86.5 mph EV, 12.5% barrels. Fried LHB split -1.46, HR risk -1.16. tough split lane (-1.46); pitcher suppresses HR (-1.16).""", contact={'stars': 3, 'k': 21.8, 'batterK': 17.5, 'batterWhiff': 17.9, 'pitcherK': 26.2}),
            row("Jake McCarthy", "L", "+1060", 44, "", ["vs Fried"], """0 HR, 1 near-HR, 86.8 mph EV. Fried LHB split -1.46, HR risk -1.16. tough split lane (-1.46); pitcher suppresses HR (-1.16).""", contact={'stars': 4, 'k': 19.8, 'batterK': 13.8, 'batterWhiff': 16.5, 'pitcherK': 26.2}),
        ],
    },
    {
        "title": "HOU @ PHI - Cristian Javier (R, HOU) vs Zack Wheeler (R, PHI)",
        "kLines": {'Javier': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 19.8, 'matchupK': 23.1, 'ownK': 25.3}, 'Wheeler': {'k': 6.3, 'lo': 5, 'hi': 8, 'bf': 22.6, 'matchupK': 27.7, 'ownK': 30.4}},
        "description": "Tail key data: Park boost +28% (stadium +14%, weather +14%). Javier (HR risk 0.91, vs LHB -0.20, vs RHB +1.17). Wheeler (HR risk 0.54, vs LHB +1.01, vs RHB -0.13).",
        "rows": [
            row("Bryce Harper", "L", "+341", 91, "🌕 💣", ["vs Javier"], """1 HR, 1 near-HR, 92.5 mph EV, 12.5% barrels. Javier LHB split -0.20, HR risk 0.91. slight split headwind (-0.20).""", blast="good", contact={'stars': 2, 'k': 25.6, 'batterK': 24.7, 'batterWhiff': 31.8, 'pitcherK': 25.3}),
            row("Bryson Stott", "L", "+517", 90, "🌕 💣 💎", ["vs Javier"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 95.8 mph EV, 25.0% barrels. Javier LHB split -0.20, HR risk 0.91. slight split headwind (-0.20).""", blast="good", contact={'stars': 3, 'k': 21.8, 'batterK': 18.2, 'batterWhiff': 21.4, 'pitcherK': 25.3}),
            row("Trea Turner", "R", "+502", 77, "", ["vs Javier"], """0 HR, 2 near-HR, 91.6 mph EV. Javier RHB split +1.17, HR risk 0.91.""", blast="good", contact={'stars': 2, 'k': 24.3, 'batterK': 21.1, 'batterWhiff': 30.8, 'pitcherK': 25.3}),
            row("Kyle Schwarber", "L", "+194", 93, "⭐ 🌕 💣", ["vs Javier"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.7 mph EV, 25.0% barrels. Javier LHB split -0.20, HR risk 0.91. slight split headwind (-0.20).""", blast="high", contact={'stars': 2, 'k': 24.7, 'batterK': 22.8, 'batterWhiff': 30.2, 'pitcherK': 25.3}),
            row("Derek Hill", "R", "N/A", 87, "", ["vs Javier"], """1 HR, 1 near-HR, 87.6 mph EV, 12.5% barrels. Javier RHB split +1.17, HR risk 0.91. lighter EV form (87.6 mph).""", blast="good", contact={'stars': 2, 'k': 24.8, 'batterK': 24.2, 'batterWhiff': 30.6, 'pitcherK': 25.3}),
            row("Brandon Marsh", "L", "+540", 81, "", ["vs Javier"], """0 HR, 1 near-HR, 94.1 mph EV, 12.5% barrels. Javier LHB split -0.20, HR risk 0.91. slight split headwind (-0.20); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.5, 'batterK': 20.4, 'batterWhiff': 21.4, 'pitcherK': 25.3}),
            row("Yordan Alvarez", "L", "+235", 93, "⭐ 🌕 💣", ["vs Wheeler"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.7 mph EV, 25.0% barrels. Wheeler LHB split +1.01, HR risk 0.54.""", blast="good", contact={'stars': 3, 'k': 23.2, 'batterK': 18.6, 'batterWhiff': 15.4, 'pitcherK': 30.4}),
            row("Cam Smith", "R", "+820", 86, "", ["vs Wheeler"], """1 HR, 2 near-HR, 93.5 mph EV, 25.0% barrels. Wheeler RHB split -0.13, HR risk 0.54. slight split headwind (-0.13).""", blast="good", contact={'stars': 1, 'k': 29.3, 'batterK': 30.2, 'batterWhiff': 30.9, 'pitcherK': 30.4}),
            row("Isaac Paredes", "R", "+680", 64, "", ["vs Wheeler"], """0 HR, 90.9 mph EV. Wheeler RHB split -0.13, HR risk 0.54. slight split headwind (-0.13); limited recent HR events.""", contact={'stars': 3, 'k': 20.2, 'batterK': 10.5, 'batterWhiff': 13.3, 'pitcherK': 30.4}),
            row("Nelson Velazquez", "R", "N/A", 84, "", ["vs Wheeler"], """0 HR, 1 near-HR, 96.2 mph EV, 12.5% barrels. Wheeler RHB split -0.13, HR risk 0.54. slight split headwind (-0.13); limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 33.0, 'batterK': 43.2, 'batterWhiff': 48.5, 'pitcherK': 30.4}),
            row("LaMonte Wade Jr.", "L", "+502", 84, "", ["vs Wheeler"], """1 HR, 1 near-HR, 93.3 mph EV, 12.5% barrels. Wheeler LHB split +1.01, HR risk 0.54.""", blast="good", contact={'stars': 1, 'k': 28.8, 'batterK': 37.5, 'batterWhiff': 29.9, 'pitcherK': 30.4}),
        ],
    },
    {
        "title": "PIT @ CWS - Jared Jones (R, PIT) vs Hagen Smith (L, CWS)",
        "kLines": {'Jones': {'k': 5.7, 'lo': 4, 'hi': 7, 'bf': 20.1, 'matchupK': 28.3, 'ownK': 29.5}, 'Smith': {'k': 6.5, 'lo': 5, 'hi': 8, 'bf': 21.7, 'matchupK': 30.1, 'ownK': 37.1}},
        "description": "Tail key data: Park boost -12% (stadium -5%, weather -7%). Jones (HR risk 0.47, vs LHB +0.79, vs RHB -0.05). Smith (HR risk -1.38, vs LHB -0.18, vs RHB -1.23).",
        "rows": [
            row("Munetaka Murakami", "L", "+315", 87, "⭐", ["vs Jones"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.3 mph EV, 12.5% barrels. Jones LHB split +0.79, HR risk 0.47. park/weather net drag (-12%).""", blast="good", contact={'stars': 1, 'k': 35.8, 'batterK': 42.7, 'batterWhiff': 42.1, 'pitcherK': 29.5}),
            row("Tristan Peters", "L", "+800", 76, "💎", ["vs Jones"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.0 mph EV, 12.5% barrels. Jones LHB split +0.79, HR risk 0.47. park/weather net drag (-12%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.2, 'batterK': 15.3, 'batterWhiff': 24.6, 'pitcherK': 29.5}),
            row("Andrew Benintendi", "L", "+620", 82, "🌕 💣", ["vs Jones"], """0 HR, 99.5 mph EV, 25.0% barrels. Jones LHB split +0.79, HR risk 0.47. park/weather net drag (-12%); limited recent HR events.""", blast="high", contact={'stars': 2, 'k': 24.8, 'batterK': 19.7, 'batterWhiff': 22.6, 'pitcherK': 29.5}),
            row("Randal Grichuk", "R", "N/A", 74, "", ["vs Jones"], """1 HR, 1 near-HR, 91.7 mph EV. Jones RHB split -0.05, HR risk 0.47. slight split headwind (-0.05); park/weather net drag (-12%).""", blast="good", contact={'stars': 2, 'k': 24.9, 'batterK': 23.3, 'batterWhiff': 20.0, 'pitcherK': 29.5}),
            row("Esmerlyn Valdez", "R", "N/A", 83, "⭐ 🌕 💣", ["vs Smith"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 96.0 mph EV, 25.0% barrels. Smith RHB split -1.23, HR risk -1.38. tough split lane (-1.23); pitcher suppresses HR (-1.38).""", blast="high", contact={'stars': 1, 'k': 33.7, 'batterK': 39.3, 'batterWhiff': 38.7, 'pitcherK': 37.1}),
            row("Bryan Reynolds", "S", "+497", 57, "⭐", ["vs Smith"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 98.1 mph EV. Smith SHB→RHB split -1.23, HR risk -1.38. tough split lane (-1.23); pitcher suppresses HR (-1.38).""", blast="good", contact={'stars': 2, 'k': 24.5, 'batterK': 16.9, 'batterWhiff': 26.8, 'pitcherK': 37.1}),
            row("Oneil Cruz", "L", "+451", 55, "", ["vs Smith"], """0 HR, 1 near-HR, 90.5 mph EV, 12.5% barrels. Smith LHB split -0.18, HR risk -1.38. slight split headwind (-0.18); pitcher suppresses HR (-1.38).""", contact={'stars': 1, 'k': 30.9, 'batterK': 33.8, 'batterWhiff': 33.3, 'pitcherK': 37.1}),
            row("Rafael Flores", "R", "N/A", 59, "", ["vs Smith"], """1 HR, 1 near-HR, 93.4 mph EV, 12.5% barrels. Smith RHB split -1.23, HR risk -1.38. tough split lane (-1.23); pitcher suppresses HR (-1.38).""", blast="good", contact={'stars': 1, 'k': 28.8, 'batterK': 29.7, 'batterWhiff': 29.8, 'pitcherK': 37.1}),
            row("Jacob Gonzalez", "L", "+850", 49, "", ["vs Smith"], """0 HR, 93.7 mph EV, 12.5% barrels. Smith LHB split -0.18, HR risk -1.38. slight split headwind (-0.18); pitcher suppresses HR (-1.38).""", blast="good", contact={'stars': 3, 'k': 24.0, 'batterK': 18.5, 'batterWhiff': 19.0, 'pitcherK': 37.1}),
        ],
    },
    {
        "title": "TB @ ATL - Nick Martinez (R, TB) vs Martin Perez (L, ATL)",
        "kLines": {'Martinez': {'k': 3.9, 'lo': 2, 'hi': 6, 'bf': 23.4, 'matchupK': 16.7, 'ownK': 14.5}, 'Perez': {'k': 3.4, 'lo': 2, 'hi': 5, 'bf': 21.4, 'matchupK': 16.1, 'ownK': 15.9}},
        "description": "Tail key data: Park boost +1% (stadium -6%, weather +7%). Martinez (HR risk -0.07, vs LHB -0.50, vs RHB +0.20). Perez (HR risk -0.41, vs LHB +1.03, vs RHB -0.74).",
        "rows": [
            row("Ozzie Albies", "S", "+760", 54, "", ["vs Martinez"], """0 HR, 94.2 mph EV. Martinez SHB→LHB split -0.50, HR risk -0.07. tough split lane (-0.50); pitcher risk below avg (-0.07).""", blast="good", contact={'stars': 5, 'k': 16.1, 'batterK': 18.1, 'batterWhiff': 19.2, 'pitcherK': 14.5}),
            row("Ronald Acuna Jr.", "R", "+370", 62, "💎", ["vs Martinez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 88.2 mph EV. Martinez RHB split +0.20, HR risk -0.07. pitcher risk below avg (-0.07); park suppresses carry (-6%).""", blast="good"),
            row("Austin Riley", "R", "+525", 68, "💎", ["vs Martinez"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.3 mph EV, 12.5% barrels. Martinez RHB split +0.20, HR risk -0.07. pitcher risk below avg (-0.07); park suppresses carry (-6%).""", blast="good", contact={'stars': 3, 'k': 21.0, 'batterK': 35.1, 'batterWhiff': 28.7, 'pitcherK': 14.5}),
            row("Matt Olson", "L", "+320", 73, "⭐", ["vs Martinez"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 99.8 mph EV, 12.5% barrels. Martinez LHB split -0.50, HR risk -0.07. tough split lane (-0.50); pitcher risk below avg (-0.07).""", blast="good", contact={'stars': 3, 'k': 20.2, 'batterK': 27.7, 'batterWhiff': 31.6, 'pitcherK': 14.5}),
            row("Ryan Vilade", "R", "+880", 71, "🚀", ["vs Perez"], """0 HR, 103.0 mph EV, 12.5% barrels. Perez RHB split -0.74, HR risk -0.41. tough split lane (-0.74); pitcher suppresses HR (-0.41).""", blast="good", contact={'stars': 4, 'k': 19.5, 'batterK': 21.7, 'batterWhiff': 27.6, 'pitcherK': 15.9}),
            row("Junior Caminero", "R", "+352", 49, "💎", ["vs Perez"], """Worst Pickz Hidden Gem. 0 HR, 86.4 mph EV. Perez RHB split -0.74, HR risk -0.41. tough split lane (-0.74); pitcher suppresses HR (-0.41).""", contact={'stars': 4, 'k': 17.3, 'batterK': 17.0, 'batterWhiff': 22.7, 'pitcherK': 15.9}),
            row("Victor Mesa Jr.", "L", "+650", 50, "", ["vs Perez"], """0 HR, 81.9 mph EV. Perez LHB split +1.03, HR risk -0.41. pitcher suppresses HR (-0.41); park suppresses carry (-6%).""", contact={'stars': 5, 'k': 17.0, 'batterK': 11.0, 'batterWhiff': 25.8, 'pitcherK': 15.9}),
            row("Jonathan Aranda", "L", "+730", 52, "", ["vs Perez"], """0 HR, 87.6 mph EV. Perez LHB split +1.03, HR risk -0.41. pitcher suppresses HR (-0.41); park suppresses carry (-6%).""", contact={'stars': 3, 'k': 20.3, 'batterK': 27.1, 'batterWhiff': 25.4, 'pitcherK': 15.9}),
        ],
    },
    {
        "title": "TEX @ SEA - Jacob deGrom (R, TEX) vs Logan Gilbert 🧤 (R, SEA)",
        "kLines": {'deGrom': {'k': 6.0, 'lo': 4, 'hi': 8, 'bf': 21.6, 'matchupK': 27.7, 'ownK': 29.2}, 'Gilbert': {'k': 5.8, 'lo': 4, 'hi': 7, 'bf': 23.3, 'matchupK': 24.8, 'ownK': 25.6}},
        "description": "Tail key data: Park boost -1% (stadium +1%, weather -2%). deGrom (HR risk -0.02, vs LHB -0.06, vs RHB -0.11). Gilbert 🧤 (HR risk 1.29, vs LHB -0.22, vs RHB +1.67).",
        "rows": [
            row("Lazaro Montes", "L", "+630", 83, "🌕 💣", ["vs deGrom"], """2 HR, 2 near-HR, 96.4 mph EV, 66.7% barrels. deGrom LHB split -0.06, HR risk -0.02. slight split headwind (-0.06); pitcher risk below avg (-0.02).""", blast="high", contact={'stars': 1, 'k': 30.2, 'batterK': 45.0, 'batterWhiff': 51.1, 'pitcherK': 29.2}),
            row("Cal Raleigh", "S", "+323", 88, "⭐ 🌕 💣", ["vs deGrom"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.3 mph EV, 50.0% barrels. deGrom SHB→LHB split -0.06, HR risk -0.02. slight split headwind (-0.06); pitcher risk below avg (-0.02).""", blast="high", contact={'stars': 1, 'k': 27.6, 'batterK': 25.6, 'batterWhiff': 29.9, 'pitcherK': 29.2}),
            row("Dominic Canzone", "L", "+457", 74, "", ["vs deGrom"], """1 HR, 1 near-HR, 93.3 mph EV, 12.5% barrels. deGrom LHB split -0.06, HR risk -0.02. slight split headwind (-0.06); pitcher risk below avg (-0.02).""", blast="good", contact={'stars': 2, 'k': 25.9, 'batterK': 23.6, 'batterWhiff': 23.8, 'pitcherK': 29.2}),
            row("Julio Rodriguez", "R", "+500", 75, "🚀 🌕 💣", ["vs deGrom"], """0 HR, 102.3 mph EV, 25.0% barrels. deGrom RHB split -0.11, HR risk -0.02. slight split headwind (-0.11); pitcher risk below avg (-0.02).""", blast="high"),
            row("J.P Crawford", "L", "+910", 60, "", ["vs deGrom"], """0 HR, 94.5 mph EV. deGrom LHB split -0.06, HR risk -0.02. slight split headwind (-0.06); pitcher risk below avg (-0.02).""", blast="good", contact={'stars': 3, 'k': 22.8, 'batterK': 20.0, 'batterWhiff': 14.4, 'pitcherK': 29.2}),
            row("Corey Seager", "L", "+370", 94, "🌕 💣", ["vs Gilbert"], """2 HR, 2 near-HR, 92.3 mph EV, 25.0% barrels. Gilbert LHB split -0.22, HR risk 1.29. slight split headwind (-0.22).""", blast="high", contact={'stars': 2, 'k': 24.3, 'batterK': 19.3, 'batterWhiff': 31.3, 'pitcherK': 25.6}),
            row("Danny Jansen", "R", "+820", 91, "🌕 💣", ["vs Gilbert"], """2 HR, 2 near-HR, 90.4 mph EV, 25.0% barrels. Gilbert RHB split +1.67, HR risk 1.29.""", blast="high", contact={'stars': 2, 'k': 27.3, 'batterK': 31.7, 'batterWhiff': 32.5, 'pitcherK': 25.6}),
            row("Justin Foscue", "R", "N/A", 91, "🌕 💣", ["vs Gilbert"], """1 HR, 2 near-HR, 89.8 mph EV, 25.0% barrels. Gilbert RHB split +1.67, HR risk 1.29.""", blast="good", contact={'stars': 3, 'k': 21.3, 'batterK': 16.4, 'batterWhiff': 17.0, 'pitcherK': 25.6}),
            row("Brandon Nimmo", "L", "+540", 78, "", ["vs Gilbert"], """0 HR, 97.6 mph EV. Gilbert LHB split -0.22, HR risk 1.29. slight split headwind (-0.22); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.7, 'batterK': 21.8, 'batterWhiff': 23.9, 'pitcherK': 25.6}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-10")

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

    out = ROOT / '_games-0910.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
