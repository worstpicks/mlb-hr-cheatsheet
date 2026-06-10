#!/usr/bin/env python3
"""Generate games[] block for 2026-06-10 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Adley Rutschman (S)",
    "Bobby Witt Jr. (R)",
    "Brandon Marsh (L)",
    "Brent Rooker (R)",
    "Corbin Carroll (L)",
    "Dillon Dingler (R)",
    "Dominic Canzone (L)",
    "Freddie Freeman (L)",
    "Jake Bauers (L)",
    "Jazz Chisholm Jr. (L)",
    "Junior Caminero (R)",
    "Kyle Stowers (L)",
    "Nick Kurtz (L)",
    "Rafael Devers (L)",
    "Rhys Hoskins (R)",
    "Riley Greene (L)",
    "Samuel Basallo (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Alex Jackson (R)",
    "Cam Smith (R)",
    "Chad Stevens (R)",
    "Colton Cowser (L)",
    "Dalton Rushing (L)",
    "Dylan Crews (R)",
    "Garrett Mitchell (L)",
    "Hunter Feduccia (L)",
    "Jeremy Pena (R)",
    "Matt McLain (R)",
    "Yohendrick Pinango (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BAL",
    "Alec Burleson (L)": "STL",
    "Alex Jackson (R)": "MIN",
    "Andrew Benintendi (L)": "CWS",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Brayan Rocchio (S)": "CLE",
    "Brent Rooker (R)": "ATH",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Cam Smith (R)": "HOU",
    "Chad Stevens (R)": "COL",
    "Colson Montgomery (L)": "CWS",
    "Colt Keith (L)": "DET",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Dylan Crews (R)": "WSH",
    "Edmundo Sosa (R)": "PHI",
    "Freddie Freeman (L)": "LAD",
    "Freddy Fermin (R)": "SD",
    "Gabriel Moreno (R)": "ARI",
    "Garrett Mitchell (L)": "MIL",
    "Henry Davis (R)": "PIT",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "TB",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "J.T. Realmuto (R)": "PHI",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Holliday (L)": "BAL",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jarren Duran (L)": "BOS",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jeremy Pena (R)": "HOU",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Jordan Walker (R)": "STL",
    "Jose Ramirez (S)": "CLE",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kerry Carpenter (L)": "DET",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Luis Garcia Jr. (L)": "WSH",
    "Luke Raley (L)": "SEA",
    "MJ Melendez (L)": "NYM",
    "Marcell Ozuna (R)": "PIT",
    "Marcus Semien (R)": "NYM",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Nick Kurtz (L)": "ATH",
    "Oneil Cruz (L)": "PIT",
    "Otto Lopez (R)": "MIA",
    "Owen Caissie (L)": "MIA",
    "Patrick Wisdom (R)": "SEA",
    "Paul Goldschmidt (R)": "NYY",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Randy Arozarena (R)": "SEA",
    "Rhys Hoskins (R)": "CLE",
    "Riley Greene (L)": "DET",
    "Ryan O'Hearn (L)": "PIT",
    "Samuel Basallo (L)": "BAL",
    "Starling Marte (R)": "KC",
    "Trent Grisham (L)": "NYY",
    "Tyler Stephenson (R)": "CIN",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Yandy Diaz (R)": "TB",
    "Yohendrick Pinango (L)": "TOR",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_PITCHERS = {
    "Griffin",
    "Imanaga",
    "Scherzer",
    "Singer",
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
        "title": "ARI @ MIA - Ryne Nelson (R, ARI) vs Ryan Gusto (R, MIA)",
        "description": "Tail key data: Park boost -14% (stadium -13%, weather -1%). Nelson (HR risk 0.39, vs LHB +0.15, vs RHB +0.64). Gusto (HR risk -0.62, vs LHB -0.26, vs RHB -0.43).",
        "rows": [
            row("Kyle Stowers", "L", "+470", 78, "⭐ 💎", ["vs Nelson"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.7 mph EV. Nelson LHB split +0.15, HR risk 0.39. park/weather net drag (-14%).""", blast="good"),
            row("Heriberto Hernandez", "R", "N/A", 70, "💎", ["vs Nelson"], """0 HR, 93.5 mph EV. Nelson RHB split +0.64, HR risk 0.39. park/weather net drag (-14%); limited recent HR events.""", blast="good"),
            row("Otto Lopez", "R", "+830", 66, "💎", ["vs Nelson"], """0 HR, 91.5 mph EV. Nelson RHB split +0.64, HR risk 0.39. park/weather net drag (-14%); limited recent HR events."""),
            row("Owen Caissie", "L", "+680", 78, "💎", ["vs Nelson"], """0 HR, 1 near-HR, 99.6 mph EV. Nelson LHB split +0.15, HR risk 0.39. park/weather net drag (-14%); limited recent HR events.""", blast="good"),
            row("Corbin Carroll", "L", "+425", 88, "⭐ 🌕 💣", ["vs Gusto"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.7 mph EV. Gusto LHB split -0.26, HR risk -0.62. slight split headwind (-0.26); pitcher suppresses HR (-0.62).""", blast="high"),
            row("Gabriel Moreno", "R", "+1050", 72, "💎", ["vs Gusto"], """1 HR, 1 near-HR, 89.6 mph EV. Gusto RHB split -0.43, HR risk -0.62. tough split lane (-0.43); pitcher suppresses HR (-0.62).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ CWS - Chris Sale (L, ATL) vs Davis Martin (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Sale (HR risk -1.04, vs LHB -0.26, vs RHB -0.98). Home starter risk unavailable.",
        "rows": [
            row("Randal Grichuk", "R", "+410", 70, "💎", ["vs Sale"], """1 HR, 1 near-HR, 83.4 mph EV. Sale RHB split -0.98, HR risk -1.04. tough split lane (-0.98); pitcher suppresses HR (-1.04).""", blast="good"),
            row("Andrew Benintendi", "L", "N/A", 62, "💎", ["vs Sale"], """0 HR, 77.4 mph EV. Sale LHB split -0.26, HR risk -1.04. slight split headwind (-0.26); pitcher suppresses HR (-1.04)."""),
            row("Miguel Vargas", "R", "+410", 78, "💎", ["vs Sale"], """1 HR, 1 near-HR, 95.5 mph EV. Sale RHB split -0.98, HR risk -1.04. tough split lane (-0.98); pitcher suppresses HR (-1.04).""", blast="good"),
            row("Colson Montgomery", "L", "+680", 69, "💎", ["vs Sale"], """0 HR, 2 near-HR, 89.0 mph EV. Sale LHB split -0.26, HR risk -1.04. slight split headwind (-0.26); pitcher suppresses HR (-1.04).""", blast="good"),
            row("Matt Olson", "L", "+358", 78, "💎", ["vs Martin"], """1 HR, 1 near-HR, 96.2 mph EV. Martin split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Michael Harris II", "L", "+422", 78, "💎", ["vs Martin"], """1 HR, 2 near-HR, 94.2 mph EV. Martin split/risk data unavailable. limited split/risk sample.""", blast="good"),
        ],
    },
    {
        "title": "BOS @ TB - Jake Bennett (L, BOS) vs Drew Rasmussen (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -3%, weather +1%). Away starter risk unavailable. Rasmussen (HR risk -0.62, vs LHB -0.06, vs RHB -1.07).",
        "rows": [
            row("Junior Caminero", "R", "+456", 77, "⭐ 💎", ["vs Bennett"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 99.2 mph EV. Bennett split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Hunter Feduccia", "L", "N/A", 69, "💎", ["vs Bennett"], """Worst Pickz Hidden Gem. 0 HR, 92.7 mph EV. Bennett split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Yandy Diaz", "R", "+543", 80, "💎", ["vs Bennett"], """1 HR, 3 near-HR, 94.5 mph EV. Bennett split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Jarren Duran", "L", "+710", 90, "🌕 💣", ["vs Rasmussen"], """3 HR, 4 near-HR, 91.8 mph EV. Rasmussen LHB split -0.06, HR risk -0.62. slight split headwind (-0.06); pitcher suppresses HR (-0.62).""", blast="high"),
            row("Willson Contreras", "R", "+520", 72, "💎", ["vs Rasmussen"], """1 HR, 2 near-HR, 88.1 mph EV. Rasmussen RHB split -1.07, HR risk -0.62. tough split lane (-1.07); pitcher suppresses HR (-0.62).""", blast="good"),
            row("Wilyer Abreu", "L", "+558", 76, "💎", ["vs Rasmussen"], """1 HR, 2 near-HR, 91.9 mph EV. Rasmussen LHB split -0.06, HR risk -0.62. slight split headwind (-0.06); pitcher suppresses HR (-0.62).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ COL - Shota Imanaga 🧤 (L, CHC) vs Michael Lorenzen (R, COL)",
        "description": "Tail key data: Park boost +24% (stadium +21%, weather +3%). Imanaga 🧤 (HR risk 1.56, vs LHB +0.98, vs RHB +1.41). Lorenzen (HR risk 0.35, vs LHB +0.71, vs RHB -0.10).",
        "rows": [
            row("Hunter Goodman", "R", "+235", 70, "💎", ["vs Imanaga"], """1 HR, 1 near-HR, 87.3 mph EV. Imanaga RHB split +1.41, HR risk 1.56. lighter EV form (87.3 mph).""", blast="good"),
            row("Kyle Karros", "R", "+790", 76, "💎", ["vs Imanaga"], """0 HR, 2 near-HR, 95.5 mph EV. Imanaga RHB split +1.41, HR risk 1.56.""", blast="good"),
            row("Chad Stevens", "R", "+870", 78, "🚀 💎", ["vs Imanaga"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 100.0 mph EV. Imanaga RHB split +1.41, HR risk 1.56. limited recent HR events.""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+280", 87, "🌕 💣", ["vs Lorenzen"], """2 HR, 4 near-HR, 93.1 mph EV. Lorenzen LHB split +0.71, HR risk 0.35.""", blast="high"),
            row("Ian Happ", "S", "+284", 88, "🌕 💣", ["vs Lorenzen"], """2 HR, 3 near-HR, 95.6 mph EV. Lorenzen RHB split -0.10, HR risk 0.35. slight split headwind (-0.10).""", blast="high"),
            row("Michael Conforto", "L", "N/A", 75, "💎", ["vs Lorenzen"], """1 HR, 2 near-HR, 91.2 mph EV. Lorenzen LHB split +0.71, HR risk 0.35.""", blast="good"),
        ],
    },
    {
        "title": "CIN @ SD - Brady Singer 🧤 (R, CIN) vs Michael King (R, SD)",
        "description": "Tail key data: Park boost +1% (stadium -5%, weather +6%). Singer 🧤 (HR risk 1.57, vs LHB +1.41, vs RHB +0.48). King (HR risk -0.06, vs LHB +0.06, vs RHB -0.10).",
        "rows": [
            row("Freddy Fermin", "R", "+800", 71, "💎", ["vs Singer"], """1 HR, 1 near-HR, 89.1 mph EV. Singer RHB split +0.48, HR risk 1.57.""", blast="good"),
            row("JJ Bleday", "L", "+490", 76, "💎", ["vs King"], """1 HR, 1 near-HR, 93.7 mph EV. King LHB split +0.06, HR risk -0.06. pitcher risk below avg (-0.06).""", blast="good"),
            row("Matt McLain", "R", "+790", 83, "🌕 💣 💎", ["vs King"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 92.6 mph EV. King RHB split -0.10, HR risk -0.06. slight split headwind (-0.10); pitcher risk below avg (-0.06).""", blast="high"),
            row("Tyler Stephenson", "R", "+880", 82, "🌕 💣", ["vs King"], """2 HR, 2 near-HR, 91.6 mph EV. King RHB split -0.10, HR risk -0.06. slight split headwind (-0.10); pitcher risk below avg (-0.06).""", blast="high"),
        ],
    },
    {
        "title": "HOU @ LAA - Peter Lambert (R, HOU) vs Reid Detmers (L, LAA)",
        "description": "Tail key data: Park boost +7% (stadium +7%, weather +0%). Lambert (HR risk -0.57, vs LHB -0.90, vs RHB +0.46). Detmers (HR risk -0.38, vs LHB -0.61, vs RHB -0.08).",
        "rows": [
            row("Zach Neto", "R", "+471", 79, "🌕 💣", ["vs Lambert"], """2 HR, 2 near-HR, 88.7 mph EV. Lambert RHB split +0.46, HR risk -0.57. pitcher suppresses HR (-0.57).""", blast="high"),
            row("Mike Trout", "R", "+357", 75, "💎", ["vs Lambert"], """0 HR, 1 near-HR, 97.3 mph EV. Lambert RHB split +0.46, HR risk -0.57. pitcher suppresses HR (-0.57); limited recent HR events.""", blast="good"),
            row("Jo Adell", "R", "+406", 79, "🌕 💣", ["vs Lambert"], """2 HR, 2 near-HR, 89.3 mph EV. Lambert RHB split +0.46, HR risk -0.57. pitcher suppresses HR (-0.57).""", blast="high"),
            row("Cam Smith", "R", "+710", 71, "💎", ["vs Detmers"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 89.4 mph EV. Detmers RHB split -0.08, HR risk -0.38. slight split headwind (-0.08); pitcher risk below avg (-0.38).""", blast="good"),
            row("Yordan Alvarez", "L", "+290", 82, "🚀 ⭐ 💎", ["vs Detmers"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 108.5 mph EV. Detmers LHB split -0.61, HR risk -0.38. tough split lane (-0.61); pitcher risk below avg (-0.38).""", blast="good"),
            row("Jeremy Pena", "R", "+491", 76, "💎", ["vs Detmers"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.3 mph EV. Detmers RHB split -0.08, HR risk -0.38. slight split headwind (-0.08); pitcher risk below avg (-0.38).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ PIT - Shohei Ohtani (R, LAD) vs Jared Jones (R, PIT)",
        "description": "Tail key data: Park boost -8% (stadium -15%, weather +6%). Ohtani (HR risk -1.05, vs LHB -0.80, vs RHB -0.68). Jones (HR risk 0.78, vs LHB +2.54, vs RHB -1.24).",
        "rows": [
            row("Brandon Lowe", "L", "+470", 76, "💎", ["vs Ohtani"], """1 HR, 2 near-HR, 91.5 mph EV. Ohtani LHB split -0.80, HR risk -1.05. tough split lane (-0.80); pitcher suppresses HR (-1.05).""", blast="good"),
            row("Oneil Cruz", "L", "+520", 72, "💎", ["vs Ohtani"], """1 HR, 1 near-HR, 89.7 mph EV. Ohtani LHB split -0.80, HR risk -1.05. tough split lane (-0.80); pitcher suppresses HR (-1.05).""", blast="good"),
            row("Bryan Reynolds", "S", "+900", 67, "💎", ["vs Ohtani"], """0 HR, 1 near-HR, 90.6 mph EV. Ohtani RHB split -0.68, HR risk -1.05. tough split lane (-0.68); pitcher suppresses HR (-1.05)."""),
            row("Marcell Ozuna", "R", "N/A", 76, "💎", ["vs Ohtani"], """1 HR, 1 near-HR, 93.8 mph EV. Ohtani RHB split -0.68, HR risk -1.05. tough split lane (-0.68); pitcher suppresses HR (-1.05).""", blast="good"),
            row("Henry Davis", "R", "N/A", 70, "💎", ["vs Ohtani"], """1 HR, 1 near-HR, 86.1 mph EV. Ohtani RHB split -0.68, HR risk -1.05. tough split lane (-0.68); pitcher suppresses HR (-1.05).""", blast="good"),
            row("Ryan O'Hearn", "L", "+840", 89, "🌕 💣", ["vs Ohtani"], """3 HR, 3 near-HR, 93.2 mph EV. Ohtani LHB split -0.80, HR risk -1.05. tough split lane (-0.80); pitcher suppresses HR (-1.05).""", blast="high"),
            row("Freddie Freeman", "L", "+505", 84, "⭐ 🌕 💣", ["vs Jones"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 88.3 mph EV. Jones LHB split +2.54, HR risk 0.78. park/weather net drag (-8%).""", blast="high"),
            row("Dalton Rushing", "L", "+525", 75, "💎", ["vs Jones"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 89.4 mph EV. Jones LHB split +2.54, HR risk 0.78. park/weather net drag (-8%).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ ATH - Brandon Sproat (R, MIL) vs Jack Perkins (R, ATH)",
        "description": "Tail key data: Park boost +80% (stadium +66%, weather +14%). Sproat (HR risk 0.24, vs LHB -0.50, vs RHB +0.91). Perkins (HR risk -0.57, vs LHB -0.85, vs RHB +0.02).",
        "rows": [
            row("Nick Kurtz", "L", "+198", 87, "⭐ 🌕 💣", ["vs Sproat"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.7 mph EV. Sproat LHB split -0.50, HR risk 0.24. tough split lane (-0.50).""", blast="high"),
            row("Brent Rooker", "R", "+235", 80, "⭐ 🌕 💣", ["vs Sproat"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 89.6 mph EV. Sproat RHB split +0.91, HR risk 0.24.""", blast="high"),
            row("Zack Gelof", "R", "+366", 72, "💎", ["vs Sproat"], """1 HR, 2 near-HR, 77.7 mph EV. Sproat RHB split +0.91, HR risk 0.24. lighter EV form (77.7 mph).""", blast="good"),
            row("Jake Bauers", "L", "+328", 80, "⭐ 💎", ["vs Perkins"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.1 mph EV. Perkins LHB split -0.85, HR risk -0.57. tough split lane (-0.85); pitcher suppresses HR (-0.57).""", blast="good"),
            row("Jackson Chourio", "R", "+320", 92, "🌕 💣", ["vs Perkins"], """3 HR, 4 near-HR, 93.6 mph EV. Perkins RHB split +0.02, HR risk -0.57. pitcher suppresses HR (-0.57).""", blast="high"),
            row("Garrett Mitchell", "L", "+440", 79, "💎", ["vs Perkins"], """Worst Pickz Hidden Gem. 0 HR, 3 near-HR, 97.0 mph EV. Perkins LHB split -0.85, HR risk -0.57. tough split lane (-0.85); pitcher suppresses HR (-0.57).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ DET - Mike Paredes (R, MIN) vs Framber Valdez (L, DET)",
        "description": "Tail key data: Park boost +10% (stadium -10%, weather +19%). Away starter risk unavailable. Valdez (HR risk -0.58, vs LHB -0.29, vs RHB -0.47).",
        "rows": [
            row("Dillon Dingler", "R", "+473", 98, "⭐ 🌕 💣", ["vs Paredes"], """Worst Pickz Favorite. 4 HR, 6 near-HR, 96.4 mph EV. Paredes split/risk data unavailable. limited split/risk sample; park suppresses carry (-10%).""", blast="high"),
            row("Kerry Carpenter", "L", "+390", 78, "🌕 💣", ["vs Paredes"], """2 HR, 2 near-HR, 87.2 mph EV. Paredes split/risk data unavailable. limited split/risk sample; park suppresses carry (-10%).""", blast="high"),
            row("Riley Greene", "L", "+410", 92, "⭐ 🌕 💣", ["vs Paredes"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 97.7 mph EV. Paredes split/risk data unavailable. limited split/risk sample; park suppresses carry (-10%).""", blast="high"),
            row("Colt Keith", "L", "+980", 71, "💎", ["vs Paredes"], """0 HR, 2 near-HR, 91.1 mph EV. Paredes split/risk data unavailable. limited split/risk sample; park suppresses carry (-10%).""", blast="good"),
            row("Byron Buxton", "R", "+270", 66, "💎", ["vs Valdez"], """0 HR, 1 near-HR, 90.3 mph EV. Valdez RHB split -0.47, HR risk -0.58. tough split lane (-0.47); pitcher suppresses HR (-0.58)."""),
            row("Alex Jackson", "R", "+500", 74, "💎", ["vs Valdez"], """Worst Pickz Hidden Gem. 0 HR, 98.0 mph EV. Valdez RHB split -0.47, HR risk -0.58. tough split lane (-0.47); pitcher suppresses HR (-0.58).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ CLE - Carlos Rodon (L, NYY) vs Parker Messick (L, CLE)",
        "description": "Tail key data: Park boost +18% (stadium -5%, weather +22%). Rodon (HR risk -0.88, vs LHB +0.22, vs RHB -1.08). Messick (HR risk -0.33, vs LHB -0.22, vs RHB -0.24).",
        "rows": [
            row("Rhys Hoskins", "R", "+500", 79, "⭐ 💎", ["vs Rodon"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.0 mph EV. Rodon RHB split -1.08, HR risk -0.88. tough split lane (-1.08); pitcher suppresses HR (-0.88).""", blast="good"),
            row("Jose Ramirez", "S", "+420", 75, "💎", ["vs Rodon"], """0 HR, 99.2 mph EV. Rodon RHB split -1.08, HR risk -0.88. tough split lane (-1.08); pitcher suppresses HR (-0.88).""", blast="good"),
            row("Brayan Rocchio", "S", "+980", 65, "💎", ["vs Rodon"], """0 HR, 90.9 mph EV. Rodon RHB split -1.08, HR risk -0.88. tough split lane (-1.08); pitcher suppresses HR (-0.88)."""),
            row("Jazz Chisholm Jr.", "L", "+650", 88, "⭐ 🌕 💣", ["vs Messick"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.8 mph EV. Messick LHB split -0.22, HR risk -0.33. slight split headwind (-0.22); pitcher risk below avg (-0.33).""", blast="high"),
            row("Trent Grisham", "L", "+511", 65, "💎", ["vs Messick"], """0 HR, 90.7 mph EV. Messick LHB split -0.22, HR risk -0.33. slight split headwind (-0.22); pitcher risk below avg (-0.33)."""),
            row("Ben Rice", "L", "+381", 72, "💎", ["vs Messick"], """0 HR, 1 near-HR, 94.0 mph EV. Messick LHB split -0.22, HR risk -0.33. slight split headwind (-0.22); pitcher risk below avg (-0.33).""", blast="good"),
            row("Paul Goldschmidt", "R", "+540", 78, "🌕 💣", ["vs Messick"], """2 HR, 2 near-HR, 88.5 mph EV. Messick RHB split -0.24, HR risk -0.33. slight split headwind (-0.24); pitcher risk below avg (-0.33).""", blast="high"),
        ],
    },
    {
        "title": "PHI @ TOR - Jesus Luzardo (L, PHI) vs Max Scherzer 🧤 (R, TOR)",
        "description": "Tail key data: Park boost +18% (stadium +7%, weather +12%). Luzardo (HR risk -0.53, vs LHB -0.79, vs RHB -0.20). Scherzer 🧤 (HR risk 1.65, vs LHB +1.17, vs RHB +1.25).",
        "rows": [
            row("Kazuma Okamoto", "R", "+490", 80, "🌕 💣", ["vs Luzardo"], """2 HR, 2 near-HR, 90.5 mph EV. Luzardo RHB split -0.20, HR risk -0.53. slight split headwind (-0.20); pitcher suppresses HR (-0.53).""", blast="high"),
            row("Yohendrick Pinango", "L", "+1000", 76, "💎", ["vs Luzardo"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 98.2 mph EV. Luzardo LHB split -0.79, HR risk -0.53. tough split lane (-0.79); pitcher suppresses HR (-0.53).""", blast="good"),
            row("Brandon Marsh", "L", "+590", 87, "⭐ 🌕 💣", ["vs Scherzer"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.1 mph EV. Scherzer LHB split +1.17, HR risk 1.65.""", blast="high"),
            row("J.T. Realmuto", "R", "+690", 70, "💎", ["vs Scherzer"], """1 HR, 1 near-HR, 86.6 mph EV. Scherzer RHB split +1.25, HR risk 1.65. lighter EV form (86.6 mph).""", blast="good"),
            row("Kyle Schwarber", "L", "+191", 81, "💎", ["vs Scherzer"], """1 HR, 1 near-HR, 99.1 mph EV. Scherzer LHB split +1.17, HR risk 1.65.""", blast="good"),
            row("Edmundo Sosa", "R", "N/A", 73, "💎", ["vs Scherzer"], """0 HR, 1 near-HR, 95.4 mph EV. Scherzer RHB split +1.25, HR risk 1.65. limited recent HR events.""", blast="good"),
            row("Bryce Harper", "L", "+402", 64, "💎", ["vs Scherzer"], """0 HR, 1 near-HR, 87.7 mph EV. Scherzer LHB split +1.17, HR risk 1.65. limited recent HR events; lighter EV form (87.7 mph)."""),
        ],
    },
    {
        "title": "SEA @ BAL - George Kirby (R, SEA) vs Brandon Young (R, BAL)",
        "description": "Tail key data: Park boost +13% (stadium -1%, weather +14%). Kirby (HR risk -0.36, vs LHB +0.00, vs RHB -0.69). Young (HR risk -0.03, vs LHB +0.03, vs RHB -0.00).",
        "rows": [
            row("Adley Rutschman", "S", "N/A", 77, "⭐ 💎", ["vs Kirby"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.4 mph EV. Kirby RHB split -0.69, HR risk -0.36. tough split lane (-0.69); pitcher risk below avg (-0.36).""", blast="good"),
            row("Samuel Basallo", "L", "+470", 78, "🚀 ⭐ 💎", ["vs Kirby"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 101.0 mph EV. Kirby LHB split +0.00, HR risk -0.36. pitcher risk below avg (-0.36); limited recent HR events.""", blast="good"),
            row("Colton Cowser", "L", "+504", 70, "💎", ["vs Kirby"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 89.6 mph EV. Kirby LHB split +0.00, HR risk -0.36. pitcher risk below avg (-0.36).""", blast="good"),
            row("Jackson Holliday", "L", "+730", 65, "💎", ["vs Kirby"], """0 HR, 1 near-HR, 88.7 mph EV. Kirby LHB split +0.00, HR risk -0.36. pitcher risk below avg (-0.36); limited recent HR events."""),
            row("Dominic Canzone", "L", "+360", 90, "🚀 ⭐ 🌕 💣", ["vs Young"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 101.4 mph EV. Young LHB split +0.03, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="high"),
            row("Luke Raley", "L", "+350", 74, "💎", ["vs Young"], """1 HR, 2 near-HR, 89.5 mph EV. Young LHB split +0.03, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="good"),
            row("Randy Arozarena", "R", "+620", 79, "💎", ["vs Young"], """1 HR, 3 near-HR, 92.9 mph EV. Young RHB split -0.00, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="good"),
            row("Patrick Wisdom", "R", "+414", 69, "💎", ["vs Young"], """0 HR, 92.9 mph EV. Young RHB split -0.00, HR risk -0.03. pitcher risk below avg (-0.03); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "STL @ NYM - Andre Pallante (R, STL) vs David Peterson (L, NYM)",
        "description": "Tail key data: Park boost +17% (stadium -1%, weather +18%). Pallante (HR risk -0.46, vs LHB +0.00, vs RHB -0.77). Home starter risk unavailable.",
        "rows": [
            row("Marcus Semien", "R", "+730", 95, "🌕 💣", ["vs Pallante"], """4 HR, 4 near-HR, 92.9 mph EV. Pallante RHB split -0.77, HR risk -0.46. tough split lane (-0.77); pitcher suppresses HR (-0.46).""", blast="high"),
            row("MJ Melendez", "L", "+620", 77, "💎", ["vs Pallante"], """1 HR, 1 near-HR, 94.9 mph EV. Pallante LHB split +0.00, HR risk -0.46. pitcher suppresses HR (-0.46).""", blast="good"),
            row("Jared Young", "L", "+900", 86, "🌕 💣", ["vs Pallante"], """2 HR, 2 near-HR, 95.6 mph EV. Pallante LHB split +0.00, HR risk -0.46. pitcher suppresses HR (-0.46).""", blast="high"),
            row("Alec Burleson", "L", "+575", 86, "🌕 💣", ["vs Peterson"], """2 HR, 2 near-HR, 95.5 mph EV. Peterson split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Jordan Walker", "R", "+478", 74, "💎", ["vs Peterson"], """0 HR, 98.0 mph EV. Peterson split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("JJ Wetherholt", "L", "+490", 74, "💎", ["vs Peterson"], """0 HR, 2 near-HR, 94.5 mph EV. Peterson split/risk data unavailable. limited split/risk sample.""", blast="good"),
        ],
    },
    {
        "title": "TEX @ KC - MacKenzie Gore (L, TEX) vs Seth Lugo (R, KC)",
        "description": "Tail key data: Park boost +39% (stadium +12%, weather +28%). Gore (HR risk -0.54, vs LHB -0.24, vs RHB -0.42). Lugo (HR risk 0.57, vs LHB +0.23, vs RHB +0.91).",
        "rows": [
            row("Jac Caglianone", "L", "+520", 70, "💎", ["vs Gore"], """1 HR, 1 near-HR, 79.3 mph EV. Gore LHB split -0.24, HR risk -0.54. slight split headwind (-0.24); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Bobby Witt Jr.", "R", "+375", 75, "⭐ 💎", ["vs Gore"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 95.3 mph EV. Gore RHB split -0.42, HR risk -0.54. tough split lane (-0.42); pitcher suppresses HR (-0.54).""", blast="good"),
            row("Starling Marte", "R", "+800", 64, "💎", ["vs Gore"], """0 HR, 1 near-HR, 86.8 mph EV. Gore RHB split -0.42, HR risk -0.54. tough split lane (-0.42); pitcher suppresses HR (-0.54)."""),
            row("Joc Pederson", "L", "+417", 75, "💎", ["vs Lugo"], """1 HR, 2 near-HR, 90.8 mph EV. Lugo LHB split +0.23, HR risk 0.57.""", blast="good"),
            row("Brandon Nimmo", "L", "+470", 85, "🌕 💣", ["vs Lugo"], """1 HR, 4 near-HR, 95.2 mph EV. Lugo LHB split +0.23, HR risk 0.57.""", blast="high"),
        ],
    },
    {
        "title": "WSH @ SF - Foster Griffin 🧤 (L, WSH) vs Robbie Ray (L, SF)",
        "description": "Tail key data: Park boost data unavailable. Griffin 🧤 (HR risk 1.01, vs LHB +0.05, vs RHB +1.20). Ray (HR risk 0.50, vs LHB -0.55, vs RHB +0.80).",
        "rows": [
            row("Willy Adames", "R", "+516", 70, "💎", ["vs Griffin"], """1 HR, 1 near-HR, 86.1 mph EV. Griffin RHB split +1.20, HR risk 1.01. lighter EV form (86.1 mph).""", blast="good"),
            row("Rafael Devers", "L", "+556", 79, "⭐ 💎", ["vs Griffin"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.7 mph EV. Griffin LHB split +0.05, HR risk 1.01.""", blast="good"),
            row("Dylan Crews", "R", "+690", 73, "💎", ["vs Ray"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.6 mph EV. Ray RHB split +0.80, HR risk 0.50.""", blast="good"),
            row("James Wood", "L", "+459", 72, "💎", ["vs Ray"], """0 HR, 96.0 mph EV. Ray LHB split -0.55, HR risk 0.50. tough split lane (-0.55); limited recent HR events.""", blast="good"),
            row("Luis Garcia Jr.", "L", "+426", 70, "💎", ["vs Ray"], """1 HR, 1 near-HR, 86.9 mph EV. Ray LHB split -0.55, HR risk 0.50. tough split lane (-0.55); lighter EV form (86.9 mph).""", blast="good"),
            row("CJ Abrams", "L", "+780", 79, "💎", ["vs Ray"], """1 HR, 1 near-HR, 97.3 mph EV. Ray LHB split -0.55, HR risk 0.50. tough split lane (-0.55).""", blast="good"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-10")

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

    out = ROOT / '_games-0610.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
