#!/usr/bin/env python3
"""Deep content audit for the 2026-08-13 sheet: prop coverage, markers, bums, staleness."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-13"
PREVIEW = ROOT / "preview" / "index.html"

STAR = "\u2b50"
GEM = "\U0001f48e"
GLOVE = "\U0001f9e4"

# (name, marker) exactly as the user listed them for 8/13
USER_PROPS: list[tuple[str, str]] = [
    ("Griffin Conine", STAR),
    ("Owen Caissie", ""),
    ("Brandon Lowe", GEM),
    ("Jacob Gonzalez", ""),
    ("Endy Rodriguez", STAR),
    ("Eduardo Valencia", ""),
    ("James Outman", ""),
    ("Dillon Dingler", ""),
    ("Jo Adell", ""),
    ("Rhys Hoskins", GEM),
    ("Nathaniel Lowe", GEM),
    ("Angel Genao", ""),
    ("Chase DeLauter", ""),
    ("Ben Rice", STAR),
    ("Trent Grisham", ""),
    ("Spencer Jones", GEM),
    ("Heliot Ramos", ""),
    ("Munetaka Murakami", STAR),
    ("Miguel Vargas", GEM),
    ("Tyler Stephenson", GEM),
    ("JJ Bleday", ""),
    ("Kazuma Okamoto", ""),
    ("Alejandro Kirk", ""),
    ("Ernie Clement", ""),
    ("Jarren Duran", GEM),
    ("Wilyer Abreu", ""),
    ("Brady House", ""),
    ("Dylan Crews", GEM),
    ("Abimelec Ortiz", ""),
    ("Daylen Lile", ""),
    ("Keibert Ruiz", ""),
    ("Kody Clemens", STAR),
    ("Josh Bell", ""),
    ("Royce Lewis", ""),
    ("Victor Caratini", ""),
    ("Bryce Harper", STAR),
    ("Kyle Schwarber", STAR),
    ("Derek Hill", ""),
    ("Bryson Stott", ""),
    ("Bryan De La Cruz", ""),
    ("Moises Ballesteros", ""),
    ("Alex Bregman", ""),
    ("Miguel Amaya", ""),
    ("Mike Trout", ""),
    ("Travis d'Arnaud", ""),
    ("Vaughn Grissom", ""),
    ("Ezequiel Duran", ""),
    ("Joc Pederson", GEM),
    ("Corey Seager", ""),
    ("Teoscar Hernandez", ""),
    ("Mookie Betts", ""),
    ("Andy Pages", ""),
    ("Endy Hernandez", ""),  # sheet resolves to Enrique Hernandez (LAD)
    ("Kyle Tucker", ""),
    ("Jackson Chourio", STAR),
    ("William Contreras", GEM),
    ("Brice Turang", STAR),
    ("Jake Bauers", ""),
    ("Garrett Mitchell", ""),
]

# Name the sheet legitimately uses that differs from the user's spelling.
RESOLVED = {"Endy Hernandez": "Enrique Hernandez"}

# 8/12-only content that must not survive onto the 8/13 sheet.
STALE_8_12 = [
    "Elly De La Cruz",
    "Pete Alonso",
    "Jonny DeLuca",
    "Junior Caminero",
    "Michael Massey",
    "Yandy Diaz",
    "Eugenio Suarez",
    "Cal Raleigh",
    "Ryan Feltner",
    "Jack Perkins",
    "Luis Castillo",
    "Zebby Matthews",
    "Jackson Kent",
]

EXPECTED_BUMS = {"Max Scherzer", "Aaron Nola"}

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
    if len(titles) != 9:
        fail(f"expected 9 games, got {len(titles)}")
    for t, meta in zip(titles, metas):
        if "Park " not in meta:
            fail(f"game missing park %: {t}")
        if "LHB" not in meta or "RHB" not in meta:
            fail(f"game missing hand park split: {t}")
        if meta.count("overall") < 2 and "no MLB HR data yet" not in meta:
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
    for name in STALE_8_12:
        if fold(name) in body_folded:
            fail(f"stale 8/12 content on sheet: {name}")

    # Date correctness
    if "Thursday, August 13, 2026" not in html:
        fail("hero must read Thursday, August 13, 2026")
    for wrong in ("Monday, August 13", "Tuesday, August 13", "Wednesday, August 13",
                  "Friday, August 13", "Saturday, August 13", "Sunday, August 13"):
        if wrong in html:
            fail(f"wrong weekday for August 13: {wrong}")

    # Field of Dreams park factor made it onto the special-event game
    if "PHI @ MIN" in html:
        m = re.search(
            r'title: "PHI @ MIN[^"]*".*?gameMeta: "((?:[^"\\]|\\.)*)"', html, re.S
        )
        if m and "Park " not in m.group(1):
            fail("PHI @ MIN (Field of Dreams) missing park factor")

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
