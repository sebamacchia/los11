// ---------- lote 1: gráfica y tipografía · película y cinta ----------

ESTILOS.push({ slug: "art-deco", nombre: "Art déco", dur: 8, poster: 6.5,
  que: "Negro y oro: rayos de sol que giran, marcos escalonados que se dibujan, letras de los años 20 y el año en números romanos.",
  uso: "Para una apertura solemne o una placa de homenaje: la final del Azteca, la entrega de la copa, el cierre del video.",
  draw(c, t, T) {
    c.fillStyle = "#0b0a08"; c.fillRect(0, 0, W, H);
    const oro = c.createLinearGradient(0, 0, 0, H); oro.addColorStop(0, "#f7e7a1"); oro.addColorStop(.5, "#c99a2e"); oro.addColorStop(1, "#8a6414");
    c.save(); c.translate(W / 2, 300); c.rotate(t * .04); c.globalAlpha = .55 * eo(seg(t, 0, 1));
    for (let i = 0; i < 36; i++) { c.rotate(TAU / 36); c.fillStyle = i % 2 ? "#1d1810" : "#2a2214"; c.beginPath(); c.moveTo(0, 0); c.lineTo(-30, -700); c.lineTo(30, -700); c.fill() } c.restore();
    const k = eio(seg(t, .3, 2.2));
    c.strokeStyle = oro; c.lineWidth = 2;
    const marco = (m) => { const pts = [[m, 60 + m], [W / 2 - 120, 60 + m], [W / 2 - 100, 40 + m], [W / 2 + 100, 40 + m], [W / 2 + 120, 60 + m], [W - m, 60 + m], [W - m, H - 40 - m], [m, H - 40 - m], [m, 60 + m]]; trazo(c, pts, k) };
    marco(30); marco(42);
    const kf = eo(seg(t, 1.2, 2.4));
    if (kf > 0) { c.save(); c.globalAlpha = kf; c.beginPath(); c.moveTo(W / 2 - 110, 420); c.lineTo(W / 2 - 110, 190); c.arc(W / 2, 190, 110, Math.PI, 0); c.lineTo(W / 2 + 110, 420); c.closePath(); c.save(); c.clip();
      c.drawImage(proc("deco-foto", () => duotono(IMG.brazos, "#0b0a08", "#f2d98a", 440, 248, 0, 0, 960, 540)), W / 2 - 290, 140, 480, 290); c.restore(); c.strokeStyle = oro; c.lineWidth = 4; c.stroke(); c.restore() }
    const kt = eo(seg(t, 2.6, 3.4));
    if (kt > 0) { c.save(); c.globalAlpha = kt; c.fillStyle = oro; c.font = `${tam(c, apellido(T), "Limelight", 82, 760)}px Limelight`; c.textAlign = "center"; c.fillText(apellido(T), W / 2, 492 - (1 - kt) * 12);
      c.font = "22px Cinzel"; c.fillText(`· ${romano(T.anio)} ·`, W / 2, 128); c.restore() }
    const kc = seg(t, 4.2, 5.0); if (kc > 0) { c.save(); c.globalAlpha = kc; c.fillStyle = "#f2d98a"; c.font = "18px Cinzel"; c.textAlign = "center"; c.fillText(`S.S.C. NAPOLI  ◆  ${T.cifra}  ◆  STADIO SAN PAOLO`, W / 2, 524 - 22); c.restore() }
    const sh = (t * .5) % 2 - .5; const g = c.createLinearGradient((sh - .1) * W, 0, (sh + .1) * W, H); g.addColorStop(0, "rgba(255,240,190,0)"); g.addColorStop(.5, "rgba(255,240,190,.12)"); g.addColorStop(1, "rgba(255,240,190,0)"); c.fillStyle = g; c.fillRect(0, 0, W, H);
  } });

