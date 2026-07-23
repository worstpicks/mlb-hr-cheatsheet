#!/usr/bin/env python3
"""Generate games[] block for 2026-07-21 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Ben Rice (L)",
    "Byron Buxton (R)",
    "Carter Jensen (L)",
    "Coby Mayo (R)",
    "Heriberto Hernandez (R)",
    "Hunter Feduccia (L)",
    "Hunter Goodman (R)",
    "Jake Rogers (R)",
    "Jazz Chisholm Jr. (L)",
    "Jo Adell (R)",
    "Joc Pederson (L)",
    "Kyle Schwarber (L)",
    "Kyle Stowers (L)",
    "Kyle Teel (L)",
    "Luis Garcia Jr. (L)",
    "Manny Machado (R)",
    "Matt Olson (L)",
    "Pete Alonso (R)",
    "Seiya Suzuki (R)",
    "Tyler O'Neill (R)",
    "Willson Contreras (R)",
    "Willy Adames (R)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Dominic Canzone (L)",
    "Drake Baldwin (L)",
    "George Springer (R)",
    "Joe Mack (L)",
    "Taylor Trammell (L)",
    "Tristan Peters (L)",
    "Tyler Stephenson (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Andres Gimenez (L)": "TOR",
    "Ben Rice (L)": "NYY",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Carter Jensen (L)": "KC",
    "Chase DeLauter (L)": "CLE",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Coby Mayo (R)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "David Fry (R)": "CLE",
    "Daylen Lile (L)": "WSH",
    "Derek Hill (R)": "PHI",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Gary Sanchez (R)": "MIL",
    "George Springer (R)": "TOR",
    "Gleyber Torres (R)": "DET",
    "Griffin Conine (L)": "MIA",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "TB",
    "Hunter Goodman (R)": "COL",
    "Jac Caglianone (L)": "KC",
    "Jacob Wilson (R)": "ATH",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jake Rogers (R)": "DET",
    "James Outman (L)": "DET",
    "James Wood (L)": "WSH",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "Joey Ortiz (R)": "MIL",
    "Jonathan Aranda (L)": "TB",
    "Josh Jung (R)": "TEX",
    "Joshua Kuroda-Grauer (R)": "ATH",
    "Junior Caminero (R)": "TB",
    "Kody Clemens (L)": "MIN",
    "Kyle Higashioka (R)": "TEX",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Kyle Teel (L)": "CWS",
    "Lane Thomas (R)": "KC",
    "Luis Campusano (R)": "SD",
    "Luis Garcia Jr. (L)": "WSH",
    "Luis Robert (R)": "NYM",
    "Luke Raley (L)": "SEA",
    "Manny Machado (R)": "SD",
    "Marcell Ozuna (R)": "PIT",
    "Matt Olson (L)": "ATL",
    "Mitch Garver (R)": "SEA",
    "Munetaka Murakami (L)": "CWS",
    "Nolan Arenado (R)": "ARI",
    "Pete Alonso (R)": "BAL",
    "Randy Arozarena (R)": "SEA",
    "Royce Lewis (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Ryan O'Hearn (L)": "PIT",
    "Ryan Vilade (R)": "TB",
    "Salvador Perez (R)": "KC",
    "Samuel Basallo (L)": "BAL",
    "Seiya Suzuki (R)": "CHC",
    "Shea Langeliers (R)": "ATH",
    "Taylor Trammell (L)": "HOU",
    "Tommy Edman (S)": "LAD",
    "Trent Grisham (L)": "NYY",
    "Tristan Peters (L)": "CWS",
    "Ty France (R)": "SD",
    "Tyler O'Neill (R)": "BAL",
    "Tyler Stephenson (R)": "CIN",
    "Victor Caratini (S)": "MIN",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("ATH @ ARI", "Perkins"),
    ("CWS @ TEX", "Schultz"),
    ("MIA @ HOU", "Imai"),
    ("PIT @ NYY", "Warren"),
    ("SD @ ATL", "Buehler"),
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
        "title": "ATH @ ARI - Jack Perkins 🧤 (R, ATH) vs Kohl Drake (L, ARI)",
        "description": "Tail key data: Park boost -9% (stadium -9%, weather -1%). Perkins 🧤 (HR risk 1.15, vs LHB +0.65, vs RHB +0.75). Drake (HR risk 0.00, vs LHB +0.00, vs RHB +0.00).",
        "rows": [
            row("Nolan Arenado", "R", "+650", 76, "", ["vs Perkins"], """1 HR, 1 near-HR, 88.0 mph EV. Perkins RHB split +0.75, HR risk 1.15. park/weather net drag (-9%).""", blast="good"),
            row("Corbin Carroll", "L", "+470", 78, "", ["vs Perkins"], """1 HR, 2 near-HR, 90.2 mph EV. Perkins LHB split +0.65, HR risk 1.15. park/weather net drag (-9%).""", blast="good"),
            row("Shea Langeliers", "R", "+360", 68, "", ["vs Drake"], """1 HR, 3 near-HR, 98.1 mph EV. Drake RHB split +0.00, HR risk 0.00. park/weather net drag (-9%).""", blast="good"),
            row("Joshua Kuroda-Grauer", "R", "N/A", 61, "", ["vs Drake"], """1 HR, 1 near-HR, 94.7 mph EV. Drake RHB split +0.00, HR risk 0.00. park/weather net drag (-9%).""", blast="good"),
            row("Henry Bolte", "R", "+900", 60, "", ["vs Drake"], """1 HR, 1 near-HR, 94.2 mph EV. Drake RHB split +0.00, HR risk 0.00. park/weather net drag (-9%).""", blast="good"),
            row("Jacob Wilson", "R", "+1200", 58, "", ["vs Drake"], """1 HR, 1 near-HR, 86.4 mph EV. Drake RHB split +0.00, HR risk 0.00. park/weather net drag (-9%); lighter EV form (86.4 mph).""", blast="good"),
        ],
    },
    {
        "title": "BAL @ BOS - Kyle Bradish (R, BAL) vs Eduardo Rivera (L, BOS)",
        "description": "Tail key data: Park boost +10% (stadium -6%, weather +16%). Bradish (HR risk -0.94, vs LHB -0.77, vs RHB -0.39). Rivera (HR risk -0.46, vs LHB -1.77, vs RHB +0.79).",
        "rows": [
            row("Willson Contreras", "R", "+440", 58, "⭐", ["vs Bradish"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.6 mph EV. Bradish RHB split -0.39, HR risk -0.94. slight split headwind (-0.39); pitcher suppresses HR (-0.94).""", blast="good"),
            row("Wilyer Abreu", "L", "+444", 58, "", ["vs Bradish"], """1 HR, 1 near-HR, 95.4 mph EV. Bradish LHB split -0.77, HR risk -0.94. tough split lane (-0.77); pitcher suppresses HR (-0.94).""", blast="good"),
            row("Tyler O'Neill", "R", "+525", 78, "⭐ 🌕 💣", ["vs Rivera"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.2 mph EV. Rivera RHB split +0.79, HR risk -0.46. pitcher suppresses HR (-0.46); park suppresses carry (-6%).""", blast="high"),
            row("Pete Alonso", "R", "+360", 69, "⭐", ["vs Rivera"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.6 mph EV. Rivera RHB split +0.79, HR risk -0.46. pitcher suppresses HR (-0.46); park suppresses carry (-6%).""", blast="good"),
            row("Coby Mayo", "R", "+500", 87, "⭐ 🌕 💣", ["vs Rivera"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 98.9 mph EV. Rivera RHB split +0.79, HR risk -0.46. pitcher suppresses HR (-0.46); park suppresses carry (-6%).""", blast="high"),
            row("Christian Encarnacion-Strand", "R", "+600", 69, "🚀", ["vs Rivera"], """1 HR, 1 near-HR, 103.2 mph EV. Rivera RHB split +0.79, HR risk -0.46. pitcher suppresses HR (-0.46); park suppresses carry (-6%).""", blast="good"),
            row("Samuel Basallo", "L", "N/A", 58, "", ["vs Rivera"], """1 HR, 1 near-HR, 91.0 mph EV. Rivera LHB split -1.77, HR risk -0.46. tough split lane (-1.77); pitcher suppresses HR (-0.46).""", blast="good"),
        ],
    },
    {
        "title": "CIN @ SEA - Chase Burns (R, CIN) vs Luis Castillo (R, SEA)",
        "description": "Tail key data: Park boost -2% (stadium +1%, weather -3%). Burns (HR risk 0.03, vs LHB +0.45, vs RHB -0.71). Castillo (HR risk 0.20, vs LHB +0.59, vs RHB -0.79).",
        "rows": [
            row("Dominic Canzone", "L", "+404", 63, "💎", ["vs Burns"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 89.9 mph EV. Burns LHB split +0.45, HR risk 0.03.""", blast="good"),
            row("Mitch Garver", "R", "N/A", 58, "", ["vs Burns"], """1 HR, 1 near-HR, 92.8 mph EV. Burns RHB split -0.71, HR risk 0.03. tough split lane (-0.71).""", blast="good"),
            row("Randy Arozarena", "R", "+470", 70, "🌕 💣", ["vs Burns"], """2 HR, 3 near-HR, 93.2 mph EV. Burns RHB split -0.71, HR risk 0.03. tough split lane (-0.71).""", blast="high"),
            row("Luke Raley", "L", "+457", 58, "", ["vs Burns"], """0 HR, 88.2 mph EV. Burns LHB split +0.45, HR risk 0.03. limited recent HR events."""),
            row("Tyler Stephenson", "R", "+525", 73, "🌕 💣 💎", ["vs Castillo"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 94.5 mph EV. Castillo RHB split -0.79, HR risk 0.20. tough split lane (-0.79).""", blast="high"),
            row("Eugenio Suarez", "R", "+430", 60, "", ["vs Castillo"], """1 HR, 2 near-HR, 93.6 mph EV. Castillo RHB split -0.79, HR risk 0.20. tough split lane (-0.79).""", blast="good"),
            row("Elly De La Cruz", "S", "+390", 72, "", ["vs Castillo"], """1 HR, 2 near-HR, 97.3 mph EV. Castillo SHB→LHB split +0.59, HR risk 0.20.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ TEX - Noah Schultz 🧤 (L, CWS) vs Kumar Rocker (R, TEX)",
        "description": "Tail key data: Park boost -12% (stadium -11%, weather -1%). Schultz 🧤 (HR risk 1.51, vs LHB -1.00, vs RHB +1.54). Rocker (HR risk 0.69, vs LHB +1.39, vs RHB -0.54).",
        "rows": [
            row("Wyatt Langford", "R", "+430", 87, "", ["vs Schultz"], """1 HR, 1 near-HR, 91.0 mph EV. Schultz RHB split +1.54, HR risk 1.51. park/weather net drag (-12%).""", blast="good"),
            row("Joc Pederson", "L", "N/A", 70, "⭐", ["vs Schultz"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.7 mph EV. Schultz LHB split -1.00, HR risk 1.51. tough split lane (-1.00); park/weather net drag (-12%).""", blast="good"),
            row("Kyle Higashioka", "R", "+600", 91, "🌕 💣", ["vs Schultz"], """1 HR, 1 near-HR, 96.0 mph EV. Schultz RHB split +1.54, HR risk 1.51. park/weather net drag (-12%).""", blast="good"),
            row("Jake Burger", "R", "+422", 91, "🌕 💣", ["vs Schultz"], """1 HR, 1 near-HR, 98.0 mph EV. Schultz RHB split +1.54, HR risk 1.51. park/weather net drag (-12%).""", blast="good"),
            row("Josh Jung", "R", "+650", 86, "", ["vs Schultz"], """0 HR, 99.9 mph EV. Schultz RHB split +1.54, HR risk 1.51. park/weather net drag (-12%); limited recent HR events.""", blast="good"),
            row("Kyle Teel", "L", "N/A", 76, "⭐", ["vs Rocker"], """Worst Pickz Favorite. 0 HR, 96.0 mph EV. Rocker LHB split +1.39, HR risk 0.69. park/weather net drag (-12%); limited recent HR events.""", blast="good"),
            row("Tristan Peters", "L", "+900", 76, "💎", ["vs Rocker"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.0 mph EV. Rocker LHB split +1.39, HR risk 0.69. park/weather net drag (-12%); limited recent HR events.""", blast="good"),
            row("Munetaka Murakami", "L", "+320", 66, "", ["vs Rocker"], """0 HR, 89.7 mph EV. Rocker LHB split +1.39, HR risk 0.69. park/weather net drag (-12%); limited recent HR events."""),
        ],
    },
    {
        "title": "DET @ CHC - Framber Valdez (L, DET) vs David Peterson (L, CHC)",
        "description": "Tail key data: Park boost -12% (stadium +0%, weather -12%). Valdez (HR risk -0.78, vs LHB -0.63, vs RHB -0.37). Peterson (HR risk 0.13, vs LHB +0.67, vs RHB -0.35).",
        "rows": [
            row("Seiya Suzuki", "R", "+600", 58, "⭐", ["vs Valdez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.7 mph EV. Valdez RHB split -0.37, HR risk -0.78. slight split headwind (-0.37); pitcher suppresses HR (-0.78).""", blast="good"),
            row("Gleyber Torres", "R", "+700", 58, "", ["vs Peterson"], """1 HR, 2 near-HR, 92.8 mph EV. Peterson RHB split -0.35, HR risk 0.13. slight split headwind (-0.35); park/weather net drag (-12%).""", blast="good"),
            row("Jake Rogers", "R", "+460", 61, "⭐", ["vs Peterson"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.3 mph EV. Peterson RHB split -0.35, HR risk 0.13. slight split headwind (-0.35); park/weather net drag (-12%).""", blast="good"),
            row("James Outman", "L", "+1050", 64, "", ["vs Peterson"], """0 HR, 1 near-HR, 97.5 mph EV. Peterson LHB split +0.67, HR risk 0.13. park/weather net drag (-12%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "LAD @ PHI - Justin Wrobleski (L, LAD) vs Zack Wheeler (R, PHI)",
        "description": "Tail key data: Park boost +44% (stadium +13%, weather +31%). Wrobleski (HR risk -0.01, vs LHB +0.32, vs RHB +0.07). Wheeler (HR risk -0.63, vs LHB -0.52, vs RHB -0.32).",
        "rows": [
            row("Kyle Schwarber", "L", "+213", 76, "⭐", ["vs Wrobleski"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.7 mph EV. Wrobleski LHB split +0.32, HR risk -0.01. pitcher risk below avg (-0.01).""", blast="good"),
            row("Derek Hill", "R", "+560", 70, "", ["vs Wrobleski"], """1 HR, 1 near-HR, 91.4 mph EV. Wrobleski RHB split +0.07, HR risk -0.01. pitcher risk below avg (-0.01).""", blast="good"),
            row("Tommy Edman", "S", "+770", 64, "", ["vs Wheeler"], """1 HR, 1 near-HR, 94.2 mph EV. Wheeler SHB→RHB split -0.32, HR risk -0.63. slight split headwind (-0.32); pitcher suppresses HR (-0.63).""", blast="good"),
            row("Dalton Rushing", "L", "+422", 59, "", ["vs Wheeler"], """1 HR, 1 near-HR, 90.7 mph EV. Wheeler LHB split -0.52, HR risk -0.63. tough split lane (-0.52); pitcher suppresses HR (-0.63).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ HOU - Tyler Phillips (R, MIA) vs Tatsuya Imai 🧤 (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +6%, weather -1%). Phillips (HR risk 0.08, vs LHB +0.25, vs RHB -0.13). Imai 🧤 (HR risk 1.47, vs LHB +1.12, vs RHB +0.25).",
        "rows": [
            row("Yordan Alvarez", "L", "+250", 68, "⭐", ["vs Phillips"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.7 mph EV. Phillips LHB split +0.25, HR risk 0.08.""", blast="good"),
            row("Taylor Trammell", "L", "N/A", 68, "💎", ["vs Phillips"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 94.0 mph EV. Phillips LHB split +0.25, HR risk 0.08.""", blast="good"),
            row("Joe Mack", "L", "+710", 91, "🌕 💣 💎", ["vs Imai"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.5 mph EV. Imai LHB split +1.12, HR risk 1.47.""", blast="good"),
            row("Kyle Stowers", "L", "+310", 87, "🚀 ⭐", ["vs Imai"], """Worst Pickz Favorite. 0 HR, 102.2 mph EV. Imai LHB split +1.12, HR risk 1.47. limited recent HR events.""", blast="good"),
            row("Heriberto Hernandez", "R", "+431", 80, "⭐", ["vs Imai"], """Worst Pickz Favorite. 0 HR, 98.4 mph EV. Imai RHB split +0.25, HR risk 1.47. limited recent HR events.""", blast="good"),
            row("Griffin Conine", "L", "+400", 91, "🚀 🌕 💣", ["vs Imai"], """1 HR, 1 near-HR, 100.9 mph EV. Imai LHB split +1.12, HR risk 1.47.""", blast="good"),
        ],
    },
    {
        "title": "MIN @ CLE - Kendry Rojas (L, MIN) vs Parker Messick (L, CLE)",
        "description": "Tail key data: Park boost +12% (stadium -6%, weather +18%). Rojas (HR risk -1.04, vs LHB +0.33, vs RHB -1.28). Messick (HR risk -1.04, vs LHB -1.18, vs RHB -0.45).",
        "rows": [
            row("David Fry", "R", "+680", 58, "🌕 💣", ["vs Rojas"], """2 HR, 2 near-HR, 89.6 mph EV. Rojas RHB split -1.28, HR risk -1.04. tough split lane (-1.28); pitcher suppresses HR (-1.04).""", blast="high"),
            row("Chase DeLauter", "L", "+500", 64, "🌕 💣", ["vs Rojas"], """2 HR, 2 near-HR, 89.7 mph EV. Rojas LHB split +0.33, HR risk -1.04. pitcher suppresses HR (-1.04); park suppresses carry (-6%).""", blast="high"),
            row("Byron Buxton", "R", "+280", 58, "⭐", ["vs Messick"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 98.3 mph EV. Messick RHB split -0.45, HR risk -1.04. tough split lane (-0.45); pitcher suppresses HR (-1.04).""", blast="good"),
            row("Royce Lewis", "R", "+475", 58, "", ["vs Messick"], """0 HR, 93.3 mph EV. Messick RHB split -0.45, HR risk -1.04. tough split lane (-0.45); pitcher suppresses HR (-1.04).""", blast="good"),
            row("Kody Clemens", "L", "N/A", 58, "", ["vs Messick"], """1 HR, 1 near-HR, 91.5 mph EV. Messick LHB split -1.18, HR risk -1.04. tough split lane (-1.18); pitcher suppresses HR (-1.04).""", blast="good"),
            row("Victor Caratini", "S", "+850", 58, "", ["vs Messick"], """1 HR, 1 near-HR, 90.5 mph EV. Messick SHB→RHB split -0.45, HR risk -1.04. tough split lane (-0.45); pitcher suppresses HR (-1.04).""", blast="good"),
        ],
    },
    {
        "title": "NYM @ MIL - Zach Thornton (L, NYM) vs Brandon Sproat (R, MIL)",
        "description": "Tail key data: Park boost +18% (stadium +10%, weather +8%). Thornton (HR risk -0.43, vs LHB +0.61, vs RHB -0.69). Sproat (HR risk 0.07, vs LHB -0.36, vs RHB +0.63).",
        "rows": [
            row("Jake Bauers", "L", "+394", 58, "", ["vs Thornton"], """0 HR, 86.9 mph EV. Thornton LHB split +0.61, HR risk -0.43. pitcher suppresses HR (-0.43); limited recent HR events."""),
            row("Gary Sanchez", "R", "+450", 58, "", ["vs Thornton"], """1 HR, 1 near-HR, 91.6 mph EV. Thornton RHB split -0.69, HR risk -0.43. tough split lane (-0.69); pitcher suppresses HR (-0.43).""", blast="good"),
            row("Joey Ortiz", "R", "+930", 58, "", ["vs Thornton"], """1 HR, 2 near-HR, 92.7 mph EV. Thornton RHB split -0.69, HR risk -0.43. tough split lane (-0.69); pitcher suppresses HR (-0.43).""", blast="good"),
            row("Francisco Alvarez", "R", "+460", 68, "", ["vs Sproat"], """1 HR, 1 near-HR, 89.4 mph EV. Sproat RHB split +0.63, HR risk 0.07.""", blast="good"),
            row("Francisco Lindor", "S", "+390", 82, "🌕 💣", ["vs Sproat"], """2 HR, 2 near-HR, 93.7 mph EV. Sproat SHB→RHB split +0.63, HR risk 0.07.""", blast="high"),
            row("Luis Robert", "R", "+560", 69, "", ["vs Sproat"], """0 HR, 96.0 mph EV. Sproat RHB split +0.63, HR risk 0.07. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "PIT @ NYY - Bubba Chandler (R, PIT) vs Will Warren 🧤 (R, NYY)",
        "description": "Tail key data: Park boost +24% (stadium +3%, weather +21%). Chandler (HR risk -0.62, vs LHB -0.03, vs RHB -0.82). Warren 🧤 (HR risk 1.05, vs LHB +0.49, vs RHB +0.86).",
        "rows": [
            row("Trent Grisham", "L", "+307", 80, "🌕 💣", ["vs Chandler"], """2 HR, 4 near-HR, 97.0 mph EV. Chandler LHB split -0.03, HR risk -0.62. slight split headwind (-0.03); pitcher suppresses HR (-0.62).""", blast="high"),
            row("Jazz Chisholm Jr.", "L", "+353", 69, "⭐ 🌕 💣", ["vs Chandler"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.6 mph EV. Chandler LHB split -0.03, HR risk -0.62. slight split headwind (-0.03); pitcher suppresses HR (-0.62).""", blast="high"),
            row("Ben Rice", "L", "+250", 79, "⭐ 🌕 💣", ["vs Chandler"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 96.3 mph EV. Chandler LHB split -0.03, HR risk -0.62. slight split headwind (-0.03); pitcher suppresses HR (-0.62).""", blast="high"),
            row("Ryan McMahon", "L", "+440", 65, "", ["vs Chandler"], """1 HR, 1 near-HR, 96.0 mph EV. Chandler LHB split -0.03, HR risk -0.62. slight split headwind (-0.03); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+300", 89, "🌕 💣", ["vs Warren"], """1 HR, 2 near-HR, 92.0 mph EV. Warren RHB split +0.86, HR risk 1.05.""", blast="good"),
            row("Marcell Ozuna", "R", "N/A", 89, "🌕 💣", ["vs Warren"], """1 HR, 1 near-HR, 93.2 mph EV. Warren RHB split +0.86, HR risk 1.05.""", blast="good"),
            row("Bryan Reynolds", "S", "+444", 84, "", ["vs Warren"], """1 HR, 1 near-HR, 87.9 mph EV. Warren SHB→RHB split +0.86, HR risk 1.05. lighter EV form (87.9 mph).""", blast="good"),
            row("Ryan O'Hearn", "L", "+517", 75, "", ["vs Warren"], """0 HR, 1 near-HR, 90.5 mph EV. Warren LHB split +0.49, HR risk 1.05. limited recent HR events."""),
        ],
    },
    {
        "title": "SD @ ATL - Walker Buehler 🧤 (R, SD) vs Reynaldo Lopez (R, ATL)",
        "description": "Tail key data: Park boost +4% (stadium -3%, weather +7%). Buehler 🧤 (HR risk 1.53, vs LHB +0.30, vs RHB +1.69). Lopez (HR risk -0.20, vs LHB +0.18, vs RHB -0.55).",
        "rows": [
            row("Matt Olson", "L", "+360", 92, "⭐ 🌕 💣", ["vs Buehler"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.4 mph EV. Buehler LHB split +0.30, HR risk 1.53.""", blast="high"),
            row("Drake Baldwin", "L", "+480", 86, "💎", ["vs Buehler"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.1 mph EV. Buehler LHB split +0.30, HR risk 1.53.""", blast="good"),
            row("Manny Machado", "R", "+404", 58, "⭐", ["vs Lopez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.6 mph EV. Lopez RHB split -0.55, HR risk -0.20. tough split lane (-0.55); pitcher risk below avg (-0.20).""", blast="good"),
            row("Ty France", "R", "+550", 59, "", ["vs Lopez"], """1 HR, 1 near-HR, 97.4 mph EV. Lopez RHB split -0.55, HR risk -0.20. tough split lane (-0.55); pitcher risk below avg (-0.20).""", blast="good"),
            row("Luis Campusano", "R", "+680", 58, "", ["vs Lopez"], """1 HR, 1 near-HR, 94.5 mph EV. Lopez RHB split -0.55, HR risk -0.20. tough split lane (-0.55); pitcher risk below avg (-0.20).""", blast="good"),
        ],
    },
    {
        "title": "SF @ KC - Tyler Mahle (R, SF) vs Luinder Avila (R, KC)",
        "description": "Tail key data: Park boost +8% (stadium +12%, weather -3%). Mahle (HR risk -0.62, vs LHB -0.57, vs RHB -0.24). Avila (HR risk -0.78, vs LHB -0.92, vs RHB +0.74).",
        "rows": [
            row("Carter Jensen", "L", "+492", 58, "⭐", ["vs Mahle"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.8 mph EV. Mahle LHB split -0.57, HR risk -0.62. tough split lane (-0.57); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Jac Caglianone", "L", "+400", 58, "", ["vs Mahle"], """1 HR, 2 near-HR, 92.7 mph EV. Mahle LHB split -0.57, HR risk -0.62. tough split lane (-0.57); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Lane Thomas", "R", "+750", 58, "", ["vs Mahle"], """0 HR, 1 near-HR, 95.6 mph EV. Mahle RHB split -0.24, HR risk -0.62. slight split headwind (-0.24); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Salvador Perez", "R", "+502", 59, "", ["vs Mahle"], """1 HR, 1 near-HR, 95.9 mph EV. Mahle RHB split -0.24, HR risk -0.62. slight split headwind (-0.24); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Bryce Eldridge", "L", "+450", 63, "🌕 💣", ["vs Avila"], """2 HR, 2 near-HR, 95.4 mph EV. Avila LHB split -0.92, HR risk -0.78. tough split lane (-0.92); pitcher suppresses HR (-0.78).""", blast="high"),
            row("Willy Adames", "R", "+540", 73, "⭐ 🌕 💣", ["vs Avila"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 82.6 mph EV. Avila RHB split +0.74, HR risk -0.78. pitcher suppresses HR (-0.78); lighter EV form (82.6 mph).""", blast="high"),
        ],
    },
    {
        "title": "STL @ LAA - Matthew Liberatore (L, STL) vs Walbert Urena (R, LAA)",
        "description": "Tail key data: Park boost +11% (stadium +8%, weather +3%). Liberatore (HR risk 0.25, vs LHB -0.06, vs RHB +0.37). Urena (HR risk -1.42, vs LHB -0.74, vs RHB -1.16).",
        "rows": [
            row("Jo Adell", "R", "+341", 82, "🚀 ⭐ 🌕 💣", ["vs Liberatore"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 102.0 mph EV. Liberatore RHB split +0.37, HR risk 0.25.""", blast="high"),
            row("Zach Neto", "R", "+340", 66, "", ["vs Liberatore"], """1 HR, 1 near-HR, 89.6 mph EV. Liberatore RHB split +0.37, HR risk 0.25.""", blast="good"),
            row("Jimmy Crooks", "L", "+450", 58, "", ["vs Urena"], """1 HR, 1 near-HR, 93.9 mph EV. Urena LHB split -0.74, HR risk -1.42. tough split lane (-0.74); pitcher suppresses HR (-1.42).""", blast="good"),
            row("Alec Burleson", "L", "+434", 58, "⭐", ["vs Urena"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 94.4 mph EV. Urena LHB split -0.74, HR risk -1.42. tough split lane (-0.74); pitcher suppresses HR (-1.42).""", blast="good"),
        ],
    },
    {
        "title": "TB @ TOR - Drew Rasmussen (R, TB) vs Kevin Gausman (R, TOR)",
        "description": "Tail key data: Park boost +2% (stadium +6%, weather -5%). Rasmussen (HR risk -0.01, vs LHB +0.11, vs RHB -0.24). Gausman (HR risk 0.66, vs LHB -0.55, vs RHB +1.46).",
        "rows": [
            row("George Springer", "R", "+610", 58, "💎", ["vs Rasmussen"], """Worst Pickz Hidden Gem. 0 HR, 80.4 mph EV. Rasmussen RHB split -0.24, HR risk -0.01. slight split headwind (-0.24); pitcher risk below avg (-0.01)."""),
            row("Andres Gimenez", "L", "+1120", 58, "", ["vs Rasmussen"], """0 HR, 91.2 mph EV. Rasmussen LHB split +0.11, HR risk -0.01. pitcher risk below avg (-0.01); weather carry headwind (-5%)."""),
            row("Ryan Vilade", "R", "N/A", 92, "🌕 💣", ["vs Gausman"], """2 HR, 2 near-HR, 95.1 mph EV. Gausman RHB split +1.46, HR risk 0.66. weather carry headwind (-5%).""", blast="high"),
            row("Hunter Feduccia", "L", "+1160", 76, "⭐", ["vs Gausman"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 98.5 mph EV. Gausman LHB split -0.55, HR risk 0.66. tough split lane (-0.55); weather carry headwind (-5%).""", blast="good"),
            row("Jonathan Aranda", "L", "+518", 67, "🚀", ["vs Gausman"], """0 HR, 2 near-HR, 100.9 mph EV. Gausman LHB split -0.55, HR risk 0.66. tough split lane (-0.55); weather carry headwind (-5%).""", blast="good"),
            row("Junior Caminero", "R", "+251", 80, "", ["vs Gausman"], """1 HR, 1 near-HR, 90.1 mph EV. Gausman RHB split +1.46, HR risk 0.66. weather carry headwind (-5%).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ COL - Carson Palmquist (L, WSH) vs Michael Lorenzen (R, COL)",
        "description": "Tail key data: Park boost +26% (stadium +19%, weather +7%). Palmquist (HR risk 0.21, vs LHB +1.72, vs RHB -0.37). Lorenzen (HR risk -0.05, vs LHB -0.05, vs RHB +0.25).",
        "rows": [
            row("Hunter Goodman", "R", "+186", 70, "⭐", ["vs Palmquist"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.6 mph EV. Palmquist RHB split -0.37, HR risk 0.21. slight split headwind (-0.37).""", blast="good"),
            row("Kyle Karros", "R", "+548", 58, "", ["vs Palmquist"], """0 HR, 89.5 mph EV. Palmquist RHB split -0.37, HR risk 0.21. slight split headwind (-0.37); limited recent HR events."""),
            row("CJ Abrams", "L", "+304", 76, "🌕 💣", ["vs Lorenzen"], """2 HR, 2 near-HR, 92.4 mph EV. Lorenzen LHB split -0.05, HR risk -0.05. slight split headwind (-0.05); pitcher risk below avg (-0.05).""", blast="high"),
            row("Luis Garcia Jr.", "L", "+307", 65, "⭐", ["vs Lorenzen"], """Worst Pickz Favorite. 0 HR, 97.9 mph EV. Lorenzen LHB split -0.05, HR risk -0.05. slight split headwind (-0.05); pitcher risk below avg (-0.05).""", blast="good"),
            row("James Wood", "L", "+220", 70, "", ["vs Lorenzen"], """1 HR, 1 near-HR, 98.8 mph EV. Lorenzen LHB split -0.05, HR risk -0.05. slight split headwind (-0.05); pitcher risk below avg (-0.05).""", blast="good"),
            row("Daylen Lile", "L", "+475", 64, "", ["vs Lorenzen"], """0 HR, 1 near-HR, 94.3 mph EV. Lorenzen LHB split -0.05, HR risk -0.05. slight split headwind (-0.05); pitcher risk below avg (-0.05).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-21")

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
