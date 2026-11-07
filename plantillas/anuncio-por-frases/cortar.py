"""Corta un anuncio (tramos [a, b] con margen o [a, b, 0] exactos) desde su clip SDR con metodo_corte.py y nivela la voz de cada pieza a la mediana.
Uso (desde la raíz del sistema): .venv/bin/python proyectos/<proyecto>/cortar.py <clave>"""
import sys, os, json, subprocess, wave
import numpy as np
B = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))   # carpeta del proyecto (copia de esta plantilla); correr desde la raíz del repo
K = sys.argv[1]; C = json.load(open(f'{B}/tomas.json'))[K]; P = f'{B}/{K}'
# clip de cámara: la versión Rec.709 de convertir_sdr.sh (_sdr/) si existe; si no, el crudo de crudos/ (video que ya es SDR)
_sdr = f"{B}/_sdr/{C['clip']}.mov"
CAM = _sdr if os.path.exists(_sdr) else next((f'{B}/crudos/{x}' for x in sorted(os.listdir(f'{B}/crudos')) if os.path.splitext(x)[0] == C['clip']), None)
if not CAM: sys.exit(f"✗ no encuentro el clip {C['clip']} en {B}/_sdr ni en {B}/crudos")
FPS = str(C.get('fps', '24'))   # fps nativo de la cámara (iPhone: 24, 30 o 60)
os.makedirs(f'{P}/corte', exist_ok=True)
MARGEN_A, MARGEN_B = .07, .12
# [a, b] lleva margen al silencio; [a, b, 0] es un corte exacto (p. ej. para quitar una palabra repetida pegada)
tr = [[round(max(0, t[0] - MARGEN_A), 3), round(t[1] + MARGEN_B, 3)] if len(t) == 2 else [t[0], t[1]] for t in C['tramos']]
# pausa 0.6: no se cortan las pausas naturales dentro de una frase (cada corte ahí es un jump cut);
# fps nativo + ajustar_cuadros: corte por número de cuadro, sin convertir a 23.976; audio y video miden lo mismo al unir piezas
json.dump({'camara': os.path.abspath(CAM), 'recorte': {'vertical': True}, 'tramos': tr,
           'pausa': .6, 'fps': FPS, 'ajustar_cuadros': True}, open(f'{P}/metodo.json', 'w'), indent=1)
# un "word" por tramo: las pausas internas las parte metodo_corte por energía real
json.dump([{'w': 'x', 's': a, 'e': b - .03} for a, b in tr], open(f'{P}/corte/words.json', 'w'))
subprocess.run(['.venv/bin/python', 'estilo-cine/metodo_corte.py', P], check=True)
# ---- voz pareja ----
cam = f'{P}/corte/cam.mov'; piezas = json.load(open(f'{P}/corte/mapa.json'))['piezas']
w = f'{P}/corte/_a.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', cam, '-vn', '-ac', '1', '-ar', '48000', '-c:a', 'pcm_s16le', w], check=True)
wf = wave.open(w); x = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(float)
def nivel(s):
    h = 480; e = np.array([np.sqrt((s[i:i + h] ** 2).mean()) for i in range(0, max(1, len(s) - h), h)]) + 1e-9
    return 20 * np.log10(np.percentile(e, 80) / 32768)
pos, lv, rangos = 0, [], []
for a, b in piezas:
    n = int((b - a) * 48000); rangos.append((pos, min(pos + n, len(x)))); lv.append(nivel(x[rangos[-1][0]:rangos[-1][1]])); pos += n
med = float(np.median(lv)); g = np.ones(len(x))
for (i0, i1), l in zip(rangos, lv): g[i0:i1] = 10 ** (np.clip(med - l, -5, 5) / 20)
k = np.ones(480) / 480; g = np.convolve(g, k, 'same')   # sin saltos: rampa de 10 ms
y = np.clip(x * g, -32768, 32767).astype(np.int16)
f = wave.open(w, 'wb'); f.setnchannels(1); f.setsampwidth(2); f.setframerate(48000); f.writeframes(y.tobytes()); f.close()
tmp = f'{P}/corte/_cam.mov'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', cam, '-i', w, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'pcm_s16le', '-shortest', tmp], check=True)
os.replace(tmp, cam); os.remove(w)
print(f'✓ {K}: {len(piezas)} piezas, {pos / 48000:.1f} s; niveles {min(lv):.1f}…{max(lv):.1f} dB → {med:.1f} dB')
