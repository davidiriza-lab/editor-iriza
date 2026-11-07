// Formato "Metodología" (tutorial cámara + pantalla, como Referencia.mp4 de CONTENIDO/Metodología):
// arriba tu cámara con filtro de belleza, franja negra con subtítulos serif de 1–3 palabras, abajo la pantalla con zoom al cursor.
// Uso: node estilo-cine/metodo.mjs proyectos/<n> [--stills 3,10] [--hasta 8]
// Necesita: corte/cam.mov (audio), cuadros_pro/ (cámara 1080x768 con piel), scr/ (pantalla 1920x1080), zoom.json, voz/palabras.json, metodo.json
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import puppeteer from '../motor/node_modules/puppeteer-core/lib/puppeteer/puppeteer-core.js';
import { medirArchivo, medirGrafo, nivelar } from './volumen.mjs';

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CHROME = process.env.CHROME || ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/local/bin/chromium'].find(f => fs.existsSync(f)) || 'google-chrome';  // Mac, Linux o Windows (WSL)
const args = process.argv.slice(2), proy = path.resolve(args[0]);
const opt = k => { const i = args.indexOf(k); return i > 0 ? args[i + 1] : null; };
const cfg = JSON.parse(fs.readFileSync(path.join(proy, 'metodo.json')));
const FPS = '24000/1001', fps = 24000 / 1001;
const n = fs.readdirSync(path.join(proy, 'cuadros_pro')).filter(f => f.endsWith('.jpg')).length;
const zoom = JSON.parse(fs.readFileSync(path.join(proy, 'zoom.json')));
const voz = JSON.parse(fs.readFileSync(path.join(proy, 'voz/palabras.json')));

// ---- subtítulos: 1–3 palabras, cortando en puntuación ----
const CAMBIA = Object.assign({ medita: 'me edita', prono: 'prompt', promo: 'prompt', prompte: 'prompt', cloud: 'Claude' }, cfg.cambia || {});
const limpia = t => { const b = t.replace(/[.,;:…]+$/u, ''); return CAMBIA[b.toLowerCase()] ?? b; };
const subs = []; let cur = null;
voz.forEach((w, i) => {
  const txt = limpia(w.t); if (!txt) return;
  const nueva = /^[A-ZÁÉÍÓÚÑ¿¡]/.test(w.t) && !/^(Claude|DM|Instagram|Design|IA)/.test(w.t);  // Whisper pone mayúscula al iniciar oración
  if (!cur || nueva || cur.n >= 3 || cur.txt.length + txt.length > 18 || /[.,;:?!]$/.test(voz[i - 1]?.t || '') || w.a - cur.b > .45) {
    cur = { a: w.a, b: w.b, txt, n: 1 }; subs.push(cur);
  } else { cur.txt += ' ' + txt; cur.b = w.b; cur.n++; }
});
subs.forEach((s, i) => { s.fin = Math.min(i < subs.length - 1 ? subs[i + 1].a : s.b + .6, s.b + .7); });
const dur = n / fps;

