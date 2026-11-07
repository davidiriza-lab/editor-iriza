# Guía para Claude · Editor 14 · Franja cinemascope

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Franja Cinemascope (hermanos: Editor 22 · Texto con brillo rojo)

**La idea:** Fondo negro con una franja horizontal al centro (formato panorámico) donde pasa toda la animación.

**Lo que se ve en la referencia:** Fondo negro con una franja horizontal blanca al centro (formato panorámico). Motion graphics minimal: guías de diseño, "Hello" con mano saludando, silueta de perfil, ojo de gato que se abre, palabras que rotan ("Creative Producer/Director/Editor/Partner"), logo al final. Tipografía sans negra fina. Presentación de marca personal. 11 s.

**Para qué sirve:** Intros de marca personal o presentaciones.

## Cómo reconocerlo
- **Texto:** Sans fina; palabra clave con brillo naranja/rojo; animaciones de texto: pixelado, máquina de escribir, rebote.
- **Animación y ritmo:** Motion graphics minimal (ojo que se abre, silueta, palabras que rotan).
- **Audio:** Música ambiental.
- **Medido en la referencia:** 11.1 s · 4 cortes (tranquilo, 0.36 cortes/s) · vertical 9:16
- **Paleta medida:** `#000000` 69 % · `#f1f3f6` 18 % · `#0c0b1a` 12 % · `#ca9167` 0 % · `#766359` 0 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Animación en panorámico

### 2. Pasos
1. estilo-cine con lienzo panorámico (`"lienzo"`) dentro de un fondo negro vertical
2. Toda la animación vive en la franja central

**Motor sugerido:** estilo-cine con lienzo panorámico (ya soporta “lienzo”).

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Elementos fuera de la franja
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
