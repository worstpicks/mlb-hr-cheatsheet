#!/usr/bin/env python3
"""Generate games[] block for 2026-07-16 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Bryce Harper (L)",
    "Juan Soto (L)",
}

GEMS = {
    "Brett Baty (L)",
    "Edmundo Sosa (R)",
}

PLAYER_TEAMS = {
    "Brett Baty (L)": "NYM",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Edmundo Sosa (R)": "PHI",
    "Francisco Lindor (S)": "NYM",
    "Juan Soto (L)": "NYM",
    "Kyle Schwarber (L)": "PHI",
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
        "title": "NYM @ PHI - Christian Scott (R, NYM) vs Aaron Nola (R, PHI)",
        "description": "Tail key data: Park boost +30% (stadium +14%, weather +16%). Scott (HR risk -0.40, vs LHB +0.40, vs RHB -0.20). Nola (HR risk 0.40, vs LHB -0.40, vs RHB +0.20).",
        "rows": [
            row("Juan Soto", "L", "+179", 90, "⭐ 🌕 💣", ["vs Nola"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 93.4 mph EV. Nola LHB split -0.40, HR risk 0.40. tough split lane (-0.40).""", blast="high"),
            row("Brett Baty", "L", "+580", 75, "💎", ["vs Nola"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 99.2 mph EV. Nola LHB split -0.40, HR risk 0.40. tough split lane (-0.40).""", blast="good"),
            row("Francisco Lindor", "S", "+225", 80, "", ["vs Nola"], """1 HR, 2 near-HR, 94.7 mph EV. Nola SHB→RHB split +0.20, HR risk 0.40.""", blast="good"),
            row("Edmundo Sosa", "R", "N/A", 66, "💎", ["vs Scott"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.4 mph EV. Scott RHB split -0.20, HR risk -0.40. slight split headwind (-0.20); pitcher suppresses HR (-0.40).""", blast="good"),
            row("Bryson Stott", "L", "+273", 66, "", ["vs Scott"], """0 HR, 1 near-HR, 94.4 mph EV. Scott LHB split +0.40, HR risk -0.40. pitcher suppresses HR (-0.40); limited recent HR events.""", blast="good"),
            row("Kyle Schwarber", "L", "+124", 73, "🚀", ["vs Scott"], """1 HR, 2 near-HR, 104.4 mph EV. Scott LHB split +0.40, HR risk -0.40. pitcher suppresses HR (-0.40).""", blast="good"),
            row("Bryce Harper", "L", "+158", 76, "⭐ 🌕 💣", ["vs Scott"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 91.0 mph EV. Scott LHB split +0.40, HR risk -0.40. pitcher suppresses HR (-0.40).""", blast="high"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-16")

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
