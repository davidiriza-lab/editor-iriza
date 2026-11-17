"""Biblioteca del armado: de un plan declarativo (plan.json) a cine.json para render.mjs.

Antes cada campaña copiaba su propio armador (armar.py, armar_e.py, armar_cine_u.py…) y las correcciones quedaban en unos
sí y en otros no. Aquí vive lo que todos repetían; el formato del plan está documentado en `armar.py` (el comando).

Funciones principales (todas trabajan con la lista de palabras de voz/palabras.json: [{t, a, b}]):
  norm(texto)                       minúsculas sin acentos ni signos: así se comparan palabras y anclas
  cargar_palabras(proy)             palabras + respaldo voz/palabras_orig.json (los ajustes siempre parten del original)
  leer_piezas(proy, fuente)         piezas del corte: corte/mapa.json (cortar.py) o tiempos.json (armar_dg.py)
  alinear_cortes(W, piezas, …)      la palabra que Whisper estira sobre un corte empieza DESPUÉS del corte
  alinear_escenas(W, inis, limites) un cambio de escena pegado a un corte (< 0.3 s) arranca EN el corte
  Anclas(W, piezas)                 '@palabra#n$+0.3', '@.palabra' (desde la escena), '@[pieza]', '@[pieza].ini|.fin', '@fin'
  tokens(W, texto)                  cómo se ve cada palabra: 'oye|ve' (mostrar, mayúsculas, guion exacto)
  grupos_escena(…)                  subtítulos de una escena según su estilo (frase, frase-entera, etiqueta, cinetico, escalon)
  encuadre(proy, …)                 caras por tramo, caraH = 1.22 × mediana, caraY = mediana real
  contar_cuadros(proy), fps_proyecto(proy), kit()
  armar(proy, plan)                 todo junto: escribe voz/palabras.json (ajustado) y cine.json; devuelve el cine.json
"""
import copy
import json
import os
import re
import statistics as st
import subprocess
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
if AQUI not in sys.path: sys.path.insert(0, AQUI)
from comun import fps_nativo, fps_num  # noqa: E402

# Palabras de enlace: nunca cierran un subtítulo ni quedan solas en grande.
# DEBIL es la lista de la receta por frases (4-nov); ENLACE la de los estilos cinético/escalón (10/11-nov).
DEBIL = {'de', 'la', 'el', 'los', 'las', 'un', 'una', 'a', 'en', 'y', 'que', 'mi', 'tu', 'su', 'por', 'para', 'con', 'se', 'lo', 'del', 'al',
         'me', 'te', 'sin', 'ni', 'o', 'le', 'les', 'nos', 'muy', 'si', 'solo', 'este', 'esta', 'ese', 'esa', 'mis', 'tus', 'sus', 'cada'}
ENLACE = {'o', 'de', 'la', 'el', 'que', 'y', 'a', 'en', 'no', 'un', 'una', 'los', 'las', 'se', 'con', 'por', 'para', 'lo', 'al', 'del', 'es',
          'te', 'tu', 'ya', 'yo', 'mi', 'si', 'sin', 'pero', 'como', 'cómo', 'qué', 'da', 'son', 'le', 'me'}

# Estilos de subtítulo = cómo se corta la voz (cortar) + cómo se dibuja cada trozo (forma)
ESTILOS = {
    'frase':        {'cortar': 'frase', 'forma': 'linea', 'frase': True, 'maxPal': 4, 'maxLetras': 26},   # receta 4-nov: 2-4 palabras, una línea
    'frase-entera': {'cortar': 'entera', 'forma': 'linea', 'frase': True},                               # la frase completa en un grupo
    'etiqueta':     {'cortar': 'linea', 'forma': 'linea', 'maxLetras': 26},                              # una línea en píldora (cfg etiqueta)
    'cinetico':     {'cortar': 'pocas', 'forma': 'chica-grande', 'maxPal': 3, 'retroceso': 'uno', 'unirEnlace': True},   # estilo E (10-nov)
    'escalon':      {'cortar': 'pocas', 'forma': 'chica-grande', 'maxPal': 4, 'retroceso': 'todos', 'enlaceChica': True},  # aprobado 11-nov
    'ocultos':      {'cortar': 'ocultos'},                                                                # la escena ya dice la frase
}

