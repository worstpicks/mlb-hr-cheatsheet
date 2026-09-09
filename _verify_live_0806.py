import re
import urllib.request

url = "https://www.worstpickz.win/"
html = urllib.request.urlopen(url, timeout=45).read().decode("utf-8", "replace")
meta = re.search(r'name="sheet-date" content="([^"]+)"', html)
hero = re.search(r"(Wednesday|Tuesday|Thursday), August \d+, 2026", html)
print("url", url)
print("sheet-date", meta.group(1) if meta else None)
print("hero", hero.group(0) if hero else None)
for s in ["Derek Hill", "Wilyer Abreu", "Gunnar Henderson", "J.T. Realmuto", "Miles Mikolas"]:
    print(("OK" if s in html else "MISS"), s)
print("stale Lile", "Daylen Lile — vs Painter" in html or "Daylen Lile &mdash; vs Painter" in html)
print("69 props", "69 listed" in html)
assert meta and meta.group(1) == "2026-08-06"
assert hero and hero.group(0) == "Thursday, August 6, 2026"
assert "Derek Hill" in html and "Wilyer Abreu" in html
print("LIVE OK")
