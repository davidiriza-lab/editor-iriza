# Guía para Claude · Editor 35 · Montaje relámpago

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Montaje Relámpago

**La idea:** Hook en split (titular serif arriba, tú abajo) y luego montaje rapidísimo: tú, B-roll, capturas, titular pixel, billetes, celular.

**Lo que se ve en la referencia:** Pantalla dividida al inicio: arriba beige con titular serif ("Claude Code Skills", mascota pixel), abajo él con micrófono en estudio rojo. Luego montaje rapidísimo: titular pixel "CLAUDE CODE", íconos de archivos con flechas y números rojos a mano, B-roll (billetes contando, ventana con plantas), capturas, celular con WhatsApp sobre ciudad, destellos amarillos. Subtítulos blancos bold grandes + palabra amarilla/verde; algunos serif itálica. 16.7 s, 24 cortes.

**Para qué sirve:** Listas (“5 proyectos que…”). Valor.

## Cómo reconocerlo
- **Texto:** Subtítulos blancos bold grandes con palabra amarilla/verde; algunos en serif itálica.
- **Animación y ritmo:** Corte cada 0.5–0.7 s, destellos amarillos, zoom de golpe.
- **Audio:** Voz rápida + beat marcado.
- **Medido en la referencia:** 16.7 s · 24 cortes (muy rápido, 1.44 cortes/s) · vertical 9:16
- **Paleta medida:** `#130e12` 35 % · `#dbe1d9` 23 % · `#492f36` 17 % · `#827f81` 11 % · `#f3cb78` 8 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Video de la persona + B-roll y capturas

### 2. Pasos
1. Hook en split: titular serif arriba, persona abajo (`doble.mjs`)
2. Luego Cine Pro con cortes cada 0.5–1 s alternando persona, B-roll, capturas, titular pixel
3. Efectos de golpe en cada corte

**Motor sugerido:** Cine Pro con cortes más rápidos y B-roll.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Planos de más de 1.5 s después del hook
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
