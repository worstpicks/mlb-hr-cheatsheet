#!/usr/bin/env python3
"""Generate games[] block for 2026-06-15 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Bobby Witt Jr. (R)",
    "Byron Buxton (R)",
    "Fernando Tatis Jr. (R)",
    "Francisco Alvarez (R)",
    "Heriberto Hernandez (R)",
    "Kyle Schwarber (L)",
    "Logan O'Hoppe (R)",
    "Matt McLain (R)",
    "Max Muncy (L)",
    "Michael Busch (L)",
    "Riley Greene (L)",
    "Seiya Suzuki (R)",
    "Tyler Callihan (L)",
}

GEMS = {
    "Bryce Harper (L)",
    "Endy Rodriguez (S)",
    "Jacob Young (R)",
    "Juan Soto (L)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Andy Pages (R)": "LAD",
    "Ben Williamson (R)": "TB",
    "Bo Bichette (R)": "NYM",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "Cam Smith (R)": "HOU",
    "Christian Walker (R)": "HOU",
    "Colt Keith (L)": "DET",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Dane Myers (R)": "CIN",
    "Dillon Dingler (R)": "DET",
    "Donovan Walton (L)": "LAA",
    "Endy Rodriguez (S)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Freddie Freeman (L)": "LAD",
    "Gabriel Moreno (R)": "ARI",
    "Gleyber Torres (R)": "DET",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Isaac Paredes (R)": "HOU",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jacob Young (R)": "WSH",
    "James Wood (L)": "WSH",
    "Joe Mack (L)": "MIA",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Ketel Marte (S)": "ARI",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Lars Nootbaar (L)": "STL",
    "Logan O'Hoppe (R)": "LAA",
    "Maikel Garcia (R)": "KC",
    "Matt McLain (R)": "CIN",
    "Max Muncy (L)": "LAD",
    "Michael Busch (L)": "CHC",
    "Mike Trout (R)": "LAA",
    "Owen Caissie (L)": "MIA",
    "Pete Crow-Armstrong (L)": "CHC",
    "Riley Greene (L)": "DET",
    "Royce Lewis (R)": "MIN",
    "Ryan Vilade (R)": "TB",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Seiya Suzuki (R)": "CHC",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Tyler Callihan (L)": "PIT",
    "Xander Bogaerts (R)": "SD",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_RISK_MIN = 0.95

BUM_PITCHERS = {
    "Imanaga",
    "Lauer",
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
        "title": "COL @ CHC - Michael Lorenzen (R, COL) vs Shota Imanaga 🧤 (L, CHC)",
        "description": "Tail key data: Park boost +13% (stadium -1%, weather +14%). Lorenzen (HR risk 0.31, vs LHB +0.27, vs RHB +0.14). Imanaga 🧤 (HR risk 1.65, vs LHB +0.67, vs RHB +1.70).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+289", 64, "", ["vs Lorenzen"], """0 HR, 1 near-HR, 85.7 mph EV. Lorenzen LHB split +0.27, HR risk 0.31. limited recent HR events; lighter EV form (85.7 mph)."""),
            row("Michael Busch", "L", "+322", 78, "⭐", ["vs Lorenzen"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 92.3 mph EV. Lorenzen LHB split +0.27, HR risk 0.31.""", blast="good"),
            row("Ian Happ", "S", "+340", 72, "", ["vs Lorenzen"], """1 HR, 2 near-HR, 87.1 mph EV. Lorenzen RHB split +0.14, HR risk 0.31. lighter EV form (87.1 mph).""", blast="good"),
            row("Seiya Suzuki", "R", "+410", 83, "⭐ 🌕 💣", ["vs Lorenzen"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 91.4 mph EV. Lorenzen RHB split +0.14, HR risk 0.31.""", blast="high"),
            row("Kyle Karros", "R", "+710", 75, "", ["vs Imanaga"], """0 HR, 2 near-HR, 94.9 mph EV. Imanaga RHB split +1.70, HR risk 1.65.""", blast="good"),
            row("Hunter Goodman", "R", "+270", 70, "", ["vs Imanaga"], """1 HR, 1 near-HR, 84.4 mph EV. Imanaga RHB split +1.70, HR risk 1.65. lighter EV form (84.4 mph).""", blast="good"),
        ],
    },
    {
        "title": "DET @ HOU - Troy Melton (R, DET) vs Kai-Wei Teng (R, HOU)",
        "description": "Tail key data: Park boost +4% (stadium +4%, weather -1%). Melton (HR risk -0.11, vs LHB -0.19, vs RHB -0.08). Teng (HR risk -0.57, vs LHB -0.34, vs RHB -0.49).",
        "rows": [
            row("Cam Smith", "R", "+710", 76, "", ["vs Melton"], """0 HR, 1 near-HR, 98.4 mph EV. Melton RHB split -0.08, HR risk -0.11. slight split headwind (-0.08); pitcher risk below avg (-0.11).""", blast="good"),
            row("Yordan Alvarez", "L", "+286", 64, "", ["vs Melton"], """0 HR, 90.1 mph EV. Melton LHB split -0.19, HR risk -0.11. slight split headwind (-0.19); pitcher risk below avg (-0.11)."""),
            row("Isaac Paredes", "R", "+549", 83, "🌕 💣", ["vs Melton"], """2 HR, 2 near-HR, 93.0 mph EV. Melton RHB split -0.08, HR risk -0.11. slight split headwind (-0.08); pitcher risk below avg (-0.11).""", blast="high"),
            row("Christian Walker", "R", "+379", 80, "", ["vs Melton"], """1 HR, 2 near-HR, 95.7 mph EV. Melton RHB split -0.08, HR risk -0.11. slight split headwind (-0.08); pitcher risk below avg (-0.11).""", blast="good"),
            row("Riley Greene", "L", "+432", 90, "⭐ 🌕 💣", ["vs Teng"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 96.1 mph EV. Teng LHB split -0.34, HR risk -0.57. slight split headwind (-0.34); pitcher suppresses HR (-0.57).""", blast="high"),
            row("Dillon Dingler", "R", "+447", 73, "", ["vs Teng"], """0 HR, 2 near-HR, 92.8 mph EV. Teng RHB split -0.49, HR risk -0.57. tough split lane (-0.49); pitcher suppresses HR (-0.57).""", blast="good"),
            row("Colt Keith", "L", "+1060", 77, "", ["vs Teng"], """1 HR, 3 near-HR, 91.0 mph EV. Teng LHB split -0.34, HR risk -0.57. slight split headwind (-0.34); pitcher suppresses HR (-0.57).""", blast="good"),
            row("Gleyber Torres", "R", "+890", 77, "", ["vs Teng"], """1 HR, 1 near-HR, 94.8 mph EV. Teng RHB split -0.49, HR risk -0.57. tough split lane (-0.49); pitcher suppresses HR (-0.57).""", blast="good"),
        ],
    },
    {
        "title": "KC @ WSH - Mitch Spence (R, KC) vs Andrew Alvarez (L, WSH)",
        "description": "Tail key data: Park boost data unavailable. Spence (HR risk 0.56, vs LHB +1.84, vs RHB -0.51). Alvarez (HR risk -0.41, vs LHB -0.31, vs RHB -0.12).",
        "rows": [
            row("James Wood", "L", "+390", 78, "🌕 💣", ["vs Spence"], """2 HR, 2 near-HR, 88.5 mph EV. Spence LHB split +1.84, HR risk 0.56.""", blast="high"),
            row("Jacob Young", "R", "+1400", 66, "💎", ["vs Spence"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 89.7 mph EV. Spence RHB split -0.51, HR risk 0.56. tough split lane (-0.51); limited recent HR events."""),
            row("Salvador Perez", "R", "+496", 79, "", ["vs Alvarez"], """1 HR, 1 near-HR, 97.3 mph EV. Alvarez RHB split -0.12, HR risk -0.41. slight split headwind (-0.12); pitcher suppresses HR (-0.41).""", blast="good"),
            row("Jac Caglianone", "L", "+640", 72, "", ["vs Alvarez"], """1 HR, 2 near-HR, 81.1 mph EV. Alvarez LHB split -0.31, HR risk -0.41. slight split headwind (-0.31); pitcher suppresses HR (-0.41).""", blast="good"),
            row("Bobby Witt Jr.", "R", "+475", 74, "⭐", ["vs Alvarez"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.2 mph EV. Alvarez RHB split -0.12, HR risk -0.41. slight split headwind (-0.12); pitcher suppresses HR (-0.41).""", blast="good"),
            row("Maikel Garcia", "R", "+1160", 77, "", ["vs Alvarez"], """0 HR, 1 near-HR, 99.0 mph EV. Alvarez RHB split -0.12, HR risk -0.41. slight split headwind (-0.12); pitcher suppresses HR (-0.41).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ ARI - Walbert Urena (R, LAA) vs Ryne Nelson (R, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Urena (HR risk -1.06, vs LHB -1.20, vs RHB -0.25). Nelson (HR risk 0.73, vs LHB +0.34, vs RHB +0.63).",
        "rows": [
            row("Corbin Carroll", "L", "+518", 80, "🌕 💣", ["vs Urena"], """2 HR, 2 near-HR, 90.4 mph EV. Urena LHB split -1.20, HR risk -1.06. tough split lane (-1.20); pitcher suppresses HR (-1.06).""", blast="high"),
            row("Gabriel Moreno", "R", "+790", 88, "🌕 💣", ["vs Urena"], """3 HR, 4 near-HR, 90.0 mph EV. Urena RHB split -0.25, HR risk -1.06. slight split headwind (-0.25); pitcher suppresses HR (-1.06).""", blast="high"),
            row("Ketel Marte", "S", "+420", 64, "", ["vs Urena"], """0 HR, 1 near-HR, 88.2 mph EV. Urena RHB split -0.25, HR risk -1.06. slight split headwind (-0.25); pitcher suppresses HR (-1.06)."""),
            row("Logan O'Hoppe", "R", "+599", 82, "⭐ 🌕 💣", ["vs Nelson"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.1 mph EV. Nelson RHB split +0.63, HR risk 0.73. park/weather net drag (-8%).""", blast="high"),
            row("Donovan Walton", "L", "+1060", 66, "", ["vs Nelson"], """0 HR, 1 near-HR, 90.1 mph EV. Nelson LHB split +0.34, HR risk 0.73. park/weather net drag (-8%); limited recent HR events."""),
            row("Zach Neto", "R", "+470", 72, "", ["vs Nelson"], """1 HR, 1 near-HR, 90.0 mph EV. Nelson RHB split +0.63, HR risk 0.73. park/weather net drag (-8%).""", blast="good"),
            row("Mike Trout", "R", "+340", 82, "🚀", ["vs Nelson"], """1 HR, 1 near-HR, 101.1 mph EV. Nelson RHB split +0.63, HR risk 0.73. park/weather net drag (-8%).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ PHI - Ryan Gusto (R, MIA) vs Zack Wheeler (R, PHI)",
        "description": "Tail key data: Park boost +8% (stadium +16%, weather -8%). Gusto (HR risk -0.69, vs LHB -0.61, vs RHB -0.36). Wheeler (HR risk 0.02, vs LHB -0.10, vs RHB +0.04).",
        "rows": [
            row("Bryce Harper", "L", "+340", 78, "💎", ["vs Gusto"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.9 mph EV. Gusto LHB split -0.61, HR risk -0.69. tough split lane (-0.61); pitcher suppresses HR (-0.69).""", blast="good"),
            row("Kyle Schwarber", "L", "+225", 81, "⭐", ["vs Gusto"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.3 mph EV. Gusto LHB split -0.61, HR risk -0.69. tough split lane (-0.61); pitcher suppresses HR (-0.69).""", blast="good"),
            row("Heriberto Hernandez", "R", "+920", 85, "⭐ 🌕 💣", ["vs Wheeler"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.6 mph EV. Wheeler RHB split +0.04, HR risk 0.02. weather carry headwind (-8%).""", blast="high"),
            row("Owen Caissie", "L", "+850", 73, "", ["vs Wheeler"], """0 HR, 1 near-HR, 94.7 mph EV. Wheeler LHB split -0.10, HR risk 0.02. slight split headwind (-0.10); weather carry headwind (-8%).""", blast="good"),
            row("Joe Mack", "L", "+1040", 63, "", ["vs Wheeler"], """0 HR, 89.4 mph EV. Wheeler LHB split -0.10, HR risk 0.02. slight split headwind (-0.10); weather carry headwind (-8%)."""),
        ],
    },
    {
        "title": "MIN @ TEX - Mike Paredes (R, MIN) vs MacKenzie Gore (L, TEX)",
        "description": "Tail key data: Park boost -12% (stadium -12%, weather -1%). Away starter risk unavailable. Gore (HR risk -0.75, vs LHB -0.62, vs RHB -0.38).",
        "rows": [
            row("Brandon Nimmo", "L", "+420", 70, "", ["vs Paredes"], """0 HR, 94.4 mph EV. Paredes split/risk data unavailable. limited split/risk sample; park/weather net drag (-12%).""", blast="good"),
            row("Corey Seager", "L", "N/A", 74, "", ["vs Paredes"], """1 HR, 2 near-HR, 90.1 mph EV. Paredes split/risk data unavailable. limited split/risk sample; park/weather net drag (-12%).""", blast="good"),
            row("Byron Buxton", "R", "+381", 90, "⭐ 🌕 💣", ["vs Gore"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 98.2 mph EV. Gore RHB split -0.38, HR risk -0.75. slight split headwind (-0.38); pitcher suppresses HR (-0.75).""", blast="high"),
            row("Royce Lewis", "R", "+640", 70, "", ["vs Gore"], """1 HR, 1 near-HR, 85.9 mph EV. Gore RHB split -0.38, HR risk -0.75. slight split headwind (-0.38); pitcher suppresses HR (-0.75).""", blast="good"),
        ],
    },
    {
        "title": "NYM @ CIN - Tobias Myers (R, NYM) vs Chase Burns (R, CIN)",
        "description": "Tail key data: Park boost +10% (stadium +12%, weather -2%). Myers (HR risk 0.37, vs LHB +0.11, vs RHB +0.11). Burns (HR risk 0.02, vs LHB -0.14, vs RHB +0.02).",
        "rows": [
            row("Matt McLain", "R", "+554", 75, "⭐", ["vs Myers"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.7 mph EV. Myers RHB split +0.11, HR risk 0.37. limited recent HR events.""", blast="good"),
            row("Sal Stewart", "R", "+378", 73, "", ["vs Myers"], """0 HR, 2 near-HR, 93.1 mph EV. Myers RHB split +0.11, HR risk 0.37.""", blast="good"),
            row("Dane Myers", "R", "+610", 72, "", ["vs Myers"], """0 HR, 1 near-HR, 94.4 mph EV. Myers RHB split +0.11, HR risk 0.37. limited recent HR events.""", blast="good"),
            row("Eugenio Suarez", "R", "+340", 75, "", ["vs Myers"], """1 HR, 1 near-HR, 93.1 mph EV. Myers RHB split +0.11, HR risk 0.37.""", blast="good"),
            row("Bo Bichette", "R", "+660", 81, "🌕 💣", ["vs Burns"], """2 HR, 2 near-HR, 91.3 mph EV. Burns RHB split +0.02, HR risk 0.02.""", blast="high"),
            row("Francisco Alvarez", "R", "+479", 79, "⭐", ["vs Burns"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.0 mph EV. Burns RHB split +0.02, HR risk 0.02.""", blast="good"),
            row("Juan Soto", "L", "+340", 75, "💎", ["vs Burns"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 91.1 mph EV. Burns LHB split -0.14, HR risk 0.02. slight split headwind (-0.14).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ ATH - Jared Jones (R, PIT) vs J.T. Ginn (R, ATH)",
        "description": "Tail key data: Park boost +38% (stadium +32%, weather +6%). Jones (HR risk 0.43, vs LHB +1.29, vs RHB -1.21). Ginn (HR risk -0.35, vs LHB -0.49, vs RHB +0.03).",
        "rows": [
            row("Henry Bolte", "R", "+775", 76, "🚀", ["vs Jones"], """0 HR, 103.4 mph EV. Jones RHB split -1.21, HR risk 0.43. tough split lane (-1.21); limited recent HR events.""", blast="good"),
            row("Shea Langeliers", "R", "+265", 73, "", ["vs Jones"], """1 HR, 1 near-HR, 91.4 mph EV. Jones RHB split -1.21, HR risk 0.43. tough split lane (-1.21).""", blast="good"),
            row("Tyler Callihan", "L", "+523", 86, "⭐ 🌕 💣", ["vs Ginn"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.1 mph EV. Ginn LHB split -0.49, HR risk -0.35. tough split lane (-0.49); pitcher risk below avg (-0.35).""", blast="high"),
            row("Endy Rodriguez", "S", "+610", 85, "🌕 💣 💎", ["vs Ginn"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 95.2 mph EV. Ginn RHB split +0.03, HR risk -0.35. pitcher risk below avg (-0.35).""", blast="high"),
            row("Brandon Lowe", "L", "+340", 85, "🌕 💣", ["vs Ginn"], """2 HR, 3 near-HR, 92.7 mph EV. Ginn LHB split -0.49, HR risk -0.35. tough split lane (-0.49); pitcher risk below avg (-0.35).""", blast="high"),
        ],
    },
    {
        "title": "SD @ STL - Lucas Giolito (R, SD) vs Dustin May (R, STL)",
        "description": "Tail key data: Park boost -8% (stadium -9%, weather +1%). Away starter risk unavailable. May (HR risk -0.62, vs LHB -0.67, vs RHB -0.31).",
        "rows": [
            row("Alec Burleson", "L", "+475", 86, "⭐ 🌕 💣", ["vs Giolito"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.2 mph EV. Giolito split/risk data unavailable. limited split/risk sample; park/weather net drag (-8%).""", blast="high"),
            row("Lars Nootbaar", "L", "+650", 78, "", ["vs Giolito"], """1 HR, 2 near-HR, 93.9 mph EV. Giolito split/risk data unavailable. limited split/risk sample; park/weather net drag (-8%).""", blast="good"),
            row("JJ Wetherholt", "L", "+570", 77, "", ["vs Giolito"], """1 HR, 2 near-HR, 93.0 mph EV. Giolito split/risk data unavailable. limited split/risk sample; park/weather net drag (-8%).""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+600", 74, "⭐", ["vs May"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.0 mph EV. May RHB split -0.31, HR risk -0.62. slight split headwind (-0.31); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Xander Bogaerts", "R", "+980", 72, "", ["vs May"], """0 HR, 1 near-HR, 93.5 mph EV. May RHB split -0.31, HR risk -0.62. slight split headwind (-0.31); pitcher suppresses HR (-0.62).""", blast="good"),
        ],
    },
    {
        "title": "TB @ LAD - Nick Martinez (R, TB) vs Eric Lauer 🧤 (L, LAD)",
        "description": "Tail key data: Park boost +14% (stadium +18%, weather -4%). Martinez (HR risk -0.65, vs LHB -0.65, vs RHB -0.12). Lauer 🧤 (HR risk 1.12, vs LHB +0.81, vs RHB +1.14).",
        "rows": [
            row("Max Muncy", "L", "+300", 70, "⭐", ["vs Martinez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 87.6 mph EV. Martinez LHB split -0.65, HR risk -0.65. tough split lane (-0.65); pitcher suppresses HR (-0.65).""", blast="good"),
            row("Freddie Freeman", "L", "+443", 70, "", ["vs Martinez"], """1 HR, 1 near-HR, 87.1 mph EV. Martinez LHB split -0.65, HR risk -0.65. tough split lane (-0.65); pitcher suppresses HR (-0.65).""", blast="good"),
            row("Shohei Ohtani", "L", "+229", 80, "", ["vs Martinez"], """1 HR, 2 near-HR, 96.2 mph EV. Martinez LHB split -0.65, HR risk -0.65. tough split lane (-0.65); pitcher suppresses HR (-0.65).""", blast="good"),
            row("Andy Pages", "R", "+394", 82, "🌕 💣", ["vs Martinez"], """2 HR, 2 near-HR, 91.8 mph EV. Martinez RHB split -0.12, HR risk -0.65. slight split headwind (-0.12); pitcher suppresses HR (-0.65).""", blast="high"),
            row("Yandy Diaz", "R", "+365", 70, "", ["vs Lauer"], """1 HR, 1 near-HR, 88.0 mph EV. Lauer RHB split +1.14, HR risk 1.12. weather carry headwind (-4%).""", blast="good"),
            row("Junior Caminero", "R", "+240", 73, "", ["vs Lauer"], """0 HR, 96.8 mph EV. Lauer RHB split +1.14, HR risk 1.12. weather carry headwind (-4%); limited recent HR events.""", blast="good"),
            row("Ben Williamson", "R", "+1120", 75, "", ["vs Lauer"], """1 HR, 2 near-HR, 91.2 mph EV. Lauer RHB split +1.14, HR risk 1.12. weather carry headwind (-4%).""", blast="good"),
            row("Ryan Vilade", "R", "+640", 62, "", ["vs Lauer"], """0 HR, 86.7 mph EV. Lauer RHB split +1.14, HR risk 1.12. weather carry headwind (-4%); limited recent HR events."""),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-15")

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

    out = ROOT / '_games-0614.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
