# Guía para Claude · Editor 7 · Split hoja rayada

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

## Qué es
**Familia:** Split Explicador (hermanos: Editor 9 · Split podcast logos, Editor 12 · Split ilustración terracota, Editor 45 · Split sellos NUNCA, Editor 48 · Split pósters IA)

**La idea:** Pantalla dividida: arriba (40–45 %) un gráfico que cambia con cada idea; abajo tú hablando. El subtítulo vive en la unión.

**Lo que se ve en la referencia:** Arriba ~40 % blanco/hoja rayada con gráficos simples (logo de Instagram + mascota pixel de Claude con cuchillo, celular con perfil, tarjeta de skill con sello GRATIS, cuadrícula "13 skills", chat). Abajo ~60 % la persona hablando (casa, plantas). En la unión, subtítulo en etiqueta negra mayúsculas chica. Gráfico cambia con cada idea, ~1 cambio por segundo. 21 s.

**Para qué sirve:** Hablar a cámara sin perder el ritmo visual. Sirve para Dolor, Valor y Objeciones.

## Cómo reconocerlo
- **Texto:** Subtítulo en etiqueta (negra, azul o con bloque naranja detrás de la palabra) justo en la línea de unión. Arriba titulares cortos.
- **Animación y ritmo:** El gráfico de arriba cambia ~1 vez por segundo (íconos, pósters, sellos, capturas); tu toma corre continua.
- **Audio:** Tu voz + música baja.
- **Medido en la referencia:** 20.9 s · 3 cortes (casi un solo plano, 0.14 cortes/s) · vertical 9:16
- **Paleta medida:** `#eeeeec` 40 % · `#31302f` 23 % · `#1e1a18` 10 % · `#a17561` 9 % · `#675535` 9 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Video de la persona hablando

### 2. Pasos
1. Mitad de arriba (40–45 %): gráfico que cambia con cada idea, hecho en estilo-cine con lienzo horizontal
2. Mitad de abajo: la persona (corte con `metodo_corte.py` o el editor de testimoniales)
3. Armar con `estilo-cine/doble.mjs` (doble pantalla)
4. Subtítulo en la unión de las dos mitades

**Motor sugerido:** Lo tenemos casi: es el formato doble.mjs (Original vs Editado) con la mitad de arriba hecha en estilo-cine.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Que el subtítulo tape la cara
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
