#!/usr/bin/env python3
"""Scaffold 2026-08-10 build/patch/verify from 8/9 templates."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Jesus Sanchez💎",
    "Brandon Valenzuela",
    "Wilyer Abreu💎",
    "Willson Contreras⭐",
    "Masataka Yoshida",
    "Jake Rogers",
    "Matt Olson⭐",
    "Ronald Acuna Jr.⭐",
    "Mike Yastrzemski",
    "Francisco Alvarez💎",
    "Brett Baty⭐",
    "Royce Lewis",
    "Pete Alonso⭐",
    "Leody Taveras💎",
    "Coby Mayo💎",
    "Alec Burleson⭐",
    "Ivan Herrera💎",
    "Bryce Harper",
    "Brandon Marsh",
    "Derek Hill",
    "Jose Siri⭐",
    "Zach Neto",
    "Brandon Nimmo💎",
    "Jake Burger⭐",
    "Corey Seager",
    "Jackson Merrill⭐",
    "Manny Machado⭐",
    "Fernando Tatis Jr.⭐",
    "Jackson Chourio⭐",
    "Jake Bauers",
    "Brice Turang",
    "Max Muncy(ATH)⭐",
    "Henry Bolte",
    "Lawrence Butler",
    "Yandy Diaz💎",
    "Ryan Vilade💎",
    "Tim Tawa",
    "Ryan Waldschmidt",
    "Hunter Goodman",
    "Mickey Moniak⭐",
    "Willi Castro⭐",
    "Osleivis Basabe💎",
    "Taylor Trammell💎",
    "Daulton Varsho⭐",
    "Yordan Alvarez",
    "Teoscar Hernandez",
    "Kyle Tucker⭐",
    "Carter Jensen",
]"""

ALIASES = """ALIASES = {
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Fernando Tatis Jr.": "Fernando Tatis Jr.",
    "Ryan Waldschmdit": "Ryan Waldschmidt",
    "Ryan Waldschmidt": "Ryan Waldschmidt",
    "Max Muncy(ATH)": "Max Muncy",
    "Max Muncy (ATH)": "Max Muncy",
    "Willson Contreras": "Willson Contreras",
    "William Contreras": "William Contreras",
    "Masataka Yoshida": "Masataka Yoshida",
    "Brandon Valenzuela": "Brandon Valenzuela",
    "Jesus Sanchez": "Jesus Sanchez",
    "Wilyer Abreu": "Wilyer Abreu",
    "Francisco Alvarez": "Francisco Alvarez",
    "Brett Baty": "Brett Baty",
    "Pete Alonso": "Pete Alonso",
    "Leody Taveras": "Leody Taveras",
    "Coby Mayo": "Coby Mayo",
    "Alec Burleson": "Alec Burleson",
    "Ivan Herrera": "Ivan Herrera",
    "Jose Siri": "Jose Siri",
    "Brandon Nimmo": "Brandon Nimmo",
    "Jake Burger": "Jake Burger",
    "Jackson Merrill": "Jackson Merrill",
    "Manny Machado": "Manny Machado",
    "Jackson Chourio": "Jackson Chourio",
    "Yandy Diaz": "Yandy Diaz",
    "Ryan Vilade": "Ryan Vilade",
    "Tim Tawa": "Tim Tawa",
    "Hunter Goodman": "Hunter Goodman",
    "Mickey Moniak": "Mickey Moniak",
    "Willi Castro": "Willi Castro",
    "Osleivis Basabe": "Osleivis Basabe",
    "Taylor Trammell": "Taylor Trammell",
    "Daulton Varsho": "Daulton Varsho",
    "Yordan Alvarez": "Yordan Alvarez",
    "Teoscar Hernandez": "Teoscar Hernandez",
    "Kyle Tucker": "Kyle Tucker",
    "Carter Jensen": "Carter Jensen",
    "Henry Bolte": "Henry Bolte",
    "Lawrence Butler": "Lawrence Butler",
    "Derek Hill": "Derek Hill",
    "Jake Rogers": "Jake Rogers",
    "Matt Olson": "Matt Olson",
    "Mike Yastrzemski": "Mike Yastrzemski",
    "Royce Lewis": "Royce Lewis",
    "Bryce Harper": "Bryce Harper",
    "Brandon Marsh": "Brandon Marsh",
    "Zach Neto": "Zach Neto",
    "Corey Seager": "Corey Seager",
    "Jake Bauers": "Jake Bauers",
    "Brice Turang": "Brice Turang",
    "Hayden Wesneski": "Hayden Wesneski",
    "Blade Tidwell": "Blade Tidwell",
    "MacKenzie Gore": "MacKenzie Gore",
    "Reid Detmers": "Reid Detmers",
    "Jameson Taillon": "Jameson Taillon",
    "Christian Scott": "Christian Scott",
    "Bryce Elder": "Bryce Elder",
    "Andrew Painter": "Andrew Painter",
    "Hunter Dobbins": "Hunter Dobbins",
    "Freddy Peralta": "Freddy Peralta",
    "Jacob Lopez": "Jacob Lopez",
    "Logan Henderson": "Logan Henderson",
    "Casey Mize": "Casey Mize",
    "Gabriel Hughes": "Gabriel Hughes",
    "Michael Soroka": "Michael Soroka",
    "Noah Cameron": "Noah Cameron",
    "Tarik Skubal": "Tarik Skubal",
    "Trevor Rogers": "Trevor Rogers",
    "Dean Kremer": "Dean Kremer",
    "Sonny Gray": "Sonny Gray",
}"""