ESTILOS.push({ slug: "bauhaus-shapes", nombre: "Formas Bauhaus", dur: 8, poster: 6.4,
  que: "Círculo, cuadrado y triángulo en rojo, azul y amarillo explican la idea: la pelota rueda, los bloques se apilan y la cifra se arma con geometría.",
  uso: "Para explicar conceptos y números sin fotos: cuánto valía un pase, cómo jugaba el 3-5-2 de Bilardo. También sirve para placas de capítulo.",
  draw(c, t, T) {
    c.fillStyle = "#efe8d8"; c.fillRect(0, 0, W, H);
    const R = "#d6382c", A = "#1f4aa8", Y = "#f0bd1d", N = "#1a1a1a";
    const k1 = eo(seg(t, .2, 1.4)); const bx = lerp(-80, 250, k1); c.fillStyle = R; c.beginPath(); c.arc(bx, 300, 120, 0, TAU); c.fill();
    c.fillStyle = "#efe8d8"; c.save(); c.translate(bx, 300); c.rotate(k1 * 6); c.fillRect(-4, -120, 8, 240); c.restore();
    const k2 = eb(seg(t, 1.2, 1.8)); c.fillStyle = A; c.fillRect(420, 420 - 300 * k2, 160, 300 * k2);
    const k3 = eo(seg(t, 1.8, 2.6)); poligono(c, [[600, 420], [600 + 300 * k3, 420], [600, 420 - 260 * k3]], Y);
    c.fillStyle = N; c.fillRect(60, 430, 840 * eio(seg(t, .6, 2.4)), 10);
    const n = cifraNum(T.cifra); const v = n.n * eo(seg(t, 3.0, 4.4));
    const kt = seg(t, 2.8, 3.2);
    if (kt > 0) { c.globalAlpha = kt; texto(c, miles(v), 60, 510, `${tam(c, miles(n.n), "'Rubik Mono One'", 54, 700)}px 'Rubik Mono One'`, N); texto(c, n.pre, 60, 470, "18px 'Space Mono'", R); c.globalAlpha = 1 }
    const k4 = seg(t, 4.8, 5.4); if (k4 > 0) { c.globalAlpha = k4; texto(c, "1", 480, 400, "120px 'Rubik Mono One'", "#efe8d8", "center"); texto(c, "JUGADOR", 680, 120, "40px 'Rubik Mono One'", N); texto(c, T.anio, 680, 168, "40px 'Rubik Mono One'", R); texto(c, "BARCELONA → NAPOLI", 682, 196, "15px 'Space Mono'", N); c.globalAlpha = 1 }
    c.save(); c.globalAlpha = .25; c.globalCompositeOperation = "multiply"; c.drawImage(granoDe(3), 0, 0, W, H); c.restore();
  } });

ESTILOS.push({ slug: "flat-space-explainer", nombre: "Zoom de escala", dur: 9, poster: 5.4,
  que: "Un alejamiento continuo que cambia de escala: de la cara al estadio, del estadio a la ciudad y de la ciudad al Mediterráneo, con la regla de escala siempre a la vista.",
  uso: "Para ubicar al espectador: dónde queda Nápoles, qué tan lejos estaba México, el tamaño del Azteca.",
  draw(c, t, T) {
    const k = eio(seg(t, .6, 8.2)); const L = lerp(0, Math.log(400000), k); const z = Math.exp(-L);
    c.fillStyle = "#123047"; c.fillRect(0, 0, W, H);
    const mpp = .0025 / z; // metros por pixel
    const kmpp = mpp / 1000;
    if (mpp > 40) { const P = ([lo, la]) => [W / 2 + (lo - NAP[0]) * 111000 * .755 / mpp, H / 2 + (NAP[1] - la) * 111000 / mpp]; dibujarCosta(c, P, "#f2c14e", "#123047", 2) }
    else { c.fillStyle = "#f2c14e"; c.fillRect(0, 0, W, H) }
    const est = 250 / mpp; // el estadio mide ~250 m
    if (est > 6) { c.save(); c.globalAlpha = cl((est - 6) / 20); c.fillStyle = "#e4572e"; c.beginPath(); c.ellipse(W / 2, H / 2, est / 2, est * .38, 0, 0, TAU); c.fill();
      c.fillStyle = "#4caf6d"; c.fillRect(W / 2 - est * .21, H / 2 - est * .14, est * .42, est * .28); if (est > 120) { c.globalAlpha = 1; cancha(c, W / 2 - est * .21, H / 2 - est * .14, est * .42, est * .28, "#fff", Math.max(1, est / 400)) } c.restore() }
    const persona = 1.8 / mpp;
    if (persona > 3) { c.save(); c.globalAlpha = cl((persona - 3) / 30); const s = persona / 414 * 1.15; c.translate(W / 2, H / 2); c.scale(s, s); c.drawImage(IMG.rec, -137, -230); c.restore() }
    const opciones = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000];
    let m = opciones[0]; for (const o of opciones) if (o / mpp < 220) m = o;
    const px = m / mpp; c.fillStyle = "#fff"; c.fillRect(40, 490, px, 6); c.fillRect(40, 482, 3, 22); c.fillRect(40 + px - 3, 482, 3, 22);
    texto(c, m >= 1000 ? `${m / 1000} km` : `${m} m`, 40, 474, "20px 'IBM Plex Sans'", "#fff");
    const etapa = mpp < 1 ? "DIEGO · 1,65 m" : mpp < 40 ? "STADIO SAN PAOLO" : mpp < 500 ? "NÁPOLES" : "EL MEDITERRÁNEO";
    caja(c, 40, 30, 330, 48, "rgba(18,48,71,.85)"); texto(c, etapa, 56, 63, "26px 'Bebas Neue'", "#f2c14e");
    texto(c, `${T.nombre.toUpperCase()} · ${T.anio}`, 920, 512, "14px 'Space Mono'", "#fff", "right");
  } });

