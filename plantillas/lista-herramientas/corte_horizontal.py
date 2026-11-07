"""Corte de "Herramientas gratis": tomas horizontales 1080p → vertical 1080x1920, cuerpo completo, tú a ~30 % del ancho.
Cada tramo: (archivo, a, b, centro_x medido con Vision). El tramo "mudo" va en cámara lenta y luego congelado (sin voz).
Salida: corte/cam.mov (24000/1001, pcm) + corte/mapa.json
"""
import subprocess, json, os
B = '<tu carpeta de contenido>/Replica viral/Herramientas gratis/'
AQUI = os.path.dirname(os.path.abspath(__file__))
T = [  # archivo, a, b, centro x, tipo
    ('C3566', 42.86, 45.62, 1169, 'voz'),    # ideas de contenido
    ('C3566', 83.08, 87.34, 1103, 'voz'),    # clonarse (2ª vuelta)
    ('C3567', 40.44, 43.94, 1062, 'voz'),    # editar videos (2ª vuelta)
    ('C3567', 58.34, 62.28, 1059, 'voz'),    # carruseles
    ('C3567', 91.10, 95.12, 1051, 'voz'),    # páginas web
    ('C3567', 112.16, 115.58, 1046, 'voz'),  # agentes
    ('C3567', 133.76, 138.62, 1049, 'voz'),  # CTA 1
    ('C3567', 148.26, 151.12, 1045, 'voz'),  # CTA 2
]
CW, LENTO, CONGELA = 608, 2.0, 1.9
COLOR = 'colorbalance=rs=-0.08:rm=-0.10:rh=-0.06:bs=0.06:bm=0.10:bh=0.06,hue=s=0.88,eq=brightness=0.02'  # menos naranja
ins, fc, vs, as_, mapa, acc = [], '', [], [], [], 0.0
for i, (f, a, b, cx, tipo) in enumerate(T):
    ins += ['-i', B + f + '.MP4']
    x = int(min(1920 - CW, max(0, cx - .68 * CW))); x -= x % 2  # tú a la derecha: la lista va a la izquierda, donde señalas
    crop = f"{COLOR},crop={CW}:1080:{x}:0,scale=1080:1920:flags=lanczos,setsar=1"
    if tipo == 'voz':
        fc += f"[{i}:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=24000/1001,{crop}[v{i}];"
        fc += f"[{i}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.01,areverse,afade=t=in:d=0.02,areverse[a{i}];"
        d = b - a
    else:
        d = (b - a) * LENTO + CONGELA
        fc += (f"[{i}:v]trim={a}:{b},setpts={LENTO}*(PTS-STARTPTS),fps=24000/1001,{crop},"
               f"tpad=stop_mode=clone:stop_duration={CONGELA}[v{i}];")
        fc += f"anullsrc=r=48000:cl=stereo,atrim=0:{d:.4f}[a{i}];"
    mapa.append({'archivo': f, 'a': a, 'b': b, 'tipo': tipo, 'ini': round(acc, 3), 'fin': round(acc + d, 3), 'crop_x': x})
    acc += d
    vs.append(f'[v{i}][a{i}]')
fc += ''.join(vs) + f'concat=n={len(T)}:v=1:a=1[v][a]'
os.makedirs(os.path.join(AQUI, 'corte'), exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '14',
                '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'pcm_s16le', os.path.join(AQUI, 'corte', 'cam.mov')], check=True)
json.dump({'piezas': [[m['ini'], m['fin']] for m in mapa], 'tramos': mapa}, open(os.path.join(AQUI, 'corte', 'mapa.json'), 'w'), indent=1)
for m in mapa: print(m)
print('total', round(acc, 2))
