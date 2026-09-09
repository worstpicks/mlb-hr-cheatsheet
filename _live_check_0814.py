#!/usr/bin/env python3
"""Post-push verification of both live hosts for the 2026-08-14 sheet."""

from __future__ import annotations

import random
import re
import sys
import urllib.request

GLOVE = "\U0001f9e4"
HOSTS = {
    "Netlify (primary)  www.worstpickz.win": "https://www.worstpickz.win/index.html",
    "GitHub Pages mirror": "https://worstpicks.github.io/mlb-hr-cheatsheet/index.html",
}
RESEARCH = "https://www.worstpickz.win/research/index.html"


def fetch(url: str) -> str:
    req = urllib.request.Request(
        f"{url}?cb={random.randint(1, 10**9)}",
        headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache", "Pragma": "no-cache"},
    )
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")


def main() -> int:
    ok = True
    for label, url in HOSTS.items():
        print(label)
        try:
            h = fetch(url)
        except Exception as exc:
            print(f"   ERROR {exc}\n")
            ok = False
            continue

        date = re.search(r'content="(2026-\d\d-\d\d)"', h)
        date = date.group(1) if date else "?"
        hero = re.search(r"((?:Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day, August \d+, 2026)", h)
        hero = hero.group(1) if hero else "?"
        titles = re.findall(r'title: "([^"]+)"', h)
        props = len(re.findall(r'\{ name: "', h))
        gloved = [t for t in titles if GLOVE in t]
        metas = re.findall(r'gameMeta: "((?:[^"\\]|\\.)*)"', h)
        full_meta = sum(1 for m in metas if "Park " in m and m.count("pitcher-meta") == 2)

        good = (
            date == "2026-08-14"
            and hero == "Friday, August 14, 2026"
            and len(titles) == 13
            and props == 85
            and len(gloved) == 3
            and full_meta == 13
        )
        ok = ok and good
        print(f"   {'OK  ' if good else 'STALE/FAIL'}  sheet-date={date}  hero={hero}")
        print(f"   games={len(titles)}  props={props}  gloved={len(gloved)}  complete_headers={full_meta}/13")
        for t in gloved:
            print(f"     glove: {t}")
        print()

    print("Research tab")
    try:
        r = fetch(RESEARCH)
        ver = re.search(r"research\.js\?v=(\d+)", r)
        print(f"   OK    loads, research.js v={ver.group(1) if ver else '?'}")
    except Exception as exc:
        print(f"   ERROR {exc}")
        ok = False

    print()
    print("RESULT:", "BOTH HOSTS LIVE WITH 8/14" if ok else "at least one host not current")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