const rel = `/${path.relative(RAIZ, proy)}`;
const PAGE = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:IS;src:url(/estilo-cine/fuentes/InstrumentSerif-Regular.ttf)}
html,body{margin:0;background:#000;overflow:hidden}</style></head><body><canvas id="c" width="1080" height="1920"></canvas><script>
const g = document.getElementById('c').getContext('2d'), FR = new Map();
const img = s => { if (!FR.has(s)) FR.set(s, new Promise(ok => { const i = new Image(); i.onload = () => ok(i); i.src = s; })); return FR.get(s); };
let D;
const RUIDO = [0, 1, 2, 3, 4, 5].map(() => { const c = document.createElement('canvas'); c.width = 540; c.height = 390; const x = c.getContext('2d'), d = x.createImageData(540, 390);
  for (let i = 0; i < d.data.length; i += 4) { const v = Math.random() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); return c; });
window.init = async d => { D = d; await document.fonts.load('80px IS'); return true; };
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), eOut = k => 1 - Math.pow(1 - k, 3);
window.render = async t => {
  const k = Math.min(D.n, Math.max(1, Math.round(t * D.fps) + 1)), nn = String(k).padStart(5, '0');
  const [cam, scr] = await Promise.all([img(D.dir + '/cuadros_pro/' + nn + '.jpg'), img(D.dir + '/scr/' + nn + '.jpg')]);
  for (const key of [...FR.keys()]) if (+key.slice(-9, -4) < k - 2) FR.delete(key);
  g.fillStyle = '#000'; g.fillRect(0, 0, 1080, 1920);
  // cámara: bajada unos px para que la barra de Instagram no tape la cara; el hueco se rellena con la pared desenfocada
  const L = D.layout, camH = cam.height * 1080 / cam.width, OFF = L.top ?? D.bajar, CH = L.top != null ? L.top + camH : L.cam;
  g.save(); g.beginPath(); g.rect(0, 0, 1080, CH); g.clip();
  g.filter = 'blur(28px)'; g.drawImage(cam, 0, 0, cam.width, cam.height * (D.layout.franja ?? .2), -40, -40, 1160, OFF + 120); g.filter = 'none';
  const LK = D.look;
  if (LK) g.filter = 'brightness(' + LK.brillo + ') contrast(' + LK.contraste + ') saturate(' + LK.sat + ') sepia(' + LK.sepia + ') blur(' + (LK.suave || 0) + 'px)';
  g.drawImage(cam, 0, OFF, 1080, camH); g.filter = 'none';
  if (LK) {  // look Cine Pro (como la capa final del motor cine): viñeta + grano fino
    const vg = g.createRadialGradient(540, CH * .45, 120, 540, CH * .45, 760);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,' + LK.vineta + ')');
    g.fillStyle = vg; g.fillRect(0, 0, 1080, CH);
    g.globalAlpha = LK.grano; g.globalCompositeOperation = 'overlay'; g.drawImage(RUIDO[k % RUIDO.length], 0, 0, 1080, CH);
    g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
  }
  g.restore();
  // pantalla con zoom
  const y0 = CH + L.banda;
  if (L.pantalla === 'completa') g.drawImage(scr, 0, y0, 1080, 608);  // todo el tablero, 16:9
  else { const [cx, cy, w] = D.zoom[Math.min(k - 1, D.zoom.length - 1)], h = w * 810 / 1080; g.drawImage(scr, cx - w / 2, cy - h / 2, w, h, 0, y0, 1080, 810); }
  // subtítulo
  const s = D.subs.find(s => t >= s.a - .04 && t < s.fin);
  if (s) {
    const ki = eOut(clamp((t - s.a + .04) / .16));
    g.save(); g.globalAlpha = ki; g.filter = ki < 1 ? 'blur(' + ((1 - ki) * 6).toFixed(1) + 'px)' : 'none';
    g.fillStyle = '#fff'; g.font = '78px IS'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(s.txt, 540, CH + L.banda / 2 + (1 - ki) * 8); g.restore();
  }
  return true;
};
</script></body></html>`;

const srv = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]);
  if (u === '/metodo.html') { res.writeHead(200, { 'Content-Type': 'text/html' }); return res.end(PAGE); }
  const f = path.join(RAIZ, u);
  if (!f.startsWith(RAIZ) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': f.endsWith('.ttf') ? 'font/ttf' : 'image/jpeg' }); fs.createReadStream(f).pipe(res);
}).listen(0, '127.0.0.1');
await new Promise(r => srv.once('listening', r));
const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: [...(process.platform === 'linux' ? ['--no-sandbox'] : []), '--force-color-profile=srgb', '--hide-scrollbars'] });
const page = await browser.newPage();
await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
await page.goto(`http://127.0.0.1:${srv.address().port}/metodo.html`);
await page.evaluate(d => window.init(d), { n, fps, dir: rel, zoom, subs, bajar: cfg.bajar ?? 200, look: cfg.look ?? null, layout: { cam: 768, banda: 102, pantalla: 'zoom', ...(cfg.layout || {}) } });
const cuadro = async (t, tipo = 'jpeg') => { await page.evaluate(t => window.render(t), t); return page.screenshot({ type: tipo, ...(tipo === 'jpeg' ? { quality: 93, optimizeForSpeed: true } : {}) }); };
fs.mkdirSync(path.join(proy, 'salida'), { recursive: true });

if (opt('--stills')) {
  for (const t of opt('--stills').split(',').map(Number)) { const f = path.join(proy, 'salida', `metodo_${t.toFixed(2)}.png`); fs.writeFileSync(f, await cuadro(t, 'png')); console.log(f); }
  await browser.close(); srv.close(); process.exit(0);
}
const hasta = Math.min(dur, Number(opt('--hasta')) || dur), N = Math.round(hasta * fps);
const salida = opt('--hasta') ? path.join(proy, 'salida', 'metodo_prueba.mp4') : cfg.salida;
const M = cfg.musica, CAM_MOV = path.join(proy, 'corte/cam.mov');
let fc = `[1:a]aresample=48000,aformat=channel_layouts=stereo,${nivelar(medirArchivo(CAM_MOV), -16, -2)},atrim=0:${hasta.toFixed(3)},asplit=2[v][sc];` +
  `[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:${hasta.toFixed(3)},asetpts=PTS-STARTPTS,volume=${M.vol},afade=t=in:d=0.4,afade=t=out:st=${Math.max(0, hasta - 1.5).toFixed(2)}:d=1.5[m0];` +
  `[m0][sc]sidechaincompress=threshold=0.05:ratio=3:attack=10:release=300[m];[v][m]amix=inputs=2:normalize=0:duration=first[pre]`;
fc += `;[pre]${nivelar(medirGrafo(['-f', 'lavfi', '-i', 'anullsrc', '-i', CAM_MOV, '-ss', String(M.desde), '-i', path.resolve(proy, M.archivo)], fc, 'pre'), -14, -1)}[a]`;
const enc = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', FPS, '-i', '-', '-i', path.join(proy, 'corte/cam.mov'),
  '-ss', String(M.desde), '-i', path.resolve(proy, M.archivo), '-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-t', hasta.toFixed(3),
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-maxrate', '16M', '-bufsize', '32M', '-pix_fmt', 'yuv420p', '-r', FPS,
  '-c:a', 'aac', '-b:a', '192k', '-map_chapters', '-1', '-map_metadata', '-1', '-movflags', '+faststart', salida], { stdio: ['pipe', 'inherit', 'inherit'] });
enc.on('close', c => { if (c) { console.error('✗ ffmpeg', c); process.exit(1); } });
for (let i = 0; i < N; i++) {
  const buf = await cuadro(i / fps);
  if (!enc.stdin.write(buf)) await new Promise(r => enc.stdin.once('drain', r));
  if (i % 240 === 0) process.stdout.write(`  ${i}/${N}`);
}
enc.stdin.end(); await new Promise(r => enc.on('close', r));
await browser.close(); srv.close();
console.log(`\n✓ ${salida}  (${hasta.toFixed(1)} s, ${subs.length} subtítulos)`);
