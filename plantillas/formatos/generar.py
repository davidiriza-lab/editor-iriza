"""Plantillas de Formatos/1023: por cada video saca fotogramas clave (cada toma + cada 0.5 s), hoja de cuadros,
paleta de colores y ESTILO.md.
Uso: <python con opencv> generar.py [n ...]      (sin argumentos: todos; con argumentos: solo esos, p. ej. 1p 13p pizarra)
Los videos horizontales (p. ej. el video que corre dentro de una laptop, formatos "Np") conservan su orientación.
"""
import sys
import cv2, numpy as np, json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(AQUI, 'formatos.json')))
F = D['familias']


TAM = (540, 960)
def analiza(ruta):
    global TAM
    cap = cv2.VideoCapture(ruta); fps = cap.get(cv2.CAP_PROP_FPS) or 30
    TAM = (960, 540) if cap.get(cv2.CAP_PROP_FRAME_WIDTH) > cap.get(cv2.CAP_PROP_FRAME_HEIGHT) else (540, 960)
    prev, dif, chicos, todos = None, [], [], []
    i = 0
    while True:
        ok, fr = cap.read()
        if not ok: break
        g = cv2.cvtColor(cv2.resize(fr, (54, 96)), cv2.COLOR_BGR2GRAY).astype(float)
        dif.append(0 if prev is None else float(np.abs(g - prev).mean())); prev = g
        if i % max(1, int(round(fps / 6))) == 0: todos.append((i, cv2.resize(fr, TAM)))
        i += 1
    n = i; dif = np.array(dif); med = float(np.median(dif)) if len(dif) else 0
    cortes = [k for k in range(1, len(dif)) if dif[k] > max(18, med * 4) and dif[k] >= dif[max(0, k - 2):k + 3].max()]
    return fps, n, cortes, todos


def elegir(todos, fps, cortes, n, maximo):
    # candidatos: mitad de cada toma + uno cada 0.5 s; luego se quitan los casi iguales
    bordes = [0] + cortes + [n]
    cand = {int((a + b) / 2) for a, b in zip(bordes, bordes[1:]) if b - a > 2} | set(range(0, n, int(fps / 2)))
    idx = sorted(cand); mapa = dict(todos)
    cerca = lambda k: min(mapa, key=lambda j: abs(j - k))
    fr = [(k, mapa[cerca(k)]) for k in idx]
    sel = []
    for k, im in fr:
        p = cv2.resize(im, (36, 64)).astype(float)
        if all(q is None or np.abs(p - q).mean() > 2.5 for _, _, q in sel): sel.append((k, im, p))
    if len(sel) < min(15, len(fr)):  # videos oscuros/minimal: completar con fotogramas repartidos en el tiempo
        ya = {k for k, _, _ in sel}; resto = [x for x in fr if x[0] not in ya]
        falta = min(15, len(fr)) - len(sel); paso = len(resto) / falta
        sel += [(resto[int(j * paso)][0], resto[int(j * paso)][1], None) for j in range(falta)]
        sel.sort(key=lambda x: x[0])
    if len(sel) > maximo:
        paso = len(sel) / maximo; sel = [sel[int(j * paso)] for j in range(maximo)]
    return [(k, im) for k, im, _ in sel]


def hoja(sel, fps, salida, cols=5):
    w, h = (216, 384) if TAM[1] > TAM[0] else (384, 216); ims = []
    for k, im in sel:
        t = cv2.resize(im, (w, h)); cv2.rectangle(t, (0, 0), (60, 20), (0, 0, 0), -1)
        cv2.putText(t, f'{k / fps:.1f}s', (4, 15), cv2.FONT_HERSHEY_SIMPLEX, .45, (255, 255, 255), 1, cv2.LINE_AA)
        ims.append(cv2.copyMakeBorder(t, 3, 3, 3, 3, cv2.BORDER_CONSTANT, value=(255, 255, 255)))
    while len(ims) % cols: ims.append(np.full_like(ims[0], 255))
    cv2.imwrite(salida, np.vstack([np.hstack(ims[r:r + cols]) for r in range(0, len(ims), cols)]), [cv2.IMWRITE_JPEG_QUALITY, 86])


