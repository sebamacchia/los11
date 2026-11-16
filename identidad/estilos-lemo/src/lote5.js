// ---------- lote 5: dibujos animados · pantallas e interfaces · juegos ----------

function cabezaDiego(c, x, y, r, piel = "#e0a77a", pelo = "#1d140e", linea = "#111", lw = 3) { // caricatura simple
  c.save(); c.translate(x, y); c.fillStyle = pelo; for (let i = 0; i < 11; i++) { const a = Math.PI + i / 10 * Math.PI; c.beginPath(); c.arc(Math.cos(a) * r * .85, Math.sin(a) * r * .75 - r * .1, r * .38, 0, TAU); c.fill() }
  c.fillStyle = piel; c.beginPath(); c.ellipse(0, r * .1, r * .78, r * .9, 0, 0, TAU); c.fill(); c.strokeStyle = linea; c.lineWidth = lw; c.stroke();
  c.fillStyle = pelo; for (let i = 0; i < 7; i++) { c.beginPath(); c.arc(-r * .6 + i * r * .2, -r * .62, r * .22, 0, TAU); c.fill() }
  c.fillStyle = linea; c.beginPath(); c.arc(-r * .28, r * .05, r * .09, 0, TAU); c.arc(r * .28, r * .05, r * .09, 0, TAU); c.fill();
  c.beginPath(); c.lineWidth = lw * .8; c.arc(0, r * .32, r * .3, .2, Math.PI - .2); c.stroke(); c.restore();
}

ESTILOS.push({ slug: "comic-history", nombre: "Historieta de historia", dur: 8, poster: 5.8,
  que: "Historia contada con un mapa de caricatura: los países como piezas con borde grueso, personajes cabezones que saltan de un lugar a otro y carteles con humor.",
  uso: "Para geopolítica liviana: Malvinas y el partido con Inglaterra, la Italia de los extranjeros, el reparto de sedes del Mundial.",
  draw(c, t, T) {
    c.fillStyle = "#9fd4e8"; c.fillRect(0, 0, W, H); const P = proyector(8.5, 40.5, 1.25);
    c.save(); c.strokeStyle = "#1b1b1b"; c.lineWidth = 4; c.lineJoin = "round"; dibujarCosta(c, P, "#f3e2b3", "#1b1b1b", 4); c.restore();
    const lugar = (q, s, col) => { c.fillStyle = col; c.beginPath(); c.arc(...q, 9, 0, TAU); c.fill(); c.strokeStyle = "#1b1b1b"; c.lineWidth = 3; c.stroke(); caja(c, q[0] - 60, q[1] + 16, 120, 30, "#fff", "#1b1b1b", 3, 8); texto(c, s, q[0], q[1] + 38, "20px Bangers", "#1b1b1b", "center") };
    const b = P(BCN), n = P(NAP); lugar(b, "BARCELONA", "#a50044"); lugar(n, "NÁPOLES", "#1e7bd6");
    const k = eio(seg(t, 1.2, 4)); const p = curva(b, n, 150); const idx = Math.min(p.length - 1, Math.floor(k * (p.length - 1)));
    c.strokeStyle = "#1b1b1b"; c.setLineDash([10, 8]); c.lineWidth = 3; trazo(c, p, k); c.setLineDash([]);
    const sq = 1 + Math.sin(t * 12) * .06 * (k > 0 && k < 1 ? 1 : 0); escala(c, p[idx][0], p[idx][1] - 46, 1, () => { c.scale(1 / sq, sq); cabezaDiego(c, 0, 0, 36) });
    if (t > 4.2) { const kk = eb(seg(t, 4.2, 4.6)); escala(c, n[0] + 140, n[1] - 120, kk, () => { caja(c, -110, -40, 220, 70, "#fff", "#1b1b1b", 4, 16); texto(c, "¡FORZA NAPOLI!", 0, 6, "30px Bangers", "#1e7bd6", "center") }) }
    caja(c, 30, 24, 380, 56, "#ffd84a", "#1b1b1b", 4, 6); texto(c, `VERANO DE ${T.anio}: ¡MUDANZA!`, 46, 62, "32px Bangers", "#1b1b1b");
    if (t > 5.4) { caja(c, 560, 450, 360, 60, "#fff", "#1b1b1b", 4, 6); texto(c, `PRECIO: ${T.cifra}`, 576, 490, "30px Bangers", "#d62828") }
  } });

ESTILOS.push({ slug: "manga-panels", nombre: "Viñetas de manga", dur: 8, poster: 6,
  que: "Páginas de manga en blanco y negro: viñetas que entran en diagonal, tramas de puntos, líneas de velocidad y una onomatopeya enorme.",
  uso: "Para jugadas épicas en clave de anime: el gol del siglo en viñetas, la previa de la final como capítulo de shōnen.",
  draw(c, t, T) {
    c.fillStyle = "#fff"; c.fillRect(0, 0, W, H);
    const tinta = proc("mg-t", () => { const a = umbral(IMG.fotografos, "#111", .32, 420, 520, 330, 20, 300, 372); return a });
    const tr = proc("mg-tr", () => tramado(IMG.fotografos, "#111", 420, 520, 330, 20, 300, 372, 5));
    const panel = (pts, t0, fn) => { const k = eo(seg(t, t0, t0 + .35)); if (k <= 0) return; c.save(); c.globalAlpha = k; c.beginPath(); pts.forEach((p, i) => i ? c.lineTo(...p) : c.moveTo(...p)); c.closePath(); c.save(); c.clip(); fn(); c.restore(); c.strokeStyle = "#111"; c.lineWidth = 5; c.stroke(); c.restore() };
    panel([[16, 16], [560, 16], [500, 300], [16, 300]], .2, () => { c.save(); c.translate(250, 160); for (let i = 0; i < 80; i++) { const a = rnd(i) * TAU, r0 = 60 + rnd(i + 3) * 40; c.strokeStyle = "#111"; c.lineWidth = .8 + rnd(i + 5) * 2.4; c.beginPath(); c.moveTo(Math.cos(a) * r0, Math.sin(a) * r0); c.lineTo(Math.cos(a) * 520, Math.sin(a) * 520); c.stroke() } c.restore(); pelota(c, 250, 160, 46, t * 2, "#fff", "#111", 3) });
    panel([[580, 16], [944, 16], [944, 524], [520, 524], [520, 316]], 1.2, () => { c.drawImage(tr, 520, 4, 430, 532); c.globalCompositeOperation = "multiply"; c.drawImage(tinta, 520, 4, 430, 532); c.globalCompositeOperation = "source-over" });
    panel([[16, 316], [500, 316], [500, 524], [16, 524]], 2.4, () => { c.fillStyle = "#111"; c.fillRect(16, 316, 490, 210); const s = apellido(T); c.save(); c.translate(260, 450); c.rotate(-.08); c.font = `${tam(c, s, "Bangers", 96, 440)}px Bangers`; c.textAlign = "center"; c.lineWidth = 10; c.strokeStyle = "#fff"; c.strokeText(s, 0, 0); c.fillStyle = "#111"; c.fillText(s, 0, 0); c.restore() });
    if (t > 3.4) { const k = eb(seg(t, 3.4, 3.8)); escala(c, 470, 110, k, () => { c.rotate(.15); c.font = "110px Bangers"; c.textAlign = "center"; c.lineWidth = 12; c.strokeStyle = "#fff"; c.strokeText("¡BAM!", 0, 0); c.fillStyle = "#111"; c.fillText("¡BAM!", 0, 0) }) }
    if (t > 4.6) { caja(c, 560, 40, 150, 80, "#fff", "#111", 3, 30); texto(c, "Nápoles,", 635, 74, "22px 'Special Elite'", "#111", "center"); texto(c, T.anio + ".", 635, 100, "22px 'Special Elite'", "#111", "center") }
  } });