# Recetas aprobadas: valores por defecto que un plan puede cambiar clave por clave
RECETAS = {
    # plantillas/anuncio-por-frases (aprobada el 4-nov-2026): subtítulo por frase, un encuadre, cortes alineados
    'anuncio-por-frases': {
        'texto': {'estilo': 'frase', 'y': .715, 'resaltar': []},
        'base': {'visual': 'persona', 'tema': 'oscuro'}, 'forzar': {'textoTema': 'oscuro'},
        'base_visual': {'pizarra': {'vig': .06}, 'editorial': {'vig': .06}, 'pantalla': {'vig': .06}},
        'piezas': 'mapa', 'alinear': {'margen': .02, 'max': False, 'escenas': True}, 'zoom': ['escenas_persona', 'piezas'],
        'encuadre': {'min': 3, 'faltan': 'anterior', 'margenFinal': 2, 'caraY': 'auto', 'caraH': 'auto'},
        'persona': {'cuadros': 'cuadros', 'mascaras': 'mascaras', 'crudos': 'cuadros', 'fondo': 'real', 'bajar': 0, 'zoomAlt': 1.05},
        'sfx_cambio': {'f': 'whoosh_rapido.mp3', 'ruta': 'absoluta', 'desfase': .02, 'pico': .3, 'vol': .16},
        'cola': .25, 'cine': {'acentoTexto': '#fff', 'limpio': {}, 'marcas': {'impacto': -9, 'tap': -9}, 'sfx_auto': False},
    },
    # Cine Pro estilo E (10-nov-2026): línea chica + palabra grande, golpes, escenas 3D
    'cine-e': {
        'texto': {'estilo': 'cinetico', 'y': .74, 'sombra': True},
        'base': {'visual': 'persona', 'tema': 'oscuro', 'textoTema': 'oscuro'},
        'alinear': False, 'zoom': ['escenas'], 'encuadre': False,
        'persona': {'cuadros': 'cuadros_pro', 'mascaras': 'mascaras', 'crudos': 'cuadros', 'fondo': 'real', 'bajar': 0, 'zoomAlt': 1.08},
        'cine': {'marcas': {'impacto': -9, 'tap': -9}, 'sfx_auto': True},
    },
    # estilo aprobado el 11/12-nov-2026: escalón (barra inclinada), piezas de tiempos.json, capas imp/pant/cap
    'escalon': {
        'texto': {'estilo': 'escalon', 'y': .70, 'sombra': True, 'mayusculaInicio': True},
        'base': {'visual': 'persona', 'tema': 'oscuro', 'textoTema': 'oscuro'},
        'piezas': 'tiempos', 'alinear': {'margen': .04, 'max': True, 'escenas': False}, 'zoom': ['internos'],
        'encuadre': {'min': 5, 'minH': 150, 'faltan': {'cx': 540, 'cy': 633.6, 'h': 9999}, 'margenFinal': 3,
                     'caraY': .42, 'caraH': 300},
        'persona': {'cuadros': 'cuadros_pro', 'mascaras': 'mascaras', 'crudos': 'cuadros', 'fondo': 'real', 'bajar': 0, 'zoomAlt': 1.05},
        'cine': {'marcas': {'impacto': -9, 'tap': -9}, 'sfx_auto': True},
    },
}

# claves del plan que se mezclan con las de la receta en vez de reemplazarlas
MEZCLA = {'texto', 'encuadre', 'persona', 'cine', 'alinear', 'base', 'base_visual', 'forzar', 'sfx_cambio'}
# claves de la raíz de cine.json que calcula el armador (el resto de las que conoce render.mjs pasan tal cual)
CALCULADAS = {'escenas', 'cortes', 'caras', 'caraH', 'persona', 'fps', 'sfx', 'musica', 'nombre', 'handle', 'cola', 'voz', 'salida'}
# claves de una escena que usa el armador y no van al cine.json
DE_ESCENA = {'desde', 'texto', 'y', 'ocultar', 'sinSub'}


def norm(x):
    x = unicodedata.normalize('NFD', str(x).lower())
    x = ''.join(c for c in x if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9ñ]', '', x)


def leer(f):
    with open(f) as h: return json.load(h)


def guardar(f, o):
    with open(f, 'w') as h: json.dump(o, h, ensure_ascii=False, indent=1)


def falla(msg): sys.exit(f'✗ {msg}')


# ---------------------------------------------------------------- datos del proyecto

def kit():
    """Nombre y @usuario de la persona (config/kit.json)."""
    f = os.path.join(RAIZ, 'config', 'kit.json')
    return leer(f) if os.path.exists(f) else {}


def fps_proyecto(proy, voz='corte/cam.mov'):
    """Los fps con los que se cortó (metodo.json, lo escribe cortar.py/metodo_corte.py) o los del corte mismo. Nunca a mano."""
    m = os.path.join(proy, 'metodo.json')
    if os.path.exists(m) and leer(m).get('fps'): return str(leer(m)['fps'])
    f = os.path.join(proy, voz)
    if os.path.exists(f): return fps_nativo(f)
    falla(f'no sé los fps: falta metodo.json y {voz}')


def contar_cuadros(proy, carpeta='cuadros', voz='corte/cam.mov', fps=None):
    """persona.n = cuadros que sacó preparar.py. Si el proyecto se limpió (sin cuadros/), se cuentan en el corte."""
    d = os.path.join(proy, carpeta)
    n = len([f for f in os.listdir(d) if f.endswith('.jpg')]) if os.path.isdir(d) else 0
    if n: return n
    f = os.path.join(proy, voz)
    if not os.path.exists(f): return 0
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries', 'stream=nb_read_packets,duration',
                        '-of', 'json', f], capture_output=True, text=True).stdout
    s = (json.loads(r or '{}').get('streams') or [{}])[0]
    n = int(s.get('nb_read_packets') or 0) or round(float(s.get('duration') or 0) * fps_num(fps or fps_nativo(f)))
    print(f'  ⚠ no hay {carpeta}/ (¿proyecto limpio?): persona.n = {n} contado en {voz}. Regenera con: .venv/bin/python estilo-cine/preparar.py <proyecto>')
    return n


def claves_raiz_motor():
    """Claves de la raíz de cine.json que lee render.mjs (salen del propio código, como hace su validación)."""
    try:
        with open(os.path.join(AQUI, 'render.mjs')) as h: return set(re.findall(r'\bcfg\.([A-Za-z_]\w*)', h.read()))
    except OSError:
        return {'acento', 'acentoTexto', 'anillos', 'apretado', 'bio', 'contorno', 'fuenteChica', 'fuenteGrande', 'hdr_ok', 'imagenes', 'lienzo',
                'limpio', 'logos', 'marcas', 'paleta', 'perfil', 'pop', 'sfx_auto', 'suave', 'subtitulo', 'titular', 'top5'}


# ---------------------------------------------------------------- voz y piezas

