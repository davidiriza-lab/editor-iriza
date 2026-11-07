# Cine Pro 3D

Plantilla de edición de reels, creada el 22 oct 2026 a partir de la réplica viral "Top 5 herramientas de IA" (C8251).

Es **Cine Pro** (su fondo real, filtro de piel C8253, subtítulos palabra por palabra, textura de película) **más** los gráficos de la referencia (`CONTENIDO/Replica viral/Top/Referencia.mp4`):

1. **Intro con ventana "Top N"**: en la primera frase ("las top 5…") cae una barra naranja desde arriba, se abre en una ventana naranja brillante, se escribe el título y aparecen los candados uno por uno. Detrás de él hay una rejilla naranja con triángulos dorados, entre su fondo real y su silueta.
2. **Presentación 3D de cada herramienta**: un quemado de luz naranja lleva a un fondo oscuro con motas y triángulos dorados. Un bloque 3D (Three.js) con el logo en blanco sube desde abajo apagado, se enciende en naranja, se queda girando poquito y aparece el nombre debajo. Si son dos herramientas, sube un bloque y el segundo entra cuando la nombra.
3. **Interfaz a pantalla completa** de cada herramienta, emulada en código a partir de capturas reales: se escribe, se da clic y se genera mientras él lo explica.
4. **La persona a cuadro con su fondo real** entre herramientas: apps tachadas pixeleadas, cronómetro, etc.
5. **Cierre**: vuelve la ventana Top N con todas las herramientas desbloqueadas, luego el CTA con palabra clave y la notificación de DM.

Cuadros: `cuadros_intro.png`, `cuadros_herramientas.png`, `cuadros_interfaces.png`, `cuadros_persona.png`. Ejemplo completo: `Ejemplo Cine Pro 3D (Top 5).mp4` (84 s).

## Receta (motor `estilo-cine`)

1. **Corte**: `metodo_corte.py` con `metodo.json` (solo cámara: `recorte.vertical`, tramos en orden; ver `metodo_base.json`). Luego `segmentar` (máscaras Vision), cuadros JPG y `piel.py` (valores por defecto = filtro C8253).
2. **Verificar retomas** con clips cortos y energía del audio, no solo con Whisper. En C8251 había cuatro tropiezos escondidos: "utilizando *de* inteligencia", "puedes *hacer* cambiar", una frase repetida y "y la quinta son…" repetido.
   - Para quitarlos después de tener cuadros y máscaras: `python3 estilo-cine/quitar_tramos.py proyectos/<n> a-b c-d …`. Ajusta a cuadros completos, renumera cuadros, máscaras y `cuadros_pro`, corta el audio con microfundidos y deja respaldo.
   - Después de cortar, volver a transcribir el audio y reconstruir las escenas.
3. **cine.json** (base: `cine_base.json`):
   - `persona: {fondo:"real", bajar:0, cuadros:"cuadros_pro", n:<cuadros>, zoomAlt:1.05}`.
   - `top5: {veces:[[inicio_intro, fin_intro], [inicio_recap, fin_recap]], slots:[{en, logo}…]}`.
   - Escena `{"visual":"icono3d","trans":"quemado","icono3d":{"nombre":"NotebookLM","logos":[{"n":"notebooklm","en":t}]}}`. Para dos herramientas: `"nombre":"HeyGen y\nElevenLabs"` y dos `logos`.
   - Escena `{"visual":"interfaz","trans":"whip","ui":{tipo,…tiempos}}`. Tipos: `notebooklm` (youtube, pregunta, respuesta, audio, pdf), `higgsfield` (escribe, generar, referencia, listos[4]), `claudecode` (claude, pedido, respuesta, codex), `napkin` (selecciona, rayo, diagrama), `heygen` (sube, creando, listo), `elevenlabs` (escribe, generar). Subtítulos en y≈.775.
   - Herramienta nueva: agregar `uiX(U,t)` en cine.js (copiar una existente, basada en capturas) y su modo de glifo en `GLIFO` (claro/oscuro/alfa/brillante/codigo).
   - Logos en `proyectos/<n>/logos/*.png` (favicon de Google sz=256 o `/icon.png` del sitio) declarados en `logos`.
   - `cortes`: solo los saltos de cámara VISIBLES dentro de escenas de persona. Medirlos con la diferencia entre cuadros consecutivos; nunca poner cortes dentro de interfaces.
4. **Render**: `node estilo-cine/render.mjs proyectos/<n> --stills …` para revisar, luego completo. La salida va a la carpeta del video como `Video editado - <nombre>.mp4`.

## Reglas que no se rompen
- Nunca recortarlo ni cambiarle el fondo (se ve "chafa"). Tampoco bajarlo en el cuadro.
- Empezar justo cuando empieza a hablar. Sin silencios a cuadro.
- Las interfaces van a pantalla completa, no como tarjeta encima de él.
- Sin zoom acumulado: el empuje lento de cámara se mide desde el último corte o inicio de escena y tiene tope de +5 %. Ya está corregido en el motor.
- Una canción distinta por video, audible desde el segundo 0. Mezcla a −14 LUFS.
- Primero la escaleta; editar solo cuando la persona la apruebe.
- Higgsfield: solo imágenes, salvo que él pida otra cosa.
