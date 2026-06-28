#!/usr/bin/env python3
"""Generate games[] block for 2026-06-27 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Austin Riley (R)",
    "Ben Rice (L)",
    "Fernando Tatis Jr. (R)",
    "Max Muncy (L)",
    "Mookie Betts (R)",
    "Shohei Ohtani (L)",
}

GEMS = {
}

PLAYER_TEAMS = {
    "Andruw Monasterio (R)": "BOS",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Fernando Tatis Jr. (R)": "SD",
    "Gavin Sheets (L)": "SD",
    "Max Muncy (L)": "LAD",
    "Max Schuemann (R)": "NYY",
    "Mookie Betts (R)": "LAD",
    "Paul Goldschmidt (R)": "NYY",
    "Rafael Devers (L)": "SF",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Jones (L)": "NYY",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
}

BUM_MATCHUPS = {
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
        "title": "ATL @ SF - Chris Sale (L, ATL) vs Robbie Ray (L, SF)",
        "description": "Tail key data: Park boost -6% (stadium -14%, weather +9%). Sale (HR risk -1.18, vs LHB -1.06, vs RHB -0.93). Ray (HR risk -0.25, vs LHB -0.32, vs RHB -0.20).",
        "rows": [
            row("Rafael Devers", "L", "+800", 82, "", ["vs Sale"], """1 HR, 3 near-HR, 96.3 mph EV. Sale LHB split -1.06, HR risk -1.18. tough split lane (-1.06); pitcher suppresses HR (-1.18).""", blast="good"),
            row("Willy Adames", "R", "+660", 80, "🌕 💣", ["vs Sale"], """2 HR, 3 near-HR, 88.0 mph EV. Sale RHB split -0.93, HR risk -1.18. tough split lane (-0.93); pitcher suppresses HR (-1.18).""", blast="high"),
            row("Austin Riley", "R", "+500", 76, "🚀 ⭐", ["vs Ray"], """Worst Pickz Favorite. 0 HR, 100.3 mph EV. Ray RHB split -0.20, HR risk -0.25. slight split headwind (-0.20); pitcher risk below avg (-0.25).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ SD - Emmet Sheehan (R, LAD) vs Michael King (R, SD)",
        "description": "Tail key data: Park boost -1% (stadium -5%, weather +3%). Sheehan (HR risk 0.45, vs LHB +0.32, vs RHB +0.58). King (HR risk -0.11, vs LHB -0.15, vs RHB +0.00).",
        "rows": [
            row("Gavin Sheets", "L", "+503", 70, "", ["vs Sheehan"], """1 HR, 1 near-HR, 87.8 mph EV. Sheehan LHB split +0.32, HR risk 0.45. lighter EV form (87.8 mph).""", blast="good"),
            row("Fernando Tatis Jr.", "R", "+438", 78, "🚀 ⭐", ["vs Sheehan"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 100.7 mph EV. Sheehan RHB split +0.58, HR risk 0.45. limited recent HR events.""", blast="good"),
            row("Shohei Ohtani", "L", "+243", 90, "⭐ 🌕 💣", ["vs King"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 99.7 mph EV. King LHB split -0.15, HR risk -0.11. slight split headwind (-0.15); pitcher risk below avg (-0.11).""", blast="high"),
            row("Mookie Betts", "R", "+630", 87, "⭐ 🌕 💣", ["vs King"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 91.0 mph EV. King RHB split +0.00, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="high"),
            row("Max Muncy", "L", "+405", 66, "⭐", ["vs King"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 89.9 mph EV. King LHB split -0.15, HR risk -0.11. slight split headwind (-0.15); pitcher risk below avg (-0.11)."""),
        ],
    },
    {
        "title": "NYY @ BOS - Carlos Rodon (L, NYY) vs Sonny Gray (R, BOS)",
        "description": "Tail key data: Park boost +3% (stadium -6%, weather +9%). Rodon (HR risk -0.53, vs LHB -0.10, vs RHB -0.54). Gray (HR risk -0.38, vs LHB -0.21, vs RHB -0.64).",
        "rows": [
            row("Willson Contreras", "R", "+434", 73, "", ["vs Rodon"], """1 HR, 2 near-HR, 88.8 mph EV. Rodon RHB split -0.54, HR risk -0.53. tough split lane (-0.54); pitcher suppresses HR (-0.53).""", blast="good"),
            row("Andruw Monasterio", "R", "+950", 70, "", ["vs Rodon"], """1 HR, 1 near-HR, 88.5 mph EV. Rodon RHB split -0.54, HR risk -0.53. tough split lane (-0.54); pitcher suppresses HR (-0.53).""", blast="good"),
            row("Ben Rice", "L", "+350", 98, "⭐ 🌕 💣", ["vs Gray"], """Worst Pickz Favorite. 3 HR, 6 near-HR, 98.0 mph EV. Gray LHB split -0.21, HR risk -0.38. slight split headwind (-0.21); pitcher risk below avg (-0.38).""", blast="high"),
            row("Max Schuemann", "R", "N/A", 71, "", ["vs Gray"], """0 HR, 95.4 mph EV. Gray RHB split -0.64, HR risk -0.38. tough split lane (-0.64); pitcher risk below avg (-0.38).""", blast="good"),
            row("Paul Goldschmidt", "R", "+570", 62, "", ["vs Gray"], """0 HR, 84.0 mph EV. Gray RHB split -0.64, HR risk -0.38. tough split lane (-0.64); pitcher risk below avg (-0.38)."""),
            row("Spencer Jones", "L", "+690", 77, "", ["vs Gray"], """1 HR, 97.4 mph EV. Gray LHB split -0.21, HR risk -0.38. slight split headwind (-0.21); pitcher risk below avg (-0.38).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-28")

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

    out = ROOT / '_games-0628.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