def cargar_palabras(proy, respaldar=True):
    """voz/palabras.json con respaldo en voz/palabras_orig.json: los ajustes de inicio (cortes, escenas) siempre se aplican
    sobre la transcripción original, así que volver a armar con otro plan no arrastra ajustes viejos. Si palabras.json trae
    otras palabras o finales (se volvió a transcribir, remapear.py, afinar_palabras.py), esa pasa a ser la original."""
    fp, fo = os.path.join(proy, 'voz', 'palabras.json'), os.path.join(proy, 'voz', 'palabras_orig.json')
    W = leer(fp)
    if os.path.exists(fo):
        O = leer(fo)
        if len(O) == len(W) and all(o['t'] == w['t'] and abs(o['b'] - w['b']) < 1e-9 for o, w in zip(O, W)): return copy.deepcopy(O)
        print('  voz/palabras.json cambió (nueva transcripción): pasa a ser la original (voz/palabras_orig.json)')
    if respaldar: guardar(fo, W)
    return copy.deepcopy(W)


def leer_piezas(proy, fuente='auto'):
    """Piezas del corte, en segundos del video armado: [{nombre, ini, fin, voz, cortes, _ini}].
    'mapa' = corte/mapa.json (piezas de la fuente; se nombran 1, 2, 3…) · 'tiempos' = tiempos.json (items con nombre,
    'voz' = fin de la voz y 'cortes' internos) · 'auto' = tiempos.json si existe, si no corte/mapa.json · None = sin piezas."""
    ft, fm = os.path.join(proy, 'tiempos.json'), os.path.join(proy, 'corte', 'mapa.json')
    if fuente == 'auto': fuente = 'tiempos' if os.path.exists(ft) else 'mapa' if os.path.exists(fm) else None
    if fuente == 'tiempos':
        return [{'nombre': t['item'], 'ini': t['ini'], '_ini': t['ini'], 'fin': t['fin'], 'voz': t.get('voz_fin', t['fin']), 'cortes': t.get('cortes', []), '_fuente': 'tiempos'}
                for t in leer(ft)]
    if fuente == 'mapa':
        out, t = [], 0
        for k, (a, b) in enumerate(leer(fm)['piezas']):
            ini = t; t += b - a
            out.append({'nombre': str(k + 1), 'ini': round(ini, 3), '_ini': ini, 'fin': round(t, 3), 'voz': round(t, 3), 'cortes': [], '_fuente': 'mapa'})
        return out
    return []


def limites(piezas):
    """Los cortes entre piezas (segundos)."""
    return [p['ini'] for p in piezas[1:]]


def alinear_cortes(W, piezas, margen=.02, siempre=False):
    """Whisper estira la palabra que abre una pieza sobre el corte: se la hace empezar `margen` s después del corte.
    siempre=False (receta 4-nov) solo si empezaba antes del corte; True (receta escalon) nunca antes de corte + margen."""
    for p in piezas[1:]:
        t = p['_ini']
        w = next((w for w in W if w['b'] > t + .05), None)
        if w is None: continue
        if siempre: w['a'] = round(max(w['a'], t + margen), 3)
        elif w['a'] < t: w['a'] = round(t + margen, 3)


def alinear_escenas(W, inis, lims, ventana=.3):
    """Un cambio de escena pegado a un corte (< 0.3 s después) arranca EN el corte: si no, se asoman 1–7 cuadros de la toma siguiente."""
    for i0 in inis[1:]:
        c = next((c for c in lims if 0 < W[i0]['a'] - c < ventana), None)
        if c is not None: W[i0]['a'] = round(c + .001, 3)


def i_pieza(W, piezas, j):
    """Primera palabra de la pieza j: la primera que termina después de que la pieza empieza."""
    if j == 0: return 0
    return next(i for i, w in enumerate(W) if w['b'] > piezas[j]['ini'] + .05)


# ---------------------------------------------------------------- anclas

_ANCLA = re.compile(r'^@(?P<esc>\.)?(?:\[(?P<pz>[^\]]+)\](?P<campo>\.(?:ini|fin))?)?(?P<pal>[^#+\-$]*?)(?:#(?P<n>\d+))?(?P<final>\$)?(?P<off>[+-]\d*\.?\d+)?$')


