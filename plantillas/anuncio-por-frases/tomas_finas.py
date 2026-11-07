"""Mapa fino de tomas: parte cada crudo por silencios cortos y transcribe cada pedazo por separado (para elegir tramos de tomas.json).
Uso: .venv/bin/python proyectos/<proyecto>/tomas_finas.py [clip …]   (sin argumentos: todos los de crudos/)
→ <proyecto>/_tomas/<clip>/finas.json"""
import sys, os, json, subprocess, tempfile, wave
import numpy as np, mlx_whisper
B = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))   # carpeta del proyecto (copia de esta plantilla); correr desde la raíz del repo
_NOMBRES = os.path.join(B, 'nombres.txt')   # nombres propios que Whisper escribe mal, en una línea
PR = open(_NOMBRES).read().strip() if os.path.exists(_NOMBRES) else ''
D = f'{B}/crudos'   # crudos de cámara
CLIPS = sys.argv[1:] or sorted(os.path.splitext(x)[0] for x in os.listdir(D) if not x.startswith('.'))
def crudo(c): return next(f'{D}/{x}' for x in sorted(os.listdir(D)) if os.path.splitext(x)[0] == c)
MOD = 'mlx-community/whisper-large-v3-turbo'
tmp = tempfile.mkdtemp()
for c in CLIPS:
    w = os.path.join(tmp, c + '.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', crudo(c), '-vn', '-ac', '1', '-ar', '16000', w], check=True)
    x = np.frombuffer(wave.open(w).readframes(10 ** 9), np.int16).astype(float); h = 320
    e = np.array([20 * np.log10(np.sqrt((x[i:i + h] ** 2).mean()) / 32768 + 1e-9) for i in range(0, len(x) - h, h)])
    v = e > np.percentile(e, 92) - 17
    R, i = [], 0
    while i < len(v):
        if v[i]:
            j = fin = i
            while j < len(v) and (v[j] or j - fin < 9):   # une huecos < 0.18 s
                if v[j]: fin = j
                j += 1
            if fin - i >= 10: R.append((i * .02, (fin + 1) * .02))
            i = j
        else: i += 1
    out = []
    print('=====', c, flush=True)
    for a, b in R:
        seg = np.concatenate([np.zeros(4000), x[int(max(0, a - .05) * 16000):int((b + .08) * 16000)], np.zeros(4000)]).astype(np.int16)
        t = os.path.join(tmp, 't.wav'); f = wave.open(t, 'wb'); f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000); f.writeframes(seg.tobytes()); f.close()
        txt = mlx_whisper.transcribe(t, path_or_hf_repo=MOD, language='es', condition_on_previous_text=False, initial_prompt=PR or None)['text'].strip()
        db = float(np.percentile(e[int(a / .02):int(b / .02)], 90))
        out.append({'a': round(a, 2), 'b': round(b, 2), 'db': round(db, 1), 't': txt})
        print(f'{a:7.2f}-{b:7.2f} [{db:5.1f}] {txt}', flush=True)
    os.makedirs(f'{B}/_tomas/{c}', exist_ok=True)
    json.dump(out, open(f'{B}/_tomas/{c}/finas.json', 'w'), ensure_ascii=False, indent=0)
