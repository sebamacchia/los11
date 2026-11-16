// ---------- lote 4: boceto y pizarra · pintura e ilustración ----------

ESTILOS.push({ slug: "chalkboard", nombre: "Pizarrón de tiza", dur: 8, poster: 6.8,
  que: "Pizarrón verde con tiza: la letra se escribe en vivo, los dibujos se hacen a mano alzada y quedan rastros de borrador. Clase de escuela.",
  uso: "Para desmitificar o explicar el origen de algo: de dónde viene «el pibe de oro», qué era el «3-5-2», la regla del offside de 1986.",
  draw(c, t0, T) {
    const f = Math.floor(t0 * 12), t = t0;
    const g = c.createRadialGradient(W / 2, H / 2, 100, W / 2, H / 2, 650); g.addColorStop(0, "#2f5a45"); g.addColorStop(1, "#1d3a2c"); c.fillStyle = g; c.fillRect(0, 0, W, H);
    c.fillStyle = "rgba(255,255,255,.05)"; for (let i = 0; i < 6; i++) { c.beginPath(); c.ellipse(150 + i * 140, 120 + (i % 2) * 260, 120, 40, .3, 0, TAU); c.fill() }
    c.fillStyle = "#6b4a2b"; c.fillRect(0, H - 22, W, 22); c.fillStyle = "#eee"; c.fillRect(120, H - 30, 40, 9);
    const esc = (s, x, y, t1, size = 44, col = "#f3f1ea") => { const k = seg(t, t1, t1 + s.length * .05); if (k > 0) tiza(c, tipeo(s, k), x, y, size, "Caveat", col, f) };
    esc(`${T.anio}: el pase más caro`, 60, 90, .2, 56);
    esc("BARCELONA", 80, 220, 1.4); esc("NAPOLI", 640, 220, 2.0);
    const k = seg(t, 2.4, 3.2); c.strokeStyle = "rgba(243,241,234,.85)"; c.lineWidth = 3; c.lineCap = "round"; const p = curva([270, 205], [630, 205], 60); const fin = trazo(c, p, k); if (k >= 1) punta(c, p[p.length - 3], fin, 18);
    if (t > 3.2) { c.save(); c.strokeStyle = "rgba(243,241,234,.8)"; c.lineWidth = 3; c.beginPath(); c.arc(450, 330, 46, 0, TAU * seg(t, 3.2, 3.8)); c.stroke(); c.restore(); esc("$", 438, 348, 3.6, 50, "#f6e27a") }
    esc(`= ${T.cifra}`, 520, 345, 4.0, 46, "#f6e27a");
    esc(`(${T.nombre})`, 60, 440, 5.2, 34, "#cfe3d6");
    if (t > 6.4) { c.save(); c.globalAlpha = .9; c.strokeStyle = "#f6e27a"; c.lineWidth = 4; trazo(c, [[515, 360], [880, 360]], seg(t, 6.4, 6.8)); c.restore() }
  } });

