# Guía para Claude · Editor 20 · UI flotante azul

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** UI Minimal (hermanos: Editor 24 · Blanco minimal buscador, Editor 50 · Intro perfil gris)

**La idea:** Elementos de interfaz aislados flotando sobre fondo liso (negro con brillo azul o blanco/gris), con cursor que hace clic.

**Lo que se ve en la referencia:** Fondo negro total. Elementos de interfaz aislados que flotan con resplandor azul/morado: logo de Drive, botón "+ New" con cursor, menú desplegable, tarjeta "Upload" que se inclina en 3D, barra de progreso verde. Tutorial sin persona ni texto grande. 11 s.

**Para qué sirve:** Tutoriales cortos o anuncios de tu propia cuenta.

## Cómo reconocerlo
- **Texto:** Sans fina negra/blanca; palabras que entran por letras; palabra en azul o rojo.
- **Animación y ritmo:** Botones que se presionan, menús que se despliegan, tarjetas que se inclinan en 3D, barras de progreso.
- **Audio:** Clics y whooshes.
- **Medido en la referencia:** 11.3 s · 0 cortes (casi un solo plano, 0.0 cortes/s) · vertical 9:16
- **Paleta medida:** `#000000` 90 % · `#010017` 6 % · `#121215` 3 % · `#20223e` 0 % · `#546586` 0 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Interfaces reales a recrear

### 2. Pasos
1. Interfaces en código (escena `interfaz` de Cine Pro 3D) sin fondo
2. Fondo liso negro con brillo azul o blanco/gris
3. Cursor que hace clic

**Motor sugerido:** Interfaces en código (como las de Cine Pro 3D) sin fondo.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Ruido visual alrededor de la interfaz
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
