"""Un solo comando para editar, con paradas donde la persona tiene que revisar.

Uso (desde editor/):
  .venv/bin/python editar.py <proyecto> plan       1) revisa cortes (bordes, pausas, doble transcripción, volumen) → PLAN.md
                                                      → Claude MUESTRA EL PLAN TAL CUAL a la persona y espera su "sí"
  .venv/bin/python editar.py <proyecto> armar      2) aplica los cortes y arma (HDR, encuadre, voz pareja, stock, flecha, caras)
                                                      → Claude escribe pages.txt con corte.txt
  .venv/bin/python editar.py <proyecto> terminar   3) subtítulos → acomodo sin tapar la cara (parte frases si no caben) →
                                                      tomas sin caras bajo el texto → contraste → revisión de cortes → render → mezcla → doble revisión del audio →
                                                      revisión final cuadro por cuadro (revisar_final.py + hojas de contacto)
Se detiene en cuanto algo falla y dice qué. Nada se entrega sin pasar las revisiones.
"""
import sys, os, subprocess
os.environ["NO_ENTREGAR"] = "1"          # mezcla.py no copia a la salida: se entrega al final, solo si todo pasó
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import conf

HERE = os.path.dirname(os.path.abspath(__file__)); PY = os.path.join(HERE, ".venv", "bin", "python")
proj = os.path.abspath(sys.argv[1]); etapa = sys.argv[2] if len(sys.argv) > 2 else "plan"
P = lambda f: os.path.join(proj, f)

def paso(nombre, cmd, puede_fallar=False):
    print(f"\n▸ {nombre}", flush=True)
    r = subprocess.run(cmd, cwd=HERE)
    if r.returncode and not puede_fallar: sys.exit(f"\n✗ se detuvo en: {nombre}. Corrige lo de arriba y vuelve a correr `editar.py {sys.argv[1]} {etapa}`.")
    return r.returncode

py = lambda s, *a: [PY, os.path.join(HERE, s), proj, *a]
node = lambda *a: ["node", os.path.join(HERE, "render.mjs"), proj, *a]

if etapa == "plan":
    paso("revisar cortes (bordes, pausas, doble transcripción, volumen)", py("cortes.py"))
    paso("plan para la persona", py("plan.py"))
    print("\n→ Muestra el plan TAL CUAL a la persona y espera su \"sí\" o sus correcciones. Luego: editar.py <p> armar")

elif etapa == "armar":
    paso("aplicar cortes", py("cortes.py", "--aplicar"))
    paso("armar", py("armar.py"))
    print(open(P("corte.txt")).read())
    print("→ Escribe pages.txt (ver README) y corre: editar.py <p> terminar")

elif etapa == "terminar":
    if not os.path.exists(P("pages.txt")): sys.exit("✗ falta pages.txt")
    for vuelta in range(1, 6):
        paso("alinear subtítulos", py("alinear.py"))
        paso("acomodo de textos", node("layout"))
        if paso("revisar textos (cara, zona segura, flecha)", py("revisar_texto.py"), puede_fallar=True) == 0: break
        r = paso("partir frases que no caben", py("partir.py"), puede_fallar=True)
        if r == 1: sys.exit("\n✗ la revisión de textos falló por algo que no se arregla partiendo frases (ver el aviso arriba)")
        if r == 2: sys.exit("\n✗ hay textos de una sola línea que no caben sin tapar la cara: acórtalos en pages.txt")
    else: sys.exit("\n✗ después de 5 vueltas sigue habiendo textos encima de la cara")
    paso("tomas de stock sin caras debajo de los subtítulos", py("stock_caras.py"))
    paso("contraste del fondo", py("contraste.py"))
    paso("revisar cambios de escena y tomas de stock", py("revisar_cortes.py"))
    paso("render + mezcla", node())
    paso("doble revisión del audio (uniones y subtítulos vs lo que se oye)", py("revisar_audio.py"))
    paso("revisión final cuadro por cuadro del video terminado", py("revisar_final.py"))
    out = conf.entregar(proj)
    if not out: sys.exit("\n✗ el video pasó todas las revisiones pero no se pudo copiar a la salida")
    print(f"\n✓ listo, revisado y entregado en: {out}\n  Mira las hojas de revision_final/ (marco rojo = problema) antes de mandarlo.")
else:
    sys.exit(__doc__)
