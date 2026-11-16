// ---------- estilos: los primeros 12 ----------


// 1 · cel-anime-80s
ESTILOS.push({ slug: "cel-anime-80s", nombre: "Anime de los 80", dur: 8, poster: 6.5,
  que: "Atardecer synthwave, grilla de neón, letras cromadas y la foto en dos tonos rosa y cian. Como una apertura de anime de 1986 en VHS.",
  uso: "La apertura de la intro, en «1986: el mundo estaba completamente loco». Une el fútbol con el pop de esa década.",
  draw(c, t, T) {
    const hz = 340;
    let g = c.createLinearGradient(0, 0, 0, hz); g.addColorStop(0, "#0d0221"); g.addColorStop(.55, "#4a0d67"); g.addColorStop(1, "#ff3d81");
    c.fillStyle = g; c.fillRect(0, 0, W, H);
    for (let i = 0; i < 70; i++) { const a = .3 + .7 * Math.abs(Math.sin(t * 2 + i)); c.fillStyle = `rgba(255,255,255,${a * .7})`; c.fillRect(rnd(i) * W, rnd(i + 50) * hz * .7, 1.6, 1.6) }
    const sol = proc("sol80", () => { const s = lienzo(320, 320), x = s.getContext("2d"); const gg = x.createLinearGradient(0, 0, 0, 320); gg.addColorStop(0, "#ffe76a"); gg.addColorStop(.6, "#ff7a3d"); gg.addColorStop(1, "#ff2d95"); x.fillStyle = gg; x.beginPath(); x.arc(160, 160, 158, 0, 7); x.fill(); x.globalCompositeOperation = "destination-out"; for (let k = 0; k < 8; k++) x.fillRect(0, 170 + k * 19, 320, 3 + k * 1.4); return s });
    const sy = lerp(330, 210, eo(seg(t, 0, 2.6)));
    c.save(); c.beginPath(); c.rect(0, 0, W, hz); c.clip(); c.drawImage(sol, W / 2 - 160, sy - 160); c.restore();
    c.fillStyle = "#1b0533"; c.beginPath(); c.moveTo(0, hz);
    [[0, 300], [90, 262], [170, 296], [260, 248], [350, 300], [610, 300], [700, 252], [790, 290], [880, 246], [960, 290], [960, hz]].forEach(p => c.lineTo(...p)); c.fill();
    g = c.createLinearGradient(0, hz, 0, H); g.addColorStop(0, "#2a0845"); g.addColorStop(1, "#05010d"); c.fillStyle = g; c.fillRect(0, hz, W, H - hz);
    c.save(); c.strokeStyle = "#ff2fd0"; c.lineWidth = 1.6; c.shadowColor = "#ff2fd0"; c.shadowBlur = 8;
    for (let k = -14; k <= 14; k++) { c.beginPath(); c.moveTo(W / 2 + k * 9, hz); c.lineTo(W / 2 + k * 120, H); c.stroke() }
    const fr = (t * .9) % 1;
    for (let i = 0; i < 14; i++) { const p = (i + fr) / 14; const y = hz + (H - hz) * p * p; c.globalAlpha = p; c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke() }
    c.restore();
    const foto = proc("cel-diego", () => {
      const d = duotono(IMG.brazos, "#1a0a4a", "#7ff3ff", 520, 520, 40, 0, 540, 540, .9);
      const m = lienzo(520, 520), x = m.getContext("2d"); x.drawImage(d, 0, 0);
      x.globalCompositeOperation = "destination-in"; const gg = x.createLinearGradient(0, 0, 0, 520); gg.addColorStop(.55, "#000"); gg.addColorStop(1, "rgba(0,0,0,0)"); x.fillStyle = gg; x.fillRect(0, 0, 520, 520);
      const gl = x.createLinearGradient(0, 0, 520, 0); gl.addColorStop(0, "rgba(0,0,0,0)"); gl.addColorStop(.25, "#000"); x.fillStyle = gl; x.fillRect(0, 0, 520, 520); return m });
    const kf = eo(seg(t, 1.4, 2.6));
    c.save(); c.globalAlpha = kf; c.globalCompositeOperation = "screen"; c.drawImage(foto, 440 + (1 - kf) * 60, 20); c.restore();
    const kt = seg(t, .9, 1.5), xT = lerp(-700, 60, eo(kt));
    if (kt > 0) {
      c.save(); c.translate(xT, 200); c.transform(1, 0, -.2, 1, 0, 0);
      const s = apellido(T), sz = tam(c, s, "Anton", 128, 600);
      c.font = `${sz}px Anton`; c.textBaseline = "alphabetic";
      const gr = c.createLinearGradient(0, -sz * .8, 0, 0); gr.addColorStop(0, "#f2fbff"); gr.addColorStop(.48, "#6ab7ff"); gr.addColorStop(.5, "#2a0b4a"); gr.addColorStop(.62, "#ff7ad9"); gr.addColorStop(1, "#ffe7f6");
      c.lineWidth = 6; c.strokeStyle = "#ff2fd0"; c.shadowColor = "#ff2fd0"; c.shadowBlur = 18; c.strokeText(s, 0, 0); sinSombra(c);
      c.fillStyle = gr; c.fillText(s, 0, 0);
      if (kt < 1) { c.strokeStyle = "rgba(255,255,255,.7)"; c.lineWidth = 2; for (let i = 0; i < 6; i++) { const y = -sz * (.15 + i * .12); c.beginPath(); c.moveTo(-40 - 300 * (1 - kt), y); c.lineTo(-20, y); c.stroke() } }
      c.restore();
    }
    const enc = t > 2.8 && !(t > 3.0 && t < 3.08) && !(t > 3.25 && t < 3.3);
    if (enc) { c.save(); c.shadowColor = "#3ff7ff"; c.shadowBlur = 22; texto(c, T.anio, 70, 300, "64px Monoton", "#bfffff"); c.restore() }
    const kc = eo(seg(t, 4.2, 4.8));
    if (kc > 0) {
      c.save(); c.globalAlpha = kc; c.translate(70, 380 + (1 - kc) * 20);
      c.font = "38px 'Bebas Neue'"; const w = c.measureText(T.cifra).width + 36;
      c.strokeStyle = "#ffe76a"; c.lineWidth = 3; c.shadowColor = "#ffb800"; c.shadowBlur = 16; c.strokeRect(0, 0, w, 56);
      texto(c, T.cifra, 18, 44, "38px 'Bebas Neue'", "#fff3b0"); sinSombra(c);
      texto(c, T.titulo.toUpperCase(), 0, 84, "15px 'Space Mono'", "#ffc2ec"); c.restore();
    }
    c.fillStyle = "rgba(0,0,0,.18)"; for (let y = 0; y < H; y += 3) c.fillRect(0, y, W, 1);
    if (t < .5) { const a = 1 - t / .5; c.fillStyle = `rgba(255,255,255,${a * .25})`; c.fillRect(0, (t * 900) % H, W, 30) }
  } });

