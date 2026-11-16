// ===================== CAPAS: mezcla + "metele algo acá" =====================
// Cada capa vive en P.capas (coordenadas lógicas 960×540, tiempos en segundos de la pieza).
//  texto    {texto, x, y, tam, fuente, color, fondo, alin, entrada}
//  imagen   {ruta, x, y, w, rot, borde, entrada}
//  circulo  {x, y, w, h, color, grosor, entrada}      resaltador {x, y, w, h, color}
//  flecha   {x, y, x2, y2, color, grosor, curva, entrada}
//  estilo   {slug, x, y, w, h, encaje: ventana|escalar, mascara: rect|elipse|ninguna, mezcla, opacidad, desfase}
//  pedido   {x, y, texto}   ← pin para Claude: no se exporta
// Todas: {id, tipo, desde, hasta (null = hasta el final), oculta}
const FUENTES_CAPA = { "Plex Sans": "700 {t}px 'IBM Plex Sans'", "Plex fina": "400 {t}px 'IBM Plex Sans'", "JetBrains Mono": "600 {t}px 'JetBrains Mono'", "Anton": "{t}px Anton", "Bebas Neue": "{t}px 'Bebas Neue'", "Marcador": "{t}px 'Permanent Marker'", "Máquina": "{t}px 'Special Elite'", "A mano": "{t}px Caveat" };
const COLORES_CAPA = { texto: "#f2efe8", claro: "#c8e6c8", acento: "#7ab37a", medio: "#4a7c4a", fondo: "#1a2e1a", noche: "#0c160c", rojo: "#c8102e", amarillo: "#ffd84a", blanco: "#ffffff", negro: "#000000" };
const MEZCLAS = { "source-over": "Normal", multiply: "Multiplicar", screen: "Trama clara", overlay: "Superponer", lighter: "Sumar luz", difference: "Diferencia", luminosity: "Luminosidad", color: "Color" };
const ENTRADAS = { fundido: "Fundido", corte: "Corte", golpe: "Golpe", tipeo: "Tipeo", trazo: "Trazo", deslizar: "Deslizar" };
const NOMBRES_TIPO = { texto: "Texto", imagen: "Imagen", circulo: "Círculo", resaltador: "Resaltador", flecha: "Flecha", estilo: "Estilo mezclado", pedido: "Pedido" };
const fontCapa = cp => (FUENTES_CAPA[cp.fuente] || FUENTES_CAPA["Plex Sans"]).replace("{t}", Math.round(cp.tam || 48));
let selId = null, herramienta = "mover";
const capas = () => (P.capas = P.capas || []);
const capaSel = () => capas().find(c => c.id === selId);
const nuevoId = () => "c" + Date.now().toString(36) + Math.floor(Math.random() * 1e3);
const IMGS_CAPA = new Map();
function imgCapa(ruta) { if (!IMGS_CAPA.has(ruta)) { const i = new Image(); i.src = `/p/${proyecto}/${ruta}`; IMGS_CAPA.set(ruta, i) } const i = IMGS_CAPA.get(ruta); return i.complete && i.naturalWidth ? i : null }
const activa = (cp, tg) => !cp.oculta && tg >= (cp.desde || 0) && (cp.hasta == null || tg < cp.hasta + .25);

