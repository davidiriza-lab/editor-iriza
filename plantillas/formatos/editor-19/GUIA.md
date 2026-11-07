# Guía para Claude · Editor 19 · Vidrio sobre toma real

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Vidrio sobre Toma Real

**La idea:** Toma real ambiental (tú en la laptop, sin hablar) con tarjetas de vidrio esmerilado numeradas encima.

**Lo que se ve en la referencia:** Persona en su laptop con luz morada/ambiente (toma real, sin hablar a cámara). Titular arriba mezcla serif itálica naranja + sans blanca bold ("*7 agentes* de Claude / que puedes crear / *en 10 minutos*"). Luego tarjetas de vidrio esmerilado numeradas "01/07 Setter 24/7", "02 Busca clientes"… con mini diagrama de flujo de íconos y logo Claude en la esquina; cada tarjeta reemplaza a la anterior. 7 s.

**Para qué sirve:** Listas rápidas (“7 agentes que puedes crear”). Valor.

## Cómo reconocerlo
- **Texto:** Titular serif itálica naranja + sans blanca bold; tarjetas “01/07 Setter 24/7” con mini diagrama de íconos.
- **Animación y ritmo:** Cada tarjeta reemplaza a la anterior con desenfoque.
- **Audio:** Música.
- **Medido en la referencia:** 7.0 s · 0 cortes (casi un solo plano, 0.0 cortes/s) · vertical 9:16
- **Paleta medida:** `#1e171f` 27 % · `#63504a` 25 % · `#3c323d` 23 % · `#866d5a` 18 % · `#2e3a6f` 5 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Toma real ambiental (persona en la laptop, sin hablar)

### 2. Pasos
1. estilo-cine sobre la toma real
2. Tarjetas de vidrio esmerilado numeradas (blur de fondo + borde claro) que aparecen con cada punto

**Motor sugerido:** estilo-cine sobre tu toma real.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Tarjetas opacas
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
