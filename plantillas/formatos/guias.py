"""Escribe una GUIA.md por formato (para que cualquier Claude Code entienda qué es y cómo hacerlo) y el índice GUIA-FORMATOS.md.

Uso:  python3 guias.py          (lee formatos.json + recetas.json; se vuelve a correr cuando cambie algo)
"""
import json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(AQUI, "formatos.json"))); F = D["familias"]; E = D["editores"]
R = {k: v for k, v in json.load(open(os.path.join(AQUI, "recetas.json"))).items() if not k.startswith("_")}

carpeta = lambda e: e.get("carpeta_nombre") or ("pizarra-pro" if e["n"] == "pizarra" else f"editor-{int(e['n']):02d}")
titulo = lambda e: f"{e['nombre']} · {e['apodo']}"
por_n = {str(e["n"]): e for e in E}
ritmo_txt = lambda r: "muy rápido" if r > 1 else "rápido" if r > .5 else "tranquilo" if r > .15 else "casi un solo plano"

def guia(e):
    fam = F[e["familia"]]; rec = R.get(e["familia"], {}); n = str(e["n"])
    herm = [por_n[str(x)] for x in fam["eds"] if str(x) != n and str(x) in por_n]
    import glob, struct
    cs = sorted(glob.glob(os.path.join(AQUI, carpeta(e), "cuadros", "*.jpg")))
    def dims(f):                                  # ancho/alto de un JPG sin abrir librerías
        b = open(f, "rb").read(); i = 2
        while i < len(b):
            m, L = b[i + 1], int.from_bytes(b[i + 2:i + 4], "big")
            if m in (0xC0, 0xC2): return int.from_bytes(b[i + 7:i + 9], "big"), int.from_bytes(b[i + 5:i + 7], "big")
            i += 2 + L
        return 9, 16
    w, h = dims(cs[0]) if cs else (9, 16)
    vert = "horizontal 16:9" if w > h else "vertical 9:16"
    rel = ""
    if e["familia"] == "pantalla-filmada" and f"{n}p" in por_n:
        i = por_n[f"{n}p"]
        rel = f"\n> **El video que corre DENTRO de la pantalla es otro formato:** {titulo(i)} → [`../{carpeta(i)}/GUIA.md`](../{carpeta(i)}/GUIA.md). Hazlo primero y luego pégalo en la pantalla con esta guía.\n"
    if n.endswith("p"):
        o = por_n[n[:-1]]
        rel = f"\n> **Origen:** es el video que se ve dentro de la laptop/monitor de {titulo(o)} ([`../{carpeta(o)}/GUIA.md`](../{carpeta(o)}/GUIA.md)), sacado derecho con `pantalla_interior.py`. Se puede publicar solo o volver a meter en una pantalla filmada.\n"
    pal = " · ".join(f"`{h}` {p} %" for h, p in zip(e.get("paleta", [])[:5], e.get("paleta_pct", [])[:5]))
    L = [f"# Guía para Claude · {titulo(e)}", "",
         "> Esta guía explica **qué es** este formato y **cómo hacerlo** con el sistema de edición. Las rutas son relativas a la raíz del",
         "> sistema (ver `plantillas/formatos/GUIA-FORMATOS.md`). Antes de editar, mira la referencia: `hoja.jpg` y `cuadros/` de esta carpeta",
         "> (si no están, básate en la descripción y en la paleta medida).", rel,
         "## Qué es", f"**Familia:** {fam['nombre']}" + (f" (hermanos: {', '.join(titulo(h) for h in herm)})" if herm else ""), "",
         f"**La idea:** {fam['idea']}", "", f"**Lo que se ve en la referencia:** {e['detalle']}", "",
         f"**Para qué sirve:** {fam['para']}", "",
         "## Cómo reconocerlo",
         f"- **Texto:** {fam['texto']}", f"- **Animación y ritmo:** {fam['mov']}", f"- **Audio:** {fam['audio']}",
         f"- **Medido en la referencia:** {e.get('dur', '?')} s · {e.get('cortes', '?')} cortes ({ritmo_txt(e.get('ritmo', 0))}, {e.get('ritmo', 0)} cortes/s) · {vert}",
         f"- **Paleta medida:** {pal}" if pal else "", "",
         "## Cómo hacerlo", "### 0. Antes de empezar (siempre)",
         "- Pregunta una sola vez: música (carpeta con canciones o MCP de música como Epidemic Sound), duración máxima, formato (Redes 1080 por defecto, 4K solo si lo piden) y nombres propios.",
         "- Mira `hoja.jpg` y algunos `cuadros/` de esta carpeta con Read para copiar el look (es guía de look: no se recrea el video ajeno tal cual, se aplica a la idea de la persona).",
         "- Muestra a la persona el **plan tal cual, paso a paso**, con la lista de posibles errores, y no edites hasta que diga \"sí\" (CLAUDE.md, paso 3).", "",
         "### 1. Qué necesitas"] + [f"- {x}" for x in rec.get("necesitas", ["(sin receta: usa la idea y el motor de la familia)"])] + [
         "", "### 2. Pasos"] + [f"{k}. {x}" for k, x in enumerate(rec.get("pasos", [fam.get("motor", "")]), 1)] + [
         f"", f"**Motor sugerido:** {fam['motor']}", "",
         "### 3. Antes de entregar (siempre)",
         "- Stills en 6–10 tiempos (incluye cortes, cambios de escena y el CTA) y míralos.",
         "- Zona segura de Instagram en 1080x1920: nada importante con y < 262, y > 1540, ni x > 900 desde y > 700.",
         "- Nada encima de la cara de la persona; subtítulos de al menos 0.9 s; sin palabras cortadas ni pausas > 0.35 s; voz pareja y −14 LUFS.",
         "- **Revisión final cuadro por cuadro:** `editor-testimoniales/editor/.venv/bin/python editor-testimoniales/editor/revisar_final.py <carpeta> \"<video>\"` y mira las hojas de `revision_final/`.", "",
         "## Evita"] + [f"- {x}" for x in rec.get("evitar", [])] + [
         "- Inventar datos, cifras o pantallas de apps que no existen.", "- Generar videos con Higgsfield (son caros): solo imágenes, y se animan con código.", "",
         f"Archivos de esta carpeta: `ESTILO.md` (ficha medida), `hoja.jpg`, `paleta.png`, `cuadros/`."]
    return "\n".join(x for x in L if x is not None) + "\n"