ESTILOS.push({ slug: "ipad-sketch", nombre: "Boceto en tableta", dur: 8, poster: 7,
  que: "Dibujos de marcador de colores sobre una hoja blanca de tableta: trazos rápidos, íconos simpáticos, letra a mano y la barra de herramientas al costado.",
  uso: "Para explicaciones livianas: qué comían en la concentración, cómo viajaron, la vida en el Club América.",
  draw(c, t, T) {
    c.fillStyle = "#fbfbfb"; c.fillRect(0, 0, W, H); caja(c, 20, 140, 50, 260, "#f0f0f0", "#ddd", 1, 12); ["#e74c3c", "#3498db", "#f1c40f", "#2ecc71", "#222"].forEach((col, i) => { c.fillStyle = col; c.beginPath(); c.arc(45, 170 + i * 48, 13, 0, TAU); c.fill() });
    c.lineCap = "round"; c.lineJoin = "round";
    const marca = (pts, col, lw, t0, dur = .7) => { const k = seg(t, t0, t0 + dur); if (k <= 0) return null; c.strokeStyle = col; c.lineWidth = lw; return trazo(c, pts, k) };
    const pin = (x, y, col, t0) => { const pts = []; for (let i = 0; i <= 30; i++) { const a = Math.PI * .75 + i / 30 * Math.PI * 1.5; pts.push([x + Math.cos(a) * 26, y - 30 + Math.sin(a) * 26]) } pts.push([x, y + 10]); pts.push(pts[0]); marca(pts, col, 5, t0) };
    pin(200, 260, "#e74c3c", .2); pin(700, 240, "#3498db", 1.0);
    if (t > .9) texto(c, "Barcelona", 140, 330, "36px 'Permanent Marker'", "#e74c3c"); if (t > 1.7) texto(c, "Napoli", 650, 310, "36px 'Permanent Marker'", "#3498db");
    marca(curva([230, 230], [670, 210], 90), "#222", 4, 1.8, 1.2);
    const kb = seg(t, 3.2, 3.9); if (kb > 0) { c.save(); c.globalAlpha = kb; c.fillStyle = "#f1c40f"; c.beginPath(); c.arc(450, 400, 60, 0, TAU); c.fill(); c.strokeStyle = "#222"; c.lineWidth = 4; c.stroke(); texto(c, "$", 450, 425, "64px 'Permanent Marker'", "#222", "center"); c.restore() }
    if (t > 4.2) { const s = tipeo(`¡${T.cifra}!`, seg(t, 4.2, 5.4)); texto(c, s, 540, 430, `${tam(c, `¡${T.cifra}!`, "'Permanent Marker'", 40, 380)}px 'Permanent Marker'`, "#2ecc71") }
    marca([[540, 445], [900, 450]], "#2ecc71", 6, 5.4, .4);
    if (t > 6) texto(c, `${nombre1(T)}, ${T.anio}`, 120, 80, "34px Caveat", "#555");
    const tip = [[200, 260], [700, 240], [450, 220], [450, 400], [700, 430], [700, 445], [160, 70]][Math.min(6, Math.floor(t / 1.1))]; c.save(); c.translate(tip[0] + 6, tip[1] - 6); c.rotate(.7); c.fillStyle = "#ddd"; c.fillRect(0, -6, 120, 12); c.fillStyle = "#555"; c.beginPath(); c.moveTo(0, -6); c.lineTo(-16, 0); c.lineTo(0, 6); c.fill(); c.restore();
  } });

ESTILOS.push({ slug: "marker-paper", nombre: "Marcador sobre papel", dur: 8, poster: 7.4,
  que: "Un problema resuelto a mano con marcador sobre papel cuadriculado: los números se escriben, se subrayan y se encierran en círculo, paso por paso.",
  uso: "Para las cuentas: cuántos dólares por hincha, cuántos kilómetros recorrió el plantel, la diferencia de altura entre sedes.",
  draw(c, t, T) {
    c.fillStyle = "#fffdf5"; c.fillRect(0, 0, W, H); c.strokeStyle = "rgba(60,120,200,.18)"; c.lineWidth = 1; for (let x = 0; x < W; x += 28) { c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke() } for (let y = 0; y < H; y += 28) { c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke() }
    const n = cifraNum(T.cifra).n || 7500000, hinchas = 70000, r = n / hinchas;
    const lin = [[`¿Cuánto costó cada hincha?`, 70, 80, "#d6382c", .2], [`${miles(n)} ÷ ${miles(hinchas)}`, 90, 180, "#1d1d1d", 1.4], [`= ${r.toFixed(1).replace(".", ",")} US$`, 90, 260, "#1d1d1d", 2.8], [`por cada persona en el San Paolo (${T.anio})`, 90, 330, "#555", 4.2]];
    lin.forEach(([s, x, y, col, t0]) => { const k = seg(t, t0, t0 + s.length * .04); if (k > 0) texto(c, tipeo(s, k), x, y, "46px 'Permanent Marker'".replace("46", s.length > 30 ? "34" : "46"), col) });
    const ks = seg(t, 5.4, 6.2); if (ks > 0) { c.strokeStyle = "#d6382c"; c.lineWidth = 4; c.beginPath(); c.ellipse(250, 245, 190, 45, -.02, 0, TAU * ks); c.stroke() }
    const ku = seg(t, 6.4, 6.9); if (ku > 0) { c.strokeStyle = "#f2c200"; c.globalAlpha = .45; c.lineWidth = 22; trazo(c, [[80, 170], [640, 170]], ku); c.globalAlpha = 1 }
    texto(c, "≈ 70.000 personas en la presentación", 70, 480, "26px Caveat", "#777");
  } });

