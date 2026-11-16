// ---------- reproductor ----------
const CATS = /*CATS*/{};
const CAT_ES = { "Graphic & Type": "Gráfica y tipografía", "Instruments & Evidence": "Instrumentos y pruebas", "Film & Tape": "Película y cinta",
  "Line Diagrams": "Diagramas de línea", "3D & Miniature": "3D y miniatura", "Edit & Documentary": "Montaje y documental", "Sketch & Board": "Boceto y pizarra",
  "Light & Lines": "Luz y líneas", "Painting & Illustration": "Pintura e ilustración", "Cartoons": "Dibujos animados", "Screens & Interfaces": "Pantallas e interfaces",
  "Data & Maps": "Datos y mapas", "Games": "Juegos", "Traditional Crafts": "Oficios tradicionales", "Print & Printmaking": "Impresión y grabado" };
ESTILOS.forEach(e => e.cat = CAT_ES[CATS[e.slug]] || "Otros");
const cv = document.getElementById("cv"), ctx = cv.getContext("2d"), vid = document.getElementById("vid");
const $ = id => document.getElementById(id);
let actual = 0, t = 0, play = false, vel = 1, ultimo = 0, listo = false, filtro = "Todos";
function T() { return { nombre: $("t-nombre").value || " ", titulo: $("t-titulo").value || " ", cifra: $("t-cifra").value || "0", anio: $("t-anio").value || "1984" } }
function dibujar(c, est, tt, env) {
  c.save(); c.setTransform(c.canvas.width / W, 0, 0, c.canvas.height / H, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = "source-over"; c.imageSmoothingEnabled = true; sinSombra(c); c.setLineDash([]); c.lineCap = "butt"; c.lineJoin = "miter";
  try { est.draw(c, tt, T(), env) } catch (e) { console.error(est.slug, e); c.fillStyle = "#300"; c.fillRect(0, 0, W, H); texto(c, "error: " + est.slug, 20, 40, "20px monospace", "#f88") }
  c.restore();
}
function frame() { if (!listo) return; dibujar(ctx, ESTILOS[actual], t, { vid, reproduciendo: play }); $("scrub").value = t; $("tiempo").textContent = `${t.toFixed(1)} / ${ESTILOS[actual].dur.toFixed(1)} s` }
function loop(ts) { if (play) { const dt = Math.min(.1, (ts - ultimo) / 1000) * vel; t += dt; if (t >= ESTILOS[actual].dur) t = 0 } ultimo = ts; frame(); requestAnimationFrame(loop) }
function visibles() { return ESTILOS.map((e, i) => i).filter(i => filtro === "Todos" || ESTILOS[i].cat === filtro) }
function elegir(i, auto = true) {
  actual = i; const e = ESTILOS[i]; t = 0; $("scrub").max = e.dur;
  $("nombre").textContent = e.nombre; $("slug").textContent = `${e.slug} · ${e.cat}`; $("que").textContent = e.que; $("uso").textContent = e.uso;
  document.querySelectorAll(".grilla button").forEach(b => b.setAttribute("aria-current", +b.dataset.i === i ? "true" : "false"));
  try { if (location.hash !== "#" + e.slug) history.replaceState(null, "", "#" + e.slug) } catch (_) {}
  if (!e.video && !vid.paused) vid.pause();
  setPlay(auto);
}
function setPlay(v) { play = v; $("play").textContent = v ? "❚❚ Pausa" : "▶ Play"; if (!v && !vid.paused) vid.pause() }
function paso(d) { const v = visibles(), k = v.indexOf(actual); const n = v[(k + d + v.length) % v.length]; elegir(n ?? 0); }
$("play").onclick = () => setPlay(!play);
$("ant").onclick = () => paso(-1);
$("sig").onclick = () => paso(1);
$("scrub").oninput = e => { t = +e.target.value; setPlay(false) };
$("vel").onclick = () => { vel = vel === 1 ? .5 : vel === .5 ? .25 : 1; $("vel").textContent = vel + "×" };
document.addEventListener("keydown", e => { if (e.target.tagName === "INPUT") return; if (e.code === "Space") { e.preventDefault(); setPlay(!play) } if (e.code === "ArrowRight") paso(1); if (e.code === "ArrowLeft") paso(-1) });
$("textos").addEventListener("submit", e => e.preventDefault());
let pendiente = null;
$("textos").addEventListener("input", () => { clearTimeout(pendiente); pendiente = setTimeout(() => document.querySelectorAll(".grilla canvas").forEach(m => m.dataset.hecho && miniatura(m)), 300) });
window.addEventListener("hashchange", () => { const i = ESTILOS.findIndex(e => "#" + e.slug === location.hash); if (i >= 0 && i !== actual) elegir(i) });

function miniatura(m) { const i = +m.dataset.i; dibujar(m.getContext("2d"), ESTILOS[i], ESTILOS[i].poster, { miniatura: true }); m.dataset.hecho = "1" }
const obs = "IntersectionObserver" in window ? new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting && listo) { miniatura(en.target); obs.unobserve(en.target) } }), { rootMargin: "300px" }) : null;
function armarGrilla() {
  const g = $("grilla"); g.textContent = "";
  const v = visibles(); $("cuenta").textContent = filtro === "Todos" ? `Catálogo · ${ESTILOS.length} estilos` : `${filtro} · ${v.length}`;
  v.forEach(i => { const e = ESTILOS[i]; const b = document.createElement("button"); b.type = "button"; b.dataset.i = i; b.setAttribute("aria-current", i === actual ? "true" : "false");
    const m = document.createElement("canvas"); m.width = 384; m.height = 216; m.dataset.i = i; const s = document.createElement("span"); s.textContent = e.nombre; const sm = document.createElement("small"); sm.textContent = e.slug;
    b.append(m, s, sm); b.onclick = () => { elegir(i); window.scrollTo({ top: 0, behavior: "smooth" }) }; g.append(b);
    if (obs && listo) obs.observe(m); else if (listo) miniatura(m) });
}
function armarFiltros() {
  const f = $("filtros"); f.textContent = ""; const cuenta = {}; ESTILOS.forEach(e => cuenta[e.cat] = (cuenta[e.cat] || 0) + 1);
  ["Todos", ...Object.keys(cuenta).sort((a, b) => a.localeCompare(b, "es"))].forEach(c => { const b = document.createElement("button"); b.type = "button"; b.textContent = c; const n = document.createElement("span"); n.textContent = c === "Todos" ? ESTILOS.length : cuenta[c]; b.append(n);
    b.setAttribute("aria-pressed", c === filtro ? "true" : "false"); b.onclick = () => { filtro = c; armarFiltros(); armarGrilla() }; f.append(b) });
}

