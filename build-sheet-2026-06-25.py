#!/usr/bin/env python3
"""Generate games[] block for 2026-06-25 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "George Springer (R)",
    "Jac Caglianone (L)",
    "Junior Caminero (R)",
    "Kyle Schwarber (L)",
    "Marcell Ozuna (R)",
    "Mark Vientos (R)",
    "Miguel Amaya (R)",
    "Paul Goldschmidt (R)",
    "Pete Crow-Armstrong (L)",
    "Rafael Devers (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Esmerlyn Valdez (R)",
    "Henry Davis (R)",
    "Hunter Feduccia (L)",
    "John Rave (L)",
    "Nate Eaton (R)",
    "Randy Arozarena (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Alejandro Kirk (R)": "TOR",
    "Ben Rice (L)": "NYY",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "CJ Abrams (L)": "WSH",
    "Cam Smith (R)": "HOU",
    "Carson Benge (L)": "NYM",
    "Carson Kelly (R)": "CHC",
    "Casey Schmitt (R)": "SF",
    "Colt Keith (L)": "DET",
    "Corbin Carroll (L)": "ARI",
    "Curtis Mead (R)": "WSH",
    "Dansby Swanson (R)": "CHC",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Edmundo Sosa (R)": "PHI",
    "Endy Rodriguez (S)": "PIT",
    "Esmerlyn Valdez (R)": "PIT",
    "Francisco Alvarez (R)": "NYM",
    "George Springer (R)": "TOR",
    "Henry Davis (R)": "PIT",
    "Hunter Feduccia (L)": "TB",
    "Isaac Paredes (R)": "HOU",
    "Ivan Herrera (R)": "STL",
    "Jac Caglianone (L)": "KC",
    "James Wood (L)": "WSH",
    "Jarred Kelenic (L)": "TEX",
    "Joc Pederson (L)": "TEX",
    "John Rave (L)": "KC",
    "Jonah Heim (S)": "ATH",
    "Jonathan Aranda (L)": "TB",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Kyle Higashioka (R)": "TEX",
    "Kyle Schwarber (L)": "PHI",
    "Lars Nootbaar (L)": "STL",
    "Luis Garcia Jr. (L)": "WSH",
    "Luke Raley (L)": "SEA",
    "Marcell Ozuna (R)": "PIT",
    "Mark Vientos (R)": "NYM",
    "Max Schuemann (R)": "NYY",
    "Miguel Amaya (R)": "CHC",
    "Nate Eaton (R)": "BOS",
    "Nick Kurtz (L)": "ATH",
    "Paul Goldschmidt (R)": "NYY",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randy Arozarena (R)": "SEA",
    "Ryan O'Hearn (L)": "PIT",
    "Seiya Suzuki (R)": "CHC",
    "Spencer Jones (L)": "NYY",
    "Taylor Trammell (L)": "HOU",
    "Tyler Soderstrom (L)": "ATH",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("ATH @ SF", "Springs"),
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
        "title": "ARI @ STL - Zac Gallen (R, ARI) vs Michael McGreevy (R, STL)",
        "description": "Tail key data: Park boost -7% (stadium -9%, weather +2%). Gallen (HR risk 0.56, vs LHB +0.90, vs RHB +0.16). McGreevy (HR risk 0.35, vs LHB +0.65, vs RHB +0.10).",
        "rows": [
            row("Alec Burleson", "L", "+470", 71, "", ["vs Gallen"], """0 HR, 1 near-HR, 93.3 mph EV. Gallen LHB split +0.90, HR risk 0.56. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
            row("Ivan Herrera", "R", "+750", 75, "", ["vs Gallen"], """1 HR, 1 near-HR, 93.4 mph EV. Gallen RHB split +0.16, HR risk 0.56. park/weather net drag (-7%).""", blast="good"),
            row("Lars Nootbaar", "L", "+610", 75, "", ["vs Gallen"], """0 HR, 2 near-HR, 94.7 mph EV. Gallen LHB split +0.90, HR risk 0.56. park/weather net drag (-7%).""", blast="good"),
            row("Corbin Carroll", "L", "+427", 64, "", ["vs McGreevy"], """0 HR, 1 near-HR, 88.2 mph EV. McGreevy LHB split +0.65, HR risk 0.35. park/weather net drag (-7%); limited recent HR events."""),
            row("Ketel Marte", "S", "+485", 68, "", ["vs McGreevy"], """0 HR, 92.5 mph EV. McGreevy RHB split +0.10, HR risk 0.35. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "ATH @ SF - Jeffrey Springs 🧤 (L, ATH) vs Landen Roupp (R, SF)",
        "description": "Tail key data: Park boost -22% (stadium -15%, weather -7%). Springs 🧤 (HR risk 2.00, vs LHB +0.94, vs RHB +1.94). Roupp (HR risk -0.82, vs LHB -0.20, vs RHB -0.89).",
        "rows": [
            row("Rafael Devers", "L", "+480", 78, "⭐", ["vs Springs"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 91.7 mph EV. Springs LHB split +0.94, HR risk 2.00. park/weather net drag (-22%).""", blast="good"),
            row("Bryce Eldridge", "L", "+498", 72, "", ["vs Springs"], """1 HR, 2 near-HR, 83.3 mph EV. Springs LHB split +0.94, HR risk 2.00. park/weather net drag (-22%); lighter EV form (83.3 mph).""", blast="good"),
            row("Casey Schmitt", "R", "+434", 65, "", ["vs Springs"], """0 HR, 91.2 mph EV. Springs RHB split +1.94, HR risk 2.00. park/weather net drag (-22%); limited recent HR events."""),
            row("Tyler Soderstrom", "L", "+710", 83, "🌕 💣", ["vs Roupp"], """2 HR, 2 near-HR, 92.9 mph EV. Roupp LHB split -0.20, HR risk -0.82. slight split headwind (-0.20); pitcher suppresses HR (-0.82).""", blast="high"),
            row("Nick Kurtz", "L", "+473", 69, "", ["vs Roupp"], """0 HR, 92.6 mph EV. Roupp LHB split -0.20, HR risk -0.82. slight split headwind (-0.20); pitcher suppresses HR (-0.82).""", blast="good"),
            row("Jonah Heim", "S", "+880", 78, "", ["vs Roupp"], """1 HR, 1 near-HR, 95.6 mph EV. Roupp RHB split -0.89, HR risk -0.82. tough split lane (-0.89); pitcher suppresses HR (-0.82).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ NYM - Matthew Boyd (L, CHC) vs Freddy Peralta (R, NYM)",
        "description": "Tail key data: Park boost +15% (stadium -1%, weather +16%). Boyd (HR risk -0.04, vs LHB -0.93, vs RHB +0.16). Peralta (HR risk 0.01, vs LHB +0.92, vs RHB -1.40).",
        "rows": [
            row("Mark Vientos", "R", "+409", 84, "⭐ 🌕 💣", ["vs Boyd"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 85.0 mph EV. Boyd RHB split +0.16, HR risk -0.04. pitcher risk below avg (-0.04); lighter EV form (85.0 mph).""", blast="high"),
            row("Carson Benge", "L", "+940", 86, "🌕 💣", ["vs Boyd"], """2 HR, 2 near-HR, 95.9 mph EV. Boyd LHB split -0.93, HR risk -0.04. tough split lane (-0.93); pitcher risk below avg (-0.04).""", blast="high"),
            row("Juan Soto", "L", "+350", 74, "", ["vs Boyd"], """0 HR, 97.5 mph EV. Boyd LHB split -0.93, HR risk -0.04. tough split lane (-0.93); pitcher risk below avg (-0.04).""", blast="good"),
            row("Francisco Alvarez", "R", "+465", 70, "", ["vs Boyd"], """1 HR, 1 near-HR, 87.9 mph EV. Boyd RHB split +0.16, HR risk -0.04. pitcher risk below avg (-0.04); lighter EV form (87.9 mph).""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+340", 83, "⭐ 🌕 💣", ["vs Peralta"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.6 mph EV. Peralta LHB split +0.92, HR risk 0.01.""", blast="high"),
            row("Miguel Amaya", "R", "N/A", 70, "⭐", ["vs Peralta"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 89.5 mph EV. Peralta RHB split -1.40, HR risk 0.01. tough split lane (-1.40).""", blast="good"),
            row("Seiya Suzuki", "R", "+423", 62, "", ["vs Peralta"], """0 HR, 86.4 mph EV. Peralta RHB split -1.40, HR risk 0.01. tough split lane (-1.40); limited recent HR events."""),
            row("Carson Kelly", "R", "+650", 78, "", ["vs Peralta"], """1 HR, 1 near-HR, 96.5 mph EV. Peralta RHB split -1.40, HR risk 0.01. tough split lane (-1.40).""", blast="good"),
            row("Dansby Swanson", "R", "+596", 76, "", ["vs Peralta"], """1 HR, 1 near-HR, 94.5 mph EV. Peralta RHB split -1.40, HR risk 0.01. tough split lane (-1.40).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ DET - Tatsuya Imai (R, HOU) vs Troy Melton (R, DET)",
        "description": "Tail key data: Park boost +3% (stadium -11%, weather +13%). Imai (HR risk 0.05, vs LHB +0.25, vs RHB -0.06). Melton (HR risk 0.10, vs LHB +0.61, vs RHB -0.56).",
        "rows": [
            row("Dillon Dingler", "R", "+456", 80, "🌕 💣", ["vs Imai"], """2 HR, 2 near-HR, 89.5 mph EV. Imai RHB split -0.06, HR risk 0.05. slight split headwind (-0.06); park suppresses carry (-11%).""", blast="high"),
            row("Colt Keith", "L", "+600", 82, "🌕 💣", ["vs Imai"], """1 HR, 4 near-HR, 91.8 mph EV. Imai LHB split +0.25, HR risk 0.05. park suppresses carry (-11%).""", blast="high"),
            row("Yordan Alvarez", "L", "+277", 74, "⭐", ["vs Melton"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 89.7 mph EV. Melton LHB split +0.61, HR risk 0.10. park suppresses carry (-11%).""", blast="good"),
            row("Isaac Paredes", "R", "+496", 72, "", ["vs Melton"], """1 HR, 2 near-HR, 87.2 mph EV. Melton RHB split -0.56, HR risk 0.10. tough split lane (-0.56); park suppresses carry (-11%).""", blast="good"),
            row("Cam Smith", "R", "+720", 75, "", ["vs Melton"], """1 HR, 2 near-HR, 91.3 mph EV. Melton RHB split -0.56, HR risk 0.10. tough split lane (-0.56); park suppresses carry (-11%).""", blast="good"),
            row("Taylor Trammell", "L", "N/A", 77, "", ["vs Melton"], """1 HR, 1 near-HR, 94.6 mph EV. Melton LHB split +0.61, HR risk 0.10. park suppresses carry (-11%).""", blast="good"),
        ],
    },
    {
        "title": "KC @ TB - Seth Lugo (R, KC) vs Casey Legumina (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -3%, weather +1%). Lugo (HR risk 0.79, vs LHB +0.67, vs RHB +0.66). Legumina (HR risk -1.09, vs LHB -0.57, vs RHB -0.56).",
        "rows": [
            row("Junior Caminero", "R", "+285", 92, "⭐ 🌕 💣", ["vs Lugo"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 99.5 mph EV. Lugo RHB split +0.66, HR risk 0.79.""", blast="high"),
            row("Jonathan Aranda", "L", "+430", 74, "", ["vs Lugo"], """1 HR, 1 near-HR, 91.8 mph EV. Lugo LHB split +0.67, HR risk 0.79.""", blast="good"),
            row("Hunter Feduccia", "L", "+870", 75, "💎", ["vs Lugo"], """Worst Pickz Hidden Gem. 0 HR, 98.9 mph EV. Lugo LHB split +0.67, HR risk 0.79. limited recent HR events.""", blast="good"),
            row("John Rave", "L", "N/A", 72, "💎", ["vs Legumina"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 80.3 mph EV. Legumina LHB split -0.57, HR risk -1.09. tough split lane (-0.57); pitcher suppresses HR (-1.09).""", blast="good"),
            row("Jac Caglianone", "L", "+343", 94, "⭐ 🌕 💣", ["vs Legumina"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 97.5 mph EV. Legumina LHB split -0.57, HR risk -1.09. tough split lane (-0.57); pitcher suppresses HR (-1.09).""", blast="high"),
        ],
    },
    {
        "title": "NYY @ BOS - Cam Schlittler (R, NYY) vs Connelly Early (L, BOS)",
        "description": "Tail key data: Park boost +0% (stadium -8%, weather +8%). Schlittler (HR risk -0.79, vs LHB -0.58, vs RHB -0.43). Early (HR risk 0.31, vs LHB -0.32, vs RHB +0.53).",
        "rows": [
            row("Wilyer Abreu", "L", "+496", 73, "", ["vs Schlittler"], """1 HR, 1 near-HR, 90.9 mph EV. Schlittler LHB split -0.58, HR risk -0.79. tough split lane (-0.58); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Nate Eaton", "R", "+729", 79, "💎", ["vs Schlittler"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.9 mph EV. Schlittler RHB split -0.43, HR risk -0.79. tough split lane (-0.43); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Willson Contreras", "R", "+500", 77, "", ["vs Schlittler"], """1 HR, 1 near-HR, 95.2 mph EV. Schlittler RHB split -0.43, HR risk -0.79. tough split lane (-0.43); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Paul Goldschmidt", "R", "+400", 85, "⭐ 🌕 💣", ["vs Early"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 88.6 mph EV. Early RHB split +0.53, HR risk 0.31. park suppresses carry (-8%).""", blast="high"),
            row("Max Schuemann", "R", "+870", 66, "", ["vs Early"], """0 HR, 1 near-HR, 90.3 mph EV. Early RHB split +0.53, HR risk 0.31. park suppresses carry (-8%); limited recent HR events."""),
            row("Spencer Jones", "L", "N/A", 71, "", ["vs Early"], """0 HR, 95.2 mph EV. Early LHB split -0.32, HR risk 0.31. slight split headwind (-0.32); park suppresses carry (-8%).""", blast="good"),
            row("Ben Rice", "L", "+430", 62, "", ["vs Early"], """0 HR, 88.3 mph EV. Early LHB split -0.32, HR risk 0.31. slight split headwind (-0.32); park suppresses carry (-8%)."""),
        ],
    },
    {
        "title": "PHI @ WSH - Cristopher Sanchez (L, PHI) vs Cade Cavalli (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Sanchez (HR risk -0.29, vs LHB -1.19, vs RHB +0.03). Cavalli (HR risk -0.52, vs LHB -0.37, vs RHB -0.18).",
        "rows": [
            row("James Wood", "L", "+600", 69, "", ["vs Sanchez"], """0 HR, 93.0 mph EV. Sanchez LHB split -1.19, HR risk -0.29. tough split lane (-1.19); pitcher risk below avg (-0.29).""", blast="good"),
            row("Luis Garcia Jr.", "L", "N/A", 78, "", ["vs Sanchez"], """1 HR, 1 near-HR, 95.8 mph EV. Sanchez LHB split -1.19, HR risk -0.29. tough split lane (-1.19); pitcher risk below avg (-0.29).""", blast="good"),
            row("CJ Abrams", "L", "+810", 70, "", ["vs Sanchez"], """1 HR, 1 near-HR, 87.9 mph EV. Sanchez LHB split -1.19, HR risk -0.29. tough split lane (-1.19); pitcher risk below avg (-0.29).""", blast="good"),
            row("Curtis Mead", "R", "+568", 81, "🌕 💣", ["vs Sanchez"], """2 HR, 3 near-HR, 88.6 mph EV. Sanchez RHB split +0.03, HR risk -0.29. pitcher risk below avg (-0.29).""", blast="high"),
            row("Kyle Schwarber", "L", "+200", 88, "⭐ 🌕 💣", ["vs Cavalli"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.2 mph EV. Cavalli LHB split -0.37, HR risk -0.52. slight split headwind (-0.37); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Bryce Harper", "L", "+411", 72, "", ["vs Cavalli"], """1 HR, 1 near-HR, 90.5 mph EV. Cavalli LHB split -0.37, HR risk -0.52. slight split headwind (-0.37); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Edmundo Sosa", "R", "N/A", 74, "", ["vs Cavalli"], """1 HR, 2 near-HR, 90.2 mph EV. Cavalli RHB split -0.18, HR risk -0.52. slight split headwind (-0.18); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Brandon Marsh", "L", "+630", 62, "", ["vs Cavalli"], """0 HR, 83.5 mph EV. Cavalli LHB split -0.37, HR risk -0.52. slight split headwind (-0.37); pitcher suppresses HR (-0.52)."""),
        ],
    },
    {
        "title": "SEA @ PIT - Bryce Miller (R, SEA) vs Bubba Chandler (R, PIT)",
        "description": "Tail key data: Park boost -4% (stadium -13%, weather +9%). Miller (HR risk -0.02, vs LHB -0.82, vs RHB +1.09). Chandler (HR risk -0.60, vs LHB +0.59, vs RHB -1.30).",
        "rows": [
            row("Bryan Reynolds", "S", "+559", 98, "🌕 💣", ["vs Miller"], """3 HR, 6 near-HR, 97.1 mph EV. Miller RHB split +1.09, HR risk -0.02. pitcher risk below avg (-0.02); park suppresses carry (-13%).""", blast="high"),
            row("Esmerlyn Valdez", "R", "N/A", 72, "💎", ["vs Miller"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 87.9 mph EV. Miller RHB split +1.09, HR risk -0.02. pitcher risk below avg (-0.02); park suppresses carry (-13%).""", blast="good"),
            row("Marcell Ozuna", "R", "+308", 74, "⭐", ["vs Miller"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.6 mph EV. Miller RHB split +1.09, HR risk -0.02. pitcher risk below avg (-0.02); park suppresses carry (-13%).""", blast="good"),
            row("Ryan O'Hearn", "L", "+620", 68, "", ["vs Miller"], """0 HR, 2 near-HR, 87.8 mph EV. Miller LHB split -0.82, HR risk -0.02. tough split lane (-0.82); pitcher risk below avg (-0.02).""", blast="good"),
            row("Endy Rodriguez", "S", "N/A", 87, "🌕 💣", ["vs Miller"], """2 HR, 2 near-HR, 97.1 mph EV. Miller RHB split +1.09, HR risk -0.02. pitcher risk below avg (-0.02); park suppresses carry (-13%).""", blast="high"),
            row("Henry Davis", "R", "+770", 80, "🌕 💣 💎", ["vs Miller"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 80.3 mph EV. Miller RHB split +1.09, HR risk -0.02. pitcher risk below avg (-0.02); park suppresses carry (-13%).""", blast="high"),
            row("Randy Arozarena", "R", "+750", 79, "💎", ["vs Chandler"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 94.9 mph EV. Chandler RHB split -1.30, HR risk -0.60. tough split lane (-1.30); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Luke Raley", "L", "+552", 80, "", ["vs Chandler"], """1 HR, 2 near-HR, 96.0 mph EV. Chandler LHB split +0.59, HR risk -0.60. pitcher suppresses HR (-0.60); park suppresses carry (-13%).""", blast="good"),
            row("Dominic Canzone", "L", "+443", 78, "🌕 💣", ["vs Chandler"], """2 HR, 2 near-HR, 88.0 mph EV. Chandler LHB split +0.59, HR risk -0.60. pitcher suppresses HR (-0.60); park suppresses carry (-13%).""", blast="high"),
        ],
    },
    {
        "title": "TEX @ TOR - MacKenzie Gore (L, TEX) vs Kevin Gausman (R, TOR)",
        "description": "Tail key data: Park boost +1% (stadium +6%, weather -5%). Gore (HR risk -0.12, vs LHB -0.49, vs RHB +0.12). Gausman (HR risk 0.10, vs LHB -0.06, vs RHB +0.60).",
        "rows": [
            row("George Springer", "R", "+350", 73, "⭐", ["vs Gore"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 89.4 mph EV. Gore RHB split +0.12, HR risk -0.12. pitcher risk below avg (-0.12); weather carry headwind (-5%).""", blast="good"),
            row("Kazuma Okamoto", "R", "+331", 64, "", ["vs Gore"], """0 HR, 90.2 mph EV. Gore RHB split +0.12, HR risk -0.12. pitcher risk below avg (-0.12); weather carry headwind (-5%)."""),
            row("Alejandro Kirk", "R", "+579", 62, "", ["vs Gore"], """0 HR, 85.9 mph EV. Gore RHB split +0.12, HR risk -0.12. pitcher risk below avg (-0.12); weather carry headwind (-5%)."""),
            row("Brandon Nimmo", "L", "+530", 77, "", ["vs Gausman"], """0 HR, 1 near-HR, 98.9 mph EV. Gausman LHB split -0.06, HR risk 0.10. slight split headwind (-0.06); weather carry headwind (-5%).""", blast="good"),
            row("Jarred Kelenic", "L", "N/A", 70, "", ["vs Gausman"], """0 HR, 93.9 mph EV. Gausman LHB split -0.06, HR risk 0.10. slight split headwind (-0.06); weather carry headwind (-5%).""", blast="good"),
            row("Joc Pederson", "L", "+487", 73, "", ["vs Gausman"], """1 HR, 1 near-HR, 91.1 mph EV. Gausman LHB split -0.06, HR risk 0.10. slight split headwind (-0.06); weather carry headwind (-5%).""", blast="good"),
            row("Wyatt Langford", "R", "+470", 78, "🌕 💣", ["vs Gausman"], """2 HR, 2 near-HR, 86.2 mph EV. Gausman RHB split +0.60, HR risk 0.10. weather carry headwind (-5%); lighter EV form (86.2 mph).""", blast="high"),
            row("Kyle Higashioka", "R", "+890", 64, "", ["vs Gausman"], """0 HR, 90.5 mph EV. Gausman RHB split +0.60, HR risk 0.10. weather carry headwind (-5%); limited recent HR events."""),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-25")

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

    out = ROOT / '_games-0625.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
