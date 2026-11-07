"""Escaletas de los anuncios de este proyecto: una entrada de PLANES por video (la clave = carpeta del video).
Se arman con armar.py <clave>: subtítulo por frase y anclas @palabra#n (ver LEEME.md).

Cada plan lleva:
  frases     las frases del guion, palabra por palabra igual que la voz (armar.py lo verifica)
  escenas    lista de escenas; cada una arranca en `desde` (ancla) y elige un visual: persona (por defecto),
             pantalla, pizarra, split, franja, editorial…, más capas (gigantes, tachados, datos, capas)
  acento     color del marcatextos · subtitulo: estilo del subtítulo · resaltar: palabras que se marcan
Anclas: '@palabra' = inicio de la palabra · '#2' = segunda vez que aparece · '$' = final de la palabra ·
'+0.3' / '-0.1' = segundos de más o de menos · '@fin' = final de la voz. No distinguen mayúsculas ni acentos.
"""

# ---- PALETA (edítala para cada marca) ----
FONDO, FONDO2 = '#0B1D2E', '#1B3A54'        # fondo oscuro de las pantallas y su variante
ACENTO, ACENTO_T = '#B08D57', '#d6ac63'     # acento sobre fondo claro / sobre fondo oscuro
CLARO = '#F7F3F0'                            # fondo claro (marfil)
RAYAS = 'rgba(255,255,255,.045)'
ACENTO_G = ['#F8E6B8', '#DDB46B', '#A9782F']     # degradado metálico sobre fondo oscuro (de arriba a abajo); un color plano se ve opaco
ACENTO_G_C = ['#D4A85E', '#A9803F', '#73501C']   # el mismo degradado, más hondo para que contraste sobre fondo claro
FOCO = dict(color='rgba(56,104,152,.42)', y=.5, r=.62)   # foco de luz radial detrás del texto en las pantallas oscuras
HN = 'Helvetica Neue'      # sans gruesa de las palabras gigantes
IT = 'Instrument Italic'   # línea chica serif itálica

def flecha(en, color=ACENTO_T): return {'tipo': 'flecha-abajo', 'x': 540, 'y': 1400, 's': 76, 'en': en, 'color': color}
def chica(t, en, y, color='#fff', size=78, **k): return dict(t=t, en=en, y=y, size=size, fuente=IT, color=color, esp='0px', **k)
def grande(t, en, y, color='#fff', size=190, **k):
    g = {ACENTO_T: ACENTO_G, ACENTO: ACENTO_G_C}.get(color)
    return dict(t=t, en=en, y=y, size=size, fuente=HN, peso=800, color=color, esp='-5px', **({'degradado': g} if g else {}), **k)

import json as _json, os as _os
def F(k, *ini):
    """Frases desde la transcripción del corte: cada número es el índice de palabra donde empieza una frase.
    Útil cuando la persona dijo el guion con otras palabras: se parte su transcripción en lugar de copiar el guion."""
    W = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), k, 'voz', 'palabras.json')))
    lim = list(ini) + [len(W)]
    fr = [' '.join(w['t'] for w in W[a:b]) for a, b in zip(lim, lim[1:])]
    return [f[0].upper() + f[1:] if f[0].isalpha() else f[0] + f[1:2].upper() + f[2:] for f in fr]   # cada frase con mayúscula
def sellos(en, fin, items, y=1000, paso=None): return dict(en=en, fin=fin, estilo='sello', y=y, items=items, **({'paso': paso} if paso else {}))

# Palabra gigante detrás o arriba de la cabeza: serif itálica bold, mayúsculas y minúsculas, crema con sombra suave
# (acento claro en la palabra clave) y ARRIBA de la cabeza: y = coronilla − 40 px, para que al menos ⅔ de la palabra
# quede fuera de la cabeza. Nunca un color oscuro sobre fondo oscuro.
PF, CREMA, ACENTO_CL = 'Playfair Bold Italic', '#F6EFE4', '#F2D58E'
SOMBRA = dict(color='rgba(0,0,0,.55)', blur=36, y=6)
def detras(t, en, fin, size=175, color=CREMA, y=240): return dict(t=t, en=en, fin=fin, y=y, size=size, color=color, fuente=PF, peso=400, esp='0px', sombra=SOMBRA)
# Etiquetas: en lugar de sellos apilados o torcidos, una lista limpia (tarjeta clara, renglones alineados que entran uno por uno sin taparse)
def lista(en, fin, items, y=1010, **k): return dict(en=en, fin=fin, estilo='lista', y=y, items=items, **k)

