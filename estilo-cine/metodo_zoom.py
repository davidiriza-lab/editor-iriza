"""Camino de zoom para la grabación de pantalla (panel de abajo, 4:3): sigue al cursor rojo cuando se mueve.
Uso: .venv/bin/python estilo-cine/metodo_zoom.py proyectos/<n>
Lee scr/%05d.jpg (1920x1080) y escribe zoom.json: [[cx, cy, ancho], ...] por cuadro.
- cursor = píxeles rojos que cambiaron respecto a hace 3 cuadros
- zona muerta: la cámara solo se mueve si el cursor sale del centro del encuadre
- si cambia casi toda la pantalla (paneo del tablero), abre el plano
"""
import sys, os, glob, json
import numpy as np, cv2

proy = sys.argv[1]
fs = sorted(glob.glob(os.path.join(proy, 'scr', '*.jpg')))
SW, SH, K = 1920, 1080, 4            # tamaño original y factor de reducción para analizar
ANCHO = int(sys.argv[sys.argv.index('--ancho') + 1]) if '--ancho' in sys.argv else 1180
ANCHO_PANEO, ASP = max(1440, ANCHO), 810 / 1080
small = [None] * len(fs)

def lee(i):
    if small[i] is None: small[i] = cv2.resize(cv2.imread(fs[i]), (SW // K, SH // K), interpolation=cv2.INTER_AREA)
    return small[i]

obj, cursor_visto = [], 0
cx, cy, w = SW / 2, SH / 2, ANCHO
for i in range(len(fs)):
    a = lee(i); b = lee(max(0, i - 3))
    if i > 6: small[i - 6] = None
    g1, g0 = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    cambio = cv2.absdiff(g1, g0) > 22
    frac = cambio.mean()
    B, G, R = [a[..., k].astype(int) for k in range(3)]
    rojo = (R > 165) & (G < 95) & (B < 110) & (R - G > 90)
    cur = rojo & cv2.dilate(cambio.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    ys, xs = np.nonzero(cur)
    if frac > .28:                                   # paneo / cambio de vista: abrir y centrar en el movimiento
        w = ANCHO_PANEO; ys2, xs2 = np.nonzero(cambio); cx, cy = xs2.mean() * K, ys2.mean() * K
    elif len(xs) >= 3:
        px, py = np.median(xs) * K, np.median(ys) * K
        h = w * ASP
        if abs(px - cx) > w * .22 or abs(py - cy) > h * .22: cx, cy = px, py + h * .08
        w = ANCHO
    obj.append([cx, cy, w])

o = np.array(obj, float)
def suave(x, tau):  # EMA ida y vuelta (sin retraso)
    al = 1 - np.exp(-1 / (tau * 23.976)); y = x.copy()
    for i in range(1, len(y)): y[i] = y[i - 1] + al * (y[i] - y[i - 1])
    for i in range(len(y) - 2, -1, -1): y[i] = y[i + 1] + al * (y[i] - y[i + 1])
    return y
o[:, 0], o[:, 1], o[:, 2] = suave(o[:, 0], .55), suave(o[:, 1], .55), suave(o[:, 2], .8)
for r in o:  # que el recorte no se salga de la pantalla
    hw, hh = r[2] / 2, r[2] * ASP / 2
    r[0] = min(max(r[0], hw), SW - hw); r[1] = min(max(r[1], hh), SH - hh)
json.dump(np.round(o, 1).tolist(), open(os.path.join(proy, 'zoom.json'), 'w'))
print(f'✓ zoom.json ({len(o)} cuadros)')
