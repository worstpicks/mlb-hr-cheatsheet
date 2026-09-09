#!/usr/bin/env python3
from pathlib import Path
import re

RAW = """Pete Crow Armstrong⭐
Seiya Suzuki⭐
Michael Busch
Bryce Eldrige⭐
Casey Schmitt
Edmundo Sosa
Bryce Harper
Kyle Schwarber
Colson Montgomery⭐
Miguel Vargas
Dillon Dingler⭐
Spencer Torkelson
Kerry Carpenter
Julio Rodriguez⭐
Rob Refsnyder
Ben Rice⭐
Wilyer Abreu
Willson Contreras
Jesus Sanchez
Kazuma Okamoto
Pete Alonso
Blaze Alexander
Jackson Holliday⭐
Adley Rutschman
Heriberto Hernandez⭐
Kyle Stowers⭐
Otto Lopez
Owen Caissie
Liam Hicks
Jonathan Aranda⭐
Cedric Mullins
Yandy Diaz
JUnior Caminero
Matt Olson
Michael Harris II
Ronald Acuna JR
Austin Riley
Bryan Reynolds⭐
Oneil Cruz
Yordan Alvarez⭐
Isaac Paredes
Shea Langeliers⭐
Tyler Soderstrom⭐
Nick Kurtz
Carlos Cortes
Joc Pederson
Justin Foscue
Jose Ramirez
Kyle Manzardo
Rhys Hoskins
Jordan Walker
JJ Wetherholt
JJ Bleday⭐
Will Benson
Sal Stewart
Byron Buxton
Trevor Larnach
Kody Clemens
Tristan Gray
Josh Bell
Salvador Perez
Vinnie Pasquantino⭐
Bobby Witt Jr⭐
Lane Thomas⭐
Willi Castro
Ezequiel Tovar
TJ Rumfield
Jake McCarthy
Jackson Chourio⭐
Jake Bauers
Garrett Mitchell
David Hamilton
Manny Machado
JAckson Merrill
Ty France
Jared Young⭐
Juan Soto
MJ Melendez
Ketel Marte
Corbin Carroll
Keibert Ruiz
James Wood
Cj Abrams
Curtis Mead
Will Smith⭐
Andy Pages
Shohei Ohtani
Mookie Betts
Zach Neto
Wade Meckler
Vaughn Grissom
Mike Trout⭐
Jo Adell""".strip().splitlines()

props_lines = ["RAW_PROPS = ["]
for p in RAW:
    props_lines.append(f'    "{p.strip()}",')
props_lines.append("]")
props_block = "\n".join(props_lines)

ALIASES = """ALIASES = {
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Bryce Eldrige": "Bryce Eldridge",
    "Jesus Sanchez": "Jesús Sánchez",
    "JUnior Caminero": "Junior Caminero",
    "Ronald Acuna JR": "Ronald Acuña Jr.",
    "Jose Ramirez": "José Ramírez",
    "Bobby Witt Jr": "Bobby Witt Jr.",
    "JAckson Merrill": "Jackson Merrill",
    "Cj Abrams": "CJ Abrams",
    "Julio Rodriguez": "Julio Rodríguez",
}"""

path = Path("build-0605-from-csv.py")
text = path.read_text(encoding="utf-8")
text = text.replace("2026-06-04", "2026-06-05")
text = text.replace("build-0604", "build-0605")
text = re.sub(r"RAW_PROPS = \[.*?\]", props_block, text, count=1, flags=re.S)
text = re.sub(r"ALIASES = \{.*?\}", ALIASES, text, count=1, flags=re.S)
path.write_text(text, encoding="utf-8")
print("patched build-0605-from-csv.py")
