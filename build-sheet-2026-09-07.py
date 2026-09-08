#!/usr/bin/env python3
"""Generate games[] block for 2026-09-07 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Bobby Witt Jr. (R)",
    "Bryce Harper (L)",
    "Christian Yelich (L)",
    "Coby Mayo (R)",
    "Daylen Lile (L)",
    "Elly De La Cruz (S)",
    "Francisco Lindor (S)",
    "Heriberto Hernandez (R)",
    "Jake Bauers (L)",
    "Kazuma Okamoto (R)",
    "Kody Clemens (L)",
    "Kyle Schwarber (L)",
    "Lawrence Butler (L)",
    "Matt McLain (R)",
    "Max Muncy (L)",
    "Mickey Gasper (S)",
    "Pete Alonso (R)",
    "Pete Crow Armstrong (L)",
    "Rafael Devers (L)",
    "Ronald Acuna Jr. (R)",
}

GEMS = {
    "Alejandro Kirk (R)",
    "Brett Baty (L)",
    "JJ Bleday (L)",
    "Ketel Marte (S)",
    "Michael Conforto (L)",
    "Moises Ballesteros (L)",
    "Salvador Perez (R)",
    "Tyler Stephenson (R)",
}

PLAYER_TEAMS = {
    "Agustin Ramirez (R)": "MIA",
    "Alec Burleson (L)": "STL",
    "Alejandro Kirk (R)": "TOR",
    "Alex Freeland (S)": "LAD",
    "Andrew Knizner (R)": "SF",
    "Andrew Vaughn (R)": "MIL",
    "Bo Bichette (R)": "NYM",
    "Bobby Witt Jr. (R)": "KC",
    "Brett Baty (L)": "NYM",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Carson Kelly (R)": "CHC",
    "Christian Yelich (L)": "MIL",
    "Coby Mayo (R)": "BAL",
    "Colton Cowser (L)": "BAL",
    "David Fry (R)": "CLE",
    "Daylen Lile (L)": "WSH",
    "Drake Baldwin (L)": "ATL",
    "Elly De La Cruz (S)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Lindor (S)": "NYM",
    "Garrett Mitchell (L)": "MIL",
    "George Springer (R)": "TOR",
    "Gleyber Torres (R)": "DET",
    "Grant McCray (L)": "SF",
    "Heriberto Hernandez (R)": "MIA",
    "JJ Bleday (L)": "CIN",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Jarren Duran (L)": "BOS",
    "Jeff McNeil (L)": "ATH",
    "Jesus Sanchez (L)": "TOR",
    "Joshua Baez (R)": "STL",
    "Juan Soto (L)": "NYM",
    "Kazuma Okamoto (R)": "TOR",
    "Keibert Ruiz (S)": "WSH",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Tucker (L)": "LAD",
    "Lane Thomas (R)": "ATL",
    "Lawrence Butler (L)": "ATH",
    "Leonardo Bernal (S)": "STL",
    "Manny Machado (R)": "SD",
    "Matt McLain (R)": "CIN",
    "Max Muncy (L)": "LAD",
    "Michael Conforto (L)": "CHC",
    "Mickey Gasper (S)": "BOS",
    "Miguel Amaya (R)": "CHC",
    "Moises Ballesteros (L)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Patrick Bailey (S)": "CLE",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Riley Greene (L)": "DET",
    "Roman Anthony (L)": "BOS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan Jeffers (R)": "MIN",
    "Salvador Perez (R)": "KC",
    "Seiya Suzuki (R)": "CHC",
    "Thomas Saggese (R)": "STL",
    "Tim Tawa (R)": "ARI",
    "Trevor Larnach (L)": "MIN",
    "Tyler Stephenson (R)": "CIN",
    "Tyrone Taylor (R)": "CHC",
    "Vinnie Pasquantino (L)": "KC",
    "William Contreras (R)": "MIL",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("WSH @ SD", "Irvin"),
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
        "title": "ARI @ KC - Jose Cabrera (R, ARI) vs Noah Cameron (L, KC)",
        "kLines": {"Cabrera": {"k": 3.6, "lo": 2, "hi": 5, "bf": 21.7, "matchupK": 16.7, "ownK": 15.1}, "Cameron": {"k": 4.7, "lo": 3, "hi": 6, "bf": 23.5, "matchupK": 20.1, "ownK": 22.0}},
        "description": "Tail key data: Park boost +10% (stadium +12%, weather -1%). Cabrera (BAA vs LHB .214, vs RHB .316, HR/9 1.50). Cameron (HR risk -0.45, vs LHB +0.85, vs RHB -0.62).",
        "rows": [
            row("Salvador Perez", "R", "+475", 79, "💎", ["vs Cabrera"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.5 mph EV, 12.5% barrels. limited split/risk sample.""", blast="good", contact={'stars': 4, 'k': 17.8, 'batterK': 15.3, 'batterWhiff': 24.6, 'pitcherK': 15.1}),
            row("Bobby Witt Jr.", "R", "+460", 90, "⭐ 🌕 💣", ["vs Cabrera"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 97.1 mph EV, 25.0% barrels. limited split/risk sample.""", blast="high", contact={'stars': 5, 'k': 17.1, 'batterK': 14.1, 'batterWhiff': 23.6, 'pitcherK': 15.1}),
            row("Vinnie Pasquantino", "L", "+590", 87, "🌕 💣", ["vs Cabrera"], """2 HR, 3 near-HR, 89.8 mph EV, 25.0% barrels. limited split/risk sample.""", blast="high", contact={'stars': 5, 'k': 13.9, 'batterK': 7.0, 'batterWhiff': 13.8, 'pitcherK': 15.1}),
            row("Ketel Marte", "S", "+322", 72, "💎", ["vs Cameron"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.5 mph EV, 12.5% barrels. Cameron SHB→RHB split -0.62, HR risk -0.45. tough split lane (-0.62); pitcher suppresses HR (-0.45).""", blast="good", contact={'stars': 4, 'k': 19.5, 'batterK': 16.7, 'batterWhiff': 19.3, 'pitcherK': 22.0}),
            row("Tim Tawa", "R", "+630", 55, "", ["vs Cameron"], """0 HR, 91.7 mph EV. Cameron RHB split -0.62, HR risk -0.45. tough split lane (-0.62); pitcher suppresses HR (-0.45).""", contact={'stars': 2, 'k': 25.2, 'batterK': 30.8, 'batterWhiff': 30.3, 'pitcherK': 22.0}),
        ],
    },
    {
        "title": "ATL @ PHI - Grant Holmes (R, ATL) vs Jesus Luzardo (L, PHI)",
        "kLines": {"Holmes": {"k": 3.6, "lo": 2, "hi": 5, "bf": 21.2, "matchupK": 16.8, "ownK": 16.4}, "Luzardo": {"k": 7.6, "lo": 6, "hi": 9, "bf": 24.5, "matchupK": 30.9, "ownK": 32.2}},
        "description": "Tail key data: Park boost -4% (stadium +14%, weather -19%). Holmes (HR risk -0.19, vs LHB -0.12, vs RHB +0.40). Luzardo (HR risk -0.51, vs LHB -0.83, vs RHB -0.17).",
        "rows": [
            row("Bryce Harper", "L", "+430", 83, "⭐", ["vs Holmes"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.3 mph EV, 25.0% barrels. Holmes LHB split -0.12, HR risk -0.19. slight split headwind (-0.12); pitcher risk below avg (-0.19).""", blast="good", contact={'stars': 4, 'k': 19.0, 'batterK': 19.8, 'batterWhiff': 27.6, 'pitcherK': 16.4}),
            row("Kyle Schwarber", "L", "+240", 76, "⭐", ["vs Holmes"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 90.7 mph EV, 25.0% barrels. Holmes LHB split -0.12, HR risk -0.19. slight split headwind (-0.12); pitcher risk below avg (-0.19).""", blast="good", contact={'stars': 3, 'k': 20.7, 'batterK': 22.8, 'batterWhiff': 33.2, 'pitcherK': 16.4}),
            row("Ronald Acuna Jr.", "R", "+541", 65, "🚀 ⭐", ["vs Luzardo"], """Worst Pickz Favorite. 0 HR, 100.8 mph EV, 12.5% barrels. Luzardo RHB split -0.17, HR risk -0.51. slight split headwind (-0.17); pitcher suppresses HR (-0.51).""", blast="good", contact={'stars': 1, 'k': 31.1, 'batterK': 26.4, 'batterWhiff': 32.8, 'pitcherK': 32.2}),
            row("Drake Baldwin", "L", "+820", 60, "", ["vs Luzardo"], """0 HR, 94.5 mph EV. Luzardo LHB split -0.83, HR risk -0.51. tough split lane (-0.83); pitcher suppresses HR (-0.51).""", blast="good", contact={'stars': 1, 'k': 32.2, 'batterK': 28.4, 'batterWhiff': 35.1, 'pitcherK': 32.2}),
            row("Lane Thomas", "R", "+790", 63, "", ["vs Luzardo"], """1 HR, 1 near-HR, 91.4 mph EV. Luzardo RHB split -0.17, HR risk -0.51. slight split headwind (-0.17); pitcher suppresses HR (-0.51).""", blast="good", contact={'stars': 1, 'k': 31.7, 'batterK': 34.1, 'batterWhiff': 35.1, 'pitcherK': 32.2}),
        ],
    },
    {
        "title": "CHC @ MIL - Matthew Boyd (L, CHC) vs Robert Gasser (L, MIL)",
        "kLines": {"Boyd": {"k": 3.9, "lo": 2, "hi": 5, "bf": 23.2, "matchupK": 16.7, "ownK": 15.4}, "Gasser": {"k": 4.5, "lo": 3, "hi": 6, "bf": 21.9, "matchupK": 20.5, "ownK": 22.1}},
        "description": "Tail key data: Park boost -11% (stadium -3%, weather -8%). Boyd (HR risk 0.93, vs LHB -1.04, vs RHB +1.20). Gasser (HR risk 0.35, vs LHB -0.21, vs RHB +0.31).",
        "rows": [
            row("Jake Bauers", "L", "+490", 80, "⭐", ["vs Boyd"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.7 mph EV, 25.0% barrels. Boyd LHB split -1.04, HR risk 0.93. tough split lane (-1.04); park/weather net drag (-11%).""", blast="good", contact={'stars': 3, 'k': 20.3, 'batterK': 26.3, 'batterWhiff': 31.5, 'pitcherK': 15.4}),
            row("William Contreras", "R", "+630", 85, "", ["vs Boyd"], """1 HR, 2 near-HR, 95.2 mph EV, 12.5% barrels. Boyd RHB split +1.20, HR risk 0.93. park/weather net drag (-11%).""", blast="good", contact={'stars': 5, 'k': 16.3, 'batterK': 16.3, 'batterWhiff': 22.0, 'pitcherK': 15.4}),
            row("Christian Yelich", "L", "+870", 70, "⭐", ["vs Boyd"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 90.7 mph EV, 37.5% barrels. Boyd LHB split -1.04, HR risk 0.93. tough split lane (-1.04); park/weather net drag (-11%).""", blast="good", contact={'stars': 4, 'k': 18.4, 'batterK': 21.5, 'batterWhiff': 26.1, 'pitcherK': 15.4}),
            row("Garrett Mitchell", "L", "N/A", 68, "", ["vs Boyd"], """0 HR, 99.2 mph EV. Boyd LHB split -1.04, HR risk 0.93. tough split lane (-1.04); park/weather net drag (-11%).""", blast="good", contact={'stars': 3, 'k': 20.4, 'batterK': 28.1, 'batterWhiff': 31.2, 'pitcherK': 15.4}),
            row("Andrew Vaughn", "R", "+570", 70, "", ["vs Boyd"], """0 HR, 92.0 mph EV. Boyd RHB split +1.20, HR risk 0.93. park/weather net drag (-11%); limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 16.4, 'batterK': 17.5, 'batterWhiff': 17.9, 'pitcherK': 15.4}),
            row("Pete Crow Armstrong", "L", "+390", 83, "⭐", ["vs Gasser"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.6 mph EV, 12.5% barrels. Gasser LHB split -0.21, HR risk 0.35. slight split headwind (-0.21); park/weather net drag (-11%).""", blast="good", contact={'stars': 3, 'k': 20.4, 'batterK': 18.9, 'batterWhiff': 20.8, 'pitcherK': 22.1}),
            row("Michael Conforto", "L", "N/A", 76, "💎", ["vs Gasser"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.6 mph EV, 25.0% barrels. Gasser LHB split -0.21, HR risk 0.35. slight split headwind (-0.21); park/weather net drag (-11%).""", blast="good", contact={'stars': 3, 'k': 21.8, 'batterK': 23.2, 'batterWhiff': 22.6, 'pitcherK': 22.1}),
            row("Seiya Suzuki", "R", "+497", 72, "", ["vs Gasser"], """1 HR, 1 near-HR, 87.3 mph EV, 12.5% barrels. Gasser RHB split +0.31, HR risk 0.35. park/weather net drag (-11%); lighter EV form (87.3 mph).""", blast="good", contact={'stars': 3, 'k': 20.3, 'batterK': 20.0, 'batterWhiff': 18.2, 'pitcherK': 22.1}),
            row("Tyrone Taylor", "R", "+750", 69, "", ["vs Gasser"], """1 HR, 1 near-HR, 91.5 mph EV, 12.5% barrels. Gasser RHB split +0.31, HR risk 0.35. park/weather net drag (-11%).""", blast="good", contact={'stars': 4, 'k': 18.0, 'batterK': 11.3, 'batterWhiff': 12.0, 'pitcherK': 22.1}),
            row("Carson Kelly", "R", "+620", 71, "", ["vs Gasser"], """1 HR, 1 near-HR, 89.8 mph EV, 12.5% barrels. Gasser RHB split +0.31, HR risk 0.35. park/weather net drag (-11%).""", blast="good", contact={'stars': 3, 'k': 20.4, 'batterK': 18.8, 'batterWhiff': 20.1, 'pitcherK': 22.1}),
            row("Miguel Amaya", "R", "N/A", 64, "", ["vs Gasser"], """1 HR, 2 near-HR, 87.6 mph EV, 12.5% barrels. Gasser RHB split +0.31, HR risk 0.35. park/weather net drag (-11%); lighter EV form (87.6 mph).""", blast="good", contact={'stars': 2, 'k': 25.3, 'batterK': 33.3, 'batterWhiff': 31.8, 'pitcherK': 22.1}),
        ],
    },
    {
        "title": "CIN @ LAD - Chase Burns (R, CIN) vs Emmet Sheehan (R, LAD)",
        "kLines": {"Burns": {"k": 5.9, "lo": 4, "hi": 8, "bf": 22.2, "matchupK": 26.7, "ownK": 28.3}, "Sheehan": {"k": 5.9, "lo": 4, "hi": 8, "bf": 20.9, "matchupK": 28.2, "ownK": 28.9}},
        "description": "Tail key data: Park boost +21% (stadium +18%, weather +3%). Burns (HR risk -0.16, vs LHB +0.81, vs RHB -1.16). Sheehan (season BAA .247).",
        "rows": [
            row("Max Muncy", "L", "+421", 76, "⭐", ["vs Burns"], """Worst Pickz Favorite. 0 HR, 94.5 mph EV, 25.0% barrels. Burns LHB split +0.81, HR risk -0.16. pitcher risk below avg (-0.16); limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 27.6, 'batterK': 26.8, 'batterWhiff': 30.4, 'pitcherK': 28.3}),
            row("Mookie Betts", "R", "+560", 56, "", ["vs Burns"], """0 HR, 94.6 mph EV. Burns RHB split -1.16, HR risk -0.16. tough split lane (-1.16); pitcher risk below avg (-0.16).""", blast="good", contact={'stars': 4, 'k': 18.6, 'batterK': 9.7, 'batterWhiff': 12.5, 'pitcherK': 28.3}),
            row("Kyle Tucker", "L", "+600", 70, "", ["vs Burns"], """1 HR, 1 near-HR, 90.1 mph EV, 12.5% barrels. Burns LHB split +0.81, HR risk -0.16. pitcher risk below avg (-0.16).""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 11.1, 'batterWhiff': 20.1, 'pitcherK': 28.3}),
            row("Alex Freeland", "S", "+900", 58, "", ["vs Burns"], """0 HR, 88.8 mph EV, 12.5% barrels. Burns SHB→LHB split +0.81, HR risk -0.16. pitcher risk below avg (-0.16); limited recent HR events.""", contact={'stars': 1, 'k': 29.0, 'batterK': 34.0, 'batterWhiff': 35.4, 'pitcherK': 28.3}),
            row("Tyler Stephenson", "R", "+546", 87, "🌕 💣 💎", ["vs Sheehan"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.9 mph EV, 25.0% barrels. limited split/risk sample.""", blast="high", contact={'stars': 1, 'k': 31.2, 'batterK': 37.2, 'batterWhiff': 34.0, 'pitcherK': 28.9}),
            row("JJ Bleday", "L", "+500", 81, "💎", ["vs Sheehan"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.8 mph EV, 37.5% barrels. limited split/risk sample.""", blast="good", contact={'stars': 2, 'k': 26.5, 'batterK': 24.7, 'batterWhiff': 27.1, 'pitcherK': 28.9}),
            row("Matt McLain", "R", "+680", 74, "⭐", ["vs Sheehan"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 91.6 mph EV, 12.5% barrels. limited split/risk sample.""", blast="good", contact={'stars': 2, 'k': 26.8, 'batterK': 26.2, 'batterWhiff': 26.3, 'pitcherK': 28.9}),
            row("Elly De La Cruz", "S", "+500", 83, "⭐", ["vs Sheehan"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.4 mph EV, 25.0% barrels. limited split/risk sample; limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 28.6, 'batterK': 30.5, 'batterWhiff': 26.9, 'pitcherK': 28.9}),
        ],
    },
    {
        "title": "CLE @ BAL - Joey Cantillo (L, CLE) vs Trevor Rogers (L, BAL)",
        "kLines": {"Cantillo": {"k": 5.2, "lo": 4, "hi": 7, "bf": 21.2, "matchupK": 24.6, "ownK": 24.0}, "Rogers": {"k": 5.6, "lo": 4, "hi": 7, "bf": 23.0, "matchupK": 24.5, "ownK": 27.9}},
        "description": "Tail key data: Park boost -17% (stadium -8%, weather -9%). Cantillo (HR risk -0.60, vs LHB -0.29, vs RHB -0.29). Rogers (HR risk 0.32, vs LHB -1.36, vs RHB +0.66).",
        "rows": [
            row("Pete Alonso", "R", "+410", 80, "⭐", ["vs Cantillo"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.9 mph EV, 37.5% barrels. Cantillo RHB split -0.29, HR risk -0.60. slight split headwind (-0.29); pitcher suppresses HR (-0.60).""", blast="good", contact={'stars': 2, 'k': 24.7, 'batterK': 24.7, 'batterWhiff': 30.0, 'pitcherK': 24.0}),
            row("Colton Cowser", "L", "+525", 57, "", ["vs Cantillo"], """1 HR, 1 near-HR, 88.3 mph EV, 12.5% barrels. Cantillo LHB split -0.29, HR risk -0.60. slight split headwind (-0.29); pitcher suppresses HR (-0.60).""", blast="good", contact={'stars': 2, 'k': 25.1, 'batterK': 31.0, 'batterWhiff': 28.0, 'pitcherK': 24.0}),
            row("Coby Mayo", "R", "+582", 70, "⭐", ["vs Cantillo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 87.9 mph EV, 12.5% barrels. Cantillo RHB split -0.29, HR risk -0.60. slight split headwind (-0.29); pitcher suppresses HR (-0.60).""", blast="good", contact={'stars': 2, 'k': 24.8, 'batterK': 27.0, 'batterWhiff': 28.4, 'pitcherK': 24.0}),
            row("Patrick Bailey", "S", "+650", 62, "", ["vs Rogers"], """0 HR, 96.0 mph EV. Rogers SHB→RHB split +0.66, HR risk 0.32. park/weather net drag (-17%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.9, 'batterK': 22.4, 'batterWhiff': 22.9, 'pitcherK': 27.9}),
            row("David Fry", "R", "+730", 51, "", ["vs Rogers"], """0 HR, 89.8 mph EV. Rogers RHB split +0.66, HR risk 0.32. park/weather net drag (-17%); limited recent HR events.""", contact={'stars': 2, 'k': 26.2, 'batterK': 28.2, 'batterWhiff': 26.2, 'pitcherK': 27.9}),
        ],
    },
    {
        "title": "LAA @ BOS - Grayson Rodriguez (R, LAA) vs Brayan Bello (R, BOS)",
        "kLines": {"Rodriguez": {"k": 4.7, "lo": 3, "hi": 6, "bf": 21.7, "matchupK": 21.8, "ownK": 22.8}, "Bello": {"k": 4.5, "lo": 3, "hi": 6, "bf": 22.5, "matchupK": 20.0, "ownK": 17.7}},
        "description": "Tail key data: Park boost -2% (stadium -8%, weather +6%). Rodriguez (HR risk 0.26, vs LHB +0.93, vs RHB -0.61). Bello (BAA vs LHB .282, vs RHB .288, HR/9 1.01).",
        "rows": [
            row("Roman Anthony", "L", "+570", 85, "", ["vs Rodriguez"], """1 HR, 2 near-HR, 93.4 mph EV, 25.0% barrels. Rodriguez LHB split +0.93, HR risk 0.26. park suppresses carry (-8%).""", blast="good", contact={'stars': 3, 'k': 23.7, 'batterK': 25.6, 'batterWhiff': 25.9, 'pitcherK': 22.8}),
            row("Mickey Gasper", "S", "+630", 91, "⭐ 🌕 💣", ["vs Rodriguez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.5 mph EV, 25.0% barrels. Rodriguez SHB→LHB split +0.93, HR risk 0.26. park suppresses carry (-8%).""", blast="high", contact={'stars': 4, 'k': 17.5, 'batterK': 9.2, 'batterWhiff': 15.0, 'pitcherK': 22.8}),
            row("Jarren Duran", "L", "+630", 72, "", ["vs Rodriguez"], """0 HR, 93.5 mph EV. Rodriguez LHB split +0.93, HR risk 0.26. park suppresses carry (-8%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.2, 'batterK': 23.3, 'batterWhiff': 32.4, 'pitcherK': 22.8}),
            row("Zach Neto", "R", "+520", 78, "", ["vs Bello"], """1 HR, 1 near-HR, 95.9 mph EV, 12.5% barrels. limited split/risk sample; park suppresses carry (-8%).""", blast="good", contact={'stars': 3, 'k': 22.0, 'batterK': 25.8, 'batterWhiff': 29.6, 'pitcherK': 17.7}),
            row("Moises Ballesteros", "L", "+1040", 72, "💎", ["vs Bello"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.6 mph EV, 12.5% barrels. limited split/risk sample; park suppresses carry (-8%).""", blast="good", contact={'stars': 3, 'k': 22.4, 'batterK': 27.2, 'batterWhiff': 30.5, 'pitcherK': 17.7}),
        ],
    },
    {
        "title": "MIN @ DET - Connor Prielipp (L, MIN) vs Troy Melton (R, DET)",
        "kLines": {"Prielipp": {"k": 6.1, "lo": 4, "hi": 8, "bf": 22.4, "matchupK": 27.3, "ownK": 27.7}, "Melton": {"k": 4.2, "lo": 3, "hi": 6, "bf": 23.5, "matchupK": 17.7, "ownK": 18.8}},
        "description": "Tail key data: Park boost -14% (stadium -10%, weather -4%). Prielipp (BAA vs LHB .287, vs RHB .246, HR/9 1.12). Melton (HR risk 0.39, vs LHB +0.88, vs RHB -0.24).",
        "rows": [
            row("Riley Greene", "L", "+470", 76, "🌕 💣", ["vs Prielipp"], """2 HR, 2 near-HR, 90.4 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-14%).""", blast="high", contact={'stars': 2, 'k': 27.3, 'batterK': 26.4, 'batterWhiff': 29.9, 'pitcherK': 27.7}),
            row("Gleyber Torres", "R", "+920", 64, "", ["vs Prielipp"], """0 HR, 1 near-HR, 94.4 mph EV, 25.0% barrels. limited split/risk sample; park/weather net drag (-14%).""", blast="good", contact={'stars': 3, 'k': 23.1, 'batterK': 19.0, 'batterWhiff': 20.2, 'pitcherK': 27.7}),
            row("Kody Clemens", "L", "+424", 81, "⭐", ["vs Melton"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.0 mph EV, 12.5% barrels. Melton LHB split +0.88, HR risk 0.39. park/weather net drag (-14%).""", blast="good", contact={'stars': 4, 'k': 18.9, 'batterK': 19.8, 'batterWhiff': 20.4, 'pitcherK': 18.8}),
            row("Trevor Larnach", "L", "+650", 72, "", ["vs Melton"], """0 HR, 1 near-HR, 93.7 mph EV, 12.5% barrels. Melton LHB split +0.88, HR risk 0.39. park/weather net drag (-14%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.8, 'batterK': 21.7, 'batterWhiff': 33.3, 'pitcherK': 18.8}),
            row("Ryan Jeffers", "R", "+425", 91, "🌕 💣", ["vs Melton"], """2 HR, 3 near-HR, 96.2 mph EV, 12.5% barrels. Melton RHB split -0.24, HR risk 0.39. slight split headwind (-0.24); park/weather net drag (-14%).""", blast="high", contact={'stars': 5, 'k': 16.7, 'batterK': 16.7, 'batterWhiff': 12.0, 'pitcherK': 18.8}),
            row("Royce Lewis", "R", "+490", 62, "", ["vs Melton"], """0 HR, 1 near-HR, 93.4 mph EV, 12.5% barrels. Melton RHB split -0.24, HR risk 0.39. slight split headwind (-0.24); park/weather net drag (-14%).""", blast="good", contact={'stars': 4, 'k': 19.5, 'batterK': 17.5, 'batterWhiff': 26.6, 'pitcherK': 18.8}),
        ],
    },
    {
        "title": "NYM @ MIA - Jonah Tong (R, NYM) vs Eury Perez (R, MIA)",
        "kLines": {"Tong": {"k": 4.7, "lo": 3, "hi": 6, "bf": 21.6, "matchupK": 22.0, "ownK": 20.6}, "Perez": {"k": 5.3, "lo": 4, "hi": 7, "bf": 22.2, "matchupK": 23.9, "ownK": 23.7}},
        "description": "Tail key data: Park boost -12% (stadium -12%, weather +0%). Tong (HR risk -0.24, vs LHB -1.24, vs RHB +1.54). Perez (HR risk 0.82, vs LHB +0.63, vs RHB +0.62).",
        "rows": [
            row("Heriberto Hernandez", "R", "+523", 88, "⭐ 🌕 💣", ["vs Tong"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.3 mph EV, 12.5% barrels. Tong RHB split +1.54, HR risk -0.24. pitcher risk below avg (-0.24); park/weather net drag (-12%).""", blast="high", contact={'stars': 3, 'k': 23.9, 'batterK': 26.1, 'batterWhiff': 30.5, 'pitcherK': 20.6}),
            row("Agustin Ramirez", "R", "+465", 61, "", ["vs Tong"], """1 HR, 1 near-HR, 90.4 mph EV, 12.5% barrels. Tong RHB split +1.54, HR risk -0.24. pitcher risk below avg (-0.24); park/weather net drag (-12%).""", blast="good", contact={'stars': 3, 'k': 21.8, 'batterK': 23.3, 'batterWhiff': 24.1, 'pitcherK': 20.6}),
            row("Brett Baty", "L", "+850", 90, "🌕 💣 💎", ["vs Perez"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 97.5 mph EV, 37.5% barrels. Perez LHB split +0.63, HR risk 0.82. park/weather net drag (-12%).""", blast="high", contact={'stars': 2, 'k': 25.5, 'batterK': 26.3, 'batterWhiff': 33.9, 'pitcherK': 23.7}),
            row("Juan Soto", "L", "+346", 89, "🌕 💣", ["vs Perez"], """1 HR, 2 near-HR, 93.6 mph EV, 12.5% barrels. Perez LHB split +0.63, HR risk 0.82. park/weather net drag (-12%).""", blast="good", contact={'stars': 3, 'k': 21.1, 'batterK': 15.7, 'batterWhiff': 24.3, 'pitcherK': 23.7}),
            row("Francisco Lindor", "S", "+470", 81, "⭐", ["vs Perez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.2 mph EV, 12.5% barrels. Perez SHB→LHB split +0.63, HR risk 0.82. park/weather net drag (-12%).""", blast="good", contact={'stars': 3, 'k': 22.9, 'batterK': 21.3, 'batterWhiff': 25.9, 'pitcherK': 23.7}),
            row("Bo Bichette", "R", "+880", 71, "", ["vs Perez"], """1 HR, 1 near-HR, 85.0 mph EV, 12.5% barrels. Perez RHB split +0.62, HR risk 0.82. park/weather net drag (-12%); lighter EV form (85.0 mph).""", blast="good", contact={'stars': 3, 'k': 21.5, 'batterK': 19.3, 'batterWhiff': 21.2, 'pitcherK': 23.7}),
        ],
    },
    {
        "title": "STL @ SF - Michael McGreevy (R, STL) vs Logan Webb (R, SF)",
        "kLines": {"McGreevy": {"k": 4.1, "lo": 2, "hi": 6, "bf": 22.5, "matchupK": 18.1, "ownK": 17.1}, "Webb": {"k": 5.3, "lo": 4, "hi": 7, "bf": 24.2, "matchupK": 21.7, "ownK": 20.3}},
        "description": "Tail key data: Park boost -18% (stadium -19%, weather +1%). McGreevy (HR risk 0.46, vs LHB +1.01, vs RHB -0.33). Webb (HR risk -0.78, vs LHB -0.20, vs RHB -0.51).",
        "rows": [
            row("Rafael Devers", "L", "+362", 95, "🚀 ⭐ 🌕 💣", ["vs McGreevy"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 104.2 mph EV, 50.0% barrels. McGreevy LHB split +1.01, HR risk 0.46. park/weather net drag (-18%).""", blast="high", contact={'stars': 4, 'k': 19.4, 'batterK': 19.8, 'batterWhiff': 28.6, 'pitcherK': 17.1}),
            row("Grant McCray", "L", "N/A", 84, "", ["vs McGreevy"], """1 HR, 2 near-HR, 92.5 mph EV, 25.0% barrels. McGreevy LHB split +1.01, HR risk 0.46. park/weather net drag (-18%).""", blast="good", contact={'stars': 3, 'k': 22.1, 'batterK': 30.0, 'batterWhiff': 34.0, 'pitcherK': 17.1}),
            row("Andrew Knizner", "R", "N/A", 63, "", ["vs McGreevy"], """0 HR, 1 near-HR, 92.0 mph EV, 20.0% barrels. McGreevy RHB split -0.33, HR risk 0.46. slight split headwind (-0.33); park/weather net drag (-18%).""", blast="good", contact={'stars': 3, 'k': 20.0, 'batterK': 22.0, 'batterWhiff': 27.9, 'pitcherK': 17.1}),
            row("Bryce Eldridge", "L", "+571", 63, "", ["vs McGreevy"], """0 HR, 83.6 mph EV. McGreevy LHB split +1.01, HR risk 0.46. park/weather net drag (-18%); limited recent HR events.""", contact={'stars': 3, 'k': 20.6, 'batterK': 25.6, 'batterWhiff': 25.9, 'pitcherK': 17.1}),
            row("Alec Burleson", "L", "+725", 59, "⭐", ["vs Webb"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 90.8 mph EV, 25.0% barrels. Webb LHB split -0.20, HR risk -0.78. slight split headwind (-0.20); pitcher suppresses HR (-0.78).""", blast="good", contact={'stars': 3, 'k': 21.3, 'batterK': 22.5, 'batterWhiff': 25.5, 'pitcherK': 20.3}),
            row("Joshua Baez", "R", "+790", 56, "", ["vs Webb"], """0 HR, 95.7 mph EV. Webb RHB split -0.51, HR risk -0.78. tough split lane (-0.51); pitcher suppresses HR (-0.78).""", blast="good", contact={'stars': 2, 'k': 26.2, 'batterK': 33.8, 'batterWhiff': 37.3, 'pitcherK': 20.3}),
            row("Leonardo Bernal", "S", "+1060", 64, "", ["vs Webb"], """1 HR, 1 near-HR, 96.0 mph EV, 14.3% barrels. Webb SHB→LHB split -0.20, HR risk -0.78. slight split headwind (-0.20); pitcher suppresses HR (-0.78).""", blast="good"),
            row("Thomas Saggese", "R", "+1300", 48, "", ["vs Webb"], """0 HR, 1 near-HR, 90.8 mph EV. Webb RHB split -0.51, HR risk -0.78. tough split lane (-0.51); pitcher suppresses HR (-0.78).""", contact={'stars': 3, 'k': 20.8, 'batterK': 19.2, 'batterWhiff': 25.0, 'pitcherK': 20.3}),
        ],
    },
    {
        "title": "TOR @ ATH - Dylan Cease (R, TOR) vs Jacob Lopez (L, ATH)",
        "kLines": {"Cease": {"k": 7.3, "lo": 6, "hi": 9, "bf": 23.5, "matchupK": 30.9, "ownK": 32.5}, "Lopez": {"k": 5.1, "lo": 3, "hi": 7, "bf": 21.6, "matchupK": 23.4, "ownK": 26.5}},
        "description": "Tail key data: Park boost +27% (stadium +29%, weather -2%). Cease (HR risk -0.60, vs LHB +0.00, vs RHB -0.60). Lopez (HR risk 0.30, vs LHB -0.69, vs RHB +0.47).",
        "rows": [
            row("Lawrence Butler", "L", "+600", 85, "⭐ 🌕 💣", ["vs Cease"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.7 mph EV, 25.0% barrels. Cease LHB split +0.00, HR risk -0.60. pitcher suppresses HR (-0.60).""", blast="high", contact={'stars': 1, 'k': 32.4, 'batterK': 34.1, 'batterWhiff': 28.0, 'pitcherK': 32.5}),
            row("Zack Gelof", "R", "+520", 77, "", ["vs Cease"], """1 HR, 2 near-HR, 90.8 mph EV, 25.0% barrels. Cease RHB split -0.60, HR risk -0.60. tough split lane (-0.60); pitcher suppresses HR (-0.60).""", blast="good", contact={'stars': 1, 'k': 30.8, 'batterK': 25.0, 'batterWhiff': 33.9, 'pitcherK': 32.5}),
            row("Jeff McNeil", "L", "+890", 80, "🌕 💣", ["vs Cease"], """2 HR, 2 near-HR, 92.2 mph EV, 12.5% barrels. Cease LHB split +0.00, HR risk -0.60. pitcher suppresses HR (-0.60).""", blast="high", contact={'stars': 3, 'k': 21.0, 'batterK': 9.0, 'batterWhiff': 13.5, 'pitcherK': 32.5}),
            row("Kazuma Okamoto", "R", "+319", 89, "⭐ 🌕 💣", ["vs Lopez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 92.7 mph EV, 25.0% barrels. Lopez RHB split +0.47, HR risk 0.30.""", blast="good", contact={'stars': 2, 'k': 25.5, 'batterK': 21.7, 'batterWhiff': 30.7, 'pitcherK': 26.5}),
            row("George Springer", "R", "+407", 67, "", ["vs Lopez"], """0 HR, 96.8 mph EV. Lopez RHB split +0.47, HR risk 0.30. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.5, 'batterK': 18.9, 'batterWhiff': 24.0, 'pitcherK': 26.5}),
            row("Alejandro Kirk", "R", "+517", 68, "💎", ["vs Lopez"], """Worst Pickz Hidden Gem. 0 HR, 92.3 mph EV. Lopez RHB split +0.47, HR risk 0.30. limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 18.7, 'batterK': 10.3, 'batterWhiff': 14.1, 'pitcherK': 26.5}),
            row("Jesus Sanchez", "L", "N/A", 55, "", ["vs Lopez"], """0 HR, 90.2 mph EV. Lopez LHB split -0.69, HR risk 0.30. tough split lane (-0.69); limited recent HR events.""", contact={'stars': 1, 'k': 27.9, 'batterK': 26.5, 'batterWhiff': 37.9, 'pitcherK': 26.5}),
        ],
    },
    {
        "title": "WSH @ SD - Jake Irvin 🧤 (R, WSH) vs Nick Pivetta (R, SD)",
        "kLines": {"Irvin": {"k": 4.6, "lo": 3, "hi": 6, "bf": 21.4, "matchupK": 21.4, "ownK": 21.2}, "Pivetta": {"k": 5.3, "lo": 4, "hi": 7, "bf": 19.4, "matchupK": 27.1, "ownK": 31.3}},
        "description": "Tail key data: Park boost -5% (stadium -6%, weather +1%). Irvin 🧤 (HR risk 1.56, vs LHB +1.40, vs RHB +0.82). Pivetta (HR risk -1.87, vs LHB -0.52, vs RHB -1.47).",
        "rows": [
            row("Fernando Tatis Jr.", "R", "+376", 94, "🌕 💣", ["vs Irvin"], """1 HR, 1 near-HR, 97.2 mph EV, 40.0% barrels. Irvin RHB split +0.82, HR risk 1.56. park/weather net drag (-5%).""", blast="high", contact={'stars': 4, 'k': 19.4, 'batterK': 15.9, 'batterWhiff': 21.9, 'pitcherK': 21.2}),
            row("Jackson Merrill", "L", "+390", 92, "🚀 🌕 💣", ["vs Irvin"], """0 HR, 103.8 mph EV, 40.0% barrels. Irvin LHB split +1.40, HR risk 1.56. park/weather net drag (-5%); limited recent HR events.""", blast="high", contact={'stars': 3, 'k': 23.0, 'batterK': 23.8, 'batterWhiff': 29.9, 'pitcherK': 21.2}),
            row("Manny Machado", "R", "+426", 83, "", ["vs Irvin"], """1 HR, 1 near-HR, 86.3 mph EV, 40.0% barrels. Irvin RHB split +0.82, HR risk 1.56. park/weather net drag (-5%); lighter EV form (86.3 mph).""", blast="good", contact={'stars': 3, 'k': 20.4, 'batterK': 18.2, 'batterWhiff': 23.9, 'pitcherK': 21.2}),
            row("Daylen Lile", "L", "+532", 75, "⭐ 🌕 💣", ["vs Pivetta"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.0 mph EV, 25.0% barrels. Pivetta LHB split -0.52, HR risk -1.87. tough split lane (-0.52); pitcher suppresses HR (-1.87).""", blast="high", contact={'stars': 2, 'k': 25.1, 'batterK': 24.1, 'batterWhiff': 22.8, 'pitcherK': 31.3}),
            row("James Wood", "L", "+360", 65, "", ["vs Pivetta"], """0 HR, 92.8 mph EV, 12.5% barrels. Pivetta LHB split -0.52, HR risk -1.87. tough split lane (-0.52); pitcher suppresses HR (-1.87).""", blast="good", contact={'stars': 2, 'k': 25.1, 'batterK': 22.3, 'batterWhiff': 25.7, 'pitcherK': 31.3}),
            row("Keibert Ruiz", "S", "+700", 42, "", ["vs Pivetta"], """0 HR, 1 near-HR, 95.5 mph EV. Pivetta SHB→LHB split -0.52, HR risk -1.87. tough split lane (-0.52); pitcher suppresses HR (-1.87).""", blast="good", contact={'stars': 3, 'k': 20.2, 'batterK': 9.7, 'batterWhiff': 16.8, 'pitcherK': 31.3}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-07")

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

    out = ROOT / '_games-0907.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
