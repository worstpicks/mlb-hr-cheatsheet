#!/usr/bin/env python3
import re
import urllib.request

urls = [
    "https://www.worstpickz.win/",
    "https://worstpickz.win/",
    "https://worstpicks.github.io/mlb-hr-cheatsheet/",
]
for url in urls:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")
    meta = re.search(r'content="(2026-0[78]-\d+)"', html)
    picks = re.findall(r'class="straight-pick-name">([^<]+)', html)
    print(url)
    print(
        "  meta",
        meta.group(1) if meta else None,
        "saturday",
        "Saturday, August 1, 2026" in html,
        "friday_wrong",
        "Friday, August 1" in html or "Friday, July 31, 2026 — Worst" in html,
        "props",
        re.search(r"\d+ listed HR props", html).group(0)
        if re.search(r"\d+ listed HR props", html)
        else None,
    )
    print("  straights:", picks)
