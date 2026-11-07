"""Mide en el VIDEO FINAL cuánto salta la cara en cada corte (bin/caras sobre el mp4 renderizado).
Uso: .venv/bin/python proyectos/<proyecto>/auditar_final.py <clave>"""
import sys, json, subprocess, os
import numpy as np
B = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))   # carpeta del proyecto (copia de esta plantilla); correr desde la raíz del repo
K = sys.argv[1]; P = f'{B}/{K}'; mp4 = f'{P}/salida/{K}.mp4'; out = f'{P}/salida/_caras_final.json'
subprocess.run(['editor-testimoniales/editor/bin/caras', mp4, out], check=True, capture_output=True)
F = [c for c in json.load(open(out))['f'] if len(c) >= 5]
cfg = json.load(open(f'{P}/cine.json'))
def cara(t, lado):
    c = [f for f in F if (t - .25 <= f[0] < t - .02 if lado < 0 else t + .02 < f[0] <= t + .25)]
    if not c: return None
    c = [f for f in c if f[4] - f[2] > 40]
    if not c: return None
    f = c[-1] if lado < 0 else c[0]; return ((f[1] + f[3]) / 2, (f[2] + f[4]) / 2, f[4] - f[2])
# inicio de cada escena = primera palabra de sus grupos; solo cuentan los cortes con la persona a cuadro de los dos lados
W = json.load(open(f'{P}/voz/palabras.json')); ini, n = [], 0
for e in cfg['escenas']:
    ini.append((W[min(n, len(W) - 1)]['a'], e.get('visual', 'persona'))); n += sum(len(l.split(' ')) for gp in e['grupos'] for l in gp['lineas'])
def visual(t): return [v for a, v in ini if a <= t][-1] if any(a <= t for a, _ in ini) else ini[0][1]
malos = 0
print(f'===== {K} (video final)')
for t in cfg['cortes']:
    if visual(t - .06) != 'persona' or visual(t + .06) != 'persona': continue
    a, b = cara(t, -1), cara(t, +1)
    if not a or not b: continue
    d, s = np.hypot(b[0] - a[0], b[1] - a[1]), abs(b[2] - a[2]) / a[2] * 100
    m = d > 45 or s > 10; malos += m
    print(f'  corte {t:6.2f}: cara se mueve {d:4.0f} px, tamaño {s:4.1f} %' + ('   ← SALTO' if m else ''))
print(f'  → {malos} cortes con salto visible')
