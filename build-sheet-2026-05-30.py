#!/usr/bin/env python3
"""Generate games[] block for 2026-05-30 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Randal Grichuk (R)",
    "Dillon Dingler (R)",
    "James Wood (L)",
    "Brandon Nimmo (L)",
    "Jac Caglianone (L)",
    "Brandon Lowe (L)",
    "Jesus Sanchez (L)",
    "Yordan Alvarez (L)",
    "Garrett Mitchell (L)",
    "Jackson Chourio (R)",
    "Jordan Walker (R)",
    "Alec Burleson (L)",
    "Ian Happ (S)",
    "Willy Adames (R)",
    "Luke Raley (L)",
    "Ketel Marte (S)",
    "Kyle Schwarber (L)",
    "Trea Turner (R)",
    "Bryce Harper (L)",
}

PLAYER_TEAMS = {
    "Aaron Judge (R)": "NYY",
    "Alec Burleson (L)": "STL",
    "Andy Pages (R)": "LAD",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Blaze Alexander (R)": "TOR",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Brett Baty (L)": "NYM",
    "Bryan Reynolds (S)": "PIT",
    "Bryan Torres (L)": "STL",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Christian Yelich (L)": "MIL",
    "Colby Thomas (R)": "ATH",
    "Corbin Carroll (L)": "ARI",
    "Dillon Dingler (R)": "DET",
    "Elly De La Cruz (S)": "CIN",
    "Eric Haase (R)": "SF",
    "Eugenio Suarez (R)": "CIN",
    "Fernando Tatis (R)": "SD",
    "Freddie Freeman (L)": "LAD",
    "Garrett Mitchell (L)": "MIL",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Isaac Paredes (R)": "HOU",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Holliday (L)": "BAL",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Jesus Sanchez (L)": "TOR",
    "Jorbit Vivas (L)": "WSH",
    "Jordan Walker (R)": "STL",
    "Juan Soto (L)": "NYM",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Ketel Marte (S)": "ARI",
    "Kyle Higashioka (R)": "TEX",
    "Kyle Schwarber (L)": "PHI",
    "Luke Raley (L)": "SEA",
    "MJ Melendez (L)": "MIA",
    "Manny Machado (R)": "SD",
    "Marcell Ozuna (R)": "PIT",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Michael Busch (L)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Mike Yastrzemski (L)": "ATL",
    "Oneil Cruz (L)": "PIT",
    "Owen Caissie (L)": "MIA",
    "Patrick Bailey (S)": "CLE",
    "Pete Alonso (R)": "BAL",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "DET",
    "Ryan McMahon (L)": "NYY",
    "Salvador Perez (R)": "KC",
    "Samuel Basallo (L)": "BAL",
    "Seiya Suzuki (R)": "CHC",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Horwitz (L)": "PIT",
    "Spencer Torkelson (R)": "DET",
    "Tj Rumfield (L)": "COL",
    "Travis Bazzana (L)": "CLE",
    "Trea Turner (R)": "PHI",
    "Vaughn Grissom (R)": "LAA",
    "Will Smith (R)": "LAD",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Xavier Edwards (S)": "MIA",
    "Yandy Diaz (R)": "TB",
    "Yohendrick Pinango (L)": "TOR",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

def display(name, hand):
    return f"{name} ({hand})"


def odds_text(odds):
    return "Listed prop - Over 0.5 HR" if odds == "N/A" else f"Listed {odds} - Over 0.5 HR"


def row(name, hand, odds, score, emojis, chips, note, blast=None):
    item = {
        "name": display(name, hand),
        "odds": odds_text(odds),
        "score": score,
        "emojis": emojis,
        "note": note,
        "chips": chips,
    }
    if blast:
        item["blast"] = blast
    return item
BUM_PITCHERS = {
    "Feltner",
    "Singer",
}
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
        "title": "ARI @ SEA - Ryne Nelson (R, ARI) vs Bryan Woo (R, SEA)",
        "description": "T-Mobile Park — HR environment -24% (stadium +1%, weather -25%). Ryne Nelson: 0.66 HR risk (vs LHB +0.15, vs RHB +1.19; strongest RHB lane +1.19). Bryan Woo: -0.24 HR risk (vs LHB +0.28, vs RHB -0.90; strongest LHB lane +0.28).",
        "rows": [
            row("Ketel Marte", "S", "+410", 80, "⭐ 💎", ["vs Woo"], """Worst Pickz favorite with 2 HR, 2 near-HR, 84.9 mph EV and 13.3% barrels. Draws opposing starter Woo; T-Mobile Park.""", blast="good"),
            row("Corbin Carroll", "L", "+490", 85, "💎", ["vs Woo"], """1 HR, 1 near-HR, 97.9 mph EV and 16.7% barrels. Draws opposing starter Woo; T-Mobile Park.""", blast="good"),
            row("Julio Rodriguez", "R", "+430", 74, "💎", ["vs Nelson"], """1 HR, 1 near-HR, 82.2 mph EV and 10.5% barrels. Draws opposing starter Nelson; T-Mobile Park.""", blast="good"),
            row("Luke Raley", "L", "+440", 68, "⭐", ["vs Nelson"], """Worst Pickz favorite with 1 HR, 1 near-HR, 86.1 mph EV. Draws opposing starter Nelson; T-Mobile Park."""),
        ],
    },
    {
        "title": "ATL @ CIN - Martin Perez (R, ATL) vs Brady Singer 🧤 (R, CIN)",
        "description": "Great American BP — HR environment +14% (stadium +12%, weather +2%). Martin Perez: 0.11 HR risk (vs LHB -0.25, vs RHB +0.38; strongest RHB lane +0.38). Brady Singer: 2.44 HR risk (vs LHB +2.61, vs RHB +0.54; strongest LHB lane +2.61).",
        "rows": [
            row("Matt Olson", "L", "+327", 71, "💎", ["vs Singer"], """0 HR, 94.8 mph EV. Draws opposing starter Singer; Great American BP.""", blast="good"),
            row("Austin Riley", "R", "+449", 83, "🌕 💣", ["vs Singer"], """1 HR, 1 near-HR, 94.1 mph EV and 14.3% barrels. Draws opposing starter Singer; Great American BP.""", blast="high"),
            row("Mike Yastrzemski", "L", "+490", 80, "💎", ["vs Singer"], """1 HR, 1 near-HR, 95.2 mph EV and 8.3% barrels. Draws opposing starter Singer; Great American BP.""", blast="good"),
            row("Eugenio Suarez", "R", "+440", 83, "💎", ["vs Perez"], """1 HR, 1 near-HR, 99.1 mph EV and 6.7% barrels. Draws opposing starter Perez; Great American BP.""", blast="good"),
            row("Elly De La Cruz", "S", "+496", 83, "🚀 💎", ["vs Perez"], """0 HR, 100.6 mph EV and 20.0% barrels. Draws opposing starter Perez; Great American BP.""", blast="good"),
        ],
    },
    {
        "title": "BOS @ CLE - Sonny Gray (R, BOS) vs Parker Messick (R, CLE)",
        "description": "Progressive Field — HR environment -30% (stadium -5%, weather -25%). Sonny Gray: -0.50 HR risk (vs LHB -0.07, vs RHB -0.82; strongest LHB lane -0.07). Parker Messick: 0.01 HR risk (vs LHB -0.27, vs RHB +0.16; strongest RHB lane +0.16).",
        "rows": [
            row("Willson Contreras", "R", "+504", 80, "💎", ["vs Messick"], """1 HR, 2 near-HR, 93.5 mph EV and 8.7% barrels. Draws opposing starter Messick; Progressive Field.""", blast="good"),
            row("Wilyer Abreu", "L", "+580", 70, "💎", ["vs Messick"], """0 HR, 84.7 mph EV and 18.9% barrels. Draws opposing starter Messick; Progressive Field.""", blast="good"),
            row("Patrick Bailey", "S", "+1140", 76, "💎", ["vs Gray"], """1 HR, 3 near-HR, 89.0 mph EV and 10.0% barrels. Draws opposing starter Gray; Progressive Field."""),
            row("Travis Bazzana", "L", "+910", 83, "💎", ["vs Gray"], """2 HR, 3 near-HR, 91.2 mph EV and 10.0% barrels. Draws opposing starter Gray; Progressive Field."""),
        ],
    },
    {
        "title": "CHC @ STL - Ben Brown (R, CHC) vs Kyle Leahy (R, STL)",
        "description": "Busch Stadium — HR environment -13% (stadium -10%, weather -3%). Ben Brown: -0.77 HR risk (vs LHB -0.52, vs RHB -0.58; strongest LHB lane -0.52). Kyle Leahy: 0.65 HR risk (vs LHB +1.15, vs RHB -0.55; strongest LHB lane +1.15).",
        "rows": [
            row("Ian Happ", "S", "+570", 82, "⭐ 💎", ["vs Leahy"], """Worst Pickz favorite with 2 HR, 2 near-HR, 89.4 mph EV and 14.3% barrels. Draws opposing starter Leahy; Busch Stadium.""", blast="good"),
            row("Michael Busch", "L", "+570", 84, "💎", ["vs Leahy"], """1 HR, 1 near-HR, 93.6 mph EV and 25.0% barrels. Draws opposing starter Leahy; Busch Stadium.""", blast="good"),
            row("Seiya Suzuki", "R", "+540", 77, "💎", ["vs Leahy"], """0 HR, 1 near-HR, 90.6 mph EV and 26.1% barrels. Draws opposing starter Leahy; Busch Stadium.""", blast="good"),
            row("Jordan Walker", "R", "+420", 94, "⭐ 🌕 💣", ["vs Brown"], """Worst Pickz favorite with 2 HR, 2 near-HR, 95.3 mph EV and 25.0% barrels. Draws opposing starter Brown; Busch Stadium.""", blast="high"),
            row("Alec Burleson", "L", "+570", 80, "⭐ 💎", ["vs Brown"], """Worst Pickz favorite with 1 HR, 3 near-HR, 93.6 mph EV. Draws opposing starter Brown; Busch Stadium.""", blast="good"),
            row("Bryan Torres", "L", "+980", 68, "💎", ["vs Brown"], """1 HR, 1 near-HR, 86.8 mph EV. Draws opposing starter Brown; Busch Stadium."""),
        ],
    },
    {
        "title": "DET @ CWS - Framber Valdez (R, DET) vs Anthony Kay (R, CWS)",
        "description": "Rate Field — HR environment -7% (stadium +2%, weather -9%). Framber Valdez: 0.07 HR risk (vs LHB +0.47, vs RHB -0.15; strongest LHB lane +0.47). Anthony Kay: -0.06 HR risk (vs LHB -1.31, vs RHB +0.53; strongest RHB lane +0.53).",
        "rows": [
            row("Dillon Dingler", "R", "+480", 88, "⭐ 🌕 💣", ["vs Kay"], """Worst Pickz favorite with 1 HR, 2 near-HR, 98.1 mph EV and 17.6% barrels. Draws opposing starter Kay; Rate Field.""", blast="good"),
            row("Spencer Torkelson", "R", "+500", 74, "💎", ["vs Kay"], """1 HR, 2 near-HR, 81.9 mph EV and 12.5% barrels. Draws opposing starter Kay; Rate Field."""),
            row("Randal Grichuk", "R", "N/A", 73, "⭐ 💎", ["vs Kay"], """Worst Pickz favorite with 1 HR, 1 near-HR, 93.2 mph EV. Draws opposing starter Kay; Rate Field."""),
            row("Miguel Vargas", "R", "+470", 88, "🌕 💣", ["vs Valdez"], """2 HR, 2 near-HR, 96.5 mph EV and 9.1% barrels. Draws opposing starter Valdez; Rate Field.""", blast="good"),
        ],
    },
    {
        "title": "KC @ TEX - Seth Lugo (R, KC) vs Kumar Rocker (R, TEX)",
        "description": "Globe Life Field — HR environment -10% (stadium -9%, weather -1%). Seth Lugo: 0.12 HR risk (vs LHB -0.11, vs RHB +0.98; strongest RHB lane +0.98). Kumar Rocker: -0.06 HR risk (vs LHB +0.03, vs RHB +0.03; strongest RHB lane +0.03).",
        "rows": [
            row("Salvador Perez", "R", "+235", 78, "💎", ["vs Rocker"], """1 HR, 1 near-HR, 92.5 mph EV and 11.1% barrels. Draws opposing starter Rocker; Globe Life Field.""", blast="good"),
            row("Jac Caglianone", "L", "+243", 92, "🚀 ⭐ 🌕 💣", ["vs Rocker"], """Worst Pickz favorite with 1 HR, 1 near-HR, 102.9 mph EV and 29.9% barrels. Draws opposing starter Rocker; Globe Life Field.""", blast="good"),
            row("Brandon Nimmo", "L", "+431", 91, "⭐ 🌕 💣", ["vs Lugo"], """Worst Pickz favorite with 2 HR, 4 near-HR, 92.3 mph EV and 20.0% barrels. Draws opposing starter Lugo; Globe Life Field.""", blast="good"),
            row("Kyle Higashioka", "R", "N/A", 76, "💎", ["vs Lugo"], """2 HR, 2 near-HR, 85.5 mph EV and 5.9% barrels. Draws opposing starter Lugo; Globe Life Field."""),
        ],
    },
    {
        "title": "LAA @ TB - Reid Detmers (R, LAA) vs Drew Rasmussen (R, TB)",
        "description": "Tropicana Field — HR environment -3% (stadium -4%, weather +1%). Reid Detmers: -0.47 HR risk (vs LHB -0.82, vs RHB -0.20; strongest RHB lane -0.20). Drew Rasmussen: -0.35 HR risk (vs LHB -0.28, vs RHB -0.08; strongest RHB lane -0.08).",
        "rows": [
            row("Zach Neto", "R", "+450", 93, "🌕 💣", ["vs Rasmussen"], """2 HR, 3 near-HR, 92.1 mph EV and 27.8% barrels. Draws opposing starter Rasmussen; Tropicana Field.""", blast="high"),
            row("Mike Trout", "R", "+363", 77, "💎", ["vs Rasmussen"], """1 HR, 2 near-HR, 88.6 mph EV and 12.5% barrels. Draws opposing starter Rasmussen; Tropicana Field.""", blast="good"),
            row("Vaughn Grissom", "R", "+680", 79, "💎", ["vs Rasmussen"], """1 HR, 1 near-HR, 94.5 mph EV and 13.6% barrels. Draws opposing starter Rasmussen; Tropicana Field."""),
            row("Junior Caminero", "R", "+184", 86, "🌕 💣", ["vs Detmers"], """1 HR, 1 near-HR, 94.1 mph EV and 24.0% barrels. Draws opposing starter Detmers; Tropicana Field.""", blast="high"),
            row("Yandy Diaz", "R", "+219", 79, "💎", ["vs Detmers"], """0 HR, 2 near-HR, 89.9 mph EV and 26.7% barrels. Draws opposing starter Detmers; Tropicana Field.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ NYM - Tyler Phillips (R, MIA) vs Christian Scott (R, NYM)",
        "description": "Citi Field — HR environment -8% (stadium -2%, weather -7%). Tyler Phillips: -1.30 HR risk (vs LHB -0.83, vs RHB -0.90; strongest LHB lane -0.83). Christian Scott: -1.27 HR risk (vs LHB -1.32, vs RHB -0.05; strongest RHB lane -0.05).",
        "rows": [
            row("Xavier Edwards", "S", "+1200", 67, "💎", ["vs Scott"], """0 HR, 1 near-HR, 89.3 mph EV and 5.6% barrels. Draws opposing starter Scott; Citi Field."""),
            row("Owen Caissie", "L", "+680", 92, "🌕 💣", ["vs Scott"], """1 HR, 1 near-HR, 99.5 mph EV and 33.3% barrels. Draws opposing starter Scott; Citi Field.""", blast="good"),
            row("Juan Soto", "L", "+360", 87, "🌕 💣", ["vs Phillips"], """1 HR, 1 near-HR, 93.2 mph EV and 43.8% barrels. Draws opposing starter Phillips; Citi Field.""", blast="high"),
            row("Brett Baty", "L", "+820", 84, "💎", ["vs Phillips"], """1 HR, 1 near-HR, 96.8 mph EV and 14.3% barrels. Draws opposing starter Phillips; Citi Field.""", blast="good"),
            row("MJ Melendez", "L", "+550", 72, "💎", ["vs Scott"], """0 HR, 95.0 mph EV and 8.3% barrels. Draws opposing starter Scott; Citi Field."""),
        ],
    },
    {
        "title": "MIL @ HOU - Brandon Sproat (R, MIL) vs Peter Lambert (R, HOU)",
        "description": "Daikin Park — HR environment +6% (stadium +6%, weather 0%). Brandon Sproat: 0.41 HR risk (vs LHB +0.16, vs RHB +0.91; strongest RHB lane +0.91). Peter Lambert: -0.66 HR risk (vs LHB -0.81, vs RHB +0.30; strongest RHB lane +0.30).",
        "rows": [
            row("Christian Yelich", "L", "+590", 76, "💎", ["vs Lambert"], """1 HR, 1 near-HR, 90.5 mph EV and 10.0% barrels. Draws opposing starter Lambert; Daikin Park.""", blast="good"),
            row("Jake Bauers", "L", "+440", 80, "💎", ["vs Lambert"], """1 HR, 1 near-HR, 88.5 mph EV and 28.6% barrels. Draws opposing starter Lambert; Daikin Park.""", blast="good"),
            row("Garrett Mitchell", "L", "+790", 98, "⭐ 🌕 💣", ["vs Lambert"], """Worst Pickz favorite with 2 HR, 4 near-HR, 98.9 mph EV and 27.3% barrels. Draws opposing starter Lambert; Daikin Park.""", blast="good"),
            row("Jackson Chourio", "R", "+490", 86, "⭐ 💎", ["vs Lambert"], """Worst Pickz favorite with 0 HR, 2 near-HR, 96.2 mph EV and 35.7% barrels. Draws opposing starter Lambert; Daikin Park.""", blast="good"),
            row("Isaac Paredes", "R", "+500", 87, "💎", ["vs Sproat"], """2 HR, 3 near-HR, 91.2 mph EV and 16.7% barrels. Draws opposing starter Sproat; Daikin Park.""", blast="good"),
            row("Yordan Alvarez", "L", "+300", 87, "⭐ 🌕 💣", ["vs Sproat"], """Worst Pickz favorite with 2 HR, 3 near-HR, 95.3 mph EV. Draws opposing starter Sproat; Daikin Park.""", blast="high"),
        ],
    },
    {
        "title": "MIN @ PIT - Bailey Ober (R, MIN) vs Mitch Keller (R, PIT)",
        "description": "PNC Park — HR environment -25% (stadium -14%, weather -11%). Bailey Ober: 0.54 HR risk (vs LHB +0.84, vs RHB -0.30; strongest LHB lane +0.84). Mitch Keller: -0.36 HR risk (vs LHB +0.22, vs RHB -1.29; strongest LHB lane +0.22).",
        "rows": [
            row("Byron Buxton", "R", "+233", 95, "🌕 💣", ["vs Keller"], """3 HR, 3 near-HR, 91.5 mph EV and 22.2% barrels. Draws opposing starter Keller; PNC Park.""", blast="high"),
            row("Spencer Horwitz", "L", "+730", 82, "🌕 💣", ["vs Ober"], """1 HR, 1 near-HR, 84.4 mph EV and 30.8% barrels. Draws opposing starter Ober; PNC Park.""", blast="high"),
            row("Brandon Lowe", "L", "+340", 98, "⭐ 🌕 💣", ["vs Ober"], """Worst Pickz favorite with 2 HR, 4 near-HR, 95.6 mph EV and 30.8% barrels. Draws opposing starter Ober; PNC Park.""", blast="high"),
            row("Oneil Cruz", "L", "+375", 80, "💎", ["vs Ober"], """1 HR, 2 near-HR, 96.4 mph EV. Draws opposing starter Ober; PNC Park.""", blast="good"),
            row("Bryan Reynolds", "S", "+610", 74, "💎", ["vs Ober"], """1 HR, 1 near-HR, 84.6 mph EV and 11.1% barrels. Draws opposing starter Ober; PNC Park.""", blast="good"),
            row("Marcell Ozuna", "R", "+582", 80, "💎", ["vs Ober"], """1 HR, 1 near-HR, 91.6 mph EV and 18.2% barrels. Draws opposing starter Ober; PNC Park.""", blast="good"),
        ],
    },
    {
        "title": "NYY @ ATH - Ryan Weathers (R, NYY) vs J.T. Ginn (R, ATH)",
        "description": "Sutter Health Park — HR environment +31% (stadium +32%, weather -1%). Ryan Weathers: 0.27 HR risk (vs LHB -0.81, vs RHB +0.66; strongest RHB lane +0.66). J.T. Ginn: -0.46 HR risk (vs LHB -0.25, vs RHB -0.34; strongest LHB lane -0.25).",
        "rows": [
            row("Ben Rice", "L", "+340", 78, "💎", ["vs Ginn"], """2 HR, 2 near-HR, 90.0 mph EV. Draws opposing starter Ginn; Sutter Health Park.""", blast="good"),
            row("Aaron Judge", "R", "+220", 89, "🌕 💣", ["vs Ginn"], """1 HR, 2 near-HR, 97.7 mph EV and 15.4% barrels. Draws opposing starter Ginn; Sutter Health Park.""", blast="high"),
            row("Ryan McMahon", "L", "+540", 82, "💎", ["vs Ginn"], """2 HR, 2 near-HR, 88.0 mph EV and 18.2% barrels. Draws opposing starter Ginn; Sutter Health Park.""", blast="good"),
            row("Shea Langeliers", "R", "+280", 70, "💎", ["vs Weathers"], """0 HR, 91.4 mph EV and 12.5% barrels. Draws opposing starter Weathers; Sutter Health Park."""),
            row("Colby Thomas", "R", "+470", 69, "💎", ["vs Weathers"], """0 HR, 1 near-HR, 87.6 mph EV and 15.4% barrels. Draws opposing starter Weathers; Sutter Health Park."""),
        ],
    },
    {
        "title": "PHI @ LAD - Jesus Luzardo (R, PHI) vs Roki Sasaki (R, LAD)",
        "description": "Dodger Stadium — HR environment +10% (stadium +17%, weather -8%). Jesus Luzardo: -0.75 HR risk (vs LHB -0.55, vs RHB -0.62; strongest LHB lane -0.55). Roki Sasaki: 0.91 HR risk (vs LHB +0.73, vs RHB +0.91; strongest RHB lane +0.91).",
        "rows": [
            row("Kyle Schwarber", "L", "+290", 98, "🚀 ⭐ 🌕 💣", ["vs Sasaki"], """Worst Pickz favorite with 3 HR, 3 near-HR, 101.7 mph EV and 30.0% barrels. Draws opposing starter Sasaki; Dodger Stadium.""", blast="high"),
            row("Trea Turner", "R", "+380", 90, "⭐ 🌕 💣", ["vs Sasaki"], """Worst Pickz favorite with 2 HR, 3 near-HR, 92.5 mph EV and 22.2% barrels. Draws opposing starter Sasaki; Dodger Stadium.""", blast="good"),
            row("Bryce Harper", "L", "+500", 82, "⭐ 💎", ["vs Sasaki"], """Worst Pickz favorite with 1 HR, 1 near-HR, 93.0 mph EV and 22.2% barrels. Draws opposing starter Sasaki; Dodger Stadium.""", blast="good"),
            row("Freddie Freeman", "L", "+550", 82, "🌕 💣", ["vs Luzardo"], """0 HR, 94.4 mph EV and 33.3% barrels. Draws opposing starter Luzardo; Dodger Stadium.""", blast="high"),
            row("Shohei Ohtani", "L", "+310", 76, "🌕 💣", ["vs Luzardo"], """0 HR, 82.3 mph EV and 30.0% barrels. Draws opposing starter Luzardo; Dodger Stadium.""", blast="high"),
            row("Will Smith", "R", "+578", 86, "🌕 💣", ["vs Luzardo"], """0 HR, 97.7 mph EV and 33.3% barrels. Draws opposing starter Luzardo; Dodger Stadium.""", blast="high"),
            row("Max Muncy", "L", "+320", 78, "💎", ["vs Luzardo"], """0 HR, 91.6 mph EV and 50.0% barrels. Draws opposing starter Luzardo; Dodger Stadium.""", blast="good"),
            row("Andy Pages", "R", "+582", 71, "💎", ["vs Luzardo"], """1 HR, 1 near-HR, 87.7 mph EV and 7.7% barrels. Draws opposing starter Luzardo; Dodger Stadium."""),
        ],
    },
    {
        "title": "SD @ WSH - Michael King (R, SD) vs Foster Griffin (R, WSH)",
        "description": "Nationals Park — HR environment -22% (stadium +3%, weather -26%). Michael King: -0.37 HR risk (vs LHB +0.18, vs RHB -1.07; strongest LHB lane +0.18). Foster Griffin: 0.49 HR risk (vs LHB +0.20, vs RHB +0.69; strongest RHB lane +0.69).",
        "rows": [
            row("Fernando Tatis", "R", "+420", 76, "💎", ["vs Griffin"], """0 HR, 3 near-HR, 88.2 mph EV and 17.0% barrels. Draws opposing starter Griffin; Nationals Park.""", blast="good"),
            row("Manny Machado", "R", "+520", 80, "🌕 💣", ["vs Griffin"], """1 HR, 2 near-HR, 86.8 mph EV and 16.7% barrels. Draws opposing starter Griffin; Nationals Park.""", blast="high"),
            row("James Wood", "L", "+360", 82, "⭐ 💎", ["vs King"], """Worst Pickz favorite with 1 HR, 3 near-HR, 96.2 mph EV. Draws opposing starter King; Nationals Park.""", blast="good"),
            row("CJ Abrams", "L", "+590", 80, "💎", ["vs King"], """1 HR, 1 near-HR, 93.8 mph EV and 11.1% barrels. Draws opposing starter King; Nationals Park.""", blast="good"),
            row("Jorbit Vivas", "L", "+1300", 71, "💎", ["vs King"], """1 HR, 1 near-HR, 85.6 mph EV and 8.3% barrels. Draws opposing starter King; Nationals Park."""),
        ],
    },
    {
        "title": "SF @ COL - Adrian Houser (R, SF) vs Ryan Feltner 🧤 (R, COL)",
        "description": "Coors Field — HR environment +16% (stadium +21%, weather -5%). Adrian Houser: 0.27 HR risk (vs LHB +0.74, vs RHB -0.46; strongest LHB lane +0.74). Ryan Feltner: 1.64 HR risk (vs LHB +1.00, vs RHB +1.79; strongest RHB lane +1.79).",
        "rows": [
            row("Willy Adames", "R", "+540", 98, "⭐ 🌕 💣", ["vs Feltner"], """Worst Pickz favorite with 4 HR, 4 near-HR, 92.3 mph EV and 22.0% barrels. Draws opposing starter Feltner; Coors Field.""", blast="high"),
            row("Rafael Devers", "L", "+380", 97, "🌕 💣", ["vs Feltner"], """1 HR, 4 near-HR, 97.9 mph EV and 28.0% barrels. Draws opposing starter Feltner; Coors Field.""", blast="high"),
            row("Tj Rumfield", "L", "+880", 78, "💎", ["vs Houser"], """1 HR, 3 near-HR, 81.2 mph EV and 11.1% barrels. Draws opposing starter Houser; Coors Field.""", blast="good"),
            row("Hunter Goodman", "R", "+410", 68, "💎", ["vs Houser"], """0 HR, 87.4 mph EV and 11.1% barrels. Draws opposing starter Houser; Coors Field.""", blast="good"),
            row("Eric Haase", "R", "+950", 86, "💎", ["vs Feltner"], """2 HR, 3 near-HR, 89.5 mph EV and 25.0% barrels. Draws opposing starter Feltner; Coors Field."""),
        ],
    },
    {
        "title": "TOR @ BAL - Trey Yesavage (R, TOR) vs Brandon Young (R, BAL)",
        "description": "Oriole Park — HR environment -22% (stadium -1%, weather -21%). Trey Yesavage: -1.33 HR risk (vs LHB -0.74, vs RHB -1.42; strongest LHB lane -0.74). Brandon Young: 0.34 HR risk (vs LHB +0.18, vs RHB +0.65; strongest RHB lane +0.65).",
        "rows": [
            row("Pete Alonso", "R", "+410", 98, "🌕 💣", ["vs Yesavage"], """3 HR, 3 near-HR, 97.8 mph EV and 20.0% barrels. Draws opposing starter Yesavage; Oriole Park.""", blast="high"),
            row("Jackson Holliday", "L", "+850", 87, "💎", ["vs Yesavage"], """2 HR, 2 near-HR, 95.2 mph EV and 12.5% barrels. Draws opposing starter Yesavage; Oriole Park.""", blast="good"),
            row("Samuel Basallo", "L", "+470", 85, "💎", ["vs Yesavage"], """1 HR, 1 near-HR, 95.2 mph EV and 22.2% barrels. Draws opposing starter Yesavage; Oriole Park.""", blast="good"),
            row("Blaze Alexander", "R", "N/A", 87, "💎", ["vs Young"], """1 HR, 3 near-HR, 96.1 mph EV and 14.3% barrels. Draws opposing starter Young; Oriole Park.""", blast="good"),
            row("Yohendrick Pinango", "L", "N/A", 67, "💎", ["vs Young"], """0 HR, 88.1 mph EV and 14.3% barrels. Draws opposing starter Young; Oriole Park."""),
            row("Jesus Sanchez", "L", "+720", 86, "⭐ 💎", ["vs Young"], """Worst Pickz favorite with 1 HR, 2 near-HR, 96.0 mph EV and 17.9% barrels. Draws opposing starter Young; Oriole Park.""", blast="good"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

if __name__ == "__main__":
    def js_string(value):
        return json.dumps(value, ensure_ascii=False)

    def emit_games_js(games_data):
        lines = ["const games = ["]
        for game in games_data:
            lines.append("    {")
            lines.append(f"        title: {js_string(game['title'])},")
            lines.append(f"        description: {js_string(game['description'])},")
            lines.append("        rows: [")
            for entry in game['rows']:
                parts = [
                    f"name: {js_string(entry['name'])}",
                    f"odds: {js_string(entry['odds'])}",
                    f"score: {entry['score']}",
                    f"emojis: {js_string(entry['emojis'])}",
                    f"note: {js_string(entry['note'])}",
                    f"chips: {js_string(entry['chips'])}",
                ]
                if entry.get("blast"):
                    parts.append(f"blast: {js_string(entry['blast'])}")
                lines.append("            { " + ", ".join(parts) + " },")
            lines.append("        ],")
            lines.append("    },")
        lines.append("];")
        return "\n".join(lines)

    out = ROOT / "_games-0530.txt"
    out.write_text(emit_games_js(games) + "\n", encoding="utf-8")
    print("wrote", out.name)
