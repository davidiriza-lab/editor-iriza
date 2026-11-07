#!/bin/bash
# Video HDR (HLG/PQ: iPhone, DJI) → Rec.709 1080x1920 en _sdr/. Sin esto el video se ve lavado.
# Uso: proyectos/<proyecto>/convertir_sdr.sh [clip …]   (sin argumentos: todos los de crudos/; CRUDOS=<carpeta> para usar otra)
B=$(cd "$(dirname "$0")" && pwd); R=$(cd "$B/../.." && pwd); cd "$R"; B=${B#"$R"/}
D="${CRUDOS:-$B/crudos}"; S=editor-testimoniales/editor/bin/sdr; mkdir -p "$B/_sdr"
[ -x "$S" ] || { echo "Falta $S: corre ./instalar.sh"; exit 1; }
clips=("$@"); [ ${#clips[@]} -eq 0 ] && for f in "$D"/*; do n=$(basename "$f"); clips+=("${n%.*}"); done
for c in "${clips[@]}"; do
  [ -f "$B/_sdr/$c.mov" ] && continue
  f=$(ls "$D/$c".* 2>/dev/null | head -1); [ -z "$f" ] && { echo "FALTA $c en $D"; continue; }
  "$S" "$f" "$B/_sdr/_$c.mov" 1080 1920 && mv "$B/_sdr/_$c.mov" "$B/_sdr/$c.mov" && echo "ok $c" || echo "FALLO $c"
done
echo FIN
