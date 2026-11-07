"""Revisa y corrige los cortes ANTES de armar (sobre el audio limpio del video original).

Uso:  .venv/bin/python cortes.py <proyecto> [--aplicar]

Para cada corte de proyecto.json -> "cortes":
  1. Bordes: si la voz sigue pegada al inicio o al final (p. ej. la "-gía" de "tecnología" tras la oclusiva), mueve el borde
     hasta el silencio real (≥ 0.18 s) + 0.1 s de aire. Máximo 0.6 s; si no hay silencio, avisa.
  2. Pausas: las pausas internas más largas que `pausa_max` (plantilla.json, 0.35 s) se recortan partiendo el corte.
     Los cortes en proyecto.json -> "intactos" (índices) no se tocan: silencios a propósito (silla vacía, alguien que se sienta).
  3. Doble revisión de palabras: transcribe el corte exacto y el mismo con 0.5 s de más a cada lado; si la primera o la última
     palabra cambia (p. ej. "tecnolo" vs "tecnología"), el corte se come una palabra → avisa.
  4. Volumen: un corte mucho más bajo que los demás (≥ 6 dB) suele ser la voz del director o de alguien fuera de cámara → avisa.
Escribe revision_cortes.json (lo lee plan.py). Con --aplicar guarda los cortes nuevos y corre broll/flecha manuales.
"""
import sys, os, json, re, tempfile, unicodedata
import numpy as np
import conf

proj = sys.argv[1]; P = lambda f: os.path.join(proj, f)
C = conf.cargar(proj); TMP = tempfile.mkdtemp()
H, SIL, AIRE, MAX = 0.01, 0.18, 0.1, 0.6
PMAX = C.get("pausa_max", .35); INTACTOS = set(C.get("intactos", []))
norm = lambda s: re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn"))


def silencio(v, i, paso):
    k, run = i, 0
    for _ in range(int((MAX + SIL) / H)):
        if k < 0 or k >= len(v): return k
        run = run + 1 if not v[k] else 0
        if run >= int(SIL / H): return k - paso * (run - 1)
        k += paso
    return None


def palabras(src, a, b):
    w = os.path.join(TMP, "t.wav"); conf.wav_tramo(src, a, b, w)
    return [x for x in conf.transcribir(w, vocabulario=C.get("vocabulario", ""))["text"].split() if norm(x)]


