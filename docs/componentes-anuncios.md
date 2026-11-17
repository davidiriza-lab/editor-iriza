# Componentes para anuncios: subtítulo escalón, capas de impacto, pantallas y cierres

Lo que `estilo-cine/cine.js` trae para anuncios a cámara, además de lo que ya lista `CLAUDE.md`. Todo se escribe en el `cine.json` (o en el `plan.json` que arma `estilo-cine/armar.py`) y cada tiempo puede ser un número de segundos o un ancla `@palabra`.

Las opciones exactas de cada capa están en el comentario que la encabeza en `cine.js` (busca su nombre). `node estilo-cine/render.mjs proyectos/<nombre> --validar` avisa si una clave o una opción no existe y sugiere la más parecida.

## Identidad del anuncio (raíz del cine.json)

Antes de animar, pregunta para qué producto es el anuncio y saca su identidad (colores, tipografía, botón) de su página de registro. Va en todo el video.

| Clave | Qué hace |
|---|---|
| `acento`, `acentoTexto` | Color de marcatextos, barras y botones, y el color del texto encima de ellos |
| `paleta` | Fondo de las escenas sin persona: `"seminario"` (negro con resplandor y cuadrícula del acento) o `"blanca"` (blanco con resplandor menta y azul, cuadrícula tenue). Sin `paleta`, papel marfil |
| `fuenteGrande`, `fuenteChica` | Tipografía de la línea grande y la chica: `Outfit`, `Inter`, `Barlow Italic`, `Anton`, `Bebas Neue`, `Oswald`, `League Gothic`, `Playfair Bold Italic`… (lista `FUENTES` en `cine.js`) |
| `pop` | Subtítulo palabra por palabra con rebote: `{size, color, activo, borde, clave: {fondo, color}, maxw}` |
| `pop.modo: "escalon"` | Línea chica blanca arriba y palabra grande abajo en Barlow Condensed Black Italic; la palabra clave va sobre una barra inclinada de color (`pop.clave.fondo`) y la palabra que se está diciendo se pinta de `pop.activo`. Grupos con `tinta: true` van en negro (fondos claros) |
| `apretado` | `{junta: .03, juntaResalte: .2}` pega la línea chica a la palabra grande |
| `suave` | `{blur, barrido, rgb, grano, vig}`: transiciones con movimiento pero sin glitch ni destellos (probado: `blur .30`, `barrido .5`). `limpio` las aplana todas |
| `imagenes` | Mapa nombre → archivo (logo, fotos de caras) que usan los cierres y las tarjetas |

Por grupo de texto: `sombra: true`, `etiqueta: {fondo, color, size, peso, fuente, resaltar, unaLinea}` (subtítulo en etiqueta solo en ese grupo: sirve cuando la cara llena el cuadro y el texto cae sobre ropa clara) y `estrecho`.

## Sobre la toma (overlays de escena)

| Clave de la escena | Qué dibuja |
|---|---|
| `titulares` + `veloArriba {h, a}` | Titulares sobre cualquier toma, con un degradado oscuro detrás solo mientras hay titular. `anim: "mascara"` los sube palabra por palabra y los subraya con el acento |
| `explica {tipo, en, fin, titulo…}` | Animación explicativa en un panel esmerilado sobre la toma. Tipos: `pastel`, `chat`, `personas`, `barras`, `contador`, `red`, `engranes`, `lista`. Los subtítulos siguen encima |
| `interruptores {y, titulo, items: [{t, en, on}]}` | Tarjeta de ajustes tipo iPhone con filas que se encienden cuando se dicen |
| `logoImg {img, y, w, banda}` | Logo grande (clave de `imagenes`); `banda` le pone una franja blanca para que no quede sobre el video |
| `cap {num, t}` | Capítulo 01 / 02 / 03 arriba, dentro de la zona segura |
| `datos` | Chip de dato; acepta `fuente`, `peso`, `tam`, `borde`, `fondo`, `radio` |
| `fechaHero {en, logo, jueves, hora, linea, gratis, dia, horaTexto, zona, nombre, caras, carasTexto}` | Pantalla de fecha en movimiento: logo que se revela, celular "EN VIVO", el día (`dia`), la hora en una barra con brillo (`horaTexto`, `zona`), píldoras "En línea" y "Gratis" que se encienden en su palabra y caras con un texto (`carasTexto`). `jueves`, `hora`, `linea` y `gratis` son los tiempos en que se dice cada cosa |

## Sistema «impacto»: capas `imp`, golpes y pantallas

