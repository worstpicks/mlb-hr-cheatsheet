#!/usr/bin/env python3
"""Put ↑ Top above ↓ Bottom in scroll-jump-fab."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = """                .scroll-jump-fab {
            display: flex;
            flex-direction: column-reverse;
            align-items: stretch;
            gap: 4px;
        }"""
NEW = OLD.replace("column-reverse", "column")

for rel in ("preview/index.html", "index.html"):
    p = ROOT / rel
    t = p.read_text(encoding="utf-8")
    if OLD not in t:
        print("skip (no match):", rel)
        continue
    p.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("patched", rel)
