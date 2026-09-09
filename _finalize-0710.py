#!/usr/bin/env python3
"""One-off: finalize 7/10 patch + build RAW_PROPS."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = [
    "Riley Greene⭐",
    "Kyle Schwarber⭐",
    "Edmundo Sosa",
    "Bryan Reynolds",
    "Ryan O'Hearn",
    "Esmerlyn Valdez",
    "Brandon Lowe",
    "Jake Bauers",
    "Garrett Mitchell",
    "Brice Turang",
    "James Wood",
    "Curtis Mead",
    "Dylan Crews",
    "Ben Rice⭐",
    "Austin Wells",
    "Max Schuemann",
    "Trent Grisham",
    "Pete Alonso",
    "Tyler O'Neill",
    "Samuel Basallo",
    "Jac Caglianone⭐",
    "Michael Massey",
    "Lane Thomas",
    "Sal Stewart",
    "Elly De La Cruz",
    "Pete Crow Armstrong⭐",
    "Seiya Suzuki",
    "Ian Happ",
    "Michael Conforto",
    "Hunter Feduccia",
    "Dominic Canzone",
    "Cole Young",
    "Mitch Garver",
    "Heriberto Hernandez⭐",
    "Griffin Conine",
    "Leo Jimenez",
    "Rhys Hoskins",
    "Juan Soto⭐",
    "AJ Ewing",
    "Wilyer Abreu",
    "Jarren Duran⭐",
    "Kyle Teel💎",
    "Junior Perez",
    "Nick Kurtz⭐",
    "Shea Langeliers⭐",
    "Brandon Nimmo",
    "Joc Pederson",
    "Yordan Alvarez⭐",
    "Taylor Trammell💎",
    "Christian Walker",
    "Kody Clemens",
    "Josh Bell",
    "Mike Trout⭐",
    "Josh Lowe",
    "Jordan Walker⭐",
    "Nelson Velazquez💎",
    "Matt Olson⭐",
    "Joey Bart💎",
    "Drake Baldwin",
    "Mike Yastrzemski",
    "Manny Machado⭐",
    "Fernando Tatis Jr.",
    "Luis Campusano",
    "Kazuma Okamoto⭐",
    "George Springer",
    "Shohei Ohtani",
    "Max Muncy",
    "Dalton Rushing",
    "Mookie Betts⭐",
    "Max Kepler⭐",
    "Ketel Marte",
    "Corbin Carroll",
    "Rafael Devers",
    "Heliot Ramos⭐",
    "Bryce Eldridge",
    "Victor Bericoto💎",
    "Hunter Goodman⭐",
    "Edouard Julien",
]

ALIASES = {
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "AJ Ewing": "A.J. Ewing",
    "Fernando Tatis Jr.": "Fernando Tatis Jr.",
}

PITCHER_HAND = {
    "Aaron Nola": "R",
    "Jack Flaherty": "R",
    "Brandon Sproat": "R",
    "Braxton Ashcraft": "R",
    "Ryan Weathers": "L",
    "Carson Palmquist": "L",
    "Zack Littell": "R",
    "Luinder Avila": "R",
    "Brandon Young": "R",
    "Shota Imanaga": "L",
    "Hunter Greene": "R",
    "Parker Messick": "L",
    "Sandy Alcantara": "R",
    "Luis Castillo": "R",
    "Nick Martinez": "R",
    "Sonny Gray": "R",
    "Nolan McLean": "R",
    "Aaron Civale": "R",
    "Sean Burke": "R",
    "Hunter Brown": "R",
    "Cal Quantrill": "R",
    "Grayson Rodriguez": "R",
    "Zebby Matthews": "R",
    "Chris Sale": "L",
    "Kyle Leahy": "R",
    "Shane Bieber": "R",
    "JP Sears": "L",
    "Eduardo Rodriguez": "L",
    "Shohei Ohtani": "R",
    "Tanner Gordon": "R",
    "Robbie Ray": "L",
}


def patch_build() -> None:
    path = ROOT / "build-0710-from-csv.py"
    text = path.read_text(encoding="utf-8")

    # Replace RAW_PROPS block
    props_body = ",\n".join(f'    "{p}"' for p in RAW_PROPS)
    text = re.sub(
        r"RAW_PROPS = \[.*?\n\]",
        f"RAW_PROPS = [\n{props_body},\n]",
        text,
        count=1,
        flags=re.S,
    )

    aliases_body = ",\n".join(f'    "{k}": "{v}"' for k, v in ALIASES.items())
    text = re.sub(
        r"ALIASES = \{.*?\}",
        f"ALIASES = {{\n{aliases_body},\n}}",
        text,
        count=1,
        flags=re.S,
    )

    hand_body = ",\n".join(f'    "{k}": "{v}"' for k, v in PITCHER_HAND.items())
    text = re.sub(
        r"PITCHER_HAND = \{.*?\}",
        f"PITCHER_HAND = {{\n{hand_body},\n}}",
        text,
        count=1,
        flags=re.S,
    )

    # Park alias for ATH @ CWS
    if '"ATH @ CWS": "ATH @ CHW"' not in text:
        text = text.replace(
            '"BOS @ CWS": "BOS @ CHW",',
            '"BOS @ CWS": "BOS @ CHW",\n        "ATH @ CWS": "ATH @ CHW",\n        "NYY @ WSH": "NYY @ WAS",',
        )

    # Output games file name already 0710 from bulk replace
    text = text.replace("_games-0710.txt", "_games-0710.txt")
    text = text.replace("2026-07-09 MLB", "2026-07-10 MLB")

    path.write_text(text, encoding="utf-8")
    print("updated", path.name)


def patch_preview() -> None:
    path = ROOT / "patch-0710-preview.py"
    text = path.read_text(encoding="utf-8")

    text = text.replace(
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-07-08.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-07-09.html"',
    )

    # Clear straight locks
    text = re.sub(
        r"# 7/10.*?\nstraight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}",
        "# 7/10: no client straight locks yet — auto-pick until user chooses.\n"
        "_o05_lock = None\n"
        "_o15_lock = None\n"
        "if _o05_lock and _o15_lock and _o05_lock[\"game_key\"] != _o15_lock[\"game_key\"]:\n"
        "    _o05_ok = _o05_lock in straight_o05_pool(straight_rows, strict=True)\n"
        "    _o15_ok = (\n"
        "        _o15_lock[\"hr\"] >= 2\n"
        "        and _o15_lock[\"near\"] >= 2\n"
        "        and _o15_lock[\"split\"] >= 0.15\n"
        "        and not (_o15_lock[\"split\"] <= 0.0 and _o15_lock[\"risk\"] <= 0.0)\n"
        "    )\n"
        "    if _o05_ok and _o15_ok:\n"
        "        straight_o05 = _o05_lock\n"
        "        straight_o15 = _o15_lock\n"
        "straight_names = {straight_o05[\"name\"], straight_o15[\"name\"]}",
        text,
        count=1,
        flags=re.S,
    )

    fav_new = """_fav3_pick_order = [
    "Riley Greene",
    "Kyle Schwarber",
    "Ben Rice",
    "Jac Caglianone",
    "Pete Crow-Armstrong",
    "Heriberto Hernandez",
    "Juan Soto",
    "Jarren Duran",
    "Nick Kurtz",
    "Shea Langeliers",
    "Yordan Alvarez",
    "Jordan Walker",
    "Matt Olson",
    "Manny Machado",
    "Kazuma Okamoto",
    "Mookie Betts",
    "Max Kepler",
    "Heliot Ramos",
    "Hunter Goodman",
    "Mike Trout",
]"""
    text = re.sub(r"_fav3_pick_order = \[[^\]]+\]", fav_new, text, count=1, flags=re.S)

    # Manifest: ensure July 9 archive entry exists after current
    if '"date": "2026-07-09"' not in text:
        text = text.replace(
            '{"date": SHEET_DATE, "label": "July 10, 2026 — current slate", "href": "index.html"},\n'
            '        {"date": "2026-07-08", "label": "July 8, 2026", "href": "archive/2026-07-08.html"},',
            '{"date": SHEET_DATE, "label": "July 10, 2026 — current slate", "href": "index.html"},\n'
            '        {"date": "2026-07-09", "label": "July 9, 2026", "href": "archive/2026-07-09.html"},\n'
            '        {"date": "2026-07-08", "label": "July 8, 2026", "href": "archive/2026-07-08.html"},',
        )

    path.write_text(text, encoding="utf-8")
    print("updated", path.name)
    for needle in ("ARCHIVE_PREVIOUS", "_o05_lock = None", "_fav3_pick_order", "July 9, 2026"):
        print(needle, "OK" if needle in path.read_text(encoding="utf-8") or (
            needle == "_o05_lock = None" and '_o05_lock = None' in path.read_text(encoding="utf-8")
        ) else "MISSING")


def patch_audit() -> None:
    path = ROOT / "audit-0710.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace("EXPECTED_GAMES = 13", "EXPECTED_GAMES = 15")
    text = text.replace("EXPECTED_PROPS = 77", "EXPECTED_PROPS = 78")
    path.write_text(text, encoding="utf-8")
    print("updated", path.name)


if __name__ == "__main__":
    patch_build()
    patch_preview()
    patch_audit()