// 2 · telestrator
ESTILOS.push({ slug: "telestrator", nombre: "Pizarra sobre la jugada", dur: 8, poster: 6.2, video: true,
  que: "Corre la jugada real, se congela y se dibuja encima con fibrón amarillo: la pelota marcada, flechas y zonas, como en el análisis de la tele.",
  uso: "Para explicar jugadas: el gol del siglo, la mano de Dios, el pase a Burruchaga en la final. Es el estilo que más va con un canal de fútbol.",
  draw(c, t, T, env) {
    const vid = env.vid, congelado = 2.0;
    const usarVideo = vid && vid.readyState >= 2 && !env.miniatura;
    if (usarVideo) {
      const meta = Math.min(t, congelado);
      if (env.reproduciendo && t < congelado) { if (vid.paused) { vid.currentTime = meta; vid.play().catch(() => {}) } else if (Math.abs(vid.currentTime - meta) > .25) vid.currentTime = meta }
      else { if (!vid.paused) vid.pause(); if (Math.abs(vid.currentTime - meta) > .04) vid.currentTime = meta }
      c.drawImage(vid, 0, 0, W, H);
    } else c.drawImage(IMG.freeze, 0, 0, W, H);
    if (t < congelado) { texto(c, "▶", 30, 50, "22px 'Space Mono'", "rgba(255,255,255,.8)"); return }
    const fuera = 1 - seg(t, 7.4, 7.9);
    c.fillStyle = `rgba(0,10,30,${.22 * fuera})`; c.fillRect(0, 0, W, H);
    const sp = c.createRadialGradient(740, 380, 40, 740, 380, 420); sp.addColorStop(0, "rgba(0,0,0,0)"); sp.addColorStop(1, `rgba(0,0,0,${.35 * fuera})`); c.fillStyle = sp; c.fillRect(0, 0, W, H);
    if (t < 2.12) { c.fillStyle = `rgba(255,255,255,${(1 - (t - 2) / .12) * .7})`; c.fillRect(0, 0, W, H) }
    c.save(); c.globalAlpha = fuera;
    c.lineCap = "round"; c.lineJoin = "round"; c.shadowColor = "rgba(0,0,0,.55)"; c.shadowOffsetY = 2; c.shadowBlur = 3;
    const am = "#ffe600";
    const kz = eo(seg(t, 4.6, 5.2));
    if (kz > 0) { c.fillStyle = `rgba(255,230,0,${.2 * kz})`; c.beginPath(); [[150, 300], [390, 320], [350, 430], [120, 400]].forEach((p, i) => i ? c.lineTo(...p) : c.moveTo(...p)); c.fill();
      c.strokeStyle = am; c.lineWidth = 3; c.setLineDash([10, 9]); c.stroke(); c.setLineDash([]) }
    c.strokeStyle = am; c.lineWidth = 6;
    const ke = seg(t, 2.3, 2.9);
    if (ke > 0) { c.beginPath(); c.ellipse(740, 382, 74, 24, -.06, -1.2, -1.2 + ke * Math.PI * 2.1); c.stroke() }
    const ka = seg(t, 3.2, 3.9), kb = seg(t, 3.6, 4.3);
    if (ka > 0) { const p = curva([500, 350], [300, 330], 50); const f = trazo(c, p, ka); if (ka >= 1) punta(c, p[p.length - 2], f) }
    if (kb > 0) { const p = curva([395, 312], [215, 268], 35); const f = trazo(c, p, kb); if (kb >= 1) punta(c, p[p.length - 2], f) }
    c.lineWidth = 1;
    const et = (s, x, y, k, rot = 0) => { if (k <= 0) return; c.save(); c.globalAlpha = fuera * k; c.translate(x, y); c.rotate(rot); c.font = "30px 'Permanent Marker'"; c.lineWidth = 6; c.strokeStyle = "rgba(0,0,0,.6)"; c.strokeText(s, 0, 0); c.fillStyle = am; c.fillText(s, 0, 0); c.restore() };
    et("PELOTA", 690, 450, seg(t, 2.8, 3.0), -.04);
    et("DESMARQUES", 260, 230, seg(t, 4.2, 4.4), -.08);
    et("EL ESPACIO", 150, 470, seg(t, 5.1, 5.3), .03);
    c.restore();
    const kt = eo(seg(t, 2.05, 2.5)) * fuera;
    if (kt > 0) { c.save(); c.globalAlpha = kt; c.fillStyle = "#111"; c.fillRect(24, 22, 330, 64); c.fillStyle = am; c.fillRect(24, 22, 10, 64);
      texto(c, "LA JUGADA", 48, 58, "30px 'Permanent Marker'", am); texto(c, "ARGENTINA–INGLATERRA · 1986", 48, 78, "12px 'Space Mono'", "#ddd");
      texto(c, "❚❚", 920, 56, "22px 'Space Mono'", "rgba(255,255,255,.85)", "right"); c.restore() }
  } });

// 3 · kino-montage
ESTILOS.push({ slug: "kino-montage", nombre: "Montaje de números", dur: 8, poster: 3.3,
  que: "Cortes secos sobre el pulso de la música: números gigantes, fotos en blanco y negro bien contrastadas y franjas rojas. El ritmo cuenta la historia.",
  uso: "Para las cifras que impactan: US$ 7.500.000, 24 selecciones, 114.600 personas en el Azteca. También sirve de puente entre capítulos.",
  draw(c, t, T) {
    const cortes = [0, 1.0, 2.2, 3.6, 4.4, 6.0];
    c.fillStyle = "#050505"; c.fillRect(0, 0, W, H);
    const g1 = proc("k-fot", () => gris(IMG.fotografos, 1.7)), g2 = proc("k-jue", () => gris(IMG.jueguitos, 1.6)), g3 = proc("k-bra", () => gris(IMG.brazos, 1.6));
    if (t < 1.0) { const s = 1.06 - .06 * eo(seg(t, 0, 1)); c.save(); c.translate(W / 2, H / 2 + 110); c.scale(s, s); const sz = tam(c, T.anio, "Anton", 430, 880); texto(c, T.anio, 0, 0, `${sz}px Anton`, "#f4f4f0", "center"); c.restore() }
    else if (t < 2.2) { cubrir(c, g1, 0, 0, W, H, .5, .35, 1.05 + .07 * seg(t, 1, 2.2)); c.fillStyle = "#d4241c"; c.fillRect(0, 410, 520, 70); texto(c, T.titulo ? "BARCELONA → NÁPOLES" : "", 34, 462, "46px 'Bebas Neue'", "#fff"); texto(c, "01", 30, 52, "16px 'Space Mono'", "#fff") }
    else if (t < 3.6) { const { n, pre } = cifraNum(T.cifra); const v = n * eo(seg(t, 2.25, 3.2)); const s = miles(v);
      const sz = tam(c, miles(n), "Anton", 250, 860); texto(c, pre, 60, 170, "40px 'Bebas Neue'", "#f4f4f0"); texto(c, s, 50, 170 + sz * .95, `${sz}px Anton`, "#e5261b"); c.fillStyle = "#f4f4f0"; c.fillRect(60, 440, 860 * eo(seg(t, 2.6, 3.4)), 6) }
    else if (t < 4.4) { cubrir(c, g2, 0, 0, W / 2, H, .42, .5, 1.1); const ps = T.nombre.toUpperCase().split(/\s+/); ps.forEach((p, i) => texto(c, p, 520, 150 + i * 92, `${tam(c, p, "Anton", 96, 400)}px Anton`, i === ps.length - 1 ? "#e5261b" : "#f4f4f0")) }
    else if (t < 6.0) { const ls = lineas(c, T.titulo.toUpperCase(), "Anton", 92, 820); const k = seg(t, 4.4, 5.0);
      ls.forEach((l, i) => { if (k * ls.length > i - .01) texto(c, l, 64, 150 + i * 104, "92px Anton", i === ls.length - 1 ? "#e5261b" : "#f4f4f0") }); c.fillStyle = "#e5261b"; c.fillRect(64, 160 + ls.length * 104 - 60, 300 * eo(seg(t, 5.0, 5.6)), 10) }
    else { cubrir(c, g3, 0, 0, W, H, .3, .3, 1.08 + .06 * seg(t, 6, 8)); c.fillStyle = "rgba(229,38,27,.88)"; c.fillRect(0, 380, W, 160); const sz = tam(c, T.cifra, "Anton", 110, 860); texto(c, T.cifra, 50, 380 + 80 + sz * .36, `${sz}px Anton`, "#fff") }
    for (const k of cortes) if (t >= k && t - k < 1 / 24 && k > 0) { c.fillStyle = "rgba(255,255,255,.85)"; c.fillRect(0, 0, W, H) }
  } });

