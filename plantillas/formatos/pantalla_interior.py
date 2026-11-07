"""Saca DERECHO el video que se reproduce dentro de una laptop/monitor filmado (familia "Pantalla Filmada").

Uso:  python pantalla_interior.py <video> <salida_dir> [--esquinas x1,y1,x2,y2,x3,y3,x4,y4] [--cuadro N]
  1. Esquinas de la pantalla en el cuadro de referencia (por defecto el del medio): si no se dan, se buscan solas
     (la zona que más cambia con el tiempo = el contenido de la pantalla) → revisar <salida>/pantalla_ref.jpg.
  2. Sigue la pantalla en CADA cuadro con puntos del marco, el teclado y el fondo (no del contenido, que cambia):
     homografía cuadro de referencia → cuadro i.
  3. Endereza la pantalla con perspectiva y escribe <salida>/interior.mp4 (con el audio original) + esquinas.json.
"""
import sys, os, json, subprocess
import numpy as np, cv2

src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
arg = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS) or 30
F = []
while True:
    ok, fr = cap.read()
    if not ok: break
    F.append(fr)
n = len(F); H, W = F[0].shape[:2]; ref = int(arg("--cuadro") or n // 2)
esc = 540 / W; peq = lambda im: cv2.resize(im, (540, int(H * esc)))
G = [cv2.cvtColor(peq(f), cv2.COLOR_BGR2GRAY) for f in F]

def ordenar(p):
    p = np.array(p, np.float32); s = p.sum(1); d = np.diff(p, axis=1).ravel()
    return np.array([p[np.argmin(s)], p[np.argmin(d)], p[np.argmax(s)], p[np.argmax(d)]], np.float32)  # sup-izq, sup-der, inf-der, inf-izq

# ---------- 1. esquinas en el cuadro de referencia ----------
if arg("--esquinas"):
    q = ordenar(np.array(list(map(float, arg("--esquinas").split(",")))).reshape(4, 2))
else:
    # lo que más cambia con el tiempo (alineado a la referencia) es el contenido de la pantalla
    orb = cv2.ORB_create(3000); kr, dr = orb.detectAndCompute(G[ref], None); bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    acc = np.zeros(G[ref].shape, np.float32); cnt = 0
    for i in range(0, n, max(1, n // 60)):
        k, d = orb.detectAndCompute(G[i], None)
        if d is None or dr is None: continue
        m = sorted(bf.match(dr, d), key=lambda x: x.distance)[:400]
        if len(m) < 12: continue
        Hm, _ = cv2.findHomography(np.float32([k[x.trainIdx].pt for x in m]), np.float32([kr[x.queryIdx].pt for x in m]), cv2.RANSAC, 4)
        if Hm is None: continue
        al = cv2.warpPerspective(G[i], Hm, G[ref].shape[::-1]).astype(np.float32)
        acc += np.abs(al - G[ref]); cnt += 1
    mapa = cv2.GaussianBlur(acc / max(cnt, 1), (0, 0), 6)
    _, bi = cv2.threshold(mapa, np.percentile(mapa, 70), 255, cv2.THRESH_BINARY)
    bi = cv2.morphologyEx(bi.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    cs, _ = cv2.findContours(bi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cs, key=cv2.contourArea); ap = cv2.approxPolyDP(c, .04 * cv2.arcLength(c, True), True)
    q = ordenar(ap.reshape(-1, 2) if len(ap) == 4 else cv2.boxPoints(cv2.minAreaRect(c))) / esc

# ---------- 2. seguir la pantalla en cada cuadro (puntos FUERA de la pantalla) ----------
mask = np.full(G[ref].shape, 255, np.uint8)
cv2.fillConvexPoly(mask, (ordenar(q) * esc).astype(np.int32), 0)
mask = cv2.erode(mask, np.ones((15, 15), np.uint8))
orb = cv2.ORB_create(4000); kr, dr = orb.detectAndCompute(G[ref], mask); bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
Qs, prev = [], None
for i in range(n):
    k, d = orb.detectAndCompute(G[i], None); Hm = None
    if d is not None and dr is not None:
        m = sorted(bf.match(dr, d), key=lambda x: x.distance)[:500]
        if len(m) >= 15:
            Hm, inl = cv2.findHomography(np.float32([kr[x.queryIdx].pt for x in m]), np.float32([k[x.trainIdx].pt for x in m]), cv2.RANSAC, 3)
            if Hm is not None and inl.sum() < 12: Hm = None
    qi = cv2.perspectiveTransform((q * esc).reshape(-1, 1, 2), Hm).reshape(4, 2) / esc if Hm is not None else (prev if prev is not None else q)
    if prev is not None and np.abs(qi - prev).max() > W * .08: qi = prev         # salto raro: conservar el anterior
    Qs.append(qi); prev = qi
Qs = np.array(Qs)
k = max(1, int(fps * .1)); Qs = np.array([Qs[max(0, i - k):i + k + 1].mean(0) for i in range(n)])  # suavizado 0.2 s

# ---------- 3. enderezar ----------
ancho = float(np.linalg.norm(q[1] - q[0]) + np.linalg.norm(q[2] - q[3])) / 2
alto = float(np.linalg.norm(q[3] - q[0]) + np.linalg.norm(q[2] - q[1])) / 2
r = ancho / alto
OW = 1440 if r >= 1 else int(1440 * r) // 2 * 2; OH = int(OW / r) // 2 * 2 if r >= 1 else 1440
dst = np.float32([[0, 0], [OW, 0], [OW, OH], [0, OH]])
tmp = os.path.join(out, "_interior_sin_audio.mp4")
vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (OW, OH))
for f, qi in zip(F, Qs): vw.write(cv2.warpPerspective(f, cv2.getPerspectiveTransform(qi.astype(np.float32), dst), (OW, OH), flags=cv2.INTER_CUBIC))
vw.release()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-shortest", os.path.join(out, "interior.mp4")], check=True); os.remove(tmp)
vis = F[ref].copy(); cv2.polylines(vis, [q.astype(np.int32)], True, (0, 0, 255), max(3, W // 300))
cv2.imwrite(os.path.join(out, "pantalla_ref.jpg"), cv2.resize(vis, (540, int(H * esc))))
json.dump({"ref": ref, "esquinas_ref": q.round(1).tolist(), "tam": [OW, OH], "fps": fps}, open(os.path.join(out, "esquinas.json"), "w"))
print(f"✓ interior {OW}x{OH} · {n} cuadros · revisa {out}/pantalla_ref.jpg")
