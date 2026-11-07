# Guía para Claude · Editor 27 · Pasos numerados

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Pasos Numerados

**La idea:** “Paso 1/2/3” gigante rojo-naranja arriba; mockups de tablet/celular y tarjetas de fotos que se abren en abanico.

**Lo que se ve en la referencia:** "Paso 1/2/3" gigante rojo-naranja arriba. Alterna fondo blanco (degradado rosa abajo, cuadritos de color flotando) y fondo negro. Mockups de tablet/celular con la herramienta, tarjetas de fotos que se abren en abanico (clones de la cara), palabra acento en serif itálica ("gratis") o manuscrita ("lo que querés"), subtítulo chico al centro. Cierre con un prompt en pantalla. 23 s.

**Para qué sirve:** Tutoriales de 3 pasos. Metodología.

## Cómo reconocerlo
- **Texto:** Paso gigante + subtítulo chico al centro; palabra acento en serif itálica o manuscrita.
- **Animación y ritmo:** Alterna fondo blanco (degradado rosa) y negro; cuadritos de color flotando.
- **Audio:** Voz en off.
- **Medido en la referencia:** 23.3 s · 11 cortes (tranquilo, 0.47 cortes/s) · vertical 9:16
- **Paleta medida:** `#020202` 40 % · `#f9f9f8` 36 % · `#ebd7cf` 9 % · `#2f2b2a` 9 % · `#7b7b76` 5 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Guion en pasos

### 2. Pasos
1. "Paso 1/2/3" gigante rojo-naranja arriba
2. Mockups de tablet/celular (`telefonos`) y tarjetas de fotos que se abren en abanico

**Motor sugerido:** estilo-cine + mockups en código.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Más de 5 pasos
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
