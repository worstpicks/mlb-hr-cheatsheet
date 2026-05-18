#!/usr/bin/env python3
"""Generate games[] block for 2026-05-18 MLB HR cheat sheet (88 props, 15 games)."""
import json
import re
from pathlib import Path

from overdue_eval import apply_inferred_due, tag_games_overdue

ROOT = Path(__file__).resolve().parent
STATCAST_PATH = ROOT / "data" / "statcast-2026-05-18.json"

FAVS = {
    "Kyle Schwarber (L)",
    "JJ Bleday (L)",
    "Will Benson (L)",
    "James Wood (L)",
    "Juan Soto (L)",
    "Byron Buxton (R)",
    "Yordan Alvarez (L)",
    "Bobby Witt Jr. (R)",
    "Ian Happ (S)",
    "Seiya Suzuki (R)",
    "Michael Busch (L)",
    "Michael Conforto (L)",
    "Hunter Goodman (R)",
    "Miguel Vargas (R)",
    "Gavin Sheets (L)",
    "Jackson Merrill (L)",
    "Julio Rodriguez (R)",
    "Will Smith (R)",
    "Shohei Ohtani (L)",
}

def row(name, odds, score, emojis, note, chips, blast=None):
    r = {"name": name, "odds": f"Listed {odds} - Over 0.5 HR", "score": score, "emojis": emojis, "note": note, "chips": chips}
    if blast:
        r["blast"] = blast
    return r