def paleta(sel, salida, k=6):
    px = np.vstack([cv2.resize(im, (54, 96)).reshape(-1, 3) for _, im in sel]).astype(np.float32)
    _, lab, cen = cv2.kmeans(px, k, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, .5), 3, cv2.KMEANS_PP_CENTERS)
    cnt = np.bincount(lab.ravel(), minlength=k); orden = np.argsort(-cnt)
    hexes = ['#%02x%02x%02x' % tuple(int(c) for c in cen[i][::-1]) for i in orden]
    img = np.full((120, 720, 3), 255, np.uint8)
    for j, i in enumerate(orden):
        c = tuple(int(v) for v in cen[i]); cv2.rectangle(img, (j * 120, 0), (j * 120 + 118, 84), c, -1)
        cv2.putText(img, hexes[j], (j * 120 + 8, 108), cv2.FONT_HERSHEY_SIMPLEX, .5, (40, 40, 40), 1, cv2.LINE_AA)
    cv2.imwrite(salida, img); return hexes, [round(float(cnt[i] / cnt.sum()) * 100) for i in orden]


solo = set(sys.argv[1:])
resumen = []
for e in D['editores']:
    if solo and str(e['n']) not in solo: resumen.append(e); continue
    carpeta = os.path.join(AQUI, e.get('carpeta_nombre') or ('pizarra-pro' if e['n'] == 'pizarra' else f"editor-{e['n']:02d}"))
    os.makedirs(os.path.join(carpeta, 'cuadros'), exist_ok=True)
    fps, n, cortes, todos = analiza(e['archivo'])
    dur = n / fps
    todos_sel = elegir(todos, fps, cortes, n, 999)        # todos los distintos → carpeta
    for f in os.listdir(os.path.join(carpeta, 'cuadros')): os.remove(os.path.join(carpeta, 'cuadros', f))
    for k, im in todos_sel: cv2.imwrite(os.path.join(carpeta, 'cuadros', f'{k / fps:06.2f}s.jpg'), im, [cv2.IMWRITE_JPEG_QUALITY, 88])
    sel = elegir(todos, fps, cortes, n, 15)               # los 15 más representativos → hoja
    hoja(sel, fps, os.path.join(carpeta, 'hoja.jpg'))
    hexes, pct = paleta(todos_sel, os.path.join(carpeta, 'paleta.png'))
    fam = F[e['familia']]
    ritmo = len(cortes) / dur if dur else 0
    e.update(dur=round(dur, 1), cortes=len(cortes), ritmo=round(ritmo, 2), paleta=hexes, paleta_pct=pct, cuadros=len(todos_sel), carpeta=carpeta)
    hermanos = [x for x in fam['eds'] if x != e['n']]
    nombre_de = lambda x: 'Pizarra Pro' if x == 'pizarra' else (f"Editor {str(x)[:-1]} · pantalla" if str(x).endswith('p') else f'Editor {x}')
    md = f"""# {e['nombre']} · {e['apodo']}

Familia: **{fam['nombre']}**{' (misma familia que ' + ', '.join(nombre_de(x) for x in hermanos) + ')' if hermanos else ''}
Video de referencia: `{e['archivo']}`
Duración {e['dur']} s · {e['cortes']} cortes ({'muy rápido' if ritmo > 1 else 'rápido' if ritmo > .5 else 'tranquilo' if ritmo > .15 else 'casi un solo plano'}: {ritmo:.2f} cortes/s) · {e['cuadros']} fotogramas distintos en `cuadros/`

## Lo que se ve en este video
{e['detalle']}

## La plantilla (familia {fam['nombre']})
- **Idea:** {fam['idea']}
- **Texto:** {fam['texto']}
- **Animación y ritmo:** {fam['mov']}
- **Audio:** {fam['audio']}
- **Para qué te sirve:** {fam['para']}
- **Cómo lo hacemos con nuestro motor:** {fam['motor']}

## Paleta (medida de los fotogramas)
{' · '.join(f'`{h}` {p}%' for h, p in zip(hexes, pct))}

Archivos: `hoja.jpg` (15 fotogramas clave), `paleta.png`, `cuadros/` (todos los fotogramas distintos, {TAM[0]}×{TAM[1]}).
"""
    open(os.path.join(carpeta, 'ESTILO.md'), 'w').write(md)
    print(e['nombre'], e['dur'], 's', e['cortes'], 'cortes', e['cuadros'], 'cuadros', flush=True)
    resumen.append(e)

json.dump({'familias': F, 'editores': resumen}, open(os.path.join(AQUI, 'formatos.json'), 'w'), ensure_ascii=False, indent=1)