ESTILOS.push({ slug: "pictogram-motion", nombre: "Pictogramas en movimiento", dur: 8, poster: 6.6,
  que: "Pictogramas de señalética, como los de los Juegos Olímpicos, que cobran vida: el jugador patea, el avión vuela y la bolsa de plata cae sobre baldosas de color.",
  uso: "Para resúmenes y separadores: «24 equipos, 52 partidos, 1 campeón». También para explicar reglas o el formato del Mundial.",
  draw(c, t, T) {
    const cols = ["#0e7c66", "#e8a33d", "#2d5fa8", "#d6452f"]; const tile = 480 / 2;
    for (let i = 0; i < 4; i++) { c.fillStyle = cols[i]; c.fillRect((i % 2) * W / 2, Math.floor(i / 2) * H / 2, W / 2, H / 2) }
    const blanco = "#fff"; c.fillStyle = blanco; c.strokeStyle = blanco; c.lineCap = "round"; c.lineWidth = 22;
    { const ox = 240, oy = 140, a = Math.sin(t * 5) * .6; c.beginPath(); c.arc(ox - 10, oy - 70, 22, 0, TAU); c.fill(); c.beginPath(); c.moveTo(ox - 10, oy - 40); c.lineTo(ox, oy + 20); c.stroke();
      c.beginPath(); c.moveTo(ox, oy + 20); c.lineTo(ox - 40, oy + 80); c.stroke(); c.beginPath(); c.moveTo(ox, oy + 20); c.lineTo(ox + 40 + Math.max(0, a) * 30, oy + 70 - Math.max(0, a) * 40); c.stroke();
      c.beginPath(); c.moveTo(ox - 8, oy - 25); c.lineTo(ox - 60, oy); c.moveTo(ox - 8, oy - 25); c.lineTo(ox + 50, oy - 10); c.stroke();
      const bx = ox + 90 + ((t * 1.2) % 1) * 110; c.beginPath(); c.arc(bx, oy + 80, 16, 0, TAU); c.fill() }
    { const k = (t * .35) % 1, x = 520 + k * 380, y = 150 - Math.sin(k * Math.PI) * 50; c.save(); c.translate(x, y); c.rotate(-.15 + k * .3); c.lineWidth = 0;
      poligono(c, [[-60, -8], [50, -8], [70, 0], [50, 8], [-60, 8]], blanco); poligono(c, [[-10, -6], [20, -6], [-20, -60], [-35, -60]], blanco); poligono(c, [[-10, 6], [20, 6], [-20, 60], [-35, 60]], blanco); poligono(c, [[-60, -6], [-45, -6], [-62, -28], [-70, -28]], blanco); c.restore() }
    { const k = eb(seg(t, 1, 1.6)); escala(c, 240, 400, k, () => { c.beginPath(); c.arc(0, 10, 70, 0, TAU); c.fill(); poligono(c, [[-26, -56], [26, -56], [12, -80], [-12, -80]], blanco); texto(c, "$", 0, 40, "88px 'IBM Plex Sans'", cols[2], "center") }) }
    { const k = eo(seg(t, 2, 2.8)); if (k > 0) { c.globalAlpha = k; texto(c, T.cifra, 720, 400, `${tam(c, T.cifra, "'IBM Plex Sans'", 52, 420, 700)}px 'IBM Plex Sans'`, blanco, "center"); texto(c, `BARCELONA → NAPOLI · ${T.anio}`, 720, 440, "16px 'Space Mono'", blanco, "center"); c.globalAlpha = 1 } }
    c.fillStyle = "rgba(0,0,0,.18)"; c.fillRect(W / 2 - 1, 0, 2, H); c.fillRect(0, H / 2 - 1, W, 2);
  } });

