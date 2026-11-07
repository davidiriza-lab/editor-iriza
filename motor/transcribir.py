"""Transcribe un video o audio (archivo local o link de Instagram/TikTok/YouTube).

Uso: python3 motor/transcribir.py <archivo|link> [--modelo small]
Deja el texto en transcripciones/<nombre>.txt, listo para convertirlo en guion.
"""
import subprocess, sys, tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src, modelo = sys.argv[1], (sys.argv[sys.argv.index("--modelo") + 1] if "--modelo" in sys.argv else "small")
    out = RAIZ / "transcripciones"; out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        if src.startswith("http"):
            subprocess.run(["yt-dlp", "-q", "--no-warnings", "-o", str(tmp / "fuente.%(ext)s"), src], check=True)
            fuente = next(tmp.glob("fuente.*"))
            nombre = src.rstrip("/").split("/")[-1].split("?")[0] or "link"
        else:
            fuente = Path(src).resolve(); nombre = fuente.stem
        wav = tmp / f"{nombre}.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(fuente), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
        subprocess.run(["whisper", str(wav), "--model", modelo, "--language", "es", "--output_format", "txt",
                        "--output_dir", str(out), "--verbose", "False"], check=True)
    f = out / f"{nombre}.txt"
    print(f.read_text()); print(f"→ {f}")


if __name__ == "__main__":
    main()
