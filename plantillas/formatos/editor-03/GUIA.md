# Guía para Claude · Editor 3 · Mascota en marfil

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Mascota en Marfil

**La idea:** Fondo marfil liso, una mascota 3D (robot) que interactúa con íconos, celular y tarjetas.

**Lo que se ve en la referencia:** Fondo marfil liso, mascota 3D (robot verde agua) + íconos (Instagram), celular mockup con perfil, tarjeta tipo skill con sello GRATIS, cuadrícula de 13 mascotas, candado resaltado "LA MEJOR". Titular arriba negro mayúsculas bold + palabra naranja. Subtítulos abajo en etiqueta negra mayúsculas chica con palabra naranja. Marca de agua arriba (píldora con handle). 14 s.

**Para qué sirve:** Noticia de herramienta (“Claude acaba de…”). Valor.

## Cómo reconocerlo
- **Texto:** Titular negro mayúsculas bold + palabra naranja; subtítulo en etiqueta negra mayúsculas chica con palabra naranja.
- **Animación y ritmo:** Objetos que entran con rebote, confeti, cuadrícula de 13 mascotas que se ilumina, candado resaltado.
- **Audio:** Voz en off + pops.
- **Medido en la referencia:** 13.9 s · 1 cortes (casi un solo plano, 0.07 cortes/s) · vertical 9:16
- **Paleta medida:** `#dad9cf` 42 % · `#e9e8e0` 33 % · `#f4f4ee` 18 % · `#b39996` 3 % · `#1e2020` 2 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Mascota (imagen de Higgsfield recortada)

### 2. Pasos
1. Fondo marfil liso en estilo-cine
2. Mascota recortada que interactúa con íconos, celular (`telefonos`) y tarjetas (`tarjetas`)
3. Texto negro palabra por palabra

**Motor sugerido:** Imágenes de Higgsfield (mascota) recortadas + animación por código sobre papel.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Fondos con textura
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