// ---------- dibujo de capas ----------
const OFF = new Map();
function dibujarCapas(c, tg, env) {
  for (const cp of capas()) {
    if (cp.tipo === "pedido" || !activa(cp, tg)) continue;
    const d0 = cp.desde || 0, kIn = seg(tg, d0, d0 + .45), kOut = cp.hasta == null ? 1 : 1 - seg(tg, cp.hasta, cp.hasta + .25), ent = cp.entrada || "fundido";
    c.save(); c.globalAlpha = kOut * (ent === "fundido" || ent === "deslizar" ? eo(kIn) : 1);
    try { DIBUJO[cp.tipo] && DIBUJO[cp.tipo](c, cp, tg - d0, kIn, ent, env) } catch (e) { console.error("capa", cp, e) }
    c.restore();
  }
}
function lineasTexto(c, cp) { c.font = fontCapa(cp); const ls = String(cp.texto || "").split("\n"); const lh = (cp.tam || 48) * 1.12; return { ls, lh, w: Math.max(...ls.map(l => c.measureText(l).width), 10) } }
const DIBUJO = {
  texto(c, cp, tl, k, ent) {
    const { ls, lh, w } = lineasTexto(c, cp), al = cp.alin || "left", x0 = al === "center" ? cp.x - w / 2 : al === "right" ? cp.x - w : cp.x, tam = cp.tam || 48;
    if (ent === "golpe") { const s = eb(k); c.translate(x0 + w / 2, cp.y + lh * ls.length / 2); c.scale(s, s); c.translate(-(x0 + w / 2), -(cp.y + lh * ls.length / 2)) }
    if (ent === "deslizar") c.translate(0, (1 - eo(k)) * 30);
    if (cp.fondo) { const pad = tam * .28; caja(c, x0 - pad, cp.y - pad * .6, w + pad * 2, lh * ls.length + pad * .9, cp.fondo) }
    let total = ls.join("").length, n = ent === "tipeo" ? Math.floor(total * cl(tl / Math.max(.5, total * .045))) : total;
    ls.forEach((l, i) => { const s = l.slice(0, Math.max(0, n)); n -= l.length; _texto(c, s, al === "center" ? cp.x : al === "right" ? cp.x : cp.x, cp.y + i * lh, fontCapa(cp), cp.color || "#f2efe8", al, "top") });
  },
  imagen(c, cp, tl, k, ent) {
    const im = imgCapa(cp.ruta); if (!im) return; const w = cp.w || 320, h = w * im.naturalHeight / im.naturalWidth, cx = cp.x + w / 2, cy = cp.y + h / 2;
    c.translate(cx, cy + (ent === "deslizar" ? (1 - eo(k)) * 40 : 0)); c.rotate((cp.rot || 0) * Math.PI / 180); if (ent === "golpe") { const s = eb(k); c.scale(s, s) }
    if (cp.borde) { sombra(c, 6, 10, .45); caja(c, -w / 2 - 10, -h / 2 - 10, w + 20, h + 20, "#f6f3ea"); sinSombra(c) }
    c.drawImage(im, -w / 2, -h / 2, w, h);
  },
  circulo(c, cp, tl, k, ent) {
    const kk = ent === "trazo" || ent === "fundido" ? eio(k) : 1; c.strokeStyle = cp.color || "#c8102e"; c.lineWidth = cp.grosor || 5; c.lineCap = "round";
    c.beginPath(); c.ellipse(cp.x + cp.w / 2, cp.y + cp.h / 2, Math.abs(cp.w / 2), Math.abs(cp.h / 2), -.04, -Math.PI / 2, -Math.PI / 2 + TAU * kk * 1.04); c.stroke();
  },
  resaltador(c, cp, tl, k) { c.globalCompositeOperation = "multiply"; c.globalAlpha *= .55; c.fillStyle = cp.color || "#ffd84a"; c.fillRect(cp.x, cp.y, cp.w * eo(k), cp.h) },
  flecha(c, cp, tl, k, ent) {
    const a = [cp.x, cp.y], b = [cp.x2, cp.y2], len = Math.hypot(b[0] - a[0], b[1] - a[1]); const pts = curva(a, b, (cp.curva ?? .2) * len);
    c.strokeStyle = c.fillStyle = cp.color || "#c8102e"; c.lineWidth = cp.grosor || 5; c.lineCap = "round"; c.lineJoin = "round";
    const fin = trazo(c, pts, ent === "corte" || ent === "golpe" ? 1 : eio(k)); if ((ent === "corte" || ent === "golpe" ? 1 : k) > .85) { const pre = pts[pts.length - 4]; punta(c, pre, fin, 10 + (cp.grosor || 5) * 2.4); c.stroke() }
  },
  estilo(c, cp, tl, k, ent, env) {
    const e2 = ESTILOS.find(e => e.slug === cp.slug); if (!e2) return; const sc = c.canvas.width / W, ow = Math.round(W * sc), oh = Math.round(H * sc);
    let off = OFF.get(cp.id); if (!off || off.width !== ow) { off = lienzo(ow, oh); OFF.set(cp.id, off) }
    dibujarEn(off.getContext("2d"), e2, Math.min(e2.dur, Math.max(0, tl + (+cp.desfase || 0))), P.T, { vid: env.vid, reproduciendo: false, capa: true }, false);
    c.globalAlpha *= cp.opacidad ?? 1; c.globalCompositeOperation = cp.mezcla || "source-over"; if (ent === "golpe") { const s = eb(k); c.translate(cp.x + cp.w / 2, cp.y + cp.h / 2); c.scale(s, s); c.translate(-(cp.x + cp.w / 2), -(cp.y + cp.h / 2)) }
    const m = cp.mascara || "rect"; if (m !== "ninguna") { c.beginPath(); if (m === "elipse") c.ellipse(cp.x + cp.w / 2, cp.y + cp.h / 2, Math.abs(cp.w / 2), Math.abs(cp.h / 2), 0, 0, TAU); else c.rect(cp.x, cp.y, cp.w, cp.h); c.clip() }
    if ((cp.encaje || "ventana") === "ventana" || m === "ninguna") c.drawImage(off, 0, 0, W, H);
    else { const f = Math.max(Math.abs(cp.w) / W, Math.abs(cp.h) / H), w = W * f, h = H * f; c.drawImage(off, cp.x + (cp.w - w) / 2, cp.y + (cp.h - h) / 2, w, h) }
  },
};

