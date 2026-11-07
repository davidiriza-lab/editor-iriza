"""Afina los tiempos de voz/palabras.json: transcribe cada pieza del corte por separado (contexto corto = mejor
alineación) y lleva el inicio de cada palabra al arranque real de su sonido (energía en pasos de 10 ms).
Uso (desde la raíz del sistema): .venv/bin/python proyectos/<proyecto>/afinar_palabras.py <clave> [--escribir]
Sin --escribir solo reporta cuánto se movería cada palabra."""
import sys, os, json, re, subprocess, tempfile, wave, unicodedata
import numpy as np, mlx_whisper
B = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))   # carpeta del proyecto (copia de esta plantilla); correr desde la raíz del repo
_NOMBRES = os.path.join(B, 'nombres.txt')   # nombres propios que Whisper escribe mal, en una línea
PR = open(_NOMBRES).read().strip() if os.path.exists(_NOMBRES) else ''
K = sys.argv[1]; P = f'{B}/{K}'; MOD = 'mlx-community/whisper-large-v3-turbo'
def norm(x):
    x = unicodedata.normalize('NFD', x.lower()); x = ''.join(c for c in x if unicodedata.category(c) != 'Mn'); return re.sub(r'[^a-z0-9ñ]', '', x)
W = json.load(open(f'{P}/voz/palabras.json')); pz = json.load(open(f'{P}/corte/mapa.json'))['piezas']
tmp = tempfile.mkdtemp(); wav = os.path.join(tmp, 'a.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{P}/corte/cam.mov', '-vn', '-ac', '1', '-ar', '16000', wav], check=True)
x = np.frombuffer(wave.open(wav).readframes(10 ** 9), np.int16).astype(float); SR = 16000; h = 160
E = np.array([20 * np.log10(np.sqrt((x[i:i + h] ** 2).mean()) / 32768 + 1e-9) for i in range(0, len(x) - h, h)])  # 10 ms
nuevos, t0 = [], 0.0
for a, b in pz:
    d = b - a; seg = x[int(t0 * SR):int((t0 + d) * SR)]; PAD = .3
    s = np.concatenate([np.zeros(int(PAD * SR)), seg, np.zeros(int(PAD * SR))]).astype(np.int16)
    f = os.path.join(tmp, 'p.wav'); o = wave.open(f, 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR); o.writeframes(s.tobytes()); o.close()
    r = mlx_whisper.transcribe(f, path_or_hf_repo=MOD, language='es', word_timestamps=True, condition_on_previous_text=False, initial_prompt=PR or None)
    for sg in r['segments']:
        for w in sg['words']:
            nuevos.append({'t': w['word'].strip(), 'a': round(t0 + max(0, w['start'] - PAD), 3), 'b': round(t0 + min(d, w['end'] - PAD), 3)})
    t0 += d
# emparejar por secuencia de tokens normalizados
import difflib
A = [norm(w['t']) for w in W]; B = [norm(w['t']) for w in nuevos]
sm = difflib.SequenceMatcher(a=A, b=B, autojunk=False); movs = []; sin = 0
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == 'equal':
        for i, j in zip(range(i1, i2), range(j1, j2)):
            na, nb = nuevos[j]['a'], nuevos[j]['b']
            # arranque real: dentro de ±0.12 s del inicio estimado, el primer cuadro de 10 ms que sube de −45 dB tras un valle
            k0 = int(na * 100); lo, hi = max(0, k0 - 12), min(len(E) - 1, k0 + 12); seg = E[lo:hi]
            if len(seg):
                v = lo + int(np.argmin(seg[:max(1, k0 - lo + 4)]))  # valle antes (o justo en) el inicio estimado
                sube = next((k for k in range(v, hi) if E[k] > -45), None)
                if sube is not None and E[v] < -42: na = round(sube / 100, 3)
            movs.append((i, W[i]['t'], W[i]['a'], na)); W[i]['a'], W[i]['b'] = na, max(na + .06, nb)
    else: sin += i2 - i1
grandes = [m for m in movs if abs(m[3] - m[2]) >= .12]
print(f'{K}: {len(movs)} palabras emparejadas, {sin} sin emparejar; {len(grandes)} se mueven ≥ 0.12 s')
for i, t, a0, a1 in grandes: print(f'  {i:3d} {t:16s} {a0:6.2f} → {a1:6.2f} ({a1 - a0:+.2f})')
if '--escribir' in sys.argv:
    json.dump(W, open(f'{P}/voz/palabras.json', 'w'), ensure_ascii=False, indent=1); print('✓ escrito voz/palabras.json')
