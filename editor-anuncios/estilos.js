// Estilos de las fichas (plantillas/formatos/editor-NN/ESTILO.md) construidos como componentes del overlay.
// Se carga después del script principal: usa C, W, H, U, V, THEMES y los helpers (css, prog, eOut, eInOut, back, lerp, pop, icon, rnd).
// Un estilo por anuncio: 36 Brutalista Neón · 16 Tarjetas Anthropic · 7 Split hoja rayada · 11 Manuscrito amarillo ·
// 44 Podcast verde · 10 Testimonio cinemático · 14 Franja cinemascope · 5 Tipografía roja editorial.

const px = n => n * U + "px";
const wordsHtml = (words, f) => words.map((w, i) => `<span data-w="${i}" style="display:inline-block;${f(w, i)}">${w.t}</span>`).join(" ");
const seqIdx = (list, t) => { let k = -1; list.forEach((x, i) => { if (t >= x.at) k = i; }); return k; };   // última entrada ya dicha

// ---------- 36 · Brutalista Neón ----------
// Franja negra arriba con titular condensado en mayúsculas; una palabra en verde neón tachada.
C.band = {
  make(el, c) { const h = (c.h || .24) * H; css(el, { left: 0, top: 0, width: W + "px", height: h + "px", background: c.bg || "#040509", overflow: "hidden" });
    el.innerHTML = `<div data-in style="position:absolute;left:${px(42)};right:${px(42)};top:50%;transform:translateY(-50%);text-align:${c.align || "left"};font-family:'Bebas Neue','League Gothic',Impact,sans-serif;font-size:${px(c.size || 150)};line-height:.92;letter-spacing:.01em;color:#e6e6df;text-transform:uppercase">
      ${c.lines.map((l, i) => `<div data-l="${i}" style="position:relative;${l.neon ? "color:#c6ff2e" : ""}">${l.t}${l.strike ? `<span data-strike style="position:absolute;left:-2%;top:50%;height:${px(12)};width:104%;background:#c6ff2e;transform-origin:left;transform:scaleX(0)"></span>` : ""}</div>`).join("")}</div>`; },
  draw(el, c, t) { const a = eOut(prog(t, c.start, c.start + .35)), b = c.hold ? 0 : eInOut(prog(t, c.end - .25, c.end));
    css(el, { transform: `translateY(${(1 - a) * -100 - b * 100}%)` });
    c.lines.forEach((l, i) => { const n = el.querySelector(`[data-l="${i}"]`); pop(n, t, l.at, { dx: -40, dy: 0, d: .22 });
      const s = n.querySelector("[data-strike]"); if (s) s.style.transform = `scaleX(${eOut(prog(t, l.strikeAt ?? l.at + .45, (l.strikeAt ?? l.at + .45) + .25))})`; }); },
};
// Pantalla negra (o naranja) con UNA palabra itálica condensada por golpe, al ritmo de la voz.
C.golpe = {
  make(el, c) { el.className = "full"; css(el, { width: W + "px", height: H + "px", background: c.bg || "#040509" });
    el.innerHTML = c.words.map((w, i) => `<div data-g="${i}" style="position:absolute;left:0;right:0;top:${(c.y || .42) * H}px;text-align:center;font-family:'Bebas Neue','League Gothic',Impact,sans-serif;font-size:${px(w.size || 260)};line-height:.9;color:${w.color || (c.bg && c.bg !== "#040509" ? "#040509" : "#e6e6df")};transform:skewX(-9deg);text-transform:uppercase;opacity:0">${w.t}</div>`).join(""); },
  draw(el, c, t) { const b = c.hold ? 0 : prog(t, c.end - .12, c.end); css(el, { opacity: 1 - b });
    const k = seqIdx(c.words, t);
    c.words.forEach((w, i) => { const n = el.querySelector(`[data-g="${i}"]`); if (i !== k) { n.style.opacity = 0; return; }
      const p = prog(t, w.at, w.at + .14); css(n, { opacity: 1, transform: `skewX(-9deg) scale(${lerp(1.25, 1, eOut(p)) * (1 + .025 * Math.min(4, t - w.at))}) translateX(${Math.sin(t * .9) * 6 * U}px)`, filter: `blur(${(1 - eOut(p)) * 10 * U}px)` }); }); },
};

// ---------- 16 · Tarjetas Anthropic ----------
// Fondo carbón, etiqueta naranja espaciada, tarjetas 2x2 con cifra/palabra que entra una a una, titular serif con palabra itálica naranja subrayada a mano.
C.grid = {
  make(el, c) { el.className = "full"; css(el, { width: W + "px", height: H + "px", background: "#11120d", color: "#e2e2df" });
    const n = c.cards.length, cols = n <= 2 ? 1 : 2, gw = .86 * W, cw = cols === 1 ? gw : (gw - 28 * U) / 2, ch = (c.cardH || 250) * U;
    const underline = `<svg data-ul viewBox="0 0 300 24" preserveAspectRatio="none" style="position:absolute;left:-2%;bottom:-${px(10)};width:104%;height:${px(20)}"><path d="M4 16 C 60 6, 120 20, 170 12 S 260 8, 296 14" fill="none" stroke="#c36b58" stroke-width="5" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"/></svg>`;
    el.innerHTML = `<div data-k style="position:absolute;left:0;right:0;top:${.09 * H}px;text-align:center;font:600 ${px(26)} Inter,sans-serif;letter-spacing:.3em;text-transform:uppercase;color:#c36b58">${c.kicker || ""}</div>
      ${c.cards.map((k, i) => `<div data-c="${i}" style="position:absolute;left:${(W - gw) / 2 + (i % cols) * (cw + 28 * U)}px;top:${(c.top || .17) * H + Math.floor(i / cols) * (ch + 28 * U)}px;width:${cw}px;height:${ch}px;box-sizing:border-box;padding:${px(28)} ${px(30)};border-radius:${px(22)};background:#1e1c1b;border:1px solid #3a3734;opacity:0">
        <div style="font:500 ${px(22)} Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#908f8e">${k.label || ""}</div>
        <div data-v style="margin-top:${px(10)};font:700 ${px(k.size || 86)}/1 'DM Serif Display','Instrument Serif',serif;color:#e2e2df">${k.num != null ? "0" : k.t}</div>
        ${k.sub ? `<div style="margin-top:${px(10)};font:400 ${px(24)} Inter,sans-serif;color:#908f8e">${k.sub}</div>` : ""}</div>`).join("")}
      ${c.title ? `<div data-t style="position:absolute;left:${.07 * W}px;right:${.07 * W}px;top:${(c.titleTop || .64) * H}px;text-align:center;font:400 ${px(c.titleSize || 84)}/1.08 'DM Serif Display','Instrument Serif',serif;opacity:0">
        ${c.title.replace(/\*([^*]+)\*/g, (_, w) => `<span style="position:relative;display:inline-block;font-family:'Instrument Serif',serif;font-style:italic;color:#c36b58">${w}${underline}</span>`)}</div>` : ""}
      ${(c.bars || []).map((b, i) => `<div data-b="${i}" style="position:absolute;left:${.1 * W}px;width:${.8 * W}px;top:${(c.barsTop || .80) * H + i * 70 * U}px;opacity:0"><div style="font:500 ${px(24)} Inter,sans-serif;color:#908f8e;margin-bottom:${px(8)}">${b.label}</div><div style="height:${px(10)};border-radius:${px(5)};background:#2a2826"><div data-f style="height:100%;width:0;border-radius:${px(5)};background:#c36b58"></div></div></div>`).join("")}`; },
  draw(el, c, t) { fullIO(el, Object.assign({ inFx: "fade", outFx: "fade" }, c), t); pop(el.querySelector("[data-k]"), t, c.start + .1, { dy: 10 });
    c.cards.forEach((k, i) => { const n = el.querySelector(`[data-c="${i}"]`); pop(n, t, k.at, { dy: 30, d: .4 }); if (t > k.at + .4) n.style.transform = `translateY(${Math.sin(t * 1.3 + i) * 5 * U}px) scale(${1 + .01 * Math.min(4, t - k.at)})`;
      if (k.num != null) n.querySelector("[data-v]").textContent = (k.prefix || "") + Math.round(lerp(0, k.num, eOut(prog(t, k.at + .1, k.at + 1.1)))).toLocaleString("es-MX") + (k.suffix || ""); });
    const tt = el.querySelector("[data-t]"); if (tt) { pop(tt, t, c.titleAt, { dy: 24, d: .45 }); if (t > c.titleAt + .45) tt.style.transform = `scale(${1 + .015 * Math.min(4, t - c.titleAt)}) translateY(${Math.sin(t * .9) * 4 * U}px)`; const ul = tt.querySelector("[data-ul] path"); if (ul) ul.setAttribute("stroke-dashoffset", 100 * (1 - eOut(prog(t, c.titleAt + .5, c.titleAt + 1.0)))); }
    (c.bars || []).forEach((b, i) => { const n = el.querySelector(`[data-b="${i}"]`); pop(n, t, b.at, { dy: 16 }); n.querySelector("[data-f]").style.width = (b.frac * 100 * eOut(prog(t, b.at + .2, b.at + 1.2))) + "%"; }); },
};

// ---------- 7 · Split hoja rayada ----------
// Arriba 40 %: hoja rayada con un gráfico que cambia con cada idea; abajo la persona. La etiqueta del subtítulo vive en la unión (preset "label").
C.split = {
  make(el, c) { const h = (c.h || .40) * H; css(el, { left: 0, top: 0, width: W + "px", height: h + "px", overflow: "hidden", background: "#eeeeec",
      backgroundImage: `repeating-linear-gradient(0deg, transparent 0 ${px(54)}, rgba(49,48,47,.16) ${px(54)} ${px(56)})`, backgroundPosition: `0 ${px(20)}` });
    el.innerHTML = `<div style="position:absolute;left:${px(70)};top:0;bottom:0;width:${px(3)};background:rgba(161,117,97,.55)"></div>` +
      c.items.map((it, i) => `<div data-i="${i}" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:${px(18)};padding:${px(40)} ${px(80)} ${px(90)};box-sizing:border-box;text-align:center;opacity:0">
        ${it.icon ? `<div style="width:${px(150)};height:${px(150)};border-radius:50%;background:#1e1a18;color:#eeeeec;display:grid;place-items:center"><div style="width:48%;height:48%">${icon(it.icon, 1.8)}</div></div>` : ""}
        ${it.stamp ? `<div style="transform:rotate(-6deg);border:${px(6)} solid #a17561;color:#a17561;border-radius:${px(14)};padding:${px(10)} ${px(26)};font:800 ${px(64)} Inter,sans-serif;letter-spacing:.06em;text-transform:uppercase">${it.stamp}</div>` : ""}
        ${it.t ? `<div style="font:800 ${px(it.size || 66)}/1.05 Inter,sans-serif;color:#1e1a18">${it.t}</div>` : ""}
        ${it.sub ? `<div style="font:500 ${px(30)} Inter,sans-serif;color:#675535">${it.sub}</div>` : ""}</div>`).join("") +
      `<div style="position:absolute;left:0;right:0;bottom:0;height:${px(6)};background:#1e1a18"></div>`; },
  draw(el, c, t) { const a = eOut(prog(t, c.start, c.start + .4)), b = c.hold ? 0 : eInOut(prog(t, c.end - .3, c.end)); css(el, { transform: `translateY(${(1 - a) * -100 - b * 100}%)` });
    const k = seqIdx(c.items, t);
    c.items.forEach((it, i) => { const n = el.querySelector(`[data-i="${i}"]`); if (i !== k) { n.style.opacity = 0; return; }
      const p = eOut(prog(t, it.at, it.at + .3)); css(n, { opacity: p, transform: `translateY(${(1 - p) * 30 * U}px) scale(${lerp(.94, 1, p)})` }); }); },
};

// ---------- 11 · Manuscrito amarillo ----------
// Frase manuscrita sola sobre negro (blanco + palabra clave amarilla); los subtítulos van con el preset "hand".
C.manuscrito = {
  make(el, c) { el.className = "full"; css(el, { width: W + "px", height: H + "px", background: "#030202" });
    el.innerHTML = `<div style="position:absolute;left:${.08 * W}px;right:${.08 * W}px;top:${(c.y || .40) * H}px;text-align:center;font:400 ${px(c.size || 104)}/1.15 Noteworthy,'Bradley Hand','Marker Felt',cursive;color:#fff">
      ${wordsHtml(c.words, w => `${w.key ? "color:#f5b547;" : ""}opacity:0`)}</div>`; },
  draw(el, c, t) { fullIO(el, Object.assign({ inFx: "fade", outFx: "fade", inDur: .2, outDur: .2 }, c), t);
    el.firstElementChild.style.transform = `translate(${Math.sin(t * .8) * 10 * U}px, ${Math.cos(t * .6) * 8 * U}px) scale(${1 + .012 * Math.min(4, t - c.start)})`;
    el.querySelectorAll("[data-w]").forEach((n, i) => { const p = eOut(prog(t, c.words[i].at, c.words[i].at + .2)); css(n, { opacity: p, transform: `rotate(${(1 - p) * -4}deg) scale(${lerp(.8, 1, p)})` }); }); },
};

// ---------- 44 · Podcast verde ----------
// Pantalla verde bosque con rayas finas y una palabra gigante por golpe (sans bold) + línea chica serif itálica. El metraje va en blanco y negro (E.vf).
C.verde = {
  make(el, c) { el.className = "full"; css(el, { width: W + "px", height: H + "px", background: c.bg || "#154833", backgroundImage: `repeating-linear-gradient(0deg, transparent 0 ${px(7)}, rgba(255,255,255,.07) ${px(7)} ${px(8)})` });
    el.innerHTML = c.words.map((w, i) => `<div data-g="${i}" style="position:absolute;left:${px(40)};right:${px(40)};top:${(c.y || .36) * H}px;text-align:center;opacity:0">
      ${w.small ? `<div style="font:italic 400 ${px(44)} 'Instrument Serif',serif;color:#f9faf9;margin-bottom:${px(10)}">${w.small}</div>` : ""}
      <div style="font:900 ${px(w.size || 190)}/.95 Anton,Inter,sans-serif;color:${w.color || "#f9faf9"};text-transform:uppercase;letter-spacing:-.01em;overflow-wrap:anywhere">${w.t}</div></div>`).join(""); },
  draw(el, c, t) { const b = c.hold ? 0 : prog(t, c.end - .1, c.end); css(el, { opacity: 1 - b }); const k = seqIdx(c.words, t);
    c.words.forEach((w, i) => { const n = el.querySelector(`[data-g="${i}"]`); if (i !== k) { n.style.opacity = 0; return; }
      const p = eOut(prog(t, w.at, w.at + .12)); css(n, { opacity: 1, transform: `scale(${lerp(1.18, 1, p) * (1 + .022 * Math.min(4, t - w.at))}) translateY(${Math.sin(t * 1.1) * 5 * U}px)` }); }); },
};

// ---------- 10 · Testimonio cinemático ----------
// Sobre el pecho: línea chica blanca + palabra gigante condensada con degradado amarillo→naranja→rojo; íconos tipo emoji que entran desde abajo.
C.gradword = {
  make(el, c) { css(el, { left: 0, top: 0, width: W + "px", height: H + "px", pointerEvents: "none" }); el._noFull = true;
    el.innerHTML = c.words.map((w, i) => `<div data-g="${i}" style="position:absolute;left:${px(30)};right:${px(30)};top:${(w.y || c.y || .50) * H}px;text-align:center;opacity:0">
      ${w.small ? `<div style="font:600 ${px(40)} Inter,sans-serif;color:#fff;text-shadow:0 4px 18px rgba(0,0,0,.6);margin-bottom:${px(4)}">${w.small}</div>` : ""}
      <div style="font:400 ${px(w.size || 230)}/.92 'Bebas Neue','League Gothic',Impact,sans-serif;text-transform:uppercase;letter-spacing:.01em;background:linear-gradient(180deg,#ffd24a 0%,#ff7a1a 55%,#d8232a 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 8px 24px rgba(0,0,0,.55))">${w.t}</div></div>`).join("") +
      (c.icons || []).map((ic, i) => `<div data-ic="${i}" style="position:absolute;left:${ic.x * W}px;top:${ic.y * H}px;width:${px(150)};height:${px(150)};margin:${px(-75)} 0 0 ${px(-75)};border-radius:${px(36)};background:linear-gradient(145deg,#ffe28a,#f0a034 60%,#c86a16);box-shadow:0 ${px(18)} ${px(40)} rgba(0,0,0,.45), inset 0 ${px(-8)} ${px(14)} rgba(0,0,0,.25), inset 0 ${px(6)} ${px(10)} rgba(255,255,255,.5);color:#5a2d05;display:grid;place-items:center;opacity:0"><div style="width:54%;height:54%">${icon(ic.icon, 2.2)}</div></div>`).join(""); },
  draw(el, c, t) { const k = seqIdx(c.words, t);
    c.words.forEach((w, i) => { const n = el.querySelector(`[data-g="${i}"]`); const fin = c.words[i + 1] ? c.words[i + 1].at : c.end; if (i !== k || t > fin) { n.style.opacity = 0; return; }
      const p = eOut(prog(t, w.at, w.at + .18)), o = prog(t, fin - .15, fin); css(n, { opacity: p * (1 - o), transform: `scale(${lerp(1.3, 1, p)}) translateY(${(1 - p) * 20 * U}px)` }); });
    (c.icons || []).forEach((ic, i) => { const n = el.querySelector(`[data-ic="${i}"]`); const p = back(prog(t, ic.at, ic.at + .5)), o = prog(t, (ic.until || c.end) - .2, ic.until || c.end);
      css(n, { opacity: clamp(p * 2) * (1 - o), transform: `translateY(${(1 - Math.min(1, p)) * 260 * U}px) rotate(${(1 - p) * 25 + Math.sin(t * 2.2 + i) * 4}deg) scale(${Math.max(.2, p)})` }); }); },
};

// ---------- 14 · Franja cinemascope ----------
// Barras negras arriba y abajo; la persona vive en la franja central; en las barras, sans fina con palabra clave con brillo naranja y palabras que rotan.
C.strip = {
  make(el, c) { const y0 = (c.y0 || .31) * H, y1 = (c.y1 || .69) * H; css(el, { left: 0, top: 0, width: W + "px", height: H + "px", pointerEvents: "none" }); el._noFull = true;
    const bar = (top, h) => `<div style="position:absolute;left:0;width:${W}px;top:${top}px;height:${h}px;background:#000"></div>`;
    el.innerHTML = bar(0, y0) + bar(y1, H - y1) +
      `<div style="position:absolute;left:0;width:${W}px;top:${y0 - 1}px;height:1px;background:rgba(241,243,246,.35)"></div><div style="position:absolute;left:0;width:${W}px;top:${y1}px;height:1px;background:rgba(241,243,246,.35)"></div>` +
      (c.lines || []).map((l, i) => `<div data-l="${i}" style="position:absolute;left:${px(60)};right:${px(60)};top:${(l.y || .14) * H}px;text-align:${l.align || "center"};font:${l.weight || 300} ${px(l.size || 54)}/1.2 Inter,'Space Grotesk',sans-serif;letter-spacing:.02em;color:#f1f3f6;opacity:0">${l.t.split("|").map((s, j) => j % 2 ? `<span style="color:#ff6a2a;text-shadow:0 0 ${px(18)} rgba(255,106,42,.9),0 0 ${px(40)} rgba(255,80,20,.5);font-weight:500">${s}</span>` : s).join("")}</div>`).join("") +
      (c.rotate ? `<div data-rot style="position:absolute;left:0;right:0;top:${(c.rotate.y || .82) * H}px;text-align:center;font:300 ${px(c.rotate.size || 60)}/1.1 Inter,sans-serif;color:#f1f3f6"><span style="color:#8a8d93">${c.rotate.prefix || ""}</span> <span data-rw style="display:inline-block;color:#ff6a2a;font-weight:500"></span></div>` : ""); },
  draw(el, c, t) { const b = c.hold ? 0 : prog(t, c.end - .25, c.end); css(el, { opacity: 1 - b });
    (c.lines || []).forEach((l, i) => { const n = el.querySelector(`[data-l="${i}"]`); const fin = l.until || c.end;
      if (l.type === "typewriter") { const total = l.t.replace(/\|/g, "").length, k = Math.floor(clamp((t - l.at) / (l.dur || 1.2)) * total);
        n.style.opacity = t >= l.at && t < fin ? 1 : 0; n.textContent = l.t.replace(/\|/g, "").slice(0, k) + (t < l.at + (l.dur || 1.2) && Math.floor(t * 6) % 2 ? "▌" : ""); }
      else { const p = eOut(prog(t, l.at, l.at + .35)), o = prog(t, fin - .2, fin); css(n, { opacity: p * (1 - o), transform: `translateY(${(1 - p) * 14 * U}px)` }); } });
    if (c.rotate) { const r = el.querySelector("[data-rw]"), ws = c.rotate.words, k = Math.floor(Math.max(0, t - c.rotate.at) / (c.rotate.every || .55)) % ws.length, ph = (Math.max(0, t - c.rotate.at) % (c.rotate.every || .55)) / (c.rotate.every || .55);
      r.textContent = ws[k]; const p = eOut(clamp(ph * 3)); css(r, { opacity: p, transform: `translateY(${(1 - p) * 22 * U}px)` });
      el.querySelector("[data-rot]").style.opacity = t >= c.rotate.at && t < (c.rotate.until || 1e9) ? 1 : 0; } },
};

// ---------- 5 · Tipografía roja editorial ----------
// Palabras que giran en arco alrededor de la cabeza (sans blanca + serif itálica + rojo), "!!!" rojo dibujado, destellos (E.flashes) y zoom.
C.arc = {
  make(el, c) { css(el, { left: 0, top: 0, width: W + "px", height: H + "px", pointerEvents: "none" }); el._noFull = true;
    const cx = (c.cx || .5) * W, cy = (c.cy || .42) * H;
    el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" style="position:absolute;inset:0;width:100%;height:100%;overflow:visible"><defs>
      ${c.arcs.map((a, i) => { const r = (a.r || 440) * U, s = a.dir === "down" ? 1 : 0; return `<path id="arc${i}" d="M ${cx - r} ${cy} A ${r} ${r} 0 0 ${s ? 0 : 1} ${cx + r} ${cy}" fill="none"/>`; }).join("")}</defs>
      ${c.arcs.map((a, i) => `<g data-a="${i}" style="transform-origin:${cx}px ${cy}px;opacity:0"><text font-family="${a.serif ? "'Instrument Serif',serif" : "Inter,Helvetica,sans-serif"}" font-style="${a.serif ? "italic" : "normal"}" font-weight="${a.serif ? 400 : 800}" font-size="${(a.size || 96) * U}" fill="${a.color || "#fff"}" letter-spacing="${a.serif ? 0 : 2}" style="text-transform:${a.serif ? "none" : "uppercase"};paint-order:stroke fill" stroke="rgba(0,0,0,.35)" stroke-width="${a.serif ? 0 : 6 * U}"><textPath href="#arc${i}" startOffset="${a.offset ?? 50}%" text-anchor="middle">${a.t}</textPath></text></g>`).join("")}
      ${c.bang ? `<g data-bang style="opacity:0;transform-origin:${(c.bang.x || .8) * W}px ${(c.bang.y || .28) * H}px"><text x="${(c.bang.x || .8) * W}" y="${(c.bang.y || .28) * H}" text-anchor="middle" font-family="'Bradley Hand','Marker Felt',Noteworthy,cursive" font-size="${210 * U}" font-weight="700" fill="#e1000f" transform="rotate(-12 ${(c.bang.x || .8) * W} ${(c.bang.y || .28) * H})">!!!</text></g>` : ""}
      ${(c.stamps || []).map((s, i) => `<g data-s="${i}" style="opacity:0;transform-origin:${s.x * W}px ${s.y * H}px"><rect x="${s.x * W - (s.w || 420) * U / 2}" y="${s.y * H - 60 * U}" width="${(s.w || 420) * U}" height="${120 * U}" fill="#770306" transform="rotate(${s.rot || -6} ${s.x * W} ${s.y * H})"/><text x="${s.x * W}" y="${s.y * H + 26 * U}" text-anchor="middle" font-family="Inter,Helvetica,sans-serif" font-weight="800" font-size="${(s.size || 70) * U}" fill="#fff" transform="rotate(${s.rot || -6} ${s.x * W} ${s.y * H})" style="text-transform:uppercase">${s.t}</text></g>`).join("")}</svg>`; },
  draw(el, c, t) { const b = c.hold ? 0 : prog(t, c.end - .2, c.end); css(el, { opacity: 1 - b });
    c.arcs.forEach((a, i) => { const g = el.querySelector(`[data-a="${i}"]`), p = eOut(prog(t, a.at, a.at + .4)), fin = a.until || c.end, o = prog(t, fin - .2, fin);
      css(g, { opacity: p * (1 - o), transform: `rotate(${(a.spin || 10) * (t - a.at) + (1 - p) * -40}deg) scale(${lerp(.8, 1, p)})` }); });
    const bg = el.querySelector("[data-bang]"); if (bg && c.bang.at != null) { const p = back(prog(t, c.bang.at, c.bang.at + .3)); css(bg, { opacity: clamp(p * 2), transform: `scale(${Math.max(.3, p)}) rotate(${Math.sin(t * 9) * 3}deg)` }); }
    (c.stamps || []).forEach((s, i) => { const g = el.querySelector(`[data-s="${i}"]`), p = prog(t, s.at, s.at + .2); css(g, { opacity: clamp(p * 3), transform: `scale(${lerp(2.2, 1, eOut(p))})` }); }); },
};

// Marca de agua / etiqueta fija (p. ej. chip de la masterclass arriba) — simple, sin animación salvo la entrada.
C.etiqueta = {
  make(el, c) { css(el, { left: 0, top: (c.y || .05) * H + "px", width: W + "px", textAlign: "center", pointerEvents: "none" }); el._noFull = true;
    el.innerHTML = `<span style="display:inline-block;padding:${px(14)} ${px(28)};border-radius:999px;background:${c.bg || "rgba(0,0,0,.72)"};color:${c.color || "#fff"};font:700 ${px(c.size || 30)} Inter,sans-serif;letter-spacing:.04em">${c.t}</span>`; },
  draw(el, c, t) { const p = eOut(prog(t, c.start, c.start + .3)), b = c.hold ? 0 : prog(t, c.end - .2, c.end); css(el, { opacity: p * (1 - b), transform: `translateY(${(1 - p) * -20 * U}px)` }); },
};

// ---------- presets de subtítulos de las fichas ----------
Object.assign(SUB_PRESETS, {
  // 36: caja roja, itálica, mayúsculas, en la unión
  cajaRoja: { font: "Inter", weight: 800, italic: true, upper: true, color: "#fff", keyColor: "#c6ff2e", box: "#c1571a", reveal: "chunk", size: 54, y: .285, maxWords: 4, maxChars: 24, shadow: "none" },
  // 16: gris chico con palabra naranja
  grisNaranja: { font: "Inter", weight: 500, color: "#b9b7b4", keyColor: "#c36b58", reveal: "chunk", size: 50, y: .80, maxWords: 4, maxChars: 26, shadow: "0 2px 10px rgba(0,0,0,.6)" },
  // 7: etiqueta negra, mayúsculas chica, en la unión
  label: { font: "Inter", weight: 700, upper: true, color: "#fff", box: "#1e1a18", reveal: "chunk", size: 40, y: .40, maxWords: 4, maxChars: 26, shadow: "none" },
  // 11: manuscrita blanca + palabra amarilla (viene "hand"; aquí con fuentes de la Mac)
  manuscrita: { font: "Noteworthy, 'Bradley Hand', 'Marker Felt'", weight: 700, color: "#fff", keyColor: "#f5b547", reveal: "word", blur: true, size: 78, y: .64, maxWords: 3, maxChars: 20, shadow: "0 4px 14px rgba(0,0,0,.6)" },
  // 44: blanca bold mínima
  minima: { font: "Inter", weight: 800, color: "#fff", keyColor: "#8fd3b0", reveal: "chunk", size: 62, y: .66, maxWords: 3, maxChars: 18, shadow: "0 4px 16px rgba(0,0,0,.6)" },
  // 10: línea chica blanca (la palabra gigante la pone gradword)
  chica: { font: "Inter", weight: 600, color: "#fff", reveal: "chunk", size: 46, y: .70, maxWords: 4, maxChars: 26, shadow: "0 3px 12px rgba(0,0,0,.65)" },
  // 14: sans fina en la barra inferior
  fina: { font: "Inter", weight: 300, color: "#f1f3f6", keyColor: "#ff6a2a", reveal: "chunk", size: 48, y: .76, maxWords: 4, maxChars: 26, shadow: "none", spacing: ".02em" },
  // 5: serif itálica + rojo
  roja: { font: "Inter", weight: 800, upper: true, color: "#fff", keyFont: "'Instrument Serif'", keyItalic: true, keyColor: "#e1000f", keyScale: 1.35, allowSizes: true, reveal: "word", blur: true, size: 72, y: .66, maxWords: 3, maxChars: 18, shadow: "0 4px 16px rgba(0,0,0,.55)" },
});

// Caja de color detrás del bloque de subtítulos (presets con `box`): se aplica una vez por chunk.
const _drawSubs = drawSubs;
drawSubs = function (t, fullOn) {
  _drawSubs(t, fullOn);
  const S = subStyle(), line = subsEl.firstChild;
  if (!line) return;
  if (S.box) css(line, { background: S.box, padding: `${px(10)} ${px(26)}`, borderRadius: px(6) });
  else css(line, { background: "", padding: "", borderRadius: "" });
};

// Los componentes marcados _noFull no apagan los subtítulos aunque cubran todo el cuadro.
const _render = render;
render = function (t) {
  let fullOn = false;
  for (const { c, el } of cues) {
    const on = t >= c.start && t <= c.end; el.classList.toggle("hide", !on);
    if (on) { C[c.type].draw(el, c, t); if ((el.classList.contains("full") && !el._noFull) || c.noSubs || (E.subs && E.subs.onlyClean && t >= c.start - .15 && t <= c.end + .15)) fullOn = true; }
  }
  drawSubs(t, fullOn); drawFlash(t);
};
window.__render = render;
