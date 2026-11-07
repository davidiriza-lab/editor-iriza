"""Revisa, fotograma por fotograma, dónde quedaron los textos.

Uso:  python revisar_texto.py <proyecto>
Necesita caras.json (bin/caras, lo corre armar.py) y layout.json (lo escribe render.mjs; `node render.mjs <p> layout` lo
genera en un segundo sin renderizar). Comprueba:
  1. ningún subtítulo encima de la cabeza (coronilla → barbilla +10 %, ancho de cara +15 % por lado; sin contar tomas de stock)
  2. subtítulos y flecha dentro de la zona segura de Instagram (plantilla.json → zona_segura)
  3. ningún subtítulo encima de la flecha mientras se ve
  4. que layout.json sea más nuevo que pages.json / proyecto.json / caras.json (si no, la revisión sería falsa)
Sale con código 1 si algo falla.
"""
import sys, os, json

proj = sys.argv[1]; P = lambda f: os.path.join(proj, f)
for f in ("pages.json", "proyecto.json", "caras.json"):
    if os.path.exists(P(f)) and os.path.getmtime(P(f)) > os.path.getmtime(P("layout.json")) + 1:
        print(f"✗ layout.json es más viejo que {f}: corre `node render.mjs {proj} layout` y vuelve a revisar"); sys.exit(1)
C = json.load(open(P("proyecto.json"))); CA = json.load(open(P("caras.json"))); LY = json.load(open(P("layout.json")))
L = [p for p in LY["paginas"] if p]; FL = LY.get("flecha"); ZS = LY.get("zona_segura")
mal_flecha = None
if "flecha" in C and C["flecha"].get("en") is None:
    mal_flecha = "el proyecto pide flecha pero no tiene tiempo (no se encontró «clic» al armar): revisa proyecto.json → flecha"; FL = None
br = C.get("broll", [])
mal = [mal_flecha] if mal_flecha else []

# 1. cara (los fotogramas sin detección usan la más cercana ≤ 1 s, como el overlay)
F = CA["f"]; ok = [f[1] >= 0 and f[4] - f[2] >= 60 for f in F]
choques, revisados = {}, 0
for i, f in enumerate(F):
    t = f[0]
    if any(r["a"] - .02 <= t < r["b"] + .02 for r in br): continue
    if not ok[i]:
        cerca = [j for j in range(max(0, i - 30), min(len(F), i + 31)) if ok[j]]
        if not cerca: continue
        f = [t] + F[min(cerca, key=lambda j: abs(j - i))][1:]
    _, x0, y0, x1, y1, cab = f; hc, wc = y1 - y0, x1 - x0
    top = cab if cab >= 0 else y0 - .35 * hc
    cx0, cx1, cy0, cy1 = x0 - .15 * wc, x1 + .15 * wc, top, y1 + .1 * hc
    revisados += 1
    for k, p in enumerate(L):
        if p["start"] - .3 <= t <= p["end"] + .3 and p["x0"] < cx1 and p["x1"] > cx0 and p["y0"] < cy1 and p["y1"] > cy0:
            choques.setdefault(k, []).append(round(t, 2))
for k, ts in choques.items():
    mal.append(f"página {k} ({L[k]['start']:.2f}-{L[k]['end']:.2f}s) encima de la cara en {len(ts)} fotogramas ({ts[0]}–{ts[-1]}s)")

# 2. zona segura
if ZS:
    dentro = lambda b: b["x0"] >= ZS["x0"] - 2 and b["x1"] <= ZS["x1"] + 2 and b["y0"] >= ZS["y0"] - 2 and b["y1"] <= ZS["y1"] + 2
    for k, p in enumerate(L):
        if not dentro(p): mal.append(f"página {k} ({p['start']:.2f}s) fuera de la zona segura de Instagram: x {p['x0']:.0f}–{p['x1']:.0f}, y {p['y0']:.0f}–{p['y1']:.0f}")
    if FL and not dentro(FL): mal.append(f"flecha fuera de la zona segura: y {FL['y0']:.0f}–{FL['y1']:.0f}")

# 3. texto contra flecha
if FL:
    for k, p in enumerate(L):
        if p["end"] + .3 > FL["en"] and p["start"] - .3 < FL["fin"] and p["x0"] < FL["x1"] and p["x1"] > FL["x0"] and p["y0"] < FL["y1"] and p["y1"] > FL["y0"]:
            mal.append(f"página {k} ({p['start']:.2f}s) encima de la flecha")
for k, p in enumerate(L):
    if p.get("sc", 1) < 1: print(f"  · página {k} se encogió a {p['sc']:.0%} para no tapar la cara")

print(f"{revisados} fotogramas con persona revisados · {len(L)} páginas")
if not mal: print("✓ textos fuera de la cara, dentro de la zona segura y sin pisar la flecha"); sys.exit(0)
for m in mal: print("  ⚠", m)
sys.exit(1)
