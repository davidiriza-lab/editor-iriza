# Guía para Claude · Pizarra Pro · Pizarra con íconos

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Pizarra Pro

**La idea:** Fondo blanco con cuadrícula fina tipo libreta: íconos en círculos oscuros (Claude, monitores) unidos con líneas punteadas, anillos azules con signos “?”, círculo que se rompe en pedazos, termómetro de proyectos que sube.

**Lo que se ve en la referencia:** Ver familia.

**Para qué sirve:** Explicar sistemas o cómo se conectan herramientas (Claude + Higgsfield).

## Cómo reconocerlo
- **Texto:** Etiquetas serif itálica en píldora terracota (“Claude”) y píldoras negras (“Project 1”).
- **Animación y ritmo:** Íconos que caen y se juntan en embudo, brillo naranja, piezas que se rompen y se arman.
- **Audio:** Voz en off.
- **Medido en la referencia:** 12.0 s · 3 cortes (tranquilo, 0.25 cortes/s) · vertical 9:16
- **Paleta medida:** `#d7d5d4` 38 % · `#bfbab6` 26 % · `#f1f0ef` 21 % · `#241c1a` 9 % · `#b96532` 3 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Esquema de la idea (nodos y conexiones)

### 2. Pasos
1. Organigrama animado en estilo-cine
2. Fondo blanco con cuadrícula fina; íconos en círculos oscuros unidos con líneas punteadas que se dibujan
3. Anillos azules con "?", círculo que se rompe en pedazos, termómetro que sube

**Motor sugerido:** Plantilla Esquema de empresa (Miro) animada en estilo-cine.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Colores fuera de negro, azul y blanco
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
