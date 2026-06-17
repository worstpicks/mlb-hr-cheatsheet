#!/usr/bin/env python3
"""Generate games[] block for 2026-06-17 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Colt Keith (L)",
    "Heriberto Hernandez (R)",
    "Jake Bauers (L)",
    "Jose Siri (R)",
    "Ketel Marte (S)",
    "Matt McLain (R)",
    "Mookie Betts (R)",
    "Nick Kurtz (L)",
    "Seiya Suzuki (R)",
    "Willi Castro (S)",
}

GEMS = {
    "Brice Matthews (R)",
    "J.P. Crawford (L)",
    "James Wood (L)",
    "Tommy Troy (R)",
    "Tyler Callihan (L)",
    "Yohendrick Pinango (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BAL",
    "Alec Bohm (R)": "PHI",
    "Alec Burleson (L)": "STL",
    "Alejandro Kirk (R)": "TOR",
    "Andrew Benintendi (L)": "CWS",
    "Blaze Jordan (R)": "STL",
    "Brandon Marsh (L)": "PHI",
    "Brice Matthews (R)": "HOU",
    "Bryan Reynolds (S)": "PIT",
    "Carson Benge (L)": "NYM",
    "Ceddanne Rafaela (R)": "BOS",
    "Cedric Mullins (L)": "TB",
    "Cole Carrigg (S)": "COL",
    "Colt Keith (L)": "DET",
    "Corbin Carroll (L)": "ARI",
    "Davis Schneider (R)": "TOR",
    "Dominic Canzone (L)": "SEA",
    "Endy Rodriguez (S)": "PIT",
    "Fernando Tatis Jr. (R)": "SD",
    "Freddie Freeman (L)": "LAD",
    "Garrett Mitchell (L)": "MIL",
    "Gary Sanchez (R)": "MIL",
    "Gleyber Torres (R)": "DET",
    "Heriberto Hernandez (R)": "MIA",
    "Ian Happ (S)": "CHC",
    "Isaac Paredes (R)": "HOU",
    "J.P. Crawford (L)": "SEA",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Holliday (L)": "BAL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jeremiah Jackson (R)": "BAL",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Jose Siri (R)": "LAA",
    "Juan Soto (L)": "NYM",
    "Ketel Marte (S)": "ARI",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Schwarber (L)": "PHI",
    "Lars Nootbaar (L)": "STL",
    "Luke Raley (L)": "SEA",
    "Matt McLain (R)": "CIN",
    "Max Muncy (L)": "LAD",
    "Michael Busch (L)": "CHC",
    "Michael Massey (L)": "KC",
    "Miguel Vargas (R)": "CWS",
    "Mookie Betts (R)": "LAD",
    "Nick Kurtz (L)": "ATH",
    "Oswald Peraza (R)": "LAA",
    "Patrick Bailey (S)": "CLE",
    "Paul Goldschmidt (R)": "NYY",
    "Pete Alonso (R)": "BAL",
    "Randal Grichuk (R)": "CWS",
    "Riley Greene (L)": "DET",
    "Rodolfo Durán (R)": "SD",
    "Seiya Suzuki (R)": "CHC",
    "Spencer Torkelson (R)": "DET",
    "TJ Rumfield (L)": "COL",
    "Tommy Troy (R)": "ARI",
    "Tyler Callihan (L)": "PIT",
    "Tyler O'Neill (R)": "BAL",
    "Willi Castro (S)": "COL",
    "Wilyer Abreu (L)": "BOS",
    "Yohendrick Pinango (L)": "TOR",
    "Zach Neto (R)": "LAA",
}

BUM_RISK_MIN = 0.95

BUM_PITCHERS = {
    "Civale",
    "Scherzer",
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
        "title": "BAL @ SEA - Kyle Bradish (R, BAL) vs George Kirby (R, SEA)",
        "description": "Tail key data: Park boost -5% (stadium +0%, weather -5%). Bradish (HR risk 0.39, vs LHB +0.33, vs RHB +0.53). Kirby (HR risk 0.06, vs LHB +0.11, vs RHB +0.15).",
        "rows": [
            row("J.P. Crawford", "L", "+675", 89, "🌕 💣 💎", ["vs Bradish"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 92.8 mph EV. Bradish LHB split +0.33, HR risk 0.39. park/weather net drag (-5%).""", blast="high"),
            row("Dominic Canzone", "L", "+550", 85, "🌕 💣", ["vs Bradish"], """2 HR, 2 near-HR, 95.3 mph EV. Bradish LHB split +0.33, HR risk 0.39. park/weather net drag (-5%).""", blast="high"),
            row("Luke Raley", "L", "+450", 79, "", ["vs Bradish"], """1 HR, 2 near-HR, 94.6 mph EV. Bradish LHB split +0.33, HR risk 0.39. park/weather net drag (-5%).""", blast="good"),
            row("Pete Alonso", "R", "+361", 90, "🌕 💣", ["vs Kirby"], """3 HR, 3 near-HR, 93.5 mph EV. Kirby RHB split +0.15, HR risk 0.06. park/weather net drag (-5%).""", blast="high"),
            row("Adley Rutschman", "S", "+660", 73, "", ["vs Kirby"], """1 HR, 1 near-HR, 90.9 mph EV. Kirby RHB split +0.15, HR risk 0.06. park/weather net drag (-5%).""", blast="good"),
            row("Jackson Holliday", "L", "+900", 72, "", ["vs Kirby"], """1 HR, 2 near-HR, 87.2 mph EV. Kirby LHB split +0.11, HR risk 0.06. park/weather net drag (-5%); lighter EV form (87.2 mph).""", blast="good"),
            row("Tyler O'Neill", "R", "N/A", 64, "", ["vs Kirby"], """0 HR, 1 near-HR, 86.3 mph EV. Kirby RHB split +0.15, HR risk 0.06. park/weather net drag (-5%); limited recent HR events."""),
            row("Jeremiah Jackson", "R", "N/A", 77, "", ["vs Kirby"], """1 HR, 1 near-HR, 94.9 mph EV. Kirby RHB split +0.15, HR risk 0.06. park/weather net drag (-5%).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ MIL - Gavin Williams (R, CLE) vs Brandon Sproat (R, MIL)",
        "description": "Tail key data: Park boost +6% (stadium +11%, weather -4%). Williams (HR risk 0.70, vs LHB +0.63, vs RHB +0.46). Sproat (HR risk 0.21, vs LHB -0.59, vs RHB +1.13).",
        "rows": [
            row("Jake Bauers", "L", "+490", 96, "⭐ 🌕 💣", ["vs Williams"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 99.8 mph EV. Williams LHB split +0.63, HR risk 0.70. weather carry headwind (-4%).""", blast="high"),
            row("Gary Sanchez", "R", "N/A", 88, "🌕 💣", ["vs Williams"], """2 HR, 3 near-HR, 96.4 mph EV. Williams RHB split +0.46, HR risk 0.70. weather carry headwind (-4%).""", blast="high"),
            row("Garrett Mitchell", "L", "+590", 74, "", ["vs Williams"], """0 HR, 3 near-HR, 92.3 mph EV. Williams LHB split +0.63, HR risk 0.70. weather carry headwind (-4%).""", blast="good"),
            row("Kyle Manzardo", "L", "N/A", 64, "", ["vs Sproat"], """0 HR, 1 near-HR, 88.3 mph EV. Sproat LHB split -0.59, HR risk 0.21. tough split lane (-0.59); weather carry headwind (-4%)."""),
            row("Patrick Bailey", "S", "N/A", 72, "", ["vs Sproat"], """0 HR, 1 near-HR, 94.2 mph EV. Sproat RHB split +1.13, HR risk 0.21. weather carry headwind (-4%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "COL @ CHC - Sean Sullivan (L, COL) vs Javier Assad (R, CHC)",
        "description": "Tail key data: Park boost +23% (stadium -1%, weather +24%). Away starter risk unavailable. Assad (HR risk -0.65, vs LHB +0.27, vs RHB -1.16).",
        "rows": [
            row("Seiya Suzuki", "R", "+374", 74, "⭐", ["vs Sullivan"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.2 mph EV. Sullivan split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Ian Happ", "S", "+370", 79, "", ["vs Sullivan"], """1 HR, 1 near-HR, 96.7 mph EV. Sullivan split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Michael Busch", "L", "+508", 71, "", ["vs Sullivan"], """0 HR, 94.9 mph EV. Sullivan split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Cole Carrigg", "S", "+610", 72, "", ["vs Assad"], """1 HR, 1 near-HR, 90.2 mph EV. Assad RHB split -1.16, HR risk -0.65. tough split lane (-1.16); pitcher suppresses HR (-0.65).""", blast="good"),
            row("TJ Rumfield", "L", "+730", 79, "🌕 💣", ["vs Assad"], """2 HR, 2 near-HR, 89.2 mph EV. Assad LHB split +0.27, HR risk -0.65. pitcher suppresses HR (-0.65).""", blast="high"),
            row("Willi Castro", "S", "+630", 72, "⭐", ["vs Assad"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 89.8 mph EV. Assad RHB split -1.16, HR risk -0.65. tough split lane (-1.16); pitcher suppresses HR (-0.65).""", blast="good"),
        ],
    },
    {
        "title": "CWS @ NYY - Anthony Kay (L, CWS) vs Carlos Rodon (L, NYY)",
        "description": "Tail key data: Park boost data unavailable. Kay (HR risk 0.25, vs LHB -0.19, vs RHB +0.42). Rodon (HR risk -0.36, vs LHB +0.34, vs RHB -0.53).",
        "rows": [
            row("Jazz Chisholm Jr.", "L", "+470", 92, "🌕 💣", ["vs Kay"], """2 HR, 4 near-HR, 98.2 mph EV. Kay LHB split -0.19, HR risk 0.25. slight split headwind (-0.19).""", blast="high"),
            row("Paul Goldschmidt", "R", "+464", 70, "", ["vs Kay"], """1 HR, 1 near-HR, 86.4 mph EV. Kay RHB split +0.42, HR risk 0.25. lighter EV form (86.4 mph).""", blast="good"),
            row("Randal Grichuk", "R", "+492", 78, "🌕 💣", ["vs Rodon"], """2 HR, 2 near-HR, 86.1 mph EV. Rodon RHB split -0.53, HR risk -0.36. tough split lane (-0.53); pitcher risk below avg (-0.36).""", blast="high"),
            row("Andrew Benintendi", "L", "N/A", 62, "", ["vs Rodon"], """0 HR, 72.8 mph EV. Rodon LHB split +0.34, HR risk -0.36. pitcher risk below avg (-0.36); limited recent HR events."""),
            row("Miguel Vargas", "R", "+445", 74, "", ["vs Rodon"], """1 HR, 1 near-HR, 91.5 mph EV. Rodon RHB split -0.53, HR risk -0.36. tough split lane (-0.53); pitcher risk below avg (-0.36).""", blast="good"),
        ],
    },
    {
        "title": "DET @ HOU - Casey Mize (R, DET) vs Peter Lambert (R, HOU)",
        "description": "Tail key data: Park boost +3% (stadium +4%, weather -1%). Mize (HR risk -0.91, vs LHB -0.77, vs RHB -0.34). Lambert (HR risk -0.01, vs LHB -1.01, vs RHB +0.89).",
        "rows": [
            row("Isaac Paredes", "R", "+490", 83, "🌕 💣", ["vs Mize"], """2 HR, 2 near-HR, 92.7 mph EV. Mize RHB split -0.34, HR risk -0.91. slight split headwind (-0.34); pitcher suppresses HR (-0.91).""", blast="high"),
            row("Brice Matthews", "R", "N/A", 65, "💎", ["vs Mize"], """Worst Pickz Hidden Gem. 0 HR, 90.9 mph EV. Mize RHB split -0.34, HR risk -0.91. slight split headwind (-0.34); pitcher suppresses HR (-0.91)."""),
            row("Colt Keith", "L", "+910", 88, "⭐ 🌕 💣", ["vs Lambert"], """Worst Pickz Favorite. 3 HR, 5 near-HR, 87.5 mph EV. Lambert LHB split -1.01, HR risk -0.01. tough split lane (-1.01); pitcher risk below avg (-0.01).""", blast="high"),
            row("Gleyber Torres", "R", "+488", 78, "", ["vs Lambert"], """1 HR, 1 near-HR, 96.0 mph EV. Lambert RHB split +0.89, HR risk -0.01. pitcher risk below avg (-0.01).""", blast="good"),
            row("Riley Greene", "L", "+440", 89, "🌕 💣", ["vs Lambert"], """2 HR, 4 near-HR, 94.6 mph EV. Lambert LHB split -1.01, HR risk -0.01. tough split lane (-1.01); pitcher risk below avg (-0.01).""", blast="high"),
            row("Spencer Torkelson", "R", "+411", 82, "🌕 💣", ["vs Lambert"], """2 HR, 2 near-HR, 92.2 mph EV. Lambert RHB split +0.89, HR risk -0.01. pitcher risk below avg (-0.01).""", blast="high"),
        ],
    },
    {
        "title": "KC @ WSH - Luinder Avila (R, KC) vs Zack Littell (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Avila (HR risk -0.16, vs LHB +0.45, vs RHB -0.56). Littell (HR risk 0.37, vs LHB +0.75, vs RHB -0.36).",
        "rows": [
            row("James Wood", "L", "+320", 77, "💎", ["vs Avila"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 92.6 mph EV. Avila LHB split +0.45, HR risk -0.16. pitcher risk below avg (-0.16).""", blast="good"),
            row("Jac Caglianone", "L", "+320", 77, "", ["vs Littell"], """0 HR, 1 near-HR, 99.1 mph EV. Littell LHB split +0.75, HR risk 0.37. limited recent HR events.""", blast="good"),
            row("Michael Massey", "L", "+456", 72, "", ["vs Littell"], """1 HR, 1 near-HR, 89.8 mph EV. Littell LHB split +0.75, HR risk 0.37.""", blast="good"),
        ],
    },
    {
        "title": "LAA @ ARI - Samuel Aldegheri (L, LAA) vs Eduardo Rodriguez (L, ARI)",
        "description": "Tail key data: Park boost -7% (stadium -7%, weather +0%). Aldegheri (HR risk -0.54, vs LHB +0.14, vs RHB -0.50). Rodriguez (HR risk -0.07, vs LHB -0.35, vs RHB +0.17).",
        "rows": [
            row("Ketel Marte", "S", "+375", 81, "⭐", ["vs Aldegheri"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.7 mph EV. Aldegheri RHB split -0.50, HR risk -0.54. tough split lane (-0.50); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Tommy Troy", "R", "+1000", 77, "💎", ["vs Aldegheri"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.0 mph EV. Aldegheri RHB split -0.50, HR risk -0.54. tough split lane (-0.50); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Corbin Carroll", "L", "+475", 78, "", ["vs Aldegheri"], """1 HR, 2 near-HR, 94.4 mph EV. Aldegheri LHB split +0.14, HR risk -0.54. pitcher suppresses HR (-0.54); park/weather net drag (-7%).""", blast="good"),
            row("Jose Siri", "R", "+780", 86, "⭐ 🌕 💣", ["vs Rodriguez"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.5 mph EV. Rodriguez RHB split +0.17, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-7%).""", blast="high"),
            row("Zach Neto", "R", "+554", 72, "", ["vs Rodriguez"], """1 HR, 2 near-HR, 86.4 mph EV. Rodriguez RHB split +0.17, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-7%).""", blast="good"),
            row("Oswald Peraza", "R", "+800", 80, "", ["vs Rodriguez"], """1 HR, 2 near-HR, 96.1 mph EV. Rodriguez RHB split +0.17, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-7%).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ PHI - Sandy Alcantara (R, MIA) vs Andrew Painter (R, PHI)",
        "description": "Tail key data: Park boost +32% (stadium +16%, weather +16%). Alcantara (HR risk 0.30, vs LHB +0.47, vs RHB -0.07). Painter (HR risk 0.35, vs LHB +0.60, vs RHB -0.17).",
        "rows": [
            row("Kyle Schwarber", "L", "+242", 80, "", ["vs Alcantara"], """1 HR, 1 near-HR, 97.6 mph EV. Alcantara LHB split +0.47, HR risk 0.30.""", blast="good"),
            row("Brandon Marsh", "L", "+570", 79, "🌕 💣", ["vs Alcantara"], """2 HR, 2 near-HR, 89.3 mph EV. Alcantara LHB split +0.47, HR risk 0.30.""", blast="high"),
            row("Alec Bohm", "R", "+880", 82, "🌕 💣", ["vs Alcantara"], """3 HR, 2 near-HR, 87.1 mph EV. Alcantara RHB split -0.07, HR risk 0.30. slight split headwind (-0.07); lighter EV form (87.1 mph).""", blast="high"),
            row("Heriberto Hernandez", "R", "+396", 85, "⭐ 🌕 💣", ["vs Painter"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.8 mph EV. Painter RHB split -0.17, HR risk 0.35. slight split headwind (-0.17).""", blast="high"),
        ],
    },
    {
        "title": "NYM @ CIN - Nolan McLean (R, NYM) vs Nick Lodolo (L, CIN)",
        "description": "Tail key data: Park boost +10% (stadium +12%, weather -2%). McLean (HR risk -0.13, vs LHB +0.05, vs RHB -0.22). Lodolo (HR risk 0.35, vs LHB -0.95, vs RHB +0.83).",
        "rows": [
            row("Matt McLain", "R", "+680", 89, "⭐ 🌕 💣", ["vs McLean"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 97.3 mph EV. McLean RHB split -0.22, HR risk -0.13. slight split headwind (-0.22); pitcher risk below avg (-0.13).""", blast="high"),
            row("JJ Bleday", "L", "+360", 76, "🌕 💣", ["vs McLean"], """2 HR, 1 near-HR, 88.4 mph EV. McLean LHB split +0.05, HR risk -0.13. pitcher risk below avg (-0.13).""", blast="high"),
            row("Carson Benge", "L", "+650", 79, "", ["vs Lodolo"], """1 HR, 2 near-HR, 95.4 mph EV. Lodolo LHB split -0.95, HR risk 0.35. tough split lane (-0.95).""", blast="good"),
            row("Juan Soto", "L", "+287", 71, "", ["vs Lodolo"], """1 HR, 1 near-HR, 88.9 mph EV. Lodolo LHB split -0.95, HR risk 0.35. tough split lane (-0.95).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ ATH - Braxton Ashcraft (R, PIT) vs Aaron Civale 🧤 (R, ATH)",
        "description": "Tail key data: Park boost +38% (stadium +32%, weather +6%). Ashcraft (HR risk -0.45, vs LHB +0.08, vs RHB -0.70). Civale 🧤 (HR risk 1.12, vs LHB +0.99, vs RHB +0.90).",
        "rows": [
            row("Nick Kurtz", "L", "+280", 98, "⭐ 🌕 💣", ["vs Ashcraft"], """Worst Pickz Favorite. 5 HR, 5 near-HR, 92.8 mph EV. Ashcraft LHB split +0.08, HR risk -0.45. pitcher suppresses HR (-0.45).""", blast="high"),
            row("Bryan Reynolds", "S", "+430", 84, "🌕 💣", ["vs Civale"], """2 HR, 3 near-HR, 91.6 mph EV. Civale RHB split +0.90, HR risk 1.12.""", blast="high"),
            row("Endy Rodriguez", "S", "+475", 88, "🌕 💣", ["vs Civale"], """2 HR, 2 near-HR, 98.4 mph EV. Civale RHB split +0.90, HR risk 1.12.""", blast="high"),
            row("Tyler Callihan", "L", "+490", 80, "💎", ["vs Civale"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 94.2 mph EV. Civale LHB split +0.99, HR risk 1.12.""", blast="good"),
        ],
    },
    {
        "title": "SD @ STL - Griffin Canning (R, SD) vs Kyle Leahy (R, STL)",
        "description": "Tail key data: Park boost +3% (stadium -9%, weather +12%). Away starter risk unavailable. Leahy (HR risk 0.40, vs LHB +0.62, vs RHB -0.09).",
        "rows": [
            row("Alec Burleson", "L", "+441", 89, "⭐ 🌕 💣", ["vs Canning"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 97.3 mph EV. Canning split/risk data unavailable. limited split/risk sample; park suppresses carry (-9%).""", blast="high"),
            row("Lars Nootbaar", "L", "+540", 78, "", ["vs Canning"], """1 HR, 2 near-HR, 94.0 mph EV. Canning split/risk data unavailable. limited split/risk sample; park suppresses carry (-9%).""", blast="good"),
            row("Blaze Jordan", "R", "+680", 77, "", ["vs Canning"], """1 HR, 1 near-HR, 95.0 mph EV. Canning split/risk data unavailable. limited split/risk sample; park suppresses carry (-9%).""", blast="good"),
            row("JJ Wetherholt", "L", "+520", 76, "", ["vs Canning"], """1 HR, 2 near-HR, 91.6 mph EV. Canning split/risk data unavailable. limited split/risk sample; park suppresses carry (-9%).""", blast="good"),
            row("Jordan Walker", "R", "+370", 75, "", ["vs Canning"], """0 HR, 1 near-HR, 97.3 mph EV. Canning split/risk data unavailable. limited split/risk sample; park suppresses carry (-9%).""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+520", 81, "", ["vs Leahy"], """1 HR, 2 near-HR, 97.3 mph EV. Leahy RHB split -0.09, HR risk 0.40. slight split headwind (-0.09); park suppresses carry (-9%).""", blast="good"),
            row("Jackson Merrill", "L", "+491", 73, "", ["vs Leahy"], """1 HR, 2 near-HR, 88.9 mph EV. Leahy LHB split +0.62, HR risk 0.40. park suppresses carry (-9%).""", blast="good"),
            row("Rodolfo Durán", "R", "+850", 70, "", ["vs Leahy"], """1 HR, 1 near-HR, 85.6 mph EV. Leahy RHB split -0.09, HR risk 0.40. slight split headwind (-0.09); park suppresses carry (-9%).""", blast="good"),
        ],
    },
    {
        "title": "TB @ LAD - Shane McClanahan (L, TB) vs Shohei Ohtani (R, LAD)",
        "description": "Tail key data: Park boost +21% (stadium +16%, weather +5%). McClanahan (HR risk -0.32, vs LHB -0.73, vs RHB -0.12). Ohtani (HR risk -1.07, vs LHB -0.76, vs RHB -0.79).",
        "rows": [
            row("Mookie Betts", "R", "+495", 76, "⭐", ["vs McClanahan"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.7 mph EV. McClanahan RHB split -0.12, HR risk -0.32. slight split headwind (-0.12); pitcher risk below avg (-0.32).""", blast="good"),
            row("Freddie Freeman", "L", "+490", 72, "", ["vs McClanahan"], """1 HR, 1 near-HR, 89.7 mph EV. McClanahan LHB split -0.73, HR risk -0.32. tough split lane (-0.73); pitcher risk below avg (-0.32).""", blast="good"),
            row("Max Muncy", "L", "+421", 70, "", ["vs McClanahan"], """1 HR, 1 near-HR, 87.1 mph EV. McClanahan LHB split -0.73, HR risk -0.32. tough split lane (-0.73); pitcher risk below avg (-0.32).""", blast="good"),
            row("Cedric Mullins", "L", "+578", 91, "🌕 💣", ["vs Ohtani"], """3 HR, 4 near-HR, 93.0 mph EV. Ohtani LHB split -0.76, HR risk -1.07. tough split lane (-0.76); pitcher suppresses HR (-1.07).""", blast="high"),
            row("Jonathan Aranda", "L", "+532", 64, "", ["vs Ohtani"], """0 HR, 89.7 mph EV. Ohtani LHB split -0.76, HR risk -1.07. tough split lane (-0.76); pitcher suppresses HR (-1.07)."""),
        ],
    },
    {
        "title": "TOR @ BOS - Max Scherzer 🧤 (R, TOR) vs Jake Bennett (L, BOS)",
        "description": "Tail key data: Park boost -2% (stadium -7%, weather +5%). Scherzer 🧤 (HR risk 2.43, vs LHB +1.87, vs RHB +2.15). Bennett (HR risk -0.54, vs LHB -1.36, vs RHB +0.02).",
        "rows": [
            row("Wilyer Abreu", "L", "+370", 83, "🌕 💣", ["vs Scherzer"], """2 HR, 2 near-HR, 93.4 mph EV. Scherzer LHB split +1.87, HR risk 2.43. park suppresses carry (-7%).""", blast="high"),
            row("Ceddanne Rafaela", "R", "+571", 73, "", ["vs Scherzer"], """1 HR, 2 near-HR, 88.7 mph EV. Scherzer RHB split +2.15, HR risk 2.43. park suppresses carry (-7%).""", blast="good"),
            row("Davis Schneider", "R", "+650", 70, "", ["vs Bennett"], """1 HR, 1 near-HR, 85.7 mph EV. Bennett RHB split +0.02, HR risk -0.54. pitcher suppresses HR (-0.54); park suppresses carry (-7%).""", blast="good"),
            row("Yohendrick Pinango", "L", "N/A", 73, "💎", ["vs Bennett"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.1 mph EV. Bennett LHB split -1.36, HR risk -0.54. tough split lane (-1.36); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Alejandro Kirk", "R", "+620", 76, "🚀", ["vs Bennett"], """0 HR, 101.4 mph EV. Bennett RHB split +0.02, HR risk -0.54. pitcher suppresses HR (-0.54); park suppresses carry (-7%).""", blast="good"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-17")

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

    out = ROOT / '_games-0617.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
