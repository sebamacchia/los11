// ---------- lote 3: diagramas de línea · luz y líneas ----------

ESTILOS.push({ slug: "assembly-line-diagram", nombre: "Línea de montaje", dur: 8, poster: 6.2,
  que: "Un proceso explicado como una línea de producción: estaciones numeradas, una cinta que avanza y el objeto que se transforma en cada paso, en dibujo técnico.",
  uso: "Para procesos: cómo se arma una convocatoria, el camino de una pelota del vestuario a la red, la preparación física para la altura.",
  draw(c, t, T) {
    c.fillStyle = "#f2efe6"; c.fillRect(0, 0, W, H); const N = "#1f2a44", R = "#d4472c";
    texto(c, "CÓMO SE HACE UN TRASPASO RÉCORD", 40, 50, "700 22px 'IBM Plex Sans'", N);
    const y = 330; c.strokeStyle = N; c.lineWidth = 2; caja(c, 40, y, 880, 26, "#e2ddcf", N, 2, 13);
    for (let x = 50 - ((t * 80) % 30); x < 920; x += 30) { c.beginPath(); c.arc(x + 15, y + 13, 7, 0, TAU); c.stroke() }
    const est = [["1", "TALENTO", "Fiorito"], ["2", "VIDRIERA", "Barcelona"], ["3", "OFERTA", T.cifra], ["4", "DESTINO", "Napoli"]];
    est.forEach(([n, a, b], i) => { const x = 90 + i * 220; caja(c, x, 150, 150, 140, "#fff", N, 2); poligono(c, [[x + 50, 290], [x + 100, 290], [x + 90, y], [x + 60, y]], "#fff", N, 2);
      c.fillStyle = R; c.beginPath(); c.arc(x + 20, 172, 14, 0, TAU); c.fill(); texto(c, n, x + 20, 177, "700 15px 'IBM Plex Sans'", "#fff", "center");
      texto(c, a, x + 75, 215, "700 18px 'IBM Plex Sans'", N, "center"); texto(c, b, x + 75, 245, `${tam(c, b, "'Space Mono'", 14, 136)}px 'Space Mono'`, N, "center");
      const act = (t * .55) % 4; if (Math.floor(act) === i) { c.fillStyle = R; c.fillRect(x + 6, 282, 138 * (act % 1), 4) } });
    const px = 60 + ((t * .55) % 4) * 220 + 60; pelota(c, px, y - 22, 20, t * 5, "#fff", N, 2);
    texto(c, `${T.nombre.toUpperCase()} · ${T.anio}`, 40, 420, "15px 'Space Mono'", N);
    c.strokeStyle = N; c.setLineDash([4, 4]); c.beginPath(); c.moveTo(40, 440); c.lineTo(920, 440); c.stroke(); c.setLineDash([]);
    texto(c, "FIG. 1 — Línea de montaje del pase (no a escala)", 40, 470, "italic 14px 'IBM Plex Sans'", "#555");
  } });

ESTILOS.push({ slug: "blueprint", nombre: "Plano técnico", dur: 8, poster: 6.6,
  que: "Plano azul de ingeniería: líneas blancas que se dibujan solas, cotas con flechas, grilla y rótulo con número de plano y escala.",
  uso: "Para objetos y espacios: la camiseta del 86, la pelota Azteca, el plano del Azteca y su campo de juego.",
  draw(c, t, T) {
    c.fillStyle = "#123a7a"; c.fillRect(0, 0, W, H); c.strokeStyle = "rgba(255,255,255,.08)"; c.lineWidth = 1; for (let x = 0; x < W; x += 20) { c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke() } for (let y = 0; y < H; y += 20) { c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke() }
    c.strokeStyle = "#eaf2ff"; c.lineWidth = 2; const k = eio(seg(t, .2, 3.2));
    const cam = [[300, 110], [345, 95], [380, 120], [415, 95], [460, 110], [560, 170], [520, 230], [470, 205], [470, 430], [290, 430], [290, 205], [240, 230], [200, 170], [300, 110]].map(([x, y]) => [x + 40, y + 10]);
    trazo(c, cam, k); c.beginPath(); c.arc(420, 108, 30, .2, Math.PI - .2); if (k > .9) c.stroke();
    if (t > 3) { c.save(); c.globalAlpha = seg(t, 3, 3.6); trazoTexto(c, "10", 420, 340, "120px Anton", "#eaf2ff", 2, "center"); c.restore() }
    const cota = (a, b, s, t0, off = 0) => { const kk = seg(t, t0, t0 + .5); if (kk <= 0) return; c.globalAlpha = kk; c.strokeStyle = "#ffd36b"; c.lineWidth = 1.2; c.beginPath(); c.moveTo(...a); c.lineTo(...b); c.stroke(); punta(c, b, a, 8); punta(c, a, b, 8);
      texto(c, s, (a[0] + b[0]) / 2 + off, (a[1] + b[1]) / 2 - 6, "13px 'Space Mono'", "#ffd36b", "center"); c.globalAlpha = 1 };
    cota([330, 465], [510, 465], "48 cm", 3.6); cota([600, 120], [600, 440], "", 4.0); if (t > 4.2) texto(c, "72 cm", 612, 285, "13px 'Space Mono'", "#ffd36b");
    cota([240, 70], [600, 70], "ESCUDO S.S.C.N. → 18 cm", 4.4);
    const kr = seg(t, 5, 5.6); c.globalAlpha = kr; caja(c, 680, 400, 260, 120, null, "#eaf2ff", 1.5); c.strokeStyle = "#eaf2ff"; [430, 460, 490].forEach(y => { c.beginPath(); c.moveTo(680, y); c.lineTo(940, y); c.stroke() });
    texto(c, "PLANO N.º 10", 690, 422, "15px 'Space Mono'", "#eaf2ff"); texto(c, "CAMISETA S.S.C. NAPOLI", 690, 452, "13px 'Space Mono'", "#eaf2ff"); texto(c, `ESC 1:5 · ${T.anio}`, 690, 482, "13px 'Space Mono'", "#eaf2ff"); texto(c, `TITULAR: ${apellido(T)}`, 690, 510, "13px 'Space Mono'", "#eaf2ff"); c.globalAlpha = 1;
  } });

