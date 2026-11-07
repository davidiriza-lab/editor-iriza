# Guía para Claude · Editor 18 · Recorte sobre fondos

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Recorte en Collage (hermanos: Editor 39 · Collage papel amarillo)

**La idea:** Tú recortado (sin fondo) encima de fondos que cambian con cada idea: cuadrícula, papel arrugado, fotos, papel rasgado amarillo.

**Lo que se ve en la referencia:** Persona tipo selfie recortada (sin fondo) encima de fondos que cambian por idea: cuadrícula con titular "GANCHOS adictivos" (serif negra + script roja) e ilustración de cerebro, papel arrugado con capturas de estadísticas, foto de Santa Claus con gráfica de línea roja, fondo blanco con pictogramas (espectador → ojos; tú → Santa). Subtítulo: una palabra blanca mayúsculas con contorno negro a la altura del pecho. 28 s.

**Para qué sirve:** Hooks y explicaciones con mucha energía. OJO: a ti no te gustó cuando te cambiamos el fondo; usar solo si el recorte queda limpio.

## Cómo reconocerlo
- **Texto:** Titulares de póster (serif negra + script roja, o condensada negra sobre tiras de papel); subtítulo una palabra blanca mayúsculas con contorno.
- **Animación y ritmo:** Cambio de fondo por frase, stickers, cinta adhesiva, cabezas recortadas multiplicadas.
- **Audio:** Voz + efectos de papel.
- **Medido en la referencia:** 28.1 s · 5 cortes (tranquilo, 0.18 cortes/s) · vertical 9:16
- **Paleta medida:** `#f4f3f3` 44 % · `#ddd9d7` 23 % · `#c4bab6` 13 % · `#ae8b88` 11 % · `#775b58` 7 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Video de la persona

### 2. Pasos
1. Máscara de persona (`estilo-cine/preparar.py`, visual `persona` con `fondo: "estilo"`)
2. Fondos que cambian con cada idea: cuadrícula, papel arrugado, fotos, papel rasgado (Higgsfield o código)

**Motor sugerido:** Máscara de persona (Vision) + fondos de Higgsfield o collage en código.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Cambiar el fondo de la persona cuando la plantilla es Cine Pro (va con su fondo real): este formato es aparte
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