// ---------- cajas para tocar / mover ----------
function caja2(cp) {
  if (cp.tipo === "texto") { const { lh, ls, w } = lineasTexto(ctx, cp), al = cp.alin || "left"; return [al === "center" ? cp.x - w / 2 : al === "right" ? cp.x - w : cp.x, cp.y, w, lh * ls.length] }
  if (cp.tipo === "imagen") { const im = imgCapa(cp.ruta), w = cp.w || 320; return [cp.x, cp.y, w, im ? w * im.naturalHeight / im.naturalWidth : w * .66] }
  if (cp.tipo === "flecha") return [Math.min(cp.x, cp.x2), Math.min(cp.y, cp.y2), Math.abs(cp.x2 - cp.x) || 1, Math.abs(cp.y2 - cp.y) || 1];
  if (cp.tipo === "pedido") return [cp.x - 14, cp.y - 34, 28, 34];
  return [Math.min(cp.x, cp.x + cp.w), Math.min(cp.y, cp.y + cp.h), Math.abs(cp.w), Math.abs(cp.h)];
}
const manija = cp => { if (cp.tipo === "flecha") return [cp.x2, cp.y2]; if (cp.tipo === "pedido") return null; const [x, y, w, h] = caja2(cp); return [x + w, y + h] };

// ---------- capa de edición (no se exporta) ----------
const ov = $("ov"), octx = ov.getContext("2d");
function escalaPantalla() { const r = cv.getBoundingClientRect(), s = Math.min(r.width / W, r.height / H); return { r, s, ox: (r.width - W * s) / 2, oy: (r.height - H * s) / 2 } }
function aLogico(ev) { const { r, s, ox, oy } = escalaPantalla(); return [(ev.clientX - r.left - ox) / s, (ev.clientY - r.top - oy) / s] }
function dibujarOverlay() {
  const { r, s, ox, oy } = escalaPantalla(), dpr = devicePixelRatio || 1; if (ov.width !== Math.round(r.width * dpr) || ov.height !== Math.round(r.height * dpr)) { ov.width = Math.round(r.width * dpr); ov.height = Math.round(r.height * dpr) }
  octx.setTransform(1, 0, 0, 1, 0, 0); octx.clearRect(0, 0, ov.width, ov.height); if (!P) return; octx.setTransform(dpr * s, 0, 0, dpr * s, dpr * ox, dpr * oy); const px = 1 / s;
  let n = 0; for (const cp of capas()) { if (cp.tipo !== "pedido" || cp.oculta) continue; n++; const on = t >= (cp.desde || 0) - .05; octx.globalAlpha = on ? 1 : .35;
    octx.fillStyle = cp.hecho ? "#7ab37a" : "#ff8a3d"; octx.beginPath(); octx.moveTo(cp.x, cp.y); octx.arc(cp.x, cp.y - 20 * px, 13 * px, Math.PI * .8, Math.PI * .2); octx.closePath(); octx.fill();
    octx.fillStyle = "#111"; octx.font = `700 ${13 * px}px 'IBM Plex Sans'`; octx.textAlign = "center"; octx.textBaseline = "middle"; octx.fillText(cp.hecho ? "✓" : String(n), cp.x, cp.y - 20 * px); octx.globalAlpha = 1 }
  const cp = capaSel(); if (cp) { const [x, y, w, h] = caja2(cp); octx.strokeStyle = "#7ab37a"; octx.lineWidth = 1.5 * px; octx.setLineDash([5 * px, 4 * px]); octx.strokeRect(x - 4 * px, y - 4 * px, w + 8 * px, h + 8 * px); octx.setLineDash([]);
    const m = manija(cp); if (m) { octx.fillStyle = "#7ab37a"; octx.fillRect(m[0] - 6 * px, m[1] - 6 * px, 12 * px, 12 * px) } if (cp.tipo === "flecha") { octx.fillStyle = "#7ab37a"; octx.beginPath(); octx.arc(cp.x, cp.y, 5 * px, 0, TAU); octx.fill() } }
  if (arrastre?.preview) { const [x0, y0] = arrastre.p0, [x1, y1] = arrastre.p; octx.strokeStyle = "#ff8a3d"; octx.lineWidth = 1.5 * px; octx.setLineDash([6 * px, 4 * px]); octx.strokeRect(Math.min(x0, x1), Math.min(y0, y1), Math.abs(x1 - x0), Math.abs(y1 - y0)); octx.setLineDash([]) }
}

