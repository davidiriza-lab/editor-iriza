"""Pasa los tiempos de voz/palabras.json del corte anterior (corte/mapa_v1.json + voz/palabras_v1.json) al corte nuevo
(corte/mapa.json) por tiempo de origen, sin volver a transcribir: las palabras y sus índices quedan idénticos.
Uso: python3 proyectos/<proyecto>/remapear.py <clave>"""
import sys, json, bisect
P = f'{B}/{sys.argv[1]}'
v1 = json.load(open(f'{P}/corte/mapa_v1.json'))['piezas']; v2 = json.load(open(f'{P}/corte/mapa.json'))['piezas']; W = json.load(open(f'{P}/voz/palabras_v1.json'))
def acum(pz):
    T, t = [], 0
    for a, b in pz: T.append(t); t += b - a
    return T
T1, T2 = acum(v1), acum(v2)
# armar.py mueve el inicio de las palabras que cruzan un corte; se recuperan los inicios originales de transcripcion.txt
import re, os
B = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))   # carpeta del proyecto (copia de esta plantilla); correr desde la raíz del repo
if os.path.exists(f'{P}/transcripcion.txt'):
    lin = next((l for l in open(f'{P}/transcripcion.txt').read().splitlines() if l.startswith('0:')), '')
    orig = re.findall(r'(\d+):\S+@(\d+\.\d+)', lin)
    if len(orig) == len(W):
        for (i, a0) in orig: W[int(i)]['a'] = float(a0)
        print('  inicios originales recuperados de transcripcion.txt')
def a_origen(t):
    i = max(0, bisect.bisect_right(T1, t) - 1); return v1[i][0] + (t - T1[i])
def a_nuevo(src):
    best = None
    for j, (a, b) in enumerate(v2):
        if a - 1e-3 <= src <= b + 1e-3: return T2[j] + (src - a)
        d = min(abs(src - a), abs(src - b)); best = min(best or (9e9, 0), (d, T2[j] + (min(max(src, a), b) - a)))
    return best[1]
lejos = 0
for w in W:
    for k in ('a', 'b'): w[k] = round(a_nuevo(a_origen(w[k])), 3)
json.dump(W, open(f'{P}/voz/palabras.json', 'w'), ensure_ascii=False, indent=1)
print(f'✓ {sys.argv[1]}: {len(W)} palabras remapeadas · {len(v1)} → {len(v2)} piezas · {sum(b - a for a, b in v1):.2f} s → {sum(b - a for a, b in v2):.2f} s')