// 4 · news-package
ESTILOS.push({ slug: "news-package", nombre: "Noticiero de época", dur: 8, poster: 5,
  que: "Estudio de noticiero de los 80: la imagen en un recuadro biselado, zócalo de último momento, panel con la cifra, cinta que corre y el reloj del canal.",
  uso: "Para contar los hechos como noticia: el pase al Napoli, el sorteo del Mundial, el regreso del plantel. Le da a la información un tono de archivo.",
  draw(c, t, T) {
    let g = c.createLinearGradient(0, 0, W, H); g.addColorStop(0, "#0b2a78"); g.addColorStop(1, "#020a26"); c.fillStyle = g; c.fillRect(0, 0, W, H);
    c.save(); c.globalAlpha = .08; c.strokeStyle = "#7fb0ff"; for (let x = -H; x < W; x += 28) { c.beginPath(); c.moveTo(x + (t * 20) % 28, 0); c.lineTo(x + H + (t * 20) % 28, H); c.stroke() } c.restore();
    const sw = ((t * .35) % 1.6) * W * 1.4 - 200; const sh = c.createLinearGradient(sw - 120, 0, sw + 120, 0); sh.addColorStop(0, "rgba(255,255,255,0)"); sh.addColorStop(.5, "rgba(255,255,255,.06)"); sh.addColorStop(1, "rgba(255,255,255,0)"); c.fillStyle = sh; c.fillRect(0, 0, W, H);
    c.fillStyle = "#d8261c"; c.fillRect(28, 22, 78, 34); texto(c, "LOS 11", 67, 46, "20px 'Bebas Neue'", "#fff", "center"); texto(c, "NOTICIAS", 114, 46, "20px 'Bebas Neue'", "#fff");
    texto(c, "21:00", 930, 46, "20px 'Space Mono'", "#ffd400", "right");
    const ki = eb(seg(t, .2, .8));
    if (ki > 0) { c.save(); c.translate(320, 236); c.scale(ki, ki);
      const bg = c.createLinearGradient(0, -160, 0, 160); bg.addColorStop(0, "#e8eef8"); bg.addColorStop(.5, "#7d8aa6"); bg.addColorStop(1, "#dfe6f2");
      c.fillStyle = bg; c.fillRect(-276, -160, 552, 320); cubrir(c, IMG.fotografos, -266, -150, 532, 300, .5, .3, 1 + .05 * seg(t, .5, 8));
      c.restore();
      if (Math.floor(t * 2) % 2 === 0 && t > .9) { c.fillStyle = "#ffd400"; c.fillRect(58, 90, 150, 24); texto(c, "VÍA SATÉLITE", 133, 108, "17px 'Bebas Neue'", "#0b1a40", "center") } }
    const kp = eo(seg(t, 2.2, 2.8));
    if (kp > 0) { const x = lerp(W + 20, 628, kp); c.fillStyle = "rgba(2,10,38,.82)"; c.fillRect(x, 92, 300, 290); c.fillStyle = "#ffd400"; c.fillRect(x, 92, 300, 6);
      texto(c, "CIFRA RÉCORD", x + 20, 130, "22px 'Bebas Neue'", "#9fc3ff");
      const sz = tam(c, T.cifra, "Bebas Neue", 76, 260); texto(c, T.cifra, x + 20, 210, `${sz}px 'Bebas Neue'`, "#ffd400");
      const k2 = seg(t, 2.9, 3.4); c.globalAlpha = k2; texto(c, "AÑO " + T.anio, x + 20, 262, "26px 'Bebas Neue'", "#fff"); texto(c, "BARCELONA → NÁPOLES", x + 20, 298, "26px 'Bebas Neue'", "#fff"); texto(c, "TRASPASO", x + 20, 344, "14px 'Space Mono'", "#9fc3ff"); c.globalAlpha = 1 }
    const kl = eo(seg(t, 1.2, 1.7)), kw = eo(seg(t, 1.45, 2.1));
    if (kl > 0) { c.fillStyle = "#d8261c"; c.fillRect(0, 404, 250 * kl, 40); texto(c, "ÚLTIMO MOMENTO", 18, 433, "28px 'Bebas Neue'", "#fff");
      c.save(); c.beginPath(); c.rect(0, 444, 40 + 880 * kw, 52); c.clip(); c.fillStyle = "#f3f4f7"; c.fillRect(0, 444, 920, 52);
      const sz = tam(c, T.titulo.toUpperCase(), "Bebas Neue", 40, 860); texto(c, T.titulo.toUpperCase(), 18, 484, `${sz}px 'Bebas Neue'`, "#0b1a40"); c.restore() }
    c.fillStyle = "#020814"; c.fillRect(0, 506, W, 34); c.fillStyle = "#ffd400"; c.fillRect(0, 506, 110, 34); texto(c, "EN VIVO", 55, 530, "20px 'Bebas Neue'", "#020814", "center");
    const cinta = `${T.nombre.toUpperCase()} AL NAPOLI   ★   ${T.cifra}   ★   PRESENTACIÓN EN EL SAN PAOLO   ★   ${T.anio}   ★   `;
    c.save(); c.beginPath(); c.rect(110, 506, W - 110, 34); c.clip(); c.font = "20px 'Bebas Neue'"; const cw = c.measureText(cinta).width; const x0 = W - (t * 110) % cw;
    for (let x = x0 - cw; x < W; x += cw) texto(c, cinta, x, 530, "20px 'Bebas Neue'", "#fff"); c.restore();
  } });