ESTILOS.push({ slug: "midcentury-toon", nombre: "Dibujo animado de los 50", dur: 8, poster: 5.2,
  que: "Dibujo animado de mediados de siglo: formas geométricas planas, colores mostaza, turquesa y coral, texturas de papel y personajes estilizados.",
  uso: "Para guías y procesos con encanto retro: cómo se armaba la valija, el viaje en avión, el reglamento contado como cartoon educativo.",
  draw(c, t, T) {
    c.fillStyle = "#f2e3c6"; c.fillRect(0, 0, W, H); c.fillStyle = "#e7b13c"; c.beginPath(); c.arc(760, 150, 110, 0, TAU); c.fill();
    c.fillStyle = "#2a9d8f"; poligono(c, [[0, 400], [180, 300], [380, 380], [600, 290], [960, 400], [960, 540], [0, 540]], "#2a9d8f");
    c.fillStyle = "#e76f51"; c.fillRect(0, 440, W, 100);
    for (let i = 0; i < 7; i++) { const x = 60 + i * 140; poligono(c, [[x, 440], [x + 20, 360], [x + 40, 440]], "#264653") }
    const k = eio(seg(t, .4, 3.6)), x = lerp(120, 560, k), y = 400 - Math.abs(Math.sin(t * 6)) * 14 * (k < 1 ? 1 : 0);
    poligono(c, [[x - 40, y - 10], [x + 40, y - 10], [x + 25, y - 110], [x - 25, y - 110]], "#3d7cc9"); texto(c, "10", x, y - 50, "36px 'Bebas Neue'", "#f2e3c6", "center");
    c.fillStyle = "#264653"; c.fillRect(x - 30, y - 10, 18, 50); c.fillRect(x + 12, y - 10, 18, 50);
    c.fillStyle = "#e0a77a"; c.beginPath(); c.arc(x, y - 140, 32, 0, TAU); c.fill(); c.fillStyle = "#264653"; for (let i = 0; i < 6; i++) { c.beginPath(); c.arc(x - 26 + i * 10, y - 168, 12, 0, TAU); c.fill() }
    c.fillStyle = "#264653"; c.fillRect(x - 14, y - 146, 6, 6); c.fillRect(x + 8, y - 146, 6, 6);
    const bx = x + 60 + Math.sin(t * 6) * 6, by = 430 - Math.abs(Math.sin(t * 6)) * 40; c.fillStyle = "#fff"; c.beginPath(); c.arc(bx, by, 16, 0, TAU); c.fill(); c.strokeStyle = "#264653"; c.lineWidth = 3; c.stroke();
    if (t > 3.8) { const kk = eo(seg(t, 3.8, 4.4)); caja(c, 600, 300 + (1 - kk) * 40, 320, 110, "#264653"); texto(c, "NAPOLI", 760, 352 + (1 - kk) * 40, "44px 'Bebas Neue'", "#e7b13c", "center"); texto(c, `${T.anio} · ${T.cifra}`, 760, 384 + (1 - kk) * 40, "16px 'Space Mono'", "#f2e3c6", "center") }
    texto(c, "THE KID FROM FIORITO", 40, 60, "34px 'Bebas Neue'", "#264653");
    c.save(); c.globalAlpha = .2; c.globalCompositeOperation = "multiply"; c.drawImage(granoDe(2), 0, 0, W, H); c.restore();
  } });

