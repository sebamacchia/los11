
const W = 960, H = 540, K = 1.5;
const cl = v => Math.max(0, Math.min(1, v));
const seg = (t, a, b) => cl((t - a) / (b - a));
const eo = x => 1 - Math.pow(1 - x, 3);
const eio = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const eb = x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2) };
const lerp = (a, b, k) => a + (b - a) * k;
const rnd = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x) };

// ---------- assets ----------
const IMG = {};
function cargar(n, src) { return new Promise(r => { const i = new Image(); i.onload = () => { IMG[n] = i; r() }; i.onerror = () => r(); i.src = src }) }
function lienzo(w, h) { const c = document.createElement("canvas"); c.width = w; c.height = h; return c }
const cache = {};
function proc(key, fn) { return cache[key] || (cache[key] = fn()) }
function pix(img, w, h, sx = 0, sy = 0, sw = img.width, sh = img.height) {
  const c = lienzo(w, h), x = c.getContext("2d"); x.drawImage(img, sx, sy, sw, sh, 0, 0, w, h);
  return { c, x, d: x.getImageData(0, 0, w, h) };
}
const lum = (d, i) => (d[i] * .299 + d[i + 1] * .587 + d[i + 2] * .114) / 255;
function hex(h) { const n = parseInt(h.slice(1), 16); return [n >> 16 & 255, n >> 8 & 255, n & 255] }
function gris(img, contraste = 1.4, w = 960, h = Math.round(img.height * 960 / img.width)) {
  const p = pix(img, w, h), d = p.d.data;
  for (let i = 0; i < d.length; i += 4) { let v = (lum(d, i) - .5) * contraste + .5; v = cl(v) * 255; d[i] = d[i + 1] = d[i + 2] = v }
  p.x.putImageData(p.d, 0, 0); return p.c;
}
function duotono(img, c1, c2, w, h, sx, sy, sw, sh, gamma = 1) {
  const p = pix(img, w, h, sx, sy, sw, sh), d = p.d.data, a = hex(c1), b = hex(c2);
  for (let i = 0; i < d.length; i += 4) { const v = Math.pow(lum(d, i), gamma); for (let k = 0; k < 3; k++) d[i + k] = a[k] + (b[k] - a[k]) * v }
  p.x.putImageData(p.d, 0, 0); return p.c;
}
function umbral(img, color, nivel, w, h, sx, sy, sw, sh) { // tinta donde es oscuro, transparente donde es claro
  const p = pix(img, w, h, sx, sy, sw, sh), d = p.d.data, c = hex(color);
  for (let i = 0; i < d.length; i += 4) { const v = lum(d, i); const a = v < nivel ? 255 : 0; d[i] = c[0]; d[i + 1] = c[1]; d[i + 2] = c[2]; d[i + 3] = a }
  p.x.putImageData(p.d, 0, 0); return p.c;
}
function tramado(img, color, w, h, sx, sy, sw, sh, celda = 7) { // medio tono de puntos
  const p = pix(img, Math.ceil(w / celda), Math.ceil(h / celda), sx, sy, sw, sh), d = p.d.data;
  const c = lienzo(w, h), x = c.getContext("2d"); x.fillStyle = color;
  for (let j = 0; j < p.c.height; j++) for (let i = 0; i < p.c.width; i++) {
    const v = 1 - lum(d, (j * p.c.width + i) * 4); const r = Math.sqrt(v) * celda * .62;
    if (r > .4) { x.beginPath(); x.arc(i * celda + celda / 2, j * celda + celda / 2, r, 0, 7); x.fill() }
  }
  return c;
}
function difuminado(img, color, w, h, sx, sy, sw, sh) { // dither ordenado (risografía)
  const p = pix(img, w, h, sx, sy, sw, sh), d = p.d.data, c = hex(color);
  const B = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
  for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
    const k = (j * w + i) * 4, v = lum(d, k) * 1.15 - .05, on = v < (B[(j % 4) * 4 + i % 4] + .5) / 16;
    d[k] = c[0]; d[k + 1] = c[1]; d[k + 2] = c[2]; d[k + 3] = on ? 255 : 0;
  }
  p.x.putImageData(p.d, 0, 0); return p.c;
}
function poster(img, paleta, w, h, sx, sy, sw, sh) {
  const p = pix(img, w, h, sx, sy, sw, sh), d = p.d.data, P = paleta.map(hex);
  for (let i = 0; i < d.length; i += 4) { const v = lum(d, i); const k = Math.min(P.length - 1, Math.floor(v * P.length * 1.05)); d[i] = P[k][0]; d[i + 1] = P[k][1]; d[i + 2] = P[k][2] }
  p.x.putImageData(p.d, 0, 0); return p.c;
}
function ruido(n, w = 320, h = 180, fuerza = 255) {
  const c = lienzo(w, h), x = c.getContext("2d"), id = x.createImageData(w, h), d = id.data;
  for (let i = 0; i < d.length; i += 4) { const v = rnd(i * 0.37 + n * 991.3) * 255; d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = rnd(i * 0.71 + n * 13.1) * fuerza }
  x.putImageData(id, 0, 0); return c;
}
function papel(base, w = 480, h = 270, fibra = 18) {
  const c = lienzo(w, h), x = c.getContext("2d"); x.fillStyle = base; x.fillRect(0, 0, w, h);
  const id = x.getImageData(0, 0, w, h), d = id.data;
  for (let i = 0; i < d.length; i += 4) { const n = (rnd(i * .13) - .5) * fibra; d[i] += n; d[i + 1] += n; d[i + 2] += n }
  x.putImageData(id, 0, 0); return c;
}
const grano = [0, 1, 2, 3].map(n => null);
function granoDe(f) { const k = f % 4; return grano[k] || (grano[k] = ruido(k + 1, 320, 180, 70)) }

