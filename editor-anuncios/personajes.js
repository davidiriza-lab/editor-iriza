// Personajes "monitos de palito" — estilo oficial (ref 2: corredor dorado).
// Esqueleto 2D con poses clave por ángulos de articulación, interpolación suave y apoyo automático en el piso.
//
// Convenciones de ángulos (radianes): 0 = apuntando hacia abajo; positivo = hacia adelante (hacia donde mira).
//   pierna: t (muslo), k (flexión de rodilla: el pie se va hacia atrás)
//   brazo:  a (brazo), e (flexión de codo: la mano se va hacia adelante/arriba)
//   1 = lado cercano (brillante, al frente), 2 = lado lejano (más oscuro, detrás del torso)
(function () {
  const P = { head: 0.095, gap: 0.035, torso: 0.30, thigh: 0.22, shin: 0.235, upper: 0.165, fore: 0.15, sw: 0.072 };

  // ---- poses estáticas ----
  const base = { lean: 0, tilt: 0, t1: .06, k1: .04, t2: -.06, k2: .04, a1: .14, e1: .12, a2: -.14, e2: .12, lift: 0 };
  const POSES = {
    stand:   { view: "front", t1: .1, t2: .1, a1: .16, e1: .05, a2: .16, e2: .05 },
    point:   { a1: 1.55, e1: .02, a2: -.1, e2: .15 },
    think:   { tilt: .12, a1: .45, e1: 2.55, a2: .55, e2: 1.45, t1: .02, t2: -.1 },
    worried: { view: "front", t1: .1, t2: .1, a1: 2.45, e1: 2.05, a2: 2.45, e2: 2.05 },
    sad:     { lean: .22, tilt: .35, a1: .05, e1: .05, a2: -.02, e2: .05 },
    sit:     { lean: -.05, t1: 1.52, k1: 1.52, t2: 1.45, k2: 1.45, a1: .55, e1: .7, a2: .45, e2: .8 },
    floor:   { lean: .35, tilt: .2, t1: 1.45, k1: .9, t2: 1.35, k2: .35, a1: .95, e1: .5, a2: .85, e2: .6 },
    kneel:   { lean: .08, t1: 1.25, k1: 1.25, t2: -.05, k2: 1.57, a1: .3, e1: .4, a2: .2, e2: .3 },
    carry:   { lean: -.06, a1: .95, e1: .75, a2: .9, e2: .8 },
    push:    { lean: .62, t1: .45, k1: .35, t2: -.55, k2: .2, a1: 1.5, e1: .25, a2: 1.42, e2: .35 },
    reach:   { a1: 2.85, e1: .05, a2: .2, e2: .2 },
    hug:     { lean: .06, a1: 1.35, e1: 1.25, a2: 1.3, e2: 1.3 },
    hands:   { a1: .9, e1: 1.2, a2: .8, e2: 1.2 },                 // explicando, manos al frente
    arms:    { view: "front", t1: .12, t2: .12, a1: .55, e1: 1.6, a2: .55, e2: 1.6 },   // brazos cruzados
    shrug:   { view: "front", t1: .1, t2: .1, a1: .75, e1: -1.4, a2: .75, e2: -1.4 },   // no sé
    victory: { view: "front", a1: 2.55, e1: .1, a2: 2.55, e2: .1, t1: .14, t2: .14 },
    hold:    { view: "front", t1: .14, t2: .14, a1: 2.92, e1: .12, a2: 2.92, e2: .12 },   // sostiene algo arriba
    strain:  { view: "front", t1: .22, k1: .35, t2: .22, k2: .35, a1: 2.75, e1: .5, a2: 2.75, e2: .5 },  // sostiene con esfuerzo
    tired:   { lean: .45, tilt: .3, t1: .35, k1: .5, t2: -.15, k2: .45, a1: .5, e1: .1, a2: .4, e2: .1 },
  };

  // ---- ciclos (fase 0..1). Se definen la mitad del ciclo y la otra mitad es el espejo (lados intercambiados) ----
  const CYCLES = {
    run: { hz: 1.35, bob: .045, keys: [
      { lean: .26, t1: .62, k1: .25, t2: -.78, k2: 1.25, a1: -.85, e1: 1.45, a2: .8, e2: 1.62, lift: 0 },     // contacto
      { lean: .26, t1: .15, k1: .55, t2: -.2, k2: 2.05, a1: -.3, e1: 1.6, a2: .3, e2: 1.55, lift: 0 },       // carga
      { lean: .26, t1: -.35, k1: .3, t2: .45, k2: 1.85, a1: .35, e1: 1.55, a2: -.4, e2: 1.5, lift: .06 },    // impulso / vuelo
    ] },
    walk: { hz: .95, bob: .018, keys: [
      { lean: .05, t1: .38, k1: .05, t2: -.32, k2: .3, a1: -.32, e1: .3, a2: .34, e2: .35, lift: 0 },
      { lean: .05, t1: .05, k1: .08, t2: .08, k2: .95, a1: .02, e1: .25, a2: -.02, e2: .25, lift: .01 },
      { lean: .05, t1: -.22, k1: .1, t2: .32, k2: .35, a1: .25, e1: .3, a2: -.25, e2: .3, lift: 0 },
    ] },
    cheer: { hz: 1.6, bob: .03, view: "front", keys: [
      { t1: .12, k1: .05, t2: .12, k2: .05, a1: 2.35, e1: .3, a2: 2.6, e2: .05 },
      { t1: .12, k1: .12, t2: .12, k2: .12, a1: 2.6, e1: .1, a2: 2.4, e2: .3, lift: .03 },
      { t1: .12, k1: .05, t2: .12, k2: .05, a1: 2.5, e1: .2, a2: 2.55, e2: .15 },
    ] },
    wave: { hz: 1.4, bob: 0, view: "front", keys: [
      { t1: .1, t2: .1, a1: 2.3, e1: .2, a2: .16, e2: .05 }, { t1: .1, t2: .1, a1: 2.25, e1: .85, a2: .16, e2: .05 }, { t1: .1, t2: .1, a1: 2.3, e1: .35, a2: .16, e2: .05 },
    ] },
    talk: { hz: .7, bob: 0, keys: [
      { a1: .9, e1: 1.2, a2: .75, e2: 1.15 }, { a1: 1.05, e1: 1.05, a2: .7, e2: 1.3 }, { a1: .85, e1: 1.3, a2: .9, e2: 1.05 },
    ] },
  };
  const KEYS = ["lean", "tilt", "t1", "k1", "t2", "k2", "a1", "e1", "a2", "e2", "lift"];
  const full = o => Object.assign({}, base, o);
  const mirror = o => ({ ...o, t1: o.t2, k1: o.k2, t2: o.t1, k2: o.k1, a1: o.a2, e1: o.e2, a2: o.a1, e2: o.e1 });
  const lerp = (a, b, x) => a + (b - a) * x;
  const mix = (A, B, x) => { const o = {}; for (const k of KEYS) o[k] = lerp(A[k] ?? base[k], B[k] ?? base[k], x); return o; };
  const smooth = x => x * x * (3 - 2 * x);

  // pose de un ciclo en la fase ph (Catmull-Rom sobre claves en anillo: mitad + espejo)
  function cyclePose(name, ph) {
    const C = CYCLES[name], half = C.keys.map(full), ring = [...half, ...half.map(mirror)], n = ring.length;
    const u = ((ph % 1) + 1) % 1 * n, i = Math.floor(u), f = u - i, g = k => ring[((i + k) % n + n) % n];
    const o = {};
    for (const k of KEYS) { const p0 = g(-1)[k], p1 = g(0)[k], p2 = g(1)[k], p3 = g(2)[k];
      o[k] = 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f * f * f); }
    o.bob = C.bob * (Math.abs(Math.sin(ph * Math.PI * 2)));   // sube en el vuelo (2 veces por ciclo)
    o.view = C.view || "side";
    return o;
  }
  function poseAt(name, t, phase = 0) {
    if (CYCLES[name]) return cyclePose(name, t * CYCLES[name].hz + phase);
    return { ...full(POSES[name] || {}), bob: 0, view: (POSES[name] || {}).view || "side" };
  }

  // cinemática directa → puntos (unidades de altura; pies en y=0)
  function solve(o, kid) {
    const k = kid ? { head: .125, torso: .26, thigh: .2, shin: .2, upper: .15, fore: .13 } : P;
    const legPts = (t, kn) => { const knee = [Math.sin(t) * k.thigh, Math.cos(t) * k.thigh]; const sa = t - kn; return [knee, [knee[0] + Math.sin(sa) * k.shin, knee[1] + Math.cos(sa) * k.shin]]; };
    const L1 = legPts(o.t1, o.k1), L2 = legPts(o.t2, o.k2);
    const lowest = Math.max(L1[0][1], L1[1][1], L2[0][1], L2[1][1]);
    const hip = [0, -lowest - (o.lift || 0) - (o.bob || 0)];
    const sh = [hip[0] + Math.sin(o.lean) * k.torso, hip[1] - Math.cos(o.lean) * k.torso];
    const hd = [sh[0] + Math.sin(o.lean + o.tilt) * (P.gap + k.head), sh[1] - Math.cos(o.lean + o.tilt) * (P.gap + k.head)];
    const armPts = (a, e) => { const aa = a + o.lean * .6, el = [sh[0] + Math.sin(aa) * k.upper, sh[1] + Math.cos(aa) * k.upper], fa = aa + e; return [el, [el[0] + Math.sin(fa) * k.fore, el[1] + Math.cos(fa) * k.fore]]; };
    const add = p => [p[0] + hip[0], p[1] + hip[1]];
    let A2 = armPts(o.a2, o.e2), L2m = L2.map(add);
    if (o.view === "front") {   // de frente: el lado 2 es espejo del lado 1 (piernas abiertas, brazos a ambos lados)
      const cx = hip[0], sx = sh[0];
      L2m = L2m.map(p => [2 * cx - p[0], p[1]]); A2 = A2.map(p => [2 * sx - p[0], p[1]]);
    }
    return { hip, sh, hd, r: k.head, L1: L1.map(add), L2: L2m, A1: armPts(o.a1, o.e1), A2, front: o.view === "front" };
  }

  let gid = 0;
  // Dibuja un personaje. o: { x, y (piso), h (altura px), pose, t, phase, facing (1|-1), color: "acc"|"grey"|"#hex", kid, blend:{from,to,x} }
  function draw(o, theme) {
    let pose;
    if (o.blend) { const A = poseAt(o.blend.from, o.t, o.phase), B = poseAt(o.blend.to, o.t, o.phase); pose = mix(A, B, smooth(o.blend.x)); pose.view = o.blend.x < .5 ? A.view : B.view; }
    else pose = poseAt(o.pose || "stand", o.t, o.phase || 0);
    const s = solve(pose, o.kid), h = o.h, f = o.facing || 1, id = "pg" + (gid++);
    const top = o.y - h, cA = o.color === "grey" ? ["#D0D0D0", "#6A6A6A"] : o.color && o.color[0] === "#" ? [o.color, o.color] : [theme.acc, theme.accDark];
    const limb = (root, pts, far) => `<path d="M${root[0]} ${root[1]} L${pts[0][0]} ${pts[0][1]} L${pts[1][0]} ${pts[1][1]}" stroke="${far ? `url(#${id}f)` : `url(#${id})`}" stroke-width="${P.sw}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>`;
    return `<g transform="translate(${o.x} ${o.y}) scale(${h * f} ${h})" ${o.blur ? `filter="url(#pblur)"` : ""} opacity="${o.opacity ?? 1}">
      <defs><linearGradient id="${id}" gradientUnits="userSpaceOnUse" x1="0" y1="-1" x2="0" y2="0"><stop offset="0" stop-color="${cA[0]}"/><stop offset="1" stop-color="${cA[1]}"/></linearGradient>
      <linearGradient id="${id}f" gradientUnits="userSpaceOnUse" x1="0" y1="-1" x2="0" y2="0"><stop offset="0" stop-color="${cA[0]}" stop-opacity="1"/><stop offset="1" stop-color="${cA[1]}"/></linearGradient></defs>
      <g opacity="${s.front ? .9 : .62}">${limb(s.sh, s.A2, true)}${limb(s.hip, s.L2, true)}</g>
      ${limb(s.hip, [s.sh, s.sh], false)}
      <circle cx="${s.hd[0]}" cy="${s.hd[1]}" r="${s.r}" fill="url(#${id})"/>
      ${limb(s.hip, s.L1, false)}${limb(s.sh, s.A1, false)}
      ${o.prop === "box" ? `<rect x="${s.A1[1][0] - .02}" y="${s.A1[1][1] - .16}" width=".26" height=".2" rx=".02" fill="url(#${id})" opacity=".85"/>` : ""}</g>`;
  }
  window.PERSONAJES = { draw, poseAt, POSES, CYCLES };
})();
