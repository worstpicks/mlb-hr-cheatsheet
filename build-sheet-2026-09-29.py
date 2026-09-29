#!/usr/bin/env python3
"""Generate games[] block for 2026-09-29 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Bohm (R)",
    "Alex Bregman (R)",
    "Roman Anthony (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Ben Rice (L)",
    "Cody Bellinger (L)",
    "Heliot Ramos (R)",
    "Munetaka Murakami (L)",
    "Trea Turner (R)",
    "Yainer Diaz (R)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BOS",
    "Alec Bohm (R)": "PHI",
    "Alex Bregman (R)": "CHC",
    "Austin Riley (R)": "ATL",
    "Ben Rice (L)": "NYY",
    "Braden Montgomery (S)": "CWS",
    "Brewer Hicklen (R)": "ATL",
    "Ceddanne Rafaela (R)": "BOS",
    "Christian Walker (R)": "HOU",
    "Cody Bellinger (L)": "NYY",
    "Edmundo Sosa (R)": "PHI",
    "Fernando Tatis Jr. (R)": "SD",
    "George Lombard Jr. (R)": "NYY",
    "Heliot Ramos (R)": "NYY",
    "Jackson Merrill (L)": "SD",
    "Jarren Duran (L)": "BOS",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Teel (L)": "CWS",
    "Luis Garcia Jr. (L)": "NYY",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Munetaka Murakami (L)": "CWS",
    "Pete Crow Armstrong (L)": "CHC",
    "Roman Anthony (L)": "BOS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Spencer Jones (L)": "NYY",
    "Trea Turner (R)": "PHI",
    "Ty France (R)": "SD",
    "Yainer Diaz (R)": "HOU",
    "Yordan Alvarez (L)": "HOU",
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
        "title": "BOS @ NYY - Payton Tolle (L, BOS) vs Cam Schlittler (R, NYY)",
        "kLines": {'Tolle': {'k': 6.9, 'lo': 5, 'hi': 9, 'bf': 22.9, 'matchupK': 30.3, 'ownK': 31.8}, 'Schlittler': {'k': 7.2, 'lo': 6, 'hi': 9, 'bf': 22.9, 'matchupK': 31.4, 'ownK': 33.2}},
        "description": "Tail key data: Park boost -4% (stadium +6%, weather -10%). Tolle (HR risk 0.60, vs LHB +0.20, vs RHB +0.43). Schlittler (HR risk -0.21, vs LHB +0.02, vs RHB -0.08).",
        "rows": [
            row("Luis Garcia Jr.", "L", "N/A", 81, "", ["vs Tolle"], """0 HR, 1 near-HR, 97.7 mph EV, 12.5% barrels. Tolle LHB split +0.20, HR risk 0.60. weather carry headwind (-10%); limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 29.0, 'batterK': 26.3, 'batterWhiff': 26.8, 'pitcherK': 31.8}),
            row("Heliot Ramos", "R", "+577", 87, "🌕 💣 💎", ["vs Tolle"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 98.2 mph EV, 25.0% barrels. Tolle RHB split +0.43, HR risk 0.60. weather carry headwind (-10%); limited recent HR events.""", blast="high", contact={'stars': 1, 'k': 30.1, 'batterK': 26.8, 'batterWhiff': 31.5, 'pitcherK': 31.8}),
            row("Spencer Jones", "L", "+500", 70, "", ["vs Tolle"], """0 HR, 87.9 mph EV, 12.5% barrels. Tolle LHB split +0.20, HR risk 0.60. weather carry headwind (-10%); limited recent HR events.""", contact={'stars': 1, 'k': 36.0, 'batterK': 39.8, 'batterWhiff': 40.4, 'pitcherK': 31.8}),
            row("Ben Rice", "L", "+478", 86, "💎", ["vs Tolle"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.6 mph EV, 12.5% barrels. Tolle LHB split +0.20, HR risk 0.60. weather carry headwind (-10%).""", blast="good", contact={'stars': 2, 'k': 26.1, 'batterK': 20.0, 'batterWhiff': 22.1, 'pitcherK': 31.8}),
            row("George Lombard Jr.", "R", "+1280", 79, "", ["vs Tolle"], """1 HR, 2 near-HR, 94.6 mph EV, 12.5% barrels. Tolle RHB split +0.43, HR risk 0.60. weather carry headwind (-10%).""", blast="good", contact={'stars': 1, 'k': 28.7, 'batterK': 26.2, 'batterWhiff': 24.8, 'pitcherK': 31.8}),
            row("Cody Bellinger", "L", "+640", 60, "💎", ["vs Tolle"], """Worst Pickz Hidden Gem. 0 HR, 88.3 mph EV. Tolle LHB split +0.20, HR risk 0.60. weather carry headwind (-10%); limited recent HR events.""", contact={'stars': 2, 'k': 24.7, 'batterK': 16.3, 'batterWhiff': 21.1, 'pitcherK': 31.8}),
            row("Adley Rutschman", "S", "+860", 51, "", ["vs Schlittler"], """0 HR, 91.9 mph EV. Schlittler SHB→LHB split +0.02, HR risk -0.21. pitcher risk below avg (-0.21); weather carry headwind (-10%).""", contact={'stars': 2, 'k': 25.3, 'batterK': 20.3, 'batterWhiff': 14.7, 'pitcherK': 33.2}),
            row("Roman Anthony", "L", "+650", 70, "⭐", ["vs Schlittler"], """Worst Pickz Favorite. 0 HR, 99.3 mph EV, 12.5% barrels. Schlittler LHB split +0.02, HR risk -0.21. pitcher risk below avg (-0.21); weather carry headwind (-10%).""", blast="good", contact={'stars': 1, 'k': 32.8, 'batterK': 31.8, 'batterWhiff': 32.1, 'pitcherK': 33.2}),
            row("Ceddanne Rafaela", "R", "+1120", 52, "", ["vs Schlittler"], """0 HR, 92.4 mph EV. Schlittler RHB split -0.08, HR risk -0.21. slight split headwind (-0.08); pitcher risk below avg (-0.21).""", blast="good", contact={'stars': 1, 'k': 27.5, 'batterK': 20.7, 'batterWhiff': 24.3, 'pitcherK': 33.2}),
            row("Jarren Duran", "L", "+840", 44, "", ["vs Schlittler"], """0 HR, 80.8 mph EV. Schlittler LHB split +0.02, HR risk -0.21. pitcher risk below avg (-0.21); weather carry headwind (-10%).""", contact={'stars': 1, 'k': 31.2, 'batterK': 25.4, 'batterWhiff': 35.0, 'pitcherK': 33.2}),
        ],
    },
    {
        "title": "CHC @ SD - Matthew Boyd (L, CHC) vs Michael King (R, SD)",
        "kLines": {'Boyd': {'k': 3.8, 'lo': 2, 'hi': 5, 'bf': 23.2, 'matchupK': 16.5, 'ownK': 14.6}, 'King': {'k': 4.5, 'lo': 3, 'hi': 6, 'bf': 23.3, 'matchupK': 19.2, 'ownK': 20.7}},
        "description": "Tail key data: Park boost +4% (stadium -3%, weather +7%). Boyd (HR risk -0.50, vs LHB -0.65, vs RHB -0.39). King (HR risk 0.31, vs LHB +0.59, vs RHB +0.24).",
        "rows": [
            row("Ty France", "R", "+600", 63, "", ["vs Boyd"], """1 HR, 1 near-HR, 95.8 mph EV. Boyd RHB split -0.39, HR risk -0.50. slight split headwind (-0.39); pitcher suppresses HR (-0.50).""", blast="good", contact={'stars': 4, 'k': 18.5, 'batterK': 20.9, 'batterWhiff': 30.5, 'pitcherK': 14.6}),
            row("Fernando Tatis Jr.", "R", "+390", 70, "", ["vs Boyd"], """0 HR, 93.9 mph EV. Boyd RHB split -0.39, HR risk -0.50. slight split headwind (-0.39); pitcher suppresses HR (-0.50).""", blast="good", contact={'stars': 5, 'k': 16.0, 'batterK': 17.6, 'batterWhiff': 19.7, 'pitcherK': 14.6}),
            row("Jackson Merrill", "L", "+680", 85, "🌕 💣", ["vs Boyd"], """2 HR, 2 near-HR, 94.1 mph EV, 25.0% barrels. Boyd LHB split -0.65, HR risk -0.50. tough split lane (-0.65); pitcher suppresses HR (-0.50).""", blast="high", contact={'stars': 4, 'k': 19.2, 'batterK': 22.6, 'batterWhiff': 32.1, 'pitcherK': 14.6}),
            row("Manny Machado", "R", "+423", 65, "", ["vs Boyd"], """0 HR, 98.7 mph EV, 12.5% barrels. Boyd RHB split -0.39, HR risk -0.50. slight split headwind (-0.39); pitcher suppresses HR (-0.50).""", blast="good", contact={'stars': 5, 'k': 16.8, 'batterK': 19.5, 'batterWhiff': 21.8, 'pitcherK': 14.6}),
            row("Alex Bregman", "R", "+760", 86, "⭐ 🌕 💣", ["vs King"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.6 mph EV, 37.5% barrels. King RHB split +0.24, HR risk 0.31.""", blast="high", contact={'stars': 5, 'k': 14.9, 'batterK': 7.3, 'batterWhiff': 10.2, 'pitcherK': 20.7}),
            row("Pete Crow Armstrong", "L", "+350", 79, "", ["vs King"], """0 HR, 92.0 mph EV. King LHB split +0.59, HR risk 0.31. limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 22.2, 'batterWhiff': 24.1, 'pitcherK': 20.7}),
        ],
    },
    {
        "title": "CWS @ HOU - Erick Fedde (R, CWS) vs Tatsuya Imai (R, HOU)",
        "kLines": {'Fedde': {'k': 4.7, 'lo': 3, 'hi': 6, 'bf': 20.7, 'matchupK': 22.6, 'ownK': None}, 'Imai': {'k': 4.4, 'lo': 3, 'hi': 6, 'bf': 18.8, 'matchupK': 23.5, 'ownK': None}},
        "description": "Tail key data: Park boost +7% (stadium +7%, weather +0%). Fedde (BAA vs LHB .247, vs RHB .267, HR/9 0.84 vs LHB, 2.22 vs RHB). Imai (BAA vs LHB .218, vs RHB .191, HR/9 1.38 vs LHB, 0.58 vs RHB).",
        "rows": [
            row("Yordan Alvarez", "L", "+340", 70, "⭐", ["vs Fedde"], """Worst Pickz Favorite. 0 HR, 90.1 mph EV, 12.5% barrels. limited split/risk sample; limited recent HR events.""", contact={'stars': 3, 'k': 20.5, 'batterK': 17.2, 'batterWhiff': 23.3, 'pitcherK': None}),
            row("Yainer Diaz", "R", "+610", 78, "💎", ["vs Fedde"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.9 mph EV, 37.5% barrels. limited split/risk sample.""", blast="good", contact={'stars': 3, 'k': 20.1, 'batterK': 15.8, 'batterWhiff': 22.1, 'pitcherK': None}),
            row("Christian Walker", "R", "+524", 69, "", ["vs Fedde"], """1 HR, 1 near-HR, 84.5 mph EV, 12.5% barrels. limited split/risk sample; lighter EV form (84.5 mph).""", blast="good", contact={'stars': 3, 'k': 22.1, 'batterK': 20.3, 'batterWhiff': 26.8, 'pitcherK': None}),
            row("Munetaka Murakami", "L", "+355", 87, "🌕 💣 💎", ["vs Imai"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.7 mph EV, 50.0% barrels. limited split/risk sample.""", blast="high", contact={'stars': 1, 'k': 30.4, 'batterK': 41.2, 'batterWhiff': 41.3, 'pitcherK': None}),
            row("Kyle Teel", "L", "+800", 77, "", ["vs Imai"], """1 HR, 1 near-HR, 93.6 mph EV, 12.5% barrels. limited split/risk sample.""", blast="good", contact={'stars': 2, 'k': 26.4, 'batterK': 32.4, 'batterWhiff': 34.8, 'pitcherK': None}),
            row("Braden Montgomery", "S", "+980", 65, "", ["vs Imai"], """0 HR, 96.4 mph EV. limited split/risk sample; limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 23.4, 'batterK': 19.4, 'batterWhiff': 33.3, 'pitcherK': None}),
        ],
    },
    {
        "title": "PHI @ ATL - Jesus Luzardo (L, PHI) vs Chris Sale (L, ATL)",
        "kLines": {'Luzardo': {'k': 6.9, 'lo': 5, 'hi': 9, 'bf': 24.5, 'matchupK': 28.3, 'ownK': 31.6}, 'Sale': {'k': 7.3, 'lo': 6, 'hi': 9, 'bf': 23.6, 'matchupK': 31.0, 'ownK': 33.9}},
        "description": "Tail key data: Park boost -7% (stadium -4%, weather -3%). Luzardo (HR risk 0.27, vs LHB -0.76, vs RHB +0.20). Sale (HR risk -0.10, vs LHB -0.71, vs RHB +0.08).",
        "rows": [
            row("Brewer Hicklen", "R", "N/A", 58, "🚀", ["vs Luzardo"], """0 HR, 100.5 mph EV. Luzardo RHB split +0.20, HR risk 0.27. park/weather net drag (-7%); limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 33.3, 'batterK': 34.0, 'batterWhiff': 43.5, 'pitcherK': 31.6}),
            row("Ronald Acuna Jr.", "R", "+470", 60, "", ["vs Luzardo"], """1 HR, 1 near-HR, 83.6 mph EV, 12.5% barrels. Luzardo RHB split +0.20, HR risk 0.27. park/weather net drag (-7%); lighter EV form (83.6 mph).""", blast="good", contact={'stars': 2, 'k': 24.8, 'batterK': 15.1, 'batterWhiff': 22.9, 'pitcherK': 31.6}),
            row("Austin Riley", "R", "+575", 74, "", ["vs Luzardo"], """1 HR, 1 near-HR, 90.2 mph EV, 12.5% barrels. Luzardo RHB split +0.20, HR risk 0.27. park/weather net drag (-7%).""", blast="good", contact={'stars': 1, 'k': 32.3, 'batterK': 35.5, 'batterWhiff': 30.5, 'pitcherK': 31.6}),
            row("Matt Olson", "L", "+408", 72, "", ["vs Luzardo"], """1 HR, 1 near-HR, 92.8 mph EV, 12.5% barrels. Luzardo LHB split -0.76, HR risk 0.27. tough split lane (-0.76); park/weather net drag (-7%).""", blast="good", contact={'stars': 2, 'k': 25.0, 'batterK': 14.8, 'batterWhiff': 23.4, 'pitcherK': 31.6}),
            row("Alec Bohm", "R", "+870", 74, "⭐ 🌕 💣", ["vs Sale"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 98.9 mph EV, 25.0% barrels. Sale RHB split +0.08, HR risk -0.10. pitcher risk below avg (-0.10); park/weather net drag (-7%).""", blast="high", contact={'stars': 2, 'k': 24.0, 'batterK': 11.5, 'batterWhiff': 17.5, 'pitcherK': 33.9}),
            row("Edmundo Sosa", "R", "+1220", 63, "", ["vs Sale"], """1 HR, 2 near-HR, 90.1 mph EV. Sale RHB split +0.08, HR risk -0.10. pitcher risk below avg (-0.10); park/weather net drag (-7%).""", blast="good", contact={'stars': 1, 'k': 31.0, 'batterK': 26.5, 'batterWhiff': 31.2, 'pitcherK': 33.9}),
            row("Kyle Schwarber", "L", "+390", 71, "", ["vs Sale"], """1 HR, 1 near-HR, 95.2 mph EV. Sale LHB split -0.71, HR risk -0.10. tough split lane (-0.71); pitcher risk below avg (-0.10).""", blast="good", contact={'stars': 1, 'k': 29.6, 'batterK': 23.1, 'batterWhiff': 26.6, 'pitcherK': 33.9}),
            row("Trea Turner", "R", "+860", 59, "💎", ["vs Sale"], """Worst Pickz Hidden Gem. 0 HR, 94.6 mph EV. Sale RHB split +0.08, HR risk -0.10. pitcher risk below avg (-0.10); park/weather net drag (-7%).""", blast="good", contact={'stars': 1, 'k': 28.5, 'batterK': 18.0, 'batterWhiff': 30.0, 'pitcherK': 33.9}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-29")

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

    out = ROOT / '_games-0929.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
