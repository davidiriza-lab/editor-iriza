"""Auditoría de CORTES de una pieza, sobre el audio ya cortado. Funciona con cualquier receta de armado.

  .venv/bin/python estilo-cine/auditar_voz.py proyectos/<nombre> [--sin-transcribir] [--pausa 0.6]

Junta en el motor las reglas de corte que se corrigieron cuatro veces (4, 10, 11 y 12-nov-2026) y que vivían en recetas sueltas:
  · ARRANQUE: el video empieza cuando empieza la voz (sin cara esperando).
  · PAUSAS: ningún silencio de más de 0.6 s entre frases.
  · UNIONES (si hay corte/mapa.json): en cada unión de piezas no debe haber voz sonando: si la hay, una palabra quedó
    cortada o la pieza termina antes del silencio real.
  · TOMAS REPETIDAS: Whisper pega "seguramente es… Seguramente es porque" en una sola frase y no se ve en la transcripción.
    Aquí el audio se parte en ráfagas de voz, cada ráfaga se transcribe SOLA y se marca cuando una empieza igual que la
    anterior, o cuando una frase de 6+ palabras se dice dos veces (4 o 5 palabras iguales: solo aviso).
  · FINAL: no queda silencio colgando después de la última palabra (más allá de la cola).
Deja <proyecto>/revision/voz.json y una lista para leer: cada ráfaga con su texto (debe leerse como frase completa).
Sale con código 1 si hay errores. Lo llama estilo-cine/revisar.py.
"""
import json, os, re, shutil, subprocess, sys, tempfile, unicodedata, wave
import numpy as np

