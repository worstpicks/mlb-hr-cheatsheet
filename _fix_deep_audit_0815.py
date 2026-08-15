#!/usr/bin/env python3
"""Re-point _deep_audit_0815.py at the 8/15 prop list, aliases and bums.

The scaffold only swaps dates and counts, so the deep audit inherits the prior
slate's USER_PROPS / RESOLVED / EXPECTED_BUMS tables. Done as a separate script
rather than inside _make_0815.py because re-running the scaffold would overwrite
the straight and Goblin judgment locks already applied to patch-0815-preview.py.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "_deep_audit_0815.py"

# Names exactly as they appear on the built sheet, with the marker the user gave.
PROPS: list[tuple[str, str]] = [
    ("Eduardo Valencia", "GEM"),
    ("Gleyber Torres", ""),
    ("Munetaka Murakami", "STAR"),
    ("Colson Montgomery", "GEM"),
    ("Andrew Benintendi", ""),
    ("Braden Montgomery", ""),
    ("Ian Happ", ""),
    ("Miguel Amaya", "GEM"),
    ("Pete Crow-Armstrong", "GEM"),
    ("Michael Conforto", ""),
    ("Jordan Walker", "STAR"),
    ("Ivan Herrera", ""),
    ("Jimmy Crooks", ""),
    ("Jose Fermin", ""),
    ("Jesus Sanchez", "STAR"),
    ("Vladimir Guerrero Jr.", ""),
    ("Ernie Clement", ""),
    ("Trent Grisham", ""),
    ("Jazz Chisholm Jr.", ""),
    ("Luis Garcia Jr.", ""),
    ("Spencer Jones", ""),
    ("Ben Rice", "STAR"),
    ("Heliot Ramos", ""),
    ("Jung Hoo Lee", ""),
    ("Bryce Eldridge", "GEM"),
    ("Rafael Devers", ""),
    ("Zac Veen", "GEM"),
    ("Willi Castro", ""),
    ("Hunter Goodman", ""),
    ("Mickey Moniak", ""),
    ("Brett Baty", "GEM"),
    ("Francisco Lindor", ""),
    ("Jorge Polanco", ""),
    ("Daylen Lile", ""),
    ("Brady House", ""),
    ("Andrew Pinckney", ""),
    ("Dylan Crews", ""),
    ("Jonathan Aranda", ""),
    ("Victor Mesa Jr.", ""),
    ("Junior Caminero", ""),
    ("Gunnar Henderson", "GEM"),
    ("Christian Encarnacion-Strand", ""),
    ("Coby Mayo", "GEM"),
    ("Pete Alonso", "STAR"),
    ("Jeremiah Jackson", ""),
    ("Tyler Stephenson", "GEM"),
    ("Eugenio Suarez", ""),
    ("Sal Stewart", ""),
    ("Griffin Conine", "STAR"),
    ("Heriberto Hernandez", ""),
    ("Owen Caissie", ""),
    ("Joe Mack", ""),
    ("Royce Lewis", "STAR"),
    ("Byron Buxton", ""),
    ("Austin Martin", ""),
    ("Victor Caratini", ""),
    ("Bryson Stott", ""),
    ("Kyle Schwarber", ""),
    ("Trea Turner", ""),
    ("J.T. Realmuto", "GEM"),
    ("Bryce Harper", ""),
    ("Yordan Alvarez", "STAR"),
    ("Taylor Trammell", "GEM"),
    ("Daulton Varsho", ""),
    ("Nelson Velazquez", ""),
    ("Dominic Canzone", "STAR"),
    ("Cal Raleigh", ""),
    ("Josh Naylor", ""),
    ("Julio Rodriguez", ""),
    ("Randy Arozarena", ""),
    ("Nathaniel Lowe", ""),
    ("Chase DeLauter", "GEM"),
    ("Jo Adell", ""),
    ("Rhys Hoskins", ""),
    ("Jase Bowen", ""),
    ("Fernando Tatis Jr.", "GEM"),
    ("Jackson Merrill", "STAR"),
    ("Manny Machado", "GEM"),
    ("Jacob Gonzalez", ""),
    ("Brandon Lowe", "GEM"),
    ("Jake Mangum", ""),
    ("Connor Wong", ""),
    ("Jarren Duran", "GEM"),
    ("Wilyer Abreu", ""),
    ("Shohei Ohtani", ""),
    ("Hunter Feduccia", ""),
    ("Teoscar Hernandez", ""),
    ("Max Muncy", ""),
    ("Andrew Vaughn", "GEM"),
    ("Jake Bauers", ""),
    ("Jackson Chourio", "STAR"),
    ("Gary Sanchez", ""),
    ("Ozzie Albies", ""),
    ("Matt Olson", ""),
    ("Lane Thomas", ""),
    ("Austin Riley", "STAR"),
    ("Jim Jarvis", ""),
    ("Corbin Carroll", "STAR"),
    ("Lars Nootbaar", "GEM"),
    ("Travis d'Arnaud", ""),
    ("Moises Ballesteros", ""),
    ("Josh Lowe", ""),
    ("Jac Caglianone", "STAR"),
    ("Carter Jensen", "GEM"),
    ("Salvador Perez", ""),
    ("Tyler Soderstrom", "GEM"),
    ("Jonah Heim", ""),
    ("Henry Bolte", ""),
    ("Zack Gelof", ""),
    ("Joc Pederson", "GEM"),
    ("Corey Seager", "STAR"),
    ("Wyatt Langford", ""),
]

RESOLVED = {
    "Btaden Montgomery": "Braden Montgomery",
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "JT Realmuto": "J.T. Realmuto",
    "Josh lowe": "Josh Lowe",
}

EXPECTED_BUMS = ["Justin Wrobleski", "Michael Lorenzen", "Jared Jones"]


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")

    body = "".join(
        f'    ("{n}", {m or chr(34) + chr(34)}),\n' for n, m in PROPS
    )
    block = "USER_PROPS: list[tuple[str, str]] = [\n" + body + "]"
    text, n = re.subn(
        r"USER_PROPS: list\[tuple\[str, str\]\] = \[.*?\n\]", block, text, count=1, flags=re.S
    )
    assert n == 1, "USER_PROPS block not found"

    res = "RESOLVED = {" + ", ".join(f'"{k}": "{v}"' for k, v in RESOLVED.items()) + "}"
    text, n = re.subn(r"RESOLVED = \{[^\n]*\}", res, text, count=1)
    assert n == 1, "RESOLVED block not found"

    bums = "EXPECTED_BUMS = {" + ", ".join(f'"{b}"' for b in EXPECTED_BUMS) + "}"
    text, n = re.subn(r"EXPECTED_BUMS = \{[^\n]*\}", bums, text, count=1)
    assert n == 1, "EXPECTED_BUMS block not found"

    stars = sum(1 for _, m in PROPS if m == "STAR")
    gems = sum(1 for _, m in PROPS if m == "GEM")
    TARGET.write_text(text, encoding="utf-8")
    print(f"re-pointed {TARGET.name}: {len(PROPS)} props, {stars} stars, {gems} gems")
    print(f"  bums: {EXPECTED_BUMS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