games = [
    {
        "title": "BAL @ TB - Shane McClanahan 🧤 (L, TB) vs Trevor Rogers 🧤 (L, BAL)",
        "description": "Tropicana Field — closed dome, weather-neutral (-6% HR row). McClanahan suppresses both hands overall; Rogers' vs-RHB HR-risk (0.25) is the main Baltimore righty lane.",
        "rows": [
            row("Junior Caminero (R)", "+360", 86, "🚀 🌕 ⚾", "One HR and one near-HR with 96.2 mph EV and 54.5% hard-hit; Rogers' vs-RHB split is the clearest Orioles attack point into Tampa.", ["vs Rogers"], "high"),
            row("Coby Mayo (R)", "+600", 91, "🚀 🌕 💣 ⚾", "Three HR and three near-HR with 33.3% barrels, 55.6% pull-air, and 1.000 SLG in the window; same McClanahan RHB lane with elite damage rate.", ["vs McClanahan"], "high"),
            row("Pete Alonso (R)", "+441", 88, "🚀 🌕 ⚾", "Two HR and two near-HR with 98.7 mph EV and 22.2% barrels; McClanahan's vs-RHB line (-0.48) is softer than his lefty suppression.", ["vs McClanahan", "📜 3-3 vs McClanahan"], "high"),
            row("Samuel Basallo (L)", "+600", 79, "🚀 💎", "One HR and two near-HR with 52.9% squared-up contact; Rogers LHB lane is modest but Basallo's 94.9 mph EV keeps him playable.", ["vs Rogers"]),
            row("Yandy Diaz (R)", "+550", 74, "🚀 💎", "One HR with 50% hard-hit; McClanahan's overall HR suppression (-1.07 composite) caps the ceiling despite Diaz's pull-side fly balls.", ["vs McClanahan"]),
        ],
    },
    {
        "title": "CIN @ PHI - Andrew Painter 🧤 (R, PHI) vs Nick Lodolo 🧤 (L, CIN)",
        "description": "Citizens Bank Park — +31% HR row, 88°F, 11 mph blowing out. Painter's vs-RHB HR-risk (1.95) and 3.14 HR/9 to righties headline the Phillies side; Lodolo is hittable for RHB (1.04) in a small park.",
        "rows": [
            row("Kyle Schwarber (L)", "+230", 90, "🚀 🌕 ⚾ 🕊️ 🏟️", "One HR with 33.3% barrels and .857 ISO; clear pitcher HR-risk advantage—Painter's vs-LHB index (0.18) is red for pitchers but Lodolo's RHB leakage powers Philly lefty pull at a short price.", ["vs Lodolo"], "high"),
            row("Adolis Garcia (R)", "+450", 85, "🚀 🌕 ⚾ 🕊️", "One HR with 97.5 mph EV and 80% hard-hit; clear pitcher HR-risk advantage on Lodolo's vs-RHB split (1.04) in the slate's top HR park row.", ["vs Lodolo"], "high"),
            row("Alec Bohm (R)", "+680", 82, "🚀 ⚾ 🕊️", "One HR with 92.7 mph EV and 42.9% pull-air; Painter's RHB HR/9 (3.14) and 38.5% HR/FB to righties fit Bohm's damage.", ["vs Painter"], "good"),
            row("JJ Bleday (L)", "+390", 84, "🚀 🌕 💎", "One HR and two near-HR with .545 ISO and 60% pull-air; Lodolo's LHB line is only mildly green—Bleday's L5 stick and Citizens Bank carry do the work.", ["vs Lodolo"], "high"),
            row("Elly De La Cruz (S)", "+410", 80, "🚀 💎", "One HR and two near-HR with 97.7 mph EV; SHB uses Painter's RHB mix where Philadelphia's attack is cleaner than the Reds side.", ["vs Painter"], "good"),
            row("Tyler Stephenson (R)", "+552", 76, "💎 ⚾", "One HR with pull-side contact; Painter RHB leak at plus money—Stephenson's K rate is the drag.", ["vs Painter"]),
            row("Matt McLain (R)", "+790", 73, "💎", "One HR with 45.5% hard-hit; Painter's vs-RHB HR-risk is the angle at long price.", ["vs Painter"]),
            row("J.T. Realmuto (R)", "+575", 71, "💎", "Modest L5 line but 53.3% hard-hit; Painter RHB lane—mostly catcher pop longshot.", ["vs Painter"]),
            row("Will Benson (L)", "+410", 72, "💎", "14.3% barrels and 97.3 mph EV in a small window; Lodolo suppresses lefties overall—favorite tag is form/price sensitive.", ["vs Lodolo"]),
        ],
    },
    {
        "title": "ATL @ MIA - JR Ritchie 🧤 (R, ATL) vs Max Meyer (R, MIA)",
        "description": "loanDepot park — partial roof, 81°F, 13% precip. Ritchie's vs-LHB HR-risk (1.29) powers Atlanta; Meyer is contact-heavy with modest RHB leakage (0.41).",
        "rows": [
            row("Austin Riley (R)", "+570", 93, "🚀 🌕 💣 ⚾", "Three HR and five near-HR with 23.8% barrels and 47.6% pull-air; Ritchie's vs-LHB HR-risk (1.29) is the clearest Braves lane despite Meyer's overall suppression.", ["vs Meyer"], "high"),
            row("Matt Olson (L)", "+451", 86, "🚀 🌕 ⚾", "Three HR and three near-HR with 16.7% barrels and 96.4 mph EV; Meyer limits HR overall but Olson's pull-side ceiling versus RHP stays elite.", ["vs Meyer"], "high"),
            row("Mike Yastrzemski (L)", "+800", 78, "🚀 💎", "Two HR and two near-HR with 28.6% pull-air; Ritchie's LHB leakage (2.63 HR/9 to lefties in split) is the Atlanta lefty path.", ["vs Meyer"]),
            row("Jakob Marsee (L)", "+850", 74, "💎", "One HR and two near-HR with 35.5% squared-up rate; Meyer RHB context at plus money.", ["vs Meyer"]),
            row("Otto Lopez (R)", "+790", 68, "💎", "Modest contact versus Ritchie's stingy RHB line (-1.73)—longshot only.", ["vs Ritchie"]),
            row("Xavier Edwards (S)", "+1450", 65, "💎", "SHB versus Ritchie with limited pull-air; mostly price dart.", ["vs Ritchie"]),
        ],
    },
    {
        "title": "CLE @ DET - Slade Cecconi 🧤 (R, CLE) vs Framber Valdez 🧤 (L, DET)",
        "description": "Comerica Park — -1% runs row, 84°F, 16 mph wind. Valdez allows RHB damage (0.56 HR-risk); Cecconi's vs-RHB split (0.24) is mildly hittable for Detroit righties.",
        "rows": [
            row("Dillon Dingler (R)", "+610", 77, "🚀 💎", "40% hard-hit with pull-side fly balls; Cecconi's RHB line is the Cleveland attack lane into Detroit.", ["vs Cecconi"]),
            row("Rhys Hoskins (R)", "+575", 75, "🚀 💎", "One near-HR with 96.7 mph EV and 80% hard-hit; Cecconi RHB context—Hoskins' tiny sample K rate is the drag.", ["vs Cecconi"], "good"),
            row("Travis Bazzana (L)", "+1500", 72, "💎", "One HR with .750 SLG in the window; Valdez LHB lane at long price for the Tigers prospect bat.", ["vs Valdez"]),
        ],
    },
    {
        "title": "NYM @ WSH - Christian Scott (R, NYM) vs Jake Irvin 🧤 (R, WSH)",
        "description": "Nationals Park — +9% HR row, 92°F, 10 mph. Irvin's vs-RHB HR-risk (0.48) and Scott's LHB suppression (-1.29) set up a hot-air Mets righty path versus Washington.",
        "rows": [
            row("James Wood (L)", "+295", 89, "🚀 🌕 ⚾ 🏟️", "Two near-HR with 99.5 mph EV and 72.7% hard-hit; Scott's RHB leakage plus Nationals Park heat is the slate's top lefty environment row.", ["vs Scott"], "high"),
            row("Mark Vientos (R)", "+390", 81, "🚀 💎", "Two near-HR with 37.5% hard-hit; Scott's vs-RHB line (0.39) is workable for Mets righty pull.", ["vs Scott"], "good"),
            row("Jose Tena (L)", "+750", 78, "🚀 💎", "One HR with 103.6 mph EV and .667 ISO; Irvin LHB context at plus money.", ["vs Irvin"], "good"),
            row("Juan Soto (L)", "+280", 76, "💎", "Two HR in window but .158 BA—mostly pedigree and Irvin exposure at a short price; Scott suppresses lefties.", ["vs Scott", "📜 2-9 vs Irvin"]),
            row("MJ Melendez (L)", "+450", 70, "💎", "One near-HR with 96.1 mph EV; Irvin RHB lane for Mets bench bat—high K risk.", ["vs Irvin"]),
        ],
    },
    {
        "title": "TOR @ NYY - Patrick Corbin (L, TOR) vs Ryan Weathers 🧤 (L, NYY)",
        "description": "Yankee Stadium — -7% HR row, 73°F, 10 mph R-L. Weathers' vs-RHB HR-risk (0.59) is the Toronto righty lane; Corbin suppresses both hands in the Bronx.",
        "rows": [
            row("Paul Goldschmidt (R)", "+450", 84, "🚀 🌕 💎", "One HR with 16.7% barrels and 50% hard-hit; Weathers' vs-RHB split is the cleaner Blue Jays attack lane.", ["vs Weathers", "📜 1-18 vs Weathers"], "high"),
            row("Trent Grisham (L)", "+510", 80, "🚀 💎", "One HR with 18.2% barrels and 54.5% hard-hit; Corbin's LHB suppression (-0.79) is real but Grisham's pull-side fit versus lefty keeps him live.", ["vs Corbin"]),
            row("George Springer (R)", "+575", 77, "🚀 💎", "One near-HR with 54.5% hard-hit and 50% fastball contact; Weathers RHB lane.", ["vs Weathers"]),
            row("Kazuma Okamoto (R)", "+480", 79, "🚀 ⚾", "One HR with 101.6 mph EV and 77.8% hard-hit; Weathers vs-RHB HR-risk fits Japanese slugger's pull profile.", ["vs Weathers"], "good"),
            row("Jazz Chisholm Jr. (L)", "+650", 72, "💎", "Modest L5 versus Corbin; mostly athleticism longshot.", ["vs Corbin"]),
            row("Amed Rosario (R)", "+980", 71, "💎", "One HR with 95 mph EV; Weathers RHB at long price.", ["vs Weathers"]),
            row("Ernie Clement (R)", "+1120", 68, "💎", "One HR with .700 SLG in tiny window; Weathers exposure only.", ["vs Weathers"]),
        ],
    },
    {
        "title": "HOU @ MIN - Tatsuya Imai 🧤 (R, HOU) vs Kendry Rojas (L, MIN)",
        "description": "Target Field — flat HR row (0%), 59°F, 56% precip risk. Imai's vs-LHB HR-risk (0.76) helps Houston lefties; Rojas is stingy to both hands in a cold night script.",
        "rows": [
            row("Byron Buxton (R)", "+297", 92, "🚀 🌕 ⚾ 🕊️", "Three HR and five near-HR with 46.2% barrels and .842 SLG; clear pitcher HR-risk advantage—Imai's vs-RHB line (-0.02) is neutral but Buxton's damage form is slate-breaking.", ["vs Imai"], "high"),
            row("Yordan Alvarez (L)", "+340", 88, "🚀 🌕 ⚾ 🕊️", "One HR with 92.5 mph EV and 47.1% hard-hit; clear pitcher HR-risk advantage on Imai's vs-LHB split (0.76) despite Target's carry tax.", ["vs Rojas"], "high"),
            row("Ryan Jeffers (R)", "+592", 83, "🚀 ⚾", "One HR with 33.3% barrels and 66.7% hard-hit; Rojas RHB lane with Jeffers' pull-side damage.", ["vs Rojas"], "good"),
            row("Brice Matthews (R)", "+590", 76, "💎", "One HR with 83.9 mph EV; Imai RHB context—Matthews' K rate caps score.", ["vs Imai"]),
            row("Zach Dezenzo (R)", "+725", 80, "🚀 💎", "One HR and two near-HR with 66.7% barrels in micro-sample; Imai hittable for Houston righties at plus money.", ["vs Imai"], "good"),
            row("Tristan Gray (L)", "+900", 68, "💎", "One near-HR with 95.8 mph EV; Imai LHB lane—limited PA window.", ["vs Imai"]),
        ],
    },
    {
        "title": "BOS @ KC - Sonny Gray 🧤 (R, BOS) vs Seth Lugo 🧤 (R, KC)",
        "description": "Kauffman Stadium — +35% HR row, 79°F, 18 mph blowing out. Lugo's HR suppression (0.48 HR/9 season) fights the park; Gray's modest RHB leak pairs with Kansas City's wind-receptive outfield.",
        "rows": [
            row("Bobby Witt Jr. (R)", "+475", 87, "🚀 🌕 ⚾ 🏟️ 🕊️", "Two HR and two near-HR with 96.3 mph EV and 69.2% hard-hit; Kauffman's +35% HR row plus Gray's RHB lane (0.56 HR-risk for opponents) is the Royals' premium stack.", ["vs Gray", "📜 17-17 vs Gray"], "high"),
            row("Michael Massey (L)", "+850", 84, "🚀 🌕 🏟️", "Two HR and three near-HR with 23.5% barrels and 76.5% HR/FB; Lugo suppresses HR but Massey's pull-air wins in the wind.", ["vs Lugo"], "high"),
            row("Salvador Perez (R)", "+538", 80, "🚀 ⚾ 🏟️", "One HR and two near-HR with 21.4% pull-air; Gray RHB exposure in Kansas City heat.", ["vs Gray", "📜 34-34 vs Gray"]),
            row("Jac Caglianone (L)", "+900", 78, "🚀 💎 🏟️", "One HR with 27.3% barrels and 54.5% hard-hit; Gray LHB lane plus Kauffman carry.", ["vs Gray"], "good"),
            row("Ceddanne Rafaela (R)", "+750", 75, "💎 🏟️", "One HR with pull-air chip; Gray RHB at plus money in the wind.", ["vs Gray"]),
            row("Wilyer Abreu (L)", "+375", 74, "💎", "Modest barrels but Lugo's fly-ball profile is hittable for Boston lefties—price is short.", ["vs Lugo"]),
            row("Mickey Gasper (S)", "+650", 70, "💎", "11.8% barrels and 93.2 mph EV; SHB versus Lugo—bench dart.", ["vs Lugo"]),
        ],
    },
    {
        "title": "MIL @ CHC - Brandon Sproat 🧤 (R, MIL) vs Shota Imanaga (L, CHC)",
        "description": "Wrigley Field — +42% HR row (slate headliner), 76°F, 17 mph out. Sproat's vs-LHB HR-risk (0.45) and 2.00 HR/9 power Milwaukee's lefty pull; Imanaga suppresses RHB (-0.43).",
        "rows": [
            row("Seiya Suzuki (R)", "+375", 90, "🚀 🌕 ⚾ 🏟️ 🕊️", "Two HR and two near-HR with 20% barrels; clear pitcher HR-risk advantage—Sproat's vs-RHB line (-0.01) in Wrigley's +42% HR environment is the Cubs' top righty lane.", ["vs Sproat"], "high"),
            row("Michael Busch (L)", "+358", 88, "🚀 🌕 🏟️", "One HR and two near-HR with 20% barrels and 60% hard-hit; Sproat LHB leakage plus Wrigley wind receptivity.", ["vs Sproat"], "high"),
            row("Michael Conforto (L)", "+449", 86, "🚀 🌕 🏟️", "Two HR and three near-HR with 12.5% barrels and 96.9 mph EV; same Sproat LHB attack in the slate's best HR park row.", ["vs Sproat"], "high"),
            row("Ian Happ (S)", "+359", 82, "🚀 🏟️", "Two near-HR with 20% barrels and 60% hard-hit; SHB uses Imanaga's LHB mix—Happ's K rate is the drag in a strong park.", ["vs Imanaga"]),
            row("Pete Crow-Armstrong (L)", "+500", 79, "🚀 💎 🏟️", "One HR with 22.2% BB rate and pull-side fly balls; Sproat LHB at Wrigley.", ["vs Sproat"]),
            row("Andrew Vaughn (R)", "+378", 77, "🚀 💎", "Micro-sample power versus Imanaga; mostly price and park.", ["vs Imanaga"], "good"),
            row("Jake Bauers (L)", "+820", 74, "💎 🏟️", "One HR with .545 ISO in tiny window; Sproat LHB longshot in Wrigley.", ["vs Sproat"]),
        ],
    },
    {
        "title": "TEX @ COL - Jose Quintana 🧤 (L, TEX) vs MacKenzie Gore (L, COL)",
        "description": "Coors Field — +3% combined HR row at 36°F (Ballpark Pal: weather suppresses carry ~30%). Quintana's vs-LHB HR-risk (1.68) is extreme; Gore is modest overall in the cold.",
        "rows": [
            row("Hunter Goodman (R)", "+361", 83, "🚀 ⚾", "One near-HR with 50% hard-hit; Quintana's vs-RHB suppression (-0.79) is the drag—Goodman's Coors familiarity still grades playable.", ["vs Quintana"]),
            row("Jordan Beck (R)", "+650", 72, "💎", "Modest contact versus Quintana; cold Coors limits ceiling.", ["vs Quintana"]),
            row("Kyle Karros (R)", "+1050", 76, "🚀 💎", "98.5 mph EV and 71.4% hard-hit in small window; Quintana RHB leak at long price.", ["vs Quintana"], "good"),
            row("Mickey Moniak (L)", "+525", 78, "💎", "One HR with 37.5% HR/FB; Gore LHB lane in altitude despite cold air.", ["vs Gore"]),
            row("Jake Burger (R)", "+440", 75, "💎", "One near-HR with 50% hard-hit; Quintana RHB context.", ["vs Quintana"]),
            row("Kyle Higashioka (R)", "+540", 70, "💎", "Modest L5 versus Gore; catcher pop longshot.", ["vs Gore"]),
        ],
    },
    {
        "title": "ATH @ LAA - J.T. Ginn 🧤 (R, ATH) vs Walbert Urena (R, LAA)",
        "description": "Angel Stadium — +3% HR row, 70°F, 9 mph out. Ginn's vs-LHB HR-risk (0.27) helps Oakland lefties; Urena suppresses HR overall (0.66 HR/9).",
        "rows": [
            row("Shea Langeliers (R)", "+333", 94, "🚀 🌕 💣 🧤", "Four HR and four near-HR with 35.3% barrels and 29.6% blast rate; Urena's contact management cannot contain Langeliers' pull-side damage.", ["vs Urena"], "high"),
            row("Brent Rooker (R)", "+425", 86, "🚀 🌕", "One HR and two near-HR with 21.1% barrels and 95.4 mph EV; Urena RHB lane with consistent out-blowing Angel Stadium pattern.", ["vs Urena"], "high"),
            row("Zack Gelof (R)", "+600", 84, "🚀 ⚾", "Two HR and two near-HR with 15.8% barrels; same Urena exposure.", ["vs Urena"], "good"),
            row("Jorge Soler (R)", "+470", 80, "🚀 💎", "One HR and two near-HR with 25% barrels; Ginn LHB suppression is real but Soler's pull loft versus RHP stays live.", ["vs Ginn"], "good"),
            row("Mike Trout (R)", "+390", 78, "💎", "One near-HR with 33.3% pull-air; Ginn RHB line—Trout's K spike is the fade factor.", ["vs Ginn"]),
            row("Yoan Moncada (S)", "+590", 71, "💎", "40% pull-air in window; SHB versus Ginn—mostly longshot.", ["vs Ginn"]),
        ],
    },
    {
        "title": "CHW @ SEA - Noah Schultz (L, CHW) vs Bryan Woo 🧤 (R, SEA)",
        "description": "T-Mobile Park — -21% runs row, dome, 61°F. Woo suppresses HR (1.02 HR/9); Schultz is contact-oriented—White Sox lefty pull is the only real HR path.",
        "rows": [
            row("Munetaka Murakami (L)", "+365", 85, "🚀 🌕 ⚾ 🕊️", "One HR with 99 mph EV and 28.6% barrels; clear pitcher HR-risk advantage—Woo's vs-LHB HR-risk (0.85) is green for batters despite T-Mobile's carry tax.", ["vs Woo"], "high"),
            row("Colson Montgomery (L)", "+439", 83, "🚀 ⚾", "One HR and two near-HR with 18.2% pull-air; Woo LHB lane for Chicago lefty.", ["vs Woo"], "good"),
            row("Miguel Vargas (R)", "+725", 81, "🚀 ⚾", "Two HR and three near-HR with 26.3% barrels; Schultz RHB context at plus money.", ["vs Schultz"], "good"),
            row("Andrew Benintendi (L)", "+725", 78, "🚀 💎", "One HR and two near-HR with 66.7% hard-hit; Woo LHB split.", ["vs Woo"]),
            row("Jarred Kelenic (L)", "+725", 77, "🚀 💎", "33.3% barrels and 101 mph EV; Woo LHB—park fade caps ceiling.", ["vs Woo"]),
            row("Julio Rodriguez (R)", "+500", 76, "💎", "One HR with 62.5% pull; Schultz suppresses RHB—mostly pedigree.", ["vs Schultz"]),
            row("Randy Arozarena (R)", "+525", 73, "💎", "One HR with 58.3% hard-hit; Schultz RHB longshot.", ["vs Schultz"]),
            row("Rob Refsnyder (R)", "+800", 68, "💎", "Modest contact versus Schultz; bench dart.", ["vs Schultz"]),
        ],
    },
    {
        "title": "LAD @ SD - Yoshinobu Yamamoto (R, LAD) vs Michael King 🧤 (R, SD)",
        "description": "Petco Park — -7% HR row, 66°F, 8 mph out. Yamamoto's modest HR-risk (0.31); King's vs-RHB suppression (-0.62) headlines San Diego—Dodgers lefty pull is the cleaner lane.",
        "rows": [
            row("Shohei Ohtani (L)", "+327", 88, "🚀 🌕 ⚾", "One HR and two near-HR with 15% barrels and 40% hard-hit; King's LHB line is softer than his RHB suppression—Ohtani's short price reflects the lane.", ["vs King"], "high"),
            row("Mookie Betts (R)", "+690", 84, "🚀 🌕", "Two HR and three near-HR with 11.8% barrels; King RHB context at Petco.", ["vs King"], "high"),
            row("Will Smith (R)", "+650", 82, "🚀 🌕", "One HR and six near-HR with 35% barrels and 94.8 mph EV; Yamamoto hittable for catcher pop.", ["vs Yamamoto"], "high"),
            row("Andy Pages (R)", "+750", 80, "🚀 💎", "Four HR and four near-HR with 22.2% barrels; Yamamoto fly-ball profile.", ["vs Yamamoto"], "good"),
            row("Jackson Merrill (L)", "+650", 75, "💎", "One near-HR with 54.5% hard-hit; King LHB—favorite tag despite Petco fade.", ["vs King"]),
            row("Manny Machado (R)", "+650", 74, "💎", "One HR with 23.1% pull-air; Yamamoto RHB for Padres.", ["vs Yamamoto", "📜 8-8 vs Yamamoto"]),
            row("Gavin Sheets (L)", "+840", 72, "💎", "Two HR in window; King LHB at long price—duplicate prop angle if rostered.", ["vs King"]),
        ],
    },
    {
        "title": "SF @ ARI - Robbie Ray 🧤 (L, SF) vs Zac Gallen (R, ARI)",
        "description": "Chase Field — roof open, +8% HR row, 85°F, 8 mph. Ray's vs-RHB HR-risk (0.89) and 2.35 HR/9 to righties power Arizona; Gallen is contact-heavy overall.",
        "rows": [
            row("Corbin Carroll (L)", "+650", 82, "🚀 ⚾ 🏟️", "One near-HR with 58.3% hard-hit and 25% pull-air; Ray LHB leakage in Chase heat.", ["vs Ray"], "good"),
            row("Nolan Arenado (R)", "+570", 85, "🚀 📜 🏟️", "One near-HR with 50% hard-hit; clear Ray RHB HR-risk (0.89) plus BvP (3-43, .790 SLG).", ["vs Ray", "📜 3-43 vs Ray"], "good"),
            row("Rafael Devers (L)", "+500", 83, "🚀 ⚾ 📜", "One HR and two near-HR with 50% hard-hit; Ray LHB lane in open-roof Chase.", ["vs Ray", "📜 1-9 vs Ray"], "good"),
            row("Willy Adames (R)", "+650", 80, "🚀 💎", "Two near-HR with 50% hard-hit and 94 mph EV; Ray RHB split is the D-backs' primary HR path.", ["vs Ray"], "good"),
            row("Gabriel Moreno (R)", "+875", 76, "💎", "One HR and two near-HR with 50% HR/FB; Ray RHB at long price.", ["vs Ray"]),
            row("Casey Schmitt (R)", "+650", 72, "💎", "31.2% HR/FB in window; Ray RHB exposure.", ["vs Ray"]),
            row("Harrison Bader (R)", "+1200", 70, "💎", "One HR and three near-HR with 35.3% pull-air; Ray RHB longshot.", ["vs Ray"]),
            row("Eric Haase (R)", "+900", 71, "💎", "One HR with .700 SLG in micro-sample; Ray RHB.", ["vs Ray"]),
            row("Luis Arraez (L)", "+1800", 68, "💎", "One HR with .571 SLG; Ray LHB at extreme long price in hitter-friendly air.", ["vs Ray"]),
        ],
    },
]

