"""cine.json de un video de este proyecto: python3 armar.py <clave>   (desde la raíz del repo o desde aquí)

Lee planes.py → PLANES[clave] y lo arma con la biblioteca del motor (estilo-cine/armado.py) usando la receta
"anuncio-por-frases" (aprobada el 4-nov-2026): subtítulos por frase de 2-4 palabras en una línea, anclas @palabra#n, un solo
encuadre por video (caras por pieza, caraH = 1.22 × mediana, caraY = mediana real), cambios de escena pegados a un corte
arrancan EN el corte, la palabra que abre una pieza empieza después del corte, whoosh en cada cambio de visual.
Escribe <clave>/cine.json y <clave>/voz/palabras.json (inicios ajustados; el original queda en voz/palabras_orig.json).

Un PLANES[clave] es un plan.json escrito en Python: también se puede armar con
    python3 estilo-cine/armar.py proyectos/<proyecto>/<clave>   (con "receta": "anuncio-por-frases" en su plan.json)
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = AQUI
while not os.path.exists(os.path.join(RAIZ, 'estilo-cine', 'armado.py')):
    if os.path.dirname(RAIZ) == RAIZ: sys.exit('✗ no encuentro estilo-cine/armado.py: esta carpeta debe vivir dentro del repo (proyectos/<nombre>/)')
    RAIZ = os.path.dirname(RAIZ)
sys.path[:0] = [AQUI, os.path.join(RAIZ, 'estilo-cine')]
import armado  # noqa: E402
from planes import PLANES  # noqa: E402

if len(sys.argv) < 2 or sys.argv[1] not in PLANES: sys.exit(__doc__ + f'\nClaves en planes.py: {", ".join(PLANES)}')
K = sys.argv[1]; P = PLANES[K]
cfg = armado.armar(os.path.join(AQUI, P.get('dir', K)), {'receta': 'anuncio-por-frases', 'archivo': K, **P})
print(f"✓ {K}: {len(cfg['escenas'])} escenas, {sum(len(e['grupos']) for e in cfg['escenas'])} frases; caras h {[int(c['h']) for c in cfg.get('caras', [])]}")
