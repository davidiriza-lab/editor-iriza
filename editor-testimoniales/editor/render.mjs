// Paso 4 — render: subtítulos + transición en cada corte + cierre con fundido. Luego mezcla.py pone voz + música.
//   node render.mjs <proyecto> layout              -> <proyecto>/layout.json (dónde quedó cada texto; para revisar_texto.py)
//   node render.mjs <proyecto> stills 1.5,8,20     -> <proyecto>/stills/s_<t>.jpg (prueba rápida)
//   node render.mjs <proyecto>                     -> <proyecto>/_video.mp4 y corre mezcla.py -> <proyecto>/<salida>
//   node render.mjs <proyecto> v1 [stills t1,t2]   -> subtítulos solo en las tomas de stock del V1 (v1.json, ver v1.py)
import { chromium } from "playwright-core";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));   // rutas con espacios: sin %20
const PROJ = path.resolve(process.argv[2]);
const ARGS = process.argv.slice(3);
const V1 = ARGS[0] === "v1"; if (V1) ARGS.shift();
const STILLS = ARGS[0] === "stills" ? ARGS[1].split(",").map(Number) : null;
const P = f => path.join(PROJ, f);
const J = f => JSON.parse(fs.readFileSync(P(f), "utf8"));
const BASE = JSON.parse(fs.readFileSync(path.join(HERE, "plantilla.json"), "utf8"));
const C = { ...BASE, ...J("proyecto.json") }, FACES = J("faces.json"), PAGES = J("pages.json");
const CJ = J("cortes.json");
// candado: dos renders del mismo proyecto a la vez se pisan el archivo
const LOCK = P(".render.lock");
if (!["layout", "stills"].includes(ARGS[0])) {
  if (fs.existsSync(LOCK)) { const pid = +fs.readFileSync(LOCK, "utf8"); let vivo = false; try { process.kill(pid, 0); vivo = true; } catch {}
    if (vivo) { console.error(`✗ ya hay un render de este proyecto corriendo (pid ${pid})`); process.exit(1); } }
  fs.writeFileSync(LOCK, String(process.pid)); process.on("exit", () => { try { fs.unlinkSync(LOCK); } catch {} });
}
const probe = (f, e) => execFileSync("ffprobe", ["-v", "error", ...e, "-of", "csv=p=0", f]).toString().trim();
const C0 = J("proyecto.json"), VERT = !!C0.vertical, W = VERT ? 1080 : 1920, H = VERT ? 1920 : 1080;

