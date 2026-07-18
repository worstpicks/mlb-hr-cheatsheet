#!/usr/bin/env python3
"""Generate games[] block for 2026-07-18 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "CJ Abrams (L)",
    "Dalton Rushing (L)",
    "James Wood (L)",
    "Ryan McMahon (L)",
    "Spencer Torkelson (R)",
    "Tyler Soderstrom (L)",
    "Zach Neto (R)",
}

GEMS = {
    "Esmerlyn Valdez (R)",
    "Max Muncy (L)",
}

PLAYER_TEAMS = {
    "Andy Pages (R)": "LAD",
    "Ben Rice (L)": "NYY",
    "Bryce Eldridge (L)": "SF",
    "CJ Abrams (L)": "WSH",
    "Colt Keith (L)": "DET",
    "Dalton Rushing (L)": "LAD",
    "Esmerlyn Valdez (R)": "PIT",
    "JP Crawford (L)": "SEA",
    "James Wood (L)": "WSH",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jose Siri (R)": "LAA",
    "Kyle Tucker (L)": "LAD",
    "Max Muncy (L)": "LAD",
    "Mitch Garver (R)": "SEA",
    "Rafael Devers (L)": "SF",
    "Riley Greene (L)": "DET",
    "Ryan McMahon (L)": "NYY",
    "Spencer Torkelson (R)": "DET",
    "Trent Grisham (L)": "NYY",
    "Tyler Soderstrom (L)": "ATH",
    "Willy Adames (R)": "SF",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("WSH @ ATH", "Littell"),
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
        "title": "DET @ LAA - Tarik Skubal (L, DET) vs Grayson Rodriguez (R, LAA)",
        "description": "Tail key data: Park boost +17% (stadium +9%, weather +8%). Skubal (HR risk 0.35, vs LHB +0.11, vs RHB +0.70). Rodriguez (HR risk 0.12, vs LHB +0.31, vs RHB -0.19).",
        "rows": [
            row("Zach Neto", "R", "+430", 78, "⭐", ["vs Skubal"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 95.0 mph EV. Skubal RHB split +0.70, HR risk 0.35.""", blast="good"),
            row("Jose Siri", "R", "+541", 88, "🌕 💣", ["vs Skubal"], """2 HR, 3 near-HR, 92.6 mph EV. Skubal RHB split +0.70, HR risk 0.35.""", blast="high"),
            row("Spencer Torkelson", "R", "+351", 82, "⭐ 🌕 💣", ["vs Rodriguez"], """Worst Pickz Favorite. 2 HR, 5 near-HR, 94.4 mph EV. Rodriguez RHB split -0.19, HR risk 0.12. slight split headwind (-0.19).""", blast="high"),
            row("Riley Greene", "L", "+310", 80, "🌕 💣", ["vs Rodriguez"], """2 HR, 3 near-HR, 89.4 mph EV. Rodriguez LHB split +0.31, HR risk 0.12.""", blast="high"),
            row("Colt Keith", "L", "+497", 69, "", ["vs Rodriguez"], """1 HR, 2 near-HR, 90.7 mph EV. Rodriguez LHB split +0.31, HR risk 0.12.""", blast="good"),
        ],
    },
    {
        "title": "LAD @ NYY - Emmet Sheehan (R, LAD) vs Ryan Weathers (L, NYY)",
        "description": "Tail key data: Park boost +5% (stadium +3%, weather +1%). Sheehan (HR risk 0.39, vs LHB +0.33, vs RHB +0.35). Weathers (HR risk -0.27, vs LHB +0.29, vs RHB -0.31).",
        "rows": [
            row("Ryan McMahon", "L", "+492", 70, "⭐", ["vs Sheehan"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 93.9 mph EV. Sheehan LHB split +0.33, HR risk 0.39.""", blast="good"),
            row("Ben Rice", "L", "+255", 80, "⭐ 🌕 💣", ["vs Sheehan"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.6 mph EV. Sheehan LHB split +0.33, HR risk 0.39.""", blast="high"),
            row("Jazz Chisholm Jr.", "L", "+360", 58, "", ["vs Sheehan"], """0 HR, 88.7 mph EV. Sheehan LHB split +0.33, HR risk 0.39. limited recent HR events."""),
            row("Trent Grisham", "L", "+310", 73, "", ["vs Sheehan"], """1 HR, 2 near-HR, 97.5 mph EV. Sheehan LHB split +0.33, HR risk 0.39.""", blast="good"),
            row("Dalton Rushing", "L", "+478", 58, "⭐", ["vs Weathers"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 91.5 mph EV. Weathers LHB split +0.29, HR risk -0.27. pitcher risk below avg (-0.27); limited recent HR events."""),
            row("Max Muncy", "L", "+444", 69, "🌕 💣 💎", ["vs Weathers"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 90.2 mph EV. Weathers LHB split +0.29, HR risk -0.27. pitcher risk below avg (-0.27).""", blast="high"),
            row("Andy Pages", "R", "+401", 58, "", ["vs Weathers"], """1 HR, 2 near-HR, 86.6 mph EV. Weathers RHB split -0.31, HR risk -0.27. slight split headwind (-0.31); pitcher risk below avg (-0.27).""", blast="good"),
            row("Kyle Tucker", "L", "+610", 58, "", ["vs Weathers"], """0 HR, 1 near-HR, 90.3 mph EV. Weathers LHB split +0.29, HR risk -0.27. pitcher risk below avg (-0.27); limited recent HR events."""),
        ],
    },
    {
        "title": "PIT @ CLE - TBD (R, PIT) vs Logan Allen (L, CLE)",
        "description": "Tail key data: Park boost -2% (stadium -4%, weather +1%). Away starter risk unavailable. Allen (HR risk 0.01, vs LHB +0.10, vs RHB -0.06).",
        "rows": [
            row("Esmerlyn Valdez", "R", "+330", 64, "💎", ["vs Allen"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 98.2 mph EV. Allen RHB split -0.06, HR risk 0.01. slight split headwind (-0.06).""", blast="good"),
        ],
    },
    {
        "title": "SF @ SEA - Logan Webb (R, SF) vs Bryan Woo (R, SEA)",
        "description": "Tail key data: Park boost -2% (stadium +1%, weather -3%). Webb (HR risk -0.68, vs LHB -0.48, vs RHB -0.42). Woo (HR risk -0.18, vs LHB -0.07, vs RHB -0.22).",
        "rows": [
            row("JP Crawford", "L", "+980", 58, "", ["vs Webb"], """0 HR, 95.3 mph EV. Webb LHB split -0.48, HR risk -0.68. tough split lane (-0.48); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Mitch Garver", "R", "N/A", 58, "", ["vs Webb"], """1 HR, 1 near-HR, 90.0 mph EV. Webb RHB split -0.42, HR risk -0.68. tough split lane (-0.42); pitcher suppresses HR (-0.68).""", blast="good"),
            row("Bryce Eldridge", "L", "+525", 62, "", ["vs Woo"], """1 HR, 1 near-HR, 98.3 mph EV. Woo LHB split -0.07, HR risk -0.18. slight split headwind (-0.07); pitcher risk below avg (-0.18).""", blast="good"),
            row("Rafael Devers", "L", "+324", 71, "🌕 💣", ["vs Woo"], """2 HR, 2 near-HR, 96.4 mph EV. Woo LHB split -0.07, HR risk -0.18. slight split headwind (-0.07); pitcher risk below avg (-0.18).""", blast="high"),
            row("Willy Adames", "R", "+630", 58, "", ["vs Woo"], """1 HR, 1 near-HR, 89.9 mph EV. Woo RHB split -0.22, HR risk -0.18. slight split headwind (-0.22); pitcher risk below avg (-0.18).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ ATH - Zack Littell 🧤 (R, WSH) vs J.T. Ginn (R, ATH)",
        "description": "Tail key data: Park boost +33% (stadium +30%, weather +3%). Littell 🧤 (HR risk 1.25, vs LHB +1.08, vs RHB +0.76). Ginn (HR risk -0.01, vs LHB +0.34, vs RHB -0.40).",
        "rows": [
            row("Tyler Soderstrom", "L", "+280", 96, "⭐ 🌕 💣", ["vs Littell"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.7 mph EV. Littell LHB split +1.08, HR risk 1.25.""", blast="high"),
            row("James Wood", "L", "+236", 91, "🚀 ⭐ 🌕 💣", ["vs Ginn"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 101.7 mph EV. Ginn LHB split +0.34, HR risk -0.01. pitcher risk below avg (-0.01).""", blast="high"),
            row("CJ Abrams", "L", "+345", 67, "⭐", ["vs Ginn"], """Worst Pickz Favorite. 0 HR, 93.4 mph EV. Ginn LHB split +0.34, HR risk -0.01. pitcher risk below avg (-0.01); limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-18")

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
