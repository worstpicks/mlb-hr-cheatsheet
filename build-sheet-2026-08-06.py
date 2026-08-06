#!/usr/bin/env python3
"""Generate games[] block for 2026-08-06 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Eugenio Suarez (R)",
    "Gunnar Henderson (L)",
    "J.T. Realmuto (R)",
    "Jake Bauers (L)",
    "Pete Crow-Armstrong (L)",
    "Rhys Hoskins (R)",
    "Spencer Torkelson (R)",
    "Willson Contreras (R)",
    "Wilyer Abreu (L)",
}

GEMS = {
    "Brandon Lowe (L)",
    "Coby Mayo (R)",
    "Derek Hill (R)",
    "Dillon Dingler (R)",
    "Drake Baldwin (L)",
    "Esmerlyn Valdez (R)",
    "Hao-Yu Lee (R)",
    "Jo Adell (R)",
    "Josh Bell (S)",
    "Mike Yastrzemski (L)",
    "Munetaka Murakami (L)",
    "Ronald Acuna Jr. (R)",
    "Sal Stewart (R)",
    "Travis d'Arnaud (R)",
}

PLAYER_TEAMS = {
    "Andrew Vaughn (R)": "MIL",
    "Bo Bichette (R)": "NYM",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Lowe (L)": "PIT",
    "Brice Turang (L)": "MIL",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Coby Mayo (R)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Daylen Lile (L)": "WSH",
    "Derek Hill (R)": "PHI",
    "Dillon Dingler (R)": "DET",
    "Drake Baldwin (L)": "ATL",
    "Dylan Crews (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Endy Rodriguez (S)": "PIT",
    "Ernie Clement (R)": "TOR",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Freddy Fermin (R)": "SD",
    "Geraldo Perdomo (S)": "ARI",
    "Gunnar Henderson (L)": "BAL",
    "Hao-Yu Lee (R)": "DET",
    "Heriberto Hernandez (R)": "MIA",
    "J.T. Realmuto (R)": "PHI",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jacob Gonzalez (L)": "PIT",
    "Jake Bauers (L)": "MIL",
    "Javier Sanoja (R)": "MIA",
    "Jo Adell (R)": "CLE",
    "Jonah Heim (S)": "ATH",
    "Josh Bell (S)": "MIN",
    "Josh Lowe (L)": "LAA",
    "Julio Rodriguez (R)": "SEA",
    "Kazuma Okamoto (R)": "TOR",
    "Kyle Schwarber (L)": "PHI",
    "Lawrence Butler (L)": "ATH",
    "Luis Arraez (L)": "PHI",
    "Luis Torrens (R)": "NYM",
    "Manny Machado (R)": "SD",
    "Marcus Semien (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Mike Yastrzemski (L)": "ATL",
    "Munetaka Murakami (L)": "CWS",
    "Patrick Bailey (S)": "CLE",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Randy Arozarena (R)": "SEA",
    "Rhys Hoskins (R)": "CLE",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Sal Stewart (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Seiya Suzuki (R)": "CHC",
    "Spencer Torkelson (R)": "DET",
    "Sung-Mun Song (L)": "SD",
    "Travis d'Arnaud (R)": "LAA",
    "Tyler Soderstrom (L)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "Tyler Tolbert (R)": "KC",
    "Tyrone Taylor (R)": "CHC",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "William Contreras (R)": "MIL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
}

BUM_MATCHUPS = {
    ("LAA @ BAL", "Johnson"),
    ("SD @ ARI", "Drake"),
    ("WSH @ PHI", "Mikolas"),
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
        "title": "ATH @ CIN - Mason Barnett (R, ATH) vs Andrew Abbott (L, CIN)",
        "description": "Tail key data: Park boost +17% (stadium +15%, weather +3%). Barnett (HR risk -0.08, vs LHB -0.89, vs RHB +1.01). Abbott (HR risk -0.61, vs LHB -0.31, vs RHB -0.36).",
        "rows": [
            row("Eugenio Suarez", "R", "+360", 82, "⭐ 🌕 💣", ["vs Barnett"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.6 mph EV. Barnett RHB split +1.01, HR risk -0.08. pitcher risk below avg (-0.08).""", blast="high"),
            row("Sal Stewart", "R", "+320", 83, "🌕 💣 💎", ["vs Barnett"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.1 mph EV. Barnett RHB split +1.01, HR risk -0.08. pitcher risk below avg (-0.08).""", blast="high"),
            row("Elly De La Cruz", "S", "+310", 73, "", ["vs Barnett"], """1 HR, 1 near-HR, 93.2 mph EV. Barnett SHB→RHB split +1.01, HR risk -0.08. pitcher risk below avg (-0.08).""", blast="good"),
            row("Tyler Stephenson", "R", "+412", 71, "", ["vs Barnett"], """1 HR, 1 near-HR, 91.3 mph EV. Barnett RHB split +1.01, HR risk -0.08. pitcher risk below avg (-0.08).""", blast="good"),
            row("Tyler Soderstrom", "L", "+330", 58, "", ["vs Abbott"], """0 HR, 1 near-HR, 95.2 mph EV. Abbott LHB split -0.31, HR risk -0.61. slight split headwind (-0.31); pitcher suppresses HR (-0.61).""", blast="good"),
            row("Jonah Heim", "S", "+472", 75, "🌕 💣", ["vs Abbott"], """2 HR, 3 near-HR, 96.2 mph EV. Abbott SHB→LHB split -0.31, HR risk -0.61. slight split headwind (-0.31); pitcher suppresses HR (-0.61).""", blast="high"),
            row("Lawrence Butler", "L", "+424", 58, "", ["vs Abbott"], """1 HR, 1 near-HR, 82.8 mph EV. Abbott LHB split -0.31, HR risk -0.61. slight split headwind (-0.31); pitcher suppresses HR (-0.61).""", blast="good"),
        ],
    },
    {
        "title": "CWS @ BOS - Luis Castillo (R, CWS) vs Ranger Suarez (L, BOS)",
        "description": "Tail key data: Park boost data unavailable. Castillo (HR risk 0.66, vs LHB +0.81, vs RHB -0.40). Suarez (HR risk -1.47, vs LHB -0.33, vs RHB -1.41).",
        "rows": [
            row("Wilyer Abreu", "L", "+310", 92, "⭐ 🌕 💣", ["vs Castillo"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 93.8 mph EV. Castillo LHB split +0.81, HR risk 0.66.""", blast="high"),
            row("Willson Contreras", "R", "+360", 58, "⭐", ["vs Castillo"], """Worst Pickz Favorite. 0 HR, 89.0 mph EV. Castillo RHB split -0.40, HR risk 0.66. tough split lane (-0.40); limited recent HR events."""),
            row("Munetaka Murakami", "L", "+416", 58, "💎", ["vs Suarez"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 90.0 mph EV. Suarez LHB split -0.33, HR risk -1.47. slight split headwind (-0.33); pitcher suppresses HR (-1.47)."""),
            row("Miguel Vargas", "R", "+425", 58, "", ["vs Suarez"], """0 HR, 97.3 mph EV. Suarez RHB split -1.41, HR risk -1.47. tough split lane (-1.41); pitcher suppresses HR (-1.47).""", blast="good"),
        ],
    },
    {
        "title": "DET @ SEA - Framber Valdez (L, DET) vs Bryce Miller (R, SEA)",
        "description": "Tail key data: Park boost +12% (stadium +0%, weather +13%). Valdez (HR risk -0.65, vs LHB -0.94, vs RHB -0.24). Miller (HR risk -0.00, vs LHB -0.16, vs RHB +0.16).",
        "rows": [
            row("Randy Arozarena", "R", "+522", 58, "", ["vs Valdez"], """0 HR, 95.1 mph EV. Valdez RHB split -0.24, HR risk -0.65. slight split headwind (-0.24); pitcher suppresses HR (-0.65).""", blast="good"),
            row("Cal Raleigh", "S", "+400", 58, "", ["vs Valdez"], """0 HR, 89.3 mph EV. Valdez SHB→RHB split -0.24, HR risk -0.65. slight split headwind (-0.24); pitcher suppresses HR (-0.65)."""),
            row("Julio Rodriguez", "R", "+531", 58, "", ["vs Valdez"], """0 HR, 1 near-HR, 90.8 mph EV. Valdez RHB split -0.24, HR risk -0.65. slight split headwind (-0.24); pitcher suppresses HR (-0.65)."""),
            row("Spencer Torkelson", "R", "+424", 84, "⭐ 🌕 💣", ["vs Miller"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 97.5 mph EV. Miller RHB split +0.16, HR risk -0.00.""", blast="high"),
            row("Dillon Dingler", "R", "+466", 61, "💎", ["vs Miller"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 88.3 mph EV. Miller RHB split +0.16, HR risk -0.00.""", blast="good"),
            row("Hao-Yu Lee", "R", "N/A", 67, "💎", ["vs Miller"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.1 mph EV. Miller RHB split +0.16, HR risk -0.00.""", blast="good"),
        ],
    },
    {
        "title": "LAA @ BAL - Ryan Johnson 🧤 (R, LAA) vs Brandon Young (R, BAL)",
        "description": "Tail key data: Park boost +9% (stadium -5%, weather +13%). Johnson 🧤 (HR risk 1.35, vs LHB +1.05, vs RHB +0.74). Young (HR risk -0.11, vs LHB -0.35, vs RHB +0.29).",
        "rows": [
            row("Coby Mayo", "R", "+377", 88, "🌕 💣 💎", ["vs Johnson"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.1 mph EV. Johnson RHB split +0.74, HR risk 1.35.""", blast="good"),
            row("Gunnar Henderson", "L", "+370", 88, "⭐ 🌕 💣", ["vs Johnson"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.8 mph EV. Johnson LHB split +1.05, HR risk 1.35. limited recent HR events.""", blast="good"),
            row("Pete Alonso", "R", "+304", 84, "", ["vs Johnson"], """0 HR, 95.4 mph EV. Johnson RHB split +0.74, HR risk 1.35. limited recent HR events.""", blast="good"),
            row("Travis d'Arnaud", "R", "N/A", 62, "💎", ["vs Young"], """Worst Pickz Hidden Gem. 0 HR, 95.3 mph EV. Young RHB split +0.29, HR risk -0.11. pitcher risk below avg (-0.11); limited recent HR events.""", blast="good"),
            row("Josh Lowe", "L", "+640", 58, "", ["vs Young"], """0 HR, 1 near-HR, 84.3 mph EV. Young LHB split -0.35, HR risk -0.11. slight split headwind (-0.35); pitcher risk below avg (-0.11)."""),
            row("Mike Trout", "R", "+357", 58, "", ["vs Young"], """0 HR, 84.6 mph EV. Young RHB split +0.29, HR risk -0.11. pitcher risk below avg (-0.11); limited recent HR events."""),
        ],
    },
    {
        "title": "MIA @ ATL - Janson Junk (R, MIA) vs Martin Perez (L, ATL)",
        "description": "Tail key data: Park boost +2% (stadium -2%, weather +4%). Junk (HR risk -0.14, vs LHB -0.22, vs RHB +0.06). Perez (HR risk -0.28, vs LHB +0.13, vs RHB -0.37).",
        "rows": [
            row("Mike Yastrzemski", "L", "+620", 76, "🌕 💣 💎", ["vs Junk"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 95.7 mph EV. Junk LHB split -0.22, HR risk -0.14. slight split headwind (-0.22); pitcher risk below avg (-0.14).""", blast="high"),
            row("Matt Olson", "L", "+325", 60, "", ["vs Junk"], """1 HR, 2 near-HR, 92.7 mph EV. Junk LHB split -0.22, HR risk -0.14. slight split headwind (-0.22); pitcher risk below avg (-0.14).""", blast="good"),
            row("Drake Baldwin", "L", "+416", 64, "💎", ["vs Junk"], """Worst Pickz Hidden Gem. 0 HR, 3 near-HR, 98.8 mph EV. Junk LHB split -0.22, HR risk -0.14. slight split headwind (-0.22); pitcher risk below avg (-0.14).""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+404", 58, "💎", ["vs Junk"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.1 mph EV. Junk RHB split +0.06, HR risk -0.14. pitcher risk below avg (-0.14); limited recent HR events.""", blast="good"),
            row("Heriberto Hernandez", "R", "+434", 65, "🌕 💣", ["vs Perez"], """2 HR, 2 near-HR, 91.8 mph EV. Perez RHB split -0.37, HR risk -0.28. slight split headwind (-0.37); pitcher risk below avg (-0.28).""", blast="high"),
            row("Javier Sanoja", "R", "+1000", 58, "", ["vs Perez"], """1 HR, 1 near-HR, 87.3 mph EV. Perez RHB split -0.37, HR risk -0.28. slight split headwind (-0.37); pitcher risk below avg (-0.28).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ KC - Bailey Ober (R, MIN) vs Michael Wacha (R, KC)",
        "description": "Tail key data: Park boost +19% (stadium +12%, weather +7%). Ober (HR risk 0.62, vs LHB +0.43, vs RHB +0.25). Wacha (HR risk 0.14, vs LHB -0.54, vs RHB +1.27).",
        "rows": [
            row("Salvador Perez", "R", "+384", 85, "🌕 💣", ["vs Ober"], """1 HR, 4 near-HR, 89.8 mph EV. Ober RHB split +0.25, HR risk 0.62.""", blast="high"),
            row("Bobby Witt Jr.", "R", "+360", 69, "", ["vs Ober"], """0 HR, 2 near-HR, 87.9 mph EV. Ober RHB split +0.25, HR risk 0.62. lighter EV form (87.9 mph).""", blast="good"),
            row("Jac Caglianone", "L", "+352", 74, "", ["vs Ober"], """1 HR, 1 near-HR, 88.5 mph EV. Ober LHB split +0.43, HR risk 0.62.""", blast="good"),
            row("Tyler Tolbert", "R", "N/A", 76, "", ["vs Ober"], """1 HR, 3 near-HR, 76.3 mph EV. Ober RHB split +0.25, HR risk 0.62. lighter EV form (76.3 mph).""", blast="good"),
            row("Josh Bell", "S", "+569", 80, "💎", ["vs Wacha"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.7 mph EV. Wacha SHB→RHB split +1.27, HR risk 0.14.""", blast="good"),
            row("Royce Lewis", "R", "+425", 75, "", ["vs Wacha"], """0 HR, 99.2 mph EV. Wacha RHB split +1.27, HR risk 0.14. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "NYM @ CLE - Nolan McLean (R, NYM) vs Foster Griffin (L, CLE)",
        "description": "Tail key data: Park boost -1% (stadium -4%, weather +2%). McLean (HR risk -0.42, vs LHB -0.33, vs RHB -0.66). Griffin (HR risk -0.41, vs LHB +0.40, vs RHB -0.48).",
        "rows": [
            row("Rhys Hoskins", "R", "N/A", 63, "⭐ 🌕 💣", ["vs McLean"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.7 mph EV. McLean RHB split -0.66, HR risk -0.42. tough split lane (-0.66); pitcher suppresses HR (-0.42).""", blast="high"),
            row("Patrick Bailey", "S", "+1000", 66, "🌕 💣", ["vs McLean"], """2 HR, 2 near-HR, 94.5 mph EV. McLean SHB→LHB split -0.33, HR risk -0.42. slight split headwind (-0.33); pitcher suppresses HR (-0.42).""", blast="high"),
            row("Jo Adell", "R", "+630", 58, "💎", ["vs McLean"], """Worst Pickz Hidden Gem. 0 HR, 94.7 mph EV. McLean RHB split -0.66, HR risk -0.42. tough split lane (-0.66); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Luis Torrens", "R", "+1020", 62, "🌕 💣", ["vs Griffin"], """2 HR, 2 near-HR, 91.7 mph EV. Griffin RHB split -0.48, HR risk -0.41. tough split lane (-0.48); pitcher suppresses HR (-0.41).""", blast="high"),
            row("Bo Bichette", "R", "+740", 58, "", ["vs Griffin"], """1 HR, 1 near-HR, 89.0 mph EV. Griffin RHB split -0.48, HR risk -0.41. tough split lane (-0.48); pitcher suppresses HR (-0.41).""", blast="good"),
            row("Marcus Semien", "R", "+750", 58, "", ["vs Griffin"], """1 HR, 2 near-HR, 89.4 mph EV. Griffin RHB split -0.48, HR risk -0.41. tough split lane (-0.48); pitcher suppresses HR (-0.41).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ MIL - Braxton Ashcraft (R, PIT) vs Dustin May (R, MIL)",
        "description": "Tail key data: Park boost +16% (stadium +11%, weather +5%). Ashcraft (HR risk 0.18, vs LHB +0.43, vs RHB -0.72). May (HR risk -0.98, vs LHB -0.70, vs RHB -0.70).",
        "rows": [
            row("Jake Bauers", "L", "+390", 88, "⭐ 🌕 💣", ["vs Ashcraft"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 99.2 mph EV. Ashcraft LHB split +0.43, HR risk 0.18.""", blast="high"),
            row("Jackson Chourio", "R", "+475", 65, "", ["vs Ashcraft"], """1 HR, 1 near-HR, 97.8 mph EV. Ashcraft RHB split -0.72, HR risk 0.18. tough split lane (-0.72).""", blast="good"),
            row("Brice Turang", "L", "+630", 64, "", ["vs Ashcraft"], """1 HR, 1 near-HR, 81.3 mph EV. Ashcraft LHB split +0.43, HR risk 0.18. lighter EV form (81.3 mph).""", blast="good"),
            row("William Contreras", "R", "+580", 62, "", ["vs Ashcraft"], """1 HR, 1 near-HR, 92.7 mph EV. Ashcraft RHB split -0.72, HR risk 0.18. tough split lane (-0.72).""", blast="good"),
            row("Andrew Vaughn", "R", "+730", 62, "", ["vs Ashcraft"], """1 HR, 1 near-HR, 92.8 mph EV. Ashcraft RHB split -0.72, HR risk 0.18. tough split lane (-0.72).""", blast="good"),
            row("Brandon Lowe", "L", "+361", 58, "💎", ["vs May"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.5 mph EV. May LHB split -0.70, HR risk -0.98. tough split lane (-0.70); pitcher suppresses HR (-0.98).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+441", 58, "💎", ["vs May"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.2 mph EV. May RHB split -0.70, HR risk -0.98. tough split lane (-0.70); pitcher suppresses HR (-0.98).""", blast="good"),
            row("Jacob Gonzalez", "L", "+920", 58, "", ["vs May"], """1 HR, 1 near-HR, 93.2 mph EV. May LHB split -0.70, HR risk -0.98. tough split lane (-0.70); pitcher suppresses HR (-0.98).""", blast="good"),
            row("Endy Rodriguez", "S", "+690", 58, "", ["vs May"], """1 HR, 1 near-HR, 93.2 mph EV. May SHB→LHB split -0.70, HR risk -0.98. tough split lane (-0.70); pitcher suppresses HR (-0.98).""", blast="good"),
        ],
    },
    {
        "title": "SD @ ARI - Walker Buehler (R, SD) vs Kohl Drake 🧤 (L, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Buehler (HR risk 0.47, vs LHB +0.25, vs RHB +0.33). Drake 🧤 (HR risk 1.71, vs LHB +2.06, vs RHB +0.95).",
        "rows": [
            row("Corbin Carroll", "L", "+465", 66, "", ["vs Buehler"], """0 HR, 95.9 mph EV. Buehler LHB split +0.25, HR risk 0.47. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Geraldo Perdomo", "S", "+1040", 58, "", ["vs Buehler"], """0 HR, 1 near-HR, 88.0 mph EV. Buehler SHB→RHB split +0.33, HR risk 0.47. park/weather net drag (-8%); limited recent HR events."""),
            row("Manny Machado", "R", "+350", 79, "", ["vs Drake"], """0 HR, 92.7 mph EV. Drake RHB split +0.95, HR risk 1.71. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
            row("Freddy Fermin", "R", "N/A", 73, "", ["vs Drake"], """0 HR, 90.0 mph EV. Drake RHB split +0.95, HR risk 1.71. park/weather net drag (-8%); limited recent HR events."""),
            row("Sung-Mun Song", "L", "N/A", 87, "", ["vs Drake"], """0 HR, 93.3 mph EV. Drake LHB split +2.06, HR risk 1.71. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TOR @ CHC - Dylan Cease (R, TOR) vs David Peterson (L, CHC)",
        "description": "Tail key data: Park boost +10% (stadium -4%, weather +14%). Cease (HR risk -1.01, vs LHB -0.48, vs RHB -1.29). Peterson (HR risk -0.24, vs LHB +0.22, vs RHB -0.37).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+483", 58, "⭐", ["vs Cease"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.2 mph EV. Cease LHB split -0.48, HR risk -1.01. tough split lane (-0.48); pitcher suppresses HR (-1.01).""", blast="good"),
            row("Seiya Suzuki", "R", "+579", 58, "", ["vs Cease"], """0 HR, 88.5 mph EV. Cease RHB split -1.29, HR risk -1.01. tough split lane (-1.29); pitcher suppresses HR (-1.01)."""),
            row("Tyrone Taylor", "R", "N/A", 58, "🌕 💣", ["vs Cease"], """2 HR, 2 near-HR, 88.6 mph EV. Cease RHB split -1.29, HR risk -1.01. tough split lane (-1.29); pitcher suppresses HR (-1.01).""", blast="high"),
            row("Ernie Clement", "R", "+1040", 58, "", ["vs Peterson"], """1 HR, 1 near-HR, 86.0 mph EV. Peterson RHB split -0.37, HR risk -0.24. slight split headwind (-0.37); pitcher risk below avg (-0.24).""", blast="good"),
            row("Kazuma Okamoto", "R", "+442", 58, "", ["vs Peterson"], """0 HR, 92.5 mph EV. Peterson RHB split -0.37, HR risk -0.24. slight split headwind (-0.37); pitcher risk below avg (-0.24).""", blast="good"),
            row("Vladimir Guerrero Jr.", "R", "+525", 58, "", ["vs Peterson"], """0 HR, 93.1 mph EV. Peterson RHB split -0.37, HR risk -0.24. slight split headwind (-0.37); pitcher risk below avg (-0.24).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ PHI - Miles Mikolas 🧤 (R, WSH) vs Cristopher Sanchez (L, PHI)",
        "description": "Tail key data: Park boost data unavailable. Mikolas 🧤 (HR risk 1.64, vs LHB +0.83, vs RHB +1.57). Sanchez (HR risk -0.36, vs LHB -1.37, vs RHB +0.38).",
        "rows": [
            row("Derek Hill", "R", "N/A", 95, "🌕 💣 💎", ["vs Mikolas"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.2 mph EV. Mikolas RHB split +1.57, HR risk 1.64.""", blast="high"),
            row("J.T. Realmuto", "R", "+580", 93, "⭐ 🌕 💣", ["vs Mikolas"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 98.5 mph EV. Mikolas RHB split +1.57, HR risk 1.64.""", blast="good"),
            row("Bryce Harper", "L", "+290", 83, "", ["vs Mikolas"], """1 HR, 1 near-HR, 90.3 mph EV. Mikolas LHB split +0.83, HR risk 1.64.""", blast="good"),
            row("Bryson Stott", "L", "+520", 84, "", ["vs Mikolas"], """0 HR, 96.6 mph EV. Mikolas LHB split +0.83, HR risk 1.64. limited recent HR events.""", blast="good"),
            row("Kyle Schwarber", "L", "+216", 83, "", ["vs Mikolas"], """0 HR, 95.5 mph EV. Mikolas LHB split +0.83, HR risk 1.64. limited recent HR events.""", blast="good"),
            row("Luis Arraez", "L", "+1060", 86, "", ["vs Mikolas"], """1 HR, 1 near-HR, 93.0 mph EV. Mikolas LHB split +0.83, HR risk 1.64.""", blast="good"),
            row("Daylen Lile", "L", "+1000", 58, "", ["vs Sanchez"], """1 HR, 1 near-HR, 91.6 mph EV. Sanchez LHB split -1.37, HR risk -0.36. tough split lane (-1.37); pitcher risk below avg (-0.36).""", blast="good"),
            row("Dylan Crews", "R", "+600", 58, "", ["vs Sanchez"], """0 HR, 1 near-HR, 92.2 mph EV. Sanchez RHB split +0.38, HR risk -0.36. pitcher risk below avg (-0.36); limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-06")

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

    out = ROOT / '_games-0806.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
