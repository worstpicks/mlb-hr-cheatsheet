#!/usr/bin/env python3
import re
import urllib.request

url = "https://www.worstpickz.win/"
html = urllib.request.urlopen(
    urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=45
).read().decode("utf-8", "replace")
picks = re.findall(r'class="straight-pick-name">([^<]+)', html)
gambly = re.findall(r"data-goblin-gambly-lines='([^']+)'", html)
print("straights:", picks)
print("o05 gambly:", gambly[0].replace("&quot;", '"') if gambly else None)
print("fav3 gambly:", gambly[5].replace("&quot;", '"') if len(gambly) > 5 else None)
