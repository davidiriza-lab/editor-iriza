#!/bin/zsh
# Guarda (o reemplaza) la API key de ElevenLabs en el Llavero de macOS.
# La clave nunca se escribe en archivos del proyecto.
# Uso: ./motor/clave.sh          -> pide la clave sin mostrarla
#      ./motor/clave.sh --ver    -> confirma que existe (muestra solo el inicio)
#      ./motor/clave.sh --borrar -> la elimina del Llavero
S="videos-voz-ia.elevenlabs"
case "$1" in
  --ver)    k=$(security find-generic-password -s "$S" -w 2>/dev/null) && echo "Guardada: ${k:0:6}…" || echo "No hay clave guardada." ;;
  --borrar) security delete-generic-password -s "$S" >/dev/null 2>&1 && echo "Clave eliminada." || echo "No había clave." ;;
  *)        read -rs "k?Pega tu API key de ElevenLabs: "; echo
            [[ -z "$k" ]] && { echo "Vacía, no se guardó."; exit 1; }
            security add-generic-password -a "$USER" -s "$S" -l "ElevenLabs API (videos-voz-ia)" -w "$k" -U && echo "Guardada en el Llavero." ;;
esac
