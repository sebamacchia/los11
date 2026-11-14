"""Planos documentales (Johnny Harris / The Kid Stays in the Picture / Wes Anderson / Saul Bass, sin que se note):
una "mesa" en alta resolución (papel, fotos impresas, recortes) que la CÁMARA recorre con zooms y paneos lentos
y con intención, más rótulos escritos a máquina, líneas de tinta, retratos en círculo y grano de película.

Visual en el guion (armar.py):
  {"tipo": "doc", "planos": [
     {"en": 0, "mesa": "papel" | "negro" | {"archivo": clip/foto, "desde": s} (desenfocado),
      "capas": [{"archivo": "material/x.jpg", "x": 960, "y": 540, "alto": 1000, "rot": 0, "papel": true,
                 "recorte": [x0,y0,x1,y1]}],               # x, y, alto en coordenadas de pantalla (1920x1080)
      "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1}, {"t": "@la cinta", "x": 1400, "y": 640, "zoom": 2.6}],
      "rotulos": [{"tipo": "maquina", "texto": "...", "x": 120, "y": 900, "en": "@frase", "tam": 34},
                  {"tipo": "titulo", "texto": "...", "x":, "y":, "en":, "tam": 120}   (Plex condensada, Saul Bass)
                  {"tipo": "linea", "desde": [x,y], "hasta": [x,y], "en":, "dibujo": 0.5, "mundo": true}
                  {"tipo": "retrato", "archivo":, "x":, "y":, "r": 90, "en":, "nombre": "..."}
                  {"tipo": "subrayado", "x":, "y":, "ancho":, "en":}]},
     {"en": "@otra frase", ...}]}       cada plano corta en seco al siguiente
Coordenadas "mundo" (de la mesa) = las de pantalla con la cámara en zoom 1. Un rótulo con "mundo": true sigue a la
cámara (queda pegado a lo que señala); si no, queda fijo en pantalla.
"""
import math
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "animaciones" / "futbol" / "assets" / "fonts"
W, H, FPS = 1920, 1080, 30
K = 2.5                         # resolución de la mesa (zoom hasta ~2.5x sin perder nitidez)
PAPEL = (236, 230, 216)
TINTA = (28, 26, 22)
ROJO = (178, 38, 30)            # tinta roja, apagada
CREMA = (242, 238, 228)


def fuente(tam, mono=True, peso=500):
    f = ImageFont.truetype(str(FUENTES / ("jetbrains-mono.ttf" if mono else "plex-sans.ttf")), int(tam))
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


def suave(x):  # ease in-out (movimientos de cámara)
    x = max(0.0, min(1.0, x))
    return x * x * x * (x * (6 * x - 15) + 10)


