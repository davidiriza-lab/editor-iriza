# Guía para Claude · Editor 13 · pantalla · Órbita de creadores

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

> **Origen:** es el video que se ve dentro de la laptop/monitor de Editor 13 · Laptop UI morada ([`../editor-13/GUIA.md`](../editor-13/GUIA.md)), sacado derecho con `pantalla_interior.py`. Se puede publicar solo o volver a meter en una pantalla filmada.

## Qué es
**Familia:** Interfaz en Órbita

**La idea:** Fondo morado oscuro con viñeta: tarjetas de interfaz (chat de WhatsApp, teclado numérico, tablero de creativos) y un círculo de fotos verticales de creadores que gira alrededor de un logo (Meta).

**Lo que se ve en la referencia:** Fondo morado oscuro: chat de WhatsApp con una creadora, mosaico de fotos verticales de creadores que se acomodan en un anillo alrededor del logo de Meta, tablero de "creativos nuevos" con miniaturas y tachado rojo. Texto blanco con palabras en lila ("tuvieras de 10 a 100 videos", "Meta") y serif itálica gris.

**Para qué sirve:** Explicar un servicio digital (anuncios, contenido UGC, automatización) con piezas de interfaz reales.

## Cómo reconocerlo
- **Texto:** Blanca bold centrada arriba; palabras clave en lila/morado; frases secundarias en serif itálica gris. Subtítulo abajo palabra por palabra.
- **Animación y ritmo:** Continuo, sin cortes (~16 s): tarjetas que entran con desenfoque, fotos que se acomodan en anillo y orbitan, contador que sube, tachado rojo sobre una tarjeta para el "problema".
- **Audio:** Voz en off + música suave tecnológica.
- **Medido en la referencia:** 15.7 s · 0 cortes (casi un solo plano, 0.0 cortes/s) · horizontal 16:9
- **Paleta medida:** `#19181d` 58 % · `#060808` 20 % · `#2c2b38` 15 % · `#a69e8b` 3 % · `#dae9da` 2 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Capturas o mockups de las interfaces (chat, tablero, teclado)
- Fotos verticales de personas/creadores (propias o de Higgsfield)
- Logo de la plataforma (SVG)

### 2. Pasos
1. estilo-cine horizontal, fondo `#1b1626` con viñeta morada
2. Escena `chat` para la conversación de WhatsApp y `tarjetas` para el tablero; teclado y contadores con `contador`
3. Anillo de fotos que orbita alrededor del logo: Three.js en `cine.js` (no existe como escena: agrégala como `orbita` con N tarjetas en círculo)
4. Texto blanco bold centrado arriba, palabras clave en lila `#b48cff`, frases secundarias en serif itálica gris
5. Tachado rojo animado sobre la tarjeta del problema
6. Sin cortes: todo se transforma en un solo plano

**Motor sugerido:** estilo-cine: escenas tarjetas/chat/telefonos con lienzo horizontal, fondo #1b1626 con viñeta morada, órbita con Three.js o CSS.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Fondos planos sin viñeta
- Cortes secos entre escenas
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
