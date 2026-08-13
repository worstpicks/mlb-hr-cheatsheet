#!/usr/bin/env python3
"""Map the 8/13 prop list against available CSV coverage before building."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-08-13"

PROPS = """Griffin Conine⭐
Owen Caissie
Brandon Lowe💎
Jacob Gonzalez
Endy Rodriguez⭐
Eduardo Valencia
James Outman
Dillon Dingler
Jo Adell
Rhys Hoskins💎
Nathaniel Lowe💎
Angel Genao
Chase DeLauter
Ben Rice⭐
Trent Grisham
Spencer Jones💎
Heliot Ramos
Munetaka Murakami⭐
Miguel Vargas💎
Tyler Stephenson💎
JJ Bleday
Kazuma Okamoto
Alejandro Kirk
Ernie Clement
Jarren Duran💎
Wilyer Abreu
Brady House
Dylan Crews💎
Abimelec Ortiz
Daylen Lile
Keibert Ruiz
Kody Clemens⭐
Josh Bell
Royce Lewis
Victor Caratini
Bryce Harper⭐
Kyle Schwarber⭐
Derek Hill
Bryson Stott
Bryan De La Cruz
Moises Ballesteros
Mike Trout
Travis d'Arnaud
Vaughn Grissom
Ezequiel Duran
Joc Pederson💎
Corey Seager
Teoscar Hernandez
Mookie Betts
Andy Pages
Endy Hernandez
Kyle Tucker
Jackson Chourio⭐
William Contreras💎
Brice Turang⭐
Jake Bauers
Garrett Mitchell""".splitlines()


def key(name: str) -> str:
    n = name.replace("\u2b50", "").replace("\U0001f48e", "").strip()
    n = re.sub(r"^\d+\s+", "", n)
    n = re.sub(r"\s+(LHB|RHB|SHB)$", "", n)
    n = n.lower().replace(".", "").replace("'", "").replace("\u2019", "")
    return re.sub(r"\s+", " ", n).strip()


def main() -> None:
    # Batters present in matchup CSVs, by game
    matchup_batters: dict[str, set[str]] = {}
    for path in sorted(DATA.glob(f"hr-matchups-*-{DATE}.csv")):
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        game = lines[0].split(",", 1)[1].strip() if lines else "?"
        hdr_i = next(
            (i for i, l in enumerate(lines) if l.split(",")[0].strip().upper() == "BATTER"),
            None,
        )
        if hdr_i is None:
            continue
        rdr = csv.reader(lines[hdr_i + 1 :])
        for row in rdr:
            if row and row[0].strip():
                matchup_batters.setdefault(game, set()).add(key(row[0]))

    all_matchup = set().union(*matchup_batters.values()) if matchup_batters else set()

    zone_batters: set[str] = set()
    zone_by_pitcher: dict[str, set[str]] = {}
    with (DATA / f"zone-matchups-{DATE}.csv").open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            b = key(row["Batter"])
            zone_batters.add(b)
            zone_by_pitcher.setdefault(row["Pitcher"], set()).add(b)

    print(f"matchup CSV games: {len(matchup_batters)} | batters: {len(all_matchup)}")
    print(f"zone batters: {len(zone_batters)} | zone pitchers: {len(zone_by_pitcher)}\n")

    missing_both, zone_only, ok = [], [], []
    for p in PROPS:
        k = key(p)
        in_m = k in all_matchup
        in_z = k in zone_batters
        if in_m:
            ok.append(p)
        elif in_z:
            zone_only.append(p)
        else:
            missing_both.append(p)

    print(f"in matchup CSV ({len(ok)}): fine\n")
    print(f"ZONE ONLY - need synthetic matchup row ({len(zone_only)}):")
    for p in zone_only:
        k = key(p)
        pit = [pt for pt, bs in zone_by_pitcher.items() if k in bs]
        print(f"  {p:24} vs {pit}")
    print(f"\nMISSING EVERYWHERE ({len(missing_both)}):")
    for p in missing_both:
        print(f"  {p}")

    # near-miss suggestions for the fully-missing names
    if missing_both:
        print("\nclosest names in CSVs (alias candidates):")
        pool = sorted(all_matchup | zone_batters)
        for p in missing_both:
            k = key(p)
            last = k.split()[-1]
            first = k.split()[0]
            cands = [c for c in pool if last in c or (len(first) > 3 and first in c)]
            print(f"  {p:24} -> {cands[:6]}")


if __name__ == "__main__":
    main()