ESTILOS.push({ slug: "silhouette-rhythm", nombre: "Siluetas al ritmo", dur: 8, poster: 4.9,
  que: "Siluetas negras contra un atardecer enorme. Todo late al tempo de la música: la figura avanza, el sol palpita y las palabras entran en cada golpe.",
  uso: "Para un videoclip o una apertura emotiva: la salida a la cancha en la final, el festejo. Funciona solo con música.",
  draw(c, t, T) {
    const { beat, fase } = reloj(t, 110); const pulso = 1 + .03 * Math.exp(-fase * 6);
    const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, "#2b1055"); g.addColorStop(.45, "#d9445b"); g.addColorStop(.75, "#f9a03f"); g.addColorStop(1, "#ffd27a"); c.fillStyle = g; c.fillRect(0, 0, W, H);
    c.fillStyle = "#ffe6a8"; c.beginPath(); c.arc(W / 2, 330, 190 * pulso, 0, TAU); c.fill();
    c.fillStyle = "#1a0d1f"; c.fillRect(0, 430, W, 110);
    for (let i = 0; i < 9; i++) { const x = ((i * 130 - t * 60) % (W + 200) + W + 200) % (W + 200) - 100; c.beginPath(); c.moveTo(x, 430); c.lineTo(x + 50, 380 - (i % 3) * 20); c.lineTo(x + 100, 430); c.fill() }
    const sil = silueta("#120814"); const s = .95 * pulso, x = lerp(-200, 470, eo(seg(t, 0, 3.5))), y = 440 - 414 * s + Math.abs(Math.sin(t * 6)) * 6;
    c.drawImage(sil, x - 137 * s, y, 275 * s, 414 * s);
    for (let i = 0; i < 6; i++) { const bx = ((i * 170 + t * 90) % (W + 100)) - 50, by = 90 + rnd(i) * 120 + Math.sin(t * 3 + i) * 10; c.strokeStyle = "#1a0d1f"; c.lineWidth = 3; c.beginPath(); c.moveTo(bx - 12, by); c.quadraticCurveTo(bx - 6, by - 8 * Math.abs(Math.sin(t * 8 + i)), bx, by); c.quadraticCurveTo(bx + 6, by - 8 * Math.abs(Math.sin(t * 8 + i)), bx + 12, by); c.stroke() }
    const palabras = [nombre1(T), "EL", "PIBE", "DE", "ORO", T.anio, "NÁPOLES"]; const i = Math.min(palabras.length - 1, Math.max(0, beat - 3));
    if (beat >= 3) { const kk = 1 - fase * .3; texto(c, palabras[i], 60, 130, `${96 * kk + 10}px Anton`, "#1a0d1f") }
    if (t > 6.2) texto(c, T.cifra, 60, 200, "40px 'Bebas Neue'", "#1a0d1f");
  } });

ESTILOS.push({ slug: "spy-titles", nombre: "Títulos de espías de los 60", dur: 8, poster: 6.2,
  que: "Secuencia de títulos de película de espías de los años 60: planos de color recortados, barras que entran, la silueta en franjas y créditos con tipografía desplazada.",
  uso: "Para presentar a los protagonistas como personajes de película: Bilardo, Valdano, Burruchaga, Pumpido. También para el cartel del título.",
  draw(c, t, T) {
    c.fillStyle = "#e9682a"; c.fillRect(0, 0, W, H);
    for (let i = 0; i < 7; i++) { const k = eio(seg(t, i * .12, .8 + i * .12)); const x = 40 + i * 70; c.fillStyle = i % 2 ? "#151515" : "#f3e7cf"; c.fillRect(x, H - H * k * (.6 + rnd(i) * .4), 34, H) }
    const sil = silueta("#151515"); const tiras = 9;
    for (let i = 0; i < tiras; i++) { const k = eo(seg(t, 1.2 + i * .08, 2 + i * .08)); const sy = i * 414 / tiras; const dx = (1 - k) * (i % 2 ? 500 : -500);
      c.drawImage(sil, 0, sy, 275, 414 / tiras + 1, 600 + dx, 60 + sy * 1.1, 275 * 1.1, (414 / tiras + 1) * 1.1) }
    const kt = seg(t, 2.6, 3.0); if (kt > 0) { c.save(); c.globalAlpha = kt; const s = nombre1(T); c.font = "120px Anton"; c.fillStyle = "#151515"; let x = 60; for (let i = 0; i < s.length; i++) { c.fillText(s[i], x, 230 + (i % 2 ? 20 : -10)); x += c.measureText(s[i]).width + 4 } c.restore() }
    const cred = [["UNA PRODUCCIÓN", "S.S.C. NAPOLI"], ["CON", T.nombre.toUpperCase()], ["PRESUPUESTO", T.cifra], ["AÑO", T.anio]];
    const ic = Math.floor((t - 3.6) / 1.1); if (ic >= 0 && ic < cred.length) { const k = seg(t, 3.6 + ic * 1.1, 3.8 + ic * 1.1); c.globalAlpha = k; texto(c, cred[ic][0], 64, 330, "16px 'Space Mono'", "#151515"); texto(c, cred[ic][1], 64, 380, `${tam(c, cred[ic][1], "'Bebas Neue'", 50, 480)}px 'Bebas Neue'`, "#f3e7cf"); c.globalAlpha = 1 }
    if (t > 8 - 1.2) { const k = eo(seg(t, 6.8, 7.4)); c.fillStyle = "#151515"; c.beginPath(); c.arc(300, 420, 60 * k, 0, TAU); c.fill(); c.fillStyle = "#e9682a"; c.beginPath(); c.arc(300, 420, 20 * k, 0, TAU); c.fill() }
  } });

