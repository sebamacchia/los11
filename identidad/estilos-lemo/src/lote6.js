// ---------- lote 6: datos y mapas · 3D y miniatura · oficios tradicionales · impresión ----------

const CARRERA = [["FIORITO", "1960"], ["ARGENTINOS", "1976"], ["BOCA", "1981"], ["BARCELONA", "1982"], ["NAPOLI", "1984"]];

// ===== Datos y mapas =====
ESTILOS.push({ slug: "data-physical", nombre: "Datos con objetos", dur: 8, poster: 6.4,
  que: "Los números hechos objetos sobre una mesa: fajos de billetes que caen y se apilan, con sombra real, y una regla que mide la pila.",
  uso: "Para que una cifra se sienta: el valor del pase en fajos, los goles como pelotas apiladas, los kilómetros como hilo.",
  draw(c, t, T) {
    const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, "#3a3530"); g.addColorStop(1, "#1d1a17"); c.fillStyle = g; c.fillRect(0, 0, W, H);
    c.fillStyle = "#5a4632"; poligono(c, [[0, 360], [W, 360], [W, H], [0, H]], "#5a4632"); c.fillStyle = "rgba(0,0,0,.2)"; for (let i = 0; i < 12; i++) c.fillRect(0, 370 + i * 14, W, 2);
    const n = Math.round((cifraNum(T.cifra).n || 7500000) / 500000); const fajo = (x, y, a) => { c.save(); c.globalAlpha = a; poligono(c, [[x, y], [x + 120, y], [x + 150, y - 22], [x + 30, y - 22]], "#8fbf7a", "#2c4a22", 1.2); poligono(c, [[x, y], [x + 120, y], [x + 120, y + 14], [x, y + 14]], "#6d9c5a", "#2c4a22", 1.2); poligono(c, [[x + 120, y], [x + 150, y - 22], [x + 150, y - 8], [x + 120, y + 14]], "#557d45", "#2c4a22", 1.2); c.fillStyle = "#e9e2c8"; c.fillRect(x + 52, y, 16, 14); c.restore() };
    for (let i = 0; i < n; i++) { const col = i % 5, row = Math.floor(i / 5); const t0 = .3 + i * .28; const k = eb(seg(t, t0, t0 + .35)); if (k <= 0) continue; const yf = 430 - row * 14; fajo(140 + col * 0 + (i % 5) * 0 + (row % 2) * 4 + (col) * 0 + col * 140, lerp(yf - 260, yf, k), cl(k * 3)) }
    sombra(c, 0, 0, 0); const top = 430 - (Math.ceil(n / 5) - 1) * 14 - 22; const kr = seg(t, 5, 5.6); if (kr > 0) { c.globalAlpha = kr; c.strokeStyle = "#f4e7b5"; c.lineWidth = 2; c.beginPath(); c.moveTo(880, 444); c.lineTo(880, top); c.stroke(); punta(c, [880, 444], [880, top], 10); texto(c, T.cifra, 870, top - 14, "700 26px 'IBM Plex Sans'", "#f4e7b5", "right"); texto(c, `${n} fajos de US$ 500.000`, 870, top + 14, "14px 'Space Mono'", "#cfc4a0", "right"); c.globalAlpha = 1 }
    texto(c, `EL PASE, EN LA MESA · ${T.anio}`, 40, 60, "34px 'Bebas Neue'", "#f4e7b5");
  } });

ESTILOS.push({ slug: "dataviz", nombre: "Gráfico de unidades", dur: 8, poster: 6.6,
  que: "Datos limpios y precisos: cada cuadradito es una cantidad fija, se llenan en orden, y un número grande con una etiqueta explica qué estamos viendo.",
  uso: "Para proporciones claras: los 70.000 de la presentación, los minutos jugados por cada titular, goles a favor y en contra.",
  draw(c, t, T) {
    c.fillStyle = "#fafaf7"; c.fillRect(0, 0, W, H); const total = 75, lleno = 70, cols = 15;
    for (let i = 0; i < total; i++) { const x = 60 + (i % cols) * 34, y = 170 + Math.floor(i / cols) * 34; const k = eo(seg(t, .4 + i * .045, .7 + i * .045)); caja(c, x, y, 28, 28, "#e6e6e0", null, 0, 4); if (i < lleno && k > 0) { const s = 28 * k; caja(c, x + (28 - s) / 2, y + (28 - s) / 2, s, s, "#1e6fd9", null, 0, 4) } }
    const vis = Math.min(lleno, Math.floor(seg(t, .4, .4 + lleno * .045 + .3) * lleno)); texto(c, miles(vis * 1000), 620, 250, "700 76px 'IBM Plex Sans'", "#1e6fd9"); texto(c, "personas en el San Paolo", 620, 286, "20px 'IBM Plex Sans'", "#333"); texto(c, `para ver a ${nombre1(T).charAt(0) + nombre1(T).slice(1).toLowerCase()} hacer jueguitos (5/7/${T.anio})`, 620, 312, "15px 'IBM Plex Sans'", "#666");
    caja(c, 60, 360, 20, 20, "#1e6fd9", null, 0, 4); texto(c, "= 1.000 personas (aprox.)", 90, 376, "14px 'IBM Plex Sans'", "#555");
    texto(c, "La presentación", 60, 80, "700 30px 'IBM Plex Sans'", "#111"); texto(c, "Público estimado en el estadio, julio de " + T.anio, 60, 110, "16px 'IBM Plex Sans'", "#666");
    c.fillStyle = "#ddd"; c.fillRect(60, 470, 840, 1); texto(c, "Fuente: crónicas de la época (≈70.000)", 60, 494, "12px 'IBM Plex Sans'", "#999");
  } });

ESTILOS.push({ slug: "map-explainer", nombre: "Mapa explicativo", dur: 8, poster: 6,
  que: "Un mapa inclinado en perspectiva, como de noticiero de lujo: la cámara vuela de un punto al otro, los lugares se levantan como banderines y la ruta se dibuja.",
  uso: "Para geografía con sentido: las sedes del Mundial, la ruta de Diego de club en club, dónde queda cada estadio.",
  draw(c, t, T) {
    c.fillStyle = "#0e2236"; c.fillRect(0, 0, W, H); const k = eio(seg(t, .3, 5)); const cx = lerp(BCN[0], NAP[0], k), cy = lerp(BCN[1], NAP[1], k);
    c.save(); c.translate(W / 2, H * .58); c.transform(1, 0, 0, .55, 0, 0); c.translate(-W / 2, -H / 2); const P = proyector(cx, cy, 2.6); c.strokeStyle = "rgba(255,255,255,.05)"; for (let x = -400; x < W + 400; x += 40) { c.beginPath(); c.moveTo(x, -400); c.lineTo(x, H + 400); c.stroke() } dibujarCosta(c, P, "#25465e", "#6ea3c7", 1.5);
    const p = curva(P(BCN), P(NAP), 120); c.strokeStyle = "#ffcc4d"; c.lineWidth = 4; trazo(c, p, eio(seg(t, .5, 5))); const pb = P(BCN), pn = P(NAP); c.restore();
    const proy = q => [W / 2 + (q[0] - W / 2), H * .58 + (q[1] - H / 2) * .55];
    [[pb, "BARCELONA", "1982–84", 0], [pn, "NÁPOLES", T.anio, 4.6]].forEach(([q, s, a, t0]) => { const kk = eb(seg(t, t0, t0 + .5)); if (kk <= 0) return; const [x, y] = proy(q); c.strokeStyle = "#fff"; c.lineWidth = 2; c.beginPath(); c.moveTo(x, y); c.lineTo(x, y - 70 * kk); c.stroke(); caja(c, x - 2, y - 70 * kk - 46, 150, 46, "#fff", null, 0, 4); texto(c, s, x + 10, y - 70 * kk - 26, "700 16px 'IBM Plex Sans'", "#0e2236"); texto(c, a, x + 10, y - 70 * kk - 8, "13px 'Space Mono'", "#557"); c.fillStyle = "#ffcc4d"; c.beginPath(); c.arc(x, y, 6, 0, TAU); c.fill() });
    texto(c, "≈1.000 km EN LÍNEA RECTA", 40, 60, "34px 'Bebas Neue'", "#e8f1f8"); texto(c, `${T.nombre} · ${T.cifra}`, 40, 86, "14px 'Space Mono'", "#8fb3cf");
  } });