ESTILOS.push({ slug: "hardcore-info", nombre: "Corte en línea", dur: 8, poster: 6,
  que: "Dibujo de línea en blanco y negro con un corte que muestra el interior, líneas guía hacia cada pieza y etiquetas técnicas precisas.",
  uso: "Para explicar objetos: la pelota Azteca (la primera sintética de un Mundial), los botines, la estructura de un estadio.",
  draw(c, t, T) {
    c.fillStyle = "#fbfbf8"; c.fillRect(0, 0, W, H); const cx = 360, cy = 280, R = 170; const k = eio(seg(t, .3, 2));
    c.strokeStyle = "#111"; c.lineWidth = 2.5; c.beginPath(); c.arc(cx, cy, R, -Math.PI / 2, -Math.PI / 2 + k * TAU); c.stroke();
    const kc = eo(seg(t, 2, 3)); if (kc > 0) { c.save(); c.beginPath(); c.moveTo(cx, cy); c.arc(cx, cy, R + 2, -Math.PI / 2, -Math.PI / 2 + kc * Math.PI / 2); c.closePath(); c.fillStyle = "#fbfbf8"; c.fill(); c.restore();
      c.save(); c.beginPath(); c.moveTo(cx, cy); c.arc(cx, cy, R, -Math.PI / 2, -Math.PI / 2 + kc * Math.PI / 2); c.closePath(); c.clip();
      [[R, "#fff"], [R - 10, "#ddd"], [R - 22, "#fff"], [R - 30, "#eee"]].forEach(([r, f]) => { c.fillStyle = f; c.beginPath(); c.arc(cx, cy, r, 0, TAU); c.fill(); c.strokeStyle = "#111"; c.lineWidth = 1.5; c.stroke() });
      c.strokeStyle = "#111"; c.lineWidth = .8; for (let i = 0; i < 40; i++) { c.beginPath(); c.moveTo(cx + i * 6, cy - R); c.lineTo(cx + i * 6 - 60, cy - R + 60); c.stroke() } c.restore();
      c.strokeStyle = "#111"; c.lineWidth = 2.5; c.beginPath(); c.moveTo(cx, cy - R); c.lineTo(cx, cy); c.lineTo(cx + R, cy); c.stroke() }
    if (k > .99) { c.strokeStyle = "#111"; c.lineWidth = 1.5; for (let i = 0; i < 3; i++) { const a = 2.2 + i * .9; c.beginPath(); for (let j = 0; j < 6; j++) { const b = a + j * TAU / 6 * .14; c.lineTo(cx + Math.cos(b) * R * .55, cy + Math.sin(b) * R * .55) } c.stroke() } }
    const et = [[cx + R * .9, cy - R * .5, "CAPA EXTERIOR SINTÉTICA (POLIURETANO)", 3.2], [cx + R * .6, cy - R * .2, "CAPAS INTERNAS DE TELA", 3.7], [cx + R * .35, cy - R * .05, "CÁMARA DE LÁTEX", 4.2], [cx + 4, cy - R + 6, "VÁLVULA", 4.7]];
    et.forEach(([x, y, s, t0], i) => { const kk = seg(t, t0, t0 + .4); if (kk <= 0) return; const ty = 110 + i * 64; c.strokeStyle = "#111"; c.lineWidth = 1; trazo(c, [[x, y], [600, ty], [620, ty]], kk); c.fillStyle = "#111"; c.beginPath(); c.arc(x, y, 3, 0, TAU); c.fill(); if (kk >= 1) texto(c, s, 628, ty + 5, "13px 'Space Mono'", "#111") });
    const kt = seg(t, 5.2, 5.8); c.globalAlpha = kt; texto(c, "PELOTA AZTECA · MÉXICO 1986", 40, 490, "700 22px 'IBM Plex Sans'", "#111"); texto(c, "La primera pelota totalmente sintética de un Mundial.", 40, 516, "15px 'IBM Plex Sans'", "#444"); c.globalAlpha = 1;
  } });

