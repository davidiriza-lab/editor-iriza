"""Analiza un video de tomas de stock (B-roll) cuadro por cuadro y guarda qué tramos se pueden usar.

Uso:  .venv/bin/python stock.py <video_stock> [--ver]
Genera <video_stock>.tomas.json junto al video (se reusa en todos los proyectos):
  planos:   [inicio, fin] de cada plano (cambio de plano = salto grande de imagen entre cuadros)
  dividida: cuadros con pantalla dividida (franja oscura horizontal o vertical cruzando el cuadro) → no se usan
  tramos:   pedazos dentro de un plano (nunca cruzan un cambio de plano), ≥ 0.25 s, marcados si son pantalla dividida
  limpios:  los tramos a pantalla completa (se prefieren)
armar.py lo usa con proyecto.json -> "broll_auto". --ver arma una hoja de contacto de los tramos limpios.
"""
import sys, os, json, subprocess
import numpy as np

src = os.path.abspath(sys.argv[1]); out = src + ".tomas.json"
pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate", "-of", "json", src], capture_output=True, text=True)
s = json.loads(pr.stdout)["streams"][0]; fps = eval(s["r_frame_rate"])
W, H = 108, 192 if s["height"] > s["width"] else 108   # cuadros chiquitos en gris bastan para cortes y franjas
if s["width"] > s["height"]: W, H = 192, 108
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(float); n = len(F)

# 1. cambios de plano: diferencia entre cuadros en el cuadro completo y en cada mitad (en pantalla dividida a veces cambia
#    solo una mitad), pico aislado frente a sus vecinos
D = np.abs(np.diff(F, axis=0)); h2 = H // 2
corte = []
for d in (D.mean(axis=(1, 2)), D[:, :h2].mean(axis=(1, 2)), D[:, h2:].mean(axis=(1, 2))):
    d = np.r_[0, d]
    corte += [i for i in range(1, n) if d[i] > 18 and d[i] > 3 * np.median(d[max(1, i - 6):i + 7])]
corte = sorted({i for i in corte if not any(0 < i - j < 3 for j in corte)})
bordes = [0] + corte + [n]
planos = [[round(a / fps, 3), round(b / fps, 3)] for a, b in zip(bordes, bordes[1:]) if b - a > 1]

# 2. pantalla dividida: franja casi negra y uniforme que cruza el cuadro entre el 25 % y el 75 %
def dividida(f):
    for eje in (1, 0):                       # filas (división horizontal), columnas (vertical)
        perfil = f.mean(axis=eje); var = f.std(axis=eje); L = len(perfil)
        for k in range(int(L * .25), int(L * .75)):
            if perfil[k] < 22 and var[k] < 10 and (perfil[max(0, k - 6)] > 45 or perfil[min(L - 1, k + 6)] > 45): return True
    return False
div = np.array([dividida(f) for f in F])

# 3. tramos usables: dentro de un plano (2 cuadros de margen en cada orilla), del mismo tipo (completa / dividida), ≥ 0.25 s
tramos = []
for a, b in zip(bordes, bordes[1:]):
    i = a + 2
    while i < b - 2:
        j = i
        while j < b - 2 and div[j] == div[i]: j += 1
        if (j - i) / fps >= .25: tramos.append({"a": round(i / fps, 3), "b": round(j / fps, 3), "dividida": bool(div[i])})
        i = j
limpios = [[t["a"], t["b"]] for t in tramos if not t["dividida"]]
json.dump({"fuente": src, "fps": fps, "duracion": round(n / fps, 3), "planos": planos,
           "dividida_seg": round(div.sum() / fps, 2), "tramos": tramos, "limpios": limpios}, open(out, "w"), indent=1)
print(f"✓ {len(planos)} planos · {div.sum() / fps:.1f}s con pantalla dividida · {len(tramos)} tramos usables ({len(limpios)} a pantalla completa) → {out}")
for t in tramos: print(f"   {t['a']:6.2f}–{t['b']:6.2f}  ({t['b'] - t['a']:.2f}s){'  dividida' if t['dividida'] else ''}")

if "--ver" in sys.argv:
    tiles = []
    for t in tramos: tiles += ["-ss", str((t["a"] + t["b"]) / 2), "-i", src]
    N = len(tramos); cols = min(8, N)
    fc = "".join(f"[{k}:v]scale=180:320[t{k}];" for k in range(N))
    fc += "".join(f"[t{k}]" for k in range(N)) + f"xstack=inputs={N}:layout=" + "|".join(f"{(k % cols) * 180}_{(k // cols) * 320}" for k in range(N)) + ":fill=black"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *tiles, "-filter_complex", fc, "-frames:v", "1", src + ".tomas.jpg"], check=True)
    print("hoja de contacto:", src + ".tomas.jpg")
