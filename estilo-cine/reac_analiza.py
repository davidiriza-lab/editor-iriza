"""Analiza una carpeta de video reacción: tu grabación (C82xx.MP4) + el/los video(s) original(es).
Uso: .venv/bin/python estilo-cine/reac_analiza.py "<carpeta>" <salida.json>
- Empareja por audio cuál original suena en tu grabación y en qué segundo arranca.
- Tu intro: lo que dices con tu voz (fuerte) en los segundos antes de que arranque el original.
- CTA del original: por audio (comenta / escribe / sígueme / link / DM / suscríbete...) y por imagen
  (cuadro congelado al final o cambio brusco de imagen con texto encima). Propone el punto de corte.
"""
import sys, os, glob, json, re, subprocess
import numpy as np, cv2
import mlx_whisper

carpeta, salida = sys.argv[1], sys.argv[2]
fs = [f for f in glob.glob(os.path.join(carpeta, '*')) if os.path.isfile(f) and not os.path.basename(f).startswith(('._', 'Video editado'))]
cam = [f for f in fs if re.match(r'C\d+\.MP4$', os.path.basename(f), re.I)][0]
origs = [f for f in fs if f != cam and f.lower().endswith(('.mp4', '.mov'))]

def audio(f, sr=16000):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'], capture_output=True).stdout, np.int16).astype(float)
def env(x):
    e = np.log(np.sqrt(np.convolve(x ** 2, np.ones(800) / 800, 'same'))[::160] + 1); return (e - e.mean()) / e.std()
def dur(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
def transcribe(x, off=0):
    tmp = '/tmp/_reac.wav'; import wave
    w = wave.open(tmp, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(x.astype(np.int16).tobytes()); w.close()
    r = mlx_whisper.transcribe(tmp, path_or_hf_repo='mlx-community/whisper-large-v3-turbo', language='es', word_timestamps=True, condition_on_previous_text=False)
    return [{'t': w['word'].strip(), 'a': round(w['start'] + off, 2), 'b': round(w['end'] + off, 2)} for s in r['segments'] for w in s['words']]

xc = audio(cam); ec = env(xc)
mejor = None
for o in origs:
    xo = audio(o); eo = env(xo); n = len(ec) + len(eo)
    c = np.fft.irfft(np.fft.rfft(ec, n) * np.conj(np.fft.rfft(eo, n)), n); i = int(np.argmax(c))
    lag = (i if i < n // 2 else i - n) / 100; score = c.max() / len(eo)
    if not mejor or score > mejor['score']: mejor = {'orig': o, 'lag': lag, 'score': round(float(score), 3), 'xo': xo}
o, lag, xo = mejor['orig'], mejor['lag'], mejor.pop('xo')

# ---- tu intro: tu voz (≥ 12 dB más fuerte que la bocina) en los 12 s previos al arranque del original
h = 160; ecdb = 20 * np.log10(np.array([np.sqrt((xc[i:i + h] ** 2).mean()) for i in range(0, len(xc) - h, h)]) / 32768 + 1e-9)
ini = max(0, lag - 12); seg = xc[int(ini * 16000):int(max(ini + .5, lag) * 16000)]
pal = transcribe(seg, ini) if len(seg) > 8000 else []
voz = [w for w in pal if np.percentile(ecdb[int(w['a'] * 100):max(int(w['a'] * 100) + 1, int(w['b'] * 100))], 90) > -32]
# quedarse con la última frase continua (huecos < 1.2 s)
intro = []
for w in reversed(voz):
    if intro and intro[0]['a'] - w['b'] > 1.2: break
    intro.insert(0, w)

# ---- CTA por audio en el original
po = transcribe(xo)
CTA = r'coment|escrib|s[ií]gue|s[ií]gueme|link|enlace|bio\b|biograf|\bdm\b|mensaje directo|suscr|desc[áa]rg|[úu]nete|reg[íi]str|guarda este|comparte|etiqueta|te lo (env|mand|pas)|te env[íi]o|deja (un|tu) coment'
cta_audio = None
texto = ' '.join(w['t'] for w in po)
for i, w in enumerate(po):
    frase = ' '.join(x['t'] for x in po[i:i + 6]).lower()
    if w['a'] > dur(o) * .45 and re.search(CTA, frase):
        # retroceder al inicio de la oración
        j = i
        while j > 0 and not re.search(r'[.?!]$', po[j - 1]['t']) and w['a'] - po[j - 1]['a'] < 4: j -= 1
        cta_audio = {'t': po[j]['a'], 'frase': ' '.join(x['t'] for x in po[j:j + 14])}; break

# ---- CTA por imagen: congelado al final / salto brusco
cap = cv2.VideoCapture(o); fps = cap.get(cv2.CAP_PROP_FPS); prev = None; d = []
while True:
    ok, f = cap.read()
    if not ok: break
    g = cv2.cvtColor(cv2.resize(f, (90, 160)), cv2.COLOR_BGR2GRAY).astype(float)
    d.append(0 if prev is None else np.abs(g - prev).mean()); prev = g
d = np.array(d); nfr = len(d)
from scipy.signal import medfilt
crudo = d.copy(); d = medfilt(d, 5)  # ignora destellos aislados
congelado = None
k = nfr - 1
while k > 0 and d[k] < .35: k -= 1
if (nfr - 1 - k) / fps > .5:   # desde aquí ya no se mueve; si entró con un salto brusco (CTA encima), cortar en ese salto
    j = max(range(max(0, k - 4), min(nfr, k + 2)), key=lambda q: crudo[q])
    if crudo[j] > 15: k = j
    congelado = {'cuadro': int(k), 't': round(k / fps, 2)}
cortes = [x for x in [cta_audio and cta_audio['t'], congelado and congelado['t']] if x]
corte = round(min(cortes), 2) if cortes else round(nfr / fps, 2)

res = {'carpeta': os.path.basename(carpeta.rstrip('/')), 'camara': cam, 'original': o, 'score': mejor['score'], 'arranque': lag,
       'intro': ' '.join(w['t'] for w in intro), 'intro_a': intro[0]['a'] if intro else None, 'intro_b': intro[-1]['b'] if intro else None,
       'dur_original': round(dur(o), 2), 'fps': fps, 'cta_audio': cta_audio, 'congelado': congelado, 'corte': corte, 'texto_original': texto}
json.dump(res, open(salida, 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'texto_original'}, ensure_ascii=False, indent=1))