ESTILOS.push({ slug: "instruction-manual", nombre: "Manual de instrucciones", dur: 8, poster: 7,
  que: "Ilustración de manual para armar un mueble: pasos numerados, piezas con cantidad, flechas de movimiento y un muñequito sin cara. Humor seco.",
  uso: "Para explicar algo con ironía: «cómo armar un campeón del mundo», «cómo mudarse a Nápoles», las cábalas de Bilardo paso a paso.",
  draw(c, t, T) {
    c.fillStyle = "#fff"; c.fillRect(0, 0, W, H); c.strokeStyle = "#111"; c.fillStyle = "#111"; c.lineWidth = 2.5; c.lineCap = "round"; c.lineJoin = "round";
    const paso = (n, x, t0, fn) => { const k = seg(t, t0, t0 + .4); if (k <= 0) return; c.globalAlpha = k; caja(c, x, 60, 290, 360, null, "#111", 2); texto(c, String(n), x + 14, 104, "700 40px 'IBM Plex Sans'", "#111"); fn(x); c.globalAlpha = 1 };
    const muneco = (x, y, s = 1, conPelota = false) => { c.beginPath(); c.arc(x, y - 70 * s, 16 * s, 0, TAU); c.stroke(); c.beginPath(); c.moveTo(x, y - 54 * s); c.lineTo(x, y); c.moveTo(x, y); c.lineTo(x - 18 * s, y + 46 * s); c.moveTo(x, y); c.lineTo(x + 18 * s, y + 46 * s); c.moveTo(x, y - 40 * s); c.lineTo(x - 24 * s, y - 14 * s); c.moveTo(x, y - 40 * s); c.lineTo(x + 24 * s, y - 14 * s); c.stroke(); if (conPelota) pelota(c, x + 34 * s, y + 38 * s, 10 * s, 0, "#fff", "#111", 1.5) };
    paso(1, 20, .2, x => { caja(c, x + 70, 200, 150, 110, "#fff", "#111", 2.5); texto(c, "BARCELONA", x + 145, 262, "600 16px 'IBM Plex Sans'", "#111", "center"); muneco(x + 145, 230, .7); texto(c, "×1", x + 230, 380, "700 24px 'IBM Plex Sans'", "#111") });
    paso(2, 335, 1.6, x => { const k = eio(seg(t, 2, 3.4)); c.beginPath(); c.moveTo(x + 40, 300); c.quadraticCurveTo(x + 145, 140, x + 250, 300); c.setLineDash([6, 6]); c.stroke(); c.setLineDash([]);
      const bx = lerp(x + 40, x + 250, k), by = 300 - Math.sin(k * Math.PI) * 80; muneco(bx, by, .5); texto(c, "BCN → NAP", x + 145, 350, "600 16px 'IBM Plex Sans'", "#111", "center") });
    paso(3, 650, 3.6, x => { muneco(x + 120, 270, 1, true); caja(c, x + 30, 330, 230, 2, "#111"); texto(c, "NAPOLI", x + 210, 160, "600 16px 'IBM Plex Sans'", "#111", "center"); const kk = seg(t, 4.4, 4.8); if (kk > 0) { c.strokeStyle = "#1a9a52"; c.lineWidth = 6; trazo(c, [[x + 210, 200], [x + 230, 222], [x + 262, 180]], kk); c.strokeStyle = "#111"; c.lineWidth = 2.5 } });
    const kp = seg(t, 5.2, 5.8); if (kp > 0) { c.globalAlpha = kp; caja(c, 20, 440, 920, 80, "#f2f2f2", "#111", 1.5); texto(c, `1× ${T.nombre.toUpperCase()}`, 40, 472, "600 16px 'IBM Plex Sans'", "#111"); texto(c, `1× ${T.cifra}`, 40, 500, "600 16px 'IBM Plex Sans'", "#111"); texto(c, `MODELO ${T.anio}`, 920, 500, "14px 'Space Mono'", "#555", "right"); c.globalAlpha = 1 }
  } });