# ───────────────────────────── la mesa ─────────────────────────────
def papel(w, h, seed=3):
    base = Image.new("RGB", (w, h), PAPEL)
    g = Image.effect_noise((w // 2, h // 2), 26).convert("L").resize((w, h), Image.BILINEAR)
    base = ImageChops.multiply(base, Image.merge("RGB", [g.point(lambda v: 222 + v // 8)] * 3))
    rnd = random.Random(seed)
    d = ImageDraw.Draw(base)
    for _ in range(int(w * h / 4000)):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        a, l = rnd.uniform(0, math.pi), rnd.uniform(6, 26) * K / 2
        c = rnd.randint(200, 222)
        d.line([(x, y), (x + l * math.cos(a), y + l * math.sin(a))], fill=(c, c - 4, c - 12), width=1)
    v = Image.new("L", (w, h), 0)
    ImageDraw.Draw(v).ellipse([-w * 0.25, -h * 0.35, w * 1.25, h * 1.35], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(w / 9))
    return Image.composite(base, ImageChops.multiply(base, Image.new("RGB", (w, h), (200, 190, 170))), v)


def impresa(im, rnd):
    """Foto impresa vieja: un poco de contraste, cálida, grano."""
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageChops.multiply(im, Image.new("RGB", im.size, (255, 248, 236)))
    g = Image.effect_noise((max(1, im.width // 2), max(1, im.height // 2)), 18).convert("L").resize(im.size)
    return ImageChops.multiply(im, Image.merge("RGB", [g.point(lambda v: 214 + v // 6)] * 3))


def trama(im, paso):
    """Trama de imprenta: puntos en grilla cuyo tamaño sigue la luminancia (revista de 1985)."""
    w, h = im.size
    g = ImageOps.grayscale(im)
    pat = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(pat)
    peq = g.resize((max(1, w // paso), max(1, h // paso)), Image.BOX)
    for j in range(peq.height):
        for i in range(peq.width):
            v = peq.getpixel((i, j))
            r = paso * 0.62 * (1 - v / 255) ** 0.8
            x, y = i * paso + paso / 2 + (paso / 2 if j % 2 else 0), j * paso + paso / 2
            if r > 0.4:
                d.ellipse([x - r, y - r, x + r, y + r], fill=0)
    pat = pat.filter(ImageFilter.GaussianBlur(0.6))
    puntos = Image.merge("RGB", [pat.point(lambda v: 150 + v * 105 // 255)] * 3)
    return Image.blend(im, ImageChops.multiply(im, puntos), 0.55)


def cancha(base):
    """Cancha horizontal en tinta fina sobre el papel (mitad izquierda = Argentina, ataca hacia la derecha)."""
    d = ImageDraw.Draw(base)
    w, h = base.size
    col = (120, 112, 98)
    lw = max(2, int(2 * K))
    x0, y0, x1, y1 = 60 * K, 40 * K, w - 60 * K, h - 40 * K
    d.rectangle([x0, y0, x1, y1], outline=col, width=lw)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.line([(cx, y0), (cx, y1)], fill=col, width=lw)
    r = 150 * K
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=lw)
    for lado in (0, 1):
        xa = x0 if lado == 0 else x1
        s = 1 if lado == 0 else -1
        d.rectangle(sorted([xa, xa + s * 260 * K]) and [min(xa, xa + s * 260 * K), cy - 330 * K,
                    max(xa, xa + s * 260 * K), cy + 330 * K], outline=col, width=lw)
        d.rectangle([min(xa, xa + s * 90 * K), cy - 140 * K, max(xa, xa + s * 90 * K), cy + 140 * K],
                    outline=col, width=lw)


def mesa(plano, cuadros_fondo=None):
    """Imagen de la mesa en resolución K, o None si el fondo es un clip (se compone por cuadro)."""
    tipo = plano.get("mesa", "papel")
    mw, mh = int(W * K), int(H * K)
    if tipo == "negro":
        base = Image.new("RGB", (mw, mh), (10, 10, 9))
    elif tipo == "papel":
        base = papel(mw, mh)
    else:
        base = None
    if plano.get("cancha") and base is not None:
        cancha(base)
    piezas = []
    for k, c in enumerate(plano.get("capas", [])):
        rnd = random.Random(40 + k)
        src = Image.open(RAIZ / c["archivo"]).convert("RGB")
        if c.get("recorte"):
            src = src.crop(c["recorte"])
        if c.get("bn"):
            src = ImageOps.grayscale(src).convert("RGB")
        alto = int(c.get("alto", 900) * K)
        src = src.resize((max(1, int(src.width * alto / src.height)), alto), Image.LANCZOS)
        for _ in range(2 if c.get("trama") else 0):  # foto de revista: trama de imprenta (2 pasadas = look aprobado 14/11)
            src = trama(src.filter(ImageFilter.GaussianBlur(K * 0.8)), int(c["trama"] * K))
        if c.get("papel", True):
            src = impresa(src, rnd)
        pieza = src.convert("RGBA")
        if c.get("borde"):  # borde de papel fino (foto impresa), opcional
            b = int(c["borde"] * K)
            marco = Image.new("RGBA", (pieza.width + 2 * b, pieza.height + 2 * b), (240, 236, 226, 255))
            marco.paste(pieza, (b, b))
            pieza = marco
        pieza = pieza.rotate(c.get("rot", 0), resample=Image.BICUBIC, expand=True)
        x, y = int(c["x"] * K - pieza.width / 2), int(c["y"] * K - pieza.height / 2)
        sombra = None
        if c.get("sombra", True) and tipo != "negro":
            sombra = Image.new("RGBA", pieza.size, (0, 0, 0, 0))
            sombra.putalpha(pieza.getchannel("A").point(lambda v: v * 110 // 255)
                            .filter(ImageFilter.GaussianBlur(10 * K)))
        piezas.append({"im": pieza, "x": x, "y": y, "sombra": sombra,
                       "en": float(c.get("en", plano.get("en", 0))), "sale": c.get("sale")})
    return base, piezas


def componer(base, piezas, visibles, mw=None, mh=None):
    """Mesa con las capas visibles (en el orden del guion: las nuevas quedan arriba)."""
    if base is None:
        comp = Image.new("RGBA", (int(W * K), int(H * K)), (0, 0, 0, 0))
    else:
        comp = base.convert("RGBA")
    for k in visibles:
        p = piezas[k]
        if p["sombra"] is not None:
            comp.alpha_composite(p["sombra"], (p["x"] + int(6 * K), p["y"] + int(10 * K)))
        comp.alpha_composite(p["im"], (p["x"], p["y"]))
    return comp if base is None else comp.convert("RGB")


def camara(plano, t):
    """(cx, cy, zoom) en coordenadas de pantalla con interpolación suave entre keyframes."""
    kf = plano.get("camara") or [{"t": 0, "x": W / 2, "y": H / 2, "zoom": 1}]
    kf = sorted(kf, key=lambda k: k["t"])
    if t <= kf[0]["t"]:
        k = kf[0]
        return k["x"], k["y"], k["zoom"]
    for a, b in zip(kf, kf[1:]):
        if t <= b["t"]:
            f = suave((t - a["t"]) / max(1e-6, b["t"] - a["t"]))
            # el zoom se interpola en escala logarítmica (se siente parejo)
            z = math.exp(math.log(a["zoom"]) + (math.log(b["zoom"]) - math.log(a["zoom"])) * f)
            return a["x"] + (b["x"] - a["x"]) * f, a["y"] + (b["y"] - a["y"]) * f, z
    k = kf[-1]
    return k["x"], k["y"], k["zoom"]


def ver(img_mundo, cx, cy, z):
    """Recorta la mesa (resolución K) según la cámara y la lleva a 1920x1080."""
    z = max(1.0, z)
    w, h = W * K / z, H * K / z
    x0 = min(max(0.0, cx * K - w / 2), W * K - w)   # la cámara nunca se sale de la mesa
    y0 = min(max(0.0, cy * K - h / 2), H * K - h)
    return img_mundo.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))


def a_pantalla(p, cam):
    cx, cy, z = cam
    return (W / 2 + (p[0] - cx) * z, H / 2 + (p[1] - cy) * z)


# ───────────────────────────── rótulos ─────────────────────────────
def rotulo(lienzo, r, t, cam):
    d = ImageDraw.Draw(lienzo)
    edad = t - r["en"]
    if edad < 0 or (r.get("sale") is not None and t >= r["sale"]):
        return
    claro = r.get("claro", False)
    color = CREMA if claro else TINTA
    pos = (r["x"], r["y"]) if "x" in r else None
    if pos and r.get("mundo"):
        pos = a_pantalla(pos, cam)
    tipo = r["tipo"]
    zt = cam[2] if r.get("mundo") else 1.0   # un texto pegado a la mesa crece con el zoom
    if tipo == "maquina":  # se tipea: ~28 letras por segundo
        f = fuente(r.get("tam", 32) * zt, peso=r.get("peso", 500))
        n = int(edad * r.get("vel", 28))
        lh = int(r.get("tam", 32) * 1.45 * zt)
        restante = n
        for i, l in enumerate(r["texto"].split("\n")):
            vis = l[:max(0, restante)]
            restante -= len(l)
            if vis:
                if r.get("fondo_tira"):
                    tw = f.getlength(l)
                    d.rectangle([pos[0] - 14 * zt, pos[1] + i * lh - 8 * zt, pos[0] + tw + 14 * zt,
                                 pos[1] + i * lh + lh - 10 * zt],
                                fill=(PAPEL if not claro else (14, 14, 12)) + (235,))
                d.text((pos[0], pos[1] + i * lh), vis, font=f, fill=(ROJO if r.get("rojo") else color) + (255,))
    elif tipo == "titulo":  # tipografía contundente, aparece de golpe
        f = fuente(r.get("tam", 120) * zt, mono=False, peso=r.get("peso", 700))
        lh = int(r.get("tam", 120) * 1.02 * zt)
        for i, l in enumerate(r["texto"].split("\n")):
            if r.get("fondo_tira"):  # tira de papel detrás, para que se lea sobre una foto
                bb = f.getbbox(l)
                pad = 12 * zt
                d.rectangle([pos[0] + bb[0] - pad, pos[1] + i * lh + bb[1] - pad * 0.6,
                             pos[0] + bb[2] + pad, pos[1] + i * lh + bb[3] + pad * 0.6],
                            fill=(PAPEL if not claro else (14, 14, 12)) + (240,))
            d.text((pos[0], pos[1] + i * lh), l, font=f, fill=(ROJO if r.get("rojo") else color) + (255,))
    elif tipo in ("linea", "subrayado"):
        if tipo == "subrayado":
            a, b = (r["x"], r["y"]), (r["x"] + r["ancho"], r["y"])
        else:
            a, b = tuple(r["desde"]), tuple(r["hasta"])
        if r.get("mundo"):
            a, b = a_pantalla(a, cam), a_pantalla(b, cam)
            if tipo == "subrayado":
                zt = cam[2]
        f = suave(edad / r.get("dibujo", 0.5))
        fin = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        d.line([a, fin], fill=(ROJO if r.get("rojo", tipo == "subrayado") else color) + (255,),
               width=max(1, int(r.get("grosor", 4 if tipo == "subrayado" else 2) * zt)))
        if r.get("punto") and f >= 1:
            d.ellipse([b[0] - 6, b[1] - 6, b[0] + 6, b[1] + 6], fill=color + (255,))
    elif tipo == "circulo":  # marcador rojo a mano alzada, pegado a la mesa
        cx, cy = a_pantalla((r["x"], r["y"]), cam) if r.get("mundo", True) else (r["x"], r["y"])
        z = cam[2] if r.get("mundo", True) else 1
        rx, ry = r["ancho"] / 2 * z, r["alto"] / 2 * z
        f = suave(edad / r.get("dibujo", 0.6))
        pts = []
        n = 90
        for k in range(int(n * 1.12 * f) + 1):  # da un poco más de una vuelta, como a mano
            a = -2.2 + 2 * math.pi * k / n
            w = 1 + 0.04 * math.sin(k * 0.21) + 0.05 * k / n
            pts.append((cx + rx * w * math.cos(a), cy + ry * w * math.sin(a)))
        if len(pts) > 1:
            d.line(pts, fill=ROJO + (255,), width=r.get("grosor", 6), joint="curve")
    elif tipo == "flecha":
        a, b = tuple(r["desde"]), tuple(r["hasta"])
        if r.get("mundo", True):
            a, b = a_pantalla(a, cam), a_pantalla(b, cam)
        f = suave(edad / r.get("dibujo", 0.4))
        fin = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        d.line([a, fin], fill=ROJO + (255,), width=r.get("grosor", 5))
        if f > 0.95:
            ang = math.atan2(b[1] - a[1], b[0] - a[0])
            for da in (2.6, -2.6):
                d.line([b, (b[0] + 26 * math.cos(ang + da), b[1] + 26 * math.sin(ang + da))],
                       fill=ROJO + (255,), width=r.get("grosor", 5))
    elif tipo == "retrato":
        im = _retrato(r)
        rr = r.get("r", 90)
        lienzo.alpha_composite(im, (int(pos[0] - im.width / 2), int(pos[1] - rr - 8)))
        if r.get("nombre"):
            f = fuente(r.get("tam", 20), peso=600)
            txt = r["nombre"].upper()
            d.text((pos[0] - f.getlength(txt) / 2, pos[1] + rr + 14), txt, font=f, fill=color + (255,))


_cache_retratos = {}


def _retrato(r):
    clave = (r["archivo"], r.get("r", 90), r.get("anillo", True), str(r.get("recorte")))
    if clave not in _cache_retratos:
        rr = r.get("r", 90)
        src = Image.open(RAIZ / r["archivo"]).convert("RGB")
        if r.get("recorte"):
            src = src.crop(r["recorte"])
        src = ImageOps.fit(src, (rr * 2, rr * 2), Image.LANCZOS, centering=(0.5, 0.4))
        src = impresa(ImageEnhance.Color(src).enhance(0.75), random.Random(1))
        m = Image.new("L", (rr * 8, rr * 8), 0)
        ImageDraw.Draw(m).ellipse([0, 0, rr * 8 - 1, rr * 8 - 1], fill=255)
        m = m.resize((rr * 2, rr * 2), Image.LANCZOS)
        out = Image.new("RGBA", (rr * 2 + 16, rr * 2 + 16), (0, 0, 0, 0))
        tmp = src.convert("RGBA")
        tmp.putalpha(m)
        out.alpha_composite(tmp, (8, 8))
        if r.get("anillo", True):
            ImageDraw.Draw(out).ellipse([4, 4, rr * 2 + 11, rr * 2 + 11], outline=TINTA + (255,), width=3)
        _cache_retratos[clave] = out
    return _cache_retratos[clave]


# ───────────────────────────── película ─────────────────────────────
def _granos(n=6):
    out = []
    for k in range(n):
        g = Image.effect_noise((W // 2, H // 2), 40).convert("L").resize((W, H), Image.BILINEAR)
        out.append(Image.merge("RGB", [g.point(lambda v: 232 + v // 11)] * 3))
    return out


def _vineta():
    v = Image.new("L", (W, H), 150)
    ImageDraw.Draw(v).ellipse([-W * 0.15, -H * 0.25, W * 1.15, H * 1.25], fill=255)
    return Image.merge("RGB", [v.filter(ImageFilter.GaussianBlur(160))] * 3)


def render(cfg, salida):
    dur = cfg["duracion"]
    planos = sorted(cfg["planos"], key=lambda p: p["en"])
    n = int(round(dur * FPS))
    granos, vin = _granos(), _vineta()
    sys.path.insert(0, str(RAIZ / "herramientas"))
    cache = {}
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                             "-pix_fmt", "yuv420p", str(salida)], stdin=subprocess.PIPE)
    fondo_gen, comp_cache = {}, {}
    for fi in range(n):
        t = fi / FPS
        idx = max(i for i, p in enumerate(planos) if p["en"] <= t + 1e-6) if planos[0]["en"] <= t else 0
        pl = planos[idx]
        tl = t - pl["en"]
        if idx not in cache:
            cache[idx] = mesa(pl)
        base, piezas = cache[idx]
        vis = tuple(k for k, p in enumerate(piezas)
                    if p["en"] - pl["en"] <= tl + 1e-6 and (p["sale"] is None or tl < p["sale"] - pl["en"]))
        clave = (idx, vis)
        if comp_cache.get("clave") != clave:
            comp_cache["clave"], comp_cache["im"] = clave, componer(base, piezas, vis)
        if base is None:  # mesa = clip/foto desenfocado: se compone en resolución de pantalla
            if idx not in fondo_gen:
                import collage
                fin = planos[idx + 1]["en"] if idx + 1 < len(planos) else dur
                tr = dict(pl["mesa"], t=0)
                fondo_gen[idx] = collage.fondos_vox({"fondos": [tr]}, fin - pl["en"])
            try:
                fondo = next(fondo_gen[idx])
            except StopIteration:
                fondo = Image.new("RGB", (W, H), (20, 30, 20))
            cam = camara(pl, tl)
            cuadro = fondo.convert("RGBA")
            cuadro.alpha_composite(ver(comp_cache["im"], *cam))
        else:
            cam = camara(pl, tl)
            cuadro = ver(comp_cache["im"], *cam).convert("RGBA")
        for r in pl.get("rotulos", []):
            rr = dict(r)
            rr["en"] = r["en"] - pl["en"]
            if r.get("sale") is not None:
                rr["sale"] = r["sale"] - pl["en"]
            rotulo(cuadro, rr, tl, cam)
        rgb = cuadro.convert("RGB")
        if cfg.get("pelicula", True):
            rgb = ImageChops.multiply(rgb, granos[fi % len(granos)])
            rgb = ImageChops.multiply(rgb, vin)
        proc.stdin.write(rgb.tobytes())
    proc.stdin.close()
    proc.wait()


def sonidos(cfg):
    """Efectos: un "clac" de máquina de escribir suave por rótulo a máquina, y nada más (sobrio)."""
    out = []
    for p in cfg["planos"]:
        for r in p.get("rotulos", []):
            if r["tipo"] == "maquina" and not r.get("mudo"):
                out.append((float(r["en"]), "maquina"))
    return out


def sfx(destino, clase, seed):
    if clase == "maquina":  # ráfaga de teclas: 6 golpecitos
        partes = ";".join(f"[{i}]adelay={i * 70 + (seed * 13 % 20)}:all=1[k{i}]" for i in range(6))
        entradas = []
        for i in range(6):
            entradas += ["-f", "lavfi", "-i", f"anoisesrc=d=0.025:c=white:a=0.7:s={seed + i},"
                                              "bandpass=f=3200:w=2400,afade=t=out:d=0.025"]
        subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex",
                        partes + ";" + "".join(f"[k{i}]" for i in range(6)) + "amix=6:normalize=0,volume=0.8",
                        "-ar", "44100", "-ac", "2", str(destino)], check=True)
