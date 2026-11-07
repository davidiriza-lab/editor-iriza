// Render automático: guion.json + voz (palabras con tiempos) -> salida/video.mp4
// Uso: node motor/render.mjs proyectos/<nombre> [--stills 1.2,3.4] [--hasta 8]
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer-core';

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CHROME = process.env.CHROME || ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/local/bin/chromium'].find(f => fs.existsSync(f)) || 'google-chrome';  // Mac, Linux o Windows (WSL)
const args = process.argv.slice(2), proy = path.resolve(args[0] || '');
const opt = k => { const i = args.indexOf(k); return i > 0 ? args[i + 1] : null; };
if (!fs.existsSync(path.join(proy, 'guion.json'))) { console.error('No encuentro guion.json en', proy); process.exit(1); }

const cfg = JSON.parse(fs.readFileSync(path.join(RAIZ, 'config.json')));
const guion = JSON.parse(fs.readFileSync(path.join(proy, 'guion.json')));
const vozDir = path.join(proy, 'voz'), wordsF = path.join(vozDir, 'palabras.json');
if (!fs.existsSync(wordsF)) { console.error('Falta la voz. Corre primero: ./video voz', path.basename(proy)); process.exit(1); }
const palabras = JSON.parse(fs.readFileSync(wordsF));
const { ancho: W, alto: H, fps, cola } = cfg.video;

const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9ñ]/g, '');
const limpiar = s => s.replace(/^[«(]+/, '').replace(/[.,;:»)]+$/, '');

function buscaImg(ref) {
  if (!ref) return null;
  const cands = /[./]/.test(ref) ? [path.resolve(proy, ref), path.join(RAIZ, 'assets', ref), path.join(RAIZ, 'assets', ref + '.png')]
    : ['png', 'jpg', 'jpeg', 'webp', 'svg'].flatMap(e => [path.join(proy, 'iconos', `${ref}.${e}`), path.join(RAIZ, 'assets/iconos', `${ref}.${e}`)]);
  const f = cands.find(c => fs.existsSync(c));
  if (!f) { console.warn('  ⚠ no encontré la imagen:', ref); return null; }
  return pathToFileURL(f).href;
}

// ---------- tiempos de cada pantalla ----------
const dur = palabras.at(-1).fin + cola;
const pants = guion.pantallas.map((p, i) => {
  const ws = palabras.filter(w => w.pantalla === i);
  if (!ws.length) throw new Error(`La pantalla ${i + 1} (${p.tipo}) no tiene "voz".`);
  return { ...p, ws, inicio: i === 0 ? 0 : Math.max(0, ws[0].inicio - .02) };
});
pants.forEach((p, i) => { p.fin = i + 1 < pants.length ? pants[i + 1].inicio : dur; });
pants.forEach((p, i) => {
  if (p.transicion === 'luz' || (p.transicion !== false && p.tipo !== 'gancho' && i > 0 && pants[i - 1].tipo === 'gancho')) p.luz = true;
  if (p.tipo !== 'gancho') p.img = buscaImg(p.img);
});

// gancho: cada palabra/ícono aparece cuando la voz la dice
for (const p of pants.filter(p => p.tipo === 'gancho')) {
  let ptr = 0, last = p.inicio;
  const cuando = w => { const j = p.ws.findIndex((x, k) => k >= ptr && norm(x.texto) === norm(w)); if (j < 0) return null; ptr = j + 1; return p.ws[j].inicio; };
  p.lineas = (p.lineas || [p.voz]).map(l => {
    const grande = l.includes('**');
    const toks = (l.replace(/\*\*/g, '').match(/\{[^}]+\}|\S+/g) || []).map(tk => {
      const m = tk.match(/^\{([^@}]+)(?:@([^}]+))?\}$/);
      if (m) {
        const [, nom, en] = m, emoji = !/^[\w-]+$/.test(nom);
        let t = en ? (p.ws.find(x => norm(x.texto) === norm(en))?.inicio ?? last) : last + .05;
        last = Math.max(last, t);
        return emoji ? { texto: nom, emoji: true, t } : { img: buscaImg(nom), texto: nom, t };
      }
      const t = cuando(tk) ?? last; last = t; return { texto: tk, t };
    });
    return { grande, toks };
  });
}

// portada: cuándo aparece el CTA
for (const p of pants.filter(p => p.tipo === 'portada' && p.cta)) {
  const clave = norm(p.cta_en || p.cta.split(/\s+/)[0]);
  p.ctaT = p.ws.find(w => norm(w.texto) === clave)?.inicio ?? p.inicio + (p.fin - p.inicio) * .6;
}

