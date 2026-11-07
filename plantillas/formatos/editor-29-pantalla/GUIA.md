# Guía para Claude · Editor 29 · pantalla · Demo con terminal

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

> **Origen:** es el video que se ve dentro de la laptop/monitor de Editor 29 · Laptop plateada ([`../editor-29/GUIA.md`](../editor-29/GUIA.md)), sacado derecho con `pantalla_interior.py`. Se puede publicar solo o volver a meter en una pantalla filmada.

## Qué es
**Familia:** Demo de App con Terminal

**La idea:** Demo de producto que mezcla animación y pantalla real: celular con chat y QR, ventana de la app con logo (botones de macOS), panel oscuro con estadísticas y la terminal de Claude Code escribiendo la integración.

**Lo que se ve en la referencia:** "Desde el 1 de octubre, la API de WhatsApp cobra" con celular y QR, ventana "Wazend" con botones de macOS, panel oscuro de la app, "Conecta tu WhatsApp con un QR", terminal de Claude Code que escribe la integración y celular final con el chat funcionando.

**Para qué sirve:** Mostrar cómo se instala/usa una herramienta con Claude Code (tutorial vendedor).

## Cómo reconocerlo
- **Texto:** Blanca bold con la palabra clave en rojo ("Desde el 1 de octubre, la API de WhatsApp cobra"); textos cortos que cuentan los pasos ("Dale a tu agente acceso…", "Tu agente escribe la integración").
- **Animación y ritmo:** 10 cortes en 25 s: zoom a la ventana, cursor que da clic, terminal que escribe sola, celular que entra girando.
- **Audio:** Voz en off + música tecnológica.
- **Medido en la referencia:** 25.2 s · 10 cortes (tranquilo, 0.4 cortes/s) · horizontal 16:9
- **Paleta medida:** `#191f28` 36 % · `#c7d7d5` 21 % · `#2d3841` 13 % · `#585c64` 12 % · `#9fb8b6` 9 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- La app real (capturas o grabación de pantalla)
- Los comandos reales que corre Claude Code

### 2. Pasos
1. Grabación de pantalla con el motor de Metodología (`estilo-cine/metodo_corte.py`, `metodo_zoom.py` para zoom al cursor)
2. Escenas en código: `claudecode`/`vscode` para la terminal que escribe sola, `telefonos` para el celular con el chat/QR
3. Ventana de la app con botones de macOS y logo; panel oscuro con estadísticas
4. Texto blanco bold con palabra clave en rojo; un texto corto por paso
5. Zoom a la ventana y cursor que da clic en cada paso

**Motor sugerido:** Interfaces en código (escenas vscode/claudecode y telefonos de estilo-cine) + grabación de pantalla real con el motor de Metodología.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Pasos que no existen en la app real
- Mostrar llaves o datos privados en la terminal
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
