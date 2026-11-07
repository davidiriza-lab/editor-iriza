# Editor Iriza · instrucciones para Claude

Sistema de edición para reels y anuncios verticales grabados a cámara: corte de tomas, subtítulos palabra por palabra, filtro de piel, gráficos y escenas 3D hechos con código, interfaces emuladas y render en 1080 o 4K. Es una base para mejorar: cuando una corrección de la persona sirva para otros videos, déjala aquí como regla o como código.

Los datos de la persona (nombre, @usuario, carpeta de videos) están en `config/kit.json`: úsalos en cada `cine.json` (`"nombre"`, `"handle"`). Si falta `.venv`, `bin/segmentar` o `config/kit.json`, corre `./instalar.sh` antes de nada, y después `./verificar.sh`.

## Cuál herramienta usar
| Material | Herramienta |
|---|---|
| Reel a cámara, tutorial, reacción, lista de herramientas | `estilo-cine/` (Cine Pro y formatos). Elegir con `plantillas/formatos/GUIA-FORMATOS.md`; no repetir estilo entre videos de una tanda |
| Anuncio grabado frase por frase (varias tomas de cada frase) | `plantillas/anuncio-por-frases/`: se copia a `proyectos/<nombre>` y trae la receta probada de cortes sin saltos (ver su `LEEME.md`) |
| Testimonial, entrevista o anuncio a cámara con guion | `editor-testimoniales/`: `editor/editar.py <proyecto> plan → armar → terminar`, con revisiones que frenan la entrega |
| Anuncio con gráficos por cues y zoom a la cara | `editor-anuncios/` (`prepare → build → armar_cues → track → render`) |
| Reel sin cara con voz IA, simple | `motor/` + `./video` (`docs/motor-tutoriales.md`) |
| Video animado sin cara (explicador 3D, motion graphics) | Fuera de aquí: la fábrica de animados, https://github.com/davidiriza-lab/fabrica-animados |
| Motion graphics puro | HyperFrames o Remotion |
| Retoque manual del timeline | El editor que use la persona (CapCut, Premiere, DaVinci) |

## Qué hay aquí
| Carpeta | Para qué |
|---|---|
| `estilo-cine/` | **Motor principal**: `cine.js` (escenas, texto, 3D, interfaces), `render.mjs`, `metodo_corte.py`, `transcribir.py`, `quitar_tramos.py`, `preparar.py`, `piel.py`, `prep4k.py`, `volumen.mjs`, reacción (`reac_*.py`), doble pantalla (`doble.mjs`), tutorial cámara+pantalla (`metodo*.{py,mjs}`). Ver su README. |
| `plantillas/` | `cine-pro/`, `cine-pro-3d/` (receta + `cine_base.json`), `estilo-apple/`, `lista-herramientas/`, `anuncio-por-frases/` y `formatos/<formato>/` (61 formatos con `GUIA.md` y `ESTILO.md`). Las imágenes de referencia de cada formato (`hoja.jpg`, `cuadros/`) no vienen en el repo porque son cuadros de videos de otros creadores: la guía describe el look con palabras y medidas. |
| `editor-anuncios/` | Anuncios con retomas: zoom con cara, subtítulos, transiciones, cues y `estilos.js`. `palabras_a_words.py` convierte el JSON de `whisper-cli -oj -ml 1 -sow` al `words.json` que pide `prepare.py`. `verificar_finales.sh <proyectos…>` revisa duración, LUFS, fluidez y palabras perdidas. |
| `editor-testimoniales/` | Testimoniales y anuncios a cámara. Ver su README. |
| `motor/` + `video` | Reels sin cara con voz de ElevenLabs. |
| `audio/` | Catálogo de música y generador de efectos libres (`audio/LEEME.md`). |
| `skills/` | `editor-iriza`, que `instalar.sh` copia a `~/.claude/skills`. |

## Antes de editar: preguntar (una sola vez, todo junto)
- **Música:** ¿carpeta con canciones propias o con licencia, o sin música? Sin música no se entrega, salvo que la persona diga "sin música". Si se genera con MusicGen, avisar que sus pesos son CC-BY-NC: no sirve para anuncios pagados.
- **Duración máxima** del video: con eso se decide qué partes entran y cuáles no.
- **Formato:** Redes 1080 (por defecto) o 4K.
- **Nombres propios** que Whisper escribe mal (personas, marcas).

