// Pantalla doble "Original / Editado por Claude": dos videos 16:9 apilados en un reel 1080x1920.
// Uso: node estilo-cine/doble.mjs <original.mov> <editado.mp4> <salida.mp4> [--etiqueta "C8256.MP4 · SIN TOCAR"] [--modelo "Claude Opus 5.5"]
// El audio sale del editado. El original se ve tal cual (sin color, sin zoom), con los mismos cortes.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';
import puppeteer from '../motor/node_modules/puppeteer-core/lib/puppeteer/puppeteer-core.js';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const [orig, edit, salida] = args;
const etiqueta = opt('--etiqueta', `${path.basename(orig).toUpperCase()} · SIN TOCAR`);
const modelo = opt('--modelo', 'Claude Opus 5.5');
const CHROME = process.env.CHROME || ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/local/bin/chromium'].find(f => fs.existsSync(f)) || 'google-chrome';  // Mac, Linux o Windows (WSL)

// medidas del marco (dentro de la zona segura: arriba >262, abajo <1540)
const M = { x: 60, w: 960, h: 540, y1: 345, y2: 990, r: 24 };

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:1080px;height:1920px;background:transparent;overflow:hidden;font-family:"Helvetica Neue",Helvetica,Arial,sans-serif}
#c{position:absolute;inset:0}
.t{position:absolute;left:0;right:0;text-align:center;font-weight:700;font-size:60px;letter-spacing:-1.5px;color:#f2efe9}
.t b{color:#d97757;font-weight:700}
.chip{position:absolute;left:${M.x + 22}px;top:${M.y1 + 20}px;padding:9px 16px;border-radius:10px;background:rgba(10,10,10,.62);
  color:#ececec;font:500 22px Menlo,monospace;letter-spacing:1px}
</style></head><body><canvas id="c" width="1080" height="1920"></canvas>
<div class="t" style="top:${M.y1 - 92}px">Original</div>
<div class="t" style="top:${M.y2 - 92}px">Editado por <b>${modelo}</b></div>
<div class="chip">${etiqueta}</div>
<script>
const g = document.getElementById('c').getContext('2d'), M = ${JSON.stringify(M)};
// fondo oscuro con luz cálida suave
const bg = g.createRadialGradient(540, 900, 100, 540, 900, 1200); bg.addColorStop(0, '#221d18'); bg.addColorStop(1, '#0c0b0a');
g.fillStyle = bg; g.fillRect(0, 0, 1080, 1920);
// huecos de las pantallas
g.globalCompositeOperation = 'destination-out';
for (const y of [M.y1, M.y2]) { g.beginPath(); g.roundRect(M.x, y, M.w, M.h, M.r); g.fill(); }
g.globalCompositeOperation = 'source-over';
g.lineWidth = 2; g.strokeStyle = 'rgba(255,255,255,.16)'; g.beginPath(); g.roundRect(M.x, M.y1, M.w, M.h, M.r); g.stroke();
g.lineWidth = 3; g.strokeStyle = '#d97757'; g.shadowColor = 'rgba(217,119,87,.45)'; g.shadowBlur = 30;
g.beginPath(); g.roundRect(M.x - 1, M.y2 - 1, M.w + 2, M.h + 2, M.r + 1); g.stroke();
</script></body></html>`;

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'doble-'));
const fHtml = path.join(tmp, 'marco.html'), fPng = path.join(tmp, 'marco.png');
fs.writeFileSync(fHtml, html);
const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: [...(process.platform === 'linux' ? ['--no-sandbox'] : []), '--force-color-profile=srgb', '--hide-scrollbars'] });
const page = await browser.newPage();
await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
await page.goto('file://' + fHtml);
await page.screenshot({ path: fPng, omitBackground: true });
await browser.close();

const dur = spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', edit]).stdout.toString().trim();
const fc = [
  `color=c=#0c0b0a:s=1080x1920:r=24000/1001:d=${dur}[bg]`,
  `[0:v]scale=${M.w}:${M.h},setsar=1,fps=24000/1001,tpad=stop_mode=clone:stop_duration=5[o]`,
  `[1:v]scale=${M.w}:${M.h},setsar=1,fps=24000/1001[e]`,
  `[bg][o]overlay=${M.x}:${M.y1}:shortest=0[a]`,
  `[a][e]overlay=${M.x}:${M.y2}[b]`,
  `[b][2:v]overlay=0:0,format=yuv420p[v]`,
].join(';');
const r = spawnSync('ffmpeg', ['-y', '-v', 'error', '-i', orig, '-i', edit, '-loop', '1', '-i', fPng, '-filter_complex', fc,
  '-map', '[v]', '-map', '1:a', '-t', dur, '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-maxrate', '16M', '-bufsize', '32M',
  '-c:a', 'copy', '-map_chapters', '-1', '-map_metadata', '-1', '-movflags', '+faststart', salida], { stdio: 'inherit' });
if (r.status) process.exit(1);
console.log(`✓ ${salida}  (${(+dur).toFixed(1)} s)`);
