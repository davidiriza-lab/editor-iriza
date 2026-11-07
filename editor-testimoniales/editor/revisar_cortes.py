"""Revisa que los cambios de escena no se vean raros (después de armar.py).

Uso:  .venv/bin/python revisar_cortes.py <proyecto>
  1. Tomas de stock: ninguna cruza un cambio de plano del video de stock (si no, se ve un destello de otra imagen).
  2. Rebanadas: entre una toma de stock y un corte del armado no quedan < 0.15 s de la persona (3–4 cuadros sueltos).
  3. Brincos: cada corte donde se ve a la persona lleva transición (no está en "sin_transicion" ni tapado sin querer).
  4. Final: la cola es imagen real (no cuadro congelado) y dura lo de `cola`.
Sale con código 1 si algo falla.
"""
import sys, os, json
import conf

proj = sys.argv[1]; P = lambda f: os.path.join(proj, f)
C = conf.cargar(proj); CJ = json.load(open(P("cortes.json"))); bd = CJ["fronteras"][:-1]
br = C.get("broll", []); mal, ok = [], []

# 1. tomas que cruzan un cambio de plano
planos_de = {}
for r in br:
    st = r["fuente"] + ".tomas.json"
    if r["fuente"] not in planos_de:
        planos_de[r["fuente"]] = json.load(open(st))["planos"] if os.path.exists(st) else None
    pl = planos_de[r["fuente"]]
    if pl is None: mal.append(f"no está analizado el stock {os.path.basename(r['fuente'])} (corre stock.py)"); continue
    a, b = r["desde"], r["desde"] + (r["b"] - r["a"])
    if not any(p0 - .01 <= a and b <= p1 + .01 for p0, p1 in pl):
        mal.append(f"toma de stock en {r['a']:.2f}s (stock {a:.2f}–{b:.2f}) cruza un cambio de plano → destello")
if br: ok.append(f"{len(br)} tomas de stock revisadas contra los cambios de plano")

# 2. rebanadas de persona entre stock y cortes
marcas = sorted({x for r in br for x in (r["a"], r["b"])} | set(bd))
for x, y in zip(marcas, marcas[1:]):
    tapado = any(r["a"] - .01 <= x and y <= r["b"] + .01 for r in br)
    if not tapado and 0 < y - x < .15: mal.append(f"rebanada de {y - x:.2f}s de la persona entre {x:.2f} y {y:.2f}s (se ve como parpadeo)")

# 3. cortes visibles sin transición
sin = C.get("sin_transicion", [])
for c in bd:
    if any(r["a"] - .05 < c < r["b"] + .05 for r in br): continue
    if any(abs(c - s) < .05 for s in sin): mal.append(f"corte en {c:.2f}s sin transición (está en sin_transicion): se verá el brinco")
ok.append(f"{len(bd)} cortes del armado; los visibles llevan desenfoque de transición")

# 4. final
if CJ.get("cola_real") is None: mal.append("proyecto viejo: el final se congela (vuelve a correr armar.py)")
elif CJ["cola_real"] < C.get("cola", .6) - .1: mal.append(f"el video original se acaba: solo hay {CJ['cola_real']:.2f}s de imagen tras la última palabra")
else: ok.append(f"final con {CJ['cola_real']:.2f}s de imagen real y fundido desde {CJ['fin_voz'] - .15:.2f}s")

for o in ok: print("  ✓", o)
for m in mal: print("  ⚠", m)
sys.exit(1 if mal else 0)