ESTILOS.push({ slug: "one-line", nombre: "Dibujo de una sola línea", dur: 8, poster: 7.6,
  que: "Todo con una sola línea continua que nunca se corta: la línea va dibujando la pelota, el número y la firma, sobre fondo claro.",
  uso: "Para momentos simples y elegantes: una dedicatoria, el homenaje del final, el logo de un capítulo.",
  draw(c, t, T) {
    c.fillStyle = "#f5f2ec"; c.fillRect(0, 0, W, H);
    const pts = proc("ol-path", () => { const P = []; for (let i = 0; i <= 60; i++) P.push([80 + i * 3, 420 - Math.sin(i * .1) * 10]);
      for (let i = 0; i <= 120; i++) { const a = Math.PI + i / 120 * TAU * 1.05; P.push([340 + Math.cos(a) * 90, 300 + Math.sin(a) * 90]) }
      for (let i = 0; i <= 30; i++) { const a = i / 30 * TAU; P.push([340 + Math.cos(a) * 28, 300 + Math.sin(a) * 28]) }
      [[420, 300], [480, 380], [520, 240], [520, 420], [560, 420], [600, 240]].forEach(p => P.push(p));
      for (let i = 0; i <= 80; i++) { const a = -Math.PI / 2 + i / 80 * TAU; P.push([660 + Math.cos(a) * 50, 330 + Math.sin(a) * 90]) }
      for (let i = 0; i <= 60; i++) P.push([710 + i * 3.5, 420 + Math.sin(i * .25) * 8]); return P });
    c.strokeStyle = "#1c1c1c"; c.lineWidth = 3; c.lineCap = "round"; c.lineJoin = "round"; const fin = trazo(c, pts, eio(seg(t, .2, 6.6)));
    c.fillStyle = "#d6382c"; c.beginPath(); c.arc(...fin, 5, 0, TAU); c.fill();
    if (t > 6.8) { c.globalAlpha = seg(t, 6.8, 7.4); texto(c, `${T.nombre} · ${T.anio}`, 80, 490, "18px 'IBM Plex Sans'", "#555"); c.globalAlpha = 1 }
  } });

ESTILOS.push({ slug: "sketchnote", nombre: "Apuntes visuales", dur: 8, poster: 7.4,
  que: "Una página de apuntes visuales: títulos en recuadro, íconos dibujados, flechas, viñetas y resaltador. Todo el resumen en una sola hoja.",
  uso: "Para el resumen del video o de un capítulo: los 7 partidos en una página, los datos clave antes del final.",
  draw(c, t, T) {
    c.fillStyle = "#fdfcf7"; c.fillRect(0, 0, W, H); c.strokeStyle = "#222"; c.lineWidth = 2.5; c.lineCap = "round";
    const ap = (t0) => eo(seg(t, t0, t0 + .5));
    let k = ap(.2); if (k) { c.globalAlpha = k; caja(c, 300, 24, 360, 64, "#ffe28a", "#222", 3, 10); texto(c, `EL PASE · ${T.anio}`, 480, 68, "36px 'Permanent Marker'", "#222", "center"); c.globalAlpha = 1 }
    const nota = (x, y, tit, cuerpo, t0, icono) => { const k2 = ap(t0); if (!k2) return; c.globalAlpha = k2; texto(c, tit, x, y, "28px 'Permanent Marker'", "#d6382c"); c.strokeStyle = "#d6382c"; c.lineWidth = 2; c.beginPath(); c.moveTo(x, y + 6); c.lineTo(x + c.measureText(tit).width, y + 8); c.stroke();
      cuerpo.forEach((l, i) => texto(c, "• " + l, x, y + 40 + i * 30, "26px Caveat", "#222")); icono && icono(); c.globalAlpha = 1 };
    nota(50, 140, "¿QUIÉN?", [T.nombre, "23 años"], 1.0, () => { c.strokeStyle = "#222"; c.lineWidth = 2.5; c.beginPath(); c.arc(330, 150, 26, 0, TAU); c.stroke(); for (let i = 0; i < 7; i++) { c.beginPath(); c.arc(312 + i * 6, 128, 7, Math.PI, 0); c.stroke() } });
    nota(520, 140, "¿CUÁNTO?", [T.cifra, "récord mundial"], 2.0, () => pelota(c, 860, 160, 24, .3, "#fff", "#222", 2));
    nota(50, 340, "¿DÓNDE?", ["Barcelona → Nápoles", "San Paolo, 5 de julio"], 3.0, () => { c.strokeStyle = "#222"; c.beginPath(); c.moveTo(330, 360); c.quadraticCurveTo(380, 320, 430, 360); c.stroke(); punta(c, [420, 352], [430, 360], 10) });
    nota(520, 340, "¿Y DESPUÉS?", ["2 scudetti", "México 86 →"], 4.0, () => { c.strokeStyle = "#222"; c.lineWidth = 2.5; poligono(c, [[860, 330], [890, 330], [884, 380], [866, 380]], null, "#222", 2.5) });
    const kh = seg(t, 5.2, 5.8); if (kh) { c.save(); c.globalAlpha = .35; c.fillStyle = "#7ee0a1"; c.fillRect(515, 172, 300 * kh, 30); c.restore() }
    if (t > 6) { c.strokeStyle = "#222"; c.setLineDash([6, 6]); c.lineWidth = 1.5; c.beginPath(); c.moveTo(480, 110); c.lineTo(480, 520); c.moveTo(30, 300); c.lineTo(930, 300); c.stroke(); c.setLineDash([]) }
  } });