PROP_NAMES = [
    "Yandy Diaz", "Junior Caminero", "Pete Alonso", "Samuel Basallo", "Coby Mayo",
    "Kyle Schwarber", "Alec Bohm", "Adolis Garcia", "J.T. Realmuto", "Matt McLain",
    "JJ Bleday", "Elly De La Cruz", "Tyler Stephenson", "Will Benson", "Jakob Marsee",
    "Otto Lopez", "Xavier Edwards", "Austin Riley", "Matt Olson", "Mike Yastrzemski",
    "Dillon Dingler", "Rhys Hoskins", "Travis Bazzana", "James Wood", "Jose Tena",
    "Mark Vientos", "Juan Soto", "MJ Melendez", "Trent Grisham", "Paul Goldschmidt",
    "Amed Rosario", "Jazz Chisholm Jr.", "Kazuma Okamoto", "Ernie Clement", "George Springer",
    "Byron Buxton", "Tristan Gray", "Ryan Jeffers", "Yordan Alvarez", "Zach Dezenzo",
    "Brice Matthews", "Michael Massey", "Bobby Witt Jr.", "Jac Caglianone", "Salvador Perez",
    "Mickey Gasper", "Ceddanne Rafaela", "Wilyer Abreu", "Ian Happ", "Seiya Suzuki",
    "Michael Busch", "Michael Conforto", "Pete Crow-Armstrong", "Jake Bauers", "Andrew Vaughn",
    "Hunter Goodman", "Jordan Beck", "Kyle Karros", "Mickey Moniak", "Jake Burger",
    "Kyle Higashioka", "Jorge Soler", "Mike Trout", "Yoan Moncada", "Shea Langeliers",
    "Brent Rooker", "Zack Gelof", "Julio Rodriguez", "Randy Arozarena", "Rob Refsnyder",
    "Munetaka Murakami", "Miguel Vargas", "Colson Montgomery", "Andrew Benintendi", "Jarred Kelenic",
    "Gavin Sheets", "Jackson Merrill", "Manny Machado", "Andy Pages", "Mookie Betts",
    "Will Smith", "Shohei Ohtani", "Corbin Carroll", "Nolan Arenado", "Gabriel Moreno",
    "Casey Schmitt", "Harrison Bader", "Eric Haase", "Rafael Devers", "Luis Arraez", "Willy Adames",
]

