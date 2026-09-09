#!/usr/bin/env python3
from patch_targets import SHEET_HTML

for p in SHEET_HTML:
    if not p.is_file():
        continue
    t = p.read_text(encoding="utf-8")
    if 'height="24""' in t:
        t = t.replace('height="24""', 'height="24"')
        p.write_text(t, encoding="utf-8")
        print("fixed", p)
    else:
        print("ok", p)
