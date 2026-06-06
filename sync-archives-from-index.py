#!/usr/bin/env python3
"""Rebuild archive sheets from preview/index.html, keeping each day's slate data."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "preview" / "index.html"
ARCHIVE_DIR = ROOT / "preview" / "archive"
MANIFEST_FB = (
    '<script type="application/json" id="sheets-manifest-fallback">'
    + json.dumps(
        json.loads((ROOT / "preview" / "sheets-manifest.json").read_text(encoding="utf-8")),
        ensure_ascii=False,
    ).replace("</", "<\\/")
    + "</script>"
)
MANIFEST = json.loads((ROOT / "preview" / "sheets-manifest.json").read_text(encoding="utf-8"))
CURRENT_DATE = MANIFEST["sheets"][0]["date"]

GAMES_PAT = re.compile(r"const games = \[.*?\];", re.DOTALL)
FAVS_PAT = re.compile(r"const WORST_PICKZ_FAVORITE_NAMES = new Set\(\[[\s\S]*?\]\);", re.DOTALL)
SUMMARY_SECTION_PAT = re.compile(
    r'<section class="summary-section">[\s\S]*?</section>',
    re.DOTALL,
)
HIT_SECTION_PAT = re.compile(
    r'<section class="batters-hit-section"[\s\S]*?</section>',
    re.DOTALL,
)
HEADER_P_PAT = re.compile(
    r"<p>(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), "
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December) "
    r"\d+, 2026 — Worst Pickz HR cheat sheet[\s\S]*?</p>",
    re.DOTALL,
)
def must_match(pat: re.Pattern[str], text: str, label: str, path: Path) -> str:
    m = pat.search(text)
    if not m:
        raise ValueError(f"{path.name}: missing {label}")
    return m.group(0)


def sync_archive(archive_path: Path, master: str) -> None:
    old = archive_path.read_text(encoding="utf-8")
    date = archive_path.stem

    games = must_match(GAMES_PAT, old, "games block", archive_path)
    favs = must_match(FAVS_PAT, old, "favorites set", archive_path)
    summary_section = must_match(SUMMARY_SECTION_PAT, old, "summary-section", archive_path)
    hit_section = HIT_SECTION_PAT.search(old)
    header_p = HEADER_P_PAT.search(old)

    text = master
    text = GAMES_PAT.sub(lambda _: games, text, count=1)
    text = FAVS_PAT.sub(lambda _: favs, text, count=1)
    if not SUMMARY_SECTION_PAT.search(text):
        raise ValueError(f"{archive_path.name}: master missing summary-section")
    text = SUMMARY_SECTION_PAT.sub(lambda _: summary_section, text, count=1)

    if header_p and HEADER_P_PAT.search(text):
        text = HEADER_P_PAT.sub(header_p.group(0), text, count=1)
    if hit_section and HIT_SECTION_PAT.search(text):
        text = HIT_SECTION_PAT.sub(hit_section.group(0), text, count=1)

    text = re.sub(
        r'<meta name="sheet-date" content="[^"]*">',
        f'<meta name="sheet-date" content="{date}">',
        text,
        count=1,
    )
    text = re.sub(
        r'<script type="application/json" id="sheets-manifest-fallback">.*?</script>',
        MANIFEST_FB,
        text,
        count=1,
        flags=re.DOTALL,
    )

    text = text.replace('src="assets/', 'src="../assets/')
    text = text.replace("src='assets/", "src='../assets/")

    archive_path.write_text(text, encoding="utf-8")
    print("synced", archive_path.relative_to(ROOT))


def main() -> None:
    if not MASTER.is_file():
        raise SystemExit(f"missing master: {MASTER}")
    master = MASTER.read_text(encoding="utf-8")
    current_meta = re.search(r'<meta name="sheet-date" content="([^"]+)">', master)
    if not current_meta or current_meta.group(1) != CURRENT_DATE:
        found = current_meta.group(1) if current_meta else "missing"
        raise SystemExit(
            f"refusing to sync archives from stale preview/index.html: "
            f"found {found}, manifest current is {CURRENT_DATE}"
        )
    archives = sorted(ARCHIVE_DIR.glob("2026-*.html"))
    if not archives:
        raise SystemExit("no archive HTML files found")
    for path in archives:
        sync_archive(path, master)
    root_index = ROOT / "index.html"
    if root_index.is_file():
        root_index.write_text(master, encoding="utf-8")
        print("updated", root_index.relative_to(ROOT))


if __name__ == "__main__":
    main()
