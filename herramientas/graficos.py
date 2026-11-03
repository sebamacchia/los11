"""Gráficos del canal dibujados con Pillow: intro animada, marcador, placas de texto y zócalos.

Las animaciones se renderizan cuadro a cuadro y se mandan a ffmpeg por pipe.
"""
import math
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FPS = 30
DORADO = (232, 179, 58)
BLANCO = (245, 245, 240)
GRIS = (150, 150, 150)
FONDO = (10, 10, 12)
F_TITULO = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
F_TEXTO = "/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf"
CANAL = "LOS 11"


def fuente(ruta, tam):
    return ImageFont.truetype(ruta, int(tam))


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def _fondo(W, H):
    """Fondo oscuro con viñeta suave (se cachea por tamaño)."""
    clave = (W, H)
    if clave not in _fondo.cache:
        img = Image.new("RGB", (W, H), FONDO)
        glow = Image.new("L", (W, H), 0)
        ImageDraw.Draw(glow).ellipse([W * 0.15, H * 0.1, W * 0.85, H * 0.9], fill=40)
        glow = glow.filter(ImageFilter.GaussianBlur(W / 8))
        img = Image.composite(Image.new("RGB", (W, H), (40, 38, 34)), img, glow)
        _fondo.cache[clave] = img
    return _fondo.cache[clave].copy()


_fondo.cache = {}


def _texto_centrado(d, cx, y, txt, f, color, espaciado=0, alpha=255):
    txt = txt.replace("·", "|")  # DIN no tiene el punto medio
    if espaciado:
        anchos = [d.textlength(c, font=f) for c in txt]
        total = sum(anchos) + espaciado * (len(txt) - 1)
        x = cx - total / 2
        for c, a in zip(txt, anchos):
            d.text((x, y), c, font=f, fill=color + (alpha,))
            x += a + espaciado
    else:
        w = d.textlength(txt, font=f)
        d.text((cx - w / 2, y), txt, font=f, fill=color + (alpha,))


def _render(dest, W, H, dur, cuadro_fn):
    n = round(dur * FPS)
    p = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-an", str(dest)], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(cuadro_fn(i / FPS, i, n).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit(f"ffmpeg falló renderizando {dest}")


# ---------- intro del canal ----------
def intro(dest, W, H, dur=3.2, subtitulo=""):
    s = W / 1920
    f_t = fuente(F_TITULO, 150 * s)
    f_s = fuente(F_TEXTO, 34 * s)
    letras = list(CANAL)
    base = _fondo(W, H)

    def cuadro(t, i, n):
        img = base.copy().convert("RGBA")
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        cy = H / 2
        # línea dorada que se abre desde el centro
        a = ease(t / 0.6)
        lw = W * 0.42 * a
        d.rectangle([W / 2 - lw, cy + 70 * s, W / 2 + lw, cy + 74 * s], fill=DORADO + (255,))
        # letras que suben una por una
        esp = 10 * s
        anchos = [d.textlength(c, font=f_t) for c in letras]
        x = W / 2 - (sum(anchos) + esp * (len(letras) - 1)) / 2
        for k, (c, aw) in enumerate(zip(letras, anchos)):
            tk = ease((t - 0.25 - k * 0.035) / 0.45)
            if tk > 0:
                d.text((x, cy - 95 * s + (1 - tk) * 40 * s), c, font=f_t, fill=BLANCO + (int(255 * tk),))
            x += aw + esp
        if subtitulo:
            ts = ease((t - 1.2) / 0.5)
            _texto_centrado(d, W / 2, cy + 100 * s, subtitulo.upper(), f_s, DORADO, 6 * s, int(255 * ts))
        img = Image.alpha_composite(img, capa)
        # destello sutil al completarse y fundido final
        fin = max(0.0, (t - (dur - 0.45)) / 0.45)
        if fin > 0:
            img = Image.blend(img, Image.new("RGBA", (W, H), (0, 0, 0, 255)), min(1, fin))
        return img

    _render(dest, W, H, dur, cuadro)