ESTILOS.push({ slug: "stick-explainer", nombre: "Explicación con palitos", dur: 8, poster: 4.6,
  que: "Muñequitos de palito que actúan la historia: caminan, cargan cosas, hablan con globitos y se mueven entre lugares dibujados con lo mínimo.",
  uso: "Para ideas y relaciones: la pelea Menotti-Bilardo, el grupo que se cerró, la red de pases del equipo.",
  draw(c, t, T) {
    c.fillStyle = "#fff"; c.fillRect(0, 0, W, H); c.strokeStyle = "#111"; c.lineWidth = 3; c.lineCap = "round";
    c.beginPath(); c.moveTo(0, 430); c.lineTo(W, 430); c.stroke();
    const edif = (x, n) => { c.strokeRect(x, 280, 140, 150); for (let i = 0; i < 3; i++) c.strokeRect(x + 15 + i * 42, 300, 26, 30); texto(c, n, x + 70, 270, "600 18px 'IBM Plex Sans'", "#111", "center") };
    edif(40, "BARCELONA"); edif(780, "NAPOLI");
    const k = eio(seg(t, 1, 4.5)); const x = lerp(240, 720, k), fase = t * 9 * (k > 0 && k < 1 ? 1 : 0);
    c.beginPath(); c.arc(x, 330, 16, 0, TAU); c.stroke(); for (let i = 0; i < 5; i++) { c.beginPath(); c.arc(x - 12 + i * 6, 316, 6, Math.PI, 0); c.stroke() }
    c.beginPath(); c.moveTo(x, 346); c.lineTo(x, 390); c.moveTo(x, 390); c.lineTo(x - 14 * Math.sin(fase), 430); c.moveTo(x, 390); c.lineTo(x + 14 * Math.sin(fase), 430); c.moveTo(x, 360); c.lineTo(x + 20, 380); c.moveTo(x, 360); c.lineTo(x - 20, 380); c.stroke();
    pelota(c, x + 26 + Math.abs(Math.sin(fase)) * 4, 420 - Math.abs(Math.sin(fase * .5)) * 20, 10, fase, "#fff", "#111", 1.5);
    const globo = (gx, gy, s, t0, t1) => { if (t < t0 || t > t1) return; c.font = "22px Caveat"; const w = c.measureText(s).width + 30; caja(c, gx - w / 2, gy - 50, w, 44, "#fff", "#111", 2, 14); c.beginPath(); c.moveTo(gx - 6, gy - 6); c.lineTo(gx, gy + 10); c.lineTo(gx + 6, gy - 6); c.fillStyle = "#fff"; c.fill(); c.stroke(); texto(c, s, gx, gy - 20, "22px Caveat", "#111", "center") };
    globo(240, 300, "¡Ciao, Barcelona!", .3, 1.6); globo(720, 300, "¡Ciao, Napoli!", 4.6, 6.2);
    if (t > 5.4) { const k2 = seg(t, 5.4, 6); c.globalAlpha = k2; texto(c, T.cifra, W / 2, 140, `${tam(c, T.cifra, "'Permanent Marker'", 54, 600)}px 'Permanent Marker'`, "#111", "center"); texto(c, `${T.nombre} · ${T.anio}`, W / 2, 180, "20px Caveat", "#555", "center"); c.globalAlpha = 1 }
  } });