ESTILOS.push({ slug: "pip-simulation", nombre: "Simulación de puntitos", dur: 8, poster: 5.6,
  que: "Miles de puntitos que se mueven solos como una simulación: salen de los barrios, fluyen por las calles y llenan el estadio. Cada punto es una persona.",
  uso: "Para multitudes y flujos: los hinchas llegando al Azteca, la caravana del regreso, la gente en la Plaza de Mayo.",
  draw(c, t, T) {
    c.fillStyle = "#0f1115"; c.fillRect(0, 0, W, H); const ex = 640, ey = 270;
    c.strokeStyle = "rgba(255,255,255,.08)"; c.lineWidth = 18; c.lineCap = "round"; [[[60, 80], [400, 200], [ex, ey]], [[60, 470], [380, 360], [ex, ey]], [[300, 30], [ex, ey]]].forEach(r => { c.beginPath(); r.forEach((p, i) => i ? c.lineTo(...p) : c.moveTo(...p)); c.stroke() });
    c.strokeStyle = "#e5e5e5"; c.lineWidth = 3; c.beginPath(); c.ellipse(ex, ey, 160, 110, 0, 0, TAU); c.stroke(); cancha(c, ex - 70, ey - 45, 140, 90, "rgba(255,255,255,.35)", 1);
    const N = 1400; let dentro = 0; for (let i = 0; i < N; i++) { const ruta = i % 3, t0 = rnd(i) * 4.5, k = eio(seg(t, t0, t0 + 2.2)); const ori = [[60, 80], [60, 470], [300, 30]][ruta]; const mid = [[400, 200], [380, 360], [470, 150]][ruta];
      const a = rnd(i + 3) * TAU, r = Math.sqrt(rnd(i + 5)); const dst = [ex + Math.cos(a) * (110 + r * 45), ey + Math.sin(a) * (75 + r * 32)]; const o = [ori[0] + (rnd(i + 7) - .5) * 60, ori[1] + (rnd(i + 9) - .5) * 60];
      let x, y; if (k < .5) { x = lerp(o[0], mid[0], k * 2); y = lerp(o[1], mid[1], k * 2) } else { x = lerp(mid[0], dst[0], (k - .5) * 2); y = lerp(mid[1], dst[1], (k - .5) * 2) } if (k >= 1) dentro++;
      c.fillStyle = k >= 1 ? "#4fd1ff" : "#ffb347"; c.fillRect(x - 1.5 + (rnd(i + 11) - .5) * 8 * (k < 1), y - 1.5 + (rnd(i + 13) - .5) * 8 * (k < 1), 3, 3) }
    texto(c, "≈" + miles(Math.round(dentro / N * 70000 / 100) * 100), 40, 470, "700 54px 'IBM Plex Sans'", "#4fd1ff"); texto(c, `adentro del San Paolo · 5/7/${T.anio}`, 40, 500, "15px 'IBM Plex Sans'", "#9aa3ad");
    caja(c, 40, 40, 14, 14, "#ffb347"); texto(c, "en camino", 62, 53, "14px 'IBM Plex Sans'", "#ccc"); caja(c, 160, 40, 14, 14, "#4fd1ff"); texto(c, "en el estadio", 182, 53, "14px 'IBM Plex Sans'", "#ccc"); texto(c, "1 punto = 50 personas", 40, 80, "12px 'Space Mono'", "#777");
  } });

ESTILOS.push({ slug: "transit-map", nombre: "Mapa de subte", dur: 8, poster: 6.4,
  que: "Una carrera dibujada como línea de subte: tramos a 45°, estaciones redondas con nombre, combinaciones y un trencito que va recorriendo.",
  uso: "Para trayectorias: los clubes de un jugador, el camino al título partido por partido, la línea de técnicos de la selección.",
  draw(c, t, T) {
    c.fillStyle = "#fbfbf8"; c.fillRect(0, 0, W, H); const pts = [[90, 400], [250, 400], [350, 300], [560, 300], [660, 200], [870, 200]]; const est = [[90, 400], [250, 400], [455, 300], [660, 200], [870, 200]];
    c.lineCap = "round"; c.lineJoin = "round"; c.strokeStyle = "#ddd"; c.lineWidth = 16; c.beginPath(); pts.forEach((p, i) => i ? c.lineTo(...p) : c.moveTo(...p)); c.stroke();
    c.strokeStyle = "#e0312a"; c.lineWidth = 16; const fin = trazo(c, pts, eio(seg(t, .3, 5.6)));
    c.strokeStyle = "#1e6fd9"; c.lineWidth = 16; c.beginPath(); c.moveTo(455, 300); c.lineTo(455, 470); c.stroke(); texto(c, "SELECCIÓN →", 470, 478, "600 14px 'IBM Plex Sans'", "#1e6fd9");
    est.forEach(([x, y], i) => { c.fillStyle = "#fff"; c.strokeStyle = "#111"; c.lineWidth = 4; c.beginPath(); c.arc(x, y, 14, 0, TAU); c.fill(); c.stroke(); const up = i % 2; texto(c, CARRERA[i][0], x, up ? y - 30 : y + 42, "700 16px 'IBM Plex Sans'", "#111", "center"); texto(c, CARRERA[i][1], x, up ? y - 50 : y + 62, "13px 'Space Mono'", "#777", "center") });
    caja(c, fin[0] - 22, fin[1] - 12, 44, 24, "#111", null, 0, 8); c.fillStyle = "#ffd84a"; c.fillRect(fin[0] + 12, fin[1] - 5, 6, 10);
    caja(c, 40, 40, 300, 60, "#e0312a", null, 0, 8); texto(c, "LÍNEA D · " + apellido(T), 56, 80, "700 24px 'IBM Plex Sans'", "#fff"); if (t > 5.8) texto(c, `Terminal Napoli · ${T.cifra}`, 800, 290, "14px 'Space Mono'", "#e0312a", "center");
  } });

ESTILOS.push({ slug: "white-model", nombre: "Maqueta blanca", dur: 8, poster: 5,
  que: "Una maqueta de arquitectura toda blanca, con luz suave y sombras largas, que la cámara rodea mientras un color marca el lugar importante.",
  uso: "Para estadios y lugares: el Azteca en maqueta con la tribuna donde estaba la hinchada, el área chica del gol con la mano.",
  draw(c, t, T) {
    c.fillStyle = "#dcdcd8"; c.fillRect(0, 0, W, H); const rot = t * .12; const ox = 480, oy = 300;
    const P = (x, y, z) => { const X = x * Math.cos(rot) - y * Math.sin(rot), Y = x * Math.sin(rot) + y * Math.cos(rot); return [ox + X, oy + Y * .5 - z] };
    const anillo = (r1, r2, h, col, n = 48) => { for (let i = 0; i < n; i++) { const a = i / n * TAU, b = (i + 1) / n * TAU; const q = [P(Math.cos(a) * r1 * 1.4, Math.sin(a) * r1, 0), P(Math.cos(b) * r1 * 1.4, Math.sin(b) * r1, 0), P(Math.cos(b) * r2 * 1.4, Math.sin(b) * r2, h), P(Math.cos(a) * r2 * 1.4, Math.sin(a) * r2, h)]; const luz = .82 + .16 * Math.cos(a + rot - .8); const v = Math.round(255 * luz); poligono(c, q, col || `rgb(${v},${v},${v - 4})`, "rgba(0,0,0,.08)", 1) } };
    c.fillStyle = "rgba(0,0,0,.12)"; c.beginPath(); c.ellipse(ox + 30, oy + 20, 300, 140, 0, 0, TAU); c.fill();
    const base = [P(-150, -95, 0), P(150, -95, 0), P(150, 95, 0), P(-150, 95, 0)]; poligono(c, base, "#f2f2ee");
    const k = seg(t, 2.4, 3); poligono(c, [P(-150, -95, 0), P(150, -95, 0), P(150, 95, 0), P(-150, 95, 0)], `rgba(60,170,90,${.55 * k})`);
    anillo(200, 250, 70); const kb = seg(t, 3.4, 4); if (kb > 0) { c.globalAlpha = kb; for (let i = 0; i < 8; i++) { const a = -.5 + i * .06, b = a + .06; poligono(c, [P(Math.cos(a) * 200 * 1.4, Math.sin(a) * 200, 0), P(Math.cos(b) * 200 * 1.4, Math.sin(b) * 200, 0), P(Math.cos(b) * 250 * 1.4, Math.sin(b) * 250, 70), P(Math.cos(a) * 250 * 1.4, Math.sin(a) * 250, 70)], "#3d8fe0") } c.globalAlpha = 1 }
    if (t > 4.2) { const q = P(Math.cos(-.26) * 260 * 1.4, Math.sin(-.26) * 260, 90); c.strokeStyle = "#222"; c.lineWidth = 1; c.beginPath(); c.moveTo(...q); c.lineTo(q[0] + 40, q[1] - 60); c.lineTo(q[0] + 140, q[1] - 60); c.stroke(); texto(c, "Curva B · hinchada", q[0] + 44, q[1] - 68, "14px 'IBM Plex Sans'", "#222") }
    texto(c, "STADIO SAN PAOLO · MAQUETA 1:1000", 40, 50, "14px 'Space Mono'", "#555"); texto(c, `${apellido(T)} · ${T.anio}`, 40, 72, "14px 'Space Mono'", "#888");
  } });

