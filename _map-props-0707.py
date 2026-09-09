#!/usr/bin/env python3
"""One-off: map 7/7 user props to CSV games."""
from csv_slate_meta import derive_games_from_csv, name_lookup_key

DATE = "2026-07-07"
games = {g["key"]: g for g in derive_games_from_csv(DATE)}

PROPS = [
    "Pete Alonso",
    "Taylor Ward",
    "Pete Crow-Armstrong",
    "Junior Caminero",
    "Jonathan Aranda",
    "Ben Rice",
    "Trent Grisham",
    "Max Schuemann",
    "Jazz Chisholm Jr.",
    "Brandon Lowe",
    "Ryan O'Hearn",
    "Tyler Callihan",
    "Matt Olson",
    "Michael Harris II",
    "Drake Baldwin",
    "Kyle Stowers",
    "Otto Lopez",
    "Owen Caissie",
    "Joe Mack",
    "Cal Raleigh",
    "Randy Arozarena",
    "Josh Naylor",
    "Riley Greene",
    "Kerry Carpenter",
    "Nick Kurtz",
    "Colby Thomas",
    "Jonah Heim",
    "Luis Garcia Jr.",
    "James Wood",
    "CJ Abrams",
    "Yordan Alvarez",
    "Juan Soto",
    "Jac Caglianone",
    "Carter Jensen",
    "Sal Stewart",
    "Matt McLain",
    "Trea Turner",
    "Alec Bohm",
    "Byron Buxton",
    "Victor Caratini",
    "Josh Bell",
    "Kyle Manzardo",
    "Austin Hedges",
    "Miguel Vargas",
    "Colson Montgomery",
    "Randal Grichuk",
    "Wilyer Abreu",
    "Willson Contreras",
    "Jarren Duran",
    "Lars Nootbaar",
    "JJ Wetherholt",
    "Nelson Velazquez",
    "Jordan Walker",
    "Jake Bauers",
    "Jackson Chourio",
    "Garrett Mitchell",
    "Jake Burger",
    "Brandon Nimmo",
    "Joc Pederson",
    "Josh Smith",
    "Jo Adell",
    "Zach Neto",
    "Josh Lowe",
    "Manny Machado",
    "Ty France",
    "Max Kepler",
    "Ketel Marte",
    "Heliot Ramos",
    "Kazuma Okamoto",
    "Brandon Valenzuela",
    "Mookie Betts",
    "Freddie Freeman",
    "Hunter Goodman",
]

ctx = {}
for g in games.values():
    for row in g["batters"].values():
        key = name_lookup_key(row["name"])
        vs = row["vs"]
        team = g["home"] if vs == g["away_sp"] else g["away"]
        ctx.setdefault(key, (row["name"], g["key"], team, vs))

found, missing = [], []
for p in PROPS:
    k = name_lookup_key(p)
    if k in ctx:
        found.append((p, ctx[k]))
    else:
        missing.append(p)

print("GAMES:", sorted(games))
for g in sorted(games.values(), key=lambda x: x["key"]):
    print(f"  {g['key']}: {g['away_sp_full']} vs {g['home_sp_full']}")
print("FOUND", len(found))
for p, (n, gkey, t, sp) in sorted(found, key=lambda x: x[1][1]):
    print(f"  {p:24} -> {gkey} vs {sp} ({t})")
print("MISSING", len(missing))
for p in missing:
    print(" ", p)
