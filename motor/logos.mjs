// Descarga logos de la web y los guarda en PNG.
//   node motor/logos.mjs chatgpt claude gemini instagram ...
//     → assets/iconos/<nombre>.png        ícono oficial de la app (App Store, 1024 px, con fondo)
//     → assets/logos/<nombre>.png          logo solo, sin fondo, color de marca (Simple Icons)
//     → assets/logos/<nombre>_blanco.png   logo solo, sin fondo, en blanco
//   node motor/logos.mjs --url <link de imagen> <nombre>
//     → assets/imagenes/<nombre>.png       cualquier imagen (svg, webp, jpg, avif…) convertida a PNG
// Al final arma assets/muestrario.png con todo lo descargado para revisarlo de un vistazo.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import puppeteer from 'puppeteer-core';

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const A = d => { const p = path.join(RAIZ, 'assets', d); fs.mkdirSync(p, { recursive: true }); return p; };
const CHROME = process.env.CHROME || ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/local/bin/chromium'].find(f => fs.existsSync(f)) || 'google-chrome';  // Mac, Linux o Windows (WSL)
const REG = path.join(RAIZ, 'assets', 'logos.json');
const registro = fs.existsSync(REG) ? JSON.parse(fs.readFileSync(REG)) : {};
const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]/g, '');
const archivo = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9_-]+/g, '-').replace(/^-|-$/g, '');

// Cómo buscar cada marca cuando el nombre corto no basta (búsqueda en App Store / slug de Simple Icons)
const ALIAS = {
  chatgpt: { app: 'ChatGPT', vendedor: 'OpenAI', si: 'openai' },
  openai: { app: 'ChatGPT', vendedor: 'OpenAI', si: 'openai' },
  claude: { app: 'Claude by Anthropic', vendedor: 'Anthropic', si: 'claude' },
  anthropic: { app: 'Claude by Anthropic', vendedor: 'Anthropic', si: 'anthropic' },
  gemini: { app: 'Google Gemini', vendedor: 'Google', si: 'googlegemini' },
  whatsapp: { app: 'WhatsApp Messenger', vendedor: 'WhatsApp', si: 'whatsapp' },
  whatsappbusiness: { app: 'WhatsApp Business', vendedor: 'WhatsApp', si: 'whatsapp' },
  instagram: { app: 'Instagram', vendedor: 'Instagram', si: 'instagram' },
  facebook: { app: 'Facebook', vendedor: 'Meta', si: 'facebook' },
  messenger: { app: 'Messenger', vendedor: 'Meta', si: 'messenger' },
  threads: { app: 'Threads', vendedor: 'Instagram', si: 'threads' },
  manychat: { app: 'Manychat', vendedor: 'ManyChat', si: null },
  tiktok: { app: 'TikTok', vendedor: 'TikTok', si: 'tiktok' },
  youtube: { app: 'YouTube', vendedor: 'Google', si: 'youtube' },
  x: { app: 'X', vendedor: 'X Corp', si: 'x' },
  twitter: { app: 'X', vendedor: 'X Corp', si: 'x' },
  telegram: { app: 'Telegram Messenger', vendedor: 'Telegram', si: 'telegram' },
  perplexity: { app: 'Perplexity', vendedor: 'Perplexity', si: 'perplexity' },
  grok: { app: 'Grok', vendedor: 'X.AI', si: 'grok' },
  deepseek: { app: 'DeepSeek', vendedor: 'DeepSeek', si: 'deepseek' },
  copilot: { app: 'Microsoft Copilot', vendedor: 'Microsoft', si: 'githubcopilot' },
  notion: { app: 'Notion', vendedor: 'Notion', si: 'notion' },
  canva: { app: 'Canva', vendedor: 'Canva', si: 'canva' },
  capcut: { app: 'CapCut', vendedor: 'Bytedance', si: 'capcut' },
  elevenlabs: { app: 'ElevenLabs', vendedor: 'Eleven', si: 'elevenlabs' },
  gmail: { app: 'Gmail', vendedor: 'Google', si: 'gmail' },
  googledrive: { app: 'Google Drive', vendedor: 'Google', si: 'googledrive' },
  zoom: { app: 'Zoom Workplace', vendedor: 'Zoom', si: 'zoom' },
  spotify: { app: 'Spotify', vendedor: 'Spotify', si: 'spotify' },
  linkedin: { app: 'LinkedIn', vendedor: 'LinkedIn', si: null },
  slack: { app: 'Slack', vendedor: 'Slack', si: null },
  discord: { app: 'Discord', vendedor: 'Discord', si: 'discord' },
  calendly: { app: 'Calendly', vendedor: 'Calendly', si: 'calendly' },
  stripe: { app: 'Stripe Dashboard', vendedor: 'Stripe', si: 'stripe' },
  shopify: { app: 'Shopify', vendedor: 'Shopify', si: 'shopify' },
  hotmart: { app: 'Hotmart', vendedor: 'Hotmart', si: 'hotmart' },
  midjourney: { app: null, si: 'midjourney' },
  n8n: { app: null, si: 'n8n' },
  make: { app: 'Make', vendedor: 'Celonis', si: 'make' },
  zapier: { app: null, si: 'zapier' },
};

