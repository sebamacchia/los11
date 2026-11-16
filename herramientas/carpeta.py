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


def pila(salida, elementos, dur, base=None, sacudones=(), capas=False, vhs_hasta=0.0, solo=None):
    """capas=True: además deja <salida>_capas/ con UNA capa por elemento (NN_nombre.mov con transparencia, empieza
    cuando entra el elemento), 00_fondo.png, 99_vhs.mov y capas.json (para armar el .fcproj). solo={nombres}: rehace
    nada más esas capas (no toca el video armado ni las demás)."""
    salida = Path(salida)
    base = base or base_carton()
    # videos: decodificar una vez
    for e in elementos:
        if e.get("video"):
            ruta, desde, vel, rec, ancho = e["video"]
            e["_cuadros"] = cuadros_video(ruta, desde, vel, rec, ancho, dur - e["t"] + 0.5)
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
            if t < e["t"]:
                continue
            u = (t - e["t"]) / e.get("dura", 0.2)
            x, y, esc, rot = e["x"], e["y"], e.get("esc", 1.0), e.get("rot", 0.0)
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
            if e.get("_cuadros"):
                j = min(len(e["_cuadros"]) - 1, int((tk - e["t"]) * FPS))
                img = recorte_cuadro(e["_cuadros"][j], seed=i)
            else:
                img = e["img"]
            if ent == "trazo" and u < 1:                       # tiza que se dibuja de izquierda a derecha
                img = img.copy()
                a = img.split()[3]
                corte = int(img.width * suave(u))
                a.paste(0, (corte, 0, img.width, img.height))
                img.putalpha(a)
            vivo = 0.0 if e.get("_cuadros") is None and u >= 1 else 1.0
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
                vc[i] = Capa(dcap / f"{nombres[i]}.mov", movida=bool(elementos[i].get("_cuadros")) or elementos[i].get("entrada") == "trazo")
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
    """Preview con sonido: efectos (y la voz del narrador, si se pasa) sobre el video mudo."""
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
    fil.append("".join(f"[a{i}]" for i in range(1, n + 1)) + f"amix=inputs={n}:normalize=0:duration=longest,alimiter=limit=0.7:level=0[mix]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fil), "-map", "0:v", "-map", "[mix]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(salida)], check=True)


def voz_escena(guion_tmp, n):
    """Voz (mp3 del caché) e inicio de la escena n de un render previo (tmp_guion_x/linea.json)."""
    l = json.load(open(guion_tmp / "linea.json"))
    v = l["voces"][n]
    ruta = Path(v["archivo"])
    if not ruta.exists():
        ruta = RAIZ / ".cache" / "elevenlabs" / ruta.name
    ini = [p for p in l["piezas"] if p["escena"] == n + 1][0]["inicio"]
    return ruta, v["inicio"] - ini


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
    # "completamente loco": tiza que rodea a Mr. T y flecha
    circ = [p for p in tiza if 0.8 < p.width / p.height < 1.25]
    if circ:
        pon(circ[0].resize((520, int(circ[0].height * 520 / circ[0].width))), 520, 560, 6.1, rot=0,
            entrada="trazo", dura=0.45, grupo="tiza")
    # 7.51 "y el fútbol no se quedaba atrás": cosas locas del fútbol del 86 (16/11, en vez del clip de Bélgica)
    ola = Image.open(M / "intro/ola_azteca.jpg").convert("RGB")
    ola = ola.resize((1100, int(ola.height * 1100 / ola.width)), Image.LANCZOS)
    pon(recorte_cuadro(ola, seed=5), 980, 470, 7.55, rot=-3, grupo="futbol")                    # la ola en el Azteca
    pon(fig(recorte_png(R / "valderrama_cali.png"), 640), 500, 600, 7.95, rot=4, grupo="futbol")   # el Pibe, Cali 86
    pon(fig(recorte_png(R / "pique_azteca.png"), 520), 1480, 560, 8.4, rot=-6, grupo="futbol")    # Pique, la mascota
    pon(figurita(tarjeta_roja(250)), 1290, 880, 8.85, rot=14, entrada="golpe", dura=0.12, grupo="futbol")  # Batista
    pon(sello("56 SEG", 130), 1580, 900, 9.15, rot=-8, entrada="golpe", dura=0.1, grupo="sellos")
    E.insert(0, dict(img=None, x=0, y=0, t=0.0, grupo="vhs", sonido={"archivo": "vhs_entra", "dur": 2.3, "vol": 0.8}))
    E.insert(1, dict(img=None, x=0, y=0, t=0.4, grupo="vhs", sonido={"archivo": "estatica", "desde": 3, "dur": 1.9,
                                                                    "vol": 0.25}))
    for e in E:
        if e.get("entrada") == "desliza" and e["x"] == 900:      # DeLorean
            e["sonido"] = {"archivo": "auto_pasa", "pico": True, "dur": 1.6, "vol": 0.8}
        elif e.get("entrada") == "desliza":                       # F-14
            e["sonido"] = {"archivo": "avion_pasa", "pico": True, "dur": 2.0, "vol": 0.8}
    salida = Path(salida)
    vis = [e for e in E if e.get("img") is not None or e.get("video")]
    for e, n in zip(vis, ["sello_1986", "cubo", "cassette", "joystick", "entrada", "vhs", "mr_t", "carta_ajuste",
                          "madonna", "delorean", "f14", "walkman", "diario", "zapatillas", "sticker", "tiza_circulo",
                          "la_ola", "valderrama", "pique", "tarjeta_roja", "sello_56seg"]):
        e["nombre"] = n
    pila(salida, vis, 10.27, sacudones=[(2.45, 2.0), (6.1, 1.2), (7.55, 1.6)], capas=capas, vhs_hasta=2.3, solo=solo)
    if solo:
        return
    cues = sonidos_de(E)
    json.dump(cues, open(salida.with_suffix(".sonidos.json"), "w"), indent=1)
    voz, voz_en = voz_escena(RAIZ / "proyectos/argentina-1986/tmp_guion_intro", 0)
    mezclar(salida, cues, salida.with_name(salida.stem + "_con_sonido.mp4"), voz, voz_en)
    if capas:                                              # la voz va en el .fcproj (filmcraft.py capas)
        ij = salida.with_name(salida.stem + "_capas") / "capas.json"
        d = json.load(open(ij))
        d["voz"] = {"archivo": str(voz), "inicio": round(voz_en, 3)}
        json.dump(d, open(ij, "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "1986":
        a = sys.argv
        solo = set(a[a.index("--solo") + 1].split(",")) if "--solo" in a else None
        intro_1986(a[2], capas="--capas" in a or bool(solo), solo=solo)
    elif sys.argv[1] == "peluca":
        a = sys.argv[2:]
        texto = a[a.index("--texto") + 1] if "--texto" in a else None
        peluca(a[0], a[1] if len(a) > 1 and not a[1].startswith("--") else None, texto, capas="--capas" in a)
