#!/usr/bin/env python3
"""Print the Goblin / straight Gambly leg lists as they sit in the built sheet."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LABELS = ("Favorite 3 Leg", "3 Leg HR", "2 Leg HR", "Hits Parlay", "Straights of the Day")


def main() -> int:
    h = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
    ms = list(re.finditer(r"data-goblin-gambly-lines='([^']+)'", h))
    print(f"gambly buttons: {len(ms)}")
    for m in ms:
        try:
            lines = json.loads(html.unescape(m.group(1)))
        except json.JSONDecodeError as exc:
            print(f"  UNPARSEABLE: {exc}")
            continue
        ctx = h[max(0, m.start() - 2000) : m.start()]
        label = ""
        best = -1
        for cand in LABELS:
            pos = ctx.rfind(cand)
            if pos > best:
                best, label = pos, cand
        print(f"  {label:22} {len(lines)} legs")
        for l in lines:
            print(f"      {l}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
