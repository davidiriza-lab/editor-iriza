#!/usr/bin/env python3
"""Cliente mínimo de Higgsfield (imágenes y video).

La llave vive en el Llavero de macOS (servicio `videos-voz-ia.higgsfield`, formato id:secreto).

Uso:
  hf.py imagen "<prompt>" salida.png [--modelo grok|soul] [--ratio 9:16]
  hf.py video  entrada.png "<prompt>" salida.mp4 [--dur 5] [--modelo kling3-turbo|kling3-std]
"""
import argparse, json, subprocess, sys, time, urllib.request, urllib.error, uuid
from pathlib import Path

BASE = "https://api.higgsfield.ai"
IMAGEN = {
    "grok": ("xai/grok-imagine-image-2.0", lambda p, r: {"prompt": p, "aspect_ratio": r, "resolution": "2k", "quality": "medium"}),
    "soul": ("higgsfield-ai/soul/v2/standard", lambda p, r: {"prompt": p, "aspect_ratio": r, "resolution": "1080p"}),
}
VIDEO = {
    "kling3-turbo": "kling-video/v3.0-turbo/image-to-video",
    "kling3-std": "kling-video/v3.0/std/image-to-video",
}


def llave():
    k = subprocess.run(["security", "find-generic-password", "-s", "videos-voz-ia.higgsfield", "-w"],
                       capture_output=True, text=True).stdout.strip()
    if not k:
        sys.exit("No hay llave de Higgsfield en el Llavero (servicio videos-voz-ia.higgsfield).")
    return k


def pedir(metodo, url, cuerpo=None, auth=True, headers=None):
    h = {"Content-Type": "application/json"} if cuerpo is not None else {}
    if auth:
        h["Authorization"] = f"Key {llave()}"
    h.update(headers or {})
    data = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url, data=data, headers=h, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            t = r.read()
            return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"Higgsfield {e.code}: {e.read().decode()[:500]}")


def subir(ruta):
    ruta = Path(ruta)
    ct = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}[ruta.suffix.lower()]
    u = pedir("POST", f"{BASE}/files/generate-upload-url", {"content_type": ct})
    req = urllib.request.Request(u["upload_url"], data=ruta.read_bytes(), headers=u["upload_headers"], method="PUT")
    urllib.request.urlopen(req, timeout=120).read()
    return u["public_url"]


def correr(endpoint, args):
    r = pedir("POST", f"{BASE}/{endpoint}", args, headers={"Idempotency-Key": str(uuid.uuid4())})
    rid = r["request_id"]
    print(f"  {endpoint} → {rid}", flush=True)
    espera = 3
    while True:
        time.sleep(espera)
        s = pedir("GET", f"{BASE}/requests/{rid}/status")
        st = s.get("status")
        if st == "completed":
            return s
        if st in ("failed", "nsfw", "canceled", "cancelled"):
            sys.exit(f"Higgsfield {rid}: {st} {json.dumps(s)[:400]}")
        espera = min(espera * 1.4, 15)


def bajar(url, salida):
    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, salida)
    print(f"  ✓ {salida}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("imagen"); a.add_argument("prompt"); a.add_argument("salida")
    a.add_argument("--modelo", default="grok", choices=IMAGEN); a.add_argument("--ratio", default="9:16")
    b = sub.add_parser("video"); b.add_argument("entrada"); b.add_argument("prompt"); b.add_argument("salida")
    b.add_argument("--dur", type=int, default=5); b.add_argument("--modelo", default="kling3-turbo", choices=VIDEO)
    o = ap.parse_args()
    if o.cmd == "imagen":
        ep, f = IMAGEN[o.modelo]
        s = correr(ep, f(o.prompt, o.ratio))
        bajar(s["images"][0]["url"], o.salida)
    else:
        url = subir(o.entrada)
        s = correr(VIDEO[o.modelo], {"prompt": o.prompt, "image_url": url, "duration": o.dur, "resolution": "1080p"})
        bajar(s["video"]["url"], o.salida)


if __name__ == "__main__":
    main()
