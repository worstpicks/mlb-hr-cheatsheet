#!/usr/bin/env python3
"""Generate games[] block for 2026-08-22 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Adley Rutschman (S)",
    "Brett Baty (L)",
    "Cam Smith (R)",
    "Coby Mayo (R)",
    "Colt Keith (L)",
    "Fernando Tatis Jr. (R)",
    "Gabriel Moreno (R)",
    "Jackson Merrill (L)",
    "Jazz Chisholm Jr. (L)",
    "Jo Adell (R)",
    "Joc Pederson (L)",
    "Josh Bell (S)",
    "Junior Caminero (R)",
    "Kazuma Okamoto (R)",
    "Luis Garcia Jr. (L)",
    "Matt Olson (L)",
    "Max Muncy (L)",
    "Michael Conforto (L)",
    "Michael Harris II (L)",
    "Mickey Gasper (S)",
    "Mickey Moniak (L)",
    "Munetaka Murakami (L)",
    "William Contreras (R)",
    "Wyatt Langford (R)",
    "Yordan Alvarez (L)",
    "Zach Neto (R)",
}

GEMS = {
    "Bryce Eldridge (L)",
    "Christian Encarnacion Strand (R)",
    "Christian Walker (R)",
    "Daz Cameron (R)",
    "Hunter Feduccia (L)",
    "Jimmy Crooks (L)",
    "Joshua Baez (R)",
    "Kody Clemens (L)",
    "Manny Machado (R)",
    "Oneil Cruz (L)",
    "Spencer Torkelson (R)",
    "Tim Tawa (R)",
    "Trent Grisham (L)",
    "Willi Castro (S)",
    "Xander Bogaerts (R)",
}

PLAYER_TEAMS = {
    "Abimelec Ortiz (L)": "WSH",
    "Adley Rutschman (S)": "BOS",
    "Alec Bohm (R)": "PHI",
    "Alejandro Kirk (R)": "TOR",
    "Alex Bregman (R)": "CHC",
    "Andres Chaparro (R)": "WSH",
    "Andrew Benintendi (L)": "CWS",
    "Angel Genao (S)": "CLE",
    "Ben Malgeri (R)": "DET",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Nimmo (L)": "TEX",
    "Brett Baty (L)": "NYM",
    "Brock Rodden (S)": "SEA",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Cal Raleigh (S)": "SEA",
    "Cam Smith (R)": "HOU",
    "Carson Benge (L)": "NYM",
    "Carter Jensen (L)": "KC",
    "Christian Encarnacion Strand (R)": "BAL",
    "Christian Walker (R)": "HOU",
    "Coby Mayo (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Colt Keith (L)": "DET",
    "Corbin Carroll (L)": "ARI",
    "Daz Cameron (R)": "TOR",
    "Donovan Walton (L)": "ATH",
    "Dylan Crews (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Lindor (S)": "NYM",
    "Gabriel Moreno (R)": "ARI",
    "Garrett Mitchell (L)": "MIL",
    "Griffin Conine (L)": "MIA",
    "Harry Ford (R)": "WSH",
    "Hunter Feduccia (L)": "LAD",
    "Ildemaro Vargas (S)": "ARI",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "CLE",
    "Joc Pederson (L)": "TEX",
    "Joey Ortiz (R)": "MIL",
    "Jonathan Aranda (L)": "TB",
    "Jordan Beck (R)": "COL",
    "Jordan Walker (R)": "STL",
    "Jose Siri (R)": "LAA",
    "Josh Bell (S)": "MIN",
    "Joshua Baez (R)": "STL",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kevin Alcantara (R)": "CHC",
    "Kody Clemens (L)": "MIN",
    "Kyle Isbel (L)": "KC",
    "Kyle Schwarber (L)": "PHI",
    "Lars Nootbaar (L)": "ARI",
    "Luis Campusano (R)": "SD",
    "Luis Garcia Jr. (L)": "NYY",
    "Manny Machado (R)": "SD",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Max Muncy (R)": "ATH",
    "Michael Busch (L)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Mickey Gasper (S)": "BOS",
    "Mickey Moniak (L)": "COL",
    "Miguel Amaya (R)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Moises Ballesteros (L)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Nick Gonzales (R)": "PIT",
    "Oneil Cruz (L)": "PIT",
    "Owen Caissie (L)": "MIA",
    "Pete Crow Armstrong (L)": "CHC",
    "Randal Grichuk (R)": "CWS",
    "Ryan Jeffers (R)": "MIN",
    "Ryan Vilade (R)": "TB",
    "Samuel Basallo (L)": "BAL",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Trent Grisham (L)": "NYY",
    "Trevor Larnach (L)": "MIN",
    "Tyler Stephenson (R)": "CIN",
    "Vinnie Pasquantino (L)": "KC",
    "Willi Castro (S)": "COL",
    "William Contreras (R)": "MIL",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Xander Bogaerts (R)": "SD",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("LAA @ TEX", "Johnson"),
    ("NYM @ CWS", "Castillo"),
    ("PIT @ LAD", "Jones"),
    ("WSH @ MIA", "Irvin"),
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
        "title": "ATH @ HOU - Jacob Lopez (L, ATH) vs Hunter Brown (R, HOU)",
        "description": "Tail key data: Park boost +4% (stadium +4%, weather -1%). Lopez (HR risk -0.16, vs LHB -1.15, vs RHB +0.17). Brown (HR risk -0.18, vs LHB +0.44, vs RHB -0.83).",
        "rows": [
            row("Cam Smith", "R", "+500", 58, "⭐", ["vs Lopez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 87.8 mph EV. Lopez RHB split +0.17, HR risk -0.16. pitcher risk below avg (-0.16); lighter EV form (87.8 mph).""", blast="good"),
            row("Yordan Alvarez", "L", "+289", 58, "⭐", ["vs Lopez"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 90.2 mph EV. Lopez LHB split -1.15, HR risk -0.16. tough split lane (-1.15); pitcher risk below avg (-0.16)."""),
            row("Christian Walker", "R", "+403", 58, "💎", ["vs Lopez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 85.7 mph EV. Lopez RHB split +0.17, HR risk -0.16. pitcher risk below avg (-0.16); lighter EV form (85.7 mph).""", blast="good"),
            row("Max Muncy", "R", "+860", 60, "", ["vs Brown"], """1 HR, 3 near-HR, 90.8 mph EV. Brown RHB split -0.83, HR risk -0.18. tough split lane (-0.83); pitcher risk below avg (-0.18).""", blast="good"),
            row("Donovan Walton", "L", "+920", 58, "", ["vs Brown"], """0 HR, 1 near-HR, 91.4 mph EV. Brown LHB split +0.44, HR risk -0.18. pitcher risk below avg (-0.18); limited recent HR events."""),
        ],
    },
    {
        "title": "ATL @ MIL - Martin Perez (L, ATL) vs Logan Henderson (R, MIL)",
        "description": "Tail key data: Park boost +5% (stadium -2%, weather +7%). Perez (HR risk -0.97, vs LHB -0.52, vs RHB -0.66). Henderson (HR risk 0.78, vs LHB +0.99, vs RHB -0.30).",
        "rows": [
            row("William Contreras", "R", "+600", 58, "⭐", ["vs Martin Perez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.1 mph EV. Martin Perez RHB split -0.66, HR risk -0.97. tough split lane (-0.66); pitcher suppresses HR (-0.97).""", blast="good"),
            row("Jackson Chourio", "R", "+466", 58, "", ["vs Martin Perez"], """0 HR, 96.8 mph EV. Martin Perez RHB split -0.66, HR risk -0.97. tough split lane (-0.66); pitcher suppresses HR (-0.97).""", blast="good"),
            row("Joey Ortiz", "R", "+1000", 58, "", ["vs Martin Perez"], """1 HR, 1 near-HR, 82.4 mph EV. Martin Perez RHB split -0.66, HR risk -0.97. tough split lane (-0.66); pitcher suppresses HR (-0.97).""", blast="good"),
            row("Garrett Mitchell", "L", "N/A", 58, "", ["vs Martin Perez"], """0 HR, 88.7 mph EV. Martin Perez LHB split -0.52, HR risk -0.97. tough split lane (-0.52); pitcher suppresses HR (-0.97)."""),
            row("Michael Harris II", "L", "+370", 78, "⭐", ["vs Henderson"], """Worst Pickz Favorite. 0 HR, 98.2 mph EV. Henderson LHB split +0.99, HR risk 0.78. limited recent HR events.""", blast="good"),
            row("Matt Olson", "L", "+258", 84, "⭐", ["vs Henderson"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 90.2 mph EV. Henderson LHB split +0.99, HR risk 0.78.""", blast="good"),
        ],
    },
    {
        "title": "CHC @ SEA - David Peterson (L, CHC) vs Kade Anderson (L, SEA)",
        "description": "Tail key data: Park boost +5% (stadium +0%, weather +5%). Peterson (HR risk -0.76, vs LHB +0.02, vs RHB -0.74). Anderson (HR risk 0.24, vs LHB +0.29, vs RHB -0.06).",
        "rows": [
            row("Cal Raleigh", "S", "+368", 67, "🌕 💣", ["vs Peterson"], """2 HR, 2 near-HR, 94.1 mph EV. Peterson SHB→LHB split +0.02, HR risk -0.76. pitcher suppresses HR (-0.76).""", blast="high"),
            row("Julio Rodriguez", "R", "+545", 58, "", ["vs Peterson"], """0 HR, 1 near-HR, 90.6 mph EV. Peterson RHB split -0.74, HR risk -0.76. tough split lane (-0.74); pitcher suppresses HR (-0.76)."""),
            row("Brock Rodden", "S", "N/A", 58, "", ["vs Peterson"], """0 HR, 2 near-HR, 94.2 mph EV. Peterson SHB→LHB split +0.02, HR risk -0.76. pitcher suppresses HR (-0.76).""", blast="good"),
            row("Pete Crow Armstrong", "L", "N/A", 86, "🌕 💣", ["vs Kade Anderson"], """4 HR, 4 near-HR, 94.3 mph EV. Kade Anderson LHB split +0.29, HR risk 0.24.""", blast="high"),
            row("Miguel Amaya", "R", "N/A", 68, "", ["vs Kade Anderson"], """1 HR, 2 near-HR, 94.7 mph EV. Kade Anderson RHB split -0.06, HR risk 0.24. slight split headwind (-0.06).""", blast="good"),
            row("Alex Bregman", "R", "N/A", 61, "", ["vs Kade Anderson"], """1 HR, 1 near-HR, 89.5 mph EV. Kade Anderson RHB split -0.06, HR risk 0.24. slight split headwind (-0.06).""", blast="good"),
            row("Michael Conforto", "L", "N/A", 67, "⭐", ["vs Kade Anderson"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 91.5 mph EV. Kade Anderson LHB split +0.29, HR risk 0.24.""", blast="good"),
            row("Kevin Alcantara", "R", "N/A", 62, "", ["vs Kade Anderson"], """0 HR, 98.5 mph EV. Kade Anderson RHB split -0.06, HR risk 0.24. slight split headwind (-0.06); limited recent HR events.""", blast="good"),
            row("Michael Busch", "L", "N/A", 63, "", ["vs Kade Anderson"], """0 HR, 2 near-HR, 91.0 mph EV. Kade Anderson LHB split +0.29, HR risk 0.24.""", blast="good"),
        ],
    },
    {
        "title": "CIN @ ARI - Rhett Lowder (R, CIN) vs Michael Soroka (R, ARI)",
        "description": "Tail key data: Park boost -9% (stadium -9%, weather +0%). Lowder (HR risk 0.24, vs LHB +0.56, vs RHB -0.51). Soroka (HR risk -0.74, vs LHB -0.80, vs RHB -0.09).",
        "rows": [
            row("Ildemaro Vargas", "S", "+1400", 63, "", ["vs Lowder"], """1 HR, 1 near-HR, 90.6 mph EV. Lowder SHB→LHB split +0.56, HR risk 0.24. park/weather net drag (-9%).""", blast="good"),
            row("Lars Nootbaar", "L", "+770", 69, "", ["vs Lowder"], """1 HR, 2 near-HR, 94.9 mph EV. Lowder LHB split +0.56, HR risk 0.24. park/weather net drag (-9%).""", blast="good"),
            row("Corbin Carroll", "L", "+464", 67, "", ["vs Lowder"], """1 HR, 1 near-HR, 94.0 mph EV. Lowder LHB split +0.56, HR risk 0.24. park/weather net drag (-9%).""", blast="good"),
            row("Gabriel Moreno", "R", "+840", 60, "⭐", ["vs Lowder"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.3 mph EV. Lowder RHB split -0.51, HR risk 0.24. tough split lane (-0.51); park/weather net drag (-9%).""", blast="good"),
            row("Tim Tawa", "R", "+760", 58, "💎", ["vs Lowder"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 94.2 mph EV. Lowder RHB split -0.51, HR risk 0.24. tough split lane (-0.51); park/weather net drag (-9%).""", blast="good"),
            row("Matt McLain", "R", "+900", 58, "", ["vs Soroka"], """1 HR, 1 near-HR, 93.9 mph EV. Soroka RHB split -0.09, HR risk -0.74. slight split headwind (-0.09); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Tyler Stephenson", "R", "+790", 58, "", ["vs Soroka"], """1 HR, 1 near-HR, 94.1 mph EV. Soroka RHB split -0.09, HR risk -0.74. slight split headwind (-0.09); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Eugenio Suarez", "R", "+500", 58, "", ["vs Soroka"], """0 HR, 92.5 mph EV. Soroka RHB split -0.09, HR risk -0.74. slight split headwind (-0.09); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Elly De La Cruz", "S", "+481", 58, "", ["vs Soroka"], """0 HR, 94.5 mph EV. Soroka SHB→RHB split -0.09, HR risk -0.74. slight split headwind (-0.09); pitcher suppresses HR (-0.74).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ COL - Tanner Bibee (R, CLE) vs Gabriel Hughes (R, COL)",
        "description": "Tail key data: Park boost +18% (stadium +19%, weather -1%). Bibee (HR risk 0.28, vs LHB +1.01, vs RHB -0.70). Hughes (HR risk -0.85, vs LHB -0.64, vs RHB -0.52).",
        "rows": [
            row("Willi Castro", "S", "+370", 74, "💎", ["vs Bibee"], """Worst Pickz Hidden Gem. 0 HR, 99.6 mph EV. Bibee SHB→LHB split +1.01, HR risk 0.28. limited recent HR events.""", blast="good"),
            row("Jordan Beck", "R", "N/A", 58, "", ["vs Bibee"], """0 HR, 1 near-HR, 90.6 mph EV. Bibee RHB split -0.70, HR risk 0.28. tough split lane (-0.70); limited recent HR events."""),
            row("Mickey Moniak", "L", "+340", 66, "⭐", ["vs Bibee"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 90.7 mph EV. Bibee LHB split +1.01, HR risk 0.28. limited recent HR events."""),
            row("Jo Adell", "R", "+320", 58, "⭐", ["vs Hughes"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 91.7 mph EV. Hughes RHB split -0.52, HR risk -0.85. tough split lane (-0.52); pitcher suppresses HR (-0.85).""", blast="good"),
            row("Angel Genao", "S", "+560", 58, "", ["vs Hughes"], """0 HR, 93.8 mph EV. Hughes SHB→RHB split -0.52, HR risk -0.85. tough split lane (-0.52); pitcher suppresses HR (-0.85).""", blast="good"),
        ],
    },
    {
        "title": "DET @ KC - Drew Anderson (R, DET) vs Michael Wacha (R, KC)",
        "description": "Tail key data: Park boost +11% (stadium +10%, weather +0%). Anderson (HR risk 0.24, vs LHB +0.29, vs RHB -0.06). Wacha (HR risk 0.44, vs LHB -0.56, vs RHB +1.26).",
        "rows": [
            row("Vinnie Pasquantino", "L", "+800", 68, "", ["vs Drew Anderson"], """0 HR, 1 near-HR, 96.3 mph EV. Drew Anderson LHB split +0.29, HR risk 0.24. limited recent HR events.""", blast="good"),
            row("Carter Jensen", "L", "+587", 72, "", ["vs Drew Anderson"], """1 HR, 3 near-HR, 90.0 mph EV. Drew Anderson LHB split +0.29, HR risk 0.24.""", blast="good"),
            row("Bobby Witt Jr.", "R", "+531", 69, "", ["vs Drew Anderson"], """1 HR, 3 near-HR, 89.6 mph EV. Drew Anderson RHB split -0.06, HR risk 0.24. slight split headwind (-0.06).""", blast="good"),
            row("Kyle Isbel", "L", "+1480", 65, "", ["vs Drew Anderson"], """1 HR, 1 near-HR, 89.6 mph EV. Drew Anderson LHB split +0.29, HR risk 0.24.""", blast="good"),
            row("Jac Caglianone", "L", "+630", 69, "", ["vs Drew Anderson"], """0 HR, 2 near-HR, 96.0 mph EV. Drew Anderson LHB split +0.29, HR risk 0.24.""", blast="good"),
            row("Spencer Torkelson", "R", "+419", 77, "💎", ["vs Wacha"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.0 mph EV. Wacha RHB split +1.26, HR risk 0.44. limited recent HR events.""", blast="good"),
            row("Colt Keith", "L", "+720", 58, "⭐", ["vs Wacha"], """Worst Pickz Favorite. 0 HR, 90.5 mph EV. Wacha LHB split -0.56, HR risk 0.44. tough split lane (-0.56); limited recent HR events."""),
            row("Ben Malgeri", "R", "N/A", 94, "🌕 💣", ["vs Wacha"], """3 HR, 3 near-HR, 95.0 mph EV. Wacha RHB split +1.26, HR risk 0.44.""", blast="high"),
        ],
    },
    {
        "title": "LAA @ TEX - Ryan Johnson 🧤 (R, LAA) vs Cody Bradford (L, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -10%, weather -1%). Johnson 🧤 (HR risk 2.02, vs LHB +1.87, vs RHB +0.82). Bradford (HR risk -0.25, vs LHB +0.59, vs RHB -0.51).",
        "rows": [
            row("Joc Pederson", "L", "+430", 99, "🚀 ⭐ 🌕 💣", ["vs Johnson"], """Worst Pickz Favorite. 4 HR, 4 near-HR, 103.2 mph EV. Johnson LHB split +1.87, HR risk 2.02. park/weather net drag (-11%).""", blast="high"),
            row("Brandon Nimmo", "L", "+404", 92, "🌕 💣", ["vs Johnson"], """1 HR, 2 near-HR, 98.0 mph EV. Johnson LHB split +1.87, HR risk 2.02. park/weather net drag (-11%).""", blast="good"),
            row("Wyatt Langford", "R", "+426", 81, "⭐", ["vs Johnson"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 90.5 mph EV. Johnson RHB split +0.82, HR risk 2.02. park/weather net drag (-11%).""", blast="good"),
            row("Moises Ballesteros", "L", "+680", 58, "", ["vs Bradford"], """0 HR, 92.2 mph EV. Bradford LHB split +0.59, HR risk -0.25. pitcher risk below avg (-0.25); park/weather net drag (-11%).""", blast="good"),
            row("Zach Neto", "R", "+419", 58, "⭐", ["vs Bradford"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.6 mph EV. Bradford RHB split -0.51, HR risk -0.25. tough split lane (-0.51); pitcher risk below avg (-0.25).""", blast="good"),
            row("Jose Siri", "R", "+450", 58, "", ["vs Bradford"], """1 HR, 1 near-HR, 91.0 mph EV. Bradford RHB split -0.51, HR risk -0.25. tough split lane (-0.51); pitcher risk below avg (-0.25).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ SD - Dean Kremer (R, MIN) vs Casey Mize (R, SD)",
        "description": "Tail key data: Park boost +2% (stadium -4%, weather +6%). Kremer (HR risk 0.38, vs LHB -0.60, vs RHB +1.24). Mize (HR risk -0.09, vs LHB -0.53, vs RHB +0.42).",
        "rows": [
            row("Fernando Tatis Jr.", "R", "+403", 84, "🚀 ⭐", ["vs Kremer"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 100.7 mph EV. Kremer RHB split +1.24, HR risk 0.38.""", blast="good"),
            row("Xander Bogaerts", "R", "+820", 72, "💎", ["vs Kremer"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.7 mph EV. Kremer RHB split +1.24, HR risk 0.38. limited recent HR events.""", blast="good"),
            row("Manny Machado", "R", "+436", 77, "💎", ["vs Kremer"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.8 mph EV. Kremer RHB split +1.24, HR risk 0.38.""", blast="good"),
            row("Luis Campusano", "R", "+600", 69, "", ["vs Kremer"], """0 HR, 2 near-HR, 89.2 mph EV. Kremer RHB split +1.24, HR risk 0.38.""", blast="good"),
            row("Jackson Merrill", "L", "+560", 58, "⭐", ["vs Kremer"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 92.5 mph EV. Kremer LHB split -0.60, HR risk 0.38. tough split lane (-0.60); limited recent HR events.""", blast="good"),
            row("Josh Bell", "S", "+499", 66, "⭐", ["vs Mize"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.2 mph EV. Mize SHB→RHB split +0.42, HR risk -0.09. pitcher risk below avg (-0.09).""", blast="good"),
            row("Kody Clemens", "L", "+400", 58, "💎", ["vs Mize"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 92.3 mph EV. Mize LHB split -0.53, HR risk -0.09. tough split lane (-0.53); pitcher risk below avg (-0.09).""", blast="good"),
            row("Trevor Larnach", "L", "+790", 58, "", ["vs Mize"], """0 HR, 91.6 mph EV. Mize LHB split -0.53, HR risk -0.09. tough split lane (-0.53); pitcher risk below avg (-0.09)."""),
            row("Ryan Jeffers", "R", "+540", 58, "", ["vs Mize"], """0 HR, 2 near-HR, 80.8 mph EV. Mize RHB split +0.42, HR risk -0.09. pitcher risk below avg (-0.09); lighter EV form (80.8 mph).""", blast="good"),
        ],
    },
    {
        "title": "NYM @ CWS - Christian Scott (R, NYM) vs Luis Castillo 🧤 (R, CWS)",
        "description": "Tail key data: Park boost +7% (stadium -5%, weather +13%). Scott (HR risk -0.89, vs LHB -0.51, vs RHB -0.63). Castillo 🧤 (HR risk 1.05, vs LHB +0.95, vs RHB +0.39).",
        "rows": [
            row("Munetaka Murakami", "L", "+272", 64, "⭐ 🌕 💣", ["vs Scott"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.4 mph EV. Scott LHB split -0.51, HR risk -0.89. tough split lane (-0.51); pitcher suppresses HR (-0.89).""", blast="high"),
            row("Miguel Vargas", "R", "+364", 60, "🌕 💣", ["vs Scott"], """2 HR, 2 near-HR, 93.2 mph EV. Scott RHB split -0.63, HR risk -0.89. tough split lane (-0.63); pitcher suppresses HR (-0.89).""", blast="high"),
            row("Randal Grichuk", "R", "N/A", 58, "", ["vs Scott"], """1 HR, 1 near-HR, 89.9 mph EV. Scott RHB split -0.63, HR risk -0.89. tough split lane (-0.63); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Colson Montgomery", "L", "+350", 58, "", ["vs Scott"], """1 HR, 2 near-HR, 92.4 mph EV. Scott LHB split -0.51, HR risk -0.89. tough split lane (-0.51); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Andrew Benintendi", "L", "+549", 58, "", ["vs Scott"], """1 HR, 1 near-HR, 91.9 mph EV. Scott LHB split -0.51, HR risk -0.89. tough split lane (-0.51); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Brett Baty", "L", "+475", 92, "🚀 ⭐ 🌕 💣", ["vs Castillo"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 100.6 mph EV. Castillo LHB split +0.95, HR risk 1.05.""", blast="good"),
            row("Francisco Lindor", "S", "+319", 80, "", ["vs Castillo"], """0 HR, 93.2 mph EV. Castillo SHB→LHB split +0.95, HR risk 1.05. limited recent HR events.""", blast="good"),
            row("Carson Benge", "L", "+500", 84, "", ["vs Castillo"], """1 HR, 1 near-HR, 91.7 mph EV. Castillo LHB split +0.95, HR risk 1.05.""", blast="good"),
        ],
    },
    {
        "title": "PIT @ LAD - Jared Jones 🧤 (R, PIT) vs Tarik Skubal (L, LAD)",
        "description": "Tail key data: Park boost +25% (stadium +18%, weather +7%). Jones 🧤 (HR risk 1.15, vs LHB +0.21, vs RHB +1.39). Skubal (HR risk -0.30, vs LHB -0.16, vs RHB -0.14).",
        "rows": [
            row("Max Muncy", "L", "+350", 93, "⭐ 🌕 💣", ["vs Jones"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.0 mph EV. Jones LHB split +0.21, HR risk 1.15.""", blast="high"),
            row("Shohei Ohtani", "L", "+240", 82, "", ["vs Jones"], """0 HR, 98.0 mph EV. Jones LHB split +0.21, HR risk 1.15. limited recent HR events.""", blast="good"),
            row("Hunter Feduccia", "L", "+1100", 82, "💎", ["vs Jones"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.4 mph EV. Jones LHB split +0.21, HR risk 1.15.""", blast="good"),
            row("Teoscar Hernandez", "R", "+440", 90, "🌕 💣", ["vs Jones"], """0 HR, 1 near-HR, 92.8 mph EV. Jones RHB split +1.39, HR risk 1.15. limited recent HR events.""", blast="good"),
            row("Oneil Cruz", "L", "+547", 63, "🚀 💎", ["vs Skubal"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 100.8 mph EV. Skubal LHB split -0.16, HR risk -0.30. slight split headwind (-0.16); pitcher risk below avg (-0.30).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+488", 63, "", ["vs Skubal"], """0 HR, 2 near-HR, 94.8 mph EV. Skubal RHB split -0.14, HR risk -0.30. slight split headwind (-0.14); pitcher risk below avg (-0.30).""", blast="good"),
            row("Bryan Reynolds", "S", "+529", 63, "", ["vs Skubal"], """0 HR, 1 near-HR, 98.2 mph EV. Skubal SHB→RHB split -0.14, HR risk -0.30. slight split headwind (-0.14); pitcher risk below avg (-0.30).""", blast="good"),
            row("Nick Gonzales", "R", "+940", 58, "", ["vs Skubal"], """0 HR, 88.4 mph EV. Skubal RHB split -0.14, HR risk -0.30. slight split headwind (-0.14); pitcher risk below avg (-0.30)."""),
        ],
    },
    {
        "title": "SF @ BOS - Blade Tidwell (R, SF) vs Patrick Sandoval (L, BOS)",
        "description": "Tail key data: Park boost -12% (stadium -8%, weather -4%). Tidwell (HR risk -0.62, vs LHB +0.12, vs RHB -1.00). Sandoval (HR risk -0.84, vs LHB +0.91, vs RHB -0.87).",
        "rows": [
            row("Wilyer Abreu", "L", "+430", 58, "", ["vs Tidwell"], """1 HR, 2 near-HR, 90.9 mph EV. Tidwell LHB split +0.12, HR risk -0.62. pitcher suppresses HR (-0.62); park/weather net drag (-12%).""", blast="good"),
            row("Adley Rutschman", "S", "+800", 58, "⭐", ["vs Tidwell"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 89.8 mph EV. Tidwell SHB→LHB split +0.12, HR risk -0.62. pitcher suppresses HR (-0.62); park/weather net drag (-12%).""", blast="good"),
            row("Mickey Gasper", "S", "+870", 67, "⭐ 🌕 💣", ["vs Tidwell"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 88.4 mph EV. Tidwell SHB→LHB split +0.12, HR risk -0.62. pitcher suppresses HR (-0.62); park/weather net drag (-12%).""", blast="high"),
            row("Bryce Eldridge", "L", "+720", 58, "💎", ["vs Sandoval"], """Worst Pickz Hidden Gem. 0 HR, 92.8 mph EV. Sandoval LHB split +0.91, HR risk -0.84. pitcher suppresses HR (-0.84); park/weather net drag (-12%).""", blast="good"),
            row("Willy Adames", "R", "+591", 58, "", ["vs Sandoval"], """0 HR, 89.9 mph EV. Sandoval RHB split -0.87, HR risk -0.84. tough split lane (-0.87); pitcher suppresses HR (-0.84)."""),
        ],
    },
    {
        "title": "STL @ PHI - Quinn Mathews (L, STL) vs Andrew Painter (R, PHI)",
        "description": "Tail key data: Park boost +0% (stadium +14%, weather -14%). Mathews (BAA vs LHB .333, vs RHB .294). Painter (HR risk 0.78, vs LHB +0.94, vs RHB +0.01).",
        "rows": [
            row("Jimmy Crooks", "L", "N/A", 80, "💎", ["vs Painter"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 92.9 mph EV. Painter LHB split +0.94, HR risk 0.78. weather carry headwind (-14%).""", blast="good"),
            row("JJ Wetherholt", "L", "+531", 77, "", ["vs Painter"], """0 HR, 96.0 mph EV. Painter LHB split +0.94, HR risk 0.78. weather carry headwind (-14%); limited recent HR events.""", blast="good"),
            row("Joshua Baez", "R", "+700", 67, "💎", ["vs Painter"], """Worst Pickz Hidden Gem. 0 HR, 94.0 mph EV. Painter RHB split +0.01, HR risk 0.78. weather carry headwind (-14%); limited recent HR events.""", blast="good"),
            row("Jordan Walker", "R", "+350", 76, "🌕 💣", ["vs Painter"], """2 HR, 2 near-HR, 87.7 mph EV. Painter RHB split +0.01, HR risk 0.78. weather carry headwind (-14%); lighter EV form (87.7 mph).""", blast="high"),
            row("Kyle Schwarber", "L", "N/A", 58, "", ["vs Mathews"], """0 HR, 1 near-HR, 89.9 mph EV. limited split/risk sample; weather carry headwind (-14%)."""),
            row("Alec Bohm", "R", "N/A", 60, "", ["vs Mathews"], """0 HR, 95.4 mph EV. limited split/risk sample; weather carry headwind (-14%).""", blast="good"),
        ],
    },
    {
        "title": "TB @ BAL - Shane McClanahan (L, TB) vs Brandon Young (R, BAL)",
        "description": "Tail key data: Park boost -5% (stadium -4%, weather -2%). McClanahan (HR risk -0.30, vs LHB -0.60, vs RHB +0.02). Young (HR risk 0.69, vs LHB -0.84, vs RHB +2.00).",
        "rows": [
            row("Coby Mayo", "R", "+461", 78, "⭐ 🌕 💣", ["vs McClanahan"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 97.8 mph EV. McClanahan RHB split +0.02, HR risk -0.30. pitcher risk below avg (-0.30); park/weather net drag (-5%).""", blast="high"),
            row("Christian Encarnacion Strand", "R", "+540", 62, "💎", ["vs McClanahan"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 99.0 mph EV. McClanahan RHB split +0.02, HR risk -0.30. pitcher risk below avg (-0.30); park/weather net drag (-5%).""", blast="good"),
            row("Samuel Basallo", "L", "+640", 58, "", ["vs McClanahan"], """1 HR, 1 near-HR, 91.0 mph EV. McClanahan LHB split -0.60, HR risk -0.30. tough split lane (-0.60); pitcher risk below avg (-0.30).""", blast="good"),
            row("Junior Caminero", "R", "+345", 83, "⭐", ["vs Young"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 97.2 mph EV. Young RHB split +2.00, HR risk 0.69. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
            row("Yandy Diaz", "R", "+586", 90, "🌕 💣", ["vs Young"], """2 HR, 2 near-HR, 89.1 mph EV. Young RHB split +2.00, HR risk 0.69. park/weather net drag (-5%).""", blast="high"),
            row("Ryan Vilade", "R", "+800", 77, "", ["vs Young"], """1 HR, 1 near-HR, 81.4 mph EV. Young RHB split +2.00, HR risk 0.69. park/weather net drag (-5%); lighter EV form (81.4 mph).""", blast="good"),
            row("Jonathan Aranda", "L", "+485", 61, "", ["vs Young"], """0 HR, 2 near-HR, 91.7 mph EV. Young LHB split -0.84, HR risk 0.69. tough split lane (-0.84); park/weather net drag (-5%).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ NYY - Dylan Cease (R, TOR) vs Ryan Weathers (L, NYY)",
        "description": "Tail key data: Park boost +2% (stadium +6%, weather -4%). Cease (HR risk -0.91, vs LHB -0.74, vs RHB -0.60). Weathers (HR risk -0.58, vs LHB -0.90, vs RHB -0.17).",
        "rows": [
            row("Ben Rice", "L", "+420", 61, "🌕 💣", ["vs Cease"], """2 HR, 2 near-HR, 95.8 mph EV. Cease LHB split -0.74, HR risk -0.91. tough split lane (-0.74); pitcher suppresses HR (-0.91).""", blast="high"),
            row("Trent Grisham", "L", "+470", 60, "🌕 💣 💎", ["vs Cease"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.8 mph EV. Cease LHB split -0.74, HR risk -0.91. tough split lane (-0.74); pitcher suppresses HR (-0.91).""", blast="high"),
            row("Luis Garcia Jr.", "L", "+520", 58, "⭐", ["vs Cease"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.7 mph EV. Cease LHB split -0.74, HR risk -0.91. tough split lane (-0.74); pitcher suppresses HR (-0.91).""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "+560", 58, "⭐", ["vs Cease"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.4 mph EV. Cease LHB split -0.74, HR risk -0.91. tough split lane (-0.74); pitcher suppresses HR (-0.91).""", blast="good"),
            row("Spencer Jones", "L", "+750", 58, "", ["vs Cease"], """0 HR, 97.1 mph EV. Cease LHB split -0.74, HR risk -0.91. tough split lane (-0.74); pitcher suppresses HR (-0.91).""", blast="good"),
            row("Kazuma Okamoto", "R", "+491", 58, "⭐", ["vs Weathers"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.2 mph EV. Weathers RHB split -0.17, HR risk -0.58. slight split headwind (-0.17); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Daz Cameron", "R", "N/A", 58, "💎", ["vs Weathers"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.4 mph EV. Weathers RHB split -0.17, HR risk -0.58. slight split headwind (-0.17); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Alejandro Kirk", "R", "+800", 58, "", ["vs Weathers"], """0 HR, 90.6 mph EV. Weathers RHB split -0.17, HR risk -0.58. slight split headwind (-0.17); pitcher suppresses HR (-0.58)."""),
        ],
    },
    {
        "title": "WSH @ MIA - Jake Irvin 🧤 (R, WSH) vs Eury Perez (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -13%, weather -1%). Irvin 🧤 (HR risk 1.19, vs LHB +0.91, vs RHB +0.57). Perez (HR risk -0.77, vs LHB -0.92, vs RHB -0.23).",
        "rows": [
            row("Griffin Conine", "L", "+380", 93, "🌕 💣", ["vs Irvin"], """2 HR, 3 near-HR, 99.9 mph EV. Irvin LHB split +0.91, HR risk 1.19. park/weather net drag (-13%).""", blast="high"),
            row("Owen Caissie", "L", "+465", 76, "", ["vs Irvin"], """1 HR, 1 near-HR, 87.6 mph EV. Irvin LHB split +0.91, HR risk 1.19. park/weather net drag (-13%); lighter EV form (87.6 mph).""", blast="good"),
            row("Andres Chaparro", "R", "+394", 58, "", ["vs Eury Perez"], """1 HR, 1 near-HR, 94.5 mph EV. Eury Perez RHB split -0.23, HR risk -0.77. slight split headwind (-0.23); pitcher suppresses HR (-0.77).""", blast="good"),
            row("Dylan Crews", "R", "+610", 58, "", ["vs Eury Perez"], """0 HR, 1 near-HR, 92.8 mph EV. Eury Perez RHB split -0.23, HR risk -0.77. slight split headwind (-0.23); pitcher suppresses HR (-0.77).""", blast="good"),
            row("Abimelec Ortiz", "L", "+500", 58, "", ["vs Eury Perez"], """1 HR, 1 near-HR, 93.9 mph EV. Eury Perez LHB split -0.92, HR risk -0.77. tough split lane (-0.92); pitcher suppresses HR (-0.77).""", blast="good"),
            row("Harry Ford", "R", "+669", 58, "🌕 💣", ["vs Eury Perez"], """2 HR, 2 near-HR, 89.9 mph EV. Eury Perez RHB split -0.23, HR risk -0.77. slight split headwind (-0.23); pitcher suppresses HR (-0.77).""", blast="high"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-22")

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

    out = ROOT / '_games-0822.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