// ---------- interacción ----------
let arrastre = null;
const PREVIEW = { estilo: true };
function crear(base) { const cp = { id: nuevoId(), desde: Math.round(t * 10) / 10, hasta: null, ...base }; capas().push(cp); selId = cp.id; cambio(); pintarCapas(); return cp }
function tocar(p) { // capa más arriba bajo el punto (prefiere las visibles en este segundo)
  const ls = capas().slice().reverse(); const dentro = cp => { const [x, y, w, h] = caja2(cp), m = 6; return p[0] >= x - m && p[0] <= x + w + m && p[1] >= y - m && p[1] <= y + h + m };
  return ls.find(cp => !cp.oculta && (cp.tipo === "pedido" || activa(cp, t)) && dentro(cp)) || ls.find(cp => !cp.oculta && dentro(cp)) }
ov.addEventListener("pointerdown", ev => {
  if (!P || !nombre) return toast("Primero creá o elegí una pieza"); const p = aLogico(ev); ov.setPointerCapture(ev.pointerId); setPlay(false);
  const h = herramienta;
  if (h === "mover") { const cp = capaSel(), { s } = escalaPantalla(), m = cp && manija(cp);
    if (m && Math.hypot(p[0] - m[0], p[1] - m[1]) < 12 / s) { arrastre = { modo: "escalar", cp, p0: p, orig: { ...cp }, caja: caja2(cp) }; return }
    const hit = tocar(p); selId = hit?.id || null; pintarCapas(); if (hit) arrastre = { modo: "mover", cp: hit, p0: p, orig: { ...hit } }; return }
  if (h === "texto") { const cp = crear({ tipo: "texto", texto: "Texto nuevo", x: p[0], y: p[1], tam: 48, fuente: "Plex Sans", color: "#f2efe8", fondo: null, alin: "left", entrada: "fundido" }); herr("mover"); setTimeout(() => { const i = document.querySelector('#capa-props [data-k="texto"]'); i && (i.focus(), i.select()) }, 50); return }
  if (h === "imagen") { herr("mover"); alMaterial = ruta => { const cp = crear({ tipo: "imagen", ruta, x: p[0], y: p[1], w: 320, rot: 0, borde: true, entrada: "golpe" }) }; abrirMaterial(null); return }
  if (h === "pedido") { crear({ tipo: "pedido", x: p[0], y: p[1], texto: "" }); herr("mover"); setTimeout(() => document.querySelector('#capa-props [data-k="texto"]')?.focus(), 50); return }
  arrastre = { modo: "crear", tipo: h, p0: p, p, preview: true };
});
ov.addEventListener("pointermove", ev => {
  const p = aLogico(ev); if (!arrastre) { ov.style.cursor = herramienta !== "mover" ? "crosshair" : (tocar(p) ? "move" : "default"); return }
  const a = arrastre, dx = p[0] - a.p0[0], dy = p[1] - a.p0[1]; a.p = p;
  if (a.modo === "mover") { a.cp.x = a.orig.x + dx; a.cp.y = a.orig.y + dy; if (a.cp.tipo === "flecha") { a.cp.x2 = a.orig.x2 + dx; a.cp.y2 = a.orig.y2 + dy } }
  if (a.modo === "escalar") { const cp = a.cp, [x, y, w] = a.caja;
    if (cp.tipo === "flecha") { cp.x2 = p[0]; cp.y2 = p[1] } else if (cp.tipo === "texto") cp.tam = Math.max(8, a.orig.tam * Math.max(.1, (p[0] - x) / w)); else if (cp.tipo === "imagen") cp.w = Math.max(20, p[0] - cp.x); else { cp.w = p[0] - cp.x; cp.h = p[1] - cp.y } }
});
ov.addEventListener("pointerup", ev => {
  const a = arrastre; arrastre = null; if (!a) return;
  if (a.modo === "mover" || a.modo === "escalar") { if (a.p) { cambio(); pintarProps() } return }
  let [x0, y0] = a.p0, [x1, y1] = a.p; const chico = Math.hypot(x1 - x0, y1 - y0) < 8;
  if (a.tipo === "flecha") { if (chico) { x1 = x0 + 140; y1 = y0 - 60 } crear({ tipo: "flecha", x: x0, y: y0, x2: x1, y2: y1, color: "#c8102e", grosor: 5, curva: .2, entrada: "trazo" }) }
  else { if (chico) { x0 -= 90; y0 -= 60; x1 = x0 + 180; y1 = y0 + 120 } const r = { x: Math.min(x0, x1), y: Math.min(y0, y1), w: Math.abs(x1 - x0), h: Math.abs(y1 - y0) };
    if (a.tipo === "circulo") crear({ tipo: "circulo", ...r, color: "#c8102e", grosor: 5, entrada: "trazo" });
    if (a.tipo === "resaltador") crear({ tipo: "resaltador", ...r, color: "#ffd84a", entrada: "trazo" });
    if (a.tipo === "estilo") abrirEstilos(slug => crear({ tipo: "estilo", slug, ...r, encaje: "ventana", mascara: "rect", mezcla: "source-over", opacidad: 1, desfase: 0, entrada: "fundido" })) }
  herr("mover");
});
document.addEventListener("keydown", ev => {
  if (/INPUT|TEXTAREA|SELECT/.test(ev.target.tagName)) return;
  if ((ev.metaKey || ev.ctrlKey) && ev.code === "KeyZ") { ev.preventDefault(); deshacer(); return }
  const cp = capaSel(); if (!cp) return;
  if (ev.code === "Backspace" || ev.code === "Delete") { ev.preventDefault(); borrarCapa(cp.id) }
  if ((ev.metaKey || ev.ctrlKey) && ev.code === "KeyD") { ev.preventDefault(); const c2 = JSON.parse(JSON.stringify(cp)); c2.id = nuevoId(); c2.x += 20; c2.y += 20; if (c2.x2 != null) { c2.x2 += 20; c2.y2 += 20 } capas().push(c2); selId = c2.id; cambio(); pintarCapas() }
  const paso = ev.shiftKey ? 10 : 1, mv = { ArrowLeft: [-paso, 0], ArrowRight: [paso, 0], ArrowUp: [0, -paso], ArrowDown: [0, paso] }[ev.code];
  if (mv && ev.altKey) { ev.preventDefault(); cp.x += mv[0]; cp.y += mv[1]; if (cp.x2 != null) { cp.x2 += mv[0]; cp.y2 += mv[1] } cambio() }
});
function herr(h) { herramienta = h; document.querySelectorAll("#herramientas button").forEach(b => b.setAttribute("aria-pressed", b.dataset.h === h)) }
document.querySelectorAll("#herramientas button").forEach(b => b.onclick = () => herr(b.dataset.h));
function borrarCapa(id) { P.capas = capas().filter(c => c.id !== id); if (selId === id) selId = null; OFF.delete(id); cambio(); pintarCapas() }

