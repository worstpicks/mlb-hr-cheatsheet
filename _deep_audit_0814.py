#!/usr/bin/env python3
"""Deep content audit for the 2026-08-14 sheet: prop coverage, markers, bums, staleness."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-14"
PREVIEW = ROOT / "preview" / "index.html"

STAR = "\u2b50"
GEM = "\U0001f48e"
GLOVE = "\U0001f9e4"

# (name, marker) exactly as the user listed them for 8/14
USER_PROPS: list[tuple[str, str]] = [
    ("Tyler Stephenson", GEM),
    ("Matt McLain", ""),
    ("Eugenio Suarez", ""),
    ("Sal Stewart", ""),
    ("Griffin Conine", STAR),
    ("Joe Mack", ""),
    ("Owen Caissie", ""),
    ("Ronny Simon", ""),
    ("Bryan Reynolds", GEM),
    ("Esmerlyn Valdez", ""),
    ("Jarren Duran", ""),
    ("Wilyer Abreu", ""),
    ("Eduardo Valencia", ""),
    ("Gleyber Torres", ""),
    ("Spencer Torkelson", ""),
    ("Munetaka Murakami", STAR),
    ("Drew Romo", ""),
    ("Randal Grichuk", ""),
    ("Victor Mesa Jr.", GEM),
    ("Yandy Diaz", ""),
    ("Jonathan Aranda", GEM),
    ("Junior Caminero", ""),
    ("Pete Alonso", STAR),
    ("Coby Mayo", STAR),
    ("Francisco Alvarez", GEM),
    ("Carson Benge", ""),
    ("A.J. Ewing", ""),
    ("Luis Robert", STAR),
    ("Daylen Lile", STAR),
    ("Abimelec Ortiz", STAR),
    ("Jose Tena", ""),
    ("Angel Genao", GEM),
    ("Nathaniel Lowe", ""),
    ("Patrick Bailey", ""),
    ("Chase DeLauter", ""),
    ("Jackson Merrill", STAR),
    ("Manny Machado", ""),
    ("Xander Bogaerts", ""),
    ("Fernando Tatis Jr.", ""),
    ("Jesus Sanchez", ""),
    ("Kazuma Okamoto", ""),
    ("George Springer", ""),
    ("Ben Rice", ""),
    ("Spencer Jones", ""),
    ("Jazz Chisholm Jr.", ""),
    ("Luis Garcia Jr.", ""),
    ("Matt Olson", ""),
    ("Drake Baldwin", GEM),
    ("Ronald Acuna Jr.", ""),
    ("Michael Harris II", ""),
    ("Daulton Varsho", GEM),
    ("Taylor Trammell", ""),
    ("Yordan Alvarez", STAR),
    ("Nelson Velazquez", ""),
    ("Cam Smith", ""),
    ("Julio Rodriguez", ""),
    ("Dominic Canzone", GEM),
    ("Josh Naylor", GEM),
    ("Mike Trout", STAR),
    ("Moises Ballesteros", ""),
    ("Jac Caglianone", STAR),
    ("Salvador Perez", ""),
    ("Bobby Witt Jr.", ""),
    ("Isaac Collins", ""),
    ("Lawrence Butler", STAR),
    ("Tyler Soderstrom", GEM),
    ("Henry Bolte", ""),
    ("Zack Gelof", ""),
    ("Justin Foscue", ""),
    ("Elias Diaz", ""),
    ("Teoscar Hernandez", GEM),
    ("Mookie Betts", ""),
    ("Shohei Ohtani", GEM),
    ("Andy Pages", ""),
    ("Jake Bauers", GEM),
    ("Brice Turang", ""),
    ("William Contreras", GEM),
    ("Joey Ortiz", ""),
    ("Rafael Devers", ""),
    ("Bryce Eldridge", ""),
    ("Victor Bericoto", ""),
    ("Willy Adames", ""),
    ("Zac Veen", ""),
    ("Willi Castro", ""),
    ("Hunter Goodman", STAR),
]

# Name the sheet legitimately uses that differs from the user's spelling.
RESOLVED = {"Spencer Torkleson": "Spencer Torkelson", "Ronald Acuna": "Ronald Acuna Jr."}

# 8/13-only content that must not survive onto the 8/14 sheet. Prior-day starters plus
# batters absent from this slate - shared names like Alonso or Suarez are on 8/14 too,
# so listing them here would fail every correct sheet.
STALE_8_13 = [
    "Max Scherzer",
    "Aaron Nola",
    "Parker Messick",
    "Keider Montero",
    "Braxton Ashcraft",
    "Tyler Phillips",
    "Logan Gilbert",
    "Max Fried",
    "Andrew Abbott",
    "Davis Martin",
    "Payton Tolle",
    "Kevin Gausman",
    "Cade Cavalli",
    "Taj Bradley",
    "Jacob deGrom",
    "Walbert Urena",
    "Shane Drohan",
    "Roki Sasaki",
    "Kyle Schwarber",
    "Bryce Harper",
    "Jackson Chourio",
    "Kody Clemens",
    "Alex Bregman",
    "Miguel Amaya",
]

EXPECTED_BUMS = {"Grayson Rodriguez", "Gavin Williams", "Kumar Rocker"}

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
    if len(titles) != 13:
        fail(f"expected 13 games, got {len(titles)}")
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
    for name in STALE_8_13:
        if fold(name) in body_folded:
            fail(f"stale 8/13 content on sheet: {name}")

    # Date correctness
    if "Friday, August 14, 2026" not in html:
        fail("hero must read Friday, August 14, 2026")
    for wrong in ("Monday, August 14", "Tuesday, August 14", "Wednesday, August 14",
                  "Thursday, August 14", "Saturday, August 14", "Sunday, August 14"):
        if wrong in html:
            fail(f"wrong weekday for August 14: {wrong}")

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
