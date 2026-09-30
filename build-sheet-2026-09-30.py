#!/usr/bin/env python3
"""Generate games[] block for 2026-09-30 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Fernando Tatis Jr. (R)",
    "Giancarlo Stanton (R)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Alec Bohm (R)",
    "Alex Bregman (R)",
    "Ben Rice (L)",
    "Kyle Schwarber (L)",
    "Miguel Andujar (R)",
    "Spencer Jones (L)",
    "Xander Bogaerts (R)",
}

PLAYER_TEAMS = {
    "Alec Bohm (R)": "PHI",
    "Alex Bregman (R)": "CHC",
    "Austin Wells (L)": "NYY",
    "Ben Rice (L)": "NYY",
    "Brewer Hicklen (R)": "ATL",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Ceddanne Rafaela (R)": "BOS",
    "Christian Walker (R)": "HOU",
    "Colson Montgomery (L)": "CWS",
    "Fernando Tatis Jr. (R)": "SD",
    "Giancarlo Stanton (R)": "NYY",
    "Ha-Seong Kim (R)": "ATL",
    "Kyle Schwarber (L)": "PHI",
    "Lucas Spence (L)": "HOU",
    "Matt Olson (L)": "ATL",
    "Michael Busch (L)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Miguel Andujar (R)": "SD",
    "Munetaka Murakami (L)": "CWS",
    "Nelson Velazquez (R)": "HOU",
    "Otto Kemp (R)": "PHI",
    "Ronald Acuna Jr. (R)": "ATL",
    "Ryan McMahon (L)": "NYY",
    "Sam Antonacci (L)": "CWS",
    "Spencer Jones (L)": "NYY",
    "Taylor Trammell (L)": "HOU",
    "Trent Grisham (L)": "NYY",
    "Willson Contreras (R)": "BOS",
    "Xander Bogaerts (R)": "SD",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("CHC @ SD", "Gausman"),
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
        "title": "BOS @ NYY - Sonny Gray (R, BOS) vs Max Fried (L, NYY)",
        "kLines": {'Gray': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 23.2, 'matchupK': 22.7, 'ownK': 22.2}, 'Fried': {'k': 5.8, 'lo': 4, 'hi': 7, 'bf': 21.7, 'matchupK': 26.9, 'ownK': 27.8}},
        "description": "Tail key data: Park boost +10% (stadium +4%, weather +5%). Gray (HR risk -0.38, vs LHB -0.14, vs RHB -0.15). Fried (HR risk -0.99, vs LHB -0.74, vs RHB -0.78).",
        "rows": [
            row("Giancarlo Stanton", "R", "N/A", 82, "⭐", ["vs Gray"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.7 mph EV, 12.5% barrels. Gray RHB split -0.15, HR risk -0.38. slight split headwind (-0.15); pitcher risk below avg (-0.38).""", blast="good", contact={'stars': 2, 'k': 27.3, 'batterK': 31.3, 'batterWhiff': 40.0, 'pitcherK': 22.2}),
            row("Ben Rice", "L", "+328", 91, "🌕 💣 💎", ["vs Gray"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 92.2 mph EV, 37.5% barrels. Gray LHB split -0.14, HR risk -0.38. slight split headwind (-0.14); pitcher risk below avg (-0.38).""", blast="high", contact={'stars': 3, 'k': 21.0, 'batterK': 20.0, 'batterWhiff': 22.1, 'pitcherK': 22.2}),
            row("Spencer Jones", "L", "+500", 74, "💎", ["vs Gray"], """Worst Pickz Hidden Gem. 0 HR, 94.6 mph EV, 12.5% barrels. Gray LHB split -0.14, HR risk -0.38. slight split headwind (-0.14); pitcher risk below avg (-0.38).""", blast="good", contact={'stars': 1, 'k': 29.7, 'batterK': 39.8, 'batterWhiff': 40.4, 'pitcherK': 22.2}),
            row("Trent Grisham", "L", "+473", 55, "", ["vs Gray"], """0 HR, 90.3 mph EV. Gray LHB split -0.14, HR risk -0.38. slight split headwind (-0.14); pitcher risk below avg (-0.38).""", contact={'stars': 3, 'k': 22.2, 'batterK': 25.9, 'batterWhiff': 19.8, 'pitcherK': 22.2}),
            row("Ryan McMahon", "L", "+920", 63, "", ["vs Gray"], """1 HR, 1 near-HR, 89.4 mph EV, 12.5% barrels. Gray LHB split -0.14, HR risk -0.38. slight split headwind (-0.14); pitcher risk below avg (-0.38).""", blast="good", contact={'stars': 3, 'k': 22.4, 'batterK': 25.4, 'batterWhiff': 23.6, 'pitcherK': 22.2}),
            row("Austin Wells", "L", "+760", 91, "🌕 💣", ["vs Gray"], """3 HR, 3 near-HR, 92.6 mph EV, 37.5% barrels. Gray LHB split -0.14, HR risk -0.38. slight split headwind (-0.14); pitcher risk below avg (-0.38).""", blast="high", contact={'stars': 3, 'k': 22.2, 'batterK': 22.7, 'batterWhiff': 24.8, 'pitcherK': 22.2}),
            row("Ceddanne Rafaela", "R", "+1040", 40, "", ["vs Fried"], """0 HR, 86.1 mph EV, 11.1% barrels. Fried RHB split -0.78, HR risk -0.99. tough split lane (-0.78); pitcher suppresses HR (-0.99).""", contact={'stars': 2, 'k': 24.5, 'batterK': 20.7, 'batterWhiff': 24.3, 'pitcherK': 27.8}),
            row("Willson Contreras", "R", "+552", 53, "", ["vs Fried"], """0 HR, 89.8 mph EV. Fried RHB split -0.78, HR risk -0.99. tough split lane (-0.78); pitcher suppresses HR (-0.99).""", contact={'stars': 2, 'k': 26.5, 'batterK': 25.0, 'batterWhiff': 28.0, 'pitcherK': 27.8}),
        ],
    },
    {
        "title": "CHC @ SD - Kevin Gausman 🧤 (R, CHC) vs Nick Pivetta (R, SD)",
        "kLines": {'Gausman': {'k': 5.6, 'lo': 4, 'hi': 7, 'bf': 23.2, 'matchupK': 24.3, 'ownK': 26.0}, 'Pivetta': {'k': 4.8, 'lo': 3, 'hi': 6, 'bf': 19.3, 'matchupK': 25.0, 'ownK': 30.0}},
        "description": "Tail key data: Park boost -3% (stadium -5%, weather +2%). Gausman 🧤 (HR risk 1.47, vs LHB +0.60, vs RHB +1.71). Pivetta (HR risk 0.28, vs LHB +0.06, vs RHB +0.45).",
        "rows": [
            row("Fernando Tatis Jr.", "R", "+353", 98, "⭐ 🌕 💣", ["vs Gausman"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.3 mph EV, 37.5% barrels. Gausman RHB split +1.71, HR risk 1.47.""", blast="high", contact={'stars': 3, 'k': 21.8, 'batterK': 17.6, 'batterWhiff': 19.7, 'pitcherK': 26.0}),
            row("Xander Bogaerts", "R", "+800", 91, "🌕 💣 💎", ["vs Gausman"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.9 mph EV, 12.5% barrels. Gausman RHB split +1.71, HR risk 1.47.""", blast="good", contact={'stars': 3, 'k': 23.6, 'batterK': 20.3, 'batterWhiff': 24.2, 'pitcherK': 26.0}),
            row("Miguel Andujar", "R", "N/A", 78, "💎", ["vs Gausman"], """Worst Pickz Hidden Gem. 0 HR, 2 near-HR, 91.1 mph EV, 12.5% barrels. Gausman RHB split +1.71, HR risk 1.47.""", blast="good", contact={'stars': 3, 'k': 20.0, 'batterK': 8.9, 'batterWhiff': 15.3, 'pitcherK': 26.0}),
            row("Alex Bregman", "R", "+570", 75, "💎", ["vs Pivetta"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.6 mph EV, 25.0% barrels. Pivetta RHB split +0.45, HR risk 0.28.""", blast="good", contact={'stars': 4, 'k': 18.0, 'batterK': 7.3, 'batterWhiff': 10.2, 'pitcherK': 30.0}),
            row("Michael Conforto", "L", "N/A", 68, "", ["vs Pivetta"], """0 HR, 91.7 mph EV, 12.5% barrels. Pivetta LHB split +0.06, HR risk 0.28. limited recent HR events.""", contact={'stars': 3, 'k': 22.6, 'batterK': 14.7, 'batterWhiff': 19.4, 'pitcherK': 30.0}),
            row("Michael Busch", "L", "+680", 56, "", ["vs Pivetta"], """0 HR, 82.3 mph EV, 12.5% barrels. Pivetta LHB split +0.06, HR risk 0.28. limited recent HR events; lighter EV form (82.3 mph).""", contact={'stars': 2, 'k': 25.5, 'batterK': 23.5, 'batterWhiff': 23.4, 'pitcherK': 30.0}),
        ],
    },
    {
        "title": "CWS @ HOU - Sean Burke (R, CWS) vs Hunter Brown (R, HOU)",
        "kLines": {'Burke': {'k': 4.9, 'lo': 3, 'hi': 7, 'bf': 22.2, 'matchupK': 22.2, 'ownK': 21.3}, 'Brown': {'k': 6.7, 'lo': 5, 'hi': 8, 'bf': 22.4, 'matchupK': 30.0, 'ownK': 30.3}},
        "description": "Tail key data: Park boost +7% (stadium +8%, weather +0%). Burke (HR risk 0.23, vs LHB +0.70, vs RHB -0.04). Brown (HR risk -0.71, vs LHB -0.12, vs RHB -0.62).",
        "rows": [
            row("Yordan Alvarez", "L", "+320", 88, "🚀 ⭐ 🌕 💣", ["vs Burke"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 100.5 mph EV, 12.5% barrels. Burke LHB split +0.70, HR risk 0.23.""", blast="good", contact={'stars': 3, 'k': 20.0, 'batterK': 17.2, 'batterWhiff': 23.3, 'pitcherK': 21.3}),
            row("Taylor Trammell", "L", "+860", 86, "", ["vs Burke"], """1 HR, 2 near-HR, 94.8 mph EV, 25.0% barrels. Burke LHB split +0.70, HR risk 0.23.""", blast="good", contact={'stars': 2, 'k': 27.2, 'batterK': 37.1, 'batterWhiff': 39.4, 'pitcherK': 21.3}),
            row("Lucas Spence", "L", "+880", 90, "🌕 💣", ["vs Burke"], """4 HR, 4 near-HR, 86.9 mph EV, 25.0% barrels. Burke LHB split +0.70, HR risk 0.23. lighter EV form (86.9 mph).""", blast="high", contact={'stars': 2, 'k': 26.6, 'batterK': 34.9, 'batterWhiff': 38.3, 'pitcherK': 21.3}),
            row("Christian Walker", "R", "+425", 89, "🌕 💣", ["vs Burke"], """2 HR, 3 near-HR, 93.2 mph EV, 25.0% barrels. Burke RHB split -0.04, HR risk 0.23. slight split headwind (-0.04).""", blast="high", contact={'stars': 3, 'k': 21.6, 'batterK': 20.3, 'batterWhiff': 26.8, 'pitcherK': 21.3}),
            row("Nelson Velazquez", "R", "N/A", 85, "🌕 💣", ["vs Burke"], """1 HR, 2 near-HR, 99.2 mph EV, 37.5% barrels. Burke RHB split -0.04, HR risk 0.23. slight split headwind (-0.04).""", blast="high", contact={'stars': 2, 'k': 26.5, 'batterK': 44.1, 'batterWhiff': 43.8, 'pitcherK': 21.3}),
            row("Munetaka Murakami", "L", "+447", 87, "🌕 💣", ["vs Brown"], """1 HR, 1 near-HR, 97.5 mph EV, 37.5% barrels. Brown LHB split -0.12, HR risk -0.71. slight split headwind (-0.12); pitcher suppresses HR (-0.71).""", blast="high", contact={'stars': 1, 'k': 35.6, 'batterK': 41.2, 'batterWhiff': 41.3, 'pitcherK': 30.3}),
            row("Colson Montgomery", "L", "+525", 61, "", ["vs Brown"], """1 HR, 1 near-HR, 88.7 mph EV, 12.5% barrels. Brown LHB split -0.12, HR risk -0.71. slight split headwind (-0.12); pitcher suppresses HR (-0.71).""", blast="good", contact={'stars': 1, 'k': 36.3, 'batterK': 47.4, 'batterWhiff': 40.3, 'pitcherK': 30.3}),
            row("Sam Antonacci", "L", "+1260", 46, "", ["vs Brown"], """0 HR, 90.9 mph EV. Brown LHB split -0.12, HR risk -0.71. slight split headwind (-0.12); pitcher suppresses HR (-0.71).""", contact={'stars': 4, 'k': 19.4, 'batterK': 7.9, 'batterWhiff': 10.4, 'pitcherK': 30.3}),
        ],
    },
    {
        "title": "PHI @ ATL - Cristopher Sanchez (L, PHI) vs Tyler Mahle (R, ATL)",
        "kLines": {'Sanchez': {'k': 5.9, 'lo': 4, 'hi': 8, 'bf': 25.3, 'matchupK': 23.4, 'ownK': 24.8}, 'Mahle': {'k': 5.3, 'lo': 4, 'hi': 7, 'bf': 22.6, 'matchupK': 23.3, 'ownK': 24.3}},
        "description": "Tail key data: Park boost -10% (stadium -3%, weather -7%). Sanchez (HR risk 0.24, vs LHB -1.13, vs RHB +0.35). Mahle (HR risk -0.12, vs LHB +0.78, vs RHB -0.92).",
        "rows": [
            row("Ronald Acuna Jr.", "R", "+610", 64, "", ["vs Sanchez"], """0 HR, 98.2 mph EV. Sanchez RHB split +0.35, HR risk 0.24. park/weather net drag (-10%); limited recent HR events.""", blast="good", contact={'stars': 3, 'k': 21.2, 'batterK': 15.1, 'batterWhiff': 22.9, 'pitcherK': 24.8}),
            row("Brewer Hicklen", "R", "N/A", 57, "🚀", ["vs Sanchez"], """0 HR, 101.6 mph EV. Sanchez RHB split +0.35, HR risk 0.24. park/weather net drag (-10%); limited recent HR events.""", blast="good", contact={'stars': 1, 'k': 28.9, 'batterK': 34.0, 'batterWhiff': 43.5, 'pitcherK': 24.8}),
            row("Matt Olson", "L", "+534", 77, "", ["vs Sanchez"], """1 HR, 1 near-HR, 96.9 mph EV, 12.5% barrels. Sanchez LHB split -1.13, HR risk 0.24. tough split lane (-1.13); park/weather net drag (-10%).""", blast="good", contact={'stars': 3, 'k': 21.4, 'batterK': 14.8, 'batterWhiff': 23.4, 'pitcherK': 24.8}),
            row("Ha-Seong Kim", "R", "+1400", 43, "", ["vs Sanchez"], """0 HR, 88.8 mph EV. Sanchez RHB split +0.35, HR risk 0.24. park/weather net drag (-10%); limited recent HR events.""", contact={'stars': 3, 'k': 22.8, 'batterK': 24.2, 'batterWhiff': 19.3, 'pitcherK': 24.8}),
            row("Otto Kemp", "R", "N/A", 52, "🚀", ["vs Mahle"], """0 HR, 101.5 mph EV. Mahle RHB split -0.92, HR risk -0.12. tough split lane (-0.92); pitcher risk below avg (-0.12).""", blast="good", contact={'stars': 2, 'k': 26.2, 'batterK': 37.0, 'batterWhiff': 37.9, 'pitcherK': 24.3}),
            row("Bryson Stott", "L", "+900", 57, "", ["vs Mahle"], """0 HR, 98.8 mph EV. Mahle LHB split +0.78, HR risk -0.12. pitcher risk below avg (-0.12); park/weather net drag (-10%).""", blast="good", contact={'stars': 4, 'k': 18.8, 'batterK': 11.5, 'batterWhiff': 15.7, 'pitcherK': 24.3}),
            row("Kyle Schwarber", "L", "+285", 67, "💎", ["vs Mahle"], """Worst Pickz Hidden Gem. 0 HR, 94.2 mph EV. Mahle LHB split +0.78, HR risk -0.12. pitcher risk below avg (-0.12); park/weather net drag (-10%).""", blast="good", contact={'stars': 3, 'k': 23.9, 'batterK': 23.1, 'batterWhiff': 26.6, 'pitcherK': 24.3}),
            row("Bryce Harper", "L", "+416", 69, "", ["vs Mahle"], """1 HR, 1 near-HR, 86.8 mph EV, 12.5% barrels. Mahle LHB split +0.78, HR risk -0.12. pitcher risk below avg (-0.12); park/weather net drag (-10%).""", blast="good", contact={'stars': 2, 'k': 27.2, 'batterK': 26.7, 'batterWhiff': 38.3, 'pitcherK': 24.3}),
            row("Alec Bohm", "R", "+1040", 44, "💎", ["vs Mahle"], """Worst Pickz Hidden Gem. 0 HR, 90.9 mph EV. Mahle RHB split -0.92, HR risk -0.12. tough split lane (-0.92); pitcher risk below avg (-0.12).""", contact={'stars': 4, 'k': 19.2, 'batterK': 11.5, 'batterWhiff': 17.5, 'pitcherK': 24.3}),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-09-30")

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

    out = ROOT / '_games-0930.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
