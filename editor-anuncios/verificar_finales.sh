#!/bin/zsh
# Verifica renders del editor de anuncios: duración, loudness, fluidez (quieto < 5 %) y que el audio diga lo mismo que el original.
# Uso: editor-anuncios/verificar_finales.sh <carpeta_proyecto> [<carpeta_proyecto> …]   (cada una con final.mp4 y words.json)
AQUI="$(cd "$(dirname "$0")" && pwd)"; PY="$AQUI/../.venv/bin/python"
MODELO=~/.cache/whisper-cpp/ggml-large-v3-turbo.bin
for p in "$@"; do
  f="$p/final.mp4"; n="$(basename "$p")"; [ -f "$f" ] || { echo "$n: SIN RENDER"; continue; }
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  lufs=$(ffmpeg -i "$f" -af ebur128=framelog=quiet -f null - 2>&1 | grep -E "I:\s" | tail -1 | awk '{print $2}')
  flu=$("$PY" "$AQUI/fluidez.py" "$f" | head -1)
  w=$(mktemp -t vf).wav; ffmpeg -loglevel error -y -i "$f" -vn -ac 1 -ar 16000 "$w"
  txt=$(whisper-cli -m "$MODELO" -l es -mc 0 -np -nt -f "$w" 2>/dev/null | tr '\n' ' '); rm -f "$w"
  orig=$(python3 -I -c "import json,sys; print(' '.join(w['w'] for w in json.load(open(sys.argv[1]))))" "$p/words.json")
  faltan=$(python3 -I - "$txt" "$orig" <<'PY'
import sys, re, unicodedata
n=lambda s: [re.sub(r'[^a-z0-9ñ]','',unicodedata.normalize('NFD',w.lower()).encode('ascii','ignore').decode()) for w in s.split()]
a=[w for w in n(sys.argv[2]) if w]; b=set(w for w in n(sys.argv[1]) if w)
print(', '.join(w for w in a if w not in b and len(w)>3) or 'ninguna')
PY
)
  printf "%s: %.1fs · %s LUFS · %s · palabras del original que no se oyen: %s\n" "$n" "$dur" "$lufs" "$flu" "$faltan"
done
