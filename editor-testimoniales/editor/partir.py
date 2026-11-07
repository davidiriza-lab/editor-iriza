"""Parte en dos los subtítulos que no caben sin tapar la cara (layout.json → "choca") y vuelve a alinear.

Uso:  .venv/bin/python partir.py <proyecto>
Busca en pages.txt el renglón de cada página que choca y lo divide en dos renglones por la mitad (en una frontera de línea,
sin dejar una línea gigante B sola al final si se puede). Devuelve código 0 si partió algo (hay que volver a sacar el layout),
1 si no había nada que partir, 2 si alguna página que choca ya es de una sola línea (no se puede partir más: revisar a mano).
"""
import sys, os, json, subprocess

proj = sys.argv[1]; P = lambda f: os.path.join(proj, f)
L = json.load(open(P("layout.json")))["paginas"]; PG = json.load(open(P("pages.json")))
filas = open(P("pages.txt")).read().split("\n")
partir, sueltas = set(), []
for k, p in enumerate(L):
    if p and p.get("choca"):
        for f in PG[k]["filas"]:
            if len(filas[f].split(" / ")) > 1: partir.add(f)
            else: sueltas.append(filas[f].strip())
for f in sorted(partir, reverse=True):
    txt = filas[f]; tag = ""
    if txt.rstrip().split()[-1].startswith("#"): txt, tag = txt.rsplit(" ", 1); tag = " " + tag
    partes = txt.split(" / "); n = len(partes)
    corto = lambda x: len(x.split(":", 1)[1].strip()) <= 3                       # "a", "tu", "en": no se queda solo al final
    # mitad más pareja posible, sin dejar una palabrita suelta al final del primer pedazo ni empezar el segundo con ella sola
    opciones = sorted(range(1, n), key=lambda m: abs(m - n / 2))
    m = next((m for m in opciones if not corto(partes[m - 1]) and not (m == n - 1 and corto(partes[m]))), opciones[0])
    filas[f] = " / ".join(partes[:m]) + "\n" + " / ".join(partes[m:]) + tag
    print(f"partido: «{txt.strip()}»\n   → «{' / '.join(partes[:m])}»\n   → «{' / '.join(partes[m:])}»")
open(P("pages.txt"), "w").write("\n".join(filas))
if sueltas: print("⚠ no se pueden partir más (una sola línea y aun así tapan la cara):", sueltas)
sys.exit(0 if partir else (2 if sueltas else 1))
