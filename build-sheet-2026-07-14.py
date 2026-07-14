#!/usr/bin/env python3
"""Generate games[] block for 2026-07-14 MLB All-Star HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Juan Soto (L)",
    "Junior Caminero (R)",
    "Mike Trout (R)",
}

GEMS = {
    "James Wood (L)",
}

PLAYER_TEAMS = {
    "Ben Rice (L)": "AL",
    "CJ Abrams (L)": "NL",
    "Drake Baldwin (L)": "NL",
    "James Wood (L)": "NL",
    "Juan Soto (L)": "NL",
    "Junior Caminero (R)": "AL",
    "Kyle Schwarber (L)": "NL",
    "Mike Trout (R)": "AL",
    "Randy Arozarena (R)": "AL",
    "Yandy Diaz (R)": "AL",
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
        "title": "AL @ NL - Dylan Cease (R, AL) vs Cristopher Sanchez (L, NL)",
        "description": "Tail key data: Park boost +37% (stadium +13%, weather +24%). Cease (HR risk -0.80, vs LHB +0.90, vs RHB -0.70). Sanchez (HR risk 0.80, vs LHB -0.90, vs RHB +0.70).",
        "rows": [
            row("Juan Soto", "L", "N/A", 73, "⭐", ["vs Cease"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.8 mph EV. Cease LHB split +0.90, HR risk -0.80. pitcher suppresses HR (-0.80).""", blast="good"),
            row("James Wood", "L", "N/A", 90, "🌕 💣 💎", ["vs Cease"], """Worst Pickz Hidden Gem. 5 HR, 5 near-HR, 98.7 mph EV. Cease LHB split +0.90, HR risk -0.80. pitcher suppresses HR (-0.80).""", blast="high"),
            row("Drake Baldwin", "L", "N/A", 67, "", ["vs Cease"], """0 HR, 95.1 mph EV. Cease LHB split +0.90, HR risk -0.80. pitcher suppresses HR (-0.80); limited recent HR events.""", blast="good"),
            row("Kyle Schwarber", "L", "N/A", 72, "", ["vs Cease"], """1 HR, 2 near-HR, 93.1 mph EV. Cease LHB split +0.90, HR risk -0.80. pitcher suppresses HR (-0.80).""", blast="good"),
            row("CJ Abrams", "L", "N/A", 74, "", ["vs Cease"], """1 HR, 2 near-HR, 95.0 mph EV. Cease LHB split +0.90, HR risk -0.80. pitcher suppresses HR (-0.80).""", blast="good"),
            row("Mike Trout", "R", "N/A", 80, "⭐", ["vs Sanchez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 83.9 mph EV. Sanchez RHB split +0.70, HR risk 0.80. lighter EV form (83.9 mph).""", blast="good"),
            row("Ben Rice", "L", "N/A", 70, "", ["vs Sanchez"], """1 HR, 1 near-HR, 86.7 mph EV. Sanchez LHB split -0.90, HR risk 0.80. tough split lane (-0.90); lighter EV form (86.7 mph).""", blast="good"),
            row("Junior Caminero", "R", "N/A", 95, "🚀 ⭐ 🌕 💣", ["vs Sanchez"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 101.7 mph EV. Sanchez RHB split +0.70, HR risk 0.80.""", blast="high"),
            row("Randy Arozarena", "R", "N/A", 75, "", ["vs Sanchez"], """0 HR, 91.4 mph EV. Sanchez RHB split +0.70, HR risk 0.80. limited recent HR events."""),
            row("Yandy Diaz", "R", "N/A", 80, "", ["vs Sanchez"], """0 HR, 92.4 mph EV. Sanchez RHB split +0.70, HR risk 0.80. limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-14")

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