ESTILOS.push({ slug: "rubber-hose", nombre: "Dibujo animado de los años 30", dur: 8, poster: 4,
  que: "Dibujo animado en blanco y negro de los años 30: personajes con brazos de manguera, guantes blancos y ojos de pastel que rebotan al ritmo, con grano de película.",
  uso: "Para el humor del lado B: la pelota «enamorada» de Diego, las cábalas, el colectivo que no arrancaba.",
  draw(c, t0, T) {
    const f = Math.floor(t0 * 12), t = f / 12;
    c.fillStyle = "#e9e4d6"; c.fillRect(0, 0, W, H); c.fillStyle = "#cfc8b4"; c.fillRect(0, 400, W, 140);
    const bounce = Math.abs(Math.sin(t * 5)), sq = 1 + (1 - bounce) * .25;
    const x = 480, y = 400 - bounce * 90;
    c.fillStyle = "rgba(0,0,0,.25)"; c.beginPath(); c.ellipse(x, 412, 70 * (1 - bounce * .4), 12, 0, 0, TAU); c.fill();
    c.save(); c.translate(x, y); c.scale(sq, 1 / sq);
    c.strokeStyle = "#111"; c.lineWidth = 9; c.lineCap = "round"; const sw = Math.sin(t * 10) * 30;
    c.beginPath(); c.moveTo(-70, 0); c.bezierCurveTo(-130, -20, -150, -80 + sw, -120, -120 + sw); c.stroke(); c.beginPath(); c.moveTo(70, 0); c.bezierCurveTo(130, -20, 150, -80 - sw, 120, -120 - sw); c.stroke();
    c.beginPath(); c.moveTo(-30, 70); c.bezierCurveTo(-40, 110, -70 + sw * .5, 120, -80, 130); c.moveTo(30, 70); c.bezierCurveTo(40, 110, 70 - sw * .5, 120, 80, 130); c.stroke();
    pelota(c, 0, 0, 80, 0, "#f6f3ea", "#111", 5);
    c.fillStyle = "#fff"; c.beginPath(); c.ellipse(-24, -20, 18, 26, 0, 0, TAU); c.ellipse(24, -20, 18, 26, 0, 0, TAU); c.fill(); c.strokeStyle = "#111"; c.lineWidth = 3; c.stroke();
    c.fillStyle = "#111"; [-24, 24].forEach(ex => { c.beginPath(); c.moveTo(ex, -12); c.arc(ex, -12, 11, -1.1, Math.PI * 1.4); c.closePath(); c.fill() });
    c.beginPath(); c.lineWidth = 5; c.arc(0, 20, 30, .2, Math.PI - .2); c.stroke();
    [[-120, -120 + sw], [120, -120 - sw]].forEach(([gx, gy]) => { c.fillStyle = "#fff"; c.beginPath(); c.arc(gx, gy, 20, 0, TAU); c.fill(); c.lineWidth = 4; c.stroke() });
    c.restore();
    texto(c, "¡LA PELOTA", 480, 90, "62px Limelight", "#111", "center"); texto(c, `ENCONTRÓ A ${nombre1(T)}!`, 480, 150, "40px Limelight", "#111", "center");
    texto(c, `NÁPOLES · ${T.anio}`, 480, 500, "20px Limelight", "#333", "center");
    c.save(); c.globalAlpha = .5; c.drawImage(granoDe(f), 0, 0, W, H); c.restore(); vineta(c, .65, .3);
  } });

ESTILOS.push({ slug: "scifi-toon", nombre: "Comedia de ciencia ficción", dur: 8, poster: 4.4,
  que: "Dibujo animado de comedia de ciencia ficción: un portal verde que gira, un personaje que salta de un mundo a otro y colores ácidos.",
  uso: "Para el humor absurdo: «si Diego viajara en el tiempo», los universos paralelos de la final, comparaciones imposibles.",
  draw(c, t, T) {
    const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, "#3a1e6b"); g.addColorStop(1, "#7a3e9b"); c.fillStyle = g; c.fillRect(0, 0, W, H); estrellas(c, 60, t);
    c.fillStyle = "#4b2a2a"; poligono(c, [[0, 430], [W, 400], [W, H], [0, H]], "#5b3b2a");
    const pk = eb(seg(t, .3, 1.2)) * (1 - seg(t, 6.6, 7.4)); const px = 300, py = 280;
    if (pk > 0) { c.save(); c.translate(px, py); c.scale(pk, pk); for (let i = 0; i < 12; i++) { c.rotate(t * 1.5 + i * .5); c.fillStyle = i % 2 ? "#7dff4f" : "#2fd12f"; c.beginPath(); c.ellipse(0, 0, 130 - i * 9, 170 - i * 12, 0, 0, TAU); c.fill() } c.fillStyle = "#c6ff9a"; c.beginPath(); c.ellipse(0, 0, 30, 40, 0, 0, TAU); c.fill(); c.restore() }
    const k = eio(seg(t, 1.6, 3.4)); if (k > 0) { const x = lerp(px, 640, k), y = py - Math.sin(k * Math.PI) * 160 + k * 60, r = lerp(8, 1, 1 - k);
      c.save(); c.translate(x, y); c.rotate((1 - k) * 6); const s = lerp(.2, 1, k); c.scale(s, s); cabezaDiego(c, 0, -80, 46, "#f2c39b", "#2b1a0e", "#1a0a2a", 4);
      c.fillStyle = "#3d7cc9"; c.strokeStyle = "#1a0a2a"; c.lineWidth = 4; c.beginPath(); c.roundRect(-40, -30, 80, 100, 16); c.fill(); c.stroke(); texto(c, "10", 0, 34, "40px Fredoka", "#fff", "center"); c.restore() }
    if (t > 3.6) { const kk = eb(seg(t, 3.6, 4)); escala(c, 720, 140, kk, () => { caja(c, -170, -50, 340, 90, "#fff", "#1a0a2a", 4, 30); texto(c, "¿Esto es Nápoles?", 0, -4, "30px Fredoka", "#1a0a2a", "center"); texto(c, `Dimensión ${T.anio}-C`, 0, 26, "18px Fredoka", "#7a3e9b", "center") }) }
    if (t > 5) texto(c, T.cifra, 640, 500, "34px Fredoka", "#c6ff9a", "center");
  } });

