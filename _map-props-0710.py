#!/usr/bin/env python3
"""One-off: map 7/10 user props to CSV games."""
from csv_slate_meta import derive_games_from_csv, name_lookup_key

DATE = "2026-07-10"
games = {g["key"]: g for g in derive_games_from_csv(DATE)}

PROPS = [
    "Riley Greene",
    "Kyle Schwarber",
    "Edmundo Sosa",
    "Bryan Reynolds",
    "Ryan O'Hearn",
    "Esmerlyn Valdez",
    "Brandon Lowe",
    "Jake Bauers",
    "Garrett Mitchell",
    "Brice Turang",
    "James Wood",
    "Curtis Mead",
    "Dylan Crews",
    "Ben Rice",
    "Austin Wells",
    "Max Schuemann",
    "Trent Grisham",
    "Pete Alonso",
    "Tyler O'Neill",
    "Samuel Basallo",
    "Jac Caglianone",
    "Michael Massey",
    "Lane Thomas",
    "Sal Stewart",
    "Elly De La Cruz",
    "Pete Crow Armstrong",
    "Seiya Suzuki",
    "Ian Happ",
    "Michael Conforto",
    "Hunter Feduccia",
    "Dominic Canzone",
    "Cole Young",
    "Mitch Garver",
    "Heriberto Hernandez",
    "Griffin Conine",
    "Leo Jimenez",
    "Rhys Hoskins",
    "Juan Soto",
    "AJ Ewing",
    "Wilyer Abreu",
    "Jarren Duran",
    "Kyle Teel",
    "Junior Perez",
    "Nick Kurtz",
    "Shea Langeliers",
    "Brandon Nimmo",
    "Joc Pederson",
    "Yordan Alvarez",
    "Taylor Trammell",
    "Christian Walker",
    "Kody Clemens",
    "Josh Bell",
    "Mike Trout",
    "Josh Lowe",
    "Jordan Walker",
    "Nelson Velazquez",
    "Matt Olson",
    "Joey Bart",
    "Drake Baldwin",
    "Mike Yastrzemski",
    "Manny Machado",
    "Fernando Tatis Jr.",
    "Luis Campusano",
    "Kazuma Okamoto",
    "George Springer",
    "Shohei Ohtani",
    "Max Muncy",
    "Dalton Rushing",
    "Mookie Betts",
    "Max Kepler",
    "Ketel Marte",
    "Corbin Carroll",
    "Rafael Devers",
    "Heliot Ramos",
    "Bryce Eldridge",
    "Victor Bericoto",
    "Hunter Goodman",
    "Edouard Julien",
]

ALIASES = {
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "AJ Ewing": "A.J. Ewing",
    "Fernando Tatis Jr.": "Fernando Tatis Jr.",
    "Mike Yastrzemski": "Mike Yastrzemski",
}

ctx = {}
for g in games.values():
    for row in g["batters"].values():
        key = name_lookup_key(row["name"])
        vs = row["vs"]
        team = g["home"] if vs == g["away_sp"] else g["away"]
        ctx.setdefault(key, (row["name"], g["key"], team, vs))

found, missing = [], []
for p in PROPS:
    clean = ALIASES.get(p, p)
    k = name_lookup_key(clean)
    if k in ctx:
        found.append((p, ctx[k]))
    else:
        missing.append(p)

print("GAMES:", sorted(games))
for g in sorted(games.values(), key=lambda x: x["key"]):
    print(f"  {g['key']}: {g['away_sp_full']} vs {g['home_sp_full']} ({len(g['batters'])})")
print("FOUND", len(found))
for p, (n, gkey, t, sp) in sorted(found, key=lambda x: x[1][1]):
    print(f"  {p:24} -> {gkey} vs {sp} ({t})")
print("MISSING", len(missing))
for p in missing:
    print(" ", p)
