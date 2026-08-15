#!/usr/bin/env python3
"""Pre-build probe for 2026-08-15: prop coverage, zone gaps, pitcher conflicts."""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-15"

RAW = """Eduardo Valencia💎
Gleyber Torres
Munetaka Murakami⭐
Colson Montgomery💎
Andrew Benintendi
Btaden Montgomery
Ian Happ
Miguel Amaya💎
Pete Crow Armstrong💎
Michael Conforto
Jordan Walker⭐
Ivan Herrera
Jimmy Crooks
Jose Fermin
Jesus Sanchez⭐
Vladimir Guerrero Jr.
Ernie Clement
Trent Grisham
Jazz Chisholm Jr.
Luis Garcia Jr.
Spencer Jones
Ben Rice⭐
Heliot Ramos
Jung Hoo Lee
Bryce Eldridge💎
Rafael Devers
Zac Veen💎
Willi Castro
Hunter Goodman
Mickey Moniak
Brett Baty💎
Francisco Lindor
Jorge Polanco
Daylen Lile
Brady House
Andrew Pinckney
Dylan Crews
Jonathan Aranda
Victor Mesa Jr.
Junior Caminero
Gunnar Henderson💎
Christian Encarnacion-Strand
Coby Mayo💎
Pete Alonso⭐
Jeremiah Jackson
Tyler Stephenson💎
Eugenio Suarez
Sal Stewart
Griffin Conine⭐
Heriberto Hernandez
Owen Caissie
Joe Mack
Royce Lewis⭐
Byron Buxton
Austin Martin
Victor Caratini
Bryson Stott
Kyle Schwarber
Trea Turner
JT Realmuto💎
Bryce Harper
Yordan Alvarez⭐
Taylor Trammell💎
Daulton Varsho
Nelson Velazquez
Dominic Canzone⭐
Cal Raleigh
Josh Naylor
Julio Rodriguez
Randy Arozarena
Nathaniel Lowe
Chase DeLauter💎
Jo Adell
Rhys Hoskins
Jase Bowen
Fernando Tatis Jr.💎
Jackson Merrill⭐
Manny Machado💎
Jacob Gonzalez
Brandon Lowe💎
Jake Mangum
Connor Wong
Jarren Duran💎
Wilyer Abreu
Shohei Ohtani
Hunter Feduccia
Teoscar Hernandez
Max Muncy
Andrew Vaughn💎
Jake Bauers
Jackson Chourio⭐
Gary Sanchez
Ozzie Albies
Matt Olson
Lane Thomas
Austin Riley⭐
Jim Jarvis
Corbin Carroll⭐
Lars Nootbaar💎
Travis d'Arnaud
Moises Ballesteros
Josh lowe
Jac Caglianone⭐
Carter Jensen💎
Salvador Perez
Tyler Soderstrom💎
Jonah Heim
Henry Bolte
Zack Gelof
Joc Pederson💎
Corey Seager⭐
Wyatt Langford"""

# Projected starters from the user's lineups (game -> [away SP, home SP]).
PROJECTED = {
    "CWS @ DET": ["Anthony Kay", "Troy Melton"],
    "STL @ CHC": ["Michael McGreevy", "Matthew Boyd"],
    "NYY @ TOR": ["Cam Schlittler", "Simeon Woods Richardson"],
    "COL @ SF": ["Michael Lorenzen", "Logan Webb"],
    "WSH @ NYM": ["Brad Lord", "Sean Manaea"],
    "BAL @ TB": ["Kyle Bradish", "Ian Seymour"],
    "MIA @ CIN": ["Ryan Gusto", "Brady Singer"],
    "SD @ CLE": ["Randy Vasquez", "Joey Cantillo"],
    "PHI @ MIN": ["Jesus Luzardo", "Connor Prielipp"],
    "SEA @ HOU": ["Emerson Hancock", "Hayden Wesneski"],
    "ARI @ ATL": ["Eduardo Rodriguez", "Grant Holmes"],
    "MIL @ LAD": ["Jacob Misiorowski", "Justin Wrobleski"],
    "BOS @ PIT": ["Sonny Gray", "Jared Jones"],
    "KC @ LAA": ["Randy Dobnak", "Reid Detmers"],
    "TEX @ ATH": ["MacKenzie Gore", "J.T. Ginn"],
}


