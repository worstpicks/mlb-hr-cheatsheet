#!/usr/bin/env python3
"""Generate games[] block for 2026-09-02 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Bobby Witt Jr. (R)",
    "Carter Jensen (L)",
    "Colt Keith (L)",
    "Colton Cowser (L)",
    "Daylen Lile (L)",
    "Elly De La Cruz (S)",
    "Heliot Ramos (R)",
    "Jac Caglianone (L)",
    "Jake Burger (R)",
    "Juan Soto (L)",
    "Julio Rodriguez (R)",
    "Kazuma Okamoto (R)",
    "Kody Clemens (L)",
    "Kyle Schwarber (L)",
    "Lawrence Butler (L)",
    "Michael Busch (L)",
    "Mickey Gasper (S)",
    "Nelson Velazquez (R)",
    "Pete Crow Armstrong (L)",
    "Rafael Devers (L)",
    "Roman Anthony (L)",
    "Victor Mesa Jr. (L)",
    "Will Smith (R)",
}

GEMS = {
    "Andrew Knizner (R)",
    "Andrew Vaughn (R)",
    "Ben Malgeri (R)",
    "Blaze Alexander (R)",
    "Brandon Lowe (L)",
    "Cal Raleigh (S)",
    "Cody Bellinger (L)",
    "Francisco Lindor (S)",
    "Heriberto Hernandez (R)",
    "Jarren Duran (L)",
    "Jordan Beck (R)",
    "LaMonte Wade Jr. (L)",
    "Lars Nootbaar (L)",
    "Matt Olson (L)",
    "Munetaka Murakami (L)",
    "Nick Loftin (R)",
    "Pedro Ramirez (S)",
    "Ryan Kreidler (R)",
    "Spencer Jones (L)",
    "Teoscar Hernandez (R)",
    "Tyler Stephenson (R)",
    "Vaughn Grissom (R)",
    "Zack Gelof (R)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BOS",
    "Alejandro Kirk (R)": "TOR",
    "Andres Chaparro (R)": "WSH",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Knizner (R)": "SF",
    "Andrew Vaughn (R)": "MIL",
    "Ben Malgeri (R)": "DET",
    "Ben Rice (L)": "NYY",
    "Blaze Alexander (R)": "BAL",
    "Bobby Witt Jr. (R)": "KC",
    "Brady House (R)": "WSH",
    "Brandon Lowe (L)": "PIT",
    "Brandon Valenzuela (S)": "TOR",
    "Brett Callahan (L)": "DET",
    "Brian Navarreto (R)": "MIA",
    "Brooks Lee (S)": "MIN",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Harper (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Carter Jensen (L)": "KC",
    "Chase DeLauter (L)": "CLE",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Christian Moore (R)": "LAA",
    "Cody Bellinger (L)": "NYY",
    "Cole Carrigg (S)": "COL",
    "Colt Keith (L)": "DET",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "Daylen Lile (L)": "WSH",
    "Elias Diaz (R)": "TEX",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Freddie Freeman (L)": "LAD",
    "Garrett Mitchell (L)": "MIL",
    "George Springer (R)": "TOR",
    "Heliot Ramos (R)": "NYY",
    "Heriberto Hernandez (R)": "MIA",
    "JT Realmuto (R)": "PHI",
    "Jac Caglianone (L)": "KC",
    "Jackson Merrill (L)": "SD",
    "Jake Burger (R)": "TEX",
    "James McCann (R)": "ARI",
    "Jarren Duran (L)": "BOS",
    "Jazz Chisholm Jr. (L)": "NYY",
    "John Peck (R)": "DET",
    "Jonathan Aranda (L)": "TB",
    "Jordan Beck (R)": "COL",
    "Josh Lowe (L)": "LAA",
    "Juan Soto (L)": "NYM",
    "Julio Rodriguez (R)": "SEA",
    "Jung Hoo Lee (L)": "SF",
    "Justin Foscue (R)": "TEX",
    "Kazuma Okamoto (R)": "TOR",
    "Kevin McGonigle (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "LaMonte Wade Jr. (L)": "HOU",
    "Lars Nootbaar (L)": "ARI",
    "Lawrence Butler (L)": "ATH",
    "Liam Hicks (L)": "TB",
    "Luis Torrens (R)": "NYM",
    "Luke Keaschall (R)": "MIN",
    "Matt Olson (L)": "ATL",
    "Michael Busch (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Mickey Gasper (S)": "BOS",
    "Munetaka Murakami (L)": "CWS",
    "Nathaniel Lowe (L)": "CLE",
    "Nelson Velazquez (R)": "HOU",
    "Nick Loftin (R)": "KC",
    "Patrick Bailey (S)": "CLE",
    "Patrick Wisdom (R)": "SEA",
    "Pedro Ramirez (S)": "CHC",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randy Arozarena (R)": "SEA",
    "Roman Anthony (L)": "BOS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Ryan Kreidler (R)": "MIN",
    "Sal Stewart (R)": "CIN",
    "Samuel Basallo (L)": "BAL",
    "Sean Murphy (R)": "ATL",
    "Seiya Suzuki (R)": "CHC",
    "Spencer Jones (L)": "NYY",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Tommy White (R)": "ATH",
    "Travis Bazzana (L)": "CLE",
    "Trea Turner (R)": "PHI",
    "Tristan Peters (L)": "CWS",
    "Ty France (R)": "SD",
    "Tyler Stephenson (R)": "CIN",
    "Vaughn Grissom (R)": "LAA",
    "Victor Mesa Jr. (L)": "TB",
    "Vinnie Pasquantino (L)": "KC",
    "Will Smith (R)": "LAD",
    "Wyatt Langford (R)": "TEX",
    "Yainer Diaz (R)": "HOU",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("BAL @ COL", "Sugano"),
    ("CWS @ HOU", "Martin"),
    ("NYM @ TB", "Hagenman"),
    ("PHI @ ARI", "Clarke"),
    ("SD @ CIN", "Mize"),
    ("SEA @ BOS", "Miller"),
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
        "title": "ATH @ TEX - Jacob Lopez (L, ATH) vs Cody Bradford (L, TEX)",
        "description": "Tail key data: Park boost data unavailable. Lopez (HR risk -0.08, vs LHB -0.93, vs RHB +0.31). Bradford (HR risk -0.64, vs LHB +0.27, vs RHB -0.89).",
        "rows": [
            row("Jake Burger", "R", "+470", 66, "⭐", ["vs Lopez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.2 mph EV. Lopez RHB split +0.31, HR risk -0.08. pitcher risk below avg (-0.08).""", blast="good"),
            row("Justin Foscue", "R", "+690", 64, "", ["vs Lopez"], """1 HR, 1 near-HR, 93.3 mph EV. Lopez RHB split +0.31, HR risk -0.08. pitcher risk below avg (-0.08).""", blast="good"),
            row("Elias Diaz", "R", "+625", 61, "", ["vs Lopez"], """0 HR, 96.8 mph EV. Lopez RHB split +0.31, HR risk -0.08. pitcher risk below avg (-0.08); limited recent HR events.""", blast="good"),
            row("Wyatt Langford", "R", "+540", 61, "", ["vs Lopez"], """0 HR, 95.9 mph EV. Lopez RHB split +0.31, HR risk -0.08. pitcher risk below avg (-0.08); limited recent HR events.""", blast="good"),
            row("Lawrence Butler", "L", "+590", 59, "⭐", ["vs Bradford"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.0 mph EV. Bradford LHB split +0.27, HR risk -0.64. pitcher suppresses HR (-0.64).""", blast="good"),
            row("Tommy White", "R", "+740", 58, "", ["vs Bradford"], """0 HR, 92.8 mph EV. Bradford RHB split -0.89, HR risk -0.64. tough split lane (-0.89); pitcher suppresses HR (-0.64).""", blast="good"),
            row("Zack Gelof", "R", "+530", 58, "💎", ["vs Bradford"], """Worst Pickz Hidden Gem. 0 HR, 93.2 mph EV. Bradford RHB split -0.89, HR risk -0.64. tough split lane (-0.89); pitcher suppresses HR (-0.64).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ WSH - Grant Holmes (R, ATL) vs Brad Lord (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Holmes (HR risk -0.40, vs LHB -0.53, vs RHB +0.29). Lord (HR risk -0.48, vs LHB +0.02, vs RHB -0.40).",
        "rows": [
            row("Daylen Lile", "L", "+540", 65, "⭐ 🌕 💣", ["vs Holmes"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.9 mph EV. Holmes LHB split -0.53, HR risk -0.40. tough split lane (-0.53); pitcher suppresses HR (-0.40).""", blast="high"),
            row("Andres Chaparro", "R", "N/A", 58, "", ["vs Holmes"], """0 HR, 1 near-HR, 92.4 mph EV. Holmes RHB split +0.29, HR risk -0.40. pitcher suppresses HR (-0.40); limited recent HR events.""", blast="good"),
            row("Brady House", "R", "+570", 58, "", ["vs Holmes"], """0 HR, 92.4 mph EV. Holmes RHB split +0.29, HR risk -0.40. pitcher suppresses HR (-0.40); limited recent HR events.""", blast="good"),
            row("Matt Olson", "L", "+328", 59, "💎", ["vs Lord"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.7 mph EV. Lord LHB split +0.02, HR risk -0.48. pitcher suppresses HR (-0.48).""", blast="good"),
            row("Michael Harris II", "L", "+490", 58, "", ["vs Lord"], """1 HR, 1 near-HR, 87.4 mph EV. Lord LHB split +0.02, HR risk -0.48. pitcher suppresses HR (-0.48); lighter EV form (87.4 mph).""", blast="good"),
            row("Sean Murphy", "R", "+710", 58, "", ["vs Lord"], """1 HR, 1 near-HR, 88.0 mph EV. Lord RHB split -0.40, HR risk -0.48. tough split lane (-0.40); pitcher suppresses HR (-0.48).""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+470", 58, "", ["vs Lord"], """0 HR, 2 near-HR, 92.3 mph EV. Lord RHB split -0.40, HR risk -0.48. tough split lane (-0.40); pitcher suppresses HR (-0.48).""", blast="good"),
        ],
    },
    {
        "title": "BAL @ COL - Trevor Rogers (L, BAL) vs Tomoyuki Sugano 🧤 (R, COL)",
        "description": "Tail key data: Park boost data unavailable. Rogers (HR risk 0.50, vs LHB -1.79, vs RHB +1.17). Sugano 🧤 (HR risk 1.51, vs LHB +1.56, vs RHB +0.45).",
        "rows": [
            row("Cole Carrigg", "S", "+680", 75, "", ["vs Rogers"], """1 HR, 1 near-HR, 89.2 mph EV. Rogers SHB→RHB split +1.17, HR risk 0.50.""", blast="good"),
            row("Jordan Beck", "R", "+820", 62, "💎", ["vs Rogers"], """Worst Pickz Hidden Gem. 0 HR, 83.5 mph EV. Rogers RHB split +1.17, HR risk 0.50. limited recent HR events; lighter EV form (83.5 mph)."""),
            row("Christian Encarnacion-Strand", "R", "+377", 70, "", ["vs Sugano"], """0 HR, 89.5 mph EV. Sugano RHB split +0.45, HR risk 1.51. limited recent HR events."""),
            row("Samuel Basallo", "L", "+380", 89, "🌕 💣", ["vs Sugano"], """1 HR, 1 near-HR, 90.5 mph EV. Sugano LHB split +1.56, HR risk 1.51.""", blast="good"),
            row("Pete Alonso", "R", "+257", 86, "", ["vs Sugano"], """1 HR, 1 near-HR, 96.2 mph EV. Sugano RHB split +0.45, HR risk 1.51.""", blast="good"),
            row("Blaze Alexander", "R", "+349", 86, "💎", ["vs Sugano"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.3 mph EV. Sugano RHB split +0.45, HR risk 1.51.""", blast="good"),
            row("Colton Cowser", "L", "+529", 89, "⭐ 🌕 💣", ["vs Sugano"], """Worst Pickz Favorite. 0 HR, 97.6 mph EV. Sugano LHB split +1.56, HR risk 1.51. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ HOU - Davis Martin 🧤 (R, CWS) vs Hayden Wesneski (R, HOU)",
        "description": "Tail key data: Park boost data unavailable. Martin 🧤 (HR risk 1.01, vs LHB +0.69, vs RHB +0.82). Wesneski (HR risk -0.36, vs LHB +0.37, vs RHB -1.08).",
        "rows": [
            row("Yainer Diaz", "R", "+720", 84, "", ["vs Martin"], """1 HR, 1 near-HR, 95.1 mph EV. Martin RHB split +0.82, HR risk 1.01.""", blast="good"),
            row("LaMonte Wade Jr.", "L", "N/A", 84, "💎", ["vs Martin"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.4 mph EV. Martin LHB split +0.69, HR risk 1.01.""", blast="good"),
            row("Yordan Alvarez", "L", "+300", 86, "", ["vs Martin"], """1 HR, 2 near-HR, 97.5 mph EV. Martin LHB split +0.69, HR risk 1.01.""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 81, "⭐", ["vs Martin"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.4 mph EV. Martin RHB split +0.82, HR risk 1.01. limited recent HR events.""", blast="good"),
            row("Andrew Benintendi", "L", "+579", 65, "", ["vs Wesneski"], """1 HR, 2 near-HR, 95.6 mph EV. Wesneski LHB split +0.37, HR risk -0.36. pitcher risk below avg (-0.36).""", blast="good"),
            row("Tristan Peters", "L", "+850", 60, "", ["vs Wesneski"], """1 HR, 1 near-HR, 91.6 mph EV. Wesneski LHB split +0.37, HR risk -0.36. pitcher risk below avg (-0.36).""", blast="good"),
            row("Munetaka Murakami", "L", "+340", 58, "💎", ["vs Wesneski"], """Worst Pickz Hidden Gem. 0 HR, 92.1 mph EV. Wesneski LHB split +0.37, HR risk -0.36. pitcher risk below avg (-0.36); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "DET @ MIN - Drew Anderson (R, DET) vs Dean Kremer (R, MIN)",
        "description": "Tail key data: Park boost data unavailable. Anderson (HR risk 0.67, vs LHB +0.43, vs RHB +0.68). Kremer (HR risk 0.55, vs LHB +0.35, vs RHB +0.65).",
        "rows": [
            row("Kody Clemens", "L", "+400", 92, "⭐ 🌕 💣", ["vs Anderson"], """Worst Pickz Favorite. 3 HR, 5 near-HR, 99.7 mph EV. Anderson LHB split +0.43, HR risk 0.67.""", blast="high"),
            row("Brooks Lee", "S", "+760", 82, "🌕 💣", ["vs Anderson"], """2 HR, 2 near-HR, 89.6 mph EV. Anderson SHB→RHB split +0.68, HR risk 0.67.""", blast="high"),
            row("Luke Keaschall", "R", "+900", 78, "", ["vs Anderson"], """1 HR, 1 near-HR, 95.3 mph EV. Anderson RHB split +0.68, HR risk 0.67.""", blast="good"),
            row("Ryan Kreidler", "R", "N/A", 63, "💎", ["vs Anderson"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 88.2 mph EV. Anderson RHB split +0.68, HR risk 0.67. limited recent HR events."""),
            row("Colt Keith", "L", "+650", 68, "⭐", ["vs Kremer"], """Worst Pickz Favorite. 0 HR, 94.0 mph EV. Kremer LHB split +0.35, HR risk 0.55. limited recent HR events.""", blast="good"),
            row("Brett Callahan", "L", "+550", 70, "", ["vs Kremer"], """0 HR, 2 near-HR, 92.8 mph EV. Kremer LHB split +0.35, HR risk 0.55.""", blast="good"),
            row("Ben Malgeri", "R", "N/A", 75, "💎", ["vs Kremer"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.5 mph EV. Kremer RHB split +0.65, HR risk 0.55.""", blast="good"),
            row("Kevin McGonigle", "L", "+725", 67, "", ["vs Kremer"], """0 HR, 92.8 mph EV. Kremer LHB split +0.35, HR risk 0.55. limited recent HR events.""", blast="good"),
            row("John Peck", "R", "+980", 72, "", ["vs Kremer"], """0 HR, 97.3 mph EV. Kremer RHB split +0.65, HR risk 0.55. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ KC - Eury Perez (R, MIA) vs Noah Cameron (L, KC)",
        "description": "Tail key data: Park boost data unavailable. Perez (HR risk -0.49, vs LHB -0.88, vs RHB +0.41). Cameron (HR risk -0.78, vs LHB -0.04, vs RHB -0.60).",
        "rows": [
            row("Carter Jensen", "L", "+425", 60, "⭐", ["vs Perez"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 95.4 mph EV. Perez LHB split -0.88, HR risk -0.49. tough split lane (-0.88); pitcher suppresses HR (-0.49).""", blast="good"),
            row("Jac Caglianone", "L", "+370", 58, "⭐", ["vs Perez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.1 mph EV. Perez LHB split -0.88, HR risk -0.49. tough split lane (-0.88); pitcher suppresses HR (-0.49).""", blast="good"),
            row("Bobby Witt Jr.", "R", "+450", 59, "⭐", ["vs Perez"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 94.3 mph EV. Perez RHB split +0.41, HR risk -0.49. pitcher suppresses HR (-0.49).""", blast="good"),
            row("Nick Loftin", "R", "+880", 59, "💎", ["vs Perez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.7 mph EV. Perez RHB split +0.41, HR risk -0.49. pitcher suppresses HR (-0.49).""", blast="good"),
            row("Vinnie Pasquantino", "L", "+540", 58, "", ["vs Perez"], """1 HR, 1 near-HR, 88.9 mph EV. Perez LHB split -0.88, HR risk -0.49. tough split lane (-0.88); pitcher suppresses HR (-0.49).""", blast="good"),
            row("Brian Navarreto", "R", "+875", 58, "", ["vs Cameron"], """1 HR, 1 near-HR, 90.8 mph EV. Cameron RHB split -0.60, HR risk -0.78. tough split lane (-0.60); pitcher suppresses HR (-0.78).""", blast="good"),
            row("Heriberto Hernandez", "R", "+364", 58, "💎", ["vs Cameron"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.8 mph EV. Cameron RHB split -0.60, HR risk -0.78. tough split lane (-0.60); pitcher suppresses HR (-0.78).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ CHC - Jacob Misiorowski (R, MIL) vs David Peterson (L, CHC)",
        "description": "Tail key data: Park boost data unavailable. Misiorowski (HR risk -0.52, vs LHB +0.03, vs RHB -0.96). Peterson (HR risk -0.72, vs LHB -0.72, vs RHB -0.25).",
        "rows": [
            row("Michael Busch", "L", "+550", 59, "⭐", ["vs Misiorowski"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.4 mph EV. Misiorowski LHB split +0.03, HR risk -0.52. pitcher suppresses HR (-0.52).""", blast="good"),
            row("Pete Crow Armstrong", "L", "+340", 77, "⭐ 🌕 💣", ["vs Misiorowski"], """Worst Pickz Favorite. 4 HR, 4 near-HR, 95.3 mph EV. Misiorowski LHB split +0.03, HR risk -0.52. pitcher suppresses HR (-0.52).""", blast="high"),
            row("Pedro Ramirez", "S", "+990", 59, "💎", ["vs Misiorowski"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.6 mph EV. Misiorowski SHB→LHB split +0.03, HR risk -0.52. pitcher suppresses HR (-0.52).""", blast="good"),
            row("Seiya Suzuki", "R", "+493", 58, "", ["vs Misiorowski"], """0 HR, 1 near-HR, 91.9 mph EV. Misiorowski RHB split -0.96, HR risk -0.52. tough split lane (-0.96); pitcher suppresses HR (-0.52)."""),
            row("Andrew Vaughn", "R", "+650", 58, "💎", ["vs Peterson"], """Worst Pickz Hidden Gem. 0 HR, 93.7 mph EV. Peterson RHB split -0.25, HR risk -0.72. slight split headwind (-0.25); pitcher suppresses HR (-0.72).""", blast="good"),
            row("Garrett Mitchell", "L", "+700", 58, "", ["vs Peterson"], """0 HR, 97.2 mph EV. Peterson LHB split -0.72, HR risk -0.72. tough split lane (-0.72); pitcher suppresses HR (-0.72).""", blast="good"),
        ],
    },
    {
        "title": "NYM @ TB - Justin Hagenman 🧤 (R, NYM) vs Griffin Jax (R, TB)",
        "description": "Tail key data: Park boost data unavailable. Hagenman 🧤 (HR risk 1.35, vs LHB +1.92, vs RHB +0.14). Jax (HR risk -0.07, vs LHB +0.28, vs RHB -0.43).",
        "rows": [
            row("Victor Mesa Jr.", "L", "+475", 96, "⭐ 🌕 💣", ["vs Hagenman"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.2 mph EV. Hagenman LHB split +1.92, HR risk 1.35.""", blast="high"),
            row("Jonathan Aranda", "L", "+500", 93, "🌕 💣", ["vs Hagenman"], """1 HR, 1 near-HR, 97.2 mph EV. Hagenman LHB split +1.92, HR risk 1.35.""", blast="good"),
            row("Liam Hicks", "L", "+900", 90, "🌕 💣", ["vs Hagenman"], """1 HR, 1 near-HR, 89.4 mph EV. Hagenman LHB split +1.92, HR risk 1.35.""", blast="good"),
            row("Francisco Lindor", "S", "+467", 80, "🌕 💣 💎", ["vs Jax"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 97.5 mph EV. Jax SHB→LHB split +0.28, HR risk -0.07. pitcher risk below avg (-0.07).""", blast="high"),
            row("Juan Soto", "L", "+373", 72, "⭐", ["vs Jax"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 96.1 mph EV. Jax LHB split +0.28, HR risk -0.07. pitcher risk below avg (-0.07).""", blast="good"),
            row("Luis Torrens", "R", "N/A", 58, "", ["vs Jax"], """1 HR, 1 near-HR, 93.5 mph EV. Jax RHB split -0.43, HR risk -0.07. tough split lane (-0.43); pitcher risk below avg (-0.07).""", blast="good"),
            row("Francisco Alvarez", "R", "+575", 58, "", ["vs Jax"], """0 HR, 1 near-HR, 91.0 mph EV. Jax RHB split -0.43, HR risk -0.07. tough split lane (-0.43); pitcher risk below avg (-0.07)."""),
        ],
    },
    {
        "title": "NYY @ LAA - Cam Schlittler (R, NYY) vs Reid Detmers (L, LAA)",
        "description": "Tail key data: Park boost data unavailable. Schlittler (HR risk -0.68, vs LHB -0.07, vs RHB -1.00). Detmers (HR risk -0.37, vs LHB -0.63, vs RHB -0.03).",
        "rows": [
            row("Josh Lowe", "L", "+870", 58, "", ["vs Schlittler"], """1 HR, 2 near-HR, 91.2 mph EV. Schlittler LHB split -0.07, HR risk -0.68. slight split headwind (-0.07); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Zach Neto", "R", "+547", 58, "", ["vs Schlittler"], """1 HR, 1 near-HR, 95.7 mph EV. Schlittler RHB split -1.00, HR risk -0.68. tough split lane (-1.00); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Christian Moore", "R", "+920", 58, "", ["vs Schlittler"], """1 HR, 2 near-HR, 92.4 mph EV. Schlittler RHB split -1.00, HR risk -0.68. tough split lane (-1.00); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Vaughn Grissom", "R", "+910", 58, "💎", ["vs Schlittler"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.3 mph EV. Schlittler RHB split -1.00, HR risk -0.68. tough split lane (-1.00); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Heliot Ramos", "R", "+450", 61, "⭐", ["vs Detmers"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.4 mph EV. Detmers RHB split -0.03, HR risk -0.37. slight split headwind (-0.03); pitcher risk below avg (-0.37).""", blast="good"),
            row("Ben Rice", "L", "+430", 58, "", ["vs Detmers"], """1 HR, 1 near-HR, 90.3 mph EV. Detmers LHB split -0.63, HR risk -0.37. tough split lane (-0.63); pitcher risk below avg (-0.37).""", blast="good"),
            row("Spencer Jones", "L", "+550", 58, "💎", ["vs Detmers"], """Worst Pickz Hidden Gem. 0 HR, 94.1 mph EV. Detmers LHB split -0.63, HR risk -0.37. tough split lane (-0.63); pitcher risk below avg (-0.37).""", blast="good"),
            row("Cody Bellinger", "L", "+600", 58, "💎", ["vs Detmers"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.4 mph EV. Detmers LHB split -0.63, HR risk -0.37. tough split lane (-0.63); pitcher risk below avg (-0.37).""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "+630", 58, "", ["vs Detmers"], """1 HR, 2 near-HR, 90.5 mph EV. Detmers LHB split -0.63, HR risk -0.37. tough split lane (-0.63); pitcher risk below avg (-0.37).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ ARI - Andrew Painter (R, PHI) vs Taylor Clarke 🧤 (R, ARI)",
        "description": "Tail key data: Park boost data unavailable. Painter (HR risk -0.28, vs LHB +0.07, vs RHB -0.53). Clarke 🧤 (HR risk 1.10, vs LHB +0.34, vs RHB +0.67).",
        "rows": [
            row("Lars Nootbaar", "L", "+725", 71, "🌕 💣 💎", ["vs Painter"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.5 mph EV. Painter LHB split +0.07, HR risk -0.28. pitcher risk below avg (-0.28).""", blast="high"),
            row("Tim Tawa", "R", "+900", 58, "", ["vs Painter"], """1 HR, 2 near-HR, 89.6 mph EV. Painter RHB split -0.53, HR risk -0.28. tough split lane (-0.53); pitcher risk below avg (-0.28).""", blast="good"),
            row("James McCann", "R", "+591", 58, "", ["vs Painter"], """0 HR, 95.6 mph EV. Painter RHB split -0.53, HR risk -0.28. tough split lane (-0.53); pitcher risk below avg (-0.28).""", blast="good"),
            row("Corbin Carroll", "L", "+520", 58, "", ["vs Painter"], """0 HR, 86.1 mph EV. Painter LHB split +0.07, HR risk -0.28. pitcher risk below avg (-0.28); limited recent HR events."""),
            row("Kyle Schwarber", "L", "+327", 89, "⭐ 🌕 💣", ["vs Clarke"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.0 mph EV. Clarke LHB split +0.34, HR risk 1.10.""", blast="high"),
            row("JT Realmuto", "R", "+1120", 79, "", ["vs Clarke"], """0 HR, 95.6 mph EV. Clarke RHB split +0.67, HR risk 1.10. limited recent HR events.""", blast="good"),
            row("Bryce Harper", "L", "+570", 75, "", ["vs Clarke"], """1 HR, 1 near-HR, 88.9 mph EV. Clarke LHB split +0.34, HR risk 1.10.""", blast="good"),
            row("Trea Turner", "R", "+890", 75, "", ["vs Clarke"], """0 HR, 92.1 mph EV. Clarke RHB split +0.67, HR risk 1.10. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "SD @ CIN - Casey Mize 🧤 (R, SD) vs Brandon Williamson (L, CIN)",
        "description": "Tail key data: Park boost data unavailable. Mize 🧤 (HR risk 1.03, vs LHB -0.27, vs RHB +2.26). Williamson (HR risk -0.20, vs LHB +0.70, vs RHB -0.26).",
        "rows": [
            row("Elly De La Cruz", "S", "+340", 92, "🚀 ⭐ 🌕 💣", ["vs Mize"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 101.5 mph EV. Mize SHB→RHB split +2.26, HR risk 1.03.""", blast="good"),
            row("Tyler Stephenson", "R", "+424", 91, "🌕 💣 💎", ["vs Mize"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.2 mph EV. Mize RHB split +2.26, HR risk 1.03.""", blast="good"),
            row("Sal Stewart", "R", "+381", 91, "🌕 💣", ["vs Mize"], """1 HR, 2 near-HR, 92.0 mph EV. Mize RHB split +2.26, HR risk 1.03.""", blast="good"),
            row("Ty France", "R", "+436", 58, "", ["vs Williamson"], """1 HR, 1 near-HR, 89.8 mph EV. Williamson RHB split -0.26, HR risk -0.20. slight split headwind (-0.26); pitcher risk below avg (-0.20).""", blast="good"),
            row("Jackson Merrill", "L", "+380", 58, "", ["vs Williamson"], """0 HR, 89.0 mph EV. Williamson LHB split +0.70, HR risk -0.20. pitcher risk below avg (-0.20); limited recent HR events."""),
        ],
    },
    {
        "title": "SEA @ BOS - Bryce Miller 🧤 (R, SEA) vs Patrick Sandoval (L, BOS)",
        "description": "Tail key data: Park boost data unavailable. Miller 🧤 (HR risk 1.14, vs LHB +1.09, vs RHB +0.45). Sandoval (HR risk -0.04, vs LHB -0.54, vs RHB +0.34).",
        "rows": [
            row("Mickey Gasper", "S", "+730", 95, "⭐ 🌕 💣", ["vs Miller"], """Worst Pickz Favorite. 4 HR, 4 near-HR, 92.2 mph EV. Miller SHB→LHB split +1.09, HR risk 1.14.""", blast="high"),
            row("Adley Rutschman", "S", "N/A", 81, "", ["vs Miller"], """1 HR, 2 near-HR, 87.0 mph EV. Miller SHB→LHB split +1.09, HR risk 1.14. lighter EV form (87.0 mph).""", blast="good"),
            row("Roman Anthony", "L", "+630", 84, "⭐", ["vs Miller"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 97.1 mph EV. Miller LHB split +1.09, HR risk 1.14. limited recent HR events.""", blast="good"),
            row("Jarren Duran", "L", "+630", 84, "💎", ["vs Miller"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.2 mph EV. Miller LHB split +1.09, HR risk 1.14. limited recent HR events.""", blast="good"),
            row("Cal Raleigh", "S", "+450", 66, "💎", ["vs Sandoval"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.5 mph EV. Sandoval SHB→RHB split +0.34, HR risk -0.04. pitcher risk below avg (-0.04).""", blast="good"),
            row("Randy Arozarena", "R", "+600", 70, "🌕 💣", ["vs Sandoval"], """2 HR, 2 near-HR, 89.5 mph EV. Sandoval RHB split +0.34, HR risk -0.04. pitcher risk below avg (-0.04).""", blast="high"),
            row("Julio Rodriguez", "R", "+561", 62, "⭐", ["vs Sandoval"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.6 mph EV. Sandoval RHB split +0.34, HR risk -0.04. pitcher risk below avg (-0.04); limited recent HR events.""", blast="good"),
            row("Patrick Wisdom", "R", "N/A", 59, "", ["vs Sandoval"], """0 HR, 93.7 mph EV. Sandoval RHB split +0.34, HR risk -0.04. pitcher risk below avg (-0.04); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "SF @ PIT - Landen Roupp (R, SF) vs Bubba Chandler (R, PIT)",
        "description": "Tail key data: Park boost data unavailable. Roupp (HR risk -0.64, vs LHB -0.43, vs RHB -0.54). Chandler (HR risk -1.01, vs LHB -0.20, vs RHB -1.33).",
        "rows": [
            row("Brandon Lowe", "L", "+493", 58, "💎", ["vs Roupp"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.1 mph EV. Roupp LHB split -0.43, HR risk -0.64. tough split lane (-0.43); pitcher suppresses HR (-0.64).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+630", 58, "", ["vs Roupp"], """0 HR, 92.9 mph EV. Roupp RHB split -0.54, HR risk -0.64. tough split lane (-0.54); pitcher suppresses HR (-0.64).""", blast="good"),
            row("Bryan Reynolds", "S", "+800", 58, "", ["vs Roupp"], """0 HR, 91.7 mph EV. Roupp SHB→LHB split -0.43, HR risk -0.64. tough split lane (-0.43); pitcher suppresses HR (-0.64)."""),
            row("Rafael Devers", "L", "+420", 63, "🚀 ⭐ 🌕 💣", ["vs Chandler"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 101.0 mph EV. Chandler LHB split -0.20, HR risk -1.01. slight split headwind (-0.20); pitcher suppresses HR (-1.01).""", blast="high"),
            row("Jung Hoo Lee", "L", "+1120", 58, "", ["vs Chandler"], """0 HR, 96.3 mph EV. Chandler LHB split -0.20, HR risk -1.01. slight split headwind (-0.20); pitcher suppresses HR (-1.01).""", blast="good"),
            row("Andrew Knizner", "R", "N/A", 58, "💎", ["vs Chandler"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.6 mph EV. Chandler RHB split -1.33, HR risk -1.01. tough split lane (-1.33); pitcher suppresses HR (-1.01).""", blast="good"),
        ],
    },
    {
        "title": "STL @ LAD - Brycen Mautz (L, STL) vs Yoshinobu Yamamoto (R, LAD)",
        "description": "Tail key data: Park boost data unavailable. Mautz (BAA vs LHB .400, vs RHB .312, HR/9 1.50). Yamamoto (HR risk -0.44, vs LHB -0.61, vs RHB +0.16).",
        "rows": [
            row("Teoscar Hernandez", "R", "+600", 68, "💎", ["vs Mautz"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 97.2 mph EV. limited split/risk sample.""", blast="good"),
            row("Will Smith", "R", "N/A", 60, "⭐", ["vs Mautz"], """Worst Pickz Favorite. 0 HR, 94.6 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Dalton Rushing", "L", "N/A", 59, "", ["vs Mautz"], """0 HR, 94.1 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Freddie Freeman", "L", "+580", 59, "", ["vs Mautz"], """0 HR, 93.6 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TOR @ CLE - Dylan Cease (R, TOR) vs Joey Cantillo (L, CLE)",
        "description": "Tail key data: Park boost data unavailable. Cease (HR risk -0.58, vs LHB -0.27, vs RHB -0.61). Cantillo (HR risk -0.08, vs LHB -0.20, vs RHB +0.10).",
        "rows": [
            row("Nathaniel Lowe", "L", "+660", 58, "", ["vs Cease"], """1 HR, 1 near-HR, 99.7 mph EV. Cease LHB split -0.27, HR risk -0.58. slight split headwind (-0.27); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Travis Bazzana", "L", "+900", 58, "", ["vs Cease"], """0 HR, 87.1 mph EV. Cease LHB split -0.27, HR risk -0.58. slight split headwind (-0.27); pitcher suppresses HR (-0.58)."""),
            row("Chase DeLauter", "L", "+610", 58, "", ["vs Cease"], """0 HR, 95.4 mph EV. Cease LHB split -0.27, HR risk -0.58. slight split headwind (-0.27); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Patrick Bailey", "S", "+900", 58, "", ["vs Cease"], """1 HR, 1 near-HR, 86.4 mph EV. Cease SHB→LHB split -0.27, HR risk -0.58. slight split headwind (-0.27); pitcher suppresses HR (-0.58).""", blast="good"),
            row("George Springer", "R", "+600", 62, "", ["vs Cantillo"], """1 HR, 1 near-HR, 93.8 mph EV. Cantillo RHB split +0.10, HR risk -0.08. pitcher risk below avg (-0.08).""", blast="good"),
            row("Kazuma Okamoto", "R", "+400", 69, "⭐", ["vs Cantillo"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 94.8 mph EV. Cantillo RHB split +0.10, HR risk -0.08. pitcher risk below avg (-0.08).""", blast="good"),
            row("Alejandro Kirk", "R", "+820", 58, "", ["vs Cantillo"], """0 HR, 91.7 mph EV. Cantillo RHB split +0.10, HR risk -0.08. pitcher risk below avg (-0.08); limited recent HR events."""),
            row("Brandon Valenzuela", "S", "N/A", 60, "", ["vs Cantillo"], """0 HR, 1 near-HR, 95.4 mph EV. Cantillo SHB→RHB split +0.10, HR risk -0.08. pitcher risk below avg (-0.08); limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-02")

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

    out = ROOT / '_games-0902.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
