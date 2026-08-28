#!/usr/bin/env python3
"""Generate games[] block for 2026-08-28 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Adley Rutschman (S)",
    "Andres Chaparro (R)",
    "Braden Montgomery (S)",
    "Bryce Eldridge (L)",
    "Cal Raleigh (S)",
    "Carter Jensen (L)",
    "Christian Moore (R)",
    "Christian Yelich (L)",
    "Coby Mayo (R)",
    "Corey Seager (L)",
    "Drake Baldwin (L)",
    "Elly De La Cruz (S)",
    "Esmerlyn Valdez (R)",
    "Fernando Tatis Jr. (R)",
    "Garrett Mitchell (L)",
    "Heriberto Hernandez (R)",
    "Hunter Goodman (R)",
    "JJ Wetherholt (L)",
    "Jac Caglianone (L)",
    "Jackson Chourio (R)",
    "Jarren Duran (L)",
    "Jase Bowen (R)",
    "Jeremy Pena (R)",
    "Jesus Sanchez (L)",
    "Joshua Baez (R)",
    "Junior Caminero (R)",
    "Kyle Stowers (L)",
    "Matt Olson (L)",
    "Mickey Moniak (L)",
    "Mike Trout (R)",
    "Oneil Cruz (L)",
    "Rafael Devers (L)",
    "Shay Whitcomb (R)",
    "Shohei Ohtani (L)",
    "Ty France (R)",
    "Zach Neto (R)",
}

GEMS = {
    "Alec Bohm (R)",
    "Ben Rice (L)",
    "Brett Baty (L)",
    "Bryce Harper (L)",
    "Daulton Varsho (L)",
    "Dominic Canzone (L)",
    "Esteury Ruiz (R)",
    "Heliot Ramos (R)",
    "Jose Ramirez (S)",
    "Kevin McGonigle (L)",
    "Luis Robert (R)",
    "Max Kepler (L)",
    "Mike Yastrzemski (L)",
    "Patrick Wisdom (R)",
    "Randy Arozarena (R)",
    "Ryan Jeffers (R)",
    "Sal Stewart (R)",
    "Teoscar Hernandez (R)",
    "Trevor Larnach (L)",
    "Tristan Peters (L)",
    "Troy Johnston (L)",
    "Tyler Stephenson (R)",
    "Yordan Alvarez (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BOS",
    "Agustin Ramirez (R)": "MIA",
    "Alec Bohm (R)": "PHI",
    "Alejandro Kirk (R)": "TOR",
    "Andres Chaparro (R)": "WSH",
    "Andrew Pinckney (R)": "WSH",
    "Andrew Vaughn (R)": "MIL",
    "Angel Genao (S)": "CLE",
    "Austin Riley (R)": "ATL",
    "Ben Malgeri (R)": "DET",
    "Ben Rice (L)": "NYY",
    "Blaze Jordan (R)": "STL",
    "Bo Bichette (R)": "NYM",
    "Braden Montgomery (S)": "CWS",
    "Brett Baty (L)": "NYM",
    "Brewer Hicklen (R)": "ATL",
    "Brian Serven (R)": "ATH",
    "Brooks Lee (S)": "MIN",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Carlos Cortes (L)": "ATH",
    "Carter Jensen (L)": "KC",
    "Chase DeLauter (L)": "CLE",
    "Christian Franklin (R)": "BAL",
    "Christian Moore (R)": "LAA",
    "Christian Yelich (L)": "MIL",
    "Coby Mayo (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Connor Norby (R)": "COL",
    "Corey Seager (L)": "TEX",
    "Daulton Varsho (L)": "HOU",
    "Daylen Lile (L)": "WSH",
    "Dominic Canzone (L)": "SEA",
    "Donovan Walton (L)": "ATH",
    "Drake Baldwin (L)": "ATL",
    "Dylan Crews (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Esteury Ruiz (R)": "MIA",
    "Ezequiel Tovar (R)": "COL",
    "Fernando Tatis Jr. (R)": "SD",
    "Gabriel Moreno (R)": "ARI",
    "Garrett Mitchell (L)": "MIL",
    "George Lombard Jr. (R)": "NYY",
    "Geraldo Perdomo (S)": "ARI",
    "Hao Yu Lee (R)": "DET",
    "Heliot Ramos (R)": "NYY",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "LAD",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "JT Realmuto (R)": "PHI",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jake Rogers (R)": "CWS",
    "James McCann (R)": "ARI",
    "Jared Young (L)": "NYM",
    "Jarren Duran (L)": "BOS",
    "Jase Bowen (R)": "SD",
    "Javier Sanoja (R)": "MIA",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jeremy Pena (R)": "HOU",
    "Jesus Sanchez (L)": "TOR",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "CLE",
    "John Rave (L)": "KC",
    "Jonny DeLuca (R)": "TB",
    "Jordan Walker (R)": "STL",
    "Jose Fermin (R)": "STL",
    "Jose Ramirez (S)": "CLE",
    "Jose Tena (L)": "WSH",
    "Josh Lowe (L)": "LAA",
    "Joshua Baez (R)": "STL",
    "Junior Caminero (R)": "TB",
    "Kaelen Culpepper (R)": "MIN",
    "Kevin McGonigle (L)": "DET",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lawrence Butler (L)": "ATH",
    "Luis Robert (R)": "NYM",
    "Luis Torrens (R)": "NYM",
    "Luke Keaschall (R)": "MIN",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Max Muncy (L)": "LAD",
    "Max Muncy (R)": "ATH",
    "Michael Busch (L)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Mickey Gasper (S)": "BOS",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Mike Yastrzemski (L)": "ATL",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Nathan Lukes (L)": "TOR",
    "Nelson Velazquez (R)": "HOU",
    "Oneil Cruz (L)": "PIT",
    "Ozzie Albies (S)": "ATL",
    "Patrick Wisdom (R)": "SEA",
    "Pete Alonso (R)": "BAL",
    "Rafael Devers (L)": "SF",
    "Ramon Urias (R)": "STL",
    "Randy Arozarena (R)": "SEA",
    "Ryan Jeffers (R)": "MIN",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Shay Whitcomb (R)": "SF",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Teoscar Hernandez (R)": "LAD",
    "Trea Turner (R)": "PHI",
    "Trevor Larnach (L)": "MIN",
    "Tristan Peters (L)": "CWS",
    "Troy Johnston (L)": "COL",
    "Ty France (R)": "SD",
    "Tyler Stephenson (R)": "CIN",
    "Vinnie Pasquantino (L)": "KC",
    "Willi Castro (S)": "COL",
    "Wilyer Abreu (L)": "BOS",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("ARI @ SF", "Drake"),
    ("COL @ ATL", "Sugano"),
    ("CWS @ MIN", "Castillo"),
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
        "title": "ARI @ SF - Kohl Drake 🧤 (L, ARI) vs Blade Tidwell (R, SF)",
        "description": "Tail key data: Park boost -22% (stadium -16%, weather -5%). Drake 🧤 (HR risk 1.34, vs LHB +2.23, vs RHB +0.36). Tidwell (HR risk -0.92, vs LHB -0.13, vs RHB -1.19).",
        "rows": [
            row("Rafael Devers", "L", "N/A", 91, "⭐ 🌕 💣", ["vs Drake"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.6 mph EV. Drake LHB split +2.23, HR risk 1.34. park/weather net drag (-22%).""", blast="good"),
            row("Bryce Eldridge", "L", "N/A", 90, "⭐ 🌕 💣", ["vs Drake"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.8 mph EV. Drake LHB split +2.23, HR risk 1.34. park/weather net drag (-22%).""", blast="good"),
            row("Shay Whitcomb", "R", "N/A", 79, "⭐", ["vs Drake"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.8 mph EV. Drake RHB split +0.36, HR risk 1.34. park/weather net drag (-22%).""", blast="good"),
            row("Max Kepler", "L", "N/A", 58, "💎", ["vs Tidwell"], """Worst Pickz Hidden Gem. 0 HR, 97.4 mph EV. Tidwell LHB split -0.13, HR risk -0.92. slight split headwind (-0.13); pitcher suppresses HR (-0.92).""", blast="good"),
            row("James McCann", "R", "N/A", 58, "", ["vs Tidwell"], """0 HR, 94.6 mph EV. Tidwell RHB split -1.19, HR risk -0.92. tough split lane (-1.19); pitcher suppresses HR (-0.92).""", blast="good"),
            row("Gabriel Moreno", "R", "N/A", 58, "", ["vs Tidwell"], """0 HR, 1 near-HR, 94.6 mph EV. Tidwell RHB split -1.19, HR risk -0.92. tough split lane (-1.19); pitcher suppresses HR (-0.92).""", blast="good"),
            row("Geraldo Perdomo", "S", "N/A", 58, "", ["vs Tidwell"], """0 HR, 92.3 mph EV. Tidwell SHB→LHB split -0.13, HR risk -0.92. slight split headwind (-0.13); pitcher suppresses HR (-0.92).""", blast="good"),
        ],
    },
    {
        "title": "BAL @ ATH - Brandon Young (R, BAL) vs Jacob Lopez (L, ATH)",
        "description": "Tail key data: Park boost +28% (stadium +29%, weather -1%). Young (HR risk 0.79, vs LHB -0.59, vs RHB +1.66). Lopez (BAA vs LHB .200, vs RHB .270, HR/9 1.44).",
        "rows": [
            row("Brian Serven", "R", "N/A", 91, "🌕 💣", ["vs Young"], """1 HR, 1 near-HR, 92.4 mph EV. Young RHB split +1.66, HR risk 0.79.""", blast="good"),
            row("Henry Bolte", "R", "N/A", 79, "", ["vs Young"], """0 HR, 89.6 mph EV. Young RHB split +1.66, HR risk 0.79. limited recent HR events."""),
            row("Carlos Cortes", "L", "N/A", 62, "", ["vs Young"], """0 HR, 91.0 mph EV. Young LHB split -0.59, HR risk 0.79. tough split lane (-0.59); limited recent HR events."""),
            row("Donovan Walton", "L", "N/A", 62, "", ["vs Young"], """0 HR, 90.7 mph EV. Young LHB split -0.59, HR risk 0.79. tough split lane (-0.59); limited recent HR events."""),
            row("Lawrence Butler", "L", "N/A", 71, "", ["vs Young"], """0 HR, 97.8 mph EV. Young LHB split -0.59, HR risk 0.79. tough split lane (-0.59); limited recent HR events.""", blast="good"),
            row("Max Muncy", "R", "N/A", 75, "", ["vs Young"], """0 HR, 83.1 mph EV. Young RHB split +1.66, HR risk 0.79. limited recent HR events; lighter EV form (83.1 mph)."""),
            row("Coby Mayo", "R", "N/A", 81, "⭐ 🌕 💣", ["vs Lopez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.3 mph EV. limited split/risk sample.""", blast="high"),
            row("Pete Alonso", "R", "N/A", 73, "", ["vs Lopez"], """1 HR, 1 near-HR, 95.2 mph EV. limited split/risk sample.""", blast="good"),
            row("Christian Franklin", "R", "N/A", 70, "", ["vs Lopez"], """0 HR, 1 near-HR, 96.1 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "BOS @ NYY - Patrick Sandoval (L, BOS) vs Cam Schlittler (R, NYY)",
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +1%). Sandoval (HR risk -0.10, vs LHB +0.19, vs RHB -0.14). Schlittler (HR risk -0.76, vs LHB -0.34, vs RHB -0.70).",
        "rows": [
            row("Jazz Chisholm Jr.", "L", "N/A", 66, "", ["vs Sandoval"], """1 HR, 2 near-HR, 94.5 mph EV. Sandoval LHB split +0.19, HR risk -0.10. pitcher risk below avg (-0.10).""", blast="good"),
            row("Ben Rice", "L", "+440", 64, "💎", ["vs Sandoval"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.0 mph EV. Sandoval LHB split +0.19, HR risk -0.10. pitcher risk below avg (-0.10).""", blast="good"),
            row("Spencer Jones", "L", "+389", 58, "", ["vs Sandoval"], """0 HR, 91.8 mph EV. Sandoval LHB split +0.19, HR risk -0.10. pitcher risk below avg (-0.10); limited recent HR events."""),
            row("Heliot Ramos", "R", "N/A", 58, "💎", ["vs Sandoval"], """Worst Pickz Hidden Gem. 0 HR, 95.6 mph EV. Sandoval RHB split -0.14, HR risk -0.10. slight split headwind (-0.14); pitcher risk below avg (-0.10).""", blast="good"),
            row("George Lombard Jr.", "R", "+680", 58, "", ["vs Sandoval"], """0 HR, 1 near-HR, 91.2 mph EV. Sandoval RHB split -0.14, HR risk -0.10. slight split headwind (-0.14); pitcher risk below avg (-0.10)."""),
            row("Adley Rutschman", "S", "+401", 58, "⭐", ["vs Schlittler"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.8 mph EV. Schlittler SHB→LHB split -0.34, HR risk -0.76. slight split headwind (-0.34); pitcher suppresses HR (-0.76).""", blast="good"),
            row("Jarren Duran", "L", "+560", 58, "⭐", ["vs Schlittler"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.1 mph EV. Schlittler LHB split -0.34, HR risk -0.76. slight split headwind (-0.34); pitcher suppresses HR (-0.76).""", blast="good"),
            row("Mickey Gasper", "S", "+680", 65, "🌕 💣", ["vs Schlittler"], """2 HR, 2 near-HR, 95.8 mph EV. Schlittler SHB→LHB split -0.34, HR risk -0.76. slight split headwind (-0.34); pitcher suppresses HR (-0.76).""", blast="high"),
            row("Wilyer Abreu", "L", "+400", 58, "", ["vs Schlittler"], """0 HR, 94.4 mph EV. Schlittler LHB split -0.34, HR risk -0.76. slight split headwind (-0.34); pitcher suppresses HR (-0.76).""", blast="good"),
        ],
    },
    {
        "title": "CIN @ CHC - Rhett Lowder (R, CIN) vs David Peterson (L, CHC)",
        "description": "Tail key data: Park boost -9% (stadium -3%, weather -6%). Lowder (HR risk 0.35, vs LHB +0.27, vs RHB +0.12). Peterson (HR risk -0.87, vs LHB -0.26, vs RHB -0.69).",
        "rows": [
            row("Michael Busch", "L", "+500", 58, "", ["vs Lowder"], """0 HR, 92.2 mph EV. Lowder LHB split +0.27, HR risk 0.35. park/weather net drag (-9%); limited recent HR events.""", blast="good"),
            row("Ian Happ", "S", "+420", 62, "", ["vs Lowder"], """1 HR, 1 near-HR, 90.4 mph EV. Lowder SHB→LHB split +0.27, HR risk 0.35. park/weather net drag (-9%).""", blast="good"),
            row("Michael Conforto", "L", "+450", 58, "", ["vs Lowder"], """1 HR, 1 near-HR, 86.6 mph EV. Lowder LHB split +0.27, HR risk 0.35. park/weather net drag (-9%); lighter EV form (86.6 mph).""", blast="good"),
            row("Elly De La Cruz", "S", "+480", 58, "⭐", ["vs Peterson"], """Worst Pickz Favorite. 0 HR, 91.1 mph EV. Peterson SHB→LHB split -0.26, HR risk -0.87. slight split headwind (-0.26); pitcher suppresses HR (-0.87)."""),
            row("JJ Bleday", "L", "+600", 58, "", ["vs Peterson"], """0 HR, 89.1 mph EV. Peterson LHB split -0.26, HR risk -0.87. slight split headwind (-0.26); pitcher suppresses HR (-0.87)."""),
            row("Tyler Stephenson", "R", "+600", 58, "💎", ["vs Peterson"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 90.8 mph EV. Peterson RHB split -0.69, HR risk -0.87. tough split lane (-0.69); pitcher suppresses HR (-0.87)."""),
            row("Sal Stewart", "R", "+500", 58, "💎", ["vs Peterson"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 85.8 mph EV. Peterson RHB split -0.69, HR risk -0.87. tough split lane (-0.69); pitcher suppresses HR (-0.87).""", blast="good"),
        ],
    },
    {
        "title": "COL @ ATL - Tomoyuki Sugano 🧤 (R, COL) vs Grant Holmes (R, ATL)",
        "description": "Tail key data: Park boost -3% (stadium -2%, weather -1%). Sugano 🧤 (HR risk 1.05, vs LHB +0.99, vs RHB +0.20). Holmes (HR risk 0.35, vs LHB +0.26, vs RHB +0.15).",
        "rows": [
            row("Drake Baldwin", "L", "N/A", 86, "⭐", ["vs Sugano"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.5 mph EV. Sugano LHB split +0.99, HR risk 1.05.""", blast="good"),
            row("Mike Yastrzemski", "L", "N/A", 81, "💎", ["vs Sugano"], """Worst Pickz Hidden Gem. 0 HR, 96.7 mph EV. Sugano LHB split +0.99, HR risk 1.05. limited recent HR events.""", blast="good"),
            row("Matt Olson", "L", "N/A", 82, "⭐", ["vs Sugano"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 98.5 mph EV. Sugano LHB split +0.99, HR risk 1.05. limited recent HR events.""", blast="good"),
            row("Ozzie Albies", "S", "N/A", 71, "", ["vs Sugano"], """0 HR, 90.4 mph EV. Sugano SHB→LHB split +0.99, HR risk 1.05. limited recent HR events."""),
            row("Austin Riley", "R", "N/A", 67, "", ["vs Sugano"], """0 HR, 1 near-HR, 91.1 mph EV. Sugano RHB split +0.20, HR risk 1.05. limited recent HR events."""),
            row("Brewer Hicklen", "R", "N/A", 66, "", ["vs Sugano"], """0 HR, 91.5 mph EV. Sugano RHB split +0.20, HR risk 1.05. limited recent HR events."""),
            row("Hunter Goodman", "R", "N/A", 84, "⭐ 🌕 💣", ["vs Holmes"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 96.3 mph EV. Holmes RHB split +0.15, HR risk 0.35.""", blast="high"),
            row("Mickey Moniak", "L", "N/A", 69, "⭐", ["vs Holmes"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.4 mph EV. Holmes LHB split +0.26, HR risk 0.35.""", blast="good"),
            row("Willi Castro", "S", "N/A", 61, "", ["vs Holmes"], """1 HR, 1 near-HR, 88.3 mph EV. Holmes SHB→LHB split +0.26, HR risk 0.35.""", blast="good"),
            row("Connor Norby", "R", "N/A", 61, "", ["vs Holmes"], """0 HR, 94.3 mph EV. Holmes RHB split +0.15, HR risk 0.35. limited recent HR events.""", blast="good"),
            row("Troy Johnston", "L", "N/A", 58, "💎", ["vs Holmes"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 90.0 mph EV. Holmes LHB split +0.26, HR risk 0.35. limited recent HR events."""),
            row("Ezequiel Tovar", "R", "N/A", 59, "", ["vs Holmes"], """0 HR, 92.8 mph EV. Holmes RHB split +0.15, HR risk 0.35. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ MIN - Luis Castillo 🧤 (R, CWS) vs Dean Kremer (R, MIN)",
        "description": "Tail key data: Park boost -9% (stadium -7%, weather -3%). Castillo 🧤 (HR risk 1.26, vs LHB +0.67, vs RHB +0.93). Kremer (HR risk 0.38, vs LHB -0.23, vs RHB +0.79).",
        "rows": [
            row("Ryan Jeffers", "R", "+392", 73, "💎", ["vs Castillo"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 90.8 mph EV. Castillo RHB split +0.93, HR risk 1.26. park/weather net drag (-9%); limited recent HR events."""),
            row("Luke Keaschall", "R", "+617", 81, "", ["vs Castillo"], """1 HR, 1 near-HR, 90.5 mph EV. Castillo RHB split +0.93, HR risk 1.26. park/weather net drag (-9%).""", blast="good"),
            row("Trevor Larnach", "L", "+422", 79, "💎", ["vs Castillo"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.8 mph EV. Castillo LHB split +0.67, HR risk 1.26. park/weather net drag (-9%).""", blast="good"),
            row("Brooks Lee", "S", "+304", 90, "🌕 💣", ["vs Castillo"], """2 HR, 2 near-HR, 91.2 mph EV. Castillo SHB→RHB split +0.93, HR risk 1.26. park/weather net drag (-9%).""", blast="high"),
            row("Kaelen Culpepper", "R", "+570", 90, "🌕 💣", ["vs Castillo"], """2 HR, 2 near-HR, 90.6 mph EV. Castillo RHB split +0.93, HR risk 1.26. park/weather net drag (-9%).""", blast="high"),
            row("Tristan Peters", "L", "+404", 66, "🌕 💣 💎", ["vs Kremer"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 89.0 mph EV. Kremer LHB split -0.23, HR risk 0.38. slight split headwind (-0.23); park/weather net drag (-9%).""", blast="high"),
            row("Miguel Vargas", "R", "+273", 58, "", ["vs Kremer"], """0 HR, 91.3 mph EV. Kremer RHB split +0.79, HR risk 0.38. park/weather net drag (-9%); limited recent HR events."""),
            row("Braden Montgomery", "S", "+398", 60, "⭐", ["vs Kremer"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 91.9 mph EV. Kremer SHB→RHB split +0.79, HR risk 0.38. park/weather net drag (-9%); limited recent HR events."""),
            row("Munetaka Murakami", "L", "+174", 61, "", ["vs Kremer"], """1 HR, 1 near-HR, 93.0 mph EV. Kremer LHB split -0.23, HR risk 0.38. slight split headwind (-0.23); park/weather net drag (-9%).""", blast="good"),
            row("Colson Montgomery", "L", "+204", 58, "", ["vs Kremer"], """0 HR, 89.3 mph EV. Kremer LHB split -0.23, HR risk 0.38. slight split headwind (-0.23); park/weather net drag (-9%)."""),
            row("Jake Rogers", "R", "N/A", 59, "", ["vs Kremer"], """0 HR, 2 near-HR, 82.2 mph EV. Kremer RHB split +0.79, HR risk 0.38. park/weather net drag (-9%); lighter EV form (82.2 mph).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ NYM - Hunter Brown (R, HOU) vs Christian Scott (R, NYM)",
        "description": "Tail key data: Park boost -6% (stadium -2%, weather -4%). Brown (HR risk -0.06, vs LHB +0.66, vs RHB -0.91). Scott (HR risk -0.33, vs LHB +0.13, vs RHB -0.73).",
        "rows": [
            row("Jared Young", "L", "N/A", 60, "", ["vs Brown"], """0 HR, 93.8 mph EV. Brown LHB split +0.66, HR risk -0.06. pitcher risk below avg (-0.06); park/weather net drag (-6%).""", blast="good"),
            row("Luis Torrens", "R", "N/A", 73, "🌕 💣", ["vs Brown"], """3 HR, 3 near-HR, 94.1 mph EV. Brown RHB split -0.91, HR risk -0.06. tough split lane (-0.91); pitcher risk below avg (-0.06).""", blast="high"),
            row("Luis Robert", "R", "N/A", 67, "🌕 💣 💎", ["vs Brown"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 99.9 mph EV. Brown RHB split -0.91, HR risk -0.06. tough split lane (-0.91); pitcher risk below avg (-0.06).""", blast="high"),
            row("Bo Bichette", "R", "N/A", 67, "🌕 💣", ["vs Brown"], """2 HR, 3 near-HR, 91.8 mph EV. Brown RHB split -0.91, HR risk -0.06. tough split lane (-0.91); pitcher risk below avg (-0.06).""", blast="high"),
            row("Brett Baty", "L", "N/A", 61, "💎", ["vs Brown"], """Worst Pickz Hidden Gem. 0 HR, 95.1 mph EV. Brown LHB split +0.66, HR risk -0.06. pitcher risk below avg (-0.06); park/weather net drag (-6%).""", blast="good"),
            row("Yordan Alvarez", "L", "N/A", 58, "💎", ["vs Scott"], """Worst Pickz Hidden Gem. 0 HR, 94.5 mph EV. Scott LHB split +0.13, HR risk -0.33. pitcher risk below avg (-0.33); park/weather net drag (-6%).""", blast="good"),
            row("Daulton Varsho", "L", "N/A", 58, "💎", ["vs Scott"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.7 mph EV. Scott LHB split +0.13, HR risk -0.33. pitcher risk below avg (-0.33); park/weather net drag (-6%).""", blast="good"),
            row("Jeremy Pena", "R", "N/A", 58, "⭐", ["vs Scott"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 90.0 mph EV. Scott RHB split -0.73, HR risk -0.33. tough split lane (-0.73); pitcher risk below avg (-0.33).""", blast="good"),
            row("Nelson Velazquez", "R", "N/A", 58, "", ["vs Scott"], """0 HR, 1 near-HR, 87.9 mph EV. Scott RHB split -0.73, HR risk -0.33. tough split lane (-0.73); pitcher risk below avg (-0.33)."""),
        ],
    },
    {
        "title": "KC @ CLE - Michael Wacha (R, KC) vs Tanner Bibee (R, CLE)",
        "description": "Tail key data: Park boost -16% (stadium -3%, weather -13%). Wacha (HR risk 0.22, vs LHB -0.69, vs RHB +1.23). Bibee (HR risk 0.38, vs LHB +0.96, vs RHB -0.81).",
        "rows": [
            row("Jose Ramirez", "S", "N/A", 67, "💎", ["vs Wacha"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 95.0 mph EV. Wacha SHB→RHB split +1.23, HR risk 0.22. park/weather net drag (-16%); limited recent HR events.""", blast="good"),
            row("Jo Adell", "R", "N/A", 58, "", ["vs Wacha"], """0 HR, 89.9 mph EV. Wacha RHB split +1.23, HR risk 0.22. park/weather net drag (-16%); limited recent HR events."""),
            row("Angel Genao", "S", "N/A", 63, "", ["vs Wacha"], """0 HR, 92.0 mph EV. Wacha SHB→RHB split +1.23, HR risk 0.22. park/weather net drag (-16%); limited recent HR events.""", blast="good"),
            row("Chase DeLauter", "L", "N/A", 58, "", ["vs Wacha"], """0 HR, 95.3 mph EV. Wacha LHB split -0.69, HR risk 0.22. tough split lane (-0.69); park/weather net drag (-16%).""", blast="good"),
            row("Carter Jensen", "L", "N/A", 72, "⭐", ["vs Bibee"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.3 mph EV. Bibee LHB split +0.96, HR risk 0.38. park/weather net drag (-16%).""", blast="good"),
            row("Jac Caglianone", "L", "N/A", 67, "⭐", ["vs Bibee"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.7 mph EV. Bibee LHB split +0.96, HR risk 0.38. park/weather net drag (-16%); limited recent HR events.""", blast="good"),
            row("John Rave", "L", "N/A", 63, "", ["vs Bibee"], """0 HR, 92.7 mph EV. Bibee LHB split +0.96, HR risk 0.38. park/weather net drag (-16%); limited recent HR events.""", blast="good"),
            row("Salvador Perez", "R", "N/A", 58, "", ["vs Bibee"], """1 HR, 1 near-HR, 88.3 mph EV. Bibee RHB split -0.81, HR risk 0.38. tough split lane (-0.81); park/weather net drag (-16%).""", blast="good"),
            row("Vinnie Pasquantino", "L", "N/A", 58, "", ["vs Bibee"], """0 HR, 87.5 mph EV. Bibee LHB split +0.96, HR risk 0.38. park/weather net drag (-16%); limited recent HR events."""),
        ],
    },
    {
        "title": "LAD @ DET - Tarik Skubal (L, LAD) vs Drew Anderson (R, DET)",
        "description": "Tail key data: Park boost -23% (stadium -11%, weather -12%). Skubal (HR risk -0.58, vs LHB -0.03, vs RHB -0.39). Anderson (HR risk 0.70, vs LHB +0.43, vs RHB +0.37).",
        "rows": [
            row("Kevin McGonigle", "L", "+870", 58, "💎", ["vs Skubal"], """Worst Pickz Hidden Gem. 0 HR, 92.4 mph EV. Skubal LHB split -0.03, HR risk -0.58. slight split headwind (-0.03); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Hao Yu Lee", "R", "+830", 58, "", ["vs Skubal"], """0 HR, 1 near-HR, 94.7 mph EV. Skubal RHB split -0.39, HR risk -0.58. slight split headwind (-0.39); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Ben Malgeri", "R", "+1060", 58, "", ["vs Skubal"], """0 HR, 92.7 mph EV. Skubal RHB split -0.39, HR risk -0.58. slight split headwind (-0.39); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Max Muncy", "L", "+300", 72, "", ["vs Anderson"], """1 HR, 1 near-HR, 96.4 mph EV. Anderson LHB split +0.43, HR risk 0.70. park/weather net drag (-23%).""", blast="good"),
            row("Shohei Ohtani", "L", "+320", 64, "⭐", ["vs Anderson"], """Worst Pickz Favorite. 0 HR, 93.6 mph EV. Anderson LHB split +0.43, HR risk 0.70. park/weather net drag (-23%); limited recent HR events.""", blast="good"),
            row("Mookie Betts", "R", "+600", 58, "", ["vs Anderson"], """0 HR, 91.5 mph EV. Anderson RHB split +0.37, HR risk 0.70. park/weather net drag (-23%); limited recent HR events."""),
            row("Teoscar Hernandez", "R", "+560", 60, "💎", ["vs Anderson"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 91.8 mph EV. Anderson RHB split +0.37, HR risk 0.70. park/weather net drag (-23%); limited recent HR events."""),
            row("Hunter Feduccia", "L", "+800", 58, "", ["vs Anderson"], """0 HR, 86.5 mph EV. Anderson LHB split +0.43, HR risk 0.70. park/weather net drag (-23%); limited recent HR events."""),
        ],
    },
    {
        "title": "MIA @ WSH - Eury Perez (R, MIA) vs Jackson Kent (L, WSH)",
        "description": "Tail key data: Park boost +10% (stadium +4%, weather +6%). Perez (HR risk -0.95, vs LHB -0.86, vs RHB -0.30). Kent (HR risk -0.47, vs LHB -1.45, vs RHB +0.04).",
        "rows": [
            row("Dylan Crews", "R", "+520", 58, "", ["vs Perez"], """0 HR, 98.7 mph EV. Perez RHB split -0.30, HR risk -0.95. slight split headwind (-0.30); pitcher suppresses HR (-0.95).""", blast="good"),
            row("Andres Chaparro", "R", "N/A", 58, "⭐", ["vs Perez"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 91.5 mph EV. Perez RHB split -0.30, HR risk -0.95. slight split headwind (-0.30); pitcher suppresses HR (-0.95)."""),
            row("Daylen Lile", "L", "+600", 58, "🌕 💣", ["vs Perez"], """2 HR, 2 near-HR, 88.0 mph EV. Perez LHB split -0.86, HR risk -0.95. tough split lane (-0.86); pitcher suppresses HR (-0.95).""", blast="high"),
            row("Andrew Pinckney", "R", "N/A", 58, "", ["vs Perez"], """0 HR, 90.9 mph EV. Perez RHB split -0.30, HR risk -0.95. slight split headwind (-0.30); pitcher suppresses HR (-0.95)."""),
            row("Jose Tena", "L", "N/A", 58, "", ["vs Perez"], """0 HR, 90.1 mph EV. Perez LHB split -0.86, HR risk -0.95. tough split lane (-0.86); pitcher suppresses HR (-0.95)."""),
            row("Heriberto Hernandez", "R", "+360", 59, "⭐", ["vs Kent"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 97.0 mph EV. Kent RHB split +0.04, HR risk -0.47. pitcher suppresses HR (-0.47); limited recent HR events.""", blast="good"),
            row("Esteury Ruiz", "R", "N/A", 58, "💎", ["vs Kent"], """Worst Pickz Hidden Gem. 0 HR, 89.1 mph EV. Kent RHB split +0.04, HR risk -0.47. pitcher suppresses HR (-0.47); limited recent HR events."""),
            row("Kyle Stowers", "L", "+450", 58, "⭐", ["vs Kent"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 97.8 mph EV. Kent LHB split -1.45, HR risk -0.47. tough split lane (-1.45); pitcher suppresses HR (-0.47).""", blast="good"),
            row("Agustin Ramirez", "R", "+520", 58, "", ["vs Kent"], """0 HR, 92.4 mph EV. Kent RHB split +0.04, HR risk -0.47. pitcher suppresses HR (-0.47); limited recent HR events.""", blast="good"),
            row("Javier Sanoja", "R", "N/A", 58, "", ["vs Kent"], """0 HR, 93.3 mph EV. Kent RHB split +0.04, HR risk -0.47. pitcher suppresses HR (-0.47); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "PHI @ LAA - Andrew Painter (R, PHI) vs Reid Detmers (L, LAA)",
        "description": "Tail key data: Park boost +0% (stadium -9%, weather +9%). Painter (HR risk -0.03, vs LHB -0.04, vs RHB -0.01). Detmers (HR risk 0.09, vs LHB -0.11, vs RHB +0.07).",
        "rows": [
            row("Zach Neto", "R", "N/A", 64, "⭐", ["vs Painter"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.0 mph EV. Painter RHB split -0.01, HR risk -0.03. slight split headwind (-0.01); pitcher risk below avg (-0.03).""", blast="good"),
            row("Josh Lowe", "L", "N/A", 62, "", ["vs Painter"], """1 HR, 2 near-HR, 92.9 mph EV. Painter LHB split -0.04, HR risk -0.03. slight split headwind (-0.04); pitcher risk below avg (-0.03).""", blast="good"),
            row("Christian Moore", "R", "N/A", 63, "⭐", ["vs Painter"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.2 mph EV. Painter RHB split -0.01, HR risk -0.03. slight split headwind (-0.01); pitcher risk below avg (-0.03).""", blast="good"),
            row("Mike Trout", "R", "N/A", 60, "⭐", ["vs Painter"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 94.1 mph EV. Painter RHB split -0.01, HR risk -0.03. slight split headwind (-0.01); pitcher risk below avg (-0.03).""", blast="good"),
            row("Bryce Harper", "L", "N/A", 64, "💎", ["vs Detmers"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.1 mph EV. Detmers LHB split -0.11, HR risk 0.09. slight split headwind (-0.11); park suppresses carry (-9%).""", blast="good"),
            row("JT Realmuto", "R", "N/A", 58, "", ["vs Detmers"], """0 HR, 93.7 mph EV. Detmers RHB split +0.07, HR risk 0.09. park suppresses carry (-9%); limited recent HR events.""", blast="good"),
            row("Kyle Schwarber", "L", "N/A", 58, "", ["vs Detmers"], """0 HR, 92.1 mph EV. Detmers LHB split -0.11, HR risk 0.09. slight split headwind (-0.11); park suppresses carry (-9%).""", blast="good"),
            row("Alec Bohm", "R", "N/A", 59, "💎", ["vs Detmers"], """Worst Pickz Hidden Gem. 0 HR, 94.9 mph EV. Detmers RHB split +0.07, HR risk 0.09. park suppresses carry (-9%); limited recent HR events.""", blast="good"),
            row("Trea Turner", "R", "N/A", 60, "", ["vs Detmers"], """0 HR, 98.6 mph EV. Detmers RHB split +0.07, HR risk 0.09. park suppresses carry (-9%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "PIT @ STL - Jared Jones (R, PIT) vs Quinn Mathews (L, STL)",
        "description": "Tail key data: Park boost -20% (stadium -9%, weather -11%). Jones (HR risk 0.78, vs LHB -0.28, vs RHB +1.50). Mathews (HR risk -1.49, vs LHB +0.00, vs RHB -0.80).",
        "rows": [
            row("Joshua Baez", "R", "+364", 67, "⭐", ["vs Jones"], """Worst Pickz Favorite. 0 HR, 90.5 mph EV. Jones RHB split +1.50, HR risk 0.78. park/weather net drag (-20%); limited recent HR events."""),
            row("JJ Wetherholt", "L", "+444", 62, "⭐", ["vs Jones"], """Worst Pickz Favorite. 0 HR, 98.7 mph EV. Jones LHB split -0.28, HR risk 0.78. slight split headwind (-0.28); park/weather net drag (-20%).""", blast="good"),
            row("Jordan Walker", "R", "+362", 86, "🌕 💣", ["vs Jones"], """2 HR, 2 near-HR, 91.3 mph EV. Jones RHB split +1.50, HR risk 0.78. park/weather net drag (-20%).""", blast="high"),
            row("Jimmy Crooks", "L", "+448", 58, "", ["vs Jones"], """0 HR, 1 near-HR, 89.9 mph EV. Jones LHB split -0.28, HR risk 0.78. slight split headwind (-0.28); park/weather net drag (-20%)."""),
            row("Ramon Urias", "R", "N/A", 66, "", ["vs Jones"], """0 HR, 90.1 mph EV. Jones RHB split +1.50, HR risk 0.78. park/weather net drag (-20%); limited recent HR events."""),
            row("Jose Fermin", "R", "+941", 73, "", ["vs Jones"], """0 HR, 93.1 mph EV. Jones RHB split +1.50, HR risk 0.78. park/weather net drag (-20%); limited recent HR events.""", blast="good"),
            row("Blaze Jordan", "R", "N/A", 66, "", ["vs Jones"], """0 HR, 1 near-HR, 88.3 mph EV. Jones RHB split +1.50, HR risk 0.78. park/weather net drag (-20%); limited recent HR events."""),
            row("Esmerlyn Valdez", "R", "+294", 58, "⭐", ["vs Mathews"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 98.1 mph EV. Mathews RHB split -0.80, HR risk -1.49. tough split lane (-0.80); pitcher suppresses HR (-1.49).""", blast="good"),
            row("Oneil Cruz", "L", "+315", 58, "⭐", ["vs Mathews"], """Worst Pickz Favorite. 0 HR, 96.5 mph EV. Mathews LHB split +0.00, HR risk -1.49. pitcher suppresses HR (-1.49); park/weather net drag (-20%).""", blast="good"),
        ],
    },
    {
        "title": "SD @ TB - Casey Mize (R, SD) vs Shane McClanahan (L, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Mize (HR risk 0.55, vs LHB -0.21, vs RHB +1.07). McClanahan (HR risk -0.20, vs LHB -0.51, vs RHB +0.11).",
        "rows": [
            row("Junior Caminero", "R", "N/A", 75, "⭐", ["vs Mize"], """Worst Pickz Favorite. 0 HR, 95.8 mph EV. Mize RHB split +1.07, HR risk 0.55. limited recent HR events.""", blast="good"),
            row("Jonny DeLuca", "R", "N/A", 64, "", ["vs Mize"], """0 HR, 89.7 mph EV. Mize RHB split +1.07, HR risk 0.55. limited recent HR events."""),
            row("Yandy Diaz", "R", "N/A", 65, "", ["vs Mize"], """0 HR, 90.7 mph EV. Mize RHB split +1.07, HR risk 0.55. limited recent HR events."""),
            row("Fernando Tatis Jr.", "R", "N/A", 80, "⭐ 🌕 💣", ["vs McClanahan"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 97.2 mph EV. McClanahan RHB split +0.11, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="high"),
            row("Jase Bowen", "R", "N/A", 72, "🚀 ⭐ 🌕 💣", ["vs McClanahan"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.5 mph EV. McClanahan RHB split +0.11, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="high"),
            row("Ty France", "R", "N/A", 61, "⭐", ["vs McClanahan"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.0 mph EV. McClanahan RHB split +0.11, HR risk -0.20. pitcher risk below avg (-0.20).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ TOR - Emerson Hancock (R, SEA) vs Dylan Cease (R, TOR)",
        "description": "Tail key data: Park boost -7% (stadium +6%, weather -13%). Hancock (BAA vs LHB .233, vs RHB .236, HR/9 1.21). Cease (HR risk -1.05, vs LHB -0.73, vs RHB -0.62).",
        "rows": [
            row("Jesus Sanchez", "L", "N/A", 58, "⭐", ["vs Hancock"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 90.4 mph EV. limited split/risk sample; park/weather net drag (-7%)."""),
            row("Nathan Lukes", "L", "N/A", 63, "", ["vs Hancock"], """1 HR, 1 near-HR, 94.3 mph EV. limited split/risk sample; park/weather net drag (-7%).""", blast="good"),
            row("Alejandro Kirk", "R", "N/A", 58, "", ["vs Hancock"], """0 HR, 92.4 mph EV. limited split/risk sample; park/weather net drag (-7%).""", blast="good"),
            row("Cal Raleigh", "S", "N/A", 58, "⭐ 🌕 💣", ["vs Cease"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.5 mph EV. Cease SHB→RHB split -0.62, HR risk -1.05. tough split lane (-0.62); pitcher suppresses HR (-1.05).""", blast="high"),
            row("Randy Arozarena", "R", "N/A", 58, "💎", ["vs Cease"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.8 mph EV. Cease RHB split -0.62, HR risk -1.05. tough split lane (-0.62); pitcher suppresses HR (-1.05).""", blast="good"),
            row("Patrick Wisdom", "R", "N/A", 58, "💎", ["vs Cease"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 91.6 mph EV. Cease RHB split -0.62, HR risk -1.05. tough split lane (-0.62); pitcher suppresses HR (-1.05)."""),
            row("Dominic Canzone", "L", "N/A", 58, "💎", ["vs Cease"], """Worst Pickz Hidden Gem. 0 HR, 95.0 mph EV. Cease LHB split -0.73, HR risk -1.05. tough split lane (-0.73); pitcher suppresses HR (-1.05).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ MIL - Cody Bradford (L, TEX) vs Logan Henderson (R, MIL)",
        "description": "Tail key data: Park boost +5% (stadium -3%, weather +7%). Bradford (HR risk -0.55, vs LHB +0.79, vs RHB -0.63). Henderson (HR risk 0.12, vs LHB +0.53, vs RHB -0.68).",
        "rows": [
            row("Jackson Chourio", "R", "+204", 58, "⭐", ["vs Bradford"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.5 mph EV. Bradford RHB split -0.63, HR risk -0.55. tough split lane (-0.63); pitcher suppresses HR (-0.55).""", blast="good"),
            row("Christian Yelich", "L", "+362", 60, "⭐", ["vs Bradford"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 91.4 mph EV. Bradford LHB split +0.79, HR risk -0.55. pitcher suppresses HR (-0.55).""", blast="good"),
            row("Garrett Mitchell", "L", "+419", 62, "⭐", ["vs Bradford"], """Worst Pickz Favorite. 0 HR, 97.3 mph EV. Bradford LHB split +0.79, HR risk -0.55. pitcher suppresses HR (-0.55); limited recent HR events.""", blast="good"),
            row("Andrew Vaughn", "R", "+238", 58, "", ["vs Bradford"], """0 HR, 93.0 mph EV. Bradford RHB split -0.63, HR risk -0.55. tough split lane (-0.63); pitcher suppresses HR (-0.55).""", blast="good"),
            row("Jake Burger", "R", "+268", 63, "🚀", ["vs Henderson"], """1 HR, 2 near-HR, 100.5 mph EV. Henderson RHB split -0.68, HR risk 0.12. tough split lane (-0.68).""", blast="good"),
            row("Corey Seager", "L", "+189", 62, "⭐", ["vs Henderson"], """Worst Pickz Favorite. 0 HR, 92.5 mph EV. Henderson LHB split +0.53, HR risk 0.12. limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-28")

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

    out = ROOT / '_games-0828.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
