"""Paso 5 — mezcla de audio (render.mjs la corre sola al final; se puede repetir para ajustar la música sin volver a renderizar).

Uso:  .venv/bin/python mezcla.py <carpeta_proyecto> [volumen_musica] [factor_bajo_voz]

- Voz: el armado ya trae cada corte nivelado (armar.py); aquí solo se mezcla.
- Música (proyecto.json -> "musica"): un archivo, o una CARPETA de canciones (elige una que no se haya usado en otro
  proyecto y la anota en proyectos/_musica_usada.json). Si no hay música, se detiene y pide una carpeta o un MCP de música
  ("sin_musica": true para entregar sin música). Suena desde el segundo 0 (sin intro suave: arranca donde la canción ya
  está llena, o en "musica_desde"), baja mientras hay voz (ducking por la energía REAL de la voz) y se va con el fundido final.
- Whoosh suave en cada transición, sin pisar la última sílaba antes del corte.
- Volumen final exacto a `lufs` (plantilla.json, −14 = estándar de redes) en dos pasadas.
- Escribe <proyecto>/final.mp4 y luego lo copia a "salida" y verifica la copia (si la salida es una tarjeta SD y algo falla,
  queda el original en el proyecto).
"""
import subprocess, sys, os, json, glob, random, shutil
import numpy as np
import conf

proj = os.path.abspath(sys.argv[1]); P = lambda f: os.path.join(proj, f)
HERE = conf.HERE; C = conf.cargar(proj)
V = float(sys.argv[2]) if len(sys.argv) > 2 else C.get("volumen_musica", 0.39)
DUCK = float(sys.argv[3]) if len(sys.argv) > 3 else C.get("ducking", 0.6)
probe = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
DUR = probe(P("_video.mp4")); SR = 48000
CUTS = json.load(open(P("_transiciones.json"))) if os.path.exists(P("_transiciones.json")) else []
CJ = json.load(open(P("cortes.json")))
FIN_VOZ = CJ.get("fin_voz", DUR - .2); FADE0 = max(0, min(DUR - .4, FIN_VOZ - .15))
WS = [w for s in json.load(open(P("words.json")))["segments"] for w in s["words"]]

# ---------- música: archivo o carpeta ----------
def elegir_musica():
    m = C.get("musica")
    if C.get("sin_musica"): return None
    if not m or not os.path.exists(m if os.path.isabs(m) else P(m)):
        sys.exit("✗ Falta la música. Pásame una CARPETA con canciones (mp3/wav) o conecta un MCP de música (p. ej. Epidemic Sound)\n"
                 "  y pon su ruta en proyecto.json -> \"musica\". Para entregar sin música: \"sin_musica\": true.")
    m = m if os.path.isabs(m) else P(m)
    if os.path.isfile(m): return m
    canciones = sorted(f for f in glob.glob(os.path.join(m, "**", "*"), recursive=True) if f.lower().endswith((".mp3", ".wav", ".m4a", ".aif", ".aiff", ".flac")))
    if not canciones: sys.exit(f"✗ La carpeta de música está vacía: {m}")
    reg_p = os.path.join(os.path.dirname(proj), "_musica_usada.json"); reg = json.load(open(reg_p)) if os.path.exists(reg_p) else {}
    nombre = os.path.basename(proj)
    if reg.get(nombre) in canciones: return reg[nombre]
    usadas = set(reg.values()); libres = [c for c in canciones if c not in usadas] or canciones
    elegida = random.Random(nombre).choice(libres); reg[nombre] = elegida
    json.dump(reg, open(reg_p, "w"), ensure_ascii=False, indent=1)
    print(f"música: {os.path.basename(elegida)} ({len(libres)} sin usar en la carpeta)")
    return elegida

def pcm(path, sr=SR, ch=2):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", str(ch), "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()