ESTILOS.push({ slug: "whiteboard", nombre: "Pizarra blanca con mano", dur: 8, poster: 7.3,
  que: "Una mano con marcador dibuja y escribe en una pizarra blanca, todo en tiempo real: cada idea aparece justo cuando se nombra.",
  uso: "Para explicaciones largas con narración: el reglamento del Mundial, el contexto político de 1986, la historia de la AFA.",
  draw(c, t, T) {
    c.fillStyle = "#fafafa"; c.fillRect(0, 0, W, H); c.strokeStyle = "#1a1a1a"; c.lineWidth = 4; c.lineCap = "round"; c.lineJoin = "round"; let mano = [W + 50, H];
    const k1 = seg(t, .2, 1.6); if (k1 > 0) { const s = tipeo(T.titulo.toUpperCase(), k1); texto(c, s, 60, 90, `${tam(c, T.titulo.toUpperCase(), "'Permanent Marker'", 44, 840)}px 'Permanent Marker'`, "#1a1a1a"); c.font = `${tam(c, T.titulo.toUpperCase(), "'Permanent Marker'", 44, 840)}px 'Permanent Marker'`; mano = [60 + c.measureText(s).width, 80] }
    const k2 = seg(t, 1.8, 3.2); if (k2 > 0) { const p = [[120, 280], [180, 240], [260, 260], [300, 230], [340, 280], [120, 280]]; mano = trazo(c, p, k2); if (k2 >= 1) texto(c, "BCN", 190, 320, "30px 'Permanent Marker'", "#1a1a1a") }
    const k3 = seg(t, 3.2, 4.4); if (k3 > 0) { c.strokeStyle = "#1565c0"; const p = curva([360, 260], [600, 260], 80); mano = trazo(c, p, k3); if (k3 >= 1) punta(c, p[p.length - 3], p[p.length - 1], 18); c.strokeStyle = "#1a1a1a" }
    const k4 = seg(t, 4.4, 5.6); if (k4 > 0) { const p = []; for (let i = 0; i <= 40; i++) { const a = i / 40 * TAU; p.push([700 + Math.cos(a) * 70, 260 + Math.sin(a) * 60]) } mano = trazo(c, p, k4); if (k4 >= 1) texto(c, "NAP", 700, 270, "30px 'Permanent Marker'", "#1a1a1a", "center") }
    const k5 = seg(t, 5.6, 6.8); if (k5 > 0) { c.fillStyle = "#c62828"; const s = tipeo(T.cifra, k5); texto(c, s, 300, 440, "52px 'Permanent Marker'", "#c62828"); c.font = "52px 'Permanent Marker'"; mano = [300 + c.measureText(s).width, 430] }
    c.save(); c.translate(mano[0], mano[1]); c.rotate(.5); c.fillStyle = "#2b2b2b"; c.fillRect(-6, 0, 12, 90); c.fillStyle = "#f1c9a5"; c.beginPath(); c.ellipse(10, 110, 34, 46, -.3, 0, TAU); c.fill(); c.fillStyle = "#e3b48c"; c.beginPath(); c.ellipse(-14, 80, 10, 22, .4, 0, TAU); c.fill(); c.restore();
  } });

