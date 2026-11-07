#!/bin/bash
# Uso: proyectos/<proyecto>/preparar_cola.sh k1 k2 … → corte + voz pareja + transcripción + cuadros/máscaras + caras + revisión de uniones
B=$(cd "$(dirname "$0")" && pwd); R=$(cd "$B/../.." && pwd); cd "$R"; B=${B#"$R"/}
[ -d /opt/homebrew/opt/ffmpeg-full/bin ] && export PATH=/opt/homebrew/opt/ffmpeg-full/bin:$PATH
PR=$(cat "$B/nombres.txt" 2>/dev/null)   # nombres propios que Whisper escribe mal
for k in "$@"; do p=$B/$k; echo "=== $k $(date +%H:%M:%S)"
  .venv/bin/python $B/cortar.py $k 2>&1 | tail -1
  .venv/bin/python estilo-cine/transcribir.py $p ${PR:+--prompt "$PR"} > $p/transcripcion.txt 2>&1 || echo "FALLO transcribir $k"
  .venv/bin/python estilo-cine/preparar.py $p --sin-piel > $p/preparar.log 2>&1 || echo "FALLO preparar $k"
  editor-testimoniales/editor/bin/caras $p/corte/cam.mov $p/corte/caras.json > /dev/null 2>&1 || echo "FALLO caras $k"
  .venv/bin/python $B/revisar_uniones.py $k > $p/uniones.txt 2>&1 || echo "FALLO uniones $k"
  echo "ok $k $(date +%H:%M:%S)"
done; echo "=== COLA LISTA"
