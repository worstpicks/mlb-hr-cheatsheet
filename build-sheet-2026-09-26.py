#!/usr/bin/env python3
"""Generate games[] block for 2026-09-26 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Cam Smith (R)",
    "Fernando Tatis Jr. (R)",
    "Jac Caglianone (L)",
    "Jackson Chourio (R)",
    "Jordan Walker (R)",
    "Lars Nootbaar (L)",
    "Munetaka Murakami (L)",
    "Randal Grichuk (R)",
    "Vinnie Pasquantino (L)",
}

GEMS = {
    "Dominic Canzone (L)",
    "Isaac Paredes (R)",
    "JJ Wetherholt (L)",
    "Ketel Marte (S)",
    "Pavin Smith (L)",
    "Salvador Perez (R)",
    "Yordan Alvarez (L)",
    "Zach Neto (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Austin Hays (R)": "SD",
    "Bobby Witt Jr. (R)": "KC",
    "Brenton Doyle (R)": "CWS",
    "Bryan De La Cruz (R)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Cam Smith (R)": "HOU",
    "Carter Jensen (L)": "KC",
    "Dominic Canzone (L)": "SEA",
    "Fernando Tatis Jr. (R)": "SD",
    "Gabriel Moreno (R)": "ARI",
    "Henry Bolte (R)": "ATH",
    "Isaac Paredes (R)": "HOU",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake Bauers (L)": "MIL",
    "Jeff McNeil (L)": "ATH",
    "Jo Adell (R)": "CLE",
    "Jordan Walker (R)": "STL",
    "Junior Caminero (R)": "TB",
    "Ketel Marte (S)": "ARI",
    "Lars Nootbaar (L)": "ARI",
    "Lazaro Montes (L)": "SEA",
    "Lucas Spence (L)": "HOU",
    "Mickey Moniak (L)": "COL",
    "Mike Trout (R)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Pavin Smith (L)": "ARI",
    "Randal Grichuk (R)": "CWS",
    "Randy Arozarena (R)": "SEA",
    "Salvador Perez (R)": "KC",
    "Vinnie Pasquantino (L)": "KC",
    "William Contreras (R)": "MIL",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
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
        "title": "ARI @ SD - Ryne Nelson (R, ARI) vs Walker Buehler (R, SD)",
        "kLines": {'Nelson': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 23.1, 'matchupK': 16.1, 'ownK': 14.4}, 'Buehler': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 20.6, 'matchupK': 17.8, 'ownK': 18.6}},
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Nelson (BAA vs LHB .227, vs RHB .269, HR/9 1.88). Buehler (HR risk 0.80, vs LHB +0.62, vs RHB +0.39).",
        "rows": [
            row("Fernando Tatis Jr.", "R", "+350", 92, "⭐ 🌕 💣", ["vs Nelson"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 92.7 mph EV, 50.0% barrels. limited split/risk sample.""", blast="high", contact={'stars': 5, 'k': 16.4, 'batterK': 17.8, 'batterWhiff': 20.3, 'pitcherK': 14.4}),
            row("Austin Hays", "R", "N/A", 55, "", ["vs Nelson"], """0 HR, 91.0 mph EV. limited split/risk sample; limited recent HR events.""", contact={'stars': 3, 'k': 20.2, 'batterK': 24.4, 'batterWhiff': 35.2, 'pitcherK': 14.4}),
            row("Gabriel Moreno", "R", "+820", 85, "", ["vs Buehler"], """1 HR, 1 near-HR, 96.1 mph EV, 12.5% barrels. Buehler RHB split +0.39, HR risk 0.80.""", blast="good", contact={'stars': 5, 'k': 16.1, 'batterK': 11.4, 'batterWhiff': 16.8, 'pitcherK': 18.6}),
            row("Pavin Smith", "L", "+820", 89, "🌕 💣 💎", ["vs Buehler"], """Worst Pickz Hidden Gem. 2 HR, 4 near-HR, 98.9 mph EV, 25.0% barrels. Buehler LHB split +0.62, HR risk 0.80.""", blast="high", contact={'stars': 4, 'k': 19.0, 'batterK': 19.7, 'batterWhiff': 19.8, 'pitcherK': 18.6}),
            row("Lars Nootbaar", "L", "+610", 84, "⭐", ["vs Buehler"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.7 mph EV, 25.0% barrels. Buehler LHB split +0.62, HR risk 0.80.""", blast="good", contact={'stars': 4, 'k': 19.6, 'batterK': 22.5, 'batterWhiff': 20.5, 'pitcherK': 18.6}),
            row("Ketel Marte", "S", "+454", 78, "💎", ["vs Buehler"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 97.6 mph EV, 12.5% barrels. Buehler SHB→LHB split +0.62, HR risk 0.80. limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 14.7, 'batterK': 8.7, 'batterWhiff': 13.7, 'pitcherK': 18.6}),
        ],
    },
    {
        "title": "CLE @ KC - Tanner Bibee (R, CLE) vs Michael Wacha (R, KC)",
        "kLines": {'Bibee': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 23.3, 'matchupK': 18.5, 'ownK': 18.4}, 'Wacha': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 24.8, 'matchupK': 18.7, 'ownK': 20.2}},
        "description": "Tail key data: Park boost +17% (stadium +12%, weather +4%). Bibee (HR risk 0.05, vs LHB +0.24, vs RHB -0.10). Wacha (HR risk 0.11, vs LHB -0.43, vs RHB +0.50).",
        "rows": [
            row("Carter Jensen", "L", "+375", 93, "🌕 💣", ["vs Bibee"], """3 HR, 3 near-HR, 91.4 mph EV, 25.0% barrels. Bibee LHB split +0.24, HR risk 0.05.""", blast="high", contact={'stars': 3, 'k': 22.6, 'batterK': 26.7, 'batterWhiff': 32.5, 'pitcherK': 18.4}),
            row("Salvador Perez", "R", "+550", 81, "💎", ["vs Bibee"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.0 mph EV, 25.0% barrels. Bibee RHB split -0.10, HR risk 0.05. slight split headwind (-0.10).""", blast="good", contact={'stars': 4, 'k': 18.5, 'batterK': 15.8, 'batterWhiff': 23.4, 'pitcherK': 18.4}),
            row("Vinnie Pasquantino", "L", "+524", 79, "⭐", ["vs Bibee"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.2 mph EV, 12.5% barrels. Bibee LHB split +0.24, HR risk 0.05.""", blast="good", contact={'stars': 5, 'k': 15.4, 'batterK': 12.3, 'batterWhiff': 11.4, 'pitcherK': 18.4}),
            row("Bobby Witt Jr.", "R", "+500", 79, "", ["vs Bibee"], """0 HR, 93.7 mph EV, 12.5% barrels. Bibee RHB split -0.10, HR risk 0.05. slight split headwind (-0.10); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.7, 'batterK': 17.0, 'batterWhiff': 24.6, 'pitcherK': 18.4}),
            row("Jac Caglianone", "L", "+425", 85, "⭐", ["vs Bibee"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 99.2 mph EV, 12.5% barrels. Bibee LHB split +0.24, HR risk 0.05. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 22.0, 'batterK': 26.3, 'batterWhiff': 30.1, 'pitcherK': 18.4}),
            row("Jo Adell", "R", "+479", 61, "", ["vs Wacha"], """0 HR, 90.5 mph EV. Wacha RHB split +0.50, HR risk 0.11. limited recent HR events.""", contact={'stars': 3, 'k': 22.7, 'batterK': 25.9, 'batterWhiff': 28.7, 'pitcherK': 20.2}),
        ],
    },
    {
        "title": "COL @ CWS - Jose Quintana (L, COL) vs Davis Martin (R, CWS)",
        "kLines": {'Quintana': {'k': 3.2, 'lo': 2, 'hi': 5, 'bf': 20.6, 'matchupK': 15.4, 'ownK': 11.1}, 'Martin': {'k': 3.5, 'lo': 2, 'hi': 5, 'bf': 21.8, 'matchupK': 16.2, 'ownK': 15.0}},
        "description": "Tail key data: Park boost -22% (stadium -5%, weather -17%). Quintana (HR risk 0.23, vs LHB +0.96, vs RHB -0.07). Martin (HR risk 0.13, vs LHB -0.13, vs RHB +0.22).",
        "rows": [
            row("Munetaka Murakami", "L", "+340", 85, "⭐", ["vs Quintana"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.9 mph EV, 12.5% barrels. Quintana LHB split +0.96, HR risk 0.23. park/weather net drag (-22%).""", blast="good", contact={'stars': 2, 'k': 24.1, 'batterK': 42.9, 'batterWhiff': 41.8, 'pitcherK': 11.1}),
            row("Randal Grichuk", "R", "+420", 73, "⭐", ["vs Quintana"], """Worst Pickz Favorite. 0 HR, 96.7 mph EV, 12.5% barrels. Quintana RHB split -0.07, HR risk 0.23. slight split headwind (-0.07); park/weather net drag (-22%).""", blast="good", contact={'stars': 5, 'k': 15.6, 'batterK': 18.0, 'batterWhiff': 20.9, 'pitcherK': 11.1}),
            row("Brenton Doyle", "R", "+740", 84, "🌕 💣", ["vs Quintana"], """2 HR, 3 near-HR, 99.1 mph EV, 25.0% barrels. Quintana RHB split -0.07, HR risk 0.23. slight split headwind (-0.07); park/weather net drag (-22%).""", blast="high", contact={'stars': 3, 'k': 21.0, 'batterK': 43.9, 'batterWhiff': 41.3, 'pitcherK': 11.1}),
            row("Mickey Moniak", "L", "+540", 72, "", ["vs Martin"], """1 HR, 1 near-HR, 95.7 mph EV, 12.5% barrels. Martin LHB split -0.13, HR risk 0.13. slight split headwind (-0.13); park/weather net drag (-22%).""", blast="good", contact={'stars': 3, 'k': 22.4, 'batterK': 32.8, 'batterWhiff': 35.3, 'pitcherK': 15.0}),
        ],
    },
    {
        "title": "HOU @ ATH - Hayden Wesneski (R, HOU) vs Jack Perkins (R, ATH)",
        "kLines": {'Wesneski': {'k': 4.3, 'lo': 3, 'hi': 6, 'bf': 21.8, 'matchupK': 19.6, 'ownK': 18.7}, 'Perkins': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 21.6, 'matchupK': 24.0, 'ownK': 23.9}},
        "description": "Tail key data: Park boost +22% (stadium +29%, weather -7%). Wesneski (HR risk -0.50, vs LHB -0.39, vs RHB -0.41). Perkins (HR risk 0.08, vs LHB -0.03, vs RHB +0.20).",
        "rows": [
            row("Henry Bolte", "R", "+680", 76, "🌕 💣", ["vs Wesneski"], """0 HR, 1 near-HR, 97.4 mph EV, 25.0% barrels. Wesneski RHB split -0.41, HR risk -0.50. tough split lane (-0.41); pitcher suppresses HR (-0.50).""", blast="high", contact={'stars': 3, 'k': 23.5, 'batterK': 31.5, 'batterWhiff': 28.4, 'pitcherK': 18.7}),
            row("Jeff McNeil", "L", "+760", 56, "", ["vs Wesneski"], """1 HR, 1 near-HR, 87.0 mph EV. Wesneski LHB split -0.39, HR risk -0.50. slight split headwind (-0.39); pitcher suppresses HR (-0.50).""", blast="good", contact={'stars': 5, 'k': 16.8, 'batterK': 13.6, 'batterWhiff': 16.7, 'pitcherK': 18.7}),
            row("Cam Smith", "R", "+490", 90, "⭐ 🌕 💣", ["vs Perkins"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 92.1 mph EV, 37.5% barrels. Perkins RHB split +0.20, HR risk 0.08. weather carry headwind (-7%).""", blast="high", contact={'stars': 2, 'k': 27.1, 'batterK': 35.2, 'batterWhiff': 31.1, 'pitcherK': 23.9}),
            row("Isaac Paredes", "R", "+470", 81, "🌕 💣 💎", ["vs Perkins"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 91.2 mph EV, 12.5% barrels. Perkins RHB split +0.20, HR risk 0.08. weather carry headwind (-7%).""", blast="high", contact={'stars': 4, 'k': 19.2, 'batterK': 16.5, 'batterWhiff': 13.1, 'pitcherK': 23.9}),
            row("Lucas Spence", "L", "+875", 90, "🌕 💣", ["vs Perkins"], """3 HR, 3 near-HR, 89.3 mph EV, 25.0% barrels. Perkins LHB split -0.03, HR risk 0.08. slight split headwind (-0.03); weather carry headwind (-7%).""", blast="high", contact={'stars': 1, 'k': 28.2, 'batterK': 35.8, 'batterWhiff': 40.4, 'pitcherK': 23.9}),
            row("Nelson Velazquez", "R", "N/A", 79, "", ["vs Perkins"], """0 HR, 1 near-HR, 97.0 mph EV, 12.5% barrels. Perkins RHB split +0.20, HR risk 0.08. weather carry headwind (-7%); limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 28.0, 'batterK': 44.1, 'batterWhiff': 43.8, 'pitcherK': 23.9}),
            row("Yordan Alvarez", "L", "+250", 81, "💎", ["vs Perkins"], """Worst Pickz Hidden Gem. 0 HR, 94.7 mph EV. Perkins LHB split -0.03, HR risk 0.08. slight split headwind (-0.03); weather carry headwind (-7%).""", blast="good", contact={'stars': 3, 'k': 20.6, 'batterK': 16.5, 'batterWhiff': 20.4, 'pitcherK': 23.9}),
        ],
    },
    {
        "title": "LAA @ SEA - Ryan Johnson (R, LAA) vs Kade Anderson (L, SEA)",
        "kLines": {'Johnson': {'k': 4.2, 'lo': 3, 'hi': 6, 'bf': 21.4, 'matchupK': 19.6, 'ownK': 19.0}, 'Anderson': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 21.8, 'matchupK': 24.3, 'ownK': 21.4}},
        "description": "Tail key data: Park boost -10% (stadium +0%, weather -11%). Johnson (HR risk 0.13, vs LHB +0.45, vs RHB -0.10). Anderson (HR risk -0.20, vs LHB -0.37, vs RHB -0.08).",
        "rows": [
            row("Dominic Canzone", "L", "+428", 74, "💎", ["vs Johnson"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 90.2 mph EV, 25.0% barrels. Johnson LHB split +0.45, HR risk 0.13. park/weather net drag (-10%).""", blast="good", contact={'stars': 4, 'k': 18.8, 'batterK': 16.9, 'batterWhiff': 23.4, 'pitcherK': 19.0}),
            row("Randy Arozarena", "R", "+537", 74, "", ["vs Johnson"], """0 HR, 1 near-HR, 98.5 mph EV, 12.5% barrels. Johnson RHB split -0.10, HR risk 0.13. slight split headwind (-0.10); park/weather net drag (-10%).""", blast="good", contact={'stars': 3, 'k': 20.1, 'batterK': 21.1, 'batterWhiff': 24.3, 'pitcherK': 19.0}),
            row("Lazaro Montes", "L", "+680", 72, "", ["vs Johnson"], """1 HR, 1 near-HR, 88.2 mph EV, 12.5% barrels. Johnson LHB split +0.45, HR risk 0.13. park/weather net drag (-10%).""", blast="good", contact={'stars': 1, 'k': 27.5, 'batterK': 43.6, 'batterWhiff': 46.0, 'pitcherK': 19.0}),
            row("Mike Trout", "R", "+500", 79, "", ["vs Anderson"], """1 HR, 1 near-HR, 92.8 mph EV, 37.5% barrels. Anderson RHB split -0.08, HR risk -0.20. slight split headwind (-0.08); pitcher risk below avg (-0.20).""", blast="good", contact={'stars': 2, 'k': 25.0, 'batterK': 27.0, 'batterWhiff': 35.0, 'pitcherK': 21.4}),
            row("Zach Neto", "R", "+450", 69, "💎", ["vs Anderson"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.9 mph EV. Anderson RHB split -0.08, HR risk -0.20. slight split headwind (-0.08); pitcher risk below avg (-0.20).""", blast="good", contact={'stars': 2, 'k': 24.8, 'batterK': 29.7, 'batterWhiff': 29.0, 'pitcherK': 21.4}),
        ],
    },
    {
        "title": "STL @ MIL - Quinn Mathews (L, STL) vs Dustin May (R, MIL)",
        "kLines": {'Mathews': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 22.9, 'matchupK': 22.0, 'ownK': 20.5}, 'May': {'k': 4.6, 'lo': 3, 'hi': 6, 'bf': 20.5, 'matchupK': 22.6, 'ownK': 21.6}},
        "description": "Tail key data: Park boost -18% (stadium -1%, weather -17%). Mathews (HR risk -0.78, vs LHB +0.80, vs RHB -0.95). May (HR risk 0.41, vs LHB +0.33, vs RHB +0.18).",
        "rows": [
            row("Jackson Chourio", "R", "+441", 77, "⭐ 🌕 💣", ["vs Mathews"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.8 mph EV, 25.0% barrels. Mathews RHB split -0.95, HR risk -0.78. tough split lane (-0.95); pitcher suppresses HR (-0.78).""", blast="high", contact={'stars': 3, 'k': 22.7, 'batterK': 24.7, 'batterWhiff': 28.5, 'pitcherK': 20.5}),
            row("William Contreras", "R", "+590", 45, "", ["vs Mathews"], """0 HR, 90.2 mph EV, 12.5% barrels. Mathews RHB split -0.95, HR risk -0.78. tough split lane (-0.95); pitcher suppresses HR (-0.78).""", contact={'stars': 3, 'k': 20.6, 'batterK': 20.0, 'batterWhiff': 24.1, 'pitcherK': 20.5}),
            row("Jake Bauers", "L", "+470", 79, "🌕 💣", ["vs Mathews"], """2 HR, 3 near-HR, 90.6 mph EV, 25.0% barrels. Mathews LHB split +0.80, HR risk -0.78. pitcher suppresses HR (-0.78); park/weather net drag (-18%).""", blast="high", contact={'stars': 2, 'k': 26.7, 'batterK': 32.5, 'batterWhiff': 39.9, 'pitcherK': 20.5}),
            row("Alec Burleson", "L", "+630", 89, "⭐ 🌕 💣", ["vs May"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.9 mph EV, 25.0% barrels. May LHB split +0.33, HR risk 0.41. park/weather net drag (-18%).""", blast="high", contact={'stars': 3, 'k': 23.2, 'batterK': 26.9, 'batterWhiff': 25.9, 'pitcherK': 21.6}),
            row("Jordan Walker", "R", "+490", 85, "⭐ 🌕 💣", ["vs May"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.3 mph EV, 25.0% barrels. May RHB split +0.18, HR risk 0.41. park/weather net drag (-18%).""", blast="high", contact={'stars': 1, 'k': 28.4, 'batterK': 36.4, 'batterWhiff': 41.0, 'pitcherK': 21.6}),
            row("JJ Wetherholt", "L", "+920", 75, "💎", ["vs May"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.8 mph EV, 12.5% barrels. May LHB split +0.33, HR risk 0.41. park/weather net drag (-18%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 23.8, 'batterWhiff': 19.3, 'pitcherK': 21.6}),
        ],
    },
    {
        "title": "TB @ PHI - Griffin Jax (R, TB) vs Aaron Nola (R, PHI)",
        "kLines": {'Jax': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 19.1, 'matchupK': 26.0, 'ownK': 28.4}, 'Nola': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 22.8, 'matchupK': 22.9, 'ownK': 25.5}},
        "description": "Tail key data: Park boost -8% (stadium +15%, weather -24%). Jax (HR risk -0.27, vs LHB +0.23, vs RHB -0.61). Nola (BAA vs LHB .248, vs RHB .272, HR/9 1.86).",
        "rows": [
            row("Bryan De La Cruz", "R", "N/A", 50, "", ["vs Jax"], """0 HR, 91.9 mph EV, 12.5% barrels. Jax RHB split -0.61, HR risk -0.27. tough split lane (-0.61); pitcher risk below avg (-0.27).""", contact={'stars': 3, 'k': 23.9, 'batterK': 18.8, 'batterWhiff': 20.4, 'pitcherK': 28.4}),
            row("Bryson Stott", "L", "N/A", 53, "", ["vs Jax"], """0 HR, 91.2 mph EV, 12.5% barrels. Jax LHB split +0.23, HR risk -0.27. pitcher risk below avg (-0.27); park/weather net drag (-8%).""", contact={'stars': 3, 'k': 22.0, 'batterK': 14.3, 'batterWhiff': 19.1, 'pitcherK': 28.4}),
            row("Junior Caminero", "R", "+360", 68, "", ["vs Nola"], """0 HR, 94.7 mph EV. limited split/risk sample; park/weather net drag (-8%).""", blast="good", contact={'stars': 3, 'k': 21.9, 'batterK': 17.4, 'batterWhiff': 21.3, 'pitcherK': 25.5}),
            row("Yandy Diaz", "R", "+610", 59, "", ["vs Nola"], """0 HR, 90.9 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-8%).""", contact={'stars': 4, 'k': 19.5, 'batterK': 13.3, 'batterWhiff': 15.8, 'pitcherK': 25.5}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-26")

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

    out = ROOT / '_games-0926.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
