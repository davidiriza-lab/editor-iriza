# Guía para Claude · Editor 46 · Bola de luz

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Bola de Luz

**La idea:** Una esfera roja que rebota y funciona como foco: proyecta un cono de luz que revela el texto. Termina con texturas 3D y partículas.

**Lo que se ve en la referencia:** Marca (Claude Opus): fondo negro/marfil alternando, una esfera roja brillante que rebota y funciona como foco de luz (proyecta cono de luz que revela el texto), palabras gigantes sans black ("we don't just direct.", "MADE BY CODE.", "LIGHT IS JUST MATH." con palabra roja/azul), luego "claude" condensado sobre texturas 3D (gelatina, espiral, cubos, celular de vidrio) y "OPUS" formado por partículas sobre azul Klein. 19 s, 31 cortes.

**Para qué sirve:** Intro de marca / presentación de producto.

## Cómo reconocerlo
- **Texto:** Sans black gigante (palabra roja o azul), luego condensada sobre texturas 3D.
- **Animación y ritmo:** Física de rebote, cono de luz, partículas que forman letras; 31 cortes en 19 s.
- **Audio:** Música electrónica.
- **Medido en la referencia:** 19.2 s · 31 cortes (muy rápido, 1.61 cortes/s) · vertical 9:16
- **Paleta medida:** `#ece4d3` 35 % · `#0b0a0d` 31 % · `#1f32ec` 14 % · `#e15735` 9 % · `#453d3c` 6 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Guion corto

### 2. Pasos
1. Three.js en estilo-cine: esfera roja que rebota y proyecta un cono de luz que revela el texto
2. Cierre con texturas 3D y partículas

**Motor sugerido:** Three.js en estilo-cine (luz y partículas).

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Iluminar todo el texto a la vez
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