const browser = await chromium.launch({ executablePath: process.env.CHROME || ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/local/bin/chromium'].find(f => fs.existsSync(f)) || 'google-chrome', headless: true, args: [...(process.platform === 'linux' ? ['--no-sandbox'] : []), "--allow-file-access-from-files"] });
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on("pageerror", e => console.error("página:", e.message));
await page.goto("file://" + path.join(HERE, "overlay.html") + "?proj=" + encodeURIComponent(PROJ) + (V1 ? "&v1=1" : "") + (VERT ? "&vert=1" : ""));
await page.waitForFunction(() => window.__ready === true, null, { timeout: 30000 });
// layout.json: caja real de cada subtítulo, de la flecha y la zona segura → revisar_texto.py
fs.writeFileSync(P("layout.json"), JSON.stringify(await page.evaluate(() => ({ paginas: window.__layout || [], flecha: window.__flecha || null, zona_segura: window.__zs }))));
if (ARGS[0] === "layout") { await browser.close(); console.error("layout en", P("layout.json")); process.exit(0); }
const shot = async t => { await page.evaluate(t => window.__render(t), t); return page.screenshot({ type: "png", omitBackground: true }); };

// ---------- modo V1: subtítulos solo dentro de las tomas insertadas ----------
if (V1) {
  const V = J("v1.json"), SRC = V.video;
  const OUT = V.salida || (/PRE SUBS/i.test(SRC) ? SRC.replace(/PRE SUBS/i, "CON SUBS") : SRC.replace(/\.mp4$/i, " CON SUBS.mp4"));
  const FPS = eval(probe(SRC, ["-select_streams", "v:0", "-show_entries", "stream=r_frame_rate"])), DUR = +probe(SRC, ["-show_entries", "format=duration"]);
  if (STILLS) { const dir = P("stills_v1"); fs.mkdirSync(dir, { recursive: true });
    for (const t of STILLS) { fs.writeFileSync(path.join(dir, "_ov.png"), await shot(t));
      execFileSync("ffmpeg", ["-v", "error", "-y", "-ss", String(t), "-i", SRC, "-i", path.join(dir, "_ov.png"), "-filter_complex", "[0:v][1:v]overlay", "-frames:v", "1", "-q:v", "3", path.join(dir, `s_${t}.jpg`)]); }
    await browser.close(); console.error("stills en", dir); process.exit(0); }
  const FR = P("_frames_v1"), N = Math.round(DUR * FPS);
  fs.rmSync(FR, { recursive: true, force: true }); fs.mkdirSync(FR);
  fs.writeFileSync(path.join(FR, "blank.png"), await shot(-100));
  for (let i = 0; i < N; i++) { const t = i / FPS, f = path.join(FR, `f_${String(i).padStart(5, "0")}.png`);
    if (V.ventanas.some(([a, z]) => t >= a - .05 && t < z + .05)) fs.writeFileSync(f, await shot(t)); else fs.symlinkSync("blank.png", f); }
  await browser.close();
  execFileSync("ffmpeg", ["-v", "error", "-y", "-i", SRC, "-framerate", String(FPS), "-i", path.join(FR, "f_%05d.png"), "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
    "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", OUT], { stdio: "inherit" });
  fs.rmSync(FR, { recursive: true, force: true }); console.error("listo ->", OUT); process.exit(0);
}

// ---------- armado normal ----------
// la cola ya viene en corte.mp4 como imagen real (armar.py); solo los proyectos viejos sin cola_real se congelan al final
const SRC = P("corte.mp4"), FPS = 30000 / 1001, SRC_DUR = +probe(SRC, ["-show_entries", "format=duration"]), TAIL = CJ.cola_real != null ? 0 : (C.cola ?? 1.6), DUR = SRC_DUR + TAIL;
// fundido final: empieza justo antes de que termine de hablar
const FIN_VOZ = CJ.fin_voz ?? (SRC_DUR - .2), FADE0 = Math.max(0, Math.min(DUR - .4, FIN_VOZ - .15));
const panels = PAGES.filter(p => p.tag === "panel");
// transición en cada corte, salvo los marcados, los tapados por un panel o por una toma de stock (ahí no se ve el corte)
const tapado = c => (C.broll || []).some(r => c > r.a - .05 && c < r.b + .05);
const CUTS = CJ.fronteras.slice(0, -1).filter(c => !(C.sin_transicion || []).some(x => Math.abs(x - c) < .05) && !panels.some(p => c > p.start - .35 && c < p.end + .15) && !tapado(c));
const fx = FACES.filter(c => c.cx != null), FX = fx.reduce((a, c) => a + c.cx, 0) / (fx.length || 1), FY = fx.reduce((a, c) => a + c.cy, 0) / (fx.length || 1);
const f = x => Number(x).toFixed(4), PRE = .12, POST = .28;
const bump = c => `if(between(t,${f(c - PRE)},${f(c)}),pow((t-${f(c - PRE)})/${PRE},2),if(between(t,${f(c)},${f(c + POST)}),pow(1-(t-${f(c)})/${POST},2),0))`;
const Z = C.sin_zoom ? "1" : CUTS.map(c => `(1+0.12*${bump(c)})`).join("*") || "1";   // sin_zoom: el corte solo lleva un destello de desenfoque
const win = (a, b) => CUTS.map(c => `between(t,${f(c + a)},${f(c + b)})`).join("+") || "0";
// transición sin zoom: desenfoque fuerte alrededor del corte y suave en las orillas (plantilla.json -> transicion)
const TS = C.transicion?.sigma ?? 18, TD = C.transicion?.dur ?? .22;
const cam = `scale=w='trunc(${W}*(${Z})/2)*2':h='trunc(${H}*(${Z})/2)*2':eval=frame:flags=lanczos,crop=${W}:${H}:x='${f(FX)}*(iw-${W})':y='${f(FY)}*(ih-${H})'` +
  (CUTS.length ? `,gblur=sigma=${TS}:enable='${win(-TD * .3, TD * .35)}',gblur=sigma=${(TS * .4).toFixed(1)}:enable='${win(-TD * .55, -TD * .3)}+${win(TD * .35, TD * .75)}'` : "");

if (STILLS) {
  const dir = P("stills"); fs.mkdirSync(dir, { recursive: true });
  for (const t of STILLS) { const png = path.join(dir, "_ov.png"); fs.writeFileSync(png, await shot(t));
    execFileSync("ffmpeg", ["-v", "error", "-y", "-ss", String(Math.min(t, SRC_DUR - .05)), "-i", SRC, "-i", png, "-filter_complex", "[0:v][1:v]overlay=0:0", "-frames:v", "1", "-q:v", "3", path.join(dir, `s_${t}.jpg`)]); }
  await browser.close(); console.error("stills en", dir); process.exit(0);
}
const FR = P("_frames"), N = Math.round(DUR * FPS);
fs.rmSync(FR, { recursive: true, force: true }); fs.mkdirSync(FR);
const t0 = Date.now();
for (let i = 0; i < N; i++) {
  fs.writeFileSync(path.join(FR, `f_${String(i).padStart(5, "0")}.png`), await shot(i / FPS));
  if (i % 300 === 0) console.error(`cuadro ${i}/${N}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
await browser.close();
const fc = `[0:v]${TAIL > 0 ? `tpad=stop_mode=clone:stop_duration=${TAIL},` : ""}${cam}[cv];[cv][1:v]overlay=0:0:format=auto,fade=t=out:st=${f(FADE0)}:d=${f(DUR - FADE0)},format=yuv420p[v]`;
fs.writeFileSync(P("_render_filter.txt"), fc);
execFileSync("ffmpeg", ["-v", "error", "-y", "-i", SRC, "-framerate", "30000/1001", "-i", path.join(FR, "f_%05d.png"), "-/filter_complex", P("_render_filter.txt"),
  "-map", "[v]", "-t", f(DUR), "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-movflags", "+faststart", P("_video.mp4")], { stdio: "inherit" });
fs.rmSync(FR, { recursive: true, force: true });
fs.writeFileSync(P("_transiciones.json"), JSON.stringify(CUTS));
console.error(`video listo en ${((Date.now() - t0) / 1000).toFixed(0)}s · transiciones en ${CUTS.join(", ")}`);
execFileSync(path.join(HERE, ".venv", "bin", "python"), [path.join(HERE, "mezcla.py"), PROJ], { stdio: "inherit" });
