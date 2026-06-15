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
        "description": "Tail key data: Park boost +18% (stadium -1%, weather +19%). Lorenzen (HR risk 0.36, vs LHB +0.33, vs RHB +0.17). Imanaga 🧤 (HR risk 1.66, vs LHB +0.72, vs RHB +1.69).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+289", 64, "", ["vs Lorenzen"], """0 HR, 1 near-HR, 85.7 mph EV. Lorenzen LHB split +0.33, HR risk 0.36. limited recent HR events; lighter EV form (85.7 mph)."""),
            row("Michael Busch", "L", "+322", 78, "⭐", ["vs Lorenzen"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 92.3 mph EV. Lorenzen LHB split +0.33, HR risk 0.36.""", blast="good"),
            row("Ian Happ", "S", "+340", 72, "", ["vs Lorenzen"], """1 HR, 2 near-HR, 87.1 mph EV. Lorenzen RHB split +0.17, HR risk 0.36. lighter EV form (87.1 mph).""", blast="good"),
            row("Seiya Suzuki", "R", "+410", 83, "⭐ 🌕 💣", ["vs Lorenzen"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 91.4 mph EV. Lorenzen RHB split +0.17, HR risk 0.36.""", blast="high"),
            row("Kyle Karros", "R", "+710", 75, "", ["vs Imanaga"], """0 HR, 2 near-HR, 94.9 mph EV. Imanaga RHB split +1.69, HR risk 1.66.""", blast="good"),
            row("Hunter Goodman", "R", "+270", 70, "", ["vs Imanaga"], """1 HR, 1 near-HR, 84.4 mph EV. Imanaga RHB split +1.69, HR risk 1.66. lighter EV form (84.4 mph).""", blast="good"),
        ],
    },
    {
        "title": "DET @ HOU - Troy Melton (R, DET) vs Kai-Wei Teng (R, HOU)",
        "description": "Tail key data: Park boost +4% (stadium +4%, weather -1%). Melton (HR risk -0.00, vs LHB -0.11, vs RHB -0.05). Teng (HR risk -0.42, vs LHB -0.25, vs RHB -0.44).",
        "rows": [
            row("Cam Smith", "R", "+710", 76, "", ["vs Melton"], """0 HR, 1 near-HR, 98.4 mph EV. Melton RHB split -0.05, HR risk -0.00. slight split headwind (-0.05); limited recent HR events.""", blast="good"),
            row("Yordan Alvarez", "L", "+286", 64, "", ["vs Melton"], """0 HR, 90.1 mph EV. Melton LHB split -0.11, HR risk -0.00. slight split headwind (-0.11); limited recent HR events."""),
            row("Isaac Paredes", "R", "+549", 83, "🌕 💣", ["vs Melton"], """2 HR, 2 near-HR, 93.0 mph EV. Melton RHB split -0.05, HR risk -0.00. slight split headwind (-0.05).""", blast="high"),
            row("Christian Walker", "R", "+379", 80, "", ["vs Melton"], """1 HR, 2 near-HR, 95.7 mph EV. Melton RHB split -0.05, HR risk -0.00. slight split headwind (-0.05).""", blast="good"),
            row("Riley Greene", "L", "+432", 90, "⭐ 🌕 💣", ["vs Teng"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 96.1 mph EV. Teng LHB split -0.25, HR risk -0.42. slight split headwind (-0.25); pitcher suppresses HR (-0.42).""", blast="high"),
            row("Dillon Dingler", "R", "+447", 73, "", ["vs Teng"], """0 HR, 2 near-HR, 92.8 mph EV. Teng RHB split -0.44, HR risk -0.42. tough split lane (-0.44); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Colt Keith", "L", "+1060", 77, "", ["vs Teng"], """1 HR, 3 near-HR, 91.0 mph EV. Teng LHB split -0.25, HR risk -0.42. slight split headwind (-0.25); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Gleyber Torres", "R", "+890", 77, "", ["vs Teng"], """1 HR, 1 near-HR, 94.8 mph EV. Teng RHB split -0.44, HR risk -0.42. tough split lane (-0.44); pitcher suppresses HR (-0.42).""", blast="good"),
        ],
    },
    {
        "title": "KC @ WSH - Mitch Spence (R, KC) vs Andrew Alvarez (L, WSH)",
        "description": "Tail key data: Park boost data unavailable. Spence (HR risk 0.63, vs LHB +1.91, vs RHB -0.47). Alvarez (HR risk -0.26, vs LHB -0.23, vs RHB -0.07).",
        "rows": [
            row("James Wood", "L", "+390", 78, "🌕 💣", ["vs Spence"], """2 HR, 2 near-HR, 88.5 mph EV. Spence LHB split +1.91, HR risk 0.63.""", blast="high"),
            row("Jacob Young", "R", "+1400", 66, "💎", ["vs Spence"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 89.7 mph EV. Spence RHB split -0.47, HR risk 0.63. tough split lane (-0.47); limited recent HR events."""),
            row("Salvador Perez", "R", "+496", 79, "", ["vs Alvarez"], """1 HR, 1 near-HR, 97.3 mph EV. Alvarez RHB split -0.07, HR risk -0.26. slight split headwind (-0.07); pitcher risk below avg (-0.26).""", blast="good"),
            row("Jac Caglianone", "L", "+640", 72, "", ["vs Alvarez"], """1 HR, 2 near-HR, 81.1 mph EV. Alvarez LHB split -0.23, HR risk -0.26. slight split headwind (-0.23); pitcher risk below avg (-0.26).""", blast="good"),
            row("Bobby Witt Jr.", "R", "+475", 74, "⭐", ["vs Alvarez"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.2 mph EV. Alvarez RHB split -0.07, HR risk -0.26. slight split headwind (-0.07); pitcher risk below avg (-0.26).""", blast="good"),
            row("Maikel Garcia", "R", "+1160", 77, "", ["vs Alvarez"], """0 HR, 1 near-HR, 99.0 mph EV. Alvarez RHB split -0.07, HR risk -0.26. slight split headwind (-0.07); pitcher risk below avg (-0.26).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ ARI - Walbert Urena (R, LAA) vs Ryne Nelson (R, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Urena (HR risk -0.96, vs LHB -1.14, vs RHB -0.23). Nelson (HR risk 0.77, vs LHB +0.41, vs RHB +0.64).",
        "rows": [
            row("Corbin Carroll", "L", "+518", 80, "🌕 💣", ["vs Urena"], """2 HR, 2 near-HR, 90.4 mph EV. Urena LHB split -1.14, HR risk -0.96. tough split lane (-1.14); pitcher suppresses HR (-0.96).""", blast="high"),
            row("Gabriel Moreno", "R", "+790", 88, "🌕 💣", ["vs Urena"], """3 HR, 4 near-HR, 90.0 mph EV. Urena RHB split -0.23, HR risk -0.96. slight split headwind (-0.23); pitcher suppresses HR (-0.96).""", blast="high"),
            row("Ketel Marte", "S", "+420", 64, "", ["vs Urena"], """0 HR, 1 near-HR, 88.2 mph EV. Urena RHB split -0.23, HR risk -0.96. slight split headwind (-0.23); pitcher suppresses HR (-0.96)."""),
            row("Logan O'Hoppe", "R", "+599", 82, "⭐ 🌕 💣", ["vs Nelson"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.1 mph EV. Nelson RHB split +0.64, HR risk 0.77. park/weather net drag (-8%).""", blast="high"),
            row("Donovan Walton", "L", "+1060", 66, "", ["vs Nelson"], """0 HR, 1 near-HR, 90.1 mph EV. Nelson LHB split +0.41, HR risk 0.77. park/weather net drag (-8%); limited recent HR events."""),
            row("Zach Neto", "R", "+470", 72, "", ["vs Nelson"], """1 HR, 1 near-HR, 90.0 mph EV. Nelson RHB split +0.64, HR risk 0.77. park/weather net drag (-8%).""", blast="good"),
            row("Mike Trout", "R", "+340", 82, "🚀", ["vs Nelson"], """1 HR, 1 near-HR, 101.1 mph EV. Nelson RHB split +0.64, HR risk 0.77. park/weather net drag (-8%).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ PHI - Ryan Gusto (R, MIA) vs Zack Wheeler (R, PHI)",
        "description": "Tail key data: Park boost +16% (stadium +16%, weather +0%). Gusto (HR risk -0.70, vs LHB -0.55, vs RHB -0.35). Wheeler (HR risk 0.09, vs LHB -0.02, vs RHB +0.05).",
        "rows": [
            row("Bryce Harper", "L", "+340", 78, "💎", ["vs Gusto"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.9 mph EV. Gusto LHB split -0.55, HR risk -0.70. tough split lane (-0.55); pitcher suppresses HR (-0.70).""", blast="good"),
            row("Kyle Schwarber", "L", "+225", 81, "⭐", ["vs Gusto"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.3 mph EV. Gusto LHB split -0.55, HR risk -0.70. tough split lane (-0.55); pitcher suppresses HR (-0.70).""", blast="good"),
            row("Heriberto Hernandez", "R", "+920", 85, "⭐ 🌕 💣", ["vs Wheeler"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.6 mph EV. Wheeler RHB split +0.05, HR risk 0.09.""", blast="high"),
            row("Owen Caissie", "L", "+850", 73, "", ["vs Wheeler"], """0 HR, 1 near-HR, 94.7 mph EV. Wheeler LHB split -0.02, HR risk 0.09. slight split headwind (-0.02); limited recent HR events.""", blast="good"),
            row("Joe Mack", "L", "+1040", 63, "", ["vs Wheeler"], """0 HR, 89.4 mph EV. Wheeler LHB split -0.02, HR risk 0.09. slight split headwind (-0.02); limited recent HR events."""),
        ],
    },
    {
        "title": "MIN @ TEX - Mike Paredes (R, MIN) vs MacKenzie Gore (L, TEX)",
        "description": "Tail key data: Park boost -12% (stadium -11%, weather +0%). Away starter risk unavailable. Gore (HR risk -0.68, vs LHB -0.57, vs RHB -0.35).",
        "rows": [
            row("Brandon Nimmo", "L", "+420", 70, "", ["vs Paredes"], """0 HR, 94.4 mph EV. Paredes split/risk data unavailable. limited split/risk sample; park/weather net drag (-12%).""", blast="good"),
            row("Corey Seager", "L", "N/A", 74, "", ["vs Paredes"], """1 HR, 2 near-HR, 90.1 mph EV. Paredes split/risk data unavailable. limited split/risk sample; park/weather net drag (-12%).""", blast="good"),
            row("Byron Buxton", "R", "+381", 90, "⭐ 🌕 💣", ["vs Gore"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 98.2 mph EV. Gore RHB split -0.35, HR risk -0.68. slight split headwind (-0.35); pitcher suppresses HR (-0.68).""", blast="high"),
            row("Royce Lewis", "R", "+640", 70, "", ["vs Gore"], """1 HR, 1 near-HR, 85.9 mph EV. Gore RHB split -0.35, HR risk -0.68. slight split headwind (-0.35); pitcher suppresses HR (-0.68).""", blast="good"),
        ],
    },
    {
        "title": "NYM @ CIN - Tobias Myers (R, NYM) vs Chase Burns (R, CIN)",
        "description": "Tail key data: Park boost +4% (stadium +12%, weather -8%). Myers (HR risk 0.46, vs LHB +0.18, vs RHB +0.16). Burns (HR risk 0.02, vs LHB -0.08, vs RHB +0.03).",
        "rows": [
            row("Matt McLain", "R", "+554", 75, "⭐", ["vs Myers"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.7 mph EV. Myers RHB split +0.16, HR risk 0.46. weather carry headwind (-8%); limited recent HR events.""", blast="good"),
            row("Sal Stewart", "R", "+378", 73, "", ["vs Myers"], """0 HR, 2 near-HR, 93.1 mph EV. Myers RHB split +0.16, HR risk 0.46. weather carry headwind (-8%).""", blast="good"),
            row("Dane Myers", "R", "+610", 72, "", ["vs Myers"], """0 HR, 1 near-HR, 94.4 mph EV. Myers RHB split +0.16, HR risk 0.46. weather carry headwind (-8%); limited recent HR events.""", blast="good"),
            row("Eugenio Suarez", "R", "+340", 75, "", ["vs Myers"], """1 HR, 1 near-HR, 93.1 mph EV. Myers RHB split +0.16, HR risk 0.46. weather carry headwind (-8%).""", blast="good"),
            row("Bo Bichette", "R", "+660", 81, "🌕 💣", ["vs Burns"], """2 HR, 2 near-HR, 91.3 mph EV. Burns RHB split +0.03, HR risk 0.02. weather carry headwind (-8%).""", blast="high"),
            row("Francisco Alvarez", "R", "+479", 79, "⭐", ["vs Burns"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.0 mph EV. Burns RHB split +0.03, HR risk 0.02. weather carry headwind (-8%).""", blast="good"),
            row("Juan Soto", "L", "+340", 75, "💎", ["vs Burns"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 91.1 mph EV. Burns LHB split -0.08, HR risk 0.02. slight split headwind (-0.08); weather carry headwind (-8%).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ ATH - Jared Jones (R, PIT) vs J.T. Ginn (R, ATH)",
        "description": "Tail key data: Park boost +40% (stadium +32%, weather +8%). Jones (HR risk 0.44, vs LHB +1.34, vs RHB -1.16). Ginn (HR risk -0.25, vs LHB -0.42, vs RHB +0.05).",
        "rows": [
            row("Henry Bolte", "R", "+775", 76, "🚀", ["vs Jones"], """0 HR, 103.4 mph EV. Jones RHB split -1.16, HR risk 0.44. tough split lane (-1.16); limited recent HR events.""", blast="good"),
            row("Shea Langeliers", "R", "+265", 73, "", ["vs Jones"], """1 HR, 1 near-HR, 91.4 mph EV. Jones RHB split -1.16, HR risk 0.44. tough split lane (-1.16).""", blast="good"),
            row("Tyler Callihan", "L", "+523", 86, "⭐ 🌕 💣", ["vs Ginn"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.1 mph EV. Ginn LHB split -0.42, HR risk -0.25. tough split lane (-0.42); pitcher risk below avg (-0.25).""", blast="high"),
            row("Endy Rodriguez", "S", "+610", 85, "🌕 💣 💎", ["vs Ginn"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 95.2 mph EV. Ginn RHB split +0.05, HR risk -0.25. pitcher risk below avg (-0.25).""", blast="high"),
            row("Brandon Lowe", "L", "+340", 85, "🌕 💣", ["vs Ginn"], """2 HR, 3 near-HR, 92.7 mph EV. Ginn LHB split -0.42, HR risk -0.25. tough split lane (-0.42); pitcher risk below avg (-0.25).""", blast="high"),
        ],
    },
    {
        "title": "SD @ STL - Lucas Giolito (R, SD) vs Dustin May (R, STL)",
        "description": "Tail key data: Park boost -9% (stadium -9%, weather +0%). Away starter risk unavailable. May (HR risk -0.54, vs LHB -0.59, vs RHB -0.28).",
        "rows": [
            row("Alec Burleson", "L", "+475", 86, "⭐ 🌕 💣", ["vs Giolito"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.2 mph EV. Giolito split/risk data unavailable. limited split/risk sample; park/weather net drag (-9%).""", blast="high"),
            row("Lars Nootbaar", "L", "+650", 78, "", ["vs Giolito"], """1 HR, 2 near-HR, 93.9 mph EV. Giolito split/risk data unavailable. limited split/risk sample; park/weather net drag (-9%).""", blast="good"),
            row("JJ Wetherholt", "L", "+570", 77, "", ["vs Giolito"], """1 HR, 2 near-HR, 93.0 mph EV. Giolito split/risk data unavailable. limited split/risk sample; park/weather net drag (-9%).""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+600", 74, "⭐", ["vs May"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.0 mph EV. May RHB split -0.28, HR risk -0.54. slight split headwind (-0.28); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Xander Bogaerts", "R", "+980", 72, "", ["vs May"], """0 HR, 1 near-HR, 93.5 mph EV. May RHB split -0.28, HR risk -0.54. slight split headwind (-0.28); pitcher suppresses HR (-0.54).""", blast="good"),
        ],
    },
    {
        "title": "TB @ LAD - Nick Martinez (R, TB) vs Eric Lauer 🧤 (L, LAD)",
        "description": "Tail key data: Park boost +11% (stadium +18%, weather -7%). Martinez (HR risk -0.58, vs LHB -0.60, vs RHB -0.09). Lauer 🧤 (HR risk 1.16, vs LHB +0.93, vs RHB +1.13).",
        "rows": [
            row("Max Muncy", "L", "+300", 70, "⭐", ["vs Martinez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 87.6 mph EV. Martinez LHB split -0.60, HR risk -0.58. tough split lane (-0.60); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Freddie Freeman", "L", "+443", 70, "", ["vs Martinez"], """1 HR, 1 near-HR, 87.1 mph EV. Martinez LHB split -0.60, HR risk -0.58. tough split lane (-0.60); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Shohei Ohtani", "L", "+229", 80, "", ["vs Martinez"], """1 HR, 2 near-HR, 96.2 mph EV. Martinez LHB split -0.60, HR risk -0.58. tough split lane (-0.60); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Andy Pages", "R", "+394", 82, "🌕 💣", ["vs Martinez"], """2 HR, 2 near-HR, 91.8 mph EV. Martinez RHB split -0.09, HR risk -0.58. slight split headwind (-0.09); pitcher suppresses HR (-0.58).""", blast="high"),
            row("Yandy Diaz", "R", "+365", 70, "", ["vs Lauer"], """1 HR, 1 near-HR, 88.0 mph EV. Lauer RHB split +1.13, HR risk 1.16. weather carry headwind (-7%).""", blast="good"),
            row("Junior Caminero", "R", "+240", 73, "", ["vs Lauer"], """0 HR, 96.8 mph EV. Lauer RHB split +1.13, HR risk 1.16. weather carry headwind (-7%); limited recent HR events.""", blast="good"),
            row("Ben Williamson", "R", "+1120", 75, "", ["vs Lauer"], """1 HR, 2 near-HR, 91.2 mph EV. Lauer RHB split +1.13, HR risk 1.16. weather carry headwind (-7%).""", blast="good"),
            row("Ryan Vilade", "R", "+640", 62, "", ["vs Lauer"], """0 HR, 86.7 mph EV. Lauer RHB split +1.13, HR risk 1.16. weather carry headwind (-7%); limited recent HR events."""),
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
