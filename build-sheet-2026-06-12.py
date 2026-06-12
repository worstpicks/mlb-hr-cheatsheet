#!/usr/bin/env python3
"""Generate games[] block for 2026-06-12 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Colson Montgomery (L)",
    "Daylen Lile (L)",
    "Fernando Tatis Jr. (R)",
    "Garrett Mitchell (L)",
    "Jac Caglianone (L)",
    "James Wood (L)",
    "Kazuma Okamoto (R)",
    "Ketel Marte (S)",
    "Kyle Stowers (L)",
    "Matt Olson (L)",
    "Mike Trout (R)",
    "Nick Kurtz (L)",
    "Riley Greene (L)",
    "Shohei Ohtani (L)",
    "Spencer Steer (R)",
    "Tyler Callihan (L)",
    "Wilyer Abreu (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Cam Smith (R)",
    "Colton Cowser (L)",
    "Endy Rodriguez (S)",
    "Eric Haase (R)",
    "Henry Bolte (R)",
    "Jacob Gonzalez (L)",
    "Luis Garcia Jr. (L)",
    "Miguel Vargas (R)",
    "Tommy Troy (R)",
    "Victor Caratini (S)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Andy Pages (R)": "LAD",
    "Ben Rice (L)": "NYY",
    "Braden Montgomery (S)": "CWS",
    "Brandon Marsh (L)": "PHI",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "Cam Smith (R)": "HOU",
    "Colby Thomas (R)": "ATH",
    "Colson Montgomery (L)": "CWS",
    "Colton Cowser (L)": "BAL",
    "Corey Seager (L)": "TEX",
    "Daylen Lile (L)": "WSH",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Edmundo Sosa (R)": "PHI",
    "Edouard Julien (L)": "COL",
    "Endy Rodriguez (S)": "PIT",
    "Eric Haase (R)": "SF",
    "Fernando Tatis Jr. (R)": "SD",
    "Garrett Mitchell (L)": "MIL",
    "Gary Sanchez (R)": "MIL",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "TB",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Isaac Paredes (R)": "HOU",
    "J.T. Realmuto (R)": "PHI",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jacob Gonzalez (L)": "CWS",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jarren Duran (L)": "BOS",
    "Jordan Walker (R)": "STL",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kerry Carpenter (L)": "DET",
    "Ketel Marte (S)": "ARI",
    "Kyle Karros (R)": "COL",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lars Nootbaar (L)": "STL",
    "Logan O'Hoppe (R)": "LAA",
    "Luis Garcia Jr. (L)": "WSH",
    "Luis Torrens (R)": "NYM",
    "Luke Raley (L)": "SEA",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Michael Massey (L)": "KC",
    "Mickey Gasper (S)": "BOS",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Nick Kurtz (L)": "ATH",
    "Oswald Peraza (R)": "LAA",
    "Owen Caissie (L)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Riley Greene (L)": "DET",
    "Ryan McMahon (L)": "NYY",
    "Ryan Waldschmidt (R)": "ARI",
    "Samuel Basallo (L)": "BAL",
    "Seiya Suzuki (R)": "CHC",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Steer (R)": "CIN",
    "Tommy Troy (R)": "ARI",
    "Tyler Callihan (L)": "PIT",
    "Victor Caratini (S)": "MIN",
    "Vinnie Pasquantino (L)": "KC",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_PITCHERS = {
    "Imai",
    "Lodolo",
    "Weathers",
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

def add_bum_row_emojis(entry):
    chip = entry["chips"][0].replace("vs ", "").strip()
    if chip not in BUM_PITCHERS:
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
        "title": "ARI @ CIN - Eduardo Rodriguez (L, ARI) vs Nick Lodolo 🧤 (L, CIN)",
        "description": "Tail key data: Park boost +11% (stadium +13%, weather -3%). Rodriguez (HR risk -0.38, vs LHB -0.72, vs RHB +0.30). Lodolo 🧤 (HR risk 1.06, vs LHB -1.37, vs RHB +2.05).",
        "rows": [
            row("Spencer Steer", "R", "+390", 80, "⭐ 🌕 💣", ["vs Rodriguez"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 88.1 mph EV. Rodriguez RHB split +0.30, HR risk -0.38. pitcher risk below avg (-0.38).""", blast="high"),
            row("Ketel Marte", "S", "+281", 89, "⭐ 🌕 💣", ["vs Lodolo"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 95.0 mph EV. Lodolo RHB split +2.05, HR risk 1.06.""", blast="high"),
            row("Ryan Waldschmidt", "R", "+600", 70, "", ["vs Lodolo"], """0 HR, 2 near-HR, 89.7 mph EV. Lodolo RHB split +2.05, HR risk 1.06.""", blast="good"),
            row("Tommy Troy", "R", "+790", 75, "💎", ["vs Lodolo"], """Worst Pickz Hidden Gem. 0 HR, 99.4 mph EV. Lodolo RHB split +2.05, HR risk 1.06. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "ATL @ NYM - Spencer Strider (R, ATL) vs Nolan McLean (R, NYM)",
        "description": "Tail key data: Park boost +8% (stadium -2%, weather +9%). Strider (HR risk 0.91, vs LHB +1.11, vs RHB -0.33). McLean (HR risk 0.10, vs LHB +0.11, vs RHB +0.01).",
        "rows": [
            row("Jared Young", "L", "+539", 85, "🌕 💣", ["vs Strider"], """2 HR, 3 near-HR, 92.7 mph EV. Strider LHB split +1.11, HR risk 0.91.""", blast="high"),
            row("Luis Torrens", "R", "+427", 77, "", ["vs Strider"], """0 HR, 2 near-HR, 97.0 mph EV. Strider RHB split -0.33, HR risk 0.91. slight split headwind (-0.33).""", blast="good"),
            row("Matt Olson", "L", "+394", 80, "⭐", ["vs McLean"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.2 mph EV. McLean LHB split +0.11, HR risk 0.10.""", blast="good"),
        ],
    },
    {
        "title": "CHC @ SF - Javier Assad (R, CHC) vs Landen Roupp (R, SF)",
        "description": "Tail key data: Park boost -17% (stadium -15%, weather -2%). Assad (HR risk -0.46, vs LHB +0.57, vs RHB -1.09). Roupp (HR risk -0.72, vs LHB -0.80, vs RHB -0.00).",
        "rows": [
            row("Eric Haase", "R", "N/A", 92, "🚀 🌕 💣 💎", ["vs Assad"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 101.1 mph EV. Assad RHB split -1.09, HR risk -0.46. tough split lane (-1.09); pitcher suppresses HR (-0.46).""", blast="high"),
            row("Willy Adames", "R", "+559", 72, "", ["vs Assad"], """0 HR, 3 near-HR, 89.9 mph EV. Assad RHB split -1.09, HR risk -0.46. tough split lane (-1.09); pitcher suppresses HR (-0.46).""", blast="good"),
            row("Bryce Eldridge", "L", "+625", 77, "", ["vs Assad"], """1 HR, 2 near-HR, 92.9 mph EV. Assad LHB split +0.57, HR risk -0.46. pitcher suppresses HR (-0.46); park/weather net drag (-17%).""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+500", 78, "", ["vs Roupp"], """1 HR, 2 near-HR, 93.5 mph EV. Roupp LHB split -0.80, HR risk -0.72. tough split lane (-0.80); pitcher suppresses HR (-0.72).""", blast="good"),
            row("Ian Happ", "S", "+710", 78, "", ["vs Roupp"], """1 HR, 2 near-HR, 94.4 mph EV. Roupp RHB split -0.00, HR risk -0.72. pitcher suppresses HR (-0.72); park/weather net drag (-17%).""", blast="good"),
            row("Seiya Suzuki", "R", "+730", 70, "", ["vs Roupp"], """1 HR, 1 near-HR, 88.4 mph EV. Roupp RHB split -0.00, HR risk -0.72. pitcher suppresses HR (-0.72); park/weather net drag (-17%).""", blast="good"),
        ],
    },
    {
        "title": "COL @ ATH - Kyle Freeland (L, COL) vs Gage Jump (L, ATH)",
        "description": "Tail key data: Park boost +112% (stadium +90%, weather +22%). Away starter risk unavailable. Jump (HR risk -1.94, vs LHB -1.30, vs RHB -1.28).",
        "rows": [
            row("Nick Kurtz", "L", "+168", 98, "🚀 ⭐ 🌕 💣", ["vs Freeland"], """Worst Pickz Favorite. 4 HR, 3 near-HR, 101.5 mph EV. Freeland split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Shea Langeliers", "R", "+154", 83, "🌕 💣", ["vs Freeland"], """2 HR, 2 near-HR, 93.4 mph EV. Freeland split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Henry Bolte", "R", "+425", 82, "🚀 💎", ["vs Freeland"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 104.9 mph EV. Freeland split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Zack Gelof", "R", "+310", 74, "", ["vs Freeland"], """1 HR, 1 near-HR, 92.1 mph EV. Freeland split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Colby Thomas", "R", "+270", 77, "", ["vs Freeland"], """1 HR, 1 near-HR, 95.4 mph EV. Freeland split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Kyle Karros", "R", "+548", 64, "", ["vs Jump"], """0 HR, 1 near-HR, 86.1 mph EV. Jump RHB split -1.28, HR risk -1.94. tough split lane (-1.28); pitcher suppresses HR (-1.94)."""),
            row("Hunter Goodman", "R", "+201", 70, "", ["vs Jump"], """1 HR, 1 near-HR, 86.1 mph EV. Jump RHB split -1.28, HR risk -1.94. tough split lane (-1.28); pitcher suppresses HR (-1.94).""", blast="good"),
            row("Edouard Julien", "L", "N/A", 64, "", ["vs Jump"], """0 HR, 1 near-HR, 83.3 mph EV. Jump LHB split -1.30, HR risk -1.94. tough split lane (-1.30); pitcher suppresses HR (-1.94)."""),
        ],
    },
    {
        "title": "DET @ CLE - Jack Flaherty (R, DET) vs Tanner Bibee (R, CLE)",
        "description": "Tail key data: Park boost +6% (stadium -2%, weather +9%). Flaherty (HR risk 0.20, vs LHB -0.11, vs RHB +0.67). Bibee (HR risk 0.86, vs LHB +0.99, vs RHB +0.33).",
        "rows": [
            row("Kyle Manzardo", "L", "+487", 78, "🌕 💣", ["vs Flaherty"], """2 HR, 2 near-HR, 88.1 mph EV. Flaherty LHB split -0.11, HR risk 0.20. slight split headwind (-0.11).""", blast="high"),
            row("Riley Greene", "L", "+400", 96, "⭐ 🌕 💣", ["vs Bibee"], """Worst Pickz Favorite. 3 HR, 5 near-HR, 95.7 mph EV. Bibee LHB split +0.99, HR risk 0.86.""", blast="high"),
            row("Dillon Dingler", "R", "+490", 96, "🌕 💣", ["vs Bibee"], """3 HR, 5 near-HR, 95.7 mph EV. Bibee RHB split +0.33, HR risk 0.86.""", blast="high"),
            row("Kerry Carpenter", "L", "+391", 78, "🌕 💣", ["vs Bibee"], """2 HR, 2 near-HR, 88.0 mph EV. Bibee LHB split +0.99, HR risk 0.86.""", blast="high"),
        ],
    },
    {
        "title": "HOU @ KC - Tatsuya Imai 🧤 (R, HOU) vs Luinder Avila (R, KC)",
        "description": "Tail key data: Park boost +3% (stadium +12%, weather -8%). Imai 🧤 (HR risk 1.01, vs LHB +1.27, vs RHB -0.21). Avila (HR risk -1.18, vs LHB -0.38, vs RHB -1.35).",
        "rows": [
            row("Jac Caglianone", "L", "+525", 80, "🚀 ⭐", ["vs Imai"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 100.5 mph EV. Imai LHB split +1.27, HR risk 1.01. weather carry headwind (-8%).""", blast="good"),
            row("Vinnie Pasquantino", "L", "+529", 78, "", ["vs Imai"], """1 HR, 1 near-HR, 96.4 mph EV. Imai LHB split +1.27, HR risk 1.01. weather carry headwind (-8%).""", blast="good"),
            row("Michael Massey", "L", "+650", 80, "🌕 💣", ["vs Imai"], """2 HR, 2 near-HR, 89.7 mph EV. Imai LHB split +1.27, HR risk 1.01. weather carry headwind (-8%).""", blast="high"),
            row("Yordan Alvarez", "L", "+345", 88, "⭐ 🌕 💣", ["vs Avila"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 96.5 mph EV. Avila LHB split -0.38, HR risk -1.18. slight split headwind (-0.38); pitcher suppresses HR (-1.18).""", blast="high"),
            row("Isaac Paredes", "R", "+540", 83, "🌕 💣", ["vs Avila"], """2 HR, 2 near-HR, 93.3 mph EV. Avila RHB split -1.35, HR risk -1.18. tough split lane (-1.35); pitcher suppresses HR (-1.18).""", blast="high"),
            row("Cam Smith", "R", "+730", 76, "🚀 💎", ["vs Avila"], """Worst Pickz Hidden Gem. 0 HR, 100.6 mph EV. Avila RHB split -1.35, HR risk -1.18. tough split lane (-1.35); pitcher suppresses HR (-1.18).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ CWS - Roki Sasaki (R, LAD) vs Anthony Kay (L, CWS)",
        "description": "Tail key data: Park boost data unavailable. Sasaki (HR risk 0.22, vs LHB -0.03, vs RHB +0.61). Kay (HR risk 0.42, vs LHB -0.51, vs RHB +0.90).",
        "rows": [
            row("Colson Montgomery", "L", "+350", 81, "⭐ 🌕 💣", ["vs Sasaki"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.3 mph EV. Sasaki LHB split -0.03, HR risk 0.22. slight split headwind (-0.03).""", blast="high"),
            row("Miguel Vargas", "R", "+425", 74, "💎", ["vs Sasaki"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 88.5 mph EV. Sasaki RHB split +0.61, HR risk 0.22.""", blast="good"),
            row("Jacob Gonzalez", "L", "+680", 72, "💎", ["vs Sasaki"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.5 mph EV. Sasaki LHB split -0.03, HR risk 0.22. slight split headwind (-0.03).""", blast="good"),
            row("Braden Montgomery", "S", "N/A", 78, "🚀", ["vs Sasaki"], """0 HR, 1 near-HR, 105.4 mph EV. Sasaki RHB split +0.61, HR risk 0.22. limited recent HR events.""", blast="good"),
            row("Andy Pages", "R", "+432", 86, "🌕 💣", ["vs Kay"], """2 HR, 3 near-HR, 94.1 mph EV. Kay RHB split +0.90, HR risk 0.42.""", blast="high"),
            row("Shohei Ohtani", "L", "+270", 85, "⭐ 🌕 💣", ["vs Kay"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 93.2 mph EV. Kay LHB split -0.51, HR risk 0.42. tough split lane (-0.51).""", blast="high"),
            row("Mookie Betts", "R", "+516", 73, "", ["vs Kay"], """1 HR, 1 near-HR, 90.9 mph EV. Kay RHB split +0.90, HR risk 0.42.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ PIT - Sandy Alcantara (R, MIA) vs Braxton Ashcraft (R, PIT)",
        "description": "Tail key data: Park boost -7% (stadium -16%, weather +9%). Alcantara (HR risk 0.23, vs LHB +0.18, vs RHB +0.21). Ashcraft (HR risk -0.38, vs LHB +0.08, vs RHB -0.57).",
        "rows": [
            row("Tyler Callihan", "L", "+730", 85, "⭐ 🌕 💣", ["vs Alcantara"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.6 mph EV. Alcantara LHB split +0.18, HR risk 0.23. park/weather net drag (-7%).""", blast="high"),
            row("Endy Rodriguez", "S", "+820", 75, "💎", ["vs Alcantara"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.2 mph EV. Alcantara RHB split +0.21, HR risk 0.23. park/weather net drag (-7%).""", blast="good"),
            row("Bryan Reynolds", "S", "+725", 75, "", ["vs Alcantara"], """0 HR, 1 near-HR, 96.7 mph EV. Alcantara RHB split +0.21, HR risk 0.23. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
            row("Kyle Stowers", "L", "+478", 79, "⭐", ["vs Ashcraft"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.6 mph EV. Ashcraft LHB split +0.08, HR risk -0.38. pitcher risk below avg (-0.38); park/weather net drag (-7%).""", blast="good"),
            row("Owen Caissie", "L", "+790", 70, "", ["vs Ashcraft"], """1 HR, 1 near-HR, 88.5 mph EV. Ashcraft LHB split +0.08, HR risk -0.38. pitcher risk below avg (-0.38); park/weather net drag (-7%).""", blast="good"),
            row("Heriberto Hernandez", "R", "N/A", 74, "", ["vs Ashcraft"], """1 HR, 1 near-HR, 91.9 mph EV. Ashcraft RHB split -0.57, HR risk -0.38. tough split lane (-0.57); pitcher risk below avg (-0.38).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ TOR - Ryan Weathers 🧤 (L, NYY) vs Trey Yesavage (R, TOR)",
        "description": "Tail key data: Park boost +15% (stadium +7%, weather +8%). Weathers 🧤 (HR risk 1.17, vs LHB +0.83, vs RHB +1.19). Yesavage (HR risk -0.92, vs LHB -0.81, vs RHB -0.26).",
        "rows": [
            row("Kazuma Okamoto", "R", "+432", 82, "⭐ 🌕 💣", ["vs Weathers"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.4 mph EV. Weathers RHB split +1.19, HR risk 1.17.""", blast="high"),
            row("Ben Rice", "L", "+371", 76, "", ["vs Yesavage"], """0 HR, 1 near-HR, 98.5 mph EV. Yesavage LHB split -0.81, HR risk -0.92. tough split lane (-0.81); pitcher suppresses HR (-0.92).""", blast="good"),
            row("Ryan McMahon", "L", "+710", 70, "", ["vs Yesavage"], """1 HR, 1 near-HR, 84.3 mph EV. Yesavage LHB split -0.81, HR risk -0.92. tough split lane (-0.81); pitcher suppresses HR (-0.92).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ MIL - Andrew Painter (R, PHI) vs Jacob Misiorowski (R, MIL)",
        "description": "Tail key data: Park boost +30% (stadium +11%, weather +19%). Painter (HR risk 0.75, vs LHB +0.49, vs RHB +0.73). Misiorowski (HR risk -1.55, vs LHB -1.08, vs RHB -1.01).",
        "rows": [
            row("Gary Sanchez", "R", "N/A", 85, "🌕 💣", ["vs Painter"], """2 HR, 2 near-HR, 95.0 mph EV. Painter RHB split +0.73, HR risk 0.75.""", blast="high"),
            row("Jake Bauers", "L", "+410", 81, "🌕 💣", ["vs Painter"], """2 HR, 2 near-HR, 91.3 mph EV. Painter LHB split +0.49, HR risk 0.75.""", blast="high"),
            row("Garrett Mitchell", "L", "+600", 77, "⭐", ["vs Painter"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 96.9 mph EV. Painter LHB split +0.49, HR risk 0.75.""", blast="good"),
            row("Jackson Chourio", "R", "+434", 91, "🌕 💣", ["vs Painter"], """3 HR, 4 near-HR, 93.4 mph EV. Painter RHB split +0.73, HR risk 0.75.""", blast="high"),
            row("Edmundo Sosa", "R", "N/A", 73, "", ["vs Misiorowski"], """0 HR, 1 near-HR, 95.4 mph EV. Misiorowski RHB split -1.01, HR risk -1.55. tough split lane (-1.01); pitcher suppresses HR (-1.55).""", blast="good"),
            row("Bryce Harper", "L", "+470", 74, "", ["vs Misiorowski"], """1 HR, 1 near-HR, 91.5 mph EV. Misiorowski LHB split -1.08, HR risk -1.55. tough split lane (-1.08); pitcher suppresses HR (-1.55).""", blast="good"),
            row("J.T. Realmuto", "R", "+1000", 70, "", ["vs Misiorowski"], """1 HR, 1 near-HR, 86.3 mph EV. Misiorowski RHB split -1.01, HR risk -1.55. tough split lane (-1.01); pitcher suppresses HR (-1.55).""", blast="good"),
            row("Brandon Marsh", "L", "+820", 83, "🌕 💣", ["vs Misiorowski"], """2 HR, 2 near-HR, 92.6 mph EV. Misiorowski LHB split -1.08, HR risk -1.55. tough split lane (-1.08); pitcher suppresses HR (-1.55).""", blast="high"),
            row("Kyle Schwarber", "L", "+346", 74, "", ["vs Misiorowski"], """0 HR, 97.9 mph EV. Misiorowski LHB split -1.08, HR risk -1.55. tough split lane (-1.08); pitcher suppresses HR (-1.55).""", blast="good"),
        ],
    },
    {
        "title": "SD @ BAL - Griffin Canning (R, SD) vs Shane Baz (R, BAL)",
        "description": "Tail key data: Park boost +6% (stadium -2%, weather +7%). Canning (HR risk 0.73, vs LHB +1.28, vs RHB -1.00). Baz (HR risk -0.02, vs LHB -0.05, vs RHB +0.05).",
        "rows": [
            row("Colton Cowser", "L", "+535", 81, "🌕 💣 💎", ["vs Canning"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 89.4 mph EV. Canning LHB split +1.28, HR risk 0.73.""", blast="high"),
            row("Samuel Basallo", "L", "+410", 76, "", ["vs Canning"], """0 HR, 1 near-HR, 98.1 mph EV. Canning LHB split +1.28, HR risk 0.73. limited recent HR events.""", blast="good"),
            row("Pete Alonso", "R", "+358", 83, "🌕 💣", ["vs Canning"], """2 HR, 2 near-HR, 92.9 mph EV. Canning RHB split -1.00, HR risk 0.73. tough split lane (-1.00).""", blast="high"),
            row("Fernando Tatis Jr.", "R", "+390", 75, "⭐", ["vs Baz"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 94.6 mph EV. Baz RHB split +0.05, HR risk -0.02. pitcher risk below avg (-0.02).""", blast="good"),
            row("Jackson Merrill", "L", "+410", 62, "", ["vs Baz"], """0 HR, 79.6 mph EV. Baz LHB split -0.05, HR risk -0.02. slight split headwind (-0.05); pitcher risk below avg (-0.02)."""),
            row("Manny Machado", "R", "+431", 76, "", ["vs Baz"], """1 HR, 2 near-HR, 91.6 mph EV. Baz RHB split +0.05, HR risk -0.02. pitcher risk below avg (-0.02).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ WSH - Bryce Miller (R, SEA) vs Zack Littell (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Miller (HR risk -0.68, vs LHB -1.37, vs RHB +0.74). Littell (HR risk 0.38, vs LHB +0.52, vs RHB +0.06).",
        "rows": [
            row("Daylen Lile", "L", "+680", 78, "⭐", ["vs Miller"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.6 mph EV. Miller LHB split -1.37, HR risk -0.68. tough split lane (-1.37); pitcher suppresses HR (-0.68).""", blast="good"),
            row("James Wood", "L", "+330", 78, "⭐", ["vs Miller"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.8 mph EV. Miller LHB split -1.37, HR risk -0.68. tough split lane (-1.37); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Luis Garcia Jr.", "L", "+540", 80, "💎", ["vs Miller"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 95.7 mph EV. Miller LHB split -1.37, HR risk -0.68. tough split lane (-1.37); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Dominic Canzone", "L", "+440", 81, "", ["vs Littell"], """1 HR, 1 near-HR, 99.2 mph EV. Littell LHB split +0.52, HR risk 0.38.""", blast="good"),
            row("Luke Raley", "L", "+360", 82, "🌕 💣", ["vs Littell"], """2 HR, 3 near-HR, 89.7 mph EV. Littell LHB split +0.52, HR risk 0.38.""", blast="high"),
        ],
    },
    {
        "title": "STL @ MIN - Kyle Leahy (R, STL) vs Joe Ryan (R, MIN)",
        "description": "Tail key data: Park boost -1% (stadium -7%, weather +6%). Leahy (HR risk 0.11, vs LHB +0.81, vs RHB -0.57). Ryan (HR risk 0.43, vs LHB +0.46, vs RHB +0.10).",
        "rows": [
            row("Victor Caratini", "S", "+880", 73, "💎", ["vs Leahy"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 88.8 mph EV. Leahy RHB split -0.57, HR risk 0.11. tough split lane (-0.57); park suppresses carry (-7%).""", blast="good"),
            row("Byron Buxton", "R", "+285", 80, "🌕 💣", ["vs Leahy"], """2 HR, 2 near-HR, 89.7 mph EV. Leahy RHB split -0.57, HR risk 0.11. tough split lane (-0.57); park suppresses carry (-7%).""", blast="high"),
            row("Alec Burleson", "L", "+425", 80, "⭐", ["vs Ryan"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.9 mph EV. Ryan LHB split +0.46, HR risk 0.43. park suppresses carry (-7%).""", blast="good"),
            row("Lars Nootbaar", "L", "+500", 81, "", ["vs Ryan"], """1 HR, 2 near-HR, 97.2 mph EV. Ryan LHB split +0.46, HR risk 0.43. park suppresses carry (-7%).""", blast="good"),
            row("Jordan Walker", "R", "+410", 69, "", ["vs Ryan"], """0 HR, 93.1 mph EV. Ryan RHB split +0.10, HR risk 0.43. park suppresses carry (-7%); limited recent HR events.""", blast="good"),
            row("JJ Wetherholt", "L", "+475", 73, "", ["vs Ryan"], """0 HR, 2 near-HR, 93.4 mph EV. Ryan LHB split +0.46, HR risk 0.43. park suppresses carry (-7%).""", blast="good"),
        ],
    },
    {
        "title": "TB @ LAA - Shane McClanahan (L, TB) vs Samuel Aldegheri (L, LAA)",
        "description": "Tail key data: Park boost +14% (stadium +8%, weather +6%). McClanahan (HR risk -0.43, vs LHB -1.13, vs RHB +0.17). Aldegheri (HR risk -0.23, vs LHB +0.41, vs RHB +0.07).",
        "rows": [
            row("Zach Neto", "R", "+521", 70, "", ["vs McClanahan"], """1 HR, 1 near-HR, 87.0 mph EV. McClanahan RHB split +0.17, HR risk -0.43. pitcher suppresses HR (-0.43); lighter EV form (87.0 mph).""", blast="good"),
            row("Mike Trout", "R", "+419", 74, "⭐", ["vs McClanahan"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.4 mph EV. McClanahan RHB split +0.17, HR risk -0.43. pitcher suppresses HR (-0.43).""", blast="good"),
            row("Oswald Peraza", "R", "+680", 70, "", ["vs McClanahan"], """1 HR, 1 near-HR, 86.9 mph EV. McClanahan RHB split +0.17, HR risk -0.43. pitcher suppresses HR (-0.43); lighter EV form (86.9 mph).""", blast="good"),
            row("Logan O'Hoppe", "R", "+720", 70, "", ["vs McClanahan"], """0 HR, 2 near-HR, 89.9 mph EV. McClanahan RHB split +0.17, HR risk -0.43. pitcher suppresses HR (-0.43).""", blast="good"),
            row("Hunter Feduccia", "L", "N/A", 73, "", ["vs Aldegheri"], """0 HR, 96.9 mph EV. Aldegheri LHB split +0.41, HR risk -0.23. pitcher risk below avg (-0.23); limited recent HR events.""", blast="good"),
            row("Junior Caminero", "R", "+287", 74, "", ["vs Aldegheri"], """0 HR, 98.1 mph EV. Aldegheri RHB split +0.07, HR risk -0.23. pitcher risk below avg (-0.23); limited recent HR events.""", blast="good"),
            row("Yandy Diaz", "R", "+371", 77, "", ["vs Aldegheri"], """1 HR, 3 near-HR, 90.6 mph EV. Aldegheri RHB split +0.07, HR risk -0.23. pitcher risk below avg (-0.23).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ BOS - Jack Leiter (R, TEX) vs Sonny Gray (R, BOS)",
        "description": "Tail key data: Park boost -2% (stadium -8%, weather +7%). Leiter (HR risk 0.47, vs LHB +0.55, vs RHB +0.03). Gray (HR risk -0.16, vs LHB -0.01, vs RHB -0.48).",
        "rows": [
            row("Wilyer Abreu", "L", "+430", 76, "⭐", ["vs Leiter"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 91.8 mph EV. Leiter LHB split +0.55, HR risk 0.47. park suppresses carry (-8%).""", blast="good"),
            row("Jarren Duran", "L", "+590", 82, "🌕 💣", ["vs Leiter"], """2 HR, 3 near-HR, 89.6 mph EV. Leiter LHB split +0.55, HR risk 0.47. park suppresses carry (-8%).""", blast="high"),
            row("Mickey Gasper", "S", "+790", 75, "", ["vs Leiter"], """0 HR, 4 near-HR, 90.9 mph EV. Leiter RHB split +0.03, HR risk 0.47. park suppresses carry (-8%).""", blast="good"),
            row("Wyatt Langford", "R", "+490", 70, "", ["vs Gray"], """0 HR, 93.6 mph EV. Gray RHB split -0.48, HR risk -0.16. tough split lane (-0.48); pitcher risk below avg (-0.16).""", blast="good"),
            row("Jake Burger", "R", "+470", 65, "", ["vs Gray"], """0 HR, 1 near-HR, 88.8 mph EV. Gray RHB split -0.48, HR risk -0.16. tough split lane (-0.48); pitcher risk below avg (-0.16)."""),
            row("Corey Seager", "L", "+390", 66, "", ["vs Gray"], """0 HR, 1 near-HR, 89.7 mph EV. Gray LHB split -0.01, HR risk -0.16. slight split headwind (-0.01); pitcher risk below avg (-0.16)."""),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-12")

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

    out = ROOT / '_games-0612.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
