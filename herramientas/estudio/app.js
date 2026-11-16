// ===================== ESTUDIO LOS 11 =====================
const CATS = /*CATS*/{};
const CAT_ES = { "Graphic & Type": "Gráfica y tipografía", "Instruments & Evidence": "Instrumentos y pruebas", "Film & Tape": "Película y cinta",
  "Line Diagrams": "Diagramas de línea", "3D & Miniature": "3D y miniatura", "Edit & Documentary": "Montaje y documental", "Sketch & Board": "Boceto y pizarra",
  "Light & Lines": "Luz y líneas", "Painting & Illustration": "Pintura e ilustración", "Cartoons": "Dibujos animados", "Screens & Interfaces": "Pantallas e interfaces",
  "Data & Maps": "Datos y mapas", "Games": "Juegos", "Traditional Crafts": "Oficios tradicionales", "Print & Printmaking": "Impresión y grabado" };
ESTILOS.forEach(e => e.cat = e.cat || CAT_ES[CATS[e.slug]] || "Propios");

const $ = id => document.getElementById(id);
const MARCA = { noche: "#0c160c", fondo: "#1a2e1a", panel: "#2d4a2d", medio: "#4a7c4a", acento: "#7ab37a", claro: "#c8e6c8", texto: "#f2efe8", suave: "#b9c4b5", rojo: "#c8102e" };
const SLOTS = { fotografos: "Retrato (foto 1)", brazos: "Festejo (foto 2)", jueguitos: "Estadio (foto 3)", freeze: "Cuadro de jugada", dolar: "Billete / objeto", rec: "Recorte sin fondo" };
const ORIGEN = { fotografos: "img/fotografos.jpg", brazos: "img/brazos.jpg", jueguitos: "img/jueguitos.jpg", freeze: "img/freeze.jpg", dolar: "img/dolar.jpg", rec: "img/recorte.png" };
const T0 = { nombre: "Diego Armando Maradona", titulo: "El pase más caro de la historia", cifra: "US$ 7.500.000", anio: "1984" };
const vid = $("vid");

// ---------- estado ----------
let proyecto = null, nombre = null, P = null, mtime = 0, guardando = null;
let t = 0, play = false, vel = 1, ultimo = 0;
const nuevaPieza = slug => ({ estilo: slug, T: { ...T0 }, textos: {}, imagenes: {}, marca: { modo: "original", intensidad: 1, fuentes: false }, tiempo: { dur: null, hold: 0 }, pedidos: "", codigo: "", capas: [] });
const est = () => ESTILOS.find(e => e.slug === P?.estilo) || ESTILOS[0];
const durEst = () => +P?.tiempo?.dur || est().dur;
const total = () => durEst() + (+P?.tiempo?.hold || 0);
const tEst = tt => Math.min(tt, durEst()) * est().dur / durEst();

// ---------- imágenes: getters que registran qué usa cada estilo ----------
const ORIG = {}, ACTUAL = {}, USADOS = new Set(); let registrar = false;
Object.keys(SLOTS).forEach(k => Object.defineProperty(IMG, k, { configurable: true, get() { if (registrar) USADOS.add(k); return ACTUAL[k] }, set(v) { ACTUAL[k] = v } }));
const limpiarCache = () => { for (const k in cache) delete cache[k] };
const cargarImg = src => new Promise((ok, mal) => { const i = new Image(); i.onload = () => ok(i); i.onerror = mal; i.src = src });
async function armarSlot(k) { // encuadra la imagen elegida al tamaño que espera el estilo
  const cfg = P.imagenes[k]; if (!cfg?.ruta) { ACTUAL[k] = ORIG[k]; return }
  const im = await cargarImg(`/p/${proyecto}/${cfg.ruta}`); const o = ORIG[k], w = o.width, h = o.height, s = lienzo(w, h), x = s.getContext("2d");
  const z = +cfg.zoom || 1, dx = +cfg.x || 0, dy = +cfg.y || 0;
  if (k === "rec") { const f = Math.min(w / im.width, h / im.height) * z, iw = im.width * f, ih = im.height * f; x.drawImage(im, (w - iw) / 2 + dx * w / 2, h - ih + dy * h / 2, iw, ih) }
  else { const f = Math.max(w / im.width, h / im.height) * z, iw = im.width * f, ih = im.height * f; x.drawImage(im, (w - iw) / 2 * (1 - dx), (h - ih) / 2 * (1 - dy), iw, ih) }
  ACTUAL[k] = s;
}
async function aplicarImagenes() { await Promise.all(Object.keys(SLOTS).map(armarSlot)); limpiarCache() }

