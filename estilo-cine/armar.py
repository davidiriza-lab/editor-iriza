"""Arma cine.json desde un plan declarativo: python3 estilo-cine/armar.py proyectos/<n> [--plan otro.json] [--seco]

Lee proyectos/<n>/plan.json + voz/palabras.json (+ corte/mapa.json o tiempos.json, corte/caras.json, metodo.json, cuadros/) y
escribe cine.json (y voz/palabras.json con los inicios ajustados a los cortes; el original queda en voz/palabras_orig.json).
--seco: no escribe nada, solo muestra el resumen. Después: `node estilo-cine/render.mjs proyectos/<n> --validar` y revisar.py.
La lógica vive en estilo-cine/armado.py; aquí solo está el formato.

FORMATO DE plan.json (todo es opcional salvo "escenas"; lo que falta lo pone la receta)
  "receta"     "anuncio-por-frases" (4-nov: subtítulo por frase) · "cine-e" (10-nov: línea chica + palabra grande)
               · "escalon" (11/12-nov: barra inclinada, piezas de tiempos.json). Ver RECETAS en armado.py.
  "nombre", "handle"   por defecto config/kit.json        "salida" o "archivo" (→ salida/<archivo>.mp4)      "cola"
  "cine"       claves de la raíz del cine.json que pasan TAL CUAL: acento, acentoTexto, paleta, pop, subtitulo, suave,
               apretado, limpio, imagenes, fuenteGrande, sfx_auto, hdr_ok… (también valen sueltas en la raíz del plan,
               como en planes.py: el armador pasa toda clave que render.mjs lea como cfg.X)
  "persona"    {cuadros, mascaras, crudos, fondo, bajar, zoomAlt} · n se cuenta en cuadros/ (o en el corte si se limpió)
               · false = video sin persona.  fps: de metodo.json o corte/cam.mov, nunca a mano.
  "texto"      estilo de los subtítulos (cada escena puede cambiarlo con su propio "texto"):
                 estilo   frase · frase-entera · etiqueta · cinetico · escalon · ocultos
                 y, resaltar [palabras], contorno [palabras], mostrar {"40": "cuarenta"}, enlace [palabras de enlace],
                 capitalizar ["Instagram", "tu Negocio"] (mayúscula en las palabras escritas así),
                 mayusculaInicio, sombra, etiqueta {fondo, color, size…}, maxPal, maxLetras, forma linea|chica-grande,
                 suelta (palabra suelta → línea chica del siguiente), oSuelta, grupo {claves extra en cada grupo: tinta, lim…}
  "frases"     guion exacto (opcional): frases palabra por palabra igual que la voz; se verifica y marca dónde acaba
               cada frase. "oido_distinto": palabras que la voz dice distinto.   "y", "resaltar": atajos de texto.
  "textoHasta" ancla desde la cual la voz queda sin subtítulo (p. ej. la tarjeta final la dice)
  "piezas"     "mapa" (corte/mapa.json) · "tiempos" (tiempos.json) · "auto"
  "alinear"    {margen, max, escenas}: la palabra que abre una pieza empieza después del corte; una escena que empieza
               < 0.3 s después de un corte arranca EN el corte. false = no tocar palabras.json.
  "zoom"       de dónde salen los "cortes" del zoom alterno: "escenas" · "escenas_persona" · "piezas" · "internos"
  "encuadre"   {caraY: auto|n, caraH: auto|n, min, minH, faltan: anterior|{cx,cy,h}, sinEncuadre [piezas], margenFinal}
               un solo encuadre por video (caras por tramo de corte/caras.json) · false = sin caras
  "base"       claves por defecto de cada escena con voz ({"visual": "persona", "tema": "oscuro"}) · "forzar": se imponen
               · "base_visual" {"pizarra": {"vig": .06}}: por defecto según el visual
  "escenas"    lista en orden. Con "desde" (ancla) la escena se lleva las palabras hasta la siguiente con "desde";
               sin "desde" lleva "inicio" y va sin texto (tarjeta final). Claves del armador: desde, texto, y,
               ocultar [["@a", "@b"]] (["@a"] = hasta el fin de la escena), sinSub, grupos (a mano, se usan tal cual).
               TODO lo demás (visual, trans, capas, imp, pant, cap, gigantes, fechaHero, cierre…) pasa tal cual al
               cine.json con sus anclas convertidas a segundos: el armador no necesita entender cada capa.
  "sfx"        [{f: "boom.mp3" (de estilo-cine/sfx) o ruta, en: ancla, pico, vol, repite, cada}] · avisa si pisa
               el final de una frase.  "sfx_cambio": {f, desfase, pico, vol} un efecto en cada cambio de visual.
  "musica"     {archivo, desde, vol, vol_drop, silencio: [anclas], drop: ancla, golpe: s} · con "golpe" (segundo de la
               canción donde pega) se calcula "desde" para que caiga en "drop".

ANCLAS (cualquier texto que empiece con @, en cualquier nivel de la escena, de sfx y de musica; no distinguen mayúsculas
ni acentos): "@palabra" inicio · "#2" la segunda vez · "$" final de la palabra · "+0.3"/"-0.1" segundos · "@.palabra"
contando desde el inicio de la escena · "@[pieza]" primera palabra de la pieza (nombre de tiempos.json o número de
corte/mapa.json) · "@[pieza]palabra#2" contando desde la pieza · "@[pieza].ini" / ".fin" inicio de la pieza / fin de su voz
· "@fin" final de la voz · "@@texto" un texto que empieza con @. En "desde" también vale un número de segundos.

EJEMPLO MÍNIMO
  {"receta": "escalon", "salida": "salida/Video editado - X.mp4", "cola": 2.6,
   "cine": {"acento": "#FFD000", "paleta": "blanca", "pop": {"modo": "escalon", "activo": "#FFD000"}},
   "musica": {"archivo": "audio/cancion.mp3", "golpe": 15.62, "drop": "@[gancho]juego", "vol": 0.17},
   "escenas": [
     {"desde": "@[gancho]", "imp": {"golpes": [{"en": "@.enjaulado+0.27", "k": 1}]}},
     {"desde": "@[fecha]", "texto": {"estilo": "ocultos"}, "fechaHero": {"en": "@[fecha]", "jueves": "@.jueves"}},
     {"inicio": "@fin+0.12", "visual": "cierreClaro", "tema": "claro", "cierre": {"titulo": ["…"]}}],
   "sfx": [{"f": "boom.mp3", "en": "@.enjaulado+0.27", "vol": 0.55}]}

PASAR UN ARMADOR VIEJO A plan.json: elegir la receta más parecida; copiar el bloque cfg a "cine" (sin fps, persona.n,
caras ni cortes: se calculan); una escena por cada escena del armador con su "desde" (la palabra o la pieza donde empieza)
y sus capas tal cual, cambiando cada a(…)/w(…) por su ancla; comprobar con un diff de JSON contra el cine.json viejo.
Ejemplos verificados: plantillas/anuncio-por-frases (planes.py = plan con receta anuncio-por-frases), README de estilo-cine.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import armado  # noqa: E402

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or args[0].startswith('-'): sys.exit(__doc__)
    proy = os.path.abspath(args[0])
    fplan = args[args.index('--plan') + 1] if '--plan' in args else os.path.join(proy, 'plan.json')
    if not os.path.exists(fplan): sys.exit(f'✗ no existe {fplan} (ver el formato: python3 estilo-cine/armar.py)')
    with open(fplan) as h: plan = json.load(h)
    seco = '--seco' in args
    cfg = armado.armar(proy, plan, escribir=not seco)
    print(f"{'(en seco) ' if seco else '✓ cine.json · '}" + '\n'.join(armado.resumen(cfg)))
