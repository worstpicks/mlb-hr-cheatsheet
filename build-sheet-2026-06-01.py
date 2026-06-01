#!/usr/bin/env python3
"""Generate games[] block for 2026-06-01 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Andy Pages (R)",
    "Brandon Nimmo (L)",
    "Byron Buxton (R)",
    "Casey Schmitt (R)",
    "Jac Caglianone (L)",
    "Jonathan Aranda (L)",
    "Julio Rodriguez (R)",
    "Mike Trout (R)",
    "Willy Adames (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Andrew Benintendi (L)": "CWS",
    "Andy Pages (R)": "LAD",
    "Bo Bichette (R)": "NYM",
    "Brandon Nimmo (L)": "TEX",
    "Brice Turang (L)": "MIL",
    "Brooks Lee (S)": "MIN",
    "Byron Buxton (R)": "MIN",
    "Casey Schmitt (R)": "SF",
    "Chase Meidroth (R)": "CWS",
    "Christian Yelich (L)": "MIL",
    "Colson Montgomery (L)": "CWS",
    "Colt Emerson (L)": "SEA",
    "Corbin Carroll (L)": "ARI",
    "Curtis Mead (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Ezequiel Tovar (R)": "COL",
    "Freddie Freeman (L)": "LAD",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ivan Herrera (R)": "STL",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "James Wood (L)": "WSH",
    "Joc Pederson (L)": "TEX",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Jorge Soler (R)": "LAA",
    "Jose Siri (R)": "LAA",
    "Jose Tena (L)": "WSH",
    "Josh Jung (R)": "TEX",
    "Juan Soto (L)": "NYM",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Keibert Ruiz (S)": "WSH",
    "Ketel Marte (S)": "ARI",
    "Kyle Stowers (L)": "MIA",
    "Luis Garcia Jr. (L)": "WSH",
    "MJ Melendez (L)": "NYM",
    "Mark Vientos (R)": "NYM",
    "Michael Massey (L)": "KC",
    "Mike Trout (R)": "LAA",
    "Mitch Garver (R)": "SEA",
    "Mookie Betts (R)": "LAD",
    "Nathaniel Lowe (L)": "CIN",
    "Nolan Arenado (R)": "ARI",
    "Oswald Peraza (R)": "LAA",
    "Owen Caissie (L)": "MIA",
    "Randy Arozarena (R)": "SEA",
    "Riley Greene (L)": "DET",
    "Rob Refsnyder (R)": "SEA",
    "Salvador Perez (R)": "KC",
    "Spencer Torkelson (R)": "DET",
    "TJ Rumfield (L)": "COL",
    "Will Smith (R)": "LAD",
    "William Contreras (R)": "MIL",
    "Willy Adames (R)": "SF",
    "Yandy Diaz (R)": "TB",
}

BUM_PITCHERS = {
    "Freeland",
    "deGrom",
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
        "title": "COL @ LAA - Kyle Freeland 🧤 (R, COL) vs Jose Soriano (R, LAA)",
        "description": "Tail key data: Kyle Freeland 🧤 (HR risk 2.04, vs LHB -0.14, vs RHB +2.43). Jose Soriano (HR risk -0.10, vs LHB -0.44, vs RHB +0.47).",
        "rows": [
            row("Jose Siri", "R", "N/A", 71, "💎", ["vs Freeland"], """Tail: 1 HR, 1 near-HR, 89.3 mph EV. Matchup: Freeland RHB split +2.43, HR risk 2.04. Model score 71; odds Listed prop - Over 0.5 HR.""", blast="good"),
            row("Mike Trout", "R", "+319", 74, "⭐ 💎", ["vs Freeland"], """Tail: 1 HR, 1 near-HR, 92.4 mph EV. Matchup: Freeland RHB split +2.43, HR risk 2.04. Model score 74; odds Listed +319 - Over 0.5 HR.""", blast="good"),
            row("Jorge Soler", "R", "+370", 72, "💎", ["vs Freeland"], """Tail: 0 HR, 95.8 mph EV. Matchup: Freeland RHB split +2.43, HR risk 2.04. Model score 72; odds Listed +370 - Over 0.5 HR.""", blast="good"),
            row("Oswald Peraza", "R", "+610", 75, "💎", ["vs Freeland"], """Tail: 1 HR, 1 near-HR, 92.8 mph EV. Matchup: Freeland RHB split +2.43, HR risk 2.04. Model score 75; odds Listed +610 - Over 0.5 HR.""", blast="good"),
            row("Ezequiel Tovar", "R", "+990", 78, "🌕 💣", ["vs Soriano"], """Tail: 2 HR, 2 near-HR, 86.5 mph EV. Matchup: Soriano RHB split +0.47, HR risk -0.10. Model score 78; odds Listed +990 - Over 0.5 HR.""", blast="high"),
            row("Hunter Goodman", "R", "+426", 62, "💎", ["vs Soriano"], """Tail: 0 HR, 77.8 mph EV. Matchup: Soriano RHB split +0.47, HR risk -0.10. Model score 62; odds Listed +426 - Over 0.5 HR."""),
            row("TJ Rumfield", "L", "+920", 72, "💎", ["vs Soriano"], """Tail: 1 HR, 2 near-HR, 82.1 mph EV. Matchup: Soriano LHB split -0.44, HR risk -0.10. Model score 72; odds Listed +920 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ MIN - David Sandlin (R, CWS) vs Joe Ryan (R, MIN)",
        "description": "Tail key data: Away starter risk unavailable. Joe Ryan (HR risk -0.07, vs LHB +0.21, vs RHB -0.61).",
        "rows": [
            row("Byron Buxton", "R", "+271", 77, "⭐ 💎", ["vs Sandlin"], """Tail: 1 HR, 1 near-HR, 95.2 mph EV. Matchup: Sandlin split/risk data unavailable. Model score 77; odds Listed +271 - Over 0.5 HR.""", blast="good"),
            row("Brooks Lee", "S", "+820", 82, "🌕 💣", ["vs Sandlin"], """Tail: 2 HR, 4 near-HR, 88.0 mph EV. Matchup: Sandlin split/risk data unavailable. Model score 82; odds Listed +820 - Over 0.5 HR.""", blast="high"),
            row("Andrew Benintendi", "L", "+534", 71, "💎", ["vs Ryan"], """Tail: 1 HR, 1 near-HR, 89.0 mph EV. Matchup: Ryan LHB split +0.21, HR risk -0.07. Model score 71; odds Listed +534 - Over 0.5 HR.""", blast="good"),
            row("Chase Meidroth", "R", "+1260", 71, "💎", ["vs Ryan"], """Tail: 1 HR, 1 near-HR, 89.3 mph EV. Matchup: Ryan RHB split -0.61, HR risk -0.07. Model score 71; odds Listed +1260 - Over 0.5 HR.""", blast="good"),
            row("Colson Montgomery", "L", "+360", 70, "💎", ["vs Ryan"], """Tail: 1 HR, 1 near-HR, 87.5 mph EV. Matchup: Ryan LHB split +0.21, HR risk -0.07. Model score 70; odds Listed +360 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "DET @ TB - Ty Madden (R, DET) vs Griffin Jax (R, TB)",
        "description": "Tail key data: Ty Madden (HR risk -0.48, vs LHB +0.39, vs RHB -0.87). Griffin Jax (HR risk -0.54, vs LHB -0.95, vs RHB +0.60).",
        "rows": [
            row("Jonathan Aranda", "L", "+540", 94, "⭐ 🌕 💣", ["vs Madden"], """Tail: 2 HR, 5 near-HR, 97.9 mph EV. Matchup: Madden LHB split +0.39, HR risk -0.48. Model score 94; odds Listed +540 - Over 0.5 HR.""", blast="high"),
            row("Yandy Diaz", "R", "+544", 82, "🌕 💣", ["vs Madden"], """Tail: 2 HR, 3 near-HR, 90.4 mph EV. Matchup: Madden RHB split -0.87, HR risk -0.48. Model score 82; odds Listed +544 - Over 0.5 HR.""", blast="high"),
            row("Junior Caminero", "R", "+318", 77, "💎", ["vs Madden"], """Tail: 0 HR, 2 near-HR, 96.6 mph EV. Matchup: Madden RHB split -0.87, HR risk -0.48. Model score 77; odds Listed +318 - Over 0.5 HR.""", blast="good"),
            row("Spencer Torkelson", "R", "+540", 73, "💎", ["vs Jax"], """Tail: 1 HR, 2 near-HR, 89.3 mph EV. Matchup: Jax RHB split +0.60, HR risk -0.54. Model score 73; odds Listed +540 - Over 0.5 HR.""", blast="good"),
            row("Riley Greene", "L", "+540", 65, "💎", ["vs Jax"], """Tail: 0 HR, 90.6 mph EV. Matchup: Jax LHB split -0.95, HR risk -0.54. Model score 65; odds Listed +540 - Over 0.5 HR."""),
        ],
    },
    {
        "title": "KC @ CIN - Luinder Avila (R, KC) vs Chase Burns (R, CIN)",
        "description": "Tail key data: Luinder Avila (HR risk -1.05, vs LHB -0.73, vs RHB -0.73). Chase Burns (HR risk 0.02, vs LHB +0.19, vs RHB -0.07).",
        "rows": [
            row("JJ Bleday", "L", "+310", 81, "🌕 💣", ["vs Avila"], """Tail: 2 HR, 2 near-HR, 91.1 mph EV. Matchup: Avila LHB split -0.73, HR risk -1.05. Model score 81; odds Listed +310 - Over 0.5 HR.""", blast="high"),
            row("Nathaniel Lowe", "L", "+390", 81, "🌕 💣", ["vs Avila"], """Tail: 2 HR, 3 near-HR, 88.9 mph EV. Matchup: Avila LHB split -0.73, HR risk -1.05. Model score 81; odds Listed +390 - Over 0.5 HR.""", blast="high"),
            row("Elly De La Cruz", "S", "N/A", 76, "💎", ["vs Avila"], """Tail: 1 HR, 1 near-HR, 93.9 mph EV. Matchup: Avila RHB split -0.73, HR risk -1.05. Model score 76; odds Listed prop - Over 0.5 HR.""", blast="good"),
            row("Jac Caglianone", "L", "+403", 78, "🚀 ⭐ 💎", ["vs Burns"], """Tail: 0 HR, 1 near-HR, 103.8 mph EV. Matchup: Burns LHB split +0.19, HR risk 0.02. Model score 78; odds Listed +403 - Over 0.5 HR.""", blast="good"),
            row("Michael Massey", "L", "+630", 72, "💎", ["vs Burns"], """Tail: 1 HR, 1 near-HR, 89.6 mph EV. Matchup: Burns LHB split +0.19, HR risk 0.02. Model score 72; odds Listed +630 - Over 0.5 HR.""", blast="good"),
            row("Salvador Perez", "R", "+463", 64, "💎", ["vs Burns"], """Tail: 0 HR, 1 near-HR, 87.7 mph EV. Matchup: Burns RHB split -0.07, HR risk 0.02. Model score 64; odds Listed +463 - Over 0.5 HR."""),
        ],
    },
    {
        "title": "LAD @ ARI - Emmet Sheehan (R, LAD) vs Eduardo Rodriguez (R, ARI)",
        "description": "Tail key data: Emmet Sheehan (HR risk 0.77, vs LHB +0.84, vs RHB +0.42). Eduardo Rodriguez (HR risk -0.61, vs LHB -0.46, vs RHB -0.29).",
        "rows": [
            row("Ketel Marte", "S", "+411", 70, "💎", ["vs Sheehan"], """Tail: 1 HR, 1 near-HR, 80.9 mph EV. Matchup: Sheehan RHB split +0.42, HR risk 0.77. Model score 70; odds Listed +411 - Over 0.5 HR.""", blast="good"),
            row("Nolan Arenado", "R", "+630", 62, "💎", ["vs Sheehan"], """Tail: 0 HR, 83.2 mph EV. Matchup: Sheehan RHB split +0.42, HR risk 0.77. Model score 62; odds Listed +630 - Over 0.5 HR."""),
            row("Corbin Carroll", "L", "+470", 70, "💎", ["vs Sheehan"], """Tail: 0 HR, 93.8 mph EV. Matchup: Sheehan LHB split +0.84, HR risk 0.77. Model score 70; odds Listed +470 - Over 0.5 HR.""", blast="good"),
            row("Andy Pages", "R", "+547", 70, "⭐ 💎", ["vs Rodriguez"], """Tail: 1 HR, 1 near-HR, 86.5 mph EV. Matchup: Rodriguez RHB split -0.29, HR risk -0.61. Model score 70; odds Listed +547 - Over 0.5 HR.""", blast="good"),
            row("Mookie Betts", "R", "+690", 83, "🌕 💣", ["vs Rodriguez"], """Tail: 2 HR, 2 near-HR, 93.3 mph EV. Matchup: Rodriguez RHB split -0.29, HR risk -0.61. Model score 83; odds Listed +690 - Over 0.5 HR.""", blast="high"),
            row("Will Smith", "R", "+640", 71, "💎", ["vs Rodriguez"], """Tail: 0 HR, 95.3 mph EV. Matchup: Rodriguez RHB split -0.29, HR risk -0.61. Model score 71; odds Listed +640 - Over 0.5 HR.""", blast="good"),
            row("Freddie Freeman", "L", "+650", 64, "💎", ["vs Rodriguez"], """Tail: 0 HR, 1 near-HR, 83.7 mph EV. Matchup: Rodriguez LHB split -0.46, HR risk -0.61. Model score 64; odds Listed +650 - Over 0.5 HR."""),
        ],
    },
    {
        "title": "MIA @ WSH - Sandy Alcantara (R, MIA) vs Cade Cavalli (R, WSH)",
        "description": "Tail key data: Sandy Alcantara (HR risk 0.21, vs LHB +0.50, vs RHB -0.30). Cade Cavalli (HR risk -0.27, vs LHB -0.45, vs RHB +0.14).",
        "rows": [
            row("Curtis Mead", "R", "+750", 91, "🌕 💣", ["vs Alcantara"], """Tail: 3 HR, 4 near-HR, 93.3 mph EV. Matchup: Alcantara RHB split -0.30, HR risk 0.21. Model score 91; odds Listed +750 - Over 0.5 HR.""", blast="high"),
            row("James Wood", "L", "+301", 83, "💎", ["vs Alcantara"], """Tail: 1 HR, 3 near-HR, 97.4 mph EV. Matchup: Alcantara LHB split +0.50, HR risk 0.21. Model score 83; odds Listed +301 - Over 0.5 HR.""", blast="good"),
            row("Keibert Ruiz", "S", "+910", 82, "🌕 💣", ["vs Alcantara"], """Tail: 2 HR, 3 near-HR, 89.7 mph EV. Matchup: Alcantara RHB split -0.30, HR risk 0.21. Model score 82; odds Listed +910 - Over 0.5 HR.""", blast="high"),
            row("Jose Tena", "L", "+410", 75, "💎", ["vs Alcantara"], """Tail: 1 HR, 1 near-HR, 92.7 mph EV. Matchup: Alcantara LHB split +0.50, HR risk 0.21. Model score 75; odds Listed +410 - Over 0.5 HR.""", blast="good"),
            row("Luis Garcia Jr.", "L", "+670", 85, "🌕 💣", ["vs Alcantara"], """Tail: 2 HR, 3 near-HR, 92.7 mph EV. Matchup: Alcantara LHB split +0.50, HR risk 0.21. Model score 85; odds Listed +670 - Over 0.5 HR.""", blast="high"),
            row("Heriberto Hernandez", "R", "N/A", 64, "💎", ["vs Cavalli"], """Tail: 0 HR, 90.2 mph EV. Matchup: Cavalli RHB split +0.14, HR risk -0.27. Model score 64; odds Listed prop - Over 0.5 HR."""),
            row("Owen Caissie", "L", "+930", 78, "💎", ["vs Cavalli"], """Tail: 1 HR, 1 near-HR, 95.9 mph EV. Matchup: Cavalli LHB split -0.45, HR risk -0.27. Model score 78; odds Listed +930 - Over 0.5 HR.""", blast="good"),
            row("Kyle Stowers", "L", "+559", 68, "💎", ["vs Cavalli"], """Tail: 0 HR, 92.1 mph EV. Matchup: Cavalli LHB split -0.45, HR risk -0.27. Model score 68; odds Listed +559 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "NYM @ SEA - Austin Warren (R, NYM) vs Emerson Hancock (R, SEA)",
        "description": "Tail key data: Austin Warren (HR risk -0.66, vs LHB +0.11, vs RHB -1.23). Emerson Hancock (HR risk -0.12, vs LHB +0.11, vs RHB -0.38).",
        "rows": [
            row("Julio Rodriguez", "R", "+520", 87, "⭐ 🌕 💣", ["vs Warren"], """Tail: 3 HR, 3 near-HR, 91.0 mph EV. Matchup: Warren RHB split -1.23, HR risk -0.66. Model score 87; odds Listed +520 - Over 0.5 HR.""", blast="high"),
            row("Colt Emerson", "L", "+980", 81, "💎", ["vs Warren"], """Tail: 1 HR, 1 near-HR, 98.7 mph EV. Matchup: Warren LHB split +0.11, HR risk -0.66. Model score 81; odds Listed +980 - Over 0.5 HR.""", blast="good"),
            row("Rob Refsnyder", "R", "+596", 63, "💎", ["vs Warren"], """Tail: 0 HR, 89.1 mph EV. Matchup: Warren RHB split -1.23, HR risk -0.66. Model score 63; odds Listed +596 - Over 0.5 HR."""),
            row("Mitch Garver", "R", "+290", 76, "💎", ["vs Warren"], """Tail: 1 HR, 1 near-HR, 93.9 mph EV. Matchup: Warren RHB split -1.23, HR risk -0.66. Model score 76; odds Listed +290 - Over 0.5 HR.""", blast="good"),
            row("Randy Arozarena", "R", "+680", 78, "💎", ["vs Warren"], """Tail: 1 HR, 2 near-HR, 93.8 mph EV. Matchup: Warren RHB split -1.23, HR risk -0.66. Model score 78; odds Listed +680 - Over 0.5 HR.""", blast="good"),
            row("Juan Soto", "L", "+370", 97, "🌕 💣", ["vs Hancock"], """Tail: 4 HR, 5 near-HR, 93.2 mph EV. Matchup: Hancock LHB split +0.11, HR risk -0.12. Model score 97; odds Listed +370 - Over 0.5 HR.""", blast="high"),
            row("Mark Vientos", "R", "+570", 72, "💎", ["vs Hancock"], """Tail: 1 HR, 2 near-HR, 87.7 mph EV. Matchup: Hancock RHB split -0.38, HR risk -0.12. Model score 72; odds Listed +570 - Over 0.5 HR.""", blast="good"),
            row("MJ Melendez", "L", "N/A", 77, "💎", ["vs Hancock"], """Tail: 1 HR, 1 near-HR, 94.6 mph EV. Matchup: Hancock LHB split +0.11, HR risk -0.12. Model score 77; odds Listed prop - Over 0.5 HR.""", blast="good"),
            row("Bo Bichette", "R", "+790", 62, "💎", ["vs Hancock"], """Tail: 0 HR, 88.0 mph EV. Matchup: Hancock RHB split -0.38, HR risk -0.12. Model score 62; odds Listed +790 - Over 0.5 HR."""),
        ],
    },
    {
        "title": "SF @ MIL - Landen Roupp (R, SF) vs Shane Drohan (R, MIL)",
        "description": "Tail key data: Landen Roupp (HR risk -1.04, vs LHB -1.38, vs RHB +0.05). Shane Drohan (HR risk -0.03, vs LHB -0.39, vs RHB +0.01).",
        "rows": [
            row("Christian Yelich", "L", "+880", 70, "💎", ["vs Roupp"], """Tail: 1 HR, 1 near-HR, 84.1 mph EV. Matchup: Roupp LHB split -1.38, HR risk -1.04. Model score 70; odds Listed +880 - Over 0.5 HR.""", blast="good"),
            row("William Contreras", "R", "+650", 71, "💎", ["vs Roupp"], """Tail: 0 HR, 94.7 mph EV. Matchup: Roupp RHB split +0.05, HR risk -1.04. Model score 71; odds Listed +650 - Over 0.5 HR.""", blast="good"),
            row("Brice Turang", "L", "+840", 62, "💎", ["vs Roupp"], """Tail: 0 HR, 75.2 mph EV. Matchup: Roupp LHB split -1.38, HR risk -1.04. Model score 62; odds Listed +840 - Over 0.5 HR."""),
            row("Jackson Chourio", "R", "+508", 64, "💎", ["vs Roupp"], """Tail: 0 HR, 90.1 mph EV. Matchup: Roupp RHB split +0.05, HR risk -1.04. Model score 64; odds Listed +508 - Over 0.5 HR."""),
            row("Willy Adames", "R", "+620", 66, "⭐ 💎", ["vs Drohan"], """Tail: 0 HR, 91.6 mph EV. Matchup: Drohan RHB split +0.01, HR risk -0.03. Model score 66; odds Listed +620 - Over 0.5 HR."""),
            row("Casey Schmitt", "R", "+423", 72, "⭐ 💎", ["vs Drohan"], """Tail: 1 HR, 2 near-HR, 85.7 mph EV. Matchup: Drohan RHB split +0.01, HR risk -0.03. Model score 72; odds Listed +423 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "TEX @ STL - Jacob deGrom 🧤 (R, TEX) vs Michael McGreevy (R, STL)",
        "description": "Tail key data: Jacob deGrom 🧤 (HR risk 1.61, vs LHB +2.04, vs RHB +0.67). Michael McGreevy (HR risk 0.30, vs LHB +0.55, vs RHB -0.32).",
        "rows": [
            row("Jordan Walker", "R", "+407", 71, "💎", ["vs deGrom"], """Tail: 1 HR, 1 near-HR, 89.2 mph EV. Matchup: deGrom RHB split +0.67, HR risk 1.61. Model score 71; odds Listed +407 - Over 0.5 HR.""", blast="good"),
            row("Alec Burleson", "L", "+448", 78, "💎", ["vs deGrom"], """Tail: 1 HR, 1 near-HR, 96.4 mph EV. Matchup: deGrom LHB split +2.04, HR risk 1.61. Model score 78; odds Listed +448 - Over 0.5 HR.""", blast="good"),
            row("Ivan Herrera", "R", "+588", 78, "💎", ["vs deGrom"], """Tail: 1 HR, 1 near-HR, 96.3 mph EV. Matchup: deGrom RHB split +0.67, HR risk 1.61. Model score 78; odds Listed +588 - Over 0.5 HR.""", blast="good"),
            row("JJ Wetherholt", "L", "+490", 81, "💎", ["vs deGrom"], """Tail: 1 HR, 2 near-HR, 96.9 mph EV. Matchup: deGrom LHB split +2.04, HR risk 1.61. Model score 81; odds Listed +490 - Over 0.5 HR.""", blast="good"),
            row("Joc Pederson", "L", "+390", 84, "🌕 💣", ["vs McGreevy"], """Tail: 3 HR, 3 near-HR, 86.0 mph EV. Matchup: McGreevy LHB split +0.55, HR risk 0.30. Model score 84; odds Listed +390 - Over 0.5 HR.""", blast="high"),
            row("Brandon Nimmo", "L", "+484", 90, "⭐ 🌕 💣", ["vs McGreevy"], """Tail: 2 HR, 5 near-HR, 93.5 mph EV. Matchup: McGreevy LHB split +0.55, HR risk 0.30. Model score 90; odds Listed +484 - Over 0.5 HR.""", blast="high"),
            row("Josh Jung", "R", "+810", 63, "💎", ["vs McGreevy"], """Tail: 0 HR, 88.8 mph EV. Matchup: McGreevy RHB split -0.32, HR risk 0.30. Model score 63; odds Listed +810 - Over 0.5 HR."""),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

if __name__ == '__main__':
    def js_string(value):
        return json.dumps(value, ensure_ascii=False)

    def emit_games_js(games_data):
        out = ['const games = [']
        for game in games_data:
            out.append('    {')
            out.append(f"        title: {js_string(game['title'])},")
            out.append(f"        description: {js_string(game['description'])},")
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

    out = ROOT / '_games-0601.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
