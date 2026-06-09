#!/usr/bin/env python3
"""Generate games[] block for 2026-06-09 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Colby Thomas (R)",
    "Dillon Dingler (R)",
    "Ian Happ (S)",
    "Jake Bauers (L)",
    "Kyle Schwarber (L)",
    "Michael Conforto (L)",
    "Nick Kurtz (L)",
    "Riley Greene (L)",
    "Samuel Basallo (L)",
    "Shea Langeliers (R)",
    "Willson Contreras (R)",
}

GEMS = {
    "Blaze Alexander (R)",
    "Henry Davis (R)",
    "Hunter Goodman (R)",
    "Max Muncy (R)",
    "Patrick Wisdom (R)",
    "Pete Crow-Armstrong (L)",
    "Ryan Waldschmidt (R)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BAL",
    "Andrew Benintendi (L)": "CWS",
    "Ben Rice (L)": "NYY",
    "Blaze Alexander (R)": "BAL",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Brice Turang (L)": "MIL",
    "Brooks Lee (S)": "MIN",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "Cam Smith (R)": "HOU",
    "Carson Benge (L)": "NYM",
    "Casey Schmitt (R)": "SF",
    "Chase DeLauter (L)": "CLE",
    "Coby Mayo (R)": "BAL",
    "Cody Bellinger (L)": "NYY",
    "Colby Thomas (R)": "ATH",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "David Hamilton (L)": "MIL",
    "Daylen Lile (L)": "WSH",
    "Dillon Dingler (R)": "DET",
    "Fernando Tatis Jr. (R)": "SD",
    "Garrett Mitchell (L)": "MIL",
    "Gleyber Torres (R)": "DET",
    "Henry Davis (R)": "PIT",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Holliday (L)": "BAL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Jose Ramirez (S)": "CLE",
    "Josh Bell (S)": "MIN",
    "Junior Caminero (R)": "TB",
    "Kevin McGonigle (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "LaMonte Wade Jr. (L)": "HOU",
    "Lars Nootbaar (L)": "STL",
    "Luis Garcia Jr. (L)": "WSH",
    "MJ Melendez (L)": "NYM",
    "Manny Machado (R)": "SD",
    "Marcus Semien (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Max Muncy (R)": "ATH",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Michael Massey (L)": "KC",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Nick Kurtz (L)": "ATH",
    "Nolan Gorman (L)": "STL",
    "Oneil Cruz (L)": "PIT",
    "Owen Caissie (L)": "MIA",
    "Patrick Wisdom (R)": "SEA",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Ronald Acuna Jr. (R)": "ATL",
    "Ryan McMahon (L)": "NYY",
    "Ryan Waldschmidt (R)": "ARI",
    "Sal Stewart (R)": "CIN",
    "Samuel Basallo (L)": "BAL",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Tyler Soderstrom (L)": "ATH",
    "Victor Caratini (S)": "MIN",
    "Vinnie Pasquantino (L)": "KC",
    "Will Benson (L)": "CIN",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Yandy Diaz (R)": "TB",
    "Yohendrick Pinango (L)": "TOR",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_PITCHERS = {
    "Holmes",
    "Lauer",
    "Sugano",
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
        "title": "ARI @ MIA - Zac Gallen (R, ARI) vs Max Meyer (R, MIA)",
        "description": "Tail key data: Park boost -14% (stadium -13%, weather -1%). Gallen (HR risk 0.84, vs LHB +0.74, vs RHB +0.38). Meyer (HR risk -0.28, vs LHB -0.86, vs RHB +0.61).",
        "rows": [
            row("Kyle Stowers", "L", "+470", 70, "💎", ["vs Gallen"], """1 HR, 1 near-HR, 86.4 mph EV. Gallen LHB split +0.74, HR risk 0.84. park/weather net drag (-14%); lighter EV form (86.4 mph).""", blast="good"),
            row("Owen Caissie", "L", "+730", 74, "💎", ["vs Gallen"], """0 HR, 98.5 mph EV. Gallen LHB split +0.74, HR risk 0.84. park/weather net drag (-14%); limited recent HR events.""", blast="good"),
            row("Corbin Carroll", "L", "+490", 79, "💎", ["vs Meyer"], """1 HR, 2 near-HR, 94.8 mph EV. Meyer LHB split -0.86, HR risk -0.28. tough split lane (-0.86); pitcher risk below avg (-0.28).""", blast="good"),
            row("Ryan Waldschmidt", "R", "+1750", 68, "💎", ["vs Meyer"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 91.7 mph EV. Meyer RHB split +0.61, HR risk -0.28. pitcher risk below avg (-0.28); park/weather net drag (-14%)."""),
        ],
    },
    {
        "title": "ATL @ CWS - Grant Holmes 🧤 (R, ATL) vs Erick Fedde (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Holmes 🧤 (HR risk 1.22, vs LHB +1.35, vs RHB +0.09). Fedde (HR risk 0.74, vs LHB -0.36, vs RHB +1.28).",
        "rows": [
            row("Andrew Benintendi", "L", "+470", 84, "🌕 💣", ["vs Holmes"], """2 HR, 3 near-HR, 92.2 mph EV. Holmes LHB split +1.35, HR risk 1.22.""", blast="high"),
            row("Miguel Vargas", "R", "+370", 64, "💎", ["vs Holmes"], """0 HR, 1 near-HR, 87.5 mph EV. Holmes RHB split +0.09, HR risk 1.22. limited recent HR events; lighter EV form (87.5 mph)."""),
            row("Ronald Acuna Jr.", "R", "+375", 84, "🌕 💣", ["vs Fedde"], """3 HR, 3 near-HR, 87.8 mph EV. Fedde RHB split +1.28, HR risk 0.74. lighter EV form (87.8 mph).""", blast="high"),
            row("Michael Harris II", "L", "+430", 82, "🌕 💣", ["vs Fedde"], """2 HR, 3 near-HR, 89.8 mph EV. Fedde LHB split -0.36, HR risk 0.74. slight split headwind (-0.36).""", blast="high"),
            row("Matt Olson", "L", "+367", 66, "💎", ["vs Fedde"], """0 HR, 91.7 mph EV. Fedde LHB split -0.36, HR risk 0.74. slight split headwind (-0.36); limited recent HR events."""),
        ],
    },
    {
        "title": "BOS @ TB - Payton Tolle (L, BOS) vs Nick Martinez (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -3%, weather +1%). Tolle (HR risk -0.71, vs LHB -0.22, vs RHB -0.60). Martinez (HR risk -0.65, vs LHB -0.65, vs RHB -0.23).",
        "rows": [
            row("Yandy Diaz", "R", "+489", 78, "💎", ["vs Tolle"], """1 HR, 2 near-HR, 93.8 mph EV. Tolle RHB split -0.60, HR risk -0.71. tough split lane (-0.60); pitcher suppresses HR (-0.71).""", blast="good"),
            row("Junior Caminero", "R", "+360", 76, "🚀 💎", ["vs Tolle"], """0 HR, 100.9 mph EV. Tolle RHB split -0.60, HR risk -0.71. tough split lane (-0.60); pitcher suppresses HR (-0.71).""", blast="good"),
            row("Willson Contreras", "R", "+410", 83, "⭐ 💎", ["vs Martinez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 98.6 mph EV. Martinez RHB split -0.23, HR risk -0.65. slight split headwind (-0.23); pitcher suppresses HR (-0.65).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ COL - Colin Rea (R, CHC) vs Tomoyuki Sugano 🧤 (R, COL)",
        "description": "Tail key data: Park boost +19% (stadium +22%, weather -2%). Rea (HR risk 0.69, vs LHB +0.09, vs RHB +1.24). Sugano 🧤 (HR risk 1.23, vs LHB +2.29, vs RHB -0.24).",
        "rows": [
            row("Hunter Goodman", "R", "+270", 91, "🌕 💣 💎", ["vs Rea"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 95.0 mph EV. Rea RHB split +1.24, HR risk 0.69.""", blast="high"),
            row("Willi Castro", "S", "+630", 72, "💎", ["vs Rea"], """1 HR, 2 near-HR, 88.3 mph EV. Rea RHB split +1.24, HR risk 0.69.""", blast="good"),
            row("Ian Happ", "S", "+310", 85, "⭐ 🌕 💣", ["vs Sugano"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 92.7 mph EV. Sugano RHB split -0.24, HR risk 1.23. slight split headwind (-0.24).""", blast="high"),
            row("Pete Crow-Armstrong", "L", "+250", 98, "🌕 💣 💎", ["vs Sugano"], """Worst Pickz Hidden Gem. 4 HR, 6 near-HR, 94.8 mph EV. Sugano LHB split +2.29, HR risk 1.23.""", blast="high"),
            row("Michael Conforto", "L", "+380", 79, "⭐ 💎", ["vs Sugano"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 92.9 mph EV. Sugano LHB split +2.29, HR risk 1.23.""", blast="good"),
        ],
    },
    {
        "title": "CIN @ SD - Chase Burns (L, CIN) vs Lucas Giolito (R, SD)",
        "description": "Tail key data: Park boost -7% (stadium -4%, weather -2%). Burns (HR risk 0.10, vs LHB +0.60, vs RHB -0.35). Giolito (HR risk 0.22, vs LHB -0.43, vs RHB +0.66).",
        "rows": [
            row("Fernando Tatis Jr.", "R", "+579", 69, "💎", ["vs Burns"], """0 HR, 92.6 mph EV. Burns RHB split -0.35, HR risk 0.10. slight split headwind (-0.35); park/weather net drag (-7%).""", blast="good"),
            row("Manny Machado", "R", "+610", 76, "💎", ["vs Burns"], """1 HR, 2 near-HR, 91.6 mph EV. Burns RHB split -0.35, HR risk 0.10. slight split headwind (-0.35); park/weather net drag (-7%).""", blast="good"),
            row("Jackson Merrill", "L", "+525", 62, "💎", ["vs Burns"], """0 HR, 77.5 mph EV. Burns LHB split +0.60, HR risk 0.10. park/weather net drag (-7%); limited recent HR events."""),
            row("JJ Bleday", "L", "+502", 82, "🌕 💣", ["vs Giolito"], """2 HR, 2 near-HR, 92.3 mph EV. Giolito LHB split -0.43, HR risk 0.22. tough split lane (-0.43); park/weather net drag (-7%).""", blast="high"),
            row("Will Benson", "L", "N/A", 70, "💎", ["vs Giolito"], """1 HR, 1 near-HR, 82.0 mph EV. Giolito LHB split -0.43, HR risk 0.22. tough split lane (-0.43); park/weather net drag (-7%).""", blast="good"),
            row("Sal Stewart", "R", "+470", 71, "💎", ["vs Giolito"], """0 HR, 1 near-HR, 92.7 mph EV. Giolito RHB split +0.66, HR risk 0.22. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "HOU @ LAA - Kai-Wei Teng (R, HOU) vs Walbert Urena (R, LAA)",
        "description": "Tail key data: Park boost +12% (stadium +7%, weather +5%). Teng (HR risk -0.40, vs LHB +0.08, vs RHB -0.62). Urena (HR risk -0.92, vs LHB -1.12, vs RHB -0.10).",
        "rows": [
            row("Mike Trout", "R", "+360", 84, "🌕 💣", ["vs Teng"], """1 HR, 4 near-HR, 94.0 mph EV. Teng RHB split -0.62, HR risk -0.40. tough split lane (-0.62); pitcher suppresses HR (-0.40).""", blast="high"),
            row("Jo Adell", "R", "+517", 78, "🌕 💣", ["vs Teng"], """2 HR, 2 near-HR, 82.7 mph EV. Teng RHB split -0.62, HR risk -0.40. tough split lane (-0.62); pitcher suppresses HR (-0.40).""", blast="high"),
            row("Zach Neto", "R", "+484", 72, "💎", ["vs Teng"], """1 HR, 2 near-HR, 84.5 mph EV. Teng RHB split -0.62, HR risk -0.40. tough split lane (-0.62); pitcher suppresses HR (-0.40).""", blast="good"),
            row("Yordan Alvarez", "L", "+283", 91, "🌕 💣", ["vs Urena"], """2 HR, 4 near-HR, 97.2 mph EV. Urena LHB split -1.12, HR risk -0.92. tough split lane (-1.12); pitcher suppresses HR (-0.92).""", blast="high"),
            row("LaMonte Wade Jr.", "L", "+790", 76, "💎", ["vs Urena"], """1 HR, 1 near-HR, 94.4 mph EV. Urena LHB split -1.12, HR risk -0.92. tough split lane (-1.12); pitcher suppresses HR (-0.92).""", blast="good"),
            row("Cam Smith", "R", "+880", 71, "💎", ["vs Urena"], """0 HR, 95.2 mph EV. Urena RHB split -0.10, HR risk -0.92. slight split headwind (-0.10); pitcher suppresses HR (-0.92).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ PIT - Eric Lauer 🧤 (L, LAD) vs Paul Skenes (R, PIT)",
        "description": "Tail key data: Park boost -8% (stadium -15%, weather +7%). Lauer 🧤 (HR risk 1.60, vs LHB +1.28, vs RHB +1.19). Skenes (HR risk -1.19, vs LHB -0.91, vs RHB -0.83).",
        "rows": [
            row("Henry Davis", "R", "+630", 74, "💎", ["vs Lauer"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.3 mph EV. Lauer RHB split +1.19, HR risk 1.60. park/weather net drag (-8%).""", blast="good"),
            row("Oneil Cruz", "L", "+450", 76, "🚀 💎", ["vs Lauer"], """0 HR, 102.2 mph EV. Lauer LHB split +1.28, HR risk 1.60. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Shohei Ohtani", "L", "+375", 85, "🌕 💣", ["vs Skenes"], """2 HR, 2 near-HR, 95.3 mph EV. Skenes LHB split -0.91, HR risk -1.19. tough split lane (-0.91); pitcher suppresses HR (-1.19).""", blast="high"),
            row("Dalton Rushing", "L", "+675", 72, "💎", ["vs Skenes"], """1 HR, 2 near-HR, 85.6 mph EV. Skenes LHB split -0.91, HR risk -1.19. tough split lane (-0.91); pitcher suppresses HR (-1.19).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ ATH - Robert Gasser (L, MIL) vs J.T. Ginn (R, ATH)",
        "description": "Tail key data: Park boost +63% (stadium +55%, weather +8%). Gasser (HR risk 0.34, vs LHB -0.68, vs RHB +0.46). Ginn (HR risk -0.52, vs LHB -0.22, vs RHB -0.52).",
        "rows": [
            row("Nick Kurtz", "L", "+190", 94, "⭐ 🌕 💣", ["vs Gasser"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 98.5 mph EV. Gasser LHB split -0.68, HR risk 0.34. tough split lane (-0.68).""", blast="high"),
            row("Shea Langeliers", "R", "+170", 89, "⭐ 🌕 💣", ["vs Gasser"], """Worst Pickz Favorite. 3 HR, 2 near-HR, 95.2 mph EV. Gasser RHB split +0.46, HR risk 0.34.""", blast="high"),
            row("Tyler Soderstrom", "L", "+312", 91, "🌕 💣", ["vs Gasser"], """3 HR, 3 near-HR, 94.6 mph EV. Gasser LHB split -0.68, HR risk 0.34. tough split lane (-0.68).""", blast="high"),
            row("Colby Thomas", "R", "+300", 76, "⭐ 💎", ["vs Gasser"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.3 mph EV. Gasser RHB split +0.46, HR risk 0.34.""", blast="good"),
            row("Max Muncy", "R", "+333", 78, "💎", ["vs Gasser"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 99.6 mph EV. Gasser RHB split +0.46, HR risk 0.34. limited recent HR events.""", blast="good"),
            row("Jake Bauers", "L", "+290", 98, "⭐ 🌕 💣", ["vs Ginn"], """Worst Pickz Favorite. 4 HR, 4 near-HR, 96.9 mph EV. Ginn LHB split -0.22, HR risk -0.52. slight split headwind (-0.22); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Brice Turang", "L", "+430", 84, "🌕 💣", ["vs Ginn"], """2 HR, 4 near-HR, 89.6 mph EV. Ginn LHB split -0.22, HR risk -0.52. slight split headwind (-0.22); pitcher suppresses HR (-0.52).""", blast="high"),
            row("David Hamilton", "L", "+710", 86, "🌕 💣", ["vs Ginn"], """3 HR, 3 near-HR, 90.3 mph EV. Ginn LHB split -0.22, HR risk -0.52. slight split headwind (-0.22); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Garrett Mitchell", "L", "+470", 78, "💎", ["vs Ginn"], """0 HR, 3 near-HR, 96.1 mph EV. Ginn LHB split -0.22, HR risk -0.52. slight split headwind (-0.22); pitcher suppresses HR (-0.52).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ DET - Taj Bradley (R, MIN) vs Troy Melton (R, DET)",
        "description": "Tail key data: Park boost +8% (stadium -10%, weather +19%). Bradley (HR risk -0.32, vs LHB +0.25, vs RHB -0.92). Melton (HR risk -1.04, vs LHB -0.54, vs RHB -0.74).",
        "rows": [
            row("Dillon Dingler", "R", "+495", 89, "⭐ 🌕 💣", ["vs Bradley"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 95.1 mph EV. Bradley RHB split -0.92, HR risk -0.32. tough split lane (-0.92); pitcher risk below avg (-0.32).""", blast="high"),
            row("Riley Greene", "L", "+520", 79, "⭐ 💎", ["vs Bradley"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.9 mph EV. Bradley LHB split +0.25, HR risk -0.32. pitcher risk below avg (-0.32); park suppresses carry (-10%).""", blast="good"),
            row("Kevin McGonigle", "L", "+850", 66, "💎", ["vs Bradley"], """0 HR, 91.9 mph EV. Bradley LHB split +0.25, HR risk -0.32. pitcher risk below avg (-0.32); park suppresses carry (-10%)."""),
            row("Gleyber Torres", "R", "+920", 78, "💎", ["vs Bradley"], """1 HR, 1 near-HR, 95.6 mph EV. Bradley RHB split -0.92, HR risk -0.32. tough split lane (-0.92); pitcher risk below avg (-0.32).""", blast="good"),
            row("Brooks Lee", "S", "+830", 91, "🌕 💣", ["vs Melton"], """3 HR, 3 near-HR, 94.6 mph EV. Melton RHB split -0.74, HR risk -1.04. tough split lane (-0.74); pitcher suppresses HR (-1.04).""", blast="high"),
            row("Byron Buxton", "R", "+316", 84, "🌕 💣", ["vs Melton"], """2 HR, 2 near-HR, 93.6 mph EV. Melton RHB split -0.74, HR risk -1.04. tough split lane (-0.74); pitcher suppresses HR (-1.04).""", blast="high"),
            row("Josh Bell", "S", "+650", 82, "💎", ["vs Melton"], """1 HR, 3 near-HR, 96.0 mph EV. Melton RHB split -0.74, HR risk -1.04. tough split lane (-0.74); pitcher suppresses HR (-1.04).""", blast="good"),
            row("Victor Caratini", "S", "+960", 75, "💎", ["vs Melton"], """1 HR, 1 near-HR, 92.7 mph EV. Melton RHB split -0.74, HR risk -1.04. tough split lane (-0.74); pitcher suppresses HR (-1.04).""", blast="good"),
            row("Kody Clemens", "L", "+491", 80, "💎", ["vs Melton"], """1 HR, 3 near-HR, 94.0 mph EV. Melton LHB split -0.54, HR risk -1.04. tough split lane (-0.54); pitcher suppresses HR (-1.04).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ CLE - Gerrit Cole (R, NYY) vs Slade Cecconi (R, CLE)",
        "description": "Tail key data: Park boost +16% (stadium -2%, weather +18%). Cole (HR risk -0.26, vs LHB -0.18, vs RHB -0.17). Cecconi (HR risk -0.81, vs LHB -0.79, vs RHB -0.18).",
        "rows": [
            row("Jose Ramirez", "S", "+393", 80, "🌕 💣", ["vs Cole"], """2 HR, 2 near-HR, 90.0 mph EV. Cole RHB split -0.17, HR risk -0.26. slight split headwind (-0.17); pitcher risk below avg (-0.26).""", blast="high"),
            row("Rhys Hoskins", "R", "+450", 70, "💎", ["vs Cole"], """1 HR, 1 near-HR, 88.2 mph EV. Cole RHB split -0.17, HR risk -0.26. slight split headwind (-0.17); pitcher risk below avg (-0.26).""", blast="good"),
            row("Chase DeLauter", "L", "+559", 68, "💎", ["vs Cole"], """0 HR, 92.5 mph EV. Cole LHB split -0.18, HR risk -0.26. slight split headwind (-0.18); pitcher risk below avg (-0.26).""", blast="good"),
            row("Ryan McMahon", "L", "+493", 90, "🌕 💣", ["vs Cecconi"], """3 HR, 3 near-HR, 94.0 mph EV. Cecconi LHB split -0.79, HR risk -0.81. tough split lane (-0.79); pitcher suppresses HR (-0.81).""", blast="high"),
            row("Ben Rice", "L", "+270", 84, "🌕 💣", ["vs Cecconi"], """2 HR, 3 near-HR, 92.4 mph EV. Cecconi LHB split -0.79, HR risk -0.81. tough split lane (-0.79); pitcher suppresses HR (-0.81).""", blast="high"),
            row("Cody Bellinger", "L", "+390", 74, "💎", ["vs Cecconi"], """1 HR, 1 near-HR, 92.3 mph EV. Cecconi LHB split -0.79, HR risk -0.81. tough split lane (-0.79); pitcher suppresses HR (-0.81).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ TOR - Zack Wheeler (R, PHI) vs Dylan Cease (R, TOR)",
        "description": "Tail key data: Park boost +3% (stadium +7%, weather -4%). Wheeler (HR risk -0.03, vs LHB +0.23, vs RHB -0.37). Cease (HR risk -0.10, vs LHB +0.20, vs RHB -0.43).",
        "rows": [
            row("Yohendrick Pinango", "L", "N/A", 73, "💎", ["vs Wheeler"], """1 HR, 1 near-HR, 91.3 mph EV. Wheeler LHB split +0.23, HR risk -0.03. pitcher risk below avg (-0.03); weather carry headwind (-4%).""", blast="good"),
            row("Bryce Harper", "L", "+520", 64, "💎", ["vs Cease"], """0 HR, 1 near-HR, 86.8 mph EV. Cease LHB split +0.20, HR risk -0.10. pitcher risk below avg (-0.10); weather carry headwind (-4%)."""),
            row("Kyle Schwarber", "L", "+290", 79, "⭐ 💎", ["vs Cease"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.6 mph EV. Cease LHB split +0.20, HR risk -0.10. pitcher risk below avg (-0.10); weather carry headwind (-4%).""", blast="good"),
            row("Brandon Marsh", "L", "+800", 78, "💎", ["vs Cease"], """1 HR, 1 near-HR, 95.9 mph EV. Cease LHB split +0.20, HR risk -0.10. pitcher risk below avg (-0.10); weather carry headwind (-4%).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ BAL - Logan Gilbert (R, SEA) vs Trevor Rogers (L, BAL)",
        "description": "Tail key data: Park boost -1% (stadium -4%, weather +3%). Gilbert (HR risk 0.74, vs LHB +0.77, vs RHB +0.42). Rogers (HR risk 0.20, vs LHB -0.95, vs RHB +0.35).",
        "rows": [
            row("Adley Rutschman", "S", "+582", 76, "💎", ["vs Gilbert"], """1 HR, 1 near-HR, 93.6 mph EV. Gilbert RHB split +0.42, HR risk 0.74.""", blast="good"),
            row("Samuel Basallo", "L", "+450", 77, "⭐ 💎", ["vs Gilbert"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.4 mph EV. Gilbert LHB split +0.77, HR risk 0.74.""", blast="good"),
            row("Colton Cowser", "L", "+531", 74, "💎", ["vs Gilbert"], """1 HR, 3 near-HR, 87.5 mph EV. Gilbert LHB split +0.77, HR risk 0.74. lighter EV form (87.5 mph).""", blast="good"),
            row("Jackson Holliday", "L", "+810", 75, "💎", ["vs Gilbert"], """1 HR, 2 near-HR, 91.2 mph EV. Gilbert LHB split +0.77, HR risk 0.74.""", blast="good"),
            row("Coby Mayo", "R", "+444", 77, "💎", ["vs Gilbert"], """1 HR, 1 near-HR, 95.0 mph EV. Gilbert RHB split +0.42, HR risk 0.74.""", blast="good"),
            row("Blaze Alexander", "R", "N/A", 77, "💎", ["vs Gilbert"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 92.6 mph EV. Gilbert RHB split +0.42, HR risk 0.74.""", blast="good"),
            row("Patrick Wisdom", "R", "+339", 74, "💎", ["vs Rogers"], """Worst Pickz Hidden Gem. 0 HR, 97.6 mph EV. Rogers RHB split +0.35, HR risk 0.20. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "STL @ NYM - Dustin May (R, STL) vs Freddy Peralta (R, NYM)",
        "description": "Tail key data: Park boost +2% (stadium -1%, weather +3%). May (HR risk -0.43, vs LHB -0.26, vs RHB -0.27). Peralta (HR risk 0.13, vs LHB +0.32, vs RHB -0.41).",
        "rows": [
            row("Jared Young", "L", "+620", 85, "🌕 💣", ["vs May"], """2 HR, 2 near-HR, 94.6 mph EV. May LHB split -0.26, HR risk -0.43. slight split headwind (-0.26); pitcher suppresses HR (-0.43).""", blast="high"),
            row("Marcus Semien", "R", "+800", 86, "🌕 💣", ["vs May"], """3 HR, 3 near-HR, 90.3 mph EV. May RHB split -0.27, HR risk -0.43. slight split headwind (-0.27); pitcher suppresses HR (-0.43).""", blast="high"),
            row("Carson Benge", "L", "+650", 88, "🌕 💣", ["vs May"], """2 HR, 3 near-HR, 95.6 mph EV. May LHB split -0.26, HR risk -0.43. slight split headwind (-0.26); pitcher suppresses HR (-0.43).""", blast="high"),
            row("MJ Melendez", "L", "+630", 73, "💎", ["vs May"], """1 HR, 1 near-HR, 91.1 mph EV. May LHB split -0.26, HR risk -0.43. slight split headwind (-0.26); pitcher suppresses HR (-0.43).""", blast="good"),
            row("Nolan Gorman", "L", "+540", 70, "💎", ["vs Peralta"], """1 HR, 1 near-HR, 87.7 mph EV. Peralta LHB split +0.32, HR risk 0.13. lighter EV form (87.7 mph).""", blast="good"),
            row("Lars Nootbaar", "L", "+575", 71, "💎", ["vs Peralta"], """0 HR, 1 near-HR, 93.4 mph EV. Peralta LHB split +0.32, HR risk 0.13. limited recent HR events.""", blast="good"),
            row("JJ Wetherholt", "L", "+490", 74, "💎", ["vs Peralta"], """0 HR, 1 near-HR, 96.0 mph EV. Peralta LHB split +0.32, HR risk 0.13. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TEX @ KC - Nathan Eovaldi (R, TEX) vs Stephen Kolek (R, KC)",
        "description": "Tail key data: Park boost +43% (stadium +12%, weather +31%). Eovaldi (HR risk 0.10, vs LHB -0.22, vs RHB +0.22). Kolek (HR risk -0.50, vs LHB -0.59, vs RHB +0.05).",
        "rows": [
            row("Bobby Witt Jr.", "R", "+390", 64, "💎", ["vs Eovaldi"], """0 HR, 1 near-HR, 88.3 mph EV. Eovaldi RHB split +0.22, HR risk 0.10. limited recent HR events."""),
            row("Michael Massey", "L", "+640", 83, "🌕 💣", ["vs Eovaldi"], """2 HR, 2 near-HR, 93.3 mph EV. Eovaldi LHB split -0.22, HR risk 0.10. slight split headwind (-0.22).""", blast="high"),
            row("Vinnie Pasquantino", "L", "+549", 71, "💎", ["vs Eovaldi"], """1 HR, 1 near-HR, 88.8 mph EV. Eovaldi LHB split -0.22, HR risk 0.10. slight split headwind (-0.22).""", blast="good"),
            row("Jac Caglianone", "L", "+494", 76, "💎", ["vs Eovaldi"], """0 HR, 99.9 mph EV. Eovaldi LHB split -0.22, HR risk 0.10. slight split headwind (-0.22); limited recent HR events.""", blast="good"),
            row("Joc Pederson", "L", "+502", 75, "💎", ["vs Kolek"], """1 HR, 2 near-HR, 90.7 mph EV. Kolek LHB split -0.59, HR risk -0.50. tough split lane (-0.59); pitcher suppresses HR (-0.50).""", blast="good"),
            row("Brandon Nimmo", "L", "+543", 84, "🌕 💣", ["vs Kolek"], """1 HR, 5 near-HR, 92.3 mph EV. Kolek LHB split -0.59, HR risk -0.50. tough split lane (-0.59); pitcher suppresses HR (-0.50).""", blast="high"),
        ],
    },
    {
        "title": "WSH @ SF - Andrew Alvarez (L, WSH) vs Adrian Houser (R, SF)",
        "description": "Tail key data: Park boost data unavailable. Alvarez (HR risk 0.12, vs LHB +0.67, vs RHB +0.22). Houser (HR risk -0.11, vs LHB +0.10, vs RHB -0.22).",
        "rows": [
            row("Willy Adames", "R", "+660", 70, "💎", ["vs Alvarez"], """1 HR, 1 near-HR, 88.5 mph EV. Alvarez RHB split +0.22, HR risk 0.12.""", blast="good"),
            row("Casey Schmitt", "R", "+670", 62, "💎", ["vs Alvarez"], """0 HR, 82.8 mph EV. Alvarez RHB split +0.22, HR risk 0.12. limited recent HR events; lighter EV form (82.8 mph)."""),
            row("James Wood", "L", "+380", 78, "💎", ["vs Houser"], """1 HR, 2 near-HR, 93.9 mph EV. Houser LHB split +0.10, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="good"),
            row("Daylen Lile", "L", "+1000", 70, "💎", ["vs Houser"], """1 HR, 1 near-HR, 85.8 mph EV. Houser LHB split +0.10, HR risk -0.11. pitcher risk below avg (-0.11); lighter EV form (85.8 mph).""", blast="good"),
            row("Luis Garcia Jr.", "L", "+800", 73, "💎", ["vs Houser"], """1 HR, 2 near-HR, 89.1 mph EV. Houser LHB split +0.10, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="good"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-09")

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

    out = ROOT / '_games-0609.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
