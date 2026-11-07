# Guía para Claude · Editor 37 · Selfie + pantalla

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Selfie + Pantalla (UGC)

**La idea:** Look casero: tú en selfie muy cerca + el celular apuntando al monitor mientras señalas con el dedo.

**Lo que se ve en la referencia:** Él hablando en selfie muy cerca + cámara en mano apuntando al monitor (dedo señalando la pantalla: apps, landing "Flighty told you first", terminal con código). Título fijo arriba en caja roja con texto blanco y emojis ("Motion Graphics con Claude 🤖 en MINUTOS 😍"). Subtítulos amarillos con contorno, frase completa al centro-abajo. Look casero, sin animaciones. 31 s.

**Para qué sirve:** Videos rápidos y auténticos (“mira lo que me hizo Claude”).

## Cómo reconocerlo
- **Texto:** Título fijo arriba en caja roja con emojis; subtítulos amarillos con contorno, frase completa.
- **Animación y ritmo:** Cámara en mano, sin animaciones.
- **Audio:** Tu voz directa.
- **Medido en la referencia:** 31.3 s · 8 cortes (tranquilo, 0.26 cortes/s) · vertical 9:16
- **Paleta medida:** `#1f1d22` 34 % · `#dad1c7` 25 % · `#866c63` 14 % · `#4d4043` 13 % · `#b99d89` 12 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Selfie hablando + toma del celular apuntando al monitor

### 2. Pasos
1. Solo corte + subtítulos (editor de anuncios o de testimoniales)
2. Look casero: sin gráficos

**Motor sugerido:** Solo corte + subtítulos (Editor Anuncios o Metodología).

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Pulirlo de más
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
