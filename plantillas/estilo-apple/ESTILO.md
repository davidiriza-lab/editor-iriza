# Estilo Apple — desglose de la referencia

Referencia: `referencia/original.mp4` (copia de `~/Downloads/Ejemplo estilo apple.mp4`)
· 1080×1920, 30 fps, 7.5 s (225 cuadros) · cuadros sueltos en `referencia/cuadros/` · hojas de contacto numeradas en `referencia/hojas/`.

## Qué es el video (el formato)

No es una animación a pantalla completa: es **un celular grabando la pantalla de una MacBook** (fondo de pantalla de macOS arriba,
teclado y trackpad abajo) mientras corre un comercial falso de **AirPods Pro 3** al estilo Apple. Un solo texto fijo encima del video:
**"opus 5.5"** (sans bold blanca con sombra suave, centrada, justo sobre el teclado, ~y 1290 px). La idea que vende:
*"esto lo hizo la IA"*. Audio: una canción en tendencia (rap en inglés), sin voz en off. Plano fijo, sin cortes de cámara.

## Línea de tiempo (cuadro a cuadro)

| Cuadros | Tiempo | Qué pasa en la pantalla | Técnica |
|---|---|---|---|
| 0–2 | 0.00–0.07 | Pantalla casi negra (azul muy oscuro). | Arranque en negro. |
| 3–8 | 0.10–0.27 | Aparece un **degradado radial** desde el centro (crema → verde menta → turquesa → azul rey), desenfocado, junto con el título. | Fade-in + desenfoque que se aclara (blur → nítido) en ~0.25 s. |
| 9–38 | 0.30–1.27 | Título fijo: **"All new"** (chico, gris) sobre **"Airpods Pro 3"** (grande, gris oscuro, sans delgada). Los anillos del degradado "respiran" muy leve. | Hold ~1 s. Tipografía SF Pro Display Regular/Light, centrada. |
| 39–50 | 1.30–1.67 | Todo se apaga: el degradado se encoge a un círculo borroso y el título se desvanece con él. | Fade-out + blur + escala hacia adentro. |
| 51–59 | 1.70–1.97 | Negro. | Respiro de ~0.3 s (el único "tiempo muerto"). |
| 60 | 2.00 | Un puntito (el estuche, minúsculo) aparece al centro. | Semilla del siguiente plano. |
| 61–69 | 2.03–2.30 | El estuche **crece de golpe** desde el punto hasta tamaño protagonista y el degradado radial vuelve a florecer detrás. | Scale-up con ease-out fuerte (~0.25 s). |
| 70–76 | 2.33–2.53 | El degradado se **disuelve** a un fondo beige cálido liso; el estuche queda. | Cross-dissolve de fondo, objeto fijo. |
| 77–110 | 2.57–3.67 | El estuche **gira en 3D**: se abre la tapa, se inclina, rota casi 360°, enseña los audífonos dentro y vuelve de frente. | Rotación 3D continua con **motion blur** en los giros rápidos; se asienta con ease-out. |
| 111–112 | 3.70–3.73 | El estuche se inclina hacia atrás y sale. | Salida rápida. |
| 113–128 | 3.77–4.27 | Texto **"Rebuilt from the ground up"** se escribe **palabra por palabra**: cada palabra entra desenfocada y gris claro y se enfoca a gris oscuro (~3 cuadros por palabra). El bloque arranca arriba-izquierda y se desliza al centro mientras se escribe. | Blur-in por palabra + deriva lenta del bloque. Bold/Semibold. |
| 129–134 | 4.30–4.47 | Frase completa, centrada, quieta. | Hold corto (~0.2 s). |
| 135–139 | 4.50–4.63 | El texto se **comprime y se hace chiquito** con desenfoque horizontal. | Salida con motion blur horizontal + escala hacia abajo. |
| 140–143 | 4.67–4.77 | **Latigazo**: dos audífonos entran gigantes, muy cerca de cámara, con mucho motion blur. | Whip-in / dolly-out rápido. |
| 144–160 | 4.80–5.33 | Los dos audífonos se alejan y quedan flotando, girando lento cada uno a su ritmo. | Flotación 3D, rotación suave. |
| 161–170 | 5.37–5.67 | El audífono derecho **sale disparado hacia arriba-derecha**; el izquierdo se desliza a la izquierda. | Salida de un elemento, el otro queda como ancla. |
| 171–179 | 5.70–5.97 | Del audífono se **desprende la almohadilla** (ear tip) hacia la derecha. | Despiece / "explosión" del producto. |
| 180–186 | 6.00–6.20 | La almohadilla se **multiplica en 4 tamaños** (XS–L) en fila; debajo aparece **"Fit, finally figured out."** con el mismo blur-in. | Duplicación en cascada + texto blur-in. |
| 187–206 | 6.23–6.87 | Composición fija: audífono a la izquierda, 4 almohadillas en fila, texto debajo alineado. | Hold ~0.6 s. |
| 207–211 | 6.90–7.03 | Las almohadillas **se colapsan** de regreso hacia el audífono con blur horizontal; el texto se barre y desaparece. | Rewind / colapso con motion blur. |
| 212–224 | 7.07–7.47 | Queda un solo audífono que gira hacia cámara (empieza la siguiente escena; el video corta aquí, se siente como loop). | Corte en movimiento → invita a re-ver. |

