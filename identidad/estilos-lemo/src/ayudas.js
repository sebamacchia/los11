// ---------- ayudas para los 87 estilos nuevos ----------
const TAU = Math.PI * 2;
function silueta(color, w = 275, h = 414) { // Diego recortado (corriendo, Napoli), pintado de un color
  return proc("sil-" + color + w, () => { const c = lienzo(w, h), x = c.getContext("2d"); x.drawImage(IMG.rec, 0, 0, w, h); x.globalCompositeOperation = "source-in"; x.fillStyle = color; x.fillRect(0, 0, w, h); return c });
}
function recorteDuo(c1, c2, w = 275, h = 414) {
  return proc("rduo-" + c1 + c2 + w, () => { const d = duotono(IMG.rec, c1, c2, w, h, 0, 0, IMG.rec.width, IMG.rec.height); const x = d.getContext("2d"); x.globalCompositeOperation = "destination-in"; x.drawImage(IMG.rec, 0, 0, w, h); return d });
}
function bordes(img, color, w, h, sx = 0, sy = 0, sw = img.width, sh = img.height, umbralB = .18) { // líneas por Sobel
  const p = pix(img, w, h, sx, sy, sw, sh), d = p.d.data, L = new Float32Array(w * h), c = hex(color);
  for (let i = 0; i < w * h; i++) L[i] = lum(d, i * 4);
  const out = p.x.createImageData(w, h), o = out.data;
  for (let y = 1; y < h - 1; y++) for (let x = 1; x < w - 1; x++) {
    const i = y * w + x;
    const gx = -L[i - w - 1] - 2 * L[i - 1] - L[i + w - 1] + L[i - w + 1] + 2 * L[i + 1] + L[i + w + 1];
    const gy = -L[i - w - 1] - 2 * L[i - w] - L[i - w + 1] + L[i + w - 1] + 2 * L[i + w] + L[i + w + 1];
    const m = Math.hypot(gx, gy); const a = cl((m - umbralB) * 3);
    o[i * 4] = c[0]; o[i * 4 + 1] = c[1]; o[i * 4 + 2] = c[2]; o[i * 4 + 3] = a * 255;
  }
  p.x.putImageData(out, 0, 0); return p.c;
}
function chico(img, w, h, sx = 0, sy = 0, sw = img.width, sh = img.height) { const c = lienzo(w, h); c.getContext("2d").drawImage(img, sx, sy, sw, sh, 0, 0, w, h); return c }
function pixelado(c, img, x, y, w, h) { c.save(); c.imageSmoothingEnabled = false; c.drawImage(img, x, y, w, h); c.restore() }
function lumGrid(img, cols, rows, sx = 0, sy = 0, sw = img.width, sh = img.height) { const p = pix(img, cols, rows, sx, sy, sw, sh), d = p.d.data, g = new Float32Array(cols * rows); for (let i = 0; i < g.length; i++) g[i] = lum(d, i * 4); return g }
function borroso(img, f = 6) { const w = Math.max(2, Math.round(img.width / f)), h = Math.max(2, Math.round(img.height / f)); const a = chico(img, w, h); const b = lienzo(img.width, img.height); const x = b.getContext("2d"); x.imageSmoothingQuality = "high"; x.drawImage(a, 0, 0, img.width, img.height); return b }
function cancha(c, x, y, w, h, col = "#fff", lw = 2) {
  c.save(); c.strokeStyle = col; c.lineWidth = lw; c.strokeRect(x, y, w, h); c.beginPath(); c.moveTo(x + w / 2, y); c.lineTo(x + w / 2, y + h); c.stroke();
  c.beginPath(); c.arc(x + w / 2, y + h / 2, h * .13, 0, TAU); c.stroke();
  const aw = w * .16, ah = h * .58; c.strokeRect(x, y + (h - ah) / 2, aw, ah); c.strokeRect(x + w - aw, y + (h - ah) / 2, aw, ah);
  const cw = w * .055, ch = h * .26; c.strokeRect(x, y + (h - ch) / 2, cw, ch); c.strokeRect(x + w - cw, y + (h - ch) / 2, cw, ch); c.restore();
}
function pelota(c, x, y, r, rot = 0, fondo = "#fff", linea = "#111", lw = 2) {
  c.save(); c.translate(x, y); c.rotate(rot); c.fillStyle = fondo; c.strokeStyle = linea; c.lineWidth = lw; c.beginPath(); c.arc(0, 0, r, 0, TAU); c.fill(); c.stroke();
  c.fillStyle = linea; const pent = (px, py, s) => { c.beginPath(); for (let i = 0; i < 5; i++) { const a = -Math.PI / 2 + i * TAU / 5; c.lineTo(px + Math.cos(a) * s, py + Math.sin(a) * s) } c.closePath(); c.fill() };
  pent(0, 0, r * .32); for (let i = 0; i < 5; i++) { const a = -Math.PI / 2 + i * TAU / 5; c.save(); c.beginPath(); c.arc(0, 0, r, 0, TAU); c.clip(); pent(Math.cos(a) * r * .9, Math.sin(a) * r * .9, r * .28); c.restore();
    c.beginPath(); c.moveTo(Math.cos(a) * r * .32, Math.sin(a) * r * .32); c.lineTo(Math.cos(a) * r * .66, Math.sin(a) * r * .66); c.stroke() }
  c.restore();
}
function proyector(cx, cy, z = 1, sx0 = 27) { const sx = sx0 * z, sy = sx * 1.32; return ([lo, la]) => [W / 2 + (lo - cx) * sx, H / 2 + (cy - la) * sy] }
function dibujarCosta(c, P, fill, stroke, lw = 1.4) { c.fillStyle = fill; c.strokeStyle = stroke; c.lineWidth = lw; Object.values(COSTA).forEach(poly => { c.beginPath(); poly.forEach((p, i) => i ? c.lineTo(...P(p)) : c.moveTo(...P(p))); c.closePath(); if (fill) c.fill(); if (stroke) c.stroke() }) }
const BCN = [2.17, 41.39], NAP = [14.27, 40.85];
function romano(n) { n = parseInt(n, 10) || 0; const v = [[1000, "M"], [900, "CM"], [500, "D"], [400, "CD"], [100, "C"], [90, "XC"], [50, "L"], [40, "XL"], [10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"]]; let s = ""; for (const [a, r] of v) while (n >= a) { s += r; n -= a } return s }
function puntosSilueta(n, seed = 1) { // puntos dentro del recorte, en coordenadas 0..1
  return proc("pts" + n + seed, () => { const w = 110, h = 166, p = pix(IMG.rec, w, h), d = p.d.data, out = []; let k = 0;
    while (out.length < n && k < n * 60) { const x = rnd(k * 1.7 + seed), y = rnd(k * 3.1 + seed * 7); k++; const a = d[(Math.floor(y * h) * w + Math.floor(x * w)) * 4 + 3]; if (a > 128) out.push([x, y]) } return out });
}
function iso(x, y, z, ox = W / 2, oy = H / 2, s = 1) { return [ox + (x - y) * .866 * s, oy + (x + y) * .5 * s - z * s] }
function poligono(c, pts, fill, stroke, lw = 1) { c.beginPath(); pts.forEach((p, i) => i ? c.lineTo(...p) : c.moveTo(...p)); c.closePath(); if (fill) { c.fillStyle = fill; c.fill() } if (stroke) { c.strokeStyle = stroke; c.lineWidth = lw; c.stroke() } }
function caja(c, x, y, w, h, fill, stroke, lw = 2, r = 0) { c.beginPath(); r ? c.roundRect(x, y, w, h, r) : c.rect(x, y, w, h); if (fill) { c.fillStyle = fill; c.fill() } if (stroke) { c.strokeStyle = stroke; c.lineWidth = lw; c.stroke() } }
function trazoTexto(c, s, x, y, font, color, lw = 2, al = "left") { c.font = font; c.textAlign = al; c.textBaseline = "alphabetic"; c.strokeStyle = color; c.lineWidth = lw; c.strokeText(s, x, y) }
function brillo(c, color, blur) { c.shadowColor = color; c.shadowBlur = blur; c.shadowOffsetX = 0; c.shadowOffsetY = 0 }
function tiza(c, s, x, y, size, fam, color, f, al = "left") { c.save(); c.font = `${size}px ${fam}`; c.textAlign = al; c.fillStyle = color; for (let i = 0; i < 3; i++) { c.globalAlpha = .45; c.fillText(s, x + (rnd(f + i) - .5) * 2, y + (rnd(f + i + 4) - .5) * 2) } c.restore() }
function vineta(c, a = .6, r0 = .35) { const v = c.createRadialGradient(W / 2, H / 2, H * r0, W / 2, H / 2, H * .95); v.addColorStop(0, "rgba(0,0,0,0)"); v.addColorStop(1, `rgba(0,0,0,${a})`); c.fillStyle = v; c.fillRect(0, 0, W, H) }
function lineasScan(c, a = .15, paso = 3) { c.fillStyle = `rgba(0,0,0,${a})`; for (let y = 0; y < H; y += paso) c.fillRect(0, y, W, 1) }
function ola(c, x0, x1, y, amp, fr, fase, color, lw) { c.strokeStyle = color; c.lineWidth = lw; c.beginPath(); for (let x = x0; x <= x1; x += 6) c.lineTo(x, y + Math.sin(x * fr + fase) * amp); c.stroke() }
function reloj(t, bpm = 120) { const b = t * bpm / 60; return { beat: Math.floor(b), fase: b % 1 } }
const PALETA_HIERRO = ["#000000", "#1b0a5c", "#6a0f8c", "#b0236b", "#e2462a", "#f8862a", "#fbd03c", "#fffbe0"];
function mapaColor(img, paleta, w, h, sx, sy, sw, sh) { const p = pix(img, w, h, sx, sy, sw, sh), d = p.d.data, P = paleta.map(hex);
  for (let i = 0; i < d.length; i += 4) { const v = lum(d, i) * (P.length - 1), k = Math.min(P.length - 2, Math.floor(v)), f = v - k; for (let j = 0; j < 3; j++) d[i + j] = P[k][j] + (P[k + 1][j] - P[k][j]) * f } p.x.putImageData(p.d, 0, 0); return p.c }
function invertido(img, w, h, tinte = [255, 140, 60]) { const p = pix(img, w, h), d = p.d.data; for (let i = 0; i < d.length; i += 4) { const v = 1 - lum(d, i); d[i] = v * tinte[0]; d[i + 1] = v * tinte[1]; d[i + 2] = v * tinte[2] } p.x.putImageData(p.d, 0, 0); return p.c }
function estrellas(c, n, t, col = "255,255,255", alto = H) { for (let i = 0; i < n; i++) { const a = .3 + .7 * Math.abs(Math.sin(t * 1.5 + i)); c.fillStyle = `rgba(${col},${a * .8})`; c.fillRect(rnd(i + 3) * W, rnd(i + 70) * alto, 1.5, 1.5) } }
function escala(c, x, y, k, fn) { c.save(); c.translate(x, y); c.scale(k, k); fn(); c.restore() }