mus = elegir_musica()
ins = ["-i", P("_video.mp4"), "-i", P("corte.mp4")]
fc = f"[1:a]aresample=48000,apad=whole_dur={DUR:.3f}[voz]"; mix = "[voz]"
if mus:
    m = pcm(mus)
    # arranque: donde la canción ya está llena (≥ 70 % de su energía típica), salvo "musica_desde"
    rms = np.sqrt((m[:len(m) // SR * SR, 0].reshape(-1, SR) ** 2).mean(axis=1))
    desde = C.get("musica_desde")
    if desde is None:
        lleno = np.where(rms >= .7 * np.median(rms))[0]; desde = float(lleno[0]) if len(lleno) else 0.0
    m = m[int(desde * SR):]
    if len(m) < DUR * SR: m = np.concatenate([m, np.zeros((int(DUR * SR) - len(m) + 1, 2), np.float32)])
    m = m[:int(DUR * SR)]
    # ducking con la energía real de la voz del armado (10 ms), no con los tiempos de Whisper
    v = pcm(P("corte.mp4"), 16000, 1)[:, 0]; n = 160
    e = np.array([20 * np.log10(np.sqrt((v[i:i + n] ** 2).mean()) + 1e-9) for i in range(0, len(v) - n, n)])
    voz = e > max(np.percentile(e, 15) + 12, -44)
    g = np.ones(len(m), np.float32)
    for i in np.where(voz)[0]: g[max(0, int((i * .01 - .12) * SR)):int((i * .01 + .25) * SR)] = DUCK
    k = int(.3 * SR); g = np.convolve(g, np.ones(k) / k, mode="same")
    t = np.arange(len(m)) / SR
    g *= np.clip(t / .15, 0, 1) * np.clip((DUR - t) / max(.3, DUR - FADE0), 0, 1)      # desde el segundo 0; se va con el fundido
    m *= (g * V)[:, None]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", P("_musica_mezcla.wav")], input=m.tobytes(), check=True)
    ins += ["-i", P("_musica_mezcla.wav")]; fc += ";[2:a]anull[mus]"; mix += "[mus]"
    print(f"música desde {desde:.1f}s de {os.path.basename(mus)}")
# whoosh: nunca empieza antes de que termine la última palabra antes del corte
WH = os.path.join(HERE, "sfx", "whoosh.wav")
if not os.path.exists(WH): print("(sin whoosh: falta sfx/whoosh.wav)"); CUTS = []
for k_, c in enumerate(CUTS):
    antes = [w["end"] for w in WS if w["end"] <= c + .05]
    ini = max(c - .22, (max(antes) + .03) if antes else 0)
    if ini > c + .1: continue
    n_ = len(ins) // 2; ins += ["-i", os.path.join(HERE, "sfx", "whoosh.wav")]
    fc += f";[{n_}:a]aresample=48000,volume=0.18,adelay={round(ini * 1000)}:all=1[w{k_}]"; mix += f"[w{k_}]"
n_in = mix.count("[")
fc += (f";{mix}amix=inputs={n_in}:normalize=0:duration=first,atrim=0:{DUR:.3f}[pre]" if n_in > 1 else f";[voz]atrim=0:{DUR:.3f}[pre]")

# ---------- volumen final exacto (loudnorm en dos pasadas) ----------
L = C.get("lufs", -14)
o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *ins, "-filter_complex", fc + f";[pre]loudnorm=I={L}:TP=-1.5:LRA=11:print_format=json[a]",
                    "-map", "[a]", "-f", "null", "-"], capture_output=True, text=True).stderr
mj = json.loads(o[o.rindex("{"):o.rindex("}") + 1])
ln = (f"loudnorm=I={L}:TP=-1.5:LRA=11:measured_I={mj['input_i']}:measured_TP={mj['input_tp']}:measured_LRA={mj['input_lra']}:"
      f"measured_thresh={mj['input_thresh']}:offset={mj['target_offset']}:linear=true,aresample=48000")
final = P("final.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc + f";[pre]{ln}[a]", "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", final], check=True)

def lufs(path):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr
    return [l.split("I:")[1].strip() for l in o.splitlines() if l.strip().startswith("I:")][0]

# ---------- copia a la salida: solo si se corre suelto; editar.py entrega al final, después de todas las revisiones ----------
if not os.environ.get("NO_ENTREGAR"):
    out = conf.entregar(proj)
    if out: print("listo ->", out)
print("final:", final, "| mezcla:", lufs(final), "| música sola:", lufs(P("_musica_mezcla.wav")) if mus else "-")
