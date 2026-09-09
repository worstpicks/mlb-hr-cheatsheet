#!/usr/bin/env python3
"""Customize cloned 7/30 scripts for 2026-07-31 slate."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Pete Crow-Armstrong⭐",
    "Miguel Amaya",
    "Justin Dean",
    "Ben Rice",
    "Spencer Jones",
    "Jazz Chisholm Jr.",
    "Austin Wells",
    "Elly De La Cruz⭐",
    "Matt McLain",
    "Eugenio Suarez",
    "Bryan Reynolds⭐",
    "Esmerlyn Valdez",
    "Endy Rodriguez",
    "Brandon Lowe",
    "Gunnar Henderson💎",
    "Dylan Beavers",
    "Coby Mayo💎",
    "Tyler O'Neill",
    "Bryce Harper",
    "Derek Hill💎",
    "Trea Turner",
    "George Springer💎",
    "Brandon Valenzuela",
    "Jimmy Crooks💎",
    "Alec Burleson",
    "Victor Mesa Jr.⭐",
    "Junior Caminero",
    "Munetaka Murakami",
    "Sam Antonacci",
    "Colson Montgomery",
    "Brett Baty⭐",
    "Francisco Alvarez",
    "Joe Mack",
    "Griffin Conine",
    "Kyle Stowers⭐",
    "Heriberto Hernandez",
    "Travis Bazzana",
    "Rhys Hoskins",
    "Brayan Rocchio",
    "Corbin Carroll",
    "Austin Riley",
    "Matt Olson",
    "Ozzie Albies",
    "Luis Garcia Jr.⭐",
    "James Wood",
    "Daylen Lile",
    "Yordan Alvarez",
    "Taylor Trammell💎",
    "Joc Pederson",
    "Wyatt Langford",
    "Alejandro Osuna",
    "Hunter Goodman💎",
    "Willi Castro💎",
    "Mickey Moniak",
    "Carter Jensen",
    "Salvador Perez",
    "Starling Marte",
    "John Rave",
    "Zach Neto",
    "Travis d'Arnaud",
    "Jo Adell💎",
    "Jake Bauers💎",
    "Andrew Vaughn",
    "Christian Yelich",
    "Nick Kurtz💎",
    "Tyler Soderstrom💎",
    "Lawrence Butler⭐",
    "Tommy White",
    "Hao-Yu Lee",
    "James Outman",
    "Eduardo Valencia",
    "Dillon Dingler",
    "Manny Machado💎",
    "Fernando Tatis Jr.",
    "Ty France",
    "Jackson Merrill",
    "Drew Gilbert",
    "Rafael Devers",
    "Bryce Eldridge",
    "Grant McCray",
    "Luke Raley",
    "Randy Arozarena",
    "Mitch Garver",
    "Rob Refsnyder💎",
    "Kody Clemens⭐",
    "Ryan Jeffers",
    "Royce Lewis💎",
]"""

ALIASES = """ALIASES = {
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Pete Crow-Armstrong": "Pete Crow-Armstrong",
    "Luis Garcia Jr": "Luis Garcia Jr.",
    "Luis Garcia Jr.": "Luis Garcia Jr.",
    "Jazz Chisholm Jr": "Jazz Chisholm Jr.",
    "Jazz Chisholm Jr.": "Jazz Chisholm Jr.",
    "Fernando Tatis Jr": "Fernando Tatis Jr.",
    "Fernando Tatis Jr.": "Fernando Tatis Jr.",
    "Victor Mesa Jr": "Victor Mesa Jr.",
    "Victor Mesa Jr.": "Victor Mesa Jr.",
    "Hao Yu lee": "Hao-Yu Lee",
    "Hao Yu Lee": "Hao-Yu Lee",
    "Hao-Yu Lee": "Hao-Yu Lee",
    "Travis d Arnaud": "Travis d'Arnaud",
    "Travis d'Arnaud": "Travis d'Arnaud",
    "Tyler ONeill": "Tyler O'Neill",
    "Tyler O'Neill": "Tyler O'Neill",
}"""

