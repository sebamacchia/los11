"""Escribe compositions/pizarra.html: el cambio táctico del entretiempo (escena 28 del guion de Estambul).

Los tiempos salen de la voz de la escena (transcripción palabra por palabra):
  "entra Hamann" 0.88 s · "tres defensores" 4.81 s · "Gerrard queda más libre" 5.95 s · "hacer un gol" 10.72 s
Volver a correr este script después de cambiar posiciones o tiempos: `python3 generar.py`.
"""
from pathlib import Path

W, H = 1050, 680  # cancha en unidades SVG (largo x ancho)


def P(x, y):
    return round(x / 100 * W, 1), round(y / 100 * H, 1)


# id, número, nombre, posición al empezar (primer tiempo), posición final (segundo tiempo)
JUGADORES = [
    ("dudek", 1, "Dudek", (5, 50), None),
    ("traore", 21, "Traoré", (22, 14), (20, 28)),
    ("carragher", 23, "Carragher", (20, 40), (18, 50)),
    ("hyypia", 4, "Hyypiä", (20, 62), (20, 72)),
    ("finnan", 3, "Finnan", (22, 88), (22, 120)),
    ("riise", 6, "Riise", (46, 12), None),
    ("smicer", 11, "Smicer", (46, 88), None),
    ("alonso", 14, "Alonso", (38, 40), None),
    ("hamann", 16, "Hamann", (36, 120), (36, 62)),
    ("gerrard", 8, "Gerrard", (44, 58), (64, 36)),
    ("garcia", 10, "García", (64, 66), None),
    ("baros", 5, "Baroš", (82, 50), None),
]

franjas = "".join(f'<rect x="{k * W / 10}" y="0" width="{W / 10}" height="{H}" fill="{"#1f6b38" if k % 2 else "#23763e"}"/>'
                  for k in range(10))
L = 'fill="none" stroke="rgba(255,255,255,.6)" stroke-width="4"'
lineas = (f'<rect x="0" y="0" width="{W}" height="{H}" {L}/><line x1="{W/2}" y1="0" x2="{W/2}" y2="{H}" {L}/>'
          f'<circle cx="{W/2}" cy="{H/2}" r="90" {L}/>'
          f'<rect x="0" y="{H/2-200}" width="165" height="400" {L}/><rect x="0" y="{H/2-90}" width="55" height="180" {L}/>'
          f'<rect id="pz-area" x="{W-165}" y="{H/2-200}" width="165" height="400" {L}/>'
          f'<rect x="{W-55}" y="{H/2-90}" width="55" height="180" {L}/>')

jugadores = ""
for jid, num, nombre, ini, fin in JUGADORES:
    anillo = ""
    if jid == "hamann":
        anillo = '<circle class="anillo" cx="0" cy="0" r="42" fill="none" stroke="#c8e6c8" stroke-width="5"/>'
    if jid == "finnan":
        anillo = '<circle class="anillo" cx="0" cy="0" r="42" fill="none" stroke="#ff4d4d" stroke-width="5"/>'
    if jid == "gerrard":
        anillo = '<circle class="anillo" cx="0" cy="0" r="42" fill="none" stroke="#7ab37a" stroke-width="5"/>'
    x0, y0 = P(*ini)
    jugadores += (f'<g transform="translate({x0} {y0})"><g id="pz-{jid}"><g class="cuerpo">{anillo}'
                  f'<circle cx="0" cy="0" r="29" fill="#c8102e" stroke="#fff" stroke-width="4"/>'
                  f'<text x="0" y="10" text-anchor="middle" font-size="24" fill="#fff">{num}</text>'
                  f'<text x="0" y="66" text-anchor="middle" font-size="25" fill="#fff" class="nombre">{nombre}</text>'
                  f'</g></g></g>')

tx, ty = P(20, 28); cx_, cy_ = P(18, 50); hx, hy = P(20, 72)
gx0, gy0 = P(44, 58); gx1, gy1 = P(64, 36); ax1, ay1 = P(97, 50)
trazos = (f'<polyline id="pz-linea3" points="{tx},{ty} {cx_},{cy_} {hx},{hy}" fill="none" stroke="#7ab37a" stroke-width="7" '
          f'stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="600" stroke-dashoffset="600"/>'
          f'<line id="pz-estela" x1="{gx0}" y1="{gy0}" x2="{gx1}" y2="{gy1}" stroke="#7ab37a" stroke-width="6" stroke-dasharray="14 12"/>'
          f'<path id="pz-flecha" d="M{gx1 + 30},{gy1 + 10} Q{(gx1 + ax1) / 2},{gy1 - 40} {ax1},{ay1}" fill="none" stroke="#7ab37a" '
          f'stroke-width="9" stroke-linecap="round" stroke-dasharray="520" stroke-dashoffset="520" data-layout-ignore marker-end="url(#pz-punta)"/>')