ESTILOS.push({ slug: "swiss-motion", nombre: "Diseño suizo en movimiento", dur: 8, poster: 5.2,
  que: "Grilla estricta, un solo color de señal y tipografía grande que se mueve exacta, cada cambio sobre el pulso. Limpio y preciso.",
  uso: "Para placas de datos y la identidad del canal: estadísticas de un partido, la formación, el resumen final.",
  draw(c, t, T) {
    c.fillStyle = "#f4f4f1"; c.fillRect(0, 0, W, H); const R = "#e3001b", N = "#111";
    c.strokeStyle = "rgba(0,0,0,.08)"; c.lineWidth = 1; for (let x = 40; x < W; x += 80) { c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke() } for (let y = 30; y < H; y += 60) { c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke() }
    const { beat } = reloj(t, 120);
    const pos = [[680, 150], [680, 390], [200, 390], [200, 150]]; const a = pos[Math.floor(beat / 2) % 4], b = pos[(Math.floor(beat / 2) + 1) % 4]; const f = eio(((t * 2) % 2) / 2);
    c.fillStyle = R; c.beginPath(); c.arc(lerp(a[0], b[0], f), lerp(a[1], b[1], f), 70, 0, TAU); c.fill();
    const n = cifraNum(T.cifra); const sz = tam(c, miles(n.n), "'IBM Plex Sans'", 150, 860, 700);
    c.save(); c.beginPath(); c.rect(40, 210, 880, 170); c.clip(); const y = 360 + (1 - eo(seg(t, .4, 1.2))) * 170; texto(c, miles(n.n), 36, y, `700 ${sz}px 'IBM Plex Sans'`, N); c.restore();
    const linea = (s, x, y0, t0) => { const k = eo(seg(t, t0, t0 + .4)); c.save(); c.beginPath(); c.rect(x, y0 - 24, 400, 32); c.clip(); texto(c, s, x, y0 + (1 - k) * 30, "600 20px 'IBM Plex Sans'", N); c.restore() };
    linea(n.pre || "US$", 40, 180, 1.6); linea(T.nombre, 40, 450, 2.0); linea(`Barcelona → Napoli`, 40, 480, 2.4); linea(T.anio, 760, 180, 2.8);
    c.fillStyle = N; c.fillRect(40, 400, 880 * eio(seg(t, 3, 4)), 3);
    if (t > 4.5) { const k = eo(seg(t, 4.5, 5)); c.fillStyle = R; c.fillRect(600, 430, 320 * k, 70); texto(c, "RÉCORD MUNDIAL", 616, 476, "700 26px 'IBM Plex Sans'", "#fff") }
  } });