// 5 · halftone-dossier
ESTILOS.push({ slug: "halftone-dossier", nombre: "Expediente en trama", dur: 8, poster: 6.6,
  que: "Un expediente sobre papel: la foto impresa en puntos de trama, fichas escritas a máquina, líneas que conectan con los datos, un sello rojo y el resaltador.",
  uso: "Para presentar a un personaje (Bilardo, Diego, Valdano) o un caso con datos: el doping de Caniggia, la polémica de Menotti y Bilardo.",
  draw(c, t, T) {
    c.drawImage(proc("p-dos", () => papel("#ece4d2", 480, 270, 22)), 0, 0, W, H);
    const fold = c.createLinearGradient(470, 0, 500, 0); fold.addColorStop(0, "rgba(0,0,0,0)"); fold.addColorStop(.5, "rgba(80,60,30,.12)"); fold.addColorStop(1, "rgba(0,0,0,0)"); c.fillStyle = fold; c.fillRect(470, 0, 30, H);
    texto(c, tipeo("EXPEDIENTE N.º 10", seg(t, .1, .7)), 48, 58, "26px 'Special Elite'", "#1d1a16");
    texto(c, "S.S.C. NAPOLI · ARCHIVO", 48, 82, "14px 'Space Mono'", "#b3271d"); c.fillStyle = "#1d1a16"; c.fillRect(48, 94, 864 * eo(seg(t, .2, 1.0)), 2);
    const kf = eo(seg(t, .5, 1.3));
    const ht = proc("dos-ht", () => tramado(IMG.fotografos, "#1d1a16", 380, 380, 330, 40, 300, 300, 5));
    c.save(); c.translate(64 + 190, 120 + 190 + (1 - kf) * 30); c.rotate(-.035); c.globalAlpha = kf;
    sombra(c, 10, 4, .25); c.fillStyle = "#f6f1e6"; c.fillRect(-200, -200, 400, 400); sinSombra(c);
    c.fillStyle = "#e6dcc6"; c.fillRect(-190, -190, 380, 380); c.globalCompositeOperation = "multiply"; c.drawImage(ht, -190, -190); c.globalCompositeOperation = "source-over";
    c.strokeStyle = "#8a8f96"; c.lineWidth = 5; c.beginPath(); c.roundRect(-130, -222, 26, 70, 13); c.stroke();
    c.restore();
    const kc = seg(t, 2.8, 3.5); if (kc > 0) { c.strokeStyle = "#c8281e"; c.lineWidth = 4; c.lineCap = "round"; c.beginPath(); c.ellipse(252, 288, 62, 76, .1, -1.4, -1.4 + kc * 6.5); c.stroke() }
    const campos = [["SUJETO", T.nombre.toUpperCase()], ["ORIGEN", "F.C. BARCELONA"], ["DESTINO", "S.S.C. NAPOLI"], ["MONTO", T.cifra], ["PRESENTACIÓN", `5 JUL ${T.anio} · SAN PAOLO`]];
    campos.forEach(([a, b], i) => { const t0 = 1.4 + i * .55, y = 170 + i * 66, k = seg(t, t0, t0 + .5);
      if (k <= 0) return;
      if (i === 3) { const kh = eo(seg(t, 6.0, 6.5)); if (kh > 0) { c.save(); c.globalCompositeOperation = "multiply"; c.fillStyle = "rgba(255,226,60,.85)"; c.fillRect(536, y - 24, 340 * kh, 34); c.restore() } }
      texto(c, a, 540, y - 30, "12px 'Space Mono'", "#7b6f5c"); texto(c, tipeo(b, k), 540, y, `${tam(c, b, "Special Elite", 26, 370)}px 'Special Elite'`, "#1d1a16");
      c.strokeStyle = "rgba(29,26,22,.25)"; c.lineWidth = 1; c.beginPath(); c.moveTo(540, y + 10); c.lineTo(900, y + 10); c.stroke() });
    const kl = seg(t, 3.4, 4.0); if (kl > 0) { c.strokeStyle = "#c8281e"; c.lineWidth = 1.5; [170, 368].forEach((y, i) => { const p = [[312, 270 + i * 30], [455, 270 + i * 30], [530, y - 10]]; trazo(c, p, kl); if (kl >= 1) { c.fillStyle = "#c8281e"; c.beginPath(); c.arc(530, y - 10, 4, 0, 7); c.fill() } }) }
    const ks = seg(t, 5.0, 5.35);
    if (ks > 0) { const s = lerp(1.7, 1, eo(ks)); c.save(); c.translate(260, 455); c.rotate(-.18); c.scale(s, s); c.globalAlpha = .85 * ks;
      c.strokeStyle = "#c8281e"; c.lineWidth = 5; c.beginPath(); c.roundRect(-150, -36, 300, 72, 8); c.stroke(); c.lineWidth = 2; c.beginPath(); c.roundRect(-140, -27, 280, 54, 5); c.stroke();
      texto(c, "CONFIDENCIAL", 0, 14, "40px 'Rubik Mono One'", "#c8281e", "center"); c.restore() }
  } });

// 6 · vintage-collage
ESTILOS.push({ slug: "vintage-collage", nombre: "Collage de época", dur: 8, poster: 7.5,
  que: "Recortes en stop motion a 12 cuadros por segundo: foto con cinta, estampilla, el billete, la entrada del estadio, matasellos y letras recortadas tipo anónimo.",
  uso: "Para el contexto de época: la Argentina del 86, Malvinas, la llegada a México. Encaja con la mesa de fotos que ya usamos.",
  draw(c, t0, T) {
    const t = Math.floor(t0 * 12) / 12, f = Math.floor(t0 * 12);
    c.drawImage(proc("p-col", () => papel("#e9dfc8", 480, 270, 26)), 0, 0, W, H);
    c.fillStyle = "rgba(160,120,70,.25)"; c.fillRect(470, 0, 490, H);
    const pop = (a) => { const k = seg(t, a, a + .17); return k <= 0 ? 0 : (k < 1 ? 1.12 * k : 1) };
    const jit = (i) => (rnd(f * 7 + i) - .5) * .012;
    const pieza = (a, x, y, r, i, fn) => { const k = pop(a); if (!k) return; c.save(); c.translate(x, y); c.rotate(r + jit(i)); c.scale(k, k); sombra(c, 8, 4, .3); fn(); sinSombra(c); c.restore() };
    const sep = proc("col-sep", () => duotono(IMG.jueguitos, "#2b1d12", "#f3e3c4", 420, 300, 200, 0, 560, 400));
    pieza(.3, 270, 220, -.07, 1, () => { c.fillStyle = "#fbf7ee"; c.fillRect(-222, -168, 444, 336); sinSombra(c); c.drawImage(sep, -210, -156, 420, 300);
      c.fillStyle = "rgba(235,225,190,.75)"; c.save(); c.rotate(-.6); c.fillRect(-40, -200, 90, 28); c.restore(); c.save(); c.translate(200, 150); c.rotate(-.7); c.fillRect(-45, -14, 90, 28); c.restore() });
    const est = proc("col-est", () => { const s = lienzo(200, 240), x = s.getContext("2d"); x.fillStyle = "#fff"; x.fillRect(0, 0, 200, 240); x.globalCompositeOperation = "destination-out";
      for (let i = 0; i <= 200; i += 14) { x.beginPath(); x.arc(i, 0, 6, 0, 7); x.arc(i, 240, 6, 0, 7); x.fill() } for (let j = 0; j <= 240; j += 14) { x.beginPath(); x.arc(0, j, 6, 0, 7); x.arc(200, j, 6, 0, 7); x.fill() }
      x.globalCompositeOperation = "source-over"; x.drawImage(duotono(IMG.brazos, "#8e1b12", "#f6e2c8", 168, 170, 120, 40, 400, 405), 16, 34);
      x.fillStyle = "#8e1b12"; x.font = "bold 20px 'Bebas Neue'"; x.fillText("ITALIA", 18, 26); x.textAlign = "right"; x.fillText("L. 450", 184, 26); x.textAlign = "left"; x.font = "13px 'Space Mono'"; x.fillText("POSTE ITALIANE", 18, 226); return s });
    pieza(1.0, 760, 150, .1, 2, () => c.drawImage(est, -100, -120));
    pieza(1.8, 700, 400, -.17, 3, () => c.drawImage(IMG.dolar, -165, -70, 330, 141));
    pieza(2.6, 230, 440, .05, 4, () => { c.fillStyle = "#e88a3a"; c.fillRect(-150, -52, 300, 104); c.strokeStyle = "rgba(0,0,0,.5)"; c.setLineDash([4, 5]); c.beginPath(); c.moveTo(80, -52); c.lineTo(80, 52); c.stroke(); c.setLineDash([]);
      texto(c, "STADIO SAN PAOLO", -136, -18, "22px 'Bebas Neue'", "#2a1408"); texto(c, `5 · 7 · ${T.anio}`, -136, 14, "26px 'Special Elite'", "#2a1408"); texto(c, "INGRESSO", -136, 38, "12px 'Space Mono'", "#2a1408"); texto(c, "N.º 0010", 92, 6, "11px 'Space Mono'", "#2a1408") });
    const km = pop(3.4); if (km) { c.save(); c.translate(660, 230); c.rotate(-.3); c.globalAlpha = .62 * km; c.strokeStyle = "#1a1714"; c.lineWidth = 3; c.beginPath(); c.arc(0, 0, 58, 0, 7); c.stroke(); c.beginPath(); c.arc(0, 0, 44, 0, 7); c.stroke();
      texto(c, "NAPOLI", 0, -10, "16px 'Space Mono'", "#1a1714", "center"); texto(c, `5.VII.${T.anio.slice(-2)}`, 0, 14, "15px 'Space Mono'", "#1a1714", "center");
      for (let i = 0; i < 4; i++) { c.beginPath(); c.moveTo(62, -24 + i * 14); for (let x = 62; x < 200; x += 10) c.lineTo(x, -24 + i * 14 + Math.sin(x * .1) * 4); c.stroke() } c.restore() }
    const letras = apellido(T).split(""), cols = ["#f2e6c9", "#1d1d1d", "#c8281e", "#f7d046", "#ffffff", "#2b4d9b"];
    letras.forEach((L, i) => { const a = 4.2 + i * .12; const k = pop(a); if (!k) return; const bgc = cols[(i * 3 + 1) % cols.length], fg = (bgc === "#1d1d1d" || bgc === "#c8281e" || bgc === "#2b4d9b") ? "#fff" : "#111";
      c.save(); c.translate(380 + i * 66, 72 + (rnd(i) - .5) * 14); c.rotate((rnd(i + 9) - .5) * .25 + jit(i + 20)); c.scale(k, k); sombra(c, 4, 2, .3); c.fillStyle = bgc; c.fillRect(-28, -34, 56, 66); sinSombra(c);
      texto(c, L, 0, 18, `${46 + rnd(i + 3) * 10}px ${i % 2 ? "Anton" : "'Rubik Mono One'"}`, fg, "center"); c.restore() });
    pieza(5.6, 620, 492, -.04, 5, () => { c.fillStyle = "#fbf7ee"; c.beginPath(); c.moveTo(-150, -26); for (let x = -150; x <= 150; x += 10) c.lineTo(x, -26 + (rnd(x) - .5) * 5); c.lineTo(150, 24); for (let x = 150; x >= -150; x -= 10) c.lineTo(x, 24 + (rnd(x + 99) - .5) * 5); c.fill();
      sinSombra(c); const sz = tam(c, T.cifra, "Special Elite", 30, 280); texto(c, T.cifra, 0, 10, `${sz}px 'Special Elite'`, "#1d1a16", "center") });
  } });

