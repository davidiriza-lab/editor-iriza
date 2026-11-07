"""Auditoría de cortes: por cada unión del corte (corte/mapa.json) mide
  · tipo: 'pausa' (misma toma, se quitó un silencio) o 'toma' (salta a otra toma)
  · audio: energía (dBFS) en los 30 ms antes y después de la unión → si hay voz, el corte muerde una palabra
  · cara: cuánto se mueve el centro y el tamaño de la cara entre el cuadro de antes y el de después (bin/caras)
  · imagen: diferencia media entre el cuadro de antes y el de después
  · piezas muy cortas (< 0.6 s) y desfase audio/video del archivo cortado
Uso (desde la raíz): .venv/bin/python proyectos/<proyecto>/auditar_cortes.py k1 k2 …"""
import sys, json, subprocess, wave, tempfile, os
import numpy as np
from PIL import Image
B = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))   # carpeta del proyecto (copia de esta plantilla); correr desde la raíz del repo
tmp = tempfile.mkdtemp()
def dur(f, s): return float(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', s, '-show_entries', 'stream=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.strip() or 0)
for k in sys.argv[1:]:
    P = f'{B}/{k}'; cam = f'{P}/corte/cam.mov'; pz = json.load(open(f'{P}/corte/mapa.json'))['piezas']
    tr = json.load(open(f'{B}/tomas.json'))[k]['tramos']
    w = os.path.join(tmp, 'a.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', cam, '-vn', '-ac', '1', '-ar', '16000', w], check=True)
    x = np.frombuffer(wave.open(w).readframes(10 ** 9), np.int16).astype(float)
    def db(a, b):
        s = x[max(0, int(a * 16000)):int(b * 16000)]; return 20 * np.log10(np.sqrt((s ** 2).mean()) / 32768 + 1e-9) if len(s) else -99
    C = {round(c[0], 2): c for c in json.load(open(f'{P}/corte/caras.json'))['f'] if len(c) >= 5}
    def cara(t):
        ks = sorted(C, key=lambda q: abs(q - t))[:1]; c = C[ks[0]] if ks and abs(ks[0] - t) < .2 else None
        return None if c is None else ((c[1] + c[3]) / 2, (c[2] + c[4]) / 2, c[4] - c[2])
    fps = 24000 / 1001; nq = len([f for f in os.listdir(f'{P}/cuadros') if f.endswith('.jpg')])
    def cuadro(t): i = min(nq, max(1, int(round(t * fps)) + 1)); return np.asarray(Image.open(f'{P}/cuadros/{i:05d}.jpg').convert('L').resize((135, 240)), float)
    def tramo_de(a): return next((i for i, t in enumerate(tr) if t[0] - .3 <= a <= t[1] + .3), -1)
    dv, da = dur(cam, 'v:0'), dur(cam, 'a:0')
    print(f'===== {k}: {len(pz)} piezas · video {dv:.3f} s · audio {da:.3f} s · desfase final {(da - dv) * 1000:+.0f} ms')
    t = 0; malos = 0
    for i, (a, b) in enumerate(pz):
        d = b - a; corto = d < .6
        if i < len(pz) - 1:
            a2 = pz[i + 1][0]; tipo = 'pausa' if tramo_de(a) == tramo_de(a2) and tramo_de(a) >= 0 else 'toma'
            u = t + d; e1, e2 = db(u - .03, u), db(u, u + .03)
            c1, c2 = cara(u - .05), cara(u + .05)
            mov = (np.hypot(c2[0] - c1[0], c2[1] - c1[1]), abs(c2[2] - c1[2]) / max(1, c1[2]) * 100) if c1 and c2 else (None, None)
            dif = np.abs(cuadro(u - .045) - cuadro(u + .045)).mean()
            alerta = []
            if max(e1, e2) > -40: alerta.append(f'VOZ en el corte ({e1:.0f}/{e2:.0f} dB)')
            if mov[0] is not None and (mov[0] > 25 or mov[1] > 6): alerta.append(f'cara salta {mov[0]:.0f}px / {mov[1]:.0f}%')
            if tipo == 'pausa': alerta.append(f'jump cut dentro de la toma (se quitaron {a2 - b:.2f} s)')
            if corto: alerta.append(f'pieza corta {d:.2f} s')
            if alerta: malos += 1
            print(f'{i:2d}→{i + 1:<2d} t={u:6.2f}  {tipo:5s} img {dif:5.1f}  ' + (' · '.join(alerta) if alerta else 'ok'))
        t += d
    print(f'  → {malos} uniones con algo que revisar')