ESTILOS.push({ slug: "iso-infographic", nombre: "Infografía isométrica", dur: 8, poster: 6,
  que: "Infografía en perspectiva isométrica: bloques que crecen como torres de datos, una cancha en miniatura y etiquetas que flotan sobre cada elemento.",
  uso: "Para comparar magnitudes: el presupuesto de cada selección, la altura de cada sede, los goles por partido.",
  draw(c, t, T) {
    c.fillStyle = "#eef3f6"; c.fillRect(0, 0, W, H);
    const cubo = (x, y, z0, w, d, h, col) => { const p = (a, b, cc) => iso(a, b, cc, 480, 330, 1); const top = [p(x, y, z0 + h), p(x + w, y, z0 + h), p(x + w, y + d, z0 + h), p(x, y + d, z0 + h)];
      poligono(c, [p(x + w, y, z0), p(x + w, y + d, z0), p(x + w, y + d, z0 + h), p(x + w, y, z0 + h)], col[1]); poligono(c, [p(x, y + d, z0), p(x + w, y + d, z0), p(x + w, y + d, z0 + h), p(x, y + d, z0 + h)], col[2]); poligono(c, top, col[0]) };
    const cancha3 = [iso(-260, -120, 0, 480, 330), iso(40, -120, 0, 480, 330), iso(40, 60, 0, 480, 330), iso(-260, 60, 0, 480, 330)]; poligono(c, cancha3, "#5cbf7e", "#fff", 2);
    const hA = 260 * eo(seg(t, .6, 2.4)), hB = 120 * eo(seg(t, 1, 2.4));
    cubo(100, -140, 0, 70, 70, hA, ["#7cc4ff", "#3b8fd8", "#2a6fb0"]); cubo(100, 20, 0, 70, 70, hB, ["#ff9c8a", "#e2604a", "#b8442f"]);
    pelota(c, ...iso(-110, -30, 14 + Math.abs(Math.sin(t * 3)) * 30, 480, 330), 14, t * 3, "#fff", "#222", 1.5);
    const tag = (p, s1, s2, t0) => { const k = seg(t, t0, t0 + .4); if (k <= 0) return; c.globalAlpha = k; caja(c, p[0] + 20, p[1] - 50, 190, 50, "#fff", "#c5d3dd", 1, 6); texto(c, s1, p[0] + 32, p[1] - 28, "700 16px 'IBM Plex Sans'", "#1d2b38"); texto(c, s2, p[0] + 32, p[1] - 10, "12px 'Space Mono'", "#5d6d7b"); c.strokeStyle = "#c5d3dd"; c.beginPath(); c.moveTo(p[0], p[1]); c.lineTo(p[0] + 20, p[1] - 24); c.stroke(); c.globalAlpha = 1 };
    tag(iso(170, -105, hA, 480, 330), T.cifra, `NAPOLI · ${T.anio}`, 2.6); tag(iso(170, 55, hB, 480, 330), "Pase anterior", "BARCELONA · 1982", 3.2);
    texto(c, "EL PASE EN BLOQUES", 40, 60, "700 26px 'IBM Plex Sans'", "#1d2b38"); texto(c, T.nombre, 40, 86, "15px 'IBM Plex Sans'", "#5d6d7b");
  } });

ESTILOS.push({ slug: "pen-plotter", nombre: "Plóter de pluma", dur: 8, poster: 7.6,
  que: "Un plóter con lapicera dibuja la imagen línea por línea: renglones ondulados que se espesan en las sombras, con la pluma moviéndose sobre el papel.",
  uso: "Para retratos con oficio: los 23 de la lista, cada uno dibujado en vivo. También para mapas y recorridos.",
  draw(c, t, T) {
    c.fillStyle = "#f4f1ea"; c.fillRect(0, 0, W, H); const filas = 64, x0 = 250, x1 = 710, y0 = 40, y1 = 500;
    const g = proc("plot-g", () => lumGrid(IMG.fotografos, 120, 64, 300, 40, 360, 380)); const prog = seg(t, .3, 7.2) * filas;
    c.strokeStyle = "#1e2a5a"; c.lineWidth = 1.1;
    let pen = [x0, y0];
    for (let j = 0; j < Math.min(filas, Math.ceil(prog)); j++) { const y = y0 + (y1 - y0) * j / filas; const hasta = j < Math.floor(prog) ? 1 : prog % 1; c.beginPath();
      for (let i = 0; i <= 240 * hasta; i++) { const v = cl((1 - g[j * 120 + Math.min(119, i >> 1)] - .25) * 1.6); const x = x0 + (x1 - x0) * i / 240; const yy = y + Math.sin(i * 2.4) * v * 6.5; i ? c.lineTo(x, yy) : c.moveTo(x, yy); pen = [x, yy] } c.stroke() }
    c.save(); c.translate(pen[0], pen[1]); c.fillStyle = "#333"; c.fillRect(-4, -60, 8, 56); c.fillStyle = "#1e2a5a"; c.beginPath(); c.moveTo(-4, -4); c.lineTo(4, -4); c.lineTo(0, 2); c.fill(); c.restore();
    c.fillStyle = "#999"; c.fillRect(0, pen[1] - 62, W, 3);
    texto(c, apellido(T), 40, 470, "28px 'Special Elite'", "#1e2a5a"); texto(c, `${T.anio} · PLÓTER 0.3 mm`, 40, 496, "13px 'Space Mono'", "#666");
  } });

