"""Jugadas "intervenidas": el video de la transmisión se pausa, el fondo se apaga, los jugadores quedan
recortados con contorno verde, y aparecen aros, nombres, flechas y datos (pedido del usuario, 10/11).

Uso: /usr/bin/python3 animaciones/futbol/intervenidos.py <specs.json> [id ...]
  -> compositions/intervenido_<id>.html + assets/iv_<id>_* ; con --render además renderiza cada una a
     proyectos/estambul-2005/salida/graficos_sin_logo/iv_<id>.mp4

Spec (todas las coordenadas en píxeles de la FUENTE 1920x1080; la cámara es [zoom, centro_x, centro_y]):
{"id": "117", "fuente": "../../proyectos/.../final_uefa.mp4", "dur": 8.37,
 "tramos": [
   {"play": [518.6, 519.5], "t": [0, 1.3], "cam": [[1.5, 780, 390], [2, 780, 390]]},
   {"pausa": 519.5, "t": [1.3, 3.4], "cam": [2, 780, 390],
    "marcas": [{"x": 1060, "y": 450, "w": 120, "h": 150, "et": "CABEZAZO", "nm": "SHEVCHENKO", "en": 1.45,
                "lado": "abajo"}],
    "flecha": {"de": [1050, 420], "a": [680, 400], "curva": -80, "en": 1.8},
    "num": "117'"},
 ],
 "datos": [{"a": "DOBLE ATAJADA", "b": "MINUTO 117", "t": [6.6, 8.37]}]}
"""
import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
CG = '{"preset":null,"intensity":1,"adjust":{"exposure":-0.7,"contrast":0.1,"saturation":-1}}'
# planos abiertos (jugadores chicos): fondo menos apagado para que se vean ("suave": true en la pausa)
CG_SUAVE = '{"preset":null,"intensity":1,"adjust":{"exposure":-0.3,"contrast":0.05,"saturation":-0.7}}'


def sh(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, cwd=AQUI)
    if r.returncode:
        raise SystemExit(" ".join(map(str, cmd)) + "\n" + r.stderr[-2000:])
    return r.stdout


def pantalla(cam, x, y):
    k, cx, cy = cam
    return k * (x - cx) + 960, k * (y - cy) + 540


def transform(cam):
    """#plano con transformOrigin 0 0: pantalla = k*p + t."""
    k, cx, cy = cam
    return {"scale": k, "x": round(960 - k * cx, 1), "y": round(540 - k * cy, 1)}


def assets(spec, fuente):
    i = spec["id"]
    for n, tr in enumerate(spec["tramos"]):
        if "play" in tr:
            a, b = tr["play"]
            d = tr["t"][1] - tr["t"][0]
            out = AQUI / f"assets/iv_{i}_s{n}.mp4"
            sh(["ffmpeg", "-v", "error", "-y", "-ss", a, "-t", b - a, "-i", fuente, "-vf",
                f"setpts=PTS*{d / (b - a):.5f},fps=30", "-t", f"{d:.3f}", "-an", "-c:v", "libx264", "-crf", "16",
                "-g", "5", "-pix_fmt", "yuv420p", out])
        else:
            f = AQUI / f"assets/iv_{i}_f{n}.png"
            sh(["ffmpeg", "-v", "error", "-y", "-ss", tr["pausa"], "-i", fuente, "-frames:v", "1", f])
            c = AQUI / f"assets/iv_{i}_f{n}_cut.png"
            if not c.exists():
                sh(["npx", "hyperframes@0.9.17", "remove-background", f, "-o", c])


