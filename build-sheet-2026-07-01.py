#!/usr/bin/env python3
"""Generate games[] block for 2026-07-01 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Bobby Witt Jr. (R)",
    "Bryce Eldridge (L)",
    "Byron Buxton (R)",
    "Francisco Lindor (S)",
    "Hunter Goodman (R)",
    "Jac Caglianone (L)",
    "James Wood (L)",
    "Josh Bell (S)",
    "Juan Soto (L)",
    "Junior Caminero (R)",
    "Kyle Schwarber (L)",
    "Manny Machado (R)",
    "Nick Kurtz (L)",
    "Rafael Devers (L)",
    "Riley Greene (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Bryce Harper (L)",
    "Casey Schmitt (R)",
    "Curtis Mead (R)",
    "Dillon Dingler (R)",
    "Francisco Alvarez (R)",
    "John Rave (L)",
    "Lars Nootbaar (L)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Andruw Monasterio (R)": "BOS",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Brandon Valenzuela (S)": "TOR",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Casey Schmitt (R)": "SF",
    "Christian Walker (R)": "HOU",
    "Coby Mayo (R)": "BAL",
    "Colby Thomas (R)": "ATH",
    "Corbin Carroll (L)": "ARI",
    "Curtis Mead (R)": "WSH",
    "Daniel Schneemann (L)": "CLE",
    "Dansby Swanson (R)": "CHC",
    "Daulton Varsho (L)": "TOR",
    "Dillon Dingler (R)": "DET",
    "Elly De La Cruz (S)": "CIN",
    "Endy Rodriguez (S)": "PIT",
    "Esmerlyn Valdez (R)": "PIT",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Freddie Freeman (L)": "LAD",
    "Gary Sanchez (R)": "MIL",
    "Gavin Sheets (L)": "SD",
    "Hunter Goodman (R)": "COL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Holliday (L)": "BAL",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Joc Pederson (L)": "TEX",
    "John Rave (L)": "KC",
    "Jonathan Aranda (L)": "TB",
    "Josh Bell (S)": "MIN",
    "Josh Jung (R)": "TEX",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kerry Carpenter (L)": "DET",
    "Ketel Marte (S)": "ARI",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lars Nootbaar (L)": "STL",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Nick Kurtz (L)": "ATH",
    "Nolan Arenado (R)": "ARI",
    "Otto Lopez (R)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Ryan O'Hearn (L)": "PIT",
    "Ryan Vilade (R)": "TB",
    "Sal Stewart (R)": "CIN",
    "Seiya Suzuki (R)": "CHC",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Taylor Trammell (L)": "HOU",
    "Teoscar Hernandez (R)": "LAD",
    "Ty France (R)": "SD",
    "William Contreras (R)": "MIL",
    "Wilyer Abreu (L)": "BOS",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("MIA @ COL", "Freeland"),
    ("MIN @ HOU", "Bradley"),
    ("NYM @ TOR", "Fisher"),
    ("TB @ KC", "Lugo"),
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
        "title": "CIN @ MIL - Andrew Abbott (L, CIN) vs Shane Drohan (L, MIL)",
        "description": "Tail key data: Park boost +24% (stadium +9%, weather +15%). Abbott (HR risk 0.85, vs LHB -0.64, vs RHB +1.11). Drohan (HR risk -0.50, vs LHB -1.08, vs RHB +0.33).",
        "rows": [
            row("Jackson Chourio", "R", "+365", 71, "", ["vs Abbott"], """0 HR, 95.4 mph EV. Abbott RHB split +1.11, HR risk 0.85. limited recent HR events.""", blast="good"),
            row("Gary Sanchez", "R", "+375", 70, "", ["vs Abbott"], """1 HR, 1 near-HR, 86.3 mph EV. Abbott RHB split +1.11, HR risk 0.85. lighter EV form (86.3 mph).""", blast="good"),
            row("Jake Bauers", "L", "N/A", 62, "", ["vs Abbott"], """0 HR, 81.0 mph EV. Abbott LHB split -0.64, HR risk 0.85. tough split lane (-0.64); limited recent HR events."""),
            row("William Contreras", "R", "+447", 71, "", ["vs Abbott"], """0 HR, 1 near-HR, 92.9 mph EV. Abbott RHB split +1.11, HR risk 0.85. limited recent HR events.""", blast="good"),
            row("Elly De La Cruz", "S", "+436", 82, "🚀", ["vs Drohan"], """1 HR, 1 near-HR, 100.3 mph EV. Drohan RHB split +0.33, HR risk -0.50. pitcher suppresses HR (-0.50).""", blast="good"),
            row("Sal Stewart", "R", "+390", 74, "", ["vs Drohan"], """0 HR, 98.5 mph EV. Drohan RHB split +0.33, HR risk -0.50. pitcher suppresses HR (-0.50); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ BAL - Noah Schultz (L, CWS) vs Dean Kremer (R, BAL)",
        "description": "Tail key data: Park boost data unavailable. Schultz (HR risk 0.31, vs LHB -1.05, vs RHB +0.72). Home starter risk unavailable.",
        "rows": [
            row("Coby Mayo", "R", "+210", 92, "🌕 💣", ["vs Schultz"], """3 HR, 3 near-HR, 95.8 mph EV. Schultz RHB split +0.72, HR risk 0.31.""", blast="high"),
            row("Jackson Holliday", "L", "+580", 66, "", ["vs Schultz"], """0 HR, 91.9 mph EV. Schultz LHB split -1.05, HR risk 0.31. tough split lane (-1.05); limited recent HR events."""),
            row("Pete Alonso", "R", "+257", 70, "", ["vs Schultz"], """0 HR, 93.6 mph EV. Schultz RHB split +0.72, HR risk 0.31. limited recent HR events.""", blast="good"),
            row("Randal Grichuk", "R", "N/A", 77, "", ["vs Kremer"], """1 HR, 1 near-HR, 90.0 mph EV, 14.0% barrels. Kremer split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Miguel Vargas", "R", "N/A", 68, "", ["vs Kremer"], """0 HR, 1 near-HR, 88.0 mph EV, 12.0% barrels. Kremer split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
        ],
    },
    {
        "title": "DET @ NYY - Troy Melton (R, DET) vs Will Warren (R, NYY)",
        "description": "Tail key data: Park boost +20% (stadium +5%, weather +15%). Melton (HR risk 0.46, vs LHB +0.83, vs RHB -0.92). Warren (HR risk -0.40, vs LHB -0.46, vs RHB +0.28).",
        "rows": [
            row("Ben Rice", "L", "+255", 91, "⭐ 🌕 💣", ["vs Melton"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 97.3 mph EV. Melton LHB split +0.83, HR risk 0.46.""", blast="high"),
            row("Spencer Jones", "L", "+430", 75, "", ["vs Melton"], """1 HR, 95.1 mph EV. Melton LHB split +0.83, HR risk 0.46.""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "+300", 85, "🌕 💣", ["vs Melton"], """2 HR, 3 near-HR, 92.6 mph EV. Melton LHB split +0.83, HR risk 0.46.""", blast="high"),
            row("Riley Greene", "L", "+329", 91, "⭐ 🌕 💣", ["vs Warren"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 94.8 mph EV. Warren LHB split -0.46, HR risk -0.40. tough split lane (-0.46); pitcher suppresses HR (-0.40).""", blast="high"),
            row("Dillon Dingler", "R", "+390", 92, "🌕 💣 💎", ["vs Warren"], """Worst Pickz Hidden Gem. 3 HR, 5 near-HR, 92.4 mph EV. Warren RHB split +0.28, HR risk -0.40. pitcher suppresses HR (-0.40).""", blast="high"),
            row("Spencer Torkelson", "R", "+360", 73, "", ["vs Warren"], """1 HR, 1 near-HR, 90.7 mph EV. Warren RHB split +0.28, HR risk -0.40. pitcher suppresses HR (-0.40).""", blast="good"),
            row("Kerry Carpenter", "L", "+330", 77, "", ["vs Warren"], """1 HR, 2 near-HR, 93.0 mph EV. Warren LHB split -0.46, HR risk -0.40. tough split lane (-0.46); pitcher suppresses HR (-0.40).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ ATH - Charlie Barnes (L, LAD) vs J.T. Ginn (R, ATH)",
        "description": "Tail key data: Park boost +38% (stadium +32%, weather +6%). Away starter risk unavailable. Ginn (HR risk -0.54, vs LHB -0.15, vs RHB -0.41).",
        "rows": [
            row("Nick Kurtz", "L", "N/A", 85, "⭐", ["vs Barnes"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.0 mph EV, 18.0% barrels. Barnes split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Colby Thomas", "R", "N/A", 79, "", ["vs Barnes"], """1 HR, 1 near-HR, 92.0 mph EV, 16.0% barrels. Barnes split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Shea Langeliers", "R", "N/A", 78, "", ["vs Barnes"], """1 HR, 1 near-HR, 91.0 mph EV, 15.0% barrels. Barnes split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Teoscar Hernandez", "R", "+539", 62, "", ["vs Ginn"], """0 HR, 86.6 mph EV. Ginn RHB split -0.41, HR risk -0.54. tough split lane (-0.41); pitcher suppresses HR (-0.54)."""),
            row("Shohei Ohtani", "L", "+210", 87, "🌕 💣", ["vs Ginn"], """2 HR, 2 near-HR, 97.3 mph EV. Ginn LHB split -0.15, HR risk -0.54. slight split headwind (-0.15); pitcher suppresses HR (-0.54).""", blast="high"),
            row("Freddie Freeman", "L", "+363", 73, "", ["vs Ginn"], """1 HR, 1 near-HR, 91.2 mph EV. Ginn LHB split -0.15, HR risk -0.54. slight split headwind (-0.15); pitcher suppresses HR (-0.54).""", blast="good"),
        ],
    },
    {
        "title": "MIA @ COL - Max Meyer (R, MIA) vs Kyle Freeland 🧤 (L, COL)",
        "description": "Tail key data: Park boost +23% (stadium +22%, weather +1%). Meyer (HR risk -0.33, vs LHB -0.58, vs RHB +0.45). Freeland 🧤 (HR risk 0.99, vs LHB -0.62, vs RHB +1.18).",
        "rows": [
            row("Hunter Goodman", "R", "+283", 93, "⭐ 🌕 💣", ["vs Meyer"], """Worst Pickz Favorite. 3 HR, 5 near-HR, 92.6 mph EV. Meyer RHB split +0.45, HR risk -0.33. pitcher risk below avg (-0.33).""", blast="high"),
            row("Mickey Moniak", "L", "+434", 71, "", ["vs Meyer"], """1 HR, 1 near-HR, 88.7 mph EV. Meyer LHB split -0.58, HR risk -0.33. tough split lane (-0.58); pitcher risk below avg (-0.33).""", blast="good"),
            row("Kyle Karros", "R", "+1040", 85, "🌕 💣", ["vs Meyer"], """2 HR, 2 near-HR, 95.0 mph EV. Meyer RHB split +0.45, HR risk -0.33. pitcher risk below avg (-0.33).""", blast="high"),
            row("Kyle Stowers", "L", "+360", 62, "", ["vs Freeland"], """0 HR, 86.1 mph EV. Freeland LHB split -0.62, HR risk 0.99. tough split lane (-0.62); limited recent HR events."""),
            row("Otto Lopez", "R", "+572", 71, "", ["vs Freeland"], """1 HR, 1 near-HR, 88.7 mph EV. Freeland RHB split +1.18, HR risk 0.99.""", blast="good"),
        ],
    },
    {
        "title": "MIN @ HOU - Taj Bradley 🧤 (R, MIN) vs Tatsuya Imai (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +5%, weather +0%). Bradley 🧤 (HR risk 1.14, vs LHB +1.46, vs RHB -0.40). Imai (HR risk 0.02, vs LHB +0.13, vs RHB +0.00).",
        "rows": [
            row("Yordan Alvarez", "L", "+220", 79, "⭐", ["vs Bradley"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.1 mph EV. Bradley LHB split +1.46, HR risk 1.14.""", blast="good"),
            row("Taylor Trammell", "L", "+551", 89, "🌕 💣", ["vs Bradley"], """2 HR, 3 near-HR, 96.9 mph EV. Bradley LHB split +1.46, HR risk 1.14.""", blast="high"),
            row("Christian Walker", "R", "+360", 71, "", ["vs Bradley"], """1 HR, 1 near-HR, 88.6 mph EV. Bradley RHB split -0.40, HR risk 1.14. tough split lane (-0.40).""", blast="good"),
            row("Byron Buxton", "R", "N/A", 81, "⭐ 🌕 💣", ["vs Imai"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 89.1 mph EV. Imai RHB split +0.00, HR risk 0.02.""", blast="high"),
            row("Josh Bell", "S", "+480", 82, "⭐ 🌕 💣", ["vs Imai"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 90.2 mph EV. Imai RHB split +0.00, HR risk 0.02.""", blast="high"),
        ],
    },
    {
        "title": "NYM @ TOR - Freddy Peralta (R, NYM) vs Braydon Fisher 🧤 (R, TOR)",
        "description": "Tail key data: Park boost +2% (stadium +7%, weather -4%). Peralta (HR risk -0.01, vs LHB +0.55, vs RHB -1.34). Fisher 🧤 (HR risk 1.07, vs LHB +1.65, vs RHB -0.44).",
        "rows": [
            row("Brandon Valenzuela", "S", "N/A", 76, "", ["vs Peralta"], """1 HR, 2 near-HR, 91.6 mph EV. Peralta RHB split -1.34, HR risk -0.01. tough split lane (-1.34); pitcher risk below avg (-0.01).""", blast="good"),
            row("Kazuma Okamoto", "R", "+356", 72, "", ["vs Peralta"], """1 HR, 1 near-HR, 90.3 mph EV. Peralta RHB split -1.34, HR risk -0.01. tough split lane (-1.34); pitcher risk below avg (-0.01).""", blast="good"),
            row("Daulton Varsho", "L", "+505", 78, "🌕 💣", ["vs Peralta"], """2 HR, 2 near-HR, 82.5 mph EV. Peralta LHB split +0.55, HR risk -0.01. pitcher risk below avg (-0.01); weather carry headwind (-4%).""", blast="high"),
            row("Francisco Lindor", "S", "+471", 88, "⭐ 🌕 💣", ["vs Fisher"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.5 mph EV. Fisher RHB split -0.44, HR risk 1.07. tough split lane (-0.44); weather carry headwind (-4%).""", blast="high"),
            row("Juan Soto", "L", "+333", 76, "⭐", ["vs Fisher"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 98.3 mph EV. Fisher LHB split +1.65, HR risk 1.07. weather carry headwind (-4%); limited recent HR events.""", blast="good"),
            row("Francisco Alvarez", "R", "+610", 76, "💎", ["vs Fisher"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.1 mph EV. Fisher RHB split -0.44, HR risk 1.07. tough split lane (-0.44); weather carry headwind (-4%).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ PHI - Paul Skenes (R, PIT) vs Zack Wheeler (R, PHI)",
        "description": "Tail key data: Park boost +44% (stadium +14%, weather +30%). Skenes (HR risk -0.52, vs LHB +0.00, vs RHB -0.43). Wheeler (HR risk -0.57, vs LHB +0.00, vs RHB -0.85).",
        "rows": [
            row("Kyle Schwarber", "L", "+190", 90, "🚀 ⭐ 🌕 💣", ["vs Skenes"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 102.5 mph EV. Skenes LHB split +0.00, HR risk -0.52. pitcher suppresses HR (-0.52).""", blast="high"),
            row("Bryce Harper", "L", "+310", 98, "🌕 💣 💎", ["vs Skenes"], """Worst Pickz Hidden Gem. 4 HR, 4 near-HR, 98.0 mph EV. Skenes LHB split +0.00, HR risk -0.52. pitcher suppresses HR (-0.52).""", blast="high"),
            row("Brandon Marsh", "L", "+560", 75, "", ["vs Skenes"], """1 HR, 1 near-HR, 92.7 mph EV. Skenes LHB split +0.00, HR risk -0.52. pitcher suppresses HR (-0.52).""", blast="good"),
            row("Endy Rodriguez", "S", "+520", 82, "🚀", ["vs Wheeler"], """1 HR, 1 near-HR, 100.0 mph EV. Wheeler RHB split -0.85, HR risk -0.57. tough split lane (-0.85); pitcher suppresses HR (-0.57).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+502", 74, "", ["vs Wheeler"], """1 HR, 2 near-HR, 89.8 mph EV. Wheeler RHB split -0.85, HR risk -0.57. tough split lane (-0.85); pitcher suppresses HR (-0.57).""", blast="good"),
            row("Ryan O'Hearn", "L", "+590", 78, "🌕 💣", ["vs Wheeler"], """2 HR, 2 near-HR, 84.7 mph EV. Wheeler LHB split +0.00, HR risk -0.57. pitcher suppresses HR (-0.57); lighter EV form (84.7 mph).""", blast="high"),
        ],
    },
    {
        "title": "SD @ CHC - Walker Buehler (R, SD) vs Colin Rea (R, CHC)",
        "description": "Tail key data: Park boost +47% (stadium -1%, weather +48%). Buehler (HR risk -0.31, vs LHB -0.80, vs RHB +0.79). Rea (HR risk 0.02, vs LHB -0.60, vs RHB +1.17).",
        "rows": [
            row("Seiya Suzuki", "R", "+320", 72, "", ["vs Buehler"], """1 HR, 2 near-HR, 86.5 mph EV. Buehler RHB split +0.79, HR risk -0.31. pitcher risk below avg (-0.31); lighter EV form (86.5 mph).""", blast="good"),
            row("Dansby Swanson", "R", "+405", 92, "🌕 💣", ["vs Buehler"], """3 HR, 3 near-HR, 96.1 mph EV. Buehler RHB split +0.79, HR risk -0.31. pitcher risk below avg (-0.31).""", blast="high"),
            row("Michael Conforto", "L", "+430", 71, "", ["vs Buehler"], """1 HR, 1 near-HR, 88.9 mph EV. Buehler LHB split -0.80, HR risk -0.31. tough split lane (-0.80); pitcher risk below avg (-0.31).""", blast="good"),
            row("Manny Machado", "R", "+266", 95, "⭐ 🌕 💣", ["vs Rea"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 97.4 mph EV. Rea RHB split +1.17, HR risk 0.02.""", blast="high"),
            row("Gavin Sheets", "L", "+395", 80, "🌕 💣", ["vs Rea"], """2 HR, 2 near-HR, 90.0 mph EV. Rea LHB split -0.60, HR risk 0.02. tough split lane (-0.60).""", blast="high"),
            row("Fernando Tatis Jr.", "R", "+240", 90, "🌕 💣", ["vs Rea"], """2 HR, 2 near-HR, 99.8 mph EV. Rea RHB split +1.17, HR risk 0.02.""", blast="high"),
            row("Ty France", "R", "+400", 84, "🌕 💣", ["vs Rea"], """3 HR, 3 near-HR, 87.6 mph EV. Rea RHB split +1.17, HR risk 0.02. lighter EV form (87.6 mph).""", blast="high"),
        ],
    },
    {
        "title": "SF @ ARI - Trevor McDonald (R, SF) vs Zac Gallen (R, ARI)",
        "description": "Tail key data: Park boost -9% (stadium -9%, weather +0%). McDonald (HR risk -0.94, vs LHB +0.10, vs RHB -1.63). Gallen (HR risk 0.58, vs LHB +0.47, vs RHB +0.36).",
        "rows": [
            row("Corbin Carroll", "L", "+484", 67, "", ["vs McDonald"], """0 HR, 1 near-HR, 91.1 mph EV. McDonald LHB split +0.10, HR risk -0.94. pitcher suppresses HR (-0.94); park/weather net drag (-9%)."""),
            row("Ketel Marte", "S", "+439", 74, "", ["vs McDonald"], """1 HR, 1 near-HR, 91.6 mph EV. McDonald RHB split -1.63, HR risk -0.94. tough split lane (-1.63); pitcher suppresses HR (-0.94).""", blast="good"),
            row("Nolan Arenado", "R", "+1040", 70, "", ["vs McDonald"], """1 HR, 1 near-HR, 88.0 mph EV. McDonald RHB split -1.63, HR risk -0.94. tough split lane (-1.63); pitcher suppresses HR (-0.94).""", blast="good"),
            row("Rafael Devers", "L", "+418", 87, "⭐ 🌕 💣", ["vs Gallen"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.7 mph EV. Gallen LHB split +0.47, HR risk 0.58. park/weather net drag (-9%).""", blast="high"),
            row("Bryce Eldridge", "L", "+550", 77, "⭐", ["vs Gallen"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 99.1 mph EV. Gallen LHB split +0.47, HR risk 0.58. park/weather net drag (-9%); limited recent HR events.""", blast="good"),
            row("Casey Schmitt", "R", "+475", 80, "💎", ["vs Gallen"], """Worst Pickz Hidden Gem. 0 HR, 3 near-HR, 98.2 mph EV. Gallen RHB split +0.36, HR risk 0.58. park/weather net drag (-9%).""", blast="good"),
        ],
    },
    {
        "title": "STL @ ATL - Michael McGreevy (R, STL) vs Reynaldo Lopez (R, ATL)",
        "description": "Tail key data: Park boost +9% (stadium -3%, weather +11%). McGreevy (HR risk -0.02, vs LHB +0.11, vs RHB -0.04). Lopez (HR risk -1.19, vs LHB -0.56, vs RHB -0.26).",
        "rows": [
            row("Matt Olson", "L", "+330", 62, "", ["vs McGreevy"], """0 HR, 87.7 mph EV. McGreevy LHB split +0.11, HR risk -0.02. pitcher risk below avg (-0.02); limited recent HR events."""),
            row("Michael Harris II", "L", "+424", 70, "", ["vs McGreevy"], """1 HR, 1 near-HR, 85.3 mph EV. McGreevy LHB split +0.11, HR risk -0.02. pitcher risk below avg (-0.02); lighter EV form (85.3 mph).""", blast="good"),
            row("Lars Nootbaar", "L", "+477", 76, "💎", ["vs Lopez"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 95.6 mph EV. Lopez LHB split -0.56, HR risk -1.19. tough split lane (-0.56); pitcher suppresses HR (-1.19).""", blast="good"),
            row("Alec Burleson", "L", "+390", 74, "", ["vs Lopez"], """0 HR, 97.7 mph EV. Lopez LHB split -0.56, HR risk -1.19. tough split lane (-0.56); pitcher suppresses HR (-1.19).""", blast="good"),
        ],
    },
    {
        "title": "TB @ KC - Shane McClanahan (L, TB) vs Seth Lugo 🧤 (R, KC)",
        "description": "Tail key data: Park boost +40% (stadium +11%, weather +30%). McClanahan (HR risk 0.30, vs LHB +1.19, vs RHB -0.21). Lugo 🧤 (HR risk 1.25, vs LHB +0.57, vs RHB +1.42).",
        "rows": [
            row("Jac Caglianone", "L", "+360", 95, "⭐ 🌕 💣", ["vs McClanahan"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 96.7 mph EV. McClanahan LHB split +1.19, HR risk 0.30.""", blast="high"),
            row("Bobby Witt Jr.", "R", "+357", 78, "⭐", ["vs McClanahan"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.4 mph EV. McClanahan RHB split -0.21, HR risk 0.30. slight split headwind (-0.21).""", blast="good"),
            row("John Rave", "L", "N/A", 76, "💎", ["vs McClanahan"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 97.6 mph EV. McClanahan LHB split +1.19, HR risk 0.30. limited recent HR events.""", blast="good"),
            row("Junior Caminero", "R", "+220", 98, "⭐ 🌕 💣", ["vs Lugo"], """Worst Pickz Favorite. 5 HR, 6 near-HR, 95.6 mph EV. Lugo RHB split +1.42, HR risk 1.25.""", blast="high"),
            row("Jonathan Aranda", "L", "+403", 72, "", ["vs Lugo"], """1 HR, 1 near-HR, 90.5 mph EV. Lugo LHB split +0.57, HR risk 1.25.""", blast="good"),
            row("Ryan Vilade", "R", "N/A", 73, "", ["vs Lugo"], """1 HR, 1 near-HR, 90.8 mph EV. Lugo RHB split +1.42, HR risk 1.25.""", blast="good"),
        ],
    },
    {
        "title": "TEX @ CLE - MacKenzie Gore (L, TEX) vs Joey Cantillo (L, CLE)",
        "description": "Tail key data: Park boost +14% (stadium -4%, weather +18%). Gore (HR risk -0.60, vs LHB -0.46, vs RHB -0.21). Cantillo (HR risk 0.53, vs LHB +0.26, vs RHB +0.49).",
        "rows": [
            row("Rhys Hoskins", "R", "+440", 74, "", ["vs Gore"], """0 HR, 97.7 mph EV. Gore RHB split -0.21, HR risk -0.60. slight split headwind (-0.21); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Daniel Schneemann", "L", "N/A", 74, "", ["vs Gore"], """1 HR, 1 near-HR, 92.3 mph EV. Gore LHB split -0.46, HR risk -0.60. tough split lane (-0.46); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Joc Pederson", "L", "N/A", 78, "", ["vs Cantillo"], """0 HR, 1 near-HR, 99.8 mph EV. Cantillo LHB split +0.26, HR risk 0.53. limited recent HR events.""", blast="good"),
            row("Josh Jung", "R", "+630", 70, "", ["vs Cantillo"], """0 HR, 94.4 mph EV. Cantillo RHB split +0.49, HR risk 0.53. limited recent HR events.""", blast="good"),
            row("Brandon Nimmo", "L", "N/A", 64, "", ["vs Cantillo"], """0 HR, 89.7 mph EV. Cantillo LHB split +0.26, HR risk 0.53. limited recent HR events."""),
        ],
    },
    {
        "title": "WSH @ BOS - Andrew Alvarez (L, WSH) vs Payton Tolle (L, BOS)",
        "description": "Tail key data: Park boost data unavailable. Alvarez (HR risk -1.33, vs LHB -0.84, vs RHB -0.74). Tolle (HR risk -0.25, vs LHB +0.54, vs RHB -0.42).",
        "rows": [
            row("Wilyer Abreu", "L", "+460", 72, "", ["vs Alvarez"], """1 HR, 1 near-HR, 90.3 mph EV. Alvarez LHB split -0.84, HR risk -1.33. tough split lane (-0.84); pitcher suppresses HR (-1.33).""", blast="good"),
            row("Andruw Monasterio", "R", "+710", 70, "", ["vs Alvarez"], """1 HR, 1 near-HR, 85.7 mph EV. Alvarez RHB split -0.74, HR risk -1.33. tough split lane (-0.74); pitcher suppresses HR (-1.33).""", blast="good"),
            row("James Wood", "L", "+288", 72, "⭐", ["vs Tolle"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 90.1 mph EV. Tolle LHB split +0.54, HR risk -0.25. pitcher risk below avg (-0.25).""", blast="good"),
            row("Curtis Mead", "R", "+400", 79, "💎", ["vs Tolle"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 95.4 mph EV. Tolle RHB split -0.42, HR risk -0.25. tough split lane (-0.42); pitcher risk below avg (-0.25).""", blast="good"),
            row("CJ Abrams", "L", "+520", 65, "", ["vs Tolle"], """0 HR, 91.2 mph EV. Tolle LHB split +0.54, HR risk -0.25. pitcher risk below avg (-0.25); limited recent HR events."""),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-01")

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

    out = ROOT / '_games-0701.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
