# Guía para Claude · Editor 31 · Monitor verde Shopify

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

> **El video que corre DENTRO de la pantalla es otro formato:** Editor 31 · pantalla · Comercial Shopify → [`../editor-31-pantalla/GUIA.md`](../editor-31-pantalla/GUIA.md). Hazlo primero y luego pégalo en la pantalla con esta guía.

## Qué es
**Familia:** Pantalla Filmada (hermanos: Editor 1 · Laptop en la oscuridad, Editor 13 · Laptop UI morada, Editor 15 · Laptop lienzo amarillo, Editor 17 · Monitor de edición, Editor 25 · Laptop escritorio luminoso, Editor 29 · Laptop plateada, Editor 30 · Monitor + laptop Amazon, Editor 32 · Monitor amarillo Higgsfield, Editor 40 · Laptop keynote Apple)

**La idea:** Se filma con el celular una laptop o monitor REAL (cuarto oscuro, escritorio con plantas o ventana con ciudad) y la animación vive dentro de la pantalla. Vende "esto lo hizo la IA": etiqueta fija arriba tipo "Video hecho 100% con Opus 5.5".

**Lo que se ve en la referencia:** Monitor frente a ventana con ciudad; comercial con resplandor verde neón (logo Shopify, celular, tarjetas de pedidos, frase final). Abajo timeline de edición visible. Etiqueta fija arriba "Claude Opus 5.5 🤓". 22.7 s.

**Para qué sirve:** Demostrar que la IA hizo un comercial/animación. Ideal para Autoridad y Valor (“mira lo que hizo Claude”).

## Cómo reconocerlo
- **Texto:** Etiqueta fija arriba (píldora negra o texto blanco bold con emoji). Dentro de la pantalla: tipografía cinética grande, palabra clave en otro color o en serif itálica.
- **Animación y ritmo:** Cámara en mano con micro-movimiento; dentro de la pantalla transiciones suaves con resplandor (glow) del color de la marca. Casi sin cortes: un solo plano de 6–30 s.
- **Audio:** Música o voz en off; el sonido real del cuarto se pierde.
- **Medido en la referencia:** 22.7 s · 0 cortes (casi un solo plano, 0.0 cortes/s) · vertical 9:16
- **Paleta medida:** `#0b0d0e` 50 % · `#afc6e3` 17 % · `#282e2a` 14 % · `#d6e0ec` 12 % · `#757874` 6 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Una toma REAL de una laptop o monitor, de 6–30 s, en celular vertical, con la pantalla en blanco o apagada (o una imagen de Higgsfield de una laptop en el ambiente deseado: cuarto oscuro, escritorio con plantas o ventana con ciudad)
- El video que va DENTRO de la pantalla: hazlo con el formato interior correspondiente (p. ej. Editor 1 · pantalla, Editor 30 · pantalla)
- Texto de la etiqueta fija de arriba (p. ej. "Video hecho 100% con Opus 5.5")

### 2. Pasos
1. Haz primero el video interior (horizontal 1920x1080, salvo que la pantalla sea vertical) con su propia guía y rénderalo
2. Marca las 4 esquinas de la pantalla en la toma: en estilo-cine la escena `laptop` recibe `img` (toma o imagen) y `pantalla` (4 esquinas en px) y pega el video interior en perspectiva
3. Si la cámara se mueve, sigue la pantalla cuadro por cuadro: `plantillas/formatos/pantalla_interior.py` ya resuelve el seguimiento (homografía con puntos fuera de la pantalla); usa la misma lógica a la inversa para pegar
4. Agrega la etiqueta fija arriba (píldora negra o texto blanco bold) dentro de la zona segura (y ≥ 262)
5. Suma reflejo/brillo leve sobre la pantalla para que no se vea pegada
6. Audio: voz en off o música del video interior

**Motor sugerido:** Ya lo tenemos casi: animación con estilo-cine/HTML → render → se pega en perspectiva sobre una toma real de tu laptop (como la laptop de Higgsfield de C8253). Solo falta grabar tu laptop/monitor con la pantalla en blanco.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Que el video interior se vea plano o sin perspectiva (debe seguir la pantalla)
- Cortes: es un solo plano largo
- Tapar la pantalla con el texto
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
