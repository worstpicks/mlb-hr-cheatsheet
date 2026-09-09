#!/usr/bin/env python3
import re
import urllib.request

html = urllib.request.urlopen("https://www.worstpickz.win/", timeout=30).read().decode(
    "utf-8", "replace"
)
print("sheet-date", re.search(r'content="(2026-08-\d+)"', html).group(1))
print(
    "hero",
    re.search(
        r"<p>((?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday), [^<]+)",
        html,
    ).group(1)[:100],
)
print("straights", re.findall(r'class="straight-pick-name">([^<]+)', html))
print("props", re.search(r"(\d+) listed HR props", html).group(0))
print("stale Aug3 current?", "August 3, 2026 — current slate" in html)
print("Tuesday Aug4?", "Tuesday, August 4, 2026" in html)
