#!/usr/bin/env python3
from pathlib import Path
from csv_slate_meta import derive_games_from_csv, name_lookup_key
import re

ROOT = Path(__file__).resolve().parent
DATE = "2026-07-31"

needed = [
    "hr-matchups-KC-at-COL-Michael-Wacha-2026-07-31.csv",
    "hr-matchups-WSH-at-ATL-Foster-Griffin-2026-07-31.csv",
    "hr-matchups-BOS-at-LAD-Ranger-Suarez-2026-07-31.csv",
    "hr-matchups-BOS-at-LAD-Yoshinobu-Yamamoto-2026-07-31.csv",
]
dl = Path.home() / "Downloads"
for n in needed:
    print(f"{n}: DL={(dl/n).exists()} DATA={(ROOT/'data'/n).exists()}")

print("\nOther DL hits:")
for p in sorted(dl.glob(f"*{DATE}*")):
    if any(x in p.name for x in ("BOS", "LAD", "Wacha", "Griffin", "Yamamoto", "Suarez", "KC-at-COL")):
        print(" ", p.name)

games = derive_games_from_csv(DATE)
print(f"\ngames {len(games)}")
for g in sorted(games, key=lambda x: x["key"]):
    print(
        f"{g['key']:12} | {g['away_sp_full']:22} vs {g['home_sp_full']:22} | batters {len(g['batters'])}"
    )

RAW = """Pete Crow Armstrong⭐
Miguel Amaya
Justin Dean
Ben Rice
Spencer Jones
Jazz Chisholm Jr.
Austin Wells
Elly De La Cruz⭐
Matt McLain
Eugenio Suarez
Bryan Reynolds⭐
Esmerlyn Valdez
Endy Rodriguez
Brandon Lowe
Gunnar Henderson💎
Dylan Beavers
Coby Mayo💎
Tyler O'Neill
Bryce Harper
Derek Hill💎
Trea Turner
George Springer💎
Brandon Valenzuela
Jimmy Crooks💎
Alec Burleson
Victor Mesa Jr.⭐
Junior Caminero
Munetaka Murakami
Sam Antonacci
Colson Montgomery
Brett Baty⭐
Francisco Alvarez
Joe Mack
Griffin Conine
Kyle Stowers⭐
Heriberto Hernandez
Travis Bazzana
Rhys Hoskins
Brayan Rocchio
Corbin Carroll
Austin Riley
Matt Olson
Ozzie Albies
Luis Garcia Jr.⭐
James Wood
Daylen Lile
Yordan Alvarez
Taylor Trammell💎
Joc Pederson
Wyatt Langford
Alejandro Osuna
Hunter Goodman💎
Willi Castro💎
Mickey Moniak
Carter Jensen
Salvador Perez
Starling Marte 
John Rave
Zach Neto
Travis d'Arnaud
Jo Adell💎
Jake Bauers💎
Andrew Vaughn
Christian Yelich
Nick Kurtz💎
Tyler Soderstrom💎
Lawrence Butler⭐
Tommy White
Hao Yu lee
James Outman
Eduardo Valencia
Dillon Dingler
Manny Machado💎
Fernando Tatis Jr.
Ty France
Jackson Merrill
Drew Gilbert
Rafael Devers
Bryce Eldridge
Grant McCray
Luke Raley
Randy Arozarena
Mitch Garver
Rob Refsnyder💎
Kody Clemens⭐
Ryan Jeffers
Royce Lewis💎""".strip().splitlines()

batters = {}
for g in games:
    for k, b in g["batters"].items():
        batters[k] = (b["name"], g["key"], b["vs"])

missing = []
found = 0
for line in RAW:
    name = re.sub(r"[⭐💎]", "", line).strip()
    if not name:
        continue
    # normalize Crow-Armstrong / Hao-Yu
    aliases = {
        "Pete Crow Armstrong": "Pete Crow-Armstrong",
        "Hao Yu lee": "Hao-Yu Lee",
        "Hao Yu Lee": "Hao-Yu Lee",
        "Travis d'Arnaud": "Travis d'Arnaud",
        "Starling Marte": "Starling Marte",
    }
    name = aliases.get(name, name)
    k = name_lookup_key(name)
    if k in batters:
        found += 1
    else:
        missing.append(name)

print(f"\nprops found {found} missing {len(missing)}")
for m in missing:
    print(" MISS", m)