(async () => {
  const fuentes = ["Anton", "Bebas Neue", "Special Elite", "Permanent Marker", "Bangers", "Monoton", "Limelight", "Space Mono", "Rubik Mono One", "VT323", "Press Start 2P", "Caveat", "UnifrakturMaguntia", "Michroma", "Fredoka", "Cinzel", "IBM Plex Sans"];
  await Promise.all([cargar("brazos", "img/brazos.jpg"), cargar("jueguitos", "img/jueguitos.jpg"), cargar("fotografos", "img/fotografos.jpg"), cargar("dolar", "img/dolar.jpg"), cargar("freeze", "img/freeze.jpg"), cargar("rec", "img/recorte.png"),
    ...fuentes.map(f => document.fonts.load(`40px "${f}"`).catch(() => {}))]);
  listo = true;
  let q; try { q = new URLSearchParams(location.search) } catch (_) { q = new URLSearchParams() }
  if (q.has("hoja")) { const L = q.get("hoja").split(","); document.body.classList.add("hoja"); filtro = "Todos";
    const g = $("grilla"); armarFiltros(); g.textContent = "";
    L.forEach(sl => { const i = ESTILOS.findIndex(e => e.slug === sl); if (i < 0) return; const m = document.createElement("canvas"); m.width = 480; m.height = 270; m.dataset.i = i; m.style.width = "340px"; const d = document.createElement("div"); d.append(m, Object.assign(document.createElement("small"), { textContent: sl })); g.append(d); miniatura(m) });
    return }
  const i0 = Math.max(0, ESTILOS.findIndex(e => "#" + e.slug === location.hash || e.slug === q.get("estilo")));
  armarFiltros(); armarGrilla(); elegir(i0, !q.has("t"));
  if (q.has("t")) t = +q.get("t");
  requestAnimationFrame(ts => { ultimo = ts; loop(ts) });
})();
