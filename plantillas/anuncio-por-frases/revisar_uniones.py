"""Doble revisión: cada pieza exacta y cada unión con contexto, transcritas por separado.
Uso: .venv/bin/python proyectos/<proyecto>/revisar_uniones.py k1 k2 …"""
import sys, json, subprocess, tempfile, os, re
import mlx_whisper
B = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))   # carpeta del proyecto (copia de esta plantilla); correr desde la raíz del repo
_NOMBRES = os.path.join(B, 'nombres.txt')   # nombres propios que Whisper escribe mal, en una línea
PR = open(_NOMBRES).read().strip() if os.path.exists(_NOMBRES) else ''
MOD = 'mlx-community/whisper-large-v3-turbo'; tmp = tempfile.mkdtemp()
def tx(src, a, d):
    w = os.path.join(tmp, 'c.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{max(0, a):.3f}', '-t', f'{d:.3f}', '-i', src, '-vn', '-ac', '1', '-ar', '16000', '-af', 'adelay=250,apad=pad_dur=0.25', w], check=True)
    return mlx_whisper.transcribe(w, path_or_hf_repo=MOD, language='es', condition_on_previous_text=False, initial_prompt=PR or None)['text'].strip()
for k in sys.argv[1:]:
    p = f'{B}/{k}'; pz = json.load(open(f'{p}/corte/mapa.json'))['piezas']; cam = f'{p}/corte/cam.mov'
    print('=====', k); t = 0
    for i, (a, b) in enumerate(pz):
        d = b - a
        ex = tx(cam, t, d)
        un = tx(cam, t + d - 1.1, 2.2) if i < len(pz) - 1 else ''
        print(f'{i:2d} {t:6.2f} [{ex}]' + (f'  || unión: {un}' if un else ''), flush=True); t += d
