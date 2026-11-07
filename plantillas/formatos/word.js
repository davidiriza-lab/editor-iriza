const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, ImageRun, AlignmentType, LevelFormat, Table, TableRow, TableCell,
  WidthType, ShadingType, PageBreak, BorderStyle, TableOfContents } = require('docx');
const D = JSON.parse(fs.readFileSync(__dirname + '/docdata.json', 'utf8'));
const SALIDA = process.argv[2];
const ANCHO = 6.5 * 96;  // px a 96 dpi para 6.5 in

const img = ([p, w, h], maxW = ANCHO, maxH = 8.3 * 96) => {
  let W = Math.min(maxW, w), H = W * h / w; if (H > maxH) { H = maxH; W = H * w / h; }
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
    children: [new ImageRun({ type: p.endsWith('.png') ? 'png' : 'jpg', data: fs.readFileSync(p), transformation: { width: Math.round(W), height: Math.round(H) } })] });
};
const p = (t, o = {}) => new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: t, ...o })] });
const b = (neg, t) => new Paragraph({ numbering: { reference: 'v', level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: neg, bold: true }), new TextRun(t)] });
const h1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, spacing: { after: 160 }, children: [new TextRun(t)] });
const h2 = (t, salto = true) => new Paragraph({ heading: HeadingLevel.HEADING_2, pageBreakBefore: salto, spacing: { after: 80 }, children: [new TextRun(t)] });
const borde = { style: BorderStyle.SINGLE, size: 4, color: 'D0D0D0' }, bordes = { top: borde, bottom: borde, left: borde, right: borde };
const tabla = (anchos, filas) => new Table({ width: { size: anchos.reduce((a, c) => a + c), type: WidthType.DXA }, columnWidths: anchos,
  rows: filas.map((f, i) => new TableRow({ tableHeader: i === 0, children: f.map((c, j) => new TableCell({ borders: bordes, width: { size: anchos[j], type: WidthType.DXA },
    shading: i === 0 ? { fill: '1F1F1F', type: ShadingType.CLEAR, color: 'auto' } : undefined, margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({ children: [new TextRun({ text: String(c), bold: i === 0, color: i === 0 ? 'FFFFFF' : '222222', size: 18 })] })] })) })) });

const F = D.familias, E = D.editores;
const nombreFam = id => F[id].nombre;
const nomEd = n => n === 'pizarra' ? 'Pizarra Pro' : String(n).endsWith('p') ? `Editor ${String(n).slice(0, -1)} · pantalla` : 'Editor ' + n;
const c = [];
// ---------- portada
c.push(new Paragraph({ heading: HeadingLevel.TITLE, spacing: { before: 2400, after: 200 }, children: [new TextRun('Plantillas y Editores')] }));
c.push(p('Catálogo de estilos de edición · actualizado el 24 de octubre de 2026', { color: '666666' }));
c.push(p(`${D.existentes.length} plantillas que ya usamos + ${E.length} formatos analizados fotograma por fotograma (50 de Formatos/1023, "Pizarra Pro" y 10 videos que corren DENTRO de una laptop o monitor, los "Editor N · pantalla"), agrupados en ${Object.keys(F).length} familias de estilo.`));
c.push(p('Cómo usarlo: pásale un video a Claude y di "edítalo con el Editor N" (o con el nombre de la plantilla). Cada plantilla tiene su carpeta con ESTILO.md, la hoja de fotogramas, la paleta y todos los fotogramas en alta resolución.', { color: '444444' }));
c.push(p('Carpetas: plantillas/formatos/editor-NN (y editor-NN-pantalla) · motor de edición: estilo-cine', { color: '888888', size: 18 }));
c.push(p('Cada formato tiene una GUIA.md escrita para Claude (qué es y cómo hacerlo paso a paso); el índice está en GUIA-FORMATOS.md.', { color: '888888', size: 18 }));
c.push(new Paragraph({ children: [new PageBreak()] }));
c.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('Índice')] }));
c.push(new TableOfContents('Índice', { hyperlink: true, headingStyleRange: '1-2' }));
c.push(p('(Si el índice sale vacío: clic derecho → Actualizar campo.)', { color: '999999', size: 16 }));