// ===== 3D y miniatura =====
ESTILOS.push({ slug: "brick-toy", nombre: "Ladrillitos de juguete", dur: 8, poster: 6,
  que: "Todo armado con ladrillitos de plástico encastrables: piezas con botones que caen y se encajan una sobre otra hasta formar la figura.",
  uso: "Para reconstrucciones simpáticas: el equipo armado pieza por pieza, la copa en bloques, el estadio que se construye.",
  draw(c, t, T) {
    c.fillStyle = "#cfe8ff"; c.fillRect(0, 0, W, H); c.fillStyle = "#3aa655"; c.fillRect(0, 430, W, 110); for (let x = 10; x < W; x += 40) for (let y = 445; y < H; y += 40) { c.fillStyle = "#43b660"; c.beginPath(); c.ellipse(x + 10, y, 12, 6, 0, 0, TAU); c.fill() }
    const lad = (x, y, w, col, os) => { const h = 34; caja(c, x, y, w, h, col, "rgba(0,0,0,.25)", 1.5, 3); c.fillStyle = "rgba(255,255,255,.18)"; c.fillRect(x + 2, y + 2, w - 4, 6); for (let i = 0; i < w / 40; i++) { const sx = x + 20 + i * 40; c.fillStyle = os; c.beginPath(); c.ellipse(sx, y - 2, 12, 6, 0, 0, TAU); c.fill(); c.fillStyle = col; c.fillRect(sx - 12, y - 8, 24, 6); c.beginPath(); c.ellipse(sx, y - 8, 12, 6, 0, 0, TAU); c.fill() } };
    const piezas = [[400, 396, 80, "#1b5fc1", "#164e9e"], [480, 396, 80, "#1b5fc1", "#164e9e"], [400, 362, 160, "#ffffff", "#d8d8d8"], [400, 328, 160, "#4ba3ff", "#3a86d6"], [400, 294, 160, "#4ba3ff", "#3a86d6"], [360, 294, 40, "#f4c27a", "#d6a560"], [560, 294, 40, "#f4c27a", "#d6a560"], [440, 260, 80, "#f4c27a", "#d6a560"], [440, 226, 80, "#f4c27a", "#d6a560"], [430, 192, 100, "#2b1a0e", "#1c1108"]];
    piezas.forEach(([x, y, w, col, os], i) => { const t0 = .2 + i * .42; const k = eb(seg(t, t0, t0 + .35)); if (k <= 0) return; lad(x, lerp(y - 300, y, k), w, col, os) });
    if (t > 4.6) { c.fillStyle = "#111"; c.fillRect(458, 236, 8, 8); c.fillRect(494, 236, 8, 8); texto(c, "10", 480, 322, "700 28px 'IBM Plex Sans'", "#fff", "center") }
    if (t > 5) { caja(c, 620, 120, 300, 80, "#ffd400", "#111", 3, 8); texto(c, `SET ${T.anio}`, 640, 154, "700 24px 'IBM Plex Sans'", "#e3000b"); texto(c, `${apellido(T)} · NAPOLI`, 640, 184, "600 16px 'IBM Plex Sans'", "#111") }
  } });

ESTILOS.push({ slug: "crayon-world", nombre: "Mundo de crayón en 3D", dur: 8, poster: 5.6,
  que: "Un mundito en miniatura que parece hecho de crayón y plastilina: colinas redondas, casitas, árboles que se mueven y todo con textura cerosa.",
  uso: "Para los orígenes con ternura: Villa Fiorito como pueblito de cuento, el potrero, la casa de la familia.",
  draw(c, t, T) {
    c.fillStyle = "#ffe7c2"; c.fillRect(0, 0, W, H);
    const cerosa = (fn, col, sem) => { c.save(); c.beginPath(); fn(); c.fillStyle = col; c.fill(); c.clip(); c.strokeStyle = "rgba(255,255,255,.22)"; c.lineWidth = 3; for (let i = 0; i < 90; i++) { const x = rnd(i + sem) * W, y = rnd(i * 2 + sem) * H; c.beginPath(); c.moveTo(x, y); c.lineTo(x + 30, y - 10); c.stroke() } c.restore() };
    cerosa(() => c.arc(780, 110, 50, 0, TAU), "#ffb703", 1);
    cerosa(() => { c.moveTo(0, 360); c.quadraticCurveTo(240, 200, 480, 340); c.quadraticCurveTo(720, 220, 960, 330); c.lineTo(960, 540); c.lineTo(0, 540) }, "#8ecf6e", 2);
    cerosa(() => { c.moveTo(0, 450); c.quadraticCurveTo(480, 360, 960, 450); c.lineTo(960, 540); c.lineTo(0, 540) }, "#6cb24e", 3);
    [[170, 330], [300, 300], [640, 300]].forEach(([x, y], i) => { cerosa(() => c.rect(x - 40, y - 50, 80, 60), ["#ff8fa3", "#8ecae6", "#ffd166"][i], 10 + i); cerosa(() => { c.moveTo(x - 50, y - 48); c.lineTo(x, y - 90); c.lineTo(x + 50, y - 48) }, "#e76f51", 20 + i); c.fillStyle = "#5a3b2e"; c.fillRect(x - 10, y - 26, 20, 36) });
    [[90, 380], [440, 330], [860, 360]].forEach(([x, y], i) => { c.fillStyle = "#7a4e2d"; c.fillRect(x - 5, y - 10, 10, 40); const s = Math.sin(t * 2 + i) * 4; cerosa(() => c.arc(x + s, y - 30, 30, 0, TAU), "#2a9d8f", 30 + i) });
    const bx = 470 + Math.sin(t * 2) * 90, by = 430 - Math.abs(Math.sin(t * 4)) * 50; c.fillStyle = "rgba(0,0,0,.15)"; c.beginPath(); c.ellipse(bx, 445, 20, 6, 0, 0, TAU); c.fill(); pelota(c, bx, by, 16, t * 4, "#fff", "#333", 2.5);
    texto(c, "Villa Fiorito", 40, 70, "52px Caveat", "#5a3b2e"); if (t > 3) texto(c, `donde empezó todo (antes de ${T.anio})`, 40, 106, "30px Caveat", "#7a5a4e");
  } });

ESTILOS.push({ slug: "glass-product", nombre: "Producto de vidrio", dur: 8, poster: 5,
  que: "Un objeto de vidrio o cristal girando en un estudio oscuro: refracciones, brillos que recorren los bordes y una base que refleja la luz.",
  uso: "Para trofeos y objetos de culto: la Copa del Mundo, el Balón de Oro, la medalla. Lujo de comercial de perfume.",
  draw(c, t, T) {
    const g = c.createRadialGradient(W / 2, 260, 40, W / 2, 300, 560); g.addColorStop(0, "#1d2a3c"); g.addColorStop(1, "#05070b"); c.fillStyle = g; c.fillRect(0, 0, W, H);
    const cx = 480, cy = 250, R = 130, a = t * .9;
    c.fillStyle = "rgba(120,180,255,.08)"; c.beginPath(); c.ellipse(cx, 430, 200, 30, 0, 0, TAU); c.fill(); c.strokeStyle = "rgba(160,210,255,.4)"; c.lineWidth = 1.5; c.stroke();
    c.save(); c.beginPath(); c.arc(cx, cy, R, 0, TAU); c.clip(); const fondo = c.createLinearGradient(cx - R, cy - R, cx + R, cy + R); fondo.addColorStop(0, "rgba(140,200,255,.15)"); fondo.addColorStop(1, "rgba(20,40,80,.4)"); c.fillStyle = fondo; c.fillRect(cx - R, cy - R, 2 * R, 2 * R);
    c.save(); c.translate(cx, cy); c.scale(-1, 1); c.font = "120px Anton"; c.textAlign = "center"; c.fillStyle = "rgba(255,255,255,.18)"; c.fillText("10", Math.sin(a) * 30, 40); c.restore();
    for (let i = 0; i < 6; i++) { const b = a + i * TAU / 6, x = Math.cos(b) * R * .7; c.strokeStyle = `rgba(200,230,255,${.15 + .25 * Math.max(0, Math.cos(b))})`; c.lineWidth = 2; c.beginPath(); c.ellipse(cx + x * .3, cy, Math.abs(Math.cos(b)) * R, R, 0, 0, TAU); c.stroke() }
    const hl = c.createLinearGradient(cx - R, 0, cx + R, 0); const p = (Math.sin(a) + 1) / 2; hl.addColorStop(cl(p - .08), "rgba(255,255,255,0)"); hl.addColorStop(p, "rgba(255,255,255,.55)"); hl.addColorStop(cl(p + .08), "rgba(255,255,255,0)"); c.fillStyle = hl; c.fillRect(cx - R, cy - R, 2 * R, 2 * R); c.restore();
    c.strokeStyle = "rgba(220,240,255,.8)"; c.lineWidth = 2.5; c.beginPath(); c.arc(cx, cy, R, 0, TAU); c.stroke(); c.fillStyle = "#fff"; brillo(c, "#bde0ff", 20); c.beginPath(); c.ellipse(cx - 60, cy - 70, 22, 10, -.7, 0, TAU); c.fill(); sinSombra(c);
    poligono(c, [[cx - 40, cy + R - 4], [cx + 40, cy + R - 4], [cx + 60, 420], [cx - 60, 420]], "rgba(140,200,255,.18)", "rgba(200,230,255,.6)", 1.5);
    const k = seg(t, 3.6, 4.4); c.globalAlpha = k; texto(c, `${nombre1(T).charAt(0) + nombre1(T).slice(1).toLowerCase()}. Edición ${T.anio}.`, cx, 490, "300 30px 'IBM Plex Sans'", "#e8f2ff", "center"); texto(c, "Cristal · pieza única", cx, 520, "14px 'Space Mono'", "#8aa4c2", "center"); c.globalAlpha = 1;
  } });