// ---------- deshacer ----------
const HIST = []; let foto = null;
function sacarFoto() { const s = JSON.stringify(P); if (foto && foto !== s) { HIST.push(foto); if (HIST.length > 80) HIST.shift() } foto = s }
async function deshacer() { if (!HIST.length) return toast("Nada para deshacer"); const s = HIST.pop(); P = JSON.parse(s); foto = s; await aplicarImagenes(); pintarTodo(); guardar(); toast("Deshecho") }

// ---------- panel de capas ----------
function resumen(cp) { if (cp.tipo === "texto" || cp.tipo === "pedido") return (cp.texto || "(vacío)").split("\n")[0].slice(0, 34); if (cp.tipo === "imagen") return cp.ruta.split("/").pop(); if (cp.tipo === "estilo") return ESTILOS.find(e => e.slug === cp.slug)?.nombre || cp.slug; return "" }
function pintarCapas() {
  const box = $("lista-capas"); if (!box || !P) return; box.textContent = ""; const ls = capas();
  if (!ls.length) box.innerHTML = '<p class="nota">Sin capas. Elegí una herramienta arriba de la pantalla y tocá donde la querés.</p>';
  ls.slice().reverse().forEach(cp => { const fila = document.createElement("div"); fila.className = "capa" + (cp.id === selId ? " sel" : "") + (cp.oculta ? " oculta" : "");
    const nom = document.createElement("button"); nom.type = "button"; nom.className = "nom"; nom.innerHTML = "<b></b> <span></span><small></small>"; nom.querySelector("b").textContent = NOMBRES_TIPO[cp.tipo]; nom.querySelector("span").textContent = resumen(cp); nom.querySelector("small").textContent = `${(cp.desde || 0).toFixed(1)}–${cp.hasta == null ? "fin" : cp.hasta.toFixed(1)} s`;
    nom.onclick = () => { selId = cp.id; t = Math.max(t, 0); if (!activa(cp, t) && cp.tipo !== "pedido") t = (cp.desde || 0) + .6; setPlay(false); pintarCapas() };
    const bt = (txt, tit, fn) => { const b = document.createElement("button"); b.type = "button"; b.textContent = txt; b.title = tit; b.onclick = fn; return b };
    const i = ls.indexOf(cp);
    fila.append(nom, bt("↑", "Subir", () => { if (i < ls.length - 1) { [ls[i], ls[i + 1]] = [ls[i + 1], ls[i]]; cambio(); pintarCapas() } }), bt("↓", "Bajar", () => { if (i > 0) { [ls[i], ls[i - 1]] = [ls[i - 1], ls[i]]; cambio(); pintarCapas() } }),
      bt(cp.oculta ? "◌" : "●", "Mostrar / ocultar", () => { cp.oculta = !cp.oculta; cambio(); pintarCapas() }), bt("✕", "Borrar", () => borrarCapa(cp.id)));
    box.append(fila) });
  pintarProps();
}
function campo(cp, k, tipo, etiqueta, opciones, extra = {}) {
  const l = document.createElement("label"); if (extra.ancho) l.style.gridColumn = "1/-1"; l.append(etiqueta); let inp;
  if (tipo === "select") { inp = document.createElement("select"); Object.entries(opciones).forEach(([v, n]) => inp.append(new Option(n, v))); inp.value = cp[k] ?? Object.keys(opciones)[0] }
  else if (tipo === "area") { inp = document.createElement("textarea"); inp.value = cp[k] ?? ""; inp.style.minHeight = "64px" }
  else if (tipo === "check") { l.className = "fila"; inp = document.createElement("input"); inp.type = "checkbox"; inp.checked = !!cp[k]; l.prepend(inp); inp.dataset.k = k; inp.onchange = () => { cp[k] = inp.checked; cambio() }; return l }
  else if (tipo === "color") { inp = document.createElement("select"); inp.append(new Option(extra.nulo || "—", "")); Object.entries(COLORES_CAPA).forEach(([n, c]) => { const o = new Option(n, c); o.style.background = c; inp.append(o) }); inp.value = cp[k] || "" }
  else { inp = document.createElement("input"); inp.type = tipo; Object.assign(inp, opciones || {}); inp.value = cp[k] ?? "" }
  inp.dataset.k = k;
  inp.oninput = inp.onchange = () => { let v = inp.value; if (tipo === "number" || tipo === "range") v = v === "" ? null : +v; if (tipo === "color") v = v || null; cp[k] = v; cambio(); if (k === "texto") pintarCapasLista() };
  l.append(inp); return l;
}
let _pcl = null; function pintarCapasLista() { clearTimeout(_pcl); _pcl = setTimeout(() => { const f = document.activeElement; const k = f?.dataset?.k; pintarCapas(); if (k) { const i = document.querySelector(`#capa-props [data-k="${k}"]`); if (i) { i.focus(); try { i.setSelectionRange(i.value.length, i.value.length) } catch (_) {} } } }, 500) }
function pintarProps() {
  const box = $("capa-props"); if (!box) return; box.textContent = ""; const cp = capaSel(); if (!cp) { box.innerHTML = '<p class="nota">Tocá una capa en la pantalla (herramienta Mover) o en la lista para editarla. Mover: arrastrar · tamaño: el cuadradito · Alt+flechas: ajuste fino · ⌘D duplicar · ⌫ borrar · ⌘Z deshacer.</p>'; return }
  const g = document.createElement("div"); g.className = "dos"; const A = (...xs) => g.append(...xs);
  if (cp.tipo === "texto") A(campo(cp, "texto", "area", "Texto (Enter = otra línea)", null, { ancho: 1 }), campo(cp, "fuente", "select", "Fuente", Object.fromEntries(Object.keys(FUENTES_CAPA).map(k => [k, k]))), campo(cp, "tam", "number", "Tamaño", { min: 8, max: 300 }), campo(cp, "color", "color", "Color"), campo(cp, "fondo", "color", "Caja detrás", null, { nulo: "sin caja" }), campo(cp, "alin", "select", "Alineación", { left: "Izquierda", center: "Centro", right: "Derecha" }), campo(cp, "entrada", "select", "Entrada", ENTRADAS));
  if (cp.tipo === "imagen") { A(campo(cp, "w", "number", "Ancho", { min: 20, max: 1400 }), campo(cp, "rot", "number", "Giro (°)", { min: -45, max: 45 }), campo(cp, "entrada", "select", "Entrada", ENTRADAS), campo(cp, "borde", "check", "Borde de foto impresa"));
    const b = document.createElement("button"); b.type = "button"; b.textContent = "Cambiar imagen…"; b.style.gridColumn = "1/-1"; b.onclick = () => { alMaterial = r => { cp.ruta = r; cambio(); pintarCapas() }; abrirMaterial(null) }; A(b) }
  if (cp.tipo === "circulo" || cp.tipo === "flecha") A(campo(cp, "color", "color", "Color"), campo(cp, "grosor", "number", "Grosor", { min: 1, max: 30 }), campo(cp, "entrada", "select", "Entrada", ENTRADAS));
  if (cp.tipo === "flecha") A(campo(cp, "curva", "range", "Curva", { min: -.6, max: .6, step: .02 }));
  if (cp.tipo === "resaltador") A(campo(cp, "color", "color", "Color"));
  if (cp.tipo === "estilo") { A(campo(cp, "mezcla", "select", "Mezcla", MEZCLAS), campo(cp, "opacidad", "range", "Opacidad", { min: 0, max: 1, step: .05 }), campo(cp, "mascara", "select", "Forma", { rect: "Rectángulo", elipse: "Óvalo", ninguna: "Pantalla entera" }), campo(cp, "encaje", "select", "Encaje", { ventana: "Ventana (tamaño real)", escalar: "Achicado adentro" }), campo(cp, "desfase", "number", "Adelantar su tiempo (s)", { step: .1 }), campo(cp, "entrada", "select", "Entrada", ENTRADAS));
    const b = document.createElement("button"); b.type = "button"; b.textContent = "Cambiar estilo de esta capa…"; b.style.gridColumn = "1/-1"; b.onclick = () => abrirEstilos(slug => { cp.slug = slug; cambio(); pintarCapas() }); A(b) }
  if (cp.tipo === "pedido") { A(campo(cp, "texto", "area", "¿Qué querés acá? (lo leo yo)", null, { ancho: 1 })); const n = document.createElement("p"); n.className = "nota"; n.style.gridColumn = "1/-1"; n.textContent = `Lugar: (${Math.round(cp.x)}, ${Math.round(cp.y)}) en 960×540 · segundo ${(cp.desde || 0).toFixed(1)}${cp.hecho ? " · ✓ hecho" : ""}`; A(n) }
  if (cp.tipo !== "pedido") { const d = campo(cp, "desde", "number", "Desde (s)", { step: .1, min: 0 }), h = campo(cp, "hasta", "number", "Hasta (s, vacío = fin)", { step: .1, min: 0 });
    const ya = (k) => { const b = document.createElement("button"); b.type = "button"; b.textContent = k === "desde" ? "desde acá" : "hasta acá"; b.onclick = () => { cp[k] = Math.round(t * 10) / 10; cambio(); pintarCapas() }; return b }; A(d, h, ya("desde"), ya("hasta")) }
  else { const b = document.createElement("button"); b.type = "button"; b.textContent = "mover al segundo actual"; b.onclick = () => { cp.desde = Math.round(t * 10) / 10; cambio(); pintarProps() }; A(b) }
  const tit = document.createElement("div"); tit.className = "nota"; tit.style.gridColumn = "1/-1"; tit.innerHTML = `<b style="color:var(--fg)">${NOMBRES_TIPO[cp.tipo]}</b>`; g.prepend(tit);
  box.append(g);
}