class Anclas:
    """Anclas de palabra (no distinguen mayúsculas ni acentos):
      '@palabra'  inicio de la primera vez que se dice      '@palabra#2'  la segunda vez
      '@palabra$' final de la palabra                        '+0.3' / '-0.1' segundos de más o de menos
      '@.palabra' contando desde el inicio de la escena (en `desde`: desde la escena anterior)
      '@[pieza]'  primera palabra de una pieza (nombre de tiempos.json o número de corte/mapa.json, desde 1)
      '@[pieza]palabra#2'  contando desde esa pieza       '@[pieza].ini' / '@[pieza].fin'  inicio de la pieza / fin de su voz
      '@fin'      final de la voz                          '@@texto'  texto que empieza con @ (no es ancla)
    En `desde` también vale un número: segundos (la primera palabra que termina después)."""

    def __init__(self, W, piezas):
        self.W, self.P = W, piezas

    def pieza(self, nombre):
        for j, p in enumerate(self.P):
            if p['nombre'] == nombre: return j
        if nombre.isdigit() and 1 <= int(nombre) <= len(self.P): return int(nombre) - 1
        falla(f'pieza no encontrada: [{nombre}] (hay: {", ".join(p["nombre"] for p in self.P) or "ninguna"})')

    def _partes(self, a):
        m = _ANCLA.match(a)
        if not m: falla(f'ancla mal escrita: {a}')
        return m

    def idx(self, a, desde=None):
        """Índice de la palabra del ancla (se ignoran $ y desplazamiento)."""
        if isinstance(a, (int, float)):
            return next((i for i, w in enumerate(self.W) if w['b'] > a + .05), len(self.W) - 1)
        if re.match(r'^@fin([+-]\d*\.?\d+)?$', a): return len(self.W) - 1
        m = self._partes(a); s = 0
        if m['esc']:
            if desde is None: falla(f'{a}: "@." cuenta desde la escena y aquí no hay escena')
            s = desde
        if m['pz']:
            j = self.pieza(m['pz'])
            if m['campo']: return self.idx(self.P[j]['ini'] if m['campo'] == '.ini' else self.P[j]['voz'])
            s = i_pieza(self.W, self.P, j)
            if not m['pal']: return s
        pal, n, c = norm(m['pal']), int(m['n'] or 1), 0
        for i in range(s, len(self.W)):
            if norm(self.W[i]['t']) == pal:
                c += 1
                if c == n: return i
        falla(f'ancla no encontrada: {a}' + (f' (contando desde la palabra {s}: "{self.W[s]["t"]}")' if s else ''))

    def seg(self, a, desde=None):
        """Segundos del ancla."""
        if isinstance(a, (int, float)): return float(a)
        f = re.match(r'^@fin([+-]\d*\.?\d+)?$', a)
        if f: return self.W[-1]['b'] + float(f.group(1) or 0)   # '@fin' exacto: '@fines' es una palabra
        m = self._partes(a); off = float(m['off'] or 0)
        if m['pz'] and m['campo']:
            p = self.P[self.pieza(m['pz'])]
            return (p['ini'] if m['campo'] == '.ini' else p['voz']) + off
        i = self.idx(a, desde)
        return (self.W[i]['b'] if m['final'] else self.W[i]['a']) + off

    def resolver(self, o, desde=None):
        """Cambia cada texto '@…' (en cualquier nivel) por sus segundos, redondeados a milésimas."""
        if isinstance(o, dict): return {k: self.resolver(v, desde) for k, v in o.items()}
        if isinstance(o, list): return [self.resolver(v, desde) for v in o]
        if isinstance(o, str) and o.startswith('@@'): return o[1:]
        if isinstance(o, str) and o.startswith('@'): return round(self.seg(o, desde), 3)
        return o


# ---------------------------------------------------------------- texto

def _punt(w): return bool(re.search(r'[.,;:?!]$', w['t']))


def guion(W, frases, oido_distinto=()):
    """Guion exacto (lista de frases, palabra por palabra igual que la voz): lo visible de cada palabra y dónde acaba cada frase.
    Comprueba que coincide con la voz (salvo las palabras en oido_distinto)."""
    vis, fines = [], set()
    for f in frases:
        vis += f.split(); fines.add(len(vis))
    N = len(W)
    if len(vis) != N:
        falla(f'el guion tiene {len(vis)} palabras y la voz {N}: ' + str([(i, a, W[i]['t']) for i, a in enumerate(vis) if i < N and norm(a) != norm(W[i]['t'])][:6]))
    od = {norm(x) for x in oido_distinto}
    for i, a in enumerate(vis):
        if norm(a) != norm(W[i]['t']) and norm(a) not in od: falla(f'palabra {i}: guion "{a}" vs voz "{W[i]["t"]}"')
    return vis, fines


def fines_por_signos(W):
    return {i + 1 for i, w in enumerate(W) if w['t'].rstrip()[-1:] in '.?!…'}


def tokens(W, T, vis=None):
    """Cómo se ve cada palabra en el guion visual del cine.json: 'oye' o 'oye|ve' ('oye|' la oculta).
    vis (guion exacto) manda; si no: oSuelta, mostrar {palabra: texto}, capitalizar ['Instagram', 'tu Negocio']
    (se ponen en mayúscula las palabras escritas con mayúscula) y mayusculaInicio (primera palabra de cada oración)."""
    if vis is not None: return [W[i]['t'] + '|' + vis[i] for i in range(len(W))]
    mostrar = {norm(k): v for k, v in (T.get('mostrar') or {}).items()}
    pats = [p.split() for p in T.get('capitalizar') or []]
    piezas_ini = T.get('_inicios_pieza') or []
    out = []
    for i, w in enumerate(W):
        t, n = w['t'], norm(w['t'])
        if T.get('oSuelta') and n == 'o' and i + 1 < len(W) and any(abs(W[i + 1]['a'] - c) < .3 for c in piezas_ini):
            out.append(t + '|'); continue   # "o" que Whisper pega al final de una frase
        if n in mostrar: out.append(f'{t}|{mostrar[n]}'); continue
        cap = T.get('mayusculaInicio') and (i == 0 or W[i - 1]['t'].rstrip()[-1:] in '.?!…')
        for p in pats:
            for k, pk in enumerate(p):
                if pk[:1].isupper() and k <= i and i - k + len(p) <= len(W) and all(norm(W[i - k + q]['t']) == norm(p[q]) for q in range(len(p))):
                    cap = True
        out.append(f'{t}|{t[0].upper()}{t[1:]}' if cap and t[:1].islower() else t)
    return out


