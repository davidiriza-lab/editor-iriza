# Anuncio por frases

Plantilla para anuncios y reels a cámara **grabados frase por frase** (varias tomas de cada frase, celular vertical). De los crudos saca un video con cortes sin saltos, un solo encuadre, subtítulos por frase, pantallas y pizarras al ritmo de la voz, color parejo y revisión antes de entregar. El motor es `estilo-cine/` (`cine.js` + `render.mjs`); esta carpeta solo arma los datos.

## Empezar
```
cp -R plantillas/anuncio-por-frases proyectos/<nombre>
mkdir proyectos/<nombre>/crudos           # aquí van los .MOV/.MP4 originales
cp proyectos/<nombre>/tomas.ejemplo.json proyectos/<nombre>/tomas.json
cp proyectos/<nombre>/nombres.ejemplo.txt proyectos/<nombre>/nombres.txt
```
Todos los scripts se corren **desde la raíz del repo** (`proyectos/<nombre>/render.sh k1`). Cada video es una clave (`k1`, `gancho`, `oferta`…): una entrada en `tomas.json`, una en `planes.py` y su carpeta `proyectos/<nombre>/<clave>/`.

## Flujo
1. **HDR → Rec.709** (iPhone, DJI): `convertir_sdr.sh` deja cada clip en `_sdr/`. Si el video no es HDR, `cortar.py` usa el crudo directo.
2. **Transcribir y elegir tomas**: `transcribir_todos.sh` (y `tomas_finas.py` para el detalle por pedazo) → en `tomas.json` pon por clave el `clip`, su `fps` nativo y los `tramos` `[inicio, fin]` de la mejor toma completa de cada frase. `[a, b, 0]` = corte exacto sin margen (para quitar una palabra repetida pegada).
3. **Cortar y preparar**: `preparar_cola.sh k1 k2` → corte con voz pareja, transcripción, cuadros y máscaras, caras y revisión de uniones (`<clave>/uniones.txt`). Si cambias tramos después: `recortar_cola.sh k1` (conserva las palabras con `remapear.py`).
4. **Escribir el plan** en `planes.py` (copia `PLANES['ejemplo']`): frases, escenas y anclas `@palabra#n`. `ajustar_anclas.py` y `verificar_anclas.py` afinan y comprueban en el audio dónde empieza cada palabra; `afinar_palabras.py` retranscribe por pieza.
5. **Color de la serie** (opcional): `color_medir.py <clave>` → `color_serie.py <clave> --prueba` (hoja antes/después) → sin `--prueba` para aplicarlo.
6. **Stills**: `stills.sh <clave> 1.5,4,9` → `<clave>/salida/hoja_stills.jpg`. Revisar con la zona segura antes del render.
7. **Render**: `render.sh k1 k2` → arma `cine.json`, renderiza y corre `revisar_final.py`.
8. **Revisar a ojo**: `hoja_cortes.py <clave>` (cuadro de antes y después de cada corte), `auditar_cortes.py` (voz en el corte, jump cuts, desfase) y `auditar_final.py` (salto de la cara en el video final). Mira el video terminado cada medio segundo antes de entregar.

Imágenes de fondo (escritorio, póster): `gen_img.py imagenes.json` con `OPENAI_API_KEY` en el entorno → `_img/`.

## Cortes que sí quedan bien
1. **Tomas completas, nunca remiendos a media frase.** Si la persona se trabó, usar otra toma completa de esa frase aunque se pierda un detalle; empalmar tomas distintas solo en una pausa natural (coma o punto). Inicio de tramo con ~70 ms de margen antes del ataque de la voz.
2. **Pausa 0.6 s, fps nativo y corte por cuadro** (`cortar.py` escribe `"pausa": 0.6`, `"fps"` y `"ajustar_cuadros": true`): sin jump cuts internos, sin conversión a 23.976, y audio y video miden exactamente lo mismo.
3. **Un solo encuadre por video:** `caraY` = mediana real de la altura de la cara y `caraH` = 1.22 × mediana del tamaño de cara (`armar.py` los calcula). Nunca encuadre por escena: la persona brinca 100–250 px en cada cambio.
4. **Un cambio de escena pegado a un corte (< 0.3 s) arranca en el corte** (`armar.py`); si no, se asoman 1–7 cuadros de la toma siguiente.
5. **El texto entra con la palabra que muestra.** Las palabras pasan de un corte a otro con `remapear.py` (sin volver a transcribir) y se afinan con `afinar_palabras.py`.
6. **Revisión de cortes a ojo:** `hoja_cortes.py` además de `auditar_cortes.py`. El detector de caras sobre el video final da falsos saltos (manos, palabras gigantes): manda la hoja, no ese número.
