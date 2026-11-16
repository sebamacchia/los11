// ---------- lote 2: instrumentos y pruebas · montaje y documental ----------

ESTILOS.push({ slug: "archive-lighttable", nombre: "Mesa de luz de archivo", dur: 8, poster: 5.2,
  que: "Negativos sobre una mesa de luz: tiras de película con la imagen invertida, una lupa que pasa y muestra el positivo, marcas de lápiz graso y etiquetas.",
  uso: "Para buscar «la foto» dentro del archivo: el momento exacto de la mano de Dios, la foto del vestuario. Sirve para presentar material inédito.",
  draw(c, t, T) {
    const g = c.createRadialGradient(W / 2, H / 2, 50, W / 2, H / 2, 700); g.addColorStop(0, "#fffef8"); g.addColorStop(1, "#d9d6c8"); c.fillStyle = g; c.fillRect(0, 0, W, H);
    const imgs = [IMG.brazos, IMG.jueguitos, IMG.fotografos, IMG.brazos, IMG.jueguitos];
    const tira = (y, dx, rot, i0) => { c.save(); c.translate(0, y); c.rotate(rot); c.fillStyle = "#3a2410"; c.fillRect(-40 + dx, -70, 1100, 140);
      for (let i = 0; i < 5; i++) { const x = -20 + dx + i * 210; const neg = proc("neg" + ((i0 + i) % 3), () => invertido(imgs[(i0 + i) % 3], 200, 112)); c.drawImage(neg, x, -56, 190, 112);
        c.fillStyle = "#d8b07a"; for (let k = 0; k < 6; k++) { c.fillRect(x + 8 + k * 32, -66, 14, 7); c.fillRect(x + 8 + k * 32, 59, 14, 7) } texto(c, `${(i0 + i) * 2 + 10}A`, x + 4, 66, "10px 'Space Mono'", "#d8b07a") } c.restore() };
    tira(150, -30 + t * 6, -.03, 0); tira(390, -120 - t * 5, .02, 2);
    const lx = lerp(180, 620, eio(seg(t, .5, 4.5))), ly = lerp(150, 380, eio(seg(t, .5, 4.5))), r = 120;
    c.save(); c.beginPath(); c.arc(lx, ly, r, 0, TAU); c.clip(); c.fillStyle = "#111"; c.fillRect(0, 0, W, H); cubrir(c, IMG.fotografos, lx - r * 1.4, ly - r, r * 2.8, r * 2, .5, .3, 1); c.restore();
    c.strokeStyle = "#222"; c.lineWidth = 12; c.beginPath(); c.arc(lx, ly, r + 6, 0, TAU); c.stroke(); c.lineWidth = 22; c.beginPath(); c.moveTo(lx + r * .75, ly + r * .75); c.lineTo(lx + r * 1.4, ly + r * 1.4); c.stroke();
    const kc = seg(t, 4.8, 5.6); if (kc > 0) { c.strokeStyle = "#d42a1f"; c.lineWidth = 5; c.lineCap = "round"; c.beginPath(); c.ellipse(lx, ly, r + 26, r + 20, -.2, 0, kc * TAU); c.stroke(); texto(c, "¡ÉSTA!", lx + r + 30, ly - r + 10, "40px 'Permanent Marker'", "#d42a1f") }
    const ke = seg(t, 5.6, 6.2); if (ke > 0) { c.save(); c.globalAlpha = ke; c.translate(70, 470); c.rotate(-.04); caja(c, 0, 0, 380, 46, "#f6efd4", "#aa9a6a", 1); texto(c, `ARCHIVO · NAPOLI · 5/7/${T.anio} · ROLLO 10`, 14, 30, "14px 'Space Mono'", "#333"); c.restore() }
  } });

