"""Tomas de stock sin caras debajo de los subtítulos (después del acomodo de textos, antes del contraste).

Uso:  .venv/bin/python stock_caras.py <proyecto>
El acomodo (overlay.html) esquiva la cara de la persona, pero no puede esquivar las caras de las tomas: son 8 tomas
distintas en ~2 s. Aquí se hace al revés: con las cajas reales de los subtítulos (layout.json), cada toma busca un
pedazo del stock, dentro de un mismo plano (stock.py), donde ninguna cara (todas las que ve Vision, ojos incluidos)
toque el texto que está en pantalla en ese momento, y que no sea del mismo plano que la toma de al lado (se veía como
un brinco) ni, si se puede, que la de dos lugares antes o después (A-B-A se siente como tropiezo). Se prefiere el pedazo que ya tenía; si no sirve, uno de un plano poco usado, sin repetir imagen de otra
toma. Si cambió algo, rehace corte.mp4 (stock_encima.py).
Sale con código 1 si alguna toma no tiene ningún pedazo libre.
"""
import sys, os, json, subprocess
import conf

proj = sys.argv[1]; P = lambda f: os.path.join(proj, f)
C = conf.cargar(proj); RAW = json.load(open(P("proyecto.json"))); br = RAW.get("broll", [])
if not br: print("sin tomas de stock"); sys.exit(0)
LY = [p for p in json.load(open(P("layout.json")))["paginas"] if p]
M = 30                                                     # aire alrededor del texto (las palabras entran 22 px más abajo)

def fotos(src):
    j = src + ".fotogramas.json"
    if not os.path.exists(j) or os.path.getmtime(j) < os.path.getmtime(src):
        subprocess.run([os.path.join(conf.HERE, "bin", "fotogramas"), src, j], check=True)
    return json.load(open(j))

def choques(r, desde):
    """cuadros del stock que se ven en la ventana [a, b) cuya cara toca un subtítulo activo"""
    FO = FOT[r["fuente"]]; fps = FO["fps"]; n = 0
    cajas = [p for p in LY if p["start"] - .3 < r["b"] and r["a"] < p["end"] + .05]
    if not cajas: return 0
    for k in range(int(round((r["b"] - r["a"]) * fps)) + 1):
        i = int(round((desde + k / fps) * fps))
        if i >= len(FO["f"]): return 99
        for x0, y0, x1, y1 in FO["f"][i]["caras"]:
            h = y1 - y0
            if h < 60: continue
            fx0, fx1, fy0, fy1 = x0 - .1 * h, x1 + .1 * h, y0 - .25 * h, y1 + .08 * h     # frente y barbilla, como revisar_final
            if any(fx0 < p["x1"] + M and fx1 > p["x0"] - M and fy0 < p["y1"] + M and fy1 > p["y0"] - M for p in cajas): n += 1; break
    return n

FOT = {r["fuente"]: fotos(r["fuente"]) for r in br}
TOM = {f: json.load(open(f + ".tomas.json")) for f in FOT}
plano = lambda f, d: next((i for i, (p0, p1) in enumerate(TOM[f]["planos"]) if p0 - .01 <= d < p1), -1)
cambios, sin_salida = [], []
for k, r in enumerate(br):
    dur = r["b"] - r["a"]; f = r["fuente"]
    vecinos = [plano(o["fuente"], o["desde"]) for j, o in enumerate(br) if abs(j - k) == 1 and o["fuente"] == f]
    a_dos = [plano(o["fuente"], o["desde"]) for j, o in enumerate(br) if abs(j - k) == 2 and o["fuente"] == f]   # A-B-A
    antes = choques(r, r["desde"]); pl0 = plano(f, r["desde"]); pegada = pl0 in vecinos
    if antes == 0 and not pegada and pl0 not in a_dos: continue
    # dos tomas seguidas del mismo plano se ven como un brinco; se prefieren planos que no usen las otras tomas.
    # Imagen que ya usan las otras tomas: no se repite; si así no hay salida, solo se evita la de las tomas vecinas
    for vecinas in (False, True):
        usados = [(o["desde"], o["desde"] + o["b"] - o["a"]) for j, o in enumerate(br)
                  if j != k and o["fuente"] == f and (not vecinas or abs(j - k) == 1)]
        cands = []
        for t in TOM[f]["tramos"]:
            d = t["a"]; pl = plano(f, t["a"])
            veces = sum(plano(o["fuente"], o["desde"]) == pl for j, o in enumerate(br) if j != k and o["fuente"] == f)
            while d + dur <= t["b"] + 1e-6:
                if not any(d < u1 and u0 < d + dur for u0, u1 in usados):
                    cands.append((choques(r, d), pl in vecinos, pl in a_dos, veces, t["dividida"], abs(d - r["desde"]), round(d, 3)))
                d += 1 / 30
        cands.sort()
        if cands and cands[0][0] == 0 and not cands[0][1] and not cands[0][2]: break
    if not cands or cands[0][0] > 0:
        sin_salida.append(f"toma {k} ({r['a']:.2f}s): ningún pedazo del stock deja libre el texto"); continue
    if cands[0][:3] >= (antes, pegada, pl0 in a_dos): continue          # no hay nada mejor que lo que ya tenía
    motivo = f"cara bajo el texto en {antes} cuadros" if antes else "mismo plano que la toma de al lado" if pegada else "mismo plano dos tomas antes o después (A-B-A)"
    cambios.append(f"toma {k} ({r['a']:.2f}s): stock {r['desde']:.2f}s → {cands[0][-1]:.2f}s ({motivo})")
    r["desde"] = cands[0][-1]
    if cands[0][1]: print(f"  · toma {k} ({r['a']:.2f}s): no hay plano distinto al de al lado sin cara bajo el texto")

for c in cambios: print("  ↻", c)
for s in sin_salida: print("  ⚠", s)
if cambios:
    json.dump(RAW, open(P("proyecto.json"), "w"), ensure_ascii=False, indent=1)
    subprocess.run([os.path.join(conf.HERE, ".venv", "bin", "python"), os.path.join(conf.HERE, "stock_encima.py"), proj], check=True)
if not cambios and not sin_salida: print("✓ ninguna cara de las tomas queda debajo de un subtítulo")
sys.exit(1 if sin_salida else 0)
