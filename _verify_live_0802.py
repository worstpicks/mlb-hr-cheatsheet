import re
import urllib.request

html = urllib.request.urlopen("https://www.worstpickz.win/", timeout=30).read().decode(
    "utf-8", "replace"
)
print("date", re.search(r'sheet-date" content="([^"]+)"', html).group(1))
print("hero", re.search(r"<p>((?:Sunday|Saturday|Friday), [^—]+)", html).group(1))
print("Crooks", "Jimmy Crooks" in html)
print("Castro O1.5", "Willi Castro" in html and "Over 1.5 homeruns" in html)
print("Scherzer", "Max Scherzer" in html)
print("props", re.search(r"(\d+) listed HR props", html).group(0))
print("favs", "25 Worst Pickz Favorite" in html)
print("NOT Saturday Aug 1 current", "Saturday, August 1, 2026 — Worst" not in html)
