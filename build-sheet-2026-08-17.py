#!/usr/bin/env python3
"""Generate games[] block for 2026-08-17 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Christian Encarnacion-Strand (R)",
    "Heriberto Hernandez (R)",
    "Joshua Baez (R)",
    "Kyle Schwarber (L)",
    "Lawrence Butler (L)",
    "Michael Conforto (L)",
    "Munetaka Murakami (L)",
    "Rafael Flores (R)",
    "Spencer Torkelson (R)",
}

GEMS = {
    "Alec Burleson (L)",
    "Ben Malgeri (R)",
    "Ceddanne Rafaela (R)",
    "Dansby Swanson (R)",
    "Esmerlyn Valdez (R)",
    "Francisco Lindor (S)",
    "Hunter Feduccia (L)",
    "Jackson Merrill (L)",
    "Josh Bell (S)",
    "Max Muncy (L)",
    "Miguel Vargas (R)",
    "Pete Alonso (R)",
    "Tyler Stephenson (R)",
    "Victor Mesa Jr. (L)",
    "Xander Bogaerts (R)",
    "Zack Gelof (R)",
}

PLAYER_TEAMS = {
    "Agustin Ramirez (R)": "MIA",
    "Alec Burleson (L)": "STL",
    "Austin Riley (R)": "ATL",
    "Ben Malgeri (R)": "DET",
    "Bo Bichette (R)": "NYM",
    "Brandon Marsh (L)": "PHI",
    "Brett Baty (L)": "NYM",
    "Bryan Reynolds (S)": "PIT",
    "Byron Buxton (R)": "MIN",
    "Ceddanne Rafaela (R)": "BOS",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Coby Mayo (R)": "BAL",
    "Cole Carrigg (S)": "COL",
    "Colt Keith (L)": "DET",
    "Corbin Carroll (L)": "ARI",
    "Dansby Swanson (R)": "CHC",
    "Derek Hill (R)": "PHI",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Lindor (S)": "NYM",
    "Gavin Sheets (L)": "SD",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "LAD",
    "Hunter Goodman (R)": "COL",
    "Ivan Herrera (R)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Merrill (L)": "SD",
    "Jahmai Jones (R)": "BOS",
    "Jake McCarthy (L)": "COL",
    "Jeff McNeil (L)": "ATH",
    "Jordan Walker (R)": "STL",
    "Josh Bell (S)": "MIN",
    "Joshua Baez (R)": "STL",
    "Ke'Bryan Hayes (R)": "CIN",
    "Ketel Marte (S)": "ARI",
    "Kyle Schwarber (L)": "PHI",
    "Lawrence Butler (L)": "ATH",
    "Luisangel Acuna (R)": "CWS",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Max Muncy (L)": "LAD",
    "Michael Conforto (L)": "CHC",
    "Michael Massey (L)": "KC",
    "Michael Toglia (S)": "CIN",
    "Mickey Moniak (L)": "COL",
    "Miguel Amaya (R)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Mike Yastrzemski (L)": "ATL",
    "Munetaka Murakami (L)": "CWS",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Flores (R)": "PIT",
    "Ronald Acuna Jr. (R)": "ATL",
    "Ronny Simon (S)": "PIT",
    "Sal Stewart (R)": "CIN",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Torkelson (R)": "DET",
    "Teoscar Hernandez (R)": "LAD",
    "Tyler Stephenson (R)": "CIN",
    "Victor Mesa Jr. (L)": "TB",
    "Xander Bogaerts (R)": "SD",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("ATH @ KC", "Barnett"),
    ("CWS @ CHC", "Castillo"),
    ("LAD @ COL", "Sugano"),
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
        "title": "ARI @ BOS - Mitch Bratt (L, ARI) vs Brayan Bello (R, BOS)",
        "description": "Tail key data: Park boost -15% (stadium -7%, weather -8%). Bratt (HR risk 0.14, vs LHB +0.12, vs RHB +0.10). Home starter risk unavailable.",
        "rows": [
            row("Ceddanne Rafaela", "R", "+630", 66, "🌕 💣 💎", ["vs Bratt"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 89.8 mph EV. Bratt RHB split +0.10, HR risk 0.14. park/weather net drag (-15%).""", blast="high"),
            row("Jahmai Jones", "R", "+475", 58, "", ["vs Bratt"], """1 HR, 1 near-HR, 90.7 mph EV. Bratt RHB split +0.10, HR risk 0.14. park/weather net drag (-15%).""", blast="good"),
            row("Corbin Carroll", "L", "+541", 58, "", ["vs Bello"], """1 HR, 1 near-HR, 91.3 mph EV. Bello split/risk data unavailable. limited split/risk sample; park/weather net drag (-15%).""", blast="good"),
            row("Max Kepler", "L", "+830", 58, "", ["vs Bello"], """0 HR, 92.0 mph EV. Bello split/risk data unavailable. limited split/risk sample; park/weather net drag (-15%).""", blast="good"),
            row("Ketel Marte", "S", "+470", 58, "", ["vs Bello"], """0 HR, 2 near-HR, 87.2 mph EV. Bello split/risk data unavailable. limited split/risk sample; park/weather net drag (-15%).""", blast="good"),
        ],
    },
    {
        "title": "ATH @ KC - Mason Barnett 🧤 (R, ATH) vs Michael Wacha (R, KC)",
        "description": "Tail key data: Park boost +5% (stadium +11%, weather -7%). Barnett 🧤 (HR risk 1.32, vs LHB +0.11, vs RHB +2.21). Wacha (HR risk -0.07, vs LHB -0.73, vs RHB +0.87).",
        "rows": [
            row("Jac Caglianone", "L", "+405", 80, "", ["vs Barnett"], """0 HR, 1 near-HR, 98.0 mph EV. Barnett LHB split +0.11, HR risk 1.32. weather carry headwind (-7%); limited recent HR events.""", blast="good"),
            row("Michael Massey", "L", "+720", 76, "", ["vs Barnett"], """1 HR, 1 near-HR, 88.4 mph EV. Barnett LHB split +0.11, HR risk 1.32. weather carry headwind (-7%).""", blast="good"),
            row("Zack Gelof", "R", "+564", 87, "🌕 💣 💎", ["vs Wacha"], """Worst Pickz Hidden Gem. 3 HR, 4 near-HR, 93.8 mph EV. Wacha RHB split +0.87, HR risk -0.07. pitcher risk below avg (-0.07); weather carry headwind (-7%).""", blast="high"),
            row("Lawrence Butler", "L", "+630", 65, "⭐ 🌕 💣", ["vs Wacha"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.8 mph EV. Wacha LHB split -0.73, HR risk -0.07. tough split lane (-0.73); pitcher risk below avg (-0.07).""", blast="high"),
            row("Jeff McNeil", "L", "+920", 58, "", ["vs Wacha"], """1 HR, 1 near-HR, 91.3 mph EV. Wacha LHB split -0.73, HR risk -0.07. tough split lane (-0.73); pitcher risk below avg (-0.07).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ MIN - Martin Perez (L, ATL) vs Bailey Ober (R, MIN)",
        "description": "Tail key data: Park boost +1% (stadium -7%, weather +8%). Perez (HR risk -0.71, vs LHB -0.23, vs RHB -0.67). Ober (HR risk 0.64, vs LHB +0.47, vs RHB +0.59).",
        "rows": [
            row("Josh Bell", "S", "N/A", 58, "💎", ["vs Perez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.6 mph EV. Perez SHB→LHB split -0.23, HR risk -0.71. slight split headwind (-0.23); pitcher suppresses HR (-0.71).""", blast="good"),
            row("Byron Buxton", "R", "N/A", 58, "", ["vs Perez"], """0 HR, 80.4 mph EV. Perez RHB split -0.67, HR risk -0.71. tough split lane (-0.67); pitcher suppresses HR (-0.71)."""),
            row("Austin Riley", "R", "N/A", 72, "", ["vs Ober"], """0 HR, 1 near-HR, 93.7 mph EV. Ober RHB split +0.59, HR risk 0.64. park suppresses carry (-7%); limited recent HR events.""", blast="good"),
            row("Matt Olson", "L", "N/A", 85, "🌕 💣", ["vs Ober"], """2 HR, 3 near-HR, 89.3 mph EV. Ober LHB split +0.47, HR risk 0.64. park suppresses carry (-7%).""", blast="high"),
            row("Mike Yastrzemski", "L", "N/A", 77, "", ["vs Ober"], """1 HR, 2 near-HR, 93.9 mph EV. Ober LHB split +0.47, HR risk 0.64. park suppresses carry (-7%).""", blast="good"),
            row("Ronald Acuna Jr.", "R", "N/A", 73, "", ["vs Ober"], """0 HR, 1 near-HR, 95.2 mph EV. Ober RHB split +0.59, HR risk 0.64. park suppresses carry (-7%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "BAL @ TB - Brandon Young (R, BAL) vs Shane McClanahan (L, TB)",
        "description": "Tail key data: Park boost -4% (stadium -4%, weather +0%). Young (HR risk -0.14, vs LHB -0.65, vs RHB +0.51). McClanahan (HR risk -0.62, vs LHB -0.23, vs RHB -0.58).",
        "rows": [
            row("Victor Mesa Jr.", "L", "+475", 58, "🌕 💣 💎", ["vs Young"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 86.6 mph EV. Young LHB split -0.65, HR risk -0.14. tough split lane (-0.65); pitcher risk below avg (-0.14).""", blast="high"),
            row("Christian Encarnacion-Strand", "R", "+499", 69, "🚀 ⭐ 🌕 💣", ["vs McClanahan"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 101.1 mph EV. McClanahan RHB split -0.58, HR risk -0.62. tough split lane (-0.58); pitcher suppresses HR (-0.62).""", blast="high"),
            row("Pete Alonso", "R", "+439", 62, "🌕 💣 💎", ["vs McClanahan"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.8 mph EV. McClanahan RHB split -0.58, HR risk -0.62. tough split lane (-0.58); pitcher suppresses HR (-0.62).""", blast="high"),
            row("Coby Mayo", "R", "+450", 67, "🌕 💣", ["vs McClanahan"], """2 HR, 3 near-HR, 95.8 mph EV. McClanahan RHB split -0.58, HR risk -0.62. tough split lane (-0.58); pitcher suppresses HR (-0.62).""", blast="high"),
        ],
    },
    {
        "title": "CWS @ CHC - Luis Castillo 🧤 (R, CWS) vs Shota Imanaga (L, CHC)",
        "description": "Tail key data: Park boost +8% (stadium -1%, weather +9%). Castillo 🧤 (HR risk 0.98, vs LHB +1.35, vs RHB +0.02). Imanaga (HR risk 0.76, vs LHB +1.15, vs RHB +0.31).",
        "rows": [
            row("Michael Conforto", "L", "+535", 88, "⭐ 🌕 💣", ["vs Castillo"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 91.6 mph EV. Castillo LHB split +1.35, HR risk 0.98.""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+320", 92, "🌕 💣", ["vs Castillo"], """2 HR, 2 near-HR, 89.6 mph EV. Castillo LHB split +1.35, HR risk 0.98.""", blast="high"),
            row("Dansby Swanson", "R", "N/A", 71, "💎", ["vs Castillo"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 86.4 mph EV. Castillo RHB split +0.02, HR risk 0.98. lighter EV form (86.4 mph).""", blast="good"),
            row("Miguel Amaya", "R", "+650", 73, "", ["vs Castillo"], """0 HR, 94.1 mph EV. Castillo RHB split +0.02, HR risk 0.98. limited recent HR events.""", blast="good"),
            row("Munetaka Murakami", "L", "+338", 86, "⭐", ["vs Imanaga"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.7 mph EV. Imanaga LHB split +1.15, HR risk 0.76.""", blast="good"),
            row("Miguel Vargas", "R", "+330", 79, "💎", ["vs Imanaga"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.8 mph EV. Imanaga RHB split +0.31, HR risk 0.76.""", blast="good"),
            row("Luisangel Acuna", "R", "+1260", 75, "🚀", ["vs Imanaga"], """0 HR, 1 near-HR, 101.0 mph EV. Imanaga RHB split +0.31, HR risk 0.76. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "DET @ PIT - Framber Valdez (L, DET) vs Carmen Mlodzinski (R, PIT)",
        "description": "Tail key data: Park boost -6% (stadium -16%, weather +10%). Valdez (HR risk -0.37, vs LHB -0.70, vs RHB -0.18). Mlodzinski (HR risk -0.31, vs LHB -0.36, vs RHB -0.04).",
        "rows": [
            row("Rafael Flores", "R", "+750", 68, "⭐ 🌕 💣", ["vs Valdez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 99.8 mph EV. Valdez RHB split -0.18, HR risk -0.37. slight split headwind (-0.18); pitcher risk below avg (-0.37).""", blast="high"),
            row("Esmerlyn Valdez", "R", "+551", 58, "💎", ["vs Valdez"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.2 mph EV. Valdez RHB split -0.18, HR risk -0.37. slight split headwind (-0.18); pitcher risk below avg (-0.37).""", blast="good"),
            row("Bryan Reynolds", "S", "+900", 58, "", ["vs Valdez"], """0 HR, 95.5 mph EV. Valdez SHB→RHB split -0.18, HR risk -0.37. slight split headwind (-0.18); pitcher risk below avg (-0.37).""", blast="good"),
            row("Ronny Simon", "S", "+1040", 58, "", ["vs Valdez"], """0 HR, 2 near-HR, 96.9 mph EV. Valdez SHB→RHB split -0.18, HR risk -0.37. slight split headwind (-0.18); pitcher risk below avg (-0.37).""", blast="good"),
            row("Spencer Torkelson", "R", "+520", 58, "⭐", ["vs Mlodzinski"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 97.1 mph EV. Mlodzinski RHB split -0.04, HR risk -0.31. slight split headwind (-0.04); pitcher risk below avg (-0.31).""", blast="good"),
            row("Ben Malgeri", "R", "N/A", 58, "💎", ["vs Mlodzinski"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 89.7 mph EV. Mlodzinski RHB split -0.04, HR risk -0.31. slight split headwind (-0.04); pitcher risk below avg (-0.31).""", blast="good"),
            row("Colt Keith", "L", "+810", 58, "", ["vs Mlodzinski"], """0 HR, 1 near-HR, 93.9 mph EV. Mlodzinski LHB split -0.36, HR risk -0.31. slight split headwind (-0.36); pitcher risk below avg (-0.31).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ COL - Blake Snell (L, LAD) vs Tomoyuki Sugano 🧤 (R, COL)",
        "description": "Tail key data: Park boost +28% (stadium +21%, weather +7%). Snell (HR risk -2.03, vs LHB -1.28, vs RHB -1.59). Sugano 🧤 (HR risk 1.32, vs LHB +1.40, vs RHB +0.67).",
        "rows": [
            row("Cole Carrigg", "S", "+780", 58, "", ["vs Snell"], """0 HR, 1 near-HR, 91.7 mph EV. Snell SHB→LHB split -1.28, HR risk -2.03. tough split lane (-1.28); pitcher suppresses HR (-2.03)."""),
            row("Jake McCarthy", "L", "+1060", 58, "", ["vs Snell"], """1 HR, 1 near-HR, 86.0 mph EV. Snell LHB split -1.28, HR risk -2.03. tough split lane (-1.28); pitcher suppresses HR (-2.03).""", blast="good"),
            row("Mickey Moniak", "L", "+470", 58, "", ["vs Snell"], """1 HR, 1 near-HR, 87.3 mph EV. Snell LHB split -1.28, HR risk -2.03. tough split lane (-1.28); pitcher suppresses HR (-2.03).""", blast="good"),
            row("Hunter Goodman", "R", "+248", 58, "", ["vs Snell"], """0 HR, 83.1 mph EV. Snell RHB split -1.59, HR risk -2.03. tough split lane (-1.59); pitcher suppresses HR (-2.03)."""),
            row("Max Muncy", "L", "+250", 92, "🌕 💣 💎", ["vs Sugano"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.0 mph EV. Sugano LHB split +1.40, HR risk 1.32.""", blast="good"),
            row("Hunter Feduccia", "L", "+650", 93, "🌕 💣 💎", ["vs Sugano"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.1 mph EV. Sugano LHB split +1.40, HR risk 1.32.""", blast="good"),
            row("Shohei Ohtani", "L", "+185", 92, "🌕 💣", ["vs Sugano"], """0 HR, 1 near-HR, 95.4 mph EV. Sugano LHB split +1.40, HR risk 1.32. limited recent HR events.""", blast="good"),
            row("Teoscar Hernandez", "R", "+379", 85, "", ["vs Sugano"], """0 HR, 92.5 mph EV. Sugano RHB split +0.67, HR risk 1.32. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIA @ PHI - Janson Junk (R, MIA) vs Cristopher Sanchez (L, PHI)",
        "description": "Tail key data: Park boost +13% (stadium +16%, weather -3%). Junk (HR risk 0.09, vs LHB +0.07, vs RHB +0.07). Sanchez (HR risk -1.10, vs LHB -1.28, vs RHB -0.79).",
        "rows": [
            row("Kyle Schwarber", "L", "+201", 84, "⭐ 🌕 💣", ["vs Junk"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 95.5 mph EV. Junk LHB split +0.07, HR risk 0.09.""", blast="high"),
            row("Brandon Marsh", "L", "+680", 64, "", ["vs Junk"], """1 HR, 1 near-HR, 91.0 mph EV. Junk LHB split +0.07, HR risk 0.09.""", blast="good"),
            row("Derek Hill", "R", "N/A", 66, "", ["vs Junk"], """1 HR, 2 near-HR, 91.3 mph EV. Junk RHB split +0.07, HR risk 0.09.""", blast="good"),
            row("Agustin Ramirez", "R", "+820", 58, "", ["vs Sanchez"], """0 HR, 2 near-HR, 96.7 mph EV. Sanchez RHB split -0.79, HR risk -1.10. tough split lane (-0.79); pitcher suppresses HR (-1.10).""", blast="good"),
            row("Heriberto Hernandez", "R", "+680", 59, "⭐ 🌕 💣", ["vs Sanchez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.1 mph EV. Sanchez RHB split -0.79, HR risk -1.10. tough split lane (-0.79); pitcher suppresses HR (-1.10).""", blast="high"),
        ],
    },
    {
        "title": "SD @ NYM - Walker Buehler (R, SD) vs Nolan McLean (R, NYM)",
        "description": "Tail key data: Park boost -6% (stadium -1%, weather -5%). Buehler (HR risk -0.13, vs LHB -0.34, vs RHB +0.22). McLean (HR risk 0.09, vs LHB +0.32, vs RHB -0.58).",
        "rows": [
            row("Brett Baty", "L", "+640", 69, "🌕 💣", ["vs Buehler"], """2 HR, 2 near-HR, 97.9 mph EV. Buehler LHB split -0.34, HR risk -0.13. slight split headwind (-0.34); pitcher risk below avg (-0.13).""", blast="high"),
            row("Francisco Lindor", "S", "+446", 64, "💎", ["vs Buehler"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 94.6 mph EV. Buehler SHB→RHB split +0.22, HR risk -0.13. pitcher risk below avg (-0.13); park/weather net drag (-6%).""", blast="good"),
            row("Bo Bichette", "R", "+760", 63, "", ["vs Buehler"], """1 HR, 2 near-HR, 94.2 mph EV. Buehler RHB split +0.22, HR risk -0.13. pitcher risk below avg (-0.13); park/weather net drag (-6%).""", blast="good"),
            row("Gavin Sheets", "L", "+700", 62, "", ["vs McLean"], """1 HR, 1 near-HR, 92.1 mph EV. McLean LHB split +0.32, HR risk 0.09. park/weather net drag (-6%).""", blast="good"),
            row("Xander Bogaerts", "R", "+1000", 69, "🌕 💣 💎", ["vs McLean"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 96.9 mph EV. McLean RHB split -0.58, HR risk 0.09. tough split lane (-0.58); park/weather net drag (-6%).""", blast="high"),
            row("Fernando Tatis Jr.", "R", "+500", 61, "", ["vs McLean"], """1 HR, 2 near-HR, 96.8 mph EV. McLean RHB split -0.58, HR risk 0.09. tough split lane (-0.58); park/weather net drag (-6%).""", blast="good"),
            row("Manny Machado", "R", "+493", 58, "", ["vs McLean"], """0 HR, 98.5 mph EV. McLean RHB split -0.58, HR risk 0.09. tough split lane (-0.58); park/weather net drag (-6%).""", blast="good"),
            row("Jackson Merrill", "L", "+543", 61, "💎", ["vs McLean"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.4 mph EV. McLean LHB split +0.32, HR risk 0.09. park/weather net drag (-6%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "STL @ CIN (G1) - Quinn Mathews (L, STL) vs Chase Petty (R, CIN)",
        "description": "Tail key data: Park boost +30% (stadium +14%, weather +16%). Away starter risk unavailable. Petty (HR risk 0.31, vs LHB -0.09, vs RHB +0.55).",
        "rows": [
            row("Elly De La Cruz", "S", "N/A", 74, "", ["vs Mathews"], """1 HR, 1 near-HR, 97.5 mph EV. Mathews split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Eugenio Suarez", "R", "N/A", 66, "", ["vs Mathews"], """1 HR, 1 near-HR, 88.2 mph EV. Mathews split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Sal Stewart", "R", "N/A", 68, "", ["vs Mathews"], """1 HR, 2 near-HR, 88.1 mph EV. Mathews split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Tyler Stephenson", "R", "N/A", 68, "💎", ["vs Mathews"], """Worst Pickz Hidden Gem. 0 HR, 95.9 mph EV. Mathews split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Alec Burleson", "L", "N/A", 84, "🌕 💣 💎", ["vs Petty"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 99.5 mph EV. Petty LHB split -0.09, HR risk 0.31 (risk carried from 8/7). slight split headwind (-0.09).""", blast="high"),
            row("Jordan Walker", "R", "N/A", 65, "", ["vs Petty"], """0 HR, 1 near-HR, 89.7 mph EV. Petty RHB split +0.55, HR risk 0.31 (risk carried from 8/7). limited recent HR events."""),
        ],
    },
    {
        "title": "STL @ CIN (G2) - Andre Pallante (R, STL) vs Rhett Lowder (R, CIN)",
        "description": "Tail key data: Park boost +17% (stadium +14%, weather +3%). Away starter risk unavailable. Lowder (HR risk 0.13, vs LHB +0.78, vs RHB -1.16).",
        "rows": [
            row("Ke'Bryan Hayes", "R", "N/A", 80, "🌕 💣", ["vs Pallante"], """2 HR, 2 near-HR, 96.4 mph EV. Pallante split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Elly De La Cruz", "S", "N/A", 71, "", ["vs Pallante"], """1 HR, 1 near-HR, 97.5 mph EV. Pallante split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Tyler Stephenson", "R", "N/A", 65, "", ["vs Pallante"], """0 HR, 95.9 mph EV. Pallante split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Michael Toglia", "S", "N/A", 65, "", ["vs Pallante"], """0 HR, 98.5 mph EV. Pallante split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Alec Burleson", "L", "N/A", 86, "🌕 💣", ["vs Lowder"], """2 HR, 2 near-HR, 99.5 mph EV. Lowder LHB split +0.78, HR risk 0.13.""", blast="high"),
            row("Ivan Herrera", "R", "N/A", 61, "", ["vs Lowder"], """0 HR, 1 near-HR, 95.8 mph EV. Lowder RHB split -1.16, HR risk 0.13. tough split lane (-1.16); limited recent HR events.""", blast="good"),
            row("Joshua Baez", "R", "N/A", 59, "⭐", ["vs Lowder"], """Worst Pickz Favorite. 0 HR, 95.6 mph EV. Lowder RHB split -1.16, HR risk 0.13. tough split lane (-1.16); limited recent HR events.""", blast="good"),
            row("Jordan Walker", "R", "N/A", 58, "", ["vs Lowder"], """0 HR, 1 near-HR, 89.7 mph EV. Lowder RHB split -1.16, HR risk 0.13. tough split lane (-1.16); limited recent HR events."""),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-17")

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

    out = ROOT / '_games-0817.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
