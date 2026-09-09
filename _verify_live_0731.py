#!/usr/bin/env python3
import re
import urllib.request

urls = [
    "https://www.worstpickz.win/",
    "https://worstpickz.win/",
    "https://worstpicks.github.io/mlb-hr-cheatsheet/",
]
for url in urls:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")
        meta = re.search(r'content="(2026-07-\d+)"', html)
        print(url)
        print(
            "  meta",
            meta.group(1) if meta else None,
            "friday",
            "Friday, July 31, 2026" in html,
            "wood",
            "James Wood" in html,
            "castro",
            "Willi Castro" in html,
            "clemens fav3",
            "Kody Clemens" in html,
            "props",
            re.search(r"\d+ listed HR props", html).group(0)
            if re.search(r"\d+ listed HR props", html)
            else None,
        )
    except Exception as e:
        print(url, "ERR", e)