ESTILOS.push({ slug: "text-flash-cuts", nombre: "Palabras en flash", dur: 8, poster: 6.25,
  que: "Palabras sueltas que cortan al ritmo, blanco sobre negro con cuadros invertidos y un fogonazo de foto en rojo. Tensión de tráiler.",
  uso: "Para el hook y los tráileres: los primeros 10 segundos del video, el anuncio del próximo capítulo.",
  draw(c, t, T) {
    const frases = ["UN", "PIBE", "DE", "FIORITO", "·", "LLEGA", "A", "NÁPOLES", "·", T.cifra, "·", "EL", "MÁS", "CARO", "DE", "LA", "HISTORIA", apellido(T)];
    const dt = 8 / frases.length; const i = Math.min(frases.length - 1, Math.floor(t / dt)); const f = (t % dt) / dt; const s = frases[i];
    const inv = i % 5 === 3, foto = s === "·";
    c.fillStyle = inv ? "#f2f2ee" : "#050505"; c.fillRect(0, 0, W, H);
    if (foto) { cubrir(c, proc("tf-rojo", () => duotono(IMG.brazos, "#1a0000", "#ff3b2e", 960, 540, 0, 0, 960, 540)), 0, 0, W, H, .3, .3, 1.05 + f * .1); return }
    const ult = i === frases.length - 1; const sz = tam(c, s, "Anton", ult ? 200 : 260, 880);
    c.save(); c.translate(W / 2, H / 2 + sz * .34); const k = 1 + (1 - f) * .04; c.scale(k, k); texto(c, s, 0, 0, `${sz}px Anton`, ult ? "#e5261b" : (inv ? "#050505" : "#f2f2ee"), "center"); c.restore();
    if (f < .15) { c.fillStyle = "rgba(255,255,255,.15)"; c.fillRect(0, 0, W, H) }
    texto(c, `${T.anio}`, W - 30, H - 24, "14px 'Space Mono'", inv ? "#050505" : "#777", "right");
  } });

ESTILOS.push({ slug: "ascii-crt", nombre: "Terminal ASCII", dur: 8, poster: 3.4,
  que: "Monitor de fósforo ámbar: todo es texto en una grilla. La foto se arma con caracteres según su densidad, hay líneas tipeadas y un cursor que titila.",
  uso: "Para datos fríos y tensión: la planilla de convocados, el sorteo de grupos, un «archivo secreto» de la AFA.",
  draw(c, t, T) {
    c.fillStyle = "#120a02"; c.fillRect(0, 0, W, H);
    const rampa = " .`:-=+*cox%#&@"; const amb = (a) => `rgba(255,${160 + a * 90},${60 + a * 110},${.5 + a * .5})`;
    const cols = Math.round(lerp(60, 120, eio(seg(t, 2.5, 7)))), rows = Math.round(cols * .375);
    const g = proc("ascii" + cols, () => lumGrid(IMG.brazos, cols, rows, 0, 0, 960, 540));
    const cw = W / cols, ch = H / rows; c.font = `${ch * 1.05}px VT323`; c.textBaseline = "top"; c.textAlign = "left";
    const kf = seg(t, 1.6, 2.6);
    if (kf > 0) for (let j = 0; j < rows; j++) { if (j / rows > kf) break; for (let i = 0; i < cols; i++) { let v = g[j * cols + i]; v = cl((v - .42) * 1.9 + .5); const ch2 = rampa[Math.floor(v * (rampa.length - 1))]; if (ch2 === " ") continue; c.fillStyle = amb(v); c.fillText(ch2, i * cw, j * ch) } }
    const lines = ["> CARGAR TRASPASO.DAT", `SUJETO ..... ${T.nombre.toUpperCase()}`, `DESTINO .... S.S.C. NAPOLI`, `MONTO ...... ${T.cifra}`, `ESTADO ..... CONFIRMADO ${T.anio}`];
    const kl = t < 1.6 ? 1 : 1 - seg(t, 1.6, 2.0);
    c.font = "30px VT323"; lines.forEach((l, i) => { const k = seg(t, i * .28, i * .28 + .3); if (k > 0 && kl > 0) { c.fillStyle = `rgba(255,190,90,${kl})`; c.fillText(tipeo(l, k), 40, 40 + i * 34) } });
    if (t > 6) { c.fillStyle = "rgba(18,10,2,.8)"; c.fillRect(30, H - 90, 520, 56); c.font = "36px VT323"; c.fillStyle = "#ffcf7a"; c.fillText(tipeo(`> ${T.titulo.toUpperCase()}`, seg(t, 6, 7.2)), 44, H - 82) }
    if (Math.floor(t * 2) % 2) { c.fillStyle = "#ffcf7a"; c.fillRect(44 + (t > 6 ? Math.min(500, 10 + 16 * T.titulo.length * seg(t, 6, 7.2)) : 0), t > 6 ? H - 78 : 40 + 5 * 34, 14, 26) }
    lineasScan(c, .25, 3); vineta(c, .7, .45);
  } });

