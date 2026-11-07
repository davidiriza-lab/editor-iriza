# Guía para Claude · Editor 16 · Tarjetas Anthropic

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Tarjetas Anthropic

**La idea:** Fondo carbón, tarjetas oscuras que aparecen una por una con cifras que cuentan; titular serif con palabra itálica naranja subrayada a mano.

**Lo que se ve en la referencia:** Sin persona. Fondo carbón casi negro. Etiqueta arriba en mayúsculas naranja espaciada ("SI TE ACEPTAN"). Tarjetas oscuras con borde sutil que aparecen una a una en cuadrícula 2x2 (logo + cifra grande que cuenta: "1 año", "$1.000", "$45K", "45 sesiones"). Luego titular serif con palabra itálica naranja subrayada a mano ("¿Quién puede *postular*?") y barras de progreso naranjas. Subtítulos abajo gris chico con palabra naranja. Estética Anthropic. 22.7 s, sin cortes.

**Para qué sirve:** Explicar beneficios, programas o requisitos (becas, ofertas).

## Cómo reconocerlo
- **Texto:** Etiqueta mayúsculas naranja espaciada arriba; cifras grandes; subtítulo gris chico con palabra naranja.
- **Animación y ritmo:** Tarjetas en cuadrícula 2x2 que entran en orden, contadores, barras de progreso.
- **Audio:** Voz en off tranquila.
- **Medido en la referencia:** 22.7 s · 0 cortes (casi un solo plano, 0.0 cortes/s) · vertical 9:16
- **Paleta medida:** `#11120d` 82 % · `#1e1c1b` 15 % · `#524c49` 1 % · `#908f8e` 1 % · `#e2e2df` 1 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Cifras reales

### 2. Pasos
1. Fondo carbón en estilo-cine
2. Tarjetas oscuras (`tarjetas`) que aparecen una por una con `contador`
3. Titular serif con palabra itálica naranja subrayada a mano

**Motor sugerido:** estilo-cine (tarjetas + contadores ya existen).

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Más de 4 tarjetas a la vez
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
