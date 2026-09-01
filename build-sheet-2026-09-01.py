#!/usr/bin/env python3
"""Generate games[] block for 2026-09-01 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Adley Rutschman (S)",
    "Alec Burleson (L)",
    "Alejandro Kirk (R)",
    "Blaze Alexander (R)",
    "Cal Raleigh (S)",
    "Carter Jensen (L)",
    "Corbin Carroll (L)",
    "Daylen Lile (L)",
    "Dylan Beavers (L)",
    "Jac Caglianone (L)",
    "Jake Burger (R)",
    "Jordan Walker (R)",
    "Junior Caminero (R)",
    "Kyle Stowers (L)",
    "Munetaka Murakami (L)",
    "Nathaniel Lowe (L)",
    "Oneil Cruz (L)",
    "Rafael Devers (L)",
    "Sal Stewart (R)",
    "Seiya Suzuki (R)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Andrew Benintendi (L)",
    "Ben Malgeri (R)",
    "Brady House (R)",
    "Bryan Reynolds (S)",
    "Christian Moore (R)",
    "Dominic Canzone (L)",
    "Edmundo Sosa (R)",
    "Elly De La Cruz (S)",
    "Gabriel Moreno (R)",
    "George Lombard Jr. (R)",
    "Hunter Feduccia (L)",
    "Jarren Duran (L)",
    "Jesus Sanchez (L)",
    "Jose Tena (L)",
    "Justin Foscue (R)",
    "Kenny Piper (R)",
    "Ketel Marte (S)",
    "Kody Clemens (L)",
    "Kyle Schwarber (L)",
    "LaMonte Wade Jr. (L)",
    "Mark Vientos (R)",
    "Michael Busch (L)",
    "Mike Yastrzemski (L)",
    "Nelson Velazquez (R)",
    "Nolan Gorman (L)",
    "Pete Crow Armstrong (L)",
    "Roman Anthony (L)",
    "Ryan Vilade (R)",
    "Spencer Jones (L)",
    "Teoscar Hernandez (R)",
    "Vinnie Pasquantino (L)",
    "Wyatt Langford (R)",
    "Zac Veen (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BOS",
    "Alec Bohm (R)": "PHI",
    "Alec Burleson (L)": "STL",
    "Alejandro Kirk (R)": "TOR",
    "Amed Rosario (R)": "NYY",
    "Andres Chaparro (R)": "WSH",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Pinckney (R)": "WSH",
    "Andrew Vaughn (R)": "MIL",
    "Angel Genao (S)": "CLE",
    "Austin Riley (R)": "ATL",
    "Ben Malgeri (R)": "DET",
    "Blaze Alexander (R)": "BAL",
    "Bo Bichette (R)": "NYM",
    "Brady House (R)": "WSH",
    "Brandon Nimmo (L)": "TEX",
    "Brett Callahan (L)": "DET",
    "Bryan Reynolds (S)": "PIT",
    "Cal Raleigh (S)": "SEA",
    "Carter Jensen (L)": "KC",
    "Chase DeLauter (L)": "CLE",
    "Christian Moore (R)": "LAA",
    "Christian Yelich (L)": "MIL",
    "Coby Mayo (R)": "BAL",
    "Cody Bellinger (L)": "NYY",
    "Colt Keith (L)": "DET",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Daylen Lile (L)": "WSH",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Drew Cavanaugh (L)": "SF",
    "Dylan Beavers (L)": "BAL",
    "Edmundo Sosa (R)": "PHI",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Lindor (S)": "NYM",
    "Gabriel Moreno (R)": "ARI",
    "George Lombard Jr. (R)": "NYY",
    "Griffin Conine (L)": "MIA",
    "Hao Yu Lee (R)": "DET",
    "Hector Rodriguez (L)": "CIN",
    "Heliot Ramos (R)": "NYY",
    "Hunter Feduccia (L)": "LAD",
    "Hunter Goodman (R)": "COL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jake McCarthy (L)": "COL",
    "Jarren Duran (L)": "BOS",
    "Jase Bowen (R)": "SD",
    "Jesus Sanchez (L)": "TOR",
    "Jordan Walker (R)": "STL",
    "Jorge Mateo (R)": "TB",
    "Jose Ramirez (S)": "CLE",
    "Jose Tena (L)": "WSH",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kazuma Okamoto (R)": "TOR",
    "Kenny Piper (R)": "TB",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "LaMonte Wade Jr. (L)": "HOU",
    "Leody Taveras (S)": "BAL",
    "Luis Campusano (R)": "SD",
    "Luis Torrens (R)": "NYM",
    "Mark Vientos (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Max Muncy (R)": "ATH",
    "Michael Busch (L)": "CHC",
    "Mickey Gasper (S)": "BOS",
    "Miguel Vargas (R)": "CWS",
    "Mike Yastrzemski (L)": "ATL",
    "Munetaka Murakami (L)": "CWS",
    "Nathaniel Lowe (L)": "CLE",
    "Nelson Velazquez (R)": "HOU",
    "Nolan Gorman (L)": "STL",
    "Oneil Cruz (L)": "PIT",
    "Patrick Wisdom (R)": "SEA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randy Arozarena (R)": "SEA",
    "Roman Anthony (L)": "BOS",
    "Ryan Jeffers (R)": "MIN",
    "Ryan Vilade (R)": "TB",
    "Sal Stewart (R)": "CIN",
    "Seiya Suzuki (R)": "CHC",
    "Spencer Jones (L)": "NYY",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Tommy White (R)": "ATH",
    "Travis d'Arnaud (R)": "LAA",
    "Tristan Peters (L)": "CWS",
    "Turner Hill (L)": "SF",
    "Ty France (R)": "SD",
    "Tyler Stephenson (R)": "CIN",
    "Tyrone Taylor (R)": "CHC",
    "Vaughn Grissom (R)": "LAA",
    "Vinnie Pasquantino (L)": "KC",
    "Willi Castro (S)": "COL",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
    "Zac Veen (L)": "COL",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("NYM @ TB", "Manaea"),
    ("SD @ CIN", "Lodolo"),
    ("TOR @ CLE", "Williams"),
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
        "title": "ATH @ TEX - Brady Basso (L, ATH) vs MacKenzie Gore (L, TEX)",
        "description": "Tail key data: Park boost -14% (stadium -13%, weather -1%). Basso (HR risk -0.74, vs LHB -1.56, vs RHB +0.01). Gore (HR risk -0.30, vs LHB -0.22, vs RHB -0.10).",
        "rows": [
            row("Jake Burger", "R", "+449", 58, "⭐", ["vs Basso"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.1 mph EV. Basso RHB split +0.01, HR risk -0.74. pitcher suppresses HR (-0.74); park/weather net drag (-14%).""", blast="good"),
            row("Justin Foscue", "R", "+690", 58, "💎", ["vs Basso"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 89.9 mph EV. Basso RHB split +0.01, HR risk -0.74. pitcher suppresses HR (-0.74); park/weather net drag (-14%).""", blast="good"),
            row("Wyatt Langford", "R", "+572", 58, "💎", ["vs Basso"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 99.3 mph EV. Basso RHB split +0.01, HR risk -0.74. pitcher suppresses HR (-0.74); park/weather net drag (-14%).""", blast="good"),
            row("Brandon Nimmo", "L", "+625", 58, "", ["vs Basso"], """0 HR, 1 near-HR, 94.2 mph EV. Basso LHB split -1.56, HR risk -0.74. tough split lane (-1.56); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Tommy White", "R", "+1150", 58, "", ["vs Gore"], """0 HR, 92.8 mph EV. Gore RHB split -0.10, HR risk -0.30. slight split headwind (-0.10); pitcher risk below avg (-0.30).""", blast="good"),
            row("Max Muncy", "R", "+575", 58, "", ["vs Gore"], """1 HR, 1 near-HR, 85.8 mph EV. Gore RHB split -0.10, HR risk -0.30. slight split headwind (-0.10); pitcher risk below avg (-0.30).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ WSH - AJ Smith-Shawver (R, ATL) vs Jake Irvin (R, WSH)",
        "description": "Tail key data: Park boost +19% (stadium +3%, weather +16%). Smith-Shawver (HR risk -0.58, vs LHB -0.07, vs RHB -0.85). Irvin (HR risk 0.86, vs LHB +1.00, vs RHB +0.47).",
        "rows": [
            row("Daylen Lile", "L", "+487", 66, "⭐ 🌕 💣", ["vs Smith-Shawver"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 89.1 mph EV. Smith-Shawver LHB split -0.07, HR risk -0.58. slight split headwind (-0.07); pitcher suppresses HR (-0.58).""", blast="high"),
            row("Andrew Pinckney", "R", "N/A", 58, "", ["vs Smith-Shawver"], """0 HR, 98.4 mph EV. Smith-Shawver RHB split -0.85, HR risk -0.58. tough split lane (-0.85); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Andres Chaparro", "R", "+254", 58, "", ["vs Smith-Shawver"], """0 HR, 1 near-HR, 92.7 mph EV. Smith-Shawver RHB split -0.85, HR risk -0.58. tough split lane (-0.85); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Jose Tena", "L", "N/A", 58, "💎", ["vs Smith-Shawver"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.8 mph EV. Smith-Shawver LHB split -0.07, HR risk -0.58. slight split headwind (-0.07); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Brady House", "R", "+531", 61, "💎", ["vs Smith-Shawver"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 98.5 mph EV. Smith-Shawver RHB split -0.85, HR risk -0.58. tough split lane (-0.85); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Mike Yastrzemski", "L", "+480", 82, "🚀 💎", ["vs Irvin"], """Worst Pickz Hidden Gem. 0 HR, 100.4 mph EV. Irvin LHB split +1.00, HR risk 0.86. limited recent HR events.""", blast="good"),
            row("Matt Olson", "L", "+244", 80, "", ["vs Irvin"], """0 HR, 93.3 mph EV. Irvin LHB split +1.00, HR risk 0.86. limited recent HR events.""", blast="good"),
            row("Drake Baldwin", "L", "+335", 84, "", ["vs Irvin"], """0 HR, 2 near-HR, 94.2 mph EV. Irvin LHB split +1.00, HR risk 0.86.""", blast="good"),
            row("Austin Riley", "R", "+390", 71, "", ["vs Irvin"], """0 HR, 1 near-HR, 91.3 mph EV. Irvin RHB split +0.47, HR risk 0.86. limited recent HR events."""),
        ],
    },
    {
        "title": "BAL @ COL - Kyle Bradish (R, BAL) vs Gabriel Hughes (R, COL)",
        "description": "Tail key data: Park boost +24% (stadium +21%, weather +3%). Bradish (HR risk -0.00, vs LHB +0.42, vs RHB -0.23). Hughes (HR risk -0.23, vs LHB -0.23, vs RHB +0.20).",
        "rows": [
            row("Zac Veen", "L", "+630", 74, "🚀 💎", ["vs Bradish"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 100.2 mph EV. Bradish LHB split +0.42, HR risk -0.00.""", blast="good"),
            row("Jake McCarthy", "L", "+900", 70, "", ["vs Bradish"], """1 HR, 2 near-HR, 90.6 mph EV. Bradish LHB split +0.42, HR risk -0.00.""", blast="good"),
            row("Hunter Goodman", "R", "+298", 80, "🌕 💣", ["vs Bradish"], """2 HR, 3 near-HR, 93.2 mph EV. Bradish RHB split -0.23, HR risk -0.00. slight split headwind (-0.23).""", blast="high"),
            row("Willi Castro", "S", "+568", 66, "", ["vs Bradish"], """1 HR, 1 near-HR, 87.7 mph EV. Bradish SHB→LHB split +0.42, HR risk -0.00. lighter EV form (87.7 mph).""", blast="good"),
            row("Blaze Alexander", "R", "N/A", 70, "⭐", ["vs Hughes"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.1 mph EV. Hughes RHB split +0.20, HR risk -0.23. pitcher risk below avg (-0.23).""", blast="good"),
            row("Colton Cowser", "L", "+526", 64, "", ["vs Hughes"], """1 HR, 1 near-HR, 93.9 mph EV. Hughes LHB split -0.23, HR risk -0.23. slight split headwind (-0.23); pitcher risk below avg (-0.23).""", blast="good"),
            row("Pete Alonso", "R", "+285", 68, "", ["vs Hughes"], """1 HR, 1 near-HR, 93.7 mph EV. Hughes RHB split +0.20, HR risk -0.23. pitcher risk below avg (-0.23).""", blast="good"),
            row("Leody Taveras", "S", "+725", 60, "", ["vs Hughes"], """1 HR, 1 near-HR, 83.2 mph EV. Hughes SHB→RHB split +0.20, HR risk -0.23. pitcher risk below avg (-0.23); lighter EV form (83.2 mph).""", blast="good"),
            row("Dylan Beavers", "L", "+592", 62, "⭐", ["vs Hughes"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 93.9 mph EV. Hughes LHB split -0.23, HR risk -0.23. slight split headwind (-0.23); pitcher risk below avg (-0.23).""", blast="good"),
            row("Coby Mayo", "R", "+400", 58, "", ["vs Hughes"], """0 HR, 90.4 mph EV. Hughes RHB split +0.20, HR risk -0.23. pitcher risk below avg (-0.23); limited recent HR events."""),
        ],
    },
    {
        "title": "CWS @ HOU - Sean Burke (R, CWS) vs Ronel Blanco (R, HOU)",
        "description": "Tail key data: Park boost +7% (stadium +7%, weather +0%). Burke (HR risk 0.40, vs LHB +0.85, vs RHB +0.03). Blanco (BAA vs LHB .286, vs RHB .188, HR/9 2.70).",
        "rows": [
            row("Yordan Alvarez", "L", "+290", 80, "⭐", ["vs Burke"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.6 mph EV. Burke LHB split +0.85, HR risk 0.40.""", blast="good"),
            row("LaMonte Wade Jr.", "L", "N/A", 80, "💎", ["vs Burke"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.0 mph EV. Burke LHB split +0.85, HR risk 0.40.""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 69, "💎", ["vs Burke"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.4 mph EV. Burke RHB split +0.03, HR risk 0.40. limited recent HR events.""", blast="good"),
            row("Munetaka Murakami", "L", "+310", 60, "⭐", ["vs Blanco"], """Worst Pickz Favorite. 0 HR, 92.8 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Andrew Benintendi", "L", "+475", 61, "💎", ["vs Blanco"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.3 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Tristan Peters", "L", "+880", 58, "", ["vs Blanco"], """0 HR, 89.8 mph EV. limited split/risk sample; limited recent HR events."""),
            row("Miguel Vargas", "R", "+390", 58, "", ["vs Blanco"], """0 HR, 87.0 mph EV. limited split/risk sample; limited recent HR events."""),
        ],
    },
    {
        "title": "DET @ MIN - Troy Melton (R, DET) vs Andrew Morris (R, MIN)",
        "description": "Tail key data: Park boost +0% (stadium -8%, weather +8%). Melton (HR risk -0.52, vs LHB +0.16, vs RHB -0.92). Morris (HR risk -0.99, vs LHB +0.11, vs RHB -1.11).",
        "rows": [
            row("Kody Clemens", "L", "+446", 67, "💎", ["vs Melton"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 97.5 mph EV. Melton LHB split +0.16, HR risk -0.52. pitcher suppresses HR (-0.52); park suppresses carry (-8%).""", blast="good"),
            row("Ryan Jeffers", "R", "+630", 58, "🌕 💣", ["vs Melton"], """2 HR, 2 near-HR, 87.1 mph EV. Melton RHB split -0.92, HR risk -0.52. tough split lane (-0.92); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Ben Malgeri", "R", "+830", 58, "💎", ["vs Morris"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.7 mph EV. Morris RHB split -1.11, HR risk -0.99. tough split lane (-1.11); pitcher suppresses HR (-0.99).""", blast="good"),
            row("Brett Callahan", "L", "+792", 58, "", ["vs Morris"], """0 HR, 1 near-HR, 96.7 mph EV. Morris LHB split +0.11, HR risk -0.99. pitcher suppresses HR (-0.99); park suppresses carry (-8%).""", blast="good"),
            row("Colt Keith", "L", "+850", 58, "", ["vs Morris"], """0 HR, 89.9 mph EV. Morris LHB split +0.11, HR risk -0.99. pitcher suppresses HR (-0.99); park suppresses carry (-8%)."""),
            row("Hao Yu Lee", "R", "+650", 58, "", ["vs Morris"], """1 HR, 1 near-HR, 92.9 mph EV. Morris RHB split -1.11, HR risk -0.99. tough split lane (-1.11); pitcher suppresses HR (-0.99).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ KC - Tyler Phillips (R, MIA) vs Randy Dobnak (R, KC)",
        "description": "Tail key data: Park boost +17% (stadium +12%, weather +5%). Phillips (HR risk 0.38, vs LHB +0.08, vs RHB +0.49). Dobnak (HR risk -1.32, vs LHB -0.69, vs RHB -1.26).",
        "rows": [
            row("Carter Jensen", "L", "+408", 74, "⭐", ["vs Phillips"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.9 mph EV. Phillips LHB split +0.08, HR risk 0.38.""", blast="good"),
            row("Jac Caglianone", "L", "+380", 67, "⭐", ["vs Phillips"], """Worst Pickz Favorite. 0 HR, 98.3 mph EV. Phillips LHB split +0.08, HR risk 0.38. limited recent HR events.""", blast="good"),
            row("Vinnie Pasquantino", "L", "+519", 59, "💎", ["vs Phillips"], """Worst Pickz Hidden Gem. 0 HR, 91.4 mph EV. Phillips LHB split +0.08, HR risk 0.38. limited recent HR events."""),
            row("Kyle Stowers", "L", "+310", 58, "⭐", ["vs Dobnak"], """Worst Pickz Favorite. 0 HR, 95.8 mph EV. Dobnak LHB split -0.69, HR risk -1.32. tough split lane (-0.69); pitcher suppresses HR (-1.32).""", blast="good"),
            row("Griffin Conine", "L", "+396", 58, "🌕 💣", ["vs Dobnak"], """2 HR, 2 near-HR, 91.9 mph EV. Dobnak LHB split -0.69, HR risk -1.32. tough split lane (-0.69); pitcher suppresses HR (-1.32).""", blast="high"),
        ],
    },
    {
        "title": "MIL @ CHC - Robert Gasser (L, MIL) vs Matthew Boyd (L, CHC)",
        "description": "Tail key data: Park boost +26% (stadium -2%, weather +27%). Gasser (HR risk 0.11, vs LHB -0.49, vs RHB +0.21). Boyd (HR risk 0.74, vs LHB -1.27, vs RHB +1.14).",
        "rows": [
            row("Tyrone Taylor", "R", "+521", 64, "", ["vs Gasser"], """1 HR, 1 near-HR, 85.3 mph EV. Gasser RHB split +0.21, HR risk 0.11. lighter EV form (85.3 mph).""", blast="good"),
            row("Seiya Suzuki", "R", "+310", 66, "⭐", ["vs Gasser"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 88.8 mph EV. Gasser RHB split +0.21, HR risk 0.11.""", blast="good"),
            row("Michael Busch", "L", "+477", 62, "💎", ["vs Gasser"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 89.6 mph EV. Gasser LHB split -0.49, HR risk 0.11. tough split lane (-0.49).""", blast="good"),
            row("Pete Crow Armstrong", "L", "+290", 66, "💎", ["vs Gasser"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 92.1 mph EV. Gasser LHB split -0.49, HR risk 0.11. tough split lane (-0.49).""", blast="good"),
            row("Jake Bauers", "L", "+500", 72, "", ["vs Boyd"], """1 HR, 1 near-HR, 92.7 mph EV. Boyd LHB split -1.27, HR risk 0.74. tough split lane (-1.27).""", blast="good"),
            row("Jackson Chourio", "R", "+340", 87, "", ["vs Boyd"], """1 HR, 1 near-HR, 92.8 mph EV. Boyd RHB split +1.14, HR risk 0.74.""", blast="good"),
            row("Christian Yelich", "L", "+920", 68, "", ["vs Boyd"], """0 HR, 2 near-HR, 90.7 mph EV. Boyd LHB split -1.27, HR risk 0.74. tough split lane (-1.27).""", blast="good"),
            row("Andrew Vaughn", "R", "+520", 82, "", ["vs Boyd"], """0 HR, 93.7 mph EV. Boyd RHB split +1.14, HR risk 0.74. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "NYM @ TB - Sean Manaea 🧤 (L, NYM) vs Freddy Peralta (R, TB)",
        "description": "Tail key data: Park boost -2% (stadium -3%, weather +1%). Manaea 🧤 (HR risk 1.29, vs LHB -0.07, vs RHB +1.30). Peralta (HR risk 0.27, vs LHB +0.33, vs RHB +0.25).",
        "rows": [
            row("Ryan Vilade", "R", "+550", 91, "🚀 🌕 💣 💎", ["vs Manaea"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 102.6 mph EV. Manaea RHB split +1.30, HR risk 1.29.""", blast="good"),
            row("Junior Caminero", "R", "+280", 90, "🚀 ⭐ 🌕 💣", ["vs Manaea"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 102.8 mph EV. Manaea RHB split +1.30, HR risk 1.29.""", blast="good"),
            row("Kenny Piper", "R", "N/A", 90, "🚀 🌕 💣 💎", ["vs Manaea"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 102.5 mph EV. Manaea RHB split +1.30, HR risk 1.29.""", blast="good"),
            row("Jorge Mateo", "R", "+725", 86, "", ["vs Manaea"], """0 HR, 96.4 mph EV. Manaea RHB split +1.30, HR risk 1.29. limited recent HR events.""", blast="good"),
            row("Mark Vientos", "R", "N/A", 64, "💎", ["vs Peralta"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.5 mph EV. Peralta RHB split +0.25, HR risk 0.27. limited recent HR events.""", blast="good"),
            row("Luis Torrens", "R", "+1080", 81, "🌕 💣", ["vs Peralta"], """3 HR, 3 near-HR, 91.2 mph EV. Peralta RHB split +0.25, HR risk 0.27.""", blast="high"),
            row("Francisco Lindor", "S", "+472", 66, "", ["vs Peralta"], """1 HR, 2 near-HR, 91.5 mph EV. Peralta SHB→LHB split +0.33, HR risk 0.27.""", blast="good"),
            row("Bo Bichette", "R", "+680", 64, "", ["vs Peralta"], """0 HR, 1 near-HR, 97.0 mph EV. Peralta RHB split +0.25, HR risk 0.27. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "NYY @ LAA - Gerrit Cole (R, NYY) vs Grayson Rodriguez (R, LAA)",
        "description": "Tail key data: Park boost -7% (stadium -9%, weather +2%). Cole (HR risk -0.43, vs LHB -0.20, vs RHB -0.31). Rodriguez (HR risk -0.62, vs LHB -0.35, vs RHB -0.48).",
        "rows": [
            row("Vaughn Grissom", "R", "+910", 58, "", ["vs Cole"], """0 HR, 1 near-HR, 89.4 mph EV. Cole RHB split -0.31, HR risk -0.43. slight split headwind (-0.31); pitcher suppresses HR (-0.43)."""),
            row("Zach Neto", "R", "+432", 58, "", ["vs Cole"], """1 HR, 1 near-HR, 95.2 mph EV. Cole RHB split -0.31, HR risk -0.43. slight split headwind (-0.31); pitcher suppresses HR (-0.43).""", blast="good"),
            row("Christian Moore", "R", "+564", 58, "💎", ["vs Cole"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 90.1 mph EV. Cole RHB split -0.31, HR risk -0.43. slight split headwind (-0.31); pitcher suppresses HR (-0.43).""", blast="good"),
            row("Travis d'Arnaud", "R", "N/A", 58, "", ["vs Cole"], """0 HR, 1 near-HR, 94.9 mph EV. Cole RHB split -0.31, HR risk -0.43. slight split headwind (-0.31); pitcher suppresses HR (-0.43).""", blast="good"),
            row("Spencer Jones", "L", "+476", 58, "💎", ["vs Grayson Rodriguez"], """Worst Pickz Hidden Gem. 0 HR, 95.1 mph EV. Grayson Rodriguez LHB split -0.35, HR risk -0.62. slight split headwind (-0.35); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Heliot Ramos", "R", "N/A", 58, "", ["vs Grayson Rodriguez"], """0 HR, 90.1 mph EV. Grayson Rodriguez RHB split -0.48, HR risk -0.62. tough split lane (-0.48); pitcher suppresses HR (-0.62)."""),
            row("George Lombard Jr.", "R", "N/A", 58, "💎", ["vs Grayson Rodriguez"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 97.0 mph EV. Grayson Rodriguez RHB split -0.48, HR risk -0.62. tough split lane (-0.48); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Cody Bellinger", "L", "+480", 58, "", ["vs Grayson Rodriguez"], """0 HR, 89.0 mph EV. Grayson Rodriguez LHB split -0.35, HR risk -0.62. slight split headwind (-0.35); pitcher suppresses HR (-0.62)."""),
            row("Amed Rosario", "R", "+725", 58, "🌕 💣", ["vs Grayson Rodriguez"], """2 HR, 2 near-HR, 91.0 mph EV. Grayson Rodriguez RHB split -0.48, HR risk -0.62. tough split lane (-0.48); pitcher suppresses HR (-0.62).""", blast="high"),
        ],
    },
    {
        "title": "PHI @ ARI - Jesus Luzardo (L, PHI) vs Eduardo Rodriguez (L, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Luzardo (HR risk -0.68, vs LHB -1.35, vs RHB -0.20). Rodriguez (HR risk -0.96, vs LHB -0.84, vs RHB -0.49).",
        "rows": [
            row("Ketel Marte", "S", "+525", 58, "💎", ["vs Luzardo"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.8 mph EV. Luzardo SHB→RHB split -0.20, HR risk -0.68. slight split headwind (-0.20); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Gabriel Moreno", "R", "+1040", 58, "💎", ["vs Luzardo"], """Worst Pickz Hidden Gem. 0 HR, 89.4 mph EV. Luzardo RHB split -0.20, HR risk -0.68. slight split headwind (-0.20); pitcher suppresses HR (-0.68)."""),
            row("Corbin Carroll", "L", "+780", 58, "⭐", ["vs Luzardo"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 99.6 mph EV. Luzardo LHB split -1.35, HR risk -0.68. tough split lane (-1.35); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Tim Tawa", "R", "+1000", 58, "", ["vs Luzardo"], """0 HR, 96.1 mph EV. Luzardo RHB split -0.20, HR risk -0.68. slight split headwind (-0.20); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Edmundo Sosa", "R", "+850", 58, "💎", ["vs Eduardo Rodriguez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.9 mph EV. Eduardo Rodriguez RHB split -0.49, HR risk -0.96. tough split lane (-0.49); pitcher suppresses HR (-0.96).""", blast="good"),
            row("Kyle Schwarber", "L", "+366", 58, "💎", ["vs Eduardo Rodriguez"], """Worst Pickz Hidden Gem. 0 HR, 92.8 mph EV. Eduardo Rodriguez LHB split -0.84, HR risk -0.96. tough split lane (-0.84); pitcher suppresses HR (-0.96).""", blast="good"),
            row("Alec Bohm", "R", "+910", 58, "", ["vs Eduardo Rodriguez"], """0 HR, 91.5 mph EV. Eduardo Rodriguez RHB split -0.49, HR risk -0.96. tough split lane (-0.49); pitcher suppresses HR (-0.96)."""),
        ],
    },
    {
        "title": "SD @ CIN - Randy Vasquez (R, SD) vs Nick Lodolo 🧤 (L, CIN)",
        "description": "Tail key data: Park boost +19% (stadium +14%, weather +5%). Vasquez (HR risk -0.47, vs LHB -0.04, vs RHB -0.49). Lodolo 🧤 (HR risk 1.24, vs LHB -0.01, vs RHB +1.06).",
        "rows": [
            row("Hector Rodriguez", "L", "+452", 73, "🌕 💣", ["vs Vasquez"], """2 HR, 2 near-HR, 94.6 mph EV. Vasquez LHB split -0.04, HR risk -0.47. slight split headwind (-0.04); pitcher suppresses HR (-0.47).""", blast="high"),
            row("Sal Stewart", "R", "+369", 58, "⭐", ["vs Vasquez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 90.9 mph EV. Vasquez RHB split -0.49, HR risk -0.47. tough split lane (-0.49); pitcher suppresses HR (-0.47).""", blast="good"),
            row("Elly De La Cruz", "S", "+390", 58, "💎", ["vs Vasquez"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.9 mph EV. Vasquez SHB→LHB split -0.04, HR risk -0.47. slight split headwind (-0.04); pitcher suppresses HR (-0.47).""", blast="good"),
            row("Tyler Stephenson", "R", "+478", 58, "", ["vs Vasquez"], """1 HR, 1 near-HR, 91.9 mph EV. Vasquez RHB split -0.49, HR risk -0.47. tough split lane (-0.49); pitcher suppresses HR (-0.47).""", blast="good"),
            row("Jase Bowen", "R", "N/A", 92, "🌕 💣", ["vs Lodolo"], """1 HR, 1 near-HR, 97.0 mph EV. Lodolo RHB split +1.06, HR risk 1.24.""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+270", 94, "🌕 💣", ["vs Lodolo"], """2 HR, 2 near-HR, 93.0 mph EV. Lodolo RHB split +1.06, HR risk 1.24.""", blast="high"),
            row("Luis Campusano", "R", "N/A", 90, "🌕 💣", ["vs Lodolo"], """1 HR, 1 near-HR, 92.9 mph EV. Lodolo RHB split +1.06, HR risk 1.24.""", blast="good"),
            row("Ty France", "R", "+497", 87, "", ["vs Lodolo"], """1 HR, 1 near-HR, 89.1 mph EV. Lodolo RHB split +1.06, HR risk 1.24.""", blast="good"),
        ],
    },
    {
        "title": "SEA @ BOS - Bryan Woo (R, SEA) vs Jedixson Paez (R, BOS)",
        "description": "Tail key data: Park boost -16% (stadium -8%, weather -7%). Woo (HR risk 0.59, vs LHB +0.80, vs RHB +0.17). Paez (season BAA .333).",
        "rows": [
            row("Adley Rutschman", "S", "+800", 76, "⭐", ["vs Woo"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.3 mph EV. Woo SHB→LHB split +0.80, HR risk 0.59. park/weather net drag (-16%).""", blast="good"),
            row("Roman Anthony", "L", "+725", 71, "💎", ["vs Woo"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 97.1 mph EV. Woo LHB split +0.80, HR risk 0.59. park/weather net drag (-16%); limited recent HR events.""", blast="good"),
            row("Mickey Gasper", "S", "+725", 88, "🌕 💣", ["vs Woo"], """3 HR, 3 near-HR, 91.2 mph EV. Woo SHB→LHB split +0.80, HR risk 0.59. park/weather net drag (-16%).""", blast="high"),
            row("Jarren Duran", "L", "+725", 71, "💎", ["vs Woo"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.2 mph EV. Woo LHB split +0.80, HR risk 0.59. park/weather net drag (-16%); limited recent HR events.""", blast="good"),
            row("Cal Raleigh", "S", "N/A", 80, "🚀 ⭐ 🌕 💣", ["vs Paez"], """Worst Pickz Favorite. 4 HR, 5 near-HR, 101.9 mph EV. limited split/risk sample; park/weather net drag (-16%).""", blast="high"),
            row("Dominic Canzone", "L", "N/A", 58, "💎", ["vs Paez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.9 mph EV. limited split/risk sample; park/weather net drag (-16%).""", blast="good"),
            row("Randy Arozarena", "R", "N/A", 58, "", ["vs Paez"], """0 HR, 93.0 mph EV. limited split/risk sample; park/weather net drag (-16%).""", blast="good"),
            row("Patrick Wisdom", "R", "N/A", 58, "", ["vs Paez"], """0 HR, 2 near-HR, 93.2 mph EV. limited split/risk sample; park/weather net drag (-16%).""", blast="good"),
        ],
    },
    {
        "title": "SF @ PIT - Logan Webb (R, SF) vs Paul Skenes (R, PIT)",
        "description": "Tail key data: Park boost +3% (stadium -14%, weather +17%). Webb (HR risk -0.83, vs LHB -0.52, vs RHB -0.55). Skenes (HR risk -0.18, vs LHB -0.11, vs RHB -0.02).",
        "rows": [
            row("Oneil Cruz", "L", "+475", 58, "⭐ 🌕 💣", ["vs Webb"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 89.8 mph EV. Webb LHB split -0.52, HR risk -0.83. tough split lane (-0.52); pitcher suppresses HR (-0.83).""", blast="high"),
            row("Esmerlyn Valdez", "R", "+600", 58, "", ["vs Webb"], """0 HR, 90.0 mph EV. Webb RHB split -0.55, HR risk -0.83. tough split lane (-0.55); pitcher suppresses HR (-0.83)."""),
            row("Bryan Reynolds", "S", "+875", 58, "💎", ["vs Webb"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.0 mph EV. Webb SHB→LHB split -0.52, HR risk -0.83. tough split lane (-0.52); pitcher suppresses HR (-0.83).""", blast="good"),
            row("Rafael Devers", "L", "+361", 72, "⭐ 🌕 💣", ["vs Skenes"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 99.0 mph EV. Skenes LHB split -0.11, HR risk -0.18. slight split headwind (-0.11); pitcher risk below avg (-0.18).""", blast="high"),
            row("Turner Hill", "L", "+1396", 58, "", ["vs Skenes"], """0 HR, 2 near-HR, 91.6 mph EV. Skenes LHB split -0.11, HR risk -0.18. slight split headwind (-0.11); pitcher risk below avg (-0.18).""", blast="good"),
            row("Drew Cavanaugh", "L", "+1250", 58, "", ["vs Skenes"], """0 HR, 1 near-HR, 90.5 mph EV. Skenes LHB split -0.11, HR risk -0.18. slight split headwind (-0.11); pitcher risk below avg (-0.18)."""),
        ],
    },
    {
        "title": "STL @ LAD - Michael McGreevy (R, STL) vs Eric Lauer (L, LAD)",
        "description": "Tail key data: Park boost +18% (stadium +18%, weather +0%). McGreevy (HR risk 0.37, vs LHB +1.03, vs RHB -0.28). Lauer (HR risk 0.66, vs LHB +1.40, vs RHB +0.21).",
        "rows": [
            row("Max Muncy", "L", "+409", 61, "", ["vs McGreevy"], """0 HR, 83.6 mph EV. McGreevy LHB split +1.03, HR risk 0.37. limited recent HR events; lighter EV form (83.6 mph)."""),
            row("Hunter Feduccia", "L", "N/A", 74, "💎", ["vs McGreevy"], """Worst Pickz Hidden Gem. 0 HR, 94.6 mph EV. McGreevy LHB split +1.03, HR risk 0.37. limited recent HR events.""", blast="good"),
            row("Teoscar Hernandez", "R", "+470", 58, "💎", ["vs McGreevy"], """Worst Pickz Hidden Gem. 0 HR, 89.6 mph EV. McGreevy RHB split -0.28, HR risk 0.37. slight split headwind (-0.28); limited recent HR events."""),
            row("Jordan Walker", "R", "+324", 89, "⭐ 🌕 💣", ["vs Lauer"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.9 mph EV. Lauer RHB split +0.21, HR risk 0.66.""", blast="high"),
            row("Alec Burleson", "L", "+483", 74, "⭐", ["vs Lauer"], """Worst Pickz Favorite. 0 HR, 90.8 mph EV. Lauer LHB split +1.40, HR risk 0.66. limited recent HR events."""),
            row("Nolan Gorman", "L", "N/A", 71, "💎", ["vs Lauer"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 85.4 mph EV. Lauer LHB split +1.40, HR risk 0.66. limited recent HR events; lighter EV form (85.4 mph)."""),
        ],
    },
    {
        "title": "TOR @ CLE - Spencer Miles (R, TOR) vs Gavin Williams 🧤 (R, CLE)",
        "description": "Tail key data: Park boost +17% (stadium -4%, weather +21%). Miles (HR risk -1.16, vs LHB +0.03, vs RHB -1.60). Williams 🧤 (HR risk 1.44, vs LHB +0.17, vs RHB +2.25).",
        "rows": [
            row("Nathaniel Lowe", "L", "N/A", 59, "⭐", ["vs Miles"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.6 mph EV. Miles LHB split +0.03, HR risk -1.16. pitcher suppresses HR (-1.16).""", blast="good"),
            row("Jose Ramirez", "S", "N/A", 58, "", ["vs Miles"], """1 HR, 1 near-HR, 92.8 mph EV. Miles SHB→LHB split +0.03, HR risk -1.16. pitcher suppresses HR (-1.16).""", blast="good"),
            row("Chase DeLauter", "L", "N/A", 58, "", ["vs Miles"], """0 HR, 95.6 mph EV. Miles LHB split +0.03, HR risk -1.16. pitcher suppresses HR (-1.16); limited recent HR events.""", blast="good"),
            row("Angel Genao", "S", "N/A", 58, "", ["vs Miles"], """0 HR, 91.3 mph EV. Miles SHB→LHB split +0.03, HR risk -1.16. pitcher suppresses HR (-1.16); limited recent HR events."""),
            row("Alejandro Kirk", "R", "+930", 93, "⭐ 🌕 💣", ["vs Williams"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.6 mph EV. Williams RHB split +2.25, HR risk 1.44.""", blast="good"),
            row("Jesus Sanchez", "L", "+710", 74, "💎", ["vs Williams"], """Worst Pickz Hidden Gem. 0 HR, 91.3 mph EV. Williams LHB split +0.17, HR risk 1.44. limited recent HR events."""),
            row("Kazuma Okamoto", "R", "+481", 92, "🌕 💣", ["vs Williams"], """1 HR, 2 near-HR, 88.0 mph EV. Williams RHB split +2.25, HR risk 1.44.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-01")

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

    out = ROOT / '_games-0901.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
