"""Piezas animadas de intros "pop" (pedido 15/11 para la intro de Argentina 86): montajes rápidos que van como clips
en el guion ({"archivo": "salida/graficos/x.mp4", ...}).

  iconos    fotos de época a cortes rápidos (al ritmo de una batería), con rótulo y look VHS
  afiches   línea de tiempo de afiches a toda velocidad que frena en seco en el último (con golpe y flash)
  satelital zoom desde el espacio hasta un estadio (Tierra -> ciudad -> estadio, fundidos)
  banderas  mosaico de banderas que explota y se achica hasta dejar una sola en el centro, brillando
  peluca    dibujito: un señor al que una ráfaga le vuela la peluca

  /usr/bin/python3 herramientas/intro_pop.py <pieza> <carpeta_material> <salida.mp4>   (ver main para los parámetros)
"""
import math
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).parent))
import documental as doc  # noqa: E402

W, H, FPS = 1920, 1080, 30
ROJO, CREMA, TINTA = doc.ROJO, doc.CREMA, doc.TINTA


class Video:
    def __init__(self, salida):
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                                   f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17",
                                   "-pix_fmt", "yuv420p", str(salida)], stdin=subprocess.PIPE)

    def __call__(self, im):
        self.p.stdin.write(im.convert("RGB").tobytes())

    def cerrar(self):
        self.p.stdin.close()
        self.p.wait()


def cubrir(im, w=W, h=H, foco=(0.5, 0.5)):
    return ImageOps.fit(im.convert("RGB"), (w, h), Image.LANCZOS, centering=foco)


