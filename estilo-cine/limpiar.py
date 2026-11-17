"""Limpiador: borra lo intermedio de un proyecto ya terminado y deja lo que importa.

  python3 estilo-cine/limpiar.py proyectos/<nombre> [--simular] [--forzar]
  python3 estilo-cine/limpiar.py --todo [--simular]        # todos los proyectos de proyectos/

Se queda SIEMPRE: los videos finales (salida/), el material de origen (crudos, _sdr, corte, audio), los planes y
configuraciones (cine.json, plan.json, metodo.json…), la voz y las revisiones.
Se borra: lo que se regenera solo con `preparar.py`: cuadros extraídos y máscaras (suelen ser varios GB por video).

Candados (se saltan con --forzar):
  · una pieza solo se limpia si YA tiene video final en salida/ (si no, sigue en proceso);
  · no se toca nada modificado en las últimas 48 horas (puede haber otra sesión trabajando ahí).
Con --simular no borra nada: solo dice cuánto se liberaría.
"""
import shutil
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# carpetas regenerables de una pieza (salen de corte/ con preparar.py y bin/segmentar)
BORRAR = ["cuadros", "cuadros_pro", "cuadros_orig", "cuadros_4k", "cuadros_pro_4k", "mascaras", "mascaras_4k", "__pycache__"]
RECIENTE = 48 * 3600


def peso(p: Path) -> int:
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file() and not f.is_symlink())


def reciente(p: Path) -> bool:
    try:
        return time.time() - p.stat().st_mtime < RECIENTE
    except OSError:
        return False


def tam(n: int) -> str:
    return f"{n / 1e9:.2f} GB" if n >= 1e8 else f"{n / 1e6:.1f} MB"


def limpiar(carpeta: Path, simular: bool, forzar: bool) -> int:
    """Cada subcarpeta con cine.json es una pieza. Limpia solo las que ya tienen video final."""
    carpeta = carpeta.expanduser().resolve()
    if not carpeta.is_dir():
        sys.exit(f"✗ no existe {carpeta}")
    libre = 0
    for cine in sorted(carpeta.rglob("cine.json")):
        pieza = cine.parent
        if "node_modules" in pieza.parts:
            continue
        finales = list((pieza / "salida").glob("*.mp4")) if (pieza / "salida").is_dir() else []
        if not forzar and not finales:
            print(f"  · salto {pieza.name} (sin video final: sigue en proceso)")
            continue
        if not forzar and (reciente(cine) or any(reciente(f) for f in finales)):
            print(f"  · salto {pieza.name} (modificado hace menos de 48 h)")
            continue
        for nombre in BORRAR:
            d = pieza / nombre
            if d.is_dir() and not d.is_symlink():
                libre += peso(d)
                if not simular:
                    shutil.rmtree(d)
    return libre


def main() -> None:
    simular, forzar = "--simular" in sys.argv, "--forzar" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--todo" in sys.argv:
        objetivos = [RAIZ / "proyectos"]
    elif args:
        objetivos = [Path(a) for a in args]
    else:
        sys.exit(__doc__)
    total = 0
    for o in objetivos:
        n = limpiar(o, simular, forzar)
        print(f"{'(simulación) ' if simular else ''}{o}: {tam(n)} {'se liberarían' if simular else 'liberados'}")
        total += n
    print(f"\nTotal: {tam(total)} {'por liberar' if simular else 'liberados'}. Videos finales, crudos, cortes y planes intactos.")


if __name__ == "__main__":
    main()
