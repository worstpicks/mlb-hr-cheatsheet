#!/usr/bin/env python3
"""Generate games[] block for 2026-05-28 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Wilyer Abreu (L)",
    "Pete Alonso (R)",
    "Yohendrick Pinango (L)",
    "Brandon Lowe (L)",
    "Spencer Horwitz (L)",
    "Brandon Nimmo (L)",
    "Yordan Alvarez (L)",
}

PLAYER_TEAMS = {
    "Dillon Dingler (R)": "DET",
    "Colt Keith (L)": "DET",
    "Gage Workman (L)": "DET",
    "Mike Trout (R)": "LAA",
    "Zach Neto (R)": "LAA",
    "Vaughn Grissom (R)": "LAA",
    "Donovan Walton (L)": "LAA",
    "Colson Montgomery (L)": "CWS",
    "Miguel Vargas (R)": "CWS",
    "Munetaka Murakami (L)": "CWS",
    "Derek Hill (R)": "CWS",
    "Byron Buxton (R)": "MIN",
    "Wilyer Abreu (L)": "BOS",
    "Isiah Kiner-Falefa (R)": "BOS",
    "Jarren Duran (L)": "BOS",
    "Matt Olson (L)": "ATL",
    "Jorge Mateo (R)": "ATL",
    "Mauricio Dubon (R)": "ATL",
    "Coby Mayo (R)": "BAL",
    "Pete Alonso (R)": "BAL",
    "Adley Rutschman (S)": "BAL",
    "Gunnar Henderson (L)": "BAL",
    "Daulton Varsho (L)": "TOR",
    "Ernie Clement (R)": "TOR",
    "Yohendrick Pinango (L)": "TOR",
    "Brandon Lowe (L)": "PIT",
    "Spencer Horwitz (L)": "PIT",
    "Oneil Cruz (L)": "PIT",
    "Marcell Ozuna (R)": "PIT",
    "Michael Busch (L)": "CHC",
    "Ian Happ (S)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Brandon Nimmo (L)": "TEX",
    "Joc Pederson (L)": "TEX",
    "Yordan Alvarez (L)": "HOU",
}


def display(name, hand):
    return f"{name} ({hand})"


def odds_text(odds):
    return "Listed prop - Over 0.5 HR" if odds == "N/A" else f"Listed {odds} - Over 0.5 HR"


def row(name, hand, odds, score, emojis, chips, note, blast=None):
    item = {
        "name": display(name, hand),
        "odds": odds_text(odds),
        "score": score,
        "emojis": emojis,
        "note": note,
        "chips": chips,
    }
    if blast:
        item["blast"] = blast
    return item


def n(player, pitcher, park, angle):
    angle = angle.rstrip(".")
    return f"{angle}. Draws opposing starter {pitcher}; {park}."


BUM_PITCHERS = {
    "Rodriguez",
    "Flaherty",
    "Rea",
    "Eovaldi",
    "Corbin",
}


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
        "title": "LAA @ DET - Jack Flaherty 🧤 (L, LAA) vs Grayson Rodriguez 🧤 (R, DET)",
        "description": "Comerica Park — Ballpark Pal grades -13% HR and -5% runs with cool 62°F air, 15 mph L-R wind, and high air pressure. Grayson Rodriguez carries 1.58 LHB HR risk; Jack Flaherty's RHB split is the cleaner Angels attack lane despite Detroit's large outfield.",
        "rows": [
            row("Zach Neto", "R", "+460", 80, "🌕 💣", ["vs Rodriguez"], n("Zach Neto", "Rodriguez", "Rodriguez RHB HR risk fits Neto's pull-side power", "1 HR, 2 near-HR with 95.5 mph EV and 25.0% barrels"), "high"),
            row("Mike Trout", "R", "+380", 82, "💎", ["vs Rodriguez"], n("Mike Trout", "Rodriguez", "Rodriguez RHB sample keeps Trout's pull-air live", "0 HR but 88.9 mph EV and 14.3% barrels in the pitch-mix window"), "good"),
            row("Vaughn Grissom", "R", "+1000", 71, "💎", ["vs Rodriguez"], n("Vaughn Grissom", "Rodriguez", "righty lane versus Rodriguez's weaker RHB split", "2 HR, 2 near-HR with 90.3 mph EV and 22.2% barrels"), "good"),
            row("Donovan Walton", "L", "N/A", 57, "💎", ["vs Rodriguez"], n("Donovan Walton", "Rodriguez", "1 near-HR with 95.5 mph EV but no listed odds posted", "0 HR, 1 near-HR with 25.0% barrels versus Rodriguez")),
            row("Dillon Dingler", "R", "+550", 65, "💎", ["vs Flaherty"], n("Dillon Dingler", "Flaherty", "Flaherty RHB HR leakage is the Tigers righty lane", "0 HR with 81.6 mph EV in a thin sample versus Flaherty")),
            row("Colt Keith", "L", "+790", 66, "💎", ["vs Flaherty"], n("Colt Keith", "Flaherty", "Flaherty suppresses LHB but Keith's near-HR keeps thin lefty value", "0 HR, 1 near-HR with 89.4 mph EV and 8.3% barrels"), "good"),
            row("Gage Workman", "L", "+650", 60, "💎", ["vs Flaherty"], n("Gage Workman", "Flaherty", "Flaherty LHB sample is Workman's only HR path", "0 HR with 94.4 mph EV peak but 60.0% K rate in the window")),
        ],
    },
    {
        "title": "MIN @ CWS - Taj Bradley (R, MIN) vs Davis Martin (R, CWS)",
        "description": "Rate Field — -3% HR row with -1% combined runs, cool 64°F air, 14 mph L-R wind, and 1022 mb high pressure. Davis Martin suppresses HRs; Chicago bats get the form-driven lane versus a Twins arm with limited sample.",
        "rows": [
            row("Miguel Vargas", "R", "+460", 83, "🌕 💣", ["vs Bradley"], n("Miguel Vargas", "Bradley", "Bradley RHB split fits Vargas' elite power window", "1 HR, 1 near-HR with 98.3 mph EV and 25.0% barrels"), "high"),
            row("Munetaka Murakami", "L", "+360", 84, "🌕 💣", ["vs Bradley"], n("Munetaka Murakami", "Bradley", "lefty pull-air versus Bradley's limited LHB sample", "0 HR with 84.6 mph EV and loud hard-hit in the pitch-mix window"), "high"),
            row("Colson Montgomery", "L", "+500", 70, "💎", ["vs Bradley"], n("Colson Montgomery", "Bradley", "Bradley LHB leakage supports Montgomery lift", "0 HR, 1 near-HR with 92.8 mph EV and 11.1% barrels"), "good"),
            row("Derek Hill", "R", "+820", 64, "💎", ["vs Bradley"], n("Derek Hill", "Bradley", "Bradley RHB lane with 1 HR in the sample", "1 HR, 1 near-HR with 81.6 mph EV versus Bradley")),
            row("Byron Buxton", "R", "+290", 90, "🌕 💣", ["vs Martin"], n("Byron Buxton", "Martin", "Martin RHB split plus Buxton's slate-best power tier", "3 HR, 3 near-HR with 95.1 mph EV and 17.6% barrels"), "high"),
        ],
    },
    {
        "title": "ATL @ BOS - Chris Sale (L, ATL) vs Payton Tolle (L, BOS)",
        "description": "Fenway Park — -18% HR row with -4% runs, cool 61°F air, and 6 mph in-blowing wind despite high receptivity. Chris Sale suppresses Boston; Braves lefties face Payton Tolle's limited sample in a pitcher-friendly Thursday environment.",
        "rows": [
            row("Matt Olson", "L", "+440", 76, "🌕 💎", ["vs Tolle"], n("Matt Olson", "Tolle", "Tolle LHB sample is the Braves lefty lane at Fenway", "1 HR, 1 near-HR with 93.0 mph EV and 7.1% barrels"), "high"),
            row("Jorge Mateo", "R", "N/A", 61, "💎", ["vs Tolle"], n("Jorge Mateo", "Tolle", "1 HR in sample but no listed odds posted", "1 HR, 1 near-HR with 90.4 mph EV and 11.1% barrels versus Tolle")),
            row("Mauricio Dubon", "R", "+900", 62, "💎", ["vs Tolle"], n("Mauricio Dubon", "Tolle", "Tolle RHB split is the Braves righty angle", "0 HR, 1 near-HR with 91.0 mph EV in the pitch-mix window")),
            row("Wilyer Abreu", "L", "+820", 78, "⭐ 💎", ["vs Sale"], n("Wilyer Abreu", "Sale", "Sale LHB split is suppressive but Abreu carries 87.9 mph EV", "Worst Pickz favorite with 0 HR but 12.5% barrels and pull-side fit versus Sale"), "good"),
            row("Jarren Duran", "L", "+880", 77, "💎", ["vs Sale"], n("Jarren Duran", "Sale", "lefty lane versus Sale despite Fenway's -18% HR drag", "0 HR with 93.0 mph EV and 57.1% hard-hit versus Sale"), "good"),
            row("Isiah Kiner-Falefa", "R", "+1700", 63, "💎", ["vs Sale"], n("Isiah Kiner-Falefa", "Sale", "Sale RHB split is the Red Sox righty longshot lane", "1 HR, 1 near-HR with 85.3 mph EV in a small sample")),
        ],
    },
    {
        "title": "TOR @ BAL - Patrick Corbin 🧤 (L, TOR) vs Chris Bassitt (R, BAL)",
        "description": "Oriole Park — -22% HR row (slate-worst) with -6% runs, warm 70°F air, and 13 mph wind. Patrick Corbin's 0.27 vs-RHB HR risk keeps Baltimore righties live despite the brutal HR model.",
        "rows": [
            row("Coby Mayo", "R", "+500", 86, "🌕 💣", ["vs Corbin"], n("Coby Mayo", "Corbin", "Corbin RHB HR leakage is the Orioles' clearest attack lane", "2 HR, 2 near-HR with 93.1 mph EV and 21.4% barrels"), "high"),
            row("Pete Alonso", "R", "+360", 85, "⭐ 🌕 💣", ["vs Corbin"], n("Pete Alonso", "Corbin", "Corbin RHB split plus Alonso's 97.1 mph EV peak", "Worst Pickz favorite with 0 HR, 1 near-HR and 22.2% barrels versus Corbin"), "high"),
            row("Gunnar Henderson", "L", "+590", 74, "💎", ["vs Corbin"], n("Gunnar Henderson", "Corbin", "Corbin suppresses LHB but Henderson's contact keeps him in play", "0 HR with 84.1 mph EV in the pitch-mix sample"), "good"),
            row("Adley Rutschman", "S", "+610", 67, "💎", ["vs Corbin"], n("Adley Rutschman", "Corbin", "switch lane versus Corbin's RHB weakness", "0 HR with 14.3% barrels and 88.8 mph EV versus Corbin")),
            row("Yohendrick Pinango", "L", "+840", 93, "🚀 ⭐ 🌕 💣", ["vs Bassitt"], n("Yohendrick Pinango", "Bassitt", "105.4 mph EV and 40.0% barrels versus Bassitt", "Worst Pickz favorite with 1 HR, 2 near-HR and slate-best EV in the window"), "high"),
            row("Ernie Clement", "R", "+1220", 69, "💎", ["vs Bassitt"], n("Ernie Clement", "Bassitt", "1 HR, 2 near-HR with pull-side air versus Bassitt", "1 HR, 2 near-HR with 78.5 mph EV and 15.4% barrels"), "good"),
            row("Daulton Varsho", "L", "+500", 68, "💎", ["vs Bassitt"], n("Daulton Varsho", "Bassitt", "lefty lane versus Bassitt at Camden's -22% HR row", "0 HR with 86.8 mph EV and 41.7% hard-hit versus Bassitt")),
        ],
    },
    {
        "title": "CHC @ PIT - Colin Rea 🧤 (R, CHC) vs Paul Skenes (R, PIT)",
        "description": "PNC Park — -18% HR row with -3% runs, cooling 66°F air, and 9 mph wind. Colin Rea is the slate's top HR-risk arm (1.21, 1.70 vs RHB); Paul Skenes suppresses Chicago bats despite Pittsburgh's shallow right side.",
        "rows": [
            row("Brandon Lowe", "L", "+410", 96, "⭐ 🌕 💣", ["vs Rea"], n("Brandon Lowe", "Rea", "Rea is slate-high HR risk with 3 HR and 38.5% barrels in the window", "Worst Pickz favorite with 3 HR, 5 near-HR and 98.3 mph EV versus Rea"), "high"),
            row("Spencer Horwitz", "L", "+870", 81, "⭐ 💎", ["vs Rea"], n("Spencer Horwitz", "Rea", "Rea LHB leakage plus Horwitz's 2 HR in the sample", "Worst Pickz favorite with 2 HR, 2 near-HR, 88.0 mph EV and 30.0% barrels versus Rea"), "good"),
            row("Oneil Cruz", "L", "+440", 79, "🚀 🌕 💣", ["vs Rea"], n("Oneil Cruz", "Rea", "Rea RHB damage profile fits Cruz pull-air", "0 HR with 100.6 mph EV and 77.8% hard-hit versus Rea"), "high"),
            row("Marcell Ozuna", "R", "+710", 59, "💎", ["vs Rea"], n("Marcell Ozuna", "Rea", "Rea RHB split is Ozuna's clearest path at PNC", "1 HR, 2 near-HR with 92.6 mph EV and 13.3% barrels versus Rea"), "good"),
            row("Michael Busch", "L", "+630", 72, "💎 📜", ["vs Skenes"], n("Michael Busch", "Skenes", "1 career HR in 14 BvP AB versus Skenes", "1 HR, 1 near-HR and 13.3% barrels versus Skenes with 90.3 mph EV"), "good"),
            row("Ian Happ", "S", "+725", 73, "💎", ["vs Skenes"], n("Ian Happ", "Skenes", "12 AB BvP sample versus Skenes keeps the switch lane in play", "1 HR, 1 near-HR with 88.1 mph EV and 12.8% barrels versus Skenes"), "good"),
            row("Michael Conforto", "L", "N/A", 58, "💎", ["vs Skenes"], n("Michael Conforto", "Skenes", "1 near-HR in sample but no listed odds posted", "0 HR, 1 near-HR with 36.4% hard-hit versus Skenes")),
        ],
    },
    {
        "title": "HOU @ TEX - Spencer Arrighetti (R, HOU) vs Nathan Eovaldi 🧤 (R, TEX)",
        "description": "Globe Life Field — -11% HR row with -7% runs, roof closed, and 83°F dome air. Nathan Eovaldi carries 0.79 vs-LHB HR risk; Houston's top bats are the clearest attack targets in the night cap.",
        "rows": [
            row("Yordan Alvarez", "L", "+314", 92, "⭐ 🌕 💣 📜", ["vs Eovaldi"], n("Yordan Alvarez", "Eovaldi", "2 career HR in 23 BvP AB plus Eovaldi LHB HR risk", "Worst Pickz favorite with 1 HR, 2 near-HR and 96.5 mph EV versus Eovaldi"), "high"),
            row("Brandon Nimmo", "L", "+525", 88, "⭐ 🌕 💣", ["vs Arrighetti"], n("Brandon Nimmo", "Arrighetti", "Arrighetti LHB sample is the Rangers lefty attack lane", "Worst Pickz favorite with 2 HR, 3 near-HR, 92.2 mph EV and 29.4% barrels versus Arrighetti"), "high"),
            row("Joc Pederson", "L", "+548", 75, "💎", ["vs Arrighetti"], n("Joc Pederson", "Arrighetti", "2 HR in the pitch-mix window versus Arrighetti", "2 HR, 2 near-HR with 87.3 mph EV and 12.5% barrels versus Arrighetti"), "good"),
        ],
    },
]

PROP_NAMES = {name.split(" (")[0] for name in PLAYER_TEAMS}
found = {r["name"].split(" (")[0] for g in games for r in g["rows"]}
missing = sorted(PROP_NAMES - found)
if missing:
    raise SystemExit(f"Missing props: {missing}")

for game in games:
    for entry in game["rows"]:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)


def js_string(value):
    return json.dumps(value, ensure_ascii=False)


def emit_games_js(games_data):
    lines = ["const games = ["]
    for game in games_data:
        lines.append("    {")
        lines.append(f"        title: {js_string(game['title'])},")
        lines.append(f"        description: {js_string(game['description'])},")
        lines.append("        rows: [")
        for entry in game["rows"]:
            parts = [
                f"name: {js_string(entry['name'])}",
                f"odds: {js_string(entry['odds'])}",
                f"score: {entry['score']}",
                f"emojis: {js_string(entry['emojis'])}",
                f"note: {js_string(entry['note'])}",
                f"chips: {js_string(entry['chips'])}",
            ]
            if entry.get("blast"):
                parts.append(f"blast: {js_string(entry['blast'])}")
            lines.append("            { " + ", ".join(parts) + " },")
        lines.append("        ],")
        lines.append("    },")
    lines.append("];")
    return "\n".join(lines)


if __name__ == "__main__":
    print(emit_games_js(games))
