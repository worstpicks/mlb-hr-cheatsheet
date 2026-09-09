import re
from pathlib import Path

root = Path(__file__).parent
text = (root / "build-sheet-2026-05-18.py").read_text(encoding="utf-8")
prop_block = text.split("PROP_NAMES = [")[1].split("]")[0]
props = re.findall(r'"([^"]+)"', prop_block)

idx = (root / "preview/index.html").read_text(encoding="utf-8")
block = idx.split("const games =")[1].split("];")[0]
names = re.findall(r'name: "([^"]+)"', block)
bases = [n.split(" (")[0] for n in names]

from collections import Counter
c = Counter(bases)
dups = [k for k, v in c.items() if v > 1]
print("props", len(props), "rows", len(bases), "unique", len(set(bases)))
print("dups", dups)

USER = """Yandy Diaz Junior Caminero Pete Alonso Samuel Basallo Coby Mayo Kyle Schwarber Alec Bohm Adolis Garcia J.T. Realmuto Matt McLain JJ Bleday Elly De La Cruz Tyler Stephenson Will Benson Jakob Marsee Otto Lopez Xavier Edwards Austin Riley Matt Olson Mike Yastrzemski Dillon Dingler Rhys Hoskins Travis Bazzana James Wood Jose Tena Mark Vientos Juan Soto MJ Melendez Trent Grisham Paul Goldschmidt Amed Rosario Jazz Chisholm Jr. Kazuma Okamoto Ernie Clement George Springer Byron Buxton Tristan Gray Ryan Jeffers Yordan Alvarez Zach Dezenzo Brice Matthews Michael Massey Bobby Witt Jr. Jac Caglianone Salvador Perez Mickey Gasper Ceddanne Rafaela Wilyer Abreu Ian Happ Seiya Suzuki Michael Busch Michael Conforto Pete Crow-Armstrong Jake Bauers Andrew Vaughn Hunter Goodman Jordan Beck Kyle Karros Mickey Moniak Jake Burger Kyle Higashioka Jorge Soler Mike Trout Yoan Moncada Shea Langeliers Brent Rooker Zack Gelof Julio Rodriguez Randy Arozarena Rob Refsnyder Munetaka Murakami Miguel Vargas Colson Montgomery Andrew Benintendi Jarred Kelenic Gavin Sheets Jackson Merrill Manny Machado Andy Pages Mookie Betts Will Smith Shohei Ohtani Corbin Carroll Nolan Arenado Gabriel Moreno Casey Schmitt Harrison Bader Eric Haase Rafael Devers Luis Arraez Willy Adames""".split()

print("user count", len(USER))
not_user = sorted(set(props) - set(USER))
not_props = sorted(set(USER) - set(props))
print("in props not user", not_user)
print("in user not props", not_props)
