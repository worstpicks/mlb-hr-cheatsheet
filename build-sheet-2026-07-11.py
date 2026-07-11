#!/usr/bin/env python3
"""Generate games[] block for 2026-07-11 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "JJ Bleday (L)",
    "Jac Caglianone (L)",
    "Max Muncy (L)",
    "Pete Alonso (R)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Max Kepler (L)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Austin Riley (R)": "ATL",
    "Brandon Nimmo (L)": "TEX",
    "Bryce Harper (L)": "PHI",
    "Coby Mayo (R)": "BAL",
    "Dansby Swanson (R)": "CHC",
    "Elly De La Cruz (S)": "CIN",
    "George Springer (R)": "TOR",
    "JJ Bleday (L)": "CIN",
    "Jac Caglianone (L)": "KC",
    "Kazuma Okamoto (R)": "TOR",
    "Kyle Schwarber (L)": "PHI",
    "Luis Campusano (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Max Muncy (L)": "LAD",
    "Michael Massey (L)": "KC",
    "Pete Alonso (R)": "BAL",
    "Sal Stewart (R)": "CIN",
    "Seiya Suzuki (R)": "CHC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Torkelson (R)": "DET",
    "Taylor Trammell (L)": "HOU",
    "Tyler O'Neill (R)": "BAL",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("TOR @ SD", "Buehler"),
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
        "title": "ARI @ LAD - Brandon Pfaadt (R, ARI) vs Yoshinobu Yamamoto (R, LAD)",
        "description": "Tail key data: Park boost +21% (stadium +16%, weather +5%). Pfaadt (HR risk 0.78, vs LHB +1.48, vs RHB -0.44). Yamamoto (HR risk -0.96, vs LHB -0.37, vs RHB -0.77).",
        "rows": [
            row("Shohei Ohtani", "L", "+230", 86, "", ["vs Pfaadt"], """1 HR, 2 near-HR, 89.2 mph EV. Pfaadt LHB split +1.48, HR risk 0.78.""", blast="good"),
            row("Max Muncy", "L", "+310", 86, "⭐", ["vs Pfaadt"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 94.0 mph EV. Pfaadt LHB split +1.48, HR risk 0.78. limited recent HR events.""", blast="good"),
            row("Max Kepler", "L", "+560", 61, "💎", ["vs Yamamoto"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 93.2 mph EV. Yamamoto LHB split -0.37, HR risk -0.96. slight split headwind (-0.37); pitcher suppresses HR (-0.96).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ STL - Reynaldo Lopez (R, ATL) vs Matthew Liberatore (L, STL)",
        "description": "Tail key data: Park boost -11% (stadium -10%, weather +0%). Lopez (HR risk -0.67, vs LHB -0.24, vs RHB -0.55). Liberatore (HR risk 0.87, vs LHB +0.21, vs RHB +0.88).",
        "rows": [
            row("Alec Burleson", "L", "+510", 58, "", ["vs Lopez"], """1 HR, 1 near-HR, 88.3 mph EV. Lopez LHB split -0.24, HR risk -0.67. slight split headwind (-0.24); pitcher suppresses HR (-0.67).""", blast="good"),
            row("Matt Olson", "L", "+420", 68, "", ["vs Liberatore"], """0 HR, 1 near-HR, 93.5 mph EV. Liberatore LHB split +0.21, HR risk 0.87. park/weather net drag (-11%); limited recent HR events.""", blast="good"),
            row("Austin Riley", "R", "+610", 74, "", ["vs Liberatore"], """0 HR, 96.7 mph EV. Liberatore RHB split +0.88, HR risk 0.87. park/weather net drag (-11%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "CHC @ CIN - Javier Assad (R, CHC) vs Nick Lodolo (L, CIN)",
        "description": "Tail key data: Park boost +21% (stadium +14%, weather +7%). Assad (HR risk 0.85, vs LHB +1.57, vs RHB -0.35). Lodolo (HR risk -0.84, vs LHB -1.10, vs RHB -0.40).",
        "rows": [
            row("Elly De La Cruz", "S", "+341", 86, "", ["vs Assad"], """0 HR, 95.0 mph EV. Assad SHB→LHB split +1.57, HR risk 0.85. limited recent HR events.""", blast="good"),
            row("Sal Stewart", "R", "+354", 73, "", ["vs Assad"], """1 HR, 1 near-HR, 91.0 mph EV. Assad RHB split -0.35, HR risk 0.85. slight split headwind (-0.35).""", blast="good"),
            row("JJ Bleday", "L", "+291", 89, "⭐ 🌕 💣", ["vs Assad"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.6 mph EV. Assad LHB split +1.57, HR risk 0.85.""", blast="good"),
            row("Seiya Suzuki", "R", "+322", 61, "🌕 💣", ["vs Lodolo"], """2 HR, 2 near-HR, 89.0 mph EV. Lodolo RHB split -0.40, HR risk -0.84. tough split lane (-0.40); pitcher suppresses HR (-0.84).""", blast="high"),
            row("Dansby Swanson", "R", "+403", 58, "", ["vs Lodolo"], """1 HR, 2 near-HR, 91.4 mph EV. Lodolo RHB split -0.40, HR risk -0.84. tough split lane (-0.40); pitcher suppresses HR (-0.84).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ TEX - Peter Lambert (R, HOU) vs Kumar Rocker (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -11%, weather -1%). Lambert (HR risk 0.48, vs LHB +0.13, vs RHB +0.72). Rocker (HR risk -0.19, vs LHB +0.53, vs RHB -0.79).",
        "rows": [
            row("Brandon Nimmo", "L", "+425", 58, "", ["vs Lambert"], """0 HR, 91.8 mph EV. Lambert LHB split +0.13, HR risk 0.48. park/weather net drag (-11%); limited recent HR events."""),
            row("Yordan Alvarez", "L", "+260", 78, "⭐ 🌕 💣", ["vs Rocker"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 98.4 mph EV. Rocker LHB split +0.53, HR risk -0.19. pitcher risk below avg (-0.19); park/weather net drag (-11%).""", blast="high"),
            row("Taylor Trammell", "L", "+625", 74, "🌕 💣", ["vs Rocker"], """2 HR, 3 near-HR, 92.1 mph EV. Rocker LHB split +0.53, HR risk -0.19. pitcher risk below avg (-0.19); park/weather net drag (-11%).""", blast="high"),
        ],
    },
    {
        "title": "KC @ BAL - Noah Cameron (L, KC) vs Kyle Bradish (R, BAL)",
        "description": "Tail key data: Park boost -10% (stadium -3%, weather -7%). Cameron (HR risk -0.07, vs LHB -0.24, vs RHB +0.16). Bradish (HR risk -0.36, vs LHB -0.02, vs RHB -0.33).",
        "rows": [
            row("Pete Alonso", "R", "+398", 58, "⭐", ["vs Cameron"], """Worst Pickz Favorite. 0 HR, 97.4 mph EV. Cameron RHB split +0.16, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-10%).""", blast="good"),
            row("Coby Mayo", "R", "+390", 72, "🌕 💣", ["vs Cameron"], """2 HR, 2 near-HR, 98.1 mph EV. Cameron RHB split +0.16, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-10%).""", blast="high"),
            row("Tyler O'Neill", "R", "+409", 61, "", ["vs Cameron"], """1 HR, 1 near-HR, 94.6 mph EV. Cameron RHB split +0.16, HR risk -0.07. pitcher risk below avg (-0.07); park/weather net drag (-10%).""", blast="good"),
            row("Jac Caglianone", "L", "+425", 76, "🚀 ⭐ 🌕 💣", ["vs Bradish"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 100.5 mph EV. Bradish LHB split -0.02, HR risk -0.36. slight split headwind (-0.02); pitcher risk below avg (-0.36).""", blast="high"),
            row("Michael Massey", "L", "+680", 58, "", ["vs Bradish"], """0 HR, 2 near-HR, 94.7 mph EV. Bradish LHB split -0.02, HR risk -0.36. slight split headwind (-0.02); pitcher risk below avg (-0.36).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ DET - Cristopher Sanchez (L, PHI) vs Casey Mize (R, DET)",
        "description": "Tail key data: Park boost +5% (stadium -11%, weather +16%). Sanchez (HR risk 0.43, vs LHB -1.41, vs RHB +0.76). Mize (HR risk -0.59, vs LHB -0.51, vs RHB -0.13).",
        "rows": [
            row("Spencer Torkelson", "R", "+480", 69, "", ["vs Sanchez"], """1 HR, 1 near-HR, 86.4 mph EV. Sanchez RHB split +0.76, HR risk 0.43. park suppresses carry (-11%); lighter EV form (86.4 mph).""", blast="good"),
            row("Kyle Schwarber", "L", "+240", 58, "", ["vs Mize"], """1 HR, 2 near-HR, 94.0 mph EV. Mize LHB split -0.51, HR risk -0.59. tough split lane (-0.51); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Bryce Harper", "L", "+370", 58, "", ["vs Mize"], """1 HR, 1 near-HR, 91.1 mph EV. Mize LHB split -0.51, HR risk -0.59. tough split lane (-0.51); pitcher suppresses HR (-0.59).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ SD - Trey Yesavage (R, TOR) vs Walker Buehler 🧤 (R, SD)",
        "description": "Tail key data: Park boost -1% (stadium -4%, weather +3%). Yesavage (HR risk -0.28, vs LHB -0.35, vs RHB +0.09). Buehler 🧤 (HR risk 1.04, vs LHB -0.09, vs RHB +1.77).",
        "rows": [
            row("Luis Campusano", "R", "+630", 61, "", ["vs Yesavage"], """1 HR, 1 near-HR, 94.5 mph EV. Yesavage RHB split +0.09, HR risk -0.28. pitcher risk below avg (-0.28).""", blast="good"),
            row("Kazuma Okamoto", "R", "+390", 92, "🌕 💣", ["vs Buehler"], """2 HR, 2 near-HR, 89.4 mph EV. Buehler RHB split +1.77, HR risk 1.04.""", blast="high"),
            row("George Springer", "R", "+490", 89, "🌕 💣", ["vs Buehler"], """1 HR, 1 near-HR, 92.3 mph EV. Buehler RHB split +1.77, HR risk 1.04.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-11")

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

    out = ROOT / '_games-0711.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
