# Guía para Claude · Editor 31 · pantalla · Comercial Shopify

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

> **Origen:** es el video que se ve dentro de la laptop/monitor de Editor 31 · Monitor verde Shopify ([`../editor-31/GUIA.md`](../editor-31/GUIA.md)), sacado derecho con `pantalla_interior.py`. Se puede publicar solo o volver a meter en una pantalla filmada.

## Qué es
**Familia:** Comercial de Marca con Resplandor (hermanos: Editor 30 · pantalla · Comercial Amazon, Editor 32 · pantalla · Comercial Higgsfield)

**La idea:** Comercial oscuro, casi negro, donde todo emite luz del color de la marca (naranja Amazon, verde Shopify, lima Higgsfield): logo dibujado por un trazo de luz, celular o interfaz flotando con halo, mapa 3D isométrico con ruta luminosa, objeto 3D (caja), eslogan final y logo.

**Lo que se ve en la referencia:** Negro con halo verde: logo de Shopify, celular con apps, listas de productos, tablero "Live View" con $0.00 que sube, "Sell what you make", "and hear your first sale" con notificación de pedido, logo final y crédito.

**Para qué sirve:** Recrear el comercial de una marca o de tu propio producto para demostrar que la IA lo hizo.

## Cómo reconocerlo
- **Texto:** Sans blanca limpia (estilo marca) centrada; una palabra en el color de la marca; textos muy cortos ("From A to Z.", "Sell what you make", "Become an AI Director.").
- **Animación y ritmo:** Cámara que viaja (dolly) entre escenas con desenfoque de movimiento; trazos de luz que conectan escenas; 0–16 cortes en ~20 s según la versión.
- **Audio:** Música de comercial épica-minimalista + efectos de luz (whoosh, shimmer).
- **Medido en la referencia:** 22.7 s · 0 cortes (casi un solo plano, 0.0 cortes/s) · horizontal 16:9
- **Paleta medida:** `#0d1211` 81 % · `#273f21` 9 % · `#2aa5b3` 3 % · `#776e6e` 3 % · `#cebfc9` 3 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Logo de la marca (SVG) y su color
- Objeto o interfaz protagonista (producto 3D, app, mapa)
- Eslogan corto

### 2. Pasos
1. estilo-cine en modo `codigo` (Three.js) con fondo `#050505` y halos/luces del color de la marca
2. Apertura: trazo de luz que dibuja el logo (logos extruidos de `logos`)
3. Escenas: celular o interfaz flotando con halo (`telefonos`/`interfaz`), mapa 3D isométrico con ruta luminosa o carrusel de tomas, objeto 3D (caja/producto)
4. Transiciones de cámara que viaja con desenfoque de movimiento (`trans: zoom`/`pan`)
5. Textos muy cortos en sans blanca, una palabra en el color de la marca
6. Cierre: eslogan + logo con halo
7. Música de comercial + efectos de luz

**Motor sugerido:** estilo-cine en modo código (Three.js: logos extruidos, mapa, objetos) con fondo #050505 y halos del color de la marca; interfaces en código para la app.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Fondos que no sean casi negros
- Más de un color de acento
- Usar la marca real en un anuncio sin permiso: para recrearla como ejercicio está bien, para publicar usa la tuya
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