## Principios del estilo (lo que hay que copiar)

1. **Paleta**: fondo beige/marfil cálido casi plano (real aprox. `#EFE8DC`–`#E6DCCB`, en la grabación se ve `#BEA98E`)
   + un **degradado radial** solo en la apertura: centro crema `#F4E3A6` → menta `#8FE0B0` → turquesa `#3FC2D0` → azul `#1E6BD6`.
   Texto gris carbón (`#3A3A3C`), subtítulo gris medio. Nada saturado fuera del degradado.
2. **Tipografía**: SF Pro Display (o Inter como respaldo). Título Regular/Light grande; frases Semibold medianas. Frases cortas,
   tipo eslogan, 3–6 palabras ("Rebuilt from the ground up", "Fit, finally figured out.").
3. **Texto palabra por palabra con blur-in**: cada palabra entra desenfocada + clara y se enfoca en ~0.1 s; salidas con
   desenfoque horizontal y encogimiento.
4. **Producto como protagonista 3D**: un objeto al centro sobre fondo vacío, girando suave; giros rápidos con motion blur;
   "despiece" del producto para explicar una característica.
5. **Ritmo**: escenas de 0.7–1.7 s, cada transición dura 4–6 cuadros y siempre es **con movimiento** (crece desde un punto,
   latigazo, colapso, barrido); casi nunca corte seco. Solo un negro de ~0.3 s entre apertura y producto.
6. **Mucho aire**: 60–70 % de la pantalla vacía; un elemento o una frase a la vez.
7. **Envoltura "hecho con IA"**: la animación se presenta en la pantalla de la Mac grabada con el celular + etiqueta fija
   ("opus 5.5"). Canción en tendencia de fondo, sin voz.

## Cómo aplicarlo a un video

Al recibir el video, confirmar cuál de las dos lecturas quiere:
- **A. Animación estilo Apple** (lo más probable): sobre su contenido (producto, oferta, idea) armar escenas con
  degradado de apertura + título, objeto/elemento central animado, frases blur-in palabra por palabra, transiciones con
  motion blur, fondo marfil. Si sale la persona hablando: recortado sobre fondo marfil, sin efectos sobre la cara.
- **B. Formato completo "lo hizo la IA"**: además, montar la animación dentro de una pantalla de MacBook (mockup o
  grabación real) con la etiqueta fija tipo "opus 5.5".

Motor sugerido: HTML/CSS animado + render a video (mismo pipeline HTML→ffmpeg de Cine Pro), con
`filter: blur()` para blur-in y motion blur simulado (varias copias semitransparentes / blur direccional).
Objetos 3D: imagen recortada del producto con rotación CSS 3D, o modelo Three.js si hay GLB.