## Flujo de trabajo (no saltarse pasos)
1. **Elegir herramienta** con la tabla de arriba. Si la persona nombra una plantilla ("Cine Pro", "Cine Pro 3D", "Editor 12"…), manda eso. Si hay dos capturas de la misma sesión, usar la de 60 fps.
2. **Transcribir y buscar retomas:** `transcribir.py --tramos`. Whisper de corrido FUSIONA frases repetidas: confirma cada sospecha con la energía del audio (pasos de 10–100 ms) y transcribiendo clips cortos. Separa la voz de la persona (−11 a −23 dB) del audio que suena de fondo en una bocina o celular (−25 a −45 dB): nunca usar esos tramos.
3. **Mostrar el PLAN TAL CUAL a la persona y no editar nada** hasta que diga "sí". Empezar con: "Esto es lo que voy a hacer con tu video, paso a paso. Revísalo y dime si algo está mal antes de que lo arme." El plan lleva: qué partes se usan (tiempo · qué dice · qué se ve · animación · texto en pantalla), retomas que se quitan, duración contra el máximo, música, cada paso de la edición y una lista de **posibles errores** que la persona debe revisar (voz que podría ser de otra persona, palabras que podrían quedar cortadas, licencia de música…). En el editor de testimoniales lo genera `editar.py <p> plan` (PLAN.md). Corregir fila por fila.
4. **Cortar** (`metodo_corte.py` o el `cortar.py` de la plantilla de anuncios), **preparar** (`preparar.py`), armar `cine.json`.
5. **Revisar con stills** (`render.mjs --stills`) con la zona segura encima (`estilo-cine/zona_segura.png`) antes del render completo.
6. **Render** y **verificar**: transcribir el audio final por tramos (con música encima Whisper inventa cosas como "Suscríbete": compara contra la energía), medir volumen (−14 LUFS), ver una hoja de cuadros. Guardar como `Video editado - <nombre>.mp4` en la carpeta del video; si viene del Escritorio o de iCloud, en `~/Movies/` (iCloud traba la reproducción).
7. **Revisión final cuadro por cuadro (siempre, con cualquier editor):** con el video TERMINADO corre
   `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta_del_proyecto> "<video final>"`.
   Lee con Vision todos los fotogramas (cara y texto real en pantalla) y busca texto sobre la cara, fuera de la zona segura, subtítulos que no se ven, destellos de un cuadro, cuadros negros, imagen congelada y audio que satura; deja hojas de contacto en `<carpeta>/revision_final/` con marco rojo en los cuadros con problema. **Abre y mira las hojas** antes de entregar. Las pantallas negras a propósito (estilo Golpe) salen como falso positivo. En el editor de testimoniales ya viene dentro de `editar.py … terminar`, y solo entrega si todo pasó.
8. **Mirar el video terminado cada medio segundo** (`select='not(mod(n\,12))'` en hojas de 7×3): una hoja cada 1.5 s no alcanza, y hay errores que ninguna revisión automática ve (ver "Lección aprendida" abajo).
9. Si algo no se pudo verificar (por ejemplo, no se vio de corrido), decirlo.

## Reglas de corte y audio (en TODOS los editores)
- **Palabras cortadas: doble revisión siempre.** Cada inicio y final se lleva al silencio real; cada corte se transcribe exacto y otra vez con medio segundo de más (si cambia la primera o la última palabra, el corte se la come). Al final, transcribir cada unión del video armado con el audio limpio (sin música).
- **Pausas:** no cortar pausas naturales de menos de ~0.6 s dentro de una frase: cada corte ahí es un jump cut y se ve peor que la pausa. Solo se quitan silencios largos o tramos de otra persona.