ESTILOS.push({ slug: "isometric-picture-book", nombre: "Libro ilustrado isométrico", dur: 8, poster: 6,
  que: "Una manzana de ciudad en isométrico, como página de libro ilustrado: edificios de colores suaves, gente chiquita, autitos y detalles para descubrir.",
  uso: "Para recrear un barrio o un día: Nápoles el día de la llegada, el barrio de la concentración, la calle del festejo.",
  draw(c, t, T) {
    c.fillStyle = "#f7efe2"; c.fillRect(0, 0, W, H); const O = [470, 300], s = .9;
    const bloque = (x, y, w, d, h, cols) => { const p = (a, b, z) => iso(a, b, z, O[0], O[1], s); poligono(c, [p(x + w, y, 0), p(x + w, y + d, 0), p(x + w, y + d, h), p(x + w, y, h)], cols[1]); poligono(c, [p(x, y + d, 0), p(x + w, y + d, 0), p(x + w, y + d, h), p(x, y + d, h)], cols[2]); poligono(c, [p(x, y, h), p(x + w, y, h), p(x + w, y + d, h), p(x, y + d, h)], cols[0]);
      for (let z = 20; z < h - 10; z += 28) for (let i = 10; i < w - 10; i += 26) { const q = p(x + i, y + d, z); poligono(c, [q, [q[0] + 12, q[1] + 7], [q[0] + 12, q[1] - 7], [q[0], q[1] - 14]], "rgba(255,255,255,.55)") } };
    poligono(c, [iso(-220, -220, 0, ...O), iso(240, -220, 0, ...O), iso(240, 240, 0, ...O), iso(-220, 240, 0, ...O)], "#d9cbb3");
    poligono(c, [iso(-220, 0, 0, ...O), iso(240, 0, 0, ...O), iso(240, 50, 0, ...O), iso(-220, 50, 0, ...O)], "#9c9488");
    bloque(-200, -200, 90, 90, 110, ["#ffd3b0", "#f2a97e", "#e08e63"]); bloque(-90, -200, 100, 90, 70, ["#bde0d8", "#8cc5b8", "#6fae9f"]); bloque(30, -200, 90, 90, 140, ["#f8e3a3", "#e8c96e", "#d6b451"]); bloque(-200, 70, 120, 100, 60, ["#d8c8f0", "#b7a2e0", "#9b84cf"]); bloque(-60, 70, 90, 100, 100, ["#ffc2c7", "#f59aa2", "#e57c86"]);
    const k = (t * .08) % 1; const car = iso(lerp(-220, 240, k), 25, 0, ...O); caja(c, car[0] - 14, car[1] - 12, 28, 14, "#1e6fd9", null, 0, 3);
    for (let i = 0; i < 14; i++) { const q = iso(-180 + ((rnd(i) * 400 + t * 10 * (i % 2 ? 1 : -1)) % 400 + 400) % 400, 55 + rnd(i + 3) * 10, 0, ...O); c.fillStyle = ["#1e6fd9", "#e04f5f", "#222"][i % 3]; c.fillRect(q[0] - 2, q[1] - 10, 4, 10); c.fillStyle = "#e0a77a"; c.beginPath(); c.arc(q[0], q[1] - 13, 3, 0, TAU); c.fill() }
    const ban = iso(90, -150, 140, ...O); c.strokeStyle = "#333"; c.lineWidth = 2; c.beginPath(); c.moveTo(...ban); c.lineTo(ban[0], ban[1] - 40); c.stroke(); poligono(c, [[ban[0], ban[1] - 40], [ban[0] + 40 + Math.sin(t * 3) * 4, ban[1] - 32], [ban[0], ban[1] - 24]], "#29a3ff");
    caja(c, 620, 420, 310, 90, "#fffaf0", "#d9cbb3", 2, 8); texto(c, "Nápoles, julio de " + T.anio, 640, 454, "30px Caveat", "#5a4632"); texto(c, `todo el barrio esperaba a ${nombre1(T).charAt(0) + nombre1(T).slice(1).toLowerCase()}`, 640, 488, "22px Caveat", "#8a7660");
  } });

ESTILOS.push({ slug: "lowpoly-island", nombre: "Isla de pocos polígonos", dur: 8, poster: 5,
  que: "Un paisaje de pocos polígonos, facetado como un juego indie: la bahía, el volcán y el mar con triángulos que cambian de luz mientras pasa el día.",
  uso: "Para lugares como postal: el golfo de Nápoles con el Vesubio, el DF con los volcanes, la sede de cada partido.",
  draw(c, t, T) {
    const d = (Math.sin(t * .4) + 1) / 2; const cielo = c.createLinearGradient(0, 0, 0, 300); cielo.addColorStop(0, `rgb(${lerp(60, 255, d * .5) | 0},${lerp(120, 160, d) | 0},${lerp(200, 220, d) | 0})`); cielo.addColorStop(1, "#ffd9a8"); c.fillStyle = cielo; c.fillRect(0, 0, W, H);
    const tri = (a, b, cc, col, l) => { const k = .75 + l * .35; const [r, g, bl] = hex(col); poligono(c, [a, b, cc], `rgb(${Math.min(255, r * k) | 0},${Math.min(255, g * k) | 0},${Math.min(255, bl * k) | 0})`) };
    const cima = [560, 120]; const pie = [[300, 330], [380, 300], [460, 280], [640, 280], [720, 300], [820, 330]];
    for (let i = 0; i < pie.length - 1; i++) tri(cima, pie[i], pie[i + 1], "#7d6a5a", Math.cos((i - 2.5) * .5 - d) * .4); tri([540, 128], [580, 128], cima, "#5a4a3e", .1);
    c.fillStyle = "rgba(230,230,230,.8)"; for (let i = 0; i < 4; i++) { poligono(c, [[560 + i * 10, 110 - i * 22 - (t * 8) % 20], [590 + i * 14, 98 - i * 22 - (t * 8) % 20], [575 + i * 12, 84 - i * 22 - (t * 8) % 20]], "rgba(235,235,235,.7)") }
    for (let j = 0; j < 6; j++) for (let i = 0; i < 16; i++) { const x0 = i * 64 - (j % 2) * 32, y0 = 330 + j * 36; const ond = Math.sin(t * 1.5 + i + j) * .3; tri([x0, y0], [x0 + 64, y0], [x0 + 32, y0 + 36], "#2b7bb9", ond); tri([x0 + 32, y0 + 36], [x0 + 96, y0 + 36], [x0 + 64, y0], "#2b7bb9", -ond * .5) }
    for (let i = 0; i < 8; i++) { const x = 40 + i * 34; tri([x, 330], [x + 30, 330], [x + 15, 300 - (i % 3) * 14], "#e8d2b0", .2) }
    c.save(); c.translate(240 + Math.sin(t * .5) * 10, 380); poligono(c, [[-30, 0], [30, 0], [20, 12], [-20, 12]], "#fff"); poligono(c, [[0, -40], [0, 0], [24, -4]], "#ff6b5a"); c.restore();
    texto(c, "GOLFO DE NÁPOLES", 40, 60, "34px 'Bebas Neue'", "#2a2a3a"); texto(c, `Vesubio 1.281 m · ${apellido(T)} llega en ${T.anio}`, 40, 86, "14px 'Space Mono'", "#3a3a4a");
  } });