// ---------- textos: se pueden reemplazar todos los que pasan por texto/tipeo/tiza/trazoTexto ----------
const VISTOS = new Map(); let TIPEADOS = new Set(), muestraActual = 0;
const MONO = /'?(Space Mono|VT323|Press Start 2P|monospace)'?/;
const DISPLAY = /'?(Anton|Bebas Neue|Bangers|Rubik Mono One|Limelight|Monoton|Cinzel|UnifrakturMaguntia|Michroma|Fredoka|Permanent Marker|Special Elite|Caveat|IBM Plex Sans)'?/;
function fuenteMarca(f) { if (!P?.marca?.fuentes) return f; if (MONO.test(f)) return f.replace(MONO, "'JetBrains Mono'"); if (DISPLAY.test(f)) { f = f.replace(DISPLAY, "'IBM Plex Sans'"); return /^\s*(\d00|bold|italic)/.test(f) ? f : "600 " + f } return f }
const reemplazo = s => (P?.textos?.[s] ?? "") !== "" ? P.textos[s] : s;
function ver(s) { if (!registrar || !s || String(s).trim().length < 2) return; const v = VISTOS.get(s) || new Set(); v.add(muestraActual); VISTOS.set(s, v) }
const _texto = texto, _tipeo = tipeo, _tiza = tiza, _trazo = trazoTexto;
tipeo = (s, k) => { s = String(s); ver(s); const r = _tipeo(reemplazo(s), k); TIPEADOS.add(r); return r };
texto = (c, s, x, y, font, color, al, base) => { s = String(s); if (!TIPEADOS.has(s)) { ver(s); s = reemplazo(s) } _texto(c, s, x, y, fuenteMarca(font), color, al, base) };
tiza = (c, s, x, y, size, fam, color, f, al) => { s = String(s); if (!TIPEADOS.has(s)) { ver(s); s = reemplazo(s) } if (P?.marca?.fuentes) fam = "'IBM Plex Sans'"; _tiza(c, s, x, y, size, fam, color, f, al) };
trazoTexto = (c, s, x, y, font, color, lw, al) => { s = String(s); if (!TIPEADOS.has(s)) { ver(s); s = reemplazo(s) } _trazo(c, s, x, y, fuenteMarca(font), color, lw, al) };

// ---------- colores de la marca (post-proceso con tabla de 32³) ----------
const RAMPA = ["noche", "fondo", "panel", "medio", "acento", "claro", "texto"].map(k => hex(MARCA[k]));
const TODOS = Object.values(MARCA).map(hex);
const MODOS = { original: "Original", mapa: "Mapa de marca", paleta: "Paleta exacta", duotono: "Duotono verde" };
let LUT = null, lutDe = "";
function armarLUT(modo) {
  const L = new Uint8Array(32768 * 3), rojo = hex(MARCA.rojo), d1 = hex(MARCA.noche), d2 = hex(MARCA.claro);
  for (let r = 0; r < 32; r++) for (let g = 0; g < 32; g++) for (let b = 0; b < 32; b++) {
    const R = r * 8 + 4, G = g * 8 + 4, B = b * 8 + 4, l = (.299 * R + .587 * G + .114 * B) / 255; let o;
    if (modo === "paleta") { let best = 1e9; for (const p of TODOS) { const dr = R - p[0], dg = G - p[1], db = B - p[2], d = 2 * dr * dr + 4 * dg * dg + 3 * db * db; if (d < best) { best = d; o = p } } }
    else if (modo === "duotono") o = [lerp(d1[0], d2[0], l), lerp(d1[1], d2[1], l), lerp(d1[2], d2[2], l)];
    else { const u = l * (RAMPA.length - 1), i = Math.min(RAMPA.length - 2, Math.floor(u)), f = u - i; o = [0, 1, 2].map(j => lerp(RAMPA[i][j], RAMPA[i + 1][j], f));
      const mx = Math.max(R, G, B), mn = Math.min(R, G, B), sat = mx ? (mx - mn) / mx : 0; if (R > G * 1.5 && R > B * 1.4 && sat > .45 && mx > 90) { const k = cl((sat - .45) * 3); o = o.map((v, j) => lerp(v, rojo[j] * (.6 + .5 * l), k)) } }
    const i3 = ((r << 10) | (g << 5) | b) * 3; L[i3] = o[0]; L[i3 + 1] = o[1]; L[i3 + 2] = o[2] }
  return L;
}
function aplicarMarca(c) {
  const m = P?.marca; if (!m || m.modo === "original" || !(+m.intensidad > 0)) return;
  if (lutDe !== m.modo) { LUT = armarLUT(m.modo); lutDe = m.modo }
  const w = c.canvas.width, h = c.canvas.height, id = c.getImageData(0, 0, w, h), d = id.data, k = +m.intensidad;
  for (let i = 0; i < d.length; i += 4) { const j = (((d[i] >> 3) << 10) | ((d[i + 1] >> 3) << 5) | (d[i + 2] >> 3)) * 3;
    if (k >= 1) { d[i] = LUT[j]; d[i + 1] = LUT[j + 1]; d[i + 2] = LUT[j + 2] } else { d[i] += (LUT[j] - d[i]) * k; d[i + 1] += (LUT[j + 1] - d[i + 1]) * k; d[i + 2] += (LUT[j + 2] - d[i + 2]) * k } }
  c.putImageData(id, 0, 0);
}

