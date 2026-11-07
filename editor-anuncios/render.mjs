// Paso 3 — render final: zooms con seguimiento de cara + transiciones + gráficos + subtítulos + sfx + volumen.
//   node render.mjs <carpeta_proyecto> stills 1.5,8,20   -> cuadros de prueba en <proyecto>/stills
//   node render.mjs <carpeta_proyecto>                   -> <proyecto>/final.mp4
import puppeteer from "puppeteer-core";
import { execFileSync } from "node:child_process";
import { pathToFileURL, fileURLToPath } from "node:url";
import { medirArchivo, medirGrafo, nivelar } from "../estilo-cine/volumen.mjs";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";

const PROJ = path.resolve(process.argv[2]), MODE = process.argv[3] || "full";
const HERE = fileURLToPath(new URL(".", import.meta.url));   // rutas con espacios: sin %20 doble
const J = f => JSON.parse(fs.readFileSync(path.join(PROJ, f), "utf8"));
const edl = J("edl.json"), words = J("words_out.json");
const ctx = { window: {} }; vm.runInNewContext(fs.readFileSync(path.join(PROJ, "cues.js"), "utf8"), ctx);
const E = ctx.window.EDIT;
const { W, H } = edl, [num, den] = edl.fps, FPS = num / den, V = H > W;
fs.writeFileSync(path.join(PROJ, "_data.js"), `window.EDL=${JSON.stringify(edl)};window.WORDS=${JSON.stringify(words)};`);

// ---------- plan de cámara por tramo ----------
const CAM = Object.assign({ med: V ? 0.21 : 0.30, close: V ? 0.27 : 0.40, maxZ: 1.9, fx: 0.5, fy: V ? 0.42 : 0.33, push: 0.05 }, E.camera || {});
const TR = { settle: [0.045, 0.30], zoom: [0.16, 0.26], cut: [0, 0.01] };
let level = "close";
// cortes propios del video (ya editado): se usan para cambiar encuadre justo ahí
const baseSegs = [];
for (const s of edl.segments) {
  const cuts = (E.splits || []).filter(x => x > s.out_in + .3 && x < s.out_out - .3), pts = [s.out_in, ...cuts, s.out_out];
  for (let i = 0; i < pts.length - 1; i++) baseSegs.push({ ...s, out_in: pts[i], out_out: pts[i + 1] });
}
const segs = baseSegs.map((s, k) => {
  const dur = s.out_out - s.out_in;
  if (dur >= 0.7 || k === 0) level = level === "med" ? "close" : "med";      // alterna encuadre en cada corte (tramos muy cortos lo heredan)
  const lv = (E.framing && E.framing[k]) || level;
  const fh = Math.max(0.05, s.face[2]);
  const zb = Math.min(CAM.maxZ, Math.max(1, CAM[lv] / fh));
  const tr = (E.transitions && E.transitions[k]) || (k === 0 ? "cut" : k % 4 === 0 ? "zoom" : "settle");
  return { k, s: s.out_in, e: s.out_out, zb, cx: s.face[0], cy: s.face[1], tr, push: dur > 3.2 ? CAM.push : 0 };
});
// seguimiento de cara (track.py): la persona siempre al centro
const TRACK = fs.existsSync(path.join(PROJ, "face_track.json")) && E.center !== false ? J("face_track.json") : null;
if (TRACK) for (const g of segs) {
  const pts = TRACK.filter(r => r[0] >= g.s - .05 && r[0] < g.e);
  if (!pts.length) continue;
  const zmin = Math.max(...pts.map(r => Math.max(.5 / r[1], .5 / (1 - r[1]))));
  g.zb = Math.min(CAM.maxZ, Math.max(g.zb, zmin + .02));
}
if (TRACK) for (const g of segs) { const pts = TRACK.filter(r => r[0] >= g.s - .05 && r[0] < g.e); if (pts.length) { const fh = pts.map(r => r[3]).sort((a, b) => a - b)[Math.floor(pts.length / 2)]; g.target = Math.min(CAM.maxZ, g.zb) * fh; } }
const flashes = [...(E.flashes || []), ...segs.filter(g => g.tr === "flash").map(g => g.s)];
segs.forEach(g => { if (g.tr === "flash") g.tr = "zoom"; });
const emph = E.zooms || [];   // [inicio, fin, z0, z1] multiplicativos (golpes de zoom de énfasis)

const PRE_ = .12, POST_ = .26; let CUTFX_ = [];
// misma fórmula en JS (cuadros de prueba) y en expresión de ffmpeg (render)
function trackAt(t) { if (!TRACK) return null; let i = TRACK.findIndex(r => r[0] > t); if (i <= 0) i = i < 0 ? TRACK.length - 1 : 1;
  const a = TRACK[i - 1], b = TRACK[i], q = b[0] > a[0] && b[0] - a[0] < .5 ? Math.min(1, Math.max(0, (t - a[0]) / (b[0] - a[0]))) : 0; return [a[1] + (b[1] - a[1]) * q, a[2] + (b[2] - a[2]) * q, a[3] + (b[3] - a[3]) * q]; }
