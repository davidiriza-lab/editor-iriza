"""Paso 1 — transcribir el video crudo para elegir las mejores partes.

Uso:  .venv/bin/python transcribir.py <video_crudo> <carpeta_proyecto> ["Nombres, Marcas"]

Transcribe POR PEDAZOS de voz (separados por silencios) con Whisper mlx: de corrido, Whisper fusiona tomas repetidas,
se salta frases y desfasa los tiempos hasta 0.5 s. Cada pedazo lleva su volumen: la persona a cámara suena más fuerte
(≈ −20…−30 dB) que el director o quien dicta fuera de cámara (≈ −35…−45 dB) → se marca «¿director?».
Genera en la carpeta del proyecto:
  fuente.txt          [mm:ss.s – mm:ss.s] [dB] texto   (para proponer cortes; las tomas buenas suelen ser las últimas y más fuertes)
  fuente_regiones.json  lo mismo en JSON
  proyecto.json       plantilla con "fuente" ya puesta (si no existía)
"""
import sys, os, json
import numpy as np
import conf

video, proj = os.path.abspath(sys.argv[1]), sys.argv[2]
VOC = sys.argv[3] if len(sys.argv) > 3 else ""          # nombres propios: "el mentor, la empresa del cliente"
os.makedirs(proj, exist_ok=True); P = lambda f: os.path.join(proj, f)
e, thr = conf.energia(video, .05); voz = e > max(thr, -42)
regs, i = [], 0
while i < len(voz):
    if voz[i]:
        j = i
        while j < len(voz) and (voz[j] or voz[j:j + 7].any()): j += 1      # une huecos < 0.35 s
        if (j - i) * .05 >= .3: regs.append((i * .05, j * .05, float(np.percentile(e[i:j], 80))))
        i = j
    else: i += 1
med = float(np.percentile([r[2] for r in regs], 75)) if regs else -30      # volumen típico de la persona a cámara
mmss = lambda t: f"{int(t // 60):02d}:{t % 60:04.1f}"
out = []
for a, b, d in regs:
    w = P("_tramo.wav"); conf.wav_tramo(video, max(0, a - .05), b + .1, w)
    txt = conf.transcribir(w, vocabulario=VOC)["text"].strip(); os.remove(w)
    pal = txt.split()
    if len(txt) > 25 * (b - a) + 25 or (len(pal) > 6 and len(set(pal)) < len(pal) / 3): txt = "(ruido o texto inventado por Whisper)"
    out.append({"a": round(a, 2), "b": round(b, 2), "db": round(d, 1), "texto": txt, "director": d < med - 6})
json.dump(out, open(P("fuente_regiones.json"), "w"), ensure_ascii=False, indent=1)
with open(P("fuente.txt"), "w") as f:
    for r in out:
        f.write(f"[{mmss(r['a'])} – {mmss(r['b'])}] [{r['db']:4.0f} dB] {r['texto']}{'   ← ¿director?' if r['director'] else ''}\n")
if not os.path.exists(P("proyecto.json")):
    json.dump({"nombre": os.path.basename(proj), "fuente": video, "cortes": [], "vocabulario": VOC, "salida": "final.mp4"}, open(P("proyecto.json"), "w"), ensure_ascii=False, indent=1)
print(open(P("fuente.txt")).read())
