# Editor de testimoniales

Plantilla para convertir una entrevista cruda en un testimonial emotivo para vender un programa o servicio: mejores partes, subtítulos de testimonial (línea chica + palabra gigante), transición en cada corte (o sin zoom: `sin_zoom`), modo vertical para anuncios, música de
Epidemic Sound con ducking, y subtítulos para las tomas de stock que se agregan después.

Dos acomodos probados: texto a la derecha con tarjeta de Instagram y panel con el número del gancho, o texto a la
izquierda con degradado (`vineta`) cuando el fondo tiene un logo o letras.

```
editor/        scripts + overlay.html + fuentes + sfx   (.venv con OpenCV 4, node_modules con playwright-core)
proyectos/<n>/ un testimonial por carpeta
```

## Flujo (un solo comando, con paradas para la persona)

Todo se corre desde `editor/`. Antes de empezar, preguntarle a la persona:
- **Música:** una carpeta con canciones o un MCP de música conectado (p. ej. Epidemic Sound). Sin eso no se entrega (o `"sin_musica": true`).
- **Duración máxima** del video (`duracion_max`) y si quiere **Redes 1080** (por defecto) o 4K.
- **Nombres propios** que Whisper escribe mal (`vocabulario`).

| Paso | Comando | Qué hace |
|---|---|---|
| 1 | `.venv/bin/python transcribir.py <video> ../proyectos/<n> "Nombres, Marcas"` | Transcribe **por pedazos** (separados por silencios) con su volumen: tomas repetidas a la vista y `← ¿director?` en lo que suena fuera de cámara |
| — | *(Claude)* | Propone las partes con minuto/segundo → `proyecto.json` → `cortes` |
| 2 | `.venv/bin/python editar.py ../proyectos/<n> plan` | Revisa cada corte (bordes, pausas > `pausa_max`, **doble transcripción** de palabras cortadas, volumen/director) y escribe **PLAN.md** |
| — | *(Claude)* | **Muestra el PLAN TAL CUAL a la persona** y espera su "sí" o sus correcciones |
| 3 | `.venv/bin/python editar.py ../proyectos/<n> armar` | Aplica los cortes y arma: HDR → Rec.709, horizontal → vertical siguiendo la cara, voz pareja entre cortes, tomas de stock (`broll_auto`), flecha en "clic", cara en todos los fotogramas |
| — | *(Claude)* | Escribe `pages.txt` con `corte.txt` |
| 4 | `.venv/bin/python editar.py ../proyectos/<n> terminar` | Subtítulos (mín. `min_pagina` en pantalla) → acomodo fuera de la cara y dentro de la zona segura de IG (parte frases que no caben) → contraste → revisión de cortes y stock → render → mezcla a −14 LUFS → **doble revisión del audio** → copia verificada a `salida` |
| — | `node render.mjs ../proyectos/<n> stills 2,8,15` | Cuadros de prueba (verlos antes de entregar) |
| 5 | `.venv/bin/python mezcla.py ../proyectos/<n> [vol] [duck]` | Solo rehace el audio. "Súbele a la música" → subir `vol` |
| 6 | `v1.py` / `render.mjs <p> v1` | Subtítulos sobre las tomas de stock que la persona metió en su versión (ver abajo) |

Cada script también se puede correr suelto: `cortes.py`, `armar.py`, `alinear.py`, `render.mjs <p> layout`,
`revisar_texto.py`, `partir.py`, `contraste.py`, `revisar_cortes.py`, `revisar_audio.py`, `stock.py <video_stock> --ver`.

### Al trabajar con este editor
- **Elegir partes:** la persona a cámara suena más fuerte que el director (marcado `← ¿director?`); con retomas, la buena suele ser la última y más fuerte.
- **Si `terminar` se detiene:** con texto encima de la cara o fuera de la zona segura parte frases solo; si no puede, acortar `pages.txt`. Con una toma de stock que cruza un cambio de plano, revisar `broll`. Con una unión que se come una palabra o un subtítulo distinto a lo que se oye, corregir el corte o `pages.txt`.
- **Antes de decir que quedó:** mirar `revision_final/hoja_*.jpg` (marco rojo = problema) y sacar `render.mjs <p> stills t1,t2,…` con 6–10 tiempos que incluyan cortes, tomas de stock y CTA. Verlos.
- **Al entregar:** decir en corto dónde quedó el video, duración, volumen, qué se revisó y cualquier aviso que quedó (p. ej. licencia de música).
- **Videos de otros editores:** `revisar_final.py <carpeta> "<video>"` también funciona sin `pages.json`.