ESTILOS.push({ slug: "precise-mechanism", nombre: "Mecanismo por colores", dur: 8, poster: 5,
  que: "Un mecanismo que funciona de verdad, con cada pieza en su color: engranajes que se mueven, una palanca que empuja y flechas que muestran la fuerza.",
  uso: "Para explicar un sistema: cómo funcionaba el líbero de Bilardo, la presión alta, el mecanismo de la FIFA para el sorteo.",
  draw(c, t, T) {
    c.fillStyle = "#f6f4ef"; c.fillRect(0, 0, W, H);
    const rueda = (x, y, r, dientes, ang, col, s) => { c.save(); c.translate(x, y); c.rotate(ang); c.fillStyle = col; c.beginPath(); for (let i = 0; i < dientes * 2; i++) { const a = i / (dientes * 2) * TAU, rr = i % 2 ? r : r + 12; c.lineTo(Math.cos(a) * rr, Math.sin(a) * rr); c.lineTo(Math.cos(a + TAU / dientes / 2) * rr, Math.sin(a + TAU / dientes / 2) * rr) } c.closePath(); c.fill(); c.strokeStyle = "#222"; c.lineWidth = 2; c.stroke();
      c.fillStyle = "#f6f4ef"; c.beginPath(); c.arc(0, 0, r * .3, 0, TAU); c.fill(); c.stroke(); c.restore(); texto(c, s, x, y + r + 40, "600 16px 'IBM Plex Sans'", "#222", "center") };
    const a = t * .9; rueda(250, 240, 100, 14, a, "#e2604a", "BARCELONA"); rueda(250 + 100 + 12 + 70 + 4, 240, 70, 10, -a * 100 / 70 + .15, "#3b8fd8", T.cifra); rueda(250 + 200 + 24 + 140 + 8 - 10, 240, 100, 14, a + .1, "#f0bd1d", "NAPOLI");
    const px = 760 + Math.sin(a * 1.2) * 30; c.strokeStyle = "#222"; c.lineWidth = 6; c.beginPath(); c.moveTo(640, 240); c.lineTo(px + 60, 120); c.stroke();
    c.fillStyle = "#3b8fd8"; c.beginPath(); c.moveTo(px + 60, 120); c.lineTo(px + 110, 100); c.lineTo(px + 98, 130); c.fill();
    c.strokeStyle = "#e2604a"; c.lineWidth = 3; for (let i = 0; i < 3; i++) { const y = 420 + i * 22, k = ((t * 1.5 + i * .3) % 1); c.beginPath(); c.moveTo(150, y); c.lineTo(150 + k * 600, y); c.stroke(); punta(c, [140 + k * 600, y], [150 + k * 600, y], 10) }
    const l = [["#e2604a", "fuerza: la oferta"], ["#3b8fd8", "transmisión: el dinero"], ["#f0bd1d", "salida: el pase"]]; l.forEach(([col, s], i) => { caja(c, 40, 30 + i * 26, 16, 16, col, "#222", 1); texto(c, s, 64, 44 + i * 26, "14px 'IBM Plex Sans'", "#222") });
    texto(c, `${T.nombre.toUpperCase()} · ${T.anio}`, W - 30, 44, "13px 'Space Mono'", "#555", "right");
  } });

ESTILOS.push({ slug: "teardown", nombre: "Despiece", dur: 8, poster: 5.2,
  que: "Vista despiezada: las capas de un objeto se separan en el aire, alineadas sobre un eje, cada una con su nombre, y después vuelven a juntarse.",
  uso: "Para objetos del Mundial: el botín de Diego, la camiseta con sus partes, la copa FIFA por dentro.",
  draw(c, t, T) {
    c.fillStyle = "#e9ecef"; c.fillRect(0, 0, W, H); const ab = Math.sin(seg(t, .4, 7.4) * Math.PI); const sep = eio(ab) * 70;
    const capas = [["CORDONES", "#f8f8f8"], ["CAPELLADA DE CUERO", "#1b1b1b"], ["PLANTILLA", "#c9a26b"], ["SUELA", "#2a2a2a"], [`TAPONES ×6`, "#888"]];
    const cx = 380, base = 340;
    capas.slice().reverse().forEach(([n, col], ri) => { const i = capas.length - 1 - ri; const y = base - (capas.length - 1 - i) * 18 - (capas.length - 1 - i) * sep * .55 + i * 0; const yy = 150 + i * (40 + sep * .55);
      const sh = (yy2) => { c.save(); c.translate(cx, yy2); c.transform(1, 0, -.35, .45, 0, 0);
        if (i === 4) { for (let k = 0; k < 6; k++) { c.fillStyle = col; c.beginPath(); c.arc(-150 + k * 60, 0, 14, 0, TAU); c.fill() } }
        else { c.fillStyle = col; c.beginPath(); c.moveTo(-200, -40); c.quadraticCurveTo(-210, 40, -120, 50); c.lineTo(170, 40); c.quadraticCurveTo(230, 0, 170, -40); c.closePath(); c.fill(); c.strokeStyle = "#555"; c.lineWidth = 2; c.stroke() }
        if (i === 0) { c.strokeStyle = "#ddd"; c.lineWidth = 4; for (let k = 0; k < 5; k++) { c.beginPath(); c.moveTo(-60 + k * 30, -30); c.lineTo(-40 + k * 30, 30); c.stroke() } }
        c.restore() };
      sh(yy); const k = cl(sep / 50); if (k > 0) { c.globalAlpha = k; c.strokeStyle = "#777"; c.lineWidth = 1; c.beginPath(); c.moveTo(cx + 230, yy); c.lineTo(640, yy); c.stroke(); texto(c, n, 650, yy + 5, "14px 'Space Mono'", "#222"); c.globalAlpha = 1 } });
    c.strokeStyle = "rgba(0,0,0,.25)"; c.setLineDash([4, 6]); c.beginPath(); c.moveTo(cx - 70, 120); c.lineTo(cx - 70, 470); c.stroke(); c.setLineDash([]);
    texto(c, `EL BOTÍN · ${apellido(T)} · ${T.anio}`, 40, 50, "700 22px 'IBM Plex Sans'", "#222"); texto(c, "VISTA DESPIEZADA", 40, 74, "13px 'Space Mono'", "#666");
  } });

