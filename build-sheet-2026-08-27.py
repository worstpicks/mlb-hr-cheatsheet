#!/usr/bin/env python3
"""Generate games[] block for 2026-08-27 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Austin Riley (R)",
    "Brett Baty (L)",
    "Christian Encarnacion-Strand (R)",
    "Corbin Carroll (L)",
    "Jackson Chourio (R)",
    "Joshua Baez (R)",
    "Kazuma Okamoto (R)",
    "Kyle Isbel (L)",
    "Rafael Devers (L)",
    "Spencer Jones (L)",
    "Teoscar Hernandez (R)",
}

GEMS = {
    "Andres Chaparro (R)",
    "Andrew Vaughn (R)",
    "Ben Rice (L)",
    "Carter Jensen (L)",
    "Coby Mayo (R)",
    "Daz Cameron (R)",
    "Drake Baldwin (L)",
    "Drew Gilbert (L)",
    "Dylan Crews (R)",
    "Gary Sanchez (R)",
    "Grant McCray (L)",
    "JJ Wetherholt (L)",
    "Luis Garcia Jr. (L)",
    "Luis Robert (R)",
    "Nelson Velazquez (R)",
    "Pete Alonso (R)",
    "Tim Tawa (R)",
    "Willi Castro (S)",
}

PLAYER_TEAMS = {
    "AJ Ewing (L)": "NYM",
    "Alec Burleson (L)": "STL",
    "Alejandro Kirk (R)": "TOR",
    "Andres Chaparro (R)": "WSH",
    "Andrew Vaughn (R)": "MIL",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Brady House (R)": "WSH",
    "Brett Baty (L)": "NYM",
    "Carter Jensen (L)": "KC",
    "Christian Encarnacion-Strand (R)": "BAL",
    "Christian Franklin (R)": "BAL",
    "Coby Mayo (R)": "BAL",
    "Connor Norby (R)": "COL",
    "Corbin Carroll (L)": "ARI",
    "Daylen Lile (L)": "WSH",
    "Daz Cameron (R)": "TOR",
    "Drake Baldwin (L)": "ATL",
    "Drew Gilbert (L)": "SF",
    "Dylan Crews (R)": "WSH",
    "Eric Wagaman (R)": "NYM",
    "Gary Sanchez (R)": "MIL",
    "Grant McCray (L)": "SF",
    "Hunter Goodman (R)": "COL",
    "Isaac Paredes (R)": "HOU",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake Bauers (L)": "MIL",
    "Jeremy Pena (R)": "HOU",
    "Jordan Walker (R)": "STL",
    "Joshua Baez (R)": "STL",
    "Kazuma Okamoto (R)": "TOR",
    "Kyle Isbel (L)": "KC",
    "Kyle Tucker (L)": "LAD",
    "Luis Garcia Jr. (L)": "NYY",
    "Luis Robert (R)": "NYM",
    "Luis Torrens (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Michael Harris II (L)": "ATL",
    "Mike Yastrzemski (L)": "ATL",
    "Nelson Velazquez (R)": "HOU",
    "Pete Alonso (R)": "BAL",
    "Rafael Devers (L)": "SF",
    "Ramon Urias (R)": "STL",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Trent Grisham (L)": "NYY",
    "Turner Hill (L)": "SF",
    "Willi Castro (S)": "COL",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("COL @ WSH", "Irvin"),
    ("MIL @ NYM", "Manaea"),
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
        "title": "ARI @ SF - Jose Cabrera (R, ARI) vs Landen Roupp (R, SF)",
        "description": "Tail key data: Park boost -20% (stadium -20%, weather +0%). Cabrera (HR risk 0.37, vs LHB +0.74, vs RHB -0.02). Roupp (HR risk -0.72, vs LHB -0.42, vs RHB -0.73).",
        "rows": [
            row("Rafael Devers", "L", "+470", 86, "⭐ 🌕 💣", ["vs Cabrera"], """Worst Pickz Favorite. 4 HR, 4 near-HR, 97.9 mph EV. Cabrera LHB split +0.74, HR risk 0.37. park/weather net drag (-20%).""", blast="high"),
            row("Drew Gilbert", "L", "+920", 74, "💎", ["vs Cabrera"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 94.9 mph EV. Cabrera LHB split +0.74, HR risk 0.37. park/weather net drag (-20%).""", blast="good"),
            row("Grant McCray", "L", "+850", 58, "💎", ["vs Cabrera"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 89.2 mph EV. Cabrera LHB split +0.74, HR risk 0.37. park/weather net drag (-20%); limited recent HR events."""),
            row("Turner Hill", "L", "+1340", 61, "", ["vs Cabrera"], """0 HR, 2 near-HR, 90.8 mph EV. Cabrera LHB split +0.74, HR risk 0.37. park/weather net drag (-20%).""", blast="good"),
            row("Tim Tawa", "R", "+1060", 59, "🌕 💣 💎", ["vs Roupp"], """Worst Pickz Hidden Gem. 1 HR, 4 near-HR, 95.1 mph EV. Roupp RHB split -0.73, HR risk -0.72. tough split lane (-0.73); pitcher suppresses HR (-0.72).""", blast="high"),
            row("Corbin Carroll", "L", "+600", 58, "⭐", ["vs Roupp"], """Worst Pickz Favorite. 0 HR, 98.9 mph EV. Roupp LHB split -0.42, HR risk -0.72. tough split lane (-0.42); pitcher suppresses HR (-0.72).""", blast="good"),
        ],
    },
    {
        "title": "BAL @ STL - Trevor Rogers (L, BAL) vs Cooper Hjerpe (L, STL)",
        "description": "Tail key data: Park boost -17% (stadium -8%, weather -9%). Rogers (HR risk -0.03, vs LHB -1.50, vs RHB +0.53). Hjerpe - MLB debut, no book.",
        "rows": [
            row("Joshua Baez", "R", "+560", 80, "⭐ 🌕 💣", ["vs Rogers"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 94.1 mph EV. Rogers RHB split +0.53, HR risk -0.03. pitcher risk below avg (-0.03); park/weather net drag (-17%).""", blast="high"),
            row("JJ Wetherholt", "L", "+830", 58, "💎", ["vs Rogers"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.6 mph EV. Rogers LHB split -1.50, HR risk -0.03. tough split lane (-1.50); pitcher risk below avg (-0.03).""", blast="good"),
            row("Jordan Walker", "R", "+480", 65, "🌕 💣", ["vs Rogers"], """2 HR, 2 near-HR, 86.9 mph EV. Rogers RHB split +0.53, HR risk -0.03. pitcher risk below avg (-0.03); park/weather net drag (-17%).""", blast="high"),
            row("Alec Burleson", "L", "+750", 58, "", ["vs Rogers"], """0 HR, 93.8 mph EV. Rogers LHB split -1.50, HR risk -0.03. tough split lane (-1.50); pitcher risk below avg (-0.03).""", blast="good"),
            row("Ramon Urias", "R", "+875", 61, "", ["vs Rogers"], """1 HR, 1 near-HR, 92.7 mph EV. Rogers RHB split +0.53, HR risk -0.03. pitcher risk below avg (-0.03); park/weather net drag (-17%).""", blast="good"),
            row("Christian Encarnacion-Strand", "R", "N/A", 68, "⭐", ["vs Hjerpe"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 95.8 mph EV. limited split/risk sample; park/weather net drag (-17%).""", blast="good"),
            row("Pete Alonso", "R", "N/A", 62, "💎", ["vs Hjerpe"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.8 mph EV. limited split/risk sample; park/weather net drag (-17%).""", blast="good"),
            row("Coby Mayo", "R", "N/A", 69, "🌕 💣 💎", ["vs Hjerpe"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 93.3 mph EV. limited split/risk sample; park/weather net drag (-17%).""", blast="high"),
            row("Christian Franklin", "R", "N/A", 58, "", ["vs Hjerpe"], """0 HR, 1 near-HR, 96.1 mph EV. limited split/risk sample; park/weather net drag (-17%).""", blast="good"),
        ],
    },
    {
        "title": "COL @ WSH - Gabriel Hughes (R, COL) vs Jake Irvin 🧤 (R, WSH)",
        "description": "Tail key data: Park boost +18% (stadium +3%, weather +15%). Hughes (HR risk -0.18, vs LHB -0.50, vs RHB +0.66). Irvin 🧤 (HR risk 1.63, vs LHB +1.29, vs RHB +1.36).",
        "rows": [
            row("Andres Chaparro", "R", "N/A", 82, "🌕 💣 💎", ["vs Hughes"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 95.6 mph EV. Hughes RHB split +0.66, HR risk -0.18. pitcher risk below avg (-0.18).""", blast="high"),
            row("Dylan Crews", "R", "+418", 67, "💎", ["vs Hughes"], """Worst Pickz Hidden Gem. 0 HR, 97.7 mph EV. Hughes RHB split +0.66, HR risk -0.18. pitcher risk below avg (-0.18); limited recent HR events.""", blast="good"),
            row("Brady House", "R", "+519", 70, "", ["vs Hughes"], """0 HR, 2 near-HR, 97.2 mph EV. Hughes RHB split +0.66, HR risk -0.18. pitcher risk below avg (-0.18).""", blast="good"),
            row("Daylen Lile", "L", "+460", 63, "🌕 💣", ["vs Hughes"], """2 HR, 2 near-HR, 83.9 mph EV. Hughes LHB split -0.50, HR risk -0.18. tough split lane (-0.50); pitcher risk below avg (-0.18).""", blast="high"),
            row("Hunter Goodman", "R", "+265", 92, "🌕 💣", ["vs Irvin"], """1 HR, 2 near-HR, 91.8 mph EV. Irvin RHB split +1.36, HR risk 1.63.""", blast="good"),
            row("Connor Norby", "R", "+526", 94, "🌕 💣", ["vs Irvin"], """1 HR, 2 near-HR, 95.7 mph EV. Irvin RHB split +1.36, HR risk 1.63.""", blast="good"),
            row("Willi Castro", "S", "+450", 92, "🌕 💣 💎", ["vs Irvin"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.3 mph EV. Irvin SHB→RHB split +1.36, HR risk 1.63.""", blast="good"),
        ],
    },
    {
        "title": "HOU @ NYY - Hayden Wesneski (R, HOU) vs Gerrit Cole (R, NYY)",
        "description": "Tail key data: Park boost +22% (stadium +4%, weather +19%). Wesneski (HR risk -0.22, vs LHB +0.49, vs RHB -0.87). Cole (HR risk -0.48, vs LHB -0.28, vs RHB -0.60).",
        "rows": [
            row("Spencer Jones", "L", "+426", 72, "⭐", ["vs Wesneski"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.8 mph EV. Wesneski LHB split +0.49, HR risk -0.22. pitcher risk below avg (-0.22).""", blast="good"),
            row("Ben Rice", "L", "+294", 78, "🌕 💣 💎", ["vs Wesneski"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 92.8 mph EV. Wesneski LHB split +0.49, HR risk -0.22. pitcher risk below avg (-0.22).""", blast="high"),
            row("Luis Garcia Jr.", "L", "+340", 80, "🌕 💣 💎", ["vs Wesneski"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.5 mph EV. Wesneski LHB split +0.49, HR risk -0.22. pitcher risk below avg (-0.22).""", blast="high"),
            row("Trent Grisham", "L", "+307", 78, "🌕 💣", ["vs Wesneski"], """2 HR, 2 near-HR, 92.9 mph EV. Wesneski LHB split +0.49, HR risk -0.22. pitcher risk below avg (-0.22).""", blast="high"),
            row("Nelson Velazquez", "R", "N/A", 58, "💎", ["vs Cole"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 94.8 mph EV. Cole RHB split -0.60, HR risk -0.48. tough split lane (-0.60); pitcher suppresses HR (-0.48).""", blast="good"),
            row("Jeremy Pena", "R", "+598", 60, "", ["vs Cole"], """1 HR, 2 near-HR, 93.4 mph EV. Cole RHB split -0.60, HR risk -0.48. tough split lane (-0.60); pitcher suppresses HR (-0.48).""", blast="good"),
            row("Isaac Paredes", "R", "+566", 58, "", ["vs Cole"], """1 HR, 1 near-HR, 91.0 mph EV. Cole RHB split -0.60, HR risk -0.48. tough split lane (-0.60); pitcher suppresses HR (-0.48).""", blast="good"),
            row("Yordan Alvarez", "L", "+250", 58, "", ["vs Cole"], """0 HR, 95.5 mph EV. Cole LHB split -0.28, HR risk -0.48. slight split headwind (-0.28); pitcher suppresses HR (-0.48).""", blast="good"),
        ],
    },
    {
        "title": "KC @ TOR - Noah Cameron (L, KC) vs Spencer Arrighetti (R, TOR)",
        "description": "Tail key data: Park boost +14% (stadium +6%, weather +8%). Cameron (HR risk -0.83, vs LHB -0.03, vs RHB -0.71). Arrighetti (HR risk 0.68, vs LHB +1.13, vs RHB +0.04).",
        "rows": [
            row("Kazuma Okamoto", "R", "+408", 58, "⭐", ["vs Cameron"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.4 mph EV. Cameron RHB split -0.71, HR risk -0.83. tough split lane (-0.71); pitcher suppresses HR (-0.83).""", blast="good"),
            row("Daz Cameron", "R", "+660", 58, "💎", ["vs Cameron"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.9 mph EV. Cameron RHB split -0.71, HR risk -0.83. tough split lane (-0.71); pitcher suppresses HR (-0.83).""", blast="good"),
            row("Alejandro Kirk", "R", "+710", 58, "", ["vs Cameron"], """0 HR, 88.7 mph EV. Cameron RHB split -0.71, HR risk -0.83. tough split lane (-0.71); pitcher suppresses HR (-0.83)."""),
            row("Carter Jensen", "L", "+429", 80, "💎", ["vs Arrighetti"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 93.7 mph EV. Arrighetti LHB split +1.13, HR risk 0.68. limited recent HR events.""", blast="good"),
            row("Kyle Isbel", "L", "+1060", 91, "⭐ 🌕 💣", ["vs Arrighetti"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.8 mph EV. Arrighetti LHB split +1.13, HR risk 0.68.""", blast="high"),
            row("Jac Caglianone", "L", "+376", 84, "", ["vs Arrighetti"], """0 HR, 2 near-HR, 96.9 mph EV. Arrighetti LHB split +1.13, HR risk 0.68.""", blast="good"),
        ],
    },
    {
        "title": "LAD @ ATL - Yoshinobu Yamamoto (R, LAD) vs Chris Sale (L, ATL)",
        "description": "Tail key data: Park boost +2% (stadium -3%, weather +5%). Yamamoto (HR risk -0.59, vs LHB -1.03, vs RHB +0.21). Sale (HR risk -1.20, vs LHB -0.88, vs RHB -0.73).",
        "rows": [
            row("Austin Riley", "R", "+650", 58, "⭐", ["vs Yamamoto"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 93.6 mph EV. Yamamoto RHB split +0.21, HR risk -0.59. pitcher suppresses HR (-0.59); limited recent HR events.""", blast="good"),
            row("Drake Baldwin", "L", "+600", 58, "💎", ["vs Yamamoto"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 92.0 mph EV. Yamamoto LHB split -1.03, HR risk -0.59. tough split lane (-1.03); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Michael Harris II", "L", "+600", 58, "", ["vs Yamamoto"], """0 HR, 1 near-HR, 97.4 mph EV. Yamamoto LHB split -1.03, HR risk -0.59. tough split lane (-1.03); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Matt Olson", "L", "+430", 58, "", ["vs Yamamoto"], """0 HR, 2 near-HR, 97.5 mph EV. Yamamoto LHB split -1.03, HR risk -0.59. tough split lane (-1.03); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Mike Yastrzemski", "L", "+830", 58, "", ["vs Yamamoto"], """0 HR, 96.1 mph EV. Yamamoto LHB split -1.03, HR risk -0.59. tough split lane (-1.03); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Teoscar Hernandez", "R", "+560", 58, "⭐", ["vs Sale"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 94.4 mph EV. Sale RHB split -0.73, HR risk -1.20. tough split lane (-0.73); pitcher suppresses HR (-1.20).""", blast="good"),
            row("Shohei Ohtani", "L", "+428", 58, "", ["vs Sale"], """1 HR, 1 near-HR, 94.9 mph EV. Sale LHB split -0.88, HR risk -1.20. tough split lane (-0.88); pitcher suppresses HR (-1.20).""", blast="good"),
            row("Kyle Tucker", "L", "+970", 58, "", ["vs Sale"], """0 HR, 95.0 mph EV. Sale LHB split -0.88, HR risk -1.20. tough split lane (-0.88); pitcher suppresses HR (-1.20).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ NYM - Jacob Misiorowski (R, MIL) vs Sean Manaea 🧤 (L, NYM)",
        "description": "Tail key data: Park boost +13% (stadium -1%, weather +15%). Misiorowski (HR risk -0.06, vs LHB +0.36, vs RHB -0.70). Manaea 🧤 (HR risk 1.62, vs LHB +0.62, vs RHB +1.57).",
        "rows": [
            row("Brett Baty", "L", "+870", 70, "🚀 ⭐", ["vs Misiorowski"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 101.7 mph EV. Misiorowski LHB split +0.36, HR risk -0.06. pitcher risk below avg (-0.06).""", blast="good"),
            row("Luis Robert", "R", "+600", 78, "🌕 💣 💎", ["vs Misiorowski"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 94.1 mph EV. Misiorowski RHB split -0.70, HR risk -0.06. tough split lane (-0.70); pitcher risk below avg (-0.06).""", blast="high"),
            row("Luis Torrens", "R", "+977", 80, "🌕 💣", ["vs Misiorowski"], """3 HR, 3 near-HR, 95.8 mph EV. Misiorowski RHB split -0.70, HR risk -0.06. tough split lane (-0.70); pitcher risk below avg (-0.06).""", blast="high"),
            row("Eric Wagaman", "R", "N/A", 58, "🚀", ["vs Misiorowski"], """0 HR, 105.8 mph EV. Misiorowski RHB split -0.70, HR risk -0.06. tough split lane (-0.70); pitcher risk below avg (-0.06).""", blast="good"),
            row("AJ Ewing", "L", "+1220", 58, "", ["vs Misiorowski"], """0 HR, 1 near-HR, 89.1 mph EV. Misiorowski LHB split +0.36, HR risk -0.06. pitcher risk below avg (-0.06); limited recent HR events."""),
            row("Gary Sanchez", "R", "+430", 91, "🌕 💣 💎", ["vs Manaea"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 90.4 mph EV. Manaea RHB split +1.57, HR risk 1.62.""", blast="good"),
            row("Jake Bauers", "L", "N/A", 94, "🌕 💣", ["vs Manaea"], """2 HR, 2 near-HR, 95.0 mph EV. Manaea LHB split +0.62, HR risk 1.62.""", blast="high"),
            row("Jackson Chourio", "R", "+413", 94, "⭐ 🌕 💣", ["vs Manaea"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.2 mph EV. Manaea RHB split +1.57, HR risk 1.62.""", blast="good"),
            row("Andrew Vaughn", "R", "+542", 91, "🌕 💣 💎", ["vs Manaea"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.0 mph EV. Manaea RHB split +1.57, HR risk 1.62.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-27")

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

    out = ROOT / '_games-0827.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
