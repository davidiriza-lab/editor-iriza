// Render del estilo "cine": cine.json + voz → salida/cine_<modo>.mp4
// Uso: node estilo-cine/render.mjs proyectos/<nombre> [--perfil redes|4k] [--modo codigo|hf] [--stills 1.2,3.4] [--hasta 8] [--reanudar]
//      … --validar   solo revisa el cine.json (claves, opciones, fps, cuadros, palabras contra la voz) y sale
//      … --forzar    renderiza aunque la validación marque errores
//      … --capas <carpeta> [--paso 0.2]   cuadros con y sin texto para estilo-cine/revisar.py (texto sobre la cara, zona segura)
// Perfil (estilo-cine/perfiles.json): redes = 1080x1920; 4k = 2160x3840 por bloques, HEVC por hardware y prioridad baja.
// En 4K conviene revisar con --perfil redes (rápido) y dejar --perfil 4k solo para el render final.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import http from 'node:http';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { medirArchivo, medirGrafo, nivelar } from './volumen.mjs';
import puppeteer from '../motor/node_modules/puppeteer-core/lib/puppeteer/puppeteer-core.js';

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CHROME = process.env.CHROME || ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/local/bin/chromium'].find(f => fs.existsSync(f)) || 'google-chrome';  // Mac, Linux o Windows (WSL)
const args = process.argv.slice(2), proy = path.resolve(args[0] || '');
const opt = k => { const i = args.indexOf(k); return i > 0 ? args[i + 1] : null; };
const modo = opt('--modo') || 'codigo';
const cfg = JSON.parse(fs.readFileSync(path.join(proy, 'cine.json')));
const W = cfg.lienzo?.w || 1080, H = cfg.lienzo?.h || 1920, FPS = String(cfg.fps || 30), fps = eval(FPS);
const PERFILES = JSON.parse(fs.readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)), 'perfiles.json')));
// fuera de Mac no hay codificador por hardware de Apple (videotoolbox): se usa x264/x265
if (process.platform !== 'darwin') for (const p of Object.values(PERFILES)) {
  p.video = p.video.map(a => a === 'hevc_videotoolbox' ? 'libx265' : a === 'h264_videotoolbox' ? 'libx264' : a);
  const i = p.video.indexOf('-allow_sw'); if (i >= 0) p.video.splice(i, 2);
}
const nPerfil = opt('--perfil') || cfg.perfil || 'redes', PF = PERFILES[nPerfil];
if (!PF) { console.error(`✗ perfil "${nPerfil}" no existe (usa: ${Object.keys(PERFILES).join(', ')})`); process.exit(1); }
const ES = PF.escala;
if (PF.prioridad) try { os.setPriority(PF.prioridad); } catch {}
if (cfg.persona && ES > 1) {
  const d4 = path.join(proy, PF.cuadros), n4 = fs.existsSync(d4) ? fs.readdirSync(d4).filter(f => f.endsWith('.jpg')).length : 0;
  if (n4 < cfg.persona.n) { console.error(`✗ faltan los cuadros 4K (${PF.cuadros}: ${n4}/${cfg.persona.n}). Corre primero: python3 estilo-cine/prep4k.py ${path.relative(RAIZ, proy)}`); process.exit(1); }
}
console.log(`  perfil: ${PF.nombre} → ${W * ES}x${H * ES}`);
const voz = JSON.parse(fs.readFileSync(path.join(proy, 'voz/palabras.json')));
const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9ñ]/g, '');
const limpio = s => s.replace(/[.,;:…]+$/u, '').replace(/^[¿¡]+/, '');

