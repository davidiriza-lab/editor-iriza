# Editor Iriza

Pásale tu video a Claude y te regresa el reel, el anuncio o el testimonial ya editado.

Es un editor de video para Claude Code, pensado para quien graba a cámara en vertical y no quiere (o no sabe) editar: le pasas tus clips, encuentra las tomas buenas, te enseña un plan y, cuando lo apruebas, corta, subtitula, anima, mezcla el audio y revisa el resultado cuadro por cuadro antes de entregártelo. Todo corre en tu Mac: no hay generadores de video ni suscripciones de por medio.

## Instalar: pega esto en Claude Code

```
Lee https://raw.githubusercontent.com/davidiriza-lab/editor-iriza/main/INSTALAR.md
y sigue sus instrucciones al pie de la letra.
```

Claude revisa tu Mac, te dice qué falta y te pide permiso antes de instalar cada cosa, baja el editor en `~/editor-iriza`, lo instala y hace un video de prueba de 17 segundos para confirmar que todo funciona. La primera vez tarda varios minutos, casi todo en descargas. Al terminar, cierra y abre Claude Code.

Si prefieres hacerlo a mano:

```
git clone https://github.com/davidiriza-lab/editor-iriza.git ~/editor-iriza
cd ~/editor-iriza
./instalar.sh      # entorno de Python, Whisper, paquetes de Node, herramientas de imagen, la skill y el agente de Claude
./verificar.sh     # revisa todo y renderiza el video de prueba
```

## Qué necesitas

