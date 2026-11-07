# Editor Iriza

Editor de video con Claude Code para reels, anuncios y testimoniales verticales grabados a cámara. Le pasas tus clips, encuentra las tomas buenas, te enseña un plan y, cuando lo apruebas, corta, subtitula, anima, mezcla y revisa cuadro por cuadro antes de entregar.

```
cd editor-iriza && claude
"Edita este video con Cine Pro: /ruta/al/video.MOV"
"Edita estos clips como anuncio: /carpeta/clips · sin música · máximo 40 s"
"Haz un testimonial de esta entrevista: /ruta/entrevista.mp4 · máximo 60 s"
```

## Qué trae

| Editor | Para qué |
|---|---|
| `estilo-cine/` | Motor principal: reels estilo cine con tu fondo real, subtítulos palabra por palabra, palabra gigante detrás de la cabeza, escenas 3D, interfaces de apps emuladas, pizarras explicativas y textura de película |
| `plantillas/anuncio-por-frases/` | Receta probada para anuncios grabados frase por frase: cortes sin saltos, un solo encuadre, color parejo y revisión de cada corte |
| `editor-testimoniales/` | Entrevista cruda → testimonial: elige las mejores partes, quita la voz del director, nivela el audio y no entrega si una revisión falla |
| `editor-anuncios/` | Anuncios con retomas, zoom a la cara, gráficos por cues y transiciones |
| `motor/` | Reels sin cara con voz de IA (ElevenLabs) |
| `plantillas/formatos/` | 61 recetas de estilo (Editor 1–50, Pizarra Pro y 10 formatos "en pantalla"), cada una con su guía |

Todo es código que corre en tu computadora: no hay generadores de video ni suscripciones de por medio.

## Requisitos

- Mac con chip Apple y macOS 14 o más nuevo (la detección de caras y el recorte usan Vision; Whisper corre con MLX).
- [Claude Code](https://claude.com/claude-code).
- `ffmpeg`, `node`, `uv`, las herramientas de línea de comandos de Xcode (`swiftc`) y Google Chrome.

```
brew install ffmpeg node uv
xcode-select --install
brew install --cask google-chrome
```

Opcionales, con tu propia cuenta: una llave de ElevenLabs (reels con voz de IA, se guarda en el Llavero con `./motor/clave.sh`), una de OpenAI o Higgsfield si quieres imágenes de fondo generadas.

## Instalar

```
git clone https://github.com/davidiriza-lab/editor-iriza.git
cd editor-iriza
./instalar.sh      # entorno de Python, Whisper, paquetes de Node, binarios de Vision y la skill de Claude
./verificar.sh     # revisa todo y renderiza un video de prueba de 17 s
```

`instalar.sh` no usa `brew` ni pide contraseña; se puede correr varias veces. Te deja `config/kit.json` para que pongas tu nombre y tu @usuario.

## Cómo trabaja

1. Transcribe y separa tus tomas (incluidas las repetidas y lo que dice alguien fuera de cámara).
2. Te enseña un **plan**: qué partes usa, qué texto va en pantalla, cuánto dura y qué podría salir mal. No edita nada hasta que dices que sí.
3. Corta en silencios reales, nivela la voz, prepara la imagen (HDR a Rec.709, filtro de piel sutil, encuadre de la cara).
4. Arma los subtítulos y gráficos amarrados a cada palabra, fuera de la cara y dentro de la zona segura de Instagram.
5. Renderiza a 1080×1920 (o 4K) con el audio a −14 LUFS.
6. Revisa el video terminado con Vision, cuadro por cuadro, y te deja hojas de contacto con lo que encontró.

Las reglas completas (cortes, audio, estilo y cada receta) están en [`CLAUDE.md`](CLAUDE.md): es lo que Claude lee antes de editar.

## Lo que no viene

- **Música.** Usa la tuya o la de un catálogo con licencia; `audio/efectos_basicos.py` genera efectos de sonido libres para que todo funcione desde el primer día. Ver [`audio/LEEME.md`](audio/LEEME.md).
- **Las imágenes de referencia de los formatos.** Son cuadros de videos de otros creadores; las guías describen cada look con palabras y medidas.

## Créditos y licencia

El sistema nació del paquete de edición de Saúl Martínez y lo publico con su permiso. Encima van mis cambios: la receta de anuncios por frases, componentes nuevos de `cine.js`, la pizarra explicativa y las reglas que salieron de editar anuncios reales.

Licencia MIT: úsalo, modifícalo y edita con él videos propios y de clientes. Componentes de terceros en [`AVISOS.md`](AVISOS.md).

Guía paso a paso: https://davidiriza.com/lab/editor-de-video-con-claude