// ---- validación: lo que el motor no conoce ya no se pierde en silencio ----
// Todo error detiene el render ANTES de gastar tiempo (se puede seguir con --forzar). Las listas salen del propio código
// (cine.js y este archivo), así que no hay un esquema aparte que mantener: clave nueva en el motor = clave válida aquí.
const AQUI = path.dirname(fileURLToPath(import.meta.url));
const errores = [], avisos = [];
{
  const yo = fs.readFileSync(fileURLToPath(import.meta.url), 'utf8'), fuente = fs.readFileSync(path.join(AQUI, 'cine.js'), 'utf8') + '\n' + yo;
  const NOMBRES = new Set(fuente.match(/[A-Za-z_$\u00C0-\u024F][\w$\u00C0-\u024F]*/g));
  const TEXTOS = new Set([...fuente.matchAll(/'([^'\\\n]{1,48})'|"([^"\\\n]{1,48})"|`([^`\\\n$]{1,48})`/g)].map(m => m[1] ?? m[2] ?? m[3]));
  const DE_RAIZ = new Set([...yo.matchAll(/\bcfg\.([A-Za-z_]\w*)/g)].map(m => m[1])), DE_GRUPO = new Set([...yo.matchAll(/\bgp\.([A-Za-z_]\w*)/g)].map(m => m[1]));
  const LIBRES = new Set(['imagenes', 'logos']);   // mapas cuyos nombres pone cada proyecto
  const OPCIONES = new Set(['visual', 'tipo', 'trans', 'tema', 'textoTema', 'paleta', 'anim', 'modo', 'estilo', 'forma', 'efecto', 'look']);   // claves cuyo valor es una opción del motor
  const dist = (a, b) => { const d = [...Array(a.length + 1)].map((_, i) => [i]); for (let j = 1; j <= b.length; j++) d[0][j] = j;
    for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++) d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] !== b[j - 1])); return d[a.length][b.length]; };
  const parecido = (k, de) => { let m = null, dm = 3; for (const n of de) { if (Math.abs(n.length - k.length) > 2) continue; const d = dist(k.toLowerCase(), n.toLowerCase()); if (d < dm) { dm = d; m = n; } } return m ? ` (¿quisiste decir "${m}"?)` : ''; };
  const anda = (o, ruta) => {
    if (Array.isArray(o)) return o.forEach((x, i) => anda(x, `${ruta}[${i + 1}]`));
    if (!o || typeof o !== 'object') return;
    for (const [k, v] of Object.entries(o)) {
      const r = ruta ? `${ruta}.${k}` : k;
      if (!NOMBRES.has(k)) errores.push(`${r}: el motor no conoce la clave "${k}"${parecido(k, NOMBRES)}`);
      if (typeof v === 'string' && OPCIONES.has(k) && !TEXTOS.has(v) && !NOMBRES.has(v)) errores.push(`${r}: "${v}" no es una opción del motor para "${k}"${parecido(v, TEXTOS)}`);
      if (!LIBRES.has(k)) anda(v, r);
    }
  };
  anda(cfg, '');
  for (const k of Object.keys(cfg)) if (NOMBRES.has(k) && !DE_RAIZ.has(k)) errores.push(`${k}: render.mjs no lee esa clave en la raíz del cine.json (va dentro de otra sección o falta pasarla a la página)`);
  if (!Array.isArray(cfg.escenas) || !cfg.escenas.length) errores.push('cine.json no tiene "escenas"');
  (cfg.escenas || []).forEach((s, i) => {
    if (!Array.isArray(s.grupos)) return errores.push(`escenas[${i + 1}]: falta "grupos" (si la escena no lleva texto: "grupos": [] e "inicio": <segundo>)`);
    if (!s.grupos.length && s.inicio == null && i > 0) errores.push(`escenas[${i + 1}]: sin grupos y sin "inicio": no se sabe cuándo empieza`);
    s.grupos.forEach((gp, j) => {
      if (!Array.isArray(gp.lineas)) errores.push(`escenas[${i + 1}].grupos[${j + 1}]: falta "lineas"`);
      for (const k of Object.keys(gp)) if (NOMBRES.has(k) && !DE_GRUPO.has(k)) errores.push(`escenas[${i + 1}].grupos[${j + 1}].${k}: render.mjs no pasa esa clave de grupo a la página (agrégala donde se arman los grupos o quítala)`);
    });
  });
  // imagen y voz tienen que medir lo mismo: fps del cine.json = fps del corte, y los cuadros que dice = los que hay
  const fVoz = path.join(proy, cfg.voz || 'voz/voz.mp3');
  if (!fs.existsSync(fVoz)) errores.push(`no está la voz: ${cfg.voz || 'voz/voz.mp3'}`);
  else if (cfg.persona) {
    const sv = spawnSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate,nb_frames', '-of', 'csv=p=0', fVoz], { encoding: 'utf8' }).stdout.trim();
    const trc = spawnSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_transfer', '-of', 'csv=p=0', fVoz], { encoding: 'utf8' }).stdout.trim().split(',')[0];
    if (['arib-std-b67', 'smpte2084'].includes(trc) && !cfg.hdr_ok) errores.push(`${cfg.voz} está marcado como HDR (${trc === 'smpte2084' ? 'PQ' : 'HLG'}): sin convertir a Rec.709 la persona se ve lavada. Convierte el crudo (bin/sdr; metodo_corte.py ya lo hace solo) y vuelve a cortar. Si ya está convertido y solo quedó la etiqueta, pon "hdr_ok": true en el cine.json`);
    if (sv) {
      const [r, nf] = sv.split(','), [a, b] = r.split('/').map(Number), fv = a / (b || 1);
      if (Math.abs(fv - fps) > .01) errores.push(`fps: el cine.json dice ${FPS} y ${cfg.voz} está a ${r}: la imagen y la voz se desfasan. Pon "fps": "${r}"`);
      if (Number(nf) && Math.abs(Number(nf) - cfg.persona.n) > 2) errores.push(`persona.n = ${cfg.persona.n}, pero ${cfg.voz} tiene ${nf} cuadros`);
    }
    for (const d of [...new Set([cfg.persona.cuadros, cfg.persona.mascaras, cfg.persona.crudos || 'cuadros'])].filter(Boolean)) {
      const dd = path.join(proy, d), hay = fs.existsSync(dd) ? fs.readdirSync(dd).filter(f => /\.(jpg|png)$/.test(f)).length : 0;
      if (hay < cfg.persona.n) errores.push(`${d}: hay ${hay} cuadros y persona.n pide ${cfg.persona.n}${hay ? '' : ' (corre preparar.py; si ya limpiaste el proyecto, se regeneran desde corte/)'}`);
    }
  }
}
const alto = () => {
  avisos.forEach(a => console.warn(`  ⚠ ${a}`));
  if (!errores.length) return;
  console.error(`\n✗ ${errores.length} problema${errores.length > 1 ? 's' : ''} en ${path.relative(RAIZ, proy)}/cine.json:`); errores.forEach(e => console.error(`   · ${e}`));
  if (!args.includes('--forzar')) { console.error('  No se renderiza hasta corregirlo (o agrega --forzar si es a propósito).'); process.exit(1); }
  console.error('  --forzar: se renderiza de todos modos.'); errores.length = 0;
};
alto();
if (args.includes('--validar')) { console.log('✓ cine.json válido: el motor conoce todas las claves y opciones; fps y cuadros coinciden con el corte'); }

