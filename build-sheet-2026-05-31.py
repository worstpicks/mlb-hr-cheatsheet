#!/usr/bin/env python3
"""Generate games[] block for 2026-05-31 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Brandon Lowe (L)",
    "Brandon Nimmo (L)",
    "CJ Abrams (L)",
    "Elly De La Cruz (S)",
    "Garrett Mitchell (L)",
    "Heriberto Hernandez (R)",
    "Jarren Duran (L)",
    "Jonathan Aranda (L)",
    "Juan Soto (L)",
    "Kazuma Okamoto (R)",
    "Ketel Marte (S)",
    "Luke Raley (L)",
    "Mike Trout (R)",
    "Oneil Cruz (L)",
    "Rafael Devers (L)",
    "Rhys Hoskins (R)",
    "Shohei Ohtani (L)",
    "Will Smith (R)",
    "Willy Adames (R)",
    "Yordan Alvarez (L)",
}

PLAYER_TEAMS = {
    "Ben Rice (L)": "NYY",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Cam Smith (R)": "HOU",
    "Carlos Cortes (L)": "ATH",
    "Casey Schmitt (R)": "SF",
    "Christian Walker (R)": "HOU",
    "Christian Yelich (L)": "MIL",
    "Coby Mayo (R)": "BAL",
    "Cody Bellinger (L)": "NYY",
    "Colson Montgomery (L)": "CWS",
    "Colt Keith (L)": "DET",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Elly De La Cruz (S)": "CIN",
    "Freddie Freeman (L)": "LAD",
    "Garrett Mitchell (L)": "MIL",
    "Gavin Sheets (L)": "SD",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jarren Duran (L)": "BOS",
    "Jo Adell (R)": "LAA",
    "Jonathan Aranda (L)": "TB",
    "Josh Jung (R)": "TEX",
    "Juan Soto (L)": "NYM",
    "Julio Rodriguez (R)": "SEA",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Konnor Griffin (R)": "PIT",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Schwarber (L)": "PHI",
    "Luke Raley (L)": "SEA",
    "MJ Melendez (L)": "NYM",
    "Matt McLain (R)": "CIN",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Mickey Gasper (S)": "BOS",
    "Mike Trout (R)": "LAA",
    "Mitch Garver (R)": "SEA",
    "Oneil Cruz (L)": "PIT",
    "Oswald Peraza (R)": "LAA",
    "Otto Lopez (R)": "MIA",
    "Owen Caissie (L)": "MIA",
    "Patrick Wisdom (R)": "SEA",
    "Paul Goldschmidt (R)": "NYY",
    "Pete Alonso (R)": "BAL",
    "Rafael Devers (L)": "SF",
    "Rhys Hoskins (R)": "CLE",
    "Salvador Perez (R)": "KC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Horwitz (L)": "PIT",
    "Spencer Torkelson (R)": "DET",
    "Trea Turner (R)": "PHI",
    "Trevor Larnach (L)": "MIN",
    "Ty France (R)": "SD",
    "Tyler Soderstrom (L)": "ATH",
    "Will Smith (R)": "LAD",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Dezenzo (R)": "HOU",
}

BUM_PITCHERS = {
    "Lodolo",
    "Ray",
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
        "title": "ARI @ SEA - Merrill Kelly (R, ARI) vs Bryce Miller (R, SEA)",
        "description": "T-Mobile Park — HR environment -13% (stadium +1%, weather -15%). Merrill Kelly: 0.13 HR risk (vs LHB +0.31, vs RHB -0.18; strongest LHB lane +0.31). Bryce Miller: -0.53 HR risk (vs LHB -1.10, vs RHB +0.72; strongest RHB lane +0.72).",
        "rows": [
            row("Julio Rodriguez", "R", "N/A", 87, "🌕 💣", ["vs Kelly"], """3 HR, 3 near-HR, 91.1 mph EV. Draws opposing starter Kelly; ARI @ SEA.""", blast="high"),
            row("Luke Raley", "L", "N/A", 78, "⭐ 🌕 💣", ["vs Kelly"], """Worst Pickz favorite with 2 HR, 2 near-HR, 85.1 mph EV. Draws opposing starter Kelly; ARI @ SEA.""", blast="high"),
            row("Mitch Garver", "R", "N/A", 85, "🌕 💣", ["vs Kelly"], """2 HR, 2 near-HR, 94.6 mph EV. Draws opposing starter Kelly; ARI @ SEA.""", blast="high"),
            row("Patrick Wisdom", "R", "N/A", 75, "💎", ["vs Kelly"], """0 HR, 98.8 mph EV. Draws opposing starter Kelly; ARI @ SEA.""", blast="good"),
            row("Ketel Marte", "S", "N/A", 80, "⭐ 🌕 💣", ["vs Miller"], """Worst Pickz favorite with 2 HR, 3 near-HR, 83.2 mph EV. Draws opposing starter Miller; ARI @ SEA.""", blast="high"),
            row("Corbin Carroll", "L", "N/A", 72, "💎", ["vs Miller"], """1 HR, 1 near-HR, 90.1 mph EV. Draws opposing starter Miller; ARI @ SEA.""", blast="good"),
        ],
    },
    {
        "title": "ATL @ CIN - Spencer Strider (R, ATL) vs Nick Lodolo 🧤 (R, CIN)",
        "description": "Great American BP — HR environment +0% (stadium +12%, weather -12%). Spencer Strider: 0.90 HR risk (vs LHB +1.12, vs RHB -0.47; strongest LHB lane +1.12). Nick Lodolo: 1.03 HR risk (vs LHB -0.55, vs RHB +1.25; strongest RHB lane +1.25).",
        "rows": [
            row("JJ Bleday", "L", "N/A", 78, "🌕 💣", ["vs Strider"], """2 HR, 2 near-HR, 87.8 mph EV. Draws opposing starter Strider; ATL @ CIN.""", blast="high"),
            row("Elly De La Cruz", "S", "N/A", 88, "⭐ 🌕 💣", ["vs Strider"], """Worst Pickz favorite with 2 HR, 3 near-HR, 96.5 mph EV. Draws opposing starter Strider; ATL @ CIN.""", blast="high"),
            row("Matt McLain", "R", "N/A", 73, "💎", ["vs Strider"], """1 HR, 1 near-HR, 91.0 mph EV. Draws opposing starter Strider; ATL @ CIN.""", blast="good"),
            row("Matt Olson", "L", "N/A", 75, "💎", ["vs Lodolo"], """1 HR, 1 near-HR, 93.4 mph EV. Draws opposing starter Lodolo; ATL @ CIN.""", blast="good"),
        ],
    },
    {
        "title": "BOS @ CLE - Ranger Suarez (R, BOS) vs Tanner Bibee (R, CLE)",
        "description": "Progressive Field — HR environment -22% (stadium -5%, weather -18%). Ranger Suarez: -1.42 HR risk (vs LHB +0.13, vs RHB -1.15; strongest LHB lane +0.13). Tanner Bibee: 0.88 HR risk (vs LHB +0.69, vs RHB +0.54; strongest LHB lane +0.69).",
        "rows": [
            row("Rhys Hoskins", "R", "+535", 92, "🚀 ⭐ 🌕 💣", ["vs Suarez"], """Worst Pickz favorite with 2 HR, 3 near-HR, 101.6 mph EV. Draws opposing starter Suarez; BOS @ CLE.""", blast="high"),
            row("Kyle Manzardo", "L", "+810", 70, "💎", ["vs Suarez"], """1 HR, 1 near-HR, 83.7 mph EV. Draws opposing starter Suarez; BOS @ CLE.""", blast="good"),
            row("Jarren Duran", "L", "+571", 98, "⭐ 🌕 💣", ["vs Bibee"], """Worst Pickz favorite with 4 HR, 5 near-HR, 95.1 mph EV. Draws opposing starter Bibee; BOS @ CLE.""", blast="high"),
            row("Willson Contreras", "R", "+413", 70, "💎", ["vs Bibee"], """1 HR, 1 near-HR, 87.5 mph EV. Draws opposing starter Bibee; BOS @ CLE.""", blast="good"),
            row("Mickey Gasper", "S", "+660", 75, "💎", ["vs Bibee"], """0 HR, 2 near-HR, 94.7 mph EV. Draws opposing starter Bibee; BOS @ CLE.""", blast="good"),
        ],
    },
    {
        "title": "DET @ CWS - Keider Montero (R, DET) vs Sean Burke (R, CWS)",
        "description": "Rate Field — HR environment -8% (stadium +3%, weather -11%). Keider Montero: 0.31 HR risk (vs LHB +0.53, vs RHB -0.12; strongest LHB lane +0.53). Sean Burke: -0.67 HR risk (vs LHB -0.50, vs RHB -0.25; strongest RHB lane -0.25).",
        "rows": [
            row("Colson Montgomery", "L", "+159", 70, "💎", ["vs Montero"], """1 HR, 1 near-HR, 85.4 mph EV. Draws opposing starter Montero; DET @ CWS.""", blast="good"),
            row("Colt Keith", "L", "N/A", 62, "💎", ["vs Burke"], """0 HR, 86.3 mph EV. Draws opposing starter Burke; DET @ CWS."""),
            row("Spencer Torkelson", "R", "N/A", 72, "💎", ["vs Burke"], """1 HR, 2 near-HR, 88.1 mph EV. Draws opposing starter Burke; DET @ CWS.""", blast="good"),
        ],
    },
    {
        "title": "KC @ TEX - Michael Wacha (R, KC) vs Jack Leiter (R, TEX)",
        "description": "Globe Life Field — HR environment -10% (stadium -9%, weather -1%). Michael Wacha: -0.49 HR risk (vs LHB -0.60, vs RHB +0.23; strongest RHB lane +0.23). Jack Leiter: -0.23 HR risk (vs LHB -0.08, vs RHB -0.18; strongest LHB lane -0.08).",
        "rows": [
            row("Brandon Nimmo", "L", "N/A", 89, "⭐ 🌕 💣", ["vs Wacha"], """Worst Pickz favorite with 2 HR, 5 near-HR, 93.1 mph EV. Draws opposing starter Wacha; KC @ TEX.""", blast="high"),
            row("Josh Jung", "R", "N/A", 85, "🌕 💣", ["vs Wacha"], """2 HR, 4 near-HR, 91.0 mph EV. Draws opposing starter Wacha; KC @ TEX.""", blast="high"),
            row("Jac Caglianone", "L", "N/A", 84, "🚀 💎", ["vs Leiter"], """1 HR, 2 near-HR, 103.2 mph EV. Draws opposing starter Leiter; KC @ TEX.""", blast="good"),
            row("Salvador Perez", "R", "N/A", 75, "💎", ["vs Leiter"], """1 HR, 1 near-HR, 92.6 mph EV. Draws opposing starter Leiter; KC @ TEX.""", blast="good"),
        ],
    },
    {
        "title": "LAA @ TB - Jack Kochanowicz (R, LAA) vs Shane McClanahan (R, TB)",
        "description": "Tropicana Field — HR environment -4% (stadium -4%, weather +1%). Jack Kochanowicz: -0.28 HR risk (vs LHB -0.57, vs RHB +0.20; strongest RHB lane +0.20). Shane McClanahan: -1.17 HR risk (vs LHB -1.46, vs RHB -0.40; strongest RHB lane -0.40).",
        "rows": [
            row("Jonathan Aranda", "L", "+252", 80, "⭐ 💎", ["vs Kochanowicz"], """Worst Pickz favorite with 1 HR, 2 near-HR, 95.6 mph EV. Draws opposing starter Kochanowicz; LAA @ TB.""", blast="good"),
            row("Yandy Diaz", "R", "+334", 90, "🌕 💣", ["vs Kochanowicz"], """3 HR, 4 near-HR, 91.7 mph EV. Draws opposing starter Kochanowicz; LAA @ TB.""", blast="high"),
            row("Mike Trout", "R", "N/A", 73, "⭐ 💎", ["vs McClanahan"], """Worst Pickz favorite with 1 HR, 1 near-HR, 90.7 mph EV. Draws opposing starter McClanahan; LAA @ TB.""", blast="good"),
            row("Oswald Peraza", "R", "N/A", 76, "💎", ["vs McClanahan"], """1 HR, 2 near-HR, 91.7 mph EV. Draws opposing starter McClanahan; LAA @ TB.""", blast="good"),
            row("Jo Adell", "R", "N/A", 91, "🌕 💣", ["vs McClanahan"], """2 HR, 3 near-HR, 98.7 mph EV. Draws opposing starter McClanahan; LAA @ TB.""", blast="high"),
        ],
    },
    {
        "title": "MIA @ NYM - Janson Junk (R, MIA) vs Nolan McLean (R, NYM)",
        "description": "Citi Field — HR environment -8% (stadium -2%, weather -6%). Janson Junk: 0.09 HR risk (vs LHB +0.10, vs RHB +0.04; strongest LHB lane +0.10). Nolan McLean: 0.28 HR risk (vs LHB +0.14, vs RHB +0.35; strongest RHB lane +0.35).",
        "rows": [
            row("Juan Soto", "L", "N/A", 94, "⭐ 🌕 💣", ["vs Junk"], """Worst Pickz favorite with 3 HR, 4 near-HR, 96.4 mph EV. Draws opposing starter Junk; MIA @ NYM.""", blast="high"),
            row("Jared Young", "L", "N/A", 79, "💎", ["vs Junk"], """1 HR, 1 near-HR, 96.8 mph EV. Draws opposing starter Junk; MIA @ NYM.""", blast="good"),
            row("MJ Melendez", "L", "N/A", 74, "💎", ["vs Junk"], """1 HR, 1 near-HR, 91.9 mph EV. Draws opposing starter Junk; MIA @ NYM.""", blast="good"),
            row("Heriberto Hernandez", "R", "N/A", 63, "⭐ 💎", ["vs McLean"], """Worst Pickz favorite with 0 HR, 88.9 mph EV. Draws opposing starter McLean; MIA @ NYM."""),
            row("Otto Lopez", "R", "N/A", 66, "💎", ["vs McLean"], """0 HR, 1 near-HR, 90.5 mph EV. Draws opposing starter McLean; MIA @ NYM."""),
            row("Owen Caissie", "L", "N/A", 79, "💎", ["vs McLean"], """1 HR, 2 near-HR, 94.7 mph EV. Draws opposing starter McLean; MIA @ NYM.""", blast="good"),
        ],
    },
    {
        "title": "MIL @ HOU - Jacob Misiorowski (R, MIL) vs Tatsuya Imai (R, HOU)",
        "description": "Daikin Park — HR environment +6% (stadium +7%, weather 0%). Jacob Misiorowski: -1.71 HR risk (vs LHB -0.86, vs RHB -1.33; strongest LHB lane -0.86). Tatsuya Imai: 0.79 HR risk (vs LHB +1.20, vs RHB -0.38; strongest LHB lane +1.20).",
        "rows": [
            row("Yordan Alvarez", "L", "N/A", 86, "🚀 ⭐ 💎", ["vs Misiorowski"], """Worst Pickz favorite with 1 HR, 3 near-HR, 102.0 mph EV. Draws opposing starter Misiorowski; MIL @ HOU.""", blast="good"),
            row("Christian Walker", "R", "N/A", 75, "💎", ["vs Misiorowski"], """1 HR, 1 near-HR, 93.2 mph EV. Draws opposing starter Misiorowski; MIL @ HOU.""", blast="good"),
            row("Cam Smith", "R", "N/A", 72, "💎", ["vs Misiorowski"], """0 HR, 95.5 mph EV. Draws opposing starter Misiorowski; MIL @ HOU.""", blast="good"),
            row("Zach Dezenzo", "R", "N/A", 68, "💎", ["vs Misiorowski"], """0 HR, 1 near-HR, 91.6 mph EV. Draws opposing starter Misiorowski; MIL @ HOU."""),
            row("Garrett Mitchell", "L", "N/A", 94, "🚀 ⭐ 🌕 💣", ["vs Imai"], """Worst Pickz favorite with 2 HR, 4 near-HR, 101.1 mph EV. Draws opposing starter Imai; MIL @ HOU.""", blast="high"),
            row("Christian Yelich", "L", "N/A", 70, "💎", ["vs Imai"], """0 HR, 93.7 mph EV. Draws opposing starter Imai; MIL @ HOU.""", blast="good"),
            row("Jackson Chourio", "R", "N/A", 74, "💎", ["vs Imai"], """0 HR, 2 near-HR, 93.5 mph EV. Draws opposing starter Imai; MIL @ HOU.""", blast="good"),
        ],
    },
    {
        "title": "MIN @ PIT - Zebby Matthews (R, MIN) vs Braxton Ashcraft (R, PIT)",
        "description": "PNC Park — HR environment -29% (stadium -14%, weather -15%). Zebby Matthews: 0.09 HR risk (vs LHB +0.31, vs RHB -0.12; strongest LHB lane +0.31). Braxton Ashcraft: -1.05 HR risk (vs LHB -0.44, vs RHB -0.91; strongest LHB lane -0.44).",
        "rows": [
            row("Brandon Lowe", "L", "+247", 89, "⭐ 🌕 💣", ["vs Matthews"], """Worst Pickz favorite with 2 HR, 4 near-HR, 94.9 mph EV. Draws opposing starter Matthews; MIN @ PIT.""", blast="high"),
            row("Oneil Cruz", "L", "+304", 90, "⭐ 🌕 💣", ["vs Matthews"], """Worst Pickz favorite with 2 HR, 3 near-HR, 97.5 mph EV. Draws opposing starter Matthews; MIN @ PIT.""", blast="high"),
            row("Spencer Horwitz", "L", "+383", 84, "🌕 💣", ["vs Matthews"], """3 HR, 3 near-HR, 86.0 mph EV. Draws opposing starter Matthews; MIN @ PIT.""", blast="high"),
            row("Konnor Griffin", "R", "N/A", 70, "💎", ["vs Matthews"], """1 HR, 1 near-HR, 77.6 mph EV. Draws opposing starter Matthews; MIN @ PIT.""", blast="good"),
            row("Byron Buxton", "R", "+229", 75, "💎", ["vs Ashcraft"], """1 HR, 1 near-HR, 93.1 mph EV. Draws opposing starter Ashcraft; MIN @ PIT.""", blast="good"),
            row("Trevor Larnach", "L", "+583", 71, "💎", ["vs Ashcraft"], """1 HR, 1 near-HR, 89.1 mph EV. Draws opposing starter Ashcraft; MIN @ PIT.""", blast="good"),
        ],
    },
    {
        "title": "NYY @ ATH - Will Warren (R, NYY) vs Jacob Lopez (R, ATH)",
        "description": "Sutter Health Park — HR environment +23% (stadium +32%, weather -9%). Will Warren: -0.13 HR risk (vs LHB -0.11, vs RHB +0.22; strongest RHB lane +0.22). Jacob Lopez: no reliable HR-risk sample in today's export.",
        "rows": [
            row("Carlos Cortes", "L", "N/A", 70, "💎", ["vs Warren"], """1 HR, 1 near-HR, 84.7 mph EV. Draws opposing starter Warren; NYY @ ATH.""", blast="good"),
            row("Tyler Soderstrom", "L", "N/A", 65, "💎", ["vs Warren"], """0 HR, 1 near-HR, 88.9 mph EV. Draws opposing starter Warren; NYY @ ATH."""),
            row("Ben Rice", "L", "N/A", 72, "💎", ["vs Lopez"], """0 HR, 1 near-HR, 93.9 mph EV. Draws opposing starter Lopez; NYY @ ATH.""", blast="good"),
            row("Cody Bellinger", "L", "N/A", 70, "💎", ["vs Lopez"], """1 HR, 1 near-HR, 85.5 mph EV. Draws opposing starter Lopez; NYY @ ATH.""", blast="good"),
            row("Paul Goldschmidt", "R", "N/A", 76, "💎", ["vs Lopez"], """1 HR, 1 near-HR, 93.6 mph EV. Draws opposing starter Lopez; NYY @ ATH.""", blast="good"),
        ],
    },
    {
        "title": "PHI @ LAD - Andrew Painter (R, PHI) vs Yoshinobu Yamamoto (R, LAD)",
        "description": "Dodger Stadium — HR environment +20% (stadium +18%, weather +3%). Andrew Painter: 0.23 HR risk (vs LHB -0.61, vs RHB +1.28; strongest RHB lane +1.28). Yoshinobu Yamamoto: -0.09 HR risk (vs LHB -0.21, vs RHB +0.18; strongest RHB lane +0.18).",
        "rows": [
            row("Freddie Freeman", "L", "N/A", 98, "🌕 💣", ["vs Painter"], """4 HR, 4 near-HR, 96.4 mph EV. Draws opposing starter Painter; PHI @ LAD.""", blast="high"),
            row("Shohei Ohtani", "L", "N/A", 95, "⭐ 🌕 💣", ["vs Painter"], """Worst Pickz favorite with 3 HR, 3 near-HR, 98.6 mph EV. Draws opposing starter Painter; PHI @ LAD.""", blast="high"),
            row("Will Smith", "R", "N/A", 86, "⭐ 🌕 💣", ["vs Painter"], """Worst Pickz favorite with 2 HR, 4 near-HR, 91.6 mph EV. Draws opposing starter Painter; PHI @ LAD.""", blast="high"),
            row("Max Muncy", "L", "N/A", 82, "🌕 💣", ["vs Painter"], """2 HR, 3 near-HR, 89.6 mph EV. Draws opposing starter Painter; PHI @ LAD.""", blast="high"),
            row("Trea Turner", "R", "N/A", 91, "🌕 💣", ["vs Yamamoto"], """3 HR, 4 near-HR, 93.4 mph EV. Draws opposing starter Yamamoto; PHI @ LAD.""", blast="high"),
            row("Brandon Marsh", "L", "N/A", 74, "💎", ["vs Yamamoto"], """0 HR, 98.5 mph EV. Draws opposing starter Yamamoto; PHI @ LAD.""", blast="good"),
            row("Kyle Schwarber", "L", "N/A", 78, "💎", ["vs Yamamoto"], """1 HR, 2 near-HR, 94.4 mph EV. Draws opposing starter Yamamoto; PHI @ LAD.""", blast="good"),
        ],
    },
    {
        "title": "SD @ WSH - Griffin Canning (R, SD) vs Zack Littell (R, WSH)",
        "description": "Nationals Park — HR environment -6% (stadium +3%, weather -9%). Griffin Canning: 0.41 HR risk (vs LHB +1.10, vs RHB -1.10; strongest LHB lane +1.10). Zack Littell: 0.61 HR risk (vs LHB +0.77, vs RHB +0.06; strongest LHB lane +0.77).",
        "rows": [
            row("CJ Abrams", "L", "N/A", 74, "⭐ 💎", ["vs Canning"], """Worst Pickz favorite with 1 HR, 1 near-HR, 92.1 mph EV. Draws opposing starter Canning; SD @ WSH.""", blast="good"),
            row("James Wood", "L", "N/A", 72, "💎", ["vs Canning"], """0 HR, 1 near-HR, 94.4 mph EV. Draws opposing starter Canning; SD @ WSH.""", blast="good"),
            row("Gavin Sheets", "L", "N/A", 71, "💎", ["vs Littell"], """1 HR, 1 near-HR, 89.4 mph EV. Draws opposing starter Littell; SD @ WSH.""", blast="good"),
            row("Ty France", "R", "N/A", 76, "💎", ["vs Littell"], """1 HR, 2 near-HR, 92.5 mph EV. Draws opposing starter Littell; SD @ WSH.""", blast="good"),
        ],
    },
    {
        "title": "SF @ COL - Robbie Ray 🧤 (R, SF) vs Tanner Gordon (R, COL)",
        "description": "Coors Field — HR environment +32% (stadium +20%, weather +12%). Robbie Ray: 1.22 HR risk (vs LHB -1.09, vs RHB +1.54; strongest RHB lane +1.54). Tanner Gordon: 0.40 HR risk (vs LHB +1.28, vs RHB -0.53; strongest LHB lane +1.28).",
        "rows": [
            row("Hunter Goodman", "R", "N/A", 71, "💎", ["vs Ray"], """1 HR, 1 near-HR, 89.0 mph EV. Draws opposing starter Ray; SF @ COL.""", blast="good"),
            row("Willi Castro", "S", "N/A", 67, "💎", ["vs Ray"], """0 HR, 1 near-HR, 90.7 mph EV. Draws opposing starter Ray; SF @ COL."""),
            row("Willy Adames", "R", "N/A", 95, "⭐ 🌕 💣", ["vs Gordon"], """Worst Pickz favorite with 4 HR, 4 near-HR, 93.1 mph EV. Draws opposing starter Gordon; SF @ COL.""", blast="high"),
            row("Rafael Devers", "L", "N/A", 88, "⭐ 🌕 💣", ["vs Gordon"], """Worst Pickz favorite with 1 HR, 4 near-HR, 98.5 mph EV. Draws opposing starter Gordon; SF @ COL.""", blast="high"),
            row("Casey Schmitt", "R", "N/A", 72, "💎", ["vs Gordon"], """1 HR, 1 near-HR, 90.4 mph EV. Draws opposing starter Gordon; SF @ COL.""", blast="good"),
        ],
    },
    {
        "title": "TOR @ BAL - Spencer Miles (R, TOR) vs Kyle Bradish (R, BAL)",
        "description": "Oriole Park — HR environment -20% (stadium -1%, weather -19%). Spencer Miles: no reliable HR-risk sample in today's export. Kyle Bradish: -0.03 HR risk (vs LHB -0.08, vs RHB +0.20; strongest RHB lane +0.20).",
        "rows": [
            row("Coby Mayo", "R", "+435", 78, "💎", ["vs Miles"], """1 HR, 1 near-HR, 96.2 mph EV. Draws opposing starter Miles; TOR @ BAL.""", blast="good"),
            row("Pete Alonso", "R", "+246", 96, "🌕 💣", ["vs Miles"], """3 HR, 3 near-HR, 99.7 mph EV. Draws opposing starter Miles; TOR @ BAL.""", blast="high"),
            row("Colton Cowser", "L", "+375", 80, "🌕 💣", ["vs Miles"], """2 HR, 3 near-HR, 88.4 mph EV. Draws opposing starter Miles; TOR @ BAL.""", blast="high"),
            row("Kazuma Okamoto", "R", "+296", 64, "⭐ 💎", ["vs Bradish"], """Worst Pickz favorite with 0 HR, 1 near-HR, 83.2 mph EV. Draws opposing starter Bradish; TOR @ BAL."""),
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

    out = ROOT / '_games-0531.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
