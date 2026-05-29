#!/usr/bin/env python3
"""Generate games[] block for 2026-05-29 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Mike Yastrzemski (L)",
    "Gavin Sheets (L)",
    "Brandon Lowe (L)",
    "Byron Buxton (R)",
    "Kazuma Okamoto (R)",
    "George Springer (R)",
    "Jonathan Aranda (L)",
    "Jo Adell (R)",
    "Juan Soto (L)",
    "Rhys Hoskins (R)",
    "Jarren Duran (L)",
    "Jordan Walker (R)",
    "Munetaka Murakami (L)",
    "Miguel Vargas (R)",
    "Salvador Perez (R)",
    "Jackson Chourio (R)",
    "Ben Rice (L)",
    "Ketel Marte (S)",
    "Corbin Carroll (L)",
    "Will Smith (R)",
    "Freddie Freeman (L)",
    "Shohei Ohtani (L)",
    "Kyle Schwarber (L)",
    "Bryce Harper (L)",
}

PLAYER_TEAMS = {
    "AJ Ewing (L)": "NYM",
    "Aaron Judge (R)": "NYY",
    "Alec Bohm (R)": "PHI",
    "Andy Pages (R)": "LAD",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Blaze Alexander (R)": "TOR",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Bryan Rocchio (S)": "CLE",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Ceddanne Rafaela (R)": "BOS",
    "Christian Walker (R)": "HOU",
    "Christian Yelich (L)": "MIL",
    "Colby Thomas (R)": "ATH",
    "Colson Montgomery (L)": "CWS",
    "Colt Emerson (L)": "SEA",
    "Corbin Carroll (L)": "ARI",
    "Dominic Canzone (L)": "SEA",
    "Elly De La Cruz (S)": "CIN",
    "Freddie Freeman (L)": "LAD",
    "Gabriel Moreno (R)": "ARI",
    "Gage Workman (L)": "DET",
    "Garrett Mitchell (L)": "MIL",
    "Gavin Sheets (L)": "SD",
    "George Springer (R)": "TOR",
    "Gunnar Henderson (L)": "BAL",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "TB",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Isaac Paredes (R)": "HOU",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "Jackson Chourio (R)": "MIL",
    "Jackson Holliday (L)": "BAL",
    "Jackson Merrill (L)": "SD",
    "Jacob Young (R)": "WSH",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jarren Duran (L)": "BOS",
    "Jo Adell (R)": "LAA",
    "Joc Pederson (L)": "TEX",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Jose Ramirez (S)": "CLE",
    "Juan Soto (L)": "NYM",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Kyle Schwarber (L)": "PHI",
    "Luis Garcia Jr. (L)": "WSH",
    "Luke Raley (L)": "SEA",
    "Manny Machado (R)": "SD",
    "Marcell Ozuna (R)": "PIT",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Mike Yastrzemski (L)": "ATL",
    "Mitch Garver (R)": "SEA",
    "Munetaka Murakami (L)": "CWS",
    "Nick Kurtz (L)": "ATH",
    "Nolan Arenado (R)": "ARI",
    "Nolan Gorman (L)": "STL",
    "Owen Caissie (L)": "MIA",
    "Patrick Wisdom (R)": "SEA",
    "Pete Crow-Armstrong (L)": "CHC",
    "Ramon Laureano (R)": "SD",
    "Rhys Hoskins (R)": "CLE",
    "Richie Palacios (L)": "TB",
    "Riley Greene (L)": "DET",
    "Ronald Acuna Jr. (R)": "ATL",
    "Ryan Kreidler (R)": "MIN",
    "Ryan McMahon (L)": "NYY",
    "Salvador Perez (R)": "KC",
    "Samuel Bassallo (L)": "BAL",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Horwitz (L)": "PIT",
    "Spencer Torkelson (R)": "DET",
    "Tj Rumfield (L)": "COL",
    "Will Smith (R)": "LAD",
    "Willson Contreras (R)": "BOS",
    "Xavier Edwards (S)": "MIA",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
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


def n(player, pitcher, park, angle):
    angle = angle.rstrip(".")
    return f"{angle}. Draws opposing starter {pitcher}; {park}."


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
        "description": "Great American Ball Park \u2014 Ballpark Pal grades +9% HR and +13% combined runs with 75\u00b0F partially cloudy air and 2 mph wind. Grant Holmes carries 1.22 HR risk; Chris Paddack is attackable to both splits at the smallest outfield in MLB.",
        "rows": [
            row("Michael Harris II", "L", "+311", 88, "🌕 💣", ["vs Paddack"], """3 HR, 4 near-HR, 90.1 mph EV and 18.8% barrels. Draws opposing starter Paddack; Great American Ball Park.""", blast="high"),
            row("Austin Riley", "R", "+360", 86, "🌕 💣", ["vs Paddack"], """2 HR, 2 near-HR, 95.6 mph EV and 14.3% barrels. Draws opposing starter Paddack; Great American Ball Park.""", blast="high"),
            row("Mike Yastrzemski", "L", "+550", 84, "⭐ 💎 📜", ["vs Paddack"], """Worst Pickz favorite with 2 HR, 3 near-HR, 90.8 mph EV and 8.3% barrels; 25 AB BvP versus Paddack. Draws opposing starter Paddack; Great American Ball Park.""", blast="good"),
            row("Matt Olson", "L", "+270", 78, "💎 📜", ["vs Paddack"], """0 HR, 96.1 mph EV; 9 AB BvP versus Paddack. Draws opposing starter Paddack; Great American Ball Park.""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+375", 82, "💎", ["vs Paddack"], """1 HR, 2 near-HR, 94.4 mph EV and 18.2% barrels. Draws opposing starter Paddack; Great American Ball Park.""", blast="good"),
            row("JJ Bleday", "L", "+410", 80, "💎", ["vs Holmes"], """2 HR, 2 near-HR, 93.4 mph EV and 14.3% barrels. Draws opposing starter Holmes; Great American Ball Park.""", blast="good"),
            row("Matt McLain", "R", "+750", 72, "💎", ["vs Holmes"], """1 HR, 1 near-HR, 89.8 mph EV and 6.7% barrels. Draws opposing starter Holmes; Great American Ball Park."""),
            row("Elly De La Cruz", "S", "+406", 85, "💎", ["vs Holmes"], """2 HR, 2 near-HR, 96.2 mph EV and 20.0% barrels. Draws opposing starter Holmes; Great American Ball Park.""", blast="good"),
        ],
    },
    {
        "title": "SD @ WSH - Lucas Giolito (R, SD) vs Andrew Alvarez (L, WSH)",
        "description": "Nationals Park \u2014 +8% HR row with +6% combined runs, 75\u00b0F clear air, and 7 mph wind. Lucas Giolito suppresses (-1.58 HR risk); Nationals bats get the cleaner attack lane versus Alvarez.",
        "rows": [
            row("Ramon Laureano", "R", "+500", 74, "💎", ["vs Alvarez"], """0 HR, 91.3 mph EV. Draws opposing starter Alvarez; Nationals Park."""),
            row("Manny Machado", "R", "+470", 90, "🚀 🌕 💣", ["vs Alvarez"], """1 HR, 1 near-HR, 100.5 mph EV and 16.7% barrels. Draws opposing starter Alvarez; Nationals Park.""", blast="high"),
            row("Jackson Merrill", "L", "+730", 68, "💎", ["vs Alvarez"], """0 HR, 1 near-HR, 86.9 mph EV and 16.7% barrels. Draws opposing starter Alvarez; Nationals Park."""),
            row("Gavin Sheets", "L", "+710", 83, "⭐ 💎", ["vs Alvarez"], """Worst Pickz favorite with 3 HR, 3 near-HR, 92.3 mph EV and 25.0% barrels. Draws opposing starter Alvarez; Nationals Park.""", blast="good"),
            row("Jacob Young", "R", "+980", 79, "💎", ["vs Giolito"], """3 HR, 3 near-HR, 97.4 mph EV and 28.6% barrels. Draws opposing starter Giolito; Nationals Park.""", blast="good"),
            row("James Wood", "L", "+350", 81, "💎", ["vs Giolito"], """0 HR, 1 near-HR, 96.0 mph EV. Draws opposing starter Giolito; Nationals Park.""", blast="good"),
            row("Luis Garcia Jr.", "L", "+590", 77, "💎", ["vs Giolito"], """1 HR, 2 near-HR, 94.2 mph EV and 20.0% barrels. Draws opposing starter Giolito; Nationals Park."""),
            row("CJ Abrams", "L", "+540", 80, "💎", ["vs Giolito"], """1 HR, 1 near-HR, 93.1 mph EV and 11.1% barrels. Draws opposing starter Giolito; Nationals Park.""", blast="good"),
        ],
    },
    {
        "title": "MIN @ PIT - Taj Bradley (R, MIN) vs Jared Jones (R, PIT)",
        "description": "PNC Park \u2014 -6% HR row with +2% combined runs, 74\u00b0F clear air, and 10 mph out-blowing wind. Jared Jones has no 2026 splits; Brandon Lowe and Spencer Horwitz carry the loudest form on the board.",
        "rows": [
            row("Byron Buxton", "R", "+340", 91, "⭐ 🌕 💣", ["vs Jones"], """Worst Pickz favorite with 2 HR, 2 near-HR, 98.6 mph EV and 22.2% barrels. Draws opposing starter Jones; PNC Park.""", blast="high"),
            row("Ryan Kreidler", "R", "N/A", 65, "💎", ["vs Jones"], """1 HR, 1 near-HR, 91.5 mph EV and 25.0% barrels. Draws opposing starter Jones; PNC Park."""),
            row("Spencer Horwitz", "L", "+730", 86, "🌕 💣", ["vs Bradley"], """3 HR, 3 near-HR, 87.4 mph EV and 30.8% barrels. Draws opposing starter Bradley; PNC Park.""", blast="high"),
            row("Brandon Lowe", "L", "+340", 92, "⭐ 🌕 💣", ["vs Bradley"], """Worst Pickz favorite with 2 HR, 4 near-HR, 97.6 mph EV and 30.8% barrels. Draws opposing starter Bradley; PNC Park.""", blast="high"),
            row("Marcell Ozuna", "R", "+582", 74, "💎", ["vs Bradley"], """1 HR, 1 near-HR, 90.0 mph EV and 18.2% barrels. Draws opposing starter Bradley; PNC Park.""", blast="good"),
        ],
    },
    {
        "title": "TOR @ BAL - Austin Voth (R, TOR) vs Trevor Rogers (L, BAL)",
        "description": "Oriole Park \u2014 +1% HR row with 74\u00b0F clear air and 6 mph L-R crosswind. Trevor Rogers owns a 0.87 vs-RHB HR risk split; Baltimore righties are the premium attack lane.",
        "rows": [
            row("George Springer", "R", "N/A", 76, "⭐ 💎", ["vs Rogers"], """Worst Pickz favorite with 1 HR, 2 near-HR, 94.5 mph EV and 16.7% barrels. Draws opposing starter Rogers; Oriole Park.""", blast="good"),
            row("Kazuma Okamoto", "R", "N/A", 70, "⭐ 💎", ["vs Rogers"], """Worst Pickz favorite with 1 HR, 1 near-HR, 83.4 mph EV and 16.7% barrels. Draws opposing starter Rogers; Oriole Park."""),
            row("Blaze Alexander", "R", "N/A", 78, "💎", ["vs Rogers"], """1 HR, 3 near-HR, 89.0 mph EV and 14.3% barrels. Draws opposing starter Rogers; Oriole Park.""", blast="good"),
            row("Jackson Holliday", "L", "N/A", 72, "💎", ["vs Voth"], """1 HR, 1 near-HR, 96.2 mph EV and 12.5% barrels. Draws opposing starter Voth; Oriole Park.""", blast="good"),
            row("Samuel Bassallo", "L", "N/A", 80, "🚀 💎", ["vs Voth"], """2 HR, 2 near-HR, 100.1 mph EV and 22.2% barrels. Draws opposing starter Voth; Oriole Park.""", blast="good"),
            row("Gunnar Henderson", "L", "N/A", 70, "💎", ["vs Voth"], """0 HR, 89.9 mph EV and 22.2% barrels. Draws opposing starter Voth; Oriole Park."""),
        ],
    },
    {
        "title": "LAA @ TB - Walbert Urena (R, LAA) vs Nick Martinez (R, TB)",
        "description": "Tropicana Field \u2014 closed dome, flat +0% HR row. Nick Martinez suppresses overall (-0.67 HR risk); Angels bats lean on form and Trout BvP history.",
        "rows": [
            row("Zach Neto", "R", "+450", 87, "🌕 💣", ["vs Martinez"], """3 HR, 4 near-HR, 92.5 mph EV and 27.8% barrels. Draws opposing starter Martinez; Tropicana Field.""", blast="high"),
            row("Jo Adell", "R", "+496", 81, "⭐ 💎", ["vs Martinez"], """Worst Pickz favorite with 1 HR, 3 near-HR, 95.5 mph EV and 23.1% barrels. Draws opposing starter Martinez; Tropicana Field.""", blast="good"),
            row("Mike Trout", "R", "+363", 79, "💎 📜", ["vs Martinez"], """1 HR, 1 near-HR, 89.7 mph EV and 12.5% barrels; 25 AB BvP versus Martinez. Draws opposing starter Martinez; Tropicana Field.""", blast="good"),
            row("Yandy Diaz", "R", "+710", 83, "💎", ["vs Urena"], """3 HR, 5 near-HR, 92.1 mph EV and 21.7% barrels. Draws opposing starter Urena; Tropicana Field.""", blast="good"),
            row("Hunter Feduccia", "L", "+1360", 68, "💎", ["vs Urena"], """1 HR, 3 near-HR, 84.8 mph EV and 6.2% barrels. Draws opposing starter Urena; Tropicana Field."""),
            row("Jonathan Aranda", "L", "+578", 82, "⭐ 💎", ["vs Urena"], """Worst Pickz favorite with 1 HR, 5 near-HR, 94.1 mph EV and 26.1% barrels. Draws opposing starter Urena; Tropicana Field.""", blast="good"),
            row("Richie Palacios", "L", "+1300", 66, "💎", ["vs Urena"], """0 HR, 1 near-HR, 89.7 mph EV and 4.2% barrels. Draws opposing starter Urena; Tropicana Field."""),
        ],
    },
    {
        "title": "MIA @ NYM - Max Meyer (R, MIA) vs Freddy Peralta (R, NYM)",
        "description": "Citi Field \u2014 +1% HR but -8% combined runs with 72\u00b0F air, 11 mph out wind, and poor contact environment. Juan Soto's form is slate-elite; Meyer is the Mets' cleaner attack target.",
        "rows": [
            row("Owen Caissie", "L", "+760", 84, "💎", ["vs Peralta"], """1 HR, 1 near-HR, 97.6 mph EV and 33.3% barrels. Draws opposing starter Peralta; Citi Field.""", blast="good"),
            row("Xavier Edwards", "S", "+1300", 62, "💎", ["vs Peralta"], """0 HR, 84.3 mph EV and 5.6% barrels. Draws opposing starter Peralta; Citi Field."""),
            row("Heriberto Hernandez", "R", "N/A", 80, "💎", ["vs Peralta"], """1 HR, 1 near-HR, 96.3 mph EV and 18.2% barrels. Draws opposing starter Peralta; Citi Field.""", blast="good"),
            row("Juan Soto", "L", "+350", 95, "⭐ 🌕 💣", ["vs Meyer"], """Worst Pickz favorite with 6 HR, 7 near-HR, 93.9 mph EV and 33.3% barrels. Draws opposing starter Meyer; Citi Field.""", blast="high"),
            row("AJ Ewing", "L", "+790", 71, "💎", ["vs Meyer"], """0 HR, 89.9 mph EV and 6.7% barrels. Draws opposing starter Meyer; Citi Field."""),
            row("Jared Young", "L", "N/A", 73, "💎", ["vs Meyer"], """0 HR, 1 near-HR, 88.8 mph EV and 33.3% barrels. Draws opposing starter Meyer; Citi Field."""),
        ],
    },
    {
        "title": "BOS @ CLE - Brayan Bello (R, BOS) vs Slade Cecconi (R, CLE)",
        "description": "Progressive Field \u2014 flat +0% HR row with -2% combined runs, 72\u00b0F clear air, and 5 mph wind. Jarren Duran and Rhys Hoskins own the loudest power form on the board.",
        "rows": [
            row("Jarren Duran", "L", "+557", 90, "⭐ 🌕 💣", ["vs Cecconi"], """Worst Pickz favorite with 4 HR, 5 near-HR, 95.8 mph EV and 33.3% barrels. Draws opposing starter Cecconi; Progressive Field.""", blast="high"),
            row("Ceddanne Rafaela", "R", "+830", 68, "💎", ["vs Cecconi"], """0 HR, 90.2 mph EV and 10.0% barrels. Draws opposing starter Cecconi; Progressive Field."""),
            row("Willson Contreras", "R", "+504", 80, "💎", ["vs Cecconi"], """2 HR, 2 near-HR, 87.7 mph EV and 8.7% barrels. Draws opposing starter Cecconi; Progressive Field.""", blast="good"),
            row("Rhys Hoskins", "R", "+507", 88, "🚀 ⭐ 🌕 💣", ["vs Bello"], """Worst Pickz favorite with 2 HR, 3 near-HR, 101.1 mph EV and 37.5% barrels. Draws opposing starter Bello; Progressive Field.""", blast="high"),
            row("Bryan Rocchio", "S", "+1240", 74, "💎", ["vs Bello"], """0 HR, 2 near-HR, 88.7 mph EV and 8.3% barrels. Draws opposing starter Bello; Progressive Field."""),
            row("Jose Ramirez", "S", "+460", 83, "💎", ["vs Bello"], """0 HR, 97.5 mph EV. Draws opposing starter Bello; Progressive Field.""", blast="good"),
        ],
    },
    {
        "title": "CHC @ STL - Shota Imanaga 🧤 (L, CHC) vs Kyle Leahy (R, STL)",
        "description": "Busch Stadium \u2014 slate-harsh -15% HR row with -9% combined runs, 78\u00b0F overcast, and 19% rain risk. Shota Imanaga is a bum arm (1.04 HR risk, 1.68 vs LHB); Cardinals lefties are the clearest attack lane.",
        "rows": [
            row("Ian Happ", "S", "+525", 76, "💎", ["vs Leahy"], """1 HR, 1 near-HR, 87.9 mph EV and 14.3% barrels. Draws opposing starter Leahy; Busch Stadium.""", blast="good"),
            row("Michael Conforto", "L", "N/A", 72, "💎", ["vs Leahy"], """0 HR, 1 near-HR, 89.4 mph EV. Draws opposing starter Leahy; Busch Stadium."""),
            row("Pete Crow-Armstrong", "L", "+525", 79, "💎", ["vs Leahy"], """1 HR, 2 near-HR, 93.7 mph EV and 16.7% barrels. Draws opposing starter Leahy; Busch Stadium.""", blast="good"),
            row("Jordan Walker", "R", "+410", 86, "⭐ 🌕 💣", ["vs Imanaga"], """Worst Pickz favorite with 1 HR, 2 near-HR, 96.3 mph EV and 11.8% barrels. Draws opposing starter Imanaga; Busch Stadium.""", blast="high"),
            row("Nolan Gorman", "L", "N/A", 68, "💎", ["vs Imanaga"], """0 HR, 1 near-HR, 86.6 mph EV and 14.3% barrels. Draws opposing starter Imanaga; Busch Stadium."""),
            row("JJ Wetherholt", "L", "+590", 75, "💎", ["vs Imanaga"], """0 HR, 1 near-HR, 91.6 mph EV and 15.4% barrels. Draws opposing starter Imanaga; Busch Stadium.""", blast="good"),
        ],
    },
    {
        "title": "DET @ CWS - Troy Melton (R, DET) vs Erick Fedde 🧤 (R, CWS)",
        "description": "Rate Field \u2014 -2% HR row with -4% combined runs, cool 66\u00b0F air, and 7 mph wind. Erick Fedde is the slate's top HR-risk arm (1.67, 1.94 vs RHB); Tigers bats are the premium attack lane versus Fedde.",
        "rows": [
            row("Riley Greene", "L", "+410", 84, "💎 📜", ["vs Fedde"], """0 HR, 97.9 mph EV and 10.0% barrels; 7 AB BvP versus Fedde. Draws opposing starter Fedde; Rate Field.""", blast="good"),
            row("Spencer Torkelson", "R", "+500", 72, "💎", ["vs Fedde"], """0 HR, 1 near-HR, 88.4 mph EV and 12.5% barrels. Draws opposing starter Fedde; Rate Field."""),
            row("Gage Workman", "L", "+448", 78, "💎", ["vs Fedde"], """1 HR, 2 near-HR, 95.6 mph EV and 37.5% barrels. Draws opposing starter Fedde; Rate Field.""", blast="good"),
            row("Munetaka Murakami", "L", "+250", 91, "🚀 ⭐ 🌕 💣", ["vs Melton"], """Worst Pickz favorite with 2 HR, 2 near-HR, 101.1 mph EV and 25.0% barrels. Draws opposing starter Melton; Rate Field.""", blast="high"),
            row("Miguel Vargas", "R", "+470", 82, "⭐ 💎", ["vs Melton"], """Worst Pickz favorite with 0 HR, 1 near-HR, 94.1 mph EV and 9.1% barrels. Draws opposing starter Melton; Rate Field.""", blast="good"),
            row("Colson Montgomery", "L", "+290", 70, "💎", ["vs Melton"], """0 HR, 82.1 mph EV. Draws opposing starter Melton; Rate Field."""),
        ],
    },
    {
        "title": "KC @ TEX - Stephen Kolek (R, KC) vs MacKenzie Gore (L, TEX)",
        "description": "Globe Life Field \u2014 -11% HR row with roof closed and 87\u00b0F dome air. MacKenzie Gore suppresses; Texas lefties Joc Pederson and Brandon Nimmo get the cleaner form read.",
        "rows": [
            row("Salvador Perez", "R", "+516", 78, "⭐ 💎", ["vs Gore"], """Worst Pickz favorite with 1 HR, 1 near-HR, 90.7 mph EV and 11.1% barrels. Draws opposing starter Gore; Globe Life Field.""", blast="good"),
            row("Bobby Witt Jr.", "R", "+408", 80, "💎", ["vs Gore"], """1 HR, 1 near-HR, 95.6 mph EV and 14.3% barrels. Draws opposing starter Gore; Globe Life Field.""", blast="good"),
            row("Joc Pederson", "L", "+440", 77, "💎", ["vs Kolek"], """2 HR, 2 near-HR, 88.7 mph EV and 10.5% barrels. Draws opposing starter Kolek; Globe Life Field.""", blast="good"),
            row("Brandon Nimmo", "L", "+431", 81, "💎", ["vs Kolek"], """1 HR, 3 near-HR, 91.0 mph EV and 20.0% barrels. Draws opposing starter Kolek; Globe Life Field.""", blast="good"),
        ],
    },
    {
        "title": "MIL @ HOU - Coleman Crow (R, MIL) vs Kai-Wei Teng (R, HOU)",
        "description": "Daikin Park \u2014 roof closed, -4% combined runs despite 87\u00b0F air. Coleman Crow suppresses (-1.04 HR risk); Houston bats get the cleaner attack lane versus Crow.",
        "rows": [
            row("Jackson Chourio", "R", "+490", 83, "⭐ 💎", ["vs Teng"], """Worst Pickz favorite with 0 HR, 1 near-HR, 99.7 mph EV and 35.7% barrels. Draws opposing starter Teng; Daikin Park.""", blast="good"),
            row("Christian Yelich", "L", "+590", 76, "💎", ["vs Teng"], """1 HR, 1 near-HR, 92.0 mph EV and 10.0% barrels. Draws opposing starter Teng; Daikin Park.""", blast="good"),
            row("Jake Bauers", "L", "+440", 79, "💎", ["vs Teng"], """0 HR, 94.3 mph EV and 28.6% barrels. Draws opposing starter Teng; Daikin Park.""", blast="good"),
            row("Garrett Mitchell", "L", "+790", 82, "💎", ["vs Teng"], """1 HR, 3 near-HR, 99.0 mph EV and 27.3% barrels. Draws opposing starter Teng; Daikin Park.""", blast="good"),
            row("Isaac Paredes", "R", "+500", 80, "💎", ["vs Crow"], """2 HR, 2 near-HR, 88.6 mph EV and 16.7% barrels. Draws opposing starter Crow; Daikin Park.""", blast="good"),
            row("Christian Walker", "R", "+410", 77, "💎", ["vs Crow"], """1 HR, 1 near-HR, 87.1 mph EV and 7.1% barrels. Draws opposing starter Crow; Daikin Park.""", blast="good"),
            row("Yordan Alvarez", "L", "+300", 85, "🌕 💣", ["vs Crow"], """0 HR, 1 near-HR, 98.1 mph EV. Draws opposing starter Crow; Daikin Park.""", blast="high"),
        ],
    },
    {
        "title": "SF @ COL - Logan Webb (R, SF) vs Michael Lorenzen 🧤 (R, COL)",
        "description": "Coors Field \u2014 slate-best +14% HR and +30% combined runs with 77\u00b0F air and 6 mph wind. Michael Lorenzen is a bum arm (1.24 HR risk, 2.29 vs LHB); Rockies bats are live despite Webb on the mound.",
        "rows": [
            row("Tj Rumfield", "L", "+880", 74, "💎", ["vs Webb"], """1 HR, 3 near-HR, 82.5 mph EV and 11.1% barrels. Draws opposing starter Webb; Coors Field.""", blast="good"),
            row("Hunter Goodman", "R", "+410", 78, "💎", ["vs Webb"], """1 HR, 1 near-HR, 89.8 mph EV and 11.1% barrels. Draws opposing starter Webb; Coors Field.""", blast="good"),
        ],
    },
    {
        "title": "NYY @ ATH - Carlos Rodon (L, NYY) vs Luis Severino (R, ATH)",
        "description": "Sutter Health Park \u2014 +9% HR row with +9% combined runs, 72\u00b0F clear air, and 6 mph wind. Luis Severino is attackable; A's bats get the plus carry environment.",
        "rows": [
            row("Ben Rice", "L", "+328", 88, "⭐ 🌕 💣", ["vs Severino"], """Worst Pickz favorite with 1 HR, 1 near-HR, 90.0 mph EV. Draws opposing starter Severino; Sutter Health Park.""", blast="good"),
            row("Aaron Judge", "R", "+235", 84, "🌕 💣 📜", ["vs Severino"], """1 HR, 2 near-HR, 97.0 mph EV and 15.4% barrels; 20 AB BvP versus Severino. Draws opposing starter Severino; Sutter Health Park.""", blast="high"),
            row("Ryan McMahon", "L", "N/A", 76, "💎", ["vs Severino"], """2 HR, 2 near-HR, 88.3 mph EV and 18.2% barrels. Draws opposing starter Severino; Sutter Health Park.""", blast="good"),
            row("Shea Langeliers", "R", "+392", 74, "💎", ["vs Rodon"], """0 HR, 87.2 mph EV and 12.5% barrels. Draws opposing starter Rodon; Sutter Health Park."""),
            row("Zack Gelof", "R", "+750", 79, "💎", ["vs Rodon"], """1 HR, 1 near-HR, 93.8 mph EV and 16.7% barrels. Draws opposing starter Rodon; Sutter Health Park.""", blast="good"),
            row("Colby Thomas", "R", "+610", 72, "💎", ["vs Rodon"], """0 HR, 2 near-HR, 87.0 mph EV and 15.4% barrels. Draws opposing starter Rodon; Sutter Health Park."""),
            row("Nick Kurtz", "L", "+500", 83, "💎", ["vs Rodon"], """1 HR, 1 near-HR, 97.9 mph EV and 20.0% barrels. Draws opposing starter Rodon; Sutter Health Park.""", blast="good"),
        ],
    },
    {
        "title": "ARI @ SEA - Zac Gallen (R, ARI) vs George Kirby (R, SEA)",
        "description": "T-Mobile Park \u2014 slate-worst -12% HR and -14% combined runs with 58\u00b0F overcast dome air. George Kirby suppresses; Seattle bats face Gallen in the harshest HR environment.",
        "rows": [
            row("Ketel Marte", "S", "+520", 86, "⭐ 💎", ["vs Kirby"], """Worst Pickz favorite with 2 HR, 2 near-HR, 78.4 mph EV and 13.3% barrels. Draws opposing starter Kirby; T-Mobile Park.""", blast="good"),
            row("Corbin Carroll", "L", "+550", 84, "⭐ 💎", ["vs Kirby"], """Worst Pickz favorite with 1 HR, 2 near-HR, 94.0 mph EV and 16.7% barrels. Draws opposing starter Kirby; T-Mobile Park.""", blast="good"),
            row("Nolan Arenado", "R", "N/A", 62, "💎", ["vs Kirby"], """0 HR, 1 near-HR, 89.0 mph EV. Draws opposing starter Kirby; T-Mobile Park."""),
            row("Gabriel Moreno", "R", "+990", 75, "💎", ["vs Kirby"], """1 HR, 1 near-HR, 92.2 mph EV and 8.3% barrels. Draws opposing starter Kirby; T-Mobile Park."""),
            row("Mitch Garver", "R", "+650", 82, "💎", ["vs Gallen"], """2 HR, 2 near-HR, 98.9 mph EV and 11.1% barrels. Draws opposing starter Gallen; T-Mobile Park.""", blast="good"),
            row("Dominic Canzone", "L", "+583", 78, "💎", ["vs Gallen"], """1 HR, 1 near-HR, 93.3 mph EV and 16.7% barrels. Draws opposing starter Gallen; T-Mobile Park.""", blast="good"),
            row("Colt Emerson", "L", "+920", 74, "💎", ["vs Gallen"], """1 HR, 1 near-HR, 90.4 mph EV. Draws opposing starter Gallen; T-Mobile Park."""),
            row("Luke Raley", "L", "+423", 68, "💎", ["vs Gallen"], """0 HR, 85.0 mph EV. Draws opposing starter Gallen; T-Mobile Park."""),
            row("Patrick Wisdom", "R", "N/A", 70, "💎", ["vs Gallen"], """0 HR, 98.8 mph EV and 33.3% barrels. Draws opposing starter Gallen; T-Mobile Park."""),
        ],
    },
    {
        "title": "PHI @ LAD - Zack Wheeler (R, PHI) vs Justin Wrobleski (L, LAD)",
        "description": "Dodger Stadium \u2014 +6% HR row with 63\u00b0F clear air and consistent 11 mph out-blowing wind. Zack Wheeler suppresses (-0.68 HR risk); Dodgers lefties are the premium attack lane versus Wrobleski.",
        "rows": [
            row("Kyle Schwarber", "L", "+290", 92, "⭐ 🌕 💣", ["vs Wrobleski"], """Worst Pickz favorite with 3 HR, 3 near-HR, 95.1 mph EV and 30.0% barrels. Draws opposing starter Wrobleski; Dodger Stadium.""", blast="high"),
            row("Bryce Harper", "L", "+500", 80, "⭐ 💎", ["vs Wrobleski"], """Worst Pickz favorite with 0 HR, 2 near-HR, 95.4 mph EV and 22.2% barrels. Draws opposing starter Wrobleski; Dodger Stadium.""", blast="good"),
            row("Alec Bohm", "R", "+650", 79, "💎", ["vs Wrobleski"], """2 HR, 2 near-HR, 91.8 mph EV and 11.1% barrels. Draws opposing starter Wrobleski; Dodger Stadium.""", blast="good"),
            row("Will Smith", "R", "+578", 87, "⭐ 🌕 💣 📜", ["vs Wheeler"], """Worst Pickz favorite with 2 HR, 4 near-HR, 96.2 mph EV and 33.3% barrels; 8 AB BvP versus Wheeler. Draws opposing starter Wheeler; Dodger Stadium.""", blast="high"),
            row("Freddie Freeman", "L", "+550", 89, "⭐ 🌕 💣 📜", ["vs Wheeler"], """Worst Pickz favorite with 3 HR, 3 near-HR, 91.2 mph EV and 33.3% barrels; 54 AB BvP versus Wheeler with career HR history. Draws opposing starter Wheeler; Dodger Stadium.""", blast="high"),
            row("Shohei Ohtani", "L", "+310", 90, "⭐ 🌕 💣", ["vs Wheeler"], """Worst Pickz favorite with 2 HR, 2 near-HR, 96.6 mph EV and 30.0% barrels. Draws opposing starter Wheeler; Dodger Stadium.""", blast="high"),
            row("Andy Pages", "R", "+582", 72, "💎", ["vs Wheeler"], """0 HR, 1 near-HR, 89.7 mph EV and 7.7% barrels. Draws opposing starter Wheeler; Dodger Stadium."""),
        ],
    },
]

PROP_NAMES = {name.split(" (")[0] for name in PLAYER_TEAMS}
found = {r["name"].split(" (")[0] for g in games for r in g["rows"]}
missing = sorted(PROP_NAMES - found)
if missing:
    raise SystemExit(f"Missing props: {missing}")

for game in games:
    for entry in game["rows"]:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)


def js_string(value):
    return json.dumps(value, ensure_ascii=False)


def emit_games_js(games_data):
    lines = ["const games = ["]
    for game in games_data:
        lines.append("    {")
        lines.append(f"        title: {js_string(game['title'])},")
        lines.append(f"        description: {js_string(game['description'])},")
        lines.append("        rows: [")
        for entry in game["rows"]:
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


if __name__ == "__main__":
    out = ROOT / "_games-0529.txt"
    out.write_text(emit_games_js(games) + "\n", encoding="utf-8")
    print(f"wrote {out.name}")