ESTILOS.push({ slug: "briefing-board", nombre: "Tablero de decisión", dur: 8, poster: 6.8,
  que: "Un tablero de ingeniería con dos opciones lado a lado, barras que se comparan, notas a mano y una tilde que marca la elegida. Parece una presentación interna.",
  uso: "Para comparar decisiones: Bilardo o Menotti, el 3-5-2 o el 4-4-2, ir o no al Mundial con Maradona lesionado. Ordena los argumentos.",
  draw(c, t, T) {
    c.fillStyle = "#f3f5f7"; c.fillRect(0, 0, W, H); c.strokeStyle = "rgba(30,60,120,.08)"; for (let x = 0; x < W; x += 24) { c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke() } for (let y = 0; y < H; y += 24) { c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke() }
    const A = "#1d4e9e"; texto(c, "DECISIÓN · VERANO " + T.anio, 40, 54, "600 26px 'IBM Plex Sans'", "#111"); texto(c, "¿Dónde juega " + nombre1(T).charAt(0) + nombre1(T).slice(1).toLowerCase() + "?", 40, 84, "18px 'IBM Plex Sans'", "#555");
    const col = (x, tit, sub, vals, t0, gana) => { const k = eo(seg(t, t0, t0 + .6)); c.globalAlpha = k; caja(c, x, 110, 420, 360, "#fff", gana && t > 5.4 ? "#1a9a52" : "#c9d2dc", gana && t > 5.4 ? 3 : 1.5, 6);
      texto(c, tit, x + 20, 150, "700 26px 'IBM Plex Sans'", A); texto(c, sub, x + 20, 174, "14px 'Space Mono'", "#666");
      [["Plata", vals[0]], ["Protagonismo", vals[1]], ["Presión", vals[2]], ["Ciudad", vals[3]]].forEach(([n, v], i) => { const y = 214 + i * 56; texto(c, n, x + 20, y, "15px 'IBM Plex Sans'", "#333"); caja(c, x + 20, y + 10, 380, 14, "#e8edf2"); caja(c, x + 20, y + 10, 380 * v * eo(seg(t, t0 + .5 + i * .2, t0 + 1 + i * .2)), 14, A) }); c.globalAlpha = 1 };
    col(40, "A · F.C. BARCELONA", "SEGUIR EN ESPAÑA", [.6, .45, .7, .6], .4, false); col(500, "B · S.S.C. NAPOLI", T.cifra, [.95, .95, .9, .85], 1.2, true);
    if (t > 5.4) { const k = seg(t, 5.4, 5.9); c.strokeStyle = "#1a9a52"; c.lineWidth = 9; c.lineCap = "round"; trazo(c, [[820, 150], [850, 182], [905, 118]], k) }
    if (t > 6.2) { c.save(); c.translate(70, 505); c.rotate(-.02); texto(c, tipeo("→ firma en julio. Presentación en el San Paolo.", seg(t, 6.2, 7.4)), 0, 0, "26px Caveat", "#c0392b"); c.restore() }
  } });

ESTILOS.push({ slug: "dark-documentary", nombre: "Documental de radar", dur: 8, poster: 6.4,
  que: "Pantalla verde de radar en la oscuridad: el barrido revela la costa de a poco, un punto late en el objetivo y los datos aparecen con calma.",
  uso: "Para historia y ubicación con suspenso: el avión a México, la concentración secreta, la ruta del equipo.",
  draw(c, t, T) {
    c.fillStyle = "#020805"; c.fillRect(0, 0, W, H); const cx = 480, cy = 280, R = 250; const ang = t * 1.4;
    c.save(); c.beginPath(); c.arc(cx, cy, R, 0, TAU); c.clip();
    const P = proyector(13, 41, 2.2);
    dibujarCosta(c, P, "rgba(40,190,110,.16)", "rgba(80,255,150,.55)", 1.3);
    for (let i = 0; i < 24; i++) { const a0 = ang - i * .06; c.save(); c.beginPath(); c.moveTo(cx, cy); c.arc(cx, cy, R, a0 - .065, a0); c.closePath(); c.clip(); c.globalAlpha = Math.pow(1 - i / 24, 2); dibujarCosta(c, P, "rgba(40,190,110,.3)", "rgba(110,255,170,1)", 1.8); c.restore() }
    const g = c.createConicGradient ? c.createConicGradient(ang - .6, cx, cy) : null; if (g) { g.addColorStop(0, "rgba(60,255,140,0)"); g.addColorStop(.095, "rgba(60,255,140,.28)"); g.addColorStop(.1, "rgba(60,255,140,0)"); c.fillStyle = g; c.fillRect(0, 0, W, H) }
    c.restore();
    c.strokeStyle = "rgba(80,255,150,.35)"; c.lineWidth = 1; for (let r = 60; r <= R; r += 63) { c.beginPath(); c.arc(cx, cy, r, 0, TAU); c.stroke() } c.beginPath(); c.moveTo(cx - R, cy); c.lineTo(cx + R, cy); c.moveTo(cx, cy - R); c.lineTo(cx, cy + R); c.stroke();
    const n = P(NAP); const pul = (t * 1.4) % 1; if (t > 2) { c.fillStyle = "#b6ffd2"; c.beginPath(); c.arc(...n, 5, 0, TAU); c.fill(); c.strokeStyle = `rgba(182,255,210,${1 - pul})`; c.beginPath(); c.arc(...n, 6 + pul * 30, 0, TAU); c.stroke(); texto(c, "NÁPOLES", n[0] + 12, n[1] - 8, "14px 'Space Mono'", "#b6ffd2") }
    const L = [`OBJETIVO ....... ${T.nombre.toUpperCase()}`, `LLEGADA ........ 5 JUL ${T.anio}`, `VALOR .......... ${T.cifra}`];
    L.forEach((l, i) => { const k = seg(t, 3.4 + i * .8, 4.2 + i * .8); texto(c, tipeo(l, k), 760, 210 + i * 30, "13px 'Space Mono'", "rgba(140,255,190,.9)", "left") });
    texto(c, "SEÑAL 40.85N 14.27E", 40, 500, "13px 'Space Mono'", "rgba(80,255,150,.7)");
  } });

