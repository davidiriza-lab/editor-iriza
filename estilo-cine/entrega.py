"""Verificador y normalizador de entrega: revisa que el MP4 final esté listo para subirse a redes.

Sirve para cualquier MP4 (de este editor o de otra herramienta). El contrato por defecto es un vertical de 1080×1920
en H.264 + AAC a −14 LUFS; se puede cambiar con una sección "entrega" en config/kit.json (opcional).

  python3 estilo-cine/entrega.py verificar  <video.mp4> [--horizontal] [--sin-audio]
  python3 estilo-cine/entrega.py normalizar <video.mp4> [salida.mp4]

verificar  → tamaño, códecs, fps, audio y video del mismo largo, volumen (LUFS) y pico, cuadros negros,
             tramos congelados y PRIMER CUADRO (es la portada: no puede salir vacío). Sale con 1 si hay algo por corregir.
normalizar → deja el audio en el volumen del contrato (dos pasadas, sin tocar la imagen si ya cumple),
             yuv420p + faststart. Escribe "<nombre>.entrega.mp4" si no se da salida.
Corre ffmpeg con prioridad baja y a 270 px: no traba la compu.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

PERFIL = Path(__file__).resolve().parent.parent / "config" / "kit.json"
NICE = ["nice", "-n", "19"]
DEFECTO = {"ancho": 1080, "alto": 1920, "fps_validos": [23.976, 24, 30, 60], "video": "h264", "pixeles": "yuv420p",
           "audio": "aac", "lufs": -14, "tolerancia_lufs": 1.0, "pico_maximo_db": -1.0}


def contrato() -> dict:
    try:
        return {**DEFECTO, **json.loads(PERFIL.read_text()).get("entrega", {})}
    except (OSError, ValueError):
        return DEFECTO


def sonda(mp4: Path) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(mp4)], capture_output=True, text=True)
    d = json.loads(r.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s["codec_type"] == "video"), None)
    a = next((s for s in d.get("streams", []) if s["codec_type"] == "audio"), None)
    return {"v": v, "a": a, "dur": float(d.get("format", {}).get("duration", 0))}


def medir(mp4: Path, con_audio: bool) -> dict:
    """Una pasada: luz y cambio por cuadro, entropía (detalle) y volumen."""
    cmd = NICE + ["ffmpeg", "-v", "info", "-nostats", "-nostdin", "-threads", "2", "-i", str(mp4), "-vf",
                  "scale=270:-2,scdet=threshold=0:sc_pass=0,signalstats,metadata=print:file=-"]
    cmd += ["-af", "ebur128=peak=true"] if con_audio else ["-an"]
    out = subprocess.run(cmd + ["-f", "null", "-"], capture_output=True, text=True)
    t, dif, luz, act = [], [], [], None
    for linea in out.stdout.splitlines():
        if "pts_time:" in linea:
            act = float(linea.split("pts_time:")[1].split()[0])
        elif "lavfi.scd.score=" in linea:
            t.append(act); dif.append(float(linea.split("=")[1]))
        elif "lavfi.signalstats.YAVG=" in linea:
            luz.append(float(linea.split("=")[1]))
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", out.stderr)
    pico = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", out.stderr)
    return {"t": t, "dif": dif, "luz": luz, "lufs": float(lufs[-1]) if lufs else None, "pico": float(pico[-1]) if pico else None}


def bordes(mp4: Path, extra: list[str], filtro: str = "") -> list[float]:
    """Cuánto dibujo hay en cada cuadro (bordes detectados). Un cuadro vacío o de puro fondo da casi 0."""
    o = subprocess.run(NICE + ["ffmpeg", "-v", "info", "-nostats", "-nostdin", *extra, "-i", str(mp4), "-vf",
                               f"{filtro}scale=270:-2,edgedetect=low=0.08:high=0.2,signalstats,metadata=print:file=-", "-an", "-f", "null", "-"],
                       capture_output=True, text=True).stdout
    return [float(x.split("=")[1]) for x in o.splitlines() if "signalstats.YAVG=" in x]


def verificar(mp4: Path, horizontal: bool, sin_audio: bool) -> int:
    C = contrato()
    s = sonda(mp4)
    if not s["v"]:
        print(f"✗ {mp4.name}: no tiene pista de video"); return 1
    mal, avisos = [], []
    v, a = s["v"], s["a"]
    W, H = (C["alto"], C["ancho"]) if horizontal else (C["ancho"], C["alto"])
    if (v["width"], v["height"]) != (W, H):
        mal.append(f"tamaño    {v['width']}×{v['height']} (el contrato pide {W}×{H}{'' if horizontal else '; usa --horizontal si el video va en horizontal'})")
    if v["codec_name"] != C["video"]:
        mal.append(f"códec     video en {v['codec_name']} (se entrega en {C['video']})")
    if v.get("pix_fmt") not in (C["pixeles"], "yuvj420p"):   # yuvj420p = mismo formato en rango completo: se reproduce igual
        mal.append(f"píxeles   {v.get('pix_fmt')} (se entrega en {C['pixeles']}: otros formatos no abren en todos los celulares)")
    # color: el estándar es Rec.709 de rango de video. "yuvj420p" (rango completo) o sin etiqueta 709 se ve bien en la
    # mayoría de los reproductores, pero uno que no lea etiquetas cambia el contraste (~4 % medido el 12-nov-2026).
    if v.get("pix_fmt") == "yuvj420p" or v.get("color_range") == "pc" or v.get("color_space") not in ("bt709",):
        avisos.append(f"color     {v.get('pix_fmt')} / {v.get('color_space', 'sin etiqueta')} / rango {v.get('color_range', '?')}: lo estándar es yuv420p · bt709 · tv (el editor ya sale así; vuelve a renderizar o recodifica)")
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 0
    if not any(abs(fps - f) < 0.06 for f in C["fps_validos"]):
        avisos.append(f"fps       {fps:.2f} no está entre {C['fps_validos']}")
    if not a and not sin_audio:
        mal.append("audio     no tiene pista de audio (usa --sin-audio si es un inserto mudo)")
    if a:
        if a["codec_name"] != C["audio"]:
            mal.append(f"códec     audio en {a['codec_name']} (se entrega en {C['audio']})")
        da, dv = float(a.get("duration", s["dur"])), float(v.get("duration", s["dur"]))
        if abs(da - dv) > 0.12:
            mal.append(f"duración  el audio dura {da:.2f} s y el video {dv:.2f} s")
    m = medir(mp4, bool(a))
    if a and m["lufs"] is not None:
        if abs(m["lufs"] - C["lufs"]) > C["tolerancia_lufs"]:
            mal.append(f"volumen   {m['lufs']} LUFS (el contrato pide {C['lufs']} ± {C['tolerancia_lufs']}): corre `entrega.py normalizar`")
        if m["pico"] is not None and m["pico"] > C["pico_maximo_db"] + 0.5:
            avisos.append(f"pico      {m['pico']} dBFS (máximo {C['pico_maximo_db']}): puede saturar")
    n = len(m["dif"])
    paso = max(1, round(fps)) if fps else 30
    # en rango de video (lo estándar) el negro vale 16, no 0: se lleva a escala completa para comparar igual en los dos casos
    completo = v.get("color_range") == "pc" or str(v.get("pix_fmt", "")).startswith("yuvj")
    luz = m["luz"] if completo else [(y - 16) * 255 / 219 for y in m["luz"]]
    negros = [m["t"][i] for i, y in enumerate(luz[:n]) if y < 12]
    if negros:   # aviso, no error: hay pantallas negras a propósito (golpes, fundidos)
        avisos.append(f"negro     {len(negros)} cuadros casi negros (el primero en {negros[0]:.2f} s): confirma que es a propósito")
    quieto = 0
    for i, x in enumerate(m["dif"]):
        quieto = quieto + 1 if x < 0.002 else 0
        if quieto == paso * 2:
            avisos.append(f"congelado 2 s sin ningún movimiento hacia {m['t'][i]:.1f} s")
    # primer cuadro: es la portada. Si casi no tiene dibujo comparado con el resto del video, salió vacío.
    b0, resto = bordes(mp4, ["-t", "0.05"]), bordes(mp4, [], "fps=1,")
    if b0 and len(resto) > 2:
        medio = sorted(resto)[len(resto) // 2]
        if medio > 0.5 and b0[0] < medio * 0.25:
            mal.append(f"portada   el primer cuadro está casi vacío ({b0[0]:.1f} de dibujo contra {medio:.1f} del resto): es lo que se ve como portada")
    print(f"\n{mp4.name} · {v['width']}×{v['height']} · {fps:.2f} fps · {s['dur']:.1f} s · "
          f"{'volumen ' + str(m['lufs']) + ' LUFS' if m['lufs'] is not None else 'sin audio'}")
    for x in mal: print("✗ " + x)
    for x in avisos: print("⚠ " + x)
    print("✓ Cumple el contrato de entrega." if not mal and not avisos else f"\n{len(mal)} por corregir, {len(avisos)} advertencias.")
    return 1 if mal else 0


def normalizar(mp4: Path, salida: Path) -> int:
    C = contrato()
    s = sonda(mp4)
    v, a = s["v"], s["a"]
    reencode = v["codec_name"] != C["video"] or v.get("pix_fmt") not in (C["pixeles"], "yuvj420p")
    vid = ["-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", C["pixeles"]] if reencode else ["-c:v", "copy"]
    aud = ["-an"]
    if a:
        med = subprocess.run(NICE + ["ffmpeg", "-hide_banner", "-nostats", "-nostdin", "-i", str(mp4), "-vn", "-af",
                                     f"loudnorm=I={C['lufs']}:TP={C['pico_maximo_db'] - 0.5}:LRA=11:print_format=json", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
        j = json.loads(med[med.rindex("{"):med.rindex("}") + 1])
        filtro = (f"loudnorm=I={C['lufs']}:TP={C['pico_maximo_db'] - 0.5}:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}"
                  f":measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
        aud = ["-af", filtro, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
    r = subprocess.run(NICE + ["ffmpeg", "-v", "error", "-nostdin", "-y", "-i", str(mp4), *vid, *aud, "-movflags", "+faststart", str(salida)])
    if r.returncode == 0:
        print(f"✓ normalizado → {salida}  ({'imagen recodificada' if reencode else 'imagen intacta'}, audio a {C['lufs']} LUFS)")
    return r.returncode


def main() -> None:
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(args) < 2 or args[0] not in ("verificar", "normalizar"):
        sys.exit(__doc__)
    mp4 = Path(args[1]).expanduser().resolve()
    if not mp4.is_file():
        sys.exit(f"✗ no existe {mp4}")
    if args[0] == "verificar":
        sys.exit(verificar(mp4, "--horizontal" in sys.argv, "--sin-audio" in sys.argv))
    salida = Path(args[2]).expanduser().resolve() if len(args) > 2 else mp4.with_suffix(".entrega.mp4")
    sys.exit(normalizar(mp4, salida))


if __name__ == "__main__":
    main()
