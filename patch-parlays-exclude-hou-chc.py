#!/usr/bin/env python3
"""Update Goblin parlays only — exclude HOU @ CHC (first game final)."""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"

spec = importlib.util.spec_from_file_location("patch0522", ROOT / "patch-0522-preview.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

text = PREVIEW.read_text(encoding="utf-8")
pat = (
    r'                <div class="summary-card full-width best-bets-card">[\s\S]*?\n'
    r'                </div>\n                <div class="summary-card full-width top-five-card">'
)
new_text, count = re.subn(pat, mod.GOBLIN_CARD + '\n                <div class="summary-card full-width top-five-card">', text, count=1)
if count != 1:
    sys.exit("Could not replace Goblin card")
PREVIEW.write_text(new_text, encoding="utf-8")
print("updated Goblin parlays (HOU @ CHC excluded)")