// ---------- dibujo ----------
let extra = null, extraDe = null;
function capaExtra() { const src = P?.codigo || ""; if (src !== extraDe) { extraDe = src; try { extra = src.trim() ? new Function("c", "t", "T", "P", src) : null } catch (e) { console.error("codigo de la pieza", e); extra = null } } return extra }
function dibujarEn(c, e, tt, T, env, conMarca = true) {
  TIPEADOS = new Set();
  c.save(); c.setTransform(c.canvas.width / W, 0, 0, c.canvas.height / H, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = "source-over"; c.imageSmoothingEnabled = true; sinSombra(c); c.setLineDash([]); c.lineCap = "butt"; c.lineJoin = "miter";
  try { e.draw(c, tt, T, env); if (!env.miniatura && !env.capa) { dibujarCapas(c, env.tg ?? tt, env); const x = capaExtra(); if (x) { c.save(); x(c, env.tg ?? tt, T, P); c.restore() } } }
  catch (err) { console.error(e.slug, err); c.fillStyle = "#300"; c.fillRect(0, 0, W, H); _texto(c, "error: " + err.message, 20, 40, "20px monospace", "#f88") }
  c.restore(); if (conMarca) aplicarMarca(c);
}
const cv = $("cv"), ctx = cv.getContext("2d", { willReadFrequently: true });
function frame() { if (!P) return; dibujarEn(ctx, est(), tEst(t), P.T, { vid, reproduciendo: play && t < durEst(), tg: t }); dibujarOverlay(); $("scrub").value = t; $("tiempo").textContent = `${t.toFixed(1)} / ${total().toFixed(1)} s` }
function loop(ts) { if (play) { t += Math.min(.1, (ts - ultimo) / 1000) * vel; if (t >= total()) t = 0 } ultimo = ts; frame(); requestAnimationFrame(loop) }
function setPlay(v) { play = v; $("play").textContent = v ? "❚❚ Pausa" : "▶ Play"; if (!v && !vid.paused) vid.pause() }
$("play").onclick = () => setPlay(!play);
$("scrub").oninput = e => { t = +e.target.value; setPlay(false) };
$("vel").onclick = () => { vel = vel === 1 ? .5 : vel === .5 ? .25 : 1; $("vel").textContent = vel + "×" };
document.addEventListener("keydown", e => { if (/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return; if (e.code === "Space") { e.preventDefault(); setPlay(!play) } });

// ---------- escaneo: qué textos e imágenes usa el estilo ----------
const lienzoScan = lienzo(480, 270), cScan = lienzoScan.getContext("2d");
function escanear() {
  VISTOS.clear(); USADOS.clear(); registrar = true; const e = est();
  for (let k = 0; k <= 40; k++) { muestraActual = k; dibujarEn(cScan, e, e.dur * k / 40, P.T, { miniatura: true }, false) }
  registrar = false;
  const lista = [...VISTOS].filter(([s, v]) => v.size >= 2 || P.textos[s] !== undefined).map(([s]) => s).filter(s => !Object.values(P.T).some(v => String(v).toUpperCase() === s.toUpperCase()));
  Object.keys(P.textos).forEach(s => { if (!lista.includes(s)) lista.push(s) });
  pintarTextos(lista); pintarSlots();
}

// ---------- panel ----------
function estado(s) { $("estado").textContent = s }
function toast(s) { const el = $("toast"); el.textContent = s; el.classList.add("ver"); clearTimeout(el._t); el._t = setTimeout(() => el.classList.remove("ver"), 2600) }
function cambio(rehacer = false) { clearTimeout(guardando); estado("sin guardar…"); guardando = setTimeout(guardar, 600); if (rehacer) { clearTimeout(cambio._s); cambio._s = setTimeout(escanear, 400) } }
async function guardar() {
  if (!proyecto || !nombre) return; sacarFoto(); const r = await fetch(`/api/pieza?p=${proyecto}&n=${nombre}`, { method: "POST", body: JSON.stringify(P) }); const j = await r.json();
  if (j.ok) { mtime = j.mtime; estado("guardado · " + new Date().toLocaleTimeString().slice(0, 5)) } else estado("error al guardar: " + j.error);
}
document.querySelectorAll("[data-t]").forEach(inp => inp.oninput = () => { P.T[inp.dataset.t] = inp.value; cambio(true) });
function pintarTextos(lista) {
  const box = $("textos"); box.textContent = "";
  if (!lista.length) { box.innerHTML = '<p class="nota">Este estilo no tiene otros textos sueltos.</p>'; return }
  lista.forEach(s => { const d = document.createElement("label"); d.className = "txt"; const sm = document.createElement("small"); sm.textContent = s; sm.title = s;
    const inp = document.createElement("input"); inp.value = P.textos[s] ?? ""; inp.placeholder = s; inp.classList.toggle("cambiado", !!inp.value);
    inp.oninput = () => { if (inp.value) P.textos[s] = inp.value; else delete P.textos[s]; inp.classList.toggle("cambiado", !!inp.value); cambio() }; d.append(sm, inp); box.append(d) });
}
function pintarSlots() {
  const box = $("slots"); box.textContent = ""; const usados = Object.keys(SLOTS).filter(k => USADOS.has(k));
  if (est().video) box.insertAdjacentHTML("beforeend", '<p class="nota">Este estilo usa el clip de la jugada como video. Para otro clip, pedímelo.</p>');
  if (!usados.length) { box.insertAdjacentHTML("beforeend", '<p class="nota">Este estilo no usa fotos: todo es dibujo. Si querés sumar una, pedímelo.</p>'); return }
  usados.forEach(k => { const cfg = P.imagenes[k] || {}; const d = document.createElement("div"); d.className = "slot";
    const mini = document.createElement("div"); mini.className = "mini" + (k === "rec" ? " rec" : ""); mini.style.backgroundImage = `url("${cfg.ruta ? `/p/${proyecto}/${cfg.ruta}` : "/lemo/" + ORIGEN[k]}")`; mini.title = "Cambiar imagen"; mini.onclick = () => abrirMaterial(k);
    const txt = document.createElement("div"); txt.innerHTML = `<div class="t"></div><div class="r"></div><div class="acc"></div>`; txt.querySelector(".t").textContent = SLOTS[k]; txt.querySelector(".r").textContent = cfg.ruta || "(ejemplo de Maradona)";
    const b1 = document.createElement("button"); b1.type = "button"; b1.textContent = "Cambiar"; b1.onclick = () => abrirMaterial(k); txt.querySelector(".acc").append(b1);
    if (cfg.ruta) { const b2 = document.createElement("button"); b2.type = "button"; b2.textContent = "Volver al ejemplo"; b2.onclick = async () => { delete P.imagenes[k]; await armarSlot(k); limpiarCache(); cambio(); pintarSlots() }; txt.querySelector(".acc").append(b2) }
    d.append(mini, txt);
    if (cfg.ruta) { const enc = document.createElement("div"); enc.className = "enc";
      [["zoom", "Zoom", .5, 3, 1], ["x", "X", -1, 1, 0], ["y", "Y", -1, 1, 0]].forEach(([p, n, mn, mx, def]) => { const l = document.createElement("label"); l.textContent = n; const r = document.createElement("input"); r.type = "range"; r.min = mn; r.max = mx; r.step = .01; r.value = cfg[p] ?? def;
        r.oninput = async () => { cfg[p] = +r.value; await armarSlot(k); limpiarCache(); cambio() }; l.append(r); enc.append(l) }); d.append(enc) }
    box.append(d) });
}
// marca
$("paleta").append(...Object.entries(MARCA).map(([n, c]) => Object.assign(document.createElement("span"), { title: `${n} ${c}`, style: `background:${c}` })));
function pintarMarca() {
  const box = $("modos"); box.textContent = "";
  Object.entries(MODOS).forEach(([k, n]) => { const b = document.createElement("button"); b.type = "button"; b.textContent = n; b.setAttribute("aria-pressed", P.marca.modo === k); b.onclick = () => { P.marca.modo = k; pintarMarca(); cambio() }; box.append(b) });
  $("m-int").value = P.marca.intensidad ?? 1; $("m-fuentes").checked = !!P.marca.fuentes;
}
$("m-int").oninput = e => { P.marca.intensidad = +e.target.value; cambio() };
$("m-fuentes").onchange = e => { P.marca.fuentes = e.target.checked; cambio() };
// tiempo y pedidos
$("d-dur").oninput = e => { P.tiempo.dur = +e.target.value || null; $("scrub").max = total(); cambio() };
$("d-hold").oninput = e => { P.tiempo.hold = +e.target.value || 0; $("scrub").max = total(); cambio() };
$("pedidos").oninput = e => { P.pedidos = e.target.value; cambio() };

function pintarTodo() {
  const e = est(); $("e-nombre").textContent = e.nombre; $("e-slug").textContent = `${e.slug} · ${e.cat}`;
  $("info").innerHTML = ""; $("info").append(Object.assign(document.createElement("b"), { textContent: e.nombre + ". " }), e.que + " ", Object.assign(document.createElement("i"), { textContent: e.uso }));
  document.querySelectorAll("[data-t]").forEach(inp => inp.value = P.T[inp.dataset.t] ?? "");
  $("d-dur").value = durEst(); $("d-hold").value = P.tiempo.hold || 0; $("pedidos").value = P.pedidos || "";
  $("scrub").max = total(); $("snip").textContent = `{"archivo": "material/animaciones/${nombre}.mp4"}`;
  pintarMarca(); escanear(); pintarCapas();
}

// ---------- piezas ----------
async function listarPiezas(sel) {
  const l = await (await fetch(`/api/piezas?p=${proyecto}`)).json(); const s = $("pieza"); s.textContent = "";
  if (!l.length) s.append(new Option("(sin piezas: creá una →)", "")); l.forEach(n => s.append(new Option(n, n))); if (sel) s.value = sel; return l;
}
async function abrirPieza(n, silencioso = false) {
  if (!n) { nombre = null; P = null; return }
  const j = await (await fetch(`/api/pieza?p=${proyecto}&n=${n}`)).json(); if (j.error) return toast(j.error);
  const base = nuevaPieza(j.datos.estilo); P = { ...base, ...j.datos, marca: { ...base.marca, ...(j.datos.marca || {}) }, tiempo: { ...base.tiempo, ...(j.datos.tiempo || {}) }, T: { ...base.T, ...(j.datos.T || {}) } };
  if (n !== nombre) { selId = null; HIST.length = 0 } nombre = n; mtime = j.mtime; foto = JSON.stringify(P); try { localStorage.setItem("estudio:" + proyecto, n) } catch (_) {}
  await aplicarImagenes(); if (!silencioso) t = 0; pintarTodo(); estado(j.video ? "guardado · ya exportado" : "guardado"); if (!silencioso) setPlay(true);
}
$("pieza").onchange = e => abrirPieza(e.target.value);
$("proyecto").onchange = async e => { proyecto = e.target.value; const l = await listarPiezas(); let n = null; try { n = localStorage.getItem("estudio:" + proyecto) } catch (_) {} n = l.includes(n) ? n : l[0]; $("pieza").value = n || ""; await abrirPieza(n); MATERIAL = null };
$("f-nueva").onsubmit = e => { e.preventDefault(); const n = $("n-nueva").value.trim().toLowerCase().replace(/\s+/g, "-"); if (!/^[\w\-]{1,80}$/.test(n)) return toast("Nombre: letras, números, - y _"); abrirEstilos(async slug => { nombre = n; P = nuevaPieza(slug); selId = null; HIST.length = 0; foto = JSON.stringify(P); await aplicarImagenes(); await guardar(); await listarPiezas(n); $("n-nueva").value = ""; t = 0; pintarTodo(); setPlay(true) }) };
// Claude (u otro) cambió el JSON → recargar
setInterval(async () => { if (!nombre || document.hidden) return; try { const j = await (await fetch(`/api/pieza?p=${proyecto}&n=${nombre}`)).json(); if (j.mtime && j.mtime > mtime + .01) { await abrirPieza(nombre, true); toast("La pieza se actualizó desde afuera") } } catch (_) {} }, 2000);

// ---------- modal de estilos ----------
let alElegir = null, filtro = "Todos";
function abrirEstilos(fn) { alElegir = fn; $("m-estilos").classList.add("abierto"); pintarFiltros(); pintarEstilos(); $("busca-estilo").focus() }
$("cambiar-estilo").onclick = () => abrirEstilos(slug => { P.estilo = slug; P.textos = {}; P.tiempo.dur = null; t = 0; limpiarCache(); pintarTodo(); cambio(); setPlay(true) });
function pintarFiltros() { const f = $("filtros"); f.textContent = ""; const n = {}; ESTILOS.forEach(e => n[e.cat] = (n[e.cat] || 0) + 1);
  ["Todos", ...Object.keys(n).sort((a, b) => a.localeCompare(b, "es"))].forEach(c => { const b = document.createElement("button"); b.type = "button"; b.textContent = `${c} ${c === "Todos" ? ESTILOS.length : n[c]}`; b.setAttribute("aria-pressed", c === filtro); b.onclick = () => { filtro = c; pintarFiltros(); pintarEstilos() }; f.append(b) }) }
const obsMini = new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting) { const m = en.target, e = ESTILOS[+m.dataset.i]; dibujarEn(m.getContext("2d"), e, e.poster, P?.T || T0, { miniatura: true }); obsMini.unobserve(m) } }), { rootMargin: "200px" });
function pintarEstilos() { const g = $("rej-estilos"), q = $("busca-estilo").value.toLowerCase(); g.textContent = "";
  ESTILOS.forEach((e, i) => { if (filtro !== "Todos" && e.cat !== filtro) return; if (q && !(e.nombre + e.slug + e.que + e.uso).toLowerCase().includes(q)) return;
    const b = document.createElement("button"); b.type = "button"; const m = document.createElement("canvas"); m.width = 384; m.height = 216; m.dataset.i = i;
    b.append(m, Object.assign(document.createElement("span"), { textContent: e.nombre }), Object.assign(document.createElement("small"), { textContent: e.slug })); b.title = e.que;
    b.onclick = () => { $("m-estilos").classList.remove("abierto"); alElegir && alElegir(e.slug) }; g.append(b); obsMini.observe(m) }) }