// ---- asignar cada palabra del guion visual a su palabra de la voz ----
let iw = 0;
const ESTILO = { '-': 'chico', '*': 'resalte', '~': 'contorno' };
const escenas = cfg.escenas.map((s, iEsc) => ({
  ...s,
  grupos: (s.grupos || []).map(gp => ({
    y: gp.y, x: gp.x, lim: gp.lim, escala: gp.escala, maxTam: gp.maxTam, resaltar: gp.resaltar, frase: gp.frase, velo: !!gp.velo, detras: !!gp.detras, sombra: !!gp.sombra, etiqueta: gp.etiqueta || null, estrecho: !!gp.estrecho, tinta: !!gp.tinta, a0: voz[iw] ? voz[iw].a : 0,
    lineas: gp.lineas.map(l => {
      const estilo = ESTILO[l[0]] || 'grande', txt = ESTILO[l[0]] ? l.slice(1) : l;
      return {
        estilo, palabras: txt.split(/\s+/).map(tk => {
          // "palabra|como se muestra" cambia lo que se ve; "palabra|" la oculta
          const [oye, ve] = tk.includes('|') ? tk.split('|') : [tk, tk];
          const w = voz[iw++];
          if (!w || norm(w.t) !== norm(oye)) errores.push(`escenas[${iEsc + 1}]: el guion dice "${oye}" y en ese lugar la voz dice ${w ? `"${w.t}" (palabra ${iw} de voz/palabras.json, ${w.a.toFixed(2)} s)` : 'nada: ya no quedan palabras'}`);
          const wv = w || voz.at(-1);
          return { txt: (gp.frase ? ve : limpio(ve)).replace(/_/g, ' '), a: wv.a, b: wv.b };  // "un|a_tu" → se ve "a tu"
        }).filter(p => p.txt !== ''),
      };
    }).filter(l => l.palabras.length),  // un grupo puede quedar oculto entero (lo dibuja otra capa, p. ej. el anillo)
  })),
}));
if (errores.length > 6) { const n = errores.length; errores.length = 6; errores.push(`… y ${n - 6} palabras más (desde la primera que falla, todo lo demás queda corrido)`); }
if (iw < voz.length) avisos.push(`el guion visual usa ${iw} palabras y la voz tiene ${voz.length}: las últimas ${voz.length - iw} ("${voz.slice(iw, iw + 4).map(w => w.t).join(' ')}…") salen sin texto`);
alto();
if (args.includes('--validar')) { console.log('✓ el guion visual coincide palabra por palabra con la voz'); process.exit(0); }
const dur = voz.at(-1).b + (cfg.cola ?? .8);
escenas.forEach((s, i) => {
  s.ini = s.inicio ?? (i === 0 ? 0 : s.grupos[0].a0);  // escena sin voz: "inicio" explícito
  s.grupos.forEach(gp => gp.ini = gp.a0);
});
escenas.forEach((s, i) => {
  s.fin = i < escenas.length - 1 ? escenas[i + 1].ini : dur;
  s.grupos.forEach((gp, j) => { gp.fin = j < s.grupos.length - 1 ? s.grupos[j + 1].ini : s.fin; if (gp.detras && s.detrasDura) gp.fin = Math.min(s.fin, Math.max(gp.fin, gp.ini + s.detrasDura)); });
});
const marca = k => { const v = (cfg.marcas || {})[k]; if (typeof v === 'number') return v; const w = voz.find(w => norm(w.t) === norm(v || '')); return w ? w.a + (k === 'tap' ? .12 : 0) : -9; };
const rel = `/${path.relative(RAIZ, proy)}`;
escenas.forEach(s => { if (s.clip) s.clip = { ...s.clip, dir: `${rel}/${s.clip.dir}` }; });
const EDIT = { modo, escenas, dur, fps, handle: cfg.handle, nombre: cfg.nombre, acento: cfg.acento || null, acentoTexto: cfg.acentoTexto || null, fuenteGrande: cfg.fuenteGrande || null, fuenteChica: cfg.fuenteChica || null, paleta: cfg.paleta || null, suave: cfg.suave || null, apretado: cfg.apretado || null, contorno: cfg.contorno || null, pop: cfg.pop || null, subtitulo: cfg.subtitulo || null, limpio: cfg.limpio || null, caras: cfg.caras || null, caraH: cfg.caraH || null, hfDir: `${rel}/hf`, marca: { impacto: marca('impacto'), tap: marca('tap') }, cortes: cfg.cortes || [],
  persona: cfg.persona ? { cuadros: `${rel}/${ES > 1 ? PF.cuadros : cfg.persona.cuadros}`, mascaras: `${rel}/${cfg.persona.mascaras}`, n: cfg.persona.n, fondo: cfg.persona.fondo || 'real', crudos: `${rel}/${cfg.persona.crudos || 'cuadros'}`,
    bajar: cfg.persona.bajar || 0, zoomAlt: cfg.persona.zoomAlt ?? 1.13, fondoImg: cfg.persona.fondoImg || null } : null,
  bio: cfg.bio || null, anillos: cfg.anillos || [], titular: cfg.titular || null, top5: cfg.top5 || null,
  logos: Object.fromEntries(Object.entries(cfg.logos || {}).map(([k, v]) => [k, `${rel}/${v}`])),
  imagenes: Object.fromEntries(Object.entries(cfg.imagenes || {}).map(([k, v]) => [k, `${rel}/${v}`])) };

