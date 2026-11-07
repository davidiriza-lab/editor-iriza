# Guía para Claude · Editor 43 · Duelo de pantallas

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Duelo de Pantallas

**La idea:** Dos ventanas apiladas (ChatGPT vs Gemini) con la misma petición escribiéndose y el resultado de cada una.

**Lo que se ve en la referencia:** Fondo azul eléctrico con degradado. Dos ventanas apiladas (arriba ChatGPT, abajo Gemini / "GPT 6 Astra") con la misma petición escribiéndose y el resultado de cada una (paisaje vs ciudad neón). Etiqueta arriba "After Effects", CTA fijo abajo serif "Cmt the word 'Astra' for the link". 7.4 s.

**Para qué sirve:** Comparativos de herramientas.

## Cómo reconocerlo
- **Texto:** Etiqueta arriba; CTA fijo abajo en serif (“Comenta la palabra…”).
- **Animación y ritmo:** Tecleo simultáneo, resultado que crece desde la ventana.
- **Audio:** Música.
- **Medido en la referencia:** 7.4 s · 0 cortes (casi un solo plano, 0.0 cortes/s) · vertical 9:16
- **Paleta medida:** `#0c102f` 38 % · `#09090c` 21 % · `#2114f0` 20 % · `#a7c6e2` 7 % · `#2c3c75` 7 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- La misma petición en las dos herramientas

### 2. Pasos
1. Dos interfaces en código apiladas (escenas `interfaz`/`chat` duplicadas)
2. La petición se escribe en las dos a la vez y luego aparece cada resultado

**Motor sugerido:** Interfaces en código (Cine Pro 3D) duplicadas.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Resultados inventados: usa los reales
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
