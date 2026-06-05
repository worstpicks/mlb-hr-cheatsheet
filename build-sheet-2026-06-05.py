#!/usr/bin/env python3
"""Generate games[] block for 2026-06-05 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Bobby Witt Jr. (R)",
    "Bryan Reynolds (S)",
    "Bryce Eldridge (L)",
    "Colson Montgomery (L)",
    "Dillon Dingler (R)",
    "Heriberto Hernandez (R)",
    "JJ Bleday (L)",
    "Jackson Chourio (R)",
    "Jackson Holliday (L)",
    "Jared Young (L)",
    "Jonathan Aranda (L)",
    "Julio Rodriguez (R)",
    "Kyle Stowers (L)",
    "Lane Thomas (R)",
    "Mike Trout (R)",
    "Pete Crow-Armstrong (L)",
    "Seiya Suzuki (R)",
    "Shea Langeliers (R)",
    "Tyler Soderstrom (L)",
    "Vinnie Pasquantino (L)",
    "Will Smith (R)",
    "Yordan Alvarez (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BAL",
    "Andy Pages (R)": "LAD",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Blaze Alexander (R)": "BAL",
    "Bobby Witt Jr. (R)": "KC",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Carlos Cortes (L)": "ATH",
    "Casey Schmitt (R)": "SF",
    "Cedric Mullins (L)": "TB",
    "Colson Montgomery (L)": "CWS",
    "Corbin Carroll (L)": "ARI",
    "Curtis Mead (R)": "WSH",
    "David Hamilton (L)": "MIL",
    "Dillon Dingler (R)": "DET",
    "Edmundo Sosa (R)": "PHI",
    "Ezequiel Tovar (R)": "COL",
    "Garrett Mitchell (L)": "MIL",
    "Heriberto Hernandez (R)": "MIA",
    "Isaac Paredes (R)": "HOU",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "Jackson Chourio (R)": "MIL",
    "Jackson Holliday (L)": "BAL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jake McCarthy (L)": "COL",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jesus Sanchez (L)": "TOR",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Jose Ramirez (S)": "CLE",
    "Josh Bell (S)": "MIN",
    "Juan Soto (L)": "NYM",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kazuma Okamoto (R)": "TOR",
    "Keibert Ruiz (S)": "WSH",
    "Kerry Carpenter (L)": "DET",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lane Thomas (R)": "KC",
    "Liam Hicks (L)": "MIA",
    "MJ Melendez (L)": "NYM",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Michael Busch (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Nick Kurtz (L)": "ATH",
    "Oneil Cruz (L)": "PIT",
    "Otto Lopez (R)": "MIA",
    "Owen Caissie (L)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rhys Hoskins (R)": "CLE",
    "Rob Refsnyder (R)": "SEA",
    "Ronald Acuna Jr. (R)": "ATL",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Seiya Suzuki (R)": "CHC",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Torkelson (R)": "DET",
    "TJ Rumfield (L)": "COL",
    "Trevor Larnach (L)": "MIN",
    "Tristan Gray (L)": "MIN",
    "Ty France (R)": "SD",
    "Tyler Soderstrom (L)": "ATH",
    "Vaughn Grissom (R)": "LAA",
    "Vinnie Pasquantino (L)": "KC",
    "Wade Meckler (L)": "LAA",
    "Will Benson (L)": "CIN",
    "Will Smith (R)": "LAD",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_PITCHERS = {
    "Feltner",
    "Griffin",
    "Ray",
    "Singer",
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
        "title": "ATH @ HOU - Jack Perkins (R, ATH) vs Peter Lambert (R, HOU)",
        "description": "Tail key data: Park boost +4% (stadium +5%, weather +0%). Perkins (HR risk -0.64, vs LHB -0.97, vs RHB -0.08). Lambert (HR risk -0.66, vs LHB -0.91, vs RHB +0.09).",
        "rows": [
            row("Yordan Alvarez", "L", "N/A", 92, "🚀 ⭐ 🌕 💣", ["vs Perkins"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 100.2 mph EV. Perkins LHB split -0.97, HR risk -0.64. tough split lane (-0.97); pitcher suppresses HR (-0.64).""", blast="high"),
            row("Isaac Paredes", "R", "N/A", 70, "💎", ["vs Perkins"], """1 HR, 1 near-HR, 85.3 mph EV. Perkins RHB split -0.08, HR risk -0.64. slight split headwind (-0.08); pitcher suppresses HR (-0.64).""", blast="good"),
            row("Shea Langeliers", "R", "N/A", 64, "⭐ 💎", ["vs Lambert"], """Worst Pickz Favorite. 0 HR, 89.5 mph EV. Lambert RHB split +0.09, HR risk -0.66. pitcher suppresses HR (-0.66); limited recent HR events."""),
            row("Tyler Soderstrom", "L", "N/A", 75, "⭐ 💎", ["vs Lambert"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 90.8 mph EV. Lambert LHB split -0.91, HR risk -0.66. tough split lane (-0.91); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Nick Kurtz", "L", "N/A", 64, "💎", ["vs Lambert"], """0 HR, 1 near-HR, 85.9 mph EV. Lambert LHB split -0.91, HR risk -0.66. tough split lane (-0.91); pitcher suppresses HR (-0.66)."""),
            row("Carlos Cortes", "L", "N/A", 75, "💎", ["vs Lambert"], """1 HR, 3 near-HR, 89.0 mph EV. Lambert LHB split -0.91, HR risk -0.66. tough split lane (-0.91); pitcher suppresses HR (-0.66).""", blast="good"),
        ],
    },
    {
        "title": "BAL @ TOR - Brandon Young (R, BAL) vs Trey Yesavage (R, TOR)",
        "description": "Tail key data: Park boost +9% (stadium +7%, weather +2%). Young (HR risk -0.18, vs LHB -0.14, vs RHB +0.04). Yesavage (HR risk -1.30, vs LHB -0.87, vs RHB -1.30).",
        "rows": [
            row("Jesus Sanchez", "L", "+307", 81, "💎", ["vs Young"], """1 HR, 2 near-HR, 96.7 mph EV. Young LHB split -0.14, HR risk -0.18. slight split headwind (-0.14); pitcher risk below avg (-0.18).""", blast="good"),
            row("Kazuma Okamoto", "R", "+198", 72, "💎", ["vs Young"], """1 HR, 2 near-HR, 86.8 mph EV. Young RHB split +0.04, HR risk -0.18. pitcher risk below avg (-0.18); lighter EV form (86.8 mph).""", blast="good"),
            row("Pete Alonso", "R", "+165", 86, "🌕 💣", ["vs Yesavage"], """2 HR, 2 near-HR, 95.9 mph EV. Yesavage RHB split -1.30, HR risk -1.30. tough split lane (-1.30); pitcher suppresses HR (-1.30).""", blast="high"),
            row("Blaze Alexander", "R", "N/A", 83, "💎", ["vs Yesavage"], """1 HR, 3 near-HR, 96.6 mph EV. Yesavage RHB split -1.30, HR risk -1.30. tough split lane (-1.30); pitcher suppresses HR (-1.30).""", blast="good"),
            row("Jackson Holliday", "L", "+580", 74, "⭐ 💎", ["vs Yesavage"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.5 mph EV. Yesavage LHB split -0.87, HR risk -1.30. tough split lane (-0.87); pitcher suppresses HR (-1.30).""", blast="good"),
            row("Adley Rutschman", "S", "+340", 68, "💎", ["vs Yesavage"], """0 HR, 92.1 mph EV. Yesavage RHB split -1.30, HR risk -1.30. tough split lane (-1.30); pitcher suppresses HR (-1.30).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ NYY - Sonny Gray (R, BOS) vs Ryan Weathers (R, NYY)",
        "description": "Tail key data: Park boost +7% (stadium +2%, weather +5%). Gray (HR risk -0.71, vs LHB -0.36, vs RHB -0.85). Weathers (HR risk 0.51, vs LHB +0.89, vs RHB +0.33).",
        "rows": [
            row("Ben Rice", "L", "+300", 64, "⭐ 💎", ["vs Gray"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 86.9 mph EV. Gray LHB split -0.36, HR risk -0.71. slight split headwind (-0.36); pitcher suppresses HR (-0.71)."""),
            row("Wilyer Abreu", "L", "+555", 62, "💎", ["vs Weathers"], """0 HR, 86.0 mph EV. Weathers LHB split +0.89, HR risk 0.51. limited recent HR events; lighter EV form (86.0 mph)."""),
            row("Willson Contreras", "R", "+388", 66, "💎", ["vs Weathers"], """0 HR, 1 near-HR, 90.4 mph EV. Weathers RHB split +0.33, HR risk 0.51. limited recent HR events."""),
        ],
    },
    {
        "title": "CIN @ STL - Brady Singer 🧤 (R, CIN) vs Kyle Leahy (R, STL)",
        "description": "Tail key data: Park boost +6% (stadium -10%, weather +16%). Singer 🧤 (HR risk 2.17, vs LHB +2.18, vs RHB +1.17). Leahy (HR risk 0.18, vs LHB +0.79, vs RHB -0.61).",
        "rows": [
            row("Jordan Walker", "R", "+428", 80, "💎", ["vs Singer"], """1 HR, 1 near-HR, 98.0 mph EV. Singer RHB split +1.17, HR risk 2.17. park suppresses carry (-10%).""", blast="good"),
            row("JJ Wetherholt", "L", "+484", 74, "💎", ["vs Singer"], """0 HR, 97.5 mph EV. Singer LHB split +2.18, HR risk 2.17. park suppresses carry (-10%); limited recent HR events.""", blast="good"),
            row("JJ Bleday", "L", "+411", 86, "⭐ 🌕 💣", ["vs Leahy"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 90.1 mph EV. Leahy LHB split +0.79, HR risk 0.18. park suppresses carry (-10%).""", blast="high"),
            row("Will Benson", "L", "N/A", 70, "💎", ["vs Leahy"], """1 HR, 1 near-HR, 84.4 mph EV. Leahy LHB split +0.79, HR risk 0.18. park suppresses carry (-10%); lighter EV form (84.4 mph).""", blast="good"),
            row("Sal Stewart", "R", "+555", 64, "💎", ["vs Leahy"], """0 HR, 90.1 mph EV. Leahy RHB split -0.61, HR risk 0.18. tough split lane (-0.61); park suppresses carry (-10%)."""),
        ],
    },
    {
        "title": "CLE @ TEX - Parker Messick (R, CLE) vs Kumar Rocker (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -10%, weather -1%). Messick (HR risk -0.59, vs LHB -0.81, vs RHB -0.34). Rocker (HR risk -0.35, vs LHB +0.10, vs RHB -0.62).",
        "rows": [
            row("Joc Pederson", "L", "N/A", 76, "🚀 💎", ["vs Messick"], """0 HR, 104.2 mph EV. Messick LHB split -0.81, HR risk -0.59. tough split lane (-0.81); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Justin Foscue", "R", "+960", 84, "🚀 💎", ["vs Messick"], """1 HR, 2 near-HR, 100.5 mph EV. Messick RHB split -0.34, HR risk -0.59. slight split headwind (-0.34); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Jose Ramirez", "S", "+567", 73, "💎", ["vs Rocker"], """1 HR, 1 near-HR, 91.0 mph EV. Rocker RHB split -0.62, HR risk -0.35. tough split lane (-0.62); pitcher risk below avg (-0.35).""", blast="good"),
            row("Kyle Manzardo", "L", "+561", 62, "💎", ["vs Rocker"], """0 HR, 88.3 mph EV. Rocker LHB split +0.10, HR risk -0.35. pitcher risk below avg (-0.35); park/weather net drag (-11%)."""),
            row("Rhys Hoskins", "R", "N/A", 70, "💎", ["vs Rocker"], """1 HR, 1 near-HR, 79.5 mph EV. Rocker RHB split -0.62, HR risk -0.35. tough split lane (-0.62); pitcher risk below avg (-0.35).""", blast="good"),
        ],
    },
    {
        "title": "CWS @ PHI - Anthony Kay (R, CWS) vs Jesus Luzardo (R, PHI)",
        "description": "Tail key data: Park boost data unavailable. Kay (HR risk -0.31, vs LHB -1.35, vs RHB +0.14). Luzardo (HR risk -0.97, vs LHB -0.83, vs RHB -0.76).",
        "rows": [
            row("Edmundo Sosa", "R", "+710", 78, "🌕 💣", ["vs Kay"], """2 HR, 2 near-HR, 88.5 mph EV. Kay RHB split +0.14, HR risk -0.31. pitcher risk below avg (-0.31).""", blast="high"),
            row("Bryce Harper", "L", "+410", 73, "💎", ["vs Kay"], """0 HR, 96.8 mph EV. Kay LHB split -1.35, HR risk -0.31. tough split lane (-1.35); pitcher risk below avg (-0.31).""", blast="good"),
            row("Kyle Schwarber", "L", "+210", 83, "🌕 💣", ["vs Kay"], """2 HR, 2 near-HR, 93.0 mph EV. Kay LHB split -1.35, HR risk -0.31. tough split lane (-1.35); pitcher risk below avg (-0.31).""", blast="high"),
            row("Colson Montgomery", "L", "+233", 76, "⭐ 💎", ["vs Luzardo"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 95.5 mph EV. Luzardo LHB split -0.83, HR risk -0.97. tough split lane (-0.83); pitcher suppresses HR (-0.97).""", blast="good"),
            row("Miguel Vargas", "R", "+410", 74, "💎", ["vs Luzardo"], """0 HR, 97.6 mph EV. Luzardo RHB split -0.76, HR risk -0.97. tough split lane (-0.76); pitcher suppresses HR (-0.97).""", blast="good"),
        ],
    },
    {
        "title": "KC @ MIN - Michael Wacha (R, KC) vs Zebby Matthews (R, MIN)",
        "description": "Tail key data: Park boost +0% (stadium -7%, weather +6%). Wacha (HR risk -0.38, vs LHB -0.34, vs RHB -0.04). Matthews (HR risk 0.97, vs LHB +1.03, vs RHB +0.60).",
        "rows": [
            row("Byron Buxton", "R", "+272", 74, "💎", ["vs Wacha"], """1 HR, 1 near-HR, 92.0 mph EV. Wacha RHB split -0.04, HR risk -0.38. slight split headwind (-0.04); pitcher risk below avg (-0.38).""", blast="good"),
            row("Trevor Larnach", "L", "+910", 70, "💎", ["vs Wacha"], """1 HR, 1 near-HR, 85.2 mph EV. Wacha LHB split -0.34, HR risk -0.38. slight split headwind (-0.34); pitcher risk below avg (-0.38).""", blast="good"),
            row("Kody Clemens", "L", "+534", 80, "💎", ["vs Wacha"], """1 HR, 3 near-HR, 93.8 mph EV. Wacha LHB split -0.34, HR risk -0.38. slight split headwind (-0.34); pitcher risk below avg (-0.38).""", blast="good"),
            row("Tristan Gray", "L", "+810", 79, "💎", ["vs Wacha"], """1 HR, 3 near-HR, 93.3 mph EV. Wacha LHB split -0.34, HR risk -0.38. slight split headwind (-0.34); pitcher risk below avg (-0.38).""", blast="good"),
            row("Josh Bell", "S", "+600", 72, "💎", ["vs Wacha"], """0 HR, 1 near-HR, 93.9 mph EV. Wacha RHB split -0.04, HR risk -0.38. slight split headwind (-0.04); pitcher risk below avg (-0.38).""", blast="good"),
            row("Salvador Perez", "R", "+526", 66, "💎", ["vs Matthews"], """0 HR, 1 near-HR, 89.6 mph EV. Matthews RHB split +0.60, HR risk 0.97. park suppresses carry (-7%); limited recent HR events."""),
            row("Vinnie Pasquantino", "L", "+488", 72, "⭐ 💎", ["vs Matthews"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 85.8 mph EV. Matthews LHB split +1.03, HR risk 0.97. park suppresses carry (-7%); lighter EV form (85.8 mph).""", blast="good"),
            row("Bobby Witt Jr.", "R", "+476", 79, "⭐ 💎", ["vs Matthews"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.6 mph EV. Matthews RHB split +0.60, HR risk 0.97. park suppresses carry (-7%).""", blast="good"),
            row("Lane Thomas", "R", "N/A", 73, "⭐ 💎", ["vs Matthews"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 89.0 mph EV. Matthews RHB split +0.60, HR risk 0.97. park suppresses carry (-7%).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ LAD - Reid Detmers (R, LAA) vs Roki Sasaki (R, LAD)",
        "description": "Tail key data: Park boost +18% (stadium +18%, weather +0%). Away starter risk unavailable. Sasaki (HR risk 0.43, vs LHB +0.30, vs RHB +0.58).",
        "rows": [
            row("Will Smith", "R", "N/A", 74, "⭐ 💎", ["vs Detmers"], """Worst Pickz Favorite. 0 HR, 97.7 mph EV. Detmers split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Andy Pages", "R", "N/A", 62, "💎", ["vs Detmers"], """0 HR, 86.9 mph EV. Detmers split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
            row("Shohei Ohtani", "L", "N/A", 72, "💎", ["vs Detmers"], """0 HR, 95.8 mph EV. Detmers split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Mookie Betts", "R", "N/A", 70, "💎", ["vs Detmers"], """1 HR, 1 near-HR, 88.1 mph EV. Detmers split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Zach Neto", "R", "N/A", 75, "💎", ["vs Sasaki"], """1 HR, 1 near-HR, 92.8 mph EV. Sasaki RHB split +0.58, HR risk 0.43.""", blast="good"),
            row("Wade Meckler", "L", "N/A", 74, "💎", ["vs Sasaki"], """1 HR, 3 near-HR, 85.8 mph EV. Sasaki LHB split +0.30, HR risk 0.43. lighter EV form (85.8 mph).""", blast="good"),
            row("Vaughn Grissom", "R", "N/A", 77, "💎", ["vs Sasaki"], """1 HR, 2 near-HR, 93.3 mph EV. Sasaki RHB split +0.58, HR risk 0.43.""", blast="good"),
            row("Mike Trout", "R", "N/A", 75, "⭐ 💎", ["vs Sasaki"], """Worst Pickz Favorite. 0 HR, 99.2 mph EV. Sasaki RHB split +0.58, HR risk 0.43. limited recent HR events.""", blast="good"),
            row("Jo Adell", "R", "N/A", 85, "🌕 💣", ["vs Sasaki"], """2 HR, 2 near-HR, 94.9 mph EV. Sasaki RHB split +0.58, HR risk 0.43.""", blast="high"),
        ],
    },
    {
        "title": "MIL @ COL - Brandon Sproat (R, MIL) vs Ryan Feltner 🧤 (R, COL)",
        "description": "Tail key data: Park boost +27% (stadium +20%, weather +6%). Sproat (HR risk 0.18, vs LHB -0.23, vs RHB +0.62). Feltner 🧤 (HR risk 1.09, vs LHB +0.68, vs RHB +1.15).",
        "rows": [
            row("Willi Castro", "S", "+620", 79, "💎", ["vs Sproat"], """1 HR, 2 near-HR, 94.6 mph EV. Sproat RHB split +0.62, HR risk 0.18.""", blast="good"),
            row("Ezequiel Tovar", "R", "+526", 70, "💎", ["vs Sproat"], """1 HR, 1 near-HR, 81.3 mph EV. Sproat RHB split +0.62, HR risk 0.18. lighter EV form (81.3 mph).""", blast="good"),
            row("TJ Rumfield", "L", "+471", 80, "🌕 💣", ["vs Sproat"], """2 HR, 3 near-HR, 86.0 mph EV. Sproat LHB split -0.23, HR risk 0.18. slight split headwind (-0.23); lighter EV form (86.0 mph).""", blast="high"),
            row("Jake McCarthy", "L", "+610", 78, "🌕 💣", ["vs Sproat"], """2 HR, 2 near-HR, 86.7 mph EV. Sproat LHB split -0.23, HR risk 0.18. slight split headwind (-0.23); lighter EV form (86.7 mph).""", blast="high"),
            row("Jackson Chourio", "R", "+399", 96, "⭐ 🌕 💣", ["vs Feltner"], """Worst Pickz Favorite. 3 HR, 5 near-HR, 96.4 mph EV. Feltner RHB split +1.15, HR risk 1.09.""", blast="high"),
            row("Jake Bauers", "L", "+375", 73, "💎", ["vs Feltner"], """1 HR, 1 near-HR, 91.4 mph EV. Feltner LHB split +0.68, HR risk 1.09.""", blast="good"),
            row("Garrett Mitchell", "L", "+505", 78, "💎", ["vs Feltner"], """1 HR, 1 near-HR, 96.0 mph EV. Feltner LHB split +0.68, HR risk 1.09.""", blast="good"),
            row("David Hamilton", "L", "+600", 84, "🌕 💣", ["vs Feltner"], """2 HR, 2 near-HR, 94.3 mph EV. Feltner LHB split +0.68, HR risk 1.09.""", blast="high"),
        ],
    },
    {
        "title": "NYM @ SD - Christian Scott (R, NYM) vs Michael King (R, SD)",
        "description": "Tail key data: Park boost -2% (stadium -4%, weather +2%). Scott (HR risk -1.33, vs LHB -1.26, vs RHB -0.49). King (HR risk -0.27, vs LHB +0.26, vs RHB -0.98).",
        "rows": [
            row("Manny Machado", "R", "+502", 77, "💎", ["vs Scott"], """1 HR, 2 near-HR, 92.7 mph EV. Scott RHB split -0.49, HR risk -1.33. tough split lane (-0.49); pitcher suppresses HR (-1.33).""", blast="good"),
            row("Jackson Merrill", "L", "+570", 62, "💎", ["vs Scott"], """0 HR, 79.3 mph EV. Scott LHB split -1.26, HR risk -1.33. tough split lane (-1.26); pitcher suppresses HR (-1.33)."""),
            row("Ty France", "R", "+630", 77, "💎", ["vs Scott"], """1 HR, 2 near-HR, 93.4 mph EV. Scott RHB split -0.49, HR risk -1.33. tough split lane (-0.49); pitcher suppresses HR (-1.33).""", blast="good"),
            row("Jared Young", "L", "+570", 82, "🚀 ⭐ 💎", ["vs King"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 101.0 mph EV. King LHB split +0.26, HR risk -0.27. pitcher risk below avg (-0.27).""", blast="good"),
            row("Juan Soto", "L", "+340", 84, "🌕 💣", ["vs King"], """2 HR, 2 near-HR, 93.6 mph EV. King LHB split +0.26, HR risk -0.27. pitcher risk below avg (-0.27).""", blast="high"),
            row("MJ Melendez", "L", "+337", 78, "💎", ["vs King"], """1 HR, 1 near-HR, 95.6 mph EV. King LHB split +0.26, HR risk -0.27. pitcher risk below avg (-0.27).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ ATL - Mitch Keller (R, PIT) vs Martin Perez (R, ATL)",
        "description": "Tail key data: Park boost -5% (stadium -2%, weather -3%). Keller (HR risk -0.36, vs LHB +0.24, vs RHB -1.22). Perez (HR risk 0.15, vs LHB +0.35, vs RHB -0.03).",
        "rows": [
            row("Matt Olson", "L", "+360", 69, "💎", ["vs Keller"], """0 HR, 93.3 mph EV. Keller LHB split +0.24, HR risk -0.36. pitcher risk below avg (-0.36); park/weather net drag (-5%).""", blast="good"),
            row("Michael Harris II", "L", "+360", 90, "🌕 💣", ["vs Keller"], """3 HR, 3 near-HR, 94.2 mph EV. Keller LHB split +0.24, HR risk -0.36. pitcher risk below avg (-0.36); park/weather net drag (-5%).""", blast="high"),
            row("Ronald Acuna Jr.", "R", "+470", 88, "🌕 💣", ["vs Keller"], """3 HR, 3 near-HR, 91.5 mph EV. Keller RHB split -1.22, HR risk -0.36. tough split lane (-1.22); pitcher risk below avg (-0.36).""", blast="high"),
            row("Austin Riley", "R", "+540", 67, "💎", ["vs Keller"], """0 HR, 1 near-HR, 91.3 mph EV. Keller RHB split -1.22, HR risk -0.36. tough split lane (-1.22); pitcher risk below avg (-0.36)."""),
            row("Bryan Reynolds", "S", "+490", 84, "🚀 ⭐ 💎", ["vs Perez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 100.9 mph EV. Perez RHB split -0.03, HR risk 0.15. slight split headwind (-0.03); park/weather net drag (-5%).""", blast="good"),
            row("Oneil Cruz", "L", "+360", 76, "🚀 💎", ["vs Perez"], """0 HR, 108.6 mph EV. Perez LHB split +0.35, HR risk 0.15. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "SEA @ DET - Bryan Woo (R, SEA) vs Framber Valdez (R, DET)",
        "description": "Tail key data: Park boost -6% (stadium -10%, weather +5%). Woo (HR risk -0.79, vs LHB -0.44, vs RHB -0.86). Valdez (HR risk 0.14, vs LHB +0.36, vs RHB +0.10).",
        "rows": [
            row("Dillon Dingler", "R", "+660", 77, "⭐ 💎", ["vs Woo"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.2 mph EV. Woo RHB split -0.86, HR risk -0.79. tough split lane (-0.86); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Spencer Torkelson", "R", "+577", 75, "💎", ["vs Woo"], """1 HR, 2 near-HR, 90.6 mph EV. Woo RHB split -0.86, HR risk -0.79. tough split lane (-0.86); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Kerry Carpenter", "L", "+350", 74, "💎", ["vs Woo"], """1 HR, 1 near-HR, 92.5 mph EV. Woo LHB split -0.44, HR risk -0.79. tough split lane (-0.44); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Julio Rodriguez", "R", "+426", 95, "⭐ 🌕 💣", ["vs Valdez"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 99.2 mph EV. Valdez RHB split +0.10, HR risk 0.14. park/weather net drag (-6%).""", blast="high"),
            row("Rob Refsnyder", "R", "+710", 83, "💎", ["vs Valdez"], """1 HR, 2 near-HR, 99.2 mph EV. Valdez RHB split +0.10, HR risk 0.14. park/weather net drag (-6%).""", blast="good"),
        ],
    },
    {
        "title": "SF @ CHC - Robbie Ray 🧤 (R, SF) vs Edward Cabrera (R, CHC)",
        "description": "Tail key data: Park boost +51% (stadium -2%, weather +53%). Ray 🧤 (HR risk 1.06, vs LHB -0.67, vs RHB +1.47). Cabrera (HR risk 0.69, vs LHB +0.26, vs RHB +1.28).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+410", 83, "⭐ 💎", ["vs Ray"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 96.6 mph EV. Ray LHB split -0.67, HR risk 1.06. tough split lane (-0.67).""", blast="good"),
            row("Seiya Suzuki", "R", "+414", 71, "⭐ 💎", ["vs Ray"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 92.6 mph EV. Ray RHB split +1.47, HR risk 1.06. limited recent HR events.""", blast="good"),
            row("Michael Busch", "L", "+373", 78, "🌕 💣", ["vs Ray"], """2 HR, 2 near-HR, 87.6 mph EV. Ray LHB split -0.67, HR risk 1.06. tough split lane (-0.67); lighter EV form (87.6 mph).""", blast="high"),
            row("Bryce Eldridge", "L", "N/A", 87, "⭐ 🌕 💣", ["vs Cabrera"], """Worst Pickz Favorite. 1 HR, 4 near-HR, 96.7 mph EV. Cabrera LHB split +0.26, HR risk 0.69.""", blast="high"),
            row("Casey Schmitt", "R", "N/A", 71, "💎", ["vs Cabrera"], """1 HR, 1 near-HR, 88.7 mph EV. Cabrera RHB split +1.28, HR risk 0.69.""", blast="good"),
        ],
    },
    {
        "title": "TB @ MIA - Drew Rasmussen (R, TB) vs Ryan Gusto (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -14%, weather +1%). Rasmussen (HR risk -0.17, vs LHB +0.21, vs RHB -0.38). Gusto (HR risk -0.25, vs LHB +0.35, vs RHB -0.28).",
        "rows": [
            row("Heriberto Hernandez", "R", "N/A", 78, "⭐ 💎", ["vs Rasmussen"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.5 mph EV. Rasmussen RHB split -0.38, HR risk -0.17. slight split headwind (-0.38); pitcher risk below avg (-0.17).""", blast="good"),
            row("Kyle Stowers", "L", "+630", 75, "⭐ 💎", ["vs Rasmussen"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.8 mph EV. Rasmussen LHB split +0.21, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-13%).""", blast="good"),
            row("Otto Lopez", "R", "+1060", 78, "💎", ["vs Rasmussen"], """1 HR, 2 near-HR, 94.5 mph EV. Rasmussen RHB split -0.38, HR risk -0.17. slight split headwind (-0.38); pitcher risk below avg (-0.17).""", blast="good"),
            row("Owen Caissie", "L", "+1160", 70, "💎", ["vs Rasmussen"], """0 HR, 94.1 mph EV. Rasmussen LHB split +0.21, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-13%).""", blast="good"),
            row("Liam Hicks", "L", "+940", 70, "💎", ["vs Rasmussen"], """1 HR, 1 near-HR, 83.4 mph EV. Rasmussen LHB split +0.21, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-13%).""", blast="good"),
            row("Jonathan Aranda", "L", "+568", 86, "⭐ 💎", ["vs Gusto"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 99.6 mph EV. Gusto LHB split +0.35, HR risk -0.25. pitcher risk below avg (-0.25); park/weather net drag (-13%).""", blast="good"),
            row("Cedric Mullins", "L", "+710", 72, "💎", ["vs Gusto"], """1 HR, 1 near-HR, 90.0 mph EV. Gusto LHB split +0.35, HR risk -0.25. pitcher risk below avg (-0.25); park/weather net drag (-13%).""", blast="good"),
            row("Yandy Diaz", "R", "+720", 78, "💎", ["vs Gusto"], """1 HR, 2 near-HR, 93.5 mph EV. Gusto RHB split -0.28, HR risk -0.25. slight split headwind (-0.28); pitcher risk below avg (-0.25).""", blast="good"),
            row("Junior Caminero", "R", "+435", 78, "💎", ["vs Gusto"], """1 HR, 2 near-HR, 93.8 mph EV. Gusto RHB split -0.28, HR risk -0.25. slight split headwind (-0.28); pitcher risk below avg (-0.25).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ ARI - Foster Griffin 🧤 (R, WSH) vs Merrill Kelly (R, ARI)",
        "description": "Tail key data: Park boost data unavailable. Griffin 🧤 (HR risk 1.20, vs LHB +0.27, vs RHB +1.48). Kelly (HR risk 0.51, vs LHB +0.92, vs RHB -0.21).",
        "rows": [
            row("Ketel Marte", "S", "+514", 72, "💎", ["vs Griffin"], """0 HR, 1 near-HR, 93.7 mph EV. Griffin RHB split +1.48, HR risk 1.20. limited recent HR events.""", blast="good"),
            row("Corbin Carroll", "L", "+514", 62, "💎", ["vs Griffin"], """0 HR, 83.1 mph EV. Griffin LHB split +0.27, HR risk 1.20. limited recent HR events; lighter EV form (83.1 mph)."""),
            row("Keibert Ruiz", "S", "+1040", 70, "💎", ["vs Kelly"], """1 HR, 1 near-HR, 86.8 mph EV. Kelly RHB split -0.21, HR risk 0.51. slight split headwind (-0.21); lighter EV form (86.8 mph).""", blast="good"),
            row("James Wood", "L", "+336", 85, "🌕 💣", ["vs Kelly"], """2 HR, 2 near-HR, 95.0 mph EV. Kelly LHB split +0.92, HR risk 0.51.""", blast="high"),
            row("CJ Abrams", "L", "+640", 73, "💎", ["vs Kelly"], """1 HR, 1 near-HR, 90.7 mph EV. Kelly LHB split +0.92, HR risk 0.51.""", blast="good"),
            row("Curtis Mead", "R", "+880", 87, "🌕 💣", ["vs Kelly"], """2 HR, 3 near-HR, 94.7 mph EV. Kelly RHB split -0.21, HR risk 0.51. slight split headwind (-0.21).""", blast="high"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-05")

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

    out = ROOT / '_games-0604.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
