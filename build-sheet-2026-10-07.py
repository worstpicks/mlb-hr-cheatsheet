#!/usr/bin/env python3
"""Generate games[] block for 2026-10-07 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Drake Baldwin (L)",
    "Fernando Tatis Jr. (R)",
    "Giancarlo Stanton (R)",
    "Jo Adell (R)",
    "Junior Caminero (R)",
    "Manny Machado (R)",
    "Ty France (R)",
}

GEMS = {
    "Austin Wells (L)",
    "Max Muncy (L)",
    "Ozzie Albies (S)",
    "William Contreras (R)",
}

PLAYER_TEAMS = {
    "Andrew Benintendi (L)": "CWS",
    "Andy Pages (R)": "LAD",
    "Austin Wells (L)": "NYY",
    "Ben Rice (L)": "NYY",
    "Braden Montgomery (S)": "CWS",
    "Cody Bellinger (L)": "NYY",
    "Drake Baldwin (L)": "ATL",
    "Fernando Tatis Jr. (R)": "SD",
    "Freddie Freeman (L)": "LAD",
    "Garrett Mitchell (L)": "MIL",
    "Giancarlo Stanton (R)": "NYY",
    "Jackson Chourio (R)": "MIL",
    "Jo Adell (R)": "CLE",
    "Jose Ramirez (S)": "CLE",
    "Junior Caminero (R)": "TB",
    "Manny Machado (R)": "SD",
    "Max Muncy (L)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Ozzie Albies (S)": "ATL",
    "Patrick Bailey (S)": "CLE",
    "Ronald Acuna Jr. (R)": "ATL",
    "Rowdy Tellez (L)": "ATL",
    "Shohei Ohtani (L)": "LAD",
    "Teoscar Hernandez (R)": "LAD",
    "Ty France (R)": "SD",
    "Victor Mesa Jr. (L)": "TB",
    "William Contreras (R)": "MIL",
}

BUM_MATCHUPS = {
}

def odds_text(odds):
    return "Listed prop - Over 0.5 HR" if odds == "N/A" else f"Listed {odds} - Over 0.5 HR"

def row(name, hand, odds, score, emojis, chips, note, blast=None, contact=None):
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
    if contact:
        item["contact"] = contact
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
        "title": "CLE @ CWS - Foster Griffin (L, CLE) vs Davis Martin (R, CWS)",
        "kLines": {'Griffin': {'k': 5.2, 'lo': 4, 'hi': 7, 'bf': 23.0, 'matchupK': 22.8, 'ownK': 20.3}, 'Martin': {'k': 3.1, 'lo': 2, 'hi': 5, 'bf': 21.4, 'matchupK': 14.7, 'ownK': 14.1}},
        "description": "Tail key data: Park boost -4% (stadium -4%, weather +0%). Griffin (HR risk -1.11, vs LHB -0.60, vs RHB -0.65). Martin (HR risk 0.13, vs LHB -0.13, vs RHB +0.22).",
        "rows": [
            row("Munetaka Murakami", "L", "+410", 82, "🚀 🌕 💣", ["vs Griffin"], """2 HR, 2 near-HR, 102.4 mph EV, 50.0% barrels. Griffin LHB split -0.60, HR risk -1.11 (risk carried from 9/23). tough split lane (-0.60); pitcher suppresses HR (-1.11).""", blast="high", contact={'stars': 1, 'k': 29.2, 'batterK': 41.2, 'batterWhiff': 41.3, 'pitcherK': 20.3}),
            row("Braden Montgomery", "S", "+1060", 49, "", ["vs Griffin"], """0 HR, 97.3 mph EV. Griffin SHB→RHB split -0.65, HR risk -1.11 (risk carried from 9/23). tough split lane (-0.65); pitcher suppresses HR (-1.11).""", blast="good", contact={'stars': 3, 'k': 22.4, 'batterK': 19.4, 'batterWhiff': 33.3, 'pitcherK': 20.3}),
            row("Andrew Benintendi", "L", "+650", 59, "", ["vs Griffin"], """1 HR, 1 near-HR, 90.8 mph EV, 12.5% barrels. Griffin LHB split -0.60, HR risk -1.11 (risk carried from 9/23). tough split lane (-0.60); pitcher suppresses HR (-1.11).""", blast="good", contact={'stars': 3, 'k': 22.4, 'batterK': 27.3, 'batterWhiff': 27.3, 'pitcherK': 20.3}),
            row("Jo Adell", "R", "+540", 65, "⭐", ["vs Martin"], """Worst Pickz Favorite. 0 HR, 98.4 mph EV. Martin RHB split +0.22, HR risk 0.13 (risk carried from 9/26). limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.7, 'batterK': 24.4, 'batterWhiff': 28.9, 'pitcherK': 14.1}),
            row("Jose Ramirez", "S", "+570", 57, "", ["vs Martin"], """0 HR, 95.7 mph EV. Martin SHB→LHB split -0.13, HR risk 0.13 (risk carried from 9/26). slight split headwind (-0.13); limited recent HR events.""", blast="good", contact={'stars': 5, 'k': 13.8, 'batterK': 11.1, 'batterWhiff': 13.0, 'pitcherK': 14.1}),
            row("Patrick Bailey", "S", "+930", 64, "", ["vs Martin"], """0 HR, 98.7 mph EV. Martin SHB→LHB split -0.13, HR risk 0.13 (risk carried from 9/26). slight split headwind (-0.13); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.1, 'batterK': 35.6, 'batterWhiff': 29.1, 'pitcherK': 14.1}),
        ],
    },
    {
        "title": "LAD @ ATL - Tyler Glasnow (R, LAD) vs Tyler Mahle (R, ATL)",
        "kLines": {'Glasnow': {'k': 6.8, 'lo': 5, 'hi': 8, 'bf': 22.0, 'matchupK': 30.7, 'ownK': 35.0}, 'Mahle': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 22.6, 'matchupK': 23.5, 'ownK': 24.3}},
        "description": "Tail key data: Park boost +3% (stadium -2%, weather +5%). Glasnow (HR risk -0.23, vs LHB +0.88, vs RHB -0.67). Mahle (HR risk -0.59, vs LHB +0.29, vs RHB -0.68).",
        "rows": [
            row("Drake Baldwin", "L", "+525", 90, "⭐ 🌕 💣", ["vs Glasnow"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 94.0 mph EV, 25.0% barrels. Glasnow LHB split +0.88, HR risk -0.23. pitcher risk below avg (-0.23).""", blast="good", contact={'stars': 1, 'k': 28.6, 'batterK': 21.7, 'batterWhiff': 23.6, 'pitcherK': 35.0}),
            row("Rowdy Tellez", "L", "N/A", 73, "", ["vs Glasnow"], """1 HR, 1 near-HR, 90.4 mph EV, 50.0% barrels. Glasnow LHB split +0.88, HR risk -0.23. pitcher risk below avg (-0.23).""", blast="good", contact={'stars': 1, 'k': 29.7, 'batterK': 27.3, 'batterWhiff': 30.4, 'pitcherK': 35.0}),
            row("Ozzie Albies", "S", "+800", 74, "💎", ["vs Glasnow"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 92.8 mph EV, 37.5% barrels. Glasnow SHB→LHB split +0.88, HR risk -0.23. pitcher risk below avg (-0.23).""", blast="good", contact={'stars': 1, 'k': 30.1, 'batterK': 23.4, 'batterWhiff': 28.0, 'pitcherK': 35.0}),
            row("Ronald Acuna Jr.", "R", "+517", 48, "", ["vs Glasnow"], """0 HR, 90.8 mph EV. Glasnow RHB split -0.67, HR risk -0.23. tough split lane (-0.67); pitcher risk below avg (-0.23).""", contact={'stars': 2, 'k': 26.2, 'batterK': 15.1, 'batterWhiff': 22.9, 'pitcherK': 35.0}),
            row("Max Muncy", "L", "+418", 88, "🌕 💣 💎", ["vs Mahle"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 97.0 mph EV, 25.0% barrels. Mahle LHB split +0.29, HR risk -0.59. pitcher suppresses HR (-0.59).""", blast="high", contact={'stars': 2, 'k': 24.6, 'batterK': 24.1, 'batterWhiff': 28.9, 'pitcherK': 24.3}),
            row("Shohei Ohtani", "L", "+310", 72, "", ["vs Mahle"], """0 HR, 92.4 mph EV, 37.5% barrels. Mahle LHB split +0.29, HR risk -0.59. pitcher suppresses HR (-0.59); limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 28.7, 'batterK': 32.3, 'batterWhiff': 36.8, 'pitcherK': 24.3}),
            row("Freddie Freeman", "L", "+660", 57, "", ["vs Mahle"], """0 HR, 1 near-HR, 91.7 mph EV, 12.5% barrels. Mahle LHB split +0.29, HR risk -0.59. pitcher suppresses HR (-0.59); limited recent HR events.""", contact={'stars': 2, 'k': 26.3, 'batterK': 27.1, 'batterWhiff': 33.1, 'pitcherK': 24.3}),
            row("Andy Pages", "R", "+720", 69, "", ["vs Mahle"], """1 HR, 1 near-HR, 92.7 mph EV, 12.5% barrels. Mahle RHB split -0.68, HR risk -0.59. tough split lane (-0.68); pitcher suppresses HR (-0.59).""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 18.1, 'batterWhiff': 19.6, 'pitcherK': 24.3}),
            row("Teoscar Hernandez", "R", "+525", 70, "", ["vs Mahle"], """1 HR, 2 near-HR, 95.2 mph EV, 25.0% barrels. Mahle RHB split -0.68, HR risk -0.59. tough split lane (-0.68); pitcher suppresses HR (-0.59).""", blast="good", contact={'stars': 2, 'k': 26.8, 'batterK': 28.4, 'batterWhiff': 34.0, 'pitcherK': 24.3}),
        ],
    },
    {
        "title": "MIL @ SD - Robert Gasser (L, MIL) vs Walker Buehler (R, SD)",
        "kLines": {'Gasser': {'k': 5.0, 'lo': 3, 'hi': 7, 'bf': 21.9, 'matchupK': 22.9, 'ownK': 23.2}, 'Buehler': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 20.6, 'matchupK': 21.6, 'ownK': 19.9}},
        "description": "Tail key data: Park boost -5% (stadium -3%, weather -2%). Gasser (HR risk 0.35, vs LHB -0.21, vs RHB +0.31). Buehler (HR risk 0.61, vs LHB +0.87, vs RHB +0.27).",
        "rows": [
            row("Manny Machado", "R", "+492", 86, "🚀 ⭐ 🌕 💣", ["vs Gasser"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 100.6 mph EV, 25.0% barrels. Gasser RHB split +0.31, HR risk 0.35 (risk carried from 9/7). park/weather net drag (-5%).""", blast="high", contact={'stars': 3, 'k': 21.3, 'batterK': 19.5, 'batterWhiff': 21.8, 'pitcherK': 23.2}),
            row("Fernando Tatis Jr.", "R", "+411", 91, "⭐ 🌕 💣", ["vs Gasser"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.0 mph EV, 25.0% barrels. Gasser RHB split +0.31, HR risk 0.35 (risk carried from 9/7). park/weather net drag (-5%).""", blast="high", contact={'stars': 3, 'k': 20.4, 'batterK': 17.6, 'batterWhiff': 19.7, 'pitcherK': 23.2}),
            row("Ty France", "R", "+690", 71, "⭐", ["vs Gasser"], """Worst Pickz Favorite. 0 HR, 97.0 mph EV. Gasser RHB split +0.31, HR risk 0.35 (risk carried from 9/7). park/weather net drag (-5%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.4, 'batterK': 20.9, 'batterWhiff': 30.5, 'pitcherK': 23.2}),
            row("William Contreras", "R", "+680", 79, "💎", ["vs Buehler"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.2 mph EV. Buehler RHB split +0.27, HR risk 0.61. park/weather net drag (-5%).""", blast="good", contact={'stars': 3, 'k': 20.3, 'batterK': 20.9, 'batterWhiff': 23.1, 'pitcherK': 19.9}),
            row("Jackson Chourio", "R", "+490", 67, "", ["vs Buehler"], """0 HR, 90.9 mph EV, 12.5% barrels. Buehler RHB split +0.27, HR risk 0.61. park/weather net drag (-5%); limited recent HR events.""", contact={'stars': 3, 'k': 20.8, 'batterK': 20.5, 'batterWhiff': 26.6, 'pitcherK': 19.9}),
            row("Garrett Mitchell", "L", "+940", 82, "", ["vs Buehler"], """0 HR, 94.7 mph EV. Buehler LHB split +0.87, HR risk 0.61. park/weather net drag (-5%); limited recent HR events.""", blast="good", contact={'stars': 2, 'k': 24.1, 'batterK': 30.3, 'batterWhiff': 31.8, 'pitcherK': 19.9}),
        ],
    },
    {
        "title": "TB @ NYY - Nick Martinez (R, TB) vs Max Fried (L, NYY)",
        "kLines": {'Martinez': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 23.0, 'matchupK': 19.4, 'ownK': 17.8}, 'Fried': {'k': 5.6, 'lo': 4, 'hi': 7, 'bf': 21.7, 'matchupK': 25.8, 'ownK': 27.8}},
        "description": "Tail key data: Park boost +9% (stadium +6%, weather +3%). Martinez (HR risk -0.18, vs LHB +0.20, vs RHB -0.26). Fried (HR risk -1.06, vs LHB -0.82, vs RHB -0.57).",
        "rows": [
            row("Ben Rice", "L", "+340", 92, "⭐ 🌕 💣", ["vs Martinez"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 96.1 mph EV, 25.0% barrels. Martinez LHB split +0.20, HR risk -0.18. pitcher risk below avg (-0.18).""", blast="high", contact={'stars': 4, 'k': 18.7, 'batterK': 20.0, 'batterWhiff': 22.1, 'pitcherK': 17.8}),
            row("Giancarlo Stanton", "R", "N/A", 87, "🚀 ⭐ 🌕 💣", ["vs Martinez"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 102.3 mph EV, 37.5% barrels. Martinez RHB split -0.26, HR risk -0.18. slight split headwind (-0.26); pitcher risk below avg (-0.18).""", blast="high", contact={'stars': 2, 'k': 24.6, 'batterK': 31.3, 'batterWhiff': 40.0, 'pitcherK': 17.8}),
            row("Austin Wells", "L", "+521", 73, "💎", ["vs Martinez"], """Worst Pickz Hidden Gem. 0 HR, 99.4 mph EV, 12.5% barrels. Martinez LHB split +0.20, HR risk -0.18. pitcher risk below avg (-0.18); limited recent HR events.""", blast="good", contact={'stars': 4, 'k': 19.9, 'batterK': 22.7, 'batterWhiff': 24.8, 'pitcherK': 17.8}),
            row("Cody Bellinger", "L", "+540", 71, "", ["vs Martinez"], """1 HR, 1 near-HR, 93.6 mph EV. Martinez LHB split +0.20, HR risk -0.18. pitcher risk below avg (-0.18).""", blast="good", contact={'stars': 4, 'k': 17.6, 'batterK': 16.3, 'batterWhiff': 21.1, 'pitcherK': 17.8}),
            row("Junior Caminero", "R", "+436", 64, "⭐", ["vs Fried"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 90.0 mph EV, 12.5% barrels. Fried RHB split -0.57, HR risk -1.06. tough split lane (-0.57); pitcher suppresses HR (-1.06).""", contact={'stars': 3, 'k': 22.6, 'batterK': 15.9, 'batterWhiff': 21.5, 'pitcherK': 27.8}),
            row("Victor Mesa Jr.", "L", "+620", 65, "", ["vs Fried"], """1 HR, 1 near-HR, 94.8 mph EV, 12.5% barrels. Fried LHB split -0.82, HR risk -1.06. tough split lane (-0.82); pitcher suppresses HR (-1.06).""", blast="good", contact={'stars': 2, 'k': 24.0, 'batterK': 17.6, 'batterWhiff': 25.2, 'pitcherK': 27.8}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-10-07")

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

    out = ROOT / '_games-1007.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