// etiquetas (subtítulo de 1–3 palabras encima de la tarjeta)
const etiquetas = [];
for (const p of pants.filter(p => p.tipo !== 'gancho' && p.etiquetas !== false)) {
  let cur = null;
  const cerrar = () => { if (cur) etiquetas.push(cur); cur = null; };
  p.ws.forEach((w, k) => {
    if (!cur) cur = { texto: '', inicio: k === 0 ? p.inicio : w.inicio - .02, n: 0 };
    cur.texto += (cur.n ? ' ' : '') + limpiar(w.texto); cur.n++; cur.ult = w;
    const largo = w.texto.replace(/[^\p{L}\d]/gu, '').length > 3, punt = /[.,;:?!]$/.test(w.texto);
    if (punt || cur.n >= 3 || cur.texto.length > 15 || (w.fin - cur.inicio >= .42 && largo)) cerrar();
  });
  cerrar();
}
etiquetas.forEach((e, i) => {
  const sig = etiquetas[i + 1], p = pants.find(p => e.inicio >= p.inicio && e.inicio < p.fin);
  e.fin = sig && sig.inicio < p.fin + 1e-6 ? sig.inicio : p.fin;
  delete e.ult; delete e.n;
});

const EDIT = { W, H, fps, dur, etiquetas, pantallas: pants.map(({ ws, ...p }) => p) };
fs.mkdirSync(path.join(proy, 'salida'), { recursive: true });
fs.writeFileSync(path.join(proy, 'salida', 'edit.json'), JSON.stringify(EDIT, null, 1));

// ---------- dibujar ----------
const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: [...(process.platform === 'linux' ? ['--no-sandbox'] : []), '--allow-file-access-from-files', '--force-color-profile=srgb', '--hide-scrollbars'] });
const page = await browser.newPage();
await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(path.join(RAIZ, 'motor/plantilla.html')).href);
const faltan = await page.evaluate(e => window.init(e), EDIT);
if (faltan.length) console.warn('  ⚠ imágenes que no cargaron:', faltan);
const cuadro = async (t, tipo = 'jpeg') => { await page.evaluate(t => window.render(t), t); return page.screenshot({ type: tipo, ...(tipo === 'jpeg' ? { quality: 93, optimizeForSpeed: true } : {}) }); };

if (opt('--stills')) {
  for (const t of opt('--stills').split(',').map(Number)) {
    const f = path.join(proy, 'salida', `still_${t.toFixed(2)}.png`); fs.writeFileSync(f, await cuadro(t, 'png')); console.log(f);
  }
  await browser.close(); process.exit(0);
}

const hasta = Math.min(dur, Number(opt('--hasta')) || dur), N = Math.ceil(hasta * fps);
const salida = path.join(proy, 'salida', 'video.mp4');
const mus = guion.musica || cfg.audio.musica, musF = mus ? path.resolve(RAIZ, mus) : null;
const ff = ['-y', '-v', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(fps), '-i', '-', '-i', path.join(vozDir, 'voz.mp3')];
let fc = `[1:a]aresample=48000,loudnorm=I=-16:TP=-1.5,apad[v]`;
if (musF && fs.existsSync(musF)) {
  ff.push('-stream_loop', '-1', '-i', musF);
  fc += `;[2:a]aresample=48000,loudnorm=I=${-16 + cfg.audio.musica_db}:TP=-6,afade=t=out:st=${(hasta - .8).toFixed(2)}:d=.8[m];[v][m]amix=inputs=2:normalize=0[mix];[mix]loudnorm=I=${cfg.audio.lufs}:TP=-1[a]`;
} else fc += `;[v]loudnorm=I=${cfg.audio.lufs}:TP=-1[a]`;
ff.push('-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-t', hasta.toFixed(3),
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(fps), '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', salida);
const enc = spawn('ffmpeg', ff, { stdio: ['pipe', 'inherit', 'inherit'] });
const t0 = Date.now();
for (let i = 0; i < N; i++) {
  const buf = await cuadro(i / fps);
  if (!enc.stdin.write(buf)) await new Promise(r => enc.stdin.once('drain', r));
  if (i % 60 === 0) process.stdout.write(`\r  cuadro ${i}/${N}  (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
}
enc.stdin.end();
await new Promise(r => enc.on('close', r));
await browser.close();
console.log(`\n✓ ${salida}  (${hasta.toFixed(1)} s, ${N} cuadros, ${((Date.now() - t0) / 1000).toFixed(0)} s de render)`);
