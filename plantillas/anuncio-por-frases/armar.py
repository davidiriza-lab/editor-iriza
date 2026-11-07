"""cine.json con subtítulos por FRASE (armar_cine.py dejaba palabras sueltas).
Uso: python3 armar.py <clave>. Lee planes.py → PLANES[clave]; anclas como en armar_cine.py."""
import json, os, re, sys, unicodedata, statistics as st
sys.path.insert(0, os.path.dirname(__file__))
from planes import PLANES
K = sys.argv[1]; P = PLANES[K]; proy = os.path.join(os.path.dirname(os.path.abspath(__file__)), P.get('dir', K))
W = json.load(open(f'{proy}/voz/palabras.json')); N = len(W)
pz = json.load(open(f'{proy}/corte/mapa.json'))['piezas']; t = 0; CR = []
for a, b in pz[:-1]:
    t += b - a; CR.append(round(t, 3))
    for w in W:
        if w['b'] > t + .05:
            if w['a'] < t: w['a'] = round(t + .02, 3)
            break
json.dump(W, open(f'{proy}/voz/palabras.json', 'w'), ensure_ascii=False, indent=1)
def norm(x):
    x = unicodedata.normalize('NFD', x.lower()); x = ''.join(c for c in x if unicodedata.category(c) != 'Mn'); return re.sub(r'[^a-z0-9ñ]', '', x)
def idx(a):
    m = re.match(r'^@?([^#+\-$]+?)(?:#(\d+))?(\$)?(?:[+-]\d*\.?\d+)?$', a); pal, k = norm(m.group(1)), int(m.group(2) or 1); c = 0
    for i, w in enumerate(W):
        if norm(w['t']) == pal:
            c += 1
            if c == k: return i
    sys.exit(f'✗ ancla no encontrada: {a}')
def seg(a):
    x = a.lstrip('@')
    if re.match(r'^fin([+-]\d*\.?\d+)?$', x): return W[-1]['b'] + float(x[3:] or 0)   # @fin exacto; @fines es una palabra
    m = re.match(r'^([^#+\-$]+?)(?:#(\d+))?(\$)?([+-]\d*\.?\d+)?$', x); i = idx('@' + m.group(1) + (f'#{m.group(2)}' if m.group(2) else ''))
    return (W[i]['b'] if m.group(3) else W[i]['a']) + float(m.group(4) or 0)
def res(o):
    if isinstance(o, dict): return {k: res(v) for k, v in o.items()}
    if isinstance(o, list): return [res(v) for v in o]
    if isinstance(o, str) and o.startswith('@'): return round(seg(o), 3)
    return o
# frases → token visible por palabra, con límites de frase
vis, fin = [], set(); 
for f in P['frases']:
    for tk in f.split(): vis.append(tk)
    fin.add(len(vis))
assert len(vis) == N, f'{K}: frases {len(vis)} vs voz {N}: ' + str([(i, a, W[i]['t']) for i, a in enumerate(vis) if i < N and norm(a) != norm(W[i]['t'])][:6])
for i, a in enumerate(vis):
    if norm(a) != norm(W[i]['t']) and norm(a) not in P.get('oido_distinto', []): sys.exit(f'✗ {K} palabra {i}: guion "{a}" vs voz "{W[i]["t"]}"')
_C = [c for c in json.load(open(f'{proy}/corte/caras.json'))['f'] if len(c) >= 5]
CARA_Y = P.get('caraY', round(st.median((c[2] + c[4]) / 2 for c in _C) / 1920, 3))   # altura objetivo = mediana real: el ajuste por toma es chico
inis = [idx(e['desde']) for e in P['escenas']]; assert inis == sorted(inis) and inis[0] == 0, inis
# un cambio de escena pegado a un corte (< 0.3 s después) arranca EN el corte: si no, se asoman 1–7 cuadros de la toma siguiente
for i0 in inis[1:]:
    c = next((c for c in CR if 0 < W[i0]['a'] - c < .3), None)
    if c is not None: W[i0]['a'] = round(c + .001, 3)
json.dump(W, open(f'{proy}/voz/palabras.json', 'w'), ensure_ascii=False, indent=1)
# Subtítulos de 2–4 palabras en una sola línea, al ritmo de la voz. Corte óptimo por frase: pocos trozos, ≤ 4 palabras
# y ≤ 26 letras, de preferencia tras una coma/punto, nunca dejando colgada una palabra débil ni una palabra sola
DEBIL = {'de', 'la', 'el', 'los', 'las', 'un', 'una', 'a', 'en', 'y', 'que', 'mi', 'tu', 'su', 'por', 'para', 'con', 'se', 'lo', 'del', 'al', 'me', 'te', 'sin', 'ni', 'o', 'le', 'les', 'nos', 'muy', 'si', 'solo', 'este', 'esta', 'ese', 'esa', 'mis', 'tus', 'sus', 'cada'}
def trozos(tk):
    if not tk: return []
    v = [t.split('|', 1)[1] for t in tk]
    if not any(v): return [tk]   # oculto: un solo grupo
    n = len(tk); best = [0] + [None] * n; cut = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(max(0, j - 4), j):
            if best[i] is None: continue
            txt = ' '.join(v[i:j]); s_ = j - i
            if s_ > 1 and len(txt) > 26: continue
            c = 1 + (1.3 if s_ == 1 and n > 1 else 0)
            if j < n:
                if v[j - 1].lower().strip(',.;:?!…«»¿¡') in DEBIL: c += 1.2   # con acento: «mí» no es débil, «mi» sí
                if v[j - 1][-1:] in ',.;:?!…»': c -= .5
            if best[j] is None or best[i] + c < best[j]: best[j], cut[j] = best[i] + c, i
    out, j = [], n
    while j > 0: out.append(tk[cut[j]:j]); j = cut[j]
    return out[::-1]