$("busca-estilo").oninput = pintarEstilos;

// ---------- modal de material ----------
let MATERIAL = null, slotMat = null, alMaterial = null;
async function abrirMaterial(k) { slotMat = k; $("mat-tit").textContent = k ? "Imagen para: " + SLOTS[k] : "Imagen para la capa"; $("mat-recortar").checked = k === "rec"; if (k) alMaterial = null; $("m-material").classList.add("abierto");
  if (!MATERIAL) MATERIAL = await (await fetch(`/api/material?p=${proyecto}`)).json(); pintarMaterial(); $("busca-mat").focus() }
function pintarMaterial() { const g = $("rej-mat"), q = $("busca-mat").value.toLowerCase(); g.textContent = "";
  MATERIAL.filter(r => !q || r.toLowerCase().includes(q)).forEach(r => { const b = document.createElement("button"); b.type = "button"; const im = document.createElement("img"); im.loading = "lazy"; im.src = `/p/${proyecto}/${r}`; im.alt = "";
    b.append(im, Object.assign(document.createElement("small"), { textContent: r })); b.onclick = () => elegirMaterial(r); g.append(b) }) }
$("busca-mat").oninput = pintarMaterial;
async function elegirMaterial(r) {
  $("m-material").classList.remove("abierto"); const k = slotMat;
  if ($("mat-recortar").checked && !r.startsWith("estudio/recortes/")) { estado("recortando (rembg)…"); toast("Sacando el fondo… (puede tardar unos segundos)");
    const j = await (await fetch(`/api/recorte?p=${proyecto}`, { method: "POST", body: JSON.stringify({ ruta: r }) })).json(); if (j.error) { estado("error en recorte"); return toast("Error: " + j.error.slice(0, 120)) } r = j.ruta; MATERIAL = null }
  if (alMaterial) { const f = alMaterial; alMaterial = null; return f(r) }
  P.imagenes[k] = { ruta: r, zoom: 1, x: 0, y: 0 }; await armarSlot(k); limpiarCache(); cambio(); pintarSlots();
}
document.querySelectorAll("[data-cerrar]").forEach(b => b.onclick = () => b.closest(".modal").classList.remove("abierto"));
document.querySelectorAll(".modal").forEach(m => m.onclick = e => { if (e.target === m) m.classList.remove("abierto") });
document.addEventListener("keydown", e => { if (e.code === "Escape") document.querySelectorAll(".modal.abierto").forEach(m => m.classList.remove("abierto")) });

