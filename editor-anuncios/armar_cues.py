"""Arma cues.js para editor-anuncios a partir de un plan anclado a palabras habladas.

Uso:  python3 armar_cues.py planes.json <clave> <carpeta_proyecto>

El plan de cada anuncio describe los gráficos con anclas de texto ("palabra", n-ésima
aparición) en vez de segundos: aquí se resuelven contra words_out.json (tiempos ya cortados)
y se escribe <carpeta_proyecto>/cues.js con la forma que lee overlay.html / render.mjs.
"""
import json, re, sys, unicodedata, os

planes = json.load(open(sys.argv[1]))
N = sys.argv[2]
plan = planes[N]
proj = os.path.abspath(sys.argv[3])
words = json.load(open(os.path.join(proj, 'words_out.json')))
edl = json.load(open(os.path.join(proj, 'edl.json')))
DUR = edl['duration']

def norm(t):
    t = unicodedata.normalize('NFD', t.lower())
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9ñ]', '', t)

def t_de(ancla):
    """'palabra' | 'palabra#2' | 'palabra+0.3' | número → segundo (inicio de la palabra)."""
    if isinstance(ancla, (int, float)): return float(ancla)
    m = re.match(r'^([^#+\-]+?)(?:#(\d+))?(?:([+-]\d*\.?\d+))?$', ancla.strip())
    pal, n, off = m.group(1), int(m.group(2) or 1), float(m.group(3) or 0)
    k = 0
    for w in words:
        if (norm(w['w']).startswith(norm(pal[:-1])) if pal.endswith('*') else norm(w['w']) == norm(pal)):
            k += 1
            if k == n: return round(w['s'] + off, 3)
    raise SystemExit(f'{N}: no encontré "{ancla}"')

def fin_de(ancla):
    """Fin de la palabra (para cerrar justo después de decirla)."""
    if isinstance(ancla, (int, float)): return float(ancla)
    m = re.match(r'^([^#+\-]+?)(?:#(\d+))?(?:([+-]\d*\.?\d+))?$', ancla.strip())
    pal, n, off = m.group(1), int(m.group(2) or 1), float(m.group(3) or 0)
    k = 0
    for w in words:
        if (norm(w['w']).startswith(norm(pal[:-1])) if pal.endswith('*') else norm(w['w']) == norm(pal)):
            k += 1
            if k == n: return round(w['e'] + off, 3)
    raise SystemExit(f'{N}: no encontré "{ancla}"')

cues = []
for c in plan['cues']:
    c = dict(c)
    c['start'] = max(0.0, t_de(c.pop('desde')))
    c['end'] = min(DUR, fin_de(c.pop('hasta'))) if 'hasta' in c else DUR
    # anclas internas
    for k in ('clickAt', 'arrowAt', 'subAt', 'pickAt', 'barsAt', 'noteAt', 'drawFrom', 'drawTo', 'labelAt', 'ghostAt'):
        if k in c and isinstance(c[k], str): c[k] = t_de(c[k])
    for lista in ('lines', 'items', 'chips', 'nodes', 'words', 'rows', 'blocks', 'cards', 'bars', 'arcs', 'icons', 'stamps'):
        for it in c.get(lista, []) or []:
            for k in ('at', 'checkAt', 'strikeAt'):
                if k in it and isinstance(it[k], str): it[k] = t_de(it[k])
            if 'until' in it and isinstance(it['until'], str): it['until'] = t_de(it['until'])
    for k in ('titleAt',):
        if k in c and isinstance(c[k], str): c[k] = t_de(c[k])
    if isinstance(c.get('bang'), dict) and isinstance(c['bang'].get('at'), str): c['bang']['at'] = t_de(c['bang']['at'])
    if isinstance(c.get('rotate'), dict):
        for k in ('at', 'until'):
            if isinstance(c['rotate'].get(k), str): c['rotate'][k] = t_de(c['rotate'][k])
    cues.append(c)

E = {
    'theme': plan.get('theme', 'palabras'),
    'camera': plan.get('camera', {'med': 0.21, 'close': 0.26, 'maxZ': 1.55, 'push': 0.04}),
    'subs': plan.get('subs', {}),
    'cues': cues,
    'sfx': plan.get('sfx', True),
}
if 'splits' in plan: E['splits'] = [t_de(x) for x in plan['splits']]
if 'flashes' in plan: E['flashes'] = [t_de(x) for x in plan['flashes']]
if 'transitions' in plan: E['transitions'] = plan['transitions']
if 'zooms' in plan: E['zooms'] = [[t_de(a), t_de(b), z0, z1] for a, b, z0, z1 in plan['zooms']]
if 'vf' in plan: E['vf'] = plan['vf']

out = 'window.EDIT = ' + json.dumps(E, ensure_ascii=False, indent=1) + ';\n'
open(os.path.join(proj, 'cues.js'), 'w').write(out)
print(f'{N}: {len(cues)} cues · {DUR:.1f}s · ' + ' · '.join(f"{c['type']}@{c['start']:.1f}-{c['end']:.1f}" for c in cues))
