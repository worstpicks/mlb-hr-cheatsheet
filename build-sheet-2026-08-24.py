#!/usr/bin/env python3
"""Generate games[] block for 2026-08-24 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Adley Rutschman (S)",
    "Alex Bregman (R)",
    "Fernando Tatis Jr. (R)",
    "Jarren Duran (L)",
    "Junior Caminero (R)",
    "Mickey Moniak (L)",
    "Munetaka Murakami (L)",
    "Oneil Cruz (L)",
    "Pete Crow Armstrong (L)",
    "Rafael Devers (L)",
    "Ryan Vilade (R)",
    "Tyler Stephenson (R)",
    "Zach Neto (R)",
}

GEMS = {
    "Alan Roden (L)",
    "Ben Malgeri (R)",
    "Brock Rodden (S)",
    "Byron Buxton (R)",
    "Colson Montgomery (L)",
    "Colt Keith (L)",
    "Esmerlyn Valdez (R)",
    "Gabriel Moreno (R)",
    "Harry Ford (R)",
    "Jackson Merrill (L)",
    "Jo Adell (R)",
    "Mickey Gasper (S)",
    "Miguel Vargas (R)",
    "Moises Ballesteros (L)",
    "Royce Lewis (R)",
    "Wilyer Abreu (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BOS",
    "Agustin Ramirez (R)": "MIA",
    "Alan Roden (L)": "MIN",
    "Alec Bohm (R)": "PHI",
    "Alex Bregman (R)": "CHC",
    "Andres Chaparro (R)": "WSH",
    "Andrew Benintendi (L)": "CWS",
    "Andrew Pinckney (R)": "WSH",
    "Ben Malgeri (R)": "DET",
    "Braden Montgomery (S)": "CWS",
    "Brandon Nimmo (L)": "TEX",
    "Brock Rodden (S)": "SEA",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Buddy Kennedy (R)": "SF",
    "Byron Buxton (R)": "MIN",
    "Cal Raleigh (S)": "SEA",
    "Christian Moore (R)": "LAA",
    "Colson Montgomery (L)": "CWS",
    "Colt Keith (L)": "DET",
    "Derek Hill (R)": "PHI",
    "Drew Gilbert (L)": "SF",
    "Dylan Crews (R)": "WSH",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Fernando Tatis Jr. (R)": "SD",
    "Gabriel Moreno (R)": "ARI",
    "Griffin Conine (L)": "MIA",
    "Harry Ford (R)": "WSH",
    "Heriberto Hernandez (R)": "MIA",
    "Jackson Merrill (L)": "SD",
    "Jarren Duran (L)": "BOS",
    "Jo Adell (R)": "CLE",
    "Joc Pederson (L)": "TEX",
    "Jordan Lawlar (R)": "ARI",
    "Josh Bell (S)": "MIN",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Justin Foscue (R)": "TEX",
    "Kevin Alcantara (R)": "CHC",
    "Kyle Schwarber (L)": "PHI",
    "Lawrence Butler (L)": "ATH",
    "Max Muncy (R)": "ATH",
    "Michael Busch (L)": "CHC",
    "Mickey Gasper (S)": "BOS",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Moises Ballesteros (L)": "LAA",
    "Munetaka Murakami (L)": "CWS",
    "Oneil Cruz (L)": "PIT",
    "Owen Caissie (L)": "MIA",
    "Patrick Wisdom (R)": "SEA",
    "Pete Crow Armstrong (L)": "CHC",
    "Petey Halpin (L)": "CLE",
    "Rafael Devers (L)": "SF",
    "Royce Lewis (R)": "MIN",
    "Ryan Jeffers (R)": "MIN",
    "Ryan Vilade (R)": "TB",
    "Spencer Torkelson (R)": "DET",
    "Ty France (R)": "SD",
    "Tyler Stephenson (R)": "CIN",
    "Victor Bericoto (R)": "SF",
    "Willi Castro (S)": "COL",
    "Wilyer Abreu (L)": "BOS",
    "Xander Bogaerts (R)": "SD",
    "Zac Veen (L)": "COL",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("COL @ WSH", "Feltner"),
    ("MIN @ ATH", "Matthews"),
    ("MIN @ ATH", "Springs"),
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
        "title": "BOS @ MIA - Ranger Suarez (L, BOS) vs Sandy Alcantara (R, MIA)",
        "description": "Tail key data: Park boost -14% (stadium -13%, weather +0%). Suarez (HR risk -1.10, vs LHB -0.62, vs RHB -0.70). Alcantara (HR risk -1.02, vs LHB -0.35, vs RHB -0.97).",
        "rows": [
            row("Heriberto Hernandez", "R", "+562", 58, "", ["vs Suarez"], """1 HR, 1 near-HR, 92.6 mph EV. Suarez RHB split -0.70, HR risk -1.10. tough split lane (-0.70); pitcher suppresses HR (-1.10).""", blast="good"),
            row("Owen Caissie", "L", "N/A", 58, "", ["vs Suarez"], """0 HR, 89.4 mph EV. Suarez LHB split -0.62, HR risk -1.10. tough split lane (-0.62); pitcher suppresses HR (-1.10)."""),
            row("Griffin Conine", "L", "+630", 58, "", ["vs Suarez"], """0 HR, 90.5 mph EV. Suarez LHB split -0.62, HR risk -1.10. tough split lane (-0.62); pitcher suppresses HR (-1.10)."""),
            row("Agustin Ramirez", "R", "+825", 58, "", ["vs Suarez"], """0 HR, 92.6 mph EV. Suarez RHB split -0.70, HR risk -1.10. tough split lane (-0.70); pitcher suppresses HR (-1.10).""", blast="good"),
            row("Mickey Gasper", "S", "+1000", 65, "🌕 💣 💎", ["vs Alcantara"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 94.6 mph EV. Alcantara SHB→LHB split -0.35, HR risk -1.02. slight split headwind (-0.35); pitcher suppresses HR (-1.02).""", blast="high"),
            row("Wilyer Abreu", "L", "+500", 58, "💎", ["vs Alcantara"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.8 mph EV. Alcantara LHB split -0.35, HR risk -1.02. slight split headwind (-0.35); pitcher suppresses HR (-1.02).""", blast="good"),
            row("Adley Rutschman", "S", "+840", 58, "⭐", ["vs Alcantara"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.1 mph EV. Alcantara SHB→LHB split -0.35, HR risk -1.02. slight split headwind (-0.35); pitcher suppresses HR (-1.02).""", blast="good"),
            row("Jarren Duran", "L", "+780", 58, "⭐", ["vs Alcantara"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 89.4 mph EV. Alcantara LHB split -0.35, HR risk -1.02. slight split headwind (-0.35); pitcher suppresses HR (-1.02).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ ARI - Kevin Gausman (R, CHC) vs Merrill Kelly (R, ARI)",
        "description": "Tail key data: Park boost -9% (stadium -8%, weather +0%). Gausman (HR risk -0.31, vs LHB +0.16, vs RHB -0.54). Kelly (HR risk 0.81, vs LHB +1.01, vs RHB -0.17).",
        "rows": [
            row("Gabriel Moreno", "R", "+900", 58, "💎", ["vs Gausman"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.8 mph EV. Gausman RHB split -0.54, HR risk -0.31. tough split lane (-0.54); pitcher risk below avg (-0.31).""", blast="good"),
            row("Jordan Lawlar", "R", "+616", 58, "", ["vs Gausman"], """1 HR, 1 near-HR, 90.3 mph EV. Gausman RHB split -0.54, HR risk -0.31. tough split lane (-0.54); pitcher risk below avg (-0.31).""", blast="good"),
            row("Alex Bregman", "R", "+710", 80, "⭐ 🌕 💣", ["vs Kelly"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.5 mph EV. Kelly RHB split -0.17, HR risk 0.81. slight split headwind (-0.17); park/weather net drag (-9%).""", blast="high"),
            row("Pete Crow Armstrong", "L", "+343", 90, "⭐ 🌕 💣", ["vs Kelly"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 87.8 mph EV. Kelly LHB split +1.01, HR risk 0.81. park/weather net drag (-9%); lighter EV form (87.8 mph).""", blast="high"),
            row("Kevin Alcantara", "R", "N/A", 66, "", ["vs Kelly"], """0 HR, 97.2 mph EV. Kelly RHB split -0.17, HR risk 0.81. slight split headwind (-0.17); park/weather net drag (-9%).""", blast="good"),
            row("Michael Busch", "L", "+542", 74, "", ["vs Kelly"], """0 HR, 2 near-HR, 91.9 mph EV. Kelly LHB split +1.01, HR risk 0.81. park/weather net drag (-9%).""", blast="good"),
        ],
    },
    {
        "title": "CIN @ SF - Chase Burns (R, CIN) vs Carson Whisenhunt (L, SF)",
        "description": "Tail key data: Park boost -17% (stadium -17%, weather +0%). Burns (HR risk -0.89, vs LHB -0.18, vs RHB -0.97). Whisenhunt (BAA vs LHB .167, vs RHB .330, HR/9 1.41).",
        "rows": [
            row("Rafael Devers", "L", "+535", 58, "⭐", ["vs Burns"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.3 mph EV. Burns LHB split -0.18, HR risk -0.89. slight split headwind (-0.18); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Drew Gilbert", "L", "+1100", 58, "", ["vs Burns"], """1 HR, 2 near-HR, 87.9 mph EV. Burns LHB split -0.18, HR risk -0.89. slight split headwind (-0.18); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Bryce Eldridge", "L", "+630", 58, "", ["vs Burns"], """1 HR, 1 near-HR, 86.3 mph EV. Burns LHB split -0.18, HR risk -0.89. slight split headwind (-0.18); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Victor Bericoto", "R", "N/A", 58, "", ["vs Burns"], """0 HR, 1 near-HR, 93.5 mph EV. Burns RHB split -0.97, HR risk -0.89. tough split lane (-0.97); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Buddy Kennedy", "R", "+1500", 58, "🚀", ["vs Burns"], """0 HR, 102.1 mph EV. Burns RHB split -0.97, HR risk -0.89. tough split lane (-0.97); pitcher suppresses HR (-0.89).""", blast="good"),
            row("Elly De La Cruz", "S", "+650", 58, "", ["vs Whisenhunt"], """0 HR, 90.1 mph EV. limited split/risk sample; park/weather net drag (-17%)."""),
            row("Tyler Stephenson", "R", "+680", 58, "⭐", ["vs Whisenhunt"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 88.9 mph EV. limited split/risk sample; park/weather net drag (-17%)."""),
        ],
    },
    {
        "title": "CLE @ LAA - Parker Messick (L, CLE) vs George Klassen (R, LAA)",
        "description": "Tail key data: Park boost -4% (stadium -9%, weather +5%). Messick (HR risk -0.81, vs LHB -0.55, vs RHB -0.61). Klassen (HR risk -0.13, vs LHB +0.01, vs RHB -0.15).",
        "rows": [
            row("Moises Ballesteros", "L", "+710", 58, "💎", ["vs Messick"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.7 mph EV. Messick LHB split -0.55, HR risk -0.81. tough split lane (-0.55); pitcher suppresses HR (-0.81).""", blast="good"),
            row("Zach Neto", "R", "+366", 58, "⭐", ["vs Messick"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.4 mph EV. Messick RHB split -0.61, HR risk -0.81. tough split lane (-0.61); pitcher suppresses HR (-0.81).""", blast="good"),
            row("Christian Moore", "R", "+800", 58, "", ["vs Messick"], """0 HR, 1 near-HR, 91.1 mph EV. Messick RHB split -0.61, HR risk -0.81. tough split lane (-0.61); pitcher suppresses HR (-0.81)."""),
            row("Jo Adell", "R", "+493", 58, "💎", ["vs Klassen"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 96.8 mph EV. Klassen RHB split -0.15, HR risk -0.13. slight split headwind (-0.15); pitcher risk below avg (-0.13).""", blast="good"),
            row("Petey Halpin", "L", "+529", 58, "", ["vs Klassen"], """1 HR, 1 near-HR, 89.1 mph EV. Klassen LHB split +0.01, HR risk -0.13. pitcher risk below avg (-0.13); park suppresses carry (-9%).""", blast="good"),
        ],
    },
    {
        "title": "COL @ WSH - Ryan Feltner 🧤 (R, COL) vs Cade Cavalli (R, WSH)",
        "description": "Tail key data: Park boost -7% (stadium +2%, weather -9%). Feltner 🧤 (HR risk 1.00, vs LHB +0.46, vs RHB +0.98). Cavalli (HR risk 0.53, vs LHB +0.23, vs RHB +0.50).",
        "rows": [
            row("Dylan Crews", "R", "+500", 79, "", ["vs Feltner"], """0 HR, 97.4 mph EV. Feltner RHB split +0.98, HR risk 1.00. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
            row("Andres Chaparro", "R", "+496", 81, "", ["vs Feltner"], """1 HR, 1 near-HR, 92.9 mph EV. Feltner RHB split +0.98, HR risk 1.00. park/weather net drag (-7%).""", blast="good"),
            row("Andrew Pinckney", "R", "N/A", 70, "", ["vs Feltner"], """0 HR, 90.9 mph EV. Feltner RHB split +0.98, HR risk 1.00. park/weather net drag (-7%); limited recent HR events."""),
            row("Harry Ford", "R", "N/A", 78, "💎", ["vs Feltner"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 89.1 mph EV. Feltner RHB split +0.98, HR risk 1.00. park/weather net drag (-7%).""", blast="good"),
            row("Willi Castro", "S", "+720", 72, "", ["vs Cavalli"], """0 HR, 2 near-HR, 97.7 mph EV. Cavalli SHB→RHB split +0.50, HR risk 0.53. park/weather net drag (-7%).""", blast="good"),
            row("Zac Veen", "L", "+900", 70, "", ["vs Cavalli"], """1 HR, 1 near-HR, 93.8 mph EV. Cavalli LHB split +0.23, HR risk 0.53. park/weather net drag (-7%).""", blast="good"),
            row("Mickey Moniak", "L", "+500", 65, "⭐", ["vs Cavalli"], """Worst Pickz Favorite. 0 HR, 94.1 mph EV. Cavalli LHB split +0.23, HR risk 0.53. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIN @ ATH - Zebby Matthews 🧤 (R, MIN) vs Jeffrey Springs 🧤 (L, ATH)",
        "description": "Tail key data: Park boost +39% (stadium +29%, weather +10%). Matthews 🧤 (HR risk 0.98, vs LHB +1.22, vs RHB +0.10). Springs 🧤 (HR risk 1.32, vs LHB +1.16, vs RHB +0.72).",
        "rows": [
            row("Zack Gelof", "R", "+492", 88, "🌕 💣", ["vs Matthews"], """2 HR, 2 near-HR, 85.6 mph EV. Matthews RHB split +0.10, HR risk 0.98. lighter EV form (85.6 mph).""", blast="high"),
            row("Lawrence Butler", "L", "+511", 79, "", ["vs Matthews"], """0 HR, 86.5 mph EV. Matthews LHB split +1.22, HR risk 0.98. limited recent HR events; lighter EV form (86.5 mph)."""),
            row("Max Muncy", "R", "+575", 91, "🌕 💣", ["vs Matthews"], """1 HR, 3 near-HR, 92.4 mph EV. Matthews RHB split +0.10, HR risk 0.98.""", blast="good"),
            row("Byron Buxton", "R", "+201", 89, "🌕 💣 💎", ["vs Springs"], """Worst Pickz Hidden Gem. 0 HR, 93.7 mph EV. Springs RHB split +0.72, HR risk 1.32. limited recent HR events.""", blast="good"),
            row("Alan Roden", "L", "+800", 92, "🌕 💣 💎", ["vs Springs"], """Worst Pickz Hidden Gem. 0 HR, 99.8 mph EV. Springs LHB split +1.16, HR risk 1.32. limited recent HR events.""", blast="good"),
            row("Ryan Jeffers", "R", "+401", 88, "🌕 💣", ["vs Springs"], """0 HR, 92.9 mph EV. Springs RHB split +0.72, HR risk 1.32. limited recent HR events.""", blast="good"),
            row("Royce Lewis", "R", "+320", 84, "💎", ["vs Springs"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 81.7 mph EV. Springs RHB split +0.72, HR risk 1.32. lighter EV form (81.7 mph).""", blast="good"),
            row("Josh Bell", "S", "+409", 91, "🌕 💣", ["vs Springs"], """1 HR, 1 near-HR, 87.3 mph EV. Springs SHB→LHB split +1.16, HR risk 1.32. lighter EV form (87.3 mph).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ SEA - Zack Wheeler (R, PHI) vs Logan Gilbert (R, SEA)",
        "description": "Tail key data: Park boost -2% (stadium +0%, weather -2%). Wheeler (HR risk 0.15, vs LHB +0.88, vs RHB -0.76). Gilbert (HR risk 0.52, vs LHB +0.09, vs RHB +0.75).",
        "rows": [
            row("Cal Raleigh", "S", "+450", 60, "", ["vs Wheeler"], """0 HR, 1 near-HR, 91.6 mph EV. Wheeler SHB→LHB split +0.88, HR risk 0.15. limited recent HR events."""),
            row("Brock Rodden", "S", "N/A", 60, "💎", ["vs Wheeler"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 91.8 mph EV. Wheeler SHB→LHB split +0.88, HR risk 0.15. limited recent HR events."""),
            row("Patrick Wisdom", "R", "+600", 58, "", ["vs Wheeler"], """0 HR, 1 near-HR, 92.3 mph EV. Wheeler RHB split -0.76, HR risk 0.15. tough split lane (-0.76); limited recent HR events.""", blast="good"),
            row("Julio Rodriguez", "R", "+555", 58, "", ["vs Wheeler"], """0 HR, 87.1 mph EV. Wheeler RHB split -0.76, HR risk 0.15. tough split lane (-0.76); limited recent HR events."""),
            row("Alec Bohm", "R", "+940", 75, "", ["vs Gilbert"], """1 HR, 1 near-HR, 93.5 mph EV. Gilbert RHB split +0.75, HR risk 0.52.""", blast="good"),
            row("Bryce Harper", "L", "+458", 67, "", ["vs Gilbert"], """1 HR, 1 near-HR, 90.5 mph EV. Gilbert LHB split +0.09, HR risk 0.52.""", blast="good"),
            row("Kyle Schwarber", "L", "+280", 68, "", ["vs Gilbert"], """1 HR, 1 near-HR, 91.1 mph EV. Gilbert LHB split +0.09, HR risk 0.52.""", blast="good"),
            row("Derek Hill", "R", "N/A", 72, "", ["vs Gilbert"], """1 HR, 1 near-HR, 90.8 mph EV. Gilbert RHB split +0.75, HR risk 0.52.""", blast="good"),
        ],
    },
    {
        "title": "PIT @ SD - Braxton Ashcraft (R, PIT) vs Robbie Ray (L, SD)",
        "description": "Tail key data: Park boost +7% (stadium -4%, weather +11%). Ashcraft (HR risk 0.12, vs LHB +0.21, vs RHB -0.12). Ray (HR risk -0.05, vs LHB -1.01, vs RHB +0.43).",
        "rows": [
            row("Fernando Tatis Jr.", "R", "+468", 68, "⭐", ["vs Ashcraft"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 98.7 mph EV. Ashcraft RHB split -0.12, HR risk 0.12. slight split headwind (-0.12).""", blast="good"),
            row("Jackson Merrill", "L", "+480", 62, "💎", ["vs Ashcraft"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.6 mph EV. Ashcraft LHB split +0.21, HR risk 0.12. limited recent HR events.""", blast="good"),
            row("Ty France", "R", "+640", 58, "", ["vs Ashcraft"], """0 HR, 92.8 mph EV. Ashcraft RHB split -0.12, HR risk 0.12. slight split headwind (-0.12); limited recent HR events.""", blast="good"),
            row("Xander Bogaerts", "R", "+880", 58, "", ["vs Ashcraft"], """0 HR, 91.7 mph EV. Ashcraft RHB split -0.12, HR risk 0.12. slight split headwind (-0.12); limited recent HR events."""),
            row("Esmerlyn Valdez", "R", "+400", 66, "💎", ["vs Ray"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 94.8 mph EV. Ray RHB split +0.43, HR risk -0.05. pitcher risk below avg (-0.05).""", blast="good"),
            row("Oneil Cruz", "L", "+425", 58, "🚀 ⭐", ["vs Ray"], """Worst Pickz Favorite. 0 HR, 103.4 mph EV. Ray LHB split -1.01, HR risk -0.05. tough split lane (-1.01); pitcher risk below avg (-0.05).""", blast="good"),
            row("Bryan Reynolds", "S", "+600", 64, "", ["vs Ray"], """0 HR, 2 near-HR, 93.1 mph EV. Ray SHB→RHB split +0.43, HR risk -0.05. pitcher risk below avg (-0.05).""", blast="good"),
        ],
    },
    {
        "title": "TB @ DET - Drew Rasmussen (R, TB) vs Framber Valdez (L, DET)",
        "description": "Tail key data: Park boost -4% (stadium -11%, weather +6%). Rasmussen (HR risk -1.06, vs LHB -0.67, vs RHB -0.53). Valdez (HR risk -0.58, vs LHB -0.87, vs RHB -0.21).",
        "rows": [
            row("Colt Keith", "L", "+680", 58, "💎", ["vs Rasmussen"], """Worst Pickz Hidden Gem. 0 HR, 96.0 mph EV. Rasmussen LHB split -0.67, HR risk -1.06. tough split lane (-0.67); pitcher suppresses HR (-1.06).""", blast="good"),
            row("Spencer Torkelson", "R", "+520", 58, "", ["vs Rasmussen"], """0 HR, 1 near-HR, 95.2 mph EV. Rasmussen RHB split -0.53, HR risk -1.06. tough split lane (-0.53); pitcher suppresses HR (-1.06).""", blast="good"),
            row("Ben Malgeri", "R", "N/A", 58, "💎", ["vs Rasmussen"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.9 mph EV. Rasmussen RHB split -0.53, HR risk -1.06. tough split lane (-0.53); pitcher suppresses HR (-1.06).""", blast="good"),
            row("Ryan Vilade", "R", "+680", 74, "⭐ 🌕 💣", ["vs Valdez"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 95.4 mph EV. Valdez RHB split -0.21, HR risk -0.58. slight split headwind (-0.21); pitcher suppresses HR (-0.58).""", blast="high"),
            row("Junior Caminero", "R", "+311", 58, "⭐", ["vs Valdez"], """Worst Pickz Favorite. 0 HR, 94.9 mph EV. Valdez RHB split -0.21, HR risk -0.58. slight split headwind (-0.21); pitcher suppresses HR (-0.58).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ CWS - Kumar Rocker (R, TEX) vs José Urquidy (R, CWS)",
        "description": "Tail key data: Park boost -15% (stadium -5%, weather -10%). Rocker (HR risk 0.61, vs LHB +0.48, vs RHB +0.35). Urquidy (BAA vs LHB .229, vs RHB .412, HR/9 1.12).",
        "rows": [
            row("Munetaka Murakami", "L", "+320", 82, "⭐ 🌕 💣", ["vs Rocker"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.9 mph EV. Rocker LHB split +0.48, HR risk 0.61. park/weather net drag (-15%).""", blast="high"),
            row("Braden Montgomery", "S", "+800", 68, "", ["vs Rocker"], """1 HR, 1 near-HR, 90.6 mph EV. Rocker SHB→LHB split +0.48, HR risk 0.61. park/weather net drag (-15%).""", blast="good"),
            row("Colson Montgomery", "L", "+390", 69, "💎", ["vs Rocker"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.0 mph EV. Rocker LHB split +0.48, HR risk 0.61. park/weather net drag (-15%).""", blast="good"),
            row("Miguel Vargas", "R", "+457", 64, "💎", ["vs Rocker"], """Worst Pickz Hidden Gem. 0 HR, 93.6 mph EV. Rocker RHB split +0.35, HR risk 0.61. park/weather net drag (-15%); limited recent HR events.""", blast="good"),
            row("Andrew Benintendi", "L", "+600", 60, "", ["vs Rocker"], """0 HR, 1 near-HR, 90.6 mph EV. Rocker LHB split +0.48, HR risk 0.61. park/weather net drag (-15%); limited recent HR events."""),
            row("Brandon Nimmo", "L", "+575", 58, "", ["vs Urquidy"], """0 HR, 92.1 mph EV. limited split/risk sample; park/weather net drag (-15%).""", blast="good"),
            row("Joc Pederson", "L", "+361", 58, "", ["vs Urquidy"], """0 HR, 1 near-HR, 92.2 mph EV. limited split/risk sample; park/weather net drag (-15%).""", blast="good"),
            row("Justin Foscue", "R", "N/A", 58, "", ["vs Urquidy"], """0 HR, 2 near-HR, 83.9 mph EV. limited split/risk sample; park/weather net drag (-15%).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-24")

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

    out = ROOT / '_games-0824.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
