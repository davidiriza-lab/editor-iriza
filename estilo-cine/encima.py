"""Pone un efecto ENCIMA de un video ya renderizado (la capa con transparencia).

Para lo que debe verse sobre la persona y sobre los textos: chispas, un impacto, un destello, una
animación con fondo transparente. No toca cine.js: trabaja sobre el MP4 final con ffmpeg.

  python3 estilo-cine/encima.py <base.mp4> <efecto> <salida.mp4> --en 3.2 [--dur 1.5]
          [--modo pantalla|alfa|normal] [--x 540] [--y 900] [--w 700] [--opacidad 1]

  --modo pantalla  (por defecto) el efecto viene sobre fondo NEGRO: lo negro desaparece y lo claro se suma a la imagen
                   (fuego, rayos, chispas, destellos; cualquier clip con fondo negro).
  --modo alfa      el efecto trae canal alfa (WebM VP9, MOV ProRes 4444 o secuencia PNG).
  --modo normal    se pone tal cual, opaco (una ventanita).
  --x --y          centro del efecto en píxeles del video (por defecto, el centro del cuadro).
  --w              ancho del efecto en píxeles (por defecto, el ancho del video).
  --en --dur       cuándo entra y cuánto dura (por defecto, lo que dure el efecto).

El audio del video base se conserva intacto. Después, como siempre: estilo-cine/entrega.py verificar.
"""
import argparse
import json
import subprocess
import sys

a = argparse.ArgumentParser()
a.add_argument("base"); a.add_argument("efecto"); a.add_argument("salida")
a.add_argument("--en", type=float, default=0.0)
a.add_argument("--dur", type=float, default=None)
a.add_argument("--modo", choices=["pantalla", "alfa", "normal"], default="pantalla")
a.add_argument("--x", type=float, default=None); a.add_argument("--y", type=float, default=None)
a.add_argument("--w", type=int, default=None)
a.add_argument("--opacidad", type=float, default=1.0)
o = a.parse_args()


def sonda(f):
    d = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", f], capture_output=True, text=True).stdout or "{}")
    v = next((s for s in d.get("streams", []) if s["codec_type"] == "video"), None)
    if not v:
        sys.exit(f"✗ {f} no tiene video")
    return v, float(d["format"].get("duration", 0)), any(s["codec_type"] == "audio" for s in d["streams"])


vb, durb, con_audio = sonda(o.base)
ve, dure, _ = sonda(o.efecto)
W, H = vb["width"], vb["height"]
w = o.w or W
w -= w % 2
h = round(ve["height"] * w / ve["width"]); h -= h % 2
cx, cy = (o.x if o.x is not None else W / 2), (o.y if o.y is not None else H / 2)
x, y = round(cx - w / 2), round(cy - h / 2)
dur = min(o.dur or dure, dure, max(0.05, durb - o.en))
fin = o.en + dur
fx = f"[1:v]trim=0:{dur:.3f},setpts=PTS-STARTPTS+{o.en:.3f}/TB,scale={w}:{h}"
cuando = f"enable='between(t,{o.en:.3f},{fin:.3f})'"
A709 = "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"   # entrega estándar: Rec.709 de rango de video

if o.modo == "pantalla":
    # el efecto se pinta sobre un lienzo negro del tamaño del video y se funde en modo "pantalla": lo negro no suma nada
    filtro = (f"{fx},format=gbrp,colorchannelmixer=rr={o.opacidad}:gg={o.opacidad}:bb={o.opacidad}[fx];"
              f"color=black:s={W}x{H}:d={durb:.3f},format=gbrp[negro];"
              f"[negro][fx]overlay={x}:{y}:eof_action=pass[capa];"
              f"[0:v]format=gbrp[b];[b][capa]blend=all_mode=screen:{cuando},{A709}[v]")
elif o.modo == "alfa":
    filtro = (f"{fx},format=yuva420p,colorchannelmixer=aa={o.opacidad}[fx];"
              f"[0:v][fx]overlay={x}:{y}:eof_action=pass:{cuando},{A709}[v]")
else:
    filtro = f"{fx}[fx];[0:v][fx]overlay={x}:{y}:eof_action=pass:{cuando},{A709}[v]"

cmd = ["nice", "-n", "19", "ffmpeg", "-v", "error", "-nostdin", "-y", "-i", o.base, "-i", o.efecto, "-filter_complex", filtro,
       "-map", "[v]", "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "-movflags", "+faststart"]
cmd += ["-map", "0:a", "-c:a", "copy"] if con_audio else []
r = subprocess.run(cmd + ["-t", f"{durb:.3f}", o.salida])
if r.returncode:
    sys.exit(r.returncode)
print(f"✓ efecto encima de {o.en:.2f} a {fin:.2f} s · {w}×{h} px centrado en ({cx:.0f}, {cy:.0f}) · modo {o.modo} → {o.salida}")
