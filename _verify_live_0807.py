import re
import urllib.request

url = "https://www.worstpickz.win/"
html = urllib.request.urlopen(url, timeout=45).read().decode("utf-8", "replace")
meta = re.search(r'name="sheet-date" content="([^"]+)"', html)
hero = re.search(r"(Wednesday|Tuesday|Thursday|Friday), August \d+, 2026", html)
print("url", url)
print("sheet-date", meta.group(1) if meta else None)
print("hero", hero.group(0) if hero else None)
for s in ["Willson Contreras", "Alec Burleson", "Owen Caissie", "Ronel Blanco", "Jack Perkins"]:
    print(("OK" if s in html else "MISS"), s)
print("stale Hill straight", "Derek Hill &mdash; vs Mikolas" in html)
print("67 props", "67 listed" in html)
assert meta and meta.group(1) == "2026-08-07"
assert hero and hero.group(0) == "Friday, August 7, 2026"
assert "Willson Contreras" in html and "Alec Burleson" in html
print("LIVE OK")
