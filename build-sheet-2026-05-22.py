#!/usr/bin/env python3
"""Generate games[] block for 2026-05-22 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Kyle Schwarber (L)",
    "Rhys Hoskins (R)",
    "Elly De La Cruz (S)",
    "Ben Rice (L)",
    "Yandy Diaz (R)",
    "Brandon Lowe (L)",
    "Owen Caissie (L)",
    "Juan Soto (L)",
    "Byron Buxton (R)",
    "Pete Alonso (R)",
    "Mike Yastrzemski (L)",
    "Jose Tena (L)",
    "Jacob Young (R)",
    "Josh Jung (R)",
    "Nick Kurtz (L)",
    "Corbin Carroll (L)",
    "Colson Montgomery (L)",
}

PLAYER_TEAMS = {
    "Ian Happ (S)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Michael Busch (L)": "CHC",
    "Yordan Alvarez (L)": "HOU",
    "Isaac Paredes (R)": "HOU",
    "Christian Walker (R)": "HOU",
    "Kyle Schwarber (L)": "PHI",
    "Rhys Hoskins (R)": "CLE",
    "Jose Ramirez (S)": "CLE",
    "Travis Bazzana (L)": "CLE",
    "Will Benson (L)": "CIN",
    "Elly De La Cruz (S)": "CIN",
    "Spencer Steer (R)": "CIN",
    "Alec Burleson (L)": "STL",
    "JJ Wetherholt (L)": "STL",
    "Ben Rice (L)": "NYY",
    "Yandy Diaz (R)": "TB",
    "Jonathan Aranda (L)": "TB",
    "Junior Caminero (R)": "TB",
    "Daulton Varsho (L)": "TOR",
    "Kazuma Okamoto (R)": "TOR",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Brandon Lowe (L)": "PIT",
    "Marcell Ozuna (R)": "PIT",
    "Oneil Cruz (L)": "PIT",
    "Owen Caissie (L)": "MIA",
    "Jakob Marsee (L)": "MIA",
    "Kyle Stowers (L)": "MIA",
    "Juan Soto (L)": "NYM",
    "Brett Baty (L)": "NYM",
    "A.J. Ewing (L)": "NYM",
    "Mark Vientos (R)": "NYM",
    "Jarren Duran (L)": "BOS",
    "Byron Buxton (R)": "MIN",
    "James Outman (L)": "MIN",
    "Pete Alonso (R)": "BAL",
    "Taylor Ward (R)": "BAL",
    "Samuel Basallo (L)": "BAL",
    "Riley Greene (L)": "DET",
    "Dillon Dingler (R)": "DET",
    "Spencer Torkelson (R)": "DET",
    "Michael Harris II (L)": "ATL",
    "Austin Riley (R)": "ATL",
    "Mike Yastrzemski (L)": "ATL",
    "James Wood (L)": "WSH",
    "Jose Tena (L)": "WSH",
    "Jacob Young (R)": "WSH",
    "Jackson Chourio (R)": "MIL",
    "Max Muncy (L)": "LAD",
    "Shohei Ohtani (L)": "LAD",
    "Mookie Betts (R)": "LAD",
    "Jac Caglianone (L)": "KC",
    "Bobby Witt Jr. (R)": "KC",
    "Julio Rodriguez (R)": "SEA",
    "Randy Arozarena (R)": "SEA",
    "Vaughn Grissom (R)": "LAA",
    "Josh Lowe (L)": "LAA",
    "Jo Adell (R)": "LAA",
    "Ezequiel Duran (R)": "TEX",
    "Josh Jung (R)": "TEX",
    "Justin Foscue (R)": "TEX",
    "Fernando Tatis Jr. (R)": "SD",
    "Gavin Sheets (L)": "SD",
    "Shea Langeliers (R)": "ATH",
    "Nick Kurtz (L)": "ATH",
    "Corbin Carroll (L)": "ARI",
    "Mickey Moniak (L)": "COL",
    "Willy Adames (R)": "SF",
    "Rafael Devers (L)": "SF",
    "Casey Schmitt (R)": "SF",
    "Colson Montgomery (L)": "CWS",
    "Munetaka Murakami (L)": "CWS",
    "Miguel Vargas (R)": "CWS",
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
    "Taillon",
    "Williams",
    "Leahy",
    "Martinez",
    "Chandler",
    "Myers",
    "Perez",
    "Flaherty",
    "Bassitt",
    "Mikolas",
    "Henderson",
    "Gilbert",
    "Cameron",
    "deGrom",
    "Springs",
    "Sugano",
    "Martin",
    "McDonald",
    "Wrobleski",
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
    entry["emojis"] = em


games = [
    {
        "title": "HOU @ CHC - Spencer Arrighetti (R, HOU) vs Jameson Taillon 🧤 (R, CHC)",
        "description": "Wrigley Field — Ballpark Pal grades -16% HR with cool 55°F air, 16 mph wind and extreme wind receptivity. Jameson Taillon is the slate's top HR-risk arm; Houston lefties get the cleaner attack lane despite the park drag.",
        "rows": [
            row("Ian Happ", "S", "+850", 74, "💎", ["vs Arrighetti"], n("Ian Happ", "Arrighetti", "Wrigley wind is the main obstacle", "0 HR but 90.3 mph EV and 25.0% hard-hit in the pitch-mix sample")),
            row("Michael Conforto", "L", "+800", 78, "🚀 💎", ["vs Arrighetti"], n("Michael Conforto", "Arrighetti", "lefty lane is the Cubs path", "0 HR, 1 near-HR, 94.1 mph EV and 40.0% pull-air")),
            row("Michael Busch", "L", "+830", 76, "💎", ["vs Arrighetti"], n("Michael Busch", "Arrighetti", "LHB split helps but park suppresses", "0 HR, 1 near-HR, 91.4 mph EV and 50.0% hard-hit")),
            row("Yordan Alvarez", "L", "+470", 88, "🚀 🌕 💣", ["vs Taillon"], n("Yordan Alvarez", "Taillon", "Taillon is the slate's loudest HR-risk starter", "2 HR, 3 near-HR, 98.2 mph EV and 11.8% barrels"), "high"),
            row("Isaac Paredes", "R", "+820", 80, "🚀 💎", ["vs Taillon"], n("Isaac Paredes", "Taillon", "Taillon's RHB split is still attackable", "2 HR, 2 near-HR, 83.4 mph EV and 42.9% pull-air"), "good"),
            row("Christian Walker", "R", "+710", 82, "🚀 💎", ["vs Taillon"], n("Christian Walker", "Taillon", "righty power fits Taillon's damage profile", "2 HR, 2 near-HR, 91.9 mph EV and 50.0% hard-hit"), "good"),
        ],
    },
    {
        "title": "CLE @ PHI - Gavin Williams 🧤 (R, CLE) vs Cristopher Sanchez (L, PHI)",
        "description": "Citizens Bank Park — -14% HR model with overcast 59°F air and 29% rain risk. Cristopher Sanchez suppresses overall, but Kyle Schwarber's form is slate-best tier and Rhys Hoskins gets a loud RHB split read.",
        "rows": [
            row("Kyle Schwarber", "L", "+240", 96, "🚀 ⭐ 🌕 💣", ["vs Williams"], n("Kyle Schwarber", "Williams", "Williams is attackable to LHB contact quality", "Worst Pickz favorite with 5 HR, 5 near-HR, 96.7 mph EV and 36.8% barrels"), "high"),
            row("Rhys Hoskins", "R", "+650", 84, "🚀 ⭐ 💎", ["vs Sanchez"], n("Rhys Hoskins", "Sanchez", "Sanchez is strong but Hoskins' pull damage is loud", "Worst Pickz favorite with 0 HR, 1 near-HR, 99.3 mph EV and 80.0% hard-hit"), "good"),
            row("Jose Ramirez", "S", "+490", 86, "🚀 💎", ["vs Sanchez"], n("Jose Ramirez", "Sanchez", "switch bat gets a neutral Sanchez split", "1 HR, 1 near-HR, 97.6 mph EV and 66.7% hard-hit"), "good"),
            row("Travis Bazzana", "L", "+1260", 79, "🚀 💎", ["vs Sanchez"], n("Travis Bazzana", "Sanchez", "lefty longshot with loud underlying contact", "1 HR, 2 near-HR, .778 SLG and 25.0% barrels")),
        ],
    },
    {
        "title": "STL @ CIN - Kyle Leahy 🧤 (R, STL) vs Chris Paddack (R, CIN)",
        "description": "Great American Ball Park — slate's #2 HR environment at +5% with 71°F air, though 92% rain risk is real. Leahy is weaker to RHB; Paddack gives up quality Cardinals lefty contact in a small park.",
        "rows": [
            row("Will Benson", "L", "+461", 81, "🚀 💎 🏟️", ["vs Leahy"], n("Will Benson", "Leahy", "GABP heat helps lefty lift", "0 HR but 96.3 mph EV, 45.5% barrels and 54.5% hard-hit")),
            row("Elly De La Cruz", "S", "+448", 90, "🚀 ⭐ 🌕 💣 🏟️", ["vs Leahy"], n("Elly De La Cruz", "Leahy", "Leahy's RHB split plus GABP is premium", "Worst Pickz favorite with 1 HR, 2 near-HR, 93.9 mph EV and 52.4% hard-hit"), "high"),
            row("Spencer Steer", "R", "+561", 78, "💎 🏟️", ["vs Leahy"], n("Spencer Steer", "Leahy", "righty split is the cleaner Reds lane", "1 HR, 1 near-HR, 89.6 mph EV and 34.6% pull-air")),
            row("Alec Burleson", "L", "+367", 83, "🚀 💎 🏟️", ["vs Paddack"], n("Alec Burleson", "Paddack", "Paddack's LHB split is the Cardinals angle", "1 HR, 3 near-HR, 89.4 mph EV and 44.0% hard-hit"), "good"),
            row("JJ Wetherholt", "L", "+500", 80, "🚀 💎 🏟️", ["vs Paddack"], n("JJ Wetherholt", "Paddack", "lefty contact quality fits Paddack", "2 HR, 2 near-HR, 89.7 mph EV and 36.4% hard-hit"), "good"),
        ],
    },
    {
        "title": "TB @ NYY - Nick Martinez 🧤 (R, TB) vs Gerrit Cole (R, NYY)",
        "description": "Yankee Stadium — -30% HR model (slate's harshest short-porch drag) with cool air and wind in. Nick Martinez is weaker to LHB; Cole has no 2026 splits in the feed, so Rays bats lean on form and BvP.",
        "rows": [
            row("Ben Rice", "L", "+260", 94, "🚀 ⭐ 🌕 💣", ["vs Martinez"], n("Ben Rice", "Martinez", "Martinez LHB lane plus short porch", "Worst Pickz favorite with 4 HR, 4 near-HR, 94.0 mph EV and 25.0% barrels"), "high"),
            row("Yandy Diaz", "R", "+720", 86, "🚀 ⭐ 💎 📜", ["vs Martinez"], n("Yandy Diaz", "Martinez", "Martinez RHB split is attackable with BvP help", "Worst Pickz favorite with 3 HR, 4 near-HR, 18.5% barrels and career HR history"), "good"),
            row("Jonathan Aranda", "L", "+550", 82, "🚀 💎", ["vs Martinez"], n("Jonathan Aranda", "Martinez", "lefty lane is the Rays path versus Martinez", "1 HR, 4 near-HR, 90.0 mph EV and 50.0% hard-hit"), "good"),
            row("Junior Caminero", "R", "+310", 88, "🚀 🌕 💣", ["vs Cole"], n("Junior Caminero", "Cole", "Cole splits unavailable; form drives the play", "2 HR, 5 near-HR, 92.5 mph EV and 19.2% barrels"), "high"),
        ],
    },
    {
        "title": "PIT @ TOR - Bubba Chandler 🧤 (R, PIT) vs Kevin Gausman (R, TOR)",
        "description": "Rogers Centre — roof closed, +2% HR model. Bubba Chandler is a top-10 HR-risk arm; Kevin Gausman is tougher but Brandon Lowe's form is loud enough to keep Pittsburgh bats live.",
        "rows": [
            row("Vladimir Guerrero Jr.", "R", "+472", 74, "💎", ["vs Chandler"], n("Vladimir Guerrero Jr.", "Chandler", "Chandler RHB risk helps but form is lighter", "1 HR, 1 near-HR, 84.0 mph EV and 30.8% hard-hit")),
            row("Daulton Varsho", "L", "+500", 80, "🚀 💎", ["vs Chandler"], n("Daulton Varsho", "Chandler", "Chandler's LHB split is the Toronto lane", "1 HR, 1 near-HR, 94.0 mph EV and 62.5% hard-hit"), "good"),
            row("Kazuma Okamoto", "R", "+388", 68, "💎", ["vs Chandler"], n("Kazuma Okamoto", "Chandler", "righty split fits Chandler's weak side", "0 HR, 89.2 mph EV and 40.0% hard-hit in a thin sample")),
            row("Brandon Lowe", "L", "+470", 93, "🚀 ⭐ 🌕 💣", ["vs Gausman"], n("Brandon Lowe", "Gausman", "Gausman is steady but Lowe's power is slate-best tier", "Worst Pickz favorite with 2 HR, 3 near-HR, 103.5 mph EV and 42.9% barrels"), "high"),
            row("Marcell Ozuna", "R", "+522", 79, "💎", ["vs Gausman"], n("Marcell Ozuna", "Gausman", "righty split is neutral versus Gausman", "1 HR, 1 near-HR, 91.2 mph EV and 30.0% hard-hit")),
            row("Oneil Cruz", "L", "+422", 91, "🚀 🌕 💣", ["vs Gausman"], n("Oneil Cruz", "Gausman", "lefty power lane with elite EV", "1 HR, 1 near-HR, 96.3 mph EV and 70.0% hard-hit"), "high"),
        ],
    },
    {
        "title": "NYM @ MIA - Tobias Myers 🧤 (R, NYM) vs Eury Perez 🧤 (R, MIA)",
        "description": "loanDepot park — roof closed, -13% HR. Tobias Myers is weaker to RHB; Eury Perez owns the slate's best RHB HR-risk split, making Juan Soto and the Mets lefties the premium attack lane.",
        "rows": [
            row("Owen Caissie", "L", "+800", 87, "🚀 ⭐ 🌕 💎", ["vs Myers"], n("Owen Caissie", "Myers", "Myers RHB risk helps Miami lefties", "Worst Pickz favorite with 2 HR, 2 near-HR, 97.8 mph EV and 50.0% barrels"), "good"),
            row("Jakob Marsee", "L", "+1040", 76, "💎", ["vs Myers"], n("Jakob Marsee", "Myers", "lefty lane versus Myers' RHB split", "1 HR, 1 near-HR, 79.4 mph EV and 30.0% hard-hit")),
            row("Kyle Stowers", "L", "+475", 82, "🚀 💎", ["vs Myers"], n("Kyle Stowers", "Myers", "lefty contact quality fits Myers", "0 HR, 1 near-HR, 92.9 mph EV and 41.7% barrels")),
            row("Juan Soto", "L", "+333", 95, "🚀 ⭐ 🌕 💣", ["vs Perez"], n("Juan Soto", "Perez", "Perez RHB HR risk is the slate's clearest Mets lane", "Worst Pickz favorite with 4 HR, 5 near-HR, 97.6 mph EV and 27.8% barrels"), "high"),
            row("Brett Baty", "L", "+650", 74, "💎", ["vs Perez"], n("Brett Baty", "Perez", "lefty lane versus Perez's RHB weakness", "0 HR, 88.2 mph EV and 50.0% hard-hit")),
            row("A.J. Ewing", "L", "+860", 81, "🚀 💎", ["vs Perez"], n("A.J. Ewing", "Perez", "Perez RHB split supports lefty lift", "1 HR, 1 near-HR, 87.0 mph EV and 38.5% hard-hit")),
            row("Mark Vientos", "R", "+593", 77, "💎", ["vs Perez"], n("Mark Vientos", "Perez", "righty split is tougher but EV is strong", "0 HR, 2 near-HR, 92.0 mph EV and 53.8% hard-hit")),
        ],
    },
    {
        "title": "MIN @ BOS - Connor Prielipp (L, MIN) vs Payton Tolle (L, BOS)",
        "description": "Fenway Park — slate-worst HR environment at -36% with cool air and high pressure. Both lefty starters suppress; Byron Buxton is the one bat with enough barrel rate to stay listed.",
        "rows": [
            row("Jarren Duran", "L", "+675", 72, "💎", ["vs Tolle"], n("Jarren Duran", "Tolle", "Fenway drag is severe despite lefty lane", "0 HR, 98.8 mph EV and 60.0% hard-hit in a tiny sample")),
            row("Byron Buxton", "R", "+297", 89, "🚀 ⭐ 🌕", ["vs Tolle"], n("Byron Buxton", "Tolle", "best bat in the worst HR park on the slate", "Worst Pickz favorite with 0 HR, 1 near-HR, 92.7 mph EV and 42.9% barrels"), "good"),
            row("James Outman", "L", "+825", 70, "💎", ["vs Tolle"], n("James Outman", "Tolle", "Fenway -36% HR makes this a thin dart", "0 HR, 90.0 mph EV and 50.0% hard-hit in 3 PA")),
        ],
    },
    {
        "title": "DET @ BAL - Jack Flaherty 🧤 (R, DET) vs Chris Bassitt 🧤 (R, BAL)",
        "description": "Oriole Park — -27% HR with rain/overcast and wind in. Jack Flaherty is attackable; Chris Bassitt is the slate's #2 fade arm for RHB, but Pete Alonso's form keeps Baltimore bats listed.",
        "rows": [
            row("Pete Alonso", "R", "+440", 88, "🚀 ⭐ 🌕 💎 📜", ["vs Flaherty"], n("Pete Alonso", "Flaherty", "Flaherty RHB split plus BvP HR signal", "Worst Pickz favorite with 1 HR, 1 near-HR, 101.6 mph EV and career HR off Flaherty"), "good"),
            row("Taylor Ward", "R", "+690", 79, "💎", ["vs Flaherty"], n("Taylor Ward", "Flaherty", "righty lane versus Flaherty's damage profile", "1 HR, 1 near-HR, 88.6 mph EV and 28.6% hard-hit")),
            row("Samuel Basallo", "L", "+505", 80, "🚀 💎", ["vs Flaherty"], n("Samuel Basallo", "Flaherty", "lefty power fits Flaherty's LHB split", "0 HR, 90.6 mph EV and 36.4% hard-hit")),
            row("Riley Greene", "L", "+500", 85, "🚀 🌕 💎", ["vs Bassitt"], n("Riley Greene", "Bassitt", "Bassitt is a fade arm but Greene's form is loud", "0 HR, 1 near-HR, 99.9 mph EV and 83.3% hard-hit"), "good"),
            row("Dillon Dingler", "R", "+820", 76, "💎", ["vs Bassitt"], n("Dillon Dingler", "Bassitt", "Bassitt RHB fade helps Detroit righties", "1 HR, 1 near-HR, 85.9 mph EV and 42.9% hard-hit")),
            row("Spencer Torkelson", "R", "+810", 70, "💎", ["vs Bassitt"], n("Spencer Torkelson", "Bassitt", "Bassitt fade plus price, but HR form is light", "0 HR, 87.4 mph EV and 33.3% hard-hit")),
        ],
    },
    {
        "title": "WSH @ ATL - Miles Mikolas 🧤 (R, WSH) vs Bryce Elder (R, ATL)",
        "description": "Truist Park — -10% HR with 73% rain risk and warm 75°F air. Miles Mikolas is HR-risky to LHB; Bryce Elder suppresses but Atlanta's top bats have the loudest form on the board.",
        "rows": [
            row("Michael Harris II", "L", "+464", 90, "🚀 🌕 💣", ["vs Mikolas"], n("Michael Harris II", "Mikolas", "Mikolas LHB HR risk fits Harris' lefty power", "2 HR, 3 near-HR, 92.6 mph EV and 61.9% hard-hit"), "high"),
            row("Austin Riley", "R", "+350", 92, "🚀 🌕 💣 📜", ["vs Mikolas"], n("Austin Riley", "Mikolas", "Mikolas RHB split plus BvP extra-base history", "2 HR, 4 near-HR, 93.6 mph EV and 25.0% barrels"), "high"),
            row("Mike Yastrzemski", "L", "+353", 91, "🚀 ⭐ 🌕 💣 📜", ["vs Mikolas"], n("Mike Yastrzemski", "Mikolas", "Mikolas LHB lane plus BvP HR history", "Worst Pickz favorite with 3 HR, 4 near-HR, 92.3 mph EV and career HR off Mikolas"), "high"),
            row("James Wood", "L", "N/A", 84, "🚀 💎", ["vs Elder"], n("James Wood", "Elder", "Elder suppresses but Wood is the Nationals ceiling bat", "Submitted-card power bat versus Elder in a warm Truist setup")),
            row("Jose Tena", "L", "N/A", 72, "⭐ 💎", ["vs Elder"], n("Jose Tena", "Elder", "Worst Pickz favorite in a tough HR park", "Submitted-card inclusion versus Elder; power indicators are lighter")),
            row("Jacob Young", "R", "N/A", 68, "⭐ 💎", ["vs Elder"], n("Jacob Young", "Elder", "Worst Pickz favorite longshot versus Elder", "Submitted-card inclusion; Elder RHB split is closer to neutral")),
        ],
    },
    {
        "title": "LAD @ MIL - Justin Wrobleski 🧤 (L, LAD) vs Logan Henderson 🧤 (R, MIL)",
        "description": "American Family Field — roof closed, -4% HR. Justin Wrobleski is weaker to RHB; Logan Henderson has a small sample but LAD lefties have the slate's loudest power indicators.",
        "rows": [
            row("Max Muncy", "L", "+326", 94, "🚀 🌕 💣", ["vs Henderson"], n("Max Muncy", "Henderson", "Henderson LHB lane plus Muncy's elite form", "2 HR, 4 near-HR, 92.9 mph EV and 40.0% barrels"), "high"),
            row("Shohei Ohtani", "L", "+273", 90, "🚀 🌕 💣", ["vs Henderson"], n("Shohei Ohtani", "Henderson", "lefty power fits Henderson's LHB split", "1 HR, 1 near-HR, 89.7 mph EV and 23.1% barrels"), "high"),
            row("Mookie Betts", "R", "+600", 82, "🚀 💎", ["vs Henderson"], n("Mookie Betts", "Henderson", "righty split is the cleaner Dodgers lane", "1 HR, 1 near-HR, 93.5 mph EV and 50.0% hard-hit"), "good"),
            row("Jackson Chourio", "R", "+399", 78, "💎", ["vs Wrobleski"], n("Jackson Chourio", "Wrobleski", "Wrobleski RHB split helps Milwaukee", "0 HR, 104.9 mph EV and 100.0% hard-hit in a tiny sample")),
        ],
    },
    {
        "title": "SEA @ KC - Logan Gilbert 🧤 (R, SEA) vs Noah Cameron 🧤 (L, KC)",
        "description": "Kauffman Stadium — slate-best HR weather at +6% with mild 68°F air and the largest non-Coors outfield. Logan Gilbert is HR-risky; Noah Cameron is attackable to RHB in the best carry environment.",
        "rows": [
            row("Jac Caglianone", "L", "+525", 86, "🚀 💎 🏟️", ["vs Gilbert"], n("Jac Caglianone", "Gilbert", "Gilbert RHB risk plus Kauffman carry", "1 HR, 1 near-HR, 99.1 mph EV and 81.8% hard-hit"), "good"),
            row("Bobby Witt Jr.", "R", "+452", 84, "🚀 💎 🏟️ 📜", ["vs Gilbert"], n("Bobby Witt Jr.", "Gilbert", "Gilbert RHB split plus BvP HR history", "1 HR, 93.4 mph EV and career HR off Gilbert"), "good"),
            row("Julio Rodriguez", "R", "+410", 93, "🚀 🌕 💣 🏟️", ["vs Cameron"], n("Julio Rodriguez", "Cameron", "Kauffman +6% HR plus Cameron RHB lane", "3 HR, 3 near-HR, 90.4 mph EV and 23.1% barrels"), "high"),
            row("Randy Arozarena", "R", "+525", 80, "🚀 💎 🏟️", ["vs Cameron"], n("Randy Arozarena", "Cameron", "best weather game supports Seattle righties", "1 HR, 2 near-HR, 91.7 mph EV and 54.5% hard-hit"), "good"),
        ],
    },
    {
        "title": "TEX @ LAA - Jacob deGrom 🧤 (R, TEX) vs Grayson Rodriguez (R, LAA)",
        "description": "Angel Stadium — +4% HR with mild 68°F air and typical out-blowing carry. Jacob deGrom is HR-risky to LHB; Grayson Rodriguez has a tiny 2026 sample but Texas bats get the cleaner form read.",
        "rows": [
            row("Vaughn Grissom", "R", "+840", 76, "💎 🏟️", ["vs deGrom"], n("Vaughn Grissom", "deGrom", "deGrom LHB risk is the Angels angle", "1 HR, 1 near-HR, 91.5 mph EV and 66.7% hard-hit")),
            row("Josh Lowe", "L", "+730", 72, "💎 🏟️", ["vs deGrom"], n("Josh Lowe", "deGrom", "lefty lane versus deGrom's LHB split", "0 HR, 92.0 mph EV and 62.5% hard-hit")),
            row("Jo Adell", "R", "+470", 78, "💎 🏟️", ["vs deGrom"], n("Jo Adell", "deGrom", "Angel carry helps righty lift", "0 HR, 92.3 mph EV and 33.3% hard-hit")),
            row("Ezequiel Duran", "R", "+770", 83, "🚀 💎 🏟️", ["vs deGrom"], n("Ezequiel Duran", "deGrom", "deGrom RHB split is attackable", "1 HR, 2 near-HR, 90.6 mph EV and 37.5% barrels"), "good"),
            row("Josh Jung", "R", "+650", 85, "🚀 ⭐ 💎 🏟️", ["vs Rodriguez"], n("Josh Jung", "Rodriguez", "Rodriguez sample is tiny but Jung's form is loud", "Worst Pickz favorite with 0 HR, 2 near-HR, 94.1 mph EV and 50.0% hard-hit"), "good"),
            row("Justin Foscue", "R", "+710", 79, "💎 🏟️", ["vs Rodriguez"], n("Justin Foscue", "Rodriguez", "Angel weather plus Rodriguez uncertainty", "0 HR, 2 near-HR, 97.0 mph EV and 66.7% hard-hit")),
        ],
    },
    {
        "title": "ATH @ SD - Jeffrey Springs 🧤 (L, ATH) vs Walker Buehler (R, SD)",
        "description": "Petco Park — -4% HR with mild coastal air. Jeffrey Springs is weaker to RHB; Walker Buehler suppresses but Nick Kurtz and Shea Langeliers have the loudest A's power form.",
        "rows": [
            row("Fernando Tatis Jr.", "R", "+430", 76, "💎", ["vs Springs"], n("Fernando Tatis Jr.", "Springs", "Springs RHB split is the Padres lane", "0 HR, 96.9 mph EV and 75.0% hard-hit")),
            row("Gavin Sheets", "L", "+740", 70, "💎", ["vs Springs"], n("Gavin Sheets", "Springs", "lefty lane versus Springs in Petco", "0 HR in a tiny sample versus Springs")),
            row("Shea Langeliers", "R", "+376", 84, "🚀 💎", ["vs Buehler"], n("Shea Langeliers", "Buehler", "Buehler RHB split helps Oakland catchers", "1 HR, 1 near-HR, 89.3 mph EV and 15.0% barrels"), "good"),
            row("Nick Kurtz", "L", "+375", 92, "🚀 ⭐ 🌕 💣", ["vs Buehler"], n("Nick Kurtz", "Buehler", "Buehler LHB lane plus Kurtz's elite power", "Worst Pickz favorite with 2 HR, 3 near-HR, 99.0 mph EV and 33.3% barrels"), "high"),
        ],
    },
    {
        "title": "COL @ ARI - Tomoyuki Sugano 🧤 (R, COL) vs Michael Soroka (R, ARI)",
        "description": "Chase Field — roof closed, 92°F desert air but -10% HR model. Tomoyuki Sugano is HR-risky to LHB; Soroka suppresses but Carroll's form is slate-elite in the heat.",
        "rows": [
            row("Corbin Carroll", "L", "+375", 95, "🚀 ⭐ 🌕 💣", ["vs Sugano"], n("Corbin Carroll", "Sugano", "Sugano LHB HR risk in Chase heat", "Worst Pickz favorite with 3 HR, 4 near-HR, 98.9 mph EV and 50.0% barrels"), "high"),
            row("Mickey Moniak", "L", "+500", 78, "💎", ["vs Sugano"], n("Mickey Moniak", "Sugano", "lefty lane versus Sugano's LHB split", "0 HR, 90.8 mph EV and 57.1% pull-air")),
        ],
    },
    {
        "title": "CWS @ SF - Davis Martin 🧤 (R, CWS) vs Trevor McDonald 🧤 (R, SF)",
        "description": "Oracle Park — -26% HR with cool air and wind. Davis Martin is weaker to LHB; Trevor McDonald is a fade arm to RHB, giving Chicago lefties the cleaner attack path despite Oracle's drag.",
        "rows": [
            row("Willy Adames", "R", "+720", 86, "🚀 💎", ["vs McDonald"], n("Willy Adames", "McDonald", "McDonald RHB fade helps Giants righties", "2 HR, 3 near-HR, 97.3 mph EV and 22.2% barrels"), "good"),
            row("Rafael Devers", "L", "+570", 84, "🚀 💎", ["vs McDonald"], n("Rafael Devers", "McDonald", "McDonald LHB lane is the Giants path", "1 HR, 2 near-HR, 98.4 mph EV and 66.7% hard-hit"), "good"),
            row("Casey Schmitt", "R", "+775", 78, "💎", ["vs McDonald"], n("Casey Schmitt", "McDonald", "McDonald RHB fade supports Schmitt", "1 HR, 1 near-HR, 92.8 mph EV and 45.5% hard-hit")),
            row("Colson Montgomery", "L", "+525", 83, "🚀 ⭐ 💎", ["vs Martin"], n("Colson Montgomery", "Martin", "Martin LHB split fits Montgomery's lefty power", "Worst Pickz favorite with 1 HR, 1 near-HR, 90.9 mph EV and 50.0% hard-hit"), "good"),
            row("Munetaka Murakami", "L", "+420", 88, "🚀 🌕 💎", ["vs Martin"], n("Munetaka Murakami", "Martin", "Martin LHB HR risk is the White Sox lane", "1 HR, 1 near-HR, 98.3 mph EV and 28.6% barrels"), "good"),
            row("Miguel Vargas", "R", "+775", 87, "🚀 💎", ["vs Martin"], n("Miguel Vargas", "Martin", "Martin RHB split plus loud underlying contact", "1 HR, 3 near-HR, 97.8 mph EV and 62.5% hard-hit"), "good"),
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