ESTILOS.push({ slug: "lidar-survey", nombre: "Relevamiento LiDAR", dur: 9, poster: 6.2,
  que: "Una nube de puntos en 3D, como un escaneo láser: el estadio se arma punto por punto, coloreado por altura, mientras la cámara lo rodea y una línea de escaneo lo recorre.",
  uso: "Para los estadios del Mundial: el Azteca, el Cuauhtémoc de Puebla. También sirve para reconstruir un lugar que ya no existe.",
  draw(c, t, T) {
    c.fillStyle = "#04060a"; c.fillRect(0, 0, W, H);
    const pts = proc("lidar-pts", () => { const out = []; for (let i = 0; i < 5200; i++) { const a = rnd(i) * TAU, tier = rnd(i + 7), rx = 300 + tier * 140, ry = 200 + tier * 105; out.push([Math.cos(a) * rx, Math.sin(a) * ry, tier * 70 + rnd(i + 3) * 6, 0]) }
      for (let i = 0; i < 1600; i++) { const x = (rnd(i + 50) - .5) * 420, y = (rnd(i + 90) - .5) * 270; out.push([x, y, 0, 1]) }
      puntosSilueta(900, 3).forEach(([u, v]) => out.push([(u - .5) * 30, 0, (1 - v) * 46, 2])); return out });
    const yaw = .5 + t * .22, pitch = .55; const cs = Math.cos(yaw), sn = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    const scan = seg(t, .3, 5) * 2 - 1; const k = eo(seg(t, .2, 4.5));
    const col = (h, tipo) => tipo === 2 ? "#ffffff" : tipo === 1 ? "#2fbf71" : `hsl(${200 - h * 2.4},90%,${50 + h * .2}%)`;
    for (let i = 0; i < pts.length; i++) { const [x, y, z, tipo] = pts[i]; if (rnd(i * .3) > k) continue;
      const X = x * cs - y * sn, Y = x * sn + y * cs; const sy = Y * cp - z * sp * 2.2, d = 1 + (Y * sp) / 900; const px = W / 2 + X * .78 / d, py = 300 + sy * .78 / d;
      c.fillStyle = col(z, tipo); c.globalAlpha = tipo === 2 ? .95 : .7; c.fillRect(px, py, tipo === 2 ? 2 : 1.6, tipo === 2 ? 2 : 1.6) }
    c.globalAlpha = 1; const ly = 300 + scan * 230; c.fillStyle = "rgba(120,220,255,.12)"; c.fillRect(0, ly - 2, W, 4);
    texto(c, "RELEVAMIENTO · STADIO SAN PAOLO", 30, 40, "14px 'Space Mono'", "#9fdcff"); texto(c, `PUNTOS: ${miles(pts.length * k)}`, 30, 62, "13px 'Space Mono'", "#5f8fb0");
    if (t > 5.4) { const kk = seg(t, 5.4, 6.2); c.globalAlpha = kk; texto(c, "≈ 70.000 PERSONAS EN LA PRESENTACIÓN", W - 30, H - 56, "16px 'Space Mono'", "#fff", "right"); texto(c, `${T.nombre.toUpperCase()} · 5/7/${T.anio}`, W - 30, H - 32, "13px 'Space Mono'", "#9fdcff", "right"); c.globalAlpha = 1 }
  } });