args = sys.argv[1:]
if not args or args[0].startswith('--'): sys.exit(__doc__)
proy = os.path.abspath(args[0]); P = lambda *f: os.path.join(proy, *f)
opt = lambda k, d=None: args[args.index(k) + 1] if k in args else d
PAUSA = float(opt('--pausa', .6)); TRANSCRIBIR = '--sin-transcribir' not in args
cfg = json.load(open(P('cine.json'))) if os.path.exists(P('cine.json')) else {}
fuente = P(cfg.get('voz') or 'corte/cam.mov')
if not os.path.exists(fuente): sys.exit(f'✗ no está el audio de la voz: {fuente}')
tmp = tempfile.mkdtemp(); wav = os.path.join(tmp, 'voz.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-i', fuente, '-vn', '-ac', '1', '-ar', '16000', wav], check=True)
w = wave.open(wav); SR = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; dur = len(x) / SR
PASO = .01; st = int(SR * PASO)
e = np.array([20 * np.log10(np.sqrt((x[i * st:(i + 1) * st] ** 2).mean()) + 1e-9) for i in range(len(x) // st)])
nivel = float(np.percentile(e, 90))                      # qué tan fuerte habla la persona
UMBRAL = max(-48.0, nivel - 26)                          # debajo de esto es silencio (relativo: sirve con voz baja o alta)
db = lambda a, b: float(e[max(0, int(a / PASO)):max(1, int(b / PASO))].max()) if b > a and int(a / PASO) < len(e) else -99.0

def rafagas(sil=.18, minimo=.2):
    idx = np.flatnonzero(e > UMBRAL)
    if not len(idx): return []
    segs, a, prev = [], idx[0], idx[0]
    for i in idx[1:]:
        if (i - prev) * PASO >= sil: segs.append((a, prev + 1)); a = i
        prev = i
    segs.append((a, prev + 1))
    return [(a * PASO, b * PASO) for a, b in segs if (b - a) * PASO >= minimo]

R = rafagas(); errores, avisos = [], []
if not R: sys.exit('✗ no se detectó voz en el audio')
seg = lambda t: f'{t:.2f} s'

# arranque y final
if R[0][0] > .25: errores.append(f'ARRANQUE: la voz empieza en {seg(R[0][0])}: hay {R[0][0]:.2f} s de cara esperando (el video arranca cuando empieza a hablar)')
cola = float(cfg.get('cola', .8))
if dur - R[-1][1] > cola + .6: avisos.append(f'FINAL: quedan {dur - R[-1][1]:.1f} s sin voz después de la última palabra ({seg(R[-1][1])})')
# pausas
for (a0, b0), (a1, b1) in zip(R, R[1:]):
    if a1 - b0 > PAUSA: errores.append(f'PAUSA de {a1 - b0:.2f} s entre {seg(b0)} y {seg(a1)} (máximo {PAUSA} s): silencio con la cara esperando')
# uniones de piezas
uniones = []
if os.path.exists(P('corte', 'mapa.json')):
    t = 0
    for a, b in json.load(open(P('corte', 'mapa.json'))).get('piezas', [])[:-1]:
        t += b - a; uniones.append(round(t, 3))
for u in uniones:
    antes, desp = db(u - .04, u), db(u, u + .04)
    if antes > UMBRAL + 8 and desp > UMBRAL + 8: errores.append(f'UNIÓN en {seg(u)}: hay voz sonando de los dos lados del corte ({antes:.0f}/{desp:.0f} dB): una palabra quedó cortada')
    elif antes > UMBRAL + 10: avisos.append(f'UNIÓN en {seg(u)}: la pieza termina con voz sonando ({antes:.0f} dB): revisa que la última sílaba esté completa')
    elif desp > UMBRAL + 10: avisos.append(f'UNIÓN en {seg(u)}: la pieza siguiente empieza con voz ya sonando ({desp:.0f} dB): revisa el arranque de la palabra')

# tomas repetidas: cada ráfaga transcrita sola
norm = lambda s: [p for p in re.sub(r'[^a-z0-9ñ ]', ' ', unicodedata.normalize('NFKD', s.lower().replace('ñ', '\x00')).encode('ascii', 'ignore').decode().replace('\x00', 'ñ')).split() if p]
textos = [''] * len(R)
if TRANSCRIBIR:
    cli = shutil.which('whisper-cli'); modelo = os.path.expanduser('~/.cache/whisper-cpp/ggml-large-v3-turbo.bin')
    idioma = os.environ.get('IDIOMA', 'es')
    if cli and os.path.exists(modelo):
        def oye(a, b):
            f = os.path.join(tmp, 'r.wav')
            subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-i', wav, '-ss', f'{max(0, a - .05):.3f}', '-to', f'{b + .05:.3f}', f], check=True)
            return ' '.join(subprocess.run(['nice', cli, '-m', modelo, '-l', idioma, '-t', '4', '-nt', '-f', f], capture_output=True, text=True).stdout.split())
    else:
        try:
            import mlx_whisper
            def oye(a, b):
                return mlx_whisper.transcribe(x[int(max(0, a - .05) * SR):int((b + .05) * SR)], path_or_hf_repo=os.environ.get('WHISPER_MODELO', 'mlx-community/whisper-large-v3-turbo'), language=idioma, condition_on_previous_text=False)['text'].strip()
        except Exception:
            oye = None; avisos.append('sin whisper (whisper-cli ni mlx_whisper): no se revisaron tomas repetidas')
    if oye:
        textos = [oye(a, b) for a, b in R]
        for k in range(1, len(R)):
            n0, n1 = norm(textos[k - 1]), norm(textos[k])
            if not n0 or not n1: continue
            if n1[:len(n0)] == n0 or (len(n0) <= 3 and n0[0] == n1[0] and len(n0[0]) > 2) or (len(n0) >= 2 and n0[-2:] == n1[:2]):
                errores.append(f'TOMA REPETIDA: «{textos[k - 1]}» ({seg(R[k - 1][0])}) y enseguida «{textos[k][:60]}» ({seg(R[k][0])}): quedó un arranque fallido')
        # una frase larga dicha dos veces es una toma repetida; cuatro o cinco palabras iguales puede ser forma de hablar
        todo = [(p, k) for k, t in enumerate(textos) for p in norm(t)]
        for largo, lista, que in ((6, errores, 'FRASE DICHA DOS VECES'), (4, avisos, 'Palabras repetidas (¿toma repetida o forma de hablar?)')):
            vistos = {}; ya = False
            for i in range(len(todo) - largo + 1):
                g = tuple(p for p, _ in todo[i:i + largo])
                if g in vistos and i - vistos[g] >= largo:
                    if not (largo == 4 and any('DOS VECES' in x for x in errores)): lista.append(f'{que}: «{" ".join(g)}» en {seg(R[todo[vistos[g]][1]][0])} y en {seg(R[todo[i][1]][0])}')
                    ya = True; break
                vistos.setdefault(g, i)
shutil.rmtree(tmp, ignore_errors=True)

os.makedirs(P('revision'), exist_ok=True)
json.dump({'ok': not errores, 'errores': errores, 'avisos': avisos, 'nivel_voz_db': round(nivel, 1), 'umbral_silencio_db': round(UMBRAL, 1), 'uniones': uniones,
           'rafagas': [{'a': round(a, 2), 'b': round(b, 2), 'texto': t} for (a, b), t in zip(R, textos)]}, open(P('revision', 'voz.json'), 'w'), ensure_ascii=False, indent=1)
print(f'Cortes de {os.path.basename(proy)}: {dur:.1f} s · {len(R)} ráfagas de voz · {len(uniones)} uniones · voz a {nivel:.0f} dB, silencio bajo {UMBRAL:.0f} dB')
if TRANSCRIBIR and any(textos):
    print('  Cada ráfaga sola (debe leerse como frase completa, sin empezar ni terminar a media idea):')
    for (a, b), t in zip(R, textos): print(f'   [{a:6.2f}–{b:6.2f}] {t}')
for x_ in errores: print('  ✗', x_)
for x_ in avisos: print('  ⚠', x_)
print('✓ cortes sin errores' if not errores else f'✗ {len(errores)} error(es) de corte')
sys.exit(1 if errores else 0)
