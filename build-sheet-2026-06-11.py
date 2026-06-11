#!/usr/bin/env python3
"""Generate games[] block for 2026-06-11 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Adley Rutschman (S)",
    "Bobby Witt Jr. (R)",
    "Byron Buxton (R)",
    "Dillon Dingler (R)",
    "Ezequiel Tovar (R)",
    "Hunter Goodman (R)",
    "Juan Soto (L)",
    "Kody Clemens (L)",
    "Kyle Stowers (L)",
    "Luke Raley (L)",
    "Riley Greene (L)",
    "Victor Caratini (S)",
}

GEMS = {
    "Jackson Holliday (L)",
    "Jorge Barrosa (S)",
    "Jorge Mateo (R)",
    "Marcus Semien (R)",
    "Starling Marte (R)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BAL",
    "Alec Burleson (L)": "STL",
    "Andrew Benintendi (L)": "CWS",
    "Austin Riley (R)": "ATL",
    "Blaze Alexander (R)": "BAL",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Nimmo (L)": "TEX",
    "Brooks Lee (S)": "MIN",
    "Bryan Torres (L)": "STL",
    "Byron Buxton (R)": "MIN",
    "Colson Montgomery (L)": "CWS",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Dillon Dingler (R)": "DET",
    "Dominic Canzone (L)": "SEA",
    "Edouard Julien (L)": "COL",
    "Ezequiel Tovar (R)": "COL",
    "Francisco Alvarez (R)": "NYM",
    "Freddie Freeman (L)": "LAD",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "JJ Wetherholt (L)": "STL",
    "Jackson Holliday (L)": "BAL",
    "Jared Young (L)": "NYM",
    "Joc Pederson (L)": "TEX",
    "Jordan Walker (R)": "STL",
    "Jorge Barrosa (S)": "ARI",
    "Jorge Mateo (R)": "ATL",
    "Juan Soto (L)": "NYM",
    "Julio Rodriguez (R)": "SEA",
    "Kevin McGonigle (L)": "DET",
    "Kody Clemens (L)": "MIN",
    "Kyle Stowers (L)": "MIA",
    "Luke Raley (L)": "SEA",
    "Marcell Ozuna (R)": "PIT",
    "Marcus Semien (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Michael Massey (L)": "KC",
    "Otto Lopez (R)": "MIA",
    "Patrick Wisdom (R)": "SEA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Randal Grichuk (R)": "CWS",
    "Riley Greene (L)": "DET",
    "Samuel Basallo (L)": "BAL",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Horwitz (L)": "PIT",
    "Spencer Torkelson (R)": "DET",
    "Starling Marte (R)": "KC",
    "Victor Caratini (S)": "MIN",
    "Vinnie Pasquantino (L)": "KC",
    "Will Smith (R)": "LAD",
}

BUM_PITCHERS = {
    "Cabrera",
    "Kelly",
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

def add_bum_row_emojis(entry):
    chip = entry["chips"][0].replace("vs ", "").strip()
    if chip not in BUM_PITCHERS:
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
        "title": "ARI @ MIA - Merrill Kelly 🧤 (R, ARI) vs Tyler Phillips (R, MIA)",
        "description": "Tail key data: Park boost -14% (stadium -14%, weather +0%). Kelly 🧤 (HR risk 1.07, vs LHB +1.40, vs RHB +0.03). Phillips (HR risk -1.03, vs LHB -0.80, vs RHB -0.70).",
        "rows": [
            row("Kyle Stowers", "L", "+400", 84, "⭐ 🌕 💣", ["vs Kelly"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 91.7 mph EV. Kelly LHB split +1.40, HR risk 1.07. park/weather net drag (-14%).""", blast="high"),
            row("Otto Lopez", "R", "+725", 73, "💎", ["vs Kelly"], """1 HR, 1 near-HR, 91.0 mph EV. Kelly RHB split +0.03, HR risk 1.07. park/weather net drag (-14%).""", blast="good"),
            row("Corbin Carroll", "L", "+475", 66, "💎", ["vs Phillips"], """0 HR, 91.8 mph EV. Phillips LHB split -0.80, HR risk -1.03. tough split lane (-0.80); pitcher suppresses HR (-1.03)."""),
            row("Jorge Barrosa", "S", "N/A", 71, "💎", ["vs Phillips"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.6 mph EV. Phillips RHB split -0.70, HR risk -1.03. tough split lane (-0.70); pitcher suppresses HR (-1.03).""", blast="good"),
        ],
    },
    {
        "title": "ATL @ CWS - Martin Perez (L, ATL) vs Anthony Kay (L, CWS)",
        "description": "Tail key data: Park boost data unavailable. Perez (HR risk -0.11, vs LHB -0.00, vs RHB -0.07). Home starter risk unavailable.",
        "rows": [
            row("Randal Grichuk", "R", "+442", 83, "🌕 💣", ["vs Perez"], """2 HR, 2 near-HR, 92.8 mph EV. Perez RHB split -0.07, HR risk -0.11. slight split headwind (-0.07); pitcher risk below avg (-0.11).""", blast="high"),
            row("Colson Montgomery", "L", "N/A", 70, "💎", ["vs Perez"], """0 HR, 1 near-HR, 92.1 mph EV. Perez LHB split -0.00, HR risk -0.11. pitcher risk below avg (-0.11); limited recent HR events.""", blast="good"),
            row("Andrew Benintendi", "L", "+576", 62, "💎", ["vs Perez"], """0 HR, 87.2 mph EV. Perez LHB split -0.00, HR risk -0.11. pitcher risk below avg (-0.11); limited recent HR events."""),
            row("Matt Olson", "L", "+335", 80, "💎", ["vs Kay"], """1 HR, 2 near-HR, 95.7 mph EV. Kay split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Michael Harris II", "L", "+405", 62, "💎", ["vs Kay"], """0 HR, 88.3 mph EV. Kay split/risk data unavailable. limited split/risk sample; limited recent HR events."""),
            row("Austin Riley", "R", "+452", 76, "💎", ["vs Kay"], """0 HR, 1 near-HR, 97.7 mph EV. Kay split/risk data unavailable. limited split/risk sample; limited recent HR events.""", blast="good"),
            row("Jorge Mateo", "R", "+800", 83, "🌕 💣 💎", ["vs Kay"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 92.9 mph EV. Kay split/risk data unavailable. limited split/risk sample.""", blast="high"),
        ],
    },
    {
        "title": "CHC @ COL - Edward Cabrera 🧤 (R, CHC) vs Ryan Feltner (R, COL)",
        "description": "Tail key data: Park boost +27% (stadium +22%, weather +5%). Cabrera 🧤 (HR risk 1.57, vs LHB +0.17, vs RHB +2.08). Feltner (HR risk 0.68, vs LHB +0.35, vs RHB +0.61).",
        "rows": [
            row("Hunter Goodman", "R", "+309", 98, "⭐ 🌕 💣", ["vs Cabrera"], """Worst Pickz Favorite. 5 HR, 5 near-HR, 93.2 mph EV. Cabrera RHB split +2.08, HR risk 1.57.""", blast="high"),
            row("Ezequiel Tovar", "R", "+610", 83, "⭐ 🌕 💣", ["vs Cabrera"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 91.4 mph EV. Cabrera RHB split +2.08, HR risk 1.57.""", blast="high"),
            row("Edouard Julien", "L", "+775", 72, "💎", ["vs Cabrera"], """0 HR, 1 near-HR, 93.9 mph EV. Cabrera LHB split +0.17, HR risk 1.57. limited recent HR events.""", blast="good"),
            row("Pete Crow-Armstrong", "L", "+310", 81, "🌕 💣", ["vs Feltner"], """2 HR, 3 near-HR, 89.4 mph EV. Feltner LHB split +0.35, HR risk 0.68.""", blast="high"),
            row("Ian Happ", "S", "+410", 83, "🌕 💣", ["vs Feltner"], """2 HR, 2 near-HR, 93.4 mph EV. Feltner RHB split +0.61, HR risk 0.68.""", blast="high"),
            row("Michael Conforto", "L", "N/A", 68, "💎", ["vs Feltner"], """0 HR, 1 near-HR, 91.6 mph EV. Feltner LHB split +0.35, HR risk 0.68. limited recent HR events."""),
        ],
    },
    {
        "title": "LAD @ PIT - Justin Wrobleski (L, LAD) vs Mitch Keller (R, PIT)",
        "description": "Tail key data: Park boost +6% (stadium -15%, weather +21%). Wrobleski (HR risk -0.13, vs LHB +0.75, vs RHB -0.32). Keller (HR risk -0.26, vs LHB -0.10, vs RHB -0.34).",
        "rows": [
            row("Spencer Horwitz", "L", "N/A", 75, "💎", ["vs Wrobleski"], """1 HR, 1 near-HR, 92.7 mph EV. Wrobleski LHB split +0.75, HR risk -0.13. pitcher risk below avg (-0.13); park suppresses carry (-15%).""", blast="good"),
            row("Marcell Ozuna", "R", "+590", 78, "💎", ["vs Wrobleski"], """1 HR, 1 near-HR, 96.0 mph EV. Wrobleski RHB split -0.32, HR risk -0.13. slight split headwind (-0.32); pitcher risk below avg (-0.13).""", blast="good"),
            row("Freddie Freeman", "L", "+475", 78, "🌕 💣", ["vs Keller"], """2 HR, 2 near-HR, 87.1 mph EV. Keller LHB split -0.10, HR risk -0.26. slight split headwind (-0.10); pitcher risk below avg (-0.26).""", blast="high"),
            row("Will Smith", "R", "N/A", 89, "🌕 💣", ["vs Keller"], """2 HR, 3 near-HR, 96.9 mph EV. Keller RHB split -0.34, HR risk -0.26. slight split headwind (-0.34); pitcher risk below avg (-0.26).""", blast="high"),
            row("Shohei Ohtani", "L", "+270", 67, "💎", ["vs Keller"], """0 HR, 1 near-HR, 90.8 mph EV. Keller LHB split -0.10, HR risk -0.26. slight split headwind (-0.10); pitcher risk below avg (-0.26)."""),
        ],
    },
    {
        "title": "MIN @ DET - Zebby Matthews (R, MIN) vs Keider Montero (R, DET)",
        "description": "Tail key data: Park boost +10% (stadium -11%, weather +20%). Matthews (HR risk 0.70, vs LHB +0.78, vs RHB +0.20). Montero (HR risk 0.38, vs LHB +0.76, vs RHB -0.24).",
        "rows": [
            row("Dillon Dingler", "R", "+450", 83, "⭐ 💎", ["vs Matthews"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 97.1 mph EV. Matthews RHB split +0.20, HR risk 0.70. park suppresses carry (-11%).""", blast="good"),
            row("Kevin McGonigle", "L", "+600", 72, "💎", ["vs Matthews"], """1 HR, 1 near-HR, 90.4 mph EV. Matthews LHB split +0.78, HR risk 0.70. park suppresses carry (-11%).""", blast="good"),
            row("Riley Greene", "L", "+383", 93, "⭐ 🌕 💣", ["vs Matthews"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 98.9 mph EV. Matthews LHB split +0.78, HR risk 0.70. park suppresses carry (-11%).""", blast="high"),
            row("Spencer Torkelson", "R", "+490", 74, "💎", ["vs Matthews"], """1 HR, 1 near-HR, 91.6 mph EV. Matthews RHB split +0.20, HR risk 0.70. park suppresses carry (-11%).""", blast="good"),
            row("Byron Buxton", "R", "+265", 83, "⭐ 🌕 💣", ["vs Montero"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 92.8 mph EV. Montero RHB split -0.24, HR risk 0.38. slight split headwind (-0.24); park suppresses carry (-11%).""", blast="high"),
            row("Brooks Lee", "S", "+680", 86, "🌕 💣", ["vs Montero"], """3 HR, 3 near-HR, 90.1 mph EV. Montero RHB split -0.24, HR risk 0.38. slight split headwind (-0.24); park suppresses carry (-11%).""", blast="high"),
            row("Kody Clemens", "L", "+334", 82, "⭐ 💎", ["vs Montero"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 96.0 mph EV. Montero LHB split +0.76, HR risk 0.38. park suppresses carry (-11%).""", blast="good"),
            row("Victor Caratini", "S", "+620", 76, "⭐ 💎", ["vs Montero"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 92.3 mph EV. Montero RHB split -0.24, HR risk 0.38. slight split headwind (-0.24); park suppresses carry (-11%).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ BAL - Bryan Woo (R, SEA) vs Kyle Bradish (R, BAL)",
        "description": "Tail key data: Park boost +6% (stadium -1%, weather +7%). Woo (HR risk -0.59, vs LHB -0.31, vs RHB -0.67). Bradish (HR risk -0.25, vs LHB -0.67, vs RHB +0.41).",
        "rows": [
            row("Pete Alonso", "R", "+383", 84, "🌕 💣", ["vs Woo"], """2 HR, 2 near-HR, 94.3 mph EV. Woo RHB split -0.67, HR risk -0.59. tough split lane (-0.67); pitcher suppresses HR (-0.59).""", blast="high"),
            row("Adley Rutschman", "S", "N/A", 78, "⭐ 💎", ["vs Woo"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 95.5 mph EV. Woo RHB split -0.67, HR risk -0.59. tough split lane (-0.67); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Blaze Alexander", "R", "+467", 73, "💎", ["vs Woo"], """1 HR, 1 near-HR, 91.1 mph EV. Woo RHB split -0.67, HR risk -0.59. tough split lane (-0.67); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Jackson Holliday", "L", "+549", 77, "💎", ["vs Woo"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 92.9 mph EV. Woo LHB split -0.31, HR risk -0.59. slight split headwind (-0.31); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Samuel Basallo", "L", "+375", 75, "💎", ["vs Woo"], """0 HR, 99.3 mph EV. Woo LHB split -0.31, HR risk -0.59. slight split headwind (-0.31); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Colton Cowser", "L", "+484", 72, "💎", ["vs Woo"], """1 HR, 2 near-HR, 86.8 mph EV. Woo LHB split -0.31, HR risk -0.59. slight split headwind (-0.31); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Dominic Canzone", "L", "+440", 78, "💎", ["vs Bradish"], """1 HR, 1 near-HR, 95.8 mph EV. Bradish LHB split -0.67, HR risk -0.25. tough split lane (-0.67); pitcher risk below avg (-0.25).""", blast="good"),
            row("Julio Rodriguez", "R", "+447", 62, "💎", ["vs Bradish"], """0 HR, 86.4 mph EV. Bradish RHB split +0.41, HR risk -0.25. pitcher risk below avg (-0.25); limited recent HR events."""),
            row("Luke Raley", "L", "+422", 76, "⭐ 💎", ["vs Bradish"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 91.5 mph EV. Bradish LHB split -0.67, HR risk -0.25. tough split lane (-0.67); pitcher risk below avg (-0.25).""", blast="good"),
            row("Patrick Wisdom", "R", "+416", 75, "💎", ["vs Bradish"], """0 HR, 1 near-HR, 97.4 mph EV. Bradish RHB split +0.41, HR risk -0.25. pitcher risk below avg (-0.25); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "STL @ NYM - Hunter Dobbins (R, STL) vs Christian Scott (R, NYM)",
        "description": "Tail key data: Park boost +5% (stadium -1%, weather +6%). Dobbins (HR risk 0.13, vs LHB -0.31, vs RHB +0.38). Scott (HR risk -1.57, vs LHB -1.84, vs RHB -0.44).",
        "rows": [
            row("Marcus Semien", "R", "+538", 92, "🌕 💣 💎", ["vs Dobbins"], """Worst Pickz Hidden Gem. 4 HR, 5 near-HR, 88.3 mph EV. Dobbins RHB split +0.38, HR risk 0.13.""", blast="high"),
            row("Juan Soto", "L", "+350", 80, "⭐ 💎", ["vs Dobbins"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.8 mph EV. Dobbins LHB split -0.31, HR risk 0.13. slight split headwind (-0.31).""", blast="good"),
            row("Francisco Alvarez", "R", "+490", 81, "💎", ["vs Dobbins"], """1 HR, 3 near-HR, 95.1 mph EV. Dobbins RHB split +0.38, HR risk 0.13.""", blast="good"),
            row("Jared Young", "L", "+522", 87, "🌕 💣", ["vs Dobbins"], """2 HR, 3 near-HR, 94.6 mph EV. Dobbins LHB split -0.31, HR risk 0.13. slight split headwind (-0.31).""", blast="high"),
            row("Alec Burleson", "L", "+453", 78, "💎", ["vs Scott"], """1 HR, 1 near-HR, 95.9 mph EV. Scott LHB split -1.84, HR risk -1.57. tough split lane (-1.84); pitcher suppresses HR (-1.57).""", blast="good"),
            row("Jordan Walker", "R", "+410", 73, "💎", ["vs Scott"], """0 HR, 97.1 mph EV. Scott RHB split -0.44, HR risk -1.57. tough split lane (-0.44); pitcher suppresses HR (-1.57).""", blast="good"),
            row("Bryan Torres", "L", "N/A", 82, "🌕 💣", ["vs Scott"], """2 HR, 2 near-HR, 91.9 mph EV. Scott LHB split -1.84, HR risk -1.57. tough split lane (-1.84); pitcher suppresses HR (-1.57).""", blast="high"),
            row("JJ Wetherholt", "L", "+526", 72, "💎", ["vs Scott"], """0 HR, 2 near-HR, 91.9 mph EV. Scott LHB split -1.84, HR risk -1.57. tough split lane (-1.84); pitcher suppresses HR (-1.57).""", blast="good"),
        ],
    },
    {
        "title": "TEX @ KC - Kumar Rocker (R, TEX) vs Michael Wacha (R, KC)",
        "description": "Tail key data: Park boost +42% (stadium +13%, weather +29%). Rocker (HR risk -0.42, vs LHB +0.07, vs RHB -0.85). Wacha (HR risk -0.16, vs LHB -0.26, vs RHB -0.10).",
        "rows": [
            row("Michael Massey", "L", "+610", 81, "🌕 💣", ["vs Rocker"], """2 HR, 2 near-HR, 91.0 mph EV. Rocker LHB split +0.07, HR risk -0.42. pitcher suppresses HR (-0.42).""", blast="high"),
            row("Vinnie Pasquantino", "L", "+470", 75, "💎", ["vs Rocker"], """1 HR, 1 near-HR, 93.3 mph EV. Rocker LHB split +0.07, HR risk -0.42. pitcher suppresses HR (-0.42).""", blast="good"),
            row("Bobby Witt Jr.", "R", "+418", 78, "🚀 ⭐ 💎", ["vs Rocker"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 101.2 mph EV. Rocker RHB split -0.85, HR risk -0.42. tough split lane (-0.85); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Starling Marte", "R", "N/A", 78, "💎", ["vs Rocker"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.4 mph EV. Rocker RHB split -0.85, HR risk -0.42. tough split lane (-0.85); pitcher suppresses HR (-0.42).""", blast="good"),
            row("Brandon Nimmo", "L", "+500", 83, "💎", ["vs Wacha"], """1 HR, 3 near-HR, 97.2 mph EV. Wacha LHB split -0.26, HR risk -0.16. slight split headwind (-0.26); pitcher risk below avg (-0.16).""", blast="good"),
            row("Joc Pederson", "L", "+375", 77, "💎", ["vs Wacha"], """1 HR, 2 near-HR, 92.8 mph EV. Wacha LHB split -0.26, HR risk -0.16. slight split headwind (-0.26); pitcher risk below avg (-0.16).""", blast="good"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-11")

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

    out = ROOT / '_games-0611.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
