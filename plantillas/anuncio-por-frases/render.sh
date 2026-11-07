#!/bin/bash
# Render + revisión final. Uso: proyectos/<proyecto>/render.sh k1 k2 …
# render.mjs a veces no termina tras escribir el mp4: se cierra en cuanto el log confirma.
B=$(cd "$(dirname "$0")" && pwd); R=$(cd "$B/../.." && pwd); cd "$R"; B=${B#"$R"/}
[ -d /opt/homebrew/opt/ffmpeg-full/bin ] && export PATH=/opt/homebrew/opt/ffmpeg-full/bin:$PATH
for k in "$@"; do p=$B/$k; python3 $B/armar.py $k | cut -c1-90; rm -f $p/render.log
  node estilo-cine/render.mjs $p > $p/render.log 2>&1 & pid=$!
  while kill -0 $pid 2>/dev/null; do if grep -q "de render)" $p/render.log 2>/dev/null; then /bin/sleep 3; kill $pid 2>/dev/null; break; fi; /bin/sleep 2; done
  grep -q "de render)" $p/render.log && echo "render ok $k" || { echo "FALLO $k"; tail -3 $p/render.log | cut -c1-200; continue; }
  editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py $p "$p/salida/$k.mp4" > $p/revision.log 2>&1; grep -E "LUFS|⚠|sin errores" $p/revision.log | cut -c1-110
done