// 7 · silkscreen-poster
ESTILOS.push({ slug: "silkscreen-poster", nombre: "Afiche serigrafiado", dur: 8, poster: 7,
  que: "Un afiche que se imprime en vivo, una tinta por pasada (amarillo, azul, rojo y negro), con el rodillo y el registro que se corre un poco.",
  uso: "Para las placas de capítulo y los afiches del Mundial. Los afiches de 1930-1986 «intervenidos» van muy bien con este estilo.",
  draw(c, t, T) {
    c.drawImage(proc("p-ser", () => papel("#f1ebdd", 480, 270, 14)), 0, 0, W, H);
    const push = 1 + .04 * eio(seg(t, 5, 8)); c.save(); c.translate(W / 2, H / 2); c.scale(push, push); c.translate(-W / 2, -H / 2);
    const capa = (a, i, fn) => { const k = seg(t, a, a + .6); if (k <= 0) return; const off = (1 - eo(seg(t, a, a + 1.6))) * 10 + 2;
      c.save(); c.beginPath(); c.rect(0, 0, W * eio(k), H); c.clip(); c.translate(off * (i % 2 ? 1 : -1), off * .6); c.globalCompositeOperation = "multiply"; fn(); c.restore();
      if (k < 1) { const x = W * eio(k); c.fillStyle = "rgba(60,60,60,.55)"; c.fillRect(x - 6, 0, 12, H) } };
    capa(.2, 0, () => { c.fillStyle = "#f5c400"; c.beginPath(); c.arc(640, 250, 220, 0, 7); c.fill(); c.fillRect(0, 456, W, 26) });
    const az = proc("ser-az", () => umbral(IMG.fotografos, "#1f3fb5", .4, 560, 540, 240, 20, 480, 463));
    capa(1.2, 1, () => c.drawImage(az, 380, 0));
    capa(2.2, 2, () => { const s = apellido(T); const sz = tam(c, s, "'Rubik Mono One'", 150, 900); texto(c, s, 30, 500, `${sz}px 'Rubik Mono One'`, "#e2372b") });
    capa(3.2, 3, () => { texto(c, T.anio, 40, 110, "78px 'Rubik Mono One'", "#151515"); texto(c, T.nombre.toUpperCase(), 44, 150, "16px 'Space Mono'", "#151515");
      texto(c, "BARCELONA → NÁPOLES", 44, 174, "16px 'Space Mono'", "#151515"); texto(c, T.cifra, 44, 214, `${tam(c, T.cifra, "'Rubik Mono One'", 30, 300)}px 'Rubik Mono One'`, "#151515") });
    c.restore();
    c.save(); c.globalAlpha = .5; c.globalCompositeOperation = "multiply"; c.drawImage(granoDe(1), 0, 0, W, H); c.restore();
  } });

// 8 · pop-art
ESTILOS.push({ slug: "pop-art", nombre: "Historieta pop", dur: 8, poster: 6,
  que: "Viñetas de historieta con puntos Ben-Day, la foto en cuatro colores planos, una explosión con la cifra y cartelas de narrador.",
  uso: "Para anécdotas y el «lado B»: las cábalas de Bilardo, el colectivo, las camisetas compradas en un comercio. Es liviano y tiene humor.",
  draw(c, t, T) {
    c.fillStyle = "#111"; c.fillRect(0, 0, W, H);
    const ben = proc("pop-ben", () => { const s = lienzo(480, 300), x = s.getContext("2d"); x.fillStyle = "#ffd83a"; x.fillRect(0, 0, 480, 300); x.fillStyle = "#ff5a4e"; for (let j = 0; j < 300; j += 12) for (let i = (j / 12) % 2 ? 6 : 0; i < 480; i += 12) { x.beginPath(); x.arc(i, j, 3.4, 0, 7); x.fill() } return s });
    const pf = proc("pop-foto", () => poster(IMG.fotografos, ["#111111", "#1d4fd6", "#e3261d", "#f7cf3b", "#fff2dc"], 440, 520, 290, 30, 380, 450));
    const panel = (k, x, y, w, h, fn) => { if (k <= 0) return; c.save(); const s = eb(k); c.translate(x + w / 2, y + h / 2); c.scale(s, s); c.translate(-(x + w / 2), -(y + h / 2)); c.beginPath(); c.rect(x, y, w, h); c.save(); c.clip(); fn(); c.restore(); c.lineWidth = 6; c.strokeStyle = "#111"; c.stroke(); c.restore() };
    c.fillStyle = "#fffaf0"; c.fillRect(0, 0, W, H);
    panel(seg(t, .1, .5), 16, 16, 430, 508, () => { c.drawImage(pf, 16, 4, 440, 520);
      c.fillStyle = "#ffe14d"; c.fillRect(16, 16, 300, 64); c.strokeStyle = "#111"; c.lineWidth = 3; c.strokeRect(16, 16, 300, 64);
      texto(c, `NÁPOLES, JULIO DE ${T.anio}...`, 30, 56, "26px Bangers", "#111") });
    panel(seg(t, 1.2, 1.6), 462, 16, 482, 300, () => { c.drawImage(ben, 462, 16);
      c.save(); c.strokeStyle = "rgba(17,17,17,.5)"; c.lineWidth = 2; for (let i = 0; i < 26; i++) { const a = i / 26 * 6.283; c.beginPath(); c.moveTo(703 + Math.cos(a) * 90, 166 + Math.sin(a) * 70); c.lineTo(703 + Math.cos(a) * 320, 166 + Math.sin(a) * 250); c.stroke() } c.restore();
      const kb = eb(seg(t, 1.7, 2.2)); if (kb > 0) { c.save(); c.translate(703, 172); c.rotate(-.06 + Math.sin(t * 9) * .015); c.scale(kb, kb);
        c.beginPath(); for (let i = 0; i < 36; i++) { const a = i / 36 * 6.283, r = i % 2 ? 92 : 148; c.lineTo(Math.cos(a) * r * 1.45, Math.sin(a) * r * .82) } c.closePath(); c.fillStyle = "#e3261d"; c.fill(); c.lineWidth = 5; c.strokeStyle = "#111"; c.stroke();
        const sz = tam(c, T.cifra, "Bangers", 60, 230); c.font = `${sz}px Bangers`; c.textAlign = "center"; c.lineWidth = 8; c.strokeStyle = "#111"; c.strokeText(T.cifra, 0, 22); c.fillStyle = "#fff"; c.fillText(T.cifra, 0, 22);
        texto(c, "¡RÉCORD!", 0, -38, "36px Bangers", "#ffe14d", "center"); c.restore() } });
    panel(seg(t, 3.0, 3.4), 462, 332, 482, 192, () => { c.fillStyle = "#1d4fd6"; c.fillRect(462, 332, 482, 192);
      const ls = lineas(c, T.titulo.toUpperCase() + "!", "Bangers", 50, 430); const k = seg(t, 3.4, 4.2);
      ls.forEach((l, i) => { if (k * ls.length > i) { c.font = "50px Bangers"; c.textAlign = "left"; c.lineWidth = 7; c.strokeStyle = "#111"; c.strokeText(i === 0 ? "¡" + l : l, 488, 396 + i * 54); c.fillStyle = "#fff"; c.fillText(i === 0 ? "¡" + l : l, 488, 396 + i * 54) } }) });
  } });