ESTILOS.push({ slug: "memphis-diorama", nombre: "Diorama Memphis", dur: 8, poster: 5.5,
  que: "Un escenario de juguete en estilo Memphis de los 80: formas geométricas con sombra dura, zigzags, puntos y colores pastel chillones que se mueven al ritmo.",
  uso: "Para el ambiente de los 80: la moda del 86, los programas de TV de la época, una sección «mientras tanto en el mundo».",
  draw(c, t, T) {
    c.fillStyle = "#fde2e4"; c.fillRect(0, 0, W, H); c.fillStyle = "#cdb4db"; c.fillRect(0, 380, W, 160);
    const { fase } = reloj(t, 110); const pop = 1 + (1 - fase) * .06;
    const sh = (fn, col, dx = 10, dy = 10) => { c.save(); c.translate(dx, dy); fn("#222"); c.restore(); fn(col) };
    sh(col => { c.fillStyle = col; c.beginPath(); c.arc(220, 220, 90 * pop, 0, TAU); c.fill() }, "#ffd166");
    sh(col => poligono(c, [[600, 120], [760, 380], [440, 380]], col), "#06d6a0");
    sh(col => { c.fillStyle = col; c.fillRect(760, 160, 120, 220) }, "#118ab2");
    c.strokeStyle = "#222"; c.lineWidth = 8; c.lineJoin = "miter"; c.beginPath(); for (let i = 0; i < 9; i++) c.lineTo(80 + i * 40, 440 + (i % 2) * 30 + Math.sin(t * 3) * 4); c.stroke();
    c.fillStyle = "#222"; for (let i = 0; i < 6; i++) for (let j = 0; j < 4; j++) { c.beginPath(); c.arc(560 + i * 24, 430 + j * 22, 4, 0, TAU); c.fill() }
    c.strokeStyle = "#ef476f"; c.lineWidth = 10; c.beginPath(); for (let x = 300; x <= 520; x += 6) c.lineTo(x, 110 + Math.sin(x * .05 + t * 4) * 16); c.stroke();
    c.save(); c.translate(220, 220); c.rotate(t * .6); pelota(c, 0, 0, 50, 0, "#fff", "#222", 4); c.restore();
    sh(col => { caja(c, 360, 230, 300, 90, col, null, 0, 0); texto(c, T.anio, 510, 300, "80px 'Rubik Mono One'", "#222", "center") }, "#fff", 8, 8);
    texto(c, `${apellido(T)} · NAPOLI`, 40, 60, "26px 'Rubik Mono One'", "#222");
  } });

ESTILOS.push({ slug: "paper-popup", nombre: "Libro desplegable", dur: 8, poster: 5,
  que: "Un libro de papel que se abre y levanta piezas desplegables: capas de cartulina que se paran con sombra, solapas que se doblan y un texto impreso.",
  uso: "Para empezar un capítulo como cuento: «había una vez un estadio», la llegada a México, el álbum familiar.",
  draw(c, t, T) {
    c.fillStyle = "#6b4a3a"; c.fillRect(0, 0, W, H); c.fillStyle = "rgba(0,0,0,.25)"; for (let i = 0; i < 30; i++) c.fillRect(0, i * 18, W, 2);
    const ab = eio(seg(t, .2, 1.8)); const lomo = [480, 440];
    poligono(c, [[lomo[0], 200], [lomo[0] - 420 * ab, 200 + (1 - ab) * 160], [lomo[0] - 420 * ab, 480], lomo], "#f6efdf", "#c9b99a", 2); poligono(c, [[lomo[0], 200], [lomo[0] + 420, 200], [lomo[0] + 420, 480], lomo], "#f3ead7", "#c9b99a", 2);
    const capa = (k0, fn) => { const k = eb(seg(t, k0, k0 + .7)) * ab; if (k <= 0) return; c.save(); c.translate(0, 440); c.scale(1, k); c.translate(0, -440); c.fillStyle = "rgba(0,0,0,.18)"; c.save(); c.translate(10, 8); fn(true); c.restore(); fn(false); c.restore() };
    capa(1.6, sh => poligono(c, [[180, 440], [300, 250], [360, 230], [420, 260], [520, 440]], sh ? "rgba(0,0,0,.2)" : "#8a7766", sh ? null : "#5a4a3a", 2));
    capa(2.1, sh => { if (sh) { c.fillRect(560, 300, 260, 140); return } caja(c, 560, 300, 260, 140, "#d8d2c4", "#5a4a3a", 2); c.fillStyle = "#3a8f5a"; c.fillRect(590, 330, 200, 90); cancha(c, 590, 330, 200, 90, "#fff", 1.5) });
    capa(2.6, sh => { if (sh) { c.beginPath(); c.arc(470, 340, 60, 0, TAU); c.fill(); return } c.fillStyle = "#f2d16b"; c.beginPath(); c.arc(470, 340, 60, 0, TAU); c.fill(); c.strokeStyle = "#5a4a3a"; c.lineWidth = 2; c.stroke() });
    capa(3.1, sh => { if (sh) { c.drawImage(silueta("rgba(0,0,0,.25)"), 620, 180, 110, 166); return } c.drawImage(silueta("#1e5fa8"), 620, 180, 110, 166) });
    if (t > 3.8) { texto(c, "Capítulo 2", 140, 140, "26px 'Special Elite'", "#f3ead7"); texto(c, `Nápoles, ${T.anio}`, 140, 176, "36px 'Special Elite'", "#fff") }
  } });

ESTILOS.push({ slug: "tilt-shift", nombre: "Miniatura con desenfoque", dur: 8, poster: 4,
  que: "Una escena real que parece una maqueta: la franja del medio nítida, arriba y abajo desenfocado, colores saturados y movimiento acelerado.",
  uso: "Para planos de multitud o ciudad: la tribuna como un juguete, la caravana por la avenida, el estadio desde arriba.",
  draw(c, t, T) {
    const sat = proc("ts-sat", () => { const s = lienzo(960, 540), x = s.getContext("2d"); x.filter = "saturate(1.9) contrast(1.15) brightness(1.05)"; x.drawImage(IMG.jueguitos, 0, 0, 960, 540); return s });
    const bl = proc("ts-bl", () => borroso(sat, 10)), bl2 = proc("ts-bl2", () => borroso(sat, 5));
    const z = 1.05 + t * .012; c.save(); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2); c.drawImage(bl, 0, 0, W, H);
    c.save(); c.beginPath(); c.rect(0, 130, W, 300); c.clip(); c.drawImage(bl2, 0, 0, W, H); c.restore(); c.save(); c.beginPath(); c.rect(0, 190, W, 180); c.clip(); c.drawImage(sat, 0, 0, W, H); c.restore(); c.restore();
    vineta(c, .35, .5);
    caja(c, 40, 470, 360, 44, "rgba(255,255,255,.88)", null, 0, 22); texto(c, `San Paolo en miniatura · ${T.anio}`, 60, 498, "600 17px 'IBM Plex Sans'", "#222");
  } });

// ===== Oficios tradicionales =====
ESTILOS.push({ slug: "gilded-illumination", nombre: "Manuscrito iluminado", dur: 8, poster: 6.2,
  que: "Una página de manuscrito medieval: letra capitular dorada que brilla, bordes con enredaderas pintadas, letra gótica y el año en números romanos.",
  uso: "Para lo legendario: «el evangelio según Diego», la leyenda del 10, la crónica de la final como texto sagrado.",
  draw(c, t, T) {
    c.drawImage(proc("gi-pap", () => papel("#efe0bd", 480, 270, 22)), 0, 0, W, H);
    const kb = seg(t, .2, 2); c.strokeStyle = "#6a1e22"; c.lineWidth = 3; c.strokeRect(30, 30, W - 60, H - 60); c.strokeStyle = "#1f4a7a"; c.lineWidth = 2; c.strokeRect(42, 42, W - 84, H - 84);
    const hoja = (x, y, a, col) => { c.save(); c.translate(x, y); c.rotate(a); c.fillStyle = col; c.beginPath(); c.ellipse(0, 0, 10, 5, 0, 0, TAU); c.fill(); c.restore() };
    for (let i = 0; i < 40 * kb; i++) { const y = 60 + i * 11; c.strokeStyle = "#3a6a3a"; c.lineWidth = 2; c.beginPath(); c.moveTo(60 + Math.sin(i * .6) * 8, y); c.lineTo(60 + Math.sin(i * .6 + .6) * 8, y + 11); c.stroke(); if (i % 3 === 0) hoja(66 + Math.sin(i * .6) * 8, y, i, i % 2 ? "#a3262e" : "#3a6a3a") }
    const kc = seg(t, 1, 2.4); if (kc > 0) { caja(c, 110, 80, 150, 170, "#7a1e24", "#c9a13a", 4); c.save(); c.globalAlpha = kc; const g = c.createLinearGradient(110, 80, 260, 250); const p = (t * .3) % 1; g.addColorStop(0, "#8a6a1a"); g.addColorStop(cl(p), "#fff3b0"); g.addColorStop(1, "#b8861c"); c.font = "160px UnifrakturMaguntia"; c.textAlign = "center"; c.fillStyle = g; c.fillText(nombre1(T).charAt(0), 185, 225); c.restore() }
    const lineasT = [nombre1(T).slice(1).toLowerCase() + ", hijo de Fiorito,", "llegó a la ciudad del volcán", "y la ciudad lo recibió como a un rey.", `Anno Domini ${romano(T.anio)}`];
    lineasT.forEach((s, i) => { const k = seg(t, 2.4 + i * .8, 3.2 + i * .8); if (k > 0) texto(c, tipeo(s, k), i === 0 ? 280 : 120, i ? 250 + i * 58 : 130, `${i === 3 ? 40 : 34}px UnifrakturMaguntia`, i === 3 ? "#7a1e24" : "#2a1a10") });
  } });

