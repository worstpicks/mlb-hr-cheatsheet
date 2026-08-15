#!/usr/bin/env python3
"""Final pre-push verification for the 2026-08-15 sheet.

Kept as a file rather than an inline command: the gameMeta regex needs backslash
escapes that PowerShell here-strings mangle, which silently emptied the match list
and made the park/split loop pass without running.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-15"
GLOVE = "\U0001f9e4"
GAMECOUNT = 15
BUMCOUNT = 3

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
    chk(f"{GAMECOUNT} game titles", len(titles) == GAMECOUNT, str(len(titles)))
    chk(f"{GAMECOUNT} gameMeta strings", len(metas) == GAMECOUNT, str(len(metas)))
    if len(metas) != GAMECOUNT:
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
        clean = re.sub(r'<[^>]+>|"', "", m).replace("\\u00b7", "·")
        print(f"  {t.split(' - ')[0]:12} {clean[:150]}")

    print()
    print("=== ROOT / PREVIEW PARITY ===")
    root_metas = re.findall(r'gameMeta: "((?:[^"\\]|\\.)*)"', root)
    chk(f"root has {GAMECOUNT} gameMeta", len(root_metas) == GAMECOUNT, str(len(root_metas)))
    chk("root gameMeta identical to preview", root_metas == metas)
    chk("root prop count matches", root.count('{ name: "') == cur.count('{ name: "'))
    chk("root carries the 8/15 slate date", 'content="2026-08-15"' in root)

    print()
    print("=== BUM GLOVES ===")
    gloved = [t for t in titles if GLOVE in t]
    print(f"  gloved titles ({len(gloved)}):")
    for t in gloved:
        print(f"    {t}")
    chk(f"{BUMCOUNT} gloved titles", len(gloved) == BUMCOUNT)

    print()
    print("=== FEATURE PARITY vs 8/14 ===")

    def secs(h: str) -> set[str]:
        s = set()
        for m in re.finditer(r"<(h[1-4])[^>]*>(.*?)</\1>", h, re.S):
            t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(2))).strip()
            if t and len(t) < 70 and not re.search(r"August|\d{4}", t):
                s.add(t)
        return s

    prev = (ROOT / "preview" / "archive" / "2026-08-14.html").read_text(encoding="utf-8")
    missing = sorted(secs(prev) - secs(cur))
    chk("no sections lost vs 8/14", not missing, str(missing))
    for f in [
        "Homerun Form",
        "Damage Window",
        "Worst Pickz Straights of the Day",
        "Goblin's Insight",
        "Top 5 HR Tickets",
        "Weather Heavy",
        "Favorite 3 Leg",
        "Hits Parlay",
        "research/index.html",
        "Pikkit",
    ]:
        chk(f"feature present: {f}", f in cur)

    print()
    print("RESULT:", "ALL CHECKS PASSED" if not fails else f"{len(fails)} FAILURES: {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
