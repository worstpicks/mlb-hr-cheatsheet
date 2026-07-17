#!/usr/bin/env python3
"""Generate games[] block for 2026-07-17 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Ben Rice (L)",
    "Bryce Eldridge (L)",
    "Casey Schmitt (R)",
    "Chase DeLauter (L)",
    "Eugenio Suarez (R)",
    "Heliot Ramos (R)",
    "Junior Caminero (R)",
    "Max Kepler (L)",
    "Rafael Devers (L)",
    "Rhys Hoskins (R)",
    "Shea Langeliers (R)",
}

GEMS = {
    "Griffin Conine (L)",
    "Lane Thomas (R)",
    "Mike Trout (R)",
    "Ryan McMahon (L)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Ben Rice (L)": "NYY",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Brice Turang (L)": "MIL",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "CJ Abrams (L)": "WSH",
    "Casey Schmitt (R)": "SF",
    "Chase DeLauter (L)": "CLE",
    "Cole Carrigg (S)": "COL",
    "Cole Young (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Eduardo Valencia (R)": "DET",
    "Eugenio Suarez (R)": "CIN",
    "Gabriel Arias (R)": "CLE",
    "Garrett Mitchell (L)": "MIL",
    "Griffin Conine (L)": "MIA",
    "Gunnar Henderson (L)": "BAL",
    "Heliot Ramos (R)": "SF",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "JJ Bleday (L)": "CIN",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "James McCann (R)": "ARI",
    "James Outman (L)": "DET",
    "James Wood (L)": "WSH",
    "Jarren Duran (L)": "BOS",
    "Joc Pederson (L)": "TEX",
    "Jonathan Aranda (L)": "TB",
    "Josh Lowe (L)": "LAA",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kazuma Okamoto (R)": "TOR",
    "Kody Clemens (L)": "MIN",
    "Kyle Stowers (L)": "MIA",
    "Lane Thomas (R)": "KC",
    "Lars Nootbaar (L)": "STL",
    "Manny Machado (R)": "SD",
    "Marcell Ozuna (R)": "PIT",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Max Schuemann (R)": "NYY",
    "Mickey Moniak (L)": "COL",
    "Miguel Rojas (R)": "LAD",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Mitch Garver (R)": "SEA",
    "Munetaka Murakami (L)": "CWS",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Rhys Hoskins (R)": "CLE",
    "Royce Lewis (R)": "MIN",
    "Ryan Jeffers (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Samuel Basallo (L)": "BAL",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Steer (R)": "CIN",
    "Spencer Torkelson (R)": "DET",
    "Starling Marte (R)": "KC",
    "Ty France (R)": "SD",
    "Tyler Soderstrom (L)": "ATH",
    "Vaughn Grissom (R)": "LAA",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("BAL @ HOU", "Kremer"),
    ("LAD @ NYY", "Sasaki"),
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
        "title": "BAL @ HOU - Dean Kremer 🧤 (R, BAL) vs Peter Lambert (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +0%). Kremer 🧤 (HR risk 1.95, vs LHB +1.77, vs RHB +1.21). Lambert (HR risk 0.19, vs LHB -0.00, vs RHB +0.41).",
        "rows": [
            row("Yordan Alvarez", "L", "+261", 99, "🌕 💣", ["vs Kremer"], """2 HR, 3 near-HR, 95.4 mph EV. Kremer LHB split +1.77, HR risk 1.95.""", blast="high"),
            row("Samuel Basallo", "L", "+532", 81, "🌕 💣", ["vs Lambert"], """2 HR, 3 near-HR, 96.7 mph EV. Lambert LHB split -0.00, HR risk 0.19.""", blast="high"),
            row("Gunnar Henderson", "L", "+500", 68, "", ["vs Lambert"], """1 HR, 2 near-HR, 95.1 mph EV. Lambert LHB split -0.00, HR risk 0.19.""", blast="good"),
            row("Pete Alonso", "R", "+211", 61, "", ["vs Lambert"], """1 HR, 1 near-HR, 82.9 mph EV. Lambert RHB split +0.41, HR risk 0.19. lighter EV form (82.9 mph).""", blast="good"),
        ],
    },
    {
        "title": "CIN @ COL - Brady Singer (R, CIN) vs Gabriel Hughes (R, COL)",
        "description": "Tail key data: Park boost +23% (stadium +20%, weather +3%). Singer (HR risk 0.17, vs LHB +0.58, vs RHB -0.47). Hughes (HR risk -1.87, vs LHB -1.62, vs RHB -1.31).",
        "rows": [
            row("Hunter Goodman", "R", "+261", 58, "", ["vs Singer"], """1 HR, 1 near-HR, 81.9 mph EV. Singer RHB split -0.47, HR risk 0.17. tough split lane (-0.47); lighter EV form (81.9 mph).""", blast="good"),
            row("Mickey Moniak", "L", "+303", 69, "", ["vs Singer"], """1 HR, 1 near-HR, 88.1 mph EV. Singer LHB split +0.58, HR risk 0.17.""", blast="good"),
            row("Cole Carrigg", "S", "+800", 81, "", ["vs Singer"], """1 HR, 3 near-HR, 94.4 mph EV. Singer SHB→LHB split +0.58, HR risk 0.17.""", blast="good"),
            row("Spencer Steer", "R", "+400", 58, "🌕 💣", ["vs Hughes"], """2 HR, 2 near-HR, 93.4 mph EV. Hughes RHB split -1.31, HR risk -1.87. tough split lane (-1.31); pitcher suppresses HR (-1.87).""", blast="high"),
            row("Eugenio Suarez", "R", "+401", 58, "⭐ 🌕 💣", ["vs Hughes"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.5 mph EV. Hughes RHB split -1.31, HR risk -1.87. tough split lane (-1.31); pitcher suppresses HR (-1.87).""", blast="high"),
            row("JJ Bleday", "L", "+327", 58, "", ["vs Hughes"], """0 HR, 87.9 mph EV. Hughes LHB split -1.62, HR risk -1.87. tough split lane (-1.62); pitcher suppresses HR (-1.87)."""),
        ],
    },
    {
        "title": "CWS @ TOR - Anthony Kay (L, CWS) vs Spencer Miles (R, TOR)",
        "description": "Tail key data: Park boost +5% (stadium +7%, weather -2%). Kay (HR risk -0.47, vs LHB -0.65, vs RHB -0.26). Miles (HR risk -1.17, vs LHB -0.14, vs RHB -1.57).",
        "rows": [
            row("Vladimir Guerrero Jr.", "R", "+382", 58, "", ["vs Kay"], """0 HR, 96.0 mph EV. Kay RHB split -0.26, HR risk -0.47. slight split headwind (-0.26); pitcher suppresses HR (-0.47).""", blast="good"),
            row("Kazuma Okamoto", "R", "+339", 58, "", ["vs Kay"], """1 HR, 2 near-HR, 92.5 mph EV. Kay RHB split -0.26, HR risk -0.47. slight split headwind (-0.26); pitcher suppresses HR (-0.47).""", blast="good"),
            row("Munetaka Murakami", "L", "+297", 72, "🌕 💣", ["vs Miles"], """3 HR, 3 near-HR, 96.3 mph EV. Miles LHB split -0.14, HR risk -1.17. slight split headwind (-0.14); pitcher suppresses HR (-1.17).""", blast="high"),
            row("Miguel Vargas", "R", "+362", 58, "", ["vs Miles"], """0 HR, 2 near-HR, 93.5 mph EV. Miles RHB split -1.57, HR risk -1.17. tough split lane (-1.57); pitcher suppresses HR (-1.17).""", blast="good"),
        ],
    },
    {
        "title": "DET @ LAA - Troy Melton (R, DET) vs Reid Detmers (L, LAA)",
        "description": "Tail key data: Park boost +17% (stadium +9%, weather +8%). Melton (HR risk 0.08, vs LHB +0.63, vs RHB -0.74). Detmers (HR risk 0.01, vs LHB -0.53, vs RHB +0.21).",
        "rows": [
            row("Mike Trout", "R", "+310", 58, "💎", ["vs Melton"], """Worst Pickz Hidden Gem. 0 HR, 81.3 mph EV. Melton RHB split -0.74, HR risk 0.08. tough split lane (-0.74); limited recent HR events."""),
            row("Josh Lowe", "L", "+599", 70, "", ["vs Melton"], """1 HR, 2 near-HR, 89.7 mph EV. Melton LHB split +0.63, HR risk 0.08.""", blast="good"),
            row("Vaughn Grissom", "R", "+750", 58, "", ["vs Melton"], """1 HR, 1 near-HR, 86.9 mph EV. Melton RHB split -0.74, HR risk 0.08. tough split lane (-0.74); lighter EV form (86.9 mph).""", blast="good"),
            row("Eduardo Valencia", "R", "+520", 71, "🚀", ["vs Detmers"], """1 HR, 1 near-HR, 100.5 mph EV. Detmers RHB split +0.21, HR risk 0.01.""", blast="good"),
            row("Spencer Torkelson", "R", "+401", 66, "", ["vs Detmers"], """1 HR, 1 near-HR, 91.9 mph EV. Detmers RHB split +0.21, HR risk 0.01.""", blast="good"),
            row("James Outman", "L", "+720", 60, "", ["vs Detmers"], """0 HR, 1 near-HR, 95.1 mph EV. Detmers LHB split -0.53, HR risk 0.01. tough split lane (-0.53); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "LAD @ NYY - Roki Sasaki 🧤 (R, LAD) vs Gerrit Cole (R, NYY)",
        "description": "Tail key data: Park boost +5% (stadium +3%, weather +1%). Sasaki 🧤 (HR risk 1.64, vs LHB +1.17, vs RHB +1.77). Cole (HR risk 0.44, vs LHB +0.93, vs RHB -0.61).",
        "rows": [
            row("Ben Rice", "L", "+320", 95, "⭐ 🌕 💣", ["vs Sasaki"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.4 mph EV. Sasaki LHB split +1.17, HR risk 1.64.""", blast="high"),
            row("Ryan McMahon", "L", "+480", 89, "🌕 💣 💎", ["vs Sasaki"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.1 mph EV. Sasaki LHB split +1.17, HR risk 1.64.""", blast="good"),
            row("Max Schuemann", "R", "+900", 83, "", ["vs Sasaki"], """0 HR, 90.4 mph EV. Sasaki RHB split +1.77, HR risk 1.64. limited recent HR events."""),
            row("Shohei Ohtani", "L", "+215", 62, "", ["vs Cole"], """0 HR, 1 near-HR, 85.7 mph EV. Cole LHB split +0.93, HR risk 0.44. limited recent HR events; lighter EV form (85.7 mph)."""),
            row("Miguel Rojas", "R", "N/A", 58, "", ["vs Cole"], """0 HR, 91.5 mph EV. Cole RHB split -0.61, HR risk 0.44. tough split lane (-0.61); limited recent HR events."""),
        ],
    },
    {
        "title": "MIA @ MIL - Sandy Alcantara (R, MIA) vs Logan Henderson (R, MIL)",
        "description": "Tail key data: Park boost +29% (stadium +10%, weather +19%). Alcantara (HR risk -0.89, vs LHB -0.47, vs RHB -1.02). Henderson (HR risk -0.25, vs LHB -0.20, vs RHB -0.03).",
        "rows": [
            row("Jake Bauers", "L", "+350", 58, "", ["vs Alcantara"], """1 HR, 1 near-HR, 91.9 mph EV. Alcantara LHB split -0.47, HR risk -0.89. tough split lane (-0.47); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Garrett Mitchell", "L", "+477", 58, "", ["vs Alcantara"], """0 HR, 95.7 mph EV. Alcantara LHB split -0.47, HR risk -0.89. tough split lane (-0.47); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Brice Turang", "L", "+600", 59, "", ["vs Alcantara"], """1 HR, 2 near-HR, 93.9 mph EV. Alcantara LHB split -0.47, HR risk -0.89. tough split lane (-0.47); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Griffin Conine", "L", "+374", 77, "🌕 💣 💎", ["vs Henderson"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 98.5 mph EV. Henderson LHB split -0.20, HR risk -0.25. slight split headwind (-0.20); pitcher risk below avg (-0.25).""", blast="high"),
            row("Kyle Stowers", "L", "+296", 68, "", ["vs Henderson"], """1 HR, 1 near-HR, 96.0 mph EV. Henderson LHB split -0.20, HR risk -0.25. slight split headwind (-0.20); pitcher risk below avg (-0.25).""", blast="good"),
            row("Heriberto Hernandez", "R", "+390", 66, "", ["vs Henderson"], """1 HR, 1 near-HR, 93.1 mph EV. Henderson RHB split -0.03, HR risk -0.25. slight split headwind (-0.03); pitcher risk below avg (-0.25).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ CHC - Bailey Ober (R, MIN) vs Colin Rea (R, CHC)",
        "description": "Tail key data: Park boost +26% (stadium -2%, weather +28%). Ober (HR risk 0.84, vs LHB +1.07, vs RHB +0.23). Rea (HR risk -0.18, vs LHB -0.45, vs RHB +0.30).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+250", 80, "", ["vs Ober"], """1 HR, 1 near-HR, 82.4 mph EV. Ober LHB split +1.07, HR risk 0.84. lighter EV form (82.4 mph).""", blast="good"),
            row("Royce Lewis", "R", "+376", 76, "🌕 💣", ["vs Rea"], """2 HR, 2 near-HR, 90.5 mph EV. Rea RHB split +0.30, HR risk -0.18. pitcher risk below avg (-0.18).""", blast="high"),
            row("Ryan Jeffers", "R", "+363", 68, "", ["vs Rea"], """1 HR, 2 near-HR, 91.0 mph EV. Rea RHB split +0.30, HR risk -0.18. pitcher risk below avg (-0.18).""", blast="good"),
            row("Kody Clemens", "L", "+377", 59, "", ["vs Rea"], """1 HR, 1 near-HR, 89.6 mph EV. Rea LHB split -0.45, HR risk -0.18. tough split lane (-0.45); pitcher risk below avg (-0.18).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ CLE - Jared Jones (R, PIT) vs Gavin Williams (R, CLE)",
        "description": "Tail key data: Park boost -2% (stadium -4%, weather +1%). Jones (HR risk -0.16, vs LHB +0.21, vs RHB -0.44). Williams (HR risk 0.46, vs LHB +0.03, vs RHB +1.34).",
        "rows": [
            row("Chase DeLauter", "L", "+560", 74, "⭐ 🌕 💣", ["vs Jones"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.1 mph EV. Jones LHB split +0.21, HR risk -0.16. pitcher risk below avg (-0.16).""", blast="high"),
            row("Rhys Hoskins", "R", "N/A", 68, "⭐ 🌕 💣", ["vs Jones"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.9 mph EV. Jones RHB split -0.44, HR risk -0.16. tough split lane (-0.44); pitcher risk below avg (-0.16).""", blast="high"),
            row("Gabriel Arias", "R", "+500", 58, "", ["vs Jones"], """1 HR, 1 near-HR, 94.9 mph EV. Jones RHB split -0.44, HR risk -0.16. tough split lane (-0.44); pitcher risk below avg (-0.16).""", blast="good"),
            row("Bryan Reynolds", "S", "+465", 67, "", ["vs Williams"], """0 HR, 1 near-HR, 89.6 mph EV. Williams SHB→RHB split +1.34, HR risk 0.46. limited recent HR events."""),
            row("Brandon Lowe", "L", "+396", 73, "", ["vs Williams"], """1 HR, 2 near-HR, 98.5 mph EV. Williams LHB split +0.03, HR risk 0.46.""", blast="good"),
            row("Marcell Ozuna", "R", "N/A", 79, "", ["vs Williams"], """1 HR, 1 near-HR, 93.2 mph EV. Williams RHB split +1.34, HR risk 0.46.""", blast="good"),
        ],
    },
    {
        "title": "SD @ KC - Michael King (R, SD) vs Seth Lugo (R, KC)",
        "description": "Tail key data: Park boost +27% (stadium +12%, weather +16%). King (HR risk -0.88, vs LHB -0.71, vs RHB -0.59). Lugo (HR risk 0.92, vs LHB +0.68, vs RHB +1.06).",
        "rows": [
            row("Lane Thomas", "R", "+563", 58, "💎", ["vs King"], """Worst Pickz Hidden Gem. 0 HR, 99.1 mph EV. King RHB split -0.59, HR risk -0.88. tough split lane (-0.59); pitcher suppresses HR (-0.88).""", blast="good"),
            row("Starling Marte", "R", "N/A", 59, "", ["vs King"], """1 HR, 2 near-HR, 94.7 mph EV. King RHB split -0.59, HR risk -0.88. tough split lane (-0.59); pitcher suppresses HR (-0.88).""", blast="good"),
            row("Ty France", "R", "+500", 87, "", ["vs Lugo"], """0 HR, 1 near-HR, 96.9 mph EV. Lugo RHB split +1.06, HR risk 0.92. limited recent HR events.""", blast="good"),
            row("Manny Machado", "R", "+360", 73, "", ["vs Lugo"], """0 HR, 87.6 mph EV. Lugo RHB split +1.06, HR risk 0.92. limited recent HR events; lighter EV form (87.6 mph)."""),
        ],
    },
    {
        "title": "SF @ SEA - Landen Roupp (R, SF) vs Bryce Miller (R, SEA)",
        "description": "Tail key data: Park boost -2% (stadium +1%, weather -3%). Roupp (HR risk -0.78, vs LHB -0.86, vs RHB -0.30). Miller (HR risk 0.22, vs LHB +0.13, vs RHB +0.35).",
        "rows": [
            row("Cole Young", "L", "+900", 61, "🌕 💣", ["vs Roupp"], """2 HR, 2 near-HR, 98.7 mph EV. Roupp LHB split -0.86, HR risk -0.78. tough split lane (-0.86); pitcher suppresses HR (-0.78).""", blast="high"),
            row("Mitch Garver", "R", "N/A", 58, "", ["vs Roupp"], """1 HR, 1 near-HR, 89.7 mph EV. Roupp RHB split -0.30, HR risk -0.78. slight split headwind (-0.30); pitcher suppresses HR (-0.78).""", blast="good"),
            row("Rafael Devers", "L", "+393", 77, "⭐ 🌕 💣", ["vs Miller"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.7 mph EV. Miller LHB split +0.13, HR risk 0.22.""", blast="high"),
            row("Bryce Eldridge", "L", "+552", 67, "⭐", ["vs Miller"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.3 mph EV. Miller LHB split +0.13, HR risk 0.22.""", blast="good"),
            row("Casey Schmitt", "R", "+483", 66, "⭐", ["vs Miller"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.4 mph EV. Miller RHB split +0.35, HR risk 0.22.""", blast="good"),
            row("Heliot Ramos", "R", "+525", 75, "⭐", ["vs Miller"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 97.8 mph EV. Miller RHB split +0.35, HR risk 0.22.""", blast="good"),
            row("Willy Adames", "R", "+538", 72, "🌕 💣", ["vs Miller"], """2 HR, 2 near-HR, 90.1 mph EV. Miller RHB split +0.35, HR risk 0.22.""", blast="high"),
        ],
    },
    {
        "title": "STL @ ARI - Andre Pallante (R, STL) vs Merrill Kelly (R, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -7%, weather -1%). Pallante (HR risk -0.35, vs LHB +0.10, vs RHB -0.55). Kelly (HR risk 0.80, vs LHB +0.41, vs RHB +1.06).",
        "rows": [
            row("Max Kepler", "L", "+324", 62, "⭐", ["vs Pallante"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.7 mph EV. Pallante LHB split +0.10, HR risk -0.35. pitcher risk below avg (-0.35); park/weather net drag (-8%).""", blast="good"),
            row("James McCann", "R", "N/A", 59, "🌕 💣", ["vs Pallante"], """2 HR, 3 near-HR, 83.5 mph EV. Pallante RHB split -0.55, HR risk -0.35. tough split lane (-0.55); pitcher risk below avg (-0.35).""", blast="high"),
            row("Lars Nootbaar", "L", "+399", 68, "", ["vs Kelly"], """1 HR, 1 near-HR, 88.5 mph EV. Kelly LHB split +0.41, HR risk 0.80. park/weather net drag (-8%).""", blast="good"),
            row("Alec Burleson", "L", "+242", 70, "⭐", ["vs Kelly"], """Worst Pickz Favorite. 0 HR, 99.2 mph EV. Kelly LHB split +0.41, HR risk 0.80. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TB @ BOS - Griffin Jax (R, TB) vs Jake Bennett (L, BOS)",
        "description": "Tail key data: Park boost +3% (stadium -6%, weather +9%). Jax (HR risk 0.62, vs LHB +0.49, vs RHB +0.71). Bennett (HR risk -0.82, vs LHB -1.75, vs RHB -0.30).",
        "rows": [
            row("Wilyer Abreu", "L", "+440", 73, "", ["vs Jax"], """0 HR, 1 near-HR, 94.8 mph EV. Jax LHB split +0.49, HR risk 0.62. park suppresses carry (-6%); limited recent HR events.""", blast="good"),
            row("Jarren Duran", "L", "+600", 81, "", ["vs Jax"], """1 HR, 3 near-HR, 93.1 mph EV. Jax LHB split +0.49, HR risk 0.62. park suppresses carry (-6%).""", blast="good"),
            row("Junior Caminero", "R", "+265", 65, "🚀 ⭐ 🌕 💣", ["vs Bennett"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.7 mph EV. Bennett RHB split -0.30, HR risk -0.82. slight split headwind (-0.30); pitcher suppresses HR (-0.82).""", blast="high"),
            row("Jonathan Aranda", "L", "+680", 58, "", ["vs Bennett"], """0 HR, 1 near-HR, 88.8 mph EV. Bennett LHB split -1.75, HR risk -0.82. tough split lane (-1.75); pitcher suppresses HR (-0.82)."""),
        ],
    },
    {
        "title": "TEX @ ATL - Cal Quantrill (R, TEX) vs Chris Sale (L, ATL)",
        "description": "Tail key data: Park boost +5% (stadium -1%, weather +7%). Quantrill (HR risk 0.26, vs LHB +0.62, vs RHB -0.05). Sale (HR risk -0.63, vs LHB -1.04, vs RHB -0.27).",
        "rows": [
            row("Matt Olson", "L", "+175", 74, "", ["vs Quantrill"], """1 HR, 2 near-HR, 95.9 mph EV. Quantrill LHB split +0.62, HR risk 0.26.""", blast="good"),
            row("Drake Baldwin", "L", "+480", 72, "", ["vs Quantrill"], """1 HR, 1 near-HR, 95.1 mph EV. Quantrill LHB split +0.62, HR risk 0.26.""", blast="good"),
            row("Jake Burger", "R", "+521", 58, "", ["vs Sale"], """1 HR, 1 near-HR, 90.3 mph EV. Sale RHB split -0.27, HR risk -0.63. slight split headwind (-0.27); pitcher suppresses HR (-0.63).""", blast="good"),
            row("Joc Pederson", "L", "N/A", 58, "🚀", ["vs Sale"], """0 HR, 1 near-HR, 101.5 mph EV. Sale LHB split -1.04, HR risk -0.63. tough split lane (-1.04); pitcher suppresses HR (-0.63).""", blast="good"),
            row("Brandon Nimmo", "L", "+720", 58, "", ["vs Sale"], """1 HR, 1 near-HR, 88.5 mph EV. Sale LHB split -1.04, HR risk -0.63. tough split lane (-1.04); pitcher suppresses HR (-0.63).""", blast="good"),
            row("Justin Foscue", "R", "+790", 69, "🌕 💣", ["vs Sale"], """3 HR, 3 near-HR, 89.6 mph EV. Sale RHB split -0.27, HR risk -0.63. slight split headwind (-0.27); pitcher suppresses HR (-0.63).""", blast="high"),
        ],
    },
    {
        "title": "WSH @ ATH - Cade Cavalli (R, WSH) vs Gage Jump (L, ATH)",
        "description": "Tail key data: Park boost +33% (stadium +30%, weather +3%). Cavalli (HR risk -0.45, vs LHB -0.07, vs RHB -0.75). Jump (HR risk -0.02, vs LHB -0.21, vs RHB +0.07).",
        "rows": [
            row("Shea Langeliers", "R", "+320", 58, "⭐", ["vs Cavalli"], """Worst Pickz Favorite. 0 HR, 95.0 mph EV. Cavalli RHB split -0.75, HR risk -0.45. tough split lane (-0.75); pitcher suppresses HR (-0.45).""", blast="good"),
            row("Tyler Soderstrom", "L", "+471", 65, "", ["vs Cavalli"], """1 HR, 1 near-HR, 92.8 mph EV. Cavalli LHB split -0.07, HR risk -0.45. slight split headwind (-0.07); pitcher suppresses HR (-0.45).""", blast="good"),
            row("James Wood", "L", "+306", 66, "", ["vs Jump"], """1 HR, 1 near-HR, 91.1 mph EV. Jump LHB split -0.21, HR risk -0.02. slight split headwind (-0.21); pitcher risk below avg (-0.02).""", blast="good"),
            row("CJ Abrams", "L", "+484", 62, "", ["vs Jump"], """1 HR, 1 near-HR, 87.5 mph EV. Jump LHB split -0.21, HR risk -0.02. slight split headwind (-0.21); pitcher risk below avg (-0.02).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-17")

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
