# Guía para Claude · Editor 1 · pantalla · Documento cinético

> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del
> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta
> (si no están, básate en la descripción y en la paleta medida).

> **Origen:** es el video que se ve dentro de la laptop/monitor de Editor 1 · Laptop en la oscuridad ([`../editor-01/GUIA.md`](../editor-01/GUIA.md)), sacado derecho con `pantalla_interior.py`. Se puede publicar solo o volver a meter en una pantalla filmada.

## Qué es
**Familia:** Documento Cinético

**La idea:** Animación horizontal sobre una hoja blanca hueso tipo documento: la frase se escribe con tipografía cinética y aparecen objetos 3D (fajos de billetes) y cifras grandes. Parece un archivo de trabajo que cobra vida.

**Lo que se ve en la referencia:** Hoja blanca hueso en horizontal: "Tu caja te está mintiendo." letra por letra en sans negra con "mintiendo" en serif itálica azul; se apilan fajos de billetes verdes 3D, aparece "$4.000.000" y el subtítulo "Dice que hoy vendiste $4 millones. ¿Pero cuánto te quedó?" con palabras clave en verde y morado. 6 s, un solo plano.

**Para qué sirve:** Hook de dinero o de dolor de negocio ("tu caja te está mintiendo"). Funciona como el video que va DENTRO de la laptop de un video Pantalla Filmada.

## Cómo reconocerlo
- **Texto:** Sans negra grande que entra letra por letra con giro y desenfoque; palabra clave en serif itálica azul. Cifras gigantes arriba a la derecha ("$4.000.000"). Subtítulo chico abajo al centro, palabra por palabra, con la palabra clave en verde o morado.
- **Animación y ritmo:** Un solo plano de ~6 s sin cortes. Letras que caen y se acomodan; billetes 3D que se apilan desde arriba con rebote suave; cifra que aparece con fundido.
- **Audio:** Voz en off; música mínima.
- **Medido en la referencia:** 6.3 s · 0 cortes (casi un solo plano, 0.0 cortes/s) · horizontal 16:9
- **Paleta medida:** `#e3e3d4` 47 % · `#d9d6ca` 34 % · `#bcdaaf` 8 % · `#050607` 6 % · `#3f453f` 4 %

## Cómo hacerlo
### 0. Antes de empezar (siempre)
- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.
- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).
- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga "sí" (CLAUDE.md, paso 3).

### 1. Qué necesitas
- Guion corto (1–3 frases) con una cifra fuerte
- Voz (ElevenLabs o la persona) para sincronizar palabra por palabra

### 2. Pasos
1. Proyecto de estilo-cine con `"lienzo": {"w": 1920, "h": 1080}` y fondo papel `#e3dfd3`
2. Frase principal en sans negra gigante entrando letra por letra; la palabra clave en serif itálica azul
3. Objeto 3D del tema (escena `moneda` o billetes con Three.js en `cine.js`) que se apila desde arriba con rebote
4. Cifra gigante arriba a la derecha con fundido; subtítulo chico abajo palabra por palabra con la palabra clave en verde/morado
5. Un solo plano sin cortes (6–10 s)
6. Si va dentro de una laptop, úsalo como video interior del formato Pantalla Filmada

**Motor sugerido:** estilo-cine con lienzo horizontal 1920x1080, fondo papel #e3dfd3, escena moneda/tarjetas para los billetes 3D y grupos de texto palabra por palabra.

### 3. Antes de entregar (siempre)
- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.
- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.
- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.
- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> "<video>"` y mira las hojas de `revision_final/`.

## Evita
- Más de una idea por toma
- Colores saturados: es papel neutro con un solo acento
- Inventar datos, cifras o pantallas de apps que no existen.
- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.

Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`.
