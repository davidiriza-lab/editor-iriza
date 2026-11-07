"""Paso 2 — cortar: arma la línea de tiempo con las frases elegidas y genera cut.mov.

Uso:  .venv/bin/python build.py <carpeta_proyecto> [--drop 8,14] [--keep 5] [--gap 0.30]

- Toma las frases con keep=true de phrases.json (--drop / --keep cambian la selección y la guardan).
- Dentro de cada frase quita pausas mayores a --gap segundos.
- Afina inicio/fin de cada tramo con la energía del audio (no se come sílabas finales).
- Ajusta los tramos a la rejilla de cuadros para que audio y video queden exactos.
Genera: edl.json, words_out.json, guion.txt (texto con tiempos ya cortados) y cut.mov
"""
import sys, os, json, subprocess, wave
import numpy as np

args = sys.argv[1:]
proj = args[0]
P = lambda f: os.path.join(proj, f)
opt = lambda k, d: args[args.index(k) + 1] if k in args else d
GAP = float(opt("--gap", "0.30"))

meta = json.load(open(P("meta.json")))
words = json.load(open(P("words.json")))
ph = json.load(open(P("phrases.json")))
for k in [int(x) for x in opt("--drop", "").split(",") if x]: ph[k]["keep"], ph[k]["why"] = False, "manual"
for k in [int(x) for x in opt("--keep", "").split(",") if x]: ph[k]["keep"], ph[k]["why"] = True, "manual"
json.dump(ph, open(P("phrases.json"), "w"), ensure_ascii=False, indent=1)

num, den = meta["fps"]; fps = num / den

# energía del audio (10 ms) para afinar bordes
with wave.open(P("audio.wav")) as wf:
    sr = wf.getframerate(); a = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32)
hop = sr // 100
rms = np.sqrt(np.convolve(a ** 2, np.ones(hop) / hop, "same")[::hop] + 1e-9)
floor = np.percentile(rms, 15); thr = max(floor * float(opt("--umbral", "3.0")), 150)   # --umbral 2.0 si habla bajito y se come palabras
def extend(t, direction, limit):
    i = int(t * 100); n = 0
    while 0 <= i < len(rms) and rms[i] > thr and n < limit * 100:
        i += direction; n += 1
    return i / 100

# tramos de habla: dentro de cada frase elegida, la voz se detecta con la energía real del audio
# (Whisper estira palabras sobre los silencios, así que sus tiempos no sirven para hallar pausas)
import re as _re
def runs_of(mask, i0, min_len=4, join=0):
    out, start = [], None
    for i, v in enumerate(mask):
        if v and start is None: start = i
        if not v and start is not None: out.append([start, i]); start = None
    if start is not None: out.append([start, len(mask)])
    out = [r for r in out if r[1] - r[0] >= min_len]
    merged = []
    for r in out:
        if merged and r[0] - merged[-1][1] <= join: merged[-1][1] = r[1]
        else: merged.append(r)
    return [[i0 + a, i0 + b] for a, b in merged]

def align(ws, runs):
    """Re-alinea palabras con el audio.
    1) Cada pausa real (hueco entre tramos con voz) se asigna a una frontera entre palabras,
       eligiendo la asignación monótona que mejor coincide con los inicios que da Whisper (programación dinámica).
    2) Entre pausas asignadas, las palabras se reparten por número de letras sobre el tiempo con voz."""
    if not runs or not ws: return
    n, onsets = len(ws), [r[0] / 100 for r in runs[1:]]          # inicio de cada tramo después de una pausa
    m, SKIP, INF = len(onsets), 0.45, 1e9
    # D[k][j]: costo usando las primeras k pausas, la última asignada a una frontera <= j
    D = [[INF] * n for _ in range(m + 1)]; B = [[None] * n for _ in range(m + 1)]
    for j in range(n): D[0][j] = 0
    for k in range(1, m + 1):
        for j in range(n):
            best, arg = D[k - 1][j] + SKIP, ("skip", j)             # la pausa cae dentro de una palabra
            if j >= 1:
                c = D[k - 1][j - 1] + abs(onsets[k - 1] - ws[j]["s"])  # pausa antes de la palabra j
                if c < best: best, arg = c, ("set", j)
                if D[k][j - 1] < best: best, arg = D[k][j - 1], ("carry", j - 1)
            D[k][j], B[k][j] = best, arg
    cuts, k, j = {}, m, n - 1                                       # recupera: palabra j empieza en la pausa k
    while k > 0:
        kind, jj = B[k][j]
        if kind == "set": cuts[j] = k; k, j = k - 1, j - 1
        elif kind == "skip": k -= 1
        else: j = jj
    bounds = [0] + sorted(cuts) + [n]                               # grupos de palabras entre pausas asignadas
    run_of = lambda j: 0 if j == 0 else cuts[j]
    for gi in range(len(bounds) - 1):
        j0, j1 = bounds[gi], bounds[gi + 1]
        r0 = run_of(j0); r1 = cuts[j1] if j1 < n else len(runs)
        idx = [i for a, b in runs[r0:r1] for i in range(a, b)]
        if not idx: continue
        wt = [max(2, len(_re.sub(r"[^\wáéíóúñü]", "", w["w"])) + 1) for w in ws[j0:j1]]
        tot, acc, V = sum(wt), 0, len(idx)
        for w, c in zip(ws[j0:j1], wt):
            v0, v1 = V * acc / tot, V * (acc + c) / tot; acc += c
            w["s"] = idx[min(V - 1, int(v0))] / 100
            w["e"] = (idx[max(0, min(V - 1, int(v1) - 1))] + 1) / 100

