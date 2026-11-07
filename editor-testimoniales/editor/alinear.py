"""Paso 3 — alinear los subtítulos escritos a mano con los tiempos de cada palabra.

Uso:  .venv/bin/python alinear.py <carpeta_proyecto>

Lee pages.txt + words.json y genera pages.json (frases con tiempo de cada palabra).

Formato de pages.txt (una frase por renglón; las líneas se separan con " / "):
  s: línea chica (Helvetica)     B: palabras clave gigantes (League Gothic)     i: itálica serif
  [palabras] = caja terracota que barre      {palabras} = píldora terracota
  palabra@12.34 = fuerza el tiempo (s del armado) cuando Whisper se equivoca o fusiona frases
  al final del renglón:  #panel = panel claro a pantalla completa (el B se vuelve el número/titular gigante)
                         #card  = tarjeta de perfil de Instagram debajo del texto (proyecto.json -> "tarjeta")
Reglas que funcionan: renglones s: de ≤ 22–26 letras, 2–4 líneas por frase, 1 bloque B por frase,
corregir lo que Whisper escribe mal (nombres, "Apellido").
"""
import sys, os, json, re, unicodedata, difflib, subprocess
import conf

proj = sys.argv[1]
P = lambda f: os.path.join(proj, f)
C = conf.cargar(proj)
MINP = C.get("min_pagina", .9)
EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]")      # no hay fuente para dibujarlos
CJ = json.load(open(P("cortes.json"))) if os.path.exists(P("cortes.json")) else {}
d = json.load(open(P("words.json")))
W = [(w["word"].strip(), w["start"], w["end"]) for s in d["segments"] for w in s["words"]]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", P("corte.mp4")], capture_output=True, text=True).stdout)
norm = lambda s: re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn"))

pages, toks = [], []
quitados = []
for fila, ln in enumerate(open(P("pages.txt"))):
    if EMOJI.search(ln): quitados += EMOJI.findall(ln); ln = EMOJI.sub("", ln)
    ln = ln.strip()
    if not ln or ln.startswith("#"): continue
    tag = None; m = re.search(r"\s#(\w+)$", ln)
    if m: tag = m.group(1); ln = ln[:m.start()]
    page = {"lines": [], "tag": tag, "filas": [fila]}
    for part in ln.split(" / "):
        st, txt = part.split(":", 1); line = {"st": st.strip(), "w": []}; mode = None
        for raw in txt.strip().split():
            if not raw.strip("[]{}"): continue
            if raw.startswith("["): mode = "box"; raw = raw[1:]
            if raw.startswith("{"): mode = "pill"; raw = raw[1:]
            dec = mode
            if "]" in raw: raw = raw.replace("]", ""); mode = None
            if raw.endswith("}"): raw = raw[:-1]; mode = None
            force = None
            if "@" in raw: raw, force = raw.split("@"); force = float(force)
            w = {"t": raw, "dec": dec, "force": force}; line["w"].append(w); toks.append(w)
        page["lines"].append(line)
    pages.append(page)

sm = difflib.SequenceMatcher(None, [norm(w["t"]) for w in toks], [norm(w[0]) for w in W], autojunk=False)
for a, b, n in sm.get_matching_blocks():
    for k in range(n): toks[a + k]["s"] = W[b + k][1]; toks[a + k]["e"] = W[b + k][2]
for w in toks:
    if w["force"] is not None: w["s"] = w["force"]; w["e"] = w["force"] + .3
idx = [i for i, w in enumerate(toks) if "s" in w]
miss = []
for i, w in enumerate(toks):
    if "s" in w: continue
    miss.append(w["t"])
    p = max([j for j in idx if j < i], default=None); q = min([j for j in idx if j > i], default=None)
    w["s"] = toks[q]["s"] - .2 * (q - i) if p is None else toks[p]["s"] + .25 * (i - p) if q is None else toks[p]["s"] + (toks[q]["s"] - toks[p]["s"]) * (i - p) / (q - p)
    w["e"] = w["s"] + .25
for i in range(1, len(toks)):
    if toks[i]["s"] < toks[i - 1]["s"]: toks[i]["s"] = toks[i - 1]["s"] + .05
for p in pages:
    ws = [w for l in p["lines"] for w in l["w"]]; p["start"] = ws[0]["s"]; p["last"] = max(w["e"] for w in ws)
# fin de la voz: el último subtítulo se va con el fundido final (la cola ya viene en corte.mp4 como imagen real)
fin = dur - .1 if CJ.get("cola_real") is not None else dur + C.get("cola", 1.6) - .16
def fines():
    for i, p in enumerate(pages):
        p["end"] = min(pages[i + 1]["start"] - .08, p["last"] + 1.4) if i + 1 < len(pages) else fin
fines()
# ningún subtítulo dura menos de min_pagina: primero entra antes (sus palabras se adelantan), si no alcanza se une al siguiente
ajustes = []
i = 0
while i < len(pages):
    p = pages[i]
    if p["end"] - p["start"] < MINP:
        tope = pages[i - 1]["last"] + .12 if i else 0
        nuevo = max(tope, p["end"] - MINP)
        if nuevo < p["start"] - .01:
            delta = p["start"] - nuevo
            for l in p["lines"]:
                for w in l["w"]: w["s"] = max(nuevo, w["s"] - delta)
            p["start"] = nuevo; ajustes.append(f"frase {i} entra {delta:.2f}s antes")
            if i: pages[i - 1]["end"] = min(pages[i - 1]["end"], nuevo - .08)
        if p["end"] - p["start"] < MINP - .05 and i + 1 < len(pages) and len(p["lines"]) + len(pages[i + 1]["lines"]) <= 4:
            q = pages.pop(i + 1); p["lines"] += q["lines"]; p["last"] = q["last"]; p["tag"] = p["tag"] or q["tag"]; p["filas"] += q["filas"]
            ajustes.append(f"frase {i} muy corta → unida con la siguiente"); fines(); continue
        if p["end"] - p["start"] < MINP - .05 and i + 1 < len(pages):
            # último recurso: la frase siguiente espera (máx. 0.4 s) para que esta alcance a leerse
            q = pages[i + 1]; espera = min(.4, MINP - (p["end"] - p["start"]))
            q["start"] += espera; p["end"] += espera
            for l in q["lines"]:
                for w in l["w"]: w["s"] = max(w["s"], q["start"])
            ajustes.append(f"frase {i} muy corta → la siguiente espera {espera:.2f}s")
    i += 1
for p in pages:
    for l in p["lines"]:
        for w in l["w"]: w.pop("force", None)
json.dump(pages, open(P("pages.json"), "w"), ensure_ascii=False)
print(f"{len(pages)} frases · palabras con tiempo interpolado: {miss or 'ninguna'}")
for a in ajustes: print("  ·", a)
if quitados: print("  ⚠ quité emojis (no se pueden dibujar):", " ".join(quitados))
for i, p in enumerate(pages):
    print(f"{i:2d} {p['start']:6.2f}-{p['end']:6.2f} {p['tag'] or '':6s}", " / ".join(" ".join(w["t"] for w in l["w"]) for l in p["lines"]))
