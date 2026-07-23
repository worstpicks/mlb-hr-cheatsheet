#!/usr/bin/env python3
"""Generate games[] block for 2026-07-22 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Bryce Eldridge (L)",
    "CJ Abrams (L)",
    "Chase DeLauter (L)",
    "Coby Mayo (R)",
    "Dylan Crews (R)",
    "Esmerlyn Valdez (R)",
    "Francisco Lindor (S)",
    "Garrett Mitchell (L)",
    "Griffin Conine (L)",
    "Heriberto Hernandez (R)",
    "Hunter Goodman (R)",
    "Jazz Chisholm Jr. (L)",
    "Jordan Walker (R)",
    "Ketel Marte (S)",
    "Luis Garcia Jr. (L)",
    "Michael Conforto (L)",
    "Mike Yastrzemski (L)",
    "Patrick Bailey (S)",
    "Riley Greene (L)",
    "Royce Lewis (R)",
    "Starling Marte (R)",
    "Trea Turner (R)",
    "Ty France (R)",
    "Willson Contreras (R)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Ben Rice (L)",
    "Braden Shewmake (L)",
    "Brice Turang (L)",
    "Ryan McMahon (L)",
    "Ryan Vilade (R)",
    "Trent Grisham (L)",
    "Willi Castro (S)",
}

PLAYER_TEAMS = {
    "Alec Bohm (R)": "PHI",
    "Ben Rice (L)": "NYY",
    "Blaze Jordan (R)": "STL",
    "Braden Shewmake (L)": "MIL",
    "Brice Turang (L)": "MIL",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "CJ Abrams (L)": "WSH",
    "Cam Smith (R)": "HOU",
    "Chase DeLauter (L)": "CLE",
    "Coby Mayo (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Colt Keith (L)": "DET",
    "Derek Hill (R)": "PHI",
    "Dillon Dingler (R)": "DET",
    "Drake Baldwin (L)": "ATL",
    "Dylan Crews (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Francisco Lindor (S)": "NYM",
    "Garrett Mitchell (L)": "MIL",
    "George Springer (R)": "TOR",
    "Griffin Conine (L)": "MIA",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "TB",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Isaac Paredes (R)": "HOU",
    "JJ Wetherholt (L)": "STL",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake Burger (R)": "TEX",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Josh Lowe (L)": "LAA",
    "Ketel Marte (S)": "ARI",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lane Thomas (R)": "KC",
    "Luis Garcia Jr. (L)": "WSH",
    "Luke Raley (L)": "SEA",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Michael Conforto (L)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Mike Yastrzemski (L)": "ATL",
    "Mookie Betts (R)": "LAD",
    "Nathaniel Lowe (L)": "CIN",
    "Nelson Velazquez (R)": "STL",
    "Patrick Bailey (S)": "CLE",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randy Arozarena (R)": "SEA",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Royce Lewis (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Ryan Vilade (R)": "TB",
    "Ryan Waldschmidt (R)": "ARI",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Starling Marte (R)": "KC",
    "Taylor Ward (R)": "BAL",
    "Travis Bazzana (L)": "CLE",
    "Trea Turner (R)": "PHI",
    "Trent Grisham (L)": "NYY",
    "Ty France (R)": "SD",
    "Tyler O'Neill (R)": "BAL",
    "Tyler Soderstrom (L)": "ATH",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("BAL @ BOS", "Kremer"),
    ("LAD @ PHI", "Nola"),
    ("MIN @ CLE", "Ober"),
    ("SF @ KC", "Lugo"),
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
    if (game_key, chip) not in BUM_MATCHUPS:
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
        "title": "ATH @ ARI - Gage Jump (L, ATH) vs Merrill Kelly (R, ARI)",
        "description": "Tail key data: Park boost -9% (stadium -8%, weather -1%). Jump (HR risk 0.31, vs LHB -0.37, vs RHB +0.67). Kelly (HR risk 0.84, vs LHB +0.65, vs RHB +0.81).",
        "rows": [
            row("Ketel Marte", "S", "+359", 84, "⭐ 🌕 💣", ["vs Jump"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.2 mph EV. Jump SHB→RHB split +0.67, HR risk 0.31. park/weather net drag (-9%).""", blast="high"),
            row("Ryan Waldschmidt", "R", "+1200", 61, "", ["vs Jump"], """0 HR, 2 near-HR, 89.4 mph EV. Jump RHB split +0.67, HR risk 0.31. park/weather net drag (-9%).""", blast="good"),
            row("Shea Langeliers", "R", "+340", 79, "", ["vs Kelly"], """1 HR, 1 near-HR, 97.1 mph EV. Kelly RHB split +0.81, HR risk 0.84. park/weather net drag (-9%).""", blast="good"),
            row("Tyler Soderstrom", "L", "+448", 75, "", ["vs Kelly"], """1 HR, 1 near-HR, 92.6 mph EV. Kelly LHB split +0.65, HR risk 0.84. park/weather net drag (-9%).""", blast="good"),
        ],
    },
    {
        "title": "BAL @ BOS - Dean Kremer 🧤 (R, BAL) vs Jake Bennett (L, BOS)",
        "description": "Tail key data: Park boost +15% (stadium -6%, weather +21%). Kremer 🧤 (HR risk 1.86, vs LHB +1.75, vs RHB +0.92). Bennett (HR risk -0.98, vs LHB -1.92, vs RHB -0.33).",
        "rows": [
            row("Willson Contreras", "R", "+287", 98, "⭐ 🌕 💣", ["vs Kremer"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 97.9 mph EV. Kremer RHB split +0.92, HR risk 1.86. park suppresses carry (-6%).""", blast="high"),
            row("Wilyer Abreu", "L", "+330", 94, "🌕 💣", ["vs Kremer"], """1 HR, 1 near-HR, 95.4 mph EV. Kremer LHB split +1.75, HR risk 1.86. park suppresses carry (-6%).""", blast="good"),
            row("Taylor Ward", "R", "+640", 58, "", ["vs Bennett"], """1 HR, 1 near-HR, 94.5 mph EV. Bennett RHB split -0.33, HR risk -0.98. slight split headwind (-0.33); pitcher suppresses HR (-0.98).""", blast="good"),
            row("Coby Mayo", "R", "+390", 66, "⭐ 🌕 💣", ["vs Bennett"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.0 mph EV. Bennett RHB split -0.33, HR risk -0.98. slight split headwind (-0.33); pitcher suppresses HR (-0.98).""", blast="high"),
            row("Tyler O'Neill", "R", "+391", 66, "🌕 💣", ["vs Bennett"], """2 HR, 2 near-HR, 95.3 mph EV. Bennett RHB split -0.33, HR risk -0.98. slight split headwind (-0.33); pitcher suppresses HR (-0.98).""", blast="high"),
            row("Pete Alonso", "R", "+343", 58, "", ["vs Bennett"], """0 HR, 97.4 mph EV. Bennett RHB split -0.33, HR risk -0.98. slight split headwind (-0.33); pitcher suppresses HR (-0.98).""", blast="good"),
        ],
    },
    {
        "title": "CIN @ SEA - Brady Singer (R, CIN) vs Emerson Hancock (R, SEA)",
        "description": "Tail key data: Park boost +12% (stadium +1%, weather +11%). Singer (HR risk 0.35, vs LHB +0.73, vs RHB -0.51). Hancock (HR risk -0.09, vs LHB +0.22, vs RHB -0.41).",
        "rows": [
            row("Luke Raley", "L", "+424", 58, "", ["vs Singer"], """0 HR, 1 near-HR, 84.2 mph EV. Singer LHB split +0.73, HR risk 0.35. limited recent HR events; lighter EV form (84.2 mph)."""),
            row("Randy Arozarena", "R", "+514", 71, "🌕 💣", ["vs Singer"], """2 HR, 2 near-HR, 90.9 mph EV. Singer RHB split -0.51, HR risk 0.35. tough split lane (-0.51).""", blast="high"),
            row("Elly De La Cruz", "S", "+433", 70, "", ["vs Hancock"], """1 HR, 2 near-HR, 95.8 mph EV. Hancock SHB→LHB split +0.22, HR risk -0.09. pitcher risk below avg (-0.09).""", blast="good"),
            row("Nathaniel Lowe", "L", "+475", 79, "🌕 💣", ["vs Hancock"], """2 HR, 3 near-HR, 93.0 mph EV. Hancock LHB split +0.22, HR risk -0.09. pitcher risk below avg (-0.09).""", blast="high"),
        ],
    },
    {
        "title": "CWS @ TEX - Anthony Kay (L, CWS) vs Tyler Alexander (L, TEX)",
        "description": "Tail key data: Park boost -13% (stadium -13%, weather -1%). Kay (HR risk -0.33, vs LHB -1.13, vs RHB +0.29). Alexander (HR risk -1.12, vs LHB -0.61, vs RHB -0.97).",
        "rows": [
            row("Joc Pederson", "L", "N/A", 58, "", ["vs Kay"], """0 HR, 1 near-HR, 95.7 mph EV. Kay LHB split -1.13, HR risk -0.33. tough split lane (-1.13); pitcher risk below avg (-0.33).""", blast="good"),
            row("Jake Burger", "R", "+364", 58, "", ["vs Kay"], """1 HR, 1 near-HR, 93.5 mph EV. Kay RHB split +0.29, HR risk -0.33. pitcher risk below avg (-0.33); park/weather net drag (-13%).""", blast="good"),
            row("Colson Montgomery", "L", "+280", 58, "", ["vs Alexander"], """1 HR, 1 near-HR, 81.7 mph EV. Alexander LHB split -0.61, HR risk -1.12. tough split lane (-0.61); pitcher suppresses HR (-1.12).""", blast="good"),
            row("Miguel Vargas", "R", "+390", 58, "", ["vs Alexander"], """0 HR, 92.8 mph EV. Alexander RHB split -0.97, HR risk -1.12. tough split lane (-0.97); pitcher suppresses HR (-1.12).""", blast="good"),
        ],
    },
    {
        "title": "DET @ CHC - Keider Montero (R, DET) vs Colin Rea (R, CHC)",
        "description": "Tail key data: Park boost -24% (stadium -1%, weather -23%). Montero (HR risk -0.99, vs LHB -0.14, vs RHB -0.82). Rea (HR risk -0.19, vs LHB -0.57, vs RHB +0.46).",
        "rows": [
            row("Michael Conforto", "L", "N/A", 62, "⭐ 🌕 💣", ["vs Montero"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.3 mph EV. Montero LHB split -0.14, HR risk -0.99. slight split headwind (-0.14); pitcher suppresses HR (-0.99).""", blast="high"),
            row("Ian Happ", "S", "+560", 58, "", ["vs Montero"], """1 HR, 1 near-HR, 93.3 mph EV. Montero SHB→LHB split -0.14, HR risk -0.99. slight split headwind (-0.14); pitcher suppresses HR (-0.99).""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+447", 58, "", ["vs Montero"], """0 HR, 92.4 mph EV. Montero LHB split -0.14, HR risk -0.99. slight split headwind (-0.14); pitcher suppresses HR (-0.99).""", blast="good"),
            row("Riley Greene", "L", "+454", 60, "⭐ 🌕 💣", ["vs Rea"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.6 mph EV. Rea LHB split -0.57, HR risk -0.19. tough split lane (-0.57); pitcher risk below avg (-0.19).""", blast="high"),
            row("Colt Keith", "L", "+810", 58, "", ["vs Rea"], """1 HR, 1 near-HR, 89.1 mph EV. Rea LHB split -0.57, HR risk -0.19. tough split lane (-0.57); pitcher risk below avg (-0.19).""", blast="good"),
            row("Dillon Dingler", "R", "+584", 65, "🌕 💣", ["vs Rea"], """2 HR, 2 near-HR, 90.2 mph EV. Rea RHB split +0.46, HR risk -0.19. pitcher risk below avg (-0.19); park/weather net drag (-24%).""", blast="high"),
        ],
    },
    {
        "title": "LAD @ PHI - Eric Lauer (L, LAD) vs Aaron Nola 🧤 (R, PHI)",
        "description": "Tail key data: Park boost +22% (stadium +13%, weather +9%). Lauer (HR risk 0.68, vs LHB +0.23, vs RHB +0.78). Nola 🧤 (HR risk 1.25, vs LHB +0.67, vs RHB +1.79).",
        "rows": [
            row("Kyle Schwarber", "L", "+221", 90, "🌕 💣", ["vs Lauer"], """2 HR, 3 near-HR, 92.0 mph EV. Lauer LHB split +0.23, HR risk 0.68.""", blast="high"),
            row("Derek Hill", "R", "+600", 83, "", ["vs Lauer"], """1 HR, 1 near-HR, 93.4 mph EV. Lauer RHB split +0.78, HR risk 0.68.""", blast="good"),
            row("Trea Turner", "R", "+480", 84, "⭐", ["vs Lauer"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.0 mph EV. Lauer RHB split +0.78, HR risk 0.68.""", blast="good"),
            row("Alec Bohm", "R", "+527", 87, "", ["vs Lauer"], """1 HR, 2 near-HR, 95.7 mph EV. Lauer RHB split +0.78, HR risk 0.68.""", blast="good"),
            row("Shohei Ohtani", "L", "+210", 77, "", ["vs Nola"], """0 HR, 90.9 mph EV. Nola LHB split +0.67, HR risk 1.25. limited recent HR events."""),
            row("Mookie Betts", "R", "+501", 95, "🌕 💣", ["vs Nola"], """2 HR, 2 near-HR, 89.4 mph EV. Nola RHB split +1.79, HR risk 1.25.""", blast="high"),
            row("Max Muncy", "L", "+321", 79, "", ["vs Nola"], """0 HR, 1 near-HR, 91.4 mph EV. Nola LHB split +0.67, HR risk 1.25. limited recent HR events."""),
        ],
    },
    {
        "title": "MIA @ HOU - Sandy Alcantara (R, MIA) vs Peter Lambert (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +6%, weather -1%). Alcantara (HR risk -0.79, vs LHB -0.52, vs RHB -0.70). Lambert (HR risk 0.10, vs LHB -0.34, vs RHB +0.69).",
        "rows": [
            row("Cam Smith", "R", "+640", 58, "", ["vs Alcantara"], """1 HR, 1 near-HR, 91.8 mph EV. Alcantara RHB split -0.70, HR risk -0.79. tough split lane (-0.70); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Yordan Alvarez", "L", "+230", 58, "⭐", ["vs Alcantara"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.0 mph EV. Alcantara LHB split -0.52, HR risk -0.79. tough split lane (-0.52); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Isaac Paredes", "R", "+520", 58, "", ["vs Alcantara"], """1 HR, 1 near-HR, 84.5 mph EV. Alcantara RHB split -0.70, HR risk -0.79. tough split lane (-0.70); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Heriberto Hernandez", "R", "+390", 69, "⭐", ["vs Lambert"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 95.8 mph EV. Lambert RHB split +0.69, HR risk 0.10.""", blast="good"),
            row("Griffin Conine", "L", "+500", 73, "⭐ 🌕 💣", ["vs Lambert"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.2 mph EV. Lambert LHB split -0.34, HR risk 0.10. slight split headwind (-0.34).""", blast="high"),
            row("Joe Mack", "L", "+650", 67, "🌕 💣", ["vs Lambert"], """2 HR, 2 near-HR, 89.3 mph EV. Lambert LHB split -0.34, HR risk 0.10. slight split headwind (-0.34).""", blast="high"),
            row("Kyle Stowers", "L", "+375", 58, "", ["vs Lambert"], """0 HR, 96.6 mph EV. Lambert LHB split -0.34, HR risk 0.10. slight split headwind (-0.34); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIN @ CLE - Bailey Ober 🧤 (R, MIN) vs Slade Cecconi (R, CLE)",
        "description": "Tail key data: Park boost -2% (stadium -3%, weather +1%). Ober 🧤 (HR risk 1.19, vs LHB +1.14, vs RHB +0.57). Cecconi (HR risk -0.06, vs LHB -0.04, vs RHB +0.07).",
        "rows": [
            row("Chase DeLauter", "L", "+513", 93, "🚀 ⭐ 🌕 💣", ["vs Ober"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.6 mph EV. Ober LHB split +1.14, HR risk 1.19.""", blast="high"),
            row("Patrick Bailey", "S", "+980", 95, "⭐ 🌕 💣", ["vs Ober"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 98.7 mph EV. Ober SHB→LHB split +1.14, HR risk 1.19.""", blast="high"),
            row("Rhys Hoskins", "R", "N/A", 80, "", ["vs Ober"], """1 HR, 1 near-HR, 91.5 mph EV. Ober RHB split +0.57, HR risk 1.19.""", blast="good"),
            row("Travis Bazzana", "L", "+500", 93, "🌕 💣", ["vs Ober"], """2 HR, 2 near-HR, 94.0 mph EV. Ober LHB split +1.14, HR risk 1.19.""", blast="high"),
            row("Royce Lewis", "R", "+477", 62, "⭐", ["vs Cecconi"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.2 mph EV. Cecconi RHB split +0.07, HR risk -0.06. pitcher risk below avg (-0.06).""", blast="good"),
        ],
    },
    {
        "title": "NYM @ MIL - Christian Scott (R, NYM) vs Logan Henderson (R, MIL)",
        "description": "Tail key data: Park boost +7% (stadium +10%, weather -3%). Scott (HR risk 0.79, vs LHB +1.21, vs RHB -0.76). Henderson (HR risk 0.11, vs LHB +0.13, vs RHB +0.05).",
        "rows": [
            row("Jackson Chourio", "R", "+432", 75, "", ["vs Scott"], """1 HR, 3 near-HR, 93.5 mph EV. Scott RHB split -0.76, HR risk 0.79. tough split lane (-0.76).""", blast="good"),
            row("Braden Shewmake", "L", "N/A", 84, "💎", ["vs Scott"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 96.6 mph EV. Scott LHB split +1.21, HR risk 0.79.""", blast="good"),
            row("Garrett Mitchell", "L", "+475", 79, "⭐", ["vs Scott"], """Worst Pickz Favorite. 0 HR, 94.6 mph EV. Scott LHB split +1.21, HR risk 0.79. limited recent HR events.""", blast="good"),
            row("Brice Turang", "L", "+650", 88, "🌕 💣 💎", ["vs Scott"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 98.0 mph EV. Scott LHB split +1.21, HR risk 0.79.""", blast="good"),
            row("Jared Young", "L", "+500", 63, "", ["vs Henderson"], """1 HR, 2 near-HR, 89.3 mph EV. Henderson LHB split +0.13, HR risk 0.11.""", blast="good"),
            row("Francisco Lindor", "S", "+360", 66, "⭐", ["vs Henderson"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.7 mph EV. Henderson SHB→LHB split +0.13, HR risk 0.11.""", blast="good"),
        ],
    },
    {
        "title": "PIT @ NYY (G1) - Mitch Keller (R, PIT) vs Gerrit Cole (R, NYY)",
        "description": "Tail key data: Park boost +20% (stadium +3%, weather +18%). Keller (HR risk 0.56, vs LHB +0.84, vs RHB -0.34). Cole (HR risk 0.87, vs LHB +1.25, vs RHB -0.43).",
        "rows": [
            row("Jazz Chisholm Jr.", "L", "+292", 91, "🌕 💣", ["vs Keller"], """2 HR, 2 near-HR, 94.8 mph EV. Keller LHB split +0.84, HR risk 0.56.""", blast="high"),
            row("Ben Rice", "L", "+230", 95, "⭐ 🌕 💣", ["vs Keller"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 99.0 mph EV. Keller LHB split +0.84, HR risk 0.56.""", blast="high"),
            row("Ryan McMahon", "L", "+400", 86, "💎", ["vs Keller"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 97.2 mph EV. Keller LHB split +0.84, HR risk 0.56.""", blast="good"),
            row("Trent Grisham", "L", "+285", 90, "🌕 💣 💎", ["vs Keller"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 96.5 mph EV. Keller LHB split +0.84, HR risk 0.56.""", blast="good"),
            row("Esmerlyn Valdez", "R", "+316", 85, "⭐ 🌕 💣", ["vs Cole"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.4 mph EV. Cole RHB split -0.43, HR risk 0.87. tough split lane (-0.43).""", blast="high"),
            row("Bryan Reynolds", "S", "+456", 93, "🌕 💣", ["vs Cole"], """2 HR, 2 near-HR, 93.5 mph EV. Cole SHB→LHB split +1.25, HR risk 0.87.""", blast="high"),
        ],
    },
    {
        "title": "PIT @ NYY (G2) - Bubba Chandler (R, PIT) vs Max Fried (L, NYY)",
        "description": "Tail key data: Park boost +11% (stadium +2%, weather +9%). Chandler (HR risk -0.52, vs LHB +0.00, vs RHB -0.92). Fried (HR risk -1.57, vs LHB -0.70, vs RHB -1.37).",
        "rows": [
            row("Trent Grisham", "L", "+280", 78, "🌕 💣", ["vs Chandler"], """2 HR, 4 near-HR, 97.0 mph EV. Chandler LHB split +0.00, HR risk -0.52. pitcher suppresses HR (-0.52).""", blast="high"),
            row("Jazz Chisholm Jr.", "L", "+300", 67, "⭐ 🌕 💣", ["vs Chandler"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.6 mph EV. Chandler LHB split +0.00, HR risk -0.52. pitcher suppresses HR (-0.52).""", blast="high"),
            row("Ben Rice", "L", "+250", 77, "🌕 💣 💎", ["vs Chandler"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 96.3 mph EV. Chandler LHB split +0.00, HR risk -0.52. pitcher suppresses HR (-0.52).""", blast="high"),
            row("Ryan McMahon", "L", "+390", 63, "", ["vs Chandler"], """1 HR, 1 near-HR, 96.0 mph EV. Chandler LHB split +0.00, HR risk -0.52. pitcher suppresses HR (-0.52).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+320", 58, "🚀 🌕 💣", ["vs Fried"], """2 HR, 2 near-HR, 100.5 mph EV. Fried RHB split -1.37, HR risk -1.57. tough split lane (-1.37); pitcher suppresses HR (-1.57).""", blast="high"),
        ],
    },
    {
        "title": "SD @ ATL - Michael King (R, SD) vs Martin Perez (L, ATL)",
        "description": "Tail key data: Park boost +6% (stadium -3%, weather +9%). King (HR risk -0.63, vs LHB -0.67, vs RHB -0.15). Perez (HR risk -0.11, vs LHB +0.58, vs RHB -0.33).",
        "rows": [
            row("Matt Olson", "L", "+335", 58, "", ["vs King"], """1 HR, 1 near-HR, 94.3 mph EV. King LHB split -0.67, HR risk -0.63. tough split lane (-0.67); pitcher suppresses HR (-0.63).""", blast="good"),
            row("Drake Baldwin", "L", "+458", 58, "", ["vs King"], """1 HR, 2 near-HR, 97.1 mph EV. King LHB split -0.67, HR risk -0.63. tough split lane (-0.67); pitcher suppresses HR (-0.63).""", blast="good"),
            row("Mike Yastrzemski", "L", "+610", 58, "⭐", ["vs King"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 89.3 mph EV. King LHB split -0.67, HR risk -0.63. tough split lane (-0.67); pitcher suppresses HR (-0.63).""", blast="good"),
            row("Jackson Merrill", "L", "+520", 76, "🌕 💣", ["vs Perez"], """2 HR, 2 near-HR, 93.2 mph EV. Perez LHB split +0.58, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="high"),
            row("Ty France", "R", "+480", 62, "⭐", ["vs Perez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.6 mph EV. Perez RHB split -0.33, HR risk -0.11. slight split headwind (-0.33); pitcher risk below avg (-0.11).""", blast="good"),
        ],
    },
    {
        "title": "SF @ KC - Landen Roupp (R, SF) vs Seth Lugo 🧤 (R, KC)",
        "description": "Tail key data: Park boost -3% (stadium +11%, weather -14%). Roupp (HR risk -0.89, vs LHB -0.93, vs RHB -0.30). Lugo 🧤 (HR risk 1.10, vs LHB +0.70, vs RHB +1.21).",
        "rows": [
            row("Starling Marte", "R", "+1450", 58, "🚀 ⭐", ["vs Roupp"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 100.2 mph EV. Roupp RHB split -0.30, HR risk -0.89. slight split headwind (-0.30); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Lane Thomas", "R", "+850", 58, "", ["vs Roupp"], """1 HR, 1 near-HR, 96.6 mph EV. Roupp RHB split -0.30, HR risk -0.89. slight split headwind (-0.30); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Bryce Eldridge", "L", "+450", 83, "⭐", ["vs Lugo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.2 mph EV. Lugo LHB split +0.70, HR risk 1.10. weather carry headwind (-14%).""", blast="good"),
            row("Rafael Devers", "L", "+353", 81, "", ["vs Lugo"], """1 HR, 1 near-HR, 92.7 mph EV. Lugo LHB split +0.70, HR risk 1.10. weather carry headwind (-14%).""", blast="good"),
        ],
    },
    {
        "title": "STL @ LAA - Hunter Dobbins (R, STL) vs Reid Detmers (L, LAA)",
        "description": "Tail key data: Park boost +15% (stadium +7%, weather +8%). Dobbins (HR risk 0.41, vs LHB +0.04, vs RHB +0.94). Detmers (HR risk 0.13, vs LHB -0.74, vs RHB +0.47).",
        "rows": [
            row("Josh Lowe", "L", "+520", 67, "", ["vs Dobbins"], """1 HR, 2 near-HR, 85.5 mph EV. Dobbins LHB split +0.04, HR risk 0.41. lighter EV form (85.5 mph).""", blast="good"),
            row("Blaze Jordan", "R", "+830", 66, "", ["vs Detmers"], """0 HR, 1 near-HR, 93.1 mph EV. Detmers RHB split +0.47, HR risk 0.13. limited recent HR events.""", blast="good"),
            row("Nelson Velazquez", "R", "+456", 72, "", ["vs Detmers"], """1 HR, 1 near-HR, 94.5 mph EV. Detmers RHB split +0.47, HR risk 0.13.""", blast="good"),
            row("JJ Wetherholt", "L", "+535", 61, "", ["vs Detmers"], """1 HR, 1 near-HR, 92.3 mph EV. Detmers LHB split -0.74, HR risk 0.13. tough split lane (-0.74).""", blast="good"),
            row("Jordan Walker", "R", "+365", 69, "🚀 ⭐", ["vs Detmers"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 102.2 mph EV. Detmers RHB split +0.47, HR risk 0.13. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TB @ TOR - Griffin Jax (R, TB) vs Braydon Fisher (R, TOR)",
        "description": "Tail key data: Park boost +7% (stadium +6%, weather +1%). Jax (HR risk 0.46, vs LHB +0.27, vs RHB +0.66). Fisher (HR risk -0.11, vs LHB +0.26, vs RHB -0.08).",
        "rows": [
            row("George Springer", "R", "+472", 75, "", ["vs Jax"], """1 HR, 2 near-HR, 90.7 mph EV. Jax RHB split +0.66, HR risk 0.46.""", blast="good"),
            row("Jonathan Aranda", "L", "+571", 63, "", ["vs Fisher"], """0 HR, 1 near-HR, 97.3 mph EV. Fisher LHB split +0.26, HR risk -0.11. pitcher risk below avg (-0.11); limited recent HR events.""", blast="good"),
            row("Ryan Vilade", "R", "N/A", 73, "🌕 💣 💎", ["vs Fisher"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.8 mph EV. Fisher RHB split -0.08, HR risk -0.11. slight split headwind (-0.08); pitcher risk below avg (-0.11).""", blast="high"),
            row("Hunter Feduccia", "L", "+1040", 68, "", ["vs Fisher"], """1 HR, 2 near-HR, 95.6 mph EV. Fisher LHB split +0.26, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ COL - Cade Cavalli (R, WSH) vs Gabriel Hughes (R, COL)",
        "description": "Tail key data: Park boost +25% (stadium +18%, weather +7%). Cavalli (HR risk -0.24, vs LHB +0.26, vs RHB -0.81). Hughes (HR risk -1.57, vs LHB -1.53, vs RHB -0.72).",
        "rows": [
            row("Hunter Goodman", "R", "+250", 75, "⭐ 🌕 💣", ["vs Cavalli"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 93.9 mph EV. Cavalli RHB split -0.81, HR risk -0.24. tough split lane (-0.81); pitcher risk below avg (-0.24).""", blast="high"),
            row("Willi Castro", "S", "N/A", 73, "💎", ["vs Cavalli"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 92.4 mph EV. Cavalli SHB→LHB split +0.26, HR risk -0.24. pitcher risk below avg (-0.24).""", blast="good"),
            row("Luis Garcia Jr.", "L", "+352", 58, "🚀 ⭐", ["vs Hughes"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 100.4 mph EV. Hughes LHB split -1.53, HR risk -1.57. tough split lane (-1.53); pitcher suppresses HR (-1.57).""", blast="good"),
            row("CJ Abrams", "L", "+344", 66, "⭐ 🌕 💣", ["vs Hughes"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 93.1 mph EV. Hughes LHB split -1.53, HR risk -1.57. tough split lane (-1.53); pitcher suppresses HR (-1.57).""", blast="high"),
            row("James Wood", "L", "+240", 68, "🌕 💣", ["vs Hughes"], """3 HR, 3 near-HR, 95.2 mph EV. Hughes LHB split -1.53, HR risk -1.57. tough split lane (-1.53); pitcher suppresses HR (-1.57).""", blast="high"),
            row("Dylan Crews", "R", "+488", 58, "⭐", ["vs Hughes"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.6 mph EV. Hughes RHB split -0.72, HR risk -1.57. tough split lane (-0.72); pitcher suppresses HR (-1.57).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-22")

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

    out = ROOT / '_games-0711.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
