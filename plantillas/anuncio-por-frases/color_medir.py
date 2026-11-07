"""Mide por pieza del corte: piel de la cara (Lab mediana del centro de la cara) y fondo (L fuera de la silueta).
Uso: .venv/bin/python proyectos/<proyecto>/color_medir.py <clave> [--de cuadros_orig] → imprime y deja <clave>/color_piezas.json"""
import sys, os, json, numpy as np, cv2
B = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))   # carpeta del proyecto (copia de esta plantilla); correr desde la raíz del repo
K = sys.argv[1]; P = f'{B}/{K}'
DE = sys.argv[sys.argv.index('--de') + 1] if '--de' in sys.argv else ('cuadros_orig' if os.path.isdir(f'{P}/cuadros_orig') else 'cuadros')
pz = json.load(open(f'{P}/corte/mapa.json'))['piezas']; C = [c for c in json.load(open(f'{P}/corte/caras.json'))['f'] if len(c) >= 5]
n = len([f for f in os.listdir(f'{P}/{DE}') if f.endswith('.jpg')])
def cara_en(t):
    c = min(C, key=lambda c: abs(c[0] - t)); return c if abs(c[0] - t) < .25 else None
out, t0 = [], 0.0
for k, (a, b) in enumerate(pz):
    t1 = t0 + (b - a); f0, f1 = int(round(t0 * 24)) + 1, min(n, int(round(t1 * 24)))
    L, A, B, CR, CB, BG, FG = [], [], [], [], [], [], []
    for fi in np.linspace(f0, f1, min(10, max(1, f1 - f0 + 1))).astype(int):
        c = cara_en((fi - 1) / 24)
        if c is None: continue
        im = cv2.imread(f'{P}/{DE}/{fi:05d}.jpg'); m = cv2.imread(f'{P}/mascaras/{fi:05d}.jpg', 0)
        x0, y0, x1, y1 = c[1:5]; w, h = x1 - x0, y1 - y0
        r = im[int(y0 + .4 * h):int(y0 + .82 * h), int(x0 + .28 * w):int(x1 - .28 * w)]
        if r.size == 0: continue
        lab = cv2.cvtColor(r, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(float); ycc = cv2.cvtColor(r, cv2.COLOR_BGR2YCrCb).reshape(-1, 3).astype(float)
        ok = (lab[:, 0] > 50) & (lab[:, 0] < 240)
        if ok.sum() < 50: continue
        L.append(np.median(lab[ok, 0])); A.append(np.median(lab[ok, 1])); B.append(np.median(lab[ok, 2])); CR.append(np.median(ycc[ok, 1])); CB.append(np.median(ycc[ok, 2]))
        if m is not None:
            mm = cv2.resize(m, (im.shape[1], im.shape[0])) > 128; Lf = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)[..., 0]
            BG.append(float(np.percentile(Lf[~mm], 90)) if (~mm).sum() else 0); FG.append(float(np.median(Lf[mm])) if mm.sum() else 0)
    md = lambda v: round(float(np.median(v)), 1) if v else None
    out.append(dict(pieza=k, f0=f0, f1=f1, L=md(L), a=md(A), b=md(B), cr=md(CR), cb=md(CB), fondo90=md(BG), persona=md(FG)))
    t0 = t1
json.dump(out, open(f'{P}/color_piezas.json', 'w'), indent=1)
for o in out: print(K, o)