// ---- servidor local (los módulos ES no cargan desde file://) ----
const TIPOS = { '.html': 'text/html', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.json': 'application/json' };
const srv = http.createServer((req, res) => {
  const f = path.join(RAIZ, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(RAIZ) || !fs.existsSync(f)) { if (!/favicon/.test(req.url)) console.warn(`  ⚠ no existe el archivo que pide la página: ${decodeURIComponent(req.url.split('?')[0])}`); res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TIPOS[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
}).listen(0, '127.0.0.1');
await new Promise(r => srv.once('listening', r));
const base = `http://127.0.0.1:${srv.address().port}`;

// La Mac no se duerme mientras dure el render: en reposo Chrome deja de responder a media captura y el render se quedaba
// colgado (medido el 12-nov-2026: reposo de mantenimiento cada 5 min con la tapa cerrada). caffeinate sale solo al terminar.
if (process.platform === 'darwin') try { spawn('caffeinate', ['-i', '-w', String(process.pid)], { stdio: 'ignore' }).unref(); } catch {}
let browser, page, sinTexto = false;
const SIN_TEXTO = () => { for (const C of [window.CanvasRenderingContext2D, window.OffscreenCanvasRenderingContext2D]) if (C) { C.prototype.fillText = function () {}; C.prototype.strokeText = function () {}; } };
const lanzar = async () => {
  browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: [...(process.platform === 'linux' ? ['--no-sandbox'] : []), '--force-color-profile=srgb', '--hide-scrollbars', ...(process.platform === 'darwin' ? ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] : [])], protocolTimeout: 60000 });
  page = await browser.newPage();
  page.on('console', m => { if (['error', 'warning', 'warn'].includes(m.type()) && !/favicon|status of 404/.test(m.text())) console.log('  [página]', m.text()); });
  page.on('pageerror', e => console.log('  [página]', e.message));
  await page.setViewport({ width: W, height: H, deviceScaleFactor: ES });
  if (sinTexto) await page.evaluateOnNewDocument(SIN_TEXTO);   // página en la que dibujar texto no hace nada (ni en lienzos auxiliares ni en cachés)
};
await lanzar();
const abrir = async () => {  // (re)carga la página: en 4K se hace en cada bloque para soltar la memoria de imágenes y texturas
  await page.goto(`${base}/estilo-cine/cine.html?w=${W}&h=${H}&e=${ES}`);
  await page.waitForFunction(() => window.init);
  const faltan = await page.evaluate(e => window.init(e), EDIT);
  if (faltan.length) console.warn('  ⚠ imágenes que no cargaron:', faltan);
};
await abrir();
// Si Chrome deja de responder, se relanza y se repite ESE cuadro (el dibujo depende solo del tiempo, así que sale idéntico).
const foto = async (t, o) => {
  for (let intento = 0; ; intento++) {
    try { await page.evaluate(t => window.render(t), t); return await page.screenshot(o); }
    catch (e) {
      if (intento >= 3) throw e;
      console.warn(`\n  ⚠ Chrome no respondió en ${t.toFixed(2)} s (${String(e.message).slice(0, 70)}): se relanza y se repite el cuadro`);
      try { await Promise.race([browser.close(), new Promise(r => setTimeout(r, 5000))]); } catch {}
      try { browser.process()?.kill('SIGKILL'); } catch {}
      await lanzar(); await abrir();
    }
  }
};
const cuadro = (t, tipo = 'jpeg') => foto(t, { type: tipo, ...(tipo === 'jpeg' ? { quality: PF.jpeg, optimizeForSpeed: true } : {}) });
fs.mkdirSync(path.join(proy, 'salida'), { recursive: true });
const fin = async () => { try { await Promise.race([browser.close(), new Promise(r => setTimeout(r, 8000))]); } catch {} srv.close(); };

