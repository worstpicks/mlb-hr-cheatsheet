#!/usr/bin/env python3
"""One-shot generator for build-sheet-2026-05-29.py"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "build-sheet-2026-05-29.py"

FAVS = [
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
]

ROCKET = {"Manny Machado", "Rhys Hoskins", "Jordan Walker", "Munetaka Murakami"}

BVP = {
    "Mike Yastrzemski": "25 AB BvP versus Paddack",
    "Matt Olson": "9 AB BvP versus Paddack",
    "Freddie Freeman": "54 AB BvP versus Wheeler with career HR history",
    "Aaron Judge": "20 AB BvP versus Severino",
    "Mike Trout": "25 AB BvP versus Martinez",
    "Riley Greene": "7 AB BvP versus Fedde",
    "Will Smith": "8 AB BvP versus Wheeler",
}

# name, hand, odds, score, chip, hr, near, ev, barrel, angle, blast
PROPS = [
    # ATL @ CIN
    ("Michael Harris II", "L", "+311", 88, "Paddack", 3, 4, 90.1, 18.8, "Mikolas-style lefty power lane at GABP +9% HR", "high"),
    ("Austin Riley", "R", "+360", 86, "Paddack", 2, 2, 95.6, 14.3, "righty pull-air versus Paddack RHB split", "high"),
    ("Mike Yastrzemski", "L", "+550", 84, "Paddack", 2, 3, 90.8, 8.3, "lefty lane at Great American with BvP sample", "good"),
    ("Matt Olson", "L", "+270", 78, "Paddack", 0, 0, 96.1, 0, "Olson BvP history helps at the small park", "good"),
    ("Ronald Acuna Jr.", "R", "+375", 82, "Paddack", 1, 2, 94.4, 18.2, "Acuna pull-side versus Paddack", "good"),
    ("JJ Bleday", "L", "+410", 80, "Holmes", 2, 2, 93.4, 14.3, "Holmes is slate-high HR risk (1.21)", "good"),
    ("Matt McLain", "R", "+750", 72, "Holmes", 1, 1, 89.8, 6.7, "Holmes RHB split is the cleaner Reds lane", None),
    ("Elly De La Cruz", "S", "+406", 85, "Holmes", 2, 2, 96.2, 20.0, "Holmes RHB leakage fits Elly switch power", "good"),
    # SD @ WSH
    ("Ramon Laureano", "R", "+500", 74, "Alvarez", 0, 0, 91.3, 0, "Alvarez limits damage but Laureano EV is live", None),
    ("Manny Machado", "R", "+470", 90, "Alvarez", 1, 1, 100.5, 16.7, "100.5 mph EV versus Alvarez at Nationals Park +8% HR", "high"),
    ("Jackson Merrill", "L", "+730", 68, "Alvarez", 0, 1, 86.9, 16.7, "lefty lane versus Alvarez in a plus HR row", None),
    ("Gavin Sheets", "L", "+710", 83, "Alvarez", 3, 3, 92.3, 25.0, "Worst Pickz favorite with 3 HR and 50.0% pull-air", "good"),
    ("Jacob Young", "R", "+980", 79, "Giolito", 3, 3, 97.4, 28.6, "Giolito suppresses but Young's tiny sample is loud", "good"),
    ("James Wood", "L", "+350", 81, "Giolito", 0, 1, 96.0, 0, "Wood ceiling bat versus Giolito LHB sample", "good"),
    ("Luis Garcia Jr.", "L", "+590", 77, "Giolito", 1, 2, 94.2, 20.0, "lefty contact quality fits Giolito", None),
    ("CJ Abrams", "L", "+540", 80, "Giolito", 1, 1, 93.1, 11.1, "Abrams pull-side versus Giolito", "good"),
    # MIN @ PIT
    ("Byron Buxton", "R", "+340", 91, "Jones", 2, 2, 98.6, 22.2, "Worst Pickz favorite with 2 HR and 98.6 mph EV", "high"),
    ("Ryan Kreidler", "R", "N/A", 65, "Jones", 1, 1, 91.5, 25.0, "1 HR in sample but no listed odds posted", None),
    ("Spencer Horwitz", "L", "+730", 86, "Bradley", 3, 3, 87.4, 30.8, "3 HR, 3 near-HR with 46.2% pull-air versus Bradley", "high"),
    ("Brandon Lowe", "L", "+340", 92, "Bradley", 2, 4, 97.6, 30.8, "Worst Pickz favorite with 2 HR and 97.6 mph EV", "high"),
    ("Marcell Ozuna", "R", "+582", 74, "Bradley", 1, 1, 90.0, 18.2, "Bradley RHB split is Ozuna's lane at PNC", "good"),
    # TOR @ BAL
    ("George Springer", "R", "N/A", 76, "Rogers", 1, 2, 94.5, 16.7, "Worst Pickz favorite with Rogers RHB split", "good"),
    ("Kazuma Okamoto", "R", "N/A", 70, "Rogers", 1, 1, 83.4, 16.7, "Worst Pickz favorite in thin sample versus Rogers", None),
    ("Blaze Alexander", "R", "N/A", 78, "Rogers", 1, 3, 89.0, 14.3, "1 HR, 3 near-HR with 57.1% hard-hit versus Rogers", "good"),
    ("Jackson Holliday", "L", "N/A", 72, "Voth", 1, 1, 96.2, 12.5, "Voth sample is tiny; Holliday EV keeps him listed", "good"),
    ("Samuel Bassallo", "L", "N/A", 80, "Voth", 2, 2, 100.1, 22.2, "2 HR in sample versus Voth at Camden +1% HR", "good"),
    ("Gunnar Henderson", "L", "N/A", 70, "Voth", 0, 0, 89.9, 22.2, "Voth RHB lane with Henderson pull-air", None),
    # LAA @ TB
    ("Zach Neto", "R", "+450", 87, "Martinez", 3, 4, 92.5, 27.8, "3 HR, 4 near-HR with 44.4% barrels versus Martinez", "high"),
    ("Jo Adell", "R", "+496", 81, "Martinez", 1, 3, 95.5, 23.1, "Worst Pickz favorite with 30.8% barrels versus Martinez", "good"),
    ("Mike Trout", "R", "+363", 79, "Martinez", 1, 1, 89.7, 12.5, "Trout BvP history versus Martinez at the dome", "good"),
    ("Yandy Diaz", "R", "+710", 83, "Urena", 2, 3, 91.3, 26.7, "2 HR, 3 near-HR with pull-side lift versus Urena", "good"),
    ("Hunter Feduccia", "L", "+1360", 68, "Urena", 1, 3, 89.5, 11.1, "longshot with 3 near-HR in small sample", None),
    ("Jonathan Aranda", "L", "+578", 82, "Urena", 0, 2, 98.9, 22.2, "Worst Pickz favorite with 77.8% hard-hit versus Urena", "good"),
    ("Richie Palacios", "L", "+1300", 66, "Urena", 0, 1, 91.3, 8.3, "Palacios pull-air versus Urena LHB lane", None),
    # MIA @ NYM
    ("Owen Caissie", "L", "+760", 84, "Peralta", 1, 1, 97.6, 33.3, "1 HR with 97.6 mph EV and 83.3% hard-hit", "good"),
    ("Xavier Edwards", "S", "+1300", 62, "Peralta", 0, 0, 84.3, 5.6, "switch bat versus Peralta in Citi drag", None),
    ("Heriberto Hernandez", "R", "N/A", 80, "Peralta", 1, 1, 96.3, 18.2, "1 HR with 72.7% hard-hit versus Peralta", "good"),
    ("Juan Soto", "L", "+350", 95, "Meyer", 6, 7, 99.2, 43.8, "Worst Pickz favorite with 6 HR and slate-best form", "high"),
    ("AJ Ewing", "L", "+790", 71, "Meyer", 0, 0, 90.8, 9.1, "Meyer RHB split supports Mets lefty lift", None),
    ("Jared Young", "L", "N/A", 73, "Meyer", 0, 1, 88.8, 33.3, "1 near-HR with 44.4% hard-hit versus Meyer", None),
    # BOS @ CLE
    ("Jarren Duran", "L", "+557", 90, "Cecconi", 4, 5, 95.8, 33.3, "Worst Pickz favorite with 4 HR and 95.8 mph EV", "high"),
    ("Ceddanne Rafaela", "R", "+830", 68, "Cecconi", 0, 0, 90.2, 10.0, "Cecconi RHB split is Rafaela's lane", None),
    ("Willson Contreras", "R", "+504", 80, "Cecconi", 2, 2, 87.7, 8.7, "2 HR with pull-side air versus Cecconi", "good"),
    ("Rhys Hoskins", "R", "+507", 88, "Bello", 2, 3, 101.1, 37.5, "Worst Pickz favorite with 101.1 mph EV and 62.5% pull-air", "high"),
    ("Bryan Rocchio", "S", "+1240", 74, "Bello", 0, 2, 88.7, 8.3, "2 near-HR with 58.3% hard-hit versus Bello", None),
    ("Jose Ramirez", "S", "+460", 83, "Bello", 0, 0, 97.5, 0, "Ramirez switch bat versus Bello RHB split", "good"),
    # CHC @ STL
    ("Ian Happ", "S", "+525", 76, "Leahy", 1, 1, 87.9, 14.3, "Happ BvP history versus Leahy at Busch -15% HR", "good"),
    ("Michael Conforto", "L", "N/A", 72, "Leahy", 0, 1, 89.4, 0, "1 near-HR with 50.0% pull-air versus Leahy", None),
    ("Pete Crow-Armstrong", "L", "+525", 79, "Leahy", 1, 2, 93.7, 16.7, "1 HR, 2 near-HR with 41.7% pull-air", "good"),
    ("Jordan Walker", "R", "+410", 86, "Imanaga", 1, 2, 101.8, 25.0, "Worst Pickz favorite with 101.8 mph EV versus Imanaga LHB risk", "high"),
    ("Nolan Gorman", "L", "N/A", 68, "Imanaga", 0, 1, 86.6, 14.3, "Imanaga is slate bum (1.04 HR risk, 1.69 vs LHB)", None),
    ("JJ Wetherholt", "L", "+590", 75, "Imanaga", 0, 1, 97.5, 16.7, "Imanaga LHB leakage supports Wetherholt lift", "good"),
    # DET @ CWS
    ("Riley Greene", "L", "+410", 84, "Fedde", 0, 0, 97.9, 10.0, "Greene BvP versus Fedde plus 97.9 mph EV", "good"),
    ("Spencer Torkelson", "R", "+500", 72, "Fedde", 0, 1, 88.4, 12.5, "Fedde RHB HR risk (1.94) is the Tigers righty lane", None),
    ("Gage Workman", "L", "+448", 78, "Fedde", 1, 2, 95.6, 37.5, "1 HR, 2 near-HR with 37.5% pull-air versus Fedde", "good"),
    ("Munetaka Murakami", "L", "+250", 91, "Melton", 2, 2, 101.1, 25.0, "Worst Pickz favorite with 101.1 mph EV and 2 HR", "high"),
    ("Miguel Vargas", "R", "+470", 82, "Melton", 0, 1, 94.1, 9.1, "Worst Pickz favorite with 94.1 mph EV versus Melton", "good"),
    ("Colson Montgomery", "L", "+290", 70, "Melton", 0, 0, 82.1, 0, "Montgomery lefty lane versus Melton small sample", None),
    # KC @ TEX
    ("Salvador Perez", "R", "+516", 78, "Gore", 1, 1, 90.7, 11.1, "Worst Pickz favorite with Gore LHB sample at the dome", "good"),
    ("Bobby Witt Jr.", "R", "+408", 80, "Gore", 1, 1, 95.6, 14.3, "Witt pull-side versus Gore at Globe Life", "good"),
    ("Joc Pederson", "L", "+440", 77, "Kolek", 2, 2, 88.7, 10.5, "2 HR with 26.3% pull-air versus Kolek", "good"),
    ("Brandon Nimmo", "L", "+431", 81, "Kolek", 1, 3, 91.0, 20.0, "1 HR, 3 near-HR with 46.7% hard-hit versus Kolek", "good"),
    # MIL @ HOU
    ("Jackson Chourio", "R", "+490", 83, "Teng", 0, 1, 99.7, 35.7, "Worst Pickz favorite with 99.7 mph EV and 64.3% hard-hit", "good"),
    ("Christian Yelich", "L", "+590", 76, "Teng", 1, 1, 92.0, 10.0, "Yelich lefty lane versus Teng at Daikin Park", "good"),
    ("Jake Bauers", "L", "+440", 79, "Teng", 0, 0, 94.3, 28.6, "94.3 mph EV with 71.4% hard-hit versus Teng", "good"),
    ("Garrett Mitchell", "L", "+790", 82, "Teng", 1, 3, 99.0, 27.3, "1 HR, 3 near-HR with 99.0 mph EV versus Teng", "good"),
    ("Isaac Paredes", "R", "+500", 80, "Crow", 2, 2, 88.6, 16.7, "2 HR with pull-side damage versus Crow", "good"),
    ("Christian Walker", "R", "+410", 77, "Crow", 1, 1, 87.1, 7.1, "Walker righty lane versus Crow RHB split", "good"),
    ("Yordan Alvarez", "L", "+300", 85, "Crow", 0, 1, 98.1, 0, "Alvarez lefty power versus Crow at the dome", "high"),
    # SF @ COL
    ("Tj Rumfield", "L", "+880", 74, "Lorenzen", 1, 3, 82.5, 11.1, "Coors +14% HR plus Lorenzen bum (1.24 HR risk)", "good"),
    ("Hunter Goodman", "R", "+410", 78, "Lorenzen", 1, 1, 89.8, 11.1, "Lorenzen RHB split at Coors +30% runs", "good"),
    # NYY @ ATH
    ("Ben Rice", "L", "+328", 88, "Severino", 1, 1, 90.0, 0, "Worst Pickz favorite with pull-side fit versus Severino", "good"),
    ("Aaron Judge", "R", "+235", 84, "Severino", 1, 2, 97.0, 15.4, "Judge BvP history versus Severino at Sutter +9% HR", "high"),
    ("Ryan McMahon", "L", "N/A", 76, "Severino", 2, 2, 88.3, 18.2, "2 HR with 36.4% hard-hit versus Severino", "good"),
    ("Shea Langeliers", "R", "+392", 74, "Rodon", 0, 0, 87.2, 12.5, "Rodon suppresses but Langeliers EV is live", None),
    ("Zack Gelof", "R", "+750", 79, "Rodon", 1, 1, 93.8, 16.7, "1 HR with 66.7% hard-hit versus Rodon", "good"),
    ("Colby Thomas", "R", "+610", 72, "Rodon", 0, 2, 87.0, 15.4, "2 near-HR with 38.5% hard-hit versus Rodon", None),
    ("Nick Kurtz", "L", "+500", 83, "Rodon", 1, 1, 97.9, 20.0, "1 HR with 97.9 mph EV and 60.0% hard-hit", "good"),
    # ARI @ SEA
    ("Ketel Marte", "S", "+520", 86, "Kirby", 2, 2, 78.4, 13.3, "Worst Pickz favorite with 2 HR versus Kirby", "good"),
    ("Corbin Carroll", "L", "+550", 84, "Kirby", 1, 2, 94.0, 16.7, "Worst Pickz favorite with 94.0 mph EV versus Kirby", "good"),
    ("Nolan Arenado", "R", "N/A", 62, "Kirby", 0, 1, 89.0, 0, "1 near-HR versus Kirby in T-Mobile -14% drag", None),
    ("Gabriel Moreno", "R", "+990", 75, "Kirby", 1, 1, 92.2, 8.3, "1 HR with 50.0% hard-hit versus Kirby", None),
    ("Mitch Garver", "R", "+650", 82, "Gallen", 2, 2, 98.9, 11.1, "2 HR with 98.9 mph EV and 55.6% pull-air", "good"),
    ("Dominic Canzone", "L", "+583", 78, "Gallen", 1, 1, 93.3, 16.7, "1 HR with 58.3% hard-hit versus Gallen", "good"),
    ("Colt Emerson", "L", "+920", 74, "Gallen", 1, 1, 90.4, 0, "1 HR with 42.9% pull-air versus Gallen", None),
    ("Luke Raley", "L", "+423", 68, "Gallen", 0, 0, 85.0, 0, "Raley lefty lane versus Gallen in harsh T-Mobile row", None),
    ("Patrick Wisdom", "R", "N/A", 70, "Gallen", 0, 0, 98.8, 33.3, "98.8 mph EV and 66.7% hard-hit in tiny sample", None),
    # PHI @ LAD
    ("Kyle Schwarber", "L", "+290", 92, "Wrobleski", 3, 3, 95.1, 30.0, "Worst Pickz favorite with 3 HR and 60.0% pull-air", "high"),
    ("Bryce Harper", "L", "+500", 80, "Wrobleski", 0, 2, 95.4, 22.2, "Worst Pickz favorite with 95.4 mph EV versus Wrobleski", "good"),
    ("Alec Bohm", "R", "+650", 79, "Wrobleski", 2, 2, 91.8, 11.1, "2 HR with 91.8 mph EV versus Wrobleski RHB lane", "good"),
    ("Will Smith", "R", "+578", 87, "Wheeler", 2, 4, 96.2, 33.3, "Worst Pickz favorite with 2 HR and BvP versus Wheeler", "high"),
    ("Freddie Freeman", "L", "+550", 89, "Wheeler", 3, 3, 91.2, 33.3, "Worst Pickz favorite with 3 HR and Freeman BvP history", "high"),
    ("Shohei Ohtani", "L", "+310", 90, "Wheeler", 2, 2, 96.6, 30.0, "Worst Pickz favorite with 2 HR and 96.6 mph EV", "high"),
    ("Andy Pages", "R", "+582", 72, "Wheeler", 0, 1, 89.7, 7.7, "Pages righty lane versus Wheeler at Dodger Stadium +6% HR", None),
]

GAME_META = [
    {
        "key": "ATL @ CIN",
        "title": "ATL @ CIN - Grant Holmes 🧤 (R, ATL) vs Chris Paddack (R, CIN)",
        "desc": "Great American Ball Park — Ballpark Pal grades +9% HR and +13% combined runs with 75°F partially cloudy air and 2 mph wind. Grant Holmes carries 1.21 HR risk; Chris Paddack is attackable to both splits at the smallest outfield in MLB.",
        "away": "ATL",
        "home": "CIN",
        "away_sp": "Holmes",
        "home_sp": "Paddack",
    },
    {
        "key": "SD @ WSH",
        "title": "SD @ WSH - Lucas Giolito (R, SD) vs Andrew Alvarez (L, WSH)",
        "desc": "Nationals Park — +8% HR row with +6% combined runs, 75°F clear air, and 7 mph wind. Lucas Giolito suppresses (-1.62 HR risk); Nationals bats get the cleaner attack lane versus Alvarez.",
        "away": "SD",
        "home": "WSH",
        "away_sp": "Giolito",
        "home_sp": "Alvarez",
    },
    {
        "key": "MIN @ PIT",
        "title": "MIN @ PIT - Taj Bradley (R, MIN) vs Jared Jones (R, PIT)",
        "desc": "PNC Park — -6% HR row with +2% combined runs, 74°F clear air, and 10 mph out-blowing wind. Jared Jones has no 2026 splits; Brandon Lowe and Spencer Horwitz carry the loudest form on the board.",
        "away": "MIN",
        "home": "PIT",
        "away_sp": "Bradley",
        "home_sp": "Jones",
    },
    {
        "key": "TOR @ BAL",
        "title": "TOR @ BAL - Austin Voth (R, TOR) vs Trevor Rogers (L, BAL)",
        "desc": "Oriole Park — +1% HR row with 74°F clear air and 6 mph L-R crosswind. Trevor Rogers owns a 0.84 vs-RHB HR risk split; Baltimore righties are the premium attack lane.",
        "away": "TOR",
        "home": "BAL",
        "away_sp": "Voth",
        "home_sp": "Rogers",
    },
    {
        "key": "LAA @ TB",
        "title": "LAA @ TB - Walbert Urena (R, LAA) vs Nick Martinez (R, TB)",
        "desc": "Tropicana Field — closed dome, flat +0% HR row. Nick Martinez suppresses overall (-0.70 HR risk); Angels bats lean on form and Trout BvP history.",
        "away": "LAA",
        "home": "TB",
        "away_sp": "Urena",
        "home_sp": "Martinez",
    },
    {
        "key": "MIA @ NYM",
        "title": "MIA @ NYM - Max Meyer (R, MIA) vs Freddy Peralta (R, NYM)",
        "desc": "Citi Field — +1% HR but -8% combined runs with 72°F air, 11 mph out wind, and poor contact environment. Juan Soto's form is slate-elite; Meyer is the Mets' cleaner attack target.",
        "away": "MIA",
        "home": "NYM",
        "away_sp": "Meyer",
        "home_sp": "Peralta",
    },
    {
        "key": "BOS @ CLE",
        "title": "BOS @ CLE - Brayan Bello (R, BOS) vs Slade Cecconi (R, CLE)",
        "desc": "Progressive Field — flat +0% HR row with -2% combined runs, 72°F clear air, and 5 mph wind. Jarren Duran and Rhys Hoskins own the loudest power form on the board.",
        "away": "BOS",
        "home": "CLE",
        "away_sp": "Bello",
        "home_sp": "Cecconi",
    },
    {
        "key": "CHC @ STL",
        "title": "CHC @ STL - Shota Imanaga 🧤 (L, CHC) vs Kyle Leahy (R, STL)",
        "desc": "Busch Stadium — slate-harsh -15% HR row with -9% combined runs, 78°F overcast, and 19% rain risk. Shota Imanaga is a bum arm (1.04 HR risk, 1.69 vs LHB); Cardinals lefties are the clearest attack lane.",
        "away": "CHC",
        "home": "STL",
        "away_sp": "Imanaga",
        "home_sp": "Leahy",
    },
    {
        "key": "DET @ CWS",
        "title": "DET @ CWS - Troy Melton (R, DET) vs Erick Fedde 🧤 (R, CWS)",
        "desc": "Rate Field — -2% HR row with -4% combined runs, cool 66°F air, and 7 mph wind. Erick Fedde is the slate's top HR-risk arm (1.69, 1.94 vs RHB); White Sox bats are the premium attack targets.",
        "away": "DET",
        "home": "CWS",
        "away_sp": "Melton",
        "home_sp": "Fedde",
    },
    {
        "key": "KC @ TEX",
        "title": "KC @ TEX - Stephen Kolek (R, KC) vs MacKenzie Gore (L, TEX)",
        "desc": "Globe Life Field — -11% HR row with roof closed and 87°F dome air. MacKenzie Gore suppresses; Texas lefties Joc Pederson and Brandon Nimmo get the cleaner form read.",
        "away": "KC",
        "home": "TEX",
        "away_sp": "Kolek",
        "home_sp": "Gore",
    },
    {
        "key": "MIL @ HOU",
        "title": "MIL @ HOU - Coleman Crow (R, MIL) vs Kai-Wei Teng (R, HOU)",
        "desc": "Daikin Park — roof closed, -4% combined runs despite 87°F air. Coleman Crow suppresses (-1.09 HR risk); Houston bats get the cleaner attack lane versus Crow.",
        "away": "MIL",
        "home": "HOU",
        "away_sp": "Crow",
        "home_sp": "Teng",
    },
    {
        "key": "SF @ COL",
        "title": "SF @ COL - Logan Webb (R, SF) vs Michael Lorenzen 🧤 (R, COL)",
        "desc": "Coors Field — slate-best +14% HR and +30% combined runs with 77°F air and 6 mph wind. Michael Lorenzen is a bum arm (1.24 HR risk, 2.32 vs LHB); Rockies bats are live despite Webb on the mound.",
        "away": "SF",
        "home": "COL",
        "away_sp": "Webb",
        "home_sp": "Lorenzen",
    },
    {
        "key": "NYY @ ATH",
        "title": "NYY @ ATH - Carlos Rodon (L, NYY) vs Luis Severino (R, ATH)",
        "desc": "Sutter Health Park — +9% HR row with +9% combined runs, 72°F clear air, and 6 mph wind. Luis Severino is attackable; A's bats get the plus carry environment.",
        "away": "NYY",
        "home": "ATH",
        "away_sp": "Rodon",
        "home_sp": "Severino",
    },
    {
        "key": "ARI @ SEA",
        "title": "ARI @ SEA - Zac Gallen (R, ARI) vs George Kirby (R, SEA)",
        "desc": "T-Mobile Park — slate-worst -12% HR and -14% combined runs with 58°F overcast dome air. George Kirby suppresses; Seattle bats face Gallen in the harshest HR environment.",
        "away": "ARI",
        "home": "SEA",
        "away_sp": "Gallen",
        "home_sp": "Kirby",
    },
    {
        "key": "PHI @ LAD",
        "title": "PHI @ LAD - Zack Wheeler (R, PHI) vs Justin Wrobleski (L, LAD)",
        "desc": "Dodger Stadium — +6% HR row with 63°F clear air and consistent 11 mph out-blowing wind. Zack Wheeler suppresses (-0.72 HR risk); Dodgers lefties are the premium attack lane versus Wrobleski.",
        "away": "PHI",
        "home": "LAD",
        "away_sp": "Wheeler",
        "home_sp": "Wrobleski",
    },
]

TEAM_MAP = {
    "Michael Harris II": "ATL",
    "Austin Riley": "ATL",
    "Mike Yastrzemski": "ATL",
    "Matt Olson": "ATL",
    "Ronald Acuna Jr.": "ATL",
    "JJ Bleday": "CIN",
    "Matt McLain": "CIN",
    "Elly De La Cruz": "CIN",
    "Ramon Laureano": "SD",
    "Manny Machado": "SD",
    "Jackson Merrill": "SD",
    "Gavin Sheets": "SD",
    "Jacob Young": "WSH",
    "James Wood": "WSH",
    "Luis Garcia Jr.": "WSH",
    "CJ Abrams": "WSH",
    "Byron Buxton": "MIN",
    "Ryan Kreidler": "MIN",
    "Spencer Horwitz": "PIT",
    "Brandon Lowe": "PIT",
    "Marcell Ozuna": "PIT",
    "George Springer": "TOR",
    "Kazuma Okamoto": "TOR",
    "Blaze Alexander": "TOR",
    "Jackson Holliday": "BAL",
    "Samuel Bassallo": "BAL",
    "Gunnar Henderson": "BAL",
    "Zach Neto": "LAA",
    "Jo Adell": "LAA",
    "Mike Trout": "LAA",
    "Yandy Diaz": "TB",
    "Hunter Feduccia": "TB",
    "Jonathan Aranda": "TB",
    "Richie Palacios": "TB",
    "Owen Caissie": "MIA",
    "Xavier Edwards": "MIA",
    "Heriberto Hernandez": "MIA",
    "Juan Soto": "NYM",
    "AJ Ewing": "NYM",
    "Jared Young": "NYM",
    "Jarren Duran": "BOS",
    "Ceddanne Rafaela": "BOS",
    "Willson Contreras": "BOS",
    "Rhys Hoskins": "CLE",
    "Bryan Rocchio": "CLE",
    "Jose Ramirez": "CLE",
    "Ian Happ": "CHC",
    "Michael Conforto": "CHC",
    "Pete Crow-Armstrong": "CHC",
    "Jordan Walker": "STL",
    "Nolan Gorman": "STL",
    "JJ Wetherholt": "STL",
    "Riley Greene": "DET",
    "Spencer Torkelson": "DET",
    "Gage Workman": "DET",
    "Munetaka Murakami": "CWS",
    "Miguel Vargas": "CWS",
    "Colson Montgomery": "CWS",
    "Salvador Perez": "KC",
    "Bobby Witt Jr.": "KC",
    "Joc Pederson": "TEX",
    "Brandon Nimmo": "TEX",
    "Jackson Chourio": "MIL",
    "Christian Yelich": "MIL",
    "Jake Bauers": "MIL",
    "Garrett Mitchell": "MIL",
    "Isaac Paredes": "HOU",
    "Christian Walker": "HOU",
    "Yordan Alvarez": "HOU",
    "Tj Rumfield": "COL",
    "Hunter Goodman": "COL",
    "Ben Rice": "NYY",
    "Aaron Judge": "NYY",
    "Ryan McMahon": "NYY",
    "Shea Langeliers": "ATH",
    "Zack Gelof": "ATH",
    "Colby Thomas": "ATH",
    "Nick Kurtz": "ATH",
    "Ketel Marte": "ARI",
    "Corbin Carroll": "ARI",
    "Nolan Arenado": "ARI",
    "Gabriel Moreno": "ARI",
    "Mitch Garver": "SEA",
    "Dominic Canzone": "SEA",
    "Colt Emerson": "SEA",
    "Luke Raley": "SEA",
    "Patrick Wisdom": "SEA",
    "Kyle Schwarber": "PHI",
    "Bryce Harper": "PHI",
    "Alec Bohm": "PHI",
    "Will Smith": "LAD",
    "Freddie Freeman": "LAD",
    "Shohei Ohtani": "LAD",
    "Andy Pages": "LAD",
}

GAME_ORDER = [g["key"] for g in GAME_META]
PROP_BY_GAME: dict[str, list] = {k: [] for k in GAME_ORDER}
for p in PROPS:
    name = p[0]
    team = TEAM_MAP[name]
    for gm in GAME_META:
        if team in (gm["away"], gm["home"]):
            PROP_BY_GAME[gm["key"]].append(p)
            break


def fav_emojis(name, hand):
    disp = f"{name} ({hand})"
    em = []
    if disp in FAVS:
        em.append("⭐")
    return em


def build_emojis(name, hand, chip, score, blast):
    em = fav_emojis(name, hand)
    if name in ROCKET:
        em.insert(0, "🚀")
    if score >= 88 or blast == "high":
        if "🌕" not in em:
            em.append("🌕")
        if "💣" not in em:
            em.append("💣")
    elif score >= 78 or blast == "good":
        if "💎" not in em:
            em.append("💎")
    elif score >= 70:
        if "💎" not in em:
            em.append("💎")
    if name in BVP:
        if "📜" not in em:
            em.append("📜")
    return " ".join(em) if em else "💎"


def note_for(name, pitcher, park, hr, near, ev, barrel, angle, hand):
    parts = [angle.rstrip(".")]
    stat = f"{hr} HR"
    if near:
        stat += f", {near} near-HR"
    stat += f", {ev} mph EV"
    if barrel:
        stat += f" and {barrel}% barrels"
    disp = f"{name} ({hand})"
    if disp in FAVS:
        stat = f"Worst Pickz favorite with {stat}"
    if name in BVP:
        stat += f"; {BVP[name]}"
    return f"{stat}. Draws opposing starter {pitcher}; {park}."


def emit_build():
    lines = [
        '#!/usr/bin/env python3',
        '"""Generate games[] block for 2026-05-29 MLB HR cheat sheet."""',
        "import json",
        "from pathlib import Path",
        "",
        "from overdue_eval import apply_inferred_due",
        "",
        "ROOT = Path(__file__).resolve().parent",
        "",
        "FAVS = {",
    ]
    for f in FAVS:
        lines.append(f'    "{f}",')
    lines.append("}")
    lines.append("")
    lines.append("PLAYER_TEAMS = {")
    for name, team in sorted(TEAM_MAP.items()):
        hand = next(p[1] for p in PROPS if p[0] == name)
        lines.append(f'    "{name} ({hand})": "{team}",')
    lines.append("}")
    lines.append("")
    lines.extend(
        textwrap.dedent(
            """
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
            """
        ).strip().splitlines()
    )

    for gm in GAME_META:
        lines.append("    {")
        lines.append(f'        "title": {json.dumps(gm["title"])},')
        lines.append(f'        "description": {json.dumps(gm["desc"])},')
        lines.append('        "rows": [')
        for p in PROP_BY_GAME[gm["key"]]:
            name, hand, odds, score, chip, hr, near, ev, barrel, angle, blast = p
            team = TEAM_MAP[name]
            opp_sp = gm["home_sp"] if team == gm["away"] else gm["away_sp"]
            park = gm["desc"].split(" — ")[0]
            em = build_emojis(name, hand, chip, score, blast)
            note = note_for(name, opp_sp, park, hr, near, ev, barrel, angle, hand)
            blast_s = f', blast="{blast}"' if blast else ""
            lines.append(
                f'            row("{name}", "{hand}", "{odds}", {score}, "{em}", ["vs {opp_sp}"], '
                f'"""{note}"""{blast_s}),'
            )
        lines.append("        ],")
        lines.append("    },")

    lines.extend(
        textwrap.dedent(
            """
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
            """
        ).strip().splitlines()
    )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name} with {len(PROPS)} props")


if __name__ == "__main__":
    emit_build()
