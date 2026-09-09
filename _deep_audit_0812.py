#!/usr/bin/env python3
"""Deep content audit for the 2026-08-12 sheet: props, emojis, bums, staleness."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-12"
HTML = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")

# Exactly as the user listed them, with the aliases applied by build-0812-from-csv.py.
USER_PROPS = [
    ("Kody Clemens", "fav"), ("Pete Alonso", "fav"), ("Gunnar Henderson", "fav"),
    ("Colton Cowser", ""), ("Jimmy Crooks", ""), ("Jordan Walker", "gem"),
    ("Ivan Herrera", ""), ("Kyle Schwarber", "fav"), ("Bryce Harper", ""),
    ("Lawrence Butler", "gem"), ("Tyler Soderstrom", ""), ("Zack Gelof", ""),
    ("Yandy Diaz", ""), ("Jonny DeLuca", "gem"), ("Junior Caminero", ""),
    ("Victor Mesa Jr.", "gem"), ("Corbin Carroll", ""), ("Lars Nootbaar", ""),
    ("Hunter Goodman", ""), ("Willi Castro", ""), ("Mickey Moniak", "fav"),
    ("Willy Adames", "fav"), ("Rafael Devers", ""), ("Yordan Alvarez", "fav"),
    ("Nelson Velazquez", "gem"), ("Taylor Trammell", ""), ("Jackson Merrill", "fav"),
    ("Ty France", "gem"), ("Manny Machado", "gem"), ("Jake Bauers", ""),
    ("Jackson Chourio", ""), ("William Contreras", ""), ("Andrew Vaughn", ""),
    ("Griffin Conine", "fav"), ("Owen Caissie", "fav"), ("Brandon Lowe", "fav"),
    ("Esmerlyn Valdez", ""), ("James Outman", "gem"), ("Eduardo Valencia", ""),
    ("Jo Adell", "fav"), ("Pete Crow-Armstrong", ""), ("Ian Happ", ""),
    ("Dylan Crews", ""), ("Daylen Lile", ""), ("Luis Garcia Jr.", "fav"),
    ("Spencer Jones", ""), ("Ben Rice", ""), ("Josh Naylor", ""),
    ("Cal Raleigh", "fav"), ("Julio Rodriguez", ""), ("Randy Arozarena", "gem"),
    ("Kazuma Okamoto", "fav"), ("Vladimir Guerrero Jr.", ""), ("Jarren Duran", "fav"),
    ("Wilyer Abreu", ""), ("Ceddanne Rafaela", ""), ("Matt Olson", "fav"),
    ("Austin Riley", "fav"), ("Ronald Acuna Jr.", ""), ("Francisco Alvarez", ""),
    ("Francisco Lindor", ""), ("Brett Baty", "gem"), ("Munetaka Murakami", "fav"),
    ("Miguel Vargas", ""), ("Elly De La Cruz", "gem"), ("Tyler Stephenson", ""),
    ("Eugenio Suarez", "gem"), ("Teoscar Hernandez", "fav"), ("Freddie Freeman", ""),
    ("Carter Jensen", "fav"), ("John Rave", ""), ("Michael Massey", ""),
    ("Jac Caglianone", "fav"), ("Moises Ballesteros", "fav"), ("Mike Trout", ""),
    ("Nolan Schanuel", ""), ("Jarred Kelenic", "fav"), ("Corey Seager", ""),
    ("Elias Diaz", ""),
]

STALE_8_11 = [
    "Josh Bell &mdash;",
    "Andres Chaparro",
    "Brady House",
    "JJ Bleday",
    "Joc Pederson",
    "Tomoyuki Sugano",
    "Mason Barnett",
    "Ryan Johnson",
    "Jake Irvin",
    "Carson Whisenhunt",
]

errs: list[str] = []


def fail(msg: str) -> None:
    errs.append(msg)


def main() -> int:
    block = re.search(r"const games = \[(.*?)\n\];", HTML, re.S)
    if not block:
        print("games block missing")
        return 1
    games_js = block.group(1)

    entries = re.findall(r'name:\s*"([^"]+)",\s*emojis:\s*"([^"]*)"', games_js)
    if not entries:
        entries = [
            (m.group(1), m.group(2))
            for m in re.finditer(r'\{\s*name:\s*"([^"]+)".*?emojis:\s*"([^"]*)"', games_js, re.S)
        ]
    by_plain: dict[str, str] = {}
    for name, em in entries:
        by_plain.setdefault(re.sub(r"\s*\([LRS]\)$", "", name), em)

    for name, mark in USER_PROPS:
        if name not in by_plain:
            fail(f"prop missing from sheet: {name}")
            continue
        em = by_plain[name]
        if mark == "fav" and "⭐" not in em:
            fail(f"{name}: expected ⭐, got {em!r}")
        if mark == "gem" and "💎" not in em:
            fail(f"{name}: expected 💎, got {em!r}")
        if mark == "" and ("⭐" in em or "💎" in em):
            fail(f"{name}: unexpected ⭐/💎 in {em!r}")

    n_fav = sum(1 for e in by_plain.values() if "⭐" in e)
    n_gem = sum(1 for e in by_plain.values() if "💎" in e)
    if n_fav != sum(1 for _, m in USER_PROPS if m == "fav"):
        fail(f"favorite count {n_fav} != {sum(1 for _, m in USER_PROPS if m == 'fav')}")
    if n_gem != sum(1 for _, m in USER_PROPS if m == "gem"):
        fail(f"gem count {n_gem} != {sum(1 for _, m in USER_PROPS if m == 'gem')}")

    # Every row facing a bum SP must carry the ⚾🕊️🧤 trio.
    titles = re.findall(r'title:\s*"([^"]+)"', games_js)
    chunks = re.split(r'\{\s*title:\s*"', games_js)[1:]
    for title, chunk in zip(titles, chunks):
        bums = {
            m.group(1).split()[-1]
            for m in re.finditer(r"([A-Z][A-Za-z.\-']+(?: [A-Za-z.\-']+)*) 🧤", title)
        }
        if not bums:
            continue
        for rname, rem, rchips in re.findall(
            r'name:\s*"([^"]+)",\s*emojis:\s*"([^"]*)".*?chips:\s*\[([^\]]*)\]', chunk, re.S
        ):
            chip = re.sub(r'["\s]|vs ', "", rchips)
            if chip.split()[-1] if " " in chip else chip:
                pass
            if any(b in chip for b in bums):
                for glyph in ("⚾", "🕊️", "🧤"):
                    if glyph not in rem:
                        fail(f"{title[:24]}: {rname} vs bum missing {glyph} (emojis {rem!r})")

    # The streak tracker legitimately names past winners, so exclude its payload.
    body = re.sub(
        r'<script type="application/json" id="straights-history-data">.*?</script>',
        "",
        HTML,
        flags=re.S,
    )
    for stale in STALE_8_11:
        if stale in body:
            fail(f"stale 8/11 content present: {stale}")

    for needle in (
        'content="2026-08-12"',
        "Wednesday, August 12, 2026",
        "79 listed HR props",
    ):
        if needle not in HTML:
            fail(f"missing: {needle}")

    print("=== DEEP AUDIT 2026-08-12 ===")
    print(f"rows parsed: {len(by_plain)} · favorites {n_fav} · gems {n_gem}")
    print("games:", len(titles))
    if errs:
        print("ERRORS:")
        for e in errs:
            print(" ", e)
        return 1
    print("OK deep audit passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