HANDS = """PITCHER_HAND = {
    "Will Warren": "R",
    "Shota Imanaga": "L",
    "Paul Skenes": "R",
    "Hunter Greene": "R",
    "Brian Keller": "R",
    "Brandon Young": "R",
    "Kyle Leahy": "R",
    "Dylan Cease": "R",
    "Mitch Bratt": "L",
    "Tanner Bibee": "R",
    "Janson Junk": "R",
    "Freddy Peralta": "R",
    "Erick Fedde": "R",
    "Nick Martinez": "R",
    "Foster Griffin": "L",
    "Bryce Elder": "R",
    "Nathan Eovaldi": "R",
    "Hunter Brown": "R",
    "Michael Wacha": "R",
    "Tomoyuki Sugano": "R",
    "Shane Drohan": "L",
    "Ryan Johnson": "R",
    "Casey Mize": "R",
    "Jeffrey Springs": "L",
    "Carson Whisenhunt": "L",
    "German Marquez": "R",
    "Zebby Matthews": "R",
    "Bryce Miller": "R",
    "Ranger Suarez": "L",
    "Yoshinobu Yamamoto": "R",
}"""

# --- build-0731-from-csv.py ---
src = (ROOT / "build-0730-from-csv.py").read_text(encoding="utf-8")
src = src.replace("2026-07-30", "2026-07-31")
src = src.replace("0730", "0731")
src = src.replace("07-30", "07-31")
src = re.sub(r"RAW_PROPS = \[.*?\n\]", RAW_PROPS, src, count=1, flags=re.S)
src = re.sub(r"ALIASES = \{.*?\n\}", ALIASES, src, count=1, flags=re.S)
src = re.sub(r"PITCHER_HAND = \{.*?\n\}", HANDS, src, count=1, flags=re.S)
src = re.sub(
    r"ATL_NYM_DH_SPECS: dict\[str, dict\] = \{.*?\n\}",
    "ATL_NYM_DH_SPECS: dict[str, dict] = {}",
    src,
    count=1,
    flags=re.S,
)
(ROOT / "build-0731-from-csv.py").write_text(src, encoding="utf-8")
print("wrote build-0731-from-csv.py")

# --- patch / verify / audit ---
for src_name, dst_name in [
    ("patch-0730-preview.py", "patch-0731-preview.py"),
    ("verify-summary-0730.py", "verify-summary-0731.py"),
    ("_audit_0730_final.py", "_audit_0731_final.py"),
]:
    text = (ROOT / src_name).read_text(encoding="utf-8")
    text = text.replace("2026-07-30", "2026-07-31")
    text = text.replace("0730", "0731")
    text = text.replace("July 30, 2026", "July 31, 2026")
    text = text.replace("Thursday, July 30, 2026", "Friday, July 31, 2026")
    text = text.replace("2026-07-29.html", "2026-07-30.html")
    text = text.replace("2026-07-29", "TEMP_PREV")
    # carefully: after replacing 07-30->07-31, archive previous should be 07-30
    # First restore archive date handling from a clean copy approach:
    (ROOT / dst_name).write_text(text, encoding="utf-8")
    print("draft", dst_name)

# Re-copy patch from 0730 and do careful replacements
text = (ROOT / "patch-0730-preview.py").read_text(encoding="utf-8")
reps = [
    ("Patch preview sheet to 2026-07-30.", "Patch preview sheet to 2026-07-31."),
    (
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-07-29.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-07-30.html"',
    ),
    ('SHEET_DATE = "2026-07-30"', 'SHEET_DATE = "2026-07-31"'),
    (
        'spec = importlib.util.spec_from_file_location("build0730", ROOT / "build-sheet-2026-07-30.py")',
        'spec = importlib.util.spec_from_file_location("build0731", ROOT / "build-sheet-2026-07-31.py")',
    ),
    (
        '{"date": SHEET_DATE, "label": "July 30, 2026 — current slate", "href": "index.html"}',
        '{"date": SHEET_DATE, "label": "July 31, 2026 — current slate", "href": "index.html"}',
    ),
    (
        "<p>Thursday, July 30, 2026 — Worst Pickz HR cheat sheet",
        "<p>Friday, July 31, 2026 — Worst Pickz HR cheat sheet",
    ),
]
for old, new in reps:
    if old not in text:
        raise SystemExit(f"patch missing: {old!r}")
    text = text.replace(old, new)

