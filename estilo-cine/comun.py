"""Lo que comparten los scripts del motor: un solo lugar para sondear un video, sus fps, su color y si es HDR.

Antes cada script traía su copia (y sus fps fijos: 23.976 aquí, 24 allá). Regla: nada de fps escritos a mano;
se leen del archivo. Uso: `from comun import fps_nativo, fps_num, filtro_jpg, es_hdr, a_sdr` (los scripts del
motor se corren como `python3 estilo-cine/<script>.py`, así que este archivo ya está en la ruta de importación).
"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sonda(f):
    """Datos del primer video del archivo (dict de ffprobe; vacío si no tiene video)."""
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams', '-of', 'json', f], capture_output=True, text=True).stdout
    s = (json.loads(r or '{}').get('streams') or [{}])[0]
    return s


def fps_nativo(f, si_no='24000/1001'):
    """Los fps reales del archivo como texto ("24/1", "30000/1001"…). Cortar o indexar a otros fps repite o tira
    cuadros y desfasa la voz."""
    r = sonda(f).get('r_frame_rate', '')
    return r if r and r != '0/0' else si_no


def fps_num(txt):
    """"30000/1001" → 29.97…  ·  "24" → 24.0  (sin eval)."""
    txt = str(txt)
    if '/' in txt:
        a, b = txt.split('/')
        return float(a) / (float(b) or 1)
    return float(txt)


def es_hdr(f):
    """HLG o PQ (iPhone, DJI): si se edita sin convertir a Rec.709 se ve lavado."""
    return sonda(f).get('color_transfer') in ('arib-std-b67', 'smpte2084')


def a_sdr(f, carpeta):
    """Convierte un video HDR a Rec.709 con el mapeo de tonos de macOS (bin/sdr) y devuelve la ruta nueva.
    Si ya se convirtió antes, la reutiliza. Fuera de Mac (sin bin/sdr) avisa y devuelve el original."""
    herr = next((p for p in (os.path.join(RAIZ, 'bin', 'sdr'), os.path.join(RAIZ, 'editor-testimoniales', 'editor', 'bin', 'sdr')) if os.path.exists(p)), None)
    if not herr:
        print(f'⚠ {os.path.basename(f)} es HDR y falta bin/sdr (./instalar.sh): se edita tal cual y puede verse lavado', file=sys.stderr)
        return f
    os.makedirs(carpeta, exist_ok=True)
    sal = os.path.join(carpeta, os.path.splitext(os.path.basename(f))[0] + '.mov')
    if not os.path.exists(sal) or os.path.getmtime(sal) < os.path.getmtime(f):
        print(f'  {os.path.basename(f)} viene en HDR: se convierte a Rec.709 → {sal}', flush=True)
        tmp = os.path.join(carpeta, '_' + os.path.basename(sal))
        subprocess.run([herr, f, tmp], check=True)
        os.replace(tmp, sal)
    return sal


_ZSCALE = None


def tiene_zscale():
    """zscale (libzimg) convierte color sin sesgo; viene en ffmpeg-full. Sin él se usa swscale en modo preciso."""
    global _ZSCALE
    if _ZSCALE is None:
        _ZSCALE = ' zscale ' in subprocess.run(['ffmpeg', '-hide_banner', '-filters'], capture_output=True, text=True).stdout
    return _ZSCALE


def filtro_jpg(f):
    """Filtro de ffmpeg para sacar cuadros JPG fieles al video.

    Un JPG siempre se lee como BT.601 de rango completo (así lo abre Chrome, que es quien dibuja el video). Sin este
    filtro ffmpeg guardaba los cuadros con la matriz del video (BT.709) y la piel salía con ~2 % menos rojo que en la
    cámara (−4.8 de rojo y −2.3 de verde sobre 255, medido contra una conversión de referencia el 12-nov-2026).
    Con zscale el error medio queda en 0.05; con swscale preciso, en menos de 1."""
    s = sonda(f)
    m = s.get('color_space') or ''
    hd = max(int(s.get('width', 0)), int(s.get('height', 0))) >= 1280
    de = 'bt601' if m in ('bt470bg', 'smpte170m') else 'bt2020' if m.startswith('bt2020') else 'bt709' if (m == 'bt709' or hd) else 'bt601'
    completo = s.get('color_range') == 'pc' or str(s.get('pix_fmt', '')).startswith('yuvj')
    if tiene_zscale():
        zm = {'bt601': '470bg', 'bt709': '709', 'bt2020': '2020_ncl'}[de]
        return f"zscale=min={zm}:rin={'full' if completo else 'limited'}:m=470bg:r=full,format=yuvj420p"
    return f"scale=in_color_matrix={de}:in_range={'full' if completo else 'tv'}:out_color_matrix=bt601:out_range=full:flags=bicubic+accurate_rnd+full_chroma_int"


def vf_entrega():
    """Filtro para codificar a video lo que sale de cuadros JPG o de Chrome (BT.601 completo) en el estándar de entrega:
    Rec.709 de rango de video, con etiquetas. Antes el MP4 salía "yuvj420p / bt470bg": un reproductor que no lee
    etiquetas lo mostraba con ~4 % de error de color y contraste (medido el 12-nov-2026). render.mjs usa el mismo filtro."""
    base = 'zscale=min=470bg:rin=full:m=709:r=limited' if tiene_zscale() else \
           'scale=in_color_matrix=bt601:in_range=full:out_color_matrix=bt709:out_range=tv:flags=bicubic+accurate_rnd+full_chroma_int'
    return base + ',format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv'