PITCHER_HAND = """PITCHER_HAND = {
    # 8/10 LHP
    "Trevor Rogers": "L",
    "MacKenzie Gore": "L",
    "Reid Detmers": "L",
    "Jacob Lopez": "L",
    "Noah Cameron": "L",
    "Tarik Skubal": "L",
    # 8/10 RHP
    "Sonny Gray": "R",
    "Jameson Taillon": "R",
    "Christian Scott": "R",
    "Bryce Elder": "R",
    "Dean Kremer": "R",
    "Andrew Painter": "R",
    "Hunter Dobbins": "R",
    "Freddy Peralta": "R",
    "Logan Henderson": "R",
    "Casey Mize": "R",
    "Gabriel Hughes": "R",
    "Michael Soroka": "R",
    "Hayden Wesneski": "R",
    "Blade Tidwell": "R",
}"""


def swap_dates(text: str) -> str:
    text = text.replace("2026-08-09", "TEMP_CUR")
    text = text.replace("2026-08-08", "TEMP_PREV")
    text = text.replace("TEMP_CUR", "2026-08-10")
    text = text.replace("TEMP_PREV", "2026-08-09")
    text = text.replace("08-09", "TEMP_MMDD")
    text = text.replace("08-08", "TEMP_PREV_MMDD")
    text = text.replace("TEMP_MMDD", "08-10")
    text = text.replace("TEMP_PREV_MMDD", "08-09")
    text = text.replace("0809", "TEMP_CODE")
    text = text.replace("0808", "TEMP_PREV_CODE")
    text = text.replace("TEMP_CODE", "0810")
    text = text.replace("TEMP_PREV_CODE", "0809")
    text = text.replace("Sunday, August 9, 2026", "Monday, August 10, 2026")
    text = text.replace("Sunday, August 9", "Monday, August 10")
    text = text.replace("August 9, 2026", "August 10, 2026")
    text = text.replace("August 9", "August 10")
    # fix accidental weekday leftovers
    text = text.replace("Sunday, August 10", "Monday, August 10")
    text = text.replace("Saturday, August 10", "Monday, August 10")
    text = text.replace("Tuesday, August 10", "Monday, August 10")
    return text


