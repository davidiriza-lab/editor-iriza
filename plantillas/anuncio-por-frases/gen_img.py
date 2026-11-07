"""Genera imágenes con la API de OpenAI (gpt-image-2) en paralelo. La llave se lee de OPENAI_API_KEY (nunca de un archivo).
Uso: OPENAI_API_KEY=… python3 proyectos/<proyecto>/gen_img.py imagenes.json
imagenes.json = [{"nombre": "mesa", "calidad": "low", "prompt": "…"}]  → _img/<nombre>.jpg (1024x1536)"""
import sys, os, json, base64, urllib.request, concurrent.futures as cf
K = os.environ['OPENAI_API_KEY']; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_img')
def gen(it):
    f = os.path.join(OUT, it['nombre'] + '.jpg')
    if os.path.exists(f): return f"· {it['nombre']} ya existe"
    for intento in range(3):
        m = _gen(it, f)
        if m.startswith('✓') or ' 4' in m[:12]: return m
    return m
def _gen(it, f):
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
with cf.ThreadPoolExecutor(6) as ex:
    for m in ex.map(gen, json.load(open(sys.argv[1]))): print(m, flush=True)