# Pizarra: nodos oscuros con ícono, textos y líneas punteadas
def nodo(x, y, en, icono=None, t=None, r=110, **k): return dict(tipo='nodo', x=x, y=y, r=r, oscuro=FONDO, icono=icono, t=t, en=en, dur=.3, **k)
def txt(t, x, y, en, size=60, color=FONDO, peso=800, **k): return dict(tipo='texto', t=t, x=x, y=y, size=size, color=color, peso=peso, en=en, **k)

# Pasos numerados (fondo claro / oscuro alterno, con la persona en un recuadro)
def cuadritos(*xy): return [dict(tipo='caja', x=x, y=y, w=w, h=w, color=c, en=0) for x, y, w, c in xy]
CUAD_C = cuadritos((96, 760, 64, 'rgba(176,141,87,.38)'), (930, 600, 46, 'rgba(27,58,84,.22)'), (900, 1120, 70, 'rgba(176,141,87,.26)'), (150, 1210, 34, 'rgba(27,58,84,.3)'))
CUAD_O = cuadritos((96, 760, 64, 'rgba(201,164,106,.32)'), (930, 600, 46, 'rgba(247,243,240,.14)'), (900, 1120, 70, 'rgba(201,164,106,.22)'), (150, 1210, 34, 'rgba(247,243,240,.2)'))
def paso(n, palabra, sub, en_n, en_p, en_s, oscuro, antes=None):
    fondo, tx = (FONDO, '#fff') if oscuro else (CLARO, FONDO)
    return dict(visual='pantalla', sinSub=True, pantalla=dict(fondo=fondo, **({'foco': FOCO} if oscuro else {}), inserto=dict(x=240, y=560, w=600, h=720, r=36), textos=[
        grande(n, en_n, 410, ACENTO_T if oscuro else ACENTO, 300), grande(palabra, en_p, 1375, tx, 130), chica(sub, en_s, 1492, ACENTO_T if oscuro else ACENTO, 76)]
        + ([chica(antes[0], antes[1], 1375, tx, 84, fin=antes[2])] if antes else [])),
        capas=CUAD_O if oscuro else CUAD_C)

# Escritorio visto desde arriba (beige con sombra de ventana hecha con cajas); `foto` opcional en _img/ (gen_img.py)
SOMBRA_VENTANA = [dict(tipo='caja', x=x, y=0, w=w, h=1920, color='rgba(84,62,36,.075)', en=0) for x, w in ((170, 120), (520, 95), (850, 130))] + \
                 [dict(tipo='caja', x=0, y=y, w=1080, h=h, color='rgba(84,62,36,.06)', en=0) for y, h in ((470, 60), (1240, 70))]
def escritorio(*elementos, textos=(), foto=None):
    return dict(visual='pantalla', pantalla=dict(fondo='#E7DBC2', **({'fondoImg': foto} if foto else {}), textos=list(textos)),
                capas=(SOMBRA_VENTANA if not foto else []) + list(elementos))
def hoja(x, y, giro, en, cae=True, fin=None, **k):
    d = dict(tipo='doc', x=x, y=y - (280 if cae else 0), w=470, titulo='Documento', filas=[{}, {}, {}, {}], alto=62, giro=giro, en=en, dur=.35, **k)
    if cae: d['mueve'] = dict(en=en, fin=f'{en}+0.32' if isinstance(en, str) else en + .32, dy=280)
    if fin: d['fin'] = fin
    return d

# Póster de revista: papel marfil, titular condensado con degradado acero, párrafos decorativos y código de barras
ACERO = ['#8AA0B2', '#4E6A82', '#1B3A54']
LG = 'League Gothic'
def titular(t, en, y, size=210, alfa=1, **k):
    cols = ACERO if alfa >= 1 else [f'rgba(78,106,130,{alfa})'] * 2
    return dict(t=t, en=en, y=y, size=size, fuente=LG, peso=400, color=ACERO[1], degradado=cols, esp='2px', **k)
def parrafo(x, y, en, n=5, w=330):   # bloque de texto chico justificado (decorado): renglones grises
    return [dict(tipo='caja', x=x, y=y + i * 22, w=w if i < n - 1 else w * .6, h=8, r=4, color='rgba(40,48,56,.22)', en=en) for i in range(n)]