def trozos_frase(tk, maxPal=4, maxLetras=26, debil=DEBIL):
    """Corte óptimo de una frase en subtítulos de una línea (receta 4-nov): pocos trozos, ≤ maxPal palabras y ≤ maxLetras letras,
    de preferencia tras una coma o punto, nunca dejando colgada una palabra débil ni una palabra sola."""
    if not tk: return []
    v = [t.split('|', 1)[-1] for t in tk]
    if not any(v): return [tk]   # oculto: un solo grupo
    n = len(tk); best = [0] + [None] * n; cut = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(max(0, j - maxPal), j):
            if best[i] is None: continue
            txt = ' '.join(v[i:j]); s_ = j - i
            if s_ > 1 and len(txt) > maxLetras: continue
            c = 1 + (1.3 if s_ == 1 and n > 1 else 0)
            if j < n:
                if v[j - 1].lower().strip(',.;:?!…«»¿¡') in debil: c += 1.2   # con acento: «mí» no es débil, «mi» sí
                if v[j - 1][-1:] in ',.;:?!…»': c -= .5
            if best[j] is None or best[i] + c < best[j]: best[j], cut[j] = best[i] + c, i
    out, j = [], n
    while j > 0: out.append(tk[cut[j]:j]); j = cut[j]
    return out[::-1]


def cortar_linea(W, a, b, maxc=26, enlace=ENLACE):
    """Una línea por trozo: corta en signo o al pasar de maxc letras, sin cerrar en palabra de enlace."""
    out, s = [], a
    for i in range(a, b):
        txt = ' '.join(W[j]['t'] for j in range(s, i + 2)) if i + 1 < b else ''
        p = _punt(W[i])
        if i == b - 1 or p or len(txt) > maxc:
            j = i + 1
            if not p and i < b - 1:
                while j - 1 > s and norm(W[j - 1]['t']) in enlace: j -= 1
            out.append((s, j)); s = j
    if s < b: out.append((s, b))
    return out


def cortar_pocas(W, a, b, maxw=3, enlace=ENLACE, retroceso='todos', unir=False):
    """Trozos de ≤ maxw palabras cortando en signos. Al llegar al tope sin signo no se cierra en palabra de enlace:
    retroceso 'uno' (estilo E) la pasa al trozo siguiente; 'todos' (escalón) retrocede todas las que haya.
    unir: un trozo de una sola palabra de enlace se pega al anterior."""
    out, s = [], a
    for i in range(a, b):
        p = _punt(W[i])
        if retroceso == 'uno':
            if p or i == b - 1: out.append((s, i + 1)); s = i + 1
            elif i - s + 1 >= maxw:
                if norm(W[i]['t']) in enlace and i > s: out.append((s, i)); s = i
                else: out.append((s, i + 1)); s = i + 1
        elif p or i == b - 1 or i - s + 1 >= maxw:
            j = i + 1
            if i - s + 1 >= maxw and not p and i < b - 1:
                while j - 1 > s and norm(W[j - 1]['t']) in enlace: j -= 1
            out.append((s, j)); s = j
    if s < b: out.append((s, b))
    if unir:
        fix = []
        for x, y in out:
            if fix and y - x == 1 and norm(W[x]['t']) in enlace: fix[-1] = (fix[-1][0], y)
            else: fix.append((x, y))
        out = fix
    return out


def _grupo(T, y, lineas, extra=True):
    g = {'y': y}
    if T.get('frase'): g['frase'] = True
    if T.get('sombra') is not None: g['sombra'] = T['sombra']
    if T.get('etiqueta'): g['etiqueta'] = T['etiqueta']
    g['lineas'] = lineas
    if T['forma'] == 'linea' and 'resaltar' in T: g['resaltar'] = T['resaltar']
    if extra: g.update(T.get('grupo') or {})
    return g


def forma_chica_grande(W, tk, x, z, T, enlace):
    """Línea chica + palabra grande: la grande es la palabra clave (resaltar → marcatextos '*', contorno → '~') o la última
    con contenido; si quedan palabras después, van en un grupo aparte."""
    R, C = {norm(r) for r in T.get('resaltar') or []}, {norm(r) for r in T.get('contorno') or []}
    ws = list(range(x, z)); y = T['y']
    key = next((i for i in ws if norm(W[i]['t']) in R | C), None)
    if key is None: key = next((i for i in reversed(ws) if norm(W[i]['t']) not in enlace), ws[-1])
    chico, grande = [i for i in ws if i < key], [i for i in ws if i >= key][:2]
    resto = [i for i in ws if i > (grande[-1] if grande else key)]
    n = norm(W[key]['t']); pre = '*' if n in R else ('~' if n in C else '')
    lineas = (['-' + ' '.join(tk[i] for i in chico)] if chico else []) + [pre + ' '.join(tk[i] for i in grande)]
    gps = [_grupo(T, y, lineas)]
    if resto: gps.append(_grupo(T, y, [' '.join(tk[i] for i in resto)]))
    return gps


def _enlace_a_chica(gps, enlace):
    """Escalón: un grupo que solo trae palabras de enlace ("Y", "que") no va gigante: pasa a la línea chica."""
    for gp in gps:
        ws = ' '.join(gp['lineas']).replace('*', '').replace('-', '').split()
        if all(norm(w.split('|')[-1]) in enlace for w in ws): gp['lineas'] = ['-' + ' '.join(l.lstrip('*-') for l in gp['lineas'])]


def _suelta_al_siguiente(gps):
    """Una palabra suelta que sobró ("va") pasa a la línea chica del grupo siguiente."""
    out = []
    for k, gp in enumerate(gps):
        if len(gp['lineas']) == 1 and len(gp['lineas'][0].lstrip('*-').split()) == 1 and k + 1 < len(gps):
            nx = gps[k + 1]; pal = gp['lineas'][0].lstrip('*-')
            nx['lineas'] = (['-' + pal + ' ' + nx['lineas'][0].lstrip('-')] + nx['lineas'][1:]) if nx['lineas'][0].startswith('-') else (['-' + pal] + nx['lineas'])
            continue
        out.append(gp)
    return out


