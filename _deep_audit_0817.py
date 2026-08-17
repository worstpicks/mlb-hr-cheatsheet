#!/usr/bin/env python3
"""Deep content audit for the 2026-08-17 sheet: prop coverage, markers, bums, staleness."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-17"
PREVIEW = ROOT / "preview" / "index.html"

STAR = "⭐"
GEM = "\U0001f48e"
GLOVE = "\U0001f9e4"

GAMECOUNT = 11
WEEKDAY = "Monday"
DATE_TEXT = "August 17, 2026"

# (name, game_suffix, marker) exactly as the user listed them for 8/17.
# STL @ CIN is a doubleheader, so four hitters appear twice under the same name with
# different markers per game — the audit keys on (name, game) rather than name alone,
# or Stephenson's G1 gem would be checked against his unmarked G2 row.
G1, G2, ANY = "STL @ CIN (G1)", "STL @ CIN (G2)", None
USER_PROPS: list[tuple[str, str | None, str]] = [
    ("Elly De La Cruz", G1, ""),
    ("Eugenio Suarez", G1, ""),
    ("Sal Stewart", G1, ""),
    ("Tyler Stephenson", G1, GEM),
    ("Alec Burleson", G1, GEM),
    ("Jordan Walker", G1, ""),
    ("Victor Mesa Jr.", ANY, GEM),
    ("Christian Encarnacion-Strand", ANY, STAR),
    ("Pete Alonso", ANY, GEM),
    ("Coby Mayo", ANY, ""),
    ("Kyle Schwarber", ANY, STAR),
    ("Brandon Marsh", ANY, ""),
    ("Derek Hill", ANY, ""),
    ("Agustin Ramirez", ANY, ""),
    ("Heriberto Hernandez", ANY, STAR),
    ("Ke'Bryan Hayes", G2, ""),
    ("Elly De La Cruz", G2, ""),
    ("Tyler Stephenson", G2, ""),
    ("Michael Toglia", G2, ""),
    ("Alec Burleson", G2, ""),
    ("Ivan Herrera", G2, ""),
    ("Joshua Baez", G2, STAR),
    ("Jordan Walker", G2, ""),
    ("Rafael Flores", ANY, STAR),
    ("Esmerlyn Valdez", ANY, GEM),
    ("Bryan Reynolds", ANY, ""),
    ("Ronny Simon", ANY, ""),
    ("Spencer Torkelson", ANY, STAR),
    ("Ben Malgeri", ANY, GEM),
    ("Colt Keith", ANY, ""),
    ("Brett Baty", ANY, ""),
    ("Francisco Lindor", ANY, GEM),
    ("Bo Bichette", ANY, ""),
    ("Gavin Sheets", ANY, ""),
    ("Xander Bogaerts", ANY, GEM),
    ("Fernando Tatis Jr.", ANY, ""),
    ("Manny Machado", ANY, ""),
    ("Jackson Merrill", ANY, GEM),
    ("Ceddanne Rafaela", ANY, GEM),
    ("Jahmai Jones", ANY, ""),
    ("Corbin Carroll", ANY, ""),
    ("Max Kepler", ANY, ""),
    ("Ketel Marte", ANY, ""),
    ("Josh Bell", ANY, GEM),
    ("Byron Buxton", ANY, ""),
    ("Austin Riley", ANY, ""),
    ("Matt Olson", ANY, ""),
    ("Mike Yastrzemski", ANY, ""),
    ("Ronald Acuna Jr.", ANY, ""),
    ("Jac Caglianone", ANY, ""),
    ("Michael Massey", ANY, ""),
    ("Zack Gelof", ANY, GEM),
    ("Lawrence Butler", ANY, STAR),
    ("Jeff McNeil", ANY, ""),
    ("Michael Conforto", ANY, STAR),
    ("Pete Crow-Armstrong", ANY, ""),
    ("Dansby Swanson", ANY, GEM),
    ("Miguel Amaya", ANY, ""),
    ("Munetaka Murakami", ANY, STAR),
    ("Miguel Vargas", ANY, GEM),
    ("Luisangel Acuna", ANY, ""),
    ("Cole Carrigg", ANY, ""),
    ("Jake McCarthy", ANY, ""),
    ("Mickey Moniak", ANY, ""),
    ("Hunter Goodman", ANY, ""),
    ("Max Muncy", ANY, GEM),
    ("Hunter Feduccia", ANY, GEM),
    ("Shohei Ohtani", ANY, ""),
    ("Teoscar Hernandez", ANY, ""),
]

# Name the sheet legitimately uses that differs from the user's spelling.
RESOLVED = {
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Victor Mesa": "Victor Mesa Jr.",
    "Ronald Acuna": "Ronald Acuna Jr.",
}

# 8/16-only content that must not survive onto the 8/17 sheet. Prior-day starters that
# are not on this slate — arms working both days would fail every correct sheet.
STALE_8_16 = [
    "Andrew Painter",
    "Blade Tidwell",
    "Bryan Woo",
    "Bryce Elder",
    "Casey Mize",
    "Christian Scott",
    "Cody Bradford",
    "Dean Kremer",
    "Drew Anderson",
    "Dylan Cease",
    "Edward Cabrera",
    "Eury Perez",
    "Freddy Peralta",
    "Gabriel Hughes",
    "Hunter Brown",
    "Hunter Dobbins",
    "Jacob Lopez",
    "Jake Irvin",
    "Lake Bachar",
    "Logan Henderson",
    "Michael Soroka",
    "Nick Lodolo",
    "Noah Cameron",
    "Patrick Sandoval",
    "Ryan Johnson",
    "Ryan Weathers",
    "Sean Burke",
    "Tanner Bibee",
    "Tarik Skubal",
    "Trevor Rogers",
]

# HR risk >= 0.95 on today's hr-targets export.
EXPECTED_BUMS = {"Mason Barnett", "Luis Castillo", "Tomoyuki Sugano"}

# Every game now carries both starters' splits: the 11:42 re-export shipped rows for
# all 22 arms, and the two 0-BF arms (Emanuel, Gamboa) render the honest
# "no MLB HR data yet" lane rather than being dropped from the header.
SINGLE_SPLIT_GAMES: set[str] = set()

# Probables that were replaced during the day. They must not survive anywhere on the
# sheet: Cincinnati's Game 1 starter went Chase Petty -> Kent Emanuel and Boston's went
# Brayan Bello -> Alec Gamboa (MLB Stats API, 11:42).
SUPERSEDED_PROBABLES = ["Chase Petty", "Brayan Bello"]

errs: list[str] = []
warns: list[str] = []


def fail(msg: str) -> None:
    errs.append(msg)


def fold(text: str) -> str:
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return t.lower().replace("’", "'")


def main() -> int:
    html = PREVIEW.read_text(encoding="utf-8")

    titles = re.findall(r'title: "([^"]+)"', html)
    print(f"=== DEEP AUDIT {DATE} ===")

    # Row objects grouped by the game block they sit in, so doubleheader duplicates
    # can be told apart.
    rows: list[tuple[str, str, str]] = []  # (game_key, plain name, emojis)
    for gm in re.finditer(r'\{\s*title: "([^"]+)".*?rows: \[(.*?)\n\s*\],', html, re.S):
        gkey = gm.group(1).split(" - ")[0]
        for rm in re.finditer(r'\{ name: "([^"]+)"[^}]*?emojis: "([^"]*)"', gm.group(2)):
            rows.append((gkey, rm.group(1).rsplit(" (", 1)[0], rm.group(2)))

    print(f"rows parsed: {len(rows)}")
    if len(rows) != len(USER_PROPS):
        fail(f"expected {len(USER_PROPS)} rows, parsed {len(rows)}")

    by_key: dict[tuple[str, str], str] = {(g, fold(n)): em for g, n, em in rows}
    by_name: dict[str, list[str]] = {}
    for _g, n, em in rows:
        by_name.setdefault(fold(n), []).append(em)

    fav = sum(1 for _g, _n, em in rows if STAR in em)
    gem = sum(1 for _g, _n, em in rows if GEM in em)
    want_fav = sum(1 for _n, _g, m in USER_PROPS if m == STAR)
    want_gem = sum(1 for _n, _g, m in USER_PROPS if m == GEM)
    print(f"favorites {fav} (want {want_fav}) · gems {gem} (want {want_gem})")
    if fav != want_fav:
        fail(f"expected {want_fav} favorites, got {fav}")
    if gem != want_gem:
        fail(f"expected {want_gem} gems, got {gem}")

    # Every listed prop present with the right marker, in the right game.
    for name, game, marker in USER_PROPS:
        lookup = fold(RESOLVED.get(name, name))
        if game is None:
            ems = by_name.get(lookup)
            if not ems:
                fail(f"prop missing from sheet: {name}")
                continue
            em = ems[0]
        else:
            em = by_key.get((game, lookup))
            if em is None:
                fail(f"prop missing from sheet: {name} [{game}]")
                continue
        label = name if game is None else f"{name} [{game}]"
        if marker == STAR and STAR not in em:
            fail(f"{label} should be a favorite (star)")
        if marker == GEM and GEM not in em:
            fail(f"{label} should be a hidden gem")
        if marker == "" and (STAR in em or GEM in em):
            fail(f"{label} should have no star/gem, got {em!r}")

    # Games and park/split header coverage
    # gameMeta embeds escaped quotes around the pitcher-meta spans, so a plain [^"]*
    # capture stops after the park segment and hides the pitcher splits.
    metas = re.findall(r'gameMeta: "((?:[^"\\]|\\.)*)"', html)
    print(f"games: {len(titles)}")
    if len(titles) != GAMECOUNT:
        fail(f"expected {GAMECOUNT} games, got {len(titles)}")
    for t, meta in zip(titles, metas):
        gkey = t.split(" - ")[0]
        if "Park " not in meta:
            fail(f"game missing park %: {t}")
        if "LHB" not in meta or "RHB" not in meta:
            fail(f"game missing hand park split: {t}")
        if meta.count("pitcher-meta") < 2:
            if gkey in SINGLE_SPLIT_GAMES:
                warns.append(f"{gkey}: one SP split only — PropFinder shipped no 8/17 row for that arm")
            else:
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
        gm = re.search(r"vs ([^(]+?) " + GLOVE, t) or re.search(r"- ([^(]+?) " + GLOVE, t)
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
    body = re.sub(r'<script[^>]*straights-history-data.*?</script>', "", html, flags=re.S)
    body_folded = fold(body)
    for name in STALE_8_16:
        if fold(name) in body_folded:
            fail(f"stale 8/16 content on sheet: {name}")
    for name in SUPERSEDED_PROBABLES:
        if fold(name) in body_folded:
            fail(f"superseded probable still on sheet: {name}")

    # Date correctness
    if f"{WEEKDAY}, {DATE_TEXT}" not in html:
        fail(f"hero must read {WEEKDAY}, {DATE_TEXT}")
    for wrong in ("Sunday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"):
        if f"{wrong}, {DATE_TEXT}" in html:
            fail(f"wrong weekday for {DATE_TEXT}: {wrong}")
    if f'<meta name="sheet-date" content="{DATE}">' not in html:
        fail(f"sheet-date meta must be {DATE}")

    # Regression guard for the CWS/WSH park-key aliasing bug: Ballpark Pal ships these
    # as CHW / WAS, and the old pair-by-pair alias map dropped unseen matchups.
    for gkey in ("CWS @ CHC",):
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
