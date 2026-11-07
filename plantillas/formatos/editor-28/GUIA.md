# Guía para Claude · Editor 28 · Tutorial cuadrícula clara

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Tutorial con Flechas (hermanos: Editor 4 · Tutorial en laptop, Editor 26 · Tutorial cuadrícula negra)

**La idea:** Paso a paso de una herramienta con capturas reales. Cada clic se señala con una flecha roja curva dibujada a mano y un recuadro rojo.

**Lo que se ve en la referencia:** Igual al 26 pero en papel hueso con cuadrícula fina: titular negro bold + palabra coral ("Cómo crear carruseles *ganadores* en 60 segundos"), tarjetas/capturas oscuras al centro, flecha roja curva señalando, carruseles de ejemplo, cierre "Comenta "IA"" grande con flecha. Subtítulo negro chico arriba de la tarjeta. 25.5 s.

**Para qué sirve:** Tutoriales y lead magnets (“comenta X y te mando el tutorial”). Metodología.

## Cómo reconocerlo
- **Texto:** Titular grande blanco o negro con palabra en color ("Cómo crear carruseles *ganadores*"). Subtítulo corto (2–4 palabras) justo arriba de la captura; "Paso uno/dos/tres". Cierre con CTA grande "Comenta “BOT”".
- **Animación y ritmo:** Corte cada ~1 s, zoom a la ventana activa, flecha que entra con rebote, sello verde "CONNECTED" cuando algo queda listo.
- **Audio:** Voz en off rápida + clics y whooshes suaves.
- **Medido en la referencia:** 25.5 s · 14 cortes (rápido, 0.55 cortes/s) · vertical 9:16
- **Paleta medida:** `#edeae0` 76 % · `#191816` 17 % · `#c4c0b9` 3 % · `#565452` 2 % · `#938880` 2 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Grabación de pantalla de cada paso de la herramienta

### 2. Pasos
1. Motor de Metodología: `estilo-cine/metodo_corte.py` + `metodo_zoom.py` (zoom al cursor) + `metodo.mjs`
2. Flechas rojas curvas dibujadas a mano y recuadros rojos en cada clic (capa SVG; si no existe en metodo.mjs, agrégala)
3. Fondo de cuadrícula alrededor de la captura
4. Texto del paso abajo, corto

**Motor sugerido:** Se hace con el motor de Metodología (grabación de pantalla + zoom al cursor) agregando flechas rojas y fondo de cuadrícula.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Pasos de más: solo los clics necesarios
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