// ---------- tabla resumen
c.push(h1('Resumen de todas las plantillas'));
c.push(tabla([2200, 2600, 4560], [['Plantilla', 'Tipo', 'Para qué'], ...D.existentes.map(x => [x.nombre, x.tipo, x.texto[0].slice(0, 120) + (x.texto[0].length > 120 ? '…' : '')])]));
c.push(p(''));
c.push(tabla([1500, 2300, 2100, 3460], [['Nombre', 'Apodo', 'Familia', 'Para qué'], ...E.map(e => [e.nombre, e.apodo, nombreFam(e.familia), F[e.familia].para.slice(0, 110) + (F[e.familia].para.length > 110 ? '…' : '')])]));

// ---------- parte 1
c.push(h1('Parte 1 · Plantillas que ya usamos'));
c.push(p('Estas ya están hechas y probadas con tus videos.'));
D.existentes.forEach((x, i) => {
  c.push(h2(x.nombre, i > 0));
  c.push(p(x.tipo, { italics: true, color: '777777' }));
  x.texto.forEach(t => c.push(p(t)));
  x.imgs.forEach(im => c.push(img(im, ANCHO, 4.6 * 96)));
});

// ---------- parte 2: familias
c.push(h1('Parte 2 · Formatos analizados (Formatos/1023 + pantallas)'));
c.push(p('Cada video quedó como su propia plantilla con el nombre que le pusiste (Editor 1 … Editor 50) más un apodo. Cuando varios son el mismo estilo, comparten familia: la familia dice cómo se construye, y cada editor guarda sus detalles propios.'));
c.push(tabla([2400, 3000, 3960], [['Familia', 'Editores', 'Idea'], ...Object.entries(F).map(([id, f]) => [f.nombre, f.eds.map(nomEd).join(', '), f.idea.slice(0, 140) + (f.idea.length > 140 ? '…' : '')])]));
E.forEach(e => {
  const f = F[e.familia];
  c.push(h2(`${e.nombre} · ${e.apodo}`));
  const otros = f.eds.filter(n => n !== e.n).map(nomEd);
  c.push(p(`Familia: ${f.nombre}${otros.length ? ' (igual que ' + otros.join(', ') + ')' : ''} · ${e.dur} s · ${e.cortes} cortes · ${e.cuadros} fotogramas guardados`, { italics: true, color: '777777' }));
  c.push(img(e.hoja, ANCHO, 6.0 * 96));
  c.push(img(e.pal, 3.6 * 96, 1 * 96));
  c.push(b('Lo que se ve: ', e.detalle));
  c.push(b('Idea de la plantilla: ', f.idea));
  c.push(b('Texto: ', f.texto));
  c.push(b('Animación y ritmo: ', f.mov));
  c.push(b('Para qué te sirve: ', f.para));
  c.push(b('Cómo lo hacemos: ', f.motor));
  c.push(p(`Video: ${e.archivo}`, { color: '999999', size: 16 }));
  c.push(p(`Guía para Claude: ${e.guia}`, { color: '999999', size: 16 }));
});

const doc = new Document({
  styles: { default: { document: { run: { font: 'Helvetica Neue', size: 21 } } },
    paragraphStyles: [{ id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 30, bold: true, color: '111111' }, paragraph: { outlineLevel: 1 } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 40, bold: true, color: '111111' }, paragraph: { outlineLevel: 0 } }] },
  numbering: { config: [{ reference: 'v', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 220 } } } }] }] },
  features: { updateFields: true },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1000, bottom: 1000, left: 1440, right: 1440 } } }, children: c }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(SALIDA, buf); console.log('ok', (buf.length / 1e6).toFixed(1), 'MB'); });