ESTILOS.push({ slug: "colored-pencil", nombre: "Lápices de colores científicos", dur: 8, poster: 6.6,
  que: "Ilustración científica con lápices de colores: un corte que muestra el interior, sombreado con trazos cruzados, etiquetas a mano y un papel con textura.",
  uso: "Para ciencia y geografía: el volcán de Nápoles, la altura del DF y el aire, el cuerpo de un atleta en la altura.",
  draw(c, t, T) {
    c.drawImage(proc("cp-pap", () => papel("#f6f1e3", 480, 270, 16)), 0, 0, W, H);
    const lapiz = (pts, col, densidad, ang, t0) => { const k = seg(t, t0, t0 + 1.2); if (k <= 0) return; c.save(); c.beginPath(); pts.forEach((p, i) => i ? c.lineTo(...p) : c.moveTo(...p)); c.closePath(); c.clip(); c.strokeStyle = col; c.lineWidth = 1.4; c.globalAlpha = .7;
      const n = Math.floor(260 * k * densidad); for (let i = 0; i < n; i++) { const x = rnd(i) * W, y = rnd(i + 3) * H; c.beginPath(); c.moveTo(x, y); c.lineTo(x + Math.cos(ang) * 60, y + Math.sin(ang) * 60); c.stroke() } c.restore() };
    const volcan = [[120, 450], [380, 170], [440, 160], [480, 175], [760, 450]];
    lapiz(volcan, "#7a5a3a", 3, -.9, .2); lapiz(volcan, "#a57b4c", 2, .7, .6);
    const camara = [[330, 450], [430, 330], [480, 330], [560, 450]]; lapiz(camara, "#d8442a", 4, -.6, 1.6); lapiz([[425, 330], [440, 175], [470, 175], [480, 330]], "#ef7a2a", 4, .3, 2.2);
    c.strokeStyle = "#3a2a1a"; c.lineWidth = 2; poligono(c, volcan, null, "#3a2a1a", 2); c.fillStyle = "rgba(110,150,200,.35)"; c.fillRect(0, 450, W, 90);
    if (t > 3) { c.save(); c.globalAlpha = .8; c.fillStyle = "#cfcfcf"; for (let i = 0; i < 5; i++) { c.beginPath(); c.arc(455 + Math.sin(t + i) * 20, 150 - i * 24 - (t % 2) * 6, 16 + i * 4, 0, TAU); c.fill() } c.restore() }
    const et = [[450, 165, 640, 140, "CRÁTER", 3.6], [470, 380, 680, 360, "CÁMARA MAGMÁTICA", 4.2], [600, 450, 760, 480, "GOLFO DE NÁPOLES", 4.8]];
    et.forEach(([a, b, x, y, s, t0]) => { const k = seg(t, t0, t0 + .4); if (k <= 0) return; c.globalAlpha = k; c.strokeStyle = "#3a2a1a"; c.lineWidth = 1; c.beginPath(); c.moveTo(a, b); c.lineTo(x - 6, y - 6); c.stroke(); texto(c, s, x, y, "26px Caveat", "#3a2a1a"); c.globalAlpha = 1 });
    texto(c, "Vesubio · 1.281 m", 40, 60, "38px Caveat", "#3a2a1a"); if (t > 5.4) texto(c, `y a sus pies, desde ${T.anio}, ${nombre1(T).charAt(0) + nombre1(T).slice(1).toLowerCase()}.`, 40, 96, "28px Caveat", "#8a3a2a");
  } });

ESTILOS.push({ slug: "crayon-book", nombre: "Libro de crayones", dur: 8, poster: 6.4,
  que: "Dibujo infantil con crayones: trazos cerosos que no llenan del todo, un sol con rayos, una casita y un nene con la pelota. Cuento antes de dormir.",
  uso: "Para la infancia de Diego en Fiorito, el sueño del Mundial, una carta a la mamá. Es tierno y directo.",
  draw(c, t, T) {
    c.fillStyle = "#fdfaf1"; c.fillRect(0, 0, W, H);
    const cera = (fn, col, t0, n = 200) => { const k = seg(t, t0, t0 + .8); if (k <= 0) return; c.save(); c.beginPath(); fn(); c.clip(); c.strokeStyle = col; c.lineWidth = 7; c.globalAlpha = .55; c.lineCap = "round";
      for (let i = 0; i < n * k; i++) { const x = rnd(i * 1.3 + t0) * W, y = rnd(i * 2.1 + t0) * H; c.beginPath(); c.moveTo(x - 40, y + 14); c.lineTo(x + 40, y - 14); c.stroke() } c.restore() };
    cera(() => c.rect(0, 0, W, 330), "#8fd3ff", .1, 260); cera(() => c.rect(0, 330, W, 210), "#7cc96b", .5, 220);
    cera(() => c.arc(800, 100, 60, 0, TAU), "#ffd23f", 1.0, 120); if (t > 1.2) { c.strokeStyle = "#ffb200"; c.lineWidth = 6; c.lineCap = "round"; for (let i = 0; i < 10; i++) { const a = i / 10 * TAU + t * .2; c.beginPath(); c.moveTo(800 + Math.cos(a) * 75, 100 + Math.sin(a) * 75); c.lineTo(800 + Math.cos(a) * 105, 100 + Math.sin(a) * 105); c.stroke() } }
    cera(() => c.rect(120, 230, 180, 140), "#ff8c69", 1.6, 140); cera(() => { c.moveTo(100, 235); c.lineTo(210, 150); c.lineTo(320, 235) }, "#c0392b", 2.0, 120);
    if (t > 2.6) { c.strokeStyle = "#333"; c.lineWidth = 5; c.lineCap = "round"; const x = 520, y = 330 + Math.sin(t * 4) * 4; c.beginPath(); c.arc(x, y - 70, 22, 0, TAU); c.stroke(); for (let i = 0; i < 6; i++) { c.beginPath(); c.arc(x - 15 + i * 6, y - 92, 7, Math.PI, 0); c.stroke() }
      c.beginPath(); c.moveTo(x, y - 48); c.lineTo(x, y + 10); c.moveTo(x, y + 10); c.lineTo(x - 20, y + 60); c.moveTo(x, y + 10); c.lineTo(x + 24, y + 54); c.moveTo(x, y - 30); c.lineTo(x - 30, y - 10); c.moveTo(x, y - 30); c.lineTo(x + 30, y - 50); c.stroke();
      pelota(c, x + 60 + Math.sin(t * 4) * 10, y + 54 - Math.abs(Math.sin(t * 4)) * 30, 18, t * 4, "#fff", "#333", 3) }
    if (t > 3.6) texto(c, tipeo("Había una vez un pibe en Fiorito", seg(t, 3.6, 5.2)), 60, 480, "40px Caveat", "#333");
    if (t > 5.4) texto(c, tipeo(`que soñaba con la pelota... (${T.anio})`, seg(t, 5.4, 6.8)), 60, 520, "32px Caveat", "#555");
  } });

