import re
import urllib.request

url = "https://www.worstpickz.win/"
html = urllib.request.urlopen(url, timeout=45).read().decode("utf-8", "replace")
meta = re.search(r'name="sheet-date" content="([^"]+)"', html)
hero = re.search(r"(Wednesday|Tuesday), August \d+, 2026", html)
print("url", url)
print("sheet-date", meta.group(1) if meta else None)
print("hero", hero.group(0) if hero else None)
for s in ["Daylen Lile", "Coby Mayo", "Taylor Trammell", "Andrew Painter", "Jameson Taillon"]:
    print(("OK" if s in html else "MISS"), s)
print("stale Littell", "Zack Littell" in html)
print("102 props", "102 listed" in html)
assert meta and meta.group(1) == "2026-08-05"
assert hero and "August 5" in hero.group(0) and "Wednesday" in hero.group(0)
assert "Daylen Lile" in html and "Coby Mayo" in html
print("LIVE OK")