### Cortes que quedan bien (receta probada)
Está completa en `plantillas/anuncio-por-frases/`; cópiala como base para cualquier anuncio o reel a cámara grabado frase por frase:
1. **Tomas completas, nunca remiendos a media frase.** Si la persona se trabó («fue… fue»), usar otra toma completa de esa frase aunque se pierda un detalle; empalmar tomas distintas solo en una pausa natural (coma o punto). Inicio de tramo con ~70 ms de margen antes del ataque de la voz (medir energía en pasos de 10 ms).
2. **`metodo.json` con `"pausa": 0.6, "fps": "<fps nativo>", "ajustar_cuadros": true`** (lo escribe `cortar.py`): sin jump cuts internos, sin conversión a 23.976 y corte por número de cuadro → audio y video miden exactamente lo mismo.
3. **Un solo encuadre por video:** `caraY` = mediana real de la altura de la cara en el corte y `caraH` = 1.22 × mediana del tamaño de cara (`armar.py` los calcula). Nunca `caraY`/`caraH` por escena: cada cambio hace brincar a la persona 100–250 px.
4. **Cambio de escena pegado a un corte (< 0.3 s) arranca EN el corte** (`armar.py`): si no, se asoman 1–7 cuadros de la toma siguiente.
5. **Texto entra con la palabra que muestra** y las palabras se pasan de un corte a otro con `remapear.py` (sin volver a transcribir) + `afinar_palabras.py` (por pieza).
6. **Revisión de cortes a ojo:** `hoja_cortes.py` (cuadro de antes y de después de cada corte) además de `auditar_cortes.py` (voz en el corte, jump cuts, desfase). El detector de caras sobre el video FINAL da falsos «saltos» (manos, palabras gigantes): manda la hoja, no ese número.
- **Voz pareja:** nivelar el volumen de cada corte antes de unirlos (que no brinque entre tomas o clips) y dejar el final a −14 LUFS.
- **Volumen:** `estilo-cine/volumen.mjs` (ganancia fija + limitador). No regresar a loudnorm de una pasada: sube el ruido en las pausas. `reac_render.py` y `motor/render.mjs` todavía lo usan.
- **Voz de otra persona:** el director o quien dicta fuera de cámara suena ~6 dB más bajo: nunca usar esos tramos.
- **Final sin congelar:** el fundido empieza justo cuando la persona termina de hablar (o un poco antes) sobre imagen real; nunca un cuadro congelado. Si el clip termina justo en la última palabra, bajar `cola` (0.25).
- **Cambios de escena y tomas de stock:** ninguna toma cruza un cambio de plano del stock (se ve un destello); no dejar rebanadas de 2–4 cuadros de la persona entre una toma y un corte; transición visible en cada corte.
- **Video HDR (HLG/PQ, p. ej. DJI, iPhone):** convertir a Rec.709 antes de editar (`editor-testimoniales/editor/bin/sdr`) o se ve lavado. `metodo_corte.py` no lo convierte.

## Reglas de estilo (respetarlas siempre)
- **Fondo real.** No recortar a la persona ni cambiarle el fondo salvo que lo pida. Tampoco bajarla en el cuadro. El recorte (máscara) solo sirve para meter texto gigante entre el fondo y la persona.
- **La persona siempre a color**, también en insertos: aunque el formato de referencia sea blanco y negro (Editor 44), no usar `bn` ni `inserto.bn` salvo que la persona lo pida.
- **Filtro de piel sutil**: `piel.py` con valores por defecto. Cuidar que no se vea verde (no usar `eq=saturation` ni grano en canales de color). Si la toma se ve muy naranja/cálida: `colorbalance` hacia azul y `piel.py --color 0.5`. Si marca parches en la cara, `preparar.py --sin-piel`.
- **Arrancar justo cuando empieza a hablar.** Sin silencios ni miradas al celular a cuadro. Pausas largas dentro de una frase se recortan.
- **Zona segura de Instagram** (video 1080x1920): nada importante con y < 262, y > 1540, ni x > 900 desde y > 700; 42 px de margen a cada lado. Aplica a subtítulos, flechas y gráficos; revisarlo con medidas, no a ojo. **Se cumple angostando, no corriendo:** centrado en x 540 con máximo 680–720 de ancho. Mover el texto a un lado de la persona se ve chueco.
- **Nada encima de la cara:** detectar la cara en TODOS los fotogramas antes de colocar textos o gráficos (en el editor de testimoniales: `bin/caras` + `revisar_texto.py`). Si un subtítulo no cabe, partirlo en dos antes que taparla.
- **Subtítulos cortos:** ninguno dura menos de ~0.9 s en pantalla; si es más corto, aparece antes o se une al siguiente.
- **Subtítulos** palabra por palabra (línea chica + palabra grande, `*` resalte, `~` contorno). Blancos con sombra si la ropa o el fondo son oscuros (`"textoTema": "oscuro"`); texto "detrás" de la cabeza oscuro sobre pared clara.
- **Cuando menciona una herramienta**, mostrar su interfaz emulada con código (basada en capturas reales) a **pantalla completa**, con interacción (escribir, clic, generar). En escenas de interfaz no poner `cortes`.
- **Listas de herramientas**: la columna va del lado al que la persona SEÑALA (revisar cuadro por cuadro sus gestos). Solo poner lo que la persona dice.
- **Zoom**: el empuje lento tiene tope (+5 %) y se reinicia en cada corte o escena; nada de acercamientos acumulados.
- **Ritmo**: animaciones encadenadas, sin tiempo muerto (< 5 % del video quieto, pausas ≤ 0.3 s); transición visible en cada corte.
- **Música**: una canción distinta por video, que se escuche desde el segundo 0; baja cuando hablan (voz ≥ 8 dB por encima). Los efectos no deben pisar la última sílaba de una frase. Confirmar que la licencia cubra anuncios pagados si es para un cliente.
- **Imágenes con IA**: solo imágenes, nunca videos salvo que lo pidan; pedir OK antes de gastar créditos. Animar con código.
- **Referencias de otros creadores** son guía de look, no para copiar su contenido.
- **CTA**: tarjeta de comentario con la palabra clave + notificación de DM al final (`cta`, `dm`).

