"""Pone las tomas de stock (proyecto.json -> "broll") encima del armado: _corte_sin_broll.mp4 -> corte.mp4.

Uso:  .venv/bin/python stock_encima.py <proyecto>
armar.py lo llama; también sirve para rehacer solo las tomas sin volver a armar (luego: editar.py <p> terminar).
Cada toma se recorta 0.1 s más larga que su ventana y, si aun así se acaba antes (redondeo 30 → 29.97 fps), repite su
último cuadro: con eof_action=pass se colaba 1–2 cuadros de la persona entre toma y toma.
"""
import sys, os, subprocess
import conf

proj = sys.argv[1]; P = lambda f: os.path.join(proj, f)
C = conf.cargar(proj); br = C.get("broll", [])
W, H = (1080, 1920) if C.get("vertical") else (1920, 1080)
if not br: sys.exit("proyecto.json no tiene 'broll'")
if not os.path.exists(P("_corte_sin_broll.mp4")): os.replace(P("corte.mp4"), P("_corte_sin_broll.mp4"))
ESC = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
ins, fb, prev = ["-i", P("_corte_sin_broll.mp4")], [], "0:v"
for k, r_ in enumerate(br):
    ins += ["-ss", str(r_.get("desde", 0)), "-i", r_["fuente"]]
    # lo que se ve sigue siendo solo [desde, desde + (b − a)] del stock: el cuadro en t es el del stock en desde + (t − a)
    fb.append(f"[{k + 1}:v]trim=0:{r_['b'] - r_['a'] + .1:.3f},setpts=PTS-STARTPTS+{r_['a']:.3f}/TB,fps=30000/1001,{ESC},format=yuv420p[b{k}]")
    fb.append(f"[{prev}][b{k}]overlay=eof_action=repeat:enable='between(t,{r_['a']:.3f},{r_['b']:.3f})'[o{k}]"); prev = f"o{k}"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fb), "-map", f"[{prev}]", "-map", "0:a", "-c:v", "libx264", "-crf", "16",
                "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", P("corte.mp4")], check=True)
print(f"✓ {len(br)} tomas de stock encima del armado → corte.mp4")