async function iconoApp(nombre, a) {
  if (a.app === null) return null;
  const q = a.app || nombre;
  const r = await (await fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(q)}&entity=software&country=mx&limit=15`)).json();
  const ok = r.results.filter(x => norm(x.trackName).includes(norm(q)) || norm(x.trackName).startsWith(norm(nombre)));
  const pick = ok.find(x => !a.vendedor || norm(x.sellerName).includes(norm(a.vendedor))) || ok[0];
  if (!pick) return null;
  const url = pick.artworkUrl512.replace(/\/\d+x\d+bb\.(jpg|png)$/, '/1024x1024bb.png');
  const buf = Buffer.from(await (await fetch(url)).arrayBuffer());
  fs.writeFileSync(path.join(A('iconos'), `${nombre}.png`), buf);
  return { app: pick.trackName, vendedor: pick.sellerName, url };
}

async function svgAPng(page, svg, salida, lado = 1024) {
  await page.setViewport({ width: lado, height: lado });
  await page.setContent(`<html><body style="margin:0;background:transparent"><div style="width:${lado}px;height:${lado}px;display:flex;align-items:center;justify-content:center">
    <div style="width:86%;height:86%">${svg.replace('<svg', '<svg width="100%" height="100%"')}</div></div></body></html>`);
  await page.screenshot({ path: salida, omitBackground: true });
}

async function logoSuelto(page, nombre, a) {
  const slug = a.si === undefined ? norm(nombre) : a.si, dir = A('logos');
  if (slug) {
    const color = await fetch(`https://cdn.simpleicons.org/${slug}`);
    if (color.ok) {
      await svgAPng(page, await color.text(), path.join(dir, `${nombre}.png`));
      await svgAPng(page, await (await fetch(`https://cdn.simpleicons.org/${slug}/white`)).text(), path.join(dir, `${nombre}_blanco.png`));
      return { simpleicons: slug };
    }
    // respaldo: el paquete de Simple Icons en jsDelivr (trae marcas que el CDN ya no sirve; vienen en negro)
    const r = await fetch(`https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/${slug}.svg`);
    if (r.ok) {
      const svg = await r.text();
      await svgAPng(page, svg, path.join(dir, `${nombre}.png`));
      await svgAPng(page, svg.replace('<svg', '<svg fill="#ffffff"'), path.join(dir, `${nombre}_blanco.png`));
      return { simpleicons: slug, fuente: 'jsdelivr' };
    }
  }
  // último recurso: recortar el logo del ícono de la app quitando su fondo liso
  const ic = path.join(A('iconos'), `${nombre}.png`);
  if (fs.existsSync(ic) && await quitarFondo(page, ic, path.join(dir, `${nombre}.png`), path.join(dir, `${nombre}_blanco.png`))) return { recortado_de: 'icono' };
  return null;
}

