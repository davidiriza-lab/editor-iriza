"""Hoja de cortes: por cada corte del video final, el cuadro de antes y el de después lado a lado (para revisar saltos a ojo).
Uso: python3 proyectos/<proyecto>/hoja_cortes.py <clave>  → <clave>/salida/hoja_cortes.jpg"""
import sys, json, subprocess, tempfile, os
B = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))   # carpeta del proyecto (copia de esta plantilla); correr desde la raíz del repo
K = sys.argv[1]; P = f'{B}/{K}'; mp4 = f'{P}/salida/{K}.mp4'; tmp = tempfile.mkdtemp()
cortes = json.load(open(f'{P}/cine.json'))['cortes']; ins = []
for i, t in enumerate(cortes):
    for j, dt in enumerate((-.06, .06)):
        f = os.path.join(tmp, f'{i:02d}{j}.jpg')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{max(0, t + dt):.3f}', '-i', mp4, '-frames:v', '1', '-vf',
                        f"scale=200:-2,drawtext=text='{t:.2f}{'a' if j == 0 else 'd'}':x=6:y=6:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.6", f], check=True)
        ins.append(f)
n = len(ins); cols = 10
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-pattern_type', 'glob', '-i', os.path.join(tmp, '*.jpg'), '-vf', f'tile={cols}x{(n + cols - 1) // cols}:padding=3:color=red', '-frames:v', '1', '-q:v', '3', f'{P}/salida/hoja_cortes.jpg'], check=True)
print(f'{P}/salida/hoja_cortes.jpg · {len(cortes)} cortes')