function camAt(t) {
  const g = segs.find(x => t >= x.s && t < x.e) || segs[segs.length - 1];
  const bumpJ = c => t >= c - PRE_ && t < c ? Math.pow((t - (c - PRE_)) / PRE_, 2) : t >= c && t <= c + POST_ ? Math.pow(1 - (t - c) / POST_, 2) : 0;
  const [A, D] = TR[g.tr], p = Math.min(1, Math.max(0, (t - g.s) / (g.e - g.s)));
  let z = g.zb * (1 + g.push * p) * (1 + A * Math.pow(Math.max(0, 1 - (t - g.s) / D), 2));
  const tk = trackAt(t);
  if (tk && E.stabilize !== false) {   // tamaño de cara constante en pantalla: compensa el zoom que ya trae el video
    const target = g.target ?? (g.zb * tk[2]);
    const zs = target / Math.max(.05, tk[2]), zc = Math.max(.5 / tk[0] + .015, .5 / (1 - tk[0]) + .015);
    let zz = Math.max(zs, Math.min(zc, zs * 1.08));   // prioridad: sin zoom visible; centra hasta donde no agrande más de 8%
    z = Math.min(CAM.maxZ, Math.max(1, zz)) * (1 + A * Math.pow(Math.max(0, 1 - (t - g.s) / D), 2));
  }
  for (const [a, b, z0, z1] of emph) if (t >= a && t <= b) { const q = (t - a) / (b - a); z *= z0 + (z1 - z0) * q * q * (3 - 2 * q); }
  for (const x of CUTFX_) z *= 1 + (x.fx === "zoom" ? .22 : .3) * bumpJ(x.t);
  const tr = trackAt(t); return { z, cx: tr ? tr[0] : g.cx, cy: tr ? tr[1] : g.cy };
}
const f = x => Number(x).toFixed(5);
function nest(list, val, dflt) { return list.reduceRight((acc, g) => `if(between(t,${f(g.s)},${f(g.e)}),${val(g)},${acc})`, dflt); }
const Zseg = nest(segs, g => `${f(g.zb)}*(1+${f(g.push)}*clip((t-${f(g.s)})/${f(g.e - g.s)},0,1))*(1+${f(TR[g.tr][0])}*pow(max(0,1-(t-${f(g.s)})/${f(TR[g.tr][1])}),2))`, f(segs[segs.length - 1].zb));
const Zemph = emph.reduceRight((acc, [a, b, z0, z1]) => `if(between(t,${f(a)},${f(b)}),(${f(z0)}+${f(z1 - z0)}*(3*pow((t-${f(a)})/${f(b - a)},2)-2*pow((t-${f(a)})/${f(b - a)},3))),${acc})`, "1");
// Transiciones visibles en los cortes (ocultan el brinco): "zoom" = acercamiento con desenfoque; "whip" = barrido lateral con desenfoque de movimiento
const cutFx = (E.cutFx || (E.splits || []).map((t, i) => ({ t, fx: "zoom" }))).filter(x => !(E.cues || []).some(c => ["counter", "support", "build", "shield", "headline", "path", "blocks", "plan", "badge", "scene", "meter", "runner"].includes(c.type) && x.t > c.start + .05 && x.t < c.end - .05));
const PRE = PRE_, POST = POST_; CUTFX_ = cutFx;
const bump = c => `if(between(t,${f(c - PRE)},${f(c)}),pow((t-${f(c - PRE)})/${PRE},2),if(between(t,${f(c)},${f(c + POST)}),pow(1-(t-${f(c)})/${POST},2),0))`;
const Ztr = cutFx.map(x => `(1+${x.fx === "zoom" ? 0.22 : 0.3}*${bump(x.t)})`).join("*") || "1";   // el barrido también acerca un poco para tener espacio de movimiento
const Xtr = cutFx.filter(x => x.fx === "whip").map((x, i) => `${i % 2 ? "-" : ""}${(W * .22).toFixed(1)}*if(lt(t,${f(x.t)}),${bump(x.t)},-${bump(x.t)})`).join("+") || "0";
const Z = `(${Zseg})*(${Zemph})*(${Ztr})`;
const win = (list, a, b) => list.map(x => `between(t,${f(x.t + a)},${f(x.t + b)})`).join("+") || "0";
const zl = cutFx.filter(x => x.fx === "zoom"), wl = cutFx.filter(x => x.fx === "whip");
const blurFx = [
  zl.length && `gblur=sigma=${(18 * W / 1080).toFixed(1)}:enable='${win(zl, -.05, .07)}'`,
  zl.length && `gblur=sigma=${(7 * W / 1080).toFixed(1)}:enable='${win(zl, -.11, -.05)}+${win(zl, .07, .17)}'`,
  wl.length && `gblur=sigma=${(42 * W / 1080).toFixed(1)}:sigmaV=0.6:enable='${win(wl, -.06, .08)}'`,
  wl.length && `gblur=sigma=${(16 * W / 1080).toFixed(1)}:sigmaV=0.4:enable='${win(wl, -.12, -.06)}+${win(wl, .08, .18)}'`,
].filter(Boolean).join(",");
// centro: interpolación lineal entre muestras de la cara (suma de tramos, sin anidar)
const lin = k => { if (!TRACK) return null; const terms = [];
  for (let i = 0; i < TRACK.length - 1; i++) { const [t0, t1] = [TRACK[i][0], TRACK[i + 1][0]], a = TRACK[i][k], b = TRACK[i + 1][k];
    if (t1 - t0 > .5) { terms.push(`gte(t,${f(t0)})*lt(t,${f(t1)})*${f(a)}`); continue; }    // hueco (corte): mantener
    terms.push(`gte(t,${f(t0)})*lt(t,${f(t1)})*(${f(a)}+(t-${f(t0)})*(${f((b - a) / (t1 - t0))}))`); }
  const last = TRACK[TRACK.length - 1]; terms.push(`gte(t,${f(last[0])})*${f(last[k])}`); return `if(isnan(t),${f(TRACK[0][k])},${terms.join("+")})`; };
