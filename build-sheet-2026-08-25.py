#!/usr/bin/env python3
"""Generate games[] block for 2026-08-25 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "A.J. Ewing (L)",
    "Bryce Harper (L)",
    "Cal Raleigh (S)",
    "Christopher Morel (R)",
    "Coby Mayo (R)",
    "Corey Seager (L)",
    "Daylen Lile (L)",
    "Drake Baldwin (L)",
    "Elly De La Cruz (S)",
    "Esmerlyn Valdez (R)",
    "Fernando Tatis Jr. (R)",
    "Freddie Freeman (L)",
    "Gabriel Moreno (R)",
    "JJ Bleday (L)",
    "JJ Wetherholt (L)",
    "JT Realmuto (R)",
    "Jackson Merrill (L)",
    "Jo Adell (R)",
    "Kyle Schwarber (L)",
    "Luis Garcia Jr. (L)",
    "Matt Olson (L)",
    "Oneil Cruz (L)",
    "Rafael Devers (L)",
    "Spencer Jones (L)",
    "Yordan Alvarez (L)",
    "Zach Neto (R)",
}

GEMS = {
    "Christian Franklin (R)",
    "Daulton Varsho (L)",
    "Eduardo Valencia (R)",
    "Hunter Feduccia (L)",
    "Jimmy Crooks (L)",
    "Jonathan Aranda (L)",
    "Jordan Beck (R)",
    "Joshua Baez (R)",
    "Kevin McGonigle (L)",
    "Kyle Stowers (L)",
    "Lars Nootbaar (L)",
    "Michael Busch (L)",
    "Michael Conforto (L)",
    "Mickey Gasper (S)",
    "Nelson Velazquez (R)",
    "Tim Tawa (R)",
    "Tyler Stephenson (R)",
    "Zack Gelof (R)",
}

PLAYER_TEAMS = {
    "A.J. Ewing (L)": "NYM",
    "Agustin Ramirez (R)": "MIA",
    "Alan Roden (L)": "MIN",
    "Alec Burleson (L)": "STL",
    "Alejandro Kirk (R)": "TOR",
    "Andres Chaparro (R)": "WSH",
    "Andrew Vaughn (R)": "MIL",
    "Ben Rice (L)": "NYY",
    "Bo Bichette (R)": "NYM",
    "Bobby Witt Jr. (R)": "KC",
    "Brady House (R)": "WSH",
    "Brandon Lowe (L)": "PIT",
    "Brayan Rocchio (S)": "CLE",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Harper (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Carson Benge (L)": "NYM",
    "Carter Jensen (L)": "KC",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Christian Franklin (R)": "BAL",
    "Christian Moore (R)": "LAA",
    "Christian Yelich (L)": "MIL",
    "Christopher Morel (R)": "NYM",
    "Coby Mayo (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Daulton Varsho (L)": "HOU",
    "Daylen Lile (L)": "WSH",
    "Dominic Canzone (L)": "SEA",
    "Donovan Walton (L)": "ATH",
    "Drake Baldwin (L)": "ATL",
    "Eduardo Valencia (R)": "DET",
    "Elias Diaz (R)": "TEX",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Ezequiel Duran (R)": "TEX",
    "Fernando Tatis Jr. (R)": "SD",
    "Freddie Freeman (L)": "LAD",
    "Gabriel Moreno (R)": "ARI",
    "Gleyber Torres (R)": "DET",
    "Griffin Conine (L)": "MIA",
    "Hao-Yu Lee (R)": "DET",
    "Hector Rodriguez (L)": "CIN",
    "Heliot Ramos (R)": "NYY",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "LAD",
    "Ildemaro Vargas (S)": "ARI",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "JT Realmuto (R)": "PHI",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jarren Duran (L)": "BOS",
    "Jeff McNeil (L)": "ATH",
    "Jeremy Pena (R)": "HOU",
    "Jesus Sanchez (L)": "TOR",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "CLE",
    "Joc Pederson (L)": "TEX",
    "Jonathan Aranda (L)": "TB",
    "Jordan Beck (R)": "COL",
    "Jose Siri (R)": "LAA",
    "Jose Tena (L)": "WSH",
    "Joshua Baez (R)": "STL",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kevin McGonigle (L)": "DET",
    "Kyle Isbel (L)": "KC",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lars Nootbaar (L)": "ARI",
    "Lawrence Butler (L)": "ATH",
    "Luis Garcia Jr. (L)": "NYY",
    "Luis Torrens (R)": "NYM",
    "Luke Keaschall (R)": "MIN",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Max Muncy (R)": "ATH",
    "Michael Busch (L)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Mickey Gasper (S)": "BOS",
    "Miguel Vargas (R)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Oneil Cruz (L)": "PIT",
    "Otto Lopez (R)": "MIA",
    "Patrick Bailey (S)": "CLE",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randy Arozarena (R)": "SEA",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan Jeffers (R)": "MIN",
    "Ryan Vilade (R)": "TB",
    "Sal Stewart (R)": "CIN",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Taylor Trammell (L)": "HOU",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Travis Bazzana (L)": "CLE",
    "Trent Grisham (L)": "NYY",
    "Tristan Peters (L)": "CWS",
    "Ty France (R)": "SD",
    "Tyler Stephenson (R)": "CIN",
    "Vinnie Pasquantino (L)": "KC",
    "Willi Castro (S)": "COL",
    "William Contreras (R)": "MIL",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Xander Bogaerts (R)": "SD",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("CLE @ LAA", "Williams"),
    ("HOU @ NYY", "Warren"),
    ("TB @ DET", "Seymour"),
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
        "title": "BAL @ STL - Chris Bassitt (R, BAL) vs Matthew Liberatore (L, STL)",
        "description": "Tail key data: Park boost -14% (stadium -8%, weather -5%). Bassitt (HR risk -0.38, vs LHB +0.32, vs RHB -1.25). Liberatore (BAA vs LHB .296, vs RHB .275, HR/9 1.51).",
        "rows": [
            row("Joshua Baez", "R", "+600", 58, "💎", ["vs Bassitt"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 97.0 mph EV. Bassitt RHB split -1.25, HR risk -0.38. tough split lane (-1.25); pitcher risk below avg (-0.38).""", blast="good"),
            row("Alec Burleson", "L", "+535", 58, "", ["vs Bassitt"], """1 HR, 2 near-HR, 90.1 mph EV. Bassitt LHB split +0.32, HR risk -0.38. pitcher risk below avg (-0.38); park/weather net drag (-14%).""", blast="good"),
            row("Jimmy Crooks", "L", "+930", 58, "💎", ["vs Bassitt"], """Worst Pickz Hidden Gem. 0 HR, 95.0 mph EV. Bassitt LHB split +0.32, HR risk -0.38. pitcher risk below avg (-0.38); park/weather net drag (-14%).""", blast="good"),
            row("JJ Wetherholt", "L", "+770", 58, "⭐", ["vs Bassitt"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.3 mph EV. Bassitt LHB split +0.32, HR risk -0.38. pitcher risk below avg (-0.38); park/weather net drag (-14%).""", blast="good"),
            row("Coby Mayo", "R", "+495", 80, "⭐ 🌕 💣", ["vs Liberatore"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 98.4 mph EV. limited split/risk sample; park/weather net drag (-14%).""", blast="high"),
            row("Christian Franklin", "R", "+1500", 59, "💎", ["vs Liberatore"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.1 mph EV. limited split/risk sample; park/weather net drag (-14%).""", blast="good"),
            row("Christian Encarnacion-Strand", "R", "+620", 64, "", ["vs Liberatore"], """1 HR, 2 near-HR, 95.4 mph EV. limited split/risk sample; park/weather net drag (-14%).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ MIA - Payton Tolle (L, BOS) vs Tyler Phillips (R, MIA)",
        "description": "Tail key data: Park boost -14% (stadium -14%, weather +0%). Tolle (HR risk 0.00, vs LHB +0.71, vs RHB -0.05). Phillips (BAA vs LHB .268, vs RHB .223, HR/9 1.16).",
        "rows": [
            row("Kyle Stowers", "L", "+578", 58, "💎", ["vs Tolle"], """Worst Pickz Hidden Gem. 0 HR, 88.8 mph EV. Tolle LHB split +0.71, HR risk 0.00. park/weather net drag (-14%); limited recent HR events."""),
            row("Griffin Conine", "L", "N/A", 58, "", ["vs Tolle"], """0 HR, 91.3 mph EV. Tolle LHB split +0.71, HR risk 0.00. park/weather net drag (-14%); limited recent HR events."""),
            row("Heriberto Hernandez", "R", "+462", 58, "", ["vs Tolle"], """0 HR, 91.2 mph EV. Tolle RHB split -0.05, HR risk 0.00. slight split headwind (-0.05); park/weather net drag (-14%)."""),
            row("Otto Lopez", "R", "+920", 58, "", ["vs Tolle"], """0 HR, 87.9 mph EV. Tolle RHB split -0.05, HR risk 0.00. slight split headwind (-0.05); park/weather net drag (-14%)."""),
            row("Agustin Ramirez", "R", "+775", 58, "", ["vs Tolle"], """0 HR, 96.4 mph EV. Tolle RHB split -0.05, HR risk 0.00. slight split headwind (-0.05); park/weather net drag (-14%).""", blast="good"),
            row("Mickey Gasper", "S", "+1050", 72, "🌕 💣 💎", ["vs Phillips"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.2 mph EV. limited split/risk sample; park/weather net drag (-14%).""", blast="high"),
            row("Jarren Duran", "L", "+725", 58, "", ["vs Phillips"], """1 HR, 1 near-HR, 89.9 mph EV. limited split/risk sample; park/weather net drag (-14%).""", blast="good"),
            row("Wilyer Abreu", "L", "+450", 59, "", ["vs Phillips"], """0 HR, 1 near-HR, 96.0 mph EV. limited split/risk sample; park/weather net drag (-14%).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ ARI - Clay Holmes (R, CHC) vs Brandon Pfaadt (R, ARI)",
        "description": "Tail key data: Park boost -9% (stadium -9%, weather +0%). Holmes (HR risk -1.00, vs LHB -0.62, vs RHB -0.75). Pfaadt (HR risk -0.44, vs LHB +0.09, vs RHB -0.66).",
        "rows": [
            row("Lars Nootbaar", "L", "+870", 58, "💎", ["vs Holmes"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.6 mph EV. Holmes LHB split -0.62, HR risk -1.00. tough split lane (-0.62); pitcher suppresses HR (-1.00).""", blast="good"),
            row("Ildemaro Vargas", "S", "+1840", 58, "", ["vs Holmes"], """0 HR, 1 near-HR, 96.1 mph EV. Holmes SHB→LHB split -0.62, HR risk -1.00. tough split lane (-0.62); pitcher suppresses HR (-1.00).""", blast="good"),
            row("Gabriel Moreno", "R", "+1000", 58, "⭐", ["vs Holmes"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 94.3 mph EV. Holmes RHB split -0.75, HR risk -1.00. tough split lane (-0.75); pitcher suppresses HR (-1.00).""", blast="good"),
            row("Corbin Carroll", "L", "+525", 58, "", ["vs Holmes"], """0 HR, 97.3 mph EV. Holmes LHB split -0.62, HR risk -1.00. tough split lane (-0.62); pitcher suppresses HR (-1.00).""", blast="good"),
            row("Tim Tawa", "R", "+930", 58, "💎", ["vs Holmes"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 93.4 mph EV. Holmes RHB split -0.75, HR risk -1.00. tough split lane (-0.75); pitcher suppresses HR (-1.00).""", blast="good"),
            row("Michael Conforto", "L", "+680", 58, "💎", ["vs Pfaadt"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 87.8 mph EV. Pfaadt LHB split +0.09, HR risk -0.44. pitcher suppresses HR (-0.44); park/weather net drag (-9%).""", blast="good"),
            row("Michael Busch", "L", "+630", 58, "💎", ["vs Pfaadt"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 91.9 mph EV. Pfaadt LHB split +0.09, HR risk -0.44. pitcher suppresses HR (-0.44); park/weather net drag (-9%).""", blast="good"),
            row("Pete Crow Armstrong", "L", "+370", 59, "🌕 💣", ["vs Pfaadt"], """2 HR, 2 near-HR, 84.7 mph EV. Pfaadt LHB split +0.09, HR risk -0.44. pitcher suppresses HR (-0.44); park/weather net drag (-9%).""", blast="high"),
        ],
    },
    {
        "title": "CIN @ SF - Brady Singer (R, CIN) vs Adrian Houser (R, SF)",
        "description": "Tail key data: Park boost -23% (stadium -19%, weather -4%). Singer (HR risk 0.32, vs LHB +0.41, vs RHB +0.06). Houser (HR risk -0.67, vs LHB -0.11, vs RHB -0.66).",
        "rows": [
            row("Rafael Devers", "L", "+340", 65, "⭐", ["vs Singer"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.8 mph EV. Singer LHB split +0.41, HR risk 0.32. park/weather net drag (-23%).""", blast="good"),
            row("JJ Bleday", "L", "+524", 58, "⭐", ["vs Houser"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 89.6 mph EV. Houser LHB split -0.11, HR risk -0.67. slight split headwind (-0.11); pitcher suppresses HR (-0.67).""", blast="good"),
            row("Elly De La Cruz", "S", "+630", 58, "⭐", ["vs Houser"], """Worst Pickz Favorite. 0 HR, 99.2 mph EV. Houser SHB→LHB split -0.11, HR risk -0.67. slight split headwind (-0.11); pitcher suppresses HR (-0.67).""", blast="good"),
            row("Tyler Stephenson", "R", "+870", 58, "💎", ["vs Houser"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 88.4 mph EV. Houser RHB split -0.66, HR risk -0.67. tough split lane (-0.66); pitcher suppresses HR (-0.67).""", blast="good"),
            row("Sal Stewart", "R", "+790", 58, "", ["vs Houser"], """0 HR, 94.1 mph EV. Houser RHB split -0.66, HR risk -0.67. tough split lane (-0.66); pitcher suppresses HR (-0.67).""", blast="good"),
            row("Hector Rodriguez", "L", "+1150", 58, "", ["vs Houser"], """1 HR, 1 near-HR, 93.3 mph EV. Houser LHB split -0.11, HR risk -0.67. slight split headwind (-0.11); pitcher suppresses HR (-0.67).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ LAA - Gavin Williams 🧤 (R, CLE) vs Walbert Urena (R, LAA)",
        "description": "Tail key data: Park boost -2% (stadium -10%, weather +8%). Williams 🧤 (HR risk 1.00, vs LHB +0.29, vs RHB +1.37). Urena (HR risk -0.75, vs LHB -0.57, vs RHB -0.41).",
        "rows": [
            row("Zach Neto", "R", "+506", 85, "⭐", ["vs Williams"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.3 mph EV. Williams RHB split +1.37, HR risk 1.00. park suppresses carry (-10%).""", blast="good"),
            row("Jose Siri", "R", "+548", 89, "🌕 💣", ["vs Williams"], """1 HR, 2 near-HR, 94.5 mph EV. Williams RHB split +1.37, HR risk 1.00. park suppresses carry (-10%).""", blast="good"),
            row("Christian Moore", "R", "+870", 82, "", ["vs Williams"], """0 HR, 1 near-HR, 93.5 mph EV. Williams RHB split +1.37, HR risk 1.00. park suppresses carry (-10%); limited recent HR events.""", blast="good"),
            row("Jo Adell", "R", "+504", 58, "🚀 ⭐", ["vs Urena"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 100.4 mph EV. Urena RHB split -0.41, HR risk -0.75. tough split lane (-0.41); pitcher suppresses HR (-0.75).""", blast="good"),
            row("Patrick Bailey", "S", "+830", 58, "", ["vs Urena"], """1 HR, 1 near-HR, 86.6 mph EV. Urena SHB→RHB split -0.41, HR risk -0.75. tough split lane (-0.41); pitcher suppresses HR (-0.75).""", blast="good"),
            row("Brayan Rocchio", "S", "+1100", 58, "", ["vs Urena"], """0 HR, 92.5 mph EV. Urena SHB→RHB split -0.41, HR risk -0.75. tough split lane (-0.41); pitcher suppresses HR (-0.75).""", blast="good"),
            row("Travis Bazzana", "L", "+820", 58, "", ["vs Urena"], """0 HR, 86.9 mph EV. Urena LHB split -0.57, HR risk -0.75. tough split lane (-0.57); pitcher suppresses HR (-0.75)."""),
        ],
    },
    {
        "title": "COL @ WSH - Mason Adams (R, COL) vs Andrew Alvarez (L, WSH)",
        "description": "Tail key data: Park boost +11% (stadium +3%, weather +8%). Adams - MLB debut, no book. Alvarez (HR risk -1.05, vs LHB -0.22, vs RHB -0.84).",
        "rows": [
            row("Andres Chaparro", "R", "N/A", 66, "", ["vs Adams"], """1 HR, 1 near-HR, 92.8 mph EV. limited split/risk sample.""", blast="good"),
            row("Daylen Lile", "L", "N/A", 63, "⭐", ["vs Adams"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 89.5 mph EV. limited split/risk sample.""", blast="good"),
            row("Jose Tena", "L", "N/A", 66, "", ["vs Adams"], """1 HR, 1 near-HR, 92.5 mph EV. limited split/risk sample.""", blast="good"),
            row("Brady House", "R", "N/A", 63, "", ["vs Adams"], """0 HR, 95.4 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Jordan Beck", "R", "+820", 58, "💎", ["vs Alvarez"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.7 mph EV. Alvarez RHB split -0.84, HR risk -1.05. tough split lane (-0.84); pitcher suppresses HR (-1.05).""", blast="good"),
            row("Willi Castro", "S", "+810", 58, "", ["vs Alvarez"], """1 HR, 1 near-HR, 85.9 mph EV. Alvarez SHB→LHB split -0.22, HR risk -1.05. slight split headwind (-0.22); pitcher suppresses HR (-1.05).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ NYY - Ethan Pecko (R, HOU) vs Will Warren 🧤 (R, NYY)",
        "description": "Tail key data: Park boost +9% (stadium +4%, weather +5%). Pecko (BAA vs LHB .167, vs RHB .250). Warren 🧤 (HR risk 1.03, vs LHB +0.38, vs RHB +1.15).",
        "rows": [
            row("Luis Garcia Jr.", "L", "N/A", 67, "🚀 ⭐", ["vs Pecko"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 101.2 mph EV. limited split/risk sample.""", blast="good"),
            row("Ben Rice", "L", "+351", 58, "", ["vs Pecko"], """0 HR, 89.0 mph EV. limited split/risk sample; limited recent HR events."""),
            row("Trent Grisham", "L", "+335", 62, "", ["vs Pecko"], """1 HR, 1 near-HR, 91.4 mph EV. limited split/risk sample.""", blast="good"),
            row("Spencer Jones", "L", "+410", 58, "⭐", ["vs Pecko"], """Worst Pickz Favorite. 0 HR, 91.9 mph EV. limited split/risk sample; limited recent HR events."""),
            row("Heliot Ramos", "R", "N/A", 58, "", ["vs Pecko"], """0 HR, 1 near-HR, 89.0 mph EV. limited split/risk sample; limited recent HR events."""),
            row("Yordan Alvarez", "L", "+240", 79, "⭐", ["vs Warren"], """Worst Pickz Favorite. 0 HR, 99.4 mph EV. Warren LHB split +0.38, HR risk 1.03. limited recent HR events.""", blast="good"),
            row("Taylor Trammell", "L", "N/A", 75, "", ["vs Warren"], """0 HR, 92.6 mph EV. Warren LHB split +0.38, HR risk 1.03. limited recent HR events.""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 86, "🚀 💎", ["vs Warren"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 101.0 mph EV. Warren RHB split +1.15, HR risk 1.03. limited recent HR events.""", blast="good"),
            row("Jeremy Pena", "R", "+620", 82, "", ["vs Warren"], """0 HR, 1 near-HR, 92.2 mph EV. Warren RHB split +1.15, HR risk 1.03. limited recent HR events.""", blast="good"),
            row("Daulton Varsho", "L", "+569", 81, "💎", ["vs Warren"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.5 mph EV. Warren LHB split +0.38, HR risk 1.03.""", blast="good"),
        ],
    },
    {
        "title": "KC @ TOR - Seth Lugo (R, KC) vs Max Scherzer (R, TOR)",
        "description": "Tail key data: Park boost +0% (stadium +7%, weather -6%). Lugo (HR risk -0.59, vs LHB -0.37, vs RHB -0.33). Scherzer (HR risk 0.65, vs LHB +0.14, vs RHB +1.14).",
        "rows": [
            row("Jesus Sanchez", "L", "+820", 58, "", ["vs Lugo"], """0 HR, 1 near-HR, 94.5 mph EV. Lugo LHB split -0.37, HR risk -0.59. slight split headwind (-0.37); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Kazuma Okamoto", "R", "+379", 58, "", ["vs Lugo"], """0 HR, 92.3 mph EV. Lugo RHB split -0.33, HR risk -0.59. slight split headwind (-0.33); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Alejandro Kirk", "R", "+560", 58, "", ["vs Lugo"], """1 HR, 2 near-HR, 92.3 mph EV. Lugo RHB split -0.33, HR risk -0.59. slight split headwind (-0.33); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Bobby Witt Jr.", "R", "+357", 80, "", ["vs Scherzer"], """1 HR, 2 near-HR, 91.6 mph EV. Scherzer RHB split +1.14, HR risk 0.65. weather carry headwind (-6%).""", blast="good"),
            row("Kyle Isbel", "L", "+1020", 81, "🌕 💣", ["vs Scherzer"], """2 HR, 2 near-HR, 93.2 mph EV. Scherzer LHB split +0.14, HR risk 0.65. weather carry headwind (-6%).""", blast="high"),
            row("Vinnie Pasquantino", "L", "+555", 67, "", ["vs Scherzer"], """0 HR, 1 near-HR, 92.7 mph EV. Scherzer LHB split +0.14, HR risk 0.65. weather carry headwind (-6%); limited recent HR events.""", blast="good"),
            row("Carter Jensen", "L", "+376", 70, "", ["vs Scherzer"], """0 HR, 2 near-HR, 93.9 mph EV. Scherzer LHB split +0.14, HR risk 0.65. weather carry headwind (-6%).""", blast="good"),
            row("Jac Caglianone", "L", "+403", 70, "", ["vs Scherzer"], """0 HR, 1 near-HR, 96.1 mph EV. Scherzer LHB split +0.14, HR risk 0.65. weather carry headwind (-6%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "LAD @ ATL - Tyler Glasnow (R, LAD) vs Bryce Elder (R, ATL)",
        "description": "Tail key data: Park boost +7% (stadium -1%, weather +8%). Glasnow (HR risk 0.63, vs LHB -0.14, vs RHB +1.34). Elder (HR risk 0.38, vs LHB +0.43, vs RHB +0.12).",
        "rows": [
            row("Matt Olson", "L", "+334", 89, "🚀 ⭐ 🌕 💣", ["vs Glasnow"], """Worst Pickz Favorite. 2 HR, 5 near-HR, 102.0 mph EV. Glasnow LHB split -0.14, HR risk 0.63. slight split headwind (-0.14).""", blast="high"),
            row("Michael Harris II", "L", "+500", 68, "🚀", ["vs Glasnow"], """0 HR, 100.6 mph EV. Glasnow LHB split -0.14, HR risk 0.63. slight split headwind (-0.14); limited recent HR events.""", blast="good"),
            row("Drake Baldwin", "L", "+474", 75, "⭐", ["vs Glasnow"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.9 mph EV. Glasnow LHB split -0.14, HR risk 0.63. slight split headwind (-0.14).""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+481", 79, "", ["vs Glasnow"], """0 HR, 1 near-HR, 93.1 mph EV. Glasnow RHB split +1.34, HR risk 0.63. limited recent HR events.""", blast="good"),
            row("Teoscar Hernandez", "R", "+480", 63, "", ["vs Elder"], """0 HR, 2 near-HR, 91.2 mph EV. Elder RHB split +0.12, HR risk 0.38.""", blast="good"),
            row("Max Muncy", "L", "+350", 73, "", ["vs Elder"], """1 HR, 1 near-HR, 96.6 mph EV. Elder LHB split +0.43, HR risk 0.38.""", blast="good"),
            row("Shohei Ohtani", "L", "+233", 73, "", ["vs Elder"], """1 HR, 1 near-HR, 96.3 mph EV. Elder LHB split +0.43, HR risk 0.38.""", blast="good"),
            row("Hunter Feduccia", "L", "+875", 73, "💎", ["vs Elder"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.0 mph EV. Elder LHB split +0.43, HR risk 0.38.""", blast="good"),
            row("Freddie Freeman", "L", "+484", 69, "⭐", ["vs Elder"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 94.5 mph EV. Elder LHB split +0.43, HR risk 0.38.""", blast="good"),
        ],
    },
    {
        "title": "MIL @ NYM - Kyle Harrison (L, MIL) vs Zach Thornton (L, NYM)",
        "description": "Tail key data: Park boost +3% (stadium -1%, weather +4%). Harrison (HR risk 0.31, vs LHB -0.84, vs RHB +0.72). Thornton (HR risk 0.44, vs LHB -0.92, vs RHB +1.07).",
        "rows": [
            row("Christopher Morel", "R", "+610", 70, "⭐", ["vs Harrison"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 97.8 mph EV. Harrison RHB split +0.72, HR risk 0.31. limited recent HR events.""", blast="good"),
            row("A.J. Ewing", "L", "+1160", 65, "⭐", ["vs Harrison"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.9 mph EV. Harrison LHB split -0.84, HR risk 0.31. tough split lane (-0.84).""", blast="good"),
            row("Luis Torrens", "R", "+950", 78, "🌕 💣", ["vs Harrison"], """2 HR, 2 near-HR, 90.3 mph EV. Harrison RHB split +0.72, HR risk 0.31.""", blast="high"),
            row("Carson Benge", "L", "+870", 79, "🌕 💣", ["vs Harrison"], """3 HR, 3 near-HR, 94.5 mph EV. Harrison LHB split -0.84, HR risk 0.31. tough split lane (-0.84).""", blast="high"),
            row("Bo Bichette", "R", "+600", 60, "", ["vs Harrison"], """0 HR, 91.6 mph EV. Harrison RHB split +0.72, HR risk 0.31. limited recent HR events."""),
            row("William Contreras", "R", "+554", 80, "", ["vs Thornton"], """1 HR, 1 near-HR, 95.0 mph EV. Thornton RHB split +1.07, HR risk 0.44.""", blast="good"),
            row("Jackson Chourio", "R", "+458", 81, "", ["vs Thornton"], """1 HR, 2 near-HR, 94.9 mph EV. Thornton RHB split +1.07, HR risk 0.44.""", blast="good"),
            row("Christian Yelich", "L", "N/A", 65, "", ["vs Thornton"], """0 HR, 3 near-HR, 91.4 mph EV. Thornton LHB split -0.92, HR risk 0.44. tough split lane (-0.92).""", blast="good"),
            row("Andrew Vaughn", "R", "+600", 73, "", ["vs Thornton"], """0 HR, 93.3 mph EV. Thornton RHB split +1.07, HR risk 0.44. limited recent HR events.""", blast="good"),
            row("Jake Bauers", "L", "+500", 71, "🌕 💣", ["vs Thornton"], """2 HR, 2 near-HR, 89.8 mph EV. Thornton LHB split -0.92, HR risk 0.44. tough split lane (-0.92).""", blast="high"),
        ],
    },
    {
        "title": "MIN @ ATH - Taj Bradley (R, MIN) vs Gage Jump (L, ATH)",
        "description": "Tail key data: Park boost +32% (stadium +29%, weather +3%). Bradley (HR risk -0.06, vs LHB +0.44, vs RHB -0.67). Jump (HR risk -0.54, vs LHB -0.84, vs RHB -0.06).",
        "rows": [
            row("Lawrence Butler", "L", "+510", 85, "🌕 💣", ["vs Bradley"], """2 HR, 2 near-HR, 98.2 mph EV. Bradley LHB split +0.44, HR risk -0.06. pitcher risk below avg (-0.06).""", blast="high"),
            row("Zack Gelof", "R", "+436", 76, "🌕 💣 💎", ["vs Bradley"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 97.2 mph EV. Bradley RHB split -0.67, HR risk -0.06. tough split lane (-0.67); pitcher risk below avg (-0.06).""", blast="high"),
            row("Donovan Walton", "L", "+840", 66, "", ["vs Bradley"], """0 HR, 92.5 mph EV. Bradley LHB split +0.44, HR risk -0.06. pitcher risk below avg (-0.06); limited recent HR events.""", blast="good"),
            row("Jeff McNeil", "L", "+630", 81, "🌕 💣", ["vs Bradley"], """2 HR, 2 near-HR, 92.1 mph EV. Bradley LHB split +0.44, HR risk -0.06. pitcher risk below avg (-0.06).""", blast="high"),
            row("Max Muncy", "R", "+560", 75, "🌕 💣", ["vs Bradley"], """2 HR, 3 near-HR, 90.2 mph EV. Bradley RHB split -0.67, HR risk -0.06. tough split lane (-0.67); pitcher risk below avg (-0.06).""", blast="high"),
            row("Royce Lewis", "R", "+390", 58, "", ["vs Jump"], """0 HR, 2 near-HR, 87.7 mph EV. Jump RHB split -0.06, HR risk -0.54. slight split headwind (-0.06); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Ryan Jeffers", "R", "+406", 61, "", ["vs Jump"], """0 HR, 95.0 mph EV. Jump RHB split -0.06, HR risk -0.54. slight split headwind (-0.06); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Alan Roden", "L", "N/A", 58, "", ["vs Jump"], """0 HR, 99.8 mph EV. Jump LHB split -0.84, HR risk -0.54. tough split lane (-0.84); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Luke Keaschall", "R", "+750", 58, "", ["vs Jump"], """0 HR, 1 near-HR, 90.9 mph EV. Jump RHB split -0.06, HR risk -0.54. slight split headwind (-0.06); pitcher suppresses HR (-0.54)."""),
        ],
    },
    {
        "title": "PHI @ SEA - Aaron Nola (R, PHI) vs George Kirby (R, SEA)",
        "description": "Tail key data: Park boost +8% (stadium +0%, weather +8%). Nola (HR risk 0.93, vs LHB +0.61, vs RHB +0.86). Kirby (HR risk 0.54, vs LHB +0.79, vs RHB +0.20).",
        "rows": [
            row("Cal Raleigh", "S", "+347", 83, "⭐", ["vs Nola"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.5 mph EV. Nola SHB→RHB split +0.86, HR risk 0.93.""", blast="good"),
            row("Dominic Canzone", "L", "+445", 76, "", ["vs Nola"], """0 HR, 94.9 mph EV. Nola LHB split +0.61, HR risk 0.93. limited recent HR events.""", blast="good"),
            row("Randy Arozarena", "R", "+557", 81, "", ["vs Nola"], """1 HR, 1 near-HR, 91.9 mph EV. Nola RHB split +0.86, HR risk 0.93.""", blast="good"),
            row("Kyle Schwarber", "L", "+256", 92, "⭐ 🌕 💣", ["vs Kirby"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 97.6 mph EV. Kirby LHB split +0.79, HR risk 0.54.""", blast="high"),
            row("Bryce Harper", "L", "+481", 78, "⭐", ["vs Kirby"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 97.4 mph EV. Kirby LHB split +0.79, HR risk 0.54.""", blast="good"),
            row("JT Realmuto", "R", "+950", 74, "⭐", ["vs Kirby"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.8 mph EV. Kirby RHB split +0.20, HR risk 0.54.""", blast="good"),
        ],
    },
    {
        "title": "PIT @ SD - Paul Skenes (R, PIT) vs Michael King (R, SD)",
        "description": "Tail key data: Park boost +0% (stadium -5%, weather +5%). Skenes (HR risk 0.05, vs LHB -0.05, vs RHB +0.20). King (HR risk 0.46, vs LHB +0.64, vs RHB -0.10).",
        "rows": [
            row("Fernando Tatis Jr.", "R", "+471", 63, "⭐", ["vs Skenes"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 98.4 mph EV. Skenes RHB split +0.20, HR risk 0.05. limited recent HR events.""", blast="good"),
            row("Ty France", "R", "+690", 58, "", ["vs Skenes"], """0 HR, 90.4 mph EV. Skenes RHB split +0.20, HR risk 0.05. limited recent HR events."""),
            row("Xander Bogaerts", "R", "+900", 67, "", ["vs Skenes"], """1 HR, 1 near-HR, 98.4 mph EV. Skenes RHB split +0.20, HR risk 0.05.""", blast="good"),
            row("Jackson Merrill", "L", "+513", 79, "⭐ 🌕 💣", ["vs Skenes"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 97.9 mph EV. Skenes LHB split -0.05, HR risk 0.05. slight split headwind (-0.05).""", blast="high"),
            row("Manny Machado", "R", "+525", 63, "", ["vs Skenes"], """1 HR, 1 near-HR, 92.6 mph EV. Skenes RHB split +0.20, HR risk 0.05.""", blast="good"),
            row("Brandon Lowe", "L", "+423", 71, "", ["vs King"], """1 HR, 1 near-HR, 90.5 mph EV. King LHB split +0.64, HR risk 0.46.""", blast="good"),
            row("Oneil Cruz", "L", "+394", 79, "⭐ 🌕 💣", ["vs King"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 89.1 mph EV. King LHB split +0.64, HR risk 0.46.""", blast="high"),
            row("Bryan Reynolds", "S", "+630", 71, "", ["vs King"], """0 HR, 2 near-HR, 92.8 mph EV. King SHB→LHB split +0.64, HR risk 0.46.""", blast="good"),
            row("Esmerlyn Valdez", "R", "+472", 58, "⭐", ["vs King"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 87.3 mph EV. King RHB split -0.10, HR risk 0.46. slight split headwind (-0.10); limited recent HR events."""),
        ],
    },
    {
        "title": "TB @ DET - Ian Seymour 🧤 (L, TB) vs Jackson Jobe (R, DET)",
        "description": "Tail key data: Park boost -17% (stadium -10%, weather -7%). Seymour 🧤 (HR risk 1.02, vs LHB +0.56, vs RHB +1.02). Jobe (HR risk 0.21, vs LHB +1.10, vs RHB -1.44).",
        "rows": [
            row("Eduardo Valencia", "R", "+558", 91, "🌕 💣 💎", ["vs Seymour"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 95.5 mph EV. Seymour RHB split +1.02, HR risk 1.02. park/weather net drag (-17%).""", blast="high"),
            row("Kevin McGonigle", "L", "+750", 71, "💎", ["vs Seymour"], """Worst Pickz Hidden Gem. 0 HR, 93.7 mph EV. Seymour LHB split +0.56, HR risk 1.02. park/weather net drag (-17%); limited recent HR events.""", blast="good"),
            row("Gleyber Torres", "R", "+850", 67, "", ["vs Seymour"], """0 HR, 1 near-HR, 88.0 mph EV. Seymour RHB split +1.02, HR risk 1.02. park/weather net drag (-17%); limited recent HR events."""),
            row("Hao-Yu Lee", "R", "+550", 67, "", ["vs Seymour"], """0 HR, 89.8 mph EV. Seymour RHB split +1.02, HR risk 1.02. park/weather net drag (-17%); limited recent HR events."""),
            row("Jonathan Aranda", "L", "+557", 58, "💎", ["vs Jobe"], """Worst Pickz Hidden Gem. 0 HR, 90.9 mph EV. Jobe LHB split +1.10, HR risk 0.21. park/weather net drag (-17%); limited recent HR events."""),
            row("Junior Caminero", "R", "+350", 58, "🚀", ["vs Jobe"], """0 HR, 100.0 mph EV. Jobe RHB split -1.44, HR risk 0.21. tough split lane (-1.44); park/weather net drag (-17%).""", blast="good"),
            row("Ryan Vilade", "R", "N/A", 58, "", ["vs Jobe"], """1 HR, 1 near-HR, 81.4 mph EV. Jobe RHB split -1.44, HR risk 0.21. tough split lane (-1.44); park/weather net drag (-17%).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ CWS - Jacob deGrom (R, TEX) vs Anthony Kay (L, CWS)",
        "description": "Tail key data: Park boost -8% (stadium -5%, weather -3%). deGrom (HR risk -0.15, vs LHB +0.26, vs RHB -0.50). Kay (HR risk -0.34, vs LHB -1.19, vs RHB +0.24).",
        "rows": [
            row("Tristan Peters", "L", "+930", 72, "🌕 💣", ["vs deGrom"], """3 HR, 3 near-HR, 87.4 mph EV. deGrom LHB split +0.26, HR risk -0.15. pitcher risk below avg (-0.15); park/weather net drag (-8%).""", blast="high"),
            row("Miguel Vargas", "R", "+446", 64, "🌕 💣", ["vs deGrom"], """2 HR, 2 near-HR, 93.3 mph EV. deGrom RHB split -0.50, HR risk -0.15. tough split lane (-0.50); pitcher risk below avg (-0.15).""", blast="high"),
            row("Colson Montgomery", "L", "+416", 58, "", ["vs deGrom"], """0 HR, 90.0 mph EV. deGrom LHB split +0.26, HR risk -0.15. pitcher risk below avg (-0.15); park/weather net drag (-8%)."""),
            row("Elias Diaz", "R", "+790", 58, "", ["vs Kay"], """0 HR, 98.6 mph EV. Kay RHB split +0.24, HR risk -0.34. pitcher risk below avg (-0.34); park/weather net drag (-8%).""", blast="good"),
            row("Joc Pederson", "L", "N/A", 58, "", ["vs Kay"], """1 HR, 2 near-HR, 93.4 mph EV. Kay LHB split -1.19, HR risk -0.34. tough split lane (-1.19); pitcher risk below avg (-0.34).""", blast="good"),
            row("Corey Seager", "L", "+503", 65, "⭐ 🌕 💣", ["vs Kay"], """Worst Pickz Favorite. 1 HR, 4 near-HR, 95.4 mph EV. Kay LHB split -1.19, HR risk -0.34. tough split lane (-1.19); pitcher risk below avg (-0.34).""", blast="high"),
            row("Wyatt Langford", "R", "+546", 58, "", ["vs Kay"], """0 HR, 1 near-HR, 97.0 mph EV. Kay RHB split +0.24, HR risk -0.34. pitcher risk below avg (-0.34); park/weather net drag (-8%).""", blast="good"),
            row("Ezequiel Duran", "R", "+900", 59, "", ["vs Kay"], """0 HR, 2 near-HR, 97.9 mph EV. Kay RHB split +0.24, HR risk -0.34. pitcher risk below avg (-0.34); park/weather net drag (-8%).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-25")

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

    out = ROOT / '_games-0825.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
