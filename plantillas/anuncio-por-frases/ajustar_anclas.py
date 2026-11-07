"""Ajusta en voz/palabras.json el inicio de cada palabra que se usa como ancla en planes.py (textos, escenas, sellos):
avanza una ventana de 40 en 40 ms desde 0.15 s antes del inicio estimado y fija el inicio en el primer punto donde el audio
ya empieza con esa palabra (transcribiendo [t, t+0.7]). Así el texto entra cuando la persona la dice, no 0.3 s antes ni después.
Uso: .venv/bin/python proyectos/<proyecto>/ajustar_anclas.py <clave>"""
import sys, os, json, re, subprocess, tempfile, unicodedata
import mlx_whisper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from planes import PLANES
B = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))   # carpeta del proyecto (copia de esta plantilla); correr desde la raíz del repo
K = sys.argv[1]; P = f'{B}/{K}'; W = json.load(open(f'{P}/voz/palabras.json')); tmp = tempfile.mkdtemp()
def norm(x):
    x = unicodedata.normalize('NFD', x.lower()); x = ''.join(c for c in x if unicodedata.category(c) != 'Mn'); return re.sub(r'[^a-z0-9ñ]', '', x)
def anclas(o, out):
    if isinstance(o, dict): [anclas(v, out) for v in o.values()]
    elif isinstance(o, list): [anclas(v, out) for v in o]
    elif isinstance(o, str) and o.startswith('@'):
        m = re.match(r'^@([^#+\-$]+?)(?:#(\d+))?(\$)?([+-]\d*\.?\d+)?$', o)
        if m and not re.match(r'^fin$', m.group(1)): out.add((norm(m.group(1)), int(m.group(2) or 1)))
    return out
def idx(pal, n):
    c = 0
    for i, w in enumerate(W):
        if norm(w['t']) == pal:
            c += 1
            if c == n: return i
def primera(a):
    w = os.path.join(tmp, 'c.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{max(0, a):.3f}', '-t', '0.7', '-i', f'{P}/corte/cam.mov', '-vn', '-ac', '1', '-ar', '16000', '-af', 'adelay=300,apad=pad_dur=0.3', w], check=True)
    t = mlx_whisper.transcribe(w, path_or_hf_repo='mlx-community/whisper-large-v3-turbo', language='es', condition_on_previous_text=False)['text']
    toks = [norm(x) for x in t.split() if norm(x)]; return toks[0] if toks else ''
cambios = []
for pal, n in sorted(anclas(PLANES[K], set()), key=lambda q: idx(*q) or 0):
    i = idx(pal, n)
    if i is None or i == 0 or len(pal) < 3: continue   # palabras de 1–2 letras no se distinguen en una ventana
    a0 = W[i]['a']; t = a0 - .15; hallado = None
    while t <= a0 + .6:
        p = primera(t)
        if p == pal or (len(pal) > 4 and p[:4] == pal[:4]): hallado = round(t + .02, 3); break
        t += .04
    if hallado is not None and abs(hallado - a0) >= .06:
        W[i]['a'] = hallado; W[i]['b'] = max(W[i]['b'], hallado + .1); cambios.append((i, W[i]['t'], a0, hallado))
    elif hallado is None: cambios.append((i, W[i]['t'], a0, None))
json.dump(W, open(f'{P}/voz/palabras.json', 'w'), ensure_ascii=False, indent=1)
print(f'{K}: {len(cambios)} anclas corregidas')
for i, t, a0, a1 in cambios: print(f'  {i:3d} {t:16s} {a0:6.2f} → ' + (f'{a1:6.2f} ({a1 - a0:+.2f})' if a1 is not None else 'no se encontró (se deja)'))
