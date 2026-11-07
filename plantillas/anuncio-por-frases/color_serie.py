"""Preset de color de una serie: la misma piel en todos los videos y en cada toma.
Se aplica sobre el material limpio (cuadros sin gráficos): cuadros_orig/ (copia intacta del corte) → cuadros/.
Por pieza del corte (color_piezas.json, de color_medir.py):
  - piel (silueta ∩ tono de la cara medido en esa pieza) → al tono objetivo: menos rojo/magenta, un poco hacia amarillo
  - exposición de la cara al objetivo (curva en L; la persona completa, el fondo a medias) y, si el fondo es mucho más
    claro que la cara (p. ej. una ventana), se bajan sus altas luces
  - balance de blancos solo en lo neutro (pared gris, saco crema): corrige el tinte verde de un muro sin tocar colores fuertes
  - look de la serie: saturación −5 % (los amarillos fuertes no se tocan), contraste un poco arriba
  - --cuadro: un objeto rojo/naranja del fondo que distrae, con menos saturación
Uso: .venv/bin/python proyectos/<proyecto>/color_serie.py <clave> [--cuadro] [--prueba]   (--prueba: solo hoja antes/después)"""
import sys, os, json, shutil, numpy as np, cv2
from concurrent.futures import ThreadPoolExecutor
B = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))   # carpeta del proyecto (copia de esta plantilla); correr desde la raíz del repo
K = sys.argv[1]; P = f'{B}/{K}'; CUADRO = '--cuadro' in sys.argv; PRUEBA = '--prueba' in sys.argv
OBJ = dict(L=138.0, a=147.5, b=145.5)   # tono de piel objetivo en Lab de OpenCV (piel un poco menos roja y más amarilla, medios claros); ajústalo con lo que mide color_medir.py
NEUTRO = (129.0, 131.0)                 # gris ligeramente cálido
if not os.path.isdir(f'{P}/cuadros_orig'): shutil.copytree(f'{P}/cuadros', f'{P}/cuadros_orig')
PZ = json.load(open(f'{P}/color_piezas.json'))
ok = [p for p in PZ if p['L'] is not None]
for p in PZ:   # pieza sin cara medida: la vecina más cercana
    if p['L'] is None:
        v = min(ok, key=lambda q: abs(q['pieza'] - p['pieza'])); p.update({k: v[k] for k in ('L', 'a', 'b', 'cr', 'cb', 'fondo90')})
n = len([f for f in os.listdir(f'{P}/cuadros_orig') if f.endswith('.jpg')])
pieza_de = np.zeros(n + 2, int)
for i, p in enumerate(PZ): pieza_de[p['f0']:p['f1'] + 1] = i
pieza_de[PZ[-1]['f1'] + 1:] = len(PZ) - 1
x = np.arange(256, dtype=np.float32)
S_CURVA = x + 10 * np.sin(np.pi * (x / 255 * 2 - 1)) * (x / 255) * (1 - x / 255) * 4 * .5   # contraste suave en S

def params(p):
    da, db = np.clip((OBJ['a'] - p['a']) * .85, -11, 11), np.clip((OBJ['b'] - p['b']) * .7, -9, 9)
    dl = float(np.clip((OBJ['L'] - p['L']) * .8, -9, 24))
    L0 = p['L'] / 255; g = np.log(np.clip(L0 + dl / 255, .05, .95)) / np.log(L0)   # curva que lleva L0 a L0+dl
    return dict(da=da, db=db, g=g, cr=p['cr'], cb=p['cb'], ventana=p['fondo90'] - p['L'] > 70 and dl > 8)
PAR = [params(p) for p in PZ]

