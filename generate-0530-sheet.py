#!/usr/bin/env python3
"""One-shot generator for build-sheet-2026-05-30.py (Saturday 5/30/2026 slate)."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "build-sheet-2026-05-30.py"

FAVS = [
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
]

ROCKET = {
    "Manny Machado",
    "Oneil Cruz",
    "Jordan Walker",
    "Samuel Basallo",
}

BVP = {
    "Mike Yastrzemski": "25 AB BvP versus Paddack",
    "Matt Olson": "9 AB BvP versus Paddack",
    "Freddie Freeman": "54 AB BvP versus Wheeler with career HR history",
    "Aaron Judge": "20 AB BvP versus Severino",
    "Mike Trout": "25 AB BvP versus Martinez",
    "Will Smith": "8 AB BvP versus Wheeler",
    "Eugenio Suarez": "6 AB BvP versus Holmes with 1 HR",
    "Michael Busch": "4 AB BvP versus Pallante with 1 HR",
    "Seiya Suzuki": "8 AB BvP versus Pallante with 2 HR",
    "Eric Haase": "3 AB BvP versus Lorenzen",
    "Max Muncy": "9 AB BvP versus Wheeler with 1 HR",
    "Kyle Higashioka": "2 AB BvP versus Kolek with 1 HR",
}

# name, hand, odds, score, chip, hr, near, ev, barrel, angle, blast
PROPS = [
    # ATL @ CIN
    ("Matt Olson", "L", "+270", 78, "Paddack", 0, 0, 96.1, 0, "Olson lefty power at the smallest outfield in MLB", "good"),
    ("Austin Riley", "R", "+360", 86, "Paddack", 2, 2, 95.6, 14.3, "Riley pull-air versus Paddack RHB split at GABP", "high"),
    ("Mike Yastrzemski", "L", "+550", 84, "Paddack", 2, 3, 90.8, 8.3, "Yastrzemski BvP history versus Paddack", "good"),
    ("Eugenio Suarez", "R", "+374", 83, "Holmes", 0, 1, 83.9, 6.7, "Suarez BvP versus Holmes at Great American Ball Park", "good"),
    ("Elly De La Cruz", "S", "+406", 85, "Holmes", 2, 2, 96.2, 20.0, "Holmes HR risk (1.22) fits Elly switch power", "good"),
    # SD @ WSH
    ("Fernando Tatis", "R", "+420", 76, "Alvarez", 0, 3, 88.2, 17.0, "Tatis ceiling versus Alvarez at Nationals Park +8% contact row", "good"),
    ("Manny Machado", "R", "+470", 90, "Alvarez", 1, 1, 100.5, 16.7, "100.5 mph EV versus Alvarez with plus Nationals carry", "high"),
    ("James Wood", "L", "+350", 82, "Giolito", 0, 1, 96.0, 0, "Worst Pickz favorite with 96.0 mph EV versus Giolito", "good"),
    ("CJ Abrams", "L", "+540", 80, "Giolito", 1, 1, 93.1, 11.1, "Abrams pull-side versus Giolito LHB sample", "good"),
    ("Jorbit Vivas", "L", "N/A", 72, "Giolito", 1, 1, 88.5, 8.3, "1 HR with pull-side lift versus Giolito", None),
    # MIN @ PIT
    ("Byron Buxton", "R", "+340", 91, "Jones", 2, 2, 98.6, 22.2, "2 HR and 98.6 mph EV with 10 mph out wind at PNC", "high"),
    ("Spencer Horwitz", "L", "+730", 86, "Bradley", 3, 3, 87.4, 30.8, "3 HR, 3 near-HR with 46.2% pull-air versus Bradley LHB split", "high"),
    ("Brandon Lowe", "L", "+340", 92, "Bradley", 2, 4, 97.6, 30.8, "Worst Pickz favorite with 2 HR and Bradley +0.66 vs LHB", "high"),
    ("Oneil Cruz", "L", "+375", 79, "Bradley", 0, 0, 100.1, 0, "100.1 mph EV versus Bradley with out-blowing PNC wind", "good"),
    ("Bryan Reynolds", "S", "+610", 76, "Bradley", 1, 1, 87.1, 11.1, "Reynolds switch bat versus Bradley RHB lane", "good"),
    ("Marcell Ozuna", "R", "+582", 74, "Bradley", 1, 1, 90.0, 18.2, "Bradley RHB split is Ozuna's lane at PNC", "good"),
    # TOR @ BAL
    ("Pete Alonso", "R", "+380", 88, "Voth", 2, 2, 97.5, 20.0, "Alonso righty power versus Austin Voth at Oriole Park", "high"),
    ("Jackson Holliday", "L", "N/A", 72, "Voth", 1, 1, 96.2, 12.5, "Holliday EV keeps him live versus Voth", "good"),
    ("Samuel Basallo", "L", "N/A", 80, "Voth", 2, 2, 100.1, 22.2, "2 HR in sample versus Voth at Oriole Park", "good"),
    ("Blaze Alexander", "R", "N/A", 78, "Rogers", 1, 3, 89.0, 14.3, "1 HR, 3 near-HR with 57.1% hard-hit versus Rogers", "good"),
    ("Yohendrick Pinango", "L", "N/A", 70, "Voth", 1, 1, 91.0, 14.3, "Pinango lefty lane versus Voth in plus Camden row", None),
    ("Jesus Sanchez", "L", "+520", 81, "Rogers", 3, 3, 92.0, 17.9, "Worst Pickz favorite with 3 HR versus Rogers RHB split", "good"),
    # LAA @ TB
    ("Zach Neto", "R", "+450", 87, "Martinez", 3, 4, 92.5, 27.8, "3 HR, 4 near-HR with 44.4% barrels versus Martinez", "high"),
    ("Mike Trout", "R", "+363", 79, "Martinez", 1, 1, 89.7, 12.5, "Trout BvP history versus Martinez at the dome", "good"),
    ("Vaughn Grissom", "R", "+680", 71, "Martinez", 1, 3, 91.0, 13.6, "1 HR, 3 near-HR versus Martinez in closed dome", None),
    ("Junior Caminero", "R", "+375", 84, "Urena", 2, 6, 95.7, 24.0, "2 HR, 6 near-HR with pull-side damage versus Urena", "high"),
    ("Yandy Diaz", "R", "+710", 83, "Urena", 2, 3, 91.3, 26.7, "2 HR, 3 near-HR with pull-side lift versus Urena", "good"),
    # MIA @ NYM
    ("Xavier Edwards", "S", "+1300", 62, "Peralta", 0, 0, 84.3, 5.6, "Switch bat versus Peralta in Citi drag", None),
    ("Owen Caissie", "L", "+760", 84, "Peralta", 1, 1, 97.6, 33.3, "1 HR with 97.6 mph EV and 83.3% hard-hit", "good"),
    ("Juan Soto", "L", "+350", 95, "Meyer", 6, 7, 99.2, 43.8, "6 HR, 7 near-HR and slate-best form versus Meyer", "high"),
    ("Brett Baty", "L", "+710", 77, "Meyer", 1, 1, 90.8, 14.3, "Baty lefty lane versus Meyer RHB split at Citi", "good"),
    ("MJ Melendez", "L", "+550", 68, "Meyer", 0, 0, 90.7, 8.3, "Melendez pull-side versus Meyer in Marlins attack row", None),
    # BOS @ CLE
    ("Willson Contreras", "R", "+504", 80, "Cecconi", 2, 2, 87.7, 8.7, "2 HR with pull-side air versus Cecconi RHB split", "good"),
    ("Wilyer Abreu", "L", "+580", 79, "Bello", 2, 5, 94.0, 18.9, "2 HR, 5 near-HR versus Bello at Progressive Field", "good"),
    ("Patrick Bailey", "S", "+1140", 70, "Bello", 1, 2, 89.5, 10.0, "1 HR, 2 near-HR versus Bello RHB lane", None),
    ("Travis Bazzana", "L", "+910", 68, "Bello", 0, 2, 82.9, 10.0, "2 near-HR with 40.0% hard-hit versus Bello", None),
    # CHC @ STL — Pallante (STL) / Imanaga (CHC)
    ("Ian Happ", "S", "+525", 78, "Pallante", 1, 1, 87.9, 14.3, "Worst Pickz favorite with Happ BvP history versus Pallante", "good"),
    ("Michael Busch", "L", "+590", 76, "Pallante", 1, 4, 92.0, 25.0, "Busch BvP versus Pallante with 4 near-HR in sample", "good"),
    ("Seiya Suzuki", "R", "+520", 82, "Pallante", 2, 2, 94.5, 26.1, "Suzuki BvP versus Pallante with 2 HR in sample", "good"),
    ("Jordan Walker", "R", "+410", 86, "Imanaga", 1, 2, 101.8, 25.0, "Worst Pickz favorite with 101.8 mph EV versus Imanaga LHB risk", "high"),
    ("Alec Burleson", "L", "+500", 80, "Imanaga", 0, 0, 93.4, 0, "Worst Pickz favorite with Imanaga 1.68 vs LHB leakage", "good"),
    ("Bryan Torres", "L", "+1120", 66, "Imanaga", 0, 0, 87.1, 0, "Torres lefty lane versus Imanaga at Busch", None),
    # DET @ CWS
    ("Dillon Dingler", "R", "+480", 79, "Fedde", 4, 1, 92.0, 17.6, "Worst Pickz favorite with 4 HR versus Fedde RHB HR risk", "good"),
    ("Spencer Torkelson", "R", "+500", 72, "Fedde", 0, 1, 88.4, 12.5, "Fedde RHB HR risk (1.94) is the Tigers righty lane", None),
    ("Randal Grichuk", "R", "N/A", 74, "Melton", 0, 0, 86.5, 0, "Worst Pickz favorite with pull-side fit versus Melton", None),
    ("Miguel Vargas", "R", "+470", 82, "Melton", 0, 1, 94.1, 9.1, "94.1 mph EV versus Melton at Rate Field", "good"),
    # KC @ TEX
    ("Salvador Perez", "R", "+516", 78, "Gore", 1, 1, 90.7, 11.1, "Perez righty lane versus Gore at Globe Life dome", "good"),
    ("Jac Caglianone", "L", "+620", 80, "Gore", 2, 5, 94.0, 29.9, "Worst Pickz favorite with 2 HR versus Gore LHB sample", "good"),
    ("Brandon Nimmo", "L", "+431", 81, "Kolek", 1, 3, 91.0, 20.0, "Worst Pickz favorite with 1 HR, 3 near-HR versus Kolek", "good"),
    ("Kyle Higashioka", "R", "N/A", 68, "Kolek", 1, 1, 84.7, 5.9, "1 HR with BvP versus Kolek at Globe Life", None),
    # MIL @ HOU
    ("Christian Yelich", "L", "+590", 76, "Teng", 1, 1, 92.0, 10.0, "Yelich lefty lane versus Teng at Daikin Park", "good"),
    ("Jake Bauers", "L", "+440", 79, "Teng", 0, 0, 94.3, 28.6, "94.3 mph EV with 71.4% hard-hit versus Teng", "good"),
    ("Garrett Mitchell", "L", "+790", 82, "Teng", 1, 3, 99.0, 27.3, "Worst Pickz favorite with 99.0 mph EV versus Teng", "good"),
    ("Jackson Chourio", "R", "+490", 83, "Teng", 0, 1, 99.7, 35.7, "Worst Pickz favorite with 99.7 mph EV and 64.3% hard-hit", "good"),
    ("Isaac Paredes", "R", "+500", 80, "Crow", 2, 2, 88.6, 16.7, "2 HR with pull-side damage versus Crow", "good"),
    ("Yordan Alvarez", "L", "+300", 85, "Crow", 0, 1, 98.1, 0, "Worst Pickz favorite with Alvarez lefty power versus Crow", "high"),
    # SF @ COL
    ("Willy Adames", "R", "+540", 84, "Lorenzen", 2, 3, 96.5, 22.0, "Worst Pickz favorite with Adames power versus Lorenzen at Coors", "high"),
    ("Rafael Devers", "L", "+380", 88, "Lorenzen", 2, 3, 98.4, 28.0, "Devers lefty lane versus Lorenzen 2.29 LHB HR leak at Coors", "high"),
    ("Tj Rumfield", "L", "+880", 74, "Webb", 1, 3, 82.5, 11.1, "Coors altitude with Webb on the mound", "good"),
    ("Hunter Goodman", "R", "+410", 78, "Webb", 1, 1, 89.8, 11.1, "Goodman righty lane versus Webb at Coors", "good"),
    ("Eric Haase", "R", "+950", 70, "Lorenzen", 0, 0, 88.0, 25.0, "Haase BvP versus Lorenzen in plus Coors row", None),
    # NYY @ ATH
    ("Ben Rice", "L", "+328", 84, "Severino", 1, 1, 90.0, 0, "Rice pull-side fit versus Severino at Sutter +9% HR", "good"),
    ("Aaron Judge", "R", "+235", 84, "Severino", 1, 2, 97.0, 15.4, "Judge BvP history versus Severino", "high"),
    ("Ryan McMahon", "L", "N/A", 76, "Severino", 2, 2, 88.3, 18.2, "2 HR with 36.4% hard-hit versus Severino", "good"),
    ("Shea Langeliers", "R", "+392", 74, "Rodon", 0, 0, 87.2, 12.5, "Langeliers EV live versus Rodon at Sutter Health", None),
    ("Colby Thomas", "R", "+610", 72, "Rodon", 0, 2, 87.0, 15.4, "2 near-HR with 38.5% hard-hit versus Rodon", None),
    # ARI @ SEA
    ("Ketel Marte", "S", "+520", 86, "Kirby", 2, 2, 78.4, 13.3, "Worst Pickz favorite with 2 HR versus Kirby", "good"),
    ("Corbin Carroll", "L", "+550", 84, "Kirby", 1, 2, 94.0, 16.7, "94.0 mph EV versus Kirby despite T-Mobile drag", "good"),
    ("Julio Rodriguez", "R", "+500", 82, "Gallen", 2, 2, 90.1, 10.5, "2 HR with 90.1 mph EV versus Gallen", "good"),
    ("Luke Raley", "L", "+423", 72, "Gallen", 0, 0, 85.0, 0, "Worst Pickz favorite with lefty lane versus Gallen", None),
    # PHI @ LAD
    ("Kyle Schwarber", "L", "+290", 92, "Wrobleski", 3, 3, 95.1, 30.0, "Worst Pickz favorite with 3 HR and 60.0% pull-air", "high"),
    ("Trea Turner", "R", "+380", 84, "Wrobleski", 2, 2, 94.0, 22.2, "Worst Pickz favorite with 2 HR versus Wrobleski RHB lane", "good"),
    ("Bryce Harper", "L", "+500", 80, "Wrobleski", 0, 2, 95.4, 22.2, "Worst Pickz favorite with 95.4 mph EV versus Wrobleski", "good"),
    ("Freddie Freeman", "L", "+550", 89, "Wheeler", 3, 3, 91.2, 33.3, "3 HR and Freeman BvP history versus Wheeler", "high"),
    ("Shohei Ohtani", "L", "+310", 90, "Wheeler", 2, 2, 96.6, 30.0, "2 HR and 96.6 mph EV versus Wheeler with 13 mph out wind", "high"),
    ("Will Smith", "R", "+578", 87, "Wheeler", 2, 4, 96.2, 33.3, "2 HR, 4 near-HR and BvP versus Wheeler", "high"),
    ("Max Muncy", "L", "+320", 81, "Wheeler", 1, 2, 89.0, 50.0, "Muncy BvP versus Wheeler with 50.0% barrels in sample", "good"),
    ("Andy Pages", "R", "+582", 72, "Wheeler", 0, 1, 89.7, 7.7, "Pages righty lane versus Wheeler at Dodger Stadium +6% HR", None),
]

GAME_META = [
    {
        "key": "ATL @ CIN",
        "title": "ATL @ CIN - Grant Holmes 🧤 (R, ATL) vs Chris Paddack (R, CIN)",
        "desc": "Great American Ball Park — smallest outfield in MLB with 76°F partially cloudy air and 2 mph wind. Grant Holmes carries 1.22 HR risk; Chris Paddack is attackable to both splits.",
        "away": "ATL",
        "home": "CIN",
        "away_sp": "Holmes",
        "home_sp": "Paddack",
    },
    {
        "key": "SD @ WSH",
        "title": "SD @ WSH - Lucas Giolito (R, SD) vs Andrew Alvarez (L, WSH)",
        "desc": "Nationals Park — great contact environment with 75°F clear air and 7 mph wind. Lucas Giolito suppresses (-1.58 HR risk); James Wood and Nationals bats attack Alvarez.",
        "away": "SD",
        "home": "WSH",
        "away_sp": "Giolito",
        "home_sp": "Alvarez",
    },
    {
        "key": "MIN @ PIT",
        "title": "MIN @ PIT - Taj Bradley (R, MIN) vs Jared Jones (R, PIT)",
        "desc": "PNC Park — 74°F clear air with 10 mph out-blowing wind. Taj Bradley owns +0.66 vs LHB; Brandon Lowe and Spencer Horwitz are the premium lefty attack lane.",
        "away": "MIN",
        "home": "PIT",
        "away_sp": "Bradley",
        "home_sp": "Jones",
    },
    {
        "key": "TOR @ BAL",
        "title": "TOR @ BAL - Austin Voth (R, TOR) vs Trevor Rogers (L, BAL)",
        "desc": "Oriole Park — 75°F clear air with 6 mph crosswind and HR-friendly right side. Trevor Rogers owns 0.87 vs RHB for Toronto; Pete Alonso and Baltimore righties attack Austin Voth.",
        "away": "TOR",
        "home": "BAL",
        "away_sp": "Voth",
        "home_sp": "Rogers",
    },
    {
        "key": "LAA @ TB",
        "title": "LAA @ TB - Walbert Urena (R, LAA) vs Nick Martinez (R, TB)",
        "desc": "Tropicana Field — closed dome, flat +2% HR row. Nick Martinez suppresses (-0.67 HR risk); Junior Caminero and Rays bats lean on form versus Urena.",
        "away": "LAA",
        "home": "TB",
        "away_sp": "Urena",
        "home_sp": "Martinez",
    },
    {
        "key": "MIA @ NYM",
        "title": "MIA @ NYM - Max Meyer (R, MIA) vs Freddy Peralta (R, NYM)",
        "desc": "Citi Field — poor contact environment with 73°F air and 12 mph out wind. Juan Soto owns slate-best form; Meyer is the Mets' cleaner attack target.",
        "away": "MIA",
        "home": "NYM",
        "away_sp": "Meyer",
        "home_sp": "Peralta",
    },
    {
        "key": "BOS @ CLE",
        "title": "BOS @ CLE - Brayan Bello (R, BOS) vs Slade Cecconi (R, CLE)",
        "desc": "Progressive Field — high wind receptivity (17 mph) with 74°F clear air. Wilyer Abreu and Willson Contreras own the loudest Boston form versus Cecconi and Bello.",
        "away": "BOS",
        "home": "CLE",
        "away_sp": "Bello",
        "home_sp": "Cecconi",
    },
    {
        "key": "CHC @ STL",
        "title": "CHC @ STL - Shota Imanaga 🧤 (L, CHC) vs Andre Pallante (R, STL)",
        "desc": "Busch Stadium — large outfield with 79°F air and 6 mph wind. Shota Imanaga is a bum arm (1.04 HR risk, 1.68 vs LHB); Jordan Walker and Alec Burleson lead the Cardinal attack.",
        "away": "CHC",
        "home": "STL",
        "away_sp": "Imanaga",
        "home_sp": "Pallante",
    },
    {
        "key": "DET @ CWS",
        "title": "DET @ CWS - Troy Melton (R, DET) vs Erick Fedde 🧤 (R, CWS)",
        "desc": "Rate Field — smallest outfield in MLB with 66°F air and 8 mph wind. Erick Fedde is the slate's top HR-risk arm (1.67, 1.94 vs RHB); Dillon Dingler and Miguel Vargas are live.",
        "away": "DET",
        "home": "CWS",
        "away_sp": "Melton",
        "home_sp": "Fedde",
    },
    {
        "key": "KC @ TEX",
        "title": "KC @ TEX - Stephen Kolek (R, KC) vs MacKenzie Gore (L, TEX)",
        "desc": "Globe Life Field — roof closed with 87°F dome air and +8% typical flight. MacKenzie Gore suppresses; Brandon Nimmo and Jac Caglianone get the cleaner Texas lanes.",
        "away": "KC",
        "home": "TEX",
        "away_sp": "Kolek",
        "home_sp": "Gore",
    },
    {
        "key": "MIL @ HOU",
        "title": "MIL @ HOU - Coleman Crow (R, MIL) vs Kai-Wei Teng (R, HOU)",
        "desc": "Daikin Park — roof closed with 87°F dome air. Coleman Crow suppresses (-1.04 HR risk); Yordan Alvarez and Houston bats attack Crow.",
        "away": "MIL",
        "home": "HOU",
        "away_sp": "Crow",
        "home_sp": "Teng",
    },
    {
        "key": "SF @ COL",
        "title": "SF @ COL - Logan Webb (R, SF) vs Michael Lorenzen 🧤 (R, COL)",
        "desc": "Coors Field — slate-best +29 altitude boost with 76°F air and 7 mph wind. Michael Lorenzen is a bum arm (1.24 HR risk, 2.29 vs LHB); Devers and Adames lead the Giants attack.",
        "away": "SF",
        "home": "COL",
        "away_sp": "Webb",
        "home_sp": "Lorenzen",
    },
    {
        "key": "NYY @ ATH",
        "title": "NYY @ ATH - Carlos Rodon (L, NYY) vs Luis Severino (R, ATH)",
        "desc": "Sutter Health Park — very high wind receptivity with 73°F clear air and 6 mph wind. Luis Severino is attackable; Aaron Judge and A's bats get plus carry.",
        "away": "NYY",
        "home": "ATH",
        "away_sp": "Rodon",
        "home_sp": "Severino",
    },
    {
        "key": "ARI @ SEA",
        "title": "ARI @ SEA - Zac Gallen (R, ARI) vs George Kirby (R, SEA)",
        "desc": "T-Mobile Park — slate-harshest -6% altitude drag with 57°F dome air. George Kirby suppresses; Julio Rodriguez and Seattle bats face Gallen in a contact-poor row.",
        "away": "ARI",
        "home": "SEA",
        "away_sp": "Gallen",
        "home_sp": "Kirby",
    },
    {
        "key": "PHI @ LAD",
        "title": "PHI @ LAD - Zack Wheeler (R, PHI) vs Justin Wrobleski (L, LAD)",
        "desc": "Dodger Stadium — +6% HR row with 67°F clear air and consistent 13 mph out-blowing wind. Zack Wheeler suppresses (-0.68 HR risk); Schwarber, Turner, and Harper attack Wrobleski.",
        "away": "PHI",
        "home": "LAD",
        "away_sp": "Wheeler",
        "home_sp": "Wrobleski",
    },
]

TEAM_MAP = {
    "Matt Olson": "ATL",
    "Austin Riley": "ATL",
    "Mike Yastrzemski": "ATL",
    "Eugenio Suarez": "CIN",
    "Elly De La Cruz": "CIN",
    "Fernando Tatis": "SD",
    "Manny Machado": "SD",
    "James Wood": "WSH",
    "CJ Abrams": "WSH",
    "Jorbit Vivas": "WSH",
    "Byron Buxton": "MIN",
    "Spencer Horwitz": "PIT",
    "Brandon Lowe": "PIT",
    "Oneil Cruz": "PIT",
    "Bryan Reynolds": "PIT",
    "Marcell Ozuna": "PIT",
    "Pete Alonso": "BAL",
    "Jackson Holliday": "BAL",
    "Samuel Basallo": "BAL",
    "Blaze Alexander": "TOR",
    "Yohendrick Pinango": "TOR",
    "Jesus Sanchez": "TOR",
    "Zach Neto": "LAA",
    "Mike Trout": "LAA",
    "Vaughn Grissom": "LAA",
    "Junior Caminero": "TB",
    "Yandy Diaz": "TB",
    "Xavier Edwards": "MIA",
    "Owen Caissie": "MIA",
    "Juan Soto": "NYM",
    "Brett Baty": "NYM",
    "MJ Melendez": "MIA",
    "Willson Contreras": "BOS",
    "Wilyer Abreu": "BOS",
    "Patrick Bailey": "CLE",
    "Travis Bazzana": "CLE",
    "Ian Happ": "CHC",
    "Michael Busch": "CHC",
    "Seiya Suzuki": "CHC",
    "Jordan Walker": "STL",
    "Alec Burleson": "STL",
    "Bryan Torres": "STL",
    "Dillon Dingler": "DET",
    "Spencer Torkelson": "DET",
    "Randal Grichuk": "DET",
    "Miguel Vargas": "CWS",
    "Salvador Perez": "KC",
    "Jac Caglianone": "KC",
    "Brandon Nimmo": "TEX",
    "Kyle Higashioka": "TEX",
    "Christian Yelich": "MIL",
    "Jake Bauers": "MIL",
    "Garrett Mitchell": "MIL",
    "Jackson Chourio": "MIL",
    "Isaac Paredes": "HOU",
    "Yordan Alvarez": "HOU",
    "Willy Adames": "SF",
    "Rafael Devers": "SF",
    "Tj Rumfield": "COL",
    "Hunter Goodman": "COL",
    "Eric Haase": "SF",
    "Ben Rice": "NYY",
    "Aaron Judge": "NYY",
    "Ryan McMahon": "NYY",
    "Shea Langeliers": "ATH",
    "Colby Thomas": "ATH",
    "Ketel Marte": "ARI",
    "Corbin Carroll": "ARI",
    "Julio Rodriguez": "SEA",
    "Luke Raley": "SEA",
    "Kyle Schwarber": "PHI",
    "Trea Turner": "PHI",
    "Bryce Harper": "PHI",
    "Freddie Freeman": "LAD",
    "Shohei Ohtani": "LAD",
    "Will Smith": "LAD",
    "Max Muncy": "LAD",
    "Andy Pages": "LAD",
}

PROP_BY_GAME: dict[str, list] = {k: [] for k in [g["key"] for g in GAME_META]}
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
    if name in ROCKET and "🚀" not in em:
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
        '"""Generate games[] block for 2026-05-30 MLB HR cheat sheet."""',
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
        lines.append(f'        "title": {json.dumps(gm["title"], ensure_ascii=False)},')
        lines.append(f'        "description": {json.dumps(gm["desc"], ensure_ascii=False)},')
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
        [
            "]",
            "",
            "for game in games:",
            "    for entry in game['rows']:",
            "        add_bum_row_emojis(entry)",
            "        apply_inferred_due(entry, game)",
            "",
            'if __name__ == "__main__":',
            "    def js_string(value):",
            "        return json.dumps(value, ensure_ascii=False)",
            "",
            "    def emit_games_js(games_data):",
            '        lines = ["const games = ["]',
            "        for game in games_data:",
            '            lines.append("    {")',
            '            lines.append(f"        title: {js_string(game[\'title\'])},")',
            '            lines.append(f"        description: {js_string(game[\'description\'])},")',
            '            lines.append("        rows: [")',
            "            for entry in game['rows']:",
            "                parts = [",
            '                    f"name: {js_string(entry[\'name\'])}",',
            '                    f"odds: {js_string(entry[\'odds\'])}",',
            '                    f"score: {entry[\'score\']}",',
            '                    f"emojis: {js_string(entry[\'emojis\'])}",',
            '                    f"note: {js_string(entry[\'note\'])}",',
            '                    f"chips: {js_string(entry[\'chips\'])}",',
            "                ]",
            '                if entry.get("blast"):',
            '                    parts.append(f"blast: {js_string(entry[\'blast\'])}")',
            '                lines.append("            { " + ", ".join(parts) + " },")',
            '            lines.append("        ],")',
            '            lines.append("    },")',
            '        lines.append("];")',
            '        return "\\n".join(lines)',
            "",
            '    out = ROOT / "_games-0530.txt"',
            "    out.write_text(emit_games_js(games) + \"\\n\", encoding=\"utf-8\")",
            '    print("wrote", out.name)',
        ]
    )
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name}")
    print(f"props: {len(PROPS)}, games: {len(GAME_META)}, favs: {len(FAVS)}")


if __name__ == "__main__":
    emit_build()
