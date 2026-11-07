# Guía para Claude · Editor 25 · pantalla · Coral con cifras

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

> **Origen:** es el video que se ve dentro de la laptop/monitor de Editor 25 · Laptop escritorio luminoso ([`../editor-25/GUIA.md`](../editor-25/GUIA.md)), sacado derecho con `pantalla_interior.py`. Se puede publicar solo o volver a meter en una pantalla filmada.

## Qué es
**Familia:** Tarjetas Coral con Cifras

**La idea:** Horizontal y muy dinámico: alterna fondos coral/salmón, gris oscuro y blanco; ventanas de app 3D apiladas, pantalla dividida "vos vs tu competencia" con chats, cifras gigantes ("+28 negocios", "8 países") con cintas de texto diagonales y mockup de celular.

**Lo que se ve en la referencia:** "hay empresas que se van a fundir", cartel CERRADO con globos de notificación, "por no usar inteligencia artificial" en coral, chat repetido "×9 el mismo mensaje", ventanas de facturas 3D, pantalla dividida vos vs tu competencia, glitch "se va", "+28 negocios", "8 países" con cintas diagonales y celular "automatizamos tu whatsapp".

**Para qué sirve:** Vender automatización o un servicio a negocios con prueba social en números.

## Cómo reconocerlo
- **Texto:** Sans redondeada extra bold (blanca o negra); palabra clave en coral o rojo; subtítulo abajo con la palabra clave resaltada; etiquetas tipo píldora ("vos", "tu competencia").
- **Animación y ritmo:** Rápido: 11 cortes en 26 s. Entradas con rebote, glitch de texto ("se va"), cintas que corren, contadores que suben, ventanas que caen en cascada.
- **Audio:** Voz en off + música enérgica + efectos (pop, whoosh).
- **Medido en la referencia:** 25.7 s · 11 cortes (tranquilo, 0.43 cortes/s) · horizontal 16:9
- **Paleta medida:** `#ded8d5` 23 % · `#51444a` 21 % · `#211c1f` 20 % · `#7c6b74` 16 % · `#a7a4b8` 12 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Guion de problema → solución → prueba social con cifras
- Datos reales (número de negocios, países)

### 2. Pasos
1. estilo-cine horizontal; paleta coral `#f26b5b`, gris `#2a2a2e`, blanco hueso `#f2f0ec`
2. Problema: cartel/escena con globos de notificación; chat repetido "×9 el mismo mensaje" con `chat`
3. Pantalla dividida "vos vs tu competencia": dos escenas `chat` lado a lado con etiquetas píldora
4. Glitch de texto en la palabra de pérdida (`trans: glitch`)
5. Cifras gigantes con `contador`; cintas de texto diagonales que corren (agregar a `cine.js` si no existe: banda rotada con texto en loop)
6. Cierre con mockup de celular (`telefonos`) y CTA
7. Ritmo rápido: un cambio cada ~2 s con efectos pop/whoosh

**Motor sugerido:** estilo-cine horizontal: escenas chat (split), contador, tarjetas, telefonos; paleta #f26b5b / #2a2a2e / #f2f0ec.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Cifras inventadas
- Texto largo: máximo 6 palabras por pantalla
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
