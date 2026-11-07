# Guía para Claude · Editor 8 · Demo SaaS restaurante

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Comercial de Producto (hermanos: Editor 34 · Mundo 3D verde, Editor 47 · Comercial oscuro naranja)

**La idea:** Comercial sin persona: mockups de iPhone/iPad con la app real, mundo 3D o fotos cinematográficas por nicho, y titulares grandes.

**Lo que se ve en la referencia:** Sin persona. Intro oscura con resplandor radial naranja y pregunta grande blanca con palabras naranjas ("¿Y si tu restaurante funcionara en piloto automático?") + chips flotando. Luego fondo claro durazno-lavanda, barra de pasos con íconos arriba, titular negro bold + palabra naranja ("Tus clientes piden solos."), mockups de iPhone/iPad con la app real (QR, menú, pedido enviado ✓, cobrado $728, tickets por WhatsApp). Transiciones de dispositivo que entra/sale. 26 s.

**Para qué sirve:** Anunciar un producto o servicio propio (bots, apps, tarjetas de fidelidad).

## Cómo reconocerlo
- **Texto:** Titular blanco/negro bold + palabra en color de marca (naranja, verde menta) o serif itálica; resalte en caja.
- **Animación y ritmo:** Dispositivos que entran y salen, notificaciones, tarjetas UI que se apilan, cierre con logo y botón al sitio.
- **Audio:** Voz en off + música de marca.
- **Medido en la referencia:** 25.6 s · 13 cortes (rápido, 0.51 cortes/s) · vertical 9:16
- **Paleta medida:** `#f2eeed` 49 % · `#edded7` 26 % · `#161010` 10 % · `#8e7d73` 6 % · `#c4bbb8` 5 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Capturas reales de la app
- Fondos por nicho (Higgsfield, solo imágenes)

### 2. Pasos
1. estilo-cine sin persona: mockups de celular/tablet en código (`telefonos`) con la app real
2. Fondos cinematográficos o mundo 3D
3. Titulares grandes, uno por escena

**Motor sugerido:** estilo-cine + mockups de celular (ya los hacemos en código) + imágenes de Higgsfield para fondos.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Mockups con apps inventadas
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
