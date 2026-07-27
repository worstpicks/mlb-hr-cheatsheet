#!/usr/bin/env python3
"""Generate games[] block for 2026-07-27 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Andrew Vaughn (R)",
    "Austin Riley (R)",
    "Bryce Harper (L)",
    "Chase DeLauter (L)",
    "Esmerlyn Valdez (R)",
    "JJ Bleday (L)",
    "James Wood (L)",
    "Joc Pederson (L)",
    "Luis Garcia Jr. (L)",
    "Rafael Devers (L)",
    "Riley Greene (L)",
    "Tyler Stephenson (R)",
    "Willson Contreras (R)",
    "Yohendrick Pinango (L)",
}

GEMS = {
    "Nelson Velazquez (R)",
    "Patrick Bailey (S)",
}

PLAYER_TEAMS = {
    "Andrew Vaughn (R)": "MIL",
    "Austin Riley (R)": "ATL",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "CJ Abrams (L)": "WSH",
    "Casey Schmitt (R)": "SF",
    "Chase DeLauter (L)": "CLE",
    "Christian Yelich (L)": "MIL",
    "Cole Young (L)": "SEA",
    "Colt Keith (L)": "DET",
    "Cooper Pratt (R)": "MIL",
    "Corbin Carroll (L)": "ARI",
    "Dylan Crews (R)": "WSH",
    "Eli White (R)": "ATL",
    "Elly De La Cruz (S)": "CIN",
    "Esmerlyn Valdez (R)": "PIT",
    "Eugenio Suarez (R)": "CIN",
    "Griffin Conine (L)": "MIA",
    "Gunnar Henderson (L)": "BAL",
    "JJ Bleday (L)": "CIN",
    "JJ Wetherholt (L)": "STL",
    "Jacob Wilson (R)": "ATH",
    "James Wood (L)": "WSH",
    "Jeremy Pena (R)": "HOU",
    "Joc Pederson (L)": "TEX",
    "Joe Mack (L)": "MIA",
    "Jorge Soler (R)": "LAA",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Kyle Manzardo (L)": "CLE",
    "Luis Garcia Jr. (L)": "WSH",
    "Luis Robert (R)": "NYM",
    "Luke Raley (L)": "SEA",
    "Michael Conforto (L)": "CHC",
    "Miguel Vargas (R)": "CWS",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "STL",
    "Nick Kurtz (L)": "ATH",
    "Patrick Bailey (S)": "CLE",
    "Rafael Devers (L)": "SF",
    "Riley Greene (L)": "DET",
    "Ryan Waldschmidt (R)": "ARI",
    "Sam Huff (R)": "BAL",
    "Shawn Ross (R)": "PIT",
    "Spencer Torkelson (R)": "DET",
    "Travis Bazzana (L)": "CLE",
    "Tyler Stephenson (R)": "CIN",
    "Vaughn Grissom (R)": "LAA",
    "Willson Contreras (R)": "BOS",
    "Wyatt Langford (R)": "TEX",
    "Yohendrick Pinango (L)": "TOR",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("TOR @ WSH", "Scherzer"),
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
        "title": "ARI @ PIT - Merrill Kelly (R, ARI) vs Mitch Keller (R, PIT)",
        "description": "Tail key data: Park boost -8% (stadium -15%, weather +7%). Kelly (HR risk 0.93, vs LHB +0.78, vs RHB +0.94). Keller (HR risk 0.37, vs LHB +0.55, vs RHB -0.37).",
        "rows": [
            row("Esmerlyn Valdez", "R", "+405", 94, "🚀 ⭐ 🌕 💣", ["vs Kelly"], """Worst Pickz Favorite. 4 HR, 4 near-HR, 100.6 mph EV. Kelly RHB split +0.94, HR risk 0.93. park/weather net drag (-8%).""", blast="high"),
            row("Shawn Ross", "R", "N/A", 81, "", ["vs Kelly"], """1 HR, 1 near-HR, 96.6 mph EV. Kelly RHB split +0.94, HR risk 0.93. park/weather net drag (-8%).""", blast="good"),
            row("Bryan Reynolds", "S", "+550", 76, "", ["vs Kelly"], """0 HR, 2 near-HR, 93.4 mph EV. Kelly SHB→RHB split +0.94, HR risk 0.93. park/weather net drag (-8%).""", blast="good"),
            row("Corbin Carroll", "L", "+316", 71, "", ["vs Keller"], """1 HR, 3 near-HR, 90.3 mph EV. Keller LHB split +0.55, HR risk 0.37. park/weather net drag (-8%).""", blast="good"),
            row("Ryan Waldschmidt", "R", "+660", 59, "", ["vs Keller"], """1 HR, 1 near-HR, 91.7 mph EV. Keller RHB split -0.37, HR risk 0.37. slight split headwind (-0.37); park/weather net drag (-8%).""", blast="good"),
            row("Ketel Marte", "S", "+313", 62, "", ["vs Keller"], """0 HR, 93.3 mph EV. Keller SHB→LHB split +0.55, HR risk 0.37. park/weather net drag (-8%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "ATL @ NYM - Martin Perez (L, ATL) vs Zach Thornton (L, NYM)",
        "description": "Tail key data: Park boost +10% (stadium -1%, weather +11%). Perez (HR risk -0.11, vs LHB +0.45, vs RHB -0.27). Thornton (HR risk -0.03, vs LHB +0.63, vs RHB -0.37).",
        "rows": [
            row("Luis Robert", "R", "+512", 64, "🚀", ["vs Perez"], """1 HR, 1 near-HR, 102.9 mph EV. Perez RHB split -0.27, HR risk -0.11. slight split headwind (-0.27); pitcher risk below avg (-0.11).""", blast="good"),
            row("Austin Riley", "R", "+375", 60, "🚀 ⭐", ["vs Thornton"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 100.3 mph EV. Thornton RHB split -0.37, HR risk -0.03. slight split headwind (-0.37); pitcher risk below avg (-0.03).""", blast="good"),
            row("Eli White", "R", "+600", 78, "🌕 💣", ["vs Thornton"], """3 HR, 4 near-HR, 93.1 mph EV. Thornton RHB split -0.37, HR risk -0.03. slight split headwind (-0.37); pitcher risk below avg (-0.03).""", blast="high"),
        ],
    },
    {
        "title": "BAL @ DET - Kyle Bradish (R, BAL) vs Keider Montero (R, DET)",
        "description": "Tail key data: Park boost +2% (stadium -11%, weather +13%). Bradish (HR risk -0.71, vs LHB -1.00, vs RHB -0.24). Montero (HR risk -0.43, vs LHB -0.45, vs RHB -0.24).",
        "rows": [
            row("Riley Greene", "L", "+426", 65, "⭐ 🌕 💣", ["vs Bradish"], """Worst Pickz Favorite. 1 HR, 4 near-HR, 98.0 mph EV. Bradish LHB split -1.00, HR risk -0.71. tough split lane (-1.00); pitcher suppresses HR (-0.71).""", blast="high"),
            row("Spencer Torkelson", "R", "+476", 58, "", ["vs Bradish"], """1 HR, 1 near-HR, 88.3 mph EV. Bradish RHB split -0.24, HR risk -0.71. slight split headwind (-0.24); pitcher suppresses HR (-0.71).""", blast="good"),
            row("Colt Keith", "L", "+670", 58, "", ["vs Bradish"], """0 HR, 1 near-HR, 90.6 mph EV. Bradish LHB split -1.00, HR risk -0.71. tough split lane (-1.00); pitcher suppresses HR (-0.71)."""),
            row("Gunnar Henderson", "L", "+425", 58, "", ["vs Montero"], """1 HR, 1 near-HR, 87.5 mph EV. Montero LHB split -0.45, HR risk -0.43. tough split lane (-0.45); pitcher suppresses HR (-0.43).""", blast="good"),
            row("Sam Huff", "R", "+950", 58, "", ["vs Montero"], """0 HR, 2 near-HR, 89.3 mph EV. Montero RHB split -0.24, HR risk -0.43. slight split headwind (-0.24); pitcher suppresses HR (-0.43).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ ATH - Payton Tolle (L, BOS) vs Jack Perkins (R, ATH)",
        "description": "Tail key data: Park boost +34% (stadium +33%, weather +1%). Tolle (HR risk 0.04, vs LHB -0.71, vs RHB +0.60). Perkins (HR risk 0.67, vs LHB +0.61, vs RHB +0.68).",
        "rows": [
            row("Nick Kurtz", "L", "+343", 58, "", ["vs Tolle"], """0 HR, 83.4 mph EV. Tolle LHB split -0.71, HR risk 0.04. tough split lane (-0.71); limited recent HR events."""),
            row("Jacob Wilson", "R", "+690", 70, "", ["vs Tolle"], """1 HR, 1 near-HR, 87.6 mph EV. Tolle RHB split +0.60, HR risk 0.04. lighter EV form (87.6 mph).""", blast="good"),
            row("Willson Contreras", "R", "+340", 94, "⭐ 🌕 💣", ["vs Perkins"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.0 mph EV. Perkins RHB split +0.68, HR risk 0.67.""", blast="high"),
        ],
    },
    {
        "title": "CHC @ STL - David Peterson (L, CHC) vs Matthew Liberatore (L, STL)",
        "description": "Tail key data: Park boost -6% (stadium -10%, weather +4%). Peterson (HR risk -0.15, vs LHB +0.24, vs RHB -0.23). Liberatore (HR risk 0.48, vs LHB +0.72, vs RHB +0.28).",
        "rows": [
            row("JJ Wetherholt", "L", "+680", 62, "", ["vs Peterson"], """1 HR, 1 near-HR, 94.3 mph EV. Peterson LHB split +0.24, HR risk -0.15. pitcher risk below avg (-0.15); park/weather net drag (-6%).""", blast="good"),
            row("Nelson Velazquez", "R", "+583", 58, "💎", ["vs Peterson"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.6 mph EV. Peterson RHB split -0.23, HR risk -0.15. slight split headwind (-0.23); pitcher risk below avg (-0.15).""", blast="good"),
            row("Michael Conforto", "L", "+358", 86, "🚀 🌕 💣", ["vs Liberatore"], """2 HR, 2 near-HR, 102.6 mph EV. Liberatore LHB split +0.72, HR risk 0.48. park/weather net drag (-6%).""", blast="high"),
        ],
    },
    {
        "title": "CLE @ CIN - Slade Cecconi (R, CLE) vs Chase Burns (R, CIN)",
        "description": "Tail key data: Park boost +20% (stadium +15%, weather +5%). Cecconi (HR risk 0.24, vs LHB +0.21, vs RHB +0.20). Burns (HR risk -0.01, vs LHB +0.30, vs RHB -0.59).",
        "rows": [
            row("JJ Bleday", "L", "+373", 71, "⭐", ["vs Cecconi"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 92.2 mph EV. Cecconi LHB split +0.21, HR risk 0.24.""", blast="good"),
            row("Tyler Stephenson", "R", "+460", 69, "⭐", ["vs Cecconi"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.0 mph EV. Cecconi RHB split +0.20, HR risk 0.24. limited recent HR events.""", blast="good"),
            row("Elly De La Cruz", "S", "+312", 71, "", ["vs Cecconi"], """1 HR, 1 near-HR, 93.7 mph EV. Cecconi SHB→LHB split +0.21, HR risk 0.24.""", blast="good"),
            row("Eugenio Suarez", "R", "+423", 72, "", ["vs Cecconi"], """1 HR, 1 near-HR, 94.3 mph EV. Cecconi RHB split +0.20, HR risk 0.24.""", blast="good"),
            row("Patrick Bailey", "S", "+840", 89, "🌕 💣 💎", ["vs Burns"], """Worst Pickz Hidden Gem. 3 HR, 4 near-HR, 99.7 mph EV. Burns SHB→LHB split +0.30, HR risk -0.01. pitcher risk below avg (-0.01).""", blast="high"),
            row("Chase DeLauter", "L", "+440", 81, "🚀 ⭐ 🌕 💣", ["vs Burns"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.0 mph EV. Burns LHB split +0.30, HR risk -0.01. pitcher risk below avg (-0.01).""", blast="high"),
            row("Travis Bazzana", "L", "+630", 71, "", ["vs Burns"], """1 HR, 1 near-HR, 94.7 mph EV. Burns LHB split +0.30, HR risk -0.01. pitcher risk below avg (-0.01).""", blast="good"),
            row("Kyle Manzardo", "L", "+520", 68, "", ["vs Burns"], """0 HR, 1 near-HR, 95.7 mph EV. Burns LHB split +0.30, HR risk -0.01. pitcher risk below avg (-0.01); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "HOU @ LAA - Tatsuya Imai (R, HOU) vs Walbert Urena (R, LAA)",
        "description": "Tail key data: Park boost +16% (stadium +8%, weather +8%). Imai (HR risk 0.89, vs LHB +0.86, vs RHB +0.27). Urena (HR risk -1.32, vs LHB -1.35, vs RHB -1.01).",
        "rows": [
            row("Jeremy Pena", "R", "+750", 61, "🌕 💣", ["vs Urena"], """2 HR, 2 near-HR, 96.8 mph EV. Urena RHB split -1.01, HR risk -1.32. tough split lane (-1.01); pitcher suppresses HR (-1.32).""", blast="high"),
            row("Yordan Alvarez", "L", "+240", 58, "", ["vs Urena"], """1 HR, 1 near-HR, 91.9 mph EV. Urena LHB split -1.35, HR risk -1.32. tough split lane (-1.35); pitcher suppresses HR (-1.32).""", blast="good"),
            row("Jorge Soler", "R", "+514", 76, "", ["vs Imai"], """0 HR, 2 near-HR, 93.1 mph EV. Imai RHB split +0.27, HR risk 0.89.""", blast="good"),
            row("Vaughn Grissom", "R", "+840", 84, "🌕 💣", ["vs Imai"], """2 HR, 2 near-HR, 88.5 mph EV. Imai RHB split +0.27, HR risk 0.89.""", blast="high"),
        ],
    },
    {
        "title": "MIL @ SF - Brandon Sproat (R, MIL) vs Tyler Mahle (R, SF)",
        "description": "Tail key data: Park boost -15% (stadium -18%, weather +3%). Sproat (HR risk -0.02, vs LHB -0.46, vs RHB +0.65). Mahle (HR risk -0.48, vs LHB -0.51, vs RHB -0.27).",
        "rows": [
            row("Rafael Devers", "L", "+457", 58, "⭐", ["vs Sproat"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.0 mph EV. Sproat LHB split -0.46, HR risk -0.02. tough split lane (-0.46); pitcher risk below avg (-0.02).""", blast="good"),
            row("Bryce Eldridge", "L", "+650", 58, "", ["vs Sproat"], """1 HR, 1 near-HR, 95.5 mph EV. Sproat LHB split -0.46, HR risk -0.02. tough split lane (-0.46); pitcher risk below avg (-0.02).""", blast="good"),
            row("Casey Schmitt", "R", "+600", 70, "🌕 💣", ["vs Sproat"], """2 HR, 2 near-HR, 90.9 mph EV. Sproat RHB split +0.65, HR risk -0.02. pitcher risk below avg (-0.02); park/weather net drag (-15%).""", blast="high"),
            row("Andrew Vaughn", "R", "+940", 58, "⭐", ["vs Mahle"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.7 mph EV. Mahle RHB split -0.27, HR risk -0.48. slight split headwind (-0.27); pitcher suppresses HR (-0.48).""", blast="good"),
            row("Cooper Pratt", "R", "+1650", 58, "", ["vs Mahle"], """1 HR, 1 near-HR, 90.8 mph EV. Mahle RHB split -0.27, HR risk -0.48. slight split headwind (-0.27); pitcher suppresses HR (-0.48).""", blast="good"),
            row("Christian Yelich", "L", "+730", 58, "", ["vs Mahle"], """1 HR, 2 near-HR, 93.4 mph EV. Mahle LHB split -0.51, HR risk -0.48. tough split lane (-0.51); pitcher suppresses HR (-0.48).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ CWS - Max Fried (L, NYY) vs Noah Schultz (L, CWS)",
        "description": "Tail key data: Park boost +17% (stadium +3%, weather +13%). Fried (HR risk -1.49, vs LHB -1.21, vs RHB -1.18). Schultz (HR risk 0.88, vs LHB -0.09, vs RHB +1.11).",
        "rows": [
            row("Miguel Vargas", "R", "+425", 58, "", ["vs Fried"], """0 HR, 92.1 mph EV. Fried RHB split -1.18, HR risk -1.49. tough split lane (-1.18); pitcher suppresses HR (-1.49).""", blast="good"),
            row("Munetaka Murakami", "L", "+370", 58, "", ["vs Fried"], """0 HR, 91.5 mph EV. Fried LHB split -1.21, HR risk -1.49. tough split lane (-1.21); pitcher suppresses HR (-1.49)."""),
        ],
    },
    {
        "title": "PHI @ MIA - Zack Wheeler (R, PHI) vs Tyler Phillips (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -13%, weather +0%). Wheeler (HR risk -0.55, vs LHB -0.53, vs RHB -0.43). Phillips (HR risk 0.04, vs LHB +0.10, vs RHB -0.02).",
        "rows": [
            row("Griffin Conine", "L", "+700", 58, "", ["vs Wheeler"], """1 HR, 1 near-HR, 93.0 mph EV. Wheeler LHB split -0.53, HR risk -0.55. tough split lane (-0.53); pitcher suppresses HR (-0.55).""", blast="good"),
            row("Joe Mack", "L", "+875", 60, "🌕 💣", ["vs Wheeler"], """2 HR, 2 near-HR, 94.6 mph EV. Wheeler LHB split -0.53, HR risk -0.55. tough split lane (-0.53); pitcher suppresses HR (-0.55).""", blast="high"),
            row("Bryce Harper", "L", "+475", 62, "⭐", ["vs Phillips"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.5 mph EV. Phillips LHB split +0.10, HR risk 0.04. park/weather net drag (-13%).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ TEX - George Kirby (R, SEA) vs Kumar Rocker (R, TEX)",
        "description": "Tail key data: Park boost -10% (stadium -9%, weather -1%). Kirby (HR risk -0.05, vs LHB -0.01, vs RHB -0.18). Rocker (HR risk 0.01, vs LHB +0.54, vs RHB -0.56).",
        "rows": [
            row("Joc Pederson", "L", "+450", 71, "⭐ 🌕 💣", ["vs Kirby"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 98.4 mph EV. Kirby LHB split -0.01, HR risk -0.05. slight split headwind (-0.01); pitcher risk below avg (-0.05).""", blast="high"),
            row("Wyatt Langford", "R", "+441", 58, "", ["vs Kirby"], """0 HR, 93.6 mph EV. Kirby RHB split -0.18, HR risk -0.05. slight split headwind (-0.18); pitcher risk below avg (-0.05).""", blast="good"),
            row("Luke Raley", "L", "+400", 62, "", ["vs Rocker"], """0 HR, 1 near-HR, 96.6 mph EV. Rocker LHB split +0.54, HR risk 0.01. park/weather net drag (-10%); limited recent HR events.""", blast="good"),
            row("Cole Young", "L", "+600", 58, "", ["vs Rocker"], """0 HR, 1 near-HR, 84.6 mph EV. Rocker LHB split +0.54, HR risk 0.01. park/weather net drag (-10%); limited recent HR events."""),
        ],
    },
    {
        "title": "TOR @ WSH - Max Scherzer 🧤 (R, TOR) vs Andrew Alvarez (L, WSH)",
        "description": "Tail key data: Park boost +14% (stadium +3%, weather +11%). Scherzer 🧤 (HR risk 2.33, vs LHB +2.05, vs RHB +2.28). Alvarez (HR risk -1.03, vs LHB -0.98, vs RHB -0.78).",
        "rows": [
            row("James Wood", "L", "+215", 95, "⭐ 🌕 💣", ["vs Scherzer"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.0 mph EV. Scherzer LHB split +2.05, HR risk 2.33.""", blast="good"),
            row("CJ Abrams", "L", "+330", 99, "🌕 💣", ["vs Scherzer"], """3 HR, 3 near-HR, 95.6 mph EV. Scherzer LHB split +2.05, HR risk 2.33.""", blast="high"),
            row("Luis Garcia Jr.", "L", "+340", 94, "⭐ 🌕 💣", ["vs Scherzer"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.1 mph EV. Scherzer LHB split +2.05, HR risk 2.33.""", blast="good"),
            row("Dylan Crews", "R", "+560", 95, "🌕 💣", ["vs Scherzer"], """1 HR, 2 near-HR, 95.3 mph EV. Scherzer RHB split +2.28, HR risk 2.33.""", blast="good"),
            row("Yohendrick Pinango", "L", "N/A", 58, "⭐", ["vs Alvarez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.4 mph EV. Alvarez LHB split -0.98, HR risk -1.03. tough split lane (-0.98); pitcher suppresses HR (-1.03).""", blast="good"),
            row("Kazuma Okamoto", "R", "+431", 58, "", ["vs Alvarez"], """1 HR, 1 near-HR, 93.3 mph EV. Alvarez RHB split -0.78, HR risk -1.03. tough split lane (-0.78); pitcher suppresses HR (-1.03).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-27")

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

    out = ROOT / '_games-0727.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