if (opt('--stills')) {
  for (const t of opt('--stills').split(',').map(Number)) {
    const f = path.join(proy, 'salida', `${modo}${ES > 1 ? '_' + nPerfil : ''}_${t.toFixed(2)}.png`); fs.writeFileSync(f, await cuadro(t, 'png')); console.log(f);
  }
  await fin(); process.exit(0);
}

// ---- --capas <carpeta>: los mismos instantes CON y SIN texto, para revisar.py ----
// La diferencia entre las dos capas es exactamente el texto que se ve (lo que queda detrás de la persona no cuenta). Con eso
// revisar.py mide texto sobre la cara, fuera de la zona segura o cortado por el borde, sin depender de leer letras (OCR).
if (opt('--capas')) {
  const dirC = path.resolve(opt('--capas')), paso = Number(opt('--paso')) || .2, ts = new Set();
  for (let t = 0; t < dur; t += paso) ts.add(+t.toFixed(3));
  escenas.forEach(s => s.grupos.forEach(gp => { if (gp.fin - gp.ini > .12) ts.add(+Math.max(gp.ini, gp.fin - .06).toFixed(3)); }));   // el instante con todas las palabras del grupo a la vista
  const T = [...ts].filter(t => t < dur).sort((a, b) => a - b);
  for (const capa of ['con', 'sin']) {
    fs.rmSync(path.join(dirC, capa), { recursive: true, force: true }); fs.mkdirSync(path.join(dirC, capa), { recursive: true });
    if (capa === 'sin') { sinTexto = true; await page.evaluateOnNewDocument(SIN_TEXTO); await abrir(); }
    for (let i = 0; i < T.length; i++) {
      fs.writeFileSync(path.join(dirC, capa, `${String(i + 1).padStart(5, '0')}.jpg`), await foto(T[i], { type: 'jpeg', quality: 90, optimizeForSpeed: true }));
      if (i % 20 === 0) process.stdout.write(`\r  capa ${capa} texto: ${i}/${T.length}`);
    }
  }
  fs.writeFileSync(path.join(dirC, 'tiempos.json'), JSON.stringify({ w: W, h: H, fps, dur, t: T,
    escenas: escenas.map((s, i) => ({ i: i + 1, ini: +s.ini.toFixed(3), fin: +s.fin.toFixed(3), visual: s.visual || 'persona', trans: s.trans || null })),
    grupos: escenas.flatMap((s, i) => s.grupos.map((gp, j) => ({ escena: i + 1, grupo: j + 1, ini: +gp.ini.toFixed(3), fin: +gp.fin.toFixed(3), detras: gp.detras, texto: gp.lineas.map(l => l.palabras.map(p => p.txt).join(' ')).join(' / ') }))) }));
  console.log(`\r✓ ${T.length} instantes con y sin texto → ${dirC}`);
  await fin(); process.exit(0);
}