def grupos_escena(W, tk, i0, i1, T, ocultos=(), fines=None):
    """Subtítulos de las palabras [i0, i1) con el estilo T (ya resuelto). ocultos = índices que no se muestran."""
    ocultos = set(ocultos); grupos = []
    enlace = {norm(x) for x in T['enlace']} if T.get('enlace') else (DEBIL if T['cortar'] in ('frase', 'entera') else ENLACE)
    if T['cortar'] == 'ocultos': ocultos |= set(range(i0, i1))
    if T['cortar'] in ('frase', 'entera'):   # receta 4-nov: trozos dentro de cada frase; lo oculto, en su propio grupo
        cur, estado = [], None
        def cierra():
            nonlocal cur
            chs = trozos_frase(cur, T.get('maxPal', 4), T.get('maxLetras', 26), enlace) if T['cortar'] == 'frase' else ([cur] if cur else [])
            for ch in chs: grupos.append({'y': T['y'], 'frase': True, 'lineas': [' '.join(ch)], 'resaltar': T.get('resaltar', [])} | (T.get('grupo') or {}))
            cur = []
        for i in range(i0, i1):
            oc = i in ocultos
            if estado is not None and oc != estado: cierra()
            estado = oc; cur.append(W[i]['t'] + '|' if oc else tk[i])
            if fines and i + 1 in fines: cierra(); estado = None
        cierra()
        return grupos
    i = i0
    while i < i1:   # tramos seguidos de palabras visibles u ocultas
        oc = i in ocultos; j = i
        while j < i1 and (j in ocultos) == oc: j += 1
        if oc:
            grupos.append({'y': T.get('yOculto', .5), 'lineas': [' '.join(W[q]['t'] + '|' for q in range(i, j))]})
        else:
            if T['cortar'] == 'linea': trozos = cortar_linea(W, i, j, T.get('maxLetras', 26), enlace)
            else: trozos = cortar_pocas(W, i, j, T.get('maxPal', 3), enlace, T.get('retroceso', 'todos'), T.get('unirEnlace', False))
            gps = []
            for x, z in trozos:
                if T['forma'] == 'chica-grande': gps += forma_chica_grande(W, tk, x, z, T, enlace)
                else: gps.append(_grupo(T, T['y'], [' '.join(tk[q] for q in range(x, z))]))
            if T.get('enlaceChica'): _enlace_a_chica(gps, enlace)
            if T.get('suelta'): gps = _suelta_al_siguiente(gps)
            grupos += gps
        i = j
    return grupos


def estilo_texto(base, *capas):
    """Mezcla la configuración de texto (receta → plan → escena). Cambiar 'estilo' trae los valores de ese estilo."""
    T = dict(base)
    for c in capas:
        if not c: continue
        if 'estilo' in c and c['estilo'] != T.get('estilo'):
            for k in ('cortar', 'forma', 'frase', 'maxPal', 'maxLetras', 'retroceso', 'unirEnlace', 'enlaceChica'): T.pop(k, None)
        T.update(c)
    est = T.get('estilo', 'frase')
    if est not in ESTILOS: falla(f'estilo de texto desconocido: {est} (hay: {", ".join(ESTILOS)})')
    return {**ESTILOS[est], **T}


# ---------------------------------------------------------------- encuadre

def encuadre(proy, W, piezas, E):
    """Un solo encuadre por video: caras por tramo (mediana de cada pieza), caraH = 1.22 × mediana del tamaño de cara,
    caraY = mediana real de la altura de la cara. Lee corte/caras.json (bin/caras). Devuelve (caras, caraH, caraY)."""
    f = os.path.join(proy, 'corte', 'caras.json')
    if not os.path.exists(f): falla('falta corte/caras.json para el encuadre (corre bin/caras) o pon "encuadre": false')
    C = leer(f)['f']
    fin = (piezas[-1]['fin'] if piezas and piezas[-1].get('_fuente') == 'tiempos' else W[-1]['b']) + E.get('margenFinal', 2)   # el último tramo dura hasta el final
    lim = [0] + limites(piezas) + [fin]; nombres = [p['nombre'] for p in piezas] or ['1']
    caras, prev = [], None
    for k, (a, b) in enumerate(zip(lim, lim[1:])):
        f = [c for c in C if a <= c[0] < b and len(c) >= 5 and (E.get('minH') is None or c[4] - c[2] > E['minH'])]
        sin = k < len(nombres) and any(nombres[k].startswith(x) for x in E.get('sinEncuadre') or [])   # p. ej. la toma del público
        if not sin and len(f) >= E.get('min', 3):
            prev = {'ini': a, 'fin': b, 'cx': round(st.median((c[1] + c[3]) / 2 for c in f), 1), 'cy': round(st.median((c[2] + c[4]) / 2 for c in f), 1),
                    'h': round(st.median(c[4] - c[2] for c in f), 1)}
            caras.append(prev)
        elif isinstance(E.get('faltan'), dict): caras.append({'ini': a, 'fin': b, **E['faltan']})   # encuadre fijo donde no hay cara
        elif prev: prev = {**prev, 'ini': a, 'fin': b}; caras.append(prev)                         # 'anterior': se queda el de la pieza previa
    cH = E.get('caraH', 'auto')
    if cH == 'auto': cH = round(1.22 * st.median(c['h'] for c in caras))   # 22 % de margen: alcanza para llevar la cara al mismo lugar en cada corte
    cY = E.get('caraY')
    if cY == 'auto': cY = round(st.median((c[2] + c[4]) / 2 for c in C if len(c) >= 5) / 1920, 3)
    return caras, cH, cY