// ---------- exportar ----------
$("exportar").onclick = async () => {
  if (!P) return; await guardar(); setPlay(false); const btn = $("exportar"); btn.disabled = true; const fps = 30, n = Math.round(total() * fps), e = est();
  const off = lienzo(1920, 1080), c = off.getContext("2d", { willReadFrequently: true }); const { id } = await (await fetch("/api/exportar/inicio", { method: "POST" })).json();
  const seek = () => new Promise(r => { if (!vid.seeking) return r(); vid.addEventListener("seeked", r, { once: true }); setTimeout(r, 1500) });
  try {
    for (let k = 0; k < n; k++) { const tt = tEst(k / fps), env = { vid, reproduciendo: false, tg: k / fps }; dibujarEn(c, e, tt, P.T, env);
      if (e.video || capas().some(x => x.tipo === "estilo" && ESTILOS.find(z => z.slug === x.slug)?.video)) { await seek(); dibujarEn(c, e, tt, P.T, env) }
      const blob = await new Promise(r => off.toBlob(r, "image/jpeg", .93)); await fetch(`/api/exportar/cuadro?id=${id}&k=${k}`, { method: "POST", body: blob });
      $("prog").style.width = (100 * (k + 1) / n).toFixed(1) + "%"; estado(`exportando ${k + 1}/${n}`) }
    estado("codificando…"); const j = await (await fetch(`/api/exportar/fin?id=${id}&p=${proyecto}&n=${nombre}&fps=${fps}`, { method: "POST" })).json();
    if (j.error) { estado("error al exportar"); toast("Error: " + j.error.slice(0, 160)) } else { estado("exportado · " + j.ruta); toast("Listo: " + j.ruta) }
  } finally { btn.disabled = false; setTimeout(() => $("prog").style.width = "0", 2500) }
};