// ---- audio: voz + música (con hueco antes del golpe) + efectos ----
const hasta = Math.min(dur, Number(opt('--hasta')) || dur), N = Math.ceil(hasta * fps);
const ff = ['-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', '__LISTA__', '-i', path.join(proy, cfg.voz || 'voz/voz.mp3')];
// música opcional: sin archivo (p. ej. sin cuenta de Epidemic) se renderiza solo con voz y efectos
const m = { desde: 0, vol: .2, vol_drop: .2, ...(cfg.musica || {}) }, musicaOk = cfg.musica?.archivo && fs.existsSync(path.join(proy, cfg.musica.archivo));
if (cfg.musica?.archivo && !musicaOk) console.warn(`  ⚠ no está la música ${cfg.musica.archivo}: el video sale sin música (ver audio/LEEME.md)`);
if (musicaOk) ff.push('-ss', String(m.desde), '-i', path.join(proy, m.archivo)); else { ff.push('-f', 'lavfi', '-t', '1', '-i', 'anullsrc=r=48000:cl=stereo'); m.vol = m.vol_drop = 0; }
// efectos automáticos según la transición de cada escena
const SFX = path.join(RAIZ, 'estilo-cine/sfx'), AUTO = {
  whip: ['whoosh_rapido.mp3', .35, .45], glitch: ['glitch_corto.mp3', .25, .4], flash: ['whoosh_grave.mp3', .8, .5],
  zoom: ['whoosh_rapido.mp3', .35, .45], drop: ['boom.mp3', .5, .75], pan: ['whoosh_grave.mp3', .8, .45] };
