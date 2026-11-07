# Guía para Claude · Editor 15 · pantalla · Lienzo amarillo

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

> **Origen:** es el video que se ve dentro de la laptop/monitor de Editor 15 · Laptop lienzo amarillo ([`../editor-15/GUIA.md`](../editor-15/GUIA.md)), sacado derecho con `pantalla_interior.py`. Se puede publicar solo o volver a meter en una pantalla filmada.

## Qué es
**Familia:** Lienzo Amarillo con Íconos

**La idea:** Vertical 9:16 con fondo amarillo saturado: frases cortas, íconos de línea negros (velocímetro con aguja, personas, hexágonos con íconos) y una mascota negra en la esquina.

**Lo que se ve en la referencia:** Vertical amarillo: "Tiempo" gigante, "El tiempo de tu equipo es caro" con un velocímetro cuya aguja gira, equipo de personitas en un marco, "Lo que la IA hace" con notas flotantes, contador "3 en segundos" y hexágonos con íconos que se conectan; mascota negra abajo.

**Para qué sirve:** Explicar un beneficio con metáforas visuales simples (tiempo, equipo, IA que ayuda).

## Cómo reconocerlo
- **Texto:** Sans negra mediana para frases; palabra gigante condensada al entrar ("Tiempo"); serif itálica para la frase de remate ("cada hora"); notas tipo post-it flotando.
- **Animación y ritmo:** Transiciones con desenfoque y zoom, aguja que gira, hexágonos que se duplican y se conectan, contador circular "3 en segundos". 1 corte en 12 s.
- **Audio:** Voz en off + música alegre.
- **Medido en la referencia:** 12.5 s · 1 cortes (casi un solo plano, 0.08 cortes/s) · vertical 9:16
- **Paleta medida:** `#dca304` 46 % · `#f0c906` 27 % · `#241d11` 17 % · `#6a4f17` 5 % · `#7f9578` 3 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Guion con 4–6 ideas simples (tiempo, equipo, IA, resultado)
- Íconos de línea (SVG) y una mascota/personaje (Higgsfield, solo imagen)

### 2. Pasos
1. estilo-cine vertical con fondo amarillo `#f1b80c`
2. Palabra gigante condensada que entra con desenfoque; frases en sans negra mediana; remate en serif itálica
3. Metáforas con íconos: velocímetro con aguja que gira, personas en un marco, hexágonos con íconos que se duplican y se conectan
4. Contador circular con `contador` ("3 en segundos")
5. Mascota fija abajo a la derecha que reacciona
6. Transiciones con desenfoque y zoom (`trans: zoom`)

**Motor sugerido:** estilo-cine vertical con tema de fondo #f1b80c, íconos SVG de línea, escena contador y tarjetas.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Fotografía: aquí todo es ícono de línea negro
- Más de 2 colores además del amarillo
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
