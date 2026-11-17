#!/bin/zsh
# Instala o repara el entorno. Se puede correr varias veces y no pisa nada tuyo: tu config/kit.json se queda como está,
# y si la skill o el agente de Claude ya instalados tienen cambios que no hizo este instalador, los deja y avisa
# (./instalar.sh --reemplazar pone la versión nueva y guarda la anterior en respaldos/). No usa brew ni pide contraseña:
# si falta algo, dice qué es y cómo conseguirlo, y se detiene sin haber tocado nada.
set -e
KIT="$(cd "$(dirname "$0")" && pwd)"; cd "$KIT"
REEMPLAZAR=""; [[ "$1" == "--reemplazar" ]] && REEMPLAZAR=1

# ---- 1. Lo que debe estar instalado antes ----
faltan=()
command -v ffmpeg >/dev/null || faltan+=("ffmpeg  →  brew install ffmpeg")
{ command -v node >/dev/null && command -v npm >/dev/null } || faltan+=("Node.js (node y npm)  →  brew install node")
command -v uv >/dev/null || faltan+=("uv (instala Python 3.12)  →  brew install uv")
{ xcode-select -p >/dev/null 2>&1 && command -v swiftc >/dev/null } || faltan+=("herramientas de Xcode (swiftc)  →  xcode-select --install")
if (( ${#faltan} )); then
  print "Falta instalar esto antes de seguir:\n"
  for x in $faltan; do print "  ✗ $x"; done
  print "\nSi no tienes Homebrew (el comando brew), se instala desde https://brew.sh"
  print "Cuando esté todo, vuelve a correr ./instalar.sh. No se cambió nada."
  exit 1
fi
[[ "$(uname -sm)" == "Darwin arm64" ]] || print "⚠ Esto está hecho para Mac con chip Apple (M1 o más nuevo): en otra máquina Whisper y la detección de caras no funcionan."
[[ -d "/Applications/Google Chrome.app" || -n "$CHROME" ]] || print "⚠ No veo Google Chrome y hace falta para renderizar: brew install --cask google-chrome (o bájalo de google.com/chrome)."

# ---- 2. Python, Whisper y paquetes de Node ----
print "1/5 Entorno de Python…"
[[ -d .venv ]] || uv venv --python 3.12 --seed .venv
.venv/bin/pip install -q -r requirements.txt || { print "✗ No se pudieron instalar los paquetes de Python (requirements.txt). Revisa tu conexión y vuelve a correr ./instalar.sh"; exit 1; }
print "2/5 Modelo de Whisper (la primera vez baja 1.6 GB; puede tardar varios minutos)…"
.venv/bin/python -c "from huggingface_hub import snapshot_download as d; d('mlx-community/whisper-large-v3-turbo')" >/dev/null 2>&1 || print "  · no se pudo bajar ahora: se bajará solo la primera vez que transcribas"
print "3/5 Paquetes de Node…"
for d in motor editor-anuncios editor-testimoniales/editor; do
  (cd "$d" && npm install --silent --no-audit --no-fund --ignore-scripts >/dev/null) || { print "✗ npm install falló en $d. Revisa tu conexión y vuelve a correr ./instalar.sh"; exit 1; }
done

# ---- 3. Herramientas de Vision (recorte de persona, caras, HDR) y efectos de sonido ----
print "4/5 Herramientas de imagen y efectos de sonido…"
T=editor-testimoniales/editor; mkdir -p bin $T/bin $T/sfx
compila() {
  local err; err=$(swiftc -O "$1" -o "$2" 2>&1) || { print "✗ No se pudo compilar $1 (¿macOS 14 o más nuevo y xcode-select --install?):"; print -r -- "$err" | tail -5; exit 1; }
}
compila estilo-cine/segmentar.swift bin/segmentar
for s in caras sdr fotogramas; do compila $T/$s.swift $T/bin/$s; done
[[ -e $T/.venv ]] || ln -s ../../.venv $T/.venv
[[ -f estilo-cine/sfx/whoosh_rapido.mp3 ]] || .venv/bin/python audio/efectos_basicos.py >/dev/null
[[ -f $T/sfx/whoosh.wav ]] || ffmpeg -v error -y -i estilo-cine/sfx/whoosh_rapido.mp3 $T/sfx/whoosh.wav
[[ -f config/kit.json ]] || cp config/kit.ejemplo.json config/kit.json

# ---- 4. Skill y agente de Claude ----
# Skill: se copia a ~/.claude/skills (o a $SKILLS_DIR) con la ruta de este repo al final
print "5/5 Skill de Claude…"
# poner <archivo ya armado> <destino> <nombre>: copia sin pisar cambios de la persona. Recuerda la huella de lo que dejó;
# si lo instalado ya no coincide con esa huella, es de la persona: se queda como está, salvo que diga que sí (en una
# terminal pregunta; sin terminal, con ./instalar.sh --reemplazar) y entonces guarda antes una copia en respaldos/.
huella() { shasum "$1" | cut -d' ' -f1; }
poner() {
  local o="$1" d="$2" reg="$KIT/.instalado/$3.sha" r resp="$REEMPLAZAR"
  mkdir -p "${d:h}" "$KIT/.instalado"
  if [[ -f "$d" ]] && ! cmp -s "$o" "$d" && [[ ! -f "$reg" || "$(huella "$d")" != "$(<"$reg")" ]]; then
    # sin huella pero con la marca de este repo: lo puso una versión anterior de este instalador → se actualiza (con copia)
    if [[ ! -f "$reg" ]] && grep -qF "Repositorio del sistema de edición: \`$KIT\`" "$d"; then resp=1; fi
    if [[ -z "$resp" && -t 0 ]]; then read "resp?  $d ya existe y no lo dejó así este instalador. ¿Lo reemplazo? (guardo una copia antes) [s/N] " || resp=""; fi
    if [[ "$resp" != [sSyY1]* ]]; then
      print "  · $d ya existe y no lo dejó así este instalador: se queda como está. Para poner la versión nueva (guarda una copia antes): ./instalar.sh --reemplazar"
      return 0
    fi
    r="$KIT/respaldos/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$r"; cp "$d" "$r/${d:t}"
    print "  · reemplacé $d; la versión anterior quedó en ${r#$KIT/}/${d:t}"
  fi
  cp "$o" "$d"; huella "$d" > "$reg"
}
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
SK="${SKILLS_DIR:-$HOME/.claude/skills}"
for n in editor-iriza; do
  cp -R "skills/$n" "$TMP/$n"
  print "\n> Repositorio del sistema de edición: \`$KIT\` (todas las rutas relativas de esta skill son relativas a esa carpeta)." >> "$TMP/$n/SKILL.md"
  for f in "$TMP/$n"/**/*(.N); do poner "$f" "$SK/$n/${f#$TMP/$n/}" "skill-$n-${${f#$TMP/$n/}//\//-}"; done
done
if [[ -d agentes ]]; then   # agentes de Claude que acompañan al editor (el crítico que mira el video antes de entregarlo)
  AG="${AGENTS_DIR:-$HOME/.claude/agents}"
  for f in agentes/*.md(N); do
    a="$(<"$f")"; print -r -- "${a//__EDITOR__/$KIT}" > "$TMP/${f:t}"
    poner "$TMP/${f:t}" "$AG/${f:t}" "agente-${f:t:r}"
  done
fi

print "\nListo. Sigue con: ./verificar.sh"
print "Tus datos van en config/kit.json (nombre y @usuario que salen en los videos)."
print "Opcional, y todo funciona sin ello: llave de ElevenLabs para reels sin cara con voz de IA (./motor/clave.sh)."