# ---------------------------------------------------------------- sonido

def ruta_sfx(f, proy, absoluta=False):
    """'boom.mp3' → estilo-cine/sfx/boom.mp3 relativo al proyecto (o absoluto); una ruta con '/' se deja tal cual."""
    if '/' in f: return f
    r = os.path.join(AQUI, 'sfx', f)
    if not os.path.exists(r): print(f'  ⚠ no existe el efecto estilo-cine/sfx/{f}')
    return os.path.abspath(r) if absoluta else os.path.relpath(r, proy)


def avisos_sfx(W, sfx, margen=.12):
    """Un efecto no debe pisar la última sílaba de una frase: avisa si su golpe cae en los últimos `margen` s de una palabra que
    cierra frase."""
    out = []
    finales = [w for k, w in enumerate(W) if w['t'].rstrip()[-1:] in '.?!…,' or k == len(W) - 1]
    for s in sfx:
        for w in finales:
            if w['b'] - margen <= s['en'] <= w['b']:
                out.append(f'{os.path.basename(s["f"])} en {s["en"]:.2f} s cae sobre el final de "{w["t"]}" ({w["b"]:.2f} s)'); break
    return out


# ---------------------------------------------------------------- todo junto

def componer(plan):
    """Receta + plan (las claves de MEZCLA se mezclan; las demás se reemplazan) + atajos de planes.py."""
    plan = copy.deepcopy(plan)
    rec = plan.get('receta')
    if rec and rec not in RECETAS: falla(f'receta desconocida: {rec} (hay: {", ".join(RECETAS)})')
    P = copy.deepcopy(RECETAS.get(rec, {}))
    for k, v in plan.items():
        if k in MEZCLA and isinstance(v, dict) and isinstance(P.get(k), dict): P[k] = {**P[k], **v}
        else: P[k] = v
    T = P.setdefault('texto', {})
    for k in ('y', 'resaltar', 'mostrar', 'enlace'):   # atajos de planes.py en la raíz (el bloque "texto" del plan manda)
        if k in plan and k not in (plan.get('texto') or {}): T[k] = plan[k]
    if P.get('encuadre') is not False:
        P['encuadre'] = dict(P.get('encuadre') or {})
        for k in ('caraY', 'caraH'):
            if k in plan: P['encuadre'][k] = plan[k]
    if 'zoomAlt' in plan and P.get('persona') is not False: P['persona'] = {**(P.get('persona') or {}), 'zoomAlt': plan['zoomAlt']}
    raiz = claves_raiz_motor() - CALCULADAS
    P['_cine'] = {**RECETAS.get(rec, {}).get('cine', {}), **{k: v for k, v in plan.items() if k in raiz}, **(plan.get('cine') or {})}
    return P