ESTILOS.push({ slug: "impasto", nombre: "Óleo con empaste", dur: 8, poster: 7.2,
  que: "Pintura al óleo cargada: cada pincelada tiene grosor, brillo y sombra propia, y el cuadro se va pintando de a poco hasta mostrar la escena.",
  uso: "Para los momentos épicos que merecen un cuadro: Diego levantando la copa, el abrazo del final, el retrato del capitán.",
  draw(c, t, T) {
    c.fillStyle = "#2a2018"; c.fillRect(0, 0, W, H);
    const pin = proc("imp-pin", () => { const g = pix(IMG.brazos, 192, 108), d = g.d.data, out = []; for (let i = 0; i < 5200; i++) { const x = rnd(i) * 192, y = rnd(i + 11) * 108, k = (Math.floor(y) * 192 + Math.floor(x)) * 4; out.push([x * 5, y * 5, d[k], d[k + 1], d[k + 2], rnd(i + 5) * Math.PI, 10 + rnd(i + 2) * 16, rnd(i + 8)]) } return out });
    const k = eio(seg(t, .2, 6.2));
    for (let i = 0; i < pin.length; i++) { const [x, y, r, g, b, a, l, ord] = pin[i]; if (ord > k) continue; c.save(); c.translate(x, y); c.rotate(a);
      c.fillStyle = `rgba(0,0,0,.28)`; c.beginPath(); c.ellipse(1.5, 2, l, 5, 0, 0, TAU); c.fill(); c.fillStyle = `rgb(${r},${g},${b})`; c.beginPath(); c.ellipse(0, 0, l, 5, 0, 0, TAU); c.fill();
      c.fillStyle = "rgba(255,255,255,.18)"; c.beginPath(); c.ellipse(-l * .3, -2, l * .5, 1.4, 0, 0, TAU); c.fill(); c.restore() }
    if (t > 6.6) { const kk = seg(t, 6.6, 7.2); c.globalAlpha = kk; caja(c, 40, H - 74, 420, 48, "rgba(28,20,14,.8)"); texto(c, `«${nombre1(T)}» · óleo, ${T.anio}`, 56, H - 42, "26px 'Special Elite'", "#f0e2c6"); c.globalAlpha = 1 }
    c.strokeStyle = "#7a5a2a"; c.lineWidth = 14; c.strokeRect(7, 7, W - 14, H - 14);
  } });