# ---------- placa de texto grande (pausas / datos / capítulos) ----------
def placa(dest, W, H, dur, texto, sub="", etiqueta=""):
    s = W / 1920
    tam = 170 if len(texto) < 14 else 120 if len(texto) < 24 else 86
    f_t = fuente(F_TITULO, tam * s)
    f_s = fuente(F_TEXTO, 40 * s)
    f_e = fuente(F_TEXTO, 30 * s)
    base = _fondo(W, H)
    lineas = _partir(texto.upper(), f_t, W * 0.82)

    def cuadro(t, i, n):
        img = base.copy().convert("RGBA")
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.5)
        alto = tam * s * 1.05
        y0 = H / 2 - alto * len(lineas) / 2 - (30 * s if sub else 0) + (1 - a) * 30 * s
        if etiqueta:
            _texto_centrado(d, W / 2, y0 - 85 * s, etiqueta.upper(), f_e, DORADO, 8 * s, int(255 * a))
        for k, l in enumerate(lineas):
            _texto_centrado(d, W / 2, y0 + k * alto, l, f_t, BLANCO, 0, int(255 * a))
        if sub:
            b = ease((t - 0.35) / 0.5)
            _texto_centrado(d, W / 2, y0 + len(lineas) * alto + 25 * s, sub, f_s, GRIS, 0, int(255 * b))
        lw = 90 * s * a
        yl = y0 - 20 * s
        d.rectangle([W / 2 - lw, yl, W / 2 + lw, yl + 4 * s], fill=DORADO + (int(255 * a),))
        return Image.alpha_composite(img, capa)

    _render(dest, W, H, dur, cuadro)


def _partir(txt, f, ancho):
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lineas, actual = [], ""
    for p in txt.split():
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=f) > ancho and actual:
            lineas.append(actual)
            actual = p
        else:
            actual = prueba
    return lineas + [actual]


# ---------- marcador ----------
def marcador(dest, W, H, dur, local, visitante, goles, etiqueta="", cambios=None):
    """goles=(gl, gv). cambios=[[seg, gl, gv, 'texto opcional'], ...] anima los goles."""
    s = W / 1920
    f_eq = fuente(F_TITULO, 110 * s)
    f_gol = fuente(F_TITULO, 260 * s)
    f_e = fuente(F_TEXTO, 34 * s)
    f_n = fuente(F_TEXTO, 38 * s)
    base = _fondo(W, H)
    eventos = sorted(cambios or [], key=lambda c: c[0])

    def estado(t):
        gl, gv, nota, t_cambio = goles[0], goles[1], "", -10
        for c in eventos:
            if t >= c[0]:
                gl, gv, t_cambio = c[1], c[2], c[0]
                nota = c[3] if len(c) > 3 else ""
        return gl, gv, nota, t_cambio

    def cuadro(t, i, n):
        img = base.copy().convert("RGBA")
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.5)
        al = int(255 * a)
        gl, gv, nota, tc = estado(t)
        cy = H / 2
        if etiqueta:
            _texto_centrado(d, W / 2, cy - 230 * s, etiqueta.upper(), f_e, DORADO, 8 * s, al)
        # equipos
        off = (1 - a) * 80 * s
        wl = d.textlength(local.upper(), font=f_eq)
        d.text((W / 2 - 300 * s - wl - off, cy - 95 * s), local.upper(), font=f_eq, fill=BLANCO + (al,))
        d.text((W / 2 + 300 * s + off, cy - 95 * s), visitante.upper(), font=f_eq, fill=BLANCO + (al,))
        # goles (con pulso dorado cuando cambian)
        pulso = max(0.0, 1 - (t - tc) / 0.6) if t >= tc else 0
        col = tuple(int(BLANCO[k] + (DORADO[k] - BLANCO[k]) * pulso) for k in range(3))
        _texto_centrado(d, W / 2, cy - 150 * s, f"{gl}  -  {gv}", f_gol, col, 0, al)
        d.rectangle([W / 2 - 520 * s * a, cy + 140 * s, W / 2 + 520 * s * a, cy + 143 * s], fill=DORADO + (al,))
        if nota:
            b = ease((t - tc) / 0.4)
            _texto_centrado(d, W / 2, cy + 175 * s, nota, f_n, BLANCO, 0, int(255 * b))
        img = Image.alpha_composite(img, capa)
        if pulso > 0.6:  # flash breve en el gol
            img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), (pulso - 0.6) * 0.5)
        return img

    _render(dest, W, H, dur, cuadro)


# ---------- zócalo (PNG transparente que se superpone a una foto) ----------
def zocalo(dest, W, H, titulo, sub=""):
    s = W / 1920
    f_t = fuente(F_TITULO, 72 * s)
    f_s = fuente(F_TEXTO, 32 * s)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x, y = 90 * s, H - 230 * s
    ancho = max(d.textlength(titulo.upper(), font=f_t), d.textlength(sub, font=f_s) if sub else 0) + 70 * s
    caja = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(caja).rectangle([x, y, x + ancho, y + (150 if sub else 105) * s], fill=(0, 0, 0, 175))
    img = Image.alpha_composite(img, caja)
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + 8 * s, y + (150 if sub else 105) * s], fill=DORADO + (255,))
    sub = sub.replace("·", "|")
    d.text((x + 35 * s, y + 18 * s), titulo.upper(), font=f_t, fill=BLANCO + (255,))
    if sub:
        d.text((x + 35 * s, y + 98 * s), sub, font=f_s, fill=DORADO + (255,))
    img.save(dest)