ESTILOS.push({ slug: "microscope", nombre: "Bajo el microscopio", dur: 8, poster: 3.2,
  que: "Campo circular de microscopio que acerca de a poco: la foto del diario se vuelve puntos de trama, con el aumento, la retícula y la regla de escala.",
  uso: "Para mirar un detalle de cerca: un recorte de diario, la firma del contrato, el pie de Diego en la mano de Dios.",
  draw(c, t, T) {
    c.fillStyle = "#050505"; c.fillRect(0, 0, W, H); const cx = W / 2, cy = H / 2, R = 245;
    const z = Math.exp(lerp(0, Math.log(14), eio(seg(t, .8, 6.5)))); const fx = 480, fy = 175; // la cara en la foto
    c.save(); c.beginPath(); c.arc(cx, cy, R, 0, TAU); c.clip(); c.fillStyle = "#f0ece2"; c.fillRect(0, 0, W, H);
    if (z < 5) { const s = 1.1 * z; c.globalAlpha = 1 - seg(z, 3, 5); c.drawImage(IMG.fotografos, cx - fx * s, cy - fy * s, 960 * s, 562 * s); c.globalAlpha = 1 }
    if (z > 3) { const tr = proc("micro-tr", () => tramado(IMG.fotografos, "#1b1b2e", 1200, 1200, 380, 80, 200, 200, 9)); const s = 1.1 * z * 200 / 1200; c.globalAlpha = seg(z, 3, 5); c.globalCompositeOperation = "multiply";
      c.drawImage(tr, cx - (fx - 380) * 1.1 * z, cy - (fy - 80) * 1.1 * z, 1200 * s, 1200 * s); c.globalCompositeOperation = "source-over"; c.globalAlpha = 1 }
    const foco = Math.abs(Math.sin(t * 1.3)) * .25; c.fillStyle = `rgba(240,236,226,${foco * .3})`; c.fillRect(0, 0, W, H);
    const v = c.createRadialGradient(cx, cy, R * .6, cx, cy, R); v.addColorStop(0, "rgba(0,0,0,0)"); v.addColorStop(1, "rgba(0,0,0,.7)"); c.fillStyle = v; c.fillRect(0, 0, W, H); c.restore();
    c.strokeStyle = "rgba(255,255,255,.35)"; c.lineWidth = 1; c.beginPath(); c.moveTo(cx - R, cy); c.lineTo(cx + R, cy); c.moveTo(cx, cy - R); c.lineTo(cx, cy + R); c.stroke(); for (let i = -5; i <= 5; i++) { c.beginPath(); c.moveTo(cx + i * 20, cy - 5); c.lineTo(cx + i * 20, cy + 5); c.stroke() }
    texto(c, `×${Math.round(z * 10)}`, 60, 70, "40px 'Space Mono'", "#e8e2d0"); texto(c, "MUESTRA: DIARIO", 60, 100, "13px 'Space Mono'", "#9a9486"); texto(c, `NÁPOLES, 6 JUL ${T.anio}`, 60, 120, "13px 'Space Mono'", "#9a9486");
    const bar = 80; c.fillStyle = "#e8e2d0"; c.fillRect(W - 160, H - 70, bar, 4); texto(c, z > 5 ? "1 mm" : "1 cm", W - 160, H - 80, "13px 'Space Mono'", "#e8e2d0");
    if (t > 6.6) texto(c, "LA FOTO ERA TINTA: PUNTOS DE TRAMA", W / 2, H - 20, "14px 'Space Mono'", "#e8e2d0", "center");
  } });