## Plantillas con nombre
- **Cine Pro**: reel estilo cine con la persona y su fondo real, texto palabra por palabra, escenas 3D, textura de película.
- **Cine Pro 3D**: Cine Pro + ventana "Top N" naranja con candados, un bloque 3D por herramienta e interfaz de cada herramienta a pantalla completa. Receta: `plantillas/cine-pro-3d/ESTILO.md`.
- **Formatos (61)**: Editor 1–50, Pizarra Pro y 10 "Editor N · pantalla". Son recetas, no plantillas que corren solas: cada `GUIA.md` dice qué es y cómo armarlo con los motores. Para elegir, abre primero `plantillas/formatos/GUIA-FORMATOS.md`.

## Calidad de salida: Redes (1080) o 4K
Por defecto **Redes**. Solo si la persona pide 4K: editar todo en la copia de 1080 y al final `prep4k.py` + `render.mjs --perfil 4k` (por bloques, HEVC por hardware, prioridad baja). Si la cámara no es 4K, avisar que saldrá escalado.

## Anuncios a cámara con Cine Pro: componentes y anclas
- Clips ya limpios (sin retomas): `metodo.json` con un solo tramo `[0, duración]` y `corte/words.json` copiado del `words.json` de `editor-anuncios/prepare.py` (mismo formato) → `metodo_corte.py` quita solas las pausas > 0.32 s. Muletillas de arranque («A ver,») se quitan con `quitar_tramos.py` y se vuelve a transcribir.
- `plantillas/anuncio-por-frases/armar.py` arma `cine.json` desde `voz/palabras.json` y el plan de `planes.py`: escenas por anclas de palabra (`@palabra`, `@palabra#2`, `@palabra$+0.3`, `@fin`), subtítulos por frase (nunca cierra un grupo con palabra función), `resaltar` (marcatextos con `cfg.acento`), `detras` (palabra gigante tras la cabeza), `ocultar` (palabras que carga un gráfico), `sinSub`.
- **Anclas: no distinguen mayúsculas NI acentos.** «@tú» cae en «tu», «@qué» en «que», «@El» en «el». Contar con `#n`; un `detras` con ancla fuera de su escena desaparece sin avisar. El ancla `@fin` solo es exacta: `@fines` es una palabra.
- Componentes de `cine.js`: `datos` (chip chico arriba a la izquierda, fuera de la cara), `tachados` (frases, `sello` o `lista` que se tachan), `comparacion` (dos mensajes con `candado`), visual `split` (gráfico arriba 40 % con paneles burbuja/barras/pregunta/tarjeta, persona recortada abajo; subtítulos en `y` .32 dentro del panel; admite `elementos`, `puntos`, `sinLineas`, `sinUnion`), visual `broll` (cuadros a pantalla completa), visual `editorial` (papel + kicker), visual `cierre` (tarjeta final con `cola` 2.9), visual `franja` (brutalista: titular condensado arriba, persona abajo), visual `golpe` (pantalla negra, una palabra por golpe), visual `pantalla` (color liso con rayas, textos e inserto de la persona); `chips` admite `oscuro` y sin icono; `cfg.acento` colorea el marcatextos.
- **Pizarra explicativa:** visual `pizarra` con `elementos` declarativos (texto, nodo, linea, burbuja, candado, tacha, check, cruz, icono, barra, bloques, circulo, puerta, engrane, circuito, grieta, figura, plataforma, columna, tarjeta-lista, tarjeta-video, flecha-abajo, reproductor, anillo, termo, doc, piso), cada uno con `en`/`fin`/`mueve` en segundos o anclas `@palabra`. Zona útil y 330–1200, x ≤ 900 debajo de y 700; subtítulos en .745. La persona debe estar a cuadro los primeros 3 s y más del 60 % del tiempo.
- Por escena: `capas` (elementos de pizarra sobre cualquier visual), `encuadre` {z, dx, dy}, `temaDetras`, `detrasDura`, `vig`. Por grupo: `maxTam`. En cine.json: `fuenteGrande`, `subtitulo` {fondo, color, size, unaLinea}, `limpio` (sin efectos agresivos), `caras` (encuadre medido por pieza con `bin/caras`).
- Zoom alterno por escena: `cortes` = inicio de cada escena de persona (zoomAlt 1.05–1.08).
- Cara en el tercio superior (centro y ≈ .28): nada arriba de la cabeza salvo el chip a la izquierda o la palabra `detras`; subtítulos a .72–.745; gráficos entre .50 y .70 (sobre el torso/manos).
- Render ~80 s por anuncio de 45 s; `revisar_final.py` ~2 min. `render.mjs` a veces se queda colgado al terminar (0 % de CPU, el mp4 ya está escrito): el `render.sh` de la plantilla lo cierra en cuanto el log confirma.
- `revisar_final.py` sin `pages.json` no revisa texto contra cara: medirlo con `_fotogramas.json`. Lo que va detrás de la cabeza sale como falso positivo.

