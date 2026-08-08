#!/usr/bin/env python3
"""Generate games[] block for 2026-08-08 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Brandon Lowe (L)",
    "Cal Raleigh (S)",
    "Colson Montgomery (L)",
    "Jimmy Crooks (L)",
    "Julio Rodriguez (R)",
    "Junior Caminero (R)",
    "Munetaka Murakami (L)",
    "Pete Alonso (R)",
    "Pete Crow-Armstrong (L)",
    "Wyatt Langford (R)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Abimelec Ortiz (L)",
    "Alec Burleson (L)",
    "Brice Turang (L)",
    "Christian Encarnacion-Strand (R)",
    "Dillon Dingler (R)",
    "Elly De La Cruz (S)",
    "Endy Rodriguez (S)",
    "Francisco Lindor (S)",
    "Gleyber Torres (R)",
    "Hao-Yu Lee (R)",
    "Jackson Chourio (R)",
    "Jesus Sanchez (L)",
    "Mike Trout (R)",
    "Mike Yastrzemski (L)",
    "Noelvi Marte (R)",
    "Randal Grichuk (R)",
    "Ronald Acuna Jr. (R)",
    "Taylor Trammell (L)",
    "Tim Tawa (R)",
}

PLAYER_TEAMS = {
    "Abimelec Ortiz (L)": "WSH",
    "Alec Burleson (L)": "STL",
    "Alex Jackson (R)": "MIN",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Vaughn (R)": "MIL",
    "Andruw Monasterio (R)": "BOS",
    "Brandon Lowe (L)": "PIT",
    "Brett Baty (L)": "NYM",
    "Brian Serven (R)": "ATH",
    "Brice Turang (L)": "MIL",
    "Bryce Eldridge (L)": "SF",
    "Bryson Stott (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Derek Hill (R)": "PHI",
    "Dillon Dingler (R)": "DET",
    "Dominic Smith (L)": "ATL",
    "Dylan Crews (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Endy Rodriguez (S)": "PIT",
    "Ezequiel Tovar (R)": "COL",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Gage Workman (L)": "SD",
    "Garrett Mitchell (L)": "MIL",
    "George Springer (R)": "TOR",
    "Gleyber Torres (R)": "DET",
    "Gunnar Henderson (L)": "BAL",
    "Hao-Yu Lee (R)": "DET",
    "Heliot Ramos (R)": "NYY",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jesus Sanchez (L)": "TOR",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "CLE",
    "John Rave (L)": "KC",
    "Jonah Heim (S)": "ATH",
    "Jordan Walker (R)": "STL",
    "Josh Bell (S)": "MIN",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Lars Nootbaar (L)": "ARI",
    "Leody Taveras (S)": "BAL",
    "Manny Machado (R)": "SD",
    "Marcus Semien (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Miguel Amaya (R)": "CHC",
    "Mike Trout (R)": "LAA",
    "Mike Yastrzemski (L)": "ATL",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "STL",
    "Noelvi Marte (R)": "CIN",
    "Osleivis Basabe (R)": "SF",
    "Owen Caissie (L)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Randy Arozarena (R)": "SEA",
    "Rhys Hoskins (R)": "CLE",
    "Ronald Acuna Jr. (R)": "ATL",
    "Ryan Kreidler (R)": "MIN",
    "Sal Stewart (R)": "CIN",
    "Spencer Jones (L)": "NYY",
    "Starling Marte (R)": "KC",
    "Taylor Trammell (L)": "HOU",
    "Tim Tawa (R)": "ARI",
    "Tyler Soderstrom (L)": "ATH",
    "Tyrone Taylor (R)": "CHC",
    "Victor Mesa Jr. (L)": "TB",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("NYM @ PIT", "Stock"),
    ("TOR @ PHI", "Nola"),
    ("TOR @ PHI", "Scherzer"),
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
        "title": "ATH @ BOS - Gage Jump (L, ATH) vs Jake Bennett (L, BOS)",
        "description": "Tail key data: Park boost +7% (stadium -7%, weather +13%). Jump (HR risk 0.04, vs LHB +0.01, vs RHB +0.16). Bennett (HR risk -0.82, vs LHB -1.59, vs RHB -0.21).",
        "rows": [
            row("Willson Contreras", "R", "+264", 74, "🌕 💣", ["vs Jump"], """2 HR, 2 near-HR, 92.4 mph EV. Jump RHB split +0.16, HR risk 0.04. park suppresses carry (-7%).""", blast="high"),
            row("Andruw Monasterio", "R", "+560", 65, "", ["vs Jump"], """1 HR, 1 near-HR, 92.7 mph EV. Jump RHB split +0.16, HR risk 0.04. park suppresses carry (-7%).""", blast="good"),
            row("Jonah Heim", "S", "+600", 65, "🌕 💣", ["vs Bennett"], """2 HR, 2 near-HR, 94.1 mph EV. Bennett SHB→RHB split -0.21, HR risk -0.82. slight split headwind (-0.21); pitcher suppresses HR (-0.82).""", blast="high"),
            row("Tyler Soderstrom", "L", "+750", 58, "", ["vs Bennett"], """1 HR, 1 near-HR, 97.1 mph EV. Bennett LHB split -1.59, HR risk -0.82. tough split lane (-1.59); pitcher suppresses HR (-0.82).""", blast="good"),
            row("Brian Serven", "R", "N/A", 67, "🌕 💣", ["vs Bennett"], """2 HR, 2 near-HR, 96.6 mph EV. Bennett RHB split -0.21, HR risk -0.82. slight split headwind (-0.21); pitcher suppresses HR (-0.82).""", blast="high"),
        ],
    },
    {
        "title": "ATL @ NYY - Chris Sale (L, ATL) vs Gerrit Cole (R, NYY)",
        "description": "Tail key data: Park boost +23% (stadium +5%, weather +18%). Sale (HR risk -0.62, vs LHB -1.03, vs RHB -0.17). Cole (HR risk 0.48, vs LHB +0.43, vs RHB +0.22).",
        "rows": [
            row("Spencer Jones", "L", "+750", 66, "🌕 💣", ["vs Sale"], """2 HR, 2 near-HR, 92.8 mph EV. Sale LHB split -1.03, HR risk -0.62. tough split lane (-1.03); pitcher suppresses HR (-0.62).""", blast="high"),
            row("Heliot Ramos", "R", "+459", 60, "", ["vs Sale"], """1 HR, 1 near-HR, 92.9 mph EV. Sale RHB split -0.17, HR risk -0.62. slight split headwind (-0.17); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+371", 75, "💎", ["vs Cole"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 97.1 mph EV. Cole RHB split +0.22, HR risk 0.48. limited recent HR events.""", blast="good"),
            row("Matt Olson", "L", "+297", 87, "", ["vs Cole"], """1 HR, 3 near-HR, 95.7 mph EV. Cole LHB split +0.43, HR risk 0.48.""", blast="good"),
            row("Mike Yastrzemski", "L", "+480", 81, "💎", ["vs Cole"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 94.6 mph EV. Cole LHB split +0.43, HR risk 0.48.""", blast="good"),
            row("Dominic Smith", "L", "N/A", 91, "🌕 💣", ["vs Cole"], """2 HR, 3 near-HR, 94.2 mph EV. Cole LHB split +0.43, HR risk 0.48.""", blast="high"),
        ],
    },
    {
        "title": "BAL @ TEX - Kyle Bradish (R, BAL) vs Jacob deGrom (R, TEX)",
        "description": "Tail key data: Park boost -10% (stadium -10%, weather -1%). Bradish (HR risk -0.43, vs LHB -0.70, vs RHB +0.34). deGrom (HR risk -0.00, vs LHB +0.30, vs RHB -0.48).",
        "rows": [
            row("Wyatt Langford", "R", "+450", 61, "🚀 ⭐", ["vs Bradish"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 100.6 mph EV. Bradish RHB split +0.34, HR risk -0.43. pitcher suppresses HR (-0.43); park/weather net drag (-10%).""", blast="good"),
            row("Leody Taveras", "S", "+1080", 74, "🌕 💣", ["vs deGrom"], """2 HR, 2 near-HR, 99.7 mph EV. deGrom SHB→LHB split +0.30, HR risk -0.00. park/weather net drag (-10%).""", blast="high"),
            row("Pete Alonso", "R", "+395", 58, "⭐", ["vs deGrom"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.3 mph EV. deGrom RHB split -0.48, HR risk -0.00. tough split lane (-0.48); park/weather net drag (-10%).""", blast="good"),
            row("Christian Encarnacion-Strand", "R", "+498", 58, "💎", ["vs deGrom"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.1 mph EV. deGrom RHB split -0.48, HR risk -0.00. tough split lane (-0.48); park/weather net drag (-10%).""", blast="good"),
            row("Gunnar Henderson", "L", "+484", 58, "", ["vs deGrom"], """0 HR, 1 near-HR, 91.2 mph EV. deGrom LHB split +0.30, HR risk -0.00. park/weather net drag (-10%); limited recent HR events."""),
        ],
    },
    {
        "title": "CHC @ KC - Clay Holmes (R, CHC) vs Seth Lugo (R, KC)",
        "description": "Tail key data: Park boost +21% (stadium +11%, weather +11%). Holmes (HR risk -0.82, vs LHB -0.57, vs RHB -0.57). Lugo (HR risk -0.16, vs LHB -0.06, vs RHB -0.04).",
        "rows": [
            row("John Rave", "L", "+800", 58, "", ["vs Holmes"], """1 HR, 3 near-HR, 83.7 mph EV. Holmes LHB split -0.57, HR risk -0.82. tough split lane (-0.57); pitcher suppresses HR (-0.82).""", blast="good"),
            row("Starling Marte", "R", "N/A", 58, "", ["vs Holmes"], """1 HR, 1 near-HR, 92.6 mph EV. Holmes RHB split -0.57, HR risk -0.82. tough split lane (-0.57); pitcher suppresses HR (-0.82).""", blast="good"),
            row("Jac Caglianone", "L", "+460", 58, "", ["vs Holmes"], """0 HR, 96.7 mph EV. Holmes LHB split -0.57, HR risk -0.82. tough split lane (-0.57); pitcher suppresses HR (-0.82).""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+361", 66, "⭐", ["vs Lugo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.6 mph EV. Lugo LHB split -0.06, HR risk -0.16. slight split headwind (-0.06); pitcher risk below avg (-0.16).""", blast="good"),
            row("Miguel Amaya", "R", "+800", 58, "", ["vs Lugo"], """0 HR, 1 near-HR, 91.9 mph EV. Lugo RHB split -0.04, HR risk -0.16. slight split headwind (-0.04); pitcher risk below avg (-0.16)."""),
            row("Tyrone Taylor", "R", "N/A", 70, "🌕 💣", ["vs Lugo"], """2 HR, 2 near-HR, 88.6 mph EV. Lugo RHB split -0.04, HR risk -0.16. slight split headwind (-0.04); pitcher risk below avg (-0.16).""", blast="high"),
        ],
    },
    {
        "title": "CIN @ WSH - Chase Burns (R, CIN) vs Andrew Alvarez (L, WSH)",
        "description": "Tail key data: Park boost data unavailable. Burns (HR risk -0.04, vs LHB +0.40, vs RHB -0.89). Alvarez (HR risk -1.43, vs LHB -0.76, vs RHB -1.34).",
        "rows": [
            row("Abimelec Ortiz", "L", "+552", 62, "💎", ["vs Burns"], """Worst Pickz Hidden Gem. 0 HR, 97.1 mph EV. Burns LHB split +0.40, HR risk -0.04. pitcher risk below avg (-0.04); limited recent HR events.""", blast="good"),
            row("Dylan Crews", "R", "+482", 58, "", ["vs Burns"], """1 HR, 1 near-HR, 89.8 mph EV. Burns RHB split -0.89, HR risk -0.04. tough split lane (-0.89); pitcher risk below avg (-0.04).""", blast="good"),
            row("Elly De La Cruz", "S", "+390", 58, "🌕 💣 💎", ["vs Alvarez"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 97.3 mph EV. Alvarez SHB→LHB split -0.76, HR risk -1.43. tough split lane (-0.76); pitcher suppresses HR (-1.43).""", blast="high"),
            row("Sal Stewart", "R", "+390", 58, "", ["vs Alvarez"], """1 HR, 1 near-HR, 96.5 mph EV. Alvarez RHB split -1.34, HR risk -1.43. tough split lane (-1.34); pitcher suppresses HR (-1.43).""", blast="good"),
            row("Noelvi Marte", "R", "+760", 58, "💎", ["vs Alvarez"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.0 mph EV. Alvarez RHB split -1.34, HR risk -1.43. tough split lane (-1.34); pitcher suppresses HR (-1.43).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ CWS - Gavin Williams (R, CLE) vs Anthony Kay (L, CWS)",
        "description": "Tail key data: Park boost data unavailable. Williams (HR risk 0.94, vs LHB +0.59, vs RHB +1.12). Kay (HR risk -0.09, vs LHB -1.05, vs RHB +0.60).",
        "rows": [
            row("Randal Grichuk", "R", "N/A", 86, "💎", ["vs Williams"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 97.1 mph EV. Williams RHB split +1.12, HR risk 0.94.""", blast="good"),
            row("Munetaka Murakami", "L", "+303", 81, "⭐", ["vs Williams"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.3 mph EV. Williams LHB split +0.59, HR risk 0.94.""", blast="good"),
            row("Colson Montgomery", "L", "+370", 77, "⭐", ["vs Williams"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.5 mph EV. Williams LHB split +0.59, HR risk 0.94.""", blast="good"),
            row("Andrew Benintendi", "L", "+620", 91, "🌕 💣", ["vs Williams"], """2 HR, 3 near-HR, 95.0 mph EV. Williams LHB split +0.59, HR risk 0.94.""", blast="high"),
            row("Jo Adell", "R", "+620", 71, "", ["vs Kay"], """1 HR, 3 near-HR, 92.8 mph EV. Kay RHB split +0.60, HR risk -0.09. pitcher risk below avg (-0.09).""", blast="good"),
            row("Rhys Hoskins", "R", "+525", 64, "", ["vs Kay"], """1 HR, 2 near-HR, 89.6 mph EV. Kay RHB split +0.60, HR risk -0.09. pitcher risk below avg (-0.09).""", blast="good"),
        ],
    },
    {
        "title": "COL @ STL - Kyle Freeland (L, COL) vs Matthew Liberatore (L, STL)",
        "description": "Tail key data: Park boost -11% (stadium -9%, weather -2%). Freeland (HR risk 0.87, vs LHB -0.28, vs RHB +1.46). Liberatore (HR risk -0.11, vs LHB +0.11, vs RHB +0.06).",
        "rows": [
            row("Jordan Walker", "R", "+300", 78, "", ["vs Freeland"], """0 HR, 2 near-HR, 92.6 mph EV. Freeland RHB split +1.46, HR risk 0.87. park/weather net drag (-11%).""", blast="good"),
            row("Alec Burleson", "L", "+483", 72, "💎", ["vs Freeland"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 96.7 mph EV. Freeland LHB split -0.28, HR risk 0.87. slight split headwind (-0.28); park/weather net drag (-11%).""", blast="good"),
            row("Jimmy Crooks", "L", "N/A", 72, "⭐", ["vs Freeland"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.8 mph EV. Freeland LHB split -0.28, HR risk 0.87. slight split headwind (-0.28); park/weather net drag (-11%).""", blast="good"),
            row("Nelson Velazquez", "R", "+375", 83, "", ["vs Freeland"], """1 HR, 2 near-HR, 93.0 mph EV. Freeland RHB split +1.46, HR risk 0.87. park/weather net drag (-11%).""", blast="good"),
            row("Willi Castro", "S", "+650", 58, "", ["vs Liberatore"], """1 HR, 2 near-HR, 82.9 mph EV. Liberatore SHB→LHB split +0.11, HR risk -0.11. pitcher risk below avg (-0.11); park/weather net drag (-11%).""", blast="good"),
            row("Ezequiel Tovar", "R", "+780", 58, "", ["vs Liberatore"], """1 HR, 1 near-HR, 87.7 mph EV. Liberatore RHB split +0.06, HR risk -0.11. pitcher risk below avg (-0.11); park/weather net drag (-11%).""", blast="good"),
        ],
    },
    {
        "title": "DET @ SF - Jackson Jobe (R, DET) vs Landen Roupp (R, SF)",
        "description": "Tail key data: Park boost -24% (stadium -17%, weather -6%). Jobe (HR risk 0.35, vs LHB +0.60, vs RHB -0.05). Roupp (HR risk -0.75, vs LHB -0.62, vs RHB -0.15).",
        "rows": [
            row("Bryce Eldridge", "L", "+578", 58, "", ["vs Jobe"], """1 HR, 1 near-HR, 86.7 mph EV. Jobe LHB split +0.60, HR risk 0.35. park/weather net drag (-24%); lighter EV form (86.7 mph).""", blast="good"),
            row("Rafael Devers", "L", "+450", 61, "", ["vs Jobe"], """0 HR, 94.6 mph EV. Jobe LHB split +0.60, HR risk 0.35. park/weather net drag (-24%); limited recent HR events.""", blast="good"),
            row("Osleivis Basabe", "R", "N/A", 66, "🌕 💣", ["vs Jobe"], """2 HR, 2 near-HR, 90.2 mph EV. Jobe RHB split -0.05, HR risk 0.35. slight split headwind (-0.05); park/weather net drag (-24%).""", blast="high"),
            row("Gleyber Torres", "R", "+1080", 61, "🌕 💣 💎", ["vs Roupp"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 91.7 mph EV. Roupp RHB split -0.15, HR risk -0.75. slight split headwind (-0.15); pitcher suppresses HR (-0.75).""", blast="high"),
            row("Dillon Dingler", "R", "+830", 60, "🌕 💣 💎", ["vs Roupp"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 87.3 mph EV. Roupp RHB split -0.15, HR risk -0.75. slight split headwind (-0.15); pitcher suppresses HR (-0.75).""", blast="high"),
            row("Hao-Yu Lee", "R", "N/A", 58, "💎", ["vs Roupp"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 96.7 mph EV. Roupp RHB split -0.15, HR risk -0.75. slight split headwind (-0.15); pitcher suppresses HR (-0.75).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ SD - Peter Lambert (R, HOU) vs Michael King (R, SD)",
        "description": "Tail key data: Park boost +3% (stadium -4%, weather +7%). Lambert (HR risk -0.57, vs LHB -0.67, vs RHB -0.02). King (HR risk 0.09, vs LHB -0.08, vs RHB +0.63).",
        "rows": [
            row("Manny Machado", "R", "+400", 58, "", ["vs Lambert"], """0 HR, 2 near-HR, 93.5 mph EV. Lambert RHB split -0.02, HR risk -0.57. slight split headwind (-0.02); pitcher suppresses HR (-0.57).""", blast="good"),
            row("Jackson Merrill", "L", "+660", 58, "", ["vs Lambert"], """1 HR, 1 near-HR, 90.9 mph EV. Lambert LHB split -0.67, HR risk -0.57. tough split lane (-0.67); pitcher suppresses HR (-0.57).""", blast="good"),
            row("Gage Workman", "L", "N/A", 58, "", ["vs Lambert"], """0 HR, 1 near-HR, 94.7 mph EV. Lambert LHB split -0.67, HR risk -0.57. tough split lane (-0.67); pitcher suppresses HR (-0.57).""", blast="good"),
            row("Yordan Alvarez", "L", "+270", 59, "⭐", ["vs King"], """Worst Pickz Favorite. 0 HR, 94.6 mph EV. King LHB split -0.08, HR risk 0.09. slight split headwind (-0.08); limited recent HR events.""", blast="good"),
            row("Taylor Trammell", "L", "+620", 64, "💎", ["vs King"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 92.9 mph EV. King LHB split -0.08, HR risk 0.09. slight split headwind (-0.08).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ MIA - Walbert Urena (R, LAA) vs Sandy Alcantara (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -13%, weather +0%). Urena (HR risk -1.36, vs LHB -0.66, vs RHB -1.49). Alcantara (HR risk 0.01, vs LHB -0.04, vs RHB +0.35).",
        "rows": [
            row("Owen Caissie", "L", "+800", 58, "🌕 💣", ["vs Urena"], """2 HR, 3 near-HR, 94.0 mph EV. Urena LHB split -0.66, HR risk -1.36. tough split lane (-0.66); pitcher suppresses HR (-1.36).""", blast="high"),
            row("Zach Neto", "R", "+650", 61, "", ["vs Alcantara"], """1 HR, 1 near-HR, 92.9 mph EV. Alcantara RHB split +0.35, HR risk 0.01. park/weather net drag (-13%).""", blast="good"),
            row("Mike Trout", "R", "+481", 59, "💎", ["vs Alcantara"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.5 mph EV. Alcantara RHB split +0.35, HR risk 0.01. park/weather net drag (-13%).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ ARI - Yoshinobu Yamamoto (R, LAD) vs Brandon Pfaadt (R, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Yamamoto (HR risk -0.39, vs LHB -0.56, vs RHB +0.33). Pfaadt (HR risk -0.69, vs LHB -0.36, vs RHB -0.65).",
        "rows": [
            row("Tim Tawa", "R", "+970", 71, "🌕 💣 💎", ["vs Yamamoto"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.0 mph EV. Yamamoto RHB split +0.33, HR risk -0.39. pitcher risk below avg (-0.39); park/weather net drag (-8%).""", blast="high"),
            row("Lars Nootbaar", "L", "+900", 58, "", ["vs Yamamoto"], """0 HR, 1 near-HR, 85.6 mph EV. Yamamoto LHB split -0.56, HR risk -0.39. tough split lane (-0.56); pitcher risk below avg (-0.39)."""),
            row("Max Muncy", "L", "+373", 58, "", ["vs Pfaadt"], """0 HR, 90.6 mph EV. Pfaadt LHB split -0.36, HR risk -0.69. slight split headwind (-0.36); pitcher suppresses HR (-0.69)."""),
            row("Mookie Betts", "R", "+600", 58, "", ["vs Pfaadt"], """0 HR, 93.5 mph EV. Pfaadt RHB split -0.65, HR risk -0.69. tough split lane (-0.65); pitcher suppresses HR (-0.69).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ MIL - Taj Bradley (R, MIN) vs Robert Gasser (L, MIL)",
        "description": "Tail key data: Park boost +20% (stadium +9%, weather +10%). Bradley (HR risk 0.37, vs LHB +0.86, vs RHB -0.54). Gasser (HR risk 0.64, vs LHB -0.23, vs RHB +0.96).",
        "rows": [
            row("Jackson Chourio", "R", "+420", 86, "🌕 💣 💎", ["vs Bradley"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 95.7 mph EV. Bradley RHB split -0.54, HR risk 0.37. tough split lane (-0.54).""", blast="high"),
            row("Andrew Vaughn", "R", "N/A", 83, "🌕 💣", ["vs Bradley"], """2 HR, 3 near-HR, 96.2 mph EV. Bradley RHB split -0.54, HR risk 0.37. tough split lane (-0.54).""", blast="high"),
            row("Brice Turang", "L", "+600", 80, "💎", ["vs Bradley"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.0 mph EV. Bradley LHB split +0.86, HR risk 0.37.""", blast="good"),
            row("Jake Bauers", "L", "+370", 74, "", ["vs Bradley"], """0 HR, 1 near-HR, 94.6 mph EV. Bradley LHB split +0.86, HR risk 0.37. limited recent HR events.""", blast="good"),
            row("Garrett Mitchell", "L", "+600", 74, "", ["vs Bradley"], """0 HR, 99.7 mph EV. Bradley LHB split +0.86, HR risk 0.37. limited recent HR events.""", blast="good"),
            row("Josh Bell", "S", "+500", 79, "", ["vs Gasser"], """1 HR, 1 near-HR, 89.0 mph EV. Gasser SHB→RHB split +0.96, HR risk 0.64.""", blast="good"),
            row("Ryan Kreidler", "R", "+513", 80, "", ["vs Gasser"], """0 HR, 99.3 mph EV. Gasser RHB split +0.96, HR risk 0.64. limited recent HR events.""", blast="good"),
            row("Alex Jackson", "R", "N/A", 80, "", ["vs Gasser"], """0 HR, 95.4 mph EV. Gasser RHB split +0.96, HR risk 0.64. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "NYM @ PIT - Robert Stock 🧤 (R, NYM) vs Bubba Chandler (R, PIT)",
        "description": "Tail key data: Park boost -1% (stadium -15%, weather +14%). Stock 🧤 (HR risk 1.59, vs LHB +2.16, vs RHB +0.00). Chandler (HR risk -0.90, vs LHB -0.13, vs RHB -1.48).",
        "rows": [
            row("Brandon Lowe", "L", "+317", 93, "⭐ 🌕 💣", ["vs Stock"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.6 mph EV. Stock LHB split +2.16, HR risk 1.59. park suppresses carry (-15%).""", blast="good"),
            row("Endy Rodriguez", "S", "+563", 93, "🌕 💣 💎", ["vs Stock"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.5 mph EV. Stock SHB→LHB split +2.16, HR risk 1.59. park suppresses carry (-15%).""", blast="good"),
            row("Brett Baty", "L", "+600", 65, "🌕 💣", ["vs Chandler"], """2 HR, 2 near-HR, 96.6 mph EV. Chandler LHB split -0.13, HR risk -0.90. slight split headwind (-0.13); pitcher suppresses HR (-0.90).""", blast="high"),
            row("Francisco Alvarez", "R", "+505", 58, "🌕 💣", ["vs Chandler"], """2 HR, 2 near-HR, 92.3 mph EV. Chandler RHB split -1.48, HR risk -0.90. tough split lane (-1.48); pitcher suppresses HR (-0.90).""", blast="high"),
            row("Marcus Semien", "R", "+850", 58, "", ["vs Chandler"], """1 HR, 90.4 mph EV. Chandler RHB split -1.48, HR risk -0.90. tough split lane (-1.48); pitcher suppresses HR (-0.90).""", blast="good"),
            row("Francisco Lindor", "S", "+413", 58, "💎", ["vs Chandler"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 92.8 mph EV. Chandler SHB→LHB split -0.13, HR risk -0.90. slight split headwind (-0.13); pitcher suppresses HR (-0.90).""", blast="good"),
        ],
    },
    {
        "title": "TB @ SEA - Griffin Jax (R, TB) vs George Kirby (R, SEA)",
        "description": "Tail key data: Park boost -4% (stadium +1%, weather -5%). Jax (HR risk -0.06, vs LHB +0.32, vs RHB -0.44). Kirby (HR risk 0.58, vs LHB +0.47, vs RHB +0.64).",
        "rows": [
            row("Cal Raleigh", "S", "+368", 68, "⭐", ["vs Jax"], """Worst Pickz Favorite. 0 HR, 3 near-HR, 98.8 mph EV. Jax SHB→LHB split +0.32, HR risk -0.06. pitcher risk below avg (-0.06); weather carry headwind (-5%).""", blast="good"),
            row("Julio Rodriguez", "R", "+538", 66, "⭐ 🌕 💣", ["vs Jax"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.8 mph EV. Jax RHB split -0.44, HR risk -0.06. tough split lane (-0.44); pitcher risk below avg (-0.06).""", blast="high"),
            row("Randy Arozarena", "R", "+570", 58, "", ["vs Jax"], """0 HR, 1 near-HR, 94.1 mph EV. Jax RHB split -0.44, HR risk -0.06. tough split lane (-0.44); pitcher risk below avg (-0.06).""", blast="good"),
            row("Junior Caminero", "R", "+320", 90, "⭐ 🌕 💣", ["vs Kirby"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.9 mph EV. Kirby RHB split +0.64, HR risk 0.58. weather carry headwind (-5%).""", blast="high"),
            row("Victor Mesa Jr.", "L", "+600", 69, "", ["vs Kirby"], """0 HR, 3 near-HR, 87.9 mph EV. Kirby LHB split +0.47, HR risk 0.58. weather carry headwind (-5%); lighter EV form (87.9 mph).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ PHI - Max Scherzer 🧤 (R, TOR) vs Aaron Nola 🧤 (R, PHI)",
        "description": "Tail key data: Park boost +39% (stadium +16%, weather +23%). Scherzer 🧤 (HR risk 1.49, vs LHB +1.54, vs RHB +1.05). Nola 🧤 (HR risk 1.79, vs LHB +1.62, vs RHB +0.90).",
        "rows": [
            row("Derek Hill", "R", "N/A", 98, "🌕 💣", ["vs Scherzer"], """2 HR, 2 near-HR, 94.6 mph EV. Scherzer RHB split +1.05, HR risk 1.49.""", blast="high"),
            row("Bryson Stott", "L", "+460", 94, "🌕 💣", ["vs Scherzer"], """0 HR, 97.2 mph EV. Scherzer LHB split +1.54, HR risk 1.49. limited recent HR events.""", blast="good"),
            row("Jesus Sanchez", "L", "+430", 94, "🌕 💣 💎", ["vs Nola"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 89.9 mph EV. Nola LHB split +1.62, HR risk 1.79.""", blast="good"),
            row("George Springer", "R", "+479", 93, "🌕 💣", ["vs Nola"], """1 HR, 1 near-HR, 94.7 mph EV. Nola RHB split +0.90, HR risk 1.79.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-08")

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

    out = ROOT / '_games-0808.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
