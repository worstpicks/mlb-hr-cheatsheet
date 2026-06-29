#!/usr/bin/env python3
"""Generate games[] block for 2026-06-29 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Andrew Benintendi (L)",
    "Ben Rice (L)",
    "Bryce Harper (L)",
    "Joc Pederson (L)",
    "Ketel Marte (S)",
    "Max Muncy (L)",
    "Nick Kurtz (L)",
    "Pete Alonso (R)",
    "Pete Crow-Armstrong (L)",
    "Riley Greene (L)",
    "Willson Contreras (R)",
}

GEMS = {
    "Coby Mayo (R)",
    "J.T. Realmuto (R)",
    "Max Kepler (L)",
    "Nate Eaton (R)",
}

PLAYER_TEAMS = {
    "Andrew Benintendi (L)": "CWS",
    "Ben Rice (L)": "NYY",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Cam Smith (R)": "HOU",
    "Christian Walker (R)": "HOU",
    "Coby Mayo (R)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Curtis Mead (R)": "WSH",
    "David Fry (R)": "CLE",
    "Dominic Canzone (L)": "SEA",
    "Elly De La Cruz (S)": "CIN",
    "Endy Rodriguez (S)": "PIT",
    "Eric Wagaman (R)": "NYM",
    "Esmerlyn Valdez (R)": "PIT",
    "Esteury Ruiz (R)": "MIA",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Heliot Ramos (R)": "SF",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "J.T. Realmuto (R)": "PHI",
    "Jackson Chourio (R)": "MIL",
    "Jackson Holliday (L)": "BAL",
    "Jackson Merrill (L)": "SD",
    "James Wood (L)": "WSH",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Jorge Soler (R)": "LAA",
    "Juan Soto (L)": "NYM",
    "Justin Foscue (R)": "TEX",
    "Kazuma Okamoto (R)": "TOR",
    "Kerry Carpenter (L)": "DET",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Lawrence Butler (L)": "ATH",
    "Luke Raley (L)": "SEA",
    "Max Kepler (L)": "ARI",
    "Max Muncy (L)": "LAD",
    "Michael Conforto (L)": "CHC",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Mitch Garver (R)": "SEA",
    "Mookie Betts (R)": "LAD",
    "Nate Eaton (R)": "BOS",
    "Nick Kurtz (L)": "ATH",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Seiya Suzuki (R)": "CHC",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Steer (R)": "CIN",
    "Spencer Torkelson (R)": "DET",
    "Ty France (R)": "SD",
    "Tyler O'Neill (R)": "BAL",
    "Tyler Stephenson (R)": "CIN",
    "Willi Castro (S)": "COL",
    "William Contreras (R)": "MIL",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Yohendrick Pinango (L)": "TOR",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("DET @ NYY", "Weathers"),
    ("LAA @ SEA", "Johnson"),
    ("MIN @ HOU", "Matthews"),
    ("PIT @ PHI", "Nola"),
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
        "title": "CIN @ MIL - Nick Lodolo (L, CIN) vs Robert Gasser (L, MIL)",
        "description": "Tail key data: Park boost +16% (stadium +9%, weather +7%). Lodolo (HR risk -0.19, vs LHB -1.04, vs RHB +0.28). Gasser (HR risk 0.47, vs LHB +0.18, vs RHB +0.40).",
        "rows": [
            row("Jackson Chourio", "R", "+389", 87, "🌕 💣", ["vs Lodolo"], """2 HR, 2 near-HR, 96.6 mph EV. Lodolo RHB split +0.28, HR risk -0.19. pitcher risk below avg (-0.19).""", blast="high"),
            row("William Contreras", "R", "+456", 74, "", ["vs Lodolo"], """0 HR, 1 near-HR, 96.5 mph EV. Lodolo RHB split +0.28, HR risk -0.19. pitcher risk below avg (-0.19); limited recent HR events.""", blast="good"),
            row("Spencer Steer", "R", "+450", 82, "🌕 💣", ["vs Gasser"], """2 HR, 3 near-HR, 90.3 mph EV. Gasser RHB split +0.40, HR risk 0.47.""", blast="high"),
            row("Tyler Stephenson", "R", "+570", 62, "", ["vs Gasser"], """0 HR, 88.2 mph EV. Gasser RHB split +0.40, HR risk 0.47. limited recent HR events."""),
            row("Elly De La Cruz", "S", "+400", 71, "", ["vs Gasser"], """0 HR, 94.7 mph EV. Gasser RHB split +0.40, HR risk 0.47. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ BAL - Sean Burke (R, CWS) vs Shane Baz (R, BAL)",
        "description": "Tail key data: Park boost data unavailable. Burke (HR risk 0.36, vs LHB +0.54, vs RHB -0.57). Baz (HR risk -0.54, vs LHB -0.15, vs RHB -0.64).",
        "rows": [
            row("Pete Alonso", "R", "+282", 81, "⭐ 🌕 💣", ["vs Burke"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 89.4 mph EV. Burke RHB split -0.57, HR risk 0.36. tough split lane (-0.57).""", blast="high"),
            row("Coby Mayo", "R", "+431", 69, "💎", ["vs Burke"], """Worst Pickz Hidden Gem. 0 HR, 93.0 mph EV. Burke RHB split -0.57, HR risk 0.36. tough split lane (-0.57); limited recent HR events.""", blast="good"),
            row("Jackson Holliday", "L", "+630", 64, "", ["vs Burke"], """0 HR, 90.2 mph EV. Burke LHB split +0.54, HR risk 0.36. limited recent HR events."""),
            row("Tyler O'Neill", "R", "N/A", 71, "", ["vs Burke"], """0 HR, 1 near-HR, 93.1 mph EV. Burke RHB split -0.57, HR risk 0.36. tough split lane (-0.57); limited recent HR events.""", blast="good"),
            row("Andrew Benintendi", "L", "+461", 92, "⭐ 🌕 💣", ["vs Baz"], """Worst Pickz Favorite. 3 HR, 2 near-HR, 97.9 mph EV. Baz LHB split -0.15, HR risk -0.54. slight split headwind (-0.15); pitcher suppresses HR (-0.54).""", blast="high"),
            row("Miguel Vargas", "R", "+347", 76, "", ["vs Baz"], """1 HR, 2 near-HR, 91.6 mph EV. Baz RHB split -0.64, HR risk -0.54. tough split lane (-0.64); pitcher suppresses HR (-0.54).""", blast="good"),
        ],
    },
    {
        "title": "DET @ NYY - Casey Mize (R, DET) vs Ryan Weathers 🧤 (L, NYY)",
        "description": "Tail key data: Park boost +12% (stadium +4%, weather +8%). Mize (HR risk -0.76, vs LHB -0.37, vs RHB -0.71). Weathers 🧤 (HR risk 1.32, vs LHB +1.47, vs RHB +0.88).",
        "rows": [
            row("Ben Rice", "L", "+273", 98, "⭐ 🌕 💣", ["vs Mize"], """Worst Pickz Favorite. 3 HR, 6 near-HR, 98.2 mph EV. Mize LHB split -0.37, HR risk -0.76. slight split headwind (-0.37); pitcher suppresses HR (-0.76).""", blast="high"),
            row("Jazz Chisholm Jr.", "L", "+416", 85, "🌕 💣", ["vs Mize"], """2 HR, 3 near-HR, 92.9 mph EV. Mize LHB split -0.37, HR risk -0.76. slight split headwind (-0.37); pitcher suppresses HR (-0.76).""", blast="high"),
            row("Riley Greene", "L", "+522", 78, "🚀 ⭐", ["vs Weathers"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 101.4 mph EV. Weathers LHB split +1.47, HR risk 1.32. limited recent HR events.""", blast="good"),
            row("Spencer Torkelson", "R", "+364", 65, "", ["vs Weathers"], """0 HR, 91.2 mph EV. Weathers RHB split +0.88, HR risk 1.32. limited recent HR events."""),
            row("Kerry Carpenter", "L", "N/A", 64, "", ["vs Weathers"], """0 HR, 1 near-HR, 88.1 mph EV. Weathers LHB split +1.47, HR risk 1.32. limited recent HR events."""),
        ],
    },
    {
        "title": "LAA @ SEA - Ryan Johnson 🧤 (R, LAA) vs George Kirby (R, SEA)",
        "description": "Tail key data: Park boost +4% (stadium +1%, weather +3%). Johnson 🧤 (HR risk 1.09, vs LHB +0.31, vs RHB +1.55). Kirby (HR risk -0.20, vs LHB -0.20, vs RHB +0.02).",
        "rows": [
            row("Dominic Canzone", "L", "+360", 80, "🚀", ["vs Johnson"], """0 HR, 2 near-HR, 102.9 mph EV. Johnson LHB split +0.31, HR risk 1.09.""", blast="good"),
            row("Luke Raley", "L", "+474", 73, "", ["vs Johnson"], """0 HR, 1 near-HR, 95.0 mph EV. Johnson LHB split +0.31, HR risk 1.09. limited recent HR events.""", blast="good"),
            row("Mitch Garver", "R", "N/A", 74, "", ["vs Johnson"], """1 HR, 1 near-HR, 91.7 mph EV. Johnson RHB split +1.55, HR risk 1.09.""", blast="good"),
            row("Zach Neto", "R", "+589", 84, "🌕 💣", ["vs Kirby"], """2 HR, 3 near-HR, 91.8 mph EV. Kirby RHB split +0.02, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="high"),
            row("Jo Adell", "R", "+600", 74, "", ["vs Kirby"], """1 HR, 2 near-HR, 90.0 mph EV. Kirby RHB split +0.02, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="good"),
            row("Jorge Soler", "R", "+670", 78, "🌕 💣", ["vs Kirby"], """2 HR, 2 near-HR, 87.5 mph EV. Kirby RHB split +0.02, HR risk -0.20. pitcher risk below avg (-0.20); lighter EV form (87.5 mph).""", blast="high"),
        ],
    },
    {
        "title": "LAD @ ATH - Eric Lauer (L, LAD) vs Gage Jump (L, ATH)",
        "description": "Tail key data: Park boost +39% (stadium +32%, weather +7%). Lauer (HR risk 0.81, vs LHB +1.14, vs RHB +0.63). Jump (HR risk -1.92, vs LHB -1.06, vs RHB -1.64).",
        "rows": [
            row("Nick Kurtz", "L", "+240", 75, "⭐", ["vs Lauer"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 90.9 mph EV. Lauer LHB split +1.14, HR risk 0.81.""", blast="good"),
            row("Shea Langeliers", "R", "+210", 69, "", ["vs Lauer"], """0 HR, 93.0 mph EV. Lauer RHB split +0.63, HR risk 0.81. limited recent HR events.""", blast="good"),
            row("Lawrence Butler", "L", "+560", 64, "", ["vs Lauer"], """0 HR, 90.3 mph EV. Lauer LHB split +1.14, HR risk 0.81. limited recent HR events."""),
            row("Shohei Ohtani", "L", "+240", 80, "", ["vs Jump"], """1 HR, 1 near-HR, 98.4 mph EV. Jump LHB split -1.06, HR risk -1.92. tough split lane (-1.06); pitcher suppresses HR (-1.92).""", blast="good"),
            row("Mookie Betts", "R", "+430", 68, "", ["vs Jump"], """0 HR, 92.1 mph EV. Jump RHB split -1.64, HR risk -1.92. tough split lane (-1.64); pitcher suppresses HR (-1.92).""", blast="good"),
            row("Max Muncy", "L", "+495", 70, "⭐", ["vs Jump"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 86.9 mph EV. Jump LHB split -1.06, HR risk -1.92. tough split lane (-1.06); pitcher suppresses HR (-1.92).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ COL - Sandy Alcantara (R, MIA) vs Sean Sullivan (L, COL)",
        "description": "Tail key data: Park boost +20% (stadium +22%, weather -1%). Alcantara (HR risk -0.82, vs LHB -0.47, vs RHB -0.72). Home starter risk unavailable.",
        "rows": [
            row("Hunter Goodman", "R", "+294", 88, "🌕 💣", ["vs Alcantara"], """3 HR, 4 near-HR, 89.6 mph EV. Alcantara RHB split -0.72, HR risk -0.82. tough split lane (-0.72); pitcher suppresses HR (-0.82).""", blast="high"),
            row("Mickey Moniak", "L", "+325", 62, "", ["vs Alcantara"], """0 HR, 88.5 mph EV. Alcantara LHB split -0.47, HR risk -0.82. tough split lane (-0.47); pitcher suppresses HR (-0.82)."""),
            row("Willi Castro", "S", "+527", 77, "", ["vs Alcantara"], """1 HR, 1 near-HR, 95.0 mph EV. Alcantara RHB split -0.72, HR risk -0.82. tough split lane (-0.72); pitcher suppresses HR (-0.82).""", blast="good"),
            row("Esteury Ruiz", "R", "+700", 78, "🌕 💣", ["vs Sullivan"], """2 HR, 2 near-HR, 86.1 mph EV. Sullivan split/risk data unavailable. limited split/risk sample; lighter EV form (86.1 mph).""", blast="high"),
            row("Heriberto Hernandez", "R", "+372", 75, "", ["vs Sullivan"], """1 HR, 1 near-HR, 93.4 mph EV. Sullivan split/risk data unavailable. limited split/risk sample.""", blast="good"),
        ],
    },
    {
        "title": "MIN @ HOU - Zebby Matthews 🧤 (R, MIN) vs Peter Lambert (R, HOU)",
        "description": "Tail key data: Park boost +4% (stadium +5%, weather +0%). Matthews 🧤 (HR risk 1.03, vs LHB +1.01, vs RHB +0.54). Lambert (HR risk 0.01, vs LHB -0.84, vs RHB +0.86).",
        "rows": [
            row("Yordan Alvarez", "L", "+226", 73, "", ["vs Matthews"], """1 HR, 1 near-HR, 90.8 mph EV. Matthews LHB split +1.01, HR risk 1.03.""", blast="good"),
            row("Christian Walker", "R", "+359", 62, "", ["vs Matthews"], """0 HR, 87.5 mph EV. Matthews RHB split +0.54, HR risk 1.03. limited recent HR events; lighter EV form (87.5 mph)."""),
            row("Cam Smith", "R", "+690", 75, "", ["vs Matthews"], """1 HR, 1 near-HR, 93.1 mph EV. Matthews RHB split +0.54, HR risk 1.03.""", blast="good"),
            row("Byron Buxton", "R", "+226", 82, "🌕 💣", ["vs Lambert"], """2 HR, 3 near-HR, 89.7 mph EV. Lambert RHB split +0.86, HR risk 0.01.""", blast="high"),
            row("Kody Clemens", "L", "+413", 78, "", ["vs Lambert"], """1 HR, 3 near-HR, 92.1 mph EV. Lambert LHB split -0.84, HR risk 0.01. tough split lane (-0.84).""", blast="good"),
        ],
    },
    {
        "title": "NYM @ TOR - Sean Manaea (L, NYM) vs Trey Yesavage (R, TOR)",
        "description": "Tail key data: Park boost +7% (stadium +6%, weather +0%). Manaea (HR risk -0.11, vs LHB -0.36, vs RHB +0.23). Yesavage (HR risk -0.35, vs LHB -0.36, vs RHB -0.08).",
        "rows": [
            row("Kazuma Okamoto", "R", "+350", 74, "", ["vs Manaea"], """1 HR, 1 near-HR, 92.1 mph EV. Manaea RHB split +0.23, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="good"),
            row("Yohendrick Pinango", "L", "N/A", 70, "", ["vs Manaea"], """0 HR, 1 near-HR, 92.3 mph EV. Manaea LHB split -0.36, HR risk -0.11. slight split headwind (-0.36); pitcher risk below avg (-0.11).""", blast="good"),
            row("Francisco Lindor", "S", "+470", 89, "🌕 💣", ["vs Yesavage"], """2 HR, 2 near-HR, 99.0 mph EV. Yesavage RHB split -0.08, HR risk -0.35. slight split headwind (-0.08); pitcher risk below avg (-0.35).""", blast="high"),
            row("Juan Soto", "L", "+343", 72, "", ["vs Yesavage"], """0 HR, 1 near-HR, 94.0 mph EV. Yesavage LHB split -0.36, HR risk -0.35. slight split headwind (-0.36); pitcher risk below avg (-0.35).""", blast="good"),
            row("Francisco Alvarez", "R", "+516", 76, "", ["vs Yesavage"], """0 HR, 99.5 mph EV. Yesavage RHB split -0.08, HR risk -0.35. slight split headwind (-0.08); pitcher risk below avg (-0.35).""", blast="good"),
            row("Eric Wagaman", "R", "N/A", 62, "", ["vs Yesavage"], """0 HR, 0.0 mph EV. Yesavage RHB split -0.08, HR risk -0.35. slight split headwind (-0.08); pitcher risk below avg (-0.35)."""),
        ],
    },
    {
        "title": "PIT @ PHI - Braxton Ashcraft (R, PIT) vs Aaron Nola 🧤 (R, PHI)",
        "description": "Tail key data: Park boost +27% (stadium +14%, weather +13%). Ashcraft (HR risk -0.92, vs LHB -0.08, vs RHB -1.60). Nola 🧤 (HR risk 1.04, vs LHB +1.31, vs RHB -0.20).",
        "rows": [
            row("Bryce Harper", "L", "+340", 83, "⭐ 🌕 💣", ["vs Ashcraft"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.3 mph EV. Ashcraft LHB split -0.08, HR risk -0.92. slight split headwind (-0.08); pitcher suppresses HR (-0.92).""", blast="high"),
            row("Kyle Schwarber", "L", "+220", 77, "", ["vs Ashcraft"], """1 HR, 1 near-HR, 95.1 mph EV. Ashcraft LHB split -0.08, HR risk -0.92. slight split headwind (-0.08); pitcher suppresses HR (-0.92).""", blast="good"),
            row("J.T. Realmuto", "R", "+870", 83, "🌕 💣 💎", ["vs Ashcraft"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 92.6 mph EV. Ashcraft RHB split -1.60, HR risk -0.92. tough split lane (-1.60); pitcher suppresses HR (-0.92).""", blast="high"),
            row("Brandon Marsh", "L", "+540", 70, "", ["vs Ashcraft"], """0 HR, 1 near-HR, 92.4 mph EV. Ashcraft LHB split -0.08, HR risk -0.92. slight split headwind (-0.08); pitcher suppresses HR (-0.92).""", blast="good"),
            row("Brandon Lowe", "L", "+285", 77, "", ["vs Nola"], """1 HR, 1 near-HR, 94.6 mph EV. Nola LHB split +1.31, HR risk 1.04.""", blast="good"),
            row("Bryan Reynolds", "S", "+431", 84, "", ["vs Nola"], """1 HR, 3 near-HR, 97.7 mph EV. Nola RHB split -0.20, HR risk 1.04. slight split headwind (-0.20).""", blast="good"),
            row("Endy Rodriguez", "S", "+720", 80, "", ["vs Nola"], """1 HR, 1 near-HR, 97.5 mph EV. Nola RHB split -0.20, HR risk 1.04. slight split headwind (-0.20).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+555", 71, "", ["vs Nola"], """0 HR, 1 near-HR, 93.0 mph EV. Nola RHB split -0.20, HR risk 1.04. slight split headwind (-0.20); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "SD @ CHC - Griffin Canning (R, SD) vs Shota Imanaga (L, CHC)",
        "description": "Tail key data: Park boost +47% (stadium -1%, weather +48%). Away starter risk unavailable. Home starter risk unavailable.",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+285", 87, "⭐ 🌕 💣", ["vs Canning"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.8 mph EV. Canning split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Michael Conforto", "L", "N/A", 63, "", ["vs Canning"], """0 HR, 89.0 mph EV. Canning split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
            row("Seiya Suzuki", "R", "+300", 72, "", ["vs Canning"], """1 HR, 1 near-HR, 90.1 mph EV. Canning split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Jackson Merrill", "L", "+366", 66, "", ["vs Imanaga"], """0 HR, 91.7 mph EV. Imanaga split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
            row("Ty France", "R", "+374", 62, "", ["vs Imanaga"], """0 HR, 85.2 mph EV. Imanaga split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
        ],
    },
    {
        "title": "SF @ ARI - Tyler Mahle (R, SF) vs Eduardo Rodriguez (L, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Mahle (HR risk 0.10, vs LHB +0.08, vs RHB +0.09). Rodriguez (HR risk -0.30, vs LHB -0.69, vs RHB +0.12).",
        "rows": [
            row("Ketel Marte", "S", "+390", 75, "⭐", ["vs Mahle"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 97.4 mph EV. Mahle RHB split +0.09, HR risk 0.10. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Corbin Carroll", "L", "+401", 64, "", ["vs Mahle"], """0 HR, 1 near-HR, 87.3 mph EV. Mahle LHB split +0.08, HR risk 0.10. park/weather net drag (-8%); limited recent HR events."""),
            row("Max Kepler", "L", "+620", 78, "💎", ["vs Mahle"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 99.7 mph EV. Mahle LHB split +0.08, HR risk 0.10. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Willy Adames", "R", "+425", 80, "🌕 💣", ["vs Rodriguez"], """2 HR, 3 near-HR, 86.9 mph EV. Rodriguez RHB split +0.12, HR risk -0.30. pitcher risk below avg (-0.30); park/weather net drag (-8%).""", blast="high"),
            row("Heliot Ramos", "R", "+670", 68, "", ["vs Rodriguez"], """0 HR, 92.5 mph EV. Rodriguez RHB split +0.12, HR risk -0.30. pitcher risk below avg (-0.30); park/weather net drag (-8%).""", blast="good"),
            row("Rafael Devers", "L", "+525", 81, "", ["vs Rodriguez"], """1 HR, 2 near-HR, 96.9 mph EV. Rodriguez LHB split -0.69, HR risk -0.30. tough split lane (-0.69); pitcher risk below avg (-0.30).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ CLE - Winston Santos (R, TEX) vs Parker Messick (L, CLE)",
        "description": "Tail key data: Park boost +9% (stadium -3%, weather +12%). Away starter risk unavailable. Messick (HR risk -0.52, vs LHB -0.40, vs RHB -0.35).",
        "rows": [
            row("Rhys Hoskins", "R", "N/A", 62, "", ["vs Santos"], """0 HR, 84.0 mph EV. Santos split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
            row("David Fry", "R", "+620", 70, "", ["vs Santos"], """1 HR, 1 near-HR, 86.8 mph EV. Santos split/risk data unavailable. limited split/risk sample; lighter EV form (86.8 mph).""", blast="good"),
            row("Joc Pederson", "L", "N/A", 78, "🚀 ⭐", ["vs Messick"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 100.6 mph EV. Messick LHB split -0.40, HR risk -0.52. tough split lane (-0.40); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Justin Foscue", "R", "+700", 73, "", ["vs Messick"], """1 HR, 1 near-HR, 90.9 mph EV. Messick RHB split -0.35, HR risk -0.52. slight split headwind (-0.35); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Brandon Nimmo", "L", "+600", 62, "", ["vs Messick"], """0 HR, 88.5 mph EV. Messick LHB split -0.40, HR risk -0.52. tough split lane (-0.40); pitcher suppresses HR (-0.52)."""),
        ],
    },
    {
        "title": "WSH @ BOS - Miles Mikolas (R, WSH) vs Ranger Suarez (L, BOS)",
        "description": "Tail key data: Park boost data unavailable. Mikolas (HR risk 0.42, vs LHB -0.01, vs RHB +0.92). Home starter risk unavailable.",
        "rows": [
            row("Willson Contreras", "R", "N/A", 82, "⭐", ["vs Mikolas"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 91.5 mph EV, 20.0% barrels. Mikolas RHB split +0.92, HR risk 0.42.""", blast="good"),
            row("Wilyer Abreu", "L", "N/A", 76, "", ["vs Mikolas"], """1 HR, 1 near-HR, 89.0 mph EV, 14.0% barrels. Mikolas LHB split -0.01, HR risk 0.42. slight split headwind (-0.01).""", blast="good"),
            row("Nate Eaton", "R", "N/A", 67, "💎", ["vs Mikolas"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 86.0 mph EV, 10.0% barrels. Mikolas RHB split +0.92, HR risk 0.42. limited recent HR events; lighter EV form (86.0 mph)."""),
            row("James Wood", "L", "+475", 70, "", ["vs Suarez"], """0 HR, 93.8 mph EV. Suarez split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("CJ Abrams", "L", "+730", 62, "", ["vs Suarez"], """0 HR, 88.2 mph EV. Suarez split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
            row("Curtis Mead", "R", "+562", 80, "🌕 💣", ["vs Suarez"], """2 HR, 3 near-HR, 86.8 mph EV. Suarez split/risk data unavailable. limited split/risk sample; lighter EV form (86.8 mph).""", blast="high"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-29")

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

    out = ROOT / '_games-0629.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
