# Guía para Claude · Editor 40 · pantalla · Keynote AirPods

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

> **Origen:** es el video que se ve dentro de la laptop/monitor de Editor 40 · Laptop keynote Apple ([`../editor-40/GUIA.md`](../editor-40/GUIA.md)), sacado derecho con `pantalla_interior.py`. Se puede publicar solo o volver a meter en una pantalla filmada.

## Qué es
**Familia:** Keynote de Producto

**La idea:** Presentación de producto estilo keynote de Apple: abre con un degradado radial (azul, verde, crema) y el nombre del producto; luego el producto 3D sobre fondo marfil que gira, se abre y se despieza; frases muy cortas en gris.

**Lo que se ve en la referencia:** Degradado radial azul-verde-crema con "All new AirPods Pro 3", estuche que se abre en 3D sobre fondo marfil, "Rebuilt from the ground up", audífono que gira y se alinea con las almohadillas de tallas, "Fit, finally figured out."

**Para qué sirve:** Lanzamiento de producto o servicio con look premium.

## Cómo reconocerlo
- **Texto:** SF Pro / sans fina gris oscuro, pequeña y centrada ("All new AirPods Pro 3", "Rebuilt from the ground up", "Fit, finally figured out.").
- **Animación y ritmo:** 7 s, 2 cortes: el degradado pulsa, el producto entra desde abajo y rota lento, piezas que se separan y se alinean.
- **Audio:** Música minimalista de keynote.
- **Medido en la referencia:** 7.1 s · 2 cortes (tranquilo, 0.28 cortes/s) · horizontal 16:9
- **Paleta medida:** `#d0c09e` 38 % · `#323635` 25 % · `#baab8f` 23 % · `#5cbcbc` 6 % · `#676960` 5 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Producto en 3D (modelo o imágenes de Higgsfield desde varios ángulos)
- 3–4 frases muy cortas

### 2. Pasos
1. Sigue `plantillas/estilo-apple/ESTILO.md` (desglose cuadro a cuadro)
2. Apertura: degradado radial azul-verde-crema que pulsa con el nombre del producto en sans fina
3. Producto al centro sobre marfil `#e9e4da`, girando lento; se abre o se despieza
4. Frases en gris pequeño centrado entre escenas
5. Música minimalista; 7–15 s

**Motor sugerido:** Plantilla Estilo Apple (estilo-apple/ESTILO.md): estilo-cine con fondo marfil #e9e4da, Three.js o imagen de Higgsfield del producto animada por código.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Texto grande o en negritas
- Colores fuertes fuera de la apertura
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
