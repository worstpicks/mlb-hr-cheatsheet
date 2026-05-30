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
    "Fedde",
    "Lorenzen",
    "Holmes",
    "Imanaga",
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
        "title": "ATL @ CIN - Grant Holmes 🧤 (R, ATL) vs Chris Paddack (R, CIN)",
        "description": "Great American Ball Park — smallest outfield in MLB with 76°F partially cloudy air and 2 mph wind. Grant Holmes carries 1.22 HR risk; Chris Paddack is attackable to both splits.",
        "rows": [
            row("Matt Olson", "L", "+270", 78, "💎 📜", ["vs Paddack"], """0 HR, 96.1 mph EV; 9 AB BvP versus Paddack. Draws opposing starter Paddack; Great American Ball Park.""", blast="good"),
            row("Austin Riley", "R", "+360", 86, "🌕 💣", ["vs Paddack"], """2 HR, 2 near-HR, 95.6 mph EV and 14.3% barrels. Draws opposing starter Paddack; Great American Ball Park.""", blast="high"),
            row("Mike Yastrzemski", "L", "+550", 84, "💎 📜", ["vs Paddack"], """2 HR, 3 near-HR, 90.8 mph EV and 8.3% barrels; 25 AB BvP versus Paddack. Draws opposing starter Paddack; Great American Ball Park.""", blast="good"),
            row("Eugenio Suarez", "R", "+374", 83, "💎 📜", ["vs Holmes"], """0 HR, 1 near-HR, 83.9 mph EV and 6.7% barrels; 6 AB BvP versus Holmes with 1 HR. Draws opposing starter Holmes; Great American Ball Park.""", blast="good"),
            row("Elly De La Cruz", "S", "+406", 85, "💎", ["vs Holmes"], """2 HR, 2 near-HR, 96.2 mph EV and 20.0% barrels. Draws opposing starter Holmes; Great American Ball Park.""", blast="good"),
        ],
    },
    {
        "title": "SD @ WSH - Lucas Giolito (R, SD) vs Andrew Alvarez (L, WSH)",
        "description": "Nationals Park — great contact environment with 75°F clear air and 7 mph wind. Lucas Giolito suppresses (-1.58 HR risk); James Wood and Nationals bats attack Alvarez.",
        "rows": [
            row("Fernando Tatis", "R", "+420", 76, "💎", ["vs Alvarez"], """0 HR, 3 near-HR, 88.2 mph EV and 17.0% barrels. Draws opposing starter Alvarez; Nationals Park.""", blast="good"),
            row("Manny Machado", "R", "+470", 90, "🚀 🌕 💣", ["vs Alvarez"], """1 HR, 1 near-HR, 100.5 mph EV and 16.7% barrels. Draws opposing starter Alvarez; Nationals Park.""", blast="high"),
            row("James Wood", "L", "+350", 82, "⭐ 💎", ["vs Giolito"], """Worst Pickz favorite with 0 HR, 1 near-HR, 96.0 mph EV. Draws opposing starter Giolito; Nationals Park.""", blast="good"),
            row("CJ Abrams", "L", "+540", 80, "💎", ["vs Giolito"], """1 HR, 1 near-HR, 93.1 mph EV and 11.1% barrels. Draws opposing starter Giolito; Nationals Park.""", blast="good"),
            row("Jorbit Vivas", "L", "N/A", 72, "💎", ["vs Giolito"], """1 HR, 1 near-HR, 88.5 mph EV and 8.3% barrels. Draws opposing starter Giolito; Nationals Park."""),
        ],
    },
    {
        "title": "MIN @ PIT - Taj Bradley (R, MIN) vs Jared Jones (R, PIT)",
        "description": "PNC Park — 74°F clear air with 10 mph out-blowing wind. Taj Bradley owns +0.66 vs LHB; Brandon Lowe and Spencer Horwitz are the premium lefty attack lane.",
        "rows": [
            row("Byron Buxton", "R", "+340", 91, "🌕 💣", ["vs Jones"], """2 HR, 2 near-HR, 98.6 mph EV and 22.2% barrels. Draws opposing starter Jones; PNC Park.""", blast="high"),
            row("Spencer Horwitz", "L", "+730", 86, "🌕 💣", ["vs Bradley"], """3 HR, 3 near-HR, 87.4 mph EV and 30.8% barrels. Draws opposing starter Bradley; PNC Park.""", blast="high"),
            row("Brandon Lowe", "L", "+340", 92, "⭐ 🌕 💣", ["vs Bradley"], """Worst Pickz favorite with 2 HR, 4 near-HR, 97.6 mph EV and 30.8% barrels. Draws opposing starter Bradley; PNC Park.""", blast="high"),
            row("Oneil Cruz", "L", "+375", 79, "🚀 💎", ["vs Bradley"], """0 HR, 100.1 mph EV. Draws opposing starter Bradley; PNC Park.""", blast="good"),
            row("Bryan Reynolds", "S", "+610", 76, "💎", ["vs Bradley"], """1 HR, 1 near-HR, 87.1 mph EV and 11.1% barrels. Draws opposing starter Bradley; PNC Park.""", blast="good"),
            row("Marcell Ozuna", "R", "+582", 74, "💎", ["vs Bradley"], """1 HR, 1 near-HR, 90.0 mph EV and 18.2% barrels. Draws opposing starter Bradley; PNC Park.""", blast="good"),
        ],
    },
    {
        "title": "TOR @ BAL - Austin Voth (R, TOR) vs Trevor Rogers (L, BAL)",
        "description": "Oriole Park — 75°F clear air with 6 mph crosswind and HR-friendly right side. Trevor Rogers owns 0.87 vs RHB for Toronto; Pete Alonso and Baltimore righties attack Austin Voth.",
        "rows": [
            row("Pete Alonso", "R", "+380", 88, "🌕 💣", ["vs Voth"], """2 HR, 2 near-HR, 97.5 mph EV and 20.0% barrels. Draws opposing starter Voth; Oriole Park.""", blast="high"),
            row("Jackson Holliday", "L", "N/A", 72, "💎", ["vs Voth"], """1 HR, 1 near-HR, 96.2 mph EV and 12.5% barrels. Draws opposing starter Voth; Oriole Park.""", blast="good"),
            row("Samuel Basallo", "L", "N/A", 80, "🚀 💎", ["vs Voth"], """2 HR, 2 near-HR, 100.1 mph EV and 22.2% barrels. Draws opposing starter Voth; Oriole Park.""", blast="good"),
            row("Blaze Alexander", "R", "N/A", 78, "💎", ["vs Rogers"], """1 HR, 3 near-HR, 89.0 mph EV and 14.3% barrels. Draws opposing starter Rogers; Oriole Park.""", blast="good"),
            row("Yohendrick Pinango", "L", "N/A", 70, "💎", ["vs Rogers"], """1 HR, 1 near-HR, 91.0 mph EV and 14.3% barrels. Draws opposing starter Rogers; Oriole Park."""),
            row("Jesus Sanchez", "L", "+520", 81, "⭐ 💎", ["vs Rogers"], """Worst Pickz favorite with 3 HR, 3 near-HR, 92.0 mph EV and 17.9% barrels. Draws opposing starter Rogers; Oriole Park.""", blast="good"),
        ],
    },
    {
        "title": "LAA @ TB - Walbert Urena (R, LAA) vs Nick Martinez (R, TB)",
        "description": "Tropicana Field — closed dome, flat +2% HR row. Nick Martinez suppresses (-0.67 HR risk); Junior Caminero and Rays bats lean on form versus Urena.",
        "rows": [
            row("Zach Neto", "R", "+450", 87, "🌕 💣", ["vs Martinez"], """3 HR, 4 near-HR, 92.5 mph EV and 27.8% barrels. Draws opposing starter Martinez; Tropicana Field.""", blast="high"),
            row("Mike Trout", "R", "+363", 79, "💎 📜", ["vs Martinez"], """1 HR, 1 near-HR, 89.7 mph EV and 12.5% barrels; 25 AB BvP versus Martinez. Draws opposing starter Martinez; Tropicana Field.""", blast="good"),
            row("Vaughn Grissom", "R", "+680", 71, "💎", ["vs Martinez"], """1 HR, 3 near-HR, 91.0 mph EV and 13.6% barrels. Draws opposing starter Martinez; Tropicana Field."""),
            row("Junior Caminero", "R", "+375", 84, "🌕 💣", ["vs Urena"], """2 HR, 6 near-HR, 95.7 mph EV and 24.0% barrels. Draws opposing starter Urena; Tropicana Field.""", blast="high"),
            row("Yandy Diaz", "R", "+710", 83, "💎", ["vs Urena"], """2 HR, 3 near-HR, 91.3 mph EV and 26.7% barrels. Draws opposing starter Urena; Tropicana Field.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ NYM - Max Meyer (R, MIA) vs Freddy Peralta (R, NYM)",
        "description": "Citi Field — poor contact environment with 73°F air and 12 mph out wind. Juan Soto owns slate-best form; Meyer is the Mets' cleaner attack target.",
        "rows": [
            row("Xavier Edwards", "S", "+1300", 62, "💎", ["vs Peralta"], """0 HR, 84.3 mph EV and 5.6% barrels. Draws opposing starter Peralta; Citi Field."""),
            row("Owen Caissie", "L", "+760", 84, "💎", ["vs Peralta"], """1 HR, 1 near-HR, 97.6 mph EV and 33.3% barrels. Draws opposing starter Peralta; Citi Field.""", blast="good"),
            row("Juan Soto", "L", "+350", 95, "🌕 💣", ["vs Meyer"], """6 HR, 7 near-HR, 99.2 mph EV and 43.8% barrels. Draws opposing starter Meyer; Citi Field.""", blast="high"),
            row("Brett Baty", "L", "+710", 77, "💎", ["vs Meyer"], """1 HR, 1 near-HR, 90.8 mph EV and 14.3% barrels. Draws opposing starter Meyer; Citi Field.""", blast="good"),
            row("MJ Melendez", "L", "+550", 68, "💎", ["vs Peralta"], """0 HR, 90.7 mph EV and 8.3% barrels. Draws opposing starter Peralta; Citi Field."""),
        ],
    },
    {
        "title": "BOS @ CLE - Brayan Bello (R, BOS) vs Slade Cecconi (R, CLE)",
        "description": "Progressive Field — high wind receptivity (17 mph) with 74°F clear air. Wilyer Abreu and Willson Contreras own the loudest Boston form versus Cecconi and Bello.",
        "rows": [
            row("Willson Contreras", "R", "+504", 80, "💎", ["vs Cecconi"], """2 HR, 2 near-HR, 87.7 mph EV and 8.7% barrels. Draws opposing starter Cecconi; Progressive Field.""", blast="good"),
            row("Wilyer Abreu", "L", "+580", 79, "💎", ["vs Cecconi"], """2 HR, 5 near-HR, 94.0 mph EV and 18.9% barrels. Draws opposing starter Cecconi; Progressive Field.""", blast="good"),
            row("Patrick Bailey", "S", "+1140", 70, "💎", ["vs Bello"], """1 HR, 2 near-HR, 89.5 mph EV and 10.0% barrels. Draws opposing starter Bello; Progressive Field."""),
            row("Travis Bazzana", "L", "+910", 68, "💎", ["vs Bello"], """0 HR, 2 near-HR, 82.9 mph EV and 10.0% barrels. Draws opposing starter Bello; Progressive Field."""),
        ],
    },
    {
        "title": "CHC @ STL - Shota Imanaga 🧤 (L, CHC) vs Andre Pallante (R, STL)",
        "description": "Busch Stadium — large outfield with 79°F air and 6 mph wind. Shota Imanaga is a bum arm (1.04 HR risk, 1.68 vs LHB); Jordan Walker and Alec Burleson lead the Cardinal attack.",
        "rows": [
            row("Ian Happ", "S", "+525", 78, "⭐ 💎", ["vs Pallante"], """Worst Pickz favorite with 1 HR, 1 near-HR, 87.9 mph EV and 14.3% barrels. Draws opposing starter Pallante; Busch Stadium.""", blast="good"),
            row("Michael Busch", "L", "+590", 76, "💎 📜", ["vs Pallante"], """1 HR, 4 near-HR, 92.0 mph EV and 25.0% barrels; 4 AB BvP versus Pallante with 1 HR. Draws opposing starter Pallante; Busch Stadium.""", blast="good"),
            row("Seiya Suzuki", "R", "+520", 82, "💎 📜", ["vs Pallante"], """2 HR, 2 near-HR, 94.5 mph EV and 26.1% barrels; 8 AB BvP versus Pallante with 2 HR. Draws opposing starter Pallante; Busch Stadium.""", blast="good"),
            row("Jordan Walker", "R", "+410", 86, "🚀 ⭐ 🌕 💣", ["vs Imanaga"], """Worst Pickz favorite with 1 HR, 2 near-HR, 101.8 mph EV and 25.0% barrels. Draws opposing starter Imanaga; Busch Stadium.""", blast="high"),
            row("Alec Burleson", "L", "+500", 80, "⭐ 💎", ["vs Imanaga"], """Worst Pickz favorite with 0 HR, 93.4 mph EV. Draws opposing starter Imanaga; Busch Stadium.""", blast="good"),
            row("Bryan Torres", "L", "+1120", 66, "💎", ["vs Imanaga"], """0 HR, 87.1 mph EV. Draws opposing starter Imanaga; Busch Stadium."""),
        ],
    },
    {
        "title": "DET @ CWS - Troy Melton (R, DET) vs Erick Fedde 🧤 (R, CWS)",
        "description": "Rate Field — smallest outfield in MLB with 66°F air and 8 mph wind. Erick Fedde is the slate's top HR-risk arm (1.67, 1.94 vs RHB); Dillon Dingler and Miguel Vargas are live.",
        "rows": [
            row("Dillon Dingler", "R", "+480", 79, "⭐ 💎", ["vs Fedde"], """Worst Pickz favorite with 4 HR, 1 near-HR, 92.0 mph EV and 17.6% barrels. Draws opposing starter Fedde; Rate Field.""", blast="good"),
            row("Spencer Torkelson", "R", "+500", 72, "💎", ["vs Fedde"], """0 HR, 1 near-HR, 88.4 mph EV and 12.5% barrels. Draws opposing starter Fedde; Rate Field."""),
            row("Randal Grichuk", "R", "N/A", 74, "⭐ 💎", ["vs Fedde"], """Worst Pickz favorite with 0 HR, 86.5 mph EV. Draws opposing starter Fedde; Rate Field."""),
            row("Miguel Vargas", "R", "+470", 82, "💎", ["vs Melton"], """0 HR, 1 near-HR, 94.1 mph EV and 9.1% barrels. Draws opposing starter Melton; Rate Field.""", blast="good"),
        ],
    },
    {
        "title": "KC @ TEX - Stephen Kolek (R, KC) vs MacKenzie Gore (L, TEX)",
        "description": "Globe Life Field — roof closed with 87°F dome air and +8% typical flight. MacKenzie Gore suppresses; Brandon Nimmo and Jac Caglianone get the cleaner Texas lanes.",
        "rows": [
            row("Salvador Perez", "R", "+516", 78, "💎", ["vs Gore"], """1 HR, 1 near-HR, 90.7 mph EV and 11.1% barrels. Draws opposing starter Gore; Globe Life Field.""", blast="good"),
            row("Jac Caglianone", "L", "+620", 80, "⭐ 💎", ["vs Gore"], """Worst Pickz favorite with 2 HR, 5 near-HR, 94.0 mph EV and 29.9% barrels. Draws opposing starter Gore; Globe Life Field.""", blast="good"),
            row("Brandon Nimmo", "L", "+431", 81, "⭐ 💎", ["vs Kolek"], """Worst Pickz favorite with 1 HR, 3 near-HR, 91.0 mph EV and 20.0% barrels. Draws opposing starter Kolek; Globe Life Field.""", blast="good"),
            row("Kyle Higashioka", "R", "N/A", 68, "📜", ["vs Kolek"], """1 HR, 1 near-HR, 84.7 mph EV and 5.9% barrels; 2 AB BvP versus Kolek with 1 HR. Draws opposing starter Kolek; Globe Life Field."""),
        ],
    },
    {
        "title": "MIL @ HOU - Coleman Crow (R, MIL) vs Kai-Wei Teng (R, HOU)",
        "description": "Daikin Park — roof closed with 87°F dome air. Coleman Crow suppresses (-1.04 HR risk); Yordan Alvarez and Houston bats attack Crow.",
        "rows": [
            row("Christian Yelich", "L", "+590", 76, "💎", ["vs Teng"], """1 HR, 1 near-HR, 92.0 mph EV and 10.0% barrels. Draws opposing starter Teng; Daikin Park.""", blast="good"),
            row("Jake Bauers", "L", "+440", 79, "💎", ["vs Teng"], """0 HR, 94.3 mph EV and 28.6% barrels. Draws opposing starter Teng; Daikin Park.""", blast="good"),
            row("Garrett Mitchell", "L", "+790", 82, "⭐ 💎", ["vs Teng"], """Worst Pickz favorite with 1 HR, 3 near-HR, 99.0 mph EV and 27.3% barrels. Draws opposing starter Teng; Daikin Park.""", blast="good"),
            row("Jackson Chourio", "R", "+490", 83, "⭐ 💎", ["vs Teng"], """Worst Pickz favorite with 0 HR, 1 near-HR, 99.7 mph EV and 35.7% barrels. Draws opposing starter Teng; Daikin Park.""", blast="good"),
            row("Isaac Paredes", "R", "+500", 80, "💎", ["vs Crow"], """2 HR, 2 near-HR, 88.6 mph EV and 16.7% barrels. Draws opposing starter Crow; Daikin Park.""", blast="good"),
            row("Yordan Alvarez", "L", "+300", 85, "⭐ 🌕 💣", ["vs Crow"], """Worst Pickz favorite with 0 HR, 1 near-HR, 98.1 mph EV. Draws opposing starter Crow; Daikin Park.""", blast="high"),
        ],
    },
    {
        "title": "SF @ COL - Logan Webb (R, SF) vs Michael Lorenzen 🧤 (R, COL)",
        "description": "Coors Field — slate-best +29 altitude boost with 76°F air and 7 mph wind. Michael Lorenzen is a bum arm (1.24 HR risk, 2.29 vs LHB); Devers and Adames lead the Giants attack.",
        "rows": [
            row("Willy Adames", "R", "+540", 84, "⭐ 🌕 💣", ["vs Lorenzen"], """Worst Pickz favorite with 2 HR, 3 near-HR, 96.5 mph EV and 22.0% barrels. Draws opposing starter Lorenzen; Coors Field.""", blast="high"),
            row("Rafael Devers", "L", "+380", 88, "🌕 💣", ["vs Lorenzen"], """2 HR, 3 near-HR, 98.4 mph EV and 28.0% barrels. Draws opposing starter Lorenzen; Coors Field.""", blast="high"),
            row("Tj Rumfield", "L", "+880", 74, "💎", ["vs Webb"], """1 HR, 3 near-HR, 82.5 mph EV and 11.1% barrels. Draws opposing starter Webb; Coors Field.""", blast="good"),
            row("Hunter Goodman", "R", "+410", 78, "💎", ["vs Webb"], """1 HR, 1 near-HR, 89.8 mph EV and 11.1% barrels. Draws opposing starter Webb; Coors Field.""", blast="good"),
            row("Eric Haase", "R", "+950", 70, "💎 📜", ["vs Lorenzen"], """0 HR, 88.0 mph EV and 25.0% barrels; 3 AB BvP versus Lorenzen. Draws opposing starter Lorenzen; Coors Field."""),
        ],
    },
    {
        "title": "NYY @ ATH - Carlos Rodon (L, NYY) vs Luis Severino (R, ATH)",
        "description": "Sutter Health Park — very high wind receptivity with 73°F clear air and 6 mph wind. Luis Severino is attackable; Aaron Judge and A's bats get plus carry.",
        "rows": [
            row("Ben Rice", "L", "+328", 84, "💎", ["vs Severino"], """1 HR, 1 near-HR, 90.0 mph EV. Draws opposing starter Severino; Sutter Health Park.""", blast="good"),
            row("Aaron Judge", "R", "+235", 84, "🌕 💣 📜", ["vs Severino"], """1 HR, 2 near-HR, 97.0 mph EV and 15.4% barrels; 20 AB BvP versus Severino. Draws opposing starter Severino; Sutter Health Park.""", blast="high"),
            row("Ryan McMahon", "L", "N/A", 76, "💎", ["vs Severino"], """2 HR, 2 near-HR, 88.3 mph EV and 18.2% barrels. Draws opposing starter Severino; Sutter Health Park.""", blast="good"),
            row("Shea Langeliers", "R", "+392", 74, "💎", ["vs Rodon"], """0 HR, 87.2 mph EV and 12.5% barrels. Draws opposing starter Rodon; Sutter Health Park."""),
            row("Colby Thomas", "R", "+610", 72, "💎", ["vs Rodon"], """0 HR, 2 near-HR, 87.0 mph EV and 15.4% barrels. Draws opposing starter Rodon; Sutter Health Park."""),
        ],
    },
    {
        "title": "ARI @ SEA - Zac Gallen (R, ARI) vs George Kirby (R, SEA)",
        "description": "T-Mobile Park — slate-harshest -6% altitude drag with 57°F dome air. George Kirby suppresses; Julio Rodriguez and Seattle bats face Gallen in a contact-poor row.",
        "rows": [
            row("Ketel Marte", "S", "+520", 86, "⭐ 💎", ["vs Kirby"], """Worst Pickz favorite with 2 HR, 2 near-HR, 78.4 mph EV and 13.3% barrels. Draws opposing starter Kirby; T-Mobile Park.""", blast="good"),
            row("Corbin Carroll", "L", "+550", 84, "💎", ["vs Kirby"], """1 HR, 2 near-HR, 94.0 mph EV and 16.7% barrels. Draws opposing starter Kirby; T-Mobile Park.""", blast="good"),
            row("Julio Rodriguez", "R", "+500", 82, "💎", ["vs Gallen"], """2 HR, 2 near-HR, 90.1 mph EV and 10.5% barrels. Draws opposing starter Gallen; T-Mobile Park.""", blast="good"),
            row("Luke Raley", "L", "+423", 72, "⭐ 💎", ["vs Gallen"], """Worst Pickz favorite with 0 HR, 85.0 mph EV. Draws opposing starter Gallen; T-Mobile Park."""),
        ],
    },
    {
        "title": "PHI @ LAD - Zack Wheeler (R, PHI) vs Justin Wrobleski (L, LAD)",
        "description": "Dodger Stadium — +6% HR row with 67°F clear air and consistent 13 mph out-blowing wind. Zack Wheeler suppresses (-0.68 HR risk); Schwarber, Turner, and Harper attack Wrobleski.",
        "rows": [
            row("Kyle Schwarber", "L", "+290", 92, "⭐ 🌕 💣", ["vs Wrobleski"], """Worst Pickz favorite with 3 HR, 3 near-HR, 95.1 mph EV and 30.0% barrels. Draws opposing starter Wrobleski; Dodger Stadium.""", blast="high"),
            row("Trea Turner", "R", "+380", 84, "⭐ 💎", ["vs Wrobleski"], """Worst Pickz favorite with 2 HR, 2 near-HR, 94.0 mph EV and 22.2% barrels. Draws opposing starter Wrobleski; Dodger Stadium.""", blast="good"),
            row("Bryce Harper", "L", "+500", 80, "⭐ 💎", ["vs Wrobleski"], """Worst Pickz favorite with 0 HR, 2 near-HR, 95.4 mph EV and 22.2% barrels. Draws opposing starter Wrobleski; Dodger Stadium.""", blast="good"),
            row("Freddie Freeman", "L", "+550", 89, "🌕 💣 📜", ["vs Wheeler"], """3 HR, 3 near-HR, 91.2 mph EV and 33.3% barrels; 54 AB BvP versus Wheeler with career HR history. Draws opposing starter Wheeler; Dodger Stadium.""", blast="high"),
            row("Shohei Ohtani", "L", "+310", 90, "🌕 💣", ["vs Wheeler"], """2 HR, 2 near-HR, 96.6 mph EV and 30.0% barrels. Draws opposing starter Wheeler; Dodger Stadium.""", blast="high"),
            row("Will Smith", "R", "+578", 87, "🌕 💣 📜", ["vs Wheeler"], """2 HR, 4 near-HR, 96.2 mph EV and 33.3% barrels; 8 AB BvP versus Wheeler. Draws opposing starter Wheeler; Dodger Stadium.""", blast="high"),
            row("Max Muncy", "L", "+320", 81, "💎 📜", ["vs Wheeler"], """1 HR, 2 near-HR, 89.0 mph EV and 50.0% barrels; 9 AB BvP versus Wheeler with 1 HR. Draws opposing starter Wheeler; Dodger Stadium.""", blast="good"),
            row("Andy Pages", "R", "+582", 72, "💎", ["vs Wheeler"], """0 HR, 1 near-HR, 89.7 mph EV and 7.7% barrels. Draws opposing starter Wheeler; Dodger Stadium."""),
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
