#!/usr/bin/env python3
"""Restore June 1/4/5 archive HTML from git snapshots + current UX shell."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
ARCHIVE_DIR = ROOT / "preview" / "archive"
MANIFEST_PATH = ROOT / "preview" / "sheets-manifest.json"

# Final published commit per archive date (preview/index.html at that commit).
ARCHIVE_SOURCES: dict[str, tuple[str, str]] = {
    "2026-05-31": ("c14e2d7", "Sunday, May 31, 2026"),
    "2026-06-01": ("860177c", "Monday, June 1, 2026"),
    "2026-06-04": ("c66b947", "Thursday, June 4, 2026"),
    "2026-06-05": ("0a96b0b", "Friday, June 5, 2026"),
}

GAMES_PAT = re.compile(r"const games = \[.*?\];", re.DOTALL)
FAVS_PAT = re.compile(r"const WORST_PICKZ_FAVORITE_NAMES = new Set\(\[[\s\S]*?\]\);", re.DOTALL)
SUMMARY_SECTION_PAT = re.compile(r'<section class="summary-section">[\s\S]*?</section>', re.DOTALL)
HIT_SECTION_PAT = re.compile(r'<section class="batters-hit-section"[\s\S]*?</section>', re.DOTALL)
HEADER_P_PAT = re.compile(
    r"<p>(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), "
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December) "
    r"\d+, 2026 — Worst Pickz HR cheat sheet[\s\S]*?</p>",
    re.DOTALL,
)


def git_show(commit: str, path: str = "preview/index.html") -> str:
    r = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return r.stdout


def must_match(pat: re.Pattern[str], text: str, label: str) -> str:
    m = pat.search(text)
    if not m:
        raise ValueError(f"missing {label}")
    return m.group(0)


def build_manifest() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    old = {sheet["date"]: sheet for sheet in manifest.get("sheets", [])}
    ordered = [
        {"date": "2026-06-06", "label": "June 6, 2026 — current slate", "href": "index.html"},
        {"date": "2026-06-05", "label": "June 5, 2026", "href": "archive/2026-06-05.html"},
        {"date": "2026-06-04", "label": "June 4, 2026", "href": "archive/2026-06-04.html"},
        {"date": "2026-06-01", "label": "June 1, 2026", "href": "archive/2026-06-01.html"},
        {"date": "2026-05-31", "label": "May 31, 2026", "href": "archive/2026-05-31.html"},
        {"date": "2026-05-30", "label": "May 30, 2026", "href": "archive/2026-05-30.html"},
        {"date": "2026-05-29", "label": "May 29, 2026", "href": "archive/2026-05-29.html"},
        {"date": "2026-05-28", "label": "May 28, 2026", "href": "archive/2026-05-28.html"},
        {"date": "2026-05-27", "label": "May 27, 2026", "href": "archive/2026-05-27.html"},
        {"date": "2026-05-25", "label": "May 25, 2026", "href": "archive/2026-05-25.html"},
        {"date": "2026-05-21", "label": "May 21, 2026", "href": "archive/2026-05-21.html"},
    ]
    for date in ["2026-05-20", "2026-05-19", "2026-05-18", "2026-05-16", "2026-05-15", "2026-05-14"]:
        if date in old:
            ordered.append(old[date])
    payload = {"version": 1, "sheets": ordered}
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def manifest_fallback(manifest: dict) -> str:
    return (
        '<script type="application/json" id="sheets-manifest-fallback">'
        + json.dumps(manifest, ensure_ascii=False).replace("</", "<\\/")
        + "</script>"
    )


def build_archive(date: str, commit: str, header_prefix: str, master: str, manifest: dict) -> str:
    snap = git_show(commit)
    games = must_match(GAMES_PAT, snap, "games")
    favs = must_match(FAVS_PAT, snap, "favorites")
    summary = must_match(SUMMARY_SECTION_PAT, snap, "summary-section")
    hit = HIT_SECTION_PAT.search(snap)
    header_m = HEADER_P_PAT.search(snap)
    if not header_m:
        raise ValueError(f"{date}: missing header paragraph in {commit}")

    text = master
    text = GAMES_PAT.sub(lambda _: games, text, count=1)
    text = FAVS_PAT.sub(lambda _: favs, text, count=1)
    text = SUMMARY_SECTION_PAT.sub(lambda _: summary, text, count=1)
    if hit and HIT_SECTION_PAT.search(text):
        text = HIT_SECTION_PAT.sub(hit.group(0), text, count=1)

    # Correct weekday/date in intro copy.
    header = header_m.group(0)
    header = re.sub(
        r"<p>(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), "
        r"(?:January|February|March|April|May|June|July|August|September|October|November|December) "
        r"\d+, 2026 — Worst Pickz HR cheat sheet",
        f"<p>{header_prefix} — Worst Pickz HR cheat sheet",
        header,
        count=1,
    )
    if HEADER_P_PAT.search(text):
        text = HEADER_P_PAT.sub(header, text, count=1)

    text = re.sub(
        r'<meta name="sheet-date" content="[^"]*">',
        f'<meta name="sheet-date" content="{date}">',
        text,
        count=1,
    )
    text = re.sub(
        r'<script type="application/json" id="sheets-manifest-fallback">.*?</script>',
        manifest_fallback(manifest),
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = text.replace('src="assets/', 'src="../assets/')
    text = text.replace("src='assets/", "src='../assets/")
    return text


def patch_live_manifest(manifest: dict) -> None:
    fb = manifest_fallback(manifest)
    for path in (PREVIEW, ROOT / "index.html"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r'<script type="application/json" id="sheets-manifest-fallback">.*?</script>',
            fb,
            text,
            count=1,
            flags=re.DOTALL,
        )
        path.write_text(text, encoding="utf-8")
        print("updated manifest fallback in", path.relative_to(ROOT))


def main() -> None:
    if not PREVIEW.is_file():
        raise SystemExit(f"missing {PREVIEW}")
    master = PREVIEW.read_text(encoding="utf-8")
    meta = re.search(r'<meta name="sheet-date" content="([^"]+)">', master)
    if not meta or meta.group(1) != "2026-06-06":
        raise SystemExit(f"refusing: preview/index.html sheet-date is {meta.group(1) if meta else 'missing'}")

    manifest = build_manifest()
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    for date, (commit, header) in ARCHIVE_SOURCES.items():
        out = ARCHIVE_DIR / f"{date}.html"
        text = build_archive(date, commit, header, master, manifest)
        out.write_text(text, encoding="utf-8")
        print("restored", out.relative_to(ROOT), f"from {commit}")

    patch_live_manifest(manifest)
    print("OK restore-june-archives")


if __name__ == "__main__":
    main()