// Quita el fondo liso del ícono (color de la esquina), recorta al contenido y deja un margen.
// Devuelve false si el fondo no es liso (degradados): ahí no sirve.
async function quitarFondo(page, src, salida, salidaBlanco) {
  const data = 'data:image/png;base64,' + fs.readFileSync(src).toString('base64');
  await page.setViewport({ width: 400, height: 400 });
  await page.setContent('<html><body></body></html>');
  const r = await page.evaluate(async data => {
    const im = new Image(); im.src = data; await im.decode();
    const w = im.naturalWidth, h = im.naturalHeight, c = new OffscreenCanvas(w, h), g = c.getContext('2d'); g.drawImage(im, 0, 0);
    const d = g.getImageData(0, 0, w, h), p = d.data, at = (x, y) => (y * w + x) * 4;
    // color de fondo: mediana de un anillo a 6 % del borde (las esquinas de iOS pueden traer sombra)
    const m = Math.round(w * .06), mu = [];
    for (let k = m; k < w - m; k += 8) for (const [x, y] of [[k, m], [k, h - m], [m, k], [w - m, k]]) mu.push([p[at(x, y)], p[at(x, y) + 1], p[at(x, y) + 2]]);
    const med = i => mu.map(v => v[i]).sort((a, b) => a - b)[mu.length >> 1], bg = [med(0), med(1), med(2)];
    const dist = (i, c) => Math.hypot(p[i] - c[0], p[i + 1] - c[1], p[i + 2] - c[2]);
    if (mu.filter(v => Math.hypot(v[0] - bg[0], v[1] - bg[1], v[2] - bg[2]) > 40).length > mu.length * .15) return null;
    let x0 = w, y0 = h, x1 = 0, y1 = 0;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = at(x, y), dd = dist(i, bg), a = Math.max(0, Math.min(1, (dd - 18) / 50));
      if (a > 0 && (dd > 0)) {  // des-mezclar el borde con el fondo para que no quede halo
        for (let k = 0; k < 3; k++) p[i + k] = Math.max(0, Math.min(255, (p[i + k] - bg[k] * (1 - a)) / Math.max(a, .01)));
      }
      p[i + 3] = Math.round(255 * a);
      if (a > .5) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
    }
    if (x1 <= x0) return null;
    g.putImageData(d, 0, 0);
    const lado = Math.round(Math.max(x1 - x0, y1 - y0) * 1.16), out = new OffscreenCanvas(lado, lado), o = out.getContext('2d');
    o.drawImage(c, x0, y0, x1 - x0, y1 - y0, (lado - (x1 - x0)) / 2, (lado - (y1 - y0)) / 2, x1 - x0, y1 - y0);
    const toUrl = async cv => { const b = await cv.convertToBlob({ type: 'image/png' }); return new Promise(res => { const fr = new FileReader(); fr.onload = () => res(fr.result); fr.readAsDataURL(b); }); };
    const color = await toUrl(out);
    const od = o.getImageData(0, 0, lado, lado); for (let i = 0; i < od.data.length; i += 4) od.data[i] = od.data[i + 1] = od.data[i + 2] = 255;
    o.putImageData(od, 0, 0);
    return [color, await toUrl(out)];
  }, data);
  if (!r) return false;
  fs.writeFileSync(salida, Buffer.from(r[0].split(',')[1], 'base64'));
  fs.writeFileSync(salidaBlanco, Buffer.from(r[1].split(',')[1], 'base64'));
  return true;
}

