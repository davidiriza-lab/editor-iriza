"""Doble revisión del texto con el audio LIMPIO (sin música): palabras cortadas en las uniones y subtítulos vs lo que se oye.

Uso:  .venv/bin/python revisar_audio.py <proyecto>       (después de armar.py y alinear.py)
  1. Cada corte del armado se transcribe solo y otra vez con 0.6 s de más a cada lado: si la primera o la última palabra
     cambia, la unión se la comió.
  2. El armado completo se transcribe con la voz sola y se compara con los subtítulos (pages.json): palabras que el
     subtítulo dice y no se oyen, o al revés (Whisper sobre el video con música se equivoca; por eso se hace sobre la voz).
Sale con código 1 si algo falla.
"""
import sys, os, json, re, difflib, tempfile, unicodedata
import conf

proj = sys.argv[1]; P = lambda f: os.path.join(proj, f)
norm = lambda s: re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn"))
NUM = {"1": "uno", "2": "dos", "3": "tres", "4": "cuatro", "5": "cinco", "7": "siete", "10": "diez", "#1": "numerouno"}
pal = lambda txt: [NUM.get(x, norm(x)) for x in txt.replace("#1", " numero uno ").split() if norm(x) or x in NUM]
VOC = conf.cargar(proj).get("vocabulario", "")
CJ = json.load(open(P("cortes.json"))); B = [0] + CJ["fronteras"]; fin_voz = CJ.get("fin_voz", B[-1])
TMP = tempfile.mkdtemp(); src = P("corte.mp4"); mal = []

# 1. uniones
for k, (a, b) in enumerate(zip(B, B[1:])):
    b = min(b, fin_voz + .05); w = os.path.join(TMP, "u.wav"); conf.wav_tramo(src, a, b, w)
    oido = pal(conf.transcribir(w, vocabulario=VOC)["text"])
    if not oido: mal.append(f"corte {k} ({a:.2f}-{b:.2f}s): no se oye nada"); continue
    w2 = os.path.join(TMP, "v.wav"); conf.wav_tramo(src, max(0, a - .6), min(B[-1], b + .6), w2)
    amplio = pal(conf.transcribir(w2, vocabulario=VOC)["text"])
    if oido[-1] not in amplio or oido[0] not in amplio:
        mal.append(f"unión del corte {k} ({a:.2f}-{b:.2f}s): se oye «{' '.join(oido[:2])} … {' '.join(oido[-2:])}», con más audio «{' '.join(amplio[-3:])}»")
print(f"  ✓ {len(B) - 1} uniones transcritas por separado") if not mal else None

# 2. subtítulos contra lo que se oye
w = os.path.join(TMP, "todo.wav"); conf.wav_tramo(src, 0, fin_voz + .1, w)
oido = pal(conf.transcribir(w, vocabulario=VOC)["text"])
subs = [NUM.get(x["t"], norm(x["t"])) for p in json.load(open(P("pages.json"))) for l in p["lines"] for x in l["w"]]
subs = [s for s in subs if s]
sm = difflib.SequenceMatcher(None, subs, oido, autojunk=False); avisos = []
parecido = lambda a, b: difflib.SequenceMatcher(None, a, b).ratio()
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == "equal": continue
    s, o = " ".join(subs[i1:i2]), " ".join(oido[j1:j2])
    if s.replace("numerouno", "numero uno") == o: continue
    if op == "replace" and i2 - i1 == j2 - j1 and all(parecido(a, b) >= .6 for a, b in zip(subs[i1:i2], oido[j1:j2])):
        avisos.append(f"subtítulo «{s}» y se oye «{o}» (¿Whisper lo escribió distinto o el subtítulo dice otra cosa? revísalo)"); continue
    mal.append(f"subtítulo «{s or '—'}» pero se oye «{o or '—'}»")
for a in avisos: print("  ·", a)
print(f"  ✓ subtítulos idénticos a lo que se oye ({len(subs)} palabras)") if not any(m.startswith("subtítulo") for m in mal) else None
for m in mal: print("  ⚠", m)
sys.exit(1 if mal else 0)