// 9 · risograph
ESTILOS.push({ slug: "risograph", nombre: "Risografía", dur: 8, poster: 6,
  que: "Dos tintas, rosa flúo y azul, impresas una sobre otra: donde se cruzan aparece el violeta. Grano, puntos de trama y el registro un poco corrido.",
  uso: "Para los mapas y recorridos: Barcelona → Nápoles, el camino de Argentina en México 86. Es moderno y se nota hecho a mano.",
  draw(c, t, T) {
    c.drawImage(proc("p-riso", () => papel("#f6f1e7", 480, 270, 10)), 0, 0, W, H);
    const rosa = proc("riso-rosa", () => difuminado(IMG.jueguitos, "#ff4fa8", 560, 540, 260, 0, 560, 540));
    const off = 3 + Math.sin(t * 1.3) * 1.5, pan = seg(t, 0, 8);
    c.save(); c.globalCompositeOperation = "multiply";
    const kr = eo(seg(t, .2, 1.2)); c.globalAlpha = kr; c.drawImage(rosa, 400 - pan * 30, 0); c.globalAlpha = 1;
    c.translate(off, -off * .6);
    const az = "#1666c4";
    const ka = eo(seg(t, .8, 1.6)); c.globalAlpha = ka; const sz = tam(c, "NAPOLI", "Anton", 210, 540); texto(c, "NAPOLI", 40, 250 - (1 - ka) * 30, `${sz}px Anton`, az); c.globalAlpha = 1;
    const a = [80, 370], b = [560, 330], p = curva(a, b, 110);
    c.strokeStyle = az; c.lineWidth = 4; c.setLineDash([12, 10]); const fin = trazo(c, p, eio(seg(t, 1.8, 3.6))); c.setLineDash([]);
    if (t > 1.8) { c.fillStyle = az; c.beginPath(); c.arc(...fin, 10, 0, 7); c.fill() }
    c.fillStyle = az; c.beginPath(); c.arc(...a, 8, 0, 7); c.fill(); texto(c, "BARCELONA", 60, 410, "22px 'Space Mono'", az);
    if (t > 3.6) { c.beginPath(); c.arc(...b, 8, 0, 7); c.fill(); texto(c, "NÁPOLES", 520, 372, "22px 'Space Mono'", az) }
    const kc = eo(seg(t, 4.0, 4.6)); c.globalAlpha = kc; const s2 = tam(c, T.cifra, "Anton", 64, 520); texto(c, T.cifra, 40, 490, `${s2}px Anton`, az);
    texto(c, `${T.nombre.toUpperCase()} · ${T.anio}`, 44, 520, "14px 'Space Mono'", az); c.globalAlpha = 1;
    c.fillStyle = "#ff4fa8"; c.globalAlpha = kc; c.fillRect(36 - off, 438 + off * .6, 300, 14); c.globalAlpha = 1;
    c.restore();
    c.save(); c.globalAlpha = .45; c.globalCompositeOperation = "multiply"; c.drawImage(granoDe(2), 0, 0, W, H); c.restore();
  } });

// 10 · scratch-film
ESTILOS.push({ slug: "scratch-film", nombre: "Película rayada", dur: 8, poster: 5.8,
  que: "Dibujos rayados a mano sobre la emulsión negra del celuloide, que tiemblan cuadro a cuadro, con manchas de color pintadas sobre la película. Abstracto y crudo.",
  uso: "Para una pausa poética: «el pibe de Fiorito», la infancia de Diego, o el último corte antes del gol del siglo. Va poco y en un momento elegido.",
  draw(c, t0, T) {
    const f = Math.floor(t0 * 12), t = f / 12;
    const br = .06 + rnd(f) * .05; c.fillStyle = `rgb(${br * 255},${br * 240},${br * 220})`; c.fillRect(0, 0, W, H);
    if (rnd(f + 3) > .55) { c.save(); c.globalAlpha = .22; c.fillStyle = ["#ff3b30", "#ffd60a", "#30d5ff", "#ff2fd0"][f % 4]; c.beginPath(); c.ellipse(rnd(f + 1) * W, rnd(f + 2) * H, 80 + rnd(f + 4) * 160, 60 + rnd(f + 5) * 110, rnd(f) * 3, 0, 7); c.fill(); c.restore() }
    const J = (p, i) => [p[0] + (rnd(f * 31 + i) - .5) * 5, p[1] + (rnd(f * 17 + i) - .5) * 5];
    c.strokeStyle = "#f5f2ea"; c.lineWidth = 3; c.lineCap = "round"; c.lineJoin = "round";
    if (t < 2.6) { const pts = [[400, 140], [440, 128], [480, 150], [520, 128], [560, 140], [650, 190], [612, 254], [570, 232], [570, 410], [390, 410], [390, 232], [348, 254], [310, 190], [400, 140]].map(J);
      trazo(c, pts, seg(t, .2, 1.6)); if (t > 1.6) { c.save(); c.translate(...J([480, 340], 99)); c.font = "130px 'Permanent Marker'"; c.textAlign = "center"; c.lineWidth = 3; c.strokeText("10", 0, 0); c.restore() } }
    else if (t < 4.6) { const k = seg(t, 2.6, 4.6); for (let i = 0; i < 6; i++) { const kk = k - i * .05; if (kk < 0) continue; const x = 120 + kk * 720, y = 420 - Math.abs(Math.sin(kk * 9)) * 260; c.globalAlpha = i ? .25 : 1; c.beginPath(); for (let a = 0; a < 7; a += .5) { const r = 34 + (rnd(f + a * 3) - .5) * 6; c.lineTo(x + Math.cos(a) * r, y + Math.sin(a) * r) } c.stroke() } c.globalAlpha = 1;
      c.beginPath(); c.moveTo(...J([60, 460], 1)); c.lineTo(...J([900, 460], 2)); c.stroke() }
    else if (t < 6.6) { const s = nombre1(T); c.save(); c.font = `${tam(c, s, "'Permanent Marker'", 190, 760)}px 'Permanent Marker'`; c.textAlign = "center"; for (let i = 0; i < 2; i++) { c.lineWidth = 2.5; c.strokeText(s, W / 2 + (rnd(f + i) - .5) * 6, 330 + (rnd(f + i + 5) - .5) * 6) } c.restore() }
    else { c.save(); c.textAlign = "center"; c.lineWidth = 2.5; c.font = `${tam(c, T.cifra, "'Permanent Marker'", 110, 820)}px 'Permanent Marker'`; c.strokeText(T.cifra, W / 2 + (rnd(f) - .5) * 5, 300); c.font = "60px 'Permanent Marker'"; c.strokeText(T.anio, W / 2 + (rnd(f + 2) - .5) * 5, 400); c.restore() }
    c.strokeStyle = "rgba(245,242,234,.55)"; c.lineWidth = 1; for (let i = 0; i < 3; i++) if (rnd(f * 3 + i) > .4) { const x = rnd(f * 5 + i) * W; c.beginPath(); c.moveTo(x, 0); c.lineTo(x + (rnd(i + f) - .5) * 10, H); c.stroke() }
    c.fillStyle = "rgba(245,242,234,.8)"; for (let i = 0; i < 14; i++) c.fillRect(rnd(f * 11 + i) * W, rnd(f * 13 + i) * H, 1 + rnd(i + f) * 3, 1 + rnd(i * 2 + f) * 3);
    c.fillStyle = "#000"; c.fillRect(0, 0, 26, H); c.fillRect(W - 26, 0, 26, H); c.fillStyle = "#3a352c"; for (let y = -((t0 * 240) % 40); y < H; y += 40) { c.fillRect(7, y, 12, 22); c.fillRect(W - 19, y, 12, 22) }
  } });