// el efecto nunca empieza antes de que termine la última palabra de la escena anterior (no tapa la voz)
const finPrevio = t => Math.max(0, ...voz.filter(w => w.a < t - .02).map(w => w.b));
const auto = cfg.sfx_auto ? escenas.filter(s => s.trans && AUTO[s.trans]).map(s => {
  const [f, pico, vol] = AUTO[s.trans], en = Math.max(s.ini + (s.sfxDesfase || 0), finPrevio(s.ini) + pico + .02);
  return { f: path.join(SFX, f), en, pico, vol };
}) : [];
const fxTodos = [...auto, ...(cfg.sfx || []).map(s => ({ ...s, f: path.resolve(proy, s.f) }))].map(s => ({ ...s, ini: s.en - s.pico }));
const fx = fxTodos.filter(s => fs.existsSync(s.f)), faltaFx = [...new Set(fxTodos.filter(s => !fs.existsSync(s.f)).map(s => path.basename(s.f)))];
if (faltaFx.length) console.warn(`  ⚠ faltan efectos (${faltaFx.join(', ')}): se omiten. Corre: python3 audio/efectos_basicos.py`);
fx.forEach(s => ff.push('-i', s.f));
const D = hasta.toFixed(3), tDrop = m.drop ?? escenas.find(s => s.trans === 'drop')?.ini ?? 0;
const [s0, s1] = m.silencio || [-1, -1];
let fc = `[1:a]aresample=48000,aformat=channel_layouts=stereo,${nivelar(medirArchivo(path.join(proy, cfg.voz || 'voz/voz.mp3')), -16, -2)},apad,atrim=0:${D},asplit=2[v][vsc];`;
fc += `[2:a]aresample=48000,atrim=0:${D},asetpts=PTS-STARTPTS,volume='if(between(t,${s0},${s1}),0,if(lt(t,${tDrop}),${m.vol},${m.vol_drop}))${(m.bajar || []).map(([a, b, k]) => `*if(between(t,${a},${b}),${k},1)`).join('')}':eval=frame,afade=t=in:d=0.25,afade=t=out:st=${Math.max(0, hasta - 1.2).toFixed(2)}:d=1.2[m0];`;
const duck = { threshold: .03, ratio: 5, ...(m.ducking || {}) };  // cuánto se agacha la música cuando hablas
fc += `[m0][vsc]sidechaincompress=threshold=${duck.threshold}:ratio=${duck.ratio}:attack=10:release=300[m];`;
const mezcla = ['[v]', '[m]'];
fx.forEach((s, i) => {
  const k = i + 3, recorte = Math.max(0, -s.ini), ms = Math.round(Math.max(0, s.ini) * 1000);
  fc += `[${k}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start=${recorte.toFixed(3)},asetpts=PTS-STARTPTS,adelay=${ms}|${ms},volume=${s.vol}[s${i}];`;
  mezcla.push(`[s${i}]`);
});
fc += `${mezcla.join('')}amix=inputs=${mezcla.length}:normalize=0:duration=first,atrim=0:${D}[pre]`;
const salida = cfg.salida && !opt('--hasta') ? path.resolve(proy, cfg.salida).replace(/(\.mp4)$/i, ES > 1 ? ` (${PF.nombre})$1` : '$1') : path.join(proy, 'salida', `cine_${modo}${ES > 1 ? '_' + nPerfil : ''}.mp4`);
// ---- video por bloques: cada bloque se codifica a su archivo (se puede reanudar si algo se cae) ----
fs.mkdirSync(path.dirname(salida), { recursive: true });   // "salida" relativa = relativa a la carpeta del proyecto
const dirB = path.join(proy, 'salida', `_bloques_${nPerfil}`); fs.mkdirSync(dirB, { recursive: true });
const tamB = PF.bloque || N, bloques = [];
for (let i0 = 0, k = 0; i0 < N; i0 += tamB, k++) bloques.push({ k, i0, i1: Math.min(N, i0 + tamB), f: path.join(dirB, `b${String(k).padStart(4, '0')}.mp4`) });
if (!opt('--reanudar')) for (const b of bloques) fs.rmSync(b.f, { force: true });
// Chrome entrega JPG (BT.601 de rango completo): se convierte al estándar de entrega, Rec.709 de rango de video, con sus
// etiquetas. Antes el MP4 salía "yuvj420p / bt470bg" y un reproductor que no lee etiquetas lo mostraba con ~4 % de error de
// color y contraste. zscale convierte sin sesgo (viene en ffmpeg-full); sin él, swscale en modo preciso. Igual que comun.py.
const conZ = / zscale /.test(spawnSync('ffmpeg', ['-hide_banner', '-filters'], { encoding: 'utf8' }).stdout || '');
const VF_ENTREGA = (conZ ? 'zscale=min=470bg:rin=full:m=709:r=limited' : 'scale=in_color_matrix=bt601:in_range=full:out_color_matrix=bt709:out_range=tv:flags=bicubic+accurate_rnd+full_chroma_int')
  + ',format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv';