### Qué revisa solo (y por qué)
- **Palabras cortadas:** cada borde se mueve al silencio real; cada corte se transcribe exacto y con medio segundo de más (antes de armar) y cada unión se vuelve a transcribir en el armado (después).
- **Pausas:** ninguna dura más de `pausa_max` (0.35 s). Los cortes en `intactos` no se tocan (silencios a propósito: silla vacía, alguien que se sienta).
- **Voz pareja:** cada corte se nivela a la mediana de todos; el final queda a `lufs` (−14).
- **Texto:** nunca encima de la cara (Vision en todos los fotogramas, `bin/caras`), dentro de la zona segura de Instagram (x 42–900, y 262–1540), sin pisar la flecha; palabras gigantes del mismo tamaño; fondo claro → sombra fuerte.
- **Cambios de escena:** las tomas de stock nunca cruzan un cambio de plano (`stock.py` analiza el stock cuadro por cuadro, incluso pantalla dividida) ni dejan rebanadas de la persona; cada corte visible lleva transición.
- **Final:** imagen real después de la última palabra y fundido que empieza justo antes de que termine de hablar (sin cuadro congelado).

## pages.txt

Una frase por renglón; las líneas de la frase se separan con ` / `.

```
s: Mi marca personal / B: ha crecido / i: exponencialmente
s: Hoy mi negocio es una / s: [marca registrada] #card
s: Estoy por cerrar un proyecto de / B: $800 mil pesos / s: [con alguien del grupo] #panel
s: Y@102.70 fui@103.06 muy@103.60 valiente@103.78 / B: Fuiste@104.32 muy@104.52 valiente,@104.66 Sofía@105.14
```

- `s:` línea chica (Helvetica) · `B:` palabras clave gigantes (League Gothic) · `i:` itálica serif (Instrument Serif)
- `[…]` caja terracota que barre · `{…}` píldora terracota
- `palabra@seg` fuerza el tiempo (segundos del armado) cuando Whisper fusiona o se salta frases
- `#panel` panel claro a pantalla completa (para el número/resultado del gancho) · `#card` tarjeta de perfil (`proyecto.json → tarjeta`)
- Corregir lo que Whisper escribe mal: nombres, apellidos y marcas.
- **Legibilidad:** renglones `s:` cortos (≤ 22 letras si el texto va a la izquierda, ≤ 30 a la derecha), 2–4 renglones por frase, un `B:` por frase. Si un renglón deja una palabra sola, reacomodar.

## proyecto.json

| Campo | Uso |
|---|---|
| `fuente`, `cortes` | Video crudo y `[[inicio, fin], …]` en el orden del armado |
| `lado` | `auto` (opuesto a la cara), `derecha`, `izquierda` |
| `centro_y` | Altura del bloque de texto (p. ej. 610 para quedar bajo un logo) |
| `vineta` | Degradado oscuro fijo del lado del texto (fondos con logo o texto) |
| `tam_chica` | Tamaño de la línea chica (56 por defecto; 54 si el espacio es angosto) |
| `cola` | Segundos de imagen real tras la última palabra (0.6) |
| `vertical` | `true` = 1080×1920 (Reels/TikTok) con zona segura de Instagram |
| `vocabulario` | Nombres propios para Whisper: `"el mentor, la empresa del cliente"` |
| `intactos` | Índices de cortes cuyas pausas no se recortan |
| `broll_auto` | `{"fuente": "stock.mp4", "despues_de": "Apellido", "n": 8, "dur": 0.26}` (o `"en": segundos`) |
| `flecha` | `{}` = flecha hacia abajo en la palabra "clic" (o `{"en": s, "fijo": true}`) |
| `musica` | Archivo o **carpeta** (elige una canción no usada); `musica_desde` para fijar el arranque; `sin_musica` |
| `duracion_max`, `pausa_max`, `min_pagina`, `lufs`, `transicion`, `zona_segura` | Ver `editor/plantilla.json` (valores por defecto) |
| `volumen_musica`, `ducking` | Volumen de la música y cuánto baja cuando hablan (0.39 / 0.6) |
| `sin_transicion` | Cortes sin golpe de zoom (los tapados por `#panel` se omiten solos) |
| `tarjeta` | `{handle, nombre, publicaciones, seguidores, avatar}` para `#card` |
| `salida` | Nombre del video final |

## Música (carpeta o MCP)

Opción A — **carpeta:** `"musica": "/ruta/carpeta"` y `mezcla.py` elige una canción distinta por proyecto (anota cuál en `proyectos/_musica_usada.json`).
Opción B — **MCP** (p. ej. Epidemic Sound):

Lo hace Claude con el MCP `epidemic-sound`: analizar la música del video de referencia (tempo/espectro), `SearchRecordings`
(p. ej. "emotional inspiring piano cinematic", sin voz), comparar curvas de energía para que el clímax caiga en la parte
más emotiva, `EditRecording` a la duración del armado + ~2 s, `DownloadRecordingEdit` → `proyectos/<n>/musica.wav`.

## v1.json (tomas de stock)

`v1.py` deja todas las frases afectadas en `"abajo"` (subtítulo normal centrado con velo oscuro). Revisar `tomas_*.jpg`:
- Toma con un lado limpio y oscuro, sin caras → `"modos": {"9": "derecha"}` y `"izquierdas": {"9": 1300}` (estilo grande).
- Animación o gráfico con texto propio → `"omitir"`.
- `desfases` y `ventanas` vienen calculados; los bordes caen en los cortes de la persona. Revisar con stills en los bordes.
