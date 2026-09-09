import re
import urllib.request

html = urllib.request.urlopen("https://www.worstpickz.win/", timeout=30).read().decode(
    "utf-8", "replace"
)
print("date", re.search(r'sheet-date" content="([^"]+)"', html).group(1))
print("hero", re.search(r"<p>((?:Monday|Sunday|Saturday), [^—]+)", html).group(1))
print("Abrams", "CJ Abrams" in html)
print("Pena", "Jeremy Pena" in html and "Over 1.5 homeruns" in html)
print("Nola", "Aaron Nola" in html)
print("props", re.search(r"(\d+) listed HR props", html).group(0))
print("favs", "7 Worst Pickz Favorite" in html)
print("NOT Sunday Aug 2 current", "Sunday, August 2, 2026 — Worst" not in html)
print("Park +26", "Park +26%" in html)