ESTILOS.push({ slug: "security-xray", nombre: "Rayos X de seguridad", dur: 8, poster: 5.4,
  que: "Escáner de aeropuerto: el bolso avanza por la cinta y los rayos X muestran el contenido en naranja, azul y verde, con recuadros que marcan cada objeto.",
  uso: "Para el humor y los objetos: «qué llevaba Diego en el bolso a México», la valija de la AFA. Va bien para el lado B.",
  draw(c, t, T) {
    c.fillStyle = "#0c1622"; c.fillRect(0, 0, W, H);
    const bx = lerp(-520, 240, eo(seg(t, 0, 2.6))), by = 120, bw = 480, bh = 300;
    c.save(); c.globalCompositeOperation = "lighter";
    caja(c, bx, by, bw, bh, "rgba(60,120,255,.18)", "rgba(120,180,255,.6)", 2, 18); caja(c, bx + bw / 2 - 60, by - 40, 120, 50, null, "rgba(120,180,255,.6)", 6, 20);
    const nar = "rgba(255,150,40,.55)", az = "rgba(70,140,255,.75)", ve = "rgba(60,220,140,.6)";
    c.fillStyle = nar; c.beginPath(); c.arc(bx + 110, by + 170, 70, 0, TAU); c.fill(); c.strokeStyle = "rgba(255,190,90,.8)"; c.lineWidth = 2; c.stroke();
    for (let i = 0; i < 2; i++) { c.fillStyle = nar; c.beginPath(); c.ellipse(bx + 250 + i * 90, by + 220, 40, 22, .2, 0, TAU); c.fill(); c.fillStyle = az; for (let k = 0; k < 6; k++) c.fillRect(bx + 222 + i * 90 + (k % 3) * 18, by + 236 + Math.floor(k / 3) * 8, 6, 6) }
    c.fillStyle = ve; c.fillRect(bx + 230, by + 60, 200, 90); c.fillStyle = "rgba(60,220,140,.35)"; for (let k = 0; k < 5; k++) c.fillRect(bx + 236 + k * 4, by + 66 + k * 4, 188, 78);
    c.fillStyle = az; c.font = "70px Anton"; c.fillText("10", bx + 60, by + 90); c.restore();
    const tags = [[bx + 40, by + 100, 140, 140, "PELOTA", 2.8], [bx + 205, by + 190, 180, 70, "BOTINES ×2", 3.4], [bx + 225, by + 55, 210, 100, T.cifra, 4.0]];
    tags.forEach(([x, y, w, h, s, t0]) => { const k = seg(t, t0, t0 + .3); if (k <= 0) return; c.strokeStyle = "#ff3b3b"; c.lineWidth = 2; c.globalAlpha = k; c.strokeRect(x, y, w, h); caja(c, x, y - 22, Math.max(80, s.length * 10 + 14), 22, "#ff3b3b"); texto(c, s, x + 6, y - 6, "14px 'Space Mono'", "#fff"); c.globalAlpha = 1 });
    c.fillStyle = "#1f2b38"; c.fillRect(0, 440, W, 26); for (let x = -((t * 120) % 40); x < W; x += 40) { c.fillStyle = "#2a3a4c"; c.fillRect(x, 440, 20, 26) }
    caja(c, 0, 0, W, 44, "#08101a"); texto(c, `EQUIPAJE · ${T.nombre.toUpperCase()} · VUELO BCN→NAP · ${T.anio}`, 20, 29, "15px 'Space Mono'", "#9fd3ff");
    if (t > 5.2) { const k = Math.floor(t * 3) % 2; caja(c, W - 260, 60, 230, 40, k ? "#ff3b3b" : "#7a1d1d"); texto(c, "REVISIÓN MANUAL", W - 145, 87, "18px 'Space Mono'", "#fff", "center") }
  } });

ESTILOS.push({ slug: "thermal-camera", nombre: "Cámara térmica", dur: 8, poster: 6,
  que: "La imagen con la paleta de una cámara térmica (negro, violeta, rojo, amarillo y blanco), una mira con la temperatura y el máximo que sube.",
  uso: "Para medir la temperatura emocional: la tribuna antes de Inglaterra, el banco en la final. Literal y en sentido figurado.",
  draw(c, t, T) {
    const im = proc("termo", () => mapaColor(IMG.fotografos, PALETA_HIERRO, 960, 562, 0, 0, 960, 562));
    cubrir(c, im, 0, 0, W, H, .5, .35, 1.02 + t * .01);
    const fx = lerp(300, 480, eio(seg(t, .5, 3))), fy = lerp(300, 200, eio(seg(t, .5, 3)));
    c.strokeStyle = "#fff"; c.lineWidth = 2; c.beginPath(); c.moveTo(fx - 30, fy); c.lineTo(fx - 8, fy); c.moveTo(fx + 8, fy); c.lineTo(fx + 30, fy); c.moveTo(fx, fy - 30); c.lineTo(fx, fy - 8); c.moveTo(fx, fy + 8); c.lineTo(fx, fy + 30); c.stroke();
    const temp = lerp(34.2, 39.9, eio(seg(t, 1, 6))); texto(c, temp.toFixed(1) + "°C", fx + 36, fy - 10, "24px 'Space Mono'", "#fff");
    const g = c.createLinearGradient(0, 80, 0, 440); PALETA_HIERRO.slice().reverse().forEach((col, i) => g.addColorStop(i / (PALETA_HIERRO.length - 1), col)); c.fillStyle = g; c.fillRect(W - 40, 80, 16, 360);
    texto(c, "40.0", W - 48, 92, "13px 'Space Mono'", "#fff", "right"); texto(c, "20.0", W - 48, 444, "13px 'Space Mono'", "#fff", "right");
    caja(c, 20, 20, 300, 64, "rgba(0,0,0,.55)"); texto(c, `MÁX ${temp.toFixed(1)}°C`, 34, 50, "22px 'Space Mono'", "#fbd03c"); texto(c, `SAN PAOLO · 5/7/${T.anio}`, 34, 72, "13px 'Space Mono'", "#ddd");
    if (t > 6) { caja(c, 20, H - 70, 520, 46, "rgba(0,0,0,.6)"); texto(c, "NÁPOLES HIERVE: " + apellido(T), 34, H - 38, "26px 'Bebas Neue'", "#fff") }
  } });