ESTILOS.push({ slug: "ink-wash", nombre: "Tinta china", dur: 8, poster: 6,
  que: "Pintura de tinta oriental: pinceladas negras que se abren en el papel, montañas en capas de gris, mucho espacio vacío y un sello rojo.",
  uso: "Para momentos contemplativos: la calma antes de la final, el retiro, una reflexión del narrador.",
  draw(c, t, T) {
    c.drawImage(proc("iw-pap", () => papel("#f3eee2", 480, 270, 10)), 0, 0, W, H);
    const monte = (y0, amp, sem, a, t0) => { const k = eo(seg(t, t0, t0 + 1.4)); if (k <= 0) return; c.save(); c.globalAlpha = a * k; const g = c.createLinearGradient(0, y0 - amp, 0, y0 + 120); g.addColorStop(0, "#1a1a1a"); g.addColorStop(1, "rgba(26,26,26,0)"); c.fillStyle = g; c.beginPath(); c.moveTo(0, H); for (let x = 0; x <= W; x += 8) c.lineTo(x, y0 - Math.abs(Math.sin(x * .006 + sem)) * amp - Math.sin(x * .03 + sem) * 10); c.lineTo(W, H); c.fill(); c.restore() };
    monte(300, 140, 1, .25, .2); monte(360, 110, 3, .45, .9); monte(430, 80, 5, .75, 1.6);
    const kb = seg(t, 2.6, 4.2); if (kb > 0) { c.save(); c.strokeStyle = "#111"; c.lineCap = "round"; const pts = []; for (let i = 0; i <= 60; i++) { const u = i / 60; pts.push([620 + Math.sin(u * 3) * 20, 120 + u * 260]) } for (let i = 1; i < pts.length * kb; i++) { c.lineWidth = 2 + Math.sin(i / pts.length * Math.PI) * 18; c.beginPath(); c.moveTo(...pts[i - 1]); c.lineTo(...pts[i]); c.stroke() } c.restore() }
    if (t > 4.2) { const k = eo(seg(t, 4.2, 5)); c.globalAlpha = k; c.fillStyle = "#111"; c.beginPath(); c.arc(700, 160, 26, 0, TAU); c.fill(); c.fillStyle = "#f3eee2"; c.beginPath(); c.arc(708, 152, 22, 0, TAU); c.fill(); c.globalAlpha = 1 }
    if (t > 5) { const k = seg(t, 5, 5.6); c.globalAlpha = k; caja(c, 840, 380, 64, 64, "#b3261e", null, 0, 4); texto(c, "10", 872, 425, "34px Anton", "#f3eee2", "center"); texto(c, "La calma antes del", 120, 120, "30px 'Special Elite'", "#222"); texto(c, `volcán · ${T.anio}`, 120, 156, "30px 'Special Elite'", "#222"); c.globalAlpha = 1 }
  } });

ESTILOS.push({ slug: "paper-lantern", nombre: "Farolitos de papel", dur: 8, poster: 5.5,
  que: "Farolitos de papel que se encienden en la noche: la luz cálida atraviesa el papel, se mecen con el viento y cada uno lleva escrito un nombre.",
  uso: "Para homenajes y recuerdos: los nombres de los 23, los que ya no están, la noche de festejo en Nápoles.",
  draw(c, t, T) {
    const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, "#0b0f2a"); g.addColorStop(1, "#2a1530"); c.fillStyle = g; c.fillRect(0, 0, W, H); estrellas(c, 70, t);
    c.strokeStyle = "rgba(255,255,255,.25)"; c.lineWidth = 1.5; c.beginPath(); c.moveTo(0, 90); c.quadraticCurveTo(W / 2, 170, W, 90); c.stroke();
    const nombres = [apellido(T), "NAPOLI", T.anio, "10", "SAN PAOLO"];
    nombres.forEach((s, i) => { const u = (i + .5) / nombres.length, x = u * W, y0 = 90 + Math.sin(u * Math.PI) * 80; const sw = Math.sin(t * 1.4 + i) * .08; const on = seg(t, .4 + i * .6, 1 + i * .6);
      c.save(); c.translate(x, y0); c.rotate(sw); c.strokeStyle = "rgba(255,255,255,.4)"; c.beginPath(); c.moveTo(0, 0); c.lineTo(0, 40); c.stroke();
      if (on > 0) { const gl = c.createRadialGradient(0, 120, 10, 0, 120, 160); gl.addColorStop(0, `rgba(255,170,80,${.35 * on})`); gl.addColorStop(1, "rgba(255,170,80,0)"); c.fillStyle = gl; c.fillRect(-170, -40, 340, 320) }
      const cuerpo = c.createRadialGradient(0, 120, 10, 0, 120, 80); cuerpo.addColorStop(0, on > 0 ? `rgba(255,${200 + 40 * on | 0},140,1)` : "#5a2a2a"); cuerpo.addColorStop(1, on > 0 ? "#d8432a" : "#3a1a1a"); c.fillStyle = cuerpo; c.beginPath(); c.ellipse(0, 120, 60, 80, 0, 0, TAU); c.fill();
      c.strokeStyle = "rgba(90,20,10,.5)"; c.lineWidth = 1.5; for (let k = -2; k <= 2; k++) { c.beginPath(); c.ellipse(0, 120, Math.abs(k) * 15 + 1, 80, 0, 0, TAU); c.stroke() } caja(c, -30, 36, 60, 10, "#222"); caja(c, -30, 194, 60, 10, "#222");
      texto(c, s, 0, 130, `${tam(c, s, "'Bebas Neue'", 30, 90)}px 'Bebas Neue'`, on > 0 ? "#5a1a0a" : "#2a1010", "center"); c.restore() });
  } });

ESTILOS.push({ slug: "papercut-red", nombre: "Papel calado rojo", dur: 8, poster: 5.4,
  que: "Recorte de papel rojo sobre fondo claro, como el papel calado de fiesta: formas simétricas con agujeros finos, que se despliegan como al abrir el papel doblado.",
  uso: "Para festejos y celebraciones: el título de campeón, el carnaval de Nápoles, una portada de capítulo festiva.",
  draw(c, t, T) {
    c.fillStyle = "#fbf3e6"; c.fillRect(0, 0, W, H); const ab = eio(seg(t, .3, 2.2));
    const mitad = proc("pc-m", () => { const s = lienzo(480, 540), x = s.getContext("2d"); x.fillStyle = "#c8102e"; x.beginPath(); x.moveTo(480, 30); x.quadraticCurveTo(200, 40, 140, 270); x.quadraticCurveTo(200, 500, 480, 510); x.fill(); x.globalCompositeOperation = "destination-out";
      for (let i = 0; i < 10; i++) { const a = -1.3 + i * .29; x.beginPath(); x.ellipse(480 + Math.cos(a + Math.PI) * 280, 270 + Math.sin(a + Math.PI) * 200, 14, 6, a, 0, TAU); x.fill() }
      for (let i = 0; i < 6; i++) { x.beginPath(); x.moveTo(480, 120 + i * 12); x.lineTo(380 - i * 20, 200 + i * 10); x.lineTo(380 - i * 20, 210 + i * 10); x.lineTo(480, 130 + i * 12); x.fill() }
      x.beginPath(); x.arc(480, 300, 92, 0, TAU); x.fill(); for (let i = 0; i < 16; i++) { const a = i / 16 * TAU; x.beginPath(); x.arc(480 + Math.cos(a) * 115, 300 + Math.sin(a) * 115, 8, 0, TAU); x.fill() } return s });
    c.save(); c.translate(480, 0); c.scale(ab, 1); c.drawImage(mitad, -480, 0); c.restore(); c.save(); c.translate(480, 0); c.scale(-1, 1); c.drawImage(mitad, -480, 0); c.restore();
    if (ab > .98) texto(c, "10", 480, 340, "110px Anton", "#c8102e", "center");
    if (t > 2.6) { const k = seg(t, 2.6, 3.2); c.globalAlpha = k; texto(c, `${apellido(T)} · NÁPOLES ${T.anio}`, W / 2, 530, "18px 'Space Mono'", "#8a0c20", "center"); c.globalAlpha = 1 }
  } });

