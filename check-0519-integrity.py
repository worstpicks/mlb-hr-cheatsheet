#!/usr/bin/env python3
"""Local integrity checks for the 2026-05-19 current sheet."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_DATE = "2026-05-19"
EXPECTED_GAMES = 15
EXPECTED_ROWS = 89
EXPECTED_FAVS = 14


def fail(msg):
    print(f"FAIL {msg}")
    return False


def ok(msg):
    print(f"OK   {msg}")
    return True


def check_html(path: Path):
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT)
    game_count = text.count('title: "')
    row_count = text.count('{ name: "')
    checks = []
    checks.append(ok(f"{rel} date {EXPECTED_DATE}") if f'sheet-date" content="{EXPECTED_DATE}' in text else fail(f"{rel} wrong sheet date"))
    checks.append(ok(f"{rel} game count {EXPECTED_GAMES}") if game_count == EXPECTED_GAMES else fail(f"{rel} wrong game count: {game_count}"))
    checks.append(ok(f"{rel} row count {EXPECTED_ROWS}") if row_count == EXPECTED_ROWS else fail(f"{rel} wrong row count: {row_count}"))
    checks.append(ok(f"{rel} Pikkit wordmark") if "pikkit-link__wordmark" in text else fail(f"{rel} missing Pikkit wordmark"))
    checks.append(ok(f"{rel} Top over Bottom buttons") if text.find('id="scrollToTop"') < text.find('id="scrollToBottom"') else fail(f"{rel} scroll buttons not Top over Bottom"))
    fav_match = re.search(r"const WORST_PICKZ_FAVORITE_NAMES = new Set\(\[([\s\S]*?)\]\);", text)
    if fav_match:
        favs = re.findall(r'"([^"]+)"', fav_match.group(1))
        checks.append(ok(f"{rel} favorite count {EXPECTED_FAVS}") if len(favs) == EXPECTED_FAVS else fail(f"{rel} favorite count {len(favs)}"))
    else:
        checks.append(fail(f"{rel} missing favorite set"))
    return all(checks)


def main():
    manifest = json.loads((ROOT / "preview" / "sheets-manifest.json").read_text(encoding="utf-8"))
    checks = []
    checks.append(ok("manifest current 2026-05-19") if manifest["sheets"][0]["date"] == EXPECTED_DATE else fail("manifest current is not 2026-05-19"))
    checks.append(ok("5/18 archive exists") if (ROOT / "preview" / "archive" / "2026-05-18.html").exists() else fail("missing 5/18 archive"))
    checks.append(check_html(ROOT / "index.html"))
    checks.append(check_html(ROOT / "preview" / "index.html"))
    root_games = re.search(r"const games = \[([\s\S]*?)\];", (ROOT / "index.html").read_text(encoding="utf-8"))
    preview_games = re.search(r"const games = \[([\s\S]*?)\];", (ROOT / "preview" / "index.html").read_text(encoding="utf-8"))
    checks.append(ok("root/preview games blocks match") if root_games and preview_games and root_games.group(0) == preview_games.group(0) else fail("root/preview games blocks differ"))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
