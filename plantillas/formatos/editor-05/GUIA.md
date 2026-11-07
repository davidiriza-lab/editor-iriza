# Guía para Claude · Editor 5 · Tipografía roja

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Tipografía Roja Editorial

**La idea:** Persona real con tipografía cinética muy cargada alrededor: palabras en arco, silueta rellena de rojo, papel rasgado que revela billetes, collage de recortes de la cara.

**Lo que se ve en la referencia:** Persona real (mujer) + tipografía cinética muy cargada: palabras que giran en arco alrededor de ella (texto en curva), mezcla de sans blanca + serif itálica + rojo; silueta rellena de rojo con "!!!" dibujado; papel rasgado que revela billetes ("ten grand"); collage de recortes de la cara; destellos blancos; cámara con zoom. Paleta rojo/blanco/negro. 11 s, 10 cortes.

**Para qué sirve:** Hooks muy llamativos con persona. Dolor.

## Cómo reconocerlo
- **Texto:** Sans blanca + serif itálica + rojo; texto que gira en curva alrededor de la persona.
- **Animación y ritmo:** Zoom y giros, destellos blancos, papel que se rasga; 10 cortes en 11 s.
- **Audio:** Voz + efectos de papel y golpe.
- **Medido en la referencia:** 11.4 s · 10 cortes (rápido, 0.88 cortes/s) · vertical 9:16
- **Paleta medida:** `#463a3c` 25 % · `#82645d` 22 % · `#131012` 19 % · `#b7a08e` 13 % · `#e9e6dc` 10 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Video de la persona

### 2. Pasos
1. Máscara de persona con `estilo-cine/preparar.py`
2. Texto en curva y arcos alrededor de la persona, silueta rellena de rojo, papel rasgado que revela imágenes
3. Collage de recortes de la cara

**Motor sugerido:** estilo-cine con texto en curva y máscara de persona (ya la tenemos).

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Texto sobre la boca
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
