#!/usr/bin/env python3
"""Generate games[] block for 2026-05-20 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Kyle Schwarber (L)",
    "Jonathan Aranda (L)",
    "Coby Mayo (R)",
    "Yordan Alvarez (L)",
    "Corbin Carroll (L)",
    "Colson Montgomery (L)",
    "Angel Martinez (S)",
    "Ben Rice (L)",
    "Nolan Gorman (L)",
    "Brandon Lowe (L)",
    "Will Smith (R)",
}

PLAYER_TEAMS = {
    "Kyle Schwarber (L)": "PHI", "Alec Bohm (R)": "PHI", "Adolis Garcia (R)": "PHI",
    "Elly De La Cruz (S)": "CIN", "Will Benson (L)": "CIN",
    "Jonathan Aranda (L)": "TB", "Junior Caminero (R)": "TB", "Coby Mayo (R)": "BAL",
    "Byron Buxton (R)": "MIN", "Josh Bell (S)": "MIN", "Ryan Kreidler (R)": "MIN", "Yordan Alvarez (L)": "HOU",
    "Mickey Moniak (L)": "COL", "TJ Rumfield (L)": "COL", "Justin Foscue (R)": "TEX", "Brandon Nimmo (L)": "TEX",
    "Corbin Carroll (L)": "ARI", "Adrian Del Castillo (L)": "ARI", "Ryan Waldschmidt (R)": "ARI",
    "Willy Adames (R)": "SF", "Casey Schmitt (R)": "SF",
    "Luke Raley (L)": "SEA", "Randy Arozarena (R)": "SEA", "Colson Montgomery (L)": "CWS",
    "Munetaka Murakami (L)": "CWS", "Miguel Vargas (R)": "CWS", "Andrew Benintendi (L)": "CWS",
    "Connor Norby (R)": "MIA", "Javier Sanoja (R)": "MIA", "Xavier Edwards (S)": "MIA",
    "Matt Olson (L)": "ATL", "Austin Riley (R)": "ATL", "Mike Yastrzemski (L)": "ATL",
    "Gage Workman (L)": "DET", "Matt Vierling (R)": "DET", "Riley Greene (L)": "DET",
    "Angel Martinez (S)": "CLE", "Travis Bazzana (L)": "CLE",
    "CJ Abrams (L)": "WSH", "Curtis Mead (R)": "WSH", "Juan Soto (L)": "NYM", "A.J. Ewing (L)": "NYM",
    "Ben Rice (L)": "NYY", "Jazz Chisholm Jr. (L)": "NYY", "Aaron Judge (R)": "NYY", "Cody Bellinger (L)": "NYY", "Ryan McMahon (L)": "NYY",
    "Dalton Varsho (L)": "TOR", "Jesus Sanchez (L)": "TOR", "Kazuma Okamoto (R)": "TOR",
    "Carter Jensen (L)": "KC", "Bobby Witt Jr. (R)": "KC", "Jarren Duran (L)": "BOS", "Wilyer Abreu (L)": "BOS",
    "Carson Kelly (R)": "CHC", "Michael Conforto (L)": "CHC", "Brice Turang (L)": "MIL", "Jackson Chourio (R)": "MIL", "Jake Bauers (L)": "MIL", "William Contreras (R)": "MIL",
    "Alec Burleson (L)": "STL", "Nolan Gorman (L)": "STL", "Pedro Pages (R)": "STL", "Brandon Lowe (L)": "PIT", "Marcell Ozuna (R)": "PIT",
    "Miguel Andujar (R)": "SD", "Gavin Sheets (L)": "SD", "Ramon Laureano (R)": "SD", "Ty France (R)": "SD",
    "Max Muncy (L)": "LAD", "Freddie Freeman (L)": "LAD", "Will Smith (R)": "LAD",
    "Zach Neto (R)": "LAA", "Jo Adell (R)": "LAA", "Yoan Moncada (S)": "LAA", "Brent Rooker (R)": "ATH", "Nick Kurtz (L)": "ATH",
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


games = [
    {
        "title": "CIN @ PHI - Andrew Abbott (L, CIN) vs Aaron Nola 🧤 (R, PHI)",
        "description": "Citizens Bank Park — slate-best HR weather: +28% HR model, 90s heat, 13 mph wind and a 10.0 total. Nola is the bigger HR-risk arm; Phillies bats still get a major park/weather lift even with Abbott's steadier split.",
        "rows": [
            row("Kyle Schwarber", "L", "+180", 96, "🚀 🌕 💣 🏟️", ["vs Abbott"], n("Kyle Schwarber", "Abbott", "Citizens Bank heat/wind is the top HR environment", "Worst Pickz favorite with 2 HR, 2 near-HR, 101.6 mph EV and 50.0% barrels in the matchup sample"), "high"),
            row("Alec Bohm", "R", "+840", 82, "💎 🏟️", ["vs Abbott"], n("Alec Bohm", "Abbott", "same +28% HR park row", "Longer price with 2 HR, 2 near-HR and .778 ISO in the pitch-mix table")),
            row("Adolis Garcia", "R", "+460", 84, "🚀 💎 🏟️", ["vs Abbott"], n("Adolis Garcia", "Abbott", "wind/heat help his pull damage", "One HR with 95.4 mph EV and 71.4% hard-hit form"), "good"),
            row("Elly De La Cruz", "S", "+430", 87, "🚀 🌕 ⚾ 🏟️", ["vs Nola"], n("Elly De La Cruz", "Nola", "Nola is a top-five pitcher HR target on the slate", "Switch bat gets 1 HR, 2 near-HR, .536 wOBA and 96.5 mph EV"), "high"),
            row("Will Benson", "L", "+390", 80, "🚀 💎 ⚾ 🏟️", ["vs Nola"], n("Will Benson", "Nola", "Nola allows 1.93 HR/9 to LHB in the split", "Loud 95.0 mph EV and 25.0% barrels, though the PA sample is thin")),
        ],
    },
    {
        "title": "BAL @ TB - Shane Baz (R, BAL) vs Steven Matz (L, TB)",
        "description": "Tropicana Field — closed dome, weather neutral and HR model -2%. Baz is playable for Rays righty power; Baltimore props versus Matz are thinner because the scraped pitcher table had no selected starter stats.",
        "rows": [
            row("Jonathan Aranda", "L", "+525", 88, "🚀 🌕 💣", ["vs Baz"], n("Jonathan Aranda", "Baz", "dome removes weather but the bat form is loud", "Worst Pickz favorite with 98.3 mph EV, 25.0% barrels, 87.5% hard-hit and 1 HR/2 near-HR"), "high"),
            row("Junior Caminero", "R", "+360", 90, "🚀 🌕 💣", ["vs Baz"], n("Junior Caminero", "Baz", "Baz is weaker to RHB HR damage", "2 HR, 2 near-HR, 102.6 mph EV and 28.6% barrels"), "high"),
            row("Coby Mayo", "R", "N/A", 72, "⭐ 💎", ["vs Matz"], n("Coby Mayo", "Matz", "closed dome keeps this as a longshot", "Worst Pickz favorite from the submitted card; projected Baltimore power bat versus the lefty starter")),
        ],
    },
    {
        "title": "HOU @ MIN - Mike Burrows 🧤 (R, HOU) vs Joe Ryan (R, MIN)",
        "description": "Target Field — harsh HR weather (-33% HR model, cool air), but Burrows is vulnerable to lefty lift and Joe Ryan has a scary Yordan history despite excellent season run prevention.",
        "rows": [
            row("Byron Buxton", "R", "+340", 86, "🚀 🌕", ["vs Burrows"], n("Byron Buxton", "Burrows", "Target Field suppresses carry", "3 HR, 5 near-HR and 26.1% barrels keep the ceiling intact"), "good"),
            row("Josh Bell", "S", "+580", 81, "🚀 💎", ["vs Burrows"], n("Josh Bell", "Burrows", "cool weather caps the score", "2 HR with .269 ISO and 56.2% hard-hit in the matchup sample")),
            row("Ryan Kreidler", "R", "N/A", 70, "💎", ["vs Burrows"], n("Ryan Kreidler", "Burrows", "small sample plus bad weather", "1 HR in 7 PA, but limited volume makes him a thin dart")),
            row("Yordan Alvarez", "L", "+392", 93, "🚀 🌕 💣 📜", ["vs Joe Ryan"], n("Yordan Alvarez", "Joe Ryan", "Target is cold, but the BvP is elite", "Worst Pickz favorite with 2 HR in the pitch-mix sample and 3 career HR off Ryan in the BvP table"), "high"),
        ],
    },
    {
        "title": "TEX @ COL - Jack Leiter 🧤 (R, TEX) vs Kyle Freeland 🧤 (L, COL)",
        "description": "Coors Field — elite run environment, +4% HR and huge run/extra-base lift, but rain risk and cooler temps keep it from being automatic. Both starters are attackable enough to list bats from both sides.",
        "rows": [
            row("Mickey Moniak", "L", "+440", 82, "🚀 💎 🏟️", ["vs Leiter"], n("Mickey Moniak", "Leiter", "Coors altitude boosts any lifted ball", "50.0% pull-air with 89.6 mph EV, but recent results are cold")),
            row("TJ Rumfield", "L", "+820", 81, "💎 🏟️", ["vs Leiter"], n("TJ Rumfield", "Leiter", "Coors gives the longshot life", "1 HR, 3 near-HR and 20.0% barrels")),
            row("Justin Foscue", "R", "+710", 78, "💎 🏟️", ["vs Freeland"], n("Justin Foscue", "Freeland", "Freeland's RHB risk and Coors carry line up", "Micro sample, but 92.4 mph EV and .500 ISO keep him on the sheet")),
            row("Brandon Nimmo", "L", "+550", 76, "💎 🏟️", ["vs Freeland"], n("Brandon Nimmo", "Freeland", "Coors helps, but his selected-pitch power sample is lighter", "91.5 mph EV and 50.0% hard-hit are the positive hooks")),
        ],
    },
    {
        "title": "SF @ ARI - Tyler Mahle (R, SF) vs Merrill Kelly 🧤 (R, ARI)",
        "description": "Chase Field — roof closed in the model feed, HR factor -8%, but Kelly is a top HR-risk arm overall and Arizona has several loud recent bat profiles.",
        "rows": [
            row("Corbin Carroll", "L", "+520", 95, "🚀 🌕 💣", ["vs Mahle"], n("Corbin Carroll", "Mahle", "roof mutes weather, bat form does the work", "Worst Pickz favorite with 3 HR, 4 near-HR, 98.7 mph EV and 57.1% barrels"), "high"),
            row("Adrian Del Castillo", "L", "+900", 73, "💎", ["vs Mahle"], n("Adrian Del Castillo", "Mahle", "longshot in a muted park row", "14.3% barrels and 57.1% fly balls give him catcher-pop appeal")),
            row("Ryan Waldschmidt", "R", "+930", 74, "💎", ["vs Mahle"], n("Ryan Waldschmidt", "Mahle", "righty price is large enough to note", "40.0% pull-air and solid contact despite modest EV")),
            row("Willy Adames", "R", "+500", 86, "🚀 🌕 ⚾ 📜", ["vs Kelly"], n("Willy Adames", "Kelly", "Kelly is top-four on the slate by HR-risk", "2 HR, 3 near-HR and 95.2 mph EV, plus 2 HR BvP history"), "good"),
            row("Casey Schmitt", "R", "+396", 78, "🚀 💎", ["vs Kelly"], n("Casey Schmitt", "Kelly", "righty lane is not Kelly's worst side, but the form is stable", "93.7 mph EV with 54.5% hard-hit")),
        ],
    },
    {
        "title": "CWS @ SEA - Sean Burke (R, CWS) vs Emerson Hancock 🧤 (R, SEA)",
        "description": "T-Mobile Park — roof/controlled environment and -7% HR model. Hancock's LHB HR-risk is the main attack point, while Seattle power has to beat a pitcher-friendly building.",
        "rows": [
            row("Luke Raley", "L", "+410", 88, "🚀 🌕 💣 📜", ["vs Burke"], n("Luke Raley", "Burke", "park is tough but the swing data is absurd", "3 HR, 3 near-HR, 101.5 mph EV, 57.1% barrels and BvP HR signal"), "high"),
            row("Randy Arozarena", "R", "+710", 78, "🚀 💎", ["vs Burke"], n("Randy Arozarena", "Burke", "T-Mobile lowers carry", "1 HR with 91.3 mph EV and 60.0% hard-hit")),
            row("Colson Montgomery", "L", "+440", 90, "🚀 🌕 💣 ⚾", ["vs Hancock"], n("Colson Montgomery", "Hancock", "Hancock owns a clear LHB HR-risk lane", "Worst Pickz favorite with 3 HR, 4 near-HR and 23.1% barrels"), "high"),
            row("Munetaka Murakami", "L", "+360", 84, "🚀 🌕 ⚾ 📜", ["vs Hancock"], n("Munetaka Murakami", "Hancock", "Hancock is top-five on the slate by HR-risk", "1 HR in current form plus BvP HR in a tiny sample"), "good"),
            row("Miguel Vargas", "R", "+500", 82, "🚀 💎", ["vs Hancock"], n("Miguel Vargas", "Hancock", "righty split is less ideal than lefty lane", "2 HR, 3 near-HR and 23.5% barrels keep him live")),
            row("Andrew Benintendi", "L", "+810", 77, "💎 ⚾", ["vs Hancock"], n("Andrew Benintendi", "Hancock", "lefty split is the reason to include him", "1 HR with 14.3% barrels at a long price")),
        ],
    },
    {
        "title": "ATL @ MIA - Chris Sale (L, ATL) vs Janson Junk (R, MIA)",
        "description": "loanDepot park — roof, HR model -13%. This is a suppressive environment; Atlanta lefty power versus Junk is the preferred angle, while Miami bats face Sale's elite run prevention.",
        "rows": [
            row("Connor Norby", "R", "+980", 74, "💎", ["vs Sale"], n("Connor Norby", "Sale", "park and pitcher are both difficult", "1 HR and 28.6% barrels keep him as a pure longshot")),
            row("Javier Sanoja", "R", "N/A", 68, "💎", ["vs Sale"], n("Javier Sanoja", "Sale", "thin profile against a tough lefty", "1 HR in the sample but limited HR indicators overall")),
            row("Xavier Edwards", "S", "+1260", 72, "💎", ["vs Sale"], n("Xavier Edwards", "Sale", "roof park suppresses homers", "2 HR in a small sample at a massive number keeps him listed")),
            row("Matt Olson", "L", "+390", 84, "🚀 🌕", ["vs Junk"], n("Matt Olson", "Junk", "Junk is more vulnerable to LHB slug than the park suggests", "2 HR with .462 ISO and 96.9 mph EV"), "good"),
            row("Austin Riley", "R", "+470", 76, "💎", ["vs Junk"], n("Austin Riley", "Junk", "righty split is tougher", "2 near-HR and 14.3% barrels keep him playable")),
            row("Mike Yastrzemski", "L", "N/A", 78, "💎", ["vs Junk"], n("Mike Yastrzemski", "Junk", "lefty power lane is the draw", "2 HR and .353 ISO in the selected-pitch table")),
        ],
    },
    {
        "title": "CLE @ DET - Tanner Bibee (R, CLE) vs Drew Anderson (R, DET)",
        "description": "Comerica Park — harsh HR context: -32% HR model, cool temps and a large outfield. Detroit lefties get the better documented split versus Bibee; Cleveland props are more projection-based because Anderson had limited scraped matchup data.",
        "rows": [
            row("Gage Workman", "L", "+620", 75, "💎", ["vs Bibee"], n("Gage Workman", "Bibee", "Comerica is a major HR drag", "93.7 mph EV and 44.4% hard-hit are enough for a longshot look")),
            row("Matt Vierling", "R", "+930", 80, "💎 📜", ["vs Bibee"], n("Matt Vierling", "Bibee", "park is bad but BvP is excellent", "1 recent HR plus 2 career HR off Bibee in the BvP table")),
            row("Riley Greene", "L", "+500", 78, "💎", ["vs Bibee"], n("Riley Greene", "Bibee", "Bibee's LHB HR/FB lane is playable", "15.4% barrels but no recent HR in the selected sample")),
            row("Angel Martinez", "S", "N/A", 79, "⭐ 💎", ["vs Anderson"], n("Angel Martinez", "Anderson", "limited pitcher data makes this form/projection driven", "Worst Pickz favorite from the submitted card, projected switch-hit lift against the righty")),
            row("Travis Bazzana", "L", "N/A", 76, "💎", ["vs Anderson"], n("Travis Bazzana", "Anderson", "limited pitcher data and Comerica cap the score", "Lefty power profile stays on the board as a prop-card inclusion")),
        ],
    },
    {
        "title": "NYM @ WSH - Zach Thornton (L, NYM) vs Zack Littell 🧤 (R, WSH)",
        "description": "Nationals Park — warm/rainy with modest park support; Zack Littell is the No. 1 HR target pitcher on the slate with 2.98 HR/9 and massive LHB risk. Mets lefties are a priority lane.",
        "rows": [
            row("CJ Abrams", "L", "+620", 77, "💎", ["vs Thornton"], n("CJ Abrams", "Thornton", "Thornton has no 2026 splits in the scrape", "1 near-HR and 93.2 mph EV versus LHP pitch bucket")),
            row("Curtis Mead", "R", "+710", 76, "💎", ["vs Thornton"], n("Curtis Mead", "Thornton", "warm air helps but pitcher data is limited", ".449 wOBA and 42.9% hard-hit versus the LHP bucket")),
            row("Juan Soto", "L", "+290", 91, "🚀 🌕 ⚾ 📜", ["vs Littell"], n("Juan Soto", "Littell", "Littell allows extreme LHB damage", "1 HR in the pitch table plus a career HR off Littell"), "high"),
            row("A.J. Ewing", "L", "+800", 84, "🚀 💎 ⚾", ["vs Littell"], n("A.J. Ewing", "Littell", "Littell's LHB split is the slate's loudest weak spot", "1 HR, .375 ISO, 97.0 mph EV and 33.3% barrels"), "good"),
        ],
    },
    {
        "title": "TOR @ NYY - Trey Yesavage (R, TOR) vs Cam Schlittler (R, NYY)",
        "description": "Yankee Stadium — +9% HR with strong wind and rain risk. Both starters grade as HR suppressors, so this is more park/price/batter-talent than pitcher hunting.",
        "rows": [
            row("Ben Rice", "L", "+314", 90, "🚀 🌕 💣 🏟️", ["vs Yesavage"], n("Ben Rice", "Yesavage", "Yankee short porch helps lefty pull lift", "Worst Pickz favorite with 2 HR and 50.0% barrels in the sample"), "high"),
            row("Jazz Chisholm Jr.", "L", "+423", 73, "💎 🏟️", ["vs Yesavage"], n("Jazz Chisholm Jr.", "Yesavage", "park helps but pitcher profile is difficult", "66.7% pull-air in a tiny sample keeps him listed")),
            row("Aaron Judge", "R", "+280", 85, "🚀 🌕 🏟️", ["vs Yesavage"], n("Aaron Judge", "Yesavage", "raw power plus Yankee Stadium always matters", "37.5% barrels but Yesavage has allowed no HR in the 2026 summary"), "good"),
            row("Cody Bellinger", "L", "+451", 81, "💎 🏟️", ["vs Yesavage"], n("Cody Bellinger", "Yesavage", "lefty porch boosts his path", "1 HR with .375 ISO and strong walk profile")),
            row("Ryan McMahon", "L", "+509", 78, "💎 🏟️", ["vs Yesavage"], n("Ryan McMahon", "Yesavage", "park is doing most of the work", "1 HR, 2 near-HR and 92.5 mph EV")),
            row("Dalton Varsho", "L", "+470", 77, "💎", ["vs Schlittler"], n("Dalton Varsho", "Schlittler", "Schlittler is an HR suppressor", "1 HR with .263 ISO but pitcher context drags him down")),
            row("Jesus Sanchez", "L", "+610", 70, "💎", ["vs Schlittler"], n("Jesus Sanchez", "Schlittler", "tough pitcher, decent price", "Contact results are strong but HR-specific lift is lighter")),
            row("Kazuma Okamoto", "R", "+492", 74, "🚀 💎", ["vs Schlittler"], n("Kazuma Okamoto", "Schlittler", "righty raw EV is the hook", "99.5 mph EV and 69.2% hard-hit despite no recent HR")),
        ],
    },
    {
        "title": "BOS @ KC - Connelly Early 🧤 (L, BOS) vs Michael Wacha (R, KC)",
        "description": "Kauffman Stadium — very poor HR setup (-22% HR, wind in / large outfield). Early's LHB HR-risk is high on paper, but the park keeps Royals bats from becoming premium plays.",
        "rows": [
            row("Carter Jensen", "L", "+980", 69, "💎", ["vs Early"], n("Carter Jensen", "Early", "Kauffman is a major HR fade", "Lefty longshot with pull-lift indicators but thin recent power")),
            row("Bobby Witt Jr.", "R", "+508", 78, "🚀 💎", ["vs Early"], n("Bobby Witt Jr.", "Early", "park suppresses but talent carries", "1 HR with 98.2 mph EV and .316 ISO")),
            row("Jarren Duran", "L", "+700", 72, "💎", ["vs Wacha"], n("Jarren Duran", "Wacha", "Wacha is tougher to lefties and Kauffman is huge", "1 HR with 91.2 mph EV at a playable long price")),
            row("Wilyer Abreu", "L", "+525", 68, "💎", ["vs Wacha"], n("Wilyer Abreu", "Wacha", "environment is the biggest problem", "35.7% hard-hit, but no recent HR/near-HR in the sample")),
        ],
    },
    {
        "title": "MIL @ CHC - Kyle Harrison (L, MIL) vs Edward Cabrera 🧤 (R, CHC)",
        "description": "Wrigley Field — the most hostile HR weather on the slate: -41% HR model, 48-50F and wind blowing in hard. Cabrera is HR-risky, but the environment demands discounts.",
        "rows": [
            row("Carson Kelly", "R", "+1050", 66, "💎", ["vs Harrison"], n("Carson Kelly", "Harrison", "Wrigley wind in is brutal", "11.1% barrels, but this is only a longshot catcher dart")),
            row("Michael Conforto", "L", "N/A", 64, "💎", ["vs Harrison"], n("Michael Conforto", "Harrison", "pitcher and weather are both difficult", "Included from the submitted card, but this is a harsh setup")),
            row("Brice Turang", "L", "+1050", 78, "💎 ⚾", ["vs Cabrera"], n("Brice Turang", "Cabrera", "Cabrera is a top-three HR-risk arm, weather is the problem", "2 HR with .444 ISO, but Wrigley wind in keeps him below premium")),
            row("Jackson Chourio", "R", "+930", 75, "🚀 💎 📜", ["vs Cabrera"], n("Jackson Chourio", "Cabrera", "BvP HR helps offset the wind", "Career HR off Cabrera plus 95.4 mph EV in current sample")),
            row("Jake Bauers", "L", "+930", 77, "🚀 💎 ⚾", ["vs Cabrera"], n("Jake Bauers", "Cabrera", "Cabrera's LHB lane is playable", "44.4% barrels and 93.1 mph EV, but wind in is severe")),
            row("William Contreras", "R", "+980", 73, "🚀 💎", ["vs Cabrera"], n("William Contreras", "Cabrera", "righty profile has contact quality", "94.7 mph EV and 61.1% hard-hit, but no recent HR")),
        ],
    },
    {
        "title": "PIT @ STL - Carmen Mlodzinski (R, PIT) vs Michael McGreevy (R, STL)",
        "description": "Busch Stadium — HR model -26% with wind in. This game is mostly bat-form and price; Mlodzinski's lefty contact damage gives Cardinals LHBs the cleaner angle.",
        "rows": [
            row("Alec Burleson", "L", "+650", 76, "💎 📜", ["vs Mlodzinski"], n("Alec Burleson", "Mlodzinski", "Busch is a HR fade", "BvP HR plus 62.5% hard-hit keeps him viable")),
            row("Nolan Gorman", "L", "+500", 82, "🚀 ⭐ 💎", ["vs Mlodzinski"], n("Nolan Gorman", "Mlodzinski", "lefty lane is the best Cardinals path", "Worst Pickz favorite with 99.4 mph EV, 16.7% barrels and 33.3% pull-air"), "good"),
            row("Pedro Pages", "R", "+990", 67, "💎", ["vs Mlodzinski"], n("Pedro Pages", "Mlodzinski", "park and split are not ideal", "1 HR at a long price, but lower EV keeps him thin")),
            row("Brandon Lowe", "L", "+420", 86, "🚀 🌕 💣", ["vs McGreevy"], n("Brandon Lowe", "McGreevy", "park is bad but his form is loud", "Worst Pickz favorite with 2 HR, 3 near-HR and 30.0% barrels"), "good"),
            row("Marcell Ozuna", "R", "+660", 78, "🚀 💎", ["vs McGreevy"], n("Marcell Ozuna", "McGreevy", "pitcher is steady but the bat has damage", "1 HR, 3 near-HR and 53.3% fly balls")),
        ],
    },
    {
        "title": "LAD @ SD - Shohei Ohtani (R, LAD) vs Randy Vasquez (R, SD)",
        "description": "Petco Park — slightly negative HR model but the live feed shows wind out. Vasquez allows enough RHB risk for Will Smith/Pages-type contact; Ohtani suppresses San Diego bats hard overall.",
        "rows": [
            row("Miguel Andujar", "R", "+940", 70, "💎", ["vs Ohtani"], n("Miguel Andujar", "Ohtani", "Ohtani is an elite HR suppressor", "1 HR with .312 ISO, but matchup is very tough")),
            row("Gavin Sheets", "L", "+575", 75, "💎", ["vs Ohtani"], n("Gavin Sheets", "Ohtani", "lefty matchup is difficult", "1 HR with .300 ISO and strong OBP form")),
            row("Ramon Laureano", "R", "+760", 64, "💎", ["vs Ohtani"], n("Ramon Laureano", "Ohtani", "thin longshot versus elite arm", "Submitted-card inclusion with limited current power sample")),
            row("Ty France", "R", "N/A", 67, "💎", ["vs Ohtani"], n("Ty France", "Ohtani", "hard matchup", "28.6% barrels in a tiny sample keeps him barely alive")),
            row("Max Muncy", "L", "+375", 92, "🚀 🌕 💣", ["vs Vasquez"], n("Max Muncy", "Vasquez", "wind out helps offset Petco", "2 HR, 4 near-HR, 94.8 mph EV and 50.0% barrels"), "high"),
            row("Freddie Freeman", "L", "+575", 77, "💎", ["vs Vasquez"], n("Freddie Freeman", "Vasquez", "lefty lane is not Vasquez's weak side", "1 HR with .231 ISO and strong walk rate")),
            row("Will Smith", "R", "+575", 89, "🚀 🌕 💣", ["vs Vasquez"], n("Will Smith", "Vasquez", "Vasquez is weaker to RHB damage", "Worst Pickz favorite with 1 HR, 5 near-HR, 96.8 mph EV and 29.4% barrels"), "high"),
        ],
    },
    {
        "title": "ATH @ LAA - Aaron Civale (R, ATH) vs Jack Kochanowicz (R, LAA)",
        "description": "Angel Stadium — good late HR setup: +7% HR, 70s/80s temps and out-blowing wind pattern. Oakland has the cleaner power lane versus Kochanowicz, while Angels righties face Civale's RHB weakness.",
        "rows": [
            row("Zach Neto", "R", "+440", 80, "🚀 💎 🏟️", ["vs Civale"], n("Zach Neto", "Civale", "Angel Stadium gives a small carry boost", "1 HR with 93.8 mph EV and 25.0% barrels")),
            row("Jo Adell", "R", "+390", 79, "🚀 💎 🏟️", ["vs Civale"], n("Jo Adell", "Civale", "Civale's RHB split is the path", "93.9 mph EV and 25.0% pull-air despite no recent HR")),
            row("Yoan Moncada", "S", "+410", 73, "💎 🏟️", ["vs Civale"], n("Yoan Moncada", "Civale", "park helps but HR form is light", "Solid 92.8 mph EV with switch-hit flexibility")),
            row("Brent Rooker", "R", "+410", 86, "🚀 🌕 📜 🏟️", ["vs Kochanowicz"], n("Brent Rooker", "Kochanowicz", "out-blowing pattern supports righty power", "2 HR with 94.0 mph EV and career HR off Kochanowicz"), "good"),
            row("Nick Kurtz", "L", "+316", 88, "🚀 🌕 💣 📜 🏟️", ["vs Kochanowicz"], n("Nick Kurtz", "Kochanowicz", "warm Angel Stadium plus BvP signal", "1 HR, 2 near-HR, .318 ISO and career HR off Kochanowicz"), "high"),
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
