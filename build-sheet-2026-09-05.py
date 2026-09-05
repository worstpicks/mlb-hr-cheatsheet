#!/usr/bin/env python3
"""Generate games[] block for 2026-09-05 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Elly De La Cruz (S)",
    "Esmerlyn Valdez (R)",
    "Jo Adell (R)",
    "Jordan Walker (R)",
    "Jose Ramirez (S)",
    "Junior Caminero (R)",
    "Lars Nootbaar (L)",
    "Lawrence Butler (L)",
    "Max Muncy (L)",
    "Mookie Betts (R)",
    "Roman Anthony (L)",
}

GEMS = {
    "Brandon Nimmo (L)",
    "George Springer (R)",
    "Heliot Ramos (R)",
    "Jac Caglianone (L)",
    "Konnor Griffin (R)",
    "Kyle Tucker (L)",
    "Max Kepler (L)",
    "Mickey Gasper (S)",
    "Pete Alonso (R)",
    "Salvador Perez (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Alejandro Kirk (R)": "TOR",
    "Amed Rosario (R)": "NYY",
    "Andres Chaparro (R)": "WSH",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Vaughn (R)": "MIL",
    "Angel Genao (S)": "CLE",
    "Angel Martinez (S)": "CLE",
    "Brady House (R)": "WSH",
    "Brandon Nimmo (L)": "TEX",
    "Bryan Reynolds (S)": "PIT",
    "Bryson Stott (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Carter Jensen (L)": "KC",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Colton Cowser (L)": "BAL",
    "Corey Seager (L)": "TEX",
    "Dalton Rushing (L)": "LAD",
    "Daylen Lile (L)": "WSH",
    "Drake Baldwin (L)": "ATL",
    "Dylan Crews (R)": "WSH",
    "Edmundo Sosa (R)": "PHI",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Fernando Tatis Jr. (R)": "SD",
    "Freddy Fermin (R)": "SD",
    "Garrett Mitchell (L)": "MIL",
    "George Springer (R)": "TOR",
    "Gleyber Torres (R)": "DET",
    "Heliot Ramos (R)": "NYY",
    "Hunter Goodman (R)": "COL",
    "Ivan Herrera (R)": "STL",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake McCarthy (L)": "COL",
    "Jarren Duran (L)": "BOS",
    "Javier Baez (R)": "DET",
    "Jo Adell (R)": "CLE",
    "Joc Pederson (L)": "TEX",
    "Jonah Heim (S)": "ATH",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Jose Ramirez (S)": "CLE",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Konnor Griffin (R)": "PIT",
    "Kyle Tucker (L)": "LAD",
    "Lars Nootbaar (L)": "ARI",
    "Lawrence Butler (L)": "ATH",
    "Leonardo Bernal (S)": "STL",
    "Luke Keaschall (R)": "MIN",
    "Max Kepler (L)": "ARI",
    "Max Muncy (L)": "LAD",
    "Michael Harris II (L)": "ATL",
    "Mickey Gasper (S)": "BOS",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Moises Ballesteros (L)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Oneil Cruz (L)": "PIT",
    "Ozzie Albies (S)": "ATL",
    "Pete Alonso (R)": "BAL",
    "Randy Arozarena (R)": "SEA",
    "Roman Anthony (L)": "BOS",
    "Royce Lewis (R)": "MIN",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "TJ Rumfield (L)": "COL",
    "Teoscar Hernandez (R)": "LAD",
    "Ty France (R)": "SD",
    "Tyler Stephenson (R)": "CIN",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("ARI @ HOU", "Pecko"),
    ("ATH @ SEA", "Springs"),
    ("STL @ COL", "Adams"),
    ("STL @ COL", "Liberatore"),
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
        "title": "ARI @ HOU - Brandon Pfaadt (R, ARI) vs Ethan Pecko 🧤 (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +0%). Pfaadt (HR risk -0.30, vs LHB +0.21, vs RHB -0.87). Pecko 🧤 (HR risk 2.09, vs LHB +2.44, vs RHB -1.34).",
        "rows": [
            row("Lars Nootbaar", "L", "+450", 97, "⭐ 🌕 💣", ["vs Pecko"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 99.4 mph EV. Pecko LHB split +2.44, HR risk 2.09.""", blast="high"),
            row("Max Kepler", "L", "+550", 91, "🌕 💣 💎", ["vs Pecko"], """Worst Pickz Hidden Gem. 0 HR, 94.1 mph EV. Pecko LHB split +2.44, HR risk 2.09. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "ATH @ SEA - Jeffrey Springs 🧤 (L, ATH) vs George Kirby (R, SEA)",
        "description": "Tail key data: Park boost -2% (stadium +1%, weather -3%). Springs 🧤 (HR risk 0.96, vs LHB +1.58, vs RHB +0.25). Kirby (HR risk -0.25, vs LHB +0.22, vs RHB -0.94).",
        "rows": [
            row("Cal Raleigh", "S", "+340", 80, "", ["vs Springs"], """1 HR, 1 near-HR, 97.0 mph EV. Springs SHB→RHB split +0.25, HR risk 0.96.""", blast="good"),
            row("Julio Rodriguez", "R", "+413", 74, "", ["vs Springs"], """0 HR, 1 near-HR, 94.5 mph EV. Springs RHB split +0.25, HR risk 0.96. limited recent HR events.""", blast="good"),
            row("Randy Arozarena", "R", "+420", 71, "", ["vs Springs"], """1 HR, 1 near-HR, 87.1 mph EV. Springs RHB split +0.25, HR risk 0.96. lighter EV form (87.1 mph).""", blast="good"),
            row("Lawrence Butler", "L", "+600", 58, "⭐", ["vs Kirby"], """Worst Pickz Favorite. 0 HR, 98.8 mph EV. Kirby LHB split +0.22, HR risk -0.25. pitcher risk below avg (-0.25); limited recent HR events.""", blast="good"),
            row("Jonah Heim", "S", "+830", 58, "", ["vs Kirby"], """0 HR, 92.0 mph EV. Kirby SHB→LHB split +0.22, HR risk -0.25. pitcher risk below avg (-0.25); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "ATL @ PHI - Martin Perez (L, ATL) vs Zack Wheeler (R, PHI)",
        "description": "Tail key data: Park boost -3% (stadium +14%, weather -17%). Perez (HR risk -1.20, vs LHB +0.12, vs RHB -1.03). Wheeler (HR risk 0.13, vs LHB +0.83, vs RHB -0.77).",
        "rows": [
            row("Edmundo Sosa", "R", "+630", 58, "", ["vs Perez"], """1 HR, 1 near-HR, 93.5 mph EV. Perez RHB split -1.03, HR risk -1.20. tough split lane (-1.03); pitcher suppresses HR (-1.20).""", blast="good"),
            row("Bryson Stott", "L", "+1000", 58, "", ["vs Perez"], """0 HR, 1 near-HR, 89.9 mph EV. Perez LHB split +0.12, HR risk -1.20. pitcher suppresses HR (-1.20); weather carry headwind (-17%)."""),
            row("Drake Baldwin", "L", "+444", 67, "", ["vs Wheeler"], """0 HR, 1 near-HR, 95.3 mph EV. Wheeler LHB split +0.83, HR risk 0.13. weather carry headwind (-17%); limited recent HR events.""", blast="good"),
            row("Michael Harris II", "L", "+488", 73, "🌕 💣", ["vs Wheeler"], """2 HR, 2 near-HR, 88.3 mph EV. Wheeler LHB split +0.83, HR risk 0.13. weather carry headwind (-17%).""", blast="high"),
            row("Ozzie Albies", "S", "+598", 65, "", ["vs Wheeler"], """1 HR, 1 near-HR, 89.8 mph EV. Wheeler SHB→LHB split +0.83, HR risk 0.13. weather carry headwind (-17%).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ BAL - Sonny Gray (R, BOS) vs Chris Bassitt (R, BAL)",
        "description": "Tail key data: Park boost -9% (stadium -3%, weather -6%). Gray (HR risk -0.69, vs LHB -0.57, vs RHB -0.07). Bassitt (HR risk -0.26, vs LHB +0.13, vs RHB -0.65).",
        "rows": [
            row("Pete Alonso", "R", "+370", 58, "💎", ["vs Gray"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.4 mph EV. Gray RHB split -0.07, HR risk -0.69. slight split headwind (-0.07); pitcher suppresses HR (-0.69).""", blast="good"),
            row("Christian Encarnacion-Strand", "R", "+497", 58, "", ["vs Gray"], """0 HR, 87.9 mph EV. Gray RHB split -0.07, HR risk -0.69. slight split headwind (-0.07); pitcher suppresses HR (-0.69)."""),
            row("Colton Cowser", "L", "+700", 58, "", ["vs Gray"], """1 HR, 1 near-HR, 96.4 mph EV. Gray LHB split -0.57, HR risk -0.69. tough split lane (-0.57); pitcher suppresses HR (-0.69).""", blast="good"),
            row("Roman Anthony", "L", "+525", 62, "🚀 ⭐", ["vs Bassitt"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 101.0 mph EV. Bassitt LHB split +0.13, HR risk -0.26. pitcher risk below avg (-0.26); park/weather net drag (-9%).""", blast="good"),
            row("Mickey Gasper", "S", "+568", 64, "🌕 💣 💎", ["vs Bassitt"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 89.9 mph EV. Bassitt SHB→LHB split +0.13, HR risk -0.26. pitcher risk below avg (-0.26); park/weather net drag (-9%).""", blast="high"),
            row("Jarren Duran", "L", "+525", 58, "", ["vs Bassitt"], """0 HR, 96.7 mph EV. Bassitt LHB split +0.13, HR risk -0.26. pitcher risk below avg (-0.26); park/weather net drag (-9%).""", blast="good"),
        ],
    },
    {
        "title": "DET @ CLE - Framber Valdez (L, DET) vs Parker Messick (L, CLE)",
        "description": "Tail key data: Park boost -10% (stadium -4%, weather -6%). Valdez (HR risk -0.59, vs LHB -0.68, vs RHB -0.24). Messick (HR risk -1.07, vs LHB -0.76, vs RHB -0.61).",
        "rows": [
            row("Jo Adell", "R", "+560", 64, "🚀 ⭐ 🌕 💣", ["vs Valdez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.4 mph EV. Valdez RHB split -0.24, HR risk -0.59. slight split headwind (-0.24); pitcher suppresses HR (-0.59).""", blast="high"),
            row("Angel Genao", "S", "+1350", 58, "", ["vs Valdez"], """1 HR, 1 near-HR, 97.0 mph EV. Valdez SHB→RHB split -0.24, HR risk -0.59. slight split headwind (-0.24); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Angel Martinez", "S", "+820", 58, "", ["vs Valdez"], """1 HR, 1 near-HR, 99.3 mph EV. Valdez SHB→RHB split -0.24, HR risk -0.59. slight split headwind (-0.24); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Jose Ramirez", "S", "+670", 58, "⭐", ["vs Valdez"], """Worst Pickz Favorite. 0 HR, 99.0 mph EV. Valdez SHB→RHB split -0.24, HR risk -0.59. slight split headwind (-0.24); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Gleyber Torres", "R", "+910", 58, "", ["vs Messick"], """0 HR, 1 near-HR, 94.8 mph EV. Messick RHB split -0.61, HR risk -1.07. tough split lane (-0.61); pitcher suppresses HR (-1.07).""", blast="good"),
            row("Javier Baez", "R", "+1480", 58, "", ["vs Messick"], """0 HR, 82.0 mph EV. Messick RHB split -0.61, HR risk -1.07. tough split lane (-0.61); pitcher suppresses HR (-1.07)."""),
        ],
    },
    {
        "title": "LAA @ PIT - Yusei Kikuchi (L, LAA) vs Braxton Ashcraft (R, PIT)",
        "description": "Tail key data: Park boost -5% (stadium -15%, weather +10%). Kikuchi (HR risk 0.79, vs LHB -0.48, vs RHB +0.95). Ashcraft (HR risk -0.36, vs LHB -0.09, vs RHB -0.37).",
        "rows": [
            row("Esmerlyn Valdez", "R", "+485", 93, "⭐ 🌕 💣", ["vs Kikuchi"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 96.5 mph EV. Kikuchi RHB split +0.95, HR risk 0.79. park/weather net drag (-5%).""", blast="high"),
            row("Konnor Griffin", "R", "+710", 81, "💎", ["vs Kikuchi"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.3 mph EV. Kikuchi RHB split +0.95, HR risk 0.79. park/weather net drag (-5%).""", blast="good"),
            row("Oneil Cruz", "L", "+450", 58, "", ["vs Kikuchi"], """0 HR, 1 near-HR, 89.1 mph EV. Kikuchi LHB split -0.48, HR risk 0.79. tough split lane (-0.48); park/weather net drag (-5%)."""),
            row("Bryan Reynolds", "S", "+700", 73, "", ["vs Kikuchi"], """0 HR, 1 near-HR, 92.1 mph EV. Kikuchi SHB→RHB split +0.95, HR risk 0.79. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
            row("Moises Ballesteros", "L", "+900", 58, "", ["vs Ashcraft"], """1 HR, 1 near-HR, 95.0 mph EV. Ashcraft LHB split -0.09, HR risk -0.36. slight split headwind (-0.09); pitcher risk below avg (-0.36).""", blast="good"),
            row("Zach Neto", "R", "+557", 58, "", ["vs Ashcraft"], """1 HR, 1 near-HR, 97.5 mph EV. Ashcraft RHB split -0.37, HR risk -0.36. slight split headwind (-0.37); pitcher risk below avg (-0.36).""", blast="good"),
            row("Mike Trout", "R", "+540", 58, "", ["vs Ashcraft"], """0 HR, 95.1 mph EV. Ashcraft RHB split -0.37, HR risk -0.36. slight split headwind (-0.37); pitcher risk below avg (-0.36).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ CIN - Dustin May (R, MIL) vs Andrew Abbott (L, CIN)",
        "description": "Tail key data: Park boost +29% (stadium +14%, weather +15%). May (HR risk -0.11, vs LHB -0.57, vs RHB +0.51). Abbott (HR risk 0.03, vs LHB +0.51, vs RHB -0.13).",
        "rows": [
            row("Tyler Stephenson", "R", "+520", 73, "", ["vs May"], """1 HR, 1 near-HR, 93.9 mph EV. May RHB split +0.51, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="good"),
            row("Elly De La Cruz", "S", "+475", 62, "⭐", ["vs May"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 98.3 mph EV. May SHB→LHB split -0.57, HR risk -0.11. tough split lane (-0.57); pitcher risk below avg (-0.11).""", blast="good"),
            row("Sal Stewart", "R", "+391", 69, "", ["vs May"], """0 HR, 1 near-HR, 94.2 mph EV. May RHB split +0.51, HR risk -0.11. pitcher risk below avg (-0.11); limited recent HR events.""", blast="good"),
            row("JJ Bleday", "L", "+417", 65, "", ["vs May"], """1 HR, 1 near-HR, 94.9 mph EV. May LHB split -0.57, HR risk -0.11. tough split lane (-0.57); pitcher risk below avg (-0.11).""", blast="good"),
            row("Garrett Mitchell", "L", "+610", 76, "", ["vs Abbott"], """1 HR, 2 near-HR, 94.8 mph EV. Abbott LHB split +0.51, HR risk 0.03.""", blast="good"),
            row("Andrew Vaughn", "R", "+540", 58, "", ["vs Abbott"], """0 HR, 91.8 mph EV. Abbott RHB split -0.13, HR risk 0.03. slight split headwind (-0.13); limited recent HR events."""),
            row("Jackson Chourio", "R", "+343", 64, "", ["vs Abbott"], """1 HR, 1 near-HR, 88.8 mph EV. Abbott RHB split -0.13, HR risk 0.03. slight split headwind (-0.13).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ CWS - Taj Bradley (R, MIN) vs Anthony Kay (L, CWS)",
        "description": "Tail key data: Park boost +8% (stadium -5%, weather +14%). Bradley (HR risk 0.20, vs LHB +0.47, vs RHB -0.27). Kay (HR risk 0.33, vs LHB -1.22, vs RHB +0.97).",
        "rows": [
            row("Andrew Benintendi", "L", "+543", 72, "", ["vs Bradley"], """1 HR, 2 near-HR, 94.4 mph EV. Bradley LHB split +0.47, HR risk 0.20.""", blast="good"),
            row("Miguel Vargas", "R", "+404", 63, "", ["vs Bradley"], """1 HR, 1 near-HR, 92.7 mph EV. Bradley RHB split -0.27, HR risk 0.20. slight split headwind (-0.27).""", blast="good"),
            row("Colson Montgomery", "L", "+379", 62, "", ["vs Bradley"], """1 HR, 1 near-HR, 83.7 mph EV. Bradley LHB split +0.47, HR risk 0.20. lighter EV form (83.7 mph).""", blast="good"),
            row("Munetaka Murakami", "L", "+342", 70, "", ["vs Bradley"], """1 HR, 1 near-HR, 94.3 mph EV. Bradley LHB split +0.47, HR risk 0.20.""", blast="good"),
            row("Royce Lewis", "R", "+425", 64, "", ["vs Kay"], """0 HR, 1 near-HR, 91.1 mph EV. Kay RHB split +0.97, HR risk 0.33. limited recent HR events."""),
            row("Luke Keaschall", "R", "+870", 64, "", ["vs Kay"], """0 HR, 1 near-HR, 90.5 mph EV. Kay RHB split +0.97, HR risk 0.33. limited recent HR events."""),
        ],
    },
    {
        "title": "NYY @ SD - Carlos Rodon (L, NYY) vs Robbie Ray (L, SD)",
        "description": "Tail key data: Park boost -5% (stadium -3%, weather -2%). Rodon (HR risk -0.85, vs LHB -0.00, vs RHB -0.60). Ray (HR risk 0.30, vs LHB -1.01, vs RHB +0.97).",
        "rows": [
            row("Ty France", "R", "+560", 58, "🌕 💣", ["vs Rodon"], """2 HR, 2 near-HR, 91.6 mph EV. Rodon RHB split -0.60, HR risk -0.85. tough split lane (-0.60); pitcher suppresses HR (-0.85).""", blast="high"),
            row("Fernando Tatis Jr.", "R", "+400", 58, "🌕 💣", ["vs Rodon"], """2 HR, 2 near-HR, 87.6 mph EV. Rodon RHB split -0.60, HR risk -0.85. tough split lane (-0.60); pitcher suppresses HR (-0.85).""", blast="high"),
            row("Freddy Fermin", "R", "+900", 58, "", ["vs Rodon"], """0 HR, 94.1 mph EV. Rodon RHB split -0.60, HR risk -0.85. tough split lane (-0.60); pitcher suppresses HR (-0.85).""", blast="good"),
            row("Heliot Ramos", "R", "+475", 68, "💎", ["vs Ray"], """Worst Pickz Hidden Gem. 0 HR, 98.7 mph EV. Ray RHB split +0.97, HR risk 0.30. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
            row("Amed Rosario", "R", "+690", 60, "", ["vs Ray"], """0 HR, 91.6 mph EV. Ray RHB split +0.97, HR risk 0.30. park/weather net drag (-5%); limited recent HR events."""),
        ],
    },
    {
        "title": "STL @ COL - Matthew Liberatore 🧤 (L, STL) vs Mason Adams 🧤 (R, COL)",
        "description": "Tail key data: Park boost +25% (stadium +22%, weather +3%). Liberatore 🧤 (HR risk 1.14, vs LHB +0.37, vs RHB +1.08). Adams 🧤 (HR risk 1.75, vs LHB +0.82, vs RHB +1.50).",
        "rows": [
            row("TJ Rumfield", "L", "+880", 87, "", ["vs Liberatore"], """1 HR, 2 near-HR, 92.2 mph EV. Liberatore LHB split +0.37, HR risk 1.14.""", blast="good"),
            row("Jake McCarthy", "L", "+1040", 69, "", ["vs Liberatore"], """0 HR, 82.7 mph EV. Liberatore LHB split +0.37, HR risk 1.14. limited recent HR events; lighter EV form (82.7 mph)."""),
            row("Hunter Goodman", "R", "+300", 86, "", ["vs Liberatore"], """1 HR, 1 near-HR, 87.1 mph EV. Liberatore RHB split +1.08, HR risk 1.14. lighter EV form (87.1 mph).""", blast="good"),
            row("Jordan Walker", "R", "+390", 93, "⭐ 🌕 💣", ["vs Adams"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.5 mph EV. Adams RHB split +1.50, HR risk 1.75.""", blast="good"),
            row("Leonardo Bernal", "S", "+710", 92, "🚀 🌕 💣", ["vs Adams"], """1 HR, 1 near-HR, 102.4 mph EV. Adams SHB→LHB split +0.82, HR risk 1.75.""", blast="good"),
            row("Ivan Herrera", "R", "+600", 92, "🌕 💣", ["vs Adams"], """0 HR, 2 near-HR, 92.7 mph EV. Adams RHB split +1.50, HR risk 1.75.""", blast="good"),
            row("Alec Burleson", "L", "+390", 88, "🌕 💣", ["vs Adams"], """0 HR, 1 near-HR, 92.4 mph EV. Adams LHB split +0.82, HR risk 1.75. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TB @ TEX - Drew Rasmussen (R, TB) vs Jacob deGrom (R, TEX)",
        "description": "Tail key data: Park boost -10% (stadium -10%, weather +0%). Rasmussen (HR risk -1.21, vs LHB -0.74, vs RHB -0.60). deGrom (HR risk -0.60, vs LHB -0.06, vs RHB -0.62).",
        "rows": [
            row("Brandon Nimmo", "L", "+650", 58, "💎", ["vs Rasmussen"], """Worst Pickz Hidden Gem. 0 HR, 96.5 mph EV. Rasmussen LHB split -0.74, HR risk -1.21. tough split lane (-0.74); pitcher suppresses HR (-1.21).""", blast="good"),
            row("Joc Pederson", "L", "+506", 58, "", ["vs Rasmussen"], """1 HR, 2 near-HR, 94.4 mph EV. Rasmussen LHB split -0.74, HR risk -1.21. tough split lane (-0.74); pitcher suppresses HR (-1.21).""", blast="good"),
            row("Corey Seager", "L", "+405", 58, "", ["vs Rasmussen"], """0 HR, 96.9 mph EV. Rasmussen LHB split -0.74, HR risk -1.21. tough split lane (-0.74); pitcher suppresses HR (-1.21).""", blast="good"),
            row("Jonathan Aranda", "L", "+525", 58, "", ["vs deGrom"], """1 HR, 1 near-HR, 99.8 mph EV. deGrom LHB split -0.06, HR risk -0.60. slight split headwind (-0.06); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Junior Caminero", "R", "+353", 58, "⭐", ["vs deGrom"], """Worst Pickz Favorite. 0 HR, 95.1 mph EV. deGrom RHB split -0.62, HR risk -0.60. tough split lane (-0.62); pitcher suppresses HR (-0.60).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ KC - Max Scherzer (R, TOR) vs Seth Lugo (R, KC)",
        "description": "Tail key data: Park boost +8% (stadium +11%, weather -3%). Scherzer (HR risk 0.23, vs LHB -0.15, vs RHB +0.90). Lugo (HR risk -0.37, vs LHB +0.05, vs RHB -0.58).",
        "rows": [
            row("Carter Jensen", "L", "+370", 83, "🚀 🌕 💣", ["vs Scherzer"], """2 HR, 4 near-HR, 100.4 mph EV. Scherzer LHB split -0.15, HR risk 0.23. slight split headwind (-0.15).""", blast="high"),
            row("Salvador Perez", "R", "+445", 76, "💎", ["vs Scherzer"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 99.9 mph EV. Scherzer RHB split +0.90, HR risk 0.23.""", blast="good"),
            row("Jac Caglianone", "L", "+368", 58, "💎", ["vs Scherzer"], """Worst Pickz Hidden Gem. 0 HR, 92.1 mph EV. Scherzer LHB split -0.15, HR risk 0.23. slight split headwind (-0.15); limited recent HR events.""", blast="good"),
            row("George Springer", "R", "+480", 58, "💎", ["vs Lugo"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.4 mph EV. Lugo RHB split -0.58, HR risk -0.37. tough split lane (-0.58); pitcher risk below avg (-0.37).""", blast="good"),
            row("Alejandro Kirk", "R", "+690", 58, "", ["vs Lugo"], """0 HR, 96.0 mph EV. Lugo RHB split -0.58, HR risk -0.37. tough split lane (-0.58); pitcher risk below avg (-0.37).""", blast="good"),
            row("Vladimir Guerrero Jr.", "R", "+600", 58, "", ["vs Lugo"], """0 HR, 94.5 mph EV. Lugo RHB split -0.58, HR risk -0.37. tough split lane (-0.58); pitcher risk below avg (-0.37).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ LAD - Cade Cavalli (R, WSH) vs Tyler Glasnow (R, LAD)",
        "description": "Tail key data: Park boost +18% (stadium +17%, weather +2%). Cavalli (HR risk 0.24, vs LHB -0.24, vs RHB +0.77). Glasnow (HR risk -0.21, vs LHB -0.60, vs RHB +0.76).",
        "rows": [
            row("Mookie Betts", "R", "+590", 77, "⭐", ["vs Cavalli"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.5 mph EV. Cavalli RHB split +0.77, HR risk 0.24.""", blast="good"),
            row("Kyle Tucker", "L", "+570", 66, "💎", ["vs Cavalli"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.4 mph EV. Cavalli LHB split -0.24, HR risk 0.24. slight split headwind (-0.24).""", blast="good"),
            row("Dalton Rushing", "L", "+587", 69, "", ["vs Cavalli"], """1 HR, 2 near-HR, 94.7 mph EV. Cavalli LHB split -0.24, HR risk 0.24. slight split headwind (-0.24).""", blast="good"),
            row("Max Muncy", "L", "+410", 62, "⭐", ["vs Cavalli"], """Worst Pickz Favorite. 0 HR, 94.0 mph EV. Cavalli LHB split -0.24, HR risk 0.24. slight split headwind (-0.24); limited recent HR events.""", blast="good"),
            row("Teoscar Hernandez", "R", "+570", 72, "", ["vs Cavalli"], """0 HR, 96.4 mph EV. Cavalli RHB split +0.77, HR risk 0.24. limited recent HR events.""", blast="good"),
            row("Daylen Lile", "L", "+720", 72, "🚀 🌕 💣", ["vs Glasnow"], """2 HR, 2 near-HR, 100.1 mph EV. Glasnow LHB split -0.60, HR risk -0.21. tough split lane (-0.60); pitcher risk below avg (-0.21).""", blast="high"),
            row("Brady House", "R", "+970", 73, "🚀", ["vs Glasnow"], """1 HR, 1 near-HR, 100.6 mph EV. Glasnow RHB split +0.76, HR risk -0.21. pitcher risk below avg (-0.21).""", blast="good"),
            row("Andres Chaparro", "R", "+390", 59, "", ["vs Glasnow"], """0 HR, 1 near-HR, 90.0 mph EV. Glasnow RHB split +0.76, HR risk -0.21. pitcher risk below avg (-0.21); limited recent HR events."""),
            row("Dylan Crews", "R", "+640", 67, "", ["vs Glasnow"], """0 HR, 94.9 mph EV. Glasnow RHB split +0.76, HR risk -0.21. pitcher risk below avg (-0.21); limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-05")

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

    out = ROOT / '_games-0905.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
