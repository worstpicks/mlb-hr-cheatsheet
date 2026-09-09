#!/usr/bin/env python3
"""Sync embedded sheets-manifest-fallback JSON across HTML files."""
import re
from pathlib import Path

MANIFEST_FB = (
    '<script type="application/json" id="sheets-manifest-fallback">'
    '{"version":1,"sheets":['
    '{"date":"2026-05-18","label":"May 18, 2026 \\u2014 current slate","href":"/index.html"},'
    '{"date":"2026-05-16","label":"May 16, 2026","href":"/archive/2026-05-16.html"},'
    '{"date":"2026-05-15","label":"May 15, 2026","href":"/archive/2026-05-15.html"},'
    '{"date":"2026-05-14","label":"May 14, 2026","href":"/archive/2026-05-14.html"}'
    "]}</script>"
)

ROOT = Path(__file__).resolve().parent
for path in [
    ROOT / "preview" / "index.html",
    ROOT / "index.html",
    ROOT / "preview" / "archive" / "2026-05-14.html",
    ROOT / "preview" / "archive" / "2026-05-15.html",
    ROOT / "preview" / "archive" / "2026-05-16.html",
]:
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8")
    new = re.sub(
        r'<script type="application/json" id="sheets-manifest-fallback">.*?</script>',
        lambda _m: MANIFEST_FB,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if new != text:
        path.write_text(new, encoding="utf-8")
        print("updated manifest fallback", path.name)