**Lección aprendida:** una tanda de anuncios pasó todas las revisiones automáticas y aun así estaba mal. Fallaba: subtítulos a pedazos que nunca mostraban la frase completa, palabras que entraban fundidas, transiciones agresivas (whip, glitch, flash) que dejaban cuadros borrosos, cara de tamaño distinto en cada corte y `piel.py` marcando parches en la cara. Se corrige con subtítulo por frase (`frase: true` + `cfg.subtitulo`), `cfg.limpio`, `cfg.caras` y `preparar.py --sin-piel`. Por eso el paso 8 del flujo es obligatorio.

## Reglas para una serie de anuncios con marca
Salieron de las correcciones de un equipo de marca a una serie de seis anuncios; aplícalas desde el inicio:
- **Sincronía:** el texto en pantalla entra con la palabra que MUESTRA, nunca con la anterior. Whisper marca bien el inicio (±0.1–0.2 s; `verificar_anclas.py` lo comprueba en el audio). Ninguna palabra gigante dura < 0.9 s: si la escena se acaba, mover el inicio de la escena siguiente a un corte natural.
- **Sin tiempo muerto en pantallas/pizarras:** la escena empieza cuando entra su primer elemento (partir la frase si hace falta); nada de 1–2 s de fondo vacío esperando la palabra.
- **Colores que se vean bien:** el oro plano se ve caqui. `lineaTitular` y `gigantes` aceptan `degradado` [arriba→abajo] (oro metálico `#F8E6B8→#DDB46B→#A9782F`); `pantalla.foco` = foco radial detrás del texto; `termo` acepta `c1`/`c2`.
- `cortar.py` acepta tramos `[a, b, 0]` exactos (sin margen) para quitar una palabra repetida pegada («fue… fue»).
- Escritorio 3D y póster de revista sin generar video: `escritorio()` y `poster()` en `planes.py` de la plantilla.
- **Color de la serie:** `color_medir.py` + `color_serie.py <clave>` sobre el material limpio (`cuadros_orig/` → `cuadros/`, antes de rotular). Por pieza: piel al tono objetivo (menos rojo/magenta), cara a la misma exposición, balance de blancos solo en lo neutro, −5 % de saturación.
- **Palabra detrás de la cabeza:** serif itálica bold (`fonts/playfair-bold-italic.woff2`, `peso: 400` porque la fuente ya es bold), mayúsculas y minúsculas, crema `#F6EFE4` (dorado claro `#F2D58E` la clave) con `sombra`, y **arriba de la cabeza** (≥ ⅔ fuera): `y` = coronilla − 40.
- **Nada en mayúsculas completas:** etiquetas, tarjetas, titulares y pasos en mayúsculas y minúsculas.
- **Subtítulos:** 2–4 palabras en una sola línea (`subtitulo.unaLinea` + `trozos()` en `armar.py`: corta en comas, nunca tras «de/la/que/mi…»).
- **Etiquetas apiladas o torcidas → `tachados.estilo: 'lista'`:** tarjeta clara con renglones alineados que entran uno por uno, sin encimarse, arriba del subtítulo.
- **Tarjeta que dice la frase → sin subtítulo** (`sinSub` u `ocultar`). Texto claro sobre fondo claro: blanco con sombra suave, no dorado.
- **La imagen debe contar la palabra:** «incendio» = imagen del incendio, y la caja vacía hasta «sin nada».

## Seguridad
- Las llaves (ElevenLabs, OpenAI, Higgsfield) viven en el **Llavero de macOS** o en variables de entorno, nunca en archivos ni en el chat.
- Nunca publicar ni mandar mensajes en redes sin que la persona confirme.
