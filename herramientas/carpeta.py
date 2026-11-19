"""CARPETA — el lenguaje "carpeta del DT" de LOS 11: recortes de foto con borde de papel, papel viejo, tiras rasgadas,
cinta, tinta y tiza, animados en stop-motion (12 cuadros por segundo, "en dos") sobre video de 30 fps.

Texturas reales (generadas con Higgsfield, 16/11) en identidad/texturas/:
  papel.png (fondo), pizarra.png (fondo), tiza.png (trazos blancos sobre negro), tinta.png (negro sobre blanco),
  papel_rasgado.png y cinta.png (piezas sobre magenta #FF00FF). `piezas(nombre)` las separa una por una.

  /usr/bin/python3 herramientas/carpeta.py 1986 <salida.mp4> [--capas] [--solo mr_t,f14]   (capas: una por elemento)
  /usr/bin/python3 herramientas/carpeta.py peluca <salida.mp4> [fondo.png] [--texto "..."] [--capas]

Las piezas se pegan ENCIMA de lo que había en pantalla (último cuadro del plano anterior como fondo):
no hay fondo limpio nuevo, las cosas se van pisando (pedido del usuario, 16/11).
"""
import json
import math
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
TEX = RAIZ / "identidad" / "texturas"
FUENTES = RAIZ / "animaciones" / "futbol" / "assets" / "fonts"
W, H, FPS = 1920, 1080, 30
PASO = 2                                   # stop-motion: la pose cambia cada 2 cuadros (12 fps)
ROJO, CREMA, TINTA = (178, 38, 30), (242, 238, 228), (28, 26, 22)
BORDE = (250, 248, 240)


def fuente(tam, peso=700):
    f = ImageFont.truetype(str(FUENTES / "jetbrains-mono.ttf"), int(tam))
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


def textura(nombre, w=W, h=H):
    return Image.open(TEX / f"{nombre}.png").convert("RGB").resize((w, h), Image.LANCZOS)


def piezas(nombre, minimo=400, junta=None):
    """Separa las piezas de una hoja de texturas (sobre magenta, negro o blanco) en recortes RGBA."""
    im = Image.open(TEX / f"{nombre}.png").convert("RGB")
    a = np.asarray(im).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    c0 = a[2, 2]
    if c0[0] > 180 and c0[2] > 180 and c0[1] < 90:                 # hoja sobre magenta
        mag = np.clip((np.minimum(r, b) - g) / 255.0, 0, 1)        # cuánto magenta tiene cada pixel
        alfa = mag < 0.35
        alfa_suave = np.asarray(Image.fromarray((np.clip(1 - mag * 2.6, 0, 1) * 255).astype("uint8"))
                                .filter(ImageFilter.MinFilter(3))).astype(float)
        lim = np.minimum(np.minimum(r, b), g + 12)                  # despill: saca el violeta de los bordes
        a = a.copy()
        a[..., 0] = np.where(mag > 0.05, np.minimum(r, lim), r)
        a[..., 2] = np.where(mag > 0.05, np.minimum(b, lim), b)
        im = Image.fromarray(a.astype("uint8"))
    elif nombre == "tiza":
        alfa = (r + g + b) / 3 > 60
        alfa_suave = np.clip(((r + g + b) / 3 - 30) * 1.6, 0, 255)
    else:                                                           # tinta: negro sobre blanco
        alfa = (r + g + b) / 3 < 160
        alfa_suave = np.clip((230 - (r + g + b) / 3) * 1.6, 0, 255)
    out = []
    for x0, y0, x1, y1 in _componentes(alfa, junta=junta or (1 if nombre == "efimera80" else 3)):
        if alfa[y0:y1, x0:x1].sum() < minimo:
            continue
        p = im.crop((x0, y0, x1, y1)).convert("RGBA")
        p.putalpha(Image.fromarray(alfa_suave[y0:y1, x0:x1].astype("uint8")))
        out.append(p)
    return out


