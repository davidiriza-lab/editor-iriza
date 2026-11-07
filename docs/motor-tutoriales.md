# videos-voz-ia

Hace reels verticales tipo tutorial *faceless*, con la voz de IA de ElevenLabs "Fernando Martínez" (`dlGxemPxFMTY7iXagmOj`).
Es un motor propio que no depende del editor de anuncios. La guía visual del formato está en `editor-anuncios/referencias/ref14/FORMATO.md`.

## Seguridad
- La API key de ElevenLabs vive en el **Llavero de macOS** (servicio `videos-voz-ia.elevenlabs`) y nunca en archivos.
- `./video clave` la cambia (la pide sin mostrarla), `./video clave --ver` confirma que existe y `./video clave --borrar` la elimina.
- La carpeta tiene permisos solo para tu usuario. `.gitignore` excluye audios, salidas y cualquier `.env`.

## Uso
```
./video nuevo mi-video              # crea proyectos/mi-video con un guion de ejemplo
#   edita proyectos/mi-video/guion.json y pon capturas en proyectos/mi-video/capturas/
./video mi-video                    # voz + video → proyectos/mi-video/salida/video.mp4
./video voz mi-video                # solo la voz (si el texto no cambió, no gasta créditos)
./video render mi-video --stills 2,8.5   # cuadros sueltos para revisar
./video render mi-video --hasta 10       # solo los primeros 10 s
./video transcribir <archivo|link>  # transcribe un video (Whisper) → transcripciones/
```

## Logos e imágenes
```
./video logo chatgpt claude gemini instagram whatsapp   # varios a la vez
./video logo --url <link de imagen> <nombre>            # cualquier imagen → PNG
```
| Sale en | Qué es | Fuente |
|---|---|---|
| `assets/iconos/<marca>.png` | ícono oficial de la app, 1024 px, con su fondo | App Store (API pública de Apple) |
| `assets/logos/<marca>.png` y `<marca>_blanco.png` | logo solo, sin fondo, en color de marca y en blanco | Simple Icons; si no lo tiene, se recorta del ícono quitándole el fondo |
| `assets/imagenes/<nombre>.png` | cualquier imagen de un link (svg, webp, jpg, avif…) convertida a PNG con transparencia | el link que pases |

- Cada descarga queda anotada en `assets/logos.json` (de qué app y qué fuente salió). `assets/muestrario.png` muestra todo para revisarlo.
- Las marcas comunes ya tienen su búsqueda afinada (`ALIAS` en `motor/logos.mjs`): IA, redes, apps de mensajería, herramientas.
- En el guion: `{claude}` o `"img": "claude"` usan el ícono de app; `"img": "logos/claude_blanco"` usa el logo sin fondo.

## guion.json
Una lista de `pantallas`. Cada una tiene la `voz` que se dice mientras está en pantalla. La pantalla cambia cuando la voz empieza su primera palabra.

| tipo | qué muestra | campos |
|---|---|---|
| `gancho` | texto grande que se arma palabra por palabra | `lineas`: `"**palabra**"` = línea grande; `{icono@Palabra}` = ícono que aparece cuando se dice esa palabra; `{📩}` = emoji |
| `texto` | solo la etiqueta (p. ej. "Paso uno") | — |
| `logo` | ícono de app que entra volando con estela, con flecha | `img`: nombre del ícono (busca en `proyectos/x/iconos/` y luego en `assets/iconos/`) |
| `captura` | captura centrada con recuadro rojo y flecha que se dibuja | `img`, `caja: [x, y, ancho, alto]` en fracciones de la imagen (0–1), opcionales `ancho` (fracción de pantalla) y `entrada: corte/zoom/estela` |
| `scroll` | captura larga que se desplaza (chat, documento) | `img`, `mover: continuo/saltos`, `ancho` |
| `portada` | portada del lead magnet con CTA grande | `img`, `cta: "Comenta “Bot”"`, `cta_en`: palabra de la voz en la que aparece |

Otros campos: `transicion: "luz"` fuerza el destello azul (sale solo después del gancho) y `flecha: false` quita la flecha.
La etiqueta de 1–3 palabras encima de la tarjeta se genera sola a partir de la voz.

## Ajustes (`config.json`)
- Voz: modelo, estabilidad y velocidad (`speed`).
- Video: 1080×1920 a 30 fps, con una cola de 0.5 s al final.
- Audio: −14 LUFS. Para usar música, pon `musica` con la ruta a un mp3 (por ejemplo en `assets/musica/`); se mezcla 11 dB debajo de la voz.

## Cómo funciona
`motor/voz.py` llama a ElevenLabs (`with-timestamps`) para obtener el audio y el tiempo exacto de cada palabra.
`motor/render.mjs` calcula la línea de tiempo, dibuja cada cuadro con `motor/plantilla.html` en Chrome sin ventana y lo codifica con ffmpeg. Un video de 37 s tarda unos 50 s.
