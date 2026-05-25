#!/usr/bin/env python3
"""Convert audited 5/25 standalone sheet games[] to preview-site format."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = Path(r"C:\Users\allmi\mlb_hr_cheatsheet_5_25.html")
OUT = ROOT / "_games-0525.txt"

import importlib.util

spec = importlib.util.spec_from_file_location("bs525", ROOT / "build-sheet-2026-05-25.py")
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)
FAVS = bs.FAVS

BUMS = {
    "Bradish", "Liberatore", "Kay", "Wacha", "Lodolo", "Kelly", "Littell",
    "Vasquez", "Imai", "Junk", "Gordon", "Sheehan", "Civale",
}

ESCAPE_MAP = {
    r"\ud83d\ude80": "🚀",
    r"\ud83d\udc8e": "💎",
    r"\u26be": "⚾",
    r"\ud83d\udd4a\ufe0f": "🕊️",
    r"\ud83c\udf15": "🌕",
    r"\ud83c\udfdf\ufe0f": "🏟️",
    r"\ud83d\udcdc": "📜",
    r"\ud83e\udde4": "🧤",
}


def decode_js_string(s: str) -> str:
    out = s
    for esc, ch in ESCAPE_MAP.items():
        out = out.replace(esc, ch)
    out = re.sub(
        r"\\u([0-9a-fA-F]{4})",
        lambda m: chr(int(m.group(1), 16)),
        out,
    )
    return out


def decode_emojis(s: str) -> str:
    return decode_js_string(s)


def pitcher_from_chip(chips_raw: str) -> str:
    m = re.search(r'"vs ([^"]+)"', chips_raw)
    return m.group(1).strip() if m else ""


def last_name(full: str) -> str:
    parts = full.replace(".", "").split()
    if len(parts) >= 2 and parts[-1].lower() == "jr":
        return f"{parts[-2]} {parts[-1]}"
    return parts[-1] if parts else full


def bum_match(chip_pitcher: str, title: str) -> bool:
    cp = chip_pitcher.lower()
    for bum in BUMS:
        if bum.lower() in cp or cp in bum.lower():
            return True
    for bum in BUMS:
        if bum.lower() in title.lower() and f"vs {chip_pitcher}".lower() in title.lower():
            pass
    title_bums = re.findall(r"([\w\s.'-]+?)\s*🧤\s*\(", title)
    for tb in title_bums:
        if last_name(tb.strip()).lower() == cp.lower() or cp.lower() in tb.lower():
            return True
        if cp.lower() in last_name(tb.strip()).lower():
            return True
    for bum in BUMS:
        if bum.lower() == cp.lower():
            return True
    return False


def normalize_note(name: str, note: str, pitcher: str) -> str:
    note = note.strip()
    if "Draws opposing starter" not in note:
        note = f"{note} Draws opposing starter {pitcher}."
    if name in FAVS and "Worst Pickz favorite" not in note:
        lower = note.lower()
        if lower.startswith("favorite with "):
            note = "Worst Pickz favorite with " + note[len("Favorite with ") :]
        elif lower.startswith("favorite "):
            note = "Worst Pickz favorite " + note[len("Favorite ") :]
        else:
            note = f"Worst Pickz favorite with {note[0].lower()}{note[1:]}" if note else "Worst Pickz favorite."
    return note


def enrich_row(name, odds, score, emojis, note, chips, blast, title):
    emojis = decode_emojis(emojis)
    pitcher = pitcher_from_chip(chips)
    if bum_match(pitcher, title) and "🧤" not in emojis:
        emojis = (emojis + " 🧤").strip()
    if name in FAVS and "⭐" not in emojis:
        emojis = (emojis + " ⭐").strip()
    note = normalize_note(name, note, pitcher)
    note_js = note.replace("\\", "\\\\").replace('"', '\\"')
    parts = [
        f'name: "{name}"',
        f'odds: "{odds}"',
        f"score: {score}",
        f'emojis: "{emojis}"',
    ]
    if blast:
        parts.append(f'blast: "{blast}"')
    parts.append(f'note: "{note_js}"')
    parts.append(f"chips: {chips}")
    return "{ " + ", ".join(parts) + " }"


def extract_row_objects(rows_blob: str) -> list[str]:
    rows = []
    i = 0
    while i < len(rows_blob):
        start = rows_blob.find("{ name:", i)
        if start == -1:
            break
        depth = 0
        j = start
        while j < len(rows_blob):
            ch = rows_blob[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    rows.append(rows_blob[start : j + 1])
                    i = j + 1
                    break
            j += 1
        else:
            break
    return rows


ROW_RE = re.compile(
    r'\{ name: "([^"]+)", odds: "([^"]+)", score: (\d+), emojis: "([^"]*)"(?:, blast: "([^"]*)")?, note: "((?:[^"\\]|\\.)*)", chips: (\[[^\]]+\]) \}',
    re.S,
)


def extract_game_objects(block: str) -> list[str]:
    inner = block[len("const games = [") : -2]
    games = []
    i = 0
    while i < len(inner):
        start = inner.find("{ title:", i)
        if start == -1:
            break
        depth = 0
        j = start
        while j < len(inner):
            ch = inner[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    games.append(inner[start : j + 1])
                    i = j + 1
                    break
            j += 1
        else:
            break
    return games


GAME_RE = re.compile(
    r'\{ title: "([^"]+)", description: "((?:[^"\\]|\\.)*)", rows: \[(.*)\]\s*\}',
    re.S,
)


def convert_games_block(block: str) -> str:
    games = []
    for game_text in extract_game_objects(block):
        gm = GAME_RE.search(game_text)
        if not gm:
            raise ValueError(f"Could not parse game: {game_text[:120]}...")
        title = decode_emojis(gm.group(1))
        title = re.sub(r"\s*🏟️\s*", " ", title).strip()
        title = title.replace("  ", " ")
        desc = decode_js_string(gm.group(2))
        rows_blob = gm.group(3)
        row_items = []
        for row_text in extract_row_objects(rows_blob):
            row = ROW_RE.search(row_text)
            if not row:
                raise ValueError(f"Could not parse row: {row_text[:120]}...")
            note = decode_js_string(row.group(6))
            row_items.append(
                enrich_row(
                    row.group(1),
                    row.group(2),
                    int(row.group(3)),
                    row.group(4),
                    note,
                    row.group(7),
                    row.group(5),
                    title,
                )
            )
        desc_js = desc.replace("\\", "\\\\").replace('"', '\\"')
        games.append(
            "    {\n"
            f'        title: "{title}",\n'
            f'        description: "{desc_js}",\n'
            f"        rows: [\n            "
            + ",\n            ".join(row_items)
            + ",\n        ],\n    }"
        )
    return "const games = [\n" + ",\n".join(games) + "\n];"


def main():
    html = SRC.read_text(encoding="utf-8")
    start = html.index("const games = [")
    end = html.index("];", start) + 2
    block = html[start:end]
    out = convert_games_block(block)
    OUT.write_text(out + "\n", encoding="utf-8")
    names = re.findall(r'name: "([^"]+)"', out)
    print(f"wrote {OUT.name}: {len(names)} rows, {out.count('title:')} games")


if __name__ == "__main__":
    main()
