#!/bin/bash
# Transcribe cada crudo (audio del original) en _tomas/<clip>/: voz/palabras.json + tramos, para elegir las tomas de tomas.json.
# Uso: proyectos/<proyecto>/transcribir_todos.sh [clip …]   (sin argumentos: todos los de crudos/; CRUDOS=<carpeta> para usar otra)
B=$(cd "$(dirname "$0")" && pwd); R=$(cd "$B/../.." && pwd); cd "$R"; B=${B#"$R"/}
D="${CRUDOS:-$B/crudos}"; PR=$(cat "$B/nombres.txt" 2>/dev/null)
clips=("$@"); [ ${#clips[@]} -eq 0 ] && for f in "$D"/*; do n=$(basename "$f"); clips+=("${n%.*}"); done
for c in "${clips[@]}"; do
  P=$B/_tomas/$c; mkdir -p "$P"
  [ -f "$P/voz/palabras.json" ] && continue
  f=$(ls "$D/$c".* 2>/dev/null | head -1); [ -z "$f" ] && { echo "FALTA $c en $D"; continue; }
  .venv/bin/python estilo-cine/transcribir.py "$P" "$f" --tramos ${PR:+--prompt "$PR"} > "$P/transcripcion.txt" 2>&1 && echo "ok $c" || echo "FALLO $c"
done
echo FIN