ESTILOS.push({ slug: "dark-keynote", nombre: "Presentación de producto", dur: 8, poster: 6.4,
  que: "Presentación de lanzamiento tecnológico: fondo negro, frases cortas enormes con degradé, el «producto» flotando con reflejo y una ficha técnica que se completa.",
  uso: "Para presentar al equipo o a un jugador como si fuera un lanzamiento: «Argentina 86. Pro.». Ironía elegante.",
  draw(c, t, T) {
    c.fillStyle = "#000"; c.fillRect(0, 0, W, H);
    if (t < 2.6) { const k = eo(seg(t, .2, 1)) * (1 - seg(t, 2.2, 2.6)); c.globalAlpha = k; const g = c.createLinearGradient(200, 0, 760, 0); g.addColorStop(0, "#9fd2ff"); g.addColorStop(1, "#c79bff"); c.font = "700 110px 'IBM Plex Sans'"; c.textAlign = "center"; c.fillStyle = g; c.fillText(`${nombre1(T).charAt(0) + nombre1(T).slice(1).toLowerCase()}.`, W / 2, 260); c.font = "500 40px 'IBM Plex Sans'"; c.fillStyle = "#86868b"; c.fillText(`Edición ${T.anio}.`, W / 2, 330); c.globalAlpha = 1; return }
    const k = eo(seg(t, 2.6, 3.6)); const y = 270 + (1 - k) * 40 + Math.sin(t * 1.2) * 6;
    c.save(); c.globalAlpha = k; const im = recorteDuo("#0a0a0a", "#f5f5f7"); c.drawImage(IMG.rec, 160, y - 230, 275 * 1.05, 414 * 1.05);
    c.globalAlpha = .18 * k; c.translate(0, 2 * (y + 205)); c.scale(1, -1); c.drawImage(IMG.rec, 160, y - 230, 275 * 1.05, 414 * 1.05); c.restore();
    const fg = c.createLinearGradient(0, 440, 0, H); fg.addColorStop(0, "rgba(0,0,0,0)"); fg.addColorStop(.4, "#000"); c.fillStyle = fg; c.fillRect(0, 440, W, 100);
    const spec = [["Pie izquierdo", "Zurdo, de fábrica"], ["Precio", T.cifra], ["Destino", "S.S.C. Napoli"], ["Disponible", `julio de ${T.anio}`]];
    spec.forEach(([a, b], i) => { const kk = eo(seg(t, 3.6 + i * .5, 4.1 + i * .5)); c.globalAlpha = kk; texto(c, a, 540, 170 + i * 80, "500 18px 'IBM Plex Sans'", "#86868b"); texto(c, b, 540, 204 + i * 80, `600 ${tam(c, b, "'IBM Plex Sans'", 32, 380, 600)}px 'IBM Plex Sans'`, "#f5f5f7"); c.globalAlpha = 1 });
  } });

ESTILOS.push({ slug: "desktop-flythrough", nombre: "Recorrido por la app", dur: 8, poster: 5.6,
  que: "Una interfaz de escritorio flotando en perspectiva sobre una mesa: la cámara recorre las ventanas, el cursor hace clic y los datos se completan.",
  uso: "Para mostrar documentos y datos como si fueran software: la planilla de la AFA, el fixture del Mundial, el contrato del pase.",
  draw(c, t, T) {
    const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, "#d9d4cb"); g.addColorStop(1, "#b8b1a4"); c.fillStyle = g; c.fillRect(0, 0, W, H);
    const k = eio(seg(t, 0, 7)); c.save(); c.translate(W / 2, H / 2 + 20); c.transform(1, lerp(-.12, .02, k), lerp(.35, .05, k), 1, 0, 0); c.scale(lerp(.82, 1, k), lerp(.82, 1, k)); c.translate(-W / 2, -H / 2);
    sombra(c, 40, 30, .35); caja(c, 120, 60, 720, 420, "#fff", null, 0, 12); sinSombra(c);
    caja(c, 120, 60, 720, 36, "#f1f1f3", null, 0, 12); [["#ff5f57", 142], ["#febc2e", 162], ["#28c840", 182]].forEach(([col, x]) => { c.fillStyle = col; c.beginPath(); c.arc(x, 78, 6, 0, TAU); c.fill() }); texto(c, "Traspasos.app", 480, 84, "600 14px 'IBM Plex Sans'", "#333", "center");
    caja(c, 120, 96, 180, 384, "#f6f6f8"); ["Jugadores", "Clubes", "Contratos", "Pagos"].forEach((s, i) => { if (i === 2) caja(c, 130, 112 + i * 34, 160, 28, "#e3ecff", null, 0, 6); texto(c, s, 146, 132 + i * 34, "14px 'IBM Plex Sans'", "#333") });
    texto(c, "Contrato", 330, 140, "700 26px 'IBM Plex Sans'", "#111");
    const campos = [["Jugador", T.nombre], ["Desde", "F.C. Barcelona"], ["Hacia", "S.S.C. Napoli"], ["Monto", T.cifra], ["Fecha", `julio de ${T.anio}`]];
    campos.forEach(([a, b], i) => { const y = 180 + i * 46; texto(c, a, 330, y, "13px 'IBM Plex Sans'", "#888"); caja(c, 430, y - 20, 380, 30, "#fafafa", "#ddd", 1, 6); texto(c, tipeo(b, seg(t, .6 + i * .5, 1.1 + i * .5)), 442, y, "15px 'IBM Plex Sans'", "#111") });
    const ok = t > 4.6; caja(c, 650, 420, 160, 40, ok ? "#28a745" : "#0a64ff", null, 0, 8); texto(c, ok ? "✓ Firmado" : "Firmar", 730, 446, "600 16px 'IBM Plex Sans'", "#fff", "center");
    const cx = t < 4.2 ? lerp(500, 720, eio(seg(t, 2.8, 4.2))) : 720, cy = t < 4.2 ? lerp(300, 440, eio(seg(t, 2.8, 4.2))) : 440; const cs = t > 4.3 && t < 4.5 ? .85 : 1;
    c.save(); c.translate(cx, cy); c.scale(cs, cs); poligono(c, [[0, 0], [0, 22], [6, 17], [11, 27], [15, 25], [10, 16], [18, 16]], "#111", "#fff", 1.5); c.restore();
    c.restore();
  } });

