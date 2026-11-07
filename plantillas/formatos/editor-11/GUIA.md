# Guía para Claude · Editor 11 · Manuscrito amarillo

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Acento Amarillo (hermanos: Editor 33 · CapCut efectos de película)

**La idea:** Tú hablando + capturas a pantalla completa; la palabra clave en amarillo (manuscrita o serif itálica).

**Lo que se ve en la referencia:** Persona (hombre) en cuarto cálido. Subtítulos con letra tipo manuscrito: blanco + palabra clave amarilla ("conectar", "Chat GPT", "de video"). Chip de logo arriba (ChatGPT). Capturas de páginas/apps a pantalla completa en fondo negro, B-roll de manos tecleando, frases manuscritas solas sobre negro ("algo que no existe"), luego pantalla dividida UI arriba / él abajo. 17 s.

**Para qué sirve:** Tutoriales de herramientas (CapCut, ChatGPT). Metodología.

## Cómo reconocerlo
- **Texto:** Subtítulo blanco chico + palabra amarilla (manuscrita en 11, serif itálica en 33); conteo 1/2/3 gigante.
- **Animación y ritmo:** Cortes rápidos a capturas y ejemplos; en 33 ejemplos con grano de película, serigrafía de puntos y sepia.
- **Audio:** Voz + música.
- **Medido en la referencia:** 17.3 s · 6 cortes (tranquilo, 0.35 cortes/s) · vertical 9:16
- **Paleta medida:** `#030202` 52 % · `#211d18` 19 % · `#463b2d` 10 % · `#a39a8d` 8 % · `#6b6862` 6 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Video de la persona + capturas

### 2. Pasos
1. Cine Pro con capturas a pantalla completa
2. Palabra clave en amarillo con fuente manuscrita o serif itálica

**Motor sugerido:** Cine Pro cambiando la fuente del acento.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Más de una palabra resaltada por frase
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