def html(spec):
    i = spec["id"]
    cid = f"intervenido_{i}"
    D = spec["dur"]
    capas, otras, js = [], [], []
    js.append(f'tl.set("#{cid} .plano", {json.dumps(transform(spec["tramos"][0]["cam"][0] if "play" in spec["tramos"][0] else spec["tramos"][0]["cam"]))}, 0);')
    for n, tr in enumerate(spec["tramos"]):
        t0, t1 = tr["t"]
        d = round(t1 - t0, 3)
        if "play" in tr:
            capas.append(f'<video class="clip full" src="assets/iv_{i}_s{n}.mp4" data-start="{t0}" data-duration="{d}" '
                         f'data-track-index="0" muted playsinline></video>')
            c0, c1 = tr["cam"]
            js.append(f'tl.set("#{cid} .plano", {json.dumps(transform(c0))}, {t0});')
            if c0 != c1:
                js.append(f'tl.fromTo("#{cid} .plano", {json.dumps(transform(c0))}, {{...{json.dumps(transform(c1))}, '
                          f'duration: {d}, ease: "power1.inOut"}}, {t0});')
            continue
        cam = tr["cam"]
        js.append(f'tl.set("#{cid} .plano", {json.dumps(transform(cam))}, {t0});')
        capas.append(f'<img class="clip full" src="assets/iv_{i}_f{n}.png" alt="" data-start="{t0}" data-duration="{d}" '
                     f"data-track-index=\"1\" data-color-grading='{CG_SUAVE if tr.get('suave') else CG}'>")
        capas.append(f'<div class="clip tinte" data-start="{t0}" data-duration="{d}" data-track-index="2"'
                     + (' style="opacity:.4"' if tr.get("suave") else "") + '></div>')
        capas.append(f'<img class="clip full cut" src="assets/iv_{i}_f{n}_cut.png" alt="jugadores" data-start="{t0}" '
                     f'data-duration="{d}" data-track-index="3" data-layout-allow-occlusion="">')
        # flash
        js.append(f'tl.fromTo("#{cid} .flash", {{opacity: 0}}, {{opacity: 0.8, duration: 0.03}}, {max(0, t0 - 0.02)});')
        js.append(f'tl.to("#{cid} .flash", {{opacity: 0, duration: 0.25, ease: "power2.out"}}, {t0 + 0.01});')
        if tr.get("num"):
            nid = f"{cid}-num{n}"
            otras.append(f'<div id="{nid}" class="clip num" data-start="{t0}" data-duration="{d}" data-track-index="4" '
                         f'data-layout-allow-overflow="" data-layout-ignore="">{tr["num"]}</div>')
            js.append(f'tl.fromTo("#{nid}", {{opacity: 0, x: -60}}, {{opacity: 1, x: 0, duration: 0.45, ease: "expo.out"}}, {t0 + 0.1});')
        if tr.get("flecha"):
            fl = tr["flecha"]
            (x0, y0), (x1, y1) = pantalla(cam, *fl["de"]), pantalla(cam, *fl["a"])
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            # control perpendicular a la recta, "curva" px en pantalla
            dx, dy = x1 - x0, y1 - y0
            L = max(1.0, (dx * dx + dy * dy) ** 0.5)
            qx, qy = mx - dy / L * fl.get("curva", -80), my + dx / L * fl.get("curva", -80)
            largo = int(L * 1.25 + 40)
            fid = f"{cid}-fl{n}"
            otras.append(f'<svg id="{fid}" class="clip flecha" data-start="{t0}" data-duration="{d}" data-track-index="5" '
                         f'viewBox="0 0 1920 1080" data-layout-ignore=""><defs><marker id="{fid}-p" markerWidth="8" '
                         f'markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#c8e6c8"/>'
                         f'</marker></defs><path class="ln" d="M{x0:.0f},{y0:.0f} Q {qx:.0f},{qy:.0f} {x1:.0f},{y1:.0f}" '
                         f'fill="none" stroke="#c8e6c8" stroke-width="7" stroke-dasharray="{largo}" '
                         f'stroke-dashoffset="{largo}" marker-end="url(#{fid}-p)"/></svg>')
            js.append(f'tl.to("#{fid} .ln", {{strokeDashoffset: 0, duration: 0.55, ease: "power2.inOut"}}, {fl["en"]});')
        for m, mk in enumerate(tr.get("marcas", [])):
            k = cam[0]
            sx, sy = pantalla(cam, mk["x"], mk["y"])
            w, h = mk["w"] * k, mk["h"] * k
            aid, tid = f"{cid}-a{n}{m}", f"{cid}-t{n}{m}"
            otras.append(f'<div id="{aid}" class="clip aro" data-start="{t0}" data-duration="{d}" data-track-index="{6 + 2 * m}" '
                         f'style="left:{sx - w / 2:.0f}px;top:{sy - h / 2:.0f}px;width:{w:.0f}px;height:{h:.0f}px"></div>')
            lado = mk.get("lado", "abajo")
            if lado == "abajo":
                pos = f"left:{sx - w / 2:.0f}px;top:{sy + h / 2 + 16:.0f}px"
            elif lado == "arriba":
                pos = f"left:{sx - w / 2:.0f}px;bottom:{1080 - (sy - h / 2) + 16:.0f}px"
            elif lado == "der":
                pos = f"left:{sx + w / 2 + 24:.0f}px;top:{sy - 40:.0f}px"
            else:  # izq
                pos = f"right:{1920 - (sx - w / 2) + 24:.0f}px;top:{sy - 40:.0f}px;text-align:right"
            et = f'<span class="et">{mk["et"]}</span>' if mk.get("et") else ""
            otras.append(f'<div id="{tid}" class="clip tag" data-start="{t0}" data-duration="{d}" '
                         f'data-track-index="{7 + 2 * m}" style="{pos}">{et}<span class="nm">{mk["nm"]}</span></div>')
            en = mk.get("en", t0 + 0.1)
            js.append(f'tl.fromTo("#{aid}", {{opacity: 0, scale: 1.6}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "expo.out"}}, {en});')
            js.append(f'tl.fromTo("#{tid}", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.3, ease: "expo.out"}}, {en + 0.1});')
    for n, dt in enumerate(spec.get("datos", [])):
        t0, t1 = dt["t"]
        did = f"{cid}-d{n}"
        b = f'<span class="b">{dt["b"]}</span>' if dt.get("b") else ""
        otras.append(f'<div id="{did}" class="clip dato" data-start="{t0}" data-duration="{round(t1 - t0, 3)}" '
                     f'data-track-index="20"><span class="a">{dt["a"]}</span>{b}</div>')
        js.append(f'tl.fromTo("#{did} .a", {{opacity: 0, scale: 1.4}}, {{opacity: 1, scale: 1, duration: 0.25, ease: "expo.out"}}, {t0});')
        if b:
            js.append(f'tl.fromTo("#{did} .b", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: 0.3, ease: "expo.out"}}, {t0 + 0.2});')
    nl = "\n    "
    return f"""<template>
  <!-- Generado por intervenidos.py ({spec["id"]}): pausa, fondo apagado, jugadores recortados, aros y datos. -->
  <style>
    @font-face {{ font-family: "Mono"; src: url("assets/fonts/jetbrains-mono.ttf"); font-weight: 100 800; }}
    #{cid} {{ position: absolute; inset: 0; overflow: hidden; background: #000; }}
    #{cid} .plano {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 0 0; }}
    #{cid} .full {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; }}
    #{cid} .tinte {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; background: rgba(14, 26, 14, .5); }}
    #{cid} .cut {{ filter: drop-shadow(3px 0 0 #7ab37a) drop-shadow(-3px 0 0 #7ab37a) drop-shadow(0 3px 0 #7ab37a) drop-shadow(0 -3px 0 #7ab37a); }}
    #{cid} .flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; z-index: 30; }}
    #{cid} .aro {{ position: absolute; border: 5px solid #c8e6c8; border-radius: 50%; box-shadow: 0 0 24px rgba(122,179,122,.6); }}
    #{cid} .tag {{ position: absolute; font: 700 44px/1 "Mono"; color: #fff; white-space: nowrap; }}
    #{cid} .tag .et {{ display: block; font: 600 22px/1 "Mono"; letter-spacing: 3px; color: #1a2e1a; background: #c8e6c8;
                padding: 8px 12px 4px; margin-bottom: 8px; width: max-content; }}
    #{cid} .tag .nm {{ display: block; background: rgba(14,26,14,.85); padding: 10px 14px 4px; width: max-content; }}
    #{cid} .flecha {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; overflow: visible; }}
    #{cid} .num {{ position: absolute; left: 60px; top: 40px; font: 700 300px/0.8 "Mono"; color: transparent;
               -webkit-text-stroke: 3px rgba(122,179,122,.6); }}
    #{cid} .dato {{ position: absolute; left: 50%; bottom: 90px; transform: translateX(-50%); text-align: center; z-index: 25; }}
    #{cid} .dato .a {{ display: inline-block; font: 700 92px/1 "Mono"; color: #fff; text-shadow: 0 4px 0 rgba(0,0,0,.5); white-space: nowrap; }}
    #{cid} .dato .b {{ display: block; width: max-content; margin: 14px auto 0; font: 700 30px/1 "Mono"; color: #1a2e1a;
                   background: #c8e6c8; padding: 12px 20px 6px; }}
  </style>
  <div id="{cid}" data-composition-id="{cid}" data-width="1920" data-height="1080">
    <div class="plano">
    {nl.join(capas)}
    </div>
    {nl.join(otras)}
    <div class="flash"></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {nl.join(js)}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


INDEX = """<!doctype html>
<html lang="es" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>* {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #0b0c0f; }}
      #root {{ position: relative; width: 100%; height: 100%; }}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{d}" data-width="1920" data-height="1080">
      <div id="intervenido_{i}" data-composition-id="intervenido_{i}" data-composition-src="compositions/intervenido_{i}.html" data-start="0" data-duration="{d}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>
    </div>
    <script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
"""


def con_indice(spec, accion):
    """Cambia index.html por uno con solo esta jugada, corre `accion` y deja index.html como estaba."""
    idx = AQUI / "index.html"
    viejo = idx.read_text()
    try:
        idx.write_text(INDEX.format(d=spec["dur"], i=spec["id"]))
        return accion()
    finally:
        idx.write_text(viejo)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    specs = json.load(open(args[0]))
    ids = args[1:] or [s["id"] for s in specs]
    salida = RAIZ / "proyectos/estambul-2005/salida/graficos_sin_logo"
    for s in specs:
        if s["id"] not in ids:
            continue
        fuente = (Path(args[0]).resolve().parent / s["fuente"]).resolve()
        assets(s, fuente)
        (AQUI / f"compositions/intervenido_{s['id']}.html").write_text(html(s))
        if "--snap" in sys.argv:
            ts = ",".join(f"{(tr['t'][0] + tr['t'][1]) / 2 + 0.5:.2f}" for tr in s["tramos"] if "pausa" in tr)
            print(con_indice(s, lambda: sh(["npx", "hyperframes@0.9.17", "snapshot", "--at", ts]))[-400:])
        if "--render" in sys.argv:
            out = salida / f"iv_{s['id']}.mp4"
            con_indice(s, lambda: sh(["npx", "hyperframes@0.9.17", "render", "-o", out, "-q", "delivery"]))
            print("render:", out)
