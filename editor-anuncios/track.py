"""Seguimiento de cara cuadro a cuadro sobre el video ya cortado (cut.mov) para mantener a la persona centrada.
Uso: .venv/bin/python track.py <carpeta_proyecto>
Genera face_track.json: [[t, cx, cy, fh], ...] cada 0.1 s (normalizado), suavizado sin cruzar cortes."""
import sys, os, json
import numpy as np, cv2

proj = sys.argv[1]; P = lambda f: os.path.join(proj, f)
edl = json.load(open(P("edl.json")))
ctx_cuts = []
cues = open(P("cues.js")).read() if os.path.exists(P("cues.js")) else ""
import re
m = re.search(r"splits:\s*\[([^\]]*)\]", cues)
if m: ctx_cuts = [float(x) for x in m.group(1).split(",") if x.strip()]
cuts = sorted(set([round(s["out_in"], 3) for s in edl["segments"]] + ctx_cuts + [edl["duration"]]))

cap = cv2.VideoCapture(P("cut.mov")); fps = edl["fps"][0] / edl["fps"][1]
casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
raw, i, step = [], 0, max(1, round(fps / 10))
while True:
    ok = cap.grab()
    if not ok: break
    if i % step == 0:
        ok, fr = cap.retrieve()
        h, w = fr.shape[:2]; sc = 480 / max(h, w)
        g = cv2.cvtColor(cv2.resize(fr, (int(w * sc), int(h * sc))), cv2.COLOR_BGR2GRAY)
        d = casc.detectMultiScale(g, 1.08, 5, minSize=(28, 28))
        t = i / fps
        if len(d):
            x, y, a, b = max(d, key=lambda r: r[2] * r[3]); gh, gw = g.shape
            raw.append([t, (x + a / 2) / gw, (y + b / 2) / gh, b / gh])
        else: raw.append([t, None, None, None])
    i += 1

# rellena huecos y suaviza (ventana 0.5 s) dentro de cada tramo entre cortes
arr = raw; out = []
for k in range(len(cuts)):
    a = cuts[k - 1] if k else 0.0; b = cuts[k]
    seg = [r for r in arr if a - 1e-6 <= r[0] < b - 1e-6]
    good = [r for r in seg if r[1] is not None]
    if not good: continue
    med = np.median(np.array([r[1:] for r in good]), axis=0)
    vals = []
    for r in seg:
        if r[1] is None:
            near = min(good, key=lambda g: abs(g[0] - r[0])); vals.append([r[0]] + near[1:])
        else: vals.append(r)
    v = np.array(vals, dtype=float)
    # descarta saltos absurdos de detección (> 15% del ancho respecto a la mediana)
    bad = np.abs(v[:, 1] - med[0]) > .15
    v[bad, 1:] = med
    # centro: promedio móvil de ~0.9 s (quita temblor del detector, sigue movimientos reales)
    win = 9
    sm = v.copy()
    for j in range(len(v)):
        lo, hi = max(0, j - win // 2), min(len(v), j + win // 2 + 1)
        sm[j, 1:3] = v[lo:hi, 1:3].mean(axis=0)
    # tamaño de cara: mediana (quita saltos del detector) + promedio de ~1.1 s (sigue los zooms de CapCut sin temblor)
    fhm = np.array([np.median(v[max(0, j - 2):j + 3, 3]) for j in range(len(v))])
    for j in range(len(v)):
        lo, hi = max(0, j - 5), min(len(v), j + 6)
        sm[j, 3] = fhm[lo:hi].mean()
    out += [[round(x, 3) for x in r] for r in sm.tolist()]
json.dump(out, open(P("face_track.json"), "w"))
print(f"{len(out)} muestras · cortes usados: {len(cuts) - 1}")
