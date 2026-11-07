# Guía para Claude · Editor 10 · Testimonio rojo

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Testimonio Cinemático

**La idea:** Persona de cuerpo completo en estudio de color con palabra gigante en degradado sobre el pecho, íconos 3D tipo emoji y cierre con B-roll emotivo.

**Lo que se ve en la referencia:** Mujer de cuerpo completo en estudio rojo. Sobre su pecho: línea chica blanca + palabra gigante condensada con degradado amarillo→naranja→rojo ("IMPORTAR", "CERCANAS", "IMPORTACIÓN"). Íconos 3D tipo emoji (portapapeles con lápiz) que entran desde abajo, burbujas, "¿" naranja dibujado. Cierre con B-roll cinematográfico emotivo (mujer llorando, apretón de manos, "aprender a CONFIAR"). Zooms de golpe con desenfoque. 17.6 s.

**Para qué sirve:** Testimoniales e historias personales.

## Cómo reconocerlo
- **Texto:** Línea chica blanca + palabra condensada gigante con degradado amarillo→naranja→rojo.
- **Animación y ritmo:** Zoom de golpe con desenfoque, íconos que entran desde abajo.
- **Audio:** Voz + música emotiva.
- **Medido en la referencia:** 17.6 s · 14 cortes (rápido, 0.8 cortes/s) · vertical 9:16
- **Paleta medida:** `#1c1210` 23 % · `#bd4539` 22 % · `#4e352e` 19 % · `#ce968d` 16 % · `#846d62` 13 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Testimonio en estudio de color, cuerpo completo

### 2. Pasos
1. Corte y subtítulos con `editor-testimoniales/editor/editar.py`
2. Palabra gigante en degradado sobre el pecho (capa de tipografía de estilo-cine con máscara)
3. Íconos 3D tipo emoji; cierre con B-roll emotivo (`broll_auto`)

**Motor sugerido:** Editor de testimoniales + capa de tipografía de estilo-cine.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Texto sobre la cara (la revisión final lo marca)
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
