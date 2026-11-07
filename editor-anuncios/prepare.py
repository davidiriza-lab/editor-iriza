"""Paso 1 — preparar un video crudo.

Uso:  .venv/bin/python prepare.py <video> <carpeta_proyecto> [--prompt "términos, de, marca"]

Genera en la carpeta del proyecto:
  meta.json     dimensiones, fps, rotación
  words.json    transcripción con tiempos por palabra (MLX Whisper, local)
  phrases.json  frases con propuesta de keep/drop (tomas repetidas y plática de grabación)
  faces.json    posición de la cara cada 0.5 s (OpenCV Haar, local)
Edita phrases.json (campo "keep") si quieres cambiar la selección y luego corre build.py.
"""
import sys, os, json, re, subprocess, difflib, unicodedata
import numpy as np

args = sys.argv[1:]
video, proj = args[0], args[1]
prompt = args[args.index("--prompt") + 1] if "--prompt" in args else ""
os.makedirs(proj, exist_ok=True)
P = lambda f: os.path.join(proj, f)

# ---------- meta ----------
probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
    "stream=width,height,r_frame_rate,nb_frames:stream_side_data=rotation:format=duration", "-of", "json", video],
    capture_output=True, text=True).stdout)
st = probe["streams"][0]
rot = 0
for sd in st.get("side_data_list", []) or []:
    if "rotation" in sd: rot = int(sd["rotation"])
w, h = st["width"], st["height"]
if abs(rot) == 90: w, h = h, w
num, den = map(int, st["r_frame_rate"].split("/"))
meta = {"video": os.path.abspath(video), "W": w, "H": h, "fps": [num, den], "duration": float(probe["format"]["duration"]), "rotation": rot}
json.dump(meta, open(P("meta.json"), "w"), indent=1)
print(f"video {w}x{h} @ {num/den:.3f} fps, {meta['duration']:.1f}s")

# ---------- transcripción ----------
wav = P("audio.wav")
if not os.path.exists(wav):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
if not os.path.exists(P("words.json")):
    # Transcribe por bloques de voz: de corrido, Whisper "fusiona" tomas repetidas y desfasa tiempos.
    import mlx_whisper, wave
    with wave.open(wav) as wf:
        audio = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
    hop = 160
    rms = np.sqrt(np.convolve(audio ** 2, np.ones(hop) / hop, "same")[::hop] + 1e-12) * 32768
    thr = max(np.percentile(rms, 15) * 3.0, 150)
    on = rms > thr
    blocks, st_ = [], None
    for i, v in enumerate(on):
        if v and st_ is None: st_ = i
        if not v and st_ is not None: blocks.append([st_, i]); st_ = None
    if st_ is not None: blocks.append([st_, len(on)])
    merged = []
    for b0, b1 in blocks:                      # une sílabas separadas por menos de 0.45 s
        if merged and b0 - merged[-1][1] <= 45: merged[-1][1] = b1
        else: merged.append([b0, b1])
    merged = [[max(0, b0 - 15), min(len(on), b1 + 20)] for b0, b1 in merged if b1 - b0 >= 20]
    words = []
    for b0, b1 in merged:
        seg = audio[b0 * hop:b1 * hop]
        r = mlx_whisper.transcribe(seg, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="es",
                                   word_timestamps=True, initial_prompt=prompt, condition_on_previous_text=False)
        for s in r["segments"]:
            if not s["text"].strip() or s.get("no_speech_prob", 0) > 0.5 or s.get("compression_ratio", 0) > 2.6:
                continue
            for wd in s.get("words", []):
                t = wd["word"].strip()
                if t and wd["end"] > wd["start"]:
                    words.append({"w": t, "s": round(b0 / 100 + wd["start"], 3), "e": round(b0 / 100 + wd["end"], 3),
                                  "p": round(wd.get("probability", 1), 3), "blk": b0})
        words[-1:] and words[-1].update(end_blk=True)
    json.dump(words, open(P("words.json"), "w"), ensure_ascii=False, indent=0)
words = json.load(open(P("words.json")))

# ---------- frases ----------
def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", t).split()

phrases, cur = [], []
for i, wd in enumerate(words):
    if cur and (wd["s"] - cur[-1]["e"] >= 0.55 or re.search(r"[.?!]$", cur[-1]["w"]) or wd.get("blk") != cur[-1].get("blk") and wd["s"] - cur[-1]["e"] >= 0.3):
        phrases.append(cur); cur = []
    cur.append(wd)
if cur: phrases.append(cur)
ph = [{"id": k, "s": p[0]["s"], "e": p[-1]["e"], "text": " ".join(x["w"] for x in p), "n": len(p)} for k, p in enumerate(phrases)]

# ---------- propuesta automática ----------
CHATTER = re.compile(r"\b(otra vez|espera|a ver|te saliste|perdon|carajo|bloque|ok|listo|gracias|exacto|nice|todo bien|verdad|ya ya|como dices|"
                     r"cambiamos de plano|lo voy a hacer|puedo repetir|podria repetir|me esta|camara|telefono)\b")
for k, p in enumerate(ph):
    p["keep"], p["why"] = True, ""
    toks = norm(p["text"])
    if CHATTER.search(" ".join(toks)) and len(toks) <= 9:
        p["keep"], p["why"] = False, "plática de grabación"
        continue
    # fragmento suelto: sus palabras aparecen seguidas dentro de otra frase cercana
    if len(toks) <= 6:
        joined = " ".join(toks)
        if any(joined in " ".join(norm(ph[j]["text"])) for j in range(max(0, k - 3), min(k + 4, len(ph))) if j != k and ph[j]["n"] > p["n"]):
            p["keep"], p["why"] = False, "fragmento de otra toma"
            continue
    # ¿se vuelve a decir más adelante? -> es una toma repetida; se queda la última
    for j in range(k + 1, min(k + 7, len(ph))):
        tj = norm(ph[j]["text"])
        m = min(len(toks), len(tj), 7)
        if m >= 2 and difflib.SequenceMatcher(None, toks[:m], tj[:m]).ratio() >= 0.6:
            p["keep"], p["why"] = False, f"toma repetida (se usa #{j})"
            break
json.dump(ph, open(P("phrases.json"), "w"), ensure_ascii=False, indent=1)

# ---------- cara ----------
if not os.path.exists(P("faces.json")):
    import cv2
    cap = cv2.VideoCapture(video)
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    fps = num / den; step = max(1, round(fps / 2)); faces = []; i = 0
    while True:
        ok = cap.grab()
        if not ok: break
        if i % step == 0:
            ok, fr = cap.retrieve()
            if ok:
                fh, fw = fr.shape[:2]
                sc = 480 / max(fh, fw)
                g = cv2.cvtColor(cv2.resize(fr, (int(fw * sc), int(fh * sc))), cv2.COLOR_BGR2GRAY)
                d = casc.detectMultiScale(g, 1.1, 5, minSize=(24, 24))
                if len(d):
                    x, y, a, b = max(d, key=lambda r: r[2] * r[3])
                    gh, gw = g.shape
                    faces.append([round(i / fps, 2), round((x + a / 2) / gw, 4), round((y + b / 2) / gh, 4), round(b / gh, 4)])
        i += 1
    json.dump({"frame_shape": [int(fw), int(fh)] if faces else None, "faces": faces}, open(P("faces.json"), "w"))

# ---------- reporte ----------
for p in ph:
    print(f"{'✔' if p['keep'] else '✘'} #{p['id']:<3} {p['s']:7.2f}-{p['e']:7.2f}  {p['text']}" + (f"   ← {p['why']}" if p["why"] else ""))
