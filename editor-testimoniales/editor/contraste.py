"""Mide qué tan claro es el fondo detrás de cada subtítulo y marca los que necesitan más contraste.

Uso:  .venv/bin/python contraste.py <proyecto>       (después de `node render.mjs <p> layout`)
Toma 6 cuadros del armado dentro del tiempo de cada página y mide la luz en su caja de texto. Fondo claro (blusa blanca,
librero blanco, pared clara) → contraste.json marca la página y el overlay le pone sombra fuerte + velo oscuro suave.
"""
import sys, os, json, subprocess
import numpy as np

proj = sys.argv[1]; P = lambda f: os.path.join(proj, f)
L = json.load(open(P("layout.json")))["paginas"]
W, H = (1080, 1920) if json.load(open(P("proyecto.json"))).get("vertical") else (1920, 1080)
def cuadro(t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", P("corte.mp4"), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W) if len(raw) == W * H else None
claras = {}
for k, p in enumerate(L):
    if not p: continue
    x0, x1, y0, y1 = (max(0, int(p[c])) for c in ("x0", "x1", "y0", "y1"))
    vals = []
    for t in np.linspace(p["start"], max(p["start"], p["end"] - .05), 6):
        g = cuadro(t)
        if g is not None: z = g[y0:min(H, y1), x0:min(W, x1)]; vals.append((z.mean(), (z > 190).mean()))
    if not vals: continue
    media, brillo = np.mean([v[0] for v in vals]), np.mean([v[1] for v in vals])
    if media > 135 or brillo > .3: claras[k] = {"luz": round(float(media)), "brillo": round(float(brillo), 2)}
json.dump(claras, open(P("contraste.json"), "w"))
print(f"{len(claras)} de {sum(1 for p in L if p)} subtítulos sobre fondo claro → sombra fuerte: {sorted(claras)}")
