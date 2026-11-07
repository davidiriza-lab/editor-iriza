# Guía para Claude · Editor 6 · Raw vs Edited

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Raw vs Editado

**La idea:** Alterna la toma cruda (etiqueta “Raw”) y la editada (“Edited”) para presumir edición.

**Lo que se ve en la referencia:** Comparativo: etiqueta píldora arriba "Raw"/"Edited" que alterna. Lo crudo (persona sentada en estudio blanco o gym) y luego la versión editada: palabra gigante roja DETRÁS de la persona ("Scripts", "sell"), tarjetas flotantes con fotos, letras amarillas brillantes "BOMB", tarjeta cian tipo nota "mistake", "LEG DAY" detrás. Sirve como demo de servicio de edición. 19 s.

**Para qué sirve:** Vender el servicio de edición / mostrar el antes y después.

## Cómo reconocerlo
- **Texto:** Palabra gigante detrás de la persona (roja), tarjetas flotantes, letras amarillas brillantes, nota cian.
- **Animación y ritmo:** Corte seco Raw → Edited con desenfoque de movimiento.
- **Audio:** Canción.
- **Medido en la referencia:** 19.5 s · 12 cortes (rápido, 0.62 cortes/s) · vertical 9:16
- **Paleta medida:** `#e4e3e4` 44 % · `#463937` 18 % · `#151211` 17 % · `#bfb6b4` 10 % · `#837670` 9 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- El crudo y la versión editada con los mismos cortes

### 2. Pasos
1. Alternar crudo (etiqueta "Raw") y editado ("Edited") cada frase
2. O en doble pantalla con `estilo-cine/doble.mjs original.mov panel.mp4 salida.mp4 --etiqueta "X · SIN TOCAR"`

**Motor sugerido:** Igual a nuestro formato Original vs Editado (doble.mjs) pero alternando en vez de pantalla dividida.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Que el crudo y el editado se desfasen
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