ESTILOS.push({ slug: "shadow-puppet", nombre: "Teatro de sombras", dur: 8, poster: 5.4,
  que: "Teatro de sombras detrás de una tela iluminada: siluetas negras recortadas que se mueven en sus varillas, con la luz que tiembla como una vela.",
  uso: "Para recrear escenas sin imágenes: la reunión secreta, el duelo Menotti-Bilardo, una leyenda contada como fábula.",
  draw(c, t, T) {
    const fl = .92 + Math.sin(t * 13) * .03 + Math.sin(t * 7.3) * .03; const g = c.createRadialGradient(W / 2, H / 2, 40, W / 2, H / 2, 560); g.addColorStop(0, `rgba(255,${200 * fl | 0},${120 * fl | 0},1)`); g.addColorStop(1, "#5a2a0a"); c.fillStyle = g; c.fillRect(0, 0, W, H);
    c.fillStyle = "#1a0a04"; c.fillRect(0, 0, W, 30); c.fillRect(0, H - 50, W, 50); for (let i = 0; i < 12; i++) { c.beginPath(); c.moveTo(i * 80, 30); c.quadraticCurveTo(i * 80 + 40, 60, i * 80 + 80, 30); c.fill() }
    c.fillStyle = "#120804"; poligono(c, [[0, 490], [200, 420], [380, 470], [560, 400], [760, 450], [960, 410], [960, 490]], "#120804"); poligono(c, [[600, 410], [690, 300], [720, 300], [810, 430]], "#120804");
    const k = eio(seg(t, .6, 4.4)); const x = lerp(120, 520, k); c.save(); c.globalAlpha = .96; c.drawImage(silueta("#120804"), x, 140 - Math.abs(Math.sin(t * 6)) * 8 * (k < 1), 180, 271); c.restore();
    c.strokeStyle = "#120804"; c.lineWidth = 2; c.beginPath(); c.moveTo(x + 90, 300); c.lineTo(x + 70, H); c.moveTo(x + 40, 260); c.lineTo(x + 20, H); c.stroke();
    const bx = x + 160 + Math.sin(t * 6) * 10, by = 390 - Math.abs(Math.sin(t * 6)) * 30; c.fillStyle = "#120804"; c.beginPath(); c.arc(bx, by, 16, 0, TAU); c.fill(); c.beginPath(); c.moveTo(bx, by); c.lineTo(bx + 30, H); c.stroke();
    if (t > 4.6) { c.globalAlpha = seg(t, 4.6, 5.2); texto(c, "Y el pibe llegó a la ciudad del volcán", W / 2, 90, "30px 'Special Elite'", "#2a1006", "center"); texto(c, T.anio, W / 2, 124, "22px 'Special Elite'", "#3a1a0a", "center"); c.globalAlpha = 1 }
  } });

ESTILOS.push({ slug: "stained-glass", nombre: "Vitral", dur: 8, poster: 6,
  que: "Un vitral de iglesia: la imagen partida en vidrios de color con plomo negro entre cada pieza, y la luz que entra y hace brillar los colores.",
  uso: "Para la devoción: Diego como santo en Nápoles, la «Iglesia Maradoniana», el altar del barrio.",
  draw(c, t, T) {
    const vid = proc("sg-v", () => { const cw = 960, ch = 540, sem = []; for (let i = 0; i < 520; i++) { const cx = 480 + (rnd(i) - .5) * 960, cy = rnd(i + 5) * 540; const d = Math.hypot(cx - 480, (cy - 200) * 1.3); if (d < 250 || rnd(i + 9) < .45) sem.push([cx, cy]) }
      const p = pix(IMG.fotografos, 240, 135, 0, 0, 960, 562), d = p.d.data; const s = lienzo(cw / 2, ch / 2), x = s.getContext("2d"), id = x.createImageData(cw / 2, ch / 2);
      const own = new Int32Array((cw / 2) * (ch / 2)); for (let yy = 0; yy < ch / 2; yy++) for (let xx = 0; xx < cw / 2; xx++) { let b = 0, bd = 1e9; for (let k = 0; k < sem.length; k++) { const dx = sem[k][0] / 2 - xx, dy = sem[k][1] / 2 - yy, dd = dx * dx + dy * dy; if (dd < bd) { bd = dd; b = k } } own[yy * cw / 2 + xx] = b }
      const col = sem.map(([sx, sy]) => { const k = (Math.min(134, Math.floor(sy / 4)) * 240 + Math.min(239, Math.floor(sx / 4))) * 4; let r = d[k], g = d[k + 1], bl = d[k + 2]; const m = Math.max(r, g, bl), mi = Math.min(r, g, bl); const sat = 1.9; r = mi + (r - mi) * sat; g = mi + (g - mi) * sat; bl = mi + (bl - mi) * sat; return [Math.min(255, r * 1.1), Math.min(255, g * 1.1), Math.min(255, bl * 1.25)] });
      for (let yy = 0; yy < ch / 2; yy++) for (let xx = 0; xx < cw / 2; xx++) { const o = own[yy * cw / 2 + xx], i4 = (yy * cw / 2 + xx) * 4; const borde = (xx > 0 && own[yy * cw / 2 + xx - 1] !== o) || (yy > 0 && own[(yy - 1) * cw / 2 + xx] !== o); const [r, g, b] = borde ? [18, 16, 14] : col[o]; id.data[i4] = r; id.data[i4 + 1] = g; id.data[i4 + 2] = b; id.data[i4 + 3] = 255 }
      x.putImageData(id, 0, 0); return s });
    c.fillStyle = "#120e0a"; c.fillRect(0, 0, W, H); c.save(); c.beginPath(); c.moveTo(240, H); c.lineTo(240, 200); c.arc(480, 200, 240, Math.PI, 0); c.lineTo(720, H); c.closePath(); c.clip(); c.imageSmoothingEnabled = false; c.drawImage(vid, 0, 0, W, H);
    const lz = (t * .12) % 1.4 - .2; const g = c.createLinearGradient(200 + lz * 600, 0, 400 + lz * 600, H); g.addColorStop(0, "rgba(255,240,200,0)"); g.addColorStop(.5, "rgba(255,240,200,.35)"); g.addColorStop(1, "rgba(255,240,200,0)"); c.globalCompositeOperation = "lighter"; c.fillStyle = g; c.fillRect(0, 0, W, H); c.restore();
    c.strokeStyle = "#2a2018"; c.lineWidth = 10; c.beginPath(); c.moveTo(240, H); c.lineTo(240, 200); c.arc(480, 200, 240, Math.PI, 0); c.lineTo(720, H); c.stroke();
    texto(c, "SAN", 120, 260, "40px Cinzel", "#c9a24a", "center"); texto(c, apellido(T), 840, 260, `${tam(c, apellido(T), "Cinzel", 36, 200)}px Cinzel`, "#c9a24a", "center"); texto(c, romano(T.anio), 840, 300, "20px Cinzel", "#8a7034", "center");
  } });

ESTILOS.push({ slug: "ukiyoe", nombre: "Grabado japonés", dur: 8, poster: 5,
  que: "Grabado japonés en madera: olas con espuma en garras, el monte al fondo, nubes en franjas, colores planos de tinta y un cartucho vertical con el título.",
  uso: "Para paisajes con épica: el golfo de Nápoles con el Vesubio, la tormenta antes del partido, el mar que cruzó Diego.",
  draw(c, t, T) {
    c.fillStyle = "#efe2c4"; c.fillRect(0, 0, W, H); c.fillStyle = "rgba(220,160,120,.5)"; c.fillRect(0, 0, W, 180);
    c.fillStyle = "#f6ecd4"; for (let i = 0; i < 3; i++) caja(c, 80 + i * 260 + Math.sin(t * .3 + i) * 20, 60 + i * 30, 220, 18, "#f6ecd4", null, 0, 9);
    poligono(c, [[460, 340], [610, 170], [650, 165], [690, 172], [840, 340]], "#5d6e8a"); poligono(c, [[575, 210], [610, 170], [650, 165], [690, 172], [725, 210], [690, 200], [650, 214], [610, 200]], "#fff");
    c.fillStyle = "rgba(230,230,230,.8)"; c.beginPath(); c.arc(650 + Math.sin(t) * 6, 140, 18, 0, TAU); c.arc(668, 120, 14, 0, TAU); c.fill();
    const ola = (y0, amp, col, fase) => { c.fillStyle = col; c.beginPath(); c.moveTo(0, H); for (let x = 0; x <= W; x += 10) c.lineTo(x, y0 + Math.sin(x * .02 + fase) * amp); c.lineTo(W, H); c.fill(); c.strokeStyle = "#f6ecd4"; c.lineWidth = 3; c.beginPath(); for (let x = 0; x <= W; x += 10) c.lineTo(x, y0 + Math.sin(x * .02 + fase) * amp); c.stroke() };
    ola(360, 10, "#5c7fa8", t); ola(400, 12, "#1f3f73", t * 1.2 + 1);
    const cx = 230, cy = 360, k = (Math.sin(t * .8) + 1) / 2; c.fillStyle = "#1f3f73"; c.beginPath(); c.moveTo(0, H); c.lineTo(0, 300); c.bezierCurveTo(60, 180 - k * 20, 260, 150 - k * 20, 330, 250); c.bezierCurveTo(300, 230, 260, 240, 250, 290); c.lineTo(420, H); c.fill();
    c.fillStyle = "#f6ecd4"; for (let i = 0; i < 9; i++) { const a = i / 8; const x = lerp(140, 330, a), y = 165 - k * 20 + Math.pow(a - .5, 2) * 220; c.beginPath(); c.arc(x, y, 12, 0, Math.PI); c.fill(); c.beginPath(); c.arc(x + 8, y + 6, 6, 0, TAU); c.fill() }
    caja(c, 870, 40, 50, 260, "#f6ecd4", "#3a2a1a", 2); c.save(); c.font = "26px 'Special Elite'"; c.fillStyle = "#3a2a1a"; c.textAlign = "center"; [..."NAPOLI"].forEach((ch, i) => c.fillText(ch, 895, 80 + i * 36)); c.restore();
    caja(c, 870, 320, 50, 50, "#b3261e"); texto(c, "10", 895, 354, "24px Anton", "#f6ecd4", "center");
    texto(c, `${apellido(T)} · ${T.anio}`, 40, 520, "16px 'Special Elite'", "#3a2a1a");
  } });

