#!/usr/bin/env python3
"""Generate games[] block for 2026-05-19 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Drake Baldwin (L)",
    "Matt Olson (L)",
    "Pete Alonso (R)",
    "Kyle Schwarber (L)",
    "Spencer Steer (R)",
    "Ben Rice (L)",
    "Ryan Jeffers (R)",
    "Christian Walker (R)",
    "Yordan Alvarez (L)",
    "Willson Contreras (R)",
    "Ian Happ (S)",
    "Michael Conforto (L)",
    "Jo Adell (R)",
    "Gavin Sheets (L)",
}

PLAYER_TEAMS = {
    "Xavier Edwards (S)": "MIA",
    "Drake Baldwin (L)": "ATL",
    "Matt Olson (L)": "ATL",
    "Jorge Mateo (R)": "ATL",
    "Jonathan Aranda (L)": "TB",
    "Taylor Walls (S)": "TB",
    "Pete Alonso (R)": "BAL",
    "Samuel Basallo (L)": "BAL",
    "Tyler O'Neill (R)": "BAL",
    "Kyle Schwarber (L)": "PHI",
    "Bryce Harper (L)": "PHI",
    "Justin Crawford (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Spencer Steer (R)": "CIN",
    "Dane Myers (R)": "CIN",
    "Elly De La Cruz (S)": "CIN",
    "Sal Stewart (R)": "CIN",
    "Matt Vierling (R)": "DET",
    "Riley Greene (L)": "DET",
    "Hao-Yu Lee (R)": "DET",
    "Angel Martinez (S)": "CLE",
    "Chase DeLauter (L)": "CLE",
    "Jose Tena (L)": "WSH",
    "James Wood (L)": "WSH",
    "CJ Abrams (L)": "WSH",
    "Mark Vientos (R)": "NYM",
    "Brett Baty (L)": "NYM",
    "Luis Torrens (R)": "NYM",
    "Ben Rice (L)": "NYY",
    "Austin Wells (L)": "NYY",
    "Aaron Judge (R)": "NYY",
    "Kazuma Okamoto (R)": "TOR",
    "Yohendrick Pinango (L)": "TOR",
    "Daulton Varsho (L)": "TOR",
    "Byron Buxton (R)": "MIN",
    "Ryan Jeffers (R)": "MIN",
    "Josh Bell (S)": "MIN",
    "Ryan Kreidler (R)": "MIN",
    "Zach Cole (L)": "HOU",
    "Christian Walker (R)": "HOU",
    "Yordan Alvarez (L)": "HOU",
    "Zach Dezenzo (R)": "HOU",
    "Nick Loftin (R)": "KC",
    "Willson Contreras (R)": "STL",
    "Ceddanne Rafaela (R)": "BOS",
    "Jarren Duran (L)": "BOS",
    "Ian Happ (S)": "CHC",
    "Miguel Amaya (R)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Pete Crow-Armstrong (L)": "CHC",
    "Michael Busch (L)": "CHC",
    "Jake Bauers (L)": "MIL",
    "Jackson Chourio (R)": "MIL",
    "Garrett Mitchell (L)": "MIL",
    "Alec Burleson (L)": "STL",
    "Pedro Pages (R)": "STL",
    "Masyn Winn (R)": "STL",
    "Brandon Lowe (L)": "PIT",
    "Marcell Ozuna (R)": "PIT",
    "Mickey Moniak (L)": "COL",
    "Willi Castro (S)": "COL",
    "Hunter Goodman (R)": "COL",
    "Justin Foscue (R)": "TEX",
    "Jake Burger (R)": "TEX",
    "Jo Adell (R)": "LAA",
    "Jorge Soler (R)": "LAA",
    "Oswald Peraza (R)": "LAA",
    "Mike Trout (R)": "LAA",
    "Zack Gelof (R)": "ATH",
    "Nick Kurtz (L)": "ATH",
    "Brent Rooker (R)": "ATH",
    "Tyler Soderstrom (L)": "ATH",
    "Julio Rodriguez (R)": "SEA",
    "Randy Arozarena (R)": "SEA",
    "Miguel Vargas (R)": "CWS",
    "Munetaka Murakami (L)": "CWS",
    "Jarred Kelenic (L)": "CWS",
    "Jackson Merrill (L)": "SD",
    "Gavin Sheets (L)": "SD",
    "Manny Machado (R)": "SD",
    "Max Muncy (L)": "LAD",
    "Shohei Ohtani (L)": "LAD",
    "Will Smith (R)": "LAD",
    "Ketel Marte (S)": "ARI",
    "Nolan Arenado (R)": "ARI",
    "Corbin Carroll (L)": "ARI",
    "Harrison Bader (R)": "SF",
    "Willy Adames (R)": "SF",
    "Luis Arraez (L)": "SF",
}


def hand_name(name: str, hand: str) -> str:
    return f"{name} ({hand})"


def odds_text(odds: str) -> str:
    return "Listed prop - Over 0.5 HR" if odds == "N/A" else f"Listed {odds} - Over 0.5 HR"


def row(name, hand, odds, score, emojis, note, chips, blast=None):
    r = {
        "name": hand_name(name, hand),
        "odds": odds_text(odds),
        "score": score,
        "emojis": emojis,
        "note": note,
        "chips": chips,
    }
    if blast:
        r["blast"] = blast
    return r


def note(player, pitcher, park, angle):
    return f"{angle} Draws opposing starter {pitcher}; {park}."


games = [
    {
        "title": "ATL @ MIA - Martin Perez 🧤 (L, ATL) vs Braxton Garrett (L, MIA)",
        "description": "loanDepot park — roof game, HR factor -14%. Miami suppresses homers, but Garrett has tiny 2026 sample with 6.75 WHIP and Atlanta's lefty power still belongs on the sheet.",
        "rows": [
            row("Drake Baldwin", "L", "+600", 93, "🚀 🌕 💣", note("Drake Baldwin", "Garrett", "roof suppresses weather", "Worst Pickz favorite with two HR, four near-HR, 101.5 mph EV and 37.5% barrel rate in the HR matchup table"), ["vs Garrett"], "high"),
            row("Matt Olson", "L", "+460", 88, "🚀 🌕 ⚾", note("Matt Olson", "Garrett", "roof suppresses carry but the bat profile travels", "Worst Pickz favorite with 97.5 mph EV and a clean lefty power lane"), ["vs Garrett"], "high"),
            row("Jorge Mateo", "R", "N/A", 72, "💎", note("Jorge Mateo", "Garrett", "roof keeps him as a dart", "Listed prop with a 1 HR recent window and speed/pull-air upside"), ["vs Garrett"]),
            row("Xavier Edwards", "S", "+1250", 70, "💎", note("Xavier Edwards", "Perez", "Miami park is a fade but price is long", "Switch bat with one HR and one near-HR in the selected pitch mix"), ["vs Perez"]),
        ],
    },
    {
        "title": "BAL @ TB - Kyle Bradish 🧤 (R, BAL) vs Griffin Jax (R, TB)",
        "description": "Tropicana Field — dome, HR factor -2%. Bradish is the leaky arm on this game by HR-risk, while Jax is more neutral but vulnerable to right-handed pull damage.",
        "rows": [
            row("Pete Alonso", "R", "+480", 86, "🚀 🌕 ⚾", note("Pete Alonso", "Jax", "closed dome removes weather help", "Worst Pickz favorite with premium raw power and a plus matchup versus Jax's RHB split"), ["vs Jax"], "high"),
            row("Samuel Basallo", "L", "+650", 83, "🚀 🌕", note("Samuel Basallo", "Jax", "dome is neutral-to-cold for HRs", "Listed prop with 94.1 mph EV, 13.0% barrels and strong recent slug"), ["vs Jax"], "good"),
            row("Tyler O'Neill", "R", "+575", 81, "🚀 💎", note("Tyler O'Neill", "Jax", "park is the only real drag", "Three near-HR and classic pull-air power at plus money"), ["vs Jax"], "good"),
            row("Jonathan Aranda", "L", "+750", 80, "🚀 💎", note("Jonathan Aranda", "Bradish", "Tropicana caps the ceiling", "Tampa lefty gets the better pitcher side with Bradish showing a green LHB HR-risk lane"), ["vs Bradish"]),
            row("Taylor Walls", "S", "+1800", 67, "💎", note("Taylor Walls", "Bradish", "longshot only in a dome", "Included from your Taylor Wells/Walls prop; switch-hit profile keeps him listed"), ["vs Bradish"]),
        ],
    },
    {
        "title": "CIN @ PHI - Chase Burns 🧤 (R, CIN) vs Jesus Luzardo (L, PHI)",
        "description": "Citizens Bank Park — +37% HR, 91F, wind blowing out. This is one of the slate's top HR environments, especially for Philadelphia lefties against Burns' LHB risk.",
        "rows": [
            row("Kyle Schwarber", "L", "+215", 92, "🚀 🌕 💣 🏟️", note("Kyle Schwarber", "Burns", "Citizens Bank is +37% HR with out-blowing wind", "Worst Pickz favorite with three HR, 98.0 mph EV and 36.4% barrels in the recent pitch mix"), ["vs Burns"], "high"),
            row("Bryce Harper", "L", "+363", 87, "🚀 🌕 🏟️", note("Bryce Harper", "Burns", "heat plus small outfield boosts pull carry", "One HR with .429 ISO and elite plate discipline in the sample"), ["vs Burns"], "high"),
            row("Bryson Stott", "L", "+710", 86, "🚀 🌕 🏟️", note("Bryson Stott", "Burns", "same top-tier Philly weather lane", "Two HR, three near-HR and .471 ISO make him one of the better mid-price Phillies"), ["vs Burns"], "high"),
            row("Justin Crawford", "L", "+1160", 82, "🚀 💎 🏟️", note("Justin Crawford", "Burns", "Citizens Bank gives longshot legs", "One HR with 91.9 mph EV and strong contact quality"), ["vs Burns"], "good"),
            row("Spencer Steer", "R", "+570", 85, "🚀 🌕 🏟️", note("Spencer Steer", "Luzardo", "elite weather keeps Cincinnati righties live", "Worst Pickz favorite with one HR, three near-HR, .353 ISO and 94.5 mph EV"), ["vs Luzardo"], "high"),
            row("Dane Myers", "R", "+680", 80, "🚀 💎 🏟️", note("Dane Myers", "Luzardo", "park helps the righty longball path", "One HR and solid righty damage profile at plus money"), ["vs Luzardo"]),
            row("Elly De La Cruz", "S", "+528", 79, "🚀 💎 🏟️", note("Elly De La Cruz", "Luzardo", "wind gives his fly balls a boost", "Two near-HR with 93.7 mph EV and speed/power ceiling"), ["vs Luzardo"]),
            row("Sal Stewart", "R", "+409", 78, "🚀 💎 🏟️", note("Sal Stewart", "Luzardo", "price is short but environment is strong", "One HR and two near-HR with 10.0% barrels"), ["vs Luzardo"]),
        ],
    },
    {
        "title": "CLE @ DET - Parker Messick (L, CLE) vs Keider Montero 🧤 (R, DET)",
        "description": "Comerica Park — delay risk, big wind, HR factor -2%. Montero carries the bigger HR-risk mark, while Messick is lower risk but still allows right-handed balls in play.",
        "rows": [
            row("Matt Vierling", "R", "+850", 82, "🚀 🌕", note("Matt Vierling", "Messick", "Comerica is large but wind is active", "One HR, two near-HR and .364 ISO from the right side"), ["vs Messick"], "good"),
            row("Riley Greene", "L", "+575", 79, "🚀 💎", note("Riley Greene", "Messick", "park size knocks the score down", "Hot recent contact with .535 wOBA in the pitch-mix table"), ["vs Messick"]),
            row("Hao-Yu Lee", "R", "+830", 76, "💎", note("Hao-Yu Lee", "Messick", "righty lane is playable", "Listed prop with 91.1 mph EV and 72.7% fly-ball profile"), ["vs Messick"]),
            row("Angel Martinez", "S", "+630", 84, "🚀 🌕", note("Angel Martinez", "Montero", "Montero is the glove arm in this game", "Three HR, four near-HR and strong switch-hit damage keep him near the top of this game"), ["vs Montero"], "good"),
            row("Chase DeLauter", "L", "+650", 78, "🚀 💎", note("Chase DeLauter", "Montero", "LHB HR-risk is the favorable side against Montero", "93.9 mph EV with sturdy contact quality"), ["vs Montero"]),
        ],
    },
    {
        "title": "NYM @ WSH - Nolan McLean (R, NYM) vs Foster Griffin 🧤 (L, WSH)",
        "description": "Nationals Park — +5% HR, 93F. Hot air boosts this game, and Griffin's HR-risk is the main Mets path while Washington lefties face a tougher McLean profile.",
        "rows": [
            row("James Wood", "L", "+390", 88, "🚀 🌕 🏟️", note("James Wood", "McLean", "93F air keeps the ceiling alive", "Two HR, six near-HR, 96.3 mph EV and 27.3% barrels"), ["vs McLean"], "high"),
            row("Jose Tena", "L", "+990", 81, "🚀 💎 🏟️", note("Jose Tena", "McLean", "heat supports the lefty longshot", "One HR with 95.4 mph EV and 21.7% barrels"), ["vs McLean"]),
            row("CJ Abrams", "L", "+500", 77, "💎 🏟️", note("CJ Abrams", "McLean", "hot weather helps but McLean suppresses LHBs", "Listed prop with pull-air upside from the left side"), ["vs McLean"]),
            row("Mark Vientos", "R", "+460", 84, "🚀 🌕 🏟️", note("Mark Vientos", "Griffin", "Mets righties get the glove pitcher", "One HR, three near-HR, 95.2 mph EV and 60.0% hard-hit"), ["vs Griffin"], "good"),
            row("Brett Baty", "L", "+650", 74, "💎 🏟️", note("Brett Baty", "Griffin", "heat is doing most of the work", "93.0 mph EV but high whiff/K drag"), ["vs Griffin"]),
            row("Luis Torrens", "R", "+930", 70, "💎", note("Luis Torrens", "Griffin", "longshot catcher power", "Listed prop against the lower-rated starter side"), ["vs Griffin"]),
        ],
    },
    {
        "title": "TOR @ NYY - Dylan Cease (R, TOR) vs Will Warren 🧤 (R, NYY)",
        "description": "Yankee Stadium — +18% HR, 89F, wind blowing out. Warren is the pitcher to attack, while Cease is a strong suppressor despite Yankee Stadium's short porch.",
        "rows": [
            row("Ben Rice", "L", "+360", 87, "🚀 🌕 🏟️", note("Ben Rice", "Cease", "Yankee Stadium weather helps lefty lift", "Worst Pickz favorite with two HR, 50.0% barrels and .462 ISO"), ["vs Cease"], "high"),
            row("Aaron Judge", "R", "+240", 86, "🚀 🌕 🏟️", note("Aaron Judge", "Cease", "elite park/weather offsets tough pitcher", "One HR and premium raw power in the slate's second-best HR weather row"), ["vs Cease"], "high"),
            row("Austin Wells", "L", "+750", 73, "💎 🏟️", note("Austin Wells", "Cease", "short porch helps if he lifts it", "Listed prop with catcher pop but cold recent results"), ["vs Cease"]),
            row("Kazuma Okamoto", "R", "+391", 82, "🚀 💎 🏟️", note("Kazuma Okamoto", "Warren", "Toronto righties get the leaky starter", "94.5 mph EV and 16.7% barrels against Warren's higher HR-risk side"), ["vs Warren"], "good"),
            row("Yohendrick Pinango", "L", "+700", 78, "💎 🏟️", note("Yohendrick Pinango", "Warren", "Warren's LHB HR-risk is green", "One HR and two near-HR at a playable price"), ["vs Warren"]),
            row("Daulton Varsho", "L", "+410", 81, "🚀 💎 🏟️", note("Daulton Varsho", "Warren", "same LHB lane into Yankee carry", "One HR, two near-HR and 15.0% barrels"), ["vs Warren"], "good"),
        ],
    },
    {
        "title": "HOU @ MIN - Lance McCullers Jr. 🧤 (R, HOU) vs Zebby Matthews (R, MIN)",
        "description": "Target Field — cold 50F air, HR factor -22%. McCullers is the biggest HR-risk arm on the slate, but the weather is harsh for carry.",
        "rows": [
            row("Ryan Jeffers", "R", "+500", 96, "🚀 🌕 💣", note("Ryan Jeffers", "McCullers Jr.", "cold air is the only real drawback", "Worst Pickz favorite with three HR, 1.000 ISO, 96.8 mph EV and 30.0% barrels"), ["vs McCullers Jr."], "high"),
            row("Byron Buxton", "R", "N/A", 89, "🚀 🌕", note("Byron Buxton", "McCullers Jr.", "weather suppresses but pitcher is leaky", "Two HR with 41.7% pull-air and elite speed/power damage"), ["vs McCullers Jr."], "high"),
            row("Josh Bell", "S", "+700", 78, "🚀 💎", note("Josh Bell", "McCullers Jr.", "switch bat gets the glove pitcher", "One HR with 91.3 mph EV and 15.4% barrels"), ["vs McCullers Jr."]),
            row("Ryan Kreidler", "R", "N/A", 75, "💎", note("Ryan Kreidler", "McCullers Jr.", "small sample but live pitcher", "One HR in a tiny window keeps him on the prop card"), ["vs McCullers Jr."]),
            row("Yordan Alvarez", "L", "+306", 94, "🚀 🌕 💣", note("Yordan Alvarez", "Matthews", "Matthews is lower-risk but Yordan's bat is the separator", "Worst Pickz favorite with two HR, 100.4 mph EV and 69.2% hard-hit"), ["vs Matthews"], "high"),
            row("Christian Walker", "R", "+450", 88, "🚀 🌕", note("Christian Walker", "Matthews", "cold lowers the total", "Worst Pickz favorite with two HR and 16.7% barrels"), ["vs Matthews"], "high"),
            row("Zach Cole", "L", "+542", 82, "🚀 💎", note("Zach Cole", "Matthews", "lefty power at plus money", "One HR with 91.1 mph EV and 55.6% hard-hit"), ["vs Matthews"], "good"),
            row("Zach Dezenzo", "R", "N/A", 76, "💎", note("Zach Dezenzo", "Matthews", "longshot Astros righty", "96.2 mph EV and big contact when he connects"), ["vs Matthews"]),
        ],
    },
    {
        "title": "BOS @ KC - Ranger Suarez (L, BOS) vs Luinder Avila 🧤 (R, KC)",
        "description": "Kauffman Stadium — HR factor -21% but wind noted in from the projected lineup feed. Avila has limited/primary data and a high ERA, making Boston bats the better attack point.",
        "rows": [
            row("Jarren Duran", "L", "+725", 78, "💎", note("Jarren Duran", "Avila", "Kauffman is spacious with wind in", "Listed prop with 94.8 mph EV in the available pitch-mix sample"), ["vs Avila"]),
            row("Ceddanne Rafaela", "R", "+800", 76, "💎", note("Ceddanne Rafaela", "Avila", "park is a drag but matchup data is thin", "100.0 mph EV in a small sample keeps the longshot alive"), ["vs Avila"]),
            row("Nick Loftin", "R", "+1280", 72, "💎", note("Nick Loftin", "Suarez", "KC environment is not ideal", "Longshot with one near-HR and low whiff profile"), ["vs Suarez"]),
        ],
    },
    {
        "title": "MIL @ CHC - Jacob Misiorowski (R, MIL) vs Ben Brown (R, CHC)",
        "description": "Wrigley Field — HR factor -1% on Ballpark Pal despite strong crosswind. Both starters grade as HR suppressors, so this game is more bat-form than pitcher leak.",
        "rows": [
            row("Michael Conforto", "L", "+700", 86, "🚀 🌕", note("Michael Conforto", "Misiorowski", "Wrigley can still flip if wind helps carry", "Worst Pickz favorite with two HR, three near-HR, .600 ISO and 95.6 mph EV"), ["vs Misiorowski"], "high"),
            row("Ian Happ", "S", "+600", 84, "🚀 🌕", note("Ian Happ", "Misiorowski", "switch-hit power in Wrigley keeps him live", "Worst Pickz favorite with 37.5% barrels and 96.5 mph EV"), ["vs Misiorowski"], "good"),
            row("Miguel Amaya", "R", "N/A", 80, "🚀 💎", note("Miguel Amaya", "Misiorowski", "pitcher is tough but form is loud", "Two HR and two near-HR with 25.0% barrels"), ["vs Misiorowski"]),
            row("Pete Crow-Armstrong", "L", "+725", 77, "💎", note("Pete Crow-Armstrong", "Misiorowski", "speed-power dart against a tough arm", "One HR with pull-side lift in the sample"), ["vs Misiorowski"]),
            row("Michael Busch", "L", "+510", 79, "🚀 💎", note("Michael Busch", "Misiorowski", "lefty pull profile is the Cubs angle", "93.2 mph EV and strong on-base power traits"), ["vs Misiorowski"]),
            row("Jake Bauers", "L", "+575", 78, "🚀 💎", note("Jake Bauers", "Brown", "Brown is HR-suppressive, so this is bat-form driven", "98.0 mph EV and 28.6% barrels"), ["vs Brown"]),
            row("Jackson Chourio", "R", "+500", 74, "💎", note("Jackson Chourio", "Brown", "raw talent play versus a strong pitcher", "Listed prop despite Brown's low HR-risk"), ["vs Brown"]),
            row("Garrett Mitchell", "L", "+1000", 73, "💎", note("Garrett Mitchell", "Brown", "longshot only", "99.2 mph EV but difficult pitcher context"), ["vs Brown"]),
        ],
    },
    {
        "title": "PIT @ STL - Mitch Keller (R, PIT) vs Matthew Liberatore 🧤 (L, STL)",
        "description": "Busch Stadium — delay risk, HR factor -20%. Liberatore is a clear HR-risk arm, but the park/weather context is harsh.",
        "rows": [
            row("Willson Contreras", "R", "+500", 85, "🚀 🌕", note("Willson Contreras", "Keller", "Busch is cold for HRs", "Worst Pickz favorite with one HR, two near-HR and 40.0% barrels"), ["vs Keller"], "good"),
            row("Alec Burleson", "L", "N/A", 77, "💎", note("Alec Burleson", "Keller", "lefty contact profile in a pitcher park", "Included from your prop list with a playable BvP/history note"), ["vs Keller"]),
            row("Pedro Pages", "R", "N/A", 72, "💎", note("Pedro Pages", "Keller", "catcher pop in a hard park", "Listed prop with some historical contact versus Keller"), ["vs Keller"]),
            row("Masyn Winn", "R", "N/A", 71, "💎", note("Masyn Winn", "Keller", "mostly a longshot speed-contact profile", "Listed prop but HR park factor is poor"), ["vs Keller"]),
            row("Brandon Lowe", "L", "N/A", 82, "🚀 💎", note("Brandon Lowe", "Liberatore", "Liberatore is the leaky starter but Busch suppresses carry", "Worst Pickz favorite and lefty pull-power path for Pittsburgh"), ["vs Liberatore"], "good"),
            row("Marcell Ozuna", "R", "N/A", 80, "🚀 💎", note("Marcell Ozuna", "Liberatore", "pitcher leak offsets park drag", "Right-handed thump into Liberatore's weaker side"), ["vs Liberatore"]),
        ],
    },
    {
        "title": "TEX @ COL - Kumar Rocker (R, TEX) vs Tanner Gordon 🧤 (R, COL)",
        "description": "Coors Field — top run environment but HR factor -5% by Coors standards, cold 40s and delay risk. Gordon's projected 5.57 ERA/primary data makes Texas bats important to list.",
        "rows": [
            row("Mickey Moniak", "L", "+390", 82, "🚀 💎 🏟️", note("Mickey Moniak", "Rocker", "Coors altitude still matters even with cold air", "Listed prop with lefty lift and a favorable game total"), ["vs Rocker"], "good"),
            row("Willi Castro", "S", "+875", 78, "💎 🏟️", note("Willi Castro", "Rocker", "cold Coors keeps this below the elite tier", "One HR and two near-HR with 41.7% pull-air"), ["vs Rocker"]),
            row("Hunter Goodman", "R", "+360", 81, "🚀 💎 🏟️", note("Hunter Goodman", "Rocker", "home Coors pop is enough to include", "Listed prop with 93.0 mph EV and pull-air fit"), ["vs Rocker"]),
            row("Justin Foscue", "R", "+760", 80, "🚀 💎 🏟️", note("Justin Foscue", "Gordon", "Texas gets the glove starter in Coors", "One HR in a micro-sample with 103.2 mph EV"), ["vs Gordon"]),
            row("Jake Burger", "R", "+460", 77, "💎 🏟️", note("Jake Burger", "Gordon", "power plays anywhere but cold weather holds score down", "Listed prop with a pull-heavy HR profile"), ["vs Gordon"]),
        ],
    },
    {
        "title": "ATH @ LAA - Jacob Lopez 🧤 (L, ATH) vs Reid Detmers (L, LAA)",
        "description": "Angel Stadium — +5% HR, mild weather and usual out-blowing pattern. Lopez is one of the slate's clear RHB attack arms with 2.23 HR/9 and a 1.19 vs-RHB HR-risk.",
        "rows": [
            row("Jo Adell", "R", "+350", 90, "🚀 🌕 💣", note("Jo Adell", "Lopez", "Angel Stadium gives a small HR push", "Worst Pickz favorite with two HR, 98.8 mph EV and 36.4% barrels against the slate's third-ranked HR-risk arm"), ["vs Lopez"], "high"),
            row("Mike Trout", "R", "+362", 85, "🚀 🌕", note("Mike Trout", "Lopez", "righty power lane is obvious", "Listed prop with 92.1 mph EV and elite raw power against Lopez's RHB weakness"), ["vs Lopez"], "good"),
            row("Jorge Soler", "R", "+440", 82, "🚀 💎", note("Jorge Soler", "Lopez", "same RHB pitcher leak", "Listed prop with pull-air power even through recent whiff risk"), ["vs Lopez"]),
            row("Oswald Peraza", "R", "+579", 80, "🚀 💎", note("Oswald Peraza", "Lopez", "plus matchup for righty lift", "One HR and two near-HR with 93.7 mph EV"), ["vs Lopez"]),
            row("Zack Gelof", "R", "+700", 81, "🚀 💎", note("Zack Gelof", "Detmers", "Oakland righties face the steadier arm", "One HR with 93.3 mph EV and 16.7% barrels"), ["vs Detmers"]),
            row("Nick Kurtz", "L", "+440", 80, "🚀 💎", note("Nick Kurtz", "Detmers", "left-on-left but raw damage is real", "One HR with 96.2 mph EV and 33.3% barrels"), ["vs Detmers"]),
            row("Brent Rooker", "R", "+440", 82, "🚀 💎", note("Brent Rooker", "Detmers", "righty power survives the pitcher context", "One HR and 50.0% pull-air in the table"), ["vs Detmers"]),
            row("Tyler Soderstrom", "L", "+550", 79, "🚀 💎", note("Tyler Soderstrom", "Detmers", "lefty power dart", "One HR, two near-HR and 28.6% barrels"), ["vs Detmers"]),
        ],
    },
    {
        "title": "CWS @ SEA - Anthony Kay 🧤 (L, CWS) vs Luis Castillo 🧤 (R, SEA)",
        "description": "T-Mobile Park — HR factor -11%, roof environment. Kay has a dangerous RHB split and Castillo's projected 6.34 ERA/primary data keeps Chicago's top lefty power on the board.",
        "rows": [
            row("Julio Rodriguez", "R", "+470", 94, "🚀 🌕 💣", note("Julio Rodriguez", "Kay", "park is harsh but pitcher split is excellent for RHBs", "Four HR, four near-HR and 94.4 mph EV against Anthony Kay's leaky righty lane"), ["vs Kay"], "high"),
            row("Randy Arozarena", "R", "+550", 84, "🚀 🌕", note("Randy Arozarena", "Kay", "RHB angle is the Mariners' path", "One HR, two near-HR and 95.7 mph EV"), ["vs Kay"], "good"),
            row("Miguel Vargas", "R", "+550", 86, "🚀 🌕", note("Miguel Vargas", "Castillo", "T-Mobile suppresses carry but his form is loud", "Two HR, five near-HR and .346 ISO"), ["vs Castillo"], "high"),
            row("Munetaka Murakami", "L", "+320", 88, "🚀 🌕 💣", note("Munetaka Murakami", "Castillo", "park is a fade but talent/form grades through", "Three HR, 96.6 mph EV and 27.8% barrels"), ["vs Castillo"], "high"),
            row("Jarred Kelenic", "L", "+650", 80, "🚀 💎", note("Jarred Kelenic", "Castillo", "former Seattle power in a tough park", "98.1 mph EV and 31.2% barrels keep him playable"), ["vs Castillo"]),
        ],
    },
    {
        "title": "LAD @ SD - Emmet Sheehan 🧤 (R, LAD) vs Griffin Canning (R, SD)",
        "description": "Petco Park — HR factor -6%, marine layer risk. Sheehan's LHB split is the Padres angle, while Canning's overall form makes Dodgers power viable despite the park.",
        "rows": [
            row("Gavin Sheets", "L", "+580", 92, "🚀 🌕 💣", note("Gavin Sheets", "Sheehan", "Petco is harsh but Sheehan's LHB HR-risk is high", "Worst Pickz favorite with three HR, .625 ISO and 14.3% barrels"), ["vs Sheehan"], "high"),
            row("Jackson Merrill", "L", "+600", 78, "💎", note("Jackson Merrill", "Sheehan", "lefty matchup is playable but recent K rate is high", "Two near-HR and 92.6 mph EV"), ["vs Sheehan"]),
            row("Manny Machado", "R", "+630", 76, "💎", note("Manny Machado", "Sheehan", "righty lane is tougher", "Listed prop with 91.1 mph EV and pull-side damage history"), ["vs Sheehan"]),
            row("Max Muncy", "L", "+440", 91, "🚀 🌕 💣", note("Max Muncy", "Canning", "Dodgers lefty pull power can beat Petco", "Three HR, five near-HR, 95.2 mph EV and 42.9% barrels"), ["vs Canning"], "high"),
            row("Shohei Ohtani", "L", "+310", 87, "🚀 🌕", note("Shohei Ohtani", "Canning", "short price but premium barrel profile", "Listed prop with 88.4 mph EV in this table but elite season-long power"), ["vs Canning"], "high"),
            row("Will Smith", "R", "+600", 84, "🚀 🌕", note("Will Smith", "Canning", "catcher power at plus money", "One HR, five near-HR and 25.0% barrels"), ["vs Canning"], "good"),
        ],
    },
    {
        "title": "SF @ ARI - Landen Roupp (R, SF) vs Ryne Nelson 🧤 (R, ARI)",
        "description": "Chase Field — roof scheduled open, HR factor -7% but warm, dry air. Nelson is the clear glove pitcher with 1.80 HR/9 and a 1.61 vs-RHB HR-risk.",
        "rows": [
            row("Willy Adames", "R", "+500", 86, "🚀 🌕", note("Willy Adames", "Nelson", "open-roof Chase helps the righty path", "One HR, three near-HR and 92.3 mph EV against Nelson's worst split"), ["vs Nelson"], "high"),
            row("Harrison Bader", "R", "+800", 82, "🚀 💎", note("Harrison Bader", "Nelson", "RHB lane is the target", "One HR, three near-HR and 54.5% pull-air"), ["vs Nelson"], "good"),
            row("Luis Arraez", "L", "+1450", 72, "💎", note("Luis Arraez", "Nelson", "contact profile longshot", "One HR and two near-HR in the table but usually low-HR batted ball shape"), ["vs Nelson"]),
            row("Ketel Marte", "S", "+525", 83, "🚀 💎", note("Ketel Marte", "Roupp", "home side faces the lower-risk starter", "Switch-hit pop with one near-HR and solid contact quality"), ["vs Roupp"], "good"),
            row("Corbin Carroll", "L", "+650", 84, "🚀 🌕", note("Corbin Carroll", "Roupp", "warm Chase air is the helper", "One HR, three near-HR and 95.0 mph EV"), ["vs Roupp"], "good"),
            row("Nolan Arenado", "R", "+980", 81, "🚀 💎", note("Nolan Arenado", "Roupp", "righty longshot in a playable roof-open setting", "One HR with .500 ISO in the recent table"), ["vs Roupp"]),
        ],
    },
]

PROP_NAMES = {
    "Xavier Edwards", "Drake Baldwin", "Matt Olson", "Jorge Mateo", "Jonathan Aranda",
    "Taylor Walls", "Pete Alonso", "Samuel Basallo", "Tyler O'Neill", "Kyle Schwarber",
    "Bryce Harper", "Justin Crawford", "Bryson Stott", "Spencer Steer", "Dane Myers",
    "Elly De La Cruz", "Sal Stewart", "Matt Vierling", "Riley Greene", "Hao-Yu Lee",
    "Angel Martinez", "Chase DeLauter", "Jose Tena", "James Wood", "CJ Abrams",
    "Mark Vientos", "Brett Baty", "Luis Torrens", "Ben Rice", "Austin Wells",
    "Aaron Judge", "Kazuma Okamoto", "Yohendrick Pinango", "Daulton Varsho",
    "Byron Buxton", "Ryan Jeffers", "Josh Bell", "Ryan Kreidler", "Zach Cole",
    "Christian Walker", "Yordan Alvarez", "Zach Dezenzo", "Nick Loftin",
    "Willson Contreras", "Ceddanne Rafaela", "Jarren Duran", "Ian Happ",
    "Miguel Amaya", "Michael Conforto", "Pete Crow-Armstrong", "Michael Busch",
    "Jake Bauers", "Jackson Chourio", "Garrett Mitchell", "Alec Burleson",
    "Pedro Pages", "Masyn Winn", "Brandon Lowe", "Marcell Ozuna", "Mickey Moniak",
    "Willi Castro", "Hunter Goodman", "Justin Foscue", "Jake Burger", "Jo Adell",
    "Jorge Soler", "Oswald Peraza", "Mike Trout", "Zack Gelof", "Nick Kurtz",
    "Brent Rooker", "Tyler Soderstrom", "Julio Rodriguez", "Randy Arozarena",
    "Miguel Vargas", "Munetaka Murakami", "Jarred Kelenic", "Jackson Merrill",
    "Gavin Sheets", "Manny Machado", "Max Muncy", "Shohei Ohtani", "Will Smith",
    "Ketel Marte", "Nolan Arenado", "Corbin Carroll", "Harrison Bader",
    "Willy Adames", "Luis Arraez",
}

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
