# Guía para Claude · Editor 21 · Escritorio 3D

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Escritorio 3D

**La idea:** Entrevista/podcast con cortes a una mesa beige vista desde arriba donde aparecen objetos 3D (cerebro, foco, notas, storyboard).

**Lo que se ve en la referencia:** Entrevista/podcast (hombre hablando) con subtítulos cinéticos: serif amarilla brillante ("on videos"), caja naranja de resalte. Cortes a una mesa beige con sombra de ventana (vista cenital): cerebro 3D gris, foco amarillo, notas adhesivas, hojas de storyboard con clip, taza de café, flecha punteada, hojas de planta. Objetos que entran con rebote. 14 s.

**Para qué sirve:** Clips de podcast o reacciones a entrevistas.

## Cómo reconocerlo
- **Texto:** Subtítulos cinéticos: serif amarilla brillante, caja naranja de resalte.
- **Animación y ritmo:** Objetos que caen con rebote, flechas punteadas, sombra de ventana.
- **Audio:** Voz de la entrevista + música.
- **Medido en la referencia:** 14.1 s · 4 cortes (tranquilo, 0.28 cortes/s) · vertical 9:16
- **Paleta medida:** `#e3d7c0` 22 % · `#c2b59b` 21 % · `#979581` 18 % · `#0f110c` 17 % · `#7a705b` 12 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Entrevista/podcast + objetos (Higgsfield, solo imágenes)

### 2. Pasos
1. Corte de la entrevista
2. Cortes a una mesa beige vista desde arriba con objetos 3D recortados y animados por código

**Motor sugerido:** Imágenes de objetos de Higgsfield recortadas + animación por código.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Videos de Higgsfield
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
