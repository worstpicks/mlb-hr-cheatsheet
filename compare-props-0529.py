USER = [
    "JJ Bleday", "Matt McLain", "Elly De La Cruz", "Michael Harris II", "Austin Riley",
    "Mike Yastrzemski", "Matt Olson", "Ronald Acuna Jr.", "Jacob Young", "James Wood",
    "Luis Garcia Jr.", "CJ Abrams", "Ramon Laureano", "Manny Machado", "Jackson Merrill",
    "Gavin Sheets", "Brandon Lowe", "Spencer Horwitz", "Marcell Ozuna", "Byron Buxton",
    "Ryan Kreidler", "Jackson Holliday", "Samuel Bassallo", "Gunnar Henderson", "Blaze Alexander",
    "Kazuma Okamoto", "George Springer", "Yandy Diaz", "Hunter Feduccia", "Jonathan Aranda",
    "Richie Palacios", "Zach Neto", "Jo Adell", "Mike Trout", "Juan Soto", "AJ Ewing",
    "Jared Young", "Owen Caissie", "Xavier Edwards", "Heriberto Hernandez", "Rhys Hoskins",
    "Bryan Rocchio", "Jose Ramirez", "Jarren Duran", "Ceddanne Rafaela", "Willson Contreras",
    "Jordan Walker", "Nolan Gorman", "JJ Wetherholt", "Ian Happ", "Michael Conforto",
    "Pete Crow-Armstrong", "Munetaka Murakami", "Miguel Vargas", "Colson Montgomery",
    "Gage Workman", "Riley Greene", "Spencer Torkelson", "Brandon Nimmo", "Joc Pederson",
    "Salvador Perez", "Bobby Witt Jr.", "Yordan Alvarez", "Isaac Paredes", "Christian Walker",
    "Garrett Mitchell", "Jake Bauers", "Jackson Chourio", "Christian Yelich", "Tj Rumfield",
    "Hunter Goodman", "Nick Kurtz", "Shea Langeliers", "Zack Gelof", "Colby Thomas",
    "Ben Rice", "Aaron Judge", "Ryan McMahon", "Luke Raley", "Patrick Wisdom", "Mitch Garver",
    "Dominic Canzone", "Colt Emerson", "Ketel Marte", "Corbin Carroll", "Nolan Arenado",
    "Gabriel Moreno", "Will Smith", "Freddie Freeman", "Shohei Ohtani", "Andy Pages",
    "Kyle Schwarber", "Bryce Harper", "Alec Bohm",
]

import re
from pathlib import Path
src = Path("generate-0529-sheet.py").read_text(encoding="utf-8")
mine = re.findall(r'\("([^"]+)", "[LRS]"', src)
print("user", len(USER), "mine", len(mine))
print("extra in mine", sorted(set(mine) - set(USER)))
print("missing from mine", sorted(set(USER) - set(mine)))
