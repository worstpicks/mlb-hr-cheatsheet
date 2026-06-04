#!/usr/bin/env python3
"""Generate games[] block for 2026-06-04 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Colby Thomas (R)",
    "Dalton Rushing (L)",
    "Jac Caglianone (L)",
    "Kazuma Okamoto (R)",
    "Ketel Marte (S)",
    "Kyle Schwarber (L)",
    "Max Muncy (L)",
    "Pete Crow-Armstrong (L)",
    "Rhys Hoskins (R)",
    "Trea Turner (R)",
    "Yordan Alvarez (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BAL",
    "Alex Bregman (R)": "CHC",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Brayan Rocchio (S)": "CLE",
    "Brent Rooker (R)": "ATH",
    "Brooks Lee (S)": "MIN",
    "Bryce Eldridge (L)": "SF",
    "Bryson Stott (L)": "PHI",
    "Charles McAdoo (R)": "TOR",
    "Coby Mayo (R)": "BAL",
    "Colby Thomas (R)": "ATH",
    "Colton Cowser (L)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "Daulton Varsho (L)": "TOR",
    "Drew Gilbert (L)": "SF",
    "Freddie Freeman (L)": "LAD",
    "Garrett Mitchell (L)": "MIL",
    "Ian Happ (S)": "CHC",
    "J.T. Realmuto (R)": "PHI",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jake Bauers (L)": "MIL",
    "Josh Bell (S)": "MIN",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Kody Clemens (L)": "MIN",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Schwarber (L)": "PHI",
    "Lane Thomas (R)": "KC",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Michael Conforto (L)": "CHC",
    "Michael Harris II (L)": "ATL",
    "Nick Kurtz (L)": "ATH",
    "Oneil Cruz (L)": "PIT",
    "Pete Crow-Armstrong (L)": "CHC",
    "Rhys Hoskins (R)": "CLE",
    "Ryan McMahon (L)": "NYY",
    "Ryan O'Hearn (L)": "PIT",
    "Ryan Waldschmidt (R)": "ARI",
    "Samuel Basallo (L)": "BAL",
    "Shea Langeliers (R)": "ATH",
    "Shohei Ohtani (L)": "LAD",
    "Trea Turner (R)": "PHI",
    "Tristan Gray (L)": "MIN",
    "Ty France (R)": "SD",
    "Vinnie Pasquantino (L)": "KC",
    "Will Smith (R)": "LAD",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Yordan Alvarez (L)": "HOU",
}

BUM_PITCHERS = {
    "Imanaga",
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
        "title": "ATH @ CHC - J.T. Ginn (R, ATH) vs Shota Imanaga 🧤 (R, CHC)",
        "description": "Tail key data: Park boost +34% (stadium -2%, weather +36%). Ginn (HR risk -0.47, vs LHB -0.47, vs RHB -0.11). Imanaga 🧤 (HR risk 1.07, vs LHB +0.76, vs RHB +1.33).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+410", 83, "⭐ 💎", ["vs Ginn"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 96.6 mph EV. Ginn LHB split -0.47, HR risk -0.47. tough split lane (-0.47); pitcher suppresses HR (-0.47).""", blast="good"),
            row("Michael Conforto", "L", "N/A", 77, "💎", ["vs Ginn"], """1 HR, 2 near-HR, 93.0 mph EV. Ginn LHB split -0.47, HR risk -0.47. tough split lane (-0.47); pitcher suppresses HR (-0.47).""", blast="good"),
            row("Ian Happ", "S", "+360", 82, "🌕 💣", ["vs Ginn"], """2 HR, 3 near-HR, 90.5 mph EV. Ginn RHB split -0.11, HR risk -0.47. slight split headwind (-0.11); pitcher suppresses HR (-0.47).""", blast="high"),
            row("Alex Bregman", "R", "+540", 70, "💎", ["vs Ginn"], """1 HR, 1 near-HR, 83.7 mph EV. Ginn RHB split -0.11, HR risk -0.47. slight split headwind (-0.11); pitcher suppresses HR (-0.47).""", blast="good"),
            row("Brent Rooker", "R", "+277", 81, "🌕 💣", ["vs Imanaga"], """2 HR, 2 near-HR, 91.0 mph EV. Imanaga RHB split +1.33, HR risk 1.07.""", blast="high"),
            row("Nick Kurtz", "L", "+296", 81, "🌕 💣", ["vs Imanaga"], """2 HR, 2 near-HR, 90.9 mph EV. Imanaga LHB split +0.76, HR risk 1.07.""", blast="high"),
            row("Shea Langeliers", "R", "+248", 82, "🚀 💎", ["vs Imanaga"], """1 HR, 1 near-HR, 100.2 mph EV. Imanaga RHB split +1.33, HR risk 1.07.""", blast="good"),
            row("Colby Thomas", "R", "+340", 81, "⭐ 💎", ["vs Imanaga"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 97.1 mph EV. Imanaga RHB split +1.33, HR risk 1.07.""", blast="good"),
        ],
    },
    {
        "title": "BAL @ BOS - Trevor Rogers (R, BAL) vs Brayan Bello (R, BOS)",
        "description": "Tail key data: Park boost +5% (stadium -7%, weather +12%). Rogers (HR risk 0.38, vs LHB -0.56, vs RHB +1.01). Bello (HR risk -0.14, vs LHB -0.03, vs RHB -0.22).",
        "rows": [
            row("Wilyer Abreu", "L", "+520", 62, "💎", ["vs Rogers"], """0 HR, 81.2 mph EV. Rogers LHB split -0.56, HR risk 0.38. tough split lane (-0.56); park suppresses carry (-7%)."""),
            row("Willson Contreras", "R", "+390", 65, "💎", ["vs Rogers"], """0 HR, 1 near-HR, 88.8 mph EV. Rogers RHB split +1.01, HR risk 0.38. park suppresses carry (-7%); limited recent HR events."""),
            row("Colton Cowser", "L", "+600", 80, "🌕 💣", ["vs Bello"], """2 HR, 3 near-HR, 84.8 mph EV. Bello LHB split -0.03, HR risk -0.14. slight split headwind (-0.03); pitcher risk below avg (-0.14).""", blast="high"),
            row("Samuel Basallo", "L", "+425", 83, "🌕 💣", ["vs Bello"], """2 HR, 2 near-HR, 93.1 mph EV. Bello LHB split -0.03, HR risk -0.14. slight split headwind (-0.03); pitcher risk below avg (-0.14).""", blast="high"),
            row("Adley Rutschman", "S", "+498", 70, "💎", ["vs Bello"], """0 HR, 94.5 mph EV. Bello RHB split -0.22, HR risk -0.14. slight split headwind (-0.22); pitcher risk below avg (-0.14).""", blast="good"),
            row("Coby Mayo", "R", "+520", 75, "💎", ["vs Bello"], """1 HR, 1 near-HR, 92.9 mph EV. Bello RHB split -0.22, HR risk -0.14. slight split headwind (-0.22); pitcher risk below avg (-0.14).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ NYY - Slade Cecconi (R, CLE) vs Carlos Rodon (R, NYY)",
        "description": "Tail key data: Park boost +3% (stadium +7%, weather -4%). Cecconi (HR risk -0.32, vs LHB -0.39, vs RHB +0.37). Rodon (HR risk -0.53, vs LHB +0.37, vs RHB -0.97).",
        "rows": [
            row("Ben Rice", "L", "+260", 72, "⭐ 💎", ["vs Cecconi"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 87.2 mph EV. Cecconi LHB split -0.39, HR risk -0.32. slight split headwind (-0.39); pitcher risk below avg (-0.32).""", blast="good"),
            row("Ryan McMahon", "L", "+470", 89, "🌕 💣", ["vs Cecconi"], """3 HR, 3 near-HR, 93.4 mph EV. Cecconi LHB split -0.39, HR risk -0.32. slight split headwind (-0.39); pitcher risk below avg (-0.32).""", blast="high"),
            row("Rhys Hoskins", "R", "+390", 92, "🚀 ⭐ 🌕 💣", ["vs Rodon"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 101.4 mph EV. Rodon RHB split -0.97, HR risk -0.53. tough split lane (-0.97); pitcher suppresses HR (-0.53).""", blast="high"),
            row("Kyle Manzardo", "L", "+253", 72, "💎", ["vs Rodon"], """1 HR, 2 near-HR, 83.6 mph EV. Rodon LHB split +0.37, HR risk -0.53. pitcher suppresses HR (-0.53); weather carry headwind (-4%).""", blast="good"),
            row("Brayan Rocchio", "S", "+980", 71, "💎", ["vs Rodon"], """0 HR, 1 near-HR, 93.1 mph EV. Rodon RHB split -0.97, HR risk -0.53. tough split lane (-0.97); pitcher suppresses HR (-0.53).""", blast="good"),
        ],
    },
    {
        "title": "KC @ MIN - Seth Lugo (R, KC) vs Andrew Morris (R, MIN)",
        "description": "Tail key data: Park boost +1% (stadium -7%, weather +8%). Lugo (HR risk 0.31, vs LHB +0.00, vs RHB +1.07). Morris (HR risk -1.14, vs LHB -0.58, vs RHB -1.36).",
        "rows": [
            row("Josh Bell", "S", "+525", 73, "💎", ["vs Lugo"], """0 HR, 1 near-HR, 94.7 mph EV. Lugo RHB split +1.07, HR risk 0.31. park suppresses carry (-7%); limited recent HR events.""", blast="good"),
            row("Brooks Lee", "S", "+640", 80, "🌕 💣", ["vs Lugo"], """2 HR, 3 near-HR, 88.3 mph EV. Lugo RHB split +1.07, HR risk 0.31. park suppresses carry (-7%).""", blast="high"),
            row("Tristan Gray", "L", "+650", 81, "💎", ["vs Lugo"], """1 HR, 3 near-HR, 95.4 mph EV. Lugo LHB split +0.00, HR risk 0.31. park suppresses carry (-7%).""", blast="good"),
            row("Kody Clemens", "L", "+425", 80, "💎", ["vs Lugo"], """1 HR, 3 near-HR, 94.2 mph EV. Lugo LHB split +0.00, HR risk 0.31. park suppresses carry (-7%).""", blast="good"),
            row("Bobby Witt Jr.", "R", "+425", 74, "💎", ["vs Morris"], """1 HR, 2 near-HR, 90.2 mph EV. Morris RHB split -1.36, HR risk -1.14. tough split lane (-1.36); pitcher suppresses HR (-1.14).""", blast="good"),
            row("Lane Thomas", "R", "N/A", 74, "💎", ["vs Morris"], """1 HR, 2 near-HR, 90.2 mph EV. Morris RHB split -1.36, HR risk -1.14. tough split lane (-1.36); pitcher suppresses HR (-1.14).""", blast="good"),
            row("Vinnie Pasquantino", "L", "+490", 74, "💎", ["vs Morris"], """1 HR, 3 near-HR, 87.2 mph EV. Morris LHB split -0.58, HR risk -1.14. tough split lane (-0.58); pitcher suppresses HR (-1.14).""", blast="good"),
            row("Jac Caglianone", "L", "+575", 76, "🚀 ⭐ 💎", ["vs Morris"], """Worst Pickz Favorite. 0 HR, 106.7 mph EV. Morris LHB split -0.58, HR risk -1.14. tough split lane (-0.58); pitcher suppresses HR (-1.14).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ ARI - Justin Wrobleski (R, LAD) vs Ryne Nelson (R, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -7%, weather +0%). Wrobleski (HR risk -0.10, vs LHB +0.13, vs RHB -0.31). Nelson (HR risk 0.79, vs LHB +0.13, vs RHB +1.39).",
        "rows": [
            row("Ketel Marte", "S", "+426", 83, "⭐ 🌕 💣", ["vs Wrobleski"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 90.8 mph EV. Wrobleski RHB split -0.31, HR risk -0.10. slight split headwind (-0.31); pitcher risk below avg (-0.10).""", blast="high"),
            row("Corbin Carroll", "L", "+575", 70, "💎", ["vs Wrobleski"], """1 HR, 1 near-HR, 85.0 mph EV. Wrobleski LHB split +0.13, HR risk -0.10. pitcher risk below avg (-0.10); park/weather net drag (-8%).""", blast="good"),
            row("Ryan Waldschmidt", "R", "+1350", 70, "💎", ["vs Wrobleski"], """0 HR, 1 near-HR, 92.4 mph EV. Wrobleski RHB split -0.31, HR risk -0.10. slight split headwind (-0.31); pitcher risk below avg (-0.10).""", blast="good"),
            row("Dalton Rushing", "L", "+437", 68, "⭐ 💎", ["vs Nelson"], """Worst Pickz Favorite. 0 HR, 2 near-HR, 85.8 mph EV. Nelson LHB split +0.13, HR risk 0.79. park/weather net drag (-8%); lighter EV form (85.8 mph).""", blast="good"),
            row("Freddie Freeman", "L", "+525", 87, "🌕 💣", ["vs Nelson"], """3 HR, 3 near-HR, 90.8 mph EV. Nelson LHB split +0.13, HR risk 0.79. park/weather net drag (-8%).""", blast="high"),
            row("Shohei Ohtani", "L", "+260", 77, "💎", ["vs Nelson"], """1 HR, 1 near-HR, 94.8 mph EV. Nelson LHB split +0.13, HR risk 0.79. park/weather net drag (-8%).""", blast="good"),
            row("Will Smith", "R", "+550", 72, "💎", ["vs Nelson"], """1 HR, 2 near-HR, 87.5 mph EV. Nelson RHB split +1.39, HR risk 0.79. park/weather net drag (-8%); lighter EV form (87.5 mph).""", blast="good"),
            row("Max Muncy", "L", "+410", 86, "⭐ 🌕 💣", ["vs Nelson"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.2 mph EV. Nelson LHB split +0.13, HR risk 0.79. park/weather net drag (-8%).""", blast="high"),
        ],
    },
    {
        "title": "PIT @ HOU - Jared Jones (R, PIT) vs Kai-Wei Teng (R, HOU)",
        "description": "Tail key data: Park boost +6% (stadium +6%, weather -1%). Away starter risk unavailable. Teng (HR risk -0.30, vs LHB -0.42, vs RHB -0.09).",
        "rows": [
            row("Yordan Alvarez", "L", "+310", 98, "🚀 ⭐ 🌕 💣", ["vs Jones"], """Worst Pickz Favorite. 3 HR, 5 near-HR, 100.4 mph EV. Jones split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Oneil Cruz", "L", "+430", 79, "💎", ["vs Teng"], """1 HR, 2 near-HR, 94.6 mph EV. Teng LHB split -0.42, HR risk -0.30. tough split lane (-0.42); pitcher risk below avg (-0.30).""", blast="good"),
            row("Brandon Lowe", "L", "+420", 83, "🌕 💣", ["vs Teng"], """1 HR, 4 near-HR, 93.1 mph EV. Teng LHB split -0.42, HR risk -0.30. tough split lane (-0.42); pitcher risk below avg (-0.30).""", blast="high"),
            row("Ryan O'Hearn", "L", "+610", 80, "🌕 💣", ["vs Teng"], """2 HR, 2 near-HR, 90.2 mph EV. Teng LHB split -0.42, HR risk -0.30. tough split lane (-0.42); pitcher risk below avg (-0.30).""", blast="high"),
        ],
    },
    {
        "title": "SD @ PHI - Lucas Giolito (R, SD) vs Zack Wheeler (R, PHI)",
        "description": "Tail key data: Park boost +9% (stadium +14%, weather -5%). Giolito (HR risk -0.22, vs LHB -0.44, vs RHB +0.37). Wheeler (HR risk -0.09, vs LHB -0.00, vs RHB -0.34).",
        "rows": [
            row("Kyle Schwarber", "L", "+226", 88, "⭐ 🌕 💣", ["vs Giolito"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 97.8 mph EV. Giolito LHB split -0.44, HR risk -0.22. tough split lane (-0.44); pitcher risk below avg (-0.22).""", blast="high"),
            row("Brandon Marsh", "L", "+570", 72, "💎", ["vs Giolito"], """0 HR, 95.6 mph EV. Giolito LHB split -0.44, HR risk -0.22. tough split lane (-0.44); pitcher risk below avg (-0.22).""", blast="good"),
            row("Bryson Stott", "L", "+670", 75, "💎", ["vs Giolito"], """1 HR, 2 near-HR, 90.6 mph EV. Giolito LHB split -0.44, HR risk -0.22. tough split lane (-0.44); pitcher risk below avg (-0.22).""", blast="good"),
            row("Trea Turner", "R", "+579", 77, "⭐ 💎", ["vs Giolito"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.0 mph EV. Giolito RHB split +0.37, HR risk -0.22. pitcher risk below avg (-0.22); weather carry headwind (-5%).""", blast="good"),
            row("J.T. Realmuto", "R", "+630", 70, "💎", ["vs Giolito"], """1 HR, 1 near-HR, 86.0 mph EV. Giolito RHB split +0.37, HR risk -0.22. pitcher risk below avg (-0.22); weather carry headwind (-5%).""", blast="good"),
            row("Manny Machado", "R", "+600", 76, "💎", ["vs Wheeler"], """1 HR, 2 near-HR, 91.6 mph EV. Wheeler RHB split -0.34, HR risk -0.09. slight split headwind (-0.34); pitcher risk below avg (-0.09).""", blast="good"),
            row("Ty France", "R", "+760", 79, "💎", ["vs Wheeler"], """1 HR, 2 near-HR, 94.6 mph EV. Wheeler RHB split -0.34, HR risk -0.09. slight split headwind (-0.34); pitcher risk below avg (-0.09).""", blast="good"),
        ],
    },
    {
        "title": "SF @ MIL - Adrian Houser (R, SF) vs Coleman Crow (R, MIL)",
        "description": "Tail key data: Park boost +11% (stadium +11%, weather +1%). Houser (HR risk -0.11, vs LHB +0.11, vs RHB -0.48). Crow (HR risk -0.17, vs LHB -0.38, vs RHB +0.28).",
        "rows": [
            row("Jake Bauers", "L", "+470", 79, "💎", ["vs Houser"], """1 HR, 1 near-HR, 97.3 mph EV. Houser LHB split +0.11, HR risk -0.11. pitcher risk below avg (-0.11).""", blast="good"),
            row("Jackson Chourio", "R", "+570", 77, "💎", ["vs Houser"], """0 HR, 3 near-HR, 94.6 mph EV. Houser RHB split -0.48, HR risk -0.11. tough split lane (-0.48); pitcher risk below avg (-0.11).""", blast="good"),
            row("Garrett Mitchell", "L", "+590", 72, "💎", ["vs Houser"], """0 HR, 96.1 mph EV. Houser LHB split +0.11, HR risk -0.11. pitcher risk below avg (-0.11); limited recent HR events.""", blast="good"),
            row("Drew Gilbert", "L", "+920", 78, "💎", ["vs Crow"], """1 HR, 1 near-HR, 95.7 mph EV. Crow LHB split -0.38, HR risk -0.17. slight split headwind (-0.38); pitcher risk below avg (-0.17).""", blast="good"),
            row("Bryce Eldridge", "L", "+500", 72, "💎", ["vs Crow"], """0 HR, 1 near-HR, 93.6 mph EV. Crow LHB split -0.38, HR risk -0.17. slight split headwind (-0.38); pitcher risk below avg (-0.17).""", blast="good"),
            row("Willy Adames", "R", "+415", 73, "💎", ["vs Crow"], """0 HR, 2 near-HR, 93.2 mph EV. Crow RHB split +0.28, HR risk -0.17. pitcher risk below avg (-0.17).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ ATL - Mason Fluharty (R, TOR) vs Chris Sale (R, ATL)",
        "description": "Tail key data: Park boost -17% (stadium -5%, weather -12%). Away starter risk unavailable. Sale (HR risk -0.75, vs LHB -0.47, vs RHB -0.62).",
        "rows": [
            row("Michael Harris II", "L", "+520", 71, "💎", ["vs Fluharty"], """1 HR, 1 near-HR, 89.4 mph EV. Fluharty split/risk data unavailable. limited split/risk sample; park/weather net drag (-17%).""", blast="good"),
            row("Matt Olson", "L", "+416", 63, "💎", ["vs Fluharty"], """0 HR, 88.6 mph EV. Fluharty split/risk data unavailable. limited split/risk sample; park/weather net drag (-17%)."""),
            row("Kazuma Okamoto", "R", "+570", 81, "⭐ 🌕 💣", ["vs Sale"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 90.8 mph EV. Sale RHB split -0.62, HR risk -0.75. tough split lane (-0.62); pitcher suppresses HR (-0.75).""", blast="high"),
            row("Daulton Varsho", "L", "+1200", 64, "💎", ["vs Sale"], """0 HR, 1 near-HR, 84.0 mph EV. Sale LHB split -0.47, HR risk -0.75. tough split lane (-0.47); pitcher suppresses HR (-0.75)."""),
            row("Charles McAdoo", "R", "N/A", 70, "💎", ["vs Sale"], """1 HR, 1 near-HR, 85.0 mph EV. Sale RHB split -0.62, HR risk -0.75. tough split lane (-0.62); pitcher suppresses HR (-0.75).""", blast="good"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-04")

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

    out = ROOT / '_games-0604.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
