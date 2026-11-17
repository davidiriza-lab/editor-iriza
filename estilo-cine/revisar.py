"""Revisión ÚNICA de una pieza de estilo-cine: un comando, un veredicto. Sin ✓ no se entrega.

  .venv/bin/python estilo-cine/revisar.py proyectos/<nombre> [--paso 0.2] [--final "<video.mp4>"] [--solo-final]
                                                              [--rapido] (sin transcribir las ráfagas) [--sin-cortes]

Qué revisa (y deja en <proyecto>/revision/):
  1. cine.json válido (claves, opciones, fps, cuadros, palabras contra la voz): lo mismo que `render.mjs --validar`.
  2. TEXTO, midiendo lo que de verdad se dibuja (render.mjs --capas: cada instante con y sin texto; la diferencia es el
     texto visible, así que lo que va detrás de la persona no cuenta y no hace falta leer letras):
       · texto encima de la cara          · texto fuera de la zona segura de Instagram
       · texto cortado por el borde       · texto que casi no contrasta con su fondo
       · grupo de texto que dura tan poco que no se alcanza a leer
  3. RITMO (avisos, no errores): tramos largos sin ningún cambio, animaciones sin sonido, piezas de una sola receta.
     Deja el guion visual (un cuadro por segundo) para verlo de un vistazo y para el agente `critico-video`.
  3b. CORTES (auditar_voz.py): arranque sin cara esperando, pausas de más de 0.6 s, voz sonando en las uniones y tomas
     repetidas (cada ráfaga de voz transcrita sola).
  4. VIDEO FINAL, si ya existe: contrato de entrega (estilo-cine/entrega.py), que no sea anterior al último cine.json,
     cuadros negros, destellos de un solo cuadro, imagen congelada y audio que satura.
Sale con código 1 si hay errores. Escribe revision/veredicto.json (lo lee quien entrega).
"""
import json, os, re, subprocess, sys, time
import numpy as np, cv2

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
args = sys.argv[1:]
if not args or args[0].startswith('--'): sys.exit(__doc__)
proy = os.path.abspath(args[0]); P = lambda *f: os.path.join(proy, *f)
opt = lambda k, d=None: args[args.index(k) + 1] if k in args else d
PASO = float(opt('--paso', .2)); SOLO_FINAL = '--solo-final' in args
cfg = json.load(open(P('cine.json')))
REV = P('revision'); os.makedirs(REV, exist_ok=True)
errores, avisos, notas = [], [], []
seg = lambda t: f'{t:.1f} s'

# ---------------------------------------------------------------- 1. cine.json
r = subprocess.run(['node', os.path.join(AQUI, 'render.mjs'), proy, '--validar'], capture_output=True, text=True)
sal = (r.stdout + r.stderr).strip()
if r.returncode:
    print(sal); print('\n✗ REVISIÓN DETENIDA: corrige el cine.json y vuelve a correrla.')
    json.dump({'ok': False, 'errores': [l.strip(' ·') for l in sal.splitlines() if l.strip().startswith('·')], 'avisos': [], 'cuando': time.strftime('%Y-%m-%d %H:%M')}, open(os.path.join(REV, 'veredicto.json'), 'w'), ensure_ascii=False, indent=1)
    sys.exit(1)
avisos += [l.strip()[2:] for l in sal.splitlines() if l.strip().startswith('⚠')]

# ---------------------------------------------------------------- 2. texto (capas con / sin)
def zona_segura():
    for f, k in ((os.path.join(RAIZ, 'config', 'kit.json'), 'zona_segura_instagram'),):
        if os.path.exists(f):
            z = json.load(open(f)).get(k)
            if z: return z
    z = json.load(open(os.path.join(AQUI, 'zona_segura.json')))
    return {'arriba': z['arriba'][3], 'abajo': z['abajo'][1], 'derecha_x': z['derecha'][0], 'derecha_desde_y': z['derecha'][1], 'margen_lateral': z['bordes_laterales_px']}

def rachas(idx, hueco=1):
    """índices consecutivos → [(primero, último), …]"""
    out = []
    for i in sorted(idx):
        if out and i - out[-1][1] <= hueco: out[-1][1] = i
        else: out.append([i, i])
    return out

