#!/usr/bin/env python3
"""Generate games[] block for 2026-09-17 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Corey Seager (L)",
    "Jackson Merrill (L)",
    "Josh Bell (S)",
    "Junior Caminero (R)",
    "Kyle Schwarber (L)",
    "Vinnie Pasquantino (L)",
    "Wilyer Abreu (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Brandon Lowe (L)",
    "Brandon Marsh (L)",
    "Brandon Nimmo (L)",
    "Bryce Harper (L)",
    "Ethan Salas (L)",
    "Jahmai Jones (R)",
    "Jared Young (L)",
    "Joc Pederson (L)",
    "Jonathan Aranda (L)",
    "Juan Brito (S)",
    "Juan Soto (L)",
    "Manny Machado (R)",
    "Moises Ballesteros (L)",
    "Oneil Cruz (L)",
    "Randal Grichuk (R)",
    "Riley Greene (L)",
    "Royce Lewis (R)",
    "Ryan Vilade (R)",
    "Sal Stewart (R)",
    "Spencer Torkelson (R)",
    "Tyler Stephenson (R)",
    "Victor Mesa Jr. (L)",
    "Will Smith (R)",
    "Yandy Diaz (R)",
}

PLAYER_TEAMS = {
    "Alika Williams (R)": "ATH",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Vaughn (R)": "MIL",
    "Bo Bichette (R)": "NYM",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Brett Baty (L)": "NYM",
    "Brice Turang (L)": "MIL",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Harper (L)": "PHI",
    "Carson Benge (L)": "NYM",
    "Cole Carrigg (S)": "COL",
    "Colt Keith (L)": "DET",
    "Connor Norby (R)": "COL",
    "Cooper Pratt (R)": "MIL",
    "Corey Seager (L)": "TEX",
    "Danny Jansen (R)": "TEX",
    "Elly De La Cruz (S)": "CIN",
    "Emmanuel Rodriguez (L)": "MIN",
    "Ethan Salas (L)": "SD",
    "Evan Carter (L)": "TEX",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Gleyber Torres (R)": "DET",
    "Hunter Goodman (R)": "COL",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jahmai Jones (R)": "BOS",
    "Jared Young (L)": "NYM",
    "Jarren Duran (L)": "BOS",
    "Jeremy Pena (R)": "HOU",
    "Joc Pederson (L)": "TEX",
    "John Rave (L)": "KC",
    "Jonathan Aranda (L)": "TB",
    "Josh Bell (S)": "MIN",
    "Josh Lowe (L)": "LAA",
    "Juan Brito (S)": "CIN",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Kevin McGonigle (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Konnor Griffin (R)": "PIT",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Tucker (L)": "LAD",
    "Lawrence Butler (L)": "ATH",
    "Manny Machado (R)": "SD",
    "Matt McLain (R)": "CIN",
    "Moises Ballesteros (L)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Oneil Cruz (L)": "PIT",
    "Randal Grichuk (R)": "CWS",
    "Riley Greene (L)": "DET",
    "Royce Lewis (R)": "MIN",
    "Ryan Vilade (R)": "TB",
    "Sal Stewart (R)": "CIN",
    "Spencer Torkelson (R)": "DET",
    "Teoscar Hernandez (R)": "LAD",
    "Tommy Pham (R)": "CWS",
    "Tommy White (R)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "Vaughn Grissom (R)": "LAA",
    "Victor Mesa Jr. (L)": "TB",
    "Vinnie Pasquantino (L)": "KC",
    "Will Smith (R)": "LAD",
    "William Contreras (R)": "MIL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yainer Diaz (R)": "HOU",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("LAD @ CIN", "Singer"),
    ("LAD @ CIN", "Wrobleski"),
    ("MIL @ PIT", "Harrison"),
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
        "title": "ATH @ TB - Jeffrey Springs (L, ATH) vs Drew Rasmussen (R, TB)",
        "kLines": {'Springs': {'k': 3.1, 'lo': 1, 'hi': 5, 'bf': 21.9, 'matchupK': 14.0, 'ownK': 12.6}, 'Rasmussen': {'k': 5.8, 'lo': 4, 'hi': 7, 'bf': 22.2, 'matchupK': 26.3, 'ownK': 26.6}},
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Springs (HR risk 0.52, vs LHB +1.23, vs RHB +0.13). Rasmussen (HR risk -0.55, vs LHB -0.13, vs RHB -0.66).",
        "rows": [
            row("Jonathan Aranda", "L", "+312", 79, "💎", ["vs Springs"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.8 mph EV, 25.0% barrels. Springs LHB split +1.23, HR risk 0.52.""", blast="good", contact={'stars': 4, 'k': 18.0, 'batterK': 24.7, 'batterWhiff': 25.1, 'pitcherK': 12.6}),
            row("Ryan Vilade", "R", "+570", 78, "💎", ["vs Springs"], """Worst Pickz Hidden Gem. 0 HR, 96.0 mph EV, 12.5% barrels. Springs RHB split +0.13, HR risk 0.52. limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.2, 'batterK': 28.0, 'batterWhiff': 26.0, 'pitcherK': 12.6}),
            row("Victor Mesa Jr.", "L", "+690", 67, "💎", ["vs Springs"], """Worst Pickz Hidden Gem. 0 HR, 92.4 mph EV. Springs LHB split +1.23, HR risk 0.52. limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 14.9, 'batterK': 9.9, 'batterWhiff': 22.4, 'pitcherK': 12.6}),
            row("Yandy Diaz", "R", "+490", 76, "💎", ["vs Springs"], """Worst Pickz Hidden Gem. 0 HR, 93.3 mph EV, 12.5% barrels. Springs RHB split +0.13, HR risk 0.52. limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 14.5, 'batterK': 15.6, 'batterWhiff': 15.9, 'pitcherK': 12.6}),
            row("Junior Caminero", "R", "+314", 72, "⭐", ["vs Springs"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 81.4 mph EV, 12.5% barrels. Springs RHB split +0.13, HR risk 0.52. limited recent HR events; lighter EV form (81.4 mph).""", contact={'stars': 5, 'k': 15.8, 'batterK': 18.2, 'batterWhiff': 20.2, 'pitcherK': 12.6}),
            row("Lawrence Butler", "L", "+680", 84, "🌕 💣", ["vs Rasmussen"], """2 HR, 2 near-HR, 91.7 mph EV, 25.0% barrels. Rasmussen LHB split -0.13, HR risk -0.55. slight split headwind (-0.13); pitcher suppresses HR (-0.55).""", blast="high", contact={'stars': 1, 'k': 27.5, 'batterK': 31.8, 'batterWhiff': 25.1, 'pitcherK': 26.6}),
            row("Zack Gelof", "R", "+620", 77, "", ["vs Rasmussen"], """1 HR, 2 near-HR, 94.9 mph EV, 25.0% barrels. Rasmussen RHB split -0.66, HR risk -0.55. tough split lane (-0.66); pitcher suppresses HR (-0.55).""", blast="good", contact={'stars': 2, 'k': 26.5, 'batterK': 24.7, 'batterWhiff': 30.7, 'pitcherK': 26.6}),
            row("Tommy White", "R", "N/A", 41, "", ["vs Rasmussen"], """0 HR, 89.3 mph EV. Rasmussen RHB split -0.66, HR risk -0.55. tough split lane (-0.66); pitcher suppresses HR (-0.55).""", contact={'stars': 3, 'k': 23.2, 'batterK': 17.1, 'batterWhiff': 23.6, 'pitcherK': 26.6}),
            row("Alika Williams", "R", "+1240", 41, "", ["vs Rasmussen"], """0 HR, 1 near-HR, 88.1 mph EV, 12.5% barrels. Rasmussen RHB split -0.66, HR risk -0.55. tough split lane (-0.66); pitcher suppresses HR (-0.55).""", contact={'stars': 3, 'k': 23.9, 'batterK': 16.9, 'batterWhiff': 25.5, 'pitcherK': 26.6}),
        ],
    },
    {
        "title": "BOS @ TEX - Sonny Gray (R, BOS) vs Cody Bradford (L, TEX)",
        "kLines": {'Gray': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 23.2, 'matchupK': 22.5, 'ownK': 21.7}, 'Bradford': {'k': 3.4, 'lo': 2, 'hi': 5, 'bf': 21.7, 'matchupK': 15.7, 'ownK': 11.2}},
        "description": "Tail key data: Park boost -11% (stadium -11%, weather -1%). Gray (HR risk -0.53, vs LHB -0.27, vs RHB -0.66). Bradford (BAA vs LHB .392, vs RHB .281, HR/9 0.82 vs LHB, 1.19 vs RHB).",
        "rows": [
            row("Danny Jansen", "R", "+525", 60, "", ["vs Gray"], """1 HR, 1 near-HR, 92.6 mph EV, 12.5% barrels. Gray RHB split -0.66, HR risk -0.53. tough split lane (-0.66); pitcher suppresses HR (-0.53).""", blast="good", contact={'stars': 3, 'k': 22.0, 'batterK': 19.7, 'batterWhiff': 27.6, 'pitcherK': 21.7}),
            row("Brandon Nimmo", "L", "+725", 54, "💎", ["vs Gray"], """Worst Pickz Hidden Gem. 0 HR, 93.3 mph EV. Gray LHB split -0.27, HR risk -0.53. slight split headwind (-0.27); pitcher suppresses HR (-0.53).""", blast="good", contact={'stars': 3, 'k': 23.7, 'batterK': 25.9, 'batterWhiff': 29.2, 'pitcherK': 21.7}),
            row("Evan Carter", "L", "+870", 63, "", ["vs Gray"], """1 HR, 2 near-HR, 90.7 mph EV, 12.5% barrels. Gray LHB split -0.27, HR risk -0.53. slight split headwind (-0.27); pitcher suppresses HR (-0.53).""", blast="good", contact={'stars': 2, 'k': 24.1, 'batterK': 30.4, 'batterWhiff': 29.8, 'pitcherK': 21.7}),
            row("Corey Seager", "L", "+404", 67, "⭐", ["vs Gray"], """Worst Pickz Favorite. 0 HR, 96.6 mph EV. Gray LHB split -0.27, HR risk -0.53. slight split headwind (-0.27); pitcher suppresses HR (-0.53).""", blast="good", contact={'stars': 3, 'k': 22.2, 'batterK': 20.2, 'batterWhiff': 30.0, 'pitcherK': 21.7}),
            row("Wyatt Langford", "R", "+517", 61, "", ["vs Gray"], """1 HR, 1 near-HR, 87.6 mph EV, 25.0% barrels. Gray RHB split -0.66, HR risk -0.53. tough split lane (-0.66); pitcher suppresses HR (-0.53).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 25.6, 'batterWhiff': 26.4, 'pitcherK': 21.7}),
            row("Joc Pederson", "L", "+406", 71, "💎", ["vs Gray"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.7 mph EV, 12.5% barrels. Gray LHB split -0.27, HR risk -0.53. slight split headwind (-0.27); pitcher suppresses HR (-0.53).""", blast="good", contact={'stars': 3, 'k': 22.6, 'batterK': 24.0, 'batterWhiff': 27.5, 'pitcherK': 21.7}),
            row("Wilyer Abreu", "L", "+430", 75, "⭐ 🌕 💣", ["vs Bradford"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 98.6 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-11%).""", blast="high", contact={'stars': 5, 'k': 17.0, 'batterK': 20.0, 'batterWhiff': 24.3, 'pitcherK': 11.2}),
            row("Jahmai Jones", "R", "+450", 71, "💎", ["vs Bradford"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.0 mph EV, 12.5% barrels. limited split/risk sample; park/weather net drag (-11%).""", blast="good", contact={'stars': 4, 'k': 19.4, 'batterK': 25.0, 'batterWhiff': 34.3, 'pitcherK': 11.2}),
            row("Willson Contreras", "R", "+396", 66, "", ["vs Bradford"], """0 HR, 92.7 mph EV. limited split/risk sample; park/weather net drag (-11%).""", blast="good", contact={'stars': 4, 'k': 18.1, 'batterK': 23.3, 'batterWhiff': 26.8, 'pitcherK': 11.2}),
            row("Jarren Duran", "L", "N/A", 68, "", ["vs Bradford"], """1 HR, 1 near-HR, 87.6 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-11%).""", blast="good", contact={'stars': 4, 'k': 19.6, 'batterK': 25.7, 'batterWhiff': 33.3, 'pitcherK': 11.2}),
        ],
    },
    {
        "title": "DET @ CWS - Framber Valdez (L, DET) vs Erick Fedde (R, CWS)",
        "kLines": {'Valdez': {'k': 4.1, 'lo': 2, 'hi': 6, 'bf': 24.1, 'matchupK': 17.0, 'ownK': 13.9}, 'Fedde': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 20.7, 'matchupK': 18.3, 'ownK': 15.4}},
        "description": "Tail key data: Park boost -14% (stadium -5%, weather -9%). Valdez (HR risk -0.79, vs LHB -0.63, vs RHB -0.55). Fedde (HR risk -0.09, vs LHB -0.15, vs RHB +0.18).",
        "rows": [
            row("Munetaka Murakami", "L", "N/A", 67, "", ["vs Valdez"], """1 HR, 2 near-HR, 92.9 mph EV, 12.5% barrels. Valdez LHB split -0.63, HR risk -0.79. tough split lane (-0.63); pitcher suppresses HR (-0.79).""", blast="good", contact={'stars': 2, 'k': 26.5, 'batterK': 45.2, 'batterWhiff': 46.2, 'pitcherK': 13.9}),
            row("Randal Grichuk", "R", "+420", 65, "💎", ["vs Valdez"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.7 mph EV, 12.5% barrels. Valdez RHB split -0.55, HR risk -0.79. tough split lane (-0.55); pitcher suppresses HR (-0.79).""", blast="good", contact={'stars': 4, 'k': 18.0, 'batterK': 26.0, 'batterWhiff': 24.5, 'pitcherK': 13.9}),
            row("Tommy Pham", "R", "+690", 62, "", ["vs Valdez"], """1 HR, 1 near-HR, 94.8 mph EV, 33.3% barrels. Valdez RHB split -0.55, HR risk -0.79. tough split lane (-0.55); pitcher suppresses HR (-0.79).""", blast="good", contact={'stars': 4, 'k': 19.3, 'batterK': 42.1, 'batterWhiff': 35.3, 'pitcherK': 13.9}),
            row("Andrew Benintendi", "L", "N/A", 52, "", ["vs Valdez"], """0 HR, 93.9 mph EV, 12.5% barrels. Valdez LHB split -0.63, HR risk -0.79. tough split lane (-0.63); pitcher suppresses HR (-0.79).""", blast="good", contact={'stars': 5, 'k': 15.9, 'batterK': 16.9, 'batterWhiff': 19.4, 'pitcherK': 13.9}),
            row("Spencer Torkelson", "R", "+471", 78, "🌕 💣 💎", ["vs Fedde"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 87.8 mph EV, 25.0% barrels. Fedde RHB split +0.18, HR risk -0.09. pitcher risk below avg (-0.09); park/weather net drag (-14%).""", blast="high", contact={'stars': 3, 'k': 23.4, 'batterK': 33.3, 'batterWhiff': 36.2, 'pitcherK': 15.4}),
            row("Kevin McGonigle", "L", "+559", 63, "", ["vs Fedde"], """1 HR, 2 near-HR, 90.8 mph EV, 25.0% barrels. Fedde LHB split -0.15, HR risk -0.09. slight split headwind (-0.15); pitcher risk below avg (-0.09).""", blast="good", contact={'stars': 5, 'k': 15.5, 'batterK': 12.2, 'batterWhiff': 17.9, 'pitcherK': 15.4}),
            row("Colt Keith", "L", "+600", 61, "", ["vs Fedde"], """1 HR, 1 near-HR, 83.6 mph EV, 12.5% barrels. Fedde LHB split -0.15, HR risk -0.09. slight split headwind (-0.15); pitcher risk below avg (-0.09).""", blast="good", contact={'stars': 3, 'k': 21.3, 'batterK': 27.8, 'batterWhiff': 32.3, 'pitcherK': 15.4}),
            row("Gleyber Torres", "R", "+900", 50, "", ["vs Fedde"], """0 HR, 93.7 mph EV. Fedde RHB split +0.18, HR risk -0.09. pitcher risk below avg (-0.09); park/weather net drag (-14%).""", blast="good", contact={'stars': 4, 'k': 18.2, 'batterK': 21.5, 'batterWhiff': 20.0, 'pitcherK': 15.4}),
            row("Riley Greene", "L", "+340", 63, "💎", ["vs Fedde"], """Worst Pickz Hidden Gem. 0 HR, 98.2 mph EV. Fedde LHB split -0.15, HR risk -0.09. slight split headwind (-0.15); pitcher risk below avg (-0.09).""", blast="good", contact={'stars': 3, 'k': 21.7, 'batterK': 27.4, 'batterWhiff': 32.1, 'pitcherK': 15.4}),
        ],
    },
    {
        "title": "KC @ HOU - Seth Lugo (R, KC) vs Ethan Pecko (R, HOU)",
        "kLines": {'Lugo': {'k': 4.0, 'lo': 2, 'hi': 6, 'bf': 23.3, 'matchupK': 17.0, 'ownK': 15.7}, 'Pecko': {'k': 3.7, 'lo': 2, 'hi': 5, 'bf': 20.7, 'matchupK': 17.8, 'ownK': 15.6}},
        "description": "Tail key data: Park boost +5% (stadium +6%, weather +0%). Lugo (HR risk 0.00, vs LHB +0.55, vs RHB -0.58). Pecko (BAA vs LHB .204, vs RHB .212, HR/9 1.96).",
        "rows": [
            row("Yordan Alvarez", "L", "+275", 83, "⭐", ["vs Lugo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 88.7 mph EV, 25.0% barrels. Lugo LHB split +0.55, HR risk 0.00.""", blast="good", contact={'stars': 4, 'k': 18.1, 'batterK': 22.1, 'batterWhiff': 20.9, 'pitcherK': 15.7}),
            row("Nelson Velazquez", "R", "N/A", 82, "🚀 🌕 💣", ["vs Lugo"], """1 HR, 2 near-HR, 101.3 mph EV, 25.0% barrels. Lugo RHB split -0.58, HR risk 0.00. tough split lane (-0.58).""", blast="high", contact={'stars': 3, 'k': 23.3, 'batterK': 41.7, 'batterWhiff': 44.8, 'pitcherK': 15.7}),
            row("Yainer Diaz", "R", "+600", 76, "", ["vs Lugo"], """1 HR, 1 near-HR, 95.0 mph EV, 12.5% barrels. Lugo RHB split -0.58, HR risk 0.00. tough split lane (-0.58).""", blast="good", contact={'stars': 4, 'k': 18.2, 'batterK': 19.1, 'batterWhiff': 24.6, 'pitcherK': 15.7}),
            row("Jeremy Pena", "R", "+500", 69, "", ["vs Lugo"], """1 HR, 2 near-HR, 84.0 mph EV, 12.5% barrels. Lugo RHB split -0.58, HR risk 0.00. tough split lane (-0.58); lighter EV form (84.0 mph).""", blast="good", contact={'stars': 3, 'k': 22.7, 'batterK': 32.1, 'batterWhiff': 34.3, 'pitcherK': 15.7}),
            row("Bobby Witt Jr.", "R", "+425", 82, "", ["vs Pecko"], """1 HR, 1 near-HR, 96.1 mph EV, 12.5% barrels. limited split/risk sample.""", blast="good", contact={'stars': 4, 'k': 18.2, 'batterK': 15.4, 'batterWhiff': 25.3, 'pitcherK': 15.6}),
            row("Vinnie Pasquantino", "L", "+413", 73, "⭐", ["vs Pecko"], """Worst Pickz Favorite. 0 HR, 93.8 mph EV, 12.5% barrels. limited split/risk sample; limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 16.0, 'batterK': 12.8, 'batterWhiff': 15.3, 'pitcherK': 15.6}),
            row("John Rave", "L", "N/A", 70, "", ["vs Pecko"], """1 HR, 2 near-HR, 89.2 mph EV, 12.5% barrels. limited split/risk sample.""", blast="good", contact={'stars': 4, 'k': 19.4, 'batterK': 21.7, 'batterWhiff': 22.0, 'pitcherK': 15.6}),
        ],
    },
    {
        "title": "LAD @ CIN - Justin Wrobleski 🧤 (L, LAD) vs Brady Singer 🧤 (R, CIN)",
        "kLines": {'Wrobleski': {'k': 6.6, 'lo': 5, 'hi': 8, 'bf': 23.9, 'matchupK': 27.6, 'ownK': 27.9}, 'Singer': {'k': 4.0, 'lo': 2, 'hi': 6, 'bf': 23.2, 'matchupK': 17.4, 'ownK': 16.9}},
        "description": "Tail key data: Park boost +18% (stadium +14%, weather +4%). Wrobleski 🧤 (HR risk 1.23, vs LHB +0.85, vs RHB +1.06). Singer 🧤 (HR risk 1.11, vs LHB +1.16, vs RHB +0.57).",
        "rows": [
            row("Juan Brito", "S", "+650", 88, "🌕 💣 💎", ["vs Wrobleski"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.8 mph EV, 37.5% barrels. Wrobleski SHB→RHB split +1.06, HR risk 1.23.""", blast="good", contact={'stars': 2, 'k': 26.3, 'batterK': 25.4, 'batterWhiff': 27.7, 'pitcherK': 27.9}),
            row("Matt McLain", "R", "+620", 89, "🌕 💣", ["vs Wrobleski"], """1 HR, 1 near-HR, 92.4 mph EV, 25.0% barrels. Wrobleski RHB split +1.06, HR risk 1.23.""", blast="good", contact={'stars': 1, 'k': 28.9, 'batterK': 32.9, 'batterWhiff': 30.6, 'pitcherK': 27.9}),
            row("Tyler Stephenson", "R", "+440", 92, "🌕 💣 💎", ["vs Wrobleski"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.1 mph EV, 12.5% barrels. Wrobleski RHB split +1.06, HR risk 1.23.""", blast="good", contact={'stars': 2, 'k': 26.3, 'batterK': 27.4, 'batterWhiff': 25.5, 'pitcherK': 27.9}),
            row("Sal Stewart", "R", "+410", 92, "🚀 🌕 💣 💎", ["vs Wrobleski"], """Worst Pickz Hidden Gem. 0 HR, 100.4 mph EV, 12.5% barrels. Wrobleski RHB split +1.06, HR risk 1.23. limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.1, 'batterK': 20.0, 'batterWhiff': 28.7, 'pitcherK': 27.9}),
            row("Elly De La Cruz", "S", "+300", 93, "🌕 💣", ["vs Wrobleski"], """0 HR, 96.1 mph EV, 12.5% barrels. Wrobleski SHB→RHB split +1.06, HR risk 1.23. limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 26.4, 'batterK': 25.3, 'batterWhiff': 27.2, 'pitcherK': 27.9}),
            row("Teoscar Hernandez", "R", "+445", 88, "🌕 💣", ["vs Singer"], """1 HR, 1 near-HR, 92.8 mph EV, 12.5% barrels. Singer RHB split +0.57, HR risk 1.11.""", blast="good", contact={'stars': 3, 'k': 22.1, 'batterK': 25.0, 'batterWhiff': 37.3, 'pitcherK': 16.9}),
            row("Kyle Tucker", "L", "+386", 72, "", ["vs Singer"], """0 HR, 1 near-HR, 86.8 mph EV, 12.5% barrels. Singer LHB split +1.16, HR risk 1.11. limited recent HR events; lighter EV form (86.8 mph).""", contact={'stars': 5, 'k': 14.7, 'batterK': 10.3, 'batterWhiff': 12.9, 'pitcherK': 16.9}),
            row("Mookie Betts", "R", "+506", 75, "", ["vs Singer"], """0 HR, 92.8 mph EV. Singer RHB split +0.57, HR risk 1.11. limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 14.0, 'batterK': 9.7, 'batterWhiff': 12.8, 'pitcherK': 16.9}),
            row("Will Smith", "R", "+353", 79, "💎", ["vs Singer"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 90.2 mph EV, 12.5% barrels. Singer RHB split +0.57, HR risk 1.11. limited recent HR events.""", contact={'stars': 5, 'k': 17.1, 'batterK': 18.3, 'batterWhiff': 16.7, 'pitcherK': 16.9}),
        ],
    },
    {
        "title": "MIL @ PIT - Kyle Harrison 🧤 (L, MIL) vs Wilber Dotel (R, PIT)",
        "kLines": {'Harrison': {'k': 5.4, 'lo': 4, 'hi': 7, 'bf': 20.7, 'matchupK': 26.0, 'ownK': 26.5}, 'Dotel': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 20.0, 'matchupK': 22.7, 'ownK': 23.9}},
        "description": "Tail key data: Park boost -7% (stadium -15%, weather +8%). Harrison 🧤 (HR risk 1.67, vs LHB -0.85, vs RHB +2.49). Dotel (HR risk -1.29, vs LHB -1.23, vs RHB -0.46).",
        "rows": [
            row("Bryan Reynolds", "S", "+540", 94, "🌕 💣", ["vs Harrison"], """1 HR, 1 near-HR, 92.5 mph EV, 12.5% barrels. Harrison SHB→RHB split +2.49, HR risk 1.67. park/weather net drag (-7%).""", blast="good", contact={'stars': 3, 'k': 23.3, 'batterK': 19.1, 'batterWhiff': 24.9, 'pitcherK': 26.5}),
            row("Oneil Cruz", "L", "+440", 85, "💎", ["vs Harrison"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.9 mph EV, 12.5% barrels. Harrison LHB split -0.85, HR risk 1.67. tough split lane (-0.85); park/weather net drag (-7%).""", blast="good", contact={'stars': 1, 'k': 28.7, 'batterK': 30.7, 'batterWhiff': 34.5, 'pitcherK': 26.5}),
            row("Konnor Griffin", "R", "+650", 82, "", ["vs Harrison"], """0 HR, 94.5 mph EV. Harrison RHB split +2.49, HR risk 1.67. park/weather net drag (-7%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 25.1, 'batterK': 23.9, 'batterWhiff': 26.6, 'pitcherK': 26.5}),
            row("Brandon Lowe", "L", "N/A", 92, "🌕 💣 💎", ["vs Harrison"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 96.4 mph EV, 25.0% barrels. Harrison LHB split -0.85, HR risk 1.67. tough split lane (-0.85); park/weather net drag (-7%).""", blast="high", contact={'stars': 1, 'k': 28.1, 'batterK': 28.4, 'batterWhiff': 35.5, 'pitcherK': 26.5}),
            row("Andrew Vaughn", "R", "+760", 42, "", ["vs Dotel"], """0 HR, 1 near-HR, 91.1 mph EV. Dotel RHB split -0.46, HR risk -1.29. tough split lane (-0.46); pitcher suppresses HR (-1.29).""", contact={'stars': 3, 'k': 19.9, 'batterK': 20.0, 'batterWhiff': 13.8, 'pitcherK': 23.9}),
            row("William Contreras", "R", "+540", 56, "", ["vs Dotel"], """0 HR, 93.9 mph EV. Dotel RHB split -0.46, HR risk -1.29. tough split lane (-0.46); pitcher suppresses HR (-1.29).""", blast="good", contact={'stars': 3, 'k': 20.8, 'batterK': 18.1, 'batterWhiff': 21.8, 'pitcherK': 23.9}),
            row("Jackson Chourio", "R", "+452", 54, "", ["vs Dotel"], """0 HR, 90.2 mph EV, 12.5% barrels. Dotel RHB split -0.46, HR risk -1.29. tough split lane (-0.46); pitcher suppresses HR (-1.29).""", contact={'stars': 3, 'k': 21.8, 'batterK': 19.6, 'batterWhiff': 25.1, 'pitcherK': 23.9}),
            row("Brice Turang", "L", "+710", 57, "", ["vs Dotel"], """0 HR, 1 near-HR, 92.1 mph EV, 12.5% barrels. Dotel LHB split -1.23, HR risk -1.29. tough split lane (-1.23); pitcher suppresses HR (-1.29).""", blast="good", contact={'stars': 3, 'k': 21.7, 'batterK': 21.1, 'batterWhiff': 21.4, 'pitcherK': 23.9}),
            row("Cooper Pratt", "R", "+1200", 40, "", ["vs Dotel"], """0 HR, 91.9 mph EV. Dotel RHB split -0.46, HR risk -1.29. tough split lane (-0.46); pitcher suppresses HR (-1.29).""", contact={'stars': 4, 'k': 17.7, 'batterK': 12.3, 'batterWhiff': 11.5, 'pitcherK': 23.9}),
        ],
    },
    {
        "title": "MIN @ LAA - Taj Bradley (R, MIN) vs Walbert Urena (R, LAA)",
        "kLines": {'Bradley': {'k': 6.4, 'lo': 5, 'hi': 8, 'bf': 23.6, 'matchupK': 26.9, 'ownK': 27.4}, 'Urena': {'k': 4.9, 'lo': 3, 'hi': 6, 'bf': 22.4, 'matchupK': 21.8, 'ownK': 23.5}},
        "description": "Tail key data: Park boost -8% (stadium -10%, weather +2%). Bradley (HR risk 0.33, vs LHB +0.62, vs RHB -0.15). Urena (HR risk -0.49, vs LHB -0.83, vs RHB +0.20).",
        "rows": [
            row("Moises Ballesteros", "L", "+630", 84, "🌕 💣 💎", ["vs Bradley"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 97.0 mph EV, 25.0% barrels. Bradley LHB split +0.62, HR risk 0.33. park/weather net drag (-8%).""", blast="high", contact={'stars': 2, 'k': 27.0, 'batterK': 27.3, 'batterWhiff': 28.0, 'pitcherK': 27.4}),
            row("Vaughn Grissom", "R", "+870", 76, "", ["vs Bradley"], """1 HR, 2 near-HR, 94.7 mph EV, 25.0% barrels. Bradley RHB split -0.15, HR risk 0.33. slight split headwind (-0.15); park/weather net drag (-8%).""", blast="good", contact={'stars': 3, 'k': 24.0, 'batterK': 20.9, 'batterWhiff': 21.6, 'pitcherK': 27.4}),
            row("Josh Lowe", "L", "+640", 65, "", ["vs Bradley"], """1 HR, 1 near-HR, 85.1 mph EV, 12.5% barrels. Bradley LHB split +0.62, HR risk 0.33. park/weather net drag (-8%); lighter EV form (85.1 mph).""", blast="good", contact={'stars': 1, 'k': 29.2, 'batterK': 31.5, 'batterWhiff': 37.3, 'pitcherK': 27.4}),
            row("Josh Bell", "S", "+543", 77, "⭐ 🌕 💣", ["vs Urena"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.8 mph EV, 25.0% barrels. Urena SHB→LHB split -0.83, HR risk -0.49. tough split lane (-0.83); pitcher suppresses HR (-0.49).""", blast="high", contact={'stars': 3, 'k': 20.3, 'batterK': 16.7, 'batterWhiff': 19.5, 'pitcherK': 23.5}),
            row("Kody Clemens", "L", "+445", 78, "🌕 💣", ["vs Urena"], """2 HR, 2 near-HR, 92.4 mph EV, 25.0% barrels. Urena LHB split -0.83, HR risk -0.49. tough split lane (-0.83); pitcher suppresses HR (-0.49).""", blast="high", contact={'stars': 3, 'k': 21.3, 'batterK': 21.4, 'batterWhiff': 17.8, 'pitcherK': 23.5}),
            row("Emmanuel Rodriguez", "L", "+650", 77, "🌕 💣", ["vs Urena"], """1 HR, 1 near-HR, 98.7 mph EV, 60.0% barrels. Urena LHB split -0.83, HR risk -0.49. tough split lane (-0.83); pitcher suppresses HR (-0.49).""", blast="high", contact={'stars': 3, 'k': 22.9, 'batterK': 25.0, 'batterWhiff': 24.3, 'pitcherK': 23.5}),
            row("Royce Lewis", "R", "+500", 65, "💎", ["vs Urena"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.5 mph EV, 25.0% barrels. Urena RHB split +0.20, HR risk -0.49. pitcher suppresses HR (-0.49); park/weather net drag (-8%).""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 21.3, 'batterWhiff': 29.4, 'pitcherK': 23.5}),
        ],
    },
    {
        "title": "PHI @ NYM - Aaron Nola (R, PHI) vs Nolan McLean (R, NYM)",
        "kLines": {'Nola': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 22.8, 'matchupK': 23.4, 'ownK': 23.9}, 'McLean': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 23.6, 'matchupK': 22.3, 'ownK': 23.9}},
        "description": "Tail key data: Park boost +3% (stadium -2%, weather +6%). Nola (HR risk 0.35, vs LHB +0.38, vs RHB +0.28). McLean (HR risk -0.64, vs LHB -0.19, vs RHB -0.97).",
        "rows": [
            row("Carson Benge", "L", "+670", 85, "🌕 💣", ["vs Nola"], """1 HR, 1 near-HR, 97.5 mph EV, 37.5% barrels. Nola LHB split +0.38, HR risk 0.35.""", blast="high", contact={'stars': 2, 'k': 24.8, 'batterK': 27.3, 'batterWhiff': 25.6, 'pitcherK': 23.9}),
            row("Jared Young", "L", "+545", 71, "🚀 💎", ["vs Nola"], """Worst Pickz Hidden Gem. 0 HR, 102.1 mph EV, 12.5% barrels. Nola LHB split +0.38, HR risk 0.35. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.0, 'batterK': 17.1, 'batterWhiff': 20.4, 'pitcherK': 23.9}),
            row("Juan Soto", "L", "+299", 78, "💎", ["vs Nola"], """Worst Pickz Hidden Gem. 0 HR, 99.3 mph EV. Nola LHB split +0.38, HR risk 0.35. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.5, 'batterK': 17.2, 'batterWhiff': 24.3, 'pitcherK': 23.9}),
            row("Francisco Alvarez", "R", "+525", 70, "", ["vs Nola"], """0 HR, 1 near-HR, 92.7 mph EV. Nola RHB split +0.28, HR risk 0.35. limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 30.7, 'batterK': 41.1, 'batterWhiff': 41.5, 'pitcherK': 23.9}),
            row("Brett Baty", "L", "+600", 75, "", ["vs Nola"], """1 HR, 1 near-HR, 93.9 mph EV, 12.5% barrels. Nola LHB split +0.38, HR risk 0.35.""", blast="good", contact={'stars': 2, 'k': 24.1, 'batterK': 18.5, 'batterWhiff': 31.8, 'pitcherK': 23.9}),
            row("Francisco Lindor", "S", "+364", 88, "🌕 💣", ["vs Nola"], """2 HR, 2 near-HR, 90.8 mph EV, 12.5% barrels. Nola SHB→LHB split +0.38, HR risk 0.35.""", blast="high", contact={'stars': 2, 'k': 25.3, 'batterK': 27.7, 'batterWhiff': 27.3, 'pitcherK': 23.9}),
            row("Bo Bichette", "R", "+700", 64, "", ["vs Nola"], """0 HR, 96.1 mph EV. Nola RHB split +0.28, HR risk 0.35. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 20.9, 'batterK': 18.2, 'batterWhiff': 19.6, 'pitcherK': 23.9}),
            row("Kyle Schwarber", "L", "+295", 78, "⭐", ["vs McLean"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.5 mph EV, 12.5% barrels. McLean LHB split -0.19, HR risk -0.64. slight split headwind (-0.19); pitcher suppresses HR (-0.64).""", blast="good", contact={'stars': 2, 'k': 25.7, 'batterK': 27.5, 'batterWhiff': 30.0, 'pitcherK': 23.9}),
            row("Bryce Harper", "L", "+465", 74, "💎", ["vs McLean"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.5 mph EV, 12.5% barrels. McLean LHB split -0.19, HR risk -0.64. slight split headwind (-0.19); pitcher suppresses HR (-0.64).""", blast="good", contact={'stars': 2, 'k': 25.7, 'batterK': 25.9, 'batterWhiff': 33.3, 'pitcherK': 23.9}),
            row("Brandon Marsh", "L", "+860", 51, "💎", ["vs McLean"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 89.5 mph EV, 12.5% barrels. McLean LHB split -0.19, HR risk -0.64. slight split headwind (-0.19); pitcher suppresses HR (-0.64).""", contact={'stars': 3, 'k': 22.8, 'batterK': 23.5, 'batterWhiff': 22.9, 'pitcherK': 23.9}),
        ],
    },
    {
        "title": "SD @ COL - Michael King (R, SD) vs Tanner Gordon (R, COL)",
        "kLines": {'King': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 23.4, 'matchupK': 20.2, 'ownK': 21.1}, 'Gordon': {'k': 3.9, 'lo': 2, 'hi': 6, 'bf': 22.1, 'matchupK': 17.6, 'ownK': 17.0}},
        "description": "Tail key data: Park boost +27% (stadium +20%, weather +7%). King (HR risk -0.21, vs LHB -0.07, vs RHB -0.22). Gordon (HR risk 0.46, vs LHB +0.71, vs RHB -0.06).",
        "rows": [
            row("Cole Carrigg", "S", "+760", 89, "🌕 💣", ["vs King"], """2 HR, 2 near-HR, 98.4 mph EV, 12.5% barrels. King SHB→LHB split -0.07, HR risk -0.21. slight split headwind (-0.07); pitcher risk below avg (-0.21).""", blast="high", contact={'stars': 3, 'k': 22.9, 'batterK': 27.7, 'batterWhiff': 24.4, 'pitcherK': 21.1}),
            row("Connor Norby", "R", "+520", 73, "", ["vs King"], """1 HR, 3 near-HR, 90.6 mph EV, 37.5% barrels. King RHB split -0.22, HR risk -0.21. slight split headwind (-0.22); pitcher risk below avg (-0.21).""", blast="good", contact={'stars': 3, 'k': 21.5, 'batterK': 23.5, 'batterWhiff': 23.0, 'pitcherK': 21.1}),
            row("Hunter Goodman", "R", "+240", 66, "", ["vs King"], """0 HR, 1 near-HR, 89.2 mph EV, 12.5% barrels. King RHB split -0.22, HR risk -0.21. slight split headwind (-0.22); pitcher risk below avg (-0.21).""", contact={'stars': 3, 'k': 22.3, 'batterK': 22.9, 'batterWhiff': 27.9, 'pitcherK': 21.1}),
            row("Ethan Salas", "L", "N/A", 92, "🌕 💣 💎", ["vs Gordon"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 96.2 mph EV, 12.5% barrels. Gordon LHB split +0.71, HR risk 0.46.""", blast="high", contact={'stars': 4, 'k': 19.8, 'batterK': 33.3, 'batterWhiff': 24.4, 'pitcherK': 17.0}),
            row("Jackson Merrill", "L", "+327", 91, "🚀 ⭐ 🌕 💣", ["vs Gordon"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 102.0 mph EV, 12.5% barrels. Gordon LHB split +0.71, HR risk 0.46. limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.3, 'batterK': 16.1, 'batterWhiff': 26.8, 'pitcherK': 17.0}),
            row("Fernando Tatis Jr.", "R", "+280", 93, "🌕 💣", ["vs Gordon"], """2 HR, 2 near-HR, 91.8 mph EV, 25.0% barrels. Gordon RHB split -0.06, HR risk 0.46. slight split headwind (-0.06).""", blast="high", contact={'stars': 4, 'k': 18.2, 'batterK': 17.8, 'batterWhiff': 23.4, 'pitcherK': 17.0}),
            row("Manny Machado", "R", "+300", 67, "💎", ["vs Gordon"], """Worst Pickz Hidden Gem. 0 HR, 81.8 mph EV, 12.5% barrels. Gordon RHB split -0.06, HR risk 0.46. slight split headwind (-0.06); limited recent HR events.""", contact={'stars': 5, 'k': 17.2, 'batterK': 15.7, 'batterWhiff': 20.6, 'pitcherK': 17.0}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-17")

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

    out = ROOT / '_games-0917.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
