#!/bin/bash
# Uso: proyectos/<proyecto>/recortar_cola.sh k1 k2 … → corte nuevo (tras cambiar tomas.json) conservando las palabras del corte anterior
B=$(cd "$(dirname "$0")" && pwd); R=$(cd "$B/../.." && pwd); cd "$R"; B=${B#"$R"/}
[ -d /opt/homebrew/opt/ffmpeg-full/bin ] && export PATH=/opt/homebrew/opt/ffmpeg-full/bin:$PATH
for k in "$@"; do p=$B/$k; echo "=== $k $(date +%H:%M:%S)"
  [ -f $p/corte/mapa_v1.json ] || cp $p/corte/mapa.json $p/corte/mapa_v1.json
  [ -f $p/voz/palabras_v1.json ] || cp $p/voz/palabras.json $p/voz/palabras_v1.json
  .venv/bin/python $B/cortar.py $k 2>&1 | tail -1
  python3 $B/remapear.py $k
  .venv/bin/python estilo-cine/preparar.py $p --sin-piel > $p/preparar.log 2>&1 || echo "FALLO preparar $k"
  editor-testimoniales/editor/bin/caras $p/corte/cam.mov $p/corte/caras.json > /dev/null 2>&1 || echo "FALLO caras $k"
  .venv/bin/python $B/revisar_uniones.py $k > $p/uniones.txt 2>&1 || echo "FALLO uniones $k"
  echo "ok $k $(date +%H:%M:%S)"
done; echo "=== COLA LISTA"