js_pos = []
js_mov = []
for jid, num, nombre, ini, fin in JUGADORES:
    x0, y0 = P(*ini)
    if fin:
        x1, y1 = P(*fin)
        cuando = {"finnan": (1.10, 0.6, "power3.in"), "hamann": (1.15, 0.9, "expo.out"),
                  "traore": (4.81, 0.7, "power2.inOut"), "carragher": (4.85, 0.7, "power2.inOut"),
                  "hyypia": (4.89, 0.7, "power2.inOut"), "gerrard": (5.95, 0.85, "power3.out")}[jid]
        js_mov.append(f'tl.to("#pz-{jid}", {{ x: {round(x1 - x0, 1)}, y: {round(y1 - y0, 1)}, duration: {cuando[1]}, ease: "{cuando[2]}" }}, {cuando[0]});')

HTML = f'''<template>
  <style>
    @font-face {{ font-family: "Mono"; src: url("assets/fonts/jetbrains-mono.ttf"); font-weight: 100 800; }}
    @font-face {{ font-family: "Plex"; src: url("assets/fonts/plex-sans.ttf"); font-weight: 100 700; }}
    #root {{ position: absolute; inset: 0; overflow: hidden; color: #f2efe8; font-family: "Mono"; font-weight: 700;
      background: radial-gradient(ellipse at 62% 55%, #2d4a2d 0%, #1a2e1a 70%); }}
    #pz-logo {{ position: absolute; left: 96px; top: 70px; font: 700 28px "Mono"; letter-spacing: 1px;
      border-left: 8px solid #7ab37a; padding-left: 14px; }}
    #pz-etq {{ position: absolute; left: 96px; top: 134px; font: 500 24px "Mono"; letter-spacing: 4px; color: #7ab37a; }}
    #pz-tit {{ position: absolute; left: 94px; top: 176px; font: 700 92px/0.98 "Mono"; }}
    #pz-tit span {{ display: inline-block; }}
    #pz-ley {{ position: absolute; left: 96px; top: 330px; width: 500px; font: 500 30px/1.2 "Plex"; }}
    #pz-ley div {{ margin-bottom: 18px; padding-left: 38px; text-indent: -38px; }}
    #pz-ley b {{ display: inline-block; width: 22px; height: 22px; border-radius: 50%; margin-right: 16px; vertical-align: 2px; }}
    #pz-form {{ position: absolute; left: 96px; bottom: 96px; font: 700 52px "Mono"; color: #7ab37a; white-space: nowrap; }}
    #pz-form span {{ display: inline-block; }}
    #pz-form .gris {{ color: rgba(242,239,232,.5); }}
    #pz-f3 {{ color: #c8e6c8; }}
    #pz-mesa {{ position: absolute; left: 640px; top: 175px; width: 1260px; height: 900px;
      transform: perspective(1900px) rotateX(32deg) scale(1.02); transform-origin: 50% 40%; }}
    #pz-campo {{ width: 100%; height: 100%; }}
    #pz-campo svg {{ filter: drop-shadow(0 40px 50px rgba(0,0,0,.6)); }}
    .anillo, #pz-flecha, #pz-estela, #pz-f2, #pz-f3, #pz-ley div, #pz-orden {{ opacity: 0; }}
    #pz-orden {{ position: absolute; left: 96px; top: 700px; width: 480px; }}
    #pz-orden small {{ display: block; font: 500 22px "Mono"; letter-spacing: 3px; color: #7ab37a; margin-bottom: 10px; }}
    #pz-orden p {{ font: 600 40px/1.1 "Plex"; }}
    .nombre {{ paint-order: stroke; stroke: #1a2e1a; stroke-width: 7px; }}
  </style>
  <div id="root" data-composition-id="pizarra" data-width="1920" data-height="1080">
    <div id="pz-logo">LOS 11</div>
    <div id="pz-etq">EL ENTRETIEMPO — LA JUGADA DE BENÍTEZ</div>
    <div id="pz-tit"><span>TRES</span> <span>ATRÁS</span></div>
    <div id="pz-ley">
      <div id="pz-l1"><b style="background:#ff4d4d"></b>Sale Finnan, lesionado</div>
      <div id="pz-l2"><b style="background:#c8e6c8"></b>Entra Hamann, al medio</div>
      <div id="pz-l3"><b style="background:#7ab37a"></b>Tres atrás: Traoré, Carragher y Hyypiä</div>
      <div id="pz-l4"><b style="background:#7ab37a"></b>Gerrard, más libre para atacar</div>
    </div>
    <div id="pz-orden"><small>LA ORDEN DE BENÍTEZ</small><p>«Un gol rápido...<br>y ver qué pasa»</p></div>
    <div id="pz-form"><span id="pz-f1">4-4-1-1</span><span id="pz-f2" class="gris">&nbsp;→&nbsp;</span><span id="pz-f3">3-4-2-1</span></div>
    <div id="pz-mesa" data-layout-allow-overflow><div id="pz-campo">
      <svg viewBox="-70 -50 {W + 140} {H + 170}" width="1260" height="900" font-family="Mono" font-weight="700">
        <defs><marker id="pz-punta" markerWidth="4" markerHeight="4" refX="2" refY="2" orient="auto">
          <path d="M0,0 L4,2 L0,4 z" fill="#7ab37a"/></marker></defs>
        {franjas}{lineas}{trazos}{jugadores}
      </svg>
    </div></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    // entrada de la cancha, el título y los jugadores
    tl.fromTo("#pz-campo", {{ opacity: 0.35, y: 70, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.7, ease: "expo.out" }}, 0);
    tl.fromTo("#pz-logo, #pz-etq", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power2.out" }}, 0.05);
    tl.fromTo("#pz-tit span", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power4.out", stagger: 0.08 }}, 0.15);
    tl.fromTo(".cuerpo", {{ scale: 0, transformOrigin: "50% 30%" }}, {{ scale: 1, duration: 0.45, ease: "back.out(1.4)", stagger: 0.035 }}, 0.4);
    tl.fromTo("#pz-f1", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, 0.6);
    // "entra Hamann": sale Finnan, entra Hamann
    tl.to("#pz-finnan .anillo", {{ opacity: 1, duration: 0.15 }}, 0.88);
    tl.fromTo("#pz-l1", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "expo.out" }}, 0.9);
    tl.to("#pz-finnan", {{ opacity: 0, duration: 0.45, ease: "power2.in" }}, 1.25);
    tl.to("#pz-hamann .anillo", {{ opacity: 1, duration: 0.2 }}, 1.15);
    tl.fromTo("#pz-l2", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "expo.out" }}, 1.3);
    // "tres defensores": la línea de tres
    tl.to("#pz-linea3", {{ strokeDashoffset: 0, duration: 0.55, ease: "power2.inOut" }}, 5.35);
    tl.fromTo("#pz-l3", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "expo.out" }}, 4.85);
    tl.to("#pz-f1", {{ color: "#9a9a9a", duration: 0.3 }}, 5.1);
    tl.fromTo("#pz-f2", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, 5.15);
    tl.fromTo("#pz-f3", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 5.3);
    // "Gerrard queda más libre"
    tl.to("#pz-gerrard .anillo", {{ opacity: 1, duration: 0.2 }}, 5.95);
    tl.fromTo("#pz-estela", {{ opacity: 0 }}, {{ opacity: 0.9, duration: 0.4 }}, 6.1);
    tl.fromTo("#pz-l4", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "expo.out" }}, 6.0);
    // "Benítez les pide algo simple"
    tl.fromTo("#pz-orden", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 8.5);
    // "hacer un gol rápido"
    tl.set("#pz-flecha", {{ opacity: 1 }}, 10.72);
    tl.to("#pz-flecha", {{ strokeDashoffset: 0, duration: 0.7, ease: "power2.inOut" }}, 10.72);
    tl.to("#pz-area", {{ stroke: "#7ab37a", duration: 0.3 }}, 11.3);
    // movimientos
    {chr(10).join("    " + s for s in js_mov)}
    window.__timelines["pizarra"] = tl;
  </script>
</template>
'''
Path(__file__).parent.joinpath("compositions", "pizarra.html").write_text(HTML)
print("compositions/pizarra.html")
