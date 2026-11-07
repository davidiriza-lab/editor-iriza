"""Baja los logos de una lista de herramientas (favicon de Google a 256 px, o apple-touch-icon si sale más grande).
Uso: python3 plantillas/lista-herramientas/descargar_logos.py <logos.json> <carpeta_salida>
logos.json = {"nombre_archivo": "dominio.com", ...}   (ej. plantillas/lista-herramientas/logos.json)
Los que no tienen logo oficial se dibujan con sus iniciales en el motor (fichaLogo). Revisar siempre la hoja que genera.
"""
import json, os, struct, sys, urllib.request
H = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
lado = lambda b: struct.unpack('>I', b[16:20])[0] if b[:8] == b'\x89PNG\r\n\x1a\n' else 0
def baja(u):
    try: return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=15).read()
    except Exception: return b''
L = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
for k, d in L.items():
    mejor = baja(f'https://www.google.com/s2/favicons?domain={d}&sz=256')
    for u in (f'https://{d}/apple-touch-icon.png', f'https://www.{d}/apple-touch-icon.png'):
        b = baja(u)
        if lado(b) > lado(mejor): mejor = b
    if mejor: open(os.path.join(out, k + '.png'), 'wb').write(mejor); print('✓', k, lado(mejor) or '?', 'px')
    else: print('✗', k, '(se dibuja con iniciales)')