ESTILOS.push({ slug: "hologram-hud", nombre: "Holograma de ciencia ficción", dur: 8, poster: 5.6,
  que: "Hologramas cian que flotan en la oscuridad: una pelota en malla de alambre que gira, anillos de datos y la foto proyectada con líneas de escaneo.",
  uso: "Para fichas técnicas futuristas: las estadísticas de Diego en el Mundial, la comparación con Pelé, el análisis de un gol.",
  draw(c, t, T) {
    c.fillStyle = "#01070d"; c.fillRect(0, 0, W, H); const C = "#46e6ff";
    const cx = 300, cy = 270, R = 130; const pts = proc("holo-ico", () => { const o = []; for (let i = 0; i < 160; i++) { const y = 1 - 2 * (i + .5) / 160, r = Math.sqrt(1 - y * y), a = i * 2.39996; o.push([Math.cos(a) * r, y, Math.sin(a) * r]) } return o });
    const a = t * .8; c.strokeStyle = "rgba(70,230,255,.35)"; c.lineWidth = 1; const pr = pts.map(([x, y, z]) => { const X = x * Math.cos(a) + z * Math.sin(a), Z = -x * Math.sin(a) + z * Math.cos(a); return [cx + X * R, cy + y * R, Z] });
    for (let i = 0; i < pr.length; i++) for (let j = i + 1; j < Math.min(pr.length, i + 14); j++) { const d = Math.hypot(pr[i][0] - pr[j][0], pr[i][1] - pr[j][1]); if (d < 34) { c.globalAlpha = .3 + .4 * (pr[i][2] + 1) / 2; c.beginPath(); c.moveTo(pr[i][0], pr[i][1]); c.lineTo(pr[j][0], pr[j][1]); c.stroke() } }
    c.globalAlpha = 1; pr.forEach(p => { c.fillStyle = C; c.fillRect(p[0] - 1, p[1] - 1, 2, 2) });
    c.save(); c.strokeStyle = C; brillo(c, C, 10); c.lineWidth = 2; for (let i = 0; i < 3; i++) { c.beginPath(); c.arc(cx, cy, R + 30 + i * 16, t * (i % 2 ? -1 : 1) + i, t * (i % 2 ? -1 : 1) + i + 2.4); c.stroke() } c.restore();
    const kf = seg(t, 1.6, 3.2); if (kf > 0) { const im = proc("holo-f", () => duotono(IMG.fotografos, "#001018", "#8ff3ff", 300, 300, 330, 40, 300, 300)); c.save(); c.globalAlpha = .85; c.globalCompositeOperation = "lighter"; c.beginPath(); c.rect(580, 70, 300, 300 * kf); c.clip(); c.drawImage(im, 580, 70); c.restore(); lineasScan(c, 0, 3);
      c.fillStyle = "rgba(1,7,13,.25)"; for (let y = 70; y < 370; y += 3) c.fillRect(580, y, 300, 1); c.strokeStyle = C; c.lineWidth = 1.5; c.strokeRect(580, 70, 300, 300) }
    const datos = [["ID", apellido(T)], ["CLUB", "S.S.C. NAPOLI"], ["VALOR", T.cifra], ["AÑO", T.anio]];
    datos.forEach(([k2, v], i) => { const kk = seg(t, 3 + i * .4, 3.4 + i * .4); if (kk <= 0) return; c.globalAlpha = kk; texto(c, k2, 580, 410 + i * 30, "12px 'Space Mono'", "rgba(70,230,255,.6)"); texto(c, v, 680, 410 + i * 30, "16px 'Space Mono'", "#cffaff"); c.globalAlpha = 1 });
    c.save(); c.globalAlpha = .06 + Math.random() * 0; c.fillStyle = C; c.fillRect(0, (t * 140) % H, W, 2); c.restore();
  } });

ESTILOS.push({ slug: "living-screencast", nombre: "Tutorial con mascota", dur: 8, poster: 5,
  que: "Un tutorial de pantalla con una mascota que te guía: el cursor llena un formulario, aparecen globos de ayuda y la mascota festeja cada paso.",
  uso: "Para explicar trámites o reglas en clave simpática: cómo se inscribía la lista, cómo se compraba una entrada en 1986.",
  draw(c, t, T) {
    c.fillStyle = "#eef1f6"; c.fillRect(0, 0, W, H); caja(c, 60, 40, 700, 460, "#fff", "#d5dbe5", 1.5, 12); caja(c, 60, 40, 700, 40, "#f4f6fa", null, 0, 12); caja(c, 80, 50, 400, 22, "#fff", "#d5dbe5", 1, 11); texto(c, "traspasos.napoli/alta", 94, 66, "13px 'IBM Plex Sans'", "#666");
    texto(c, "Alta de jugador", 100, 130, "700 28px 'IBM Plex Sans'", "#1d2b4a");
    const campos = [["Nombre", T.nombre], ["Club de origen", "F.C. Barcelona"], ["Monto", T.cifra]];
    campos.forEach(([a, b], i) => { const y = 180 + i * 80; texto(c, a, 100, y, "600 14px 'IBM Plex Sans'", "#53607a"); const act = Math.floor((t - .5) / 1.3) === i; caja(c, 100, y + 10, 420, 40, "#fff", act ? "#4f7cff" : "#d5dbe5", act ? 2.5 : 1.5, 8); texto(c, tipeo(b, seg(t, .5 + i * 1.3, 1.5 + i * 1.3)), 114, y + 37, "16px 'IBM Plex Sans'", "#111") });
    const listo = t > 4.6; caja(c, 100, 420, 200, 46, listo ? "#22b07d" : "#4f7cff", null, 0, 10); texto(c, listo ? "¡Listo!" : "Enviar", 200, 450, "700 17px 'IBM Plex Sans'", "#fff", "center");
    const mx = 830, my = 380 + Math.sin(t * 4) * 6; pelota(c, mx, my, 50, Math.sin(t * 2) * .3, "#fff", "#1d2b4a", 3);
    c.fillStyle = "#fff"; c.beginPath(); c.arc(mx - 16, my - 6, 12, 0, TAU); c.arc(mx + 16, my - 6, 12, 0, TAU); c.fill(); c.fillStyle = "#1d2b4a"; c.beginPath(); c.arc(mx - 14, my - 4, 5, 0, TAU); c.arc(mx + 18, my - 4, 5, 0, TAU); c.fill();
    const tips = ["¡Hola! Te ayudo a dar el alta.", "Ahora el club de origen.", "¿El monto? ¡Récord!", "Ahora apretá Enviar.", `¡Bienvenido a Nápoles, ${T.anio}!`]; const ti = Math.min(4, Math.floor(t / 1.25));
    c.font = "15px 'IBM Plex Sans'"; const tw = c.measureText(tips[ti]).width + 28; caja(c, 920 - tw, 250, tw, 50, "#1d2b4a", null, 0, 12); texto(c, tips[ti], 920 - tw + 14, 281, "15px 'IBM Plex Sans'", "#fff");
    const cur = [[300, 230], [300, 310], [300, 390], [200, 444], [200, 444]][ti]; poligono(c, [[cur[0], cur[1]], [cur[0], cur[1] + 22], [cur[0] + 6, cur[1] + 17], [cur[0] + 11, cur[1] + 27], [cur[0] + 15, cur[1] + 25], [cur[0] + 10, cur[1] + 16], [cur[0] + 18, cur[1] + 16]], "#111", "#fff", 1.5);
  } });

