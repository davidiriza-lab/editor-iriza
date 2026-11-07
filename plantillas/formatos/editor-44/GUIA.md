# Guía para Claude · Editor 44 · Podcast verde

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Podcast Verde

**La idea:** Clip de podcast en blanco y negro que se interrumpe con pantallas verde bosque y una palabra gigante.

**Lo que se ve en la referencia:** Toma de podcast en blanco y negro (close-ups de la cara, micrófono). Corte a fondo verde bosque (con rayas horizontales finas) o blanco con una palabra gigante sans bold blanca/verde ("Wins", "B*TCH", "chasing") + línea chica serif itálica; tarjeta del reel B/N dentro del verde. Ritmo de una palabra por golpe. 6 s.

**Para qué sirve:** Recortes de podcast o entrevistas.

## Cómo reconocerlo
- **Texto:** Sans bold gigante blanca/verde + línea chica serif itálica.
- **Animación y ritmo:** Una palabra por golpe; la tarjeta del reel B/N dentro del verde.
- **Audio:** Voz del podcast.
- **Medido en la referencia:** 6.2 s · 9 cortes (muy rápido, 1.45 cortes/s) · vertical 9:16
- **Paleta medida:** `#154833` 42 % · `#121212` 33 % · `#f9faf9` 13 % · `#797b7a` 5 % · `#4d5b55` 4 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Clip de podcast

### 2. Pasos
1. Clip en blanco y negro (ffmpeg `hue=s=0`)
2. Interrupciones con pantallas verde bosque y una palabra gigante (estilo-cine)

**Motor sugerido:** Corte de podcast + estilo-cine paleta verde.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Color en el clip
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
