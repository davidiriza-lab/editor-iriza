# Guía para Claude · Editor 17 · pantalla · Persona + tarjetas

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

> **Origen:** es el video que se ve dentro de la laptop/monitor de Editor 17 · Monitor de edición ([`../editor-17/GUIA.md`](../editor-17/GUIA.md)), sacado derecho con `pantalla_interior.py`. Se puede publicar solo o volver a meter en una pantalla filmada.

## Qué es
**Familia:** Persona con Tarjetas de Interfaz

**La idea:** Persona sentada a cámara en estudio claro; sobre ella aparecen palabras gigantes en serif y tarjetas de interfaz (tarjeta de precio con botón verde, lista de pasos con borde rojo neón) que ilustran lo que dice.

**Lo que se ve en la referencia:** Hombre de traje sentado en estudio blanco; palabras gigantes serif detrás ("LEGAL"), frases en serif bold blanca ("is completely", "canceling"), tarjeta de precio "Startup Plan $399" con botón verde que recibe un clic y lista "You need: call a number / wait on hold / talk to a retention specialist" con borde rojo neón.

**Para qué sirve:** Anuncio de servicio con persona a cámara que "explica con interfaces" (precio, pasos, comparación).

## Cómo reconocerlo
- **Texto:** Serif bold blanca grande con efecto de entrada; palabras gigantes semitransparentes detrás; tarjetas oscuras con texto blanco y acento verde o rojo.
- **Animación y ritmo:** 2 cortes en 14 s: la persona se tapa por completo con una tarjeta que hace zoom, cursor que da clic, lista que se va llenando con marca roja.
- **Audio:** Voz real de la persona + música de fondo.
- **Medido en la referencia:** 13.8 s · 2 cortes (casi un solo plano, 0.14 cortes/s) · vertical 9:16
- **Paleta medida:** `#c8c3ca` 26 % · `#dadce2` 20 % · `#b6a6ac` 18 % · `#232427` 18 % · `#4f4d51` 9 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Video de la persona a cámara en fondo claro
- Las tarjetas que ilustran (precio, lista de pasos, comparación)

### 2. Pasos
1. Corte y subtítulos con el editor de testimoniales: `editor-testimoniales/editor/editar.py <p> plan → armar → terminar`
2. Tarjetas de interfaz hechas en código (escenas `interfaz`/`tarjetas` de estilo-cine renderizadas con fondo transparente) puestas encima del corte
3. Palabras gigantes serif semitransparentes detrás de la persona: usa la máscara de persona (`estilo-cine/preparar.py`) y grupos `"detras": true`
4. Una tarjeta puede tapar a la persona por completo con zoom (eso hace de corte)
5. Cursor que da clic en el botón verde
6. Revisión final: `revisar_final.py` (texto nunca sobre la cara salvo la tarjeta que la tapa a propósito)

**Motor sugerido:** Editor de testimoniales/anuncios para el corte y subtítulos + tarjetas de interfaz en código (escena interfaz/tarjetas de estilo-cine) encima.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Tarjetas que tapen la boca mientras habla
- Más de 2 cortes reales
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
