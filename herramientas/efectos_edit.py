"""Efectos de edit sobre un clip (jugador recortado con rembg). Estilos del catálogo:

  CONTORNO  — el jugador en blanco y negro con la camiseta en color, como sticker: anillo de puntos de imprenta
              y contornos de colores (celeste, blanco, sol, azul) que crecen de a uno, con destellos.
  AURA      — fondo en gris, los jugadores en color con un borde de luz amarilla; flash de siluetas blancas al
              entrar y, al final, todo invertido: fondo celeste neón y los jugadores en gris.
  ESTALLIDO — una estrella de puntas amarilla con textura detrás del jugador, que cambia de forma cada 3 cuadros;
              el fondo en gris.

Correr con el venv (rembg + numpy + scipy):
  herramientas/.venv/bin/python herramientas/efectos_edit.py <estilo> <video> <desde> <dur> <salida.mp4>
      [--vel 0.6] [--recorte x,y,w,h] [--jugadores 1]

El recorte saca logos de la TV (el cuadro va a la altura completa, y a los costados el mismo fondo desenfocado).
"""
import math
import random
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps
from rembg import new_session, remove
from scipy import ndimage

W, H, FPS = 1920, 1080, 30
CELESTE, SOL, AZUL_OSC, BLANCO = (117, 170, 219), (246, 190, 30), (24, 44, 96), (244, 242, 236)


def args():
    a = sys.argv[1:]
    op = {"vel": 0.6, "recorte": "0,0,790,720", "jugadores": 1}
    pos, i = [], 0
    while i < len(a):
        if a[i].startswith("--"):
            op[a[i][2:]] = a[i + 1]
            i += 2
        else:
            pos.append(a[i])
            i += 1
    return pos, op


def mascara(im, sesion, n):
    m = np.asarray(remove(im, session=sesion, only_mask=True)).astype(np.float32) / 255
    lab, k = ndimage.label(m > 0.5)
    if k:
        tam = ndimage.sum(m > 0.5, lab, range(1, k + 1))
        orden = np.argsort(tam)[::-1]
        quedan = [o + 1 for o in orden[:n] if tam[o] > 0.2 * tam[orden[0]]]
        m = m * ndimage.binary_dilation(np.isin(lab, quedan), iterations=2)
    a = np.asarray(im).astype(np.float32) / 255
    pasto = (a[..., 1] > a[..., 0] + 0.07) & (a[..., 1] > a[..., 2] + 0.03)
    return m * (1 - ndimage.binary_dilation(pasto, iterations=1))