Para que un anuncio no se vea soso: una metáfora física en el gancho, uno o dos golpes a pantalla completa con el golpe de la música, palabras gigantes detrás de la persona y cortes de 2 a 3 s con cosas reconocibles. Las capas necesitan el recorte de la persona (`preparar.py`), `caras` por pieza (`editor-testimoniales/editor/bin/caras`) y la cara un poco más abajo (`caraY .42`).

**Detrás de la persona** (entre su fondo real y su recorte), dentro de `escena.imp`:

- `gigantes [{t, en, fin, y, size, extruido | contorno | brillo, tacha}]`: palabras gigantes que golpean y se pueden tachar.
- `arco {pal: [{t, en, color}]}`: texto en arco alrededor de la cabeza; cada palabra aparece cuando se dice.
- `iconos {en, items: [{tipo: reloj | feliz | familia}]}`, `grafica` (ventas que suben y se quedan planas), `tiendas`, `reloj {de, a}` (la hora corre del amanecer a la noche), `redes` (íconos en órbita), `chip` (chip de IA con circuitos), `caras {fotos, pos, numero, enNum}`, `billetes {ventas}`, `cuenta {a, etiqueta}`, `odometro {t, enEdif}`, `logosFila {logos: [{n, en}]}`, `flechas {items: [{t, x, alto}]}`.

**Delante de la persona**, dentro de `escena.imp`:

- `jaula {en, tiembla, rompe}`: barrotes que caen, tiemblan y se rompen.
- `silueta {en, fin, color, lineas}`: la persona rellena de color con un signo gigante; el fondo se va a negro.
- `drop {en, fin, color, lineas, escala}`: golpe de color con rayos, palabras extruidas y la persona recortada encima. Admite `slots` (casillas vacías) y `boleto {en, sello, kicker, titulo, fecha}` (un pase que entra volando y recibe su sello).
- `precio {de, a, x, y}` (etiqueta que sube), `saldo {de, a, y}` (saldo que baja a rojo), `tono` (luz de día a noche), `foco {lineas}` (reflector sobre la persona con el texto iluminado), `nombre {t, sub}` (cintillo con el nombre), `boton {en, tap, y, t, color, colorTexto, flecha}` (botón que se presiona).
- `golpes [{en, k}]`: sacude la cámara en cada golpe.

**Cortes a pantalla completa**: `escena.pant = {tipo, en…}` con `competencia` (tu celular sin mensajes contra el de ellos), `mercado`, `celulares`, `negocio` (se llena y cae un sello), `procesos` (tablero que se palomea: `filas [{t, en, dato, cuenta}]`) y `antesHoy {antes, hoyT, nombre, hoy}`.

Reglas que salieron de corregir anuncios reales:

- Uno o dos `drop` por anuncio, no más; el resto del tiempo manda la toma real a pantalla completa con textos encima.
- Cada animación lleva sonido (`sfx`) y los efectos no pisan la última sílaba de una frase.
- El texto dentro de cajas, celulares o tarjetas se mide con `envolver()` / `fuenteQueCabe()`; revísalo en stills a resolución completa.
- Un reflector (`foco`) sobre una toma abierta lleva el texto a la altura del pecho (y ≥ 1000) y angosto.
- Los recortes (`drop`, `silueta`) se ven rotos si la toma es abierta y hay otra persona u objetos delante: ahí usa `foco` sobre la toma real.
- En una campaña, cada anuncio cambia de color de acento, de metáforas y de canción.
- Música: `musica {archivo, golpe, drop, silencio}`; con `golpe` (el segundo de la canción donde pega) el armador calcula `desde` para que caiga en el ancla `drop`, con un silencio corto antes.

## Cierres (última escena)

- Visual `cierreOscuro`: tarjeta final tipo portada de landing oscura. `cierre {logo, kicker, titulo, chips, cta, fuente}`: logo arriba, titular con `{palabras}` en acento y subrayado luminoso, chips por filas y botón píldora (máximo 720 px de ancho para no entrar a la columna de Instagram).
- Visual `cierreClaro`: lo mismo sobre blanco. `cierre {logo, hl, kicker, titulo, chips: [[{t, tipo}]], cta}`; `hl` es un segundo logo con la leyenda "Presentado por".
- Visual `splitClaro`: panel claro arriba (`panel`, fracción de la altura) y la toma real abajo (`foco` = centro vertical de la toma).
- Visual `cierre` (el de siempre): tarjeta final con `cola` 2.9.

## Antes de pautar en Meta

Ni la voz ni el texto pueden afirmar o insinuar un atributo personal de quien ve el anuncio (origen, situación financiera, salud), prometer ingresos ni nombrar celebridades o marcas ajenas. Hablarle a un oficio sí se puede. Lo que dice la voz cuenta igual que el texto: se corta la frase, no solo el letrero. Una ironía en la portada va como pregunta, no como afirmación.