ESTILOS.push({ slug: "circuit-board", nombre: "Placa de circuito", dur: 8, poster: 5.5,
  que: "Una placa electrónica verde: pistas de cobre que se encienden cuando pasa la corriente de un chip al otro, componentes con nombre y un LED que se prende.",
  uso: "Para flujos y conexiones: cómo llegaba la pelota de Batista a Diego, la red de contactos de Bilardo, el circuito de la plata.",
  draw(c, t, T) {
    c.fillStyle = "#0d4a2e"; c.fillRect(0, 0, W, H); c.fillStyle = "rgba(255,255,255,.04)"; for (let x = 0; x < W; x += 16) for (let y = 0; y < H; y += 16) c.fillRect(x, y, 2, 2);
    const pistas = [[[200, 200], [320, 200], [360, 160], [600, 160], [640, 200], [760, 200]], [[200, 260], [400, 260], [440, 300], [760, 300]], [[200, 320], [300, 320], [340, 380], [560, 380], [600, 340], [760, 340]]];
    pistas.forEach((p, i) => { c.strokeStyle = "#b8862b"; c.lineWidth = 6; c.lineJoin = "round"; c.beginPath(); p.forEach((q, k) => k ? c.lineTo(...q) : c.moveTo(...q)); c.stroke();
      const k = seg(t, .8 + i * .5, 2.6 + i * .5); if (k > 0) { c.save(); c.strokeStyle = "#ffe08a"; brillo(c, "#ffd34d", 14); c.lineWidth = 4; trazo(c, p, k); c.restore() } });
    const chip = (x, y, n) => { caja(c, x - 70, y - 90, 140, 180, "#1a1a1a", "#555", 2, 4); for (let k = 0; k < 8; k++) { c.fillStyle = "#c9c9c9"; c.fillRect(x - 82, y - 80 + k * 22, 12, 8); c.fillRect(x + 70, y - 80 + k * 22, 12, 8) } texto(c, n, x, y + 6, "22px 'Space Mono'", "#ddd", "center") };
    chip(130, 270, "BCN"); chip(830, 270, "NAP");
    const led = t > 3.8; c.fillStyle = led ? "#ff3b30" : "#5a1a16"; if (led) brillo(c, "#ff3b30", 30); c.beginPath(); c.arc(480, 460, 22, 0, TAU); c.fill(); sinSombra(c); texto(c, "LED10", 520, 466, "14px 'Space Mono'", "#cfe8d6");
    texto(c, "R1 " + T.cifra, 420, 140, "13px 'Space Mono'", "#cfe8d6"); texto(c, `U1 ${apellido(T)} ${T.anio}`, 40, 60, "15px 'Space Mono'", "#cfe8d6");
    for (let i = 0; i < 4; i++) { caja(c, 470 + i * 40, 220, 26, 12, "#d8c9a3", "#333", 1) }
  } });