def vhs(im, k, rnd, fuerte=1.0):
    """VHS liviano en Pillow: color corrido, líneas, ruido y alguna barra rota."""
    r, g, b = im.split()
    d = int(6 * fuerte)
    r = ImageChops.offset(r, d, 0)
    b = ImageChops.offset(b, -d, 0)
    im = Image.merge("RGB", (r, g, b))
    im = ImageEnhance.Color(im).enhance(1.25)
    ruido = Image.effect_noise((W // 2, H // 2), 40 * fuerte).convert("L").resize((W, H))
    im = ImageChops.blend(im, ImageChops.multiply(im, Image.merge("RGB", [ruido.point(lambda v: 190 + v // 4)] * 3)),
                          0.6)
    lineas = Image.new("L", (1, H), 255)
    for y in range(0, H, 3):
        lineas.putpixel((0, y), 205)
    im = ImageChops.multiply(im, Image.merge("RGB", [lineas.resize((W, H))] * 3))
    if rnd.random() < 0.18 * fuerte:  # barra de tracking
        y0 = rnd.randint(0, H - 80)
        banda = im.crop((0, y0, W, y0 + rnd.randint(20, 80)))
        im.paste(ImageChops.offset(banda, rnd.randint(-60, 60), 0), (0, y0))
    return im


def tira(d, texto, x, y, tam, fondo=(240, 214, 60), color=(20, 18, 16)):
    f = doc.fuente(tam)
    bb = d.textbbox((x, y), texto, font=f)
    d.rectangle([bb[0] - 14, bb[1] - 10, bb[2] + 14, bb[3] + 10], fill=fondo)
    d.text((x, y), texto, font=f, fill=color)


# ─────────────────────────────── iconos ───────────────────────────────
def iconos(items, salida, dur=9.0, corte=0.42, seed=4):
    """items: [(archivo, rótulo, foco_x, foco_y)]. Cortes cada `corte` s, con zoom de golpe y flash cada tanto."""
    rnd = random.Random(seed)
    v = Video(salida)
    fotos = [(cubrir(Image.open(a), int(W * 1.15), int(H * 1.15), (fx, fy)), rot) for a, rot, fx, fy in items]
    n = int(dur * FPS)
    por = max(1, int(corte * FPS))
    for k in range(n):
        i, dentro = divmod(k, por)
        im, rot = fotos[i % len(fotos)]
        z = 1.0 + 0.10 * dentro / por + (0.06 if i % 2 else 0)
        cw, ch = int(W * 1.15 / z), int(H * 1.15 / z)
        x0 = (im.width - cw) // 2 + (12 if i % 3 == 0 else -12) * dentro // por
        y0 = (im.height - ch) // 2
        f = im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
        if dentro == 0 and i % 3 == 1:
            f = Image.blend(f, Image.new("RGB", (W, H), "white"), 0.55)
        d = ImageDraw.Draw(f)
        if dentro >= 2:
            tira(d, rot, 90, 900, 40)
            tira(d, "1986", 90, 110, 30, fondo=ROJO, color=CREMA)
        v(vhs(f, k, rnd))
    v.cerrar()


# ─────────────────────────────── afiches ───────────────────────────────
def afiches(carpeta, salida, final_hold=2.4, seed=5):
    rnd = random.Random(seed)
    arch = sorted(Path(carpeta).glob("*.*"), key=lambda p: p.stem)
    anios = [p.stem for p in arch]
    fondo = doc.papel(W, H, seed=9)
    v = Video(salida)
    # duración de cada afiche: arranca rápido y se acelera; el último frena en seco
    tiempos = [max(0.12, 0.34 * 0.86 ** i) for i in range(len(arch) - 1)]
    piezas = []
    for p in arch:
        im = Image.open(p).convert("RGBA")
        base = Image.new("RGB", im.size, "white")
        base.paste(im, mask=im.split()[-1])
        im = doc.impresa(base, rnd)
        alto = 860
        im = im.resize((int(im.width * alto / im.height), alto), Image.LANCZOS)
        if im.width > 1100:
            im = im.resize((1100, int(im.height * 1100 / im.width)), Image.LANCZOS)
        marco = Image.new("RGB", (im.width + 24, im.height + 24), (248, 244, 234))
        marco.paste(im, (12, 12))
        piezas.append(marco)
    k = 0

    def cuadro(i, extra_z=1.0, sacudon=(0, 0), flash=0.0, sello=False):
        f = fondo.copy()
        d = ImageDraw.Draw(f)
        # regla de años abajo
        for j, a in enumerate(anios):
            x = 960 + (j - i) * 150
            if -100 < x < W + 100:
                col = ROJO if j == i else (120, 112, 100)
                d.text((x - 40, 980), a, font=doc.fuente(34 if j == i else 26), fill=col)
        d.line([(0, 965), (W, 965)], fill=(60, 56, 50), width=2)
        p = piezas[i]
        if extra_z != 1.0:
            p = p.resize((int(p.width * extra_z), int(p.height * extra_z)), Image.LANCZOS)
        rot = p.rotate(rnd.uniform(-1.5, 1.5) if not sello else 0, expand=True, fillcolor=(0, 0, 0, 0)) \
            if False else p
        x = 960 - rot.width // 2 + sacudon[0]
        y = 490 - rot.height // 2 + sacudon[1]
        sombra = Image.new("L", (rot.width + 40, rot.height + 40), 0)
        ImageDraw.Draw(sombra).rectangle([20, 20, rot.width + 20, rot.height + 20], fill=110)
        sombra = sombra.filter(ImageFilter.GaussianBlur(14))
        f.paste((30, 26, 20), (x - 12, y - 4), sombra)
        f.paste(rot, (x, y))
        if sello:
            tira(d, "XIII COPA DEL MUNDO", 1350, 120, 36, fondo=ROJO, color=CREMA)
        if flash:
            f = Image.blend(f, Image.new("RGB", (W, H), "white"), flash)
        return vhs(f, k, rnd, 0.5)

    for i, t in enumerate(tiempos):
        for _ in range(max(2, int(round(t * FPS)))):
            v(cuadro(i))
            k += 1
    last = len(arch) - 1
    for j in range(int(final_hold * FPS)):
        z = 1.18 - 0.18 * min(1, j / 5)
        sac = (rnd.randint(-14, 14), rnd.randint(-10, 10)) if j < 6 else (0, 0)
        v(cuadro(last, z, sac, flash=max(0, 0.8 - j * 0.2), sello=j > 8))
        k += 1
    v.cerrar()


# ─────────────────────────────── satelital ───────────────────────────────
def satelital(tierra, punto_tierra, ciudad, punto_ciudad, estadio, salida, dur=3.6, seed=6):
    """Tres capas con zoom exponencial y fundidos: Tierra entera -> ciudad -> estadio (aterriza y frena)."""
    rnd = random.Random(seed)
    T = Image.open(tierra).convert("RGB")
    C = Image.open(ciudad).convert("RGB")
    E = Image.open(estadio).convert("RGB")
    v = Video(salida)
    n = int(dur * FPS)

    def vista(img, cx, cy, ancho):
        """Recorte 16:9 de `ancho` px (en la imagen) centrado en cx, cy; lo que se sale queda negro."""
        alto = ancho * H / W
        caja = (cx - ancho / 2, cy - alto / 2, cx + ancho / 2, cy + alto / 2)
        return img.transform((W, H), Image.EXTENT, caja, Image.BILINEAR, fillcolor=(0, 0, 0))

    tw = T.width
    for k in range(n):
        t = k / (n - 1)
        if t < 0.45:  # Tierra: de entera a la ciudad
            u = doc.suave(t / 0.45) ** 1.6
            ancho = tw * 1.9 * (0.02 / 1.9) ** u
            cx = tw / 2 + (punto_tierra[0] - tw / 2) * min(1, u * 1.6)
            cy = tw / 2 + (punto_tierra[1] - tw / 2) * min(1, u * 1.6)
            f = vista(T, cx, cy, ancho)
            if t > 0.37:
                a = (t - 0.37) / 0.08
                f = Image.blend(f, vista(C, C.width / 2, C.height / 2, C.width * 1.1), min(1, a))
        elif t < 0.78:  # ciudad: zoom hacia el estadio
            u = doc.suave((t - 0.45) / 0.33)
            ancho = C.width * 1.1 * (0.09 / 1.1) ** u
            cx = C.width / 2 + (punto_ciudad[0] - C.width / 2) * u
            cy = C.height / 2 + (punto_ciudad[1] - C.height / 2) * u
            f = vista(C, cx, cy, ancho)
            if t > 0.70:
                a = (t - 0.70) / 0.08
                f = Image.blend(f, vista(E, E.width / 2, E.height * 0.42, E.width * 0.55), min(1, a))
        else:  # estadio: aterriza y frena
            u = 1 - (1 - (t - 0.78) / 0.22) ** 3
            ancho = E.width * (0.55 + 0.45 * u)
            f = vista(E, E.width / 2, E.height * 0.42, ancho)
        # nubes/velocidad: un poco de desenfoque radial falso en el medio del viaje
        if 0.15 < t < 0.8:
            f = Image.blend(f, f.filter(ImageFilter.GaussianBlur(3)), 0.35)
        v(vhs(f, k, rnd, 0.35))
    v.cerrar()


# ─────────────────────────────── banderas ───────────────────────────────
def banderas(carpeta, nombres, destacada, salida, dur=5.0, seed=7):
    rnd = random.Random(seed)
    fondo = Image.new("RGB", (W, H), (14, 16, 26))
    g = Image.new("L", (W, H), 0)
    ImageDraw.Draw(g).ellipse([300, 100, W - 300, H - 100], fill=90)
    fondo = Image.composite(Image.new("RGB", (W, H), (40, 52, 90)), fondo, g.filter(ImageFilter.GaussianBlur(200)))
    fw, fh = 270, 180
    cols, filas = 6, 4
    gx, gy = (W - cols * fw - (cols - 1) * 26) // 2, (H - filas * fh - (filas - 1) * 26) // 2
    flags = []
    orden = list(range(len(nombres)))
    rnd.shuffle(orden)
    for i, nom in enumerate(nombres):
        im = Image.open(Path(carpeta) / f"{nom}.png").convert("RGB").resize((fw, fh), Image.LANCZOS)
        x = gx + (i % cols) * (fw + 26)
        y = gy + (i // cols) * (fh + 26)
        flags.append((nom, im, x, y, orden.index(i) * 0.05))
    v = Video(salida)
    n = int(dur * FPS)
    t_ach = 2.0
    for k in range(n):
        t = k / FPS
        f = fondo.copy()
        for nom, im, x, y, t0 in flags:
            if t < t0:
                continue
            e = min(1, (t - t0) / 0.25)
            esc = 1 + 0.25 * math.sin(e * math.pi) if e < 1 else 1
            cx, cy = x + fw / 2, y + fh / 2
            alpha = 1.0
            if t > t_ach:
                u = doc.suave((t - t_ach) / 1.2)
                if nom == destacada:
                    cx += (W / 2 - cx) * u
                    cy += (H / 2 - cy) * u
                    esc *= 1 + 2.0 * u
                else:
                    esc *= 1 - 0.85 * u
                    alpha = 1 - u
            w2, h2 = int(fw * esc * e), int(fh * esc * e)
            if w2 < 4 or alpha <= 0.02:
                continue
            p = im.resize((w2, h2), Image.BILINEAR)
            if nom == destacada and t > t_ach + 0.8:  # brillo
                brillo = Image.new("L", (w2 + 160, h2 + 160), 0)
                ImageDraw.Draw(brillo).rectangle([80, 80, w2 + 80, h2 + 80], fill=int(150 + 60 * math.sin(t * 6)))
                f.paste((255, 240, 200), (int(cx - w2 / 2 - 80), int(cy - h2 / 2 - 80)),
                        brillo.filter(ImageFilter.GaussianBlur(40)))
            m = Image.new("L", p.size, int(255 * alpha))
            f.paste(p, (int(cx - w2 / 2), int(cy - h2 / 2)), m)
        if t > t_ach + 1.3:
            d = ImageDraw.Draw(f)
            tira(d, "24 SELECCIONES · MÉXICO 86", 640, 940, 34, fondo=CREMA, color=TINTA)
        v(vhs(f, k, rnd, 0.3))
    v.cerrar()


# ─────────────────────────────── peluca ───────────────────────────────
def peluca(salida, dur=3.0, seed=8):
    """Dibujito de tinta sobre papel: un señor de bigote, una ráfaga, la peluca sale volando dando vueltas."""
    rnd = random.Random(seed)
    base = doc.papel(W, H, seed=12)
    v = Video(salida)
    n = int(dur * FPS)
    cx, cy = 820, 600

    def pel(d, x, y, ang):
        pts = []
        for j in range(26):
            a = math.pi + j * math.pi / 25
            r = 175 + (16 if j % 2 else 0)
            pts.append((x + r * math.cos(a + ang), y + 0.62 * r * math.sin(a + ang)))
        d.polygon(pts, fill=(92, 58, 30), outline=TINTA)
        for j in range(0, 26, 2):
            px, py = pts[j]
            d.arc([px - 22, py - 22, px + 22, py + 22], 0, 360, fill=(60, 36, 18), width=5)

    for k in range(n):
        t = k / FPS
        f = base.copy()
        d = ImageDraw.Draw(f)
        sac = rnd.randint(-6, 6) if 0.6 < t < 1.6 else 0
        # cabeza pelada, ojos sorprendidos, bigote ochentoso, cuello y saco
        d.rectangle([cx - 230, cy + 230, cx + 230, H], fill=(70, 80, 110), outline=TINTA, width=6)
        d.ellipse([cx - 180 + sac, cy - 200, cx + 180 + sac, cy + 240], fill=(236, 196, 160), outline=TINTA, width=7)
        abre = 26 if t > 0.7 else 10
        for ox in (-70, 70):
            d.ellipse([cx + ox - 30 + sac, cy - 30 - abre, cx + ox + 30 + sac, cy - 30 + abre], fill="white",
                      outline=TINTA, width=5)
            d.ellipse([cx + ox - 9 + sac, cy - 38, cx + ox + 9 + sac, cy - 20], fill=TINTA)
        d.chord([cx - 90 + sac, cy + 40, cx + 90 + sac, cy + 120], 180, 360, fill=(50, 30, 20))
        boca = 50 if t > 0.8 else 12
        d.ellipse([cx - 30 + sac, cy + 130, cx + 30 + sac, cy + 130 + boca], fill=(90, 20, 20), outline=TINTA, width=4)
        # ráfaga
        if t > 0.4:
            for j in range(9):
                y = 260 + j * 70 + int(10 * math.sin(t * 9 + j))
                x0 = int(-400 + (t - 0.4) * 2600 - j * 90)
                d.line([(x0, y), (x0 + 380, y)], fill=TINTA, width=5)
                d.arc([x0 + 330, y - 40, x0 + 410, y + 40], 270, 90, fill=TINTA, width=5)
        # peluca: en la cabeza hasta 0.7 s, después vuela girando hacia arriba a la derecha
        if t < 0.7:
            pel(d, cx + sac, cy - 120, 0)
        else:
            u = t - 0.7
            pel(d, cx + 900 * u, cy - 120 - 520 * u + 160 * u * u, -u * 5)
        if t > 1.2:
            tira(d, "DATOS QUE TE VUELAN LA PELUCA", 1100, 920, 40, fondo=ROJO, color=CREMA)
        v(vhs(f, k, rnd, 0.3))
    v.cerrar()


if __name__ == "__main__":
    pieza, mat, out = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
    if pieza == "iconos":
        iconos([(mat / "mr_t.jpg", "MARIO BARACUS · BRIGADA A", 0.5, 0.12),
                (mat / "f14_topgun.png", "TOP GUN · 1986", 0.5, 0.5),
                (mat / "delorean.jpg", "VOLVER AL FUTURO · 1985", 0.5, 0.5),
                (mat / "cassette.jpg", "EL CASSETTE", 0.5, 0.5),
                (mat / "madonna.jpg", "MADONNA · TRUE BLUE, 1986", 0.5, 0.25),
                (mat / "f14.jpg", "TOP GUN · 1986", 0.5, 0.5)], out)
    elif pieza == "afiches":
        afiches(mat / "afiches", out)
    elif pieza == "satelital":
        satelital(mat / "tierra.jpg", (600, 2160), mat / "cdmx_satelite.jpg", (700, 640), mat.parent / "azteca_1986.jpg", out)
    elif pieza == "banderas":
        banderas(mat / "banderas", ["italy", "bulgaria", "south_korea", "mexico", "paraguay", "belgium", "iraq",
                                    "brazil", "spain", "northern_ireland", "algeria", "france", "soviet_union",
                                    "hungary", "canada", "germany", "uruguay", "scotland", "denmark", "poland",
                                    "morocco", "england", "portugal", "argentina"], "argentina", out)
    elif pieza == "peluca":
        peluca(out)