esc_out, cortes = [], []; ultimo_visual = None; sfx = []
SFX = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'estilo-cine', 'sfx', 'whoosh_rapido.mp3'))
for k, e in enumerate(P['escenas']):
    i0, i1 = inis[k], inis[k + 1] if k + 1 < len(inis) else N
    y = e.get('y', P.get('y', .715)); ocultos = set()
    for a, b in e.get('ocultar', []): ocultos |= set(range(idx(a), idx(b) + 1))
    if e.get('sinSub'): ocultos |= set(range(i0, i1))
    grupos, cur, estado = [], [], None
    def cierra():
        global cur
        for ch in trozos(cur): grupos.append({'y': y, 'frase': True, 'lineas': [' '.join(ch)], 'resaltar': P.get('resaltar', [])})
        cur = []
    for i in range(i0, i1):
        oc = i in ocultos
        if estado is not None and oc != estado: cierra()
        estado = oc; cur.append(W[i]['t'] + '|' + ('' if oc else vis[i]))
        if i + 1 in fin: cierra(); estado = None
    cierra()
    x = {kk: res(v) for kk, v in e.items() if kk not in ('desde', 'ocultar', 'sinSub', 'y')}
    x.setdefault('visual', 'persona'); x.setdefault('tema', 'oscuro')
    if x['visual'] == 'persona': x.setdefault('caraY', CARA_Y)   # un solo encuadre por video: la cara no brinca entre escenas
    x['textoTema'] = 'oscuro'; x['grupos'] = grupos
    if x['visual'] in ('pizarra', 'editorial', 'pantalla'): x.setdefault('vig', .06)
    firma = (x['visual'], x.get('pantalla', {}).get('fondo') if isinstance(x.get('pantalla'), dict) else None)
    if k > 0 and x['visual'] in ('persona', 'split', 'franja'): cortes.append(round(W[i0]['a'], 3))
    if k > 0 and firma != ultimo_visual: sfx.append({'f': SFX, 'en': round(W[i0]['a'] + .02, 3), 'pico': .3, 'vol': .16})
    ultimo_visual = firma; esc_out.append(x)
# caras por pieza
C = json.load(open(f'{proy}/corte/caras.json'))['f']; lim = [0] + CR + [W[-1]['b'] + 2]; caras = []; prev = None
for a, b in zip(lim, lim[1:]):
    f = [c for c in C if a <= c[0] < b and len(c) >= 5]
    if len(f) >= 3:
        prev = {'ini': a, 'fin': b, 'cx': round(st.median((c[1] + c[3]) / 2 for c in f), 1), 'cy': round(st.median((c[2] + c[4]) / 2 for c in f), 1), 'h': round(st.median(c[4] - c[2] for c in f), 1)}
    elif prev: prev = {**prev, 'ini': a, 'fin': b}
    if prev: caras.append(prev)
n = len([f for f in os.listdir(f'{proy}/cuadros') if f.endswith('.jpg')])
_kit = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config', 'kit.json')
KIT = json.load(open(_kit)) if os.path.exists(_kit) else {}   # nombre y @usuario de la persona (config/kit.json)
cfg = {'nombre': P.get('nombre', KIT.get('nombre', '')), 'handle': P.get('handle', KIT.get('handle', '')), 'fps': P.get('fps', '24/1'), 'cola': P.get('cola', .25), 'voz': 'corte/cam.mov', 'salida': f"salida/{P.get('archivo', K)}.mp4",
       'acento': P['acento'], 'acentoTexto': P.get('acentoTexto', '#fff'), 'limpio': P.get('limpio', {}), 'subtitulo': P['subtitulo'], 'caras': caras, 'caraH': P.get('caraH', round(1.22 * st.median(c['h'] for c in caras))),   # 22 % de margen: alcanza para llevar la cara al mismo lugar en cada corte
       'persona': {'cuadros': 'cuadros', 'mascaras': 'mascaras', 'crudos': 'cuadros', 'n': n, 'fondo': 'real', 'bajar': 0, 'zoomAlt': P.get('zoomAlt', 1.05)},
       'cortes': sorted(cortes + [c for c in CR if all(abs(c - x) > .3 for x in cortes)]), 'marcas': {'impacto': -9, 'tap': -9}, 'sfx_auto': False, 'sfx': sfx, 'escenas': esc_out}
if P.get('fuenteGrande'): cfg['fuenteGrande'] = P['fuenteGrande']
json.dump(cfg, open(f'{proy}/cine.json', 'w'), ensure_ascii=False, indent=1)
print(f"✓ {K}: {len(esc_out)} escenas, {sum(len(e['grupos']) for e in esc_out)} frases, {W[-1]['b']:.1f}s; caras h {[int(c['h']) for c in caras]}")