ESTILOS.push({ slug: "one-bit-dither", nombre: "Tramado de 1 bit", dur: 8, poster: 3,
  que: "Solo dos tintas, sin grises: todo es un patrón de puntos ordenado. Transiciones como un fax que escanea renglón por renglón y una inversión en el golpe.",
  uso: "Para archivo y misterio: telegramas de 1986, una foto que llega por fax a la redacción, la noticia que cruza el océano.",
  draw(c, t, T) {
    const P = "#e9e6d6", N = "#16161a";
    const a = proc("1b-a", () => difuminado(IMG.brazos, N, 480, 270, 0, 0, 960, 540)), b = proc("1b-b", () => difuminado(IMG.fotografos, N, 480, 270, 80, 0, 880, 495));
    c.fillStyle = P; c.fillRect(0, 0, W, H); c.save(); c.imageSmoothingEnabled = false;
    const z = 1 + t * .02; c.drawImage(a, 0, 0, 480, 270, (W - W * z) / 2, (H - H * z) / 2, W * z, H * z);
    const ks = seg(t, 3.2, 5.2); if (ks > 0) { const y = H * ks; c.beginPath(); c.rect(0, 0, W, y); c.save(); c.clip(); c.fillStyle = P; c.fillRect(0, 0, W, y); c.drawImage(b, 0, 0, W, H); c.restore(); c.fillStyle = N; c.fillRect(0, y, W, 4); c.fillStyle = P; c.fillRect(0, y + 4, W, 2) }
    c.restore();
    if (t > 5.6 && t < 5.75) { c.globalCompositeOperation = "difference"; c.fillStyle = "#fff"; c.fillRect(0, 0, W, H); c.globalCompositeOperation = "source-over" }
    caja(c, 20, H - 60, 420, 40, P, N, 2); texto(c, `FAX · NÁPOLES → BS. AS. · ${T.anio}`, 34, H - 33, "18px VT323", N);
    if (t > 5.8) { caja(c, W - 360, 20, 340, 70, N); texto(c, apellido(T), W - 190, 66, "40px VT323", P, "center") }
  } });

ESTILOS.push({ slug: "spreadsheet", nombre: "Película de planilla", dur: 8, poster: 6.4,
  que: "Una planilla de cálculo que cuenta la historia: celdas que se llenan, una fórmula que encuentra el dato y un gráfico que brota de las columnas.",
  uso: "Para las estadísticas con ironía: goles por partido, minutos jugados, tarjetas. Es un lenguaje que todos reconocen.",
  draw(c, t, T) {
    c.fillStyle = "#fff"; c.fillRect(0, 0, W, H); caja(c, 0, 0, W, 34, "#1d6f42"); texto(c, "Pases_de_Diego.xlsx", 16, 23, "600 14px 'IBM Plex Sans'", "#fff");
    caja(c, 0, 34, W, 32, "#f3f3f3", "#ddd", 1); texto(c, "fx", 14, 56, "italic 14px 'IBM Plex Sans'", "#777"); const fx = t > 3 ? `=INDICE(A2:D5; COINCIDIR(MAX(D2:D5)))` : ""; texto(c, tipeo(fx, seg(t, 3, 4)), 46, 56, "14px 'Space Mono'", "#222");
    const cols = [60, 110, 300, 520, 760]; const filas = [["Año", "Club", "Tipo", "Monto"], ["1976", "Argentinos Juniors", "debut", "—"], ["1981", "Boca Juniors", "préstamo", "—"], ["1982", "F.C. Barcelona", "récord mundial", "récord"], [T.anio, "S.S.C. Napoli", "récord mundial", T.cifra]];
    for (let j = 0; j <= 6; j++) { const y = 66 + j * 34; c.strokeStyle = "#e1e1e1"; c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke(); caja(c, 0, y, 60, 34, "#f6f6f6", "#e1e1e1", 1); texto(c, String(j + 1), 30, y + 22, "12px 'IBM Plex Sans'", "#888", "center") }
    cols.forEach(x => { c.strokeStyle = "#e1e1e1"; c.beginPath(); c.moveTo(x, 66); c.lineTo(x, 304); c.stroke() });
    filas.forEach((f, j) => f.forEach((v, i) => { const k = seg(t, .2 + j * .45 + i * .08, .5 + j * .45 + i * .08); if (k <= 0) return; texto(c, tipeo(v, k), cols[i] + 8, 66 + j * 34 + 22, `${j === 0 ? "600 " : ""}14px 'IBM Plex Sans'`, "#222") }));
    if (t > 4) { const k = Math.floor(t * 4) % 2; caja(c, 60, 66 + 4 * 34, 900, 34, k ? "rgba(255,213,0,.35)" : "rgba(255,213,0,.2)"); c.strokeStyle = "#1d6f42"; c.lineWidth = 2.5; c.strokeRect(760, 66 + 4 * 34, 200, 34) }
    const kb = eo(seg(t, 4.6, 5.4)); if (kb > 0) { c.globalAlpha = kb; caja(c, 80, 340, 800, 150, "#f3faf5", "#1d6f42", 2, 6); texto(c, "=CONTAR.SI(C2:C5; \"récord mundial\")", 104, 380, "15px 'Space Mono'", "#1d6f42"); texto(c, "2", 104, 460, "700 64px 'IBM Plex Sans'", "#1d6f42"); texto(c, "pases récord mundial en dos años", 170, 452, "20px 'IBM Plex Sans'", "#333"); c.globalAlpha = 1 }
  } });