// ===== Impresión y grabado =====
ESTILOS.push({ slug: "engraving", nombre: "Grabado de billete", dur: 8, poster: 6.6,
  que: "Retrato grabado como en un billete: miles de líneas finas paralelas que se engrosan en las sombras, guilloches circulares y números de serie.",
  uso: "Para el dinero y el poder: el precio del pase como billete, los presidentes de la AFA, un «billete de Diego» de recuerdo.",
  draw(c, t, T) {
    const tin = "#1f4a3a"; c.fillStyle = "#ece6cf"; c.fillRect(0, 0, W, H);
    c.save(); c.strokeStyle = "rgba(31,74,58,.35)"; c.lineWidth = .7; for (let i = 0; i < 36; i++) { c.beginPath(); for (let a = 0; a <= TAU + .01; a += .04) { const r = 80 + 10 * Math.sin(a * 12 + i * .3); const x = 160 + Math.cos(a + i * .05) * r * .9, y = 270 + Math.sin(a + i * .05) * r; a ? c.lineTo(x, y) : c.moveTo(x, y) } c.stroke() } c.restore();
    const g = proc("en-g", () => lumGrid(IMG.fotografos, 160, 110, 320, 40, 320, 300)); const filas = 110, k = seg(t, .3, 5.6);
    c.save(); c.beginPath(); c.ellipse(560, 270, 190, 220, 0, 0, TAU); c.clip(); c.strokeStyle = tin; c.lineCap = "round";
    for (let j = 0; j < filas * k; j++) { const y = 50 + j * 4; for (let i = 0; i < 160; i++) { const v = 1 - g[j * 160 + i]; const w = cl((v - .15) * 1.5) * 3.2; if (w < .25) continue; c.lineWidth = w; const x = 370 + i * 2.4; c.beginPath(); c.moveTo(x, y + Math.sin(i * .15) * 1.2); c.lineTo(x + 2.4, y + Math.sin((i + 1) * .15) * 1.2); c.stroke() } } c.restore();
    c.strokeStyle = tin; c.lineWidth = 3; c.beginPath(); c.ellipse(560, 270, 192, 222, 0, 0, TAU); c.stroke(); c.strokeRect(20, 20, W - 40, H - 40); c.lineWidth = 1; c.strokeRect(30, 30, W - 60, H - 60);
    const nn = cifraNum(T.cifra).n || 0, cif = nn ? String(+(nn / 1e6).toFixed(2)).replace(".", ",") : T.cifra; texto(c, "US$", 840, 120, "28px Cinzel", tin, "center"); texto(c, cif, 840, 190, "70px Cinzel", tin, "center"); texto(c, "MILLONES", 840, 220, "16px Cinzel", tin, "center");
    texto(c, apellido(T), 560, 520, "26px Cinzel", tin, "center"); texto(c, `SERIE ${T.anio} · N.º 0000010`, 160, 500, "14px 'Space Mono'", "#a2382a", "center");
  } });

ESTILOS.push({ slug: "printed-long-take", nombre: "Panorámica raspada", dur: 8, poster: 5,
  que: "Un único plano largo que se desplaza sobre un panorama hecho en raspado: fondo negro y todo dibujado con líneas blancas finas, como un grabado continuo.",
  uso: "Para recorrer una escena entera sin cortes: toda la tribuna, la ciudad de punta a punta, el camino del vestuario a la cancha.",
  draw(c, t, T) {
    const esc = proc("plt", () => { const s = lienzo(1900, 540), x = s.getContext("2d"); x.fillStyle = "#0b0b0b"; x.fillRect(0, 0, 1900, 540); const a = bordes(IMG.jueguitos, "#f2f0ea", 960, 540, 0, 0, 960, 540, .16), b = bordes(IMG.brazos, "#f2f0ea", 960, 540, 0, 0, 960, 540, .16); x.drawImage(a, 0, 0); x.save(); x.translate(1900, 0); x.scale(-1, 1); x.drawImage(b, 0, 0); x.restore();
      x.strokeStyle = "rgba(242,240,234,.5)"; x.lineWidth = .8; for (let i = 0; i < 400; i++) { const px = rnd(i) * 1900, py = rnd(i + 4) * 120; x.beginPath(); x.moveTo(px, py); x.lineTo(px + 18, py + 2); x.stroke() } return s });
    const k = eio(seg(t, 0, 8)); c.drawImage(esc, -k * (1900 - W), 0);
    const g = c.createLinearGradient(0, 0, W, 0); g.addColorStop(0, "rgba(11,11,11,.8)"); g.addColorStop(.12, "rgba(11,11,11,0)"); g.addColorStop(.88, "rgba(11,11,11,0)"); g.addColorStop(1, "rgba(11,11,11,.8)"); c.fillStyle = g; c.fillRect(0, 0, W, H);
    caja(c, 30, H - 66, 380, 40, "#0b0b0b", "#f2f0ea", 1); texto(c, `SAN PAOLO · UN SOLO PLANO · ${T.anio}`, 46, H - 40, "15px 'Space Mono'", "#f2f0ea");
  } });

ESTILOS.push({ slug: "woodcut", nombre: "Xilografía", dur: 8, poster: 5.5,
  que: "Grabado en madera de dos tintas: líneas talladas gruesas que siguen la forma, rayos detrás de la figura y textura de la madera en la impresión.",
  uso: "Para épica popular y de lucha: el pueblo con Diego, carteles de agitación, el relato de la final como leyenda impresa.",
  draw(c, t, T) {
    const P = "#efe4cc", N = "#1b1612", R = "#b3261e"; c.fillStyle = P; c.fillRect(0, 0, W, H);
    const kr = eo(seg(t, .2, 1.6)); c.save(); c.translate(480, 300); for (let i = 0; i < 28; i++) { const a = i / 28 * TAU + t * .05; c.fillStyle = i % 2 ? R : P; c.beginPath(); c.moveTo(0, 0); c.arc(0, 0, 700 * kr, a, a + TAU / 28); c.fill() } c.restore();
    const tin = proc("wc-t", () => { const s = lienzo(275, 414), x = s.getContext("2d"); x.drawImage(silueta(N), 0, 0); x.globalCompositeOperation = "destination-out"; x.lineWidth = 2.2; x.strokeStyle = "#000"; for (let y = 0; y < 414; y += 7) { x.beginPath(); for (let xx = 0; xx < 275; xx += 4) x.lineTo(xx, y + Math.sin(xx * .05 + y * .02) * 3); x.stroke() } return s });
    const k = eo(seg(t, 1.2, 2.4)); c.save(); c.globalAlpha = k; c.drawImage(silueta(N), 340, 110 + (1 - k) * 30, 290, 437); c.drawImage(tin, 340, 110 + (1 - k) * 30, 290, 437); c.restore();
    c.save(); c.globalCompositeOperation = "multiply"; c.globalAlpha = .25; c.strokeStyle = "#8a7a5a"; for (let y = 0; y < H; y += 3) { c.lineWidth = rnd(y) * 1.4; c.beginPath(); c.moveTo(0, y); c.lineTo(W, y + Math.sin(y) * 2); c.stroke() } c.restore();
    if (t > 2.6) { const kk = eb(seg(t, 2.6, 3.1)); escala(c, 480, 470, kk, () => { caja(c, -330, -40, 660, 80, N); texto(c, `¡${apellido(T)} ES DEL PUEBLO!`, 0, 18, `${tam(c, `¡${apellido(T)} ES DEL PUEBLO!`, "Anton", 50, 620)}px Anton`, P, "center") }) }
    texto(c, `NÁPOLES ${T.anio}`, 40, 60, "34px Anton", N);
  } });
