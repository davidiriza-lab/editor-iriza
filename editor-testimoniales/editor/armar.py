"""Paso 2 — armar el video con los cortes aprobados (antes: cortes.py para bordes, pausas y doble revisión).

Uso:  .venv/bin/python armar.py <carpeta_proyecto>

Lee proyecto.json (+ plantilla.json) y genera:
  corte.mp4      el armado: cortes en orden, voz de cada corte nivelada a la mediana de los cortes (que no brinque entre cortes),
                 y al final `cola` segundos de imagen REAL del video (sin cuadro congelado; la voz ya terminó)
  cortes.json    fronteras de cada corte en el tiempo del armado + fin de la voz
  words.json     transcripción del armado con tiempos por palabra (Whisper mlx)
  faces.json     cara por corte (lado del texto en horizontal)
  caras.json     cara y coronilla en TODOS los fotogramas (bin/caras) → los textos nunca van encima de la persona
  corte.txt      transcripción legible (base para escribir pages.txt)
Además:
  - Video HDR (HLG/PQ, p. ej. DJI): se convierte solo a Rec.709 con bin/sdr antes de usarlo.
  - Video horizontal en proyecto vertical: el recorte 9:16 sigue la cara de cada corte (no el centro fijo).
  - "broll_auto": elige tomas del stock que nunca crucen un cambio de plano (stock.py), distintas en cada proyecto,
    justo después de la palabra `despues_de` (p. ej. el apellido de quien se menciona). "broll" manual sigue funcionando.
  - "flecha": se coloca sola en la palabra "clic"/"click"/"botón"/"enlace" (salvo "fijo": true).
"""
import sys, os, json, subprocess, random, glob, re, difflib
import numpy as np, cv2      # cv2 solo dibuja la máscara del circulito
import conf

