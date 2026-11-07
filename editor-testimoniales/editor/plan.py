"""Plan de edición para la PERSONA dueña del video: qué se va a hacer, paso a paso, y qué podría estar mal.

Uso:  .venv/bin/python plan.py <proyecto>          (después de cortes.py; escribe PLAN.md y lo imprime)
Claude debe mostrar este texto TAL CUAL a la persona antes de armar/renderizar y esperar su "sí" o sus correcciones.
"""
import sys, os, json, subprocess
import conf

proj = sys.argv[1]; P = lambda f: os.path.join(proj, f)
C = conf.cargar(proj); RAW = json.load(open(P("proyecto.json")))
rev = json.load(open(P("revision_cortes.json"))) if os.path.exists(P("revision_cortes.json")) else []
probe = lambda f, *e: subprocess.run(["ffprobe", "-v", "error", *e, "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip()
L, avisos = [], []
w = L.append

dur = sum(b - a for r in rev for a, b in r["despues"]) if rev else sum(c[1] - c[0] for c in C["cortes"])
dur += C.get("cola", .6)
w(f"# Plan de edición — {C.get('nombre', os.path.basename(os.path.abspath(proj)))}\n")
w("Esto es lo que voy a hacer con tu video. Léelo y dime si algo está mal **antes** de que lo arme; con un \"sí\" sigo.\n")

# fuentes
fuentes = [C["fuente"]] + sorted({c[2] for c in C["cortes"] if len(c) > 2} - {C["fuente"]})
w("## 1. Tus videos")
for f in fuentes:
    wh = probe(f, "-select_streams", "v:0", "-show_entries", "stream=width,height,color_transfer").split("\n")[0].split(",")
    hdr = len(wh) > 2 and wh[2] in ("arib-std-b67", "smpte2084")
    orient = "horizontal" if int(wh[0]) > int(wh[1]) else "vertical"
    extra = []
    if hdr: extra.append("viene en HDR → lo paso a color normal (Rec.709) para que no se vea lavado")
    if orient == "horizontal" and C.get("vertical"): extra.append("es horizontal → lo recorto a vertical siguiendo tu cara en cada corte")
    w(f"- `{os.path.basename(f)}` ({wh[0]}×{wh[1]}, {orient}){': ' + '; '.join(extra) if extra else ''}")
salida = C.get("salida", "final.mp4")
w(f"\nSale en **{'vertical 1080×1920 (Reels/TikTok)' if C.get('vertical') else 'horizontal 1920×1080'}** en: `{salida}`\n")

# cortes
w("## 2. Qué partes uso (en este orden)")
w("| # | De | Entra → sale | Dura | Lo que dice |")
w("|---|---|---|---|---|")
n = 0
for r in rev:
    for a, b in r["despues"]:
        n += 1; w(f"| {n} | {r['fuente'][-12:]} | {a:.2f} → {b:.2f} s | {b - a:.1f} s | {r['texto'] if (a, b) == tuple(r['despues'][0]) else '(sigue)'} |")
    for x in r["avisos"]:
        if x.startswith("⚠") or "director" in x or "palabra cortada" in x: avisos.append(f"Parte {r['i'] + 1}: {x.lstrip('⚠ ')}")
pausas = [x for r in rev for x in r["avisos"] if x.startswith("pausa")]
bordes = [x for r in rev for x in r["avisos"] if x.startswith(("final movido", "inicio movido"))]
w("")
w(f"- **Pausas:** ninguna pausa dura más de {C.get('pausa_max', .35):.2f} s; recorto {len(pausas)} pausas largas.")
w(f"- **Palabras cortadas:** revisé cada inicio y final contra el audio (dos veces: el corte exacto y con medio segundo de más). "
  + (f"Moví {len(bordes)} bordes para no comerme palabras." if bordes else "Ninguno se come palabras."))
dm = C.get("duracion_max")
w(f"- **Duración:** ≈ {dur:.1f} s" + (f" (máximo que pediste: {dm} s)" if dm else " (dime si hay un máximo)") + "\n")
if dm and dur > dm: avisos.append(f"El video dura {dur:.1f} s y el máximo es {dm} s: dime qué parte quito (o la elijo yo)")

# voz, stock, subtítulos, flecha, música, final
w("## 3. Cómo lo voy a editar, paso a paso")
k = 1
def paso(t):
    global k; w(f"{k}. {t}"); k += 1
paso("**Voz pareja:** cada parte se nivela para que el volumen no brinque entre cortes; el video final queda a "
     f"{C.get('lufs', -14)} LUFS (volumen estándar de redes).")
paso("**Transición en cada corte** (desenfoque rápido, sin zoom) para que no se vea el brinco.")
BA = C.get("broll_auto")
if BA:
    st = BA["fuente"] + ".tomas.json"; tinfo = ""
    if os.path.exists(st):
        T = json.load(open(st)); tinfo = f" (analicé el stock cuadro por cuadro: {len(T['tramos'])} tomas usables, {T['dividida_seg']:.1f} s vienen en pantalla dividida)"
    paso(f"**Tomas de stock:** {BA.get('n', 8)} tomas rápidas de {BA.get('dur', .26):.2f} s justo después de «{BA.get('despues_de', 'Apellido')}», "
         f"de `{os.path.basename(BA['fuente'])}`{tinfo}. Ninguna cruza un cambio de plano y cada video usa una combinación distinta.")
elif C.get("broll"): paso(f"**Tomas de stock:** {len(C['broll'])} tomas puestas a mano.")
paso("**Subtítulos** palabra por palabra (línea chica + palabras clave gigantes), y antes de colocarlos detecto tu cara en "
     "TODOS los fotogramas: el texto nunca te tapa la cara, siempre queda dentro de la zona segura de Instagram "
     "(no lo tapan el usuario, la descripción ni los botones) y ningún subtítulo dura menos de "
     f"{C.get('min_pagina', .9)} s en pantalla (si es más corto, aparece antes o se une al siguiente).")
if C.get("flecha"): paso("**Flecha animada hacia abajo** cuando dices «clic», señalando el botón del anuncio.")
mus = C.get("musica")
if C.get("sin_musica"): paso("**Sin música** (así lo pediste).")
elif mus and os.path.exists(mus if os.path.isabs(mus) else P(mus)):
    paso(f"**Música:** `{os.path.basename(mus)}`" + (" (carpeta: elijo una canción que no se haya usado en otro video)" if os.path.isdir(mus) else "")
         + ", suena desde el segundo 0 y baja cuando hablas.")
    avisos.append("Confirma que tu licencia de música permita usarla en anuncios pagados de esta marca.")
else:
    paso("**Música:** ⚠ no tengo música todavía.")
    avisos.append("Necesito música: pásame una carpeta con canciones o conecta un MCP de música (p. ej. Epidemic Sound). O dime \"sin música\".")
paso(f"**Final:** el video se desvanece justo cuando terminas de hablar ({C.get('cola', .6):.1f} s de imagen real, sin cuadro congelado).")
paso("**Revisión automática antes de entregarte:** texto vs cara en cada fotograma, zona segura, tomas de stock vs cambios de plano, "
     "y doble transcripción del audio sin música (uniones y subtítulos contra lo que realmente dices).")

w("\n## 4. Lo que necesito que revises")
if avisos:
    for a in avisos: w(f"- ⚠ {a}")
else: w("- Nada raro: si el orden y las partes de la tabla están bien, dime \"sí\" y lo armo.")
texto = "\n".join(L)
open(P("PLAN.md"), "w").write(texto + "\n"); print(texto)
