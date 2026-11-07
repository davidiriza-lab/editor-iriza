"""Verifica en el audio que una palabra empieza donde dice voz/palabras.json: transcribe [a-0.05, a+0.6] y [a-0.4, a].
Uso: .venv/bin/python proyectos/<proyecto>/verificar_anclas.py <clave> palabra[#n] ..."""
import sys, json, re, subprocess, tempfile, os, unicodedata, mlx_whisper
B = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))   # carpeta del proyecto (copia de esta plantilla); correr desde la raíz del repo
K = sys.argv[1]; P = f'{B}/{K}'; W = json.load(open(f'{P}/voz/palabras.json')); tmp = tempfile.mkdtemp()
def norm(x):
    x = unicodedata.normalize('NFD', x.lower()); x = ''.join(c for c in x if unicodedata.category(c) != 'Mn'); return re.sub(r'[^a-z0-9ñ]', '', x)
def tx(a, d):
    w = os.path.join(tmp, 'c.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{max(0, a):.3f}', '-t', f'{d:.3f}', '-i', f'{P}/corte/cam.mov', '-vn', '-ac', '1', '-ar', '16000', '-af', 'adelay=300,apad=pad_dur=0.3', w], check=True)
    return mlx_whisper.transcribe(w, path_or_hf_repo='mlx-community/whisper-large-v3-turbo', language='es', condition_on_previous_text=False)['text'].strip()
for q in sys.argv[2:]:
    pal, n = (q.split('#') + ['1'])[:2]; c = 0
    for i, w in enumerate(W):
        if norm(w['t']) == norm(pal):
            c += 1
            if c == int(n): print(f"{q:12s} a={w['a']:6.2f}  desde: «{tx(w['a'] - .05, .6)}»   antes: «{tx(w['a'] - .4, .4)}»", flush=True); break
