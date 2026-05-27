#!/usr/bin/env python3
"""Generate games[] block for 2026-05-27 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Kyle Schwarber (L)",
    "Bryce Harper (L)",
    "Jonathan Aranda (L)",
    "Brandon Lowe (L)",
    "Michael Busch (L)",
    "Jarren Duran (L)",
    "Elly De La Cruz (S)",
    "Salvador Perez (R)",
    "Jac Caglianone (L)",
    "Paul Goldschmidt (R)",
    "Miguel Vargas (R)",
    "Yordan Alvarez (L)",
}

PLAYER_TEAMS = {
    "Ramon Laureano (R)": "SD",
    "Kyle Schwarber (L)": "PHI",
    "Bryce Harper (L)": "PHI",
    "Coby Mayo (R)": "BAL",
    "Taylor Ward (R)": "BAL",
    "Jonathan Aranda (L)": "TB",
    "Yandy Diaz (R)": "TB",
    "Junior Caminero (R)": "TB",
    "Brandon Lowe (L)": "PIT",
    "Spencer Horwitz (L)": "PIT",
    "Oneil Cruz (L)": "PIT",
    "Alex Bregman (R)": "CHC",
    "Ian Happ (S)": "CHC",
    "Michael Busch (L)": "CHC",
    "Riley Greene (L)": "DET",
    "Jo Adell (R)": "LAA",
    "Zach Neto (R)": "LAA",
    "Vaughn Grissom (R)": "LAA",
    "Jarren Duran (L)": "BOS",
    "Ceddanne Rafaela (R)": "BOS",
    "Willson Contreras (R)": "BOS",
    "Matt Olson (L)": "ATL",
    "Michael Harris II (L)": "ATL",
    "Bo Bichette (R)": "NYM",
    "Elly De La Cruz (S)": "CIN",
    "Nathaniel Lowe (L)": "CIN",
    "Will Benson (L)": "CIN",
    "Matt McLain (R)": "CIN",
    "Salvador Perez (R)": "KC",
    "Bobby Witt Jr. (R)": "KC",
    "Jac Caglianone (L)": "KC",
    "Carter Jensen (L)": "KC",
    "Paul Goldschmidt (R)": "NYY",
    "Anthony Volpe (R)": "NYY",
    "Trent Grisham (L)": "NYY",
    "Miguel Vargas (R)": "CWS",
    "Munetaka Murakami (L)": "CWS",
    "Colson Montgomery (L)": "CWS",
    "Byron Buxton (R)": "MIN",
    "Brandon Nimmo (L)": "TEX",
    "Kyle Higashioka (R)": "TEX",
    "Yordan Alvarez (L)": "HOU",
    "Christian Walker (R)": "HOU",
    "Zach Dezenzo (R)": "HOU",
    "Shohei Ohtani (L)": "LAD",
    "Freddie Freeman (L)": "LAD",
    "Will Smith (R)": "LAD",
    "TJ Rumfield (L)": "COL",
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
    "Gibson",
    "Taillon",
    "Chandler",
    "Early",
    "Tong",
    "Burrows",
    "deGrom",
    "Sugano",
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
        "title": "PHI @ SD - Cristopher Sanchez (L, PHI) vs Walker Buehler (R, SD)",
        "description": "Petco Park — Ballpark Pal grades -7% HR with cool 63°F air and 10 mph out-blowing wind. Cristopher Sanchez suppresses contact quality; Philly lefties still carry slate-best form versus Buehler's RHB split.",
        "rows": [
            row("Kyle Schwarber", "L", "+290", 96, "🚀 ⭐ 🌕 💣", ["vs Buehler"], n("Kyle Schwarber", "Buehler", "short porch still fights Petco drag", "Worst Pickz favorite with 10 HR, 12 near-HR and 28.3% barrels"), "high"),
            row("Bryce Harper", "L", "+575", 88, "🚀 ⭐ 🌕", ["vs Buehler"], n("Bryce Harper", "Buehler", "BvP HR history helps the Harper lane", "Worst Pickz favorite with 7 HR, 10 near-HR and 14.5% barrels"), "high"),
            row("Ramon Laureano", "R", "+1050", 72, "💎 📜", ["vs Sanchez"], n("Ramon Laureano", "Sanchez", "BvP shows 2 HR in a thin sample", "1 HR, 2 near-HR with 16.7% barrels versus Sanchez RHB split")),
        ],
    },
    {
        "title": "TB @ BAL - Steven Matz (L, TB) vs Trey Gibson 🧤 (R, BAL)",
        "description": "Oriole Park — +8% HR row with 82°F air and 5 mph L-R wind. Trey Gibson is the slate's top HR-risk arm; Rays bats get the cleaner attack profile versus Baltimore's leaky righty.",
        "rows": [
            row("Junior Caminero", "R", "+375", 90, "🚀 🌕 💣 ⚾ 🕊️ 🧤", ["vs Gibson"], n("Junior Caminero", "Gibson", "Gibson is slate-high HR risk for Rays righties", "4 HR, 5 near-HR, 91.6 mph EV and 11.7% barrels"), "high"),
            row("Jonathan Aranda", "L", "+575", 94, "🚀 ⭐ 🌕 💣 ⚾ 🕊️ 🧤", ["vs Gibson"], n("Jonathan Aranda", "Gibson", "Gibson LHB leakage plus Oriole carry", "Worst Pickz favorite with 8 HR, 12 near-HR and 17.1% barrels"), "high"),
            row("Yandy Diaz", "R", "+650", 82, "🚀 💎 ⚾ 🕊️ 🧤", ["vs Gibson"], n("Yandy Diaz", "Gibson", "Gibson RHB sample is the Rays righty lane", "2 HR, 5 near-HR with 10.9% barrels"), "good"),
            row("Coby Mayo", "R", "+500", 78, "🚀 💎", ["vs Matz"], n("Coby Mayo", "Matz", "Matz RHB split fits Mayo's pull-side profile", "1 HR, 1 near-HR with 11.8% barrels versus Matz"), "good"),
            row("Taylor Ward", "R", "+490", 74, "💎", ["vs Matz"], n("Taylor Ward", "Matz", "Matz RHB HR risk keeps Ward in the Orioles lane", "0 HR but 18.5% walk rate and pull-side fit versus Matz")),
        ],
    },
    {
        "title": "CHC @ PIT - Jameson Taillon 🧤 (R, CHC) vs Bubba Chandler 🧤 (R, PIT)",
        "description": "PNC Park — +5% runs row with warm 75°F air despite a -4% HR model. Jameson Taillon is the board's loudest HR-leaky starter; Pittsburgh lefties are the premium Taillon targets.",
        "rows": [
            row("Brandon Lowe", "L", "+375", 95, "🚀 ⭐ 🌕 💣", ["vs Taillon"], n("Brandon Lowe", "Taillon", "Taillon is slate-high HR risk with 10 HR in the window", "Worst Pickz favorite with 10 HR, 15 near-HR and 23.4% barrels"), "high"),
            row("Michael Busch", "L", "+500", 86, "🚀 ⭐ 💎", ["vs Taillon"], n("Michael Busch", "Taillon", "Taillon LHB split is the cleanest Cubs-Pirates crossover", "Worst Pickz favorite with 3 HR, 5 near-HR and 11.1% barrels"), "good"),
            row("Oneil Cruz", "L", "+418", 88, "🚀 🌕 💣", ["vs Taillon"], n("Oneil Cruz", "Taillon", "Taillon RHB damage profile fits Cruz pull-air", "4 HR, 5 near-HR, 94.0 mph EV and 13.8% barrels"), "high"),
            row("Spencer Horwitz", "L", "+750", 76, "💎", ["vs Taillon"], n("Spencer Horwitz", "Taillon", "lefty lane versus Taillon's HR leakage", "4 HR, 6 near-HR with 6.9% barrels in the pitch-mix sample")),
            row("Alex Bregman", "R", "+730", 75, "💎 ⚾", ["vs Chandler"], n("Alex Bregman", "Chandler", "Chandler RHB split is the Cubs righty angle", "2 HR, 4 near-HR with 6.7% barrels versus Chandler")),
            row("Ian Happ", "S", "+550", 80, "🚀 💎 ⚾ 📜", ["vs Chandler"], n("Ian Happ", "Chandler", "Chandler LHB risk plus 2 career HR in BvP", "2 HR, 4 near-HR, 12.8% barrels versus Chandler"), "good"),
        ],
    },
    {
        "title": "LAA @ DET - Jose Soriano (R, LAA) vs Casey Mize (R, DET)",
        "description": "Comerica Park — -1% combined runs row with 71°F air and 9 mph L-R wind. Casey Mize's RHB split is the clearer HR lane despite Detroit's large outfield.",
        "rows": [
            row("Zach Neto", "R", "+440", 87, "🚀 🌕 💣", ["vs Mize"], n("Zach Neto", "Mize", "Mize RHB HR risk fits Neto's pull-side power", "7 HR, 9 near-HR, 90.8 mph EV and 15.1% barrels"), "high"),
            row("Jo Adell", "R", "+475", 78, "🚀 💎", ["vs Mize"], n("Jo Adell", "Mize", "righty damage versus Mize's weaker split", "2 HR, 2 near-HR with 39.2% hard-hit"), "good"),
            row("Riley Greene", "L", "+640", 76, "🚀 💎", ["vs Soriano"], n("Riley Greene", "Soriano", "Soriano suppresses but Greene's form is steady", "1 HR, 4 near-HR with 8.5% barrels")),
            row("Vaughn Grissom", "R", "+880", 72, "💎", ["vs Mize"], n("Vaughn Grissom", "Mize", "Mize RHB lane with 54.5% hard-hit", "2 HR, 2 near-HR with 91.8 mph EV")),
        ],
    },
    {
        "title": "ATL @ BOS - Bryce Elder (R, ATL) vs Connelly Early 🧤 (L, BOS)",
        "description": "Fenway Park — +1% HR row with +19% runs, 84°F air, 11 mph L-R wind and high receptivity. Connelly Early's LHB split plus Fenway's unique shape keeps power bats live.",
        "rows": [
            row("Jarren Duran", "L", "+600", 93, "🚀 ⭐ 🌕 💣 🏟️", ["vs Elder"], n("Jarren Duran", "Elder", "Fenway carry plus Elder RHB leakage", "Worst Pickz favorite with 6 HR, 6 near-HR and 11.3% barrels"), "high"),
            row("Willson Contreras", "R", "+426", 85, "🚀 ⭐ 💎 📜 🏟️", ["vs Elder"], n("Willson Contreras", "Elder", "6 HR in BvP sample versus Elder", "Worst Pickz favorite with 6 HR, 6 near-HR and 17.3% barrels"), "good"),
            row("Ceddanne Rafaela", "R", "+850", 70, "💎 🏟️", ["vs Elder"], n("Ceddanne Rafaela", "Elder", "Fenway doubles environment supports extra-base upside", "2 HR, 2 near-HR with 6.4% barrels")),
            row("Matt Olson", "L", "+500", 84, "🚀 🌕 💎 ⚾ 🕊️ 🧤", ["vs Early"], n("Matt Olson", "Early", "Early LHB HR risk is the Braves lefty lane", "4 HR, 7 near-HR with 13.6% barrels versus Early"), "high"),
            row("Michael Harris II", "L", "+600", 72, "💎", ["vs Early"], n("Michael Harris II", "Early", "lefty split versus Early's LHB weakness", "0 HR but 41.4% hard-hit in the pitch-mix window")),
        ],
    },
    {
        "title": "CIN @ NYM - Andrew Abbott (L, CIN) vs Jonah Tong 🧤 (R, NYM)",
        "description": "Citi Field — -6% HR row with 84°F air and 9 mph out-blowing wind. Jonah Tong's limited sample still shows RHB HR leakage for Cincinnati bats.",
        "rows": [
            row("Elly De La Cruz", "S", "+650", 90, "🚀 ⭐ 🌕 💣", ["vs Tong"], n("Elly De La Cruz", "Tong", "Tong RHB split plus switch pull-air", "Worst Pickz favorite with 3 HR, 5 near-HR and 15.8% barrels"), "high"),
            row("Bo Bichette", "R", "+750", 74, "💎", ["vs Abbott"], n("Bo Bichette", "Abbott", "Abbott suppresses but Bichette's contact is usable", "2 HR, 2 near-HR with 88.5 mph EV")),
            row("Nathaniel Lowe", "L", "+690", 76, "🚀 💎 ⚾ 🕊️ 🧤", ["vs Tong"], n("Nathaniel Lowe", "Tong", "lefty lane versus Tong's RHB weakness", "2 HR, 5 near-HR with 11.9% barrels"), "good"),
            row("Matt McLain", "R", "+900", 72, "🚀 💎", ["vs Tong"], n("Matt McLain", "Tong", "2 HR in the pitch-mix window versus Tong", "2 HR, 2 near-HR with 12.5% barrels")),
            row("Will Benson", "L", "N/A", 68, "💎", ["vs Tong"], n("Will Benson", "Tong", "2 HR in sample but no listed odds posted", "2 HR, 2 near-HR with 20.0% barrels versus Tong")),
        ],
    },
    {
        "title": "NYY @ KC - Gerrit Cole (R, NYY) vs Noah Cameron (L, KC)",
        "description": "Kauffman Stadium — +9% HR row with mild 82°F air and an X-Large outfield. Noah Cameron is attackable; Yankees lefty bats face the cleaner Royals SP split.",
        "rows": [
            row("Paul Goldschmidt", "R", "+590", 91, "🚀 ⭐ 🌕 💣", ["vs Cameron"], n("Paul Goldschmidt", "Cameron", "Cameron LHB split fits Goldschmidt's hot window", "Worst Pickz favorite with 3 HR, 3 near-HR and 24.0% barrels"), "high"),
            row("Trent Grisham", "L", "+450", 82, "🚀 💎", ["vs Cameron"], n("Trent Grisham", "Cameron", "lefty lane versus Cameron at Kauffman", "2 HR, 2 near-HR with 20.0% barrels"), "good"),
            row("Jac Caglianone", "L", "+700", 88, "🚀 ⭐ 🌕 💣", ["vs Cole"], n("Jac Caglianone", "Cole", "Cole splits unavailable; form drives the Royals lefty", "Worst Pickz favorite with 3 HR, 4 near-HR and 22.0% barrels"), "high"),
            row("Salvador Perez", "R", "+510", 79, "🚀 ⭐ 💎", ["vs Cole"], n("Salvador Perez", "Cole", "Cole suppresses but Perez's power tier keeps him live", "Worst Pickz favorite with 4 HR, 5 near-HR and 13.2% barrels"), "good"),
            row("Bobby Witt Jr.", "R", "+475", 86, "🚀 💎 🏟️", ["vs Cole"], n("Bobby Witt Jr.", "Cole", "Kauffman +9% carry helps Witt's pull-side damage", "2 HR, 4 near-HR with 96.2 mph EV and 11.0% barrels"), "good"),
            row("Carter Jensen", "L", "+675", 80, "🚀 💎", ["vs Cole"], n("Carter Jensen", "Cole", "lefty contact quality in a plus park row", "3 HR, 4 near-HR with 7.3% barrels versus Cole")),
            row("Anthony Volpe", "R", "+700", 84, "🚀 🌕", ["vs Cameron"], n("Anthony Volpe", "Cameron", "Cameron RHB split is the Yankee shortstop lane", "1 HR, 1 near-HR with 33.3% barrels in a loud small sample"), "high"),
        ],
    },
    {
        "title": "MIN @ CWS - Connor Prielipp (L, MIN) vs Davis Martin (R, CWS)",
        "description": "Rate Field — +1% combined row with cool 66°F air and 11 mph L-R wind. Connor Prielipp gives Chicago bats a form-driven lane on a chilly night at Rate.",
        "rows": [
            row("Miguel Vargas", "R", "+510", 90, "🚀 ⭐ 🌕 💣", ["vs Prielipp"], n("Miguel Vargas", "Prielipp", "Prielipp RHB split fits Vargas' elite power window", "Worst Pickz favorite with 5 HR, 5 near-HR and .829 SLG"), "high"),
            row("Munetaka Murakami", "L", "+410", 87, "🚀 🌕 💣", ["vs Prielipp"], n("Munetaka Murakami", "Prielipp", "lefty pull-air versus Prielipp's LHB sample", "4 HR, 5 near-HR with 27.8% barrels"), "high"),
            row("Colson Montgomery", "L", "+510", 83, "🚀 ⭐ 💎", ["vs Prielipp"], n("Colson Montgomery", "Prielipp", "Prielipp LHB leakage supports Montgomery lift", "Worst Pickz favorite with 3 HR, 3 near-HR and 8.7% barrels"), "good"),
            row("Byron Buxton", "R", "+310", 88, "🚀 🌕 💣", ["vs Martin"], n("Byron Buxton", "Martin", "Martin RHB split plus Buxton's slate-best power tier", "9 HR, 12 near-HR with 18.3% barrels"), "high"),
        ],
    },
    {
        "title": "HOU @ TEX - Mike Burrows 🧤 (R, HOU) vs Jacob deGrom 🧤 (R, TEX)",
        "description": "Globe Life Field — -7% HR row with roof closed and 79°F air. Jacob deGrom and Mike Burrows both carry HR risk; Houston's top bats are the clearest attack targets.",
        "rows": [
            row("Yordan Alvarez", "L", "+310", 94, "🚀 ⭐ 🌕 💣 ⚾ 🕊️ 🧤 📜", ["vs deGrom"], n("Yordan Alvarez", "deGrom", "deGrom LHB risk plus BvP HR history", "Worst Pickz favorite with 7 HR, 12 near-HR and 18.0% barrels"), "high"),
            row("Christian Walker", "R", "+390", 86, "🚀 ⭐ 💎 ⚾ 🕊️ 🧤", ["vs deGrom"], n("Christian Walker", "deGrom", "deGrom RHB damage profile fits Walker pull-air", "Worst Pickz favorite with 8 HR, 8 near-HR and 14.3% barrels"), "good"),
            row("Brandon Nimmo", "L", "+490", 80, "🚀 💎 ⚾ 🕊️ 🧤", ["vs Burrows"], n("Brandon Nimmo", "Burrows", "Burrows LHB HR risk at the dome", "5 HR, 9 near-HR with 11.7% barrels versus Burrows"), "good"),
            row("Kyle Higashioka", "R", "N/A", 65, "💎", ["vs Burrows"], n("Kyle Higashioka", "Burrows", "Burrows RHB split but no listed odds posted", "2 HR, 4 near-HR with 14.3% barrels in the sample")),
            row("Zach Dezenzo", "R", "N/A", 70, "💎", ["vs Burrows"], n("Zach Dezenzo", "Burrows", "Burrows RHB lane with 97.5 mph EV peak", "0 HR, 1 near-HR with 60.0% hard-hit; no listed odds")),
        ],
    },
    {
        "title": "COL @ LAD - Tomoyuki Sugano 🧤 (R, COL) vs Shohei Ohtani (L, LAD)",
        "description": "Dodger Stadium — -6% HR row with cool 62°F marine air and 10 mph out-blowing wind. Tomoyuki Sugano's LHB split is the Dodger lefty angle despite park drag.",
        "rows": [
            row("Shohei Ohtani", "L", "+250", 92, "🚀 🌕 💣 ⚾ 🕊️ 🧤", ["vs Sugano"], n("Shohei Ohtani", "Sugano", "Sugano LHB HR risk is the cleanest Dodger lane", "4 HR, 8 near-HR with 95.9 mph EV and 19.0% barrels"), "high"),
            row("Freddie Freeman", "L", "+410", 86, "🚀 🌕 💎 ⚾ 🕊️ 🧤", ["vs Sugano"], n("Freddie Freeman", "Sugano", "lefty damage versus Sugano's LHB weakness", "4 HR, 9 near-HR with 14.7% barrels"), "high"),
            row("Will Smith", "R", "+418", 82, "🚀 💎", ["vs Sugano"], n("Will Smith", "Sugano", "Sugano RHB split keeps Smith's form relevant", "4 HR, 11 near-HR with 16.7% barrels"), "good"),
            row("TJ Rumfield", "L", "+850", 74, "💎", ["vs Ohtani"], n("TJ Rumfield", "Ohtani", "Ohtani suppresses but Rumfield's 4 HR form keeps him in play", "4 HR, 6 near-HR with 10.2% barrels in Dodger drag")),
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
