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
        "description": "ARI @ SEA — PropFinder CSV slate. Ryne Nelson vs Bryan Woo per imported matchup files.",
        "rows": [
            row("Ketel Marte", "S", "+410", 80, "⭐ 💎", ["vs Woo"], """Worst Pickz favorite with 2 HR, 2 near-HR, 84.9 mph EV and 13.3% barrels. Draws opposing starter Woo; ARI @ SEA.""", blast="good"),
            row("Corbin Carroll", "L", "+490", 85, "💎", ["vs Woo"], """1 HR, 1 near-HR, 97.9 mph EV and 16.7% barrels. Draws opposing starter Woo; ARI @ SEA.""", blast="good"),
            row("Julio Rodriguez", "R", "+430", 74, "💎", ["vs Nelson"], """1 HR, 1 near-HR, 82.2 mph EV and 10.5% barrels. Draws opposing starter Nelson; ARI @ SEA.""", blast="good"),
            row("Luke Raley", "L", "+440", 68, "⭐", ["vs Nelson"], """Worst Pickz favorite with 1 HR, 1 near-HR, 86.1 mph EV. Draws opposing starter Nelson; ARI @ SEA."""),
        ],
    },
    {
        "title": "ATL @ CIN - Martin Perez (R, ATL) vs Brady Singer 🧤 (R, CIN)",
        "description": "ATL @ CIN — PropFinder CSV slate. Attack lanes: Brady Singer (2.44 HR risk).",
        "rows": [
            row("Matt Olson", "L", "+327", 71, "💎", ["vs Singer"], """0 HR, 94.8 mph EV. Draws opposing starter Singer; ATL @ CIN.""", blast="good"),
            row("Austin Riley", "R", "+449", 83, "🌕 💣", ["vs Singer"], """1 HR, 1 near-HR, 94.1 mph EV and 14.3% barrels. Draws opposing starter Singer; ATL @ CIN.""", blast="high"),
            row("Mike Yastrzemski", "L", "+490", 80, "💎", ["vs Singer"], """1 HR, 1 near-HR, 95.2 mph EV and 8.3% barrels. Draws opposing starter Singer; ATL @ CIN.""", blast="good"),
            row("Eugenio Suarez", "R", "+440", 83, "💎", ["vs Perez"], """1 HR, 1 near-HR, 99.1 mph EV and 6.7% barrels. Draws opposing starter Perez; ATL @ CIN.""", blast="good"),
            row("Elly De La Cruz", "S", "+496", 83, "🚀 💎", ["vs Perez"], """0 HR, 100.6 mph EV and 20.0% barrels. Draws opposing starter Perez; ATL @ CIN.""", blast="good"),
        ],
    },
    {
        "title": "BOS @ CLE - Sonny Gray (R, BOS) vs Parker Messick (R, CLE)",
        "description": "BOS @ CLE — PropFinder CSV slate. Sonny Gray vs Parker Messick per imported matchup files.",
        "rows": [
            row("Willson Contreras", "R", "+504", 80, "💎", ["vs Messick"], """1 HR, 2 near-HR, 93.5 mph EV and 8.7% barrels. Draws opposing starter Messick; BOS @ CLE.""", blast="good"),
            row("Wilyer Abreu", "L", "+580", 70, "💎", ["vs Messick"], """0 HR, 84.7 mph EV and 18.9% barrels. Draws opposing starter Messick; BOS @ CLE.""", blast="good"),
            row("Patrick Bailey", "S", "+1140", 76, "💎", ["vs Gray"], """1 HR, 3 near-HR, 89.0 mph EV and 10.0% barrels. Draws opposing starter Gray; BOS @ CLE."""),
            row("Travis Bazzana", "L", "+910", 83, "💎", ["vs Gray"], """2 HR, 3 near-HR, 91.2 mph EV and 10.0% barrels. Draws opposing starter Gray; BOS @ CLE."""),
        ],
    },
    {
        "title": "CHC @ STL - Ben Brown (R, CHC) vs Kyle Leahy (R, STL)",
        "description": "CHC @ STL — PropFinder CSV slate. Ben Brown vs Kyle Leahy per imported matchup files.",
        "rows": [
            row("Ian Happ", "S", "+570", 82, "⭐ 💎", ["vs Leahy"], """Worst Pickz favorite with 2 HR, 2 near-HR, 89.4 mph EV and 14.3% barrels. Draws opposing starter Leahy; CHC @ STL.""", blast="good"),
            row("Michael Busch", "L", "+570", 84, "💎", ["vs Leahy"], """1 HR, 1 near-HR, 93.6 mph EV and 25.0% barrels. Draws opposing starter Leahy; CHC @ STL.""", blast="good"),
            row("Seiya Suzuki", "R", "+540", 77, "💎", ["vs Leahy"], """0 HR, 1 near-HR, 90.6 mph EV and 26.1% barrels. Draws opposing starter Leahy; CHC @ STL.""", blast="good"),
            row("Jordan Walker", "R", "+420", 94, "⭐ 🌕 💣", ["vs Brown"], """Worst Pickz favorite with 2 HR, 2 near-HR, 95.3 mph EV and 25.0% barrels. Draws opposing starter Brown; CHC @ STL.""", blast="high"),
            row("Alec Burleson", "L", "+570", 80, "⭐ 💎", ["vs Brown"], """Worst Pickz favorite with 1 HR, 3 near-HR, 93.6 mph EV. Draws opposing starter Brown; CHC @ STL.""", blast="good"),
            row("Bryan Torres", "L", "+980", 68, "💎", ["vs Brown"], """1 HR, 1 near-HR, 86.8 mph EV. Draws opposing starter Brown; CHC @ STL."""),
        ],
    },
    {
        "title": "DET @ CWS - Framber Valdez (R, DET) vs Anthony Kay (R, CWS)",
        "description": "DET @ CWS — PropFinder CSV slate. Framber Valdez vs Anthony Kay per imported matchup files.",
        "rows": [
            row("Dillon Dingler", "R", "+480", 88, "⭐ 🌕 💣", ["vs Kay"], """Worst Pickz favorite with 1 HR, 2 near-HR, 98.1 mph EV and 17.6% barrels. Draws opposing starter Kay; DET @ CWS.""", blast="good"),
            row("Spencer Torkelson", "R", "+500", 74, "💎", ["vs Kay"], """1 HR, 2 near-HR, 81.9 mph EV and 12.5% barrels. Draws opposing starter Kay; DET @ CWS."""),
            row("Randal Grichuk", "R", "N/A", 73, "⭐ 💎", ["vs Kay"], """Worst Pickz favorite with 1 HR, 1 near-HR, 93.2 mph EV. Draws opposing starter Kay; DET @ CWS."""),
            row("Miguel Vargas", "R", "+470", 88, "🌕 💣", ["vs Valdez"], """2 HR, 2 near-HR, 96.5 mph EV and 9.1% barrels. Draws opposing starter Valdez; DET @ CWS.""", blast="good"),
        ],
    },
    {
        "title": "KC @ TEX - Seth Lugo (R, KC) vs Kumar Rocker (R, TEX)",
        "description": "KC @ TEX — PropFinder CSV slate. Seth Lugo vs Kumar Rocker per imported matchup files.",
        "rows": [
            row("Salvador Perez", "R", "+235", 78, "💎", ["vs Rocker"], """1 HR, 1 near-HR, 92.5 mph EV and 11.1% barrels. Draws opposing starter Rocker; KC @ TEX.""", blast="good"),
            row("Jac Caglianone", "L", "+243", 92, "🚀 ⭐ 🌕 💣", ["vs Rocker"], """Worst Pickz favorite with 1 HR, 1 near-HR, 102.9 mph EV and 29.9% barrels. Draws opposing starter Rocker; KC @ TEX.""", blast="good"),
            row("Brandon Nimmo", "L", "+431", 91, "⭐ 🌕 💣", ["vs Lugo"], """Worst Pickz favorite with 2 HR, 4 near-HR, 92.3 mph EV and 20.0% barrels. Draws opposing starter Lugo; KC @ TEX.""", blast="good"),
            row("Kyle Higashioka", "R", "N/A", 76, "💎", ["vs Lugo"], """2 HR, 2 near-HR, 85.5 mph EV and 5.9% barrels. Draws opposing starter Lugo; KC @ TEX."""),
        ],
    },
    {
        "title": "LAA @ TB - Reid Detmers (R, LAA) vs Drew Rasmussen (R, TB)",
        "description": "LAA @ TB — PropFinder CSV slate. Reid Detmers vs Drew Rasmussen per imported matchup files.",
        "rows": [
            row("Zach Neto", "R", "+450", 93, "🌕 💣", ["vs Rasmussen"], """2 HR, 3 near-HR, 92.1 mph EV and 27.8% barrels. Draws opposing starter Rasmussen; LAA @ TB.""", blast="high"),
            row("Mike Trout", "R", "+363", 77, "💎", ["vs Rasmussen"], """1 HR, 2 near-HR, 88.6 mph EV and 12.5% barrels. Draws opposing starter Rasmussen; LAA @ TB.""", blast="good"),
            row("Vaughn Grissom", "R", "+680", 79, "💎", ["vs Rasmussen"], """1 HR, 1 near-HR, 94.5 mph EV and 13.6% barrels. Draws opposing starter Rasmussen; LAA @ TB."""),
            row("Junior Caminero", "R", "+184", 86, "🌕 💣", ["vs Detmers"], """1 HR, 1 near-HR, 94.1 mph EV and 24.0% barrels. Draws opposing starter Detmers; LAA @ TB.""", blast="high"),
            row("Yandy Diaz", "R", "+219", 79, "💎", ["vs Detmers"], """0 HR, 2 near-HR, 89.9 mph EV and 26.7% barrels. Draws opposing starter Detmers; LAA @ TB.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ NYM - Tyler Phillips (R, MIA) vs Christian Scott (R, NYM)",
        "description": "MIA @ NYM — PropFinder CSV slate. Tyler Phillips vs Christian Scott per imported matchup files.",
        "rows": [
            row("Xavier Edwards", "S", "+1200", 67, "💎", ["vs Scott"], """0 HR, 1 near-HR, 89.3 mph EV and 5.6% barrels. Draws opposing starter Scott; MIA @ NYM."""),
            row("Owen Caissie", "L", "+680", 92, "🌕 💣", ["vs Scott"], """1 HR, 1 near-HR, 99.5 mph EV and 33.3% barrels. Draws opposing starter Scott; MIA @ NYM.""", blast="good"),
            row("Juan Soto", "L", "+360", 87, "🌕 💣", ["vs Phillips"], """1 HR, 1 near-HR, 93.2 mph EV and 43.8% barrels. Draws opposing starter Phillips; MIA @ NYM.""", blast="high"),
            row("Brett Baty", "L", "+820", 84, "💎", ["vs Phillips"], """1 HR, 1 near-HR, 96.8 mph EV and 14.3% barrels. Draws opposing starter Phillips; MIA @ NYM.""", blast="good"),
            row("MJ Melendez", "L", "+550", 72, "💎", ["vs Scott"], """0 HR, 95.0 mph EV and 8.3% barrels. Draws opposing starter Scott; MIA @ NYM."""),
        ],
    },
    {
        "title": "MIL @ HOU - Brandon Sproat (R, MIL) vs Peter Lambert (R, HOU)",
        "description": "MIL @ HOU — PropFinder CSV slate. Brandon Sproat vs Peter Lambert per imported matchup files.",
        "rows": [
            row("Christian Yelich", "L", "+590", 76, "💎", ["vs Lambert"], """1 HR, 1 near-HR, 90.5 mph EV and 10.0% barrels. Draws opposing starter Lambert; MIL @ HOU.""", blast="good"),
            row("Jake Bauers", "L", "+440", 80, "💎", ["vs Lambert"], """1 HR, 1 near-HR, 88.5 mph EV and 28.6% barrels. Draws opposing starter Lambert; MIL @ HOU.""", blast="good"),
            row("Garrett Mitchell", "L", "+790", 98, "⭐ 🌕 💣", ["vs Lambert"], """Worst Pickz favorite with 2 HR, 4 near-HR, 98.9 mph EV and 27.3% barrels. Draws opposing starter Lambert; MIL @ HOU.""", blast="good"),
            row("Jackson Chourio", "R", "+490", 86, "⭐ 💎", ["vs Lambert"], """Worst Pickz favorite with 0 HR, 2 near-HR, 96.2 mph EV and 35.7% barrels. Draws opposing starter Lambert; MIL @ HOU.""", blast="good"),
            row("Isaac Paredes", "R", "+500", 87, "💎", ["vs Sproat"], """2 HR, 3 near-HR, 91.2 mph EV and 16.7% barrels. Draws opposing starter Sproat; MIL @ HOU.""", blast="good"),
            row("Yordan Alvarez", "L", "+300", 87, "⭐ 🌕 💣", ["vs Sproat"], """Worst Pickz favorite with 2 HR, 3 near-HR, 95.3 mph EV. Draws opposing starter Sproat; MIL @ HOU.""", blast="high"),
        ],
    },
    {
        "title": "MIN @ PIT - Bailey Ober (R, MIN) vs Mitch Keller (R, PIT)",
        "description": "MIN @ PIT — PropFinder CSV slate. Bailey Ober vs Mitch Keller per imported matchup files.",
        "rows": [
            row("Byron Buxton", "R", "+233", 95, "🌕 💣", ["vs Keller"], """3 HR, 3 near-HR, 91.5 mph EV and 22.2% barrels. Draws opposing starter Keller; MIN @ PIT.""", blast="high"),
            row("Spencer Horwitz", "L", "+730", 82, "🌕 💣", ["vs Ober"], """1 HR, 1 near-HR, 84.4 mph EV and 30.8% barrels. Draws opposing starter Ober; MIN @ PIT.""", blast="high"),
            row("Brandon Lowe", "L", "+340", 98, "⭐ 🌕 💣", ["vs Ober"], """Worst Pickz favorite with 2 HR, 4 near-HR, 95.6 mph EV and 30.8% barrels. Draws opposing starter Ober; MIN @ PIT.""", blast="high"),
            row("Oneil Cruz", "L", "+375", 80, "💎", ["vs Ober"], """1 HR, 2 near-HR, 96.4 mph EV. Draws opposing starter Ober; MIN @ PIT.""", blast="good"),
            row("Bryan Reynolds", "S", "+610", 74, "💎", ["vs Ober"], """1 HR, 1 near-HR, 84.6 mph EV and 11.1% barrels. Draws opposing starter Ober; MIN @ PIT.""", blast="good"),
            row("Marcell Ozuna", "R", "+582", 80, "💎", ["vs Ober"], """1 HR, 1 near-HR, 91.6 mph EV and 18.2% barrels. Draws opposing starter Ober; MIN @ PIT.""", blast="good"),
        ],
    },
    {
        "title": "NYY @ ATH - Ryan Weathers (R, NYY) vs J.T. Ginn (R, ATH)",
        "description": "NYY @ ATH — PropFinder CSV slate. Ryan Weathers vs J.T. Ginn per imported matchup files.",
        "rows": [
            row("Ben Rice", "L", "+340", 78, "💎", ["vs Ginn"], """2 HR, 2 near-HR, 90.0 mph EV. Draws opposing starter Ginn; NYY @ ATH.""", blast="good"),
            row("Aaron Judge", "R", "+220", 89, "🌕 💣", ["vs Ginn"], """1 HR, 2 near-HR, 97.7 mph EV and 15.4% barrels. Draws opposing starter Ginn; NYY @ ATH.""", blast="high"),
            row("Ryan McMahon", "L", "+540", 82, "💎", ["vs Ginn"], """2 HR, 2 near-HR, 88.0 mph EV and 18.2% barrels. Draws opposing starter Ginn; NYY @ ATH.""", blast="good"),
            row("Shea Langeliers", "R", "+280", 70, "💎", ["vs Weathers"], """0 HR, 91.4 mph EV and 12.5% barrels. Draws opposing starter Weathers; NYY @ ATH."""),
            row("Colby Thomas", "R", "+470", 69, "💎", ["vs Weathers"], """0 HR, 1 near-HR, 87.6 mph EV and 15.4% barrels. Draws opposing starter Weathers; NYY @ ATH."""),
        ],
    },
    {
        "title": "PHI @ LAD - Jesus Luzardo (R, PHI) vs Roki Sasaki (R, LAD)",
        "description": "PHI @ LAD — PropFinder CSV slate. Jesus Luzardo vs Roki Sasaki per imported matchup files.",
        "rows": [
            row("Kyle Schwarber", "L", "+290", 98, "🚀 ⭐ 🌕 💣", ["vs Sasaki"], """Worst Pickz favorite with 3 HR, 3 near-HR, 101.7 mph EV and 30.0% barrels. Draws opposing starter Sasaki; PHI @ LAD.""", blast="high"),
            row("Trea Turner", "R", "+380", 90, "⭐ 🌕 💣", ["vs Sasaki"], """Worst Pickz favorite with 2 HR, 3 near-HR, 92.5 mph EV and 22.2% barrels. Draws opposing starter Sasaki; PHI @ LAD.""", blast="good"),
            row("Bryce Harper", "L", "+500", 82, "⭐ 💎", ["vs Sasaki"], """Worst Pickz favorite with 1 HR, 1 near-HR, 93.0 mph EV and 22.2% barrels. Draws opposing starter Sasaki; PHI @ LAD.""", blast="good"),
            row("Freddie Freeman", "L", "+550", 82, "🌕 💣", ["vs Luzardo"], """0 HR, 94.4 mph EV and 33.3% barrels. Draws opposing starter Luzardo; PHI @ LAD.""", blast="high"),
            row("Shohei Ohtani", "L", "+310", 76, "🌕 💣", ["vs Luzardo"], """0 HR, 82.3 mph EV and 30.0% barrels. Draws opposing starter Luzardo; PHI @ LAD.""", blast="high"),
            row("Will Smith", "R", "+578", 86, "🌕 💣", ["vs Luzardo"], """0 HR, 97.7 mph EV and 33.3% barrels. Draws opposing starter Luzardo; PHI @ LAD.""", blast="high"),
            row("Max Muncy", "L", "+320", 78, "💎", ["vs Luzardo"], """0 HR, 91.6 mph EV and 50.0% barrels. Draws opposing starter Luzardo; PHI @ LAD.""", blast="good"),
            row("Andy Pages", "R", "+582", 71, "💎", ["vs Luzardo"], """1 HR, 1 near-HR, 87.7 mph EV and 7.7% barrels. Draws opposing starter Luzardo; PHI @ LAD."""),
        ],
    },
    {
        "title": "SD @ WSH - Michael King (R, SD) vs Foster Griffin (R, WSH)",
        "description": "SD @ WSH — PropFinder CSV slate. Michael King vs Foster Griffin per imported matchup files.",
        "rows": [
            row("Fernando Tatis", "R", "+420", 76, "💎", ["vs Griffin"], """0 HR, 3 near-HR, 88.2 mph EV and 17.0% barrels. Draws opposing starter Griffin; SD @ WSH.""", blast="good"),
            row("Manny Machado", "R", "+520", 80, "🌕 💣", ["vs Griffin"], """1 HR, 2 near-HR, 86.8 mph EV and 16.7% barrels. Draws opposing starter Griffin; SD @ WSH.""", blast="high"),
            row("James Wood", "L", "+360", 82, "⭐ 💎", ["vs King"], """Worst Pickz favorite with 1 HR, 3 near-HR, 96.2 mph EV. Draws opposing starter King; SD @ WSH.""", blast="good"),
            row("CJ Abrams", "L", "+590", 80, "💎", ["vs King"], """1 HR, 1 near-HR, 93.8 mph EV and 11.1% barrels. Draws opposing starter King; SD @ WSH.""", blast="good"),
            row("Jorbit Vivas", "L", "+1300", 71, "💎", ["vs King"], """1 HR, 1 near-HR, 85.6 mph EV and 8.3% barrels. Draws opposing starter King; SD @ WSH."""),
        ],
    },
    {
        "title": "SF @ COL - Adrian Houser (R, SF) vs Ryan Feltner 🧤 (R, COL)",
        "description": "SF @ COL — PropFinder CSV slate. Attack lanes: Ryan Feltner (1.64 HR risk).",
        "rows": [
            row("Willy Adames", "R", "+540", 98, "⭐ 🌕 💣", ["vs Feltner"], """Worst Pickz favorite with 4 HR, 4 near-HR, 92.3 mph EV and 22.0% barrels. Draws opposing starter Feltner; SF @ COL.""", blast="high"),
            row("Rafael Devers", "L", "+380", 97, "🌕 💣", ["vs Feltner"], """1 HR, 4 near-HR, 97.9 mph EV and 28.0% barrels. Draws opposing starter Feltner; SF @ COL.""", blast="high"),
            row("Tj Rumfield", "L", "+880", 78, "💎", ["vs Houser"], """1 HR, 3 near-HR, 81.2 mph EV and 11.1% barrels. Draws opposing starter Houser; SF @ COL.""", blast="good"),
            row("Hunter Goodman", "R", "+410", 68, "💎", ["vs Houser"], """0 HR, 87.4 mph EV and 11.1% barrels. Draws opposing starter Houser; SF @ COL.""", blast="good"),
            row("Eric Haase", "R", "+950", 86, "💎", ["vs Feltner"], """2 HR, 3 near-HR, 89.5 mph EV and 25.0% barrels. Draws opposing starter Feltner; SF @ COL."""),
        ],
    },
    {
        "title": "TOR @ BAL - Trey Yesavage (R, TOR) vs Brandon Young (R, BAL)",
        "description": "TOR @ BAL — PropFinder CSV slate. Trey Yesavage vs Brandon Young per imported matchup files.",
        "rows": [
            row("Pete Alonso", "R", "+410", 98, "🌕 💣", ["vs Yesavage"], """3 HR, 3 near-HR, 97.8 mph EV and 20.0% barrels. Draws opposing starter Yesavage; TOR @ BAL.""", blast="high"),
            row("Jackson Holliday", "L", "+850", 87, "💎", ["vs Yesavage"], """2 HR, 2 near-HR, 95.2 mph EV and 12.5% barrels. Draws opposing starter Yesavage; TOR @ BAL.""", blast="good"),
            row("Samuel Basallo", "L", "+470", 85, "💎", ["vs Yesavage"], """1 HR, 1 near-HR, 95.2 mph EV and 22.2% barrels. Draws opposing starter Yesavage; TOR @ BAL.""", blast="good"),
            row("Blaze Alexander", "R", "N/A", 87, "💎", ["vs Young"], """1 HR, 3 near-HR, 96.1 mph EV and 14.3% barrels. Draws opposing starter Young; TOR @ BAL.""", blast="good"),
            row("Yohendrick Pinango", "L", "N/A", 67, "💎", ["vs Young"], """0 HR, 88.1 mph EV and 14.3% barrels. Draws opposing starter Young; TOR @ BAL."""),
            row("Jesus Sanchez", "L", "+720", 86, "⭐ 💎", ["vs Young"], """Worst Pickz favorite with 1 HR, 2 near-HR, 96.0 mph EV and 17.9% barrels. Draws opposing starter Young; TOR @ BAL.""", blast="good"),
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