def armar(proy, plan, escribir=True):
    """Arma el cine.json del proyecto desde el plan. Escribe voz/palabras.json (con los inicios ajustados) y cine.json."""
    proy = os.path.abspath(proy); P = componer(plan)
    alin = P.get('alinear')
    W = cargar_palabras(proy, escribir) if alin else leer(os.path.join(proy, 'voz', 'palabras.json'))
    N = len(W)
    PZ = leer_piezas(proy, P.get('piezas', 'auto'))
    if alin and PZ: alinear_cortes(W, PZ, alin.get('margen', .02), alin.get('max', False))
    A = Anclas(W, PZ)
    vis, fines = guion(W, P['frases'], P.get('oido_distinto', ())) if P.get('frases') else (None, fines_por_signos(W))
    TP = dict(P['texto']); TP['_inicios_pieza'] = limites(PZ)

    # encuadre (antes de las escenas: caraY va en cada escena de persona)
    E = P.get('encuadre')
    caras, caraH, caraY = encuadre(proy, W, PZ, E) if E else (None, None, None)

    # escenas: las que tienen "desde" se reparten la voz; las demás (tarjeta final…) llevan "inicio" y van sin texto
    EP = P.get('escenas') or falla('el plan no tiene escenas')
    inis, prev = [], 0
    for e in EP:
        if 'desde' in e: prev = A.idx(e['desde'], prev); inis.append(prev)
    NT = A.idx(P['textoHasta']) if P.get('textoHasta') else N   # desde aquí la voz va sin subtítulo (la tarjeta final ya lo dice)
    if inis and inis[-1] >= NT: falla(f'textoHasta ({P["textoHasta"]}) cae antes de la última escena con "desde"')
    if not inis or inis != sorted(inis) or inis[0] != 0: falla(f'las escenas con "desde" deben ir en orden y la primera empezar en la primera palabra: {inis}')
    if alin and alin.get('escenas') and PZ: alinear_escenas(W, inis, limites(PZ))

    zoom = P.get('zoom') or []; z_esc, sfx = [], []
    SC = P.get('sfx_cambio'); ultimo = None
    esc_out, kw = [], 0
    for e in EP:
        resto = {k: v for k, v in e.items() if k not in DE_ESCENA}
        if 'desde' not in e:
            x = A.resolver(resto); x.setdefault('grupos', [])
            if 'inicio' not in x and esc_out: falla(f'escena {len(esc_out) + 1} sin "desde" ni "inicio": no se sabe cuándo empieza')
            esc_out.append(x); continue
        i0 = inis[kw]; i1 = inis[kw + 1] if kw + 1 < len(inis) else NT
        x = A.resolver(resto, i0)
        for k, v in (P.get('base') or {}).items(): x.setdefault(k, copy.deepcopy(v))
        x.setdefault('visual', 'persona')
        for k, v in ((P.get('base_visual') or {}).get(x['visual']) or {}).items(): x.setdefault(k, copy.deepcopy(v))
        if x['visual'] == 'persona' and caraY is not None: x.setdefault('caraY', caraY)   # un solo encuadre: la cara no brinca entre escenas
        x.update(copy.deepcopy(P.get('forzar') or {}))
        if 'grupos' in e: x['grupos'] = A.resolver(e['grupos'], i0)
        else:
            T = estilo_texto(TP, {'y': e['y']} if 'y' in e else None, e.get('texto'))
            oc = set()
            for par in e.get('ocultar', []):
                a = A.idx(par[0], i0); b = A.idx(par[1], i0) if len(par) > 1 and par[1] is not None else i1 - 1
                oc |= set(range(a, b + 1))
            if e.get('sinSub'): oc |= set(range(i0, i1))
            x['grupos'] = grupos_escena(W, tokens(W, T, vis), i0, i1, T, oc, fines)
        if kw > 0:
            if 'escenas' in zoom or ('escenas_persona' in zoom and x['visual'] in ('persona', 'split', 'franja')): z_esc.append(round(W[i0]['a'], 3))
        firma = (x['visual'], x['pantalla'].get('fondo') if isinstance(x.get('pantalla'), dict) else None)
        if SC and kw > 0 and firma != ultimo:
            sfx.append({'f': ruta_sfx(SC['f'], proy, SC.get('ruta') == 'absoluta'), 'en': round(W[i0]['a'] + SC.get('desfase', .02), 3), 'pico': SC.get('pico', .3), 'vol': SC.get('vol', .16)})
        ultimo = firma; esc_out.append(x); kw += 1

    cortes = list(z_esc)
    extra = (limites(PZ) if 'piezas' in zoom else []) + ([c for p in PZ for c in p['cortes']] if 'internos' in zoom else [])
    cortes = sorted(cortes + [c for c in extra if all(abs(c - x) > .3 for x in z_esc)])

    for s in P.get('sfx') or []:   # efectos: {f, en, pico, vol} (+ repite, cada)
        s = dict(s); rep, cada = s.pop('repite', 1), s.pop('cada', 0)
        en = A.seg(s['en']) if isinstance(s['en'], str) else s['en']
        r = {k: A.resolver(v) for k, v in s.items() if k not in ('f', 'en', 'pico')}
        for k in range(rep):
            sfx.append({'f': ruta_sfx(s['f'], proy), 'en': round(round(en, 3) + k * cada, 3), 'pico': s.get('pico', 0), **r})
    avisos = avisos_sfx(W, sfx)

    musica = None
    if P.get('musica'):
        musica = A.resolver(P['musica'])
        if 'golpe' in musica:   # segundo de la canción donde está su golpe → cae justo en "drop"
            g = musica.pop('golpe')
            if 'drop' not in musica: falla('musica.golpe necesita musica.drop (el instante del video donde debe caer)')
            musica = {'archivo': musica['archivo'], 'desde': round(g - musica['drop'], 3), **{k: v for k, v in musica.items() if k != 'archivo'}}
        if musica.get('archivo') and not os.path.exists(os.path.join(proy, musica['archivo'])): avisos.append(f'no está la música {musica["archivo"]}')

    K = kit(); voz = P.get('voz', 'corte/cam.mov'); fps = str(P['fps']) if P.get('fps') else fps_proyecto(proy, voz)
    cfg = {'nombre': P.get('nombre', K.get('nombre', '')), 'handle': P.get('handle', K.get('handle', '')), 'fps': fps, 'cola': P.get('cola', .25), 'voz': voz,
           'salida': P.get('salida') or f"salida/{P.get('archivo', os.path.basename(proy))}.mp4"}
    cfg.update(copy.deepcopy(P['_cine']))
    if P.get('persona') is not False:
        pe = dict(P.get('persona') or {}); pe['n'] = contar_cuadros(proy, pe.get('crudos', 'cuadros'), voz, fps)
        cfg['persona'] = pe
    if caras is not None: cfg['caras'] = caras; cfg['caraH'] = caraH
    cfg['cortes'] = cortes
    if sfx or 'sfx' in P or SC: cfg['sfx'] = sfx
    if musica: cfg['musica'] = musica
    cfg['escenas'] = esc_out
    for a in avisos: print(f'  ⚠ {a}')
    if escribir:
        if alin: guardar(os.path.join(proy, 'voz', 'palabras.json'), W)
        guardar(os.path.join(proy, 'cine.json'), cfg)
    return cfg


def resumen(cfg):
    """Líneas para revisar de un vistazo qué quedó en cada escena."""
    out = [f"{len(cfg['escenas'])} escenas · {sum(len(e['grupos']) for e in cfg['escenas'])} grupos · {len(cfg.get('cortes', []))} cortes · "
           f"{len(cfg.get('sfx', []))} efectos · fps {cfg['fps']} · persona.n {cfg.get('persona', {}).get('n', '-')}"]
    for e in cfg['escenas']:
        capas = [k for k in e if k not in ('visual', 'tema', 'textoTema', 'grupos', 'caraY', 'trans', 'inicio')]
        txt = ' / '.join(' '.join(l for l in g['lineas']) for g in e['grupos'])
        out.append(f"  [{e.get('visual', 'persona')}{'·' + e['trans'] if e.get('trans') else ''}]{' ' + ','.join(capas) if capas else ''}  {txt[:110]}")
    return out
