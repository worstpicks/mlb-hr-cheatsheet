#!/usr/bin/env python3
"""Generate games[] block for 2026-08-10 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Brett Baty (L)",
    "Daulton Varsho (L)",
    "Fernando Tatis Jr. (R)",
    "Jackson Chourio (R)",
    "Jackson Merrill (L)",
    "Jake Burger (R)",
    "Jose Siri (R)",
    "Kyle Tucker (L)",
    "Manny Machado (R)",
    "Matt Olson (L)",
    "Max Muncy (R)",
    "Mickey Moniak (L)",
    "Pete Alonso (R)",
    "Ronald Acuna Jr. (R)",
    "Willi Castro (S)",
    "Willson Contreras (R)",
}

GEMS = {
    "Brandon Nimmo (L)",
    "Coby Mayo (R)",
    "Francisco Alvarez (R)",
    "Ivan Herrera (R)",
    "Jesus Sanchez (L)",
    "Leody Taveras (S)",
    "Osleivis Basabe (R)",
    "Ryan Vilade (R)",
    "Taylor Trammell (L)",
    "Wilyer Abreu (L)",
    "Yandy Diaz (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Brandon Valenzuela (S)": "TOR",
    "Brett Baty (L)": "NYM",
    "Brice Turang (L)": "MIL",
    "Bryce Harper (L)": "PHI",
    "Carter Jensen (L)": "KC",
    "Coby Mayo (R)": "BAL",
    "Corey Seager (L)": "TEX",
    "Daulton Varsho (L)": "HOU",
    "Derek Hill (R)": "PHI",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Henry Bolte (R)": "ATH",
    "Hunter Goodman (R)": "COL",
    "Ivan Herrera (R)": "STL",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jake Burger (R)": "TEX",
    "Jake Rogers (R)": "BOS",
    "Jesus Sanchez (L)": "TOR",
    "Jose Siri (R)": "LAA",
    "Kyle Tucker (L)": "LAD",
    "Lawrence Butler (L)": "ATH",
    "Leody Taveras (S)": "BAL",
    "Manny Machado (R)": "SD",
    "Masataka Yoshida (L)": "BOS",
    "Matt Olson (L)": "ATL",
    "Max Muncy (R)": "ATH",
    "Mickey Moniak (L)": "COL",
    "Mike Yastrzemski (L)": "ATL",
    "Osleivis Basabe (R)": "SF",
    "Pete Alonso (R)": "BAL",
    "Ronald Acuna Jr. (R)": "ATL",
    "Royce Lewis (R)": "MIN",
    "Ryan Vilade (R)": "TB",
    "Ryan Waldschmidt (R)": "ARI",
    "Taylor Trammell (L)": "HOU",
    "Teoscar Hernandez (R)": "LAD",
    "Tim Tawa (R)": "ARI",
    "Willi Castro (S)": "COL",
    "Willson Contreras (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("BOS @ TOR", "Taillon"),
    ("TEX @ LAA", "Detmers"),
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
        "title": "BAL @ MIN - Trevor Rogers (L, BAL) vs Dean Kremer (R, MIN)",
        "description": "Tail key data: Park boost -4% (stadium -7%, weather +3%). Rogers (HR risk -0.41, vs LHB -1.30, vs RHB -0.16). Kremer (HR risk 0.91, vs LHB +0.90, vs RHB +0.84).",
        "rows": [
            row("Royce Lewis", "R", "+489", 58, "", ["vs Rogers"], """0 HR, 1 near-HR, 89.0 mph EV. Rogers RHB split -0.16, HR risk -0.41. slight split headwind (-0.16); pitcher suppresses HR (-0.41)."""),
            row("Pete Alonso", "R", "+350", 87, "⭐", ["vs Kremer"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 97.1 mph EV. Kremer RHB split +0.84, HR risk 0.91. park suppresses carry (-7%).""", blast="good"),
            row("Leody Taveras", "S", "+825", 82, "💎", ["vs Kremer"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.5 mph EV. Kremer SHB→LHB split +0.90, HR risk 0.91. park suppresses carry (-7%).""", blast="good"),
            row("Coby Mayo", "R", "+550", 78, "💎", ["vs Kremer"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 92.8 mph EV. Kremer RHB split +0.84, HR risk 0.91. park suppresses carry (-7%).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ TOR - Sonny Gray (R, BOS) vs Jameson Taillon 🧤 (R, TOR)",
        "description": "Tail key data: Park boost +22% (stadium +7%, weather +16%). Gray (HR risk -0.44, vs LHB -0.40, vs RHB -0.13). Taillon 🧤 (HR risk 1.96, vs LHB +1.55, vs RHB +1.93).",
        "rows": [
            row("Jesus Sanchez", "L", "+550", 58, "💎", ["vs Gray"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 86.7 mph EV. Gray LHB split -0.40, HR risk -0.44. tough split lane (-0.40); pitcher suppresses HR (-0.44).""", blast="good"),
            row("Brandon Valenzuela", "S", "N/A", 60, "", ["vs Gray"], """1 HR, 2 near-HR, 90.0 mph EV. Gray SHB→RHB split -0.13, HR risk -0.44. slight split headwind (-0.13); pitcher suppresses HR (-0.44).""", blast="good"),
            row("Wilyer Abreu", "L", "+290", 98, "🌕 💣 💎", ["vs Taillon"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 94.9 mph EV. Taillon LHB split +1.55, HR risk 1.96.""", blast="high"),
            row("Willson Contreras", "R", "+370", 92, "⭐ 🌕 💣", ["vs Taillon"], """Worst Pickz Favorite. 0 HR, 93.6 mph EV. Taillon RHB split +1.93, HR risk 1.96. limited recent HR events.""", blast="good"),
            row("Masataka Yoshida", "L", "+710", 91, "🌕 💣", ["vs Taillon"], """0 HR, 94.7 mph EV. Taillon LHB split +1.55, HR risk 1.96. limited recent HR events.""", blast="good"),
            row("Jake Rogers", "R", "N/A", 93, "🌕 💣", ["vs Taillon"], """1 HR, 1 near-HR, 89.9 mph EV. Taillon RHB split +1.93, HR risk 1.96.""", blast="good"),
        ],
    },
    {
        "title": "COL @ ARI - Gabriel Hughes (R, COL) vs Michael Soroka (R, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Hughes (HR risk -1.12, vs LHB -0.83, vs RHB -1.08). Soroka (HR risk -0.40, vs LHB -0.19, vs RHB -0.50).",
        "rows": [
            row("Tim Tawa", "R", "+690", 58, "", ["vs Hughes"], """1 HR, 1 near-HR, 92.7 mph EV. Hughes RHB split -1.08, HR risk -1.12. tough split lane (-1.08); pitcher suppresses HR (-1.12).""", blast="good"),
            row("Ryan Waldschmidt", "R", "+1150", 58, "", ["vs Hughes"], """1 HR, 1 near-HR, 95.9 mph EV. Hughes RHB split -1.08, HR risk -1.12. tough split lane (-1.08); pitcher suppresses HR (-1.12).""", blast="good"),
            row("Hunter Goodman", "R", "+384", 58, "", ["vs Soroka"], """1 HR, 2 near-HR, 98.6 mph EV. Soroka RHB split -0.50, HR risk -0.40. tough split lane (-0.50); pitcher suppresses HR (-0.40).""", blast="good"),
            row("Mickey Moniak", "L", "+496", 61, "⭐ 🌕 💣", ["vs Soroka"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.3 mph EV. Soroka LHB split -0.19, HR risk -0.40. slight split headwind (-0.19); pitcher suppresses HR (-0.40).""", blast="high"),
            row("Willi Castro", "S", "+900", 58, "⭐", ["vs Soroka"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 90.0 mph EV. Soroka SHB→LHB split -0.19, HR risk -0.40. slight split headwind (-0.19); pitcher suppresses HR (-0.40).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ SF - Hayden Wesneski (R, HOU) vs Blade Tidwell (R, SF)",
        "description": "Tail key data: Park boost -24% (stadium -15%, weather -9%). Wesneski (HR risk -1.26, vs LHB -0.79, vs RHB -1.01). Tidwell (HR risk -1.09, vs LHB -0.46, vs RHB -1.22).",
        "rows": [
            row("Osleivis Basabe", "R", "N/A", 58, "🌕 💣 💎", ["vs Wesneski"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 88.6 mph EV. Wesneski RHB split -1.01, HR risk -1.26. tough split lane (-1.01); pitcher suppresses HR (-1.26).""", blast="high"),
            row("Taylor Trammell", "L", "N/A", 60, "🌕 💣 💎", ["vs Tidwell"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 95.9 mph EV. Tidwell LHB split -0.46, HR risk -1.09. tough split lane (-0.46); pitcher suppresses HR (-1.09).""", blast="high"),
            row("Daulton Varsho", "L", "N/A", 58, "⭐", ["vs Tidwell"], """Worst Pickz Favorite. 0 HR, 84.2 mph EV. Tidwell LHB split -0.46, HR risk -1.09. tough split lane (-0.46); pitcher suppresses HR (-1.09)."""),
            row("Yordan Alvarez", "L", "N/A", 58, "", ["vs Tidwell"], """0 HR, 96.3 mph EV. Tidwell LHB split -0.46, HR risk -1.09. tough split lane (-0.46); pitcher suppresses HR (-1.09).""", blast="good"),
        ],
    },
    {
        "title": "KC @ LAD - Noah Cameron (L, KC) vs Tarik Skubal (L, LAD)",
        "description": "Tail key data: Park boost +19% (stadium +18%, weather +1%). Cameron (HR risk -0.06, vs LHB +0.49, vs RHB -0.28). Skubal (HR risk -0.58, vs LHB -0.68, vs RHB -0.42).",
        "rows": [
            row("Teoscar Hernandez", "R", "+450", 68, "", ["vs Cameron"], """1 HR, 3 near-HR, 91.5 mph EV. Cameron RHB split -0.28, HR risk -0.06. slight split headwind (-0.28); pitcher risk below avg (-0.06).""", blast="good"),
            row("Kyle Tucker", "L", "+516", 65, "⭐", ["vs Cameron"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 92.6 mph EV. Cameron LHB split +0.49, HR risk -0.06. pitcher risk below avg (-0.06); limited recent HR events.""", blast="good"),
            row("Carter Jensen", "L", "+720", 58, "", ["vs Skubal"], """1 HR, 2 near-HR, 91.9 mph EV. Skubal LHB split -0.68, HR risk -0.58. tough split lane (-0.68); pitcher suppresses HR (-0.58).""", blast="good"),
        ],
    },
    {
        "title": "MIL @ SD - Logan Henderson (R, MIL) vs Casey Mize (R, SD)",
        "description": "Tail key data: Park boost -2% (stadium -5%, weather +3%). Henderson (HR risk 0.44, vs LHB +0.95, vs RHB -0.46). Mize (HR risk -0.24, vs LHB -0.63, vs RHB +0.29).",
        "rows": [
            row("Jackson Merrill", "L", "+555", 86, "⭐ 🌕 💣", ["vs Henderson"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.0 mph EV. Henderson LHB split +0.95, HR risk 0.44.""", blast="high"),
            row("Manny Machado", "R", "+482", 68, "⭐", ["vs Henderson"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.5 mph EV. Henderson RHB split -0.46, HR risk 0.44. tough split lane (-0.46).""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+515", 66, "⭐", ["vs Henderson"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.5 mph EV. Henderson RHB split -0.46, HR risk 0.44. tough split lane (-0.46).""", blast="good"),
            row("Jackson Chourio", "R", "+499", 82, "⭐ 🌕 💣", ["vs Mize"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 99.9 mph EV. Mize RHB split +0.29, HR risk -0.24. pitcher risk below avg (-0.24).""", blast="high"),
            row("Jake Bauers", "L", "+461", 71, "🌕 💣", ["vs Mize"], """2 HR, 3 near-HR, 96.1 mph EV. Mize LHB split -0.63, HR risk -0.24. tough split lane (-0.63); pitcher risk below avg (-0.24).""", blast="high"),
            row("Brice Turang", "L", "+770", 58, "", ["vs Mize"], """0 HR, 96.6 mph EV. Mize LHB split -0.63, HR risk -0.24. tough split lane (-0.63); pitcher risk below avg (-0.24).""", blast="good"),
        ],
    },
    {
        "title": "NYM @ ATL - Christian Scott (R, NYM) vs Bryce Elder (R, ATL)",
        "description": "Tail key data: Park boost +3% (stadium -2%, weather +5%). Scott (HR risk -1.05, vs LHB -0.88, vs RHB -0.83). Elder (HR risk 0.71, vs LHB +0.53, vs RHB +0.86).",
        "rows": [
            row("Matt Olson", "L", "+302", 64, "⭐ 🌕 💣", ["vs Scott"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.7 mph EV. Scott LHB split -0.88, HR risk -1.05. tough split lane (-0.88); pitcher suppresses HR (-1.05).""", blast="high"),
            row("Ronald Acuna Jr.", "R", "+357", 58, "⭐", ["vs Scott"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.8 mph EV. Scott RHB split -0.83, HR risk -1.05. tough split lane (-0.83); pitcher suppresses HR (-1.05).""", blast="good"),
            row("Mike Yastrzemski", "L", "+574", 58, "", ["vs Scott"], """1 HR, 2 near-HR, 92.7 mph EV. Scott LHB split -0.88, HR risk -1.05. tough split lane (-0.88); pitcher suppresses HR (-1.05).""", blast="good"),
            row("Francisco Alvarez", "R", "+451", 85, "🌕 💣 💎", ["vs Elder"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 89.6 mph EV. Elder RHB split +0.86, HR risk 0.71.""", blast="high"),
            row("Brett Baty", "L", "+650", 91, "⭐ 🌕 💣", ["vs Elder"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 95.5 mph EV. Elder LHB split +0.53, HR risk 0.71.""", blast="high"),
        ],
    },
    {
        "title": "PHI @ STL - Andrew Painter (R, PHI) vs Hunter Dobbins (R, STL)",
        "description": "Tail key data: Park boost +6% (stadium -12%, weather +17%). Painter (HR risk 0.72, vs LHB +1.04, vs RHB +0.16). Dobbins (HR risk 0.05, vs LHB -0.29, vs RHB +0.57).",
        "rows": [
            row("Alec Burleson", "L", "+501", 91, "⭐ 🌕 💣", ["vs Painter"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.3 mph EV. Painter LHB split +1.04, HR risk 0.72. park suppresses carry (-12%).""", blast="high"),
            row("Ivan Herrera", "R", "+690", 71, "💎", ["vs Painter"], """Worst Pickz Hidden Gem. 0 HR, 98.1 mph EV. Painter RHB split +0.16, HR risk 0.72. park suppresses carry (-12%); limited recent HR events.""", blast="good"),
            row("Bryce Harper", "L", "+469", 76, "🌕 💣", ["vs Dobbins"], """2 HR, 3 near-HR, 94.2 mph EV. Dobbins LHB split -0.29, HR risk 0.05. slight split headwind (-0.29); park suppresses carry (-12%).""", blast="high"),
            row("Brandon Marsh", "L", "+830", 58, "", ["vs Dobbins"], """0 HR, 95.7 mph EV. Dobbins LHB split -0.29, HR risk 0.05. slight split headwind (-0.29); park suppresses carry (-12%).""", blast="good"),
            row("Derek Hill", "R", "N/A", 66, "", ["vs Dobbins"], """1 HR, 1 near-HR, 91.2 mph EV. Dobbins RHB split +0.57, HR risk 0.05. park suppresses carry (-12%).""", blast="good"),
        ],
    },
    {
        "title": "TB @ ATH - Freddy Peralta (R, TB) vs Jacob Lopez (L, ATH)",
        "description": "Tail key data: Park boost +37% (stadium +29%, weather +9%). Peralta (HR risk 0.46, vs LHB +0.53, vs RHB +0.32). Lopez (HR risk -0.17, vs LHB -0.60, vs RHB -0.05).",
        "rows": [
            row("Max Muncy", "R", "N/A", 91, "⭐ 🌕 💣", ["vs Peralta"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 89.9 mph EV. Peralta RHB split +0.32, HR risk 0.46.""", blast="high"),
            row("Henry Bolte", "R", "+790", 80, "", ["vs Peralta"], """1 HR, 1 near-HR, 92.3 mph EV. Peralta RHB split +0.32, HR risk 0.46.""", blast="good"),
            row("Lawrence Butler", "L", "+427", 77, "", ["vs Peralta"], """0 HR, 1 near-HR, 92.3 mph EV. Peralta LHB split +0.53, HR risk 0.46. limited recent HR events.""", blast="good"),
            row("Yandy Diaz", "R", "+398", 65, "💎", ["vs Lopez"], """Worst Pickz Hidden Gem. 0 HR, 94.2 mph EV. Lopez RHB split -0.05, HR risk -0.17. slight split headwind (-0.05); pitcher risk below avg (-0.17).""", blast="good"),
            row("Ryan Vilade", "R", "+477", 81, "🌕 💣 💎", ["vs Lopez"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 91.0 mph EV. Lopez RHB split -0.05, HR risk -0.17. slight split headwind (-0.05); pitcher risk below avg (-0.17).""", blast="high"),
        ],
    },
    {
        "title": "TEX @ LAA - MacKenzie Gore (L, TEX) vs Reid Detmers 🧤 (L, LAA)",
        "description": "Tail key data: Park boost -2% (stadium -8%, weather +6%). Gore (HR risk 0.43, vs LHB +0.31, vs RHB +0.30). Detmers 🧤 (HR risk 1.15, vs LHB +0.74, vs RHB +0.86).",
        "rows": [
            row("Jose Siri", "R", "+560", 77, "⭐ 🌕 💣", ["vs Gore"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.5 mph EV. Gore RHB split +0.30, HR risk 0.43. park suppresses carry (-8%).""", blast="high"),
            row("Zach Neto", "R", "+427", 58, "", ["vs Gore"], """0 HR, 89.5 mph EV. Gore RHB split +0.30, HR risk 0.43. park suppresses carry (-8%); limited recent HR events."""),
            row("Brandon Nimmo", "L", "+503", 93, "🌕 💣 💎", ["vs Detmers"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 94.7 mph EV. Detmers LHB split +0.74, HR risk 1.15. park suppresses carry (-8%).""", blast="high"),
            row("Jake Burger", "R", "+374", 84, "⭐", ["vs Detmers"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 95.8 mph EV. Detmers RHB split +0.86, HR risk 1.15. park suppresses carry (-8%).""", blast="good"),
            row("Corey Seager", "L", "+330", 75, "", ["vs Detmers"], """1 HR, 1 near-HR, 85.9 mph EV. Detmers LHB split +0.74, HR risk 1.15. park suppresses carry (-8%); lighter EV form (85.9 mph).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-10")

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

    out = ROOT / '_games-0810.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