ESTILOS.push({ slug: "backrooms", nombre: "Video encontrado liminal", dur: 8, poster: 6,
  que: "Cámara de mano en un pasillo amarillento e infinito, tubos fluorescentes, la fecha y el REC de la filmadora y, al fondo, una puerta que da a la cancha.",
  uso: "Para el misterio: el túnel del Azteca antes de la final, el vestuario del entretiempo contra Inglaterra. Da suspenso de verdad.",
  draw(c, t, T) {
    const bob = Math.sin(t * 3.4) * 4, sway = Math.sin(t * 1.7) * 6; const vx = W / 2 + sway, vy = H / 2 + bob - 10; const avance = t * .35;
    c.fillStyle = "#b8a35a"; c.fillRect(0, 0, W, H);
    const d = (z) => 1 / (z + .2); const marco = (z) => { const s = d(z) * 260; return [vx - s * 1.3, vy - s, vx + s * 1.3, vy + s * .9] };
    for (let k = 14; k >= 0; k--) { const z = k * .5 - (avance % .5); if (z < .05) continue; const [x0, y0, x1, y1] = marco(z); const sh = Math.min(1, .25 + z * .07);
      c.fillStyle = `rgba(60,48,10,${sh * .5})`; c.strokeStyle = `rgba(80,66,20,${.4})`; c.lineWidth = 1; c.strokeRect(x0, y0, x1 - x0, y1 - y0);
      if (k % 2 === 0) { c.fillStyle = `rgba(255,253,225,${.9 - z * .05})`; const lw = (x1 - x0) * .25; c.fillRect(vx - lw / 2 + sway * .1, y0 + 2, lw, (y1 - y0) * .02 + 2) } }
    const [fx0, fy0, fx1, fy1] = marco(6.5 - (avance % .5)); const pw = (fx1 - fx0) * .3, ph = (fy1 - fy0) * .65;
    c.save(); c.beginPath(); c.rect(vx - pw / 2, fy1 - ph, pw, ph); c.clip(); cubrir(c, IMG.jueguitos, vx - pw / 2, fy1 - ph, pw, ph, .55, .6, 1); c.fillStyle = "rgba(255,255,230,.35)"; c.fillRect(0, 0, W, H); c.restore();
    c.fillStyle = "rgba(60,50,10,.35)"; c.fillRect(0, 0, W, 60 - bob); c.fillRect(0, H - 50 + bob, W, 60);
    vineta(c, .55, .3); c.save(); c.globalAlpha = .35; c.drawImage(granoDe(Math.floor(t * 24)), 0, 0, W, H); c.restore();
    if (Math.floor(t * 1.5) % 2) { c.fillStyle = "#ff2a2a"; c.beginPath(); c.arc(50, 48, 9, 0, TAU); c.fill() } texto(c, "REC", 68, 56, "26px VT323", "#fff");
    texto(c, `JUL. 05 ${T.anio}  18:4${Math.floor(t)}:${String(Math.floor(t * 7) % 60).padStart(2, "0")}`, W - 40, H - 34, "28px VT323", "#fff", "right");
    texto(c, "SP ▶", W - 40, 56, "26px VT323", "#fff", "right");
    if (t > 4.5) { c.fillStyle = "rgba(0,0,0,.55)"; c.fillRect(W / 2 - 240, H - 110, 480, 40); texto(c, "[P1] Del otro lado se escucha a 70.000 personas.", W / 2, H - 83, "24px VT323", "#f6f0cc", "center") }
  } });

ESTILOS.push({ slug: "double-exposure", nombre: "Doble exposición", dur: 8, poster: 6,
  que: "La silueta de la persona rellena con otra imagen: el estadio y la gente adentro de Diego, sobre fondo claro, con letras finas y espaciadas.",
  uso: "Para retratos con significado: «Diego llevaba a Nápoles adentro», Bilardo y su obsesión táctica. Funciona como apertura de capítulo.",
  draw(c, t, T) {
    c.fillStyle = "#eae7e1"; c.fillRect(0, 0, W, H);
    const s = 1.22 + t * .01, w = 275 * s, h = 414 * s, x = 520, y = H - h + 30;
    const lienzoDE = proc("de-l", () => lienzo(W, H)); const x2 = lienzoDE.getContext("2d"); x2.clearRect(0, 0, W, H);
    x2.globalCompositeOperation = "source-over"; x2.drawImage(IMG.rec, x, y, w, h); x2.globalCompositeOperation = "source-in";
    const k = eio(seg(t, .8, 3)); x2.globalAlpha = 1; x2.drawImage(proc("de-gris", () => gris(IMG.jueguitos, 1.7)), x - 300 + t * 10, y - 20, 960 * 1.1, 540 * 1.1);
    x2.globalCompositeOperation = "source-atop"; x2.globalAlpha = 1 - k * .8; x2.drawImage(proc("de-gr2", () => gris(IMG.rec, 1.3, 275, 414)), x, y, w, h); x2.globalAlpha = 1;
    x2.globalCompositeOperation = "source-over";
    const a = eo(seg(t, 0, 1.2)); c.globalAlpha = a; c.drawImage(lienzoDE, 0, 0); c.globalAlpha = 1;
    const g = c.createLinearGradient(0, H - 160, 0, H); g.addColorStop(0, "rgba(234,231,225,0)"); g.addColorStop(1, "#eae7e1"); c.fillStyle = g; c.fillRect(0, H - 160, W, 160);
    const kt = seg(t, 2.6, 3.6); c.globalAlpha = kt; c.font = "300 46px Michroma"; c.fillStyle = "#222"; c.textAlign = "left";
    const nom = nombre1(T).split("").join(" "); c.font = "38px Michroma"; c.fillText(nom, 70, 250);
    c.font = "14px Michroma"; c.fillStyle = "#555"; c.fillText(`N Á P O L E S  ·  ${T.anio}`, 72, 290); c.globalAlpha = 1;
    if (t > 5) { c.globalAlpha = seg(t, 5, 5.8); c.fillStyle = "#222"; c.fillRect(72, 320, 60, 1.5); c.font = "13px 'Space Mono'"; c.fillText(T.titulo, 72, 350); c.globalAlpha = 1 }
  } });