// 11 · newsreel
ESTILOS.push({ slug: "newsreel", nombre: "Noticiario de cine", dur: 9, poster: 5.2,
  que: "Noticiario de cine en sepia: cuenta regresiva de la cola de película, carteles con marco art déco, la imagen que tiembla, parpadeo, rayas y polvo.",
  uso: "Para la historia vieja: los Mundiales del 30 al 78 y la línea de tiempo de los afiches. Diferencia el pasado del presente del relato.",
  draw(c, t, T) {
    const f = Math.floor(t * 18);
    const sep = proc("nr-sep", () => duotono(IMG.jueguitos, "#1e140a", "#f1dfbd", 960, 540, 0, 0, 960, 540, 1.1));
    const marco = () => { c.strokeStyle = "#d9c9a3"; c.lineWidth = 3; c.strokeRect(70, 60, W - 140, H - 120); c.lineWidth = 1; c.strokeRect(84, 74, W - 168, H - 148);
      [[70, 60], [W - 70, 60], [70, H - 60], [W - 70, H - 60]].forEach(([x, y]) => { c.beginPath(); c.arc(x, y, 12, 0, 7); c.stroke() }) };
    if (t < 1.6) { c.fillStyle = "#8a8173"; c.fillRect(0, 0, W, H); const n = 3 - Math.floor(t / .55); const a = ((t % .55) / .55) * 6.283;
      c.fillStyle = "#6c6457"; c.beginPath(); c.moveTo(W / 2, H / 2); c.arc(W / 2, H / 2, 400, -1.5708, -1.5708 + a); c.fill();
      c.strokeStyle = "#1c1a16"; c.lineWidth = 3; c.beginPath(); c.arc(W / 2, H / 2, 190, 0, 7); c.stroke(); c.beginPath(); c.arc(W / 2, H / 2, 160, 0, 7); c.stroke(); c.beginPath(); c.moveTo(0, H / 2); c.lineTo(W, H / 2); c.moveTo(W / 2, 0); c.lineTo(W / 2, H); c.stroke();
      texto(c, String(Math.max(1, n)), W / 2, H / 2 + 80, "220px Limelight", "#1c1a16", "center") }
    else if (t < 3.6) { c.fillStyle = "#0d0b08"; c.fillRect(0, 0, W, H); const k = seg(t, 1.6, 2.0) * (1 - seg(t, 3.3, 3.6)); c.globalAlpha = k; marco();
      texto(c, "NÁPOLES", W / 2, 270, "104px Limelight", "#efe2c4", "center"); texto(c, `JULIO DE ${T.anio}`, W / 2, 340, "34px Limelight", "#c9b88f", "center"); c.globalAlpha = 1 }
    else if (t < 6.6) { const dx = (rnd(f) - .5) * 6, dy = (rnd(f + 7) - .5) * 5; cubrir(c, sep, dx - 10, dy - 10, W + 20, H + 20, .45, .5, 1.05 + .07 * seg(t, 3.6, 6.6));
      const k = seg(t, 4.2, 4.6); c.globalAlpha = k; const ls = lineas(c, T.titulo.toUpperCase(), "Limelight", 40, 760); ls.forEach((l, i) => { c.save(); c.shadowColor = "#000"; c.shadowBlur = 8; texto(c, l, W / 2, 440 + i * 46 - (ls.length - 1) * 46, "40px Limelight", "#fff8e6", "center"); c.restore() }); c.globalAlpha = 1 }
    else { c.fillStyle = "#0d0b08"; c.fillRect(0, 0, W, H); const k = seg(t, 6.6, 7.0); c.globalAlpha = k; marco();
      texto(c, "UN PASE DE", W / 2, 220, "34px Limelight", "#c9b88f", "center"); texto(c, T.cifra, W / 2, 330, `${tam(c, T.cifra, "Limelight", 96, 700)}px Limelight`, "#efe2c4", "center"); texto(c, T.nombre, W / 2, 400, "26px Limelight", "#c9b88f", "center"); c.globalAlpha = 1 }
    c.fillStyle = `rgba(0,0,0,${.04 + rnd(f) * .12})`; c.fillRect(0, 0, W, H);
    c.save(); c.globalAlpha = .55; c.drawImage(granoDe(f), 0, 0, W, H); c.restore();
    c.strokeStyle = "rgba(240,230,210,.4)"; c.lineWidth = 1; if (rnd(f + 1) > .5) { const x = rnd(f + 2) * W; c.beginPath(); c.moveTo(x, 0); c.lineTo(x + 3, H); c.stroke() }
    c.fillStyle = "rgba(20,15,10,.7)"; for (let i = 0; i < 5; i++) if (rnd(f * 9 + i) > .6) { c.beginPath(); c.arc(rnd(f * 3 + i) * W, rnd(f * 7 + i) * H, 1 + rnd(i) * 3, 0, 7); c.fill() }
    const v = c.createRadialGradient(W / 2, H / 2, H * .35, W / 2, H / 2, H * .95); v.addColorStop(0, "rgba(0,0,0,0)"); v.addColorStop(1, "rgba(0,0,0,.75)"); c.fillStyle = v; c.fillRect(0, 0, W, H);
  } });