const CX = nest(segs, g => f(g.cx), "0.5"), CY = nest(segs, g => f(g.cy), "0.33");
const camFilter = (z, cx, cy, xx = "0") => `scale=w='trunc(${W}*(${z})/2)*2':h='trunc(${H}*(${z})/2)*2':eval=frame:flags=lanczos,` +
  `crop=${W}:${H}:x='clip((${cx})*iw-${W * CAM.fx}+(${xx}),0,iw-${W})':y='clip((${cy})*ih-${H * CAM.fy},0,ih-${H})'`;

// ---------- capa de gráficos ----------
const browser = await puppeteer.launch({ executablePath: process.env.CHROME || ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/local/bin/chromium'].find(f => fs.existsSync(f)) || 'google-chrome', args: [...(process.platform === 'linux' ? ['--no-sandbox'] : []), "--allow-file-access-from-files"] });
const page = await browser.newPage();
await page.setViewport({ width: W, height: H });
page.on("pageerror", e => console.error("página:", e.message));
await page.goto(pathToFileURL(path.join(HERE, "overlay.html")).href + `?proj=${encodeURIComponent(PROJ)}`);
await page.waitForFunction(() => window.__ready === true, { timeout: 30000 });
await page.evaluate(fl => { window.EDIT.flashes = fl; }, flashes);
const shot = async t => { await page.evaluate(t => window.__render(t), t); return page.screenshot({ type: "png", omitBackground: true }); };

if (MODE === "stills") {
  const dir = path.join(PROJ, "stills"); fs.mkdirSync(dir, { recursive: true });
  for (const t of process.argv[4].split(",").map(Number)) {
    const png = path.join(dir, "_ov.png"); fs.writeFileSync(png, await shot(t));
    const c = camAt(t);
    execFileSync("ffmpeg", ["-v", "error", "-y", "-ss", String(t), "-i", path.join(PROJ, "cut.mov"), "-i", png, "-filter_complex",
      `[0:v]${camFilter(f(c.z), f(c.cx), f(c.cy))}${E.vf ? "," + E.vf : ""}[b];[b][1:v]overlay=0:0`, "-frames:v", "1", path.join(dir, `s_${t}.jpg`)]);
  }
  await browser.close(); process.exit(0);
}

const N = edl.frames, FR = path.join(PROJ, "frames");
fs.rmSync(FR, { recursive: true, force: true }); fs.mkdirSync(FR);
const t0 = Date.now();
for (let i = 0; i < N; i++) {
  fs.writeFileSync(path.join(FR, `f_${String(i).padStart(5, "0")}.png`), await shot(i / FPS));
  if (i % 300 === 0) console.error(`cuadro ${i}/${N}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
await browser.close();

// ---------- sonido: voz normalizada + whoosh en transiciones + pop en gráficos ----------
const sfxOn = E.sfx !== false;
const events = [];
if (sfxOn) {
  cutFx.forEach(x => events.push(["whoosh", Math.max(0, x.t - 0.22), 0.5]));
  flashes.forEach(t => events.push(["whoosh", Math.max(0, t - 0.18), 0.6]));
  const FULLS = ["headline", "path", "blocks", "plan", "badge", "counter", "support", "build", "shield", "meter", "runner", "scene"];
  (E.cues || []).forEach(c => {
    if (c.start > 0.05) events.push([FULLS.includes(c.type) ? "whoosh" : "pop", Math.max(0, c.start - (FULLS.includes(c.type) ? .12 : .02)), FULLS.includes(c.type) ? .55 : .45]);
    if (FULLS.includes(c.type) && !c.hold) events.push(["whoosh", Math.max(0, c.end - .2), .4]);
    if (c.clickAt) events.push(["click", c.clickAt, .7]);
    (c.throws || []).forEach(x => events.push(["pop", x + .42, .35]));
    if (c.dropAt) events.push(["whoosh", c.dropAt, .5]);
  });
}
const ins = ["-i", path.join(PROJ, "cut.mov"), "-framerate", `${num}/${den}`, "-i", path.join(FR, "f_%05d.png")];
let camChain = camFilter(Z, CX, CY, Xtr);
if (TRACK) {   // posición exacta cuadro por cuadro (persona siempre al centro)
  const lines = [];
  for (let i = 0; i < N; i++) { const t = i / FPS, c = camAt(t), iw = Math.trunc(W * c.z / 2) * 2, ih = Math.trunc(H * c.z / 2) * 2;
    const x = Math.max(0, Math.min(iw - W, Math.round(c.cx * iw - W * CAM.fx))), y = Math.max(0, Math.min(ih - H, Math.round(c.cy * ih - H * CAM.fy)));
    lines.push(`${Math.max(0, t - .001).toFixed(4)} scale@cam w ${iw}, scale@cam h ${ih}, crop@cam x ${x}, crop@cam y ${y};`); }
  fs.writeFileSync(path.join(PROJ, "camara.txt"), lines.join("\n"));
  camChain = `sendcmd=f='${path.join(PROJ, "camara.txt")}',scale@cam=w=${W}:h=${H}:eval=frame:flags=lanczos,crop@cam=${W}:${H}:0:0`;
}
const fcV = `[0:v]${camChain}${blurFx ? "," + blurFx : ""}${E.vf ? "," + E.vf : ""}[b];[b][1:v]overlay=0:0:format=auto,format=yuv420p[v]`;
let fc = `[0:a]aresample=48000,${nivelar(medirArchivo(path.join(PROJ, "cut.mov")), -14, -1.5)}[voz]`;
events.forEach(([kind, t, vol], k) => { ins.push("-i", path.join(HERE, "sfx", `${kind}.wav`)); fc += `;[${k + 2}:a]volume=${vol},adelay=${Math.round(t * 1000)}:all=1[s${k}]`; });
// música opcional: E.music = { file, from (s), vol } — se agacha cuando hay voz (sidechain) y se desvanece al final
const MU = E.music && fs.existsSync(path.resolve(PROJ, E.music.file)) ? E.music : null;
const extra = [];
if (MU) { const k = events.length + 2, D = N / FPS; ins.push("-ss", String(MU.from || 0), "-i", path.resolve(PROJ, MU.file));
  fc += `;[voz]asplit=2[vz][vsc];[${k}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:${D.toFixed(3)},volume=${MU.vol ?? .12},afade=t=in:d=0.3,afade=t=out:st=${Math.max(0, D - 1).toFixed(2)}:d=1[m0];[m0][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=10:release=300[mus]`;
  extra.push("[mus]"); }
fc += (events.length || MU) ? `;[${MU ? "vz" : "voz"}]${events.map((_, k) => `[s${k}]`).join("")}${extra.join("")}amix=inputs=${events.length + 1 + extra.length}:normalize=0:duration=first${MU ? "[pre]" : "[a]"}` : `;[voz]anull[a]`;
if (MU) fc += `;[pre]${nivelar(medirGrafo(ins, fc, "pre"), -14, -1.5)}[a]`;
fc = fcV + ";" + fc;
const script = path.join(PROJ, "render_filter.txt"); fs.writeFileSync(script, fc);
const dst = path.join(PROJ, "final.mp4");
execFileSync("ffmpeg", ["-v", "error", "-y", ...ins, "-/filter_complex", script, "-map", "[v]", "-map", "[a]", "-r", `${num}/${den}`,
  "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", dst], { stdio: "inherit" });
fs.rmSync(FR, { recursive: true, force: true });
const got = parseInt(execFileSync("ffprobe", ["-v", "error", "-select_streams", "v", "-show_entries", "stream=nb_frames", "-of", "csv=p=0", dst]).toString(), 10);
console.error(`${Number(got) === N ? "OK" : "ERROR"} cuadros ${got}/${N}  ·  ${((Date.now() - t0) / 1000).toFixed(0)}s  ·  ${dst}`);
