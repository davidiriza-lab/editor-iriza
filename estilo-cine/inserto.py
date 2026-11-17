"""Convierte un MP4 hecho con otra herramienta (HyperFrames, Remotion, Blender, After Effects, un generador de video…)
en un inserto para cine.json: la carpeta de cuadros que leen los visuales `broll` (pantalla completa) y `clip`
(tarjeta con fondo difuminado).

Uso:  python3 estilo-cine/inserto.py <video.mp4> proyectos/<nombre> <nombre-del-inserto> [--desde 0] [--dur 3] [--modo broll|clip]

- Toma los fps y el lienzo del cine.json del proyecto (igual que render.mjs), así el inserto dura lo mismo que en el original.
- `broll` recorta a lo vertical (cubre el lienzo); `clip` conserva la proporción del video (tarjeta).
- Deja los cuadros en <proyecto>/insertos/<nombre>/00001.jpg… e imprime la escena lista para pegar en "escenas".
- El inserto se ve mientras dure su escena: si la escena es más larga que el clip, se queda en su último cuadro.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from fractions import Fraction
from comun import filtro_jpg

a = argparse.ArgumentParser()
a.add_argument("video"); a.add_argument("proyecto"); a.add_argument("nombre")
a.add_argument("--desde", type=float, default=0.0)
a.add_argument("--dur", type=float, default=None)
a.add_argument("--modo", choices=["broll", "clip"], default="broll")
o = a.parse_args()

if not os.path.isfile(o.video): sys.exit(f"✗ no existe {o.video}")
cfg_path = os.path.join(o.proyecto, "cine.json")
cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {}
fps = str(cfg.get("fps") or 30)
W, H = (cfg.get("lienzo") or {}).get("w", 1080), (cfg.get("lienzo") or {}).get("h", 1920)

rel = os.path.join("insertos", o.nombre)
dest = os.path.join(o.proyecto, rel)
shutil.rmtree(dest, ignore_errors=True); os.makedirs(dest)
escala = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}" if o.modo == "broll"
          else f"scale='min({W},iw)':-2")
cmd = ["nice", "-n", "19", "ffmpeg", "-v", "error", "-y", "-ss", str(o.desde)]
if o.dur: cmd += ["-t", str(o.dur)]
cmd += ["-i", o.video, "-vf", f"fps={fps},{escala},{filtro_jpg(o.video)}", "-q:v", "2", os.path.join(dest, "%05d.jpg")]   # color fiel al clip
subprocess.run(cmd, check=True)

n = len([f for f in os.listdir(dest) if f.endswith(".jpg")])
if not n: sys.exit("✗ no salió ningún cuadro (¿--desde más allá del final?)")
seg = n / float(Fraction(fps))
escena = {"desde": "@palabra", "visual": o.modo, "clip": {"dir": rel, "n": n}}
print(f"✓ {n} cuadros a {fps} fps ({seg:.2f} s) en {dest}")
print("Escena para cine.json (cambia el ancla @palabra por la palabra con la que entra):")
print(json.dumps(escena, ensure_ascii=False))
