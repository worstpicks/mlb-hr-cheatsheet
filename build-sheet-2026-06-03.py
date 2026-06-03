#!/usr/bin/env python3
"""Generate games[] block for 2026-06-03 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Brandon Lowe (L)",
    "Coby Mayo (R)",
    "Dillon Dingler (R)",
    "Heriberto Hernandez (R)",
    "JJ Bleday (L)",
    "Jac Caglianone (L)",
    "Jake Bauers (L)",
    "Jarren Duran (L)",
    "Jesus Sanchez (L)",
    "Joc Pederson (L)",
    "Jonathan Aranda (L)",
    "Lane Thomas (R)",
    "Nick Kurtz (L)",
    "Spencer Horwitz (L)",
    "Will Smith (R)",
    "Yandy Diaz (R)",
    "Yordan Alvarez (L)",
}

PLAYER_TEAMS = {
    "Aaron Judge (R)": "NYY",
    "Adley Rutschman (S)": "BAL",
    "Adrian Del Castillo (L)": "ARI",
    "Andrew Benintendi (L)": "CWS",
    "Andy Pages (R)": "LAD",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Blake Dunn (R)": "CIN",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Harper (L)": "PHI",
    "Carlos Cortes (L)": "ATH",
    "Chase Meidroth (R)": "CWS",
    "Christian Walker (R)": "HOU",
    "Coby Mayo (R)": "BAL",
    "Colt Emerson (L)": "SEA",
    "Connor Norby (R)": "MIA",
    "Corbin Carroll (L)": "ARI",
    "Curtis Mead (R)": "WSH",
    "Dillon Dingler (R)": "DET",
    "Eric Haase (R)": "SF",
    "Ezequiel Tovar (R)": "COL",
    "Freddie Freeman (L)": "LAD",
    "Garrett Mitchell (L)": "MIL",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ivan Herrera (R)": "STL",
    "J.P. Crawford (L)": "SEA",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jacob Young (R)": "WSH",
    "Jake Bauers (L)": "MIL",
    "Jake McCarthy (L)": "COL",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jarren Duran (L)": "BOS",
    "Jesus Sanchez (L)": "TOR",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Jonathan Aranda (L)": "TB",
    "Jorge Mateo (R)": "ATL",
    "Josh Bell (S)": "MIN",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Higashioka (R)": "TEX",
    "Kyle Schwarber (L)": "PHI",
    "Lane Thomas (R)": "KC",
    "Luke Raley (L)": "SEA",
    "Marcus Semien (R)": "NYM",
    "Masataka Yoshida (L)": "BOS",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Michael Busch (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Michael Massey (L)": "KC",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Nick Kurtz (L)": "ATH",
    "Nolan Arenado (R)": "ARI",
    "Nolan Gorman (L)": "STL",
    "Oneil Cruz (L)": "PIT",
    "Patrick Bailey (S)": "CLE",
    "Patrick Wisdom (R)": "SEA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Riley Greene (L)": "DET",
    "Ryan McMahon (L)": "NYY",
    "Salvador Perez (R)": "KC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Horwitz (L)": "PIT",
    "Spencer Torkelson (R)": "DET",
    "Travis Bazzana (L)": "CLE",
    "Ty France (R)": "SD",
    "Vaughn Grissom (R)": "LAA",
    "Wade Meckler (L)": "LAA",
    "Will Benson (L)": "CIN",
    "Will Smith (R)": "LAD",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Xavier Edwards (S)": "MIA",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_PITCHERS = {
    "Fedde",
    "Gallen",
    "Holmes",
    "Rea",
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
        "title": "ATH @ CHC - Jeffrey Springs (R, ATH) vs Colin Rea 🧤 (R, CHC)",
        "description": "Tail key data: Park boost -5% (stadium -1%, weather -4%). Jeffrey Springs (HR risk 0.71, vs LHB +0.21, vs RHB +0.61). Colin Rea 🧤 (HR risk 1.02, vs LHB +0.36, vs RHB +1.29).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+490", 77, "💎", ["vs Springs"], """Tail: 1 HR, 1 near-HR, 94.9 mph EV. Matchup: Springs LHB split +0.21, HR risk 0.71. Fade: park/weather net drag (-5%). Model score 77; odds Listed +490 - Over 0.5 HR.""", blast="good"),
            row("Michael Busch", "L", "+630", 62, "💎", ["vs Springs"], """Tail: 0 HR, 84.1 mph EV. Matchup: Springs LHB split +0.21, HR risk 0.71. Fade: park/weather net drag (-5%); limited recent HR events. Model score 62; odds Listed +630 - Over 0.5 HR."""),
            row("Nick Kurtz", "L", "+340", 78, "⭐ 💎", ["vs Rea"], """Worst Pickz Favorite. Tail: 0 HR, 1 near-HR, 99.7 mph EV. Matchup: Rea LHB split +0.36, HR risk 1.02. Fade: park/weather net drag (-5%); limited recent HR events. Model score 78; odds Listed +340 - Over 0.5 HR.""", blast="good"),
            row("Carlos Cortes", "L", "+750", 64, "💎", ["vs Rea"], """Tail: 0 HR, 1 near-HR, 81.8 mph EV. Matchup: Rea LHB split +0.36, HR risk 1.02. Fade: park/weather net drag (-5%); limited recent HR events. Model score 64; odds Listed +750 - Over 0.5 HR."""),
        ],
    },
    {
        "title": "BAL @ BOS - Chris Bassitt (R, BAL) vs Payton Tolle (R, BOS)",
        "description": "Tail key data: Park boost -10% (stadium -7%, weather -3%). Chris Bassitt (HR risk -0.45, vs LHB +0.13, vs RHB -1.06). Payton Tolle (HR risk -0.11, vs LHB +0.41, vs RHB -0.21).",
        "rows": [
            row("Jarren Duran", "L", "+509", 76, "⭐ 💎", ["vs Bassitt"], """Worst Pickz Favorite. Tail: 1 HR, 1 near-HR, 93.7 mph EV. Matchup: Bassitt LHB split +0.13, HR risk -0.45. Fade: pitcher suppresses HR (-0.45); park/weather net drag (-10%). Model score 76; odds Listed +509 - Over 0.5 HR.""", blast="good"),
            row("Willson Contreras", "R", "+680", 78, "🌕 💣", ["vs Bassitt"], """Tail: 2 HR, 2 near-HR, 86.4 mph EV. Matchup: Bassitt RHB split -1.06, HR risk -0.45. Fade: tough split lane (-1.06); pitcher suppresses HR (-0.45). Model score 78; odds Listed +680 - Over 0.5 HR.""", blast="high"),
            row("Masataka Yoshida", "L", "+1120", 64, "💎", ["vs Bassitt"], """Tail: 0 HR, 1 near-HR, 87.8 mph EV. Matchup: Bassitt LHB split +0.13, HR risk -0.45. Fade: pitcher suppresses HR (-0.45); park/weather net drag (-10%). Model score 64; odds Listed +1120 - Over 0.5 HR."""),
            row("Coby Mayo", "R", "+568", 90, "🚀 ⭐ 🌕 💣", ["vs Tolle"], """Worst Pickz Favorite. Tail: 2 HR, 2 near-HR, 101.2 mph EV. Matchup: Tolle RHB split -0.21, HR risk -0.11. Fade: slight split headwind (-0.21); pitcher risk below avg (-0.11). Model score 90; odds Listed +568 - Over 0.5 HR.""", blast="high"),
            row("Pete Alonso", "R", "+433", 78, "🚀 💎", ["vs Tolle"], """Tail: 0 HR, 1 near-HR, 100.7 mph EV. Matchup: Tolle RHB split -0.21, HR risk -0.11. Fade: slight split headwind (-0.21); pitcher risk below avg (-0.11). Model score 78; odds Listed +433 - Over 0.5 HR.""", blast="good"),
            row("Adley Rutschman", "S", "+630", 69, "💎", ["vs Tolle"], """Tail: 0 HR, 92.9 mph EV. Matchup: Tolle RHB split -0.21, HR risk -0.11. Fade: slight split headwind (-0.21); pitcher risk below avg (-0.11). Model score 69; odds Listed +630 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "CLE @ NYY - Gavin Williams (R, CLE) vs Gerrit Cole (R, NYY)",
        "description": "Tail key data: Park boost -2% (stadium +8%, weather -10%). Gavin Williams (HR risk 0.46, vs LHB +0.82, vs RHB -0.26). Gerrit Cole (HR risk -2.00, vs LHB -1.95, vs RHB -1.24).",
        "rows": [
            row("Ben Rice", "L", "+375", 64, "💎", ["vs Williams"], """Tail: 0 HR, 1 near-HR, 85.4 mph EV. Matchup: Williams LHB split +0.82, HR risk 0.46. Fade: weather carry headwind (-10%); limited recent HR events. Model score 64; odds Listed +375 - Over 0.5 HR."""),
            row("Ryan McMahon", "L", "+590", 78, "🌕 💣", ["vs Williams"], """Tail: 2 HR, 2 near-HR, 86.9 mph EV. Matchup: Williams LHB split +0.82, HR risk 0.46. Fade: weather carry headwind (-10%); lighter EV form (86.9 mph). Model score 78; odds Listed +590 - Over 0.5 HR.""", blast="high"),
            row("Aaron Judge", "R", "N/A", 83, "💎", ["vs Williams"], """Tail: 1 HR, 3 near-HR, 97.2 mph EV. Matchup: Williams RHB split -0.26, HR risk 0.46. Fade: slight split headwind (-0.26); weather carry headwind (-10%). Model score 83; odds Listed prop - Over 0.5 HR.""", blast="good"),
            row("Patrick Bailey", "S", "+1000", 77, "💎", ["vs Cole"], """Tail: 1 HR, 3 near-HR, 91.3 mph EV. Matchup: Cole RHB split -1.24, HR risk -2.00. Fade: tough split lane (-1.24); pitcher suppresses HR (-2.00). Model score 77; odds Listed +1000 - Over 0.5 HR.""", blast="good"),
            row("Travis Bazzana", "L", "+890", 75, "💎", ["vs Cole"], """Tail: 1 HR, 1 near-HR, 93.0 mph EV. Matchup: Cole LHB split -1.95, HR risk -2.00. Fade: tough split lane (-1.95); pitcher suppresses HR (-2.00). Model score 75; odds Listed +890 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "COL @ LAA - Michael Lorenzen (R, COL) vs Walbert Urena (R, LAA)",
        "description": "Tail key data: Park boost +7% (stadium +9%, weather -2%). Michael Lorenzen (HR risk 0.69, vs LHB +1.78, vs RHB -0.30). Walbert Urena (HR risk -0.66, vs LHB -0.71, vs RHB -0.30).",
        "rows": [
            row("Wade Meckler", "L", "+760", 81, "🌕 💣", ["vs Lorenzen"], """Tail: 2 HR, 3 near-HR, 88.9 mph EV. Matchup: Lorenzen LHB split +1.78, HR risk 0.69. Fade: HR outcomes are still high-variance. Model score 81; odds Listed +760 - Over 0.5 HR.""", blast="high"),
            row("Zach Neto", "R", "+420", 80, "🌕 💣", ["vs Lorenzen"], """Tail: 2 HR, 3 near-HR, 87.7 mph EV. Matchup: Lorenzen RHB split -0.30, HR risk 0.69. Fade: slight split headwind (-0.30); lighter EV form (87.7 mph). Model score 80; odds Listed +420 - Over 0.5 HR.""", blast="high"),
            row("Jo Adell", "R", "+410", 79, "🌕 💣", ["vs Lorenzen"], """Tail: 2 HR, 2 near-HR, 88.7 mph EV. Matchup: Lorenzen RHB split -0.30, HR risk 0.69. Fade: slight split headwind (-0.30). Model score 79; odds Listed +410 - Over 0.5 HR.""", blast="high"),
            row("Mike Trout", "R", "+310", 84, "🌕 💣", ["vs Lorenzen"], """Tail: 2 HR, 4 near-HR, 89.6 mph EV. Matchup: Lorenzen RHB split -0.30, HR risk 0.69. Fade: slight split headwind (-0.30). Model score 84; odds Listed +310 - Over 0.5 HR.""", blast="high"),
            row("Vaughn Grissom", "R", "+740", 78, "💎", ["vs Lorenzen"], """Tail: 1 HR, 3 near-HR, 92.5 mph EV. Matchup: Lorenzen RHB split -0.30, HR risk 0.69. Fade: slight split headwind (-0.30). Model score 78; odds Listed +740 - Over 0.5 HR.""", blast="good"),
            row("Ezequiel Tovar", "R", "+820", 78, "🌕 💣", ["vs Urena"], """Tail: 2 HR, 2 near-HR, 86.6 mph EV. Matchup: Urena RHB split -0.30, HR risk -0.66. Fade: slight split headwind (-0.30); pitcher suppresses HR (-0.66). Model score 78; odds Listed +820 - Over 0.5 HR.""", blast="high"),
            row("Willi Castro", "S", "+820", 79, "💎", ["vs Urena"], """Tail: 1 HR, 2 near-HR, 94.7 mph EV. Matchup: Urena RHB split -0.30, HR risk -0.66. Fade: slight split headwind (-0.30); pitcher suppresses HR (-0.66). Model score 79; odds Listed +820 - Over 0.5 HR.""", blast="good"),
            row("Jake McCarthy", "L", "+1040", 80, "🌕 💣", ["vs Urena"], """Tail: 2 HR, 3 near-HR, 87.3 mph EV. Matchup: Urena LHB split -0.71, HR risk -0.66. Fade: tough split lane (-0.71); pitcher suppresses HR (-0.66). Model score 80; odds Listed +1040 - Over 0.5 HR.""", blast="high"),
            row("Hunter Goodman", "R", "+390", 62, "💎", ["vs Urena"], """Tail: 0 HR, 85.7 mph EV. Matchup: Urena RHB split -0.30, HR risk -0.66. Fade: slight split headwind (-0.30); pitcher suppresses HR (-0.66). Model score 62; odds Listed +390 - Over 0.5 HR."""),
        ],
    },
    {
        "title": "CWS @ MIN - Erick Fedde 🧤 (R, CWS) vs Taj Bradley (R, MIN)",
        "description": "Tail key data: Park boost data unavailable. Erick Fedde 🧤 (HR risk 1.64, vs LHB +0.01, vs RHB +2.11). Taj Bradley (HR risk 0.86, vs LHB +1.16, vs RHB +0.10).",
        "rows": [
            row("Josh Bell", "S", "+525", 66, "💎", ["vs Fedde"], """Tail: 0 HR, 1 near-HR, 89.9 mph EV. Matchup: Fedde RHB split +2.11, HR risk 1.64. Fade: limited recent HR events. Model score 66; odds Listed +525 - Over 0.5 HR."""),
            row("Kody Clemens", "L", "+443", 72, "💎", ["vs Fedde"], """Tail: 0 HR, 1 near-HR, 94.4 mph EV. Matchup: Fedde LHB split +0.01, HR risk 1.64. Fade: limited recent HR events. Model score 72; odds Listed +443 - Over 0.5 HR.""", blast="good"),
            row("Andrew Benintendi", "L", "+600", 82, "🌕 💣", ["vs Bradley"], """Tail: 2 HR, 2 near-HR, 92.2 mph EV. Matchup: Bradley LHB split +1.16, HR risk 0.86. Fade: HR outcomes are still high-variance. Model score 82; odds Listed +600 - Over 0.5 HR.""", blast="high"),
            row("Miguel Vargas", "R", "+425", 83, "💎", ["vs Bradley"], """Tail: 1 HR, 3 near-HR, 96.9 mph EV. Matchup: Bradley RHB split +0.10, HR risk 0.86. Fade: HR outcomes are still high-variance. Model score 83; odds Listed +425 - Over 0.5 HR.""", blast="good"),
            row("Chase Meidroth", "R", "+1040", 65, "💎", ["vs Bradley"], """Tail: 0 HR, 90.9 mph EV. Matchup: Bradley RHB split +0.10, HR risk 0.86. Fade: limited recent HR events. Model score 65; odds Listed +1040 - Over 0.5 HR."""),
        ],
    },
    {
        "title": "DET @ TB - Troy Melton (R, DET) vs Nick Martinez (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Troy Melton (HR risk -0.83, vs LHB -0.77, vs RHB -0.01). Nick Martinez (HR risk -0.72, vs LHB -0.32, vs RHB -0.78).",
        "rows": [
            row("Jonathan Aranda", "L", "+495", 85, "⭐ 🌕 💣", ["vs Melton"], """Worst Pickz Favorite. Tail: 2 HR, 3 near-HR, 92.9 mph EV. Matchup: Melton LHB split -0.77, HR risk -0.83. Fade: tough split lane (-0.77); pitcher suppresses HR (-0.83). Model score 85; odds Listed +495 - Over 0.5 HR.""", blast="high"),
            row("Yandy Diaz", "R", "+475", 88, "⭐ 🌕 💣", ["vs Melton"], """Worst Pickz Favorite. Tail: 2 HR, 3 near-HR, 96.0 mph EV. Matchup: Melton RHB split -0.01, HR risk -0.83. Fade: slight split headwind (-0.01); pitcher suppresses HR (-0.83). Model score 88; odds Listed +475 - Over 0.5 HR.""", blast="high"),
            row("Junior Caminero", "R", "+350", 79, "💎", ["vs Melton"], """Tail: 1 HR, 2 near-HR, 94.9 mph EV. Matchup: Melton RHB split -0.01, HR risk -0.83. Fade: slight split headwind (-0.01); pitcher suppresses HR (-0.83). Model score 79; odds Listed +350 - Over 0.5 HR.""", blast="good"),
            row("Dillon Dingler", "R", "+525", 78, "⭐ 🌕 💣", ["vs Martinez"], """Worst Pickz Favorite. Tail: 2 HR, 2 near-HR, 86.4 mph EV. Matchup: Martinez RHB split -0.78, HR risk -0.72. Fade: tough split lane (-0.78); pitcher suppresses HR (-0.72). Model score 78; odds Listed +525 - Over 0.5 HR.""", blast="high"),
            row("Spencer Torkelson", "R", "+475", 74, "💎", ["vs Martinez"], """Tail: 0 HR, 2 near-HR, 93.9 mph EV. Matchup: Martinez RHB split -0.78, HR risk -0.72. Fade: tough split lane (-0.78); pitcher suppresses HR (-0.72). Model score 74; odds Listed +475 - Over 0.5 HR.""", blast="good"),
            row("Riley Greene", "L", "+520", 75, "💎", ["vs Martinez"], """Tail: 1 HR, 1 near-HR, 92.6 mph EV. Matchup: Martinez LHB split -0.32, HR risk -0.72. Fade: slight split headwind (-0.32); pitcher suppresses HR (-0.72). Model score 75; odds Listed +520 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "KC @ CIN - Stephen Kolek (R, KC) vs Chase Burns (R, CIN)",
        "description": "Tail key data: Park boost +0% (stadium +15%, weather -14%). Stephen Kolek (HR risk -0.16, vs LHB -0.27, vs RHB +0.18). Chase Burns (HR risk 0.08, vs LHB +0.40, vs RHB -0.23).",
        "rows": [
            row("JJ Bleday", "L", "+325", 85, "⭐ 🌕 💣", ["vs Kolek"], """Worst Pickz Favorite. Tail: 3 HR, 3 near-HR, 89.0 mph EV. Matchup: Kolek LHB split -0.27, HR risk -0.16. Fade: slight split headwind (-0.27); pitcher risk below avg (-0.16). Model score 85; odds Listed +325 - Over 0.5 HR.""", blast="high"),
            row("Will Benson", "L", "N/A", 76, "💎", ["vs Kolek"], """Tail: 1 HR, 1 near-HR, 93.7 mph EV. Matchup: Kolek LHB split -0.27, HR risk -0.16. Fade: slight split headwind (-0.27); pitcher risk below avg (-0.16). Model score 76; odds Listed prop - Over 0.5 HR.""", blast="good"),
            row("Blake Dunn", "R", "+710", 64, "💎", ["vs Kolek"], """Tail: 0 HR, 1 near-HR, 83.9 mph EV. Matchup: Kolek RHB split +0.18, HR risk -0.16. Fade: pitcher risk below avg (-0.16); weather carry headwind (-14%). Model score 64; odds Listed +710 - Over 0.5 HR."""),
            row("Lane Thomas", "R", "N/A", 73, "⭐ 💎", ["vs Burns"], """Worst Pickz Favorite. Tail: 1 HR, 2 near-HR, 89.0 mph EV. Matchup: Burns RHB split -0.23, HR risk 0.08. Fade: slight split headwind (-0.23); weather carry headwind (-14%). Model score 73; odds Listed prop - Over 0.5 HR.""", blast="good"),
            row("Bobby Witt Jr.", "R", "+399", 71, "💎", ["vs Burns"], """Tail: 0 HR, 1 near-HR, 93.3 mph EV. Matchup: Burns RHB split -0.23, HR risk 0.08. Fade: slight split headwind (-0.23); weather carry headwind (-14%). Model score 71; odds Listed +399 - Over 0.5 HR.""", blast="good"),
            row("Jac Caglianone", "L", "+500", 78, "🚀 ⭐ 💎", ["vs Burns"], """Worst Pickz Favorite. Tail: 0 HR, 1 near-HR, 102.8 mph EV. Matchup: Burns LHB split +0.40, HR risk 0.08. Fade: weather carry headwind (-14%); limited recent HR events. Model score 78; odds Listed +500 - Over 0.5 HR.""", blast="good"),
            row("Michael Massey", "L", "+680", 71, "💎", ["vs Burns"], """Tail: 1 HR, 1 near-HR, 89.3 mph EV. Matchup: Burns LHB split +0.40, HR risk 0.08. Fade: weather carry headwind (-14%). Model score 71; odds Listed +680 - Over 0.5 HR.""", blast="good"),
            row("Salvador Perez", "R", "+466", 64, "💎", ["vs Burns"], """Tail: 0 HR, 1 near-HR, 87.9 mph EV. Matchup: Burns RHB split -0.23, HR risk 0.08. Fade: slight split headwind (-0.23); weather carry headwind (-14%). Model score 64; odds Listed +466 - Over 0.5 HR."""),
        ],
    },
    {
        "title": "LAD @ ARI - Shohei Ohtani (R, LAD) vs Zac Gallen 🧤 (R, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Shohei Ohtani (HR risk -0.81, vs LHB -0.85, vs RHB -0.43). Zac Gallen 🧤 (HR risk 1.18, vs LHB +0.90, vs RHB +0.88).",
        "rows": [
            row("Ketel Marte", "S", "+506", 70, "💎", ["vs Ohtani"], """Tail: 1 HR, 1 near-HR, 87.4 mph EV. Matchup: Ohtani RHB split -0.43, HR risk -0.81. Fade: tough split lane (-0.43); pitcher suppresses HR (-0.81). Model score 70; odds Listed +506 - Over 0.5 HR.""", blast="good"),
            row("Adrian Del Castillo", "L", "N/A", 71, "💎", ["vs Ohtani"], """Tail: 1 HR, 1 near-HR, 89.1 mph EV. Matchup: Ohtani LHB split -0.85, HR risk -0.81. Fade: tough split lane (-0.85); pitcher suppresses HR (-0.81). Model score 71; odds Listed prop - Over 0.5 HR.""", blast="good"),
            row("Corbin Carroll", "L", "+570", 74, "💎", ["vs Ohtani"], """Tail: 0 HR, 2 near-HR, 94.5 mph EV. Matchup: Ohtani LHB split -0.85, HR risk -0.81. Fade: tough split lane (-0.85); pitcher suppresses HR (-0.81). Model score 74; odds Listed +570 - Over 0.5 HR.""", blast="good"),
            row("Nolan Arenado", "R", "+810", 64, "💎", ["vs Ohtani"], """Tail: 0 HR, 1 near-HR, 83.6 mph EV. Matchup: Ohtani RHB split -0.43, HR risk -0.81. Fade: tough split lane (-0.43); pitcher suppresses HR (-0.81). Model score 64; odds Listed +810 - Over 0.5 HR."""),
            row("Will Smith", "R", "+575", 74, "⭐ 💎", ["vs Gallen"], """Worst Pickz Favorite. Tail: 1 HR, 2 near-HR, 89.7 mph EV. Matchup: Gallen RHB split +0.88, HR risk 1.18. Fade: park/weather net drag (-8%). Model score 74; odds Listed +575 - Over 0.5 HR.""", blast="good"),
            row("Freddie Freeman", "L", "+571", 81, "🌕 💣", ["vs Gallen"], """Tail: 2 HR, 2 near-HR, 90.6 mph EV. Matchup: Gallen LHB split +0.90, HR risk 1.18. Fade: park/weather net drag (-8%). Model score 81; odds Listed +571 - Over 0.5 HR.""", blast="high"),
            row("Shohei Ohtani", "L", "+311", 87, "🌕 💣", ["vs Gallen"], """Tail: 2 HR, 2 near-HR, 96.8 mph EV. Matchup: Gallen LHB split +0.90, HR risk 1.18. Fade: park/weather net drag (-8%). Model score 87; odds Listed +311 - Over 0.5 HR.""", blast="high"),
            row("Max Muncy", "L", "+375", 84, "🌕 💣", ["vs Gallen"], """Tail: 2 HR, 3 near-HR, 92.5 mph EV. Matchup: Gallen LHB split +0.90, HR risk 1.18. Fade: park/weather net drag (-8%). Model score 84; odds Listed +375 - Over 0.5 HR.""", blast="high"),
            row("Andy Pages", "R", "+544", 71, "💎", ["vs Gallen"], """Tail: 0 HR, 1 near-HR, 92.7 mph EV. Matchup: Gallen RHB split +0.88, HR risk 1.18. Fade: park/weather net drag (-8%); limited recent HR events. Model score 71; odds Listed +544 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ WSH - Max Meyer (R, MIA) vs Andrew Alvarez (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Max Meyer (HR risk 0.24, vs LHB -0.52, vs RHB +0.84). Andrew Alvarez (HR risk -0.24, vs LHB +0.82, vs RHB -0.72).",
        "rows": [
            row("James Wood", "L", "+431", 69, "💎", ["vs Meyer"], """Tail: 0 HR, 92.8 mph EV. Matchup: Meyer LHB split -0.52, HR risk 0.24. Fade: tough split lane (-0.52); limited recent HR events. Model score 69; odds Listed +431 - Over 0.5 HR.""", blast="good"),
            row("Curtis Mead", "R", "+650", 93, "🌕 💣", ["vs Meyer"], """Tail: 3 HR, 4 near-HR, 95.1 mph EV. Matchup: Meyer RHB split +0.84, HR risk 0.24. Fade: HR outcomes are still high-variance. Model score 93; odds Listed +650 - Over 0.5 HR.""", blast="high"),
            row("Jacob Young", "R", "+1400", 65, "💎", ["vs Meyer"], """Tail: 0 HR, 90.8 mph EV. Matchup: Meyer RHB split +0.84, HR risk 0.24. Fade: limited recent HR events. Model score 65; odds Listed +1400 - Over 0.5 HR."""),
            row("Heriberto Hernandez", "R", "+590", 95, "⭐ 🌕 💣", ["vs Alvarez"], """Worst Pickz Favorite. Tail: 3 HR, 4 near-HR, 97.2 mph EV. Matchup: Alvarez RHB split -0.72, HR risk -0.24. Fade: tough split lane (-0.72); pitcher risk below avg (-0.24). Model score 95; odds Listed +590 - Over 0.5 HR.""", blast="high"),
            row("Xavier Edwards", "S", "+1220", 84, "🌕 💣", ["vs Alvarez"], """Tail: 2 HR, 2 near-HR, 93.6 mph EV. Matchup: Alvarez RHB split -0.72, HR risk -0.24. Fade: tough split lane (-0.72); pitcher risk below avg (-0.24). Model score 84; odds Listed +1220 - Over 0.5 HR.""", blast="high"),
            row("Connor Norby", "R", "+940", 75, "💎", ["vs Alvarez"], """Tail: 1 HR, 1 near-HR, 92.7 mph EV. Matchup: Alvarez RHB split -0.72, HR risk -0.24. Fade: tough split lane (-0.72); pitcher risk below avg (-0.24). Model score 75; odds Listed +940 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "NYM @ SEA - Freddy Peralta (R, NYM) vs George Kirby (R, SEA)",
        "description": "Tail key data: Park boost -2% (stadium +0%, weather -2%). Freddy Peralta (HR risk 0.16, vs LHB +0.32, vs RHB -0.20). George Kirby (HR risk -0.05, vs LHB +0.34, vs RHB -0.39).",
        "rows": [
            row("Colt Emerson", "L", "+960", 70, "💎", ["vs Peralta"], """Tail: 1 HR, 1 near-HR, 86.7 mph EV. Matchup: Peralta LHB split +0.32, HR risk 0.16. Fade: lighter EV form (86.7 mph). Model score 70; odds Listed +960 - Over 0.5 HR.""", blast="good"),
            row("J.P. Crawford", "L", "+710", 80, "🌕 💣", ["vs Peralta"], """Tail: 2 HR, 2 near-HR, 90.0 mph EV. Matchup: Peralta LHB split +0.32, HR risk 0.16. Fade: HR outcomes are still high-variance. Model score 80; odds Listed +710 - Over 0.5 HR.""", blast="high"),
            row("Luke Raley", "L", "+440", 78, "🌕 💣", ["vs Peralta"], """Tail: 2 HR, 2 near-HR, 83.8 mph EV. Matchup: Peralta LHB split +0.32, HR risk 0.16. Fade: lighter EV form (83.8 mph). Model score 78; odds Listed +440 - Over 0.5 HR.""", blast="high"),
            row("Patrick Wisdom", "R", "N/A", 82, "🚀 💎", ["vs Peralta"], """Tail: 1 HR, 1 near-HR, 100.6 mph EV. Matchup: Peralta RHB split -0.20, HR risk 0.16. Fade: slight split headwind (-0.20). Model score 82; odds Listed prop - Over 0.5 HR.""", blast="good"),
            row("Juan Soto", "L", "+390", 94, "🌕 💣", ["vs Kirby"], """Tail: 3 HR, 4 near-HR, 96.5 mph EV. Matchup: Kirby LHB split +0.34, HR risk -0.05. Fade: pitcher risk below avg (-0.05). Model score 94; odds Listed +390 - Over 0.5 HR.""", blast="high"),
            row("Jared Young", "L", "+830", 80, "💎", ["vs Kirby"], """Tail: 1 HR, 2 near-HR, 95.5 mph EV. Matchup: Kirby LHB split +0.34, HR risk -0.05. Fade: pitcher risk below avg (-0.05). Model score 80; odds Listed +830 - Over 0.5 HR.""", blast="good"),
            row("Marcus Semien", "R", "+880", 78, "🌕 💣", ["vs Kirby"], """Tail: 2 HR, 2 near-HR, 84.2 mph EV. Matchup: Kirby RHB split -0.39, HR risk -0.05. Fade: slight split headwind (-0.39); pitcher risk below avg (-0.05). Model score 78; odds Listed +880 - Over 0.5 HR.""", blast="high"),
        ],
    },
    {
        "title": "PIT @ HOU - Paul Skenes (R, PIT) vs Spencer Arrighetti (R, HOU)",
        "description": "Tail key data: Park boost +6% (stadium +6%, weather -1%). Paul Skenes (HR risk -0.70, vs LHB -0.66, vs RHB -0.34). Spencer Arrighetti (HR risk -0.64, vs LHB -0.74, vs RHB -0.27).",
        "rows": [
            row("Yordan Alvarez", "L", "+290", 87, "⭐ 🌕 💣", ["vs Skenes"], """Worst Pickz Favorite. Tail: 2 HR, 3 near-HR, 94.8 mph EV. Matchup: Skenes LHB split -0.66, HR risk -0.70. Fade: tough split lane (-0.66); pitcher suppresses HR (-0.70). Model score 87; odds Listed +290 - Over 0.5 HR.""", blast="high"),
            row("Christian Walker", "R", "+490", 79, "🌕 💣", ["vs Skenes"], """Tail: 2 HR, 2 near-HR, 88.9 mph EV. Matchup: Skenes RHB split -0.34, HR risk -0.70. Fade: slight split headwind (-0.34); pitcher suppresses HR (-0.70). Model score 79; odds Listed +490 - Over 0.5 HR.""", blast="high"),
            row("Spencer Horwitz", "L", "+630", 78, "⭐ 🌕 💣", ["vs Arrighetti"], """Worst Pickz Favorite. Tail: 2 HR, 2 near-HR, 87.5 mph EV. Matchup: Arrighetti LHB split -0.74, HR risk -0.64. Fade: tough split lane (-0.74); pitcher suppresses HR (-0.64). Model score 78; odds Listed +630 - Over 0.5 HR.""", blast="high"),
            row("Brandon Lowe", "L", "+390", 83, "⭐ 🌕 💣", ["vs Arrighetti"], """Worst Pickz Favorite. Tail: 1 HR, 4 near-HR, 93.2 mph EV. Matchup: Arrighetti LHB split -0.74, HR risk -0.64. Fade: tough split lane (-0.74); pitcher suppresses HR (-0.64). Model score 83; odds Listed +390 - Over 0.5 HR.""", blast="high"),
            row("Oneil Cruz", "L", "+320", 81, "💎", ["vs Arrighetti"], """Tail: 1 HR, 2 near-HR, 97.2 mph EV. Matchup: Arrighetti LHB split -0.74, HR risk -0.64. Fade: tough split lane (-0.74); pitcher suppresses HR (-0.64). Model score 81; odds Listed +320 - Over 0.5 HR.""", blast="good"),
            row("Bryan Reynolds", "S", "+710", 74, "💎", ["vs Arrighetti"], """Tail: 1 HR, 1 near-HR, 91.6 mph EV. Matchup: Arrighetti RHB split -0.27, HR risk -0.64. Fade: slight split headwind (-0.27); pitcher suppresses HR (-0.64). Model score 74; odds Listed +710 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "SD @ PHI - Walker Buehler (R, SD) vs Cristopher Sanchez (R, PHI)",
        "description": "Tail key data: Park boost +3% (stadium +14%, weather -11%). Walker Buehler (HR risk 0.19, vs LHB -0.38, vs RHB +0.62). Cristopher Sanchez (HR risk -0.92, vs LHB -1.00, vs RHB -0.53).",
        "rows": [
            row("Kyle Schwarber", "L", "+281", 77, "💎", ["vs Buehler"], """Tail: 1 HR, 2 near-HR, 93.4 mph EV. Matchup: Buehler LHB split -0.38, HR risk 0.19. Fade: slight split headwind (-0.38); weather carry headwind (-11%). Model score 77; odds Listed +281 - Over 0.5 HR.""", blast="good"),
            row("Brandon Marsh", "L", "+890", 70, "💎", ["vs Buehler"], """Tail: 0 HR, 94.4 mph EV. Matchup: Buehler LHB split -0.38, HR risk 0.19. Fade: slight split headwind (-0.38); weather carry headwind (-11%). Model score 70; odds Listed +890 - Over 0.5 HR.""", blast="good"),
            row("Bryce Harper", "L", "+432", 77, "💎", ["vs Buehler"], """Tail: 1 HR, 1 near-HR, 95.1 mph EV. Matchup: Buehler LHB split -0.38, HR risk 0.19. Fade: slight split headwind (-0.38); weather carry headwind (-11%). Model score 77; odds Listed +432 - Over 0.5 HR.""", blast="good"),
            row("Jackson Merrill", "L", "+1120", 71, "💎", ["vs Sanchez"], """Tail: 1 HR, 1 near-HR, 89.0 mph EV. Matchup: Sanchez LHB split -1.00, HR risk -0.92. Fade: tough split lane (-1.00); pitcher suppresses HR (-0.92). Model score 71; odds Listed +1120 - Over 0.5 HR.""", blast="good"),
            row("Ty France", "R", "+1020", 78, "💎", ["vs Sanchez"], """Tail: 1 HR, 1 near-HR, 96.5 mph EV. Matchup: Sanchez RHB split -0.53, HR risk -0.92. Fade: tough split lane (-0.53); pitcher suppresses HR (-0.92). Model score 78; odds Listed +1020 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "SF @ MIL - Logan Webb (R, SF) vs Coleman Crow (R, MIL)",
        "description": "Tail key data: Park boost -3% (stadium +11%, weather -14%). Logan Webb (HR risk -0.16, vs LHB -0.10, vs RHB +0.19). Home starter risk unavailable.",
        "rows": [
            row("Garrett Mitchell", "L", "+840", 80, "💎", ["vs Webb"], """Tail: 1 HR, 1 near-HR, 98.5 mph EV. Matchup: Webb LHB split -0.10, HR risk -0.16. Fade: slight split headwind (-0.10); pitcher risk below avg (-0.16). Model score 80; odds Listed +840 - Over 0.5 HR.""", blast="good"),
            row("Jake Bauers", "L", "+600", 85, "⭐ 🌕 💣", ["vs Webb"], """Worst Pickz Favorite. Tail: 2 HR, 2 near-HR, 95.4 mph EV. Matchup: Webb LHB split -0.10, HR risk -0.16. Fade: slight split headwind (-0.10); pitcher risk below avg (-0.16). Model score 85; odds Listed +600 - Over 0.5 HR.""", blast="high"),
            row("Jackson Chourio", "R", "+570", 78, "💎", ["vs Webb"], """Tail: 1 HR, 1 near-HR, 96.1 mph EV. Matchup: Webb RHB split +0.19, HR risk -0.16. Fade: pitcher risk below avg (-0.16); weather carry headwind (-14%). Model score 78; odds Listed +570 - Over 0.5 HR.""", blast="good"),
            row("Eric Haase", "R", "+620", 73, "💎", ["vs Crow"], """Tail: 1 HR, 2 near-HR, 89.2 mph EV. Matchup: Crow split/risk data unavailable. Fade: limited split/risk sample; weather carry headwind (-14%). Model score 73; odds Listed +620 - Over 0.5 HR.""", blast="good"),
            row("Willy Adames", "R", "+472", 74, "💎", ["vs Crow"], """Tail: 0 HR, 2 near-HR, 94.1 mph EV. Matchup: Crow split/risk data unavailable. Fade: limited split/risk sample; weather carry headwind (-14%). Model score 74; odds Listed +472 - Over 0.5 HR.""", blast="good"),
            row("Rafael Devers", "L", "+421", 78, "💎", ["vs Crow"], """Tail: 1 HR, 1 near-HR, 96.2 mph EV. Matchup: Crow split/risk data unavailable. Fade: limited split/risk sample; weather carry headwind (-14%). Model score 78; odds Listed +421 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "TEX @ STL - MacKenzie Gore (R, TEX) vs Andre Pallante (R, STL)",
        "description": "Tail key data: Park boost -20% (stadium -9%, weather -11%). MacKenzie Gore (HR risk -0.13, vs LHB -0.10, vs RHB -0.04). Andre Pallante (HR risk 0.18, vs LHB +0.41, vs RHB -0.13).",
        "rows": [
            row("Nolan Gorman", "L", "N/A", 72, "💎", ["vs Gore"], """Tail: 1 HR, 2 near-HR, 87.0 mph EV. Matchup: Gore LHB split -0.10, HR risk -0.13. Fade: slight split headwind (-0.10); pitcher risk below avg (-0.13). Model score 72; odds Listed prop - Over 0.5 HR.""", blast="good"),
            row("JJ Wetherholt", "L", "+710", 74, "💎", ["vs Gore"], """Tail: 0 HR, 1 near-HR, 95.6 mph EV. Matchup: Gore LHB split -0.10, HR risk -0.13. Fade: slight split headwind (-0.10); pitcher risk below avg (-0.13). Model score 74; odds Listed +710 - Over 0.5 HR.""", blast="good"),
            row("Ivan Herrera", "R", "+650", 74, "💎", ["vs Gore"], """Tail: 1 HR, 1 near-HR, 91.5 mph EV. Matchup: Gore RHB split -0.04, HR risk -0.13. Fade: slight split headwind (-0.04); pitcher risk below avg (-0.13). Model score 74; odds Listed +650 - Over 0.5 HR.""", blast="good"),
            row("Joc Pederson", "L", "+650", 78, "⭐ 🌕 💣", ["vs Pallante"], """Worst Pickz Favorite. Tail: 2 HR, 2 near-HR, 88.3 mph EV. Matchup: Pallante LHB split +0.41, HR risk 0.18. Fade: park/weather net drag (-20%). Model score 78; odds Listed +650 - Over 0.5 HR.""", blast="high"),
            row("Brandon Nimmo", "L", "+750", 70, "💎", ["vs Pallante"], """Tail: 0 HR, 1 near-HR, 92.0 mph EV. Matchup: Pallante LHB split +0.41, HR risk 0.18. Fade: park/weather net drag (-20%); limited recent HR events. Model score 70; odds Listed +750 - Over 0.5 HR.""", blast="good"),
            row("Kyle Higashioka", "R", "N/A", 70, "💎", ["vs Pallante"], """Tail: 1 HR, 1 near-HR, 86.1 mph EV. Matchup: Pallante RHB split -0.13, HR risk 0.18. Fade: slight split headwind (-0.13); park/weather net drag (-20%). Model score 70; odds Listed prop - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "TOR @ ATL - Patrick Corbin (R, TOR) vs Grant Holmes 🧤 (R, ATL)",
        "description": "Tail key data: Park boost -20% (stadium -5%, weather -15%). Patrick Corbin (HR risk -0.16, vs LHB -1.09, vs RHB +0.13). Grant Holmes 🧤 (HR risk 1.34, vs LHB +1.39, vs RHB +0.52).",
        "rows": [
            row("Matt Olson", "L", "+490", 78, "🌕 💣", ["vs Corbin"], """Tail: 2 HR, 2 near-HR, 86.0 mph EV. Matchup: Corbin LHB split -1.09, HR risk -0.16. Fade: tough split lane (-1.09); pitcher risk below avg (-0.16). Model score 78; odds Listed +490 - Over 0.5 HR.""", blast="high"),
            row("Austin Riley", "R", "+620", 75, "💎", ["vs Corbin"], """Tail: 0 HR, 1 near-HR, 97.3 mph EV. Matchup: Corbin RHB split +0.13, HR risk -0.16. Fade: pitcher risk below avg (-0.16); park/weather net drag (-20%). Model score 75; odds Listed +620 - Over 0.5 HR.""", blast="good"),
            row("Jorge Mateo", "R", "+800", 78, "💎", ["vs Corbin"], """Tail: 1 HR, 1 near-HR, 96.2 mph EV. Matchup: Corbin RHB split +0.13, HR risk -0.16. Fade: pitcher risk below avg (-0.16); park/weather net drag (-20%). Model score 78; odds Listed +800 - Over 0.5 HR.""", blast="good"),
            row("Michael Harris II", "L", "+590", 70, "💎", ["vs Corbin"], """Tail: 1 HR, 1 near-HR, 87.0 mph EV. Matchup: Corbin LHB split -1.09, HR risk -0.16. Fade: tough split lane (-1.09); pitcher risk below avg (-0.16). Model score 70; odds Listed +590 - Over 0.5 HR.""", blast="good"),
            row("Jesus Sanchez", "L", "+650", 79, "⭐ 💎", ["vs Holmes"], """Worst Pickz Favorite. Tail: 1 HR, 2 near-HR, 95.2 mph EV. Matchup: Holmes LHB split +1.39, HR risk 1.34. Fade: park/weather net drag (-20%). Model score 79; odds Listed +650 - Over 0.5 HR.""", blast="good"),
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

    out = ROOT / '_games-0603.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