def procesa(img, m, q):
    h, w = img.shape[:2]
    m = cv2.GaussianBlur(cv2.resize(m, (w, h)).astype(np.float32) / 255, (0, 0), 3)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32); L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    ycc = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb).astype(np.float32)
    d2 = (ycc[..., 1] - q['cr']) ** 2 + (ycc[..., 2] - q['cb']) ** 2
    piel = cv2.GaussianBlur(m * np.exp(-d2 / (2 * 10 ** 2)) * np.clip((L - 35) / 30, 0, 1), (0, 0), 4)
    # 1) piel al tono objetivo
    A += piel * q['da']; B += piel * q['db']
    hp = np.degrees(np.arctan2(B - 128, A - 128)); rojiza = piel * np.clip((62 - hp) / 25, 0, 1)   # mejillas: rojos y naranjas −10 %
    A = 128 + (A - 128) * (1 - .10 * rojiza); B = 128 + (B - 128) * (1 - .06 * rojiza)
    # 2) balance de blancos en lo neutro (croma bajo)
    cro = np.sqrt((A - 128) ** 2 + (B - 128) ** 2); neu = np.clip(1 - cro / 14, 0, 1) * (L > 50) * (L < 235)
    if neu.sum() > 5000:
        ma, mb = (A * neu).sum() / neu.sum(), (B * neu).sum() / neu.sum()
        A += neu * np.clip((NEUTRO[0] - ma) * .6, -4, 4); B += neu * np.clip((NEUTRO[1] - mb) * .6, -4, 4)
    # 3) exposición: persona completa, fondo a medias
    Lc = 255 * np.power(np.clip(L / 255, 1e-4, 1), q['g'])
    wexp = m + (1 - m) * (.25 if q['ventana'] else .5); L = L + (Lc - L) * wexp
    if q['ventana']: L = L - (1 - m) * np.clip(L - 170, 0, None) * .45   # altas luces de la ventana
    # 4) look de la serie: S suave, −5 % de saturación salvo amarillos fuertes
    L = np.interp(L, x, S_CURVA).astype(np.float32)
    hue = np.degrees(np.arctan2(B - 128, A - 128)); amarillo = np.clip(1 - np.abs(hue - 84) / 24, 0, 1)
    f = .95 + .05 * amarillo
    if CUADRO:   # cuadro rojo/naranja del fondo (03): −50 % de saturación fuera de la silueta
        rojo = np.clip(1 - np.abs(hue - 35) / 35, 0, 1) * np.clip((np.sqrt((A - 128) ** 2 + (B - 128) ** 2) - 18) / 15, 0, 1)
        f = f * (1 - .5 * rojo * (1 - m))
    A = 128 + (A - 128) * f; B = 128 + (B - 128) * f
    out = np.dstack([np.clip(L, 0, 255), np.clip(A, 0, 255), np.clip(B, 0, 255)]).astype(np.uint8)
    return cv2.cvtColor(out, cv2.COLOR_LAB2BGR)

def uno(i):
    n5 = f'{i:05d}.jpg'; img = cv2.imread(f'{P}/cuadros_orig/{n5}'); k = i
    m = cv2.imread(f'{P}/mascaras/{n5}', 0)
    while m is None and k > 1: k -= 1; m = cv2.imread(f'{P}/mascaras/{k:05d}.jpg', 0)
    return procesa(img, m, PAR[pieza_de[i]])

if PRUEBA:   # un cuadro por pieza, antes arriba / después abajo
    fs = [(p['f0'] + p['f1']) // 2 for p in PZ]
    with ThreadPoolExecutor(8) as ex: des = list(ex.map(uno, fs))
    ant = [cv2.imread(f'{P}/cuadros_orig/{i:05d}.jpg') for i in fs]
    ch = lambda im: cv2.resize(im[380:1000, 290:790], (250, 310))   # zona de la cara
    hoja = np.vstack([np.hstack([ch(a) for a in ant]), np.hstack([ch(d) for d in des])])
    os.makedirs(f'{P}/salida', exist_ok=True); cv2.imwrite(f'{P}/salida/color_prueba.jpg', hoja, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f'{P}/salida/color_prueba.jpg'); sys.exit()
def escribe(i): cv2.imwrite(f'{P}/cuadros/{i:05d}.jpg', uno(i), [cv2.IMWRITE_JPEG_QUALITY, 95])
with ThreadPoolExecutor(8) as ex: list(ex.map(escribe, range(1, n + 1)))
print(f'✓ {K}: {n} cuadros con el color de la serie')