// ---------- arranque ----------
(async () => {
  const fuentes = ["Anton", "Bebas Neue", "Special Elite", "Permanent Marker", "Bangers", "Monoton", "Limelight", "Space Mono", "Rubik Mono One", "VT323", "Press Start 2P", "Caveat", "UnifrakturMaguntia", "Michroma", "Fredoka", "Cinzel", "IBM Plex Sans", "JetBrains Mono"];
  await Promise.all([...Object.entries(ORIGEN).map(async ([k, src]) => { try { ORIG[k] = ACTUAL[k] = await cargarImg("/lemo/" + src) } catch (_) {} }), ...fuentes.map(f => document.fonts.load(`40px "${f}"`).catch(() => {}))]);
  const ps = await (await fetch("/api/proyectos")).json(); ps.forEach(p => $("proyecto").append(new Option(p, p)));
  let q; try { q = new URLSearchParams(location.search) } catch (_) { q = new URLSearchParams() }
  $("proyecto").value = q.get("p") || (ps.includes("argentina-1986") ? "argentina-1986" : ps[0]); proyecto = $("proyecto").value;
  const l = await listarPiezas(); let n = q.get("n"); try { n = n || localStorage.getItem("estudio:" + proyecto) } catch (_) {} n = l.includes(n) ? n : l[0]; $("pieza").value = n || "";
  if (n) await abrirPieza(n); else { estado("creá una pieza: nombre + «Nueva pieza»"); P = nuevaPieza("halftone-dossier"); pintarTodo(); nombre = null }
  if (q.has("t")) { t = +q.get("t"); setPlay(false) }
  requestAnimationFrame(ts => { ultimo = ts; loop(ts) });
  if (q.has("exportar") && nombre) { await $("exportar").onclick(); document.title = "EXPORTADO " + $("estado").textContent }
})();