proj = sys.argv[1]; P = lambda f: os.path.join(proj, f)
HERE = conf.HERE; BIN = os.path.join(HERE, "bin")
C = conf.cargar(proj); RAW = json.load(open(P("proyecto.json")))
cuts = C["cortes"]; assert cuts, "proyecto.json no tiene 'cortes'"
VERT = C.get("vertical", False); W, H = (1080, 1920) if VERT else (1920, 1080)
run = lambda *a, **k: subprocess.run(*a, check=True, **k)
probe = lambda f, *e: subprocess.run(["ffprobe", "-v", "error", *e, "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip()

# ---------- 0. limpiar lo de una corrida anterior (si no, se reusan archivos viejos) ----------
for f in ("_corte_sin_broll.mp4", "_corte_con_broll.mp4", "caras.json", "layout.json", "_video.mp4", "words.json", "contraste.json"):
    if os.path.exists(P(f)): os.remove(P(f))

# ---------- 1. fuentes: HDR → Rec.709 ----------
def preparar(src):
    tr = probe(src, "-select_streams", "v:0", "-show_entries", "stream=color_transfer").split("\n")[0]
    if tr not in ("arib-std-b67", "smpte2084"): return src
    os.makedirs(P("_sdr"), exist_ok=True); dst = P(f"_sdr/{os.path.splitext(os.path.basename(src))[0]}.mov")
    if not os.path.exists(dst):
        print(f"HDR ({tr}) → Rec.709: {os.path.basename(src)}"); run([os.path.join(BIN, "sdr"), src, dst])
    return dst
ORIG = [C["fuente"]] + sorted({c[2] for c in cuts if len(c) > 2} - {C["fuente"]})
LISTO = {s: preparar(s) for s in ORIG}
FU = [LISTO[s] for s in ORIG]
idx = lambda c: ORIG.index(c[2]) if len(c) > 2 else 0

# ---------- 2. encuadre: horizontal en vertical sigue la cara del corte ----------
def encuadre(c):
    src = FU[idx(c)]; w, h = map(int, probe(src, "-select_streams", "v:0", "-show_entries", "stream=width,height").split("\n")[0].split(","))
    if not VERT or h >= w:
        return f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    j = P("_encuadre.json"); run([os.path.join(BIN, "caras"), src, j, str(c[0]), str(c[1]), "0.5"], capture_output=True)
    cx = [(f[1] + f[3]) / 2 / w for f in json.load(open(j))["f"] if f[1] >= 0]; os.remove(j)
    x = float(np.median(cx)) if cx else .5
    sw = round(w * H / h / 2) * 2                       # ancho escalado a 1920 de alto
    x0 = int(min(sw - W, max(0, x * sw - W / 2)))
    print(f"  corte {c[0]:.2f}-{c[1]:.2f}: horizontal → recorte vertical centrado en la cara (x={x:.2f})")
    return f"scale={sw}:{H},crop={W}:{H}:{x0}:0"

# ---------- 3. volumen de la voz por corte ----------
def lufs(src, a, b):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", str(a), "-to", str(b), "-i", src, "-vn", "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr
    v = [l.split("I:")[1].split()[0] for l in o.splitlines() if l.strip().startswith("I:")]
    return float(v[0]) if v and v[0] != "-inf" else None
# se nivela contra la mediana de los cortes (solo se corrigen diferencias entre cortes; el volumen final lo pone mezcla.py)
NIV = [lufs(FU[idx(c)], c[0], c[1]) for c in cuts]
OBJ = RAW.get("voz_corte_lufs", float(np.median([x for x in NIV if x is not None] or [-23])))

# ---------- 4. armado ----------
dur_src = {s: float(probe(s, "-show_entries", "format=duration")) for s in FU}
COLA = C.get("cola", .6); f = []; largos = []; ganancias = []
for i, c in enumerate(cuts):
    a, b = c[0], c[1]; k = idx(c); src = FU[k]; ultimo = i == len(cuts) - 1
    bv = min(b + COLA, dur_src[src] - .05) if ultimo else b          # el último corte sigue con imagen real
    I = NIV[i]; g = 0 if I is None else max(-8, min(8, OBJ - I)); ganancias.append(round(g, 1))
    f.append(f"[{k}:v]trim={a}:{bv},setpts=PTS-STARTPTS,fps=30000/1001,{encuadre(c)},format=yuv420p[v{i}]")
    f.append(f"[{k}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={g:.2f}dB,"
             f"afade=t=in:d=0.02,afade=t=out:st={b - a - 0.04:.3f}:d=0.04" + (f",apad=whole_dur={bv - a:.3f}" if ultimo else "") + f"[a{i}]")
    largos.append(bv - a)
f.append("".join(f"[v{i}][a{i}]" for i in range(len(cuts))) + f"concat=n={len(cuts)}:v=1:a=1[v][a]")
open(P("_cut_filter.txt"), "w").write(";\n".join(f))
run(["ffmpeg", "-v", "error", "-y", *[x for s in FU for x in ("-i", s)], "-/filter_complex", P("_cut_filter.txt"), "-map", "[v]", "-map", "[a]",
     "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", P("corte.mp4")])
bounds = [round(float(x), 3) for x in np.cumsum(largos)]; cola_real = round(largos[-1] - (cuts[-1][1] - cuts[-1][0]), 3)
print(f"armado {bounds[-1]:.2f}s · cortes en {bounds[:-1]} · voz nivelada (dB por corte): {ganancias} · cola real {cola_real}s")

# ---------- cara y coronilla en TODOS los fotogramas (Vision) → texto nunca encima, lado del texto, circulito ----------
if os.path.exists(os.path.join(BIN, "caras")): run([os.path.join(BIN, "caras"), P("corte.mp4"), P("caras.json")])
else: sys.exit("✗ falta bin/caras: corre ./instalar.sh (Mac) o ./instalar-windows.sh (Windows/Linux) en la raíz del sistema")
CARAS = json.load(open(P("caras.json")))["f"]
def cara_en(a, b):
    fs = [f for f in CARAS if a <= f[0] <= b and f[1] >= 0]
    return fs

# ---------- 5. transcripción del armado (Whisper mlx, por palabra) ----------
run(["ffmpeg", "-v", "error", "-y", "-i", P("corte.mp4"), "-vn", "-ac", "1", "-ar", "16000", P("_corte.wav")])
r = conf.transcribir(P("_corte.wav"), palabras=True, vocabulario=C.get("vocabulario", "")); os.remove(P("_corte.wav"))
d = {"text": r["text"], "segments": [{"start": s["start"], "end": s["end"], "text": s["text"],
                                      "words": [{"word": w["word"], "start": w["start"], "end": w["end"]} for w in s.get("words", [])]} for s in r["segments"]]}
json.dump(d, open(P("words.json"), "w"), ensure_ascii=False)
with open(P("corte.txt"), "w") as fh:
    for s in d["segments"]: fh.write(f"[{s['start']:6.2f} – {s['end']:6.2f}] {s['text'].strip()}\n")
WS = [w for s in d["segments"] for w in s["words"]]
norm = lambda s: re.sub(r"[^a-z0-9ñ]", "", s.lower().translate(str.maketrans("áéíóúü", "aeiouu")))
fin_voz = round(bounds[-1] - cola_real, 3)
json.dump({"cortes": cuts, "fronteras": bounds, "fin_voz": fin_voz, "cola_real": cola_real, "ganancias_db": ganancias}, open(P("cortes.json"), "w"))

# ---------- 6. tomas de stock automáticas ----------
BA = C.get("broll_auto")
if BA:
    st = BA["fuente"] + ".tomas.json"
    if not os.path.exists(st): run([os.path.join(HERE, ".venv", "bin", "python"), os.path.join(HERE, "stock.py"), BA["fuente"]])
    T = json.load(open(st))["tramos"]; dur = BA.get("dur", .26); n = BA.get("n", 8)
    if "en" in BA: t0 = BA["en"]
    else:
        # la palabra clave (p. ej. el apellido) aunque Whisper la escriba un poco distinto
        clave = norm(BA.get("despues_de", "")); hit = [w for w in WS if clave and difflib.SequenceMatcher(None, clave, norm(w["word"])).ratio() >= .75]
        t0 = (hit[0]["end"] + .03) if hit else 1.0
        if not hit: print(f"⚠ broll_auto: no oí «{BA.get('despues_de')}»; las tomas empiezan en 1.0 s (pon \"en\": segundos)")
    # sin rebanadas: si un corte del armado cae a < 0.15 s del inicio o del final de la ráfaga, se pega al corte
    for bd in bounds[:-1]:
        if 0 < bd - t0 < .15: t0 = bd
    rnd = random.Random(os.path.basename(os.path.abspath(proj)))      # cada proyecto, otra combinación (repetible)
    completos = [t for t in T if not t["dividida"]]; divididos = [t for t in T if t["dividida"]]
    rnd.shuffle(completos); rnd.shuffle(divididos)
    elegidos = [t for t in completos + divididos if t["b"] - t["a"] >= dur + .02][:n]
    rnd.shuffle(elegidos)
    C["broll"] = []
    for k, t in enumerate(elegidos):
        desde = round(rnd.uniform(t["a"], t["b"] - dur), 3)
        C["broll"].append({"a": round(t0 + k * dur, 3), "b": round(t0 + (k + 1) * dur, 3), "fuente": BA["fuente"], "desde": desde})
    ult, t_ult = C["broll"][-1], elegidos[-1]; fin = ult["b"]
    for bd in bounds[:-1]:
        if 0 < fin - bd < .15: ult["b"] = bd                                   # acortar hasta el corte: siempre se puede
        elif 0 < bd - fin < .15:                                                # alargar hasta el corte: solo dentro de su tramo
            ult["desde"] = round(max(t_ult["a"], min(ult["desde"], t_ult["b"] - (bd - ult["a"]))), 3)
            if ult["desde"] + (bd - ult["a"]) <= t_ult["b"]: ult["b"] = bd
    print(f"tomas de stock: {len(C['broll'])} desde {t0:.2f}s ({sum(not t['dividida'] for t in elegidos)} a pantalla completa)")
if C.get("broll"):
    for k in ("broll", "flecha"):                     # stock_encima.py lee las tomas de proyecto.json
        if C.get(k) is not None: RAW[k] = C[k]
    json.dump(RAW, open(P("proyecto.json"), "w"), ensure_ascii=False, indent=1)
    os.replace(P("corte.mp4"), P("_corte_sin_broll.mp4"))
    run([os.path.join(HERE, ".venv", "bin", "python"), os.path.join(HERE, "stock_encima.py"), proj])

# ---------- 7. circulito (opcional; descartado en anuncios) ----------
if C.get("circulo"):
    base = P("_corte_sin_broll.mp4") if os.path.exists(P("_corte_sin_broll.mp4")) else P("corte.mp4")
    os.replace(P("corte.mp4"), P("_corte_con_broll.mp4"))
    ins, fb, prev = ["-i", P("_corte_con_broll.mp4"), "-i", base], [], "0:v"
    for k, r_ in enumerate(C["circulo"]):
        D = r_.get("d", 470); CX, CY = 540, r_.get("cy", 560)
        fs = cara_en(r_["a"], r_["b"])
        fx, fy, fw = (540, 700, 300) if not fs else (float(np.median([(f[1] + f[3]) / 2 for f in fs])), float(np.median([(f[2] + f[4]) / 2 for f in fs])), float(np.median([f[3] - f[1] for f in fs])))
        S = int(min(1080, max(400, fw * 2.6))); S -= S % 2
        x0 = int(min(1080 - S, max(0, fx - S / 2))); y0 = int(min(1920 - S, max(0, fy - S * .42)))
        m = np.zeros((D, D), np.uint8); cv2.circle(m, (D // 2, D // 2), D // 2 - 2, 255, -1, cv2.LINE_AA); cv2.imwrite(P(f"_mask{k}.png"), m)
        ring = np.zeros((D + 24, D + 24, 4), np.uint8); cv2.circle(ring, ((D + 24) // 2, (D + 24) // 2), D // 2 + 4, (255, 255, 255, 255), 9, cv2.LINE_AA); cv2.imwrite(P(f"_ring{k}.png"), ring)
        n_ = len(ins) // 2; ins += ["-loop", "1", "-i", P(f"_mask{k}.png"), "-loop", "1", "-i", P(f"_ring{k}.png")]
        a_, b_ = r_["a"], r_["b"]
        fb.append(f"[1:v]crop={S}:{S}:{x0}:{y0},scale={D}:{D},format=yuva420p[p{k}];[{n_}:v]format=gray,scale={D}:{D}[m{k}];[p{k}][m{k}]alphamerge[pc{k}]")
        fb.append(f"[{prev}][pc{k}]overlay={CX - D // 2}:{CY - D // 2}:shortest=1:enable='between(t,{a_},{b_})'[q{k}];[q{k}][{n_ + 1}:v]overlay={CX - (D + 24) // 2}:{CY - (D + 24) // 2}:shortest=1:enable='between(t,{a_},{b_})'[o{k}]"); prev = f"o{k}"
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fb), "-map", f"[{prev}]", "-map", "0:a", "-c:v", "libx264", "-crf", "16",
         "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", P("corte.mp4")])

# ---------- 8. flecha en la palabra "clic" ----------
if "flecha" in C and not C["flecha"].get("fijo"):          # "flecha": {} = automática (ojo: {} es falso en Python)
    hit = [w for w in WS if norm(w["word"]) in ("clic", "click", "clik", "boton", "enlace", "link")]
    if hit: C["flecha"]["en"] = round(hit[-1]["start"] - .02, 2); print(f"flecha en «{hit[-1]['word'].strip()}» {C['flecha']['en']}s")
    else: print("⚠ no encontré «clic» para la flecha: pon \"flecha\": {\"en\": segundos, \"fijo\": true}")
for k in ("broll", "flecha"):
    if C.get(k) is not None: RAW[k] = C[k]
json.dump(RAW, open(P("proyecto.json"), "w"), ensure_ascii=False, indent=1)

# ---------- 9. cara por corte (lado del texto en horizontal), a partir de caras.json ----------
B = [0] + bounds; out = []
for a, b in zip(B, B[1:]):
    fs = cara_en(a + .1, b - .1); rec = {"a": a, "b": b}
    if fs:
        rec.update(left=int(min(f[1] for f in fs)), right=int(max(f[3] for f in fs)),
                   cx=round(float(np.mean([(f[1] + f[3]) / 2 for f in fs])) / W, 3), cy=round(float(np.mean([(f[2] + f[4]) / 2 for f in fs])) / H, 3))
    out.append(rec)
json.dump(out, open(P("faces.json"), "w"))
print("-> escribe pages.txt (ver README) y corre alinear.py")