found = set()
for g in games:
    for r in g["rows"]:
        base = r["name"].split(" (")[0]
        found.add(base)
        if "J.T." in r["name"]:
            found.add("J.T. Realmuto")
        if "Bobby Witt" in r["name"]:
            found.add("Bobby Witt Jr.")

missing = [n for n in PROP_NAMES if n not in found]
if missing:
    raise SystemExit(f"Missing props: {missing}")

for g in games:
    for r in g["rows"]:
        apply_inferred_due(r, g)

if STATCAST_PATH.is_file():
    statcast = json.loads(STATCAST_PATH.read_text(encoding="utf-8"))
    for g in games:
        for r in g["rows"]:
            extra = statcast.get(r["name"])
            if extra:
                existing = r.get("due") or {}
                for k, v in extra.items():
                    if not str(k).startswith("_"):
                        existing[k] = v
                r["due"] = existing

overdue_names = tag_games_overdue(games)
print(f"Overdue (💤) tagged: {len(overdue_names)} — {', '.join(overdue_names) or 'none'}")

def js_str(s):
    return json.dumps(s, ensure_ascii=False)

lines = ["            const games = ["]
for g in games:
    lines.append(f'                {{ title: {js_str(g["title"])}, description: {js_str(g["description"])}, rows: [')
    for r in g["rows"]:
        blast = f', blast: {js_str(r["blast"])}' if r.get("blast") else ""
        overdue = ", overdue: true" if r.get("overdue") else ""
        chips = ", ".join(js_str(c) for c in r["chips"])
        lines.append(
            f'                    {{ name: {js_str(r["name"])}, odds: {js_str(r["odds"])}, score: {r["score"]}, emojis: {js_str(r["emojis"])}{blast}{overdue}, note: {js_str(r["note"])}, chips: [{chips}] }},'
        )
    lines.append("                ]},")
lines.append("            ];")
out = "\n".join(lines)
(ROOT / "_games-0518.txt").write_text(out + "\n", encoding="utf-8")
print(f"Wrote {len(found)} players across {len(games)} games")
print(out[:500], "...")
