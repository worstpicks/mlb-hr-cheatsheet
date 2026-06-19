#!/usr/bin/env python3
"""Generate games[] block for 2026-06-19 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Colt Keith (L)",
    "Heriberto Hernandez (R)",
    "Jackson Chourio (R)",
    "Jackson Holliday (L)",
    "Matt McLain (R)",
    "Zach Neto (R)",
}

GEMS = {
    "Joe Mack (L)",
    "Spencer Jones (L)",
    "Spencer Torkelson (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Ben Rice (L)": "NYY",
    "Blaze Alexander (R)": "BAL",
    "Blaze Jordan (R)": "STL",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "CJ Abrams (L)": "WSH",
    "Cam Smith (R)": "HOU",
    "Colson Montgomery (L)": "CWS",
    "Colt Keith (L)": "DET",
    "Connor Wong (R)": "BOS",
    "Dalton Rushing (L)": "LAD",
    "Drake Baldwin (L)": "ATL",
    "Elias Diaz (R)": "TEX",
    "Eugenio Suarez (R)": "CIN",
    "Ezequiel Tovar (R)": "COL",
    "Fernando Tatis Jr. (R)": "SD",
    "Freddie Freeman (L)": "LAD",
    "Gunnar Henderson (L)": "BAL",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Isaac Paredes (R)": "HOU",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Holliday (L)": "BAL",
    "Jackson Merrill (L)": "SD",
    "James Wood (L)": "WSH",
    "Jeremiah Jackson (R)": "BAL",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "Jordan Walker (R)": "STL",
    "Jose Siri (R)": "LAA",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Ketel Marte (S)": "ARI",
    "Kyle Karros (R)": "COL",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Stowers (L)": "MIA",
    "Lane Thomas (R)": "KC",
    "Lars Nootbaar (L)": "STL",
    "Matt McLain (R)": "CIN",
    "Max Muncy (R)": "ATH",
    "Michael Massey (L)": "KC",
    "Nick Kurtz (L)": "ATH",
    "Paul Goldschmidt (R)": "NYY",
    "Randal Grichuk (R)": "CWS",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Royce Lewis (R)": "MIN",
    "Sal Stewart (R)": "CIN",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Horwitz (L)": "PIT",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Tommy Troy (R)": "ARI",
    "Trevor Larnach (L)": "MIN",
    "Tyler Soderstrom (L)": "ATH",
    "Willi Castro (S)": "COL",
    "William Contreras (R)": "MIL",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_RISK_MIN = 0.95

BUM_PITCHERS = {
    "Bibee",
    "Freeland",
    "Springs",
    "Vasquez",
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
        "title": "BAL @ LAD - Trey Gibson (R, BAL) vs Roki Sasaki (R, LAD)",
        "description": "Tail key data: Park boost +5% (stadium +18%, weather -13%). Gibson (HR risk 0.87, vs LHB +0.62, vs RHB +0.78). Sasaki (HR risk 0.18, vs LHB -0.02, vs RHB +0.31).",
        "rows": [
            row("Shohei Ohtani", "L", "+242", 88, "🌕 💣", ["vs Gibson"], """2 HR, 3 near-HR, 96.3 mph EV. Gibson LHB split +0.62, HR risk 0.87. weather carry headwind (-13%).""", blast="high"),
            row("Freddie Freeman", "L", "+470", 70, "", ["vs Gibson"], """1 HR, 1 near-HR, 87.4 mph EV. Gibson LHB split +0.62, HR risk 0.87. weather carry headwind (-13%); lighter EV form (87.4 mph).""", blast="good"),
            row("Dalton Rushing", "L", "+450", 74, "", ["vs Gibson"], """1 HR, 1 near-HR, 92.2 mph EV. Gibson LHB split +0.62, HR risk 0.87. weather carry headwind (-13%).""", blast="good"),
            row("Jackson Holliday", "L", "+810", 82, "⭐ 🌕 💣", ["vs Sasaki"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 90.3 mph EV. Sasaki LHB split -0.02, HR risk 0.18. slight split headwind (-0.02); weather carry headwind (-13%).""", blast="high"),
            row("Blaze Alexander", "R", "+890", 72, "", ["vs Sasaki"], """0 HR, 96.5 mph EV. Sasaki RHB split +0.31, HR risk 0.18. weather carry headwind (-13%); limited recent HR events.""", blast="good"),
            row("Gunnar Henderson", "L", "+489", 75, "", ["vs Sasaki"], """1 HR, 2 near-HR, 90.9 mph EV. Sasaki LHB split -0.02, HR risk 0.18. slight split headwind (-0.02); weather carry headwind (-13%).""", blast="good"),
            row("Jeremiah Jackson", "R", "N/A", 77, "", ["vs Sasaki"], """1 HR, 2 near-HR, 93.4 mph EV. Sasaki RHB split +0.31, HR risk 0.18. weather carry headwind (-13%).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ SEA - Ranger Suarez (L, BOS) vs Bryce Miller (R, SEA)",
        "description": "Tail key data: Park boost +2% (stadium +0%, weather +1%). Suarez (HR risk -1.00, vs LHB -0.01, vs RHB -0.99). Miller (HR risk -0.10, vs LHB -0.77, vs RHB +0.64).",
        "rows": [
            row("Julio Rodriguez", "R", "+476", 78, "", ["vs Suarez"], """1 HR, 2 near-HR, 94.1 mph EV. Suarez RHB split -0.99, HR risk -1.00. tough split lane (-0.99); pitcher suppresses HR (-1.00).""", blast="good"),
            row("Wilyer Abreu", "L", "+410", 76, "", ["vs Miller"], """1 HR, 1 near-HR, 93.9 mph EV. Miller LHB split -0.77, HR risk -0.10. tough split lane (-0.77); pitcher risk below avg (-0.10).""", blast="good"),
            row("Willson Contreras", "R", "+445", 80, "🌕 💣", ["vs Miller"], """2 HR, 3 near-HR, 88.1 mph EV. Miller RHB split +0.64, HR risk -0.10. pitcher risk below avg (-0.10).""", blast="high"),
            row("Connor Wong", "R", "N/A", 64, "", ["vs Miller"], """0 HR, 1 near-HR, 87.2 mph EV. Miller RHB split +0.64, HR risk -0.10. pitcher risk below avg (-0.10); limited recent HR events."""),
        ],
    },
    {
        "title": "CIN @ NYY - Rhett Lowder (R, CIN) vs Cam Schlittler (R, NYY)",
        "description": "Tail key data: Park boost +8% (stadium +4%, weather +4%). Lowder (HR risk -0.18, vs LHB +0.77, vs RHB -1.37). Schlittler (HR risk -0.69, vs LHB -0.74, vs RHB -0.41).",
        "rows": [
            row("Ben Rice", "L", "+253", 83, "⭐", ["vs Lowder"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 96.7 mph EV. Lowder LHB split +0.77, HR risk -0.18. pitcher risk below avg (-0.18).""", blast="good"),
            row("Spencer Jones", "L", "+520", 75, "💎", ["vs Lowder"], """Worst Pickz Hidden Gem. 0 HR, 99.3 mph EV. Lowder LHB split +0.77, HR risk -0.18. pitcher risk below avg (-0.18); limited recent HR events.""", blast="good"),
            row("Paul Goldschmidt", "R", "+407", 78, "🌕 💣", ["vs Lowder"], """2 HR, 2 near-HR, 85.4 mph EV. Lowder RHB split -1.37, HR risk -0.18. tough split lane (-1.37); pitcher risk below avg (-0.18).""", blast="high"),
            row("Eugenio Suarez", "R", "+440", 88, "🌕 💣", ["vs Schlittler"], """3 HR, 3 near-HR, 91.6 mph EV. Schlittler RHB split -0.41, HR risk -0.69. tough split lane (-0.41); pitcher suppresses HR (-0.69).""", blast="high"),
            row("Matt McLain", "R", "+710", 85, "⭐", ["vs Schlittler"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 99.0 mph EV. Schlittler RHB split -0.41, HR risk -0.69. tough split lane (-0.41); pitcher suppresses HR (-0.69).""", blast="good"),
            row("Sal Stewart", "R", "+400", 72, "", ["vs Schlittler"], """1 HR, 2 near-HR, 87.8 mph EV. Schlittler RHB split -0.41, HR risk -0.69. tough split lane (-0.41); pitcher suppresses HR (-0.69).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ HOU - Tanner Bibee 🧤 (R, CLE) vs Tatsuya Imai (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +6%, weather -1%). Bibee 🧤 (HR risk 1.23, vs LHB +1.38, vs RHB +0.62). Imai (HR risk 0.29, vs LHB +1.22, vs RHB -0.80).",
        "rows": [
            row("Yordan Alvarez", "L", "+225", 77, "", ["vs Bibee"], """1 HR, 2 near-HR, 93.2 mph EV. Bibee LHB split +1.38, HR risk 1.23.""", blast="good"),
            row("Isaac Paredes", "R", "+470", 81, "🌕 💣", ["vs Bibee"], """2 HR, 3 near-HR, 89.0 mph EV. Bibee RHB split +0.62, HR risk 1.23.""", blast="high"),
            row("Cam Smith", "R", "+630", 78, "🚀", ["vs Bibee"], """0 HR, 1 near-HR, 100.1 mph EV. Bibee RHB split +0.62, HR risk 1.23. limited recent HR events.""", blast="good"),
            row("Rhys Hoskins", "R", "+425", 74, "", ["vs Imai"], """1 HR, 1 near-HR, 91.8 mph EV. Imai RHB split -0.80, HR risk 0.29. tough split lane (-0.80).""", blast="good"),
            row("Kyle Manzardo", "L", "+470", 67, "", ["vs Imai"], """0 HR, 1 near-HR, 91.3 mph EV. Imai LHB split +1.22, HR risk 0.29. limited recent HR events."""),
        ],
    },
    {
        "title": "CWS @ DET - Erick Fedde (R, CWS) vs Tarik Skubal (L, DET)",
        "description": "Tail key data: Park boost data unavailable. Fedde (HR risk 0.31, vs LHB -0.09, vs RHB +0.55). Skubal (HR risk -0.71, vs LHB +0.48, vs RHB -0.71).",
        "rows": [
            row("Colt Keith", "L", "+820", 86, "⭐ 🌕 💣", ["vs Fedde"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 90.0 mph EV. Fedde LHB split -0.09, HR risk 0.31. slight split headwind (-0.09).""", blast="high"),
            row("Spencer Torkelson", "R", "+381", 79, "🌕 💣 💎", ["vs Fedde"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 89.2 mph EV. Fedde RHB split +0.55, HR risk 0.31.""", blast="high"),
            row("Riley Greene", "L", "+410", 71, "", ["vs Fedde"], """0 HR, 2 near-HR, 91.4 mph EV. Fedde LHB split -0.09, HR risk 0.31. slight split headwind (-0.09).""", blast="good"),
            row("Randal Grichuk", "R", "+475", 78, "🌕 💣", ["vs Skubal"], """2 HR, 2 near-HR, 88.2 mph EV. Skubal RHB split -0.71, HR risk -0.71. tough split lane (-0.71); pitcher suppresses HR (-0.71).""", blast="high"),
            row("Colson Montgomery", "L", "+445", 84, "🌕 💣", ["vs Skubal"], """2 HR, 4 near-HR, 90.2 mph EV. Skubal LHB split +0.48, HR risk -0.71. pitcher suppresses HR (-0.71).""", blast="high"),
        ],
    },
    {
        "title": "LAA @ ATH - Jose Soriano (R, LAA) vs Jeffrey Springs 🧤 (L, ATH)",
        "description": "Tail key data: Park boost +36% (stadium +32%, weather +4%). Soriano (HR risk -0.04, vs LHB +0.10, vs RHB -0.13). Springs 🧤 (HR risk 1.46, vs LHB +0.79, vs RHB +1.31).",
        "rows": [
            row("Nick Kurtz", "L", "+300", 90, "🌕 💣", ["vs Soriano"], """3 HR, 4 near-HR, 92.1 mph EV. Soriano LHB split +0.10, HR risk -0.04. pitcher risk below avg (-0.04).""", blast="high"),
            row("Zack Gelof", "R", "+520", 85, "🌕 💣", ["vs Soriano"], """2 HR, 3 near-HR, 92.9 mph EV. Soriano RHB split -0.13, HR risk -0.04. slight split headwind (-0.13); pitcher risk below avg (-0.04).""", blast="high"),
            row("Tyler Soderstrom", "L", "+475", 78, "🌕 💣", ["vs Soriano"], """2 HR, 2 near-HR, 88.0 mph EV. Soriano LHB split +0.10, HR risk -0.04. pitcher risk below avg (-0.04).""", blast="high"),
            row("Zach Neto", "R", "+294", 78, "⭐ 🌕 💣", ["vs Springs"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 86.0 mph EV. Springs RHB split +1.31, HR risk 1.46. lighter EV form (86.0 mph).""", blast="high"),
            row("Jose Siri", "R", "+425", 74, "", ["vs Springs"], """0 HR, 1 near-HR, 96.1 mph EV. Springs RHB split +1.31, HR risk 1.46. limited recent HR events.""", blast="good"),
            row("Max Muncy", "R", "N/A", 64, "", ["vs Soriano"], """0 HR, 1 near-HR, 87.2 mph EV. Soriano RHB split -0.13, HR risk -0.04. slight split headwind (-0.13); pitcher risk below avg (-0.04)."""),
        ],
    },
    {
        "title": "MIL @ ATL - Jacob Misiorowski (R, MIL) vs Martin Perez (L, ATL)",
        "description": "Tail key data: Park boost +3% (stadium -4%, weather +7%). Misiorowski (HR risk -1.30, vs LHB -1.12, vs RHB -0.98). Perez (HR risk -0.29, vs LHB -0.02, vs RHB -0.31).",
        "rows": [
            row("Drake Baldwin", "L", "+478", 73, "", ["vs Misiorowski"], """0 HR, 2 near-HR, 93.4 mph EV. Misiorowski LHB split -1.12, HR risk -1.30. tough split lane (-1.12); pitcher suppresses HR (-1.30).""", blast="good"),
            row("Jackson Chourio", "R", "+437", 84, "⭐ 🌕 💣", ["vs Perez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.1 mph EV. Perez RHB split -0.31, HR risk -0.29. slight split headwind (-0.31); pitcher risk below avg (-0.29).""", blast="high"),
            row("William Contreras", "R", "+587", 80, "", ["vs Perez"], """1 HR, 2 near-HR, 95.5 mph EV. Perez RHB split -0.31, HR risk -0.29. slight split headwind (-0.31); pitcher risk below avg (-0.29).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ ARI - Connor Prielipp (L, MIN) vs Michael Soroka (R, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Prielipp (HR risk -0.44, vs LHB -0.35, vs RHB -0.32). Soroka (HR risk -0.60, vs LHB -0.36, vs RHB -0.65).",
        "rows": [
            row("Ketel Marte", "S", "+380", 88, "🌕 💣", ["vs Prielipp"], """2 HR, 2 near-HR, 98.1 mph EV. Prielipp RHB split -0.32, HR risk -0.44. slight split headwind (-0.32); pitcher suppresses HR (-0.44).""", blast="high"),
            row("Tommy Troy", "R", "N/A", 70, "", ["vs Prielipp"], """1 HR, 1 near-HR, 82.8 mph EV. Prielipp RHB split -0.32, HR risk -0.44. slight split headwind (-0.32); pitcher suppresses HR (-0.44).""", blast="good"),
            row("Royce Lewis", "R", "+570", 74, "", ["vs Soroka"], """1 HR, 1 near-HR, 92.2 mph EV. Soroka RHB split -0.65, HR risk -0.60. tough split lane (-0.65); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Trevor Larnach", "L", "+810", 72, "", ["vs Soroka"], """1 HR, 1 near-HR, 89.5 mph EV. Soroka LHB split -0.36, HR risk -0.60. slight split headwind (-0.36); pitcher suppresses HR (-0.60).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ COL - Bubba Chandler (R, PIT) vs Kyle Freeland 🧤 (L, COL)",
        "description": "Tail key data: Park boost +28% (stadium +20%, weather +8%). Chandler (HR risk -0.60, vs LHB +0.10, vs RHB -0.93). Freeland 🧤 (HR risk 1.16, vs LHB -0.91, vs RHB +1.30).",
        "rows": [
            row("Ezequiel Tovar", "R", "+650", 71, "", ["vs Chandler"], """1 HR, 1 near-HR, 88.6 mph EV. Chandler RHB split -0.93, HR risk -0.60. tough split lane (-0.93); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Kyle Karros", "R", "+900", 70, "", ["vs Chandler"], """1 HR, 1 near-HR, 87.0 mph EV. Chandler RHB split -0.93, HR risk -0.60. tough split lane (-0.93); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Willi Castro", "S", "+550", 64, "", ["vs Chandler"], """0 HR, 90.3 mph EV. Chandler RHB split -0.93, HR risk -0.60. tough split lane (-0.93); pitcher suppresses HR (-0.60)."""),
            row("Hunter Goodman", "R", "+270", 70, "", ["vs Chandler"], """1 HR, 1 near-HR, 87.7 mph EV. Chandler RHB split -0.93, HR risk -0.60. tough split lane (-0.93); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Bryan Reynolds", "S", "+380", 72, "", ["vs Freeland"], """1 HR, 1 near-HR, 89.5 mph EV. Freeland RHB split +1.30, HR risk 1.16.""", blast="good"),
            row("Spencer Horwitz", "L", "+670", 72, "", ["vs Freeland"], """1 HR, 1 near-HR, 89.7 mph EV. Freeland LHB split -0.91, HR risk 1.16. tough split lane (-0.91).""", blast="good"),
        ],
    },
    {
        "title": "SD @ TEX - Randy Vasquez 🧤 (R, SD) vs Jacob deGrom (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -10%, weather -1%). Vasquez 🧤 (HR risk 1.40, vs LHB +0.42, vs RHB +1.78). deGrom (HR risk 0.23, vs LHB +0.35, vs RHB +0.06).",
        "rows": [
            row("Joc Pederson", "L", "+403", 76, "", ["vs Vasquez"], """1 HR, 2 near-HR, 92.4 mph EV. Vasquez LHB split +0.42, HR risk 1.40. park/weather net drag (-11%).""", blast="good"),
            row("Elias Diaz", "R", "+880", 63, "", ["vs Vasquez"], """0 HR, 89.2 mph EV. Vasquez RHB split +1.78, HR risk 1.40. park/weather net drag (-11%); limited recent HR events."""),
            row("Fernando Tatis Jr.", "R", "+470", 83, "", ["vs deGrom"], """1 HR, 2 near-HR, 98.6 mph EV. deGrom RHB split +0.06, HR risk 0.23. park/weather net drag (-11%).""", blast="good"),
            row("Jackson Merrill", "L", "+475", 79, "", ["vs deGrom"], """1 HR, 2 near-HR, 94.6 mph EV. deGrom LHB split +0.35, HR risk 0.23. park/weather net drag (-11%).""", blast="good"),
        ],
    },
    {
        "title": "SF @ MIA - Landen Roupp (R, SF) vs Lake Bachar (L, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -12%, weather +0%). Roupp (HR risk -0.84, vs LHB -0.75, vs RHB -0.65). Home starter risk unavailable.",
        "rows": [
            row("Heriberto Hernandez", "R", "+900", 94, "⭐ 🌕 💣", ["vs Roupp"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 96.0 mph EV. Roupp RHB split -0.65, HR risk -0.84. tough split lane (-0.65); pitcher suppresses HR (-0.84).""", blast="high"),
            row("Joe Mack", "L", "+1200", 76, "💎", ["vs Roupp"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.7 mph EV. Roupp LHB split -0.75, HR risk -0.84. tough split lane (-0.75); pitcher suppresses HR (-0.84).""", blast="good"),
            row("Kyle Stowers", "L", "+630", 66, "", ["vs Roupp"], """0 HR, 1 near-HR, 90.5 mph EV. Roupp LHB split -0.75, HR risk -0.84. tough split lane (-0.75); pitcher suppresses HR (-0.84)."""),
            row("Willy Adames", "R", "+520", 91, "🌕 💣", ["vs Bachar"], """3 HR, 3 near-HR, 94.9 mph EV. Bachar split/risk data unavailable. limited split/risk sample; park/weather net drag (-13%).""", blast="high"),
            row("Bryce Eldridge", "L", "+575", 96, "🌕 💣", ["vs Bachar"], """3 HR, 4 near-HR, 97.5 mph EV. Bachar split/risk data unavailable. limited split/risk sample; park/weather net drag (-13%).""", blast="high"),
        ],
    },
    {
        "title": "STL @ KC - Michael McGreevy (R, STL) vs Seth Lugo (R, KC)",
        "description": "Tail key data: Park boost +8% (stadium +12%, weather -5%). McGreevy (HR risk 0.27, vs LHB +0.37, vs RHB +0.14). Lugo (HR risk 0.89, vs LHB +0.34, vs RHB +0.99).",
        "rows": [
            row("Jac Caglianone", "L", "+425", 85, "🌕 💣", ["vs McGreevy"], """2 HR, 2 near-HR, 94.7 mph EV. McGreevy LHB split +0.37, HR risk 0.27. weather carry headwind (-5%).""", blast="high"),
            row("Lane Thomas", "R", "+800", 87, "🌕 💣", ["vs McGreevy"], """3 HR, 4 near-HR, 89.1 mph EV. McGreevy RHB split +0.14, HR risk 0.27. weather carry headwind (-5%).""", blast="high"),
            row("Michael Massey", "L", "+590", 72, "", ["vs McGreevy"], """0 HR, 1 near-HR, 94.4 mph EV. McGreevy LHB split +0.37, HR risk 0.27. weather carry headwind (-5%); limited recent HR events.""", blast="good"),
            row("Alec Burleson", "L", "+390", 98, "🌕 💣", ["vs Lugo"], """5 HR, 6 near-HR, 92.8 mph EV. Lugo LHB split +0.34, HR risk 0.89. weather carry headwind (-5%).""", blast="high"),
            row("Lars Nootbaar", "L", "+575", 77, "", ["vs Lugo"], """1 HR, 1 near-HR, 95.4 mph EV. Lugo LHB split +0.34, HR risk 0.89. weather carry headwind (-5%).""", blast="good"),
            row("Blaze Jordan", "R", "+770", 78, "", ["vs Lugo"], """1 HR, 1 near-HR, 95.7 mph EV. Lugo RHB split +0.99, HR risk 0.89. weather carry headwind (-5%).""", blast="good"),
            row("Jordan Walker", "R", "+360", 74, "", ["vs Lugo"], """1 HR, 1 near-HR, 92.2 mph EV. Lugo RHB split +0.99, HR risk 0.89. weather carry headwind (-5%).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ TB - PJ Poulin (L, WSH) vs Griffin Jax (R, TB)",
        "description": "Tail key data: Park boost data unavailable. Away starter risk unavailable. Jax (HR risk 0.71, vs LHB +0.39, vs RHB +0.78).",
        "rows": [
            row("Junior Caminero", "R", "+300", 76, "", ["vs Poulin"], """0 HR, 99.6 mph EV. Poulin split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Yandy Diaz", "R", "+470", 70, "", ["vs Poulin"], """1 HR, 1 near-HR, 87.7 mph EV. Poulin split/risk data unavailable. limited split/risk sample; lighter EV form (87.7 mph).""", blast="good"),
            row("James Wood", "L", "+320", 77, "", ["vs Jax"], """1 HR, 2 near-HR, 93.1 mph EV. Jax LHB split +0.39, HR risk 0.71.""", blast="good"),
            row("CJ Abrams", "L", "+520", 75, "", ["vs Jax"], """1 HR, 2 near-HR, 91.4 mph EV. Jax LHB split +0.39, HR risk 0.71.""", blast="good"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-19")

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

    out = ROOT / '_games-0619.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
