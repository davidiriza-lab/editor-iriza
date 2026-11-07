#!/bin/bash
# Stills sueltos antes del render completo. Uso: proyectos/<proyecto>/stills.sh <clave> 1.5,4,9.2  → <clave>/salida/hoja_stills.jpg
B=$(cd "$(dirname "$0")" && pwd); R=$(cd "$B/../.." && pwd); cd "$R"; B=${B#"$R"/}
[ -d /opt/homebrew/opt/ffmpeg-full/bin ] && export PATH=/opt/homebrew/opt/ffmpeg-full/bin:$PATH
k=$1; p=$B/$k; python3 $B/armar.py $k | cut -c1-90; rm -f $p/salida/codigo_*.png
node estilo-cine/render.mjs $p --stills "$2" 2>&1 | grep -E "⚠|rror" | grep -v "404" | head -8
ffmpeg -v error -y -pattern_type glob -i "$p/salida/codigo_*.png" -vf "scale=270:-2,tile=7x2:padding=3" -frames:v 1 -q:v 3 $p/salida/hoja_stills.jpg
