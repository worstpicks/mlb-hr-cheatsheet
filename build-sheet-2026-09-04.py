#!/usr/bin/env python3
"""Generate games[] block for 2026-09-04 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Bo Bichette (R)",
    "Brandon Nimmo (L)",
    "Carter Jensen (L)",
    "Elly De La Cruz (S)",
    "Heriberto Hernandez (R)",
    "Jo Adell (R)",
    "Joc Pederson (L)",
    "Jonathan Aranda (L)",
    "Jordan Walker (R)",
    "Kazuma Okamoto (R)",
    "Lane Thomas (R)",
    "Lars Nootbaar (L)",
    "Mark Vientos (R)",
    "Mickey Gasper (S)",
    "Mickey Moniak (L)",
    "Pete Alonso (R)",
    "Pete Crow Armstrong (L)",
    "Rafael Devers (L)",
    "Roman Anthony (L)",
    "Ronald Acuna Jr. (R)",
    "Spencer Jones (L)",
    "Teoscar Hernandez (R)",
    "Will Smith (R)",
    "William Contreras (R)",
    "Yordan Alvarez (L)",
    "Zach Neto (R)",
}

GEMS = {
    "Alec Burleson (L)",
    "Austin Wells (L)",
    "Bryan Reynolds (S)",
    "Cody Bellinger (L)",
    "Dominic Canzone (L)",
    "Jackson Chourio (R)",
    "Jake Burger (R)",
    "Josh Bell (S)",
    "Julio Rodriguez (R)",
    "Lawrence Butler (L)",
    "Leonardo Bernal (S)",
    "Munetaka Murakami (L)",
    "Trevor Larnach (L)",
    "Yandy Diaz (R)",
    "Zac Veen (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BOS",
    "Agustin Ramirez (R)": "MIA",
    "Alec Bohm (R)": "PHI",
    "Alec Burleson (L)": "STL",
    "Alejandro Kirk (R)": "TOR",
    "Andres Chaparro (R)": "WSH",
    "Austin Wells (L)": "NYY",
    "Bo Bichette (R)": "NYM",
    "Bo Naylor (L)": "MIL",
    "Brandon Nimmo (L)": "TEX",
    "Bryan Reynolds (S)": "PIT",
    "Cal Raleigh (S)": "SEA",
    "Carter Jensen (L)": "KC",
    "Christian Yelich (L)": "MIL",
    "Cody Bellinger (L)": "NYY",
    "Corey Seager (L)": "TEX",
    "Dominic Canzone (L)": "SEA",
    "Elly De La Cruz (S)": "CIN",
    "Freddy Fermin (R)": "SD",
    "George Springer (R)": "TOR",
    "Gleyber Torres (R)": "DET",
    "Hao Yu Lee (R)": "DET",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "J.T. Realmuto (R)": "PHI",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake Burger (R)": "TEX",
    "Jake McCarthy (L)": "COL",
    "James Wood (L)": "WSH",
    "Jase Bowen (R)": "SD",
    "Jo Adell (R)": "CLE",
    "Joc Pederson (L)": "TEX",
    "Jonah Heim (S)": "ATH",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Josh Bell (S)": "MIN",
    "Juan Soto (L)": "NYM",
    "Julio Rodriguez (R)": "SEA",
    "Jung Hoo Lee (L)": "SF",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "LaMonte Wade Jr. (L)": "HOU",
    "Lane Thomas (R)": "ATL",
    "Lars Nootbaar (L)": "ARI",
    "Lawrence Butler (L)": "ATH",
    "Lazaro Montes (L)": "SEA",
    "Leonardo Bernal (S)": "STL",
    "Luis Lara (S)": "MIL",
    "Mark Vientos (R)": "NYM",
    "Matt McLain (R)": "CIN",
    "Michael Busch (L)": "CHC",
    "Michael Stefanic (R)": "ATH",
    "Mickey Gasper (S)": "BOS",
    "Mickey Moniak (L)": "COL",
    "Moises Ballesteros (L)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Oneil Cruz (L)": "PIT",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randy Arozarena (R)": "SEA",
    "Roman Anthony (L)": "BOS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Spencer Jones (L)": "NYY",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Travis d'Arnaud (R)": "LAA",
    "Trevor Larnach (L)": "MIN",
    "Trevor Story (R)": "BOS",
    "Tristan Peters (L)": "CWS",
    "Tyler Stephenson (R)": "CIN",
    "Will Smith (R)": "LAD",
    "William Contreras (R)": "MIL",
    "Yainer Diaz (R)": "HOU",
    "Yandy Diaz (R)": "TB",
    "Yohandy Morales (R)": "WSH",
    "Yordan Alvarez (L)": "HOU",
    "Zac Veen (L)": "COL",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("ATH @ SEA", "Morris"),
    ("CHC @ MIA", "Imanaga"),
    ("TOR @ KC", "Taillon"),
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
        "title": "ARI @ HOU - Merrill Kelly (R, ARI) vs Cristian Javier (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +0%). Kelly (HR risk 0.13, vs LHB +0.46, vs RHB -0.51). Javier (HR risk 0.33, vs LHB -0.17, vs RHB +0.75).",
        "rows": [
            row("Yordan Alvarez", "L", "+250", 72, "⭐", ["vs Kelly"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 98.1 mph EV. Kelly LHB split +0.46, HR risk 0.13.""", blast="good"),
            row("LaMonte Wade Jr.", "L", "+1060", 70, "", ["vs Kelly"], """1 HR, 1 near-HR, 95.2 mph EV. Kelly LHB split +0.46, HR risk 0.13.""", blast="good"),
            row("Yainer Diaz", "R", "+790", 63, "", ["vs Kelly"], """1 HR, 1 near-HR, 99.8 mph EV. Kelly RHB split -0.51, HR risk 0.13. tough split lane (-0.51).""", blast="good"),
            row("Lars Nootbaar", "L", "+475", 77, "🚀 ⭐ 🌕 💣", ["vs Javier"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 101.0 mph EV. Javier LHB split -0.17, HR risk 0.33. slight split headwind (-0.17).""", blast="high"),
            row("Tim Tawa", "R", "+571", 60, "", ["vs Javier"], """0 HR, 1 near-HR, 89.4 mph EV. Javier RHB split +0.75, HR risk 0.33. limited recent HR events."""),
            row("Ketel Marte", "S", "+390", 71, "", ["vs Javier"], """1 HR, 3 near-HR, 85.5 mph EV. Javier SHB→RHB split +0.75, HR risk 0.33. lighter EV form (85.5 mph).""", blast="good"),
        ],
    },
    {
        "title": "ATH @ SEA - Kade Morris 🧤 (R, ATH) vs Logan Gilbert (R, SEA)",
        "description": "Tail key data: Park boost -5% (stadium +1%, weather -6%). Morris 🧤 (HR risk 1.10, vs LHB +1.74, vs RHB -0.23). Gilbert (HR risk 0.28, vs LHB -0.13, vs RHB +0.82).",
        "rows": [
            row("Dominic Canzone", "L", "+490", 87, "💎", ["vs Morris"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.8 mph EV. Morris LHB split +1.74, HR risk 1.10. park/weather net drag (-5%).""", blast="good"),
            row("Cal Raleigh", "S", "+330", 89, "🌕 💣", ["vs Morris"], """1 HR, 2 near-HR, 91.2 mph EV. Morris SHB→LHB split +1.74, HR risk 1.10. park/weather net drag (-5%).""", blast="good"),
            row("Lazaro Montes", "L", "+680", 91, "🚀 🌕 💣", ["vs Morris"], """1 HR, 1 near-HR, 102.4 mph EV. Morris LHB split +1.74, HR risk 1.10. park/weather net drag (-5%).""", blast="good"),
            row("Julio Rodriguez", "R", "+520", 62, "💎", ["vs Morris"], """Worst Pickz Hidden Gem. 0 HR, 91.4 mph EV. Morris RHB split -0.23, HR risk 1.10. slight split headwind (-0.23); park/weather net drag (-5%)."""),
            row("Randy Arozarena", "R", "+529", 69, "", ["vs Morris"], """1 HR, 1 near-HR, 89.1 mph EV. Morris RHB split -0.23, HR risk 1.10. slight split headwind (-0.23); park/weather net drag (-5%).""", blast="good"),
            row("Michael Stefanic", "R", "N/A", 67, "", ["vs Gilbert"], """0 HR, 99.5 mph EV. Gilbert RHB split +0.82, HR risk 0.28. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
            row("Zack Gelof", "R", "+524", 66, "", ["vs Gilbert"], """0 HR, 95.4 mph EV. Gilbert RHB split +0.82, HR risk 0.28. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
            row("Lawrence Butler", "L", "+680", 58, "💎", ["vs Gilbert"], """Worst Pickz Hidden Gem. 0 HR, 94.5 mph EV. Gilbert LHB split -0.13, HR risk 0.28. slight split headwind (-0.13); park/weather net drag (-5%).""", blast="good"),
            row("Jonah Heim", "S", "+980", 72, "", ["vs Gilbert"], """1 HR, 1 near-HR, 95.5 mph EV. Gilbert SHB→RHB split +0.82, HR risk 0.28. park/weather net drag (-5%).""", blast="good"),
            row("Henry Bolte", "R", "+820", 67, "", ["vs Gilbert"], """0 HR, 98.9 mph EV. Gilbert RHB split +0.82, HR risk 0.28. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "ATL @ PHI - Chris Sale (L, ATL) vs Cristopher Sanchez (L, PHI)",
        "description": "Tail key data: Park boost +9% (stadium +13%, weather -4%). Sale (HR risk -1.14, vs LHB -0.82, vs RHB -0.86). Sanchez (HR risk -0.70, vs LHB -1.11, vs RHB -0.37).",
        "rows": [
            row("Kyle Schwarber", "L", "+352", 58, "", ["vs Sale"], """0 HR, 90.1 mph EV. Sale LHB split -0.82, HR risk -1.14. tough split lane (-0.82); pitcher suppresses HR (-1.14)."""),
            row("J.T. Realmuto", "R", "+725", 58, "", ["vs Sale"], """1 HR, 1 near-HR, 91.3 mph EV. Sale RHB split -0.86, HR risk -1.14. tough split lane (-0.86); pitcher suppresses HR (-1.14).""", blast="good"),
            row("Alec Bohm", "R", "+780", 58, "", ["vs Sale"], """0 HR, 1 near-HR, 90.6 mph EV. Sale RHB split -0.86, HR risk -1.14. tough split lane (-0.86); pitcher suppresses HR (-1.14)."""),
            row("Ronald Acuna Jr.", "R", "+545", 64, "⭐ 🌕 💣", ["vs Sanchez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.5 mph EV. Sanchez RHB split -0.37, HR risk -0.70. slight split headwind (-0.37); pitcher suppresses HR (-0.70).""", blast="high"),
            row("Lane Thomas", "R", "+810", 58, "⭐", ["vs Sanchez"], """Worst Pickz Favorite. 0 HR, 91.5 mph EV. Sanchez RHB split -0.37, HR risk -0.70. slight split headwind (-0.37); pitcher suppresses HR (-0.70)."""),
        ],
    },
    {
        "title": "BOS @ BAL - Ranger Suarez (L, BOS) vs Shane Baz (R, BAL)",
        "description": "Tail key data: Park boost +5% (stadium -4%, weather +9%). Suarez (HR risk -0.57, vs LHB -0.47, vs RHB -0.35). Baz (HR risk -0.40, vs LHB -0.08, vs RHB -0.64).",
        "rows": [
            row("Pete Alonso", "R", "+410", 72, "🚀 ⭐ 🌕 💣", ["vs Suarez"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 100.9 mph EV. Suarez RHB split -0.35, HR risk -0.57. slight split headwind (-0.35); pitcher suppresses HR (-0.57).""", blast="high"),
            row("Mickey Gasper", "S", "+540", 76, "⭐ 🌕 💣", ["vs Baz"], """Worst Pickz Favorite. 4 HR, 4 near-HR, 93.2 mph EV. Baz SHB→LHB split -0.08, HR risk -0.40. slight split headwind (-0.08); pitcher suppresses HR (-0.40).""", blast="high"),
            row("Roman Anthony", "L", "+500", 61, "⭐", ["vs Baz"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.1 mph EV. Baz LHB split -0.08, HR risk -0.40. slight split headwind (-0.08); pitcher suppresses HR (-0.40).""", blast="good"),
            row("Adley Rutschman", "S", "+580", 58, "", ["vs Baz"], """1 HR, 1 near-HR, 85.3 mph EV. Baz SHB→LHB split -0.08, HR risk -0.40. slight split headwind (-0.08); pitcher suppresses HR (-0.40).""", blast="good"),
            row("Trevor Story", "R", "+630", 58, "", ["vs Baz"], """1 HR, 1 near-HR, 93.4 mph EV. Baz RHB split -0.64, HR risk -0.40. tough split lane (-0.64); pitcher suppresses HR (-0.40).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ MIA - Shota Imanaga 🧤 (L, CHC) vs Janson Junk (R, MIA)",
        "description": "Tail key data: Park boost -14% (stadium -13%, weather +0%). Imanaga 🧤 (HR risk 1.60, vs LHB +1.14, vs RHB +1.21). Junk (HR risk -0.74, vs LHB -0.39, vs RHB -0.58).",
        "rows": [
            row("Heriberto Hernandez", "R", "+400", 83, "⭐", ["vs Imanaga"], """Worst Pickz Favorite. 0 HR, 99.8 mph EV. Imanaga RHB split +1.21, HR risk 1.60. park/weather net drag (-14%); limited recent HR events.""", blast="good"),
            row("Agustin Ramirez", "R", "+610", 83, "🚀", ["vs Imanaga"], """0 HR, 100.0 mph EV. Imanaga RHB split +1.21, HR risk 1.60. park/weather net drag (-14%); limited recent HR events.""", blast="good"),
            row("Pete Crow Armstrong", "L", "+300", 69, "⭐ 🌕 💣", ["vs Junk"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 95.8 mph EV. Junk LHB split -0.39, HR risk -0.74. slight split headwind (-0.39); pitcher suppresses HR (-0.74).""", blast="high"),
            row("Michael Busch", "L", "+500", 58, "", ["vs Junk"], """1 HR, 1 near-HR, 93.9 mph EV. Junk LHB split -0.39, HR risk -0.74. slight split headwind (-0.39); pitcher suppresses HR (-0.74).""", blast="good"),
        ],
    },
    {
        "title": "DET @ CLE - Andrew Sears (L, DET) vs Foster Griffin (L, CLE)",
        "description": "Tail key data: Park boost +10% (stadium -4%, weather +14%). Sears (HR risk 0.17, vs LHB +0.00, vs RHB -1.26). Griffin (HR risk 0.47, vs LHB +0.71, vs RHB +0.26).",
        "rows": [
            row("Jo Adell", "R", "+440", 76, "⭐ 🌕 💣", ["vs Sears"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.8 mph EV. Sears RHB split -1.26, HR risk 0.17. tough split lane (-1.26).""", blast="high"),
            row("Gleyber Torres", "R", "N/A", 70, "", ["vs Griffin"], """0 HR, 95.3 mph EV. Griffin RHB split +0.26, HR risk 0.47. limited recent HR events.""", blast="good"),
            row("Hao Yu Lee", "R", "N/A", 71, "", ["vs Griffin"], """1 HR, 1 near-HR, 90.6 mph EV. Griffin RHB split +0.26, HR risk 0.47.""", blast="good"),
        ],
    },
    {
        "title": "LAA @ PIT - Ryan Johnson (R, LAA) vs Jared Jones (R, PIT)",
        "description": "Tail key data: Park boost -1% (stadium -15%, weather +13%). Johnson (HR risk 0.93, vs LHB +0.60, vs RHB +0.85). Jones (HR risk 0.83, vs LHB +0.37, vs RHB +1.13).",
        "rows": [
            row("Oneil Cruz", "L", "+340", 78, "", ["vs Johnson"], """1 HR, 1 near-HR, 93.4 mph EV. Johnson LHB split +0.60, HR risk 0.93. park suppresses carry (-15%).""", blast="good"),
            row("Bryan Reynolds", "S", "+550", 76, "💎", ["vs Johnson"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.4 mph EV. Johnson SHB→RHB split +0.85, HR risk 0.93. park suppresses carry (-15%); limited recent HR events.""", blast="good"),
            row("Zach Neto", "R", "+484", 84, "⭐", ["vs Jones"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.9 mph EV. Jones RHB split +1.13, HR risk 0.83. park suppresses carry (-15%).""", blast="good"),
            row("Moises Ballesteros", "L", "+775", 78, "", ["vs Jones"], """1 HR, 2 near-HR, 94.8 mph EV. Jones LHB split +0.37, HR risk 0.83. park suppresses carry (-15%).""", blast="good"),
            row("Travis d'Arnaud", "R", "+1040", 79, "", ["vs Jones"], """0 HR, 1 near-HR, 94.9 mph EV. Jones RHB split +1.13, HR risk 0.83. park suppresses carry (-15%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIL @ CIN - Shane Drohan (L, MIL) vs Rhett Lowder (R, CIN)",
        "description": "Tail key data: Park boost +24% (stadium +15%, weather +8%). Drohan (HR risk -0.06, vs LHB -0.68, vs RHB +0.49). Lowder (HR risk 0.54, vs LHB +0.37, vs RHB +0.39).",
        "rows": [
            row("Elly De La Cruz", "S", "+400", 68, "🚀 ⭐", ["vs Drohan"], """Worst Pickz Favorite. 0 HR, 101.0 mph EV. Drohan SHB→RHB split +0.49, HR risk -0.06. pitcher risk below avg (-0.06); limited recent HR events.""", blast="good"),
            row("Tyler Stephenson", "R", "+490", 75, "", ["vs Drohan"], """1 HR, 2 near-HR, 95.9 mph EV. Drohan RHB split +0.49, HR risk -0.06. pitcher risk below avg (-0.06).""", blast="good"),
            row("Sal Stewart", "R", "+348", 81, "🌕 💣", ["vs Drohan"], """2 HR, 2 near-HR, 94.0 mph EV. Drohan RHB split +0.49, HR risk -0.06. pitcher risk below avg (-0.06).""", blast="high"),
            row("Matt McLain", "R", "+610", 72, "", ["vs Drohan"], """1 HR, 1 near-HR, 94.3 mph EV. Drohan RHB split +0.49, HR risk -0.06. pitcher risk below avg (-0.06).""", blast="good"),
            row("Christian Yelich", "L", "+503", 81, "", ["vs Lowder"], """1 HR, 1 near-HR, 96.7 mph EV. Lowder LHB split +0.37, HR risk 0.54.""", blast="good"),
            row("Bo Naylor", "L", "N/A", 81, "", ["vs Lowder"], """1 HR, 2 near-HR, 94.1 mph EV. Lowder LHB split +0.37, HR risk 0.54.""", blast="good"),
            row("William Contreras", "R", "+449", 77, "⭐", ["vs Lowder"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.9 mph EV. Lowder RHB split +0.39, HR risk 0.54.""", blast="good"),
            row("Jackson Chourio", "R", "+360", 76, "💎", ["vs Lowder"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.7 mph EV. Lowder RHB split +0.39, HR risk 0.54. limited recent HR events.""", blast="good"),
            row("Luis Lara", "S", "N/A", 74, "", ["vs Lowder"], """0 HR, 1 near-HR, 92.8 mph EV. Lowder SHB→RHB split +0.39, HR risk 0.54. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIN @ CWS - Zebby Matthews (R, MIN) vs Erick Fedde (R, CWS)",
        "description": "Tail key data: Park boost +10% (stadium -5%, weather +15%). Matthews (HR risk 0.24, vs LHB +0.36, vs RHB +0.02). Fedde (HR risk -0.06, vs LHB -0.35, vs RHB +0.52).",
        "rows": [
            row("Munetaka Murakami", "L", "+260", 65, "💎", ["vs Matthews"], """Worst Pickz Hidden Gem. 0 HR, 94.7 mph EV. Matthews LHB split +0.36, HR risk 0.24. limited recent HR events.""", blast="good"),
            row("Tristan Peters", "L", "+600", 71, "", ["vs Matthews"], """0 HR, 3 near-HR, 93.3 mph EV. Matthews LHB split +0.36, HR risk 0.24.""", blast="good"),
            row("Josh Bell", "S", "+425", 66, "💎", ["vs Fedde"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.5 mph EV. Fedde SHB→RHB split +0.52, HR risk -0.06. pitcher risk below avg (-0.06); limited recent HR events.""", blast="good"),
            row("Trevor Larnach", "L", "+500", 65, "💎", ["vs Fedde"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 95.4 mph EV. Fedde LHB split -0.35, HR risk -0.06. slight split headwind (-0.35); pitcher risk below avg (-0.06).""", blast="good"),
            row("Kody Clemens", "L", "+324", 58, "", ["vs Fedde"], """0 HR, 1 near-HR, 90.8 mph EV. Fedde LHB split -0.35, HR risk -0.06. slight split headwind (-0.35); pitcher risk below avg (-0.06)."""),
        ],
    },
    {
        "title": "NYY @ SD - Max Fried (L, NYY) vs Walker Buehler (R, SD)",
        "description": "Tail key data: Park boost +1% (stadium -5%, weather +6%). Fried (HR risk -1.06, vs LHB -0.82, vs RHB -0.75). Buehler (HR risk -0.11, vs LHB -0.08, vs RHB -0.02).",
        "rows": [
            row("Jase Bowen", "R", "N/A", 58, "", ["vs Fried"], """1 HR, 1 near-HR, 93.9 mph EV. Fried RHB split -0.75, HR risk -1.06. tough split lane (-0.75); pitcher suppresses HR (-1.06).""", blast="good"),
            row("Freddy Fermin", "R", "+1200", 58, "", ["vs Fried"], """0 HR, 1 near-HR, 93.2 mph EV. Fried RHB split -0.75, HR risk -1.06. tough split lane (-0.75); pitcher suppresses HR (-1.06).""", blast="good"),
            row("Jackson Merrill", "L", "+680", 58, "", ["vs Fried"], """0 HR, 1 near-HR, 90.8 mph EV. Fried LHB split -0.82, HR risk -1.06. tough split lane (-0.82); pitcher suppresses HR (-1.06)."""),
            row("Spencer Jones", "L", "+565", 70, "⭐ 🌕 💣", ["vs Buehler"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.7 mph EV. Buehler LHB split -0.08, HR risk -0.11. slight split headwind (-0.08); pitcher risk below avg (-0.11).""", blast="high"),
            row("Cody Bellinger", "L", "+625", 58, "💎", ["vs Buehler"], """Worst Pickz Hidden Gem. 0 HR, 94.6 mph EV. Buehler LHB split -0.08, HR risk -0.11. slight split headwind (-0.08); pitcher risk below avg (-0.11).""", blast="good"),
            row("Austin Wells", "L", "+790", 58, "💎", ["vs Buehler"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.5 mph EV. Buehler LHB split -0.08, HR risk -0.11. slight split headwind (-0.08); pitcher risk below avg (-0.11).""", blast="good"),
        ],
    },
    {
        "title": "SF @ NYM - Matt Wilkinson (L, SF) vs Nolan McLean (R, NYM)",
        "description": "Tail key data: Park boost +3% (stadium -1%, weather +4%). Wilkinson (HR risk -0.27, vs LHB +0.00, vs RHB +0.23). McLean (HR risk -0.63, vs LHB -0.26, vs RHB -0.81).",
        "rows": [
            row("Mark Vientos", "R", "+410", 80, "⭐ 🌕 💣", ["vs Wilkinson"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 94.3 mph EV. Wilkinson RHB split +0.23, HR risk -0.27. pitcher risk below avg (-0.27).""", blast="high"),
            row("Bo Bichette", "R", "+540", 61, "⭐", ["vs Wilkinson"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.2 mph EV. Wilkinson RHB split +0.23, HR risk -0.27. pitcher risk below avg (-0.27); limited recent HR events.""", blast="good"),
            row("Juan Soto", "L", "+300", 58, "", ["vs Wilkinson"], """0 HR, 96.7 mph EV. Wilkinson LHB split +0.00, HR risk -0.27. pitcher risk below avg (-0.27); limited recent HR events.""", blast="good"),
            row("Rafael Devers", "L", "+339", 72, "🚀 ⭐ 🌕 💣", ["vs McLean"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 100.9 mph EV. McLean LHB split -0.26, HR risk -0.63. slight split headwind (-0.26); pitcher suppresses HR (-0.63).""", blast="high"),
            row("Jung Hoo Lee", "L", "+1200", 58, "", ["vs McLean"], """0 HR, 93.7 mph EV. McLean LHB split -0.26, HR risk -0.63. slight split headwind (-0.26); pitcher suppresses HR (-0.63).""", blast="good"),
        ],
    },
    {
        "title": "STL @ COL - Andre Pallante (R, STL) vs Ryan Feltner (R, COL)",
        "description": "Tail key data: Park boost +27% (stadium +21%, weather +6%). Pallante (HR risk -1.10, vs LHB -0.67, vs RHB -0.95). Feltner (HR risk -0.03, vs LHB -0.10, vs RHB +0.14).",
        "rows": [
            row("Zac Veen", "L", "+710", 58, "🚀 💎", ["vs Pallante"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 100.8 mph EV. Pallante LHB split -0.67, HR risk -1.10. tough split lane (-0.67); pitcher suppresses HR (-1.10).""", blast="good"),
            row("Jake McCarthy", "L", "+1040", 58, "", ["vs Pallante"], """1 HR, 1 near-HR, 93.8 mph EV. Pallante LHB split -0.67, HR risk -1.10. tough split lane (-0.67); pitcher suppresses HR (-1.10).""", blast="good"),
            row("Hunter Goodman", "R", "+305", 66, "🌕 💣", ["vs Pallante"], """2 HR, 3 near-HR, 91.4 mph EV. Pallante RHB split -0.95, HR risk -1.10. tough split lane (-0.95); pitcher suppresses HR (-1.10).""", blast="high"),
            row("Mickey Moniak", "L", "+346", 58, "⭐", ["vs Pallante"], """Worst Pickz Favorite. 0 HR, 94.3 mph EV. Pallante LHB split -0.67, HR risk -1.10. tough split lane (-0.67); pitcher suppresses HR (-1.10).""", blast="good"),
            row("Jordan Walker", "R", "+340", 69, "⭐", ["vs Feltner"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 91.6 mph EV. Feltner RHB split +0.14, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="good"),
            row("Leonardo Bernal", "S", "+650", 72, "💎", ["vs Feltner"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.7 mph EV. Feltner SHB→RHB split +0.14, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="good"),
            row("Alec Burleson", "L", "+394", 66, "💎", ["vs Feltner"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.8 mph EV. Feltner LHB split -0.10, HR risk -0.03. slight split headwind (-0.10); pitcher risk below avg (-0.03).""", blast="good"),
        ],
    },
    {
        "title": "TB @ TEX - Nick Martinez (R, TB) vs Trevor Williams (R, TEX)",
        "description": "Tail key data: Park boost -10% (stadium -10%, weather +0%). Martinez (HR risk -0.33, vs LHB -0.25, vs RHB -0.11). Williams (BAA vs LHB .333).",
        "rows": [
            row("Joc Pederson", "L", "+345", 71, "⭐ 🌕 💣", ["vs Martinez"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 96.0 mph EV. Martinez LHB split -0.25, HR risk -0.33. slight split headwind (-0.25); pitcher risk below avg (-0.33).""", blast="high"),
            row("Brandon Nimmo", "L", "+450", 58, "⭐", ["vs Martinez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.3 mph EV. Martinez LHB split -0.25, HR risk -0.33. slight split headwind (-0.25); pitcher risk below avg (-0.33).""", blast="good"),
            row("Corey Seager", "L", "+350", 58, "", ["vs Martinez"], """0 HR, 98.5 mph EV. Martinez LHB split -0.25, HR risk -0.33. slight split headwind (-0.25); pitcher risk below avg (-0.33).""", blast="good"),
            row("Jake Burger", "R", "+390", 58, "💎", ["vs Martinez"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.1 mph EV. Martinez RHB split -0.11, HR risk -0.33. slight split headwind (-0.11); pitcher risk below avg (-0.33).""", blast="good"),
            row("Jonathan Aranda", "L", "N/A", 58, "⭐", ["vs Williams"], """Worst Pickz Favorite. 0 HR, 95.1 mph EV. limited split/risk sample; park/weather net drag (-10%).""", blast="good"),
            row("Yandy Diaz", "R", "N/A", 59, "💎", ["vs Williams"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 89.9 mph EV. limited split/risk sample; park/weather net drag (-10%).""", blast="good"),
            row("Junior Caminero", "R", "N/A", 58, "", ["vs Williams"], """0 HR, 92.6 mph EV. limited split/risk sample; park/weather net drag (-10%).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ KC - Jameson Taillon 🧤 (R, TOR) vs Daniel Lynch IV (L, KC)",
        "description": "Tail key data: Park boost +16% (stadium +9%, weather +6%). Taillon 🧤 (HR risk 1.89, vs LHB +0.86, vs RHB +2.03). Lynch IV (HR risk 0.19, vs LHB -0.20, vs RHB +0.30).",
        "rows": [
            row("Carter Jensen", "L", "+360", 98, "⭐ 🌕 💣", ["vs Taillon"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 99.2 mph EV. Taillon LHB split +0.86, HR risk 1.89.""", blast="high"),
            row("Jac Caglianone", "L", "+370", 85, "", ["vs Taillon"], """0 HR, 93.3 mph EV. Taillon LHB split +0.86, HR risk 1.89. limited recent HR events.""", blast="good"),
            row("Salvador Perez", "R", "+398", 91, "🌕 💣", ["vs Taillon"], """1 HR, 1 near-HR, 87.4 mph EV. Taillon RHB split +2.03, HR risk 1.89. lighter EV form (87.4 mph).""", blast="good"),
            row("Kazuma Okamoto", "R", "+325", 72, "⭐", ["vs Lynch IV"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.2 mph EV. Lynch IV RHB split +0.30, HR risk 0.19.""", blast="good"),
            row("Alejandro Kirk", "R", "+710", 67, "", ["vs Lynch IV"], """0 HR, 95.7 mph EV. Lynch IV RHB split +0.30, HR risk 0.19. limited recent HR events.""", blast="good"),
            row("George Springer", "R", "+499", 67, "", ["vs Lynch IV"], """0 HR, 99.1 mph EV. Lynch IV RHB split +0.30, HR risk 0.19. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "WSH @ LAD - Jackson Kent (L, WSH) vs Blake Snell (L, LAD)",
        "description": "Tail key data: Park boost +20% (stadium +18%, weather +2%). Kent (HR risk -0.72, vs LHB -0.71, vs RHB -0.45). Snell (HR risk -2.07, vs LHB -1.61, vs RHB -1.56).",
        "rows": [
            row("Teoscar Hernandez", "R", "+548", 59, "⭐", ["vs Kent"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.0 mph EV. Kent RHB split -0.45, HR risk -0.72. tough split lane (-0.45); pitcher suppresses HR (-0.72).""", blast="good"),
            row("Will Smith", "R", "+481", 58, "⭐", ["vs Kent"], """Worst Pickz Favorite. 0 HR, 97.7 mph EV. Kent RHB split -0.45, HR risk -0.72. tough split lane (-0.45); pitcher suppresses HR (-0.72).""", blast="good"),
            row("Andres Chaparro", "R", "+610", 58, "", ["vs Snell"], """1 HR, 2 near-HR, 88.4 mph EV. Snell RHB split -1.56, HR risk -2.07. tough split lane (-1.56); pitcher suppresses HR (-2.07).""", blast="good"),
            row("James Wood", "L", "+490", 58, "", ["vs Snell"], """1 HR, 1 near-HR, 92.8 mph EV. Snell LHB split -1.61, HR risk -2.07. tough split lane (-1.61); pitcher suppresses HR (-2.07).""", blast="good"),
            row("Yohandy Morales", "R", "+650", 58, "🚀", ["vs Snell"], """0 HR, 1 near-HR, 104.1 mph EV. Snell RHB split -1.56, HR risk -2.07. tough split lane (-1.56); pitcher suppresses HR (-2.07).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-04")

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

    out = ROOT / '_games-0904.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
