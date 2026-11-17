// Captura un HTML local a PNG con el mismo navegador del render: node estilo-cine/_captura_html.mjs <html> <png> <ancho> <alto>
import puppeteer from '../motor/node_modules/puppeteer-core/lib/puppeteer/puppeteer-core.js';
const [html, png, w, h] = process.argv.slice(2);
const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true, args: ['--allow-file-access-from-files'] });
const pg = await b.newPage(); await pg.setViewport({ width: +w, height: +h });
await pg.goto('file://' + html); await new Promise(r => setTimeout(r, 900));
await pg.screenshot({ path: png }); await b.close();
