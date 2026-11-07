---
name: editor-iriza
description: "Editor de video a cámara con Claude Code: reels, anuncios, testimoniales, entrevistas, tutoriales y reacciones verticales (plantillas Cine Pro, Cine Pro 3D, Editor 1-50, Pizarra Pro, anuncio por frases). Úsala cuando la persona pase un video o una carpeta de clips para editar, pida las mejores partes de una entrevista, un anuncio o un reel, o nombre una de las plantillas. No aplica a videos animados sin cara ni a clases largas."
---

# Editor Iriza

1. Abre y sigue `CLAUDE.md` de la carpeta del repositorio (ruta al final de este archivo): flujo, reglas y qué herramienta usar.
2. Si falta algo instalado (`.venv`, `bin/segmentar`, `config/kit.json`), corre `./instalar.sh` y después `./verificar.sh`.
3. Formatos: índice `plantillas/formatos/GUIA-FORMATOS.md` y una `GUIA.md` por formato. Cine Pro 3D: `plantillas/cine-pro-3d/ESTILO.md`. Anuncios grabados frase por frase: `plantillas/anuncio-por-frases/LEEME.md`.
4. Salida por defecto **Redes (1080)**; **4K** solo si la persona lo pide (`prep4k.py` + `render.mjs --perfil 4k`).
5. Primero el plan con la lista de posibles errores; no se edita ni se publica nada sin aprobación.
6. Testimoniales, entrevistas y anuncios a cámara con guion: seguir `editor-testimoniales/README.md`.
