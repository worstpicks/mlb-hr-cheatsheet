#!/usr/bin/env python3
"""Generate games[] block for 2026-06-06 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Adley Rutschman (S)",
    "Bryce Harper (L)",
    "Byron Buxton (R)",
    "Carlos Cortes (L)",
    "Dominic Canzone (L)",
    "Hunter Goodman (R)",
    "Jackson Chourio (R)",
    "Jacob Young (R)",
    "Jared Young (L)",
    "Jesus Sanchez (L)",
    "Kyle Higashioka (R)",
    "Matt Olson (L)",
    "Michael Massey (L)",
    "Mike Trout (R)",
    "Pete Crow-Armstrong (L)",
    "Spencer Torkelson (R)",
    "Vinnie Pasquantino (L)",
    "Willy Adames (R)",
    "Wilyer Abreu (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BAL",
    "Adrian Del Castillo (L)": "ARI",
    "Andrew Benintendi (L)": "CWS",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Brice Turang (L)": "MIL",
    "Brooks Lee (S)": "MIN",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "Carlos Cortes (L)": "ATH",
    "Carson Benge (L)": "NYM",
    "Casey Schmitt (R)": "SF",
    "Cedric Mullins (L)": "TB",
    "Coby Mayo (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Colt Emerson (L)": "SEA",
    "Connor Norby (R)": "MIA",
    "Corbin Carroll (L)": "ARI",
    "Dominic Canzone (L)": "SEA",
    "Eric Haase (R)": "SF",
    "Esteury Ruiz (R)": "MIA",
    "Eugenio Suarez (R)": "CIN",
    "Ezequiel Tovar (R)": "COL",
    "Freddie Freeman (L)": "LAD",
    "Garrett Mitchell (L)": "MIL",
    "Gavin Sheets (L)": "SD",
    "George Springer (R)": "TOR",
    "Gleyber Torres (R)": "DET",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Isaac Paredes (R)": "HOU",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jacob Young (R)": "WSH",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jarren Duran (L)": "BOS",
    "Jesus Sanchez (L)": "TOR",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Jonathan Aranda (L)": "TB",
    "Jose Ramirez (S)": "CLE",
    "Juan Soto (L)": "NYM",
    "Julio Rodriguez (R)": "SEA",
    "Kerry Carpenter (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Kyle Higashioka (R)": "TEX",
    "Kyle Schwarber (L)": "PHI",
    "MJ Melendez (L)": "NYM",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Mauricio Dubon (R)": "ATL",
    "Michael Conforto (L)": "CHC",
    "Michael Massey (L)": "KC",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Nick Gonzales (R)": "PIT",
    "Nick Kurtz (L)": "ATH",
    "Oneil Cruz (L)": "PIT",
    "Patrick Bailey (S)": "CLE",
    "Paul Goldschmidt (R)": "NYY",
    "Pedro Pages (R)": "STL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rhys Hoskins (R)": "CLE",
    "Ronald Acuna Jr. (R)": "ATL",
    "Ryan Vilade (R)": "TB",
    "Samuel Basallo (L)": "BAL",
    "Seiya Suzuki (R)": "CHC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Steer (R)": "CIN",
    "Spencer Torkelson (R)": "DET",
    "Tristan Gray (L)": "MIN",
    "Vinnie Pasquantino (L)": "KC",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
}

BUM_PITCHERS = {
    "Bachar",
    "Bellozo",
    "Bibee",
    "Imai",
    "Lodolo",
    "Painter",
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
        "title": "ATH @ HOU - Kade Morris (R, ATH) vs Tatsuya Imai 🧤 (R, HOU)",
        "description": "Tail key data: Park boost +4% (stadium +4%, weather +0%). Away starter risk unavailable. Imai 🧤 (HR risk 1.18, vs LHB +1.36, vs RHB -0.15).",
        "rows": [
            row("Yordan Alvarez", "L", "N/A", 98, "🌕 💣", ["vs Morris"], """4 HR, 6 near-HR, 99.1 mph EV. Morris split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Isaac Paredes", "R", "N/A", 84, "🌕 💣", ["vs Morris"], """3 HR, 3 near-HR, 84.4 mph EV. Morris split/risk data unavailable. limited split/risk sample; lighter EV form (84.4 mph).""", blast="high"),
            row("Carlos Cortes", "L", "N/A", 68, "⭐ 💎", ["vs Imai"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 88.1 mph EV. Imai LHB split +1.36, HR risk 1.18.""", blast="good"),
            row("Nick Kurtz", "L", "N/A", 73, "💎", ["vs Imai"], """0 HR, 1 near-HR, 95.4 mph EV. Imai LHB split +1.36, HR risk 1.18. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "BAL @ TOR - Kyle Bradish (R, BAL) vs Spencer Miles (R, TOR)",
        "description": "Tail key data: Park boost +3% (stadium +7%, weather -4%). Bradish (HR risk -0.41, vs LHB -0.62, vs RHB +0.29). Home starter risk unavailable.",
        "rows": [
            row("George Springer", "R", "N/A", 63, "💎", ["vs Bradish"], """0 HR, 89.4 mph EV. Bradish RHB split +0.29, HR risk -0.41. pitcher suppresses HR (-0.41); weather carry headwind (-4%)."""),
            row("Jesus Sanchez", "L", "N/A", 83, "⭐ 💎", ["vs Bradish"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 97.4 mph EV. Bradish LHB split -0.62, HR risk -0.41. tough split lane (-0.62); pitcher suppresses HR (-0.41).""", blast="good"),
            row("Samuel Basallo", "L", "N/A", 79, "💎", ["vs Miles"], """1 HR, 1 near-HR, 97.2 mph EV. Miles split/risk data unavailable. limited split/risk sample; weather carry headwind (-4%).""", blast="good"),
            row("Adley Rutschman", "S", "N/A", 78, "⭐ 💎", ["vs Miles"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.4 mph EV. Miles split/risk data unavailable. limited split/risk sample; weather carry headwind (-4%).""", blast="good"),
            row("Coby Mayo", "R", "N/A", 87, "🌕 💣", ["vs Miles"], """2 HR, 2 near-HR, 96.7 mph EV. Miles split/risk data unavailable. limited split/risk sample; weather carry headwind (-4%).""", blast="high"),
        ],
    },
    {
        "title": "BOS @ NYY - Ranger Suarez (R, BOS) vs Will Warren (R, NYY)",
        "description": "Tail key data: Park boost +21% (stadium +5%, weather +16%). Suarez (HR risk -1.14, vs LHB -0.08, vs RHB -0.98). Warren (HR risk -0.14, vs LHB -0.06, vs RHB +0.00).",
        "rows": [
            row("Paul Goldschmidt", "R", "+410", 81, "🌕 💣", ["vs Suarez"], """2 HR, 2 near-HR, 91.0 mph EV. Suarez RHB split -0.98, HR risk -1.14. tough split lane (-0.98); pitcher suppresses HR (-1.14).""", blast="high"),
            row("Ben Rice", "L", "+360", 67, "💎", ["vs Suarez"], """0 HR, 1 near-HR, 91.3 mph EV. Suarez LHB split -0.08, HR risk -1.14. slight split headwind (-0.08); pitcher suppresses HR (-1.14)."""),
            row("Jarren Duran", "L", "+490", 84, "🌕 💣", ["vs Warren"], """2 HR, 3 near-HR, 92.1 mph EV. Warren LHB split -0.06, HR risk -0.14. slight split headwind (-0.06); pitcher risk below avg (-0.14).""", blast="high"),
            row("Wilyer Abreu", "L", "+410", 73, "⭐ 💎", ["vs Warren"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.4 mph EV. Warren LHB split -0.06, HR risk -0.14. slight split headwind (-0.06); pitcher risk below avg (-0.14).""", blast="good"),
            row("Willson Contreras", "R", "+390", 81, "🌕 💣", ["vs Warren"], """2 HR, 2 near-HR, 91.2 mph EV. Warren RHB split +0.00, HR risk -0.14. pitcher risk below avg (-0.14).""", blast="high"),
        ],
    },
    {
        "title": "CIN @ STL - Nick Lodolo 🧤 (R, CIN) vs Matthew Liberatore (R, STL)",
        "description": "Tail key data: Park boost +4% (stadium -9%, weather +13%). Lodolo 🧤 (HR risk 1.28, vs LHB -0.80, vs RHB +1.70). Liberatore (HR risk 0.10, vs LHB +1.47, vs RHB -0.20).",
        "rows": [
            row("JJ Wetherholt", "L", "N/A", 74, "💎", ["vs Lodolo"], """0 HR, 1 near-HR, 95.6 mph EV. Lodolo LHB split -0.80, HR risk 1.28. tough split lane (-0.80); park suppresses carry (-9%).""", blast="good"),
            row("Pedro Pages", "R", "N/A", 68, "💎", ["vs Lodolo"], """0 HR, 1 near-HR, 91.6 mph EV. Lodolo RHB split +1.70, HR risk 1.28. park suppresses carry (-9%); limited recent HR events."""),
            row("Eugenio Suarez", "R", "N/A", 64, "💎", ["vs Liberatore"], """0 HR, 90.2 mph EV. Liberatore RHB split -0.20, HR risk 0.10. slight split headwind (-0.20); park suppresses carry (-9%)."""),
            row("Spencer Steer", "R", "N/A", 82, "🌕 💣", ["vs Liberatore"], """2 HR, 3 near-HR, 89.8 mph EV. Liberatore RHB split -0.20, HR risk 0.10. slight split headwind (-0.20); park suppresses carry (-9%).""", blast="high"),
        ],
    },
    {
        "title": "CLE @ TEX - Tanner Bibee 🧤 (R, CLE) vs Jack Leiter (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -10%, weather -1%). Bibee 🧤 (HR risk 1.07, vs LHB +1.01, vs RHB +0.55). Leiter (HR risk -0.07, vs LHB +0.18, vs RHB -0.27).",
        "rows": [
            row("Brandon Nimmo", "L", "+490", 84, "🌕 💣", ["vs Bibee"], """1 HR, 5 near-HR, 92.3 mph EV. Bibee LHB split +1.01, HR risk 1.07. park/weather net drag (-11%).""", blast="high"),
            row("Kyle Higashioka", "R", "N/A", 78, "⭐ 🌕 💣", ["vs Bibee"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 86.4 mph EV. Bibee RHB split +0.55, HR risk 1.07. park/weather net drag (-11%); lighter EV form (86.4 mph).""", blast="high"),
            row("Joc Pederson", "L", "+310", 86, "🌕 💣", ["vs Bibee"], """3 HR, 3 near-HR, 89.6 mph EV. Bibee LHB split +1.01, HR risk 1.07. park/weather net drag (-11%).""", blast="high"),
            row("Rhys Hoskins", "R", "+360", 70, "💎", ["vs Leiter"], """1 HR, 1 near-HR, 81.8 mph EV. Leiter RHB split -0.27, HR risk -0.07. slight split headwind (-0.27); pitcher risk below avg (-0.07).""", blast="good"),
            row("Patrick Bailey", "S", "+760", 79, "🌕 💣", ["vs Leiter"], """1 HR, 4 near-HR, 88.7 mph EV. Leiter RHB split -0.27, HR risk -0.07. slight split headwind (-0.27); pitcher risk below avg (-0.07).""", blast="high"),
            row("Jose Ramirez", "S", "+360", 73, "💎", ["vs Leiter"], """1 HR, 1 near-HR, 90.7 mph EV. Leiter RHB split -0.27, HR risk -0.07. slight split headwind (-0.27); pitcher risk below avg (-0.07).""", blast="good"),
        ],
    },
    {
        "title": "CWS @ PHI - Brandon Eisert (R, CWS) vs Andrew Painter 🧤 (R, PHI)",
        "description": "Tail key data: Park boost data unavailable. Eisert (HR risk -0.05, vs LHB +0.49, vs RHB -0.40). Painter 🧤 (HR risk 1.01, vs LHB +0.02, vs RHB +1.75).",
        "rows": [
            row("Bryce Harper", "L", "N/A", 77, "⭐ 💎", ["vs Eisert"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 99.2 mph EV. Eisert LHB split +0.49, HR risk -0.05. pitcher risk below avg (-0.05); limited recent HR events.""", blast="good"),
            row("Brandon Marsh", "L", "N/A", 70, "💎", ["vs Eisert"], """1 HR, 1 near-HR, 86.7 mph EV. Eisert LHB split +0.49, HR risk -0.05. pitcher risk below avg (-0.05); lighter EV form (86.7 mph).""", blast="good"),
            row("Kyle Schwarber", "L", "N/A", 75, "💎", ["vs Eisert"], """1 HR, 1 near-HR, 92.7 mph EV. Eisert LHB split +0.49, HR risk -0.05. pitcher risk below avg (-0.05).""", blast="good"),
            row("Andrew Benintendi", "L", "N/A", 84, "🌕 💣", ["vs Painter"], """2 HR, 3 near-HR, 91.8 mph EV. Painter LHB split +0.02, HR risk 1.01.""", blast="high"),
            row("Colson Montgomery", "L", "N/A", 70, "💎", ["vs Painter"], """1 HR, 1 near-HR, 88.3 mph EV. Painter LHB split +0.02, HR risk 1.01.""", blast="good"),
            row("Miguel Vargas", "R", "N/A", 78, "💎", ["vs Painter"], """1 HR, 2 near-HR, 93.8 mph EV. Painter RHB split +1.75, HR risk 1.01.""", blast="good"),
        ],
    },
    {
        "title": "KC @ MIN - Luinder Avila (R, KC) vs Joe Ryan (R, MIN)",
        "description": "Tail key data: Park boost -5% (stadium -7%, weather +1%). Avila (HR risk -1.02, vs LHB -0.24, vs RHB -1.19). Ryan (HR risk 0.16, vs LHB +0.22, vs RHB -0.04).",
        "rows": [
            row("Byron Buxton", "R", "+157", 83, "⭐ 🌕 💣", ["vs Avila"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.4 mph EV. Avila RHB split -1.19, HR risk -1.02. tough split lane (-1.19); pitcher suppresses HR (-1.02).""", blast="high"),
            row("Kody Clemens", "L", "+185", 88, "🌕 💣", ["vs Avila"], """2 HR, 3 near-HR, 95.7 mph EV. Avila LHB split -0.24, HR risk -1.02. slight split headwind (-0.24); pitcher suppresses HR (-1.02).""", blast="high"),
            row("Brooks Lee", "S", "+334", 78, "🌕 💣", ["vs Avila"], """2 HR, 2 near-HR, 86.8 mph EV. Avila RHB split -1.19, HR risk -1.02. tough split lane (-1.19); pitcher suppresses HR (-1.02).""", blast="high"),
            row("Tristan Gray", "L", "N/A", 79, "💎", ["vs Avila"], """1 HR, 2 near-HR, 94.8 mph EV. Avila LHB split -0.24, HR risk -1.02. slight split headwind (-0.24); pitcher suppresses HR (-1.02).""", blast="good"),
            row("Michael Massey", "L", "+309", 82, "⭐ 🌕 💣", ["vs Ryan"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.7 mph EV. Ryan LHB split +0.22, HR risk 0.16. park/weather net drag (-5%).""", blast="high"),
            row("Bobby Witt Jr.", "R", "+245", 70, "💎", ["vs Ryan"], """0 HR, 1 near-HR, 92.2 mph EV. Ryan RHB split -0.04, HR risk 0.16. slight split headwind (-0.04); park/weather net drag (-5%).""", blast="good"),
            row("Vinnie Pasquantino", "L", "+214", 73, "⭐ 💎", ["vs Ryan"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 89.4 mph EV. Ryan LHB split +0.22, HR risk 0.16. park/weather net drag (-5%).""", blast="good"),
            row("Jac Caglianone", "L", "+232", 75, "💎", ["vs Ryan"], """0 HR, 99.0 mph EV. Ryan LHB split +0.22, HR risk 0.16. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "LAA @ LAD - Jack Kochanowicz (R, LAA) vs Yoshinobu Yamamoto (R, LAD)",
        "description": "Tail key data: Park boost +12% (stadium +19%, weather -7%). Away starter risk unavailable. Home starter risk unavailable.",
        "rows": [
            row("Shohei Ohtani", "L", "+280", 78, "💎", ["vs Kochanowicz"], """1 HR, 1 near-HR, 95.6 mph EV. Kochanowicz split/risk data unavailable. limited split/risk sample; weather carry headwind (-7%).""", blast="good"),
            row("Freddie Freeman", "L", "+520", 78, "🌕 💣", ["vs Kochanowicz"], """2 HR, 2 near-HR, 86.8 mph EV. Kochanowicz split/risk data unavailable. limited split/risk sample; weather carry headwind (-7%).""", blast="high"),
            row("Mike Trout", "R", "+320", 73, "⭐ 💎", ["vs Yamamoto"], """Worst Pickz Favorite. 0 HR, 3 near-HR, 90.6 mph EV. Yamamoto split/risk data unavailable. limited split/risk sample; weather carry headwind (-7%).""", blast="good"),
            row("Jo Adell", "R", "+430", 80, "🌕 💣", ["vs Yamamoto"], """2 HR, 2 near-HR, 90.2 mph EV. Yamamoto split/risk data unavailable. limited split/risk sample; weather carry headwind (-7%).""", blast="high"),
        ],
    },
    {
        "title": "MIL @ COL - Jacob Misiorowski (R, MIL) vs Valente Bellozo 🧤 (R, COL)",
        "description": "Tail key data: Park boost +19% (stadium +20%, weather -1%). Misiorowski (HR risk -1.35, vs LHB -0.85, vs RHB -0.97). Bellozo 🧤 (HR risk 1.09, vs LHB +0.68, vs RHB +1.15).",
        "rows": [
            row("Hunter Goodman", "R", "N/A", 94, "⭐ 🌕 💣", ["vs Misiorowski"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 98.3 mph EV. Misiorowski RHB split -0.97, HR risk -1.35. tough split lane (-0.97); pitcher suppresses HR (-1.35).""", blast="high"),
            row("Ezequiel Tovar", "R", "N/A", 70, "💎", ["vs Misiorowski"], """1 HR, 1 near-HR, 82.9 mph EV. Misiorowski RHB split -0.97, HR risk -1.35. tough split lane (-0.97); pitcher suppresses HR (-1.35).""", blast="good"),
            row("Willi Castro", "S", "N/A", 83, "💎", ["vs Misiorowski"], """1 HR, 2 near-HR, 98.7 mph EV. Misiorowski RHB split -0.97, HR risk -1.35. tough split lane (-0.97); pitcher suppresses HR (-1.35).""", blast="good"),
            row("Jackson Chourio", "R", "+399", 96, "⭐ 🌕 💣", ["vs Bellozo"], """Worst Pickz Favorite. 3 HR, 5 near-HR, 96.4 mph EV. Bellozo RHB split +1.15, HR risk 1.09.""", blast="high"),
            row("Jake Bauers", "L", "+375", 73, "💎", ["vs Bellozo"], """1 HR, 1 near-HR, 91.4 mph EV. Bellozo LHB split +0.68, HR risk 1.09.""", blast="good"),
            row("Garrett Mitchell", "L", "+505", 78, "💎", ["vs Bellozo"], """1 HR, 1 near-HR, 96.0 mph EV. Bellozo LHB split +0.68, HR risk 1.09.""", blast="good"),
            row("Brice Turang", "L", "+469", 64, "💎", ["vs Bellozo"], """0 HR, 89.8 mph EV. Bellozo LHB split +0.68, HR risk 1.09. limited recent HR events."""),
        ],
    },
    {
        "title": "NYM @ SD - Nolan McLean (R, NYM) vs Griffin Canning (R, SD)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +2%). McLean (HR risk 0.32, vs LHB +0.01, vs RHB +0.53). Canning (HR risk 0.68, vs LHB +1.25, vs RHB -0.96).",
        "rows": [
            row("Gavin Sheets", "L", "+520", 64, "💎", ["vs McLean"], """0 HR, 89.6 mph EV. McLean LHB split +0.01, HR risk 0.32. limited recent HR events."""),
            row("Manny Machado", "R", "+502", 77, "💎", ["vs McLean"], """1 HR, 2 near-HR, 92.7 mph EV. McLean RHB split +0.53, HR risk 0.32.""", blast="good"),
            row("Jackson Merrill", "L", "+570", 62, "💎", ["vs McLean"], """0 HR, 79.3 mph EV. McLean LHB split +0.01, HR risk 0.32. limited recent HR events; lighter EV form (79.3 mph)."""),
            row("Juan Soto", "L", "+340", 84, "🌕 💣", ["vs Canning"], """2 HR, 2 near-HR, 93.6 mph EV. Canning LHB split +1.25, HR risk 0.68.""", blast="high"),
            row("Carson Benge", "L", "+760", 73, "💎", ["vs Canning"], """1 HR, 1 near-HR, 90.8 mph EV. Canning LHB split +1.25, HR risk 0.68.""", blast="good"),
            row("Jared Young", "L", "+570", 82, "🚀 ⭐ 💎", ["vs Canning"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 101.0 mph EV. Canning LHB split +1.25, HR risk 0.68.""", blast="good"),
            row("MJ Melendez", "L", "+337", 78, "💎", ["vs Canning"], """1 HR, 1 near-HR, 95.6 mph EV. Canning LHB split +1.25, HR risk 0.68.""", blast="good"),
        ],
    },
    {
        "title": "PIT @ ATL - Braxton Ashcraft (R, PIT) vs Spencer Strider (R, ATL)",
        "description": "Tail key data: Park boost +2% (stadium -1%, weather +3%). Ashcraft (HR risk -0.52, vs LHB -0.09, vs RHB -0.64). Strider (HR risk 0.74, vs LHB +1.04, vs RHB -0.41).",
        "rows": [
            row("Matt Olson", "L", "+290", 78, "⭐ 💎", ["vs Ashcraft"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.2 mph EV. Ashcraft LHB split -0.09, HR risk -0.52. slight split headwind (-0.09); pitcher suppresses HR (-0.52).""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+498", 91, "🌕 💣", ["vs Ashcraft"], """4 HR, 4 near-HR, 89.1 mph EV. Ashcraft RHB split -0.64, HR risk -0.52. tough split lane (-0.64); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Mauricio Dubon", "R", "+1220", 79, "🌕 💣", ["vs Ashcraft"], """2 HR, 2 near-HR, 89.3 mph EV. Ashcraft RHB split -0.64, HR risk -0.52. tough split lane (-0.64); pitcher suppresses HR (-0.52).""", blast="high"),
            row("Brandon Lowe", "L", "+320", 90, "🌕 💣", ["vs Strider"], """2 HR, 5 near-HR, 94.0 mph EV. Strider LHB split +1.04, HR risk 0.74.""", blast="high"),
            row("Oneil Cruz", "L", "+290", 88, "🌕 💣", ["vs Strider"], """2 HR, 3 near-HR, 95.8 mph EV. Strider LHB split +1.04, HR risk 0.74.""", blast="high"),
            row("Nick Gonzales", "R", "+790", 83, "🌕 💣", ["vs Strider"], """2 HR, 3 near-HR, 91.1 mph EV. Strider RHB split -0.41, HR risk 0.74. tough split lane (-0.41).""", blast="high"),
        ],
    },
    {
        "title": "SEA @ DET - Bryce Miller (R, SEA) vs Keider Montero (R, DET)",
        "description": "Tail key data: Park boost +11% (stadium -10%, weather +21%). Miller (HR risk -0.63, vs LHB -1.22, vs RHB +0.63). Montero (HR risk 0.20, vs LHB +0.39, vs RHB -0.15).",
        "rows": [
            row("Gleyber Torres", "R", "+920", 70, "💎", ["vs Miller"], """1 HR, 1 near-HR, 86.7 mph EV. Miller RHB split +0.63, HR risk -0.63. pitcher suppresses HR (-0.63); park suppresses carry (-10%).""", blast="good"),
            row("Kerry Carpenter", "L", "+390", 80, "🌕 💣", ["vs Miller"], """2 HR, 2 near-HR, 89.6 mph EV. Miller LHB split -1.22, HR risk -0.63. tough split lane (-1.22); pitcher suppresses HR (-0.63).""", blast="high"),
            row("Spencer Torkelson", "R", "+440", 81, "⭐ 🌕 💣", ["vs Miller"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.6 mph EV. Miller RHB split +0.63, HR risk -0.63. pitcher suppresses HR (-0.63); park suppresses carry (-10%).""", blast="high"),
            row("Julio Rodriguez", "R", "+390", 90, "🌕 💣", ["vs Montero"], """4 HR, 4 near-HR, 88.3 mph EV. Montero RHB split -0.15, HR risk 0.20. slight split headwind (-0.15); park suppresses carry (-10%).""", blast="high"),
            row("Dominic Canzone", "L", "+310", 79, "⭐ 💎", ["vs Montero"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.4 mph EV. Montero LHB split +0.39, HR risk 0.20. park suppresses carry (-10%).""", blast="good"),
            row("Colt Emerson", "L", "+710", 78, "🌕 💣", ["vs Montero"], """2 HR, 2 near-HR, 87.6 mph EV. Montero LHB split +0.39, HR risk 0.20. park suppresses carry (-10%); lighter EV form (87.6 mph).""", blast="high"),
        ],
    },
    {
        "title": "SF @ CHC - Landen Roupp (R, SF) vs Ben Brown (R, CHC)",
        "description": "Tail key data: Park boost +29% (stadium -2%, weather +31%). Roupp (HR risk -0.96, vs LHB -1.17, vs RHB -0.11). Brown (HR risk -0.76, vs LHB -0.54, vs RHB -0.44).",
        "rows": [
            row("Seiya Suzuki", "R", "+660", 79, "💎", ["vs Roupp"], """1 HR, 1 near-HR, 97.1 mph EV. Roupp RHB split -0.11, HR risk -0.96. slight split headwind (-0.11); pitcher suppresses HR (-0.96).""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+478", 78, "🚀 ⭐ 💎", ["vs Roupp"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 101.6 mph EV. Roupp LHB split -1.17, HR risk -0.96. tough split lane (-1.17); pitcher suppresses HR (-0.96).""", blast="good"),
            row("Michael Conforto", "L", "N/A", 85, "🌕 💣", ["vs Roupp"], """2 HR, 2 near-HR, 95.0 mph EV. Roupp LHB split -1.17, HR risk -0.96. tough split lane (-1.17); pitcher suppresses HR (-0.96).""", blast="high"),
            row("Ian Happ", "S", "+480", 76, "💎", ["vs Roupp"], """0 HR, 1 near-HR, 98.0 mph EV. Roupp RHB split -0.11, HR risk -0.96. slight split headwind (-0.11); pitcher suppresses HR (-0.96).""", blast="good"),
            row("Eric Haase", "R", "N/A", 80, "🌕 💣", ["vs Brown"], """2 HR, 2 near-HR, 90.2 mph EV. Brown RHB split -0.44, HR risk -0.76. tough split lane (-0.44); pitcher suppresses HR (-0.76).""", blast="high"),
            row("Bryce Eldridge", "L", "+820", 70, "💎", ["vs Brown"], """0 HR, 2 near-HR, 89.7 mph EV. Brown LHB split -0.54, HR risk -0.76. tough split lane (-0.54); pitcher suppresses HR (-0.76).""", blast="good"),
            row("Willy Adames", "R", "+517", 91, "⭐ 🌕 💣", ["vs Brown"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 95.3 mph EV. Brown RHB split -0.44, HR risk -0.76. tough split lane (-0.44); pitcher suppresses HR (-0.76).""", blast="high"),
            row("Casey Schmitt", "R", "+510", 70, "💎", ["vs Brown"], """1 HR, 1 near-HR, 88.4 mph EV. Brown RHB split -0.44, HR risk -0.76. tough split lane (-0.44); pitcher suppresses HR (-0.76).""", blast="good"),
        ],
    },
    {
        "title": "TB @ MIA - Shane McClanahan (R, TB) vs Lake Bachar 🧤 (R, MIA)",
        "description": "Tail key data: Park boost -12% (stadium -13%, weather +1%). McClanahan (HR risk -0.63, vs LHB -1.45, vs RHB -0.09). Bachar 🧤 (HR risk 1.27, vs LHB +0.20, vs RHB +1.38).",
        "rows": [
            row("Heriberto Hernandez", "R", "N/A", 81, "🌕 💣", ["vs McClanahan"], """2 HR, 2 near-HR, 90.9 mph EV. McClanahan RHB split -0.09, HR risk -0.63. slight split headwind (-0.09); pitcher suppresses HR (-0.63).""", blast="high"),
            row("Esteury Ruiz", "R", "N/A", 78, "💎", ["vs McClanahan"], """1 HR, 3 near-HR, 92.5 mph EV. McClanahan RHB split -0.09, HR risk -0.63. slight split headwind (-0.09); pitcher suppresses HR (-0.63).""", blast="good"),
            row("Connor Norby", "R", "N/A", 66, "💎", ["vs McClanahan"], """0 HR, 1 near-HR, 90.3 mph EV. McClanahan RHB split -0.09, HR risk -0.63. slight split headwind (-0.09); pitcher suppresses HR (-0.63)."""),
            row("Jonathan Aranda", "L", "N/A", 90, "🌕 💣", ["vs Bachar"], """3 HR, 4 near-HR, 91.7 mph EV. Bachar LHB split +0.20, HR risk 1.27. park/weather net drag (-12%).""", blast="high"),
            row("Cedric Mullins", "L", "N/A", 85, "🌕 💣", ["vs Bachar"], """2 HR, 2 near-HR, 95.0 mph EV. Bachar LHB split +0.20, HR risk 1.27. park/weather net drag (-12%).""", blast="high"),
            row("Yandy Diaz", "R", "N/A", 81, "💎", ["vs Bachar"], """1 HR, 1 near-HR, 98.7 mph EV. Bachar RHB split +1.38, HR risk 1.27. park/weather net drag (-12%).""", blast="good"),
            row("Ryan Vilade", "R", "N/A", 80, "🌕 💣", ["vs Bachar"], """2 HR, 2 near-HR, 89.8 mph EV. Bachar RHB split +1.38, HR risk 1.27. park/weather net drag (-12%).""", blast="high"),
        ],
    },
    {
        "title": "WSH @ ARI - Zack Littell (R, WSH) vs Eduardo Rodriguez (R, ARI)",
        "description": "Tail key data: Park boost data unavailable. Littell (HR risk 0.52, vs LHB +0.78, vs RHB -0.12). Rodriguez (HR risk -0.81, vs LHB -0.55, vs RHB -0.50).",
        "rows": [
            row("Corbin Carroll", "L", "N/A", 77, "💎", ["vs Littell"], """1 HR, 2 near-HR, 92.8 mph EV. Littell LHB split +0.78, HR risk 0.52.""", blast="good"),
            row("Adrian Del Castillo", "L", "N/A", 70, "💎", ["vs Littell"], """1 HR, 1 near-HR, 83.8 mph EV. Littell LHB split +0.78, HR risk 0.52. lighter EV form (83.8 mph).""", blast="good"),
            row("James Wood", "L", "N/A", 76, "💎", ["vs Rodriguez"], """1 HR, 1 near-HR, 93.6 mph EV. Rodriguez LHB split -0.55, HR risk -0.81. tough split lane (-0.55); pitcher suppresses HR (-0.81).""", blast="good"),
            row("Jacob Young", "R", "N/A", 75, "⭐ 💎", ["vs Rodriguez"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 97.3 mph EV. Rodriguez RHB split -0.50, HR risk -0.81. tough split lane (-0.50); pitcher suppresses HR (-0.81).""", blast="good"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-06")

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

    out = ROOT / '_games-0606.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
