#!/usr/bin/env python3
"""Generate games[] block for 2026-07-31 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Brett Baty (L)",
    "Bryan Reynolds (S)",
    "Elly De La Cruz (S)",
    "Kody Clemens (L)",
    "Kyle Stowers (L)",
    "Lawrence Butler (L)",
    "Luis Garcia Jr. (L)",
    "Pete Crow-Armstrong (L)",
    "Victor Mesa Jr. (L)",
}

GEMS = {
    "Coby Mayo (R)",
    "Derek Hill (R)",
    "George Springer (R)",
    "Gunnar Henderson (L)",
    "Hunter Goodman (R)",
    "Jake Bauers (L)",
    "Jimmy Crooks (L)",
    "Jo Adell (R)",
    "Manny Machado (R)",
    "Nick Kurtz (L)",
    "Rob Refsnyder (R)",
    "Royce Lewis (R)",
    "Taylor Trammell (L)",
    "Tyler Soderstrom (L)",
    "Willi Castro (S)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Alejandro Osuna (L)": "TEX",
    "Andrew Vaughn (R)": "MIL",
    "Austin Riley (R)": "ATL",
    "Austin Wells (L)": "NYY",
    "Ben Rice (L)": "NYY",
    "Brandon Lowe (L)": "PIT",
    "Brandon Valenzuela (S)": "TOR",
    "Brayan Rocchio (S)": "CLE",
    "Brett Baty (L)": "NYM",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Carter Jensen (L)": "KC",
    "Christian Yelich (L)": "MIL",
    "Coby Mayo (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Corbin Carroll (L)": "ARI",
    "Daylen Lile (L)": "WSH",
    "Derek Hill (R)": "PHI",
    "Dillon Dingler (R)": "DET",
    "Drew Gilbert (L)": "SF",
    "Dylan Beavers (L)": "BAL",
    "Eduardo Valencia (R)": "DET",
    "Elly De La Cruz (S)": "CIN",
    "Endy Rodriguez (S)": "PIT",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "George Springer (R)": "TOR",
    "Grant McCray (L)": "SF",
    "Griffin Conine (L)": "MIA",
    "Gunnar Henderson (L)": "BAL",
    "Hao-Yu Lee (R)": "DET",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "James Outman (L)": "DET",
    "James Wood (L)": "WSH",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jimmy Crooks (L)": "STL",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "John Rave (L)": "KC",
    "Junior Caminero (R)": "TB",
    "Justin Dean (R)": "CHC",
    "Kody Clemens (L)": "MIN",
    "Kyle Stowers (L)": "MIA",
    "Lawrence Butler (L)": "ATH",
    "Luis Garcia Jr. (L)": "WSH",
    "Luke Raley (L)": "SEA",
    "Manny Machado (R)": "SD",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Mickey Moniak (L)": "COL",
    "Miguel Amaya (R)": "CHC",
    "Mitch Garver (R)": "SEA",
    "Munetaka Murakami (L)": "CWS",
    "Nick Kurtz (L)": "ATH",
    "Ozzie Albies (S)": "ATL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randy Arozarena (R)": "SEA",
    "Rhys Hoskins (R)": "CLE",
    "Rob Refsnyder (R)": "SEA",
    "Royce Lewis (R)": "MIN",
    "Ryan Jeffers (R)": "MIN",
    "Salvador Perez (R)": "KC",
    "Sam Antonacci (L)": "CWS",
    "Spencer Jones (L)": "NYY",
    "Starling Marte (R)": "KC",
    "Taylor Trammell (L)": "HOU",
    "Tommy White (R)": "ATH",
    "Travis Bazzana (L)": "CLE",
    "Travis d'Arnaud (R)": "LAA",
    "Trea Turner (R)": "PHI",
    "Ty France (R)": "SD",
    "Tyler O'Neill (R)": "BAL",
    "Tyler Soderstrom (L)": "ATH",
    "Victor Mesa Jr. (L)": "TB",
    "Willi Castro (S)": "COL",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("KC @ COL", "Sugano"),
    ("MIL @ LAA", "Johnson"),
    ("NYY @ CHC", "Warren"),
    ("WSH @ ATL", "Elder"),
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
        "title": "ARI @ CLE - Mitch Bratt (L, ARI) vs Tanner Bibee (R, CLE)",
        "description": "Tail key data: Park boost +8% (stadium -3%, weather +11%). Bratt (HR risk 0.93, vs LHB +2.07, vs RHB +0.11). Bibee (HR risk -0.23, vs LHB +0.23, vs RHB -0.88).",
        "rows": [
            row("Travis Bazzana", "L", "N/A", 79, "", ["vs Bratt"], """0 HR, 91.7 mph EV. Bratt LHB split +2.07, HR risk 0.93. limited recent HR events."""),
            row("Rhys Hoskins", "R", "N/A", 71, "", ["vs Bratt"], """1 HR, 1 near-HR, 88.5 mph EV. Bratt RHB split +0.11, HR risk 0.93.""", blast="good"),
            row("Brayan Rocchio", "S", "N/A", 88, "🌕 💣", ["vs Bratt"], """1 HR, 1 near-HR, 91.3 mph EV. Bratt SHB→LHB split +2.07, HR risk 0.93.""", blast="good"),
            row("Corbin Carroll", "L", "N/A", 59, "", ["vs Bibee"], """0 HR, 94.3 mph EV. Bibee LHB split +0.23, HR risk -0.23. pitcher risk below avg (-0.23); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ TB - Erick Fedde (R, CWS) vs Nick Martinez (R, TB)",
        "description": "Tail key data: Park boost -4% (stadium -5%, weather +1%). Fedde (HR risk 0.49, vs LHB -0.04, vs RHB +0.81). Martinez (HR risk -0.63, vs LHB -0.06, vs RHB -1.13).",
        "rows": [
            row("Victor Mesa Jr.", "L", "+356", 76, "⭐ 🌕 💣", ["vs Fedde"], """Worst Pickz Favorite. 2 HR, 1 near-HR, 93.1 mph EV. Fedde LHB split -0.04, HR risk 0.49. slight split headwind (-0.04).""", blast="high"),
            row("Junior Caminero", "R", "+176", 67, "", ["vs Fedde"], """0 HR, 2 near-HR, 87.8 mph EV. Fedde RHB split +0.81, HR risk 0.49. lighter EV form (87.8 mph).""", blast="good"),
            row("Munetaka Murakami", "L", "N/A", 58, "", ["vs Martinez"], """1 HR, 2 near-HR, 93.2 mph EV. Martinez LHB split -0.06, HR risk -0.63. slight split headwind (-0.06); pitcher suppresses HR (-0.63).""", blast="good"),
            row("Sam Antonacci", "L", "N/A", 58, "", ["vs Martinez"], """1 HR, 1 near-HR, 93.7 mph EV. Martinez LHB split -0.06, HR risk -0.63. slight split headwind (-0.06); pitcher suppresses HR (-0.63).""", blast="good"),
            row("Colson Montgomery", "L", "N/A", 58, "", ["vs Martinez"], """0 HR, 92.0 mph EV. Martinez LHB split -0.06, HR risk -0.63. slight split headwind (-0.06); pitcher suppresses HR (-0.63).""", blast="good"),
        ],
    },
    {
        "title": "DET @ ATH - Casey Mize (R, DET) vs Jeffrey Springs (L, ATH)",
        "description": "Tail key data: Park boost +33% (stadium +32%, weather +0%). Mize (HR risk -0.99, vs LHB -1.08, vs RHB -0.30). Springs (HR risk 0.88, vs LHB -0.41, vs RHB +1.23).",
        "rows": [
            row("Nick Kurtz", "L", "N/A", 76, "🌕 💣 💎", ["vs Mize"], """Worst Pickz Hidden Gem. 3 HR, 4 near-HR, 95.6 mph EV. Mize LHB split -1.08, HR risk -0.99. tough split lane (-1.08); pitcher suppresses HR (-0.99).""", blast="high"),
            row("Tyler Soderstrom", "L", "N/A", 67, "🌕 💣 💎", ["vs Mize"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.2 mph EV. Mize LHB split -1.08, HR risk -0.99. tough split lane (-1.08); pitcher suppresses HR (-0.99).""", blast="high"),
            row("Lawrence Butler", "L", "N/A", 58, "⭐", ["vs Mize"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 95.5 mph EV. Mize LHB split -1.08, HR risk -0.99. tough split lane (-1.08); pitcher suppresses HR (-0.99).""", blast="good"),
            row("Tommy White", "R", "N/A", 58, "", ["vs Mize"], """0 HR, 1 near-HR, 88.8 mph EV. Mize RHB split -0.30, HR risk -0.99. slight split headwind (-0.30); pitcher suppresses HR (-0.99)."""),
            row("Hao-Yu Lee", "R", "N/A", 80, "", ["vs Springs"], """0 HR, 1 near-HR, 90.0 mph EV. Springs RHB split +1.23, HR risk 0.88. limited recent HR events."""),
            row("James Outman", "L", "N/A", 76, "", ["vs Springs"], """0 HR, 1 near-HR, 95.5 mph EV. Springs LHB split -0.41, HR risk 0.88. tough split lane (-0.41); limited recent HR events.""", blast="good"),
            row("Eduardo Valencia", "R", "N/A", 85, "", ["vs Springs"], """1 HR, 1 near-HR, 87.6 mph EV. Springs RHB split +1.23, HR risk 0.88. lighter EV form (87.6 mph).""", blast="good"),
            row("Dillon Dingler", "R", "N/A", 86, "", ["vs Springs"], """0 HR, 2 near-HR, 91.2 mph EV. Springs RHB split +1.23, HR risk 0.88.""", blast="good"),
        ],
    },
    {
        "title": "KC @ COL - Michael Wacha (R, KC) vs Tomoyuki Sugano 🧤 (R, COL)",
        "description": "Tail key data: Park boost +3% (stadium +20%, weather -17%). Wacha (HR risk 0.16, vs LHB -0.50, vs RHB +1.07). Sugano 🧤 (HR risk 1.29, vs LHB +1.18, vs RHB +0.74).",
        "rows": [
            row("Hunter Goodman", "R", "+304", 86, "🌕 💣 💎", ["vs Wacha"], """Worst Pickz Hidden Gem. 3 HR, 4 near-HR, 89.2 mph EV. Wacha RHB split +1.07, HR risk 0.16. weather carry headwind (-17%).""", blast="high"),
            row("Willi Castro", "S", "N/A", 85, "🌕 💣 💎", ["vs Wacha"], """Worst Pickz Hidden Gem. 3 HR, 5 near-HR, 88.5 mph EV. Wacha SHB→RHB split +1.07, HR risk 0.16. weather carry headwind (-17%).""", blast="high"),
            row("Mickey Moniak", "L", "+360", 69, "🌕 💣", ["vs Wacha"], """2 HR, 2 near-HR, 92.6 mph EV. Wacha LHB split -0.50, HR risk 0.16. tough split lane (-0.50); weather carry headwind (-17%).""", blast="high"),
            row("Carter Jensen", "L", "N/A", 91, "🌕 💣", ["vs Sugano"], """1 HR, 2 near-HR, 95.1 mph EV. Sugano LHB split +1.18, HR risk 1.29. weather carry headwind (-17%).""", blast="good"),
            row("Salvador Perez", "R", "N/A", 81, "", ["vs Sugano"], """1 HR, 2 near-HR, 87.4 mph EV. Sugano RHB split +0.74, HR risk 1.29. weather carry headwind (-17%); lighter EV form (87.4 mph).""", blast="good"),
            row("Starling Marte", "R", "N/A", 80, "", ["vs Sugano"], """0 HR, 94.0 mph EV. Sugano RHB split +0.74, HR risk 1.29. weather carry headwind (-17%); limited recent HR events.""", blast="good"),
            row("John Rave", "L", "N/A", 90, "🌕 💣", ["vs Sugano"], """1 HR, 3 near-HR, 88.8 mph EV. Sugano LHB split +1.18, HR risk 1.29. weather carry headwind (-17%).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ NYM - Janson Junk (R, MIA) vs Freddy Peralta (R, NYM)",
        "description": "Tail key data: Park boost +10% (stadium -2%, weather +12%). Junk (HR risk 0.15, vs LHB -0.13, vs RHB +0.33). Peralta (HR risk -0.03, vs LHB -0.19, vs RHB +0.19).",
        "rows": [
            row("Brett Baty", "L", "N/A", 74, "⭐ 🌕 💣", ["vs Junk"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.2 mph EV. Junk LHB split -0.13, HR risk 0.15. slight split headwind (-0.13).""", blast="high"),
            row("Francisco Alvarez", "R", "N/A", 76, "🌕 💣", ["vs Junk"], """2 HR, 2 near-HR, 91.2 mph EV. Junk RHB split +0.33, HR risk 0.15.""", blast="high"),
            row("Joe Mack", "L", "N/A", 83, "🌕 💣", ["vs Peralta"], """3 HR, 3 near-HR, 96.5 mph EV. Peralta LHB split -0.19, HR risk -0.03. slight split headwind (-0.19); pitcher risk below avg (-0.03).""", blast="high"),
            row("Griffin Conine", "L", "N/A", 82, "🌕 💣", ["vs Peralta"], """4 HR, 4 near-HR, 95.3 mph EV. Peralta LHB split -0.19, HR risk -0.03. slight split headwind (-0.19); pitcher risk below avg (-0.03).""", blast="high"),
            row("Kyle Stowers", "L", "N/A", 67, "⭐", ["vs Peralta"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.5 mph EV. Peralta LHB split -0.19, HR risk -0.03. slight split headwind (-0.19); pitcher risk below avg (-0.03).""", blast="good"),
            row("Heriberto Hernandez", "R", "N/A", 65, "", ["vs Peralta"], """0 HR, 3 near-HR, 90.9 mph EV. Peralta RHB split +0.19, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ LAA - Shane Drohan (L, MIL) vs Ryan Johnson 🧤 (R, LAA)",
        "description": "Tail key data: Park boost +0% (stadium -8%, weather +8%). Drohan (HR risk -0.64, vs LHB -0.71, vs RHB -0.32). Johnson 🧤 (HR risk 0.96, vs LHB +0.90, vs RHB +0.48).",
        "rows": [
            row("Zach Neto", "R", "N/A", 58, "", ["vs Drohan"], """0 HR, 91.6 mph EV. Drohan RHB split -0.32, HR risk -0.64. slight split headwind (-0.32); pitcher suppresses HR (-0.64)."""),
            row("Travis d'Arnaud", "R", "N/A", 58, "", ["vs Drohan"], """1 HR, 1 near-HR, 92.0 mph EV. Drohan RHB split -0.32, HR risk -0.64. slight split headwind (-0.32); pitcher suppresses HR (-0.64).""", blast="good"),
            row("Jo Adell", "R", "N/A", 68, "🌕 💣 💎", ["vs Drohan"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 90.5 mph EV. Drohan RHB split -0.32, HR risk -0.64. slight split headwind (-0.32); pitcher suppresses HR (-0.64).""", blast="high"),
            row("Jake Bauers", "L", "N/A", 94, "🚀 🌕 💣 💎", ["vs Johnson"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 100.7 mph EV. Johnson LHB split +0.90, HR risk 0.96. park suppresses carry (-8%).""", blast="high"),
            row("Andrew Vaughn", "R", "N/A", 75, "", ["vs Johnson"], """0 HR, 94.3 mph EV. Johnson RHB split +0.48, HR risk 0.96. park suppresses carry (-8%); limited recent HR events.""", blast="good"),
            row("Christian Yelich", "L", "N/A", 85, "", ["vs Johnson"], """1 HR, 2 near-HR, 93.7 mph EV. Johnson LHB split +0.90, HR risk 0.96. park suppresses carry (-8%).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ SEA - Zebby Matthews (R, MIN) vs Bryce Miller (R, SEA)",
        "description": "Tail key data: Park boost -4% (stadium +1%, weather -5%). Matthews (HR risk 0.73, vs LHB +0.13, vs RHB +0.78). Miller (HR risk 0.20, vs LHB +0.00, vs RHB +0.34).",
        "rows": [
            row("Luke Raley", "L", "N/A", 74, "", ["vs Matthews"], """1 HR, 1 near-HR, 95.6 mph EV. Matthews LHB split +0.13, HR risk 0.73. weather carry headwind (-5%).""", blast="good"),
            row("Randy Arozarena", "R", "N/A", 79, "", ["vs Matthews"], """1 HR, 1 near-HR, 96.5 mph EV. Matthews RHB split +0.78, HR risk 0.73. weather carry headwind (-5%).""", blast="good"),
            row("Mitch Garver", "R", "N/A", 74, "", ["vs Matthews"], """1 HR, 1 near-HR, 90.4 mph EV. Matthews RHB split +0.78, HR risk 0.73. weather carry headwind (-5%).""", blast="good"),
            row("Rob Refsnyder", "R", "N/A", 74, "💎", ["vs Matthews"], """Worst Pickz Hidden Gem. 0 HR, 96.7 mph EV. Matthews RHB split +0.78, HR risk 0.73. weather carry headwind (-5%); limited recent HR events.""", blast="good"),
            row("Kody Clemens", "L", "N/A", 67, "⭐", ["vs Miller"], """Worst Pickz Favorite. 0 HR, 3 near-HR, 96.7 mph EV. Miller LHB split +0.00, HR risk 0.20. weather carry headwind (-5%).""", blast="good"),
            row("Ryan Jeffers", "R", "N/A", 68, "", ["vs Miller"], """1 HR, 2 near-HR, 94.7 mph EV. Miller RHB split +0.34, HR risk 0.20. weather carry headwind (-5%).""", blast="good"),
            row("Royce Lewis", "R", "N/A", 63, "💎", ["vs Miller"], """Worst Pickz Hidden Gem. 0 HR, 98.2 mph EV. Miller RHB split +0.34, HR risk 0.20. weather carry headwind (-5%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "NYY @ CHC - Will Warren 🧤 (R, NYY) vs Shota Imanaga (L, CHC)",
        "description": "Tail key data: Park boost +24% (stadium +0%, weather +24%). Warren 🧤 (HR risk 1.00, vs LHB +0.90, vs RHB +0.33). Imanaga (HR risk -0.37, vs LHB +0.21, vs RHB -0.36).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "N/A", 93, "⭐ 🌕 💣", ["vs Warren"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 98.0 mph EV. Warren LHB split +0.90, HR risk 1.00.""", blast="good"),
            row("Miguel Amaya", "R", "N/A", 81, "", ["vs Warren"], """0 HR, 1 near-HR, 93.6 mph EV. Warren RHB split +0.33, HR risk 1.00. limited recent HR events.""", blast="good"),
            row("Justin Dean", "R", "N/A", 82, "", ["vs Warren"], """0 HR, 96.8 mph EV. Warren RHB split +0.33, HR risk 1.00. limited recent HR events.""", blast="good"),
            row("Ben Rice", "L", "N/A", 78, "🌕 💣", ["vs Imanaga"], """2 HR, 2 near-HR, 95.8 mph EV. Imanaga LHB split +0.21, HR risk -0.37. pitcher risk below avg (-0.37).""", blast="high"),
            row("Spencer Jones", "L", "N/A", 63, "", ["vs Imanaga"], """0 HR, 97.4 mph EV. Imanaga LHB split +0.21, HR risk -0.37. pitcher risk below avg (-0.37); limited recent HR events.""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "N/A", 62, "", ["vs Imanaga"], """1 HR, 1 near-HR, 89.6 mph EV. Imanaga LHB split +0.21, HR risk -0.37. pitcher risk below avg (-0.37).""", blast="good"),
            row("Austin Wells", "L", "N/A", 61, "", ["vs Imanaga"], """1 HR, 1 near-HR, 88.4 mph EV. Imanaga LHB split +0.21, HR risk -0.37. pitcher risk below avg (-0.37).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ BAL - Brian Keller (R, PHI) vs Brandon Young (R, BAL)",
        "description": "Tail key data: Park boost -2% (stadium -2%, weather -1%). Keller (HR risk 0.45, vs LHB +0.35, vs RHB +0.55). Young (HR risk -0.49, vs LHB -0.13, vs RHB -0.84).",
        "rows": [
            row("Gunnar Henderson", "L", "N/A", 70, "💎", ["vs Keller"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.2 mph EV. Keller LHB split +0.35, HR risk 0.45. limited recent HR events.""", blast="good"),
            row("Dylan Beavers", "L", "N/A", 67, "", ["vs Keller"], """0 HR, 94.8 mph EV. Keller LHB split +0.35, HR risk 0.45. limited recent HR events.""", blast="good"),
            row("Coby Mayo", "R", "N/A", 74, "💎", ["vs Keller"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.1 mph EV. Keller RHB split +0.55, HR risk 0.45.""", blast="good"),
            row("Tyler O'Neill", "R", "N/A", 66, "", ["vs Keller"], """0 HR, 92.5 mph EV. Keller RHB split +0.55, HR risk 0.45. limited recent HR events.""", blast="good"),
            row("Bryce Harper", "L", "N/A", 58, "", ["vs Young"], """1 HR, 1 near-HR, 95.2 mph EV. Young LHB split -0.13, HR risk -0.49. slight split headwind (-0.13); pitcher suppresses HR (-0.49).""", blast="good"),
            row("Derek Hill", "R", "N/A", 64, "🌕 💣 💎", ["vs Young"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.0 mph EV. Young RHB split -0.84, HR risk -0.49. tough split lane (-0.84); pitcher suppresses HR (-0.49).""", blast="high"),
            row("Trea Turner", "R", "N/A", 62, "🌕 💣", ["vs Young"], """2 HR, 2 near-HR, 93.6 mph EV. Young RHB split -0.84, HR risk -0.49. tough split lane (-0.84); pitcher suppresses HR (-0.49).""", blast="high"),
        ],
    },
    {
        "title": "PIT @ CIN - Paul Skenes (R, PIT) vs Hunter Greene (R, CIN)",
        "description": "Tail key data: Park boost +14% (stadium +14%, weather +0%). Skenes (HR risk -0.71, vs LHB -0.54, vs RHB -0.62). Greene (HR risk -0.03, vs LHB -0.40, vs RHB +0.46).",
        "rows": [
            row("Elly De La Cruz", "S", "N/A", 58, "⭐", ["vs Skenes"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 90.8 mph EV. Skenes SHB→LHB split -0.54, HR risk -0.71. tough split lane (-0.54); pitcher suppresses HR (-0.71).""", blast="good"),
            row("Matt McLain", "R", "N/A", 58, "", ["vs Skenes"], """0 HR, 92.8 mph EV. Skenes RHB split -0.62, HR risk -0.71. tough split lane (-0.62); pitcher suppresses HR (-0.71).""", blast="good"),
            row("Eugenio Suarez", "R", "N/A", 58, "", ["vs Skenes"], """1 HR, 1 near-HR, 92.9 mph EV. Skenes RHB split -0.62, HR risk -0.71. tough split lane (-0.62); pitcher suppresses HR (-0.71).""", blast="good"),
            row("Bryan Reynolds", "S", "N/A", 81, "⭐ 🌕 💣", ["vs Greene"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.9 mph EV. Greene SHB→RHB split +0.46, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="high"),
            row("Esmerlyn Valdez", "R", "N/A", 69, "", ["vs Greene"], """1 HR, 1 near-HR, 93.5 mph EV. Greene RHB split +0.46, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="good"),
            row("Endy Rodriguez", "S", "N/A", 71, "", ["vs Greene"], """1 HR, 1 near-HR, 97.0 mph EV. Greene SHB→RHB split +0.46, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="good"),
            row("Brandon Lowe", "L", "N/A", 58, "", ["vs Greene"], """0 HR, 1 near-HR, 93.9 mph EV. Greene LHB split -0.40, HR risk -0.03. tough split lane (-0.40); pitcher risk below avg (-0.03).""", blast="good"),
        ],
    },
    {
        "title": "SF @ SD - Carson Whisenhunt (L, SF) vs German Marquez (R, SD)",
        "description": "Tail key data: Park boost +0% (stadium -5%, weather +5%). Whisenhunt (HR risk 0.55, vs LHB +0.30, vs RHB +0.70). Marquez (HR risk 0.70, vs LHB +0.50, vs RHB +0.85).",
        "rows": [
            row("Manny Machado", "R", "N/A", 83, "💎", ["vs Whisenhunt"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 94.6 mph EV. Whisenhunt RHB split +0.70, HR risk 0.55.""", blast="good"),
            row("Fernando Tatis Jr.", "R", "N/A", 84, "🌕 💣", ["vs Whisenhunt"], """2 HR, 2 near-HR, 92.5 mph EV. Whisenhunt RHB split +0.70, HR risk 0.55.""", blast="high"),
            row("Ty France", "R", "N/A", 72, "", ["vs Whisenhunt"], """0 HR, 95.8 mph EV. Whisenhunt RHB split +0.70, HR risk 0.55. limited recent HR events.""", blast="good"),
            row("Jackson Merrill", "L", "N/A", 69, "", ["vs Whisenhunt"], """0 HR, 96.8 mph EV. Whisenhunt LHB split +0.30, HR risk 0.55. limited recent HR events.""", blast="good"),
            row("Drew Gilbert", "L", "N/A", 74, "", ["vs Marquez"], """0 HR, 1 near-HR, 96.5 mph EV. Marquez LHB split +0.50, HR risk 0.70. limited recent HR events.""", blast="good"),
            row("Rafael Devers", "L", "N/A", 83, "🌕 💣", ["vs Marquez"], """2 HR, 2 near-HR, 91.6 mph EV. Marquez LHB split +0.50, HR risk 0.70.""", blast="high"),
            row("Bryce Eldridge", "L", "N/A", 90, "🌕 💣", ["vs Marquez"], """2 HR, 3 near-HR, 93.8 mph EV. Marquez LHB split +0.50, HR risk 0.70.""", blast="high"),
            row("Grant McCray", "L", "N/A", 68, "", ["vs Marquez"], """1 HR, 1 near-HR, 83.1 mph EV. Marquez LHB split +0.50, HR risk 0.70. lighter EV form (83.1 mph).""", blast="good"),
        ],
    },
    {
        "title": "STL @ TOR - Kyle Leahy (R, STL) vs Dylan Cease (R, TOR)",
        "description": "Tail key data: Park boost +19% (stadium +6%, weather +12%). Leahy (HR risk -0.01, vs LHB +0.10, vs RHB -0.17). Cease (HR risk -1.02, vs LHB -0.44, vs RHB -1.35).",
        "rows": [
            row("George Springer", "R", "N/A", 75, "🌕 💣 💎", ["vs Leahy"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.0 mph EV. Leahy RHB split -0.17, HR risk -0.01. slight split headwind (-0.17); pitcher risk below avg (-0.01).""", blast="high"),
            row("Brandon Valenzuela", "S", "N/A", 61, "", ["vs Leahy"], """1 HR, 2 near-HR, 82.0 mph EV. Leahy SHB→LHB split +0.10, HR risk -0.01. pitcher risk below avg (-0.01); lighter EV form (82.0 mph).""", blast="good"),
            row("Jimmy Crooks", "L", "N/A", 58, "💎", ["vs Cease"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 99.0 mph EV. Cease LHB split -0.44, HR risk -1.02. tough split lane (-0.44); pitcher suppresses HR (-1.02).""", blast="good"),
            row("Alec Burleson", "L", "N/A", 58, "", ["vs Cease"], """0 HR, 1 near-HR, 97.4 mph EV. Cease LHB split -0.44, HR risk -1.02. tough split lane (-0.44); pitcher suppresses HR (-1.02).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ HOU - Nathan Eovaldi (R, TEX) vs Hunter Brown (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +5%, weather -1%). Eovaldi (HR risk 0.18, vs LHB -0.25, vs RHB +0.68). Brown (HR risk -0.48, vs LHB -0.08, vs RHB -0.86).",
        "rows": [
            row("Yordan Alvarez", "L", "N/A", 75, "🌕 💣", ["vs Eovaldi"], """2 HR, 2 near-HR, 96.5 mph EV. Eovaldi LHB split -0.25, HR risk 0.18. slight split headwind (-0.25).""", blast="high"),
            row("Taylor Trammell", "L", "N/A", 74, "🌕 💣 💎", ["vs Eovaldi"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 90.8 mph EV. Eovaldi LHB split -0.25, HR risk 0.18. slight split headwind (-0.25).""", blast="high"),
            row("Joc Pederson", "L", "N/A", 58, "", ["vs Brown"], """1 HR, 1 near-HR, 93.2 mph EV. Brown LHB split -0.08, HR risk -0.48. slight split headwind (-0.08); pitcher suppresses HR (-0.48).""", blast="good"),
            row("Wyatt Langford", "R", "N/A", 58, "", ["vs Brown"], """0 HR, 95.8 mph EV. Brown RHB split -0.86, HR risk -0.48. tough split lane (-0.86); pitcher suppresses HR (-0.48).""", blast="good"),
            row("Alejandro Osuna", "L", "N/A", 58, "", ["vs Brown"], """1 HR, 1 near-HR, 87.2 mph EV. Brown LHB split -0.08, HR risk -0.48. slight split headwind (-0.08); pitcher suppresses HR (-0.48).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ ATL - Foster Griffin (L, WSH) vs Bryce Elder 🧤 (R, ATL)",
        "description": "Tail key data: Park boost +11% (stadium -2%, weather +13%). Griffin (HR risk -1.00, vs LHB -0.71, vs RHB -0.68). Elder 🧤 (HR risk 1.24, vs LHB +0.62, vs RHB +1.36).",
        "rows": [
            row("Austin Riley", "R", "+425", 58, "🌕 💣", ["vs Griffin"], """2 HR, 2 near-HR, 91.4 mph EV. Griffin RHB split -0.68, HR risk -1.00. tough split lane (-0.68); pitcher suppresses HR (-1.00).""", blast="high"),
            row("Matt Olson", "L", "+240", 58, "", ["vs Griffin"], """1 HR, 1 near-HR, 95.0 mph EV. Griffin LHB split -0.71, HR risk -1.00. tough split lane (-0.71); pitcher suppresses HR (-1.00).""", blast="good"),
            row("Ozzie Albies", "S", "+414", 58, "", ["vs Griffin"], """1 HR, 1 near-HR, 82.1 mph EV. Griffin SHB→RHB split -0.68, HR risk -1.00. tough split lane (-0.68); pitcher suppresses HR (-1.00).""", blast="good"),
            row("Luis Garcia Jr.", "L", "N/A", 90, "⭐ 🌕 💣", ["vs Elder"], """Worst Pickz Favorite. 0 HR, 3 near-HR, 98.0 mph EV. Elder LHB split +0.62, HR risk 1.24.""", blast="good"),
            row("James Wood", "L", "N/A", 88, "🌕 💣", ["vs Elder"], """1 HR, 1 near-HR, 97.0 mph EV. Elder LHB split +0.62, HR risk 1.24.""", blast="good"),
            row("Daylen Lile", "L", "N/A", 83, "", ["vs Elder"], """1 HR, 1 near-HR, 90.3 mph EV. Elder LHB split +0.62, HR risk 1.24.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-31")

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

    out = ROOT / '_games-0731.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
