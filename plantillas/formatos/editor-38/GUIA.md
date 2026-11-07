# Guía para Claude · Editor 38 · Manías voxel

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Mundo Voxel (hermanos: Editor 2 · Tribunal voxel)

**La idea:** Personajes 3D tipo bloques (Claudes naranjas con cara) actuando la idea en un escenario: tribunal, oficina, riel con muro de “LÍMITE”.

**Lo que se ve en la referencia:** Fondo azul-negro con cuadrícula; personaje voxel naranja (Claude) en escritorio con hoja larga de factura, otro personaje (perro/emoji). Titular arriba blanco bold + línea amarilla/cian ("Tu Claude Code tiene *4 manías*"), tarjetas de colores numeradas con bordes neón (amarillo, rojo, verde, morado), barras comparativas cian "−53 %", carrito en riel contra muro "LÍMITE". Subtítulos abajo con resalte cian por palabra. Marca de agua abajo. 24 s.

**Para qué sirve:** Explicar un concepto abstracto (manías de Claude, cómo decide) de forma divertida. Valor.

## Cómo reconocerlo
- **Texto:** Titular arriba blanco bold + palabra en color/serif itálica; subtítulos chicos abajo con la palabra clave resaltada en caja (cian o dorada).
- **Animación y ritmo:** Cámara que viaja por la escena (dolly), desenfoque de profundidad entre planos, tarjetas de colores con bordes neón, barras comparativas animadas.
- **Audio:** Voz en off + efectos de juego.
- **Medido en la referencia:** 24.1 s · 9 cortes (tranquilo, 0.37 cortes/s) · vertical 9:16
- **Paleta medida:** `#0c0f12` 86 % · `#e1e0de` 4 % · `#607174` 3 % · `#ca6d4d` 3 % · `#413a38` 3 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Personajes (imágenes de Higgsfield, solo imágenes) o modelos 3D simples

### 2. Pasos
1. Three.js en estilo-cine: personajes con RoundedBox y caras, escenario simple (tribunal, oficina, riel)
2. Una acción por idea del guion
3. Texto palabra por palabra arriba

**Motor sugerido:** Three.js del motor (personajes con RoundedBox) o imágenes de Higgsfield de los personajes + animación por código.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Videos de Higgsfield (caros): animar con código
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
