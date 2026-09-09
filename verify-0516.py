import re
from pathlib import Path

t = Path("index.html").read_text(encoding="utf-8")
start = t.index("const games = [")
end = t.index("];", start) + 2
block = t[start:end]
names = re.findall(r'name: "([^"]+)"', block)
print("players:", len(names))
props = """Angel Martinez Daniel Schneemann Kyle Manzardo Sal Stewart Elly De La Cruz Spencer Steer Ryan Jeffers Andrew Vaughn Christian Walker Zach Cole Zach Dezenzo Evan Carter Joc Pederson Ezequiel Duran Colson Montgomery Munetaka Murakami Jarred Kelenic Miguel Vargas Ian Happ Alex Bregman Michael Conforto Luke Raley J.P. Crawford Miguel Andujar Jackson Merrill Mark Vientos Paul Goldschmidt Ben Rice Cody Bellinger Drake Baldwin Matt Olson Mickey Gasper Wilyer Abreu Jo Adell Oswald Peraza Will Smith Teoscar Hernandez Nick Kurtz Shea Langeliers Lawrence Butler Rafael Devers""".split()
found = {n.split(" (")[0] for n in names}
missing = [p for p in props if p not in found]
print("missing:", missing or "none")