def main() -> None:
    src_build = ROOT / "build-0809-from-csv.py"
    dst_build = ROOT / "build-0810-from-csv.py"
    text = swap_dates(src_build.read_text(encoding="utf-8"))
    text = re.sub(r"RAW_PROPS = \[.*?\]", RAW_PROPS, text, count=1, flags=re.S)
    text = re.sub(r"ALIASES = \{.*?\}", ALIASES, text, count=1, flags=re.S)
    text = re.sub(
        r"PROBABLE_OVERRIDES = \{.*?\}",
        "PROBABLE_OVERRIDES = {}",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(r"PITCHER_HAND = \{.*?\}", PITCHER_HAND, text, count=1, flags=re.S)
    # Max Muncy (ATH) must land on today's TB @ ATH game, not stale ATH @ MIN.
    text = text.replace(
        'game_override = "LAD @ NYM" if m.group(1).upper() == "LAD" else "ATH @ MIN"',
        'game_override = "KC @ LAD" if m.group(1).upper() == "LAD" else "TB @ ATH"',
    )
    dst_build.write_text(text, encoding="utf-8")
    print("wrote", dst_build.name)

    src_patch = ROOT / "patch-0809-preview.py"
    dst_patch = ROOT / "patch-0810-preview.py"
    ptext = swap_dates(src_patch.read_text(encoding="utf-8"))
    ptext = re.sub(
        r"\n# 8/9 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"\n# 8/9 Goblin judgment:.*?fav3 = _fav3_lock\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "20\d{2}-\d{2}-\d{2}\.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-09.html"',
        ptext,
        count=1,
    )
    ptext = re.sub(
        r'if "2026-08-0[89]" in old or ARCHIVE_PREVIOUS\.is_file\(\):\s*'
        r'old\["2026-08-0[89]"\] = \{[^}]+\}\s*',
        (
            'if "2026-08-09" in old or ARCHIVE_PREVIOUS.is_file():\n'
            '        old["2026-08-09"] = {\n'
            '            "date": "2026-08-09",\n'
            '            "label": "August 9, 2026",\n'
            '            "href": "archive/2026-08-09.html",\n'
            "        }\n    "
        ),
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"for date in \[\n(?:        \"2026-08-\d{2}\",\n){1,5}",
        'for date in [\n        "2026-08-09",\n        "2026-08-08",\n        "2026-08-07",\n        "2026-08-06",\n',
        ptext,
        count=1,
    )
    dst_patch.write_text(ptext, encoding="utf-8")
    print("wrote", dst_patch.name)

    (ROOT / "verify-summary-0810.py").write_text(
        swap_dates((ROOT / "verify-summary-0809.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote verify-summary-0810.py")

    atext = swap_dates((ROOT / "_audit_0809_final.py").read_text(encoding="utf-8"))
    atext = atext.replace(
        'if "Sunday, August 9, 2026 — Worst" in html:',
        'if "Sunday, August 9, 2026 — Worst" in html:',
    )
    atext = atext.replace(
        'if "Sunday, August 10, 2026 — Worst" in html:',
        'if "Sunday, August 9, 2026 — Worst" in html:',
    )
    atext = atext.replace(
        'if "Saturday, August 10" in html or "Monday, August 10" in html:',
        'if "Sunday, August 10" in html or "Tuesday, August 10" in html:',
    )
    # swap may have broken weekday check — force Monday
    atext = atext.replace(
        'if "Sunday, August 10" in html or "Tuesday, August 10" in html:',
        'if "Sunday, August 10" in html or "Saturday, August 10" in html:',
    )
    atext = atext.replace(
        'fail("wrong weekday on August 10 (must be Sunday)")',
        'fail("wrong weekday on August 10 (must be Monday)")',
    )
    atext = atext.replace(
        'if "August 9, 2026 — current slate" in html:\n        fail("8/9 still labeled current")',
        'if "August 9, 2026 — current slate" in html:\n        fail("8/9 still labeled current")',
    )
    atext = atext.replace("!= 97", "!= PROPCOUNT")
    atext = atext.replace("expected 97 props", "expected PROPCOUNT props")
    atext = atext.replace(
        'expected_bum = {"Brad Lord", "Grayson Rodriguez", "Justin Wrobleski", "Sean Manaea"}',
        'expected_bum = {"Jameson Taillon", "Reid Detmers"}',
    )
    atext = atext.replace(
        """    for base in (
        "Jesus Luzardo",
        "Sean Manaea",
        "Joey Cantillo",
        "Matthew Boyd",
        "Connor Prielipp",
        "Cade Povich",
        "Ian Seymour",
        "Justin Wrobleski",
        "Eduardo Rodriguez",
    ):
        if not re.search(rf"{re.escape(base)}(?: 🧤)? \\(L", html):
            fail(f"LHP hand missing/wrong: {base} (L")""",
        """    for base in (
        "Trevor Rogers",
        "MacKenzie Gore",
        "Reid Detmers",
        "Jacob Lopez",
        "Noah Cameron",
        "Tarik Skubal",
    ):
        if not re.search(rf"{re.escape(base)}(?: 🧤)? \\(L", html):
            fail(f"LHP hand missing/wrong: {base} (L")""",
    )
    atext = atext.replace(
        'arch = ROOT / "preview" / "archive" / "2026-08-09.html"',
        'arch = ROOT / "preview" / "archive" / "2026-08-09.html"',
    )
    atext = atext.replace("8/8 archive missing", "8/9 archive missing")
    atext = atext.replace("8/8 archive wrong sheet-date", "8/9 archive wrong sheet-date")
    atext = atext.replace(
        'elif \'content="2026-08-09"\' not in arch.read_text(encoding="utf-8"):',
        'elif \'content="2026-08-09"\' not in arch.read_text(encoding="utf-8"):',
    )
    # games count: 10 today
    atext = atext.replace("!= 15", "!= 10")
    atext = atext.replace("expected 15 games", "expected 10 games")
    atext = atext.replace("expected 15 gameMeta", "expected 10 gameMeta")
    (ROOT / "_audit_0810_final.py").write_text(atext, encoding="utf-8")
    print("wrote _audit_0810_final.py")

    ztext = swap_dates((ROOT / "_backfill_zones_0809.py").read_text(encoding="utf-8"))
    ztext = ztext.replace(
        """LHP = {
    "Luzardo",
    "Manaea",
    "Cantillo",
    "Boyd",
    "Prielipp",
    "Povich",
    "Seymour",
    "Wrobleski",
    "Rodriguez",
}""",
        """LHP = {
    "Rogers",
    "Gore",
    "Detmers",
    "Lopez",
    "Cameron",
    "Skubal",
}""",
    )
    (ROOT / "_backfill_zones_0810.py").write_text(ztext, encoding="utf-8")
    print("wrote _backfill_zones_0810.py")

    (ROOT / "_best_0810.py").write_text(
        swap_dates((ROOT / "_best_0809.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote _best_0810.py")


if __name__ == "__main__":
    main()
