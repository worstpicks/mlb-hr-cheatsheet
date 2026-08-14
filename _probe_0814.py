"""Coverage probe for the 8/14 slate.

Checks every user-listed prop against the imported hr-matchups / zone-matchups
exports so naming problems surface before the build instead of as dropped rows.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

DATE = "2026-08-14"
ROOT = Path(__file__).resolve().parent

# Gage Jump is deliberately absent: he is the ATH starting pitcher, not a bat.
RAW = """Tyler Stephenson💎
Matt McLain
Eugenio Suarez
Sal Stewart
Griffin Conine⭐
Joe Mack
Owen Caissie
Ronny Simon
Bryan Reynolds💎
Esmerlyn Valdez
Jarren Duran
Wilyer Abreu
Eduardo Valencia
Gleyber Torres
Spencer Torkleson
Munetaka Murakami⭐
Drew Romo
Randal Grichuk
Victor Mesa Jr.💎
Yandy Diaz
Jonathan Aranda💎
Junior Caminero
Pete Alonso⭐
Coby Mayo⭐
Francisco Alvarez💎
Carson Benge
A.J Ewing
Luis Robert⭐
Daylen Lile⭐
Abimelec Ortiz⭐
Jose Tena
Angel Genao💎
Nathaniel Lowe
Patrick Bailey
Chase DeLauter
Jackson Merrill⭐
Manny Machado
Xander Bogaerts
Fernando Tatis Jr.
Jesus Sanchez
Kazuma Okamoto
George Springer
Ben Rice
Spencer Jones
Jazz Chisholm Jr.
Luis Garcia Jr.
Matt Olson
Drake Baldwin💎
Ronald Acuna
Michael Harris II
Daulton Varsho💎
Taylor Trammell
Yordan Alvarez⭐
Nelson Velazquez
Cam Smith
Julio Rodriguez
Dominic Canzone💎
Josh Naylor💎
Mike Trout⭐
Moises Ballesteros
Jac Caglianone⭐
Salvador Perez
Bobby Witt Jr.
Isaac Collins
Lawrence Butler⭐
Tyler Soderstrom💎
Henry Bolte
Zack Gelof
Justin Foscue
Elias Diaz
Teoscar Hernandez💎
Mookie BEtts
Shohei Ohtani💎
Andy Pages
Jake Bauers💎
Brice Turang
William Contreras💎
Joey Ortiz
Rafael Devers
Bryce Eldridge
Victor Bericoto
Willy Adames
Zac Veen
Willi Castro
Hunter Goodman⭐"""


def fold(s: str) -> str:
    s = re.sub(r"\s+(LHB|RHB|SHB)$", "", s.strip())
    s = re.sub(r"^\d+\s+", "", s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace(".", "").replace("'", "").replace("’", "")
    return re.sub(r"\s+", " ", s).strip()


def strip_marks(s: str) -> str:
    return s.replace("⭐", "").replace("💎", "").strip()


def main() -> None:
    props = [strip_marks(x) for x in RAW.splitlines() if x.strip()]
    stars = {strip_marks(x) for x in RAW.splitlines() if "⭐" in x}
    gems = {strip_marks(x) for x in RAW.splitlines() if "💎" in x}
    print(f"props: {len(props)}  favorites: {len(stars)}  gems: {len(gems)}")

    # batter -> [(game, pitcher, odds)]
    seen: dict[str, list[tuple[str, str, str]]] = {}
    for p in sorted((ROOT / "data").glob(f"hr-matchups-*-{DATE}.csv")):
        m = re.match(rf"hr-matchups-(.+?)-at-(.+?)-(.+)-{DATE}\.csv", p.name)
        game = f"{m.group(1)} @ {m.group(2)}" if m else p.name
        pit = (m.group(3).replace("-", " ") if m else "?")
        lines = p.read_text(encoding="utf-8-sig").splitlines()
        hi = next((i for i, l in enumerate(lines) if l.split(",")[0].strip() == "BATTER"), None)
        if hi is None:
            print(f"  !! no BATTER header in {p.name}")
            continue
        hdr = next(csv.reader([lines[hi]]))
        oi = next((i for i, c in enumerate(hdr) if c.strip().upper() == "ODDS"), None)
        for line in lines[hi + 1:]:
            r = next(csv.reader([line]), None)
            if not r or not r[0].strip():
                continue
            odds = (r[oi].strip() if oi is not None and len(r) > oi else "")
            seen.setdefault(fold(r[0]), []).append((game, pit, odds))

    zone: set[str] = set()
    zp = ROOT / "data" / f"zone-matchups-{DATE}.csv"
    if zp.is_file():
        zl = zp.read_text(encoding="utf-8-sig").splitlines()
        zhi = next((i for i, l in enumerate(zl) if "BATTER" in l.upper()), None)
        if zhi is not None:
            zhdr = next(csv.reader([zl[zhi]]))
            bi = next((i for i, c in enumerate(zhdr) if "BATTER" in c.upper()), 0)
            for line in zl[zhi + 1:]:
                r = next(csv.reader([line]), None)
                if r and len(r) > bi and r[bi].strip():
                    zone.add(fold(r[bi]))

    missing, noprice, ok = [], [], 0
    for name in props:
        hits = seen.get(fold(name))
        if not hits:
            missing.append(name)
            continue
        ok += 1
        if not any(re.search(r"[+-]\d", h[2]) for h in hits):
            noprice.append((name, hits[0][0]))

    print(f"\nmatched in hr-matchups: {ok}/{len(props)}")
    if missing:
        print(f"\nNOT FOUND ({len(missing)}):")
        for n in missing:
            near = [k for k in seen if n.split()[-1].lower() in k]
            zn = [k for k in zone if n.split()[-1].lower() in k]
            print(f"  {n:24} matchup-near={near[:3]} zone-near={zn[:3]}")
    if noprice:
        print(f"\nno numeric price ({len(noprice)}):")
        for n, g in noprice:
            print(f"  {n:24} {g}")

    print(f"\nzone-matchups batters: {len(zone)}")
    zmiss = [n for n in props if fold(n) not in zone]
    print(f"props missing zone data ({len(zmiss)}): {zmiss}")


if __name__ == "__main__":
    main()