kept = [p for p in ph if p["keep"]]
segs = []
todas = []   # todas las palabras de las frases elegidas (para no perder ninguna en los bordes de un corte)
for p in kept:
    k = p["id"]
    lo = max(p["s"] - 0.20, ph[k - 1]["e"] + 0.05 if k else 0)
    hi = min(p["e"] + 0.40, ph[k + 1]["s"] - 0.05 if k + 1 < len(ph) else meta["duration"])
    i0, i1 = int(lo * 100), min(int(hi * 100), len(rms))
    ws = [dict(w) for w in words if p["s"] - 1e-3 <= w["s"] and w["e"] <= p["e"] + 1e-3]
    todas += ws
    fine = runs_of(rms[i0:i1] > thr, i0, min_len=3, join=6)            # voz (para alinear palabras)
    align(ws, fine)
    for a, b in runs_of(rms[i0:i1] > thr, i0, min_len=4, join=int(GAP * 100)):   # tramos (para cortar)
        s_, e_ = max(lo, a / 100 - 0.06), min(hi, b / 100 + 0.10)
        seg_ws = [w for w in ws if s_ - 0.02 <= w["s"] < e_ and not w.get("_used")]
        for w in seg_ws: w["_used"] = True
        if segs and s_ <= segs[-1]["e"] + 0.04:
            segs[-1]["e"] = max(segs[-1]["e"], e_); segs[-1]["words"] += seg_ws
        else:
            segs.append({"s": s_, "e": e_, "words": seg_ws})

# palabras que quedaron fuera de todo tramo (su inicio cayó en un borde): al tramo más cercano
for w in todas:
    if w.get("_used") or not segs: continue
    g = min(segs, key=lambda g: 0 if g["s"] <= w["s"] <= g["e"] else min(abs(w["s"] - g["s"]), abs(w["s"] - g["e"])))
    w["_used"] = True; g["words"].append(w)
for g in segs: g["words"].sort(key=lambda w: w["s"])

# fuera tramos sin palabras y muy cortos (ruidos, respiraciones)
segs = [g for g in segs if g["words"] or g["e"] - g["s"] >= 0.6]

# rejilla de cuadros + mapeo a tiempo de salida
faces = json.load(open(P("faces.json")))["faces"]
allf = np.array([f[1:] for f in faces]) if faces else None
out_f, edl, wout = 0, [], []
for g in segs:
    a_f, b_f = round(g["s"] * fps), round(g["e"] * fps)
    if b_f - a_f < 3: continue
    a_t, b_t = a_f / fps, b_f / fps
    o_t = out_f / fps
    near = [f[1:] for f in faces if a_t - 0.3 <= f[0] <= b_t + 0.3]
    face = np.median(np.array(near), axis=0).tolist() if near else (np.median(allf, axis=0).tolist() if allf is not None else [0.5, 0.33, 0.12])
    edl.append({"src_in": a_t, "src_out": b_t, "out_in": o_t, "out_out": o_t + (b_t - a_t), "frames": b_f - a_f,
                "face": [round(x, 4) for x in face], "text": " ".join(w["w"] for w in g["words"])})
    for w in g["words"]:
        ws_, we_ = min(max(w["s"], a_t), b_t), min(max(w["e"], a_t), b_t)
        wout.append({"w": w["w"], "s": round(ws_ - a_t + o_t, 3), "e": round(we_ - a_t + o_t, 3)})
    out_f += b_f - a_f

json.dump({"W": meta["W"], "H": meta["H"], "fps": meta["fps"], "frames": out_f, "duration": out_f / fps, "segments": edl},
          open(P("edl.json"), "w"), ensure_ascii=False, indent=1)
json.dump(wout, open(P("words_out.json"), "w"), ensure_ascii=False, indent=0)
with open(P("guion.txt"), "w") as f:
    for k, sg in enumerate(edl):
        f.write(f"[{sg['out_in']:6.2f}-{sg['out_out']:6.2f}] corte {k}: {sg['text']}\n")
    f.write("\n# palabras (tiempo de salida)\n")
    f.write(" ".join(f"{w['w']}@{w['s']:.2f}" for w in wout) + "\n")

# cut.mov: selección exacta por tiempo (mismos tramos para audio y video)
h = 0.5 / fps
sel = "+".join(f"between(t,{s['src_in'] - h:.5f},{s['src_out'] - h:.5f})" for s in edl)
script = P("cut_filter.txt")
open(script, "w").write(f"[0:v]select='{sel}',setpts=N/({num}/{den}*TB)[v];[0:a]aselect='{sel}',asetpts=N/SR/TB[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", meta["video"], "-/filter_complex", script, "-map", "[v]", "-map", "[a]",
                "-r", f"{num}/{den}", "-c:v", "libx264", "-crf", "12", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                "-c:a", "pcm_s16le", P("cut.mov")], check=True)
got = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-count_packets", "-show_entries", "stream=nb_read_packets",
                      "-of", "csv=p=0", P("cut.mov")], capture_output=True, text=True).stdout.strip().split(",")[0]
print(f"umbral de voz {thr:.0f} (ruido {floor:.0f})")
print(f"{len(edl)} tramos · {meta['duration']:.1f}s → {out_f / fps:.1f}s · cuadros {got}/{out_f}")
