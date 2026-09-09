#!/usr/bin/env python3
from patch_targets import SHEET_HTML

for p in SHEET_HTML:
    t = p.read_text(encoding="utf-8")
    o = t
    t = t.replace("                .pikkit-link {", "        .pikkit-link {")
    t = t.replace('                                <a class="pikkit-link"', '                <a class="pikkit-link"')
    if t != o:
        p.write_text(t, encoding="utf-8")
        print("fixed", p.name)