for e in E:
    open(os.path.join(AQUI, carpeta(e), "GUIA.md"), "w").write(guia(e))

# ---------- índice ----------
orden = sorted(F, key=lambda k: min((E.index(por_n[str(x)]) for x in F[k]["eds"] if str(x) in por_n), default=999))
I = ["# Guía de formatos (para Claude)", "",
     f"Este sistema tiene **{len(E)} formatos** en **{len(F)} familias**: los 50 \"Editor N\", \"Pizarra Pro\" y 10 formatos \"Editor N · pantalla\"",
     "(el video que corre DENTRO de la laptop/monitor en los formatos de la familia Pantalla Filmada).", "",
     "## Cómo usar esta guía",
     "1. Si la persona nombra un formato (\"hazlo como el Editor 26\", \"el de la laptop\", \"estilo Apple\"), abre su `GUIA.md` (tabla de abajo).",
     "2. Si no nombra ninguno, elige por **para qué sirve** y por el material que tiene (¿sale la persona? ¿hay grabación de pantalla? ¿solo voz?) y proponle 1–2 opciones.",
     "3. Lee la `GUIA.md` completa y mira `hoja.jpg` + `cuadros/` de esa carpeta antes de escribir el plan.",
     "4. Sigue el flujo de `CLAUDE.md` (plan tal cual → editar → revisión final cuadro por cuadro).", "",
     "Rutas: todo es relativo a la raíz del sistema (`estilo-cine/`, `editor-testimoniales/`, `editor-anuncios/`, `plantillas/`). En esta Mac:",
     "`estilo-cine` = `estilo-cine`, `editor-testimoniales` = `editor-testimoniales`, `editor-anuncios` = `editor-anuncios`,",
     "`plantillas/formatos` = `plantillas/formatos`.", ""]
for k in orden:
    fam = F[k]; eds = [por_n[str(x)] for x in fam["eds"] if str(x) in por_n]
    if not eds: continue
    I += [f"## {fam['nombre']}", fam["idea"], "", f"*Para qué:* {fam['para']}", "", "| Formato | Qué se ve | Guía |", "|---|---|---|"]
    for e in eds:
        I.append(f"| **{titulo(e)}** | {e['detalle'][:150].rstrip()}{'…' if len(e['detalle']) > 150 else ''} | [`{carpeta(e)}/GUIA.md`]({carpeta(e)}/GUIA.md) |")
    I.append("")
open(os.path.join(AQUI, "GUIA-FORMATOS.md"), "w").write("\n".join(I))
print(f"✓ {len(E)} guías (GUIA.md en cada carpeta) + GUIA-FORMATOS.md")