async function desdeUrl(page, url, nombre) {
  const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/141 Safari/537.36' } });
  if (!res.ok) throw new Error(`No se pudo bajar (${res.status}): ${url}`);
  const tipo = res.headers.get('content-type') || '', buf = Buffer.from(await res.arrayBuffer()), salida = path.join(A('imagenes'), `${nombre}.png`);
  if (tipo.includes('svg') || buf.slice(0, 200).toString().includes('<svg')) { await svgAPng(page, buf.toString(), salida, 2048); return salida; }
  // cualquier otro formato: Chrome lo decodifica y lo guardamos en PNG conservando transparencia
  const dataUrl = `data:${tipo || 'image/*'};base64,${buf.toString('base64')}`;
  await page.setContent(`<html><body style="margin:0;background:transparent"><img id="i" src="${dataUrl}" style="display:block"></body></html>`);
  const [w, h] = await page.evaluate(() => new Promise(r => { const i = document.getElementById('i'); const f = () => r([i.naturalWidth, i.naturalHeight]); i.complete ? f() : i.onload = f; }));
  if (!w) throw new Error('El archivo no es una imagen que se pueda leer.');
  await page.setViewport({ width: w, height: h });
  await page.screenshot({ path: salida, omitBackground: true });
  return salida;
}

async function muestrario(page) {
  const items = [];
  for (const d of ['iconos', 'logos']) {
    const dir = path.join(RAIZ, 'assets', d); if (!fs.existsSync(dir)) continue;
    for (const f of fs.readdirSync(dir).filter(f => /\.(png|svg)$/.test(f)).sort())
      items.push({ f: 'data:image/' + (f.endsWith('svg') ? 'svg+xml' : 'png') + ';base64,' + fs.readFileSync(path.join(dir, f)).toString('base64'), n: `${d}/${f}` });
  }
  const html = items.map(x => `<div style="width:170px;text-align:center;font:12px -apple-system;color:#ccc"><div style="height:130px;display:flex;align-items:center;justify-content:center;background:${x.n.includes('_blanco') ? '#333' : '#eee'};border-radius:10px"><img src="${x.f}" style="max-width:110px;max-height:110px;${x.n.startsWith('iconos') ? 'border-radius:22%' : ''}"></div>${x.n}</div>`).join('');
  await page.setViewport({ width: 1100, height: 400 });
  await page.setContent(`<body style="margin:0;padding:16px;background:#1a1a1a;display:flex;flex-wrap:wrap;gap:14px">${html}</body>`);
  await page.screenshot({ path: path.join(RAIZ, 'assets', 'muestrario.png'), fullPage: true });
}

const args = process.argv.slice(2);
if (!args.length) { console.log('Uso: ./video logo chatgpt claude gemini …   |   ./video logo --url <link> <nombre>'); process.exit(0); }
const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: [...(process.platform === 'linux' ? ['--no-sandbox'] : [])] });
const page = await browser.newPage();
try {
  if (args[0] === '--url') {
    const n = archivo(args[2] || 'imagen'), f = await desdeUrl(page, args[1], n);
    registro[n] = { url: args[1] }; console.log('✓', f);
  } else {
    for (const n of args) {
      const nombre = norm(n), a = ALIAS[nombre] || {};
      const ic = await iconoApp(nombre, a).catch(() => null), lg = await logoSuelto(page, nombre, a).catch(() => null);
      registro[nombre] = { ...(ic || {}), ...(lg || {}) };
      console.log(`${ic || lg ? '✓' : '✗'} ${nombre.padEnd(14)} ${ic ? `ícono: ${ic.app} (${ic.vendedor})` : 'sin ícono de app'}  ·  ${lg ? 'logo sin fondo ✓' : 'sin logo suelto'}`);
    }
  }
  fs.writeFileSync(REG, JSON.stringify(registro, null, 1));
  await muestrario(page);
  console.log('Muestrario →', path.join(RAIZ, 'assets', 'muestrario.png'));
} finally { await browser.close(); }