ESTILOS.push({ slug: "firefly-pointillism", nombre: "Puntillismo de luciérnagas", dur: 9, poster: 5,
  que: "Miles de lucecitas en la noche que vagan y de a poco se juntan para formar una figura, y después un número. Poético y nocturno.",
  uso: "Para un momento emotivo: «muchos que se vuelven uno», la hinchada que forma la cara de Diego, el cierre del video.",
  draw(c, t, T) {
    const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, "#050b24"); g.addColorStop(1, "#0f2a2a"); c.fillStyle = g; c.fillRect(0, 0, W, H);
    c.fillStyle = "#06150f"; c.beginPath(); c.moveTo(0, H); for (let x = 0; x <= W; x += 20) c.lineTo(x, 470 + Math.sin(x * .02) * 14 + Math.sin(x * .07) * 6); c.lineTo(W, H); c.fill();
    const pts = puntosSilueta(700, 5); const k1 = eio(seg(t, 1, 4)), k2 = eio(seg(t, 6, 8));
    const diez = proc("ff-10", () => { const s = lienzo(200, 120), x = s.getContext("2d"); x.fillStyle = "#000"; x.font = "110px Anton"; x.textAlign = "center"; x.fillText("10", 100, 108); const d = x.getImageData(0, 0, 200, 120).data, o = []; let k = 0; while (o.length < 700 && k < 80000) { const a = rnd(k * 2.3), b = rnd(k * 5.7); k++; if (d[(Math.floor(b * 120) * 200 + Math.floor(a * 200)) * 4 + 3] > 128) o.push([a, b]) } return o });
    c.globalCompositeOperation = "lighter";
    for (let i = 0; i < pts.length; i++) { const fx = rnd(i) * W + Math.sin(t * .7 + i) * 40, fy = rnd(i + 9) * 440 + Math.cos(t * .5 + i * 1.3) * 30;
      const sx = 380 + pts[i][0] * 210, sy = 60 + pts[i][1] * 380; const d = diez[i % diez.length]; const dx = 280 + d[0] * 400, dy = 120 + d[1] * 240;
      let x = lerp(fx, sx, k1), y = lerp(fy, sy, k1); x = lerp(x, dx, k2); y = lerp(y, dy, k2);
      const br = .4 + .6 * Math.abs(Math.sin(t * 2 + i * 1.7)); c.fillStyle = `rgba(255,230,120,${.15 * br})`; c.beginPath(); c.arc(x, y, 5, 0, TAU); c.fill(); c.fillStyle = `rgba(255,250,200,${.85 * br})`; c.fillRect(x - 1, y - 1, 2, 2) }
    c.globalCompositeOperation = "source-over";
    if (t > 4.4 && t < 6) { const k = Math.min(seg(t, 4.4, 4.9), 1 - seg(t, 5.6, 6)); c.globalAlpha = k; texto(c, nombre1(T), 720, 260, "34px Limelight", "#ffe9a6"); texto(c, `NÁPOLES · ${T.anio}`, 720, 290, "14px 'Space Mono'", "#bfae7a"); c.globalAlpha = 1 }
  } });

ESTILOS.push({ slug: "flow-field", nombre: "Líneas de viento", dur: 8, poster: 5,
  que: "Un campo de flujo: cientos de líneas finas que corren como viento o corriente sobre el mapa y marcan hacia dónde va todo.",
  uso: "Para fuerzas invisibles: el viento a favor de Argentina, la marea de hinchas hacia el Azteca, el éxodo de jugadores a Italia.",
  draw(c, t, T) {
    c.fillStyle = "#0a1626"; c.fillRect(0, 0, W, H); const P = proyector(8.2, 40.6, 1.15); dibujarCosta(c, P, "#13243a", "rgba(140,180,220,.35)", 1);
    const lineasF = proc("ff-lines", () => { const L = []; for (let i = 0; i < 260; i++) { let x = rnd(i) * W, y = rnd(i + 7) * H; const pts = [[x, y]]; for (let k = 0; k < 40; k++) { const a = Math.sin(x * .006 + 1) * .6 + Math.cos(y * .008) * .5 - .05; x += Math.cos(a) * 7; y += Math.sin(a) * 7 - (y - 300) * .004; pts.push([x, y]) } L.push(pts) } return L });
    c.lineCap = "round"; lineasF.forEach((p, i) => { const fase = (t * .6 + rnd(i * 3)) % 1; const a = Math.floor(fase * p.length * .6), b = Math.min(p.length - 1, a + 12); c.strokeStyle = `rgba(160,220,255,${.25 + rnd(i) * .4})`; c.lineWidth = 1.2; c.beginPath(); for (let k = a; k <= b; k++) k === a ? c.moveTo(...p[k]) : c.lineTo(...p[k]); c.stroke() });
    const b = P(BCN), n = P(NAP); [b, n].forEach((q, i) => { c.fillStyle = "#ffcf5a"; c.beginPath(); c.arc(...q, 6, 0, TAU); c.fill(); texto(c, i ? "NÁPOLES" : "BARCELONA", q[0] + 10, q[1] - 10, "14px 'Space Mono'", "#ffcf5a") });
    const k = eio(seg(t, 1, 4)); c.strokeStyle = "#ffcf5a"; c.lineWidth = 3; trazo(c, curva(b, n, 60), k);
    texto(c, "VIENTO A FAVOR", 40, 60, "34px 'Bebas Neue'", "#e9f4ff"); texto(c, `${T.nombre.toUpperCase()} · ${T.anio} · ${T.cifra}`, 40, 86, "13px 'Space Mono'", "#8fb6d8");
  } });

