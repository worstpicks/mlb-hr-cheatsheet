#!/usr/bin/env python3
"""Deep content audit for the 2026-08-15 sheet: prop coverage, markers, bums, staleness."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-15"
PREVIEW = ROOT / "preview" / "index.html"

STAR = "\u2b50"
GEM = "\U0001f48e"
GLOVE = "\U0001f9e4"

GAMECOUNT = 15

# (name, marker) exactly as the user listed them for 8/15
USER_PROPS: list[tuple[str, str]] = [
    ("Eduardo Valencia", GEM),
    ("Gleyber Torres", ""),
    ("Munetaka Murakami", STAR),
    ("Colson Montgomery", GEM),
    ("Andrew Benintendi", ""),
    ("Braden Montgomery", ""),
    ("Ian Happ", ""),
    ("Miguel Amaya", GEM),
    ("Pete Crow-Armstrong", GEM),
    ("Michael Conforto", ""),
    ("Jordan Walker", STAR),
    ("Ivan Herrera", ""),
    ("Jimmy Crooks", ""),
    ("Jose Fermin", ""),
    ("Jesus Sanchez", STAR),
    ("Vladimir Guerrero Jr.", ""),
    ("Ernie Clement", ""),
    ("Trent Grisham", ""),
    ("Jazz Chisholm Jr.", ""),
    ("Luis Garcia Jr.", ""),
    ("Spencer Jones", ""),
    ("Ben Rice", STAR),
    ("Heliot Ramos", ""),
    ("Jung Hoo Lee", ""),
    ("Bryce Eldridge", GEM),
    ("Rafael Devers", ""),
    ("Zac Veen", GEM),
    ("Willi Castro", ""),
    ("Hunter Goodman", ""),
    ("Mickey Moniak", ""),
    ("Brett Baty", GEM),
    ("Francisco Lindor", ""),
    ("Jorge Polanco", ""),
    ("Daylen Lile", ""),
    ("Brady House", ""),
    ("Andrew Pinckney", ""),
    ("Dylan Crews", ""),
    ("Jonathan Aranda", ""),
    ("Victor Mesa Jr.", ""),
    ("Junior Caminero", ""),
    ("Gunnar Henderson", GEM),
    ("Christian Encarnacion-Strand", ""),
    ("Coby Mayo", GEM),
    ("Pete Alonso", STAR),
    ("Jeremiah Jackson", ""),
    ("Tyler Stephenson", GEM),
    ("Eugenio Suarez", ""),
    ("Sal Stewart", ""),
    ("Griffin Conine", STAR),
    ("Heriberto Hernandez", ""),
    ("Owen Caissie", ""),
    ("Joe Mack", ""),
    ("Royce Lewis", STAR),
    ("Byron Buxton", ""),
    ("Austin Martin", ""),
    ("Victor Caratini", ""),
    ("Bryson Stott", ""),
    ("Kyle Schwarber", ""),
    ("Trea Turner", ""),
    ("J.T. Realmuto", GEM),
    ("Bryce Harper", ""),
    ("Yordan Alvarez", STAR),
    ("Taylor Trammell", GEM),
    ("Daulton Varsho", ""),
    ("Nelson Velazquez", ""),
    ("Dominic Canzone", STAR),
    ("Cal Raleigh", ""),
    ("Josh Naylor", ""),
    ("Julio Rodriguez", ""),
    ("Randy Arozarena", ""),
    ("Nathaniel Lowe", ""),
    ("Chase DeLauter", GEM),
    ("Jo Adell", ""),
    ("Rhys Hoskins", ""),
    ("Jase Bowen", ""),
    ("Fernando Tatis Jr.", GEM),
    ("Jackson Merrill", STAR),
    ("Manny Machado", GEM),
    ("Jacob Gonzalez", ""),
    ("Brandon Lowe", GEM),
    ("Jake Mangum", ""),
    ("Connor Wong", ""),
    ("Jarren Duran", GEM),
    ("Wilyer Abreu", ""),
    ("Shohei Ohtani", ""),
    ("Hunter Feduccia", ""),
    ("Teoscar Hernandez", ""),
    ("Max Muncy", ""),
    ("Andrew Vaughn", GEM),
    ("Jake Bauers", ""),
    ("Jackson Chourio", STAR),
    ("Gary Sanchez", ""),
    ("Ozzie Albies", ""),
    ("Matt Olson", ""),
    ("Lane Thomas", ""),
    ("Austin Riley", STAR),
    ("Jim Jarvis", ""),
    ("Corbin Carroll", STAR),
    ("Lars Nootbaar", GEM),
    ("Travis d'Arnaud", ""),
    ("Moises Ballesteros", ""),
    ("Josh Lowe", ""),
    ("Jac Caglianone", STAR),
    ("Carter Jensen", GEM),
    ("Salvador Perez", ""),
    ("Tyler Soderstrom", GEM),
    ("Jonah Heim", ""),
    ("Henry Bolte", ""),
    ("Zack Gelof", ""),
    ("Joc Pederson", GEM),
    ("Corey Seager", STAR),
    ("Wyatt Langford", ""),
]

# Name the sheet legitimately uses that differs from the user's spelling.
RESOLVED = {"Btaden Montgomery": "Braden Montgomery", "Pete Crow Armstrong": "Pete Crow-Armstrong", "JT Realmuto": "J.T. Realmuto", "Josh lowe": "Josh Lowe"}

# 8/14-only content that must not survive onto the 8/15 sheet. Prior-day starters plus
# batters absent from this slate - shared names like Alonso or Suarez are on 8/15 too,
# so listing them here would fail every correct sheet.
STALE_8_14 = [
    "Sandy Alcantara",
    "Chase Burns",
    "Jake Bennett",
    "Bubba Chandler",
    "Sean Newcomb",
    "Jackson Jobe",
    "Chris Bassitt",
    "Steven Matz",
    "Michael King",
    "Gavin Williams",
    "Andrew Alvarez",
    "Robert Stock",
    "Brandon Pfaadt",
    "Chris Sale",
    "Gerrit Cole",
    "Shane Bieber",
    "George Kirby",
    "Peter Lambert",
    "Seth Lugo",
    "Grayson Rodriguez",
    "Kumar Rocker",
    "Gage Jump",
    "Robert Gasser",
    "Yoshinobu Yamamoto",
    "Kyle Freeland",
    "Landen Roupp",
]

EXPECTED_BUMS = {"Justin Wrobleski", "Michael Lorenzen", "Jared Jones"}

errs: list[str] = []
warns: list[str] = []


def fail(msg: str) -> None:
    errs.append(msg)


def fold(text: str) -> str:
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return t.lower().replace("\u2019", "'")


def main() -> int:
    html = PREVIEW.read_text(encoding="utf-8")
    folded = fold(html)

    # Row objects: name + emoji string
    rows = re.findall(r'\{ name: "([^"]+)"[^}]*?emojis: "([^"]*)"', html)
    print(f"=== DEEP AUDIT {DATE} ===")
    print(f"rows parsed: {len(rows)}")
    if len(rows) != len(USER_PROPS):
        fail(f"expected {len(USER_PROPS)} rows, parsed {len(rows)}")

    by_name: dict[str, str] = {}
    for raw, em in rows:
        plain = raw.rsplit(" (", 1)[0]
        by_name[fold(plain)] = em

    fav = sum(1 for _, em in rows if STAR in em)
    gem = sum(1 for _, em in rows if GEM in em)
    want_fav = sum(1 for _, m in USER_PROPS if m == STAR)
    want_gem = sum(1 for _, m in USER_PROPS if m == GEM)
    print(f"favorites {fav} (want {want_fav}) · gems {gem} (want {want_gem})")
    if fav != want_fav:
        fail(f"expected {want_fav} favorites, got {fav}")
    if gem != want_gem:
        fail(f"expected {want_gem} gems, got {gem}")

    # Every listed prop present with the right marker
    for name, marker in USER_PROPS:
        lookup = RESOLVED.get(name, name)
        em = by_name.get(fold(lookup))
        if em is None:
            fail(f"prop missing from sheet: {name}")
            continue
        if marker == STAR and STAR not in em:
            fail(f"{name} should be a favorite (star)")
        if marker == GEM and GEM not in em:
            fail(f"{name} should be a hidden gem")
        if marker == "" and (STAR in em or GEM in em):
            fail(f"{name} should have no star/gem, got {em!r}")

    # Games and park/split header coverage
    titles = re.findall(r'title: "([^"]+)"', html)
    # gameMeta embeds escaped quotes around the pitcher-meta spans, so a plain [^"]*
    # capture stops after the park segment and hides the pitcher splits.
    metas = re.findall(r'gameMeta: "((?:[^"\\]|\\.)*)"', html)
    print(f"games: {len(titles)}")
    if len(titles) != GAMECOUNT:
        fail(f"expected {GAMECOUNT} games, got {len(titles)}")
    for t, meta in zip(titles, metas):
        if "Park " not in meta:
            fail(f"game missing park %: {t}")
        if "LHB" not in meta or "RHB" not in meta:
            fail(f"game missing hand park split: {t}")
        if meta.count("pitcher-meta") < 2:
            fail(f"game missing both pitcher splits: {t}")

    # Bums gloved in titles, and their opponents flagged on rows
    for bum in EXPECTED_BUMS:
        if f"{bum} {GLOVE}" not in html:
            fail(f"bum {bum} missing {GLOVE} in game title")
    gloved_titles = [t for t in titles if GLOVE in t]
    if len(gloved_titles) != len(EXPECTED_BUMS):
        fail(f"expected {len(EXPECTED_BUMS)} gloved titles, got {len(gloved_titles)}")

    # Rows facing a bum should carry the vs-bum emoji trio
    for t in gloved_titles:
        m = re.search(r"\{ title: \"" + re.escape(t) + r"\".*?\n\s*\], \}", html, re.S)
        block = m.group(0) if m else ""
        bum_last = None
        gm = re.search(r"vs ([^(]+?) " + GLOVE, t) or re.search(
            r"- ([^(]+?) " + GLOVE, t
        )
        if gm:
            bum_last = gm.group(1).strip().split()[-1]
        if not bum_last:
            continue
        for rm in re.finditer(
            r'\{ name: "([^"]+)"[^}]*?emojis: "([^"]*)"[^}]*?chips: \["vs ([^"]+)"\]', block
        ):
            name, em, chip = rm.groups()
            if chip.strip().split()[-1] == bum_last and GLOVE not in em:
                fail(f"{name} faces bum {bum_last} but row lacks {GLOVE}")

    # Staleness: ignore the historical straights tracker, which legitimately lists past days
    body = re.sub(
        r'<script[^>]*straights-history-data.*?</script>', "", html, flags=re.S
    )
    body_folded = fold(body)
    for name in STALE_8_14:
        if fold(name) in body_folded:
            fail(f"stale 8/14 content on sheet: {name}")

    # Date correctness
    if "Saturday, August 15, 2026" not in html:
        fail("hero must read Saturday, August 15, 2026")
    for wrong in ("Monday, August 15", "Tuesday, August 15", "Wednesday, August 15",
                  "Thursday, August 15", "Friday, August 15", "Sunday, August 15"):
        if wrong in html:
            fail(f"wrong weekday for August 15: {wrong}")

    # Regression guard for the CWS/WSH park-key aliasing bug: Ballpark Pal ships these
    # as CHW / WAS, and the old pair-by-pair alias map dropped unseen matchups.
    for gkey in ("CWS @ DET", "WSH @ NYM"):
        m = re.search(
            r'title: "' + re.escape(gkey) + r'[^"]*".*?gameMeta: "((?:[^"\\]|\\.)*)"', html, re.S
        )
        if not m:
            fail(f"{gkey} game block not found")
        elif "Park " not in m.group(1):
            fail(f"{gkey} missing park factor (team-code alias regression)")

    print()
    for w in warns:
        print("WARN", w)
    if errs:
        print("FAIL deep audit:")
        for e in errs:
            print("  -", e)
        return 1
    print("OK deep audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