# Manifest: promote 7/30, keep 7/29
text = text.replace(
    """    if "2026-07-29" in old or ARCHIVE_PREVIOUS.is_file():
        old["2026-07-29"] = {
            "date": "2026-07-29",
            "label": "July 29, 2026",
            "href": "archive/2026-07-29.html",
        }
    if "2026-07-27" not in old:
        old["2026-07-27"] = {
            "date": "2026-07-27",
            "label": "July 27, 2026",
            "href": "archive/2026-07-27.html",
        }
    ordered = [
        {"date": SHEET_DATE, "label": "July 31, 2026 — current slate", "href": "index.html"},
    ]
    for date in [
        "2026-07-29",
        "2026-07-27",""",
    """    if "2026-07-30" in old or ARCHIVE_PREVIOUS.is_file():
        old["2026-07-30"] = {
            "date": "2026-07-30",
            "label": "July 30, 2026",
            "href": "archive/2026-07-30.html",
        }
    if "2026-07-29" not in old:
        old["2026-07-29"] = {
            "date": "2026-07-29",
            "label": "July 29, 2026",
            "href": "archive/2026-07-29.html",
        }
    if "2026-07-27" not in old:
        old["2026-07-27"] = {
            "date": "2026-07-27",
            "label": "July 27, 2026",
            "href": "archive/2026-07-27.html",
        }
    ordered = [
        {"date": SHEET_DATE, "label": "July 31, 2026 — current slate", "href": "index.html"},
    ]
    for date in [
        "2026-07-30",
        "2026-07-29",
        "2026-07-27",""",
)

# Fix elif branches for archive dates
text = text.replace(
    """        elif date == "2026-07-29":
            ordered.append(
                {
                    "date": "2026-07-29",
                    "label": "July 29, 2026",
                    "href": "archive/2026-07-29.html",
                }
            )
        elif date == "2026-07-27":""",
    """        elif date == "2026-07-30":
            ordered.append(
                {
                    "date": "2026-07-30",
                    "label": "July 30, 2026",
                    "href": "archive/2026-07-30.html",
                }
            )
        elif date == "2026-07-29":
            ordered.append(
                {
                    "date": "2026-07-29",
                    "label": "July 29, 2026",
                    "href": "archive/2026-07-29.html",
                }
            )
        elif date == "2026-07-27":""",
)

(ROOT / "patch-0731-preview.py").write_text(text, encoding="utf-8")
print("wrote patch-0731-preview.py")

# verify
v = (ROOT / "verify-summary-0730.py").read_text(encoding="utf-8")
v = v.replace("0730", "0731").replace("2026-07-30", "2026-07-31").replace("July 30", "July 31")
(ROOT / "verify-summary-0731.py").write_text(v, encoding="utf-8")
print("wrote verify-summary-0731.py")

# audit
a = (ROOT / "_audit_0730_final.py").read_text(encoding="utf-8")
a = (
    a.replace("2026-07-30", "2026-07-31")
    .replace("Thursday, July 30, 2026", "Friday, July 31, 2026")
    .replace("July 30, 2026", "July 31, 2026")
    .replace("0730", "0731")
)
# archive previous becomes 7/30
a = a.replace('archive" / "2026-07-29.html"', 'archive" / "2026-07-30.html"')
a = a.replace('content="2026-07-29"', 'content="2026-07-30"')
a = a.replace("7/29 archive", "7/30 archive")
# prop/game counts unknown yet — placeholder, fix after build
(ROOT / "_audit_0731_final.py").write_text(a, encoding="utf-8")
print("wrote _audit_0731_final.py")