ESTILOS.push({ slug: "caption-news", nombre: "Noticia con subtítulos", dur: 8, poster: 4.6,
  que: "Noticia para redes: subtítulos grandes que aparecen palabra por palabra sobre la imagen, la palabra clave resaltada en amarillo y una barra de progreso.",
  uso: "Para shorts y reels del canal: un dato por video, la anécdota en 30 segundos.",
  draw(c, t, T) {
    cubrir(c, IMG.jueguitos, 0, 0, W, H, .5, .5, 1.08 + t * .02); c.fillStyle = "rgba(0,0,0,.35)"; c.fillRect(0, 0, W, H);
    const frase = `${T.anio}: ${nombre1(T)} llega al Napoli por ${T.cifra}. El pase más caro de la historia.`.split(" ");
    const clave = new Set([nombre1(T), T.cifra.split(" ").pop() + ".", "caro"]);
    const porPal = 7 / frase.length; const n = Math.min(frase.length, Math.floor(t / porPal) + 1); const desde = Math.max(0, n - 6);
    let x = 80, y = 330; c.font = "700 50px 'IBM Plex Sans'"; c.textBaseline = "alphabetic";
    const lineasP = []; let fila = []; let ancho = 0;
    for (let i = desde; i < n; i++) { const w = c.measureText(frase[i] + " ").width; if (ancho + w > 800 && fila.length) { lineasP.push(fila); fila = []; ancho = 0 } fila.push(i); ancho += w } if (fila.length) lineasP.push(fila);
    lineasP.forEach((f, li) => { x = 80; f.forEach(i => { const p = frase[i], w = c.measureText(p).width; const nuevo = i === n - 1; const k = nuevo ? eb(seg((t - (n - 1) * porPal), 0, .18)) : 1; const esClave = [...clave].some(cv => p.toUpperCase().startsWith(cv.toUpperCase()));
      if (esClave) caja(c, x - 8, y + li * 64 - 46, w + 16, 60, "#ffd400", null, 0, 6);
      c.save(); c.translate(x + w / 2, y + li * 64); c.scale(k, k); c.lineWidth = 8; c.strokeStyle = "#000"; c.lineJoin = "round"; c.textAlign = "center"; if (!esClave) c.strokeText(p, 0, 0); c.fillStyle = esClave ? "#000" : "#fff"; c.fillText(p, 0, 0); c.restore(); x += c.measureText(p + " ").width }) });
    caja(c, 0, H - 8, W * t / 8, 8, "#ffd400"); caja(c, 30, 30, 132, 34, "#e3261d", null, 0, 6); texto(c, "LOS 11", 96, 54, "700 18px 'IBM Plex Sans'", "#fff", "center");
  } });