def _componentes(mask, red=4, junta=3):
    """Cajas de las manchas separadas de una máscara (etiquetado simple a 1/red de resolución), en orden de lectura."""
    h, w = mask.shape
    m = mask[: h - h % red, : w - w % red].reshape(h // red, red, w // red, red).any((1, 3))
    m = np.asarray(Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MaxFilter(2 * junta + 1))) > 0
    hh, ww = m.shape
    lab = np.zeros((hh, ww), int)
    cajas, n = [], 0
    for y in range(hh):
        for x in range(ww):
            if m[y, x] and not lab[y, x]:
                n += 1
                pila_, lab[y, x] = [(y, x)], n
                y0 = y1 = y
                x0 = x1 = x
                while pila_:
                    cy, cx = pila_.pop()
                    y0, y1, x0, x1 = min(y0, cy), max(y1, cy), min(x0, cx), max(x1, cx)
                    for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                        if 0 <= ny < hh and 0 <= nx < ww and m[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n
                            pila_.append((ny, nx))
                cajas.append((x0 * red, y0 * red, min(w, (x1 + 1) * red), min(h, (y1 + 1) * red)))
    fila = max(1, h // 6)
    return sorted(cajas, key=lambda c: ((c[1] + c[3]) // 2 // fila, c[0]))


def _tramos(idx, hueco):
    if len(idx) == 0:
        return []
    t, ini = [], idx[0]
    for a, b in zip(idx[:-1], idx[1:]):
        if b - a > hueco:
            t.append((ini, a + 1))
            ini = b
    t.append((ini, idx[-1] + 1))
    return t


BORDE_SUAVE = 1.3     # px de desenfoque del borde del recorte (pedido 16/11: "2-4 px de blureado", que no se vea pixelado)


def figurita(im, g=0, sombra=True, seed=1):
    """Recorte "a tijera": borde irregular, sin borde blanco (g>0 lo agrega), suavizado 2-4 px, con sombra corta."""
    im = im.convert("RGBA")
    pad = g + 14
    base = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    base.paste(im, (pad, pad), im)
    al = base.split()[3].point(lambda v: 255 if v > 110 else 0)
    if g:
        al = al.filter(ImageFilter.MaxFilter(g * 2 + 1))
    # tijera: el contorno se come o se agranda 1-2 px en tramos (corte a mano, no perfecto)
    rng = np.random.default_rng(seed)
    ruido = Image.fromarray((rng.random((base.height // 18 + 2, base.width // 18 + 2)) * 255).astype("uint8"))
    ruido = ruido.resize(base.size, Image.BICUBIC)
    al = ImageChops.multiply(al.filter(ImageFilter.MaxFilter(3)),
                             ImageChops.lighter(al.filter(ImageFilter.MinFilter(5)), ruido.point(lambda v: 255 if v > 120 else 0)))
    al = al.filter(ImageFilter.GaussianBlur(BORDE_SUAVE))
    out = Image.new("RGBA", base.size, (0, 0, 0, 0))
    if sombra:
        s = Image.new("RGBA", base.size, (10, 6, 2, 0))
        s.putalpha(al.point(lambda v: v * 0.45).filter(ImageFilter.GaussianBlur(5)))
        out.alpha_composite(s, (4, 6))
    if g:
        papel = Image.new("RGBA", base.size, BORDE + (255,))
        papel.putalpha(al)
        out.alpha_composite(papel)
        out.alpha_composite(base)
    else:
        rec = base.copy()
        rec.putalpha(al)
        out.alpha_composite(rec)
    return out


def recorte_cuadro(im, seed=2, paso=34, mella=7):
    """Un cuadro (foto o video) cortado a tijera: bordes rectos pero mellados, sin marco, con sombra."""
    w, h = im.size
    rng = random.Random(seed)
    pts = []
    for x in range(0, w + 1, paso):
        pts.append((x, rng.uniform(0, mella)))
    for y in range(0, h + 1, paso):
        pts.append((w - rng.uniform(0, mella), y))
    for x in range(w, -1, -paso):
        pts.append((x, h - rng.uniform(0, mella)))
    for y in range(h, -1, -paso):
        pts.append((rng.uniform(0, mella), y))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(BORDE_SUAVE))
    pad = 14
    out = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    s = Image.new("RGBA", out.size, (10, 6, 2, 0))
    sm = Image.new("L", out.size, 0)
    sm.paste(m, (pad, pad))
    s.putalpha(sm.point(lambda v: v * 0.5).filter(ImageFilter.GaussianBlur(6)))
    out.alpha_composite(s, (5, 7))
    c = im.convert("RGBA")
    c.putalpha(m)
    out.alpha_composite(c, (pad, pad))
    return out


def pegar(fondo, im, x, y, esc=1.0, rot=0.0):
    """Pega `im` centrado en (x, y)."""
    if esc != 1:
        im = im.resize((max(1, int(im.width * esc)), max(1, int(im.height * esc))), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    fondo.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2))) if fondo.mode == "RGBA" else \
        fondo.paste(im, (int(x - im.width / 2), int(y - im.height / 2)), im)


def tira(texto, tam=46, fondo=ROJO, color=CREMA, seed=0):
    """Rótulo sobre una tira de papel rasgado teñida."""
    tiras = piezas("papel_rasgado")
    t = tiras[seed % len(tiras)]
    f = fuente(tam)
    tw = int(ImageDraw.Draw(t).textlength(texto, font=f))
    t = t.resize((tw + 2 * tam, int(tam * 2.1)), Image.LANCZOS)
    al = t.split()[3]
    gris = t.convert("L").point(lambda v: v / 255)
    tinte = Image.new("RGBA", t.size, fondo + (255,))
    tinte = ImageChops.multiply(tinte.convert("RGB"), Image.merge("RGB", [t.convert("L")] * 3)).convert("RGBA")
    tinte.putalpha(al)
    d = ImageDraw.Draw(tinte)
    d.text((tam, t.height / 2), texto, font=f, fill=color, anchor="lm")
    del gris
    return tinte


def suave(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


class Video:
    def __init__(self, salida):
        Path(salida).parent.mkdir(parents=True, exist_ok=True)
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                   "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
                                   str(salida)], stdin=subprocess.PIPE)

    def __call__(self, im):
        self.p.stdin.write(im.convert("RGB").tobytes())

    def cerrar(self):
        self.p.stdin.close()
        self.p.wait()


def grano(im, k, fuerza=10):
    rnd = np.random.default_rng(k // PASO)
    n = rnd.normal(0, fuerza, (H // 2, W // 2)).astype("int16")
    n = np.kron(n, np.ones((2, 2), dtype="int16"))
    a = np.asarray(im.convert("RGB")).astype("int16") + n[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))


# ─────────────────────────────── peluca ───────────────────────────────
PELO_CURVA = [(0, 175), (60, 165), (95, 150), (100, 115), (130, 100), (165, 105), (195, 120), (220, 140), (235, 158),
              (255, 165), (278, 175), (285, 215), (300, 245), (340, 255), (420, 255)]   # línea del pelo (maradona_italia)


class Capa:
    """Video con transparencia (ProRes 4444) de una sola capa, para editarla aparte en FilmCraft."""
    def __init__(self, salida, movida=False):
        # ProRes 4444 con transparencia (qscale 4: un tercio más liviano, sin pérdida visible). qtrle pesa 4x menos pero
        # FilmCraft deja de leerlo pasadas ~15 capas abiertas.
        cod = ["-c:v", "prores_ks", "-profile:v", "4444", "-qscale:v", "4", "-pix_fmt", "yuva444p10le"]
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                                   "-r", str(FPS), "-i", "-", *cod, str(salida)], stdin=subprocess.PIPE)

    def __call__(self, im):
        self.p.stdin.write(im.tobytes())

    def cerrar(self):
        self.p.stdin.close()
        self.p.wait()


def peluca(salida, fondo=None, texto=None, capas=False, dur=3.0,
           recorte=RAIZ / "proyectos/argentina-1986/material/recorte_maradona_italia.png"):
    """Diego recortado cae ENCIMA de lo que había en pantalla; una ráfaga de tinta le vuela el afro y la cara queda
    cortada. Capas: diego (con el pelo), rafaga, texto (opcional). Con capas=True además deja <salida>_<capa>.mov
    con transparencia."""
    r = Image.open(recorte).convert("RGBA")
    m = Image.new("L", r.size, 0)
    ImageDraw.Draw(m).polygon([(0, 0), (420, 0)] + PELO_CURVA[::-1], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(1.5))
    pelo = r.copy()
    pelo.putalpha(ImageChops.multiply(m, r.split()[3]))
    bb = pelo.getbbox()
    pelo = figurita(pelo.crop(bb), g=7)
    sin = r.copy()
    sin.putalpha(ImageChops.multiply(ImageChops.invert(m), r.split()[3]))
    cuerpo, entero = figurita(sin), figurita(r)
    cx, cy, esc = 760, 610, 1.0
    px = cx + ((bb[0] + bb[2]) / 2 - r.width / 2) * esc
    py = cy + ((bb[1] + bb[3]) / 2 - r.height / 2) * esc
    trazos = sorted(piezas("tinta"), key=lambda p: -p.width / max(1, p.height))[:3]
    cartel = tira(texto, 56, seed=1) if texto else None
    cintas = piezas("cinta")
    base = (Image.open(fondo).convert("RGB").resize((W, H)) if fondo else textura("papel")).convert("RGBA")
    salida = Path(salida)
    nombres = ["diego", "rafaga"] + (["texto"] if cartel else [])
    v = Video(salida)
    vc = {n: Capa(salida.with_name(f"{salida.stem}_{n}.mov")) for n in nombres} if capas else {}
    if capas:
        base.convert("RGB").save(salida.with_name(f"{salida.stem}_fondo.png"))
    T_CAE, T_VIENTO, T_VUELA = 0.25, 0.6, 0.9
    for k in range(int(dur * FPS)):
        t = (k - k % PASO) / FPS
        jit = random.Random(k // PASO)
        L = {n: Image.new("RGBA", (W, H), (0, 0, 0, 0)) for n in nombres}
        if t >= T_VIENTO:
            for j, tr in enumerate(trazos):
                u = (t - T_VIENTO - j * 0.06) / 0.55
                if 0 < u < 1:
                    pegar(L["rafaga"], tr, -500 + u * (W + 1000), 250 + j * 120, 0.9, jit.uniform(-3, 3))
        tiembla = 6 if T_VUELA < t < T_VUELA + 0.7 else 1.5
        dx, dy, rot = jit.uniform(-tiembla, tiembla), jit.uniform(-tiembla, tiembla), jit.uniform(-0.6, 0.6)
        d = L["diego"]
        if t < T_CAE:
            u = suave(t / T_CAE)
            pegar(d, entero, cx, cy - 40 * (1 - u), esc * (1.12 - 0.12 * u), 4 * (1 - u))
        elif t < T_VUELA:
            pegar(d, entero, cx + dx, cy + dy, esc, rot)
        else:
            pegar(d, cuerpo, cx + dx, cy + dy, esc, rot)
            u = t - T_VUELA
            salto = suave(u / 0.12) * 40
            pegar(d, pelo, px + 1250 * u * u + 380 * u, py - salto - 420 * u + 180 * u * u, esc * (1 + 0.1 * u), -u * 420)
        if cartel and t >= 1.35:
            u = suave((t - 1.35) / 0.18)
            pegar(L["texto"], cartel, 1300, 900 + (1 - u) * 260, 1, -2)
            if t >= 1.55:
                pegar(L["texto"], cintas[0], 1300 - cartel.width / 2 + 30, 900 - 40, 0.36, 35)
                pegar(L["texto"], cintas[1 % len(cintas)], 1300 + cartel.width / 2 - 30, 900 - 40, 0.36, -30)
        f = base.copy()
        for n in ("rafaga", "diego", "texto"):
            if n in L:
                f.alpha_composite(L[n])
                if n in vc:
                    vc[n](L[n])
        v(grano(f, k))
    v.cerrar()
    for c in vc.values():
        c.cerrar()


# ─────────────────────────────── pila ───────────────────────────────
# La intro como UNA pila que crece: cada elemento cae encima de lo anterior y se queda. Elemento:
#   {"img": RGBA | None, "video": (ruta, desde, vel, recorte_xyxy, ancho), "x", "y", "esc", "rot", "t": cuándo cae,
#    "entrada": "cae" | "golpe" | "desliza" | "trazo", "desde_dir": (dx, dy) para desliza, "grupo": capa}
# sacudones = [(t, fuerza)] mueven toda la pila (cámara en mano, stop-motion).

def recorte_png(ruta, ancho=None):
    im = Image.open(ruta).convert("RGBA")
    im = im.crop(im.getbbox())
    if ancho:
        im = im.resize((int(ancho), int(im.height * ancho / im.width)), Image.LANCZOS)
    return im


def tarjeta_roja(alto=170, seed=4):
    """Tarjeta roja de árbitro, de cartulina gastada."""
    w = int(alto * 0.7)
    im = Image.new("RGBA", (w, alto), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, alto - 1), radius=int(alto * 0.06), fill=(196, 22, 28, 255))
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 9, (alto, w, 1)).astype("int16")
    a = np.asarray(im).astype("int16")
    a[..., :3] = np.clip(a[..., :3] + n, 0, 255)
    brillo = np.linspace(18, -14, alto)[:, None, None].astype("int16")      # un poco de luz arriba
    a[..., :3] = np.clip(a[..., :3] + brillo, 0, 255)
    return Image.fromarray(a.astype("uint8"), "RGBA")


def afiche(ruta, ancho, margen=0.08, seed=None):
    """Afiche de un Mundial como papel impreso cortado a tijera. Los logos con transparencia van impresos sobre una
    cartulina crema (para que no floten), con un poco de tinta gastada."""
    im = Image.open(ruta)
    trans = im.mode in ("RGBA", "LA", "P") and "A" in im.convert("RGBA").getbands() and \
        im.convert("RGBA").split()[3].getextrema()[0] < 250
    im = im.convert("RGBA")
    if trans:
        im = im.crop(im.getbbox())
        m = int(max(im.size) * margen)
        lienzo = Image.new("RGBA", (im.width + 2 * m, im.height + 2 * m), (238, 232, 216, 255))
        lienzo.alpha_composite(im, (m, m))
        im = lienzo
    im = im.convert("RGB").resize((int(ancho), int(im.height * ancho / im.width)), Image.LANCZOS)
    a = np.asarray(im).astype("int16")                       # papel viejo: grano y un poco amarillento
    n = np.random.default_rng(seed or int(ancho)).normal(0, 6, a.shape[:2])[..., None]
    a = np.clip(a * [0.97, 0.95, 0.88] + [6, 4, 0] + n, 0, 255).astype("uint8")
    return recorte_cuadro(Image.fromarray(a), seed=seed or int(ancho) % 17)


def sello(texto, tam=260, color=ROJO, rot=-6, seed=3):
    """Sello de goma: texto pesado en tinta roja gastada, con marco."""
    f = ImageFont.truetype(str(FUENTES / "plex-sans.ttf"), tam)
    try:
        f.set_variation_by_axes([800])
    except Exception:
        pass
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    bb = d0.textbbox((0, 0), texto, font=f)
    w, h = bb[2] - bb[0] + tam * 0.5, bb[3] - bb[1] + tam * 0.45
    m = Image.new("L", (int(w), int(h)), 0)
    d = ImageDraw.Draw(m)
    g = max(6, tam // 18)
    d.rectangle([g, g, w - g, h - g], outline=255, width=g)
    d.text((w / 2, h / 2), texto, font=f, fill=255, anchor="mm")
    rng = np.random.default_rng(seed)
    ruido = rng.random((int(h), int(w)))
    gast = Image.fromarray(((ruido > 0.18) * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.8))
    m = ImageChops.multiply(m, gast)
    out = Image.new("RGBA", m.size, color + (0,))
    out.putalpha(m.point(lambda v: int(v * 0.92)))
    return out.rotate(rot, expand=True, resample=Image.BICUBIC)


def cuadros_video(ruta, desde, vel, recorte, ancho, dur):
    """Decodifica el tramo del clip (recortado y achicado) a una lista de cuadros RGB a 30 fps."""
    x0, y0, x1, y1 = recorte
    alto = int(ancho * (y1 - y0) / (x1 - x0)) // 2 * 2
    n = int(dur * FPS) + 2
    cmd = ["ffmpeg", "-v", "error", "-ss", str(desde), "-i", str(ruta), "-vf",
           f"setpts=PTS/{vel},fps={FPS},crop={x1 - x0}:{y1 - y0}:{x0}:{y0},scale={ancho}:{alto}",
           "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    tam = ancho * alto * 3
    return [Image.frombytes("RGB", (ancho, alto), raw[i:i + tam]) for i in range(0, len(raw) - tam + 1, tam)]


def marco_polaroid(im, borde=18, abajo=70):
    """Pone un cuadro (foto o video) dentro de un marco blanco tipo polaroid, con sombra."""
    w, h = im.size
    out = Image.new("RGBA", (w + 2 * borde + 16, h + borde + abajo + 16), (0, 0, 0, 0))
    s = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rectangle([8, 10, w + 2 * borde + 8, h + borde + abajo + 10], fill=(30, 20, 10, 110))
    out.alpha_composite(s.filter(ImageFilter.GaussianBlur(7)))
    ImageDraw.Draw(out).rectangle([2, 2, w + 2 * borde + 2, h + borde + abajo + 2], fill=(246, 243, 234, 255))
    out.paste(im.convert("RGB"), (borde + 2, borde + 2))
    return out


def base_carton(seed=5):
    """Cartón negro con fibra (la mesa donde arranca la pila)."""
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 7, (H // 4, W // 4))
    im = Image.fromarray(np.clip(26 + n, 0, 255).astype("uint8")).resize((W, H), Image.BICUBIC)
    return Image.merge("RGB", [im, im.point(lambda v: v * 0.96), im.point(lambda v: v * 0.9)]).convert("RGBA")


def pila(salida, elementos, dur, base=None, sacudones=(), capas=False, vhs_hasta=0.0, solo=None, camara=None):
    """capas=True: además deja <salida>_capas/ con UNA capa por elemento (NN_nombre.mov con transparencia, empieza
    cuando entra el elemento), 00_fondo.png, 99_vhs.mov y capas.json (para armar el .fcproj). solo={nombres}: rehace
    nada más esas capas (no toca el video armado ni las demás).
    camara=[(t, zoom, cx, cy), ...]: empuje lento de cámara (suave, a 30 fps) sobre el cuadro armado; solo en el video,
    las capas quedan sin cámara (en FilmCraft se hace con un keyframe de escala)."""
    elementos = [e for e in elementos if e.get("img") is not None or e.get("video") or e.get("fn") or e.get("_cuadros")]
    salida = Path(salida)
    base = base or base_carton()
    if not solo:     # lista de elementos para el Vibe Editor (herramientas/sala.py), sin necesidad de las capas ProRes
        json.dump([{"nombre": e.get("nombre") or e.get("grupo", "pila"), "inicio": round(e["t"], 3),
                    "fin": round(min(e.get("hasta") or dur, dur), 3)} for e in elementos],
                  open(salida.with_suffix(".elementos.json"), "w"), ensure_ascii=False, indent=1)
    # videos: decodificar una vez
    for e in elementos:
        if e.get("video"):
            ruta, desde, vel, rec, ancho = e["video"]
            e["_cuadros"] = cuadros_video(ruta, desde, vel, rec, ancho, e.get("vdur") or (dur - e["t"] + 0.5))
    nombres = [f"{i:02d}_{e.get('nombre') or e.get('grupo', 'pila')}" for i, e in enumerate(elementos, 1)]
    dcap = salida.with_name(salida.stem + "_capas")
    hacer = {i for i, n in enumerate(nombres) if not solo or n in solo or n[3:] in solo} if capas else set()
    if capas:
        dcap.mkdir(exist_ok=True)
        if not solo:
            base.save(dcap / "00_fondo.png")
    v = Video(salida) if not solo else None
    vc, primer = {}, {}
    vvhs = Capa(dcap / "99_vhs.mov", movida=True) if capas and vhs_hasta and not solo else None
    asentados = Image.new("RGBA", (W, H), (0, 0, 0, 0))      # lo que ya quedó quieto (se dibuja una sola vez)
    quietos = set()
    for k in range(int(dur * FPS)):
        tk = k / FPS
        t = (k - k % PASO) / FPS
        jit = random.Random(k // PASO)
        f = base.copy()
        L = {}
        for i, e in enumerate(elementos):
            if t < e["t"] or t >= e.get("hasta", 1e9):
                continue
            u = (t - e["t"]) / e.get("dura", 0.2)
            x, y, esc, rot = e["x"], e["y"], e.get("esc", 1.0), e.get("rot", 0.0)
            for m in e.get("mov", ()):                            # movimientos después de entrar (se suman)
                t0, t1, mx, my, curva = m[:5]                      # (t0, t1, dx, dy, curva[, giro en grados])
                if t > t0:
                    w = min(1.0, (t - t0) / (t1 - t0))
                    w = w * w * w if curva == "in" else (w if curva == "lineal" else suave(w))
                    x += mx * w
                    y += my * w
                    if len(m) > 5:
                        rot += m[5] * w
                    if len(m) > 6:                                 # (..., giro, escala): achicar/agrandar
                        esc *= 1 + (m[6] - 1) * w
            ent = e.get("entrada", "cae")
            if u < 1:
                if ent == "cae":
                    esc *= 1.18 - 0.18 * suave(u)
                    y -= 30 * (1 - suave(u))
                    rot += 5 * (1 - u)
                elif ent == "golpe":
                    esc *= 1.6 - 0.6 * suave(u ** 0.5)
                elif ent == "desliza":
                    dx, dy = e.get("desde_dir", (-1, 0))
                    x += dx * 1400 * (1 - suave(u))
                    y += dy * 900 * (1 - suave(u))
                    rot += 8 * (1 - u) * (1 if dx >= 0 else -1)
                elif ent == "aparece":                         # tranquilo: sube un poco y se funde
                    y += 22 * (1 - suave(u))
            if e.get("_cuadros"):
                j = min(len(e["_cuadros"]) - 1, int((tk - e["t"]) * FPS))
                img = recorte_cuadro(e["_cuadros"][j], seed=i)
            elif e.get("fn"):                                     # animación propia: un cuadro RGBA por instante
                img = e["fn"](tk - e["t"])
            else:
                img = e["img"]
            if ent == "aparece" and u < 1:
                img = img.copy()
                img.putalpha(img.split()[3].point(lambda v, k=suave(u): int(v * k)))
            if ent == "trazo" and u < 1:                       # tiza que se dibuja de izquierda a derecha
                img = img.copy()
                a = img.split()[3]
                corte = int(img.width * suave(u))
                a.paste(0, (corte, 0, img.width, img.height))
                img.putalpha(a)
            vivo = 0.0 if (e.get("_cuadros") is None and u >= 1) or e.get("fn") else 1.0
            x += jit.uniform(-1, 1) * vivo
            y += jit.uniform(-1, 1) * vivo
            pegar(f, img, x, y, esc, rot)
            if i in hacer:
                L[i] = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                pegar(L[i], img, x, y, esc, rot)
        sac = sum(fz * max(0, 1 - (t - ts) / 0.5) for ts, fz in sacudones if t >= ts)
        if sac:
            ang, tx, ty = jit.uniform(-1, 1) * sac * 0.4, jit.uniform(-1, 1) * sac * 6, jit.uniform(-1, 1) * sac * 6
            f = f.rotate(ang, resample=Image.BICUBIC, translate=(tx, ty))
            L = {i: c.rotate(ang, resample=Image.BICUBIC, translate=(tx, ty)) for i, c in L.items()}
        if camara:
            z, cx, cy = _camara(camara, tk)
            if z > 1.0001:
                cw, ch = W / z, H / z
                x0 = min(max(0, cx - cw / 2), W - cw)
                y0 = min(max(0, cy - ch / 2), H - ch)
                f = f.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
        if tk < vhs_hasta:                                     # arranque: pantalla de VHS con ruido y PLAY
            f = vhs_play(k)
            if vvhs:
                vvhs(f.convert("RGBA"))
        elif vvhs:
            vvhs.cerrar()
            vvhs = None
        if v:
            v(grano(f, k))
        for i, c in L.items():
            if i not in vc:
                vc[i] = Capa(dcap / f"{nombres[i]}.mov", movida=bool(elementos[i].get("_cuadros") or elementos[i].get("fn")) or elementos[i].get("entrada") == "trazo")
                primer[i] = k
            vc[i](c)
    if v:
        v.cerrar()
    for c in vc.values():
        c.cerrar()
    if capas:                                              # índice de capas para armar el .fcproj
        ij = dcap / "capas.json"
        viejo = json.load(open(ij)) if solo and ij.exists() else {}
        prev = {c["archivo"]: c for c in viejo.get("capas", [])}
        lista = []
        for i, n in enumerate(nombres):
            c = prev.get(f"{n}.mov") or {"archivo": f"{n}.mov", "nombre": n[3:]}
            if i in primer:
                c["inicio"] = round(primer[i] / FPS, 4)
            lista.append(c)
        viejo.update({"duracion": dur, "fps": FPS, "fondo": "00_fondo.png", "vhs": "99_vhs.mov" if vhs_hasta else None,
                      "vhs_hasta": vhs_hasta, "capas": lista})
        json.dump(viejo, open(ij, "w"), indent=1)


def _camara(keys, t):
    if t <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if t < b[0]:
            w = suave((t - a[0]) / (b[0] - a[0]))
            return tuple(a[i] + (b[i] - a[i]) * w for i in (1, 2, 3))
    return keys[-1][1:]


def vhs_play(k):
    rng = np.random.default_rng(k)
    n = rng.integers(0, 60, (H // 3, W // 3)).astype("uint8")
    im = Image.fromarray(n).resize((W, H), Image.NEAREST).convert("RGBA")
    d = ImageDraw.Draw(im)
    if (k // 15) % 2 == 0:
        d.text((110, 90), "▶ PLAY", font=fuente(64), fill=(235, 235, 235))
    d.text((110, 960), "SP  0:00:0" + str(k // 30), font=fuente(44), fill=(235, 235, 235))
    return im


def hoja(nombre, ancho=None):
    """Piezas de una hoja sobre magenta (objetos80, efimera80, cinta, papel_rasgado), ordenadas de izq. a der."""
    ps = piezas(nombre)
    if ancho:
        ps = [p.resize((int(ancho), int(p.height * ancho / p.width)), Image.LANCZOS) for p in ps]
    return ps


# ─────────────────────────────── sonido ───────────────────────────────
SON = RAIZ / "proyectos/argentina-1986/material/sonidos"      # sonidos CC0 de Openverse (herramientas/sonidos.py)
SONIDO_GRUPO = {"objetos": ["plastico1", "plastico2", "plastico3", "caida_corta"],
                "papeles": ["papel1", "papel2", "papel3"],
                "iconos": ["libro_cae", "caida_corta", "carta"],
                "sellos": ["sello_thump", "libro_cae"], "tiza": ["tiza"], "clip": ["carta", "libro_cae"]}


def _pico(ruta):
    """Segundo donde el audio suena más fuerte (para alinear el paso de un auto o un avión con la imagen)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ruta), "-ac", "1", "-ar", "1000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    a = np.abs(np.frombuffer(raw, dtype="int16").astype(float))
    if len(a) < 50:
        return 0.0
    env = np.convolve(a, np.ones(100) / 100, mode="same")
    return float(np.argmax(env)) / 1000


def sonidos_de(elementos):
    """Pista de efectos a partir de los elementos de la pila: cada cosa que cae suena según su grupo; un
    "sonido": {"archivo", "vol", "desde", "dur", "pico": True} propio manda sobre el del grupo."""
    cues, cuenta = [], {}
    for e in elementos:
        sd = e.get("sonido")
        if sd is False:
            continue
        if not sd:
            g = e.get("grupo", "objetos")
            lista = SONIDO_GRUPO.get(g, SONIDO_GRUPO["objetos"])
            n = cuenta.get(g, 0)
            cuenta[g] = n + 1
            sd = {"archivo": lista[n % len(lista)], "vol": 0.7}
        sd = dict(sd)
        ruta = SON / (sd["archivo"] + ".mp3") if not str(sd["archivo"]).startswith("/") else Path(sd["archivo"])
        desde = float(sd.get("desde", 0))
        t = e["t"] + (e.get("dura", 0.2) * 0.8 if e.get("entrada", "cae") in ("cae", "golpe") else 0)
        if sd.get("pico"):
            desde = max(0.0, _pico(ruta) - sd.get("antes", 0.6))
            t = e["t"] + e.get("dura", 0.3) * 0.5 - sd.get("antes", 0.6) + 0.6
        cues.append({"archivo": str(ruta), "en": round(max(0, t + sd.get("corre", 0)), 3), "desde": desde,
                     "dur": sd.get("dur", 2.5), "vol": sd.get("vol", 0.7)})
    return cues


def mezclar(video, cues, salida, voz=None, voz_en=0.0):
    """Preview con sonido: efectos (y la voz del narrador, si se pasa) sobre el video mudo. voz puede ser una ruta
    (con voz_en) o una lista [(ruta, en)] con varias frases."""
    voces = voz if isinstance(voz, list) else ([(voz, voz_en)] if voz else [])
    cues = list(cues) + [{"archivo": str(r), "en": en, "desde": 0, "dur": 60, "vol": 1.0, "_voz": True} for r, en in voces]
    voz = None
    ins, fil = ["-i", str(video)], []
    for i, c in enumerate(cues, 1):
        ins += ["-i", c["archivo"]]
        ms = int(c["en"] * 1000)
        fil.append(f"[{i}:a]atrim={c['desde']}:{c['desde'] + c['dur']},asetpts=PTS-STARTPTS,afade=t=out:st={max(0, c['dur'] - 0.3)}:d=0.3,"
                   f"volume={c['vol']},adelay={ms}|{ms},aformat=channel_layouts=stereo[a{i}]")
    n = len(cues)
    if voz:
        ins += ["-i", str(voz)]
        ms = int(voz_en * 1000)
        fil.append(f"[{n + 1}:a]adelay={ms}|{ms},volume=1.0,aformat=channel_layouts=stereo[a{n + 1}]")
        n += 1
    fil.append("".join(f"[a{i}]" for i in range(1, n + 1)) + f"amix=inputs={n}:normalize=0:duration=longest,alimiter=limit=0.7:level=0,apad[mix]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fil), "-map", "0:v", "-map", "[mix]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", str(salida)], check=True)


def voz_escena(guion_tmp, n):
    """Voz (mp3 del caché) e inicio de la escena n de un render previo (tmp_guion_x/linea.json)."""
    l = json.load(open(guion_tmp / "linea.json"))
    v = l["voces"][n]
    ruta = Path(v["archivo"])
    if not ruta.exists():
        ruta = RAIZ / ".cache" / "elevenlabs" / ruta.name
    ini = [p for p in l["piezas"] if p["escena"] == n + 1][0]["inicio"]
    return ruta, v["inicio"] - ini


VHS_MENOS = 1.0     # segundos que se le sacan al arranque de VHS de la intro (17/11)


def intro_1986(salida, capas=False, solo=None):
    """Momento 1 de la intro: 'Mil novecientos ochenta y seis. El mundo estaba completamente loco... y el fútbol no
    se quedaba atrás.' VHS -> sello 1986 -> pila de los 80 -> clip de Bélgica en polaroid."""
    M = RAIZ / "proyectos/argentina-1986/material"
    R = M / "intro/recortes"
    obj = piezas("objetos80")        # vhs, walkman con auriculares, cubo, joystick, zapatillas
    efi = piezas("efimera80")        # entrada, carta de ajuste, diario, sticker, película, polaroid
    cin = piezas("cinta")
    tiza = piezas("tiza")
    rnd = random.Random(7)

    def fig(im, ancho):
        return figurita(im.resize((int(ancho), int(im.height * ancho / im.width)), Image.LANCZOS), seed=int(ancho))

    E = []

    def pon(img, x, y, t, rot=None, **kw):
        E.append(dict(img=img, x=x, y=y, t=t, rot=rnd.uniform(-9, 9) if rot is None else rot, **kw))

    # 2.4 "Mil novecientos ochenta y seis": el sello
    pon(sello("1986", 300), 960, 520, 2.45, rot=0, entrada="golpe", dura=0.12, grupo="sellos")
    # objetos chicos que caen alrededor
    pon(fig(obj[2], 230), 420, 300, 3.05, grupo="objetos")           # cubo
    pon(fig(recorte_png(R / "cassette.png"), 520), 1450, 300, 3.3, grupo="objetos")
    pon(fig(obj[3], 220), 1560, 760, 3.55, grupo="objetos")          # joystick
    pon(figurita(efi[0].resize((420, int(efi[0].height * 420 / efi[0].width)))), 380, 800, 3.8, grupo="papeles")
    pon(fig(obj[0], 420), 640, 160, 4.05, grupo="objetos")           # vhs
    # 4.73 "El mundo estaba completamente loco": la pila se desborda
    pon(fig(recorte_png(R / "mr_t.png"), 460), 520, 560, 4.8, grupo="iconos")
    pon(figurita(efi[1].resize((520, int(efi[1].height * 520 / efi[1].width)))), 1380, 520, 5.05, grupo="papeles")
    pon(fig(recorte_png(R / "madonna.png"), 400), 1420, 600, 5.3, grupo="iconos")
    pon(fig(recorte_png(R / "delorean.png"), 760), 900, 820, 5.6, entrada="desliza", desde_dir=(-1, 0.1), dura=0.3,
        rot=-4, grupo="iconos")
    pon(fig(recorte_png(R / "f14.png"), 900), 1100, 230, 5.95, entrada="desliza", desde_dir=(1, -0.3), dura=0.28,
        rot=8, grupo="iconos")
    pon(fig(obj[1], 520), 330, 330, 6.25, grupo="objetos")           # walkman
    pon(figurita(efi[2].resize((480, int(efi[2].height * 480 / efi[2].width)))), 1560, 900, 6.45, grupo="papeles")
    pon(fig(obj[4], 420), 760, 980, 6.65, grupo="objetos")           # zapatillas
    pon(figurita(efi[3].resize((200, int(efi[3].height * 200 / efi[3].width)))), 1250, 420, 6.85, grupo="papeles")
    # (17/11, nota del usuario: sin la tiza que rodeaba a Mr. T)
    # 7.51 "y el fútbol no se quedaba atrás": cosas locas del fútbol del 86 (16/11, en vez del clip de Bélgica)
    ola = Image.open(M / "intro/ola_azteca.jpg").convert("RGB")
    ola = ola.resize((1100, int(ola.height * 1100 / ola.width)), Image.LANCZOS)
    pon(recorte_cuadro(ola, seed=5), 980, 470, 7.55, rot=-3, grupo="futbol")                    # la ola en el Azteca
    pon(fig(recorte_png(R / "valderrama_cali.png"), 640), 500, 600, 7.95, rot=4, grupo="futbol")   # el Pibe, Cali 86
    pon(fig(recorte_png(R / "pique_azteca.png"), 520), 1480, 560, 8.4, rot=-6, grupo="futbol")    # Pique, la mascota
    pon(figurita(tarjeta_roja(250)), 1290, 880, 8.85, rot=14, entrada="golpe", dura=0.12, grupo="futbol")  # Batista
    pon(sello("56 SEG", 130), 1580, 900, 9.15, rot=-8, entrada="golpe", dura=0.1, grupo="sellos")

    # ── tramo 2 (voz 10.27): "Se jugaba la decimotercera edición de la Copa del Mundo."
    # los doce afiches anteriores caen cada vez más rápido encima de todo; el 13º (México 86) cae grande + sello XIII
    A = M / "intro/afiches"
    anios = [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 1978, 1982]
    lugares = [(330, 300), (1590, 320), (760, 760), (1260, 700), (520, 520), (1450, 880), (1000, 260), (300, 860),
               (1660, 560), (720, 250), (1180, 470), (860, 600)]
    t = 10.32
    for n, (an, (x, y)) in enumerate(zip(anios, lugares)):
        im = afiche(next(A.glob(f"{an}.*")), 330 + (n % 3) * 30)
        pon(im, x, y, round(t, 3), grupo="afiches", nombre=f"afiche_{an}",
            sonido={"archivo": f"papel{n % 3 + 1}", "dur": 0.5, "vol": 0.55})
        t += 0.17 - 0.1 * n / 11                                   # se acelera: 0.17 s -> 0.07 s
    pon(afiche(A / "1986.png", 820, margen=0.12), 960, 520, 11.78, rot=-2, entrada="golpe", dura=0.14,
        grupo="afiches", nombre="afiche_1986", sonido={"archivo": "libro_cae", "vol": 0.8})
    pon(sello("XIII", 150), 1250, 330, 12.2, rot=-9, entrada="golpe", dura=0.1, grupo="sellos", nombre="sello_XIII")
    pon(tira("LA COPA DEL MUNDO", 54, seed=2), 960, 930, 12.75, rot=1.5, grupo="papeles", nombre="tira_copa",
        sonido={"archivo": "carta", "vol": 0.6})

    # ── tramo 3 (15.11, voz 16.61): "La sede: México." — 17/11 (nota del usuario): la Tierra en 3D sin borde
    # blanco, la cámara baja desde el espacio hasta México y, cuando dice "México", el país se marca en el mapa
    # (antes: foto de la Tierra con borde, satélite del DF y el Azteca). herramientas/globo.py
    import globo
    g = globo.Globo(pais="Mexico", centro=(23.5, -102.0), t_zoom=(0.25, 1.85), t_marca=1.95)
    E.append(dict(img=None, fn=g.cuadro, x=W / 2, y=H / 2, t=15.15, rot=0, entrada="aparece", dura=0.35,
                  grupo="mexico", nombre="globo_mexico", sonido={"archivo": "whoosh_grave", "vol": 0.7}))
    E.append(dict(img=None, x=0, y=0, t=15.9, grupo="mexico", sonido={"archivo": "whoosh_rapido", "vol": 0.5}))
    band = Image.open(M / "intro/banderas/mexico.png").convert("RGB").resize((440, 252), Image.LANCZOS)
    pon(recorte_cuadro(band, seed=13), 1620, 200, 17.45, rot=8, entrada="golpe", dura=0.12, grupo="mexico",
        nombre="bandera_mexico", sonido={"archivo": "carta", "vol": 0.7})
    pon(tira("MÉXICO", 104, seed=3), 960, 960, 17.2, rot=-4, entrada="golpe", dura=0.1, grupo="sellos",
        nombre="sello_mexico", sonido={"archivo": "sello_thump", "vol": 0.85})
    # 17/11 (nota en el Vibe Editor): "el ruido de VHS está medio largo, algún visitante no aguanta ese segundo":
    # el PLAY dura 1 s menos y toda la pieza se adelanta ese segundo (las voces, en mezcla_intro.py)
    for e in E:
        e["t"] = round(e["t"] - VHS_MENOS, 3)
    E.insert(0, dict(img=None, x=0, y=0, t=0.0, grupo="vhs", sonido={"archivo": "vhs_entra", "dur": 2.3 - VHS_MENOS,
                                                                    "vol": 0.8}))
    E.insert(1, dict(img=None, x=0, y=0, t=0.3, grupo="vhs", sonido={"archivo": "estatica", "desde": 3,
                                                                    "dur": 1.9 - VHS_MENOS, "vol": 0.25}))
    for e in E:
        if e.get("entrada") == "desliza" and e["x"] == 900:      # DeLorean
            e["sonido"] = {"archivo": "auto_pasa", "pico": True, "dur": 1.6, "vol": 0.8}
        elif e.get("entrada") == "desliza":                       # F-14
            e["sonido"] = {"archivo": "avion_pasa", "pico": True, "dur": 2.0, "vol": 0.8}
    salida = Path(salida)
    vis = [e for e in E if e.get("img") is not None or e.get("video") or e.get("fn")]
    for e, n in zip(vis, ["sello_1986", "cubo", "cassette", "joystick", "entrada", "vhs", "mr_t", "carta_ajuste",
                          "madonna", "delorean", "f14", "walkman", "diario", "zapatillas", "sticker",
                          "la_ola", "valderrama", "pique", "tarjeta_roja", "sello_56seg"]):
        e["nombre"] = n
    pila(salida, vis, 19.15 - VHS_MENOS, sacudones=[(t - VHS_MENOS, f) for t, f in [(2.45, 2.0), (6.1, 1.2), (7.55, 1.6),
                                                                              (11.78, 1.5), (12.2, 1.0), (17.2, 1.6)]],
         capas=capas, vhs_hasta=2.3 - VHS_MENOS, solo=solo)
    if solo:
        return
    cues = sonidos_de(E)
    json.dump(cues, open(salida.with_suffix(".sonidos.json"), "w"), indent=1)
    # voces de las escenas 1-3 en su lugar de la línea de tiempo de la intro (la intro arranca en 0)
    l = json.load(open(RAIZ / "proyectos/argentina-1986/tmp_guion_intro/linea.json"))
    voces = []
    for v in l["voces"][:3]:
        ruta = Path(v["archivo"])
        if not ruta.exists():
            ruta = RAIZ / ".cache" / "elevenlabs" / ruta.name
        voces.append((ruta, v["inicio"]))
    mezclar(salida, cues, salida.with_name(salida.stem + "_con_sonido.mp4"), voces)
    if capas:                                              # la voz va en el .fcproj (filmcraft.py capas)
        ij = salida.with_name(salida.stem + "_capas") / "capas.json"
        d = json.load(open(ij))
        d["voces"] = [{"archivo": str(r), "inicio": round(en, 3)} for r, en in voces]
        d.pop("voz", None)
        json.dump(d, open(ij, "w"), indent=1)


# ─────────────────────────── intro: tramos del medio ───────────────────────────
# Escenas 4-6 de guion_intro (24 selecciones / Maradona / "volar la peluca"). Tres piezas encadenadas: cada una
# arranca encima del último cuadro de la anterior (intro_1986_c -> medio_a -> medio_b -> medio_c -> cierre).
# Tiempos de palabra con whisper local; t = 0 es el arranque de la escena (retardo incluido).
FF6 = (200, 175, 1700, 960)          # recorte de los clips de Football Flashback 6: sin marcador, logo ni URL
PERU = (0, 62, 480, 352)             # Argentina-Perú 1985: sin el texto ruso de arriba ni el "9" de Canal 9
VOCES_MEDIO = {"a": ("voz_73a6b0899b4b418f", 0.0), "b": ("voz_2280341ee2692f81", 0.9), "c": ("voz_9d036defafe9497b", 0.0)}
DUR_MEDIO = {"a": 8.8, "b": 16.18, "c": 12.0}
# (17/11) la pieza b (Maradona/Napoli/millones) salió de la intro: la c arranca sobre la a. Versiones _v2.
ANTES_MEDIO = {"a": "intro_1986_c.mp4", "b": "intro_1986_medio_a_v2.mp4", "c": "intro_1986_medio_a_v2.mp4"}


def camino_animado(puntos, nombres, t0, t1, color=ROJO):
    """Camino punteado que se dibuja de t0 a t1 (tiempo de la pieza) por los puntos; en cada parada (puntos[1:])
    aparece un punto y una tira con el nombre. Devuelve fn(dt) -> RGBA W×H (dt desde que entra el elemento, que
    tiene que entrar en t0 - 0.1)."""
    import math as _m
    segs = list(zip(puntos[:-1], puntos[1:]))
    largos = [_m.dist(a, b) for a, b in segs]
    total = sum(largos)
    acum = [sum(largos[:i + 1]) for i in range(len(largos))]
    tiras = [tira(n, 52, fondo=TINTA, seed=30 + i).rotate((-1) ** i * 3, expand=True, resample=Image.BICUBIC)
             for i, n in enumerate(nombres)]
    cache = {}

    def fn(dt):
        t = dt + (t0 - 0.1)
        u = suave((t - t0) / (t1 - t0))
        k = round(u, 3)
        if k in cache:
            return cache[k]
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        L = u * total
        recorrido = 0.0
        for (a, b), lg in zip(segs, largos):                      # guiones de 26 px con 18 de aire, continuos
            if recorrido >= L:
                break
            n = int(lg // 4)
            for j in range(n):
                s0 = recorrido + j * lg / n
                if s0 >= L:
                    break
                if (s0 % 44) < 26:
                    f0, f1 = j / n, min(1, (j + 1) / n)
                    d.line([(a[0] + (b[0] - a[0]) * f0, a[1] + (b[1] - a[1]) * f0),
                            (a[0] + (b[0] - a[0]) * f1, a[1] + (b[1] - a[1]) * f1)], fill=color + (255,), width=9)
            recorrido += lg
        # la punta: un puntito que va adelante
        if 0 < u < 1:
            i = next(i for i, c in enumerate(acum) if c >= L)
            a, b = segs[i]
            f = 1 - (acum[i] - L) / largos[i]
            px, py = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
            d.ellipse((px - 11, py - 11, px + 11, py + 11), fill=color + (255,))
        for i, (p, tr) in enumerate(zip(puntos[1:], tiras)):
            llegada = acum[i] / total
            if u + 1e-6 < llegada:
                continue
            e = min(1.0, (t - (t0 + (t1 - t0) * llegada)) / 0.18) if u < 1 else 1.0
            e = max(0.0, e)
            r = 17 * (0.6 + 0.4 * e)
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=CREMA + (255,), outline=color + (255,), width=7)
            esc = 0.7 + 0.3 * suave(e)
            tt = tr.resize((int(tr.width * esc), int(tr.height * esc)), Image.LANCZOS)
            dy = -58 if p[1] > 260 else 58
            x = int(min(W - tt.width - 10, max(10, p[0] - tt.width / 2)))
            im.alpha_composite(tt, (x, int(p[1] + dy - tt.height / 2)))
        cache[k] = im
        return im
    return fn


def naipe(foto, alto=460):
    """El as bajo la manga: carta de cartulina con una A roja en las esquinas y una foto en el centro."""
    w = int(alto * 0.66)
    c = Image.new("RGBA", (w, alto), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w - 1, alto - 1), radius=22, fill=(244, 240, 228, 255), outline=(60, 50, 40, 255), width=3)
    d.rounded_rectangle((14, 14, w - 15, alto - 15), radius=14, outline=ROJO + (255,), width=3)
    f = foto.convert("RGB")
    fw, fh = w - 90, alto - 150
    esc = max(fw / f.width, fh / f.height)                       # que la foto llene el centro de la carta
    f = f.resize((int(f.width * esc) + 1, int(f.height * esc) + 1), Image.LANCZOS)
    x0 = (f.width - fw) // 2
    f = f.crop((x0, 0, x0 + fw, fh))
    c.paste(f, (45, 75))
    fa = fuente(int(alto * 0.13), 800)
    d.text((26, 18), "A", font=fa, fill=ROJO + (255,))
    d2 = Image.new("RGBA", c.size, (0, 0, 0, 0))
    ImageDraw.Draw(d2).text((26, 18), "A", font=fa, fill=ROJO + (255,))
    c.alpha_composite(d2.rotate(180))
    return figurita(c, seed=41)


def _cerrar_pieza(salida, E, dur, base, voces, capas, solo, sacudones):
    pila(salida, E, dur, base=base, capas=capas, solo=solo, sacudones=sacudones)
    if solo:
        return
    salida = Path(salida)
    cues = sonidos_de(E)
    json.dump(cues, open(salida.with_suffix(".sonidos.json"), "w"), indent=1)
    mezclar(salida, cues, salida.with_name(salida.stem + "_con_sonido.mp4"), voces)
    if capas:
        ij = salida.with_name(salida.stem + "_capas") / "capas.json"
        d = json.load(open(ij))
        d["voces"] = [{"archivo": str(r), "inicio": en} for r, en in voces]
        json.dump(d, open(ij, "w"), indent=1)


def medio_1986(parte, salida, capas=False, solo=None):
    M = RAIZ / "proyectos/argentina-1986/material"
    R = M / "intro/recortes"
    F = M / "fuentes"
    G = RAIZ / "proyectos/argentina-1986/salida/graficos"
    base = ultimo_cuadro(G / ANTES_MEDIO[parte])
    tiza = piezas("tiza")
    rnd = random.Random(80 + ord(parte))
    E = []

    def pon(img, x, y, t, rot=None, **kw):
        E.append(dict(img=img, x=x, y=y, t=t, rot=rnd.uniform(-7, 7) if rot is None else rot, **kw))

    def foto(ruta, ancho, caja=None):
        im = Image.open(ruta).convert("RGB")
        if caja:
            im = im.crop(caja)
        return im.resize((int(ancho), int(im.height * ancho / im.width)), Image.LANCZOS)

    def clip(nombre, ruta, desde, vel, rec, ancho, x, y, t, vdur, rot=None, **kw):
        E.append(dict(img=None, video=(ruta, desde, vel, rec, ancho), vdur=vdur, x=x, y=y, t=t, nombre=nombre,
                      rot=rnd.uniform(-5, 5) if rot is None else rot, grupo="clip", **kw))

    voz, en = VOCES_MEDIO[parte]
    voces = [(RAIZ / ".cache/elevenlabs" / f"{voz}.mp3", en)]

    if parte == "a":
        # "Veinticuatro selecciones buscando la gloria eterna. Y entre ellas, Argentina... un equipo que guardaba un as
        # bajo la manga." (versión corta, 17/11)
        pon(sello("24", 340, rot=-6), 960, 520, 0.05, rot=0, entrada="golpe", dura=0.12, grupo="sellos",
            nombre="sello_24", sonido={"archivo": "sello_thump", "vol": 0.9})
        paises = ["italy", "bulgaria", "south_korea", "mexico", "paraguay", "belgium", "iraq", "soviet_union", "france",
                  "hungary", "canada", "brazil", "spain", "northern_ireland", "algeria", "denmark", "germany",
                  "uruguay", "scotland", "morocco", "england", "poland", "portugal"]
        for n, p in enumerate(paises):
            t = 0.45 + n * 0.125
            pon(recorte_cuadro(foto(M / f"intro/banderas/{p}.png", rnd.randint(230, 300)), seed=n), rnd.uniform(160, 1760),
                rnd.uniform(130, 950), round(t, 3), grupo="banderas", nombre=f"bandera_{p}",
                sonido={"archivo": f"papel{n % 3 + 1}", "dur": 0.4, "vol": 0.4})
        pon(recorte_cuadro(foto(M / "intro/banderas/argentina.png", 760), seed=50), 960, 520, 4.29, rot=-3,
            entrada="golpe", dura=0.14, grupo="banderas", nombre="bandera_argentina",
            sonido={"archivo": "libro_cae", "vol": 0.35})       # 17/11 (Vibe Editor): "muy fuerte" (era 0.9)
        # (17/11, Vibe Editor: "no más tiza")
        # 17/11 (Vibe Editor): guion más corto, sin "llegaba al límite, sufriendo, cuestionado por todos, pero"
        # (salieron la tribuna de 1985, SUFRIENDO, Bilardo tachado y CUESTIONADO): de Argentina va directo al as
        diego = foto(M / "eg_tapa_3427.jpg", 400, caja=(15, 75, 228, 340))     # solo la foto, sin logo ni títulos
        pon(naipe(diego, 640), 960, 560, 6.7, rot=8, entrada="desliza", desde_dir=(0, 1), dura=0.5, grupo="iconos",
            nombre="as_bajo_la_manga", mov=[(7.2, 7.35, 0, -20, "s", -6)], sonido={"archivo": "carta", "vol": 0.9})
        sac = [(0.05, 1.4), (4.29, 1.8), (7.39, 1.2)]

    elif parte == "b":
        # "Tenía a Diego Armando Maradona. El pibe de Fiorito, la estrella absoluta del Napoli, que venía de romper el
        # mercado siendo el fichaje más caro de la historia: siete millones y medio de dólares. Una verdadera locura."
        o = 0.9
        clip("napoli_llega", F / "napoli1984.mp4", 84.5, 0.5, (0, 0, 1280, 720), 900, 760, 500, o + 0.05, 3.4, rot=2)
        pon(tira("DIEGO ARMANDO MARADONA", 62, seed=8), 900, 880, o + 1.38, rot=-2, entrada="golpe", dura=0.1,
            grupo="papeles", nombre="tira_maradona", sonido={"archivo": "sello_thump", "vol": 0.8})
        pon(tira("VILLA FIORITO", 56, fondo=TINTA, seed=9), 1480, 200, o + 2.89, rot=5, grupo="papeles",
            nombre="tira_fiorito", sonido={"archivo": "carta", "vol": 0.6})
        clip("napoli_estadio", F / "napoli1984.mp4", 93.5, 0.5, (0, 0, 1280, 720), 780, 1260, 520, o + 3.9, 3.0, rot=-4)
        pon(tira("NAPOLI · 1984", 56, seed=10), 1380, 300, o + 5.37, rot=3, grupo="papeles", nombre="tira_napoli",
            sonido={"archivo": "carta", "vol": 0.6})
        pon(marco_polaroid(foto(M / "maradona_napoli_fotografos.jpg", 700)), 680, 520, o + 6.3, rot=-5,
            grupo="iconos", nombre="fotografos", sonido={"archivo": "papel2", "vol": 0.7})
        pon(tira("BARCELONA → NÁPOLES", 52, fondo=TINTA, seed=11), 760, 170, o + 6.47, rot=-3, grupo="papeles",
            nombre="tira_pase", sonido={"archivo": "carta", "vol": 0.6})
        pon(tira("EL PASE MÁS CARO DE LA HISTORIA", 58, seed=12), 1100, 900, o + 8.22, rot=-2, entrada="golpe",
            dura=0.1, grupo="papeles", nombre="tira_mas_caro", sonido={"archivo": "sello_thump", "vol": 0.85})
        bill = Image.open(M / "intro/dolar.jpg").convert("RGB")
        for n in range(9):
            b = bill.resize((420, int(bill.height * 420 / bill.width)), Image.LANCZOS)
            pon(recorte_cuadro(b, seed=60 + n), rnd.uniform(250, 1670), rnd.uniform(200, 880), round(o + 10.14 + n * 0.11, 3),
                grupo="billetes", nombre=f"billete_{n + 1}", sonido={"archivo": "papel3" if n % 2 else "papel1",
                                                                      "dur": 0.4, "vol": 0.45})
        pon(tira("US$ 7.500.000", 120, seed=13), 960, 540, o + 11.21, rot=-3, entrada="golpe", dura=0.12,
            grupo="sellos", nombre="tira_millones", sonido={"archivo": "libro_cae", "vol": 0.95})
        pon(sello("LOCURA", 150, rot=8), 1450, 820, o + 12.98, rot=0, entrada="golpe", dura=0.1, grupo="sellos",
            nombre="sello_locura", sonido={"archivo": "sello_thump", "vol": 0.9})
        sac = [(o + 1.38, 0.8), (o + 8.22, 0.9), (o + 11.21, 2.0), (o + 12.98, 1.4)]

    else:
        # "En este video vamos a desenmarañar el camino de la Selección dirigida por Bilardo y el gran Diego hasta
        # tocar el cielo con las manos: los partidos, el lado B de las anécdotas, los pormenores que nadie te contó...
        # y unos datos que literalmente te van a volar la peluca."
        pon(tira("EL CAMINO", 70, fondo=TINTA, seed=14), 470, 150, 2.17, rot=-4, grupo="papeles", nombre="tira_camino",
            sonido={"archivo": "carta", "vol": 0.6})
        # 17/11 (Vibe Editor): texto más corto, sin "la selección dirigida por Bilardo y el gran Diego hasta tocar el
        # cielo con las manos" (lo dice el cierre). Sale Bilardo y dos clips; quedan Corea, Italia y Uruguay.
        clip("corea", F / "corea.mp4", 195.5, 0.6, FF6, 860, 640, 600, 2.5, 2.2, rot=-3)
        clip("italia", F / "italia.mp4", 266.0, 0.8, FF6, 820, 1180, 420, 3.1, 1.8, rot=4)
        # "el camino" (Vibe Editor: "sacá esa tiza horrible... el camino hace un camino con cada uno de los partidos,
        # una animación"): línea punteada roja que se dibuja por la pantalla y para en cada partido, en orden; la
        # final queda como "LA FINAL" (sin rival ni resultado: sin spoilers)
        paradas = [("COREA", 150, 900), ("ITALIA", 430, 700), ("BULGARIA", 300, 470), ("URUGUAY", 640, 300),
                   ("INGLATERRA", 1000, 470), ("BÉLGICA", 1330, 300), ("LA FINAL", 1720, 180)]
        T0, T1 = 2.25, 5.6
        camino_fn = camino_animado([(40, 1040)] + [(x, y) for _, x, y in paradas], [n for n, _, _ in paradas], T0, T1)
        pon(tira("LOS PARTIDOS", 62, seed=15), 1320, 900, 3.16, rot=-3, entrada="golpe", dura=0.1, grupo="papeles",
            nombre="tira_partidos", sonido={"archivo": "sello_thump", "vol": 0.7})
        pon(marco_polaroid(foto(M / "eg_comedor.jpg", 720)), 860, 560, 4.46, rot=5, grupo="iconos", nombre="comedor",
            sonido={"archivo": "papel2", "vol": 0.7})
        pon(tira("EL LADO B", 80, fondo=TINTA, seed=16), 1420, 230, 4.73, rot=4, entrada="golpe", dura=0.1,
            grupo="papeles", nombre="tira_lado_b", sonido={"archivo": "sello_thump", "vol": 0.8})
        clip("uruguay", F / "uruguay.mp4", 94.0, 0.6, FF6, 820, 680, 600, 5.6, 1.9, rot=-4)
        pon(tira("LO QUE NADIE TE CONTÓ", 66, seed=17), 1150, 880, 6.32, rot=2, entrada="golpe", dura=0.1,
            grupo="papeles", nombre="tira_nadie_conto", sonido={"archivo": "sello_thump", "vol": 0.85})
        # el camino va ENCIMA de los clips y del comedor (si no, quedaba tapado), debajo de Diego
        E.append(dict(img=None, fn=camino_fn, x=W / 2, y=H / 2, t=T0 - 0.1, rot=0, entrada="aparece", dura=0.1,
                      grupo="camino", nombre="camino_partidos", sonido={"archivo": "whoosh_rapido", "vol": 0.45}))
        for k in range(len(paradas)):                              # un golpecito de papel en cada parada
            tk = T0 + (k + 1) / len(paradas) * (T1 - T0)
            E.append(dict(img=None, x=0, y=0, t=round(tk, 2), grupo="camino",
                          sonido={"archivo": f"papel{k % 3 + 1}", "dur": 0.35, "vol": 0.45}))
        # "te van a volar la peluca": Diego cae entero; con "peluca" el afro sale volando (ráfaga de tinta)
        r = Image.open(M / "recorte_maradona_italia.png").convert("RGBA")
        mk = Image.new("L", r.size, 0)
        ImageDraw.Draw(mk).polygon([(0, 0), (420, 0)] + PELO_CURVA[::-1], fill=255)
        mk = mk.filter(ImageFilter.GaussianBlur(1.5))
        pelo = r.copy()
        pelo.putalpha(ImageChops.multiply(mk, r.split()[3]))
        bb = pelo.getbbox()
        sin = r.copy()
        sin.putalpha(ImageChops.multiply(ImageChops.invert(mk), r.split()[3]))
        cx, cy = 960, 600
        pegado = figurita(r)
        pon(pegado, cx, cy, 7.68, rot=0, hasta=10.51, grupo="peluca", nombre="diego_entero",
            sonido={"archivo": "libro_cae", "vol": 0.8})
        pon(figurita(sin), cx, cy, 10.51, rot=0, entrada="corte", grupo="peluca", nombre="diego_sin_pelo", sonido=False)
        pelo_img = figurita(pelo.crop(bb), g=7)
        px = cx + ((bb[0] + bb[2]) / 2 - r.width / 2)
        py = cy + ((bb[1] + bb[3]) / 2 - r.height / 2)
        pon(pelo_img, px, py, 10.51, rot=0, entrada="corte", grupo="peluca", nombre="peluca",
            mov=[(10.51, 11.95, 1350, -720, "lineal", -520)], sonido={"archivo": "whoosh_rapido", "vol": 0.9})
        trazos = sorted(piezas("tinta"), key=lambda p: -p.width / max(1, p.height))[:3]
        for j, tr in enumerate(trazos):
            t0 = 10.2 + j * 0.06                                  # la ráfaga cruza toda la pantalla
            pon(tr, -700, 250 + j * 140, t0, rot=0, entrada="corte", mov=[(t0, t0 + 0.6, 3400, 0, "lineal")],
                grupo="peluca", nombre=f"rafaga_{j + 1}", hasta=t0 + 0.62,
                sonido={"archivo": "whoosh_grave", "vol": 0.6} if j == 0 else False)
        sac = [(3.16, 0.6), (4.73, 0.8), (6.32, 0.9), (7.68, 1.2), (10.51, 2.4)]

    _cerrar_pieza(salida, E, DUR_MEDIO[parte], base, voces, capas, solo, sac)


def banda(color, w, h, seed=0):
    """Franja enorme de papel rasgado teñida (para armar una bandera de papel encima de todo)."""
    t = piezas("papel_rasgado")[seed % len(piezas("papel_rasgado"))].resize((w, h), Image.LANCZOS)
    gris = Image.merge("RGB", [t.convert("L").point(lambda v: min(255, int(v * 1.08)))] * 3)
    out = ImageChops.multiply(Image.new("RGB", t.size, color), gris).convert("RGBA")
    out.putalpha(t.split()[3])
    return out


def ultimo_cuadro(ruta):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-sseof", "-0.1", "-i", str(ruta), "-frames:v", "1", "-vf",
                          f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return Image.frombytes("RGB", (W, H), raw[:W * H * 3]).convert("RGBA")


def cierre_1986(salida, capas=False, solo=None):
    """Cierre de la intro (escena 7 de guion_intro, 16/11): "Así que subite, sentate, callate y agarrate... porque esto
    es LOS ONCE. Y lo que sigue es cómo Argentina ganó su segundo Mundial: la historia de un equipo que nadie quería,
    de un pibe de Fiorito que le tocó la mano a Dios... y de un mes en el que el cielo fue celeste y blanco."
    Arranca encima del último cuadro de la peluca. Tiempos de palabra = whisper local + 0.3 s de retardo."""
    M = RAIZ / "proyectos/argentina-1986/material"
    R = M / "intro/recortes"
    G = RAIZ / "proyectos/argentina-1986/salida/graficos"
    base = ultimo_cuadro(G / "intro_1986_medio_c_v2.mp4")        # sigue la pila de los tramos del medio
    tiza = piezas("tiza")
    E = []

    def pon(img, x, y, t, rot=0.0, **kw):
        E.append(dict(img=img, x=x, y=y, t=t, rot=rot, **kw))

    def foto(ruta, ancho, caja=None):
        im = Image.open(ruta).convert("RGB")
        if caja:
            im = im.crop(caja)
        return im.resize((int(ancho), int(im.height * ancho / im.width)), Image.LANCZOS)

    # las cuatro órdenes (16/11): la frase viene de una patente de Mendoza (una chica que se sube a un auto rápido);
    # acá se da vuelta: el que se sube es "el Doctor" Bilardo, al DeLorean, que sale disparado a 1986 con las dos
    # huellas de fuego. Patente negra argentina de los 80, de Mendoza.
    auto = Image.open(R / "delorean.png").convert("RGBA")
    auto = auto.crop(auto.getbbox())                               # 714x314 (bbox 44,39 del original)
    pat = Image.new("RGBA", (120, 40), (16, 16, 16, 255))
    dp = ImageDraw.Draw(pat)
    dp.rectangle((1, 1, 118, 38), outline=(200, 200, 200, 255), width=2)
    dp.text((60, 21), "M 1986", font=fuente(24), fill=(236, 236, 236, 255), anchor="mm")
    auto.alpha_composite(pat.rotate(-4, expand=True, resample=Image.BICUBIC), (520, 192))
    ea = 1.55
    auto = auto.resize((int(auto.width * ea), int(auto.height * ea)), Image.LANCZOS)
    corte = int(70 * ea)                                           # línea del capó/parabrisas (abajo = adelante)
    frente = auto.copy()
    a = frente.split()[3]
    a.paste(0, (0, 0, auto.width, corte))
    frente.putalpha(a)
    ax, ay = 760, 650                                              # centro del auto en pantalla
    vuelo = [(3.62, 4.25, 2600, 120, "in")]                        # AGARRATE: sale disparado a la derecha
    tiembla = [(3.47, 3.52, 6, -4, "s"), (3.52, 3.57, -10, 5, "s"), (3.57, 3.62, 4, -1, "s")]
    pon(figurita(auto, seed=31), ax, ay, 0.05, entrada="desliza", desde_dir=(-1, 0.05), dura=0.45,
        grupo="delorean", nombre="delorean", mov=tiembla + vuelo, sonido={"archivo": "whoosh_grave", "vol": 0.6})
    bi = Image.open(R / "bilardo.png").convert("RGBA").crop((0, 0, 551, 380))
    eb = 0.86
    bi = bi.resize((int(bi.width * eb), int(bi.height * eb)), Image.LANCZOS)
    bx, by = ax - auto.width / 2 + (330 - 44) * ea, ay - auto.height / 2 + corte - bi.height / 2 + 40
    pon(figurita(bi, seed=32), bx, by - 10, 0.76, entrada="desliza", desde_dir=(0, -1), dura=0.22, grupo="delorean",
        nombre="bilardo", mov=[(1.69, 1.85, 0, 55, "s")] + tiembla + vuelo,
        sonido={"archivo": "caida_corta", "vol": 0.7})
    pon(frente, ax, ay, 0.05, entrada="desliza", desde_dir=(-1, 0.05), dura=0.45, grupo="delorean",
        nombre="delorean_frente", mov=tiembla + vuelo, sonido=False)
    boca = (bx - bi.width / 2 + 301 * eb, by - 10 + 55 - bi.height / 2 + 134 * eb)
    cinta = piezas("cinta")[0]
    cinta = cinta.resize((175, int(cinta.height * 175 / cinta.width)), Image.LANCZOS)
    pon(cinta, boca[0], boca[1], 2.71, rot=-8, entrada="golpe", dura=0.08, grupo="delorean", nombre="cinta_boca",
        mov=tiembla + vuelo, sonido={"archivo": "papel1", "vol": 0.8})
    # las dos huellas de fuego que deja al arrancar
    # ruedas (3/4): trasera en (64, 250) y delantera en (366, 374) desde la esquina del auto escalado
    fw, fh = 2100, 240
    fuego = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    rng = np.random.default_rng(33)
    for yy, ancho, x0 in ((60, 13, 0), (184, 16, 302)):
        lin = Image.new("L", (fw, fh), 0)
        dl = ImageDraw.Draw(lin)
        for xx in range(x0, fw, 6):
            j = rng.uniform(-2.5, 2.5)
            dl.line([(xx, yy + j), (xx + 7, yy + j)], fill=255, width=int(ancho + rng.uniform(-3, 3)))
        halo = lin.filter(ImageFilter.GaussianBlur(10)).point(lambda v: min(255, int(v * 1.6)))
        capa = Image.new("RGBA", (fw, fh), (255, 120, 20, 0))
        capa.putalpha(halo)
        fuego.alpha_composite(capa)
        nucleo = Image.new("RGBA", (fw, fh), (255, 230, 150, 0))
        nucleo.putalpha(lin.filter(ImageFilter.GaussianBlur(1.5)))
        fuego.alpha_composite(nucleo)
    x_rueda = ax - auto.width / 2 + 64 - 6
    y_rueda = ay - auto.height / 2 + 250 - 60 + fh / 2
    E.insert(0, dict(img=fuego, x=x_rueda + fw / 2, y=y_rueda + 45, t=3.64, rot=-2.6, entrada="trazo", dura=0.55,
                     grupo="delorean", nombre="fuego", sonido={"archivo": "auto_pasa", "pico": True, "dur": 1.8,
                                                               "vol": 0.9}))
    pon(tira("SUBITE", 96, seed=0), 420, 140, 0.76, rot=-7, entrada="golpe", dura=0.1, grupo="ordenes",
        nombre="subite", sonido={"archivo": "sello_thump", "vol": 0.8})
    pon(tira("SENTATE", 96, fondo=TINTA, seed=1), 1500, 150, 1.69, rot=5, entrada="golpe", dura=0.1,
        grupo="ordenes", nombre="sentate", sonido={"archivo": "madera_golpe", "vol": 0.8})
    pon(tira("CALLATE", 96, seed=2), 1580, 380, 2.71, rot=4, entrada="golpe", dura=0.1, grupo="ordenes",
        nombre="callate", sonido={"archivo": "sello_thump", "vol": 0.85})
    pon(tira("AGARRATE", 130, fondo=TINTA, seed=3), 1300, 960, 3.47, rot=-5, entrada="golpe", dura=0.1,
        grupo="ordenes", nombre="agarrate", sonido={"archivo": "libro_cae", "vol": 0.9})
    # "porque esto es LOS ONCE"
    carton = Image.new("RGB", (1000, 460), (238, 232, 216))
    pon(recorte_cuadro(carton, seed=21), 960, 520, 5.5, rot=-2, grupo="canal", nombre="carton_canal",
        sonido={"archivo": "papel3", "vol": 0.7})
    pon(sello("LOS 11", 250, rot=-4), 960, 520, 5.98, entrada="golpe", dura=0.12, grupo="sellos",
        nombre="sello_los11", sonido={"archivo": "sello_thump", "vol": 1.0})
    # "cómo Argentina ganó su segundo Mundial"
    band = foto(M / "intro/banderas/argentina.png", 760)
    pon(recorte_cuadro(band, seed=22), 760, 420, 8.0, rot=6, grupo="argentina", nombre="bandera_argentina",
        sonido={"archivo": "carta", "vol": 0.7})
    pon(afiche(M / "intro/afiches/1978.png", 330), 1560, 360, 9.1, rot=-8, grupo="argentina", nombre="afiche_1978",
        sonido={"archivo": "papel1", "vol": 0.6})
    pon(tira("2º MUNDIAL", 80, seed=4), 1180, 640, 9.76, rot=-3, entrada="golpe", dura=0.1, grupo="argentina",
        nombre="tira_2mundial", sonido={"archivo": "sello_thump", "vol": 0.8})
    # "la historia de un equipo que nadie quería"
    pon(marco_polaroid(foto(M / "entrenamiento.jpg", 820)), 820, 560, 11.2, rot=-4, grupo="equipo",
        nombre="equipo", sonido={"archivo": "papel2", "vol": 0.7})
    pon(tira("NADIE LOS QUERÍA", 64, seed=5), 900, 860, 12.36, rot=3, entrada="golpe", dura=0.1, grupo="equipo",
        nombre="tira_nadie", sonido={"archivo": "sello_thump", "vol": 0.8})
    # "de un pibe de Fiorito"
    pon(marco_polaroid(foto(M / "tota_diego_joven.jpg", 420, caja=(60, 0, 640, 750))), 1500, 600, 13.8, rot=7,
        grupo="diego", nombre="pibe_fiorito", sonido={"archivo": "papel1", "vol": 0.7})
    # "que le tocó la mano a Dios": Diego salta (gol a Inglaterra) y Dios baja desde la izquierda hasta tocarle el puño
    dg = Image.open(R / "diego_mano.png").convert("RGBA")
    dg = dg.crop(dg.getbbox())                                    # bbox (614, 205, ...): puño en (696, 589) del original
    ed = 960 / dg.height
    dg = dg.resize((int(dg.width * ed), 960), Image.LANCZOS)
    puno = ((696 - 614) * ed, (589 - 205) * ed)
    dx, dy = 1330, 590                                            # centro de Diego en pantalla
    px, py = dx - dg.width / 2 + puno[0], dy - dg.height / 2 + puno[1]
    pon(figurita(dg, seed=23), dx, dy, 14.6, entrada="desliza", desde_dir=(0.15, 0.7), dura=0.3, grupo="dios",
        nombre="diego_salta", sonido={"archivo": "whoosh_rapido", "vol": 0.7})
    di = Image.open(R / "dios.png").convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)   # el dedo queda a la derecha
    ei = 0.56
    di = di.resize((int(di.width * ei), int(di.height * ei)), Image.LANCZOS)
    dedo = ((2184 - 16) * ei, 675 * ei)
    gx, gy = px - dedo[0] + di.width / 2 - 6, py - dedo[1] + di.height / 2 + 4   # la yema justo sobre el puño
    pon(figurita(di, seed=24), gx, gy, 14.95, entrada="desliza", desde_dir=(-1, -0.25), dura=0.6, grupo="dios",
        nombre="dios", sonido={"archivo": "whoosh_grave", "vol": 0.8})
    # (17/11, Vibe Editor: "no más tiza": sin la ronda del toque)
    # "y de un mes en el que el cielo fue celeste y blanco": la bandera de papel tapa todo
    CEL, BLA = (116, 172, 223), (246, 244, 238)
    pon(banda(CEL, 2400, 600, seed=0), 960, 150, 17.5, rot=-1.5, entrada="desliza", desde_dir=(-1, 0), dura=0.3,
        grupo="cielo", nombre="banda_celeste_1", sonido={"archivo": "whoosh_rapido", "vol": 0.6})
    pon(banda(CEL, 2400, 640, seed=1), 960, 900, 18.1, rot=1.2, entrada="desliza", desde_dir=(1, 0), dura=0.3,
        grupo="cielo", nombre="banda_celeste_2", sonido={"archivo": "whoosh_rapido", "vol": 0.6})
    pon(banda(BLA, 2400, 640, seed=2), 960, 540, 18.98, rot=-0.6, entrada="desliza", desde_dir=(-1, 0), dura=0.28,
        grupo="cielo", nombre="banda_blanca", sonido={"archivo": "papel3", "vol": 0.8})
    fl = Image.open(M / "intro/banderas/argentina.png").convert("RGBA")
    w0, h0 = fl.size
    sol = fl.crop((int(w0 * 0.41), int(h0 * 0.35), int(w0 * 0.59), int(h0 * 0.65)))
    sol = sol.resize((300, int(300 * sol.height / sol.width)), Image.LANCZOS)
    pon(recorte_cuadro(sol.convert("RGB"), seed=25), 960, 540, 19.45, rot=-4, entrada="golpe", dura=0.12,
        grupo="cielo", nombre="sol", sonido={"archivo": "sello_thump", "vol": 0.7})
    pila(salida, E, 20.9, base=base, capas=capas, solo=solo,
         sacudones=[(0.76, 0.8), (1.69, 0.9), (2.71, 1.0), (3.47, 2.6), (3.8, 2.0), (4.1, 1.4), (5.98, 1.6),
                    (9.76, 0.8), (12.36, 0.8), (15.55, 2.2), (18.98, 1.0), (19.45, 0.8)])
    if solo:
        return
    cues = sonidos_de(E)
    salida = Path(salida)
    json.dump(cues, open(salida.with_suffix(".sonidos.json"), "w"), indent=1)
    voz = RAIZ / ".cache/elevenlabs/voz_a48ef327b7e666e2.mp3"
    mezclar(salida, cues, salida.with_name(salida.stem + "_con_sonido.mp4"), [(voz, 0.3)])
    if capas:
        ij = salida.with_name(salida.stem + "_capas") / "capas.json"
        d = json.load(open(ij))
        d["voces"] = [{"archivo": str(voz), "inicio": 0.3}]
        json.dump(d, open(ij, "w"), indent=1)


def capitulo_1986(numero, titulo, salida, capas=False, solo=None, antes="intro_cierre_f.mp4", dur=3.6):
    """Placa de capítulo en carpeta (17/11, segunda parte: "como venimos pero más documental"): una hoja limpia entra y
    tapa el collage anterior (el "después limpiamos"), cae el sello CAPÍTULO N, la tira con el título y un subrayado de
    tiza. Arranca sobre el último cuadro de la pieza anterior; después corta al tramo documental."""
    G = RAIZ / "proyectos/argentina-1986/salida/graficos"
    base = ultimo_cuadro(G / antes)
    E = []
    hojaim = textura("papel", W + 120, H + 120).convert("RGBA")
    E.append(dict(img=hojaim, x=W / 2, y=H / 2, t=0.1, rot=-1.2, entrada="desliza", desde_dir=(0, -1), dura=0.5,
                  nombre="hoja_limpia", sonido={"archivo": "whoosh_grave", "vol": 0.5}))
    E.append(dict(img=sello(f"CAPÍTULO {numero}", tam=150, rot=-4, seed=11), x=W / 2 - 40, y=H / 2 - 120, t=0.95,
                  entrada="golpe", dura=0.08, nombre="sello_capitulo", sonido={"archivo": "sello_thump", "vol": 0.8}))
    E.append(dict(img=tira(titulo.upper(), tam=120, fondo=(24, 24, 24), seed=2), x=W / 2 + 20, y=H / 2 + 90, t=1.55,
                  rot=1.5, entrada="golpe", dura=0.1, nombre="tira_titulo", sonido={"archivo": "carta", "vol": 0.6}))
    # (18/11, pedido del usuario: "sacá todas las tizas": sin el subrayado de tiza)
    _cerrar_pieza(salida, E, dur, base, [], capas, solo, ())


if __name__ == "__main__":
    if sys.argv[1] == "capitulo":      # carpeta.py capitulo 1 "Nadie creía" <salida.mp4> [--capas]
        a = sys.argv
        solo = set(a[a.index("--solo") + 1].split(",")) if "--solo" in a else None
        capitulo_1986(a[2], a[3], a[4], capas="--capas" in a or bool(solo), solo=solo,
                      antes=a[a.index("--antes") + 1] if "--antes" in a else "intro_cierre_f.mp4")
        raise SystemExit
    if sys.argv[1] == "medio":         # carpeta.py medio a|b|c <salida.mp4> [--capas] [--solo x,y]
        a = sys.argv
        solo = set(a[a.index("--solo") + 1].split(",")) if "--solo" in a else None
        medio_1986(a[2], a[3], capas="--capas" in a or bool(solo), solo=solo)
    elif sys.argv[1] == "cierre":
        a = sys.argv
        solo = set(a[a.index("--solo") + 1].split(",")) if "--solo" in a else None
        cierre_1986(a[2], capas="--capas" in a or bool(solo), solo=solo)
    elif sys.argv[1] == "1986":
        a = sys.argv
        solo = set(a[a.index("--solo") + 1].split(",")) if "--solo" in a else None
        intro_1986(a[2], capas="--capas" in a or bool(solo), solo=solo)
    elif sys.argv[1] == "peluca":
        a = sys.argv[2:]
        texto = a[a.index("--texto") + 1] if "--texto" in a else None
        peluca(a[0], a[1] if len(a) > 1 and not a[1].startswith("--") else None, texto, capas="--capas" in a)
