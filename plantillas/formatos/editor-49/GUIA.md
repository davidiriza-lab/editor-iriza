# Guía para Claude · Editor 49 · Showreel cinemático

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Showreel Cinemático

**La idea:** Tipografía cinética gris/negra sobre marfil o negro con escenas 3D elegantes y oscuras (ojo, puerta con haz de luz, rosas, balanza, túnel).

**Lo que se ve en la referencia:** Tipografía cinética gris/negra sobre marfil o negro con escenas 3D oscuras y elegantes: ojo gigante, silueta "invisible", collage de pantallas inclinadas, carta de póker, ventana gótica con sombra, rosas rojas, puerta en pasto con haz de luz, balanza creatividad/eficiencia, reloj, túnel de luces, ramas de cerezo y hojas de maple. Palabras en distintos tamaños/pesos, onda de audio, desenfoque de movimiento entre escenas. 45 s, 40 cortes.

**Para qué sirve:** Es la referencia de la plantilla Cine Pro.

## Cómo reconocerlo
- **Texto:** Palabras de distintos tamaños y pesos, onda de audio, palabras borrosas que entran.
- **Animación y ritmo:** Desenfoque de movimiento entre escenas, 40 cortes en 45 s.
- **Audio:** Voz en off + música cinematográfica.
- **Medido en la referencia:** 44.9 s · 40 cortes (rápido, 0.89 cortes/s) · vertical 9:16
- **Paleta medida:** `#0d0d0c` 29 % · `#efeadf` 24 % · `#cac6bd` 14 % · `#333231` 14 % · `#695c56` 10 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Video de la persona (o voz)

### 2. Pasos
1. Plantilla Cine Pro (ya existe): tipografía cinética gris/negra sobre marfil o negro
2. Escenas 3D elegantes y oscuras (`ojo`, puerta con haz de luz, balanza, túnel)

**Motor sugerido:** Cine Pro (ya existe).

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Colores saturados
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
