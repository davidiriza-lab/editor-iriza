"""Render de video reacción (formato C8240): arriba el original, abajo la persona con filtro C8253.
Uso: .venv/bin/python estilo-cine/reac_render.py proyectos/reacciones/<n>.cfg.json
cfg: { camara, original, salida, intro:[a,b], arranque, corte (s del original), cabeza (fracción), abajo (fracción),
       top: {y0, y1} (filas del original a mostrar), alto_original: 1000 }
"""
import sys, os, json, subprocess, shutil

cfg = json.load(open(sys.argv[1]))
base = os.path.splitext(sys.argv[1])[0].replace('.cfg', '')
os.makedirs(base, exist_ok=True)
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEG = os.path.join(RAIZ, 'bin', 'segmentar')  # se compila con: swiftc -O estilo-cine/segmentar.swift -o bin/segmentar
PY = sys.executable
PIEL = os.path.join(RAIZ, 'estilo-cine', 'piel.py')
run = lambda *a, **k: subprocess.run(*a, check=True, **k)

HO = cfg.get('alto_original', 1000); HS = 1920 - HO
ia, ib = cfg["intro"]; ia = max(0, ia - .12); ib += .2; dI = ib - ia
A, C = cfg['arranque'], cfg['corte']
# recorte de la persona: todo el ancho, de un pelito arriba de la cabeza hasta debajo del celular
y0 = int(max(0, (cfg['cabeza'] - .012) * 3840)); y1 = int(min(3840, cfg['abajo'] * 3840)); y0 -= y0 % 2; y1 -= y1 % 2
ws = int(round(2160 * HS / (y1 - y0) / 2) * 2); ws = min(ws, 1080)
cam = os.path.join(base, 'cam.mov')
fc = (f"[0:v]trim={ia:.3f}:{ib:.3f},setpts=PTS-STARTPTS,fps=30,crop=2160:{y1 - y0}:0:{y0},scale={ws}:{HS}[v0];"
      f"[0:a]atrim={ia:.3f}:{ib:.3f},asetpts=PTS-STARTPTS[a0];"
      f"[0:v]trim={A:.3f}:{A + C:.3f},setpts=PTS-STARTPTS,fps=30,crop=2160:{y1 - y0}:0:{y0},scale={ws}:{HS}[v1];"
      f"[0:a]atrim={A:.3f}:{A + C:.3f},asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
run(['ffmpeg', '-v', 'error', '-y', '-i', cfg['camara'], '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '14',
     '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-c:a', 'pcm_s16le', cam])
for d in ['cuadros', 'mascaras', 'cuadros_pro']: shutil.rmtree(os.path.join(base, d), ignore_errors=True)
os.makedirs(os.path.join(base, 'cuadros')); os.makedirs(os.path.join(base, 'mascaras'))
mw, mh = ws // 2 - (ws // 2) % 2, HS // 2
p1 = subprocess.Popen([SEG, cam, str(mw), str(mh)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
run(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'gray', '-s', f'{mw}x{mh}', '-r', '30', '-i', '-', os.path.join(base, 'mascaras', '%05d.jpg')], stdin=p1.stdout)
run(['ffmpeg', '-v', 'error', '-y', '-i', cam, '-q:v', '2', os.path.join(base, 'cuadros', '%05d.jpg')])
run([PY, PIEL, base], stdout=subprocess.DEVNULL)

# original: zona elegida (cara + subtítulos), escalada a lo ancho del panel; si no cabe, se aleja con fondo desenfocado
T = cfg['top']; wo = cfg['W']; oy0, oy1 = T['y0'], T['y1']; oy1 -= (oy1 - oy0) % 2
hw = int(round(wo * HO / (oy1 - oy0) / 2) * 2); hw = min(hw, 1080)
dur = dI + C
lado_o = (f"split[o1][o2];[o1]scale=1080:{HO}:force_original_aspect_ratio=increase,crop=1080:{HO},gblur=sigma=30,eq=brightness=-0.06[of];"
          f"[o2]scale={hw}:{HO}[on];[of][on]overlay=(W-w)/2:0" if hw < 1080 else f"scale=1080:{HO}")
lado_s = (f"split[x][y];[x]scale=1080:{HS}:force_original_aspect_ratio=increase,crop=1080:{HS},gblur=sigma=32,eq=brightness=-0.06[fon];[fon][y]overlay=(W-w)/2:0,"
          if ws < 1080 else "")
fc = (f"[0:v]setsar=1,{lado_s}vignette=angle=PI/7,gblur=sigma=0.5,colorbalance=gm=-0.04:gs=-0.02:bm=0.02,eq=brightness=0.025,format=yuv420p,noise=c0s=6:c0f=t[sa];"
      f"[2:v]fps=30,trim=0:{C:.3f},setpts=PTS-STARTPTS,crop={wo}:{oy1 - oy0}:0:{oy0},{lado_o},setsar=1,tpad=start_duration={dI:.3f}:start_mode=clone[ov];"
      f"color=c=black:s=1080x1920:r=30:d={dur:.3f}[bg];[bg][ov]overlay=0:0[a1];[a1][sa]overlay=0:{HO}:shortest=1,format=yuv420p[v];"
      f"[1:a]atrim=0:{dI:.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-2,afade=t=out:st={dI - .1:.3f}:d=0.1[ai];"
      f"[2:a]atrim=0:{C:.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-2,afade=t=out:st={C - .1:.3f}:d=0.1[ao];"
      f"[ai][ao]concat=n=2:v=0:a=1,loudnorm=I=-14:TP=-1[a]")
run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', os.path.join(base, 'cuadros_pro', '%05d.jpg'), '-i', cam, '-i', cfg['original'],
     '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-t', f'{dur:.3f}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-maxrate', '16M',
     '-bufsize', '32M', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-map_chapters', '-1', '-map_metadata', '-1', '-movflags', '+faststart', cfg['salida']])
print(f"✓ {cfg['salida']}  ({dur:.1f} s · persona {ws}px de ancho · original {hw}px)")