ESTILOS.push({ slug: "game-show", nombre: "Programa de preguntas", dur: 8, poster: 6,
  que: "Un programa de preguntas en un estudio con luces: la pregunta en pantalla, cuatro opciones, la cuenta regresiva y la respuesta correcta que se enciende.",
  uso: "Para trivia y participación: «¿cuántos goles hizo Diego en México?», preguntas para comentar al final del video.",
  draw(c, t, T) {
    const g = c.createRadialGradient(W / 2, 120, 50, W / 2, 200, 700); g.addColorStop(0, "#3b1a8a"); g.addColorStop(1, "#0b0624"); c.fillStyle = g; c.fillRect(0, 0, W, H);
    for (let i = 0; i < 9; i++) { const a = -1 + i * .25 + Math.sin(t * 1.5 + i) * .1; c.save(); c.translate(W / 2, -40); c.rotate(a); const gr = c.createLinearGradient(0, 0, 0, 600); gr.addColorStop(0, "rgba(255,240,180,.25)"); gr.addColorStop(1, "rgba(255,240,180,0)"); c.fillStyle = gr; c.beginPath(); c.moveTo(-14, 0); c.lineTo(14, 0); c.lineTo(80, 600); c.lineTo(-80, 600); c.fill(); c.restore() }
    const kq = eb(seg(t, .2, .7)); escala(c, W / 2, 110, kq, () => { caja(c, -400, -46, 800, 92, "#0b0624", "#ffcc33", 4, 46); texto(c, `¿Cuánto pagó el Napoli por ${nombre1(T).charAt(0) + nombre1(T).slice(1).toLowerCase()} en ${T.anio}?`, 0, 10, `600 ${tam(c, `¿Cuánto pagó el Napoli por Diego en ${T.anio}?`, "'IBM Plex Sans'", 28, 740, 600)}px 'IBM Plex Sans'`, "#fff", "center") });
    const ops = ["US$ 1.000.000", "US$ 3.000.000", T.cifra, "US$ 12.000.000"]; const cor = 2, rev = t > 5.2;
    ops.forEach((o, i) => { const k = eo(seg(t, .8 + i * .25, 1.2 + i * .25)); if (k <= 0) return; const x = i % 2 ? 500 : 80, y = 220 + Math.floor(i / 2) * 100; c.globalAlpha = k;
      const col = rev ? (i === cor ? "#1fbf5f" : "#2a1b5c") : (t > 4.2 && i === cor && Math.floor(t * 6) % 2 ? "#ff9f1c" : "#2a1b5c");
      caja(c, x, y, 380, 70, col, "#ffcc33", 3, 35); texto(c, "ABCD"[i] + ":", x + 30, y + 45, "700 24px 'IBM Plex Sans'", "#ffcc33"); texto(c, o, x + 80, y + 45, `600 ${tam(c, o, "'IBM Plex Sans'", 26, 280, 600)}px 'IBM Plex Sans'`, "#fff"); c.globalAlpha = 1 });
    const tiempo = Math.max(0, Math.ceil(5 - t)); if (t < 5.2) { c.fillStyle = "#ffcc33"; c.beginPath(); c.arc(W / 2, 470, 34, 0, TAU); c.fill(); texto(c, String(tiempo), W / 2, 484, "700 36px 'IBM Plex Sans'", "#0b0624", "center") }
    else { texto(c, "¡CORRECTO!", W / 2, 490, "64px Bangers", "#1fbf5f", "center") }
  } });

ESTILOS.push({ slug: "hd-2d", nombre: "Pixel art con profundidad", dur: 8, poster: 5.4,
  que: "Pixel art dentro de un mundo con luz y profundidad: el fondo y el frente desenfocados, brillos que flotan y un cuadro de diálogo de videojuego.",
  uso: "Para recrear escenas con ternura de videojuego: la llegada al estadio, la noche antes de la final, la vuelta olímpica.",
  draw(c, t, T) {
    const px = proc("hd-px", () => chico(IMG.jueguitos, 240, 135));
    c.save(); c.imageSmoothingEnabled = false; c.drawImage(px, 0, 0, W, H); c.restore();
    const lejos = proc("hd-bl", () => borroso(chico(IMG.jueguitos, 240, 135), 3)); c.save(); c.globalAlpha = .9; c.beginPath(); c.rect(0, 0, W, 150); c.clip(); c.drawImage(lejos, 0, 0, W, H); c.restore();
    c.save(); c.globalAlpha = .9; c.beginPath(); c.rect(0, 440, W, 100); c.clip(); c.drawImage(lejos, 0, 0, W, H); c.restore();
    const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, "rgba(255,190,110,.35)"); g.addColorStop(.5, "rgba(255,190,110,0)"); g.addColorStop(1, "rgba(40,20,80,.35)"); c.fillStyle = g; c.fillRect(0, 0, W, H);
    c.globalCompositeOperation = "lighter"; for (let i = 0; i < 40; i++) { const x = (rnd(i) * W + t * 20 * (rnd(i + 3) - .3)) % W, y = (rnd(i + 5) * H - t * 30 * rnd(i + 7) + H) % H; c.fillStyle = `rgba(255,220,140,${.4 * Math.abs(Math.sin(t * 2 + i))})`; c.fillRect(Math.floor(x / 4) * 4, Math.floor(y / 4) * 4, 4, 4) } c.globalCompositeOperation = "source-over";
    if (t > 1.4) { caja(c, 120, 380, 720, 130, "rgba(16,20,48,.92)", "#e8e2c8", 4, 8); texto(c, apellido(T), 146, 414, "14px 'Press Start 2P'", "#ffd27a"); texto(c, tipeo("¡Nápoles, ya llegué!", seg(t, 1.6, 3.4)), 146, 452, "16px 'Press Start 2P'", "#fff"); if (t > 3.6) texto(c, tipeo(`(${T.cifra} · ${T.anio})`, seg(t, 3.6, 5)), 146, 486, "12px 'Press Start 2P'", "#9fb3ff"); if (Math.floor(t * 2) % 2) texto(c, "▼", 810, 494, "14px 'Press Start 2P'", "#fff") }
  } });