def camiseta(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    return (b > r + 0.1) & ((mx - mn) / (mx + 1e-6) > 0.25) & (mx > 0.2)


class Lienzo:
    """Ubica el cuadro recortado a altura completa, centrado; a los costados el mismo cuadro ampliado y desenfocado."""

    def __init__(self, sw, sh):
        self.esc = H / sh
        self.w = int(sw * self.esc)
        self.ox = (W - self.w) // 2
        x = np.linspace(-1, 1, self.w)
        borde = np.clip((1 - np.abs(x)) / 0.12, 0, 1)  # el centro nítido se funde con los costados
        self.fundido = Image.fromarray((np.tile(borde, (H, 1)) * 255).astype(np.uint8))

    def fondo(self, im, blur=10):
        cover = ImageOps.fit(im, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(blur))
        centro = im.resize((self.w, H), Image.LANCZOS)
        cover.paste(centro, (self.ox, 0), self.fundido)
        return cover

    def capa(self, im):
        return im.resize((self.w, H), Image.LANCZOS)

    def pegar(self, lienzo, capa, alfa):
        lienzo.paste(capa, (self.ox, 0), alfa)


def gris(im, contraste=1.2, luz=0.85):
    g = ImageEnhance.Contrast(ImageOps.grayscale(im)).enhance(contraste).point(lambda v: int(min(255, v * luz)))
    return Image.merge("RGB", [g] * 3)


def puntos(w, h, paso=10, r=2.6):
    """Trama de imprenta: puntos negros sobre blanco."""
    im = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(im)
    for y in range(0, h + paso, paso):
        for x in range((y // paso % 2) * paso // 2, w + paso, paso):
            d.ellipse([x - r, y - r, x + r, y + r], fill=20)
    return Image.merge("RGB", [im] * 3)


def ruido(w, h, sigma, semilla):
    rng = np.random.default_rng(semilla)
    n = ndimage.gaussian_filter(rng.standard_normal((h // 4, w // 4)), sigma / 4)
    n = (n - n.mean()) / (n.std() + 1e-6)
    return np.asarray(Image.fromarray(n.astype(np.float32)).resize((w, h), Image.BILINEAR))


def destello(d, x, y, s, col=(255, 255, 255)):
    pts = []
    for k in range(8):
        ang = k * math.pi / 4 - math.pi / 2
        rr = s if k % 2 == 0 else s * 0.16
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    d.polygon(pts, fill=col)


def textura(w, h, semilla):
    """Grano de papel/aerosol para rellenos planos (0.6..1)."""
    rng = np.random.default_rng(semilla)
    n = ndimage.gaussian_filter(rng.random((h // 3, w // 3)), 1.2)
    n = (n - n.min()) / (n.max() - n.min() + 1e-6)
    return Image.fromarray((150 + n * 105).astype(np.uint8)).resize((w, h), Image.BILINEAR)


# ── estilos ───────────────────────────────────────────────────────────────────────────────────────────────────
def contorno(k, n, im, m, L, cache):
    if "ruido" not in cache:
        cache["ruido"] = ruido(L.w, H, 40, 7) * 7
        cache["trama"] = puntos(L.w, H)
        cache["tex"] = textura(L.w, H, 3)
    lienzo = gris(L.fondo(im, 8), 1.1, 0.62)
    a = np.asarray(im).astype(np.float32) / 255
    mm = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((L.w, H), Image.BILINEAR)) / 255
    dist = ndimage.distance_transform_edt(mm < 0.5) + cache["ruido"] * (ndimage.distance_transform_edt(mm < 0.5) > 14)
    # bandas: (desde cuadro, ancho final, color o "trama"/"tex")
    t = k / FPS
    bandas = [(0.25, 16, "trama"), (0.55, 12, (52, 52, 50)), (0.8, 18, CELESTE), (1.05, 12, BLANCO),
              (1.25, 20, SOL), (1.5, 30, "azul")]
    capa = Image.new("RGB", (L.w, H))
    alfa = np.zeros((H, L.w), np.float32)
    r_ext = 0.0
    lim = []
    for t0, ancho, col in bandas:
        crece = min(1.0, max(0.0, (t - t0) / 0.3))
        if crece <= 0:
            break
        crece = 1 - (1 - crece) ** 3
        r_ext += ancho * crece
        lim.append((r_ext, col))
    for r, col in reversed(lim):  # de afuera hacia adentro
        zona = Image.fromarray(((dist <= r) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))
        if col == "trama":
            capa.paste(cache["trama"], (0, 0), zona)
        elif col == "azul":
            relleno = Image.merge("RGB", [cache["tex"].point(lambda v, c=c: int(c * v / 255)) for c in (40, 80, 160)])
            capa.paste(relleno, (0, 0), zona)
        else:
            capa.paste(col, (0, 0, L.w, H), zona)
        alfa = np.maximum(alfa, np.asarray(zona) / 255)
    L.pegar(lienzo, capa, Image.fromarray((alfa * 255).astype(np.uint8)))
    # el jugador: blanco y negro, la camiseta en color
    col = L.capa(im)
    cam = Image.fromarray((ndimage.binary_dilation(camiseta(a), iterations=1) * 255).astype(np.uint8))
    cam = cam.resize((L.w, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.5))
    r_, g_, b_ = col.split()
    vivo = ImageEnhance.Color(Image.merge("RGB", (r_, g_.point(lambda v: int(v * 0.92)), b_))).enhance(1.35)
    jug = gris(col, 1.25, 1.0)
    jug.paste(vivo, (0, 0), cam)
    L.pegar(lienzo, jug, Image.fromarray((mm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
    # destellos
    d = ImageDraw.Draw(lienzo)
    ys, xs = np.nonzero(mm > 0.5)
    if len(xs):
        x0, x1, y0, y1 = xs.min() + L.ox, xs.max() + L.ox, ys.min(), ys.max()
        for f0, fx, fy, s in [(6, -0.25, 0.3, 30), (16, 1.2, 0.15, 22), (30, 0.9, 0.05, 42), (44, -0.1, 0.75, 26),
                              (58, 1.15, 0.6, 34), (72, 0.2, 0.0, 28), (86, -0.3, 0.5, 36)]:
            e = k - f0
            if 0 <= e < 10:
                destello(d, x0 + (x1 - x0) * fx, y0 + (y1 - y0) * fy, s * math.sin(math.pi * e / 10))
    return lienzo


def aura(k, n, im, m, L, cache):
    mm = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((L.w, H), Image.BILINEAR)) / 255
    a_m = Image.fromarray((mm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    f_inv = int(n * 0.72)
    if k >= f_inv:  # final invertido: fondo celeste neón, jugadores en gris claro
        if k == f_inv:
            return Image.new("RGB", (W, H), (255, 255, 255))
        g = ImageOps.posterize(ImageOps.grayscale(L.fondo(im, 6)), 3)
        g = ImageEnhance.Contrast(g).enhance(1.4)
        lienzo = ImageOps.colorize(g, (0, 60, 130), (150, 240, 255))
        jug = gris(L.capa(im), 1.3, 1.08)
        L.pegar(lienzo, jug, a_m)
        return lienzo
    lienzo = gris(L.fondo(im, 6), 1.15, 0.8)
    # aura amarilla: halo difuso + borde firme
    afuera = ndimage.distance_transform_edt(mm < 0.5)
    halo = Image.fromarray((np.clip(1 - afuera / 46, 0, 1) ** 1.3 * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(14))
    borde = Image.fromarray(((afuera > 0) & (afuera < 10)).astype(np.uint8) * 255).filter(ImageFilter.GaussianBlur(1.6))
    capa = Image.new("RGB", (L.w, H), (250, 214, 40))
    L.pegar(lienzo, capa, halo)
    L.pegar(lienzo, capa, borde)
    if k in (2, 3):  # flash: siluetas blancas
        L.pegar(lienzo, Image.new("RGB", (L.w, H), (250, 250, 248)), a_m)
        return lienzo
    col = L.capa(im)
    r_, g_, b_ = col.split()
    vivo = ImageEnhance.Color(Image.merge("RGB", (r_.point(lambda v: min(255, int(v * 1.05))),
                                                  g_.point(lambda v: int(v * 0.92)), b_))).enhance(1.3)
    L.pegar(lienzo, vivo, a_m)
    return lienzo


def estrella(cx, cy, semilla, escala=1.0):
    rnd = random.Random(semilla)
    puntas = rnd.randint(10, 13)
    base = rnd.uniform(0, 2 * math.pi)
    pts = []
    for i in range(puntas):
        ang = base + 2 * math.pi * i / puntas + rnd.uniform(-0.12, 0.12)
        ro = rnd.uniform(430, 900) * escala
        ri = rnd.uniform(140, 230) * escala
        pts.append((cx + ro * math.cos(ang), cy + ro * math.sin(ang)))
        ang2 = ang + math.pi / puntas + rnd.uniform(-0.08, 0.08)
        pts.append((cx + ri * math.cos(ang2), cy + ri * math.sin(ang2)))
    return pts


def estallido(k, n, im, m, L, cache):
    if "tex" not in cache:
        cache["tex"] = textura(W, H, 11)
    fondo = L.fondo(im, 7)
    lienzo = gris(fondo, 1.15, 0.85)
    mm = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((L.w, H), Image.BILINEAR)) / 255
    ys, xs = np.nonzero(mm > 0.5)
    if len(xs):
        top = ys.min()
        alto = ys.max() - top
        sel = ys < top + alto * 0.35
        cx, cy = xs[sel].mean() + L.ox, top + alto * 0.28
        cache["centro"] = (cx, cy) if "centro" not in cache else (
            cache["centro"][0] * 0.7 + cx * 0.3, cache["centro"][1] * 0.7 + cy * 0.3)
    cx, cy = cache.get("centro", (W / 2, H / 2))
    crece = min(1.0, (k + 1) / 5)
    forma = Image.new("L", (W, H), 0)
    ImageDraw.Draw(forma).polygon(estrella(cx, cy, k // 3, 0.35 + 0.65 * crece), fill=255)
    # textura: la luz del fondo + grano, como un aerosol sobre papel
    luz = ImageOps.grayscale(fondo).point(lambda v: int(150 + v * 0.42))
    tex = ImageChops.multiply(luz, cache["tex"])
    tex = ImageOps.autocontrast(tex, cutoff=1).point(lambda v: int(120 + v * 0.53))
    amarillo = Image.merge("RGB", [tex.point(lambda v, c=c: int(c * v / 255)) for c in (240, 236, 60)])
    # bordes de aerosol: puntos sueltos alrededor
    rng = np.random.default_rng(k // 3)
    spray = forma.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3))
    granos = Image.fromarray((rng.random((H, W)) > 0.93).astype(np.uint8) * 255)
    forma = ImageChops.lighter(forma, ImageChops.multiply(spray, granos))
    lienzo.paste(amarillo, (0, 0), forma.point(lambda v: int(v * 0.93)))
    col = L.capa(im)
    r_, g_, b_ = col.split()
    vivo = ImageEnhance.Color(Image.merge("RGB", (r_.point(lambda v: min(255, int(v * 1.05))),
                                                  g_.point(lambda v: int(v * 0.92)), b_))).enhance(1.25)
    L.pegar(lienzo, vivo, Image.fromarray((mm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
    return lienzo


ESTILOS = {"contorno": contorno, "aura": aura, "estallido": estallido}


def main():
    (estilo, video, desde, dur, salida), op = args()
    vel = float(op["vel"])
    tmp = Path(tempfile.mkdtemp())
    x, y, w, h = op["recorte"].split(",")
    filtro = f"crop={w}:{h}:{x}:{y},setpts=PTS/{vel},fps={FPS}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(desde), "-t", str(dur), "-i", video, "-vf", filtro,
                    str(tmp / "c_%04d.png")], check=True)
    cuadros = sorted(tmp.glob("c_*.png"))
    sesion = new_session("u2net_human_seg")
    ims, masks, previo = [], [], None
    for k, f in enumerate(cuadros):
        im = Image.open(f).convert("RGB")
        if previo is not None and np.abs(np.asarray(im, np.int16) - previo[0]).mean() < 0.5:
            m = previo[1]  # cuadro repetido por la cámara lenta
        else:
            m = mascara(im, sesion, int(op["jugadores"]))
        previo = (np.asarray(im, np.int16), m)
        ims.append(im)
        masks.append(m)
        if k % 20 == 0:
            print(f"  recorte {k}/{len(cuadros)}", flush=True)
    L = Lienzo(*ims[0].size)
    fn = ESTILOS[estilo]
    cache = {}
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                             "-pix_fmt", "yuv420p", salida], stdin=subprocess.PIPE)
    for k in range(len(ims)):
        proc.stdin.write(fn(k, len(ims), ims[k], masks[k], L, cache).convert("RGB").tobytes())
    proc.stdin.close()
    proc.wait()
    print("listo:", salida)


if __name__ == "__main__":
    main()