const t0 = Date.now();
for (const b of bloques) {
  if (fs.existsSync(b.f)) { console.log(`  bloque ${b.k + 1}/${bloques.length} ya estaba (reanudar)`); continue; }
  if (b.k > 0 && PF.bloque) await abrir();
  const tmpF = b.f.replace(/\.mp4$/, '.tmp.mp4');
  const enc = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', FPS, '-i', '-', '-vf', VF_ENTREGA, ...PF.video, '-r', FPS, '-an', tmpF], { stdio: ['pipe', 'inherit', 'inherit'] });
  let err = null; enc.on('close', c => { if (c) err = c; });
  for (let i = b.i0; i < b.i1; i++) {
    const buf = await cuadro(i / fps);
    if (err) { console.error(`\n✗ ffmpeg terminó con error (${err})`); process.exit(1); }
    if (!enc.stdin.write(buf)) await new Promise(r => enc.stdin.once('drain', r));
    if (i % 30 === 0) process.stdout.write(`\r  cuadro ${i}/${N}  (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
  }
  enc.stdin.end();
  await new Promise(r => enc.on('close', r));
  if (err) { console.error(`\n✗ ffmpeg terminó con error (${err})`); process.exit(1); }
  fs.renameSync(tmpF, b.f);
}
await fin();
// ---- unir bloques (sin recodificar) + audio ----
const lista = path.join(dirB, 'lista.txt'); fs.writeFileSync(lista, bloques.map(b => `file '${b.f.replace(/'/g, "'\\''")}'`).join('\n'));
ff[ff.indexOf('__LISTA__')] = lista;
fc += `;[pre]${nivelar(medirGrafo(ff.slice(3), fc, 'pre'), -14, -1)}[a]`;
ff.push('-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-t', D, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-map_chapters', '-1', '-map_metadata', '-1', '-movflags', '+faststart', salida);
const mux = spawn('ffmpeg', ff, { stdio: ['ignore', 'inherit', 'inherit'] });
const cod = await new Promise(r => mux.on('close', r));
if (cod) { console.error(`\n✗ ffmpeg (unión) terminó con error (${cod})`); process.exit(1); }
fs.rmSync(dirB, { recursive: true, force: true });
console.log(`\n✓ ${salida}  (${PF.nombre}, ${hasta.toFixed(1)} s, ${N} cuadros, ${((Date.now() - t0) / 1000).toFixed(0)} s de render)`);
process.exit(0);   // salida explícita: sin esto el proceso podía quedarse vivo después del ✓ (había scripts que lo mataban a mano)
