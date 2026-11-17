# Instrucciones para Claude: instalar Editor Iriza

Sigue estos pasos en orden. Habla con la persona en su idioma y sin tecnicismos: probablemente no programa. No instales nada sin decirle antes qué es y para qué sirve, y solo espera su respuesta donde se indica.

## 1. Revisar la computadora

```bash
uname -sm                  # debe decir: Darwin arm64
sw_vers -productVersion    # debe ser 14 o más nuevo
```

- Si no es una Mac con chip Apple (M1 o más nuevo), dile que el editor no funciona ahí (la transcripción y la detección de caras usan el chip de Apple) y detente.
- Si macOS es anterior al 14, dile que tiene que actualizar el sistema primero y detente.

## 2. Programas que hacen falta

Revisa cuáles ya tiene:

```bash
command -v brew ffmpeg node npm uv git; xcode-select -p; ls -d "/Applications/Google Chrome.app"
```

| Programa | Para qué | Cómo se instala |
|---|---|---|
| Homebrew (`brew`) | Instalar lo demás | La persona lo instala en la app Terminal con el comando de https://brew.sh (pide su contraseña de la Mac). **Espera** a que termine |
| Herramientas de Xcode | Compilar el recorte de persona y la detección de caras | `xcode-select --install` abre una ventana: la persona da clic en Instalar. **Espera** a que termine (5 a 15 minutos) |
| `ffmpeg` | Cortar y unir video y audio | `brew install ffmpeg` |
| `node` | Dibujar el video | `brew install node` |
| `uv` | Instalar Python sin tocar el de la Mac | `brew install uv` |
| Google Chrome | El render se dibuja con Chrome | `brew install --cask google-chrome`, o que lo baje de google.com/chrome |

Dile en una sola lista qué falta y pídele permiso para instalarlo. Con su "sí", instala lo que puedas tú; lo que pide contraseña o una ventana lo hace la persona. No sigas hasta que todo esté.

## 3. Bajar el editor

La carpeta por defecto es `~/editor-iriza`. Pregúntale solo si prefiere otra.

- Si la carpeta no existe: `git clone https://github.com/davidiriza-lab/editor-iriza.git ~/editor-iriza`
- Si ya existe y es este editor (`git -C ~/editor-iriza remote -v` muestra `davidiriza-lab/editor-iriza`): es una actualización. Corre `git -C ~/editor-iriza status --short`; si no hay cambios, `git -C ~/editor-iriza pull`. Si hay cambios de la persona, no los toques: dile cuáles son y pregúntale qué quiere hacer.
- Si ya existe y es otra cosa: no la toques y pregunta por otra carpeta.

## 4. Instalar

Avísale que la primera vez tarda varios minutos porque baja el modelo de transcripción (1.6 GB), y corre:

```bash
cd ~/editor-iriza && ./instalar.sh
```

- No pide contraseña ni usa `brew`. Se puede correr varias veces.
- Si dice que falta un programa, vuelve al paso 2.
- Si dice que una skill o un agente "ya existe y no lo dejó así este instalador", lo dejó intacto. Cuéntale a la persona y, solo si ella quiere la versión nueva, corre `./instalar.sh --reemplazar` (guarda la anterior en `respaldos/`).

## 5. Sus datos

Si `config/kit.json` todavía dice "Tu nombre", pregúntale su nombre y su usuario de Instagram (los dos salen en los videos) y escríbelos en `config/kit.json`. Si ya tiene sus datos, no lo toques.

## 6. Verificar

Avísale que vas a hacer un video de prueba de 17 segundos (puede tardar un par de minutos y al final se abre la carpeta con el video):

```bash
cd ~/editor-iriza && ./verificar.sh
```

- `✓` listo. `✗` falta y hace falta: arréglalo (casi siempre con `./instalar.sh`) y vuelve a verificar.
- `○` es opcional: todo lo demás funciona sin eso. Explícale en una línea para qué sirve cada uno y no lo instales salvo que lo pida:
  - **Llave de ElevenLabs**: solo para reels sin cara con voz de IA. La guarda la persona en su terminal con `./motor/clave.sh` (nunca te la pega en el chat).
  - **Referencias de los 61 formatos**: imágenes de cómo se ve cada estilo, para elegir a ojo. Son 150 MB: `git clone https://github.com/davidiriza-lab/editor-iriza-referencias.git ~/editor-iriza-referencias && ~/editor-iriza-referencias/instalar.sh ~/editor-iriza`. Sin ellas, cada formato viene descrito con palabras y medidas.
  - **imagen-gpt / Higgsfield**: fondos generados con IA. Sin ellos, los fondos se hacen con código.
  - **HEVC por hardware**: solo para exportar en 4K.
- La música no viene incluida: el editor usa las canciones que la persona le pase (con licencia para el uso que les vaya a dar) o entrega sin música si ella lo pide.

## 7. Enseñarle a usarlo

Dile que cierre y vuelva a abrir Claude Code para que cargue la skill, y que desde cualquier carpeta puede pedir, por ejemplo:

- "Edita este video con Cine Pro: /ruta/al/video.MOV"
- "Edita estos clips como anuncio: /carpeta/de/clips · sin música · máximo 40 segundos"
- "Haz un testimonial de esta entrevista: /ruta/entrevista.mp4 · máximo 60 segundos"

Explícale qué va a pasar: primero le enseñas un plan (qué partes usas, qué texto va en pantalla, cuánto dura) y no editas nada hasta que diga que sí. Termina con un resumen de qué quedó instalado, qué es opcional y dónde quedó el video de prueba.