ESTILOS.push({ slug: "silent-film", nombre: "Cine mudo de los años 20", dur: 9, poster: 5.6,
  que: "Cine mudo en blanco y negro, en cuadro 4:3: carteles con marco art nouveau, aperturas y cierres en iris, imagen a los saltos y un parpadeo constante.",
  uso: "Para el humor y las anécdotas viejas: las cábalas, el viaje en avión, los botines prestados. Le da un tono de comedia de época.",
  draw(c, t, T) {
    c.fillStyle = "#000"; c.fillRect(0, 0, W, H); const f = Math.floor(t * 16); const X = 120, Wd = 720;
    c.save(); c.beginPath(); c.rect(X, 0, Wd, H); c.clip();
    const cartel = (l1, l2) => { c.fillStyle = "#0c0c0c"; c.fillRect(X, 0, Wd, H); c.strokeStyle = "#ddd"; c.lineWidth = 2; c.strokeRect(X + 30, 30, Wd - 60, H - 60);
      for (const [x, y, sx, sy] of [[X + 30, 30, 1, 1], [X + Wd - 30, 30, -1, 1], [X + 30, H - 30, 1, -1], [X + Wd - 30, H - 30, -1, -1]]) { c.beginPath(); c.moveTo(x, y + sy * 60); c.quadraticCurveTo(x, y, x + sx * 60, y); c.moveTo(x + sx * 12, y + sy * 40); c.quadraticCurveTo(x + sx * 12, y + sy * 12, x + sx * 40, y + sy * 12); c.stroke() }
      texto(c, l1, W / 2, 260, `${tam(c, l1, "Limelight", 52, 600)}px Limelight`, "#eee", "center"); if (l2) texto(c, l2, W / 2, 320, "26px Limelight", "#bbb", "center") };
    if (t < 2.6) cartel("Nápoles, verano de " + T.anio + ".", "Una ciudad espera a su ídolo.");
    else if (t < 6) { const sep = proc("sf-gris", () => gris(IMG.jueguitos, 1.5)); const dx = (rnd(f) - .5) * 8, dy = (rnd(f + 3) - .5) * 6; cubrir(c, sep, X + dx - 10, dy - 10, Wd + 20, H + 20, .5, .5, 1.1 + seg(t, 2.6, 6) * .08);
      const ki = Math.min(seg(t, 2.6, 3.2), 1 - seg(t, 5.4, 6)); c.fillStyle = "#000"; c.beginPath(); c.rect(X, 0, Wd, H); c.arc(W / 2, H / 2, 20 + ki * 520, 0, TAU, true); c.fill() }
    else cartel(`«¡Ha llegado ${nombre1(T).charAt(0) + nombre1(T).slice(1).toLowerCase()}!»`, `Precio: ${T.cifra}.`);
    c.fillStyle = `rgba(255,255,255,${rnd(f) * .06})`; c.fillRect(X, 0, Wd, H); c.globalAlpha = .5; c.drawImage(granoDe(f), X, 0, Wd, H); c.globalAlpha = 1;
    if (rnd(f + 9) > .6) { c.strokeStyle = "rgba(255,255,255,.5)"; c.lineWidth = 1; const x = X + rnd(f + 1) * Wd; c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke() }
    c.restore(); vineta(c, .5, .3);
  } });
