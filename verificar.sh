#!/bin/zsh
# Revisa que todo esté instalado y renderiza el video de prueba (proyectos/demo, 17 s, sin cámara).
# Uso: ./verificar.sh            (agrega --sin-render para solo revisar)
# ✓ listo · ✗ falta y hace falta (a la derecha, cómo arreglarlo) · ○ opcional: todo funciona sin eso
KIT="$(cd "$(dirname "$0")" && pwd)"; cd "$KIT"
f=0
chk() { if eval "$2" >/dev/null 2>&1; then print -P "%F{green}✓%f $1"; else print -P "%F{red}✗%f $1  →  $3"; f=1; fi; }
opc() { if eval "$2" >/dev/null 2>&1; then print -P "%F{green}✓%f $1"; else print -P "%F{yellow}○%f $1  →  $3"; fi; }
T=editor-testimoniales/editor
chk "Mac con chip Apple"           '[[ "$(uname -sm)" == "Darwin arm64" ]]'             "Whisper (MLX) y la detección de caras solo corren en Mac con chip Apple"
chk "ffmpeg"                       "command -v ffmpeg"                                  "brew install ffmpeg"
chk "Node"                         "command -v node"                                    "brew install node"
chk "Google Chrome"                "test -d '/Applications/Google Chrome.app' -o -n \"\$CHROME\"" "brew install --cask google-chrome"
chk "Python .venv"                 "test -x .venv/bin/python"                           "./instalar.sh"
chk "Whisper (mlx)"                ".venv/bin/python -c 'import mlx_whisper'"           "./instalar.sh"
chk "OpenCV / numpy / scipy"       ".venv/bin/python -c 'import cv2, numpy, scipy'"     "./instalar.sh"
chk "puppeteer (motor)"            "test -d motor/node_modules/puppeteer-core"          "./instalar.sh"
chk "bin/segmentar (Vision)"       "test -x bin/segmentar"                              "./instalar.sh"
chk "caras, sdr y fotogramas"      "test -x $T/bin/caras -a -x $T/bin/sdr -a -x $T/bin/fotogramas" "./instalar.sh"
chk "efectos de sonido"            "test -f estilo-cine/sfx/whoosh_rapido.mp3"          "./instalar.sh"
chk "skills instaladas"            "test -f ${SKILLS_DIR:-$HOME/.claude/skills}/editor-iriza/SKILL.md"  "./instalar.sh"
chk "config/kit.json"              "test -f config/kit.json"                            "./instalar.sh (o copia config/kit.ejemplo.json)"
print -P "\n%F{cyan}Opcionales (todo lo demás funciona sin esto):%f"
opc "codificador HEVC por hardware (solo para 4K)" "ffmpeg -hide_banner -encoders | grep -q hevc_videotoolbox" "sin él no hay perfil 4K; Redes 1080 no lo usa"
[[ -d agentes ]] && opc "agente critico-video (mira el video antes de entregarlo)" "test -f ${AGENTS_DIR:-$HOME/.claude/agents}/critico-video.md" "./instalar.sh"
opc "tu nombre en config/kit.json" "test -f config/kit.json && ! grep -q 'Tu nombre' config/kit.json" "pon tu nombre y tu @usuario: salen en los videos"
opc "referencias de los 61 formatos" "test -f plantillas/formatos/editor-01/hoja.jpg"   "https://github.com/davidiriza-lab/editor-iriza-referencias"
opc "Llave ElevenLabs (reels sin cara con voz de IA)" "security find-generic-password -s videos-voz-ia.elevenlabs || test -s $HOME/.config/elevenlabs/api_key" "./motor/clave.sh"
opc "imagen-gpt (fondos con tu suscripción de ChatGPT)" "test -x $HOME/.local/bin/imagen-gpt" "https://github.com/davidiriza-lab/claude-con-gemini-y-gpt"
opc "Higgsfield CLI (imágenes con IA)" "command -v higgsfield"                          "npm i -g @higgsfield/cli"
if (( f )); then print -P "\n%F{red}Falta lo marcado con ✗.%f Arréglalo (casi siempre: ./instalar.sh) y vuelve a correr ./verificar.sh"; exit 1; fi
[[ "$1" == "--sin-render" ]] && { print -P "\n%F{green}✓ Todo lo necesario está instalado.%f"; exit 0; }
print -P "\n%F{cyan}Render de prueba (proyectos/demo, 17 s de video; puede tardar un par de minutos)…%f"
if node estilo-cine/render.mjs proyectos/demo; then
  print -P "%F{green}✓ Todo funciona:%f proyectos/demo/salida/cine_codigo.mp4"; open -R proyectos/demo/salida/cine_codigo.mp4
else
  print -P "%F{red}✗ El render de prueba falló.%f Copia el error de arriba y pégaselo a Claude: casi siempre es Chrome o un paquete que faltó."; exit 1
fi
