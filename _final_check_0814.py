#!/usr/bin/env python3
"""Final pre-push verification for the 2026-08-14 sheet.

Kept as a file rather than an inline command: the gameMeta regex needs backslash
escapes that PowerShell here-strings mangle, which silently emptied the match list
and made the park/split loop pass without running.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-14"
GLOVE = "\U0001f9e4"

fails: list[str] = []


def chk(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'OK  ' if ok else 'FAIL'}  {label}{'  ' + detail if detail else ''}")
    if not ok:
        fails.append(label)


def main() -> int:
    cur = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
    root = (ROOT / "index.html").read_text(encoding="utf-8")

    titles = re.findall(r'title: "([^"]+)"', cur)
    metas = re.findall(r'gameMeta: "((?:[^"\\]|\\.)*)"', cur)

    print("=== GAME HEADERS: park % + both pitcher splits ===")
    chk("13 game titles", len(titles) == 13, str(len(titles)))
    chk("13 gameMeta strings", len(metas) == 13, str(len(metas)))
    if len(metas) != 13:
        print("  cannot verify headers without gameMeta matches")
        return 1

    for t, m in zip(titles, metas):
        short = t.split(" - ")[0]
        park = "Park " in m
        hands = "LHB" in m and "RHB" in m
        segs = m.count("pitcher-meta")
        chk(f"{short:12} park={park} hands={hands} SPsplits={segs}", park and hands and segs == 2)

    print()
    print("=== per-game header text ===")
    for t, m in zip(titles, metas):
        clean = re.sub(r'<[^>]+>|\\"', "", m).replace("\\u00b7", "·")
        print(f"  {t.split(' - ')[0]:12} {clean[:150]}")

    print()
    print("=== ROOT / PREVIEW PARITY ===")
    root_metas = re.findall(r'gameMeta: "((?:[^"\\]|\\.)*)"', root)
    chk("root has 13 gameMeta", len(root_metas) == 13, str(len(root_metas)))
    chk("root gameMeta identical to preview", root_metas == metas)
    chk("root prop count matches", root.count('{ name: "') == cur.count('{ name: "'))

    print()
    print("=== BUM GLOVES ===")
    gloved = [t for t in titles if GLOVE in t]
    print(f"  gloved titles ({len(gloved)}):")
    for t in gloved:
        print(f"    {t}")
    chk("3 gloved titles", len(gloved) == 3)

    print()
    print("RESULT:", "ALL CHECKS PASSED" if not fails else f"{len(fails)} FAILURES: {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
