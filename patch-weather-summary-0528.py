#!/usr/bin/env python3
"""Refresh May 28 summary weather/ballpark cards from patch-0528-preview constants."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Import constants from patch module
import importlib.util

spec = importlib.util.spec_from_file_location("p", ROOT / "patch-0528-preview.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

WEATHER_LIST = p.PARK_INNER.strip()
WEATHER5_LIST = p.WEATHER5_INNER.strip()
FADES_LIST = p.FADES_INNER.strip()


def patch_summary(text: str) -> str:
    text = re.sub(
        r'(<div class="summary-card">\s*<h3>Top 5 Weather Games</h3>\s*<div class="summary-list">)(.*?)(</div>\s*</div>\s*<div class="summary-card">\s*<h3>Top 5 Weather Heavy HR Plays</h3>)',
        r"\1\n" + WEATHER_LIST + r"\n                    \3",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'(<div class="summary-card">\s*<h3>Top 5 Weather Heavy HR Plays</h3>\s*<div class="summary-list">)(.*?)(</div>\s*</div>\s*<div class="summary-card">\s*<h3>Best longshot HR)',
        r"\1\n" + WEATHER5_LIST + r"\n                    \3",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'(<div class="summary-card">\s*<h3>Harsh Environment Fades</h3>\s*<div class="summary-list">)(.*?)(</div>\s*</div>\s*<div class="summary-card emoji-key-card">)',
        r"\1\n" + FADES_LIST + r"\n                    \3",
        text,
        count=1,
        flags=re.DOTALL,
    )
    return text


for rel in ("preview/index.html", "index.html"):
    path = ROOT / rel
    path.write_text(patch_summary(path.read_text(encoding="utf-8")), encoding="utf-8")
    print("patched summary weather in", rel)
