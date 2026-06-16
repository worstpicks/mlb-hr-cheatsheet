#!/usr/bin/env python3
"""Generate games[] block for 2026-06-16 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Alejandro Kirk (R)",
    "Bobby Witt Jr. (R)",
    "Bryce Eldridge (L)",
    "Bryce Harper (L)",
    "Dominic Canzone (L)",
    "Eugenio Suarez (R)",
    "Jake Bauers (L)",
    "James Wood (L)",
    "Ketel Marte (S)",
    "Matt McLain (R)",
    "Mike Trout (R)",
    "Seiya Suzuki (R)",
}

GEMS = {
    "Andrew Benintendi (L)",
    "Braden Montgomery (S)",
    "Cam Smith (R)",
    "Colt Emerson (L)",
    "Endy Rodriguez (S)",
    "Juan Soto (L)",
    "Junior Caminero (R)",
    "Kyle Manzardo (L)",
    "LuJames Groover (R)",
    "Nick Kurtz (L)",
    "Riley Greene (L)",
    "Tristan Peters (L)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Alejandro Kirk (R)": "TOR",
    "Andrew Benintendi (L)": "CWS",
    "Andy Pages (R)": "LAD",
    "Ben Rice (L)": "NYY",
    "Bo Bichette (R)": "NYM",
    "Bobby Witt Jr. (R)": "KC",
    "Braden Montgomery (S)": "CWS",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Brooks Lee (S)": "MIN",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "Cam Smith (R)": "HOU",
    "Christian Walker (R)": "HOU",
    "Christopher Morel (R)": "MIA",
    "Colson Montgomery (L)": "CWS",
    "Colt Emerson (L)": "SEA",
    "Colt Keith (L)": "DET",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "Daniel Schneemann (L)": "CLE",
    "Daylen Lile (L)": "WSH",
    "Dominic Canzone (L)": "SEA",
    "Donovan Walton (L)": "LAA",
    "Endy Rodriguez (S)": "PIT",
    "Esteury Ruiz (R)": "MIA",
    "Eugenio Suarez (R)": "CIN",
    "Ezequiel Tovar (R)": "COL",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Gabriel Rincones Jr. (L)": "PHI",
    "Garrett Mitchell (L)": "MIL",
    "Gary Sanchez (R)": "MIL",
    "Gavin Sheets (L)": "SD",
    "Henry Davis (R)": "PIT",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "J.T. Realmuto (R)": "PHI",
    "Jackson Chourio (R)": "MIL",
    "Jackson Holliday (L)": "BAL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Joc Pederson (L)": "TEX",
    "Jordan Walker (R)": "STL",
    "Jose Siri (R)": "LAA",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Tucker (L)": "LAD",
    "Lars Nootbaar (L)": "STL",
    "Logan O'Hoppe (R)": "LAA",
    "LuJames Groover (R)": "ARI",
    "Luis Garcia Jr. (L)": "WSH",
    "Matt Chapman (R)": "SF",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Michael Busch (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Miguel Amaya (R)": "CHC",
    "Mike Trout (R)": "LAA",
    "Nick Kurtz (L)": "ATH",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Riley Greene (L)": "DET",
    "Royce Lewis (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Ryan Vilade (R)": "TB",
    "Sal Stewart (R)": "CIN",
    "Seiya Suzuki (R)": "CHC",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Tristan Peters (L)": "CWS",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Yandy Diaz (R)": "TB",
    "Yohendrick Pinango (L)": "TOR",
    "Yordan Alvarez (L)": "HOU",
}

BUM_RISK_MIN = 0.95

BUM_PITCHERS = {
    "Cabrera",
    "Gasser",
    "Matthews",
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
        "title": "BAL @ SEA - Brandon Young (R, BAL) vs Logan Gilbert (R, SEA)",
        "description": "Tail key data: Park boost -8% (stadium +1%, weather -9%). Young (HR risk -0.24, vs LHB -0.29, vs RHB +0.02). Gilbert (HR risk 0.54, vs LHB +0.75, vs RHB +0.24).",
        "rows": [
            row("Dominic Canzone", "L", "+475", 90, "⭐ 🌕 💣", ["vs Young"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 97.5 mph EV. Young LHB split -0.29, HR risk -0.24. slight split headwind (-0.29); pitcher risk below avg (-0.24).""", blast="high"),
            row("Colt Emerson", "L", "+720", 84, "🌕 💣 💎", ["vs Young"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 84.0 mph EV. Young LHB split -0.29, HR risk -0.24. slight split headwind (-0.29); pitcher risk below avg (-0.24).""", blast="high"),
            row("Pete Alonso", "R", "+333", 83, "🌕 💣", ["vs Gilbert"], """2 HR, 2 near-HR, 92.9 mph EV. Gilbert RHB split +0.24, HR risk 0.54. park/weather net drag (-8%).""", blast="high"),
            row("Jackson Holliday", "L", "+1020", 75, "", ["vs Gilbert"], """1 HR, 3 near-HR, 89.3 mph EV. Gilbert LHB split +0.75, HR risk 0.54. park/weather net drag (-8%).""", blast="good"),
            row("Colton Cowser", "L", "+730", 81, "🌕 💣", ["vs Gilbert"], """2 HR, 3 near-HR, 88.7 mph EV. Gilbert LHB split +0.75, HR risk 0.54. park/weather net drag (-8%).""", blast="high"),
        ],
    },
    {
        "title": "CLE @ MIL - Slade Cecconi (R, CLE) vs Robert Gasser 🧤 (L, MIL)",
        "description": "Tail key data: Park boost +19% (stadium +9%, weather +10%). Cecconi (HR risk -0.42, vs LHB -0.45, vs RHB -0.02). Gasser 🧤 (HR risk 1.33, vs LHB +1.43, vs RHB +0.97).",
        "rows": [
            row("Jake Bauers", "L", "+490", 96, "⭐ 🌕 💣", ["vs Cecconi"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 99.8 mph EV. Cecconi LHB split -0.45, HR risk -0.42. tough split lane (-0.45); pitcher suppresses HR (-0.42).""", blast="high"),
            row("Gary Sanchez", "R", "N/A", 88, "🌕 💣", ["vs Cecconi"], """2 HR, 3 near-HR, 96.4 mph EV. Cecconi RHB split -0.02, HR risk -0.42. slight split headwind (-0.02); pitcher suppresses HR (-0.42).""", blast="high"),
            row("Jackson Chourio", "R", "+420", 92, "🌕 💣", ["vs Cecconi"], """4 HR, 3 near-HR, 92.3 mph EV. Cecconi RHB split -0.02, HR risk -0.42. slight split headwind (-0.02); pitcher suppresses HR (-0.42).""", blast="high"),
            row("Garrett Mitchell", "L", "+590", 74, "", ["vs Cecconi"], """0 HR, 3 near-HR, 92.3 mph EV. Cecconi LHB split -0.45, HR risk -0.42. tough split lane (-0.45); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Kyle Manzardo", "L", "N/A", 64, "💎", ["vs Gasser"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 88.3 mph EV. Gasser LHB split +1.43, HR risk 1.33. limited recent HR events."""),
            row("Daniel Schneemann", "L", "N/A", 71, "", ["vs Gasser"], """1 HR, 1 near-HR, 89.1 mph EV. Gasser LHB split +1.43, HR risk 1.33.""", blast="good"),
        ],
    },
    {
        "title": "COL @ CHC - Ryan Feltner (R, COL) vs Edward Cabrera 🧤 (R, CHC)",
        "description": "Tail key data: Park boost +20% (stadium -1%, weather +21%). Feltner (HR risk 0.21, vs LHB +0.21, vs RHB +0.15). Cabrera 🧤 (HR risk 1.45, vs LHB +0.52, vs RHB +2.09).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+330", 80, "🌕 💣", ["vs Feltner"], """2 HR, 3 near-HR, 87.5 mph EV. Feltner LHB split +0.21, HR risk 0.21. lighter EV form (87.5 mph).""", blast="high"),
            row("Michael Busch", "L", "+427", 78, "", ["vs Feltner"], """1 HR, 3 near-HR, 92.3 mph EV. Feltner LHB split +0.21, HR risk 0.21.""", blast="good"),
            row("Miguel Amaya", "R", "N/A", 74, "", ["vs Feltner"], """1 HR, 3 near-HR, 85.3 mph EV. Feltner RHB split +0.15, HR risk 0.21. lighter EV form (85.3 mph).""", blast="good"),
            row("Seiya Suzuki", "R", "+363", 85, "⭐ 🌕 💣", ["vs Feltner"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 92.8 mph EV. Feltner RHB split +0.15, HR risk 0.21.""", blast="high"),
            row("Hunter Goodman", "R", "+310", 90, "🌕 💣", ["vs Cabrera"], """4 HR, 3 near-HR, 90.1 mph EV. Cabrera RHB split +2.09, HR risk 1.45.""", blast="high"),
            row("Ezequiel Tovar", "R", "+640", 77, "", ["vs Cabrera"], """1 HR, 2 near-HR, 92.8 mph EV. Cabrera RHB split +2.09, HR risk 1.45.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ NYY - Davis Martin (R, CWS) vs Gerrit Cole (R, NYY)",
        "description": "Tail key data: Park boost data unavailable. Martin (HR risk -0.87, vs LHB -0.75, vs RHB -0.57). Cole (HR risk -0.50, vs LHB -0.65, vs RHB +0.17).",
        "rows": [
            row("Ben Rice", "L", "+300", 75, "", ["vs Martin"], """1 HR, 1 near-HR, 93.3 mph EV. Martin LHB split -0.75, HR risk -0.87. tough split lane (-0.75); pitcher suppresses HR (-0.87).""", blast="good"),
            row("Spencer Jones", "L", "+552", 82, "", ["vs Martin"], """1 HR, 1 near-HR, 99.6 mph EV. Martin LHB split -0.75, HR risk -0.87. tough split lane (-0.75); pitcher suppresses HR (-0.87).""", blast="good"),
            row("Ryan McMahon", "L", "+526", 72, "", ["vs Martin"], """1 HR, 1 near-HR, 89.9 mph EV. Martin LHB split -0.75, HR risk -0.87. tough split lane (-0.75); pitcher suppresses HR (-0.87).""", blast="good"),
            row("Andrew Benintendi", "L", "+487", 97, "🌕 💣 💎", ["vs Cole"], """Worst Pickz Hidden Gem. 4 HR, 5 near-HR, 92.9 mph EV. Cole LHB split -0.65, HR risk -0.50. tough split lane (-0.65); pitcher suppresses HR (-0.50).""", blast="high"),
            row("Braden Montgomery", "S", "+650", 83, "💎", ["vs Cole"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 98.7 mph EV. Cole RHB split +0.17, HR risk -0.50. pitcher suppresses HR (-0.50).""", blast="good"),
            row("Tristan Peters", "L", "+900", 76, "💎", ["vs Cole"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 92.0 mph EV. Cole LHB split -0.65, HR risk -0.50. tough split lane (-0.65); pitcher suppresses HR (-0.50).""", blast="good"),
            row("Colson Montgomery", "L", "+332", 80, "🌕 💣", ["vs Cole"], """2 HR, 2 near-HR, 90.2 mph EV. Cole LHB split -0.65, HR risk -0.50. tough split lane (-0.65); pitcher suppresses HR (-0.50).""", blast="high"),
        ],
    },
    {
        "title": "DET @ HOU - Framber Valdez (L, DET) vs Hunter Brown (R, HOU)",
        "description": "Tail key data: Park boost +3% (stadium +4%, weather -1%). Valdez (HR risk -0.21, vs LHB -0.26, vs RHB -0.03). Brown (HR risk -1.66, vs LHB -0.82, vs RHB -1.51).",
        "rows": [
            row("Cam Smith", "R", "+760", 82, "🚀 💎", ["vs Valdez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 100.1 mph EV. Valdez RHB split -0.03, HR risk -0.21. slight split headwind (-0.03); pitcher risk below avg (-0.21).""", blast="good"),
            row("Yordan Alvarez", "L", "+331", 63, "", ["vs Valdez"], """0 HR, 88.8 mph EV. Valdez LHB split -0.26, HR risk -0.21. slight split headwind (-0.26); pitcher risk below avg (-0.21)."""),
            row("Christian Walker", "R", "+410", 71, "", ["vs Valdez"], """1 HR, 1 near-HR, 89.1 mph EV. Valdez RHB split -0.03, HR risk -0.21. slight split headwind (-0.03); pitcher risk below avg (-0.21).""", blast="good"),
            row("Colt Keith", "L", "+920", 86, "🌕 💣", ["vs Brown"], """2 HR, 4 near-HR, 91.7 mph EV. Brown LHB split -0.82, HR risk -1.66. tough split lane (-0.82); pitcher suppresses HR (-1.66).""", blast="high"),
            row("Spencer Torkelson", "R", "+500", 84, "🌕 💣", ["vs Brown"], """2 HR, 2 near-HR, 94.0 mph EV. Brown RHB split -1.51, HR risk -1.66. tough split lane (-1.51); pitcher suppresses HR (-1.66).""", blast="high"),
            row("Riley Greene", "L", "+540", 88, "🌕 💣 💎", ["vs Brown"], """Worst Pickz Hidden Gem. 2 HR, 4 near-HR, 93.5 mph EV. Brown LHB split -0.82, HR risk -1.66. tough split lane (-0.82); pitcher suppresses HR (-1.66).""", blast="high"),
        ],
    },
    {
        "title": "KC @ WSH - Michael Wacha (R, KC) vs Foster Griffin (L, WSH)",
        "description": "Tail key data: Park boost data unavailable. Wacha (HR risk -0.52, vs LHB -0.03, vs RHB -0.79). Griffin (HR risk 0.81, vs LHB -0.77, vs RHB +1.45).",
        "rows": [
            row("James Wood", "L", "+333", 85, "⭐ 🌕 💣", ["vs Wacha"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 93.3 mph EV. Wacha LHB split -0.03, HR risk -0.52. slight split headwind (-0.03); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Luis Garcia Jr.", "L", "+525", 91, "🌕 💣", ["vs Wacha"], """3 HR, 4 near-HR, 93.0 mph EV. Wacha LHB split -0.03, HR risk -0.52. slight split headwind (-0.03); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Daylen Lile", "L", "+710", 76, "", ["vs Wacha"], """1 HR, 2 near-HR, 92.1 mph EV. Wacha LHB split -0.03, HR risk -0.52. slight split headwind (-0.03); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Bobby Witt Jr.", "R", "+425", 76, "⭐", ["vs Griffin"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 96.1 mph EV. Griffin RHB split +1.45, HR risk 0.81.""", blast="good"),
        ],
    },
    {
        "title": "LAA @ ARI - Reid Detmers (L, LAA) vs Merrill Kelly (R, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -7%, weather +0%). Detmers (HR risk -0.25, vs LHB -0.89, vs RHB +0.09). Kelly (HR risk 0.63, vs LHB +1.10, vs RHB -0.39).",
        "rows": [
            row("Ketel Marte", "S", "+398", 90, "⭐ 🌕 💣", ["vs Detmers"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 98.0 mph EV. Detmers RHB split +0.09, HR risk -0.25. pitcher risk below avg (-0.25); park/weather net drag (-8%).""", blast="high"),
            row("LuJames Groover", "R", "+635", 76, "💎", ["vs Detmers"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 98.0 mph EV. Detmers RHB split +0.09, HR risk -0.25. pitcher risk below avg (-0.25); park/weather net drag (-8%).""", blast="good"),
            row("Corbin Carroll", "L", "+570", 64, "", ["vs Detmers"], """0 HR, 90.0 mph EV. Detmers LHB split -0.89, HR risk -0.25. tough split lane (-0.89); pitcher risk below avg (-0.25)."""),
            row("Mike Trout", "R", "+361", 84, "⭐ 🌕 💣", ["vs Kelly"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.6 mph EV. Kelly RHB split -0.39, HR risk 0.63. slight split headwind (-0.39); park/weather net drag (-8%).""", blast="high"),
            row("Donovan Walton", "L", "+950", 72, "", ["vs Kelly"], """1 HR, 2 near-HR, 83.9 mph EV. Kelly LHB split +1.10, HR risk 0.63. park/weather net drag (-8%); lighter EV form (83.9 mph).""", blast="good"),
            row("Logan O'Hoppe", "R", "+590", 70, "", ["vs Kelly"], """1 HR, 1 near-HR, 86.5 mph EV. Kelly RHB split -0.39, HR risk 0.63. slight split headwind (-0.39); park/weather net drag (-8%).""", blast="good"),
            row("Jose Siri", "R", "N/A", 70, "", ["vs Kelly"], """1 HR, 1 near-HR, 79.5 mph EV. Kelly RHB split -0.39, HR risk 0.63. slight split headwind (-0.39); park/weather net drag (-8%).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ PHI - Tyler Phillips (R, MIA) vs Jesus Luzardo (L, PHI)",
        "description": "Tail key data: Park boost +15% (stadium +16%, weather -1%). Phillips (HR risk -0.92, vs LHB -0.58, vs RHB -0.87). Luzardo (HR risk -0.63, vs LHB -1.10, vs RHB -0.24).",
        "rows": [
            row("Bryce Harper", "L", "+390", 81, "⭐", ["vs Phillips"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.8 mph EV. Phillips LHB split -0.58, HR risk -0.92. tough split lane (-0.58); pitcher suppresses HR (-0.92).""", blast="good"),
            row("Gabriel Rincones Jr.", "L", "+850", 80, "", ["vs Phillips"], """1 HR, 1 near-HR, 97.8 mph EV. Phillips LHB split -0.58, HR risk -0.92. tough split lane (-0.58); pitcher suppresses HR (-0.92).""", blast="good"),
            row("J.T. Realmuto", "R", "+790", 73, "", ["vs Phillips"], """1 HR, 1 near-HR, 90.6 mph EV. Phillips RHB split -0.87, HR risk -0.92. tough split lane (-0.87); pitcher suppresses HR (-0.92).""", blast="good"),
            row("Kyle Schwarber", "L", "+235", 74, "", ["vs Phillips"], """0 HR, 98.5 mph EV. Phillips LHB split -0.58, HR risk -0.92. tough split lane (-0.58); pitcher suppresses HR (-0.92).""", blast="good"),
            row("Heriberto Hernandez", "R", "+610", 70, "", ["vs Luzardo"], """1 HR, 1 near-HR, 86.3 mph EV. Luzardo RHB split -0.24, HR risk -0.63. slight split headwind (-0.24); pitcher suppresses HR (-0.63).""", blast="good"),
            row("Esteury Ruiz", "R", "+920", 82, "", ["vs Luzardo"], """1 HR, 2 near-HR, 97.8 mph EV. Luzardo RHB split -0.24, HR risk -0.63. slight split headwind (-0.24); pitcher suppresses HR (-0.63).""", blast="good"),
            row("Christopher Morel", "R", "N/A", 73, "", ["vs Luzardo"], """0 HR, 1 near-HR, 95.2 mph EV. Luzardo RHB split -0.24, HR risk -0.63. slight split headwind (-0.24); pitcher suppresses HR (-0.63).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ TEX - Zebby Matthews 🧤 (R, MIN) vs Kumar Rocker (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -10%, weather -1%). Matthews 🧤 (HR risk 1.23, vs LHB +0.93, vs RHB +1.18). Rocker (HR risk -0.55, vs LHB -0.04, vs RHB -1.00).",
        "rows": [
            row("Joc Pederson", "L", "+445", 80, "", ["vs Matthews"], """1 HR, 3 near-HR, 94.2 mph EV. Matthews LHB split +0.93, HR risk 1.23. park/weather net drag (-11%).""", blast="good"),
            row("Brandon Nimmo", "L", "+425", 73, "", ["vs Matthews"], """0 HR, 97.2 mph EV. Matthews LHB split +0.93, HR risk 1.23. park/weather net drag (-11%); limited recent HR events.""", blast="good"),
            row("Brooks Lee", "S", "+880", 87, "🌕 💣", ["vs Rocker"], """3 HR, 3 near-HR, 91.2 mph EV. Rocker RHB split -1.00, HR risk -0.55. tough split lane (-1.00); pitcher suppresses HR (-0.55).""", blast="high"),
            row("Byron Buxton", "R", "+285", 82, "🌕 💣", ["vs Rocker"], """2 HR, 2 near-HR, 92.1 mph EV. Rocker RHB split -1.00, HR risk -0.55. tough split lane (-1.00); pitcher suppresses HR (-0.55).""", blast="high"),
            row("Kody Clemens", "L", "+420", 76, "", ["vs Rocker"], """1 HR, 2 near-HR, 91.9 mph EV. Rocker LHB split -0.04, HR risk -0.55. slight split headwind (-0.04); pitcher suppresses HR (-0.55).""", blast="good"),
            row("Royce Lewis", "R", "+590", 64, "", ["vs Rocker"], """0 HR, 1 near-HR, 86.6 mph EV. Rocker RHB split -1.00, HR risk -0.55. tough split lane (-1.00); pitcher suppresses HR (-0.55)."""),
        ],
    },
    {
        "title": "NYM @ CIN - Kodai Senga (R, NYM) vs Brady Singer 🧤 (R, CIN)",
        "description": "Tail key data: Park boost +11% (stadium +12%, weather -2%). Senga (HR risk 0.82, vs LHB +0.93, vs RHB +0.50). Singer 🧤 (HR risk 1.53, vs LHB +1.44, vs RHB +0.80).",
        "rows": [
            row("Eugenio Suarez", "R", "+360", 94, "⭐ 🌕 💣", ["vs Senga"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 97.5 mph EV. Senga RHB split +0.50, HR risk 0.82.""", blast="high"),
            row("Matt McLain", "R", "+540", 77, "⭐", ["vs Senga"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 99.2 mph EV. Senga RHB split +0.50, HR risk 0.82. limited recent HR events.""", blast="good"),
            row("Sal Stewart", "R", "+376", 70, "", ["vs Senga"], """0 HR, 2 near-HR, 90.3 mph EV. Senga RHB split +0.50, HR risk 0.82.""", blast="good"),
            row("Bo Bichette", "R", "+590", 83, "🌕 💣", ["vs Singer"], """2 HR, 2 near-HR, 92.6 mph EV. Singer RHB split +0.80, HR risk 1.53.""", blast="high"),
            row("Francisco Alvarez", "R", "+445", 76, "", ["vs Singer"], """1 HR, 1 near-HR, 94.2 mph EV. Singer RHB split +0.80, HR risk 1.53.""", blast="good"),
            row("Juan Soto", "L", "+209", 73, "💎", ["vs Singer"], """Worst Pickz Hidden Gem. 0 HR, 96.8 mph EV. Singer LHB split +1.44, HR risk 1.53. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "PIT @ ATH - Mitch Keller (R, PIT) vs Jack Perkins (R, ATH)",
        "description": "Tail key data: Park boost +38% (stadium +32%, weather +6%). Keller (HR risk -0.40, vs LHB -0.19, vs RHB -0.48). Perkins (HR risk -0.06, vs LHB -1.36, vs RHB +0.91).",
        "rows": [
            row("Nick Kurtz", "L", "+240", 90, "🌕 💣 💎", ["vs Keller"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 93.7 mph EV. Keller LHB split -0.19, HR risk -0.40. slight split headwind (-0.19); pitcher suppresses HR (-0.40).""", blast="high"),
            row("Shea Langeliers", "R", "+270", 70, "", ["vs Keller"], """1 HR, 1 near-HR, 87.9 mph EV. Keller RHB split -0.48, HR risk -0.40. tough split lane (-0.48); pitcher suppresses HR (-0.40).""", blast="good"),
            row("Endy Rodriguez", "S", "+680", 78, "💎", ["vs Perkins"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.5 mph EV. Perkins RHB split +0.91, HR risk -0.06. pitcher risk below avg (-0.06).""", blast="good"),
            row("Henry Davis", "R", "N/A", 78, "🌕 💣", ["vs Perkins"], """2 HR, 2 near-HR, 87.1 mph EV. Perkins RHB split +0.91, HR risk -0.06. pitcher risk below avg (-0.06); lighter EV form (87.1 mph).""", blast="high"),
            row("Bryan Reynolds", "S", "+550", 79, "", ["vs Perkins"], """1 HR, 2 near-HR, 95.3 mph EV. Perkins RHB split +0.91, HR risk -0.06. pitcher risk below avg (-0.06).""", blast="good"),
            row("Brandon Lowe", "L", "+300", 73, "", ["vs Perkins"], """1 HR, 1 near-HR, 91.1 mph EV. Perkins LHB split -1.36, HR risk -0.06. tough split lane (-1.36); pitcher risk below avg (-0.06).""", blast="good"),
        ],
    },
    {
        "title": "SD @ STL - Michael King (R, SD) vs Andre Pallante (R, STL)",
        "description": "Tail key data: Park boost -2% (stadium -9%, weather +7%). King (HR risk 0.33, vs LHB +0.44, vs RHB +0.10). Pallante (HR risk -0.38, vs LHB -0.17, vs RHB -0.43).",
        "rows": [
            row("Alec Burleson", "L", "+490", 98, "⭐ 🌕 💣", ["vs King"], """Worst Pickz Favorite. 6 HR, 7 near-HR, 97.4 mph EV. King LHB split +0.44, HR risk 0.33. park suppresses carry (-9%).""", blast="high"),
            row("Lars Nootbaar", "L", "+600", 81, "", ["vs King"], """1 HR, 3 near-HR, 94.9 mph EV. King LHB split +0.44, HR risk 0.33. park suppresses carry (-9%).""", blast="good"),
            row("Jordan Walker", "R", "+540", 77, "", ["vs King"], """1 HR, 1 near-HR, 95.0 mph EV. King RHB split +0.10, HR risk 0.33. park suppresses carry (-9%).""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+575", 79, "", ["vs Pallante"], """1 HR, 1 near-HR, 96.8 mph EV. Pallante RHB split -0.43, HR risk -0.38. tough split lane (-0.43); pitcher risk below avg (-0.38).""", blast="good"),
            row("Jackson Merrill", "L", "+680", 71, "", ["vs Pallante"], """1 HR, 1 near-HR, 89.4 mph EV. Pallante LHB split -0.17, HR risk -0.38. slight split headwind (-0.17); pitcher risk below avg (-0.38).""", blast="good"),
            row("Gavin Sheets", "L", "+710", 71, "", ["vs Pallante"], """1 HR, 1 near-HR, 88.9 mph EV. Pallante LHB split -0.17, HR risk -0.38. slight split headwind (-0.17); pitcher risk below avg (-0.38).""", blast="good"),
        ],
    },
    {
        "title": "SF @ ATL - Adrian Houser (R, SF) vs Grant Holmes (R, ATL)",
        "description": "Tail key data: Park boost -3% (stadium -2%, weather +0%). Houser (HR risk 0.04, vs LHB +0.07, vs RHB +0.10). Holmes (HR risk 0.81, vs LHB +0.92, vs RHB +0.26).",
        "rows": [
            row("Matt Olson", "L", "+360", 74, "", ["vs Houser"], """1 HR, 1 near-HR, 92.4 mph EV. Houser LHB split +0.07, HR risk 0.04.""", blast="good"),
            row("Michael Harris II", "L", "+450", 72, "", ["vs Houser"], """1 HR, 1 near-HR, 90.3 mph EV. Houser LHB split +0.07, HR risk 0.04.""", blast="good"),
            row("Bryce Eldridge", "L", "+550", 88, "⭐ 🌕 💣", ["vs Holmes"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.5 mph EV. Holmes LHB split +0.92, HR risk 0.81.""", blast="high"),
            row("Matt Chapman", "R", "+640", 72, "", ["vs Holmes"], """1 HR, 2 near-HR, 88.3 mph EV. Holmes RHB split +0.26, HR risk 0.81.""", blast="good"),
        ],
    },
    {
        "title": "TB @ LAD - Drew Rasmussen (R, TB) vs Justin Wrobleski (L, LAD)",
        "description": "Tail key data: Park boost +12% (stadium +18%, weather -6%). Rasmussen (HR risk -0.89, vs LHB -0.41, vs RHB -1.05). Wrobleski (HR risk -0.09, vs LHB +0.40, vs RHB -0.18).",
        "rows": [
            row("Kyle Tucker", "L", "+587", 84, "🌕 💣", ["vs Rasmussen"], """2 HR, 3 near-HR, 91.5 mph EV. Rasmussen LHB split -0.41, HR risk -0.89. tough split lane (-0.41); pitcher suppresses HR (-0.89).""", blast="high"),
            row("Dalton Rushing", "L", "+450", 72, "", ["vs Rasmussen"], """1 HR, 1 near-HR, 90.5 mph EV. Rasmussen LHB split -0.41, HR risk -0.89. tough split lane (-0.41); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Andy Pages", "R", "+457", 74, "", ["vs Rasmussen"], """1 HR, 1 near-HR, 92.5 mph EV. Rasmussen RHB split -1.05, HR risk -0.89. tough split lane (-1.05); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Shohei Ohtani", "L", "+262", 80, "", ["vs Rasmussen"], """1 HR, 2 near-HR, 95.5 mph EV. Rasmussen LHB split -0.41, HR risk -0.89. tough split lane (-0.41); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Yandy Diaz", "R", "+396", 81, "🌕 💣", ["vs Wrobleski"], """2 HR, 3 near-HR, 89.2 mph EV. Wrobleski RHB split -0.18, HR risk -0.09. slight split headwind (-0.18); pitcher risk below avg (-0.09).""", blast="high"),
            row("Junior Caminero", "R", "+280", 73, "💎", ["vs Wrobleski"], """Worst Pickz Hidden Gem. 0 HR, 96.6 mph EV. Wrobleski RHB split -0.18, HR risk -0.09. slight split headwind (-0.18); pitcher risk below avg (-0.09).""", blast="good"),
            row("Ryan Vilade", "R", "+840", 62, "", ["vs Wrobleski"], """0 HR, 81.7 mph EV. Wrobleski RHB split -0.18, HR risk -0.09. slight split headwind (-0.18); pitcher risk below avg (-0.09)."""),
        ],
    },
    {
        "title": "TOR @ BOS - Dylan Cease (R, TOR) vs Payton Tolle (L, BOS)",
        "description": "Tail key data: Park boost +0% (stadium -7%, weather +7%). Cease (HR risk -0.27, vs LHB +0.08, vs RHB -0.70). Tolle (HR risk -0.85, vs LHB -0.46, vs RHB -0.79).",
        "rows": [
            row("Wilyer Abreu", "L", "+572", 83, "🌕 💣", ["vs Cease"], """2 HR, 2 near-HR, 92.9 mph EV. Cease LHB split +0.08, HR risk -0.27. pitcher risk below avg (-0.27); park suppresses carry (-7%).""", blast="high"),
            row("Willson Contreras", "R", "+550", 84, "🌕 💣", ["vs Cease"], """3 HR, 3 near-HR, 88.4 mph EV. Cease RHB split -0.70, HR risk -0.27. tough split lane (-0.70); pitcher risk below avg (-0.27).""", blast="high"),
            row("Yohendrick Pinango", "L", "+1120", 73, "", ["vs Tolle"], """0 HR, 1 near-HR, 95.1 mph EV. Tolle LHB split -0.46, HR risk -0.85. tough split lane (-0.46); pitcher suppresses HR (-0.85).""", blast="good"),
            row("Alejandro Kirk", "R", "+550", 62, "⭐", ["vs Tolle"], """Worst Pickz Favorite. 0 HR, 77.4 mph EV. Tolle RHB split -0.79, HR risk -0.85. tough split lane (-0.79); pitcher suppresses HR (-0.85)."""),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-16")

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

    out = ROOT / '_games-0616.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