// 12 · satellite-briefing
const COSTA = {
  europa: [[21, 49], [-4.7, 49], [-4.7, 48.4], [-2, 47], [-1.2, 46.2], [-1.8, 43.4], [-3.8, 43.5], [-8, 43.7], [-9.3, 43], [-8.8, 42], [-8.7, 40.6], [-9.5, 38.8], [-8.8, 38.7], [-8.9, 37], [-7.4, 37.2], [-6.4, 36.8], [-5.6, 36], [-4.4, 36.7], [-2.1, 36.7], [-1.6, 37.5], [-.7, 38], [.2, 38.8], [-.3, 39.4], [0, 40], [.9, 41], [2.2, 41.4], [3.2, 41.9], [3.2, 42.4], [4, 43.5], [5.4, 43.2], [7, 43.6], [8.4, 44.2], [9.8, 44.1], [10.3, 43.5], [10.5, 42.9], [11.2, 42.4], [12.4, 41.7], [13.1, 41.2], [14.2, 40.8], [14.5, 40.6], [15, 40.2], [15.7, 40], [16, 39.4], [15.6, 38.2], [16.1, 37.9], [17.1, 38.9], [16.6, 39.6], [17.2, 40.4], [18.5, 40.1], [18, 40.6], [17, 41.1], [16, 41.9], [15.2, 41.9], [14, 42.6], [13.6, 43.5], [12.4, 44.3], [12.3, 45.3], [13.7, 45.7], [14, 45], [15, 44.8], [16.4, 43.5], [18, 42.7], [19.4, 42], [19.4, 40.6], [20, 39.7], [21, 39.5]],
  africa: [[-7, 30], [-7, 34], [-6, 35.8], [-5.3, 35.9], [-2.9, 35.3], [-1, 35.7], [1, 36.5], [3, 36.8], [5, 36.8], [7, 37], [8.6, 36.9], [10.2, 37.2], [11, 36.9], [10.5, 36], [11, 35.2], [10.1, 34.2], [10.5, 33.5], [12, 33], [15, 32.4], [19, 30.5], [21, 31], [21, 30]],
  cerdena: [[8.4, 41.1], [9.2, 41.2], [9.8, 40.6], [9.6, 39.2], [9, 39], [8.4, 39], [8.5, 40.2]],
  corcega: [[9.4, 43], [9.6, 42.6], [9.4, 41.4], [8.8, 41.5], [8.6, 42.3]],
  sicilia: [[12.4, 38.1], [13.4, 38.2], [15.6, 38.3], [15.1, 37.3], [15.1, 36.7], [14.3, 36.8], [12.4, 37.7]],
  mallorca: [[2.4, 39.6], [3.1, 39.9], [3.5, 39.7], [3.2, 39.3], [2.7, 39.5]],
};
ESTILOS.push({ slug: "satellite-briefing", nombre: "Informe satelital", dur: 9, poster: 7.6,
  que: "Pantalla de inteligencia: mapa vectorial del Mediterráneo, coordenadas, la ruta trazada de ciudad a ciudad, barrido de radar y una ficha que se escanea.",
  uso: "Para los viajes y las sedes: la concentración en el América, los estadios de México, el vuelo de vuelta. Con «La sede: México» combina con el zoom satelital.",
  draw(c, t, T) {
    c.fillStyle = "#04101a"; c.fillRect(0, 0, W, H);
    const kz = eio(seg(t, 4.6, 7.2)); const cx = lerp(8, 13.2, kz), cy = lerp(40.8, 40.85, kz), z = lerp(1, 2.4, kz);
    const sx = 27 * z, sy = sx * 1.32;
    const P = ([lo, la]) => [W / 2 + (lo - cx) * sx, H / 2 + (cy - la) * sy];
    c.strokeStyle = "rgba(79,209,255,.12)"; c.lineWidth = 1;
    for (let lo = -12; lo <= 24; lo += 2) { c.beginPath(); c.moveTo(...P([lo, 50])); c.lineTo(...P([lo, 28])); c.stroke() }
    for (let la = 28; la <= 50; la += 2) { c.beginPath(); c.moveTo(...P([-12, la])); c.lineTo(...P([24, la])); c.stroke() }
    c.fillStyle = "#0e2a3b"; c.strokeStyle = "rgba(79,209,255,.75)"; c.lineWidth = 1.4;
    Object.values(COSTA).forEach(poly => { c.beginPath(); poly.forEach((p, i) => i ? c.lineTo(...P(p)) : c.moveTo(...P(p))); c.closePath(); c.fill(); c.stroke() });
    const bar = P([2.17, 41.39]), nap = P([14.27, 40.85]);
    const scan = (t * 260) % (W + 200) - 100; const gs = c.createLinearGradient(scan - 80, 0, scan, 0); gs.addColorStop(0, "rgba(79,209,255,0)"); gs.addColorStop(1, "rgba(79,209,255,.12)"); c.fillStyle = gs; c.fillRect(scan - 80, 0, 80, H);
    const ciudad = (p, n, k, izq) => { if (k <= 0) return; c.strokeStyle = "#7fe3ff"; c.fillStyle = "#7fe3ff"; c.beginPath(); c.arc(...p, 4, 0, 7); c.fill(); c.globalAlpha = k * (1 - ((t * 1.2) % 1)); c.beginPath(); c.arc(...p, 6 + ((t * 1.2) % 1) * 24, 0, 7); c.stroke(); c.globalAlpha = k; texto(c, n, p[0] + (izq ? -10 : 10), p[1] - 10, "13px 'Space Mono'", "#bff1ff", izq ? "right" : "left"); c.globalAlpha = 1 };
    ciudad(bar, "BARCELONA 41.39N 2.17E", seg(t, .6, 1.0));
    const ka = eio(seg(t, 1.8, 4.0));
    if (ka > 0) { const p = curva(bar, nap, 70 * z); c.strokeStyle = "#ff9f1c"; c.lineWidth = 2.5; c.setLineDash([8, 6]); const fin = trazo(c, p, ka); c.setLineDash([]); c.fillStyle = "#ff9f1c"; c.beginPath(); c.arc(...fin, 5, 0, 7); c.fill();
      if (ka > .3 && ka < 1) texto(c, "≈ 1.020 KM", fin[0] + 10, fin[1] + 22, "12px 'Space Mono'", "#ffc46b") }
    ciudad(nap, "NÁPOLES 40.85N 14.27E", seg(t, 3.8, 4.2), true);
    const kf = seg(t, 5.0, 6.4);
    if (kf > 0) { const x = 660, y = 96, s = 230; c.strokeStyle = "#7fe3ff"; c.lineWidth = 1; c.globalAlpha = Math.min(1, kf * 3);
      c.beginPath(); c.moveTo(...nap); c.lineTo(x, y + s); c.stroke();
      c.save(); c.beginPath(); c.rect(x, y, s, s * kf); c.clip(); c.drawImage(proc("sat-foto", () => duotono(IMG.brazos, "#04101a", "#9feaff", 230, 230, 120, 20, 420, 420)), x, y); c.restore();
      c.fillStyle = "#7fe3ff"; c.fillRect(x, y + s * kf - 1, s, 2);
      const b = 16; c.lineWidth = 2.5; [[x, y, 1, 1], [x + s, y, -1, 1], [x, y + s, 1, -1], [x + s, y + s, -1, -1]].forEach(([a, bb, dx, dy]) => { c.beginPath(); c.moveTo(a + dx * b, bb); c.lineTo(a, bb); c.lineTo(a, bb + dy * b); c.stroke() });
      c.globalAlpha = 1;
      const kt = seg(t, 6.2, 7.4); texto(c, tipeo("OBJETIVO: " + T.nombre.toUpperCase(), kt * 1.4), x, y + s + 26, "12px 'Space Mono'", "#bff1ff"); texto(c, tipeo("MONTO: " + T.cifra, kt * 1.4 - .4), x, y + s + 46, "12px 'Space Mono'", "#ffc46b") }
    c.strokeStyle = "rgba(127,227,255,.7)"; c.lineWidth = 2; const B = 22;
    [[16, 16, 1, 1], [W - 16, 16, -1, 1], [16, H - 16, 1, -1], [W - 16, H - 16, -1, -1]].forEach(([a, b, dx, dy]) => { c.beginPath(); c.moveTo(a + dx * B, b); c.lineTo(a, b); c.lineTo(a, b + dy * B); c.stroke() });
    texto(c, "LOS 11 · BRIEFING · TRASPASO", 34, 44, "13px 'Space Mono'", "#7fe3ff"); texto(c, `05.07.${T.anio}`, W - 34, 44, "13px 'Space Mono'", "#7fe3ff", "right");
    texto(c, `CENTRO ${cy.toFixed(2)}N ${cx.toFixed(2)}E · ZOOM ${z.toFixed(1)}×`, 34, H - 32, "12px 'Space Mono'", "rgba(127,227,255,.75)");
    c.fillStyle = "rgba(0,0,0,.12)"; for (let y = 0; y < H; y += 3) c.fillRect(0, y, W, 1);
  } });

