"""Paso 6 (opcional) — La persona mete tomas de stock en su versión ("... PRE SUBS V1.mp4"): subtitular solo esas tomas.

Uso:  .venv/bin/python v1.py <carpeta_proyecto> <video_v1>

Compara el V1 contra nuestro EDIT (<proyecto>/<salida>):
  1. desfases de audio (a veces se recortan pedacitos): mapa V1 -> EDIT por tramos
  2. tomas insertadas: correlación normalizada de cuadros (aguanta cambios de color); bordes ajustados a sus cortes
  3. qué frases de pages.json caen en cada toma
Genera v1.json y hojas tomas_<n>.jpg para revisar. Por defecto todas las frases van "abajo" (subtítulo normal).
Revisa las hojas: si una toma tiene un lado limpio (oscuro, sin caras), cambia esa frase en v1.json -> "modos" a
"derecha"/"izquierda" y pon su x en "izquierdas" {indice: px}; "omitir" para no subtitular (p. ej. una animación con texto).
Luego:  node render.mjs <proyecto> v1 stills t1,t2   y   node render.mjs <proyecto> v1
"""
import sys, os, json, subprocess
import numpy as np
from PIL import Image

proj, v1 = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); P = lambda f: os.path.join(proj, f)
C = json.load(open(P("proyecto.json"))); EDIT = P(C.get("salida", "EDIT.mp4"))
PAGES = json.load(open(P("pages.json")))

def env(path):   # envolvente de audio a 100 Hz
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True).stdout
    x = np.abs(np.frombuffer(raw, np.float32)); return x[:len(x) // 80 * 80].reshape(-1, 80).mean(1)
def corr(a, b): return np.corrcoef(a, b)[0, 1] if len(a) == len(b) and a.std() > 1e-5 and b.std() > 1e-5 else -2
A, B = env(v1), env(EDIT)

# ---------- 1. desfases ----------
lags = []
for i in range(0, len(A) - 150, 50):
    seg = A[i:i + 150]
    if seg.std() < 1e-4: continue
    best = max(range(-300, 501), key=lambda L: corr(seg, B[i + L:i + L + 150]) if i + L >= 0 else -2)
    if corr(seg, B[i + best:i + best + 150]) > .8: lags.append(best)
cands = []
for L in sorted(set(lags), key=lambda x: -lags.count(x)):
    if lags.count(L) >= 2 and all(abs(L - c) > 4 for c in cands): cands.append(L)
seq = []
for i in range(0, len(A) - 60, 10):
    seg = A[i:i + 60]; sc = [corr(seg, B[i + L:i + L + 60]) if i + L >= 0 else -2 for L in cands]
    seq.append((i / 100, cands[int(np.argmax(sc))] if sc and max(sc) > .85 else None))
lab = [(t, L) for t, L in seq if L is not None]
desf, cur = [], None
for k, (t, L) in enumerate(lab):     # cambio de tramo cuando el nuevo desfase se sostiene 3 muestras seguidas
    if L != cur and all(x[1] == L for x in lab[k:k + 3]):
        desf.append([0.0 if cur is None else round(t, 2), round(L / 100, 2)]); cur = L
print("desfases V1->EDIT (desde s, +s):", desf)
off = lambda t: [o for d, o in desf if t >= d][-1]

# ---------- 2. tomas insertadas ----------
def frames(path, fps, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
Vf, Ef = frames(v1, 10, 96, 54), frames(EDIT, 10, 96, 54)
def ncc(a, b): a = a - a.mean(); b = b - b.mean(); return (a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-6)
nc = np.array([max([ncc(Vf[i], Ef[j]) for j in range(int(round((i / 10 + off(i / 10)) * 10)) - 1, int(round((i / 10 + off(i / 10)) * 10)) + 2) if 0 <= j < len(Ef)] or [0]) for i in range(len(Vf))])
F30 = frames(v1, 30, 160, 90); dd = np.abs(np.diff(F30, axis=0)).mean((1, 2))
# planos del V1 (cortes = picos aislados de diferencia) y parecido mediano de cada plano con el EDIT
cortes = [0.0] + [(i + 1) / 30 for i in range(len(dd)) if dd[i] > 30 and dd[i] / (np.median(np.r_[dd[max(0, i - 8):i], dd[i + 1:i + 9]]) + .5) > 4] + [len(Vf) / 10]
planos = [(a, b, float(np.median(nc[int(a * 10):max(int(a * 10) + 1, int(b * 10))]))) for a, b in zip(cortes, cortes[1:]) if b - a >= .15]
ref = float(np.percentile([m for a, b, m in planos for _ in range(int((b - a) * 10))], 75))   # parecido típico de la entrevista
umbral = ref * .82
print(f"parecido típico de la entrevista {ref:.2f} -> umbral de toma insertada {umbral:.2f}")
ventanas = []
for a, b, m in planos:
    if m >= umbral: continue
    if ventanas and a - ventanas[-1][1] < .3: ventanas[-1][1] = round(b, 3)
    else: ventanas.append([round(a, 3), round(b, 3)])
ventanas = [w for w in ventanas if w[1] - w[0] >= .5]

# ---------- 3. frases por toma ----------
def inv(te):   # EDIT -> V1 (si cae en un pedazo recortado, se pega al borde)
    for k, (d, o) in enumerate(desf):
        hasta = desf[k + 1][0] if k + 1 < len(desf) else 1e9
        if d <= te - o < hasta: return te - o
    return min((d for d, o in desf if d > 0), key=lambda d: abs(d - (te - off(te))), default=te)
modos = {}
print("\nTOMAS INSERTADAS (s del V1):")
for n, (a, b) in enumerate(ventanas, 1):
    print(f" {n}. {a:6.2f} – {b:6.2f}")
    for i, p in enumerate(PAGES):
        s, e = inv(p["start"]), inv(p["end"])
        if min(e, b) - max(s, a) > .25:
            modos[str(i)] = "abajo"
            print(f"     frase {i:2d} ({s:6.2f}-{e:6.2f}):", " / ".join(" ".join(w["t"] for w in l["w"]) for l in p["lines"]))
    ts = np.linspace(a + .2, b - .2, 5); ims = []
    for t in ts:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", v1, "-frames:v", "1", "-vf", "scale=480:270", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        ims.append(Image.frombytes("RGB", (480, 270), raw))
    g = Image.new("RGB", (480 * 5, 270)); [g.paste(im, (k * 480, 0)) for k, im in enumerate(ims)]; g.save(P(f"tomas_{n}.jpg"), quality=85)
json.dump({"video": v1, "salida": None, "desfases": desf, "ventanas": ventanas, "modos": modos, "izquierdas": {}}, open(P("v1.json"), "w"), indent=1, ensure_ascii=False)
print(f"\n-> v1.json y tomas_*.jpg en {proj}. Revisa las hojas, ajusta 'modos' si un lado está limpio y corre: node render.mjs {proj} v1")
