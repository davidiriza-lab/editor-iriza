#!/bin/zsh
# Revisa que todo esté instalado y renderiza el video de prueba (proyectos/demo, 17 s, sin cámara).
# Uso: ./verificar.sh            (agrega --sin-render para solo revisar)
KIT="$(cd "$(dirname "$0")" && pwd)"; cd "$KIT"
f=0
chk() { if eval "$2" >/dev/null 2>&1; then print -P "%F{green}✓%f $1"; else print -P "%F{red}✗%f $1  →  $3"; f=1; fi; }
chk "ffmpeg"                       "command -v ffmpeg"                                  "brew install ffmpeg"
chk "codificador HEVC por hardware" "ffmpeg -hide_banner -encoders | grep -q hevc_videotoolbox" "(solo afecta al perfil 4K)"
chk "Node"                         "command -v node"                                    "brew install node"
chk "Google Chrome"                "test -d '/Applications/Google Chrome.app'"          "brew install --cask google-chrome"
chk "Python .venv"                 "test -x .venv/bin/python"                           "./instalar.sh"
chk "Whisper (mlx)"                ".venv/bin/python -c 'import mlx_whisper'"           "./instalar.sh"
chk "OpenCV / numpy / scipy"       ".venv/bin/python -c 'import cv2, numpy, scipy'"     "./instalar.sh"
chk "puppeteer (motor)"            "test -d motor/node_modules/puppeteer-core"          "cd motor && npm install"
chk "bin/segmentar (Vision)"       "test -x bin/segmentar"                              "swiftc -O estilo-cine/segmentar.swift -o bin/segmentar"
chk "efectos de sonido"            "test -f estilo-cine/sfx/whoosh_rapido.mp3"          "python3 audio/efectos_basicos.py"
chk "skills instaladas"            "test -f ${SKILLS_DIR:-$HOME/.claude/skills}/editor-iriza/SKILL.md"  "./instalar.sh"
chk "config/kit.json"              "test -f config/kit.json"                            "./instalar.sh (o copia config/kit.ejemplo.json)"
print -P "\n%F{cyan}Opcionales (cuentas de cada quien):%f"
chk "Higgsfield CLI (imágenes IA)" "command -v higgsfield"                              "npm i -g @higgsfield/cli"
chk "Llave ElevenLabs (voz IA)"    "security find-generic-password -s videos-voz-ia.elevenlabs" "./motor/clave.sh"
[[ "$1" == "--sin-render" ]] && exit $f
print -P "\n%F{cyan}Render de prueba (proyectos/demo)…%f"
node estilo-cine/render.mjs proyectos/demo && print -P "%F{green}✓ Todo funciona:%f proyectos/demo/salida/cine_codigo.mp4" && open -R proyectos/demo/salida/cine_codigo.mp4
