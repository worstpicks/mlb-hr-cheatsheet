#!/usr/bin/env python3
"""Repair archive pages whose asset paths were copied verbatim from preview/index.html.

Archives live in preview/archive/, one level below preview/, so a bare "assets/..."
reference resolves to preview/archive/assets/ and 404s. Rewrite them to "../assets/".
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARCHIVE_DIR = ROOT / "preview" / "archive"


def fix(text: str) -> str:
    for attr in ("src", "href"):
        for quote in ('"', "'"):
            text = text.replace(f"{attr}={quote}assets/", f"{attr}={quote}../assets/")
    return text


def main() -> int:
    fixed = 0
    for path in sorted(ARCHIVE_DIR.glob("20??-??-??.html")):
        old = path.read_text(encoding="utf-8")
        new = fix(old)
        if new != old:
            path.write_text(new, encoding="utf-8")
            fixed += 1
            print("fixed", path.name)
    print(f"\n{fixed} archive(s) repaired")

    broken = []
    for path in sorted(ARCHIVE_DIR.glob("20??-??-??.html")):
        text = path.read_text(encoding="utf-8")
        for attr in ("src", "href"):
            if f'{attr}="assets/' in text:
                broken.append(path.name)
                break
    print("still broken:", broken or "none")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
