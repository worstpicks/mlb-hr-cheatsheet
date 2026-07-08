#!/usr/bin/env python3
"""Generate games[] block for 2026-07-08 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Bobby Witt Jr. (R)",
    "Brandon Lowe (L)",
    "Curtis Mead (R)",
    "Dalton Rushing (L)",
    "Garrett Mitchell (L)",
    "Heriberto Hernandez (R)",
    "Hunter Feduccia (L)",
    "James Wood (L)",
    "Jordan Walker (R)",
    "Juan Soto (L)",
    "Kody Clemens (L)",
    "Matt Olson (L)",
    "Max Kepler (L)",
    "Nick Kurtz (L)",
    "Owen Caissie (L)",
    "Pete Crow-Armstrong (L)",
    "Rafael Devers (L)",
    "Ryan O'Hearn (L)",
    "Willson Contreras (R)",
}

GEMS = {
    "Carter Jensen (L)",
    "Jonathan Aranda (L)",
    "Josh Bell (S)",
    "Kerry Carpenter (L)",
    "Kyle Karros (R)",
    "Kyle Stowers (L)",
    "Max Schuemann (R)",
    "Otto Lopez (R)",
    "Samuel Basallo (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BAL",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Bryce Harper (L)": "PHI",
    "Cal Raleigh (S)": "SEA",
    "Cam Smith (R)": "HOU",
    "Carlos Cortes (L)": "ATH",
    "Carson Benge (L)": "NYM",
    "Carter Jensen (L)": "KC",
    "Colson Montgomery (L)": "CWS",
    "Curtis Mead (R)": "WSH",
    "Dalton Rushing (L)": "LAD",
    "Dansby Swanson (R)": "CHC",
    "David Fry (R)": "CLE",
    "Derek Hill (R)": "PHI",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Edmundo Sosa (R)": "PHI",
    "Endy Rodriguez (S)": "PIT",
    "Francisco Lindor (S)": "NYM",
    "Freddie Freeman (L)": "LAD",
    "Garrett Mitchell (L)": "MIL",
    "Gary Sanchez (R)": "MIL",
    "Heliot Ramos (R)": "SF",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Feduccia (L)": "TB",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake Bauers (L)": "MIL",
    "Jake Cronenworth (L)": "SD",
    "James Wood (L)": "WSH",
    "Jarren Duran (L)": "BOS",
    "Joc Pederson (L)": "TEX",
    "Jonah Heim (S)": "ATH",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Jose Siri (R)": "LAA",
    "Josh Bell (S)": "MIN",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Kahlil Watson (L)": "CLE",
    "Kerry Carpenter (L)": "DET",
    "Ketel Marte (S)": "ARI",
    "Kevin McGonigle (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Stowers (L)": "MIA",
    "Lars Nootbaar (L)": "STL",
    "Luis Garcia Jr. (L)": "WSH",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Max Muncy (L)": "LAD",
    "Max Schuemann (R)": "NYY",
    "Mickey Moniak (L)": "COL",
    "Miguel Vargas (R)": "CWS",
    "Mitch Garver (R)": "SEA",
    "Mookie Betts (R)": "LAD",
    "Nelson Velazquez (R)": "STL",
    "Nick Kurtz (L)": "ATH",
    "Otto Lopez (R)": "MIA",
    "Owen Caissie (L)": "MIA",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rafael Devers (L)": "SF",
    "Randal Grichuk (R)": "CWS",
    "Riley Greene (L)": "DET",
    "Ryan O'Hearn (L)": "PIT",
    "Samuel Basallo (L)": "BAL",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Trent Grisham (L)": "NYY",
    "Trevor Larnach (L)": "MIN",
    "Tristan Gray (L)": "MIN",
    "Tyler O'Neill (R)": "BAL",
    "Victor Mesa Jr. (L)": "TB",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Yordan Alvarez (L)": "HOU",
    "Zach Dezenzo (R)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("ATH @ DET", "Springs"),
    ("CHC @ BAL", "Kremer"),
    ("COL @ LAD", "Sasaki"),
    ("KC @ NYM", "Scott"),
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
    if (game_key, chip) not in BUM_MATCHUPS:
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
        "title": "ARI @ SD - Jose Cabrera (R, ARI) vs Michael King (R, SD)",
        "description": "Tail key data: Park boost -3% (stadium -5%, weather +2%). Cabrera (HR risk 0.89, vs LHB +1.00, vs RHB +0.43). King (HR risk -0.60, vs LHB -0.52, vs RHB -0.29).",
        "rows": [
            row("Manny Machado", "R", "+390", 89, "🌕 💣", ["vs Cabrera"], """2 HR, 3 near-HR, 92.7 mph EV. Cabrera RHB split +0.43, HR risk 0.89.""", blast="high"),
            row("Jake Cronenworth", "L", "+800", 78, "", ["vs Cabrera"], """1 HR, 1 near-HR, 91.7 mph EV. Cabrera LHB split +1.00, HR risk 0.89.""", blast="good"),
            row("Max Kepler", "L", "+561", 58, "⭐", ["vs King"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 88.5 mph EV. King LHB split -0.52, HR risk -0.60. tough split lane (-0.52); pitcher suppresses HR (-0.60).""", blast="good"),
            row("Ketel Marte", "S", "+369", 67, "🌕 💣", ["vs King"], """2 HR, 3 near-HR, 92.9 mph EV. King RHB split -0.29, HR risk -0.60. slight split headwind (-0.29); pitcher suppresses HR (-0.60).""", blast="high"),
        ],
    },
    {
        "title": "ATH @ DET - Jeffrey Springs 🧤 (L, ATH) vs Troy Melton (R, DET)",
        "description": "Tail key data: Park boost +0% (stadium -11%, weather +11%). Springs 🧤 (HR risk 1.38, vs LHB -0.27, vs RHB +2.14). Melton (HR risk 0.10, vs LHB +0.60, vs RHB -0.86).",
        "rows": [
            row("Riley Greene", "L", "+400", 73, "", ["vs Springs"], """0 HR, 1 near-HR, 92.9 mph EV. Springs LHB split -0.27, HR risk 1.38. slight split headwind (-0.27); park suppresses carry (-11%).""", blast="good"),
            row("Kevin McGonigle", "L", "+600", 67, "", ["vs Springs"], """0 HR, 1 near-HR, 90.8 mph EV. Springs LHB split -0.27, HR risk 1.38. slight split headwind (-0.27); park suppresses carry (-11%)."""),
            row("Kerry Carpenter", "L", "N/A", 70, "💎", ["vs Springs"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 88.4 mph EV. Springs LHB split -0.27, HR risk 1.38. slight split headwind (-0.27); park suppresses carry (-11%).""", blast="good"),
            row("Nick Kurtz", "L", "+300", 70, "⭐", ["vs Melton"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.3 mph EV. Melton LHB split +0.60, HR risk 0.10. park suppresses carry (-11%).""", blast="good"),
            row("Shea Langeliers", "R", "+330", 58, "", ["vs Melton"], """0 HR, 92.4 mph EV. Melton RHB split -0.86, HR risk 0.10. tough split lane (-0.86); park suppresses carry (-11%).""", blast="good"),
            row("Jonah Heim", "S", "+560", 63, "", ["vs Melton"], """1 HR, 1 near-HR, 88.5 mph EV. Melton RHB split -0.86, HR risk 0.10. tough split lane (-0.86); park suppresses carry (-11%).""", blast="good"),
            row("Carlos Cortes", "L", "+875", 58, "", ["vs Melton"], """0 HR, 89.5 mph EV. Melton LHB split +0.60, HR risk 0.10. park suppresses carry (-11%); limited recent HR events."""),
        ],
    },
    {
        "title": "ATL @ PIT - Grant Holmes (R, ATL) vs Jared Jones (R, PIT)",
        "description": "Tail key data: Park boost -3% (stadium -15%, weather +12%). Holmes (HR risk 0.04, vs LHB -0.11, vs RHB +0.33). Jones (HR risk -0.04, vs LHB +0.21, vs RHB -0.24).",
        "rows": [
            row("Brandon Lowe", "L", "+360", 77, "⭐ 🌕 💣", ["vs Holmes"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 99.4 mph EV. Holmes LHB split -0.11, HR risk 0.04. slight split headwind (-0.11); park suppresses carry (-15%).""", blast="high"),
            row("Ryan O'Hearn", "L", "+540", 76, "⭐ 🌕 💣", ["vs Holmes"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 91.3 mph EV. Holmes LHB split -0.11, HR risk 0.04. slight split headwind (-0.11); park suppresses carry (-15%).""", blast="high"),
            row("Endy Rodriguez", "S", "+750", 67, "", ["vs Holmes"], """1 HR, 1 near-HR, 96.6 mph EV. Holmes RHB split +0.33, HR risk 0.04. park suppresses carry (-15%).""", blast="good"),
            row("Matt Olson", "L", "+325", 76, "⭐ 🌕 💣", ["vs Jones"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 92.6 mph EV. Jones LHB split +0.21, HR risk -0.04. pitcher risk below avg (-0.04); park suppresses carry (-15%).""", blast="high"),
            row("Drake Baldwin", "L", "+470", 58, "", ["vs Jones"], """0 HR, 89.0 mph EV. Jones LHB split +0.21, HR risk -0.04. pitcher risk below avg (-0.04); park suppresses carry (-15%)."""),
        ],
    },
    {
        "title": "BOS @ CWS - Jake Bennett (L, BOS) vs Davis Martin (R, CWS)",
        "description": "Tail key data: Park boost +10% (stadium +3%, weather +7%). Bennett (HR risk -0.79, vs LHB -1.79, vs RHB -0.06). Martin (HR risk -0.45, vs LHB -0.35, vs RHB -0.18).",
        "rows": [
            row("Miguel Vargas", "R", "+340", 58, "", ["vs Bennett"], """0 HR, 94.2 mph EV. Bennett RHB split -0.06, HR risk -0.79. slight split headwind (-0.06); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Randal Grichuk", "R", "+423", 58, "", ["vs Bennett"], """1 HR, 2 near-HR, 89.5 mph EV. Bennett RHB split -0.06, HR risk -0.79. slight split headwind (-0.06); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Colson Montgomery", "L", "+350", 58, "", ["vs Bennett"], """1 HR, 1 near-HR, 79.8 mph EV. Bennett LHB split -1.79, HR risk -0.79. tough split lane (-1.79); pitcher suppresses HR (-0.79).""", blast="good"),
            row("Willson Contreras", "R", "+380", 71, "⭐ 🌕 💣", ["vs Martin"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.8 mph EV. Martin RHB split -0.18, HR risk -0.45. slight split headwind (-0.18); pitcher suppresses HR (-0.45).""", blast="high"),
            row("Jarren Duran", "L", "+500", 58, "", ["vs Martin"], """1 HR, 2 near-HR, 87.4 mph EV. Martin LHB split -0.35, HR risk -0.45. slight split headwind (-0.35); pitcher suppresses HR (-0.45).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ BAL - Colin Rea (R, CHC) vs Dean Kremer 🧤 (R, BAL)",
        "description": "Tail key data: Park boost +9% (stadium -1%, weather +10%). Rea (HR risk 0.03, vs LHB -0.48, vs RHB +0.70). Kremer 🧤 (HR risk 1.44, vs LHB +0.83, vs RHB +1.43).",
        "rows": [
            row("Samuel Basallo", "L", "+333", 73, "🌕 💣 💎", ["vs Rea"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 97.6 mph EV. Rea LHB split -0.48, HR risk 0.03. tough split lane (-0.48).""", blast="high"),
            row("Tyler O'Neill", "R", "N/A", 69, "", ["vs Rea"], """0 HR, 1 near-HR, 96.5 mph EV. Rea RHB split +0.70, HR risk 0.03. limited recent HR events.""", blast="good"),
            row("Adley Rutschman", "S", "+463", 58, "", ["vs Rea"], """0 HR, 89.5 mph EV. Rea RHB split +0.70, HR risk 0.03. limited recent HR events."""),
            row("Dansby Swanson", "R", "+480", 92, "🌕 💣", ["vs Kremer"], """1 HR, 1 near-HR, 95.0 mph EV. Kremer RHB split +1.43, HR risk 1.44.""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+280", 83, "⭐", ["vs Kremer"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 87.9 mph EV. Kremer LHB split +0.83, HR risk 1.44. lighter EV form (87.9 mph).""", blast="good"),
            row("Ian Happ", "S", "+340", 84, "", ["vs Kremer"], """0 HR, 1 near-HR, 91.5 mph EV. Kremer RHB split +1.43, HR risk 1.44. limited recent HR events."""),
        ],
    },
    {
        "title": "CLE @ MIN - Slade Cecconi (R, CLE) vs Connor Prielipp (L, MIN)",
        "description": "Tail key data: Park boost +0% (stadium -7%, weather +7%). Cecconi (HR risk 0.05, vs LHB +0.05, vs RHB +0.15). Prielipp (HR risk -0.45, vs LHB -0.36, vs RHB -0.13).",
        "rows": [
            row("Kody Clemens", "L", "+350", 75, "⭐ 🌕 💣", ["vs Cecconi"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.6 mph EV. Cecconi LHB split +0.05, HR risk 0.05. park suppresses carry (-7%).""", blast="high"),
            row("Josh Bell", "S", "+433", 68, "💎", ["vs Cecconi"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 92.2 mph EV. Cecconi RHB split +0.15, HR risk 0.05. park suppresses carry (-7%).""", blast="good"),
            row("Trevor Larnach", "L", "+582", 64, "", ["vs Cecconi"], """0 HR, 3 near-HR, 92.8 mph EV. Cecconi LHB split +0.05, HR risk 0.05. park suppresses carry (-7%).""", blast="good"),
            row("Tristan Gray", "L", "+710", 58, "", ["vs Cecconi"], """0 HR, 89.5 mph EV. Cecconi LHB split +0.05, HR risk 0.05. park suppresses carry (-7%); limited recent HR events."""),
            row("Kahlil Watson", "L", "N/A", 58, "", ["vs Prielipp"], """0 HR, 1 near-HR, 95.3 mph EV. Prielipp LHB split -0.36, HR risk -0.45. slight split headwind (-0.36); pitcher suppresses HR (-0.45).""", blast="good"),
            row("David Fry", "R", "+630", 60, "🌕 💣", ["vs Prielipp"], """2 HR, 2 near-HR, 87.4 mph EV. Prielipp RHB split -0.13, HR risk -0.45. slight split headwind (-0.13); pitcher suppresses HR (-0.45).""", blast="high"),
        ],
    },
    {
        "title": "COL @ LAD - Gabriel Hughes (R, COL) vs Roki Sasaki 🧤 (R, LAD)",
        "description": "Tail key data: Park boost +16% (stadium +17%, weather -1%). Away starter risk unavailable. Sasaki 🧤 (HR risk 1.55, vs LHB +1.24, vs RHB +1.41).",
        "rows": [
            row("Shohei Ohtani", "L", "+210", 63, "", ["vs Hughes"], """0 HR, 93.6 mph EV. Hughes split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Max Muncy", "L", "+285", 58, "", ["vs Hughes"], """0 HR, 1 near-HR, 91.3 mph EV. Hughes split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
            row("Freddie Freeman", "L", "+373", 61, "", ["vs Hughes"], """0 HR, 92.3 mph EV. Hughes split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Mookie Betts", "R", "+430", 86, "🌕 💣", ["vs Hughes"], """3 HR, 3 near-HR, 93.9 mph EV. Hughes split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Dalton Rushing", "L", "+370", 64, "⭐", ["vs Hughes"], """Worst Pickz Favorite. 0 HR, 95.1 mph EV. Hughes split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Hunter Goodman", "R", "+253", 95, "🌕 💣", ["vs Sasaki"], """2 HR, 3 near-HR, 87.7 mph EV. Sasaki RHB split +1.41, HR risk 1.55. lighter EV form (87.7 mph).""", blast="high"),
            row("Mickey Moniak", "L", "+352", 95, "🌕 💣", ["vs Sasaki"], """2 HR, 2 near-HR, 91.5 mph EV. Sasaki LHB split +1.24, HR risk 1.55.""", blast="high"),
            row("Kyle Karros", "R", "+630", 99, "🌕 💣 💎", ["vs Sasaki"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 92.8 mph EV. Sasaki RHB split +1.41, HR risk 1.55.""", blast="high"),
            row("Willi Castro", "S", "N/A", 91, "🌕 💣", ["vs Sasaki"], """0 HR, 97.4 mph EV. Sasaki RHB split +1.41, HR risk 1.55. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "HOU @ WSH - Spencer Arrighetti (R, HOU) vs Foster Griffin (L, WSH)",
        "description": "Tail key data: Park boost +15% (stadium +3%, weather +12%). Arrighetti (HR risk 0.50, vs LHB +0.95, vs RHB -0.17). Griffin (HR risk -0.18, vs LHB -0.30, vs RHB +0.21).",
        "rows": [
            row("James Wood", "L", "+300", 91, "⭐ 🌕 💣", ["vs Arrighetti"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.2 mph EV. Arrighetti LHB split +0.95, HR risk 0.50.""", blast="high"),
            row("Curtis Mead", "R", "+462", 65, "⭐", ["vs Arrighetti"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 86.7 mph EV. Arrighetti RHB split -0.17, HR risk 0.50. slight split headwind (-0.17); lighter EV form (86.7 mph).""", blast="good"),
            row("Luis Garcia Jr.", "L", "N/A", 94, "🌕 💣", ["vs Arrighetti"], """5 HR, 6 near-HR, 94.2 mph EV. Arrighetti LHB split +0.95, HR risk 0.50.""", blast="high"),
            row("Yordan Alvarez", "L", "+270", 58, "", ["vs Griffin"], """0 HR, 94.3 mph EV. Griffin LHB split -0.30, HR risk -0.18. slight split headwind (-0.30); pitcher risk below avg (-0.18).""", blast="good"),
            row("Cam Smith", "R", "+560", 59, "", ["vs Griffin"], """1 HR, 1 near-HR, 86.7 mph EV. Griffin RHB split +0.21, HR risk -0.18. pitcher risk below avg (-0.18); lighter EV form (86.7 mph).""", blast="good"),
            row("Zach Dezenzo", "R", "+690", 60, "", ["vs Griffin"], """1 HR, 2 near-HR, 86.5 mph EV. Griffin RHB split +0.21, HR risk -0.18. pitcher risk below avg (-0.18); lighter EV form (86.5 mph).""", blast="good"),
        ],
    },
    {
        "title": "KC @ NYM - Steven Cruz (L, KC) vs Christian Scott 🧤 (R, NYM)",
        "description": "Tail key data: Park boost +8% (stadium -1%, weather +10%). Cruz (HR risk 0.19, vs LHB +0.66, vs RHB -0.26). Scott 🧤 (HR risk 0.96, vs LHB +1.19, vs RHB -0.49).",
        "rows": [
            row("Juan Soto", "L", "+295", 87, "🚀 ⭐ 🌕 💣", ["vs Cruz"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 101.3 mph EV. Cruz LHB split +0.66, HR risk 0.19.""", blast="high"),
            row("Carson Benge", "L", "+575", 67, "", ["vs Cruz"], """1 HR, 2 near-HR, 88.3 mph EV. Cruz LHB split +0.66, HR risk 0.19.""", blast="good"),
            row("Francisco Lindor", "S", "+445", 73, "", ["vs Cruz"], """1 HR, 1 near-HR, 96.5 mph EV. Cruz RHB split -0.26, HR risk 0.19. slight split headwind (-0.26).""", blast="good"),
            row("Jac Caglianone", "L", "+375", 70, "", ["vs Scott"], """0 HR, 85.7 mph EV. Scott LHB split +1.19, HR risk 0.96. limited recent HR events; lighter EV form (85.7 mph)."""),
            row("Bobby Witt Jr.", "R", "+340", 86, "⭐ 🌕 💣", ["vs Scott"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.3 mph EV. Scott RHB split -0.49, HR risk 0.96. tough split lane (-0.49).""", blast="high"),
            row("Carter Jensen", "L", "+390", 88, "🌕 💣 💎", ["vs Scott"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 94.8 mph EV. Scott LHB split +1.19, HR risk 0.96.""", blast="good"),
        ],
    },
    {
        "title": "LAA @ TEX - Walbert Urena (R, LAA) vs MacKenzie Gore (L, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -10%, weather -1%). Urena (HR risk -1.26, vs LHB -0.72, vs RHB -1.15). Gore (HR risk -0.17, vs LHB -0.53, vs RHB +0.17).",
        "rows": [
            row("Brandon Nimmo", "L", "+466", 58, "", ["vs Urena"], """0 HR, 1 near-HR, 91.3 mph EV. Urena LHB split -0.72, HR risk -1.26. tough split lane (-0.72); pitcher suppresses HR (-1.26)."""),
            row("Joc Pederson", "L", "+464", 61, "🌕 💣", ["vs Urena"], """3 HR, 3 near-HR, 93.6 mph EV. Urena LHB split -0.72, HR risk -1.26. tough split lane (-0.72); pitcher suppresses HR (-1.26).""", blast="high"),
            row("Jose Siri", "R", "+509", 67, "🌕 💣", ["vs Gore"], """2 HR, 2 near-HR, 91.7 mph EV. Gore RHB split +0.17, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-11%).""", blast="high"),
            row("Zach Neto", "R", "+360", 71, "🌕 💣", ["vs Gore"], """2 HR, 4 near-HR, 89.8 mph EV. Gore RHB split +0.17, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-11%).""", blast="high"),
        ],
    },
    {
        "title": "MIL @ STL - Kyle Harrison (L, MIL) vs Michael McGreevy (R, STL)",
        "description": "Tail key data: Park boost -9% (stadium -10%, weather +1%). Harrison (HR risk 0.29, vs LHB -0.28, vs RHB +0.61). McGreevy (HR risk 0.12, vs LHB +0.18, vs RHB +0.08).",
        "rows": [
            row("Lars Nootbaar", "L", "N/A", 58, "", ["vs Harrison"], """0 HR, 89.3 mph EV. Harrison LHB split -0.28, HR risk 0.29. slight split headwind (-0.28); park/weather net drag (-9%)."""),
            row("Jordan Walker", "R", "+416", 64, "🚀 ⭐", ["vs Harrison"], """Worst Pickz Favorite. 0 HR, 106.3 mph EV. Harrison RHB split +0.61, HR risk 0.29. park/weather net drag (-9%); limited recent HR events.""", blast="good"),
            row("JJ Wetherholt", "L", "+750", 63, "", ["vs Harrison"], """1 HR, 1 near-HR, 97.5 mph EV. Harrison LHB split -0.28, HR risk 0.29. slight split headwind (-0.28); park/weather net drag (-9%).""", blast="good"),
            row("Nelson Velazquez", "R", "+594", 65, "", ["vs Harrison"], """1 HR, 1 near-HR, 91.2 mph EV. Harrison RHB split +0.61, HR risk 0.29. park/weather net drag (-9%).""", blast="good"),
            row("Garrett Mitchell", "L", "+660", 82, "🚀 ⭐ 🌕 💣", ["vs McGreevy"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 101.0 mph EV. McGreevy LHB split +0.18, HR risk 0.12. park/weather net drag (-9%).""", blast="high"),
            row("Jake Bauers", "L", "+450", 58, "", ["vs McGreevy"], """0 HR, 87.9 mph EV. McGreevy LHB split +0.18, HR risk 0.12. park/weather net drag (-9%); limited recent HR events."""),
            row("Jackson Chourio", "R", "+520", 71, "🌕 💣", ["vs McGreevy"], """2 HR, 3 near-HR, 88.6 mph EV. McGreevy RHB split +0.08, HR risk 0.12. park/weather net drag (-9%).""", blast="high"),
            row("Gary Sanchez", "R", "N/A", 73, "🌕 💣", ["vs McGreevy"], """2 HR, 2 near-HR, 96.8 mph EV. McGreevy RHB split +0.08, HR risk 0.12. park/weather net drag (-9%).""", blast="high"),
        ],
    },
    {
        "title": "NYY @ TB - Gerrit Cole (R, NYY) vs Shane McClanahan (L, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Cole (HR risk 0.63, vs LHB +0.65, vs RHB -0.33). McClanahan (HR risk 0.07, vs LHB +0.79, vs RHB -0.15).",
        "rows": [
            row("Hunter Feduccia", "L", "+1050", 83, "⭐", ["vs Cole"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 95.5 mph EV. Cole LHB split +0.65, HR risk 0.63.""", blast="good"),
            row("Jonathan Aranda", "L", "+529", 62, "💎", ["vs Cole"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 88.1 mph EV. Cole LHB split +0.65, HR risk 0.63. limited recent HR events."""),
            row("Junior Caminero", "R", "+253", 86, "🌕 💣", ["vs Cole"], """5 HR, 5 near-HR, 95.1 mph EV. Cole RHB split -0.33, HR risk 0.63. slight split headwind (-0.33).""", blast="high"),
            row("Victor Mesa Jr.", "L", "+720", 73, "", ["vs Cole"], """1 HR, 2 near-HR, 89.8 mph EV. Cole LHB split +0.65, HR risk 0.63.""", blast="good"),
            row("Ben Rice", "L", "+444", 62, "", ["vs McClanahan"], """1 HR, 1 near-HR, 87.6 mph EV. McClanahan LHB split +0.79, HR risk 0.07. lighter EV form (87.6 mph).""", blast="good"),
            row("Trent Grisham", "L", "+425", 62, "", ["vs McClanahan"], """0 HR, 92.8 mph EV. McClanahan LHB split +0.79, HR risk 0.07. limited recent HR events.""", blast="good"),
            row("Max Schuemann", "R", "N/A", 58, "💎", ["vs McClanahan"], """Worst Pickz Hidden Gem. 0 HR, 92.7 mph EV. McClanahan RHB split -0.15, HR risk 0.07. slight split headwind (-0.15); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "PHI @ CIN - Chuck King (R, PHI) vs Chase Burns (R, CIN)",
        "description": "Tail key data: Park boost +17% (stadium +14%, weather +2%). King (HR risk -0.60, vs LHB -0.52, vs RHB -0.29). Burns (HR risk -0.10, vs LHB +0.33, vs RHB -0.75).",
        "rows": [
            row("Bryce Harper", "L", "+291", 80, "🚀 🌕 💣", ["vs Burns"], """2 HR, 2 near-HR, 101.2 mph EV. Burns LHB split +0.33, HR risk -0.10. pitcher risk below avg (-0.10).""", blast="high"),
            row("Kyle Schwarber", "L", "+200", 72, "", ["vs Burns"], """1 HR, 2 near-HR, 99.5 mph EV. Burns LHB split +0.33, HR risk -0.10. pitcher risk below avg (-0.10).""", blast="good"),
            row("Edmundo Sosa", "R", "N/A", 62, "", ["vs Burns"], """1 HR, 2 near-HR, 93.6 mph EV. Burns RHB split -0.75, HR risk -0.10. tough split lane (-0.75); pitcher risk below avg (-0.10).""", blast="good"),
            row("Derek Hill", "R", "N/A", 63, "", ["vs Burns"], """1 HR, 1 near-HR, 95.9 mph EV. Burns RHB split -0.75, HR risk -0.10. tough split lane (-0.75); pitcher risk below avg (-0.10).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ MIA - George Kirby (R, SEA) vs Tyler Phillips (R, MIA)",
        "description": "Tail key data: Park boost -12% (stadium -12%, weather +0%). Kirby (HR risk -0.22, vs LHB -0.35, vs RHB +0.18). Phillips (HR risk 0.58, vs LHB +0.85, vs RHB +0.22).",
        "rows": [
            row("Otto Lopez", "R", "+1040", 66, "🌕 💣 💎", ["vs Kirby"], """Worst Pickz Hidden Gem. 2 HR, 4 near-HR, 85.4 mph EV. Kirby RHB split +0.18, HR risk -0.22. pitcher risk below avg (-0.22); park/weather net drag (-12%).""", blast="high"),
            row("Owen Caissie", "L", "+600", 71, "⭐ 🌕 💣", ["vs Kirby"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 99.0 mph EV. Kirby LHB split -0.35, HR risk -0.22. slight split headwind (-0.35); pitcher risk below avg (-0.22).""", blast="high"),
            row("Heriberto Hernandez", "R", "+460", 70, "⭐ 🌕 💣", ["vs Kirby"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 95.5 mph EV. Kirby RHB split +0.18, HR risk -0.22. pitcher risk below avg (-0.22); park/weather net drag (-12%).""", blast="high"),
            row("Kyle Stowers", "L", "+425", 58, "💎", ["vs Kirby"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.0 mph EV. Kirby LHB split -0.35, HR risk -0.22. slight split headwind (-0.35); pitcher risk below avg (-0.22).""", blast="good"),
            row("Dominic Canzone", "L", "+475", 74, "", ["vs Phillips"], """0 HR, 2 near-HR, 97.0 mph EV. Phillips LHB split +0.85, HR risk 0.58. park/weather net drag (-12%).""", blast="good"),
            row("Cal Raleigh", "S", "+340", 63, "", ["vs Phillips"], """0 HR, 1 near-HR, 90.3 mph EV. Phillips RHB split +0.22, HR risk 0.58. park/weather net drag (-12%); limited recent HR events."""),
            row("Mitch Garver", "R", "N/A", 66, "", ["vs Phillips"], """1 HR, 1 near-HR, 90.2 mph EV. Phillips RHB split +0.22, HR risk 0.58. park/weather net drag (-12%).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ SF - Dylan Cease (R, TOR) vs Logan Webb (R, SF)",
        "description": "Tail key data: Park boost -21% (stadium -16%, weather -5%). Cease (HR risk -1.43, vs LHB -0.98, vs RHB -1.21). Webb (HR risk -0.71, vs LHB -0.48, vs RHB -0.55).",
        "rows": [
            row("Rafael Devers", "L", "+540", 59, "⭐ 🌕 💣", ["vs Cease"], """Worst Pickz Favorite. 5 HR, 6 near-HR, 97.0 mph EV. Cease LHB split -0.98, HR risk -1.43. tough split lane (-0.98); pitcher suppresses HR (-1.43).""", blast="high"),
            row("Heliot Ramos", "R", "+680", 58, "🌕 💣", ["vs Cease"], """2 HR, 4 near-HR, 92.1 mph EV. Cease RHB split -1.21, HR risk -1.43. tough split lane (-1.21); pitcher suppresses HR (-1.43).""", blast="high"),
            row("Vladimir Guerrero Jr.", "R", "+900", 58, "", ["vs Webb"], """0 HR, 91.4 mph EV. Webb RHB split -0.55, HR risk -0.71. tough split lane (-0.55); pitcher suppresses HR (-0.71)."""),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-08")

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

    out = ROOT / '_games-0708.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