- **Una Mac con chip Apple** (M1 o más nuevo) y macOS 14 o más nuevo. La transcripción y la detección de caras usan el chip de Apple; en Windows o en una Mac con Intel no funciona.
- **[Claude Code](https://claude.com/claude-code)** con tu cuenta de Claude.
- **Programas gratuitos** que Claude te ayuda a instalar: `ffmpeg`, `node`, `uv`, las herramientas de línea de comandos de Xcode y Google Chrome.
- Unos **5 GB libres** para el editor y sus descargas, más el espacio de tus videos (cada proyecto ocupa varios GB mientras se edita; al terminar se limpia).

Nada de lo siguiente es obligatorio. Con tu propia cuenta, si lo quieres:

| Opcional | Para qué | Qué pasa si no lo tienes |
|---|---|---|
| Música propia o de un catálogo con licencia | La canción de fondo | El editor te pregunta; si dices "sin música", entrega solo con voz y efectos (los efectos de sonido sí vienen: se generan al instalar) |
| Llave de [ElevenLabs](https://elevenlabs.io) | Reels sin cara con voz de IA | Todo lo que es video a cámara funciona igual |
| [Referencias de los formatos](https://github.com/davidiriza-lab/editor-iriza-referencias) (150 MB) | Ver cómo luce cada uno de los 61 estilos antes de elegir | Cada formato viene descrito con palabras y medidas |
| [imagen-gpt](https://github.com/davidiriza-lab/claude-con-gemini-y-gpt), una llave de OpenAI o Higgsfield | Fondos generados con IA | Los fondos y las animaciones se hacen con código |

## Cómo se usa

Abre Claude Code (en cualquier carpeta) y dile qué quieres, con la ruta de tu video:

```
Edita este video con Cine Pro: /ruta/al/video.MOV
Edita estos clips como anuncio: /carpeta/de/clips · sin música · máximo 40 segundos
Haz un testimonial de esta entrevista: /ruta/entrevista.mp4 · máximo 60 segundos
Hazme un reel con las mejores partes de este video, estilo Editor 12
Cámbiale el color de los subtítulos al de mi marca y vuelve a renderizar
```

Lo que pasa después:

1. Transcribe y separa tus tomas, incluidas las repetidas y lo que dice alguien fuera de cámara.
2. Te enseña un **plan**: qué partes usa, qué texto va en pantalla, cuánto dura y qué podría salir mal. No edita nada hasta que dices que sí.
3. Corta en silencios reales, nivela la voz y prepara la imagen (HDR a Rec.709, filtro de piel sutil, un solo encuadre de la cara).
4. Arma subtítulos y gráficos amarrados a cada palabra, fuera de tu cara y dentro de la zona segura de Instagram.
5. Antes de renderizar corre una **revisión única** que bloquea la entrega si encuentra texto encima de la cara, palabras cortadas, tomas repetidas o tramos sin movimiento.
6. Renderiza a 1080×1920 (o 4K) con el audio a −14 LUFS, verifica el archivo final y un agente crítico lo mira como lo vería alguien que va pasando videos.
7. Lo que apruebas y lo que corriges se queda anotado: el siguiente video sale más a tu gusto.

## Qué trae

| Carpeta | Para qué |
|---|---|
| `estilo-cine/` | Motor principal: reels estilo cine con tu fondo real, subtítulos palabra por palabra, palabra gigante detrás de la cabeza, escenas 3D, interfaces de apps emuladas, pizarras explicativas y textura de película |
| `plantillas/anuncio-por-frases/` | Receta probada para anuncios grabados frase por frase: cortes sin saltos, un solo encuadre, color parejo y revisión de cada corte |
| `docs/componentes-anuncios.md` | Lo que hace que un anuncio no se vea soso: subtítulo "escalón", golpes de color a pantalla completa, palabras gigantes detrás de ti, pantallas animadas, fecha en movimiento y cierres tipo landing |
| `editor-testimoniales/` | Entrevista cruda → testimonial: elige las mejores partes, quita la voz del director, nivela el audio y no entrega si una revisión falla |
| `editor-anuncios/` | Anuncios con retomas, zoom a la cara, gráficos por cues y transiciones |
| `motor/` | Reels sin cara con voz de IA (ElevenLabs) |
| `plantillas/formatos/` | 61 recetas de estilo (Editor 1–50, Pizarra Pro y 10 formatos "en pantalla"), cada una con su guía |
| `estilo-cine/revisar.py`, `entrega.py`, `limpiar.py` | La revisión que bloquea, el verificador del archivo final y el limpiador que libera espacio cuando terminas |
| `estilo-cine/inserto.py`, `encima.py` | Para meter clips hechos con otra herramienta (una animación, un render 3D) como escena o como efecto encima |
| `agentes/critico-video.md` | El agente que critica el video antes de que lo veas |

Las reglas completas (cortes, audio, estilo y cada receta) están en [`CLAUDE.md`](CLAUDE.md): es lo que Claude lee antes de editar. Si quieres que edite distinto, díselo; lo anota y lo respeta en los siguientes videos.

## Si algo falla

- **Primero:** en la carpeta del editor corre `./verificar.sh --sin-render`. Lo marcado con ✗ trae a la derecha cómo arreglarlo (casi siempre `./instalar.sh`); lo marcado con ○ es opcional.
- **"Falta ffmpeg / node / uv / swiftc":** pídele a Claude "instala lo que le falta al Editor Iriza" o corre `brew install ffmpeg node uv` y `xcode-select --install`.
- **El render no arranca o se queda colgado:** revisa que Google Chrome esté instalado y cierra otros renders; el editor hace uno a la vez.
- **El video se ve lavado o gris:** viene en HDR (iPhone o DJI). El editor lo convierte solo; si lo cortaste por fuera, dile a Claude "conviértelo a Rec.709 antes de editar".
- **Subtítulos con un nombre mal escrito:** dile a Claude cómo se escribe ("se escribe Iriza, no Irisa") y vuelve a armar.
- **La Mac se queda sin espacio:** `python3 estilo-cine/limpiar.py --todo --simular` dice cuánto se libera; sin `--simular` borra lo intermedio de los videos ya terminados (nunca tus crudos ni tus finales).
- **Actualizar:** `cd ~/editor-iriza && git pull && ./instalar.sh`. No pisa tu `config/kit.json` ni lo que hayas cambiado en la skill.
- **Otra cosa:** copia el error completo y pégaselo a Claude dentro de la carpeta del editor, o abre un [issue](https://github.com/davidiriza-lab/editor-iriza/issues).

## Guía completa

https://davidiriza.com/lab/que-claude-te-edite-el-video

## Créditos y licencia

El sistema nació del paquete de edición de Saúl Martínez y lo publico con su permiso. Encima van mis cambios: la receta de anuncios por frases, componentes nuevos de `cine.js`, la pizarra explicativa y las reglas que salieron de editar anuncios reales.

Licencia MIT: úsalo, modifícalo y edita con él videos propios y de clientes. Componentes de terceros en [`AVISOS.md`](AVISOS.md).
