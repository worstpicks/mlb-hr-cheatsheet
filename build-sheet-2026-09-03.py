#!/usr/bin/env python3
"""Generate games[] block for 2026-09-03 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Andrew Benintendi (L)",
    "Bryan Reynolds (S)",
    "Cal Raleigh (S)",
    "Carter Jensen (L)",
    "Corey Seager (L)",
    "Freddie Freeman (L)",
    "Heriberto Hernandez (R)",
    "Jackson Chourio (R)",
    "Jake Burger (R)",
    "Mickey Gasper (S)",
    "Nathaniel Lowe (L)",
    "Pete Crow Armstrong (L)",
    "Rafael Devers (L)",
    "Teoscar Hernandez (R)",
    "Will Smith (R)",
    "Yandy Diaz (R)",
}

GEMS = {
    "Brandon Lowe (L)",
    "Brandon Nimmo (L)",
    "Dominic Canzone (L)",
    "Ezequiel Duran (R)",
    "Graham Pauley (L)",
    "Henry Bolte (R)",
    "Jake Bauers (L)",
    "Jarren Duran (L)",
    "Junior Caminero (R)",
    "Kyle Stowers (L)",
    "Luis Robert (R)",
    "Michael Busch (L)",
    "Nelson Velazquez (R)",
    "Nico Hoerner (R)",
    "Nolan Gorman (L)",
    "Oneil Cruz (L)",
    "Ramon Urias (R)",
    "Roman Anthony (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BOS",
    "Andres Gimenez (L)": "TOR",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Knizner (R)": "SF",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Brandon Valenzuela (S)": "TOR",
    "Brayan Rocchio (S)": "CLE",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Cal Raleigh (S)": "SEA",
    "Carter Jensen (L)": "KC",
    "Chase DeLauter (L)": "CLE",
    "Christian Walker (R)": "HOU",
    "Christian Yelich (L)": "MIL",
    "Coby Mayo (R)": "BAL",
    "Corey Seager (L)": "TEX",
    "Dalton Rushing (L)": "LAD",
    "Daulton Varsho (L)": "HOU",
    "Dominic Canzone (L)": "SEA",
    "Drew Gilbert (L)": "SF",
    "Elias Diaz (R)": "TEX",
    "Esmerlyn Valdez (R)": "PIT",
    "Ezequiel Duran (R)": "TEX",
    "Freddie Freeman (L)": "LAD",
    "Graham Pauley (L)": "MIA",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jarren Duran (L)": "BOS",
    "Jesus Sanchez (L)": "TOR",
    "Joey Ortiz (R)": "MIL",
    "Jonathan Aranda (L)": "TB",
    "Joshua Baez (R)": "STL",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kyle Stowers (L)": "MIA",
    "Lawrence Butler (L)": "ATH",
    "Luis Lara (S)": "MIL",
    "Luis Robert (R)": "BAL",
    "Michael Busch (L)": "CHC",
    "Mickey Gasper (S)": "BOS",
    "Munetaka Murakami (L)": "CWS",
    "Nathaniel Lowe (L)": "CLE",
    "Nelson Velazquez (R)": "HOU",
    "Nico Hoerner (R)": "CHC",
    "Nolan Gorman (L)": "STL",
    "Oneil Cruz (L)": "PIT",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Ramon Urias (R)": "STL",
    "Roman Anthony (L)": "BOS",
    "Teoscar Hernandez (R)": "LAD",
    "Tristan Peters (L)": "CWS",
    "Vinnie Pasquantino (L)": "KC",
    "Will Smith (R)": "LAD",
    "Yainer Diaz (R)": "HOU",
    "Yandy Diaz (R)": "TB",
}

BUM_MATCHUPS = {
    ("CWS @ HOU", "Castillo"),
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
        "title": "ATH @ SEA - Jack Perkins (R, ATH) vs Kade Anderson (L, SEA)",
        "description": "Tail key data: Park boost +4% (stadium +1%, weather +3%). Perkins (HR risk 0.68, vs LHB +0.59, vs RHB +0.02). Anderson (HR risk 0.81, vs LHB +0.00, vs RHB -0.08).",
        "rows": [
            row("Cal Raleigh", "S", "+340", 92, "⭐ 🌕 💣", ["vs Perkins"], """Worst Pickz Favorite. 4 HR, 4 near-HR, 94.8 mph EV. Perkins SHB→LHB split +0.59, HR risk 0.68.""", blast="high"),
            row("Dominic Canzone", "L", "+469", 88, "🌕 💣 💎", ["vs Perkins"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 90.8 mph EV. Perkins LHB split +0.59, HR risk 0.68.""", blast="high"),
            row("Henry Bolte", "R", "+750", 85, "🌕 💣 💎", ["vs Anderson"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.0 mph EV. Anderson RHB split -0.08, HR risk 0.81. slight split headwind (-0.08).""", blast="high"),
            row("Lawrence Butler", "L", "+820", 67, "", ["vs Anderson"], """0 HR, 93.1 mph EV. Anderson LHB split +0.00, HR risk 0.81. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "BOS @ BAL - Jake Bennett (L, BOS) vs Brandon Young (R, BAL)",
        "description": "Tail key data: Park boost +6% (stadium -4%, weather +10%). Bennett (HR risk -0.64, vs LHB -1.34, vs RHB +0.07). Young (HR risk 0.58, vs LHB -0.32, vs RHB +1.05).",
        "rows": [
            row("Luis Robert", "R", "+512", 58, "💎", ["vs Bennett"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.1 mph EV. Bennett RHB split +0.07, HR risk -0.64. pitcher suppresses HR (-0.64).""", blast="good"),
            row("Coby Mayo", "R", "+327", 58, "", ["vs Bennett"], """1 HR, 1 near-HR, 90.5 mph EV. Bennett RHB split +0.07, HR risk -0.64. pitcher suppresses HR (-0.64).""", blast="good"),
            row("Pete Alonso", "R", "+311", 58, "", ["vs Bennett"], """1 HR, 1 near-HR, 92.4 mph EV. Bennett RHB split +0.07, HR risk -0.64. pitcher suppresses HR (-0.64).""", blast="good"),
            row("Mickey Gasper", "S", "+505", 83, "⭐ 🌕 💣", ["vs Young"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 86.6 mph EV. Young SHB→RHB split +1.05, HR risk 0.58. lighter EV form (86.6 mph).""", blast="high"),
            row("Adley Rutschman", "S", "+560", 73, "", ["vs Young"], """1 HR, 1 near-HR, 86.7 mph EV. Young SHB→RHB split +1.05, HR risk 0.58. lighter EV form (86.7 mph).""", blast="good"),
            row("Roman Anthony", "L", "+446", 68, "💎", ["vs Young"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 98.1 mph EV. Young LHB split -0.32, HR risk 0.58. slight split headwind (-0.32); limited recent HR events.""", blast="good"),
            row("Jarren Duran", "L", "+534", 66, "💎", ["vs Young"], """Worst Pickz Hidden Gem. 0 HR, 96.3 mph EV. Young LHB split -0.32, HR risk 0.58. slight split headwind (-0.32); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ HOU - Luis Castillo 🧤 (R, CWS) vs Hunter Brown (R, HOU)",
        "description": "Tail key data: Park boost +6% (stadium +7%, weather +0%). Castillo 🧤 (HR risk 1.49, vs LHB +0.50, vs RHB +1.24). Brown (HR risk -0.23, vs LHB +0.24, vs RHB -0.94).",
        "rows": [
            row("Nelson Velazquez", "R", "N/A", 90, "🚀 🌕 💣 💎", ["vs Castillo"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 101.5 mph EV. Castillo RHB split +1.24, HR risk 1.49. limited recent HR events.""", blast="good"),
            row("Daulton Varsho", "L", "+490", 82, "", ["vs Castillo"], """0 HR, 97.2 mph EV. Castillo LHB split +0.50, HR risk 1.49. limited recent HR events.""", blast="good"),
            row("Yainer Diaz", "R", "+910", 90, "🌕 💣", ["vs Castillo"], """1 HR, 1 near-HR, 93.3 mph EV. Castillo RHB split +1.24, HR risk 1.49.""", blast="good"),
            row("Christian Walker", "R", "+490", 89, "🌕 💣", ["vs Castillo"], """0 HR, 1 near-HR, 95.1 mph EV. Castillo RHB split +1.24, HR risk 1.49. limited recent HR events.""", blast="good"),
            row("Tristan Peters", "L", "+1040", 58, "", ["vs Brown"], """0 HR, 1 near-HR, 91.9 mph EV. Brown LHB split +0.24, HR risk -0.23. pitcher risk below avg (-0.23); limited recent HR events."""),
            row("Munetaka Murakami", "L", "+440", 62, "", ["vs Brown"], """0 HR, 1 near-HR, 95.9 mph EV. Brown LHB split +0.24, HR risk -0.23. pitcher risk below avg (-0.23); limited recent HR events.""", blast="good"),
            row("Andrew Benintendi", "L", "+820", 58, "⭐", ["vs Brown"], """Worst Pickz Favorite. 0 HR, 89.7 mph EV. Brown LHB split +0.24, HR risk -0.23. pitcher risk below avg (-0.23); limited recent HR events."""),
        ],
    },
    {
        "title": "MIA @ KC - Sandy Alcantara (R, MIA) vs Michael Wacha (R, KC)",
        "description": "Tail key data: Park boost +19% (stadium +12%, weather +7%). Alcantara (HR risk -1.11, vs LHB -0.54, vs RHB -1.01). Wacha (HR risk 0.18, vs LHB -0.74, vs RHB +1.84).",
        "rows": [
            row("Carter Jensen", "L", "+384", 72, "🚀 ⭐ 🌕 💣", ["vs Alcantara"], """Worst Pickz Favorite. 3 HR, 6 near-HR, 100.2 mph EV. Alcantara LHB split -0.54, HR risk -1.11. tough split lane (-0.54); pitcher suppresses HR (-1.11).""", blast="high"),
            row("Jac Caglianone", "L", "+365", 58, "", ["vs Alcantara"], """0 HR, 93.9 mph EV. Alcantara LHB split -0.54, HR risk -1.11. tough split lane (-0.54); pitcher suppresses HR (-1.11).""", blast="good"),
            row("Vinnie Pasquantino", "L", "+511", 58, "", ["vs Alcantara"], """0 HR, 90.9 mph EV. Alcantara LHB split -0.54, HR risk -1.11. tough split lane (-0.54); pitcher suppresses HR (-1.11)."""),
            row("Heriberto Hernandez", "R", "+333", 91, "⭐ 🌕 💣", ["vs Wacha"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.9 mph EV. Wacha RHB split +1.84, HR risk 0.18.""", blast="high"),
            row("Graham Pauley", "L", "+790", 63, "💎", ["vs Wacha"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 91.5 mph EV. Wacha LHB split -0.74, HR risk 0.18. tough split lane (-0.74).""", blast="good"),
            row("Kyle Stowers", "L", "+312", 60, "🚀 💎", ["vs Wacha"], """Worst Pickz Hidden Gem. 0 HR, 100.8 mph EV. Wacha LHB split -0.74, HR risk 0.18. tough split lane (-0.74); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIL @ CHC - Logan Henderson (R, MIL) vs Kevin Gausman (R, CHC)",
        "description": "Tail key data: Park boost +3% (stadium -2%, weather +5%). Henderson (HR risk 0.62, vs LHB +0.45, vs RHB -0.01). Gausman (HR risk 0.11, vs LHB -0.18, vs RHB +0.30).",
        "rows": [
            row("Pete Crow Armstrong", "L", "+280", 84, "⭐ 🌕 💣", ["vs Henderson"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.8 mph EV. Henderson LHB split +0.45, HR risk 0.62.""", blast="high"),
            row("Michael Busch", "L", "+430", 75, "💎", ["vs Henderson"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.1 mph EV. Henderson LHB split +0.45, HR risk 0.62.""", blast="good"),
            row("Nico Hoerner", "R", "+1220", 61, "💎", ["vs Henderson"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 91.4 mph EV. Henderson RHB split -0.01, HR risk 0.62. slight split headwind (-0.01); limited recent HR events."""),
            row("Jackson Chourio", "R", "+394", 66, "⭐", ["vs Gausman"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.1 mph EV. Gausman RHB split +0.30, HR risk 0.11.""", blast="good"),
            row("Joey Ortiz", "R", "+625", 68, "", ["vs Gausman"], """1 HR, 1 near-HR, 94.9 mph EV. Gausman RHB split +0.30, HR risk 0.11.""", blast="good"),
            row("Jake Bauers", "L", "+420", 59, "💎", ["vs Gausman"], """Worst Pickz Hidden Gem. 0 HR, 98.9 mph EV. Gausman LHB split -0.18, HR risk 0.11. slight split headwind (-0.18); limited recent HR events.""", blast="good"),
            row("Luis Lara", "S", "N/A", 62, "", ["vs Gausman"], """0 HR, 1 near-HR, 93.1 mph EV. Gausman SHB→RHB split +0.30, HR risk 0.11. limited recent HR events.""", blast="good"),
            row("Christian Yelich", "L", "+800", 64, "", ["vs Gausman"], """1 HR, 1 near-HR, 95.3 mph EV. Gausman LHB split -0.18, HR risk 0.11. slight split headwind (-0.18).""", blast="good"),
        ],
    },
    {
        "title": "SF @ PIT - Blade Tidwell (R, SF) vs Lake Bachar (R, PIT)",
        "description": "Tail key data: Park boost +1% (stadium -14%, weather +15%). Tidwell (HR risk 0.52, vs LHB +0.68, vs RHB -0.49). Bachar (HR risk -0.20, vs LHB -0.42, vs RHB +0.64).",
        "rows": [
            row("Bryan Reynolds", "S", "+550", 75, "🚀 ⭐", ["vs Tidwell"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 101.2 mph EV. Tidwell SHB→LHB split +0.68, HR risk 0.52. park suppresses carry (-14%).""", blast="good"),
            row("Oneil Cruz", "L", "+340", 74, "💎", ["vs Tidwell"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.9 mph EV. Tidwell LHB split +0.68, HR risk 0.52. park suppresses carry (-14%).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+470", 58, "", ["vs Tidwell"], """0 HR, 84.5 mph EV. Tidwell RHB split -0.49, HR risk 0.52. tough split lane (-0.49); park suppresses carry (-14%)."""),
            row("Brandon Lowe", "L", "+331", 64, "💎", ["vs Tidwell"], """Worst Pickz Hidden Gem. 0 HR, 91.5 mph EV. Tidwell LHB split +0.68, HR risk 0.52. park suppresses carry (-14%); limited recent HR events."""),
            row("Rafael Devers", "L", "+337", 77, "🚀 ⭐ 🌕 💣", ["vs Bachar"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 100.8 mph EV. Bachar LHB split -0.42, HR risk -0.20. tough split lane (-0.42); pitcher risk below avg (-0.20).""", blast="high"),
            row("Drew Gilbert", "L", "+870", 61, "", ["vs Bachar"], """1 HR, 2 near-HR, 96.5 mph EV. Bachar LHB split -0.42, HR risk -0.20. tough split lane (-0.42); pitcher risk below avg (-0.20).""", blast="good"),
            row("Andrew Knizner", "R", "+850", 58, "", ["vs Bachar"], """0 HR, 1 near-HR, 91.6 mph EV. Bachar RHB split +0.64, HR risk -0.20. pitcher risk below avg (-0.20); park suppresses carry (-14%)."""),
            row("Bryce Eldridge", "L", "+435", 58, "", ["vs Bachar"], """0 HR, 92.4 mph EV. Bachar LHB split -0.42, HR risk -0.20. tough split lane (-0.42); pitcher risk below avg (-0.20).""", blast="good"),
        ],
    },
    {
        "title": "STL @ LAD - Quinn Mathews (L, STL) vs Tarik Skubal (L, LAD)",
        "description": "Tail key data: Park boost +20% (stadium +19%, weather +1%). Mathews (HR risk -1.78, vs LHB -1.48, vs RHB -1.04). Skubal (HR risk -0.60, vs LHB -0.11, vs RHB -0.42).",
        "rows": [
            row("Teoscar Hernandez", "R", "+429", 58, "⭐", ["vs Mathews"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.4 mph EV. Mathews RHB split -1.04, HR risk -1.78. tough split lane (-1.04); pitcher suppresses HR (-1.78).""", blast="good"),
            row("Dalton Rushing", "L", "N/A", 58, "", ["vs Mathews"], """0 HR, 94.1 mph EV. Mathews LHB split -1.48, HR risk -1.78. tough split lane (-1.48); pitcher suppresses HR (-1.78).""", blast="good"),
            row("Freddie Freeman", "L", "+577", 58, "⭐", ["vs Mathews"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.9 mph EV. Mathews LHB split -1.48, HR risk -1.78. tough split lane (-1.48); pitcher suppresses HR (-1.78).""", blast="good"),
            row("Will Smith", "R", "+500", 58, "⭐", ["vs Mathews"], """Worst Pickz Favorite. 0 HR, 95.1 mph EV. Mathews RHB split -1.04, HR risk -1.78. tough split lane (-1.04); pitcher suppresses HR (-1.78).""", blast="good"),
            row("Ramon Urias", "R", "+790", 70, "🌕 💣 💎", ["vs Skubal"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.8 mph EV. Skubal RHB split -0.42, HR risk -0.60. tough split lane (-0.42); pitcher suppresses HR (-0.60).""", blast="high"),
            row("Joshua Baez", "R", "+560", 66, "🌕 💣", ["vs Skubal"], """2 HR, 2 near-HR, 91.5 mph EV. Skubal RHB split -0.42, HR risk -0.60. tough split lane (-0.42); pitcher suppresses HR (-0.60).""", blast="high"),
            row("Nolan Gorman", "L", "+525", 67, "💎", ["vs Skubal"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 94.1 mph EV. Skubal LHB split -0.11, HR risk -0.60. slight split headwind (-0.11); pitcher suppresses HR (-0.60).""", blast="good"),
        ],
    },
    {
        "title": "TB @ TEX - Shane McClanahan (L, TB) vs Cal Quantrill (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -11%, weather +0%). McClanahan (HR risk -0.30, vs LHB +0.14, vs RHB -0.33). Quantrill (HR risk -0.20, vs LHB -0.39, vs RHB +0.17).",
        "rows": [
            row("Brandon Nimmo", "L", "+535", 58, "💎", ["vs McClanahan"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.7 mph EV. McClanahan LHB split +0.14, HR risk -0.30. pitcher risk below avg (-0.30); park/weather net drag (-11%).""", blast="good"),
            row("Corey Seager", "L", "+350", 58, "⭐", ["vs McClanahan"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 92.0 mph EV. McClanahan LHB split +0.14, HR risk -0.30. pitcher risk below avg (-0.30); park/weather net drag (-11%).""", blast="good"),
            row("Elias Diaz", "R", "+760", 58, "", ["vs McClanahan"], """0 HR, 96.9 mph EV. McClanahan RHB split -0.33, HR risk -0.30. slight split headwind (-0.33); pitcher risk below avg (-0.30).""", blast="good"),
            row("Jake Burger", "R", "+411", 58, "⭐", ["vs McClanahan"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.1 mph EV. McClanahan RHB split -0.33, HR risk -0.30. slight split headwind (-0.33); pitcher risk below avg (-0.30).""", blast="good"),
            row("Ezequiel Duran", "R", "+810", 58, "💎", ["vs McClanahan"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.2 mph EV. McClanahan RHB split -0.33, HR risk -0.30. slight split headwind (-0.33); pitcher risk below avg (-0.30).""", blast="good"),
            row("Justin Foscue", "R", "+800", 58, "", ["vs McClanahan"], """1 HR, 1 near-HR, 89.3 mph EV. McClanahan RHB split -0.33, HR risk -0.30. slight split headwind (-0.33); pitcher risk below avg (-0.30).""", blast="good"),
            row("Yandy Diaz", "R", "+558", 61, "⭐", ["vs Quantrill"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.2 mph EV. Quantrill RHB split +0.17, HR risk -0.20. pitcher risk below avg (-0.20); park/weather net drag (-11%).""", blast="good"),
            row("Junior Caminero", "R", "+322", 58, "💎", ["vs Quantrill"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.3 mph EV. Quantrill RHB split +0.17, HR risk -0.20. pitcher risk below avg (-0.20); park/weather net drag (-11%).""", blast="good"),
            row("Jonathan Aranda", "L", "+480", 58, "", ["vs Quantrill"], """0 HR, 93.6 mph EV. Quantrill LHB split -0.39, HR risk -0.20. slight split headwind (-0.39); pitcher risk below avg (-0.20).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ CLE - Jose Soriano (R, TOR) vs Tanner Bibee (R, CLE)",
        "description": "Tail key data: Park boost +17% (stadium -4%, weather +21%). Soriano (HR risk -0.48, vs LHB -0.35, vs RHB -0.27). Bibee (HR risk 0.56, vs LHB +0.72, vs RHB -0.75).",
        "rows": [
            row("Nathaniel Lowe", "L", "+880", 62, "⭐", ["vs Soriano"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.3 mph EV. Soriano LHB split -0.35, HR risk -0.48. slight split headwind (-0.35); pitcher suppresses HR (-0.48).""", blast="good"),
            row("Chase DeLauter", "L", "+830", 58, "", ["vs Soriano"], """0 HR, 1 near-HR, 96.0 mph EV. Soriano LHB split -0.35, HR risk -0.48. slight split headwind (-0.35); pitcher suppresses HR (-0.48).""", blast="good"),
            row("Brayan Rocchio", "S", "+1200", 58, "", ["vs Soriano"], """0 HR, 98.7 mph EV. Soriano SHB→RHB split -0.27, HR risk -0.48. slight split headwind (-0.27); pitcher suppresses HR (-0.48).""", blast="good"),
            row("Brandon Valenzuela", "S", "+760", 70, "", ["vs Bibee"], """0 HR, 1 near-HR, 91.9 mph EV. Bibee SHB→LHB split +0.72, HR risk 0.56. limited recent HR events."""),
            row("Jesus Sanchez", "L", "+640", 67, "", ["vs Bibee"], """0 HR, 89.7 mph EV. Bibee LHB split +0.72, HR risk 0.56. limited recent HR events."""),
            row("Andres Gimenez", "L", "+980", 78, "", ["vs Bibee"], """0 HR, 2 near-HR, 93.6 mph EV. Bibee LHB split +0.72, HR risk 0.56.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-03")

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

    out = ROOT / '_games-0903.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