ESTILOS.push({ slug: "microgame", nombre: "Microjuegos frenéticos", dur: 8, poster: 1.3,
  que: "Una seguidilla de minijuegos de tres segundos con una orden a los gritos («¡PATEÁ!», «¡FIRMÁ!»), una bomba con mecha y colores saturados.",
  uso: "Para recaps rápidos y humor: «los 7 partidos en 30 segundos», un repaso a mil por hora antes del final.",
  draw(c, t, T) {
    const i = Math.min(2, Math.floor(t / 2.6)), l = (t % 2.6) / 2.6; const fondos = ["#ff3d7f", "#2bd9fe", "#ffd23f"]; c.fillStyle = fondos[i]; c.fillRect(0, 0, W, H);
    for (let k = 0; k < 12; k++) { c.fillStyle = "rgba(255,255,255,.18)"; c.save(); c.translate(W / 2, H / 2); c.rotate(k / 12 * TAU + t); c.fillRect(0, -20, 700, 40); c.restore() }
    const orden = ["¡PATEÁ!", "¡FIRMÁ!", "¡FESTEJÁ!"][i]; const ko = eb(seg(l, 0, .15)); escala(c, W / 2, 110, ko, () => { c.font = "92px Bangers"; c.textAlign = "center"; c.lineWidth = 12; c.strokeStyle = "#111"; c.strokeText(orden, 0, 30); c.fillStyle = "#fff"; c.fillText(orden, 0, 30) });
    if (i === 0) { caja(c, 680, 200, 200, 200, null, "#111", 8); const bx = lerp(200, 760, eio(seg(l, .3, .7))), by = 380 - Math.sin(seg(l, .3, .7) * Math.PI) * 160; pelota(c, bx, by, 34, l * 12, "#fff", "#111", 4) }
    if (i === 1) { caja(c, 260, 200, 440, 260, "#fff", "#111", 6, 8); texto(c, "CONTRATO", 480, 250, "40px Bangers", "#111", "center"); texto(c, T.cifra, 480, 300, "30px Bangers", "#d62828", "center"); c.strokeStyle = "#111"; c.lineWidth = 4; const pts = []; for (let k = 0; k <= 40; k++) pts.push([320 + k * 8, 400 + Math.sin(k * .8) * 16]); trazo(c, pts, seg(l, .3, .8)) }
    if (i === 2) { cabezaDiego(c, 480, 330, 90); for (let k = 0; k < 20; k++) { c.fillStyle = ["#d62828", "#1e7bd6", "#fff", "#111"][k % 4]; c.save(); c.translate(rnd(k) * W, (rnd(k + 9) * H + l * 400) % H); c.rotate(l * 8 + k); c.fillRect(-6, -10, 12, 20); c.restore() } texto(c, T.anio, 480, 500, "48px Bangers", "#111", "center") }
    const mecha = 1 - l; c.fillStyle = "#111"; c.beginPath(); c.arc(70, H - 60, 30, 0, TAU); c.fill(); c.strokeStyle = "#7a5a2a"; c.lineWidth = 6; c.beginPath(); c.moveTo(90, H - 80); c.lineTo(90 + mecha * 780, H - 80); c.stroke(); c.fillStyle = "#ffb000"; c.beginPath(); c.arc(90 + mecha * 780, H - 80, 8 + Math.random() * 0, 0, TAU); c.fill();
  } });

ESTILOS.push({ slug: "pixel-rpg", nombre: "Juego de rol de 16 bits", dur: 8, poster: 5.6,
  que: "Un juego de rol de 16 bits: mapa de baldosas, un personaje en pixeles que camina hasta el castillo, cuadros de diálogo y «¡objeto obtenido!».",
  uso: "Para recaps nostálgicos y logros: «Argentina pasó de fase», la lista de rivales como jefes finales, el álbum de figuritas.",
  draw(c, t, T) {
    const B = proc("rpg-b", () => lienzo(240, 135)); const x = B.getContext("2d"); x.imageSmoothingEnabled = false;
    for (let j = 0; j < 135; j += 8) for (let i = 0; i < 240; i += 8) { x.fillStyle = (i + j) % 16 ? "#4caf50" : "#45a049"; x.fillRect(i, j, 8, 8); if (rnd(i * 7 + j) > .86) { x.fillStyle = "#2e7d32"; x.fillRect(i + 2, j + 3, 2, 2); x.fillRect(i + 5, j + 1, 1, 2) } }
    x.fillStyle = "#c8a46a"; x.fillRect(0, 72, 240, 12); for (let i = 0; i < 240; i += 6) { x.fillStyle = "#b8945a"; x.fillRect(i, 74, 3, 1) }
    x.fillStyle = "#9e9e9e"; x.fillRect(186, 30, 44, 42); x.fillStyle = "#757575"; for (let i = 0; i < 5; i++) x.fillRect(186 + i * 10, 24, 6, 6); x.fillStyle = "#1565c0"; x.fillRect(202, 52, 12, 20); x.fillStyle = "#fff"; x.fillRect(196, 14, 1, 16); x.fillStyle = "#29b6f6"; x.fillRect(197, 14, 10, 6);
    const k = seg(t, .4, 4), px = Math.floor(lerp(10, 192, k)), paso = Math.floor(t * 8) % 2 && k < 1;
    x.fillStyle = "#1d140e"; x.fillRect(px + 1, 60, 8, 4); x.fillStyle = "#e0a77a"; x.fillRect(px + 2, 63, 6, 5); x.fillStyle = "#29b6f6"; x.fillRect(px + 1, 68, 8, 6); x.fillStyle = "#fff"; x.fillRect(px + 2, 74, 6, 3); x.fillStyle = "#111"; x.fillRect(px + 2 + (paso ? 1 : 0), 77, 2, 3); x.fillRect(px + 6 - (paso ? 1 : 0), 77, 2, 3);
    c.save(); c.imageSmoothingEnabled = false; c.drawImage(B, 0, 0, W, H); c.restore();
    texto(c, "NÁPOLES", 832, 100, "14px 'Press Start 2P'", "#fff", "center");
    if (t > 4.2) { caja(c, 40, 360, 880, 150, "#0d1b6b", "#fff", 6, 10); const s = t < 6 ? `¡${nombre1(T)} se unió al equipo!` : `¡Obtuviste ${T.cifra}!`; texto(c, tipeo(s, seg(t, t < 6 ? 4.2 : 6, t < 6 ? 5.4 : 7)), 70, 420, "18px 'Press Start 2P'", "#fff"); texto(c, `NIVEL ${T.anio}`, 70, 470, "12px 'Press Start 2P'", "#ffd54f"); if (Math.floor(t * 3) % 2) texto(c, "▶", 880, 488, "16px 'Press Start 2P'", "#fff") }
  } });