ESTILOS.push({ slug: "city-symphony", nombre: "Sinfonía de ciudad", dur: 8, poster: 6.4,
  que: "Montaje de ciudad cortado como música minimalista: los cortes se aceleran con el compás, un momento casi se detiene y termina con un corte seco a negro. Casi sin palabras.",
  uso: "Para retratar una ciudad o un ambiente: México 86, Nápoles enloquecida, Buenos Aires el día de la final. Sin narrador.",
  draw(c, t, T) {
    c.fillStyle = "#000"; c.fillRect(0, 0, W, H); if (t > 7.4) return;
    const planos = [[IMG.jueguitos, .2, .4], [IMG.fotografos, .7, .2], [IMG.brazos, .3, .3], [IMG.jueguitos, .8, .6], [IMG.fotografos, .2, .6], [IMG.brazos, .7, .5]];
    const cortes = [0, .9, 1.7, 2.4, 3.0, 3.5, 3.9, 4.25, 4.55, 4.8]; let i = cortes.findIndex((x, k) => t >= x && t < (cortes[k + 1] ?? 9)); if (i < 0) i = cortes.length - 1;
    const lento = i === cortes.length - 1; const loc = t - cortes[i];
    const [img, fx, fy] = planos[i % planos.length]; const z = lento ? 1.15 + loc * .02 : 1.1 + loc * .25;
    const g = proc("cs-" + (i % 3), () => { const im = [IMG.jueguitos, IMG.fotografos, IMG.brazos][i % 3]; const p = pix(im, 960, Math.round(im.height * 960 / im.width)), d = p.d.data; for (let k = 0; k < d.length; k += 4) { d[k] = Math.min(255, d[k] * 1.05 + 8); d[k + 2] = d[k + 2] * .9; const l = (d[k] + d[k + 1] + d[k + 2]) / 3; for (let j = 0; j < 3; j++) d[k + j] = l + (d[k + j] - l) * .8 } p.x.putImageData(p.d, 0, 0); return p.c });
    cubrir(c, g, 0, 0, W, H, fx, fy, z); c.fillStyle = "#000"; c.fillRect(0, 0, W, 22); c.fillRect(0, H - 22, W, 22);
    c.save(); c.globalAlpha = .35; c.drawImage(granoDe(Math.floor(t * 24)), 0, 0, W, H); c.restore();
    if (t < .9) { c.fillStyle = "#ede8df"; c.font = "34px Michroma"; c.fillText("N Á P O L E S", 170, 300); }
    if (lento) { const k = seg(t, 5, 5.8); c.globalAlpha = k; c.fillStyle = "#ede8df"; c.font = "54px Michroma"; c.fillText("1.212.387", 170, 300); c.fillStyle = "#D9772F"; c.fillRect(172, 318, 180, 3); c.font = "13px Michroma"; c.fillStyle = "#b0aaa0"; c.fillText("HABITANTES · CENSO DE 1981", 172, 346); c.fillText(`Y UNO MÁS · JULIO DE ${T.anio}`, 172, 370); c.globalAlpha = 1 }
  } });

ESTILOS.push({ slug: "countdown", nombre: "Cuenta regresiva en pantalla partida", dur: 8, poster: 5.2,
  que: "Pantalla partida en vivo: de un lado una ciudad y del otro la otra, con un reloj central que cuenta hacia atrás hasta el momento clave y datos que corren.",
  uso: "Para la tensión antes de un hecho: el pitazo inicial de la final, el penal, el anuncio de la lista. Muy de transmisión en vivo.",
  draw(c, t, T) {
    const restan = Math.max(0, 5.6 - t);
    caja(c, 0, 0, W / 2, H, "#7a1235"); caja(c, W / 2, 0, W / 2, H, "#0d5fb0");
    c.save(); c.beginPath(); c.rect(0, 0, W / 2, H); c.clip(); c.globalAlpha = .35; cubrir(c, proc("cd-g1", () => gris(IMG.fotografos, 1.2)), 0, 0, W / 2, H, .2, .4, 1.2); c.restore();
    c.save(); c.beginPath(); c.rect(W / 2, 0, W / 2, H); c.clip(); c.globalAlpha = .45; cubrir(c, proc("cd-g2", () => gris(IMG.jueguitos, 1.2)), W / 2, 0, W / 2, H, .55, .5, 1.1); c.restore();
    texto(c, "BARCELONA", 40, 60, "34px 'Bebas Neue'", "#fff"); texto(c, "41.39N 2.17E", 40, 84, "13px 'Space Mono'", "#f5c6d6");
    texto(c, "NÁPOLES", W - 40, 60, "34px 'Bebas Neue'", "#fff", "right"); texto(c, "40.85N 14.27E", W - 40, 84, "13px 'Space Mono'", "#c6dcf5", "right");
    caja(c, W / 2 - 170, H / 2 - 70, 340, 140, "#0b0b0b", "#fff", 2, 8);
    if (restan > 0) { const s = Math.ceil(restan); texto(c, "FIRMA EN", W / 2, H / 2 - 30, "16px 'Space Mono'", "#aaa", "center"); texto(c, `T-00:00:0${s}`, W / 2, H / 2 + 34, "48px 'Space Mono'", "#fff", "center") }
    else { const k = Math.floor(t * 4) % 2; texto(c, "OFICIAL", W / 2, H / 2 + 20, "64px 'Bebas Neue'", k ? "#ffd400" : "#fff", "center") }
    caja(c, 0, H - 40, W, 40, "rgba(0,0,0,.7)"); const cinta = `EN VIVO · ${T.nombre.toUpperCase()} · ${T.cifra} · ${T.anio} · `; c.font = "18px 'Space Mono'"; const cw = c.measureText(cinta).width; for (let x = -(t * 90) % cw; x < W; x += cw) texto(c, cinta, x, H - 14, "18px 'Space Mono'", "#fff");
    if (Math.floor(t * 2) % 2) { c.fillStyle = "#ff2a2a"; c.beginPath(); c.arc(W / 2 - 140, 40, 7, 0, TAU); c.fill() } texto(c, "EN VIVO", W / 2 - 126, 46, "15px 'Space Mono'", "#fff");
  } });