TM = None
if not SOLO_FINAL:
    CAP = os.path.join(REV, 'capas')
    r = subprocess.run(['nice', '-n', '10', 'node', os.path.join(AQUI, 'render.mjs'), proy, '--capas', CAP, '--paso', str(PASO), '--perfil', 'redes'], capture_output=True, text=True)
    if r.returncode or not os.path.exists(os.path.join(CAP, 'tiempos.json')):
        print(r.stdout[-1500:], r.stderr[-1500:]); sys.exit('✗ no se pudieron sacar las capas de texto')
    TM = json.load(open(os.path.join(CAP, 'tiempos.json'))); T = TM['t']; W, H = TM['w'], TM['h']; n = len(T)
    # caras sobre la capa SIN texto (Vision): la cara real en pantalla, ya con el encuadre y el zoom del motor
    CARAS = [None] * n
    herr = os.path.join(RAIZ, 'editor-testimoniales', 'editor', 'bin', 'caras')
    if os.path.exists(herr):
        v = os.path.join(CAP, 'sin.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-framerate', '5', '-i', os.path.join(CAP, 'sin', '%05d.jpg'), '-c:v', 'libx264', '-crf', '16', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', v], check=True)
        subprocess.run([herr, v, os.path.join(CAP, 'caras.json')], check=True, capture_output=True)
        for k, c in enumerate(json.load(open(os.path.join(CAP, 'caras.json')))['f'][:n]):
            if len(c) >= 5 and c[1] >= 0 and c[4] - c[2] >= 90: CARAS[k] = c[1:5]
        os.remove(v)
    else:
        avisos.append('falta bin/caras (./instalar.sh): no se revisó texto sobre la cara')
    ZS = zona_segura() if (W, H) == (1080, 1920) else None
    fuera = np.zeros((H, W), bool)
    if ZS:
        TOL = 30                             # margen: al animarse las palabras entran unos px más abajo y la sombra se sale un poco
        fuera[:ZS['arriba'] - TOL] = True; fuera[ZS['abajo'] + TOL:] = True; fuera[ZS['derecha_desde_y']:, ZS['derecha_x'] + TOL:] = True
        fuera[:, :max(0, ZS['margen_lateral'] - TOL)] = True; fuera[:, W - max(0, ZS['margen_lateral'] - TOL):] = True
    borde = np.zeros((H, W), bool); borde[:3] = borde[-3:] = True; borde[:, :3] = borde[:, -3:] = True
    nuc = np.ones((3, 3), np.uint8)
    M = []                                   # por instante: medidas
    marcas = {}                              # instante → (motivo, máscara reducida) para la hoja
    for k in range(n):
        a = cv2.imread(os.path.join(CAP, 'con', f'{k + 1:05d}.jpg')); b = cv2.imread(os.path.join(CAP, 'sin', f'{k + 1:05d}.jpg'))
        d = np.abs(a.astype(np.int16) - b.astype(np.int16)).max(axis=2)
        m = cv2.morphologyEx((d > 36).astype(np.uint8), cv2.MORPH_OPEN, nuc).astype(bool)
        px = int(m.sum()); med = {'px': px, 'cara': 0.0, 'fuera': 0, 'borde': 0, 'contraste': 255.0}
        if px > 150:
            med['contraste'] = float(np.percentile(d[m], 75))
            med['fuera'] = int((m & fuera).sum()); med['borde'] = int((m & borde).sum())
            c = CARAS[k]
            if c:
                x0, y0, x1, y1 = c; wc, hc = x1 - x0, y1 - y0
                X0, X1, Y0, Y1 = int(max(0, x0 - .06 * wc)), int(min(W, x1 + .06 * wc)), int(max(0, y0 - .12 * hc)), int(min(H, y1 + .06 * hc))
                med['cara'] = float(m[Y0:Y1, X0:X1].sum()) / max(1, (Y1 - Y0) * (X1 - X0))
        M.append(med)
    G = TM['grupos']
    def de_quien(t):
        g = [x for x in G if x['ini'] - .01 <= t < x['fin'] + .01 and not x['detras']] or [x for x in G if x['ini'] - .01 <= t < x['fin'] + .01]
        e = next((x for x in TM['escenas'] if x['ini'] - .01 <= t < x['fin'] + .01), TM['escenas'][-1])
        return f"escena {e['i']} ({e['visual']})" + (f" «{g[0]['texto'][:48]}»" if g else '')
    def reporta(cond, motivo, texto, minimo=2, grave=True):
        idx = [k for k in range(n) if cond(M[k])]
        for a, b in rachas(idx):
            if b - a + 1 < minimo: continue
            peor = max(range(a, b + 1), key=lambda k: texto[1](M[k]))
            (errores if grave else avisos).append(f"{motivo} de {seg(T[a])} a {seg(T[b])} · {de_quien(T[peor])} · {texto[0](M[peor])}")
            marcas[peor] = motivo
    reporta(lambda m: m['cara'] > .02, 'TEXTO ENCIMA DE LA CARA', (lambda m: f"tapa {m['cara'] * 100:.0f} % de la cara", lambda m: m['cara']))
    if ZS:
        reporta(lambda m: m['fuera'] > 600, 'TEXTO FUERA DE LA ZONA SEGURA de Instagram', (lambda m: f"{m['fuera']} px de texto donde lo tapa la interfaz", lambda m: m['fuera']))
    # aviso y no error: una palabra gigante detrás de la persona puede salirse del cuadro a propósito; se decide viendo la hoja
    reporta(lambda m: m['borde'] > 25, 'Texto cortado por el borde del cuadro', (lambda m: f"{m['borde']} px tocan la orilla", lambda m: m['borde']), grave=False)
    reporta(lambda m: m['px'] > 1500 and m['contraste'] < 60, 'Texto con poco contraste contra su fondo', (lambda m: f"diferencia de {m['contraste']:.0f} sobre 255", lambda m: -m['contraste']), minimo=4, grave=False)
    for g in G:
        if not g['texto'].strip(): continue
        if g['fin'] - g['ini'] < .28: avisos.append(f"el texto «{g['texto'][:48]}» (escena {g['escena']}, {seg(g['ini'])}) dura {g['fin'] - g['ini']:.2f} s: no se alcanza a leer")
        ks = [k for k in range(n) if g['ini'] + .1 <= T[k] < g['fin']]
        if ks and not g['detras'] and max(M[k]['px'] for k in ks) < 150: errores.append(f"el texto «{g['texto'][:48]}» (escena {g['escena']}, {seg(g['ini'])}–{seg(g['fin'])}) NO SE VE en pantalla")
    # hoja de problemas: el cuadro con el texto, la cara (amarillo), la zona segura (cian) y el texto culpable (rojo)
    if marcas:
        tiles = []
        for k, motivo in sorted(marcas.items())[:12]:
            a = cv2.imread(os.path.join(CAP, 'con', f'{k + 1:05d}.jpg')); b = cv2.imread(os.path.join(CAP, 'sin', f'{k + 1:05d}.jpg'))
            m = (np.abs(a.astype(np.int16) - b.astype(np.int16)).max(axis=2) > 36)
            culp = m & (fuera | borde) if 'CARA' not in motivo else m
            a[culp] = (a[culp] * .35 + np.array([0, 0, 255]) * .65).astype(np.uint8)
            if ZS: cv2.rectangle(a, (ZS['margen_lateral'], ZS['arriba']), (W - ZS['margen_lateral'], ZS['abajo']), (255, 255, 0), 3); cv2.line(a, (ZS['derecha_x'], ZS['derecha_desde_y']), (ZS['derecha_x'], ZS['abajo']), (255, 255, 0), 3)
            if CARAS[k]: cv2.rectangle(a, (int(CARAS[k][0]), int(CARAS[k][1])), (int(CARAS[k][2]), int(CARAS[k][3])), (0, 255, 255), 4)
            t = cv2.resize(a, (360, 640)); cv2.rectangle(t, (0, 0), (360, 44), (0, 0, 0), -1)
            cv2.putText(t, f"{T[k]:.1f}s {motivo[:26]}", (6, 30), cv2.FONT_HERSHEY_SIMPLEX, .55, (255, 255, 255), 1, cv2.LINE_AA); tiles.append(t)
        while len(tiles) % 4: tiles.append(np.zeros_like(tiles[0]))
        cv2.imwrite(os.path.join(REV, 'texto_problemas.jpg'), np.vstack([np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]), [cv2.IMWRITE_JPEG_QUALITY, 86])
        notas.append('revision/texto_problemas.jpg: rojo = texto culpable · amarillo = cara · cian = zona segura')
    elif os.path.exists(os.path.join(REV, 'texto_problemas.jpg')): os.remove(os.path.join(REV, 'texto_problemas.jpg'))

    # ------------------------------------------------------------ 3. ritmo + guion visual
    E = TM['escenas']; dur = TM['dur']
    # cuánto cambia la imagen SIN texto entre instantes (reducida): un tramo donde nada cambia salvo la persona hablando
    chicos = [cv2.resize(cv2.imread(os.path.join(CAP, 'sin', f'{k + 1:05d}.jpg'), 0), (54, 96), interpolation=cv2.INTER_AREA).astype(np.float32) for k in range(n)]
    camb = [0.0] + [float(np.abs(chicos[k] - chicos[k - 1]).mean()) for k in range(1, n)]
    UMBRAL = 14.0                             # un corte, una transición o una capa grande mueven más que esto; hablar a cámara, no
    quietos, a = [], 0
    for k in range(1, n + 1):
        if k == n or camb[k] > UMBRAL:
            if T[min(k, n - 1)] - T[a] > 0: quietos.append((T[a], T[min(k, n - 1)]))
            a = k
    largo = max(quietos, key=lambda q: q[1] - q[0]) if quietos else (0, 0)
    sfx = len(cfg.get('sfx', [])) + (sum(1 for e in cfg['escenas'] if e.get('trans')) if cfg.get('sfx_auto') else 0)
    def cuenta(o, ks):
        if isinstance(o, dict): return sum((1 if k in ks else 0) + cuenta(v, ks) for k, v in o.items())
        if isinstance(o, list): return sum(cuenta(x, ks) for x in o)
        return 0
    animadas = sum(1 for e in cfg['escenas'] if e.get('trans') or e.get('visual', 'persona') != 'persona') + cuenta([{k: v for k, v in e.items() if k != 'grupos'} for e in cfg['escenas']], {'capas', 'imp', 'pant', 'cap', 'explica', 'clip', 'broll'})
    visuales = sorted({e['visual'] for e in E}); solo_persona = sum(e['fin'] - e['ini'] for e in E if e['visual'] == 'persona') / max(dur, .1)
    ritmo = {'duracion': round(dur, 1), 'escenas': len(E), 'segundos_por_escena': round(dur / len(E), 1), 'visuales': visuales, 'parte_solo_persona': round(solo_persona, 2),
             'tramo_mas_largo_sin_cambio': [round(largo[0], 1), round(largo[1], 1)], 'cambios_fuertes': sum(1 for c in camb if c > UMBRAL), 'animaciones': animadas, 'efectos_de_sonido': sfx,
             'musica': bool(cfg.get('musica', {}).get('archivo')), 'texto_detras_de_la_persona': sum(1 for g in G if g['detras'])}
    if largo[1] - largo[0] > 6:
        e = next((x for x in E if x['ini'] - .01 <= (largo[0] + largo[1]) / 2 < x['fin'] + .01), E[-1])
        avisos.append(f"RITMO: {largo[1] - largo[0]:.0f} s seguidos sin ningún cambio de imagen ({seg(largo[0])}–{seg(largo[1])}, escena {e['i']}: {e['visual']})")
    if animadas >= 3 and sfx == 0: avisos.append(f'RITMO: {animadas} animaciones o cortes y ningún efecto de sonido (cada animación lleva su sonido)')
    if not ritmo['musica']: avisos.append('sin música (solo se entrega así si la persona pidió "sin música")')
    # guion visual: un cuadro por segundo, con su segundo y su escena
    for f_ in os.listdir(REV):
        if f_.startswith('guion_visual_'): os.remove(os.path.join(REV, f_))
    sel = [min(range(n), key=lambda k: abs(T[k] - s)) for s in np.arange(.5, dur, 1.0)]
    tw, th, COL, FIL = 216, 384, 8, 3; hojas = []
    for h in range(0, len(sel), COL * FIL):
        hoja = np.full((FIL * (th + 26), COL * tw, 3), 16, np.uint8)
        for j, k in enumerate(sel[h:h + COL * FIL]):
            y, x = (j // COL) * (th + 26), (j % COL) * tw
            hoja[y:y + th, x:x + tw] = cv2.resize(cv2.imread(os.path.join(CAP, 'con', f'{k + 1:05d}.jpg')), (tw, th), interpolation=cv2.INTER_AREA)
            e = next((x_ for x_ in E if x_['ini'] - .01 <= T[k] < x_['fin'] + .01), E[-1])
            cv2.putText(hoja, f"{T[k]:.0f}s  esc {e['i']} {e['visual'][:9]}", (x + 4, y + th + 18), cv2.FONT_HERSHEY_SIMPLEX, .42, (0, 200, 255) if k in marcas else (225, 225, 225), 1, cv2.LINE_AA)
        ruta = os.path.join(REV, f'guion_visual_{len(hojas) + 1:02d}.jpg'); cv2.imwrite(ruta, hoja, [cv2.IMWRITE_JPEG_QUALITY, 84]); hojas.append(os.path.basename(ruta))
    notas.append(f"guion visual (un cuadro por segundo): revision/{', revision/'.join(hojas)}")
    json.dump({'ritmo': ritmo, 'escenas': E, 'instantes': [{'t': T[k], **{a_: (round(v, 3) if isinstance(v, float) else v) for a_, v in M[k].items()}, 'cambio': round(camb[k], 1)} for k in range(n)]}, open(os.path.join(REV, 'medidas.json'), 'w'), ensure_ascii=False)
    import shutil; shutil.rmtree(CAP, ignore_errors=True)      # las capas se regeneran en 30 s; no se guardan
else:
    ritmo = None

# ---------------------------------------------------------------- 3b. cortes (auditar_voz.py)
if not SOLO_FINAL and '--sin-cortes' not in args:
    r = subprocess.run([sys.executable, os.path.join(AQUI, 'auditar_voz.py'), proy] + (['--sin-transcribir'] if '--rapido' in args else []), capture_output=True, text=True)
    try:
        V = json.load(open(os.path.join(REV, 'voz.json')))
        errores += ['CORTES · ' + x for x in V['errores']]; avisos += ['CORTES · ' + x for x in V['avisos']]
        notas.append(f"cortes: {len(V['rafagas'])} ráfagas de voz" + ('' if '--rapido' in args else ', cada una transcrita sola en revision/voz.json (léelas: deben ser frases completas)'))
    except Exception:
        avisos.append('no se pudo auditar los cortes: ' + (r.stdout + r.stderr).strip()[-160:])

# ---------------------------------------------------------------- 4. video final
final = opt('--final')
if not final:
    cand = os.path.join(proy, cfg['salida']) if cfg.get('salida') else None
    if cand and os.path.exists(cand): final = cand
    elif os.path.isdir(P('salida')):
        mp4 = [os.path.join(P('salida'), f) for f in os.listdir(P('salida')) if f.endswith('.mp4')]
        final = max(mp4, key=os.path.getmtime) if mp4 else None
if final and os.path.exists(final):
    if os.path.getmtime(final) < os.path.getmtime(P('cine.json')) - 2: errores.append(f'el video final ({os.path.basename(final)}) es ANTERIOR al último cambio del cine.json: vuelve a renderizar antes de entregar')
    ent = os.path.join(AQUI, 'entrega.py')
    if os.path.exists(ent):
        r = subprocess.run([sys.executable, ent, 'verificar', final], capture_output=True, text=True); o = (r.stdout + r.stderr)
        for l in o.splitlines():
            l = l.strip()
            if l.startswith('✗'): errores.append('contrato de entrega: ' + l[1:].strip())
            elif l.startswith('⚠') or l.startswith('·'): avisos.append('contrato de entrega: ' + l[1:].strip())
        if r.returncode and not any('contrato de entrega' in e for e in errores): errores.append('contrato de entrega: no cumple (corre estilo-cine/entrega.py verificar para el detalle)')
    pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate,pix_fmt,color_space', '-of', 'default=nw=1:nk=1', final], capture_output=True, text=True).stdout.split()
    a_, b_ = pr[2].split('/') if len(pr) > 2 and '/' in pr[2] else ('30', '1'); FPSF = float(a_) / float(b_)
    if pr and (pr[0].startswith('yuvj') or (len(pr) > 1 and pr[1] not in ('bt709',))): avisos.append(f'el final está en un formato de color no estándar ({" / ".join(pr[:2])}): vuelve a renderizar con el motor actual (Rec.709)')
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', final, '-vf', 'scale=90:160:out_range=full,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    Gf = np.frombuffer(raw, np.uint8).reshape(-1, 160, 90).astype(np.float32); luz = Gf.mean(axis=(1, 2)); dd = np.r_[0, np.abs(np.diff(Gf, axis=0)).mean(axis=(1, 2))]
    try: fin_voz = json.load(open(P('voz', 'palabras.json')))[-1]['b']
    except Exception: fin_voz = len(Gf) / FPSF - 1
    FADE0 = max(0, fin_voz - .15); tt = lambda i: i / FPSF
    liso = (luz < 10) | (luz > 248)
    try: ESC = TM['escenas'] if TM else json.load(open(os.path.join(REV, 'medidas.json')))['escenas']
    except Exception: ESC = []
    # una pantalla negra o blanca DISEÑADA (golpe, cierre, pantalla de color) no es un error: solo cuenta donde debería verse video
    de_video = lambda t: not ESC or next((x for x in ESC if x['ini'] - .01 <= t < x['fin'] + .01), ESC[-1])['visual'] in ('persona', 'broll', 'clip', 'split')
    for a, b in rachas([i for i in range(len(Gf)) if liso[i] and tt(i) < FADE0]):
        if (b - a + 1) / FPSF > .5 and de_video(tt((a + b) // 2)): errores.append(f'video final: {(b - a + 1) / FPSF:.1f} s en negro o en blanco desde {seg(tt(a))}, donde debería verse video')
    dest = [i for i in range(1, len(Gf) - 1) if tt(i) < FADE0 and min(dd[i], dd[i + 1]) > 22 and np.abs(Gf[i + 1] - Gf[i - 1]).mean() < min(dd[i], dd[i + 1]) / 3]
    if dest: avisos.append(f"video final: {len(dest)} destello(s) de un solo cuadro en {', '.join(seg(tt(i)) for i in dest[:6])} (un cuadro distinto entre dos iguales: si no es un golpe a propósito, es una toma que se coló)")
    quieto = 0
    for i in range(1, len(Gf)):
        quieto = quieto + 1 if dd[i] < .12 and tt(i) < FADE0 else 0
        if quieto == int(.5 * FPSF) and de_video(tt(i)): errores.append(f'video final: imagen congelada más de 0.5 s en {seg(tt(i))}')
    o = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-nostdin', '-i', final, '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    mv = re.search(r'max_volume: (-?[\d.]+)', o)
    if mv and float(mv.group(1)) > -.3: errores.append(f'video final: el audio satura (pico {mv.group(1)} dBFS)')
elif SOLO_FINAL: errores.append('no hay video final que revisar')
else: notas.append('todavía no hay video final: al renderizar, corre de nuevo con --solo-final (10 s)')

# ---------------------------------------------------------------- veredicto
ok = not errores
json.dump({'ok': ok, 'errores': errores, 'avisos': avisos, 'ritmo': ritmo, 'final': final, 'cuando': time.strftime('%Y-%m-%d %H:%M')}, open(os.path.join(REV, 'veredicto.json'), 'w'), ensure_ascii=False, indent=1)
print(f"\nRevisión de {os.path.relpath(proy, RAIZ)}" + (f" · final: {os.path.basename(final)}" if final else ''))
if ritmo: print(f"  ritmo: {ritmo['duracion']} s · {ritmo['escenas']} escenas ({ritmo['segundos_por_escena']} s c/u) · {ritmo['animaciones']} animaciones · {ritmo['efectos_de_sonido']} efectos de sonido · tramo más largo sin cambio {ritmo['tramo_mas_largo_sin_cambio'][1] - ritmo['tramo_mas_largo_sin_cambio'][0]:.0f} s")
for e in errores: print('  ✗', e)
for a in avisos: print('  ⚠', a)
for x in notas: print('  ·', x)
print('\n✓ SIN ERRORES. Mira el guion visual y pásalo por el agente critico-video antes de enseñarlo.' if ok else f'\n✗ {len(errores)} ERROR(ES): no se entrega hasta corregirlos.')
sys.exit(0 if ok else 1)
