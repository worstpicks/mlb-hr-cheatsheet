#!/usr/bin/env python3
"""Generate games[] block for 2026-08-11 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Bryce Harper (L)",
    "Cal Raleigh (S)",
    "Dillon Dingler (R)",
    "Dylan Crews (R)",
    "Ian Happ (S)",
    "JJ Bleday (L)",
    "Jake Bauers (L)",
    "Jo Adell (R)",
    "Joc Pederson (L)",
    "Jordan Walker (R)",
    "Jose Siri (R)",
    "Lars Nootbaar (L)",
    "Matt Olson (L)",
    "Munetaka Murakami (L)",
    "Owen Caissie (L)",
    "Pete Alonso (R)",
    "Spencer Torkelson (R)",
}

GEMS = {
    "Andres Chaparro (R)",
    "Ben Rice (L)",
    "Brady House (R)",
    "Carter Jensen (L)",
    "Coby Mayo (R)",
    "Dominic Canzone (L)",
    "Francisco Lindor (S)",
    "Ivan Herrera (R)",
    "Jac Caglianone (L)",
    "Jase Bowen (R)",
    "Jung Hoo Lee (L)",
    "Ketel Marte (S)",
    "Lawrence Butler (L)",
    "Miguel Amaya (R)",
    "Ronald Acuna Jr. (R)",
    "Royce Lewis (R)",
}

PLAYER_TEAMS = {
    "A.J. Ewing (L)": "NYM",
    "Alec Burleson (L)": "STL",
    "Andres Chaparro (R)": "WSH",
    "Ben Rice (L)": "NYY",
    "Brady House (R)": "WSH",
    "Brandon Lowe (L)": "PIT",
    "Brice Turang (L)": "MIL",
    "Bryce Harper (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Cam Smith (R)": "HOU",
    "Carter Jensen (L)": "KC",
    "Christian Walker (R)": "HOU",
    "Coby Mayo (R)": "BAL",
    "Cole Carrigg (S)": "COL",
    "Connor Norby (R)": "COL",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Dylan Crews (R)": "WSH",
    "Endy Rodriguez (S)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Ezequiel Tovar (R)": "COL",
    "Francisco Lindor (S)": "NYM",
    "Gary Sanchez (R)": "MIL",
    "Gavin Sheets (L)": "SD",
    "Ian Happ (S)": "CHC",
    "Ivan Herrera (R)": "STL",
    "J.T. Realmuto (R)": "PHI",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "Jackson Holliday (L)": "BAL",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jake Rogers (R)": "BOS",
    "Jakob Marsee (L)": "MIA",
    "Jarren Duran (L)": "BOS",
    "Jase Bowen (R)": "SD",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jo Adell (R)": "CLE",
    "Joc Pederson (L)": "TEX",
    "John Rave (L)": "KC",
    "Jordan Walker (R)": "STL",
    "Jose Siri (R)": "LAA",
    "Josh Bell (S)": "MIN",
    "Jung Hoo Lee (L)": "SF",
    "Junior Caminero (R)": "TB",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Lars Nootbaar (L)": "ARI",
    "Lawrence Butler (L)": "ATH",
    "Leody Taveras (S)": "BAL",
    "Luis Garcia Jr. (L)": "NYY",
    "Marcus Semien (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Michael Busch (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Miguel Amaya (R)": "CHC",
    "Moises Ballesteros (L)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Nathaniel Lowe (L)": "CLE",
    "Nolan Schanuel (L)": "LAA",
    "Owen Caissie (L)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Rhys Hoskins (R)": "CLE",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Salvador Perez (R)": "KC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Torkelson (R)": "DET",
    "Teoscar Hernandez (R)": "LAD",
    "Tyler Soderstrom (L)": "ATH",
    "Tyler Stephenson (R)": "CIN",
    "Victor Mesa Jr. (L)": "TB",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Willson Contreras (R)": "BOS",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("COL @ ARI", "Sugano"),
    ("TB @ ATH", "Barnett"),
    ("TEX @ LAA", "Johnson"),
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
        "title": "BAL @ MIN - Brandon Young (R, BAL) vs Bailey Ober (R, MIN)",
        "description": "Tail key data: Park boost +1% (stadium -7%, weather +8%). Young (HR risk 0.45, vs LHB -0.13, vs RHB +0.77). Ober (HR risk 0.28, vs LHB +0.01, vs RHB +0.46).",
        "rows": [
            row("Kody Clemens", "L", "+376", 72, "", ["vs Young"], """1 HR, 2 near-HR, 97.8 mph EV. Young LHB split -0.13, HR risk 0.45. slight split headwind (-0.13); park suppresses carry (-7%).""", blast="good"),
            row("Josh Bell", "S", "+420", 73, "", ["vs Young"], """1 HR, 1 near-HR, 91.5 mph EV. Young SHB→RHB split +0.77, HR risk 0.45. park suppresses carry (-7%).""", blast="good"),
            row("Royce Lewis", "R", "+350", 78, "💎", ["vs Young"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.2 mph EV. Young RHB split +0.77, HR risk 0.45. park suppresses carry (-7%).""", blast="good"),
            row("Leody Taveras", "S", "+560", 67, "", ["vs Ober"], """1 HR, 2 near-HR, 91.0 mph EV. Ober SHB→RHB split +0.46, HR risk 0.28. park suppresses carry (-7%).""", blast="good"),
            row("Pete Alonso", "R", "+305", 69, "⭐", ["vs Ober"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 92.9 mph EV. Ober RHB split +0.46, HR risk 0.28. park suppresses carry (-7%).""", blast="good"),
            row("Jackson Holliday", "L", "+520", 64, "", ["vs Ober"], """1 HR, 1 near-HR, 92.3 mph EV. Ober LHB split +0.01, HR risk 0.28. park suppresses carry (-7%).""", blast="good"),
            row("Coby Mayo", "R", "+359", 66, "💎", ["vs Ober"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 93.1 mph EV. Ober RHB split +0.46, HR risk 0.28. park suppresses carry (-7%).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ TOR - Patrick Sandoval (L, BOS) vs Dylan Cease (R, TOR)",
        "description": "Tail key data: Park boost +8% (stadium +7%, weather +1%). Sandoval (HR risk -0.17, vs LHB +2.20, vs RHB -0.82). Cease (HR risk -0.73, vs LHB -0.19, vs RHB -1.06).",
        "rows": [
            row("Vladimir Guerrero Jr.", "R", "+630", 58, "", ["vs Sandoval"], """0 HR, 92.1 mph EV. Sandoval RHB split -0.82, HR risk -0.17. tough split lane (-0.82); pitcher risk below avg (-0.17).""", blast="good"),
            row("Jarren Duran", "L", "+630", 68, "🚀 🌕 💣", ["vs Cease"], """2 HR, 2 near-HR, 100.2 mph EV. Cease LHB split -0.19, HR risk -0.73. slight split headwind (-0.19); pitcher suppresses HR (-0.73).""", blast="high"),
            row("Willson Contreras", "R", "+548", 58, "", ["vs Cease"], """0 HR, 92.0 mph EV. Cease RHB split -1.06, HR risk -0.73. tough split lane (-1.06); pitcher suppresses HR (-0.73).""", blast="good"),
            row("Jake Rogers", "R", "N/A", 58, "", ["vs Cease"], """1 HR, 1 near-HR, 93.5 mph EV. Cease RHB split -1.06, HR risk -0.73. tough split lane (-1.06); pitcher suppresses HR (-0.73).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ WSH - Shota Imanaga (L, CHC) vs Jake Irvin (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Imanaga (HR risk 0.48, vs LHB +0.55, vs RHB +0.27). Irvin (HR risk 0.00, vs LHB +0.00, vs RHB +0.00).",
        "rows": [
            row("Andres Chaparro", "R", "+521", 91, "🌕 💣 💎", ["vs Imanaga"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 97.2 mph EV. Imanaga RHB split +0.27, HR risk 0.48.""", blast="high"),
            row("Brady House", "R", "+610", 83, "🌕 💣 💎", ["vs Imanaga"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.4 mph EV. Imanaga RHB split +0.27, HR risk 0.48.""", blast="high"),
            row("Dylan Crews", "R", "+480", 74, "⭐", ["vs Imanaga"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.7 mph EV. Imanaga RHB split +0.27, HR risk 0.48.""", blast="good"),
            row("Ian Happ", "S", "+420", 68, "⭐ 🌕 💣", ["vs Irvin"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.3 mph EV. Irvin SHB→LHB split +0.00, HR risk 0.00.""", blast="high"),
            row("Miguel Amaya", "R", "N/A", 66, "💎", ["vs Irvin"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 96.8 mph EV. Irvin RHB split +0.00, HR risk 0.00.""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+331", 58, "", ["vs Irvin"], """0 HR, 2 near-HR, 91.9 mph EV. Irvin LHB split +0.00, HR risk 0.00.""", blast="good"),
            row("Michael Busch", "L", "+360", 58, "", ["vs Irvin"], """0 HR, 94.7 mph EV. Irvin LHB split +0.00, HR risk 0.00. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CIN @ CWS - Nick Lodolo (L, CIN) vs Sean Burke (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Lodolo (HR risk -0.34, vs LHB -1.04, vs RHB +0.03). Burke (HR risk 0.07, vs LHB +0.47, vs RHB -0.71).",
        "rows": [
            row("Munetaka Murakami", "L", "+369", 58, "⭐", ["vs Lodolo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.6 mph EV. Lodolo LHB split -1.04, HR risk -0.34. tough split lane (-1.04); pitcher risk below avg (-0.34).""", blast="good"),
            row("Randal Grichuk", "R", "+545", 58, "", ["vs Lodolo"], """0 HR, 92.8 mph EV. Lodolo RHB split +0.03, HR risk -0.34. pitcher risk below avg (-0.34); limited recent HR events.""", blast="good"),
            row("Eugenio Suarez", "R", "+497", 73, "🌕 💣", ["vs Burke"], """2 HR, 3 near-HR, 95.2 mph EV. Burke RHB split -0.71, HR risk 0.07. tough split lane (-0.71).""", blast="high"),
            row("JJ Bleday", "L", "+457", 75, "⭐ 🌕 💣", ["vs Burke"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.4 mph EV. Burke LHB split +0.47, HR risk 0.07.""", blast="high"),
            row("Tyler Stephenson", "R", "+547", 60, "", ["vs Burke"], """1 HR, 1 near-HR, 96.5 mph EV. Burke RHB split -0.71, HR risk 0.07. tough split lane (-0.71).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ DET - Tanner Bibee (R, CLE) vs Drew Anderson (R, DET)",
        "description": "Tail key data: Park boost -4% (stadium -11%, weather +7%). Bibee (HR risk 0.10, vs LHB +0.34, vs RHB -0.58). Anderson (HR risk -0.40, vs LHB -0.50, vs RHB +0.30).",
        "rows": [
            row("Dillon Dingler", "R", "+435", 73, "⭐ 🌕 💣", ["vs Bibee"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 91.8 mph EV. Bibee RHB split -0.58, HR risk 0.10. tough split lane (-0.58); park suppresses carry (-11%).""", blast="high"),
            row("Spencer Torkelson", "R", "+390", 58, "⭐", ["vs Bibee"], """Worst Pickz Favorite. 0 HR, 94.9 mph EV. Bibee RHB split -0.58, HR risk 0.10. tough split lane (-0.58); park suppresses carry (-11%).""", blast="good"),
            row("Rhys Hoskins", "R", "N/A", 62, "", ["vs Anderson"], """1 HR, 1 near-HR, 96.1 mph EV. Anderson RHB split +0.30, HR risk -0.40. pitcher suppresses HR (-0.40); park suppresses carry (-11%).""", blast="good"),
            row("Jo Adell", "R", "+502", 58, "⭐", ["vs Anderson"], """Worst Pickz Favorite. 0 HR, 96.3 mph EV. Anderson RHB split +0.30, HR risk -0.40. pitcher suppresses HR (-0.40); park suppresses carry (-11%).""", blast="good"),
            row("Nathaniel Lowe", "L", "+540", 58, "", ["vs Anderson"], """1 HR, 2 near-HR, 99.2 mph EV. Anderson LHB split -0.50, HR risk -0.40. tough split lane (-0.50); pitcher suppresses HR (-0.40).""", blast="good"),
        ],
    },
    {
        "title": "COL @ ARI - Tomoyuki Sugano 🧤 (R, COL) vs Mitch Bratt (L, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Sugano 🧤 (HR risk 1.81, vs LHB +1.08, vs RHB +1.16). Bratt (HR risk 0.45, vs LHB +0.88, vs RHB +0.03).",
        "rows": [
            row("Lars Nootbaar", "L", "+540", 84, "⭐", ["vs Sugano"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 93.6 mph EV. Sugano LHB split +1.08, HR risk 1.81. park/weather net drag (-8%).""", blast="good"),
            row("Ketel Marte", "S", "+399", 72, "💎", ["vs Sugano"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 86.3 mph EV. Sugano SHB→RHB split +1.16, HR risk 1.81. park/weather net drag (-8%); limited recent HR events."""),
            row("Ezequiel Tovar", "R", "+800", 62, "", ["vs Bratt"], """1 HR, 1 near-HR, 88.6 mph EV. Bratt RHB split +0.03, HR risk 0.45. park/weather net drag (-8%).""", blast="good"),
            row("Cole Carrigg", "S", "+750", 70, "", ["vs Bratt"], """0 HR, 2 near-HR, 91.6 mph EV. Bratt SHB→LHB split +0.88, HR risk 0.45. park/weather net drag (-8%).""", blast="good"),
            row("Connor Norby", "R", "+441", 58, "", ["vs Bratt"], """0 HR, 1 near-HR, 89.8 mph EV. Bratt RHB split +0.03, HR risk 0.45. park/weather net drag (-8%); limited recent HR events."""),
        ],
    },
    {
        "title": "HOU @ SF - Hunter Brown (R, HOU) vs Carson Whisenhunt (L, SF)",
        "description": "Tail key data: Park boost -24% (stadium -15%, weather -9%). Brown (HR risk -0.12, vs LHB +0.52, vs RHB -1.06). Whisenhunt (HR risk 0.00, vs LHB +0.00, vs RHB +0.00).",
        "rows": [
            row("Jung Hoo Lee", "L", "+1480", 58, "💎", ["vs Brown"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.7 mph EV. Brown LHB split +0.52, HR risk -0.12. pitcher risk below avg (-0.12); park/weather net drag (-24%).""", blast="good"),
            row("Rafael Devers", "L", "+547", 71, "🌕 💣", ["vs Brown"], """2 HR, 2 near-HR, 94.7 mph EV. Brown LHB split +0.52, HR risk -0.12. pitcher risk below avg (-0.12); park/weather net drag (-24%).""", blast="high"),
            row("Cam Smith", "R", "+720", 59, "🌕 💣", ["vs Whisenhunt"], """2 HR, 2 near-HR, 85.2 mph EV. Whisenhunt RHB split +0.00, HR risk 0.00. park/weather net drag (-24%); lighter EV form (85.2 mph).""", blast="high"),
            row("Christian Walker", "R", "+486", 58, "", ["vs Whisenhunt"], """1 HR, 1 near-HR, 83.8 mph EV. Whisenhunt RHB split +0.00, HR risk 0.00. park/weather net drag (-24%); lighter EV form (83.8 mph).""", blast="good"),
            row("Yordan Alvarez", "L", "+353", 61, "", ["vs Whisenhunt"], """1 HR, 3 near-HR, 91.8 mph EV. Whisenhunt LHB split +0.00, HR risk 0.00. park/weather net drag (-24%).""", blast="good"),
        ],
    },
    {
        "title": "KC @ LAD - Michael Wacha (R, KC) vs Blake Snell (L, LAD)",
        "description": "Tail key data: Park boost +20% (stadium +18%, weather +2%). Wacha (HR risk 0.16, vs LHB -0.66, vs RHB +1.30). Snell (HR risk -2.16, vs LHB -0.69, vs RHB -1.45).",
        "rows": [
            row("Shohei Ohtani", "L", "+202", 58, "", ["vs Wacha"], """0 HR, 1 near-HR, 90.8 mph EV. Wacha LHB split -0.66, HR risk 0.16. tough split lane (-0.66); limited recent HR events."""),
            row("Teoscar Hernandez", "R", "+455", 73, "", ["vs Wacha"], """0 HR, 93.5 mph EV. Wacha RHB split +1.30, HR risk 0.16. limited recent HR events.""", blast="good"),
            row("John Rave", "L", "+701", 58, "🚀", ["vs Snell"], """0 HR, 1 near-HR, 102.8 mph EV. Snell LHB split -0.69, HR risk -2.16. tough split lane (-0.69); pitcher suppresses HR (-2.16).""", blast="good"),
            row("Salvador Perez", "R", "+475", 58, "", ["vs Snell"], """0 HR, 2 near-HR, 95.1 mph EV. Snell RHB split -1.45, HR risk -2.16. tough split lane (-1.45); pitcher suppresses HR (-2.16).""", blast="good"),
            row("Carter Jensen", "L", "+650", 58, "💎", ["vs Snell"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.8 mph EV. Snell LHB split -0.69, HR risk -2.16. tough split lane (-0.69); pitcher suppresses HR (-2.16).""", blast="good"),
            row("Jac Caglianone", "L", "+536", 58, "💎", ["vs Snell"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.2 mph EV. Snell LHB split -0.69, HR risk -2.16. tough split lane (-0.69); pitcher suppresses HR (-2.16).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ SD - Kyle Harrison (L, MIL) vs Walker Buehler (R, SD)",
        "description": "Tail key data: Park boost -1% (stadium -4%, weather +4%). Harrison (HR risk 0.20, vs LHB -0.46, vs RHB +0.38). Buehler (HR risk 0.35, vs LHB -0.03, vs RHB +0.54).",
        "rows": [
            row("Jase Bowen", "R", "N/A", 58, "💎", ["vs Harrison"], """Worst Pickz Hidden Gem. 0 HR, 89.2 mph EV. Harrison RHB split +0.38, HR risk 0.20. limited recent HR events."""),
            row("Gavin Sheets", "L", "+1000", 60, "", ["vs Harrison"], """0 HR, 2 near-HR, 97.8 mph EV. Harrison LHB split -0.46, HR risk 0.20. tough split lane (-0.46).""", blast="good"),
            row("Jake Bauers", "L", "+395", 64, "⭐", ["vs Buehler"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 95.5 mph EV. Buehler LHB split -0.03, HR risk 0.35. slight split headwind (-0.03).""", blast="good"),
            row("Gary Sanchez", "R", "N/A", 64, "", ["vs Buehler"], """1 HR, 1 near-HR, 88.1 mph EV. Buehler RHB split +0.54, HR risk 0.35.""", blast="good"),
            row("Brice Turang", "L", "+770", 59, "", ["vs Buehler"], """0 HR, 92.9 mph EV. Buehler LHB split -0.03, HR risk 0.35. slight split headwind (-0.03); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "NYM @ ATL - Nolan McLean (R, NYM) vs Martin Perez (L, ATL)",
        "description": "Tail key data: Park boost +5% (stadium -2%, weather +7%). McLean (HR risk 0.14, vs LHB +0.11, vs RHB -0.51). Perez (HR risk -0.35, vs LHB +0.16, vs RHB -0.44).",
        "rows": [
            row("Matt Olson", "L", "+350", 82, "⭐ 🌕 💣", ["vs McLean"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 96.4 mph EV. McLean LHB split +0.11, HR risk 0.14.""", blast="high"),
            row("Ronald Acuna Jr.", "R", "+430", 60, "💎", ["vs McLean"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.9 mph EV. McLean RHB split -0.51, HR risk 0.14. tough split lane (-0.51).""", blast="good"),
            row("Drake Baldwin", "L", "+450", 64, "", ["vs McLean"], """0 HR, 1 near-HR, 95.8 mph EV. McLean LHB split +0.11, HR risk 0.14. limited recent HR events.""", blast="good"),
            row("Michael Harris II", "L", "+440", 65, "🚀", ["vs McLean"], """0 HR, 2 near-HR, 101.8 mph EV. McLean LHB split +0.11, HR risk 0.14.""", blast="good"),
            row("Francisco Lindor", "S", "+443", 75, "🌕 💣 💎", ["vs Martin Perez"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 93.4 mph EV. Martin Perez SHB→LHB split +0.16, HR risk -0.35. pitcher risk below avg (-0.35).""", blast="high"),
            row("Marcus Semien", "R", "+680", 72, "🌕 💣", ["vs Martin Perez"], """2 HR, 3 near-HR, 95.4 mph EV. Martin Perez RHB split -0.44, HR risk -0.35. tough split lane (-0.44); pitcher risk below avg (-0.35).""", blast="high"),
            row("A.J. Ewing", "L", "+870", 58, "", ["vs Martin Perez"], """0 HR, 90.7 mph EV. Martin Perez LHB split +0.16, HR risk -0.35. pitcher risk below avg (-0.35); limited recent HR events."""),
        ],
    },
    {
        "title": "PHI @ STL - Cristopher Sanchez (L, PHI) vs Andre Pallante (R, STL)",
        "description": "Tail key data: Park boost +3% (stadium -11%, weather +14%). Sanchez (HR risk -0.68, vs LHB -1.12, vs RHB -0.20). Pallante (HR risk -0.98, vs LHB -0.49, vs RHB -0.96).",
        "rows": [
            row("Jordan Walker", "R", "+470", 58, "⭐", ["vs Sanchez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.5 mph EV. Sanchez RHB split -0.20, HR risk -0.68. slight split headwind (-0.20); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Alec Burleson", "L", "+910", 58, "", ["vs Sanchez"], """1 HR, 1 near-HR, 95.0 mph EV. Sanchez LHB split -1.12, HR risk -0.68. tough split lane (-1.12); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Ivan Herrera", "R", "+830", 58, "💎", ["vs Sanchez"], """Worst Pickz Hidden Gem. 0 HR, 89.4 mph EV. Sanchez RHB split -0.20, HR risk -0.68. slight split headwind (-0.20); pitcher suppresses HR (-0.68)."""),
            row("Bryce Harper", "L", "+476", 67, "⭐ 🌕 💣", ["vs Pallante"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 99.5 mph EV. Pallante LHB split -0.49, HR risk -0.98. tough split lane (-0.49); pitcher suppresses HR (-0.98).""", blast="high"),
            row("J.T. Realmuto", "R", "+830", 58, "🚀", ["vs Pallante"], """1 HR, 2 near-HR, 100.1 mph EV. Pallante RHB split -0.96, HR risk -0.98. tough split lane (-0.96); pitcher suppresses HR (-0.98).""", blast="good"),
            row("Kyle Schwarber", "L", "+290", 58, "", ["vs Pallante"], """1 HR, 2 near-HR, 97.9 mph EV. Pallante LHB split -0.49, HR risk -0.98. tough split lane (-0.49); pitcher suppresses HR (-0.98).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ MIA - Paul Skenes (R, PIT) vs Eury Perez (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -13%, weather +0%). Skenes (HR risk -0.02, vs LHB -0.06, vs RHB -0.04). Perez (HR risk -0.58, vs LHB -0.78, vs RHB +0.02).",
        "rows": [
            row("Owen Caissie", "L", "+581", 67, "⭐ 🌕 💣", ["vs Skenes"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.5 mph EV. Skenes LHB split -0.06, HR risk -0.02. slight split headwind (-0.06); pitcher risk below avg (-0.02).""", blast="high"),
            row("Jakob Marsee", "L", "+870", 59, "", ["vs Skenes"], """1 HR, 1 near-HR, 94.4 mph EV. Skenes LHB split -0.06, HR risk -0.02. slight split headwind (-0.06); pitcher risk below avg (-0.02).""", blast="good"),
            row("Brandon Lowe", "L", "+450", 58, "", ["vs Eury Perez"], """1 HR, 1 near-HR, 96.6 mph EV. Eury Perez LHB split -0.78, HR risk -0.58. tough split lane (-0.78); pitcher suppresses HR (-0.58).""", blast="good"),
            row("Endy Rodriguez", "S", "N/A", 58, "", ["vs Eury Perez"], """1 HR, 1 near-HR, 93.0 mph EV. Eury Perez SHB→RHB split +0.02, HR risk -0.58. pitcher suppresses HR (-0.58); park/weather net drag (-13%).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ NYY - Bryan Woo (R, SEA) vs Ryan Weathers (L, NYY)",
        "description": "Tail key data: Park boost +22% (stadium +6%, weather +16%). Woo (HR risk 0.24, vs LHB +0.12, vs RHB -0.01). Weathers (HR risk -0.22, vs LHB -0.51, vs RHB -0.01).",
        "rows": [
            row("Ben Rice", "L", "+297", 73, "💎", ["vs Woo"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.9 mph EV. Woo LHB split +0.12, HR risk 0.24.""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "+345", 83, "🌕 💣", ["vs Woo"], """2 HR, 2 near-HR, 99.6 mph EV. Woo LHB split +0.12, HR risk 0.24.""", blast="high"),
            row("Luis Garcia Jr.", "L", "+351", 71, "", ["vs Woo"], """1 HR, 2 near-HR, 92.0 mph EV. Woo LHB split +0.12, HR risk 0.24.""", blast="good"),
            row("Cal Raleigh", "S", "+310", 68, "⭐", ["vs Weathers"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.5 mph EV. Weathers SHB→RHB split -0.01, HR risk -0.22. slight split headwind (-0.01); pitcher risk below avg (-0.22).""", blast="good"),
            row("Dominic Canzone", "L", "+421", 67, "🌕 💣 💎", ["vs Weathers"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 89.9 mph EV. Weathers LHB split -0.51, HR risk -0.22. tough split lane (-0.51); pitcher risk below avg (-0.22).""", blast="high"),
        ],
    },
    {
        "title": "TB @ ATH - Nick Martinez (R, TB) vs Mason Barnett 🧤 (R, ATH)",
        "description": "Tail key data: Park boost +34% (stadium +26%, weather +7%). Martinez (HR risk 0.16, vs LHB +0.19, vs RHB -0.24). Barnett 🧤 (HR risk 0.96, vs LHB -0.09, vs RHB +1.51).",
        "rows": [
            row("Tyler Soderstrom", "L", "+346", 72, "", ["vs Martinez"], """0 HR, 1 near-HR, 96.4 mph EV. Martinez LHB split +0.19, HR risk 0.16. limited recent HR events.""", blast="good"),
            row("Lawrence Butler", "L", "+435", 72, "💎", ["vs Martinez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.0 mph EV. Martinez LHB split +0.19, HR risk 0.16.""", blast="good"),
            row("Junior Caminero", "R", "+240", 99, "🌕 💣", ["vs Barnett"], """2 HR, 3 near-HR, 96.6 mph EV. Barnett RHB split +1.51, HR risk 0.96.""", blast="high"),
            row("Victor Mesa Jr.", "L", "+390", 76, "", ["vs Barnett"], """1 HR, 1 near-HR, 84.2 mph EV. Barnett LHB split -0.09, HR risk 0.96. slight split headwind (-0.09); lighter EV form (84.2 mph).""", blast="good"),
            row("Yandy Diaz", "R", "+478", 92, "🚀 🌕 💣", ["vs Barnett"], """0 HR, 1 near-HR, 100.2 mph EV. Barnett RHB split +1.51, HR risk 0.96. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "TEX @ LAA - Cody Bradford (L, TEX) vs Ryan Johnson 🧤 (R, LAA)",
        "description": "Tail key data: Park boost -4% (stadium -8%, weather +4%). Bradford (HR risk 0.00, vs LHB +0.00, vs RHB +0.00). Johnson 🧤 (HR risk 1.69, vs LHB +1.16, vs RHB +1.08).",
        "rows": [
            row("Zach Neto", "R", "+330", 58, "", ["vs Bradford"], """0 HR, 92.9 mph EV. Bradford RHB split +0.00, HR risk 0.00. park suppresses carry (-8%); limited recent HR events.""", blast="good"),
            row("Moises Ballesteros", "L", "+680", 58, "", ["vs Bradford"], """0 HR, 94.1 mph EV. Bradford LHB split +0.00, HR risk 0.00. park suppresses carry (-8%); limited recent HR events.""", blast="good"),
            row("Nolan Schanuel", "L", "+1100", 58, "", ["vs Bradford"], """0 HR, 1 near-HR, 91.2 mph EV. Bradford LHB split +0.00, HR risk 0.00. park suppresses carry (-8%); limited recent HR events."""),
            row("Jose Siri", "R", "+510", 77, "⭐ 🌕 💣", ["vs Bradford"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 92.4 mph EV. Bradford RHB split +0.00, HR risk 0.00. park suppresses carry (-8%).""", blast="high"),
            row("Joc Pederson", "L", "+240", 94, "⭐ 🌕 💣", ["vs Johnson"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.5 mph EV. Johnson LHB split +1.16, HR risk 1.69. park suppresses carry (-8%).""", blast="high"),
            row("Jake Burger", "R", "+340", 76, "", ["vs Johnson"], """0 HR, 1 near-HR, 90.2 mph EV. Johnson RHB split +1.08, HR risk 1.69. park suppresses carry (-8%); limited recent HR events."""),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-11")

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

    out = ROOT / '_games-0811.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
