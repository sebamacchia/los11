"""Miniaturas de YouTube (1280x720) para Estambul 2005.
Uso: /usr/bin/python3 proyectos/estambul-2005/miniaturas.py  -> salida/miniaturas/miniatura_1..4.png"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "herramientas"))
import graficos as G  # noqa: E402

P = Path(__file__).resolve().parent
A = RAIZ / "animaciones" / "futbol" / "assets"
FONDOS = Path(sys.argv[1]) if len(sys.argv) > 1 else P / "material" / "miniaturas"
OUT = P / "salida" / "miniaturas"
W, H = 1280, 720
ROJO = (200, 16, 46)
VERDE = G.ACENTO
BLANCO = (255, 255, 255)


def fondo(ruta, blur=10, brillo=0.55, tinte=None):
    im = Image.open(ruta).convert("RGB").resize((W, H), Image.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(blur))
    im = ImageEnhance.Brightness(im).enhance(brillo)
    if tinte:
        im = Image.blend(im, Image.new("RGB", (W, H), tinte), 0.25)
    return im.convert("RGBA")


def degradado(im, lado="izq", fuerza=230, ancho=0.65):
    g = Image.new("L", (W, 1))
    for x in range(W):
        k = x / W if lado == "der" else 1 - x / W
        g.putpixel((x, 0), int(fuerza * max(0.0, min(1.0, (k - (1 - ancho)) / ancho)) ** 1.2))
    g = g.resize((W, H))
    capa = Image.new("RGBA", (W, H), G.OSCURO + (0,))
    capa.putalpha(g)
    im.alpha_composite(capa)


def jugador(im, ruta, alto, x_centro, y_base=H, borde=VERDE, espejo=False):
    """Pega un recorte RGBA (1920x1080) recortado a su caja, con contorno del color del canal."""
    c = Image.open(ruta).convert("RGBA")
    c = c.crop(c.getchannel("A").getbbox())
    if espejo:
        c = c.transpose(Image.FLIP_LEFT_RIGHT)
    k = alto / c.height
    c = c.resize((int(c.width * k), int(c.height * k)), Image.LANCZOS)
    a = c.getchannel("A")
    contorno = a.filter(ImageFilter.MaxFilter(15))
    sombra = Image.new("RGBA", c.size, borde + (0,))
    sombra.putalpha(contorno)
    x, y = int(x_centro - c.width / 2), int(y_base - c.height)
    im.alpha_composite(sombra, (x, y))
    im.alpha_composite(c, (x, y))


def texto(d, xy, txt, tam, color=BLANCO, peso=800, borde=6, anchor="la"):
    f = G.fuente(peso, tam)
    d.text(xy, txt, font=f, fill=color, stroke_width=borde, stroke_fill=(0, 0, 0), anchor=anchor)
    return d.textbbox(xy, txt, font=f, stroke_width=borde, anchor=anchor)


def chip(d, xy, txt, tam, fondo_c=VERDE, color=G.OSCURO):
    f = G.fuente(800, tam)
    x, y = xy
    w = d.textlength(txt, font=f)
    d.rectangle([x, y, x + w + tam * 0.9, y + tam * 1.45], fill=fondo_c)
    d.text((x + tam * 0.45, y + tam * 0.18), txt, font=f, fill=color)
    return x + w + tam * 0.9


def marca(d):
    d.rectangle([34, 30, 44, 76], fill=VERDE)
    d.text((56, 28), "LOS 11", font=G.fuente(800, 40), fill=BLANCO, stroke_width=3, stroke_fill=(0, 0, 0))


def guardar(im, n):
    OUT.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(OUT / f"miniatura_{n}.png")
    im.convert("RGB").save(OUT / f"miniatura_{n}.jpg", quality=92)


# 1 — el 0-3 del entretiempo + Gerrard pidiendo que crean
im = fondo(FONDOS / "hinchas.png", tinte=ROJO)
degradado(im, "izq")
jugador(im, A / "cg_gerrard31_cut.png", 700, 960)
d = ImageDraw.Draw(im)
marca(d)
chip(d, (60, 150), "ENTRETIEMPO", 34)
texto(d, (52, 205), "0-3", 260, borde=10)
texto(d, (60, 470), "...Y GANARON", 66, color=VERDE)
guardar(im, 1)

# 2 — Gerrard con la copa
im = fondo(FONDOS / "copa.png", blur=8, brillo=0.6)
degradado(im, "izq", ancho=0.7)
jugador(im, A / "gerrard_cut.png", 720, 900)
d = ImageDraw.Draw(im)
marca(d)
texto(d, (56, 170), "PERDÍAN", 108)
texto(d, (52, 290), "3-0", 220, color=VERDE, borde=10)
chip(d, (60, 540), "FINAL CHAMPIONS 2005", 34, fondo_c=BLANCO)
guardar(im, 2)

# 3 — Dudek y el baile
im = fondo(FONDOS / "cancha.png", blur=6, brillo=0.5)
degradado(im, "izq", ancho=0.6)
jugador(im, FONDOS / "dudek_cut.png", 690, 920)
d = ImageDraw.Draw(im)
marca(d)
texto(d, (56, 190), "EL BAILE", 150)
texto(d, (60, 360), "QUE GANÓ", 92, color=VERDE)
texto(d, (60, 460), "UNA FINAL", 92, color=VERDE)
guardar(im, 3)

# 4 — 6 minutos: 3-0 -> 3-3, Smicer gritando
im = fondo(FONDOS / "festejo.png", tinte=ROJO)
degradado(im, "izq")
jugador(im, A / "cg_smicer32_cut.png", 700, 980)
d = ImageDraw.Draw(im)
marca(d)
texto(d, (52, 150), "6", 330, color=VERDE, borde=10)
texto(d, (290, 230), "MINUTOS", 104)
x = chip(d, (60, 500), "3-0", 64, fondo_c=(60, 60, 60), color=BLANCO)
texto(d, (x + 24, 500), "→", 76)
chip(d, (x + 120, 500), "3-3", 64)
guardar(im, 4)
print("listo:", OUT)