ESTILOS.push({ slug: "urban-sketch", nombre: "Croquis urbano", dur: 8, poster: 6.6,
  que: "Croquis de viaje con lapicera y acuarela: la línea de tinta dibuja el lugar y las manchas de color entran después, sin pedir permiso a los bordes.",
  uso: "Para los lugares: el DF de 1986, la concentración en el América, la calle de Nápoles, el barrio de Fiorito.",
  draw(c, t, T) {
    c.drawImage(proc("us-pap", () => papel("#f7f3ea", 480, 270, 12)), 0, 0, W, H);
    const tinta = proc("us-tin", () => bordes(IMG.jueguitos, "#2a2a35", 960, 540, 0, 0, 960, 540, .22));
    const lav = (x, y, rx, ry, col, t0) => { const k = eo(seg(t, t0, t0 + 1)); if (k <= 0) return; c.save(); c.globalAlpha = .38 * k; c.fillStyle = col; c.beginPath(); for (let i = 0; i <= 24; i++) { const a = i / 24 * TAU, r = 1 + (rnd(i + x) - .5) * .25; c.lineTo(x + Math.cos(a) * rx * r * k, y + Math.sin(a) * ry * r * k) } c.fill(); c.restore() };
    lav(480, 100, 520, 110, "#7fb3d9", 2.4); lav(470, 440, 420, 120, "#4f86c6", 3.0); lav(470, 290, 140, 220, "#e8b77a", 3.6); lav(200, 300, 220, 120, "#b6c98a", 4.2); lav(780, 300, 200, 120, "#d99a8a", 4.6);
    const kt = eio(seg(t, .2, 2.6)); c.save(); c.beginPath(); c.rect(0, 0, W * kt, H); c.clip(); c.drawImage(tinta, 0, 0, W, H); c.restore();
    if (t > 5.4) { texto(c, `San Paolo, 5/7/${T.anio.slice(-2)}`, 640, 500, "34px Caveat", "#2a2a35"); texto(c, nombre1(T).charAt(0) + nombre1(T).slice(1).toLowerCase() + " hace jueguitos", 640, 530, "26px Caveat", "#555") }
  } });

ESTILOS.push({ slug: "watercolor", nombre: "Acuarela", dur: 8, poster: 6.5,
  que: "Acuarela de pincel: manchas que se expanden y se mezclan con bordes más oscuros donde se secó el agua, granulado del papel y letra a mano.",
  uso: "Para un tono suave y nostálgico: el recuerdo de un hincha, la carta de despedida, el paisaje de México.",
  draw(c, t, T) {
    c.drawImage(proc("wc-pap", () => papel("#fbf8f1", 480, 270, 10)), 0, 0, W, H);
    const mancha = (x, y, r, col, t0, sem) => { const k = eo(seg(t, t0, t0 + 1.4)); if (k <= 0) return; c.save(); for (let capa = 0; capa < 4; capa++) { c.globalAlpha = .12; c.fillStyle = col; c.beginPath(); for (let i = 0; i <= 30; i++) { const a = i / 30 * TAU, rr = r * k * (1 + (rnd(i + capa * 31 + sem) - .5) * .35); c.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr * .7) } c.fill(); c.strokeStyle = col; c.globalAlpha = .18; c.lineWidth = 2; c.stroke() } c.restore() };
    mancha(480, 160, 520, "#f2a65a", .1, 1); mancha(300, 120, 300, "#e45e7a", .5, 2); mancha(700, 140, 280, "#f6d06b", .8, 3); mancha(480, 470, 600, "#5a8fc6", 1.2, 4);
    const k = eo(seg(t, 1.8, 3.4)); if (k > 0) { const sil = proc("wc-sil", () => { const s = lienzo(275, 414), x = s.getContext("2d"); x.drawImage(silueta("#244a7a"), 0, 0); x.globalCompositeOperation = "source-atop"; for (let i = 0; i < 300; i++) { x.fillStyle = `rgba(255,255,255,${rnd(i) * .25})`; x.beginPath(); x.arc(rnd(i + 1) * 275, rnd(i + 2) * 414, 4 + rnd(i + 3) * 10, 0, TAU); x.fill() } return s });
      c.save(); c.globalAlpha = .82 * k; c.drawImage(sil, 400, 520 - 414 * 1.05 * k, 275 * 1.05, 414 * 1.05); c.restore() }
    if (t > 3.8) { texto(c, tipeo(nombre1(T).charAt(0) + nombre1(T).slice(1).toLowerCase() + ", Nápoles", seg(t, 3.8, 5)), 60, 420, "56px Caveat", "#3a3a3a"); }
    if (t > 5.2) texto(c, `verano de ${T.anio}`, 64, 460, "34px Caveat", "#6a6a6a");
  } });
