# Guía para Claude · Editor 41 · Pósters IA motivación

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Póster Editorial (hermanos: Editor 23 · Póster de revista, Editor 42 · Póster lavanda)

**La idea:** Cada frase es un póster: imagen IA fotorrealista (calavera dorada, pan, ajedrez de vidrio) + tipografía de revista.

**Lo que se ve en la referencia:** Imágenes generadas fotorrealistas a pantalla completa (calavera dorada con corona, Pantera Rosa con sudadera, polaroids con emojis en tendedero, reloj de arena) + tipografía de póster: serif itálica + condensada mayúsculas, palabra repetida en capas degradadas ("SILENT"), palabra que pasa detrás del objeto. Mensaje motivacional en inglés. 7 s, un cambio por frase.

**Para qué sirve:** Frases motivacionales o de mentalidad. Encaja con tu marca personal.

## Cómo reconocerlo
- **Texto:** Condensada gigante + serif itálica; palabra repetida en capas; bloques de texto chico justificado.
- **Animación y ritmo:** Corte seco por frase, leve zoom, palabra que pasa detrás del objeto.
- **Audio:** Voz en off grave + música.
- **Medido en la referencia:** 7.0 s · 4 cortes (rápido, 0.57 cortes/s) · vertical 9:16
- **Paleta medida:** `#ece8e1` 34 % · `#110f0f` 25 % · `#43232c` 16 % · `#6f5448` 9 % · `#c4b4b2` 8 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Una imagen IA fotorrealista por frase (Higgsfield, GPT Image)

### 2. Pasos
1. `estilo-cine/gen_hf.py` para las imágenes (solo imágenes)
2. Cada frase = un póster: imagen + tipografía de revista en estilo-cine
3. Transición de página entre pósters

**Motor sugerido:** Imágenes de Higgsfield (GPT Image) + tipografía en estilo-cine.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Más de una frase por póster
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