ESTILOS.push({ slug: "neon-tubes", nombre: "Tubos de neón", dur: 8, poster: 5.4,
  que: "Carteles de neón sobre una pared de ladrillos de noche: los tubos se encienden con parpadeos, zumban y reflejan su color en la vereda mojada.",
  uso: "Para la noche y los festejos: Nápoles de fiesta, el Obelisco después de la final, el cartel del título de un capítulo.",
  draw(c, t, T) {
    c.fillStyle = "#140d10"; c.fillRect(0, 0, W, H); for (let y = 0; y < 400; y += 26) for (let x = (y / 26) % 2 ? -30 : 0; x < W; x += 60) { caja(c, x + 2, y + 2, 56, 22, "#221519") }
    const g = c.createLinearGradient(0, 400, 0, H); g.addColorStop(0, "#0b0809"); g.addColorStop(1, "#000"); c.fillStyle = g; c.fillRect(0, 400, W, 140);
    const on = (t0) => t > t0 && !(t > t0 + .1 && t < t0 + .18) && !(t > t0 + .3 && t < t0 + .34);
    const tubo = (fn, col, t0) => { const e = on(t0); c.save(); c.lineCap = "round"; c.lineJoin = "round"; c.strokeStyle = e ? col : "#3a2a30"; c.lineWidth = 7; if (e) { brillo(c, col, 28); fn(); fn(); c.shadowBlur = 8 } fn(); c.strokeStyle = e ? "#fff" : "#4a3a40"; c.lineWidth = 2; c.globalAlpha = e ? .7 : .4; fn(); c.restore() };
    tubo(() => { c.font = "120px Monoton"; c.textAlign = "center"; c.strokeText("NAPOLI", W / 2, 210) }, "#33c6ff", .5);
    tubo(() => { c.beginPath(); c.arc(170, 320, 50, 0, TAU); c.stroke(); c.beginPath(); for (let i = 0; i < 5; i++) { const a = -Math.PI / 2 + i * TAU / 5; c.lineTo(170 + Math.cos(a) * 16, 320 + Math.sin(a) * 16) } c.closePath(); c.stroke() }, "#ffffff", 1.6);
    tubo(() => { c.font = "90px Monoton"; c.textAlign = "left"; c.strokeText("10", 700, 360) }, "#ff3d8b", 2.4);
    tubo(() => { c.font = "38px Monoton"; c.textAlign = "center"; c.strokeText(T.anio, W / 2, 300) }, "#ffcf3a", 3.2);
    c.save(); c.globalAlpha = .25; c.translate(0, 800); c.scale(1, -1); c.globalCompositeOperation = "lighter"; c.drawImage(c.canvas, 0, 0, c.canvas.width, c.canvas.height * .74, 0, 0, W, H * .74); c.restore();
    if (t > 4.4) texto(c, `${T.nombre} · ${T.cifra}`, W / 2, 520, "14px 'Space Mono'", "rgba(255,220,240,.6)", "center");
  } });

ESTILOS.push({ slug: "oscilloscope-math", nombre: "Matemática de osciloscopio", dur: 8, poster: 6.2,
  que: "Osciloscopio de fósforo verde: un haz que traza curvas y fórmulas sobre la grilla, con persistencia luminosa y ecuaciones escritas al costado.",
  uso: "Para la física del fútbol: la parábola de un tiro libre, la velocidad de Burruchaga en el 3-2, la altura y el aire en México.",
  draw(c, t, T) {
    c.fillStyle = "#031208"; c.fillRect(0, 0, W, H); const ox = 80, oy = 60, gw = 600, gh = 400;
    c.strokeStyle = "rgba(60,255,140,.18)"; c.lineWidth = 1; for (let i = 0; i <= 10; i++) { c.beginPath(); c.moveTo(ox + i * gw / 10, oy); c.lineTo(ox + i * gw / 10, oy + gh); c.stroke() } for (let j = 0; j <= 8; j++) { c.beginPath(); c.moveTo(ox, oy + j * gh / 8); c.lineTo(ox + gw, oy + j * gh / 8); c.stroke() }
    const k = seg(t, .4, 4.4); const curvaP = []; for (let i = 0; i <= 120; i++) { const u = i / 120; curvaP.push([ox + u * gw, oy + gh - (4 * u * (1 - u)) * gh * .85 - 10]) }
    c.save(); c.strokeStyle = "#7dffb0"; brillo(c, "#3dff8a", 16); c.lineWidth = 2.5; const fin = trazo(c, curvaP, k); c.restore();
    c.fillStyle = "#e8fff0"; brillo(c, "#3dff8a", 20); c.beginPath(); c.arc(...fin, 5, 0, TAU); c.fill(); sinSombra(c);
    if (t > 4.4) { const k2 = seg(t, 4.4, 6.4); const lis = []; for (let i = 0; i <= 200 * k2; i++) { const a = i / 200 * TAU; lis.push([ox + gw / 2 + Math.sin(3 * a + t) * 120, oy + gh / 2 + Math.sin(2 * a) * 90]) } c.save(); c.strokeStyle = "rgba(125,255,176,.7)"; brillo(c, "#3dff8a", 10); c.lineWidth = 1.6; c.beginPath(); lis.forEach((p, i) => i ? c.lineTo(...p) : c.moveTo(...p)); c.stroke(); c.restore() }
    const eq = ["y(x) = v·sen(θ)·t − ½·g·t²", "g (México) ≈ 9,78 m/s²", "θ = 45°", T.titulo.length > 24 ? T.anio : T.titulo];
    eq.forEach((s, i) => { const kk = seg(t, 1 + i * .9, 1.6 + i * .9); texto(c, tipeo(s, kk), 710, 120 + i * 40, "15px 'Space Mono'", "#9dffc4") });
    texto(c, `CH1 · ${apellido(T)}`, ox, oy - 14, "13px 'Space Mono'", "#5fd58f"); lineasScan(c, .12, 3);
  } });
