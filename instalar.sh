#!/bin/zsh
# Instala o repara el entorno. Se puede correr varias veces. No usa brew: requiere ffmpeg, node, uv, swiftc y Chrome ya instalados.
set -e
KIT="$(cd "$(dirname "$0")" && pwd)"; cd "$KIT"
for c in ffmpeg node npm uv swiftc; do command -v $c >/dev/null || { print "Falta $c"; exit 1; }; done
[[ -d .venv ]] || uv venv --python 3.12 --seed .venv
.venv/bin/pip install -q -r requirements.txt
.venv/bin/python -c "from huggingface_hub import snapshot_download as d; d('mlx-community/whisper-large-v3-turbo')" >/dev/null 2>&1 || print "Whisper se bajará la primera vez que transcribas"
for d in motor editor-anuncios editor-testimoniales/editor; do (cd "$d" && npm install --silent --no-audit --no-fund --ignore-scripts >/dev/null); done
T=editor-testimoniales/editor; mkdir -p bin $T/bin $T/sfx
swiftc -O estilo-cine/segmentar.swift -o bin/segmentar 2>/dev/null
for s in caras sdr fotogramas; do swiftc -O $T/$s.swift -o $T/bin/$s 2>/dev/null; done
[[ -e $T/.venv ]] || ln -s ../../.venv $T/.venv
[[ -f estilo-cine/sfx/whoosh_rapido.mp3 ]] || .venv/bin/python audio/efectos_basicos.py >/dev/null
[[ -f $T/sfx/whoosh.wav ]] || ffmpeg -v error -y -i estilo-cine/sfx/whoosh_rapido.mp3 $T/sfx/whoosh.wav
[[ -f config/kit.json ]] || cp config/kit.ejemplo.json config/kit.json
# Skill: se copia a ~/.claude/skills (o a $SKILLS_DIR) con la ruta de este repo al final
SK="${SKILLS_DIR:-$HOME/.claude/skills}"; mkdir -p "$SK"
for n in editor-iriza; do
  rm -rf "${SK:?}/${n:?}"; cp -R "skills/$n" "$SK/$n"
  print "\n> Repositorio del sistema de edición: \`$KIT\` (todas las rutas relativas de esta skill son relativas a esa carpeta)." >> "$SK/$n/SKILL.md"
done
print "Listo. Sigue con: ./verificar.sh"
