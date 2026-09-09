#!/usr/bin/env python3
from csv_slate_meta import derive_games_from_csv, name_lookup_key

DATE = "2026-06-27"
games = {g["key"]: g for g in derive_games_from_csv(DATE)}
batter_ctx = {}
for g in games.values():
    for row in g["batters"].values():
        vs = row["vs"]
        if vs == g["away_sp"]:
            team = g["home"]
        elif vs == g["home_sp"]:
            team = g["away"]
        else:
            continue
        key = name_lookup_key(row["name"])
        batter_ctx[key] = (row["name"], g["key"], vs)

RAW = """
Junior Caminero⭐
Victor Mesa Jr.💎
Corbin Carroll
Tommy Troy
Pete Alonso
Coby Mayo
James Wood
Khalil Watson
Luke Raley
Dominic Canzone
Byron Buxton⭐
Victor Caratini
Kody Clemens
Mickey Moniak
Hunter Goodman
Jackson Chourio
William Contreras⭐
Seiya Suzuki⭐
Ian Happ
Lars Nootbaar
Ivan Herrera
Jimmy Crooks
Griffin Conine
Kyle Stowers
Owen Caissie⭐
Heriberto Hernandez
Manny Machado⭐
Ty France
Shohei Ohtani⭐
Max Muncy(LAD)⭐
Max Muncy(ATH)⭐
Mookie Betts⭐
Rafael Devers⭐
Casey Schmitt
Matt Olson
Jorge Mateo
Mike Yastrzemski
Rowdy Tellez⭐
Logan O Hoppe⭐
Denzer Guzman💎
Zach Neto⭐
Jorge Soler💎
Nick Kurtz⭐
Henry Bolte
""".strip().splitlines()

ALIASES = {
    "Khalil Watson": "Kahlil Watson",
    "Logan O Hoppe": "Logan O'Hoppe",
    "Max Muncy(LAD)": "Max Muncy",
    "Max Muncy(ATH)": "Max Muncy",
}

GAME_OV = {
    "Max Muncy(LAD)": "LAD @ SD",
    "Max Muncy(ATH)": "ATH @ LAA",
}

missing = []
for raw in RAW:
    clean = raw.replace("⭐", "").replace("💎", "").strip()
    for prefix in ("Max Muncy(LAD)", "Max Muncy(ATH)"):
        if clean.startswith(prefix):
            clean = prefix
            break
    nm = ALIASES.get(clean, clean)
    k = name_lookup_key(nm.split("(")[0] if "Max Muncy" in nm else nm)
    gk = GAME_OV.get(clean)
    found = False
    if gk:
        for key, val in batter_ctx.items():
            if key == name_lookup_key("Max Muncy") and val[1] == gk:
                print("OK", raw, "->", val)
                found = True
                break
    elif k in batter_ctx:
        print("OK", raw, "->", batter_ctx[k])
        found = True
    if not found:
        missing.append(raw)
        print("MISSING", raw)

print("missing count", len(missing))
