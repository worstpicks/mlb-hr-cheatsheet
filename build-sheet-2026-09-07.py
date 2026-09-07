#!/usr/bin/env python3
"""Generate games[] block for 2026-09-07 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Bobby Witt Jr. (R)",
    "Bryce Harper (L)",
    "Christian Yelich (L)",
    "Coby Mayo (R)",
    "Daylen Lile (L)",
    "Elly De La Cruz (S)",
    "Francisco Lindor (S)",
    "Heriberto Hernandez (R)",
    "Jake Bauers (L)",
    "Kazuma Okamoto (R)",
    "Kody Clemens (L)",
    "Kyle Schwarber (L)",
    "Lawrence Butler (L)",
    "Matt McLain (R)",
    "Max Muncy (L)",
    "Mickey Gasper (S)",
    "Pete Alonso (R)",
    "Pete Crow Armstrong (L)",
    "Rafael Devers (L)",
    "Ronald Acuna Jr. (R)",
}

GEMS = {
    "Alejandro Kirk (R)",
    "Brett Baty (L)",
    "JJ Bleday (L)",
    "Ketel Marte (S)",
    "Michael Conforto (L)",
    "Moises Ballesteros (L)",
    "Salvador Perez (R)",
    "Tyler Stephenson (R)",
}

PLAYER_TEAMS = {
    "Agustin Ramirez (R)": "MIA",
    "Alec Burleson (L)": "STL",
    "Alejandro Kirk (R)": "TOR",
    "Alex Freeland (S)": "LAD",
    "Andrew Knizner (R)": "SF",
    "Andrew Vaughn (R)": "MIL",
    "Bo Bichette (R)": "NYM",
    "Bobby Witt Jr. (R)": "KC",
    "Brett Baty (L)": "NYM",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "Carson Kelly (R)": "CHC",
    "Christian Yelich (L)": "MIL",
    "Coby Mayo (R)": "BAL",
    "Colton Cowser (L)": "BAL",
    "David Fry (R)": "CLE",
    "Daylen Lile (L)": "WSH",
    "Drake Baldwin (L)": "ATL",
    "Elly De La Cruz (S)": "CIN",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Lindor (S)": "NYM",
    "Garrett Mitchell (L)": "MIL",
    "George Springer (R)": "TOR",
    "Gleyber Torres (R)": "DET",
    "Grant McCray (L)": "SF",
    "Heriberto Hernandez (R)": "MIA",
    "JJ Bleday (L)": "CIN",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Jarren Duran (L)": "BOS",
    "Jeff McNeil (L)": "ATH",
    "Jesus Sanchez (L)": "TOR",
    "Joshua Baez (R)": "STL",
    "Juan Soto (L)": "NYM",
    "Kazuma Okamoto (R)": "TOR",
    "Keibert Ruiz (S)": "WSH",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Tucker (L)": "LAD",
    "Lane Thomas (R)": "ATL",
    "Lawrence Butler (L)": "ATH",
    "Leonardo Bernal (S)": "STL",
    "Manny Machado (R)": "SD",
    "Matt McLain (R)": "CIN",
    "Max Muncy (L)": "LAD",
    "Michael Conforto (L)": "CHC",
    "Mickey Gasper (S)": "BOS",
    "Miguel Amaya (R)": "CHC",
    "Moises Ballesteros (L)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Patrick Bailey (S)": "CLE",
    "Pete Alonso (R)": "BAL",
    "Pete Crow Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Riley Greene (L)": "DET",
    "Roman Anthony (L)": "BOS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan Jeffers (R)": "MIN",
    "Salvador Perez (R)": "KC",
    "Seiya Suzuki (R)": "CHC",
    "Thomas Saggese (R)": "STL",
    "Tim Tawa (R)": "ARI",
    "Trevor Larnach (L)": "MIN",
    "Tyler Stephenson (R)": "CIN",
    "Tyrone Taylor (R)": "CHC",
    "Vinnie Pasquantino (L)": "KC",
    "William Contreras (R)": "MIL",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_MATCHUPS = {
    ("WSH @ SD", "Irvin"),
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
        "title": "ARI @ KC - Jose Cabrera (R, ARI) vs Noah Cameron (L, KC)",
        "description": "Tail key data: Park boost +10% (stadium +12%, weather -1%). Cabrera (BAA vs LHB .214, vs RHB .316, HR/9 1.50). Cameron (HR risk -0.45, vs LHB +0.85, vs RHB -0.62).",
        "rows": [
            row("Salvador Perez", "R", "+475", 68, "💎", ["vs Cabrera"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.5 mph EV. limited split/risk sample.""", blast="good"),
            row("Bobby Witt Jr.", "R", "+460", 75, "⭐", ["vs Cabrera"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 97.1 mph EV. limited split/risk sample.""", blast="good"),
            row("Vinnie Pasquantino", "L", "+590", 77, "🌕 💣", ["vs Cabrera"], """2 HR, 3 near-HR, 89.8 mph EV. limited split/risk sample.""", blast="high"),
            row("Ketel Marte", "S", "+322", 58, "💎", ["vs Cameron"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.5 mph EV. Cameron SHB→RHB split -0.62, HR risk -0.45. tough split lane (-0.62); pitcher suppresses HR (-0.45).""", blast="good"),
            row("Tim Tawa", "R", "+630", 58, "", ["vs Cameron"], """0 HR, 91.7 mph EV. Cameron RHB split -0.62, HR risk -0.45. tough split lane (-0.62); pitcher suppresses HR (-0.45)."""),
        ],
    },
    {
        "title": "ATL @ PHI - Grant Holmes (R, ATL) vs Jesus Luzardo (L, PHI)",
        "description": "Tail key data: Park boost -4% (stadium +14%, weather -19%). Holmes (HR risk -0.19, vs LHB -0.12, vs RHB +0.40). Luzardo (HR risk -0.51, vs LHB -0.83, vs RHB -0.17).",
        "rows": [
            row("Bryce Harper", "L", "+430", 62, "⭐", ["vs Holmes"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.3 mph EV. Holmes LHB split -0.12, HR risk -0.19. slight split headwind (-0.12); pitcher risk below avg (-0.19).""", blast="good"),
            row("Kyle Schwarber", "L", "+240", 58, "⭐", ["vs Holmes"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 90.7 mph EV. Holmes LHB split -0.12, HR risk -0.19. slight split headwind (-0.12); pitcher risk below avg (-0.19).""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+541", 58, "🚀 ⭐", ["vs Luzardo"], """Worst Pickz Favorite. 0 HR, 100.8 mph EV. Luzardo RHB split -0.17, HR risk -0.51. slight split headwind (-0.17); pitcher suppresses HR (-0.51).""", blast="good"),
            row("Drake Baldwin", "L", "+820", 58, "", ["vs Luzardo"], """0 HR, 94.5 mph EV. Luzardo LHB split -0.83, HR risk -0.51. tough split lane (-0.83); pitcher suppresses HR (-0.51).""", blast="good"),
            row("Lane Thomas", "R", "+790", 58, "", ["vs Luzardo"], """1 HR, 1 near-HR, 91.4 mph EV. Luzardo RHB split -0.17, HR risk -0.51. slight split headwind (-0.17); pitcher suppresses HR (-0.51).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ MIL - Matthew Boyd (L, CHC) vs Robert Gasser (L, MIL)",
        "description": "Tail key data: Park boost -11% (stadium -3%, weather -8%). Boyd (HR risk 0.93, vs LHB -1.04, vs RHB +1.20). Gasser (HR risk 0.35, vs LHB -0.21, vs RHB +0.31).",
        "rows": [
            row("Jake Bauers", "L", "+490", 65, "⭐", ["vs Boyd"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.7 mph EV. Boyd LHB split -1.04, HR risk 0.93. tough split lane (-1.04); park/weather net drag (-11%).""", blast="good"),
            row("William Contreras", "R", "+630", 83, "", ["vs Boyd"], """1 HR, 2 near-HR, 95.2 mph EV. Boyd RHB split +1.20, HR risk 0.93. park/weather net drag (-11%).""", blast="good"),
            row("Christian Yelich", "L", "+870", 60, "⭐", ["vs Boyd"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 90.7 mph EV. Boyd LHB split -1.04, HR risk 0.93. tough split lane (-1.04); park/weather net drag (-11%).""", blast="good"),
            row("Garrett Mitchell", "L", "N/A", 63, "", ["vs Boyd"], """0 HR, 99.2 mph EV. Boyd LHB split -1.04, HR risk 0.93. tough split lane (-1.04); park/weather net drag (-11%).""", blast="good"),
            row("Andrew Vaughn", "R", "+570", 73, "", ["vs Boyd"], """0 HR, 92.0 mph EV. Boyd RHB split +1.20, HR risk 0.93. park/weather net drag (-11%); limited recent HR events.""", blast="good"),
            row("Pete Crow Armstrong", "L", "+390", 63, "⭐", ["vs Gasser"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.6 mph EV. Gasser LHB split -0.21, HR risk 0.35. slight split headwind (-0.21); park/weather net drag (-11%).""", blast="good"),
            row("Michael Conforto", "L", "N/A", 63, "💎", ["vs Gasser"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.6 mph EV. Gasser LHB split -0.21, HR risk 0.35. slight split headwind (-0.21); park/weather net drag (-11%).""", blast="good"),
            row("Seiya Suzuki", "R", "+497", 59, "", ["vs Gasser"], """1 HR, 1 near-HR, 87.3 mph EV. Gasser RHB split +0.31, HR risk 0.35. park/weather net drag (-11%); lighter EV form (87.3 mph).""", blast="good"),
            row("Tyrone Taylor", "R", "+750", 63, "", ["vs Gasser"], """1 HR, 1 near-HR, 91.5 mph EV. Gasser RHB split +0.31, HR risk 0.35. park/weather net drag (-11%).""", blast="good"),
            row("Carson Kelly", "R", "+620", 61, "", ["vs Gasser"], """1 HR, 1 near-HR, 89.8 mph EV. Gasser RHB split +0.31, HR risk 0.35. park/weather net drag (-11%).""", blast="good"),
            row("Miguel Amaya", "R", "N/A", 60, "", ["vs Gasser"], """1 HR, 2 near-HR, 87.6 mph EV. Gasser RHB split +0.31, HR risk 0.35. park/weather net drag (-11%); lighter EV form (87.6 mph).""", blast="good"),
        ],
    },
    {
        "title": "CIN @ LAD - Chase Burns (R, CIN) vs Emmet Sheehan (R, LAD)",
        "description": "Tail key data: Park boost +21% (stadium +18%, weather +3%). Burns (HR risk -0.16, vs LHB +0.81, vs RHB -1.16). Sheehan (season BAA .252).",
        "rows": [
            row("Max Muncy", "L", "+421", 68, "⭐", ["vs Burns"], """Worst Pickz Favorite. 0 HR, 94.5 mph EV. Burns LHB split +0.81, HR risk -0.16. pitcher risk below avg (-0.16); limited recent HR events.""", blast="good"),
            row("Mookie Betts", "R", "+560", 58, "", ["vs Burns"], """0 HR, 94.6 mph EV. Burns RHB split -1.16, HR risk -0.16. tough split lane (-1.16); pitcher risk below avg (-0.16).""", blast="good"),
            row("Kyle Tucker", "L", "+600", 69, "", ["vs Burns"], """1 HR, 1 near-HR, 90.1 mph EV. Burns LHB split +0.81, HR risk -0.16. pitcher risk below avg (-0.16).""", blast="good"),
            row("Alex Freeland", "S", "+900", 58, "", ["vs Burns"], """0 HR, 88.8 mph EV. Burns SHB→LHB split +0.81, HR risk -0.16. pitcher risk below avg (-0.16); limited recent HR events."""),
            row("Tyler Stephenson", "R", "+546", 79, "🌕 💣 💎", ["vs Sheehan"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.9 mph EV. limited split/risk sample.""", blast="high"),
            row("JJ Bleday", "L", "+500", 72, "💎", ["vs Sheehan"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.8 mph EV. limited split/risk sample.""", blast="good"),
            row("Matt McLain", "R", "+680", 69, "⭐", ["vs Sheehan"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 91.6 mph EV. limited split/risk sample.""", blast="good"),
            row("Elly De La Cruz", "S", "+500", 67, "⭐", ["vs Sheehan"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.4 mph EV. limited split/risk sample; limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CLE @ BAL - Joey Cantillo (L, CLE) vs Trevor Rogers (L, BAL)",
        "description": "Tail key data: Park boost -17% (stadium -8%, weather -9%). Cantillo (HR risk -0.60, vs LHB -0.29, vs RHB -0.29). Rogers (HR risk 0.32, vs LHB -1.36, vs RHB +0.66).",
        "rows": [
            row("Pete Alonso", "R", "+410", 58, "⭐", ["vs Cantillo"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.9 mph EV. Cantillo RHB split -0.29, HR risk -0.60. slight split headwind (-0.29); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Colton Cowser", "L", "+525", 58, "", ["vs Cantillo"], """1 HR, 1 near-HR, 88.3 mph EV. Cantillo LHB split -0.29, HR risk -0.60. slight split headwind (-0.29); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Coby Mayo", "R", "+582", 58, "⭐", ["vs Cantillo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 87.9 mph EV. Cantillo RHB split -0.29, HR risk -0.60. slight split headwind (-0.29); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Patrick Bailey", "S", "+650", 63, "", ["vs Rogers"], """0 HR, 96.0 mph EV. Rogers SHB→RHB split +0.66, HR risk 0.32. park/weather net drag (-17%); limited recent HR events.""", blast="good"),
            row("David Fry", "R", "+730", 58, "", ["vs Rogers"], """0 HR, 89.8 mph EV. Rogers RHB split +0.66, HR risk 0.32. park/weather net drag (-17%); limited recent HR events."""),
        ],
    },
    {
        "title": "LAA @ BOS - Grayson Rodriguez (R, LAA) vs Brayan Bello (R, BOS)",
        "description": "Tail key data: Park boost -2% (stadium -8%, weather +6%). Rodriguez (HR risk 0.26, vs LHB +0.93, vs RHB -0.61). Bello (BAA vs LHB .282, vs RHB .288, HR/9 1.01).",
        "rows": [
            row("Roman Anthony", "L", "+570", 73, "", ["vs Rodriguez"], """1 HR, 2 near-HR, 93.4 mph EV. Rodriguez LHB split +0.93, HR risk 0.26. park suppresses carry (-8%).""", blast="good"),
            row("Mickey Gasper", "S", "+630", 81, "⭐ 🌕 💣", ["vs Rodriguez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 93.5 mph EV. Rodriguez SHB→LHB split +0.93, HR risk 0.26. park suppresses carry (-8%).""", blast="high"),
            row("Jarren Duran", "L", "+630", 66, "", ["vs Rodriguez"], """0 HR, 93.5 mph EV. Rodriguez LHB split +0.93, HR risk 0.26. park suppresses carry (-8%); limited recent HR events.""", blast="good"),
            row("Zach Neto", "R", "+520", 66, "", ["vs Bello"], """1 HR, 1 near-HR, 95.9 mph EV. limited split/risk sample; park suppresses carry (-8%).""", blast="good"),
            row("Moises Ballesteros", "L", "+1040", 66, "💎", ["vs Bello"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.6 mph EV. limited split/risk sample; park suppresses carry (-8%).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ DET - Connor Prielipp (L, MIN) vs Troy Melton (R, DET)",
        "description": "Tail key data: Park boost -14% (stadium -10%, weather -4%). Prielipp (BAA vs LHB .287, vs RHB .246, HR/9 1.12). Melton (HR risk 0.39, vs LHB +0.88, vs RHB -0.24).",
        "rows": [
            row("Riley Greene", "L", "+470", 67, "🌕 💣", ["vs Prielipp"], """2 HR, 2 near-HR, 90.4 mph EV. limited split/risk sample; park/weather net drag (-14%).""", blast="high"),
            row("Gleyber Torres", "R", "+920", 58, "", ["vs Prielipp"], """0 HR, 1 near-HR, 94.4 mph EV. limited split/risk sample; park/weather net drag (-14%).""", blast="good"),
            row("Kody Clemens", "L", "+424", 71, "⭐", ["vs Melton"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.0 mph EV. Melton LHB split +0.88, HR risk 0.39. park/weather net drag (-14%).""", blast="good"),
            row("Trevor Larnach", "L", "+650", 65, "", ["vs Melton"], """0 HR, 1 near-HR, 93.7 mph EV. Melton LHB split +0.88, HR risk 0.39. park/weather net drag (-14%); limited recent HR events.""", blast="good"),
            row("Ryan Jeffers", "R", "+425", 77, "🌕 💣", ["vs Melton"], """2 HR, 3 near-HR, 96.2 mph EV. Melton RHB split -0.24, HR risk 0.39. slight split headwind (-0.24); park/weather net drag (-14%).""", blast="high"),
            row("Royce Lewis", "R", "+490", 58, "", ["vs Melton"], """0 HR, 1 near-HR, 93.4 mph EV. Melton RHB split -0.24, HR risk 0.39. slight split headwind (-0.24); park/weather net drag (-14%).""", blast="good"),
        ],
    },
    {
        "title": "NYM @ MIA - Jonah Tong (R, NYM) vs Eury Perez (R, MIA)",
        "description": "Tail key data: Park boost -12% (stadium -12%, weather +0%). Tong (HR risk -0.24, vs LHB -1.24, vs RHB +1.54). Perez (HR risk 0.82, vs LHB +0.63, vs RHB +0.62).",
        "rows": [
            row("Heriberto Hernandez", "R", "+523", 80, "⭐ 🌕 💣", ["vs Tong"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.3 mph EV. Tong RHB split +1.54, HR risk -0.24. pitcher risk below avg (-0.24); park/weather net drag (-12%).""", blast="high"),
            row("Agustin Ramirez", "R", "+465", 66, "", ["vs Tong"], """1 HR, 1 near-HR, 90.4 mph EV. Tong RHB split +1.54, HR risk -0.24. pitcher risk below avg (-0.24); park/weather net drag (-12%).""", blast="good"),
            row("Brett Baty", "L", "+850", 83, "💎", ["vs Perez"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 97.5 mph EV. Perez LHB split +0.63, HR risk 0.82. park/weather net drag (-12%).""", blast="good"),
            row("Juan Soto", "L", "+346", 76, "", ["vs Perez"], """1 HR, 2 near-HR, 93.6 mph EV. Perez LHB split +0.63, HR risk 0.82. park/weather net drag (-12%).""", blast="good"),
            row("Francisco Lindor", "S", "+470", 74, "⭐", ["vs Perez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.2 mph EV. Perez SHB→LHB split +0.63, HR risk 0.82. park/weather net drag (-12%).""", blast="good"),
            row("Bo Bichette", "R", "+880", 67, "", ["vs Perez"], """1 HR, 1 near-HR, 85.0 mph EV. Perez RHB split +0.62, HR risk 0.82. park/weather net drag (-12%); lighter EV form (85.0 mph).""", blast="good"),
        ],
    },
    {
        "title": "STL @ SF - Michael McGreevy (R, STL) vs Logan Webb (R, SF)",
        "description": "Tail key data: Park boost -18% (stadium -19%, weather +1%). McGreevy (HR risk 0.46, vs LHB +1.01, vs RHB -0.33). Webb (HR risk -0.78, vs LHB -0.20, vs RHB -0.51).",
        "rows": [
            row("Rafael Devers", "L", "+362", 91, "🚀 ⭐ 🌕 💣", ["vs McGreevy"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 104.2 mph EV. McGreevy LHB split +1.01, HR risk 0.46. park/weather net drag (-18%).""", blast="high"),
            row("Grant McCray", "L", "N/A", 73, "", ["vs McGreevy"], """1 HR, 2 near-HR, 92.5 mph EV. McGreevy LHB split +1.01, HR risk 0.46. park/weather net drag (-18%).""", blast="good"),
            row("Andrew Knizner", "R", "N/A", 58, "", ["vs McGreevy"], """0 HR, 1 near-HR, 92.0 mph EV. McGreevy RHB split -0.33, HR risk 0.46. slight split headwind (-0.33); park/weather net drag (-18%).""", blast="good"),
            row("Bryce Eldridge", "L", "+571", 58, "", ["vs McGreevy"], """0 HR, 83.6 mph EV. McGreevy LHB split +1.01, HR risk 0.46. park/weather net drag (-18%); limited recent HR events."""),
            row("Alec Burleson", "L", "+725", 58, "⭐", ["vs Webb"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 90.8 mph EV. Webb LHB split -0.20, HR risk -0.78. slight split headwind (-0.20); pitcher suppresses HR (-0.78)."""),
            row("Joshua Baez", "R", "+790", 58, "", ["vs Webb"], """0 HR, 95.7 mph EV. Webb RHB split -0.51, HR risk -0.78. tough split lane (-0.51); pitcher suppresses HR (-0.78).""", blast="good"),
            row("Leonardo Bernal", "S", "+1060", 58, "", ["vs Webb"], """1 HR, 1 near-HR, 96.0 mph EV. Webb SHB→LHB split -0.20, HR risk -0.78. slight split headwind (-0.20); pitcher suppresses HR (-0.78).""", blast="good"),
            row("Thomas Saggese", "R", "+1300", 58, "", ["vs Webb"], """0 HR, 1 near-HR, 90.8 mph EV. Webb RHB split -0.51, HR risk -0.78. tough split lane (-0.51); pitcher suppresses HR (-0.78)."""),
        ],
    },
    {
        "title": "TOR @ ATH - Dylan Cease (R, TOR) vs Jacob Lopez (L, ATH)",
        "description": "Tail key data: Park boost +27% (stadium +29%, weather -2%). Cease (HR risk -0.60, vs LHB +0.00, vs RHB -0.60). Lopez (HR risk 0.30, vs LHB -0.69, vs RHB +0.47).",
        "rows": [
            row("Lawrence Butler", "L", "+600", 66, "⭐", ["vs Cease"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.7 mph EV. Cease LHB split +0.00, HR risk -0.60. pitcher suppresses HR (-0.60).""", blast="good"),
            row("Zack Gelof", "R", "+520", 58, "", ["vs Cease"], """1 HR, 2 near-HR, 90.8 mph EV. Cease RHB split -0.60, HR risk -0.60. tough split lane (-0.60); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Jeff McNeil", "L", "+890", 72, "🌕 💣", ["vs Cease"], """2 HR, 2 near-HR, 92.2 mph EV. Cease LHB split +0.00, HR risk -0.60. pitcher suppresses HR (-0.60).""", blast="high"),
            row("Kazuma Okamoto", "R", "+319", 76, "⭐", ["vs Lopez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 92.7 mph EV. Lopez RHB split +0.47, HR risk 0.30.""", blast="good"),
            row("George Springer", "R", "+407", 72, "", ["vs Lopez"], """0 HR, 96.8 mph EV. Lopez RHB split +0.47, HR risk 0.30. limited recent HR events.""", blast="good"),
            row("Alejandro Kirk", "R", "+517", 69, "💎", ["vs Lopez"], """Worst Pickz Hidden Gem. 0 HR, 92.3 mph EV. Lopez RHB split +0.47, HR risk 0.30. limited recent HR events.""", blast="good"),
            row("Jesus Sanchez", "L", "N/A", 58, "", ["vs Lopez"], """0 HR, 90.2 mph EV. Lopez LHB split -0.69, HR risk 0.30. tough split lane (-0.69); limited recent HR events."""),
        ],
    },
    {
        "title": "WSH @ SD - Jake Irvin 🧤 (R, WSH) vs Nick Pivetta (R, SD)",
        "description": "Tail key data: Park boost -5% (stadium -6%, weather +1%). Irvin 🧤 (HR risk 1.56, vs LHB +1.40, vs RHB +0.82). Pivetta (HR risk -1.87, vs LHB -0.52, vs RHB -1.47).",
        "rows": [
            row("Fernando Tatis Jr.", "R", "+376", 88, "🌕 💣", ["vs Irvin"], """1 HR, 1 near-HR, 97.2 mph EV. Irvin RHB split +0.82, HR risk 1.56. park/weather net drag (-5%).""", blast="good"),
            row("Jackson Merrill", "L", "+390", 87, "🚀", ["vs Irvin"], """0 HR, 103.8 mph EV. Irvin LHB split +1.40, HR risk 1.56. park/weather net drag (-5%); limited recent HR events.""", blast="good"),
            row("Manny Machado", "R", "+426", 78, "", ["vs Irvin"], """1 HR, 1 near-HR, 86.3 mph EV. Irvin RHB split +0.82, HR risk 1.56. park/weather net drag (-5%); lighter EV form (86.3 mph).""", blast="good"),
            row("Daylen Lile", "L", "+532", 58, "⭐ 🌕 💣", ["vs Pivetta"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.0 mph EV. Pivetta LHB split -0.52, HR risk -1.87. tough split lane (-0.52); pitcher suppresses HR (-1.87).""", blast="high"),
            row("James Wood", "L", "+360", 58, "", ["vs Pivetta"], """0 HR, 92.8 mph EV. Pivetta LHB split -0.52, HR risk -1.87. tough split lane (-0.52); pitcher suppresses HR (-1.87).""", blast="good"),
            row("Keibert Ruiz", "S", "+700", 58, "", ["vs Pivetta"], """0 HR, 1 near-HR, 95.5 mph EV. Pivetta SHB→LHB split -0.52, HR risk -1.87. tough split lane (-0.52); pitcher suppresses HR (-1.87).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-07")

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

    out = ROOT / '_games-0907.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