nuevos, rev, nuevos_intactos = [], [], []
for ci, c in enumerate(C["cortes"]):
    src = conf.fuente_de(C, c); e, thr = conf.energia(src); v = e > thr; a, b = c[0], c[1]; av = []
    # 1. bordes
    s = silencio(v, int((b - AIRE) / H), 1)                # desde b − aire: si ya estaba bien, no se mueve (idempotente)
    b2 = b if s is None else max(b, round(s * H + AIRE, 3))
    if s is None: av.append("no hay silencio después del final (la voz sigue)")
    elif b2 - b > MAX: av.append(f"la voz sigue {b2 - b:.2f}s después del final"); b2 = b
    s = silencio(v, int((a + AIRE - .04) / H), -1)
    a2 = a if s is None else min(a, round((s + 1) * H - AIRE + .04, 3))
    if s is None: av.append("no hay silencio antes del inicio")
    elif a - a2 > MAX: av.append(f"la voz empieza {a - a2:.2f}s antes del inicio"); a2 = a
    a2 = max(0, a2)
    # solo se alarga sobre voz parecida a la del corte: una voz ≥ 6 dB más baja (director, cuenta regresiva) no es de la persona
    nivel = lambda x, y: float(np.percentile(e[int(x / H):max(int(x / H) + 1, int(y / H))], 80))
    base_ = nivel(a, b)
    if a - a2 > .08 and nivel(a2, a) < base_ - 6: av.append(f"no alargo el inicio: antes suena otra voz más baja ({nivel(a2, a):.0f} dB)"); a2 = a
    if b2 - b > .08 and nivel(b, b2) < base_ - 6: av.append(f"no alargo el final: después suena otra voz más baja ({nivel(b, b2):.0f} dB)"); b2 = b
    if b2 - b > .08: av.append(f"final movido +{b2 - b:.2f}s: la voz seguía (palabra cortada)")
    if a - a2 > .08: av.append(f"inicio movido −{a - a2:.2f}s: la voz ya había empezado")
    # 2. pausas internas > pausa_max → partir
    seg = v[int(a2 / H):int(b2 / H)] if ci not in INTACTOS else []; partes, ini, run = [], a2, 0
    for i, x in enumerate(seg):
        if not x: run += 1; continue
        if run * H > PMAX + .15:                           # solo si de verdad sobra: cada recorte es un corte más
            fin_voz = a2 + (i - run) * H; vuelve = a2 + i * H
            partes.append([round(ini, 3), round(fin_voz + PMAX / 2, 3)]); ini = vuelve - PMAX / 2
            av.append(f"pausa de {run * H:.2f}s en {fin_voz:.2f}s → recortada a {PMAX:.2f}s")
        run = 0
    partes.append([round(ini, 3), b2])
    # 3. doble revisión de palabras en los bordes
    exacto = palabras(src, a2, b2); amplio = palabras(src, max(0, a2 - .5), b2 + .5)
    letras = lambda xs: [norm(x) for x in xs if any(c.isalpha() for c in x)]   # Whisper inventa «1.» o «…» en las orillas
    ex, am = letras(exacto), letras(amplio)
    if ex and am:
        if ex[-1] not in am:
            av.append(f"⚠ la última palabra «{exacto[-1]}» suena cortada (con más audio se oye «{' '.join(amplio[-3:])}»)")
        if ex[0] not in am:
            av.append(f"⚠ la primera palabra «{exacto[0]}» suena cortada (con más audio se oye «{' '.join(amplio[:3])}»)")
    # 4. volumen del corte (p80 de la voz)
    voz = e[int(a2 / H):int(b2 / H)]; nivel = float(np.percentile(voz[voz > thr], 80)) if (voz > thr).any() else -60
    rev.append({"i": ci, "fuente": os.path.basename(src), "antes": [a, b], "despues": partes, "texto": " ".join(exacto),
                "nivel_db": round(nivel, 1), "avisos": av})
    if ci in INTACTOS: nuevos_intactos.append(len(nuevos))
    for p_ in partes: nuevos.append(p_ + c[2:])

med = float(np.median([r["nivel_db"] for r in rev]))
for r in rev:
    if r["nivel_db"] < med - 6:
        r["avisos"].append(f"⚠ {med - r['nivel_db']:.0f} dB más bajo que los demás: ¿es la voz del director o de alguien fuera de cámara? Recomiendo quitar este pedazo")
json.dump(rev, open(P("revision_cortes.json"), "w"), ensure_ascii=False, indent=1)

for r in rev:
    d = " + ".join(f"{x[0]:.2f}-{x[1]:.2f}" for x in r["despues"])
    print(f"{r['i']:2d} {r['fuente'][-14:]:14s} {r['antes'][0]:7.2f}-{r['antes'][1]:7.2f} → {d}   [{r['nivel_db']} dB] «{r['texto']}»")
    for x in r["avisos"]: print("      ", x)

if "--aplicar" in sys.argv:
    # tiempo del armado viejo → nuevo, pasando por el tiempo del video original (sirve aunque un corte se haya partido)
    O = np.cumsum([0] + [c[1] - c[0] for c in C["cortes"]]); N = np.cumsum([0] + [c[1] - c[0] for c in nuevos])
    def mapa(t):
        i = min(int(np.searchsorted(O, t, side="right") - 1), len(C["cortes"]) - 1); c = C["cortes"][i]
        src, s = conf.fuente_de(C, c), c[0] + (t - O[i])
        cand = [j for j, n in enumerate(nuevos) if conf.fuente_de(C, n) == src]
        j = min(cand, key=lambda j: 0 if nuevos[j][0] <= s <= nuevos[j][1] else min(abs(s - nuevos[j][0]), abs(s - nuevos[j][1])))
        return round(float(N[j] + min(max(s, nuevos[j][0]), nuevos[j][1]) - nuevos[j][0]), 3)
    for br in C.get("broll", []):
        d = br["b"] - br["a"]; br["a"] = mapa(br["a"]); br["b"] = round(br["a"] + d, 3)
    if C.get("flecha") and isinstance(C["flecha"].get("en"), (int, float)): C["flecha"]["en"] = mapa(C["flecha"]["en"])
    C["cortes"] = nuevos
    if INTACTOS: C["intactos"] = nuevos_intactos
    conf.guardar(proj, C); print(f"✓ {len(nuevos)} cortes guardados")
