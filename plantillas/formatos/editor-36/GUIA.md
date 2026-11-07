# Guía para Claude · Editor 36 · Brutalista neón

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Brutalista Neón

**La idea:** Franja negra arriba con titular condensado en mayúsculas y una palabra verde neón tachada; luego pantallas negras con una palabra itálica por golpe.

**Lo que se ve en la referencia:** Arriba franja negra con titular condensado en mayúsculas: logo Claude + "CLAUDE / MOTION (verde neón, tachado) / DESIGNERS.". Él abajo frente a ventana con edificios. Luego fondo negro con una palabra itálica condensada por golpe ("EDITAR", "CREAR", "VIDEOS"...) sobre UI de Claude y póster verde neón "PROMPTEA FÁCIL"; fondos naranja. Subtítulos en caja roja itálica mayúsculas en la unión. 16 s.

**Para qué sirve:** Declaraciones fuertes (“Claude mató a…”). Dolor/Autoridad.

## Cómo reconocerlo
- **Texto:** Condensada mayúsculas (tipo Druk) blanca + verde neón; subtítulos en caja roja itálica mayúsculas.
- **Animación y ritmo:** Una palabra por golpe al ritmo de la voz, pósters verde neón, fondos naranja.
- **Audio:** Voz + golpes secos.
- **Medido en la referencia:** 16.0 s · 11 cortes (rápido, 0.69 cortes/s) · vertical 9:16
- **Paleta medida:** `#040509` 44 % · `#e6e6df` 21 % · `#9da693` 13 % · `#c1571a` 8 % · `#dbca3c` 7 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Guion de frases cortas

### 2. Pasos
1. estilo-cine con fuente condensada en mayúsculas (Anton/Bebas Neue incluidas)
2. Franja negra arriba con titular; una palabra verde neón tachada
3. Pantallas negras con una palabra itálica por golpe

**Motor sugerido:** estilo-cine con fuente condensada + paleta negro/verde neón.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Más de dos colores (negro + verde neón)
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