def codigo_barras(x, y, en):
    anchos = [6, 3, 3, 8, 3, 5, 3, 3, 7, 4, 3, 6, 3, 3, 8, 3, 5, 4, 3, 6]; out, xx = [], x
    for i, a in enumerate(anchos):
        if i % 2 == 0: out.append(dict(tipo='caja', x=xx, y=y, w=a, h=70, color='rgba(23,27,25,.8)', en=en))
        xx += a + 4
    return out
def poster(textos, capas=(), sub=False, foto=None):
    return dict(visual='pantalla', sinSub=not sub, pantalla=dict(fondo='#F1F1EC', textos=textos, **({'fondoImg': foto, 'empuje': .03, 'fondoAjuste': 'ancho'} if foto else {})), capas=list(capas))

PLANES = {}

# ---- Ejemplo · «Tu dinero se va sin que lo veas» · anuncio de una clase gratuita de finanzas personales ----
# Copia este bloque, cambia la clave por el nombre de la carpeta del video y reescribe frases y escenas.
# Reglas: el texto entra con la palabra que MUESTRA; ninguna palabra gigante dura < 0.9 s; una escena empieza cuando
# entra su primer elemento (sin fondo vacío esperando la palabra); tarjeta que dice la frase → sin subtítulo (sinSub).
PLANES['ejemplo'] = dict(acento=ACENTO_T, y=.72,
 resaltar=['ahorrar', 'gastos', 'hormiga', 'sistema', 'gratuita', 'jueves', 'abajo'],
 subtitulo=dict(fondo='rgba(11,29,46,.84)', color='#fff', size=56, peso=700, resaltar=ACENTO_T, unaLinea=True),
 frases=['Durante años intenté ahorrar', 'y nunca me alcanzaba.', 'Culpaba al sueldo, a la renta, a la suerte.',
  'Hasta que anoté todos mis gastos', 'y encontré los gastos hormiga:', 'cafés, suscripciones y comisiones.',
  'No necesitaba ganar más,', 'necesitaba un sistema.', 'Por eso preparé una clase en línea y gratuita',
  'para armar tu presupuesto en una tarde.', 'Es este jueves.', 'Regístrate en el botón de aquí abajo.'],
 escenas=[
  dict(desde='@durante'),                                                       # persona a cuadro los primeros segundos
  dict(desde='@culpaba', visual='pantalla', sinSub=True, pantalla=dict(fondo=FONDO, rayas=RAYAS, foco=FOCO, textos=[
   chica('le echaba la culpa al', '@culpaba', 660), grande('Sueldo', '@sueldo', 830, tacha='@renta'),
   grande('Renta', '@renta', 1030, ACENTO_T, tacha='@suerte'), grande('Suerte', '@suerte', 1230, tacha='@suerte$+0.2')])),
  dict(desde='@hasta', gigantes=[detras('Gastos', '@gastos', '@gastos$+0.5', y=225)]),
  dict(desde='@y#2', tachados=lista('@cafés', '@comisiones$+0.4', [dict(t='Cafés', en='@cafés'), dict(t='Suscripciones', en='@suscripciones'),
   dict(t='Comisiones', en='@comisiones', oro=True)], y=1000)),
  dict(desde='@no', visual='pizarra', pizarra=dict(elementos=[
   txt('ganar más', 540, 520, '@ganar', 80, '#8E958E', 600), dict(tipo='tacha', x=330, y=535, x2=750, y2=505, en='@necesitaba#2', dur=.3),
   nodo(380, 860, '@necesitaba#2', 'persona'), dict(tipo='linea', x=500, y=860, x2=660, y2=860, punteada=True, w=7, color=ACENTO, en='@un'),
   dict(tipo='engrane', x=760, y=860, s=180, en='@sistema-0.1', vel=1.0), txt('Sistema', 540, 1110, '@sistema', 110, ACENTO)])),
  dict(desde='@por', datos=dict(en='@clase', fin='@gratuita$+0.4', texto='Clase en línea y gratuita', centro=True, y=1120)),
  dict(desde='@es', gigantes=[detras('Jueves', '@jueves', '@jueves$+0.6', 190, ACENTO_CL, y=225)]),
  dict(desde='@regístrate', y=.66, capas=[flecha('@abajo')]),                   # cierre con la flecha al botón
 ])
