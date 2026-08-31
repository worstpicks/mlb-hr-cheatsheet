#!/usr/bin/env python3
"""Generate games[] block for 2026-08-31 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Brady House (R)",
    "Bryce Harper (L)",
    "Colt Keith (L)",
    "Daylen Lile (L)",
    "Elly De La Cruz (S)",
    "Henry Bolte (R)",
    "Jackson Merrill (L)",
    "Jake Burger (R)",
    "Jonathan Aranda (L)",
    "Jung Hoo Lee (L)",
    "Kody Clemens (L)",
    "Kyle Stowers (L)",
    "Lars Nootbaar (L)",
    "Lawrence Butler (L)",
    "Mike Trout (R)",
    "Pete Crow Armstrong (L)",
    "Rafael Devers (L)",
    "Randy Arozarena (R)",
    "Tyler Stephenson (R)",
    "William Contreras (R)",
    "Wilyer Abreu (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Adley Rutschman (S)",
    "Andrew Pinckney (R)",
    "Blaze Alexander (R)",
    "Cal Raleigh (S)",
    "Christian Encarnacion-Strand (R)",
    "Christopher Morel (R)",
    "Corbin Carroll (L)",
    "Drew Cavanaugh (L)",
    "Griffin Conine (L)",
    "Jeremy Pena (R)",
    "Max Kepler (L)",
    "Roman Anthony (L)",
    "Sal Stewart (R)",
    "Spencer Torkelson (R)",
    "Tim Tawa (R)",
    "Tristan Peters (L)",
    "Zach Neto (R)",
    "Zack Gelof (R)",
}

PLAYER_TEAMS = {
    "AJ Ewing (L)": "NYM",
    "Adley Rutschman (S)": "BOS",
    "Alec Bohm (R)": "PHI",
    "Andres Chaparro (R)": "WSH",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Pinckney (R)": "WSH",
    "Austin Riley (R)": "ATL",
    "Blaze Alexander (R)": "BAL",
    "Bo Bichette (R)": "NYM",
    "Brady House (R)": "WSH",
    "Brandon Nimmo (L)": "TEX",
    "Brewer Hicklen (R)": "ATL",
    "Bryce Harper (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Cam Smith (R)": "HOU",
    "Cedric Mullins (L)": "TB",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Christopher Morel (R)": "NYM",
    "Colt Keith (L)": "DET",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Daylen Lile (L)": "WSH",
    "Derek Hill (R)": "PHI",
    "Drake Baldwin (L)": "ATL",
    "Drew Cavanaugh (L)": "SF",
    "Dylan Beavers (L)": "BAL",
    "Eduardo Valencia (R)": "DET",
    "Elly De La Cruz (S)": "CIN",
    "Griffin Conine (L)": "MIA",
    "Heliot Ramos (R)": "NYY",
    "Henry Bolte (R)": "ATH",
    "Hunter Goodman (R)": "COL",
    "Isaac Paredes (R)": "HOU",
    "JT Realmuto (R)": "PHI",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jake McCarthy (L)": "COL",
    "Jarren Duran (L)": "BOS",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jeremy Pena (R)": "HOU",
    "Jonathan Aranda (L)": "TB",
    "Juan Soto (L)": "NYM",
    "Julio Rodriguez (R)": "SEA",
    "Jung Hoo Lee (L)": "SF",
    "Junior Caminero (R)": "TB",
    "Kody Clemens (L)": "MIN",
    "Kyle Stowers (L)": "MIA",
    "Lars Nootbaar (L)": "ARI",
    "Lawrence Butler (L)": "ATH",
    "Luis Torrens (R)": "NYM",
    "Max Kepler (L)": "ARI",
    "Michael Busch (L)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Otto Lopez (R)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randy Arozarena (R)": "SEA",
    "Roman Anthony (L)": "BOS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Sal Stewart (R)": "CIN",
    "Sean Murphy (R)": "ATL",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Taylor Ward (R)": "SEA",
    "Tim Tawa (R)": "ARI",
    "Travis d'Arnaud (R)": "LAA",
    "Tristan Peters (L)": "CWS",
    "Tyler Stephenson (R)": "CIN",
    "Walker Jenkins (L)": "MIN",
    "William Contreras (R)": "MIL",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
    "Zac Veen (L)": "COL",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("NYM @ TB", "Seymour"),
    ("PHI @ ARI", "Nola"),
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
        "title": "ATH @ TEX - Gage Jump (L, ATH) vs Jacob deGrom (R, TEX)",
        "description": "Tail key data: Park boost -12% (stadium -11%, weather -1%). Jump (HR risk -0.68, vs LHB -0.88, vs RHB -0.10). deGrom (HR risk -0.42, vs LHB +0.10, vs RHB -0.68).",
        "rows": [
            row("Jake Burger", "R", "+457", 62, "⭐ 🌕 💣", ["vs Jump"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.8 mph EV. Jump RHB split -0.10, HR risk -0.68. slight split headwind (-0.10); pitcher suppresses HR (-0.68).""", blast="high"),
            row("Wyatt Langford", "R", "+561", 58, "", ["vs Jump"], """0 HR, 1 near-HR, 93.1 mph EV. Jump RHB split -0.10, HR risk -0.68. slight split headwind (-0.10); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Corey Seager", "L", "+360", 58, "", ["vs Jump"], """0 HR, 2 near-HR, 91.0 mph EV. Jump LHB split -0.88, HR risk -0.68. tough split lane (-0.88); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Brandon Nimmo", "L", "+630", 58, "", ["vs Jump"], """0 HR, 94.9 mph EV. Jump LHB split -0.88, HR risk -0.68. tough split lane (-0.88); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Henry Bolte", "R", "+950", 58, "⭐", ["vs deGrom"], """Worst Pickz Favorite. 0 HR, 96.2 mph EV. deGrom RHB split -0.68, HR risk -0.42. tough split lane (-0.68); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Lawrence Butler", "L", "+610", 58, "⭐", ["vs deGrom"], """Worst Pickz Favorite. 0 HR, 94.3 mph EV. deGrom LHB split +0.10, HR risk -0.42. pitcher suppresses HR (-0.42); park/weather net drag (-12%).""", blast="good"),
            row("Zack Gelof", "R", "+610", 58, "💎", ["vs deGrom"], """Worst Pickz Hidden Gem. 0 HR, 96.3 mph EV. deGrom RHB split -0.68, HR risk -0.42. tough split lane (-0.68); pitcher suppresses HR (-0.42).""", blast="good"),
        ],
    },
    {
        "title": "BAL @ COL - Kyle Bradish (R, BAL) vs Tanner Gordon (R, COL)",
        "description": "Tail key data: Park boost +7% (stadium +21%, weather -14%). Bradish (BAA vs LHB .261, vs RHB .256, HR/9 1.01). Gordon (HR risk 0.83, vs LHB +0.53, vs RHB +0.79).",
        "rows": [
            row("Jake McCarthy", "L", "+920", 66, "", ["vs Bradish"], """1 HR, 1 near-HR, 93.4 mph EV. limited split/risk sample; weather carry headwind (-14%).""", blast="good"),
            row("Hunter Goodman", "R", "+335", 65, "", ["vs Bradish"], """1 HR, 2 near-HR, 91.5 mph EV. limited split/risk sample; weather carry headwind (-14%).""", blast="good"),
            row("Mickey Moniak", "L", "+469", 58, "", ["vs Bradish"], """0 HR, 90.0 mph EV. limited split/risk sample; weather carry headwind (-14%)."""),
            row("Zac Veen", "L", "+1060", 62, "", ["vs Bradish"], """0 HR, 95.7 mph EV. limited split/risk sample; weather carry headwind (-14%).""", blast="good"),
            row("Blaze Alexander", "R", "N/A", 83, "💎", ["vs Gordon"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 99.4 mph EV. Gordon RHB split +0.79, HR risk 0.83. weather carry headwind (-14%).""", blast="good"),
            row("Pete Alonso", "R", "+224", 83, "🚀", ["vs Gordon"], """1 HR, 1 near-HR, 100.2 mph EV. Gordon RHB split +0.79, HR risk 0.83. weather carry headwind (-14%).""", blast="good"),
            row("Colton Cowser", "L", "+451", 75, "🚀", ["vs Gordon"], """0 HR, 101.1 mph EV. Gordon LHB split +0.53, HR risk 0.83. weather carry headwind (-14%); limited recent HR events.""", blast="good"),
            row("Dylan Beavers", "L", "+500", 66, "", ["vs Gordon"], """0 HR, 1 near-HR, 89.3 mph EV. Gordon LHB split +0.53, HR risk 0.83. weather carry headwind (-14%); limited recent HR events."""),
            row("Christian Encarnacion-Strand", "R", "+310", 68, "💎", ["vs Gordon"], """Worst Pickz Hidden Gem. 0 HR, 90.1 mph EV. Gordon RHB split +0.79, HR risk 0.83. weather carry headwind (-14%); limited recent HR events."""),
        ],
    },
    {
        "title": "CWS @ HOU - Anthony Kay (L, CWS) vs Peter Lambert (R, HOU)",
        "description": "Tail key data: Park boost +7% (stadium +7%, weather +0%). Kay (HR risk 0.27, vs LHB -1.39, vs RHB +0.79). Lambert (HR risk -0.66, vs LHB -0.30, vs RHB -0.62).",
        "rows": [
            row("Isaac Paredes", "R", "+475", 74, "", ["vs Kay"], """1 HR, 2 near-HR, 93.1 mph EV. Kay RHB split +0.79, HR risk 0.27.""", blast="good"),
            row("Jeremy Pena", "R", "+562", 70, "💎", ["vs Kay"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.3 mph EV. Kay RHB split +0.79, HR risk 0.27.""", blast="good"),
            row("Cam Smith", "R", "+610", 66, "", ["vs Kay"], """1 HR, 1 near-HR, 87.1 mph EV. Kay RHB split +0.79, HR risk 0.27. lighter EV form (87.1 mph).""", blast="good"),
            row("Yordan Alvarez", "L", "+325", 58, "⭐", ["vs Kay"], """Worst Pickz Favorite. 0 HR, 96.1 mph EV. Kay LHB split -1.39, HR risk 0.27. tough split lane (-1.39); limited recent HR events.""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 62, "", ["vs Kay"], """0 HR, 1 near-HR, 90.7 mph EV. Kay RHB split +0.79, HR risk 0.27. limited recent HR events."""),
            row("Andrew Benintendi", "L", "+564", 58, "", ["vs Lambert"], """1 HR, 2 near-HR, 93.1 mph EV. Lambert LHB split -0.30, HR risk -0.66. slight split headwind (-0.30); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Munetaka Murakami", "L", "+300", 58, "", ["vs Lambert"], """0 HR, 90.9 mph EV. Lambert LHB split -0.30, HR risk -0.66. slight split headwind (-0.30); pitcher suppresses HR (-0.66)."""),
            row("Tristan Peters", "L", "+870", 58, "💎", ["vs Lambert"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 88.7 mph EV. Lambert LHB split -0.30, HR risk -0.66. slight split headwind (-0.30); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Miguel Vargas", "R", "+400", 58, "", ["vs Lambert"], """0 HR, 89.7 mph EV. Lambert RHB split -0.62, HR risk -0.66. tough split lane (-0.62); pitcher suppresses HR (-0.66)."""),
        ],
    },
    {
        "title": "DET @ MIN - Jackson Jobe (R, DET) vs Taj Bradley (R, MIN)",
        "description": "Tail key data: Park boost -7% (stadium -8%, weather +1%). Jobe (HR risk -0.18, vs LHB +0.69, vs RHB -1.65). Bradley (HR risk 0.24, vs LHB +0.78, vs RHB -0.63).",
        "rows": [
            row("Kody Clemens", "L", "+390", 73, "⭐", ["vs Jobe"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 96.0 mph EV. Jobe LHB split +0.69, HR risk -0.18. pitcher risk below avg (-0.18); park/weather net drag (-7%).""", blast="good"),
            row("Walker Jenkins", "L", "+825", 58, "", ["vs Jobe"], """0 HR, 90.4 mph EV. Jobe LHB split +0.69, HR risk -0.18. pitcher risk below avg (-0.18); park/weather net drag (-7%)."""),
            row("Colt Keith", "L", "+675", 66, "⭐", ["vs Bradley"], """Worst Pickz Favorite. 0 HR, 95.9 mph EV. Bradley LHB split +0.78, HR risk 0.24. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
            row("Spencer Torkelson", "R", "+525", 58, "💎", ["vs Bradley"], """Worst Pickz Hidden Gem. 0 HR, 96.7 mph EV. Bradley RHB split -0.63, HR risk 0.24. tough split lane (-0.63); park/weather net drag (-7%).""", blast="good"),
            row("Eduardo Valencia", "R", "+405", 58, "", ["vs Bradley"], """0 HR, 1 near-HR, 91.7 mph EV. Bradley RHB split -0.63, HR risk 0.24. tough split lane (-0.63); park/weather net drag (-7%)."""),
        ],
    },
    {
        "title": "MIA @ WSH - Ryan Gusto (R, MIA) vs Will Dion (L, WSH)",
        "description": "Tail key data: Park boost +9% (stadium +4%, weather +5%). Gusto (HR risk 0.44, vs LHB -0.17, vs RHB +0.92). Dion (HR risk 0.55, vs LHB +0.87, vs RHB +0.07).",
        "rows": [
            row("Andrew Pinckney", "R", "N/A", 73, "💎", ["vs Gusto"], """Worst Pickz Hidden Gem. 0 HR, 93.4 mph EV. Gusto RHB split +0.92, HR risk 0.44. limited recent HR events.""", blast="good"),
            row("Brady House", "R", "+675", 77, "⭐", ["vs Gusto"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.4 mph EV. Gusto RHB split +0.92, HR risk 0.44.""", blast="good"),
            row("Andres Chaparro", "R", "+493", 66, "", ["vs Gusto"], """0 HR, 1 near-HR, 89.2 mph EV. Gusto RHB split +0.92, HR risk 0.44. limited recent HR events."""),
            row("Daylen Lile", "L", "+462", 66, "⭐", ["vs Gusto"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 89.3 mph EV. Gusto LHB split -0.17, HR risk 0.44. slight split headwind (-0.17).""", blast="good"),
            row("Kyle Stowers", "L", "+398", 79, "⭐", ["vs Dion"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 97.8 mph EV. Dion LHB split +0.87, HR risk 0.55.""", blast="good"),
            row("Griffin Conine", "L", "N/A", 68, "💎", ["vs Dion"], """Worst Pickz Hidden Gem. 0 HR, 91.9 mph EV. Dion LHB split +0.87, HR risk 0.55. limited recent HR events."""),
            row("Otto Lopez", "R", "+600", 74, "", ["vs Dion"], """1 HR, 2 near-HR, 93.0 mph EV. Dion RHB split +0.07, HR risk 0.55.""", blast="good"),
        ],
    },
    {
        "title": "MIL @ CHC - Kyle Harrison (L, MIL) vs Clay Holmes (R, CHC)",
        "description": "Tail key data: Park boost +47% (stadium -2%, weather +49%). Harrison (HR risk 0.61, vs LHB -0.94, vs RHB +1.02). Holmes (HR risk -1.31, vs LHB -0.74, vs RHB -0.83).",
        "rows": [
            row("Pete Crow Armstrong", "L", "+300", 92, "⭐ 🌕 💣", ["vs Harrison"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 98.3 mph EV. Harrison LHB split -0.94, HR risk 0.61. tough split lane (-0.94).""", blast="high"),
            row("Michael Busch", "L", "+523", 79, "", ["vs Harrison"], """1 HR, 2 near-HR, 96.4 mph EV. Harrison LHB split -0.94, HR risk 0.61. tough split lane (-0.94).""", blast="good"),
            row("Michael Conforto", "L", "N/A", 78, "🚀", ["vs Harrison"], """1 HR, 1 near-HR, 106.4 mph EV. Harrison LHB split -0.94, HR risk 0.61. tough split lane (-0.94).""", blast="good"),
            row("William Contreras", "R", "+560", 59, "⭐", ["vs Holmes"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.7 mph EV. Holmes RHB split -0.83, HR risk -1.31. tough split lane (-0.83); pitcher suppresses HR (-1.31).""", blast="good"),
            row("Jackson Chourio", "R", "+424", 58, "", ["vs Holmes"], """1 HR, 1 near-HR, 98.1 mph EV. Holmes RHB split -0.83, HR risk -1.31. tough split lane (-0.83); pitcher suppresses HR (-1.31).""", blast="good"),
            row("Jake Bauers", "L", "+407", 58, "", ["vs Holmes"], """0 HR, 1 near-HR, 88.9 mph EV. Holmes LHB split -0.74, HR risk -1.31. tough split lane (-0.74); pitcher suppresses HR (-1.31)."""),
        ],
    },
    {
        "title": "NYM @ TB - Robert Stock (R, NYM) vs Ian Seymour 🧤 (L, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Stock (HR risk -0.18, vs LHB -0.02, vs RHB -0.74). Seymour 🧤 (HR risk 1.30, vs LHB +0.90, vs RHB +0.88).",
        "rows": [
            row("Jonathan Aranda", "L", "+650", 62, "⭐", ["vs Stock"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.4 mph EV. Stock LHB split -0.02, HR risk -0.18. slight split headwind (-0.02); pitcher risk below avg (-0.18).""", blast="good"),
            row("Junior Caminero", "R", "+320", 58, "", ["vs Stock"], """1 HR, 1 near-HR, 95.6 mph EV. Stock RHB split -0.74, HR risk -0.18. tough split lane (-0.74); pitcher risk below avg (-0.18).""", blast="good"),
            row("Cedric Mullins", "L", "+600", 58, "", ["vs Stock"], """0 HR, 1 near-HR, 91.9 mph EV. Stock LHB split -0.02, HR risk -0.18. slight split headwind (-0.02); pitcher risk below avg (-0.18)."""),
            row("Luis Torrens", "R", "+1000", 90, "🌕 💣", ["vs Seymour"], """2 HR, 2 near-HR, 90.2 mph EV. Seymour RHB split +0.88, HR risk 1.30.""", blast="high"),
            row("AJ Ewing", "L", "+1060", 80, "", ["vs Seymour"], """0 HR, 1 near-HR, 92.6 mph EV. Seymour LHB split +0.90, HR risk 1.30. limited recent HR events.""", blast="good"),
            row("Christopher Morel", "R", "+576", 83, "💎", ["vs Seymour"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 97.8 mph EV. Seymour RHB split +0.88, HR risk 1.30. limited recent HR events.""", blast="good"),
            row("Bo Bichette", "R", "+600", 73, "", ["vs Seymour"], """0 HR, 90.7 mph EV. Seymour RHB split +0.88, HR risk 1.30. limited recent HR events."""),
            row("Juan Soto", "L", "+357", 74, "", ["vs Seymour"], """0 HR, 91.7 mph EV. Seymour LHB split +0.90, HR risk 1.30. limited recent HR events."""),
        ],
    },
    {
        "title": "NYY @ LAA - Elmer Rodríguez (R, NYY) vs Walbert Urena (R, LAA)",
        "description": "Tail key data: Park boost -5% (stadium -9%, weather +4%). Rodríguez (HR risk -0.80, vs LHB +0.10, vs RHB -0.82). Urena (HR risk -1.50, vs LHB -1.33, vs RHB -0.26).",
        "rows": [
            row("Zach Neto", "R", "+506", 58, "💎", ["vs Rodríguez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.3 mph EV. Rodríguez RHB split -0.82, HR risk -0.80. tough split lane (-0.82); pitcher suppresses HR (-0.80).""", blast="good"),
            row("Mike Trout", "R", "+490", 58, "⭐", ["vs Rodríguez"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 98.6 mph EV. Rodríguez RHB split -0.82, HR risk -0.80. tough split lane (-0.82); pitcher suppresses HR (-0.80).""", blast="good"),
            row("Travis d'Arnaud", "R", "N/A", 58, "", ["vs Rodríguez"], """0 HR, 90.5 mph EV. Rodríguez RHB split -0.82, HR risk -0.80. tough split lane (-0.82); pitcher suppresses HR (-0.80)."""),
            row("Spencer Jones", "L", "+560", 58, "", ["vs Urena"], """0 HR, 94.9 mph EV. Urena LHB split -1.33, HR risk -1.50. tough split lane (-1.33); pitcher suppresses HR (-1.50).""", blast="good"),
            row("Heliot Ramos", "R", "N/A", 58, "", ["vs Urena"], """0 HR, 1 near-HR, 92.9 mph EV. Urena RHB split -0.26, HR risk -1.50. slight split headwind (-0.26); pitcher suppresses HR (-1.50).""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "+600", 58, "", ["vs Urena"], """0 HR, 86.1 mph EV. Urena LHB split -1.33, HR risk -1.50. tough split lane (-1.33); pitcher suppresses HR (-1.50)."""),
        ],
    },
    {
        "title": "PHI @ ARI - Aaron Nola 🧤 (R, PHI) vs Brandon Pfaadt (R, ARI)",
        "description": "Tail key data: Park boost -9% (stadium -9%, weather +0%). Nola 🧤 (HR risk 1.23, vs LHB +0.75, vs RHB +0.90). Pfaadt (BAA vs LHB .262, vs RHB .205, HR/9 1.03).",
        "rows": [
            row("Lars Nootbaar", "L", "+630", 91, "⭐ 🌕 💣", ["vs Nola"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.5 mph EV. Nola LHB split +0.75, HR risk 1.23. park/weather net drag (-9%).""", blast="high"),
            row("Corbin Carroll", "L", "+532", 81, "💎", ["vs Nola"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.8 mph EV. Nola LHB split +0.75, HR risk 1.23. park/weather net drag (-9%).""", blast="good"),
            row("Max Kepler", "L", "+870", 69, "💎", ["vs Nola"], """Worst Pickz Hidden Gem. 0 HR, 90.5 mph EV. Nola LHB split +0.75, HR risk 1.23. park/weather net drag (-9%); limited recent HR events."""),
            row("Tim Tawa", "R", "+980", 80, "💎", ["vs Nola"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 92.8 mph EV. Nola RHB split +0.90, HR risk 1.23. park/weather net drag (-9%).""", blast="good"),
            row("Bryce Harper", "L", "+525", 74, "⭐ 🌕 💣", ["vs Pfaadt"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.1 mph EV. limited split/risk sample; park/weather net drag (-9%).""", blast="high"),
            row("JT Realmuto", "R", "+1100", 60, "", ["vs Pfaadt"], """1 HR, 1 near-HR, 92.2 mph EV. limited split/risk sample; park/weather net drag (-9%).""", blast="good"),
            row("Alec Bohm", "R", "+1040", 58, "", ["vs Pfaadt"], """0 HR, 82.5 mph EV. limited split/risk sample; park/weather net drag (-9%)."""),
            row("Derek Hill", "R", "N/A", 58, "", ["vs Pfaadt"], """1 HR, 1 near-HR, 86.2 mph EV. limited split/risk sample; park/weather net drag (-9%).""", blast="good"),
        ],
    },
    {
        "title": "SD @ CIN - Michael King (R, SD) vs Brady Singer (R, CIN)",
        "description": "Tail key data: Park boost +17% (stadium +14%, weather +3%). King (HR risk 0.06, vs LHB +0.26, vs RHB -0.33). Singer (HR risk 0.87, vs LHB +0.83, vs RHB +0.04).",
        "rows": [
            row("Tyler Stephenson", "R", "+493", 65, "⭐", ["vs King"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.6 mph EV. King RHB split -0.33, HR risk 0.06. slight split headwind (-0.33).""", blast="good"),
            row("Elly De La Cruz", "S", "+380", 63, "⭐", ["vs King"], """Worst Pickz Favorite. 0 HR, 93.5 mph EV. King SHB→LHB split +0.26, HR risk 0.06. limited recent HR events.""", blast="good"),
            row("Sal Stewart", "R", "+420", 69, "🌕 💣 💎", ["vs King"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 89.2 mph EV. King RHB split -0.33, HR risk 0.06. slight split headwind (-0.33).""", blast="high"),
            row("Jackson Merrill", "L", "+317", 86, "⭐", ["vs Singer"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.3 mph EV. Singer LHB split +0.83, HR risk 0.87.""", blast="good"),
        ],
    },
    {
        "title": "SEA @ BOS - George Kirby (R, SEA) vs Payton Tolle (L, BOS)",
        "description": "Tail key data: Park boost +2% (stadium -8%, weather +10%). Kirby (HR risk -0.74, vs LHB -0.15, vs RHB -0.60). Tolle (HR risk -0.17, vs LHB +0.35, vs RHB +0.01).",
        "rows": [
            row("Adley Rutschman", "S", "+900", 58, "💎", ["vs Kirby"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.9 mph EV. Kirby SHB→LHB split -0.15, HR risk -0.74. slight split headwind (-0.15); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Wilyer Abreu", "L", "+450", 58, "⭐", ["vs Kirby"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 94.5 mph EV. Kirby LHB split -0.15, HR risk -0.74. slight split headwind (-0.15); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Jarren Duran", "L", "+575", 58, "", ["vs Kirby"], """1 HR, 2 near-HR, 90.4 mph EV. Kirby LHB split -0.15, HR risk -0.74. slight split headwind (-0.15); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Roman Anthony", "L", "+600", 58, "💎", ["vs Kirby"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.4 mph EV. Kirby LHB split -0.15, HR risk -0.74. slight split headwind (-0.15); pitcher suppresses HR (-0.74).""", blast="good"),
            row("Randy Arozarena", "R", "+514", 73, "🚀 ⭐ 🌕 💣", ["vs Tolle"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 101.2 mph EV. Tolle RHB split +0.01, HR risk -0.17. pitcher risk below avg (-0.17); park suppresses carry (-8%).""", blast="high"),
            row("Cal Raleigh", "S", "+450", 62, "💎", ["vs Tolle"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.8 mph EV. Tolle SHB→LHB split +0.35, HR risk -0.17. pitcher risk below avg (-0.17); park suppresses carry (-8%).""", blast="good"),
            row("Julio Rodriguez", "R", "+434", 60, "", ["vs Tolle"], """0 HR, 2 near-HR, 94.5 mph EV. Tolle RHB split +0.01, HR risk -0.17. pitcher risk below avg (-0.17); park suppresses carry (-8%).""", blast="good"),
            row("Taylor Ward", "R", "+700", 58, "", ["vs Tolle"], """0 HR, 93.2 mph EV. Tolle RHB split +0.01, HR risk -0.17. pitcher risk below avg (-0.17); park suppresses carry (-8%).""", blast="good"),
        ],
    },
    {
        "title": "SF @ ATL - Anthony Molina (R, SF) vs Bryce Elder (R, ATL)",
        "description": "Tail key data: Park boost +12% (stadium -1%, weather +12%). Molina (HR risk 0.33, vs LHB -0.14, vs RHB +1.72). Elder (HR risk -0.09, vs LHB -0.10, vs RHB +0.13).",
        "rows": [
            row("Sean Murphy", "R", "+630", 79, "", ["vs Molina"], """1 HR, 1 near-HR, 90.5 mph EV. Molina RHB split +1.72, HR risk 0.33.""", blast="good"),
            row("Austin Riley", "R", "+475", 79, "", ["vs Molina"], """0 HR, 1 near-HR, 94.4 mph EV. Molina RHB split +1.72, HR risk 0.33. limited recent HR events.""", blast="good"),
            row("Drake Baldwin", "L", "+440", 65, "", ["vs Molina"], """0 HR, 1 near-HR, 95.5 mph EV. Molina LHB split -0.14, HR risk 0.33. slight split headwind (-0.14); limited recent HR events.""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+408", 73, "", ["vs Molina"], """0 HR, 2 near-HR, 86.9 mph EV. Molina RHB split +1.72, HR risk 0.33. lighter EV form (86.9 mph).""", blast="good"),
            row("Brewer Hicklen", "R", "N/A", 79, "🚀", ["vs Molina"], """0 HR, 101.4 mph EV. Molina RHB split +1.72, HR risk 0.33. limited recent HR events.""", blast="good"),
            row("Rafael Devers", "L", "+308", 62, "⭐", ["vs Elder"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 99.7 mph EV. Elder LHB split -0.10, HR risk -0.09. slight split headwind (-0.10); pitcher risk below avg (-0.09).""", blast="good"),
            row("Jung Hoo Lee", "L", "+1100", 62, "⭐", ["vs Elder"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.4 mph EV. Elder LHB split -0.10, HR risk -0.09. slight split headwind (-0.10); pitcher risk below avg (-0.09).""", blast="good"),
            row("Drew Cavanaugh", "L", "+900", 62, "💎", ["vs Elder"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 97.6 mph EV. Elder LHB split -0.10, HR risk -0.09. slight split headwind (-0.10); pitcher risk below avg (-0.09).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-31")

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

    out = ROOT / '_games-0831.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
