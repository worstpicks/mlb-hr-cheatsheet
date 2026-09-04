#!/usr/bin/env python3
"""Deep content audit for the 2026-09-04 sheet: prop coverage, markers, bums, staleness."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-09-04"
PREVIEW = ROOT / "preview" / "index.html"

STAR = "⭐"
GEM = "\U0001f48e"
GLOVE = "\U0001f9e4"

GAMECOUNT = 15
WEEKDAY = "Friday"
DATE_TEXT = "September 4, 2026"

# (name, game override, marker), generated from build-0821-from-csv.py RAW_PROPS so
# the audit cannot drift from what was actually built. Two Max Muncys again today
# (ATH DH and LAD 3B). The listed prop is the Dodgers one -- it sits inside the
# PIT @ LAD run of the user's list and the listed hand is L -- so it carries its game.
ANY = None
USER_PROPS: list[tuple[str, str | None, str]] = [
    ('Elly De La Cruz', ANY, STAR),
    ('Tyler Stephenson', ANY, ""),
    ('Sal Stewart', ANY, ""),
    ('Matt McLain', ANY, ""),
    ('Christian Yelich', ANY, ""),
    ('Bo Naylor', ANY, ""),
    ('William Contreras', ANY, STAR),
    ('Jackson Chourio', ANY, GEM),
    ('Luis Lara', ANY, ""),
    ('Kyle Schwarber', ANY, ""),
    ('J.T. Realmuto', ANY, ""),
    ('Alec Bohm', ANY, ""),
    ('Ronald Acuna Jr.', ANY, STAR),
    ('Lane Thomas', ANY, STAR),
    ('Oneil Cruz', ANY, ""),
    ('Bryan Reynolds', ANY, GEM),
    ('Zach Neto', ANY, STAR),
    ('Moises Ballesteros', ANY, ""),
    ("Travis d'Arnaud", ANY, ""),
    ('Pete Alonso', ANY, STAR),
    ('Mickey Gasper', ANY, STAR),
    ('Roman Anthony', ANY, STAR),
    ('Adley Rutschman', ANY, ""),
    ('Trevor Story', ANY, ""),
    ('Mark Vientos', ANY, STAR),
    ('Bo Bichette', ANY, STAR),
    ('Juan Soto', ANY, ""),
    ('Rafael Devers', ANY, STAR),
    ('Jung Hoo Lee', ANY, ""),
    ('Heriberto Hernandez', ANY, STAR),
    ('Agustin Ramirez', ANY, ""),
    ('Pete Crow Armstrong', ANY, STAR),
    ('Michael Busch', ANY, ""),
    ('Jo Adell', ANY, STAR),
    ('Gleyber Torres', ANY, ""),
    ('Hao Yu Lee', ANY, ""),
    ('Munetaka Murakami', ANY, GEM),
    ('Tristan Peters', ANY, ""),
    ('Josh Bell', ANY, GEM),
    ('Trevor Larnach', ANY, GEM),
    ('Kody Clemens', ANY, ""),
    ('Joc Pederson', ANY, STAR),
    ('Brandon Nimmo', ANY, STAR),
    ('Corey Seager', ANY, ""),
    ('Jake Burger', ANY, GEM),
    ('Jonathan Aranda', ANY, STAR),
    ('Yandy Diaz', ANY, GEM),
    ('Junior Caminero', ANY, ""),
    ('Carter Jensen', ANY, STAR),
    ('Jac Caglianone', ANY, ""),
    ('Salvador Perez', ANY, ""),
    ('Kazuma Okamoto', ANY, STAR),
    ('Alejandro Kirk', ANY, ""),
    ('George Springer', ANY, ""),
    ('Yordan Alvarez', ANY, STAR),
    ('LaMonte Wade Jr.', ANY, ""),
    ('Yainer Diaz', ANY, ""),
    ('Lars Nootbaar', ANY, STAR),
    ('Tim Tawa', ANY, ""),
    ('Ketel Marte', ANY, ""),
    ('Zac Veen', ANY, GEM),
    ('Jake McCarthy', ANY, ""),
    ('Hunter Goodman', ANY, ""),
    ('Mickey Moniak', ANY, STAR),
    ('Jordan Walker', ANY, STAR),
    ('Leonardo Bernal', ANY, GEM),
    ('Alec Burleson', ANY, GEM),
    ('Jase Bowen', ANY, ""),
    ('Freddy Fermin', ANY, ""),
    ('Jackson Merrill', ANY, ""),
    ('Spencer Jones', ANY, STAR),
    ('Cody Bellinger', ANY, GEM),
    ('Austin Wells', ANY, GEM),
    ('Dominic Canzone', ANY, GEM),
    ('Cal Raleigh', ANY, ""),
    ('Lazaro Montes', ANY, ""),
    ('Julio Rodriguez', ANY, GEM),
    ('Randy Arozarena', ANY, ""),
    ('Michael Stefanic', ANY, ""),
    ('Zack Gelof', ANY, ""),
    ('Lawrence Butler', ANY, GEM),
    ('Jonah Heim', ANY, ""),
    ('Henry Bolte', ANY, ""),
    ('Teoscar Hernandez', ANY, STAR),
    ('Will Smith', ANY, STAR),
    ('Andres Chaparro', ANY, ""),
    ('James Wood', ANY, ""),
    ('Yohandy Morales', ANY, ""),
]

# Name the sheet legitimately uses that differs from the user's spelling.
RESOLVED: dict[str, str] = {
    # The sheet renders each row under the spelling the prop list used, so nothing
    # needs remapping today. (name_lookup_key folds hyphens, which is what lets
    # "Pete Crow Armstrong" find PropFinder's "Pete Crow-Armstrong" at build time.)
}

# 8/20-only content that must not survive onto the 8/21 sheet. Derived as
# (yesterday's probables) - (today's probables), so an arm working both days can
# never fail a correct sheet.
STALE_PREV_DAY = [
    "Blade Tidwell",
    "Brandon Young",
    "Cal Quantrill",
    "Hunter Brown",
    "Jack Perkins",
    "Jake Bennett",
    "José Soriano",
    "Kade Anderson",
    "Kevin Gausman",
    "Lake Bachar",
    "Logan Henderson",
    "Luis Castillo",
    "Michael Wacha",
    "Quinn Mathews",
    "Sandy Alcantara",
    "Shane McClanahan",
    "Tanner Bibee",
    "Tarik Skubal",
]

# HR risk >= 0.95 on today's hr-targets export.
EXPECTED_BUMS = {"Jameson Taillon", "Shota Imanaga", "Kade Morris"}

# Every game carries two pitcher segments. Trevor Williams is missing from the
# HR-risk export -- PropFinder built it around Kumar Rocker -- so his header
# renders the measured BAA lane carried from his 2026-08-03 export.
SINGLE_SPLIT_GAMES: set[str] = set()

# Probables replaced after the PropFinder export, both confirmed against the MLB
# Stats API. Neither may survive anywhere on the sheet. (Will Dion was never a real
# probable -- the pasted block was stale; Washington's arm is and was Brad Lord.)
SUPERSEDED_PROBABLES: list[str] = ["Kumar Rocker"]  # TEX export arm, replaced by Trevor Williams

errs: list[str] = []
warns: list[str] = []


def fail(msg: str) -> None:
    errs.append(msg)


def _suffix_key(norm: str) -> str:
    """Drop a generational suffix so name variants of one player collapse."""
    for suf in ("jr", "sr", "ii", "iii", "iv"):
        if norm.endswith(suf) and len(norm) > len(suf) + 2:
            return norm[: -len(suf)]
    return norm


def _best_slot(slots: dict) -> dict:
    """Keep the LOWEST batting order per human.

    A lineup can list the same player twice under name variants -- "Fernando
    Tatis" at order 1 and "Fernando Tatis Jr." at order 10. Taking whichever
    landed last made the real leadoff hitter look benched.
    """
    best = {}
    for name, slot in slots.items():
        base = _suffix_key(name)
        if base not in best or slot < best[base]:
            best[base] = slot
    return {name: best[_suffix_key(name)] for name in slots}


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
    # Count GLOVES, not titles: a game can have a bum on both mounds (MIN @ ATH today
    # carries Matthews and Springs), so one title can legitimately hold two.
    glove_count = sum(t.count(GLOVE) for t in titles)
    if glove_count != len(EXPECTED_BUMS):
        fail(f"expected {len(EXPECTED_BUMS)} gloved arms, got {glove_count}")

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
    for name in STALE_PREV_DAY:
        if fold(name) in body_folded:
            fail(f"stale prior-slate content on sheet: {name}")
    for name in SUPERSEDED_PROBABLES:
        if fold(name) in body_folded:
            fail(f"superseded probable still on sheet: {name}")

    # The hits rubric ranks on lineup slot. If the research JSON is missing when the
    # patch computes ranks, every input silently falls back to a league default and the
    # ticket fills with nine-hole and bench bats -- which is exactly what shipped on
    # 8/18-8/20 before the ordering fix. Assert the outcome, not the plumbing.
    import json as _json, unicodedata as _ud
    rjson = ROOT / "preview" / "data" / f"research-{DATE}.json"
    if rjson.is_file():
        def _fold2(n):
            b = _ud.normalize("NFKD", n or "")
            b = "".join(c for c in b if not _ud.combining(c))
            return re.sub(r"[^a-z0-9]", "", b.lower())
        _d = _json.loads(rjson.read_text(encoding="utf-8"))
        _slot = {}
        for _g in _d.get("games", []):
            for _side in ("awayLineup", "homeLineup"):
                for _pl in _g.get(_side) or []:
                    if _pl.get("order"):
                        _slot[_fold2(_pl["name"])] = _pl["order"]
        _slot = _best_slot(_slot)
        _m = re.search(r"data-goblin-gambly-lines='([^']*hits[^']*)'", html)
        if _m:
            import html as _htmlmod
            _legs = [l.split(" - ")[0] for l in _json.loads(_htmlmod.unescape(_m.group(1)))]
            def _slot_of(n):
                k = _fold2(n)
                v = _slot.get(k) or _slot.get(_suffix_key(k))
                if v is None:
                    for _k, _v in _slot.items():
                        if _suffix_key(_k) == _suffix_key(k):
                            return _v
                return v
            _bench = [n for n in _legs if (_slot_of(n) or 0) > 9]
            if _bench:
                fail(f"hits parlay contains bench bats (lineup slot >9): {_bench}")
            _known = [_slot[_fold2(n)] for n in _legs if _fold2(n) in _slot]
            if _known and sum(_known) / len(_known) > 5.0:
                fail(
                    f"hits parlay mean lineup slot {sum(_known)/len(_known):.1f} > 5.0 — "
                    "expected-PA ranking looks inert"
                )
    else:
        fail(f"research JSON missing for {DATE}; hits rubric cannot rank on lineup slot")

    # No pick board may carry a bat who is not in a posted lineup. The hits parlay
    # has been guarded since 8/20; the HR boards were not, and today's O1.5 went to
    # a slot-12 bench bat before this check existed. Rows may still be LISTED --
    # only picking is barred.
    if rjson.is_file():
        _lineup = {}
        for _g in _json.loads(rjson.read_text(encoding="utf-8")).get("games", []):
            for _side in ("awayLineup", "homeLineup"):
                for _pl in _g.get(_side) or []:
                    if _pl.get("order"):
                        _lineup[_fold2(_pl["name"])] = _pl["order"]
        _lineup = _best_slot(_lineup)
        import html as _htmlmod2
        for _m2 in re.finditer(r"data-(?:goblin-gambly-lines|gambly-line)='([^']*)'", html):
            try:
                _legs2 = _json.loads(_htmlmod2.unescape(_m2.group(1)))
            except ValueError:
                continue
            for _leg in _legs2:
                _nm = _leg.split(" - ")[0]
                _sl = _lineup.get(_fold2(_nm))
                if _sl is None:
                    _sl = _lineup.get(_suffix_key(_fold2(_nm)))
                if _sl is None:
                    for _k, _v in _lineup.items():
                        if _suffix_key(_k) == _suffix_key(_fold2(_nm)):
                            _sl = _v
                            break
                if (_sl or 99) > 9:
                    fail(f"pick board carries a bat not in a posted lineup: {_nm}")

    # The owner asked for no "no HR risk" placeholders anywhere on the board: either
    # a real number or nothing at all.
    for phrase in ("no MLB HR data yet", "no PropFinder HR risk", "split/risk data unavailable"):
        if phrase in html:
            fail(f"missing-HR-risk placeholder on sheet: {phrase!r}")

    # Date correctness
    if f"{WEEKDAY}, {DATE_TEXT}" not in html:
        fail(f"hero must read {WEEKDAY}, {DATE_TEXT}")
    # Derive the wrong-weekday set instead of listing it: hardcoding the list meant
    # the correct weekday stayed in it after a date change and failed a correct sheet.
    all_days = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
    for wrong in (d for d in all_days if d != WEEKDAY):
        if f"{wrong}, {DATE_TEXT}" in html:
            fail(f"wrong weekday for {DATE_TEXT}: {wrong}")
    if f'<meta name="sheet-date" content="{DATE}">' not in html:
        fail(f"sheet-date meta must be {DATE}")

    # Regression guard for the CWS/WSH park-key aliasing bug: Ballpark Pal ships
    # these as CHW / WAS. Derive the games to check from the slate rather than
    # hardcoding a pair -- a hardcoded pair silently passes on every day those
    # clubs are not playing, which is most days.
    alias_re = re.compile(r"\b(CWS|WSH)\b")
    alias_games = [t.split(" - ")[0] for t in titles if alias_re.search(t.split(" - ")[0])]
    if not alias_games:
        warns.append("no CWS/WSH game on this slate - alias guard not exercised")
    for gkey in alias_games:
        m = re.search(
            r'title: "' + re.escape(gkey) + r'[^"]*".*?gameMeta: "((?:[^"\\]|\\.)*)"',
            html,
            re.S,
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