ESTILOS.push({ slug: "visual-investigation", nombre: "Investigación visual", dur: 8, poster: 6.2, video: false,
  que: "Análisis forense del cuadro: recuadros con números sobre cada jugador, código de tiempo, distancias medidas, ampliaciones y una línea de tiempo con fotogramas.",
  uso: "Para reconstruir jugadas polémicas: ¿la mano de Dios se veía desde el árbitro?, la posición en el gol del siglo. Es la forma más seria de mostrar una jugada.",
  draw(c, t, T) {
    c.fillStyle = "#0b0d10"; c.fillRect(0, 0, W, H); const ix = 20, iy = 50, iw = 600, ih = 338;
    c.drawImage(IMG.freeze, ix, iy, iw, ih); c.fillStyle = "rgba(0,0,0,.2)"; c.fillRect(ix, iy, iw, ih);
    const s = iw / 960; const caj = [[700, 300, 120, 140, "J1"], [460, 240, 90, 120, "J2"], [380, 230, 90, 100, "J3"], [830, 260, 80, 140, "J4"]];
    caj.forEach(([x, y, w, h, n], i) => { const k = seg(t, .5 + i * .35, .8 + i * .35); if (k <= 0) return; c.strokeStyle = i === 0 ? "#ffcc00" : "#3fd0ff"; c.lineWidth = 2; c.globalAlpha = k; c.strokeRect(ix + x * s, iy + y * s, w * s, h * s); caja(c, ix + x * s, iy + y * s - 16, 28, 16, i === 0 ? "#ffcc00" : "#3fd0ff"); texto(c, n, ix + x * s + 4, iy + y * s - 4, "12px 'Space Mono'", "#000"); c.globalAlpha = 1 });
    const km = seg(t, 2.2, 3); if (km > 0) { c.strokeStyle = "#ff5a5a"; c.setLineDash([5, 4]); c.lineWidth = 2; const a = [ix + 760 * s, iy + 440 * s], b = [ix + 505 * s, iy + 360 * s]; trazo(c, [a, b], km); c.setLineDash([]); if (km >= 1) texto(c, "J1 → J2", (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 8, "14px 'Space Mono'", "#ff5a5a", "center") }
    const kz = eo(seg(t, 3.2, 3.8)); if (kz > 0) { c.globalAlpha = kz; caja(c, 640, 50, 300, 200, "#000", "#ffcc00", 2); c.save(); c.beginPath(); c.rect(642, 52, 296, 196); c.clip(); c.drawImage(IMG.freeze, 680, 280, 180, 140, 642, 52, 296, 196 * 1.15); c.restore(); texto(c, "AMPLIACIÓN ×4 · J1", 648, 270, "13px 'Space Mono'", "#ffcc00"); c.globalAlpha = 1 }
    texto(c, "ARG–ING · 22/6/1986 · TC 00:51:36:12", 20, 32, "14px 'Space Mono'", "#cfd8e3");
    const ky = 410; caja(c, 20, ky, 920, 110, "#14181e", "#2a313b", 1); for (let i = 0; i < 8; i++) { const x = 30 + i * 112; c.drawImage(IMG.freeze, 100 + i * 60, 60, 600, 338, x, ky + 12, 104, 58); c.globalAlpha = .5; c.fillStyle = "#000"; c.fillRect(x, ky + 12, 104, 58); c.globalAlpha = 1 }
    const ph = 30 + ((t / 8) * 900); c.fillStyle = "#ff5a5a"; c.fillRect(ph, ky + 6, 2, 98); texto(c, `FOTOGRAMA ${Math.floor(t * 25)}`, 30, ky + 96, "12px 'Space Mono'", "#9aa6b5");
    if (t > 5) { const k = seg(t, 5, 5.6); c.globalAlpha = k; texto(c, "CONCLUSIÓN:", 650, 320, "13px 'Space Mono'", "#9aa6b5"); texto(c, "J1 junto a la pelota;", 650, 345, "16px 'IBM Plex Sans'", "#fff"); texto(c, "J2 y J3 pican al área.", 650, 368, "16px 'IBM Plex Sans'", "#fff"); c.globalAlpha = 1 }
  } });