def key(name: str) -> str:
    base = unicodedata.normalize("NFKD", name or "")
    base = "".join(c for c in base if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", base.lower())


def clean_prop(line: str) -> tuple[str, str]:
    emo = "".join(c for c in line if c in "\u2b50\U0001f48e")
    name = re.sub(r"[\u2b50\U0001f48e]", "", line).strip()
    return name, emo


def read_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    hi = next((i for i, l in enumerate(lines) if "BATTER" in l.upper()), None)
    if hi is None:
        return [], []
    hdr = next(csv.reader([lines[hi]]))
    out = []
    for l in lines[hi + 1 :]:
        r = next(csv.reader([l]), None)
        if r and any(c.strip() for c in r):
            out.append(r)
    return hdr, out


def norm_batter(raw: str) -> str:
    v = re.sub(r"^\d+\s+", "", (raw or "").strip())
    v = re.sub(r"\s+(LHB|RHB|SHB)$", "", v).strip()
    return v


def main() -> None:
    props = [clean_prop(l) for l in RAW.splitlines() if l.strip()]
    print(f"props listed: {len(props)}")
    favs = [n for n, e in props if "\u2b50" in e]
    gems = [n for n, e in props if "\U0001f48e" in e]
    print(f"  favorites {len(favs)} · hidden gems {len(gems)}")

    # Batter -> (game, pitcher) from matchup CSVs
    found: dict[str, list[tuple[str, str]]] = {}
    zone_present: dict[str, str] = {}
    for f in sorted((ROOT / "data").glob(f"hr-matchups-*-{DATE}.csv")):
        m = re.match(rf"hr-matchups-(.+?)-at-(.+?)-(.+)-{DATE}\.csv", f.name)
        if not m:
            continue
        game = f"{m.group(1)} @ {m.group(2)}"
        pitcher = m.group(3).replace("-", " ")
        hdr, rows = read_rows(f)
        bi = next((i for i, c in enumerate(hdr) if "BATTER" in c.upper()), 0)
        zi = next((i for i, c in enumerate(hdr) if c.strip().upper() == "ZONE"), None)
        for r in rows:
            if len(r) <= bi:
                continue
            nm = norm_batter(r[bi])
            if not nm:
                continue
            found.setdefault(key(nm), []).append((game, pitcher))
            if zi is not None and len(r) > zi and r[zi].strip() not in ("", "-"):
                zone_present[key(nm)] = r[zi].strip()

    zpath = ROOT / "data" / f"zone-matchups-{DATE}.csv"
    zhdr, zrows = read_rows(zpath)
    zbi = next((i for i, c in enumerate(zhdr) if "BATTER" in c.upper()), 0)
    zzi = next((i for i, c in enumerate(zhdr) if c.strip().upper() == "ZONE"), None)
    zone_file: set[str] = set()
    for r in zrows:
        if len(r) > zbi:
            nm = norm_batter(r[zbi])
            if nm and (zzi is None or (len(r) > zzi and r[zzi].strip() not in ("", "-"))):
                zone_file.add(key(nm))

    print("\n=== PROPS NOT FOUND IN ANY MATCHUP CSV ===")
    missing = [(n, e) for n, e in props if key(n) not in found]
    if missing:
        for n, e in missing:
            cands = [k for k in found if key(n.split()[-1]) in k or k.endswith(key(n.split()[-1]))]
            hint = ""
            if cands:
                hint = "  ~ " + ", ".join(sorted(cands)[:3])
            print(f"  MISSING {n}{e}{hint}")
    else:
        print("  none")

    print("\n=== PROPS MISSING ZONE DATA ===")
    nozone = [
        (n, e) for n, e in props if key(n) in found and key(n) not in zone_file and key(n) not in zone_present
    ]
    for n, e in nozone:
        print(f"  no zone: {n}{e}  ({found[key(n)][0][0]} vs {found[key(n)][0][1]})")
    print(f"  total without zone: {len(nozone)}")

    print("\n=== DUPLICATE GAME ASSIGNMENTS ===")
    for n, e in props:
        hits = found.get(key(n)) or []
        if len({g for g, _ in hits}) > 1:
            print(f"  {n}: {sorted({g for g, _ in hits})}")

    print("\n=== PITCHER CONFLICTS vs PROJECTED LINEUPS ===")
    exported: dict[str, set[str]] = {}
    for f in sorted((ROOT / "data").glob(f"hr-matchups-*-{DATE}.csv")):
        m = re.match(rf"hr-matchups-(.+?)-at-(.+?)-(.+)-{DATE}\.csv", f.name)
        if m:
            exported.setdefault(f"{m.group(1)} @ {m.group(2)}", set()).add(
                m.group(3).replace("-", " ")
            )
    for game, sps in PROJECTED.items():
        got = exported.get(game, set())
        got_keys = {key(g) for g in got}
        for sp in sps:
            if key(sp) not in got_keys:
                print(f"  {game}: projected '{sp}' NOT exported; export has {sorted(got)}")

    print("\n=== HR RISK / SUMMARY COVERAGE FOR STARTERS ===")
    risk_names = set()
    tp = ROOT / "data" / f"hr-targets-overall-{DATE}.csv"
    lines = tp.read_text(encoding="utf-8-sig").splitlines()
    hi = next((i for i, l in enumerate(lines) if "PITCHER" in l.upper()), None)
    if hi is not None:
        hdr = next(csv.reader([lines[hi]]))
        pi = next((i for i, c in enumerate(hdr) if "PITCHER" in c.upper()), 0)
        for l in lines[hi + 1 :]:
            r = next(csv.reader([l]), None)
            if r and len(r) > pi and r[pi].strip():
                risk_names.add(key(r[pi]))
    summ = set()
    for f in (ROOT / "data").glob(f"pitcher-summary-*-{DATE}.csv"):
        ls = f.read_text(encoding="utf-8-sig").splitlines()
        h = next((i for i, l in enumerate(ls) if "PITCHER" in l.upper() or "NAME" in l.upper()), None)
        if h is None:
            continue
        hd = next(csv.reader([ls[h]]))
        pi = next((i for i, c in enumerate(hd) if "PITCHER" in c.upper() or "NAME" in c.upper()), 0)
        for l in ls[h + 1 :]:
            r = next(csv.reader([l]), None)
            if r and len(r) > pi and r[pi].strip():
                summ.add(key(r[pi]))
    for game, sps in sorted(exported.items()):
        for sp in sorted(sps):
            flags = []
            if key(sp) not in risk_names:
                flags.append("no HR risk")
            if key(sp) not in summ:
                flags.append("no summary")
            if flags:
                print(f"  {game:11} {sp:24} {', '.join(flags)}")

    print(f"\nsummary: {len(props)} props · {len(missing)} missing · {len(nozone)} without zone")


if __name__ == "__main__":
    main()
