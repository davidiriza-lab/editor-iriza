"""Genera la voz de un proyecto con ElevenLabs y los tiempos de cada palabra.

Uso: python3 motor/voz.py proyectos/<nombre>
Lee guion.json, une el texto "voz" de todas las pantallas y llama a ElevenLabs
(endpoint with-timestamps). Deja en proyectos/<nombre>/voz/:
  voz.mp3          audio
  palabras.json    [{texto, inicio, fin, pantalla}] con tiempos en segundos
Si el texto y los ajustes no cambiaron, reutiliza el audio (no gasta créditos).
"""
import base64, hashlib, json, subprocess, sys, urllib.request, urllib.error
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LLAVERO = "videos-voz-ia.elevenlabs"


def clave():
    r = subprocess.run(["security", "find-generic-password", "-s", LLAVERO, "-w"], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("No hay API key en el Llavero. Corre: ./motor/clave.sh")
    return r.stdout.strip()


def texto_y_rangos(guion):
    """Une las voces de las pantallas y guarda qué rango de letras es de cada una."""
    partes, rangos, pos = [], [], 0
    for i, p in enumerate(guion["pantallas"]):
        t = " ".join(p.get("voz", "").split())
        if not t:
            rangos.append(None)
            continue
        if partes:
            pos += 1  # el espacio que las une
        rangos.append((pos, pos + len(t)))
        partes.append(t)
        pos += len(t)
    return " ".join(partes), rangos


def palabras(alin, rangos):
    chars, ini, fin = alin["characters"], alin["character_start_times_seconds"], alin["character_end_times_seconds"]
    out, actual = [], None
    for i, c in enumerate(chars):
        if c.isspace():
            actual = None
            continue
        if actual is None:
            pant = next((k for k, r in enumerate(rangos) if r and r[0] <= i < r[1]), None)
            actual = {"texto": "", "inicio": ini[i], "fin": fin[i], "pantalla": pant}
            out.append(actual)
        actual["texto"] += c
        actual["fin"] = fin[i]
    return out


def main():
    proy = Path(sys.argv[1]).resolve()
    cfg = json.loads((RAIZ / "config.json").read_text())["voz"]
    guion = json.loads((proy / "guion.json").read_text())
    texto, rangos = texto_y_rangos(guion)
    huella = hashlib.sha1(json.dumps([texto, cfg["voice_id"], cfg["modelo"], cfg["ajustes"]]).encode()).hexdigest()[:12]
    d = proy / "voz"; d.mkdir(exist_ok=True)
    cache = d / f"respuesta_{huella}.json"

    if cache.exists():
        resp = json.loads(cache.read_text())
        print("Voz sin cambios: reutilizo el audio (0 créditos).")
    else:
        body = json.dumps({"text": texto, "model_id": cfg["modelo"], "voice_settings": cfg["ajustes"]}).encode()
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{cfg['voice_id']}/with-timestamps?output_format=mp3_44100_128"
        req = urllib.request.Request(url, data=body, headers={"xi-api-key": clave(), "Content-Type": "application/json"})
        try:
            resp = json.load(urllib.request.urlopen(req, timeout=300))
        except urllib.error.HTTPError as e:
            sys.exit(f"ElevenLabs respondió {e.code}: {e.read()[:300].decode(errors='ignore')}")
        cache.write_text(json.dumps(resp))
        print(f"Voz generada: {len(texto)} caracteres.")

    (d / "voz.mp3").write_bytes(base64.b64decode(resp["audio_base64"]))
    ws = palabras(resp["alignment"], rangos)
    (d / "palabras.json").write_text(json.dumps(ws, ensure_ascii=False, indent=1))
    print(f"{len(ws)} palabras, {ws[-1]['fin']:.1f} s  →  {d / 'voz.mp3'}")


if __name__ == "__main__":
    main()
