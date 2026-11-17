"""Genera imágenes en paralelo. Por defecto con tu SUSCRIPCIÓN de ChatGPT (imagen-gpt, de github.com/davidiriza-lab/claude-con-gemini-y-gpt), sin gastar API.
Uso:      python3 proyectos/<proyecto>/gen_img.py imagenes.json
Por API:  OPENAI_API_KEY=… python3 proyectos/<proyecto>/gen_img.py imagenes.json --api   (se cobra por uso de la API)
imagenes.json = [{"nombre": "mesa", "calidad": "low", "prompt": "…"}]  → _img/<nombre>.jpg (1024x1536)
"calidad" y "modelo" solo aplican en modo --api; "size" decide el formato en ambos modos."""
import sys, os, json, base64, subprocess, urllib.request, concurrent.futures as cf
API = '--api' in sys.argv
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_img')
IMAGEN_GPT = os.path.expanduser('~/.local/bin/imagen-gpt')
if not API and not os.path.exists(IMAGEN_GPT):
    sys.exit('✗ No está imagen-gpt (https://github.com/davidiriza-lab/claude-con-gemini-y-gpt). Instálalo para usar tu suscripción de ChatGPT, '
             'o corre con --api y OPENAI_API_KEY en el entorno.')
os.makedirs(OUT, exist_ok=True)


def formato(size):
    w, h = (int(x) for x in size.split('x'))
    return 'vertical' if h > w else 'horizontal' if w > h else 'cuadrado'


def gen(it):
    f = os.path.join(OUT, it['nombre'] + '.jpg')
    if os.path.exists(f): return f"· {it['nombre']} ya existe"
    for intento in range(3):
        m = _gen_api(it, f) if API else _gen_suscripcion(it, f)
        if m.startswith('✓') or ' 4' in m[:12]: return m
    return m


def _gen_suscripcion(it, f):
    size = it.get('size', '1024x1536')
    lado = max(int(x) for x in size.split('x'))
    cmd = [IMAGEN_GPT, it['prompt'], '-o', f, '--formato', formato(size), '--max', str(lado)]
    for r in it.get('refs', []):
        cmd += ['--ref', r]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0 and os.path.exists(f):
        return f"✓ {it['nombre']} → {f} · suscripción ChatGPT"
    return f"✗ {it['nombre']}: {(r.stdout + r.stderr).strip()[-300:]}"


def _gen_api(it, f):
    K = os.environ.get('OPENAI_API_KEY') or sys.exit('✗ Falta OPENAI_API_KEY en el entorno (modo --api).')
    body = json.dumps({'model': it.get('modelo', 'gpt-image-2'), 'prompt': it['prompt'], 'size': it.get('size', '1024x1536'), 'quality': it.get('calidad', 'low'),
                       'output_format': 'jpeg', 'output_compression': 85, 'n': 1}).encode()
    req = urllib.request.Request('https://api.openai.com/v1/images/generations', body, {'Authorization': f'Bearer {K}', 'Content-Type': 'application/json'})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=600))
    except urllib.error.HTTPError as e:
        return f"✗ {it['nombre']}: {e.code} {e.read().decode()[:300]}"
    except Exception as e:
        return f"✗ {it['nombre']}: {type(e).__name__} (reintento)"
    open(f, 'wb').write(base64.b64decode(r['data'][0]['b64_json']))
    u = r.get('usage', {}); return f"✓ {it['nombre']} → {f} · tokens {u.get('total_tokens', '?')}"


archivo = next(a for a in sys.argv[1:] if not a.startswith('--'))
with cf.ThreadPoolExecutor(6 if API else 3) as ex:
    for m in ex.map(gen, json.load(open(archivo))): print(m, flush=True)