// ---------- helpers de dibujo ----------
function cubrir(c, img, x, y, w, h, fx = .5, fy = .5, z = 1) {
  if (!img) return;
  const iw = img.width, ih = img.height, s = Math.max(w / iw, h / ih) * z, dw = iw * s, dh = ih * s;
  let dx = x + w / 2 - fx * dw, dy = y + h / 2 - fy * dh;
  dx = Math.min(x, Math.max(x + w - dw, dx)); dy = Math.min(y, Math.max(y + h - dh, dy));
  c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip(); c.drawImage(img, dx, dy, dw, dh); c.restore();
}
function tam(c, s, fam, max, ancho, peso = "") { c.font = `${peso} ${max}px ${fam}`; const w = c.measureText(s).width; return w > ancho ? max * ancho / w : max }
function texto(c, s, x, y, font, color, al = "left", base = "alphabetic") { c.font = font; c.fillStyle = color; c.textAlign = al; c.textBaseline = base; c.fillText(s, x, y) }
function tipeo(s, k) { return s.slice(0, Math.floor(s.length * cl(k))) }
function lineas(c, s, fam, size, ancho) {
  c.font = `${size}px ${fam}`; const out = []; let l = "";
  for (const w of s.split(/\s+/)) { const p = l ? l + " " + w : w; if (c.measureText(p).width > ancho && l) { out.push(l); l = w } else l = p }
  if (l) out.push(l); return out;
}
function trazo(c, pts, k) { // polilínea dibujada hasta la fracción k
  let L = 0; const seg = []; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); seg.push(d); L += d }
  let r = L * cl(k); c.beginPath(); c.moveTo(...pts[0]); let fin = pts[0];
  for (let i = 1; i < pts.length && r > 0; i++) { const f = Math.min(1, r / seg[i - 1]); fin = [lerp(pts[i - 1][0], pts[i][0], f), lerp(pts[i - 1][1], pts[i][1], f)]; c.lineTo(...fin); r -= seg[i - 1] }
  c.stroke(); return fin;
}
function curva(a, b, alto, n = 40) { const out = []; for (let i = 0; i <= n; i++) { const t = i / n; const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2 - alto; out.push([(1 - t) ** 2 * a[0] + 2 * (1 - t) * t * mx + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * my + t * t * b[1]]) } return out }
function punta(c, a, b, l = 18) { const an = Math.atan2(b[1] - a[1], b[0] - a[0]); c.beginPath(); c.moveTo(b[0] - l * Math.cos(an - .45), b[1] - l * Math.sin(an - .45)); c.lineTo(...b); c.lineTo(b[0] - l * Math.cos(an + .45), b[1] - l * Math.sin(an + .45)); c.stroke() }
function cifraNum(s) { const d = s.replace(/\D/g, ""); return { n: d ? parseInt(d, 10) : 0, pre: (s.match(/^[^\d]*/) || [""])[0].trim() } }
const miles = n => Math.round(n).toLocaleString("es-AR");
function sombra(c, b = 14, y = 6, a = .35) { c.shadowColor = `rgba(0,0,0,${a})`; c.shadowBlur = b; c.shadowOffsetY = y; c.shadowOffsetX = 0 }
function sinSombra(c) { c.shadowColor = "transparent"; c.shadowBlur = 0; c.shadowOffsetY = 0; c.shadowOffsetX = 0 }
function apellido(T) { const p = T.nombre.trim().split(/\s+/); return (p[p.length - 1] || "").toUpperCase() }
function nombre1(T) { return (T.nombre.trim().split(/\s+/)[0] || "").toUpperCase() }

const ESTILOS = [];
